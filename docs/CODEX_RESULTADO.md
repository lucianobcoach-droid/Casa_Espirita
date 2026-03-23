# CODEX_RESULTADO

Data: 2026-03-23

## Entrega realizada

Foi executada somente a ETAPA 1 aprovada do financeiro: inclusão de saldo inicial em `ContaFinanceira`, sem iniciar extrato, sem ampliar o domínio além do necessário e sem alterar outras regras aprovadas.

## Alteração de domínio desta etapa

`ContaFinanceira` passou a ter:

- `saldo_inicial`
- `data_saldo_inicial`

Escopo funcional:

- o saldo inicial é apenas dado cadastral
- não existe extrato
- não existe cálculo de saldo por movimentação nesta etapa
- nenhum outro model foi alterado

## Migration criada

- `financeiro/migrations/0002_contafinanceira_saldo_inicial.py`

## Arquivos alterados nesta etapa

- `financeiro/models.py`
- `financeiro/forms.py`
- `financeiro/templates/financeiro/conta_list.html`
- `financeiro/migrations/0002_contafinanceira_saldo_inicial.py`
- `docs/STATE.md`
- `docs/CODEX_RESULTADO.md`

## Ajustes de interface

- o formulário de conta passou a aceitar `saldo_inicial`
- o formulário de conta passou a aceitar `data_saldo_inicial`
- a listagem de contas passou a mostrar saldo inicial e, quando existir, a data de referência

## Restrições respeitadas

- sem alterações no app `biblioteca`
- sem uso de `signals`
- sem alteração de outros models além de `ContaFinanceira`
- sem alteração de migrations antigas
- sem criação de extrato
- sem mistura com etapa 2
- mudança mínima e incremental

## Resultado prático

- `ContaFinanceira` agora aceita saldo inicial e data de saldo inicial
- a migration incremental nova foi adicionada
- as telas de conta ficaram compatíveis com a nova informação
- o restante do domínio financeiro permaneceu intacto
