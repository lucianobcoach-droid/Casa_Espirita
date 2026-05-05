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
