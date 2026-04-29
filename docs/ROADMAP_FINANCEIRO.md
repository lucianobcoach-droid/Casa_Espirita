# ROADMAP FINANCEIRO

Data: 2026-04-23

## 0.17. Balancete Institucional como relatorio proprio futuro

Este bloco registra a revisao da direcao conceitual anterior. A Prestacao/Fechamento atual permanece como relatorio analitico/gerencial ja validado; o Balancete Institucional deve nascer futuramente como relatorio proprio, com finalidade formal/documental. Nao representa implementacao concluida.

1. **Balancete Institucional**
   - Classificacao: FRENTE FUTURA DE RELATORIO / IMPRESSAO.
   - Prioridade documental: MEDIA.
   - Direcao revisada: criar relatorio proprio chamado `Balancete Institucional`, sem substituir a Prestacao/Fechamento atual.
   - Base de calculo: reutilizar a mesma regra/base de calculo da Prestacao/Fechamento, evitando divergencia de resultado e evitando duplicar regra financeira em dois lugares diferentes.
   - Status tecnico: MVP funcional iniciado com rota, view, template proprio, link em Relatorios, filtros essenciais, reaproveitamento de `montar_contexto_fechamento_periodo` e duas assinaturas selecionaveis pelo cadastro existente; refinamento visual/documental inicial aplicado no cabecalho, abrangencia impressa e ocultacao padrao de contas zeradas.
   - Apresentacao: template/documento proprio, com fundo branco, linhas compactas, secoes numeradas, valores alinhados a direita, fechamento do saldo disponivel, composicao final do saldo e aparencia institucional.
   - Regras preservadas: manter receitas/despesas separadas, transferencias fora do resultado operacional e transferencias compondo saldo apenas quando necessarias conforme escopo de contas.
   - Impressao: priorizar uma pagina quando o volume permitir; quando o relatorio for grande, quebrar paginas de forma clara e organizada, sem assinatura ou blocos finais isolados de maneira ruim.
   - Assinaturas: prever duas assinaturas, considerando o cadastro manual de assinaturas ja existente e futura definicao/selecao de duas assinaturas padrao para este documento.
   - Historico da decisao: a direcao anterior falava em evoluir a Prestacao/Fechamento para modelo tipo balancete; a direcao revisada mantem a Prestacao/Fechamento como relatorio analitico e separa o Balancete como documento proprio.

## 0.16. Pendencias documentadas apos correcao da edicao de contas

Este bloco registra pendencias levantadas pela usuaria para continuidade do financeiro. Nao representa implementacao concluida.

1. **Padronizacao do filtro de contas nas telas com selecao de contas**
   - Classificacao: MELHORIA DE UX + PADRONIZACAO TRANSVERSAL.
   - Prioridade documental: MEDIA.
   - Direcao: aplicar progressivamente o padrao visual/comportamental validado no filtro de contas do Extrato em outras telas que possuam selecao de contas, em microetapas separadas por tela ou conjunto minimo seguro.
   - Status: executado para as telas analiticas Resumo, Fechamento/Prestacao e Evolucao por categorias; listagem de lancamentos permanece em pendencia propria.

2. **Refinamento de impressao da Prestacao/Fechamento do periodo**
   - Classificacao: AJUSTE VISUAL DE RELATORIO / IMPRESSAO.
   - Prioridade documental: MEDIA.
   - Direcao: compactar margens, espacamentos e quebras de pagina do PDF/impresso da Prestacao/Fechamento, sem alterar calculos.
   - Status: executado ajuste de compactacao do modo print/PDF, sem alteracao de calculos.

## 0.15. Pendencias levantadas apos Extrato multi-contas

Este bloco registra pendencias novas levantadas pela usuaria apos a correcao do Fechamento/Prestacao e a implementacao do Extrato com multiplas contas. Nao representa implementacao concluida.

### Bugs / correcoes operacionais proximas

0. **Regra geral de identificadores-chave nos cadastros**
   - Classificacao: REGRA DE NEGOCIO + MELHORIA FUNCIONAL progressiva.
   - Prioridade documental: ALTA como diretriz; execucao incremental por cadastro.
   - Direcao: aplicar progressivamente a regra de nao duplicar identificadores-chave, como codigo, nome ou equivalentes, em contas financeiras, categorias/subcategorias, centros de custo e demais cadastros atuais ou futuros.
   - Observacao: nesta microetapa pratica, a implementacao fica restrita a favorecidos/pessoas financeiras.

1. **Favorecido duplicado por nome**
   - Classificacao: BUG / correcao operacional + REGRA DE NEGOCIO.
   - Prioridade documental: ALTA.
   - Direcao: impedir duplicidade por nome normalizado, preservando dados existentes e avaliando tratamento de duplicados ja cadastrados.

2. **Edicao de conta deve trazer saldo inicial e data do saldo ja cadastrados**
   - Classificacao: BUG / correcao operacional.
   - Prioridade documental: ALTA.
   - Direcao: ao abrir edicao de conta, os campos de saldo inicial e data do saldo devem aparecer preenchidos com os valores atuais.

