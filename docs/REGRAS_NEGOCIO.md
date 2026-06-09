# Regras de Negócio — Casa Espírita

Este documento consolida regras permanentes do sistema. Ele não substitui o histórico dos demais documentos; serve como referência rápida para evitar perda de memória.

## Governança

- O código representa o estado real do sistema.
- Os documentos em docs/ representam a memória oficial.
- O chat é apoio, mas não é fonte oficial permanente.
- Decisão aprovada deve ser registrada nos documentos.
- Execução realizada deve ser registrada em CODEX_RESULTADO.md.
- Mudança de estado deve ser registrada em STATE.md.
- Regra permanente deve ser registrada em CEREBRO_PROJETO.md ou neste documento.
- Toda regra de negócio aprovada deve ser registrada em `docs/REGRAS_NEGOCIO.md`; regra importante não deve permanecer apenas no chat.
- Uma regra de negócio reutilizável deve registrar comportamento esperado, exceções, impacto em cadastros, impacto em relatórios, racional da decisão e possibilidade de reaproveitamento em outros projetos.
- Quando uma regra tiver potencial de replicação para outros sistemas, deve ser descrita de forma estruturada e genérica o bastante para orientar futura reutilização, sem ficar presa apenas ao caso atual da Casa Espírita.

## Financeiro

- Não alterar cálculos financeiros sem pedido explícito.
- Cadastros do sistema não devem permitir duplicidade de identificadores-chave, como código, nome ou equivalentes, conforme a natureza de cada cadastro.
- Essa regra de identificadores-chave deve ser aplicada progressivamente por cadastro, sem presumir que todos os cadastros atuais já estejam endurecidos no mesmo nível.
- Separar receita, despesa e transferência.
- Transferências internas não devem inflar receitas ou despesas operacionais.
- Data de pagamento é a principal referência operacional, com fallback para competência quando aplicável.
- Rateios devem ser preservados.
- Conta destino deve ser obrigatória em transferências.
- Número de documento deve existir; quando não preenchido, deve ser gerado automaticamente conforme regra do sistema.
- Favorecido/pessoa financeira não deve permitir duplicidade por nome normalizado.
- Conta inativa não deve aparecer como opção para novos lançamentos; em filtros históricos, deve aparecer apenas quando tiver movimento no período/escopo selecionado.
- Conta ativa/inativa é regra operacional de uso em novos lançamentos; conta disponível/indisponível ou vinculada é regra gerencial/patrimonial de leitura do saldo.
- Uma conta pode estar ativa para uso operacional e, ainda assim, ter saldo total ou parcialmente indisponível/vinculado conforme sua natureza gerencial ou patrimonial.
- Valores vinculados ou indisponíveis não devem ser tratados como despesa operacional.
- Quando a modelagem de disponibilidade for implementada, valores vinculados/indisponíveis devem ser separados do saldo disponível operacional nos relatórios que apresentarem saldo livre.
- Integralização de capital é valor patrimonial/vinculado: não é despesa operacional, não deve ser somada ao saldo livre disponível sem destaque e deve compor o patrimônio financeiro fora do saldo operacional livre.
- A conta de integralização pode ser cadastrada normalmente como conta financeira; sua leitura futura como disponível ou indisponível/vinculada no Balancete patrimonial deve ser definida pelo campo `disponibilidade`.
- Para integralização que não pode ser movimentada até encerramento ou resgate, orientar o cadastro com tipo `Integralização de capital`, disponibilidade `Indisponível/vinculada` e mensagem opcional explicando a vinculação conforme regra da instituição.
- Em transferências exibidas no Extrato, quando não houver favorecido operacional, a apresentação do favorecido deve usar o texto padronizado "TRANSFERÊNCIA ENTRE CONTAS".
- Rateio deve preservar validação pelo valor total do documento e pode exibir saldo/diferença restante como apoio operacional ao usuário.

### Resultado operacional e composição de saldo

