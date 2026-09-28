@echo off
setlocal
cd /d "%~dp0"
title OPTIC IA - Microscopio UCMOS

echo ================================================
echo       OPTIC IA - Windows - UCMOS Bridge
echo ================================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  set PY=py -3
) else (
  where python >nul 2>nul
  if not %errorlevel%==0 (
    echo ERROR: Python 3 no esta instalado o no esta en PATH.
    echo Instale Python 3 para Windows y vuelva a ejecutar OPTIC IA.
    pause
    exit /b 1
  )
  set PY=python
)

if not exist "toupcam.dll" (
  echo ERROR: falta toupcam.dll junto a OPTIC IA.
  echo.
  echo Instale ToupLite/ToupView para Windows y copie el toupcam.dll x64
  echo compatible con su camara a esta carpeta.
  echo Fuente oficial: ToupCamSDK para Windows.
  echo.
  pause
  exit /b 2
)

echo Iniciando UCMOS Bridge...
start "OPTIC IA Bridge" /min cmd /c "%PY% optic_bridge.py"

echo Esperando la camara...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ok=$false; 1..30 ^| %% { try { $s=Invoke-RestMethod -Uri 'http://127.0.0.1:8765/status' -TimeoutSec 1; if($s.ok){$ok=$true; break} } catch {}; Start-Sleep -Milliseconds 500 }; if($ok){exit 0}else{exit 1}"
if not %errorlevel%==0 (
  echo.
  echo La UCMOS no entrego imagen. Abra DIAGNOSTICO-CAMARA.bat.
  pause
  exit /b 3
)

start "" "http://127.0.0.1:8765/app"
exit /b 0
