from django.contrib import admin
from .models import Cita, Solicitante, Interaccion, DisponibilidadHoraria


@admin.register(Solicitante)
class SolicitanteAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Solicitante
    """
    list_display = [
        'numero_documento', 
        'tipo_documento', 
        'get_nombre_completo',
        'celular',
        'correo_electronico',
        'fecha_registro'
    ]
    list_filter = [
        'tipo_documento',
        'sexo',
        'rango_edad',
        'localidad',
        'fecha_registro'
    ]
    search_fields = [
        'numero_documento',
        'nombre',
        'apellido',
        'correo_electronico',
        'celular'
    ]
    readonly_fields = ['fecha_registro']
    
    fieldsets = (
        ('Identificación', {
            'fields': ('tipo_documento', 'numero_documento', 'nombre', 'apellido')
        }),
        ('Contacto', {
            'fields': ('celular', 'correo_electronico')
        }),
        ('Datos Demográficos', {
            'fields': (
                'sexo',
                'genero', 
                'orientacion_sexual',
                'rango_edad',
                'nivel_educativo'
            )
        }),
        ('Caracterización', {
            'fields': (
                'grupo_etnico',
                'grupo_poblacional',
                'estrato_socioeconomico',
                'localidad'
            )
        }),
        ('Información Adicional', {
            'fields': (
                'calidad_comunicacion',
                'tiene_discapacidad',
                'tipo_discapacidad'
            )
        }),
        ('Auditoría', {
            'fields': ('fecha_registro',),
            'classes': ('collapse',)
        }),
    )
    
    def get_nombre_completo(self, obj):
        return obj.get_nombre_completo()
    get_nombre_completo.short_description = 'Nombre Completo'


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Cita
    """
    list_display = [
        'id',
        'get_nombre_solicitante',
        'get_documento',
        'fecha',
        'hora_inicio',
        'estado',
        'fecha_creacion'
    ]
    list_filter = [
        'estado',
        'fecha',
        'fecha_creacion'
    ]
    search_fields = [
        'solicitante__numero_documento',
        'solicitante__nombre',
        'solicitante__apellido',
        'usuario__username'
    ]
    readonly_fields = [
        'fecha_creacion',
        'fecha_actualizacion'
    ]
    
    fieldsets = (
        ('Solicitante', {
            'fields': ('solicitante', 'usuario'),
            'description': 'Selecciona el solicitante (sistema nuevo) o usuario (sistema antiguo)'
        }),
        ('Información de la Cita', {
            'fields': (
                'fecha',
                'hora_inicio',
                'hora_fin',
                'estado',
                'motivo',
                'url_teams'
            )
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_nombre_solicitante(self, obj):
        return obj.get_nombre_solicitante()
    get_nombre_solicitante.short_description = 'Solicitante'
    
    def get_documento(self, obj):
        return obj.get_documento_solicitante()
    get_documento.short_description = 'Documento'
    
    # Personalizar el formulario para mostrar datos relevantes
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "solicitante":
            # Mostrar solicitantes ordenados por fecha de registro
            kwargs["queryset"] = Solicitante.objects.all().order_by('-fecha_registro')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Interaccion)
class InteraccionAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Interaccion
    """
    list_display = [
        'id_interaccion',
        'cita',
        'asesor',
        'resultado',
        'fecha_registro'
    ]
    list_filter = [
        'resultado',
        'fecha_registro'
    ]
    search_fields = [
        'id_interaccion',
        'cita__solicitante__numero_documento',
        'asesor__username',
        'observaciones'
    ]
    readonly_fields = [
        'id_interaccion',
        'fecha_registro'
    ]
    
    fieldsets = (
        ('Información de la Interacción', {
            'fields': (
                'cita',
                'asesor',
                'resultado',
                'observaciones'
            )
        }),
        ('Auditoría', {
            'fields': ('id_interaccion', 'fecha_registro'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DisponibilidadHoraria)
class DisponibilidadHorariaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para DisponibilidadHoraria
    """
    list_display = [
        'fecha',
        'hora_inicio',
        'hora_fin',
        'disponible',
        'motivo'
    ]
    list_filter = [
        'disponible',
        'fecha'
    ]
    search_fields = [
        'motivo'
    ]
    
    fieldsets = (
        ('Horario', {
            'fields': (
                'fecha',
                'hora_inicio',
                'hora_fin'
            )
        }),
        ('Disponibilidad', {
            'fields': (
                'disponible',
                'motivo'
            )
        }),
    )