3. **Conta inativa em novos lancamentos e relatorios historicos**
   - Classificacao: REGRA DE NEGOCIO + correcao operacional.
   - Prioridade documental: ALTA.
   - Direcao: conta inativa nao deve aparecer para novos lancamentos, mas deve continuar disponivel em relatorios quando tiver movimento no periodo selecionado.

4. **Favorecido em transferencia no Extrato**
   - Classificacao: MELHORIA DE UX + correcao operacional.
   - Prioridade documental: MEDIA.
   - Direcao: em lancamentos de transferencia, o Extrato deve apresentar o favorecido como `Transferencia entre contas` quando nao houver favorecido operacional.

### Melhorias operacionais

5. **Diferenca restante no rateio**
   - Classificacao: MELHORIA FUNCIONAL + MELHORIA DE UX.
   - Prioridade documental: MEDIA.
   - Direcao: no fluxo de lancamento com rateio, mostrar o valor que ainda falta para fechar o valor total do documento.

6. **Filtro multi-contas na listagem de lancamentos**
   - Classificacao: MELHORIA FUNCIONAL + MELHORIA DE UX.
   - Prioridade documental: MEDIA.
   - Direcao: permitir selecionar mais de uma conta na listagem de lancamentos, reaproveitando a experiencia aprovada no Extrato multi-contas quando fizer sentido.

### Frente futura grande

7. **Tabelas personalizadas de controle**
   - Classificacao: FRENTE FUTURA GRANDE.
   - Prioridade documental: FUTURA / BAIXA para execucao imediata.
   - Direcao: disponibilizar futuramente cadastros de controles configuraveis, como energia eletrica mensal, em que o usuario defina nome das colunas, formulas por celula e colunas com totalizadores.
   - Observacao: esta frente deve ser desenhada separadamente das correcoes imediatas do financeiro, pois envolve modelo estrutural proprio, validacao de formulas e experiencia de configuracao.

## 0.13. Base analitica consolidada e retomada da padronizacao visual

- a tela `Evolucao por categorias` deixa de ser apenas uma entrega isolada e passa a ser a base atual do padrao analitico do sistema
- a estrutura consolidada dessa base fica registrada como:
  - titulo/contexto
  - filtro no topo da analise
  - KPIs
  - resultados
- nessa base, o filtro permanece no mesmo lugar estrutural quando resumido ou expandido
- a comparacao fica considerada consolidada para essa tela, incluindo:
  - `Periodo principal` e `Periodo comparativo`
  - reordenacao cronologica automatica
  - aviso discreto
  - barra do separado por magnitude absoluta
  - texto monetario com sinal real
  - tabela comparativa com semantica visual pela natureza do item
- a prioridade operacional volta a ser a propagacao controlada desse padrao para as demais telas analiticas do `financeiro`
- ordem recomendada de propagacao:
  1. `Resumo`
  2. `Extrato`
  3. `Prestacao de contas`
- observacao:
  - esta secao registra a ordem correta de continuidade
  - nao significa que `Resumo`, `Extrato` e `Prestacao de contas` ja estejam repadronizados neste mesmo contrato visual

## 0.14. Frente futura de controle de frequencia/recorrencia por competencia

- fica registrada como nova frente futura do `financeiro` a camada de controle de frequencia/recorrencia orientada por competencia
- diretriz estrutural da frente:
  - combinar `favorecido/pessoa recorrente` + `subcategoria` como eixo principal de controle da recorrencia
  - usar competencia explicita como base oficial da frequencia
  - nao inferir frequencia apenas pela data do lancamento
  - sugerir automaticamente meses/competencias em aberto
  - permitir competencias futuras
  - permitir correcao manual da competencia
  - manter a frequencia independente do valor exato pago
  - estruturar a base de forma generica para outros recorrentes, como contas de consumo
- entregaveis futuros previstos dessa frente:
  - relatorio gerencial em modo `matriz mensal com valores por competencia`
  - relatorio gerencial em modo `matriz mensal sem valores`, apenas com indicador visual de frequencia
  - `Termo de quitacao em lote por favorecido`, trazendo:
    - competencias feitas ou nao
    - valor medio contribuido
    - valor total no periodo
    - periodo selecionado

## 0.12. Evolucao por categorias

- a frente de `relatorio grafico de evolucao por categorias` deixou de ser apenas ideia futura e passou a ter primeira entrega funcional no `financeiro`
- foi criada uma tela propria em `Relatorios` para acompanhar a evolucao mensal de categorias/subcategorias selecionadas
- filtros entregues na versao atual:
  - `data inicial`
  - `data final`
  - `data inicial` e `data final` do `periodo comparativo`, em preenchimento opcional
  - controle de escopo entre `categorias` e `subcategorias`
  - selecao multipla contextual conforme o escopo
  - selecao opcional de `contas`
  - `modo analitico` do grafico
  - `forma de leitura` (`consolidado` / `separado`)
  - `granularidade` (`dias` / `meses` / `trimestres` / `anos`)
  - `mostrar valores no grafico`
