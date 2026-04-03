# CEREBRO DO PROJETO - CASA ESPIRITA

## 1. Objetivo deste arquivo
Este documento e a fonte principal de contexto funcional e operacional do projeto.
Antes de qualquer implementacao, leitura tecnica ou alteracao estrutural, ele deve ser lido junto com:
- `docs/STATE.md`
- `docs/CODEX_RESULTADO.md`
- `docs/ROADMAP_FINANCEIRO.md`

Se houver divergencia entre pedido atual, conversa e estado real do repositorio, a implementacao deve parar e a divergencia deve ser informada antes de codificar.

O arquivo `docs/ROADMAP_FINANCEIRO.md` consolida o escopo financeiro ja entregue, os refinamentos possiveis e as proximas etapas sugeridas, sem alterar o que ja foi aprovado.

### 1.1. Governanca permanente dos documentos-base
Os documentos-base permanentes do projeto sao:
- `docs/CEREBRO_PROJETO.md`
- `docs/STATE.md`
- `docs/CODEX_RESULTADO.md`
- `docs/ROADMAP_FINANCEIRO.md`

Esses documentos nao devem ser retroagidos como se o historico anterior nao existisse.
Esses documentos nao devem ser reescritos amplamente sem necessidade real.
Esses documentos nao devem ser sobrescritos como se um ciclo anterior do projeto tivesse deixado de existir.
Esses documentos devem ser atualizados por acrescimo, consolidacao ou ajuste cirurgico, preservando a cronologia util.

Papel de cada documento:
- `docs/CEREBRO_PROJETO.md` = diretrizes, definicoes estruturais e regras duradouras
- `docs/STATE.md` = estado atual consolidado
- `docs/CODEX_RESULTADO.md` = registro do que foi executado ou consolidado por etapa
- `docs/ROADMAP_FINANCEIRO.md` = frentes futuras, evolucao e planejamento

Protocolo permanente de continuidade entre chats:
- todo novo chat deste projeto deve comecar lendo os quatro documentos-base
- todo novo chat deve usar o repositorio como fonte final de verdade
- todo novo chat deve preservar o historico documental do projeto
- todo novo chat deve conduzir o trabalho em ordem exata de execucao
- todo novo chat pode usar mensagens orientadoras proprias para preparar a continuidade, desde que preserve estas diretrizes estruturais do projeto

## 2. Objetivo do sistema
O projeto **Casa Espirita** e um sistema em Django para apoiar a gestao da instituicao.

O desenvolvimento deve acontecer em etapas pequenas, seguras e sem regressao, preservando o que ja foi validado.

## 3. Branch de trabalho atual
- `feat/reinicio-financeiro`

## 4. Apps existentes no projeto
Atualmente, os apps existentes sao:
- `configuracoes`
- `biblioteca`
- `financeiro`

## 5. Regras de trabalho obrigatorias
Estas regras devem ser respeitadas em qualquer etapa:

- trabalhar sempre em etapas pequenas
- nao regredir estrutura ja aprovada
- usar o estado real do Git como fonte de verdade
- antes de implementar, resumir o estado atual e apontar divergencias reais, se existirem
- depois de cada etapa aprovada, atualizar a documentacao antes de seguir
- depois de cada etapa aprovada, fazer commit no Git antes de iniciar a proxima
- nao mexer no app `biblioteca` sem necessidade explicita
- nao usar `signals` no modulo financeiro
- nao misturar etapas diferentes na mesma implementacao
- fazer alteracoes minimas, incrementais e rastreaveis
- preservar os documentos-base do projeto sem destruir historico util
- atualizar os documentos-base por acrescimo, consolidacao ou ajuste cirurgico, sem reescrita ampla desnecessaria

