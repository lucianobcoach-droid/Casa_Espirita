@echo off
setlocal

REM Mostra status rapido do repo + tags + branch atual + ultimos commits
cd /d "%~dp0"
echo ====== BRANCH ATUAL ======
git rev-parse --abbrev-ref HEAD

echo.
echo ====== STATUS ======
git status -sb

echo.
echo ====== ULTIMOS COMMITS (main) ======
git log main --oneline -n 5

echo.
echo ====== ULTIMOS COMMITS (branch atual) ======
git log --oneline -n 5

echo.
echo ====== TAGS ======
git tag --list --sort=-creatordate | head -n 10

echo.
echo ====== BACKUPS DO DB ======
dir /od backups\db.backup.*.sqlite3 2>NUL

endlocal
