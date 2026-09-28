@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  set PY=py -3
) else (
  set PY=python
)
%PY% -m pip install --upgrade pyinstaller
if errorlevel 1 goto :err
%PY% -m PyInstaller --clean --noconfirm OPTIC-IA.spec
if errorlevel 1 goto :err
echo.
echo EXE generado en: dist\OPTIC-IA.exe
pause
exit /b 0
:err
echo.
echo ERROR al compilar OPTIC IA.
pause
exit /b 1
