# CODEX_RESULTADO

Data: 2026-03-23

## Entrega realizada

Foi executada a etapa incremental do extrato por conta com filtro por período e cálculo de saldo anterior, sem alterar o domínio além do necessário.

Complemento incremental posterior:

- saldo real das contas passou a considerar apenas lançamentos quitados
- o extrato por conta passou a listar apenas lançamentos quitados
- o saldo anterior do extrato por período passou a considerar apenas lançamentos quitados anteriores ao período

## Filtro por período

O extrato agora aceita por GET:

- `data_inicial`
- `data_final`

Sem filtro:

- mantém o extrato completo
- começa em `saldo_inicial`

Com filtro:

- lista apenas lançamentos do período
- calcula `saldo_anterior` até o dia anterior ao início informado
- inicia o saldo acumulado do período a partir desse valor

## Regra do saldo anterior

O `saldo_anterior` é calculado assim:

- começa em `saldo_inicial`
- soma receitas anteriores
- subtrai despesas anteriores
- subtrai transferências em que a conta é origem
- soma transferências em que a conta é destino

## Arquivos alterados nesta etapa

- `financeiro/views.py`
- `financeiro/templates/financeiro/conta_extrato.html`
- `docs/CEREBRO_PROJETO.md`
- `docs/STATE.md`
- `docs/CODEX_RESULTADO.md`

## Resultado prático

- o extrato continua funcionando sem filtro
- o extrato aceita filtro por período
- o saldo anterior aparece quando há `data_inicial`
- o saldo acumulado do período parte corretamente do saldo anterior
- transferências continuam coerentes na conta de origem e na conta de destino
- lançamentos não quitados deixaram de afetar saldo real e extrato
