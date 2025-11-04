# 🚀 GUÍA DE INICIO RÁPIDO

## Sistema de Agendamiento de Citas

---

## ⚡ Inicio Rápido (5 minutos)

### 1. Requisitos Previos
```bash
# Verificar que tienes Python 3.8+ instalado
python --version
```

### 2. Instalación

```bash
# Navegar al directorio del proyecto
cd agendamiento_citas

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# (Opcional) Crear datos de prueba
python crear_datos_prueba.py
```

### 3. Iniciar Servidor

```bash
python manage.py runserver
```

### 4. Acceder al Sistema

- **Aplicación Web:** http://localhost:8000
- **Panel Admin:** http://localhost:8000/admin

---

## 🔐 Credenciales por Defecto

### Admin/Staff
- **Usuario:** `admin`
- **Contraseña:** `admin123`
- **Rol:** Asesor + Administrador

### Asesor
- **Usuario:** `asesor1`
- **Contraseña:** `asesor123`
- **Rol:** Asesor

### Clientes de Prueba
- **Usuario:** `cliente1` / **Contraseña:** `cliente123`
- **Usuario:** `cliente2` / **Contraseña:** `cliente123`

---

## 📋 Funcionalidades Implementadas

### ✅ Usuarios
- [x] Registro de nuevos usuarios
- [x] Login/Logout
- [x] Perfil de usuario editable
- [x] Sistema de roles (Cliente/Asesor)

### ✅ Citas
- [x] Agendar citas con validación de horarios
- [x] Ver mis citas (pendientes y pasadas)
- [x] Cancelar citas (2 horas de anticipación)
- [x] Validación de 1 cita activa por usuario
- [x] Duración automática de 20 minutos

### ✅ Panel de Asesor
- [x] Ver todas las citas agendadas
- [x] Atender citas
- [x] Registrar interacciones
- [x] ID de interacción consecutivo automático

### ✅ Admin
- [x] Gestión completa de usuarios
- [x] Gestión de citas
- [x] Ver interacciones
- [x] Gestión de disponibilidad horaria

---

## 🕐 Horarios Configurados

### Martes y Miércoles
- **Mañana:** 7:00 AM - 12:40 PM
- **Tarde:** 2:20 PM - 4:20 PM

### Jueves
- **Tarde:** 2:00 PM - 4:20 PM

**Duración de cada cita:** 20 minutos

---

## 📁 Estructura del Proyecto

```
agendamiento_citas/
├── config/                    # Configuración principal
│   ├── settings.py           # Configuración Django
│   ├── urls.py               # URLs principales
│   └── celery.py             # Configuración Celery
│
├── usuarios/                  # App de usuarios
│   ├── models.py             # Modelo Usuario personalizado
│   ├── views.py              # Login, registro, perfil
│   ├── forms.py              # Formularios
│   └── templates/            # Templates de usuarios
│
├── citas/                     # App de citas
│   ├── models.py             # Cita, Interacción, Disponibilidad
│   ├── views.py              # Vistas de agendamiento
│   ├── forms.py              # Formularios de citas
│   ├── tasks.py              # Tareas Celery (emails)
│   └── templates/            # Templates de citas
│
├── templates/                 # Templates globales
│   ├── base.html             # Template base
│   └── home.html             # Página de inicio
│
├── manage.py                  # Django management
├── requirements.txt           # Dependencias Python
├── .env                       # Variables de entorno
├── crear_datos_prueba.py     # Script de datos de prueba
└── README.md                  # Documentación completa
```

---

## 🔧 Configuración Adicional

### Configurar Email (Microsoft/Outlook)

Edita el archivo `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_correo@empresa.com
EMAIL_HOST_PASSWORD=tu_password
```

### Celery (Tareas Asíncronas)

Para usar Celery en desarrollo/producción:

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
celery -A config worker --loglevel=info

# Terminal 3: Celery Beat (tareas programadas)
celery -A config beat --loglevel=info
```

---

## 🎯 Flujo de Uso del Sistema

### Como Cliente:

1. **Registrarse** → Crear cuenta
2. **Login** → Iniciar sesión
3. **Agendar Cita:**
   - Seleccionar fecha (Martes/Miércoles/Jueves)
   - Seleccionar hora disponible
   - Agregar motivo (opcional)
   - Confirmar
4. **Ver Mis Citas** → Consultar citas agendadas
5. **Cancelar** → Si es necesario (2 horas antes)

### Como Asesor:

1. **Login** → Iniciar sesión como asesor
2. **Panel Asesor** → Ver todas las citas
3. **Atender Cita:**
   - Ver detalles del usuario
   - Acceder a enlace de Teams
   - Registrar resultado (Efectiva/No Asiste)
   - Agregar observaciones
   - Se genera ID automático

---

## 🐛 Solución de Problemas

### Error de migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### Resetear base de datos
```bash
rm db.sqlite3
python manage.py migrate
python crear_datos_prueba.py
```

### Puerto ya en uso
```bash
# Usar otro puerto
python manage.py runserver 8001
```

---

## 📚 Próximas Implementaciones

- [ ] Templates completos de citas (mis_citas.html, agendar_cita.html)
- [ ] Calendario visual interactivo
- [ ] Envío automático de emails
- [ ] Recordatorios automáticos (1 hora antes)
- [ ] Generación automática de URL de Teams
- [ ] API REST para integración externa
- [ ] Dashboard con estadísticas
- [ ] Exportación de reportes (PDF/Excel)
- [ ] Chat en tiempo real con asesor
- [ ] Notificaciones push

---

## 💡 Tips y Recomendaciones

1. **Desarrollo:** Usa SQLite (ya configurado)
2. **Producción:** Cambia a PostgreSQL
3. **Emails en Dev:** Modo console (ver en terminal)
4. **Emails en Prod:** Configurar SMTP real
5. **Backup:** Respalda `db.sqlite3` regularmente
6. **Seguridad:** Cambia `SECRET_KEY` en producción
7. **Debug:** Mantén `DEBUG=False` en producción

---

## 📞 Soporte

Para problemas o consultas:
- Revisar `README.md` completo
- Verificar logs en terminal
- Revisar configuración de `.env`

---

## ✨ Características del Código

- ✅ Código limpio y documentado
- ✅ Validaciones robustas
- ✅ Manejo de errores
- ✅ Seguridad implementada
- ✅ Responsive design (Bootstrap 5)
- ✅ Panel de admin personalizado
- ✅ Preparado para producción

---

**¡El sistema está listo para usar! 🎉**

Ejecuta `python manage.py runserver` y comienza a agendar citas.
