@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: ============================================================
::  SudokuSolver Launcher - Windows
::  Auto-detects Python, creates venv, installs dependencies
::  Usage: launch.bat [--repair]
:: ============================================================

title SudokuSolver Launcher
set "MIN_MAJOR=3"
set "MIN_MINOR=10"
set "REPAIR_MODE=0"

:: Check for --repair flag
set "APP_ARGS="
for %%a in (%*) do (
    if /i "%%a"=="--repair" (
        set "REPAIR_MODE=1"
    ) else (
        set "APP_ARGS=!APP_ARGS! %%a"
    )
)

echo.
echo  ===================================================
echo   SudokuSolver
echo   Launcher / Lanceur automatique
echo  ===================================================
echo.

:: Change to script directory (pushd handles UNC network paths)
pushd "%~dp0" || (
    echo  [!] Cannot access script directory / Repertoire inaccessible
    pause
    exit /b 1
)

:: Use absolute paths (critical for UNC and mapped drives)
set "SCRIPT_DIR=%CD%"
set "VENV_DIR=%APPDATA%\SudokuSolver\venv"
set "REQ_FILE=%SCRIPT_DIR%\requirements.txt"
set "MAIN_SCRIPT=%SCRIPT_DIR%\main.py"

:: Warn if running from a network/UNC path (very slow for pip)
set "ORIG_PATH=%~dp0"
if "!ORIG_PATH:~0,2!"=="\\" (
    echo  [!] WARNING: Running from a network path is very slow!
    echo      ATTENTION: Lancement depuis un chemin reseau, tres lent !
    echo      Use the local copy instead / Utilisez la copie locale
    echo.
)

:: ----------------------------------------------------------
::  Repair mode: delete venv and stamp to force full reinstall
:: ----------------------------------------------------------
if "!REPAIR_MODE!"=="1" (
    echo  [REPAIR] Repair mode enabled / Mode reparation active
    echo.
    if exist "!VENV_DIR!" (
        echo  [REPAIR] Removing virtual environment...
        echo           Suppression de l'environnement virtuel...
        rmdir /s /q "!VENV_DIR!"
        echo  [OK] Virtual environment removed / Environnement virtuel supprime
    )
    echo.
)

:: ----------------------------------------------------------
::  Step 1/4: Find a working Python >= 3.10
:: ----------------------------------------------------------
echo  [Step 1/4] Searching for Python... / Recherche de Python...

set "PYTHON_CMD="

:: 1a. Try common install locations first (most reliable, avoids Store alias)
for %%p in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%APPDATA%\Programs\Python\Python313\python.exe"
    "%APPDATA%\Programs\Python\Python312\python.exe"
    "%APPDATA%\Programs\Python\Python311\python.exe"
    "%APPDATA%\Programs\Python\Python310\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "%ProgramFiles%\Python313\python.exe"
    "%ProgramFiles%\Python312\python.exe"
    "%ProgramFiles%\Python311\python.exe"
    "%ProgramFiles%\Python310\python.exe"
) do (
    if exist "%%~p" (
        "%%~p" -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
        if !errorlevel! equ 0 (
            for /f "tokens=*" %%v in ('"%%~p" --version 2^>^&1') do echo             Found / Trouve : %%v
            set "PYTHON_CMD=%%~p"
            goto :python_found
        )
    )
)

:: 1b. Try py launcher (Windows Python Launcher)
where py >nul 2>&1
if !errorlevel! equ 0 (
    py -3 -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%v in ('py -3 --version 2^>^&1') do echo             Found / Trouve : %%v ^(py launcher^)
        set "PYTHON_CMD=py -3"
        goto :python_found
    )
)

:: 1c. Try python3 / python in PATH (verify it actually works, not Store alias)
for %%c in (python3 python) do (
    where %%c >nul 2>&1
    if !errorlevel! equ 0 (
        %%c -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
        if !errorlevel! equ 0 (
            for /f "tokens=*" %%v in ('%%c --version 2^>^&1') do echo             Found / Trouve : %%v
            set "PYTHON_CMD=%%c"
            goto :python_found
        )
    )
)

:: Python not found
echo.
echo  [!] Python %MIN_MAJOR%.%MIN_MINOR%+ not found!
echo      Python %MIN_MAJOR%.%MIN_MINOR%+ introuvable !
echo.
echo  Install from / Installez depuis : https://www.python.org
pause
popd
exit /b 1

