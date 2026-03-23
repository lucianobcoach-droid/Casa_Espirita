# STATE

Data de atualização: 2026-03-23

## Estado atual do módulo financeiro

- O app `financeiro` foi criado e adicionado ao `INSTALLED_APPS`.
- A modelagem de domínio, os relacionamentos e o registro no Django admin permanecem intactos, com exceção da ETAPA 1 aprovada em `ContaFinanceira`.
- O módulo já possui base operacional própria fora do admin.
- Existem formulários, views, rotas e templates próprios para contas, centros de custo, pessoas, categorias e lançamentos.
- O módulo possui cadastro, listagem, edição, exclusão com confirmação, filtros básicos e autocomplete real no formulário de lançamento.
- Ainda não existem recorrência, recibos, anexos, extrato ou cálculo de saldo por movimentação.
- O app `biblioteca` não foi alterado.
- Não foram usados `signals`.

## ETAPA 1 aprovada em ContaFinanceira

`ContaFinanceira` agora possui:

- `saldo_inicial`
- `data_saldo_inicial`

Leitura funcional desta etapa:

- o saldo inicial é apenas um dado cadastral da conta
- não existe extrato nesta etapa
- não existe motor de apuração de saldo acumulado nesta etapa
- nenhuma outra regra de domínio foi alterada

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

## Comportamento de transferência

- A transferência continua sendo um único registro lógico em `LancamentoFinanceiro`.
- O valor continua positivo no formulário.
- Na interpretação operacional do sistema, a transferência representa saída na conta de origem e entrada na conta de destino.
- Não foi criado segundo model e não houve duplicação manual de lançamentos.
- A interface de listagem e formulário deixa esse comportamento explícito para o usuário.

## Admin

- Todos os models do app `financeiro` estão registrados no admin.

## Interface atual

- A rota `/financeiro/` foi ligada ao projeto em `casa_espirita/urls.py`.
- A home atual é `FinanceiroHomeView`, com navegação para os fluxos operacionais.
- O módulo possui listagem, cadastro, edição e exclusão de contas financeiras.
- O módulo possui listagem, cadastro, edição e exclusão de centros de custo.
- O módulo possui listagem, cadastro, edição e exclusão de pessoas financeiras.
- O módulo possui listagem, cadastro, edição e exclusão de categorias financeiras.
- O módulo possui listagem, cadastro, edição e exclusão de lançamentos financeiros.

## Ajustes de conta nesta etapa

- O formulário de conta agora aceita `saldo_inicial`.
- O formulário de conta agora aceita `data_saldo_inicial`.
- A listagem de contas passou a exibir o saldo inicial e, quando informada, a data de referência.

## Rotas operacionais atuais

- `/financeiro/`
- `/financeiro/autocomplete/pessoas/`
- `/financeiro/autocomplete/categorias/`
- `/financeiro/autocomplete/contas/`
- `/financeiro/autocomplete/centros-custo/`
- `/financeiro/contas/`
- `/financeiro/contas/nova/`
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

## Filtros básicos disponíveis

- Pessoas: por nome e código com busca por contém.
- Categorias: por nome com busca por contém e por tipo.
- Contas: por nome com busca por contém e por situação ativa/inativa.
- Centros de custo: por código e nome com busca por contém.
- Lançamentos: por tipo, status, descrição e número do documento, com busca por contém nos campos textuais.

## Autocomplete em lançamento

- Os campos relacionais `pessoa`, `categoria`, `conta` e `centro_custo` possuem autocomplete real no formulário de lançamento.
- O campo `conta_destino` também usa o mesmo mecanismo quando exibido em transferências.
- As sugestões são consultadas no banco por endpoints próprios do módulo.
- A busca de sugestões funciona por qualquer parte do texto, incluindo trechos do meio.
- A solução usa JavaScript simples e endpoints JSON leves, sem alterar o domínio nem adicionar dependência pesada.

## Ajuste de usabilidade em lançamento

- O campo `conta_destino` aparece apenas quando `tipo = transferencia`.
- Em `receita` e `despesa`, o campo fica oculto e desabilitado na interface.
- Ao trocar de `transferencia` para outro tipo, o valor de `conta_destino` é limpo no navegador.
- O `LancamentoFinanceiroForm` também limpa `conta_destino` no `clean()` quando o tipo não é `transferencia`.
- As validações do model permanecem intactas e continuam sendo a fonte de verdade do domínio.

## Views atuais

- `FinanceiroHomeView`
- `FinanceiroAutocompleteView`
- `PessoaFinanceiraAutocompleteView`
- `CategoriaFinanceiraAutocompleteView`
- `ContaFinanceiraAutocompleteView`
- `CentroCustoAutocompleteView`
- `ContaFinanceiraListView`
- `ContaFinanceiraCreateView`
- `ContaFinanceiraUpdateView`
- `ContaFinanceiraDeleteView`
- `CentroCustoListView`
- `CentroCustoCreateView`
- `CentroCustoUpdateView`
- `CentroCustoDeleteView`
- `PessoaFinanceiraListView`
- `PessoaFinanceiraCreateView`
- `PessoaFinanceiraUpdateView`
- `PessoaFinanceiraDeleteView`
- `CategoriaFinanceiraListView`
- `CategoriaFinanceiraCreateView`
- `CategoriaFinanceiraUpdateView`
- `CategoriaFinanceiraDeleteView`
- `LancamentoFinanceiroListView`
- `LancamentoFinanceiroCreateView`
- `LancamentoFinanceiroUpdateView`
- `LancamentoFinanceiroDeleteView`

## Migrações

- Existe a migration inicial `financeiro/migrations/0001_initial.py`.
- Foi criada a migration incremental `financeiro/migrations/0002_contafinanceira_saldo_inicial.py`.
- As migrations antigas não foram alteradas.

## Validação local

- Não foi possível executar `py manage.py check` com sucesso no ambiente atual.
- Motivo: o interpretador disponível não tem o pacote `django` instalado.
- Foi possível validar a sintaxe dos arquivos Python via `py -m compileall financeiro`.
- Assim, a estrutura foi deixada pronta, mas a validação automática do runtime ainda depende de um ambiente com as dependências instaladas.
