from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta, time


class Solicitante(models.Model):
    """
    Modelo para registrar personas que solicitan citas
    No requiere cuenta de usuario, se identifica por documento
    Se crea un nuevo registro por cada agendamiento para mantener historial
    """
    
    # Opciones para los campos de selección
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('TI', 'Tarjeta de Identidad'),
        ('PEP', 'Permiso Especial de Permanencia'),
        ('RC', 'Registro Civil'),
        ('PA', 'Pasaporte'),
    ]
    
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('I', 'Intersexual'),
    ]
    
    GENERO_CHOICES = [
        ('hombre', 'Hombre'),
        ('mujer', 'Mujer'),
        ('no_binario', 'No binario'),
        ('otro', 'Otro'),
        ('prefiero_no_decir', 'Prefiero no decir'),
    ]
    
    ORIENTACION_SEXUAL_CHOICES = [
        ('heterosexual', 'Heterosexual'),
        ('homosexual', 'Homosexual'),
        ('bisexual', 'Bisexual'),
        ('pansexual', 'Pansexual'),
        ('asexual', 'Asexual'),
        ('otro', 'Otro'),
        ('prefiero_no_decir', 'Prefiero no decir'),
    ]
    
    RANGO_EDAD_CHOICES = [
        ('0-17', '0-17 años'),
        ('18-25', '18-25 años'),
        ('26-35', '26-35 años'),
        ('36-45', '36-45 años'),
        ('46-55', '46-55 años'),
        ('56-65', '56-65 años'),
        ('66+', '66 años o más'),
    ]
    
    NIVEL_EDUCATIVO_CHOICES = [
        ('ninguno', 'Ninguno'),
        ('primaria', 'Primaria'),
        ('bachillerato', 'Bachillerato'),
        ('tecnico', 'Técnico'),
        ('tecnologo', 'Tecnólogo'),
        ('profesional', 'Profesional'),
        ('postgrado', 'Postgrado'),
    ]
    
    GRUPO_ETNICO_CHOICES = [
        ('ninguno', 'Ninguno'),
        ('indigena', 'Indígena'),
        ('rom', 'ROM (Gitano)'),
        ('raizal', 'Raizal'),
        ('palenquero', 'Palenquero'),
        ('negro', 'Negro(a) / Afrocolombiano(a)'),
    ]
    
    GRUPO_POBLACIONAL_CHOICES = [
        ('campesino', 'Campesino'),
        ('migrante_nacional', 'Migrante Nacional'),
        ('migrante_internacional', 'Migrante Internacional'),
        ('victima_conflicto', 'Víctima del conflicto armado'),
        ('palenquero', 'Palenquero'),
        ('veterano', 'Veterano'),
        ('ninguno', 'Ninguno'),
        ('no_responde', 'No responde'),
    ]
    
    ESTRATO_CHOICES = [
        ('1', 'Estrato 1'),
        ('2', 'Estrato 2'),
        ('3', 'Estrato 3'),
        ('4', 'Estrato 4'),
        ('5', 'Estrato 5'),
        ('6', 'Estrato 6'),
        ('7', 'No responde'),
    ]
    
    LOCALIDAD_CHOICES = [
        ('usaquen', 'Usaquén'),
        ('chapinero', 'Chapinero'),
        ('santa_fe', 'Santa Fe'),
        ('san_cristobal', 'San Cristóbal'),
        ('usme', 'Usme'),
        ('tunjuelito', 'Tunjuelito'),
        ('bosa', 'Bosa'),
        ('kennedy', 'Kennedy'),
        ('fontibon', 'Fontibón'),
        ('engativa', 'Engativá'),
        ('suba', 'Suba'),
        ('barrios_unidos', 'Barrios Unidos'),
        ('teusaquillo', 'Teusaquillo'),
        ('los_martires', 'Los Mártires'),
        ('antonio_narino', 'Antonio Nariño'),
        ('puente_aranda', 'Puente Aranda'),
        ('candelaria', 'La Candelaria'),
        ('rafael_uribe', 'Rafael Uribe Uribe'),
        ('ciudad_bolivar', 'Ciudad Bolívar'),
        ('sumapaz', 'Sumapaz'),
        ('fuera_bogota', 'No reside en Bogotá'),
    ]
    
    CALIDAD_CHOICES = [
        ('aspirante1', 'Aspirante1'),
        ('beneficiario', 'Beneficiario'),
        ('acudiente', 'Acudiente'),
        ('representante_legal', 'Representante Legal'),
        ('ciudadania_general', 'Ciudadanía en General'),
    ]
    
    # Campos de identificación (obligatorios)
    tipo_documento = models.CharField(
        max_length=5,
        choices=TIPO_DOCUMENTO_CHOICES,
        verbose_name='Tipo de Documento'
    )
    numero_documento = models.CharField(
        max_length=20,
        verbose_name='Número de Documento',
        db_index=True
    )
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')
    
    # Contacto (obligatorio)
    celular = models.CharField(max_length=15, verbose_name='Celular')
    correo_electronico = models.EmailField(verbose_name='Correo Electrónico')
    
    # Datos demográficos (todos obligatorios)
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        verbose_name='Sexo'
    )
    genero = models.CharField(
        max_length=20,
        choices=GENERO_CHOICES,
        verbose_name='Género'
    )
    orientacion_sexual = models.CharField(
        max_length=20,
        choices=ORIENTACION_SEXUAL_CHOICES,
        verbose_name='Orientación Sexual'
    )
    rango_edad = models.CharField(
        max_length=10,
        choices=RANGO_EDAD_CHOICES,
        verbose_name='Rango de Edad'
    )
    nivel_educativo = models.CharField(
        max_length=20,
        choices=NIVEL_EDUCATIVO_CHOICES,
        verbose_name='Nivel Educativo'
    )
    
    # Caracterización (todos obligatorios)
    grupo_etnico = models.CharField(
        max_length=20,
        choices=GRUPO_ETNICO_CHOICES,
        verbose_name='Grupo Étnico'
    )
    grupo_poblacional = models.CharField(
        max_length=30,
        choices=GRUPO_POBLACIONAL_CHOICES,
        verbose_name='Grupo Poblacional'
    )
    estrato_socioeconomico = models.CharField(
        max_length=1,
        choices=ESTRATO_CHOICES,
        verbose_name='Estrato Socioeconómico'
    )
    localidad = models.CharField(
        max_length=30,
        choices=LOCALIDAD_CHOICES,
        verbose_name='Localidad'
    )
    
    # Información adicional (obligatorios)
    calidad_comunicacion = models.CharField(
        max_length=30,
        choices=CALIDAD_CHOICES,
        verbose_name='Te comunicas en calidad de'
    )
    tiene_discapacidad = models.BooleanField(
        default=False,
        verbose_name='¿Tienes alguna discapacidad?'
    )
    tipo_discapacidad = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Tipo de discapacidad (si aplica)'
    )
    
    # Auditoría
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )
    
    class Meta:
        verbose_name = 'Solicitante'
        verbose_name_plural = 'Solicitantes'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['tipo_documento', 'numero_documento']),
            models.Index(fields=['numero_documento']),
            models.Index(fields=['correo_electronico']),
            models.Index(fields=['-fecha_registro']),
        ]
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.tipo_documento} {self.numero_documento}"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del solicitante"""
        return f"{self.nombre} {self.apellido}"
    
    @classmethod
    def get_ultimo_registro(cls, tipo_documento, numero_documento):
        """
        Obtiene el último registro de un solicitante por documento
        Para pre-llenar el formulario con la última información
        """
        return cls.objects.filter(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento
        ).order_by('-fecha_registro').first()
    
    @classmethod
    def get_historial_por_documento(cls, tipo_documento, numero_documento):
        """
        Obtiene todos los registros históricos de un solicitante
        """
        return cls.objects.filter(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento
        ).order_by('-fecha_registro')
    
    # ========================================
    # NUEVOS MÉTODOS PARA VALIDAR CITA ACTIVA
    # ========================================
    
    @classmethod
    def tiene_cita_activa(cls, tipo_documento, numero_documento):
        """
        Verifica si un solicitante tiene una cita activa
        
        Args:
            tipo_documento: Tipo de documento del solicitante
            numero_documento: Número de documento del solicitante
        
        Returns:
            bool: True si tiene una cita activa, False en caso contrario
        """
        return Cita.objects.filter(
            solicitante__tipo_documento=tipo_documento,
            solicitante__numero_documento=numero_documento,
            estado='agendada',
            fecha__gte=timezone.now().date()
        ).exists()
    
    @classmethod
    def get_cita_activa(cls, tipo_documento, numero_documento):
        """
        Obtiene la cita activa de un solicitante si existe
        
        Args:
            tipo_documento: Tipo de documento del solicitante
            numero_documento: Número de documento del solicitante
        
        Returns:
            Cita: La cita activa o None si no existe
        """
        return Cita.objects.filter(
            solicitante__tipo_documento=tipo_documento,
            solicitante__numero_documento=numero_documento,
            estado='agendada',
            fecha__gte=timezone.now().date()
        ).select_related('solicitante').first()
    
    def tiene_cita_activa_propia(self):
        """
        Verifica si este solicitante específico tiene una cita activa
        
        Returns:
            bool: True si tiene una cita activa, False en caso contrario
        """
        return Solicitante.tiene_cita_activa(self.tipo_documento, self.numero_documento)
    
    def get_cita_activa_propia(self):
        """
        Obtiene la cita activa de este solicitante si existe
        
        Returns:
            Cita: La cita activa o None si no existe
        """
        return Solicitante.get_cita_activa(self.tipo_documento, self.numero_documento)