- Resultado operacional considera receitas e despesas, sem incluir transferências como receita ou despesa.
- Composição de saldo considera também transferências, porque transferência é movimentação entre contas.
- Transferência entre duas contas dentro do filtro selecionado é interna ao escopo: sai de uma conta, entra em outra e se anula no consolidado.
- Transferência com apenas a conta destino dentro do filtro compõe o saldo como entrada por transferência.
- Transferência com apenas a conta origem dentro do filtro compõe o saldo como saída por transferência.
- O Extrato multi-contas deve usar a mesma regra de escopo de contas para saldo anterior, movimentos do período e saldo final.
- A listagem de lançamentos com filtro multi-contas deve exibir lançamentos reais quando a conta origem ou a conta destino estiver no conjunto selecionado; transferências internas entre contas selecionadas também devem aparecer na listagem.
- No Fechamento do período / Prestação de contas, transferências internas ao escopo selecionado não precisam aparecer como entrada/saída nem como linha zerada; totais zerados de transferências externas ao escopo também não devem aparecer.
- Transferências com apenas uma ponta dentro do filtro devem aparecer nos totais necessários de entrada/saída por transferência para explicar a reconciliação do saldo.
- A opção "Exibir transferências" controla somente detalhamento analítico/visual das transferências; não controla a inclusão das transferências no cálculo real do saldo.
- O Balancete Institucional deve reutilizar a mesma regra/base de cálculo da Prestação/Fechamento, sem cálculo divergente para saldos, receitas, despesas e transferências por escopo.

### Balancete patrimonial, tipo de conta e disponibilidade

- A evolução patrimonial do Balancete deve alterar leitura, classificação e apresentação do saldo, não a regra original de lançamentos, receitas, despesas, transferências ou cálculo financeiro.
- A frente deve ser modelada documentalmente antes de qualquer implementação de models, migrations, formulários, views ou templates.
- Tipos iniciais de conta a considerar: conta corrente, conta poupança, dinheiro/caixa, conta investimento, integralização de capital, conta vinculada/indisponível e outros.
- O tipo de conta deve permitir agrupamento gerencial: contas do mesmo tipo podem ser somadas independentemente do banco, nome ou cadastro individual da conta.
- No MVP patrimonial, tipo de conta financeira é cadastro próprio simples, e não lista fixa no código, para permitir adaptação a outras instituições, empresas e projetos futuros.
- No MVP patrimonial, disponibilidade/vinculação é total por conta: uma conta é classificada como disponível ou indisponível/vinculada em seu saldo total.
- Disponibilidade parcial fica fora do MVP e permanece como evolução futura, pois exigiria modelagem mais complexa de parcelas de saldo.
- A mensagem explicativa de indisponibilidade/vinculação ficará no cadastro da conta; se vazia, nada deve aparecer no Balancete; se preenchida, poderá aparecer no Balancete patrimonial ou relatório equivalente.
- O modo padrão do Balancete patrimonial será detalhado por conta, preservando a leitura atual e adicionando separação visual entre disponível e indisponível/vinculado quando aplicável.
- No recorte inicial já implementado, o Balancete Institucional separa a composição final entre saldo disponível operacional e saldo indisponível/vinculado sem alterar cálculo, saldo por conta ou reconciliação.
- O saldo total financeiro do Balancete deve continuar igual à composição final já calculada pela base compartilhada; a separação patrimonial é apenas classificatória.
- No Balancete, a diferenca pratica de leitura deve ser controlada diretamente pelos filtros de composicao do saldo e exibicao de vinculadas/indisponiveis, sem depender de filtros redundantes de modelo do relatorio ou detalhamento separado do saldo inicial.
- Quando contas vinculadas/indisponiveis forem ocultadas na composicao patrimonial, o documento deve deixar claro que a composicao exibida representa apenas o saldo disponivel operacional.
- Quando contas vinculadas/indisponiveis forem ocultadas, o Balancete nao deve exibir aviso textual chamando atencao para a ocultacao; a diferenca deve aparecer apenas na propria composicao apresentada e nos rotulos aplicados.
- Quando contas vinculadas/indisponiveis estiverem ocultas no Balancete, o documento inteiro deve representar o universo disponivel operacional: saldo indisponivel, contas indisponiveis e mensagens explicativas dessas contas nao aparecem em nenhuma parte do relatorio.
- Nesse modo de saldo disponivel operacional, transferencias de conta disponivel para conta vinculada/indisponivel devem aparecer no resumo como `Transferencias para saldo vinculado/indisponivel`, e o movimento inverso deve aparecer como `Transferencias de saldo vinculado/indisponivel para disponivel`; essas linhas nao viram receita nem despesa operacional.
- Quando contas vinculadas/indisponiveis estiverem exibidas, o Balancete continua representando o saldo financeiro total, com leitura patrimonial completa e mensagens explicativas apenas para contas efetivamente mostradas.
- Os filtros de composicao e exibicao de vinculadas/indisponiveis nao devem aparecer como metadados no cabecalho impresso do Balancete.
- O mesmo modo de composicao do Balancete deve valer para o saldo inicial e para o saldo final: se a leitura for por conta, as duas pontas devem ser por conta; se for por tipo, as duas pontas devem ser por tipo; se for consolidada, as duas pontas devem ser consolidadas.
- A sequencia documental do Balancete deve seguir a ordem: saldo inicial financeiro, entradas do periodo, saidas do periodo, resumo operacional do periodo, composicao do saldo final e assinaturas.
- A proxima arquitetura funcional do Balancete deve ser orientada por `Formato do Balancete`, com tres opcoes: `Operacional`, `Operacional + patrimonio vinculado` e `Financeiro completo`.
- Filtros complementares do Balancete devem ser dependentes do formato selecionado; o sistema nao deve exibir filtros que nao fazem sentido para o formato ativo.
- No formato `Operacional`, o relatorio representa apenas o universo disponivel; no formato `Operacional + patrimonio vinculado`, o bloco patrimonial deve vir separado do resumo operacional; no formato `Financeiro completo`, a leitura deve ser total da instituicao.
- O filtro antigo de exibir/ocultar vinculadas nao deve permanecer como controle principal da experiencia; quando houver necessidade de patrimonio vinculado no Balancete, a intencao do usuario deve ser definida pelo `Formato do Balancete`.
- No estado aprovado pela usuaria, o Balancete fica orientado por `Formato do Balancete` com tres opcoes (`Operacional`, `Operacional + patrimonio vinculado`, `Financeiro completo`) e o filtro `Detalhar patrimonio vinculado` deve aparecer apenas no formato `Operacional + patrimonio vinculado`.
- A logica funcional/UX aprovada do Balancete deve ser tratada como congelada no recorte atual; novos refinamentos dessa frente exigem nova decisao explicita da usuaria antes de qualquer implementacao.
- O Balancete deve poder exibir a composição do saldo em modos distintos:
  - detalhado por conta, mostrando cada conta individualmente;
  - consolidado por tipo de conta, somando contas do mesmo tipo;
  - total consolidado, mostrando apenas o total geral quando o relatório precisar ser sintético;
  - separado entre disponível e indisponível/vinculado, distinguindo saldo livre operacional de valores patrimoniais ou vinculados.
