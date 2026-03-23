# CODEX_RESULTADO

Data: 2026-03-23

## Entrega realizada

Foi executada a etapa incremental de consistência de contas: `data_saldo_inicial` tornou-se obrigatória e a listagem de contas passou a exibir `saldo_atual` calculado, sem persistir esse valor no banco.

## Verificação prévia obrigatória

Antes da implementação, foi conferido o banco local.

Resultado:

- não havia mais contas com `data_saldo_inicial` nula

## Migration criada

- `financeiro/migrations/0003_contafinanceira_data_saldo_inicial_required.py`

## Arquivos alterados nesta etapa

- `financeiro/models.py`
- `financeiro/views.py`
- `financeiro/templates/financeiro/conta_list.html`
- `financeiro/templates/financeiro/conta_extrato.html`
- `financeiro/migrations/0003_contafinanceira_data_saldo_inicial_required.py`
- `docs/CEREBRO_PROJETO.md`
- `docs/STATE.md`
- `docs/CODEX_RESULTADO.md`

## Regra do saldo_atual

O `saldo_atual` é calculado em tempo de execução:

- começa em `saldo_inicial`
- soma receitas da conta
- subtrai despesas da conta
- subtrai transferências em que a conta é origem
- soma transferências em que a conta é destino

Não foi criado campo novo para `saldo_atual`.

## Onde o saldo_atual aparece

- na listagem de contas
- no topo do extrato da conta, como referência visual do saldo final acumulado

## Restrições respeitadas

- sem alterações no app `biblioteca`
- sem uso de `signals`
- sem salvar `saldo_atual` no banco
- sem criar campo novo para `saldo_atual`
- sem criar relatórios gerais
- sem alteração de migrations antigas
- mudança mínima e incremental

## Resultado prático

- `data_saldo_inicial` agora é obrigatória
- a listagem de contas ficou mais útil com `saldo_atual` calculado
- transferências entram corretamente no cálculo
- o restante do domínio financeiro permaneceu intacto
