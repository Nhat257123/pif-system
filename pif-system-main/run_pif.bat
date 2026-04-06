@echo off
chcp 65001 > nul
cd /d "%~dp0"

title HE THONG HO SO DU LIEU PIF v2.3 Portable
set "VENV_DIR=.venv"

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║       HE THONG HO SO DU LIEU PIF (v2.3 Portable)   ║
echo ║                  R^&D Team © 2026                    ║
echo ╚══════════════════════════════════════════════════════╝
echo.

:: 1. Kiem tra Python (Ho tro ca python va python3)
set "PY_CMD=python"
python --version > nul 2>&1
if %errorlevel% neq 0 (
    python3 --version > nul 2>&1
    if %errorlevel% == 0 (
        set "PY_CMD=python3"
    ) else (
        echo [LOI] Khong tim thay Python trong he thong.
        echo Vui long truy cap https://www.python.org/ de tai va cai dat.
        echo QUAN TRONG: Nho tich chon "Add Python to PATH" khi cai dat.
        pause
        exit /b 1
    )
)

:: 2. Check/Create Virtual Environment
if not exist "%VENV_DIR%" (
    echo [1/3] Dang tao moi truong ao (.venv)... co the mat 1-2 phut...
    %PY_CMD% -m venv %VENV_DIR%
    if %errorlevel% neq 0 (
        echo [LOI] Khong the tao moi truong ao.
        pause
        exit /b 1
    )
)

:: 3. Activate VENV and Install Requirements
echo [2/3] Dang kich hoat moi truong va kiem tra thu vien...
call %VENV_DIR%\Scripts\activate

:: Check internet connection before pip install
ping -n 1 google.com > nul 2>&1
if %errorlevel% == 0 (
    echo       Dang cap nhat thu vien tu Internet...
    python -m pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
) else (
    echo       [CANH BAO] Khong co Internet. Se dung thu vien da co.
)

:: 4. Start Application
echo.
echo [3/3] Dang khoi dong ung dung...
echo.

:: Get Local IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /i "192.168"') do set "IP=%%a"
set "IP=%IP: =%"

echo ► May chu dang chay tai: http://localhost:8501
if not "%IP%"=="" (
    echo ► Truy cap tu thiet bi khac: http://%IP%:8501
)
echo.
echo [TU DONG] Se mo trinh duyet sau 3 giay...
echo.

:: Start browser
start /b cmd /c "timeout /t 3 > nul && start http://localhost:8501"

:: Run Streamlit
streamlit run app.py --server.port 8501 --server.headless false

if %errorlevel% neq 0 (
    echo.
    echo [LOI] Ung dung bi dung dot ngot.
    pause
)
pause