- No modo consolidado por tipo, integralização de capital, contas investimento e contas vinculadas/indisponíveis devem aparecer separadas quando existirem, para não poluir nem distorcer a leitura do saldo livre.
- O comportamento padrão atual do Balancete não deve ser refeito do zero: o MVP permanece base entregue, e a evolução patrimonial deve nascer como modelagem incremental.

## Relatórios e impressão

- Ajuste visual não deve alterar cálculo.
- Preservar cabeçalho institucional.
- Garantir legibilidade em tela e impressão.
- Cuidar de margens, quebras de página e continuidade entre páginas.

## UX

- Preservar o padrão analítico já validado.
- Primeiro consolidar o padrão em uma tela, depois propagar.
- Não misturar melhoria visual com mudança de regra de negócio.

## Importação

- Não perder o dado original.
- Apontar inconsistências com orientação clara.
- Transferências devem ser tratadas como movimentação entre contas.
- Categorias e favorecidos não devem ser generalizados sem validação.
- Importacoes financeiras por planilha devem manter politica all-or-nothing: se qualquer linha ou campo estiver invalido, nada deve ser gravado.
- Nova importacao operacional deve ocorrer apenas em dominio vazio; se o dominio ja tiver registros, o sistema deve bloquear a carga e orientar reset/limpeza controlada.
- O fluxo comum de importacao de lancamentos aceita lancamentos simples, transferencias simples e rateio em ate 5 blocos na mesma linha; rateios maiores devem seguir caminho tecnico proprio ate existir modelagem funcional especifica.
- Em importações por planilha, duplicidade de linha/código deve ser distinguida de conflito cadastral contra regras permanentes do cadastro.
- Uma linha de cadastro importada só deve ser tratada como duplicada quando o código for igual a outro já cadastrado/repetido na planilha ou quando todos os dados relevantes coincidirem com cadastro/linha existente.
- Quando a linha não for duplicada por esses critérios, mas violar regra permanente de cadastro, como nome normalizado já existente com código diferente, o erro deve ser tratado como conflito cadastral.

## Frequencia por competencia (MVP futuro)

