# ROADMAP FINANCEIRO

Data: 2026-03-26

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

### Extrato e saldo
- saldo inicial por conta
- saldo atual calculado
- extrato por conta
- saldo anterior por periodo

### Importacao de historico
- importacao de planilha historica
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

### Melhorias de UX ja feitas
- autocomplete real com busca por contem
- comportamento condicional do formulario de lancamento
- historico simples com os ultimos 5 lancamentos do favorecido no formulario de lancamento
- recibo em HTML imprimivel a partir do lancamento, com refinamentos posteriores de conteudo, assinatura, configuracao institucional e impressao
- mensagens de erro mais claras em campos obrigatorios
- layout mais compacto nas tabelas
- impressao refinada para extrato e prestacao de contas
- menu proprio para extratos, resumo e prestacao de contas

## 3. O que ja existe, mas ainda pode ser refinado

- comportamento de transferencia em todas as telas e relatorios
- UX do formulario de lancamento em casos limite
- evolucao futura do rateio para edicao coordenada em bloco, ainda nao implementada, mas ja com estrategia aprovada de view e formulario proprios do grupo
- modelagem documental mais rica do rateio, se necessario em etapa posterior
- acabamento operacional do rateio em edicao individual e leitura do grupo nas telas ja existentes
- estrategia aprovada para futura edicao coordenada do grupo rateado com view e formulario proprios, dados comuns em bloco e salvamento transacional
- regularizacao eventual de bases antigas de rateio sem `grupo_rateio` valido, caso precisem entrar na leitura consolidada do extrato
- revisao operacional futura da obrigatoriedade estrutural de `data_pagamento`, caso o comportamento hoje consolidado no formulario precise subir para nivel de modelagem
- expansao futura da auditoria de alteracoes no financeiro para alem de `LancamentoFinanceiro`, ampliando o que ja existe para outras entidades do modulo e mantendo model proprio sem `signals`
- refinamentos futuros de leitura para a tela de auditoria de `LancamentoFinanceiro`, alem dos filtros simples ja implementados
- consistencia visual do tratamento de transferencia
- validacoes defensivas adicionais em fluxos operacionais
- extrato com mais contexto operacional sem poluir a tela
- filtros da listagem de lancamentos com melhorias de usabilidade
- impressao da prestacao de contas com acabamento mais formal

## 4. O que ainda falta implementar

### Alta prioridade
- historico por favorecido
- relatorio anual por favorecido
- termo anual de quitacao
- contratos a pagar e a receber
- parcelas
- recorrencia
- anexos de comprovantes

### Media prioridade
- balancete padrao
- importacao de planilha historica
- cadastro rapido de pessoa dentro do lancamento
- cadastro rapido de categoria dentro do lancamento
- evolucoes futuras especificas do bloco de recibos ja entregue

## 5. Proximas etapas sugeridas

1. consulta historica por favorecido
2. relatorio anual por favorecido
3. contratos previstos a pagar e a receber
4. parcelas e recorrencia
5. anexos de comprovantes
6. balancete padrao
7. importacao historica
8. evolucoes futuras especificas do bloco de recibos ja entregue

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
