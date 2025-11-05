from django.urls import path
from . import views

app_name = 'citas'

urlpatterns = [
    # Rutas para usuarios (sin autenticación)
    path('agendar/', views.agendar_cita_publica_view, name='agendar_cita'),
    path('consultar/', views.consultar_cita_view, name='consultar_cita'),
    path('cancelar/', views.buscar_cita_cancelar_view, name='cancelar_cita_buscar'),
    path('cancelar/<int:cita_id>/', views.confirmar_cancelar_cita_view, name='cancelar_cita'),
    
    # Rutas para asesores (con autenticación)
    path('mis-citas/', views.mis_citas_view, name='mis_citas'),
    path('disponibilidad/', views.horarios_disponibles_view, name='horarios_disponibles'),
    path('panel-asesor/', views.panel_asesor_view, name='panel_asesor'),
    path('atender/<int:cita_id>/', views.atender_cita_view, name='atender_cita'),
]

