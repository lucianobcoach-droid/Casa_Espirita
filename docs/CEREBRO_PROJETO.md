# CÉREBRO DO PROJETO — CASA ESPÍRITA

## 1. Objetivo deste arquivo
Este documento é a fonte principal de contexto funcional e operacional do projeto.
Antes de qualquer implementação, leitura técnica ou alteração estrutural, ele deve ser lido junto com:
- `docs/STATE.md`
- `docs/CODEX_RESULTADO.md`

Se houver divergência entre pedido atual, conversa e estado real do repositório, a implementação deve parar e a divergência deve ser informada antes de codificar.

---

## 2. Objetivo do sistema
O projeto **Casa Espírita** é um sistema em Django para apoiar a gestão da instituição.

O desenvolvimento deve acontecer em etapas pequenas, seguras e sem regressão, preservando o que já foi validado.

---

## 3. Branch de trabalho atual
- `feat/reinicio-financeiro`

> Atualizar esta seção se a branch oficial de trabalho mudar.

---

## 4. Apps existentes no projeto
Atualmente, os apps existentes são:
- `configuracoes`
- `biblioteca`
- `financeiro`

---

## 5. Regras de trabalho obrigatórias
Estas regras devem ser respeitadas em qualquer etapa:

- trabalhar sempre em etapas pequenas
- não regredir estrutura já aprovada
- usar o estado real do Git como fonte de verdade
- antes de implementar, resumir o estado atual e apontar divergências reais, se existirem
- depois de cada etapa aprovada, atualizar a documentação antes de seguir
- depois de cada etapa aprovada, fazer commit no Git antes de iniciar a próxima
- não mexer no app `biblioteca` sem necessidade explícita
- não usar `signals` no módulo financeiro
- não misturar etapas diferentes na mesma implementação
- fazer alterações mínimas, incrementais e rastreáveis

---

## 6. Estado funcional já validado
Até o momento, está validado que:

- a rota `/financeiro/` funciona
- o módulo financeiro existe e está ativo no projeto
- o CRUD inicial do financeiro funciona para:
  - pessoas
  - categorias
  - contas
  - centros de custo
  - lançamentos
- edição funciona
- exclusão com confirmação funciona
- filtros básicos funcionam
- autocomplete real no lançamento funciona
- o autocomplete busca no banco
- o autocomplete usa busca por “contém” (`icontains`)
- o autocomplete funciona inclusive com partes do meio do texto
- `conta_destino` aparece apenas quando o tipo é `transferencia`
- a transferência ficou mais clara na interface
- `ContaFinanceira` já possui:
  - `saldo_inicial`
  - `data_saldo_inicial`
- `data_saldo_inicial` agora é obrigatória
- o extrato por conta existe
- a listagem de contas já mostra `saldo_atual` calculado
- o extrato por conta já aceita filtro por período com saldo anterior
- saldo real da conta considera apenas lançamentos `quitado`
- a interface do financeiro já possui refinamento visual discreto em tabelas, extrato e impressão
- o financeiro agora possui menu próprio `Extratos` com filtro por conta e período

---

## 7. Regras de negócio atuais do financeiro

### 7.1 Tipos de lançamento
Os tipos válidos de lançamento são:
- `receita`
- `despesa`
- `transferencia`

### 7.2 Regras mínimas
- `receita`: valor positivo
- `despesa`: valor positivo
- `transferencia`: valor informado continua positivo, mas representa:
  - saída na conta de origem
  - entrada na conta de destino

### 7.3 Regras de transferência
- `conta_destino` só aparece quando o tipo for `transferencia`
- `transferencia` não deve exigir campos irrelevantes como pessoa
- `conta` e `conta_destino` não podem ser iguais
- `conta_destino` só pode ser usada em `transferencia`

### 7.4 Regras de saldo de conta
- `ContaFinanceira` possui `saldo_inicial`
- `ContaFinanceira` possui `data_saldo_inicial` obrigatória
- o saldo inicial serve como base do extrato e do saldo acumulado
- `saldo_atual` é calculado em tempo de execução
- `saldo_atual` não é salvo no banco
- quando houver filtro por período no extrato, deve existir `saldo_anterior`
- apenas lançamentos com `status = quitado` afetam saldo real e extrato
- a nova tela `Extratos` reutiliza a mesma regra do extrato por conta

