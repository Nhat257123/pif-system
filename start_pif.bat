@echo off
cd /d "%~dp0"
title PIF SYSTEM STARTUP

echo.
echo ======================================================
echo             PIF SYSTEM STARTUP (ASCII)
echo ======================================================
echo.

:: Get Local IP using ping method (highly reliable on Windows)
for /f "delims=[] tokens=2" %%a in ('ping -4 -n 1 %computername% ^| findstr [') do set MY_IP=%%a

echo YOUR LOCAL IP ADDRESS: %MY_IP%
echo.
echo 1. Access from this computer: http://localhost:8501
echo 2. Access from other devices : http://%MY_IP%:8501
echo.
echo ======================================================
echo Starting server...
echo.

python -m streamlit run app.py --server.port 8501
pause
