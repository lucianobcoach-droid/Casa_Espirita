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
- Hoje a navegacao principal do `financeiro`, no desktop, passa a ficar priorizada na sidebar do modulo.
- A topbar do `financeiro` agora permanece como barra utilitaria minima e camada de transicao, sem substituir abruptamente a navegacao existente no mobile.
- Hoje ja existe sidebar/menu lateral implementada no shell do `financeiro` em desktop e mobile, com drawer funcional no mobile e comportamento proprio separado do desktop.
- Hoje nao existe shell visual compartilhado entre `financeiro`, `biblioteca` e `configuracoes`.
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
- O resumo por periodo agora tambem recebeu essa frente visual, com cabecalho mais compacto, filtros mais densos e blocos de totais reorganizados em hierarquia visual mais enxuta e consistente com a base compartilhada do modulo.
- A prestacao de contas agora tambem recebeu essa frente visual, com cabecalho, filtros e blocos de totais mais compactos e consistentes com o resumo por periodo, sem alterar calculos ou agrupamentos.
- A tela de auditoria do financeiro agora tambem recebeu refinamento visual incremental, com cabecalho alinhado ao padrao compartilhado, filtros mais compactos e tabela mais densa para leitura em desktop 100%, sem alterar a leitura simples da auditoria.
- Nos relatorios e extratos do financeiro, as datas visiveis ao usuario agora devem seguir apresentacao em `dd/mm/aaaa`, incluindo rotulos de periodo e metadados principais de emissao.
- O `financeiro` permanece como o app com base visual mais madura do projeto.
- A frente de governanca visual do projeto foi oficialmente aberta a partir do mapeamento estrutural da interface atual.
- A referencia inicial de menu lateral padronizado inspirado no Tabler agora ja foi implementada no shell do `financeiro`, enquanto expansoes para outros apps e refinamentos adicionais continuam dependentes de etapas futuras proprias.
- O shell do `financeiro` agora funciona como referencia inicial da governanca visual do projeto, mas ainda nao existe base compartilhada equivalente entre os demais apps.
- O shell visual do `financeiro` em `financeiro/base.html` agora concentra de forma mais explicita a base compartilhada de topbar, container principal, mensagens globais e classes reutilizaveis do modulo.
- A sigla visual da marca no shell do `financeiro` nao fica mais fixa em `CE`: ela agora deriva das iniciais do nome da `ConfiguracaoInstitucional` ativa/padrao, com fallback seguro para `CE` quando esse nome nao estiver preenchido.
- A preparacao tecnica dessa frente agora tambem consolidou no shell compartilhado componentes-base como cabecalho de pagina, callouts, chips de resumo, blocos auxiliares do rateio e a inicializacao JS reutilizavel do dropdown de contas.
- A evolucao futura da sidebar ainda depende de reduzir variacoes locais restantes entre templates importantes, especialmente em formularios complexos, extrato e relatorios, e de fechar a experiencia mobile de forma segura.
- `financeiro/base.html` agora tambem possui estrutura explicita de app shell com area utilitaria superior, area preparada para sidebar e area principal de conteudo.
- Nesta primeira microetapa da futura sidebar, a topbar atual foi preservada como navegacao principal em convivio controlado com uma sidebar estrutural secundaria no desktop, sem migracao integral da navegacao.
- O `financeiro-page-header` das paginas foi preservado como camada contextual interna, separada da navegacao principal do shell.
- Na microetapa seguinte da sidebar, o desktop do `financeiro` passou a usar a lateral como navegacao principal, com grupos coerentes, item ativo visivel e topbar reduzida a funcao utilitaria minima.
- Na microetapa seguinte, a navegacao mobile do `financeiro` passou a abrir a sidebar em modo drawer/offcanvas, com overlay, botao de abertura na topbar e fechamento previsivel sem depender de hover.
- A topbar mobile do `financeiro` agora permanece apenas como barra compacta de contexto e controle do drawer lateral.
- A experiencia mobile da sidebar ainda nao foi refinada visualmente em todos os detalhes, mas o fluxo base de abrir, fechar e navegar ja ficou funcional e preservou a estabilidade do desktop.
- Na microetapa seguinte, a sidebar do `financeiro` passou a usar grupos expansivos/recolhiveis, com grupo ativo aberto automaticamente e item ativo destacado com mais clareza.
- O shell do `financeiro` agora trabalha com menos texto explicativo permanente no topo e na lateral, reduzindo ruido visual e aproximando a navegacao de um painel administrativo mais silencioso.
- Nesta fase, a ergonomia da sidebar ficou mais escalavel: no shell renderizado, um grupo aberto por vez simplifica a leitura no desktop e segue funcional por clique/toque no mobile.
- Na microetapa seguinte, o shell compartilhado do `financeiro` recebeu acabamento visual final na sidebar, na topbar e no drawer mobile, com contraste funcional mais claro e menos peso visual.
- A sidebar desktop passou a trabalhar com largura, espacamentos e estados ativos mais maduros, deixando grupo ativo, item ativo e grupo expandido mais legiveis sem aumentar o ruido.
- O drawer mobile ficou visualmente mais leve e ergonomico, com largura mais controlada, overlay menos pesado e topbar ainda mais discreta.
- Foi identificada uma limitacao real de responsividade no shell do `financeiro`: parte do conteudo podia ficar cortada a direita por combinacao de larguras estruturais baseadas em `100vw` e comportamento de box model no shell.
- A correcao estrutural seguinte removeu esse acoplamento de largura no `financeiro/base.html`, passou a usar `width: ... 100%` nos wrappers principais, reforcou `min-width: 0`/`max-width: 100%` no conteudo principal e deixou a area central com `overflow-x: auto` quando necessario.
- Com essa correcao, o conteudo principal do `financeiro` deixa de depender de corte invisivel: tabelas, filtros e blocos largos passam a coexistir com a sidebar sem perder acessibilidade por rolagem horizontal quando precisarem exceder a largura disponivel.
- Na microetapa seguinte, a sidebar do `financeiro` passou a poder ser recolhida e expandida no desktop, liberando mais area util de trabalho sem alterar o comportamento do drawer mobile.
- O shell agora possui dois estados de navegacao lateral no desktop: expandido e recolhido real, com adaptacao correspondente da area principal.
- O estado da sidebar no desktop passou a ser persistido no navegador para manter a preferencia do usuario entre recarregamentos.
- No modo recolhido real da sidebar no desktop, o menu lateral desaparece do layout e deixa de exibir grupos, links, abreviacoes ou submenus.
- Quando a lateral esta recolhida, permanece apenas um botao de expandir encaixado na barra utilitaria do shell do desktop, com icone discreto, `title` e `aria-label`, sem sobrepor titulo, subtitulo ou conteudo principal.
- Os controles de recolher e reabrir a lateral no desktop agora compartilham linguagem visual mais uniforme, com dimensoes, borda e sombra discretas coerentes com os demais controles utilitarios do shell.
- O controle da lateral no desktop agora usa um unico slot fixo na barra utilitaria, ao lado da marca do modulo, sem trocar de lado entre os estados expandido e recolhido.
- A estrategia de rolagem vertical do shell do `financeiro` foi simplificada para evitar concorrencia entre a pagina e a navegacao lateral no desktop; a sidebar deixa de manter scrollbar proprio nessa faixa e a leitura volta a depender de uma rolagem principal unica.
- O shell do `financeiro` agora tambem usa respiro lateral mais explicito na barra utilitaria e na area principal de conteudo, evitando que a tela fique colada demais nas bordas em desktop sem desperdiçar largura util.
- Foi identificada uma regressao real na impressao/PDF do extrato apos a evolucao do shell com sidebar: o layout podia sair espremido a esquerda por heranca indevida da estrutura principal de grid/largura/overflow do shell.
- A correcao seguinte passou a isolar o extrato do shell no modo print, removendo a influencia de sidebar, topbar, wrappers de overflow e tracks do grid lateral na composicao impressa.
- O toggle da lateral no desktop tambem passou a usar apenas icone visivel, mantendo acessibilidade por `title`, `aria-label` e texto apenas para leitor de tela.
- `Resumo` e `Prestacao de Contas` agora tambem possuem acao lateral de `Imprimir`, reutilizando o isolamento de print do shell para nao herdar sidebar, topbar ou wrappers de overflow na versao impressa.
- A exibicao visivel das categorias no modulo financeiro foi simplificada: quando a natureza ja esta clara pelo contexto da tela, pelo agrupamento ou por `Tipo`, a interface passou a mostrar apenas o nome da categoria, sem prefixos longos como `Receita - ...` ou `Despesa - ...`.
- A validacao manual real de impressao de `Extrato`, `Resumo` e `Prestacao de Contas` foi concluida com sucesso em navegador/PDF real nesta base atual, sem regressao visual relevante de largura util, margens ou heranca indevida do shell.
- Os relatorios operacionais do `financeiro` ainda nao exibem logo institucional propria; hoje essa identidade visual dinamica segue concentrada no recibo e pode evoluir em etapa futura especifica.
- Extrato, Resumo e Prestacao de Contas agora tambem compartilham margem de impressao mais consistente, com pequeno respiro interno padronizado na folha e sem perder o isolamento do shell no modo print.
- A primeira onda real de padronizacao visual do `financeiro` agora foi aplicada nas telas-chave mais seguras do modulo: listagem de lancamentos, formulario de lancamento e auditoria.
- Essas tres telas passaram a compartilhar com mais consistencia o mesmo vocabulário de header/topo do shell do modulo, com titulo, subtitulo e acoes laterais alinhados ao padrao reutilizavel de `financeiro/base.html`.
- A primeira onda visual agora tambem alcancou `conta_extrato.html`, `resumo.html` e `prestacao_contas.html`, alinhando topo, subtitulo, acoes laterais e hierarquia dos blocos principais ao shell compartilhado do modulo.
- `lancamento_rateio_grupo_form.html` agora tambem passou a conversar melhor com o shell compartilhado do modulo, especialmente no header/topo e na navegacao de apoio do fluxo coordenado.
- Com essa etapa, a primeira onda de padronizacao visual do `financeiro` fica fechada nas telas operacionais centrais, restando antes da pre-etapa tecnica da sidebar apenas consolidacoes internas adicionais do shell e eventual limpeza de variacoes locais residuais.
- Na validacao tecnica local dessa primeira onda visual, as telas centrais do modulo responderam corretamente com o shell compartilhado, e a abertura da edicao coordenada do grupo rateado foi estabilizada apos remover um acesso indevido ao campo `categoria` no formulario especializado do grupo.
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
- categoria pai agora nao pode ser usada em lancamento comum nem em rateio; apenas subcategoria com `categoria_pai` preenchida pode ser vinculada ao lancamento
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
- no rateio inicial e na edicao coordenada do grupo, categoria pai tambem fica bloqueada; apenas subcategorias validas podem compor as linhas finais
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
- a obrigatoriedade de `data_pagamento` agora tambem foi consolidada no `clean()` de `LancamentoFinanceiro`, subindo de regra apenas operacional do formulario para regra estrutural de validacao da aplicacao
- nesta etapa, o campo continua aceitando `null/blank` na modelagem de banco por compatibilidade com bases legadas, mas novas gravacoes e atualizacoes passam a exigir `data_pagamento` no nivel da aplicacao
- a obrigatoriedade final de `pessoa` e `categoria` permanece condicional na camada da aplicacao
- a regra de hierarquia de categoria agora tambem foi consolidada na camada da aplicacao: tentativas de gravar `LancamentoFinanceiro` com categoria pai passam a falhar mesmo fora do formulario
- o formulario de lancamento agora pode consultar e exibir os ultimos 5 lancamentos da `pessoa` selecionada
- o bloco de historico do favorecido mostra data, tipo, descricao, valor, categoria e `numero_documento` quando existir
- o historico do favorecido acompanha a selecao da pessoa no autocomplete sem alterar a logica atual do campo
- `data_competencia` deve ser validada antes da gravacao
- `data_pagamento` nao pode ser anterior a `data_competencia`
- a primeira versao da auditoria do financeiro agora registra create, update e delete de `LancamentoFinanceiro` em model proprio
- o log da primeira versao armazena acao, modelo afetado, id do registro, data/hora, usuario quando disponivel e campos alterados em JSON simples
- o create comum, o create com rateio, a edicao individual de linha rateada e o delete agora geram eventos explicitos de auditoria
- a auditoria agora tambem registra create, update e delete de `ContaFinanceira`, mantendo o mesmo padrao incremental ja usado em `LancamentoFinanceiro`
- a auditoria agora tambem registra create, update e delete de `PessoaFinanceira`, mantendo o mesmo padrao incremental ja usado nas demais entidades ja auditadas
- a auditoria agora tambem registra create, update e delete de `CategoriaFinanceira`, mantendo o mesmo padrao incremental ja usado nas demais entidades ja auditadas
- a auditoria agora tambem registra create, update e delete de `CentroCusto`, mantendo o mesmo padrao incremental ja usado nas demais entidades ja auditadas
- a auditoria agora tambem registra create, update e delete de `AssinaturaInstitucional`, mantendo o mesmo padrao incremental ja usado nas demais entidades ja auditadas
- a auditoria agora tambem registra create, update e delete de `ConfiguracaoInstitucional`, mantendo o mesmo padrao incremental ja usado nas demais entidades ja auditadas
- a auditoria ja possui captura inicial em `LancamentoFinanceiro`, `ContaFinanceira`, `PessoaFinanceira`, `CategoriaFinanceira`, `CentroCusto`, `AssinaturaInstitucional` e `ConfiguracaoInstitucional`, tela propria de leitura minima e filtros simples
- nesta primeira expansao, a trilha inicial de auditoria ja cobre as entidades operacionais e institucionais hoje existentes no modulo financeiro
- a leitura minima da auditoria agora existe em tela propria, ordenada por `data_hora` decrescente e abrangendo as entidades ja auditadas do modulo financeiro
- a leitura inicial da auditoria mostra data/hora, acao, modelo, id do registro, usuario e campos alterados em resumo estruturado simples
- a leitura da auditoria agora possui filtros simples por acao, periodo inicial/final, id do registro e usuario, mantendo ordenacao por `data_hora` decrescente
- o filtro por usuario usa os usuarios ja presentes na trilha atual de auditoria e continua opcional, preservando leitura simples da tela
- nesta primeira leitura operacional da auditoria, ainda nao existem filtros complexos nem paginacao avancada
- o cabecalho visual da tela de auditoria agora usa estrutura mais estavel para evitar sobreposicao entre titulo, subtitulo e acoes laterais
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
- a coluna `Descricao` do extrato voltou a ficar limpa, sem linha secundaria de `Favorecido` ou `Categoria`
- o extrato agora usa coluna propria de `Favorecido`, sem reintroduzir `Categoria` na tabela nesta etapa
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
- Fica oficialmente aberta, apenas em nivel documental e sem implementacao nesta etapa, a frente estrutural futura de usuarios, autenticacao, perfis e permissoes do projeto, com separacao prevista entre administracao global e regras especificas dos modulos.
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

