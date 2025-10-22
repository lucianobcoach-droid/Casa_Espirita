@echo off
setlocal enabledelayedexpansion
REM ==========================================================
REM  prepare_codex_run.bat
REM  - Cria checkpoint (tag) com data/hora
REM  - Faz backup do banco (db.sqlite3)
REM  - Garante a branch de experimento ui-colorlib-experimento
REM  - Faz push da branch e das tags
REM ==========================================================

REM 0) Verificações básicas
where git >NUL 2>&1 || (echo [ERRO] Git nao encontrado no PATH. Instale o Git e tente novamente. & exit /b 1)

REM 1) Ir para a pasta do script (raiz do repo)
cd /d "%~dp0"

REM 2) Nome da branch de trabalho
set WORK_BRANCH=ui-colorlib-experimento

REM 3) Gerar timestamp seguro (yyyy-MM-dd_HH-mm)
for /f %%i in ('powershell -NoProfile -Command "(Get-Date).ToString(\"yyyy-MM-dd_HH-mm\")"') do set NOW=%%i
set TAG_NAME=cp-%NOW%

echo.
echo ====== Atualizando a main ======
git checkout main || (echo [ERRO] Nao foi possivel trocar para a branch main. & exit /b 1)
git pull origin main || (echo [ERRO] Falha ao atualizar a main do remoto. & exit /b 1)

REM 4) Backup do banco
echo.
echo ====== Backup do banco ======
if not exist "backups" mkdir backups
if exist "db.sqlite3" (
  copy /Y "db.sqlite3" "backups\db.backup.%NOW%.sqlite3" >NUL && (
    echo [OK] Backup criado em backups\db.backup.%NOW%.sqlite3
  ) || (
    echo [ALERTA] Nao foi possivel criar backup do banco.
  )
) else (
  echo [INFO] db.sqlite3 nao encontrado. Pulando backup.
)

REM 5) Garantir working tree limpa (apenas alerta)
echo.
echo ====== Conferindo mudancas locais ======
git status --porcelain
if not errorlevel 1 (
  for /f "delims=" %%s in ('git status --porcelain') do set HAVE_CHANGES=1
)
if defined HAVE_CHANGES (
  echo [ALERTA] Existem alteracoes nao commitadas acima. Se for intencional, prossiga com cuidado.
) else (
  echo [OK] Working tree limpa.
)

REM 6) Criar checkpoint (tag) e enviar
echo.
echo ====== Criando checkpoint (tag %TAG_NAME%) ======
git tag -a %TAG_NAME% -m "Checkpoint antes de alterações via Codex" || (echo [ERRO] Falha ao criar tag. & exit /b 1)
git push origin main --tags || (echo [ERRO] Falha ao enviar tags para o remoto. & exit /b 1)
echo [OK] Tag %TAG_NAME% criada e enviada.

REM 7) Criar/alternar para a branch de experimento
echo.
echo ====== Preparando branch de experimento: %WORK_BRANCH% ======
git rev-parse --verify %WORK_BRANCH% >NUL 2>&1
if %errorlevel%==0 (
  git checkout %WORK_BRANCH% || (echo [ERRO] Falha ao trocar para a branch %WORK_BRANCH%. & exit /b 1)
  git pull origin %WORK_BRANCH% || echo [INFO] Branch existe, mas nao foi possivel atualiza-la do remoto.
) else (
  git checkout -b %WORK_BRANCH% || (echo [ERRO] Falha ao criar a branch %WORK_BRANCH%. & exit /b 1)
)

REM 8) Subir branch (se ainda nao tiver upstream)
git rev-parse --abbrev-ref --symbolic-full-name @{u} >NUL 2>&1
if not %errorlevel%==0 (
  git push -u origin %WORK_BRANCH% || (echo [ERRO] Falha ao enviar branch %WORK_BRANCH% ao remoto. & exit /b 1)
)

echo.
echo ==========================================================
echo  PRONTO!
echo  - Checkpoint (tag): %TAG_NAME%
echo  - Branch de trabalho: %WORK_BRANCH%
echo  Agora voce pode abrir o Codex e colar os prompts.
echo  Lembre-se: peça para TRABALHAR SOMENTE NA BRANCH %WORK_BRANCH% e abrir PR para main.
echo ==========================================================
endlocal
