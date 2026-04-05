# STATE

Data de atualizacao: 2026-04-04

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
- A listagem principal de lancamentos agora usa ordem padrao mais intuitiva por data principal mais recente primeiro, priorizando `data_pagamento` quando existir e usando `data_competencia` como fallback, com desempate por `pk` mais recente, aplicada diretamente na view para evitar impacto nas demais consultas do modulo.
- As telas de `Resumo` e `Prestacao de Contas` agora possuem controle de exibicao apenas para o bloco de centro de custo, sem alterar os totais gerais do relatorio.
- A tela de `Prestacao de Contas` recebeu refinamento visual especifico para impressao em A4.
- A `Prestacao de Contas` agora tem apresentacao mais formal, com menos aparencia de dashboard.
- As telas de `Extratos` e `Resumo` agora tem impressao mais limpa, com melhor alinhamento de valores e identificacao do relatorio.
- O menu superior do financeiro foi reorganizado para separar `Financeiro`, `Lancamentos`, `Extratos`, `Relatorios` e `Cadastros`.
- Hoje a navegacao principal do `financeiro`, no desktop, passa a ficar priorizada na sidebar do modulo.
- A topbar do `financeiro` agora permanece como barra utilitaria minima e camada de transicao, sem substituir abruptamente a navegacao existente no mobile.
- Hoje ja existe sidebar/menu lateral implementada no shell do `financeiro` em desktop e mobile, com drawer funcional no mobile e comportamento proprio separado do desktop.
- Na primeira passada controlada da nova frente de leveza do menu lateral, o shell do `financeiro` passou a usar casca visual mais discreta no desktop, com barra utilitaria menos carregada, header interno da sidebar mais leve e item ativo mais elegante, sem alterar JS, drawer, rotas, `aria` ou a mecanica de expansao dos grupos.
- No ajuste fino seguinte dessa mesma frente, o controle de recolher/expandir lateral no desktop voltou a uma linguagem mais coerente com o tema, e a hierarquia tipografica do menu foi aliviada para concentrar negrito forte apenas no item ativo.
- No ajuste fino final desta rodada do shell lateral, o grupo expandido passou a usar destaque mais suave, o titulo `Navegacao principal` perdeu agressividade visual e o toggle lateral ficou ainda mais integrado ao shell, preservando negrito forte apenas no item ativo.
- Foi registrada como frente futura, ainda sem implementacao completa, a importacao/exportacao de lancamentos, incluindo importacao em massa com acao para baixar planilha modelo no layout proprio do sistema, validacao previa de colunas e tipos, pre-visualizacao antes de confirmar, tratamento de linhas invalidas e duplicidades, e exportacao de consultas/listagens com respeito aos filtros aplicados.
- A fase 1 dessa frente foi aberta com uma pagina propria de `Importacao / Exportacao de Lancamentos`, reunindo upload preparado para fase futura, link de `Baixar planilha modelo`, acao visual de exportacao e um bloco curto de ajuda operacional, ainda sem implementar upload/importacao de arquivo, pre-validacao em massa, tratamento de duplicidades ou exportacao completa.
- O layout inicial da planilha modelo foi definido com as colunas `tipo`, `status`, `descricao`, `valor`, `data_competencia`, `data_pagamento`, `pessoa_nome`, `categoria_nome`, `centro_custo_nome`, `conta_nome`, `conta_destino_nome`, `numero_documento` e `observacoes`, nessa ordem.
- O download da planilha modelo da importacao/exportacao passou de CSV para XLSX, com a aba `Modelo` contendo apenas a linha de cabecalhos oficiais e a aba `Instruções` com orientacoes praticas de preenchimento, sem linhas de exemplo e sem abrir ainda a importacao real do arquivo ou a exportacao completa.
- A exportacao real de lancamentos em XLSX passou a ficar operacional na propria tela de `Lancamentos financeiros`, com a acao `Exportar` respeitando os filtros GET ativos da listagem e gerando uma aba `Lancamentos` com cabecalhos amigaveis ao usuario, datas em `dd/mm/aaaa` e valores com virgula decimal; a pagina separada agora fica visualmente focada em importacao futura e download da planilha modelo, que permanece com layout tecnico estavel para posterior leitura do arquivo.
- A pagina de `Importacao` agora permite enviar um XLSX, valida a estrutura do arquivo e o conteudo das linhas da aba `Modelo`, ignora linhas totalmente vazias, valida campos por linha apenas contra cadastros ja existentes, mostra na propria tela o total de linhas lidas/validas/importadas/com erro e exibe erros por linha/campo com rotulos amigaveis ao usuario, sem expor nomes tecnicos de campo.
- A importacao de lancamentos passou a aceitar e orientar prioritariamente datas em `dd/mm/aaaa`, mantendo `AAAA-MM-DD` apenas como formato tambem tolerado internamente para leitura do arquivo; a aba `Instruções` da planilha modelo e as mensagens de erro de data foram alinhadas a esse formato visual.
- A primeira versao real da importacao de lancamentos foi implementada com politica all-or-nothing: se houver qualquer erro em qualquer linha, nenhuma linha e importada; se tudo estiver valido, todos os lancamentos sao gravados em uma unica transacao. O fluxo continua sem criacao automatica de pessoas, categorias, contas ou centros de custo a partir do arquivo, e preview detalhado antes de gravar, importacao de cadastros auxiliares e eventual importacao parcial permanecem apenas como fases futuras.
- O retorno visual da importacao agora destaca o resultado em um banner superior de sucesso ou erro, mantem os totais em cards de leitura rapida, apresenta cada linha com erro em blocos mais escaneaveis e, quando ha inconsistencias, oferece download de relatorio XLSX com `Linha`, `Campo`, `Mensagem`, `Como corrigir` e `Valor informado`, sem alterar a politica all-or-nothing nem expor nomes tecnicos de campo para o usuario final.
- A listagem de lancamentos passou a ter fase 1 de edicao em lote com selecao multipla por checkbox, opcao de marcar todos os itens visiveis, exclusao dos selecionados com confirmacao, alteracao transacional de `status` dos selecionados e retorno preservando os filtros GET ativos.
- Na listagem de lancamentos, rateio passou a ser exibido como grupo visual unico por `grupo_rateio`, com linha-resumo expandivel mais limpa, detalhes internos visiveis apenas ao abrir o grupo, valor total consolidado no resumo e checkbox de selecao em lote mirando o grupo inteiro; esta decisao e apenas de UX da listagem, nao altera o modelo fisico e nao foi aplicada ao extrato, prestacao, recibo, auditoria nem demais telas nesta microetapa.
- Em ajuste fino posterior dessa mesma listagem, a coluna `Descricao` foi padronizada com um mesmo wrapper interno e um slot fixo para o toggle/placeholder, alinhando visualmente o inicio do texto em lancamentos comuns, rateios fechados e rateios expandidos sem alterar a logica de agrupamento.
- Na rodada atual de UX da listagem, a coluna de acoes passou a usar slots fixos por funcao para alinhar `Recibo`, `Clonar`, `Editar` e `Excluir` entre linhas comuns e rateios; `Recibo` ficou contextual e aparece apenas em receitas comuns, enquanto a coluna `Descricao` passou a truncar o texto com reticencias e manter o conteudo completo em tooltip.
- Na sequencia dessa mesma frente, os rotulos visiveis de acoes, `Tipo` e `Status` na listagem foram compactados para iconografia com `title` e `aria-label`, preservando acessibilidade e liberando mais espaco visual para a coluna `Pessoa`, sem alterar regras de negocio nem o agrupamento de rateio.
- A listagem de lancamentos agora tambem permite ordenacao por coluna em `Descricao`, `Tipo`, `Status`, `Valor`, `Pessoa` e `Data`, com icone discreto no cabecalho, preservacao dos filtros GET ativos, manutencao do agrupamento visual de rateio e fallback para a ordenacao padrao por data principal mais recente quando nenhum criterio manual e escolhido.
- Nesta consolidacao documental, ficou registrada como proxima prioridade funcional do sistema a frente de `permissoes/autenticacao`, com configuracao de perfis em hierarquia `Modulo` > `Tela/Recurso` > `Acao`, a ser iniciada apenas apos a estabilizacao do `financeiro` como base e sem ser tratada como ajuste isolado de uma tela.
- Tambem foi formalizada uma checklist permanente de revisao para toda nova implementacao, cobrindo navegacao/menu/atalhos, permissoes, impacto em listagens, formularios, importacao/exportacao, auditoria/log, ajuda/manual do usuario, aderencia ao padrao UX/layout e atualizacao obrigatoria dos docs-base.
- Foi criado `docs/CHECKLIST_EVOLUCAO_SISTEMA.md` como checklist operacional permanente para aplicar essa revisao transversal a cada nova funcionalidade, sem transformar `STATE` em backlog puro.
- Ficaram abertas como proximas frentes estruturais/documentais a auditoria de UX entre telas existentes, a consolidacao de um padrao visual/funcional transversal, a padronizacao das melhorias aprovadas no `financeiro` para outros modulos, a evolucao do cadastro de logo com URL ou upload local e preview, e a expansao futura de acoes em lote para outros cadastros.
- Foi criado `docs/PADRAO_UX_SISTEMA.md` como documento enxuto inicial para registrar o padrao UX/layout do sistema sem substituir os quatro docs-base oficiais.
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
- No MVP de regras automaticas do lancamento, o check `Salvar como regra automatica` foi reposicionado para a linha final de acoes do formulario, com visual discreto e ocultacao no modo rateio, e a sugestao de regra deixou de aparecer em bloco inferior separado: agora o dropdown de sugestoes fica acoplado ao proprio campo `Descricao`, com o autocomplete nativo do navegador desativado no form/campo para evitar sobreposicao visual, e a selecao aplica o payload imediatamente no formulario por `mousedown` preventivo e selecao explicita da `option` nos campos com autocomplete.
- No formulario de lancamento, o campo `Categoria`/`Subcategoria` passou a ser filtrado pelo `tipo` selecionado: `receita` mostra apenas subcategorias de receita, `despesa` mostra apenas subcategorias de despesa, e `transferencia` segue sem exigir categoria; o mesmo recorte foi aplicado ao autocomplete e as linhas de rateio.
- No autocomplete AJAX de `Categoria`, foi removido na pratica o corte curto herdado da classe base para essa view especifica, porque o limite de 10 resultados omitia subcategorias validas quando havia mais de 10 opcoes compativeis para o tipo selecionado.
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
- numa microcorrecao visual posterior, o `Extrato` impresso aproximou ainda mais a tabela da grade leve usada como referencia em telas operacionais do modulo: o cabecalho da tabela passou a ficar sem linha visivel no print, as linhas horizontais do corpo foram afinadas de novo e a zebra ficou ainda mais sutil, sem reabrir a frente como pendencia estrutural
- na tela de edicao coordenada do grupo rateado, a experiencia operacional passou a separar com mais clareza o resumo do grupo, os dados comuns do documento, as linhas do rateio e as acoes finais, com menos ruido textual e com retornos mais previsiveis para listagem e linha representativa
- a leitura operacional do grupo rateado fora da tela coordenada tambem avancou: a listagem principal passou a sinalizar melhor quando a linha pertence a um grupo e que a acao de edicao abre o fluxo coordenado, enquanto a edicao individual passou a distinguir com mais clareza quando revisar apenas a linha e quando seguir para o grupo inteiro
- o formulario principal de lancamento agora tambem apresenta melhor a transicao entre lancamento comum e `Lancamento com rateio`, com hierarquia mais clara entre dados comuns do documento, `valor total do documento` e linhas do rateio, sem alterar a mecanica atual do payload nem o comportamento do formulario comum
- numa microetapa posterior de enxugamento textual, o formulario principal de lancamento manteve a mesma estrutura operacional, mas passou a usar textos mais curtos no subtitulo da pagina, no bloco `Modo do lancamento`, no callout de `valor total do documento` e na introducao do bloco `Rateio simples`, reduzindo repeticao sem perder a clareza minima do fluxo
- numa microetapa posterior de enxugamento mais incisivo, o formulario principal reduziu ainda mais o texto fixo da entrada do rateio, simplificou fortemente os blocos comparativos e passou a concentrar apenas em ajuda discreta com icone `i` a orientacao excepcional realmente necessaria sobre ativacao do rateio e fechamento pelo total do documento
- numa microetapa posterior de faxina fina, `financeiro/templates/financeiro/lancamento_form.html` removeu descricoes de secao redundantes, simplificou ainda mais o bloco `Modo do lancamento`, reduziu duplicidades no `valor total do documento`, secou a abertura das linhas do rateio e padronizou melhor rotulos e acentuacao visiveis, mantendo o `i` apenas em poucos pontos realmente uteis
- numa microetapa posterior de acabamento fino, a mesma tela recebeu ajuste final de consistencia textual e visual: o subtitulo da pagina foi removido, o `i` ficou mais padronizado e discreto, `Linhas do rateio` perdeu ajuda redundante, o bloco `Valor total do documento` ficou visualmente mais leve e a rotulagem visivel passou a ficar mais consistente na propria interface
- numa microetapa posterior de acabamento fino complementar, `financeiro/templates/financeiro/lancamento_form.html` alinhou melhor o componente `i` em tamanho, contraste e espacamento, compactou discretamente os blocos `Modo do lancamento` e `Valor total do documento`, aliviou o estado vazio do historico e padronizou o bloco final como leitura de `pessoa`, sem alterar regra de negocio nem comportamento do formulario
- numa microetapa posterior curtissima, a mesma tela consolidou a rotulagem visivel de `Valor total do documento` e passou a usar o `i` em italico, preservando o mesmo padrao de alinhamento, contraste e espacamento ja adotado
- numa microetapa posterior de polimento visual residual, a mesma tela deu um pouco mais de legibilidade ao `i`, aliviou discretamente o peso visual do bloco `Valor total do documento`, amarrou melhor `Adicionar linha` e `Remover` e reduziu mais a carga visual do estado vazio de `Ultimos lancamentos da pessoa`, sem alterar comportamento funcional
- numa microetapa posterior de reorganizacao visual, `financeiro/templates/financeiro/lancamento_form.html` passou a operar com menos sensacao de blocos independentes: os wrappers do formulario ficaram mais leves, os espacamentos foram compactados, `Adicionar linha` subiu para o cabecalho das `Linhas do rateio` e o bloco `Valor total do documento` passou a ler melhor como parte do mesmo fluxo continuo de cadastro
- numa microetapa posterior de compactacao espacial, `financeiro/templates/financeiro/lancamento_form.html` reduziu mais a distancia entre blocos internos, aproximou linhas de inputs, baixou paddings da ficha principal e do rateio e deixou o historico da pessoa mais secundario, reforcando a sensacao de lancamento rapido e sequencial sem alterar nenhuma regra de negocio
- numa microetapa posterior de compactacao mais incisiva, a mesma tela baixou novamente paddings, margens e respiros entre titulos, linhas de inputs, blocos internos e acoes finais, enfraquecendo mais a leitura de seções separadas e aproximando o formulario de um fluxo sequencial de lancamento
- numa microetapa posterior de ajuste de grade e proporcao, a mesma tela passou a trabalhar com larguras mais firmes nas linhas de identificacao, valores e complementares, reduzindo ilhas visuais entre campos e reforcando a leitura por linhas de preenchimento em vez de faixas altas separadas
- nesta microetapa nao houve alteracao de regra de negocio, calculos, filtros nem conteudo funcional de recibo ou extrato
- foi possivel executar `py manage.py check`, validar localmente `/financeiro/lancamentos/1/recibo/` e `/financeiro/extratos/?conta=3` com status `200` e gerar PDFs reais atualizados em `tmp/print-validation/`

