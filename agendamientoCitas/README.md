# Sistema de Agendamiento de Citas

Sistema web desarrollado en Django para gestionar citas con horarios específicos, notificaciones por correo y panel de administración para asesores.

## Características Principales

- ✅ Registro y autenticación de usuarios
- ✅ Agendamiento de citas con validación de horarios
- ✅ Sistema de roles (Cliente y Asesor)
- ✅ Restricción de 1 cita activa por usuario
- ✅ Cancelación de citas con 2 horas de antelación
- ✅ Panel de administración para asesores
- ✅ Registro de interacciones con ID consecutivo
- ✅ Integración con Microsoft Teams (URL)
- 📧 Notificaciones por correo electrónico (por configurar)

## Horarios de Atención

- **Martes y Miércoles:**
  - Mañana: 7:00 AM - 12:40 PM
  - Tarde: 2:20 PM - 4:20 PM

- **Jueves:**
  - Tarde: 2:00 PM - 4:20 PM

- **Duración de cada cita:** 20 minutos

## Requisitos Previos

- Python 3.8+
- pip
- Redis (para Celery - opcional en desarrollo)

## Instalación

### 1. Clonar el repositorio o descomprimir

```bash
cd agendamiento_citas
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install django djangorestframework python-decouple celery redis django-celery-beat pillow
```

### 4. Configurar variables de entorno

Edita el archivo `.env` con tus configuraciones:

```env
SECRET_KEY=tu-secret-key-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (Microsoft/Outlook)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_correo@outlook.com
EMAIL_HOST_PASSWORD=tu_password

TIME_ZONE=America/Bogota
```

### 5. Aplicar migraciones

```bash
python manage.py migrate
```

### 6. Crear superusuario (ya existe admin/admin123)

Si necesitas crear otro usuario administrador:

```bash
python manage.py createsuperuser
```

**Usuario por defecto:**
- Username: `admin`
- Password: `admin123`
- Tipo: Asesor

## Ejecución del Proyecto

### Servidor de desarrollo

```bash
python manage.py runserver
```

Accede a:
- **Aplicación:** http://localhost:8000
- **Admin:** http://localhost:8000/admin

## Estructura del Proyecto

```
agendamiento_citas/
├── config/                 # Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── usuarios/              # App de gestión de usuarios
│   ├── models.py         # Modelo Usuario personalizado
│   ├── views.py          # Vistas de autenticación
│   ├── forms.py          # Formularios de registro
│   └── templates/
├── citas/                # App de gestión de citas
│   ├── models.py         # Modelos: Cita, Interacción, Disponibilidad
│   ├── views.py          # Vistas de citas y panel asesor
│   ├── forms.py          # Formularios de citas
│   └── templates/
├── templates/            # Templates globales
├── manage.py
├── .env                  # Variables de entorno
└── README.md
```

## Modelos Principales

### Usuario
- Extiende `AbstractUser`
- Campos adicionales: `tipo_usuario`, `telefono`
- Tipos: Cliente o Asesor

### Cita
- Usuario, fecha, hora inicio/fin
- Estados: agendada, cancelada, completada, no_asistio
- Validaciones automáticas de horarios y antelación
- URL de Teams para videollamadas

### Interacción
- Registro de resultado de la cita
- ID consecutivo automático (formato: INT-YYYYMMDD-XXXX)
- Campos: resultado, observaciones
- Relacionada one-to-one con Cita

### DisponibilidadHoraria
- Para bloquear horarios específicos
- Útil para excepciones o días festivos

## Uso del Sistema

### Como Cliente

1. **Registrarse:** Crear cuenta desde /usuarios/registro/
2. **Agendar Cita:** 
   - Solo 1 cita activa permitida
   - Mínimo 1 hora de anticipación
   - Seleccionar horario disponible
3. **Ver Mis Citas:** Consultar citas agendadas y pasadas
4. **Cancelar Cita:** Mínimo 2 horas de anticipación

### Como Asesor

1. **Panel Asesor:** Ver todas las citas agendadas
2. **Atender Cita:** 
   - Ingresar a la videollamada de Teams
   - Registrar resultado (Efectiva/No Asiste)
   - Agregar observaciones (opcional)
   - Se genera ID de interacción automático

### Panel de Administración

Acceso: http://localhost:8000/admin

Funcionalidades:
- Gestionar usuarios y perfiles
- Ver todas las citas
- Gestionar disponibilidad horaria
- Ver interacciones registradas

## Próximas Implementaciones

- [ ] Formularios para crear citas (CitaForm)
- [ ] Templates completos de citas
- [ ] Envío de correos electrónicos con notificaciones
- [ ] Tareas programadas con Celery (recordatorios)
- [ ] API REST para integración externa
- [ ] Generación de URL de Teams automática
- [ ] Dashboard con estadísticas
- [ ] Exportación de reportes

## Celery (Tareas Programadas)

Para usar Celery en producción:

### 1. Iniciar Redis

```bash
redis-server
```

### 2. Iniciar Worker de Celery

```bash
celery -A config worker --loglevel=info
```

### 3. Iniciar Beat (tareas programadas)

```bash
celery -A config beat --loglevel=info
```

## Configuración de Email

Para producción, actualiza en `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.office365.com
EMAIL_HOST_USER=tu_correo_real@empresa.com
EMAIL_HOST_PASSWORD=tu_password_real
```

## Solución de Problemas

### Error de migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### Reiniciar base de datos
```bash
rm db.sqlite3
python manage.py migrate
python set_admin_password.py
```

## Tecnologías Utilizadas

- **Backend:** Django 5.2
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (producción recomendada)
- **Frontend:** Bootstrap 5 + Bootstrap Icons
- **Tareas asíncronas:** Celery + Redis
- **Email:** Microsoft Graph API / SMTP

## Contribuir

Para contribuir al proyecto:
1. Crea una rama con tu feature
2. Realiza tus cambios
3. Envía un pull request

## Licencia

Este proyecto es privado y de uso interno.

## Contacto

Para soporte o consultas sobre el sistema, contacta al equipo de desarrollo.
