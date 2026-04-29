# Script to run the Video Downloader without console
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
cd $scriptPath

# Kiểm tra thư viện ngầm
pip install -r requirements.txt --quiet

# Chạy bằng pythonw (không hiện cửa sổ đen)
start-process pythonw.exe "app.py"