## Frentes futuras abertas apenas em nivel documental

- fica oficialmente registrada, apenas em nivel documental e sem implementacao nesta etapa, a futura frente de configuracao da paleta geral do sistema, com derivacao coerente de cores a partir de uma cor principal
- fica oficialmente registrada, apenas em nivel documental e sem implementacao nesta etapa, a futura frente de log de acesso ao sistema, separada da auditoria funcional ja existente no `financeiro`
- fica registrada como revisao futura de navegacao, sem decisao de mudanca nesta etapa, a necessidade de reavaliar a posicao do `Extrato` na navegacao do modulo quando houver contexto suficiente de uso real

## Frente transversal de padronizacao de UX e comunicacao operacional

- fica oficialmente aberta, a partir desta etapa, a frente transversal de padronizacao de UX e comunicacao operacional do sistema, iniciada pelo `financeiro` e orientada pela leitura de fluxo continuo, texto fixo minimo, uso raro e padronizado do `i` e consistencia de linguagem visivel
- no estado atual do `financeiro`, `lancamento_form.html` e a referencia mais avancada dessa direcao, enquanto `lancamento_rateio_grupo_form.html` e `lancamento_list.html` ja possuem base intermediaria mais alinhada ao padrao
- as telas de relatorio impresso e recibo permanecem mais maduras no seu proprio eixo documental, sem substituir a necessidade de padronizacao operacional das telas transacionais do modulo
- a auditoria inicial desta frente mostrou que as listas e cadastros mais antigos do `financeiro`, assim como a home do modulo e a tela de auditoria, ainda concentram parte relevante da segmentacao visual excessiva, subtitulos explicativos, estados vazios pesados e inconsistencias de linguagem/acentuacao
- a continuidade correta dessa frente deve acontecer por microetapas, priorizando primeiro as telas transacionais e de consulta do `financeiro`, depois os cadastros auxiliares do proprio modulo e, so depois, a propagacao do padrao para outros apps do sistema
- na primeira microetapa executada dessa frente, `financeiro/templates/financeiro/home.html` deixou de usar hero com subtitulo generico e passou a organizar seus atalhos em grupos operacionais mais curtos e legiveis, com linguagem visivel e acentuacao mais consistentes e sem alterar nenhuma rota ou acao do modulo
- em decisao estrutural posterior, a `home` do `financeiro` deixou de ser a entrada principal do modulo: a raiz `/financeiro/` agora deve abrir diretamente a listagem de lancamentos, enquanto a antiga home passa a existir apenas como rota secundaria explicita para compatibilidade e referencia temporaria
- na microetapa seguinte da auditoria transversal, `financeiro/templates/financeiro/auditoria_lancamento_list.html` passou a trabalhar com topo mais seco, retorno alinhado a `Lancamentos`, filtros visualmente mais maduros, rotulos acentuados de forma consistente e estado vazio mais limpo, sem alterar filtros, ordenacao nem a mecanica simples da leitura da auditoria
- antes da nova frente de POC visual, foi criado um ponto de restauracao explicito em Git para preservar o estado atual aprovado e reduzir risco de retrabalho sobre a base do `financeiro`
- a frente seguinte fica enquadrada como POC controlada de tema/base visual pronta e leve, limitada primeiro a `financeiro/templates/financeiro/lancamento_form.html`
- qualquer expansao dessa POC para outras telas do modulo depende de auditoria visual e funcional posterior, incluindo verificacao de layout, legibilidade, ativacao de `Lancamento com rateio`, integridade dos campos, JS/payload, navegacao e preservacao do comportamento funcional
- antes da decisao estrutural final, houve tentativas manuais de recomposicao e compactacao visual em `financeiro/templates/financeiro/lancamento_form.html`, com cabecalho mais enxuto, corpo central unico e composicao por linhas de preenchimento relacionadas
- essas tentativas manuais anteriores nao devem ser tratadas como execucao valida da POC com tema-base real: elas serviram apenas para confirmar o esgotamento dos microajustes incrementais e para evidenciar a necessidade de testar uma base pronta e leve de verdade
- nessas tentativas manuais nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem logica de exibicao/ocultacao do rateio, mas a nova base visual aprovada com **Tabler** continua pendente de implementacao real e auditoria humana propria
- em decisao estrategica posterior, o projeto deixou explicitamente de apostar em novos microajustes incrementais sobre o layout atual de `financeiro/templates/financeiro/lancamento_form.html`
- a estrategia aprovada passou a ser uma POC visual controlada baseada em tema gratis real, e o tema escolhido como referencia principal para essa tela piloto e o **Tabler**
- essa nova fase deve comecar no proximo chat apenas por `financeiro/templates/financeiro/lancamento_form.html`, sem alteracao de regra de negocio e sem expansao para outras telas antes de auditoria visual e funcional
- fica explicitamente registrado que a proxima microetapa correta do proximo chat e aplicar a POC visual controlada com base no Tabler em `financeiro/templates/financeiro/lancamento_form.html`, auditando depois layout, legibilidade, ativacao de `Lancamento com rateio`, integridade dos campos, JS/payload, navegacao e preservacao do comportamento funcional
- a POC visual controlada com base real no **Tabler** foi enfim executada apenas em `financeiro/templates/financeiro/lancamento_form.html`, preservando a mecânica atual da tela e reposicionando o formulario como corpo unico mais central e continuo
- essa execucao ainda nao autoriza expansao para outras telas: a validacao humana visual e funcional da tela piloto continua obrigatoria antes de qualquer continuidade, especialmente com verificacao de layout desktop, legibilidade, ativacao de `Lancamento com rateio`, integridade dos campos, JS/payload, navegacao e preservacao do comportamento funcional
- no ajuste cirurgico posterior dessa tela piloto, a barra superior local passou a ocultar os controles herdados de recolher/abrir menu que nao tinham funcao real confiavel nessa pagina, preservando apenas a navegacao util da propria tela
- nessa mesma passada, a linha financeira passou a tratar o primeiro slot como substituicao coerente entre `Valor` e `Valor total do documento`: sem rateio fica `Valor`; com rateio, o mesmo primeiro lugar visual passa a exibir `Valor total do documento`, seguido por `Data pagamento` e `Data competencia`
- no ajuste estrutural seguinte da mesma tela piloto, a limpeza do topo deixou de depender de ocultacao local por CSS: `financeiro/base.html` passou a oferecer override cirurgico dos controles de topo, e `lancamento_form.html` passou a usar apenas o header de conteudo da pagina com titulo e acao de retorno
- com isso, a hierarquia visivel dessa tela piloto ficou alinhada ao padrao desejado: navegacao estrutural unica do shell, header de conteudo limpo e formulario logo em seguida, sem topo redundante na abertura da pagina
- na passada seguinte, foi identificada como redundancia residual a faixa utilitaria do shell que ainda repetia `Financeiro` antes do header de conteudo; nessa tela piloto, essa segunda faixa foi neutralizada estruturalmente por override do proprio `header` do shell, deixando a abertura visual apenas com a navegacao estrutural principal e o cabecalho da pagina
- no ajuste cirurgico seguinte, a tela piloto voltou a expor a faixa estrutural do shell apenas como suporte da navegacao lateral do tema, sem restaurar a duplicidade de `Financeiro` no topo; no mesmo ajuste, o primeiro slot financeiro passou a usar um unico container visual estavel, trocando apenas entre `Valor` e `Valor total do documento` conforme o estado do rateio
- na passada seguinte da mesma tela piloto, o affordance do controle lateral deixou de usar a seta isolada `>` e passou a conversar melhor com o padrao lateral do tema, enquanto o primeiro slot financeiro manteve a mesma casca visual nos dois estados; nessa mesma etapa, `Linhas do rateio` subiu para antes de `Observacoes` e o valor inicial do slot passou a permanecer consistente ao ativar o rateio
- na correcao responsiva posterior da mesma tela piloto, ficou explicitado no proprio `lancamento_form.html` que o header local do shell deve mostrar apenas um controle por contexto: no desktop permanece `Navegacao`, e no mobile permanece `Menu`; os dois deixam de aparecer juntos na mesma apresentacao, sem alterar a mecanica lateral nem o restante do formulario
- na primeira expansao controlada apos a aprovacao da POC piloto, `financeiro/templates/financeiro/centro_custo_list.html` passou a usar page header limpo, filtros mais maduros, tabela alinhada ao shell atual e estado vazio mais operacional, preservando links, filtros e comportamento funcional da listagem
- na consolidacao cirurgica posterior da mesma listagem, a sensacao de aplicacao hibrida foi reduzida ao reunir filtros e tabela em um unico corpo visual, retirar a rolagem local do bloco da tabela e aproximar a tela do shell atual sem abrir nova frente nem alterar a listagem de formularios relacionados
- no ajuste seguinte dessa mesma expansao controlada, a listagem de centros de custo deixou de herdar a topbar antiga completa do shell e passou a usar, so nessa tela, um header estrutural mais enxuto e coerente com a POC aprovada, mantendo `Navegacao` no desktop e `Menu` no mobile sem alterar o corpo ja consolidado
- na expansao controlada seguinte, `financeiro/templates/financeiro/categoria_list.html` passou a seguir a mesma ordem estrutural aprovada: primeiro override enxuto do `financeiro_shell_header`, preservando a sidebar como navegacao principal, e so depois consolidacao do corpo da listagem
- nessa mesma tela, o header local ficou mais limpo, os filtros passaram a conversar melhor com o shell atual, a tabela ganhou leitura mais madura para `Categoria pai`, `Ativo` e `Acoes`, e o estado vazio ficou mais operacional sem alterar links, filtros nem comportamento funcional
- na expansao controlada seguinte, `financeiro/templates/financeiro/conta_list.html` passou a seguir a mesma ordem estrutural aprovada: primeiro override enxuto do `financeiro_shell_header`, preservando a sidebar como navegacao principal, e so depois refinamento do corpo da listagem
- nessa mesma tela, o page header ficou mais limpo, os filtros passaram a conversar melhor com o shell atual, a tabela ganhou leitura mais madura para `Descricao`, `Saldo inicial`, `Saldo atual (quitado)`, `Ativa` e `Acoes`, e o estado vazio ficou mais operacional sem alterar urls, links nem comportamento funcional
- na expansao controlada seguinte, `financeiro/templates/financeiro/pessoa_list.html` passou a seguir a mesma ordem estrutural aprovada: primeiro override enxuto do `financeiro_shell_header`, preservando a sidebar como navegacao principal, e so depois refinamento do corpo da listagem
- nessa mesma tela, o page header ficou mais limpo, os filtros passaram a conversar melhor com o shell atual, a tabela ganhou leitura mais madura para `Tipo pessoa`, `Documento`, `Telefone`, `E-mail`, `Ativo` e `Acoes`, e o estado vazio ficou mais operacional sem alterar urls, links nem comportamento funcional
- na expansao controlada seguinte, `financeiro/templates/financeiro/centro_custo_form.html` passou a seguir a mesma ordem estrutural aprovada: primeiro override enxuto do `financeiro_shell_header`, preservando a sidebar como navegacao principal, e so depois refinamento do corpo do formulario
- nessa mesma tela, o page header ficou mais limpo, o formulario ganhou card unico mais maduro, melhor agrupamento visual dos campos e bloco de acoes mais coerente, sem alterar validacoes, envio nem comportamento funcional do cadastro
- na expansao controlada seguinte, `financeiro/templates/financeiro/categoria_form.html` passou a seguir a mesma ordem estrutural aprovada: primeiro override enxuto do `financeiro_shell_header`, preservando a sidebar como navegacao principal, e so depois refinamento do corpo do formulario
- nessa mesma tela, o page header ficou mais limpo, o formulario ganhou card unico mais maduro, melhor agrupamento visual dos campos e bloco de acoes mais coerente, sem alterar validacoes, envio nem comportamento funcional do cadastro
- num ajuste fino visual posterior dessa mesma tela, os campos de `categoria_form.html` passaram a usar casca mais proxima do padrao mais novo de `lancamento_form.html` e `pessoa_form.html`, com bordas menos rigidas, altura/padding mais agradaveis, largura 100% real e `mensagem_recibo` com leitura mais confortavel, sem alterar labels, `help_text`, erros, acoes nem comportamento funcional
- numa microetapa posterior de alinhamento textual local, `financeiro/templates/financeiro/categoria_form.html` passou a refletir na propria UI a nomenclatura duradoura `Categoria` / `Subcategoria`, evitando tanto a leitura antiga de `Categoria pai` quanto a solucao intermediaria `Categoria agrupadora`
- nessa mesma passada, o proprio formulario passou a tratar o campo hierarquico como `Categoria`, enquanto o campo principal de nome passou a aparecer como `Subcategoria`, com ajuda local explicando que o campo vazio representa cadastro da propria `Categoria` e o preenchimento representa vinculo da `Subcategoria`
- nessa mesma passada, a ajuda visivel de `mensagem_recibo` foi alinhada para `categoria ou subcategoria`, sem alterar models, forms Python, validacoes nem a regra funcional ainda futura de selecao em lancamentos
- numa microetapa posterior de consistencia visual transversal, `financeiro/templates/financeiro/centro_custo_form.html` e `financeiro/templates/financeiro/conta_form.html` passaram a usar a mesma casca mais nova dos campos ja aprovada em `financeiro/templates/financeiro/pessoa_form.html`, com bordas menos quadradas, altura/padding mais agradaveis, largura 100% real e foco coerente com o tema
- nessa mesma passada, `conta_form.html` preservou o agrupamento de `saldo_inicial` com `data_saldo_inicial`, enquanto `labels`, `help_text`, erros, acoes, validacoes, envio e comportamento funcional dos dois formularios permaneceram intactos
- nesta microetapa foi possivel executar `py manage.py check` com sucesso; a validacao local de `/financeiro/categorias/nova/` via `manage.py shell -c` nao concluiu no ambiente atual por `Acesso negado`
- em decisao documental e funcional posterior, o projeto consolidou para o `financeiro` a hierarquia de nomenclatura `Categoria` / `Subcategoria`: `Categoria` como agrupadora analitica e `Subcategoria` como item operacional lancavel
- essa decisao tambem consolidou que `Categoria` nao deve ser selecionavel em lancamentos; a opcao selecionavel deve ser a `Subcategoria`
- essa definicao ainda nao foi implementada no codigo nesta etapa e permanece registrada apenas como decisao de negocio e orientacao para evolucoes futuras do modulo
- na expansao controlada seguinte, `financeiro/templates/financeiro/conta_form.html` passou a seguir a mesma ordem estrutural aprovada: primeiro override enxuto do `financeiro_shell_header`, preservando a sidebar como navegacao principal, e so depois refinamento do corpo do formulario
- nessa mesma tela, o page header ficou mais limpo, o formulario ganhou card unico mais maduro, melhor agrupamento visual dos campos e bloco de acoes mais coerente, com atencao especial para a leitura conjunta de `saldo_inicial` e `data_saldo_inicial`, sem alterar validacoes, envio nem comportamento funcional do cadastro
- na expansao controlada seguinte, `financeiro/templates/financeiro/pessoa_form.html` passou a seguir a mesma ordem estrutural aprovada: primeiro override enxuto do `financeiro_shell_header`, preservando a sidebar como navegacao principal, e so depois refinamento do corpo do formulario
- nessa mesma tela, o page header ficou mais limpo, o formulario ganhou card unico mais maduro, melhor agrupamento visual dos campos e bloco de acoes mais coerente, com atencao especial para a leitura conjunta de `tipo_pessoa`, `documento`, `telefone`, `email` e `observacoes`, sem alterar validacoes, envio nem comportamento funcional do cadastro
- num ajuste fino posterior da mesma tela, a grade do formulario passou a aproveitar melhor a largura horizontal do card, com distribuicao mais firme das linhas de identificacao, documento e contato, e com `observacoes` mais confortavel em largura integral
- num polimento visual posterior da mesma tela, os campos passaram a usar casca mais proxima do padrao mais novo do `lancamento_form.html`, com bordas menos rigidas, alturas e paddings mais agradaveis, foco mais claro e `observacoes` mais confortavel sem alterar comportamento funcional
- numa microcorrecao visual posterior da mesma tela, o controle booleano `Ativo` perdeu protagonismo excessivo e passou a operar com dimensao mais discreta e proporcional ao restante do formulario, sem alterar envio, validacoes nem comportamento funcional
- numa microcorrecao visual transversal posterior, os formularios auxiliares ja refinados de `centro_custo`, `categoria` e `conta` passaram a usar a mesma linha visual discreta do booleano aprovada em `pessoa_form.html`, eliminando a inconsistencia entre checkbox azul e checkbox amarelo/laranja sem alterar labels, envio, validacoes nem comportamento funcional
- em consolidacao documental posterior, ficou registrado que a hierarquia `Categoria` / `Subcategoria` continua valida, mas a UI atual ainda nao e suficientemente autoexplicativa no proprio cadastro e deve evoluir futuramente para deixar mais explicito se o formulario esta tratando `Categoria` ou `Subcategoria`
- nessa mesma consolidacao, foi registrada como abordagem futura aceitavel a possibilidade de seletor ou toggle `Categoria | Subcategoria`, com exibicao do campo `Categoria` apenas quando o cadastro for de `Subcategoria`
- tambem ficaram registradas como frentes futuras, sem implementacao no estado atual, a leveza adicional do menu lateral, a sugestao de regras reutilizaveis no lancamento e a futura acao `Clonar lancamento`
- em delimitacao documental posterior da frente de regras reutilizaveis, o MVP inicial ficou definido com gatilho `descricao` + `pessoa`, sugestao apresentada para aplicacao apenas por acao explicita `Usar sugestao`, preenchendo `descricao`, `tipo`, `pessoa`, `categoria`, `centro_custo`, `conta`, `conta_destino` e `observacoes`, mas deixando fora `numero_documento`, datas, `status`, `valor`, rateio, ids internos e auditoria; `Salvar como regra` permanece para uma fase seguinte
- na primeira implementacao minima desse MVP, foi criado o model `RegraLancamentoFinanceiro` e um endpoint JSON dedicado de sugestoes por `descricao` + `pessoa`, retornando lista curta com resumo e payload apenas dos campos aplicaveis
- nessa mesma implementacao, `financeiro/templates/financeiro/lancamento_form.html` passou a exibir um bloco discreto e ocultavel de sugestoes apenas depois de interacao do usuario com `descricao` e `pessoa`, e a acao `Usar sugestao` preenche explicitamente apenas `descricao`, `tipo`, `pessoa`, `categoria`, `centro_custo`, `conta`, `conta_destino` e `observacoes`, preservando clone, rateio, datas, `status`, `valor` e `numero_documento`
- em decisao de negocio posterior, esse desenho com dependencia rigida de `descricao` + `pessoa` juntas foi revisado: a direcao atual passa a pedir sugestao disparada por campo gatilho individual, com `descricao` como primeiro gatilho avaliado ja durante a digitacao, enquanto `pessoa` pode entrar apenas como complemento/filtro futuro e nao como requisito obrigatorio do MVP
- a regra continua devendo funcionar como modelo preenchido sem vinculo com lancamento anterior, e alteracoes feitas pelo usuario no formulario depois de aplicar a sugestao nao devem editar automaticamente a regra de origem
- ficou registrada como fase posterior a acao explicita `Salvar como regra` dentro do fluxo de cadastro de lancamento, sem implementacao nesta microetapa
- ficou registrada tambem como melhoria futura imediata a acao `Clonar` dentro de `Ultimos lancamentos da pessoa` no `lancamento_form.html`, para reaproveitar um lancamento anterior diretamente da lista sem alterar o documento original e mantendo a mesma semantica de clone ja aprovada
- na regularizacao operacional posterior dessa frente, o endpoint JSON de sugestoes passou a aceitar `descricao` como gatilho principal sem exigir `pessoa`; quando `pessoa` vem informada, ela atua apenas como refinador opcional da busca
- nessa mesma regularizacao, o bloco de sugestoes do `lancamento_form.html` deixou de depender do botao `Usar sugestao`: cada item sugerido passou a ser selecionavel por clique direto, preenchendo automaticamente apenas os campos estruturais da regra e mantendo o usuario livre para editar antes de salvar
- o formulario de novo lancamento passou a ter o check explicito `Salvar como regra automatica`; quando marcado em lancamento comum, o `LancamentoFinanceiroCreateView` persiste uma nova `RegraLancamentoFinanceiro` sem `numero_documento`, datas, `status`, `valor`, rateio, auditoria ou vinculo com o lancamento original
- no fluxo de rateio desse MVP, o check de salvar regra automatica e ocultado e desmarcado para evitar gravacao parcial de regra a partir de documento rateado
- a secao `Ultimos lancamentos da pessoa` do `lancamento_form.html` agora exibe uma acao discreta `Clonar` por item elegivel, reaproveitando as rotas ja existentes de clone comum e de clone por `grupo_rateio` quando o lancamento historico exibido e rateado
- permissões, acesso e perfis continuam explicitamente como frente estrutural futura e nao entraram nesta microetapa documental
- em decisao documental posterior, o MVP inicial de `Clonar lancamento` foi delimitado para lancamento comum sem rateio, abrindo `lancamento_form.html` em modo criacao com dados pre-preenchidos do original, mas sem alterar o lancamento de origem
- nessa mesma delimitacao, ficou registrado que o clone deve copiar `descricao`, `tipo`, `pessoa`, `categoria`, `centro_custo`, `conta`, `conta_destino` quando transferencia, e `observacoes`, mas nao deve copiar `pk`, `numero_documento`, datas, `status`, auditoria, `grupo_rateio` ou identificadores sujeitos a colisao
- tambem ficou registrado que lancamentos com rateio permanecem fora do MVP de clonagem e podem ficar sem acao de clone nesta primeira fase, enquanto transferencias exigem cuidado para preservar `conta_destino` sem reintroduzir campos que nao pertencem ao tipo
- na primeira implementacao minima desse MVP, a listagem de lancamentos passou a exibir a acao `Clonar` apenas em lancamentos comuns sem rateio, abrindo rota/view dedicada que reaproveita `lancamento_form.html` em modo criacao com `descricao`, `tipo`, `pessoa`, `categoria`, `centro_custo`, `conta`, `conta_destino` quando transferencia, e `observacoes` como `initial` controlado
- nessa mesma implementacao, `pk`, `numero_documento`, `data_competencia`, `data_pagamento`, `status`, auditoria, `grupo_rateio` e `com_rateio` nao sao carregados do lancamento original, e acessos diretos a clone de lancamento rateado sao bloqueados com aviso e retorno seguro a listagem
- apos auditoria humana posterior, ficou consolidado que o clone comum nao deve manter qualquer vinculo com o lancamento original e deve atuar apenas como um modelo ja preenchido para acelerar o cadastro de um novo lancamento
- nessa correcao posterior do MVP comum, a view dedicada de clone passou a copiar tambem `status`, `valor`, `data_competencia` e `data_pagamento`, mantendo fora `pk`, `numero_documento`, auditoria, `grupo_rateio`, `com_rateio` e qualquer identificador interno do lancamento original
- tambem ficou documentada como proxima fase futura a clonagem de lancamento com rateio por grupo, igualmente sem vinculo com o original; nessa etapa futura, se o usuario alterar o `valor total do documento`, as linhas/categorias do rateio deverao ser ajustadas manualmente no proprio clone, sem sincronizacao com o grupo de origem
- numa correcao cirurgica posterior do clone comum, o formulario passou a normalizar `data_competencia` e `data_pagamento` para formato ISO no widget `type=date`, evitando que o navegador abra esses campos vazios na tela de clone
- nessa mesma correcao, a `categoria` inicial do clone passou a ser reincluida no queryset renderizado do campo quando necessario, para que categorias herdadas de lancamentos antigos aparecam preenchidas sem relaxar a validacao de negocio no `clean()`
- numa correcao cirurgica posterior do autocomplete do formulario de lancamento, a classe base de autocomplete deixou de fatiar o queryset antes de filtros especificos de subclasses; com isso, o endpoint de `Categoria` voltou a aceitar busca por digitacao parcial sem erro e o limite de resultados passou a ser aplicado apenas na resposta final
- na primeira implementacao minima da fase seguinte, lancamentos com rateio passaram a exibir a acao `Clonar` na listagem e a usar apenas um icone pequeno de ramificacao no lugar do texto `Rateio`, sem expor o identificador tecnico do `grupo_rateio`; essa acao abre rota/view dedicada por `grupo_rateio` em modo criacao, com cabecalho, `valor total do documento` e linhas de rateio pre-preenchidos a partir do grupo original, mas sem reaproveitar `pk`, `numero_documento`, `grupo_rateio`, IDs antigos das linhas, auditoria ou qualquer vinculo operacional com o documento de origem
- numa passada visual/controlada posterior da listagem principal de lancamentos, `financeiro/templates/financeiro/lancamento_list.html` deixou de herdar o topo utilitario padrao completo e passou a usar override enxuto do `financeiro_shell_header`, alinhando o shell dessa tela as listagens auxiliares mais recentes sem alterar rotas, filtros, clone, rateio ou acoes existentes
- nessa mesma passada, foram removidos o subtitulo explicativo do page header, a legenda fixa da tabela e as notas longas de apoio nas linhas rateadas, enquanto filtros e tabela passaram a compartilhar um unico card visual mais coerente com o shell atual e o estado vazio ficou mais operacional
- numa microetapa posterior de clareza local da UI, `financeiro/templates/financeiro/categoria_form.html` passou a expor na propria tela um seletor visual simples entre `Categoria` e `Subcategoria`, sem alterar models, views, forms Python nem regras profundas
- nessa mesma passada, o campo principal de nome passou a trocar visualmente entre `Categoria` e `Subcategoria`, enquanto o campo `Categoria` fica oculto e desativado no modo `Categoria` e reaparece no modo `Subcategoria`
- essa evolucao melhora a leitura operacional do cadastro, mas nao representa ainda a implementacao completa da regra funcional futura de `Categoria` / `Subcategoria`
- na primeira passada posterior sobre o extrato real do sistema, `financeiro/templates/financeiro/conta_extrato.html` manteve o `financeiro_shell_header` padrao e recebeu apenas refinamento do corpo da tela, com header local mais seco, filtros mais maduros, tabela mais consistente e estados vazios mais operacionais
- nessa mesma passada, `print/PDF`, `saldo anterior`, `saldo acumulado`, a leitura dos rateios consolidados e as acoes `Imprimir` e `Limpar` foram preservados explicitamente, sem alteracao de models, views, forms, calculos ou logica funcional do extrato
- num ajuste fino posterior dessa mesma tela, o `Saldo anterior` deixou de ocupar a primeira linha do corpo da tabela e passou a aparecer em bloco proprio acima do cabecalho das colunas, reforcando sua leitura como contexto inicial do extrato sem alterar calculos, saldo acumulado, rateios nem comportamento de impressao
- num ajuste visual seguinte da mesma tela, o `Saldo anterior` acima da tabela passou a usar a mesma linguagem visual do `Saldo final`, e a linha impressa `Conta | Periodo | Emitido em` permaneceu preservada, mas sem linhas horizontais acima ou abaixo
- na correcao fina posterior dessa mesma tela, o `Saldo anterior` deixou de usar bloco especial e passou a ser renderizado acima do cabecalho das colunas com a mesma linguagem visual tabular do `Saldo final`, preservando a mudanca de posicao sem criar nova identidade visual
- numa microcorrecao final posterior dessa mesma tela, a faixa impressa `Conta | Periodo | Emitido em` recebeu override especifico de print no proprio template para neutralizar de fato as linhas horizontais herdadas do shell/base, mantendo apenas a informacao textual limpa
- numa microcorrecao visual posterior dessa mesma tela, o cabecalho e as linhas do corpo do extrato passaram a usar divisorias mais finas e suaves, aliviando o peso visual da tabela sem alterar saldos, rateios, print/PDF nem a hierarquia ja aprovada
- numa correcao posterior dessa mesma microetapa, a suavizacao das divisorias da tabela foi restrita apenas ao `@media print`, preservando a tela normal como estava e deixando o alivio visual apenas na versao PDF/impressa
- numa correcao fina posterior dessa mesma microetapa, o `@media print` do extrato deixou de usar linhas de `0.7px` e passou a aplicar divisorias ainda mais leves no cabecalho e no corpo da tabela, com espessura menor e cor mais suave apenas no PDF
- num ajuste fino posterior dessa mesma microetapa, as divisorias do `@media print` foram recalibradas para um valor intermediario, mantendo o PDF mais leve do que a versao pesada original, mas sem deixar as linhas apagadas demais
- numa correcao posterior dessa mesma microetapa, foi identificado que as linhas visiveis do PDF ainda eram controladas principalmente pelos seletores de print do `financeiro/base.html` sobre `.financeiro-extrato-table`; o extrato passou entao a usar override mais especifico no proprio `@media print`, atuando diretamente em `table > thead > tr > th` e `table > tbody > tr > td`
- numa correcao posterior dessa mesma microetapa, o `Saldo anterior` passou a espelhar a mesma estrutura tabular do `Saldo final`, mudando apenas de posicao acima do cabecalho, e o `@media print` do extrato deixou de depender de espessura fracionaria para usar `1px` com cor mais suave nas divisorias do cabecalho e do corpo
- numa calibragem fina posterior dessa mesma microetapa, o `Saldo anterior` acima do cabecalho passou a usar a mesma tabela e a mesma linha visual do `Saldo final`, sem wrapper de estilo alternativo, e o print do extrato teve as divisorias de `1px` clareadas ainda mais para reduzir o peso visual do PDF sem apagar completamente as linhas
- numa correcao posterior dessa mesma microetapa, o `Saldo anterior` passou a compartilhar explicitamente o mesmo `colgroup` da tabela principal para alinhar rótulo e valor nas mesmas colunas do `Saldo final`, e o print do extrato deixou de depender de `px` fracionario para usar espessura em `pt` nas divisorias do cabecalho e do corpo
- numa correcao estrutural posterior dessa mesma microetapa, o `Saldo anterior` deixou de ser renderizado em tabela separada e passou a ocupar a primeira linha do `thead` da propria tabela principal do extrato, alinhando de forma real o rótulo e o valor as mesmas colunas do `Saldo final`
- nessa mesma correcao, o `@media print` do extrato passou a aliviar a grade tambem pela densidade de `th` e `td`, com reducao de `padding-top` e `padding-bottom` no cabecalho e no corpo, sem alterar calculos, filtros, rateios ou a linha `Conta | Periodo | Emitido em`
- numa correcao estrutural posterior dessa mesma microetapa, o `Saldo anterior` deixou o `thead` e voltou a ser renderizado com `tbody > tr > td` em tabela auxiliar acima da principal, reaproveitando o mesmo `colgroup` e a mesma linha visual do `Saldo final` para alinhar rótulo e valor nas mesmas colunas
- nessa mesma correcao, o `@media print` do extrato manteve cor proxima da base, mas recalibrou a grade pela combinacao de borda `1px` e menor `padding-top`/`padding-bottom` de `th` e `td`, para afinar a percepção da linha sem depender de clareamento progressivo
- numa reversao posterior dessa mesma microetapa, o `Saldo anterior` deixou de usar novamente tabela auxiliar e voltou a ocupar a posicao anterior acima do cabecalho, enquanto sua linha do `thead` passou a espelhar apenas a gramática visual do `Saldo final` sem alterar este ultimo
- nessa mesma reversao, o `@media print` do extrato foi recalibrado outra vez com foco em espessura e densidade da grade, reduzindo ainda mais `padding-top`/`padding-bottom` de `th` e `td` e usando borda mais fina em `pt`, sem depender de novo clareamento progressivo

