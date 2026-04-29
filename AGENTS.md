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
- Ao finalizar, informar claramente se houve commit e se houve push.
- Commit local sem push não encerra oficialmente uma etapa; deve ser tratado como pendência de sincronização antes de nova microetapa.

## Uso de skills

Quando a tarefa envolver documentação, financeiro, relatórios/impressão, UX ou importação, consultar a skill correspondente em .agents/skills/.

## Formato obrigatório de retorno

Ao finalizar qualquer tarefa, o Codex deve responder de forma curta e estruturada:

1. Resumo objetivo da execução
2. Arquivos consultados
3. Arquivos alterados
4. O que foi alterado em cada arquivo
5. Validações executadas
6. Resultado de git status --short
7. Pendências ou riscos
8. Commit/push realizado? sim/não

Regras de economia de tokens:

- Não colar diff completo, salvo se houver erro.
- Não repetir documentação longa.
- Não explicar histórico já registrado nos documentos.
- Não devolver análise extensa quando a tarefa for objetiva.
- Se houver erro, trazer o erro completo.