- O controle de frequencia por competencia nao deve usar checkbox puro como fonte principal, pois checkbox nao representa valor por competencia nem cobre pagamento parcial/multicompetencia.
- A unidade minima de controle deve ser uma alocacao de competencia com: mes/ano da competencia e valor alocado.
- A matriz com valores e a fonte principal de leitura gerencial; a matriz sem valores deve ser derivada dela (presenca/ausencia por competencia).
- O dinheiro continua vindo do lancamento financeiro; a camada de competencia e detalhamento gerencial/documental do mesmo fato financeiro.
- O controle deve ser generico por subcategoria: so entram na frequencia lancamentos (ou partes do rateio) cuja subcategoria esteja marcada como controla frequencia.
- Pessoa/favorecido recorrente define expectativa de presenca na matriz; pessoa nao recorrente nao entra como esperada no relatorio.
- No recorte cadastral minimo ja entregue, a marcacao de recorrencia fica em `PessoaFinanceira.contribuinte_recorrente`, com default `False` para preservar base existente.
- Em lancamento simples, se a subcategoria controlar frequencia, a alocacao de competencia usa apenas o valor desse lancamento/subcategoria.
- Na primeira implementacao funcional da alocacao, o formulario de lancamento exige `Competencias atendidas` apenas quando houver favorecido recorrente + subcategoria controlada em lancamento simples.
- Cada competencia atendida deve registrar `mes/ano + valor`, e a soma das alocacoes precisa ser igual ao valor controlado do lancamento.
- Em lancamento com rateio, a frequencia nao pode usar automaticamente o valor total do documento: so entra o valor do item de rateio vinculado a subcategoria que controla frequencia.
- No rateio implementado, a soma das competencias deve fechar por subcategoria controlada do grupo, e nao pelo valor bruto total do documento.
- Itens nao controlados do mesmo rateio continuam fora da frequencia e nao recebem alocacao de competencia.
- No recorte cadastral minimo ja entregue, a marcacao de subcategoria controlada fica em `CategoriaFinanceira.controla_recorrencia_competencia`, com default `False` para nao incluir subcategorias antigas automaticamente.
- Itens do mesmo recebimento com subcategorias nao recorrentes (livro, camisa, doacao avulsa etc.) ficam fora da frequencia, mesmo quando o favorecido for recorrente.
- Multiplos lancamentos para a mesma pessoa/subcategoria/competencia devem ser somados na matriz; nao devem ser bloqueados automaticamente como duplicidade.
- Dentro do mesmo lancamento e da mesma subcategoria controlada, mes/ano de competencia duplicado deve ser bloqueado para evitar ambiguidade de leitura.
- A validacao de duplicidade vale tanto para lancamento simples quanto para rateio controlado, sempre no escopo da mesma subcategoria controlada.
- Mensagem adotada para essa validacao:
  - `Ja existe uma competencia informada para este mes/ano. Agrupe o valor em uma unica linha.`
