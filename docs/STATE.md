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
- As tabelas principais do financeiro usam layout mais compacto, zebra striping e impressão mais limpa.
- O financeiro agora possui menu próprio `Extratos` com filtro por conta e período.
- O financeiro agora possui tela própria de `Resumo` consolidado por período.
- O financeiro agora possui tela própria de `Prestacao de Contas` por período.
- As telas de `Resumo` e `Prestacao de Contas` agora permitem selecionar quais contas entram no relatório.
- As telas de `Resumo` e `Prestacao de Contas` agora mostram receitas e despesas agrupadas por categoria.
- As telas de `Resumo` e `Prestacao de Contas` agora mostram despesas agrupadas por centro de custo.
- As telas de `Resumo` e `Prestacao de Contas` agora possuem controle de exibição para agrupamentos por categoria e por centro de custo, sem alterar os totais gerais do relatório.
- A tela de `Prestacao de Contas` recebeu refinamento visual específico para impressão em A4.
- A `Prestacao de Contas` agora tem apresentação mais formal, com menos aparência de dashboard.
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
- `/financeiro/extratos/`
- `/financeiro/resumo/`

Escopo funcional:

- sem filtro: extrato completo desde o saldo inicial
- com filtro: lançamentos apenas do período
- com `data_inicial`: cálculo de `saldo_anterior`
- saldo acumulado do período começa a partir de `saldo_anterior`
- somente lançamentos quitados aparecem no extrato
- não existe relatório geral nesta etapa
- a tela `Extratos` reutiliza a mesma lógica do extrato por conta

## Resumo consolidado do período

Existe visualização de resumo consolidado em rota própria:

- `/financeiro/resumo/`
- `/financeiro/prestacao-contas/`

Escopo funcional:

- filtro por `data_inicial` e `data_final`
- filtro por contas selecionadas
- sem filtro informado, assume o mês atual
- sem seleção explícita de contas, considera todas as contas
- mostra saldo inicial consolidado, receitas do período, despesas do período, saldo do período e saldo final consolidado
- mostra receitas por categoria e despesas por categoria
- mostra despesas por centro de custo
- permite escolher se os agrupamentos mostram todos os itens, apenas itens com vínculo ou apenas itens sem vínculo
- considera apenas lançamentos efetivos
- transferências internas não entram como receita nem despesa no consolidado
- lançamentos sem categoria aparecem no agrupamento como `Sem categoria`
- despesas sem centro de custo aparecem no agrupamento como `Sem centro de custo`

## Prestacao de contas do periodo

Existe visualização de prestação de contas em rota própria:

- `/financeiro/prestacao-contas/`

Escopo funcional:

- filtro por `data_inicial` e `data_final`
- filtro por contas selecionadas
- sem filtro informado, assume o mês atual
- sem seleção explícita de contas, considera todas as contas
- organiza a visualização em blocos formais
- usa cabeçalho documental e estrutura contínua de relatório
- mostra composição do saldo inicial
- mostra receitas e despesas já consolidadas por categoria
- mostra despesas agrupadas por centro de custo
- permite controlar a exibição dos agrupamentos por categoria e por centro de custo sem alterar os totais consolidados
- mostra resumo do saldo disponível
- mostra composição do saldo final por conta
- mantém transferências internas neutras no consolidado geral
- lançamentos sem categoria aparecem no agrupamento como `Sem categoria`
- despesas sem centro de custo aparecem no agrupamento como `Sem centro de custo`
- na impressão, oculta controles e mostra bloco simples de assinatura ao final

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
- O módulo possui tela própria de extratos com filtro por conta e período.
- O módulo possui tela de resumo consolidado por período.
- O módulo possui tela de prestação de contas por período.
- O extrato mostra conta, período, saldo inicial, data do saldo inicial, saldo anterior quando aplicável e saldo final exibido.
- O módulo possui listagem de contas com `saldo_atual` calculado.
- A listagem de lançamentos destaca tipo por cor e status não quitado em negrito.
- O extrato e as listagens priorizadas têm ajustes de impressão para esconder controles e manter a tabela legível.

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
