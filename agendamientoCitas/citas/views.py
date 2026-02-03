from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Cita, Interaccion
from .forms import CitaForm, InteraccionForm
from .email_utils import enviar_email_confirmacion_cita, enviar_email_cancelacion_cita


@login_required
def lista_citas_view(request):
    """Vista general de citas (redirige según el tipo de usuario)"""
    if request.user.es_asesor():
        return redirect('citas:panel_asesor')
    return redirect('citas:mis_citas')


@login_required
def mis_citas_view(request):
    """Vista para que el usuario vea sus propias citas"""
    citas = Cita.objects.filter(usuario=request.user).order_by('-fecha', '-hora_inicio')
    
    # Separar citas por estado
    citas_pendientes = citas.filter(estado='agendada', fecha__gte=timezone.now().date())
    citas_pasadas = citas.exclude(estado='agendada').order_by('-fecha', '-hora_inicio')[:10]
    
    context = {
        'citas_pendientes': citas_pendientes,
        'citas_pasadas': citas_pasadas,
    }
    return render(request, 'citas/mis_citas.html', context)


@login_required
def agendar_cita_view(request):
    """Vista para agendar una nueva cita"""
    # Verificar si el usuario ya tiene una cita agendada
    cita_existente = Cita.objects.filter(
        usuario=request.user,
        estado='agendada',
        fecha__gte=timezone.now().date()
    ).exists()
    
    if cita_existente:
        messages.error(request, 'Ya tienes una cita agendada. No puedes agendar otra hasta completar o cancelar la existente.')
        return redirect('citas:mis_citas')
    
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            try:
                cita = form.save(commit=False)
                cita.usuario = request.user
                cita.save()
                messages.success(request, '¡Cita agendada exitosamente! Recibirás un correo de confirmación.')
                # TODO: Enviar correo de confirmación
                return redirect('citas:mis_citas')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = CitaForm()
    
    return render(request, 'citas/agendar_cita.html', {'form': form})


@login_required
def cancelar_cita_view(request, cita_id):
    """Vista para cancelar una cita"""
    cita = get_object_or_404(Cita, id=cita_id, usuario=request.user)
    
    if not cita.puede_cancelarse():
        messages.error(request, 'No puedes cancelar esta cita. Debe hacerse con al menos 2 horas de antelación.')
        return redirect('citas:mis_citas')
    
    if request.method == 'POST':
        cita.estado = 'cancelada'
        cita.save()
        messages.success(request, 'Cita cancelada exitosamente.')
        # TODO: Enviar correo de cancelación
        return redirect('citas:mis_citas')
    
    return render(request, 'citas/cancelar_cita.html', {'cita': cita})


@login_required
def horarios_disponibles_view(request):
    """Vista para ver los horarios disponibles (API o template)"""
    # Esta vista se implementará más adelante con AJAX
    return render(request, 'citas/horarios_disponibles.html')


@login_required
def panel_asesor_view(request):
    """Vista del panel para asesores"""
    if not request.user.es_asesor():
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    # Obtener citas del día actual
    hoy = timezone.now().date()
    citas_hoy = Cita.objects.filter(
        fecha=hoy,
        estado='agendada'
    ).order_by('hora_inicio')
    
    # Obtener todas las citas agendadas futuras
    citas_futuras = Cita.objects.filter(
        estado='agendada',
        fecha__gte=hoy
    ).order_by('fecha', 'hora_inicio')
    
    context = {
        'citas_hoy': citas_hoy,
        'citas_futuras': citas_futuras,
    }
    return render(request, 'citas/panel_asesor.html', context)


