# STATE

Data de atualização: 2026-03-23

## Estado atual do módulo financeiro

- O app `financeiro` foi criado e adicionado ao `INSTALLED_APPS`.
- A modelagem de domínio e o registro no Django admin permanecem intactos.
- O módulo já possui base operacional própria fora do admin.
- Existem formulários, views, rotas e templates próprios para contas, centros de custo, pessoas, categorias e lançamentos.
- Ainda não existem edição, exclusão, recorrência, recibos, anexos ou cadastro rápido dentro do lançamento.
- O app `biblioteca` não foi alterado.
- Não foram usados `signals`.

## Modelos existentes no app `financeiro`

- `ContaFinanceira`
- `CentroCusto`
- `PessoaFinanceira`
- `CategoriaFinanceira`
- `LancamentoFinanceiro`

## Revisão contra critérios esperados

- `ContaFinanceira` está aderente aos campos esperados.
- `CentroCusto` está aderente aos campos esperados.
- `PessoaFinanceira` está aderente aos campos esperados.
- `CategoriaFinanceira` está aderente aos campos esperados.
- `LancamentoFinanceiro` está aderente aos campos esperados.
- As três validações mínimas obrigatórias de `LancamentoFinanceiro` já estão implementadas no model.
- Não foi identificada divergência funcional relevante que justificasse alteração de código no domínio.

## Regras mínimas já implementadas em `LancamentoFinanceiro`

- `transferencia` exige `conta_destino`
- `conta_destino` só pode ser usada em `transferencia`
- `conta` e `conta_destino` não podem ser iguais

## Admin

- Todos os models do app `financeiro` estão registrados no admin.

## Interface atual

- A rota `/financeiro/` foi ligada ao projeto em `casa_espirita/urls.py`.
- A home atual é `FinanceiroHomeView`, com navegação para os fluxos operacionais iniciais.
- O módulo possui listagem e cadastro de contas financeiras.
- O módulo possui listagem e cadastro de centros de custo.
- O módulo possui listagem e cadastro de pessoas financeiras.
- O módulo possui listagem e cadastro de categorias financeiras.
- O módulo possui listagem e cadastro de lançamentos financeiros.

## Rotas operacionais atuais

- `/financeiro/`
- `/financeiro/contas/`
- `/financeiro/contas/nova/`
- `/financeiro/centros-custo/`
- `/financeiro/centros-custo/novo/`
- `/financeiro/pessoas/`
- `/financeiro/pessoas/nova/`
- `/financeiro/categorias/`
- `/financeiro/categorias/nova/`
- `/financeiro/lancamentos/`
- `/financeiro/lancamentos/novo/`

## Formulários atuais

- `ContaFinanceiraForm`
- `CentroCustoForm`
- `PessoaFinanceiraForm`
- `CategoriaFinanceiraForm`
- `LancamentoFinanceiroForm`

## Ajuste de usabilidade em lançamento

- O campo `conta_destino` agora aparece apenas quando `tipo = transferencia`.
- Em `receita` e `despesa`, o campo fica oculto e desabilitado na interface.
- Ao trocar de `transferencia` para outro tipo, o valor de `conta_destino` é limpo no navegador.
- O `LancamentoFinanceiroForm` também limpa `conta_destino` no `clean()` quando o tipo não é `transferencia`.
- As validações do model permanecem intactas e continuam sendo a fonte de verdade do domínio.

## Views atuais

- `FinanceiroHomeView`
- `ContaFinanceiraListView`
- `ContaFinanceiraCreateView`
- `CentroCustoListView`
- `CentroCustoCreateView`
- `PessoaFinanceiraListView`
- `PessoaFinanceiraCreateView`
- `CategoriaFinanceiraListView`
- `CategoriaFinanceiraCreateView`
- `LancamentoFinanceiroListView`
- `LancamentoFinanceiroCreateView`

## Migrações

- Foi criada a migration inicial `financeiro/migrations/0001_initial.py`.
- A migration foi escrita manualmente porque o ambiente local usado nesta execução não possui Django instalado.
- A migration atual permanece compatível com a modelagem revisada nesta etapa.

## Validação local

- Não foi possível executar `py manage.py check` com sucesso no ambiente atual.
- Motivo: o interpretador disponível não tem o pacote `django` instalado.
- Foi possível validar a sintaxe dos arquivos Python via `py -m compileall financeiro casa_espirita`.
- Assim, a estrutura foi deixada pronta, mas a validação automática do runtime ainda depende de um ambiente com as dependências instaladas.
