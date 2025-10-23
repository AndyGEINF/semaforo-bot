#!/bin/bash
# Script de inicio para API Long/Short con Playwright

# Variables de entorno para Playwright en headless sin dependencias
export PLAYWRIGHT_BROWSERS_PATH=/tmp/playwright
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0

# Flags para Chromium sin dependencias del sistema
export PLAYWRIGHT_CHROMIUM_ARGS="--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage --disable-gpu --disable-software-rasterizer --disable-extensions"

# Verificar que Chromium esté instalado (el buildCommand ya lo instaló)
echo "🔍 Verificando instalación de Chromium..."
if ! python -c "from playwright.sync_api import sync_playwright; sync_playwright().start()" 2>/dev/null; then
    echo "⚠️ Playwright no inicializado correctamente, instalando Chromium..."
    python -m playwright install chromium --no-shell
fi
echo "✅ Chromium listo"

# Iniciar uvicorn
echo "🚀 Iniciando servidor SSE en puerto ${PORT:-8001}..."
exec uvicorn api_longshort_ondemand:app --host 0.0.0.0 --port ${PORT:-8001}

