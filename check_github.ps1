# Script de verificacion para GitHub
Write-Host "`nVerificando archivos para GitHub...`n" -ForegroundColor Cyan

# Archivos criticos
$files = @(
    ".gitignore",
    ".env.example",
    "README.md",
    "requirements.txt",
    "render.yaml",
    "Procfile",
    "DEPLOYMENT.md",
    "config.json",
    "main.py",
    "api_longshort_ondemand.py",
    "scrape_coinglass_v6_dropdown.py"
)

Write-Host "Archivos encontrados:" -ForegroundColor Yellow
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  OK: $file" -ForegroundColor Green
    } else {
        Write-Host "  FALTA: $file" -ForegroundColor Red
    }
}

Write-Host "`nComandos para subir a GitHub:`n" -ForegroundColor Magenta
Write-Host "git init"
Write-Host "git add ."
Write-Host "git commit -m 'Initial commit: SemaforoBot v1.0.0'"
Write-Host "git remote add origin https://github.com/TU_USUARIO/semaforo-bot.git"
Write-Host "git branch -M main"
Write-Host "git push -u origin main"
Write-Host ""
