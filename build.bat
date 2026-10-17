@echo off
REM ==========================================================
REM  CyrusCover - build a single-file Windows executable
REM  Output: exe\CyrusCover.exe
REM ==========================================================
setlocal
cd /d "%~dp0"

echo [1/3] Installing requirements...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt pyinstaller || goto :error

echo [2/3] Building CyrusCover.exe ...
python -m PyInstaller --noconfirm --clean --onefile --noconsole ^
    --name CyrusCover ^
    --icon "assets\cyruscover.ico" ^
    --hidden-import ddgs ^
    --distpath exe ^
    --workpath build ^
    --specpath build ^
    CyrusCover.pyw || goto :error

echo [3/3] Cleaning up...
rmdir /s /q build 2>nul

echo.
echo Done: %~dp0exe\CyrusCover.exe
pause
exit /b 0

:error
echo.
echo Build failed. See the messages above.
pause
exit /b 1
