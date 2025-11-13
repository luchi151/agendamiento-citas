# 📐 ARQUITECTURA Y DECISIONES TÉCNICAS

## Sistema de Agendamiento de Citas - Django

---

## 🏗️ Arquitectura del Sistema

### Patrón de Diseño: MVT (Model-View-Template)

```
┌─────────────────────────────────────────────┐
│           NAVEGADOR / CLIENTE               │
└─────────────────┬───────────────────────────┘
                  │ HTTP Request
                  ▼
┌─────────────────────────────────────────────┐
│              DJANGO URLs                    │
│         (Enrutamiento)                      │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│              VIEWS                          │
│    (Lógica de Negocio)                     │
└───────┬─────────────────────────┬───────────┘
        │                         │
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│   MODELS     │          │  TEMPLATES   │
│ (Base Datos) │          │    (HTML)    │
└──────────────┘          └──────────────┘
```

---

## 🗄️ Modelo de Datos

### Diagrama de Entidades

```
┌─────────────────┐
│    Usuario      │
│  (AbstractUser) │
├─────────────────┤
│ + tipo_usuario  │
│ + telefono      │
└────────┬────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────┐        1:1        ┌──────────────────┐
│      Cita       │◄──────────────────►│   Interacción    │
├─────────────────┤                    ├──────────────────┤
│ + fecha         │                    │ + id_interaccion │
│ + hora_inicio   │                    │ + resultado      │
│ + hora_fin      │                    │ + observaciones  │
│ + estado        │                    │ + asesor_id      │
│ + motivo        │                    └──────────────────┘
│ + url_teams     │
└─────────────────┘

┌──────────────────────────┐
│  DisponibilidadHoraria   │
├──────────────────────────┤
│ + fecha                  │
│ + hora_inicio            │
│ + hora_fin               │
│ + disponible             │
│ + motivo                 │
└──────────────────────────┘
```

---

## 🔐 Sistema de Autenticación y Autorización

### Modelo de Usuario Personalizado

**Decisión:** Extender `AbstractUser` en lugar de crear desde cero
- ✅ Mantiene funcionalidad de Django
- ✅ Fácil integración con el admin
- ✅ Campos personalizados: `tipo_usuario`, `telefono`

### Roles Implementados

```python
ROLES = {
    'cliente': {
        'permisos': [
            'agendar_cita',
            'ver_mis_citas',
            'cancelar_mi_cita',
            'editar_perfil'
        ]
    },
    'asesor': {
        'permisos': [
            'ver_todas_citas',
            'atender_cita',
            'registrar_interaccion',
            'ver_panel_asesor'
        ]
    }
}
```

---

## ⚡ Validaciones del Sistema

### 1. Validaciones de Horario

**Implementadas en:** `Cita.clean()` y `CitaForm`

```python
HORARIOS_PERMITIDOS = {
    'Martes':    [(7:00, 12:40), (14:20, 16:20)],
    'Miércoles': [(7:00, 12:40), (14:20, 16:20)],
    'Jueves':    [(14:00, 16:20)]
}
```

### 2. Validaciones de Negocio

- ✅ Solo días permitidos (Martes, Miércoles, Jueves)
- ✅ Solo horarios dentro de rangos permitidos
- ✅ Antelación mínima: 1 hora para agendar
- ✅ Antelación mínima: 2 horas para cancelar
- ✅ 1 cita activa por usuario máximo
- ✅ No duplicar citas en el mismo horario
- ✅ Duración fija: 20 minutos

### 3. Estados de Cita

```python
ESTADOS = {
    'agendada':   'Cita confirmada, pendiente',
    'cancelada':  'Cancelada por usuario/sistema',
    'completada': 'Interacción efectiva',
    'no_asistio': 'Usuario no se presentó'
}
```

---

## 📧 Sistema de Notificaciones

### Arquitectura de Emails

**Tecnología:** Celery + Redis (asíncrono)

```
Usuario Acción → Vista → Task Celery → Worker → SMTP → Email
```

### Tareas Programadas

```python
TAREAS_CELERY = [
    'enviar_confirmacion_cita',      # Inmediato
    'enviar_cancelacion_cita',       # Inmediato
    'enviar_recordatorio_cita',      # 1 hora antes (Celery Beat)
]
```

### Configuración SMTP (Microsoft)

```python
EMAIL_CONFIG = {
    'HOST': 'smtp.office365.com',
    'PORT': 587,
    'USE_TLS': True,
    'BACKEND': 'smtp'  # console en dev
}
```

---

## 🎨 Frontend

### Stack Tecnológico

- **Framework CSS:** Bootstrap 5.3
- **Iconos:** Bootstrap Icons
- **JavaScript:** Vanilla JS (opcional: HTMX futuro)

### Decisiones de Diseño

1. **Responsive First:** Mobile-friendly por defecto
2. **Accesibilidad:** Etiquetas semánticas, ARIA labels
3. **UX:** Mensajes claros, confirmaciones visuales
4. **Colores:** Sistema de estados con badges

