#!/usr/bin/env python
"""
Script para crear datos de prueba en el sistema
"""
import os
import django
from datetime import datetime, timedelta, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from usuarios.models import Usuario
from citas.models import Cita

def crear_usuarios_prueba():
    """Crear usuarios de prueba"""
    print("Creando usuarios de prueba...")
    
    # Cliente 1
    if not Usuario.objects.filter(username='cliente1').exists():
        cliente1 = Usuario.objects.create_user(
            username='cliente1',
            email='cliente1@test.com',
            password='cliente123',
            first_name='Juan',
            last_name='Pérez',
            tipo_usuario='cliente',
            telefono='3001234567'
        )
        print(f"✓ Usuario creado: {cliente1.username}")
    else:
        print("• Usuario cliente1 ya existe")
    
    # Cliente 2
    if not Usuario.objects.filter(username='cliente2').exists():
        cliente2 = Usuario.objects.create_user(
            username='cliente2',
            email='cliente2@test.com',
            password='cliente123',
            first_name='María',
            last_name='González',
            tipo_usuario='cliente',
            telefono='3007654321'
        )
        print(f"✓ Usuario creado: {cliente2.username}")
    else:
        print("• Usuario cliente2 ya existe")
    
    # Asesor adicional
    if not Usuario.objects.filter(username='asesor1').exists():
        asesor1 = Usuario.objects.create_user(
            username='asesor1',
            email='asesor1@test.com',
            password='asesor123',
            first_name='Carlos',
            last_name='Rodríguez',
            tipo_usuario='asesor',
            telefono='3009876543',
            is_staff=True
        )
        print(f"✓ Asesor creado: {asesor1.username}")
    else:
        print("• Usuario asesor1 ya existe")

def crear_citas_prueba():
    """Crear algunas citas de prueba"""
    print("\nCreando citas de prueba...")
    
    try:
        cliente1 = Usuario.objects.get(username='cliente1')
        
        # Calcular próximo martes
        hoy = timezone.now().date()
        dias_hasta_martes = (1 - hoy.weekday()) % 7
        if dias_hasta_martes == 0:
            dias_hasta_martes = 7  # Próxima semana si hoy es martes
        
        proximo_martes = hoy + timedelta(days=dias_hasta_martes)
        
        # Crear cita de prueba
        if not Cita.objects.filter(usuario=cliente1, fecha=proximo_martes).exists():
            cita = Cita.objects.create(
                usuario=cliente1,
                fecha=proximo_martes,
                hora_inicio=time(10, 0),
                hora_fin=time(10, 20),
                estado='agendada',
                motivo='Cita de prueba - Consulta general',
                url_teams='https://teams.microsoft.com/example'
            )
            print(f"✓ Cita creada: {cita}")
        else:
            print("• Ya existe una cita de prueba para cliente1")
            
    except Usuario.DoesNotExist:
        print("✗ No se encontró el usuario cliente1. Ejecuta primero crear_usuarios_prueba()")

def mostrar_resumen():
    """Mostrar resumen del sistema"""
    print("\n" + "="*50)
    print("RESUMEN DEL SISTEMA")
    print("="*50)
    
    total_usuarios = Usuario.objects.count()
    clientes = Usuario.objects.filter(tipo_usuario='cliente').count()
    asesores = Usuario.objects.filter(tipo_usuario='asesor').count()
    
    print(f"\n👥 USUARIOS:")
    print(f"   Total: {total_usuarios}")
    print(f"   Clientes: {clientes}")
    print(f"   Asesores: {asesores}")
    
    total_citas = Cita.objects.count()
    citas_agendadas = Cita.objects.filter(estado='agendada').count()
    citas_completadas = Cita.objects.filter(estado='completada').count()
    citas_canceladas = Cita.objects.filter(estado='cancelada').count()
    
    print(f"\n📅 CITAS:")
    print(f"   Total: {total_citas}")
    print(f"   Agendadas: {citas_agendadas}")
    print(f"   Completadas: {citas_completadas}")
    print(f"   Canceladas: {citas_canceladas}")
    
    print("\n" + "="*50)
    print("CREDENCIALES DE ACCESO")
    print("="*50)
    print("\n🔑 ADMIN:")
    print("   Usuario: admin")
    print("   Password: admin123")
    print("   Tipo: Asesor/Staff")
    
    print("\n🔑 ASESOR:")
    print("   Usuario: asesor1")
    print("   Password: asesor123")
    print("   Tipo: Asesor")
    
    print("\n🔑 CLIENTES:")
    print("   Usuario: cliente1")
    print("   Password: cliente123")
    print("   Tipo: Cliente")
    
    print("\n   Usuario: cliente2")
    print("   Password: cliente123")
    print("   Tipo: Cliente")
    print("\n" + "="*50 + "\n")

if __name__ == '__main__':
    print("="*50)
    print("GENERADOR DE DATOS DE PRUEBA")
    print("="*50)
    
    crear_usuarios_prueba()
    crear_citas_prueba()
    mostrar_resumen()
    
    print("✓ Datos de prueba creados exitosamente!")
