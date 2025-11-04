from django.contrib import admin
from django.utils.html import format_html
from .models import Cita, Interaccion, DisponibilidadHoraria


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Cita"""
    
    list_display = [
        'id',
        'usuario_info',
        'fecha',
        'hora_inicio',
        'hora_fin',
        'estado_badge',
        'fecha_creacion'
    ]
    list_filter = ['estado', 'fecha', 'fecha_creacion']
    search_fields = [
        'usuario__username',
        'usuario__email',
        'usuario__first_name',
        'usuario__last_name',
        'motivo'
    ]
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('usuario',)
        }),
        ('Detalles de la Cita', {
            'fields': ('fecha', 'hora_inicio', 'hora_fin', 'estado', 'motivo')
        }),
        ('Enlace de Reunión', {
            'fields': ('url_teams',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def usuario_info(self, obj):
        return f"{obj.usuario.get_full_name()} ({obj.usuario.email})"
    usuario_info.short_description = 'Usuario'
    
    def estado_badge(self, obj):
        colors = {
            'agendada': '#28a745',
            'cancelada': '#dc3545',
            'completada': '#007bff',
            'no_asistio': '#ffc107',
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('usuario')


@admin.register(Interaccion)
class InteraccionAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Interacción"""
    
    list_display = [
        'id_interaccion',
        'cita_info',
        'asesor',
        'resultado',
        'fecha_registro'
    ]
    list_filter = ['resultado', 'fecha_registro']
    search_fields = [
        'id_interaccion',
        'cita__usuario__username',
        'cita__usuario__email',
        'asesor__username',
        'observaciones'
    ]
    readonly_fields = ['id_interaccion', 'fecha_registro']
    
    fieldsets = (
        ('Información de la Cita', {
            'fields': ('cita', 'asesor')
        }),
        ('Resultado de la Interacción', {
            'fields': ('id_interaccion', 'resultado', 'observaciones')
        }),
        ('Auditoría', {
            'fields': ('fecha_registro',)
        }),
    )
    
    def cita_info(self, obj):
        return f"{obj.cita.usuario.get_full_name()} - {obj.cita.fecha} {obj.cita.hora_inicio}"
    cita_info.short_description = 'Cita'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('cita__usuario', 'asesor')


@admin.register(DisponibilidadHoraria)
class DisponibilidadHorariaAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo DisponibilidadHoraria"""
    
    list_display = [
        'fecha',
        'hora_inicio',
        'hora_fin',
        'disponible_badge',
        'motivo'
    ]
    list_filter = ['disponible', 'fecha']
    search_fields = ['motivo']
    date_hierarchy = 'fecha'
    
    def disponible_badge(self, obj):
        if obj.disponible:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Disponible</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Bloqueado</span>'
            )
    disponible_badge.short_description = 'Estado'

