# Rotina Git/GitHub — Casa Espírita

## Objetivo

Definir a rotina oficial para conferir e sincronizar a pasta local do projeto com o GitHub, evitando perda de contexto e divergencia entre a maquina local e a memoria compartilhada do projeto.

## Regra principal

O GitHub remoto, na branch `feat/reinicio-financeiro`, e a memoria oficial compartilhada do projeto.

Uma etapa so deve ser considerada oficialmente consolidada quando estiver:

1. implementada ou documentada localmente;
2. commitada no Git local;
3. enviada ao GitHub por push.

Commit local sem push e apenas avanco local temporario.

## Pasta local, commit local e push

- Pasta local: arquivos atuais na maquina de trabalho.
- Commit local: registro no Git da maquina local, ainda podendo nao existir no GitHub.
- Push para GitHub: envio dos commits locais para o repositorio remoto, tornando a etapa parte da memoria compartilhada.

## Quando o usuario pode fazer push pelo PowerShell

O usuario pode fazer push direto quando todos os criterios abaixo forem verdadeiros:

- branch atual igual a `feat/reinicio-financeiro`;
- `git status --short` sem saida;
- existe commit local pendente para enviar;
- nao existe commit remoto pendente;
- nao ha conflito, divergencia ou erro no `fetch`.

## Quando o usuario nao deve fazer push sozinho

Nao fazer push sozinho se aparecer qualquer um destes casos:

- arquivo modificado;
- arquivo nao rastreado;
- commit remoto pendente;
- erro no `git fetch origin`;
- branch diferente de `feat/reinicio-financeiro`;
- conflito;
- duvida sobre o resultado dos comandos.

Nesses casos, trazer o resultado para analise antes de qualquer push, pull ou merge.

## Comandos PowerShell seguros

```powershell
cd "C:\Users\lucia\OneDrive\Área de Trabalho\Casa_Espirita"

git branch --show-current

git status --short

git fetch origin

git log --oneline origin/feat/reinicio-financeiro..HEAD

git log --oneline HEAD..origin/feat/reinicio-financeiro

git push origin feat/reinicio-financeiro

git status --short

git log --oneline -1
```

## Criterio para push seguro

O push e seguro quando:

- a branch atual e `feat/reinicio-financeiro`;
- `git status --short` nao mostra nada;
- ha commit local pendente em `origin/feat/reinicio-financeiro..HEAD`;
- nao ha commit remoto pendente em `HEAD..origin/feat/reinicio-financeiro`;
- nao ha conflito, divergencia ou erro.

## Criterio para parar e pedir analise

Parar e pedir analise se houver:

- qualquer arquivo modificado;
- qualquer arquivo nao rastreado;
- commit remoto pendente;
- erro no fetch;
- branch diferente;
- conflito;
- duvida sobre o resultado.
