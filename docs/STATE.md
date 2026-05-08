# STATE

Data de atualizacao: 2026-05-06

## Frente futura registrada: tabelas de controle personalizadas

- registrada como frente futura separada, classificada em backlog e sem implementacao nesta etapa
- objetivo futuro: permitir tabelas configuraveis para controles internos da Casa, reduzindo dependencia de planilhas externas
- recursos desejados para especificacao futura:
  - criacao de tabelas personalizadas
  - colunas configuraveis com tipos de coluna
  - formulas controladas entre colunas
  - linhas de controle com consolidacoes basicas
  - possibilidade futura de vinculo com financeiro, pessoas, categorias ou outras entidades
- regra de seguranca desta etapa:
  - nao implementar agora
  - nao misturar com a frente atual de frequencia por competencia
  - exigir auditoria e SPEC propria antes de qualquer modelagem, model ou migration
- riscos ja registrados para analise futura: alta complexidade, risco de virar "Excel dentro do sistema", necessidade de limites de formula por seguranca, permissoes, trilha de auditoria, backup/exportacao e separacao entre dado operacional e financeiro oficial

## Validacao da alocacao de competencias no lancamento simples

- validacao local da usuaria registrada como aprovada para o recorte de lancamento simples
- confirmado em uso real:
  - bloco `Competencias atendidas` aparece quando favorecido e recorrente e a subcategoria controla recorrencia por competencia
  - cadastro de competencias por `mes/ano + valor` funciona
  - salvamento ocorre quando a soma fecha com o valor controlado do lancamento
  - divergencia de soma bloqueia o salvamento com erro de validacao
- confirmado no comportamento da etapa:
  - edicao recarrega competencias ja registradas
  - clone comum nao copia competencias automaticamente
  - ainda nao existe matriz mensal (com valores ou sem valores)
  - rateio permanece pendente para captura por item controlado em microetapa futura
- nao houve alteracao de calculo financeiro, saldos, Balancete, Extrato, Fechamento/Prestacao ou demais relatorios

## Alocacao de competencias mensais no lancamento

- implementada a estrutura `AlocacaoCompetenciaFinanceira` como filha de `LancamentoFinanceiro`, com `categoria`, `mes_competencia`, `ano_competencia` e `valor_alocado`
- a regra funcional desta microetapa ficou assim:
  - em lancamento simples, quando `PessoaFinanceira.contribuinte_recorrente=True` e a subcategoria controla recorrencia por competencia, o formulario passa a exigir o bloco `Competencias atendidas`
  - a soma das competencias informadas precisa fechar exatamente com o valor controlado do lancamento
  - mes invalido, ano invalido e valor nao positivo bloqueiam o salvamento
- em edicao, competencias existentes voltam carregadas; em exclusao, as alocacoes saem junto por `CASCADE`
- em clone comum, as competencias nao sao copiadas automaticamente para evitar duplicidade de quitacao/competencia
- para rateio, a estrutura ficou preparada, mas a primeira gravacao do grupo continua sem captura de competencias nesta etapa; o fluxo atual nao foi quebrado nem passou a usar indevidamente o valor total do documento em recebimentos mistos
- ainda nao ha matriz mensal, matriz sem valores, termo por favorecido nem modulo separado de baixa
- nao houve alteracao de calculo financeiro, saldos, Balancete, Extrato, Fechamento/Prestacao ou relatorios existentes
- proxima microetapa recomendada: implementar a captura segura de competencias por item controlado no fluxo de rateio e abrir a base da futura matriz mensal com valores

## SPEC consolidada - contribuicao mensal por competencia (sem implementacao)

- consolidada SPEC funcional/tecnica para a futura frente de controle de frequencia por competencia
- decisao registrada: nao usar checkbox puro como fonte principal; adotar alocacao de competencia com `mes/ano + valor`
- decisao registrada: manter lancamento financeiro como origem do dinheiro no MVP, sem modulo separado de baixa nesta primeira onda
- vinculo tecnico recomendado: estrutura filha/intermediaria de alocacao de competencia que funcione para lancamento simples e lancamento com rateio
- regra consolidada para rateio: quando houver itens recorrentes e nao recorrentes no mesmo documento, a frequencia considera apenas o valor da subcategoria que controla frequencia, nao o valor total do lancamento
- matriz com valores definida como base; matriz sem valores deve ser derivada dela
- termo por favorecido permanece como segunda onda apos validacao da matriz
- etapa exclusivamente documental/técnica preparatoria, sem alteracao de codigo, migrations, calculo financeiro ou relatorios atuais

## Correcao de identificacao de contas no cabecalho do Extrato impresso

- corrigida a apresentacao de `Contas selecionadas` no cabecalho impresso/PDF do Extrato
- quando houver uma unica conta selecionada, o cabecalho passa a exibir o nome da conta (ex.: `Sicredi Investimento`), em vez de apenas `1 conta selecionada`
- quando houver 2 ou 3 contas selecionadas, o cabecalho exibe os nomes das contas
- quando houver mais de 3 contas selecionadas, o cabecalho usa resumo enxuto no formato `X contas selecionadas`
- quando todas as contas estiverem selecionadas, permanece a identificacao `Todas as contas financeiras`
- alteracao restrita a apresentacao/documentacao do Extrato; sem mudanca de calculo, saldo, lancamentos, Balancete, Fechamento/Prestacao ou demais relatorios

## Simplificacao dos filtros do Balancete patrimonial

- implementada a arquitetura funcional por `Formato do Balancete`, com tres formatos: `Operacional`, `Operacional + patrimonio vinculado` e `Financeiro completo`
- o filtro antigo `Exibir contas vinculadas/indisponiveis` saiu da interface; a experiencia passa a ser orientada pelo formato principal e por filtros complementares dependentes
- no formato `Operacional`, o documento fecha apenas pelo saldo disponivel operacional
- no formato `Operacional + patrimonio vinculado`, o bloco operacional permanece separado e o patrimonio vinculado aparece em bloco complementar proprio, com detalhamento opcional
- no formato `Financeiro completo`, o Balancete representa a leitura financeira total da instituicao, com saldo disponivel, saldo vinculado e saldo total financeiro
- a mudanca foi apenas de apresentacao/classificacao do Balancete; nao houve alteracao da base de calculo nem dos demais relatorios
- arquitetura funcional aprovada para proxima evolucao do Balancete: filtro principal `Formato do Balancete` com tres opcoes (`Operacional`, `Operacional + patrimonio vinculado`, `Financeiro completo`)
- o filtro antigo `Exibir contas vinculadas/indisponiveis` passa a ser substituido por filtros dependentes do formato escolhido
- formato `Operacional`: mostra apenas universo disponivel, sem bloco vinculado e sem mensagens patrimoniais
- formato `Operacional + patrimonio vinculado`: mantém resumo operacional separado e adiciona bloco patrimonial complementar em seguida
- formato `Financeiro completo`: mostra leitura financeira total da instituicao, com disponivel e vinculado no mesmo universo financeiro
- regra permanente de UX funcional: nao exibir filtros que nao fazem sentido para o formato selecionado
- esta etapa foi apenas documental; nao houve alteracao de codigo nem mudanca de comportamento atual do Balancete
- quando `Exibir vinculadas/indisponiveis = Nao`, o Balancete passou a representar apenas o saldo disponivel operacional em todo o documento
- nesse modo, saldo indisponivel/vinculado, contas indisponiveis e mensagens explicativas dessas contas deixam de aparecer em qualquer bloco do relatorio
- transferencias entre saldo disponivel e saldo vinculado/indisponivel passaram a aparecer no resumo operacional como movimentacao especifica de fronteira do saldo disponivel, sem virar receita ou despesa operacional
- quando `Exibir vinculadas/indisponiveis = Sim`, o Balancete continua representando o saldo financeiro total com leitura patrimonial completa
- o filtro `Modelo do relatorio` foi removido do Balancete Institucional por redundancia
- o filtro separado `Detalhar saldo inicial por conta` tambem foi removido por redundancia
- a leitura pratica do documento passou a ser controlada diretamente por duas escolhas: composicao do saldo e exibir/ocultar contas vinculadas/indisponiveis
- a composicao do saldo permanece com tres modos: detalhada por conta, consolidada por tipo de conta e total consolidado; o padrao atual passou a ser `Consolidada por tipo de conta`
- o mesmo filtro `Composicao do saldo` agora comanda tanto o saldo inicial quanto o saldo final: se for por conta, as duas pontas ficam por conta; se for por tipo, as duas pontas ficam por tipo; se for consolidado, as duas pontas ficam consolidadas
- a opcao de exibir ou ocultar contas vinculadas/indisponiveis continua apenas documental/visual e nao altera calculo, saldo final financeiro, lancamentos ou transferencias
- quando as contas vinculadas/indisponiveis ficam ocultas, o Balancete deixa claro isso pelos rotulos da composicao apresentada, sem aviso textual adicional chamando atencao para as contas ocultas
- os filtros de composicao e vinculadas/indisponiveis deixaram de aparecer como metadados no cabecalho impresso
- o layout impresso foi mantido compacto, com fonte menor, menos espacamento vertical e sequencia documental mais direta, buscando caber em uma pagina quando o volume permitir

## Correcao da sequencia documental do Balancete

- o Balancete Institucional deixou de comecar por `Resumo financeiro do periodo`
- a sequencia documental foi corrigida para: `Saldo inicial financeiro`, `Entradas do periodo`, `Saidas do periodo`, `Resumo operacional do periodo`, `Composicao do saldo final` e `Assinaturas`
- a composicao do saldo inicial deixou de ficar misturada dentro do resumo e passou a abrir o documento como bloco proprio
- o resumo operacional passou a vir depois de entradas e saidas, mantendo a base financeira ja calculada e sem alterar reconciliacao
- a mensagem `Contas vinculadas/indisponiveis nao exibidas nesta composicao...` foi removida quando as contas indisponiveis/vinculadas ficam ocultas

## Leitura patrimonial no Balancete Institucional

- o Balancete Institucional passou a separar a composicao do saldo final entre saldo disponivel operacional e saldo indisponivel/vinculado, mantendo o modo detalhado por conta
- a classificacao usa os campos patrimoniais ja existentes em `ContaFinanceira`, com fallback seguro para `disponivel` quando a conta nao informar disponibilidade
- contas indisponiveis/vinculadas podem exibir mensagem explicativa discreta no Balancete quando `mensagem_indisponibilidade` estiver preenchida
- integralizacao de capital continua podendo ser cadastrada normalmente; sua leitura no Balancete depende de `disponibilidade`, sem regra paralela de calculo
- o saldo total financeiro do Balancete permanece igual a composicao final ja calculada pela base compartilhada do Fechamento/Prestacao
- os modos `Consolidada por tipo de conta` e `Total consolidado` ja estao disponiveis; permanecem como futuro apenas refinamentos adicionais de leitura, ordenacao e compactacao por uso real

## Base cadastral patrimonial das contas financeiras

- ajuste de nomenclatura aplicado: o tipo padrao com codigo `aplicacao_financeira` passa a ser exibido como `Conta investimento`; `Integralizacao de capital` permanece como nomenclatura oficial
- conta de integralizacao pode ser cadastrada normalmente como conta financeira; no futuro Balancete patrimonial, sua separacao como disponivel ou indisponivel/vinculada dependera do campo `disponibilidade`
- implementada a base cadastral minima do MVP patrimonial em contas financeiras: cadastro proprio simples de tipo de conta, disponibilidade/vinculacao total por conta e mensagem explicativa opcional
- cadastro, edicao e listagem de contas passaram a exibir os campos patrimoniais, sem alterar Balancete Institucional, Fechamento/Prestacao, Extrato, lancamentos, saldos, transferencias ou calculos financeiros
- importacao/exportacao auxiliar de contas foi ampliada com `tipo_conta`, `disponibilidade` e `mensagem_indisponibilidade`, preservando leitura de planilha legada de contas com defaults seguros
- migration criada com carga inicial idempotente dos tipos: conta corrente, conta poupanca, dinheiro/caixa, conta investimento, integralizacao de capital, conta vinculada/indisponivel e outros; contas existentes recebem `outros` e `disponivel`
- proxima microetapa funcional recomendada: avaliar modos avancados de exibicao patrimonial no Balancete, como consolidado por tipo, apenas se o uso real justificar e sem criar calculo divergente

## Auditoria tecnica preparatoria do MVP patrimonial

- auditoria tecnica concluida sem implementacao funcional: `ContaFinanceira` esta em `financeiro/models.py` com campos `nome`, `descricao`, `saldo_inicial`, `data_saldo_inicial`, `ativa`, `criado_em` e `atualizado_em`
- cadastro/edicao de conta usa `ContaFinanceiraForm`, `conta_form.html`, `conta_list.html` e views `ContaFinanceiraList/Create/Update/Delete/Exportacao`; importacao auxiliar de contas usa colunas `nome`, `descricao`, `saldo_inicial`, `data_saldo_inicial` e `ativa`
- Balancete Institucional e montado em `BalanceteInstitucionalFinanceiroView`, reaproveitando `montar_contexto_fechamento_periodo`; a composicao final atual vem de `composicao_final` e e exposta ao template como `balancete_composicao_final`
- primeira implementacao funcional futura recomendada: criar model/cadastro simples de tipo de conta e adicionar campos simples em `ContaFinanceira`, com ajustes pontuais em form, templates de conta, importacao/exportacao auxiliar e testes, ainda sem mexer em calculo, Extrato, Fechamento/Prestacao ou regras de transferencia
- riscos mapeados: migration de dados para contas existentes, compatibilidade da importacao/exportacao de contas, auditoria/snapshot de conta, ordenacao/exibicao patrimonial no Balancete e preservacao da base comum de calculo

## Decisoes funcionais do MVP patrimonial

- registradas decisoes aprovadas para o MVP patrimonial futuro: tipo de conta financeira sera cadastro proprio simples; disponibilidade/vinculacao sera total por conta no MVP; mensagem explicativa ficara no cadastro da conta; modo padrao do Balancete patrimonial sera detalhado por conta, preservando leitura atual com separacao visual entre disponivel e indisponivel/vinculado quando aplicavel
- tipos iniciais sugeridos para carga inicial futura: conta corrente, conta poupanca, dinheiro/caixa, conta investimento, integralizacao de capital, conta vinculada/indisponivel e outros
- primeira implementacao futura deve ficar restrita a cadastro/modelagem de tipo de conta, campos simples no cadastro de conta para tipo/disponibilidade/mensagem e leitura patrimonial no Balancete Institucional, preservando a base de calculo atual do Fechamento/Prestacao
- ficam fora do MVP: disponibilidade parcial, calculo patrimonial novo, alteracao de lancamentos, Extrato, Fechamento/Prestacao, importacao/exportacao, permissoes, regras de transferencia, saldos, controle por parcelas de saldo e automatizacao contabil avancada
- esta microetapa foi apenas documental; nao houve alteracao funcional, codigo, models, migrations, views, forms, templates, tests, CSS, banco de dados ou calculos financeiros

## Governanca de regras reutilizaveis e Balancete patrimonial

- registrada regra permanente: toda regra de negocio aprovada deve ir para `docs/REGRAS_NEGOCIO.md`, com comportamento esperado, excecoes, impacto em cadastros, impacto em relatorios, racional da decisao e potencial de reaproveitamento
- detalhada a frente futura de tipo/disponibilidade de conta e Balancete patrimonial, incluindo tipos iniciais de conta, diferenca entre ativa/inativa e disponivel/indisponivel, integralizacao de capital como valor patrimonial/vinculado e campo opcional de mensagem explicativa
- especificados os modos futuros de composicao do Balancete: detalhado por conta, consolidado por tipo, total consolidado e separado entre disponivel e indisponivel/vinculado
- registrada regra de seguranca: a evolucao patrimonial deve reaproveitar a base do Fechamento/Prestacao e alterar apenas classificacao/apresentacao do saldo, sem calculo proprio divergente
- modelagem documental consolidada no roadmap: impactos futuros em cadastro de contas, Balancete, relatorios e regras de negocio foram separados das decisoes ainda pendentes antes da implementacao tecnica
- nao houve alteracao funcional, codigo, models, migrations, views, forms, templates, tests ou CSS

## Checkpoint do financeiro apos homologacao local

- Concluido/homologado recentemente: rotina Git/GitHub, rotina de baixa documental, documentos por favorecido, favorecido tecnico `TRANSFERENCIA ENTRE CONTAS` no Extrato, bloco `DIFERENCA A DETALHAR` no rateio, contas inativas em consultas historicas e filtro multi-contas na listagem de lancamentos.
- Homologacao local da usuaria registrada como OK para quatro ajustes recentes: listagem de lancamentos multi-contas, favorecido tecnico no Extrato, diferenca a detalhar no rateio e contas inativas em consultas historicas.
- HOMOLOGACAO PROGRESSIVA REALIZADA: os fluxos principais do financeiro foram testados localmente durante o desenvolvimento das microetapas, evitando necessidade de repetir agora uma homologacao ponta a ponta completa de tudo que ja foi conferido.
- Implementado com pendencias futuras ou homologacao ampla: Balancete Institucional como MVP proprio com evolucoes futuras de tipo/disponibilidade de conta e modos de composicao; importacoes/cadastros auxiliares aguardando homologacao com massa real; autenticacao/perfis/permissoes com base implementada e evolucoes futuras; relatorios impressos sujeitos a validacao visual por uso real.
- Futuro real registrado: opcao visual do Extrato multi-contas para detalhar transferencias internas em duas linhas, tipo/disponibilidade de conta, frequencia/recorrencia por competencia, contratos/parcelas/recorrencias, anexos, tabelas personalizadas de controle e expansao visual/transversal progressiva.
- Proxima fase natural: uso real acompanhado do financeiro, mantendo validacao com massa definitiva para importacoes, planilhas historicas completas, relatorios impressos em volume real e rotina diaria da Casa.
- Nao houve alteracao funcional neste checkpoint documental.

## Homologacao local de melhorias recentes do financeiro

- usuaria testou localmente e validou como OK: listagem de lancamentos com filtro multi-contas, favorecido tecnico `TRANSFERENCIA ENTRE CONTAS` no Extrato, bloco `DIFERENCA A DETALHAR` no rateio e filtro de contas inativas em consultas historicas
- registrada melhoria futura para o Extrato multi-contas: opcao visual/analitica para detalhar transferencias internas entre contas selecionadas em duas linhas operacionais, sem alterar saldo consolidado, calculo financeiro ou regra atual de neutralizacao
- nao houve alteracao funcional, codigo, views, templates, forms, tests, CSS, calculos financeiros ou comportamento do Extrato nesta microetapa documental

## Filtro multi-contas na listagem de lancamentos

- a listagem de lancamentos passou a permitir filtro por uma, varias ou todas as contas
- a regra da listagem considera lancamentos cuja conta origem ou conta destino esteja no conjunto selecionado
- transferencias internas entre contas selecionadas tambem aparecem na listagem, por ser uma leitura operacional/documental de lancamentos reais
- foi preservada compatibilidade com o parametro antigo de conta unica e a exportacao da listagem segue reaproveitando os filtros ativos
- nao houve alteracao de calculo financeiro, saldos, Extrato, Resumo, Prestacao/Fechamento, Balancete, Evolucao, importacao ou models

## Filtros historicos de contas inativas

- filtros historicos de contas passaram a listar contas ativas sempre e contas inativas apenas quando houver movimento no periodo/escopo considerado
- a regra foi aplicada a base compartilhada de Resumo, Prestacao/Fechamento e Balancete, alem de Evolucao por categorias, Extratos, Historico por favorecido e listagem de lancamentos
- o criterio de movimento considera conta origem e conta destino em transferencia, usando data de pagamento com fallback para competencia
- nao houve alteracao de calculo financeiro, saldo, models, migrations, importacao/exportacao ou regras de novos lancamentos

## Refinamento visual da diferenca do rateio

- ajuste complementar: o valor de `DIFERENCA A DETALHAR` foi movido para a propria grade do rateio, ficando alinhado visualmente com a coluna `Valor`
- o apoio visual do rateio foi simplificado para exibir apenas o bloco `DIFERENCA A DETALHAR`
- os cards de valor total do documento e total rateado foram removidos da interface, mantendo o calculo dinamico da diferenca em tela
- diferenca diferente de zero aparece em vermelho; alerta textual aparece somente quando o rateio ultrapassa o valor total do documento
- a mudanca permanece restrita ao visual/UX do formulario, sem alterar validacao, persistencia, calculos financeiros, saldos, importacao/exportacao ou relatorios

## Diferenca restante no rateio

- o formulario de novo lancamento com rateio e a edicao coordenada do grupo passaram a exibir valor total do documento, total rateado e diferenca restante
- a informacao e atualizada em tela conforme o usuario altera o valor total ou as linhas do rateio, indicando quando o rateio esta fechado, faltando ratear ou ultrapassando o total
- a mudanca e apenas apoio visual/operacional e nao altera validacao, persistencia, calculos financeiros, saldos, importacao/exportacao, relatorios, recibos, termos, Balancete, Extrato ou Prestacao

## Favorecido tecnico em transferencia no Extrato

- transferencias exibidas no Extrato sem favorecido operacional agora mostram `TRANSFERÊNCIA ENTRE CONTAS` na coluna Favorecido
- o ajuste ficou restrito a apresentacao do Extrato e preserva favorecido real quando houver pessoa vinculada
- nao houve alteracao de calculo, saldo, regra de transferencia, importacao/exportacao, recibos, termo anual, Balancete ou outros relatorios

## Auditoria de importacao historica e cadastros auxiliares

- auditoria documental/tecnica concluida sem alteracao funcional de codigo
- confirmado no codigo: central de importacoes do financeiro, importacao/exportacao comum de lancamentos, modelos XLSX, importacoes auxiliares de contas/favorecidos/centros/categorias, validacao estrutural, validacao linha a linha, relatorio de inconsistencias, trava de dominio preenchido e gravacao transacional all-or-nothing
- confirmado no codigo: lancamentos simples, transferencias simples e rateio em ate 5 blocos na mesma linha no contrato comum; rateios acima desse limite continuam por caminho tecnico de backup/restauracao
- reclassificado no `MAPA_RECLASSIFICACAO.md` o item de importacao historica e cadastros auxiliares como IMPLEMENTADO COM PENDENCIAS FUTURAS / AGUARDANDO HOMOLOGACAO
- permanecem futuras as frentes de preview antes de gravar, importacao parcial, preflight mais visivel, tratamento avancado de duplicidades e homologacao com planilhas historicas reais da usuaria
- nao houve alteracao em views, urls, models, forms, templates, migrations, testes, CSS ou calculos financeiros

## Baixa documental de pendencias implementadas do financeiro

- baixadas como implementadas pendencias antigas de favorecido duplicado por nome, edicao de conta com saldo inicial/data preenchidos e logo institucional no Extrato impresso
- registrada baixa da regra geral de identificadores-chave como diretriz implementada, mantendo aplicacao progressiva futura para demais cadastros
- registrada baixa da padronizacao do filtro de contas nas telas analiticas Resumo, Prestacao/Fechamento e Evolucao por categorias, mantendo a listagem de lancamentos como pendencia propria futura
- registrada baixa do refinamento de impressao da Prestacao/Fechamento como implementado e aguardando validacao visual por uso real
- nao houve alteracao funcional, codigo, views, urls, models, forms, templates, migrations, testes, CSS ou calculos financeiros

## Auditoria de autenticacao, perfis e permissoes

- auditoria documental/tecnica concluida sem alteracao funcional de codigo
- confirmado no codigo: login/logout, recuperacao/reset de senha, models de permissao/perfil, vinculo usuario-perfil, seed inicial de permissoes, mixins backend e template tags de permissao
- confirmado no codigo: permissoes aplicadas aos apps `financeiro`, `biblioteca` e `configuracoes`, com menus/acoes condicionais nos templates principais
- reclassificado no `MAPA_RECLASSIFICACAO.md` o item de autenticacao/perfis/permissoes como IMPLEMENTADO COM PENDENCIAS FUTURAS, retirando o estado generico de duvida
- permanecem futuras as evolucoes de extras individuais, bloqueios individuais, preferencias por perfil/usuario, log de acesso e refinamento amplo da matriz
- nao houve alteracao em views, urls, models, forms, templates, migrations, testes, banco de dados ou regras financeiras

## Baixa documental do Balancete e rotina de pendencias

- consolidada rotina permanente de baixa documental de pendencias em `docs/ROTINA_BAIXA_PENDENCIAS.md`
- registrado que tarefas auditadas, implementadas, substituidas, descartadas ou parcialmente implementadas nao devem permanecer como duvida generica sem reclassificacao
- registrada baixa detalhada do Balancete Institucional: MVP nao deve ser reaberto como criacao do zero; permanecem futuras as frentes de modelagem de tipo/disponibilidade de conta, composicao e acabamento documental validavel em uso real
- nao houve alteracao funcional, codigo, templates, views, urls, models, forms, testes, CSS ou calculos financeiros

## Auditoria documental do Balancete Institucional

- auditoria concluida sem implementacao funcional: Balancete esta documentado como relatorio proprio e nao substitui a Prestacao/Fechamento
- confirmado documentalmente que o MVP reutiliza a base comum de calculo da Prestacao/Fechamento e preserva fundo branco, aparencia documental, composicao final e selecao manual de assinaturas
- reclassificados no mapa e no roadmap os pontos do Balancete como parcialmente implementados, com pendencias futuras de modelagem para tipo de conta, disponibilidade/vinculacao e modos de composicao
- regras permanentes sobre integralizacao de capital como valor patrimonial/vinculado, nao despesa operacional, ja estavam registradas em `CEREBRO_PROJETO.md` e `REGRAS_NEGOCIO.md`
- nao houve alteracao de codigo, views, templates, urls, models, forms, testes ou calculos financeiros

## Rotina oficial Git/GitHub

- consolidada documentalmente a rotina de sincronizacao local x GitHub do projeto
- GitHub remoto na branch `feat/reinicio-financeiro` passa a ficar registrado como memoria oficial compartilhada
- commit local sem push fica registrado como pendencia de sincronizacao antes de nova microetapa funcional
- criado `docs/ROTINA_GIT_GITHUB.md` com comandos PowerShell seguros e criterios para push ou parada
- nao houve alteracao funcional, codigo, templates, models, migrations, calculos ou testes

## Auditoria de documentos por favorecido no financeiro

- auditoria documental/tecnica concluida sem alteracao funcional de codigo
- confirmado no codigo: historico por favorecido com rota, view, template e acao na listagem de favorecidos
- confirmado no codigo: recibo individual, recibo em lote de mesmo favorecido e fluxo atual de recibos em lote agrupados por favorecido a partir da `lancamento_list`
- confirmado no codigo: termo anual de quitacao por resultado filtrado da `lancamento_list`, com rota plural antiga mantida apenas como compatibilidade tecnica
- a antiga direcao de relatorio anual por favorecido permanece classificada como historico/substituida pelo fluxo documental atual da listagem de lancamentos
- nao houve alteracao em views, urls, templates, models, forms, calculos financeiros ou testes

## Logo institucional no Extrato impresso

- o cabecalho impresso do Extrato passou a renderizar `financeiro_shell_brand_logo_url` como `<img>` quando houver logo institucional configurada
- quando nao houver logo, o Extrato mantem fallback textual com `financeiro_shell_brand_name`, sem reservar espaco vazio
- ajuste complementar: o print do Extrato foi compactado, o cabecalho explicativo da tela foi ocultado na impressao e o `thead` ficou restrito aos titulos das colunas para repetir em quebras de pagina
- ajuste complementar: o print foi reequilibrado com margem superior explicita, cabecalho documental mais proporcional, bloco proprio para contas selecionadas e maior destaque nos titulos das colunas
- ajuste complementar: o cabecalho impresso foi reconstruido para exibir logo e nome institucional juntos, titulo/metadados em bloco proprio e resumo das contas selecionadas sem lista longa no topo
- ajuste complementar: a margem superior do print foi ampliada, o cabecalho institucional foi alinhado verticalmente e o `thead` recebeu respiro print-only para paginas seguintes
- ajuste complementar: foi removida a frase explicativa do bloco de movimentacoes e o print foi suavizado para ficar mais proximo da leveza visual da tela
- ajuste complementar: o Extrato passou a ter contrato local de impressao com margens explicitas, padding superior real no documento e respiro de continuacao no `thead` para paginas seguintes
- ajuste complementar: a tabela do Extrato passou a ter layout fixo, truncamento para textos longos, separadores verticais leves e valores monetarios sem simbolo `R$` dentro da tabela
- ajuste complementar: o contrato local de pagina foi normalizado para A4 com margens 14mm/12mm/14mm, spacer moderado de 6,5mm e respiro final inferior discreto
- ajuste complementar: o respiro inferior da tabela longa deixou de usar `tbody::after` e passou para `tfoot` real com `table-footer-group`
- nao houve alteracao de view, filtros, calculos, regras financeiras, Prestacao, Resumo ou Balancete

