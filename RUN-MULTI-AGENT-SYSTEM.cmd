@echo off
setlocal
title Deep Research Multi-Agent System

cd /d "%~dp0"
set "LOG_FILE=%~dp0launcher-log.txt"

echo Deep Research Multi-Agent System launcher > "%LOG_FILE%"
echo Started: %DATE% %TIME% >> "%LOG_FILE%"
echo Folder: %CD% >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

set "PYTHON_EXE=C:\Users\nguye\AppData\Local\Programs\Python\Python313\python.exe"

if not exist "%PYTHON_EXE%" (
  echo Primary Python path not found: %PYTHON_EXE% >> "%LOG_FILE%"
  for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python313-32\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312-32\python.exe"
    "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
  ) do (
    if exist %%~P (
      set "PYTHON_EXE=%%~P"
      goto found_python
    )
  )
  echo Python was not found at:
  echo %PYTHON_EXE%
  echo.
  echo Open the Python installer again and install Python for your user account.
  echo Make sure "Add Python to environment variables" is checked.
  echo.
  echo Python was not found. >> "%LOG_FILE%"
  pause
  exit /b 1
)

:found_python
echo Using Python:
echo %PYTHON_EXE%
echo.
echo Using Python: %PYTHON_EXE% >> "%LOG_FILE%"
"%PYTHON_EXE%" --version >> "%LOG_FILE%" 2>&1

set "BITS_FILE=%TEMP%\deep-research-python-bits.txt"
"%PYTHON_EXE%" -c "import platform; print(platform.architecture()[0])" > "%BITS_FILE%" 2>> "%LOG_FILE%"
if errorlevel 1 (
  echo.
  echo Python was found, but the launcher could not run it correctly.
  echo A log was written to:
  echo %LOG_FILE%
  pause
  exit /b 1
)
set /p PYTHON_BITS=<"%BITS_FILE%"
echo Python architecture: %PYTHON_BITS% >> "%LOG_FILE%"

if /i not "%PYTHON_BITS%"=="64bit" (
  echo.
  echo This project needs 64-bit Python.
  echo Your current Python is: %PYTHON_BITS%
  echo.
  echo The LangGraph/OpenAI dependency stack needs packages that do not reliably install
  echo on 32-bit Windows Python, including tiktoken and ormsgpack.
  echo.
  echo Fix:
  echo 1. Uninstall Python 3.13 32-bit.
  echo 2. Install the 64-bit Windows Python installer from python.org.
  echo 3. Check "Add Python to environment variables" during install.
  echo 4. Run this launcher again.
  echo.
  echo Stopped because Python is not 64-bit. >> "%LOG_FILE%"
  echo A log was written to:
  echo %LOG_FILE%
  pause
  exit /b 1
)

if exist ".venv\pyvenv.cfg" (
  findstr /i "Python313-32 Python312-32 32-bit" ".venv\pyvenv.cfg" >nul 2>&1
  if not errorlevel 1 (
    echo Removing old 32-bit virtual environment...
    echo Removing old 32-bit virtual environment... >> "%LOG_FILE%"
    rmdir /s /q ".venv"
  )
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating local Python environment...
  echo Creating local Python environment... >> "%LOG_FILE%"
  "%PYTHON_EXE%" -m venv .venv >> "%LOG_FILE%" 2>&1
  if errorlevel 1 (
    echo.
    echo Could not create the virtual environment.
    echo Could not create the virtual environment. >> "%LOG_FILE%"
    echo.
    echo A log was written to:
    echo %LOG_FILE%
    pause
    exit /b 1
  )
)

echo Installing project requirements...
echo Installing project requirements... >> "%LOG_FILE%"
".venv\Scripts\python.exe" -m pip install --upgrade pip >> "%LOG_FILE%" 2>&1
".venv\Scripts\python.exe" -m pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo.
  echo Could not install the requirements.
  echo If this mentions network access, check your internet connection and run this launcher again.
  echo Could not install the requirements. >> "%LOG_FILE%"
  echo.
  echo A log was written to:
  echo %LOG_FILE%
  pause
  exit /b 1
)

echo.
echo Running the multi-agent system...
echo.
".venv\Scripts\python.exe" run_research.py "Research multi-agent AI systems" >> "%LOG_FILE%" 2>&1
type "%LOG_FILE%"

echo.
echo Done.
echo Done. >> "%LOG_FILE%"
pause
