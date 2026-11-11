@echo off
setlocal
title DJ THE OFFSPRIN STUDIOS - MOTOR GRATIS
cd /d "%~dp0"
echo ==================================================
echo   DJ THE OFFSPRIN STUDIOS - MOTOR REMIX GRATIS
echo ==================================================
echo.

rem ---- 1) Buscar Python (recomendado 3.11) ----
set "PY="
py -3.11 --version >nul 2>nul && set "PY=py -3.11"
if not defined PY py -3.12 --version >nul 2>nul && set "PY=py -3.12"
if not defined PY py -3.10 --version >nul 2>nul && set "PY=py -3.10"
if not defined PY py -3.13 --version >nul 2>nul && set "PY=py -3.13"
if not defined PY (
  echo Python no esta instalado. Instalandolo AUTOMATICAMENTE ^(gratis, 1-3 minutos^)...
  where winget >nul 2>nul
  if not errorlevel 1 winget install -e --id Python.Python.3.11 --scope user --silent --accept-package-agreements --accept-source-agreements
  if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set PY="%LocalAppData%\Programs\Python\Python311\python.exe"
)
if not defined PY (
  echo.
  echo [ERROR] No se pudo instalar Python automaticamente.
  echo Instalalo a mano ^(gratis^): https://www.python.org/downloads/release/python-3119/
  echo y marca "Add python.exe to PATH". Luego abre este archivo otra vez.
  echo.
  pause
  exit /b 1
)
echo [OK] Python encontrado: %PY%
%PY% --version

rem ---- 2) Entorno local ----
if not exist ".venv\Scripts\python.exe" (
  echo Creando entorno local...
  %PY% -m venv .venv
  if errorlevel 1 (
    echo [ERROR] No se pudo crear el entorno. Borra la carpeta .venv si existe y vuelve a intentar.
    pause
    exit /b 1
  )
)
set "VPY=%~dp0.venv\Scripts\python.exe"

rem ---- 3) Instalacion ^(solo la primera vez, ~1 minuto^) ----
if not exist ".venv\instalado2.ok" (
  echo.
  echo Instalando componentes ligeros. Solo la primera vez.
  "%VPY%" -m pip install --upgrade pip
  "%VPY%" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo [ERROR] Fallo la instalacion. Revisa tu conexion a internet y toma captura de este mensaje.
    pause
    exit /b 1
  )
  echo ok> ".venv\instalado2.ok"
)

rem ---- 4) Iniciar ----
echo.
echo ==================================================
echo  LISTO. Se abrira el navegador en unos segundos.
echo  Si no se abre, entra a:  http://127.0.0.1:5000
echo  NO CIERRES ESTA VENTANA mientras uses el programa.
echo  La primera vez que separes una voz se descarga
echo  el modelo de IA gratis ^(~67 MB^): espera sin cerrar.
echo ==================================================
echo.
start "" cmd /c "timeout /t 5 >nul & start http://127.0.0.1:5000"
"%VPY%" server.py
echo.
echo [AVISO] El servidor se detuvo. Si fue por un error, toma captura de las lineas de arriba.
pause