## Auditoria da logo no Extrato impresso

- auditoria concluida sem implementacao funcional: o Extrato impresso recebe o nome institucional pelo contexto global, mas o template `conta_extrato.html` nao renderiza `financeiro_shell_brand_logo_url` como imagem no cabecalho
- Prestacao, Resumo e Balancete usam a logo institucional via `<img>` com o mesmo contexto global, indicando causa provavel no template do Extrato, nao em calculo, configuracao ou regra financeira
- proxima microetapa recomendada: inserir no cabecalho documental do Extrato o mesmo bloco de logo institucional usado nos demais relatorios, mantendo fallback para nome quando nao houver logo

## Registro documental de tipo/disponibilidade de conta

- registrada frente futura para tipo de conta financeira, disponibilidade/vinculacao de saldo, mensagem opcional de indisponibilidade e modos de composicao do Balancete
- consolidado documentalmente que integralizacao de capital nao e despesa operacional e nao deve ser misturada ao saldo livre/disponivel sem destaque
- registrada pendencia separada para auditar a logo institucional no Extrato impresso
- nao houve implementacao, alteracao de codigo, templates, models, migrations, calculos ou relatorios nesta microetapa

## Auditoria da regra de conta inativa

- auditoria concluida sem implementacao funcional: formularios/autocomplete de lancamentos ainda permitem contas inativas em novos lancamentos, enquanto a importacao de lancamentos ja usa apenas contas ativas
- relatorios e filtros historicos usam contas sem filtrar por `ativa`, preservando historico, mas ainda exibem contas inativas mesmo sem movimento no periodo
- proxima microetapa recomendada: ajustar criacao/clone/autocomplete para oferecer apenas contas ativas e preservar contas inativas ja vinculadas na edicao, depois refinar filtros historicos por movimento no periodo

## Conta inativa em novos lancamentos

- novos lancamentos e conta destino de transferencia passam a aceitar apenas contas ativas no formulario/autocomplete
- edicao de lancamento antigo preserva a conta origem/destino ja vinculada, mesmo se inativa, sem abrir todas as inativas
- clones passam a ser tratados como novos lancamentos: conta origem/destino inativa do original nao e reaproveitada automaticamente
- filtros e relatorios historicos permanecem fora desta microetapa e seguem como pendencia separada

## MVP do Balancete Institucional

- foi criado o primeiro relatorio proprio `Balancete Institucional`, com rota, view, template documental e link no menu de Relatorios do financeiro
- o Balancete reutiliza `montar_contexto_fechamento_periodo`, preservando a mesma base de calculo da Prestacao/Fechamento para saldos, receitas, despesas e transferencias por escopo
- o MVP inclui filtros essenciais, fundo branco para impressao, secoes numeradas, composicao final e duas assinaturas selecionaveis a partir de `AssinaturaInstitucional`
- ajuste complementar: o print/PDF do Balancete recebeu margens A4 mais equilibradas, largura documental centralizada e respiro lateral, sem alterar calculos, filtros, view ou rota
- ajuste complementar: o print/PDF recebeu fonte/espacamento mais confortaveis, maior respiro superior e fallback de assinaturas para preencher automaticamente ate duas assinaturas ativas ou manter espacos genericos
- refinamento documental: o Balancete ganhou cabecalho mais institucional, abrangencia resumida no print, melhor uso da largura da folha e ocultacao padrao de contas zeradas apenas na apresentacao documental
- ajuste complementar: o print passou a usar margens reais mais seguras e assinaturas reais deixaram de ser preenchidas automaticamente sem selecao manual
- ajuste complementar: o documento impresso passou a ter margem visual garantida no wrapper `.balancete-documento`, o cabecalho impresso ficou sem abrangencia/lista de contas e assinaturas reais permanecem dependentes de selecao manual
- ajuste complementar: a secao de assinaturas do Balancete agora so aparece quando houver assinatura selecionada, sem linhas ou rotulos genericos, e as margens laterais do wrapper impresso foram ampliadas
- ajuste complementar: as margens laterais do wrapper impresso foram ampliadas novamente e a linha de contas consideradas foi removida tambem da tela normal do Balancete
- ajuste complementar: as margens laterais do wrapper impresso do Balancete foram ampliadas para aproximadamente tres vezes o valor anterior
- ajuste complementar: as laterais do wrapper impresso foram equilibradas para 24mm e a fonte do corpo impresso foi levemente ampliada
- ajuste complementar: a fonte do corpo impresso do Balancete foi ampliada mais um pouco, preservando as laterais de 24mm
- nao houve alteracao de calculo financeiro, regra de transferencia, models, migrations, importacao/exportacao, Extrato, Resumo, Evolucao ou template da Prestacao/Fechamento

## Base comum de calculo para Fechamento e futuro Balancete

- a logica de contexto/calculo do Fechamento passou a ter ponto tecnico comum em `montar_contexto_fechamento_periodo`, preparando reaproveitamento pelo futuro Balancete Institucional
- a Prestacao/Fechamento atual preserva os mesmos nomes de contexto e comportamento, sem alteracao visual, filtros, regras de transferencia ou calculos
- nao foram criados relatorio, rota, URL, template, CSS, models, migrations, permissao ou assinatura nova nesta microetapa

## Revisao documental da direcao do Balancete Institucional

- a direcao foi revisada: a Prestacao/Fechamento permanece como relatorio analitico/gerencial, e o Balancete Institucional fica registrado como relatorio proprio futuro
- o Balancete devera reutilizar a mesma regra/base de calculo da Prestacao/Fechamento, com template documental proprio, fundo branco e duas assinaturas
- nao houve implementacao, alteracao de codigo, templates, CSS, testes, rotas, views, models, migrations ou calculos nesta microetapa documental

## Direcao futura de balancete para Prestacao/Fechamento

- foi registrada decisao conceitual para evoluir futuramente o impresso da Prestacao/Fechamento para modelo tipo balancete institucional
- a diretriz preserva os calculos atuais, a transparencia da composicao de saldo, fundo branco por padrao para economia de tinta e possibilidade futura de duas assinaturas
- nao houve implementacao, alteracao de codigo, templates, CSS, testes, models, migrations ou calculos nesta microetapa documental

## Refinamento da impressao da Prestacao/Fechamento

- o modo print/PDF da Prestacao/Fechamento foi compactado com margens menores, cabecalho mais enxuto, tabelas mais densas e menor espacamento entre blocos
- o bloco final de composicao do saldo e assinatura passou a ter controle de quebra para reduzir assinatura isolada em pagina quase vazia quando houver espaco
- nao houve alteracao em calculos, queries, regras de transferencia, filtros, Extrato, Resumo, Evolucao, models, migrations ou permissoes

## Padronizacao do filtro de contas nas telas analiticas

- Resumo, Fechamento/Prestacao e Evolucao por categorias passaram a usar o padrao visual/comportamental do filtro de contas validado no Extrato
- o filtro ganhou opcao clara de `Todas as contas`, busca local por nome, lista empilhada e dropdown com largura/altura confortaveis
- nao houve alteracao em calculos, regras de transferencia, impressao, listagem de lancamentos, models, migrations ou permissoes

## Registro documental de novas pendencias de filtro e impressao

- foram registradas documentalmente duas pendencias futuras: padronizar o filtro de contas nas telas com selecao de contas e refinar a impressao da Prestacao/Fechamento do periodo
- nao houve implementacao funcional, alteracao de codigo, templates, CSS, testes, filtros, relatorios ou calculos nesta microetapa

## Correcao da edicao de conta financeira

- o formulario de conta financeira passou a renderizar `data_saldo_inicial` no formato HTML `YYYY-MM-DD` ao editar registro existente
- a edicao carrega o `saldo_inicial` e a `data_saldo_inicial` ja cadastrados e permite alterar esses valores
- nao houve alteracao em calculos de saldo, Extrato, Fechamento/Prestacao, lancamentos ou importacao

## Correcao de duplicidade de favorecido por nome

- o cadastro e a edicao de favorecidos/pessoas financeiras passaram a bloquear duplicidade por nome normalizado
- a normalizacao considera maiusculas/minusculas, espacos extras e acentos, preservando a edicao do proprio registro
- a importacao auxiliar de favorecidos passou a usar a mesma normalizacao para detectar nomes ja cadastrados ou repetidos na planilha
- ajuste complementar: a regra-mae de identificadores-chave foi registrada para todos os cadastros, mas a implementacao pratica segue restrita a favorecidos nesta microetapa
- na importacao de favorecidos, nome normalizado ja existente/repetido passa a ser descrito como conflito cadastral, separado conceitualmente de duplicidade de codigo/linha
- nao houve limpeza, mescla ou alteracao de registros duplicados ja existentes

## Classificacao documental de novas pendencias do financeiro

- novas melhorias levantadas apos Fechamento/Prestacao e Extrato multi-contas foram registradas e classificadas documentalmente, sem implementacao funcional nesta microetapa
- os itens foram organizados em `ROADMAP_FINANCEIRO.md`, acompanhados em `MAPA_RECLASSIFICACAO.md` e regras permanentes objetivas foram acrescentadas em `REGRAS_NEGOCIO.md`

## Extrato com seleção de múltiplas contas

- o Extrato financeiro passou a permitir seleção de uma conta, várias contas ou todas as contas em `/financeiro/extratos/`
- o comportamento antigo por conta individual foi preservado, inclusive compatibilidade com o parâmetro `conta`
- para múltiplas contas, saldo anterior, entradas, saídas, saldo acumulado linha a linha e saldo final passam a respeitar o escopo selecionado
- transferências internas ao conjunto selecionado não alteram o saldo consolidado nem aparecem como linha artificial zerada
- transferências com apenas uma ponta no escopo aparecem como entrada ou saída, conforme origem/destino selecionados
- em extrato multi-contas, cada movimento exibido mostra a conta relacionada para facilitar leitura em tela e impressão
- validações executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `py manage.py test financeiro.tests.PrestacaoContasTransferenciasEscopoTests financeiro.tests.ExtratoFinanceiroMultiplasContasTests` OK
- ajuste complementar do filtro: seleção parcial deixa de voltar automaticamente para `Todas as contas`, envio sem nenhuma conta mostra orientação clara, o seletor ficou mais largo e ganhou busca local por nome da conta
- ajuste visual complementar: o dropdown de contas do Extrato deixou de ser cortado pelo card de filtros e passou a ter altura máxima com rolagem interna
- ajuste complementar da busca: o filtro local por nome de conta passou a ocultar as opções em tempo real e a lista do Extrato ficou empilhada em uma conta por linha

## Correção do Fechamento do período por escopo de transferências

- o Fechamento do período / Prestação de contas passou a usar a mesma referência operacional do Extrato para movimentos e saldos: `data_pagamento` com fallback para `data_competencia`
- receitas e despesas continuam operacionais e não incluem transferências
- transferências passaram a compor saldo conforme o escopo de contas selecionado:
  - origem e destino dentro do filtro se anulam no consolidado
  - somente destino dentro do filtro entra como entrada por transferência
  - somente origem dentro do filtro entra como saída por transferência
- a opção `Exibir transferências` ficou limitada ao detalhamento analítico; ela não altera saldo inicial, saldo final nem reconciliação
- mesmo com `Exibir transferências` desligado, os totais de entrada/saída por transferência necessários à reconciliação continuam compondo o resumo do saldo
- transferências internas ao escopo selecionado não aparecem no bloco visual de transferências como linha zerada ou entrada/saída desnecessária
- foi criado teste pontual cobrindo transferência interna ao escopo, apenas origem no filtro, apenas destino no filtro e opção `Exibir transferências` ligada/desligada sem alterar saldo real
- validações executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `py manage.py test financeiro.tests.PrestacaoContasTransferenciasEscopoTests` OK
  - conferência local da conta `Dinheiro` em `01/03/2026 a 31/03/2026` OK: Fechamento e Extrato reconciliaram saldo inicial, entradas, saídas e saldo final
- ajuste visual complementar: linhas/cards de entradas ou saídas por transferência externa ao escopo agora só aparecem quando o respectivo total for diferente de zero, sem alterar cálculo

## Refinamento final da `Prestacao de contas` para `Fechamento do periodo`

- a microetapa refinou a mesma tela/relatorio sem reabrir regra de negocio, calculos ou reconciliacao contabil
- o nome principal da experiencia passou a ser `Fechamento do periodo`, com subtitulo e textos de apoio mais gerenciais
- a apresentacao monetaria foi padronizada com o mesmo modelo do `Extrato`:
  - `R$` a esquerda
  - numero a direita
  - mesma celula
- esse padrao passou a valer na tela e no impresso para:
  - KPIs
  - tabelas
  - totais
  - saldo inicial/final
  - composicao do saldo
- foi incluida a opcao `Mostrar contas sem movimentacao e sem saldo`
  - comportamento padrao: desligado
  - com a opcao desligada, as composicoes ocultam contas zeradas que tambem nao tiveram movimentacao no periodo
  - com a opcao ligada, essas contas voltam a aparecer no relatorio
- a impressao ficou mais compacta, sem prometer pagina unica em qualquer cenario:
  - reducao leve de fonte e padding no modo print
  - menor espacamento entre paineis
  - cabecalho impresso mais enxuto
  - ocultacao de secoes opcionais vazias, quando aplicavel, para aproveitar melhor a folha
- validacoes executadas nesta microetapa:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- com esse refinamento, a tela fica pronta para homologacao final

## Correcao da ordem formal e da paginacao impressa na `Prestacao de contas`

- a microetapa corrigiu exclusivamente a impressao/PDF da `Prestacao de contas`, sem alterar calculos, reconciliacao ou regra de negocio
- a numeracao das secoes passou a seguir a ordem visual real do relatorio, com contagem automatica aplicada apenas aos blocos formais numerados
- ordem impressa consolidada:
  - `Saldo disponivel no inicio do periodo`
  - `Resumo do saldo disponivel`
  - `Receitas do periodo`
  - `Despesas do periodo`
  - `Transferencias do periodo`, quando exibidas
  - `Composicao do saldo final`
  - `Despesas por centro de custo`, quando exibidas
- a secao `Despesas do periodo` recebeu protecao de quebra no modo print para evitar fragmentacao ruim no fim da pagina
- no modo print, os blocos em grade passam a ser empilhados para melhorar continuidade documental da leitura
- a tabela da secao passou a reforcar `thead` como cabecalho de continuacao e `tfoot` como fechamento real, impedindo que o total apareca antes do termino efetivo da listagem
- validacoes executadas nesta microetapa:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- com esse ajuste, a `Prestacao de contas` fica pronta para homologacao final focada em impressao

## Aplicacao do padrao analitico consolidado na tela `Prestacao de contas`

- a microetapa adaptou a tela `Prestacao de contas` ao padrao analitico consolidado a partir de `Evolucao por categorias`, `Resumo` e `Extrato`, preservando calculos, reconciliacao, semantica financeira e identidade documental da tela
- estrutura aplicada:
  - `titulo/contexto`
  - `filtro no topo da analise`
  - `KPIs`
  - `resultado principal`
- o filtro passou a permanecer no mesmo lugar estrutural da pagina:
  - abre no topo quando ainda nao ha leitura valida ou quando existe erro de periodo
  - fica recolhido por padrao quando o relatorio ja esta carregado
  - o resumo recolhido orienta rapidamente periodo, contas e opcoes de leitura
- heranca direta do padrao-base:
  - hero mais enxuto com contexto principal no topo
  - card proprio para filtros
  - card proprio para KPIs
  - card proprio para resultados
- adaptacoes especificas da `Prestacao de contas`:
  - o relatorio preserva carater formal/documental
  - os blocos de reconciliacao e de composicao do saldo final continuam com protagonismo
  - a impressao segue isolada do shell, dos filtros e dos KPIs, preservando a leitura documental util
- frente ativa e prioridade:
  - a frente ativa continua sendo a padronizacao das telas analiticas do `financeiro`
  - `Resumo`, `Extrato` e `Prestacao de contas` passam a formar a propagacao principal ja executada dessa base
  - a normalizacao de favorecidos permanece fora da sequencia operacional desta etapa
  - a frente de frequencia/recorrencia continua futura e nao priorizada agora
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- observacao:
  - a tela `Prestacao de contas` fica pronta para homologacao visual

## Padronizacao das celulas monetarias do `Extrato`

- a microetapa atuou apenas na composicao visual interna das celulas monetarias do `Extrato`, sem alterar calculos, colunas ou regras de negocio
- padrao consolidado:
  - `R$` alinhado a esquerda
  - numero alinhado a direita
  - ambos na mesma celula
- esse padrao passou a valer para:
  - coluna `Valor`
  - coluna `Saldo`
  - linhas especiais de `Saldo anterior`/`Saldo inicial`
  - linha de `Saldo final`
- regra preservada:
  - o sinal financeiro continua junto do numero
  - saidas/despesas continuam negativas
  - entradas/receitas continuam positivas
- efeito esperado:
  - leitura monetaria mais limpa
  - menor sensacao de `R$` solto no PDF
  - maior consistencia entre tela e impressao
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- observacao:
  - o extrato fica pronto para homologacao final desta rodada visual

## Refinamento visual do miolo do `Extrato`

- a microetapa atuou apenas no layout/apresentacao da tabela do `Extrato`, sem alterar calculos, ordenacao cronologica ou semantica financeira
- limpeza aplicada no corpo da tabela:
  - o texto auxiliar de tipo por linha (`Receita`, `Despesa`, `Transferencia`) deixou de aparecer em `Favorecido`
  - `Descricao` e `Favorecido` permanecem em colunas separadas
  - o valor passou a ser exibido de forma mais direta, em linha unica, sem `C/D`
- redistribuicao de largura:
  - `Descricao` e `Favorecido` ganharam mais largura util
  - `Data`, `Doc.`, `Valor` e `Saldo` foram protegidos com larguras menores e mais proporcionais
- regra visual consolidada:
  - entradas/receitas seguem positivas
  - saidas/despesas seguem negativas
  - o proprio valor passa a comunicar a natureza do movimento, sem texto auxiliar adicional no miolo
- efeito esperado:
  - linhas mais baixas
  - menos truncamento perceptivel
  - leitura mais limpa e financeira do extrato em tela e impressao
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- observacao:
  - o extrato fica pronto para nova homologacao visual desta rodada de limpeza

## Alinhamento estrutural do `Extrato` entre tela e impressao

- a microetapa corrigiu a tentativa anterior de modelo bancario compacto, que nao foi aprovada na homologacao visual
- a regra consolidada passa a ser:
  - tela e impressao compartilham a mesma logica estrutural de colunas
  - `Descricao` e `Favorecido` permanecem separados
  - `Valor` nao usa `C/D` e passa a respeitar sinal positivo/negativo
- estrutura final das colunas no `Extrato`:
  - `Data`
  - `Doc.`
  - `Descricao`
  - `Favorecido`
  - `Valor`
  - `Saldo`
- o impresso deixou de usar:
  - historico fundido
  - coluna `Valor` com `C/D`
  - separacao anterior entre `Entrada` e `Saida`
- regra do `Valor`:
  - receitas/entradas aparecem positivas
  - despesas/saidas aparecem negativas
  - saldo continua em coluna propria, alinhado a direita e protegido
- ajuste minimo no backend:
  - a view passou a expor `valor_exibicao` assinado e `valor_exibicao_absoluto` para a apresentacao da coluna `Valor`, sem alterar calculos do extrato
- preservacao:
  - ordem cronologica mantida
  - calculos de saldo mantidos
  - semantica financeira mantida
  - impressao continua isolada do shell e dos filtros
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - PDF de conferência gerado em `tmp/extrato_homologacao_alinhado.pdf`
- observacao:
  - o extrato fica pronto para nova homologacao visual desta estrutura alinhada

## Redesenho do impresso do `Extrato` para modelo bancario compacto

- a microetapa redesenhou apenas o layout de impressao/PDF do `Extrato`, preservando calculos, ordem cronologica, semantica financeira e a versao de tela normal
- o impresso passou a usar uma tabela propria de 5 colunas:
  - `Data`
  - `Doc.`
  - `Historico`
  - `Valor`
  - `Saldo`
- deixaram de existir como colunas separadas no impresso:
  - `Favorecido`
  - `Mov.`
  - `Entrada`
  - `Saida`
- regra do `Historico` no impresso:
  - a descricao da movimentacao passa a ser a linha principal
  - favorecido e tipo da movimentacao passam a compor uma linha secundaria compacta no mesmo campo
  - o `Historico` vira a coluna textual elastica principal do extrato impresso
- regra da coluna `Valor` no impresso:
  - `entrada` passa a ser exibida como `valor C`
  - `saida` passa a ser exibida como `valor D`
  - o saldo continua em coluna propria, alinhado a direita e protegido
- linhas especiais permanecem no documento:
  - `Saldo anterior`/`Saldo inicial`
  - `Saldo final`
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - PDF de conferência gerado em `tmp/extrato_homologacao_bancario.pdf`
- observacao:
  - o impresso do extrato fica pronto para nova homologacao visual neste modelo bancario compacto

## Correcao da sobreposicao de colunas no impresso do `Extrato`

- a microetapa atuou apenas no layout de impressao/PDF da tabela do `Extrato`, sem alterar calculos, ordenacao cronologica, saldos ou semantica financeira
- a base do ajuste foi concentrada no `@media print` do template do extrato
- correcoes aplicadas no impresso:
  - tabela passou a usar `table-layout: fixed` no papel
  - colunas numericas ficaram com larguras protegidas para `Entrada`, `Saida` e `Saldo`
  - a coluna `Mov.` ficou mais enxuta no impresso
  - a coluna `Doc.` foi reduzida no papel para liberar respiro no miolo
  - `Descricao`, `Favorecido` e `Observacoes` passaram a aceitar truncamento controlado com `ellipsis`
  - padding e font-size do miolo foram reduzidos apenas no modo print
  - alinhamento numerico foi reforcado a direita para melhorar leitura de valores e saldo final
- efeito esperado:
  - o miolo do extrato impresso deixa de colidir visualmente entre `Favorecido`, `Mov`, `Entrada`, `Saida` e `Saldo`
  - a leitura textual continua aceitavel, com prioridade pratica para valores e fechamento do extrato
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - geracao de PDF de homologacao do extrato corrigido em `tmp/extrato_homologacao_impresso_corrigido.pdf`
- observacao:
  - o impresso do extrato fica pronto para nova homologacao visual focada em PDF/print

## Refinamento do impresso do `Extrato` com compactacao tipografica leve

- a microetapa refinou novamente apenas o modo print/PDF do `Extrato`, preservando a correcao anterior de sobreposicao e sem tocar na tela normal
- objetivo desta rodada:
  - reduzir truncamento excessivo
  - manter texto em linha unica como regra principal
  - devolver mais conteudo util para `Descricao` e `Favorecido`
- ajustes aplicados no impresso:
  - fonte da tabela reduzida discretamente para um passo mais compacto
  - `line-height` e `padding` horizontal/vertical reduzidos apenas no modo print
  - redistribuicao de larguras favorecendo `Descricao` e `Favorecido`
  - `Doc.` foi rebaixada no impresso, ficando mais estreita
  - `Mov.` ficou ligeiramente mais compacta
  - `Entrada`, `Saida` e `Saldo` permaneceram protegidas e alinhadas a direita
  - truncamento por `ellipsis` foi mantido apenas como fallback nas colunas textuais mais longas
- efeito esperado:
  - menos `...` no miolo do extrato impresso
  - mais conteudo visivel em `Descricao` e `Favorecido`
  - preservacao da leitura dos valores e do saldo final
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - novo PDF de conferência gerado em `tmp/extrato_homologacao_impresso_corrigido2.pdf`
- observacao:
  - o impresso do extrato fica pronto para nova homologacao visual desta segunda rodada de refinamento

## Aplicacao do padrao analitico consolidado na tela `Extrato`

- a microetapa adaptou a tela `Extrato` ao padrao analitico consolidado em `Evolucao por categorias`, preservando a logica cronologica do extrato, os calculos de saldo e a base documental de impressao
- estrutura aplicada no `Extrato`:
  - `titulo/contexto`
  - `filtro no topo da analise`
  - `KPIs`
  - `resultado principal`
- o filtro passou a permanecer no mesmo lugar estrutural da tela:
  - abre no topo quando ainda nao ha conta selecionada ou quando existe erro de carregamento
  - fica recolhido por padrao quando o extrato ja esta carregado
  - o resumo recolhido mostra conta, periodo e estado da opcao de observacoes
- a hierarquia visual foi reforcada:
  - filtros ficaram visualmente secundarios
  - os resumos executivos ganharam mais protagonismo
  - a tabela cronologica do extrato permaneceu como area principal da pagina
- heranca direta do padrao-base:
  - hero mais enxuto com contexto principal no topo
  - card proprio para filtros
  - card proprio para KPIs
  - card proprio para resultados
- adaptacoes especificas do `Extrato`:
  - a tela manteve foco em `saldo anterior/saldo inicial`, `entradas`, `saidas`, `quantidade de movimentacoes` e `saldo final`
  - a tabela cronologica permaneceu como protagonista, com leitura crescente por data e saldo acumulado apos cada movimento
  - a impressao do extrato foi preservada, escondendo topo, filtros e KPIs no papel para manter apenas a area documental util
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK confirmando:
    - filtro no topo
    - KPIs apenas quando ha conta carregada
    - bloco principal `Movimentacoes da conta`
    - acao `Atualizar extrato`
- observacao:
  - a tela `Extrato` fica pronta para homologacao visual
  - o padrao analitico segue forte o bastante para a proxima tela da sequencia apos essa homologacao

## Aplicacao do padrao analitico consolidado na tela `Resumo`

- a microetapa adaptou a tela `Resumo` ao padrao analitico consolidado em `Evolucao por categorias`, preservando calculos, semantica financeira e fluxo documental de impressao
- estrutura aplicada no `Resumo`:
  - `titulo/contexto`
  - `filtro no topo da analise`
  - `KPIs`
  - `resultados`
- o filtro passou a permanecer no mesmo lugar estrutural da tela:
  - abre no topo quando ainda nao ha leitura valida ou quando existe erro de periodo
  - fica recolhido por padrao quando o resultado ja esta carregado
  - o resumo recolhido mostra periodo, contas e o estado das opcoes principais
- a hierarquia visual foi reforcada:
  - filtros ficaram visualmente secundarios
  - os KPIs ganharam mais protagonismo
  - a area de resultados passou a concentrar os agrupamentos de receitas, despesas, transferencias e centro de custo em blocos mais claros
- heranca direta do padrao-base:
  - hero mais enxuto com contexto principal no topo
  - card proprio para filtros
  - card proprio para KPIs
  - card proprio para resultados
- adaptacoes especificas do `Resumo`:
  - a comparacao entre periodos nao foi levada para esta tela
  - o bloco executivo foi mantido focado em saldo inicial, receitas, despesas, saldo do periodo e saldo final consolidado
  - o resultado principal foi organizado em tabelas analiticas de receitas e despesas, com blocos complementares para transferencias e centro de custo quando aplicavel
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- observacao:
  - a tela `Resumo` fica pronta para homologacao visual
  - o padrao analitico fica forte o bastante para seguir depois para a proxima tela da sequencia, desde que a homologacao visual confirme a leitura final

## Filtro fixo no topo da analise em `Evolucao por categorias`

- a microetapa atuou apenas na estrutura visual da tela `Evolucao por categorias`, preservando calculos, comparacao entre periodos, semantica financeira e impressao
- o painel de filtros deixou de mudar de posicao na pagina:
  - permanece no topo da area analitica
  - fica acima dos KPIs
  - fica acima dos resultados
- o estado resumido e o estado expandido agora ocupam o mesmo lugar estrutural
- quando ha resultado renderizado:
  - o filtro pode vir recolhido por padrao
  - o resumo compacto continua no topo da analise
  - o resumo passou a orientar melhor periodo/comparacao, escopo, leitura, granularidade e selecao resumida
- preservacao:
  - os resultados continuam protagonistas
  - nenhuma regra funcional mudou
  - nenhuma regra de receita/despesa mudou
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- observacao:
  - a tela fica pronta para homologacao visual focada em UX
  - a estrutura passa a ficar madura como base local do futuro padrao analitico do sistema

## Rebaixamento do painel de filtros e limpeza do topo em `Evolucao por categorias`

- a microetapa atuou apenas na hierarquia visual da tela `Evolucao por categorias`, preservando calculos, comparacao entre periodos, semantica financeira e impressao funcional
- o painel de filtros deixou de disputar protagonismo com a analise:
  - quando ha resultado carregado, o painel passa a vir recolhido por padrao
  - no estado recolhido, a tela mostra um resumo compacto da configuracao atual
  - o usuario pode reabrir facilmente pelo proprio resumo com acao clara de editar/ocultar filtros