@login_required
def atender_cita_view(request, cita_id):
    """Vista para que el asesor atienda y registre el resultado de una cita"""
    if not request.user.es_asesor():
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    cita = get_object_or_404(Cita, id=cita_id)
    
    # Verificar si ya existe una interacción para esta cita
    try:
        interaccion = cita.interaccion
        form = InteraccionForm(request.POST or None, instance=interaccion)
    except Interaccion.DoesNotExist:
        form = InteraccionForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            interaccion = form.save(commit=False)
            interaccion.cita = cita
            interaccion.asesor = request.user
            interaccion.save()
            messages.success(request, f'Interacción registrada exitosamente. ID: {interaccion.id_interaccion}')
            return redirect('citas:panel_asesor')
    
    context = {
        'cita': cita,
        'form': form,
    }
    return render(request, 'citas/atender_cita.html', context)



# ========================================
# VISTAS PÚBLICAS (Sin autenticación)
# ========================================

def agendar_cita_publica_view(request):
    """
    Vista pública para agendar citas - Paso 1: Datos del Solicitante
    Si el solicitante existe, pre-llena el formulario con sus últimos datos
    """
    from .forms import SolicitanteForm
    from .models import Solicitante, Cita
    from django.utils import timezone
    
    # Si viene de un POST previo con documento para buscar
    tipo_doc = request.GET.get('tipo_documento')
    numero_doc = request.GET.get('numero_documento')
    
    initial_data = {}
    
    # Si se proporcionó documento, intentar traer último registro
    if tipo_doc and numero_doc:
        # ========================================
        # NUEVA VALIDACIÓN: Verificar cita activa temprano
        # ========================================
        cita_activa = Cita.objects.filter(
            solicitante__tipo_documento=tipo_doc,
            solicitante__numero_documento=numero_doc,
            estado='agendada',
            fecha__gte=timezone.now().date()
        ).select_related('solicitante').first()
        
        if cita_activa:
            messages.warning(
                request,
                f'Ya tienes una cita agendada para el {cita_activa.fecha.strftime("%d/%m/%Y")} '
                f'a las {cita_activa.hora_inicio.strftime("%H:%M")}. '
                f'No puedes agendar otra cita hasta completar o cancelar la existente.'
            )
            # Opcionalmente, redirigir al home o a consultar cita
            # return redirect('home')
        
        ultimo_registro = Solicitante.get_ultimo_registro(tipo_doc, numero_doc)
        if ultimo_registro and not cita_activa:
            # Pre-llenar con datos del último registro solo si NO tiene cita activa
            initial_data = {
                'tipo_documento': ultimo_registro.tipo_documento,
                'numero_documento': ultimo_registro.numero_documento,
                'nombre': ultimo_registro.nombre,
                'apellido': ultimo_registro.apellido,
                'celular': ultimo_registro.celular,
                'correo_electronico': ultimo_registro.correo_electronico,
                'sexo': ultimo_registro.sexo,
                'genero': ultimo_registro.genero,
                'orientacion_sexual': ultimo_registro.orientacion_sexual,
                'rango_edad': ultimo_registro.rango_edad,
                'nivel_educativo': ultimo_registro.nivel_educativo,
                'grupo_etnico': ultimo_registro.grupo_etnico,
                'grupo_poblacional': ultimo_registro.grupo_poblacional,
                'estrato_socioeconomico': ultimo_registro.estrato_socioeconomico,
                'localidad': ultimo_registro.localidad,
                'calidad_comunicacion': ultimo_registro.calidad_comunicacion,
                'tiene_discapacidad': ultimo_registro.tiene_discapacidad,
                'tipo_discapacidad': ultimo_registro.tipo_discapacidad,
            }
            messages.info(request, 'Hemos encontrado tus datos previos. Puedes actualizarlos si es necesario.')
    
    if request.method == 'POST':
        form = SolicitanteForm(request.POST)
        if form.is_valid():
            # ========================================
            # NUEVA VALIDACIÓN: Verificar cita activa antes de continuar
            # ========================================
            tipo_doc = form.cleaned_data['tipo_documento']
            numero_doc = form.cleaned_data['numero_documento']
            
            cita_activa = Cita.objects.filter(
                solicitante__tipo_documento=tipo_doc,
                solicitante__numero_documento=numero_doc,
                estado='agendada',
                fecha__gte=timezone.now().date()
            ).select_related('solicitante').first()
            
            if cita_activa:
                messages.error(
                    request,
                    f'Ya tienes una cita agendada para el {cita_activa.fecha.strftime("%d/%m/%Y")} '
                    f'a las {cita_activa.hora_inicio.strftime("%H:%M")}. '
                    f'No puedes agendar otra cita hasta completar o cancelar la existente.'
                )
                return render(request, 'citas/agendar_paso1_solicitante.html', {'form': form})
            
            # Guardar datos en sesión para el siguiente paso
            request.session['solicitante_data'] = {
                'tipo_documento': form.cleaned_data['tipo_documento'],
                'numero_documento': form.cleaned_data['numero_documento'],
                'nombre': form.cleaned_data['nombre'],
                'apellido': form.cleaned_data['apellido'],
                'celular': form.cleaned_data['celular'],
                'correo_electronico': form.cleaned_data['correo_electronico'],
                'sexo': form.cleaned_data['sexo'],
                'genero': form.cleaned_data['genero'],
                'orientacion_sexual': form.cleaned_data['orientacion_sexual'],
                'rango_edad': form.cleaned_data['rango_edad'],
                'nivel_educativo': form.cleaned_data['nivel_educativo'],
                'grupo_etnico': form.cleaned_data['grupo_etnico'],
                'grupo_poblacional': form.cleaned_data['grupo_poblacional'],
                'estrato_socioeconomico': form.cleaned_data['estrato_socioeconomico'],
                'localidad': form.cleaned_data['localidad'],
                'calidad_comunicacion': form.cleaned_data['calidad_comunicacion'],
                'tiene_discapacidad': form.cleaned_data['tiene_discapacidad'],
                'tipo_discapacidad': form.cleaned_data.get('tipo_discapacidad', ''),
            }
            
            # Redirigir al paso 2: selección de fecha y hora
            return redirect('citas:agendar_paso2')
    else:
        form = SolicitanteForm(initial=initial_data)
    
    return render(request, 'citas/agendar_paso1_solicitante.html', {'form': form})


