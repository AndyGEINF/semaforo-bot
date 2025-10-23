#!/bin/bash
# Script de inicio para Render con Playwright

echo "🚀 [$(date +%H:%M:%S)] START_MAIN.SH - Iniciando..."

# Variables de entorno para Playwright en headless sin dependencias
export PLAYWRIGHT_BROWSERS_PATH=/tmp/playwright
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0

# Flags para Chromium sin dependencias del sistema
export PLAYWRIGHT_CHROMIUM_ARGS="--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage --disable-gpu --disable-software-rasterizer --disable-extensions"

echo "✅ [$(date +%H:%M:%S)] Variables de entorno configuradas"
echo "📍 PORT=${PORT:-8000}"
echo "🐍 Python: $(python --version)"
echo "📦 PWD: $(pwd)"

# Verificar que main.py existe
if [ -f "main.py" ]; then
    echo "✅ [$(date +%H:%M:%S)] main.py encontrado"
else
    echo "❌ [$(date +%H:%M:%S)] main.py NO ENCONTRADO"
    ls -la
    exit 1
fi

# Verificar que config.json existe
if [ -f "config.json" ]; then
    echo "✅ [$(date +%H:%M:%S)] config.json encontrado"
else
    echo "⚠️ [$(date +%H:%M:%S)] config.json NO ENCONTRADO (puede causar error)"
fi

echo "🔥 [$(date +%H:%M:%S)] Iniciando uvicorn..."
# Iniciar uvicorn con logging
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