- a pagina passou a ficar mais coerente com tela analitica:
  - o card de resultados foi separado do card de filtros
  - o resultado fica visualmente acima do formulario na hierarquia da pagina
  - KPIs e blocos de leitura continuam protagonistas
- o topo ficou menos carregado:
  - os chips principais foram reduzidos para `comparacao`/`periodo principal`, `escopo`, `leitura` e `granularidade`
  - `analise`, `selecao atual` e `contas` passaram para contexto textual secundario
- preservacao:
  - nenhuma regra funcional foi alterada
  - nenhuma regra de receita/despesa foi alterada
  - o comparativo consolidado e o fluxo normal sem comparativo foram preservados
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- observacao:
  - a tela fica pronta para nova homologacao visual focada em UX

## Reorganizacao da hierarquia visual em `Evolucao por categorias`

- a microetapa atuou apenas na apresentacao da tela `Evolucao por categorias`, preservando calculos, semantica financeira, comparacao entre periodos e fluxo normal sem comparativo
- o topo da pagina ganhou hierarquia visual mais clara:
  - cabecalho com tratamento de hero leve
  - melhor separacao entre titulo, subtitulo, contexto e acoes
  - botao principal de impressao com mais protagonismo do que a acao secundaria de retorno
- o painel de filtros passou a ter leitura mais claramente secundaria:
  - card de filtros com menor peso do que a area de resultados
  - agrupamento mais limpo
  - `Atualizar grafico` destacado como acao principal
  - `Limpar` mantido como acao secundaria
- a faixa de KPIs ganhou mais forca executiva:
  - numeros maiores
  - contraste e separacao mais firmes entre os cards
  - maior respiracao entre os indicadores
- a area de resultados ficou mais protagonista:
  - bloco principal do grafico/leitura detalhada com mais destaque
  - tabela comparativa em segundo nivel visual, sem competir com o resultado principal
  - reforco de borda, sombra, espacamento e legibilidade nos blocos comparativos
- preservacao:
  - nenhuma regra funcional foi alterada
  - nenhuma semantica de receita/despesa foi alterada
  - impressao permaneceu sem regressao estrutural
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- observacao:
  - a tela fica pronta para homologacao visual focada em UX

## Refino final da tabela comparativa e normalizacao cronologica em `Evolucao por categorias`

- a microetapa atuou apenas no comparativo da tela `Evolucao por categorias`, preservando o fluxo normal sem comparativo e sem reabrir a logica central do grafico consolidado
- a coluna `Item` da tabela comparativa passou a usar o nome curto do item:
  - nome simples quando nao ha ambiguidade
  - fallback expandido apenas quando houver nomes repetidos de fato
- a linha `Total` deixou de herdar semantica de receita/despesa individual e passou a usar leitura liquida propria:
  - `comparativo > principal` = melhor (`is-receita`)
  - `comparativo < principal` = pior (`is-despesa`)
  - empate = neutro
- essa regra do `Total` agora orienta:
  - `Diferenca absoluta`
  - `Variacao percentual`
- a comparacao entre periodos passou a ser normalizada cronologicamente:
  - `Periodo principal` sempre representa o intervalo anterior
  - `Periodo comparativo` sempre representa o intervalo posterior
  - quando o usuario preenche invertido, a tela reorganiza os intervalos automaticamente
  - a interface mostra aviso discreto informando a reorganizacao para manter a leitura `anterior -> posterior`
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando:
    - inputs reorganizados cronologicamente
    - aviso discreto de reorganizacao visivel
    - coluna `Item` com nome curto
    - linha `Total` com semantica liquida positiva quando o comparativo supera o principal
- observacao:
  - a tela fica tecnicamente pronta para encerramento deste bloco
  - homologacao visual/manual curta continua sendo a ultima confirmacao opcional antes de encerrar a frente como 100% fechada

## Correcao da barra e da semantica de cores no comparativo separado de `Evolucao por categorias`

- a microetapa reverteu a tentativa anterior de barra divergente no bloco `Itens com maior diferenca absoluta`, porque a leitura visual validada pelo usuario nao ficou boa
- regra final do bloco:
  - a barra voltou a usar apenas magnitude absoluta
  - o texto monetario continua respeitando o sinal real do item
  - `receita` permanece positiva no texto
  - `despesa` permanece negativa no texto
- o nome visual do item no bloco deixou de usar prefixo `+`; o rotulo curto agora fica neutro, preservando apenas o nome do item e o fallback expandido quando houver ambiguidade real
- a tabela comparativa passou a aplicar semantica de cor pela natureza financeira do item:
  - em `receita`, comparativo maior que principal = melhor (`is-receita`) e comparativo menor = pior (`is-despesa`)
  - em `despesa`, comparativo maior em magnitude = pior (`is-despesa`) e comparativo menor em magnitude = melhor (`is-receita`)
  - a regra passou a valer ao menos para `Diferenca absoluta` e `Variacao percentual`
- preservacao:
  - comparativo consolidado nao foi alterado
  - fluxo normal sem comparativo nao foi alterado
  - ordenacao do bloco separado permaneceu a mesma
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando:
    - barra simples por magnitude absoluta
    - despesa negativa no texto
    - ausencia do prefixo `+` no nome do item
    - semantica positiva para receita maior no comparativo
    - semantica negativa para despesa maior no comparativo
- observacao:
  - o resultado desta etapa ficou validado tecnicamente e por smoke controlado de HTML
  - a confirmacao visual/manual final no navegador real continua pendente nesta propria rodada

## Correcao da semantica visual das barras de despesa no comparativo separado

- a microetapa corrigiu o defeito remanescente do bloco `Itens com maior diferenca absoluta`: o texto ja estava negativo para despesa, mas a barra ainda crescia para a direita como se fosse positiva
- regra visual final aplicada no comparativo separado:
  - `receita` continua com texto positivo e barra crescendo para a direita
  - `despesa` continua com texto negativo e passa a ter barra crescendo para a esquerda
  - o bloco agora usa eixo central fixo na trilha para explicitar a divergencia positiva/negativa
- separacao consolidada:
  - texto continua usando campos assinados de exibicao
  - escala/largura continuam usando magnitude absoluta
  - direcao da barra passa a depender da natureza do item (`receita` / `despesa`)
- preservacao:
  - rotulos curtos permaneceram os mesmos
  - ordenacao por maior diferenca absoluta permaneceu a mesma
  - comparativo consolidado nao foi alterado
  - fluxo normal sem comparativo permaneceu preservado
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando:
    - texto de despesa negativo
    - markup de barra negativa para despesa
    - markup de barra positiva para receita
    - cores/classe coerentes no bloco
- observacao:
  - a semantica visual ficou validada tecnicamente nesta etapa
  - a confirmacao visual/manual em navegador real continua pendente para homologacao visual final

## Correcao final da renderizacao do sinal na comparacao separada de `Evolucao por categorias`

- a microetapa reabriu a correcao anterior porque o retorno do uso real confirmou que despesas ainda apareciam positivas na interface
- origem exata confirmada:
  - a comparacao separada ainda usava campos ambiguidos entre calculo visual e exibicao textual
  - no template, os textos monetarios ainda eram montados com prefixo de moeda externo sobre campos genericos formatados
  - a view ainda nao separava de forma explicita `valor exibido com sinal` de `magnitude absoluta usada na barra`
- regra final aplicada:
  - textos da comparacao agora usam campos assinados e completos, como `-R$ 300,00` e `R$ 200,00`
  - barras continuam usando apenas magnitude absoluta para largura e comparabilidade visual
  - totais textuais da comparacao tambem passaram a usar a leitura assinada, sem reaproveitar os campos de magnitude
- campos explicitamente separados no backend:
  - `valor_a_exibicao` / `valor_b_exibicao`
  - `valor_a_exibido_formatado` / `valor_b_exibido_formatado`
  - `valor_a_absoluto` / `valor_b_absoluto`
- preservacao:
  - ordenacao analitica do bloco permaneceu a mesma
  - comparativo consolidado nao foi alterado
  - fluxo normal sem comparativo permaneceu preservado
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando:
    - receita positiva no texto exibido
    - despesa negativa no texto exibido
    - barras calculadas por magnitude absoluta
    - tabela comparativa e totais usando valores assinados
    - fluxo normal sem comparativo preservado
- observacao:
  - a renderizacao tecnica ficou validada nesta etapa
  - a confirmacao visual/manual no navegador continua pendente para encerrar o defeito como homologado visualmente

## Correcao do sinal de despesas no comparativo separado de `Evolucao por categorias`

- a microetapa corrigiu uma regressao pontual no bloco `Itens com maior diferenca absoluta` da comparacao separada
- causa objetiva:
  - a comparacao separada reutilizava os totais visuais das series, armazenados em magnitude absoluta para ordenar o bloco e dimensionar as barras
  - esses mesmos totais estavam sendo formatados diretamente para exibicao, fazendo despesas aparecerem com sinal positivo ao usuario
- regra final consolidada:
  - o valor exibido respeita a natureza financeira real da serie
  - `receita` continua positiva
  - `despesa` passa a aparecer negativa
  - a barra visual continua baseada em magnitude absoluta para preservar comparabilidade e largura coerente
  - a ordenacao do bloco permanece por maior diferenca absoluta, depois maior soma de magnitudes e depois ordem alfabetica
  - os rotulos curtos com `+ Nome` e fallback por ambiguidade permanecem preservados
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando:
    - despesas negativas no comparativo separado
    - receitas positivas preservadas
    - tabela comparativa presente apenas quando ha periodo comparativo
    - fluxo normal sem comparativo preservado

## Rotulos curtos e ordenacao analitica no comparativo separado

- a microetapa refinou apenas o bloco `Itens com maior diferenca absoluta` da tela `Evolucao por categorias`
- a logica de calculo, KPIs, comparativo consolidado, comparativo separado e fluxo normal sem comparativo permaneceram preservados
- regra final de rotulo do bloco:
  - categorias e subcategorias exibem nome curto com prefixo visual `+`
  - quando nomes repetidos geram ambiguidade real, apenas esses itens usam o formato expandido `Categoria / Nome`
  - a tabela comparativa continua podendo preservar o label analitico completo
- regra final de ordenacao do bloco:
  - maior diferenca absoluta entre os periodos
  - maior valor total somado entre os dois periodos
  - ordem alfabetica como desempate final
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando labels curtos, fallback por ambiguidade, ordenacao analitica do bloco e fluxo normal preservado

## Normalizacao dos rotulos de periodo na comparacao de `Evolucao por categorias`

- a microetapa corrigiu apenas a apresentacao textual dos periodos quando `Periodo comparativo` esta preenchido
- a logica de calculo, KPIs, tabela comparativa, grafico consolidado, grafico separado e fluxo normal sem comparativo permaneceram preservados
- regra final de formatacao:
  - intervalos de mes fechado usam `MM/AA`
  - multiplos meses fechados usam `MM/AA a MM/AA`
  - intervalos quebrados em qualquer ponta usam `DD/MM/AAAA a DD/MM/AAAA`
- pontos da UI normalizados:
  - legenda do comparativo consolidado
  - chips/resumos da comparacao
  - legenda e rotulos das barras no comparativo separado
  - cabecalhos da tabela comparativa
  - resumo humano dos filtros/impressao da comparacao
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando exemplos do formatador, comparativo separado sem `Principal`/`Comparativo` soltos, consolidado com labels normalizados e fluxo normal preservado

## Correcao da legenda e anti-colisao dos rotulos no comparativo consolidado

- a microetapa atuou apenas no modo `Periodo comparativo` preenchido + `Leitura = Consolidado` da tela `Evolucao por categorias`
- o fluxo sem `Periodo comparativo` permanece preservado e o modo `Leitura = Separado` permanece com o grafico de barras horizontais por item ja aprovado
- regra final da legenda:
  - as duas series do grafico consolidado usam os periodos reais selecionados como rotulo
  - a legenda visual nao deve voltar a usar `Periodo principal` / `Periodo comparativo` como nome das series
- regra final de anti-colisao dos rotulos:
  - a serie principal posiciona seus valores acima dos pontos
  - a serie comparativa posiciona seus valores abaixo dos pontos
  - quando os valores do mesmo indice ficam muito proximos, o offset vertical aumenta
  - se ainda houver risco de colisao, um rotulo e suprimido naquele ponto e o valor exato permanece disponivel no tooltip
- validacoes executadas:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback OK confirmando legenda com periodos reais e rotulos reposicionados no comparativo consolidado

## Correcao dos rotulos no comparativo consolidado de `Evolucao por categorias`

- a microetapa corrigiu apenas o modo `Periodo comparativo` preenchido + `Leitura = Consolidado`
- o grafico consolidado manteve a estrutura ja aprovada:
  - grafico unico de linhas
  - duas series
  - legenda com os periodos reais selecionados
- a regra de rotulos foi ajustada:
  - quando `Mostrar valores no grafico` esta ativo e a comparacao possui ate 12 pontos, os valores aparecem nos pontos
  - quando a quantidade de pontos passa desse limite, os rotulos continuam suprimidos para evitar poluicao visual e a leitura exata permanece no tooltip
- o fluxo sem `Periodo comparativo` e o modo separado com barras horizontais por item permaneceram preservados
- validacoes executadas nesta microetapa:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK cobrindo:
    - fluxo normal sem comparativo sem grafico comparativo
    - comparativo consolidado com rotulos de dados renderizados em poucos pontos
    - comparativo separado preservando barras horizontais por item

## Correcao do grafico separado na comparacao de `Evolucao por categorias`

- a microetapa corrigiu apenas o modo `Periodo comparativo` preenchido + `Leitura = Separado`, sem alterar o fluxo normal sem comparativo nem o grafico consolidado ja aprovado
- o grafico-resumo anterior, que mostrava uma linha agregada entre `Principal` e `Comparativo`, foi removido por nao comunicar a comparacao item a item
- no modo separado, a tela passa a exibir um grafico-resumo discreto de barras horizontais agrupadas por item:
  - uma barra para o `Periodo principal`
  - uma barra para o `Periodo comparativo`
  - valores exibidos ao lado de cada barra
- a selecao visual do grafico separado mostra ate 8 itens, priorizados por maior diferenca absoluta entre os periodos; a tabela comparativa continua sendo a leitura principal e mantem a relacao completa
- validacoes executadas nesta microetapa:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK cobrindo fluxo normal sem comparativo, comparativo consolidado e comparativo separado com barras por item

## Correcao pontual da visualizacao comparativa em `Evolucao por categorias`

- a homologacao visual apontou tres defeitos reais no comparativo da tela e a microetapa atuou apenas neles, sem reabrir a feature
- no comparativo consolidado:
  - a legenda deixou de usar `Periodo principal` / `Periodo comparativo` como rotulos genericos
  - o grafico passou a mostrar os periodos reais selecionados como identificacao das duas series
  - os rotulos sobre os pontos passaram a ser suprimidos automaticamente quando houver risco de poluicao, preservando o tooltip como leitura exata
- no comparativo separado:
  - a tabela comparativa continua sendo a leitura principal
  - a tela voltou a ter apoio visual grafico, agora em bloco resumido e discreto, sem disputar protagonismo com a tabela
- o fluxo sem `Periodo comparativo` permaneceu intacto
- validacoes executadas nesta microetapa:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK cobrindo:
    - modo normal sem comparativo
    - comparativo consolidado com periodos reais e protecao contra sobreposicao
    - comparativo separado com grafico-resumo secundario

## Refinamento da visualizacao da comparacao em `Evolucao por categorias`

- a tela manteve integralmente o comportamento anterior quando o `Periodo comparativo` nao e preenchido
- com `Periodo comparativo` preenchido e `Leitura = Consolidado`, a comparacao passou a usar:
  - um unico grafico de linhas
  - duas series fixas: `Periodo principal` e `Periodo comparativo`
  - evolucao agregada dos valores selecionados na granularidade ativa
- com `Periodo comparativo` preenchido e `Leitura = Separado`, a comparacao deixou de priorizar graficos paralelos:
  - a tabela comparativa passou a ser a leitura principal
  - o bloco visual do comparativo ficou mais contido para evitar poluicao por excesso de linhas
- a view passou a montar um grafico consolidado proprio para a comparacao, reaproveitando a mesma base de buckets/series ja entregue na tela
- quando os rotulos temporais dos dois periodos nao coincidem exatamente, o grafico consolidado sinaliza leitura por posicao relativa dos buckets, sem alterar o modo normal da tela
- validacoes executadas nesta microetapa:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK cobrindo:
    - consulta normal sem periodo comparativo
    - comparacao consolidada com grafico unico
    - comparacao detalhada com tabela como leitura principal

## Refinamento de UX da comparacao entre periodos em `Evolucao por categorias`

- a comparacao entre periodos deixou de depender de um seletor explicito de `modo comparacao`
- a tela agora passou a trabalhar com contrato progressivo:
  - `Periodo principal` sempre visivel e obrigatorio para a consulta
  - `Periodo comparativo` opcional
  - sem `Periodo comparativo` preenchido, a tela funciona como consulta normal
  - com `Periodo comparativo` preenchido, a comparacao e ativada automaticamente
- a interface deixou de expor `Periodo A` e `Periodo B` como conceito principal de UX
- esses nomes foram substituidos visualmente por:
  - `Periodo principal`
  - `Periodo comparativo`
- o antigo seletor de modo foi mantido apenas parcialmente:
  - ele continua existindo para a escolha analitica do grafico
  - ele deixa de ser a chave para ligar ou desligar a comparacao
- a comparacao continua entregando:
  - total do periodo principal
  - total do periodo comparativo
  - diferenca absoluta
  - variacao percentual segura
  - tabela comparativa recolhida por padrao
- o modo normal permaneceu preservado sem regressao
- validacoes executadas nesta microetapa:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK cobrindo:
    - consulta normal sem periodo comparativo
    - comparacao automatica com periodo comparativo preenchido
    - renderizacao de `Periodo principal`, `Periodo comparativo` e `Tabela comparativa`

## Comparacao entre periodos entregue na tela `Evolucao por categorias`

- a tela `Evolucao por categorias` passou a suportar dois fluxos no mesmo shell:
  - modo normal ja consolidado
  - modo `Comparacao entre periodos`
- o modo novo foi implementado sem abrir nova tela e sem quebrar a arquitetura atual de filtros compactos, seletor analitico, impressao isolada e tabela auxiliar recolhida por padrao
- no modo comparacao, a interface agora exibe blocos claros para:
  - `Periodo A`
  - `Periodo B`
- os mesmos filtros analiticos continuam valendo para os dois periodos:
  - `Categorias` / `Subcategorias`
  - contas
  - leitura `Consolidado` / `Separado`
  - granularidade em `Dias`, `Meses`, `Trimestres` e `Anos`
  - opcao de mostrar valores no grafico
- a saida consolidada da comparacao passou a entregar:
  - total do `Periodo A`
  - total do `Periodo B`
  - diferenca absoluta
  - variacao percentual com tratamento seguro quando a base e zero
  - quantidade de lancamentos em cada periodo
  - tabela comparativa recolhida por padrao
- regra consolidada para percentual:
  - se `A = 0` e `B != 0`, a tela mostra `—`
  - se `A = 0` e `B = 0`, a tela mostra variacao neutra
  - se `A != 0`, calcula normalmente sobre a base do `Periodo A`
- validacoes executadas nesta microetapa:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado OK para:
    - modo normal preservado com categoria pai valida
    - modo comparacao com `Periodo A` e `Periodo B`
    - comparacao valida em `Subcategorias`
    - renderizacao de `Tabela comparativa`, `Diferenca absoluta` e `Variacao percentual`
- arquivos diretamente impactados nesta entrega:
  - [financeiro/views.py](C:\Users\lucia\OneDrive\Área de Trabalho\Casa_Espirita\financeiro\views.py)
  - [financeiro/templates/financeiro/evolucao_categorias.html](C:\Users\lucia\OneDrive\Área de Trabalho\Casa_Espirita\financeiro\templates\financeiro\evolucao_categorias.html)
  - [docs/STATE.md](C:\Users\lucia\OneDrive\Área de Trabalho\Casa_Espirita\docs\STATE.md)
  - [docs/CODEX_RESULTADO.md](C:\Users\lucia\OneDrive\Área de Trabalho\Casa_Espirita\docs\CODEX_RESULTADO.md)
  - [docs/ROADMAP_FINANCEIRO.md](C:\Users\lucia\OneDrive\Área de Trabalho\Casa_Espirita\docs\ROADMAP_FINANCEIRO.md)
- a proxima microetapa logica deixa de ser `Comparacao entre periodos` e passa a ser:
  - validacao visual/manual curta desse modo no navegador
  - depois disso, decidir entre refinamento da comparacao ou evolucao futura da tela para exportacao/tabela comparativa

## Evolucao por categorias fechada no working tree, pronta para commit

- o bloco aberto da tela `Evolucao por categorias` foi consolidado sem abrir nova frente
- o diff funcional ficou fechado apenas em:
  - [financeiro/views.py](C:\Users\lucia\OneDrive\Área de Trabalho\Casa_Espirita\financeiro\views.py)
  - [financeiro/templates/financeiro/evolucao_categorias.html](C:\Users\lucia\OneDrive\Área de Trabalho\Casa_Espirita\financeiro\templates\financeiro\evolucao_categorias.html)
- o fechamento atual consolidou como estado real da tela:
  - seletor visual limpo, em linha unica, com sinal `+`/`-` antes do nome e sem subtitulo poluente
  - ordenacao visivel crescente, `case-insensitive` e `accent-insensitive`, inclusive apos troca de escopo e busca
  - escopo separado entre `Categorias` e `Subcategorias`
  - leitura `Consolidado` / `Separado`
  - granularidade em `Dias`, `Meses`, `Trimestres` e `Anos`
  - grafico com leitura em valor absoluto, inclusive para despesas
  - eixo Y com escala arredondada e sem `R$`
  - rotulos curtos de valor no grafico e tooltip com moeda completa
  - impressao restrita a area do relatorio, sem shell/menu/formulario bruto
  - tabela de apoio recolhida por padrao e fora do impresso quando continuar recolhida
- criterio de fechamento desta microetapa:
  - nao houve abertura de `Comparacao entre periodos`
  - nao houve mistura com outras telas do `financeiro`
  - alteracao colateral na `lancamento_list` foi retirada do diff para manter o commit estritamente no escopo da tela
- validacoes tecnicas executadas no fechamento:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
- validacao visual/manual reaproveitada e mantida como evidencia desta frente em `tmp/`, com destaque para:
  - `tmp/validacao_evolucao_categorias_escala_ordenacao.png`
  - `tmp/validacao_ordenacao_categorias_aberta.png`
  - `tmp/validacao_ordenacao_subcategorias_busca.png`
  - `tmp/validacao_visual_categorias_prefixo.png`
  - `tmp/validacao_visual_subcategorias_prefixo.png`
- proxima frente logica continua sendo:
  - `Comparacao entre periodos` na propria tela `Evolucao por categorias`, mas apenas depois deste fechamento ser commitado

## Evolucao por categorias com escala limpa e ordenacao visivel validada

- a microetapa corretiva curta da `Evolucao por categorias` ficou concentrada em tres ajustes aprovados:
  - eixo Y com escala arredondada e legivel
  - remocao de `R$` da visualizacao do grafico
  - confirmacao da ordenacao visivel crescente de categorias no seletor
- causa real encontrada para a falha de ordenacao:
  - no escopo `Subcategorias`, a montagem backend ainda priorizava `categoria_pai` antes do nome exibido
  - alem disso, o DOM final do seletor nao era reordenado no cliente apos carregar, trocar escopo ou aplicar busca
- correcao final aplicada:
  - `Subcategorias` passaram a ser montadas com prioridade alfabetica pelo nome visivel
  - o JS do seletor agora reordena a lista final com `Intl.Collator('pt-BR', sensitivity: 'base')`, garantindo leitura crescente, `case-insensitive` e `accent-insensitive`
  - a mesma regra continua valendo depois de trocar escopo e depois de usar a busca
- regra visual consolidada nesta rodada:
  - o eixo Y deixou de usar valores crus/quebrados e passou a usar ticks bonitos, como `0`, `500 mil`, `1 mi`, `1,5 mi`, `2 mi`
  - os rotulos desenhados sobre o grafico deixaram de mostrar `R$`, preservando apenas o valor compacto
  - o tooltip continua sendo a referencia de valor monetario completo
- a ordenacao visivel das categorias foi revalidada no navegador real com criterio:
  - crescente
  - `case-insensitive`
  - `accent-insensitive`
- evidencias visuais geradas em `tmp/` nesta rodada:
  - `tmp/validacao_evolucao_categorias_escala_ordenacao.png`
  - `tmp/validacao_evolucao_categorias_ordenacao_aberta.png`
  - `tmp/validacao_ordenacao_categorias_aberta.png`
  - `tmp/validacao_ordenacao_subcategorias_busca.png`
- status atual da microetapa:
  - esta rodada especifica ficou visualmente validada
  - o working tree continua aberto e sem commit, conforme diretriz do usuario

## Evolucao por categorias ainda bloqueada antes do commit

- o retorno do uso real foi tratado como verdade operacional:
  - apenas o recolhimento automatico do filtro ficou efetivamente aprovado
  - os demais pontos da tela nao podem ser considerados resolvidos sem validacao visual/manual real no navegador
- nova rodada de correcao de codigo aplicada nesta microetapa:
  - remocao do texto auxiliar `Sem selecao explicita, o relatorio considera todas as contas.`
  - endurecimento da ordenacao textual para ficar `case-insensitive` e `accent-insensitive`
  - ajuste da ordenacao das categorias para leitura alfabetica real, sem deixar o agrupamento por `tipo` dominar a UX da lista
  - simplificacao dos rotulos curtos do grafico para eliminar o caso visual de aparecer apenas `R`
  - aumento da largura/utilidade do grafico e do espaco inferior do eixo para favorecer a exibicao dos labels temporais
  - reforco da estrutura de impressao para isolar a area documental e nao forcar impressao da tabela recolhida
- BLOQUEIO ABERTO da microetapa atual:
  - a tela ainda nao pode ser commitada enquanto nao houver validacao visual/manual real do navegador cobrindo:
    - ordenacao visivel de categorias, favorecidos e listas equivalentes
    - impressao limitada a area do relatorio
    - tabela recolhida fora do impresso
    - ausencia real de texto auxiliar indevido
    - rotulos de dados legiveis
    - eixo temporal visivel e legivel
- validacoes tecnicas executadas nesta rodada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado principal OK
  - smoke complementar OK para estrutura/HTML renderizado
- observacao de governanca:
  - enquanto a validacao visual/manual real do navegador nao confirmar todos os pontos, a microetapa deve permanecer aberta e sem commit

## Evolucao por categorias com ordenacao real e impressao isolada

- a microetapa corretiva da `Evolucao por categorias` ganhou mais uma rodada antes do commit para fechar os bloqueios que ainda apareciam no uso real
- regra nova aplicada na ordenacao dos seletores e listas relacionadas:
  - a ordenacao passou a ser `case-insensitive`
  - a ordenacao passou a ser `accent-insensitive`
  - isso foi aplicado nas listas da propria `Evolucao por categorias` e tambem nos seletores equivalentes mais proximos do fluxo financeiro, como filtros de `contas`, `favorecidos` e `categorias` da `lancamento_list`
- regra nova aplicada na impressao:
  - o botao `Imprimir relatorio` passou a imprimir apenas a area documental do relatorio
  - shell, menu, cabecalho operacional da pagina e formulario bruto de filtros deixam de sair no impresso
  - o impresso passa a usar um bloco proprio com resumo humano dos filtros aplicados
  - a `tabela mensal` nao sai na impressao quando estiver recolhida
  - a impressao deixou de forcar a abertura da tabela antes de chamar `window.print()`
- validacoes executadas nesta rodada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado original da tela OK
  - smoke complementar com rollback OK, confirmando:
    - ordenacao acento-insensivel de `contas`, `favorecidos` e `categorias`
    - ausencia de texto auxiliar indevido no escopo `Categorias`
    - isolamento estrutural da area de impressao
    - regra para nao imprimir a tabela recolhida

## Evolucao por categorias refinada antes do commit

- os quatro bloqueios imediatos da tela foram corrigidos antes do commit:
  - o painel de filtros volta recolhido por padrao depois de `Atualizar grafico`
  - textos auxiliares desnecessarios sairam da interface principal da selecao
  - os rotulos de dados do grafico deixaram de quebrar em apenas `R`
  - o eixo temporal voltou a renderizar labels reais conforme a granularidade
- regra aplicada ao filtro:
  - o usuario ainda pode reabrir manualmente o painel
  - os filtros aplicados continuam preservados no formulario, mas a tela nao volta expandida so porque ha filtros ativos
- regra aplicada aos rotulos do grafico:
  - os valores agora usam formato curto e inteiro o bastante para caber no SVG, como `R$ 950`, `1,25 mil` ou `2 mi`
  - o tooltip continua preservando o valor completo
