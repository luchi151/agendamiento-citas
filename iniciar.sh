#!/bin/bash

echo "========================================"
echo "Sistema de Agendamiento de Citas"
echo "========================================"
echo ""

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
    echo ""
fi

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate
echo ""

# Instalar dependencias si es necesario
if [ ! -d "venv/lib/python3*/site-packages/django" ]; then
    echo "Instalando dependencias..."
    pip install -r requirements.txt
    echo ""
fi

# Verificar si existe la base de datos
if [ ! -f "db.sqlite3" ]; then
    echo "Base de datos no encontrada. Creando..."
    python manage.py migrate
    python crear_datos_prueba.py
    echo ""
fi

echo "========================================"
echo "Iniciando servidor..."
echo "========================================"
echo ""
echo "Accede a: http://localhost:8000"
echo "Admin: http://localhost:8000/admin"
echo ""
echo "Usuario: admin"
echo "Password: admin123"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo "========================================"
echo ""

python manage.py runserver