### 5.1. Governanca visual duradoura
- o projeto passa a ter frente oficial de governanca visual
- o padrao desejado para as telas administrativas e um layout limpo, funcional e inspirado no tema Tabler, sem copia literal de estrutura nem implementacao abrupta
- a adocao desse padrao deve acontecer de forma progressiva, guiada por componentes reutilizaveis e por reorganizacao controlada do layout-base
- a base inicial dessa padronizacao e o app `financeiro`, por concentrar hoje a camada visual mais madura do projeto
- no app `financeiro`, a navegacao lateral padronizada ja foi autorizada e implementada de forma incremental no shell compartilhado, sem tornar essa mesma adocao automaticamente obrigatoria para os demais apps
- no `financeiro`, a navegacao principal do modulo deve permanecer lateral; o topo do shell nao deve competir com essa navegacao nem repetir contexto do modulo quando a propria sidebar ja cumpre esse papel
- paginas de impressao, PDF e recibo ficam fora da logica normal de navegacao e nao devem ser tratadas como alvo inicial da mesma padronizacao estrutural
- no `financeiro`, relatorios e impressos operacionais devem manter margens explicitas de folha e isolamento do shell visual para nao herdarem sidebar, topbar ou wrappers de overflow no modo print
- quando a natureza `receita` / `despesa` ja estiver clara pelo contexto da tela, pelo agrupamento ou por indicador de tipo, a exibicao visivel da categoria deve preferir nome curto, sem prefixos textuais redundantes
- no shell do `financeiro`, a sigla visual da marca deve preferir iniciais dinamicas derivadas do nome da `ConfiguracaoInstitucional` ativa/padrao, com fallback seguro para `CE` quando nao houver nome configurado
- quando a frente incremental de refinamento visual entrar em retrabalho repetitivo sobre a mesma tela, o projeto pode abrir POC controlada de tema/base visual pronta e leve, desde que exista primeiro um ponto de restauracao seguro em Git
- essa POC deve nascer em escopo minimo, começar por uma unica tela claramente definida e so pode se expandir para outras superficies depois de auditoria visual e funcional explicita
- durante a POC visual, regra de negocio, validacoes, payload JS, navegacao e comportamento funcional devem permanecer preservados
- em microetapas de refinamento visual de telas operacionais do `financeiro`, a avaliacao do `financeiro_shell_header` herdado de `financeiro/base.html` deve acontecer no inicio da etapa, antes de refinamentos no corpo local da pagina
- quando o `financeiro_shell_header` padrao causar duplicidade visual, excesso de contexto no topo ou sensacao de shell antigo sobre corpo novo, a tela deve preferir override com versao enxuta, preservando a navegacao lateral como camada estrutural principal
- a decisao de shell/topo deve ser fechada antes de ajustes em filtros, tabelas, formularios, estados vazios ou demais blocos do conteudo local

### 5.1.1. Diretriz duradoura de comunicacao operacional nas telas
- texto fixo nas telas deve ficar restrito ao minimo operacional necessario para a acao
- explicacoes sobre regra de negocio nao devem ficar espalhadas pela interface quando a propria estrutura da tela, o fluxo ou a validacao ja resolvem a compreensao
- ajuda por icone `i` deve existir apenas em pontos realmente relevantes e excepcionais, sem proliferacao decorativa pela tela
- o componente visual de ajuda por `i` deve seguir padrao coerente de aparencia e semantica sempre que for usado
- a linguagem textual das telas deve buscar consistencia visivel de rotulos, microtextos e acentuacao, evitando variacoes desnecessarias entre paginas equivalentes
- formularios e fluxos operacionais devem buscar leitura continua e sensacao de cadastro unico, evitando empilhamento desnecessario de caixas, cards ou blocos altos quando a mesma tela puder guiar a acao de forma mais fluida
- esse padrao transversal de UX e comunicacao operacional deve orientar tanto refinamentos futuros nas telas existentes quanto a construcao de novas telas, componentes, estados vazios, headings, acoes e mensagens do sistema
- quando um modulo ja possui navegacao estrutural persistente por sidebar ou menu lateral, uma home propria so deve permanecer como entrada principal se oferecer funcao operacional real; quando ela for apenas redundante como camada extra de atalhos, a entrada do modulo deve preferir redirecionar para a tela operacional central do fluxo

### 5.1.2. Diretriz duradoura de hierarquia analitica de categorias no financeiro
- no modulo `financeiro`, a nomenclatura funcional duradoura deve preferir `Categoria` e `Subcategoria`
- nessa hierarquia, `Categoria` deve ser tratada como agrupadora analitica
- nessa mesma hierarquia, `Subcategoria` deve ser tratada como item operacional lancavel
- por regra de negocio duradoura, `Categoria` nao deve entrar como opcao selecionavel no lancamento; a opcao selecionavel deve ser a `Subcategoria`
- essa definicao deve orientar evolucoes futuras de cadastro, filtros, relatorios, textos visiveis e organizacao analitica do modulo, sem implicar por si so implementacao imediata em qualquer microetapa isolada
- como diretriz futura de UX para o proprio cadastro de categorias, a tela deve evoluir para deixar explicito se o usuario esta cadastrando `Categoria` ou `Subcategoria`, evitando depender apenas da leitura implícita do campo hierarquico
- uma abordagem futura aceitavel para isso e usar seletor claro de tipo de cadastro, como toggle, radio ou seletor `Categoria | Subcategoria`
- nessa evolucao futura, quando o cadastro for de `Categoria`, o campo de vinculo hierarquico nao deve aparecer; quando o cadastro for de `Subcategoria`, o campo `Categoria` deve aparecer como vinculo obrigatorio ou explicitamente guiado
- essa definicao e apenas diretriz futura de clareza operacional e nao representa implementacao funcional concluida na UI atual