- regra aplicada ao eixo temporal:
  - a renderizacao passou a controlar quais labels aparecem no eixo X quando houver muitos buckets
  - isso evita eixo vazio, indices tecnicos e sobrecarga de texto
- validacoes executadas nesta rodada corretiva:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado cobrindo:
    - atualizacao do grafico
    - filtro recolhido por padrao apos atualizar
    - rotulos de dados visiveis e integros
    - labels temporais visiveis em `Dias`, `Meses`, `Trimestres` e `Anos`

- a tela recebeu uma segunda rodada de refinamento antes do commit, focada em corrigir a usabilidade real e a leitura do grafico
- o seletor de `Escopo` agora troca imediatamente entre `Categorias` e `Subcategorias`, sem depender de `Atualizar grafico` para atualizar a lista visivel, a busca e os itens disponiveis
- em `Categorias`, a exibicao principal ficou limpa, mostrando apenas o nome da categoria, sem complemento como `Categoria pai`
- o botao `Atualizar grafico` continua sendo a acao que atualiza de fato o relatorio, e agora trabalha junto com os novos controles para recalcular:
  - grafico
  - tabela de apoio
  - KPIs do periodo
- a tela passou a suportar `granularidade temporal` configuravel:
  - `Dias`
  - `Meses`
  - `Trimestres`
  - `Anos`
- regra consolidada da granularidade:
  - `Dias`: rotulo `dd/mm`
  - `Meses`: rotulo `mm/aa`
  - `Trimestres`: rotulo `1o tri/25`, `2o tri/25` etc.
  - `Anos`: rotulo `YYYY`
- o grafico agora aceita tambem a opcao `Mostrar valores no grafico`, desligada por padrao
- a tabela mensal continua recolhida por padrao, mas o toggle passou a ficar mais claro com texto explicito de mostrar/ocultar
- o titulo do bloco principal passou a refletir a granularidade ativa, evitando a leitura fixa de `grafico mensal`
- validacoes executadas nesta rodada:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado cobrindo:
    - troca estrutural entre `Categorias` e `Subcategorias`
    - `Atualizar grafico` com relatorio recalculado
    - granularidade em `Dias`, `Meses`, `Trimestres` e `Anos`
    - periodo menor que 30 dias
    - eixo temporal coerente com a granularidade
    - tabela mensal recolhida com toggle visivel
    - opcao de `Mostrar valores no grafico`

- a tela `Evolucao por categorias` foi evoluida para uma leitura mais limpa e operacional antes do fechamento do commit
- o filtro agora separa explicitamente o escopo em:
  - `Categorias`
  - `Subcategorias`
- regra consolidada do escopo:
  - em `Categorias`, o seletor lista apenas categorias pai e cada escolha agrega automaticamente suas subcategorias lancaveis
  - em `Subcategorias`, o seletor lista apenas subcategorias individuais, com indicacao clara da categoria pai
- a tela ganhou busca dinamica no seletor multiplo, preservando selecao multipla e limpando a experiencia quando houver muitos itens
- a forma de leitura do grafico passou a ser controlada por:
  - `Consolidado`
  - `Separado`
- regra consolidada da leitura:
  - em `Categorias`, `Consolidado` soma as categorias selecionadas em uma unica serie e `Separado` mostra uma serie por categoria
  - em `Subcategorias`, `Consolidado` soma as subcategorias selecionadas em uma unica serie e `Separado` mostra uma serie por subcategoria
- o eixo temporal do grafico passou a usar rotulo mensal em `mm/aa`
- no modo `Comparativo entrada x saida`, as series deixaram de ficar genericas e passaram a preservar os nomes reais das categorias/subcategorias escolhidas
- a tabela mensal de apoio passou a ficar recolhida por padrao, com toggle para expandir/recolher, preservando o protagonismo do grafico
- a tela ganhou a acao `Imprimir relatorio`, com CSS de impressao para emitir a propria visao da pagina com cabecalho, filtros aplicados em linguagem humana, grafico e tabela mensal
- validacoes executadas nesta evolucao:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado cobrindo:
    - `escopo categorias`
    - `escopo subcategorias`
    - `modo consolidado`
    - `modo separado`
    - `comparativo entrada x saida` com nomes reais
    - `tabela mensal` recolhida por padrao
    - botao `Imprimir relatorio` renderizado

## Relatorio grafico de evolucao por categorias

- o `financeiro` passou a ter uma nova tela de relatorio propria: `Evolucao por categorias`
- a tela entrou na area de `Relatorios` do menu superior do modulo, sem criar navegacao paralela nem poluir a listagem principal
- filtros entregues nesta primeira versao:
  - `data inicial`
  - `data final`
  - selecao multipla de `categorias/subcategorias`
  - selecao opcional de `contas`
  - `modo do grafico`
- modos suportados:
  - `Evolucao de categorias selecionadas`: uma serie por categoria/subcategoria selecionada
  - `Comparativo entrada x saida`: consolidacao comparativa entre categorias de receita e despesa no mesmo eixo temporal
- regra consolidada de agrupamento:
  - consolidacao mensal por `data_pagamento`, com fallback para `data_competencia`
  - quando o usuario seleciona `Categoria` agrupadora, a serie passa a agregar suas `Subcategorias` lancaveis
  - para evitar dupla contagem, a tela bloqueia a combinacao de categoria pai com sua propria subcategoria no mesmo grafico
- a visualizacao entregue combina:
  - grafico SVG server-side, sem depender de biblioteca JS externa
  - tabela mensal de apoio logo abaixo
  - KPIs do periodo com `receitas`, `despesas`, `quitado`, `em aberto`, `saldo liquido` e `quantidade de lancamentos`
- regra financeira adotada no grafico/tabela:
  - `receitas` entram positivas
  - `despesas` entram negativas
  - o `saldo liquido` do periodo segue a natureza real dos lancamentos considerados
- validacoes executadas nesta microetapa:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com usuario real confirmando:
    - abertura da tela
    - modo `categorias`
    - modo `comparativo`
    - renderizacao do grafico e da tabela mensal com dados reais

## Trava de seguranca nas importacoes do financeiro

- a central de importacoes do `financeiro` passou a bloquear novas importacoes quando o dominio de destino ja estiver preenchido, evitando mistura de dados, duplicidade e sobreposicao de base
- a trava foi aplicada antes da validacao estrutural/conteudo da planilha, preservando o comportamento `all-or-nothing` e evitando processamento inutil quando a base ja esta ocupada
- dominios cobertos nesta etapa:
  - `contas`
  - `favorecidos`
  - `categorias/subcategorias`
  - `centros de custo`
  - `lancamentos`
- mensagens de bloqueio agora indicam explicitamente qual dominio barrou a operacao, por exemplo:
  - `Ja existem registros em Lancamentos. Limpe ou redefina a base antes de nova importacao.`
  - `Ja existem registros em Categorias/Subcategorias. Importe apenas em base vazia desse dominio.`
- os fluxos de reset/limpeza ja existentes permanecem como caminho correto para preparar nova importacao quando a base do dominio nao estiver vazia
- validacoes executadas nesta microetapa:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado transacional com rollback:
    - dominio vazio validado em `lancamentos`, esvaziado apenas dentro da transacao de teste
    - dominio preenchido validado em `contas`, com bloqueio e mensagem clara

## Prestacao de Contas com reconciliacao explicita do saldo consolidado

- a `Prestacao de Contas` passou a explicitar no proprio fechamento a reconciliacao do saldo quando houver transferencias entre as contas selecionadas no relatorio e outras contas da instituicao
- regra consolidada:
  - essas movimentacoes nao viram `receita`
  - essas movimentacoes nao viram `despesa`
  - mas passam a interferir explicitamente no fechamento do `Saldo final consolidado`
- formula agora exposta no relatorio:
  - `Saldo final consolidado = saldo inicial consolidado + receitas do periodo - despesas do periodo + entradas de outras contas da instituicao - saidas para outras contas da instituicao`
- a regra cobre os dois sentidos:
  - saida de conta selecionada para conta nao selecionada
  - entrada de conta nao selecionada para conta selecionada
- a apresentacao da `Prestacao de Contas` passou a destacar os blocos de reconciliacao:
  - `Saldo inicial consolidado`
  - `Receitas do periodo`
  - `Despesas do periodo`
  - `Entradas de outras contas da instituicao`
  - `Saidas para outras contas da instituicao`
  - `Saldo final consolidado`
- validacoes executadas nesta microetapa:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `git diff --check` OK
  - smoke autenticado com rollback confirmando fechamento correto do saldo em transferencia de saida para conta externa e transferencia de entrada vinda de conta externa

## Simplificacao final das acoes documentais da lancamento_list

- a `lancamento_list` deixou de expor acoes documentais redundantes para recibo e termo anual
- a interface passa a mostrar apenas:
  - `Recibos em lote`
  - `Termo anual de quitacao`
- `Recibos em lote` agora usa os lancamentos selecionados e agrupa automaticamente por favorecido:
  - se houver um unico favorecido, sai um unico recibo
  - se houver varios favorecidos, o documento segue continuo, com quebra entre os grupos
- a consolidacao por descricao continua valendo dentro de cada favorecido, sem reintroduzir protagonismo de categoria
- `Termo anual de quitacao` continua usando o resultado filtrado atual da `lancamento_list`, mas passou a assumir sozinho os dois cenarios:
  - um unico favorecido no filtro gera um unico termo
  - varios favorecidos no filtro geram um termo por favorecido no mesmo documento continuo
- a triagem documental automatica do termo foi preservada: considerar apenas `receitas quitadas`, ignorando `despesas`, `transferencias`, itens em aberto e registros incompativeis
- a rota plural antiga do termo foi mantida apenas como compatibilidade tecnica e redireciona para a acao unificada
- na `Prestacao de Contas`, a leitura operacional ficou com linguagem mais humana:
  - `Entradas de outras contas da instituicao`
  - `Saidas para outras contas da instituicao`
- no `Termo anual de quitacao`, o bloco final passou a usar o mesmo estilo manuscrito ja consolidado no recibo oficial, reaproveitando a mesma linguagem visual da assinatura institucional

## Termo anual de quitacao: assinatura estabilizada e emissao em massa

- o bloco documental do termo anual foi evoluido em duas frentes: estabilizacao real da assinatura e separacao entre emissao simples e emissao em massa por favorecido
- a assinatura do termo anual foi reforcada para aparecer de forma estavel no documento final:
  - o fechamento continua com local/data, linha de assinatura, nome e cargo
  - a busca institucional deixa de depender apenas de assinatura marcada como padrao e passa a usar a melhor assinatura ativa disponivel
  - o template passou a exibir tambem o `assinatura_texto` quando houver, preservando o padrao institucional do fechamento
- a `lancamento_list` passou a concentrar a emissao documental do termo em uma unica acao visivel: `Termo anual de quitacao`
- essa acao usa o resultado filtrado atual da listagem, agrupa por favorecido e gera documento continuo com quebra de pagina entre favorecidos quando houver mais de um grupo
- regra documental automatica consolidada para ambos os fluxos do termo anual:
  - considerar apenas `receitas`
  - considerar apenas `quitados`
  - ignorar automaticamente `despesas`, `transferencias`, `receitas em aberto` e demais itens incompativeis, incluindo registros com rateio
- quando o filtro atual nao produzir nenhum lancamento compativel apos essa triagem interna, o sistema exibe mensagem clara: `Nenhum lancamento compativel com termo anual de quitacao foi encontrado no filtro atual.`
- validacoes executadas nesta microetapa: `py manage.py check` OK, `py -m compileall financeiro` OK, `git diff --check` OK e smoke autenticado com rollback confirmando termo anual unificado, filtro interno apenas de receitas quitadas e mensagem de ausencia de itens compativeis

## Termo anual de quitacao com identidade documental propria

- o `Termo anual de quitacao` deixou de usar bloco superior com cara de filtro interno e passou a ter cabecalho textual simples, mais proximo de uma declaracao anual
- sairam do topo a `Quantidade de lancamentos considerados` e o visual em chips/badges/pills
- o topo agora prioriza:
  - `TERMO ANUAL DE QUITACAO`
  - subtitulo institucional com o ano de referencia
  - identificacao textual simples de `Favorecido`
- quando houver filtro de categoria ativo, ele aparece apenas como linha textual discreta de identificacao, sem virar chip de filtro
- o texto introdutorio foi humanizado para a leitura de termo anual: `Declaramos, para os devidos fins, que os valores relacionados abaixo foram recebidos e devidamente quitados em nome do favorecido acima.`
- a tabela documental permanece focada em `Data`, `Descricao`, `Documento` e `Valor`
- o fechamento preserva `Total do favorecido`, `Valor por extenso`, local/data e assinatura institucional
- validacoes executadas nesta microetapa: `py manage.py check` OK, `py -m compileall financeiro` OK, `git diff --check` OK e smoke autenticado com rollback confirmando renderizacao do termo anual

## Termo anual de quitacao com fechamento documental final

- ajuste final aplicado ao `Termo anual de quitacao`: o ano passou a ficar concentrado no subtitulo `Referente ao ano de ...`
- o bloco de identificacao do termo ficou reduzido a `Favorecido`, sem repetir o ano
- o texto introdutorio tambem deixou de repetir o ano, mantendo a leitura mais natural: `Declaramos, para os devidos fins, que os valores relacionados abaixo foram recebidos e devidamente quitados em nome do favorecido acima.`
- a assinatura institucional deixou de depender apenas da existencia de assinatura marcada como padrao; o documento agora usa a melhor assinatura ativa disponivel e aplica fallback nominal/cargo para o bloco final nao desaparecer
- o fechamento documental do termo permanece com local/data, linha de assinatura, nome, cargo, total e valor por extenso
- validacoes executadas nesta microetapa: `py manage.py check` OK, `py -m compileall financeiro` OK, `git diff --check` OK e smoke autenticado com rollback confirmando assinatura renderizada e reducao da repeticao do ano

## Prestacao de Contas com cabecalho limpo e leitura operacional de universo de contas

- a `Prestacao de Contas` teve o cabecalho simplificado para reforcar a leitura documental: o topo passa a mostrar apenas `Periodo`, `Emitido em`, `Saldo inicial consolidado`, `Receitas do periodo`, `Despesas do periodo` e `Saldo final consolidado`
- sairam do topo os elementos redundantes ou tecnicos demais, incluindo a competicao textual entre `Prestacao Financeira` e `Prestacao de Contas`, textos introdutorios longos, `Contas incluidas` no cabecalho e a duplicidade entre `Saldo final` e `Saldo final consolidado`
- a selecao de contas continua existindo no painel de filtros, agora com rotulo mais direto de `Contas do relatorio`
- a leitura contabil/operacional foi formalizada no proprio relatorio: o saldo consolidado considera apenas o universo de contas selecionadas naquele filtro
- regra consolidada: transferencias entre contas do universo selecionado e contas fora dele, como integralizacao ou outras contas nao operacionais, nao viram receita nem despesa; elas apenas alteram o saldo consolidado das contas exibidas
- quando houver movimentacao entre os dois universos, o relatorio passa a mostrar isso em bloco proprio de leitura operacional, fora do topo principal, com total de `Entradas de outras contas da instituicao` e `Saidas para outras contas da instituicao`
- a logica central ja aprovada foi preservada: transferencias continuam neutras para os totais de receitas e despesas
- validacoes executadas nesta microetapa: `py manage.py check` OK, `py -m compileall financeiro` OK, `git diff --check` OK e smoke autenticado com rollback confirmando renderizacao da `Prestacao de Contas` com cabecalho limpo

## Fluxo documental centralizado na listagem de lancamentos

- a direcao anterior de `Relatorio anual por favorecido` como tela principal foi substituida por acoes documentais concentradas na `lancamento_list`
- a rota, view, template e acessos visiveis do relatorio anual por favorecido foram removidos das superficies principais do sistema
- a interface final da `lancamento_list` passou a expor apenas a acao `Recibos em lote`
- essa acao continua baseada nos lancamentos selecionados da listagem, agrupa automaticamente por favorecido e reaproveita fielmente o recibo oficial ja existente, incluindo layout, cabecalho, texto explicativo, valor por extenso, mensagem final e bloco de assinatura institucional
- nova regra documental consolidada para os recibos em lote: categoria deixou de ser elemento relevante de leitura do favorecido, nao aparece no topo/documento e nao bloqueia mais a emissao quando houver categorias diferentes no mesmo grupo
- nova regra documental consolidada para os recibos em lote: quando houver multiplas linhas com a mesma descricao dentro do mesmo favorecido, inclusive em casos de rateio, o documento consolida essas linhas em um unico item documental com soma dos valores
- quando a consolidacao por descricao reunir documentos ou datas diferentes, o recibo passa a sinalizar isso de forma compacta (`Doc. diversos` e `Datas diversas`) sem poluir a peca documental
- os recibos em lote passaram a usar fallback institucional/fixo do recibo oficial, sem depender de mensagem especifica por categoria para viabilizar a emissao
- foi criada a acao `Termo anual de quitacao`, baseada no resultado filtrado atual da `lancamento_list`, agrupando por favorecido e gerando documento continuo com quebra por favorecido
- regra do termo anual: exige periodo filtrado com data inicial e final dentro do mesmo ano, lancamentos de receita, quitados, com favorecido e sem rateio
- os recibos por favorecido agora seguem a mesma peca documental do recibo ja consolidado, apenas repetida por favorecido com quebra de pagina; o termo anual continua em template proprio
- correcao de integridade aplicada aos recibos em lote: a consolidacao passou a considerar apenas descricoes exatamente iguais, preservando a descricao original e somando somente os lancamentos realmente selecionados naquele grupo
- quando a consolidacao do recibo juntar datas diferentes, o item mostra `Datas diversas`; quando juntar documentos diferentes, mostra `Doc. diversos`; descricoes diferentes continuam em linhas separadas
- a renderizacao do recibo em lote deixou de carregar `status` como informacao documental secundaria; o foco do corpo ficou em `data`, `descricao`, `documento` e `valor`, alinhado ao uso real do usuario
- o `Termo anual de quitacao` foi humanizado: subtitulo documental mais claro, bloco de identificacao simplificado (`Favorecido`), texto introdutorio institucional mais amigavel e tabela final reduzida a `Data`, `Descricao`, `Documento` e `Valor`
- ainda nao foram implementados PDF, anexos, assinatura final juridica, contratos, parcelas, recorrencia ou texto juridico pesado
- `Historico do favorecido` permanece como consulta operacional contextual, agora sem atalho para relatorio anual redundante

## Ajuste final dos quadros-resumo da listagem de lancamentos

- a `lancamento_list` deixou de usar os cards principais genericos `Pagina atual`, `Status na pagina` e `Selecionados` com valor unico como leitura financeira principal
- a tela passou a exibir um quadro-resumo financeiro do resultado filtrado completo, independente da paginacao, com `Receitas`, `Despesas`, `Transferencias de entrada`, `Transferencias de saida` e `Saldo liquido operacional`
- formula consolidada na listagem: `saldo liquido = receitas + transferencias_entrada - despesas - transferencias_saida`
- a paginacao passou a aparecer apenas como informacao auxiliar no formato `Mostrando X de Y lancamento(s)`
- o resumo dos itens selecionados passou a usar a mesma estrutura do resumo principal, permitindo leitura de selecao mista por receitas, despesas, transferencias de entrada, transferencias de saida e saldo liquido operacional
- `Quitado` e `Em aberto` foram mantidos como informacao secundaria do resultado, sem substituir o resumo financeiro principal
- validacoes executadas: smoke autenticado com rollback confirmando resumo sobre resultado filtrado completo maior que a pagina visivel, resumo dos selecionados com componentes mistos, `py manage.py check` OK, `py -m compileall financeiro` OK e `git diff --check` OK

## Correcao de totalizadores liquidos e paineis compactos recolhidos

- a `lancamento_list` passou a calcular os totalizadores agregados da propria tela com sinal operacional, deixando de tratar a soma como valor bruto absoluto
- regra aplicada nos totalizadores da listagem: receita soma positivo, despesa soma negativo, transferencia de saida soma negativo e transferencia de entrada soma positivo quando a conta filtrada for a conta destino
- a correcao foi aplicada ao total da pagina, aos totais da pagina por status (`Quitado` e `Em aberto`) e ao total dinamico dos selecionados
- os valores exibidos na coluna `Valor` continuam mostrando o valor nominal do documento; a diferenca e que os cards agregados agora representam saldo liquido operacional
- os paineis compactos de filtros/configuracao/opcoes secundarias passaram a vir recolhidos por padrao em `lancamento_list`, `pessoa_historico`, `resumo` e `prestacao_contas`, mantendo indicadores discretos quando ha filtros ou opcoes ativas
- validacoes executadas: smoke autenticado com rollback para `lancamento_list` com sinais mistos e selecao, `pessoa_historico`, `resumo` com/sem transferencias e `prestacao_contas` com/sem transferencias; `py manage.py check` OK; `py -m compileall financeiro` OK; `git diff --check` OK

## Refinamentos operacionais do historico e relatorios financeiros

- a coluna `Observacoes` da `lancamento_list` foi ajustada para ter largura util controlada, quebra de linha e quebra de palavras longas, evitando que observacoes extensas alarguem demais a tabela
- `Resumo` e `Prestacao de Contas` ganharam a opcao `Exibir transferencias`
- com `Exibir transferencias` desligado, os relatorios preservam o comportamento anterior: transferencias seguem fora da leitura principal
- com `Exibir transferencias` ligado, as transferencias quitadas do periodo aparecem em bloco proprio para conferencia operacional
- quando exibidas, as transferencias mostram total movimentado e totalizadores separados de entrada e saida
- regra funcional mantida: transferencias nao entram como receitas nem despesas e nao contaminam os totais principais dos relatorios
- o filtro de contas considera transferencias que envolvem as contas selecionadas, seja como conta origem ou conta destino
- filtros, configuracao de colunas e opcoes secundarias das telas tocadas neste bloco foram reorganizados em paineis compactos/recolhiveis, com indicacao discreta quando existem filtros ou opcoes ativas
- validacoes executadas: `py manage.py check` OK, `py -m compileall financeiro` OK, `git diff --check` sem erros bloqueadores e smoke autenticado com rollback confirmando `lancamento_list` com observacao longa, `Resumo` com/sem transferencias, `Prestacao de Contas` com/sem transferencias e historico por favorecido `200`

## Historico por favorecido no financeiro

- foi implementada uma pagina propria de historico por favorecido no modulo `financeiro`
- acesso natural criado a partir da listagem de `Favorecidos financeiros`, com acao `Historico`
- a tela usa a data operacional consolidada do financeiro: `data_pagamento` com fallback para `data_competencia`
- filtros disponiveis: data inicial, data final, tipo, status, conta e busca textual por descricao ou numero de documento
- totalizadores do resultado filtrado: total geral, receitas, despesas, quitado e em aberto
- tabela entregue com data, tipo, status, descricao, conta origem, conta destino, categoria, centro de custo, numero do documento e valor
- a implementacao reaproveita permissao existente de `financeiro.lancamentos.listar`, sem criar nova permissao nem alterar a matriz
- nao foram abertas nesta etapa as frentes de exportacao especifica do historico, contratos, anexos ou codigo automatico para contas/categorias
- validacoes executadas: `py manage.py check` OK, `py -m compileall financeiro` OK e smoke autenticado com rollback confirmando listagem de favorecidos, historico, totais, colunas e filtros

## Consolidacao do working tree do ciclo recente do financeiro

- working tree auditado na branch `feat/reinicio-financeiro`, separando alteracoes funcionais, documentais e artefatos locais antes do fechamento do ciclo
- bloco funcional consolidado no commit `8912cb7d500a6a2e3dc862a629445919a9ae04fd` (`fix(financeiro): consolida fluxo contextual e ajustes finais`)
- escopo funcional consolidado:
  - retorno contextual nas listagens e formularios principais do financeiro, preservando filtros, pagina, ordenacao, `por_pagina` e demais parametros por `return_to`
  - acoes `Salvar`, `+`, `Cancelar` e exclusoes mantendo retorno contextual seguro
  - listagens auxiliares com `Exportar` contextual, respeitando filtros locais, e importacoes permanecendo centralizadas no menu superior
  - central de importacoes sem botao redundante `Voltar para lancamentos`
  - extrato com checkbox `Exibir observacao`
  - mascara monetaria ajustada para remover zeros a esquerda antes da formatacao pt-BR
- `tmp/` foi tratado como artefato local de operacao/validacao e passou a ficar ignorado pelo Git; os arquivos locais nao foram apagados nem incluidos em commit
- validacoes executadas nesta consolidacao: `py manage.py check` OK, `py -m compileall financeiro` OK, smoke autenticado com rollback das telas afetadas OK e `git diff --check` OK
- pendencias reais que permanecem abertas apos este fechamento: decisao de produto sobre eventual ampliacao de codigo automatico para `contas`/`categorias`

## Novo bloco operacional do financeiro (Lote 1 em execucao)

- foi registrado um novo pacote de trabalho por lotes para o uso real do financeiro, com 7 itens levantados e distribuicao em Lote 1, Lote 2 e Lote 3
- itens registrados: remover `Importar` da listagem de lancamentos, mascara monetaria inteligente, checkbox `Exibir observacao` no extrato, correcao de exclusao de favorecido, geracao automatica de codigo nos demais cadastros, cadastro rapido de favorecido na tela de lancamentos e recibo em lote por favorecido
- Lote 1 executado: `Importar` removido da `lancamento_list`, mantendo a importacao centralizada no menu superior
- Lote 1 executado: mascara monetaria pt-BR aplicada nos campos de valor do lancamento, com normalizacao para decimal no envio do formulario
- ajuste fino aplicado: a mascara monetaria agora remove zeros a esquerda antes de formatar, evitando casos como `0.001.000,00` ao digitar `100000`; exemplos `1`, `10`, `100`, `1000` e `100000` validados na consolidacao final
- Lote 1 executado: extrato ganhou checkbox `Exibir observacao` para controlar a coluna de observacoes
- Lote 1 executado: exclusao de favorecido bloqueia quando houver lancamentos vinculados e desvincula regras automaticas quando essa for a unica amarra restante

## Novo bloco operacional do financeiro (Lote 2 em execucao)

- Lote 2 executado: geracao automatica de codigo quando vazio para `Favorecidos` e `Centros de custo`, preservando o codigo manual quando informado
- Lote 2 executado: fluxo rapido de `Novo favorecido` no lancamento preserva os dados preenchidos e retorna com o favorecido recem-criado selecionado
- ajuste de UX: os botoes textuais foram substituidos por `+` ao lado de `Favorecido`, `Categoria` e `Centro de custo`, mantendo o mesmo comportamento de retorno com dados restaurados e item criado selecionado
- ajuste de UX complementar: os botoes `+` agora ficam fora do input, alinhados a direita do campo, sem sobreposicao

## Novo bloco operacional do financeiro (Lote 3 executado)

- foi adicionada acao de recibo em lote na listagem de lancamentos
- regra consolidada: recibo em lote so funciona quando todos os lancamentos selecionados forem do mesmo favorecido, do tipo receita e sem rateio
- o recibo em lote gera documento unico com lista de descricoes e valor total consolidado
- ajuste de estabilidade: template do recibo em lote passou a usar apenas variaveis `recibo_*` e o corpo do lote agora mostra data, descricao e valor por item
- ajuste de conteudo: no lote, o rotulo passa a ser `Lote`, a frase padrao passou para `Referente aos lancamentos listados abaixo.` e o valor nao deve repetir `Lote` quando nao houver identificador real

## Correcao do menu suspenso e centralizacao de importacoes no financeiro

- a migracao para topbar com menu suspenso ainda nao estava aprovada visualmente porque, no uso real, o dropdown do `Menu` abria atras do conteudo da pagina
- causa tecnica identificada: a barra superior do financeiro usa `backdrop-filter`, criando stacking context proprio; enquanto o painel do menu ficava como descendente absoluto dessa topbar, ele ainda podia ficar preso abaixo de cards/formularios do conteudo em render real
- correcao reforcada em `financeiro/templates/financeiro/base.html`:
  - `.financeiro-app-utility-bar` preserva camada/overflow explicitos
  - `.financeiro-menu-panel` passou a ser camada `position: fixed` com `z-index` global alto
  - o JavaScript do menu move o painel para `document.body` no carregamento e calcula a posicao pelo botao `Menu` ao abrir, evitando ficar preso ao stacking context da topbar
- a pagina central de `Importacoes` entrou no menu superior em `Movimentacao > Importacoes`, mantendo a ideia de central do modulo para importacao de lancamentos e cadastros auxiliares
- a regra de arquitetura fica mantida: importacoes ficam centralizadas na pagina de importacoes do financeiro; exportacoes permanecem locais nas listagens/telas especificas para respeitar filtros aplicados
- o botao `Voltar para lancamentos` foi removido da pagina central de importacoes, porque a navegacao principal agora fica no menu superior
- atalhos de listagem foram ajustados para `Exportar`, respeitando filtros ativos da tela, nas listagens principais de cadastros auxiliares:
  - contas
  - favorecidos
  - categorias
  - centros de custo
