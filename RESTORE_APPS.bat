@echo off
title DANG KHOI PHUC CAC BAN EXE TRONG DIST...
cd /d "%~dp0"
echo.
echo ============================================================
echo   ⚡ DANG KHOI PHUC LAI 2 BAN APP CHO BAN...
echo ============================================================
echo.

echo 1. Dang tao Icon...
python generate_icon.py
echo.

echo 2. Dang build ban: Pro_VideoDownloader_HoangDuc.exe...
pyinstaller --name="Pro_VideoDownloader_HoangDuc" --onefile --windowed --icon="icon.ico" --add-data "donors.json;." --add-data "coffee.png;." --add-data "real_qr.png;." app.py

echo.
echo 3. Dang build ban: DGMedia_TeamDownloader.exe...
pyinstaller --name="DGMedia_TeamDownloader" --onefile --windowed --icon="icon.ico" --add-data "donors.json;." --add-data "coffee.png;." --add-data "real_qr.png;." app.py

echo.
echo ============================================================
echo   ✅ DA KHOI PHUC XONG! BAN VAO THU MUC 'dist' KIEM TRA NHE.
echo ============================================================
echo.
pause
