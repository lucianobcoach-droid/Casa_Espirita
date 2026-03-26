# CEREBRO DO PROJETO - CASA ESPIRITA

## 1. Objetivo deste arquivo
Este documento e a fonte principal de contexto funcional e operacional do projeto.
Antes de qualquer implementacao, leitura tecnica ou alteracao estrutural, ele deve ser lido junto com:
- `docs/STATE.md`
- `docs/CODEX_RESULTADO.md`
- `docs/ROADMAP_FINANCEIRO.md`

Se houver divergencia entre pedido atual, conversa e estado real do repositorio, a implementacao deve parar e a divergencia deve ser informada antes de codificar.

O arquivo `docs/ROADMAP_FINANCEIRO.md` consolida o escopo financeiro ja entregue, os refinamentos possiveis e as proximas etapas sugeridas, sem alterar o que ja foi aprovado.

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
- o formulario de lancamento agora pode exibir os ultimos 5 lancamentos do favorecido selecionado, sem quebrar o autocomplete atual
- cada lancamento agora pode gerar recibo proprio em HTML imprimivel, com bloco simples de assinatura

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
- `transferencia` nao exige `pessoa`
- `transferencia` nao exige `categoria`
- `transferencia` nao exige `centro_custo`
- em `transferencia`, `conta_destino` continua obrigatoria
- erros de obrigatoriedade do lancamento devem aparecer no formulario, sem estourar erro de banco
- `numero_documento` continua opcional para o usuario, mas deve ser gerado automaticamente quando vier vazio
- `numero_documento` nao pode se repetir em outro lancamento
- se o usuario informar manualmente um `numero_documento` ja existente, o erro deve aparecer no formulario
- a validacao de duplicidade deve funcionar no cadastro e na edicao
- na edicao, o proprio registro nao deve ser tratado como duplicado dele mesmo
- `data_pagamento` nao pode ser anterior a `data_competencia`
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

## 14. Etapas futuras ja pensadas, mas nao autorizadas agora
As etapas abaixo podem existir no planejamento, mas nao devem ser implementadas antes da hora:

- historico por favorecido
- relatorio anual por favorecido
- contratos a pagar e a receber
- parcelas e recorrencia
- anexos de comprovantes
- balancete padrao
- importacao de planilha historica
- recibos

## 15. Como este arquivo deve ser mantido
Este arquivo deve ser atualizado sempre que houver:
- nova regra de negocio validada
- mudanca estrutural aprovada
- mudanca da branch principal de trabalho
- conclusao de etapa relevante
- nova restricao tecnica confirmada

Ele deve continuar curto, objetivo e confiavel.

## 16. Instrucao operacional padrao para novos chats
Ao iniciar um novo chat ou nova execucao, usar algo como:

"Leia primeiro:
- `docs/CEREBRO_PROJETO.md`
- `docs/STATE.md`
- `docs/CODEX_RESULTADO.md`

Use esses arquivos como fonte de verdade.
Antes de implementar, resuma o estado atual, informe divergencias reais e liste os arquivos que pretende alterar.
Se houver conflito entre o pedido e o repositorio, pare e avise antes de codificar."
