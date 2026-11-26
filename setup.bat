@echo off
cd /d "%~dp0"
echo Installing Python and FFmpeg if needed...
where winget >nul 2>&1
if %errorlevel% equ 0 (
 winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements
 winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
)
echo Installing optional Edge TTS package...
py -3 -m pip install --upgrade edge-tts
if errorlevel 1 echo Could not install edge-tts. Confirm Python and Internet connectivity then retry.
echo Restart terminal before running START.bat.
pause
