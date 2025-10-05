#!/bin/bash

echo "=========================================="
echo "  Configuración de Courier Quest"
echo "=========================================="
echo ""

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p saves
mkdir -p api_cache
mkdir -p data

# Crear archivo .gitkeep si no existe
touch data/.gitkeep

# Copiar archivos de ejemplo si no existen
if [ ! -f "data/puntajes.json" ]; then
    echo '[]' > data/puntajes.json
    echo "✅ puntajes.json creado"
fi

# Instalar dependencias
echo ""
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Verificar instalación
echo ""
echo "🔍 Verificando instalación..."
python -c "import pygame; import requests; print('✅ Todas las dependencias instaladas correctamente')"

# Ejecutar tests
echo ""
echo "🧪 Ejecutando tests..."
pytest tests/ -v

echo ""
echo "=========================================="
echo "  ✅ Configuración completada"
echo "=========================================="
echo ""
echo "Para ejecutar el juego:"
echo "  python -m src.main"
echo ""