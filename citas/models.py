from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta, time


class Cita(models.Model):
    """
    Modelo para gestionar las citas de los usuarios
    """
    ESTADO_CHOICES = [
        ('agendada', 'Agendada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
        ('no_asistio', 'No Asistió'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='citas',
        verbose_name='Usuario'
    )
    fecha = models.DateField(verbose_name='Fecha de la Cita')
    hora_inicio = models.TimeField(verbose_name='Hora de Inicio')
    hora_fin = models.TimeField(verbose_name='Hora de Fin')
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='agendada',
        verbose_name='Estado'
    )
    motivo = models.TextField(
        blank=True,
        null=True,
        verbose_name='Motivo de la Cita'
    )
    url_teams = models.URLField(
        blank=True,
        null=True,
        verbose_name='URL de Teams'
    )
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['fecha', 'hora_inicio']
        indexes = [
            models.Index(fields=['fecha', 'hora_inicio']),
            models.Index(fields=['usuario', 'estado']),
        ]
    
    def __str__(self):
        return f"Cita de {self.usuario.get_full_name()} - {self.fecha} {self.hora_inicio}"
    
    def clean(self):
        """Validaciones personalizadas del modelo"""
        # Validar que la fecha no sea en el pasado
        if self.fecha and self.fecha < timezone.now().date():
            raise ValidationError('No se puede agendar una cita en el pasado.')
        
        # Validar horarios permitidos
        if not self.es_horario_valido():
            raise ValidationError('El horario seleccionado no está disponible.')
        
        # Validar antelación mínima para agendar
        if self.pk is None:  # Solo para citas nuevas
            ahora = timezone.now()
            fecha_hora_cita = timezone.make_aware(
                datetime.combine(self.fecha, self.hora_inicio)
            )
            diferencia = fecha_hora_cita - ahora
            
            if diferencia < timedelta(hours=settings.ANTELACION_MINIMA_AGENDAMIENTO_HORAS):
                raise ValidationError(
                    f'Debe agendar con al menos {settings.ANTELACION_MINIMA_AGENDAMIENTO_HORAS} hora(s) de antelación.'
                )
    
    def es_horario_valido(self):
        """
        Valida si el horario está dentro de los horarios permitidos
        Martes y Miércoles: 7:00-12:40 y 14:20-16:20
        Jueves: 14:00-16:20
        """
        dia_semana = self.fecha.weekday()  # 0=Lunes, 1=Martes, ..., 6=Domingo
        
        # Solo martes (1), miércoles (2) y jueves (3)
        if dia_semana not in [1, 2, 3]:
            return False
        
        hora = self.hora_inicio
        
        if dia_semana in [1, 2]:  # Martes y Miércoles
            # 7:00 AM - 12:40 PM o 2:20 PM - 4:20 PM
            manana_valido = time(7, 0) <= hora <= time(12, 40)
            tarde_valido = time(14, 20) <= hora <= time(16, 20)
            return manana_valido or tarde_valido
        
        elif dia_semana == 3:  # Jueves
            # 2:00 PM - 4:20 PM
            return time(14, 0) <= hora <= time(16, 20)
        
        return False
    
    def puede_cancelarse(self):
        """Verifica si la cita puede cancelarse (2 horas de antelación)"""
        if self.estado != 'agendada':
            return False
        
        ahora = timezone.now()
        fecha_hora_cita = timezone.make_aware(
            datetime.combine(self.fecha, self.hora_inicio)
        )
        diferencia = fecha_hora_cita - ahora
        
        return diferencia >= timedelta(hours=settings.ANTELACION_MINIMA_CANCELACION_HORAS)


class Interaccion(models.Model):
    """
    Modelo para registrar las interacciones/resultados de las citas
    """
    RESULTADO_CHOICES = [
        ('efectiva', 'Efectiva'),
        ('no_asiste', 'No Asiste'),
    ]
    
    cita = models.OneToOneField(
        Cita,
        on_delete=models.CASCADE,
        related_name='interaccion',
        verbose_name='Cita'
    )
    asesor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='interacciones_atendidas',
        verbose_name='Asesor'
    )
    id_interaccion = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='ID de Interacción',
        editable=False
    )
    resultado = models.CharField(
        max_length=15,
        choices=RESULTADO_CHOICES,
        verbose_name='Resultado'
    )
    observaciones = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )
    
    class Meta:
        verbose_name = 'Interacción'
        verbose_name_plural = 'Interacciones'
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"Interacción {self.id_interaccion} - {self.cita}"
    
    def save(self, *args, **kwargs):
        """Generar ID de interacción automáticamente"""
        if not self.id_interaccion:
            # Generar ID consecutivo (formato: INT-YYYYMMDD-XXXX)
            fecha_actual = timezone.now()
            prefijo = f"INT-{fecha_actual.strftime('%Y%m%d')}"
            
            # Obtener el último ID del día
            ultima_interaccion = Interaccion.objects.filter(
                id_interaccion__startswith=prefijo
            ).order_by('-id_interaccion').first()
            
            if ultima_interaccion:
                ultimo_numero = int(ultima_interaccion.id_interaccion.split('-')[-1])
                nuevo_numero = ultimo_numero + 1
            else:
                nuevo_numero = 1
            
            self.id_interaccion = f"{prefijo}-{nuevo_numero:04d}"
        
        # Actualizar estado de la cita según el resultado
        if self.resultado == 'efectiva':
            self.cita.estado = 'completada'
        elif self.resultado == 'no_asiste':
            self.cita.estado = 'no_asistio'
        
        self.cita.save()
        super().save(*args, **kwargs)


class DisponibilidadHoraria(models.Model):
    """
    Modelo para gestionar bloques de disponibilidad horaria
    Útil para deshabilitar horarios específicos o agregar excepciones
    """
    fecha = models.DateField(verbose_name='Fecha')
    hora_inicio = models.TimeField(verbose_name='Hora de Inicio')
    hora_fin = models.TimeField(verbose_name='Hora de Fin')
    disponible = models.BooleanField(
        default=True,
        verbose_name='Disponible',
        help_text='Desmarcar para bloquear este horario'
    )
    motivo = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Motivo',
        help_text='Razón del bloqueo (si aplica)'
    )
    
    class Meta:
        verbose_name = 'Disponibilidad Horaria'
        verbose_name_plural = 'Disponibilidades Horarias'
        ordering = ['fecha', 'hora_inicio']
        unique_together = ['fecha', 'hora_inicio']
    
    def __str__(self):
        estado = "Disponible" if self.disponible else "Bloqueado"
        return f"{self.fecha} {self.hora_inicio}-{self.hora_fin} - {estado}"

