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
- Separar receita, despesa e transferência.
- Transferências internas não devem inflar receitas ou despesas operacionais.
- Data de pagamento é a principal referência operacional, com fallback para competência quando aplicável.
- Rateios devem ser preservados.
- Conta destino deve ser obrigatória em transferências.
- Número de documento deve existir; quando não preenchido, deve ser gerado automaticamente conforme regra do sistema.

### Resultado operacional e composição de saldo

- Resultado operacional considera receitas e despesas, sem incluir transferências como receita ou despesa.
- Composição de saldo considera também transferências, porque transferência é movimentação entre contas.
- Transferência entre duas contas dentro do filtro selecionado é interna ao escopo: sai de uma conta, entra em outra e se anula no consolidado.
- Transferência com apenas a conta destino dentro do filtro compõe o saldo como entrada por transferência.
- Transferência com apenas a conta origem dentro do filtro compõe o saldo como saída por transferência.
- O Extrato multi-contas deve usar a mesma regra de escopo de contas para saldo anterior, movimentos do período e saldo final.
- No Fechamento do período / Prestação de contas, transferências internas ao escopo selecionado não precisam aparecer como entrada/saída nem como linha zerada; totais zerados de transferências externas ao escopo também não devem aparecer.
- Transferências com apenas uma ponta dentro do filtro devem aparecer nos totais necessários de entrada/saída por transferência para explicar a reconciliação do saldo.
- A opção "Exibir transferências" controla somente detalhamento analítico/visual das transferências; não controla a inclusão das transferências no cálculo real do saldo.

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
