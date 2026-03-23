# STATE

Data de atualização: 2026-03-23

## Estado atual do módulo financeiro

- O app `financeiro` foi criado e adicionado ao `INSTALLED_APPS`.
- A modelagem de domínio, os relacionamentos e o registro no Django admin permanecem intactos, com exceção da evolução incremental já aprovada em `ContaFinanceira`.
- O módulo já possui base operacional própria fora do admin.
- Existem formulários, views, rotas e templates próprios para contas, centros de custo, pessoas, categorias e lançamentos.
- O módulo possui cadastro, listagem, edição, exclusão com confirmação, filtros básicos, autocomplete real no formulário de lançamento e extrato por conta.
- A listagem de contas já mostra `saldo_atual` calculado sem persistir esse valor no banco.
- O app `biblioteca` não foi alterado.
- Não foram usados `signals`.

## ContaFinanceira

`ContaFinanceira` agora possui:

- `saldo_inicial`
- `data_saldo_inicial` obrigatória

Leitura funcional:

- o saldo inicial é dado cadastral
- a data do saldo inicial passou a ser obrigatória
- `saldo_atual` é calculado em tempo de execução
- `saldo_atual` não é salvo no banco

## Extrato por conta

Foi criada a visualização de extrato por conta em rota própria:

- `/financeiro/contas/<id>/extrato/`

Escopo funcional:

- o extrato é individual por conta
- não existe relatório geral nesta etapa
- o saldo acumulado parte do `saldo_inicial`
- receitas entram como entrada
- despesas entram como saída
- transferências saem da conta de origem e entram na conta de destino

## Modelos existentes no app `financeiro`

- `ContaFinanceira`
- `CentroCusto`
- `PessoaFinanceira`
- `CategoriaFinanceira`
- `LancamentoFinanceiro`

## Regras mínimas já implementadas em `LancamentoFinanceiro`

- `transferencia` exige `conta_destino`
- `conta_destino` só pode ser usada em `transferencia`
- `conta` e `conta_destino` não podem ser iguais

## Interface atual

- A rota `/financeiro/` foi ligada ao projeto em `casa_espirita/urls.py`.
- O módulo possui listagem, cadastro, edição e exclusão de contas financeiras.
- O módulo possui extrato individual por conta com saldo acumulado.
- O módulo possui listagem de contas com `saldo_atual` calculado.
- O módulo possui listagem, cadastro, edição e exclusão de centros de custo.
- O módulo possui listagem, cadastro, edição e exclusão de pessoas financeiras.
- O módulo possui listagem, cadastro, edição e exclusão de categorias financeiras.
- O módulo possui listagem, cadastro, edição e exclusão de lançamentos financeiros.

## Rotas operacionais atuais

- `/financeiro/`
- `/financeiro/autocomplete/pessoas/`
- `/financeiro/autocomplete/categorias/`
- `/financeiro/autocomplete/contas/`
- `/financeiro/autocomplete/centros-custo/`
- `/financeiro/contas/`
- `/financeiro/contas/nova/`
- `/financeiro/contas/<id>/extrato/`
- `/financeiro/contas/<id>/editar/`
- `/financeiro/contas/<id>/excluir/`
- `/financeiro/centros-custo/`
- `/financeiro/centros-custo/novo/`
- `/financeiro/centros-custo/<id>/editar/`
- `/financeiro/centros-custo/<id>/excluir/`
- `/financeiro/pessoas/`
- `/financeiro/pessoas/nova/`
- `/financeiro/pessoas/<id>/editar/`
- `/financeiro/pessoas/<id>/excluir/`
- `/financeiro/categorias/`
- `/financeiro/categorias/nova/`
- `/financeiro/categorias/<id>/editar/`
- `/financeiro/categorias/<id>/excluir/`
- `/financeiro/lancamentos/`
- `/financeiro/lancamentos/novo/`
- `/financeiro/lancamentos/<id>/editar/`
- `/financeiro/lancamentos/<id>/excluir/`

## Formulários atuais

- `ContaFinanceiraForm`
- `CentroCustoForm`
- `PessoaFinanceiraForm`
- `CategoriaFinanceiraForm`
- `LancamentoFinanceiroForm`

## Regra do saldo_atual

O `saldo_atual` da conta é calculado assim:

- começa em `saldo_inicial`
- soma receitas da conta
- subtrai despesas da conta
- subtrai transferências em que a conta é origem
- soma transferências em que a conta é destino

## Autocomplete em lançamento

- Os campos relacionais `pessoa`, `categoria`, `conta` e `centro_custo` possuem autocomplete real no formulário de lançamento.
- O campo `conta_destino` também usa o mesmo mecanismo quando exibido em transferências.
- As sugestões são consultadas no banco por endpoints próprios do módulo.
- A busca funciona por qualquer parte do texto, incluindo trechos do meio.

## Migrações

- Existe a migration inicial `financeiro/migrations/0001_initial.py`.
- Existe a migration incremental `financeiro/migrations/0002_contafinanceira_saldo_inicial.py`.
- Foi criada a migration incremental `financeiro/migrations/0003_contafinanceira_data_saldo_inicial_required.py`.
- As migrations antigas não foram alteradas.

## Validação local

- Não foi possível executar `py manage.py check` com sucesso no ambiente atual.
- Motivo: o interpretador disponível não tem o pacote `django` instalado.
- Foi possível validar a sintaxe dos arquivos Python via `py -m compileall financeiro`.
- Assim, a estrutura foi deixada pronta, mas a validação automática do runtime ainda depende de um ambiente com as dependências instaladas.
