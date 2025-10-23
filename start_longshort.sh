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
if compgen -G "$CHROMIUM_PATH" > /dev/null; then
    echo "✅ [$(date +%H:%M:%S)] Chromium ya está instalado"
    ls -lh $CHROMIUM_PATH | head -1
else
    echo "⚠️ [$(date +%H:%M:%S)] Chromium NO encontrado en $PLAYWRIGHT_BROWSERS_PATH"
    echo "   Instalando... (esto tomará ~30-60 segundos)"
    
    # Crear directorio si no existe
    mkdir -p "$PLAYWRIGHT_BROWSERS_PATH"
    
    # Instalar Chromium (sin dependencias del sistema)
    if python -m playwright install chromium --no-shell; then
        echo "✅ [$(date +%H:%M:%S)] Chromium instalado exitosamente"
        # Verificar instalación
        if compgen -G "$CHROMIUM_PATH" > /dev/null; then
            ls -lh $CHROMIUM_PATH | head -1
        else
            echo "❌ [$(date +%H:%M:%S)] ERROR: Chromium instalado pero no encontrado en ruta esperada"
            echo "   Buscando en todo PLAYWRIGHT_BROWSERS_PATH..."
            find "$PLAYWRIGHT_BROWSERS_PATH" -name "headless_shell" 2>/dev/null || echo "   No se encontró headless_shell"
        fi
    else
        echo "❌ [$(date +%H:%M:%S)] ERROR instalando Chromium (código: $?)"
        echo "   El servicio intentará continuar, pero el scraping fallará"
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