- Foi possivel executar `py manage.py check` com sucesso no ambiente atual.
- Foi possivel validar a sintaxe dos arquivos Python via `py -m compileall financeiro casa_espirita`.
- A validacao tecnica local do modulo hoje pode combinar checagem do Django, compilacao e requests controlados via `Client(HTTP_HOST='localhost')`.

## Acabamento documental atual dos relatorios principais

- `Extrato`, `Resumo` e `Prestacao de Contas` agora compartilham uma base visual documental mais coerente para impressao/PDF, com cabecalho comum, hierarquia tipografica mais clara e melhor aproveitamento da folha.
- O padrao atual de identidade institucional dos relatorios passou a priorizar `logo_url` da `ConfiguracaoInstitucional` ativa/padrao quando existir e, sem logo, cair apenas para o nome institucional, sem usar sigla como pseudo-logo.
- `Prestacao de Contas` ganhou bloco final de assinatura mais formal e menos generico, ainda propositalmente simples nesta etapa.
- As margens de impressao e o respiro interno dos relatorios foram reforcados nesta etapa, com ganho adicional de aproveitamento visual no `Extrato`.
- Nesta microetapa nao houve alteracao de regra de negocio, calculos, filtros nem conteudo funcional dos relatorios.
- Foi possivel executar `py manage.py check`, validar localmente as rotas `/financeiro/extratos/`, `/financeiro/resumo/` e `/financeiro/prestacao-contas/` com status `200` e regenerar PDFs reais dos tres relatorios em `tmp/print-validation/`.
- A validacao visual fina humana do acabamento final continua podendo ser revisitada depois por uso real, especialmente quando entrarem logo institucional e configuracao futura de assinaturas por relatorio.