### 5.2. Diretriz estrutural futura de usuarios, perfis e permissoes
- o projeto passa a registrar oficialmente como frente estrutural futura a camada de usuarios, autenticacao, perfis e permissoes
- essa frente nao deve ser tratada como ajuste isolado do app `financeiro`
- a autenticacao e o controle de acesso devem nascer como base transversal do sistema, preparados para convivio entre modulos atuais e futuros
- deve existir separacao clara entre administracao global do sistema e administracoes ou cadastros especificos de cada modulo
- o desenho futuro deve permitir permissoes por modulo, permissoes por acao e perfis/funcoes de acesso reutilizaveis
- o desenho futuro tambem deve permitir centralizar cadastro de usuarios e controle de permissoes em camada comum do projeto
- com a expansao para novos modulos, o projeto deve poder reorganizar o acesso administrativo global sem acoplar essa governanca a um modulo especifico
- com a expansao para novos modulos, o projeto deve poder separar cadastros globais de cadastros especificos por modulo
- tambem fica registrada como diretriz estrutural futura a possibilidade de unificacao de entidades compartilhadas, incluindo base comum de pessoas quando isso fizer sentido para o sistema como um todo
- essa frente continua futura e nao deve ser misturada com microetapas locais de formulários, listagens, extratos ou refinamentos visuais isolados do `financeiro`

### 5.1.3. Diretriz futura de leveza e refinamento do menu lateral do financeiro
- a navegacao lateral do `financeiro` continua sendo a camada principal de navegacao do modulo
- como evolucao futura de UX, essa lateral deve ficar mais leve, mais coerente com o tema-base adotado e menos carregada visualmente
- o item ativo deve evoluir para leitura mais elegante e menos pesada, reduzindo a sensacao de painel antigo sem perder clareza operacional
- essa diretriz representa backlog de refinamento visual do shell e nao alteracao imediata da estrutura atual

### 5.1.4. Diretriz futura de assistencia por regras no lancamento
- fica registrada como frente funcional futura a possibilidade de sugerir regras existentes durante o preenchimento de novos lancamentos, a partir de campo-chave como nome ou descricao
- nessa evolucao, ao reconhecer uma regra existente e seleciona-la, o sistema pode preencher automaticamente outros campos relacionados para revisao do usuario antes do salvamento
- editar manualmente os campos preenchidos a partir da sugestao nao deve alterar automaticamente a regra de origem
- tambem fica registrada como possibilidade futura a acao de cadastrar nova regra a partir do proprio fluxo de lancamento, em etapa propria
- esta frente nao esta implementada no estado atual do repositorio e nao deve ser confundida com o autocomplete ja existente

### 5.1.5. Diretriz futura de clonagem de lancamento
- fica registrada como frente funcional futura a acao `Clonar lancamento`
- nessa evolucao, a clonagem deve abrir uma nova tela de cadastro ja preenchida com base no lancamento original
- o usuario deve poder revisar e alterar os dados antes de salvar
- o salvamento deve criar um novo lancamento sem alterar o registro original
- esta frente permanece futura e nao esta implementada no estado atual do repositorio

### 5.1.6. Diretriz futura de importacao e exportacao de lancamentos
- fica registrada como backlog funcional futuro do `financeiro` a frente de importacao em massa e exportacao de lancamentos
- na importacao, deve existir modelo de planilha/arquivo e validacao previa de colunas obrigatorias, tipos de dados e aderencia as regras de negocio ja existentes
- a importacao deve prever pre-visualizacao/validacao antes da confirmacao definitiva, comportamento claro para linhas invalidas e tratamento explicito de duplicidades
- na exportacao, consultas e listagens relevantes devem respeitar os filtros aplicados e podem evoluir para CSV/Excel; PDF deve ser reservado apenas quando fizer sentido documental
- essa frente continua futura, nao deve ser misturada com permissoes/acesso nem com regras reutilizaveis ou `Clonar lancamento`, embora possa se relacionar a elas depois
- esta diretriz nao representa implementacao concluida no estado atual do repositorio

