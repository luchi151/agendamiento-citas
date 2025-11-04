from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Configuración del admin para el modelo Usuario"""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'is_active', 'is_staff']
    list_filter = ['tipo_usuario', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('tipo_usuario', 'telefono')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('tipo_usuario', 'telefono', 'email', 'first_name', 'last_name')
        }),
    )

