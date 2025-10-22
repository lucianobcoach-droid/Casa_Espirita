@echo off
setlocal
cd /d "%~dp0"

for /f "delims=" %%t in ('git tag --list --sort=-creatordate') do (
  set LAST_TAG=%%t
  goto :found
)

:found
if not defined LAST_TAG (
  echo [ERRO] Nenhuma tag encontrada.
  exit /b 1
)

set REC_BRANCH=recovery-%LAST_TAG%
echo Criando branch de recuperacao: %REC_BRANCH% a partir de %LAST_TAG%
git fetch --all --tags
git checkout -b %REC_BRANCH% %LAST_TAG% || (echo [ERRO] Falha ao criar branch de recuperacao. & exit /b 1)
echo [OK] Branche %REC_BRANCH% criada a partir de %LAST_TAG%.
endlocal
