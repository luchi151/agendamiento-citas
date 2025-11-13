from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@shared_task
def enviar_email_confirmacion_cita(cita_id):
    """
    Tarea para enviar email de confirmación de cita
    """
    from .models import Cita
    
    try:
        cita = Cita.objects.get(id=cita_id)
        usuario = cita.usuario
        
        subject = f'Confirmación de Cita - {cita.fecha.strftime("%d/%m/%Y")}'
        
        # Contexto para el template del email
        context = {
            'usuario': usuario,
            'cita': cita,
            'fecha_formateada': cita.fecha.strftime('%d de %B de %Y'),
            'hora_formateada': cita.hora_inicio.strftime('%I:%M %p'),
        }
        
        # Renderizar template HTML (crear después)
        # html_message = render_to_string('citas/emails/confirmacion_cita.html', context)
        # message = strip_tags(html_message)
        
        message = f"""
Hola {usuario.get_full_name()},

Tu cita ha sido agendada exitosamente:

📅 Fecha: {cita.fecha.strftime('%d de %B de %Y')}
🕐 Hora: {cita.hora_inicio.strftime('%I:%M %p')} - {cita.hora_fin.strftime('%I:%M %p')}

Recuerda:
- Puedes cancelar tu cita con al menos 2 horas de anticipación
- Recibirás el enlace de la reunión de Teams antes de tu cita

¡Gracias por usar nuestro sistema!
"""
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.email],
            fail_silently=False,
        )
        
        return f'Email enviado a {usuario.email}'
    
    except Cita.DoesNotExist:
        return f'Cita con ID {cita_id} no encontrada'
    except Exception as e:
        return f'Error al enviar email: {str(e)}'


@shared_task
def enviar_email_cancelacion_cita(cita_id, usuario_email, fecha, hora):
    """
    Tarea para enviar email de cancelación de cita
    """
    subject = f'Cancelación de Cita - {fecha}'
    
    message = f"""
Tu cita ha sido cancelada:

📅 Fecha: {fecha}
🕐 Hora: {hora}

Este horario ahora está disponible para otros usuarios.

Si deseas agendar una nueva cita, puedes hacerlo desde nuestra plataforma.

¡Gracias!
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [usuario_email],
            fail_silently=False,
        )
        return f'Email de cancelación enviado a {usuario_email}'
    except Exception as e:
        return f'Error al enviar email: {str(e)}'


@shared_task
def enviar_recordatorio_cita(cita_id):
    """
    Tarea para enviar recordatorio de cita (1 hora antes)
    """
    from .models import Cita
    
    try:
        cita = Cita.objects.get(id=cita_id, estado='agendada')
        usuario = cita.usuario
        
        subject = f'Recordatorio: Tu cita es en 1 hora'
        
        message = f"""
Hola {usuario.get_full_name()},

Este es un recordatorio de que tu cita es en 1 hora:

📅 Fecha: {cita.fecha.strftime('%d de %B de %Y')}
🕐 Hora: {cita.hora_inicio.strftime('%I:%M %p')}

Enlace de la reunión: {cita.url_teams if cita.url_teams else 'Por confirmar'}

¡Te esperamos!
"""
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.email],
            fail_silently=False,
        )
        
        return f'Recordatorio enviado a {usuario.email}'
    
    except Cita.DoesNotExist:
        return f'Cita con ID {cita_id} no encontrada o ya no está agendada'
    except Exception as e:
        return f'Error al enviar recordatorio: {str(e)}'
