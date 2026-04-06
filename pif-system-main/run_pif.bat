@echo off
chcp 65001 > nul
cd /d "%~dp0"

title HE THONG HO SO DU LIEU PIF v2.2 Secured

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║       HE THONG HO SO DU LIEU PIF  (v2.2 Secured)   ║
echo ║                  R^&D Team © 2026                    ║
echo ╚══════════════════════════════════════════════════════╝
echo.

:: Check Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] Khong tim thay Python. Vui long cai Python 3.10+ va thu lai.
    echo Vui long truy cap https://www.python.org/downloads/ de tai ve.
    echo QUAN TRONG: Nho tich chon "Add Python to PATH" khi cai dat.
    pause
    exit /b 1
)

echo [1/3] Kiem tra va cap nhat thu vien (co the mat vai phut lan dau)...
python -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [LOI] Khong the cai dat thu vien. Kiem tra ket noi mang!
    pause
    exit /b 1
)

echo [2/3] Thu vien da san sang.
echo.

:: Check port 8501
netstat -an | find "8501" | find "LISTENING" > nul 2>&1
if %errorlevel% == 0 (
    echo [CANH BAO] Port 8501 dang duoc su dung boi tien trinh khac.
    echo            Streamlit se tu dong chon port khac.
    echo.
)

:: Get Local IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /i "192.168"') do set IP=%%a
set IP=%IP: =%

echo [3/3] Dang khoi dong ung dung...
echo.
echo ► Truy cap tai may nay : http://localhost:8501
if not "%IP%"=="" (
    echo ► Truy cap tu may khac: http://%IP%:8501
)
echo.
echo ► Tai khoan mac dinh:
echo     Quan tri vien : admin   / admin123
echo     Nguoi dung RD  : rd_user / rd2026
echo.
echo [QUAN TRONG] Doi mat khau sau khi dang nhap lan dau!
echo              Neu may khac khong vao duoc, hay kiem tra Firewall.
echo.
echo Nhan Ctrl+C de dung ung dung.
echo ════════════════════════════════════════════════════════
echo.

python -m streamlit run app.py --server.port 8501
if %errorlevel% neq 0 (
    echo.
    echo [LOI] Ung dung bi ngat. Xem log o tren de biet ly do.
    pause
)
pause