- modos entregues:
  - `Evolucao de categorias selecionadas`
  - `Comparativo entrada x saida`
  - `Comparacao entre periodos`
- regra consolidada nesta versao:
  - consolidacao mensal por `data_pagamento`, com fallback para `data_competencia`
  - `Categorias` listam apenas categorias pai e podem agregar automaticamente as subcategorias lancaveis
  - `Subcategorias` listam apenas subcategorias, com indicacao explicita da categoria pai
  - `Consolidado` soma os itens escolhidos em uma unica serie
  - `Separado` mostra uma serie por item selecionado
  - o modo `Comparativo entrada x saida` preserva os nomes reais das categorias/subcategorias escolhidas
  - a comparacao entre periodos e ativada automaticamente quando o `Periodo comparativo` e preenchido
  - a saida da comparacao passou a incluir `Periodo principal`, `Periodo comparativo`, diferenca absoluta e variacao percentual com tratamento seguro quando a base e zero
  - com `Periodo comparativo` preenchido e `Leitura = Consolidado`, a comparacao passa a usar um unico grafico de linhas com duas series (`Periodo principal` e `Periodo comparativo`)
  - com `Periodo comparativo` preenchido e `Leitura = Separado`, a tabela comparativa passa a ser a leitura principal para evitar poluicao visual por excesso de linhas, com apoio visual discreto em barras horizontais agrupadas por item
  - no grafico de apoio do comparativo separado, a tela exibe ate 8 itens priorizados por maior diferenca absoluta entre os periodos, mantendo a lista completa na tabela comparativa
  - a troca de `Escopo` atualiza imediatamente o seletor visivel e a busca, sem exigir submit apenas para trocar a interface
  - o submit de `Atualizar grafico` recalcula efetivamente grafico, KPIs e tabela de apoio
- entrega visual atual:
  - grafico SVG server-side
  - KPIs do periodo
  - tabela mensal de apoio recolhida por padrao
  - busca no seletor multiplo
  - acao `Imprimir relatorio`
  - toggle textual explicito para mostrar/ocultar a tabela mensal
- consolidacao visual/estrutural posterior:
  - a tela ficou madura como base atual do padrao analitico do sistema
  - o filtro permanece no topo da analise no mesmo lugar estrutural, resumido ou expandido
  - a hierarquia consolidada passa a ser `titulo/contexto -> filtro -> KPIs -> resultados`
- backlog remanescente relacionado:
  - avaliar se a tela deve ganhar exportacao futura da tabela mensal ou apenas permanecer como consulta visual
  - avaliar, por uso real, se convem expandir a comparacao para mais de dois agrupamentos operacionais alem de `entrada x saida`
  - avaliar se a comparacao entre periodos deve ganhar tabela comparativa mais rica ou exportacao propria em etapa futura

## 0.11. Trava de seguranca para importacoes por dominio preenchido

- a central de importacoes do `financeiro` passou a barrar importacoes quando o dominio de destino ja possui registros
- dominios cobertos:
  - `contas`
  - `favorecidos`
  - `categorias/subcategorias`
  - `centros de custo`
  - `lancamentos`
- regra consolidada:
  - importacao so pode acontecer em base vazia daquele dominio
  - se houver registros existentes, a operacao e bloqueada antes da validacao/conteudo da planilha
  - o bloqueio e acompanhado de mensagem clara indicando exatamente qual dominio precisa ser limpo ou redefinido
- essa trava nao substitui os fluxos de reset/limpeza ja existentes; ela passa a reforcar operacionalmente que nova carga deve acontecer apenas sobre dominio vazio
- backlog remanescente relacionado:
  - evoluir futuramente a experiencia de preflight/importacao para informar de forma ainda mais visivel o estado de preenchimento de cada dominio antes do upload

## 0.5. Execucao atual da frente de planilha comum com ate 5 rateios na mesma linha

- a frente antes mantida como futura de `exportacao/importacao comum de lancamentos com suporte a rateio em planilha` deixou de ser backlog e entrou em execucao real
- a decisao mais recente do usuario substituiu o contrato intermediario por multiplas linhas pelo novo contrato principal:
  - `1 linha = 1 documento`
  - ate `5` blocos de rateio na mesma linha
  - `valor_total_documento = soma dos blocos preenchidos`
- o contrato comum atual da planilha de lancamentos passou a cobrir:
  - lancamentos simples
  - transferencias simples
  - lancamentos com rateio em ate `5` blocos por documento
- a exportacao comum da listagem continua respeitando filtros, mas agora sai no mesmo contrato de `Modelo` + `Instrucoes` usado pela importacao
- a importacao comum continua transacional e sem criacao automatica de cadastros auxiliares, mas agora reconstroi lancamentos rateados diretamente no fluxo funcional do usuario
- compatibilidade preservada:
  - o layout simples legado continua aceito na importacao para nao quebrar arquivos antigos ja preparados