- Na primeira matriz mensal com valores, a fonte oficial de leitura e `AlocacaoCompetenciaFinanceira`, nunca o valor bruto total do lancamento ou do grupo rateado.
- A matriz com valores deve listar favorecidos recorrentes mesmo sem alocacao no periodo, para evidenciar meses vazios; favorecido nao recorrente fica fora por padrao no MVP.
- As colunas da matriz devem ser geradas por competencia mensal explicita no intervalo selecionado, e as celulas devem somar os valores alocados daquela pessoa na mesma competencia.
- A primeira versao da matriz aceita filtro por competencia inicial/final, subcategoria controlada e status do lancamento (`Todos`, `Quitados`, `Em aberto`).
- No filtro de status da matriz, `Todos` considera apenas `quitado` e `aberto`; `cancelado` fica fora da leitura gerencial desta tela.
- A matriz sem valores deve ser apenas uma visualizacao derivada da matriz com valores: contribuicao existente (`valor_alocado > 0`) vira indicador positivo, ausencia de contribuicao vira indicador negativo.
- No modo sem valores, o total por favorecido deve contar competencias com contribuicao no periodo, o total por mes deve contar favorecidos com contribuicao naquela competencia e o total geral deve contar ocorrencias positivas na matriz.
- A impressao da matriz deve reaproveitar o mesmo contrato documental dos relatorios do modulo, mantendo a mesma fonte `AlocacaoCompetenciaFinanceira` e sem abrir nova regra de negocio para frequencia.
- No impresso da matriz, a prioridade e tentar acomodar o maior numero possivel de competencias na mesma pagina por meio de compactacao visual, sem prometer pagina unica perfeita para qualquer periodo dentro do limite funcional.
- No impresso da matriz, as competencias devem usar cabecalho compacto `MM/AAAA`, e a coluna `Favorecido` deve permanecer legivel, com protecao contra quebra letra por letra.
- Na leitura da frequencia por competencia, ausencia de valor alocado em um mes nao deve ser tratada automaticamente como status `em aberto`; deve ser lida como `sem quitacao registrada`.
- Para a frente futura de assistencia de competencias, o preenchimento de valor no mes deve ser o gatilho principal da competencia atendida/quitada, sem dependencia obrigatoria de checkbox.
- Na futura UX assistida de competencias, o assistente deve aparecer apenas quando houver favorecido recorrente e subcategoria controlada; fora desse contexto, o fluxo atual/manual deve permanecer inalterado.
- Na futura UX assistida de competencias, o assistente do rateio deve operar por subcategoria controlada e nunca pelo valor bruto total do documento.
- Na futura UX assistida de competencias, a grade padrao recomendada de sugestao deve cobrir ultimos 5 meses, mes atual e proximos 5.
- Na futura UX assistida de competencias, `sem valor alocado` deve ser lido como `sem quitacao registrada`, e nao como `em aberto` automatico.
- Na futura UX assistida de competencias, `valor alocado existente` deve ser lido como `ja possui contribuicao` / `ja quitado`, sem impedir novo complemento em outro lancamento.
- Na futura UX assistida de competencias, ao editar lancamento existente que atenda favorecido recorrente + subcategoria controlada, o assistente deve aparecer mesmo se ainda nao houver nenhuma competencia salva, permitindo regularizacao do proprio lancamento.
- Na futura UX assistida de competencias, editar competencias de um lancamento existente tem funcao de redistribuicao gerencial da competencia e nao deve alterar automaticamente o valor financeiro total do lancamento/subcategoria.
- Na futura UX assistida de competencias, essa redistribuicao pode ocorrer tambem em lancamento quitado, desde que o fluxo atual permita a edicao do lancamento; o cuidado deve ser deixar claro que a alteracao afeta a leitura historica da matriz.
- Na futura UX assistida de competencias, a interface deve diferenciar claramente `Ja registrado` (referencia historica/consolidada) de `Valor deste lancamento` (campo editavel do formulario atual).
- Na futura UX assistida de competencias, o assistente deve ser apenas camada de preenchimento dos payloads atuais (`competencias_payload` e `competencias_rateio_payload`), sem criar nova fonte de persistencia nem duplicar validacoes.
- Na futura UX assistida de competencias, o modo manual atual deve continuar disponivel como base segura e fallback operacional.
- No MVP implementado do assistente de competencias, a grade sugerida padrao deve cobrir exatamente 11 meses (ultimos 5, mes atual e proximos 5), tomando `data_competencia` como referencia principal e `data_pagamento`/data atual apenas como fallback tecnico.
- No MVP implementado do assistente de competencias, `Ja registrado` serve apenas como referencia historica consolidada da mesma pessoa + subcategoria + competencia e nao pode entrar automaticamente no payload do lancamento atual.
- No MVP implementado do assistente de competencias, `Valor deste lancamento` e o campo editavel que alimenta o payload atual; se vazio, nao entra; se positivo, entra e segue sujeito as validacoes backend ja existentes.
- No MVP implementado do assistente de competencias, o assistente deve aparecer em edicao mesmo para lancamento antigo sem competencias salvas, desde que o registro atenda favorecido recorrente + subcategoria controlada.
- No MVP implementado do assistente de competencias, a redistribuicao de competencias em edicao simples ou rateada nao altera automaticamente o valor financeiro total do registro; apenas reorganiza a leitura gerencial por competencia, mantendo a soma fechada contra o valor controlado.
- No MVP implementado do assistente de competencias, o rateio assistido deve abrir uma grade independente para cada subcategoria controlada do grupo e ignorar itens nao controlados.
- No refinamento de UX do assistente de competencias, a apresentacao visual prioritara lista/tabela compacta com `Mes`, `Situacao`, `Ja registrado` e `Valor deste lancamento`, evitando cards extensos e repeticao de texto por mes.
- No refinamento de UX do assistente de competencias, a mensagem de orientacao deve ser instrutiva e nao soar como erro antecipado:
  - simples: `Distribua o valor total entre as competencias. A soma informada deve fechar com o valor do lancamento.`
  - rateio: `Distribua o valor da subcategoria entre as competencias. A soma informada deve fechar com o valor da subcategoria.`
