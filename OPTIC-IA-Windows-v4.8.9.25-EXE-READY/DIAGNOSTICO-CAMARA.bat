@echo off
setlocal
cd /d "%~dp0"
title OPTIC IA - Diagnostico UCMOS

echo OPTIC IA - Diagnostico Windows
if exist "toupcam.dll" (echo [OK] toupcam.dll presente) else (echo [FALTA] toupcam.dll)
where py >nul 2>nul && echo [OK] Python Launcher detectado
where python >nul 2>nul && echo [OK] Python detectado
powershell -NoProfile -Command "Get-PnpDevice ^| Where-Object { $_.FriendlyName -match 'Toup|USB2.0 Camera|USB3.0 Camera|UCMOS' } ^| Format-Table -AutoSize Status,Class,FriendlyName,InstanceId"
echo.
echo Si Windows ve la camara pero OPTIC no, verifique que ToupLite/ToupView este cerrado.
pause
