# STATE

Data de atualizacao: 2026-03-26

## Estado atual do modulo financeiro

- O app `financeiro` foi criado e adicionado ao `INSTALLED_APPS`.
- A modelagem de dominio, os relacionamentos e o registro no Django admin permanecem intactos, com excecao da evolucao incremental ja aprovada em `ContaFinanceira` e nas validacoes de `LancamentoFinanceiro`.
- O modulo ja possui base operacional propria fora do admin.
- Existem formularios, views, rotas e templates proprios para contas, centros de custo, pessoas, categorias e lancamentos.
- O modulo possui cadastro, listagem, edicao, exclusao com confirmacao, filtros basicos, autocomplete real no formulario de lancamento e extrato por conta.
- O extrato por conta ja aceita filtro por periodo via GET e calculo de saldo anterior.
- O saldo real das contas e o extrato agora consideram apenas lancamentos quitados.
- As tabelas principais do financeiro usam layout mais compacto, zebra striping e impressao mais limpa.
- O financeiro agora possui menu proprio `Extratos` com filtro por conta e periodo.
- O financeiro agora possui tela propria de `Resumo` consolidado por periodo.
- O financeiro agora possui tela propria de `Prestacao de Contas` por periodo.
- As telas de `Resumo` e `Prestacao de Contas` agora permitem selecionar quais contas entram no relatorio.
- As telas de `Resumo` e `Prestacao de Contas` agora mostram receitas e despesas agrupadas por categoria.
- As telas de `Resumo` e `Prestacao de Contas` agora mostram despesas agrupadas por centro de custo.
- A listagem de lancamentos agora possui filtros operacionais por data inicial, data final, conta, pessoa e categoria.
- As telas de `Resumo` e `Prestacao de Contas` agora possuem controle de exibicao apenas para o bloco de centro de custo, sem alterar os totais gerais do relatorio.
- A tela de `Prestacao de Contas` recebeu refinamento visual especifico para impressao em A4.
- A `Prestacao de Contas` agora tem apresentacao mais formal, com menos aparencia de dashboard.
- As telas de `Extratos` e `Resumo` agora tem impressao mais limpa, com melhor alinhamento de valores e identificacao do relatorio.
- O menu superior do financeiro foi reorganizado para separar `Financeiro`, `Lancamentos`, `Extratos`, `Relatorios` e `Cadastros`.
- A home do modulo financeiro agora usa atalhos mais neutros e harmonicos, com destaque principal apenas para `Lancamentos`.
- O menu superior do financeiro agora tambem possui dropdown `Configuracoes`, com acesso a `Assinaturas` e `Configuracao Institucional`.
- A home do modulo financeiro agora tambem oferece atalhos visiveis para `Assinaturas` e `Configuracao Institucional`.
- O app `biblioteca` nao foi alterado.
- Nao foram usados `signals`.

## ContaFinanceira

`ContaFinanceira` possui:

- `saldo_inicial`
- `data_saldo_inicial` obrigatoria

Leitura funcional:

- o saldo inicial e dado cadastral
- `saldo_atual` e calculado em tempo de execucao
- `saldo_atual` nao e salvo no banco
- apenas lancamentos com status `quitado` afetam `saldo_atual`

## LancamentoFinanceiro

`LancamentoFinanceiro` agora exige:

- `receita` e `despesa` exigem `pessoa`
- `receita` e `despesa` exigem `categoria`
- `transferencia` nao exige `pessoa`
- `transferencia` nao exige `categoria`
- `transferencia` nao exige `centro_custo`
- `transferencia` exige `conta_destino`

Leitura funcional:

- o cadastro e a edicao de lancamento devem exigir `pessoa` em receita e despesa
- o cadastro e a edicao de lancamento devem exigir `categoria` em receita e despesa
- em transferencia, o formulario limpa `pessoa`, `categoria` e `centro_custo`
- em transferencia, `conta_destino` deve aparecer com obrigatoriedade visual e funcional
- a ausencia de `pessoa`, `categoria`, `conta` ou `conta_destino` deve gerar erro no formulario, sem estourar `IntegrityError`
- `numero_documento` pode continuar vazio no formulario, mas e gerado automaticamente antes de salvar
- `numero_documento` informado manualmente deve ser unico entre os lancamentos
- `numero_documento` gerado automaticamente tambem deve sair unico
- a validacao de duplicidade funciona no cadastro e na edicao
- na edicao, o proprio registro e ignorado na checagem de duplicidade
- a obrigatoriedade final de `pessoa` e `categoria` permanece condicional na camada da aplicacao
- o formulario de lancamento agora pode consultar e exibir os ultimos 5 lancamentos da `pessoa` selecionada
- o bloco de historico do favorecido mostra data, tipo, descricao, valor, categoria e `numero_documento` quando existir
- o historico do favorecido acompanha a selecao da pessoa no autocomplete sem alterar a logica atual do campo
- `data_competencia` deve ser validada antes da gravacao
- `data_pagamento` nao pode ser anterior a `data_competencia`
- o extrato por conta passa a exibir `numero_documento` de forma discreta junto da descricao, quando existir
- a listagem de lancamentos pode exibir `Transferencia entre Contas` quando uma transferencia nao tiver `pessoa`
- os relatorios mantem tratamento defensivo para base antiga, exibindo `Sem categoria` se algum dado legado surgir