- limite conhecido e deliberado do fluxo comum:
  - grupos com mais de `5` linhas rateadas passam a ser bloqueados com mensagem clara na exportacao/importacao comum
  - nesses casos, o caminho tecnico de `backup/restauracao` continua sendo a excecao operacional segura
- backlog remanescente relacionado a esta frente:
  - preview mais rico antes de gravar
  - tratamento avancado de duplicidades
  - importacao parcial continua fora de escopo
  - refinamentos futuros de UX/mensagens da central conforme uso real

## 0.6. Refinamento de usabilidade da listagem principal de lancamentos

- a `lancamento_list` ganhou configuracao inicial de colunas para melhorar o uso real com a sidebar expandida, sem depender apenas de ajustes de largura em CSS
- o padrao inicial ficou enxuto, com `Data pagamento`, `Tipo`, `Descricao` e `Valor` como colunas essenciais da grade, alem de selecao/acoes quando as permissoes aplicarem
- campos complementares como `Favorecido`, `Conta origem`, `Conta destino`, `Status`, `Categoria`, `Centro de custo`, `Data competencia`, `Documento` e `Observacoes` passaram a poder ser exibidos/ocultados e ordenados manualmente
- a preferencia atual fica preservada em sessao, por ser a menor solucao segura sem criar estrutura nova de banco nesta etapa
- backlog futuro relacionado:
  - avaliar persistencia permanente por usuario em banco caso a configuracao de colunas precise sobreviver de forma mais robusta entre sessoes/navegadores
  - avaliar UI mais rica de ordenacao, como drag-and-drop, apenas se o uso real justificar

## 0.7. Novo bloco operacional: cadastros, lancamentos e extrato (lotes)

Diretriz geral:
- registrar itens de uso real em lotes coerentes, sem misturar tudo no mesmo patch

Itens levantados:
1. remover `Importar` da tela de lancamentos (importacao fica centralizada no menu)
2. gerar codigo automatico tambem nos demais cadastros, sem repetir codigo existente
3. permitir digitacao de valores monetarios sem virgula, com mascara pt-BR
4. cadastrar novo favorecido direto na tela de lancamentos, mantendo dados ja preenchidos
5. recibo em lote por favorecido, consolidando descricoes no mesmo recibo
6. checkbox `Exibir observacao` no extrato
7. corrigir protecao indevida ao excluir favorecido/pessoa apos desvinculo

Lotes definidos:
- Lote 1 (prioritario): itens 1, 3, 6 e 7 (executado)
- Lote 2: itens 2 e 4 (executado)
- Lote 3: item 5 (executado)

Entrega no Lote 2:
- geracao automatica de codigo quando vazio para `Favorecidos` e `Centros de custo`, preservando codigo manual
- fluxo rapido de `Novo favorecido` no lancamento preservando dados e retornando com o favorecido criado selecionado

Entrega no Lote 3:
- acao de recibo em lote na listagem de lancamentos
- validacao obrigatoria de mesmo favorecido, sem rateio e apenas receitas
- recibo unico consolidando descricoes e valor total

Observacao:
- `Exportacao` segue contextual nas listagens; `Importacao` permanece centralizada na pagina de importacoes do modulo

## 0.8. Historico por favorecido

- a frente de `historico por favorecido` foi executada como pagina operacional propria dentro do modulo `financeiro`
- a tela permite consultar os lancamentos vinculados a um favorecido, usando `data_pagamento` como data operacional principal e fallback para `data_competencia`
- filtros entregues: data inicial, data final, tipo, status, conta e busca textual por descricao ou documento
- totalizadores entregues: total geral, receitas, despesas, quitado e em aberto, sempre sobre o resultado filtrado
- acesso natural: acao `Historico` na listagem de `Favorecidos financeiros`
- nao foram incluidos nesta etapa: exportacao especifica do historico

## 0.9. Refinamento operacional de transferencias em relatorios

- `Resumo` e `Prestacao de Contas` passaram a oferecer opcao `Exibir transferencias`
- comportamento padrao preservado: transferencias continuam ocultas da leitura principal quando a opcao esta desligada
- quando a opcao esta ligada, transferencias quitadas do periodo aparecem em bloco proprio para conferencia operacional
- o bloco de transferencias inclui total movimentado e totalizadores separados de entrada e saida para leitura de aplicacoes/resgates entre contas
- regra mantida: transferencias nao entram como receitas nem despesas e nao alteram os totais principais desses relatorios
- o filtro de contas considera transferencias em que a conta selecionada aparece como origem ou destino
- na `Prestacao de Contas`, a leitura do universo de contas foi explicitada: o saldo consolidado considera apenas as contas selecionadas no relatorio; transferencias entre esse universo e contas fora dele, como integralizacao ou outras contas nao operacionais, alteram o saldo das contas exibidas sem virar receita ou despesa
- reconciliacao consolidada da `Prestacao de Contas`:
  - `Saldo final consolidado = saldo inicial consolidado + receitas do periodo - despesas do periodo + entradas de outras contas da instituicao - saidas para outras contas da instituicao`
  - essa reconciliacao vale tanto para saida de conta selecionada para conta nao selecionada quanto para entrada vinda de conta nao selecionada para conta selecionada
