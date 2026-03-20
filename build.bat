@echo off
setlocal enabledelayedexpansion
title MOGLabs CEM - Build Script

echo ============================================
echo   MOGLabs CEM - Windows Build Script
echo ============================================
echo.

:: Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [OK] Found Python %PYVER%

:: Check Python version is 3.8+
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>nul
if errorlevel 1 (
    echo [ERROR] Python 3.8 or higher is required. Found %PYVER%.
    pause
    exit /b 1
)

echo.
echo [1/3] Installing dependencies...
pip install -r requirements-windows.txt
if errorlevel 1 (
    echo [WARN] Some dependencies may have failed. Trying PySide6 fallback...
    pip install PySide6 numpy scipy matplotlib pyqtgraph pyserial psutil pyinstaller
)

echo.
echo [2/3] Building executable with PyInstaller...
pyinstaller CEM.spec --noconfirm
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Build complete!
echo.
echo ============================================
echo   Output: dist\CEM\CEM.exe
echo ============================================
echo.
echo You can run dist\CEM\CEM.exe directly,
echo or create an installer with Inno Setup using installer.iss
echo.
pause
