# STATE

Data de atualizacao: 2026-03-27

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
- A listagem principal de lancamentos agora usa ordem oficial explicita por `-data_competencia`, `-data_pagamento`, `-criado_em` e `-pk`, aplicada diretamente na view para evitar impacto nas demais consultas do modulo.
- As telas de `Resumo` e `Prestacao de Contas` agora possuem controle de exibicao apenas para o bloco de centro de custo, sem alterar os totais gerais do relatorio.
- A tela de `Prestacao de Contas` recebeu refinamento visual especifico para impressao em A4.
- A `Prestacao de Contas` agora tem apresentacao mais formal, com menos aparencia de dashboard.
- As telas de `Extratos` e `Resumo` agora tem impressao mais limpa, com melhor alinhamento de valores e identificacao do relatorio.
- O menu superior do financeiro foi reorganizado para separar `Financeiro`, `Lancamentos`, `Extratos`, `Relatorios` e `Cadastros`.
- A home do modulo financeiro agora usa atalhos mais neutros e harmonicos, com destaque principal apenas para `Lancamentos`.
- O menu superior do financeiro agora tambem possui dropdown `Configuracoes`, com acesso a `Assinaturas` e `Configuracao Institucional`.
- A home do modulo financeiro agora tambem oferece atalhos visiveis para `Assinaturas` e `Configuracao Institucional`.
- O menu superior do financeiro agora tambem oferece acesso a `Auditoria de Lancamentos` no dropdown `Configuracoes`.
- A home do modulo financeiro agora tambem oferece atalho visivel para `Auditoria de Lancamentos`.
- A home do modulo financeiro recebeu revisao leve de textos para melhorar clareza operacional dos atalhos, sem alterar a estrutura da pagina.
- Menu, home e titulos principais do modulo financeiro receberam padronizacao textual leve para reduzir inconsistencias de rotulagem entre telas ja existentes.
- Paginas internas do financeiro receberam padronizacao textual leve em botoes operacionais, com acoes de criacao e atualizacao mais consistentes para usuario leigo.
- As listagens principais do financeiro agora usam botoes de criacao mais especificos e coerentes com os nomes completos das entidades exibidas nas telas.
- Foi identificada como limitacao atual uma densidade visual ainda aquem do ideal em telas do financeiro, especialmente em filtros, formularios e listagens, com espaco horizontal ainda melhor aproveitavel quando o navegador esta em 100% de zoom.
- A frente transversal de densidade visual e aproveitamento horizontal do financeiro foi iniciada de forma incremental pela base compartilhada do modulo.
- Nesta primeira microetapa, a listagem de lancamentos e o formulario padrao de lancamento/edicao passaram a usar espacamentos mais compactos, melhor distribuicao de colunas e aproveitamento horizontal mais eficiente em 100% de zoom, sem redesign amplo.
- O extrato por conta agora tambem recebeu a aplicacao inicial dessa frente visual, com filtros mais compactos, cabecalho resumido em meta-informacoes mais densas e melhor distribuicao horizontal da tabela sem alterar a leitura funcional do extrato.
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
- `numero_documento` informado manualmente deve continuar unico nos lancamentos comuns
- `numero_documento` gerado automaticamente tambem deve sair unico
- a validacao de duplicidade funciona no cadastro e na edicao
- na edicao, o proprio registro e ignorado na checagem de duplicidade
- o formulario de lancamento agora pode criar rateio simples quando `Lancamento com rateio` estiver marcado
- no rateio inicial, o usuario informa um `valor total do documento` apenas para validar o fechamento do grupo
- no rateio inicial, o sistema exige no minimo 2 linhas validas com categoria obrigatoria e valor positivo
- no rateio inicial, a soma das linhas precisa ser igual ao `valor total do documento`
- no rateio inicial, o mesmo `numero_documento` pode se repetir apenas como replicacao interna entre linhas do mesmo `grupo_rateio`
- esse `numero_documento` nao pode coincidir com outro documento independente ja lancado no sistema, mesmo que o outro caso tambem seja rateado
- na edicao individual de linhas rateadas, o sistema agora tambem impede que uma linha do grupo passe a divergir do `numero_documento` compartilhado pelas demais linhas do mesmo `grupo_rateio`
- na segunda versao do rateio, categorias repetidas no payload passam a ser consolidadas por soma antes da gravacao das linhas finais
- na segunda versao do rateio, o create volta corretamente para a listagem apos criar multiplas linhas do grupo
- nesta primeira versao, `valor_total_documento` nao e persistido no model; ele existe apenas no formulario para validacao
- a edicao individual de lancamentos rateados continua disponivel por linha, agora ao lado da base inicial de edicao coordenada do grupo
- se um grupo rateado antigo estiver internamente inconsistente em `numero_documento`, a validacao agora bloqueia novas gravacoes ate que o grupo seja regularizado
- o campo `tipo` do formulario de lancamento agora abre preenchido com `receita` e sem opcao vazia inicial
- no formulario de lancamento, `data_pagamento` passou a aparecer antes de `data_competencia`
- `data_pagamento` agora passou a ser obrigatoria no formulario operacional do modulo, com indicativo visual claro de obrigatoriedade
- no formulario de lancamento, preencher `data_pagamento` agora preenche automaticamente `data_competencia` quando ela estiver vazia ou ainda estiver sob valor autoatribuido, preservando edicao manual posterior
- a revisao atual ficou concentrada no formulario e no template; nesta etapa nao houve mudanca de modelagem para tornar `data_pagamento` obrigatoria fora do fluxo operacional atual
- a obrigatoriedade final de `pessoa` e `categoria` permanece condicional na camada da aplicacao
- o formulario de lancamento agora pode consultar e exibir os ultimos 5 lancamentos da `pessoa` selecionada
- o bloco de historico do favorecido mostra data, tipo, descricao, valor, categoria e `numero_documento` quando existir
- o historico do favorecido acompanha a selecao da pessoa no autocomplete sem alterar a logica atual do campo
- `data_competencia` deve ser validada antes da gravacao
- `data_pagamento` nao pode ser anterior a `data_competencia`
- a primeira versao da auditoria do financeiro agora registra create, update e delete de `LancamentoFinanceiro` em model proprio
- o log da primeira versao armazena acao, modelo afetado, id do registro, data/hora, usuario quando disponivel e campos alterados em JSON simples
- o create comum, o create com rateio, a edicao individual de linha rateada e o delete agora geram eventos explicitos de auditoria
- a auditoria agora tambem registra create, update e delete de `ContaFinanceira`, mantendo o mesmo padrao incremental ja usado em `LancamentoFinanceiro`
- a auditoria ja possui captura inicial em `LancamentoFinanceiro` e `ContaFinanceira`, tela propria de leitura minima e filtros simples
- nesta primeira expansao, a auditoria ainda nao foi estendida para pessoas, categorias, centros de custo, assinaturas ou configuracao institucional
- a leitura minima da auditoria agora existe em tela propria, ordenada por `data_hora` decrescente e abrangendo as entidades ja auditadas do modulo financeiro
- a leitura inicial da auditoria mostra data/hora, acao, modelo, id do registro, usuario e campos alterados em resumo estruturado simples
- a leitura da auditoria agora possui filtros simples por acao, periodo inicial/final e id do registro, mantendo ordenacao por `data_hora` decrescente
- nesta leitura operacional, o filtro por usuario ainda nao foi adicionado porque o proprio usuario da auditoria continua opcional na primeira versao
- nesta primeira leitura operacional da auditoria, ainda nao existem filtros complexos nem paginacao avancada
- a edicao coordenada do grupo rateado agora possui fluxo proprio inicial, com view, rota e template proprios, sem substituir a edicao individual da linha
- a base atual da edicao coordenada carrega o grupo por `grupo_rateio`, trabalha apenas com grupos validos e prepara os dados comuns e as linhas de rateio no mesmo fluxo
- na persistencia da edicao coordenada, linhas com `id` no payload agora sao casadas exatamente com a linha correspondente do mesmo `grupo_rateio`
- ids de linhas que nao pertencem ao grupo atual agora geram erro de validacao no formulario e nao sao reaproveitados por posicao
- o salvamento da edicao coordenada do grupo agora ocorre em transacao, preservando o mesmo `grupo_rateio` e mantendo a auditoria de create, update e delete das linhas afetadas
- grupos invalidos, legados ou com consistencia insuficiente para a edicao coordenada agora retornam com mensagem operacional e redirecionamento seguro para a edicao individual da linha representativa
- a listagem principal de lancamentos agora tambem oferece acesso discreto a `Editar grupo` quando a linha pertence a um `grupo_rateio`
- a tela propria da edicao coordenada do grupo agora separa com mais clareza os dados comuns do documento e as linhas do rateio, reforcando visualmente que o salvamento afeta o grupo inteiro
- a experiencia inicial da tela coordenada agora tambem traz textos orientativos mais explicitos e feedback visual mais claro quando houver inconsistencias no payload do rateio
- a tela coordenada agora deixa mais claro o comportamento operacional de salvar, erro e retorno, incluindo mensagem de que o grupo inteiro sera atualizado e atalho direto para voltar a edicao individual da linha representativa
- quando um grupo legado, inconsistente ou insuficiente nao pode abrir a edicao coordenada, o sistema agora identifica melhor o motivo operacional do bloqueio e leva a edicao individual com contexto explicito do fallback seguro
- o fluxo coordenado agora tambem deixa mais previsivel o retorno sem erro tecnico: ao salvar ou cancelar, a listagem principal recebe contexto explicito da origem do retorno, e a volta para a edicao individual sinaliza que o fluxo em bloco foi deixado sem gravacao
- a tela coordenada do grupo rateado agora tambem tem acabamento visual mais consistente, com hierarquia mais clara entre resumo do grupo, dados comuns, linhas do rateio, alertas e acoes finais
- a tela de edicao coordenada do rateio agora foi simplificada para espelhar melhor o formulario padrao de lancamento, mantendo apenas os avisos curtos e os elementos extras estritamente necessarios para o rateio
- na tela de edicao coordenada do grupo rateado, `data_pagamento` e `data_competencia` agora chegam preenchidas no formato aceito pelos inputs HTML de data
- na listagem principal, lancamentos rateados agora usam apenas a acao principal `Editar`, apontando para a edicao coordenada do grupo sem competir com um botao separado de `Editar grupo`
- a experiencia final da edicao coordenada do grupo ainda nao foi concluida; a base inicial foi aberta sem encerrar os refinamentos futuros dessa frente
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
- a ordem oficial desejada do extrato ficou consolidada como leitura crescente por `data_competencia`, com desempate por `criado_em` e `pk`
- lancamentos rateados agora aparecem consolidados por `grupo_rateio` no extrato, com leitura documental do valor total do documento na linha exibida
- a consolidacao do rateio no extrato ficou restrita a apresentacao da tela, sem alterar a modelagem do rateio nem a base de calculo do saldo
- na apresentacao do extrato, a data principal exibida na linha passou a priorizar `data_pagamento`, com fallback para `data_competencia`
- o `numero_documento` do extrato agora aparece em coluna propria, ao lado da data, sem repetir prefixos ou textos auxiliares dentro da descricao
- o topo do extrato agora preserva apenas resumo realmente operacional, como conta, periodo e saldo anterior quando aplicavel, sem repetir `Saldo inicial` nem `Saldo final`
- a primeira linha destacada do corpo do extrato agora usa o rotulo `Saldo anterior`
- a linha `Saldo anterior` do corpo do extrato agora reutiliza o mesmo valor de `saldo_anterior` ja calculado para o periodo, sem manter um valor paralelo zerado
- o `Saldo final` do extrato permanece como ultima linha destacada no corpo da tabela, com apresentacao limpa e sem parecer uma movimentacao artificial
- a tela do extrato agora possui botao de impressao e cabecalho proprio para impressao, mantendo as linhas de saldo dentro do corpo da tabela e com tabela impressa menos rigida, com menos quebra desnecessaria nas colunas curtas
- no modo de impressao do extrato, o cabecalho visual da tela fica oculto e o PDF passa a mostrar apenas o cabecalho proprio de impressao com a tabela do extrato
- bases antigas ou inconsistentes sem `grupo_rateio` valido continuam como limitacao conhecida e aparecem individualmente no extrato ate regularizacao da base

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
- O modulo agora possui tela simples de leitura da `Auditoria de Lancamentos`.
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
- O extrato agora consolida lancamentos rateados por `grupo_rateio`, exibindo na linha mostrada ao usuario o valor total do documento e mantendo a leitura cronologica crescente do saldo.
- A auditoria de lancamentos agora pode ser consultada em tela propria simples, com ordenacao decrescente por data/hora e detalhamento basico dos campos alterados.
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
- Existe a migration incremental `financeiro/migrations/0010_lancamentofinanceiro_rateio_campos.py`.
- Existe a migration incremental `financeiro/migrations/0011_auditoriafinanceiro.py`.
- A cadeia `0005` -> `0006` representa a consolidacao incremental da obrigatoriedade condicional de `pessoa` e `categoria`.
- A `0007` adiciona `mensagem_recibo` opcional em `CategoriaFinanceira` para personalizacao controlada do recibo com fallback padrao.
- A `0008` adiciona `AssinaturaInstitucional` para uso controlado no recibo com selecao por assinatura padrao ativa.
- A `0009` adiciona `ConfiguracaoInstitucional` para uso dinamico no recibo com selecao por configuracao padrao ativa.
- A `0010` adiciona suporte incremental a `com_rateio` e `grupo_rateio` em `LancamentoFinanceiro`.
- A `0011` adiciona `AuditoriaFinanceiro` para registrar create, update e delete de `LancamentoFinanceiro` sem uso de `signals`.
- Nao foi criada migration nova para unicidade de `numero_documento` nesta etapa.
- A validacao de nao repeticao de `numero_documento` ficou na camada de aplicacao por seguranca incremental.
- As migrations antigas nao foram alteradas.

