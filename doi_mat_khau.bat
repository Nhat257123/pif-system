@echo off
chcp 65001 > nul
echo ════════════════════════════════════════════════
echo        CONG CU TAO HASH MAT KHAU – PIF SYSTEM
echo ════════════════════════════════════════════════
echo.
echo Dung cu nay giup ban tao hash SHA-256 cho mat khau moi.
echo Sau do copy hash vao phan AUTHORIZED_USERS trong app.py.
echo.

set /p USERNAME=Nhap ten dang nhap: 
set /p PASSWORD=Nhap mat khau moi: 

python -c "import hashlib; print('\nTen dang nhap:', '%USERNAME%'); print('Hash SHA-256  :', hashlib.sha256('%PASSWORD%'.encode()).hexdigest()); print('\nCopy dong sau vao AUTHORIZED_USERS trong app.py:'); print('  \"%USERNAME%\": \"' + hashlib.sha256('%PASSWORD%'.encode()).hexdigest() + '\",')"

echo.
pause
