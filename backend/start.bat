@echo off
REM Start PySpark Ride-Sharing Matchmaking Backend
REM Windows PowerShell Script

echo ========================================
echo PySpark Backend Startup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [INFO] Python found: 
python --version
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [SUCCESS] Virtual environment created
    echo.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install/Update dependencies
echo [INFO] Installing dependencies from requirements.txt...
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo [SUCCESS] Dependencies installed
echo.

REM Set Java home for PySpark (if needed)
REM Uncomment and set JAVA_HOME if you have Java installed
REM set JAVA_HOME=C:\Program Files\Java\jdk-11.0.12
REM set PATH=%JAVA_HOME%\bin;%PATH%

REM Start Flask server
echo ========================================
echo Starting Flask Server with PySpark Backend...
echo ========================================
echo.
echo Server will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

REM Deactivate virtual environment on exit
deactivate
pause
