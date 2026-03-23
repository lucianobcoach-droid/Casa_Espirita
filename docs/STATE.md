# STATE

Data de atualização: 2026-03-23

## Estado atual do módulo financeiro

- O app `financeiro` foi criado e adicionado ao `INSTALLED_APPS`.
- A modelagem de domínio, os relacionamentos e o registro no Django admin permanecem intactos, com exceção da evolução incremental já aprovada em `ContaFinanceira`.
- O módulo já possui base operacional própria fora do admin.
- Existem formulários, views, rotas e templates próprios para contas, centros de custo, pessoas, categorias e lançamentos.
- O módulo possui cadastro, listagem, edição, exclusão com confirmação, filtros básicos, autocomplete real no formulário de lançamento e extrato por conta.
- O extrato por conta já aceita filtro por período via GET e cálculo de saldo anterior.
- O saldo real das contas e o extrato agora consideram apenas lançamentos quitados.
- O app `biblioteca` não foi alterado.
- Não foram usados `signals`.

## ContaFinanceira

`ContaFinanceira` possui:

- `saldo_inicial`
- `data_saldo_inicial` obrigatória

Leitura funcional:

- o saldo inicial é dado cadastral
- `saldo_atual` é calculado em tempo de execução
- `saldo_atual` não é salvo no banco
- apenas lançamentos com status `quitado` afetam `saldo_atual`

## Extrato por conta

Existe visualização de extrato por conta em rota própria:

- `/financeiro/contas/<id>/extrato/`

Escopo funcional:

- sem filtro: extrato completo desde o saldo inicial
- com filtro: lançamentos apenas do período
- com `data_inicial`: cálculo de `saldo_anterior`
- saldo acumulado do período começa a partir de `saldo_anterior`
- somente lançamentos quitados aparecem no extrato
- não existe relatório geral nesta etapa

## Regra de saldo no extrato

Sem filtro:

- começa do `saldo_inicial`
- soma receitas
- subtrai despesas
- subtrai transferências da conta de origem
- soma transferências da conta de destino
- considera apenas lançamentos quitados

Com filtro por período:

- `saldo_anterior` começa em `saldo_inicial`
- soma e subtrai movimentações anteriores à `data_inicial`
- o período listado usa apenas lançamentos entre `data_inicial` e `data_final`
- o saldo acumulado das linhas do período começa de `saldo_anterior`
- o saldo anterior também considera apenas lançamentos quitados

## Interface atual

- A rota `/financeiro/` foi ligada ao projeto em `casa_espirita/urls.py`.
- O módulo possui listagem, cadastro, edição e exclusão de contas financeiras.
- O módulo possui extrato individual por conta com saldo acumulado.
- O extrato mostra conta, período, saldo inicial, data do saldo inicial, saldo anterior quando aplicável e saldo final exibido.
- O módulo possui listagem de contas com `saldo_atual` calculado.

## Migrações

- Existe a migration inicial `financeiro/migrations/0001_initial.py`.
- Existe a migration incremental `financeiro/migrations/0002_contafinanceira_saldo_inicial.py`.
- Existe a migration incremental `financeiro/migrations/0003_contafinanceira_data_saldo_inicial_required.py`.
- As migrations antigas não foram alteradas.

## Validação local

- Não foi possível executar `py manage.py check` com sucesso no ambiente atual.
- Motivo: o interpretador disponível não tem o pacote `django` instalado.
- Foi possível validar a sintaxe dos arquivos Python via `py -m compileall financeiro`.
- Assim, a estrutura foi deixada pronta, mas a validação automática do runtime ainda depende de um ambiente com as dependências instaladas.