## Levantamento estrutural inicial para futura matriz de permissoes

- O estado real do Git foi conferido nesta microetapa: a branch atual permanece `feat/reinicio-financeiro`, o working tree nao possui modificacoes rastreadas abertas e `tmp/` e o unico item untracked visivel no status.
- `docs/MATRIZ_PERMISSOES.md` ainda nao existe e nao foi criado nesta etapa, preservando a regra de documento protegido e a decisao ja registrada de so abrir esse arquivo quando a frente de permissoes for formalmente iniciada.
- No modulo `financeiro`, a navegacao exposta ao usuario hoje esta organizada no shell lateral em `Visao geral`, `Movimentacao`, `Relatorios`, `Cadastros` e `Institucional`, alem da `home` secundaria em `/financeiro/inicio/`.
- Ainda no `financeiro`, os recursos/telas reais ja identificados para a futura matriz sao:
  - `Lancamentos`: listar, criar, editar, excluir, clonar lancamento comum, clonar rateio, editar grupo rateado, emitir recibo, alterar status em lote, excluir em lote, exportar listagem filtrada, importar XLSX, baixar modelo, baixar relatorio de inconsistencias, consultar ultimos lancamentos da pessoa e obter sugestoes de regras automaticas.
  - `Extratos`: abrir a tela geral de extratos, consultar extrato por conta e filtrar por periodo.
  - `Resumo` e `Prestacao de Contas`: consultar relatorios por periodo/contas e imprimir.
  - `Auditoria do Financeiro`: listar registros de auditoria e filtrar por acao, periodo e id do registro.
  - `Contas`, `Pessoas`, `Categorias`, `Centros de Custo`, `Assinaturas Institucionais` e `Configuracoes Institucionais`: listar, criar, editar e excluir, com `Contas` tambem expondo extrato individual.
  - Endpoints auxiliares de autocomplete e historico (`autocomplete/pessoas`, `autocomplete/categorias`, `autocomplete/contas`, `autocomplete/centros-custo`, `historico/pessoas/.../ultimos-lancamentos`) aparecem como suporte de formulario/tela e devem herdar a mesma governanca de acesso do recurso de origem.
