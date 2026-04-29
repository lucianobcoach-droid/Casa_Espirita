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

Status inicial: PARCIALMENTE IMPLEMENTADO

Motivo:
Frente relacionada à apresentação contábil/gerencial consolidada, distinta dos relatórios já trabalhados como Resumo, Extrato e Fechamento do período. O MVP do Balancete Institucional foi iniciado como relatório próprio, reaproveitando a base comum da Prestação/Fechamento; refinamentos de layout documental e evolução funcional permanecem acompanháveis em etapas futuras.

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

Observacao complementar:
A regra-mae foi ampliada para todos os cadastros por identificadores-chave, mas a implementacao pratica desta microetapa permanece restrita a favorecidos/pessoas financeiras.

---

### 13.1. Regra geral de identificadores-chave nos cadastros

Status inicial: FUTURO REAL / APLICACAO PROGRESSIVA

Motivo:
Foi definida regra geral de que cadastros do sistema nao devem duplicar identificadores-chave, como codigo, nome ou equivalentes, conforme a natureza de cada cadastro. A extensao para contas, categorias/subcategorias, centros de custo e cadastros futuros deve ocorrer em microetapas proprias.

Classificacao documental:
- REGRA DE NEGOCIO
- MELHORIA FUNCIONAL progressiva

Prioridade documental: ALTA como diretriz; execucao incremental por cadastro

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

Status apos auditoria: AUDITADO / REQUER IMPLEMENTACAO

Status apos implementacao parcial: PARCIALMENTE IMPLEMENTADO / REQUER FILTROS HISTORICOS

Motivo:
Foi definida a regra de que conta inativa nao deve aparecer para novos lancamentos, mas deve aparecer em relatorios historicos quando tiver movimento no periodo selecionado. Requer conferencia de formularios, filtros e relatorios.

Achado da auditoria:
- `LancamentoFinanceiroForm`, `LancamentoFinanceiroGrupoRateioForm` e `ContaFinanceiraAutocompleteView` ainda usam contas sem filtrar por `ativa`, permitindo conta inativa em novo lancamento e em conta destino de transferencia.
- A edicao de lancamento antigo ainda funciona porque as contas inativas permanecem no queryset, mas uma correcao futura precisa preservar explicitamente a conta ja vinculada.
- Relatorios e filtros historicos usam todas as contas, preservando movimentos antigos, mas ainda nao aplicam o refinamento de exibir inativas apenas quando tiverem movimento no periodo.
- A importacao de lancamentos ja monta indice de contas com `ContaFinanceira.objects.filter(ativa=True)`.

Implementacao parcial:
- Forms e autocomplete de lancamentos passaram a oferecer apenas contas ativas para novos lancamentos e transferencias.
- Edicao de lancamento antigo preserva apenas a conta inativa ja vinculada ao proprio registro.
- Clone passa a limpar conta origem/destino inativa do original para revisao do usuario.
- Permanece pendente a parte de filtros historicos de relatorios.

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

---

### 20. Padronizacao do filtro de contas nas telas com selecao de contas

Status inicial: FUTURO REAL / PADRONIZACAO TRANSVERSAL

Motivo:
Foi levantada melhoria para aplicar o padrao visual/comportamental do filtro de contas validado no Extrato em outras telas que possuam selecao de contas. Deve ser implementado futuramente em microetapas por tela ou conjunto minimo seguro.

Classificacao documental:
- MELHORIA DE UX
- PADRONIZACAO TRANSVERSAL

Prioridade documental: MEDIA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/PADRAO_UX_SISTEMA.md
- docs/STATE.md

---

### 21. Refinamento de impressao da Prestacao/Fechamento do periodo

Status inicial: FUTURO REAL / AJUSTE VISUAL DE RELATORIO

Motivo:
Foi levantado que o PDF/impresso atual da Prestacao/Fechamento do periodo esta pouco compacto, com margens/espacamentos grandes e quebra de pagina ruim. O ajuste futuro deve tratar apenas layout de impressao, sem alterar calculos.

Classificacao documental:
- AJUSTE VISUAL DE RELATORIO / IMPRESSAO

Prioridade documental: MEDIA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/STATE.md
- docs/REGRAS_NEGOCIO.md

---

### 22. Balancete Institucional como relatorio proprio

Status inicial: FUTURO REAL / FRENTE DE RELATORIO

Motivo:
Foi revisada a direcao anterior: a Prestacao/Fechamento deve permanecer como relatorio analitico/gerencial, e o Balancete Institucional deve ser criado futuramente como relatorio proprio, formal/documental, reutilizando a mesma base de calculo da Prestacao/Fechamento.

Classificacao documental:
- FRENTE FUTURA DE RELATORIO / IMPRESSAO
- AJUSTE VISUAL DOCUMENTAL

Prioridade documental: MEDIA

Direcao revisada:
- relatorio proprio chamado `Balancete Institucional`
- nao substituir a Prestacao/Fechamento atual
- reaproveitar regra/base de calculo da Prestacao/Fechamento
- evitar divergencia de calculo e duplicacao de regra financeira
- preservar transparencia da composicao do saldo e regra de transferencias por escopo

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/CEREBRO_PROJETO.md
- docs/REGRAS_NEGOCIO.md

---

### 23. Duas assinaturas no Balancete Institucional

Status inicial: FUTURO REAL

Motivo:
Foi levantada necessidade futura de permitir duas assinaturas no Balancete Institucional, aproveitando a base de cadastro manual de assinaturas ja existente e evoluindo para selecao ou definicao de duas assinaturas padrao para esse documento.

Classificacao documental:
- MELHORIA FUNCIONAL
- AJUSTE DOCUMENTAL / IMPRESSAO

Prioridade documental: MEDIA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/CEREBRO_PROJETO.md

---

### 24. Fundo branco permanente nos relatorios impressos

Status inicial: DIRETRIZ PERMANENTE / FUTURO REAL PARA PROPAGACAO

Motivo:
Foi consolidada diretriz de que relatorios impressos/PDF devem usar fundo branco por padrao para economia de tinta e aparencia documental, evitando elementos de tela administrativa como fundos coloridos grandes, cards preenchidos e sombras no modo print.

Classificacao documental:
- DIRETRIZ DE UX / IMPRESSAO
- PADRONIZACAO TRANSVERSAL

Prioridade documental: MEDIA

Documentos relacionados:
- docs/CEREBRO_PROJETO.md
- docs/ROADMAP_FINANCEIRO.md

## Próxima ação recomendada

A próxima microetapa documental deve conferir os itens acima contra o código e contra os documentos atuais, um grupo por vez, sem alterar funcionalidades.

Prioridade sugerida de conferência:

1. financeiro/documentos por favorecido;
2. permissões;
3. importação;
4. padronização visual;
5. frequência/recorrência futura.
