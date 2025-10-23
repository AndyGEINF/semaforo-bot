#!/bin/bash
# Script de inicio para API Long/Short con Playwright

echo "============================================================"
echo "🚀 START_LONGSHORT.SH - $(date +%H:%M:%S)"
echo "============================================================"

# Variables de entorno para Playwright
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/.playwright
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0
export PLAYWRIGHT_CHROMIUM_ARGS="--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage --disable-gpu --disable-software-rasterizer --disable-extensions"

echo "📍 PLAYWRIGHT_BROWSERS_PATH=$PLAYWRIGHT_BROWSERS_PATH"
echo "📍 PORT=${PORT:-8001}"
echo "📍 PWD=$(pwd)"

# Verificar instalación de Chromium (buildCommand ya lo instaló)
echo "🔍 Verificando instalación de Chromium desde buildCommand..."
CHROMIUM_EXEC=$(find "$PLAYWRIGHT_BROWSERS_PATH" -name "headless_shell" -type f 2>/dev/null | head -1)

if [ -n "$CHROMIUM_EXEC" ]; then
    echo "✅ Chromium encontrado: $CHROMIUM_EXEC"
    ls -lh "$CHROMIUM_EXEC"
else
    echo "⚠️ Chromium NO encontrado en $PLAYWRIGHT_BROWSERS_PATH"
    echo "   Listando contenido del directorio:"
    ls -la "$PLAYWRIGHT_BROWSERS_PATH" 2>/dev/null || echo "   (directorio no existe)"
    echo ""
    echo "� Intentando instalación de emergencia..."
    python -m playwright install chromium --no-shell
    
    CHROMIUM_EXEC=$(find "$PLAYWRIGHT_BROWSERS_PATH" -name "headless_shell" -type f 2>/dev/null | head -1)
    if [ -n "$CHROMIUM_EXEC" ]; then
        echo "✅ Chromium instalado correctamente en: $CHROMIUM_EXEC"
    else
        echo "❌ ERROR: No se pudo instalar Chromium"
        echo "   El scraping fallará, pero el servidor iniciará de todos modos"
    fi
fi

# Iniciar uvicorn
echo "============================================================"
echo "🚀 Iniciando servidor SSE en puerto ${PORT:-8001}..."
echo "============================================================"
exec uvicorn api_longshort_ondemand:app --host 0.0.0.0 --port ${PORT:-8001} --log-level info

