@echo off
title Dang Build App Pro Video Downloader...
cd /d "%~dp0"
echo ⚡ Dang don dep ban cu...
if exist dist rd /s /q dist
if exist build rd /s /q build
echo.
echo ⚡ Dang tao Icon moi...
python generate_icon.py
echo.
echo ⚡ Dang Build file EXE (Vui long doi trong giay lat)...
pyinstaller Pro_VideoDownloader_HoangDuc.spec
echo.
echo ✅ XONG! Ban vao thu muc 'dist' de lay file 'Pro Video Downloader.exe' nhe.
echo.
pause
