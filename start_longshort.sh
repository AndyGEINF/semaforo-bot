#!/bin/bash
# Script de inicio para API Long/Short con Playwright

echo "🚀 [$(date +%H:%M:%S)] START_LONGSHORT.SH - Iniciando..."

# Variables de entorno para Playwright en headless sin dependencias
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/.playwright
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0

# Flags para Chromium sin dependencias del sistema
export PLAYWRIGHT_CHROMIUM_ARGS="--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage --disable-gpu --disable-software-rasterizer --disable-extensions"

echo "📍 PLAYWRIGHT_BROWSERS_PATH=$PLAYWRIGHT_BROWSERS_PATH"
echo "📍 PORT=${PORT:-8001}"

# 🔥 CRÍTICO: FORZAR instalación de Chromium en CADA inicio
# Render borra /tmp entre despliegues, necesitamos reinstalar
echo "🔍 [$(date +%H:%M:%S)] Verificando Chromium..."

# Verificar si el ejecutable de Chromium existe
CHROMIUM_PATH="$PLAYWRIGHT_BROWSERS_PATH/chromium-*/chrome-linux/headless_shell"
if ls $CHROMIUM_PATH 1> /dev/null 2>&1; then
    echo "✅ [$(date +%H:%M:%S)] Chromium ya está instalado"
else
    echo "⚠️ [$(date +%H:%M:%S)] Chromium NO encontrado, instalando..."
    echo "   Esto tomará ~30-60 segundos..."
    
    # Instalar Chromium (sin dependencias del sistema)
    python -m playwright install chromium --no-shell
    
    if [ $? -eq 0 ]; then
        echo "✅ [$(date +%H:%M:%S)] Chromium instalado exitosamente"
    else
        echo "❌ [$(date +%H:%M:%S)] ERROR instalando Chromium"
        exit 1
    fi
fi

# Verificar tamaño del directorio de Playwright
if [ -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then
    SIZE=$(du -sh "$PLAYWRIGHT_BROWSERS_PATH" | cut -f1)
    echo "📦 Tamaño de Playwright browsers: $SIZE"
else
    echo "⚠️ Directorio $PLAYWRIGHT_BROWSERS_PATH no existe"
fi

# Iniciar uvicorn
echo "🚀 [$(date +%H:%M:%S)] Iniciando servidor SSE en puerto ${PORT:-8001}..."
exec uvicorn api_longshort_ondemand:app --host 0.0.0.0 --port ${PORT:-8001} --log-level info