- No refinamento de UX do assistente de competencias, a digitacao nos campos mensais nao deve provocar perda de foco; a sincronizacao precisa atualizar apenas as linhas/payloads necessarios sem reconstruir o bloco inteiro a cada tecla.
- Em clone comum, competencias existentes nao devem ser copiadas automaticamente para o novo lancamento.
- Em clone de rateio, competencias tambem nao devem ser copiadas automaticamente para evitar duplicidade de quitacao por competencia.
- No MVP inicial, nao abrir modulo separado de baixa; manter o fluxo no proprio lancamento e tratar termo por favorecido como segunda onda apos validacao da matriz.
- Alocacoes de competencia vinculadas ao lancamento/linha controlada seguem exclusao por cascade; qualquer necessidade de restauracao futura deve ser tratada na frente de auditoria acionavel, nao na regra atual de competencias.
- Subcategoria pode ter centro de custo padrao para sugerir preenchimento automatico no lancamento, sem impedir alteracao manual pelo usuario.
- Em lancamento rateado, o centro de custo deve ser informado por linha do rateio. A subcategoria da linha pode sugerir um centro de custo padrao, mas o usuario pode alterar manualmente antes de salvar.
- `Contribuinte recorrente` pode ser alternado por atalho apenas na tela de favorecidos, respeitando a permissao de edicao e usando POST com CSRF.
- No assistente de competencias, `Ja registrado` e referencia historica externa; `Valor deste lancamento` e o valor editavel do documento atual; `Total apos lancamento` e apenas leitura de apoio.
- Em rateio, o assistente de competencias opera por linha controlada. Linhas nao controladas ficam fora do assistente e da validacao.
- Quando uma regra automatica por descricao e aplicada no formulario de lancamento, ela prevalece sobre o rascunho restaurado pelo botao `+` e deve preencher/sobrescrever todos os campos que a propria regra possui, sem restaurar `numero_documento`.
- Extrato Financeiro pode ser exportado em XLSX respeitando os mesmos filtros e a mesma regra de calculo da tela, sem calculo paralelo divergente.
- A tela de edicao de lancamento deve manter os mesmos atalhos de cadastro rapido da criacao para os cadastros auxiliares aplicaveis, preservando o retorno ao proprio formulario.
- O historico de um documento/lancamento deve ser consultado a partir da `AuditoriaFinanceiro` existente, filtrado por `modelo=LancamentoFinanceiro` e `registro_id` do lancamento, sem misturar eventos de outros modelos com o mesmo ID.
- Em Tabelas personalizadas, a visualizacao operacional principal da tabela deve mostrar por padrao apenas colunas `ativas` e `visiveis` e apenas linhas `ativas`.
- Em Tabelas personalizadas, remocao operacional de linhas e colunas deve priorizar acoes seguras por status/visibilidade (`Ocultar`, `Mostrar`, `Inativar`, `Reativar`, `Arquivar`) via `POST` com CSRF, evitando exclusao fisica destrutiva como acao principal.
- Nas telas de estrutura/preenchimento de Tabelas personalizadas, titulo e subtitulo contextual nao podem ficar sobrepostos visualmente.
- Em Tabelas personalizadas, coluna `formula_controlada` pode usar totalizador apenas quando a formula estiver valida e habilitada e o `resultado_tipo` for `decimal` ou `monetario`; o totalizador deve operar sobre o resultado calculado em leitura, sem persistencia nova de valor calculado.
- Tabelas personalizadas possuem acoes seguras de status/visibilidade para uso cotidiano e tambem acao secundaria de exclusao definitiva para linhas e colunas, sempre via POST, com confirmacao e aviso de perda de dados vinculados.
- Em Tabelas personalizadas, a escolha de colunas mostradas na tela e na impressao e temporaria e nao altera a configuracao estrutural `visivel` da coluna.
- Em Tabelas personalizadas, a coluna de sistema `Linha / identificacao` faz parte apenas da visualizacao e pode ser mostrada ou ocultada temporariamente sem alterar a estrutura da tabela.
- Em Tabelas personalizadas, a ordenacao manual da tela e temporaria, nao altera o campo `ordem` salvo das linhas e deve ser aplicada depois de busca/filtros e antes da impressao.
- Em Tabelas personalizadas, a impressao deve respeitar o mesmo recorte atualmente exibido na tela: filtros, busca, status de linhas e colunas temporariamente selecionadas.
- Em Tabelas personalizadas, a exportacao XLSX continua disponivel e pode respeitar a mesma selecao temporaria de colunas da visualizacao quando esse recorte estiver ativo.