- backlog remanescente: revisar, por uso real, se outros relatorios futuros devem adotar o mesmo padrao opcional de exibicao de transferencias

## 0.10. Documentos por favorecido a partir da listagem de lancamentos

- a direcao anterior de `relatorio anual por favorecido` como tela principal foi substituida por acoes documentais centralizadas na `lancamento_list`
- o relatorio anual deixou de ser fluxo exposto em menu/listagens/historico; rota, view e template foram removidos para evitar redundancia operacional
- acoes documentais consolidadas na listagem:
  - `Recibos em lote`: acao baseada na selecao manual atual da listagem, agrupando automaticamente por favorecido e gerando um bloco/pagina por favorecido quando necessario
  - `Termo anual de quitacao`: acao baseada no resultado filtrado atual da listagem, agrupando automaticamente por favorecido e gerando um ou varios termos no mesmo documento continuo
- regra atual dos recibos em lote: categoria deixou de ser elemento relevante de leitura do recibo, nao aparece no documento e nao bloqueia a emissao quando houver categorias diferentes
- regra atual dos recibos em lote: itens com a mesma descricao exata dentro do mesmo favorecido, inclusive oriundos de rateio, podem ser consolidados em uma unica linha documental com soma apenas dos valores dos lancamentos selecionados naquele grupo
- quando a consolidacao reunir datas ou documentos diferentes, o recibo sinaliza isso de forma compacta no proprio item (`Datas diversas`, `Doc. diversos`)
- os recibos em lote reaproveitam a mesma peca documental do recibo oficial ja existente e usam fallback institucional comum, sem depender de mensagem especifica por categoria
- regra do termo anual nesta primeira versao: exige filtro de periodo com data inicial e final dentro do mesmo ano e, internamente, considera apenas receitas quitadas com favorecido e sem rateio, ignorando automaticamente despesas, transferencias, receitas em aberto e demais itens incompativeis
- o termo anual em uso atual prioriza leitura documental para o usuario, com subtitulo mais claro, identificacao simples do favorecido, texto introdutorio institucional, tabela com `Data`, `Descricao`, `Documento` e `Valor` e fechamento com assinatura institucional
- na `Prestacao de Contas`, a leitura operacional das movimentacoes entre universos passou a usar linguagem mais humana: `Entradas de outras contas da instituicao` e `Saidas para outras contas da instituicao`
- permanecem futuros: PDF, anexos, assinatura final juridica, texto formal completo do termo anual, contratos, parcelas, recorrencia e refinamentos documentais apos validacao visual real

## 0.4. Ultimo bloqueio do reset real: assinaturas, configuracao institucional e regras automaticas

- depois de resolver `rateios` e `lancamentos simples` legados, o reset real ainda ficou bloqueado por uma ultima lacuna do pacote operacional
- o bloqueio era objetivo:
  - o comando de reset apagava `AssinaturaInstitucional`
  - o comando de reset apagava `ConfiguracaoInstitucional`
  - o comando de reset apagava `RegraLancamentoFinanceiro`
  - o pacote de reconstrucao ainda nao tinha trilha propria para esses itens
- a estrategia minima e segura adotada foi mista:
  - `AssinaturaInstitucional` passa a ser preservada fora do reset
  - `ConfiguracaoInstitucional` passa a ser preservada fora do reset
  - `RegraLancamentoFinanceiro` continua entrando no reset, mas passa a contar com backup/restauracao tecnica separados em `JSON`
- motivo da decisao:
  - `assinaturas` e `configuracao institucional` sao suporte documental e nao precisam ser zeradas para reiniciar a base transacional
  - `regras automaticas` dependem de cadastros que o reset precisa apagar; preserva-las fora do reset gera conflito estrutural e invalida a limpeza do dominio
- implicacao pratica:
  - o pacote operacional agora precisa incluir tambem o backup tecnico das `regras`
  - com isso, o reset real volta a ficar tecnicamente liberado
- a frente futura continua separada e visivel:
  - evolucao do layout comum de exportacao/importacao de lancamentos com suporte a `rateio` por grupo em planilha
  - essa evolucao futura nao substitui a trilha tecnica hoje adotada para restauracao de `rateios` e `regras`

## 0.1. Bloqueio real do reset e estrategia tecnica para rateios

- o reset destrutivo real do `financeiro` ficou bloqueado quando a auditoria pratica confirmou que a base local possui lancamentos `com_rateio=True` e grupos de rateio que nao podem ser recompostos pela importacao comum ja entregue
- isso nao invalida a importacao comum atual; apenas registra seu limite atual:
  - ela importa lancamentos simples
  - ela nao recompõe `grupo_rateio` como documento agrupado
