# ROADMAP FINANCEIRO

Data: 2026-03-26

## 1. Escopo inicial mapeado

### Cadastros principais
- contas financeiras
- centros de custo
- pessoas financeiras
- categorias financeiras

### Lancamentos financeiros
- receitas
- despesas
- transferencias entre contas
- filtros operacionais
- numeracao de documento
- validacoes condicionais

### Contratos, parcelas e recorrencia
- contratos a pagar
- contratos a receber
- geracao de parcelas
- recorrencia de lancamentos previstos

### Recibos
- emissao simples
- vinculo com lancamentos
- historico de recibos
- bloco historico inicial do tema; a base do recibo ja foi entregue e refinada no repositorio atual

### Relatorios e consultas
- resumo por periodo
- prestacao de contas
- consultas historicas por favorecido
- relatorios anuais
- balancete

### Extrato e saldo
- saldo inicial por conta
- saldo atual calculado
- extrato por conta
- saldo anterior por periodo

### Importacao de historico
- importacao de planilha historica
- saneamento de dados importados
- conciliacao inicial de base

### Usabilidade e interface
- autocomplete
- filtros uteis
- formularios condicionais
- impressao de relatorios
- fluxo operacional sem dependencia do admin

### Operacao e manutencao
- documentacao funcional
- etapas incrementais rastreaveis
- validacoes defensivas
- revisao de regras de negocio por tela

## 2. O que ja esta implementado

### Cadastros
- CRUD de contas financeiras
- CRUD de centros de custo
- CRUD de pessoas financeiras
- CRUD de categorias financeiras

### Lancamentos
- CRUD de lancamentos financeiros
- filtros por descricao, numero do documento, tipo e status
- filtros operacionais por data inicial, data final, conta, pessoa e categoria
- `numero_documento` manual quando informado pelo usuario
- `numero_documento` automatico quando vier vazio
- validacao para impedir repeticao de `numero_documento` em cadastro e edicao
- primeira versao de `Lancamento com rateio` sem documento pai, com `grupo_rateio` e validacao por `valor total do documento`
- segunda versao do rateio com redirecionamento estavel no create, `tipo` padrao em `receita`, sugestao automatica de `data_competencia` a partir de `data_pagamento` e consolidacao de categorias repetidas antes da gravacao
- a repeticao legitima de `numero_documento` no rateio ficou restrita a replicacao interna entre linhas do mesmo `grupo_rateio`, sem liberar coincidencia com documento independente
- a validacao do rateio agora tambem precisa preservar, na edicao individual, o mesmo `numero_documento` compartilhado pelas linhas do grupo

### Regras condicionais de transferencia
- transferencia nao exige pessoa
- transferencia nao exige categoria
- transferencia nao exige centro de custo
- transferencia exige conta de destino
- conta e conta de destino nao podem ser iguais
- conta de destino so pode ser usada em transferencia
- formulario limpa campos irrelevantes em transferencia
- listagem pode exibir `Transferencia entre Contas` quando nao houver pessoa

### Validacoes ja implantadas
- pessoa obrigatoria em receita e despesa
- categoria obrigatoria em receita e despesa
- categoria pai nao pode ser usada em lancamento; vinculacao passou a exigir subcategoria/categoria filha
- data de pagamento nao pode ser anterior a data de competencia
- erros de regra retornam ao formulario
- validacao de transferencia ocorre antes da gravacao
- duplicidade de `numero_documento` retorna erro claro no formulario

### Saldo inicial, extrato e saldo
- saldo inicial por conta
- data do saldo inicial obrigatoria
- saldo atual calculado em tempo de execucao
- extrato por conta
- extrato com filtro por periodo
- calculo de saldo anterior
- extrato e saldo real considerando apenas lancamentos efetivos
- consolidacao visual de rateios no extrato por `grupo_rateio`, com leitura do valor total do documento

