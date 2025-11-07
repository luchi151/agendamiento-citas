from django.shortcuts import redirect

class AsesorRedirectMiddleware:
    """
    Middleware que redirige a los asesores al panel de asesor
    cuando intentan acceder al home público
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Rutas públicas que los asesores NO deben ver
        public_paths = [
            '/',  # Home público
        ]
        
        # Si el usuario está autenticado, es asesor, y está en una ruta pública
        if (request.user.is_authenticated and 
            request.user.es_asesor() and 
            request.path in public_paths):
            # Redirigir al panel de asesor
            return redirect('citas:panel_asesor')
        
        response = self.get_response(request)
        return response