- para nao abrir uma grande nova frente na importacao funcional, foi adotada a menor trilha segura e reversivel:
  - backup tecnico separado dos rateios em `JSON`
  - restauracao tecnica separada dos rateios, transacional e com confirmacao explicita
- essa solucao passa a ser a ponte operacional para permitir reset futuro sem perda estrutural dos grupos rateados
- importante:
  - isso nao significa que a importacao funcional comum de lancamentos tenha ganho suporte a rateio
  - esse suporte continua fora do fluxo comum do usuario e deve seguir visivel como limite conhecido do roadmap ate decisao futura
- em decisao posterior, essa limitacao passou a ficar registrada como frente futura explicita do backlog:
  - exportacao comum de lancamentos com suporte a rateio por grupo em planilha
  - importacao comum de lancamentos com suporte a reconstrucao de rateio por grupo em planilha
- essa frente continua futura mesmo com a existencia do backup/restauracao tecnica separado; o caminho tecnico resolve reconstrucao operacional da base, mas nao substitui a evolucao funcional do layout comum

## 0.2. Novo bloqueio real encontrado no preflight do reset

- ao preparar a execucao operacional real do reset, o projeto gerou o pacote definitivo de reconstrucao e rodou um preflight com rollback
- esse preflight confirmou que os cadastros auxiliares atuais recompõem normalmente, mas revelou legado invalido tambem entre `lancamentos simples`
- o bloqueio objetivo ficou:
  - `5` linhas de lancamentos simples nao passam pelo contrato atual da importacao comum
  - parte dessas linhas usa `Categoria` pai (`Cantina`, `Estrutura`) em despesa
  - ao menos uma linha usa categoria de `receita` (`Doacao`) em um lancamento do tipo `despesa`
- consequencia pratica:
  - o reset destrutivo real permanece adiado ate existir estrategia fechada para esses legados de lancamento simples
  - essa estrategia pode passar por saneamento de dados, trilha tecnica especifica ou outra decisao controlada em microetapa propria

## 0.3. Bloqueio dos lancamentos simples saneado

- em microetapa posterior, o projeto optou por saneamento dirigido da base atual, preservando o contrato da importacao comum
- resultado:
  - os `5` lancamentos simples bloqueadores foram corrigidos
  - um novo pacote de reconstrucao foi gerado
  - o novo preflight completo com rollback passou com sucesso
- implicacao pratica:
  - o reset destrutivo real deixa de ficar bloqueado por `rateios` e tambem deixa de ficar bloqueado por `lancamentos simples` legados
  - a proxima microetapa operacional volta a ser a execucao real do procedimento de backup/reset/reconstrucao
- a frente futura continua visivel e separada:
  - evoluir exportacao comum de lancamentos para suportar `rateio` por grupo em planilha
  - evoluir importacao comum de lancamentos para reconstruir `rateio` por grupo em planilha

## 0. Reajuste recente de escopo operacional

- a decisao consolidada mais recente desta frente e:
  - importacoes auxiliares ficam centralizadas no financeiro geral
  - exportacoes permanecem nas telas/listagens especificas para respeitar filtros
  - `assinaturas` ficam fora da frente atual de importacoes auxiliares
- no estado atual do repositorio, a central de importacoes do financeiro ja cobre:
  - importacao de lancamentos
  - importacao auxiliar de contas
  - importacao auxiliar de pessoas
  - importacao auxiliar de centros de custo
  - importacao auxiliar de categorias/subcategorias
- backlog remanescente desta frente deve continuar visivel neste roadmap, sem rebaixar o que ja foi entregue no repositorio

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
- exportacao futura de consultas/listagens de lancamentos em CSV/Excel, respeitando filtros aplicados, e PDF apenas quando houver sentido documental

### Extrato e saldo
- saldo inicial por conta
- saldo atual calculado
- extrato por conta
- saldo anterior por periodo

