from django import forms
from django.utils import timezone
from datetime import datetime, timedelta, time
from django.core.exceptions import ValidationError
from .models import Cita, Interaccion
from .models import Solicitante, Cita


class CitaForm(forms.ModelForm):
    """Formulario para agendar citas"""
    
    class Meta:
        model = Cita
        fields = ['fecha', 'hora_inicio', 'motivo']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': (timezone.now() + timedelta(hours=1)).strftime('%Y-%m-%d')
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'step': '1200'  # 20 minutos en segundos
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe brevemente el motivo de tu cita (opcional)'
            }),
        }
        labels = {
            'fecha': 'Fecha de la Cita',
            'hora_inicio': 'Hora de Inicio',
            'motivo': 'Motivo de la Cita',
        }
    
    def clean_fecha(self):
        """Validar que la fecha sea válida"""
        fecha = self.cleaned_data.get('fecha')
        
        if fecha < timezone.now().date():
            raise forms.ValidationError('No puedes agendar citas en el pasado.')
        
        # Validar que sea martes (1), miércoles (2) o jueves (3)
        dia_semana = fecha.weekday()
        if dia_semana not in [1, 2, 3]:
            raise forms.ValidationError('Solo se pueden agendar citas los martes, miércoles y jueves.')
        
        return fecha
    
    def clean_hora_inicio(self):
        """Validar que la hora esté en los rangos permitidos"""
        hora = self.cleaned_data.get('hora_inicio')
        fecha = self.cleaned_data.get('fecha')
        
        if not fecha:
            return hora
        
        dia_semana = fecha.weekday()
        
        # Validar rangos horarios según el día
        # Martes, Miércoles y Jueves: 2:00 PM - 4:00 PM
        if dia_semana in [1, 2, 3]:  # Martes, Miércoles y Jueves
            if not (time(14, 0) <= hora <= time(16, 0)):
                raise forms.ValidationError(
                    'Esta fecha ya no cuenta con disponibilidad de agentamiento.'
                )
        
        return hora
    
    def clean(self):
        """Validaciones adicionales del formulario"""
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        
        if fecha and hora_inicio:
            # Validar antelación mínima
            fecha_hora_cita = timezone.make_aware(
                datetime.combine(fecha, hora_inicio)
            )
            ahora = timezone.now()
            diferencia = fecha_hora_cita - ahora
            
            if diferencia < timedelta(hours=1):
                raise forms.ValidationError(
                    'Debes agendar con al menos 1 hora de anticipación.'
                )
            
            # Calcular hora de fin (20 minutos después)
            cleaned_data['hora_fin'] = (
                datetime.combine(fecha, hora_inicio) + timedelta(minutes=20)
            ).time()
            
            # Verificar si ya existe una cita en ese horario
            citas_existentes = Cita.objects.filter(
                fecha=fecha,
                hora_inicio=hora_inicio,
                estado='agendada'
            )
            
            if citas_existentes.exists():
                raise forms.ValidationError(
                    'Ya existe una cita agendada en este horario. Por favor selecciona otro.'
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        """Guardar la cita con la hora de fin calculada"""
        cita = super().save(commit=False)
        cita.hora_fin = self.cleaned_data['hora_fin']
        
        if commit:
            cita.save()
        
        return cita


class InteraccionForm(forms.ModelForm):
    """Formulario para registrar interacciones de citas"""
    
    class Meta:
        model = Interaccion
        fields = ['resultado', 'observaciones']
        widgets = {
            'resultado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'maxlength': '200',
                'placeholder': 'Observaciones adicionales (opcional, máximo 200 caracteres)'
            }),
        }
        labels = {
            'resultado': 'Resultado de la Reunión',
            'observaciones': 'Observaciones',
        }
    
    def clean_observaciones(self):
        """Validar longitud de observaciones"""
        observaciones = self.cleaned_data.get('observaciones', '')
        
        if observaciones and len(observaciones) > 200:
            raise forms.ValidationError('Las observaciones no pueden exceder 200 caracteres.')
        
        return observaciones
    

class ConsultarCitaForm(forms.Form):
    """
    Formulario para consultar citas por documento
    Valida que el documento y datos coincidan
    """
    
    tipo_documento = forms.ChoiceField(
        choices=Solicitante.TIPO_DOCUMENTO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Tipo de documento',
        required=True
    )
    
    numero_documento = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe tu número de documento'
        }),
        label='Número de documento',
        required=True
    )
    
    celular = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa un número celular de 10 dígitos'
        }),
        label='Celular',
        required=True
    )
    
    correo_electronico = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe un correo electrónico'
        }),
        label='Correo electrónico',
        required=True
    )
    
    def clean_numero_documento(self):
        """Validar formato del número de documento"""
        numero = self.cleaned_data.get('numero_documento')
        if not numero.isdigit():
            raise forms.ValidationError('El número de documento solo debe contener números.')
        return numero
    
    def clean_celular(self):
        """Validar formato del celular"""
        celular = self.cleaned_data.get('celular')
        # Remover espacios y caracteres especiales
        celular = ''.join(filter(str.isdigit, celular))
        
        if len(celular) != 10:
            raise forms.ValidationError('El celular debe tener 10 dígitos.')
        
        return celular    
    

