@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ========================================================
echo   PortableAI - Offline Coding Assistant Launcher
echo   Working Directory: %CD%
echo ========================================================

if not exist "runtime\python\python.exe" (
    echo [ERROR] Portable Python not found at runtime\python\python.exe
    pause
    exit /b 1
)

if not exist "engine\llama-server.exe" (
    echo [ERROR] Inference engine not found at engine\llama-server.exe
    pause
    exit /b 1
)

if not exist "app\portable_ai.py" (
    echo [ERROR] Application script not found at app\portable_ai.py
    pause
    exit /b 1
)

set "MODEL_FOUND=0"
for %%F in ("models\*.gguf") do set "MODEL_FOUND=1"
if "%MODEL_FOUND%"=="0" (
    echo [ERROR] No .gguf model file found in models\
    pause
    exit /b 1
)

if not exist "output" mkdir "output"
if not exist "logs" mkdir "logs"

"runtime\python\python.exe" -u "app\portable_ai.py"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo [ERROR] PortableAI exited with code %EXIT_CODE%.
    echo Check logs\llama-server.log for engine details.
    pause
)
exit /b %EXIT_CODE%