### 5.3. Diretriz estrutural futura de identidade visual configuravel
- o projeto passa a registrar oficialmente como frente estrutural futura a configuracao da paleta geral do sistema
- essa frente nao deve ser tratada como aplicacao manual de cores soltas em telas isoladas
- a partir de uma cor principal configurada, o sistema deve poder derivar uma paleta relacionada e coerente para elementos de apoio, contraste, estados e superficies
- essa governanca futura da paleta deve ser transversal ao sistema, preservando consistencia entre shell, modulos, relatorios e demais superficies visuais

### 5.4. Diretriz futura de log de acesso ao sistema
- fica registrada como frente futura a trilha de acesso ao sistema em nivel de autenticacao e entrada de usuarios, separada da auditoria funcional do modulo `financeiro`
- esse log de acesso deve nascer como camada estrutural do projeto e nao como ajuste isolado de uma tela especifica

## 6. Estado funcional ja validado
Ate o momento, esta validado que:

- a rota `/financeiro/` funciona
- o modulo financeiro existe e esta ativo no projeto
- o CRUD inicial do financeiro funciona para pessoas, categorias, contas, centros de custo e lancamentos
- edicao funciona
- exclusao com confirmacao funciona
- filtros basicos funcionam
- autocomplete real no lancamento funciona
- o autocomplete busca no banco
- o autocomplete usa busca por `icontains`
- `conta_destino` aparece apenas quando o tipo e `transferencia`
- a transferencia ficou mais clara na interface
- `ContaFinanceira` ja possui `saldo_inicial`
- `ContaFinanceira` ja possui `data_saldo_inicial`
- `data_saldo_inicial` agora e obrigatoria
- o extrato por conta existe
- a listagem de contas ja mostra `saldo_atual` calculado
- o extrato por conta ja aceita filtro por periodo com saldo anterior
- saldo real da conta considera apenas lancamentos `quitado`
- o financeiro possui menu proprio `Extratos` com filtro por conta e periodo
- o financeiro possui tela inicial de `Resumo` consolidado por periodo
- o financeiro possui tela de `Prestacao de Contas` por periodo
- `Resumo` e `Prestacao de Contas` permitem selecionar quais contas entram no relatorio
- `Resumo` e `Prestacao de Contas` exibem agrupamento por categoria para receitas e despesas
- `Resumo` e `Prestacao de Contas` exibem despesas agrupadas por centro de custo
- `Resumo` e `Prestacao de Contas` permitem controlar a exibicao apenas do bloco de centro de custo
- a `Prestacao de Contas` possui refinamento especifico para impressao em A4 e bloco simples de assinatura
- `Extratos` e `Resumo` possuem impressao mais limpa para uso operacional real
- a listagem de lancamentos possui filtros operacionais por data, conta, pessoa e categoria, alem dos filtros ja existentes
- o menu superior do financeiro separa entrada do modulo, movimentacoes, relatorios e cadastros sem remover itens ja existentes
- o menu superior do financeiro agora tambem possui dropdown `Configuracoes` com acesso a `Assinaturas` e `Configuracao Institucional`
- a home do modulo financeiro agora tambem oferece atalhos visiveis para `Assinaturas` e `Configuracao Institucional`
- o formulario de lancamento agora pode exibir os ultimos 5 lancamentos do favorecido selecionado, sem quebrar o autocomplete atual
- o formulario de lancamento agora possui modo simples de `Lancamento com rateio` para criar multiplas linhas do mesmo documento sem documento pai
- a segunda versao do formulario de rateio agora preserva o lancamento comum, inicia `tipo` em `receita`, melhora a ordem das datas e volta corretamente para a listagem apos criar multiplas linhas
- cada lancamento agora pode gerar recibo proprio em HTML imprimivel, com bloco simples de assinatura
- no recibo, o campo `Referente a` deve usar a descricao do lancamento
- no recibo, a data principal deve priorizar `data_pagamento`, com fallback explicito para `data_competencia` quando necessario
- em relatorios e extratos do financeiro, as datas visiveis ao usuario devem seguir o padrao de apresentacao `dd/mm/aaaa`
- no recibo, nao devem aparecer conta financeira, observacoes, categoria tecnica nem centro de custo nesta etapa
- a categoria financeira agora pode ter uma mensagem opcional propria para o recibo
- quando a categoria tiver mensagem de recibo preenchida, ela deve aparecer em destaque no rodape do recibo
- quando a categoria nao tiver mensagem de recibo, o sistema deve usar uma mensagem padrao simples e segura
- o recibo deve manter apresentacao simples de documento institucional, com foco em impressao e sem aparencia de tela administrativa
- no acabamento final do recibo, `Recebi(emos) de` deve mostrar apenas o nome da pessoa
- no acabamento final do recibo, `A importancia de` deve usar valor por extenso
- no acabamento final do recibo, a data deve aparecer apenas em formato humano e documental, sem expor `data_competencia`
- o sistema agora pode ter assinaturas institucionais cadastradas para uso em recibo
- o recibo deve usar a assinatura institucional ativa marcada como padrao, quando existir
- se nao existir assinatura padrao, o recibo deve continuar funcionando com fallback simples
- o sistema agora pode ter configuracao institucional propria para uso no recibo
- o recibo deve usar nome da instituicao, cidade, logo e mensagem padrao da configuracao institucional ativa marcada como padrao, quando existirem
- se algum dado institucional nao estiver preenchido, o recibo deve usar fallback seguro sem quebrar o layout
- a logo do recibo deve ser tratada como URL acessivel pelo navegador e, se falhar, deve ser ocultada sem quebrar o cabecalho
- a assinatura configuravel do recibo deve usar `assinatura_texto` com apresentacao manuscrita no proprio template
- na impressao do recibo, o bloco documental deve ter altura guiada pelo conteudo, sem se esticar ate o fim da folha
- na impressao do recibo, o bloco deve permanecer centralizado horizontalmente e usar largura util maior na folha A4
- na impressao do recibo, o topo do documento deve manter um pequeno respiro superior sem perder compactacao

