@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ========================================================
echo   PortableAI - Target Environment Diagnostics
echo   Folder: %CD%
echo ========================================================
echo.

echo [1] OS, Architecture ^& Processor (Intel / AMD)
ver
echo PROCESSOR_ARCHITECTURE=%PROCESSOR_ARCHITECTURE%
echo PROCESSOR_IDENTIFIER=%PROCESSOR_IDENTIFIER%
powershell -NoProfile -Command "(Get-CimInstance Win32_Processor).Name" 2>nul
echo [OK] Universal CPU support: Intel Core/Xeon ^& AMD Ryzen/Athlon/FX are fully supported.
echo.

echo [2] System Memory
powershell -NoProfile -Command "$os = Get-CimInstance Win32_OperatingSystem; 'Total RAM (GB): ' + [math]::Round($os.TotalVisibleMemorySize/1MB,2); 'Free RAM (GB): ' + [math]::Round($os.FreePhysicalMemory/1MB,2)" 2>nul
if errorlevel 1 echo (Could not query RAM via PowerShell)
echo.

echo [3] Java Toolchain
where java 2>nul
if errorlevel 1 (
    echo java: NOT FOUND in PATH
) else (
    java -version 2>&1
)
where javac 2>nul
if errorlevel 1 (
    echo javac: NOT FOUND in PATH
) else (
    javac -version 2>&1
)
echo.

echo [4] C Compiler
where gcc 2>nul
if errorlevel 1 (
    echo gcc: NOT FOUND in PATH
) else (
    gcc --version 2>&1 | findstr /n "^" | findstr "^1:"
)
if exist "C:\TurboC++\BIN\TC.EXE" echo Turbo C found at C:\TurboC++\BIN\TC.EXE
if exist "C:\TC\BIN\TC.EXE" echo Turbo C found at C:\TC\BIN\TC.EXE
echo.

echo [5] Portable Python Runtime Check
if exist "runtime\python\python.exe" (
    "runtime\python\python.exe" --version 2>&1
    if errorlevel 1 (
        echo [BLOCKED/ERROR] python.exe exists but failed to execute!
    ) else (
        echo [OK] Portable Python executes properly.
    )
) else (
    echo [MISSING] runtime\python\python.exe
)
echo.

echo [6] Inference Engine Check (llama-server.exe)
if exist "engine\llama-server.exe" (
    "engine\llama-server.exe" --version >nul 2>&1
    if errorlevel 1 (
        echo [BLOCKED/ERROR] llama-server.exe exists but failed to execute!
        echo If blocked by college security policy, DO NOT bypass. Ask IT for an approved location/runtime.
    ) else (
        echo [OK] llama-server.exe executes properly.
    )
) else (
    echo [MISSING] engine\llama-server.exe
)
echo.

echo [7] Local Model Files
set "MCOUNT=0"
for %%F in ("models\*.gguf") do (
    set /a MCOUNT+=1
    echo   Found: %%~nxF ^(%%~zF bytes^)
)
if "%MCOUNT%"=="0" echo [MISSING] No .gguf model files found in models\
echo.

echo [8] Folder Write Permissions
if not exist "output" mkdir "output" 2>nul
if not exist "logs" mkdir "logs" 2>nul
echo test > "output\_write_test.tmp" 2>nul
if exist "output\_write_test.tmp" (
    del "output\_write_test.tmp" >nul 2>&1
    echo [OK] output\ is writable.
) else (
    echo [ERROR] Cannot write to output\
)
echo test > "logs\_write_test.tmp" 2>nul
if exist "logs\_write_test.tmp" (
    del "logs\_write_test.tmp" >nul 2>&1
    echo [OK] logs\ is writable.
) else (
    echo [ERROR] Cannot write to logs\
)
echo.

echo ========================================================
echo   Diagnostics Complete.
echo ========================================================
pause