## Extrato por conta

Existe visualizacao de extrato por conta em rota propria:

- `/financeiro/contas/<id>/extrato/`
- `/financeiro/extratos/`
- `/financeiro/resumo/`

Escopo funcional:

- sem filtro: extrato completo desde o saldo inicial
- com filtro: lancamentos apenas do periodo
- com `data_inicial`: calculo de `saldo_anterior`
- saldo acumulado do periodo comeca a partir de `saldo_anterior`
- somente lancamentos quitados aparecem no extrato
- nao existe relatorio geral nesta etapa
- a tela `Extratos` reutiliza a mesma logica do extrato por conta

## Resumo consolidado do periodo

Existe visualizacao de resumo consolidado em rota propria:

- `/financeiro/resumo/`
- `/financeiro/prestacao-contas/`

Escopo funcional:

- filtro por `data_inicial` e `data_final`
- filtro por contas selecionadas
- sem filtro informado, assume o mes atual
- sem selecao explicita de contas, considera todas as contas
- mostra saldo inicial consolidado, receitas do periodo, despesas do periodo, saldo do periodo e saldo final consolidado
- mostra receitas por categoria e despesas por categoria
- mostra despesas por centro de custo
- permite controlar a exibicao apenas do bloco de centro de custo
- considera apenas lancamentos efetivos
- transferencias internas nao entram como receita nem despesa no consolidado
- lancamentos sem categoria aparecem no agrupamento como `Sem categoria`
- despesas sem centro de custo aparecem no agrupamento como `Sem centro de custo`

## Prestacao de contas do periodo

Existe visualizacao de prestacao de contas em rota propria:

- `/financeiro/prestacao-contas/`

Escopo funcional:

- filtro por `data_inicial` e `data_final`
- filtro por contas selecionadas
- sem filtro informado, assume o mes atual
- sem selecao explicita de contas, considera todas as contas
- organiza a visualizacao em blocos formais
- usa cabecalho documental e estrutura continua de relatorio
- mostra composicao do saldo inicial
- mostra receitas e despesas ja consolidadas por categoria
- mostra despesas agrupadas por centro de custo
- permite controlar a exibicao apenas do bloco de centro de custo sem alterar os totais consolidados
- mostra resumo do saldo disponivel
- mostra composicao do saldo final por conta
- mantem transferencias internas neutras no consolidado geral
- lancamentos sem categoria aparecem no agrupamento como `Sem categoria`
- despesas sem centro de custo aparecem no agrupamento como `Sem centro de custo`
- na impressao, oculta controles e mostra bloco simples de assinatura ao final

## Regra de saldo no extrato

Sem filtro:

- comeca do `saldo_inicial`
- soma receitas
- subtrai despesas
- subtrai transferencias da conta de origem
- soma transferencias da conta de destino
- considera apenas lancamentos quitados

Com filtro por periodo:

- `saldo_anterior` comeca em `saldo_inicial`
- soma e subtrai movimentacoes anteriores a `data_inicial`
- o periodo listado usa apenas lancamentos entre `data_inicial` e `data_final`
- o saldo acumulado das linhas do periodo comeca de `saldo_anterior`
- o saldo anterior tambem considera apenas lancamentos quitados

## Interface atual

