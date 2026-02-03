# citas/utils.py

import logging
from datetime import datetime
from typing import Optional
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def crear_reunion_teams_automatica(cita) -> Optional[str]:
    """
    Crea una reunión de Teams automáticamente para una cita
    
    Args:
        cita: Objeto Cita confirmada
    
    Returns:
        URL de la reunión o None si falla
    """
    logger.info(f"[TEAMS] Creando reunión Teams para cita #{cita.id}")
    
    try:
        from citas.services.microsoft_teams_service import teams_service
        
        # Obtener datos usando métodos del modelo
        nombre_solicitante = cita.get_nombre_solicitante() if hasattr(cita, 'get_nombre_solicitante') else str(cita.solicitante)
        email_solicitante = cita.get_email_solicitante() if hasattr(cita, 'get_email_solicitante') else cita.solicitante.email
        
        # Preparar datos
        asunto = f"Cita ATENEA - {nombre_solicitante}"
        
        # Combinar fecha y hora
        fecha_inicio = datetime.combine(cita.fecha, cita.hora_inicio)
        
        # Hacer timezone-aware si es necesario
        if timezone.is_naive(fecha_inicio):
            fecha_inicio = timezone.make_aware(fecha_inicio)
        
        # Obtener tipo de documento y número
        try:
            tipo_doc = cita.get_tipo_documento_display() if hasattr(cita, 'get_tipo_documento_display') else cita.tipo_documento
            numero_doc = cita.numero_documento if hasattr(cita, 'numero_documento') else 'N/A'
        except:
            tipo_doc = 'Documento'
            numero_doc = 'N/A'
        
        # Obtener tipo de atención
        try:
            tipo_atencion = cita.get_tipo_atencion_display() if hasattr(cita, 'get_tipo_atencion_display') else cita.tipo_atencion
        except:
            tipo_atencion = 'Virtual'
        
        # Obtener motivo
        try:
            motivo = cita.motivo if hasattr(cita, 'motivo') else cita.get_motivo() if hasattr(cita, 'get_motivo') else 'Consulta general'
        except:
            motivo = 'Consulta general'
        
        # Descripción HTML
        descripcion = f"""
        <div style="font-family: Arial, sans-serif;">
            <h2 style="color: #5b47d6;">Cita de Atención ATENEA</h2>
            <table style="border-collapse: collapse; width: 100%;">
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Solicitante:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{nombre_solicitante}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Email:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{email_solicitante}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Documento:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{tipo_doc} {numero_doc}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Tipo de Atención:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{tipo_atencion}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Motivo:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{motivo}</td>
                </tr>
            </table>
        </div>
        """
        
        # Asistentes
        asistentes = [email_solicitante]
        
        # Duración
        duracion = cita.duracion_minutos if hasattr(cita, 'duracion_minutos') else 30
        
        # Crear reunión
        reunion_info = teams_service.crear_reunion_teams(
            asunto=asunto,
            fecha_inicio=fecha_inicio,
            duracion_minutos=duracion,
            descripcion=descripcion,
            asistentes=asistentes
        )
        
        if reunion_info and reunion_info.get('join_url'):
            # Guardar en la cita
            cita.teams_event_id = reunion_info.get('id')
            cita.url_teams = reunion_info.get('join_url')
            cita.teams_creado_en = timezone.now()
            cita.save(update_fields=['teams_event_id', 'url_teams', 'teams_creado_en'])
            
            logger.info(f"[OK] Reunión Teams creada para cita #{cita.id}: {cita.url_teams}")
            
            # Enviar email al solicitante
            try:
                enviar_email_teams_creado(cita)
            except Exception as e:
                logger.error(f"[ERROR] No se pudo enviar email: {str(e)}")
            
            return reunion_info.get('join_url')
        else:
            logger.error(f"[ERROR] No se pudo crear reunión Teams para cita #{cita.id}")
            return None
            
    except ImportError:
        logger.error("[ERROR] Servicio de Teams no disponible")
        return None
    except Exception as e:
        logger.error(f"[ERROR] Error creando reunión: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def eliminar_reunion_teams_automatica(cita) -> bool:
    """
    Elimina una reunión de Teams automáticamente
    
    Args:
        cita: Objeto Cita con teams_event_id
    
    Returns:
        True si se eliminó exitosamente
    """
    if not cita.teams_event_id:
        logger.warning(f"[WARN] Cita #{cita.id} no tiene teams_event_id")
        return False
    
    logger.info(f"[TEAMS] Eliminando reunión Teams de cita #{cita.id}")
    
    try:
        from citas.services.microsoft_teams_service import teams_service
        
        resultado = teams_service.eliminar_reunion_teams(cita.teams_event_id)
        
        if resultado:
            logger.info(f"[OK] Reunión Teams eliminada para cita #{cita.id}")
            # Limpiar campos
            cita.teams_event_id = None
            cita.url_teams = None
            cita.teams_creado_en = None
            cita.save(update_fields=['teams_event_id', 'url_teams', 'teams_creado_en'])
        
        return resultado
        
    except Exception as e:
        logger.error(f"[ERROR] Error eliminando reunión: {str(e)}")
        return False


def actualizar_reunion_teams_automatica(cita) -> bool:
    """
    Actualiza una reunión de Teams si cambió la fecha/hora
    
    Args:
        cita: Objeto Cita con teams_event_id
    
    Returns:
        True si se actualizó exitosamente
    """
    if not cita.teams_event_id:
        return False
    
    logger.info(f"[TEAMS] Actualizando reunión Teams de cita #{cita.id}")
    
    try:
        from citas.services.microsoft_teams_service import teams_service
        
        nombre_solicitante = cita.get_nombre_solicitante() if hasattr(cita, 'get_nombre_solicitante') else str(cita.solicitante)
        asunto = f"Cita ATENEA - {nombre_solicitante}"
        fecha_inicio = datetime.combine(cita.fecha, cita.hora_inicio)
        
        if timezone.is_naive(fecha_inicio):
            fecha_inicio = timezone.make_aware(fecha_inicio)
        
        duracion = cita.duracion_minutos if hasattr(cita, 'duracion_minutos') else 30
        
        resultado = teams_service.actualizar_reunion_teams(
            event_id=cita.teams_event_id,
            asunto=asunto,
            fecha_inicio=fecha_inicio,
            duracion_minutos=duracion
        )
        
        if resultado:
            logger.info(f"[OK] Reunión Teams actualizada para cita #{cita.id}")
            # Enviar email de actualización
            try:
                enviar_email_teams_actualizado(cita)
            except Exception as e:
                logger.error(f"[ERROR] No se pudo enviar email de actualización: {str(e)}")
        
        return resultado
        
    except Exception as e:
        logger.error(f"[ERROR] Error actualizando reunión: {str(e)}")
        return False


def enviar_email_teams_creado(cita):
    """Envía email cuando se crea el enlace de Teams"""
    
    # Obtener datos del modelo
    nombre_solicitante = cita.get_nombre_solicitante() if hasattr(cita, 'get_nombre_solicitante') else str(cita.solicitante)
    email_solicitante = cita.get_email_solicitante() if hasattr(cita, 'get_email_solicitante') else cita.solicitante.email
    
    asunto = f'🎉 Reunión de Teams lista - Cita {cita.fecha.strftime("%d/%m/%Y")}'
    
    # Obtener campos adicionales con manejo de errores
    try:
        tipo_atencion = cita.get_tipo_atencion_display() if hasattr(cita, 'get_tipo_atencion_display') else 'Virtual'
    except:
        tipo_atencion = 'Virtual'
    
    try:
        motivo = cita.motivo if hasattr(cita, 'motivo') else cita.get_motivo() if hasattr(cita, 'get_motivo') else 'Consulta'
    except:
        motivo = 'Consulta'
    
    try:
        duracion = cita.duracion_minutos if hasattr(cita, 'duracion_minutos') else 30
    except:
        duracion = 30
    
    contexto = {
        'cita': cita,
        'nombre_solicitante': nombre_solicitante,
        'fecha': cita.fecha.strftime('%d/%m/%Y'),
        'hora': cita.hora_inicio.strftime('%H:%M'),
        'url_teams': cita.url_teams,
        'motivo': motivo,
        'tipo_atencion': tipo_atencion,
        'duracion': duracion,
    }
    
    html_message = render_to_string('emails/teams_creado.html', contexto)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=asunto,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email_solicitante],
        html_message=html_message,
        fail_silently=False,
    )
    
    logger.info(f"[EMAIL] Email de Teams enviado a {email_solicitante}")