```css
COLORES_ESTADO = {
    agendada:   '#28a745',  /* Verde */
    cancelada:  '#dc3545',  /* Rojo */
    completada: '#007bff',  /* Azul */
    no_asistio: '#ffc107',  /* Amarillo */
}
```

---

## 🔄 Flujo de Datos Principales

### 1. Agendamiento de Cita

```
Usuario → Formulario → Validación Cliente → 
Vista → Validación Servidor → Modelo → 
Base de Datos → Task Email → Confirmación
```

### 2. Cancelación de Cita

```
Usuario → Confirmar → Validar Antelación → 
Actualizar Estado → Liberar Horario → 
Task Email → Notificación
```

### 3. Atención de Cita (Asesor)

```
Asesor → Ver Cita → Atender → 
Formulario Interacción → Generar ID → 
Actualizar Estado Cita → Guardar
```

---

## 🚀 Configuraciones de Desempeño

### Base de Datos

**Índices Creados:**
```python
INDICES = [
    ('fecha', 'hora_inicio'),  # Búsquedas de disponibilidad
    ('usuario', 'estado'),     # Consultas por usuario
]
```

### Optimizaciones de Queries

```python
# Select Related / Prefetch Related
Cita.objects.select_related('usuario')
Cita.objects.prefetch_related('interaccion')
```

### Paginación

```python
REST_FRAMEWORK = {
    'PAGE_SIZE': 10,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
}
```

---

## 🛡️ Seguridad Implementada

### 1. Protección CSRF
- ✅ Tokens CSRF en todos los formularios
- ✅ Middleware activo

### 2. Autenticación
- ✅ Login requerido en vistas sensibles
- ✅ Decorador `@login_required`
- ✅ Verificación de roles

### 3. Validación de Datos
- ✅ Validación en Forms
- ✅ Validación en Models
- ✅ Sanitización de inputs

### 4. Configuración Segura
```python
SEGURIDAD = {
    'DEBUG': False,  # En producción
    'SECRET_KEY': 'usar variable entorno',
    'ALLOWED_HOSTS': ['dominio.com'],
    'SECURE_SSL_REDIRECT': True,
    'SESSION_COOKIE_SECURE': True,
}
```

---

## 📊 Escalabilidad

### Consideraciones Futuras

1. **Base de Datos:**
   - Migrar a PostgreSQL
   - Implementar réplicas de lectura
   - Particionamiento por fecha

2. **Caché:**
   - Redis para sesiones
   - Memcached para queries frecuentes
   - Cache de templates

3. **Archivos Estáticos:**
   - CDN para static files
   - S3/Azure Storage para media

4. **Servidores:**
   - Load balancer
   - Múltiples workers Gunicorn
   - Nginx reverse proxy

---

## 🧪 Testing (Futuro)

### Estrategia de Pruebas

```python
TESTING_STRATEGY = {
    'Unit Tests': [
        'test_models.py',
        'test_forms.py',
        'test_validators.py'
    ],
    'Integration Tests': [
        'test_views.py',
        'test_workflows.py'
    ],
    'E2E Tests': [
        'test_selenium.py',
        'test_user_flows.py'
    ]
}
```

---

## 🔧 Herramientas de Desarrollo

### Debug Tools (Opcional)
```python
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
```

### Logging
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
}
```

---

## 📈 Métricas y Monitoring (Futuro)

- Sentry: Error tracking
- New Relic: Performance monitoring
- Google Analytics: User behavior
- Custom dashboard: Business metrics

---

## 🔄 Versionamiento

**Estrategia Git Flow:**
- `main`: Producción
- `develop`: Desarrollo
- `feature/*`: Nuevas características
- `hotfix/*`: Correcciones urgentes

---

## 📝 Decisiones Técnicas Clave

### ¿Por qué Django?
- ✅ Admin panel out-of-the-box
- ✅ ORM robusto
- ✅ Sistema de autenticación completo
- ✅ Gran ecosistema de paquetes
- ✅ Rápido desarrollo

### ¿Por qué SQLite en desarrollo?
- ✅ Sin configuración adicional
- ✅ Fácil de resetear
- ✅ Suficiente para desarrollo
- ⚠️ Cambiar a PostgreSQL en producción

### ¿Por qué Celery?
- ✅ Emails asíncronos
- ✅ Recordatorios programados
- ✅ No bloquea requests
- ✅ Escalable

### ¿Por qué Bootstrap?
- ✅ Responsive por defecto
- ✅ Componentes listos
- ✅ Documentación extensa
- ✅ Comunidad grande

---

## 🎯 Próximos Pasos Técnicos

1. **Implementar API REST** (Django REST Framework)
2. **Agregar WebSockets** (Django Channels)
3. **Sistema de notificaciones push**
4. **Integración con Microsoft Graph** (Teams automático)
5. **Dashboard con gráficos** (Chart.js)
6. **Exportación de reportes** (WeasyPrint/ReportLab)
7. **Multi-tenancy** (si se requiere)
8. **OAuth2** (Login social)

---

Este documento sirve como referencia técnica para desarrolladores que trabajen en el proyecto.