- limpeza de legado concluida: o HTML comentado da sidebar/drawer foi removido do `financeiro/base.html`, o CSS legado associado saiu do arquivo e nao resta JS morto do shell antigo

## Migracao controlada do shell do financeiro para topbar com menu suspenso

- a migracao recomendada na auditoria estrutural foi implementada no `financeiro/templates/financeiro/base.html`
- o shell ativo do `financeiro` passa a usar topbar unica com identidade do modulo, usuario/perfil, `Inicio do sistema`, `Admin tecnico` quando aplicavel e `Sair`
- a navegacao principal do modulo agora fica no botao `Menu`, com dropdown agrupado por:
  - `Visao geral`
  - `Movimentacao`
  - `Relatorios`
  - `Cadastros`
  - `Institucional`
- o dropdown reaproveita as permissoes ja existentes do modulo para exibir apenas links liberados ao usuario autenticado
- a sidebar persistente, o drawer mobile, o overlay e o botao de recolher/expandir foram desativados da renderizacao do shell ativo, eliminando a competicao visual entre camadas de navegacao
- o bloco antigo de sidebar/drawer foi removido do template base; nao resta HTML comentado nem CSS morto relacionado ao shell antigo
- a area principal do shell deixou de depender da coluna lateral e passou a usar a largura util disponivel em bloco unico
- validacao executada: `py manage.py check` OK, `py -m compileall financeiro` OK e smoke autenticado `200` para `lancamento_list`, `lancamento_form`, `conta_list`, `pessoa_list`, `categoria_list`, `centro_custo_list`, central de importacao/exportacao, extratos, resumo e prestacao de contas
- smoke estrutural confirmou presenca do novo menu suspenso e ausencia de controles renderizados da sidebar/drawer antigos na `lancamento_list`
- pendencia de polimento possivel, sem bloquear a arquitetura ativa: remover CSS/JS legado de sidebar/drawer que ficou inerte como transicao reversivel

## Auditoria estrutural da navegacao/menu do sistema

- foi executada auditoria estrutural da navegacao antes de qualquer implementacao de menu novo
- camadas atuais identificadas:
  - `configuracoes/templates/configuracoes/sistema_base.html`: shell autenticado geral com topbar global, contexto de usuario/perfil e acoes de inicio/admin/sair
  - `biblioteca/templates/biblioteca/base.html`: herda o shell geral e acrescenta navegacao local horizontal simples em `before_main`
  - `eventos/templates/eventos/base.html`: herda o shell geral e acrescenta navegacao local horizontal simples em `before_main`
  - `financeiro/templates/financeiro/base.html`: shell proprio do financeiro, separado do shell geral, com topbar desktop, topbar mobile, botao de recolher sidebar, drawer mobile, overlay, sidebar lateral persistente e grupos colapsaveis
  - `configuracoes/templates/configuracoes/_sistema_usuario_acoes.html`: include comum de usuario/perfil/inicio/admin/logout usado pelo shell geral e reaproveitado no shell financeiro
- achado principal: a sujeira percebida no uso real nao vem de multiplas herancas simultaneas na mesma pagina, e sim do acumulo de camadas dentro do shell do `financeiro`
- no `financeiro`, todas as telas autenticadas principais herdam `financeiro/base.html`; a auditoria atual nao encontrou overrides ativos de `financeiro_shell_header` fora do proprio `base.html`
- duplicacoes/sobreposicoes encontradas no financeiro:
  - topbar propria do financeiro + include de usuario/perfil/acoes do sistema
  - link `Inicio do sistema` + link `Inicio do modulo` + chip de contexto atual
  - botao de recolher/expandir sidebar no desktop
  - sidebar lateral persistente com grupos colapsaveis
  - topbar mobile separada + botao `Menu` + drawer/overlay reaproveitando a sidebar
  - headers locais das paginas com titulos e botoes de retorno/atalhos, reforcando a sensacao de varias camadas de navegacao
  - pagina `financeiro/home.html` ainda funciona como camada de atalhos do modulo, apesar da raiz `/financeiro/` ja redirecionar para a listagem principal
- paginas afetadas: todas as telas autenticadas do `financeiro` que herdam `financeiro/base.html`, com maior impacto percebido em telas operacionais largas como `lancamento_list`, `lancamento_form`, cadastros auxiliares, relatorios e central de importacao/exportacao
- padrao oficial recomendado para proxima implementacao: um unico shell/topbar do financeiro com navegacao principal em menu suspenso agrupado no topo, preservando contexto institucional/usuario e removendo a sidebar persistente como camada principal
- recomendacao arquitetural: preferir menu suspenso no topo; evitar sidebar recolhida por padrao como solucao principal, porque ela mantem o padrao de expandir/recolher que motivou a insatisfacao; usar solucao hibrida apenas se a sidebar/drawer permanecer como apoio responsivo ou transicional
- implementacao nao executada nesta microetapa; a proxima etapa deve ser a migracao controlada do menu do financeiro para topbar/dropdown unico, preservando permissoes, links, agrupamentos funcionais e acessibilidade

## Refinamento visual dos totalizadores e acoes em lote da `lancamento_list`

- a area de acoes em lote e totalizadores da `lancamento_list` recebeu acabamento visual local, sem alterar a logica funcional ja aprovada
- o select de `Novo status` foi ajustado para evitar aparencia de seta duplicada/quebrada, mantendo uma unica leitura visual do controle
- a faixa de totalizadores foi reorganizada em cards compactos para melhorar hierarquia entre `Pagina atual`, `Status na pagina` e `Selecionados`
- a formatacao monetaria usada pelos totalizadores e valores da listagem passou a usar padrao pt-BR com separador de milhar e duas casas decimais, por exemplo `1.234,50`
- o totalizador dinamico de selecionados preserva a atualizacao em JavaScript e agora usa a mesma hierarquia visual dos demais cards
- validacao executada: `py manage.py check` OK, `py -m compileall financeiro` OK e smoke de renderizacao da `lancamento_list` confirmando formatacao monetaria pt-BR, cards de totalizadores e ajuste visual do select de acoes em lote

## Ajuste dos totalizadores da `lancamento_list` e clone dos ultimos lancamentos

- correcao de direcao consolidada: a separacao `Quitado`/`Aberto` nao deve ficar apenas no painel de `Ultimos lancamentos do favorecido`; ela tambem passou a aparecer na `lancamento_list`, junto dos totalizadores principais da listagem
- a `lancamento_list` agora mostra, na area de totalizacao da pagina atual: quantidade exibida, soma total exibida, soma quitada e soma em aberto
- os totais `Quitado` e `Aberto` no painel de `Ultimos lancamentos do favorecido` foram preservados, porque a leitura ficou util no formulario de lancamento
- o clone aberto a partir dos ultimos lancamentos foi corrigido para funcionar com e sem `return_to`: o fallback de cancelamento/sucesso agora usa a `success_url` configurada quando existir e nao depende de `self.object` durante GET de `CreateView`
- o endpoint de ultimos lancamentos passa a propagar `return_to` para os links de clone quando houver contexto de retorno seguro
- validacao executada: `py manage.py check` OK, `py -m compileall financeiro` OK e smoke test transacional com rollback confirmando totalizadores da `lancamento_list`, clone sem `return_to`, clone com `return_to` e propagacao de `return_to` no painel de ultimos lancamentos

## Correcoes de transferencia, totais por status e extrato por pagamento

- foi corrigida a lacuna de mensagem funcional na regra de transferencia entre a mesma conta: o model segue bloqueando a operacao e agora a mensagem exibida ao usuario passa a ser clara, `A conta de destino precisa ser diferente da conta de origem.`
- a regra continua valendo para cadastro, edicao e importacao, porque a importacao comum valida os lancamentos com `full_clean()` antes de gravar
- na tela de cadastro de lancamento, o painel de `Ultimos lancamentos do favorecido` passou a mostrar totais separados de `Quitado` e `Aberto`, alem de exibir a coluna `Status` na tabela do historico
- esses totais do favorecido sao calculados no endpoint auxiliar de ultimos lancamentos e ignoram `Cancelado` como status operacional de soma principal
- o extrato passou a usar `data_pagamento` como referencia principal de filtro, classificacao e ordenacao, com fallback tecnico para `data_competencia` apenas em registros legados sem pagamento
- validacao executada: `py manage.py check` OK, `py -m compileall financeiro` OK e smoke test transacional com rollback confirmando bloqueio de transferencia mesma conta, totais por status e ordenacao do extrato por pagamento

## Ajuste do conjunto padrao da `lancamento_list`: coluna `Tipo`

- apos uso real da configuracao de colunas, ficou consolidado que `Tipo` precisa fazer parte do conjunto essencial da listagem principal de lancamentos
- o padrao revisado passa a ser: selecao quando acoes em lote estiverem permitidas, `Data pagamento`, `Tipo`, `Descricao`, `Valor` e `Acoes` quando houver permissoes de acao
- as colunas complementares continuam configuraveis: `Favorecido`, `Conta origem`, `Conta destino`, `Status`, `Categoria`, `Centro de custo`, `Data competencia`, `Documento` e `Observacoes`
- a alteracao foi cirurgica e preservou o painel de colunas, a ordenacao manual simples, a persistencia por sessao, os totalizadores, filtros, paginacao, acoes em lote e agrupamento visual de rateios

## Colunas configuraveis, ordem manual e totalizadores na `lancamento_list`

- a `lancamento_list` passou a oferecer configuracao de colunas complementares para reduzir o conflito de largura da tabela sem depender de recolher a sidebar
- conjunto padrao inicial adotado:
  - sempre visiveis: selecao quando acoes em lote estiverem permitidas, `Data pagamento`, `Tipo`, `Descricao`, `Valor` e `Acoes` quando houver permissoes de acao
  - configuraveis: `Favorecido`, `Conta origem`, `Conta destino`, `Status`, `Categoria`, `Centro de custo`, `Data competencia`, `Documento` e `Observacoes`
- a ordenacao manual das colunas configuraveis foi implementada por seletores numericos simples no painel `Configurar colunas da listagem`, evitando drag-and-drop nesta etapa para manter o fluxo confiavel
- a preferencia de colunas fica preservada na sessao do usuario autenticado; nao foi criada migration/modelo proprio para persistencia permanente por banco nesta microetapa
- foi adicionada acao para `Restaurar padrao`, retornando ao conjunto enxuto inicial
- a tabela agora tem totalizador da pagina atual exibida, com quantidade e soma dos valores visiveis
- quando ha permissao de acoes em lote, a selecao mostra dinamicamente quantidade selecionada e soma dos valores selecionados
- a implementacao manteve filtros, paginacao, acoes em lote, agrupamento visual de rateios e rolagem horizontal local da tabela
- validacao executada: `py manage.py check` OK, `py -m compileall financeiro` OK e smoke autenticado de `/financeiro/lancamentos/`, configuracao de colunas via querystring e restauracao do padrao com `200`

## Usabilidade da listagem de lancamentos: descricao, scroll superior e quantidade por pagina

- a `lancamento_list` recebeu ajuste de usabilidade focado em reduzir pressao horizontal e vertical sem redesenhar a tela inteira
- a coluna `Descricao` deixou de depender de seletores por posicao da tabela e passou a usar classe propria, com largura mais controlada, truncamento por reticencias e preservacao do texto completo via `title` ja existente nas linhas
- a tabela de lancamentos passou a ter uma barra de rolagem horizontal superior sincronizada com a rolagem inferior do wrapper local da tabela, mantendo o overflow restrito ao componente da tabela e sem transformar a pagina inteira em area de scroll horizontal
- a listagem passou a oferecer seletor de quantidade por pagina com opcoes `25`, `50`, `100` e `200`; a escolha entra por querystring `por_pagina` e tambem fica preservada na sessao quando o valor e valido
- a paginacao foi aplicada sobre a lista visual ja agrupada de lancamentos/rateios, evitando quebrar um grupo rateado entre paginas por paginar diretamente as linhas fisicas do queryset
- validacao executada: `py manage.py check` OK, `py -m compileall financeiro` OK e smoke renderizado de `/financeiro/lancamentos/`, `/financeiro/lancamentos/?por_pagina=25` e `/financeiro/lancamentos/?por_pagina=100&page=1&ordenacao=descricao` com `200`

## Ajuste fino da listagem de lancamentos: pagamento, contas e favorecido

- a correcao anterior de exibicao ficou incompleta: `data_pagamento` havia sido adicionada na tabela, mas filtros e exportacao ainda usavam `data_competencia` como referencia principal
- a listagem principal de lancamentos foi ajustada para tratar `data_pagamento` como data principal de leitura, filtro, ordenacao visual e exportacao; `data_competencia` permanece visivel como coluna complementar
- a coluna de conta voltou a explicitar os dois papeis quando existirem: `Conta origem` e `Conta destino`, preservando a leitura correta de transferencias sem misturar origem e destino
- o rotulo visivel `Pessoa` foi trocado para `Favorecido` no contexto financeiro, incluindo listagem, filtros, formularios de lancamento/rateio, historico do favorecido, cadastro auxiliar e planilhas de importacao/exportacao; os nomes internos de model/campos permanecem como `PessoaFinanceira`/`pessoa` para evitar renome estrutural desnecessario
- a tela de cadastro financeiro antes chamada de `Pessoas financeiras` passou a ser exibida como `Favorecidos financeiros`; a rota, permissoes e slugs internos `pessoas` permanecem inalterados
- validacao executada: `py manage.py check` OK, `py -m compileall financeiro` OK e smoke renderizado `200` para listagem/formulario de lancamentos, listagem/formulario de favorecidos e central de importacao/exportacao

## Correcoes pontuais de exibicao em lancamentos e recibo

- foram corrigidas tres inconsistencias objetivas observadas no uso real antes do fechamento da frente atual
- a data documental por extenso do recibo usava uma lista manual de meses em `financeiro/views.py`; o mes de marco estava registrado sem cedilha e passou a sair como `março`
- a listagem principal de lancamentos exibia apenas uma coluna generica `Data`, baseada em `data_competencia`; ela passou a exibir `Data competencia` e `Data pagamento` separadamente
- a mesma listagem exibia `Conta destino` como coluna independente, o que confundia a leitura de origem; a coluna principal de conta passa a mostrar apenas `conta` como origem do lancamento
- a excecao funcional de transferencia permanece preservada nos dados e nas regras: `conta_destino` continua existindo no model, formulario, importacao/exportacao e calculos de saldo, mas deixou de ser coluna principal da listagem de lancamentos nesta correcao de exibicao
- validacao executada:
  - `py manage.py check` OK
  - render autenticado de `lancamento_list` com `200`
  - render autenticado de recibo com `200` e mes `março`
  - render autenticado de `resumo`, `prestacao de contas`, `extratos` e `extrato por conta` com `200`

## Limpeza documental da tela de recibo

- a tela de recibo foi ajustada para reforcar a leitura de documento final, sem controles administrativos dentro da area documental
- a frase `Para fins de comprovacao documental` foi removida do bloco de assinatura do recibo
- os botoes `Imprimir` e `Voltar` sairam do cabecalho interno do recibo e passaram para uma faixa de acoes externa, no nivel da pagina
- a acao de impressao continua disponivel fora do documento, como apoio operacional ao uso do navegador
- a faixa externa usa `no-print`, preservando a impressao limpa apenas da peca documental
- a regra consolidada desta microetapa e que o corpo do recibo deve permanecer limpo, sem controles visuais de navegacao ou impressao dentro da area que representa o documento

## Diagnostico real e correcao definitiva do overflow horizontal no financeiro

- a correcao anterior da regressao visual nao atacou completamente a causa, porque aplicou `overflow-x: hidden` no shell principal do `financeiro`
- isso impedia a pagina de crescer horizontalmente, mas nao provava qual elemento ainda estava ultrapassando a largura util
- nesta microetapa, o diagnostico foi refeito em render real de `lancamento_list`, com HTML autenticado do Django e medicao via Chrome headless em viewport desktop com a sidebar expandida
- cadeia medida no render real:
  - shell principal
  - `main`
  - `container` interno
  - `header` da pagina
  - grid de filtros
  - barra de acoes em lote
  - wrapper da tabela
  - tabela
- resultado objetivo do diagnostico:
  - `shellBody`, `main`, `container`, `header`, `filtersGrid` e `bulkBar` ficaram dentro da largura util
  - o primeiro elemento realmente mais largo era a propria `table` de `lancamento_list`
  - o `tableWrap` ficou com largura util de aproximadamente `1033px` e `overflow-x: auto`
  - a `table` ficou com largura de aproximadamente `1375px`
  - mesmo sem `overflow-x: hidden` no shell, o `bodyWidth` permaneceu igual ao `viewport`, provando que o overflow ficou confinado no wrapper correto da tabela
- conclusao tecnica definitiva:
  - o shell principal nao deve esconder overflow horizontal para mascarar a pagina
  - a origem do excesso de largura esta na tabela da listagem
  - o comportamento correto e a tabela larga rolar dentro do wrapper local, sem empurrar nem cortar a pagina inteira
- ajuste final consolidado:
  - `overflow-x: hidden` foi removido de `financeiro-app-shell-body`, `financeiro-app-main` e do `container` interno da `section`
  - os wrappers locais das listagens continuam responsaveis pela rolagem horizontal (`overflow-x: auto`, `overflow-y: hidden`, `width/max-width: 100%`)
- validacao real desta microetapa:
  - captura desktop real de `lancamento_list` com sidebar expandida
  - `bodyWidth == viewport`
  - sem clipping do shell
  - rolagem horizontal localizada no wrapper da tabela
  - smoke test autenticado `200` para:
    - `lancamento_list`
    - `conta_list`
    - `pessoa_list`
    - `categoria_list`
    - `centro_custo_list`
    - `lancamento_importacao_exportacao`
- conclusao consolidada:
  - a regressao passa a ficar resolvida no nivel estrutural correto
  - o shell deixa de mascarar o problema
  - o overflow restante fica apenas no wrapper local da tabela, como esperado

## Correcao inicial do overflow horizontal com sidebar expandida no financeiro

- apos a normalizacao do shell autenticado do `financeiro`, surgiu regressao visual nas listagens com a sidebar expandida, especialmente em `lancamento_list`
- a causa tecnica consolidada ficou em duas camadas:
  - o shell principal ainda precisava reforcar contencao horizontal em `financeiro-app-shell-body`, `financeiro-app-main` e no `container` da `section`
  - os wrappers locais das tabelas em `lancamento_list`, `conta_list`, `pessoa_list`, `categoria_list` e `centro_custo_list` estavam com `overflow: visible`, permitindo que tabelas largas escapassem do card e empurrassem a pagina para a direita
- a regra estrutural consolidada passa a ser:
  - o shell principal do `financeiro` deve conter overflow horizontal no corpo principal
  - tabelas largas devem rolar no wrapper interno da tabela, nao na pagina inteira
- correcoes aplicadas:
  - `financeiro/templates/financeiro/base.html`:
    - `min-width: 0` e `overflow-x: hidden` no corpo principal do shell
    - `min-width: 0` e `overflow-x: hidden` no `container` interno da `section`
    - `table-wrapper` padronizado com `width: 100%`, `max-width: 100%`, `overflow-x: auto` e `overflow-y: hidden`
    - cabecalhos de pagina reforcados com `min-width: 0` e `max-width: 100%`
  - wrappers locais das listagens:
    - `financeiro-lancamento-table-wrap`
    - `financeiro-conta-table-wrap`
    - `financeiro-pessoa-table-wrap`
    - `financeiro-categoria-table-wrap`
    - `financeiro-centro-custo-table-wrap`
    - todos passaram para `overflow-x: auto` e `overflow-y: hidden`, com `width/max-width: 100%`
- validacao executada:
  - `py manage.py check` OK
  - smoke test autenticado com `Client` nas telas:
    - `lancamento_list`
    - `conta_list`
    - `pessoa_list`
    - `categoria_list`
    - `centro_custo_list`
    - `lancamento_importacao_exportacao`
  - todas responderam `200`
- conclusao consolidada:
  - a regressao de corte horizontal deixa de ser causada pelo shell autenticado expandido
  - a rolagem horizontal das tabelas passa a ficar contida no wrapper correto das listagens

## Carga real pequena validada no layout comum de lancamentos

- foi executada uma carga real pequena e controlada no fluxo comum do `financeiro`, usando a central de importacao do modulo e o contrato atual de planilha com ate `5` blocos de rateio na mesma linha
- antes da carga de lancamentos, o estado real da base ja nao estava totalmente vazio:
  - `1` conta (`Conta Teste`)
  - `1` pessoa (`Pessoa Teste`)
  - `1` centro de custo (`Centro Teste`)
  - `5` categorias/subcategorias
  - `0` lancamentos
- para viabilizar o lote pequeno com transferencia real, foi importada primeiro uma planilha auxiliar minima de `contas`, criando `Conta Destino 20260406_112727`
- depois disso, foi importado um lote real pequeno no layout comum com:
  - `1` lancamento simples de receita
  - `1` transferencia
  - `1` documento com rateio de `2` blocos
- arquivos operacionais usados nesta validacao:
  - `tmp/validacao_carga_real_pequena/contas_complementares_20260406_112727.xlsx`
  - `tmp/validacao_carga_real_pequena/lote_real_pequeno_20260406_112727.xlsx`
- resultado real apos a carga:
  - `2` contas
  - `1` pessoa
  - `1` centro de custo
  - `5` categorias/subcategorias
  - `4` lancamentos persistidos no banco
  - `1` grupo de rateio
  - `2` linhas rateadas
- integridade funcional confirmada na base resultante:
  - listagem de lancamentos `200`, exibindo os tres documentos do lote
  - extrato `200`, exibindo receita, transferencia e documento rateado
  - resumo `200`, exibindo agregacoes esperadas de `Doacoes`, `Material` e `Servico`
  - prestacao de contas `200`, com leitura consolidada coerente do mesmo lote
  - recibo `200` para o lancamento simples de receita
- conclusao consolidada:
  - o novo layout comum esta operacionalmente apto para uma carga maior
  - nao apareceu divergencia nova de contrato no lote real pequeno
  - o proximo passo deixa de ser validacao do contrato e passa a ser ampliacao controlada da carga real

## Auditoria transversal do shell autenticado e normalizacao do topo/lateral

- foi executada uma auditoria transversal das paginas autenticadas de `financeiro`, `configuracoes` e `biblioteca`
- o mapeamento tecnico confirmou dois shells autenticos legitimos no repositorio:
  - `financeiro/templates/financeiro/base.html`: shell completo do modulo financeiro, com barra superior contextual, contexto institucional/usuario e navegacao lateral persistente
  - `configuracoes/templates/configuracoes/sistema_base.html`: shell autenticado geral do sistema, com barra superior completa e espaco para navegacao local por modulo
- a divergencia real encontrada nao estava entre apps diferentes, e sim dentro do proprio `financeiro`
- origem tecnica da divergencia:
  - `10` templates do `financeiro` sobrescreviam o bloco `financeiro_shell_header`
  - esse override removia a topbar contextual completa e deixava apenas a casca minima com toggle/menu
  - com isso, paginas equivalentes do mesmo modulo exibiam comportamentos visuais diferentes no topo
- paginas auditadas e normalizadas no `financeiro`:
  - listagens: `lancamento_list`, `conta_list`, `pessoa_list`, `categoria_list`, `centro_custo_list`
  - formularios: `lancamento_form`, `conta_form`, `pessoa_form`, `categoria_form`, `centro_custo_form`
  - telas centrais/auxiliares confirmadas no shell completo sem ajuste estrutural novo: `lancamento_importacao_exportacao`, `resumo`, `prestacao_contas`, `auditoria_lancamento_list`, `configuracao_institucional_list`
- paginas autenticadas auditadas nos demais apps:
  - `configuracoes`: `siteconfig_detail`, `perfil_acesso_list`, `perfil_acesso_detail`, `usuario_perfil_list`, `usuario_perfil_form`, `inicio`
  - `biblioteca`: `autor_list`, `autor_form`, `livro_list`, `livro_form`, `venda_list`, `venda_form`, `emprestimo_list`, `emprestimo_form`
- padrao oficial consolidado:
  - no `financeiro`, o padrao principal das paginas autenticadas passa a ser o shell completo de `financeiro/base.html`, com barra superior contextual + contexto institucional/usuario + navegacao lateral persistente
  - em `configuracoes` e `biblioteca`, o padrao autenticado continua sendo `configuracoes/sistema_base.html`, com barra superior completa e navegacao local do modulo quando aplicavel
  - o modelo de topo minimo com apenas toggle/menu deixa de ser padrao principal e nao deve ser reutilizado sem excecao explicitamente justificada
- excecoes legitimas mantidas:
  - paginas de autenticacao (`login`, `password reset`) continuam fora desse shell autenticado
  - paginas de recibo/impressao continuam podendo isolar o shell por necessidade documental/print
- validacao tecnica desta microetapa:
  - `py manage.py check` OK
  - smoke test autenticado com `Client` em `financeiro`, `configuracoes` e `biblioteca`:
    - todas as telas auditadas responderam `200`
    - telas normalizadas do `financeiro` voltaram a renderizar `financeiro-topbar-brand`, contexto de usuario e `financeiro-sidebar`
    - telas de `configuracoes` e `biblioteca` permaneceram renderizando `ce-app-topbar` com contexto de usuario

## Layout comum de importacao/exportacao de lancamentos com ate 5 rateios na mesma linha

- a decisao consolidada mais recente substituiu o contrato intermediario por multiplas linhas e promoveu o modelo didatico como padrao principal do usuario:
  - `1 linha = 1 documento`
  - ate `5` blocos de rateio na mesma linha
  - `valor_total_documento = soma dos blocos preenchidos`
- a central de importacoes do `financeiro` continua sendo o ponto funcional de importacao de lancamentos
- a exportacao continua saindo da listagem especifica de lancamentos para respeitar filtros, mas agora usa o mesmo contrato comum de planilha da importacao
- layout consolidado da aba `Modelo`:
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
- regra funcional consolidada:
  - receita/despesa simples: apenas bloco `1` preenchido
  - receita/despesa com rateio: `2` a `5` blocos preenchidos, sem buracos entre eles
  - transferencia: continua sem suporte a rateio no fluxo comum e deve deixar todos os blocos em branco
- validacoes consolidadas do fluxo comum:
  - maximo de `5` blocos por documento
  - nao permitir buracos entre blocos
  - cada bloco usado exige subcategoria valida e valor positivo
  - categoria pai continua proibida
  - categoria precisa respeitar o tipo do lancamento
  - `valor_total_documento` precisa bater com a soma dos blocos preenchidos
  - importacao continua `all-or-nothing`
- compatibilidade preservada:
  - a importacao continua aceitando o layout simples legado de `13` colunas para nao quebrar arquivos antigos ja preparados
  - o layout intermediario por multiplas linhas deixa de ser o contrato principal do usuario
- exportacao consolidada:
  - a exportacao XLSX da listagem de lancamentos passa a gerar `Modelo` + `Instrucoes`, no mesmo contrato usado pela importacao
  - cada grupo rateado sai condensado em uma unica linha
  - se algum grupo visivel tiver mais de `5` linhas rateadas, a exportacao comum e bloqueada com mensagem clara e o caminho tecnico permanece como excecao
- validacao tecnica executada nesta microetapa:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - smoke test transacional com rollback:
    - roundtrip comum de exportacao/importacao com `1` lancamento simples e `1` documento rateado de `2` blocos: OK
    - compatibilidade do layout simples legado: OK
    - transferencia no novo layout com blocos em branco: OK
    - planilha invalida com buraco entre blocos: bloqueada com erro claro
    - planilha invalida com soma divergente: bloqueada com erro claro
    - exportacao comum de grupo com `6` linhas rateadas: bloqueada com mensagem clara
- conclusao consolidada:
  - o fluxo funcional comum do usuario agora cobre exportacao e importacao de lancamentos simples, transferencias simples e lancamentos rateados no modelo de `1 linha por documento`
  - a trilha tecnica separada de backup/restauracao continua existindo como apoio operacional para contingencia e para casos fora do limite do fluxo comum

## Reset final do financeiro sem reconstrucao

- a base do modulo `financeiro` foi zerada de forma intencional nesta microetapa para preparar uso/teste do zero, sem executar reconstrucao depois do reset
- antes da execucao real, o `dry-run` confirmou o escopo planejado de limpeza:
  - `26` lancamentos financeiros
  - `1` regra automatica de lancamento
  - `47` auditorias do financeiro
  - `5` contas financeiras
  - `2` pessoas financeiras
  - `11` categorias/subcategorias financeiras
  - `2` centros de custo
- o reset destrutivo real foi executado com:
  - `py manage.py reset_financeiro_controlado --executar --confirmar RESETAR_FINANCEIRO`
