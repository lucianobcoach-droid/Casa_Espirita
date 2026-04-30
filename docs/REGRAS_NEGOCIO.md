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
- Valores vinculados ou indisponíveis não devem ser tratados como despesa operacional.
- Quando a modelagem de disponibilidade for implementada, valores vinculados/indisponíveis devem ser separados do saldo disponível operacional nos relatórios que apresentarem saldo livre.
- Integralização de capital é exemplo de valor patrimonial/vinculado: não é despesa operacional e não deve ser somada ao saldo livre disponível sem destaque.
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
- O Balancete Institucional futuro deve reutilizar a mesma regra/base de cálculo da Prestação/Fechamento, sem cálculo divergente para saldos, receitas, despesas e transferências por escopo.

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