- A rota `/financeiro/` foi ligada ao projeto em `casa_espirita/urls.py`.
- O modulo possui listagem, cadastro, edicao e exclusao de contas financeiras.
- O modulo possui extrato individual por conta com saldo acumulado.
- O modulo possui tela propria de extratos com filtro por conta e periodo.
- O modulo possui tela de resumo consolidado por periodo.
- O modulo possui tela de prestacao de contas por periodo.
- O modulo possui tela propria de recibo por lancamento em HTML imprimivel.
- O recibo usa a descricao do lancamento como campo `Referente a`.
- O recibo prioriza `data_pagamento` como data principal e usa `data_competencia` como fallback explicito quando `data_pagamento` estiver vazia.
- O recibo nao exibe conta financeira, observacoes, categoria tecnica nem centro de custo nesta etapa.
- O recibo agora pode usar mensagem opcional cadastrada na categoria financeira do lancamento.
- Quando a categoria nao tiver mensagem de recibo, o rodape do recibo usa mensagem padrao simples e segura.
- O recibo agora usa apresentacao mais documental, com cabecalho simples, destaque de numero e valor, corpo textual e impressao A4 mais limpa.
- No acabamento fino do recibo, `Recebi(emos) de` passou a mostrar apenas o nome da pessoa, `A importancia de` passou a usar valor por extenso e a data passou a aparecer apenas em formato documental humano.
- O recibo agora pode usar assinatura institucional configuravel quando existir assinatura ativa marcada como padrao.
- Quando nao existir assinatura institucional padrao, o recibo continua com fallback simples no bloco final.
- O recibo agora pode usar configuracao institucional dinamica com nome, cidade, logo e mensagem padrao quando existir configuracao ativa marcada como padrao.
- Quando algum dado institucional nao estiver configurado, o recibo preserva fallback seguro sem quebrar o layout.
- A integracao visual final do recibo agora tenta carregar a logo por URL acessivel ao navegador, oculta a imagem com elegancia quando a URL falha e usa `assinatura_texto` com estilo manuscrito no bloco de assinatura.
- A impressao do recibo agora foi compactada para reduzir espaco vazio abaixo da assinatura e deixar o bloco com altura mais proporcional ao conteudo.
- A largura util e a centralizacao horizontal do recibo na impressao foram ajustadas para melhor aproveitamento da folha A4.
- A margem superior do recibo na impressao agora foi levemente ampliada para dar respiro inicial sem reintroduzir excesso de altura.
- O extrato mostra conta, periodo, saldo inicial, data do saldo inicial, saldo anterior quando aplicavel e saldo final exibido.
- O modulo possui listagem de contas com `saldo_atual` calculado.
- A listagem de lancamentos destaca tipo por cor e status nao quitado em negrito.
- A listagem de lancamentos agora oferece acesso direto ao recibo de cada lancamento.
- O extrato e as listagens priorizadas tem ajustes de impressao para esconder controles e manter a tabela legivel.

## Migracoes

- Existe a migration inicial `financeiro/migrations/0001_initial.py`.
- Existe a migration incremental `financeiro/migrations/0002_contafinanceira_saldo_inicial.py`.
- Existe a migration incremental `financeiro/migrations/0003_contafinanceira_data_saldo_inicial_required.py`.
- Existe a migration incremental `financeiro/migrations/0004_lancamentofinanceiro_categoria_required.py`.
- Existe a migration incremental `financeiro/migrations/0005_lancamentofinanceiro_pessoa_required.py`.
- Existe a migration incremental `financeiro/migrations/0006_lancamentofinanceiro_conditional_required_fields.py`.
- Existe a migration incremental `financeiro/migrations/0007_categoriafinanceira_mensagem_recibo.py`.
- Existe a migration incremental `financeiro/migrations/0008_assinaturainstitucional.py`.
- Existe a migration incremental `financeiro/migrations/0009_configuracaoinstitucional.py`.
- A cadeia `0005` -> `0006` representa a consolidacao incremental da obrigatoriedade condicional de `pessoa` e `categoria`.
- A `0007` adiciona `mensagem_recibo` opcional em `CategoriaFinanceira` para personalizacao controlada do recibo com fallback padrao.
- A `0008` adiciona `AssinaturaInstitucional` para uso controlado no recibo com selecao por assinatura padrao ativa.
- A `0009` adiciona `ConfiguracaoInstitucional` para uso dinamico no recibo com selecao por configuracao padrao ativa.
- Nao foi criada migration nova para unicidade de `numero_documento` nesta etapa.
- A validacao de nao repeticao de `numero_documento` ficou na camada de aplicacao por seguranca incremental.
- As migrations antigas nao foram alteradas.

## Validacao local

- Nao foi possivel executar `py manage.py check` com sucesso no ambiente atual.
- Motivo: o interpretador disponivel nao tem o pacote `django` instalado.
- Foi possivel validar a sintaxe dos arquivos Python via `py -m compileall financeiro`.
- Assim, a estrutura foi deixada pronta, mas a validacao automatica do runtime ainda depende de um ambiente com as dependencias instaladas.
