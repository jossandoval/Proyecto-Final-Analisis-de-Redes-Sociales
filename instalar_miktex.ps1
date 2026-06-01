# Script para descargar e instalar MiKTeX
Write-Host "Descargando MiKTeX Basic Installer..." -ForegroundColor Cyan

$miktexUrl = "https://ctan.math.illinois.edu/systems/win32/miktex/setup/windows-x64/miktex-24.1-basic-x64.exe"
$installerPath = "$env:TEMP\miktex-installer.exe"

# Descargar
Write-Host "Descargando desde: $miktexUrl" -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $miktexUrl -OutFile $installerPath -UseBasicParsing -ErrorAction Stop
    Write-Host "[OK] Descarga completada" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] No se pudo descargar: $_" -ForegroundColor Red
    exit 1
}

# Instalar
Write-Host "Iniciando instalacion de MiKTeX..." -ForegroundColor Cyan
Write-Host "Esto puede tomar 5-10 minutos..." -ForegroundColor Yellow
& $installerPath --unattended --shared=yes --install-miktex=yes

Write-Host "[OK] MiKTeX instalado" -ForegroundColor Green
Write-Host "Ahora puedes ejecutar: cd c:\Users\GoodM\OneDrive\Escritorio\PFARS\reporte; pdflatex reporte_final.tex" -ForegroundColor Cyan
