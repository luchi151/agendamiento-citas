import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import time
import urllib3

import msal
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Deshabilitar warnings de SSL (solo si DISABLE_SSL_VERIFY está activado)
if getattr(settings, 'DISABLE_SSL_VERIFY', False):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    logger.warning("[WARN] SSL verification DESHABILITADA - Solo usar en desarrollo")


class MicrosoftTeamsService:
    """
    Servicio para gestión automática de reuniones de Microsoft Teams
    """
    
    def __init__(self):
        self.tenant_id = settings.MICROSOFT_TENANT_ID
        self.client_id = settings.MICROSOFT_CLIENT_ID
        self.client_secret = settings.MICROSOFT_CLIENT_SECRET
        self.user_id = settings.MICROSOFT_TEAMS_USER_ID
        self.authority = settings.MICROSOFT_GRAPH_AUTHORITY
        self.scopes = settings.MICROSOFT_GRAPH_SCOPES
        self.endpoint = settings.MICROSOFT_GRAPH_API_ENDPOINT
        self.timezone = settings.TEAMS_TIMEZONE
        
        # SSL verification (False solo en desarrollo)
        self.verify_ssl = not getattr(settings, 'DISABLE_SSL_VERIFY', False)
        
        self._access_token = None
        self._token_expiry = None
        
        logger.info("[TEAMS] MicrosoftTeamsService inicializado")
        if not self.verify_ssl:
            logger.warning("[WARN] SSL verification deshabilitada")
    
    def _get_access_token(self) -> Optional[str]:
        """Obtiene access token de Azure AD"""
        if self._access_token and self._token_expiry:
            if datetime.now() < self._token_expiry - timedelta(minutes=5):
                return self._access_token
        
        try:
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret,
            )
            
            result = app.acquire_token_for_client(scopes=self.scopes)
            
            if "access_token" in result:
                self._access_token = result['access_token']
                self._token_expiry = datetime.now() + timedelta(seconds=result.get('expires_in', 3600))
                logger.info("[OK] Access token obtenido exitosamente")
                return self._access_token
            else:
                error = result.get("error")
                error_description = result.get("error_description")
                logger.error(f"[ERROR] Error obteniendo token: {error} - {error_description}")
                return None
                
        except Exception as e:
            logger.error(f"[ERROR] Excepción obteniendo token: {str(e)}")
            return None
    
    def crear_reunion_teams(
        self,
        asunto: str,
        fecha_inicio: datetime,
        duracion_minutos: int,
        descripcion: str = "",
        asistentes: list = None
    ) -> Optional[Dict[str, Any]]:
        """Crea una reunión de Teams automáticamente"""
        logger.info(f"[TEAMS] Creando reunión: {asunto}")
        
        for intento in range(settings.TEAMS_MAX_RETRIES):
            try:
                token = self._get_access_token()
                if not token:
                    logger.error("[ERROR] No se pudo obtener access token")
                    if intento < settings.TEAMS_MAX_RETRIES - 1:
                        time.sleep(settings.TEAMS_RETRY_DELAY)
                        continue
                    return None
                
                fecha_fin = fecha_inicio + timedelta(minutes=duracion_minutos)
                
                evento = {
                    "subject": asunto,
                    "start": {
                        "dateTime": fecha_inicio.isoformat(),
                        "timeZone": self.timezone
                    },
                    "end": {
                        "dateTime": fecha_fin.isoformat(),
                        "timeZone": self.timezone
                    },
                    "isOnlineMeeting": True,
                    "onlineMeetingProvider": "teamsForBusiness"
                }
                
                if descripcion:
                    evento["body"] = {
                        "contentType": "HTML",
                        "content": descripcion
                    }
                
                if asistentes:
                    evento["attendees"] = [
                        {
                            "emailAddress": {"address": email},
                            "type": "required"
                        }
                        for email in asistentes
                    ]
                
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json',
                    'Prefer': 'outlook.timezone="' + self.timezone + '"'
                }
                
                url = f"{self.endpoint}/users/{self.user_id}/calendar/events"
                
                response = requests.post(
                    url,
                    headers=headers,
                    json=evento,
                    timeout=settings.MICROSOFT_GRAPH_TIMEOUT,
                    verify=self.verify_ssl  # ← SSL verification configurable
                )
                
                if response.status_code == 201:
                    data = response.json()
                    reunion_info = {
                        'id': data.get('id'),
                        'join_url': data.get('onlineMeeting', {}).get('joinUrl'),
                        'conference_id': data.get('onlineMeeting', {}).get('conferenceId'),
                        'subject': data.get('subject'),
                        'start': data.get('start', {}).get('dateTime'),
                        'end': data.get('end', {}).get('dateTime'),
                    }
                    
                    logger.info(f"[OK] Reunión creada: {reunion_info['id']}")
                    return reunion_info
                else:
                    logger.error(f"[ERROR] HTTP {response.status_code}: {response.text}")
                    if intento < settings.TEAMS_MAX_RETRIES - 1:
                        time.sleep(settings.TEAMS_RETRY_DELAY)
                        continue
                    return None
                    
            except requests.exceptions.SSLError as e:
                logger.error(f"[ERROR] Error SSL: {str(e)}")
                logger.error("[ERROR] Configurar certificado corporativo o DISABLE_SSL_VERIFY=True")
                return None
            except requests.exceptions.Timeout:
                logger.error(f"[ERROR] Timeout (intento {intento + 1}/{settings.TEAMS_MAX_RETRIES})")
                if intento < settings.TEAMS_MAX_RETRIES - 1:
                    time.sleep(settings.TEAMS_RETRY_DELAY)
                    continue
                return None
            except Exception as e:
                logger.error(f"[ERROR] Excepción: {str(e)}")
                if intento < settings.TEAMS_MAX_RETRIES - 1:
                    time.sleep(settings.TEAMS_RETRY_DELAY)
                    continue
                return None
        
        return None
    
    def eliminar_reunion_teams(self, event_id: str) -> bool:
        """Elimina una reunión de Teams"""
        logger.info(f"[TEAMS] Eliminando reunión: {event_id}")
        
        token = self._get_access_token()
        if not token:
            return False
        
        headers = {'Authorization': f'Bearer {token}'}
        url = f"{self.endpoint}/users/{self.user_id}/calendar/events/{event_id}"
        
        try:
            response = requests.delete(
                url,
                headers=headers,
                timeout=settings.MICROSOFT_GRAPH_TIMEOUT,
                verify=self.verify_ssl  # ← SSL verification configurable
            )
            
            if response.status_code == 204:
                logger.info(f"[OK] Reunión eliminada: {event_id}")
                return True
            else:
                logger.error(f"[ERROR] Error eliminando: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Excepción eliminando: {str(e)}")
            return False
    
    def actualizar_reunion_teams(
        self,
        event_id: str,
        asunto: Optional[str] = None,
        fecha_inicio: Optional[datetime] = None,
        duracion_minutos: Optional[int] = None
    ) -> bool:
        """Actualiza una reunión existente"""
        logger.info(f"[TEAMS] Actualizando reunión: {event_id}")
        
        token = self._get_access_token()
        if not token:
            return False
        
        cambios = {}
        
        if asunto:
            cambios["subject"] = asunto
        
        if fecha_inicio and duracion_minutos:
            fecha_fin = fecha_inicio + timedelta(minutes=duracion_minutos)
            cambios["start"] = {
                "dateTime": fecha_inicio.isoformat(),
                "timeZone": self.timezone
            }
            cambios["end"] = {
                "dateTime": fecha_fin.isoformat(),
                "timeZone": self.timezone
            }
        
        if not cambios:
            logger.warning("[WARN] No hay cambios para actualizar")
            return False
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.endpoint}/users/{self.user_id}/calendar/events/{event_id}"
        
        try:
            response = requests.patch(
                url,
                headers=headers,
                json=cambios,
                timeout=settings.MICROSOFT_GRAPH_TIMEOUT,
                verify=self.verify_ssl  # ← SSL verification configurable
            )
            
            if response.status_code == 200:
                logger.info(f"[OK] Reunión actualizada: {event_id}")
                return True
            else:
                logger.error(f"[ERROR] Error actualizando: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Excepción actualizando: {str(e)}")
            return False
    
    def verificar_conexion(self) -> bool:
        """Verifica conectividad con Graph API"""
        logger.info("[TEAMS] Verificando conexión con Microsoft Graph API")
        
        token = self._get_access_token()
        if not token:
            logger.error("[ERROR] No se pudo obtener token")
            return False
        
        headers = {'Authorization': f'Bearer {token}'}
        url = f"{self.endpoint}/users/{self.user_id}"
        
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=settings.MICROSOFT_GRAPH_TIMEOUT,
                verify=self.verify_ssl  # ← SSL verification configurable
            )
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"[OK] Conexión exitosa - Usuario: {user_data.get('displayName')}")
                return True
            else:
                logger.error(f"[ERROR] Error de conexión: {response.status_code}")
                return False
                
        except requests.exceptions.SSLError as e:
            logger.error(f"[ERROR] Error SSL: {str(e)}")
            logger.error("[ERROR] Solución: Configurar certificado corporativo o DISABLE_SSL_VERIFY=True en settings.py")
            return False
        except Exception as e:
            logger.error(f"[ERROR] Excepción verificando: {str(e)}")
            return False


# Instancia singleton
teams_service = MicrosoftTeamsService()