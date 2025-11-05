from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Cita, Interaccion
from .forms import CitaForm, InteraccionForm


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
    """Vista pública para agendar citas (TODO: Implementar)"""
    from django.http import HttpResponse
    return HttpResponse("<h1>Vista de Agendamiento - En construcción</h1><p><a href='/'>Volver</a></p>")


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


def buscar_cita_cancelar_view(request):
    """Vista pública para buscar cita a cancelar por documento (TODO: Implementar)"""
    from django.http import HttpResponse
    return HttpResponse("<h1>Vista de Cancelación - En construcción</h1><p><a href='/'>Volver</a></p>")


def confirmar_cancelar_cita_view(request, cita_id):
    """Vista pública para confirmar cancelación de cita (TODO: Implementar)"""
    from django.http import HttpResponse
    return HttpResponse("<h1>Confirmar Cancelación - En construcción</h1><p><a href='/'>Volver</a></p>")


def horarios_disponibles_view(request):
    """Vista para ver horarios disponibles (TODO: Implementar)"""
    from django.http import HttpResponse
    return HttpResponse("<h1>Horarios Disponibles - En construcción</h1><p><a href='/'>Volver</a></p>")
