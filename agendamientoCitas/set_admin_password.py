#!/usr/bin/env python
"""
Script para establecer la contraseña del superusuario
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from usuarios.models import Usuario

# Establecer contraseña para el admin
try:
    admin = Usuario.objects.get(username='admin')
    admin.set_password('admin123')
    admin.tipo_usuario = 'asesor'
    admin.save()
    print("✓ Contraseña establecida para el usuario 'admin'")
    print("  Username: admin")
    print("  Password: admin123")
except Usuario.DoesNotExist:
    print("✗ Usuario admin no encontrado")
