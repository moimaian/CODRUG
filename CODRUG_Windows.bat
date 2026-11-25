@echo off
rem ============================================================================
rem  CODRUG - Instalador/lancador para Windows 10/11 (duplo clique)
rem
rem  1. Procura o Python 3.10 ou mais novo (py launcher, pasta padrao, PATH).
rem  2. Se nao achar, baixa o Python 3.10.11 do python.org (confere a assinatura
rem     digital) e instala so para o usuario atual, sem pedir administrador.
rem  3. Executa "python CODRUG.py" ja confirmando as perguntas do bootstrap
rem     (CODRUG_ASSUME_YES=1, equivale a responder S): cria o ambiente virtual
rem     com o Python 3.10.11, instala o runtime Visual C++ do Qt5, as
rem     bibliotecas essenciais e cria os atalhos CODRUG.lnk.
rem
rem  So e preciso na primeira vez: depois use o atalho CODRUG da Area de Trabalho
rem  ou do Menu Iniciar.
rem ============================================================================
setlocal EnableExtensions
title CODRUG - Instalacao e inicializacao
cd /d "%~dp0"

set "CODRUG_ASSUME_YES=1"
set "PY_VER=3.10.11"
set "PY_URL=https://www.python.org/ftp/python/%PY_VER%/python-%PY_VER%-amd64.exe"
set "PYEXE="

echo.
echo ============================================================
echo   CODRUG - preparando o ambiente (somente na primeira vez)
echo ============================================================
echo.

call :find_python
if defined PYEXE goto run

echo [CODRUG] Python nao encontrado neste computador.
echo [CODRUG] Instalando o Python %PY_VER% (somente para o seu usuario)...
call :install_python
if errorlevel 1 goto python_failed
call :find_python
if not defined PYEXE goto python_failed

:run
echo [CODRUG] Usando o Python: %PYEXE%
echo.
"%PYEXE%" "%~dp0CODRUG.py" %*
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
    echo.
    echo [CODRUG] O CODRUG terminou com o codigo %RC%. Leia as mensagens acima.
    pause
)
exit /b %RC%

:python_failed
echo.
echo [CODRUG] ERRO: nao foi possivel instalar o Python %PY_VER% automaticamente.
echo          Instale manualmente: %PY_URL%
echo          e depois de um duplo clique neste arquivo de novo.
pause
exit /b 1

rem ---------------------------------------------------------------------------
rem  Define PYEXE com um Python 3.10+ que funcione (vazio se nao houver).
rem ---------------------------------------------------------------------------
:find_python
set "PYEXE="
for /f "usebackq delims=" %%i in (`py -3.10 -c "import sys; print(sys.executable)" 2^>nul`) do if not defined PYEXE set "PYEXE=%%i"
if defined PYEXE if not exist "%PYEXE%" set "PYEXE="
if defined PYEXE exit /b 0

set "PY_DEFAULT=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
if exist "%PY_DEFAULT%" set "PYEXE=%PY_DEFAULT%"
if defined PYEXE exit /b 0

rem "python" do PATH: ignora o atalho falso da Microsoft Store e versoes antigas.
for /f "usebackq delims=" %%i in (`python -c "import sys; print(sys.executable if sys.version_info[:2] >= (3, 10) else '')" 2^>nul`) do if not defined PYEXE set "PYEXE=%%i"
if defined PYEXE if not exist "%PYEXE%" set "PYEXE="
exit /b 0

rem ---------------------------------------------------------------------------
rem  Baixa, confere a assinatura e instala o Python %PY_VER% (por usuario).
rem ---------------------------------------------------------------------------
:install_python
set "PY_INSTALLER=%TEMP%\python-%PY_VER%-amd64.exe"
echo [CODRUG] Baixando %PY_URL%
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -UseBasicParsing -Uri '%PY_URL%' -OutFile '%PY_INSTALLER%'"
if errorlevel 1 exit /b 1
if not exist "%PY_INSTALLER%" exit /b 1

rem So executa o instalador se a assinatura digital for valida e da Python Software Foundation.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s = Get-AuthenticodeSignature '%PY_INSTALLER%'; if ($s.Status -eq 'Valid' -and $s.SignerCertificate.Subject -like '*Python Software Foundation*') { exit 0 } else { exit 1 }"
if errorlevel 1 (
    echo [CODRUG] A assinatura digital do instalador nao confere. Instalacao cancelada.
    del "%PY_INSTALLER%" >nul 2>nul
    exit /b 1
)

echo [CODRUG] Executando o instalador (aguarde, pode levar alguns minutos)...
start /wait "" "%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 Include_test=0 Include_pip=1
del "%PY_INSTALLER%" >nul 2>nul
exit /b 0