- No modulo `biblioteca`, os recursos/telas reais ja expostos em menu proprio sao `Autores`, `Livros`, `Vendas` e `Emprestimos`, todos com acoes atuais de listar e criar; nao foram identificadas rotas proprias de edicao/exclusao nesse app nesta leitura.
- No modulo `configuracoes`, a raiz do projeto (`/`) exibe `SiteConfigDetailView` como tela de configuracao/site institucional, e nao existe `configuracoes/urls.py` dedicado no estado atual; o Django admin segue exposto em `/admin/`.
- A proposta inicial de hierarquia de perfis, ainda sem implementacao e sem criacao de grupos Django, fica assim registrada para avaliacao futura: `Administrador geral`, `Gestao administrativa`, `Operador financeiro`, `Operador biblioteca` e `Consulta/visualizacao`.
- Pontos que exigirao controle de acesso na futura frente: exibicao/ocultacao de menus e atalhos por perfil, protecao de rotas e endpoints auxiliares, restricao de acoes destrutivas (`excluir`, lote, configuracoes institucionais), separacao entre leitura e escrita em relatorios/listagens/formularios, governanca de importacao/exportacao, visibilidade da auditoria e futura coerencia do log de acesso.
- Impactos transversais obrigatorios da frente de permissoes ja levantados para a proxima etapa: revisar navegacao/menu, listagens, formularios, importacao/exportacao, auditoria/log, ajuda/manual, aderencia a `docs/PADRAO_UX_SISTEMA.md` e atualizacao dos docs-base conforme `docs/CHECKLIST_EVOLUCAO_SISTEMA.md`.
- Foi criada a primeira versao formal de `docs/MATRIZ_PERMISSOES.md`, estruturada em `Modulo > Tela/Recurso > Acao`, com perfis-base `Administrador geral`, `Gestao administrativa`, `Operador financeiro`, `Operador biblioteca` e `Consulta/visualizacao`.
- A matriz nasceu distinguindo administracao funcional do sistema e administracao tecnica/global via `/admin/`, e registrando que esconder menu nao basta: a permissao futura deve valer tambem em tela, botao/acao e endpoint auxiliar.
- Tambem ficou registrada a diretriz arquitetural da frente: na V1, cada usuario tera 1 perfil base; como evolucao futura, poderao existir extras individuais e bloqueios individuais por usuario, seguindo a formula conceitual `permissao final = perfil base + extras individuais - bloqueios individuais`, sem tratar essa extensao como implementada agora.
- Na auditoria documental posterior dessa matriz, as permissoes sensiveis que ainda estavam marcadas como `R` foram fechadas de forma mais objetiva: `/admin/` permanece exclusivo do `Administrador geral`; `Gestao administrativa` pode operar configuracoes funcionais e auditoria sem administracao tecnica global; `Operador financeiro` continua com escrita operacional no `financeiro`, mas sem exclusao direta de cadastros/lancamentos, sem exclusao em lote e sem acesso a auditoria/configuracoes institucionais; `Operador biblioteca` fica restrito ao modulo `biblioteca` e a leitura institucional de `/`; `Consulta/visualizacao` fica majoritariamente em leitura, com impressao/exportacao onde ja possui acesso de leitura, mas sem importar, escrever, excluir, usar lote ou consumir endpoints auxiliares de formulario.
- Foi criado `docs/PLANO_TECNICO_PERMISSOES.md` como ponte entre a matriz funcional e a futura implementacao tecnica, sem alterar codigo nesta etapa.
- A decisao tecnica registrada para a V1 de permissoes foi um modelo hibrido: usar `User`, autenticacao, sessao e login/logout do Django como base de identidade, mas manter uma camada propria de `Perfil`, `Permissao do sistema` e vinculos de autorizacao como fonte principal da governanca funcional, em vez de depender apenas de `Group/Permission` nativo.
- O plano tecnico definiu a modelagem conceitual minima esperada (`perfil base`, `permissao do sistema`, `perfil-permissao`, `usuario-perfil`) e manteve apenas como compatibilidade futura, nao implementada agora, as extensoes de extras individuais e bloqueios individuais por usuario.
- O plano tambem definiu a ordem incremental sugerida da implementacao: primeiro estrutura de dados e seeds de permissoes, depois autenticacao e primeiro enforcement backend no `financeiro`, em seguida menu/botoes/templates do `financeiro`, depois expansao para `biblioteca` e `configuracoes`, UI propria de perfis e, por fim, endurecimento/auditoria e preparacao para excecoes individuais futuras.
- O primeiro ponto de aplicacao real da V1 ficou definido como o modulo `financeiro`, com prioridade para `Lancamentos`, `Auditoria`, `Configuracoes institucionais`, `Assinaturas`, `Importar/Exportar` e endpoints auxiliares.