- o comportamento final confirmou a regra vigente do reset:
  - `AssinaturaInstitucional` foi preservada
  - `ConfiguracaoInstitucional` foi preservada
  - nao houve reconstrucao de contas, pessoas, centros de custo, categorias, lancamentos, regras ou rateios nesta etapa
- contagens finais validadas sem rollback:
  - `1` assinatura institucional preservada
  - `1` configuracao institucional preservada
  - `0` regras automaticas
  - `0` contas
  - `0` pessoas
  - `0` centros de custo
  - `0` categorias/subcategorias
  - `0` lancamentos simples
  - `0` grupos de rateio
  - `0` linhas rateadas
  - `0` lancamentos totais no modulo
- validacao tecnica complementar:
  - `py manage.py check` OK apos o reset final
- conclusao consolidada:
  - a base transacional do `financeiro` ficou intencionalmente vazia
  - o modulo ficou preparado para comecar/testar do zero a partir desta etapa

## Validacao operacional final do financeiro reconstruido

- foi executada a validacao operacional final do `financeiro` usando a base real reconstruida na microetapa anterior
- a validacao foi feita pela stack HTTP real do Django com `Client`, cobrindo rotas, renderizacao, permissao, downloads e fluxos mutaveis com rollback controlado para nao sujar a base apenas por smoke test
- resultado objetivo dos blocos principais:
  - listagem de lancamentos: OK
  - criacao de lancamento simples: OK
  - edicao de lancamento simples: OK
  - leitura/abertura da edicao coordenada de grupo rateado: OK
  - importacao/exportacao nos pontos existentes: OK
  - extrato: OK
  - resumo: OK
  - prestacao de contas: OK
  - recibo: OK
  - regras automaticas: OK
  - permissoes principais: OK
  - integridade visual minima das telas centrais: OK
- validacoes de permissao executadas nesta microetapa:
  - `Gestao administrativa` acessa a auditoria do financeiro com `200`
  - `Operador financeiro` recebe `403` na auditoria do financeiro
  - `Consulta/visualizacao` recebe `403` na central de importacao
  - `Consulta/visualizacao` continua acessando a exportacao da listagem de lancamentos com `200`
- validacoes funcionais executadas nesta microetapa:
  - listagem principal de lancamentos abriu com `200`
  - formulario de novo lancamento abriu com `200`
  - criacao de lancamento simples por `Operador financeiro` passou com `302`
  - edicao do mesmo lancamento passou com `302`
  - recibo do lancamento criado/alterado abriu com `200`
  - endpoint de sugestoes de regras respondeu `200` antes e depois da criacao com `salvar_como_regra_automatica`
  - tela de edicao coordenada do grupo rateado abriu com `200`
  - exportacao XLSX da listagem de lancamentos abriu com `200`
  - download da planilha modelo de lancamentos abriu com `200`
  - download da planilha-base auxiliar de `contas` abriu com `200`
  - extrato por conta abriu com `200`
  - resumo abriu com `200`
  - prestacao de contas abriu com `200`
- detalhe importante desta validacao:
  - a primeira tentativa de smoke tinha marcado falha na criacao do lancamento simples, mas isso foi apenas erro do proprio teste
  - a causa foi envio de `123,45` diretamente para `input type=\"number\"`, enquanto o formulario HTML trabalha com payload compativel de navegador (`123.45`)
  - ao repetir a validacao com payload coerente com o campo HTML, criacao e edicao passaram normalmente
  - tambem houve dois falsos negativos iniciais por URL de teste incorreta (`exportacao`, `modelos-cadastros` e rota do grupo rateado foram corrigidas para os caminhos reais do repositorio)
- integridade visual minima confirmada:
  - as telas centrais renderizaram sem erro com seus titulos principais esperados
  - nao apareceu regressao funcional de shell, listagem, formulario, relatorios ou recibo
  - na tela de `Importacoes do Financeiro`, a validacao textual final confirmou `200` e renderizacao correta; a unica diferenca era apenas o texto exato usado no teste, nao um bug visual do sistema
- conclusao consolidada:
  - nao apareceu bloqueio funcional novo
  - o `financeiro` reconstruido passou na validacao operacional final desta etapa
  - do ponto de vista tecnico e funcional, o modulo fica apto para fechamento de commit

## Execucao real completa de reset e reconstrucao do financeiro

- a operacao real completa de `backup/reset/reconstrucao` do `financeiro` foi finalmente executada sem rollback
- o pacote operacional usado nesta execucao real foi:
  - `tmp/operacao_reset_financeiro_20260406_081633/`
- a integridade do pacote foi confirmada antes do passo destrutivo, com presenca de:
  - `rateios_backup_definitivo.json`
  - `regras_backup_definitivo.json`
  - `01_contas_financeiras_importacao.xlsx`
  - `02_pessoas_financeiras_importacao.xlsx`
  - `03_centros_custo_importacao.xlsx`
  - `04_categorias_importacao.xlsx`
  - `05_lancamentos_simples_importacao.xlsx`
  - `manifesto_pre_reset.json`
- o reset destrutivo real foi executado com sucesso por:
  - `py manage.py reset_financeiro_controlado --executar --confirmar RESETAR_FINANCEIRO`
- o comportamento real do reset confirmou a regra final consolidada:
  - `AssinaturaInstitucional` foi preservada
  - `ConfiguracaoInstitucional` foi preservada
  - `RegraLancamentoFinanceiro` foi apagada junto com o restante do dominio transacional do `financeiro`
- a reconstrucao real foi executada na ordem operacional correta:
  - `5` contas reimportadas
  - `2` pessoas reimportadas
  - `2` centros de custo reimportados
  - `11` categorias/subcategorias reimportadas
  - `14` lancamentos simples reimportados
  - `1` regra automatica restaurada pelo comando tecnico
  - `6` grupos de rateio e `12` linhas rateadas restaurados pelo comando tecnico
- comandos tecnicos usados na operacao real:
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
  - `0` rateios sem `grupo_rateio`
  - `0` lancamentos simples usando categoria-pai
  - `0` lancamentos simples com tipo/categoria incompatíveis
  - `0` regras operacionais apontando para categoria-pai
- validacao tecnica complementar:
  - `py manage.py check` OK apos a reconstrucao real
- divergencia entre preflight e operacao real:
  - nenhuma divergencia funcional de dados ou de contagem
  - houve apenas um erro operacional inicial de quoting ao chamar os restores tecnicos pelo shell, corrigido na sequencia sem impacto nos dados
- conclusao consolidada:
  - a base local real do `financeiro` foi zerada e recomposta integralmente com sucesso
  - o modulo volta a ficar apto para a etapa final de validacao operacional local

## Ultimo bloqueio do reset real resolvido: assinaturas, configuracao institucional e regras automaticas

- o reset destrutivo real do `financeiro` ainda estava bloqueado mesmo depois da resolucao dos `rateios` e dos `5` lancamentos simples legados, porque o pacote operacional de reconstrucao ainda nao cobria integralmente tudo o que o comando de reset apagava
- o bloqueio objetivo remanescente estava em `3` itens do dominio:
  - `AssinaturaInstitucional`
  - `ConfiguracaoInstitucional`
  - `RegraLancamentoFinanceiro`
- o mapeamento final desta microetapa confirmou o papel de cada item:
  - `AssinaturaInstitucional`: apoio documental para recibos/relatorios, sem dependencia estrutural do reset dos cadastros auxiliares
  - `ConfiguracaoInstitucional`: configuracao institucional/documental do proprio modulo, tambem sem dependencia estrutural do reset transacional
  - `RegraLancamentoFinanceiro`: ajuda operacional de sugestao automatica, mas com dependencias diretas de `conta`, `pessoa`, `categoria`, `centro de custo` e, em transferencia, `conta_destino`
- decisao tecnica minima e segura adotada:
  - `AssinaturaInstitucional` passa a ser preservada fora do reset
  - `ConfiguracaoInstitucional` passa a ser preservada fora do reset
  - `RegraLancamentoFinanceiro` continua entrando no reset, mas agora ganhou trilha tecnica propria de `backup/restauracao` em `JSON`
- o motivo para nao preservar `RegraLancamentoFinanceiro` fora do reset ficou objetivo em validacao real:
  - ao testar essa alternativa, o reset passou a falhar com `ProtectedError`
  - isso acontece porque as regras automaticas referenciam cadastros que o reset precisa apagar
  - preservar as regras fora do reset exigiria preservar tambem esses cadastros, o que descaracterizaria o reset operacional do modulo
- implementacao tecnica consolidada:
  - `financeiro/management/commands/reset_financeiro_controlado.py` foi ajustado para:
    - preservar `AssinaturaInstitucional`
    - preservar `ConfiguracaoInstitucional`
    - continuar apagando `RegraLancamentoFinanceiro`
  - foi criado `financeiro/regras_backup.py` como helper tecnico para serializacao/restauracao das regras
  - foi criado `backup_regras_financeiro` para gerar `JSON` tecnico das regras
  - foi criado `restaurar_regras_financeiro` para reconstituir as regras com `dry-run` por padrao e confirmacao explicita na execucao real
- o formato tecnico adotado para regras ficou:
  - `formato`: `financeiro.regras.backup.v1`
  - referencias resolvidas por chave de negocio estavel, e nao por `pk`
  - conta por `nome`
  - pessoa por `codigo`
  - centro de custo por `codigo`
  - categoria por `tipo`, `nome` e `categoria_pai_nome`
- o pacote operacional mais recente passou a ficar incompleto sem `regras_backup_definitivo.json`; por isso, o caminho correto de reconstrucao integral agora passa a ser:
  - preservar `assinaturas`
  - preservar `configuracao institucional`
  - reimportar cadastros auxiliares
  - reimportar lancamentos simples
  - restaurar `rateios`
  - restaurar `regras automaticas`
- validacao executada nesta microetapa:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `py manage.py reset_financeiro_controlado` OK em `dry-run`, agora exibindo:
    - `regras automaticas` no escopo de exclusao
    - `assinaturas institucionais` no escopo preservado
    - `configuracoes institucionais` no escopo preservado
  - `py manage.py backup_regras_financeiro --saida tmp/operacao_reset_financeiro_20260406_081633/regras_backup_definitivo.json` OK
  - `py manage.py restaurar_regras_financeiro --arquivo tmp/operacao_reset_financeiro_20260406_081633/regras_backup_definitivo.json` OK em `dry-run`
  - validacao completa com rollback:
    - reset tecnico executado dentro de transacao de teste
    - `assinaturas` e `configuracoes institucionais` permaneceram apos o reset
    - `regras automaticas` foram apagadas pelo reset
    - reimportacao do pacote operacional + restore tecnico de `rateios` + restore tecnico de `regras` recompuseram integralmente o estado esperado
    - contagem final validada no rollback:
      - `1` assinatura institucional
      - `1` configuracao institucional
      - `1` regra automatica
      - `5` contas
      - `2` pessoas
      - `2` centros de custo
      - `11` categorias/subcategorias
      - `14` lancamentos simples
      - `12` lancamentos rateados
      - `6` grupos de rateio
- conclusao consolidada:
  - o ultimo bloqueio conhecido do reset real foi removido
  - o pacote operacional passa a cobrir integralmente tudo o que o reset apaga
  - o reset destrutivo real fica novamente liberado do ponto de vista tecnico, embora nao tenha sido executado nesta microetapa

## Saneamento dos 5 lancamentos simples legados e novo preflight

- a base atual tinha `5` lancamentos simples legados que ainda bloqueavam o reset real, mesmo depois da resolucao tecnica dos `rateios`
- os `5` bloqueadores identificados eram:
  - `pk=1` (`Desc Teste`) em `despesa`, usando `Cantina` como categoria pai
  - `pk=4` (`Desc Teste`) em `despesa`, usando `Cantina` como categoria pai
  - `pk=2` (`Negocios Digitais`) em `despesa`, usando `Estrutura` como categoria pai
  - `pk=12` (`Transf5666`) em `despesa`, usando `Estrutura` como categoria pai
  - `pk=23` (`Teste regra aut`) em `despesa`, usando `Doacao`, categoria do tipo `receita`
- diretriz aplicada nesta microetapa:
  - saneamento dirigido da base atual
  - sem afrouxar o contrato da importacao comum
  - sem transformar a microetapa em refatoracao da importacao
- correcoes aplicadas:
  - foi criada a subcategoria `Operacao Cantina` sob a categoria pai `Cantina`
  - os lancamentos `pk=1` e `pk=4` passaram de `Cantina` para `Operacao Cantina`
  - foi criada a subcategoria `Operacao Estrutura` sob a categoria pai `Estrutura`
  - os lancamentos `pk=2` e `pk=12` passaram de `Estrutura` para `Operacao Estrutura`
  - o lancamento `pk=23` passou de `despesa` para `receita`, preservando a subcategoria `Doacao`
  - a `RegraLancamentoFinanceiro pk=3`, ligada ao mesmo caso de `Teste regra aut`, tambem foi alinhada para `receita` com `Doacao`, evitando reintroduzir o legado invalido em uso futuro da regra
- as criacoes/atualizacoes foram executadas em transacao com trilha de auditoria no proprio modulo
- depois do saneamento:
  - foi gerado um novo pacote real de reconstrucao em `tmp/operacao_reset_financeiro_20260406_081633/`
  - esse pacote passou a refletir:
    - `5` contas
    - `2` pessoas
    - `2` centros de custo
    - `11` categorias no total
    - `6` categorias pai
    - `5` subcategorias
    - `14` lancamentos simples
    - `12` lancamentos rateados
    - `6` grupos de rateio
- o novo preflight completo foi executado com rollback:
  - limpeza total do dominio `financeiro` apenas dentro da transacao
  - reimportacao valida de `contas`
  - reimportacao valida de `pessoas`
  - reimportacao valida de `centros de custo`
  - reimportacao valida de `categorias/subcategorias`
  - reimportacao valida de `14` lancamentos simples
  - restauracao tecnica valida de `6` grupos de rateio e `12` linhas rateadas
  - rollback ao final, preservando a base real atual
- conclusao consolidada:
  - o bloqueio dos `5` lancamentos simples foi removido
  - o reset destrutivo real fica tecnicamente liberado do ponto de vista da reconstrucao
  - mesmo assim, o reset real ainda nao foi executado nesta microetapa
- a frente futura continua registrada sem implementacao nesta etapa:
  - exportacao comum de lancamentos com suporte a rateio por grupo em planilha
  - importacao comum de lancamentos com suporte a reconstrucao de rateio por grupo em planilha

## Procedimento real de backup/reset/reconstrucao do financeiro

- a etapa operacional real de reconstruir a base do `financeiro` foi iniciada com geracao do pacote definitivo de reconstrucao, mas o reset destrutivo real **nao** foi executado ao final desta microetapa
- o pacote real foi gerado em:
  - `tmp/operacao_reset_financeiro_20260406_074817/`
- conteudo principal do pacote:
  - `rateios_backup_definitivo.json`
  - `01_contas_financeiras_importacao.xlsx`
  - `02_pessoas_financeiras_importacao.xlsx`
  - `03_centros_custo_importacao.xlsx`
  - `04_categorias_importacao.xlsx`
  - `05_lancamentos_simples_importacao.xlsx`
  - `manifesto_pre_reset.json`
- o preflight operacional da reconstrucao foi executado em transacao com rollback antes do reset real:
  - limpeza total do dominio `financeiro` apenas dentro da transacao de teste
  - reimportacao valida de `contas`
  - reimportacao valida de `pessoas`
  - reimportacao valida de `centros de custo`
  - reimportacao valida de `categorias/subcategorias`
  - tentativa de reimportacao dos `lancamentos simples` pelo fluxo comum
  - rollback ao final, preservando a base real atual
- o preflight mostrou que o reset real ainda nao pode ser disparado com seguranca:
  - `14` lancamentos simples avaliados
  - apenas `9` linhas validas no fluxo comum
  - `5` linhas invalidas
- bloqueios objetivos encontrados na reconstrucao comum dos lancamentos simples:
  - linhas `2` e `15`: despesas usando `Cantina`, hoje tratada como `Categoria` pai e nao como `Subcategoria`
  - linhas `3` e `12`: despesas usando `Estrutura`, hoje tratada como `Categoria` pai e nao como `Subcategoria`
  - linha `13`: despesa usando `Doacao`, que pertence ao tipo `receita`
- isso cria um novo bloqueio estrutural anterior ao reset:
  - o caminho tecnico de rateio ja resolveu a preservacao dos grupos rateados
  - mas a importacao comum atual dos lancamentos simples nao recompõe integralmente a base real por causa desses legados fora do contrato atual
- decisao operacional desta microetapa:
  - `backup` definitivo gerado e guardado
  - `reset` destrutivo real adiado
  - nenhuma alteracao destrutiva aplicada na base local
- permanece registrada como frente futura explicita:
  - evoluir a exportacao comum de lancamentos para suportar rateio por grupo em planilha
  - evoluir a importacao comum de lancamentos para reconstruir rateio por grupo em planilha
- essa frente futura nao foi implementada nesta microetapa

## Backup/restauracao tecnica de rateios antes do reset real

- o reset destrutivo real do `financeiro` continuou bloqueado enquanto a base local dependia apenas da importacao comum de lancamentos para ser recomposta
- o bloqueio ficou objetivo no repositorio e na base atual:
  - existem `12` lancamentos com `com_rateio=True`
  - esses lancamentos estao distribuidos em `6` grupos de rateio
  - a importacao comum atual de lancamentos nao recompõe `grupo_rateio`, nem trata rateio como documento agrupado
- para destravar o reset futuro sem abrir uma nova frente na importacao funcional comum, foi adotada uma trilha tecnica separada:
  - novo helper tecnico `financeiro/rateio_backup.py`
  - novo comando `backup_rateios_financeiro`
  - novo comando `restaurar_rateios_financeiro`
- a estrategia final adotada nesta microetapa foi:
  - backup em `JSON` tecnico, separado do fluxo de importacao comum
  - serializacao por `grupo_rateio`, com `numero_documento`, total do grupo e linhas internas
  - cada linha preserva os campos operacionais do lancamento rateado e referencia os cadastros auxiliares por chave de negocio estavel, e nao por `pk`
  - contas: por `nome`
  - pessoas: por `codigo`
  - centros de custo: por `codigo`
  - categorias: por `tipo`, `nome` e `categoria_pai_nome`
  - restauracao transacional e explicita, com `dry-run` por padrao e confirmacao obrigatoria para gravacao real
- o restore tecnico ficou propositalmente fora da importacao funcional comum do usuario:
  - ele existe para reconstruir base apos reset, nao para operacao cotidiana
  - isso permite preservar fidelidade estrutural do rateio sem afrouxar a UX nem o contrato da importacao comum
- a validacao da restauracao revelou e passou a tratar residuos legados ja existentes na base atual:
  - ha linhas rateadas antigas apontando para `categoria pai`, hoje invalida no fluxo comum
  - ha `2` grupos legados com apenas `1` linha, embora o rateio atual de negocio trabalhe com `2+` linhas
  - o restore tecnico agora recompõe esses residuos com fidelidade, apenas no caminho tecnico, sem liberar essa excecao no cadastro/importacao funcional comum
- validacao executada nesta microetapa:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - `py manage.py backup_rateios_financeiro --saida tmp/rateios_validacao.json` OK
  - `py manage.py restaurar_rateios_financeiro --arquivo tmp/rateios_validacao.json` OK em `dry-run`
  - roundtrip controlado com rollback em subconjunto de `2` grupos:
    - grupos apagados temporariamente dentro de transacao de teste
    - restauracao tecnica executada em memoria logica
    - `roundtrip_idem=True`
    - `2` grupos restaurados
    - `4` linhas restauradas
    - `3` linhas legadas restauradas
    - `4` auditorias `create` tecnicas geradas no teste
    - rollback aplicado ao final para nao alterar a base local definitiva
- resultado pratico:
  - agora existe estrategia concreta e implementada para preservar/restaurar rateios antes do reset
  - o reset real deixa de ficar bloqueado pela ausencia de trilha tecnica para grupos rateados
  - ainda assim, o reset destrutivo real nao foi executado nesta microetapa
- comandos tecnicos consolidados:
  - backup: `py manage.py backup_rateios_financeiro --saida tmp/meu_backup_rateios.json`
  - restore em simulacao: `py manage.py restaurar_rateios_financeiro --arquivo tmp/meu_backup_rateios.json`
  - restore real: `py manage.py restaurar_rateios_financeiro --arquivo tmp/meu_backup_rateios.json --executar --confirmar RESTAURAR_RATEIOS_FINANCEIRO`
- limitacoes remanescentes:
  - o backup/restauracao tecnica cobre apenas os lancamentos `com_rateio=True` e seus grupos
  - ele nao substitui nem amplia a importacao funcional comum de lancamentos
  - ele tambem nao preserva o historico anterior de auditoria apagado pelo reset; na restauracao, novas auditorias tecnicas de criacao sao geradas para rastreabilidade minima

## Validacao controlada dos 4 fluxos de importacao auxiliar

- foi executada validacao funcional controlada dos 4 fluxos auxiliares de importacao do `financeiro`, cobrindo:
  - `contas`
  - `pessoas`
  - `centros de custo`
  - `categorias/subcategorias`
- a validacao foi feita pelo fluxo HTTP do proprio Django com `Client`, porque este ambiente nao expôs automacao de navegador confiavel e o `manage.py shell` precisou de execucao fora do sandbox para funcionar
- o roteiro executado cobriu:
  - caso de sucesso para cada fluxo
  - caso invalido para cada fluxo
  - mensagens de sucesso/erro
  - politica `all-or-nothing` por arquivo
  - permissoes exigidas
  - geracao de auditoria
  - regra de dependencia entre categoria pai e subcategoria
- resultado funcional consolidado:
  - `Operador financeiro` acessa a central e consegue importar os 4 cadastros
  - `Consulta/visualizacao` recebe `403` ao tentar acessar a central
  - um perfil temporario com apenas `financeiro.lancamentos.importar` e `financeiro.lancamentos.baixar_modelo`, sem permissao de criacao do cadastro alvo, acessa a central mas nao recebe os formularios auxiliares e recebe `403` em download/post direto de `contas`
  - nos 4 fluxos, o caso de sucesso importou 2 registros, gerou 2 auditorias `create` e exibiu mensagem de sucesso coerente
  - nos 4 fluxos, o caso invalido manteve `0` registros importados e `0` auditorias novas, confirmando `all-or-nothing`
  - em `categorias/subcategorias`, a importacao valida preservou a vinculacao `categoria pai -> subcategoria`, e o caso invalido bloqueou a carga quando a categoria pai nao existia ou nao vinha antes
- bug real encontrado e corrigido nesta microetapa:
  - as planilhas-base auxiliares eram geradas com a aba `Instrucoes`, mas a validacao estrutural aceitava apenas `Instruções`
  - isso fazia a importacao auxiliar falhar antes de ler qualquer linha, mesmo usando a planilha gerada pelo proprio sistema
  - a validacao passou a aceitar a nomenclatura sem acento, compatibilizando o upload com o layout atualmente baixado pelo usuario
- validacao tecnica executada apos a correcao:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
- limitacao remanescente desta etapa:
  - a validacao funcional ficou forte o suficiente para fechar comportamento, permissao, mensagens e auditoria, mas a checagem visual humana literal no navegador ainda continua opcional como ultima confirmacao de acabamento antes do reset destrutivo real

## Importacoes auxiliares centralizadas do financeiro

- a decisao consolidada mais recente desta frente passou a ser:
  - importacoes auxiliares ficam centralizadas no financeiro geral
  - exportacoes permanecem nas telas/listagens especificas para respeitar filtros
  - `assinaturas` ficaram fora do escopo desta frente
- com isso, a camada anterior de planilhas-base foi ajustada de forma cirurgica:
  - `AssinaturaInstitucional` saiu da central de planilhas-base/importacoes auxiliares
  - a central passou a cobrir apenas `ContaFinanceira`, `PessoaFinanceira`, `CentroCusto` e `CategoriaFinanceira`/subcategorias
- a tela central de importacoes do modulo foi consolidada como ponto unico para:
  - importacao de lancamentos
  - download das planilhas-base dos cadastros auxiliares
  - importacao real de contas
  - importacao real de pessoas
  - importacao real de centros de custo
  - importacao real de categorias/subcategorias
- a ordem operacional de carga ficou fechada assim:
  - contas
  - pessoas
  - centros de custo
  - categorias pai e depois subcategorias
  - lancamentos
- as regras finais adotadas para a importacao auxiliar ficaram:
  - reaproveitar exatamente os layouts-base ja definidos
  - fluxo centralizado no financeiro geral, sem espalhar a importacao como fluxo principal em cada cadastro
  - validacao estrutural do XLSX por abas e cabecalhos
  - validacao de conteudo linha a linha com mensagens claras por campo
  - gravacao transacional por arquivo, sem importacao parcial
  - auditoria de criacao para contas, pessoas, centros de custo e categorias importadas
  - permissao base da tela continua em `financeiro.lancamentos.importar`, e cada importacao auxiliar tambem respeita a permissao de criacao do cadastro correspondente
- os layouts ativos desta frente passam a ser:
  - contas: `nome`, `descricao`, `saldo_inicial`, `data_saldo_inicial`, `ativa`
  - pessoas: `codigo`, `nome`, `tipo_pessoa`, `documento`, `telefone`, `email`, `observacoes`, `ativo`
  - centros de custo: `codigo`, `nome`, `ativo`
  - categorias/subcategorias: `nome`, `tipo`, `categoria_pai_nome`, `mensagem_recibo`, `ativo`
- validacao local executada nesta microetapa:
  - `py manage.py check` OK
  - `py -m compileall financeiro` OK
  - houve tentativa de smoke test transacional por script para exercitar a importacao em memoria, mas o ambiente bloqueou execucoes via `manage.py shell` com `Acesso negado`; a validacao funcional fina no navegador continua recomendada antes do reset destrutivo real

## Planilhas-base reutilizaveis dos cadastros auxiliares do financeiro

- foi consolidada a camada de planilhas-base reutilizaveis para reconstruir a base local do `financeiro` apos o reset controlado, sem executar ainda a importacao auxiliar em si
- a geracao dos modelos XLSX passou a ficar disponivel no proprio fluxo existente de `Importacao de Lancamentos`, em coerencia com o padrao ja usado para a planilha modelo de lancamentos
- os cadastros auxiliares contemplados nesta microetapa foram:
  - `ContaFinanceira`
  - `PessoaFinanceira`
  - `CentroCusto`
  - `CategoriaFinanceira` e subcategorias
  - `AssinaturaInstitucional`
- a ordem operacional recomendada de carga ficou explicita na tela e no contrato tecnico:
  - contas
  - pessoas
  - centros de custo
  - categorias pai e depois subcategorias
  - assinaturas institucionais
  - somente depois, lancamentos
- os layouts-base gerados nesta etapa ficaram assim:
  - contas: `nome`, `descricao`, `saldo_inicial`, `data_saldo_inicial`, `ativa`
  - pessoas: `codigo`, `nome`, `tipo_pessoa`, `documento`, `telefone`, `email`, `observacoes`, `ativo`
  - centros de custo: `codigo`, `nome`, `ativo`
  - categorias/subcategorias: `nome`, `tipo`, `categoria_pai_nome`, `mensagem_recibo`, `ativo`
  - assinaturas: `nome`, `assinatura_texto`, `nome_exibicao`, `cargo`, `ativo`, `padrao`
- cada arquivo segue o contrato minimamente padronizado ja adotado no modulo:
  - aba `Modelo` com apenas os cabecalhos oficiais
  - aba `Instrucoes` com orientacoes praticas de preenchimento
  - nomenclatura explicita como `planilha-base`, para nao confundir o usuario com importacao auxiliar pronta
- esta microetapa nao implementou:
  - importacao auxiliar real dos cadastros
  - reset destrutivo
  - logo local
  - deploy/hospedagem
- validacao tecnica minima prevista para esta etapa:
  - `py manage.py check`
  - abertura da tela de importacao/exportacao com os downloads auxiliares expostos
  - download dos modelos XLSX pelo sistema, sem gravacao de dados

## Reset controlado do financeiro

- foi criado o management command `reset_financeiro_controlado` em `financeiro/management/commands/reset_financeiro_controlado.py` como fluxo tecnico dedicado para reiniciar apenas os dados do modulo `financeiro`
- a regra final desta microetapa ficou explicita e conservadora:
  - o comando apaga `LancamentoFinanceiro`, `RegraLancamentoFinanceiro`, `AuditoriaFinanceiro`, `ContaFinanceira`, `PessoaFinanceira`, `CategoriaFinanceira`/subcategorias, `CentroCusto`, `AssinaturaInstitucional` e `ConfiguracaoInstitucional`
  - o comando preserva `User`, autenticacao, `PerfilAcesso`, `PermissaoSistema`, `UsuarioPerfilAcesso`, `SiteConfig`, configuracoes sistemicas e modulos fora do `financeiro`
