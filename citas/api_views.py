from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Solicitante


@require_http_methods(["GET"])
def buscar_solicitante_api(request):
    """
    API endpoint para buscar un solicitante por tipo y número de documento
    Retorna los datos en formato JSON si existe
    """
    tipo_documento = request.GET.get('tipo_documento')
    numero_documento = request.GET.get('numero_documento')
    
    # Validar que se enviaron ambos parámetros
    if not tipo_documento or not numero_documento:
        return JsonResponse({
            'success': False,
            'message': 'Faltan parámetros requeridos'
        }, status=400)
    
    # Buscar el último registro del solicitante
    solicitante = Solicitante.get_ultimo_registro(tipo_documento, numero_documento)
    
    if solicitante:
        # Retornar los datos del solicitante
        return JsonResponse({
            'success': True,
            'encontrado': True,
            'datos': {
                'tipo_documento': solicitante.tipo_documento,
                'numero_documento': solicitante.numero_documento,
                'nombre': solicitante.nombre,
                'apellido': solicitante.apellido,
                'celular': solicitante.celular,
                'correo_electronico': solicitante.correo_electronico,
                'sexo': solicitante.sexo,
                'genero': solicitante.genero,
                'orientacion_sexual': solicitante.orientacion_sexual,
                'rango_edad': solicitante.rango_edad,
                'nivel_educativo': solicitante.nivel_educativo,
                'grupo_etnico': solicitante.grupo_etnico,
                'grupo_poblacional': solicitante.grupo_poblacional,
                'estrato_socioeconomico': solicitante.estrato_socioeconomico,
                'localidad': solicitante.localidad,
                'calidad_comunicacion': solicitante.calidad_comunicacion,
                'tiene_discapacidad': solicitante.tiene_discapacidad,
                'tipo_discapacidad': solicitante.tipo_discapacidad or '',
            },
            'message': 'Encontramos tus datos previos. Puedes actualizarlos si es necesario.'
        })
    else:
        # No se encontró el solicitante
        return JsonResponse({
            'success': True,
            'encontrado': False,
            'message': 'No encontramos registros previos con este documento.'
        })