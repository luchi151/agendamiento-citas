from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def enviar_email_confirmacion_cita(cita):
    """
    Envía email de confirmación al agendar una cita
    
    Args:
        cita: Objeto Cita que fue creado
    
    Returns:
        bool: True si el email se envió correctamente, False en caso contrario
    """
    try:
        # Preparar contexto para el template
        context = {
            'cita': cita,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        }
        
        # Renderizar template HTML
        html_content = render_to_string('emails/confirmacion_cita.html', context)
        
        # Crear versión texto plano (fallback)
        text_content = strip_tags(html_content)
        
        # Preparar email
        subject = f'Confirmación de Cita - {cita.fecha.strftime("%d/%m/%Y")}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [cita.solicitante.correo_electronico]
        
        # Crear mensaje
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to_email
        )
        
        # Adjuntar versión HTML
        msg.attach_alternative(html_content, "text/html")
        
        # Enviar
        msg.send()
        
        return True
        
    except Exception as e:
        # Log del error (en producción usar logging apropiado)
        print(f"Error al enviar email de confirmación: {str(e)}")
        return False


def enviar_email_cancelacion_cita(cita):
    """
    Envía email de confirmación al cancelar una cita
    
    Args:
        cita: Objeto Cita que fue cancelado
    
    Returns:
        bool: True si el email se envió correctamente, False en caso contrario
    """
    try:
        # Preparar contexto para el template
        context = {
            'cita': cita,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        }
        
        # Renderizar template HTML
        html_content = render_to_string('emails/cancelacion_cita.html', context)
        
        # Crear versión texto plano (fallback)
        text_content = strip_tags(html_content)
        
        # Preparar email
        subject = f'Cita Cancelada - {cita.fecha.strftime("%d/%m/%Y")}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [cita.solicitante.correo_electronico]
        
        # Crear mensaje
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to_email
        )
        
        # Adjuntar versión HTML
        msg.attach_alternative(html_content, "text/html")
        
        # Enviar
        msg.send()
        
        return True
        
    except Exception as e:
        # Log del error (en producción usar logging apropiado)
        print(f"Error al enviar email de cancelación: {str(e)}")
        return False


def enviar_email_recordatorio_cita(cita):
    """
    Envía email recordatorio 24 horas antes de la cita
    (Para implementar con Celery o cron job)
    
    Args:
        cita: Objeto Cita próxima
    
    Returns:
        bool: True si el email se envió correctamente, False en caso contrario
    """
    try:
        # Preparar contexto para el template
        context = {
            'cita': cita,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        }
        
        # Renderizar template HTML (crear después si lo necesitas)
        # html_content = render_to_string('emails/recordatorio_cita.html', context)
        
        # Por ahora, texto simple
        subject = f'Recordatorio: Cita Mañana - {cita.fecha.strftime("%d/%m/%Y")}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [cita.solicitante.correo_electronico]
        
        message = f"""
        Hola {cita.solicitante.nombre} {cita.solicitante.apellido},
        
        Te recordamos que tienes una cita agendada para mañana:
        
        Fecha: {cita.fecha.strftime("%d de %B de %Y")}
        Hora: {cita.hora_inicio.strftime("%I:%M %p")} - {cita.hora_fin.strftime("%I:%M %p")}
        
        Por favor, conéctate a tiempo.
        
        Saludos,
        Sistema de Agendamiento ATENEA
        """
        
        # Crear y enviar mensaje
        msg = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=from_email,
            to=to_email
        )
        
        msg.send()
        
        return True
        
    except Exception as e:
        print(f"Error al enviar email recordatorio: {str(e)}")
        return False