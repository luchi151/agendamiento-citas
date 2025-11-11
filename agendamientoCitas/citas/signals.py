# citas/signals.py

import logging
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from .models import Cita
from .utils import (
    crear_reunion_teams_automatica,
    eliminar_reunion_teams_automatica,
    actualizar_reunion_teams_automatica
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Cita)
def crear_teams_al_confirmar(sender, instance, created, **kwargs):
    """
    Signal: Crea reunión de Teams automáticamente cuando se confirma/agenda una cita
    """
    # Cambiar 'CONFIRMADA' por 'agendada' según tu modelo
    if instance.estado == 'agendada' and not instance.tiene_enlace_teams():
        logger.info(f"[SIGNAL] Cita #{instance.id} agendada, creando Teams automáticamente")
        
        try:
            url_teams = crear_reunion_teams_automatica(instance)
            
            if url_teams:
                logger.info(f"[SIGNAL] Teams creado exitosamente para cita #{instance.id}")
            else:
                logger.error(f"[SIGNAL] Falló creación de Teams para cita #{instance.id}")
                
        except Exception as e:
            logger.error(f"[SIGNAL] Excepción en crear_teams: {str(e)}")


@receiver(pre_delete, sender=Cita)
def eliminar_teams_al_borrar(sender, instance, **kwargs):
    """
    Signal: Elimina reunión de Teams cuando se borra una cita
    """
    if instance.puede_eliminar_teams():
        logger.info(f"[SIGNAL] Cita #{instance.id} eliminada, borrando Teams")
        
        try:
            eliminado = eliminar_reunion_teams_automatica(instance)
            
            if eliminado:
                logger.info(f"[SIGNAL] Teams eliminado para cita #{instance.id}")
            else:
                logger.warning(f"[SIGNAL] No se pudo eliminar Teams de cita #{instance.id}")
                
        except Exception as e:
            logger.error(f"[SIGNAL] Excepción en eliminar_teams: {str(e)}")


@receiver(post_save, sender=Cita)
def eliminar_teams_si_cancela(sender, instance, **kwargs):
    """
    Signal: Elimina Teams si la cita cambia a cancelada
    """
    if instance.estado == 'cancelada' and instance.puede_eliminar_teams():
        logger.info(f"[SIGNAL] Cita #{instance.id} cancelada, eliminando Teams")
        
        try:
            eliminar_reunion_teams_automatica(instance)
        except Exception as e:
            logger.error(f"[SIGNAL] Error eliminando Teams cancelado: {str(e)}")


# OPCIONAL: Actualizar Teams si cambia fecha/hora
@receiver(pre_save, sender=Cita)
def detectar_cambio_fecha(sender, instance, **kwargs):
    """
    Detecta si cambió la fecha/hora para actualizar Teams
    """
    if instance.pk:  # Solo si ya existe
        try:
            cita_anterior = Cita.objects.get(pk=instance.pk)
            
            # Verificar si cambió fecha u hora
            fecha_cambio = cita_anterior.fecha != instance.fecha
            hora_cambio = cita_anterior.hora_inicio != instance.hora_inicio
            
            if (fecha_cambio or hora_cambio) and instance.tiene_enlace_teams():
                # Marcar para actualizar después del save
                instance._actualizar_teams = True
                logger.info(f"[SIGNAL] Detectado cambio de fecha/hora en cita #{instance.id}")
                
        except Cita.DoesNotExist:
            pass


@receiver(post_save, sender=Cita)
def actualizar_teams_si_cambio_fecha(sender, instance, **kwargs):
    """
    Actualiza Teams si se detectó cambio de fecha/hora
    """
    if hasattr(instance, '_actualizar_teams') and instance._actualizar_teams:
        logger.info(f"[SIGNAL] Actualizando Teams por cambio de fecha en cita #{instance.id}")
        
        try:
            actualizar_reunion_teams_automatica(instance)
            delattr(instance, '_actualizar_teams')
        except Exception as e:
            logger.error(f"[SIGNAL] Error actualizando Teams: {str(e)}")