# ============================================
# 📦 Preparación para GitHub Repository
# ============================================

Write-Host "`n╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         🔍 VERIFICANDO ARCHIVOS PARA GITHUB                     ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "main.py")) {
    Write-Host "❌ Error: No se encuentra main.py. Ejecuta este script desde la raíz del proyecto." -ForegroundColor Red
    exit 1
}

Write-Host "📋 Checklist de archivos:" -ForegroundColor Yellow
Write-Host ""

# Array de archivos críticos
$criticalFiles = @(
    @{Name=".gitignore"; Required=$true},
    @{Name=".env.example"; Required=$true},
    @{Name="README.md"; Required=$true},
    @{Name="requirements.txt"; Required=$true},
    @{Name="render.yaml"; Required=$false},
    @{Name="Procfile"; Required=$false},
    @{Name="DEPLOYMENT.md"; Required=$false},
    @{Name="config.json"; Required=$true},
    @{Name="main.py"; Required=$true},
    @{Name="api_longshort_ondemand.py"; Required=$true},
    @{Name="scrape_coinglass_v6_dropdown.py"; Required=$true}
)

$allGood = $true

foreach ($file in $criticalFiles) {
    if (Test-Path $file.Name) {
        Write-Host "   ✅ $($file.Name)" -ForegroundColor Green
    } else {
        if ($file.Required) {
            Write-Host "   ❌ $($file.Name) - REQUERIDO" -ForegroundColor Red
            $allGood = $false
        } else {
            Write-Host "   ⚠️  $($file.Name) - Opcional" -ForegroundColor Yellow
        }
    }
}

Write-Host ""

# Verificar que .env NO esté en el repo
if (Test-Path ".env") {
    Write-Host "⚠️  ADVERTENCIA: Archivo .env encontrado" -ForegroundColor Yellow
    Write-Host "   Verifica que .gitignore lo excluya correctamente" -ForegroundColor Yellow
    Write-Host "   Nunca subas .env a GitHub (contiene secretos)" -ForegroundColor Red
    Write-Host ""
}

# Verificar archivos que NO deberían subirse
Write-Host "🔒 Verificando archivos sensibles excluidos:" -ForegroundColor Yellow
$sensitivePatterns = @("*.env", "*.log", "__pycache__", "venv/", ".vscode/")
$foundSensitive = $false

foreach ($pattern in $sensitivePatterns) {
    $files = Get-ChildItem -Path . -Recurse -Filter $pattern -ErrorAction SilentlyContinue
    if ($files) {
        Write-Host "   ℹ️  Encontrado: $pattern (debería estar en .gitignore)" -ForegroundColor Cyan
        $foundSensitive = $true
    }
}

if (-not $foundSensitive) {
    Write-Host "   ✅ No se encontraron archivos sensibles en el directorio" -ForegroundColor Green
}

Write-Host ""

# Estadísticas del proyecto
Write-Host "📊 Estadísticas del proyecto:" -ForegroundColor Yellow
$pyFiles = (Get-ChildItem -Path . -Recurse -Filter "*.py" | Measure-Object).Count
$htmlFiles = (Get-ChildItem -Path . -Recurse -Filter "*.html" | Measure-Object).Count
$mdFiles = (Get-ChildItem -Path . -Recurse -Filter "*.md" | Measure-Object).Count

Write-Host "   • Archivos Python: $pyFiles" -ForegroundColor Cyan
Write-Host "   • Archivos HTML: $htmlFiles" -ForegroundColor Cyan
Write-Host "   • Archivos Markdown: $mdFiles" -ForegroundColor Cyan

Write-Host ""

# Comandos Git sugeridos
if ($allGood) {
    Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║         ✅ TODO LISTO PARA SUBIR A GITHUB                        ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
    
    Write-Host "🚀 Comandos sugeridos para crear el repositorio:`n" -ForegroundColor Magenta
    
    Write-Host "# 1. Inicializar Git (si no está inicializado)" -ForegroundColor Gray
    Write-Host "git init`n" -ForegroundColor White
    
    Write-Host "# 2. Añadir archivos" -ForegroundColor Gray
    Write-Host "git add ." -ForegroundColor White
    Write-Host "git status  # Verificar qué se va a subir`n" -ForegroundColor White
    
    Write-Host "# 3. Hacer commit" -ForegroundColor Gray
    Write-Host 'git commit -m "Initial commit: SemáforoBot v1.0.0"' -ForegroundColor White
    Write-Host ""
    
    Write-Host "# 4. Crear repo en GitHub y conectarlo" -ForegroundColor Gray
    Write-Host "# Opción A: Repo nuevo" -ForegroundColor DarkGray
    Write-Host 'git remote add origin https://github.com/TU_USUARIO/semaforo-bot.git' -ForegroundColor White
    Write-Host "git branch -M main" -ForegroundColor White
    Write-Host "git push -u origin main`n" -ForegroundColor White
    
    Write-Host "# Opción B: Ya tienes el repo creado" -ForegroundColor DarkGray
    Write-Host "git remote add origin <URL_DEL_REPO>" -ForegroundColor White
    Write-Host "git push -u origin main`n" -ForegroundColor White
    
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
    
    Write-Host "📝 Después de subir, podrás:" -ForegroundColor Yellow
    Write-Host "   • Desplegar en Render (detectará render.yaml automáticamente)" -ForegroundColor Cyan
    Write-Host "   • Desplegar en Railway" -ForegroundColor Cyan
    Write-Host "   • Colaborar con otros desarrolladores" -ForegroundColor Cyan
    Write-Host "   • Activar GitHub Actions (CI/CD)" -ForegroundColor Cyan
    Write-Host ""
    
} else {
    Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║         ❌ FALTAN ARCHIVOS CRÍTICOS                             ║" -ForegroundColor Red
    Write-Host "╚══════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Red
    
    Write-Host "⚠️  Corrige los errores antes de subir a GitHub" -ForegroundColor Yellow
    Write-Host ""
}

# Verificar si Git está instalado
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitInstalled) {
    Write-Host "⚠️  Git no está instalado. Descárgalo de: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "✨ Verificación completada`n" -ForegroundColor Green
