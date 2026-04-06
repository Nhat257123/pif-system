@echo off
chcp 65001 > nul
cd /d "%~dp0"

:: Tạo timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%
set BACKUP_NAME=PIF_CodeBackup_%TIMESTAMP%.zip

echo ════════════════════════════════════════════════
echo   SAO LUU MA NGUON HE THONG PIF (Khong data)
echo ════════════════════════════════════════════════
echo.
echo Dang tao: %BACKUP_NAME%
echo CHU Y: Chi backup code + template, KHONG backup
echo        file Excel (cong thuc san pham, DB NL).
echo.

:: Chỉ backup code và template, bỏ qua dữ liệu nhạy cảm
powershell -Command ^
  "$exclude = @('*.xlsx','*.log','*.json','__pycache__','*.pyc','pif_audit.log'); ^
   $files = Get-ChildItem -Path '.' -Recurse | Where-Object { ^
     $f = $_; -not ($exclude | Where-Object { $f.Name -like $_ }) ^
   }; ^
   Compress-Archive -Path ($files.FullName) -DestinationPath '..\%BACKUP_NAME%' -Force"

if %errorlevel% == 0 (
    echo.
    echo [OK] Sao luu thanh cong!
    echo      File: ..\%BACKUP_NAME%
    echo.
    echo [NHAC NHO] File .xlsx chua cong thuc va DB nguyen lieu
    echo           KHONG duoc backup o day. Hay backup rieng
    echo           vao o cung ma hoa hoac he thong luu tru noi bo.
) else (
    echo [LOI] Sao luu that bai. Kiem tra quyen truy cap thu muc.
)
echo.
pause
