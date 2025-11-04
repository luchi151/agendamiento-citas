from django.urls import path
from . import views

app_name = 'citas'

urlpatterns = [
    path('', views.lista_citas_view, name='lista_citas'),
    path('mis-citas/', views.mis_citas_view, name='mis_citas'),
    path('agendar/', views.agendar_cita_view, name='agendar_cita'),
    path('cancelar/<int:cita_id>/', views.cancelar_cita_view, name='cancelar_cita'),
    path('disponibilidad/', views.horarios_disponibles_view, name='horarios_disponibles'),
    
    # Panel de asesor
    path('panel-asesor/', views.panel_asesor_view, name='panel_asesor'),
    path('atender/<int:cita_id>/', views.atender_cita_view, name='atender_cita'),
]