### Resumo e prestacao de contas
- resumo consolidado por periodo
- prestacao de contas por periodo
- filtro por contas selecionadas
- agrupamento por categoria
- agrupamento de despesas por centro de custo
- controle de exibicao do bloco de centro de custo
- composicao inicial e final por conta
- acao de impressao em resumo e prestacao de contas
- exibicao curta das categorias quando a natureza ja estiver clara pelo contexto do relatorio

### Melhorias de UX ja feitas
- autocomplete real com busca por contem
- comportamento condicional do formulario de lancamento
- historico simples com os ultimos 5 lancamentos do favorecido no formulario de lancamento
- recibo em HTML imprimivel a partir do lancamento, com refinamentos posteriores de conteudo, assinatura, configuracao institucional e impressao
- mensagens de erro mais claras em campos obrigatorios
- layout mais compacto nas tabelas
- impressao refinada para extrato e prestacao de contas
- validacao manual real de impressao de `Extrato`, `Resumo` e `Prestacao de Contas` concluida com sucesso, sem necessidade de ajuste adicional nesta microetapa
- menu proprio para extratos, resumo e prestacao de contas

## 3. O que ja existe, mas ainda pode ser refinado

- comportamento de transferencia em todas as telas e relatorios
- UX do formulario de lancamento em casos limite
- base inicial da edicao coordenada do rateio ja implementada com view e formulario proprios do grupo, ainda pendente de refinamentos para a experiencia final
- modelagem documental mais rica do rateio, se necessario em etapa posterior
- acabamento operacional do rateio em edicao individual e leitura do grupo nas telas ja existentes
- estrategia aprovada para futura edicao coordenada do grupo rateado com view e formulario proprios, dados comuns em bloco e salvamento transacional
- regularizacao eventual de bases antigas de rateio sem `grupo_rateio` valido, caso precisem entrar na leitura consolidada do extrato
- a obrigatoriedade de `data_pagamento` ja foi consolidada no nivel de validacao da aplicacao; eventual endurecimento futuro do campo no banco depende apenas de estrategia segura para bases legadas
- expansao futura da auditoria de alteracoes no financeiro para alem de `LancamentoFinanceiro` e `ContaFinanceira`, ampliando o que ja existe para outras entidades do modulo e mantendo model proprio sem `signals`
- refinamentos futuros de leitura para a tela de auditoria de `LancamentoFinanceiro`, alem dos filtros simples ja implementados
- consistencia visual do tratamento de transferencia
- refinamento visual transversal do modulo financeiro para melhorar largura de campos, distribuicao de colunas, densidade de filtros, quantidade de informacao visivel por tela, melhor aproveitamento horizontal em zoom 100% e consistencia visual entre telas, agora oficialmente iniciado pela base compartilhada e pelas telas de listagem/formulario de lancamentos
- refinamentos futuros do shell visual do `financeiro` e da sidebar ja implantada, guiados por uso real e sem reabrir troca estrutural ampla da navegacao
- consolidacao futura de componentes visuais compartilhados do modulo, como cabecalho de pagina, bloco de filtros, card padrao, KPI, tabela e formulario
- telas de impressao, PDF e recibo ficam fora da primeira onda dessa padronizacao estrutural
- validacoes defensivas adicionais em fluxos operacionais
- extrato com mais contexto operacional sem poluir a tela
- filtros da listagem de lancamentos com melhorias de usabilidade
- acabamento documental futuro complementar dos relatorios impressos, apenas apos uso real, especialmente quando entrarem logo institucional e configuracao avancada de assinaturas
- evolucao futura da identidade institucional nos relatorios do financeiro, incluindo uso controlado de logo quando fizer sentido documental sem poluir a leitura operacional
- evolucao futura da logica de assinaturas em relatorios do financeiro:
  - permitir mais de uma assinatura cadastrada por relatorio que tenha assinatura
  - permitir configurar em cada relatorio se mostra assinatura
  - permitir configurar quais assinaturas ativas devem aparecer em cada relatorio
