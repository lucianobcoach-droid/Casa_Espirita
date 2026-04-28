# Mapa de Reclassificação Documental — Casa Espírita

Data: 2026-04-25  
Branch: feat/reinicio-financeiro

## Objetivo

Este documento registra itens que precisam ser reclassificados antes de qualquer reorganização maior dos documentos base.

A finalidade é evitar perda de memória, evitar apagar histórico útil e impedir que itens já implementados continuem aparecendo como pendência futura.

## Regra de segurança

Nenhum item deve ser removido de CEREBRO_PROJETO.md, STATE.md, CODEX_RESULTADO.md ou ROADMAP_FINANCEIRO.md sem passar por esta classificação.

Classificações possíveis:

- IMPLEMENTADO
- PARCIALMENTE IMPLEMENTADO
- FUTURO REAL
- DÚVIDA / REQUER CONFERÊNCIA NO CÓDIGO
- HISTÓRICO / MANTER APENAS COMO REGISTRO

## Itens para reclassificação

### 1. Autenticação, perfis e permissões

Status inicial: DÚVIDA / REQUER CONFERÊNCIA NO CÓDIGO

Motivo:
Há registros antigos tratando autenticação, perfis, permissões e matriz de acesso como frente estrutural. É necessário confirmar o que está implementado no código, o que está apenas documentado e o que ainda é futuro.

Documentos relacionados:
- docs/CEREBRO_PROJETO.md
- docs/STATE.md
- docs/MATRIZ_PERMISSOES.md

---

### 2. Histórico por favorecido

Status inicial: DÚVIDA / REQUER CONFERÊNCIA NO CÓDIGO

Motivo:
A funcionalidade aparece como solicitação importante em chats e documentos. É necessário confirmar se já está totalmente implementada, parcialmente implementada ou ainda pendente.

Documentos relacionados:
- docs/CEREBRO_PROJETO.md
- docs/STATE.md
- docs/ROADMAP_FINANCEIRO.md

---

### 3. Recibos por favorecido e recibos em lote

Status inicial: DÚVIDA / REQUER CONFERÊNCIA NO CÓDIGO

Motivo:
Há registros sobre recibo em lote, recibos por favorecido e documentos financeiros. Precisa ser conferido o estado real no código.

Documentos relacionados:
- docs/STATE.md
- docs/CODEX_RESULTADO.md
- docs/ROADMAP_FINANCEIRO.md

---

### 4. Termo anual de quitação

Status inicial: DÚVIDA / REQUER CONFERÊNCIA NO CÓDIGO

Motivo:
Há registros sobre termo anual de quitação baseado nos filtros atuais da listagem financeira. Precisa confirmar se está implementado, validado e se ainda há pendências.

Documentos relacionados:
- docs/STATE.md
- docs/CODEX_RESULTADO.md
- docs/ROADMAP_FINANCEIRO.md

---

### 5. Controle de frequência / recorrência por competência

Status inicial: FUTURO REAL

Motivo:
A frente foi definida como futura e deve considerar favorecido/pessoa recorrente, subcategoria que controla frequência, matriz mensal com ou sem valores e termo de quitação por favorecido/período.

Documentos relacionados:
- docs/CEREBRO_PROJETO.md
- docs/ROADMAP_FINANCEIRO.md
- docs/REGRAS_NEGOCIO.md

---

### 6. Contratos, parcelas e recorrências

Status inicial: FUTURO REAL

Motivo:
Frente futura associada a controle financeiro avançado, compromissos recorrentes, parcelas e previsibilidade.

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md

---

### 7. Anexos de comprovantes

Status inicial: FUTURO REAL

Motivo:
Frente futura para anexar comprovantes, documentos e imagens aos lançamentos ou registros financeiros.

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md

---

### 8. Balancete padrão

Status inicial: FUTURO REAL

Motivo:
Frente futura relacionada à apresentação contábil/gerencial consolidada, distinta dos relatórios já trabalhados como Resumo, Extrato e Fechamento do período.

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/CEREBRO_PROJETO.md

---

### 9. Importação histórica e cadastros auxiliares

Status inicial: PARCIALMENTE IMPLEMENTADO / REQUER CONFERÊNCIA NO CÓDIGO

Motivo:
Há registros sobre importação, planilhas, categorias, favorecidos, contas e relatórios de inconsistência. É necessário separar o que já existe, o que foi testado e o que ainda precisa implementação.

Documentos relacionados:
- docs/CEREBRO_PROJETO.md
- docs/STATE.md
- docs/ROADMAP_FINANCEIRO.md
- docs/REGRAS_NEGOCIO.md

---

### 10. Logo institucional por upload ou arquivo local

Status inicial: FUTURO REAL / REQUER CONFERÊNCIA

