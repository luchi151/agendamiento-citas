# citas/management/commands/verificar_teams.py

from django.core.management.base import BaseCommand
from django.conf import settings
import sys


class Command(BaseCommand):
    help = 'Verifica la configuración de Microsoft Teams (Modo Automático)'
    
    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS(
            "🔍 VERIFICACIÓN DE CONFIGURACIÓN - MICROSOFT TEAMS AUTOMÁTICO"
        ))
        self.stdout.write("=" * 70)
        self.stdout.write("")
        
        # Verificar credenciales
        self.stdout.write("🔐 Verificando Credenciales de Azure AD...")
        self.stdout.write("")
        
        credenciales = {
            'MICROSOFT_TENANT_ID': settings.MICROSOFT_TENANT_ID,
            'MICROSOFT_CLIENT_ID': settings.MICROSOFT_CLIENT_ID,
            'MICROSOFT_CLIENT_SECRET': settings.MICROSOFT_CLIENT_SECRET,
            'MICROSOFT_TEAMS_USER_ID': settings.MICROSOFT_TEAMS_USER_ID,
        }
        
        todas_ok = True
        for key, value in credenciales.items():
            if value:
                # Mostrar solo primeros caracteres por seguridad
                valor_mostrar = f"{value[:10]}..." if len(value) > 10 else value
                self.stdout.write(f"  ✅ {key}: {self.style.SUCCESS(valor_mostrar)}")
            else:
                self.stdout.write(f"  ❌ {key}: {self.style.ERROR('NO CONFIGURADO')}")
                todas_ok = False
        
        self.stdout.write("")
        
        if not todas_ok:
            self.stdout.write(self.style.ERROR(
                "⚠️  FALTAN CREDENCIALES DE AZURE AD"
            ))
            self.stdout.write("")
            self.stdout.write("Para configurar:")
            self.stdout.write("1. Leer: AZURE_AD_SETUP.md")
            self.stdout.write("2. Obtener credenciales de Azure Portal")
            self.stdout.write("3. Agregar en archivo .env")
            self.stdout.write("")
            self.stdout.write("=" * 70)
            sys.exit(1)
        
        # Probar dependencias
        self.stdout.write("📦 Verificando Dependencias...")
        self.stdout.write("")
        
        try:
            import msal
            self.stdout.write(f"  ✅ msal: {self.style.SUCCESS('Instalado')}")
        except ImportError:
            self.stdout.write(f"  ❌ msal: {self.style.ERROR('NO INSTALADO')}")
            self.stdout.write("     Ejecutar: pip install msal")
            todas_ok = False
        
        try:
            import requests
            self.stdout.write(f"  ✅ requests: {self.style.SUCCESS('Instalado')}")
        except ImportError:
            self.stdout.write(f"  ❌ requests: {self.style.ERROR('NO INSTALADO')}")
            self.stdout.write("     Ejecutar: pip install requests")
            todas_ok = False
        
        self.stdout.write("")
        
        if not todas_ok:
            self.stdout.write(self.style.ERROR(
                "⚠️  FALTAN DEPENDENCIAS"
            ))
            self.stdout.write("Ejecutar: pip install -r requirements_teams.txt")
            self.stdout.write("")
            self.stdout.write("=" * 70)
            sys.exit(1)
        
        # Probar conexión con Graph API
        self.stdout.write("🌐 Probando Conexión con Microsoft Graph API...")
        self.stdout.write("")
        
        try:
            from citas.services.microsoft_teams_service import teams_service
            
            if teams_service.verificar_conexion():
                self.stdout.write(self.style.SUCCESS(
                    "✅ CONEXIÓN EXITOSA"
                ))
                self.stdout.write("")
                self.stdout.write("El sistema puede crear reuniones de Teams automáticamente.")
            else:
                self.stdout.write(self.style.ERROR(
                    "❌ ERROR DE CONEXIÓN"
                ))
                self.stdout.write("")
                self.stdout.write("Posibles causas:")
                self.stdout.write("  • Credenciales incorrectas")
                self.stdout.write("  • Falta 'Admin Consent' en Azure AD")
                self.stdout.write("  • Usuario (USER_ID) no existe")
                self.stdout.write("  • Permisos insuficientes")
                self.stdout.write("")
                self.stdout.write("Revisar: AZURE_AD_SETUP.md")
                sys.exit(1)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"❌ EXCEPCIÓN: {str(e)}"
            ))
            self.stdout.write("")
            sys.exit(1)
        
        # Resumen final
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS(
            "🎉 CONFIGURACIÓN COMPLETADA Y VERIFICADA"
        ))
        self.stdout.write("")
        self.stdout.write("El sistema está listo para:")
        self.stdout.write("  ✅ Crear reuniones de Teams automáticamente")
        self.stdout.write("  ✅ Eliminar reuniones cuando se cancelen citas")
        self.stdout.write("  ✅ Actualizar reuniones si cambia la fecha/hora")
        self.stdout.write("  ✅ Enviar emails con enlaces de Teams")
        self.stdout.write("")
        self.stdout.write("🚀 ¡Todo listo para usar!")
        self.stdout.write("=" * 70)