- item informativo futuro na tela de lancamentos, com simbolo `i` e historico de cadastro/alteracoes do documento ou lancamento quando houver ganho operacional real
- mapeamento e revisao futura das mensagens visiveis ao usuario no modulo `financeiro`, em alinhamento com a futura frente transversal do projeto
- integracao futura do `financeiro` com autenticacao e controle de acesso por usuario quando a frente estrutural do projeto for iniciada
- definicao futura de permissoes por acao dentro do `financeiro`, sem isolar essa governanca do restante do sistema
- convivencia futura do `financeiro` com administracao global centralizada de usuarios, perfis e permissoes, preservando a separacao entre cadastros globais e cadastros especificos do modulo
- POC controlada de uso de template pronto no shell do `financeiro`, apenas como experimento comparativo e sem adocao abrupta no projeto

## 4. O que ainda falta implementar

### Alta prioridade
- historico por favorecido
- relatorio anual por favorecido
- termo anual de quitacao
- contratos a pagar e a receber
- parcelas
- recorrencia
- anexos de comprovantes

### Media prioridade
- balancete padrao
- importacao de planilha historica
- cadastro rapido de pessoa dentro do lancamento
- cadastro rapido de categoria dentro do lancamento
- evolucoes futuras especificas do bloco de recibos ja entregue

## 5. Fila restante reorganizada por prioridade pratica

Observacao:
- esta secao reorganiza a fila restante sem substituir nem apagar as secoes `3` e `4`
- os itens abaixo permanecem futuros; a reorganizacao serve apenas para orientar prioridade pratica de execucao

### Imediato
- refinamentos futuros do shell visual do `financeiro` e da sidebar ja implantada, guiados por uso real e sem reabrir troca estrutural ampla da navegacao
- refinamento futuro do menu lateral para ficar mais leve, mais coerente com o tema, menos pesado visualmente e com item ativo mais elegante, reduzindo a sensacao de painel antigo sem trocar a sidebar como navegacao principal
- consolidacao futura de componentes visuais compartilhados do modulo, como cabecalho de pagina, bloco de filtros, card padrao, KPI, tabela e formulario
- refinamento visual transversal do modulo financeiro para melhorar largura de campos, distribuicao de colunas, densidade de filtros, quantidade de informacao visivel por tela, melhor aproveitamento horizontal em zoom 100% e consistencia visual entre telas, agora oficialmente iniciado pela base compartilhada e pelas telas de listagem/formulario de lancamentos
- auditoria e aplicacao incremental do novo padrao transversal de UX/comunicacao operacional no restante das telas do `financeiro`, com foco em fluxo continuo, texto fixo minimo, padronizacao de linguagem e uso raro do `i`
- nas proximas microetapas dessa frente, a decisao sobre shell/topo deve vir antes do refinamento do corpo das telas: em listagens e formularios operacionais, o `financeiro_shell_header` herdado precisa ser avaliado logo no inicio e pode exigir override enxuto quando gerar sensacao de corpo novo sob topo antigo
- POC controlada de tema/base visual pronta e leve, iniciando somente em `financeiro/templates/financeiro/lancamento_form.html` e sem expansao para outras telas antes de auditoria visual e funcional explicita
- comportamento de transferencia em todas as telas e relatorios
- consistencia visual do tratamento de transferencia
- UX do formulario de lancamento em casos limite
- validacoes defensivas adicionais em fluxos operacionais
- extrato com mais contexto operacional sem poluir a tela
- filtros da listagem de lancamentos com melhorias de usabilidade
- expansao futura da auditoria de alteracoes no financeiro para alem de `LancamentoFinanceiro` e `ContaFinanceira`, ampliando o que ja existe para outras entidades do modulo e mantendo model proprio sem `signals`
- refinamentos futuros de leitura para a tela de auditoria de `LancamentoFinanceiro`, alem dos filtros simples ja implementados
- mapeamento e revisao futura das mensagens visiveis ao usuario no modulo `financeiro`, em alinhamento com a futura frente transversal do projeto

