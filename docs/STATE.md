# STATE

Data de atualização: 2026-03-23

## Estado atual do módulo financeiro

- O app `financeiro` foi criado e adicionado ao `INSTALLED_APPS`.
- A primeira entrega contém apenas modelagem de domínio e registro no Django admin.
- Não foram criadas telas operacionais, rotas próprias, views nem formulários do módulo financeiro.
- O app `biblioteca` não foi alterado.
- Não foram usados `signals`.

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

## Admin

- Todos os models do app `financeiro` estão registrados no admin.

## Migrações

- Foi criada a migration inicial `financeiro/migrations/0001_initial.py`.
- A migration foi escrita manualmente porque o ambiente local usado nesta execução não possui Django instalado.

## Validação local

- Não foi possível executar `py manage.py makemigrations financeiro` nem `py manage.py check` com sucesso no ambiente atual.
- Motivo: o interpretador disponível não tem o pacote `django` instalado.
- Assim, a estrutura foi deixada pronta, mas a validação automática do runtime depende de um ambiente com as dependências instaladas.

