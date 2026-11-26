@echo off
cd /d "%~dp0"
py -3 server.py
if errorlevel 1 echo App stopped. Review error details above.
pause
