@echo off
setlocal

rem Windows launcher: use the local Python 3.12 install instead of WindowsApps python alias.
set "PYTHON_EXE=C:\python312\python.exe"

if not exist "%PYTHON_EXE%" (
    echo Python not found: %PYTHON_EXE%
    echo Please install Python or edit PYTHON_EXE in run.bat.
    exit /b 1
)

"%PYTHON_EXE%" main.py %*