def consultar_cita_view(request):
    """
    Vista pública para consultar citas por documento
    Valida datos del solicitante y muestra la próxima cita agendada
    """
    from django.utils import timezone
    from .forms import ConsultarCitaForm
    from .models import Solicitante, Cita
    
    if request.method == 'POST':
        form = ConsultarCitaForm(request.POST)
        if form.is_valid():
            tipo_doc = form.cleaned_data['tipo_documento']
            numero_doc = form.cleaned_data['numero_documento']
            celular = form.cleaned_data['celular']
            email = form.cleaned_data['correo_electronico']
            
            # Buscar el último registro del solicitante
            solicitante = Solicitante.get_ultimo_registro(tipo_doc, numero_doc)
            
            if not solicitante:
                messages.error(request, 'No se encontró ningún registro con el documento proporcionado.')
                return render(request, 'citas/consultar_cita.html', {'form': form})
            
            # Validar que los datos coincidan
            if solicitante.celular != celular or solicitante.correo_electronico != email:
                messages.error(request, 'Los datos proporcionados no coinciden con nuestros registros.')
                return render(request, 'citas/consultar_cita.html', {'form': form})
            
            # Buscar la próxima cita agendada
            proxima_cita = Cita.objects.filter(
                solicitante__tipo_documento=tipo_doc,
                solicitante__numero_documento=numero_doc,
                estado='agendada',
                fecha__gte=timezone.now().date()
            ).select_related('solicitante').order_by('fecha', 'hora_inicio').first()
            
            return render(request, 'citas/consultar_cita_resultado.html', {
                'form': form,
                'cita': proxima_cita,
            })
    else:
        form = ConsultarCitaForm()
    
    return render(request, 'citas/consultar_cita.html', {'form': form})

