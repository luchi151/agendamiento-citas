import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 50)
print("PROBANDO CONEXIÓN DE EMAIL")
print("=" * 50)
print(f"Host: {settings.EMAIL_HOST}")
print(f"Puerto: {settings.EMAIL_PORT}")
print(f"Usuario: {settings.EMAIL_HOST_USER}")
print(f"TLS: {settings.EMAIL_USE_TLS}")
print("=" * 50)

# Email de destino para prueba
destinatario = input("Ingresa tu email personal para la prueba: ")

try:
    print("\nEnviando email de prueba...")
    send_mail(
        subject='🧪 Prueba de Email - Sistema ATENEA',
        message='Este es un email de prueba del sistema de agendamiento ATENEA.\n\nSi recibiste este mensaje, la configuración es correcta.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[destinatario],
        fail_silently=False,
    )
    print("\n✅ ¡EMAIL ENVIADO EXITOSAMENTE!")
    print(f"✅ Revisa la bandeja de entrada de: {destinatario}")
    print("✅ (También revisa spam/correo no deseado)")
except Exception as e:
    print(f"\n❌ ERROR AL ENVIAR EMAIL:")
    print(f"❌ {str(e)}")
    print("\n💡 Posibles soluciones:")
    print("  1. Verifica la contraseña en el archivo .env")
    print("  2. Si la cuenta tiene MFA, genera una contraseña de aplicación")
    print("  3. Contacta al admin de TI para habilitar SMTP AUTH")