### Proximo
- evolucao futura do cadastro de categorias para deixar explicito na propria UI se o usuario esta cadastrando `Categoria` ou `Subcategoria`, com possibilidade de seletor `Categoria | Subcategoria` e exibicao condicional do campo `Categoria`
- base inicial da edicao coordenada do rateio ja implementada com view e formulario proprios do grupo, ainda pendente de refinamentos para a experiencia final
- acabamento operacional do rateio em edicao individual e leitura do grupo nas telas ja existentes
- estrategia aprovada para futura edicao coordenada do grupo rateado com view e formulario proprios, dados comuns em bloco e salvamento transacional
- modelagem documental mais rica do rateio, se necessario em etapa posterior
- regularizacao eventual de bases antigas de rateio sem `grupo_rateio` valido, caso precisem entrar na leitura consolidada do extrato
- item informativo futuro na tela de lancamentos, com simbolo `i` e historico de cadastro/alteracoes do documento ou lancamento quando houver ganho operacional real
- historico por favorecido
- relatorio anual por favorecido
- cadastro rapido de pessoa dentro do lancamento
- cadastro rapido de categoria dentro do lancamento
- assistencia futura por regras no cadastro de lancamentos, com sugestao de regras existentes a partir de nome/descricao, preenchimento automatico revisavel de campos relacionados e possibilidade posterior de cadastrar nova regra a partir do proprio lancamento
- acao futura `Clonar lancamento`, abrindo novo cadastro preenchido com base no original e preservando o registro original sem alteracao
- evolucao futura dos relatorios financeiros para leitura hierarquica por `Categoria` e `Subcategoria`, preservando a distincao entre agrupador analitico e item operacional lancavel
- estudo futuro de agrupamento por categoria com comportamento de expandir/recolher grupos nos relatorios e visoes consolidadas
- estudo futuro de checkboxes para definir exibicao de `centro de custo`, `categoria` e `subcategoria` em relatorios e visoes agrupadas

### Posterior
- termo anual de quitacao
- contratos a pagar e a receber
- parcelas
- recorrencia
- anexos de comprovantes
- balancete padrao
- importacao de planilha historica
- evolucoes futuras especificas do bloco de recibos ja entregue
- a obrigatoriedade de `data_pagamento` ja foi consolidada no nivel de validacao da aplicacao; eventual endurecimento futuro do campo no banco depende apenas de estrategia segura para bases legadas
- acabamento documental futuro complementar dos relatorios impressos, apenas apos uso real, especialmente quando entrarem logo institucional e configuracao avancada de assinaturas
- evolucao futura da identidade institucional nos relatorios do financeiro, incluindo uso controlado de logo quando fizer sentido documental sem poluir a leitura operacional
- permitir mais de uma assinatura cadastrada por relatorio que tenha assinatura
- permitir configurar em cada relatorio se mostra assinatura
- permitir configurar quais assinaturas ativas devem aparecer em cada relatorio

## 7. Consolidacao desta microetapa de acabamento documental

- `Extrato`, `Resumo` e `Prestacao de Contas` passaram a compartilhar cabecalho documental de impressao/PDF mais coerente, com identidade institucional leve, metadados visiveis e hierarquia visual menos tecnica.
- `Prestacao de Contas` recebeu bloco final de assinatura mais formal, ainda simples e sem antecipar a futura frente de multiplas assinaturas.
- a base atual de impressao/PDF dos tres relatorios deve ser tratada como padrao funcional e visual desta etapa; backlog futuro relacionado fica restrito a logo institucional, configuracao de assinaturas e eventual acabamento complementar por uso real
- nesta microetapa nao houve alteracao de regra de negocio nem ampliacao de escopo funcional dos relatorios