def agendar_paso2_fecha_view(request):
    """
    Vista pública para agendar citas - Paso 2: Selección de Fecha y Hora
    """
    from .forms import SeleccionFechaHoraForm
    from .models import Solicitante, Cita
    from datetime import timedelta
    from .email_utils import enviar_email_confirmacion_cita
    from django.utils import timezone
    
    # Verificar que existan datos del solicitante en sesión
    solicitante_data = request.session.get('solicitante_data')
    if not solicitante_data:
        messages.warning(request, 'Sesión expirada. Por favor ingresa tus datos nuevamente.')
        return redirect('citas:agendar_cita')
    
    # ========================================
    # NUEVA VALIDACIÓN: Verificar cita activa ANTES de mostrar el formulario
    # ========================================
    ahora = timezone.now()
    cita_activa_existente = Cita.objects.filter(
        solicitante__tipo_documento=solicitante_data['tipo_documento'],
        solicitante__numero_documento=solicitante_data['numero_documento'],
        estado='agendada',
        fecha__gte=ahora.date()
    ).select_related('solicitante').first()
    
    if cita_activa_existente:
        messages.error(
            request, 
            f'Ya tienes una cita agendada activa para el {cita_activa_existente.fecha.strftime("%d/%m/%Y")} '
            f'a las {cita_activa_existente.hora_inicio.strftime("%H:%M")}. '
            f'No puedes agendar otra cita hasta completar o cancelar la existente.'
        )
        # Limpiar sesión
        if 'solicitante_data' in request.session:
            del request.session['solicitante_data']
        return redirect('home')
    
    if request.method == 'POST':
        form = SeleccionFechaHoraForm(request.POST)
        if form.is_valid():
            # ========================================
            # VALIDACIÓN ADICIONAL: Verificar nuevamente antes de crear
            # ========================================
            cita_activa = Cita.objects.filter(
                solicitante__tipo_documento=solicitante_data['tipo_documento'],
                solicitante__numero_documento=solicitante_data['numero_documento'],
                estado='agendada',
                fecha__gte=ahora.date()
            ).exists()
            
            if cita_activa:
                messages.error(
                    request,
                    'Ya tienes una cita agendada activa. No puedes agendar otra cita hasta completar o cancelar la existente.'
                )
                # Limpiar sesión
                if 'solicitante_data' in request.session:
                    del request.session['solicitante_data']
                return redirect('home')
            
            # Crear el Solicitante
            solicitante = Solicitante.objects.create(
                tipo_documento=solicitante_data['tipo_documento'],
                numero_documento=solicitante_data['numero_documento'],
                nombre=solicitante_data['nombre'],
                apellido=solicitante_data['apellido'],
                celular=solicitante_data['celular'],
                correo_electronico=solicitante_data['correo_electronico'],
                sexo=solicitante_data['sexo'],
                genero=solicitante_data['genero'],
                orientacion_sexual=solicitante_data['orientacion_sexual'],
                rango_edad=solicitante_data['rango_edad'],
                nivel_educativo=solicitante_data['nivel_educativo'],
                grupo_etnico=solicitante_data['grupo_etnico'],
                grupo_poblacional=solicitante_data['grupo_poblacional'],
                estrato_socioeconomico=solicitante_data['estrato_socioeconomico'],
                localidad=solicitante_data['localidad'],
                calidad_comunicacion=solicitante_data['calidad_comunicacion'],
                tiene_discapacidad=solicitante_data['tiene_discapacidad'],
                tipo_discapacidad=solicitante_data.get('tipo_discapacidad', ''),
            )
            
            # Calcular hora_fin (20 minutos después)
            fecha = form.cleaned_data['fecha']
            hora_inicio = form.cleaned_data['hora_inicio']
            
            # Convertir hora_inicio a datetime para sumar 20 minutos
            from datetime import datetime, time
            dt_inicio = datetime.combine(fecha, hora_inicio)
            dt_fin = dt_inicio + timedelta(minutes=20)
            hora_fin = dt_fin.time()
            
            try:
                # Crear la Cita
                cita = Cita(
                    solicitante=solicitante,
                    fecha=fecha,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    estado='agendada',
                    motivo=form.cleaned_data.get('motivo', ''),
                )
                
                # Validar antes de guardar (ejecuta el método clean del modelo)
                cita.full_clean()
                cita.save()
                
                # Enviar email de confirmación
                email_enviado = enviar_email_confirmacion_cita(cita)
                if email_enviado:
                    messages.success(
                        request, 
                        '¡Cita agendada exitosamente! Te hemos enviado un email de confirmación.'
                    )
                else:
                    messages.success(
                        request, 
                        '¡Cita agendada exitosamente! (No pudimos enviar el email de confirmación)'
                    )
                
                # Guardar ID de cita en sesión para confirmación
                request.session['cita_id'] = cita.id
                
                # Limpiar datos del solicitante de la sesión
                del request.session['solicitante_data']
                
                return redirect('citas:agendar_confirmacion')
                
            except ValidationError as e:
                # Capturar errores de validación del modelo
                messages.error(request, str(e))
                # Si la validación falla, eliminar el solicitante creado
                solicitante.delete()
                
    else:
        form = SeleccionFechaHoraForm()
    
    # Preparar datos para mostrar en el template
    class SolicitanteDisplay:
        def __init__(self, data):
            self.data = data
            self.nombre = data['nombre']
            self.apellido = data['apellido']
            self.numero_documento = data['numero_documento']
            self.celular = data['celular']
            self.correo_electronico = data['correo_electronico']
        
        def get_tipo_documento_display(self):
            tipos = dict(Solicitante.TIPO_DOCUMENTO_CHOICES)
            return tipos.get(self.data['tipo_documento'], self.data['tipo_documento'])
    
    solicitante_display = SolicitanteDisplay(solicitante_data)
    
    return render(request, 'citas/agendar_paso2_fecha.html', {
        'form': form,
        'solicitante_data': solicitante_display,
    })