## Frentes abertas por auditoria funcional

- Ficou registrada nesta auditoria funcional a frente residual de revisao estrutural da obrigatoriedade de `data_pagamento`, caso a regra hoje concentrada no formulario precise subir para nivel de modelagem.
- Ficou registrada nesta auditoria funcional a frente de expansao da auditoria de alteracoes no financeiro para alem de `LancamentoFinanceiro`, preservando a abordagem incremental e sem `signals`.
- Nesta etapa de auditoria funcional e documental, nenhum patch de codigo foi executado.

## Diretriz incremental para auditoria de alteracoes

- a trilha de auditoria do financeiro comecou por `LancamentoFinanceiro` e deve se expandir depois para contas, pessoas, categorias, centros de custo, assinaturas e configuracao institucional
- a estrategia incremental adotada usa model proprio de auditoria, com registro explicito nas views de create, update e delete, sem `signals`
- o log agora armazena acao executada, modelo afetado, id do registro, data/hora, usuario responsavel quando disponivel e campos alterados em formato estruturado
- no estado atual do projeto, `request.user` nao esta integrado como regra operacional propria do modulo, entao o usuario da auditoria deve ser tratado como opcional na primeira versao
- a comparacao de mudancas deve priorizar diff simples de campos relevantes no backend, evitando reestruturacao ampla do dominio

## Governanca permanente entre chats

- a continuidade entre chats agora esta formalmente consolidada no projeto com base nos quatro documentos-base permanentes: `docs/CEREBRO_PROJETO.md`, `docs/STATE.md`, `docs/CODEX_RESULTADO.md` e `docs/ROADMAP_FINANCEIRO.md`
- essa continuidade deve preservar historico documental, usar o repositorio como fonte final de verdade e manter atualizacoes por acrescimo, consolidacao ou ajuste cirurgico

## Validacao local

- Nao foi possivel executar `py manage.py check` com sucesso no ambiente atual.
- Motivo: o interpretador disponivel nao tem o pacote `django` instalado.
- Foi possivel validar a sintaxe dos arquivos Python via `py -m compileall financeiro`.
- Assim, a estrutura foi deixada pronta, mas a validacao automatica do runtime ainda depende de um ambiente com as dependencias instaladas.