## 7. Regras de negocio atuais do financeiro

### 7.1 Tipos de lancamento
Os tipos validos de lancamento sao:
- `receita`
- `despesa`
- `transferencia`

### 7.2 Regras minimas
- `receita`: valor positivo
- `despesa`: valor positivo
- `transferencia`: valor informado continua positivo, mas representa:
  - saida na conta de origem
  - entrada na conta de destino

### 7.3 Regras de transferencia
- `conta_destino` so aparece quando o tipo for `transferencia`
- `transferencia` nao deve exigir campos irrelevantes como pessoa
- `transferencia` nao deve exigir categoria nem centro de custo
- `conta` e `conta_destino` nao podem ser iguais
- `conta_destino` so pode ser usada em `transferencia`

### 7.4 Regras de saldo de conta
- `ContaFinanceira` possui `saldo_inicial`
- `ContaFinanceira` possui `data_saldo_inicial` obrigatoria
- o saldo inicial serve como base do extrato e do saldo acumulado
- `saldo_atual` e calculado em tempo de execucao
- `saldo_atual` nao e salvo no banco
- quando houver filtro por periodo no extrato, deve existir `saldo_anterior`
- apenas lancamentos com `status = quitado` afetam saldo real e extrato
- a nova tela `Extratos` reutiliza a mesma regra do extrato por conta
- o `Resumo` consolidado considera apenas receitas e despesas efetivas
- transferencias internas nao alteram receita, despesa nem saldo consolidado do resumo
- a `Prestacao de Contas` reutiliza a base do resumo e acrescenta blocos formais de apresentacao
- quando nenhuma conta e selecionada explicitamente, `Resumo` e `Prestacao de Contas` consideram todas as contas por padrao
- `receita` e `despesa` exigem `pessoa`
- `receita` e `despesa` exigem `categoria`
- categoria pai nao pode ser usada em lancamento comum nem em rateio; apenas subcategoria/categoria filha pode ser vinculada a `LancamentoFinanceiro`
- `transferencia` nao exige `pessoa`
- `transferencia` nao exige `categoria`
- `transferencia` nao exige `centro_custo`
- em `transferencia`, `conta_destino` continua obrigatoria
- erros de obrigatoriedade do lancamento devem aparecer no formulario, sem estourar erro de banco
- `numero_documento` continua opcional para o usuario, mas deve ser gerado automaticamente quando vier vazio
- quando `Lancamento com rateio` nao estiver marcado, `numero_documento` continua unico entre os lancamentos
- quando `Lancamento com rateio` estiver marcado, o mesmo `numero_documento` pode se repetir apenas como replicacao interna entre linhas do mesmo grupo de rateio
- esse `numero_documento` nao pode coincidir com outro documento independente ja lancado no sistema, mesmo que o outro caso tambem seja rateado
- se o usuario informar manualmente um `numero_documento` ja existente fora do mesmo grupo de rateio, o erro deve aparecer no formulario
- a validacao de duplicidade deve funcionar no cadastro e na edicao, respeitando a excecao controlada de rateio
- na edicao, o proprio registro nao deve ser tratado como duplicado dele mesmo
- na edicao individual de linhas rateadas, uma linha nao pode divergir do `numero_documento` compartilhado pelas demais linhas do mesmo `grupo_rateio`
- se um grupo rateado existente estiver internamente inconsistente em `numero_documento`, o sistema deve bloquear novas gravacoes ate regularizacao manual
- o rateio inicial deve exigir no minimo 2 linhas validas
- no rateio, cada linha deve ter categoria obrigatoria e valor positivo
- no rateio, a soma das linhas deve ser igual ao `valor total do documento`
- no rateio, categorias repetidas no payload devem ser consolidadas por soma antes de salvar as linhas finais
- nesta primeira versao, `valor total do documento` e usado apenas para validacao do formulario e nao e persistido no model
- a edicao individual das linhas rateadas continua disponivel como fluxo proprio, sem substituir a base inicial da edicao coordenada do grupo
- a base inicial da edicao coordenada do grupo rateado agora existe em fluxo proprio, carregado por `grupo_rateio`, sem substituir a edicao individual de uma linha
- a edicao coordenada inicial do grupo deve trabalhar apenas com grupos validos de rateio e manter salvamento transacional
- no create com rateio, o redirecionamento final deve ocorrer sem depender de um `self.object` unico
- quando `data_pagamento` for preenchida e `data_competencia` ainda estiver vazia no formulario, a competencia deve ser sugerida automaticamente sem bloquear edicao manual posterior
- a revisao operacional de `data_pagamento` foi consolidada no formulario do modulo, tornando o campo obrigatorio no fluxo atual e com indicativo visual claro
- o preenchimento de `data_competencia` a partir de `data_pagamento` foi reforcado no template para comportamento mais previsivel, sem sobrescrever indevidamente valores manuais ja existentes
- a obrigatoriedade de `data_pagamento` agora tambem deve ser validada estruturalmente no `clean()` de `LancamentoFinanceiro`, mesmo sem migracao imediata do campo para `null=False` no banco
- a listagem principal de lancamentos deve usar ordem oficial por `-data_competencia`, `-data_pagamento`, `-criado_em` e `-pk`, aplicada na view e sem alterar o `Meta.ordering` do model
- no extrato, a ordem oficial deve ser crescente por `data_competencia`, com desempate por `criado_em` e `pk`
- no extrato, lancamentos rateados devem ser lidos como documento consolidado por `grupo_rateio`, com exibicao do valor total do documento na linha exibida
- a consolidacao do rateio no extrato deve ficar restrita a apresentacao da tela, preservando a modelagem atual do rateio e a base de calculo do saldo
- linhas antigas ou inconsistentes sem `grupo_rateio` valido podem continuar aparecendo de forma individual no extrato ate regularizacao manual
- ficou aberta a frente de auditoria de alteracoes no financeiro, com implementacao incremental preferencial sem `signals`
- a estrategia incremental de auditoria deve comecar por `LancamentoFinanceiro`, com model proprio e registro explicito nas views de create, update e delete
- a trilha de auditoria deve guardar acao, modelo, id do registro, data/hora, usuario quando disponivel e campos alterados em formato estruturado
- a auditoria ja implementada no modulo comecou por `LancamentoFinanceiro` e agora tambem cobre `ContaFinanceira`, mantendo model proprio e registro explicito nas views
- a primeira leitura operacional da auditoria deve permanecer simples, ordenada por `data_hora` decrescente e sem filtros complexos nesta etapa
- a tela minima de leitura da auditoria pode ser integrada ao modulo por rota propria e acesso discreto na navegacao
- a leitura operacional inicial da auditoria pode usar filtros simples por acao, periodo e id do registro, sem obrigar filtro por usuario nesta primeira versao
- `data_pagamento` nao pode ser anterior a `data_competencia`
- `CategoriaFinanceira` pode ter `mensagem_recibo` opcional para personalizar o rodape do recibo
- quando `CategoriaFinanceira.mensagem_recibo` estiver vazia, o recibo deve manter mensagem padrao simples
- o refinamento visual do recibo deve ficar isolado no proprio template, sem depender ainda de configuracao institucional
- o acabamento fino do recibo pode usar apoio minimo da view apenas para nome limpo da pessoa, valor por extenso e data documental
- `AssinaturaInstitucional` pode definir `assinatura_texto`, `nome_exibicao`, `cargo`, `ativo` e `padrao`
- so pode haver uma assinatura marcada como `padrao`
- a assinatura marcada como `padrao` precisa estar ativa
- `ConfiguracaoInstitucional` pode definir `nome_instituicao`, `cidade`, `logo_url`, `mensagem_padrao_recibo`, `ativo` e `padrao`
- so pode haver uma configuracao institucional marcada como `padrao`
- a configuracao institucional marcada como `padrao` precisa estar ativa
- no recibo, `nome_exibicao` e `cargo` da assinatura devem aparecer abaixo da assinatura manuscrita quando preenchidos
- o PDF do recibo deve terminar pouco abaixo da assinatura, sem espaco vertical excessivo
- na listagem de lancamentos, transferencias sem `pessoa` podem aparecer como `Transferencia entre Contas`
- quando um lancamento nao possui categoria, ele aparece no agrupamento como `Sem categoria`
- quando uma despesa nao possui centro de custo, ela aparece no agrupamento como `Sem centro de custo`
- os filtros de exibicao dos agrupamentos nao alteram totais gerais, saldos nem resumo do periodo

