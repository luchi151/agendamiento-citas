@echo off
echo ========================================
echo Sistema de Agendamiento de Citas
echo ========================================
echo.

REM Verificar si existe el entorno virtual
if not exist "venv\" (
    echo Creando entorno virtual...
    python -m venv venv
    echo.
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat
echo.

REM Instalar dependencias si es necesario
if not exist "venv\Lib\site-packages\django\" (
    echo Instalando dependencias...
    pip install -r requirements.txt
    echo.
)

REM Verificar si existe la base de datos
if not exist "db.sqlite3" (
    echo Base de datos no encontrada. Creando...
    python manage.py migrate
    python crear_datos_prueba.py
    echo.
)

echo ========================================
echo Iniciando servidor...
echo ========================================
echo.
echo Accede a: http://localhost:8000
echo Admin: http://localhost:8000/admin
echo.
echo Usuario: admin
echo Password: admin123
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

python manage.py runserver

pause
