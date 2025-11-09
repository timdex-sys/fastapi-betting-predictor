@echo off
echo ================================
echo Updating GitHub repository...
echo ================================

:: Step 1: Check Git status
git status

:: Step 2: Stage all changes
git add .

:: Step 3: Commit changes with message
set /p commitmsg=Enter commit message: 
if "%commitmsg%"=="" set commitmsg=Update project files
git commit -m "%commitmsg%"

:: Step 4: Pull latest changes with rebase
echo Pulling latest changes from remote...
git pull origin main --rebase

:: Step 5: Check if rebase paused due to conflicts
if %errorlevel% neq 0 (
    echo.
    echo Rebase may have conflicts. Please resolve them manually, then run:
    echo git add <file>
    echo git rebase --continue
    pause
    exit /b
)

:: Step 6: Push changes to GitHub
git push origin main

echo.
echo ================================
echo Repository updated successfully!
echo ================================
pause