- o reset nao e silencioso:
  - por padrao, o comando roda em `dry-run` e apenas mostra o que seria apagado e o que sera preservado
  - a execucao real so acontece com `--executar --confirmar RESETAR_FINANCEIRO`
- a ordem de exclusao foi implementada de forma segura para respeitar dependencias do dominio: regras e auditorias antes, lancamentos antes dos cadastros protegidos por `PROTECT`, subcategorias antes de categorias pai
- validacao pratica minima local desta microetapa:
  - `py manage.py check` OK
  - `py manage.py reset_financeiro_controlado` OK em modo simulacao, exibindo escopo de exclusao e preservacao sem alterar dados
  - a execucao destrutiva real nao foi rodada nesta validacao para evitar apagar a base local fora de uma acao operacional consciente do usuario

## Auditoria de fechamento do financeiro para homologacao/hospedagem

- o modulo `financeiro` foi auditado com foco em operacao real e prontidao para homologacao, cobrindo lancamentos, contas, pessoas, categorias/subcategorias, centros de custo, assinaturas, extrato, resumo, prestacao de contas, auditoria, clone, rateio, importacao, exportacao, acoes em lote, enforcement de permissoes e integracao ao shell compartilhado
- pela auditoria objetiva do repositorio, nao apareceu bloqueante funcional novo dentro do dominio ja entregue do `financeiro`; o modulo segue como area mais madura do sistema para homologacao
- o principal risco remanescente estava na configuracao de deploy do projeto, e nao na regra de negocio do `financeiro`
- `casa_espirita/settings.py` passou a endurecer a execucao em producao:
  - `DJANGO_SECRET_KEY` agora deixa de aceitar fallback inseguro quando `DEBUG` estiver desligado
  - `DJANGO_ALLOWED_HOSTS` passa a ser obrigatorio quando `DEBUG` estiver desligado
  - `CSRF_TRUSTED_ORIGINS` passou a aceitar configuracao por ambiente
  - `STATIC_ROOT` foi definido em `staticfiles/`, preparando `collectstatic`
  - `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT` e `SECURE_PROXY_SSL_HEADER` passaram a ter chaves de ambiente proprias para homologacao/producao
- pendencias tecnicas ainda abertas para hospedagem:
  - configurar SMTP real para que a recuperacao de senha deixe de depender do backend de console
  - validar a estrategia final de banco no provedor de hospedagem; hoje o projeto permanece em `sqlite3`, o que pode servir para homologacao simples, mas depende de armazenamento persistente no host
  - executar `migrate` e `collectstatic` no ambiente de hospedagem real
  - revisar, em etapa posterior, paginas de erro customizadas de producao (`403/404/500`) caso a hospedagem siga alem da homologacao interna
- validacao automatizada local:
  - `py manage.py check` OK
  - comandos como `showmigrations`, `collectstatic --dry-run` e alguns `manage.py shell -c` seguiram limitados neste ambiente por `Acesso negado`, entao a confirmacao final de hospedagem continua dependendo do provedor/ambiente real
- backlog externo apenas registrado, sem implementacao nesta etapa:
  - `eventos` permanece fora do foco de homologacao do `financeiro`
  - `biblioteca` e demais modulos nao devem puxar novas correcoes agora, salvo se surgirem impactos diretos no shell compartilhado ou no portal do sistema

## Pacote de hospedagem/homologacao preparado

- foi criado `docs/GUIA_HOSPEDAGEM_FINANCEIRO.md` como guia pratico de deploy/homologacao do sistema atual, com foco no `financeiro`
- foi criado `.env.example` com placeholders seguros para as variaveis de ambiente hoje necessarias na subida
- `requirements.txt` passou a incluir `gunicorn` e `whitenoise` para reduzir atrito de hospedagem
- `casa_espirita/settings.py` passou a servir estaticos com `WhiteNoise`, usar `STATIC_URL` e `MEDIA_URL` com barra inicial, aceitar `DJANGO_DB_PATH` para o SQLite em local persistente e aceitar `DJANGO_MEDIA_ROOT` por ambiente
- a configuracao de seguranca HTTPS tambem passou a prever `DJANGO_SECURE_HSTS_SECONDS`, `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` e `DJANGO_SECURE_HSTS_PRELOAD`
- validacao executada:
  - `py manage.py check` OK
  - `py manage.py check --deploy` executado com variaveis de teste e depois com simulacao mais proxima de producao
  - na simulacao mais proxima de producao, os avisos remanescentes ficaram restritos a `SECURE_HSTS_INCLUDE_SUBDOMAINS` e `SECURE_HSTS_PRELOAD`, tratados como decisao do host/dominio e nao como bloqueio imediato da homologacao
- pendencias ainda dependentes do provedor/ambiente real:
  - SMTP real
  - politica final de banco na hospedagem
  - execucao de `migrate` e `collectstatic`
  - proxy/HTTPS efetivos do host

## Estrutura inicial do modulo eventos

- o app `eventos` foi criado e registrado no projeto como nova prova estrutural de modulo aderente ao padrao consolidado do sistema
- a rota canonica `/eventos/` agora existe e funciona como landing inicial do modulo, sem 404 e sem depender de caminho interno adicional
- a landing inicial do modulo foi ligada ao shell autenticado compartilhado, exibindo nome institucional, usuario/perfil, `Inicio` e `Sair`, sem abrir ainda o dominio completo de eventos
- o portal autenticado `/inicio/` passou a considerar `Eventos` no catalogo central de modulos, com visibilidade controlada por permissao real
- a base inicial de permissoes V1 do modulo foi criada com `eventos.eventos.visualizar`, `eventos.eventos.listar` e `eventos.eventos.criar`
- essas permissoes foram semeadas para:
  - `Administrador geral`: visualizar, listar e criar
  - `Gestao administrativa`: visualizar, listar e criar
  - `Consulta/visualizacao`: visualizar e listar
- nesta fase, `Operador financeiro` e `Operador biblioteca` ficaram sem acesso inicial ao modulo para manter o nascimento de `eventos` isolado e sem ampliar escopo operacional sem demanda de negocio fechada

## Regularizacao do nome institucional em SiteConfig

- a auditoria do banco confirmou que havia apenas 1 registro em `SiteConfig` e que o valor `Lar de Teste` era dado salvo no ambiente, nao erro de leitura, duplicidade ou seed ativa do repositorio
- a origem do placeholder nao estava em seed ou migration do projeto: o codigo atual ja trabalhava com fallback de `Casa Espirita` / `Casa Espírita`; o problema estava no dado institucional persistido localmente
- foi criada a migration `configuracoes/migrations/0008_regularizar_nome_institucional_siteconfig.py`, que atualiza o `site_name` apenas quando ele estiver exatamente como `Lar de Teste`, evitando sobrescrever ambientes ja personalizados com outro nome real
- o default estrutural de `SiteConfig.site_name` passou a ser `Casa Espírita Caminheiros da Luz`, e os fallbacks usados em `views`, `context_processors` e no titulo da tela de configuracoes foram alinhados ao mesmo nome institucional oficial
- com isso, login, shell autenticado, portal `/inicio/` e telas que leem `SiteConfig` continuam usando a mesma fonte de verdade do projeto, mas agora com branding institucional correto no ambiente atual e em novos ambientes que nascerem sem configuracao manual

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

## Frequencia por competencia - matriz sem valores derivada

- a matriz com valores ja validada pela usuaria em uso real passou a oferecer tambem o formato `Sem valores (frequencia)` na mesma tela `/financeiro/frequencia-competencias/`
- a derivacao continua vindo da mesma base agregada de `AlocacaoCompetenciaFinanceira`, sem criar controle paralelo, sem checkbox manual e sem usar valor bruto do lancamento ou do grupo rateado
- o filtro novo `Formato da matriz` alterna entre:
  - `Com valores` (modo monetario ja homologado)
  - `Sem valores (frequencia)` (modo visual)
- no modo sem valores:
  - celula com valor alocado maior que zero exibe indicador positivo `✓`
  - celula sem valor exibe indicador negativo `×`
  - os mesmos filtros de periodo, subcategoria controlada e status continuam ativos
  - `Todos` segue considerando apenas `quitado + aberto`
- totais entregues no modo sem valores:
  - total por favorecido = quantidade de competencias com contribuicao no periodo
  - total por mes = quantidade de favorecidos com contribuicao naquela competencia
  - total geral = total de ocorrencias positivas na matriz
- a tela continua listando favorecidos recorrentes mesmo sem alocacao no periodo, agora com leitura visual negativa nos meses vazios
- impressao da matriz ainda nao havia sido implementada nesta microetapa
- nao houve alteracao em models, migrations, calculos financeiros, saldos, relatorios existentes ou banco real; nenhum arquivo SQLite foi alterado/versionado

## Frequencia por competencia - impressao da matriz

- a tela `/financeiro/frequencia-competencias/` passou a ter acao `Imprimir`, reaproveitando `window.print()` como nos demais relatorios do modulo
- a impressao cobre os dois formatos da matriz:
  - `Com valores`
  - `Sem valores (frequencia)`
- o impresso reaproveita o contrato documental do modulo com:
  - `financeiro-document-header`
  - `financeiro-document-meta-grid`
  - isolamento de shell/acoes por `no-print`
  - cabecalho enxuto com titulo, formato, periodo, subcategoria, status e data/hora de emissao
- foi aplicado contrato local de print para matriz larga:
  - `@page` em `A4 landscape`
  - margem reduzida `14mm 10mm`
  - tabela compactada com fonte menor, padding reduzido e `table-layout: fixed`
  - colunas mensais mais estreitas e coluna de favorecido reduzida
  - `thead` e `tfoot` preservados no print para repeticao/fechamento
- no modo sem valores, os indicadores continuam derivados de `AlocacaoCompetenciaFinanceira` e passam a imprimir com leitura aceitavel tambem em preto e branco, usando simbolo com borda leve em vez de depender apenas da cor
- elementos ocultados no print:
  - menu/shell
  - bloco hero de tela
  - filtros editaveis
  - botao de impressao e acao de voltar
  - sombras e molduras desnecessarias
- limitacao conhecida registrada:
  - o layout tenta acomodar todos os meses do intervalo na mesma pagina, mas periodos muito largos (mesmo dentro do limite funcional de 24 competencias) ainda podem ficar visualmente apertados conforme o navegador/impressora
- proxima microetapa recomendada: preparar o termo por favorecido usando a mesma base de competencias ja consolidada
- nao houve alteracao em calculos financeiros, saldos, relatorios existentes, models, migrations ou banco real; nenhum arquivo SQLite foi alterado/versionado

## Frequencia por competencia - refinamento da impressao com meses compactos

- refinada a impressao da matriz apos validacao visual em PDF real pela usuaria
- problema observado:
  - os cabecalhos mensais ocupavam espaco demais
  - a coluna `Favorecido` ficava comprimida e podia quebrar nomes de forma ruim, letra por letra
- ajuste aplicado:
  - a tela continua usando o rotulo visual ja aprovado (`Jan/2026`, `Fev/2026` etc.)
  - o impresso passa a usar rotulo compacto `MM/AAAA` (`01/2026`, `02/2026`, `03/2026` etc.)
  - a coluna `Favorecido` ganhou largura protegida via `colgroup`, `white-space: nowrap`, `text-overflow: ellipsis`, `word-break: normal` e `overflow-wrap: normal`
  - as colunas mensais ficaram mais compactas, com fonte e padding menores no print
  - valores e indicadores ficam centralizados no impresso para economizar largura
- a prioridade do PDF passa a ser: favorecido legivel, meses compactos, total visivel e tentativa de manter a matriz inteira na pagina
- a limitacao continua: periodos muito longos dentro do limite de 24 competencias podem ficar apertados conforme navegador/impressora
- nao houve alteracao de fonte de dados, calculos financeiros, saldos, relatorios existentes ou banco real; nenhum arquivo SQLite foi alterado/versionado

## Frequencia por competencia - ajuste de cor na impressao dos indicadores

- ajustada a impressao dos indicadores da matriz sem valores para tentar preservar verde (`✓`) e vermelho (`×`) tambem no PDF/print
- foi aplicado `print-color-adjust: exact` e `-webkit-print-color-adjust: exact` nos elementos de indicador, mantendo borda/simbolo como fallback legivel em preto e branco
- a regra da matriz nao mudou: indicadores continuam derivados de `AlocacaoCompetenciaFinanceira` e do valor alocado por competencia
- nao houve alteracao em models, migrations, calculos financeiros, saldos, relatorios existentes ou banco real; nenhum arquivo SQLite foi alterado/versionado

## Frente futura registrada - Assistente inteligente de competencias

- registrada como frente futura de UX, sem implementacao nesta microetapa
- objetivo: reduzir preenchimento manual de competencias quando houver favorecido recorrente + subcategoria controlada
- direcao funcional futura aprovada para SPEC:
  - sugerir janela de meses proximos (ultimos 5, mes atual e proximos 5)
  - nao tratar ausencia de competencia como status `em aberto`
  - mes sem valor alocado = sem quitacao registrada
  - mes com valor alocado = ja quitado/ja possui contribuicao
  - valor preenchido no mes deve funcionar como gatilho principal de inclusao/quitacao da competencia (sem checkbox obrigatorio)
  - modo manual atual deve continuar disponivel
  - complemento/observacao por competencia fica para SPEC propria
- proxima microetapa recomendada: abrir SPEC dedicada do assistente antes de alterar forms/models/templates de lancamento e rateio

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

## Endurecimento minimo do cadastro tecnico de usuarios para acesso funcional

- nesta fase, o cadastro e a edicao de usuarios continuam concentrados no `/admin/` tecnico; nao foi aberta uma UI funcional propria de usuarios/perfis
- o admin do `User` foi endurecido para operar junto com o vinculo `UsuarioPerfilAcesso`, exibindo e persistindo o `perfil base` no mesmo fluxo tecnico de criacao/edicao
- a regra V1 consolidada passou a ser: usuario ativo ou administrador tecnico (`is_staff`/`is_superuser`) precisa ter e-mail valido; usuario funcional ativo (ativo, nao `is_staff` e nao `is_superuser`) precisa ter tambem `perfil base`
- a separacao entre administracao tecnica/global e acesso funcional foi preservada: um superusuario ou `staff` tecnico pode permanecer sem perfil funcional, mas isso nao lhe concede acesso funcional implicito aos modulos protegidos
- o fluxo administrativo passou a aplicar validacao pratica de e-mail unico no proprio formulario do admin, sem introduzir ainda constraint de unicidade no banco; a base atual foi auditada e nao apresentou e-mails duplicados
- na auditoria do banco antes do saneamento, nao havia usuarios sem e-mail; os casos pendentes reais eram usuarios ativos sem `UsuarioPerfilAcesso`
- o saneamento seguro adotado nesta microetapa foi desativar automaticamente, por migration de dados, usuarios funcionais ativos (nao `staff`, nao `superuser`) que estivessem sem e-mail ou sem perfil-base, evitando acesso inconsistente e sem criar e-mails ficticios
- com isso, os usuarios `reset_flow_tmp` e `semperfil_cfg` ficaram inativos ate regularizacao manual no `/admin/`; o superusuario `Luciano` permaneceu ativo por ser administracao tecnica global e ja possuir e-mail valido, embora continue sem perfil funcional implicito
- smoke tests confirmaram: criacao administrativa de usuario funcional ativo sem e-mail falha; criacao administrativa de usuario funcional ativo sem perfil falha; usuario `staff` tecnico com e-mail pode permanecer sem perfil; o reset por e-mail segue funcional para usuario regularizado com e-mail

## Navegacao global autenticada e portal inicial por modulos

- o sistema agora possui uma entrada autenticada central em `/inicio/`, tratada como portal inicial do sistema-mae apos login
- o redirecionamento padrao de login deixou de apontar diretamente para `financeiro/lancamentos` e passou a levar o usuario para esse portal autenticado
- a visibilidade dos cards de `Financeiro`, `Biblioteca` e `Configuracoes` passou a ser resolvida pela base central de permissoes ja implantada, usando permissao real do usuario para decidir quais modulos aparecem
- usuario autenticado sem perfil funcional continua deny-by-default: consegue autenticar, mas o portal passa a mostrar estado sem modulos operacionais liberados, sem expor entrada funcional indevida
- foi criada uma camada central de navegacao global em `configuracoes/context_processors.py`, combinando nome institucional, usuario autenticado, perfil-base atual e lista de modulos disponiveis para reutilizacao em templates
- o shell autenticado minimo do sistema passa a exibir nome institucional, usuario autenticado, perfil base quando existir, atalho de `Inicio`, opcionalmente `Admin tecnico` para `staff` e botao global de `Sair`
- `financeiro`, `biblioteca` e `configuracoes` passaram a refletir essa navegacao global sem reabrir grande refactor visual: os modulos continuam com seus shells proprios, mas agora exibem atalho de retorno ao `Inicio` do sistema e `Sair` visivel quando o usuario esta autenticado
- smoke tests confirmaram: login bem-sucedido redireciona para `/inicio/`; `Operador financeiro` ve `Financeiro` e `Configuracoes`; `Operador biblioteca` ve `Biblioteca` e `Configuracoes`; `Consulta/visualizacao` ve os tres modulos; usuario sem perfil ve o portal sem cards operacionais; logout continua redirecionando para `/login/`

## UI funcional minima de perfis e usuarios de acesso

- a administracao funcional de acesso deixou de depender apenas do `/admin/`: foi aberta uma UI minima no app `configuracoes` para leitura de perfis-base e ajuste simples do vinculo `usuario -> perfil base`
- foram criadas rotas protegidas para `perfis`, `detalhe do perfil`, `usuarios com perfil` e `edicao do perfil base do usuario`, sem abrir ainda editor granular da matriz nem extras/bloqueios individuais
- a protecao backend dessa nova area usa a mesma base central de enforcement ja consolidada, com novas permissoes canonicas de `configuracoes`:
  - `configuracoes.perfis_acesso.listar`
  - `configuracoes.perfis_acesso.visualizar`
  - `configuracoes.usuarios_acesso.listar`
  - `configuracoes.usuarios_acesso.editar_perfil`
- essas permissoes foram semeadas de forma incremental e vinculadas apenas a `Administrador geral` e `Gestao administrativa`, mantendo `Operador financeiro`, `Operador biblioteca` e `Consulta/visualizacao` fora da administracao funcional de acesso nesta etapa
- o detalhe do perfil foi organizado por `modulo -> recurso -> acoes`, priorizando leitura clara e sem abrir checkboxes ou edicao granular de permissao
- a listagem de usuarios passou a mostrar identificacao, e-mail, status ativo/inativo, indicacao de administracao tecnica e perfil-base atual
- a edicao funcional do vinculo `usuario -> perfil base` ficou restrita a um formulario simples, seguro e coerente com as regras endurecidas no `/admin/`: usuario funcional ativo continua exigindo perfil-base; usuario tecnico (`staff`/`superuser`) pode seguir sem perfil funcional; usuario funcional sem e-mail valido nao recebe perfil pela UI
- a navegacao dessa area entra pelo modulo `Configuracoes`: a tela `SiteConfig /` passou a exibir links de `Perfis de acesso` e `Usuarios e perfis` apenas para quem possui permissao funcional de administracao dessa frente
- smoke tests confirmaram: `Administrador geral` e `Gestao administrativa` acessam listagem de perfis, detalhe do perfil, listagem de usuarios e alteracao do vinculo; `Operador financeiro` recebe `403` nessas rotas; a alteracao funcional de perfil base persiste corretamente no banco

## Polimento final da frente de autenticacao e acesso

- a tela de login passou a oferecer controle explicito de `Mostrar/Ocultar` senha, sem alterar o backend de autenticacao nem o comportamento de permissao
- o fluxo de recuperacao de senha foi endurecido contra enumeracao de usuarios: o formulario deixou de acusar explicitamente quando o e-mail nao pertence a um usuario ativo/utilizavel e passou a seguir com mensagem neutra no fluxo de confirmacao
- a decisao consolidada nesta fase foi manter a mensagem de reset neutra, por ser mais segura para a operacao real do sistema agora que autenticacao/acesso ja estao ativos
- o nome institucional do login continua vindo dinamicamente de `SiteConfig.site_name`, com fallback seguro para `Casa Espirita`; a apresentacao foi preservada sem tratar dado cadastrado provisoriamente como bug de codigo
- o portal `/inicio/` passou a tratar melhor o caso de usuario autenticado sem perfil funcional ou sem modulos liberados, com mensagem mais clara e acoes de saida/admin tecnico quando fizer sentido
- a UI funcional minima de perfis passou a ter estados vazios mais claros para lista de perfis e lista de usuarios, sem alterar as regras de acesso da area
- a avaliacao da unicidade do e-mail foi refeita nesta microetapa: a base segue sem duplicados, mas ainda nao foi introduzida constraint de banco porque o projeto continua apoiado no `User` padrao do Django e a mudanca estrutural nesse nivel segue desproporcional para o risco atual; permanece valendo a validacao forte no fluxo administrativo
- smoke tests confirmaram: login `200` com controle de senha visivel; reset de senha com e-mail inexistente segue fluxo neutro para a tela de confirmacao; usuario sem perfil recebe estado claro no portal; `Gestao administrativa` continua com acesso `200` a UI funcional de perfis; `Operador financeiro` continua barrado com `403`; logout segue retornando a `/login/`

## Consolidacao do shell autenticado compartilhado

- `configuracoes/templates/configuracoes/sistema_base.html` passou a ser a base autenticada oficial e reutilizavel do sistema, concentrando topbar global, identidade institucional, usuario/perfil, links globais, area principal de conteudo, mensagens e novos slots para navegacao local de modulo
- a duplicacao de chips e links globais (`Inicio`, `Admin tecnico`, `Sair`, usuario e perfil) foi reduzida com o parcial compartilhado `configuracoes/_sistema_usuario_acoes.html`, consumido pela base global e tambem pelo shell proprio do `financeiro`
- `biblioteca/templates/biblioteca/base.html` deixou de manter HTML/base propria e passou a derivar diretamente de `configuracoes/sistema_base.html`, preservando apenas o que e especifico do modulo: subtitulo, navegacao local por recurso e pequenos ajustes de estilo
- `configuracoes/templates/configuracoes/siteconfig_detail.html` deixou de repetir topbar/autenticacao local e passou a operar sobre a mesma base global autenticada, mantendo apenas o conteudo institucional e os atalhos funcionais de acesso dessa area
- no `financeiro`, a base propria continua existindo por necessidade real da sidebar, drawer mobile, grupos expansivos e JS local ja amadurecido; mesmo assim, o shell do modulo agora consome o mesmo bloco compartilhado de identidade/acoes globais, reduzindo repeticao sem reabrir a arquitetura da lateral
- a hierarquia consolidada desta etapa ficou assim: `configuracoes/sistema_base.html` como casca autenticada oficial do sistema; bases modulares derivadas quando necessario (`biblioteca/base.html`); shell especializado do `financeiro` preservado como caso especifico pela navegacao lateral, mas alinhado ao mesmo contrato visual global
- com isso, o projeto deixa de depender de topbars autenticadas paralelas entre `biblioteca` e `configuracoes`, e passa a ter uma base pronta para receber modulos futuros como `eventos`, `doacoes` e `corporativo` sem reabrir a casca autenticada a cada novo app
- `py manage.py check` permaneceu sem erros apos a consolidacao do shell compartilhado

## Normalizacao das entradas canonicas dos modulos

- as entradas oficiais dos modulos ficaram explicitamente fechadas como:
  - `/financeiro/`
  - `/biblioteca/`
  - `/configuracoes/`
- no `financeiro`, a decisao consolidada foi manter a raiz canonica do modulo em `/financeiro/` com redirecionamento controlado para a listagem principal de lancamentos, preservando o comportamento operacional ja amadurecido
- na `biblioteca`, a raiz `/biblioteca/` deixou de retornar `404` e passou a resolver a primeira tela de leitura permitida ao usuario entre `Autores`, `Livros`, `Vendas` e `Emprestimos`, mantendo consistencia com a matriz de permissoes sem expor caminho interno como entrada oficial
- em `configuracoes`, foi criada a entrada canonica explicita `/configuracoes/`, apontando para a mesma visualizacao funcional de `SiteConfig` ja usada na raiz; isso normaliza o contrato do modulo sem desmontar as rotas existentes de autenticacao e portal ja consolidadas em `/`, `/inicio/`, `/login/` e correlatas
- o portal autenticado `/inicio/` passou a usar apenas essas entradas oficiais ao montar os cards dos modulos, eliminando links para caminhos internos demais (`biblioteca:autor-list`) ou implícitos na raiz (`configuracoes:site-config` em `/`)
- a regra consolidada desta etapa ficou: o portal do sistema aponta para a rota canonica de cada modulo; cada modulo decide internamente se sua raiz entrega landing propria ou redireciona para a tela principal mais aderente ao estado atual do produto
- validacao tecnica: `py manage.py check` OK e entradas `/inicio/`, `/financeiro/`, `/biblioteca/` e `/configuracoes/` deixando de depender de rotas quebradas ou implícitas
## Fluxo contextual dos cadastros financeiros

- a microetapa atual consolidou retorno contextual nos principais formularios do `financeiro`, evitando que cadastros auxiliares voltem indevidamente para `lancamentos` quando a origem real foi a propria listagem do cadastro
- foi adotado o parametro seguro `return_to` para carregar a URL completa da listagem de origem, preservando filtros, ordenacao, pagina, `por_pagina` e preferencias ja presentes na querystring
- os links de criar, editar e excluir em `lancamento_list`, `conta_list`, `pessoa_list`, `categoria_list` e `centro_custo_list` passaram a incluir `return_to` com `request.get_full_path`
- os formularios de `conta`, `favorecido`, `categoria`, `centro de custo`, `lancamento` e edicao coordenada de rateio passaram a usar `cancel_url` contextual, em vez de sempre apontar para uma listagem fixa
- a acao principal `Salvar` salva e retorna conforme o contexto; a acao compacta `+`, sem texto longo, salva e permanece no fluxo de criacao para permitir cadastro em sequencia
- a acao `+` foi habilitada nos cadastros de `conta`, `favorecido`, `categoria`, `centro de custo` e `lancamento`; clones de lancamento nao usam essa acao para evitar ambiguidades operacionais
- exclusoes feitas a partir de listagens preservam o retorno contextual tambem no cancelamento e apos confirmacao
- validacao tecnica executada: `py manage.py check` OK, `py -m compileall financeiro` OK e smoke test com Django `Client` confirmando link com `return_to`, formulario com campo oculto de retorno, botao `+` e cancelamento contextual

## Estrutura de governança com AGENTS, skills, índice e regras de negócio

Foi criada e versionada a estrutura mínima de governança do projeto:

- AGENTS.md, com regras permanentes para o Codex.
- .agents/skills/, com skills iniciais para documentação, financeiro, relatórios/impressão, UX e importação.
- docs/INDICE_PROJETO.md, como ponto de entrada rápido do projeto.
- docs/REGRAS_NEGOCIO.md, como consolidação objetiva das regras permanentes.

Essa estrutura não altera o funcionamento do sistema Django. Ela organiza a forma de condução do projeto, reduz dependência de chats longos e estabelece uma base mais segura para continuidade entre conversas, GPT e Codex.

## Ajuste de UX nos filtros dependentes do Balancete

- o filtro principal `Formato do Balancete` passou a controlar imediatamente a exibição do filtro dependente `Detalhar patrimônio vinculado` no próprio frontend, sem exigir submit prévio
- a regra de exibição ficou:
  - `operacional_patrimonio`: filtro dependente visível
  - `operacional` e `financeiro_completo`: filtro dependente oculto
- a mudança foi implementada com script local no template do balancete e atributos `id/data-*` específicos para controle de visibilidade
- não houve alteração de cálculo financeiro, saldos, regras patrimoniais, models ou migrations
## Correcao do bug real de visibilidade do filtro patrimonial

- a validacao real mostrou que a etapa anterior nao ocultou o filtro de forma confiavel em todos os formatos
- causa provavel: o atributo `hidden` isolado nao foi suficiente no layout atual para garantir ocultacao visual consistente
- correcao aplicada: reforco de visibilidade com `hidden` + classe `is-hidden` + `style="display: none;"`, controlados por script local no carregamento e na troca de `Formato do Balancete`
- regra final aplicada:
  - `operacional`: oculto
  - `operacional_patrimonio`: visivel
  - `financeiro_completo`: oculto
- ajuste exclusivamente de UX, sem alteracao de calculo financeiro, saldos ou regras de negocio
## Aceite final funcional e de UX do Balancete Institucional

- a usuaria validou o Balancete Institucional como aprovado funcionalmente e em UX
- arquitetura por `Formato do Balancete` validada com tres formatos ativos:
  - `Operacional`
  - `Operacional + patrimonio vinculado`
  - `Financeiro completo`
