@echo off
echo ========================================
echo Blissful - Lidarr Music Downloader
echo ========================================
echo.

REM Ask if user wants to run tests first
set /p RUNTEST="Run setup tests first? (y/n): "

if /i "%RUNTEST%"=="y" (
    echo.
    echo Running setup tests...
    echo ========================================
    python extend\test_setup.py
    
    if %errorlevel% neq 0 (
        echo.
        echo Setup tests failed! Please fix issues before starting.
        pause
        exit /b 1
    )
    
    echo.
    echo All tests passed!
    echo.
)

echo.
echo Prerequisites Check:
echo ==================

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
) else (
    echo [OK] Python found
)

REM Check FFmpeg
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] FFmpeg not found! Some features may not work.
    echo     Download from: https://ffmpeg.org/download.html
) else (
    echo [OK] FFmpeg found
)

echo.
echo Installing/Updating dependencies...
pip install -r requirements.txt

echo.
echo ==================
echo Starting Blissful Microservice...
echo.
echo Web Interface: http://localhost:7373
echo.
echo To test the API (in another terminal):
echo   python extend\test_api.py
echo.
echo Press Ctrl+C to stop the service
echo ==================
echo.

python Blissful.py

pause