## Acabamento documental atual do recibo e do saldo acumulado do extrato

- o recibo passou a ter topo mais institucional e menos fragmentado, com `RECIBO` como titulo principal, numero em linha secundaria limpa e maior presenca da logo quando existir
- no recibo, o nome institucional agora aparece apenas como fallback discreto quando nao houver logo utilizavel; quando a logo esta presente, ela assume a identificacao visual principal do topo
- a mensagem principal do recibo ganhou centralidade e maior peso documental, deixando de parecer observacao administrativa secundarizada
- a data deixou de aparecer de forma redundante no topo do recibo, permanecendo apenas no corpo documental
- no extrato, o `saldo acumulado` passou a usar cor coerente com o sinal do valor: positivo com leitura de receita, negativo com leitura de despesa e neutro com tom sobrio
- numa microetapa posterior de ajuste fino, o `saldo acumulado` deixou de usar negrito e passou a manter apenas a leitura por cor, preservando `saldo inicial` e `saldo final` como linhas destacadas em negrito
- numa microetapa posterior de refinamento documental do `Extrato`, o topo impresso ficou mais leve, o `saldo anterior` saiu do cabecalho e permaneceu apenas no corpo da tabela, e a tabela passou a ter zebra leve e separacao visual melhor entre `saldo acumulado` e `observacoes`
- numa microetapa posterior de fechamento visual do `Extrato`, o cabecalho impresso foi simplificado para uma linha documental mais seca, os rotulos do print ficaram mais curtos, as linhas e bordas da tabela ficaram mais discretas e a distribuicao de colunas passou a reduzir melhor a sensacao de aperto entre `Favorecido`, `Tipo`, `Saldo acumulado` e `Observacoes`
- numa microetapa posterior de ajuste fino final do `Extrato`, o periodo do cabecalho impresso foi padronizado em `dd/mm/aaaa` e a grade da tabela perdeu as divisorias verticais, mantendo apenas linhas horizontais mais finas e discretas para leitura documental leve
- numa microetapa posterior de fechamento visual complementar do `Extrato`, a logo foi removida apenas do cabecalho impresso desse relatorio e substituida pelo nome institucional em negrito com leitura limpa, enquanto as linhas horizontais da tabela foram afinadas novamente para reduzir ainda mais o peso da grade
- com a validacao humana final aprovada nesta base, o ciclo visual do `Extrato` impresso pode ser tratado como encerrado para a branch atual, permanecendo apenas eventual curadoria futura por uso real sem reabrir regra de negocio
- nesta microetapa nao houve alteracao de regra de negocio, calculos, filtros nem conteudo funcional de recibo ou extrato
- foi possivel executar `py manage.py check`, validar localmente `/financeiro/lancamentos/1/recibo/` e `/financeiro/extratos/?conta=3` com status `200` e gerar PDFs reais atualizados em `tmp/print-validation/`

## Frentes futuras abertas apenas em nivel documental

- fica oficialmente registrada, apenas em nivel documental e sem implementacao nesta etapa, a futura frente de configuracao da paleta geral do sistema, com derivacao coerente de cores a partir de uma cor principal
- fica oficialmente registrada, apenas em nivel documental e sem implementacao nesta etapa, a futura frente de log de acesso ao sistema, separada da auditoria funcional ja existente no `financeiro`
- fica registrada como revisao futura de navegacao, sem decisao de mudanca nesta etapa, a necessidade de reavaliar a posicao do `Extrato` na navegacao do modulo quando houver contexto suficiente de uso real