Motivo:
A frente foi citada como melhoria para facilitar validação do sistema. É necessário confirmar se já existe algum suporte parcial ou se continua totalmente futura.

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/STATE.md

---

### 11. Padronização visual transversal

Status inicial: PARCIALMENTE IMPLEMENTADO

Motivo:
O padrão analítico foi consolidado a partir de Evolução por categorias e propagado para Resumo, Extrato e Fechamento do período. Ainda resta avaliar propagação para outras telas.

Documentos relacionados:
- docs/PADRAO_UX_SISTEMA.md
- docs/STATE.md
- docs/CODEX_RESULTADO.md

---

### 12. Homologação ponta a ponta do sistema local

Status inicial: FUTURO REAL

Motivo:
Após vários ajustes funcionais e visuais, ainda é necessária uma rodada de teste completo local para validar fluxo real, especialmente antes de novas frentes grandes.

Documentos relacionados:
- docs/STATE.md
- docs/ROADMAP_FINANCEIRO.md

---

### 13. Favorecido duplicado por nome

Status inicial: FUTURO REAL / BUG OPERACIONAL

Motivo:
Foi levantado que o cadastro de favorecidos permite duplicidade por nome. Antes de implementar, e necessario conferir a regra atual de validacao, a existencia de duplicados ja cadastrados e a melhor normalizacao de nome.

Classificacao documental:
- BUG / correcao operacional
- REGRA DE NEGOCIO

Prioridade documental: ALTA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/REGRAS_NEGOCIO.md

---

### 14. Edicao de conta sem saldo inicial/data ja preenchidos

Status inicial: FUTURO REAL / BUG OPERACIONAL

Motivo:
Foi levantado que, ao atualizar dados da conta cadastrada, o formulario deve trazer saldo inicial e data do saldo ja cadastrados. Requer conferencia do formulario atual antes de qualquer correcao.

Classificacao documental:
- BUG / correcao operacional

Prioridade documental: ALTA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/STATE.md

---

### 15. Conta inativa em novos lancamentos e relatorios historicos

Status inicial: FUTURO REAL / REQUER CONFERENCIA NO CODIGO

Motivo:
Foi definida a regra de que conta inativa nao deve aparecer para novos lancamentos, mas deve aparecer em relatorios historicos quando tiver movimento no periodo selecionado. Requer conferencia de formularios, filtros e relatorios.

Classificacao documental:
- REGRA DE NEGOCIO
- BUG / correcao operacional

Prioridade documental: ALTA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/REGRAS_NEGOCIO.md
- docs/STATE.md

---

### 16. Favorecido em transferencia no Extrato

Status inicial: FUTURO REAL

Motivo:
Foi levantado que, quando o lancamento for transferencia, o campo favorecido no Extrato deve aparecer como `Transferencia entre contas`. Requer ajuste visual pontual futuro sem alterar regra de saldo.

Classificacao documental:
- MELHORIA DE UX
- BUG / correcao operacional

Prioridade documental: MEDIA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/REGRAS_NEGOCIO.md

---

### 17. Diferenca restante no rateio

Status inicial: FUTURO REAL

Motivo:
Foi levantada melhoria para mostrar o valor que falta para fechar o valor total do documento em lancamentos com rateio.

Classificacao documental:
- MELHORIA FUNCIONAL
- MELHORIA DE UX

Prioridade documental: MEDIA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/REGRAS_NEGOCIO.md

---

### 18. Filtro multi-contas na listagem de lancamentos

Status inicial: FUTURO REAL

Motivo:
Foi levantada melhoria para permitir selecionar mais de uma conta na listagem de lancamentos, reaproveitando a experiencia validada no Extrato multi-contas.

Classificacao documental:
- MELHORIA FUNCIONAL
- MELHORIA DE UX

Prioridade documental: MEDIA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/STATE.md

---

### 19. Tabelas personalizadas de controle

Status inicial: FUTURO REAL / FRENTE FUTURA GRANDE

Motivo:
Foi levantada frente futura para controles configuraveis, como energia eletrica mensal, com colunas definidas pelo usuario, formulas por celula e totalizadores. Deve ser tratada separadamente das correcoes imediatas do financeiro.

Classificacao documental:
- FRENTE FUTURA GRANDE

Prioridade documental: FUTURA / BAIXA para execucao imediata

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/CEREBRO_PROJETO.md

## Próxima ação recomendada

A próxima microetapa documental deve conferir os itens acima contra o código e contra os documentos atuais, um grupo por vez, sem alterar funcionalidades.

Prioridade sugerida de conferência:

1. financeiro/documentos por favorecido;
2. permissões;
3. importação;
4. padronização visual;
5. frequência/recorrência futura.