def agendar_confirmacion_view(request):
    """
    Vista de confirmación de cita agendada
    Muestra los detalles de la cita recién creada
    """
    from .models import Cita
    
    # Obtener ID de cita de la sesión
    cita_id = request.session.get('cita_id')
    if not cita_id:
        messages.warning(request, 'No se encontró información de la cita.')
        return redirect('home')
    
    # Obtener la cita
    cita = get_object_or_404(Cita, id=cita_id)
    
    # Limpiar sesión
    if 'cita_id' in request.session:
        del request.session['cita_id']
    
    return render(request, 'citas/agendar_confirmacion.html', {
        'cita': cita,
    })



def buscar_cita_cancelar_view(request):
    """
    Vista pública para buscar citas a cancelar por documento
    Valida datos del solicitante y muestra citas agendadas que pueden cancelarse
    """
    from django.utils import timezone
    from .forms import ConsultarCitaForm
    from .models import Solicitante, Cita
    
    if request.method == 'POST':
        form = ConsultarCitaForm(request.POST)
        if form.is_valid():
            tipo_doc = form.cleaned_data['tipo_documento']
            numero_doc = form.cleaned_data['numero_documento']
            celular = form.cleaned_data['celular']
            email = form.cleaned_data['correo_electronico']
            
            # Buscar el último registro del solicitante
            solicitante = Solicitante.get_ultimo_registro(tipo_doc, numero_doc)
            
            if not solicitante:
                messages.error(request, 'No se encontró ningún registro con el documento proporcionado.')
                return render(request, 'citas/cancelar_cita_buscar.html', {'form': form})
            
            # Validar que los datos coincidan
            if solicitante.celular != celular or solicitante.correo_electronico != email:
                messages.error(request, 'Los datos proporcionados no coinciden con nuestros registros.')
                return render(request, 'citas/cancelar_cita_buscar.html', {'form': form})
            
            # Buscar todas las citas agendadas
            citas = Cita.objects.filter(
                solicitante__tipo_documento=tipo_doc,
                solicitante__numero_documento=numero_doc,
                estado='agendada',
                fecha__gte=timezone.now().date()
            ).select_related('solicitante').order_by('fecha', 'hora_inicio')
            
            if not citas:
                messages.info(request, 'No tienes citas agendadas para cancelar.')
                return render(request, 'citas/cancelar_cita_buscar.html', {'form': form})
            
            return render(request, 'citas/cancelar_cita_lista.html', {
                'citas': citas,
            })
    else:
        form = ConsultarCitaForm()
    
    return render(request, 'citas/cancelar_cita_buscar.html', {'form': form})