## 8. Restricoes tecnicas obrigatorias
As restricoes abaixo devem ser mantidas:

- nao alterar o app `biblioteca` sem necessidade explicita
- nao usar `signals`
- nao alterar dominio alem do necessario para a etapa atual
- nao alterar migrations antigas
- nao fazer refatoracoes paralelas fora do escopo
- nao criar funcionalidades futuras antes da etapa correta
- nao assumir comportamento nao validado sem checagem no codigo

## 9. Fonte de verdade
A ordem de prioridade para tomada de decisao deve ser:

1. estado real do repositorio
2. este arquivo `docs/CEREBRO_PROJETO.md`
3. `docs/STATE.md`
4. `docs/CODEX_RESULTADO.md`
5. instrucao atual da etapa
6. historico do chat

Se houver conflito entre chat e repositorio, prevalece o repositorio.

Regra permanente de transicao entre chats:
- todo novo chat deve comecar lendo `docs/CEREBRO_PROJETO.md`, `docs/STATE.md`, `docs/CODEX_RESULTADO.md` e `docs/ROADMAP_FINANCEIRO.md`
- o repositorio continua sendo a fonte final de verdade
- a documentacao deve ser preservada e atualizada sem destruir historico anterior

## 10. O que nao pode ser quebrado
As seguintes garantias ja aprovadas nao podem ser perdidas:

- funcionamento da rota `/financeiro/`
- CRUD inicial de pessoas
- CRUD inicial de categorias
- CRUD inicial de contas
- CRUD inicial de centros de custo
- CRUD inicial de lancamentos
- edicao funcionando
- exclusao com confirmacao funcionando
- filtros funcionando
- autocomplete real funcionando no lancamento
- comportamento condicional de `conta_destino`
- clareza da interface de transferencia
- extrato por conta funcionando

## 11. Padrao obrigatorio antes de qualquer implementacao
Antes de codificar qualquer etapa, deve-se informar objetivamente:

1. branch atual
2. estado atual resumido em ate 8 linhas
3. divergencias encontradas, se houver
4. arquivos que serao alterados
5. risco real de regressao

Se houver divergencia factual relevante, parar antes de implementar.

## 12. Padrao obrigatorio apos qualquer implementacao
Ao final de cada etapa, deve-se informar objetivamente:

1. arquivos alterados
2. migration criada, se houver
3. resumo do que foi feito
4. riscos encontrados, se houver
5. o que falta validar manualmente no navegador

Depois disso:
- validar no navegador
- atualizar documentacao
- fazer commit
- so entao seguir para a proxima etapa

## 13. Etapa atual concluida
### Estado consolidado atual do financeiro

Escopo ja consolidado no repositorio:
- base operacional propria fora do admin
- cadastros de contas, pessoas, categorias e centros de custo
- CRUD de lancamentos financeiros
- regras condicionais de transferencia
- validacao de nao repeticao de `numero_documento` na camada da aplicacao
- obrigatoriedade condicional de `pessoa` e `categoria` consolidada em formulario/model, preservando `transferencia` sem esses campos
- extrato por conta com saldo acumulado e filtro por periodo
- resumo consolidado por periodo
- prestacao de contas por periodo
- filtros operacionais na listagem de lancamentos
- documentacao de escopo consolidada em `docs/ROADMAP_FINANCEIRO.md`

Diretriz:
- as proximas etapas devem partir desse estado consolidado, sem regressao e sem reabrir etapas ja aprovadas
- a raiz `/financeiro/` deixa de funcionar como home intermediaria e passa a abrir diretamente a listagem principal de lancamentos; a antiga home pode permanecer apenas como rota secundaria explicita enquanto isso fizer sentido de compatibilidade interna

