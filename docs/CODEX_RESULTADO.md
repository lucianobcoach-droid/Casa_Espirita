# CODEX_RESULTADO

Data: 2026-04-05

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