### Importacao de historico
- importacao de planilha historica
- importacao futura em massa de lancamentos com modelo de arquivo, validacao previa, pre-visualizacao e tratamento de duplicidades
- na importacao futura, deve existir acao para baixar planilha modelo no layout proprio do sistema, com colunas e ordem esperadas para preenchimento e importacao
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
- acao `Clonar` diretamente na secao de ultimos lancamentos da pessoa dentro do formulario de lancamento, reaproveitando o fluxo ja existente de clone comum e de clone por grupo rateado
- filtro do campo `Categoria`/`Subcategoria` pelo `tipo` selecionado no lancamento, exibindo apenas subcategorias de despesa em `despesa` e apenas subcategorias de receita em `receita`, com preservacao do comportamento de `transferencia`
- fase 1 de edicao em lote na listagem de lancamentos, com selecao multipla por checkbox, marcar todos os itens visiveis, exclusao em lote com confirmacao e alteracao transacional de status dos selecionados, ainda sem expandir para outros cadastros
- agrupamento visual de rateios na listagem de lancamentos como uma unica linha-resumo expandivel por `grupo_rateio`, com leitura das linhas internas sob demanda, valor total consolidado no resumo e selecao em lote mirando o grupo inteiro, sem alterar o modelo fisico nem outras telas nesta etapa
- padronizacao visual da coluna de acoes na listagem de lancamentos por slots fixos, com `Recibo` contextual apenas quando aplicavel, descricoes truncadas com reticencias e tooltip para leitura rapida, e ordenacao padrao por data principal mais recente primeiro
- fases 1, 2 e 3 da importacao/exportacao de lancamentos com pagina propria focada em upload e link de baixar planilha modelo XLSX com abas `Modelo` e `Instruções`, validacao estrutural do XLSX enviado por extensao/formato/abas/cabecalhos, validacao de conteudo linha a linha da aba `Modelo` contra cadastros ja existentes, importacao orientada prioritariamente a datas em `dd/mm/aaaa` com tolerancia interna tambem a `AAAA-MM-DD`, mensagens com rotulos amigaveis, resumo de linhas lidas/validas/importadas/com erro, download de relatorio XLSX de inconsistencias quando ha erros e importacao real all-or-nothing quando todas as linhas estao validas, primeira exportacao real simples em XLSX acionada pela propria listagem de lancamentos com respeito aos filtros ativos, cabecalhos amigaveis ao usuario, datas em `dd/mm/aaaa` e valores com virgula decimal, e ajuda rapida operacional, ainda sem preview avancado de linhas, criacao automatica de cadastros auxiliares, importacao parcial, tratamento avancado de duplicidades ou exportacao avancada com variacoes
- a mesma central do financeiro agora tambem cobre a importacao auxiliar real de `contas`, `pessoas`, `centros de custo` e `categorias/subcategorias`, reaproveitando planilhas-base XLSX com abas `Modelo` e `Instrucoes`, mantendo gravacao transacional por arquivo e deixando `assinaturas` fora desta frente
- MVP de regras automaticas no cadastro de lancamento comum, com sugestoes por digitacao em `descricao`, `pessoa` apenas como refinador opcional, preenchimento automatico por selecao da sugestao e check explicito para salvar o lancamento atual como nova regra futura
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
- evolucao futura da listagem de lancamentos com mostrar/ocultar colunas, redimensionamento manual de colunas e preferencias persistentes de visualizacao por usuario ou navegador, tratada como refinamento de UX e nao como regra de negocio
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
- contratos a pagar e a receber
- parcelas
- recorrencia
- anexos de comprovantes

### Media prioridade
- balancete padrao
- importacao de planilha historica
- evolucao futura da importacao para oferecer preview/validacao detalhada antes de gravar, tratar duplicidades de forma mais rica, refinar a importacao auxiliar centralizada ja entregue e avaliar eventual importacao parcial apenas em fase posterior
- evolucoes futuras especificas do bloco de recibos ja entregue

## 5. Fila restante reorganizada por prioridade pratica

Observacao:
- esta secao reorganiza a fila restante sem substituir nem apagar as secoes `3` e `4`
- os itens abaixo permanecem futuros; a reorganizacao serve apenas para orientar prioridade pratica de execucao

