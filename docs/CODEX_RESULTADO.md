# CODEX_RESULTADO

Data: 2026-03-23

## Entrega realizada

Foi executada somente a ETAPA 2 aprovada do financeiro: criação do extrato por conta com saldo acumulado, sem criar relatórios gerais e sem ampliar o domínio além do necessário.

## Rota criada

- `/financeiro/contas/<id>/extrato/`

## View criada

- `ContaFinanceiraExtratoView`

## Template criado

- `financeiro/templates/financeiro/conta_extrato.html`

## Regra de saldo acumulado

O extrato segue esta lógica:

- começa em `saldo_inicial` da conta
- `receita` entra como entrada
- `despesa` entra como saída
- `transferencia` sai da conta de origem
- `transferencia` entra na conta de destino

O saldo acumulado é calculado em ordem cronológica por:

- `data_competencia`
- `criado_em`
- `pk`

## Arquivos alterados nesta etapa

- `financeiro/views.py`
- `financeiro/urls.py`
- `financeiro/templates/financeiro/conta_list.html`
- `financeiro/templates/financeiro/conta_extrato.html`
- `docs/STATE.md`
- `docs/CODEX_RESULTADO.md`

## Ajustes de interface

- a listagem de contas passou a ter a ação `Extrato`
- o extrato mostra data, descrição, tipo, entrada, saída, saldo acumulado e observações
- a tela deixa explícita a regra das transferências

## Restrições respeitadas

- sem alterações no app `biblioteca`
- sem uso de `signals`
- sem alteração do domínio além do necessário para leitura do extrato
- sem criação de relatórios gerais
- sem mistura com outras melhorias
- mudança mínima e incremental

## Resultado prático

- o extrato por conta abre em rota própria
- o saldo acumulado parte do saldo inicial cadastrado
- receitas, despesas e transferências passam a ser lidas de forma coerente na conta selecionada
- o restante do domínio financeiro permaneceu intacto