def confirmar_cancelar_cita_view(request, cita_id):
    """
    Vista pública para confirmar y ejecutar la cancelación de una cita
    Valida que la cita pueda cancelarse (2 horas de antelación)
    """
    from .models import Cita
    from .email_utils import enviar_email_cancelacion_cita
    
    cita = get_object_or_404(Cita, id=cita_id)
    
    # Validar que la cita pueda cancelarse
    if not cita.puede_cancelarse():
        messages.error(
            request, 
            'Esta cita no puede cancelarse. Debe hacerlo con al menos 2 horas de anticipación.'
        )
        return redirect('home')
    
    if request.method == 'POST':
        # Cambiar estado a cancelada
        cita.estado = 'cancelada'
        cita.save()
        # ========================================
        # ENVIAR EMAIL DE CANCELACIÓN
        # ========================================
        email_enviado = enviar_email_cancelacion_cita(cita)
        if email_enviado:
            messages.success(
                request, 
                f'Cita cancelada exitosamente. Te hemos enviado un email de confirmación. Fecha: {cita.fecha.strftime("%d/%m/%Y")} - Hora: {cita.hora_inicio.strftime("%H:%M")}'
            )
        else:
            messages.success(
                request, 
                f'Cita cancelada exitosamente. Fecha: {cita.fecha.strftime("%d/%m/%Y")} - Hora: {cita.hora_inicio.strftime("%H:%M")}'
            )
        # ========================================
        
        return redirect('home')
    
    # Si no es POST, redirigir al home
    return redirect('home')


def horarios_disponibles_view(request):
    """Vista para ver horarios disponibles (TODO: Implementar)"""
    from django.http import HttpResponse
    return HttpResponse("<h1>Horarios Disponibles - En construcción</h1><p><a href='/'>Volver</a></p>")


@login_required
def mis_interacciones_view(request):
    """Vista para que el asesor vea su historial de interacciones"""
    if not request.user.es_asesor():
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    # Obtener interacciones del asesor
    interacciones = Interaccion.objects.filter(
        asesor=request.user
    ).select_related(
        'cita', 
        'cita__solicitante',
        'cita__usuario'
    ).order_by('-fecha_registro')
    
    # Estadísticas
    total_interacciones = interacciones.count()
    efectivas = interacciones.filter(resultado='efectiva').count()
    no_asiste = interacciones.filter(resultado='no_asiste').count()
    
    context = {
        'interacciones': interacciones,
        'total_interacciones': total_interacciones,
        'efectivas': efectivas,
        'no_asiste': no_asiste,
    }
    return render(request, 'citas/mis_interacciones.html', context)