## Base tecnica inicial da V1 de permissoes/autenticacao

- a primeira camada tecnica de dados da V1 foi implementada no app `configuracoes`, sem enforcement de rotas/views/templates, sem login/logout customizado e sem criacao de grupos Django nesta microetapa
- foram criados os modelos `PerfilAcesso`, `PermissaoSistema`, `PerfilPermissaoSistema` e `UsuarioPerfilAcesso`, preservando a decisao do plano tecnico de usar `User` do Django para identidade e uma camada propria do sistema para a governanca funcional
- `UsuarioPerfilAcesso` materializa a regra V1 de 1 perfil base por usuario por meio de vinculo `OneToOne` com `AUTH_USER_MODEL`, enquanto `PerfilAcesso` e `PermissaoSistema` ficam preparados para sustentar o enforcement futuro em menu, tela, botao e endpoint auxiliar
- `PermissaoSistema` nasceu com codigo estavel e unico, campos `modulo`, `recurso` e `acao`, e unicidade adicional por `modulo` + `recurso` + `acao`, mantendo aderencia direta a `docs/MATRIZ_PERMISSOES.md`
- foram criadas as migrations `configuracoes/migrations/0003_perfilacesso_perfilpermissaosistema_permissaosistema_and_more.py` e `configuracoes/migrations/0004_seed_perfis_permissoes_v1.py`
- a migration de seed inicial cria de forma idempotente os perfis-base `Administrador geral`, `Gestao administrativa`, `Operador financeiro`, `Operador biblioteca` e `Consulta/visualizacao`, alem de um conjunto inicial de permissoes funcionais para `financeiro`, `biblioteca` e `configuracoes`
- o vinculo perfil-permissao inicial ja reflete a matriz V1 em pontos sensiveis: `/admin/` exclusivo de `Administrador geral`; `Gestao administrativa` sem admin tecnico global; `Operador financeiro` sem exclusoes sensiveis, auditoria e configuracoes institucionais; `Operador biblioteca` restrito a `biblioteca` e leitura institucional; `Consulta/visualizacao` apenas leitura/impressao/exportacao, sem escrita/importacao/lote/autocomplete de formulario
- a compatibilidade futura para extras individuais e bloqueios individuais por usuario permanece somente documental nesta etapa e nao foi implementada em models/migrations