class SolicitanteForm(forms.ModelForm):
    """
    Formulario completo para registrar datos del solicitante
    Incluye todos los campos demográficos requeridos
    """
    
    class Meta:
        model = Solicitante
        fields = [
            'tipo_documento',
            'numero_documento',
            'nombre',
            'apellido',
            'celular',
            'correo_electronico',
            'sexo',
            'genero',
            'orientacion_sexual',
            'rango_edad',
            'nivel_educativo',
            'grupo_etnico',
            'grupo_poblacional',
            'estrato_socioeconomico',
            'localidad',
            'calidad_comunicacion',
            'tiene_discapacidad',
            'tipo_discapacidad',
        ]
        widgets = {
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su número de documento',
                'required': True
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su nombre',
                'required': True
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su apellido',
                'required': True
            }),
            'celular': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 3001234567',
                'required': True
            }),
            'correo_electronico': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com',
                'required': True
            }),
            'sexo': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'genero': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'orientacion_sexual': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'rango_edad': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'nivel_educativo': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'grupo_etnico': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'grupo_poblacional': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'estrato_socioeconomico': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'localidad': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'calidad_comunicacion': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'tiene_discapacidad': forms.Select(choices=[
                ('', 'Seleccione una opción'),
                (True, 'Sí'),
                (False, 'No')
            ], attrs={
                'class': 'form-select',
                'required': True
            }),
            'tipo_discapacidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Especifique el tipo (si aplica)',
            }),
        }
        labels = {
            'tipo_documento': 'Tipo de documento',
            'numero_documento': 'Número de documento',
            'nombre': 'Nombres',
            'apellido': 'Apellidos',
            'celular': 'Número de celular',
            'correo_electronico': 'Correo electrónico',
            'sexo': '¿Cuál es tu sexo asignado al nacer?',
            'genero': '¿Cuál es tu género?',
            'orientacion_sexual': '¿Cuál es tu orientación sexual?',
            'rango_edad': '¿En qué rango de edad te encuentras?',
            'nivel_educativo': '¿Cuál es tu nivel educativo?',
            'grupo_etnico': '¿Perteneces a algún grupo étnico?',
            'grupo_poblacional': '¿Perteneces a alguna de las siguientes poblaciones?',
            'estrato_socioeconomico': '¿En qué estrato socioeconómico vives?',
            'localidad': '¿En qué localidad vives?',
            'calidad_comunicacion': 'Te comunicas en calidad de',
            'tiene_discapacidad': '¿Tienes alguna discapacidad?',
            'tipo_discapacidad': 'Tipo de discapacidad (si aplica)',
        }
    
    def clean_numero_documento(self):
        """Validar formato del número de documento"""
        numero = self.cleaned_data.get('numero_documento')
        if not numero.replace(' ', '').replace('-', '').isalnum():
            raise ValidationError('El número de documento contiene caracteres no válidos.')
        return numero
    
    def clean_celular(self):
        """Validar formato del celular"""
        celular = self.cleaned_data.get('celular')
        # Remover espacios y caracteres especiales
        celular_limpio = ''.join(filter(str.isdigit, celular))
        
        if len(celular_limpio) != 10:
            raise ValidationError('El celular debe tener 10 dígitos.')
        
        if not celular_limpio.startswith('3'):
            raise ValidationError('El celular debe comenzar con 3.')
        
        return celular_limpio
    
    def clean(self):
        """Validaciones generales del formulario"""
        cleaned_data = super().clean()
        tiene_discapacidad = cleaned_data.get('tiene_discapacidad')
        tipo_discapacidad = cleaned_data.get('tipo_discapacidad')
        
        # Si tiene discapacidad, el tipo es obligatorio
        if tiene_discapacidad and not tipo_discapacidad:
            self.add_error('tipo_discapacidad', 'Debe especificar el tipo de discapacidad.')
        
        return cleaned_data


