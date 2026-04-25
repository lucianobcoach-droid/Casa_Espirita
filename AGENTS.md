# AGENTS.md — Projeto Casa Espírita

## Papel do Codex

O Codex é executor técnico. Ele não deve redefinir regras de negócio, arquitetura ou prioridades sem autorização expressa.

## Fonte de verdade

Antes de qualquer alteração relevante, consultar os documentos em docs/.

## Regras obrigatórias

- Trabalhar sempre por microetapas.
- Não fazer refatorações amplas sem autorização.
- Não alterar cálculos financeiros sem pedido explícito.
- Não apagar histórico dos documentos base.
- Atualizar docs/STATE.md e docs/CODEX_RESULTADO.md ao final de cada etapa.
- Atualizar docs/CEREBRO_PROJETO.md somente quando houver decisão permanente.
- Ao finalizar, informar arquivos alterados, validações feitas e pendências.

## Uso de skills

Quando a tarefa envolver documentação, financeiro, relatórios/impressão, UX ou importação, consultar a skill correspondente em .agents/skills/.