## Bootstrap operacional de autenticacao e resolucao central de permissoes

- foram adicionadas rotas e views de `login` e `logout` no app `configuracoes`, usando a autenticacao base do Django e um template minimo proprio em `configuracoes/templates/configuracoes/login.html`
- `casa_espirita/settings.py` passou a declarar `LOGIN_URL`, `LOGIN_REDIRECT_URL` e `LOGOUT_REDIRECT_URL`, apontando o fluxo autenticado para o `financeiro` e o logout de volta para `/login/`
- foi criada a camada central `configuracoes/permissoes.py` com helpers para obter o perfil-base ativo do usuario e verificar uma permissao funcional por codigo canonico ja semeado
- a regra segura adotada para usuario autenticado sem perfil-base foi negar permissao funcional por padrao: `usuario_possui_permissao()` retorna `False` quando nao existe `UsuarioPerfilAcesso`, quando o usuario nao esta autenticado ou quando o perfil vinculado esta inativo
- os models `PermissaoSistema`, `PerfilAcesso`, `PerfilPermissaoSistema` e `UsuarioPerfilAcesso` foram registrados no Django admin como caminho operacional temporario de consulta/manutencao ate existir uma UI funcional propria de perfis
- a estrategia de bootstrap escolhida para o primeiro administrador funcional foi nao criar bypass automatico nesta V1: o vinculo entre um superusuario existente e o perfil `Administrador geral` deve ser feito manualmente via `/admin/`, preservando controle explicito e evitando permissao implicita baseada apenas em `is_superuser`
- esta microetapa nao aplicou enforcement fino em rotas/views/templates do `financeiro`, nao ocultou sidebar/menu por permissao e nao implementou extras ou bloqueios individuais

