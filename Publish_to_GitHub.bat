@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title PDF Compressor - GitHub publisher

echo ==============================================
echo PDF Compressor 2.6 - Publish to GitHub
echo ==============================================
echo.
echo [1] Create an EMPTY repository at https://github.com/new

echo [2] Install Git for Windows if it is not installed.
echo [3] Paste the HTTPS URL of your new repository below.
echo.
where git >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Git for Windows not found.
  echo Please install Git from https://git-scm.com/download/win
  pause
  exit /b 1
)
set /p "REPO=Repository URL (https://github.com/USER/pdf-compressor.git): "
if "%REPO%"=="" (
  echo [ERROR] No repository URL supplied.
  pause
  exit /b 1
)
set "CHECK=%REPO:~0,19%"
if /I not "%CHECK%"=="https://github.com/" (
  echo [ERROR] Use an HTTPS GitHub repository URL.
  pause
  exit /b 1
)
if not exist ".git" (
  git init
  if errorlevel 1 goto :fail
)
git add .
if errorlevel 1 goto :fail
git diff --cached --quiet
if errorlevel 1 (
  git commit -m "Initial release: PDF Compressor 2.6"
  if errorlevel 1 (
    echo.
    echo [ERROR] The commit failed. Configure your Git identity:
    echo git config --global user.name "Your Name"
    echo git config --global user.email "you@example.com"
    echo Then run this file again.
    pause
    exit /b 1
  )
)
git branch -M main
if errorlevel 1 goto :fail
git remote get-url origin >nul 2>nul
if errorlevel 1 (
  git remote add origin "%REPO%"
) else (
  git remote set-url origin "%REPO%"
)
if errorlevel 1 goto :fail

echo.
echo Uploading... Git may open a browser window to sign in.
git push -u origin main
if errorlevel 1 goto :fail

echo.
echo [OK] Repository uploaded.
echo Open: %REPO%
pause
exit /b 0
:fail
echo.
echo [ERROR] Publish failed. Check the error above and try again.
pause
exit /b 1
