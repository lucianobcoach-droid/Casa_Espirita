# CODEX_RESULTADO

Data: 2026-05-06

## Microetapa documental: frente futura de tabelas de controle personalizadas

- etapa exclusivamente documental, sem alteracao de codigo
- consolidado registro da nova frente futura `Tabelas de controle personalizadas` como backlog separado da frente de frequencia por competencia
- direcao registrada para fase futura:
  - criacao de tabelas configuraveis
  - colunas personalizadas com tipos de coluna
  - formulas controladas entre colunas
  - linhas de controle para uso interno
  - possibilidade futura de vinculo com financeiro/pessoas/categorias, sem acoplamento imediato
- regra de governanca registrada:
  - nao implementar nesta etapa
  - nao misturar com frequencia mensal por competencia
  - abrir auditoria e SPEC propria antes de qualquer modelagem/migration
- riscos documentados: complexidade alta, risco de "Excel dentro do sistema", limites de formula por seguranca, necessidade de permissoes e auditoria de alteracoes, estrategia de backup/exportacao e risco de misturar dado operacional com financeiro oficial

## Microetapa documental: validacao da alocacao de competencias mensais

- etapa exclusivamente documental, sem alteracao de codigo
- registrado aceite da usuaria para a alocacao de competencias no lancamento simples
- validado:
  - exibicao condicional do bloco `Competencias atendidas`
  - registro por `mes/ano + valor`
  - salvamento com soma fechada
  - bloqueio com soma divergente
- registrado tambem:
  - edicao recarrega competencias existentes
  - clone comum nao copia competencias
  - rateio por item controlado permanece pendente
  - ainda nao ha matriz mensal
- confirmado que nao houve alteracao de calculo financeiro, saldos ou relatorios existentes

## Microetapa: alocacao de competencias mensais no lancamento

- implementei o model `AlocacaoCompetenciaFinanceira` ligado a `LancamentoFinanceiro`, com subcategoria controlada, mes/ano da competencia e valor alocado
- no formulario de lancamento comum, o bloco `Competencias atendidas` agora aparece quando o favorecido e recorrente e a subcategoria controla recorrencia por competencia
- a soma das competencias passou a ser validada contra o valor controlado do lancamento; soma divergente retorna erro claro e bloqueia o salvamento
- em edicao, as competencias cadastradas voltam preenchidas; em clone comum, elas nao sao carregadas para evitar duplicidade de competencia
- mantive o rateio sem improviso: a modelagem ficou pronta para uso futuro por item controlado, mas a criacao inicial do grupo rateado nao passou a capturar competencias nesta microetapa
- criei migration propria e testes de model/form/cascade/clone/rateio para sustentar a evolucao futura
- nao alterei calculo financeiro, saldos, Balancete, Extrato, Fechamento/Prestacao, importacao de lancamentos nem relatorios novos

## Consolidacao de SPEC - controle de contribuicao mensal por competencia

- etapa exclusivamente documental/tecnica, sem implementacao funcional
- consolidei a SPEC do MVP de competencia mensal considerando lancamento simples e lancamento com rateio
- fechei a direcao de modelagem para nao usar checkbox puro e adotar alocacao por competencia com `mes/ano + valor`
- fechei a regra de rateio: frequencia usa apenas o valor da parte/subcategoria que controla frequencia, sem reaproveitar automaticamente o valor total do documento
- registrei que matriz com valores e a base e matriz sem valores deriva dela
- registrei que o lancamento financeiro segue como origem do dinheiro no MVP e que modulo separado de baixa nao entra na primeira onda
- termo por favorecido ficou documentado como segunda onda apos validacao da matriz
- nao houve alteracao de codigo, models, migrations, views, forms, templates, tests, CSS, calculos financeiros ou comportamento dos relatorios atuais

## Correcao do cabecalho de contas selecionadas no Extrato impresso

- corrigi o cabecalho do Extrato impresso/PDF para mostrar identificacao clara das contas selecionadas
- com uma unica conta selecionada, o cabecalho agora exibe o nome da conta, removendo a identificacao generica `1 conta selecionada`
- com 2 ou 3 contas selecionadas, o cabecalho exibe os nomes das contas
- com mais de 3 contas selecionadas, o cabecalho usa resumo `X contas selecionadas` para evitar poluicao visual
- mantive comportamento seguro para todas as contas selecionadas (`Todas as contas financeiras`)
- adicionei testes para cobranca de cabecalho (1 conta, ate 3 contas por nome, muitas contas com resumo) e preservacao dos saldos finais esperados
- nao houve alteracao de calculo financeiro, saldo, lancamentos, transferencias, Balancete, Fechamento/Prestacao ou importacao/exportacao

## Refinamento do Balancete por publico e composicao

- implementei a arquitetura do Balancete por `Formato do Balancete`, substituindo o filtro solto de vinculadas/indisponiveis por tres formatos reais de uso: `Operacional`, `Operacional + patrimonio vinculado` e `Financeiro completo`
- no formato `Operacional`, o relatorio agora mostra apenas o universo disponivel e continua tratando transferencias com saldo vinculado como movimentacao especifica de fronteira
- no formato `Operacional + patrimonio vinculado`, acrescentei bloco patrimonial complementar separado do resumo operacional, com opcao de detalhamento do patrimonio vinculado
- no formato `Financeiro completo`, mantive a leitura total da instituicao e removi da interface qualquer dependencia do filtro antigo de exibir/ocultar vinculadas
- mantive o mesmo filtro de composicao para saldo inicial e saldo final dentro do formato ativo e preservei a base de calculo do Fechamento/Prestacao sem alteracao funcional

- registrei documentalmente a nova arquitetura funcional do Balancete por `Formato do Balancete`, com tres formatos: `Operacional`, `Operacional + patrimonio vinculado` e `Financeiro completo`
- registrei que os filtros complementares passam a ser dependentes do formato escolhido e que o filtro antigo `Exibir contas vinculadas/indisponiveis` deve ser substituido por essa logica orientada por intencao
- formalizei que, no formato operacional, transferencias entre disponivel e vinculado entram no resumo como movimentacao especifica de fronteira e nao como receita/despesa operacional
- formalizei que, no formato operacional + patrimonio vinculado, o bloco patrimonial deve aparecer separado do resumo operacional
- formalizei que, no formato financeiro completo, a leitura e total da instituicao e nao deve depender de filtro de ocultacao de vinculadas
- esta microetapa foi exclusivamente documental, sem implementacao de codigo; a aplicacao funcional fica para proxima SPEC

- corrigi a leitura do Balancete quando `Exibir vinculadas/indisponiveis = Nao`: o documento passa a representar apenas o saldo disponivel operacional
- nesse modo, saldo indisponivel/vinculado, contas indisponiveis e mensagens explicativas dessas contas ficam totalmente fora da apresentacao
- transferencias entre conta disponivel e conta vinculada/indisponivel passaram a aparecer no resumo operacional como movimentacao especifica de fronteira do saldo disponivel, sem virar receita nem despesa operacional
- preservei o modo completo quando `Exibir vinculadas/indisponiveis = Sim`, mantendo saldo disponivel, saldo indisponivel/vinculado, saldo financeiro total e mensagens apenas para contas efetivamente exibidas

- corrigi a sequencia documental do Balancete para abrir com `Saldo inicial financeiro`, seguir com `Entradas do periodo`, `Saidas do periodo`, `Resumo operacional do periodo`, `Composicao do saldo final` e `Assinaturas`
- tirei a composicao do saldo inicial de dentro do resumo e mantive inicio e fim obedecendo ao mesmo filtro `Composicao do saldo`
- removi a mensagem `Contas vinculadas/indisponiveis nao exibidas nesta composicao...` quando a opcao de exibir vinculadas/indisponiveis esta desligada
- preservei a opcao de mostrar mensagens explicativas apenas para contas indisponiveis/vinculadas que estejam efetivamente sendo exibidas no documento

- removi o filtro separado `Detalhar saldo inicial por conta`, pois ele ficou redundante diante do proprio filtro `Composicao do saldo`
- alinhei a apresentacao do saldo inicial ao mesmo modo da composicao final: detalhada por conta, consolidada por tipo de conta ou total consolidado
- mantive a opcao de exibir/ocultar vinculadas/indisponiveis valendo para as duas pontas, sem alterar calculo financeiro, saldo, lancamentos, Extrato ou Fechamento/Prestacao
- preservei o resumo financeiro sintetico e passei a usar o mesmo criterio patrimonial para a composicao inicial e final quando a apresentacao detalhada aparece no documento

- removi do Balancete o filtro `Modelo do relatorio`, pois a distincao pratica entre as leituras ficou melhor resolvida pelos filtros reais de composicao, exibicao de vinculadas/indisponiveis e detalhamento do saldo inicial
- mantive os filtros `Composicao do saldo` e `Exibir vinculadas/indisponiveis`, com padrao de composicao em `Consolidada por tipo de conta`
- retirei do cabecalho impresso a exposicao desses filtros, deixando o documento mais institucional e limpo
- ajustei a observacao de ocultacao para aparecer apenas quando as contas vinculadas/indisponiveis nao sao exibidas, usando a redacao `nesta composicao`
- preservei a compactacao do impresso e a sequencia documental, sem alterar calculo financeiro, saldo, lancamentos, Extrato ou Fechamento/Prestacao

- na etapa anterior, havia sido adicionada a camada de modelos por publico; nesta microetapa, ela foi simplificada e absorvida pelos filtros diretos realmente uteis
- implementei tres modos de composicao do saldo final: detalhada por conta, consolidada por tipo de conta e total consolidado
- acrescentei opcao para exibir ou ocultar contas vinculadas/indisponiveis apenas no documento, sem alterar calculo financeiro ou saldo final real
- removi o controle separado do saldo inicial e reorganizei o impresso para reduzir repeticao entre resumo e composicao patrimonial
- compacteI o layout do Balancete com fonte menor, menos padding e sequencia documental mais direta, buscando melhor aproveitamento de uma pagina quando o volume permitir
- mantive Fechamento/Prestacao, Extrato, lancamentos, transferencias, saldos e base de calculo sem alteracao funcional

## Leitura patrimonial no Balancete Institucional

- apliquei a leitura patrimonial apenas no Balancete Institucional, reaproveitando a composicao final ja calculada pela base compartilhada do Fechamento/Prestacao
- separei a apresentacao do saldo final entre saldo disponivel operacional e saldo indisponivel/vinculado, preservando o modo detalhado por conta
- mantive o saldo total financeiro igual ao total final ja calculado, sem alterar lancamentos, saldos, transferencias, Extrato, Fechamento/Prestacao ou calculo financeiro
- passei a exibir mensagem explicativa discreta apenas para contas indisponiveis/vinculadas com `mensagem_indisponibilidade` preenchida
- adicionei testes para classificacao por disponibilidade, integralizacao indisponivel, mensagem opcional e isolamento da leitura patrimonial fora da Prestacao

## Ajuste de nomenclatura dos tipos padrao de conta

- ajustei a nomenclatura do tipo com codigo `aplicacao_financeira` para exibir `Conta investimento`
- mantive `Integralizacao de capital` como nomenclatura oficial, sem barra nem complemento `conta capital`
- registrei que a conta de integralizacao pode ser cadastrada normalmente e que a futura separacao no Balancete sera determinada por `disponibilidade`
- nao alterei Balancete, Fechamento/Prestacao, Extrato, lancamentos, saldos, transferencias, importacao/exportacao de lancamentos ou calculos financeiros

## Base cadastral patrimonial das contas financeiras

- implementei `TipoContaFinanceira` como cadastro proprio simples e acrescentei em `ContaFinanceira` os campos de tipo, disponibilidade total e mensagem explicativa opcional
- gerei migration com carga inicial idempotente dos tipos aprovados e default seguro para contas existentes
- atualizei form, cadastro/listagem de contas e importacao/exportacao auxiliar de contas para contemplar os novos campos, preservando planilha legada de contas com defaults
- adicionei testes especificos para tipos padrao, form de conta disponivel/indisponivel, mensagem opcional, importacao nova/legada e exportacao auxiliar
- mantive Balancete, Fechamento/Prestacao, Extrato, lancamentos, rateios, saldos, transferencias, permissoes e calculos financeiros sem alteracao funcional

## Auditoria tecnica preparatoria do MVP patrimonial

- auditei tecnicamente a base atual de contas, Balancete, Fechamento/Prestacao, templates, rotas, testes e importacao/exportacao relacionados a `ContaFinanceira`
- confirmei que o model atual de conta ainda nao possui tipo, disponibilidade patrimonial nem mensagem explicativa; esses pontos continuam futuros
- confirmei que o Balancete Institucional usa `BalanceteInstitucionalFinanceiroView` e reaproveita `montar_contexto_fechamento_periodo`, preservando a base comum do Fechamento/Prestacao
- mapeei os arquivos candidatos para futura implementacao: `financeiro/models.py`, `forms.py`, `views.py`, `urls.py`, `tests.py`, templates de conta e Balancete, e pontos de importacao/exportacao auxiliar de contas
- registrei que a proxima microetapa funcional minima deve tratar primeiro modelagem/cadastro simples de tipo de conta e campos simples em `ContaFinanceira`, sem alterar calculos ou relatorios fora do Balancete
- nao alterei codigo funcional, models, migrations, forms, views, urls, templates, tests, CSS, banco de dados ou calculos financeiros

## Decisoes funcionais do MVP patrimonial

- registrei as decisoes funcionais aprovadas para o MVP patrimonial antes de qualquer implementacao tecnica
- consolidei que o tipo de conta financeira deve ser cadastro proprio simples, com tipos iniciais sugeridos para carga futura
- registrei que a disponibilidade/vinculacao sera total por conta no MVP, mantendo disponibilidade parcial como evolucao futura
- registrei que a mensagem explicativa de indisponibilidade/vinculacao ficara no cadastro da conta e so aparecera no Balancete quando preenchida
- defini documentalmente o modo padrao do Balancete patrimonial como detalhado por conta, com separacao visual entre disponivel e indisponivel/vinculado quando aplicavel
- delimitei o escopo da primeira implementacao futura e o que fica fora do MVP, preservando a base de calculo do Fechamento/Prestacao
- nao alterei codigo funcional, models, migrations, views, forms, templates, tests, CSS, banco de dados ou calculos financeiros

## Regras reutilizaveis e especificacao do Balancete patrimonial

- registrei governanca permanente para que toda regra de negocio aprovada seja documentada em `docs/REGRAS_NEGOCIO.md`
- detalhei que regras reutilizaveis devem registrar comportamento esperado, excecoes, impactos em cadastros/relatorios, racional e possibilidade de reaproveitamento em outros projetos
- especifiquei a frente futura de tipo/disponibilidade de conta e Balancete patrimonial, incluindo tipos iniciais, diferenca entre ativa/inativa e disponivel/indisponivel, integralizacao de capital e mensagem explicativa por conta
- documentei modos futuros de exibicao do saldo: detalhado por conta, consolidado por tipo de conta, total consolidado e separado entre disponivel e indisponivel/vinculado
- registrei a regra de agrupamento por tipo de conta e a seguranca de reaproveitar a base do Fechamento/Prestacao sem calculo divergente
- consolidei a modelagem funcional no roadmap, incluindo impactos futuros em cadastro de contas, Balancete, relatorios e regras de negocio, alem das decisoes pendentes antes da implementacao
- nao alterei codigo funcional, models, migrations, views, forms, templates, tests, CSS ou regras financeiras executaveis

## Homologacao progressiva do financeiro

- registrei decisao documental de que a homologacao funcional do financeiro ocorreu de forma progressiva durante o desenvolvimento das microetapas
- ajustei a classificacao da homologacao ponta a ponta para `HOMOLOGACAO PROGRESSIVA REALIZADA / USO REAL ACOMPANHADO`
- mantive como acompanhamento futuro a validacao com massa definitiva, planilhas historicas completas, relatorios impressos em volume real e rotina diaria da Casa
- preservei como homologados os ajustes ja testados localmente: listagem de lancamentos multi-contas, favorecido tecnico no Extrato, diferenca a detalhar no rateio e contas inativas em consultas historicas
- nao alterei codigo funcional, views, urls, models, forms, templates, migrations, tests, CSS ou regras financeiras

## Checkpoint documental do financeiro

- registrei checkpoint curto do estado atual do modulo financeiro apos auditorias, baixas documentais, correcoes funcionais e homologacoes locais recentes
- consolidei como homologados: filtro multi-contas na listagem de lancamentos, favorecido tecnico no Extrato, diferenca a detalhar no rateio e contas inativas em consultas historicas
- destaquei como implementados com pendencias futuras ou homologacao ampla: Balancete Institucional, importacoes/cadastros auxiliares, autenticacao/perfis/permissoes e relatorios impressos sujeitos a validacao visual por uso real
- registrei os principais futuros reais ainda abertos, incluindo a opcao visual do Extrato multi-contas para detalhar transferencias internas, tipo/disponibilidade de conta, recorrencia/frequencia, contratos/parcelas, anexos e tabelas personalizadas
- indiquei como proxima prioridade recomendada a homologacao ponta a ponta do financeiro local antes de abrir frente grande de modelagem
- nao alterei codigo funcional, regras financeiras, views, urls, models, forms, templates, migrations, tests ou CSS

## Homologacao local e melhoria futura do Extrato multi-contas

- registrei a homologacao local da usuaria como OK para: listagem de lancamentos multi-contas, favorecido tecnico no Extrato, diferenca a detalhar no rateio e filtros historicos de contas inativas
- acrescentei no roadmap uma melhoria futura para o Extrato multi-contas permitir, opcionalmente, detalhar transferencias internas em duas linhas operacionais para conferencia
- registrei no mapa essa frente como FUTURO REAL / MELHORIA DE UX, sem marcar como erro da implementacao atual
- preservei a regra atual do Extrato consolidado: transferencias internas ao escopo selecionado se anulam e nao inflam o saldo consolidado
- nao alterei codigo funcional, views, templates, forms, tests, CSS, calculos financeiros, relatórios ou comportamento do Extrato

## Filtro multi-contas na listagem de lancamentos

- implementei selecao de uma, varias ou todas as contas na listagem de lancamentos, reaproveitando o dropdown de contas ja usado no modulo financeiro
- ajustei a filtragem para considerar conta origem e conta destino, preservando compatibilidade com o parametro antigo `conta`
- mantive transferencias internas entre contas selecionadas visiveis na listagem, por se tratar de leitura operacional/documental dos lancamentos reais
- adicionei testes pontuais para conta unica, duas contas, origem, destino, transferencia interna, todas as contas, combinacao com status e compatibilidade com parametro antigo
- baixei a pendencia no `MAPA_RECLASSIFICACAO.md` como IMPLEMENTADO e atualizei `ROADMAP_FINANCEIRO.md` e `REGRAS_NEGOCIO.md`
- nao alterei calculo financeiro, saldos, Extrato, Resumo, Prestacao/Fechamento, Balancete, Evolucao, importacao/exportacao ou models

## Filtros historicos de contas inativas

- criei helper para montar contas historicas de filtro com contas ativas sempre e contas inativas apenas quando houver movimento no periodo/escopo
- apliquei o filtro na base compartilhada de Resumo, Prestacao/Fechamento e Balancete, em Evolucao por categorias, Extratos, Historico por favorecido e listagem de lancamentos
- mantive o criterio de movimento por conta origem ou conta destino em transferencia, usando data de pagamento com fallback para competencia
- adicionei teste pontual para confirmar conta ativa visivel, conta inativa com movimento no periodo visivel, conta inativa sem movimento/fora do periodo oculta e selecao historica preservada
- baixei a pendencia no `MAPA_RECLASSIFICACAO.md` como IMPLEMENTADO e atualizei `ROADMAP_FINANCEIRO.md` e `REGRAS_NEGOCIO.md`
- nao alterei calculo financeiro, saldo, models, migrations, importacao/exportacao ou regras de novos lancamentos

## Refinamento visual da diferenca do rateio

- alinhei o valor de `DIFERENCA A DETALHAR` com a coluna de valores das linhas de rateio, usando uma linha de rodape da propria tabela
- simplifiquei o apoio visual do rateio para manter apenas o bloco `DIFERENCA A DETALHAR`
- removi da interface os cards de valor total do documento e total rateado
- mantive atualizacao dinamica da diferenca, com vermelho quando houver diferenca e alerta textual apenas quando o rateio ultrapassar o total do documento
- nao alterei validacao, persistencia, calculos financeiros, saldos, importacao/exportacao, relatorios, recibos, termos, Extrato, Balancete ou Prestacao

## Diferenca restante no rateio

- adicionei resumo dinamico de fechamento no formulario de novo lancamento com rateio e na edicao coordenada do grupo
- o resumo exibe valor total do documento, total rateado e diferenca restante, com mensagens simples para rateio fechado, faltando ratear ou ultrapassando o total
- mantive a alteracao restrita ao apoio visual/operacional do rateio, sem alterar validacao, persistencia, calculos, saldos, importacao/exportacao ou relatorios
- baixei a pendencia no `MAPA_RECLASSIFICACAO.md` como IMPLEMENTADO e atualizei o `ROADMAP_FINANCEIRO.md`

## Favorecido tecnico em transferencia no Extrato

- ajustei a montagem dos itens do Extrato para exibir `TRANSFERÊNCIA ENTRE CONTAS` quando a movimentacao for transferencia sem favorecido operacional
- preservei o favorecido real quando houver pessoa vinculada ao lancamento
- adicionei teste pontual no Extrato multi-contas cobrindo a exibicao padronizada em transferencias
- baixei documentalmente a pendencia como IMPLEMENTADO no `MAPA_RECLASSIFICACAO.md` e atualizei a regra permanente em `REGRAS_NEGOCIO.md`
- nao alterei calculo financeiro, saldo, regra de transferencia, importacao/exportacao, recibos, termo anual, Balancete ou outros relatorios

## Auditoria de importacao historica e cadastros auxiliares

- auditei documentos e codigo da frente de importacao/exportacao do financeiro, incluindo views, rotas, modelos/forms, template da central, backups tecnicos e comando de reset controlado
- confirmei implementados: central de importacoes, importacao/exportacao comum de lancamentos, modelos XLSX, cadastros auxiliares, trava de dominio vazio, validacao estrutural, validacao linha a linha com rotulos amigaveis, relatorio de inconsistencias e gravacao transacional all-or-nothing
- confirmei suporte a lancamentos simples, transferencias simples e rateio em ate 5 blocos na mesma linha; rateios maiores permanecem limitacao conhecida do fluxo comum e dependem do caminho tecnico de backup/restauracao
- reclassifiquei a frente no `MAPA_RECLASSIFICACAO.md` como IMPLEMENTADO COM PENDENCIAS FUTURAS / AGUARDANDO HOMOLOGACAO
- mantive como futuras: preview operacional antes de gravar, importacao parcial, preflight mais visivel, tratamento avancado de duplicidades e homologacao com planilhas historicas reais
- nao alterei codigo funcional, views, urls, models, forms, templates, migrations, testes, CSS ou calculos financeiros

## Baixa documental de pendencias implementadas do financeiro

- auditei no codigo e nos documentos as pendencias antigas de favorecido duplicado, edicao de conta, logo no Extrato impresso, impressao da Prestacao/Fechamento, filtro de contas nas telas analiticas e regra geral de identificadores-chave
- reclassifiquei `Favorecido duplicado por nome` como IMPLEMENTADO, incluindo cadastro/edicao e importacao auxiliar
- reclassifiquei `Edicao de conta sem saldo inicial/data ja preenchidos` como IMPLEMENTADO
- reclassifiquei a logo do Extrato impresso como IMPLEMENTADO / AGUARDANDO VALIDACAO VISUAL
- reclassifiquei a padronizacao do filtro de contas como IMPLEMENTADO NAS TELAS ANALITICAS, mantendo a listagem de lancamentos como futuro separado
- reclassifiquei a impressao da Prestacao/Fechamento como IMPLEMENTADO / AGUARDANDO VALIDACAO VISUAL
- mantive a regra geral de identificadores-chave como DIRETRIZ IMPLEMENTADA / APLICACAO PROGRESSIVA FUTURA
- nao alterei codigo funcional, regras financeiras, views, urls, models, forms, templates, migrations, testes ou CSS

## Auditoria de autenticacao, perfis e permissoes

- auditei documentos e codigo relacionados a autenticacao, perfis e permissoes nos apps `configuracoes`, `financeiro` e `biblioteca`
- confirmei que login/logout e recuperacao/reset de senha estao implementados no app `configuracoes`
- confirmei que existem models de permissao/perfil/vinculo, seed inicial por migrations, mixin central de permissao, mixins por app e template tags para renderizacao condicional
- confirmei que o financeiro, a biblioteca e as configuracoes usam permissoes no backend e nos templates principais
- atualizei `MAPA_RECLASSIFICACAO.md`, `STATE.md`, `CEREBRO_PROJETO.md` e `MATRIZ_PERMISSOES.md` para baixar a frente de duvida para IMPLEMENTADO COM PENDENCIAS FUTURAS
- nao alterei codigo funcional, models, views, urls, forms, templates, migrations, testes, banco de dados ou regras financeiras

## Baixa documental do Balancete e rotina de pendencias

- criei `docs/ROTINA_BAIXA_PENDENCIAS.md` com objetivo, status padronizados, criterios de baixa, documentos a atualizar, regras de seguranca e relacao com Git/GitHub
- atualizei `AGENTS.md`, `INDICE_PROJETO.md` e `CEREBRO_PROJETO.md` para registrar a rotina permanente de baixa documental
- registrei no `ROADMAP_FINANCEIRO.md` e no `MAPA_RECLASSIFICACAO.md` a baixa detalhada do Balancete Institucional contra o conceito acordado
- classifiquei o MVP do Balancete como entregue em seu bloco principal, com validacao visual/uso real e modelagem futura ainda acompanhadas separadamente
- atualizei o `STATE.md` com nota curta da consolidacao documental
- nao alterei codigo funcional, regras financeiras, views, urls, models, forms, templates, testes ou CSS

## Auditoria documental do Balancete Institucional

- auditei os registros do Balancete em `CEREBRO_PROJETO.md`, `STATE.md`, `ROADMAP_FINANCEIRO.md`, `MAPA_RECLASSIFICACAO.md`, `REGRAS_NEGOCIO.md` e `CODEX_RESULTADO.md`
- confirmei que as diretrizes permanentes ja registram o Balancete como relatorio proprio, sem substituir a Prestacao/Fechamento, reutilizando a mesma base de calculo
- confirmei que fundo branco, aparencia documental, composicao final, assinaturas, tipo de conta, disponibilidade/vinculacao, integralizacao de capital e modos futuros de composicao ja estavam documentados
- ajustei cirurgicamente o `ROADMAP_FINANCEIRO.md` e o `MAPA_RECLASSIFICACAO.md` para classificar o Balancete como parcialmente implementado, mantendo como futuras as evolucoes de modelagem e composicao
- registrei nota curta no `STATE.md`
- nao alterei codigo funcional, views, urls, models, forms, templates, testes, CSS ou calculos financeiros

## Rotina oficial Git/GitHub

- registrei a governanca permanente de versionamento local x GitHub
- criei `docs/ROTINA_GIT_GITHUB.md` com a rotina operacional segura para conferir branch, status, commits locais, commits remotos e executar push somente quando seguro
- atualizei `AGENTS.md` para exigir informacao explicita de commit/push e tratar commit local sem push como pendencia de sincronizacao
- atualizei `INDICE_PROJETO.md` e `CEREBRO_PROJETO.md` para apontar o GitHub remoto como memoria oficial compartilhada e registrar que etapa so fica consolidada apos commit e push
- nao alterei codigo funcional, regras financeiras, views, urls, models, forms, templates ou testes

## Auditoria de documentos por favorecido no financeiro

- auditei rotas, views e templates relacionados a historico por favorecido, recibos por favorecido/em lote, termo anual de quitacao e acoes documentais na `lancamento_list`
- confirmei que `PessoaFinanceiraHistoricoView`, `pessoa_historico.html` e a acao `Historico` em `pessoa_list.html` estao implementados
- confirmei que os recibos em lote existem no codigo, com fluxo visivel atual agrupando os lancamentos selecionados por favorecido
- confirmei que o termo anual de quitacao existe como acao da listagem de lancamentos baseada nos filtros atuais, e que a rota plural antiga redireciona para o fluxo unificado
- atualizei o `MAPA_RECLASSIFICACAO.md` para retirar o status generico de duvida dos itens confirmados e classificar o relatorio anual antigo como historico/substituido pelo fluxo atual
- nao alterei codigo funcional, templates, views, urls, models, forms, calculos ou testes

## Logo institucional no Extrato impresso

- corrigi pontualmente o cabecalho documental do Extrato para usar a logo institucional via `<img>` quando `financeiro_shell_brand_logo_url` estiver disponivel
- mantive fallback textual com `financeiro_shell_brand_name` quando nao houver logo configurada
- ajuste complementar: compactei o print do Extrato, reduzi a area inicial antes da tabela e garanti repeticao do cabecalho de colunas com `thead` em `table-header-group`
- ajuste complementar: reequilibrei o print com margem superior explicita, cabecalho documental mais legivel, contas selecionadas em bloco proprio e titulos de coluna com mais destaque
- ajuste complementar: reconstrui o cabecalho impresso para manter logo e nome institucional juntos, organizar titulo/periodo/emissao em bloco proprio e resumir as contas selecionadas no print
- ajuste complementar: ampliei a margem superior do print, centralizei verticalmente os blocos do cabecalho e adicionei um espacador print-only no `thead` para dar respiro nas paginas seguintes
- ajuste complementar: removi a frase explicativa do bloco de movimentacoes e suavizei linhas/bordas do print para aproximar o Extrato da tela validada
- ajuste complementar: defini um contrato local de impressao do Extrato com margens, padding superior real e respiro de continuacao no `thead`, sem propagar para outros relatorios
- ajuste complementar: estabilizei a tabela do Extrato com layout fixo, separadores verticais leves, truncamento de textos longos e exibicao monetaria sem `R$` apenas nas linhas da tabela
- ajuste complementar: normalizei o contrato local de pagina para margens A4 14mm/12mm/14mm, reduzi o spacer do `thead` e adicionei respiro final inferior
- ajuste complementar: substitui o respiro inferior baseado em `tbody::after` por `tfoot` real com `table-footer-group` e spacer proprio
- nao alterei view, contexto, filtros, calculos, outros relatorios, models ou migrations

## Auditoria da logo no Extrato impresso

- auditei o template real do Extrato (`conta_extrato.html`), o CSS de impressao, o contexto global de identidade institucional e comparei com Prestacao, Resumo e Balancete
- diagnostico: o Extrato nao renderiza a logo como `<img>`; ele usa apenas `financeiro_shell_brand_name` no cabecalho impresso, embora `financeiro_shell_brand_logo_url` esteja disponivel pelo context processor
- nao alterei codigo, templates, CSS, models, migrations, calculos ou relatorios nesta microetapa

## Registro documental de tipo/disponibilidade de conta

- registrei no roadmap a frente futura de tipo de conta, disponibilidade/vinculacao, mensagem explicativa por conta e modos de composicao do Balancete
- acrescentei diretrizes permanentes diferenciando conta ativa/inativa de conta disponivel/indisponivel e registrando integralizacao de capital como valor patrimonial/vinculado, nao despesa operacional
- atualizei o mapa de reclassificacao com itens de acompanhamento para tipo de conta, disponibilidade, mensagem de indisponibilidade, composicao do Balancete e logo no Extrato impresso
- nao alterei codigo, templates, models, migrations, calculos, Balancete ou Extrato nesta microetapa documental

## Auditoria da regra de conta inativa

- auditei modelo, forms, views, templates e fluxos de importacao/filtros relacionados a `ContaFinanceira.ativa`
- diagnostico: novos lancamentos ainda podem selecionar contas inativas via form/autocomplete; edicao de lancamento antigo permanece viavel; importacao de lancamentos ja restringe contas a `ativa=True`
- diagnostico: relatorios historicos preservam movimentos de contas inativas porque usam todas as contas, mas os filtros ainda nao limitam inativas ao criterio "com movimento no periodo"
- nao implementei correcao funcional, nao alterei Python, templates ou calculos nesta microetapa

## Conta inativa em novos lancamentos

- restringi `conta` e `conta_destino` dos forms de lancamento para contas ativas em criacao, preservando apenas as contas ja vinculadas quando a edicao for de registro antigo
- ajustei o autocomplete de contas para retornar somente contas ativas
- ajustei clones para nao reaproveitar automaticamente conta origem/destino inativa do lancamento original
- adicionei testes pontuais para novo lancamento, transferencia, rateio, edicao historica, clone e autocomplete
- nao alterei relatorios, filtros historicos, importacao, models, migrations ou calculos

## MVP do Balancete Institucional

- criei a rota `/financeiro/balancete-institucional/`, a view `BalanceteInstitucionalFinanceiroView` e o template proprio `balancete_institucional.html`
- reaproveitei `montar_contexto_fechamento_periodo` para montar saldos, receitas, despesas, transferencias por escopo, reconciliacao e composicao final, sem duplicar calculo
- adicionei link no menu de Relatorios e filtros essenciais com selecao de contas, periodo, opcoes e duas assinaturas via `AssinaturaInstitucional`
- adicionei testes pontuais para resolucao da URL e contexto/reconciliacao do Balancete
- ajuste complementar: refinei exclusivamente o CSS de print/PDF do Balancete para aumentar margens laterais, centralizar o documento e melhorar o respiro das tabelas/assinaturas sem alterar calculo, view, rota ou filtros
- ajuste complementar: aumentei fonte/espacamento do print, reforcei a margem superior visual e cobri fallback de assinaturas para ausencia de selecao manual e para cenario com apenas uma assinatura ativa
- refinamento documental: reorganizei o cabecalho institucional, removi lista longa de contas do topo impresso, passei a usar abrangencia resumida, ampliei a largura util do documento e ocultei contas zeradas por padrao nos blocos de saldo do Balancete
- ajuste complementar: corrigi o print para usar margens reais mais seguras e removi o preenchimento automatico de assinaturas reais quando o usuario nao seleciona assinatura manualmente
- ajuste complementar: apliquei margem visual diretamente no wrapper `.balancete-documento`, removi a linha de abrangencia/contas do cabecalho impresso e mantive assinatura real apenas quando recebida por GET
- ajuste complementar: removi a exibicao de linhas/rotulos genericos quando nao ha assinatura selecionada e ampliei as margens laterais do wrapper impresso do Balancete
- ajuste complementar: ampliei de novo as laterais do wrapper impresso e removi a linha `Contas consideradas` tambem da tela normal do Balancete, sem mexer na regra de assinaturas
- ajuste complementar: aumentei o padding lateral do wrapper impresso do Balancete para aproximadamente tres vezes o valor anterior, sem alterar cabecalho, assinaturas, view ou calculos
- ajuste complementar: reduzi as laterais do wrapper impresso para 24mm e aumentei levemente a fonte do corpo do Balancete, sem alterar cabecalho, assinaturas, view ou calculos
- ajuste complementar: aumentei mais um pouco a fonte do corpo impresso do Balancete, mantendo as margens laterais em 24mm e sem alterar cabecalho, assinaturas, view ou calculos
- nao alterei a Prestacao/Fechamento atual, Extrato, Resumo, Evolucao, models, migrations, importacao/exportacao ou regras de transferencia

## Base comum de calculo para Fechamento e futuro Balancete

- criei o ponto comum `montar_contexto_fechamento_periodo` para concentrar o acesso a base de calculo/contexto do Fechamento
- preservei `_build_periodo_context` como compatibilidade para as telas atuais
- adicionei teste pontual chamando a base comum e validando a reconciliacao do saldo por escopo de contas
- nao criei Balancete, rota, URL, template, CSS, model, migration, permissao ou assinatura nova
- nao alterei calculos, filtros, regras de transferencia, Extrato, Resumo ou Evolucao

## Revisao documental do Balancete Institucional como relatorio proprio

- ajustei a direcao registrada para manter a Prestacao/Fechamento como relatorio analitico/gerencial
- registrei o Balancete Institucional como relatorio proprio futuro, com finalidade formal/documental
- alinhei `ROADMAP_FINANCEIRO.md`, `CEREBRO_PROJETO.md` e `MAPA_RECLASSIFICACAO.md` para indicar reaproveitamento da regra/base de calculo da Prestacao/Fechamento
- acrescentei em `REGRAS_NEGOCIO.md` que o Balancete futuro nao deve ter calculo divergente
- nao alterei codigo, templates, CSS, testes, rotas, views, models, migrations ou calculos

## Registro documental do modelo balancete para Prestacao/Fechamento

- registrei no `ROADMAP_FINANCEIRO.md` a frente futura para evoluir a Prestacao/Fechamento para modelo tipo balancete institucional
- registrei no `CEREBRO_PROJETO.md` a diretriz duradoura de relatorios impressos com fundo branco, economia de tinta e aparencia documental
- atualizei o `MAPA_RECLASSIFICACAO.md` com acompanhamento de modelo balancete, duas assinaturas e fundo branco permanente nos impressos
- registrei nota curta no `STATE.md`
- nao alterei codigo, templates, CSS, testes, models, migrations ou calculos

## Refinamento da impressao da Prestacao/Fechamento

- compactei exclusivamente o modo print/PDF da Prestacao/Fechamento do periodo
- reduzi margens, padding, fonte, line-height e espacamentos de cabecalho, cards, tabelas e assinatura
- ocultei microtextos auxiliares no impresso para preservar leitura documental com menor altura
- agrupei composicao final e assinatura para reduzir quebra ruim e assinatura isolada quando houver espaco
- nao alterei calculos, views, queries, regras de transferencia, filtros ou outros relatorios

## Padronizacao do filtro de contas nas telas analiticas

- apliquei o padrao do filtro de contas do Extrato em Resumo, Fechamento/Prestacao e Evolucao por categorias
- mantive os parametros e o significado atual dos filtros, sem alterar calculos ou regras financeiras
- centralizei o conforto visual do dropdown em classe comum no `financeiro/base.html`
- nao alterei impressao da Prestacao/Fechamento nem implementei filtro multi-contas na listagem de lancamentos

## Registro documental de pendencias de filtro de contas e impressao

- registrei no `ROADMAP_FINANCEIRO.md` as pendencias de padronizacao do filtro de contas e refinamento da impressao da Prestacao/Fechamento
- atualizei o `MAPA_RECLASSIFICACAO.md` para acompanhar esses dois pontos como itens futuros
- registrei nota curta no `STATE.md`
- nao alterei codigo, templates, CSS, testes, filtros, relatorios ou calculos

## Correcao da edicao de conta financeira

- ajustei o form de conta financeira para preencher `data_saldo_inicial` em formato compativel com `input type="date"` na edicao
- mantive o carregamento do `saldo_inicial` salvo e a possibilidade de alterar saldo/data no proprio formulario
- adicionei teste pontual para abertura do form de edicao com saldo/data preenchidos e salvamento de novos valores
- nao alterei calculos financeiros, Extrato, Fechamento/Prestacao, lancamentos ou importacao

## Correcao de duplicidade de favorecido por nome

- implementei validacao de duplicidade por nome normalizado em `PessoaFinanceira.clean()`
- a validacao bloqueia cadastro novo duplicado e edicao para o nome de outro favorecido, mas permite salvar o proprio registro
- a normalizacao considera maiusculas/minusculas, espacos extras e acentos
- alinhei a importacao auxiliar de favorecidos para usar a mesma normalizacao de nome
- ajuste complementar: registrei a regra-mae de identificadores-chave para todos os cadastros, sem expandir implementacao para contas, categorias ou centros de custo nesta etapa
- na importacao auxiliar, mensagens de nome normalizado ja existente/repetido foram ajustadas para `conflito cadastral`, distinguindo de duplicidade de codigo/linha
- adicionei teste pontual para cadastro duplicado, edicao do proprio registro e edicao para nome de outro favorecido
- nao houve limpeza/mescla de registros duplicados existentes nem criacao de migration

## Classificacao documental de novas pendencias do financeiro

- registrei sete novas melhorias levantadas pela usuaria apos Fechamento/Prestacao e Extrato multi-contas
- classifiquei os itens entre BUG/correcao operacional, REGRA DE NEGOCIO, MELHORIA DE UX, MELHORIA FUNCIONAL e FRENTE FUTURA GRANDE
- atualizei `docs/ROADMAP_FINANCEIRO.md` com novo bloco de pendencias pos-Extrato multi-contas
- atualizei `docs/MAPA_RECLASSIFICACAO.md` para acompanhar os novos itens sem remover entradas antigas
- acrescentei em `docs/REGRAS_NEGOCIO.md` apenas regras permanentes ja claras
- registrei em `docs/CEREBRO_PROJETO.md` a frente futura grande de tabelas personalizadas de controle
- nao houve implementacao funcional, alteracao de codigo, templates, models, migrations ou testes nesta microetapa documental

## Extrato com seleção de múltiplas contas

- adaptei `/financeiro/extratos/` para aceitar seleção de uma conta, várias contas ou todas as contas
- preservei o fluxo antigo de conta única e a compatibilidade com o parâmetro `conta`
- implementei cálculo consolidado de saldo anterior, entradas, saídas, saldo acumulado e saldo final por escopo de contas
- transferências internas ao escopo selecionado deixam de alterar artificialmente o saldo consolidado; transferências com apenas origem/destino no escopo aparecem como saída/entrada
- ajustei o template do Extrato para exibir o escopo selecionado e, em multi-contas, identificar a conta relacionada ao movimento
- adicionei teste pontual cobrindo uma conta, duas contas, todas as contas, transferência externa de entrada/saída e transferência interna ao escopo
- arquivos alterados:
  - `financeiro/views.py`
  - `financeiro/templates/financeiro/conta_extrato.html`
  - `financeiro/tests.py`
  - `docs/REGRAS_NEGOCIO.md`
  - `docs/STATE.md`
  - `docs/CODEX_RESULTADO.md`
- validações executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `py manage.py test financeiro.tests.PrestacaoContasTransferenciasEscopoTests financeiro.tests.ExtratoFinanceiroMultiplasContasTests` OK
- ajuste complementar do filtro: corrigi a preservação da seleção parcial, tratei envio sem contas com mensagem clara, ampliei o seletor e adicionei busca local por nome da conta
- ajuste visual complementar: liberei o dropdown de contas do Extrato do recorte do card de filtros e defini altura máxima com rolagem interna
- ajuste complementar da busca: corrigi a filtragem local por texto no dropdown de contas e deixei as opções empilhadas em uma conta por linha

## Correção do Fechamento do período por escopo de transferências

- comparei a lógica do Extrato com a lógica do Fechamento do período / Prestação de contas
- causa encontrada: o Extrato usava data operacional (`data_pagamento` com fallback para `data_competencia`), enquanto o Fechamento calculava saldos e movimentos por `data_competencia`; além disso, o detalhamento visual podia listar transferências internas ao escopo quando `Exibir transferências` estava ligado
- corrigi o Fechamento para calcular saldo inicial, receitas/despesas, transferências e saldo final pela mesma data operacional do Extrato
- mantive transferências fora de receitas/despesas operacionais
- mantive transferências sempre dentro da composição real do saldo conforme escopo das contas, independentemente da opção `Exibir transferências`
- ajustei o detalhamento analítico para exibir apenas transferências com uma ponta dentro do filtro; transferências internas ao escopo ficam ocultas porque se anulam no consolidado
- alinhei a data exibida no detalhamento de transferências à data operacional usada no cálculo
- registrei a regra permanente em `docs/REGRAS_NEGOCIO.md`
- adicionei teste pontual para transferência interna, origem no filtro, destino no filtro e `Exibir transferências` ligada/desligada sem mudar saldo real
- arquivos alterados:
  - `financeiro/views.py`
  - `financeiro/templates/financeiro/prestacao_contas.html`
  - `financeiro/tests.py`
  - `docs/REGRAS_NEGOCIO.md`
  - `docs/STATE.md`
  - `docs/CODEX_RESULTADO.md`
- validações executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `py manage.py test financeiro.tests.PrestacaoContasTransferenciasEscopoTests` OK
  - conferência local da conta `Dinheiro` em `01/03/2026 a 31/03/2026` OK: Fechamento e Extrato retornaram saldo inicial `270.06`, entradas `756.26`, saídas `314.26` e saldo final `712.06`
- ajuste visual complementar: o relatório deixou de exibir linhas/cards zerados de entradas ou saídas por transferência externa ao escopo; cálculo e Extrato não foram alterados

Data: 2026-04-24

## Refinamento final da `Prestacao de contas` para `Fechamento do periodo`

- tratei a rodada como acabamento funcional/visual da mesma tela, preservando calculos, reconciliacao e semantica financeira
- a experiencia principal passou a usar o nome `Fechamento do periodo`, com linguagem de apoio mais gerencial e menos obrigatoria
- apliquei na tela e no impresso o mesmo padrao monetario ja consolidado no `Extrato`:
  - `R$` a esquerda
  - numero a direita
  - mesma celula
- introduzi a opcao `Mostrar contas sem movimentacao e sem saldo`:
  - por padrao ela fica desligada
  - com ela desligada, saem das composicoes as contas zeradas e sem movimentacao real no periodo
  - com ela ligada, essas contas reaparecem no relatorio sem alterar totais
- refinei a compactacao do impresso para melhorar a chance de caber em uma pagina quando o volume permitir:
  - fonte um pouco menor no PDF
  - padding e espacamentos verticais mais contidos
  - cabecalho impresso mais enxuto
  - ocultacao de secoes opcionais vazias, quando aplicavel
- arquivos alterados:
  - `financeiro/views.py`
  - `financeiro/templates/financeiro/prestacao_contas.html`
  - `docs/STATE.md`
  - `docs/CODEX_RESULTADO.md`
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- conclusao:
  - a tela `Fechamento do periodo` fica pronta para homologacao final

## Correcao da ordem formal e da paginacao impressa na `Prestacao de contas`

- tratei a rodada como correcao pontual de impressao/PDF, sem reabrir calculos, reconciliacao nem a estrutura geral da tela
- corrigi a numeracao das secoes para seguir a ordem real de leitura do documento, usando contagem automatica nas secoes formais numeradas
- ordem final consolidada no relatorio:
  - `Saldo disponivel no inicio do periodo`
  - `Resumo do saldo disponivel`
  - `Receitas do periodo`
  - `Despesas do periodo`
  - `Transferencias do periodo`, quando exibidas
  - `Composicao do saldo final`
  - `Despesas por centro de custo`, quando exibidas
- para a secao `Despesas do periodo`, endureci o comportamento de print:
  - a grade de paineis passa a empilhar no PDF para melhorar continuidade
  - a secao fica protegida contra quebra ruim no fim da pagina sempre que houver espaco insuficiente
  - `thead` e `tfoot` da tabela passam a manter papel formal de cabecalho/fechamento no impresso
  - o total da secao deixa de correr o risco de aparecer antes da continuacao da listagem
- arquivos alterados:
  - `financeiro/templates/financeiro/prestacao_contas.html`
  - `docs/STATE.md`
  - `docs/CODEX_RESULTADO.md`
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- conclusao:
  - `Prestacao de contas` segue preservando carater formal/documental e fica pronta para homologacao final de impressao

## Aplicacao do padrao analitico consolidado na tela `Prestacao de contas`

- tratei a rodada como terceira propagacao controlada do padrao analitico consolidado, sem reabrir regras de negocio da prestacao nem tocar na reconciliacao contabil ja aprovada
- heranca aplicada do padrao-base:
  - ordem `titulo/contexto -> filtro -> KPIs -> resultado principal`
  - filtro mantido no topo da area analitica
  - filtro recolhido por padrao quando o relatorio ja esta carregado
  - resumo recolhido util para orientar rapidamente periodo, contas e opcoes ativas
  - resultado como protagonista visual da pagina
- adaptacoes especificas da `Prestacao de contas`:
  - preservei o carater documental/gerencial da tela, sem transformá-la em dashboard genérico
  - mantive os blocos formais de conferencia e a reconciliacao do saldo como leitura principal
  - reorganizei o resultado em paineis mais claros para:
    - leitura operacional do relatorio
    - saldo inicial
    - resumo do saldo disponivel
    - receitas e despesas do periodo
    - transferencias do periodo, quando exibidas
    - composicao do saldo final
    - despesas por centro de custo, quando exibidas
  - preservei o bloco final de assinatura e a impressao isolada do shell administrativo
- apoio minimo no backend:
  - nenhum ajuste de regra de negocio foi necessario na view
  - a adaptacao ficou concentrada no template e na hierarquia visual
- consolidacao documental desta etapa:
  - a frente ativa continua sendo a padronizacao das telas analiticas do `financeiro`
  - a discussao de normalizacao de favorecidos nao entrou nesta sequencia operacional
  - a frente de frequencia/recorrencia continua registrada apenas como futura
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- resultado:
  - microetapa pronta para commit
  - tela `Prestacao de contas` pronta para homologacao visual

## Padronizacao das celulas monetarias do `Extrato`

- tratei a rodada como ajuste visual pontual do miolo monetario do `Extrato`, sem tocar em calculos ou estrutura logica da tabela
- causa objetiva:
  - `Valor` e `Saldo` ainda deixavam o `R$` visualmente separado do numero
  - isso enfraquecia a leitura financeira, especialmente no PDF
- solucao aplicada:
  - padronizei as celulas monetarias para usar a mesma composicao interna
  - `R$` ficou alinhado a esquerda da propria celula
  - o numero ficou alinhado a direita da mesma celula
  - o sinal negativo continuou junto do numero
- pontos cobertos:
  - coluna `Valor`
  - coluna `Saldo`
  - linha de `Saldo anterior`/`Saldo inicial`
  - linha de `Saldo final`
- exemplo final:
  - `R$        150,00`
  - `R$       -350,00`
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- resultado:
  - microetapa pronta para commit
  - extrato pronto para homologacao final

## Refinamento do `Extrato` com remocao do tipo textual no corpo da tabela

- tratei a rodada como limpeza pontual do miolo do `Extrato`, sem tocar em calculos, saldo, cronologia ou regra de negocio
- causa objetiva:
  - `Favorecido` ainda carregava uma segunda linha com `Receita`, `Despesa` ou `Transferencia`
  - isso aumentava a altura das linhas e tirava largura util de `Descricao` e `Favorecido`
  - a coluna `Valor` ainda desperdicava espaco ao separar a leitura financeira em microblocos
- solucao aplicada:
  - removi o texto auxiliar de tipo do movimento do corpo da tabela
  - mantive `Descricao` e `Favorecido` separados
  - redistribui as larguras favorecendo `Descricao` e `Favorecido`
  - deixei `Valor` mais direto, em uma unica leitura visual, com sinal positivo/negativo e sem `C/D`
- estrutura mantida:
  - `Data`
  - `Doc.`
  - `Descricao`
  - `Favorecido`
  - `Valor`
  - `Saldo`
- regra final da apresentacao do valor:
  - entrada/receita: `R$ 150,00`
  - saida/despesa: `R$ -350,00`
  - `Saldo` continua em coluna propria, alinhado a direita e protegido
- efeito esperado:
  - altura das linhas menor
  - menos truncamento em `Descricao` e `Favorecido`
  - leitura mais limpa do extrato em tela e impressao
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- resultado:
  - microetapa pronta para commit
  - extrato pronto para nova homologacao visual

## Alinhamento do layout do `Extrato` entre tela e impressao

- tratei a rodada como correcao da tentativa anterior de modelo bancario, que o usuario reprovou por fundir `Descricao` com `Favorecido` e por usar `C/D` na coluna de valor
- decisao consolidada nesta etapa:
  - tela e impressao passam a seguir a mesma logica estrutural de colunas
  - `Descricao` e `Favorecido` permanecem em colunas distintas
  - `Valor` passa a ser unico, sem `C/D`, com sinal negativo quando aplicavel
- estrutura final aplicada:
  - `Data`
  - `Doc.`
  - `Descricao`
  - `Favorecido`
  - `Valor`
  - `Saldo`
- solucao aplicada:
  - removi a tabela impressa de 5 colunas criada na rodada anterior
  - mantive uma unica estrutura de tabela entre tela e print, com ajustes apenas de largura, tipografia e compactacao no modo de impressao
  - `Descricao` ganhou linha principal e pode exibir observacao opcional como meta discreta
  - `Favorecido` ganhou linha principal e mantem o tipo da movimentacao como meta discreta, sem virar fusao com `Descricao`
- regra final da coluna `Valor`:
  - a view passou a expor `valor_exibicao` assinado
  - quando a linha representa saida/despesa, o valor e exibido com sinal `-`
  - quando a linha representa entrada/receita, o valor permanece positivo
  - o saldo continua em coluna propria e alinhada a direita
- preservacao:
  - nenhum calculo mudou
  - nenhuma ordenacao cronologica mudou
  - a versao de tela nao voltou para a fragmentacao anterior com `Entrada` e `Saida`
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - PDF de conferência gerado em `tmp/extrato_homologacao_alinhado.pdf`
- resultado:
  - microetapa pronta para commit
  - extrato pronto para nova homologacao visual desta estrutura alinhada

## Redesenho do impresso do `Extrato` para modelo bancario compacto de 5 colunas

- tratei a rodada como redesenho pontual apenas do print/PDF do `Extrato`, sem tocar na tela normal e sem alterar qualquer calculo
- causa objetiva:
  - o modelo anterior ainda carregava informacao demais em colunas demais
  - isso deixava o miolo fragmentado e distante da leitura esperada de um extrato bancario
- solucao aplicada:
  - mantive a tabela atual apenas para a versao em tela
  - criei uma tabela dedicada de impressao com 5 colunas:
    - `Data`
    - `Doc.`
    - `Historico`
    - `Valor`
    - `Saldo`
- regra final do `Historico`:
  - linha principal com a descricao da movimentacao
  - linha secundaria compacta com `favorecido` quando existir e `tipo da movimentacao`
  - `Historico` passa a ser a coluna elastica principal do impresso
- regra final da coluna `Valor`:
  - `entrada` vira `valor C`
  - `saida` vira `valor D`
  - a semantica de credito/debito fica consolidada na propria coluna
- preservacao:
  - a versao de tela normal do extrato permaneceu intacta
  - saldo anterior/inicial e saldo final permaneceram destacados
  - a coluna `Saldo` continua propria, alinhada a direita e protegida
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - PDF de conferência gerado em `tmp/extrato_homologacao_bancario.pdf`
- resultado:
  - microetapa pronta para commit
  - impresso do `Extrato` pronto para nova homologacao visual

## Correcao da sobreposicao de colunas no impresso do `Extrato`

- tratei a rodada como correcao pontual de print/PDF do `Extrato`, sem tocar na leitura cronologica da tela normal nem em qualquer calculo financeiro
- causa objetiva:
  - no impresso, o miolo da tabela ficava apertado demais
  - `Favorecido`, `Mov`, `Entrada`, `Saida` e `Saldo` disputavam largura e acabavam invadindo visualmente colunas vizinhas
- solucao aplicada:
  - ativei `table-layout: fixed` no modo print
  - protegi larguras de `Entrada`, `Saida` e `Saldo`
  - reduzi `Doc.` e deixei `Mov.` mais enxuta no papel
  - passei `Descricao`, `Favorecido` e `Observacoes` para truncamento controlado com `ellipsis`
  - reduzi `font-size` e `padding` apenas no impresso
  - reforcei alinhamento numerico a direita e o `money-cell` no print
- preservacao:
  - nenhuma regra de negocio mudou
  - nenhum calculo de saldo mudou
  - nenhuma ordenacao mudou
  - a versao de tela normal do `Extrato` permaneceu intacta
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - geracao de PDF de conferência em `tmp/extrato_homologacao_impresso_corrigido.pdf`
- resultado:
  - microetapa pronta para commit
  - impresso do `Extrato` pronto para nova homologacao visual

## Refinamento do impresso do `Extrato` com compactacao tipografica leve

- tratei a rodada como ajuste fino do print/PDF do `Extrato`, sem alterar a solucao anterior de nao sobrepor colunas e sem tocar na tela normal
- causa objetiva:
  - a correcao anterior segurou a sobreposicao
  - mas ainda deixou truncamento excessivo em `Descricao` e `Favorecido`, empobrecendo a utilidade do relatorio
- solucao aplicada:
  - reduzi discretamente a tipografia da tabela no modo print
  - reduzi `line-height` e `padding` do miolo apenas no impresso
  - redistribui larguras para devolver espaco a `Descricao` e `Favorecido`
  - rebaixei `Doc.` no papel, deixando a coluna mais estreita
  - deixei `Mov.` mais compacta no impresso
  - mantive `Entrada`, `Saida` e `Saldo` protegidas, com alinhamento numerico a direita
  - preservei `ellipsis` apenas como fallback inevitavel nas colunas textuais
- regra final desta rodada:
  - nao usar quebra de linha em massa nas celulas
  - melhorar o aproveitamento horizontal antes de aceitar truncamento
  - manter o valor financeiro mais protegido do que o texto auxiliar
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - PDF de conferência regenerado em `tmp/extrato_homologacao_impresso_corrigido2.pdf`
- resultado:
  - microetapa pronta para commit
  - impresso do `Extrato` pronto para nova homologacao visual

## Aplicacao do padrao analitico consolidado na tela `Extrato`

- tratei a rodada como segunda propagacao controlada do padrao analitico consolidado a partir de `Evolucao por categorias`, sem reabrir regra de negocio nem mexer na base de calculo do extrato
- heranca aplicada do padrao-base:
  - ordem `titulo/contexto -> filtro -> KPIs -> resultado principal`
  - filtro mantido no topo da area analitica
  - filtro recolhido por padrao quando a conta ja esta carregada
  - resumo recolhido util para orientar rapidamente conta, periodo e exibicao de observacoes
  - resultado como protagonista visual da pagina
- adaptacoes especificas do `Extrato`:
  - mantive a leitura cronologica como centro da tela, sem transformar o extrato em relatorio excessivamente gerencial
  - o bloco executivo foi reorganizado para concentrar saldo anterior/inicial, entradas, saidas, quantidade de movimentacoes e saldo final
  - a area de resultados foi reestruturada para manter a tabela de movimentacoes como leitura principal, com saldo acumulado e fechamento final preservados
  - a impressao documental foi preservada, ocultando topo, filtros e KPIs fora do papel para nao poluir o extrato impresso
- apoio minimo no backend:
  - adicionei apenas labels e totais simples necessarios ao layout (`periodo_label`, `conta_label`, `total_entradas_periodo`, `total_saidas_periodo`, `quantidade_movimentos`)
  - nao alterei classificacao de lancamentos, ordenacao cronologica nem regra de consolidacao de rateio
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK cobrindo:
    - estado sem conta carregada com filtro no topo
    - estado com conta carregada exibindo `Leitura executiva do extrato`
    - bloco principal `Movimentacoes da conta`
    - acao `Atualizar extrato`
- resultado:
  - microetapa pronta para commit
  - tela `Extrato` pronta para homologacao visual

## Aplicacao do padrao analitico consolidado na tela `Resumo`

- tratei a rodada como primeira propagacao real do padrao analitico consolidado a partir de `Evolucao por categorias`, sem reabrir regra de negocio nem mexer em calculos financeiros
- heranca aplicada do padrao-base:
  - ordem `titulo/contexto -> filtro -> KPIs -> resultados`
  - filtro mantido no topo da area analitica
  - filtro recolhido por padrao quando ja existe resultado valido
  - resumo recolhido util para orientar rapidamente periodo, contas e opcoes ativas
  - resultado como protagonista visual da pagina
- adaptacoes especificas do `Resumo`:
  - mantive a leitura executiva propria da tela, sem importar a logica de comparacao entre periodos da `Evolucao por categorias`
  - o bloco de KPIs foi reorganizado para concentrar saldo inicial, receitas, despesas, saldo do periodo e saldo final consolidado
  - a area de resultados foi reestruturada em blocos claros:
    - `Receitas por categoria`
    - `Despesas por categoria`
    - `Transferencias do periodo`, quando ativadas
    - `Despesas por centro de custo`, quando ativadas
  - a impressao documental foi preservada, mantendo cabecalho e metadados do relatorio sem reintroduzir o filtro no papel
- decisao de UX:
  - o filtro deixou de disputar protagonismo com a leitura do resumo
  - o topo passou a concentrar apenas contexto principal e acoes
  - as opcoes de leitura foram incorporadas ao mesmo painel de filtro para reduzir ruido visual
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- resultado:
  - microetapa pronta para commit
  - tela `Resumo` pronta para homologacao visual
  - o padrao analitico fica forte o suficiente para seguir depois para a proxima tela da sequencia, caso a homologacao visual confirme esta primeira propagacao

## Filtro fixo no topo da analise em `Evolucao por categorias`

- tratei a rodada como refinamento de UX estrutural/local, sem tocar em calculos, comparacao ou semantica financeira
- causa objetiva:
  - o filtro recolhido estava descendo para baixo da tela depois da analise
  - isso quebrava a orientacao mental da pagina e enfraquecia a leitura de `tela analitica`
- solucao aplicada:
  - mantive o filtro no topo da area de analise
  - removi a inversao de ordem visual que empurrava o card de filtros para baixo
  - preservei o resumo recolhido e o painel expandido no mesmo lugar estrutural
  - deixei o resumo compacto mais util, incluindo periodo/comparacao, escopo, leitura, granularidade e selecao resumida quando houver
- consolidacao:
  - a tela agora segue melhor a ordem:
    - titulo e contexto
    - filtro resumido ou expandido
    - KPIs
    - resultados
  - os resultados continuam protagonistas, mas o filtro nao perde mais o lugar logico de interacao
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- resultado:
  - microetapa pronta para commit
  - tela pronta para homologacao visual focada em UX
  - a solucao ficou madura para servir como base local do futuro padrao analitico reutilizavel

## Rebaixamento do filtro e limpeza do topo em `Evolucao por categorias`

- tratei a rodada como refinamento de UX visual/estrutural, sem tocar em calculos, comparacao, KPIs ou semantica financeira
- no painel de filtros:
  - se ja existe resultado carregado, o painel agora vem recolhido por padrao
  - o summary passou a exibir um resumo compacto do estado atual da analise
  - a acao de abrir/fechar ficou mais clara, usando o proprio summary como ponto de retorno rapido
- na hierarquia da pagina:
  - separei o card de resultados do card de filtros
  - o resultado passa a aparecer acima do filtro na hierarquia visual da pagina
  - isso ajuda a tela a parecer mais consulta analitica e menos formulario dominante
- no topo:
  - mantive como chips principais apenas os contextos mais estruturais
  - `analise`, `selecao atual` e `contas` migraram para texto secundario
  - o topo ficou menos carregado e com menor repeticao de peso visual
- preservacao:
  - nenhuma regra de negocio mudou
  - o fluxo sem comparativo foi preservado
  - o comparativo consolidado e o comparativo separado nao tiveram alteracao de calculo
  - impressao permaneceu sem regressao estrutural
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- resultado:
  - microetapa pronta para commit
  - tela pronta para nova homologacao visual focada em UX

## Reforco da hierarquia visual da tela `Evolucao por categorias`

- tratei a rodada como refinamento de UX visual, sem tocar em calculos, comparacao entre periodos ou semantica financeira
- topo da pagina:
  - transformei o cabecalho em um bloco visual mais estruturado e respirado
  - melhorei a distancia entre titulo, subtitulo, chips de contexto e acoes
  - deixei a acao principal de impressao mais evidente, mantendo o retorno aos relatorios em segundo plano
- filtros:
  - o card de filtros passou a ter peso visual secundario
  - `Atualizar grafico` ganhou mais destaque como acao principal
  - `Limpar` ficou visualmente mais discreto
- KPIs:
  - aumentei o protagonismo dos numeros
  - reforcei contraste, espacamento e separacao entre os cards
  - deixei a faixa mais executiva e menos misturada com o restante da pagina
- resultados:
  - destaquei o painel principal do grafico/leitura detalhada
  - empurrei a tabela comparativa para um segundo nivel visual
  - melhorei respiro, borda e legibilidade do bloco `Itens com maior diferenca absoluta` e da tabela
- preservacao:
  - nenhum calculo foi alterado
  - nenhuma regra de comparacao foi alterada
  - impressao permaneceu preservada
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- resultado:
  - microetapa pronta para commit
  - tela pronta para homologacao visual focada em UX

## Refino da tabela comparativa e normalizacao cronologica

- tratei a rodada como acabamento funcional/semantico do comparativo de `Evolucao por categorias`, sem mexer no fluxo normal da tela
- solucao aplicada na coluna `Item`:
  - a tabela comparativa passou a usar o mesmo rotulo curto ja consolidado no bloco visual
  - quando o nome do item e univoco, a linha mostra apenas o nome curto
  - quando houver ambiguidade real, o fallback expandido continua disponivel
- solucao aplicada na linha `Total`:
  - o total deixou de herdar leitura de receita/despesa por item
  - a linha passou a usar semantica de resultado liquido:
    - comparativo maior que principal = melhor
    - comparativo menor que principal = pior
    - sem diferenca = neutro
  - essa classe passou a ser usada em `Diferenca absoluta` e `Variacao percentual` do rodape
- solucao aplicada na cronologia:
  - a tela agora reorganiza automaticamente os periodos quando o usuario preenche `principal` e `comparativo` invertidos no tempo
  - o periodo mais antigo passa a ocupar `Periodo principal`
  - o periodo mais novo passa a ocupar `Periodo comparativo`
  - a interface mostra aviso discreto informando a reorganizacao para manter a leitura `anterior -> posterior`
- preservacao:
  - fluxo sem `Periodo comparativo` permaneceu intacto
  - comparativo separado permaneceu intacto no que ja estava aprovado visualmente
  - comparativo consolidado nao teve alteracao de calculo
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando:
    - reorganizacao cronologica dos campos
    - aviso discreto de reorganizacao
    - nome curto na coluna `Item`
    - linha `Total` positiva quando o resultado liquido melhora no comparativo
- resultado:
  - microetapa pronta para commit
  - do ponto de vista tecnico, o bloco fica pronto para encerramento definitivo apos esta etapa

## Reversao da barra divergente e cor semantica da tabela comparativa

- tratei a rodada como correcao pontual de apresentacao no comparativo separado da `Evolucao por categorias`, sem reabrir calculos nem mexer no consolidado
- causa objetiva:
  - a barra divergente validada tecnicamente na rodada anterior nao ficou boa no navegador real
  - o bloco ainda carregava prefixo `+` indevido no nome do item
  - a tabela comparativa seguia colorindo a variacao apenas pelo sinal bruto, sem considerar `receita` versus `despesa`
- solucao aplicada:
  - reverti o bloco `Itens com maior diferenca absoluta` para barra simples com magnitude absoluta
  - mantive o texto monetario assinado:
    - `receita` positiva
    - `despesa` negativa
  - removi o prefixo `+` dos rotulos curtos do bloco, mantendo nome neutro do item
  - criei na view uma regra semantica explicita para comparar `principal` x `comparativo` conforme a natureza do item
  - passei a aplicar essa semantica na tabela comparativa em:
    - `Diferenca absoluta`
    - `Variacao percentual`
- regra final consolidada da tabela:
  - `receita`: comparativo maior = melhor (`is-receita`), comparativo menor = pior (`is-despesa`)
  - `despesa`: comparativo maior em magnitude = pior (`is-despesa`), comparativo menor em magnitude = melhor (`is-receita`)
- preservacao:
  - comparativo consolidado nao foi alterado
  - fluxo normal sem `Periodo comparativo` nao foi alterado
  - ordenacao do bloco separado permaneceu a mesma
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando:
    - barra simples sem `bar-half`
    - rotulos sem prefixo `+`
    - despesa negativa no texto
    - receita com diferenca/variacao positivas na tabela
    - despesa com diferenca/variacao negativas na tabela
- resultado:
  - a microetapa ficou pronta para commit
  - a homologacao visual/manual em navegador real ainda precisa confirmar o acabamento final desta reversao

## Correcao da semantica visual das barras de despesa no comparativo separado

- tratei a rodada como correcao visual/semantica pontual do bloco `Itens com maior diferenca absoluta`, sem reabrir a comparacao nem tocar no consolidado
- causa objetiva:
  - o texto monetario da despesa ja estava negativo
  - mas a barra ainda usava trilha positiva simples, sempre crescendo para a direita, o que fazia despesa parecer receita no desenho
- solucao aplicada:
  - adaptei a estrutura HTML/CSS do bloco para barra divergente com eixo central
  - cada linha agora tem duas metades de trilha:
    - lado esquerdo para despesa
    - lado direito para receita
  - a view passou a enviar a natureza do item para o bloco (`is-despesa` / `is-receita`)
  - a largura continua proporcional a magnitude absoluta
  - a direcao visual passou a ser definida pela natureza financeira do item
- regra final consolidada:
  - `receita`: texto positivo, barra para a direita
  - `despesa`: texto negativo, barra para a esquerda
  - o eixo central deixa explicito o lado negativo/positivo
- preservacao:
  - rotulos curtos permaneceram intactos
  - ordenacao analitica permaneceu intacta
  - comparativo consolidado nao foi alterado
  - fluxo normal sem `Periodo comparativo` nao foi alterado
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando:
    - texto de despesa negativo
    - `financeiro-evolucao-bar-fill is-principal is-negative`
    - `financeiro-evolucao-bar-fill is-comparativo is-negative`
    - `financeiro-evolucao-bar-fill is-principal is-positive`
    - `financeiro-evolucao-bar-fill is-comparativo is-positive`
- resultado:
  - o defeito ficou corrigido tecnicamente
  - a homologacao visual/manual em navegador real ainda precisa confirmar a leitura final da barra

## Correcao final da renderizacao do sinal das despesas na comparacao separada

- reabri a correcao porque o retorno do usuario foi tratado como verdade operacional: despesas ainda apareciam positivas na interface, entao a rodada anterior nao podia ser considerada encerrada
- causa objetiva confirmada:
  - a view ainda entregava campos genericos demais para a comparacao separada
  - o template seguia montando texto monetario com `R$ ` por fora, reaproveitando campos que ainda carregavam ambiguidade entre exibicao e magnitude visual
- solucao aplicada:
  - criei separacao explicita entre o que e texto exibido e o que e base visual da barra
  - backend agora entrega:
    - `valor_a_exibicao` / `valor_b_exibicao`
    - `valor_a_exibido_formatado` / `valor_b_exibido_formatado`
    - `valor_a_absoluto` / `valor_b_absoluto`
  - o bloco `Itens com maior diferenca absoluta` passou a usar:
    - texto: campos assinados completos
    - barra: campos absolutos
  - a tabela comparativa passou a usar os campos assinados explicitos
  - os totais textuais da comparacao tambem passaram a usar a leitura assinada
- regra final consolidada:
  - receita aparece como valor positivo
  - despesa aparece como valor negativo
  - barra continua comparando magnitudes absolutas
  - ordenacao analitica do bloco permaneceu inalterada
- preservacao:
  - comparativo consolidado nao foi alterado
  - fluxo normal sem `Periodo comparativo` nao foi alterado
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando:
    - `-R$ 300,00` e `-R$ 100,00` para despesa
    - `R$ 200,00` e `R$ 50,00` para receita
    - tabela comparativa com leitura assinada
    - barras ainda baseadas em magnitude absoluta
    - fluxo normal sem comparativo preservado
- resultado:
  - defeito corrigido tecnicamente e pronto para nova validacao visual/manual curta no navegador
  - esta etapa nao fecha, por si so, homologacao visual real do defeito

## Correcao do sinal de despesas no comparativo separado

- tratei a rodada como correcao pontual de regressao no bloco `Itens com maior diferenca absoluta`, sem reabrir a comparacao nem mexer no fluxo normal
- causa objetiva:
  - a view usava os totais das series em valor absoluto para a leitura grafica do bloco separado
  - o mesmo valor absoluto estava sendo reaproveitado para a formatacao textual dos periodos, o que fazia despesas aparecerem como positivas
- solucao aplicada:
  - separei `magnitude visual` de `valor exibido`
  - a largura das barras e a ordenacao continuam usando os totais absolutos
  - os campos formatados exibidos ao usuario agora passam por regra de natureza:
    - `receita` permanece positiva
    - `despesa` passa a ser formatada como negativa
- preservacao:
  - rotulos curtos do bloco permaneceram intactos
  - fallback por ambiguidade permaneceu intacto
  - ordenacao analitica do bloco permaneceu intacta
  - comparativo consolidado nao foi alterado
  - fluxo normal sem `Periodo comparativo` nao foi alterado
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando:
    - `R$ -300,00` e `R$ -100,00` para item de despesa
    - `R$ 200,00` e `R$ 50,00` preservados para receita
    - `Tabela comparativa` presente so no fluxo comparativo
    - fluxo normal preservado sem tabela comparativa
- resultado:
  - o bloco fica pronto para encerramento definitivo apos esta correcao

## Rotulos curtos e ordenacao analitica no comparativo separado

- tratei a rodada como acabamento de UX do bloco `Itens com maior diferenca absoluta`, sem alterar calculos nem a estrutura da comparacao
- causa objetiva:
  - o bloco de barras herdava o label analitico completo da serie, como `Captacao / Doacao`, deixando a leitura mais pesada do que o necessario
  - a ordenacao analitica ja existia, mas precisava ficar consolidada e validada para o bloco visual
- solucao aplicada:
  - separei o label completo da tabela do label curto usado no grafico de barras
  - o bloco visual passou a usar labels como `+ Doacao` e `+ Rendimento de juros`
  - quando existe ambiguidade real por nomes repetidos, o item usa fallback expandido, como `+ Administracao / Outros`
- regra final de ordenacao:
  - ordenar por maior diferenca absoluta decrescente
  - desempatar por maior soma dos valores dos dois periodos
  - desempatar por ordem alfabetica do label visual
- preservacao:
  - comparativo consolidado nao foi alterado
  - calculos, KPIs e tabela comparativa permaneceram intactos
  - fluxo normal sem `Periodo comparativo` permaneceu sem tabela comparativa
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando:
    - labels curtos em escopo `Subcategorias`
    - labels curtos em escopo `Categorias`
    - fallback expandido para subcategorias homonimas
    - ordenacao visual coerente com maior diferenca absoluta
    - fluxo normal sem comparativo preservado
- resultado:
  - tela pronta para encerramento definitivo deste bloco, pendente apenas de homologacao visual final se desejado

## Normalizacao dos rotulos de periodo na comparacao de `Evolucao por categorias`

- tratei a rodada como correcao textual pontual, sem mexer na logica de calculo nem no fluxo normal sem comparativo
- causa objetiva:
  - alguns pontos da UI comparativa ainda exibiam `Principal` e `Comparativo` como rotulos soltos
  - os periodos conhecidos precisavam virar o proprio label visivel do usuario
- solucao aplicada:
  - criei um formatador unico para labels visiveis de periodos comparativos
  - apliquei o label normalizado na legenda do consolidado, nos resumos da comparacao, na legenda/linhas do grafico de barras separado, nos cabecalhos da tabela comparativa e no resumo humano dos filtros
- regra final adotada:
  - `01/01/2025 a 31/01/2025` vira `01/25`
  - `01/01/2025 a 31/03/2025` vira `01/25 a 03/25`
  - qualquer intervalo quebrado em pelo menos uma ponta preserva `DD/MM/AAAA a DD/MM/AAAA`
- preservacao:
  - modo normal sem comparativo continua mostrando o periodo completo como antes
  - consolidado e separado continuam usando os mesmos calculos e visualizacoes ja aprovados
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando:
    - exemplos do formatador
    - comparacao separada com `01/26 a 02/26` e `01/25` no lugar de `Principal`/`Comparativo`
    - consolidado com legenda normalizada
    - fluxo normal sem `Periodo comparativo` preservado
- resultado:
  - tela pronta para homologacao final de encerramento da comparacao

## Correcao da legenda e anti-colisao dos rotulos no comparativo consolidado

- tratei a rodada como correcao pontual do modo consolidado da comparacao em `Evolucao por categorias`
- preservacao aplicada:
  - sem `Periodo comparativo`, a tela continua no fluxo normal
  - com `Leitura = Separado`, o grafico de barras horizontais por item e a tabela comparativa permanecem intactos
- causa objetiva:
  - a legenda do grafico precisava ser garantida a partir dos labels reais dos periodos selecionados
  - os rotulos dos pontos ainda usavam a regra generica do SVG, que podia posicionar valores proximos na mesma area visual
- solucao aplicada:
  - mantive os periodos reais como labels das duas series do grafico consolidado
  - adicionei uma regra especifica para o comparativo consolidado: serie principal acima dos pontos e serie comparativa abaixo
  - quando os valores do mesmo indice ficam proximos, o offset vertical aumenta
  - se a proximidade ainda representar risco de colisao, um rotulo daquele ponto e suprimido e o tooltip preserva o valor exato
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando:
    - legenda do consolidado com `01/01/2026 a 28/02/2026` e `01/01/2025 a 28/02/2025`
    - ausencia de `Periodo principal` / `Periodo comparativo` dentro da legenda visual do consolidado
    - rotulo da serie principal acima e rotulo da serie comparativa abaixo, sem colisao menor que o limite seguro
- resultado:
  - tela pronta para homologacao final curtissima do comparativo consolidado

## Correcao dos rotulos no comparativo consolidado de `Evolucao por categorias`

- tratei a rodada como correcao pontual do modo consolidado, sem mexer no fluxo normal nem no modo separado recem-corrigido
- causa objetiva:
  - a view so liberava rotulos no comparativo consolidado quando havia no maximo 4 pontos
  - em comparacoes curtas/moderadas isso escondia valores que ainda cabem visualmente e empobrecia a leitura do grafico
- solucao aplicada:
  - mantive a dependencia da opcao `Mostrar valores no grafico`
  - ampliei o limite seguro para ate 12 pontos
  - mantive a supressao automatica acima desse limite, preservando o tooltip como fonte do valor exato
- preservacao:
  - sem periodo comparativo, o fluxo normal permaneceu inalterado
  - com comparativo + `Separado`, o grafico de barras horizontais por item e a tabela comparativa permaneceram intactos
  - com comparativo + `Consolidado`, a legenda com periodos reais foi preservada
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK confirmando:
    - ausencia de regressao no normal
    - rotulos renderizados no consolidado com poucos pontos
    - barras do separado preservadas
- resultado:
  - tela pronta para homologacao final curta

## Correcao do grafico separado na comparacao de `Evolucao por categorias`

- corrigi a visualizacao do modo separado sem reimplementar a comparacao e sem mexer no comportamento normal da tela
- causa objetiva:
  - o apoio visual do modo separado ainda era um grafico agregado com dois pontos (`Principal` e `Comparativo`)
  - isso repetia uma leitura consolidada e nao mostrava a comparacao por categoria/subcategoria
- solucao aplicada:
  - removi a linha agregada inutil do modo separado
  - passei a montar, no backend, um resumo por item a partir da propria tabela comparativa
  - renderizei esse resumo no template como barras horizontais agrupadas por item, com uma barra para cada periodo
- regra adotada para selecionar/ordenar itens:
  - exibir ate 8 itens no grafico
  - ordenar por maior diferenca absoluta entre os periodos
  - usar maior valor agregado apenas como desempate secundario
  - manter todos os itens na tabela comparativa, que continua sendo a leitura principal do modo separado
- preservacao:
  - sem periodo comparativo preenchido, o fluxo normal permanece intacto
  - com comparativo + `Consolidado`, o grafico de linhas com duas series permanece como estava
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK para:
    - consulta normal sem comparativo
    - comparacao consolidada ainda com grafico de linhas
    - comparacao separada com barras horizontais por item e tabela comparativa preservada
- resultado:
  - microetapa pronta para nova rodada curta de homologacao visual/manual

## Correcao pontual da visualizacao comparativa em `Evolucao por categorias`

- tratei a rodada como correcao focada de homologacao, sem reimplementar a comparacao e sem mexer no fluxo normal da tela
- correcao aplicada no consolidado:
  - troquei a legenda generica pelas faixas reais de `Periodo principal` e `Periodo comparativo`
  - endureci a exibicao de rotulos sobre os pontos: quando o comparativo consolidado fica denso demais, os valores deixam de ser desenhados no grafico e permanecem no tooltip para evitar sobreposicao
- correcao aplicada no separado:
  - mantive a `Tabela comparativa` como protagonista
  - devolvi um grafico-resumo secundario, curto e discreto, para a tela nao ficar sem apoio visual
- preservacao garantida:
  - sem periodo comparativo preenchido, o grafico e a leitura normal continuam inalterados
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK para:
    - `normal`
    - `comparativo_consolidado`
    - `comparativo_separado`
- resultado:
  - microetapa pronta para commit coeso
  - a homologacao visual/manual passa a ficar pronta para uma nova rodada curta de conferencia

## Refinamento da visualizacao da comparacao em `Evolucao por categorias`

- refinei apenas a visualizacao da comparacao ja entregue, sem reimplementar a feature e sem mexer no contrato de entrada `Periodo principal` + `Periodo comparativo`
- decisao de UX aplicada:
  - sem periodo comparativo preenchido, a tela continua exatamente no fluxo normal ja consolidado
  - com comparativo preenchido e leitura `Consolidado`, a comparacao passa a usar um unico grafico de linhas com duas series:
    - `Periodo principal`
    - `Periodo comparativo`
  - com comparativo preenchido e leitura `Separado`, o grafico deixa de disputar protagonismo com a comparacao analitica e a `Tabela comparativa` passa a ser a leitura principal
- no backend:
  - passei a devolver os labels do relatorio por periodo
  - criei um montador proprio do grafico consolidado da comparacao, somando visualmente os buckets de cada periodo para formar as duas series unicas
  - preservei sem regressao a montagem do modo normal e a base da tabela comparativa
- no template:
  - removi os dois graficos paralelos como visual principal da comparacao
  - exibi grafico unico apenas na comparacao consolidada
  - deixei a comparacao detalhada mais contida, com foco na tabela
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK para:
    - `normal_sem_comparativo`
    - `comparativo_consolidado`
    - `comparativo_detalhado`
- resultado:
  - a tela ficou pronta para commit coeso desta microetapa
  - a proxima microetapa logica passa a ser validacao visual/manual curta do comparativo refinado no navegador, seguida da decisao de acabamento fino ou evolucao futura da tabela/exportacao

## Refinamento de UX da comparacao entre periodos em `Evolucao por categorias`

- refinei a feature ja entregue, sem reimplementa-la do zero e sem abrir nova tela
- a principal mudanca de contrato foi:
  - sair da logica de `modo normal` versus `modo comparacao`
  - entrar na logica de `Periodo principal` + `Periodo comparativo` opcional
- decisao de UX aplicada:
  - o usuario nao precisa mais escolher um modo extra para comparar
  - se preencher o `Periodo comparativo`, a comparacao acontece automaticamente
  - se deixar o comparativo vazio, a tela continua como consulta normal
  - `Periodo A/B` deixou de ser linguagem principal da interface
- o seletor de modo foi mantido apenas parcialmente:
  - permaneceu como seletor do tipo de analise do grafico
  - deixou de controlar a ativacao da comparacao
- no backend:
  - reaproveitei a logica de comparacao ja pronta
  - a view passou a identificar a comparacao automaticamente pelo preenchimento do periodo comparativo
  - a montagem comparativa passou a reaproveitar tambem o `modo` analitico atual, sem desperdiçar a estrutura existente
- no template:
  - os blocos de filtro passaram a exibir `Periodo principal` e `Periodo comparativo`
  - KPIs, cards e tabela comparativa passaram a usar a mesma nomenclatura mais humana
  - o modo normal seguiu intacto
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK para:
    - consulta normal sem periodo comparativo
    - comparacao automatica com periodo comparativo preenchido
    - presenca de `Tabela comparativa`, `Diferenca absoluta` e `Variacao percentual`
- resultado:
  - refinamento pronto para commit coeso
  - a proxima microetapa logica passa a ser validacao visual/manual curta desse fluxo simplificado no navegador
  - depois disso, decidir se a tela pede apenas acabamento fino ou se vale evoluir exportacao/tabela comparativa

## Comparacao entre periodos na tela `Evolucao por categorias`

- evolui a tela existente, sem abrir nova view isolada, para suportar o modo `Comparacao entre periodos`
- o backend da `EvolucaoCategoriasFinanceiroView` foi reorganizado para separar:
  - montagem de relatorio por periodo
  - montagem do modo normal
  - montagem do modo comparativo entre dois intervalos
- o modo novo passou a aceitar:
  - `Periodo A`
  - `Periodo B`
  - os mesmos filtros analiticos do modo normal
- decisao de UX aplicada:
  - manter a mesma tela e o mesmo shell
  - esconder o periodo simples quando o modo e comparacao
  - mostrar blocos compactos e claros para `Periodo A` e `Periodo B`
  - preservar os filtros secundarios recolhidos por padrao
  - manter a tabela comparativa recolhida por padrao
- decisao funcional aplicada:
  - comparar lado a lado os dois intervalos usando a mesma selecao de contas e itens analiticos
  - entregar por item:
    - valor do `Periodo A`
    - valor do `Periodo B`
    - diferenca absoluta
    - variacao percentual segura
  - evitar percentual artificial quando a base e zero, usando `—` quando necessario
- no template, a comparacao foi apresentada com:
  - KPIs proprios do modo comparacao
  - dois blocos graficos separados, um para cada periodo
  - `Tabela comparativa` com totais finais
  - impressao ainda isolando apenas a area util do relatorio
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK:
    - modo normal preservado
    - modo comparacao respondendo `200`
    - comparacao valida com categoria pai e com subcategoria
    - renderizacao de `Periodo A`, `Periodo B`, `Tabela comparativa`, `Diferenca absoluta` e `Variacao percentual`
- resultado:
  - microetapa pronta para commit coeso
  - a proxima frente logica deixa de ser a comparacao em si e passa a ser validacao visual/manual curta do novo modo, seguida da decisao de refinamento ou exportacao futura

## Fechamento do bloco aberto da tela `Evolucao por categorias`

- fechei o working tree aberto da tela sem misturar nova feature
- o diff final mantido neste bloco ficou restrito a:
  - [financeiro/views.py](C:\Users\lucia\OneDrive\Área de Trabalho\Casa_Espirita\financeiro\views.py)
  - [financeiro/templates/financeiro/evolucao_categorias.html](C:\Users\lucia\OneDrive\Área de Trabalho\Casa_Espirita\financeiro\templates\financeiro\evolucao_categorias.html)
  - [docs/STATE.md](C:\Users\lucia\OneDrive\Área de Trabalho\Casa_Espirita\docs\STATE.md)
  - [docs/CODEX_RESULTADO.md](C:\Users\lucia\OneDrive\Área de Trabalho\Casa_Espirita\docs\CODEX_RESULTADO.md)
  - [docs/ROADMAP_FINANCEIRO.md](C:\Users\lucia\OneDrive\Área de Trabalho\Casa_Espirita\docs\ROADMAP_FINANCEIRO.md)
- consolidacao final mantida na tela:
  - seletor simplificado em uma linha, com `+`/`-` antes do nome
  - ordenacao visivel final no frontend, sem acento e sem diferenca de caixa
  - separacao clara entre `Categorias` e `Subcategorias`
  - leitura `Consolidado` / `Separado`
  - granularidade configuravel
  - grafico em valor absoluto
  - escala do eixo Y arredondada e sem `R$`
  - impressao apenas da area do relatorio
  - tabela de apoio recolhida por padrao
- ajuste de escopo feito no fechamento:
  - retirei do diff a alteracao colateral na ordenacao de filtros da `lancamento_list`, para que o commit feche apenas a frente da `Evolucao por categorias`
- validacoes executadas nesta etapa de fechamento:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- observacao de ordem correta:
  - a proxima frente continua sendo `Comparacao entre periodos`, mas ela nao entra neste commit
- resultado:
  - bloco pronto para commit coeso, sem abrir nova frente

## Evolucao por categorias: escala do grafico limpa, sem `R$`, e ordenacao visivel validada

- apliquei a microetapa corretiva curta focada apenas em tres pontos:
  - escala do eixo Y
  - remocao de `R$` da visualizacao do grafico
  - ordenacao visivel das categorias
- causa real da falha de ordenacao:
  - no escopo `Subcategorias`, a lista ainda era montada com prioridade por `categoria_pai`, o que quebrava a ordem alfabetica que o usuario enxergava
  - no frontend, o seletor mantinha a ordem herdada do DOM e nao reordenava a lista final apos carregar, trocar `Escopo` ou aplicar busca
- correcoes aplicadas:
  - o eixo Y deixou de usar divisao crua do range e passou a usar ticks arredondados/bem comportados
  - os rotulos do grafico deixaram de exibir `R$` no eixo e sobre os pontos
  - o tooltip do ponto continuou com valor monetario completo
  - a montagem de `Subcategorias` passou a priorizar o nome exibido
  - o JS do seletor passou a ordenar a lista final com `Intl.Collator('pt-BR')`, em modo `accent-insensitive` e `case-insensitive`
  - a leitura visivel foi revalidada em navegador real, inclusive com caso acentuado e com busca aplicada
- validacao executada nesta rodada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - validacao visual/manual real no Edge com screenshots:
    - `tmp/validacao_evolucao_categorias_escala_ordenacao.png`
    - `tmp/validacao_evolucao_categorias_ordenacao_aberta.png`
    - `tmp/validacao_ordenacao_categorias_aberta.png`
    - `tmp/validacao_ordenacao_subcategorias_busca.png`
- resultado visual confirmado:
  - eixo com escala limpa
  - rotulos sem `R$`
  - categorias visivelmente em ordem crescente
  - subcategorias visivelmente em ordem crescente mesmo apos busca por `agua`
- observacao:
  - a microetapa continua sem commit por decisao do fluxo atual; o working tree permanece aberto

## Evolucao por categorias ainda bloqueada para commit por falta de validacao visual final

- tratei como verdade o retorno do uso real: apenas o recolhimento do filtro estava aprovado; os demais pontos nao podiam mais ser marcados como resolvidos so por smoke tecnico
- nesta rodada apliquei uma nova correcao de codigo focada nos bloqueios ainda abertos:
  - removi o texto auxiliar remanescente da area principal de filtros
  - reforcei a ordenacao `case-insensitive` e `accent-insensitive`
  - troquei a prioridade de ordenacao das categorias para leitura alfabetica real, sem deixar `tipo` liderar a UX da lista
  - simplifiquei os rotulos curtos do grafico para eliminar o caso em que o usuario via apenas `R`
  - aumentei a largura base do SVG e o espaco inferior do eixo para favorecer os labels temporais
  - mantive a impressao isolada na area do relatorio e sem abrir automaticamente a tabela de apoio
- validacao executada nesta rodada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado principal OK
  - smoke complementar OK para ordenacao renderizada no HTML e estrutura de impressao
- BLOQUEIO ABERTO:
  - a microetapa continua sem commit porque ainda falta validacao visual/manual real no navegador para confirmar:
    - ordenacao visivel correta
    - impressao realmente limitada ao relatorio
    - tabela recolhida fora do impresso
    - ausencia visual do texto auxiliar
    - rotulos de dados corretos
    - eixo temporal visivel e legivel

## Evolucao por categorias com ordenacao acento-insensivel e impressao apenas do relatorio

- apliquei uma rodada corretiva adicional antes do commit para fechar os bloqueios reais ainda abertos na tela
- correcoes aplicadas:
  - ordenacao `case-insensitive` e `accent-insensitive` nas listas da `Evolucao por categorias`
  - o mesmo criterio foi levado para seletores equivalentes do `financeiro` que impactam a leitura operacional da listagem de lancamentos
  - a impressao deixou de usar a pagina inteira e passou a isolar apenas a area documental do relatorio
  - o impresso agora usa um cabecalho proprio com resumo humano dos filtros aplicados
  - a tabela mensal nao e mais forcada a abrir antes da impressao e nao sai no papel quando estiver recolhida
- ajuste tecnico relevante:
  - criei helper unico de ordenacao textual sem acento/sem diferenca de caixa em `financeiro/views.py`
  - o template da `Evolucao por categorias` passou a usar um wrapper proprio de impressao (`financeiro-evolucao-print-area`) com CSS de isolamento visual
  - a chamada JS do botao `Imprimir relatorio` deixou de abrir automaticamente a tabela de apoio
- validacoes executadas nesta rodada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado principal da tela OK
  - smoke complementar OK confirmando:
    - ordenacao correta de `contas`, `favorecidos` e `categorias`
    - texto auxiliar removido no escopo `Categorias`
    - estrutura de impressao restrita ao relatorio
    - tabela recolhida nao sendo promovida automaticamente ao impresso

## Evolucao por categorias refinada com escopo, leitura e impressao

- apliquei uma rodada corretiva final para fechar os quatro bloqueios imediatos antes do commit
- correcoes aplicadas:
  - painel de filtros volta recolhido por padrao depois do submit
  - remocao dos textos auxiliares desnecessarios na superficie principal da selecao
  - rotulos de dados do grafico passaram a usar formato curto coerente, sem truncar em apenas `R`
  - labels temporais do eixo X ficaram robustos e visiveis conforme a granularidade ativa
- ajuste tecnico relevante:
  - o template deixou de abrir automaticamente o painel so porque existem filtros ativos
  - a view passou a gerar rotulo curto proprio para os valores desenhados no SVG
  - o eixo X passou a selecionar labels visiveis de forma controlada, evitando poluicao ou sumico de datas
- validacoes executadas nesta rodada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK confirmando:
    - atualizacao real do grafico
    - painel de filtros recolhido por padrao
    - rotulos de dados sem truncamento indevido
    - labels temporais visiveis em `Dias`, `Meses`, `Trimestres` e `Anos`

- refinei a mesma tela antes do commit para corrigir pontos de UX e leitura que ainda estavam ruins no uso real
- correcoes aplicadas nesta rodada:
  - troca imediata de `Escopo` entre `Categorias` e `Subcategorias`, atualizando a lista visivel e a busca sem depender do submit
  - exibicao limpa das categorias pai no escopo `Categorias`, sem texto de apoio desnecessario na linha principal
  - novo controle de `Granularidade` com `Dias`, `Meses`, `Trimestres` e `Anos`
  - novo controle `Mostrar valores no grafico` com opcao `Sim/Nao`
  - titulo do grafico passando a refletir a granularidade ativa
  - tabela mensal mantida recolhida por padrao, agora com rotulo explicito de `Mostrar tabela mensal` / `Ocultar tabela mensal`
- ajuste funcional relevante:
  - o backend do relatorio deixou de estar preso a buckets mensais e passou a montar os agrupamentos temporais de forma generica por dia, mes, trimestre ou ano
  - o eixo do grafico e a tabela de apoio passaram a usar os mesmos buckets, evitando renderizacao confusa como `0` e `1`
- regra final da granularidade:
  - `Dias` usa `dd/mm`
  - `Meses` usa `mm/aa`
  - `Trimestres` usa `1o tri/25`, `2o tri/25`...
  - `Anos` usa `YYYY`
- arquivos alterados nesta rodada:
  - `financeiro/views.py`
  - `financeiro/templates/financeiro/evolucao_categorias.html`
  - `tmp/validar_evolucao_categorias.py`
  - `docs/STATE.md`
  - `docs/CODEX_RESULTADO.md`
  - `docs/ROADMAP_FINANCEIRO.md`
- validacoes executadas nesta rodada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK para:
    - `escopo categorias`
    - `escopo subcategorias`
    - granularidade `dias`, `meses`, `trimestres` e `anos`
    - periodo menor que `30 dias`
    - `comparativo entrada x saida`
    - toggle da tabela mensal
    - renderizacao da opcao `Mostrar valores no grafico`

- evolui a tela `Evolucao por categorias` antes do commit, sem abrir nova frente fora do relatorio
- diagnostico reaproveitado:
  - a primeira versao da tela ja tinha rota, view, grafico SVG server-side e entrada no menu de `Relatorios`
  - a base atual tambem ja tinha filtro de contas e estrutura mensal suficiente para expandir a UX sem mexer no shell/topbar
- melhorias implementadas:
  - separacao explicita do escopo em `Categorias` e `Subcategorias`
  - seletor multiplo limpo por checklist, com busca dinamica
  - destaque visual entre categoria pai e subcategoria no seletor
  - novo controle de forma de leitura:
    - `Consolidado`
    - `Separado`
  - eixo temporal ajustado para `mm/aa`
  - tabela mensal de apoio recolhida por padrao, com toggle
  - botao `Imprimir relatorio` com resumo humano dos filtros e CSS proprio de impressao
- regra final entregue:
  - `Escopo = Categorias`
    - `Consolidado`: uma unica serie somando as categorias escolhidas
    - `Separado`: uma serie por categoria escolhida
  - `Escopo = Subcategorias`
    - `Consolidado`: uma unica serie somando as subcategorias escolhidas
    - `Separado`: uma serie por subcategoria escolhida
- ajuste importante do modo `Comparativo entrada x saida`:
  - o grafico passou a preservar os nomes reais das categorias/subcategorias selecionadas, sem cair apenas em rotulos genericos
- arquivos alterados nesta microetapa:
  - `financeiro/views.py`
  - `financeiro/templates/financeiro/evolucao_categorias.html`
  - `tmp/validar_evolucao_categorias.py`
  - `docs/STATE.md`
  - `docs/CODEX_RESULTADO.md`
  - `docs/ROADMAP_FINANCEIRO.md`
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com usuario real OK para:
    - `escopo categorias`
    - `escopo subcategorias`
    - `modo consolidado`
    - `modo separado`
    - `comparativo entrada x saida` com nomes reais
    - `tabela mensal` recolhida por padrao
    - botao `Imprimir relatorio` renderizado

## Relatorio grafico de evolucao por categorias

- implementei a nova tela `Evolucao por categorias` no modulo `financeiro`
- diagnostico reaproveitado:
  - a base de `Resumo` e `Prestacao de Contas` ja entregava padrao de filtros compactos, contas selecionaveis e shell coerente para relatorios
  - o modulo ja tinha helpers de periodo e formatacao monetaria reutilizaveis em `financeiro/views.py`
  - nao havia infraestrutura de graficos no repositorio, entao optei pela menor solucao segura: grafico SVG gerado no servidor, sem dependencia nova de JS externo
- solucao implementada:
  - nova rota `financeiro:evolucao-categorias`
  - nova view `EvolucaoCategoriasFinanceiroView`
  - novo template `financeiro/templates/financeiro/evolucao_categorias.html`
  - novo ponto de entrada na secao `Relatorios` do menu superior do `financeiro`
- filtros entregues:
  - `data inicial`
  - `data final`
  - `categorias/subcategorias` com selecao multipla
  - `contas` opcionais no mesmo padrao dropdown do modulo
  - `modo do grafico`
- modos entregues:
  - `Evolucao de categorias selecionadas`
    - uma serie por categoria/subcategoria selecionada
    - quando a selecao e de categoria pai, a serie agrega as subcategorias lancaveis
  - `Comparativo entrada x saida`
    - compara no mesmo eixo temporal a soma mensal das categorias de receita e de despesa selecionadas
- regra de seguranca aplicada ao filtro:
  - a tela bloqueia a combinacao de `Categoria` agrupadora com sua propria `Subcategoria` no mesmo grafico para evitar sobreposicao e dupla contagem
- regra temporal/financeira adotada:
  - eixo mensal
  - `data_pagamento` como data operacional principal, com fallback para `data_competencia`
  - `receitas` positivas
  - `despesas` negativas
- saida final da tela:
  - grafico mensal
  - legenda por serie
  - tabela mensal de apoio
  - KPIs do periodo (`receitas`, `despesas`, `quitado`, `em aberto`, `saldo liquido`, `lancamentos considerados`)
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback/logica local confirmando:
    - acesso `200` a tela
    - modo `categorias` com render do grafico e da tabela
    - modo `comparativo` com series `Entradas` e `Saidas`

## Trava de seguranca para importacoes com base ja preenchida

- implementei uma trava previa na central de importacoes do `financeiro`
- a verificacao agora acontece antes da validacao da planilha e antes de qualquer tentativa de gravacao
- dominios cobertos:
  - `contas`
  - `pessoas/favorecidos`
  - `categorias/subcategorias`
  - `centros de custo`
  - `lancamentos`
- regra aplicada:
  - se o dominio correspondente ja tiver registros, a importacao e barrada
  - nenhuma linha e processada
  - nenhuma importacao parcial acontece
- mensagens finais entregues por dominio, com texto explicito de bloqueio
- a implementacao ficou concentrada em `financeiro/views.py`, reutilizando helper unico para detectar base preenchida e devolver a mensagem padrao correspondente
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado transacional com rollback OK:
    - importacao de `lancamentos` em dominio vazio temporario seguiu para a validacao normal da planilha e nao foi bloqueada pela nova trava
    - importacao de `contas` em dominio preenchido foi barrada com a mensagem clara esperada
- observacao de validacao:
  - a base local atual estava preenchida em todos os cinco dominios
  - para provar o cenario de dominio vazio sem tocar na base real, o smoke esvaziou `lancamentos` apenas dentro de uma transacao com rollback

## Reconciliacao explicita do saldo na Prestacao de Contas

- revisei a montagem da `Prestacao de Contas` para resolver a leitura enganosa do saldo final quando havia transferencia entre conta selecionada e outra conta da instituicao fora do filtro
- a situacao de origem nao era erro de saldo bruto: o `saldo_final_consolidado` ja vinha correto pelos saldos reais das contas selecionadas; o problema era que o fechamento visual ainda parecia apenas `saldo inicial + receitas - despesas`
- corrigi a reconciliacao exibida no relatorio sem mudar a natureza contabil das transferencias
- regra final aplicada:
  - transferencias entre contas selecionadas e outras contas da instituicao nao entram como receitas
  - nao entram como despesas
  - mas entram explicitamente na reconciliacao do saldo final consolidado como:
    - `Entradas de outras contas da instituicao`
    - `Saidas para outras contas da instituicao`
- formula final entregue no relatorio:
  - `Saldo final consolidado = saldo inicial consolidado + receitas do periodo - despesas do periodo + entradas de outras contas da instituicao - saidas para outras contas da instituicao`
- atualizei a view para calcular e expor:
  - `total_entradas_outras_contas`
  - `total_saidas_outras_contas`
  - `saldo_final_reconciliado`
  - indicador de consistencia entre o saldo reconciliado e o saldo consolidado real
- atualizei o template da `Prestacao de Contas` para mostrar esses blocos tanto nos KPIs quanto no resumo final do fechamento
- atualizei o smoke transacional com rollback para validar os dois casos:
  - transferencia da conta selecionada para conta externa
  - transferencia de conta externa para conta selecionada
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - `py manage.py shell -c "exec(open(r'tmp/validar_prestacao_contas.py', encoding='utf-8').read())"` OK

## Simplificacao final das acoes documentais e linguagem da Prestacao de Contas

- removi a redundancia de acoes documentais na `lancamento_list`
- a interface passou a manter apenas:
  - `Recibos em lote`
  - `Termo anual de quitacao`
- `Recibos em lote` agora usa os lancamentos selecionados e agrupa automaticamente por favorecido:
  - um favorecido gera um unico recibo
  - varios favorecidos geram blocos sucessivos no mesmo documento, com quebra entre grupos
- preservei a consolidacao por descricao aprovada para os recibos, sem reintroduzir categoria como elemento de bloqueio ou destaque visual
- `Termo anual de quitacao` passou a assumir sozinho a emissao simples e em massa:
  - usa o resultado filtrado atual da listagem
  - continua filtrando internamente apenas receitas quitadas
  - gera um ou varios termos conforme os favorecidos encontrados no filtro
- mantive a rota plural antiga apenas como compatibilidade tecnica, redirecionando para a acao unificada
- na `Prestacao de Contas`, troquei a linguagem tecnica:
  - `Entradas de contas fora do universo` -> `Entradas de outras contas da instituicao`
  - `Saidas para contas fora do universo` -> `Saidas para outras contas da instituicao`
- no `Termo anual de quitacao`, troquei o fechamento para o mesmo estilo manuscrito do recibo oficial, reaproveitando a mesma linguagem visual da assinatura institucional
- validacoes planejadas para este ajuste: `py manage.py check`, `py -m compileall financeiro`, `git diff --check` e smoke do bloco documental unificado

## Evolucao do termo anual: assinatura estavel, acao em massa e filtro interno automatico

- estabilizei a assinatura real do `Termo anual de quitacao`
- a busca institucional do fechamento agora usa assinatura ativa padrao ou, na falta dela, a primeira assinatura ativa disponivel, evitando que o bloco final desapareca
- o template do termo anual passou a exibir o `assinatura_texto` quando houver, mantendo local/data, linha de assinatura, nome e cargo
- mantive a acao `Termo anual de quitacao`, que agora cobre sozinha os cenarios de um ou varios favorecidos no resultado filtrado
- a rota plural antiga de termos anuais ficou apenas como compatibilidade tecnica e redireciona para a acao unificada
- comportamento consolidado da acao:
  - usa o filtro atual da listagem
  - aplica internamente a triagem documental compativel
  - agrupa por favorecido
  - gera documento continuo com uma secao por favorecido e quebra de pagina entre eles quando houver varios grupos
- regra automatica consolidada do termo anual, sem exigir filtro manual do usuario:
  - considerar apenas lancamentos do tipo `receita`
  - considerar apenas lancamentos com status `quitado`
  - ignorar automaticamente `despesas`, `transferencias`, `receitas em aberto` e outros itens incompativeis
- quando nenhum item compativel resta apos essa triagem, a acao retorna com a mensagem: `Nenhum lancamento compativel com termo anual de quitacao foi encontrado no filtro atual.`
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback cobrindo termo anual unificado, ignorar automatico de despesas/transferencias/em aberto e mensagem de ausencia de itens compativeis OK

## Ajuste visual e textual do termo anual de quitacao

- refinei o `Termo anual de quitacao` para ele deixar de parecer recibo ou tela filtrada
- removi do topo a `Quantidade de lancamentos` e o bloco visual de chips/badges que estava deixando a peca com cara de relatorio interno
- mantive o cabecalho com identidade propria:
  - titulo `TERMO ANUAL DE QUITACAO`
  - subtitulo institucional no formato `Declaracao anual de quitacao referente ao ano de ...`
  - identificacao textual simples de `Favorecido`
- quando existe filtro de categoria ativo, a informacao continua disponivel, mas em linha textual simples, sem visual de filtro
- atualizei o texto introdutorio para a redacao aprovada: declaracao anual mais humana e institucional, sem cara de recibo
- preservei a tabela com `Data`, `Descricao`, `Documento` e `Valor`, alem do fechamento com total, valor por extenso, local/data e assinatura institucional
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback do termo anual OK

## Ajuste final do termo anual: assinatura e repeticao do ano

- concentrei o ano apenas no subtitulo do termo, agora no formato `Referente ao ano de ...`
- removi a repeticao do ano do bloco de identificacao e do texto introdutorio, deixando o documento mais natural e menos artificial
- reduzi o bloco de identificacao do termo para a leitura aprovada de `Favorecido`, sem reintroduzir visual de filtro
- reforcei o fechamento documental do termo para a assinatura sempre aparecer:
  - a busca institucional agora usa a assinatura ativa padrao ou, na falta dela, a primeira assinatura ativa disponivel
  - o bloco final passa a renderizar sempre nome e cargo com fallback institucional coerente, sem depender de uma condicao que zere o fechamento
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback do termo anual final OK

## Ajuste da Prestacao de Contas: cabecalho enxuto e leitura de contas fora do universo

- simplifiquei o topo da `Prestacao de Contas` para a leitura aprovada: `Periodo`, `Emitido em`, `Saldo inicial consolidado`, `Receitas do periodo`, `Despesas do periodo` e `Saldo final consolidado`
- removi do cabecalho os blocos redundantes/tecnicos que poluiam a peca, incluindo a marca `Prestacao Financeira`, textos longos, `Contas incluidas` no topo e a duplicidade visual de saldo final
- mantive a selecao de contas apenas no painel de filtros e ajustei o rotulo para `Contas do relatorio`
- formalizei no relatorio a regra de universo consolidado: o saldo considera somente as contas selecionadas no filtro
- quando houver transferencia entre esse universo e contas de fora, como integralizacao ou outras contas nao operacionais, o relatorio passa a explicar isso em um bloco operacional proprio, fora do topo, sem transformar essas movimentacoes em receita ou despesa
- mantive inalterada a logica contabil principal ja aprovada; a microetapa foi de leitura/clareza do relatorio, nao de redefinicao das formulas
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback da `Prestacao de Contas` OK

## Fluxo documental centralizado na lancamento_list

- substitui a direcao de relatorio anual por favorecido como tela principal por tres acoes documentais na `lancamento_list`
- removi o relatorio anual das superficies principais: menu superior, listagem de favorecidos, historico do favorecido, rota, view e template
- unifiquei a interface de recibos em uma unica acao visivel: `Recibos em lote`
- essa acao usa os lancamentos selecionados, agrupa automaticamente por favorecido e renderiza um documento continuo com quebra por favorecido quando necessario
- o documento segue reaproveitando fielmente o recibo oficial ja existente, preservando cabecalho, texto explicativo, valor por extenso, mensagem final e bloco de assinatura
- na correcao seguinte, mudei a direcao documental dos recibos em lote: categoria deixou de ser elemento relevante de leitura, saiu do topo/documento e deixou de bloquear emissao quando houver categorias diferentes no mesmo favorecido
- passei a consolidar por descricao os itens repetidos dentro do mesmo favorecido, inclusive quando vierem de rateio; nesses casos o recibo soma os valores e mostra um unico item documental
- quando a consolidacao junta datas ou documentos diferentes, o recibo sinaliza isso de forma compacta como `Datas diversas` e `Doc. diversos`
- os recibos em lote passaram a usar fallback institucional/fixo do recibo oficial, sem depender de mensagem especifica por categoria para viabilizar a emissao
- implementei `Termo anual de quitacao`, usando o resultado filtrado atual da listagem, exigindo periodo anual coerente, receitas quitadas, favorecido e ausencia de rateio
- o recibo por favorecido deixou de usar template paralelo proprio e passou a nascer da mesma peca documental do recibo atual, apenas repetida por favorecido com quebra de pagina
- na correcao seguinte, ajustei a integridade do recibo em lote para ele nascer exclusivamente dos lancamentos selecionados, consolidando apenas descricoes exatamente iguais e mantendo linhas separadas quando a descricao muda
- nessa mesma correcao, o recibo em lote passou a sinalizar `Datas diversas` e `Doc. diversos` quando a consolidacao reunir datas ou documentos diferentes, sem reaproveitar `status` como dado documental visual
- tambem humanizei o `Termo anual de quitacao`: subtitulo mais amigavel, bloco de identificacao simplificado, texto introdutorio institucional e tabela reduzida para `Data`, `Descricao`, `Documento` e `Valor`
- mantive fora do escopo: PDF, anexos, assinatura final juridica, termo formal completo com juridiquês, contratos, parcelas e recorrencia

## Ajuste final dos quadros-resumo da listagem de lancamentos

- substitui a leitura principal antiga da `lancamento_list`, baseada em `Pagina atual`, `Status na pagina` e `Selecionados` com valor unico
- implementei um quadro-resumo financeiro do resultado filtrado completo, independente da paginacao, com receitas, despesas, transferencias de entrada, transferencias de saida e saldo liquido operacional
- a formula usada na listagem ficou: `saldo liquido = receitas + transferencias_entrada - despesas - transferencias_saida`
- deixei a paginacao como informacao auxiliar (`Mostrando X de Y lancamento(s)`)
- o quadro de selecionados passou a repetir a mesma estrutura do resumo principal, para selecoes mistas deixarem claro o que e receita, despesa, entrada, saida e saldo liquido
- mantive `Quitado` e `Em aberto` como leitura secundaria do resultado filtrado, sem competir com o resumo financeiro principal
- validacoes executadas: smoke autenticado com rollback confirmando resultado filtrado completo acima da pagina visivel e selecao mista, `py manage.py check` OK, `py -m compileall financeiro` OK e `git diff --check` OK

## Correcao de totalizadores liquidos e paineis recolhidos por padrao

- corrigi os totalizadores da `lancamento_list` para usarem o sinal operacional do movimento, em vez de somarem apenas valores absolutos
- a regra aplicada foi: receita positiva, despesa negativa, transferencia de saida negativa e transferencia de entrada positiva quando a tela esta filtrada pela conta destino
- o ajuste cobre total da pagina, totais da pagina separados por `Quitado`/`Em aberto` e total dinamico dos selecionados
- mantive a coluna `Valor` como valor nominal do documento, preservando a leitura da linha, enquanto os cards agregados passaram a representar saldo liquido
- ajustei os paineis compactos de filtros/configuracoes/opcoes secundarias para iniciarem recolhidos em `lancamento_list`, `pessoa_historico`, `resumo` e `prestacao_contas`
- os indicadores discretos de filtros ou opcoes ativas foram preservados, para nao esconder estado operacional importante
- validacoes executadas: smoke autenticado com rollback para totalizadores com receita/despesa/transferencia e selecao mista, `pessoa_historico`, `resumo` com/sem transferencias e `prestacao_contas` com/sem transferencias; `py manage.py check` OK; `py -m compileall financeiro` OK; `git diff --check` OK

## Refinamentos de observacoes e transferencias nos relatorios financeiros

- ajustei a coluna `Observacoes` da listagem principal de lancamentos para limitar a largura util e permitir quebra de linha/palavras longas
- acrescentei o checkbox `Exibir transferencias` no `Resumo` e na `Prestacao de Contas`
- mantive o comportamento padrao sem transferencias quando o checkbox esta desligado
- quando ligado, os relatorios exibem as transferencias quitadas do periodo em bloco separado, com data, descricao, conta origem, conta destino, documento e valor
- o bloco de transferencias exibe total movimentado e totalizadores separados de entrada e saida
- as transferencias continuam fora dos totais de receitas e despesas; o bloco serve apenas para conferencia operacional e fechamento de contas
- o filtro de contas tambem considera transferencias em que a conta selecionada aparece como destino
- filtros, configuracoes de colunas e opcoes secundarias das telas tocadas foram compactados em paineis recolhiveis para reduzir peso visual sem esconder acoes essenciais
- validacoes executadas: `py manage.py check` OK, `py -m compileall financeiro` OK, `git diff --check` sem erros bloqueadores e smoke autenticado com rollback para `lancamento_list`, `Resumo`, `Prestacao de Contas` e `Historico do favorecido`

## Historico por favorecido no modulo financeiro

- implementei a pagina dedicada `Historico do favorecido`, acessada pela listagem de `Favorecidos financeiros`
- diagnostico reaproveitado:
  - ja existia endpoint curto de ultimos lancamentos do favorecido no formulario de lancamento
  - ja existia padrao de data operacional por `data_pagamento` com fallback para `data_competencia`
  - ja existiam permissao funcional e shell/topbar do financeiro para a nova tela seguir sem criar arquitetura paralela
- a solucao minima adotada foi uma `DetailView` de `PessoaFinanceira` com queryset filtrado de `LancamentoFinanceiro`
- filtros entregues: data inicial, data final, tipo, status, conta e busca por descricao ou numero de documento
- totalizadores entregues no topo: total geral, total de receitas, total de despesas, total quitado e total em aberto, sempre sobre o resultado filtrado
- tabela entregue com data operacional, tipo, status, descricao, conta origem, conta destino, categoria, centro de custo, documento e valor
- a permissao usada foi `financeiro.lancamentos.listar`; nao criei permissao nova nem alterei a matriz
- nao implementei exportacao especifica do historico, contratos, anexos nem codigo automatico para contas/categorias
- validacoes executadas: `py manage.py check` OK, `py -m compileall financeiro` OK e smoke autenticado com rollback confirmando rota, link de acesso, totais, colunas e filtros

## Consolidacao final do working tree do ciclo recente do financeiro

- auditei o working tree pendente e separei os blocos em: reconciliacao documental, fluxo contextual/`return_to`, importacao/exportacao/listagens auxiliares, extrato/mascara/recibo/refinamentos finais e artefatos `tmp/`
- criei o commit funcional `8912cb7d500a6a2e3dc862a629445919a9ae04fd` com a mensagem `fix(financeiro): consolida fluxo contextual e ajustes finais`
- o commit funcional consolidou:
  - `return_to` nas listagens, formularios, cancelamentos e exclusoes dos cadastros principais do financeiro
  - botao compacto `+` para salvar e permanecer nos formularios auxiliares onde aplicavel
  - `Exportar` contextual em contas, favorecidos, categorias e centros de custo
  - remocao do botao redundante `Voltar para lancamentos` da central de importacoes
  - checkbox `Exibir observacao` no extrato
  - ajuste fino da mascara monetaria para evitar formatacao duplicada com zeros a esquerda
- `tmp/` foi mantido como artefato local fora de commit e adicionado ao `.gitignore`, preservando pacotes/validacoes locais sem poluir o versionamento
- validacoes executadas: `py manage.py check` OK, `py -m compileall financeiro` OK, smoke autenticado com rollback das telas afetadas OK e `git diff --check` OK
- pendencias que continuam fora deste fechamento: decisao de produto sobre expandir codigo automatico para `contas`/`categorias`

## Lote 1 do novo bloco operacional (importar removido, mascara monetaria, extrato e exclusao de favorecido)

- registrei o novo bloco de trabalho em lotes e executei o Lote 1 conforme prioridade definida
- removi o botao `Importar` da `lancamento_list`, mantendo a importacao centralizada no menu superior do financeiro
- implementei mascara monetaria pt-BR nos valores do lancamento: digitacao sem virgula e formatacao amigavel (`100000` -> `1.000,00`), com normalizacao para decimal antes do envio do formulario
- o extrato passou a oferecer checkbox `Exibir observacao`, controlando a exibicao da coluna de observacoes sem alterar a base do saldo
- a exclusao de favorecido passou a:
  - bloquear com mensagem clara quando ainda existirem lancamentos vinculados
  - desvincular regras automaticas antes da exclusao quando elas forem a unica amarra restante
- validacao executada: `py manage.py check` OK e `py -m compileall financeiro` OK

## Ajuste fino da mascara monetaria do lancamento

- causa confirmada: a mascara estava preservando zeros a esquerda do valor anterior (`0,00`), o que gerava casos como `0.001.000,00` ao digitar `100000`
- ajuste aplicado: a rotina de formatacao agora remove zeros a esquerda antes de separar centavos, mantendo a regra dos 2 ultimos digitos como centavos
- validacao executada na consolidacao final com exemplos `1 -> 0,01`, `10 -> 0,10`, `100 -> 1,00`, `1000 -> 10,00` e `100000 -> 1.000,00`

## Lote 2 do novo bloco operacional (codigo automatico e favorecido rapido no lancamento)

- implementei geracao automatica de codigo quando o campo estiver vazio para `Favorecidos` e `Centros de custo`
- o codigo manual continua sendo respeitado quando informado pelo usuario
- implementei fluxo rapido de `Novo favorecido` no formulario de lancamento:
  - o lancamento em andamento fica salvo em `sessionStorage`
  - apos salvar o favorecido, o formulario de lancamento e restaurado com os dados anteriores
  - o favorecido recem-criado ja aparece selecionado
- substitui os botoes textuais por `+` ao lado de `Favorecido`, `Categoria` e `Centro de custo`, mantendo a logica de rascunho e retorno com item criado selecionado
- corrigi o posicionamento do `+`: agora ele fica ao lado do campo, fora do input, alinhado a direita sem sobreposicao
- validacao tecnica executada: `py manage.py check` OK e `py -m compileall financeiro` OK

## Lote 3 do novo bloco operacional (recibo em lote por favorecido)

- adicionei a acao `Recibo em lote (mesmo favorecido)` nas acoes em lote da listagem de lancamentos
- regra consolidada:
  - todos os lancamentos selecionados precisam ter o mesmo favorecido
  - apenas lancamentos do tipo receita
  - sem rateio (documentos simples)
- quando valido, o sistema gera um unico recibo consolidado:
  - favorecido identificado no topo
  - lista de descricoes com valores
  - valor total consolidado
- validacao tecnica executada: `py manage.py check` OK e `py -m compileall financeiro` OK

## Ajuste do recibo em lote (erro de template + corpo detalhado)

- causa confirmada: o template do recibo em lote ainda referenciava `lancamento.*`, o que quebra o render quando so existem variaveis `recibo_*`
- ajuste aplicado: separacao explicita entre recibo individual e lote, usando apenas `recibo_*` no lote
- o corpo do lote passou a listar data, descricao e valor por item
- no lote, o rotulo `Numero` foi substituido por `Lote` e a frase passou a ser `Referente aos lancamentos listados abaixo.`
- quando nao houver identificador real, o lote nao deve repetir o texto `Lote` como valor (evita `Lote Lote`)

## Correcao do menu suspenso, importacoes no menu e limpeza de legado

- reabri a correcao visual porque o uso real mostrou que o menu suspenso do `financeiro` ainda podia abrir atras do conteudo
- causa exata: a topbar usava `backdrop-filter`, criando stacking context proprio; manter o dropdown como descendente absoluto da topbar ainda podia deixar o painel preso abaixo de cards/formularios em render real, mesmo com reforco de `z-index`
- correcao reforcada em `financeiro/templates/financeiro/base.html`:
  - mantive camada/overflow explicitos na topbar
  - converti `.financeiro-menu-panel` para camada fixa com `z-index` global alto
  - ajustei o JavaScript para mover o painel do menu para `document.body` e posiciona-lo pelo retangulo do botao `Menu` no momento da abertura
- inclui `Importacoes` no menu superior do financeiro em `Movimentacao > Importacoes`, apontando para a central `financeiro:lancamento-importacao-exportacao`
- mantive a regra operacional aprovada: importacoes auxiliares e lancamentos entram pela central; exportacoes continuam locais nas listagens porque dependem dos filtros de cada tela
- removi o botao `Voltar para lancamentos` da pagina central de importacoes, porque o menu superior passa a ser o acesso principal
- substitui `Importar` por `Exportar` nas listagens de contas, favorecidos, categorias e centros de custo, agora apontando para exportacao local de cada listagem com os filtros ativos preservados
- avancei a limpeza de legado removendo o JavaScript ativo antigo de sidebar/drawer
- legado remanescente: foi removido nesta etapa de limpeza final

## Limpeza final do legado de sidebar/drawer no `financeiro`

- removi definitivamente o bloco HTML comentado da sidebar/drawer no `financeiro/base.html`
- removi o CSS legado associado (sidebar, drawer, overlay, toggle)
- o shell ativo do `financeiro` fica apenas com topbar + menu suspenso

## Migracao controlada do financeiro para topbar com menu suspenso

- implementei a migracao do shell ativo do `financeiro` em `financeiro/templates/financeiro/base.html`, seguindo a decisao tomada apos a auditoria estrutural de navegacao
- a topbar agora concentra uma unica camada principal com:
  - identidade do modulo `Financeiro`
  - botao `Menu`
  - usuario e perfil
  - `Inicio do sistema`
  - `Admin tecnico` quando aplicavel
  - `Sair`
- o menu suspenso foi agrupado em `Visao geral`, `Movimentacao`, `Relatorios`, `Cadastros` e `Institucional`
- os links do menu continuam condicionados pelas permissoes ja existentes do `financeiro`, sem abrir bypass visual nem alterar regra de negocio
- removi da renderizacao ativa a competicao entre sidebar persistente, topbar mobile paralela, drawer, overlay e botao de recolher/expandir a navegacao lateral
- a sidebar/drawer antigos ficaram comentados no template como transicao reversivel, portanto nao aparecem no HTML final; o JS antigo foi protegido por guarda e nao executa sem os elementos correspondentes
- a area principal do shell foi simplificada para nao reservar mais coluna de sidebar, melhorando a largura util das telas operacionais
- validacao executada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - smoke autenticado `200` em `lancamento_list`, `lancamento_form`, `conta_list`, `pessoa_list`, `categoria_list`, `centro_custo_list`, central de importacao/exportacao, extratos, resumo e prestacao de contas
  - smoke estrutural confirmou o novo `data-financeiro-menu-toggle`/`data-financeiro-menu-panel` e ausencia de controles renderizados da sidebar/drawer na `lancamento_list`
- pendencia nao bloqueante registrada: remover CSS/JS legado de sidebar/drawer em uma limpeza posterior se a topbar/menu for aprovada visualmente no navegador

## Auditoria estrutural da navegacao/menu do sistema

- auditei a navegacao atual sem implementar ainda o menu suspenso, conforme diretriz da microetapa
- mapeamento das camadas:
  - `configuracoes/sistema_base.html`: shell autenticado geral com topbar global, usuario/perfil e acoes de inicio/admin/sair
  - `biblioteca/base.html`: herda `sistema_base` e adiciona nav local horizontal do modulo
  - `eventos/base.html`: herda `sistema_base` e adiciona nav local horizontal simples do modulo
  - `financeiro/base.html`: shell proprio com topbar desktop, topbar mobile, botao de recolher sidebar, drawer mobile, overlay, sidebar persistente e grupos colapsaveis
  - `_sistema_usuario_acoes.html`: include comum reutilizado tanto pelo shell geral quanto pelo shell do financeiro
- origem da duplicacao percebida:
  - nao ha, no estado atual, varias bases herdadas simultaneamente nas telas do `financeiro`
  - a sensacao de sujeira vem do proprio `financeiro/base.html`, que concentra topbar propria, acoes globais, link de inicio do modulo, chip de contexto, sidebar persistente, drawer mobile e controles de recolher/abrir
  - alem disso, varias paginas financeiras adicionam headers locais com titulos e botoes de retorno/atalhos, o que aumenta a percepcao de navegacao em camadas
- paginas afetadas:
  - todas as telas autenticadas do `financeiro` que herdam `financeiro/base.html`
  - impacto mais evidente nas telas operacionais densas: `lancamento_list`, `lancamento_form`, cadastros auxiliares, relatorios, extratos e central de importacao/exportacao
  - `biblioteca` e `eventos` nao apresentam a mesma duplicacao estrutural; eles usam o shell geral e uma nav local horizontal simples
  - `configuracoes` usa o shell geral; a pagina `siteconfig_detail` tem override proprio de `topbar_actions`, mas sem criar uma sidebar paralela
- padrao recomendado definido:
  - adotar no `financeiro` um shell/topbar unico com navegacao principal por menu suspenso agrupado no topo
  - manter usuario/perfil/acoes globais na mesma barra, sem repetir linkagens equivalentes em varias camadas
  - remover a sidebar persistente como navegacao principal do desktop
  - preservar drawer/sidebar apenas como apoio responsivo ou transicional, se necessario
- recomendacao entre alternativas:
  - `menu suspenso no topo`: recomendacao principal, porque elimina a necessidade de expandir/recolher sidebar e reduz a competicao visual
  - `sidebar recolhida por padrao`: nao recomendada como solucao principal, porque preserva o comportamento que incomodou no uso real
  - `solucao hibrida`: aceitavel apenas como transicao ou responsivo mobile, desde que nao mantenha topbar e sidebar competindo no desktop
- docs atualizados:
  - `docs/CEREBRO_PROJETO.md` recebeu ajuste cirurgico porque continha diretriz antiga de sidebar persistente como principal no financeiro
  - `docs/PADRAO_UX_SISTEMA.md` recebeu a nova regra de evitar camadas concorrentes de navegacao e recomendar menu suspenso no topo para o financeiro
  - `docs/CHECKLIST_EVOLUCAO_SISTEMA.md` recebeu item de verificacao contra duplicacao de topbar/menu/sidebar/drawer/atalhos
  - `docs/STATE.md` recebeu o estado consolidado desta auditoria

## Refinamento visual dos totalizadores e acoes em lote da `lancamento_list`

- refinei visualmente a area de acoes em lote e totalizadores da `lancamento_list`, preservando a regra funcional ja aprovada para total da pagina, quitado/em aberto e selecionados
- removi a aparencia de seta duplicada/quebrada no select de `Novo status` ao neutralizar o pseudo-elemento visual do wrapper Bulma apenas nesse controle e reforcar o estilo do select local
- reorganizei os totalizadores em cards compactos, separando melhor `Pagina atual`, `Status na pagina` e `Selecionados`
- atualizei o helper `_formatar_moeda_brl()` para usar separador de milhar e duas casas decimais no padrao pt-BR, como `1.234,50`
- a coluna visual de valor da listagem passou a usar o mesmo valor formatado que os totalizadores, mantendo consistencia de leitura monetaria
- o totalizador dinamico de selecionados continua calculando no navegador, mas passou a renderizar na mesma estrutura visual dos demais cards
- validacao executada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - smoke de renderizacao da `lancamento_list` confirmando formatacao monetaria pt-BR, cards dos totalizadores e ajuste visual do select de acoes em lote

## Ajuste dos totalizadores da listagem e clone dos ultimos lancamentos

- corrigi a direcao dos totalizadores por status: `Quitado` e `Aberto` foram adicionados tambem na `lancamento_list`, junto do total da pagina atual e do total selecionado
- os totais da `lancamento_list` ficam explicitamente no escopo da pagina atual exibida: quantidade, soma total, soma quitada e soma em aberto
- mantive os totais `Quitado` e `Aberto` no painel `Ultimos lancamentos do favorecido`, porque essa leitura foi aprovada como util no formulario
- corrigi o bug do clone no GET sem `return_to`: o fallback de `get_cancel_url()`/`get_success_url()` deixou de chamar o `get_success_url()` object-dependent do `CreateView` quando a view tem `success_url` configurada
- ajustei o link de clone dos ultimos lancamentos para propagar `return_to` quando ele existir e for seguro, preservando o retorno contextual tambem nesse fluxo
- validacao executada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - smoke transacional com rollback confirmando totalizadores por status na `lancamento_list`
  - clone sem `return_to` usando fallback seguro
  - clone com `return_to` preservando retorno
  - link de clone do painel de ultimos lancamentos propagando `return_to`

## Correcoes de transferencia, totais por status e extrato por `data_pagamento`

- reforcei a mensagem de validacao para transferencia com a mesma conta na origem e no destino, sem afrouxar a regra ja existente no model
- a causa era que a regra ja estava no `LancamentoFinanceiro.clean()`, mas a mensagem ainda aparecia com termos tecnicos (`conta`/`conta_destino`) e precisava ficar operacional para o usuario
- atualizei a mensagem equivalente tambem em `RegraLancamentoFinanceiro`, mantendo coerencia com as regras automaticas
- no painel `Ultimos lancamentos do favorecido` do formulario de lancamento, acrescentei totais separados de `Quitado` e `Aberto`, calculados no endpoint `PessoaFinanceiraUltimosLancamentosView`
- o mesmo painel passou a exibir a coluna `Status`, para a soma por situacao ficar compreensivel na propria tabela
- no extrato por conta e na entrada geral de extratos, troquei a referencia operacional para `data_pagamento`: filtros de periodo, saldo anterior e ordenacao agora usam `Coalesce(data_pagamento, data_competencia)`, preservando fallback para legado sem pagamento
- validacao executada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - smoke transacional com rollback confirmando transferencia mesma conta invalida com mensagem unica, totais `Quitado`/`Aberto` no endpoint e ordem do extrato por data de pagamento
- observacao documental: `docs/CEREBRO_PROJETO.md` ainda contem uma regra antiga de extrato por `data_competencia`; como e documento protegido e nao foi autorizado para edicao nesta microetapa, ele nao foi alterado agora

## Ajuste do conjunto padrao da `lancamento_list`: `Tipo` essencial

- ajustei o conjunto essencial da listagem principal de lancamentos para incluir `Tipo` por padrao
- o padrao revisado ficou: selecao quando aplicavel, `Data pagamento`, `Tipo`, `Descricao`, `Valor` e `Acoes` quando aplicavel
- as colunas opcionais permaneceram as mesmas: `Favorecido`, `Conta origem`, `Conta destino`, `Status`, `Categoria`, `Centro de custo`, `Data competencia`, `Documento` e `Observacoes`
- a mudanca preserva o painel de configuracao, a ordem manual simples, a persistencia por sessao e os totalizadores ja implementados

## Colunas configuraveis, ordem manual e totalizadores na `lancamento_list`

- implementei um painel `Configurar colunas da listagem` na tela principal de lancamentos
- o padrao inicial ficou mais enxuto:
  - essenciais: selecao quando aplicavel, `Data pagamento`, `Tipo`, `Descricao`, `Valor` e `Acoes` quando aplicavel
  - opcionais: `Favorecido`, `Conta origem`, `Conta destino`, `Status`, `Categoria`, `Centro de custo`, `Data competencia`, `Documento` e `Observacoes`
- o usuario pode marcar/desmarcar colunas complementares e definir a ordem delas por seletores numericos simples
- a preferencia fica salva em sessao, sem criar estrutura nova de banco nesta etapa; isso evita migration e mantem a solucao reversivel
- foi adicionada acao `Restaurar padrao`
- a listagem ganhou totalizador da pagina atual exibida, mostrando quantidade de lancamentos e soma dos valores visiveis
- a selecao em lote ganhou totalizador dinamico no navegador, mostrando quantidade e soma dos lancamentos selecionados
- a grade continua respeitando o shell autenticado, a paginacao, os filtros, as acoes em lote e o agrupamento visual de rateios
- validacao executada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - smoke autenticado de `/financeiro/lancamentos/` OK
  - smoke autenticado com configuracao de colunas via querystring OK
  - smoke autenticado com restauracao do padrao OK
- limitacao consciente:
  - a persistencia ainda e por sessao; se o uso real exigir preferencia permanente entre navegadores/sessoes longas, a evolucao correta sera criar armazenamento proprio por usuario

## Melhoria de usabilidade da `lancamento_list`

- reduzi a pressao horizontal da coluna `Descricao` na tabela principal de lancamentos: a coluna ganhou classe propria, largura controlada e continua usando truncamento com reticencias para nao dominar a tabela
- adicionei uma barra de rolagem horizontal superior na tabela de lancamentos, sincronizada por JavaScript com o wrapper inferior ja existente
- a rolagem horizontal continua confinada ao wrapper local da tabela, sem voltar a empurrar ou cortar a pagina inteira
- implementei escolha de quantidade exibida por pagina na listagem, com opcoes `25`, `50`, `100` e `200`
- a escolha usa querystring `por_pagina` e, quando valida, tambem fica guardada na sessao para reutilizacao nas proximas aberturas da listagem
- a paginacao foi feita sobre `lancamentos_visuais`, depois do agrupamento visual de rateios, para evitar que um grupo rateado seja quebrado entre paginas por causa das linhas fisicas do banco
- validacao executada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - smoke renderizado com usuario autenticado em `/financeiro/lancamentos/`, `/financeiro/lancamentos/?por_pagina=25` e `/financeiro/lancamentos/?por_pagina=100&page=1&ordenacao=descricao`, todos com `200`

## Ajuste fino de data principal, contas e favorecido no financeiro

- ajustei a listagem principal de lancamentos para assumir `data_pagamento` como referencia principal: filtros de periodo, ordenacao visual e exportacao comum agora usam pagamento antes de competencia
- mantive `data_competencia` como coluna complementar na tabela, para preservar a informacao sem comandar a leitura principal
- restaurei a coluna `Conta destino` e renomeei a leitura da tabela para `Conta origem` e `Conta destino`, mantendo `conta_destino` visivel especialmente para transferencias
- troquei os rotulos visiveis de `Pessoa` para `Favorecido` no contexto financeiro, sem renomear model/campos internos: filtros e cabecalhos da listagem de lancamentos, formularios de lancamento/rateio, historico de ultimos lancamentos, cadastro exibido como `Favorecidos financeiros`, central de importacao/exportacao e rotulos/instrucoes das planilhas
- a correcao foi mantida cirurgica: slugs, permissoes e nomes tecnicos como `pessoa`, `pessoas` e `PessoaFinanceira` foram preservados para nao abrir migracao/refatoracao estrutural
- validacao executada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - smoke renderizado com usuario autenticado em `/financeiro/lancamentos/`, `/financeiro/lancamentos/novo/`, `/financeiro/pessoas/`, `/financeiro/pessoas/nova/` e `/financeiro/lancamentos/importacao-exportacao/`, todos com `200`
  - modelo XLSX comum conferido no contrato estrutural atual, mantendo os cabecalhos tecnicos `pessoa_nome`, `conta_nome` e `conta_destino_nome` para compatibilidade

## Correcoes de mes, datas e conta na exibicao de lancamentos

- corrigi a lista manual de meses em `financeiro/views.py`, trocando `marco` por `março` para a data documental do recibo
- em `financeiro/templates/financeiro/lancamento_list.html`, a coluna generica `Data` foi renomeada para `Data competencia`
- a listagem de lancamentos passou a exibir tambem a coluna `Data pagamento`, usando `-` quando nao houver valor
- a coluna independente `Conta destino` foi removida da tabela principal de lancamentos para evitar que a leitura de origem misture `conta` e `conta_destino`
- `conta_destino` segue preservada onde e regra de negocio real: transferencia, formulario, importacao/exportacao e calculos de extrato/saldo
- validacao executada:
  - `py manage.py check` OK
  - render autenticado de `/financeiro/lancamentos/` com `200`
  - render autenticado de recibo com `200`, sem `marco` sem cedilha e com `março`
  - render autenticado de `/financeiro/resumo/`, `/financeiro/prestacao-contas/`, `/financeiro/extratos/` e extrato por conta com `200`
- observacao de validacao:
  - uma tentativa inicial em `/financeiro/extrato/` retornou `404` porque a rota real do repositorio e `/financeiro/extratos/`; a validacao foi repetida na rota correta e passou

## Limpeza do recibo e retirada de acoes da area documental

- a tela `financeiro/templates/financeiro/lancamento_recibo.html` foi ajustada de forma cirurgica para manter o recibo como documento limpo
- saiu do corpo do recibo a frase `Para fins de comprovacao documental`
- os botoes `Imprimir` e `Voltar` deixaram de ficar dentro da area documental do recibo
- foi criada uma faixa de acoes externa ao documento, no nivel da pagina, com `Imprimir` e `Voltar`
- essa faixa externa usa `no-print`, entao nao aparece na impressao
- a area impressa fica restrita ao recibo em si, preservando identidade, dados do documento, mensagem e assinatura, sem controles visuais

## Diagnostico real do elemento que estourava a largura em `lancamento_list`

- a correcao anterior nao resolveu de forma suficiente porque usava `overflow-x: hidden` no shell principal
- isso mascarava o problema: a pagina deixava de crescer, mas o elemento largo continuava existindo
- nesta microetapa, o diagnostico foi feito em render real:
  - HTML autenticado gerado pelo proprio Django
  - medicao via Chrome headless em viewport desktop com sidebar expandida
- medi os seguintes pontos da cadeia:
  - shell principal
  - `main`
  - `container` interno
  - `header` da pagina
  - grid de filtros
  - barra de acoes em lote
  - wrapper da tabela
  - tabela
- achado objetivo:
  - `shellBody`, `main`, `sectionContainer`, `pageHeader`, `filtersGrid` e `bulkBar` ficaram dentro da largura util
  - o primeiro elemento efetivamente mais largo foi a propria `table` de `lancamento_list`
  - no render desktop medido:
    - `tableWrap` com cerca de `1033px`
    - `table` com cerca de `1375px`
    - `bodyWidth` igual ao `viewport`
  - isso confirmou que a largura excedente pode existir com seguranca desde que fique confinada ao wrapper local da tabela
- correcao final aplicada:
  - remocao de `overflow-x: hidden` do shell principal em `financeiro/base.html`
  - manutencao do scroll horizontal apenas nos wrappers locais das tabelas
- por que a correcao anterior nao resolveu:
  - ela escondia o overflow no shell, mas nao demonstrava se a origem estava corrigida
  - ao retirar o clipping e repetir a medicao real, ficou provado que o shell nao precisava esconder nada; o comportamento correto depende do wrapper local da tabela
- validacao concluida:
  - captura desktop real de `lancamento_list` com sidebar expandida
  - sem clipping do shell
  - pagina principal dentro da largura util
  - overflow restrito ao wrapper da tabela
  - smoke test autenticado `200` em:
    - `lancamento_list`
    - `conta_list`
    - `pessoa_list`
    - `categoria_list`
    - `centro_custo_list`
    - `lancamento_importacao_exportacao`
- conclusao objetiva:
  - a regressao ficou resolvida no ponto certo
  - o shell nao mascara mais o problema
  - a tabela larga rola no wrapper local, sem cortar a pagina inteira

## Correcao inicial da regressao de overflow horizontal com sidebar expandida

- depois da normalizacao do shell autenticado do `financeiro`, foi identificado corte da tela `lancamento_list` à direita quando a sidebar ficava expandida
- a causa tecnica encontrada nao foi de regra de negocio:
  - o shell principal ainda precisava reforcar contencao horizontal em `financeiro-app-shell-body`, `financeiro-app-main` e no `container` interno da `section`
  - as listagens principais estavam com wrappers de tabela em `overflow: visible`, deixando a tabela escapar do card e alargar a pagina inteira
- correcao aplicada:
  - em `financeiro/base.html`, reforcei `min-width: 0` e `overflow-x: hidden` no shell principal e no container de conteudo
  - padronizei `table-wrapper` para scroll horizontal interno
  - nas listagens `lancamento`, `conta`, `pessoa`, `categoria` e `centro de custo`, troquei os wrappers locais de tabela para `overflow-x: auto` / `overflow-y: hidden` com `width/max-width: 100%`
- telas validadas:
  - `lancamento_list`
  - `conta_list`
  - `pessoa_list`
  - `categoria_list`
  - `centro_custo_list`
  - `lancamento_importacao_exportacao`
- validacao executada:
  - `py manage.py check` OK
  - smoke test autenticado com `Client`: todas as telas do escopo responderam `200`
- observacao metodologica:
  - nao havia navegador/headless disponivel no ambiente para captura visual automatizada
  - a validacao desta microetapa ficou apoiada em inspecao estrutural do HTML/CSS e smoke test autenticado das telas afetadas
- conclusao objetiva:
  - a regressao visual ficou corrigida no nivel estrutural esperado
  - tabelas largas passam a rolar dentro do wrapper correto, sem empurrar a pagina inteira para a direita

## Validacao de carga real pequena no novo layout comum do financeiro

- foi executada uma carga real pequena e controlada usando a central de importacao do `financeiro`, sem abrir nova frente funcional
- o estado real encontrado antes da carga nao era mais `base totalmente vazia`:
  - `1` conta (`Conta Teste`)
  - `1` pessoa (`Pessoa Teste`)
  - `1` centro de custo (`Centro Teste`)
  - `5` categorias/subcategorias
  - `0` lancamentos
- para viabilizar uma transferencia real no lote pequeno, foi importada primeiro uma planilha auxiliar minima de `contas`, criando:
  - `Conta Destino 20260406_112727`
- em seguida, foi importado no layout comum um lote real pequeno contendo:
  - `1` lancamento simples de receita
  - `1` transferencia
  - `1` documento com rateio de `2` blocos
- arquivos usados:
  - `tmp/validacao_carga_real_pequena/contas_complementares_20260406_112727.xlsx`
  - `tmp/validacao_carga_real_pequena/lote_real_pequeno_20260406_112727.xlsx`
- validacao objetiva da importacao:
  - importacao auxiliar de conta: `200` e banner de sucesso
  - importacao de lancamentos: `200` e banner de sucesso
  - persistencia final:
    - `4` lancamentos
    - `1` grupo de rateio
    - `2` linhas rateadas
  - integridade:
    - transferencia com `conta` de origem e `conta_destino` corretas
    - rateio reconstruido em `2` linhas com categorias `Material` e `Servico`
- validacao das telas operacionais apos a carga:
  - listagem `200`
  - extrato `200`
  - resumo `200`
  - prestacao de contas `200`
  - recibo `200`
- checks de conteudo confirmados:
  - as tres descricoes do lote apareceram na listagem
  - as tres descricoes apareceram no extrato da conta de origem
  - `Doacoes`, `Material` e `Servico` apareceram no resumo e na prestacao
  - o recibo do lancamento simples trouxe `Pessoa Teste` e a descricao esperada
- validacao tecnica complementar:
  - `py manage.py check` OK depois da carga
- conclusao objetiva:
  - o contrato atual da planilha comum passou em carga real pequena
  - nao apareceu bug novo nem divergencia de contrato que bloqueie ampliacao da carga
  - o modulo esta pronto para avancar para lote real maior de forma controlada

## Auditoria das paginas autenticadas e normalizacao do shell superior/lateral

- foi executada auditoria transversal das paginas autenticadas relevantes de `financeiro`, `configuracoes` e `biblioteca`
- a origem tecnica da divergencia ficou objetiva:
  - o sistema tem dois shells autenticos legitimos (`financeiro/base.html` e `configuracoes/sistema_base.html`)
  - a divergencia real estava em `10` templates do `financeiro` que sobrescreviam `financeiro_shell_header`
  - esses overrides removiam a topbar contextual completa e deixavam apenas um topo minimo com toggle/menu
- padrao oficial adotado:
  - `financeiro`: shell completo com barra superior contextual + contexto institucional/usuario + navegacao lateral persistente
  - `configuracoes` e `biblioteca`: `sistema_base` com barra superior completa e navegacao local do modulo quando aplicavel
  - topo minimo com apenas toggle/menu deixa de ser padrao principal
- templates normalizados no `financeiro`:
  - `lancamento_list`
  - `lancamento_form`
  - `conta_list`
  - `conta_form`
  - `pessoa_list`
  - `pessoa_form`
  - `categoria_list`
  - `categoria_form`
  - `centro_custo_list`
  - `centro_custo_form`
- telas tambem auditadas no shell completo sem exigir refatoracao estrutural nova:
  - `lancamento_importacao_exportacao`
  - `resumo`
  - `prestacao_contas`
  - `auditoria_lancamento_list`
  - `configuracao_institucional_list`
  - telas autenticadas de `configuracoes`
  - telas autenticadas de `biblioteca`
- excecoes mantidas:
  - telas de autenticacao continuam fora do shell autenticado
  - telas de recibo/impressao podem continuar isolando o shell por necessidade documental
- validacao executada:
  - `py manage.py check` OK
  - smoke test autenticado com `Client`:
    - `financeiro`: listagens, formularios, central de importacao, relatorios, auditoria e institucional responderam `200` com topbar completa e sidebar
    - `configuracoes`: telas auditadas responderam `200` com `ce-app-topbar`
    - `biblioteca`: telas auditadas responderam `200` com `ce-app-topbar` e navegacao local
- conclusao objetiva:
  - a divergencia de shell autenticado foi eliminada no `financeiro`
  - o contrato visual do topo/lateral ficou formalmente consolidado

## Layout comum de importacao/exportacao de lancamentos com ate 5 rateios na mesma linha

- a decisao mais recente do usuario substituiu o contrato intermediario por multiplas linhas pelo modelo didatico:
  - `1 linha = 1 documento`
  - ate `5` blocos de rateio na mesma linha
  - `valor_total_documento = soma dos blocos preenchidos`
- o layout final da aba `Modelo` ficou:
  - campos gerais:
    - `tipo`
    - `status`
    - `descricao`
    - `valor_total_documento`
    - `data_competencia`
    - `data_pagamento`
    - `pessoa_nome`
    - `conta_nome`
    - `conta_destino_nome`
    - `numero_documento`
    - `observacoes`
  - blocos de rateio:
    - `categoria_nome_1`, `centro_custo_nome_1`, `valor_1`
    - `categoria_nome_2`, `centro_custo_nome_2`, `valor_2`
    - `categoria_nome_3`, `centro_custo_nome_3`, `valor_3`
    - `categoria_nome_4`, `centro_custo_nome_4`, `valor_4`
    - `categoria_nome_5`, `centro_custo_nome_5`, `valor_5`
- regra funcional final:
  - so bloco `1` preenchido = lancamento simples
  - bloco `2` ou mais preenchido = lancamento com rateio
  - `transferencia` continua sem suporte a rateio e usa todos os blocos em branco
- validacoes finais entregues:
  - maximo de `5` rateios por documento
  - sem buracos entre blocos
  - cada bloco usado exige subcategoria valida e valor positivo
  - categoria pai continua proibida
  - categoria precisa respeitar o tipo do lancamento
  - `valor_total_documento` precisa bater com a soma dos blocos
  - importacao continua `all-or-nothing`
- exportacao comum:
  - continua respeitando os filtros da listagem
  - agora gera `Modelo` + `Instrucoes` no mesmo contrato consumido pela importacao
  - cada grupo rateado sai condensado em uma unica linha
  - grupos com mais de `5` linhas rateadas sao bloqueados no fluxo comum com mensagem clara, mantendo o caminho tecnico como excecao
- importacao comum:
  - continua centralizada na tela geral do financeiro
  - continua conciliando apenas contra cadastros existentes
  - preserva compatibilidade com o layout simples legado de `13` colunas
  - deixa de usar como contrato principal o layout intermediario por multiplas linhas
- testes executados:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - smoke test transacional com rollback:
    - roundtrip comum de exportacao/importacao com `1` simples + `1` documento rateado de `2` blocos: OK
    - compatibilidade do layout simples legado: OK
    - transferencia no novo layout com blocos em branco: OK
    - arquivo invalido com buraco entre blocos: bloqueado com erro claro
    - arquivo invalido com soma divergente: bloqueado com erro claro
    - exportacao comum de grupo com `6` linhas rateadas: bloqueada com mensagem clara
- conclusao objetiva:
  - o fluxo comum de planilha do usuario agora cobre simples, transferencia simples e rateio no modelo de `1 linha por documento`
  - a trilha tecnica separada continua apenas como apoio para contingencia e para grupos fora do limite do fluxo comum

## Reset final do financeiro sem reconstrucao

- foi executado o reset final do `financeiro` com a intencao explicita de deixar o modulo vazio para uso/teste do zero
- o `dry-run` confirmou previamente o escopo esperado de limpeza:
  - `26` lancamentos
  - `1` regra automatica
  - `47` auditorias
  - `5` contas
  - `2` pessoas
  - `11` categorias/subcategorias
  - `2` centros de custo
- o reset real foi executado com:
  - `py manage.py reset_financeiro_controlado --executar --confirmar RESETAR_FINANCEIRO`
- nesta microetapa nao houve reconstrucao posterior por decisao operacional
- preservado fora do reset:
  - `1` assinatura institucional
  - `1` configuracao institucional
- zerado ao final:
  - `0` regras automaticas
  - `0` contas
  - `0` pessoas
  - `0` centros de custo
  - `0` categorias/subcategorias
  - `0` lancamentos simples
  - `0` grupos de rateio
  - `0` linhas rateadas
  - `0` lancamentos totais
- validacao final:
  - `py manage.py check` OK
- conclusao objetiva:
  - o `financeiro` ficou vazio de forma intencional e controlada
  - a base esta pronta para iniciar operacao/testes do zero

## Validacao operacional final da base reconstruida

- foi executada validacao operacional final do `financeiro` ja reconstruido, sem abrir nova frente funcional
- a validacao usou a base real reconstruida e cobriu a stack HTTP do Django com smoke tests de leitura, permissao, downloads e fluxos mutaveis com rollback local
- blocos validados com sucesso:
  - listagem de lancamentos
  - criacao de lancamento simples
  - edicao de lancamento simples
  - leitura do grupo rateado pela tela de edicao coordenada
  - importacao/exportacao nos pontos ja existentes
  - extrato
  - resumo
  - prestacao de contas
  - recibo
  - regras automaticas
  - permissoes principais
  - integridade visual minima das telas centrais
- checks objetivos desta microetapa:
  - `Gestao administrativa` acessa auditoria com `200`
  - `Operador financeiro` recebe `403` na auditoria
  - `Consulta/visualizacao` recebe `403` na central de importacao
  - `Consulta/visualizacao` exporta a listagem de lancamentos com `200`
  - listagem de lancamentos, novo lancamento, extrato, resumo, prestacao de contas e recibo abriram com `200`
  - criacao e edicao de lancamento simples por `Operador financeiro` passaram com `302`
  - sugestoes de regras automaticas responderam `200` e a criacao com `Salvar como regra automatica` foi validada com rollback
  - exportacao XLSX da listagem passou com `200`
  - download do modelo de lancamentos passou com `200`
  - download da planilha-base de `contas` passou com `200`
- falso positivo descartado nesta etapa:
  - a primeira tentativa de teste marcou falha na criacao do lancamento simples porque o smoke enviou `123,45` diretamente para `input type=\"number\"`
  - isso nao caracterizou bug real do modulo; com payload compativel com o campo HTML (`123.45`), o fluxo passou normalmente
  - tambem foram corrigidas rotas incorretas usadas pelo teste inicial, sem necessidade de patch no sistema
- conclusao objetiva:
  - nao apareceu bug funcional novo no `financeiro` reconstruido
  - nao foi necessario patch de codigo nesta microetapa
  - do ponto de vista tecnico e funcional, o modulo pode seguir para fechamento de commit

## Execucao real completa do reset e da reconstrucao

- a operacao real do `financeiro` foi executada sem rollback usando o pacote:
  - `tmp/operacao_reset_financeiro_20260406_081633/`
- antes do reset, foi confirmada a integridade do pacote com todos os arquivos esperados:
  - `rateios_backup_definitivo.json`
  - `regras_backup_definitivo.json`
  - `01_contas_financeiras_importacao.xlsx`
  - `02_pessoas_financeiras_importacao.xlsx`
  - `03_centros_custo_importacao.xlsx`
  - `04_categorias_importacao.xlsx`
  - `05_lancamentos_simples_importacao.xlsx`
  - `manifesto_pre_reset.json`
- o reset real foi executado com:
  - `py manage.py reset_financeiro_controlado --executar --confirmar RESETAR_FINANCEIRO`
- a reconstrucao real foi concluida em ordem:
  - `5` contas
  - `2` pessoas
  - `2` centros de custo
  - `11` categorias/subcategorias
  - `14` lancamentos simples
  - `1` regra automatica restaurada
  - `6` grupos de rateio restaurados
  - `12` linhas rateadas restauradas
- os restores tecnicos executados foram:
  - `py manage.py restaurar_regras_financeiro --arquivo "tmp/operacao_reset_financeiro_20260406_081633/regras_backup_definitivo.json" --executar --confirmar RESTAURAR_REGRAS_FINANCEIRO`
  - `py manage.py restaurar_rateios_financeiro --arquivo "tmp/operacao_reset_financeiro_20260406_081633/rateios_backup_definitivo.json" --executar --confirmar RESTAURAR_RATEIOS_FINANCEIRO`
- validacao final sem rollback:
  - `1` assinatura institucional preservada
  - `1` configuracao institucional preservada
  - `1` regra automatica restaurada
  - `5` contas
  - `2` pessoas
  - `2` centros de custo
  - `11` categorias/subcategorias
  - `14` lancamentos simples
  - `12` lancamentos rateados
  - `6` grupos de rateio
  - `0` simples com categoria-pai
  - `0` simples com tipo/categoria incompatíveis
  - `0` regras operacionais apontando para categoria-pai
- `py manage.py check` permaneceu OK depois da operacao real
- divergencia em relacao ao preflight:
  - nao houve divergencia funcional nem de contagem
  - ocorreu apenas um erro inicial de quoting na chamada do shell para os restores tecnicos, corrigido sem impacto na base
- conclusao objetiva:
  - o reset real foi executado com sucesso
  - a reconstrucao integral da base local do `financeiro` foi concluida com sucesso
  - o proximo passo deixa de ser reconstrucao tecnica e passa a ser validacao operacional final no navegador

## Fechamento do ultimo bloqueio do reset real

- o reset destrutivo real do `financeiro` ainda nao podia ser executado com reconstrucao integral porque o pacote operacional nao cobria `AssinaturaInstitucional`, `ConfiguracaoInstitucional` e `RegraLancamentoFinanceiro`
- mapeamento e decisao final por item:
  - `AssinaturaInstitucional`: preservada fora do reset
  - `ConfiguracaoInstitucional`: preservada fora do reset
  - `RegraLancamentoFinanceiro`: continua entrando no reset e passou a ganhar trilha tecnica propria de `backup/restauracao`
- justificativa tecnica:
  - `assinaturas` e `configuracao institucional` sao apoio documental do modulo e podem permanecer com seguranca sem comprometer o objetivo de limpar a base transacional
  - `regras automaticas` dependem de `contas`, `pessoas`, `categorias` e `centros de custo`; quando tentei preserva-las fora do reset, a exclusao falhou com `ProtectedError`
  - por isso, a menor solucao segura foi preservar os 2 itens documentais e criar uma trilha tecnica separada apenas para `regras`
- implementacao realizada:
  - ajuste de `financeiro/management/commands/reset_financeiro_controlado.py`
  - criacao de `financeiro/regras_backup.py`
  - criacao de `financeiro/management/commands/backup_regras_financeiro.py`
  - criacao de `financeiro/management/commands/restaurar_regras_financeiro.py`
- regra final consolidada do reset:
  - preserva `AssinaturaInstitucional`
  - preserva `ConfiguracaoInstitucional`
  - apaga `RegraLancamentoFinanceiro` junto com o restante dos dados transacionais do `financeiro`
- o backup tecnico das regras usa `JSON` no formato `financeiro.regras.backup.v1`, com referencias por chave de negocio estavel:
  - conta por `nome`
  - pessoa por `codigo`
  - centro de custo por `codigo`
  - categoria por `tipo`, `nome` e `categoria_pai_nome`
- o pacote operacional de reconstrucao passou a incluir:
  - `tmp/operacao_reset_financeiro_20260406_081633/regras_backup_definitivo.json`
- validacao executada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `py manage.py reset_financeiro_controlado` OK em simulacao, refletindo o novo escopo
  - `py manage.py backup_regras_financeiro --saida tmp/operacao_reset_financeiro_20260406_081633/regras_backup_definitivo.json` OK
  - `py manage.py restaurar_regras_financeiro --arquivo tmp/operacao_reset_financeiro_20260406_081633/regras_backup_definitivo.json` OK em simulacao
  - roundtrip operacional completo com rollback:
    - reset dentro de transacao de teste
    - `assinaturas` e `configuracao institucional` preservadas
    - `regras` apagadas pelo reset
    - reconstrucao do pacote + restore de `rateios` + restore de `regras` concluida com sucesso
    - contagem final recomposta:
      - `1` assinatura institucional
      - `1` configuracao institucional
      - `1` regra automatica
      - `5` contas
      - `2` pessoas
      - `2` centros de custo
      - `11` categorias/subcategorias
      - `14` lancamentos simples
      - `12` linhas rateadas
      - `6` grupos de rateio
- conclusao objetiva:
  - o ultimo bloqueio conhecido do reset real foi superado
  - o reset real fica tecnicamente liberado do ponto de vista de preservacao/reconstrucao integral
  - o reset destrutivo real ainda nao foi executado nesta microetapa

## Saneamento dos 5 lancamentos simples bloqueadores

- a tentativa anterior de preparar o reset real revelou que o bloqueio ja nao estava mais nos `rateios`, e sim em `5` lancamentos simples legados fora do contrato atual da importacao comum
- os casos bloqueadores eram:
  - `pk=1` e `pk=4`: despesas usando `Cantina` como categoria pai
  - `pk=2` e `pk=12`: despesas usando `Estrutura` como categoria pai
  - `pk=23`: lancamento do tipo `despesa` usando `Doacao`, subcategoria de `receita`
- a decisao desta microetapa foi preservar o contrato atual da importacao comum e sanear a base real, em vez de afrouxar validacao
- correcoes aplicadas:
  - criacao de `Operacao Cantina` como subcategoria de `Cantina`
  - migracao dos lancamentos `pk=1` e `pk=4` para `Operacao Cantina`
  - criacao de `Operacao Estrutura` como subcategoria de `Estrutura`
  - migracao dos lancamentos `pk=2` e `pk=12` para `Operacao Estrutura`
  - alteracao do lancamento `pk=23` de `despesa` para `receita`, preservando `Doacao`
  - alteracao da `RegraLancamentoFinanceiro pk=3` para `receita` com `Doacao`, evitando reintroduzir o legado invalido por reutilizacao da regra
- depois do saneamento, foi gerado um novo pacote de reconstrucao em:
  - `tmp/operacao_reset_financeiro_20260406_081633/`
- o novo preflight completo com rollback foi executado com sucesso:
  - importacao valida de `contas`
  - importacao valida de `pessoas`
  - importacao valida de `centros de custo`
  - importacao valida de `categorias/subcategorias`
  - importacao valida de `14` lancamentos simples
  - restauracao tecnica valida de `6` grupos de `rateio`
  - restauracao tecnica valida de `12` linhas rateadas
- consolidacao objetiva:
  - o bloqueio dos `5` lancamentos simples foi resolvido
  - o reset destrutivo real passa a ficar liberado tecnicamente do ponto de vista da reconstrucao completa
  - o reset real ainda nao foi executado nesta microetapa
- a frente futura de evolucao do layout comum de importacao/exportacao com suporte a `rateio` em planilha permanece apenas registrada e nao foi implementada agora

## Tentativa operacional real de backup/reset/reconstrucao

- a microetapa saiu do plano e entrou em execucao operacional controlada, mas o reset destrutivo real acabou **nao** sendo disparado por seguranca
- primeiro foi gerado o pacote definitivo de reconstrucao em:
  - `tmp/operacao_reset_financeiro_20260406_074817/`
- arquivos gerados:
  - `rateios_backup_definitivo.json`
  - `01_contas_financeiras_importacao.xlsx`
  - `02_pessoas_financeiras_importacao.xlsx`
  - `03_centros_custo_importacao.xlsx`
  - `04_categorias_importacao.xlsx`
  - `05_lancamentos_simples_importacao.xlsx`
  - `manifesto_pre_reset.json`
- com esse pacote pronto, foi executado um preflight real com rollback:
  - reset do dominio `financeiro` apenas dentro de transacao de teste
  - reimportacao valida dos cadastros auxiliares
  - tentativa de reimportacao dos lancamentos simples pela importacao comum
  - rollback ao final para nao alterar a base local definitiva
- resultado do preflight:
  - `contas`: OK
  - `pessoas`: OK
  - `centros de custo`: OK
  - `categorias/subcategorias`: OK
  - `lancamentos simples`: BLOQUEADO
- numerica do bloqueio:
  - `14` lancamentos simples avaliados
  - `9` linhas validas
  - `5` linhas invalidas
- erros concretos encontrados:
  - linhas `2` e `15`: `Cantina` usada em despesa, mas hoje esta no cadastro como `Categoria` pai
  - linhas `3` e `12`: `Estrutura` usada em despesa, mas hoje esta no cadastro como `Categoria` pai
  - linha `13`: `Doacao` usada em `despesa`, apesar de pertencer ao tipo `receita`
- conclusao operacional:
  - o bloqueio dos `rateios` segue resolvido pela trilha tecnica separada
  - mas o reset real continua bloqueado por um novo ponto: legados de `lancamentos simples` fora do contrato atual da importacao comum
  - por isso, o reset destrutivo real nao foi executado nesta microetapa
- frente futura que precisou ficar registrada agora para nao sair do radar:
  - exportacao comum de lancamentos com suporte a rateio por grupo em planilha
  - importacao comum de lancamentos com suporte a reconstrucao de rateio por grupo
- essa evolucao futura foi apenas registrada; nao foi implementada nesta microetapa

## Estrategia tecnica minima para backup/restauracao de rateios

- o reset destrutivo real do `financeiro` nao podia seguir com seguranca porque a base local atual possui lancamentos rateados e grupos de rateio que nao sao recompostos pela importacao comum de lancamentos
- o bloqueio identificado foi objetivo:
  - `12` lancamentos rateados ativos na base
  - `6` grupos de rateio
  - a importacao funcional comum nao serializa nem restaura `grupo_rateio` como documento agrupado
- a decisao tecnica desta microetapa foi manter o fluxo comum do usuario intacto e criar uma trilha tecnica especifica, menor e reversivel:
  - `financeiro/rateio_backup.py`
  - `financeiro/management/commands/backup_rateios_financeiro.py`
  - `financeiro/management/commands/restaurar_rateios_financeiro.py`
- por que essa estrategia foi escolhida:
  - ela nao reabre a frente de evolucao da importacao comum de lancamentos
  - ela separa claramente o fluxo funcional do usuario do fluxo tecnico de contingencia/reconstrucao
  - ela usa chaves de negocio estaveis dos cadastros auxiliares, evitando dependencia de `pk` apos reset
  - ela permite restauracao `all-or-nothing` e transacional
- formato adotado:
  - `JSON` tecnico no formato `financeiro.rateio.backup.v1`
  - cada grupo exporta:
    - `grupo_rateio`
    - `numero_documento`
    - `total_linhas`
    - `valor_total`
    - lista `linhas`
  - cada linha exporta:
    - `descricao`, `tipo`, `status`, `valor`
    - `data_competencia`, `data_pagamento`
    - `numero_documento`, `observacoes`
    - `conta`
    - `conta_destino`
    - `pessoa`
    - `categoria`
    - `centro_custo`
  - referencias sao serializadas por chave de negocio:
    - conta: `nome`
    - pessoa: `codigo`
    - centro de custo: `codigo`
    - categoria: `tipo`, `nome`, `categoria_pai_nome`
- endurecimento do restore:
  - `dry-run` por padrao
  - execucao real apenas com `--executar --confirmar RESTAURAR_RATEIOS_FINANCEIRO`
  - falha se os cadastros auxiliares ainda nao tiverem sido recompostos
  - falha se houver conflito de `numero_documento` fora do grupo
  - gravacao transacional e novas auditorias tecnicas `create` para rastreabilidade minima da restauracao
- validacao executada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `py manage.py backup_rateios_financeiro --saida tmp/rateios_validacao.json` OK
  - `py manage.py restaurar_rateios_financeiro --arquivo tmp/rateios_validacao.json` OK em simulacao
  - roundtrip controlado, com rollback, em subconjunto de `2` grupos:
    - `roundtrip_idem=True`
    - `2` grupos restaurados
    - `4` linhas restauradas
    - `3` linhas legadas restauradas
    - `4` auditorias tecnicas de criacao geradas no teste
- residuos legados encontrados e tratados no caminho tecnico:
  - linhas antigas com `categoria pai` em rateio, hoje invalidas no fluxo funcional comum
  - `2` grupos legados com apenas `1` linha
  - o restore tecnico passou a reconstituir esses casos so no caminho de backup/restauracao, sem liberar essa flexibilidade para cadastro/importacao funcional do usuario
- conclusao desta microetapa:
  - o bloqueio tecnico que impedia reset futuro por falta de reconstrucao fiel de rateio foi superado
  - a importacao comum continua sem recompôr grupos de rateio e isso segue sendo verdadeiro
  - o reset destrutivo real ainda nao foi executado nesta etapa

## Validacao controlada dos fluxos auxiliares antes do reset real

- foi executado smoke test funcional controlado dos 4 fluxos auxiliares de importacao do `financeiro`:
  - `contas`
  - `pessoas`
  - `centros de custo`
  - `categorias/subcategorias`
- por limitacao deste ambiente, a validacao pratica foi feita pelo fluxo HTTP do proprio Django com `Client`, em vez de clique humano direto num navegador automatizado; ainda assim, o teste cobriu a mesma stack de permissao, view, upload, mensagem, transacao e auditoria
- o roteiro confirmou:
  - caso de sucesso para os 4 fluxos
  - caso invalido para os 4 fluxos
  - mensagens coerentes de sucesso e erro
  - `all-or-nothing` por arquivo
  - enforcement de permissao na tela central e nos endpoints auxiliares
  - geracao de auditoria `create`
  - dependencia correta entre categoria pai e subcategoria
- resultados consolidados:
  - `Operador financeiro`: `200` na central e sucesso nos 4 uploads
  - `Consulta/visualizacao`: `403` na central
  - perfil temporario com `financeiro.lancamentos.importar` + `financeiro.lancamentos.baixar_modelo`, mas sem permissao de criar `contas`: `200` na central sem renderizar formulario auxiliar de contas, `403` no download direto da planilha-base de contas e `403` no POST direto de importacao de contas
  - em cada fluxo valido: `2` registros importados + `2` auditorias `create`
  - em cada fluxo invalido: `0` registros importados + `0` auditorias novas, confirmando gravacao transacional por arquivo
  - em `categorias/subcategorias`: subcategoria importada ficou vinculada corretamente a categoria pai, e o erro de dependencia `Categoria pai nao encontrada...` bloqueou integralmente o arquivo invalido
- bug real encontrado durante a validacao:
  - a planilha-base auxiliar era gerada com a aba `Instrucoes`
  - a validacao estrutural exigia apenas `Instruções`
  - resultado: o proprio arquivo baixado pelo sistema falhava ao ser reenviado
- correcao aplicada:
  - `financeiro/views.py` passou a compatibilizar a leitura estrutural do XLSX auxiliar com a aba `Instrucoes`, sem reabrir regra de negocio nem alterar o layout funcional da tela
- validacao tecnica apos a correcao:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK

## Ajuste de escopo das planilhas-base e importacao auxiliar real

- a decisao de produto consolidada nesta microetapa foi:
  - importacoes auxiliares ficam centralizadas no financeiro geral
  - exportacoes permanecem nas telas/listagens especificas para obedecer aos filtros
  - `assinaturas` ficam fora desta frente
- por isso, a entrega anterior de planilhas-base foi ajustada de forma cirurgica:
  - `assinaturas institucionais` sairam da central de planilhas-base/importacoes auxiliares
  - a central permaneceu com `contas`, `pessoas`, `centros de custo` e `categorias/subcategorias`
- a tela central foi elevada de contrato documental para fluxo funcional real:
  - continua importando lancamentos
  - continua oferecendo download das planilhas-base
  - agora tambem importa de fato `contas`
  - agora tambem importa de fato `pessoas`
  - agora tambem importa de fato `centros de custo`
  - agora tambem importa de fato `categorias/subcategorias`
- regras finais implementadas:
  - importacao auxiliar centralizada numa unica tela do `financeiro`
  - exportacao mantida nas listagens especificas, sem mover esse fluxo para a central
  - validacao estrutural de abas/cabecalhos antes da leitura
  - validacao de conteudo linha a linha com rotulos amigaveis
  - gravacao all-or-nothing por arquivo
  - sem importacao parcial nesta etapa
  - sem importacao de assinaturas nesta frente
  - sem reset destrutivo real nesta etapa
- layouts efetivamente suportados pela importacao auxiliar real:
  - contas: `nome`, `descricao`, `saldo_inicial`, `data_saldo_inicial`, `ativa`
  - pessoas: `codigo`, `nome`, `tipo_pessoa`, `documento`, `telefone`, `email`, `observacoes`, `ativo`
  - centros de custo: `codigo`, `nome`, `ativo`
  - categorias/subcategorias: `nome`, `tipo`, `categoria_pai_nome`, `mensagem_recibo`, `ativo`
- a ordem operacional consolidada ficou:
  - contas
  - pessoas
  - centros de custo
  - categorias pai e depois subcategorias
  - lancamentos
- a importacao auxiliar passou a respeitar tambem a governanca de permissao do cadastro alvo:
  - a tela continua exigindo `financeiro.lancamentos.importar`
  - cada importacao auxiliar tambem exige a permissao de criacao do respectivo cadastro
- validacao tecnica executada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
- tentativa adicional de smoke test transacional por script foi bloqueada pelo ambiente local ao chamar `manage.py shell`, com `Acesso negado`; por isso, a validacao manual no navegador continua sendo a proxima checagem recomendada antes do reset real

## Planilhas-base reutilizaveis dos cadastros auxiliares do financeiro

- foi implementada a geracao/download de modelos XLSX reutilizaveis para apoiar a reconstruicao controlada da base local do `financeiro` apos o reset
- a entrega foi mantida no escopo exato desta microetapa: fechar o contrato dos layouts-base, sem tratar isso como importacao auxiliar pronta
- os modelos disponibilizados pelo sistema cobrem:
  - contas
  - pessoas
  - centros de custo
  - categorias/subcategorias
  - assinaturas institucionais
- a exposicao foi feita na tela ja existente `Importacao de Lancamentos`, por meio de uma secao explicita de `Planilhas-base dos cadastros auxiliares`, evitando abrir uma nova frente de UI
- foi criada tambem a rota tecnica de download por slug para cada modelo, reaproveitando o mesmo gerador XLSX do modulo e mantendo padrao de arquivo com duas abas:
  - `Modelo`
  - `Instrucoes`
- colunas finais de cada layout:
  - contas: `nome`, `descricao`, `saldo_inicial`, `data_saldo_inicial`, `ativa`
  - pessoas: `codigo`, `nome`, `tipo_pessoa`, `documento`, `telefone`, `email`, `observacoes`, `ativo`
  - centros de custo: `codigo`, `nome`, `ativo`
  - categorias/subcategorias: `nome`, `tipo`, `categoria_pai_nome`, `mensagem_recibo`, `ativo`
  - assinaturas: `nome`, `assinatura_texto`, `nome_exibicao`, `cargo`, `ativo`, `padrao`
- a ordem recomendada de reconstrucao da base foi deixada explicita na propria tela:
  - contas
  - pessoas
  - centros de custo
  - categorias pai e depois subcategorias
  - assinaturas
  - por ultimo, lancamentos
- a decisao de incluir `AssinaturaInstitucional` nesta etapa foi mantida porque o reset controlado tambem apaga esse cadastro e ele participa do uso documental real do modulo
- esta microetapa nao implementou:
  - importacao auxiliar dos cadastros
  - validacao de arquivo para esses novos layouts
  - criacao automatica de registros a partir das planilhas-base
  - logo local
  - execucao do reset destrutivo

## Reset controlado do financeiro

- foi implementado o comando tecnico dedicado `reset_financeiro_controlado` em `financeiro/management/commands/reset_financeiro_controlado.py`
- a intencao do nome foi mantida explicita para evitar ambiguidade com reset global do sistema ou com limpeza silenciosa de banco
- a regra final adotada nesta microetapa foi:
  - apagar apenas dados do dominio `financeiro`
  - preservar usuarios, autenticacao, perfis/permissoes, `SiteConfig`, configuracoes sistemicas e modulos fora do `financeiro`
- o escopo real de exclusao implementado ficou:
  - `LancamentoFinanceiro`
  - `RegraLancamentoFinanceiro`
  - `AuditoriaFinanceiro`
  - `ContaFinanceira`
  - `PessoaFinanceira`
  - `CategoriaFinanceira` e subcategorias
  - `CentroCusto`
  - `AssinaturaInstitucional`
  - `ConfiguracaoInstitucional`
- o comando foi endurecido contra uso acidental:
  - sem flags, roda apenas em `dry-run`
  - mostra de forma objetiva o que sera apagado e o que sera preservado
  - a execucao real exige `--executar`
  - a execucao real tambem exige confirmacao textual explicita com `--confirmar RESETAR_FINANCEIRO`
- a ordem de exclusao foi fechada de forma conservadora para evitar conflitos com `PROTECT`: regras/auditoria antes, lancamentos antes dos cadastros auxiliares, subcategorias antes de categorias pai
- validacao pratica minima executada:
  - `py manage.py check` OK
  - `py manage.py reset_financeiro_controlado` OK em modo simulacao
- por seguranca operacional, a execucao real destrutiva nao foi disparada nesta validacao automatizada, preservando a base local existente ate uso consciente do comando pelo operador

## Auditoria de fechamento do modulo financeiro para homologacao/hospedagem

- a mudanca de foco desta etapa foi pausar a expansao estrutural do sistema e tratar o `financeiro` como frente prioritaria de fechamento para homologacao e teste em hospedagem
- a auditoria cruzou o estado formal dos docs-base com o estado real do codigo em `financeiro`, `configuracoes` e `casa_espirita/settings.py`
- no dominio do `financeiro`, a leitura do repositorio confirmou cobertura consolidada para:
  - lancamentos, clone e rateio
  - contas, pessoas, categorias/subcategorias e centros de custo
  - assinaturas e configuracoes institucionais
  - extrato, resumo, prestacao de contas e auditoria
  - importacao/exportacao, acoes em lote e enforcement backend/visual por permissao
- nao foi identificado bloqueante funcional novo diretamente no modulo `financeiro`; o principal conjunto de pendencias para homologacao estava na configuracao de deploy
- ajustes tecnicos implementados nesta microetapa, por baixo risco e aderencia direta a hospedagem:
  - `casa_espirita/settings.py` passou a exigir `DJANGO_SECRET_KEY` quando `DEBUG` estiver desligado
  - `DJANGO_ALLOWED_HOSTS` passou a ser obrigatorio com `DEBUG` desligado
  - `CSRF_TRUSTED_ORIGINS` passou a ser lido de variavel de ambiente
  - `STATIC_ROOT` foi definido para preparar `collectstatic`
  - cookies seguros e chaves de proxy/redirect SSL passaram a ter configuracao por ambiente
- pendencias que permaneceram apenas registradas, sem implementacao precipitada:
  - SMTP real para reset de senha em hospedagem
  - decisao final sobre banco no provedor, porque o projeto segue em `sqlite3`
  - execucao real de `migrate`/`collectstatic` no ambiente de hospedagem
  - paginas de erro customizadas de producao como refinamento posterior
- backlog externo apenas registrado:
  - `eventos` fica explicitamente pausado
  - qualquer refinamento em `biblioteca` ou outros modulos so deve voltar depois do fechamento operacional do `financeiro`
- validacao tecnica executada:
  - `py manage.py check` OK
  - comandos como `showmigrations`, `collectstatic --dry-run` e algumas chamadas `manage.py shell -c` seguiram bloqueados por `Acesso negado` neste ambiente local, entao a validacao final de hospedagem continua dependente do provedor real

## Pacote pratico de deploy/homologacao

- foi criado `docs/GUIA_HOSPEDAGEM_FINANCEIRO.md` para concentrar:
  - variaveis de ambiente necessarias
  - sequencia recomendada de deploy
  - comandos de `migrate`, `collectstatic`, `check` e `check --deploy`
  - checklist pos-subida
  - pendencias que continuam dependentes do provedor
- foi criado `.env.example` com placeholders seguros, sem segredos reais, para apoiar a configuracao do host
- `requirements.txt` passou a incluir `gunicorn` e `whitenoise`, alinhando o projeto a uma subida WSGI simples com servico de estaticos no proprio app
- `casa_espirita/settings.py` recebeu ajustes pequenos e diretos para hospedagem:
  - `WhiteNoiseMiddleware`
  - `STATICFILES_STORAGE` com `CompressedManifestStaticFilesStorage`
  - `STATIC_URL` e `MEDIA_URL` normalizados com barra inicial
  - `DJANGO_DB_PATH` para permitir SQLite em caminho persistente do host
  - `DJANGO_MEDIA_ROOT` para media persistente
  - configuracao de HSTS por ambiente
- `.gitignore` passou a ignorar `.env`, preservando o modelo versionado apenas em `.env.example`
- validacao tecnica desta microetapa:
  - `py manage.py check` OK
  - `py manage.py check --deploy` executado primeiro com variaveis minimas e depois com simulacao mais proxima de producao
  - na simulacao mais proxima de producao, os avisos remanescentes ficaram apenas em:
    - `SECURE_HSTS_INCLUDE_SUBDOMAINS`
    - `SECURE_HSTS_PRELOAD`
  - esses dois itens ficaram documentados como recomendados para o host, e nao como bloqueio imediato da homologacao

## Esqueleto inicial do modulo eventos

- foi criado o app `eventos` como nova prova estrutural de modulo aderente ao shell compartilhado, ao portal `/inicio/` e a base central de permissoes
- `casa_espirita/settings.py` passou a registrar o app no `INSTALLED_APPS`, e `casa_espirita/urls.py` passou a expor a entrada canonica `/eventos/`
- o modulo ganhou `eventos/views.py`, `eventos/urls.py`, `eventos/permissoes.py` e templates proprios minimos (`eventos/base.html` e `eventos/home.html`)
- a landing `/eventos/` ficou protegida por `eventos.eventos.visualizar`, reutilizando a mesma estrategia de enforcement backend dos modulos ja existentes
- `configuracoes/permissoes.py` passou a incluir `Eventos` no catalogo de modulos do portal, apontando para `eventos:home`
- a migration `configuracoes/migrations/0009_permissoes_iniciais_eventos.py` passou a semear as permissoes:
  - `eventos.eventos.visualizar`
  - `eventos.eventos.listar`
  - `eventos.eventos.criar`
- vinculacao inicial por perfil:
  - `Administrador geral`: acesso completo inicial do modulo
  - `Gestao administrativa`: acesso completo inicial do modulo
  - `Consulta/visualizacao`: acesso de leitura (`visualizar` e `listar`)
- `Operador financeiro` e `Operador biblioteca` ficaram sem acesso inicial ao modulo porque `eventos` ainda nao possui dominio operacional fechado; isso evita expandir escopo funcional por analogia indevida com modulos ja maduros
- a landing inicial foi mantida propositalmente rasa: titulo do modulo, descricao breve de implantacao, indicacao visual de que o modulo esta em fase inicial e atalho de retorno ao portal, sem CRUD, sem agenda, sem inscricoes e sem estruturas profundas de negocio

## Regularizacao do dado institucional do SiteConfig

- a auditoria do repositorio e das migrations confirmou que `Lar de Teste` nao vinha de seed, fixture ou migration ativa do projeto; o valor estava salvo apenas no registro atual do banco local
- o model `SiteConfig` ja tinha default estrutural proprio e as telas de login/shell ja liam o nome institucional dinamicamente; a correcao necessaria era de dado persistido e de endurecimento do default/fallback oficial do projeto
- foi criada a migration `configuracoes/migrations/0008_regularizar_nome_institucional_siteconfig.py` com duas acoes:
  - alterar o default de `SiteConfig.site_name` para `Casa Espírita Caminheiros da Luz`
  - atualizar o banco apenas quando `site_name` estiver exatamente como `Lar de Teste`
- essa estrategia evita sobrescrever ambientes que ja tenham nome institucional real diferente do local atual
- `configuracoes/models.py` passou a centralizar a constante `SITE_NAME_PADRAO`
- `configuracoes/views.py`, `configuracoes/context_processors.py` e o titulo de `configuracoes/templates/configuracoes/siteconfig_detail.html` foram alinhados para usar o mesmo nome institucional oficial como fallback
- validacao prevista/execucao da etapa:
  - `py manage.py check`
  - `py manage.py migrate configuracoes`
  - confirmacao do `site_name` final como `Casa Espírita Caminheiros da Luz`
  - confirmacao de que login e shell continuam lendo `SiteConfig`, agora refletindo o nome institucional correto

## Entrega realizada

Foi executada a etapa incremental para impedir repeticao de `numero_documento` em lancamentos financeiros, sem alterar as regras ja aprovadas de transferencia, extrato, resumo ou prestacao de contas.

## Microetapa atual de leveza do shell lateral

- `financeiro/templates/financeiro/base.html` recebeu a primeira passada controlada de refinamento visual do shell lateral do `financeiro`
- a barra utilitaria desktop ficou menos carregada, com chip atual mais discreto e menor peso de borda/sombra
- o header interno da sidebar ficou mais leve
- grupos, links e `link-notes` ficaram menos pesados visualmente, com item ativo mais elegante
- a etapa permaneceu restrita a contraste, borda, sombra e espacamento
- nao houve alteracao de JS, drawer, rotas, `aria`, logica de expansao/colapso nem comportamento mobile/desktop

## Ajuste fino posterior do shell lateral

- o botao de recolher/expandir lateral no desktop foi refinado para ficar mais leve e mais coerente com o tema-base do modulo
- a hierarquia tipografica do menu foi aliviada
- grupos, titulos e links comuns perderam excesso de negrito
- o negrito forte ficou restrito ao item selecionado/ativo
- a etapa continuou sem alterar HTML estrutural relevante, JS, drawer, rotas, `aria` ou mecanica de expansao do menu

## Ajuste fino final desta rodada do shell lateral

- o toggle lateral do desktop perdeu contorno e destaque artificial
- o grupo expandido/ativo deixou de parecer uma caixa pesada e passou a usar presenca mais suave
- `Navegacao principal`, titulos de grupo e `link-notes` ficaram mais leves no conjunto
- o negrito forte continuou restrito ao item ativo
- a etapa permaneceu puramente visual, sem alterar logica, JS, drawer, rotas, `aria` ou comportamento mobile/desktop

## Consolidacao documental de importacao e exportacao de lancamentos

- foi registrada sem patch de codigo a frente futura de importacao em massa de lancamentos
- a importacao futura deve prever modelo de planilha/arquivo, validacao de colunas obrigatorias, validacao de tipos de dados, pre-visualizacao antes da confirmacao, comportamento para linhas invalidas, tratamento de duplicidades e preservacao das regras de negocio atuais
- foi registrada sem patch de codigo a frente futura de exportacao de consultas/listagens de lancamentos, respeitando filtros aplicados e priorizando formatos tabulares como CSV/Excel
- PDF ficou registrado apenas como possibilidade quando houver sentido documental
- ficou explicito que essa frente permanece como backlog futuro e nao deve ser misturada nesta microetapa com permissoes/acesso, regras reutilizaveis ou clonagem de lancamento

## Delimitacao documental do MVP de clonar lancamento

- foi registrado sem patch de codigo que a primeira implementacao dessa frente deve ser `clonar lancamento comum sem rateio`
- o MVP ficou definido como abertura de `lancamento_form.html` em modo criacao, pre-preenchido a partir do lancamento original e sem alterar o registro de origem
- os campos definidos como copiaveis nessa primeira versao foram `descricao`, `tipo`, `pessoa`, `categoria`, `centro_custo`, `conta`, `conta_destino` quando transferencia, e `observacoes`
- os campos explicitamente excluidos da copia foram `pk`, `numero_documento`, `data_competencia`, `data_pagamento`, `status`, auditoria, `grupo_rateio` e quaisquer identificadores capazes de gerar colisao ou confusao entre clone e edicao
- ficou registrado que lancamentos com rateio permanecem fora do MVP e que a acao de clone pode ficar indisponivel nesses casos ate haver desenho proprio de clonagem por grupo
- tambem ficou registrado o cuidado especifico com transferencia, para preservar `conta` e `conta_destino` sem reintroduzir campos que nao fazem parte desse tipo
- a microetapa foi exclusivamente documental e nao alterou templates, models, views, forms, rotas nem regras em producao

## Primeira implementacao minima de clonar lancamento comum

- foi criada uma rota/view dedicada para clonar lancamento comum sem rateio, reaproveitando `financeiro/templates/financeiro/lancamento_form.html` em modo de criacao e sem alterar o lancamento original
- a listagem principal de lancamentos passou a exibir a acao `Clonar` apenas quando o lancamento nao e rateado, mantendo lancamentos com `com_rateio` e `grupo_rateio` fora do MVP
- o pre-preenchimento do clone ficou restrito a `descricao`, `tipo`, `pessoa`, `categoria`, `centro_custo`, `conta`, `conta_destino` quando transferencia, e `observacoes`
- `pk`, `numero_documento`, `data_competencia`, `data_pagamento`, `status`, auditoria, `grupo_rateio` e `com_rateio` nao sao reaproveitados do lancamento original
- acessos diretos a clone de lancamento rateado sao bloqueados com aviso e retorno seguro a listagem principal
- esta microetapa nao abriu regras reutilizaveis, importacao/exportacao, permissoes nem clone por grupo de rateio

## Ajuste do clone comum como modelo editavel e registro da futura clonagem com rateio

- apos auditoria humana posterior, a regra de negocio do clone comum foi consolidada como copia sem vinculo com o original, apenas para acelerar o preenchimento de um novo lancamento
- a view dedicada de clone comum passou a preencher tambem `status`, `valor`, `data_competencia` e `data_pagamento`, mantendo `numero_documento`, `pk`, auditoria, `grupo_rateio` e `com_rateio` fora do clone
- a documentacao-base passou a registrar como fase futura a clonagem de lancamentos com rateio por grupo, tambem sem vinculo com o original e sem qualquer sincronizacao automatica entre clone e documento de origem
- nessa fase futura de rateio, se o `valor total do documento` for alterado no clone, as linhas/categorias deverao ser ajustadas manualmente pelo usuario antes de salvar
- esta microetapa nao implementou clone com rateio, regras reutilizaveis, importacao/exportacao, permissoes nem alteracao estrutural de models/forms

## Correcao cirurgica do preenchimento de datas e categoria no clone comum

- foi identificado que `data_competencia` e `data_pagamento` chegavam ao `form.initial`, mas o `DateInput(type=\"date\")` renderizava valores em `dd/mm/aaaa`, formato que o navegador nao preenche nesse tipo de campo
- `financeiro/forms.py` passou a normalizar esses dois campos para `%Y-%m-%d` em formularios nao vinculados, preservando o comportamento atual de create/edit e sem mexer na regra de negocio
- foi identificado tambem que a `categoria` do lancamento original podia ficar fora do queryset renderizado quando o registro antigo apontava para uma categoria que nao entra mais no conjunto padrao de subcategorias vinculaveis
- o queryset do campo `categoria` passou a reincluir a categoria inicial/da instancia quando necessario, para que o clone comum abra visualmente preenchido, mas a validacao do `clean()` continua bloqueando categorias pai ao salvar se o usuario nao ajustar

## Correcao do autocomplete parcial de categoria no formulario de lancamento

- foi identificado que `Pessoa`, `Conta` e `Centro de custo` ja usavam a mesma base de autocomplete com busca por `icontains`, mas o endpoint de `Categoria` quebrava ao aplicar `filter(categoria_pai__isnull=False)` depois que a classe base ja tinha fatiado o queryset
- a classe base `FinanceiroAutocompleteView` passou a montar o queryset sem slice antecipado e a aplicar o limite de resultados apenas no `get()`, permitindo que subclasses como `CategoriaFinanceiraAutocompleteView` filtrem antes da paginacao curta
- com isso, o campo `categoria` em `financeiro/templates/financeiro/lancamento_form.html` volta a usar busca/autopreenchimento por digitacao parcial com o mesmo comportamento dos demais campos, inclusive no fluxo de clone comum que reaproveita o mesmo formulario
- esta correcao nao alterou regras de negocio, validacoes, logica de rateio, permissÃµes, importacao/exportacao nem clone com rateio

## Primeira passada de alinhamento visual da listagem principal de lancamentos

- foi identificado que `financeiro/templates/financeiro/lancamento_list.html` ainda herdava o `financeiro_shell_header` padrao completo de `financeiro/base.html`, enquanto as listagens auxiliares mais recentes ja usavam override enxuto de topo, o que mantinha essa tela com sensacao de shell/layout antigo
- a tela passou a usar override local do `financeiro_shell_header` com o mesmo padrao enxuto aplicado em `categoria_list.html`, `conta_list.html` e `centro_custo_list.html`, preservando a sidebar como navegacao principal e mantendo o comportamento desktop/mobile do drawer
- filtros e tabela passaram a ficar reunidos em um unico card visual, reduzindo a sensacao de blocos soltos sem alterar filtros, acoes, rotas, clone comum nem logica de rateio
- o subtitulo explicativo do header, a legenda fixa da tabela e as notas longas de orientacao em lancamentos rateados foram removidos/aliviados para reduzir excesso de informacao, mantendo apenas um icone pequeno de ramificacao para rateio e a acao `Editar`
- esta microetapa nao alterou regras de negocio, validacoes, autocomplete de `categoria`, clone comum, permissoes nem importacao/exportacao

## Primeira implementacao minima de clonar grupo rateado

- foi criada rota/view dedicada por `grupo_rateio` para abrir `financeiro/templates/financeiro/lancamento_form.html` em modo criacao com um novo documento rateado pre-preenchido, sem alterar nem vincular o grupo original
- a listagem principal de lancamentos passou a exibir `Clonar` tambem em lancamentos com `com_rateio` e `grupo_rateio`, ao lado de `Editar`, usando apenas um icone pequeno de ramificacao para diferenciar rateio e sem mostrar o texto `Rateio` nem o hash tecnico do `grupo_rateio`
- entram no clone `descricao`, `tipo`, `status`, `data_competencia`, `data_pagamento`, `pessoa`, `centro_custo`, `conta`, `conta_destino` quando aplicavel, `observacoes`, `valor_total_documento` e as linhas de rateio com `categoria` e `valor`
- ficam fora `pk`, `numero_documento`, `grupo_rateio` original, IDs antigos das linhas, auditoria e qualquer identificador interno capaz de manter vinculo com o original
- grupos invalidos, vazios, com menos de 2 linhas ou com `numero_documento` divergente nao abrem clone e retornam com aviso para a listagem, preservando o documento de origem
- esta microetapa nao reutilizou a view/form de edicao de grupo, nao criou sincronizacao entre original e clone, nao mexeu em `forms.py`, nao abriu importacao/exportacao nem permissoes

## Delimitacao documental do MVP de regras reutilizaveis no lancamento

- foi registrado sem patch de codigo que o MVP inicial dessa frente deve usar `descricao` + `pessoa` como gatilho de sugestao de regra
- a aplicacao da sugestao deve acontecer apenas por acao explicita `Usar sugestao`, sem autoaplicacao silenciosa no formulario de lancamento
- os campos definidos como aplicaveis pela regra no MVP foram `descricao`, `tipo`, `pessoa`, `categoria`, `centro_custo`, `conta`, `conta_destino` e `observacoes`
- ficaram explicitamente fora do MVP `numero_documento`, datas, `status`, `valor`, rateio, auditoria e qualquer id interno
- `Salvar como regra` nao entra no primeiro patch e fica como fase seguinte, depois de validar o uso manual de `Usar sugestao`
- esta microetapa foi apenas documental e nao alterou models, forms, views, templates nem rotas

## Primeira implementacao minima de `Usar sugestao`

- foi criado o model `RegraLancamentoFinanceiro`, com estrutura minima para guardar `descricao`, `tipo`, `pessoa`, `categoria`, `centro_custo`, `conta`, `conta_destino`, `observacoes`, estado `ativa` e timestamps, sem incluir `numero_documento`, datas, `status`, `valor`, rateio ou vinculos internos do lancamento
- foi criada rota/view JSON dedicada para buscar sugestoes a partir de `descricao` + `pessoa`, retornando lista curta com `id`, `label`, `resumo` e payload dos campos que podem ser aplicados no formulario
- `financeiro/templates/financeiro/lancamento_form.html` passou a ter um bloco discreto e ocultavel de sugestoes, escondido por padrao e exibido apenas apos interacao do usuario quando `descricao` e `pessoa` estao preenchidos
- a aplicacao da sugestao acontece somente por botao `Usar sugestao`, preenche explicitamente os campos do MVP, dispara `change` nos selects para reaproveitar o JS atual e preserva os demais valores do formulario
- esta microetapa nao implementou `Salvar como regra`, nao misturou a frente com clone, rateio, importacao/exportacao ou permissoes, e nao exigiu alteracao em `financeiro/forms.py`

## Revisao documental da direcao de regras reutilizaveis e nova melhoria de UX

- foi registrada sem patch de codigo uma mudanca de direcao de negocio na frente de regras reutilizaveis: a sugestao deixa de depender obrigatoriamente de `descricao` + `pessoa` juntas e passa a ser pensada por campo gatilho individual, com `descricao` como primeiro gatilho a avaliar durante a digitacao
- `pessoa` permanece como possivel complemento/filtro futuro da sugestao, mas nao como dependencia rigida do MVP
- ao selecionar uma sugestao, o sistema deve continuar preenchendo automaticamente os campos da regra apenas como modelo revisavel, sem criar vinculo com lancamento anterior e sem alterar a regra quando o usuario editar o formulario depois
- foi registrada como direcao futura de UX a acao explicita `Salvar como regra` no proprio fluxo de cadastro de lancamento, em etapa posterior e separada da aplicacao de `Usar sugestao`
- tambem foi registrada como melhoria futura imediata a inclusao de `Clonar` na secao `Ultimos lancamentos da pessoa` de `financeiro/templates/financeiro/lancamento_form.html`, para reaproveitar um lancamento anterior direto da lista sem alterar o original e mantendo a mesma logica de clone ja aprovada
- esta microetapa foi exclusivamente documental e nao alterou templates, models, views, forms, migrations nem rotas

## Regularizacao operacional do MVP de regras automaticas de lancamento

- o endpoint de sugestoes de regras passou a usar `descricao` como gatilho principal por digitacao, sem depender obrigatoriamente de `pessoa`; quando `pessoa` e enviada, ela apenas refina a busca
- `financeiro/templates/financeiro/lancamento_form.html` deixou de usar o botao `Usar sugestao`; cada item de sugestao passou a funcionar como opcao clicavel e, ao ser selecionado, preenche automaticamente `descricao`, `tipo`, `pessoa`, `categoria`, `centro_custo`, `conta`, `conta_destino` e `observacoes`, sem submeter o formulario e sem bloquear edicao manual posterior
- `financeiro/forms.py` passou a expor o check `Salvar como regra automatica` apenas no formulario de criacao/clonagem em modo create e a neutralizar esse check quando `Lancamento com rateio` esta ativo
- `LancamentoFinanceiroCreateView` passou a persistir uma nova `RegraLancamentoFinanceiro` quando o check de regra automatica vem marcado em lancamento comum, sem reutilizar `numero_documento`, datas, `status`, `valor`, rateio, auditoria ou qualquer vinculo operacional com o lancamento salvo
- a melhoria futura de `Clonar` dentro de `Ultimos lancamentos da pessoa` nao entrou nesta etapa; a separacao entre regras automaticas e clone contextual permaneceu preservada
- a migration local `financeiro/migrations/0012_regralancamentofinanceiro.py` foi reaproveitada em lugar, sem necessidade de criar uma nova migration
- foi possivel executar `py manage.py check` com sucesso, validar `/financeiro/lancamentos/novo/` com status `200` e validar o endpoint `/financeiro/lancamentos/regras/sugestoes/?descricao=Teste` com status `200`

## Correcao cirurgica da UX final e do clique de autopreenchimento nas regras automaticas

- foi removido do corpo superior do formulario o card destacado de `Regra automatica`, que deixava o check visualmente mais pesado e fora da posicao desejada
- o check `Salvar como regra automatica` passou para a mesma linha da barra final de acoes, ao lado da regiao de salvar, com estilo mais discreto e secundario, mantendo disponibilidade apenas em create/clone e ocultacao no modo de rateio
- foi identificado como causa pratica do nao autopreenchimento um problema de timing na ativacao do item de sugestao por `click` puro, somado a selecao menos explicita da `option` nos campos geridos pelo autocomplete
- a selecao da sugestao passou a responder em `mousedown` com `preventDefault()`, espelhando a estrategia ja usada no autocomplete principal, e `setSelectValueFromSugestao()` passou a marcar a `option` como `selected` antes de emitir `change`
- com isso, a escolha da sugestao volta a preencher imediatamente `descricao`, `tipo`, `pessoa`, `categoria`, `centro_custo`, `conta`, `conta_destino` e `observacoes`, sem submeter o formulario automaticamente e preservando edicao manual posterior
- a frente futura de importacao/exportacao de lancamentos foi reforcada apenas em documentacao, incluindo a necessidade de acao para baixar planilha modelo no layout proprio do sistema e de respeitar a ordem/estrutura esperada de colunas

## Ajuste final do autocomplete de regras no proprio campo Descricao

- a lista separada com titulo `Sugestoes encontradas` foi removida de `financeiro/templates/financeiro/lancamento_form.html`
- o dropdown de sugestoes de regras passou a ficar acoplado diretamente ao campo `Descricao`, usando a mesma linguagem visual do autocomplete ja existente no formulario
- a selecao da sugestao no proprio campo continua acionando `applyRegraSugestao()` e preenchendo os demais campos da regra sem submeter o formulario automaticamente
- o check discreto `Salvar como regra automatica` permaneceu na barra final de acoes, ao lado de `Salvar`, e continua oculto no modo de rateio
- ficou registrada apenas em backlog, sem implementacao nesta etapa, a futura filtragem do campo `Categoria`/`Subcategoria` por `tipo`: ao escolher `despesa`, mostrar apenas opcoes de despesa; ao escolher `receita`, mostrar apenas opcoes de receita

## Bloqueio do autocomplete nativo do navegador no campo Descricao

- o `<form>` de `financeiro/templates/financeiro/lancamento_form.html` passou a declarar `autocomplete="off"`
- o widget `descricao` de `LancamentoFinanceiroForm` passou a renderizar `autocomplete="off"`, `autocorrect="off"`, `autocapitalize="none"` e `spellcheck="false"`
- o script da propria tela tambem reaplica esses atributos em `descricaoField` na inicializacao para manter o dropdown do sistema como unica sugestao visivel nesse campo
- a microcorrecao nao alterou regras de negocio, endpoint de sugestoes, persistencia de `RegraLancamentoFinanceiro`, clone, rateio nem validacoes ja consolidadas

## Acao Clonar nos ultimos lancamentos da pessoa

- a secao `Ultimos lancamentos da pessoa` de `financeiro/templates/financeiro/lancamento_form.html` passou a exibir uma acao textual discreta `Clonar` em cada linha elegivel do historico carregado para a pessoa selecionada
- `PessoaFinanceiraUltimosLancamentosView` passou a retornar `clone_url` no payload JSON de cada item, apontando para `financeiro:lancamento-clone` em lancamento comum sem rateio e para `financeiro:lancamento-rateio-clone` quando o item historico exibido pertence a um `grupo_rateio` valido
- o template reaproveita diretamente essas URLs ja existentes, sem duplicar regra de clone no JavaScript e sem alterar o formulario atual, o autocomplete de regras, o rateio, a transferencia ou a listagem principal

## Filtro de categoria/subcategoria por tipo do lancamento

- o queryset do campo `categoria` em `LancamentoFinanceiroForm` passou a considerar o `tipo` atual do lancamento, carregando apenas subcategorias de `receita` ou apenas subcategorias de `despesa` conforme o caso, sem reintroduzir categoria em `transferencia`
- o endpoint `CategoriaFinanceiraAutocompleteView` passou a aceitar o parametro opcional `tipo` e a filtrar as sugestoes de categoria pelo mesmo recorte quando o tipo e `receita` ou `despesa`
- o JS de `financeiro/templates/financeiro/lancamento_form.html` passou a enviar o `tipo` atual no autocomplete de `categoria`, limpar a categoria selecionada quando o tipo muda manualmente e filtrar tambem as opcoes das linhas de rateio conforme `receita` ou `despesa`
- na auditoria humana posterior, a causa exata da omissao de categorias validas foi identificada como o `limit = 10` herdado por `CategoriaFinanceiraAutocompleteView`, que fatiava a resposta final do endpoint mesmo quando o queryset do form ja continha mais subcategorias compativeis; essa view passou a usar um limite proprio amplo para nao truncar opcoes validas
- a microetapa preserva o fluxo de clone comum, clone rateado, regras automaticas, create comum e transferencia, sem abrir importacao/exportacao, pagina de ajuda ou refatoracao ampla do formulario

## Fase 1 da importacao/exportacao de lancamentos: planilha modelo

- foi criada a rota `lancamentos/importacao/modelo/` para baixar a planilha modelo da futura importacao de lancamentos; numa correcao posterior desta fase, o arquivo deixou de ser CSV com exemplos e passou a ser XLSX com duas abas: `Modelo` e `Instruções`
- foi criada uma pagina dedicada de `Importacao / Exportacao de Lancamentos`, acessivel a partir da listagem principal, organizando em um unico lugar upload preparado para fase futura, link para baixar modelo, acao visual de exportacao e um bloco de ajuda rapida sem expor regras internas
- a listagem de lancamentos deixou de exibir o download do modelo como acao solta e passou a oferecer a entrada `Importacao / Exportacao` no topo, sem alterar filtros, tabela, clone, recibo, rateio ou regras automaticas
- o layout oficial inicial do modelo foi definido com as colunas `tipo`, `status`, `descricao`, `valor`, `data_competencia`, `data_pagamento`, `pessoa_nome`, `categoria_nome`, `centro_custo_nome`, `conta_nome`, `conta_destino_nome`, `numero_documento` e `observacoes`
- a aba `Modelo` passa a conter apenas a linha de cabecalhos oficiais, sem linhas de exemplo, e a aba `Instruções` concentra orientacoes operacionais curtas sobre finalidade, preservacao dos cabecalhos, uma linha por lancamento, formato de datas/valores, campos que podem ficar em branco e uso de `conta_destino_nome` em transferencias
- esta fase segue sem implementar upload/importacao de arquivo do usuario, pre-validacao em massa, tratamento de duplicidades ou exportacao completa

## Primeira exportacao real de lancamentos em XLSX

- foi criada a rota `lancamentos/exportacao/` para baixar uma planilha XLSX real com os lancamentos cadastrados e, em ajuste posterior desta mesma frente, essa exportacao passou a operar a partir da propria tela de listagem de lancamentos
- a exportacao usa uma aba `Lancamentos` com cabecalhos amigaveis ao usuario na mesma ordem do modelo de importacao: `Tipo`, `Status`, `Descricao`, `Valor`, `Data de competencia`, `Data de pagamento`, `Pessoa`, `Categoria`, `Centro de custo`, `Conta`, `Conta de destino`, `Documento` e `Observacoes`
- `LancamentoFinanceiroListView` passou a montar a URL de exportacao preservando a querystring ativa, e `LancamentoFinanceiroExportacaoView` passou a reaproveitar a mesma funcao de filtro da listagem para gerar exatamente o subconjunto filtrado
- numa passada final desta frente, a exportacao operacional passou a serializar datas em `dd/mm/aaaa` e valores com virgula decimal, mantendo os cabecalhos amigaveis e sem alterar a planilha modelo tecnica da importacao
- a pagina dedicada foi ajustada para ficar visualmente focada em importacao futura e download do modelo; a exportacao principal permanece na listagem de `Lancamentos`, e a pagina dedicada passou a evitar um bloco concorrente de exportacao
- nesta mesma passada, rotulos visiveis dessa frente foram revisados para corrigir acentuacao e nomenclatura na listagem e na pagina dedicada de importacao
- esta primeira versao permanece simples e nao abre novos filtros avancados, multiplas variacoes de layout, importacao real do arquivo enviado nem validacao em massa

## Fase 1 da importacao de lancamentos: validacao estrutural do XLSX

- a pagina de `Importacao` passou a aceitar envio de arquivo XLSX e a acao principal do card foi ajustada para `Validar planilha`
- a validacao estrutural confere se o arquivo enviado tem extensao `.xlsx`, se pode ser lido como XLSX, se contem as abas `Modelo` e `Instruções` e se a primeira linha da aba `Modelo` bate exatamente com os cabecalhos oficiais esperados
- quando a estrutura esta incorreta, o sistema retorna mensagens claras de erro sem gravar lancamentos; quando a estrutura esta correta, o sistema retorna mensagem de sucesso informando explicitamente que nenhum lancamento foi importado nesta fase
- ficou registrado como direcao futura da primeira importacao real que o processamento deve depender apenas de cadastros ja existentes, sem criacao automatica de pessoas/categorias/contas/centros de custo, e que a gravacao deve ser integral: se qualquer linha/campo falhar, nada deve ser importado
- tambem ficou registrado como fase posterior que o sistema deve evoluir para devolver erros por linha/campo, oferecer preview/validacao detalhada antes de gravar, tratar importacao de cadastros auxiliares em frente propria e avaliar eventual importacao parcial apenas no futuro
- esta microetapa nao abriu leitura detalhada das linhas, validacao de negocio linha a linha, tratamento de duplicidades, pre-visualizacao de importacao nem gravacao em massa no banco

## Fase 2 da importacao de lancamentos: validacao de conteudo linha a linha

- a validacao da aba `Modelo` passou a ler as linhas de dados, ignorar linhas totalmente vazias e validar cada linha/campo sem gravar nada no banco
- `tipo`, `status`, `descricao`, `valor`, `data_competencia`, `data_pagamento`, `pessoa_nome`, `categoria_nome`, `centro_custo_nome`, `conta_nome` e `conta_destino_nome` passaram a ser conferidos linha a linha, resolvendo nomes apenas contra cadastros existentes e reaproveitando `LancamentoFinanceiro.full_clean()` para regras ja consolidadas como obrigatoriedade de pessoa/categoria em receita/despesa, subcategoria valida, data de pagamento nao anterior a competencia, conta de destino em transferencia e bloqueio de contas iguais
- a pagina de `Importacao` passou a exibir um card de `Resultado da validacao` com total de linhas lidas, linhas validas, linhas com erro e uma lista de erros por linha/campo em linguagem operacional, mantendo explicito que nenhum lancamento foi importado nesta fase
- esta microetapa nao implementou gravacao/importacao real, confirmacao final, preview persistido em sessao, importacao parcial nem criacao automatica de cadastros auxiliares

## Fase 3 da importacao de lancamentos: gravacao all-or-nothing e mensagens amigaveis

- os erros da importacao deixaram de exibir nomes tecnicos da planilha na interface e passaram a mostrar rotulos amigaveis ao usuario, como `Pessoa`, `Categoria`, `Centro de custo`, `Conta`, `Data de pagamento` e `Observacoes`, mantendo o numero da linha e a mensagem curta de validacao
- a validacao de conteudo passou a devolver tambem os `LancamentoFinanceiro` validos ja preparados em memoria, mantendo a resolucao apenas contra cadastros existentes e reaproveitando `LancamentoFinanceiro.full_clean()` para as regras de negocio ja consolidadas
- quando nao existe erro em nenhuma linha, a `LancamentoFinanceiroImportacaoExportacaoView` grava todos os lancamentos dentro de `transaction.atomic()`, registra auditoria de criacao para cada lancamento e atualiza o total de `Linhas importadas`
- se qualquer linha tiver erro, nenhuma gravacao e executada e a tela informa explicitamente que nenhuma linha foi importada; se ocorrer inconsistencia no momento da gravacao, a transacao e revertida e o resultado volta a indicar importacao zerada
- a pagina de `Importacao` passou a informar `Linhas lidas`, `Linhas validas`, `Linhas importadas` e `Linhas com erro`, e a ajuda rapida passou a reforcar que somente cadastros ja existentes podem ser usados e que a importacao nao e parcial
- esta microetapa nao implementou preview avancado, segunda tela de confirmacao, importacao parcial, criacao automatica de cadastros auxiliares nem rateio por importacao

## Refinamento visual do retorno da importacao

- o card de resultado da importacao passou a exibir um banner de status no topo, diferenciando visualmente importacao concluida e validacao com erro sem alterar a politica all-or-nothing
- os totais de linhas lidas, validas, importadas e com erro foram mantidos em cards de destaque logo abaixo desse banner, priorizando leitura rapida do resumo
- a lista de erros por linha ficou mais legivel: cada linha com inconsistencia aparece em bloco proprio e cada campo com erro passou a ser apresentado em uma faixa separada com rotulo amigavel e mensagem curta
- esta microetapa foi restrita a organizacao visual e texto operacional do retorno da importacao, sem alterar validacao, gravacao, transacao, resolucao de cadastros ou regras de negocio ja consolidadas

## Relatorio de inconsistencias para download na importacao

- quando a importacao encontra erros, o banner de resultado da pagina de importacao passa a oferecer a acao `Baixar relatorio de inconsistencias`
- foi criada uma rota POST dedicada para gerar um XLSX simples de uma unica aba `Inconsistencias`, a partir da lista de erros ja calculada pela validacao atual, sem mudar a politica all-or-nothing nem revalidar ou regravar lancamentos nesse endpoint
- o relatorio gerado contem as colunas `Linha`, `Campo` e `Mensagem`, preservando o numero da linha, o rotulo amigavel exibido ao usuario e a mensagem operacional curta para facilitar a correcao da planilha original
- a leitura principal da tela e o arquivo baixado continuam priorizando rotulos amigaveis, sem expor a coluna de campo tecnico ao usuario final

## Alinhamento do formato de datas na importacao

- a leitura da importacao passou a priorizar datas em `dd/mm/aaaa`, mantendo `AAAA-MM-DD` como formato adicional tolerado internamente para nao quebrar arquivos tecnicamente validos
- a aba `Instruções` da planilha modelo passou a orientar `dd/mm/aaaa` como formato principal de preenchimento de datas, em coerencia com a exportacao e com o formato visual exibido ao usuario
- as mensagens de erro de `Data de competência` e `Data de pagamento` passaram a indicar explicitamente `dd/mm/aaaa`
- nao houve alteracao da politica all-or-nothing, nem abertura de importacao parcial, nem mudanca de regra de negocio

## Regras aplicadas nesta etapa

- `numero_documento` continua opcional para o usuario
- quando `numero_documento` vier vazio, o sistema continua gerando automaticamente antes de salvar
- quando o usuario informar `numero_documento` manualmente, o sistema valida se ja existe em outro lancamento
- se ja existir, o erro volta ao formulario no campo `numero_documento`
- a validacao funciona no cadastro e na edicao
- na edicao, o proprio registro nao e tratado como duplicado dele mesmo
- a geracao automatica tambem consulta a base para evitar repetir um numero ja existente

## Camada tecnica adotada

- a validacao principal ficou em `financeiro/models.py`
- nao foi criada constraint de banco nem migration nova nesta etapa
- a decisao foi manter a mudanca na camada da aplicacao por menor risco de regressao no estado atual do projeto

## Arquivos alterados nesta etapa

- `financeiro/models.py`
- `docs/CEREBRO_PROJETO.md`
- `docs/STATE.md`
- `docs/CODEX_RESULTADO.md`
- `docs/ROADMAP_FINANCEIRO.md`

## Resultado pratico

- o formulario de cadastro passa a bloquear `numero_documento` duplicado
- o formulario de edicao passa a bloquear duplicidade real sem acusar o proprio registro
- o comportamento atual de transferencia permanece intacto
- o comportamento atual de extrato, resumo e prestacao de contas permanece intacto
- a geracao automatica de `numero_documento` ficou mais defensiva e nao devolve fallback repetido silencioso

## Validacao local

- Nao foi possivel executar `py manage.py check` com sucesso no ambiente atual.
- Motivo: o interpretador disponivel nao tem o pacote `django` instalado.
- Foi possivel validar a sintaxe dos arquivos Python via `py -m compileall financeiro`.

## Complemento de consolidacao controlada

- `financeiro/forms.py` foi alinhado ao model atual para manter a obrigatoriedade condicional de `pessoa` e `categoria`
- `transferencia` continua limpando campos irrelevantes e exigindo apenas `conta_destino`
- a cadeia de migrations `0005` e `0006` foi mantida como parte coerente da evolucao incremental ja existente
- o texto com encoding quebrado no erro de `conta_destino` foi corrigido sem alterar regra de negocio

## Nova etapa incremental

- o formulario de lancamento passou a exibir os ultimos 5 lancamentos do favorecido selecionado
- o historico mostra data, tipo, descricao, valor, categoria e `numero_documento` quando existir
- a atualizacao do bloco ocorre junto da selecao da pessoa no autocomplete
- a implementacao foi mantida simples, sem alterar regra de negocio do lancamento

## Etapa de recibo

- cada lancamento financeiro passou a ter visualizacao propria de recibo em HTML imprimivel
- o recibo exibe descricao, valor, datas, pessoa, categoria, conta, `numero_documento` e observacoes quando disponiveis
- a listagem de lancamentos passou a oferecer acesso direto ao recibo
- a etapa foi mantida simples, sem PDF externo e sem alterar a logica do lancamento

## Refinamento do recibo

- o campo `Referente a` passou a usar a descricao do lancamento
- a data principal do recibo passou a priorizar `data_pagamento`
- quando `data_pagamento` estiver vazia, o recibo usa `data_competencia` com fallback explicito
- o recibo deixou de exibir conta financeira, observacoes, categoria tecnica e centro de custo
- a mensagem final continua com fallback simples no template, preparando etapa futura de mensagem por categoria

## Mensagem opcional por categoria no recibo

- `CategoriaFinanceira` passou a ter o campo opcional `mensagem_recibo`
- o cadastro e a edicao de categoria agora permitem preencher essa mensagem
- quando o lancamento tiver categoria com `mensagem_recibo`, o recibo exibe esse texto em destaque no rodape
- quando a categoria nao tiver mensagem cadastrada, o recibo continua usando a mensagem padrao simples e segura
- a etapa nao implementa ainda assinatura configuravel nem configuracao institucional dinamica

## Refinamento visual do recibo

- o recibo deixou de ter aparencia principal de tabela administrativa
- o layout passou a priorizar formato de documento simples, com cabecalho, destaque de numero e valor e corpo textual
- foram adicionados placeholders visuais discretos para identidade institucional e cidade, sem criar configuracao nova nesta etapa
- o refinamento ficou isolado no template do recibo, sem alterar regra de negocio

## Acabamento fino do recibo

- o placeholder tecnico visivel do cabecalho foi removido
- `Recebi(emos) de` passou a mostrar apenas o nome da pessoa
- `A importancia de` passou a usar valor por extenso, mantendo o valor numerico em destaque no topo
- o recibo deixou de expor `data_competencia` e passou a mostrar apenas a data final em formato humano e documental
- a proporcao entre topo, corpo, assinatura e rodape foi ajustada para reduzir espacos vazios e melhorar a impressao

## Assinatura configuravel no recibo

- foi criado o cadastro simples de `AssinaturaInstitucional`
- a estrutura minima inclui `nome`, `assinatura_texto`, `nome_exibicao`, `cargo`, `ativo` e `padrao`
- o recibo passou a buscar a assinatura ativa marcada como padrao
- quando a assinatura padrao existe, o recibo mostra o texto manuscrito configurado e, quando informados, nome de exibicao e cargo
- quando nao existe assinatura padrao, o recibo continua funcionando com fallback simples
- a etapa nao implementa ainda assinatura por imagem nem configuracao institucional completa

## Configuracao institucional no recibo

- foi criado o cadastro simples de `ConfiguracaoInstitucional`
- a estrutura minima inclui `nome_instituicao`, `cidade`, `logo_url`, `mensagem_padrao_recibo`, `ativo` e `padrao`
- o recibo passou a buscar a configuracao institucional ativa marcada como padrao
- quando a configuracao existir, o recibo pode usar nome da instituicao, cidade, logo e mensagem padrao
- quando algum dado institucional nao estiver preenchido, o recibo continua usando fallback seguro e nao quebra o layout
- a etapa nao implementa ainda configuracao institucional complexa para multiplas instituicoes nem revisao global de layout

## Integracao visual final de logo e assinatura

- a logo configurada passou a ser tratada como URL acessivel pelo navegador no template do recibo
- quando a URL da logo falha, a imagem e ocultada sem quebrar o cabecalho
- `assinatura_texto` passou a ser exibido com estilo manuscrito no bloco de assinatura
- `nome_exibicao` e `cargo` continuam aparecendo abaixo da assinatura quando preenchidos
- a linha de cidade/data foi mantida limpa, com fallback seguro quando a cidade nao estiver configurada

## Compactacao final da impressao do recibo

- o bloco do recibo passou a respeitar melhor a altura do proprio conteudo na impressao
- os espacos verticais entre corpo, mensagem final, assinatura e fim do documento foram reduzidos
- o PDF do recibo deixa de aparentar preenchimento artificial da pagina inteira quando o conteudo e curto

## Centralizacao e largura util do recibo

- o bloco do recibo na impressao voltou a usar `display: block` com centralizacao horizontal
- a largura util do documento foi ampliada para melhor aproveitamento da folha A4
- o PDF deixa de ficar deslocado para a esquerda e com excesso de espaco vazio a direita

## Respiro superior do recibo

- a margem superior da versao impressa do recibo foi levemente ampliada
- o documento ganhou respiro inicial sem perder a compactacao final do PDF

## Microetapa de navegacao minima

- o texto com encoding quebrado na home do modulo financeiro foi corrigido
- o menu superior do financeiro ganhou dropdown `Configuracoes`
- o novo dropdown passou a expor `Assinaturas` e `Configuracao Institucional`
- a home do modulo financeiro passou a exibir atalhos visiveis para `Assinaturas` e `Configuracao Institucional`
- a navegacao ja validada de `Financeiro`, `Lancamentos`, `Extratos`, `Relatorios` e `Cadastros` foi preservada sem reorganizacao ampla

## Revisao leve da home do financeiro

- os textos visiveis da home foram revisados sem alterar rotas nem a estrutura geral da pagina
- o subtitulo ficou mais direto e operacional
- atalhos como `Extratos`, `Resumo` e `Assinaturas` ficaram com rotulos mais explicitos
- a etapa permaneceu limitada a clareza textual, sem redesign global nem mudanca de regra de negocio

## Padronizacao leve de rotulos do financeiro

- menu superior, home e titulos ja existentes foram confrontados para reduzir inconsistencias visiveis
- `Resumo` foi alinhado com `Resumo do Periodo` onde havia ganho claro de consistencia
- `Assinaturas` e `Configuracao Institucional` foram alinhadas aos titulos institucionais ja usados nas telas correspondentes
- a estrutura de navegacao, as rotas e as regras de negocio permaneceram intactas

## Padronizacao leve das paginas internas do financeiro

- botoes de criacao de `Assinaturas Institucionais` e `Configuracoes Institucionais` ficaram mais especificos e coerentes com os titulos das telas
- os botoes principais de `Resumo` e `Prestacao de Contas` foram alinhados para `Atualizar relatorio`
- a etapa permaneceu restrita a consistencia textual leve, sem alterar estrutura, rotas ou regra de negocio

## Fechamento leve de padronizacao nas listagens do financeiro

- os botoes principais de criacao em `Contas`, `Pessoas`, `Categorias` e `Lancamentos` foram alinhados aos nomes completos das entidades exibidas nas telas
- os rotulos ficaram mais explicitos para usuario leigo sem alterar fluxo, rotas ou estrutura

## Primeira versao do lancamento com rateio

- o formulario de lancamento passou a oferecer o checkbox `Lancamento com rateio`
- quando o checkbox nao estiver marcado, o comportamento atual do lancamento comum permanece inalterado
- quando o checkbox estiver marcado, o formulario passa a exigir `valor total do documento` e no minimo 2 linhas validas de rateio
- cada linha de rateio exige categoria e valor positivo
- a soma das linhas precisa ser igual ao `valor total do documento`
- ao salvar um rateio valido, o sistema cria multiplos `LancamentoFinanceiro` com os mesmos dados comuns, variando categoria e valor por linha
- os lancamentos criados no rateio recebem `com_rateio = True` e compartilham o mesmo `grupo_rateio`
- o mesmo `numero_documento` passou a ser aceito apenas entre linhas do mesmo grupo de rateio, preservando o bloqueio de duplicidade acidental fora desse contexto
- nesta primeira versao, `valor_total_documento` existe apenas no formulario para validacao e nao e persistido no model
- nesta primeira versao, a edicao do grupo rateado nao e coordenada em bloco; a edicao continua individual por linha e isso foi registrado como limitacao conhecida

## Segunda versao do lancamento com rateio

- o fluxo de create com rateio deixou de quebrar no redirecionamento final e volta corretamente para a listagem apos criar o grupo
- a causa raiz era o fluxo de rateio criar varias linhas sem um `self.object` unico para o comportamento esperado da `CreateView`; a resolucao foi tratar explicitamente o redirecionamento e definir um objeto de referencia do grupo criado
- o campo `tipo` do formulario passou a abrir preenchido com `receita` e sem opcao vazia inicial
- `data_pagamento` passou a aparecer antes de `data_competencia` no formulario
- ao preencher `data_pagamento`, o formulario sugere automaticamente `data_competencia` quando ela ainda estiver vazia, sem bloquear edicao manual posterior
- o lancamento comum foi preservado sem mudanca de regra
- o rateio continua aceitando mais de 2 linhas e agora consolida categorias repetidas por soma antes de salvar as linhas finais
- a validacao do total do documento continua obrigatoria
- a busca por categoria no lancamento comum continua por digitacao com busca por contem no autocomplete ja existente
- a edicao do grupo rateado continua individual por linha e ainda nao existe edicao coordenada em bloco nesta etapa

## Consolidacao documental da auditoria funcional

- foi registrada sem patch de codigo a abertura da frente de revisao operacional do formulario de lancamento para tratar obrigatoriedade de `data_pagamento` e maior previsibilidade no preenchimento de `data_competencia`
- foi registrada sem patch de codigo a abertura da frente de definicao da ordem oficial da listagem de lancamentos
- foi registrada sem patch de codigo a abertura da frente de consolidacao de rateios no extrato por `grupo_rateio` ou `numero_documento`
- foi registrada sem patch de codigo a abertura da frente de auditoria de alteracoes no financeiro, com implementacao incremental preferencial sem `signals`
- a auditoria tambem consolidou que o extrato atual ainda exibe rateios linha a linha e que o autopreenchimento de `data_competencia` segue fragil por depender apenas de comportamento visual no template

## Consolidacao documental da regra precisa de rateio e extrato

- foi registrada sem patch de codigo a correção da regra documental do rateio para deixar explicito que `numero_documento` continua unico no sistema, com excecao restrita a replicacao interna entre linhas do mesmo `grupo_rateio`
- foi registrada sem patch de codigo a vedacao explicita de coincidencia entre o `numero_documento` de um grupo rateado e outro documento independente ja lancado no sistema
- foi registrada sem patch de codigo a diretriz oficial do extrato com ordem crescente por `data_competencia`, desempate por `criado_em` e `pk`
- foi registrada sem patch de codigo a diretriz futura de leitura documental consolidada do rateio no extrato por `grupo_rateio`, com exibicao do valor total do documento

## Revisao operacional de data_pagamento e data_competencia

- `data_pagamento` passou a ser obrigatoria no formulario operacional do modulo, com indicativo visual claro de obrigatoriedade
- `data_pagamento` continua aparecendo antes de `data_competencia`
- ao preencher `data_pagamento`, o formulario agora preenche automaticamente `data_competencia` quando ela estiver vazia ou ainda mantiver valor autoatribuido
- a pessoa usuaria continua podendo editar manualmente `data_competencia` sem sobrescrita indevida quando ja houver valor proprio no campo
- o comportamento foi ajustado para funcionar melhor tanto na abertura inicial do formulario quanto na interacao posterior do usuario
- a revisao desta etapa ficou concentrada em `financeiro/forms.py` e `financeiro/templates/financeiro/lancamento_form.html`, sem alterar modelagem nem criar migration nova

## Ordem oficial da listagem principal de lancamentos

- a listagem principal de lancamentos passou a usar ordem explicita por `-data_competencia`, `-data_pagamento`, `-criado_em` e `-pk`
- a decisao foi aplicada diretamente na `LancamentoFinanceiroListView`
- o `Meta.ordering` do model foi preservado para evitar impacto colateral em extrato, relatorios, historico do favorecido e outras consultas
- os filtros atuais da listagem foram preservados sem alteracao de regra de negocio

## Validacao precisa de numero_documento no rateio

- a validacao de `numero_documento` foi reforcada para manter a unicidade global do documento, com excecao restrita as linhas do mesmo `grupo_rateio`
- o sistema continua aceitando repeticao de `numero_documento` apenas como replicacao interna do mesmo grupo rateado
- o sistema passou a impedir explicitamente que uma linha editada de grupo rateado fique com `numero_documento` diferente das demais linhas do mesmo grupo
- o sistema tambem passa a sinalizar erro quando encontrar grupo rateado antigo internamente inconsistente em `numero_documento`
- a etapa preservou o lancamento comum, o create do rateio e a premissa atual de edicao individual das linhas

## Consolidacao do rateio no extrato

- o extrato por conta passou a manter ordem crescente por `data_competencia`, com desempate por `criado_em` e `pk`
- lancamentos rateados passaram a aparecer consolidados por `grupo_rateio` na leitura da tela
- a linha consolidada do extrato agora exibe o valor total do documento rateado em vez de fragmentar o mesmo documento em varias linhas
- a consolidacao ficou restrita a apresentacao do extrato, preservando a modelagem atual do rateio e a coerencia do saldo acumulado
- lancamentos comuns permanecem com leitura individual sem alteracao
- linhas antigas ou inconsistentes sem `grupo_rateio` valido continuam aparecendo individualmente ate regularizacao manual da base

## Definicao incremental da estrategia de auditoria

- foi auditado sem patch de codigo que o modulo `financeiro` ainda nao possui trilha propria de criacao, edicao e exclusao por registro
- ficou definida como estrategia incremental mais segura a abertura da auditoria por model proprio, sem `signals` e com registro explicito nas views
- a primeira entidade recomendada para entrar na trilha e `LancamentoFinanceiro`
- a auditoria deve registrar acao, modelo, id do registro, data/hora, usuario quando disponivel e campos alterados
- a expansao posterior deve seguir para contas, pessoas, categorias, centros de custo, assinaturas e configuracao institucional

## Primeira versao da auditoria de LancamentoFinanceiro

- foi criado o model `AuditoriaFinanceiro`
- a migration `0011_auditoriafinanceiro.py` foi adicionada para persistir a trilha inicial de auditoria
- o sistema passou a registrar create, update e delete de `LancamentoFinanceiro` sem uso de `signals`
- o create comum, o create com rateio, a edicao individual de linha rateada e o delete agora geram eventos explicitos de auditoria
- cada evento de auditoria guarda acao, modelo afetado, id do registro, data/hora, usuario quando disponivel e campos alterados em JSON simples
- nesta primeira versao, a auditoria continua restrita a `LancamentoFinanceiro` e ainda nao possui interface propria de consulta

## Leitura minima da auditoria de LancamentoFinanceiro

- foi criada uma tela simples para leitura da auditoria ja gravada de `LancamentoFinanceiro`
- a listagem mostra data/hora, acao, modelo, id do registro, usuario e campos alterados em resumo estruturado
- a ordenacao da leitura ficou explicita por `data_hora` decrescente, com desempate por `pk`
- a leitura da auditoria foi integrada ao modulo por rota propria e acesso discreto no dropdown `Configuracoes` e na home
- nesta primeira leitura operacional, a tela ainda nao possui filtros complexos nem paginacao avancada

## Filtros simples na leitura da auditoria

- a tela da auditoria passou a aceitar filtros simples por `acao`, `data_inicial`, `data_final` e `registro_id`
- a ordenacao foi preservada por `-data_hora` e `-pk`
- o filtro por usuario nao entrou nesta etapa porque o proprio usuario da auditoria continua opcional na primeira versao
- a etapa manteve a leitura da auditoria simples, sem busca avancada nem paginacao complexa

## Consolidacao documental da estrategia de edicao coordenada do grupo rateado

- foi registrada sem patch de codigo a estrategia mais segura para futura edicao coordenada do grupo rateado por meio de view e formulario proprios do grupo
- ficou registrado que esse fluxo futuro nao deve se misturar com a edicao individual de uma linha rateada
- ficou registrado apenas de forma documental que a estrategia futura foi consolidada, sem implementacao nesta microetapa

## Ajuste documental de governanca entre chats

- foi registrada sem patch de codigo a consolidacao dos quatro documentos-base permanentes do projeto
- ficou registrado que esses documentos devem ser preservados sem retroagir historico e atualizados por acrescimo, consolidacao ou ajuste cirurgico
- ficou registrado que todo novo chat deve comecar lendo os quatro documentos-base, mantendo o repositorio como fonte final de verdade
- ficou registrado que a continuidade entre chats deve seguir protocolo permanente de preparacao e encerramento, sem destruir historico documental

## Base inicial da edicao coordenada do grupo rateado

- foi criada a primeira implementacao real do fluxo proprio de edicao coordenada do grupo rateado
- a nova base usa view, rota e template proprios, sem substituir a edicao individual de uma linha
- o grupo passa a ser carregado por `grupo_rateio` apenas quando houver grupo valido de rateio
- o formulario inicial da tela passa a reunir dados comuns do grupo e linhas do rateio no mesmo fluxo
- o salvamento inicial foi implementado de forma transacional, com preservacao do mesmo `grupo_rateio` e com auditoria de create, update e delete das linhas afetadas
- a etapa abriu uma base funcional e coerente, mas ainda nao entrega a experiencia final completa dessa frente

## Microcorrecao do casamento das linhas na edicao coordenada

- a persistencia da edicao coordenada do grupo deixou de reaproveitar linhas apenas por posicao na lista
- quando o payload traz `id`, a linha agora e atualizada exatamente pelo mesmo registro do `grupo_rateio` atual
- ids invalidos ou externos ao grupo agora geram erro de validacao no formulario
- linhas sem `id` continuam sendo criadas e linhas antigas ausentes no payload final continuam sendo removidas, com salvamento transacional e auditoria preservados

## Refinamento operacional da edicao coordenada do grupo rateado

- grupos invalidos, legados ou com consistencia insuficiente para a edicao coordenada passaram a retornar com mensagem operacional e redirecionamento seguro para a edicao individual
- a listagem principal de lancamentos passou a oferecer acesso discreto adicional a `Editar grupo` para linhas vinculadas a `grupo_rateio`
- a etapa manteve a separacao entre edicao individual de linha e edicao coordenada do grupo, sem redesign amplo do fluxo

## Refinamento de UX da tela de edicao coordenada do grupo rateado

- a tela propria do grupo rateado passou a separar visualmente com mais clareza os dados comuns do documento e as linhas do rateio
- os textos orientativos da tela foram reforcados para deixar explicito que o salvamento altera o grupo inteiro e nao apenas uma linha isolada
- o bloco das linhas do rateio passou a exibir feedback visual mais claro quando houver inconsistencias de validacao no payload
- a etapa preservou a base tecnica ja aberta: salvamento transacional, validacoes consolidadas, auditoria sem `signals` e edicao individual intacta

## Refinamento de mensagens e estados operacionais da tela coordenada

- a tela da edicao coordenada passou a explicar com mais clareza o que acontece ao salvar o grupo e para onde o usuario retorna depois da gravacao
- erros de validacao geral e inconsistencias do rateio passaram a aparecer com estado visual mais explicito de bloqueio antes do salvamento
- a navegacao de apoio da tela agora tambem oferece retorno direto para a edicao individual da linha representativa do grupo, sem substituir o fluxo coordenado
- o fallback seguro para grupos invalidos tambem passou a usar mensagem operacional mais clara ao redirecionar para a edicao individual

## Acabamento de estados para grupos legados ou inconsistentes

- o fallback do fluxo coordenado agora diferencia melhor os motivos operacionais de bloqueio para grupos invalidos, nao encontrados, insuficientes ou com `numero_documento` divergente
- quando o fluxo coordenado nao e aberto, a edicao individual passa a receber contexto explicito de que foi usada como caminho seguro alternativo para aquele grupo
- a etapa manteve o comportamento defensivo: grupos problematicos continuam fora da edicao coordenada e nao sao absorvidos automaticamente

## Acabamento de outros estados operacionais da edicao coordenada

- o retorno apos salvar o grupo ficou mais previsivel, com volta sinalizada para a listagem principal de lancamentos
- o cancelamento da tela coordenada agora retorna para a listagem com contexto operacional explicito de que nao houve gravacao
- a navegacao de apoio entre a tela coordenada, a tela individual e a listagem principal ficou mais coerente sem substituir nenhum dos fluxos

## Refinamentos finais de UX da tela coordenada

- a tela propria de edicao coordenada recebeu acabamento visual leve para melhorar hierarquia entre resumo do grupo, dados comuns, linhas do rateio e bloco final de acoes
- os blocos de aviso, orientacao e feedback passaram a seguir apresentacao mais consistente ao longo da tela
- as acoes principais e secundarias ficaram visualmente mais legiveis e previsiveis, sem redesign amplo nem mudanca de regra de negocio

## Simplificacao da tela de edicao do grupo rateado

- a tela coordenada foi aproximada do formulario comum de lancamento em titulo, hierarquia visual e distribuicao dos blocos
- os textos fixos longos foram reduzidos para avisos curtos e contextuais, mantendo apenas o necessario para indicar que a alteracao afeta o rateio inteiro
- o bloco de rateio foi preservado como diferenca funcional principal da tela, sem alterar validacoes, auditoria ou o fluxo individual ja existente

## Expansao incremental da auditoria para ContaFinanceira

- a auditoria do modulo financeiro passou a registrar create, update e delete de `ContaFinanceira` com o mesmo padrao incremental ja usado em `LancamentoFinanceiro`
- a expansao reaproveitou model proprio de auditoria, sem `signals` e sem reestruturacao ampla do dominio
- a leitura atual da auditoria foi mantida simples, mas passou a abranger as entidades ja auditadas do financeiro, incluindo `ContaFinanceira`
- nesta microetapa, a auditoria ainda nao foi expandida para pessoas, categorias, centros de custo, assinaturas ou configuracao institucional

## Microcorrecao da edicao rateada na listagem e nas datas do grupo

- a tela de edicao coordenada do grupo rateado passou a preencher `data_pagamento` e `data_competencia` no formato aceito pelos inputs HTML de data
- a listagem principal deixou de exibir o botao separado `Editar grupo`
- para lancamentos rateados, a acao principal `Editar` da listagem agora abre diretamente a edicao coordenada do `grupo_rateio`
- para lancamentos comuns, a acao principal `Editar` continua abrindo a edicao individual do lancamento

## Consolidacao documental de melhoria futura de densidade visual

- nesta microetapa nao houve patch de codigo
- foi registrada a partir de teste real de uso a limitacao atual de densidade visual e aproveitamento horizontal em telas do financeiro, especialmente com o navegador em 100% de zoom
- a melhoria foi consolidada documentalmente como frente futura oficial de refinamento visual transversal do modulo

## Primeira microetapa do refinamento transversal de densidade visual

- a frente transversal de densidade visual e aproveitamento horizontal do financeiro foi iniciada no repositorio
- a base visual compartilhada do modulo foi ajustada para reduzir espacamentos, compactar filtros, inputs, labels, tabelas e acoes sem redesign amplo
- nesta primeira aplicacao, a listagem de lancamentos e o formulario padrao de lancamento/edicao passaram a aproveitar melhor a largura horizontal da tela em 100% de zoom
- a etapa preservou a identidade atual do sistema e deixou a expansao para as demais telas como passo posterior da mesma frente

## Aplicacao do refinamento de densidade visual ao extrato

- o extrato por conta passou a usar cabecalho mais compacto e horizontal, com meta-informacoes resumidas em blocos mais densos
- os filtros do extrato foram reorganizados para aproveitar melhor a largura util da tela em 100% de zoom
- a tabela do extrato recebeu distribuicao horizontal mais previsivel entre data, descricao, tipo, valores, saldo acumulado e observacoes
- a microetapa preservou integralmente calculo, saldo, ordenacao e consolidacao funcional do extrato

## Microcorrecao da apresentacao operacional do extrato

- o texto fixo explicando as cores no topo do extrato foi removido
- o `numero_documento` deixou de aparecer dentro da descricao e passou a usar coluna propria ao lado da data
- a data principal exibida na linha do extrato passou a priorizar `data_pagamento`, com fallback para `data_competencia`
- a descricao da linha foi limpa para nao repetir metadados do documento nem a frase de rateio consolidado

## Ajuste do saldo inicial no corpo e preparacao da impressao do extrato

- o `Saldo inicial` deixou de aparecer no bloco resumido superior e passou a ficar como primeira linha destacada no corpo da tabela do extrato
- o `Saldo final` foi mantido como ultima linha destacada no corpo da tabela, sem migrar para o cabecalho de impressao
- a tela do extrato passou a oferecer botao de impressao
- a impressao do extrato ganhou cabecalho proprio com identificacao clara do relatorio, mantendo `Saldo inicial` e `Saldo final` dentro da tabela

## Limpeza final das linhas de saldo no extrato

- o extrato deixou de repetir `Saldo final` no bloco resumido superior e manteve no topo apenas informacoes operacionais mais uteis
- a linha de `Saldo inicial` passou a aparecer sempre como primeira linha destacada do corpo da tabela, inclusive com periodo filtrado
- as linhas de `Saldo inicial` e `Saldo final` deixaram de usar data, tipo e hifens artificiais, ficando com apresentacao mais limpa e menos parecida com movimentacao comum

## Ajuste da nomenclatura e da impressao do extrato

- a primeira linha destacada do corpo do extrato passou a usar o rotulo `Saldo anterior`
- a impressao do extrato foi refinada para reduzir quebra desnecessaria de texto, dar mais prioridade horizontal para `Descricao` e deixar as linhas com altura mais uniforme
- as colunas curtas do extrato impresso passaram a evitar quebra sempre que possivel, sem alterar calculo, ordenacao ou consolidacao funcional

## Correcao do valor exibido na linha Saldo anterior

- a linha `Saldo anterior` do corpo do extrato passou a usar diretamente o valor de `saldo_anterior` ja calculado no contexto
- quando nao houver periodo filtrado, a linha continua usando `saldo_inicial` como fallback
- a microcorrecao nao duplicou logica de calculo e nao alterou saldo, ordenacao ou consolidacao funcional

## Limpeza do topo na versao impressa do extrato

- no modo de impressao do extrato, o cabecalho visual da tela passou a ficar oculto
- o PDF passou a manter apenas o cabecalho proprio de impressao com identificacao do extrato e a tabela
- o ajuste reduziu a redundancia visual sem alterar linhas de saldo, calculo ou consolidacao funcional

## Aplicacao do refinamento de densidade visual ao resumo por periodo

- o resumo por periodo passou a usar cabecalho mais compacto e alinhado com a base visual compartilhada do financeiro
- os filtros do resumo foram reorganizados para aproveitar melhor a largura horizontal da tela em 100% de zoom, mantendo leitura aceitavel em mobile
- os blocos de totais e indicadores deixaram de usar caixas mais soltas e passaram a seguir a hierarquia visual mais enxuta dos KPIs compartilhados do modulo
- a microetapa preservou integralmente calculos, agrupamentos e consolidacoes funcionais do resumo

## Aplicacao do refinamento visual a prestacao de contas

- a tela `prestacao_contas.html` passou a reaproveitar a base visual compartilhada do financeiro em cabecalho, filtros e blocos de totais
- a prestacao de contas ganhou hierarquia visual mais compacta e consistente com o resumo por periodo, sem alterar calculos, agrupamentos ou consolidacoes funcionais
- a microetapa tambem consolidou na apresentacao dessa tela o padrao de datas visiveis ao usuario em `dd/mm/aaaa`, incluindo o periodo do relatorio e os metadados principais de emissao

## Refinamento visual da tela de auditoria do financeiro

- a tela `auditoria_lancamento_list.html` passou a usar cabecalho no padrao visual compartilhado do modulo financeiro
- os filtros existentes foram compactados para melhor aproveitamento horizontal da tela em 100% de zoom, sem abrir novos filtros ou paginacao
- a listagem da auditoria passou a ficar dentro de bloco visual mais consistente com as demais telas do modulo, mantendo leitura simples das entidades ja auditadas: `LancamentoFinanceiro` e `ContaFinanceira`
- a apresentacao de `data_hora` foi mantida em formato `dd/mm/aaaa` com horario, sem alterar captura, ordenacao ou comportamento funcional da auditoria

## Expansao incremental da auditoria para PessoaFinanceira

- a auditoria do modulo financeiro passou a registrar create, update e delete de `PessoaFinanceira` com o mesmo padrao incremental ja usado em `LancamentoFinanceiro` e `ContaFinanceira`
- a expansao reaproveitou o model proprio de auditoria, sem `signals` e sem reestruturacao ampla do dominio
- a leitura atual da auditoria foi mantida simples e passou a abranger tambem os eventos de `PessoaFinanceira`
- nesta microetapa, a auditoria ainda nao foi expandida para categorias, centros de custo, assinaturas ou configuracao institucional

## Expansao incremental da auditoria para CategoriaFinanceira

- a auditoria do modulo financeiro passou a registrar create, update e delete de `CategoriaFinanceira` com o mesmo padrao incremental ja usado nas demais entidades ja auditadas
- a expansao reaproveitou o model proprio de auditoria, sem `signals` e sem reestruturacao ampla do dominio
- a leitura atual da auditoria foi mantida simples e passou a abranger tambem os eventos de `CategoriaFinanceira`
- nesta microetapa, a auditoria ainda nao foi expandida para centros de custo, assinaturas ou configuracao institucional

## Expansao incremental da auditoria para CentroCusto

- a auditoria do modulo financeiro passou a registrar create, update e delete de `CentroCusto` com o mesmo padrao incremental ja usado nas demais entidades ja auditadas
- a expansao reaproveitou o model proprio de auditoria, sem `signals` e sem reestruturacao ampla do dominio
- a leitura atual da auditoria foi mantida simples e passou a abranger tambem os eventos de `CentroCusto`
- nesta microetapa, a auditoria ainda nao foi expandida para assinaturas ou configuracao institucional

## Expansao incremental da auditoria para AssinaturaInstitucional

- a auditoria do modulo financeiro passou a registrar create, update e delete de `AssinaturaInstitucional` com o mesmo padrao incremental ja usado nas demais entidades ja auditadas
- a expansao reaproveitou o model proprio de auditoria, sem `signals` e sem reestruturacao ampla do dominio
- a leitura atual da auditoria foi mantida simples e passou a abranger tambem os eventos de `AssinaturaInstitucional`
- nesta microetapa, a auditoria ainda nao foi expandida para configuracao institucional

## Expansao incremental da auditoria para ConfiguracaoInstitucional

- a auditoria do modulo financeiro passou a registrar create, update e delete de `ConfiguracaoInstitucional` com o mesmo padrao incremental ja usado nas demais entidades ja auditadas
- a expansao reaproveitou o model proprio de auditoria, sem `signals` e sem reestruturacao ampla do dominio
- a leitura atual da auditoria foi mantida simples e passou a abranger tambem os eventos de `ConfiguracaoInstitucional`
- com esta microetapa, a trilha inicial de auditoria passou a cobrir as entidades operacionais e institucionais hoje existentes no modulo financeiro

## Filtro por usuario na leitura da auditoria

- a tela de auditoria do financeiro passou a oferecer filtro simples por usuario, em conjunto com os filtros ja existentes por acao, periodo e id do registro
- o filtro por usuario usa a lista de usuarios ja presentes nos eventos atualmente exibidos pela auditoria
- a leitura da auditoria foi mantida simples, sem paginacao nova, sem filtros complexos adicionais e sem alterar a captura dos eventos

## Consolidacao estrutural da obrigatoriedade de data_pagamento

- a obrigatoriedade de `data_pagamento` deixou de ficar apenas no formulario e passou a ser validada tambem no `clean()` de `LancamentoFinanceiro`
- o ajuste preservou os fluxos atuais de lancamento comum e rateado, sem abrir refatoracao ampla do modulo
- nesta microetapa, a validacao estrutural subiu para o nivel da aplicacao, mas o campo permaneceu com `null/blank` na modelagem de banco por compatibilidade com bases legadas

## Correcao da apresentacao do extrato e do cabecalho da auditoria

- a coluna `Descricao` do extrato voltou a ficar limpa, sem linha secundaria de `Favorecido` ou `Categoria`
- o extrato passou a usar coluna propria de `Favorecido`, sem reintroduzir `Categoria` na tabela nesta microcorrecao
- a microetapa preservou calculo, ordenacao, consolidacao funcional do rateio e o padrao visual limpo ja consolidado no extrato
- o cabecalho visual da tela de auditoria foi reestruturado para eliminar a sobreposicao entre titulo, subtitulo e acao lateral

## Consolidacao da hierarquia entre categoria pai e subcategoria nos lancamentos

- `CategoriaFinanceira` passou a bloquear vinculacao direta de categoria pai em `LancamentoFinanceiro`
- o formulario comum, o rateio inicial e a edicao coordenada do grupo passaram a aceitar apenas subcategorias validas, com `categoria_pai` preenchida
- a validacao estrutural tambem subiu para o `clean()` de `LancamentoFinanceiro`, impedindo gravacao indevida mesmo fora do formulario
- a microetapa preservou compatibilidade de base sem migracao nova, mas lancamentos futuros ou atualizados com categoria pai passam a exigir regularizacao para subcategoria valida

## Diagnostico estrutural da camada visual e abertura da governanca visual

- foi feito mapeamento estrutural da interface atual do projeto, cobrindo templates-base, tipos de tela, componentes visuais candidatos a padronizacao e dependencias de layout
- o diagnostico confirmou que o `financeiro` hoje concentra a base visual mais madura, enquanto `biblioteca` e `configuracoes` ainda nao compartilham o mesmo shell visual
- tambem ficou registrado que a adocao imediata de sidebar ou menu lateral no projeto inteiro nao e segura no estado atual, por ainda depender de reorganizacao previa do layout-base
- nenhum patch de codigo foi feito nesta etapa
- esta etapa foi exclusivamente de diagnostico e governanca documental da frente visual

## Preparacao tecnica do shell visual compartilhado do financeiro

- `financeiro/base.html` foi reorganizado de forma cirurgica como shell visual compartilhado do modulo, sem introduzir menu lateral e sem alterar paginas de impressao, PDF ou recibo
- a base compartilhada passou a concentrar de forma mais explicita classes reutilizaveis de cabecalho de pagina, callouts, chips de resumo e blocos auxiliares usados em formularios e rateio
- a inicializacao JS do dropdown de contas foi consolidada no shell compartilhado, reduzindo duplicacao entre telas de relatorio do modulo
- a etapa preservou comportamento funcional e ficou restrita a preparacao tecnica anterior a qualquer futura troca estrutural da navegacao principal

## Primeira onda de padronizacao visual das telas-chave do financeiro

- `lancamento_list.html`, `lancamento_form.html` e `auditoria_lancamento_list.html` passaram a compartilhar com mais consistencia o mesmo padrao de header/topo do modulo
- a etapa alinhou titulo, subtitulo e acoes laterais dessas tres telas ao vocabulário visual ja consolidado em `financeiro/base.html`
- a leitura visual entre listagem, formulario e auditoria ficou mais coerente sem alterar regra de negocio, filtros, captura de auditoria ou fluxo operacional
- sidebar ou menu lateral ainda nao foram implementados nesta microetapa

## Consolidacao da sidebar como navegacao principal no desktop do financeiro

- `financeiro/base.html` foi refinado para colocar a sidebar do modulo como navegacao principal no desktop, mantendo a topbar apenas como barra utilitaria minima
- os grupos `Visao geral`, `Movimentacao`, `Relatorios`, `Cadastros` e `Institucional` passaram a organizar a navegacao lateral de forma coerente com as rotas ja existentes do modulo
- o estado ativo da navegacao passou a ficar visivel tanto no item lateral quanto no grupo correspondente, sem alterar regra de negocio nem refatorar telas individuais
- a navegacao mobile foi preservada em modo conservador nesta etapa, ainda apoiada pela topbar e sem drawer lateral completo
- a validacao local confirmou status `200` para home, listagem, formulario, auditoria, extrato, resumo, prestacao de contas e edicao coordenada do grupo rateado apos a correcao do template da sidebar

## Drawer mobile da sidebar do financeiro

- `financeiro/base.html` passou a oferecer a versao mobile da sidebar em modo drawer/offcanvas, com abertura e fechamento controlados pela topbar compacta do modulo
- a implementacao incluiu overlay, botao de abertura, botao de fechamento e encerramento do drawer por clique fora ou tecla `Escape`, sem depender de hover
- o desktop foi preservado como ja estava, com a sidebar seguindo como navegacao principal e sem regressao nas telas centrais do modulo
- a validacao local confirmou status `200` para home, listagem, formulario, auditoria, extrato, resumo, prestacao de contas e edicao coordenada do grupo rateado, e tambem confirmou a presenca dos hooks HTML do drawer no shell renderizado

## Refino visual e ergonomico da sidebar do financeiro

- `financeiro/base.html` foi refinado para reduzir textos explicativos permanentes na topbar e na lateral, deixando o shell mais silencioso visualmente
- os grupos da sidebar passaram a funcionar como blocos expansivos/recolhiveis, com indicacao visual de grupo ativo, item ativo, grupo expandido e grupo recolhido
- o grupo da rota ativa passa a abrir automaticamente no carregamento, e a interacao foi simplificada para manter um grupo aberto por vez no shell
- a mesma logica de expansao segue funcional por clique/toque no desktop e no mobile, sem depender de hover
- a validacao local confirmou status `200` para home, listagem, formulario, auditoria, extrato, resumo, prestacao de contas e edicao coordenada do grupo rateado apos esse refino

## Acabamento visual final do shell da sidebar no financeiro

- `financeiro/base.html` recebeu acabamento visual de contraste, espacamento e densidade para deixar a sidebar mais limpa, mais silenciosa e mais confortavel em uso continuo
- o estado ativo da navegacao ficou mais claro com melhor diferenca entre grupo ativo, grupo expandido, item ativo e item neutro, sem alterar a arquitetura ja consolidada
- a topbar foi deixada ainda mais discreta, com menos peso visual e menor competicao com a lateral e com o `financeiro-page-header`
- o drawer mobile tambem foi refinado em largura, overlay e ergonomia visual, mantendo a base funcional ja entregue
- a validacao local confirmou status `200` para home, listagem, formulario, auditoria, extrato, resumo, prestacao de contas e edicao coordenada do grupo rateado apos esse acabamento

## Correcao estrutural de overflow horizontal no shell do financeiro

- foi corrigido um problema real de responsividade no shell do `financeiro`, em que parte do conteudo podia ficar cortada a direita sem acesso por rolagem adequada
- a causa principal estava na combinacao de larguras estruturais baseadas em `100vw` com padding/box model do shell, o que podia empurrar o layout alem da area util visivel
- `financeiro/base.html` foi ajustado para usar `width: ... 100%` nos wrappers principais, reforcar `max-width: 100%` e `min-width: 0` no miolo do shell e deixar a area principal com `overflow-x: auto` quando necessario
- a validacao local confirmou status `200` para home, listagem, formulario, auditoria, extrato, resumo, prestacao de contas e edicao coordenada do grupo rateado apos essa correcao, e o HTML renderizado confirmou a presenca dos novos pontos estruturais de largura e scroll

## Sidebar recolhivel no desktop do financeiro

- `financeiro/base.html` passou a oferecer controle explicito para recolher e expandir a sidebar no desktop, sem alterar a arquitetura ja consolidada do shell
- a area principal agora convive com dois estados laterais no desktop, `expandido` e `recolhido`, ganhando largura util quando a navegacao e compactada
- o estado ativo da navegacao continua perceptivel no modo recolhido e o comportamento mobile permaneceu separado, ainda em drawer/offcanvas
- a preferencia de recolher ou expandir a sidebar passou a ser persistida no navegador por `localStorage`
- a validacao local confirmou status `200` para home, listagem, formulario, auditoria, extrato, resumo, prestacao de contas e edicao coordenada do grupo rateado apos essa microetapa

## Correcao do modo recolhido da sidebar no desktop

- o modo recolhido da sidebar deixou de operar como mini-menu compacto e passou a recolher o menu lateral de verdade no desktop
- no estado recolhido, a coluna lateral vai a zero no shell principal e grupos, links, abreviacoes e submenus deixam de permanecer visiveis ou espremidos
- a reabertura passou a ficar em botao fixo no desktop, com icone de tres traços e acessibilidade por `title` e `aria-label`
- a area principal passa a aproveitar de forma mais evidente a largura liberada quando a sidebar esta recolhida
- a validacao local confirmou `py manage.py check`, `py -m compileall financeiro casa_espirita` e status `200` nas telas centrais do modulo apos essa correcao

## Correcao da impressao do extrato e limpeza visual do toggle lateral

- foi corrigida uma regressao de print/PDF do extrato em que a pagina podia sair espremida a esquerda por heranca indevida do shell com sidebar
- a solucao isolou o extrato do grid principal no modo impressao, removendo a influencia de wrappers de largura, overflow e da coluna lateral na composicao impressa
- `conta_extrato.html` tambem passou a reforcar no proprio print a ocupacao integral da largura util da pagina e o uso de `overflow: visible`
- o toggle da lateral no desktop deixou de exibir texto permanente e passou a usar apenas icone visivel, mantendo acessibilidade por `aria-label`, `title` e texto reservado a leitor de tela
- a validacao local confirmou status `200` para home e extrato apos o ajuste e confirmou no HTML renderizado os novos marcadores estruturais de print e acessibilidade do toggle

## Impressao de resumo e prestacao de contas, com simplificacao visual das categorias

- `resumo.html` e `prestacao_contas.html` passaram a oferecer acao lateral de `Imprimir` no topo da tela, sem alterar calculos, agrupamentos ou filtros
- a impressao desses relatorios continua usando o isolamento de print do shell compartilhado, mantendo sidebar, topbar, drawer e controles fora da versao impressa
- `CategoriaFinanceira` passou a usar exibicao curta por padrao no modulo, retornando apenas `nome` na representacao visual comum
- a natureza `Receita` / `Despesa` continua compreensivel pelo contexto da tela, pelos blocos separados de relatorio e pelos badges ou colunas de tipo ja existentes nas telas operacionais
- a etapa reduziu ruido textual em relatorios, autocomplete, historico operacional e opcoes de rateio, evitando prefixos longos como `Receita - ...` e `Despesa - ...` quando eles eram redundantes

## Conciliacao documental completa deste ciclo

- foi feita revisao cirurgica dos documentos-base para reconciliar o historico deste chat com o estado real do repositorio e com as decisoes ja aprovadas
- `docs/CEREBRO_PROJETO.md` deixou de tratar a sidebar do `financeiro` como apenas futura e passou a registrar essa navegacao lateral como referencia inicial ja implementada no shell do modulo
- `docs/STATE.md` foi ajustado para refletir corretamente o drawer mobile ja funcional, a referencia do shell lateral do `financeiro` dentro da governanca visual e a pendencia atual de validacao manual fina do print real de `Resumo` e `Prestacao de Contas`
- `docs/ROADMAP_FINANCEIRO.md` recebeu backlog futuro ainda nao executado para: refinamento final do shell/sidebar por uso real, padronizacao futura de margens em relatorios impressos, evolucao futura da logica de assinaturas em relatorios e revisao futura das mensagens visiveis ao usuario dentro do modulo
- `docs/CEREBRO_PROJETO.md` tambem passou a registrar como frente futura transversal o mapeamento e a revisao de todas as mensagens visiveis ao usuario
- esta microetapa foi exclusivamente documental e nao executou patch de codigo

## Reposicionamento do botao de reabrir e unificacao do scroll do shell

- `financeiro/base.html` foi ajustado para tirar o botao de reabrir a sidebar da faixa do conteudo e encaixa-lo na barra utilitaria superior do shell, em posicao estavel e sem sobreposicao de titulo, subtitulo, filtros ou tabelas
- no desktop recolhido, a reabertura continua acessivel por icone apenas, com `title`, `aria-label` e texto reservado a leitor de tela, mas agora usa o mesmo vocabulario visual utilitario do shell
- a causa mais provavel da dupla barra de rolagem era a concorrencia entre a rolagem principal da pagina e o `overflow-y: auto` mantido pela navegacao lateral no desktop
- a correcao removeu essa disputa no desktop, deixando a sidebar sem scrollbar vertical proprio nessa faixa e concentrando a rolagem principal no fluxo normal da pagina
- a validacao local confirmou `py manage.py check`, `py -m compileall financeiro casa_espirita` e status `200` em home, lancamentos, formulario, auditoria, extratos, resumo e prestacao de contas apos o ajuste

## Sigla dinamica do shell e padronizacao fina do toggle lateral

- a sigla visual do shell do `financeiro` deixou de ficar hardcoded em `CE` no template base
- foi criado contexto compartilhado para expor nome institucional e iniciais dinamicas a partir da `ConfiguracaoInstitucional` ativa/padrao, com fallback seguro para `Casa Espirita` e para a sigla `CE`
- a regra de iniciais passou a priorizar as duas primeiras palavras relevantes do nome institucional, ignorando conectivos simples como `de`, `da` e `do`
- o `base.html` passou a usar essas iniciais dinamicas tanto no desktop quanto no mobile, sem alterar a navegacao nem a regra de negocio do modulo
- os controles de recolher e reabrir a lateral no desktop tambem receberam alinhamento visual fino para compartilhar melhor o mesmo padrao de borda, dimensao, sombra e peso discreto
- a validacao local confirmou `py manage.py check`, `py -m compileall financeiro casa_espirita` e status `200` nas telas centrais do modulo apos a mudanca

## Unificacao do controle da lateral em slot unico do shell

- o `base.html` deixou de manter um botao de recolher dentro da propria sidebar e outro botao de reabrir em slot separado
- no desktop, o controle da lateral passou a existir apenas em um unico slot fixo da barra utilitaria, ao lado da marca do modulo
- o mesmo botao agora recolhe a lateral quando ela esta expandida e expande a lateral quando ela esta recolhida, sem trocar de lado nem quebrar o padrao visual do shell
- o comportamento manteve icone sem texto visivel permanente, com `title`, `aria-label` e texto para leitor de tela
- a validacao local confirmou `py manage.py check`, `py -m compileall financeiro casa_espirita` e status `200` em home, lancamentos, formulario, auditoria, extratos, resumo e prestacao de contas apos essa unificacao

## Preparacao estrutural do shell para a futura sidebar do financeiro

- `financeiro/base.html` passou a usar wrappers explicitos de app shell, com area utilitaria superior, area estrutural de sidebar e area principal de conteudo
- a topbar atual foi preservada em convivio controlado como navegacao principal durante a transicao, sem migracao abrupta das telas ja estabilizadas
- a sidebar entrou apenas como base estrutural e secundaria no desktop, preparando a proxima microetapa da navegacao lateral sem substituir ainda a navegacao atual
- o `financeiro-page-header` das paginas foi mantido como camada contextual interna, separado da navegacao do shell
- a validacao tecnica local confirmou status `200` nas telas centrais do modulo apos essa mudanca estrutural, incluindo listagem, formulario, auditoria, extrato, resumo, prestacao e rateio coordenado

## Validacao pratica e estabilizacao da primeira onda visual do financeiro

- foi executada validacao tecnica local com `py manage.py check`, `py -m compileall financeiro casa_espirita` e requests via `Client(HTTP_HOST='localhost')` para as telas centrais do modulo
- `lancamento_list`, `lancamento_form`, `auditoria_lancamento_list`, `conta_extrato`, `resumo`, `prestacao_contas`, `lancamento_rateio_grupo_form` e `lancamento_recibo` responderam com status `200` na validacao local
- durante essa validacao apareceu uma regressao real na abertura da edicao coordenada do grupo rateado: o formulario especializado tentava acessar `self.fields['categoria']`, embora essa tela trabalhe o rateio por payload e nao tenha esse campo no `Meta.fields`
- a estabilizacao ficou restrita a remover esse acesso indevido no `LancamentoFinanceiroGrupoRateioForm`, preservando o fluxo especializado do grupo e sem alterar regra de negocio
- a validacao automatizada confirmou estabilidade tecnica da primeira onda visual no nivel da aplicacao; a validacao manual fina de browser e impressao real continua como verificacao complementar recomendada fora desta etapa

## Fechamento da primeira onda visual nas telas de relatorio operacional

- `conta_extrato.html`, `resumo.html` e `prestacao_contas.html` passaram a conversar com o mesmo shell visual compartilhado do `financeiro`, especialmente no topo, subtitulo, acoes laterais e hierarquia dos blocos principais
- o resumo consolidado passou a usar um bloco principal mais coerente com os componentes-base compartilhados, sem alterar totais, agrupamentos ou filtros
- o extrato e a prestacao de contas mantiveram suas particularidades operacionais e de impressao, mas ficaram mais alinhados ao mesmo vocabulário estrutural do modulo
- sidebar ou menu lateral ainda nao foram implementados nesta microetapa

## Fechamento da primeira onda visual na tela coordenada do grupo rateado

- `lancamento_rateio_grupo_form.html` passou a usar header/topo mais alinhado ao shell compartilhado do `financeiro`, com subtitulo operacional e acoes laterais coerentes com o restante do modulo
- a navegacao de apoio da tela coordenada ficou mais integrada ao mesmo vocabulário visual ja adotado nas demais telas centrais, sem alterar a logica nem a experiencia especializada do rateio
- com essa microetapa, a primeira onda de padronizacao visual do `financeiro` foi fechada nas telas operacionais centrais
- sidebar ou menu lateral ainda nao foram implementados nesta microetapa

## Ajuste de margens da tela e dos relatorios do financeiro

- `financeiro/base.html` passou a usar respiro lateral mais explicito no shell compartilhado, tanto na barra utilitaria quanto na area principal de conteudo, melhorando a leitura em tela sem perder densidade operacional
- o shell tambem passou a centralizar variaveis proprias para margem de impressao e pequeno respiro interno dos relatorios impressos
- `conta_extrato.html`, `resumo.html` e `prestacao_contas.html` passaram a usar wrappers de folha mais explicitos para o modo print, mantendo o isolamento do shell e evitando que o conteudo fique colado nas bordas da pagina
- a impressao de Extrato, Resumo e Prestacao de Contas agora compartilha margem de pagina mais consistente e pequeno respiro interno padronizado, sem reintroduzir heranca indevida de sidebar, topbar ou wrappers de overflow
- a validacao local confirmou `py manage.py check`, `py -m compileall financeiro casa_espirita` e status `200` para `/financeiro/`, `/financeiro/extratos/`, `/financeiro/resumo/` e `/financeiro/prestacao-contas/` apos a microetapa

## Auditoria final de lacunas documentais deste ciclo

- foi feita revisao final entre este chat e os documentos-base para confirmar que pedidos futuros, sugestoes aprovadas e limitacoes atuais relevantes nao ficassem fora da documentacao
- foi ampliado o registro da validacao manual pendente de impressao real para cobrir explicitamente `Extrato`, `Resumo` e `Prestacao de Contas`
- o backlog futuro do `financeiro` passou a registrar de forma explicita a possivel exibicao controlada de logo institucional nos relatorios
- o backlog futuro do `financeiro` tambem passou a registrar um item informativo futuro com simbolo `i` na tela de lancamentos, associado a historico de cadastro/alteracoes do documento ou lancamento
- esta microetapa foi exclusivamente documental e nao executou patch de codigo

## Microetapa documental sobre frente estrutural de usuarios e permissoes

- foi registrada em `docs/CEREBRO_PROJETO.md` a diretriz estrutural futura de usuarios, autenticacao, perfis e permissoes como frente transversal do projeto, sem tratar o tema como ajuste isolado do `financeiro`
- foi registrado em `docs/CEREBRO_PROJETO.md` que a evolucao futura deve prever separacao entre administracao global do sistema e camadas especificas dos modulos, alem da possibilidade de unificacao futura de entidades compartilhadas como base comum de pessoas
- foi registrado em `docs/ROADMAP_FINANCEIRO.md` apenas o impacto futuro do `financeiro` nessa frente, cobrindo integracao por usuario, permissoes por acao e convivencia com administracao global centralizada
- foi registrado em `docs/STATE.md` apenas que essa frente estrutural futura esta oficialmente aberta em nivel documental, sem implementacao marcada
- esta microetapa foi exclusivamente documental e nao implementou login, usuarios, perfis, permissao ou qualquer outra regra nova no codigo

## Organizacao documental da fila restante

- foi reorganizada em `docs/ROADMAP_FINANCEIRO.md` a fila pratica restante por grupos de prioridade, sem apagar nem substituir as secoes semanticas ja existentes de backlog
- a reorganizacao passou a distinguir explicitamente faixas como `Imediato`, `Proximo`, `Posterior`, `Estrutural futura` e `Experimental`, preservando o backlog anterior e a sequencia linear historica
- foi acrescentado em `docs/ROADMAP_FINANCEIRO.md` o registro explicito da validacao manual real de impressao de `Extrato`, `Resumo` e `Prestacao de Contas`
- foi acrescentado em `docs/ROADMAP_FINANCEIRO.md` o registro explicito da POC controlada de uso de template pronto no shell do `financeiro`
- a organizacao desta etapa foi exclusivamente documental e nao implementou codigo nem removeu qualquer item ja registrado

## Validacao manual real da impressao dos relatorios principais

- foi executada validacao visual real da impressao de `Extrato`, `Resumo` e `Prestacao de Contas` usando navegador/PDF real sobre a base atual do projeto
- o `Extrato` confirmou largura util adequada, ausencia de vestigio indevido do shell administrativo e leitura impressa coerente para a tabela e para o cabecalho proprio de impressao
- o `Resumo` confirmou margens adequadas, boa distribuicao do conteudo na folha e ausencia de heranca indevida de sidebar, topbar ou drawer na saida de impressao
- a `Prestacao de Contas` confirmou composicao formal adequada, boa leitura documental na folha e ausencia de heranca indevida do shell na saida de impressao
- nesta microetapa nao foi necessario aplicar patch de codigo, porque a validacao real nao encontrou regressao visual que justificasse correcao adicional
- `docs/STATE.md` passou a registrar o encerramento dessa pendencia e `docs/ROADMAP_FINANCEIRO.md` deixou de tratar essa validacao e o refinamento fino das margens como backlog aberto nesta base atual

## Refinamento documental de impressao/PDF dos relatorios principais

- `financeiro/templates/financeiro/base.html` passou a concentrar um vocabulario visual documental compartilhado para impressao/PDF dos relatorios do `financeiro`, incluindo cabecalho comum, metadados em cards, hierarquia tipografica e assinatura final mais formal para a prestacao
- `financeiro/templates/financeiro/conta_extrato.html` passou a usar esse padrao no modo documental, deixando o `Extrato` menos parecido com uma tabela tecnica impressa e mais com um documento final por conta
- `financeiro/templates/financeiro/resumo.html` passou a usar o mesmo padrao no topo de impressao, com cabecalho institucional leve, metadados do periodo e bloco inicial mais coerente com um relatorio consolidado final
- `financeiro/templates/financeiro/prestacao_contas.html` passou a usar cabecalho documental mais consistente e bloco final de assinatura menos cru, sem antecipar logo institucional nem a futura frente de multiplas assinaturas
- nesta microetapa nao houve alteracao de regra de negocio, calculos, filtros, agrupamentos nem conteudo funcional dos relatorios
- foi possivel executar `py manage.py check`, validar localmente as rotas centrais dos relatorios com status `200` e gerar PDFs reais dos tres documentos em `tmp/print-validation/`

## Refinamento institucional de cabecalho, margens e extrato

- `financeiro/context_processors.py` passou a expor tambem `financeiro_shell_brand_logo_url` a partir da `ConfiguracaoInstitucional` ativa/padrao, para uso institucional correto nos relatorios
- `financeiro/templates/financeiro/base.html` deixou de tratar sigla como elemento visual de relatorio e passou a preparar o cabecalho documental para usar logo quando existir, com fallback apenas para o nome institucional
- as margens de impressao e o respiro interno foram reforcados no padrao compartilhado de print/PDF dos relatorios
- `financeiro/templates/financeiro/conta_extrato.html` tambem recebeu ajuste especifico de densidade e distribuicao de colunas no print para aproveitar melhor a folha sem perder legibilidade
- `financeiro/templates/financeiro/resumo.html` e `financeiro/templates/financeiro/prestacao_contas.html` foram alinhados a essa mesma logica de identidade institucional sem pseudo-logo
- nesta microetapa nao houve alteracao de regra de negocio, calculos, filtros nem conteudo funcional dos relatorios
- foi possivel executar `py manage.py check`, validar novamente as rotas dos relatorios com status `200` e regenerar PDFs reais atualizados em `tmp/print-validation/`

## Refinamento documental do recibo e da leitura do saldo acumulado

- `financeiro/templates/financeiro/lancamento_recibo.html` foi refinado para parecer mais documento final e menos cartao administrativo, com topo mais centrado, `RECIBO` como titulo principal, numero em linha secundaria mais limpa e valor destacado sem redundancia de data no topo
- no recibo, a logo ganhou mais presenca visual e o nome institucional deixou de ser repetido ao lado dela quando a logo esta presente; o nome agora fica como fallback discreto quando nao ha logo utilizavel
- a mensagem principal do recibo ganhou bloco central com mais protagonismo documental e o fechamento passou a soar mais formal
- `financeiro/templates/financeiro/base.html` passou a oferecer classes de leitura visual para o `saldo acumulado` do extrato
- `financeiro/templates/financeiro/conta_extrato.html` passou a aplicar ao `saldo acumulado` a logica visual de cor por sinal: positivo, negativo ou neutro
- nesta microetapa nao houve alteracao de regra de negocio, calculos, filtros nem conteudo funcional de recibo ou extrato
- foi possivel executar `py manage.py check`, validar localmente `/financeiro/lancamentos/1/recibo/` e `/financeiro/extratos/?conta=3` com status `200` e gerar PDFs reais atualizados em `tmp/print-validation/`

## Reforco perceptivel de margens, bordas e identidade documental

- `financeiro/templates/financeiro/base.html` recebeu novo reforco no padrao compartilhado de print com margens de pagina mais abertas, aumento do respiro interno e quadro documental mais explicito para os relatorios impressos
- `financeiro/templates/financeiro/conta_extrato.html`, `financeiro/templates/financeiro/resumo.html` e `financeiro/templates/financeiro/prestacao_contas.html` foram alinhados para evitar repeticao desnecessaria do nome institucional quando a logo ja esta presente no cabecalho
- `financeiro/templates/financeiro/lancamento_recibo.html` recebeu reforco visual adicional de borda, topo e respiro para ficar mais institucional e menos parecido com um bloco administrativo simples
- nesta mesma etapa foi registrada, apenas em nivel documental, a futura frente de configuracao da paleta geral do sistema com derivacao coerente a partir de uma cor principal
- nesta mesma etapa tambem foram registrados, apenas em nivel documental, o futuro log de acesso ao sistema e a revisao futura da posicao do `Extrato` na navegacao
- nesta microetapa nao houve alteracao de regra de negocio, calculos, filtros, agrupamentos nem conteudo funcional
- foi possivel executar `py manage.py check`, validar as rotas de recibo e relatorios com status `200` e gerar novamente PDFs reais atualizados em `tmp/print-validation/`

## Ajuste visual cirurgico do saldo acumulado no extrato

- `financeiro/templates/financeiro/base.html` recebeu ajuste fino para remover o negrito do `saldo acumulado` no extrato
- o `saldo acumulado` manteve a leitura visual por sinal, usando cor para positivo, negativo e neutro
- `saldo inicial` e `saldo final` permanecem como linhas destacadas em negrito no corpo do extrato
- nesta microetapa nao houve alteracao de calculo, regra de negocio, logica funcional nem abertura de frente nova

## Refinamento documental focado do Extrato

- `financeiro/templates/financeiro/conta_extrato.html` teve o cabecalho documental simplificado para a versao impressa, com retirada de texto instrutivo e remocao do `saldo anterior` da faixa superior de metadados
- `financeiro/templates/financeiro/base.html` recebeu ajuste especifico para o `Extrato` impresso, aumentando perceptivelmente a margem superior util, reduzindo o peso visual do topo e deixando o quadro documental menos carregado
- a tabela do `Extrato` ganhou cabeÃ§alho com mais respiro, zebra leve no corpo e separacao visual mais clara entre `saldo acumulado` e `observacoes`
- o `saldo acumulado` permaneceu sem negrito e com leitura por cor conforme o sinal do valor
- nesta microetapa nao houve alteracao de calculo, filtros, agrupamentos, conteudo funcional nem regra de negocio
- foi possivel executar `py manage.py check`, validar a rota `/financeiro/extratos/?conta=3` com status `200` e gerar PDF real atualizado em `tmp/print-validation/extrato-v5.pdf`

## Fechamento visual do Extrato impresso

- `financeiro/templates/financeiro/conta_extrato.html` passou a usar cabecalho impresso ainda mais simples, com titulo curto, linha unica de metadados documentais e rotulos abreviados no print para reduzir peso visual
- `financeiro/templates/financeiro/base.html` recebeu alivio adicional no modo print do `Extrato`, com menos moldura, tipografia mais fina, bordas mais discretas, zebra mais suave e melhor distribuicao horizontal das colunas
- a composicao do extrato impresso ficou mais proxima de um extrato bancario leve do que de uma tabela tecnica, especialmente no topo, no cabecalho da tabela e na separacao entre `Favorecido`, `Tipo`, `Saldo` e `Obs.`
- o `saldo acumulado` foi preservado com cor por sinal e sem negrito, enquanto `saldo inicial` e `saldo final` continuaram destacados
- nesta microetapa nao houve alteracao de calculo, filtros, agrupamentos, conteudo funcional nem regra de negocio
- foi possivel executar `py manage.py check`, validar novamente `/financeiro/extratos/?conta=3` com status `200` e gerar PDF real atualizado em `tmp/print-validation/extrato-v6.pdf`

## Ajuste fino final de data e grade do Extrato impresso

- `financeiro/templates/financeiro/conta_extrato.html` passou a padronizar o periodo do cabecalho impresso em `dd/mm/aaaa`, sem alterar a estrutura funcional do extrato nem o comportamento dos filtros
- `financeiro/templates/financeiro/base.html` recebeu alivio final da grade do print do `Extrato`, removendo divisorias verticais e afinando ainda mais as linhas horizontais para leitura mais leve e documental
- o `saldo acumulado` foi preservado com cor por sinal e sem negrito, enquanto `saldo inicial` e `saldo final` continuaram destacados
- nesta microetapa nao houve alteracao de regra de negocio, calculos, filtros, agrupamentos nem conteudo funcional
- foi possivel executar `py manage.py check` e validar novamente `/financeiro/extratos/?conta=3` com status `200`

## Ajuste final de cabecalho institucional e linhas do Extrato impresso

- `financeiro/templates/financeiro/conta_extrato.html` deixou de usar logo institucional no cabecalho impresso do `Extrato` e passou a exibir apenas o nome da instituicao cadastrada, em negrito e com leitura documental limpa
- `financeiro/templates/financeiro/base.html` recebeu ajuste fino adicional para afinar ainda mais as linhas horizontais da tabela do `Extrato`, mantendo a ausencia de divisorias verticais
- o cabecalho preservou hierarquia visual leve e o `saldo acumulado` continuou com cor por sinal e sem negrito, sem alterar `saldo inicial` e `saldo final`
- nesta microetapa nao houve alteracao de regra de negocio, calculos, filtros, agrupamentos nem conteudo funcional
- foi possivel executar `py manage.py check` e validar novamente `/financeiro/extratos/?conta=3` com status `200`

## Encerramento do ciclo visual do Extrato impresso

- a validacao humana final aprovou o acabamento atual do `Extrato` impresso nesta branch
- com isso, o ciclo visual do `Extrato` pode ser tratado como encerrado no estado atual do repositorio, sem necessidade de novo ajuste funcional ou documental amplo
- qualquer evolucao posterior sobre esse relatorio deve ser tratada apenas como curadoria incremental por uso real, e nao como reabertura da frente principal de acabamento visual

## Refinamento da experiencia da edicao coordenada do grupo rateado

- `financeiro/templates/financeiro/lancamento_rateio_grupo_form.html` foi reorganizado para deixar mais clara a hierarquia entre resumo do grupo, dados comuns do documento, linhas do rateio e acoes finais
- a tela passou a usar textos mais curtos e operacionais, reduzindo redundancias e reforcando de forma mais previsivel que salvar atualiza o grupo inteiro
- os retornos para a listagem e para a linha representativa ficaram mais explicitos como saidas de navegacao, sem competir visualmente com a acao principal de salvar
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, transacao de salvamento, calculos nem integracao com `grupo_rateio`
- foi possivel executar `py manage.py check` e validar a rota real de edicao coordenada `/financeiro/lancamentos/rateio/dea3341ddf044d799a792e810bed7d52/editar/` com status `200`

## Microcorrecao visual adicional da grade do Extrato impresso

- `financeiro/templates/financeiro/base.html` recebeu um ajuste fino adicional apenas no print do `Extrato` para aproximar a tabela da grade visual mais leve usada como referencia em telas operacionais do modulo
- o cabecalho da tabela passou a ficar sem linha visivel no print, com tipografia um pouco mais leve e sem reintroduzir divisorias verticais
- o corpo da tabela passou a usar apenas linhas horizontais ainda mais finas e zebra mais suave, preservando leitura limpa e documental
- foram preservados o nome institucional no topo, o periodo em `dd/mm/aaaa`, o `saldo acumulado` com cor por sinal e sem negrito, e o destaque de `saldo inicial` / `saldo final`
- nesta microetapa nao houve alteracao de regra de negocio, calculos, filtros, estrutura funcional nem reabertura da frente principal do `Extrato`

## Refinamento da leitura operacional do grupo rateado fora da tela coordenada

- `financeiro/templates/financeiro/lancamento_list.html` passou a sinalizar de forma mais explicita quando a linha pertence a um grupo rateado, deixando mais claro que a acao `Editar` abre a edicao coordenada do grupo inteiro
- `financeiro/templates/financeiro/lancamento_form.html` passou a tratar a edicao individual de linha rateada com bloco mais operacional, diferenciando melhor a revisao da linha isolada do caminho para o grupo inteiro
- os retornos entre listagem, linha individual e grupo coordenado passaram a depender menos de texto corrido e mais de leitura operacional curta com acoes claras
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, calculos, salvamento transacional nem integracao com `grupo_rateio`

## Refinamento da entrada do rateio no formulario principal

- `financeiro/templates/financeiro/lancamento_form.html` passou a diferenciar melhor, logo na entrada da tela, o fluxo de lancamento comum e o fluxo com `Lancamento com rateio`
- a tela passou a organizar melhor o que pertence aos dados comuns do documento, o que pertence ao `valor total do documento` e o que pertence as linhas do rateio, reduzindo ruido textual e deixando a transicao para o bloco de rateio menos mecanica
- a linguagem usada no create simples foi aproximada da leitura operacional ja consolidada na edicao coordenada do grupo, sem alterar a mecanica do formulario
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, calculos, `grupo_rateio`, `numero_documento` compartilhado nem payload JS do rateio
- foi possivel executar `py manage.py check` e validar a rota real de criacao `/financeiro/lancamentos/novo/` com status `200`, confirmando tambem no HTML renderizado a presenca dos blocos `Lancamento com rateio`, `Ativar rateio deste documento` e `Rateio simples`

## Enxugamento textual inicial do formulario principal de lancamento

- `financeiro/templates/financeiro/lancamento_form.html` teve reducao cirurgica de textos explicativos no subtitulo da pagina e nos blocos ligados ao `rateio`, mantendo apenas a orientacao realmente util para a acao
- o ajuste concentrou-se no bloco `Modo do lancamento`, no callout de `valor total do documento` e na introducao do bloco `Rateio simples`, trocando frases mais longas por rotulagem operacional mais curta
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem comportamento do formulario
- foi possivel executar `py manage.py check` e validar novamente a rota `/financeiro/lancamentos/novo/` com status `200`, confirmando no HTML renderizado a presenca dos textos enxugados dessa etapa

## Enxugamento textual mais incisivo do bloco de rateio no formulario principal

- `financeiro/templates/financeiro/lancamento_form.html` reduziu ainda mais o texto fixo da entrada do `rateio`, cortando explicacoes que a propria estrutura da tela ja comunicava
- os cards comparativos da abertura do rateio foram simplificados de forma forte, a orientacao fixa ficou mais seca e a ajuda excepcional foi concentrada em poucos icones `i` discretos com `title`
- o ajuste ficou focado no bloco `Modo do lancamento`, no toggle `Lancamento com rateio`, no `valor total do documento` e na introducao das linhas do rateio
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem comportamento do formulario
- foi possivel executar `py manage.py check` e validar novamente `/financeiro/lancamentos/novo/` com status `200`, confirmando no HTML renderizado a presenca do novo texto minimo e do apoio discreto via `i`

## Faxina fina de comunicacao no formulario principal de lancamento

- `financeiro/templates/financeiro/lancamento_form.html` removeu descricoes de secao redundantes em `Dados principais`, `Valores e datas` e `Informacoes complementares`
- o bloco `Modo do lancamento` ficou mais leve, perdeu elementos decorativos sem funcao real e manteve apenas o toggle com ajuda discreta realmente necessaria
- o bloco `Valor total do documento` deixou de repetir semanticamente titulo e explicacao fixa, mantendo apenas rotulo direto e ajuda curta por `i`
- a abertura de `Linhas do rateio` perdeu camadas redundantes de titulo e textos que repetiam o que a propria tabela ja mostra
- a tela tambem passou a padronizar melhor rotulos e acentuacao visiveis, incluindo `Lançamento`, `Informações`, `Últimos`, `Ação` e `Número do documento`
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem comportamento do formulario
- foi possivel executar `py manage.py check` e validar novamente `/financeiro/lancamentos/novo/` com status `200`

## Expansao controlada da listagem de categorias

- `financeiro/templates/financeiro/categoria_list.html` recebeu a proxima expansao controlada da frente transversal, seguindo a ordem estrutural ja formalizada: primeiro decisao de shell/topo, depois refinamento do corpo
- nessa tela, a solucao correta foi sobrescrever o `financeiro_shell_header` com versao enxuta, mantendo a sidebar como navegacao principal e evitando a sensacao de shell antigo sobre corpo novo
- o conteudo local passou a usar page header mais limpo, bloco de filtros mais maduro e tabela mais coerente com o shell atual, sem alterar urls, filtros, links, acoes nem comportamento funcional da listagem
- a leitura de `Categoria pai`, `Ativo` e `Acoes` ficou mais clara, a acentuacao visivel deixou de carregar quebra de encoding e o estado vazio passou a ficar mais operacional

## Expansao controlada da listagem de contas

- `financeiro/templates/financeiro/conta_list.html` recebeu a expansao controlada seguinte da frente transversal, repetindo a ordem estrutural aprovada: primeiro override enxuto do `financeiro_shell_header`, depois consolidacao do corpo da listagem
- nessa tela, a sidebar foi preservada como navegacao principal e o topo deixou de competir com o conteudo, usando header enxuto com `Navegacao` no desktop e `Menu` no mobile
- o conteudo local passou a usar page header mais limpo, filtros mais maduros e tabela mais coerente com o shell atual, sem alterar urls, filtros, links, acoes nem comportamento funcional da listagem
- a leitura de `Descricao`, `Saldo inicial`, `Saldo atual (quitado)`, `Ativa` e `Acoes` ficou mais clara, com melhor hierarquia visual de valores e correcao dos microtextos visiveis

## Expansao controlada da listagem de pessoas

- `financeiro/templates/financeiro/pessoa_list.html` recebeu a expansao controlada seguinte da frente transversal, repetindo a ordem estrutural aprovada: primeiro override enxuto do `financeiro_shell_header`, depois refinamento do corpo da listagem
- nessa tela, a sidebar foi preservada como navegacao principal e o topo deixou de competir com o conteudo, usando header enxuto com `Navegacao` no desktop e `Menu` no mobile
- o conteudo local passou a usar page header mais limpo, filtros mais maduros e tabela mais coerente com o shell atual, sem alterar urls, filtros, links, acoes nem comportamento funcional da listagem
- a leitura de `Tipo pessoa`, `Documento`, `Telefone`, `E-mail`, `Ativo` e `Acoes` ficou mais clara, com correcao dos microtextos visiveis e estado vazio mais operacional

## Expansao controlada do formulario de centro de custo

- `financeiro/templates/financeiro/centro_custo_form.html` recebeu a expansao controlada seguinte da frente transversal, repetindo a ordem estrutural aprovada: primeiro override enxuto do `financeiro_shell_header`, depois refinamento do corpo do formulario
- nessa tela, a sidebar foi preservada como navegacao principal e o topo deixou de competir com o conteudo, usando header enxuto com `Navegacao` no desktop e `Menu` no mobile
- o conteudo local passou a usar page header mais limpo, card unico de formulario, agrupamento visual mais maduro dos campos e bloco de acoes mais coerente, sem alterar campos, validacoes, envio nem comportamento funcional
- a leitura de `help_text`, erros de campo e erros gerais ficou mais limpa, mantendo a simplicidade do formulario e sem introduzir explicacoes desnecessarias
 
## Correcao responsiva do controle de navegacao na tela piloto

- a auditoria humana mostrou que `Navegacao` e `Menu` ainda podiam aparecer juntos no topo de `financeiro/templates/financeiro/lancamento_form.html`, porque o header local da tela piloto renderizava os dois controles e dependia apenas da separacao responsiva herdada do shell
- a correcao foi mantida estritamente no template da tela piloto, com classes locais e breakpoints explicitos para garantir que o desktop exiba apenas `Navegacao` e o mobile exiba apenas `Menu`
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos, linha financeira nem ordem dos blocos do formulario

## Primeira expansao controlada da frente transversal em listagem auxiliar

- `financeiro/templates/financeiro/centro_custo_list.html` foi escolhida como primeira expansao controlada fora da tela piloto por ser a listagem auxiliar mais simples do grupo e permitir reaproveitar o padrao validado com menor risco
- a tela passou a usar `page header` limpo e coerente com o shell atual, bloco de filtros mais maduro, tabela alinhada ao padrao visual do modulo e linguagem visivel corrigida em acentuacao e microtextos
- o estado vazio deixou de soar como cadastro cru e passou a responder de forma mais operacional aos filtros atuais, sem criar explicacoes extras nem alterar URLs, acoes ou comportamento funcional da listagem

## Consolidacao estrutural da listagem de centros de custo

- a auditoria humana posterior mostrou que a tela ainda parecia parcialmente aplicada: o header tinha melhorado, mas filtros e tabela continuavam visivelmente soltos dentro do shell, reforcando sensacao hibrida entre padrao antigo e padrao novo
- a consolidacao seguinte ficou restrita a `financeiro/templates/financeiro/centro_custo_list.html`, reunindo filtros e tabela em um unico card/listagem e removendo a dependencia de rolagem local no bloco da tabela para evitar scrollbar interna indevida nessa tela simples
- a etapa preservou titulo, botao `Novo centro de custo`, filtros existentes, acoes da tabela, estado vazio operacional e microtextos corrigidos, sem alterar regra de negocio nem abrir refinamento paralelo nas demais telas auxiliares

## Alinhamento do topo da listagem de centros de custo com o shell aprovado

- a auditoria humana seguinte mostrou que o corpo da listagem tinha melhorado, mas a barra superior ainda continuava herdando o padrao antigo completo do shell, deixando topo e menu visualmente desalinhados em relacao ao padrao aprovado na tela piloto
- a correcao ficou restrita a `financeiro/templates/financeiro/centro_custo_list.html`, que passou a sobrescrever apenas o `financeiro_shell_header` com a mesma logica de header enxuto ja validada na POC: `Navegacao` no desktop e `Menu` no mobile, sem reabrir a faixa antiga de contexto no topo
- o corpo ja consolidado da listagem foi preservado integralmente, incluindo page header, botao principal, filtros, tabela, chip de `Ativo`, estado vazio operacional e comportamento funcional da tela

## Tentativas manuais de recomposicao visual no formulario principal

- `financeiro/templates/financeiro/lancamento_form.html` recebeu tentativas manuais de recomposicao visual para testar um corpo mais central, mais compacto e organizado por linhas de preenchimento relacionadas, em vez de continuar acumulando apenas microajustes incrementais sobre a composicao antiga
- nessas tentativas, `Descricao` + `Numero do documento`, `Tipo` + `Status` + `Lancamento com rateio`, `Valor` + datas + `Valor total do documento`, `Pessoa` + `Categoria` e `Centro de custo` + `Conta` + `Conta destino` passaram a ser tratados como sequencia operacional unica
- `Observacoes` ficou mais baixa e mais discreta, o rateio passou a continuar o mesmo corpo principal sem cara de tela separada e a faixa de acoes finais foi aproximada do fluxo; o historico da pessoa permaneceu funcional, mas com protagonismo visual reduzido
- essas tentativas manuais nao devem ser tratadas como execucao valida da POC com tema-base real: elas serviram apenas como experimento intermediario para demonstrar que a base atual ja nao respondia bem a novos remendos incrementais
- nessas tentativas nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem comportamento funcional do formulario

## Decisao estrategica sobre a nova base visual do formulario principal

- a avaliacao acumulada desta conversa concluiu que insistir em microajustes incrementais sobre o layout atual de `financeiro/templates/financeiro/lancamento_form.html` passou a gerar retrabalho demais e ganho insuficiente
- por isso, a estrategia aprovada deixa de tentar apenas "imitar" uma base pronta e passa a preferir o uso controlado de um tema gratis real como fundamento da composicao visual
- o tema escolhido como referencia principal para a proxima POC e o **Tabler**
- a POC valida ainda nao foi executada como adocao real de tema-base: ela deve acontecer primeiro apenas em `financeiro/templates/financeiro/lancamento_form.html`, sem expansao para outras telas antes de auditoria visual e funcional posterior
- a futura POC com Tabler deve preservar integralmente regras de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos, comportamento atual do formulario e logica de exibicao/ocultacao do rateio
- se a base do tema resolver de fato a leitura visual da tela, customizacoes pontuais posteriores por cima dela passam a ser aceitaveis; antes disso, o foco correto e validar a base pronta e leve em uma unica tela piloto
- fica registrado para o proximo chat que a microetapa correta seguinte e aplicar uma POC visual controlada com Tabler apenas em `financeiro/templates/financeiro/lancamento_form.html` e depois auditar layout, legibilidade, ativacao de `Lancamento com rateio`, integridade dos campos, JS/payload, navegacao e preservacao do comportamento funcional

## POC Tabler executada no formulario principal

- `financeiro/templates/financeiro/lancamento_form.html` recebeu a primeira execucao real da POC visual com base no **Tabler**, sem espalhar a base do tema para outras telas do modulo
- a tela piloto passou a usar composicao mais central, continua e densa, com cabecalho seco, card principal unico, linhas de preenchimento mais relacionadas e bloco de `rateio` encaixado no mesmo corpo visual
- a execucao preservou os mesmos `{{ form.campo }}`, wrappers condicionais, `data-*`, `rateio_payload`, historico da pessoa, edicao individual de linha rateada e logica atual de exibicao/ocultacao do `rateio`
- foi possivel executar `py manage.py check` com sucesso e validar `/financeiro/lancamentos/novo/` com status `200`, confirmando no HTML renderizado a presenca de `lancamento_com_rateio`, `data-financeiro-rateio-box` e `Numero do documento`
- apesar disso, a etapa ainda depende de auditoria humana visual e funcional propria antes de qualquer continuidade: a expansao da base Tabler para outras telas segue explicitamente bloqueada

## Ajuste cirurgico pos-auditoria da tela piloto

- `financeiro/templates/financeiro/lancamento_form.html` recebeu um ajuste pontual no topo para remover, apenas nessa tela piloto, os controles herdados de menu/recolhimento que estavam visivelmente bons, mas sem funcao real confiavel no contexto da pagina
- a navegacao util da propria tela foi preservada, sem reabrir a frente de shell nem espalhar o tema para outras telas
- a linha dos campos financeiros foi reorganizada para manter a ordem logica do fluxo: sem rateio, o primeiro slot segue como `Valor`; com rateio, esse mesmo slot passa a mostrar `Valor total do documento`, seguido por `Data pagamento` e `Data competencia`, sem deixar o total deslocado depois das datas
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem logica de exibicao/ocultacao do rateio
- a POC continua restrita ao `lancamento_form.html` e ainda depende de auditoria humana visual/funcional propria antes de qualquer expansao

## Limpeza estrutural do topo da tela piloto

- a redundancia do topo deixou de ser tratada como maquiagem local no proprio template: `financeiro/base.html` recebeu pontos de override cirurgicos para os controles de topo do shell, permitindo que a tela piloto remova apenas o que nao deve aparecer nela sem quebrar a navegacao estrutural das demais telas
- em `financeiro/templates/financeiro/lancamento_form.html`, o header local passou a usar apenas a camada de conteudo da pagina, mantendo titulo e acao `Voltar para lancamentos` sem repetir contexto que o shell ja comunica
- com isso, a abertura visual da tela ficou organizada em tres niveis claros: shell do modulo, header de conteudo e formulario
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem comportamento funcional do formulario

## Remocao da segunda faixa redundante do topo

- a redundancia visual restante vinha da propria `financeiro-app-utility-bar` do shell, onde a marca `CE / Financeiro` seguia aparecendo acima do header de conteudo desta tela piloto
- para esta pagina, a solucao final foi neutralizar estruturalmente o `header` utilitario inteiro por heranca de template, em vez de continuar apenas desligando controles internos dele
- com isso, a abertura da tela passou a preservar somente a navegacao estrutural principal do shell e, logo abaixo, o cabecalho de conteudo com `Novo Lancamento Financeiro` e `Voltar para lancamentos`
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem comportamento funcional do formulario

## Reativacao do shell lateral e unificacao do primeiro slot financeiro

- a perda da navegacao lateral visivel nesta tela piloto foi causada pelo override completo de `financeiro_shell_header` em `financeiro/templates/financeiro/lancamento_form.html`, que havia removido junto a faixa estrutural necessaria para os controles do shell
- a correcao passou a reativar nessa mesma tela uma faixa estrutural minima do shell, mantendo o toggle lateral no desktop e o acionamento do drawer no mobile, mas sem reintroduzir a marca `Financeiro` como contexto duplicado antes do header da pagina
- no primeiro slot financeiro, `Valor` e `Valor total do documento` passaram a compartilhar o mesmo container visual e a mesma casca de campo; com isso, quando o rateio e ativado, a troca passa a parecer apenas mudanca de label/campo no mesmo lugar, e nao a entrada de uma caixa visual diferente
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem logica do rateio

## Ajustes cirurgicos finais de menu e ordem do fluxo

- o icone `>` vinha do proprio `financeiro-sidebar-desktop-toggle` do shell compartilhado, que usa pseudo-elemento com chevron para recolher/expandir a lateral; nesta tela piloto, o controle passou a usar um affordance mais coerente com a navegacao lateral do tema, com iconografia de menu em vez de seta isolada
- `Valor total do documento` passou a usar o mesmo padrao visual dos demais campos do slot financeiro, sem reforco indevido de caixa alta nem aparencia de componente diferente
- `Linhas do rateio` foi reposicionado para antes de `Observacoes`, preservando integralmente o mesmo conteudo e a mesma mecanica do bloco
- ao marcar `Lancamento com rateio`, o primeiro slot financeiro agora preserva consistencia de valor inicial: se `Valor` ja nasce com `0,00`, `Valor total do documento` assume esse mesmo valor-base no mesmo lugar visual, sem aparentar reset ou perda de estado
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem logica do rateio

## Compactacao mais incisiva do formulario principal

- `financeiro/templates/financeiro/lancamento_form.html` recebeu uma nova passada de densidade para reduzir de forma mais firme o espaco vertical total e aproximar mais os campos entre si
- os titulos internos passaram a operar mais como separadores discretos do que como seções altas, enquanto a ficha principal reduziu paddings, margens e respiros entre linhas de inputs
- `Modo do lancamento`, `Valores e datas`, `Informacoes complementares`, `Observacoes`, a faixa de acoes finais e o bloco de `rateio` ficaram visualmente mais compactos sem perder legibilidade
- o historico vazio da pessoa ficou ainda mais secundario e mais proximo do restante da tela, sem ganhar protagonismo visual desnecessario
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem comportamento do formulario
- foi possivel executar `py manage.py check` e validar novamente `/financeiro/lancamentos/novo/` com status `200`

## Ajuste de grade e proporcao do formulario principal

- `financeiro/templates/financeiro/lancamento_form.html` recebeu uma passada complementar de proporcao para reduzir a sensacao de campos ilhados e aproximar mais a leitura de uma ficha operacional de lancamento
- as linhas de `Tipo`, `Status` e `Numero do documento`, o bloco de `Valores e datas` e as linhas de complementares passaram a usar distribuicao mais firme de colunas e gaps mais contidos
- `Modo do lancamento`, a area de acoes finais e o historico vazio ficaram menos destacados como faixas independentes e mais encaixados no mesmo fluxo vertical da tela
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem comportamento do formulario
- foi possivel executar `py manage.py check` e validar novamente `/financeiro/lancamentos/novo/` com status `200`

## Ponto de restauracao e abertura documental da POC visual

- antes de abrir uma nova tentativa de salto visual no `lancamento_form.html`, o estado rastreado atual do `financeiro` foi consolidado em commit proprio como ponto de restauracao seguro
- a partir desse marco, a frente seguinte fica enquadrada como POC controlada de tema/base visual pronta e leve, sem expansao imediata para outras telas
- a POC deve comecar somente em `financeiro/templates/financeiro/lancamento_form.html`
- a expansao posterior para outras telas so pode acontecer apos auditoria visual e funcional explicita
- essa auditoria posterior deve verificar layout, legibilidade, ativacao de `Lancamento com rateio`, integridade dos campos, JS/payload, navegacao e preservacao do comportamento funcional
- a abertura da POC nao autoriza mudanca de regra de negocio

## Compactacao espacial do formulario principal

- `financeiro/templates/financeiro/lancamento_form.html` recebeu uma passada especifica de densidade para reduzir espaco em branco e aproximar a experiencia de uma ficha de lancamento mais sequencial
- a ficha principal passou a operar com blocos internos mais proximos entre si, paddings menores e menor distancia entre titulos, linhas de inputs e acoes finais
- o bloco de `rateio`, quando ativado, foi mantido como continuacao natural do formulario, mas agora tambem com respiro mais curto e leitura mais compacta
- o historico da pessoa foi mantido funcional, porem com menos protagonismo visual e menor peso no fluxo principal da tela
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem comportamento do formulario
- foi possivel executar `py manage.py check` e validar novamente `/financeiro/lancamentos/novo/` com status `200`

## Acabamento fino complementar do formulario principal

- `financeiro/templates/financeiro/lancamento_form.html` recebeu um ultimo ajuste fino para deixar o `i` com aparencia mais consolidada em alinhamento, contraste e espacamento, sem proliferar novos pontos de ajuda na tela
- os blocos `Modo do lancamento` e `Valor total do documento` ficaram discretamente mais compactos e leves, preservando a clareza operacional minima
- o estado vazio do historico ficou menos carregado e a linguagem do bloco foi alinhada com o campo principal da tela, passando a tratar o historico como leitura da `pessoa`
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem comportamento do formulario
- foi possivel executar `py manage.py check` e validar novamente `/financeiro/lancamentos/novo/` com status `200`

## Ajuste curtissimo final de rotulagem e icone no formulario principal

- `financeiro/templates/financeiro/lancamento_form.html` manteve a rotulagem visivel de `Valor total do documento` na forma padronizada final e passou a renderizar o icone `i` em italico, sem mudar seu tamanho, alinhamento, contraste ou espacamento
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem comportamento do formulario
- foi possivel executar `py manage.py check` e validar novamente `/financeiro/lancamentos/novo/` com status `200`

## Polimento visual residual do formulario principal

- `financeiro/templates/financeiro/lancamento_form.html` recebeu um polimento curtissimo para dar um pouco mais de legibilidade ao `i`, aliviar o peso visual do bloco `Valor total do documento`, amarrar melhor o botao `Adicionar linha` e dar mais leitura ao `Remover`
- o estado vazio de `Ultimos lancamentos da pessoa` tambem ficou mais discreto, preservando a mesma funcao e sem reintroduzir texto explicativo
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem comportamento do formulario
- foi possivel executar `py manage.py check` e validar novamente `/financeiro/lancamentos/novo/` com status `200`

## Reorganizacao visual do formulario principal para fluxo mais continuo

- `financeiro/templates/financeiro/lancamento_form.html` foi reorganizado para reduzir a sensacao de empilhamento de caixas independentes e se aproximar mais de uma tela unica de inputs de cadastro, com blocos mais leves, compactos e integrados
- o bloco `Valor total do documento` passou a ter leitura mais proxima dos demais campos, sem caixa alta no rotulo visivel, e o rateio deixou de parecer uma tela dentro da tela ao trazer `Adicionar linha` para o cabecalho das `Linhas do rateio`
- `Remover` ganhou um pouco mais de legibilidade e o estado vazio de `Ultimos lancamentos da pessoa` ficou mais leve, sem alterar nenhuma regra, validacao, payload JS ou logica de exibicao/ocultacao do rateio
- foi possivel executar `py manage.py check` e validar novamente `/financeiro/lancamentos/novo/` com status `200`; no HTML renderizado, permaneceram presentes o bloco de rateio, o `Adicionar linha` e o rotulo `Valor total do documento`

## Abertura documental da frente transversal de UX e comunicacao operacional

- nesta etapa, o estado aprovado de refinamento do `lancamento_form.html` foi primeiro fechado no Git em commit proprio antes da abertura da nova frente transversal
- a partir desse fechamento, foi registrada oficialmente uma frente estrutural de padronizacao de UX e comunicacao operacional, com foco em fluxo continuo, texto fixo minimo, uso raro e padronizado do `i` e consistencia de linguagem, labels, headings, microtextos e estados vazios
- a auditoria inicial das telas principais do `financeiro` apontou como grupo mais alinhado ao padrao atual: `lancamento_form.html`, `lancamento_rateio_grupo_form.html`, `lancamento_list.html`, relatorios impressos e recibo
- a mesma auditoria apontou como grupo ainda mais pendente de padronizacao: `home.html`, `auditoria_lancamento_list.html`, `conta_list.html`, `pessoa_list.html` e, por extensao, os demais cadastros auxiliares do modulo que ainda preservam linguagem antiga, acentuacao inconsistente, segmentacao visual menos madura e estados vazios mais crus
- a ordem sugerida de aplicacao dessa frente ficou assim: 1) telas transacionais e de consulta do proprio `financeiro`; 2) cadastros auxiliares do modulo; 3) consolidacao de componentes compartilhados; 4) propagacao do padrao para novos itens e futuros modulos
- nesta etapa nao houve implementacao transversal nas telas auditadas; o trabalho ficou restrito a consolidar a diretriz duradoura, abrir a frente oficialmente e registrar o mapa inicial para execucao posterior por microetapas

## Refinamento da home do financeiro no novo padrao transversal

- `financeiro/templates/financeiro/home.html` deixou de usar hero com subtitulo generico e passou a funcionar como entrada mais operacional do modulo, com titulo seco e grade organizada por grupos de uso real
- os atalhos foram redistribuidos em blocos mais maduros de `Movimentacao`, `Relatorios`, `Cadastros` e `Controle e configuracao`, reduzindo a sensacao de grade solta sem alterar links, rotas ou navegacao
- a linguagem visivel da home foi padronizada com acentuacao e rotulos mais consistentes, sem introduzir novas explicacoes textuais
- foi possivel executar `py manage.py check` e validar novamente `/financeiro/` com status `200`

## Redefinicao estrutural da entrada do modulo financeiro

- a avaliacao estrutural posterior concluiu que a `home` do `financeiro` ficou redundante como tela de entrada, porque a sidebar do modulo ja cobre a navegacao estrutural e a pagina inicial nao agrega funcao operacional suficiente para justificar um passo intermediario
- com isso, `financeiro/urls.py` passou a redirecionar `/financeiro/` diretamente para a listagem principal de lancamentos, preservando a navegacao funcional e evitando abrir frente nova de dashboard sem base real
- a antiga `FinanceiroHomeView` foi preservada apenas como rota secundaria explicita, para compatibilidade e eventual referencia temporaria, sem seguir como entrada principal do modulo
- nesta microetapa nao houve alteracao de regra de negocio, calculos, validacoes nem comportamento funcional das telas operacionais do modulo

## Refinamento da leitura operacional da auditoria do financeiro

- `financeiro/templates/financeiro/auditoria_lancamento_list.html` recebeu um ajuste contido para ficar mais alinhada ao padrao transversal de UX/comunicacao: o subtitulo explicativo saiu, o retorno passou a apontar para `Lançamentos` e o bloco de filtros ficou mais maduro sem mudar sua logica
- a tabela perdeu a explicacao fixa redundante, os rotulos visiveis foram padronizados com acentuacao mais consistente e a leitura de `Campos alterados` ficou um pouco mais limpa mantendo `details/summary` como base funcional
- o estado vazio passou a ser mais curto e menos cru, sem criar nova funcionalidade, sem paginacao e sem alterar a ordenacao simples por evento mais recente
- nesta microetapa nao houve alteracao de regra de negocio, filtros, view, ordenacao nem estrutura funcional da auditoria
- `financeiro/templates/financeiro/categoria_form.html` passou a seguir a mesma ordem estrutural aprovada nas telas auxiliares mais recentes: primeiro override enxuto do `financeiro_shell_header`, preservando a sidebar como navegacao principal, e so depois refinamento do corpo do formulario
- nessa mesma tela, o `h1` cru e o formulario solto deram lugar a page header limpo, card unico de formulario, agrupamento visual mais previsivel dos campos e bloco de acoes final mais coerente, sem alterar validacoes, envio nem comportamento funcional do cadastro
- `help_text`, erros por campo e `non_field_errors` foram preservados funcionalmente, mas ganharam leitura mais clara dentro do mesmo card
- num ajuste fino visual posterior dessa mesma tela, a casca dos campos de `categoria_form.html` foi aproximada do padrao mais agradavel ja aprovado em `lancamento_form.html` e `pessoa_form.html`, com bordas menos quadradas, altura/padding mais confortaveis, largura 100% real nas colunas e `mensagem_recibo` mais confortavel
- nessa mesma passada, labels, `help_text`, erros, acoes, validacoes, envio do formulario e regra de negocio permaneceram preservados integralmente
- numa microetapa posterior de alinhamento documental refletido apenas na UI, `financeiro/templates/financeiro/categoria_form.html` deixou de usar tanto a rotulagem antiga `Categoria pai` quanto a solucao intermediaria `Categoria agrupadora`
- nessa mesma passada, o formulario passou a mostrar `Categoria` no campo hierarquico e `Subcategoria` no campo principal de nome, com ajuda local explicando que o campo vazio representa cadastro da propria `Categoria` e o preenchimento representa vinculo da `Subcategoria`
- nessa mesma passada, o texto de apoio de `mensagem_recibo` passou a usar a leitura `categoria ou subcategoria`, sem alterar models, forms Python, comportamento do envio nem implementar ainda a regra funcional futura completa de `Categoria` / `Subcategoria`
- numa microetapa posterior de consistencia visual transversal, `financeiro/templates/financeiro/centro_custo_form.html` e `financeiro/templates/financeiro/conta_form.html` passaram a adotar a mesma casca mais agradavel de campos ja aprovada em `financeiro/templates/financeiro/pessoa_form.html`, com bordas menos quadradas, altura/padding mais confortaveis, largura 100% real e foco mais coerente com o tema
- nessa mesma passada, `conta_form.html` preservou a leitura conjunta de `saldo_inicial` e `data_saldo_inicial`, enquanto `labels`, `help_text`, erros, acoes, validacoes, envio e comportamento funcional dos dois formularios permaneceram preservados integralmente
- nesta microetapa nao houve alteracao de views, forms, models, regras de negocio nem necessidade de mexer em `financeiro/templates/financeiro/base.html`
- foi possivel executar `py manage.py check` com sucesso; a tentativa de validar localmente `/financeiro/categorias/nova/` via `manage.py shell -c` nao concluiu no ambiente atual por `Acesso negado`
- em microetapa documental posterior, foi registrada a decisao funcional de consolidar no `financeiro` a nomenclatura `Categoria` / `Subcategoria`, com `Categoria` como agrupadora analitica e `Subcategoria` como item operacional lancavel
- nessa mesma decisao, ficou registrado que `Categoria` nao deve ser opcao selecionavel em lancamentos e que a opcao selecionavel deve ser a `Subcategoria`
- esta microetapa foi apenas documental: nao houve alteracao de models, forms, views, templates, relatorios nem qualquer mudanca funcional em producao
- `financeiro/templates/financeiro/conta_form.html` passou a seguir a mesma ordem estrutural aprovada nas telas auxiliares mais recentes: primeiro override enxuto do `financeiro_shell_header`, preservando a sidebar como navegacao principal, e so depois refinamento do corpo do formulario
- nessa mesma tela, o `h1` cru e o formulario solto deram lugar a page header limpo, card unico de formulario, agrupamento visual mais previsivel dos campos e bloco de acoes final mais coerente
- `saldo_inicial` e `data_saldo_inicial` passaram a ler juntos na mesma faixa do formulario, reforcando a compreensao do saldo-base sem alterar validacoes, envio nem comportamento funcional do cadastro
- `help_text`, erros por campo e `non_field_errors` foram preservados funcionalmente, mas ganharam leitura mais clara dentro do mesmo card
- nesta microetapa nao houve alteracao de views, forms, models, regras de negocio nem necessidade de mexer em `financeiro/templates/financeiro/base.html`
- `financeiro/templates/financeiro/pessoa_form.html` passou a seguir a mesma ordem estrutural aprovada nas telas auxiliares mais recentes: primeiro override enxuto do `financeiro_shell_header`, preservando a sidebar como navegacao principal, e so depois refinamento do corpo do formulario
- nessa mesma tela, o `h1` cru e o formulario solto deram lugar a page header limpo, card unico de formulario, agrupamento visual mais previsivel dos campos e bloco de acoes final mais coerente
- `tipo_pessoa`, `documento`, `telefone`, `email` e `observacoes` passaram a operar em agrupamentos mais legiveis dentro do mesmo fluxo de cadastro, sem alterar validacoes, envio nem comportamento funcional da tela
- `help_text`, erros por campo e `non_field_errors` foram preservados funcionalmente, mas ganharam leitura mais clara dentro do mesmo card
- nesta microetapa nao houve alteracao de views, forms, models, regras de negocio nem necessidade de mexer em `financeiro/templates/financeiro/base.html`
- num ajuste fino visual posterior dessa mesma tela, a grade passou a usar distribuicao horizontal mais bem justificada entre as linhas de identificacao, documento e contato, reduzindo a sensacao de campos curtos demais dentro do card
- `observacoes` permaneceu em largura integral, mas com leitura mais confortavel dentro da mesma ficha, sem alterar labels, `help_text`, erros, acoes nem comportamento funcional do formulario
- num polimento visual seguinte dessa mesma tela, a casca dos campos foi aproximada do padrao mais agradavel do `lancamento_form.html`, com bordas menos quadradas, altura/padding mais confortaveis, largura 100% real nas colunas e foco mais claro
- nessa mesma passada, `observacoes` foi mantido em bloco proprio e ganhou leitura mais coerente com os demais campos, sem alterar labels, `help_text`, erros, acoes, validacoes nem envio do formulario
- numa microcorrecao visual posterior dessa mesma tela, o campo booleano `Ativo` foi reduzido e enquadrado como controle mais discreto, com checkbox menor e leitura mais proporcional ao restante do card
- nessa mesma passada, label, envio, validacoes e comportamento funcional do booleano foram preservados integralmente
- numa microcorrecao visual transversal posterior, `financeiro/templates/financeiro/centro_custo_form.html`, `financeiro/templates/financeiro/categoria_form.html` e `financeiro/templates/financeiro/conta_form.html` passaram a adotar a mesma apresentacao visual discreta dos booleanos ja aprovada em `financeiro/templates/financeiro/pessoa_form.html`
- com isso, os checkboxes auxiliares deixaram de usar a aparencia amarela/laranja residual e passaram a operar com a mesma leitura azul, menor e mais proporcional ao tema, sem alterar labels, envio, validacoes nem comportamento funcional dos formularios
- em microetapa documental posterior, foram consolidadas sem patch de codigo quatro frentes futuras do `financeiro`: 1) a necessidade de deixar mais explicito na UI do cadastro de categorias se o usuario esta criando `Categoria` ou `Subcategoria`; 2) o refinamento futuro do menu lateral para leitura mais leve e elegante; 3) a sugestao futura de regras reutilizaveis no lancamento com preenchimento automatico revisavel; 4) a acao futura `Clonar lancamento`
- nessa mesma passada documental, tambem ficou reforcado que permissões, acesso, login e perfis continuam como frente estrutural futura e nao entram nesta etapa
- esta microetapa foi apenas documental: nao houve alteracao de models, forms, views, templates, relatorios nem qualquer mudanca funcional em producao
- numa microetapa posterior de clareza de UI, `financeiro/templates/financeiro/categoria_form.html` passou a usar um seletor visual simples `Categoria | Subcategoria` no proprio formulario, sem alterar models, forms Python, views nem a regra profunda do cadastro
- nessa mesma passada, o campo principal de nome passou a trocar visualmente entre `Categoria` e `Subcategoria`, e o campo `Categoria` passou a ficar oculto/desativado no modo `Categoria` e visivel no modo `Subcategoria`, preservando envio, validacoes e comportamento geral da tela
- esta evolucao ainda nao deve ser lida como implementacao completa da regra funcional futura; ela atua apenas como camada intermediaria de clareza operacional na UI atual
- numa microetapa posterior de primeira passada no extrato real do sistema, `financeiro/templates/financeiro/conta_extrato.html` manteve o `financeiro_shell_header` padrao e recebeu apenas refinamento do corpo da tela, com header local mais limpo, filtros mais maduros, tabela mais consistente e estados vazios/microtextos mais operacionais
- nessa mesma passada, `print/PDF`, `saldo anterior`, `saldo acumulado`, a leitura dos rateios consolidados e as acoes `Imprimir` e `Limpar` foram preservados como prioridade maxima, sem alterar models, views, forms, calculos nem logica do extrato
- num ajuste fino posterior dessa mesma tela, o `Saldo anterior` foi reposicionado para um bloco proprio acima do cabecalho da tabela, deixando os titulos das colunas como inicio real da listagem do periodo sem alterar calculos, saldo acumulado, leitura de rateios nem print/PDF
- num ajuste visual seguinte da mesma tela, esse bloco de `Saldo anterior` foi alinhado a mesma linguagem visual do `Saldo final`, enquanto a faixa impressa `Conta | Periodo | Emitido em` foi mantida sem linhas horizontais acima ou abaixo, preservando print/PDF e toda a logica do extrato
- na correcao fina posterior dessa mesma tela, o `Saldo anterior` acima da tabela deixou de usar bloco especial e passou a ser renderizado na mesma linguagem visual tabular do `Saldo final`, mantendo apenas a mudanca de posicao e preservando calculos, leitura de rateios e print/PDF
- numa microcorrecao final posterior dessa mesma tela, a faixa impressa `Conta | Periodo | Emitido em` recebeu override especifico no `@media print` para remover de fato as linhas horizontais herdadas de `base.html`, sem alterar calculos, leitura de rateios nem a estrutura do extrato
- numa microcorrecao visual posterior dessa mesma tela, o cabecalho e as linhas dos lancamentos passaram a usar bordas mais finas e suaves, reduzindo o peso visual da tabela sem alterar calculos, leitura de rateios, print/PDF nem a hierarquia ja aprovada do extrato
- numa correcao posterior dessa mesma microetapa, a suavizacao das bordas da tabela foi mantida apenas no `@media print`, revertendo o alivio visual da tela normal e deixando o ajuste exclusivo da versao PDF/impressa
- numa correcao fina posterior dessa mesma microetapa, o print do extrato deixou de usar linhas de `0.7px` e passou a aplicar divisorias ainda mais leves no cabecalho e no corpo da tabela, com espessura menor e cor mais suave apenas na versao PDF/impressa
- num ajuste fino posterior dessa mesma microetapa, o `@media print` do extrato foi recalibrado para usar divisorias intermediarias no cabecalho e no corpo, preservando o alivio visual sem deixar o PDF leve demais
- numa correcao posterior dessa mesma microetapa, foi identificado que a cascata real do PDF ainda vinha principalmente dos seletores de print de `financeiro/base.html` sobre `.financeiro-extrato-table`; por isso, o extrato passou a sobrescrever no proprio `@media print` os elementos reais `table > thead > tr > th` e `table > tbody > tr > td`, com seletor mais especifico e sem alterar a tela normal
- numa correcao posterior dessa mesma microetapa, o `Saldo anterior` passou a reaproveitar a mesma gramatica estrutural do `Saldo final`, mudando apenas de posicao acima do cabecalho, e o PDF do extrato foi recalibrado para usar bordas de `1px` com cor significativamente mais suave nas divisorias do cabecalho e do corpo
- numa calibragem fina posterior dessa mesma microetapa, o `Saldo anterior` acima da tabela passou a usar exatamente a mesma tabela e a mesma linha visual do `Saldo final`, enquanto o `@media print` do extrato clareou ainda mais as divisorias de `1px` no cabecalho e no corpo para reduzir o peso visual do PDF sem tornar as linhas invisiveis
- numa correcao posterior dessa mesma microetapa, o `Saldo anterior` passou a compartilhar o mesmo `colgroup` da tabela principal para alinhar visualmente o rótulo e o valor nas mesmas colunas do `Saldo final`, enquanto o print do extrato trocou a estrategia de espessura para `pt` nas divisorias do cabecalho e do corpo, sem depender apenas de cor
- numa correcao estrutural posterior dessa mesma microetapa, o `Saldo anterior` deixou de viver em tabela separada e passou a ocupar a primeira linha do `thead` da tabela principal do extrato, alinhando de forma efetiva o rótulo e o valor as mesmas colunas do `Saldo final`
- nessa mesma correcao, o `@media print` do extrato deixou de atuar apenas por borda e passou tambem a reduzir a densidade da grade no cabecalho e no corpo, ajustando `padding-top` e `padding-bottom` de `th` e `td` sem alterar calculos, filtros, rateios ou a linha de `Conta | Periodo | Emitido em`
- numa correcao estrutural posterior dessa mesma microetapa, o `Saldo anterior` deixou o `thead` e voltou a ser renderizado com `tbody > tr > td` em tabela auxiliar acima da principal, reaproveitando o mesmo `colgroup` e a mesma linha visual do `Saldo final` para alinhar rótulo e valor nas mesmas colunas
- nessa mesma correcao, o `@media print` do extrato deixou de depender de clareamento progressivo e passou a recalibrar a leveza da grade pela combinacao de borda `1px` com menor `padding-top` e `padding-bottom` de `th` e `td`, preservando calculos, filtros, rateios e a linha `Conta | Periodo | Emitido em`
- numa reversao posterior dessa mesma microetapa, o `Saldo anterior` deixou de usar novamente tabela auxiliar e voltou a ocupar a posicao anterior acima do cabecalho, enquanto a linha correspondente do `thead` passou a espelhar apenas a gramática visual do `Saldo final`, sem alterar este ultimo
- nessa mesma reversao, o `@media print` do extrato foi recalibrado outra vez com foco em espessura e densidade real da grade, reduzindo ainda mais o `padding-top`/`padding-bottom` de `th` e `td` e usando borda mais fina em `pt`, sem recorrer a novo clareamento progressivo como estrategia principal

## Acabamento fino final de consistencia no formulario principal

- `financeiro/templates/financeiro/lancamento_form.html` recebeu ajuste final de consistencia, removendo o subtitulo residual da pagina e compactando um pouco mais o bloco `Modo do lançamento`
- o componente visual do `i` ficou mais coerente em tamanho, alinhamento, contraste e espacamento, sem ampliar seu uso na tela
- o `i` de `Linhas do rateio` foi removido por redundancia, enquanto os pontos de ajuda realmente necessarios permaneceram apenas em `Lançamento com rateio` e `Valor total do documento`
- o estado vazio de `Últimos lançamentos do favorecido` ficou mais leve, e as acoes `Adicionar linha` / `Remover` ficaram discretamente mais ajustadas ao restante da tela
- nesta microetapa nao houve alteracao de regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos nem comportamento do formulario
- foi possivel executar `py manage.py check` e validar novamente `/financeiro/lancamentos/novo/` com status `200`

## Refinamento do relatorio de inconsistencias da importacao

- o relatorio XLSX de inconsistencias da importacao passou a incluir a coluna `Como corrigir`, preservando `Linha`, `Campo` e `Mensagem`
- as dicas sao curtas e operacionais, por exemplo formato de data, revisao de nomes cadastrados, compatibilidade entre `Tipo` e `Categoria`, preenchimento de `Conta de destino` e revisao de duplicidade de `Documento`
- a coluna e derivada do campo/erro ja validado e nao altera a logica de importacao, a politica all-or-nothing, a estrutura da tela nem a aba unica `Inconsistencias`

## Apoio adicional para correcao da planilha importada

- o relatorio XLSX de inconsistencias passou a incluir tambem a coluna `Valor informado`, preenchida com o valor da propria celula/campo lido da aba `Modelo` quando esse dado esta disponivel
- essa coluna ajuda o usuario a localizar rapidamente o conteudo que precisa ser corrigido na planilha original, sem reescrever o arquivo enviado e sem alterar o fluxo atual de importacao
- a aba `Inconsistencias`, as colunas `Linha`, `Campo`, `Mensagem` e `Como corrigir`, a validacao ja existente e a politica all-or-nothing permaneceram preservadas

## Fase 1 de edicao em lote na listagem de lancamentos

- `financeiro/templates/financeiro/lancamento_list.html` passou a exibir checkbox por linha, um checkbox de marcar todos os lancamentos visiveis e uma barra compacta de acoes em lote com `Alterar status` e `Excluir selecionados`
- foi criada uma rota/view POST especifica para processar acoes em lote apenas em lancamentos, preservando os filtros GET ativos no retorno e sem expandir esta frente para outros cadastros nesta fase
- a exclusao em lote exige confirmacao no navegador, executa a remocao dentro de `transaction.atomic()` e registra auditoria de exclusao para cada item selecionado
- a alteracao de status em lote valida o novo status, aplica `full_clean()` em cada lancamento, grava tudo em `transaction.atomic()` e registra auditoria de update por item; se algum item falhar, nenhuma alteracao e efetivada
- esta microetapa nao alterou regras de negocio da importacao, rateio, clone, transferencia, exportacao ou permissao; a expansao da edicao em lote para outros cadastros permanece apenas como roadmap futuro

## Agrupamento visual de rateios na listagem de lancamentos

- a listagem principal passou a montar uma estrutura visual propria na view para exibir lancamentos comuns como linhas normais e lancamentos rateados como uma unica linha-resumo por `grupo_rateio`, mantendo a ordenacao oficial da tela e sem alterar o modelo fisico dos dados
- a linha-resumo de rateio ficou mais limpa e exibe apenas os dados principais do documento/grupo enquanto esta fechada; o icone extra de rateio e o resumo curto de categorias/valores foram removidos do estado fechado, e a expansao em `details/summary` passou a concentrar a leitura das linhas internas com categoria e valor de cada parte
- o checkbox da linha-resumo de rateio passou a enviar um token de grupo para que a exclusao em lote e a alteracao de status em lote atuem sobre todas as linhas do `grupo_rateio`, enquanto lancamentos comuns continuam enviando o identificador individual
- na linha-resumo de rateio, as acoes visiveis ficaram restritas as operacoes ja semanticamente de grupo (`Clonar` e `Editar` por `grupo_rateio`), evitando expor `Recibo` e `Excluir` diretos que ainda sao rotas por linha individual; essa e uma decisao de UX apenas da listagem, sem mudanca em extrato, prestacao, recibo, auditoria e demais telas nesta microetapa
- num ajuste fino posterior, a celula de `Descricao` passou a usar a mesma estrutura interna para linhas comuns e rateios, com placeholder invisivel de mesma largura do toggle nas linhas sem expansao, eliminando o desalinhamento horizontal sem alterar a interacao do `details/summary`

## Refinamento de acoes, ordenacao e leitura da descricao na listagem

- a coluna de acoes da listagem passou a usar quatro slots fixos por funcao (`Recibo`, `Clonar`, `Editar`, `Excluir`), com placeholders invisiveis quando uma acao nao se aplica, preservando alinhamento visual entre lancamentos comuns e grupos rateados
- `Recibo` foi tratado como acao contextual e, nesta etapa, aparece apenas em lancamentos comuns do tipo `receita`, sem deslocar os demais botoes quando nao esta disponivel
- a ordenacao padrao da listagem foi ajustada para priorizar a data principal mais recente do lancamento/grupo, usando `data_pagamento` quando preenchida e `data_competencia` como fallback, com desempate por `pk` mais recente; nos rateios, a linha representativa exibida segue o primeiro lancamento do grupo encontrado nessa ordenacao
- a coluna `Descricao` passou a usar truncamento com reticencias para evitar quebra excessiva na tabela, mantendo o texto completo acessivel por `title` no lancamento comum e no `summary` do grupo rateado

## Iconografia compacta na listagem de lancamentos

- os botoes de `Recibo`, `Clonar`, `Editar` e `Excluir` foram trocados por icones SVG compactos dentro dos mesmos quatro slots fixos ja aprovados, mantendo `title`, `aria-label` e texto apenas para leitor de tela
- `Tipo` passou a ser representado por setas compactas (`receita` para cima, `despesa` para baixo e `transferencia` com setas opostas), com tooltip e rotulo acessivel preservando o nome completo
- `Status` passou a usar iconografia compacta (`aberto` com um check, `quitado` com dois checks e `cancelado` com X), mantendo cor, tooltip e `aria-label`
- a largura visual da coluna de acoes foi reduzida e a coluna `Pessoa` ganhou `min-width`, liberando leitura mais confortavel sem alterar truncamento da descricao, rateio agrupado, filtros, edicao em lote ou regras de negocio

## Ordenacao por coluna na listagem de lancamentos

- a ordenacao padrao da listagem continua priorizando a data principal mais recente do lancamento/grupo, usando `data_pagamento` quando existir, `data_competencia` como fallback e `pk` mais recente como desempate
- foi adicionada ordenacao manual por coluna no cabecalho para `Descricao`, `Tipo`, `Status`, `Valor`, `Pessoa` e `Data`, com icones discretos indicando estado neutro e direcao crescente/decrescente quando a coluna esta ativa
- a ordenacao manual preserva os filtros GET ja aplicados, reordena a estrutura visual consolidada de lancamentos/rateios sem quebrar o agrupamento por `grupo_rateio` e usa o `valor_total` do grupo quando a ordenacao e por `Valor`
- `Conta`, `Conta destino` e `Documento` ficaram fora da ordenacao manual nesta fase para manter a microetapa pequena e evitar poluir o cabecalho com criterios menos prioritarios

## Consolidacao documental de governanca e proximas prioridades estruturais

- foi registrado que a proxima frente funcional prioritaria do sistema deve ser `permissoes/autenticacao`, com interface de perfis hierarquicos em `Modulo` > `Tela/Recurso` > `Acao`, depois da estabilizacao do `financeiro`
- foram formalizadas como proximas frentes: auditoria de UX entre telas existentes, documento transversal de padrao visual/funcional do sistema, padronizacao das melhorias aprovadas no `financeiro` para outros modulos, cadastro de logo com URL ou upload local e preview, e expansao futura de acoes em lote para outros cadastros
- foi registrada uma checklist permanente para toda nova implementacao cobrindo navegacao/menu/atalhos, permissoes, listagens, formularios, importacao/exportacao, auditoria/log, ajuda/manual, aderencia ao padrao UX/layout e atualizacao obrigatoria dos docs-base
- foi criado `docs/PADRAO_UX_SISTEMA.md` como referencia inicial enxuta de UX/layout do sistema
- esta microetapa foi exclusivamente documental/estrutural e nao abriu implementacao de permissoes, nem alteracao de models, views, forms ou templates operacionais

## Checklist operacional permanente de evolucao do sistema

- foi criado `docs/CHECKLIST_EVOLUCAO_SISTEMA.md` como checklist curta e permanente para revisar toda nova funcionalidade antes de auditoria/commit
- o documento cobre navegacao/menu/atalhos, permissoes por modulo/tela/acao, impacto em listagens, impacto em formularios, importacao/exportacao, auditoria/log, ajuda/manual do usuario, aderencia a `docs/PADRAO_UX_SISTEMA.md` e atualizacao dos docs-base
- ficou registrado no roadmap que `docs/MATRIZ_PERMISSOES.md` so deve ser criado quando a frente de permissoes/autenticacao for efetivamente aberta, e nao nesta microetapa
- esta microetapa foi exclusivamente documental/estrutural e nao alterou codigo, `docs/CEREBRO_PROJETO.md` ou `docs/PADRAO_UX_SISTEMA.md`

## Levantamento estrutural para futura matriz hierarquica de permissoes

- foram relidos `docs/CEREBRO_PROJETO.md`, `docs/STATE.md`, `docs/CODEX_RESULTADO.md`, `docs/ROADMAP_FINANCEIRO.md`, `docs/PADRAO_UX_SISTEMA.md` e `docs/CHECKLIST_EVOLUCAO_SISTEMA.md`, e foi verificado que `docs/MATRIZ_PERMISSOES.md` ainda nao existe no repositorio
- o estado real do Git foi conferido antes do levantamento: branch `feat/reinicio-financeiro`, branch local `ahead 17` de `origin/feat/reinicio-financeiro`, sem modificacoes rastreadas abertas e com apenas `tmp/` como item untracked visivel, nao havendo pendencia funcional aberta da frente anterior no codigo versionado
- foi mapeada a estrutura real de modulos, rotas, telas, acoes e navegacao expostas hoje no sistema, sem implementar permissao, login/logout, grupos Django, travas de tela ou novo documento protegido
- no `financeiro`, a futura matriz deve nascer a partir dos grupos reais de menu e recursos ja existentes: `Visao geral`, `Lancamentos`, `Extratos`, `Resumo do Periodo`, `Prestacao de Contas`, `Auditoria do Financeiro`, `Contas`, `Pessoas`, `Categorias`, `Centros de Custo`, `Assinaturas Institucionais` e `Configuracoes Institucionais`
- as acoes reais a considerar no `financeiro` incluem, conforme o recurso, `listar/visualizar`, `criar`, `editar`, `excluir`, `clonar`, `emitir recibo`, `acoes em lote`, `importar`, `exportar`, `baixar modelo`, `baixar inconsistencias`, `imprimir`, `consultar autocomplete/historico` e `consultar sugestoes de regras automaticas`
- no `biblioteca`, a leitura atual identificou `Autores`, `Livros`, `Vendas` e `Emprestimos`, com menu proprio e acoes de `listar` e `criar` ja expostas; edicao/exclusao nao aparecem como rotas desse app no estado atual
- no `configuracoes`, a raiz `/` responde por `SiteConfigDetailView` e o Django admin segue disponivel em `/admin/`; nao existe `configuracoes/urls.py` no estado atual
- foi proposta uma hierarquia inicial de perfis para amadurecer na proxima etapa, ainda sem criar grupos no Django: `Administrador geral`, `Gestao administrativa`, `Operador financeiro`, `Operador biblioteca` e `Consulta/visualizacao`
- a leitura de impactos para a futura frente apontou que a governanca de permissoes nao pode ser apenas bloqueio de rota: ela precisa refletir tambem menu/sidebar/atalhos, botoes e acoes em listagens, formularios de criacao/edicao, importacao/exportacao, visibilidade da auditoria, futura ajuda/manual, logs e aderencia ao padrao UX
- proximas microetapas sugeridas, em ordem: 1) consolidar e revisar este levantamento com auditoria humana; 2) abrir `docs/MATRIZ_PERMISSOES.md` com a matriz `Modulo > Tela/Recurso > Acao`; 3) definir regras de exibicao de menu/botoes e restricao de endpoints auxiliares por perfil; 4) so depois iniciar a implementacao tecnica de autenticacao/autorizacao em codigo, em fatias pequenas
- `docs/ROADMAP_FINANCEIRO.md` nao foi alterado nesta microetapa porque a prioridade de `permissoes/autenticacao` e a criacao futura de `docs/MATRIZ_PERMISSOES.md` ja estavam registradas de forma suficiente

## Primeira versao formal de `docs/MATRIZ_PERMISSOES.md`

- foi criado `docs/MATRIZ_PERMISSOES.md` com objetivo, premissas de modelagem de acesso, estrutura hierarquica `Modulo > Tela/Recurso > Acao`, perfis-base previstos, matriz inicial por modulo/recurso/acao, regras gerais de aplicacao e itens futuros planejados sem implementacao
- os perfis-base formalizados nesta versao inicial foram `Administrador geral`, `Gestao administrativa`, `Operador financeiro`, `Operador biblioteca` e `Consulta/visualizacao`
- a matriz separou o modulo `financeiro` com granularidade operacional por `Lancamentos`, `Extratos`, `Resumo financeiro`, `Prestacao de contas`, `Auditoria`, `Contas`, `Pessoas`, `Categorias`, `Subcategorias`, `Centros de custo`, `Assinaturas institucionais` e `Configuracoes institucionais`, incluindo acoes como listar, visualizar, criar, editar, excluir, clonar, editar rateio, emitir recibo, importar, exportar, imprimir, baixar modelo, baixar inconsistencias, ver auditoria, acoes em lote e acessar endpoints auxiliares
- o modulo `biblioteca` foi contemplado com `Autores`, `Livros`, `Vendas` e `Emprestimos`, respeitando o estado real atual em que essas telas expoem listar/criar e nao apresentam rotas proprias de edicao/exclusao
- o modulo `configuracoes` foi contemplado com `SiteConfig /`, e a administracao tecnica/global foi separada em bloco proprio para `/admin/`, reforcando a diferenca entre administracao funcional do sistema e administracao tecnica do Django admin
- a regra de governanca registrada foi que esconder menu nao basta: a permissao futura precisa valer tambem em tela, botao/acao e endpoint auxiliar, com maior restricao para operacoes destrutivas, configuracoes sensiveis e auditoria
- a diretriz arquitetural registrada para a frente ficou assim: V1 com 1 perfil base por usuario; evolucao futura compativel com extras individuais e bloqueios individuais por usuario; formula conceitual futura `permissao final = perfil base + extras individuais - bloqueios individuais`; nada disso foi tratado como implementado em codigo nesta etapa
- `docs/STATE.md` foi atualizado com a consolidacao da matriz, `docs/ROADMAP_FINANCEIRO.md` recebeu apenas ajuste cirurgico para refletir que a primeira versao de `docs/MATRIZ_PERMISSOES.md` ja foi criada e para orientar as proximas subetapas, e nenhum arquivo de codigo, login/logout, grupos Django, decorators, mixins ou templates de permissao foi alterado

## Auditoria e fechamento das regras por perfil em `docs/MATRIZ_PERMISSOES.md`

- a matriz foi revisada para reduzir ambiguidades sensiveis e fechar a diferenca entre leitura, operacao comum, operacao sensivel e administracao tecnica/global
- o marcador `R` foi removido da proposta inicial e as permissoes pendentes foram resolvidas de forma explicita por perfil, preservando a legenda `S`/`-` e registrando que ausencia de permissao na matriz equivale a negacao na V1
- `/admin/` ficou exclusivo do `Administrador geral`, enquanto `Gestao administrativa` permanece com administracao funcional ampla sem acesso tecnico/global ao Django admin
- em `financeiro`, `Gestao administrativa` pode excluir, importar, operar configuracoes institucionais e ver auditoria; `Operador financeiro` pode criar/editar/clonar/importar/exportar e alterar status em lote, mas nao excluir lancamentos/cadastros, nao excluir em lote, nao ver auditoria e nao administrar configuracoes institucionais
- `Consulta/visualizacao` ficou restrito a leitura, impressao e exportacao onde ja possui acesso de leitura, sem criar, editar, excluir, importar, executar lote ou consumir endpoints auxiliares de formulario
- `Operador biblioteca` ficou restrito ao modulo `biblioteca` e a leitura institucional de `SiteConfig /`, sem herdar rotas, atalhos ou endpoints auxiliares do `financeiro`
- foi adicionada ao proprio documento uma convencao de leitura da matriz, criterios para futuras excecoes individuais e uma observacao de governanca para que endpoints auxiliares sigam a permissao do recurso principal
- esta microetapa nao alterou codigo, `docs/CEREBRO_PROJETO.md`, `docs/PADRAO_UX_SISTEMA.md` nem `docs/CHECKLIST_EVOLUCAO_SISTEMA.md`

## Plano tecnico de implementacao de permissoes/autenticacao

- foi criado `docs/PLANO_TECNICO_PERMISSOES.md` para transformar `docs/MATRIZ_PERMISSOES.md` em plano tecnico de execucao, sem iniciar codigo nesta microetapa
- o documento registra objetivo tecnico da frente, escopo da V1, itens fora de escopo, arquitetura proposta, modelagem conceitual minima, estrategia de aplicacao em camadas, ordem incremental de microetapas, riscos/dependencias e o primeiro ponto de aplicacao real
- a decisao tecnica registrada foi adotar um modelo hibrido: `User`/autenticacao/sessao/login/logout do Django para identidade e camada propria do sistema para `Perfil`, `Permissao do sistema`, `Perfil-Permissao` e `Usuario-Perfil`, mantendo `Group/Permission` nativo fora da governanca funcional principal da V1
- a justificativa registrada foi a aderencia da matriz ja aprovada ao formato `Modulo > Tela/Recurso > Acao`, a necessidade de governanca de menu/botoes/endpoints auxiliares e a compatibilidade futura com `permissao final = perfil base + extras individuais - bloqueios individuais`
- a ordem proposta de implementacao ficou: 1) estrutura de dados e seeds de perfis/permissoes; 2) login/logout e primeiro enforcement backend no `financeiro`; 3) sidebar/botoes/templates do `financeiro`; 4) expansao para `biblioteca` e `configuracoes`; 5) UI propria de administracao funcional de perfis; 6) endurecimento/auditoria e preparacao para extras/bloqueios individuais futuros
- o primeiro modulo de aplicacao real da V1 foi definido como `financeiro`, com foco inicial em `Lancamentos`, `Auditoria do Financeiro`, `Configuracoes institucionais`, `Assinaturas institucionais`, `Importar/Exportar` e endpoints auxiliares de formulario/historico
- esta microetapa atualizou `docs/STATE.md` e nao alterou codigo, `docs/CEREBRO_PROJETO.md`, `docs/MATRIZ_PERMISSOES.md`, `docs/PADRAO_UX_SISTEMA.md` nem `docs/CHECKLIST_EVOLUCAO_SISTEMA.md`

## Base de dados e seeds iniciais da V1 de permissoes

- foi implementada a estrutura de dados minima da V1 de permissoes no app `configuracoes`, com `PerfilAcesso`, `PermissaoSistema`, `PerfilPermissaoSistema` e `UsuarioPerfilAcesso`
- a modelagem preserva `User` do Django como identidade/autenticacao e usa uma camada propria do sistema para a governanca funcional de permissoes, em linha com a decisao tecnica hibrida ja documentada
- a regra V1 de 1 perfil base por usuario foi materializada com `UsuarioPerfilAcesso.usuario` em `OneToOneField` para `AUTH_USER_MODEL`, sem implementar extras individuais ou bloqueios individuais nesta fase
- foram criadas as migrations de schema e seed inicial de `configuracoes`, com seeds idempotentes baseados em `update_or_create` e vinculo perfil-permissao sincronizado por codigo estavel
- os perfis-base semeados foram `Administrador geral`, `Gestao administrativa`, `Operador financeiro`, `Operador biblioteca` e `Consulta/visualizacao`
- o seed inicial inclui permissoes funcionais para `financeiro`, `biblioteca`, `configuracoes.siteconfig` e `configuracoes.admin_global`, ja refletindo as restricoes centrais da matriz V1 sem ativar enforcement em views/templates/menu
- limitacao intencional desta microetapa: nao houve login/logout customizado, decorators/mixins, protecao de rotas, ocultacao de menu/sidebar, UI de administracao de perfis, atribuicao automatica de perfil a usuarios existentes nem implementacao de extras/bloqueios individuais

## Bootstrap operacional minimo de autenticacao e permissoes

- foram criadas rotas/views de `login` e `logout` em `configuracoes`, apoiadas na autenticacao padrao do Django e em um template minimo de login com linguagem visual propria e sem abrir uma frente ampla de UX
- `casa_espirita/urls.py` passou a incluir `configuracoes.urls`, preservando a rota da home institucional e expondo `/login/` e `/logout/`; `casa_espirita/settings.py` passou a definir os redirecionamentos padrao de login/logout
- foi criada a camada central `configuracoes/permissoes.py` com `obter_perfil_base_usuario()` e `usuario_possui_permissao()`, ja preparada para o proximo enforcement backend no `financeiro`
- a regra adotada para usuario autenticado sem `UsuarioPerfilAcesso` vinculado foi deny-by-default: nao ha permissao funcional implicita por estar logado nem por ser superusuario, enquanto o controle operacional do primeiro admin funcional deve ser feito por vinculo manual ao perfil `Administrador geral` via `/admin/`
- `PermissaoSistema`, `PerfilAcesso`, `PerfilPermissaoSistema` e `UsuarioPerfilAcesso` foram registrados no Django admin como bootstrap temporario de operacao dessa base de acesso
- esta microetapa nao aplicou enforcement fino no `financeiro`, nao condicionou sidebar/menu/templates por perfil, nao criou grupos Django e nao implementou extras individuais ou bloqueios individuais

## Primeiro enforcement backend de permissoes no financeiro

- foi criado `financeiro/permissoes.py` com o mixin `FinanceiroPermissaoMixin`, reaproveitando `usuario_possui_permissao()` da camada central de `configuracoes`
- o mixin combina exigencia de usuario autenticado com validacao funcional por codigo canonico de permissao, mantendo deny-by-default e retornando HTTP 403 com mensagem simples quando o usuario nao possui perfil/permissao
- `financeiro/views.py` passou a declarar `permissao_requerida` nas views de home secundaria, relatorios/consultas, CRUDs de cadastros, auditoria, lancamentos, clone, rateio, recibo, importacao/exportacao e endpoints auxiliares
- a view de acoes em lote passou a resolver a permissao exigida de forma dinamica a partir de `acao_lote`, diferenciando `alterar status` de `excluir em lote`
- smoke tests executados: `/financeiro/lancamentos/` redireciona anonimo para login, usuario autenticado sem perfil recebe 403, `Consulta/visualizacao` entra na listagem mas nao acessa create, `Operador financeiro` acessa create mas nao delete/auditoria, e `Gestao administrativa` acessa auditoria
- esta microetapa nao alterou menus/sidebar/templates por perfil, nao abriu enforcement em outros modulos e nao introduziu bypass funcional para superusuario

## Primeiro enforcement visual de permissoes no financeiro

- foi criada a strategy reutilizavel de template em `financeiro/templatetags/financeiro_permissoes.py`, com `tem_permissao` e `tem_alguma_permissao`, apoiada no cache de codigos ativos adicionado em `configuracoes/permissoes.py`
- o shell lateral de `financeiro/base.html` e a `home` secundaria do modulo passaram a esconder grupos/atalhos quando o perfil autenticado nao possui a permissao de leitura correspondente do recurso
- as listagens de `contas`, `pessoas`, `categorias`, `centros de custo`, `assinaturas institucionais`, `configuracoes institucionais` e `lancamentos` passaram a esconder acoes principais (`criar`, `editar`, `excluir`, `extrato`, `recibo`, `clonar`, `editar rateio`, `acoes em lote`) de forma coerente com a matriz V1, sem substituir a protecao backend
- a listagem de `lancamentos` passou a ajustar dinamicamente os controles de `exportar`, `importar`, `novo lancamento`, `acoes em lote`, coluna de selecao e coluna de acoes conforme o perfil autenticado
- a tela de `importacao/exportacao` passou a esconder `baixar planilha modelo` e `baixar relatorio de inconsistencias` quando faltarem as permissoes especificas, preservando a politica funcional da importacao
- o historico de ultimos lancamentos por pessoa deixou de expor link de clone quando o usuario nao possui `financeiro.lancamentos.clonar`, alinhando o atalho contextual ao enforcement visual
- smoke tests visuais basicos confirmaram o comportamento esperado para `Consulta/visualizacao`, `Operador financeiro` e `Gestao administrativa`, com a UI refletindo o que o backend ja permite ou nega no `financeiro`

## Expansao do enforcement backend para biblioteca e configuracoes

- o enforcement backend deixou de ser uma particularidade do `financeiro` e passou a ter uma base generica em `configuracoes/permissoes.py`, por meio do novo `PermissaoSistemaMixin`
- `financeiro/permissoes.py` foi simplificado para herdar desse mixin generico, preservando apenas a mensagem especifica do modulo e mantendo compatibilidade com o enforcement ja aprovado
- `biblioteca/permissoes.py` e `configuracoes/mixins.py` foram criados para adaptar a mesma estrategia a cada modulo sem duplicar a regra de autenticacao + permissao + 403 funcional
- `biblioteca/views.py` passou a proteger backend de `Autores`, `Livros`, `Vendas` e `Emprestimos` com os codigos canonicos semeados na V1, cobrindo as listagens e criacoes reais que existem hoje no app
- `configuracoes/views.py` passou a proteger `SiteConfig /` com `configuracoes.siteconfig.visualizar`, mantendo `login/logout` livres dessa camada e deixando `/admin/` separado como administracao tecnica/global
- a validacao tecnica revelou que a seed anterior ainda nao dava `configuracoes.siteconfig.visualizar` ao `Operador financeiro`, apesar de a matriz fechada ja prever essa leitura; isso foi corrigido com a migration de alinhamento `0005_alinhar_siteconfig_operador_financeiro.py`
- smoke tests backend confirmaram o desenho final: anonimo `302` para login, autenticado sem perfil `403`, `Consulta/visualizacao` com leitura de `biblioteca` e `/`, `Operador financeiro` sem acesso a `biblioteca` mas com acesso a `/`, `Operador biblioteca` restrito a `biblioteca` + `/`, e `Gestao administrativa` com acesso amplo coerente com a matriz

## Expansao do enforcement visual para biblioteca e configuracoes

- foi criada a template tag generica `configuracoes/templatetags/permissoes_sistema.py`, reutilizando `usuario_possui_permissao()` para os templates de `biblioteca` e `configuracoes`
- `biblioteca/templates/biblioteca/base.html` passou a condicionar a navegacao do modulo as permissoes `biblioteca.*.listar`, evitando expor links de leitura para perfis que nao deveriam usar o modulo
- as listagens de `Autores`, `Livros`, `Vendas` e `Emprestimos` passaram a esconder os botoes de criacao quando faltam as permissoes `biblioteca.autores.criar`, `biblioteca.livros.criar`, `biblioteca.vendas.criar` e `biblioteca.emprestimos.criar`
- `configuracoes/templates/configuracoes/siteconfig_detail.html` ganhou barra utilitaria minima com `Entrar` para anonimos, `Sair` para autenticados e `Admin tecnico` apenas para quem possui `configuracoes.admin_global.acessar`
- a protecao principal continua no backend; a UI passou apenas a refletir o que ja esta protegido, reduzindo menu, links e botoes que o perfil nao pode usar
- smoke tests visuais basicos confirmaram coerencia com a matriz V1: `Consulta/visualizacao` ve as listagens da `biblioteca` sem botoes de criacao; `Operador biblioteca` e `Gestao administrativa` veem navegacao e criacao em `biblioteca`; `Operador financeiro` acessa `SiteConfig /` e nao recebe navegacao funcional da `biblioteca`

## Recuperacao de senha V1 e alinhamento institucional do login

- a auditoria inicial confirmou que o nome exibido no login estava hardcoded em `configuracoes/templates/configuracoes/login.html` como `Casa Espirita`, em vez de vir do cadastro institucional real
- a tela de login passou a receber `site_name` dinamico a partir de `SiteConfig.site_name`, com fallback seguro, por meio do novo `ConfiguracoesIdentidadeMixin`
- foi criada uma base minima compartilhada para autenticacao em `configuracoes/templates/configuracoes/auth_base.html`, mantendo o layout enxuto existente e adicionando o link `Esqueci minha senha`
- o fluxo nativo do Django para reset de senha foi integrado com views/rotas/templates proprios: solicitacao, confirmacao de envio, definicao de nova senha e conclusao
- `casa_espirita/urls.py` passou a expor `admin_password_reset` em `/admin/password_reset/`, sem misturar isso com permissao funcional nem com bypass de `/admin/`
- foi criado `ConfiguracoesPasswordResetForm` para barrar e-mail sem usuario ativo/utilizavel correspondente e evitar promessa falsa de reset funcional
- `settings.py` passou a aceitar configuracao real de e-mail por variaveis de ambiente, com fallback para `django.core.mail.backends.console.EmailBackend`; assim, em desenvolvimento o fluxo funciona sem quebrar e registra a mensagem no console do servidor
- smoke tests confirmaram login `200`, nome institucional dinamico, link `Esqueci minha senha`, formulario de reset `200`, `admin_password_reset` `200`, geracao local do e-mail, link de redefinicao funcional, troca efetiva da senha e erro claro para e-mail inexistente

## Regra minima de usuarios com e-mail obrigatorio e perfil-base operacional

- a auditoria do repositorio confirmou que, nesta fase, o cadastro/edicao de usuarios do sistema continua acontecendo apenas pelo `/admin/` tecnico; nao existe ainda fluxo funcional proprio para gerenciar usuarios
- `configuracoes/admin.py` passou a substituir o `UserAdmin` padrao por uma versao endurecida, com `perfil_base` exposto no mesmo formulario tecnico e persistencia sincronizada com `UsuarioPerfilAcesso`
- a abordagem escolhida foi um endurecimento incremental do fluxo existente no admin tecnico, em vez de abrir nova UI funcional nesta microetapa
- `configuracoes/forms.py` passou a concentrar as regras minimas da V1:
  - e-mail obrigatorio para usuario ativo ou administrador tecnico
  - e-mail unico no fluxo administrativo, validado de forma pratica no formulario
  - perfil-base obrigatorio para usuario funcional ativo
  - `staff`/`superuser` tecnico podem permanecer sem perfil funcional, preservando a separacao entre administracao tecnica/global e acesso funcional
- a auditoria do banco mostrou que nao havia usuarios sem e-mail nem e-mails duplicados, mas havia tres usuarios sem perfil-base: `Luciano`, `reset_flow_tmp` e `semperfil_cfg`
- como `Luciano` e superusuario tecnico com e-mail valido, ele permaneceu ativo sem perfil funcional implicito; os usuarios funcionais ativos sem perfil (`reset_flow_tmp` e `semperfil_cfg`) foram saneados com a migration `configuracoes/migrations/0006_regularizar_usuarios_funcionais_sem_requisitos.py`, que os desativou ate regularizacao manual no `/admin/`
- a estrategia de saneamento foi propositalmente conservadora: nao foram gerados e-mails ficticios, nao houve atribuicao automatica de perfil-base e nao foi criado bypass funcional para usuarios sem vinculo regular
- smoke tests confirmaram: bloqueio de criacao administrativa para usuario funcional ativo sem e-mail, bloqueio para usuario funcional ativo sem perfil-base, permissao de `staff` tecnico com e-mail sem perfil funcional, reset por e-mail ainda valido para superusuario regularizado com e-mail e `py manage.py check` sem erros

## Navegacao global autenticada com portal inicial por modulos

- a microetapa criou uma navegacao global autenticada minima do sistema, sem abrir refactor amplo de layout nem UI propria de perfis
- foi criada a camada central `configuracoes/context_processors.py`, que injeta no template o nome institucional, o usuario autenticado, o perfil-base atual, as URLs globais (`inicio`, `logout`, `admin tecnico`) e a lista de modulos liberados por permissao real
- `configuracoes/permissoes.py` passou a concentrar tambem o catalogo de modulos visiveis (`Financeiro`, `Biblioteca`, `Configuracoes`) e a funcao `obter_modulos_disponiveis(usuario)`, evitando logica ad hoc espalhada pelos templates
- foi criado o portal autenticado `/inicio/` com `SistemaInicioView` e os templates `configuracoes/sistema_base.html` e `configuracoes/inicio.html`, tratados como ponto de entrada do sistema-mae apos login
- `LOGIN_REDIRECT_URL` deixou de apontar para `/financeiro/` e passou a apontar para `/inicio/`
- o portal mostra apenas os modulos realmente liberados ao usuario:
  - `Operador financeiro` ve `Financeiro` e `Configuracoes`
  - `Operador biblioteca` ve `Biblioteca` e `Configuracoes`
  - `Consulta/visualizacao` ve `Financeiro`, `Biblioteca` e `Configuracoes`
  - usuario autenticado sem perfil funcional nao ganha modulo operacional e ve apenas o estado seguro sem cards
- o shell autenticado minimo passou a expor `Sair` de forma visivel e consistente, alem de `Inicio` do sistema; no caso de usuario `staff`, o atalho para `Admin tecnico` continua separado como administracao tecnica/global
- `financeiro/base.html`, `biblioteca/base.html` e `configuracoes/siteconfig_detail.html` foram ajustados apenas no necessario para refletir essa navegacao global, sem alterar o enforcement funcional ja aprovado no backend
- smoke tests confirmaram redirecionamento pos-login para `/inicio/`, portal coerente por perfil, logout com retorno a `/login/` e comportamento deny-by-default preservado para usuario sem perfil

## UI funcional minima de perfis e vinculo usuario -> perfil base

- a microetapa abriu, dentro de `configuracoes`, a primeira UI funcional minima para administracao de acesso fora do `/admin/`, sem substituir o admin tecnico nem abrir editor completo da matriz
- foram criadas as rotas e views:
  - listagem de perfis-base
  - detalhe do perfil
  - listagem de usuarios com perfil atual
  - edicao simples do vinculo `usuario -> perfil base`
- a visualizacao do detalhe do perfil foi organizada por `modulo -> recurso -> acoes`, usando a propria base `PermissaoSistema`/`PerfilAcesso` ja implantada e priorizando leitura clara sobre edicao
- a listagem de usuarios mostra identificacao, e-mail, status ativo/inativo, indicacao de administracao tecnica e perfil-base atual, com acao direta de edicao do vinculo
- a edicao do vinculo passou a usar um formulario simples e seguro:
  - usuario funcional ativo precisa de perfil-base
  - usuario funcional sem e-mail valido nao recebe perfil pela UI
  - `staff`/`superuser` tecnico podem seguir sem perfil funcional, preservando a separacao entre administracao tecnica/global e acesso funcional
- foram criadas quatro novas permissoes funcionais canonicas para essa area:
  - `configuracoes.perfis_acesso.listar`
  - `configuracoes.perfis_acesso.visualizar`
  - `configuracoes.usuarios_acesso.listar`
  - `configuracoes.usuarios_acesso.editar_perfil`
- essas permissoes foram semeadas por migration incremental e vinculadas apenas a `Administrador geral` e `Gestao administrativa`, mantendo a administracao funcional de acesso restrita a esses perfis na V1
- a entrada visual da nova area ficou no modulo `Configuracoes`: `siteconfig_detail.html` passou a exibir `Perfis de acesso` e `Usuarios e perfis` apenas para quem possui permissao dessa frente
- smoke tests confirmaram o desenho final:
  - `Administrador geral`: `200` em perfis, detalhe, usuarios e alteracao de vinculo
  - `Gestao administrativa`: `200` em perfis, detalhe e usuarios
  - `Operador financeiro`: `403` nas rotas da area
  - alteracao de perfil base persistindo corretamente no banco

## Polimento final de autenticacao/acesso

- a tela de `login` recebeu controle de `Mostrar/Ocultar` senha no proprio campo, com rotulagem acessivel e sem alterar o backend de autenticacao
- o fluxo de recuperacao de senha passou de validacao explicita de e-mail existente para resposta neutra: `ConfiguracoesPasswordResetForm` voltou a seguir o fluxo nativo do Django, reduzindo enumeracao de usuarios e mantendo a confirmacao em `password_reset_done`
- a decisao adotada foi manter a mensagem de reset neutra daqui em diante, porque a frente de acesso ja saiu da fase de bootstrap e o endurecimento contra descoberta de usuarios passa a ser mais importante do que a mensagem explicita de erro
- o texto do formulario de reset e da tela de confirmacao foi revisado para deixar essa neutralidade clara sem prometer envio real fora das configuracoes disponiveis no ambiente
- o portal autenticado `/inicio/` passou a diferenciar melhor `usuario sem perfil funcional` de `usuario autenticado sem modulos liberados`, com chamada visual mais compreensivel e acoes de `Sair` e `Admin tecnico` quando aplicavel
- as listagens da UI funcional minima de perfis e usuarios ganharam estados vazios explicitos, evitando tabela ou grade silenciosa quando nao houver dados
- a verificacao do nome institucional confirmou que o login continua lendo `SiteConfig.site_name` em runtime; no ambiente local auditado, o valor atual (`Lar de Teste`) apareceu corretamente na tela
- a avaliacao da unicidade do e-mail foi refeita: a base atual continua sem duplicados, mas a microetapa nao promoveu isso a constraint de banco porque o sistema ainda usa o `User` padrao do Django e a mudanca estrutural para endurecimento no nivel da tabela `auth_user` nao compensa o risco neste momento; a validacao administrativa forte permanece como guarda atual
- smoke tests confirmaram:
  - login `200` com botao de mostrar/ocultar senha presente
  - reset com e-mail inexistente seguindo para a confirmacao neutra
  - portal de usuario sem perfil com mensagem clara
  - `Gestao administrativa` ainda com `200` na UI funcional de perfis
  - `Operador financeiro` ainda com `403` nessa area
  - logout retornando para `/login/`

## Consolidacao do shell autenticado compartilhado

- `configuracoes/templates/configuracoes/sistema_base.html` foi consolidado como shell autenticado oficial do sistema, recebendo slots reutilizaveis para topbar, navegacao local de modulo, area principal, mensagens e extensoes de cada app
- foi criado o parcial `configuracoes/templates/configuracoes/_sistema_usuario_acoes.html` para centralizar a renderizacao de usuario, perfil-base e links globais (`Inicio`, `Admin tecnico`, `Sair`) sem duplicacao ad hoc
- `biblioteca/templates/biblioteca/base.html` passou a derivar diretamente da base autenticada global, reduzindo markup repetido e mantendo no modulo apenas a navegacao local e ajustes visuais leves
- `configuracoes/templates/configuracoes/siteconfig_detail.html` tambem passou a operar sobre essa base global, eliminando a topbar local duplicada e preservando o conteudo institucional e os atalhos funcionais da area
- no `financeiro`, a base propria permaneceu por necessidade estrutural da sidebar, do drawer mobile e do JS ja consolidado, mas o topo do modulo passou a consumir o mesmo parcial compartilhado de identidade/acoes globais, alinhando a experiencia sem reabrir a arquitetura sensivel da lateral
- a decisao tecnica desta etapa foi consolidar uma base autenticada oficial + derivacoes modulares quando necessario, em vez de forcar uma heranca unica abrupta sobre o `financeiro`; isso reduz duplicacao real agora e preserva estabilidade funcional
- a hierarquia resultante ficou: `configuracoes/sistema_base.html` como shell global; `biblioteca/base.html` como derivacao leve; `siteconfig_detail.html` aderido ao mesmo shell; `financeiro/base.html` permanecendo especializado, mas ja conectado aos mesmos componentes globais reutilizaveis
- validacao tecnica executada: `py manage.py check` OK

## Normalizacao das entradas canonicas dos modulos

- auditoria de rotas confirmou o estado real anterior:
  - `financeiro/` existia e redirecionava para `lancamentos/`
  - `biblioteca/` retornava `404` por falta de rota-raiz no app
  - `configuracoes/` retornava `404` porque o modulo estava funcionalmente exposto apenas na raiz por `site-config`
- a correcao foi mantida pequena e compatível com o shell global ja aprovado:
  - `biblioteca/urls.py` ganhou a rota-raiz `biblioteca:home`
  - `biblioteca/views.py` ganhou `BibliotecaHomeRedirectView`, que resolve a primeira tela liberada ao usuario conforme as permissoes reais do modulo
  - `casa_espirita/urls.py` passou a expor `/configuracoes/` como entrada canonica explicita do modulo, reutilizando `SiteConfigDetailView`
  - `configuracoes/permissoes.py` atualizou o catalogo central do portal para apontar `Biblioteca` para `biblioteca:home` e `Configuracoes` para `configuracoes-entrada`
- decisao final por modulo:
  - `financeiro`: manter `/financeiro/` como entrada canonica com redirect para a principal tela operacional atual
  - `biblioteca`: usar `/biblioteca/` como entrada canonica com redirect seguro para a primeira area de leitura permitida
  - `configuracoes`: usar `/configuracoes/` como entrada canonica explicita para `SiteConfig`, preservando as rotas de autenticacao e portal existentes na raiz
- o portal `/inicio/` deixou de depender de conhecimento interno dos modulos e passou a apontar apenas para essas entradas oficiais
- validacao tecnica executada: `py manage.py check` OK; a verificacao automatizada das entradas canonicas ficou alinhada ao contrato novo de URLs sem manter `404` indevido nas rotas-raiz dos modulos
## Retorno contextual, filtros preservados e acao `+` nos formularios financeiros

- a frente de fluxo operacional do `financeiro` foi tratada de forma estrutural no mixin comum dos formularios/exclusoes, em vez de corrigir apenas um template isolado
- foi criado o contrato de `return_to` validado no backend com `url_has_allowed_host_and_scheme`; URLs externas ou inseguras sao descartadas e o fluxo volta para o `success_url` padrao da view
- `FinanceiroFormMixin` passou a expor `cancel_url`, `return_to`, `allow_save_and_stay` e `save_and_stay_param` para os templates; `FinanceiroDeleteMixin` passou a reaproveitar a mesma regra para exclusoes
- `Salvar` permanece como acao principal e retorna para a URL contextual quando ela existe; o botao compacto `+` envia `salvar_permanecer=1`, salva o registro e reabre a mesma tela de criacao preservando o `return_to`
- a acao `+` foi habilitada nos cadastros de `ContaFinanceira`, `PessoaFinanceira`/favorecido, `CentroCusto`, `CategoriaFinanceira` e `LancamentoFinanceiro`; clones de lancamento ficaram sem `+` por serem fluxos derivados e menos seguros para cadastro em lote
- as listagens `lancamento_list`, `conta_list`, `pessoa_list`, `categoria_list` e `centro_custo_list` passaram a anexar a URL completa atual nos links de criacao/edicao/exclusao, preservando filtros, pagina, ordenacao, `por_pagina` e preferencias de colunas quando estiverem na querystring
- o formulario coordenado de rateio tambem passou a preservar a origem ao cancelar, voltar para a linha representativa ou salvar o grupo
- templates ajustados: `conta_form`, `pessoa_form`, `categoria_form`, `centro_custo_form`, `lancamento_form`, `lancamento_rateio_grupo_form`, `confirm_delete` e as cinco listagens principais do financeiro
- validacao executada: `py manage.py check` OK, `py -m compileall financeiro` OK e smoke test com Django `Client` confirmando listagem com links contendo `return_to`, formulario de conta com campo oculto de retorno, botao `+` visivel e cancelamento preservando a URL filtrada

## Criação da estrutura de governança com AGENTS, skills, índice e regras

Foi criada uma estrutura inicial de governança para otimizar o desenvolvimento com GPT/ChatGPT e Codex:

Arquivos criados:

- AGENTS.md
- .agents/skills/docs-governanca/SKILL.md
- .agents/skills/financeiro-regras/SKILL.md
- .agents/skills/relatorios-impressao/SKILL.md
- .agents/skills/ux-padrao/SKILL.md
- .agents/skills/importacao-dados/SKILL.md
- docs/INDICE_PROJETO.md
- docs/REGRAS_NEGOCIO.md

Objetivo da etapa:

- reduzir consumo de tokens;
- evitar perda de contexto entre chats;
- estabelecer ponto de entrada curto para leitura do projeto;
- separar cérebro estratégico, executor técnico e aprovação do usuário;
- preservar os documentos existentes sem apagar histórico.

Não houve alteração de código funcional nesta etapa.

## Microetapa: UX de filtros dependentes no Balancete

- ajuste aplicado apenas no frontend do Balancete Institucional para exibir/ocultar imediatamente o filtro `Detalhar patrimônio vinculado` ao trocar `Formato do Balancete`
- implementação feita com script local no template, sem criar JS global e sem alterar lógica financeira
- filtros ficaram com comportamento imediato na tela, e a geração do relatório continua dependente apenas do clique em `Atualizar balancete`
- validações e testes da suíte `financeiro.tests` executados nesta etapa
- sem alteração de cálculo, saldos, regras de negócio financeira, models ou migrations
## Microetapa: correcao real da visibilidade do filtro patrimonial

- a validacao pratica da usuaria confirmou que a etapa anterior nao ocultou o filtro dependente de forma efetiva
- causa provavel identificada: `hidden` isolado nao garantiu ocultacao visual robusta no layout atual
- correcao implementada no template com controle combinado (`hidden`, `is-hidden` e `display: none`) no estado inicial e no evento de mudanca do `Formato do Balancete`
- regra final validada:
  - `operacional`: filtro oculto
  - `operacional_patrimonio`: filtro visivel
  - `financeiro_completo`: filtro oculto
- teste reforcado para validar estado inicial renderizado por formato (nao apenas existencia do script)
- sem alteracao de calculo financeiro, saldos, regras financeiras, models ou migrations
## Microetapa: aceite final funcional e de UX do Balancete Institucional

- etapa exclusivamente documental para registrar aceite final da usuaria apos validacao pratica
- aceite consolidado:
  - arquitetura por `Formato do Balancete` aprovada
  - tres formatos aprovados (`Operacional`, `Operacional + patrimonio vinculado`, `Financeiro completo`)
  - filtro antigo de exibicao de vinculadas permanece removido da interface
  - filtro dependente `Detalhar patrimonio vinculado` aprovado com exibicao somente em `operacional_patrimonio` e troca imediata ao mudar o formato
- regra funcional consolidada:
  - saldo operacional nao se mistura ao patrimonio vinculado no resumo operacional
  - transferencias entre operacional e vinculado seguem como movimentacao especifica de fronteira, sem virar receita/despesa operacional
- congelamento registrado: nao reabrir a logica do Balancete sem nova decisao explicita da usuaria
- sem alteracao de codigo, calculo financeiro, saldos, lancamentos, Extrato, Fechamento/Prestacao ou demais relatorios
## Microetapa: levantamento e classificacao das proximas pendencias do financeiro

- etapa exclusivamente documental/backlog apos aceite final do Balancete Institucional
- consolidado como frente encerrada: Balancete aprovado funcionalmente e em UX, com logica congelada no recorte atual
- pendencias classificadas em seis grupos:
  - implementado e aprovado
  - implementado, mas requer validacao da usuaria
  - modelado/documentado, mas nao implementado
  - pendente tecnico recomendado
  - futuro/backlog nao prioritario
  - risco documental/divergencia a conferir
- recomendacao de fila curta:
  1) homologacao real de importacoes (planilhas historicas completas e cadastros auxiliares)
  2) validacao visual final de relatorios impressos em volume real (com foco no Extrato)
  3) auditoria preparatoria da frente de frequencia/recorrencia por competencia
- sem alteracao de codigo, calculo financeiro, saldos, lancamentos, Extrato, Fechamento/Prestacao ou regras de negocio aprovadas
## Microetapa: auditoria e consolidacao do MVP de contribuicao mensal por competencia

- etapa exclusivamente documental/técnica preparatória, sem implementação
- auditoria confirmou que a frente está modelada em `CEREBRO_PROJETO.md`, `ROADMAP_FINANCEIRO.md` e `MAPA_RECLASSIFICACAO.md`, mas ainda sem campos/fluxo funcional no código
- consolidado do MVP recomendado:
  1) flags mínimas em favorecido e subcategoria
  2) matriz mensal com valores por competência
  3) matriz sem valores (indicador de frequência)
  4) termo por favorecido em segunda etapa
- decisões pendentes da usuária registradas para fechamento da SPEC funcional
- sem alteração de código, models, migrations, forms, views, urls, templates, tests, CSS ou cálculos financeiros
## Microetapa: base cadastral minima de frequencia mensal por competencia

- implementacao funcional restrita aos cadastros, sem alterar lancamentos e sem criar matriz
- criado campo booleano `contribuinte_recorrente` em `PessoaFinanceira` (default `False`)
- criado campo booleano `controla_recorrencia_competencia` em `CategoriaFinanceira` (default `False`)
- campos expostos em formularios, listagens e admin
- importacao/exportacao auxiliar de `pessoas` e `categorias` atualizada para incluir os novos campos
- migration criada para manter compatibilidade dos dados existentes com defaults seguros
- sem alteracao de calculo financeiro, saldos, Balancete, Extrato, Fechamento/Prestacao e regras de lancamento

## Microetapa: competencias mensais no rateio controlado

- implementada a captura de `Competencias atendidas` tambem no fluxo de rateio, sem criar matriz mensal
- a regra passou a comparar a soma das competencias apenas com o valor da subcategoria controlada no rateio, e nao com o valor bruto total do documento
- recebimentos mistos permanecem seguros: so a parte da subcategoria controlada entra na frequencia; itens nao controlados continuam fora
- a criacao inicial com rateio e a edicao coordenada do grupo passaram a persistir/remover alocacoes conforme as linhas finais controladas
- favorecido nao recorrente ou rateio sem subcategoria controlada continuam sem exigir competencias
- clone de rateio continua sem copiar competencias automaticamente
- sem alteracao de calculo financeiro, saldos, Balancete, Extrato, Fechamento/Prestacao ou demais relatorios existentes

## Microetapa: registro de pendencias apos competencias no rateio

- etapa exclusivamente documental, sem alteracao de codigo
- nova frente registrada: auditoria acionavel (backlog com SPEC propria obrigatoria)
- pendencia registrada na listagem de lancamentos: ausencia de acoes esperadas (exclusao/recibo) em alguns casos, com necessidade de auditoria tecnica/UX dedicada
- regra recomendada registrada para proxima implementacao: impedir duplicidade de mes/ano dentro do mesmo lancamento e da mesma subcategoria controlada, em simples e rateio
- mensagem orientativa sugerida para essa validacao futura:
  - `Ja existe uma competencia informada para este mes/ano. Agrupe o valor em uma unica linha.`
- regra de exclusao atual reafirmada: alocacoes de competencia continuam em cascade com a linha/lancamento vinculado

## Microetapa: correcao das acoes na listagem de lancamentos

- causa raiz confirmada: o template da listagem escondia `recibo` e `excluir` para linhas `eh_rateio`, por condicao fixa, mesmo quando a usuaria tinha permissao e a linha agrupada era elegivel
- ajuste aplicado na listagem:
  - URLs de `recibo` e `excluir` passaram a ser resolvidas no backend por tipo de linha visual (simples x rateio)
  - lancamentos simples, inclusive com competencia mensal, continuam com as acoes esperadas quando permitidas
  - lancamentos rateados/agrupados passaram a exibir:
    - recibo de grupo por favorecido (quando todas as linhas do grupo forem receitas e com favorecido)
    - exclusao de grupo por rota dedicada de confirmacao/exclusao
- nova rota funcional: exclusao de grupo rateado com transacao unica e auditoria por linha excluida
- cobertura de testes adicionada:
  - acoes completas em simples, simples com competencia e rateio
  - ocultacao de `Excluir` quando a permissao nao existe
  - exclusao de grupo removendo linhas e alocacoes vinculadas
- sem alteracao de calculo financeiro, saldos, regras de competencia/rateio, Balancete, Extrato, Fechamento/Prestacao ou demais relatorios

## Microetapa: alinhamento da permissao na exclusao de rateio

- investigacao confirmou alinhamento de regra: exclusao simples e exclusao de grupo rateado usam `financeiro.lancamentos.excluir`
- o catalogo de permissoes segue com esse codigo ativo e vinculado aos perfis administrativos previstos na matriz
- ajuste aplicado para evitar discrepancia de UX/permissao:
  - a view da listagem passou a gerar `recibo_url` e `excluir_url` apenas quando a permissao correspondente existe no usuario autenticado
  - o template passou a renderizar os botoes a partir dessas URLs autorizadas
- testes reforcados para cobrir:
  - GET/POST de exclusao de grupo rateado com permissao
  - bloqueio 403 sem permissao
  - manutencao da exclusao simples sob a mesma permissao
- sem alteracao de calculo financeiro, saldos, regras de rateio/competencia ou relatorios do modulo

## Microetapa: restauracao do acesso a listagem de lancamentos

- a investigacao confirmou que a listagem principal continua exigindo `financeiro.lancamentos.listar`; a regressao percebida nao veio de troca de permissao na `LancamentoFinanceiroListView`
- o catalogo funcional permanece correto para essa leitura: `financeiro.lancamentos.listar` existe e segue vinculado aos perfis `administrador-geral`, `gestao-administrativa`, `operador-financeiro` e `consulta-visualizacao`
- causa operacional identificada na base local: usuario autenticado sem vinculo `UsuarioPerfilAcesso` nao recebe permissao funcional nenhuma e, por desenho da V1, fica bloqueado com `403`
- a listagem permaneceu acessivel para quem tem `listar`, mesmo sem `emitir_recibo` e sem `excluir`; nesses cenarios os botoes sensiveis so deixam de ser renderizados
- a bateria de testes passou a cobrir explicitamente:
  - acesso `200` com apenas `financeiro.lancamentos.listar`
  - ocultacao de `Recibo`/`Excluir` quando essas permissoes nao existem
  - bloqueio `403` para usuario sem `financeiro.lancamentos.listar`
- sem alteracao de calculo financeiro, saldos, regras de rateio/competencia ou relatorios do modulo

## Microetapa: correcao emergencial do bloqueio da listagem

- nova auditoria com foco no 403 da propria rota confirmou que os commits `d0001c5` e `1f97bcd` nao mudaram a permissao-base da listagem; `LancamentoFinanceiroListView` continuou exigindo `financeiro.lancamentos.listar`
- a causa concreta do bloqueio no ambiente local foi de dados funcionais: nao havia nenhum `UsuarioPerfilAcesso` persistido, inclusive para o usuario principal utilizado nos acessos reais
- como a V1 mantem deny-by-default sem bypass funcional para superusuario, o usuario logado ficava bloqueado em `/financeiro/lancamentos/` mesmo com a matriz e o catalogo corretos
- restauracao operacional aplicada:
  - religacao do usuario principal local ao perfil-base `administrador-geral`
  - smoke test HTTP local com `HTTP_HOST=127.0.0.1` retornando `200` para a listagem
- a regra funcional permaneceu a mesma:
  - `financeiro.lancamentos.listar` abre a tela
  - falta de `emitir_recibo` e/ou `excluir` apenas oculta as acoes elegiveis
- nao foi necessario reverter a logica recente de `Recibo`/`Excluir`; a exclusao de grupo rateado permaneceu protegida por `financeiro.lancamentos.excluir`

## Microetapa: limpeza segura de dados sinteticos na listagem real

- a investigacao encontrou no codigo de testes exatamente os padroes exibidos na base local:
  - `P-LIST`, `Favorecido listagem`, `Conta listagem`
  - `Receitas listagem`, `Contribuicao listagem`, `Livro listagem`
  - `LIST-001`, `LIST-002`, `LIST-003`, `grp-list-acoes`
- leitura do `db.sqlite3` confirmou contaminacao local real:
  - 1 pessoa sintetica
  - 1 conta sintetica
  - 3 categorias sinteticas
  - 4 lancamentos sinteticos
  - 1 usuario tecnico sintetico (`debug-list`)
- comparacao com `db.sqlite3_BACKUP_ANTES_LIMPEZA_TESTES.sqlite3` mostrou que o backup foi tirado ja com a contaminacao presente; ele preserva o estado antes da limpeza, mas nao um estado limpo anterior
- a suite oficial `py manage.py test financeiro.tests` continuou executando em banco de teste isolado, sem evidenciar uso do `db.sqlite3` real; por isso, a causa provavel ficou registrada como criacao manual/interativa de fixtures inspiradas nos testes, e nao falha do runner automatizado
- limpeza local aplicada com transacao unica e filtros explicitos:
  - exclusao dos 4 lancamentos sinteticos
  - exclusao da pessoa `P-LIST`
  - exclusao da conta `Conta listagem`
  - exclusao das 3 categorias sinteticas ligadas a esse conjunto
  - exclusao do usuario `debug-list`
- a primeira tentativa falhou com `ProtectedError` ao apagar a categoria pai antes das filhas; como a operacao estava em transacao, nada ficou parcialmente removido
- validacao final:
  - listagem abriu com `200`
  - `P-LIST`, `Conta listagem` e `Receita simples` deixaram de aparecer no HTML da tela
  - demais cadastros reais permaneceram no banco
- nenhuma alteracao de codigo funcional foi necessaria nesta etapa; a baixa foi local/documental, sem mexer em calculo, saldos, rateio, competencias ou relatorios