def enviar_email_teams_actualizado(cita):
    """Envía email cuando se actualiza la reunión de Teams"""
    
    nombre_solicitante = cita.get_nombre_solicitante() if hasattr(cita, 'get_nombre_solicitante') else str(cita.solicitante)
    email_solicitante = cita.get_email_solicitante() if hasattr(cita, 'get_email_solicitante') else cita.solicitante.email
    
    asunto = f'🔄 Reunión de Teams actualizada - Cita {cita.fecha.strftime("%d/%m/%Y")}'
    
    try:
        tipo_atencion = cita.get_tipo_atencion_display() if hasattr(cita, 'get_tipo_atencion_display') else 'Virtual'
    except:
        tipo_atencion = 'Virtual'
    
    try:
        motivo = cita.motivo if hasattr(cita, 'motivo') else cita.get_motivo() if hasattr(cita, 'get_motivo') else 'Consulta'
    except:
        motivo = 'Consulta'
    
    contexto = {
        'cita': cita,
        'nombre_solicitante': nombre_solicitante,
        'fecha': cita.fecha.strftime('%d/%m/%Y'),
        'hora': cita.hora_inicio.strftime('%H:%M'),
        'url_teams': cita.url_teams,
        'motivo': motivo,
        'tipo_atencion': tipo_atencion,
    }
    
    html_message = render_to_string('emails/teams_actualizado.html', contexto)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=asunto,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email_solicitante],
        html_message=html_message,
        fail_silently=False,
    )
    
    logger.info(f"[EMAIL] Email de actualización enviado a {email_solicitante}")