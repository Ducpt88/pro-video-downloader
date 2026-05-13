@echo off
chcp 65001 >nul
title DANG DONG GOI APP PRO VIDEO DOWNLOADER 1.9...
cd /d "%~dp0"
echo.
echo ============================================================
echo   BUOC 1: Fix loi PyInstaller (setuptools)
echo ============================================================
pip install setuptools==70.0.0 --quiet
pip install --upgrade pyinstaller --quiet
echo.

echo ============================================================
echo   BUOC 2: Tao Icon
echo ============================================================
python generate_icon.py
echo.

echo ============================================================
echo   BUOC 3: Dong goi thanh file .EXE
echo ============================================================
pyinstaller --noconfirm --onefile --windowed --icon=icon.ico --name="Pro Video Downloader" --add-data "donors.json;." --add-data "coffee.png;." --add-data "real_qr.png;." --add-data "icon.ico;." app.py
echo.

if exist "dist\Pro Video Downloader.exe" (
    echo ============================================================
    echo   THANH CONG! File EXE da san sang trong thu muc dist
    echo ============================================================
    echo.
    echo   Dang mo App cho ban...
    start "" "dist\Pro Video Downloader.exe"
) else (
    echo ============================================================
    echo   THAT BAI! Dang mo ban code truc tiep...
    echo ============================================================
    start "" pythonw app.py
)
echo.
pause