---

## 8. Restrições técnicas obrigatórias
As restrições abaixo devem ser mantidas:

- não alterar o app `biblioteca` sem necessidade explícita
- não usar `signals`
- não alterar domínio além do necessário para a etapa atual
- não alterar migrations antigas
- não fazer refatorações paralelas fora do escopo
- não criar funcionalidades futuras antes da etapa correta
- não assumir comportamento não validado sem checagem no código

---

## 9. Fonte de verdade
A ordem de prioridade para tomada de decisão deve ser:

1. estado real do repositório
2. este arquivo `docs/CEREBRO_PROJETO.md`
3. `docs/STATE.md`
4. `docs/CODEX_RESULTADO.md`
5. instrução atual da etapa
6. histórico do chat

Se houver conflito entre chat e repositório, prevalece o repositório.

---

## 10. O que não pode ser quebrado
As seguintes garantias já aprovadas não podem ser perdidas:

- funcionamento da rota `/financeiro/`
- CRUD inicial de pessoas
- CRUD inicial de categorias
- CRUD inicial de contas
- CRUD inicial de centros de custo
- CRUD inicial de lançamentos
- edição funcionando
- exclusão com confirmação funcionando
- filtros funcionando
- autocomplete real funcionando no lançamento
- comportamento condicional de `conta_destino`
- clareza da interface de transferência
- extrato por conta funcionando

---

## 11. Padrão obrigatório antes de qualquer implementação
Antes de codificar qualquer etapa, deve-se informar objetivamente:

1. branch atual
2. estado atual resumido em até 8 linhas
3. divergências encontradas, se houver
4. arquivos que serão alterados
5. risco real de regressão

Se houver divergência factual relevante, parar antes de implementar.

---

## 12. Padrão obrigatório após qualquer implementação
Ao final de cada etapa, deve-se informar objetivamente:

1. arquivos alterados
2. migration criada, se houver
3. resumo do que foi feito
4. riscos encontrados, se houver
5. o que falta validar manualmente no navegador

Depois disso:
- validar no navegador
- atualizar documentação
- fazer commit
- só então seguir para a próxima etapa

---

## 13. Etapa atual concluída
### ETAPA 2 — Extrato por conta com saldo acumulado

Escopo implementado:
- rota de extrato por conta
- view de extrato por conta
- template de extrato
- cálculo de saldo acumulado a partir de `saldo_inicial`
- filtro por período via GET
- cálculo de `saldo_anterior` quando houver `data_inicial`

Regras implementadas:
- sem filtro: extrato completo desde o saldo inicial
- com filtro: lançamentos do período e saldo acumulado iniciando do saldo anterior
- `receita` = entrada
- `despesa` = saída
- `transferencia`:
  - conta de origem = saída
  - conta de destino = entrada

Complemento incremental já aplicado:
- `data_saldo_inicial` tornou-se obrigatória
- `saldo_atual` passou a ser calculado na listagem de contas

---

## 14. Etapas futuras já pensadas, mas não autorizadas agora
As etapas abaixo podem existir no planejamento, mas não devem ser implementadas antes da hora:

- relatórios gerais do financeiro
- importação de planilha histórica
- fechamentos mensais
- conciliação
- dashboards
- melhorias extras fora do escopo validado

---

## 15. Como este arquivo deve ser mantido
Este arquivo deve ser atualizado sempre que houver:
- nova regra de negócio validada
- mudança estrutural aprovada
- mudança da branch principal de trabalho
- conclusão de etapa relevante
- nova restrição técnica confirmada

Ele deve continuar curto, objetivo e confiável.

---

## 16. Instrução operacional padrão para novos chats
Ao iniciar um novo chat ou nova execução, usar algo como:

“Leia primeiro:
- `docs/CEREBRO_PROJETO.md`
- `docs/STATE.md`
- `docs/CODEX_RESULTADO.md`

Use esses arquivos como fonte de verdade.
Antes de implementar, resuma o estado atual, informe divergências reais e liste os arquivos que pretende alterar.
Se houver conflito entre o pedido e o repositório, pare e avise antes de codificar.”
