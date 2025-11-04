from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser
    """
    TIPO_USUARIO_CHOICES = [
        ('cliente', 'Cliente'),
        ('asesor', 'Asesor'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=10,
        choices=TIPO_USUARIO_CHOICES,
        default='cliente',
        verbose_name='Tipo de Usuario'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    def es_asesor(self):
        """Verifica si el usuario es un asesor"""
        return self.tipo_usuario == 'asesor'
    
    def es_cliente(self):
        """Verifica si el usuario es un cliente"""
        return self.tipo_usuario == 'cliente'