### Imediato
- proxima frente funcional prioritaria do sistema: `permissoes/autenticacao` com configuracao hierarquica de perfis por `Modulo` > `Tela/Recurso` > `Acao`, em camada transversal do projeto e nao como ajuste isolado do `financeiro`
- na abertura real da frente de `permissoes/autenticacao`, foi criada a primeira versao de `docs/MATRIZ_PERMISSOES.md` como documento proprio de mapeamento de permissoes; as proximas subetapas devem revisar essa matriz com auditoria humana, fechar a regra de exibicao de menus/botoes/endpoints por perfil e so depois iniciar a implementacao tecnica em codigo
- auditoria de UX entre telas existentes e consolidacao de um padrao visual/funcional transversal em `docs/PADRAO_UX_SISTEMA.md`, com padronizacao progressiva das melhorias ja aprovadas no `financeiro` para outros modulos
- refinamentos futuros do shell visual do `financeiro` e do menu superior atual, guiados por uso real e sem reabrir troca estrutural ampla da navegacao
- refinamento futuro do menu superior para ficar mais leve, mais coerente com o tema e menos pesado visualmente, evitando a sensacao de duplicacao de camadas
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
- evolucao futura do cadastro de logo institucional/configuracao visual para aceitar imagem opcional por URL ou upload local, com preview no formulario e regra clara de uso/fallback
- expansao futura da edicao em lote para outros cadastros e listagens operacionais alem de lancamentos, com selecao multipla de registros e aplicacao de acoes em massa, por exemplo excluir varias categorias ou trocar situacao/status em lote, tratada como melhoria de UX/operacao e nao como regra de negocio estrutural
- pagina futura de ajuda/manual de uso do sistema, voltada ao usuario final e focada em orientacao pratica de utilizacao das telas e fluxos, tratada como frente de UX/documentacao ao usuario e nao como regra de negocio nem como regras operacionais internas do modulo
- evolucao futura do cadastro de categorias para deixar explicito na propria UI se o usuario esta cadastrando `Categoria` ou `Subcategoria`, com possibilidade de seletor `Categoria | Subcategoria` e exibicao condicional do campo `Categoria`
- base inicial da edicao coordenada do rateio ja implementada com view e formulario proprios do grupo, ainda pendente de refinamentos para a experiencia final
- acabamento operacional do rateio em edicao individual e leitura do grupo nas telas ja existentes
- estrategia aprovada para futura edicao coordenada do grupo rateado com view e formulario proprios, dados comuns em bloco e salvamento transacional
- modelagem documental mais rica do rateio, se necessario em etapa posterior
- regularizacao eventual de bases antigas de rateio sem `grupo_rateio` valido, caso precisem entrar na leitura consolidada do extrato
- item informativo futuro na tela de lancamentos, com simbolo `i` e historico de cadastro/alteracoes do documento ou lancamento quando houver ganho operacional real
- evolucao futura da central de importacoes do financeiro, com preview mais rico, tratamento avancado de duplicidades e possivel importacao historica em etapa propria, preservando as exportacoes nas listagens filtradas
- evolucao futura da exportacao de lancamentos para oferecer variacoes controladas de saida e refinar o layout conforme uso real
- na importacao/exportacao futura, o fluxo de importacao deve oferecer download de planilha modelo no layout proprio do sistema, preservando a ordem e as colunas esperadas pelo backend de importacao
- refinamentos futuros do MVP de regras automaticas ja aberto no lancamento, preservando `descricao` como gatilho principal por digitacao, `pessoa` apenas como refinador opcional, preenchimento automatico por selecao de uma sugestao e check explicito para salvar nova regra a partir de lancamento comum; melhorias futuras podem incluir curadoria, edicao e governanca dessas regras em tela propria
- acao `Clonar lancamento`, com MVP inicial restrito a lancamento comum sem rateio: abrir `lancamento_form.html` em modo criacao como modelo editavel sem vinculo com o original, copiando campos operacionais seguros (`descricao`, `tipo`, `status`, `valor`, `data_competencia`, `data_pagamento`, `pessoa`, `categoria`, `centro_custo`, `conta`, `conta_destino` quando transferencia, `observacoes`) e sem copiar `pk`, `numero_documento`, auditoria, `grupo_rateio` nem `com_rateio`
- fase futura posterior de clonagem de lancamentos rateados por `grupo_rateio`, tambem sem vinculo com o original, abrindo novo documento rateado ja preenchido e exigindo ajuste manual das linhas/categorias se o `valor total do documento` for alterado no clone
- evolucao futura dos relatorios financeiros para leitura hierarquica por `Categoria` e `Subcategoria`, preservando a distincao entre agrupador analitico e item operacional lancavel
- estudo futuro de agrupamento por categoria com comportamento de expandir/recolher grupos nos relatorios e visoes consolidadas
- estudo futuro de checkboxes para definir exibicao de `centro de custo`, `categoria` e `subcategoria` em relatorios e visoes agrupadas

### Posterior
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

## 14. Checklist permanente de amarracao para novas implementacoes

- a referencia operacional curta dessa revisao passa a ser `docs/CHECKLIST_EVOLUCAO_SISTEMA.md`
- Navegacao, menu e atalhos
- Permissoes por modulo, tela/recurso e acao
- Impacto em listagens: filtros, ordenacao, colunas, truncamento, acoes em lote e exportacao
- Impacto em formularios: rotulos, obrigatoriedade, mensagens, preview e consistencia visual
- Impacto em importacao/exportacao
- Impacto em auditoria/log
- Impacto em ajuda/manual do usuario
- Aderencia ao padrao UX/layout do sistema
- Atualizacao obrigatoria de `docs/CEREBRO_PROJETO.md`, `docs/STATE.md`, `docs/CODEX_RESULTADO.md` e `docs/ROADMAP_FINANCEIRO.md`

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
1. contratos previstos a pagar e a receber
2. parcelas e recorrencia
3. anexos de comprovantes
4. balancete padrao
5. importacao historica
6. evolucoes futuras especificas do bloco de recibos ja entregue

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

## Reestruturação documental futura sem perda de histórico

Fica registrada como frente futura controlada a reorganização gradual da documentação longa do projeto.

Diretrizes:

- não apagar histórico útil;
- não reescrever documentos inteiros sem necessidade;
- criar resumos e índices antes de reduzir arquivos grandes;
- manter STATE.md como estado real;
- manter CODEX_RESULTADO.md como histórico cronológico;
- usar INDICE_PROJETO.md e REGRAS_NEGOCIO.md como camada curta de leitura;
- só mover ou arquivar conteúdo após validação do usuário.

Essa frente deve ser tratada como melhoria de governança/documentação, sem impacto direto no funcionamento do sistema financeiro.
