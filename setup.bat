@echo off
echo ========================================
echo AI Video Generator - Setup Script
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo Python found!
echo.

echo [2/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed!
echo.

echo [3/4] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo Created .env file from template
    echo IMPORTANT: Edit .env and add your API keys!
) else (
    echo .env file already exists
)
echo.

echo [4/4] Creating __init__.py for src package...
type nul > src\__init__.py
echo Created src\__init__.py
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your API keys
echo 2. Run: cd src
echo 3. Run: python main.py
echo.
echo For help, see README.md
echo.
pause