class SeleccionFechaHoraForm(forms.Form):
    """
    Formulario para seleccionar fecha y hora de la cita
    """
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True,
            'id': 'id_fecha'
        }),
        label='Selecciona la fecha de tu cita'
    )
    
    hora_inicio = forms.TimeField(
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True,
            'id': 'id_hora_inicio'
        }),
        label='Selecciona la hora'
    )
    
    motivo = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe brevemente el motivo de tu cita (opcional)'
        }),
        label='Motivo de la cita',
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        """Personalizar las opciones de hora según disponibilidad"""
        fecha_seleccionada = kwargs.pop('fecha_seleccionada', None)
        super().__init__(*args, **kwargs)
        
        # Generar todas las opciones de hora disponibles
        horas_disponibles = self._generar_horas_disponibles()
        
        # Si hay fecha seleccionada, filtrar horas ocupadas
        if fecha_seleccionada:
            horas_ocupadas = self._obtener_horas_ocupadas(fecha_seleccionada)
            horas_disponibles = [
                (hora_valor, hora_display) 
                for hora_valor, hora_display in horas_disponibles 
                if hora_valor not in horas_ocupadas
            ]
        
        self.fields['hora_inicio'].widget.choices = [('', 'Seleccione una hora')] + horas_disponibles
    
    def _generar_horas_disponibles(self):
        """Genera todas las horas disponibles para agendar"""
        horas_disponibles = []
        
        # Horarios de 14:00 a 16:00 con intervalos de 20 minutos
        for hora in range(14, 17):  # 14:00 a 16:40
            for minuto in [0, 20, 40]:
                if hora == 16 and minuto > 0:
                    continue  # Solo hasta 16:00
                horas_disponibles.append((f"{hora:02d}:{minuto:02d}:00", f"{hora:02d}:{minuto:02d}"))
        
        return horas_disponibles
    
    def _obtener_horas_ocupadas(self, fecha):
        """Obtiene las horas ya ocupadas para una fecha específica"""
        from .models import Cita
        from datetime import datetime
        
        citas_agendadas = Cita.objects.filter(
            fecha=fecha,
            estado='agendada'
        ).values_list('hora_inicio', flat=True)
        
        # Convertir a formato string "HH:MM:SS"
        horas_ocupadas = [
            hora.strftime('%H:%M:%S') if isinstance(hora, datetime.time) else str(hora)
            for hora in citas_agendadas
        ]
        
        return horas_ocupadas
    
    def clean_fecha(self):
        """Validar que la fecha sea válida"""
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        fecha = self.cleaned_data.get('fecha')
        
        if not fecha:
            return fecha
        
        # Validar que no sea una fecha pasada
        hoy = timezone.now().date()
        if fecha < hoy:
            raise forms.ValidationError('No puedes agendar citas en fechas pasadas.')
        
        # Validar que sea martes, miércoles o jueves
        dia_semana = fecha.weekday()
        if dia_semana not in [1, 2, 3]:
            raise forms.ValidationError('Solo se permiten citas los días martes, miércoles o jueves.')
        
        # NO validamos las 2 horas aquí porque eso se hace por hora específica
        # en el método clean() y en el API
        
        return fecha
    
    def clean(self):
        """Validar que la fecha y hora sean consistentes"""
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        
        if fecha and hora_inicio:
            from datetime import datetime, time, timedelta
            from django.utils import timezone
            
            # Validar que el horario sea válido para el día seleccionado
            dia_semana = fecha.weekday()
            
            # Convertir hora a objeto time si es string
            if isinstance(hora_inicio, str):
                hora_inicio = datetime.strptime(hora_inicio, '%H:%M:%S').time()
            
            # Martes, Miércoles y Jueves: 2:00 PM - 4:00 PM
            if dia_semana in [1, 2, 3]:
                if not (time(14, 0) <= hora_inicio <= time(16, 0)):
                    raise ValidationError('El horario seleccionado no está disponible para el día elegido.')
            else:
                raise ValidationError('Ya no contamos con agenda disponible para este día, por favor seleccione otro.')
            
            # ===== VALIDACIÓN DE 2 HORAS DE ANTELACIÓN =====
            ahora = timezone.now()
            fecha_hora_cita = timezone.make_aware(
                datetime.combine(fecha, hora_inicio)
            )
            
            # Calcular diferencia en horas
            diferencia = fecha_hora_cita - ahora
            horas_diferencia = diferencia.total_seconds() / 3600
            
            if horas_diferencia < 2:
                raise ValidationError(
                    'Debes agendar tu cita con al menos 2 horas de antelación. '
                    f'La cita debe ser después de las {(ahora + timedelta(hours=2)).strftime("%I:%M %p")} del día {ahora.strftime("%d/%m/%Y")}.'
                )
            
            # Validar que no exista otra cita en ese horario
            from django.db.models import Q
            citas_existentes = Cita.objects.filter(
                fecha=fecha,
                hora_inicio=hora_inicio,
                estado='agendada'
            ).exists()
            
            if citas_existentes:
                raise ValidationError('Ya existe una cita agendada en ese horario. Por favor seleccione otro.')
        
        return cleaned_data
    
    def validar_cita_activa(self, tipo_documento, numero_documento):
        """
        Validar que el solicitante no tenga otra cita activa
        Este método debe ser llamado desde la vista antes de guardar
        """
        from django.utils import timezone
        
        cita_activa = Cita.objects.filter(
            solicitante__tipo_documento=tipo_documento,
            solicitante__numero_documento=numero_documento,
            estado='agendada',
            fecha__gte=timezone.now().date()
        ).exists()
        
        return not cita_activa
