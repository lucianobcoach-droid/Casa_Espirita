# CODEX_RESULTADO

Data: 2026-03-23

## Entrega realizada

Foi executada a etapa incremental do extrato por conta com filtro por período e cálculo de saldo anterior, sem alterar o domínio além do necessário.

Complemento incremental posterior:

- saldo real das contas passou a considerar apenas lançamentos quitados
- o extrato por conta passou a listar apenas lançamentos quitados
- o saldo anterior do extrato por período passou a considerar apenas lançamentos quitados anteriores ao período
- a camada visual do financeiro foi refinada sem alterar regra de negócio
- tipos de lançamento passaram a ter destaque visual discreto
- tabelas priorizadas ficaram mais compactas e preparadas para impressão
- o financeiro passou a ter menu próprio `Extratos` com filtro por conta e período
- o financeiro passou a ter tela própria de `Resumo` consolidado por período
- o financeiro passou a ter tela própria de `Prestacao de Contas` por período
- `Resumo` e `Prestacao de Contas` passaram a aceitar seleção de contas para compor o relatório
- `Resumo` e `Prestacao de Contas` passaram a mostrar agrupamento por categoria
- `Resumo` e `Prestacao de Contas` passaram a mostrar agrupamento de despesas por centro de custo
- `Resumo` e `Prestacao de Contas` passaram a aceitar controle de exibição apenas para o bloco de centro de custo
- a `Prestacao de Contas` passou a ter refinamento específico de impressão
- a `Prestacao de Contas` passou a ter visual mais formal e menos aparência de dashboard

## Filtro por período

O extrato agora aceita por GET:

- `data_inicial`
- `data_final`

Sem filtro:

- mantém o extrato completo
- começa em `saldo_inicial`

Com filtro:

- lista apenas lançamentos do período
- calcula `saldo_anterior` até o dia anterior ao início informado
- inicia o saldo acumulado do período a partir desse valor

## Regra do saldo anterior

O `saldo_anterior` é calculado assim:

- começa em `saldo_inicial`
- soma receitas anteriores
- subtrai despesas anteriores
- subtrai transferências em que a conta é origem
- soma transferências em que a conta é destino

## Arquivos alterados nesta etapa

- `financeiro/views.py`
- `financeiro/templates/financeiro/conta_extrato.html`
- `docs/CEREBRO_PROJETO.md`
- `docs/STATE.md`
- `docs/CODEX_RESULTADO.md`

## Resultado prático

- o extrato continua funcionando sem filtro
- o extrato aceita filtro por período
- o saldo anterior aparece quando há `data_inicial`
- o saldo acumulado do período parte corretamente do saldo anterior
- transferências continuam coerentes na conta de origem e na conta de destino
- lançamentos não quitados deixaram de afetar saldo real e extrato
- o extrato, a listagem de lançamentos e a listagem de contas ficaram mais legíveis e mais compactos
- o extrato passou a ter visual mais limpo, com texto colorido sem badge no template de extrato
- o resumo consolidado mostra saldo inicial, receitas, despesas, saldo do período e saldo final
- transferências internas ficaram neutras no resumo consolidado
- a prestação de contas organiza o período em blocos formais e mostra a composição do saldo final por conta
- os cálculos dessas duas telas passaram a respeitar apenas as contas selecionadas
- `LancamentoFinanceiro` passou a usar obrigatoriedade condicional por tipo
- `receita` e `despesa` exigem `pessoa` e `categoria`
- `transferencia` não exige `pessoa`, `categoria` nem `centro_custo`
- em `transferencia`, o formulário limpa campos irrelevantes e mantém `conta_destino` como campo necessário
- o formulário passou a mostrar melhor a obrigatoriedade dinâmica de `conta`, `pessoa`, `categoria` e `conta_destino`
- a camada correta para erro de validação voltou a ser o formulário/model, desde que a migration `0006` esteja aplicada no banco
- `numero_documento` passou a ser gerado automaticamente quando o usuário deixa o campo vazio
- o extrato por conta passou a exibir `numero_documento` de forma discreta junto da descrição
- `data_pagamento` passou a ser validada contra `data_competencia` antes de salvar
- a listagem de lançamentos passou a mostrar `Transferência entre Contas` quando a transferência não tiver `pessoa`
- a listagem de lançamentos deixou de mostrar textos auxiliares redundantes em valor, conta e conta destino
- lançamentos sem categoria passaram a ser mostrados no agrupamento como `Sem categoria`
- despesas sem centro de custo passaram a ser mostradas no agrupamento como `Sem centro de custo`
- os filtros de exibição dos agrupamentos não alteram totais gerais de receitas, despesas, saldo inicial, saldo final ou resumo do período
- a visualização impressa da prestação de contas ficou mais próxima de um documento formal e ganhou bloco simples de assinatura
- receitas e despesas da prestação passaram a aparecer apenas na forma consolidada por categoria
