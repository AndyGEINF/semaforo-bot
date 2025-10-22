#!/bin/bash
# Script de inicio para Render con Playwright

# Variables de entorno para Playwright en headless sin dependencias
export PLAYWRIGHT_BROWSERS_PATH=/tmp/playwright
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0

# Flags para Chromium sin dependencias del sistema
export PLAYWRIGHT_CHROMIUM_ARGS="--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage --disable-gpu --disable-software-rasterizer --disable-extensions"

# Iniciar uvicorn
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
