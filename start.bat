@echo off
setlocal
chcp 65001 >nul
echo ========================================
echo   Starting Frontend and Backend
echo ========================================
echo.

REM Check directories
if not exist "backend" (
    echo [ERROR] backend directory not found
    pause
    exit /b 1
)

if not exist "frontend" (
    echo [ERROR] frontend directory not found
    pause
    exit /b 1
)

REM Check and install frontend dependencies
echo [0/3] Checking frontend dependencies...
if not exist "frontend\node_modules" (
    echo Frontend dependencies not found, installing...
    cd frontend
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install frontend dependencies
        cd ..
        pause
        exit /b 1
    )
    cd ..
    echo Frontend dependencies installed successfully!
) else (
    echo Frontend dependencies already installed.
)
echo.

REM Check backend virtual environment
if not exist "backend\venv\Scripts\python.exe" (
    echo [ERROR] backend virtual environment not found.
    echo Please run install.bat first.
    pause
    exit /b 1
)

REM Start backend
echo [1/3] Starting backend service...
cd backend
start "Backend-FastAPI" cmd /k "venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
cd ..
timeout /t 3 >nul

REM Start frontend
echo [2/3] Starting frontend service...
cd frontend
start "Frontend-Vite" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo   Services Started!
echo ========================================
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.

REM Send notification
echo [3/3] Sending notification...
powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $notify = New-Object System.Windows.Forms.NotifyIcon; $notify.Icon = [System.Drawing.SystemIcons]::Information; $notify.Visible = $true; $notify.ShowBalloonTip(5000, 'Task Completed', 'Frontend and Backend services started successfully!', [System.Windows.Forms.ToolTipIcon]::Info); Start-Sleep -Seconds 6; $notify.Dispose()"

echo Press any key to close...
pause >nul