- filtro antigo `Exibir contas vinculadas/indisponiveis` permanece fora da interface
- filtros complementares permanecem dependentes do formato selecionado
- o filtro `Detalhar patrimonio vinculado` foi validado para aparecer somente em `operacional_patrimonio`, com exibicao/ocultacao imediata ao trocar o formato
- regra consolidada:
  - formato `Operacional`: universo de saldo operacional disponivel, sem mistura com patrimonio vinculado
  - formato `Operacional + patrimonio vinculado`: bloco operacional + bloco patrimonial separado
  - formato `Financeiro completo`: leitura financeira total da instituicao
- transferencias entre operacional e vinculado permanecem como movimentacao de fronteira (nao viram receita/despesa operacional)
- nao houve alteracao de calculo financeiro, saldos, lancamentos, Extrato, Fechamento/Prestacao ou demais relatorios
- novos refinamentos dessa logica do Balancete ficam condicionados a nova decisao explicita da usuaria
## Levantamento de pendencias do financeiro apos aceite final do Balancete

- frente encerrada e congelada: Balancete Institucional aprovado funcionalmente e em UX; nao reabrir logica sem nova decisao explicita da usuaria
- classificacao consolidada de proximas pendencias:
  - Implementado, mas requer validacao da usuaria:
    - logo institucional no Extrato impresso em uso real de volume (`AGUARDANDO VALIDACAO VISUAL`)
    - importacoes com massa historica real e cadastros auxiliares em rotina completa (`AGUARDANDO HOMOLOGACAO`)
  - Modelado/documentado, mas nao implementado:
    - frequencia/recorrencia por competencia
    - contratos, parcelas e recorrencias
    - anexos de comprovantes
  - Pendente tecnico recomendado:
    - detalhamento opcional de transferencias internas no Extrato multi-contas (sem alterar consolidado padrao)
  - Futuro/backlog nao prioritario agora:
    - tabelas personalizadas de controle
    - evolucoes avancadas de extras/bloqueios individuais de permissao e log de acesso
  - Risco documental ou divergencia a conferir:
    - `ROADMAP_FINANCEIRO.md` ainda cita como pendente a revisao de modos avancados do Balancete em blocos historicos antigos; considerar historico, sem tratar como fila ativa enquanto o recorte aprovado estiver congelado
- recomendacao imediata: proxima microetapa deve ser auditoria documental/tecnica curta de importacoes em uso real (homologacao de planilhas historicas), sem mudanca funcional
## Auditoria documental do MVP de contribuicao mensal por competencia

- frente auditada: controle de contribuicao mensal/frequencia por competencia
- estado atual consolidado: modelada/documentada, sem implementacao funcional no codigo
- regra-base ja registrada: combinar `pessoa/favorecido recorrente` com `subcategoria que controla frequencia`, usando competencia mensal explicita e estrutura generica para outras recorrencias alem de contribuicao
- limites da etapa: nenhuma alteracao de codigo, migrations, calculos financeiros, Balancete, importacao ou relatorios existentes

Classificacao da frente:
- pronta para SPEC funcional, com decisoes pendentes da usuaria sobre recorte do MVP

MVP recomendado (futuras microetapas):
1) base cadastral minima:
   - flag de recorrencia no cadastro de pessoa/favorecido
   - flag de controle de frequencia no cadastro de subcategoria
2) matriz mensal com valores (primeira entrega de relatorio):
   - linhas por favorecido recorrente
   - colunas por competencia mensal
   - celula com valor contribuido por competencia
3) matriz mensal sem valores (foco em frequencia):
   - indicador visual de presenca/ausencia por competencia
4) termo/relatorio por favorecido (segunda onda):
   - contribuicoes feitas/nao feitas
   - valor medio e valor total no periodo

Riscos principais antes de migration:
- escolha da referencia de competencia (`data_competencia` x `data_pagamento`) e impacto em reconciliacao
- duplicidade de lancamentos no mesmo favorecido/subcategoria/mes
- contribuicoes parciais/multiplas no mesmo mes
- comportamento para favorecido inativo e para subcategoria desativada
- risco de misturar esta frente com Balancete ou importacao (escopos congelados/separados)

## Base cadastral minima de frequencia mensal por competencia

- implementada a base cadastral preparatoria da frente de frequencia/competencia no modulo financeiro
- novos campos:
  - `PessoaFinanceira.contribuinte_recorrente` (default `False`)
  - `CategoriaFinanceira.controla_recorrencia_competencia` (default `False`)
- os campos foram expostos em:
  - formularios de pessoa/favorecido e categoria/subcategoria
  - listagens de pessoa/favorecido e categoria/subcategoria
  - admin dos dois cadastros
  - importacao/exportacao auxiliar de pessoas e categorias, com compatibilidade para base nova
- nao houve implementacao de matriz mensal, alocacao de competencia ou termo por favorecido
- nao houve alteracao de calculo financeiro, lancamentos, saldos, Balancete, Extrato ou Fechamento/Prestacao

## Competencias mensais no fluxo de rateio controlado

- a captura de competencias passou a funcionar tambem no fluxo de rateio, reaproveitando `AlocacaoCompetenciaFinanceira` sem criar model nova
- a alocacao continua vinculada ao `LancamentoFinanceiro` persistido, e no rateio cada competencia fica presa apenas a linha/subcategoria controlada do grupo
- a soma das competencias do rateio agora e validada por item/subcategoria controlada, e nao pelo valor bruto total do documento
- itens nao controlados do mesmo documento (livro, camisa, doacao avulsa etc.) continuam fora da frequencia e nao recebem alocacao
- quando o favorecido nao e recorrente, ou quando nao existe item controlado no rateio, o fluxo segue sem exigir competencias
- a criacao com rateio e a edicao coordenada do grupo passaram a persistir/remover alocacoes de forma coerente com as linhas finais do grupo
- clone de rateio continua sem copiar competencias automaticamente
- exclusao da linha/lancamento continua removendo as alocacoes vinculadas por cascade
- ainda nao existe matriz mensal com valores, matriz sem valores ou termo por favorecido
- nao houve alteracao de calculo financeiro, saldos, Balancete, Extrato, Fechamento/Prestacao ou demais relatorios existentes

## Novas pendencias apos competencias no rateio controlado

- frente futura registrada: **auditoria acionavel** (pendente de SPEC propria), com necessidade de:
  - navegacao direta do registro de auditoria para o objeto/documento auditado quando existir
  - leitura clara de antes/depois
  - sinalizacao explicita quando o objeto auditado ja tiver sido excluido
  - estudo de desfazer/restaurar apenas com seguranca forte, trilha de reversao e permissoes especificas
- pendencia funcional/UX registrada: usuaria observou ausencia de acoes esperadas (exclusao/recibo) em alguns lancamentos da listagem; ficou definido auditar tecnicamente esse recorte antes de qualquer correcao
- regra recomendada registrada para proxima etapa funcional: bloquear mes/ano duplicado dentro do mesmo lancamento e da mesma subcategoria controlada (simples e rateio), orientando consolidacao do valor em linha unica
- regra atual preservada: alocacoes seguem exclusao por cascade junto da linha/lancamento; qualquer restauracao futura fica no escopo da frente de auditoria acionavel, nao na regra atual de competencias

## Correcao das acoes faltantes na listagem de lancamentos

- causa encontrada: o template da listagem bloqueava explicitamente `recibo` e `excluir` quando a linha visual era `eh_rateio`, mantendo apenas `clonar/editar` no bloco agrupado
- correcao aplicada:
  - a listagem passou a calcular `recibo_url` e `excluir_url` por linha visual (simples e rateio) no backend
  - lancamento simples (com ou sem competencias): manteve `Recibo`, `Clonar`, `Editar` e `Excluir` quando as permissoes existem
  - lancamento rateado/agrupado: passou a exibir recibo de grupo por favorecido (quando elegivel) e exclusao do grupo rateado por rota propria
- a exclusao de grupo rateado ganhou confirmacao dedicada e remove todas as linhas do grupo em transacao unica, mantendo trilha de auditoria por lancamento excluido
- impacto de permissao preservado:
  - sem permissao `financeiro.lancamentos.excluir`, o botao `Excluir` continua oculto
  - regras de permissao de `recibo`, `clonar` e `editar` permanecem inalteradas
- sem alteracao de calculo financeiro, saldos, regras de rateio, Balancete, Extrato, Fechamento/Prestacao ou demais relatorios

## Alinhamento de permissao na exclusao de grupo rateado

- auditoria da etapa confirmou que a rota de exclusao de grupo rateado e a exclusao simples usam o mesmo codigo de permissao: `financeiro.lancamentos.excluir`
- no catalogo atual, esse codigo existe e esta ativo; os perfis-base com esse acesso continuam `administrador-geral` e `gestao-administrativa`
- para eliminar qualquer risco de divergencia entre botao e backend, a listagem passou a montar `recibo_url` e `excluir_url` somente quando a permissao real do usuario estiver presente
- com isso, a renderizacao de acoes passa a depender da mesma verificacao de permissao usada no backend da rota protegida
- cobertura de testes reforcada:
  - usuario com permissao: acessa GET/POST de exclusao de grupo rateado
  - usuario sem permissao: nao recebe botao e GET direto da URL segue bloqueado (403)
  - exclusao simples continua acessivel com a mesma permissao
- sem alteracao de calculo financeiro, saldos, rateio financeiro, competencias, Balancete, Extrato ou Fechamento/Prestacao

## Restauracao de acesso a listagem de lancamentos

- a auditoria desta microetapa confirmou que o acesso a `/financeiro/lancamentos/` continua protegido por `financeiro.lancamentos.listar`; a etapa anterior nao trocou essa permissao
- o catalogo oficial segue consistente: `financeiro.lancamentos.listar` existe, esta ativo e pertence aos perfis `administrador-geral`, `gestao-administrativa`, `operador-financeiro` e `consulta-visualizacao`
- a causa encontrada para o bloqueio da usuaria foi operacional/local: usuario autenticado sem `UsuarioPerfilAcesso` vinculado recebe `403` por regra deny-by-default da camada funcional
- a listagem foi mantida com acesso normal para quem possui `financeiro.lancamentos.listar`, mesmo sem `emitir_recibo` ou `excluir`; nesses casos os botoes apenas ficam ocultos
- cobertura de testes reforcada para garantir:
  - usuario com `listar`, mas sem `emitir_recibo` e sem `excluir`, acessa a tela normalmente
  - usuario sem `listar` continua bloqueado
- sem alteracao de calculo financeiro, saldos, rateio, competencias, Balancete, Extrato ou Fechamento/Prestacao

## Correcao emergencial do bloqueio da listagem

- nova auditoria confirmou que os commits `d0001c5` e `1f97bcd` nao alteraram a permissao-base da `LancamentoFinanceiroListView`; a view segue exigindo apenas `financeiro.lancamentos.listar`
- o bloqueio real observado em `/financeiro/` e `/financeiro/lancamentos/` vinha do estado local de acesso: nao havia vinculo `UsuarioPerfilAcesso` persistido para o usuario principal autenticado
- como a camada funcional da V1 nao concede bypass automatico por `is_superuser`, usuario logado sem perfil-base continua recebendo `403` mesmo com o catalogo de permissoes correto
- restauracao aplicada localmente:
  - o usuario principal foi religado a um perfil-base valido (`administrador-geral`)
  - a validacao HTTP local via Django voltou `200` para `/financeiro/lancamentos/` com `HTTP_HOST=127.0.0.1`
- regra preservada:
  - `financeiro.lancamentos.listar` continua sendo a unica permissao exigida para abrir a listagem
  - ausencia de `excluir` ou `emitir_recibo` apenas oculta botoes e nao bloqueia a pagina
- sem alteracao de codigo financeiro, calculo, saldos, rateio, competencias, Balancete, Extrato ou Fechamento/Prestacao

## Limpeza segura de dados sinteticos na base local

- houve confirmacao de contaminacao local visivel na listagem real com padroes sinteticos vindos da frente de testes da listagem:
  - favorecido `P-LIST - Favorecido listagem`
  - conta `Conta listagem`
  - categorias `Receitas listagem`, `Contribuicao listagem` e `Livro listagem`
  - lancamentos `LIST-001`, `LIST-002`, `LIST-003` e grupo `grp-list-acoes`
  - usuario tecnico local `debug-list`
- o arquivo de backup `db.sqlite3_BACKUP_ANTES_LIMPEZA_TESTES.sqlite3` foi confirmado antes de qualquer remocao, mas a comparacao mostrou que ele ja continha a mesma contaminacao; portanto ele preserva o estado anterior a limpeza, nao um estado limpo
- consulta de leitura confirmou que os 4 lancamentos ativos do banco eram exatamente o conjunto sintetico suspeito, sem outros lancamentos financeiros no `db.sqlite3` atual
- a limpeza local foi executada em transacao unica e com filtros explicitos, removendo somente:
  - 4 `LancamentoFinanceiro` sinteticos
  - 1 `PessoaFinanceira` sintetica (`P-LIST`)
  - 1 `ContaFinanceira` sintetica (`Conta listagem`)
  - 3 `CategoriaFinanceira` sinteticas ligadas ao grupo de listagem
  - 1 usuario tecnico sintetico (`debug-list`)
- a primeira tentativa de limpeza foi revertida automaticamente por `ProtectedError` ao tentar apagar a categoria pai antes das filhas; a remocao final respeitou a ordem segura (filhas -> pai), sem efeito parcial
- dados reais preservados:
  - pessoas reais continuaram presentes na base (`358` apos a limpeza)
  - contas reais continuaram presentes (`11`)
  - categorias reais continuaram presentes (`71`)
  - a listagem abriu com `200` e deixou de exibir os padroes sinteticos removidos
- causa provavel: criacao manual/interativa de fixtures inspiradas em `financeiro/tests.py` fora do banco de teste; nao ha evidencia de falha do `manage.py test`, que continuou executando em base isolada
- nesta microetapa nao houve alteracao de codigo funcional; apenas limpeza local de dados confirmadamente sinteticos e registro documental do incidente

## Fechamento do incidente de banco local (diagnostico final validado)

- a conclusao final do incidente foi validada pela usuaria em diagnostico SQLite de leitura: o banco correto em uso e o `db.sqlite3` atual, com dados reais preservados
- contagens confirmadas no `db.sqlite3` atual:
  - `financeiro_lancamentofinanceiro = 2193`
  - `financeiro_pessoafinanceira = 358`
  - `financeiro_contafinanceira = 11`
  - `financeiro_categoriafinanceira = 71`
- comparacao consolidada dos candidatos locais:
  - `db.sqlite3`: banco real recuperado/confirmado e em uso correto no sistema
  - `db.sqlite3_BACKUP_ANTES_LIMPEZA_TESTES.sqlite3`: continha apenas 4 lancamentos sinteticos de teste
  - `db-Luciano.sqlite3`: continha 0 lancamentos e foi descartado como candidato de restauracao
- diretriz operacional consolidada para este incidente:
  - manter `db.sqlite3` atual como base correta
  - nao usar `db-Luciano.sqlite3` para restauracao
  - preservar o backup validado informado pela usuaria: `db.sqlite3_BACKUP_VALIDADO_2193_LANCAMENTOS.sqlite3`
- governanca reforcada:
  - nunca executar script/fixture manual em banco real sem backup previo
  - sempre gerar backup antes de diagnostico/limpeza local
  - manter execucao de testes no banco de teste isolado
- esta microetapa foi exclusivamente documental, sem alteracao de codigo, calculos, saldos, lancamentos ou relatorios

## Bloqueio de competencia mensal duplicada no mesmo lancamento

- a validacao de alocacao por competencia passou a bloquear duplicidade de `mes/ano` dentro do mesmo lancamento e da mesma subcategoria controlada
- a regra vale para:
  - lancamento simples com competencia
  - lancamento rateado com item/subcategoria controlada
  - edicao de grupo rateado no formulario especifico de rateio
- mensagem padrao adotada:
  - `Ja existe uma competencia informada para este mes/ano. Agrupe o valor em uma unica linha.`
- no rateio, a duplicidade e validada separadamente por subcategoria controlada; o mesmo `mes/ano` continua permitido em subcategorias controladas diferentes no mesmo grupo
- entre lancamentos diferentes, competencias iguais continuam permitidas; a matriz futura segue autorizada a somar esses valores por pessoa/subcategoria/competencia
- a validacao de soma permaneceu inalterada: depois de remover ambiguidades de duplicidade, a soma ainda precisa fechar com o valor controlado do lancamento simples ou da subcategoria controlada no rateio
- cobertura de testes reforcada para:
  - bloquear duplicidade em lancamento simples
  - permitir mesma competencia em lancamentos diferentes
  - bloquear duplicidade na mesma subcategoria controlada do rateio
  - permitir mesmo `mes/ano` em subcategorias controladas diferentes
  - bloquear duplicidade tambem no formulario de edicao do grupo rateado
- sem alteracao de calculo financeiro, saldos, relatorios, migrations ou banco real; nenhum arquivo SQLite foi alterado/versionado nesta etapa

## Ajuste da mensagem de soma com erro de linha em competencias

- a validacao de competencias foi ajustada para priorizar erros especificos de linha (mes/ano/valor invalidos, valor nao positivo ou duplicidade)
- quando existe erro de linha, a validacao agregada de soma nao e exibida para aquela mesma lista de competencias, evitando mensagem indevida
- regra aplicada em:
  - lancamento simples
  - lancamento com rateio controlado na criacao
  - edicao de grupo rateado
- quando todas as linhas estao validas, a validacao de soma continua obrigatoria e inalterada
- sem alteracao de calculo financeiro, saldos, relatorios ou banco real; nenhum arquivo SQLite foi alterado/versionado

## Primeira matriz mensal com valores por competencia

- implementada a tela `Frequencia por competencia` em `/financeiro/frequencia-competencias/`
- permissao reutilizada da camada de relatorios: `financeiro.resumo_financeiro.visualizar`
- fonte oficial dos dados:
  - `AlocacaoCompetenciaFinanceira`
  - nunca o valor bruto total do lancamento
  - nunca o valor total consolidado do grupo rateado
- filtros entregues:
  - competencia inicial (mes/ano)
  - competencia final (mes/ano)
  - subcategoria controlada (`Todas controladas` ou uma subcategoria)
  - status (`Todos`, `Quitados`, `Em aberto`)
- regra de leitura:
  - linhas = favorecidos recorrentes (`contribuinte_recorrente=True`), inclusive sem alocacao no periodo
  - colunas = todas as competencias mensais no intervalo selecionado
  - celulas = soma dos `valor_alocado` daquela pessoa na competencia
  - totais = por favorecido, por mes e geral
- consolidacoes entregues:
  - multiplos lancamentos da mesma pessoa na mesma competencia sao somados na celula
  - itens nao controlados do rateio permanecem fora da matriz
  - alocacao inconsistente ligada a favorecido nao recorrente fica ignorada no MVP
  - status `Todos` considera `quitado + aberto`; `cancelado` fica fora desta leitura inicial
- navegacao adicionada no grupo `Relatorios` do menu financeiro e na home secundaria do modulo
- limites iniciais:
  - periodo maximo de 24 competencias por consulta
  - matriz sem valores/check-X ainda nao implementada
  - termo por favorecido ainda nao implementado
  - sem exportacao e sem impressao refinada nesta microetapa
- sem alteracao de calculo financeiro, saldos, relatorios existentes, migrations ou banco real; nenhum arquivo SQLite foi alterado/versionado

## Refinamento da impressao da matriz de frequencia (cabecalho limpo + indicadores)

- impressao da matriz sem valores ajustada para preservar melhor a formatacao condicional dos indicadores:
  - `✓` positivo com tentativa de verde no print/PDF
  - `×` negativo com tentativa de vermelho no print/PDF
- aplicado `print-color-adjust: exact` e `-webkit-print-color-adjust: exact` no contexto de impressao, mantendo fallback legivel em preto e branco por simbolo e contraste
- cabecalho impresso da matriz ficou mais limpo e compacto:
  - removidos `Formato` e `Status`
  - mantidos `Periodo`, `Subcategoria` e `Emitido em`
  - `Subcategoria` passa a exibir nome legivel da selecionada; quando nao houver selecao especifica, exibe `Todas controladas`
- sem alteracao de regra de negocio da matriz, sem alteracao de fonte de dados (`AlocacaoCompetenciaFinanceira`), sem alteracao de calculo financeiro, saldos, relatorios existentes ou banco real

## Frente futura registrada - Assistente inteligente de competencias (UX)

- frente registrada como futura, sem implementacao nesta microetapa
- direcao funcional consolidada:
  - sugerir meses proximos (ultimos 5, mes atual e proximos 5)
  - mes sem valor alocado deve ser lido como `sem quitacao registrada` (nao como `em aberto` automatico)
  - mes com valor alocado deve aparecer como `ja quitado` / `ja possui contribuicao`
  - preenchimento de valor no mes deve ser o gatilho principal para incluir/quitar a competencia
  - checkbox nao deve ser obrigatorio quando o valor preenchido ja representa a competencia
  - modo manual atual permanece como base segura
  - complemento/observacao por competencia fica para SPEC propria
- governanca da frente:
  - nao implementar sem SPEC dedicada
  - qualquer evolucao deve ser tratada em microetapa propria por impactar formulario de lancamento e fluxo de rateio

## SPEC funcional consolidada - Assistente inteligente de competencias

- microetapa exclusivamente documental concluida para desenhar o MVP futuro do assistente, sem alteracao de codigo funcional
- objetivo do MVP futuro:
  - manter o modo manual atual de competencias como base segura
  - adicionar um bloco de `Sugestao rapida de competencias` sobre o fluxo ja existente
  - reaproveitar os mesmos payloads e validacoes atuais (`competencias_payload` e `competencias_rateio_payload`)
- regra de exibicao proposta:
  - lancamento simples: assistente aparece apenas quando houver favorecido recorrente + subcategoria controlada
  - rateio: assistente aparece apenas para cada subcategoria controlada do grupo
  - pessoa nao recorrente, subcategoria nao controlada e item nao controlado de rateio continuam sem assistente
- grade sugerida para o MVP:
  - ultimos 5 meses
  - mes atual
  - proximos 5 meses
- estados conceituais aprovados para a UX:
  - `sem quitacao registrada` = nao ha valor alocado previo naquela pessoa/subcategoria/competencia
  - `ja possui contribuicao` = ja existe valor alocado previo naquela pessoa/subcategoria/competencia
  - `informado neste lancamento` = usuario digitou valor no mes no formulario atual
- regra central preservada:
  - o valor preenchido no mes e o gatilho da competencia atendida
  - mes vazio nao entra no payload
  - valor zero ou negativo continua sujeito as validacoes ja existentes
  - a soma dos meses informados precisa continuar fechando com o valor controlado do lancamento ou da subcategoria controlada do rateio
- comportamento esperado no MVP:
  - lancamento simples: uma grade para a subcategoria controlada do lancamento
  - rateio: uma grade por subcategoria controlada do grupo, sem usar o valor bruto total do documento
  - edicao: carregar competencias ja salvas no mesmo bloco assistido/manual
  - lancamento antigo sem competencia: se em `Editar` o lancamento existente atender favorecido recorrente + subcategoria controlada, o assistente deve aparecer mesmo sem alocacoes ja salvas, com grade vazia pronta para regularizacao
  - clone: continua sem copiar competencias automaticamente
- decisao funcional recomendada para referencia visual:
  - mostrar no assistente o valor ja alocado anteriormente naquela competencia como apoio
  - ainda assim permitir novo valor no mes, pois a matriz futura soma multiplos lancamentos
- complemento desta SPEC para novo lancamento x edicao:
  - `ja registrado` = valor historico ja existente para aquela pessoa/subcategoria/competencia, em outros lancamentos ou como referencia consolidada
  - `valor deste lancamento` = campo editavel do lancamento atual; somente isso entra no payload atual
  - em edicao do proprio lancamento, o assistente deve carregar as competencias atuais do registro como base editavel
- redistribuicao em edicao:
  - a edicao de competencias existe para corrigir a distribuicao gerencial por competencia, sem alterar automaticamente o valor financeiro total do lancamento/subcategoria
  - a soma editada continua precisando fechar exatamente com o valor controlado do lancamento simples ou da subcategoria controlada do rateio
  - isso inclui lancamentos quitados ja existentes, desde que o sistema permita a edicao do lancamento; a redistribuicao afeta a leitura gerencial/matriz, nao cria novo valor financeiro
- comportamento esperado em lancamento quitado:
  - nao criar bloqueio novo nesta SPEC apenas por estar quitado
  - permitir ajuste das competencias como redistribuicao historica controlada
  - registrar como cuidado de UX que essa edicao altera a matriz historica e deve deixar claro o que ja estava salvo e o que esta sendo ajustado
- integracao tecnica consolidada para futura implementacao:
  - o assistente deve apenas montar/preencher os payloads atuais
  - nao deve criar nova fonte de dados nem novo fluxo de salvamento
  - validacoes de soma, duplicidade e rateio controlado devem continuar centralizadas no backend atual
- fora do MVP:
  - observacao/complemento por competencia
  - alteracao de model ou migration
  - modulo proprio de baixa
  - historico individual por competencia
  - alerta automatico
  - calculo de inadimplencia
  - importacao/exportacao de competencias
  - termo por favorecido
  - mudancas na matriz de frequencia
- riscos registrados para a futura implementacao:
  - confusao entre contribuicao anterior e contribuicao do lancamento atual
  - confusao entre `ja registrado` e `valor deste lancamento`
  - complemento em mes ja quitado ser confundido com duplicidade dentro do mesmo lancamento
  - usuario interpretar redistribuicao de competencias como alteracao do valor financeiro quitado
  - risco de poluicao visual excessiva no formulario
  - risco de quebrar o fechamento de soma do valor controlado
  - risco de quebrar o rateio controlado se o assistente fugir dos payloads atuais
  - risco de a UX reintroduzir leitura incorreta de `em aberto`
- proxima microetapa recomendada:
  - implementar o MVP do assistente no formulario de lancamento simples e no fluxo de rateio/edicao reaproveitando os payloads atuais e mantendo o modo manual visivel

## MVP implementado - Assistente inteligente de competencias

- microetapa funcional concluida sem alteracao de model, migration, calculos, saldos ou banco real
- o assistente foi implementado como camada visual de preenchimento sobre os payloads ja existentes:
  - `competencias_payload` no lancamento simples
  - `competencias_rateio_payload` no rateio controlado
- fluxos cobertos nesta entrega:
  - lancamento simples novo
  - edicao de lancamento simples
  - regularizacao de lancamento antigo sem competencia
  - rateio controlado novo
  - edicao de grupo rateado
- regra de exibicao implementada:
  - no simples, aparece apenas com favorecido recorrente + subcategoria controlada
  - no rateio, aparece apenas por subcategoria controlada
  - favorecido nao recorrente e subcategoria nao controlada continuam sem assistente
- grade sugerida implementada com 11 meses:
  - ultimos 5 meses
  - mes atual
  - proximos 5 meses
- leitura implementada na UX:
  - `Ja registrado` = referencia consolidada da mesma pessoa + subcategoria + competencia em outros lancamentos
  - `Valor deste lancamento` = campo editavel do lancamento/grupo atual
  - ausencia de registro continua como `Sem quitacao registrada`, sem uso de status `em aberto`
- em edicao, o assistente recarrega as competencias do proprio lancamento/grupo e permite redistribuicao entre meses sem alterar automaticamente o valor financeiro total; a soma continua precisando fechar com o valor controlado
- o modo manual permaneceu visivel e funcional como fallback; o assistente nao criou nova fonte de verdade nem novo fluxo de persistencia
- clone comum e clone de rateio continuam sem copiar competencias automaticamente
- cobertura automatizada reforcada para exibicao positiva e negativa do assistente, separacao entre `Ja registrado` e `Valor deste lancamento`, regularizacao de lancamento sem competencias e exibicao por subcategoria controlada no rateio

## Refino de UX - Assistente inteligente de competencias

- microetapa de refinamento concluida sem alteracao de model, migration, calculos, saldos ou banco real
- o assistente deixou de usar cards grandes e passou a usar lista/tabela compacta com quatro colunas:
  - `Mes`
  - `Situacao`
  - `Ja registrado`
  - `Valor deste lancamento`
- a mensagem orientativa foi suavizada:
  - simples: `Distribua o valor total entre as competencias. A soma informada deve fechar com o valor do lancamento.`
  - rateio: `Distribua o valor da subcategoria entre as competencias. A soma informada deve fechar com o valor da subcategoria.`
- o bug de foco foi corrigido removendo o re-render completo do assistente a cada tecla digitada; a sincronizacao passou a atualizar apenas:
  - as linhas manuais correspondentes
  - a serializacao do payload atual
- o modo manual continuou visivel e funcional como fallback
- os payloads continuam sendo:
  - `competencias_payload`
  - `competencias_rateio_payload`
- permanece pendente uma revisao visual mais ampla das secoes do formulario, pois ainda existe mistura visual entre blocos fora do escopo desta microetapa