## Primeiro enforcement backend de permissoes no modulo financeiro

- foi criada a camada reutilizavel `financeiro/permissoes.py` com `FinanceiroPermissaoMixin`, integrando `LoginRequiredMixin` e o helper central `usuario_possui_permissao()` do app `configuracoes`
- o mixin exige usuario autenticado, valida a permissao funcional por codigo canonico em `get_permissao_requerida()` e responde com HTTP 403 e mensagem simples quando o usuario autenticado nao tem a permissao exigida ou nao possui perfil-base ativo
- o enforcement backend foi aplicado nas views principais do `financeiro`, cobrindo home secundaria, listagens, cadastros, edicoes, exclusoes, extratos, resumo, prestacao de contas, auditoria, importacao/exportacao, download de modelo/inconsistencias, clone comum, clone/edicao de rateio, recibo, acoes em lote e endpoints auxiliares de autocomplete/historico/sugestoes
- em `LancamentoFinanceiroAcoesLoteView`, a permissao exigida passa a variar conforme `acao_lote`: `financeiro.lancamentos.acoes_em_lote_excluir` para exclusao em lote e `financeiro.lancamentos.acoes_em_lote_status` para alteracao de status
- o fluxo `/financeiro/` continua redirecionando para a listagem principal, e o bloqueio real acontece na view de destino, preservando a rota de entrada do modulo sem abrir ainda a etapa de ocultacao de menus/botoes
- a regra deny-by-default foi validada em smoke tests: usuario anonimo e redirecionado para `/login/`, usuario autenticado sem `UsuarioPerfilAcesso` recebe 403, `Consulta/visualizacao` acessa a listagem mas nao abre cadastro, `Operador financeiro` cria lancamento mas nao acessa exclusao nem auditoria, e `Gestao administrativa` acessa auditoria
- esta microetapa nao alterou sidebar/menu, nao condicionou botoes/templates, nao aplicou enforcement em `biblioteca`/`configuracoes`, nao implementou extras/bloqueios individuais e nao criou bypass funcional para superusuario

