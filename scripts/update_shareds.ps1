# =============================================================================
# update_shareds.ps1
# Atualiza o wheel do pacote privado 'shareds' e rebuilda a imagem Docker.
# Uso:
#   .\scripts\update_shareds.ps1              # apenas atualiza o wheel
#   .\scripts\update_shareds.ps1 -Rebuild     # atualiza o wheel + rebuild Docker
#   .\scripts\update_shareds.ps1 -Rebuild -Up # atualiza + rebuild + sobe container
# =============================================================================

param(
    [switch]$Rebuild,
    [switch]$Up,
    [string]$Port = "8001"
)

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot
$WHEELS_DIR = Join-Path $ROOT "wheels"
$PYTHON = Join-Path $ROOT ".venv\Scripts\python.exe"
$IMAGE_NAME = "qbem-backoffice-eb"
$CONTAINER_NAME = "qbem-backoffice-eb"
$ENV_FILE = Join-Path $ROOT ".env"
$SHAREDS_REPO = "git+https://github.com/qbem-repos/dados-py-shareds.git@master"

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Atualizando wheel do pacote 'shareds'..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Limpa wheels antigos do shareds
if (Test-Path $WHEELS_DIR) {
    Get-ChildItem -Path $WHEELS_DIR -Filter "shareds-*.whl" | Remove-Item -Force
    Write-Host "[1/4] Wheels antigos removidos." -ForegroundColor Yellow
} else {
    New-Item -ItemType Directory -Path $WHEELS_DIR | Out-Null
    Write-Host "[1/4] Diretório 'wheels/' criado." -ForegroundColor Yellow
}

# 2. Gera novo wheel
Write-Host "[2/4] Gerando novo wheel do shareds..." -ForegroundColor Yellow
& $PYTHON -m pip wheel --no-deps --wheel-dir $WHEELS_DIR $SHAREDS_REPO

# 3. Identifica o wheel gerado e atualiza o Dockerfile
$newWheel = Get-ChildItem -Path $WHEELS_DIR -Filter "shareds-*.whl" | Select-Object -First 1
if (-not $newWheel) {
    Write-Host "ERRO: Wheel nao gerado. Verifique acesso ao repositorio." -ForegroundColor Red
    exit 1
}

Write-Host "[3/4] Wheel gerado: $($newWheel.Name)" -ForegroundColor Green

$dockerfilePath = Join-Path $ROOT "Dockerfile"
$dockerfileContent = Get-Content $dockerfilePath -Raw
$updatedContent = $dockerfileContent -replace "wheels/shareds-[^\s]+\.whl", "wheels/$($newWheel.Name)"
Set-Content -Path $dockerfilePath -Value $updatedContent -NoNewline
Write-Host "[3/4] Dockerfile atualizado com '$($newWheel.Name)'." -ForegroundColor Green

# 4. Rebuild Docker (opcional)
if ($Rebuild) {
    Write-Host ""
    Write-Host "[4/4] Iniciando build da imagem Docker '$IMAGE_NAME'..." -ForegroundColor Yellow
    docker build -t $IMAGE_NAME $ROOT
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: Build falhou." -ForegroundColor Red
        exit 1
    }
    Write-Host "[4/4] Build concluido com sucesso!" -ForegroundColor Green
} else {
    Write-Host "[4/4] Rebuild nao solicitado. Execute com -Rebuild para reconstruir a imagem." -ForegroundColor DarkGray
}

# 5. Sobe container (opcional)
if ($Up -and $Rebuild) {
    Write-Host ""
    Write-Host "[5/5] Subindo container '$CONTAINER_NAME' na porta $Port..." -ForegroundColor Yellow
    docker rm -f $CONTAINER_NAME 2>$null
    docker run -d --name $CONTAINER_NAME -p "${Port}:8000" --env-file $ENV_FILE $IMAGE_NAME
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: Falha ao subir container." -ForegroundColor Red
        exit 1
    }
    Start-Sleep -Seconds 3
    Write-Host ""
    Write-Host "Container rodando! Logs:" -ForegroundColor Green
    docker logs $CONTAINER_NAME
    Write-Host ""
    Write-Host "API disponivel em: http://localhost:$Port/backoffice/v1/docs" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Concluido!" -ForegroundColor Green
Write-Host ""
