from django import forms
from django.utils import timezone
from datetime import datetime, timedelta, time
from .models import Cita, Interaccion
from .models import Solicitante


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
        if dia_semana in [1, 2]:  # Martes y Miércoles
            manana_valido = time(7, 0) <= hora <= time(12, 40)
            tarde_valido = time(14, 20) <= hora <= time(16, 20)
            
            if not (manana_valido or tarde_valido):
                raise forms.ValidationError(
                    'Para martes y miércoles, los horarios disponibles son: '
                    '7:00 AM - 12:40 PM o 2:20 PM - 4:20 PM'
                )
        
        elif dia_semana == 3:  # Jueves
            if not (time(14, 0) <= hora <= time(16, 20)):
                raise forms.ValidationError(
                    'Para jueves, los horarios disponibles son: 2:00 PM - 4:20 PM'
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