## Primeiro enforcement visual de permissoes no financeiro

- a camada visual do `financeiro` passou a reutilizar uma template tag propria, `financeiro/templatetags/financeiro_permissoes.py`, apoiada no resolvedor central de `configuracoes/permissoes.py`, para evitar duplicacao excessiva de checagem em sidebar, atalhos e botoes
- `configuracoes/permissoes.py` passou a expor cache por usuario dos codigos de permissao ativos do perfil-base, reduzindo repeticao de consulta entre backend e templates sem alterar a regra deny-by-default
- o shell lateral de `financeiro/base.html` agora exibe grupos e links do modulo apenas quando o usuario possui a permissao funcional correspondente de leitura/consulta do recurso; o mesmo criterio passou a valer para os atalhos da `home` secundaria do modulo
- as listagens principais de `contas`, `pessoas`, `categorias`, `centros de custo`, `assinaturas institucionais`, `configuracoes institucionais` e `lancamentos` passaram a esconder botoes de criar/editar/excluir e, quando necessario, a propria coluna de acoes, conforme as permissoes visuais disponiveis ao perfil autenticado
- em `lancamentos`, a camada visual passou a refletir permissoes de `exportar`, `importar`, `criar`, `acoes em lote`, `emitir recibo`, `clonar`, `editar`, `editar rateio` e `excluir`, preservando o backend como protecao principal e escondendo apenas o que o usuario realmente nao pode usar
- a tela de `importacao/exportacao` passou a esconder downloads auxiliares (`baixar modelo`, `baixar inconsistencias`) quando o perfil autenticado nao possui a permissao especifica, sem alterar a politica funcional all-or-nothing da importacao
- o endpoint de historico da pessoa no formulario de lancamento passou a devolver `clone_url` apenas quando o usuario possui `financeiro.lancamentos.clonar`, evitando que a UI exponha atalho contextual de clone sem a permissao correspondente
- smoke tests visuais basicos confirmaram coerencia com o enforcement backend: `Consulta/visualizacao` ve exportacao mas nao ve criar/importar/excluir na listagem de lancamentos; `Operador financeiro` ve criar/importar/exportar/editar, mas nao ve auditoria/configuracoes institucionais/excluir; `Gestao administrativa` mantem visibilidade ampliada coerente com a matriz V1
- esta microetapa nao alterou regras de negocio, nao expandiu enforcement visual para `biblioteca` ou outros modulos, nao abriu bypass por superusuario e nao implementou extras individuais ou bloqueios individuais

## Expansao do enforcement backend para biblioteca e configuracoes

- a estrategia de enforcement backend foi consolidada em `configuracoes/permissoes.py` com `PermissaoSistemaMixin`, mantendo o mesmo comportamento-base ja aprovado no `financeiro`: anonimo redirecionado para `/login/`, usuario autenticado sem perfil/permissao recebendo HTTP 403 e ausencia de bypass funcional automatico por superusuario
- `financeiro/permissoes.py` passou a reutilizar esse mixin central, preservando a mensagem especifica do modulo e sem alterar a regra funcional ja validada no `financeiro`
- o modulo `biblioteca` ganhou `biblioteca/permissoes.py` com `BibliotecaPermissaoMixin`, reaproveitando a mesma base central para proteger backend de `Autores`, `Livros`, `Vendas` e `Emprestimos`
- em `biblioteca/views.py`, as rotas reais expostas hoje passaram a exigir os codigos canonicos da matriz V1: `biblioteca.autores.listar/criar`, `biblioteca.livros.listar/criar`, `biblioteca.vendas.listar/criar` e `biblioteca.emprestimos.listar/criar`
- o modulo `configuracoes` ganhou `configuracoes/mixins.py` com `ConfiguracoesPermissaoMixin`, tambem derivado da camada central, e `SiteConfigDetailView` passou a exigir `configuracoes.siteconfig.visualizar`
- `/admin/` permaneceu intocado e continua separado como administracao tecnica/global, sem qualquer bypass funcional implicito para os recursos operacionais dos apps
- durante a validacao apareceu uma divergencia objetiva entre a matriz funcional e a seed ja aplicada: `Operador financeiro` deveria visualizar `SiteConfig /`, mas ainda nao herdava `configuracoes.siteconfig.visualizar`; isso foi alinhado por meio da migration de dados `configuracoes/migrations/0005_alinhar_siteconfig_operador_financeiro.py`
- smoke tests backend confirmaram o comportamento esperado apos o alinhamento: `Consulta/visualizacao` acessa listagens de `biblioteca` e `SiteConfig /`, mas recebe 403 nas telas de criacao; `Operador financeiro` continua barrado em `biblioteca`, mas passa a acessar `/`; `Operador biblioteca` e `Gestao administrativa` acessam `biblioteca` conforme a matriz; usuario autenticado sem perfil recebe 403 e anonimo recebe 302 para login
- esta microetapa nao aplicou enforcement visual amplo em `biblioteca` ou `configuracoes`, nao mexeu em login/logout alem do que ja existia, nao implementou extras/bloqueios individuais e nao alterou `/admin/`

## Expansao do enforcement visual para biblioteca e configuracoes

- foi criada a template tag generica `configuracoes/templatetags/permissoes_sistema.py`, reaproveitando o resolvedor central de permissoes para evitar logica ad hoc espalhada nos templates fora do `financeiro`
- em `biblioteca/templates/biblioteca/base.html`, os links de `Autores`, `Livros`, `Vendas` e `Emprestimos` passaram a aparecer apenas quando o usuario autenticado possui as permissoes de leitura correspondentes
- as listagens de `Autores`, `Livros`, `Vendas` e `Emprestimos` passaram a esconder os botoes de criacao quando faltam as permissoes `biblioteca.*.criar`, mantendo o backend como protecao principal
- em `configuracoes/templates/configuracoes/siteconfig_detail.html`, a interface passou a mostrar `Entrar` para anonimos, `Sair` para autenticados e `Admin tecnico` apenas para quem possui `configuracoes.admin_global.acessar`, preservando a separacao entre administracao funcional e administracao tecnica/global
- smoke tests visuais basicos confirmaram coerencia com o backend ja protegido: `Consulta/visualizacao` ve navegacao de leitura em `biblioteca` sem botoes de criacao; `Operador biblioteca` e `Gestao administrativa` veem botoes de criacao no modulo; `Operador financeiro` acessa `SiteConfig /` sem ganhar navegacao funcional da `biblioteca`
- esta microetapa nao expandiu enforcement visual para outros modulos, nao alterou o backend ja aprovado no `financeiro` e nao implementou extras ou bloqueios individuais

## Recuperacao de senha V1 e identidade institucional do login

- a tela de `login` deixou de usar o nome institucional hardcoded: o texto exibido agora vem do `SiteConfig.site_name`, com fallback seguro para `Casa Espirita` quando nao houver cadastro
- foi criada uma base compartilhada minima para os templates de autenticacao em `configuracoes/templates/configuracoes/auth_base.html`, preservando a linguagem visual ja existente e adicionando o link `Esqueci minha senha`
- o fluxo nativo do Django para recuperacao de senha passou a ficar exposto pelas rotas `/senha/esqueci/`, `/senha/esqueci/enviado/`, `/senha/redefinir/<uidb64>/<token>/` e `/senha/redefinir/concluido/`, com templates proprios minimos e coerentes com a tela de login
- `casa_espirita/urls.py` passou a expor tambem `admin_password_reset` em `/admin/password_reset/`, mantendo `/admin/` separado como administracao tecnica/global
- foi criado `ConfiguracoesPasswordResetForm` para evitar promessa falsa de reset a quem informa um e-mail sem usuario ativo/utilizavel correspondente; nesses casos, o formulario retorna erro claro em vez de seguir silenciosamente para a confirmacao
- o projeto passou a ter configuracao de e-mail por ambiente em `settings.py`, com fallback seguro para `django.core.mail.backends.console.EmailBackend` quando nenhuma configuracao real e informada por variavel de ambiente
- na pratica, isso deixa o fluxo funcional em desenvolvimento sem SMTP real: o e-mail de recuperacao e gerado e registrado no console do servidor; quando houver backend real configurado por ambiente, o mesmo fluxo pode enviar a mensagem de fato sem reabrir a arquitetura
- smoke tests confirmaram: login `200`, nome institucional vindo do cadastro real, link `Esqueci minha senha` visivel, `/admin/password_reset/` `200`, envio local do reset funcionando com backend `locmem` em teste, redefinicao efetiva da senha e mensagem clara para e-mail inexistente
- a regra deny-by-default das permissoes funcionais permaneceu intacta apos login/reset, sem abrir bypass automatico por superusuario