## 14. Etapas futuras ja pensadas, mas nao autorizadas agora
As etapas abaixo podem existir no planejamento, mas nao devem ser implementadas antes da hora:

- autenticacao por usuario, perfis e permissoes em camada estrutural do projeto
- historico por favorecido
- relatorio anual por favorecido
- mapeamento e revisao de todas as mensagens visiveis ao usuario
- contratos a pagar e a receber
- parcelas e recorrencia
- anexos de comprovantes
- balancete padrao
- importacao de planilha historica
- recibos (o bloco base ja foi entregue no repositorio; apenas evolucoes futuras especificas podem existir)

## 15. Como este arquivo deve ser mantido
Este arquivo deve ser atualizado sempre que houver:
- nova regra de negocio validada
- mudanca estrutural aprovada
- mudanca da branch principal de trabalho
- conclusao de etapa relevante
- nova restricao tecnica confirmada

Ele deve continuar curto, objetivo e confiavel.

Padrao de conducao do assistente:
- orientar sempre na ordem exata de execucao
- nao mandar fazer "antes" algo que ja passou
- separar claramente onde estamos, o que ja passou, o proximo passo exato e o passo seguinte
- manter obrigatoria a atualizacao documental entre etapas, conforme a regra permanente ja consolidada do projeto

## 16. Instrucao operacional padrao para novos chats
Ao iniciar um novo chat ou nova execucao, usar algo como:

"Leia primeiro:
- `docs/CEREBRO_PROJETO.md`
- `docs/STATE.md`
- `docs/CODEX_RESULTADO.md`

Use esses arquivos como fonte de verdade.
Antes de implementar, resuma o estado atual, informe divergencias reais e liste os arquivos que pretende alterar.
Se houver conflito entre o pedido e o repositorio, pare e avise antes de codificar."

## 17. Diretriz documental de impressao dos relatorios financeiros

- `Extrato`, `Resumo` e `Prestacao de Contas` devem compartilhar um mesmo padrao documental de impressao/PDF, com cabecalho coerente, identidade institucional leve e hierarquia tipografica comum, sem perder a especificidade operacional de cada relatorio.
- a identidade institucional dos relatorios deve priorizar logo institucional quando existir e, na ausencia dela, cair apenas para o nome institucional, sem usar sigla como pseudo-logo ou selo visual improvisado
- a impressao deve continuar isolada do shell administrativo, sem heranca indevida de sidebar, topbar, drawer ou controles operacionais
- evolucoes futuras como logo institucional, multiplas assinaturas e configuracao por relatorio devem entrar como acabamento incremental sobre essa base, e nao como reabertura estrutural do layout de impressao

## 18. Diretriz documental do recibo

- o recibo deve seguir linguagem de documento final, com topo institucional mais centrado, titulo principal unico e mensagem central com protagonismo maior do que controles ou ornamentos administrativos
- quando a logo institucional ja cumpre funcao de identificacao visual suficiente, o recibo nao deve repetir ao lado dela o nome da instituicao apenas por redundancia
- o recibo deve manter fallback discreto para nome institucional quando nao houver logo utilizavel, preservando sobriedade e leitura documental

## 19. Diretriz estrutural da frente visual/UX

- quando uma tela transacional entrar em ciclo de retrabalho por microajustes incrementais de layout sem resolver a base visual, o projeto deve preferir testar um tema gratis real como fundamento da composicao, em vez de continuar remendando a estrutura atual
- na frente visual atual do `financeiro`, o tema-base escolhido para a POC controlada e o **Tabler**
- essa adocao deve acontecer de forma controlada: primeiro em uma unica tela piloto, com preservacao integral de regra de negocio e comportamento funcional, antes de qualquer expansao
- na etapa atual, a tela piloto autorizada para essa POC e `financeiro/templates/financeiro/lancamento_form.html`
- tentativas manuais anteriores de recomposicao visual do `lancamento_form.html` devem ser tratadas apenas como montagem intermediaria de estudo e nao como execucao valida da POC com tema-base real
- a expansao do tema para outras telas do `financeiro` ou para modulos futuros so pode acontecer depois de auditoria visual e funcional real da tela piloto
- se a base do tema resolver o problema visual de forma convincente, customizacoes pontuais por cima dela passam a ser aceitaveis; antes disso, a prioridade e validar a base pronta em vez de reabrir refinamentos incrementais