@require_http_methods(["GET"])
def buscar_solicitante_api(request):
    """
    API endpoint para buscar un solicitante por tipo y número de documento
    Retorna los datos en formato JSON si existe
    """
    tipo_documento = request.GET.get('tipo_documento')
    numero_documento = request.GET.get('numero_documento')
    
    # Validar que se enviaron ambos parámetros
    if not tipo_documento or not numero_documento:
        return JsonResponse({
            'success': False,
            'message': 'Faltan parámetros requeridos'
        }, status=400)
    
    # Buscar el último registro del solicitante
    from .models import Solicitante
    solicitante = Solicitante.get_ultimo_registro(tipo_documento, numero_documento)
    
    if solicitante:
        # Retornar los datos del solicitante
        return JsonResponse({
            'success': True,
            'encontrado': True,
            'datos': {
                'tipo_documento': solicitante.tipo_documento,
                'numero_documento': solicitante.numero_documento,
                'nombre': solicitante.nombre,
                'apellido': solicitante.apellido,
                'celular': solicitante.celular,
                'correo_electronico': solicitante.correo_electronico,
                'sexo': solicitante.sexo,
                'genero': solicitante.genero,
                'orientacion_sexual': solicitante.orientacion_sexual,
                'rango_edad': solicitante.rango_edad,
                'nivel_educativo': solicitante.nivel_educativo,
                'grupo_etnico': solicitante.grupo_etnico,
                'grupo_poblacional': solicitante.grupo_poblacional,
                'estrato_socioeconomico': solicitante.estrato_socioeconomico,
                'localidad': solicitante.localidad,
                'calidad_comunicacion': solicitante.calidad_comunicacion,
                'tiene_discapacidad': solicitante.tiene_discapacidad,
                'tipo_discapacidad': solicitante.tipo_discapacidad or '',
            },
            'message': 'Encontramos tus datos previos. Puedes actualizarlos si es necesario.'
        })
    else:
        # No se encontró el solicitante
        return JsonResponse({
            'success': True,
            'encontrado': False,
            'message': 'No encontramos registros previos con este documento.'
        })
    
@require_http_methods(["GET"])
def obtener_horas_disponibles_api(request):
    """
    API endpoint para obtener horas disponibles según la fecha seleccionada
    """
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    fecha_str = request.GET.get('fecha')
    
    if not fecha_str:
        return JsonResponse({
            'success': False,
            'message': 'Falta el parámetro de fecha'
        }, status=400)
    
    try:
        # Convertir string a fecha
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        
        # Validar que sea martes, miércoles o jueves
        dia_semana = fecha.weekday()
        if dia_semana not in [1, 2, 3]:
            return JsonResponse({
                'success': False,
                'message': 'Ya no contamos con agenda disponible para este día, por favor seleccione otro.'
            }, status=400)
        
        # Obtener hora actual con timezone
        ahora = timezone.now()
        
        # Generar todas las horas posibles
        horas_disponibles = []
        
        # Martes, Miércoles y Jueves: 2:00 PM - 4:00 PM (cada 20 minutos)
        for hora in range(14, 17):
            for minuto in [0, 20, 40]:
                if hora == 16 and minuto > 0:
                    continue  # Solo hasta 16:00
                
                hora_str = f"{hora:02d}:{minuto:02d}:00"
                
                # Crear datetime de la cita para validar antelación
                hora_obj = datetime.strptime(hora_str, '%H:%M:%S').time()
                fecha_hora_cita = timezone.make_aware(
                    datetime.combine(fecha, hora_obj)
                )
                
                # Validar que tenga al menos 2 horas de antelación
                diferencia = fecha_hora_cita - ahora
                horas_diferencia = diferencia.total_seconds() / 3600
                
                # Solo agregar si tiene más de 2 horas de antelación
                if horas_diferencia >= 2:
                    horas_disponibles.append(hora_str)
        
        # Obtener horas ya ocupadas
        citas_ocupadas = Cita.objects.filter(
            fecha=fecha,
            estado='agendada'
        ).values_list('hora_inicio', flat=True)
        
        horas_ocupadas = [hora.strftime('%H:%M:%S') for hora in citas_ocupadas]
        
        # Filtrar horas disponibles (que no estén ocupadas)
        horas_libres = [
            {'value': hora, 'display': hora[:-3]}  # Quitar los segundos para display
            for hora in horas_disponibles
            if hora not in horas_ocupadas
        ]
        
        return JsonResponse({
            'success': True,
            'horas': horas_libres
        })
        
    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Formato de fecha inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)