## 8. Refino posterior de identidade e margens dos relatorios

- o uso de sigla como pseudo-logo deixou de ser diretriz aceitavel para os relatorios impressos do `financeiro`
- a base atual passou a priorizar logo institucional quando existir e, na ausencia dela, usar apenas o nome institucional no cabecalho documental
- a etapa tambem reforcou margens e respiro do documento impresso, mantendo o shell isolado e melhorando o aproveitamento visual do `Extrato`
- backlog futuro de acabamento final continua restrito a logo institucional melhor curada por uso real, multiplas assinaturas e configuracao por relatorio, sem reabrir regra de negocio

## 9. Refino documental do recibo e da leitura do saldo acumulado

- o recibo passou a adotar topo mais limpo e institucional, com titulo principal unico, numero em linha secundaria e mensagem central com maior protagonismo
- no recibo, a logo agora deve liderar a identidade visual quando existir; o nome institucional permanece apenas como fallback discreto quando nao houver logo utilizavel
- o `saldo acumulado` do extrato passou a usar leitura visual por sinal, alinhada ao vocabulario de valores positivos e negativos ja usado no modulo
- backlog futuro do bloco de recibos continua restrito a evolucoes especificas posteriores, sem reabrir regra de negocio nem o escopo funcional entregue

## 10. Reforco documental de margens, bordas e identidade visual

- a base atual dos relatorios impressos e do recibo passou a usar margens de pagina mais abertas, quadro documental mais explicito e respiro interno mais perceptivel
- os relatorios passaram a evitar repeticao desnecessaria do nome institucional quando a logo ja esta presente de forma suficiente no cabecalho
- backlog futuro de acabamento permanece restrito a curadoria fina por uso real, multiplas assinaturas e configuracao futura da identidade visual global do sistema

## 11. Frentes futuras documentais relacionadas

- futura configuracao da paleta geral do sistema, com definicao de cor principal e derivacao coerente da paleta relacionada, sem aplicacao manual de cor solta em cada tela
- futuro log de acesso ao sistema em camada estrutural propria, separado da auditoria funcional do `financeiro`
- revisao futura da posicao do `Extrato` na navegacao do modulo, sem decisao de mudanca nesta etapa

## 12. Auditoria inicial da frente transversal de UX/comunicacao operacional

- telas hoje mais alinhadas ao padrao: `lancamento_form.html`, `lancamento_rateio_grupo_form.html`, `lancamento_list.html`, `conta_extrato.html`, `resumo.html`, `prestacao_contas.html` e `lancamento_recibo.html`
- telas com maior necessidade de padronizacao futura: `home.html`, `auditoria_lancamento_list.html`, `conta_list.html`, `pessoa_list.html`, `categoria_list.html`, `centro_custo_list.html` e respectivos formularios auxiliares ainda nao revisitados
- os desvios mais recorrentes nessa auditoria inicial foram: subtitulos e explicacoes acima do necessario, segmentacao visual mais antiga, headings e labels menos consistentes, estados vazios crus e acentuacao/linguagem ainda nao uniformizadas em todas as listas e cadastros
- ordem recomendada de aplicacao no restante do `financeiro`: 1) `home.html`; 2) `auditoria_lancamento_list.html`; 3) listas principais de cadastros auxiliares (`conta`, `pessoa`, `categoria`, `centro_custo`); 4) formularios auxiliares; 5) consolidacao final de componentes compartilhados para reaproveitamento transversal
- esse mesmo padrao deve orientar tanto futuros ajustes nas telas existentes quanto novos itens e novas telas que entrarem no sistema, evitando reintroducao de excesso de texto, `i` disperso e empilhamento desnecessario de blocos

## 13. Reclassificacao estrutural da home do modulo financeiro

