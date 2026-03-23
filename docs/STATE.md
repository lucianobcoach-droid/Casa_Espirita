# STATE

Data de atualização: 2026-03-23

## Estado atual do módulo financeiro

- O app `financeiro` foi criado e adicionado ao `INSTALLED_APPS`.
- A modelagem de domínio e o registro no Django admin permanecem intactos.
- Foi criada a primeira interface operacional real do módulo.
- Existem formulários, views, rotas e templates próprios para pessoas, categorias e lançamentos.
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
- O módulo agora possui listagem e cadastro de pessoas financeiras.
- O módulo agora possui listagem e cadastro de categorias financeiras.
- O módulo agora possui listagem e cadastro de lançamentos financeiros.

## Rotas operacionais atuais

- `/financeiro/`
- `/financeiro/pessoas/`
- `/financeiro/pessoas/nova/`
- `/financeiro/categorias/`
- `/financeiro/categorias/nova/`
- `/financeiro/lancamentos/`
- `/financeiro/lancamentos/novo/`

## Formulários atuais

- `PessoaFinanceiraForm`
- `CategoriaFinanceiraForm`
- `LancamentoFinanceiroForm`

## Views atuais

- `FinanceiroHomeView`
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