class Cita(models.Model):
    """
    Modelo para gestionar las citas
    Ahora soporta tanto Usuario (legacy/asesores) como Solicitante (nuevo sistema)
    """
    ESTADO_CHOICES = [
        ('agendada', 'Agendada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
        ('no_asistio', 'No Asistió'),
    ]
    
    # Sistema antiguo (opcional para transición)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='citas',
        verbose_name='Usuario',
        null=True,
        blank=True,
        help_text='Usuario del sistema (solo para asesores/admin)'
    )
    
    # Sistema nuevo (principal)
    solicitante = models.ForeignKey(
        'Solicitante',
        on_delete=models.CASCADE,
        related_name='citas',
        verbose_name='Solicitante',
        null=True,
        blank=True,
        help_text='Persona que solicita la cita'
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
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    # ============================================
    # CAMPOS MICROSOFT TEAMS (AUTOMÁTICO)
    # ============================================
    
    url_teams = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Enlace de Microsoft Teams',
        help_text='URL de la reunión de Teams (generada automáticamente)'
    )
    
    teams_event_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='ID del Evento en Microsoft Graph',
        help_text='ID interno del evento de Teams en Microsoft Calendar'
    )
    
    teams_creado_en = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Creación de Teams',
        help_text='Timestamp de cuándo se creó la reunión de Teams'
    )
    
    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['fecha', 'hora_inicio']
        indexes = [
            models.Index(fields=['fecha', 'hora_inicio']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        if self.solicitante:
            nombre = self.solicitante.get_nombre_completo()
        elif self.usuario:
            nombre = self.usuario.get_full_name()
        else:
            nombre = "Sin asignar"
        return f"Cita de {nombre} - {self.fecha} {self.hora_inicio}"
    
    def get_nombre_solicitante(self):
        """Retorna el nombre del solicitante (nuevo o viejo sistema)"""
        if self.solicitante:
            return self.solicitante.get_nombre_completo()
        elif self.usuario:
            return self.usuario.get_full_name()
        return "Sin nombre"
    
    def get_email_solicitante(self):
        """Retorna el email del solicitante"""
        if self.solicitante:
            return self.solicitante.correo_electronico
        elif self.usuario:
            return self.usuario.email
        return None
    
    def get_telefono_solicitante(self):
        """Retorna el teléfono del solicitante"""
        if self.solicitante:
            return self.solicitante.celular
        elif self.usuario:
            return self.usuario.telefono if hasattr(self.usuario, 'telefono') else None
        return None
    
    def clean(self):
        """Validaciones personalizadas del modelo"""
        # Validar que tenga al menos un solicitante o usuario
        if not self.solicitante and not self.usuario:
            raise ValidationError('La cita debe tener un solicitante o usuario asignado.')
        
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
            
            # ========================================
            # NUEVA VALIDACIÓN: Cita activa única por solicitante
            # ========================================
            
            # Validar que el solicitante no tenga otra cita activa
            if self.solicitante:
                cita_activa = Cita.objects.filter(
                    solicitante__tipo_documento=self.solicitante.tipo_documento,
                    solicitante__numero_documento=self.solicitante.numero_documento,
                    estado='agendada',
                    fecha__gte=ahora.date()
                ).exists()
                
                if cita_activa:
                    raise ValidationError(
                        'Ya tienes una cita agendada activa. No puedes agendar otra cita hasta completar o cancelar la existente.'
                    )
            
            # Validar para usuarios del sistema antiguo
            elif self.usuario:
                cita_activa = Cita.objects.filter(
                    usuario=self.usuario,
                    estado='agendada',
                    fecha__gte=ahora.date()
                ).exists()
                
                if cita_activa:
                    raise ValidationError(
                        'Ya tienes una cita agendada activa. No puedes agendar otra cita hasta completar o cancelar la existente.'
                    )
    
    def es_horario_valido(self):
        """
        Valida si el horario está dentro de los horarios permitidos
        Martes y Miércoles: 7:00-12:40 y 14:20-16:20
        Jueves: 14:00-16:20

        Se corrige a martes miercoles jueves y viernes de 14:00 a 16:00
        """
        dia_semana = self.fecha.weekday()  # 0=Lunes, 1=Martes, ..., 6=Domingo
        
        # Solo martes (1), miércoles (2) y jueves (3)
        if dia_semana not in [1, 2, 3]:
            return False
        
        hora = self.hora_inicio
        
        return time(14, 0) <= hora <= time(16, 0)
        # if dia_semana in [1, 2]:  # Martes y Miércoles
        #     # 7:00 AM - 12:40 PM o 2:20 PM - 4:20 PM
        #     manana_valido = time(7, 0) <= hora <= time(12, 40)
        #     tarde_valido = time(14, 20) <= hora <= time(16, 20)
        #     return manana_valido or tarde_valido
        
        # elif dia_semana == 3:  # Jueves
        #     # 2:00 PM - 4:20 PM
        #     return time(14, 0) <= hora <= time(16, 20)
        
        return False
    
    def tiene_enlace_teams(self):
        """Verifica si la cita tiene enlace de Teams"""
        return bool(self.url_teams and self.url_teams.strip())
    
    def puede_crear_teams(self):
        """Verifica si se puede crear Teams automáticamente"""
        return self.estado == 'agendada' and not self.tiene_enlace_teams()
    
    def puede_eliminar_teams(self):
        """Verifica si se puede eliminar Teams automáticamente"""
        return bool(self.teams_event_id)
    
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
    
    def get_documento_solicitante(self):
        """Retorna el documento del solicitante"""
        if self.solicitante:
            return f"{self.solicitante.tipo_documento} {self.solicitante.numero_documento}"
        return "N/A"


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