- a `home.html` do `financeiro` deixa de ser tratada como entrada principal do modulo e passa a ser considerada rota secundaria explicita, porque a sidebar ja cobre a navegacao estrutural e a tela nao justifica uma camada intermediaria propria
- a entrada correta do modulo passa a ser a listagem principal de lancamentos, o que reduz redundancia e alinha a navegacao com a diretriz transversal de fluxo operacional direto
- com essa decisao, a fila imediata da auditoria transversal deixa de comecar por `home.html` e passa a seguir por `auditoria_lancamento_list.html`, depois `conta_list.html`, `pessoa_list.html`, `categoria_list.html`, `centro_custo_list.html` e respectivos formularios auxiliares
- a antiga home so deve voltar a ganhar protagonismo estrutural se um dashboard operacional real vier a existir em etapa futura propria e justificada

### Estrutural futura
- integracao futura do `financeiro` com autenticacao e controle de acesso por usuario quando a frente estrutural do projeto for iniciada
- definicao futura de permissoes por acao dentro do `financeiro`, sem isolar essa governanca do restante do sistema
- convivencia futura do `financeiro` com administracao global centralizada de usuarios, perfis e permissoes, preservando a separacao entre cadastros globais e cadastros especificos do modulo
- frente estrutural futura de usuarios, login, perfis e permissoes, com centralizacao progressiva de autenticacao, acesso e governanca entre modulos
- possibilidade futura de unificacao de cadastros compartilhados, incluindo base comum de pessoas e outras entidades transversais quando isso fizer sentido para o sistema como um todo
- permissões, acesso, login e perfis continuam explicitamente como frente futura e nao entram por microetapas locais desta frente visual/operacional do `financeiro`

### Experimental
- POC controlada de uso de template pronto no shell do `financeiro`, apenas como experimento comparativo e sem adocao abrupta no projeto
- telas de impressao, PDF e recibo ficam fora da primeira onda dessa padronizacao estrutural

### Prioridade imediata atual
- a frente imediata prioritaria deixa de ser novos microajustes incrementais no layout atual de `lancamento_form.html`
- a proxima microetapa correta passa a ser uma POC visual controlada com base no **Tabler** apenas em `financeiro/templates/financeiro/lancamento_form.html`
- essa tela piloto deve preservar integralmente regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos, comportamento atual do formulario e logica de exibicao/ocultacao do rateio
- recomposicoes manuais locais anteriores do `lancamento_form.html` nao contam como execucao valida dessa POC e devem ser tratadas apenas como montagem intermediaria a ser reaproveitada ou descartada de forma controlada antes da adocao real do tema-base
- a expansao do Tabler para outras telas do `financeiro` ou para outros modulos fica bloqueada ate auditoria visual e funcional real da primeira tela piloto
- so depois de validada essa POC na tela piloto o projeto pode decidir por continuidade, abandono da base ou customizacoes pontuais por cima dela

### Sequencia linear anteriormente sugerida
1. consulta historica por favorecido
2. relatorio anual por favorecido
3. contratos previstos a pagar e a receber
4. parcelas e recorrencia
5. anexos de comprovantes
6. balancete padrao
7. importacao historica
8. evolucoes futuras especificas do bloco de recibos ja entregue

Observacao semantica do backlog:
- os itens da secao `3. O que ja existe, mas ainda pode ser refinado` representam base ja entregue com espaco para refinamento futuro
- os itens da secao `4. O que ainda falta implementar` representam frentes ainda nao entregues como bloco consolidado
- os itens da secao `5. Proximas etapas sugeridas` indicam apenas ordem sugerida de trabalho e nao reclassificam entregas ja concluidas

## 6. Diretriz importante

Este roadmap nao altera nenhuma regra de negocio ja aprovada nem substitui o estado real do repositorio.

Ele serve apenas para:
- consolidar o escopo financeiro ja mapeado
- registrar o que ja foi entregue
- organizar o que ainda falta
- orientar proximas etapas pequenas, seguras e incrementais