:python_found
echo.

:: ----------------------------------------------------------
::  Step 2/4: Create or verify virtual environment
:: ----------------------------------------------------------
echo  [Step 2/4] Checking virtual environment... / Verification environnement virtuel...

set "VENV_OK=0"

if exist "!VENV_DIR!\Scripts\python.exe" (
    "!VENV_DIR!\Scripts\python.exe" -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
    if !errorlevel! equ 0 (
        set "VENV_OK=1"
        echo             OK
    ) else (
        echo             Corrupted / Corrompu - recreating...
        rmdir /s /q "!VENV_DIR!"
    )
)

if "!VENV_OK!"=="0" (
    echo             Creating... / Creation...
    if not exist "%APPDATA%\SudokuSolver" mkdir "%APPDATA%\SudokuSolver" 2>nul
    %PYTHON_CMD% -m venv "!VENV_DIR!"
    if !errorlevel! neq 0 (
        echo  [!] Venv creation failed / Echec creation venv
        pause
        popd
        exit /b 1
    )
    if not exist "!VENV_DIR!\Scripts\python.exe" (
        echo  [!] Venv created but python.exe not found / Venv cree mais python.exe introuvable
        pause
        popd
        exit /b 1
    )
    echo             Created / Cree
)

set "PYTHON_CMD=!VENV_DIR!\Scripts\python.exe"
set "PYTHONW_CMD=!VENV_DIR!\Scripts\pythonw.exe"
set "PIP_CMD=!VENV_DIR!\Scripts\pip.exe"

:: ----------------------------------------------------------
::  Step 3/4: Install dependencies
:: ----------------------------------------------------------
echo.
echo  [Step 3/4] Checking dependencies... / Verification des dependances...

set "STAMP=!VENV_DIR!\.deps_stamp"
set "NEED_INSTALL=0"

if not exist "!STAMP!" (
    set "NEED_INSTALL=1"
) else (
    fc /b "!REQ_FILE!" "!STAMP!" >nul 2>&1
    if !errorlevel! neq 0 (
        echo             Requirements changed / Dependances modifiees
        set "NEED_INSTALL=1"
    )
)

:: Quick import check: verify key packages are importable
if "!NEED_INSTALL!"=="0" (
    "!PYTHON_CMD!" -c "import PyQt6, PIL" >nul 2>&1
    if !errorlevel! neq 0 (
        echo             Missing packages detected / Paquets manquants
        set "NEED_INSTALL=1"
    )
)

if "!NEED_INSTALL!"=="1" (
    echo             Installing... this may take 1-2 minutes on first run
    echo             Installation... cela peut prendre 1-2 min au premier lancement
    echo.

    "!PIP_CMD!" install --upgrade pip --quiet >nul 2>&1

    "!PIP_CMD!" install -r "!REQ_FILE!"
    if !errorlevel! neq 0 (
        echo.
        echo  [!] Installation failed! Try: launch.bat --repair
        echo      Echec ! Essayez : launch.bat --repair
        pause
        popd
        exit /b 1
    )

    copy /y "!REQ_FILE!" "!STAMP!" >nul 2>&1

    echo.
    echo  [OK] All dependencies installed / Toutes les dependances installees
) else (
    echo             Up to date / A jour
)

:: ----------------------------------------------------------
::  Step 4/4: Launch SudokuSolver
:: ----------------------------------------------------------
echo.
echo  ===================================================
echo   [Step 4/4] Launching SudokuSolver... / Lancement...
echo  ===================================================
echo.

if not exist "!PYTHON_CMD!" (
    echo  [!] Python not found at: !PYTHON_CMD!
    echo      Try: launch.bat --repair
    pause
    popd
    exit /b 1
)
if not exist "!MAIN_SCRIPT!" (
    echo  [!] main.py not found at: !MAIN_SCRIPT!
    pause
    popd
    exit /b 1
)

:: Prefer pythonw.exe to avoid a console window behind the GUI
if exist "!PYTHONW_CMD!" (
    start "" "!PYTHONW_CMD!" "!MAIN_SCRIPT!" !APP_ARGS!
) else (
    "!PYTHON_CMD!" "!MAIN_SCRIPT!" !APP_ARGS!
)

popd
endlocal
exit /b 0
