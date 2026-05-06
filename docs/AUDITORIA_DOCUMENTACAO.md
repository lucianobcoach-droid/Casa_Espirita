# Auditoria inicial da documentação — Casa Espírita

Data: 2026-04-25  
Branch: feat/reinicio-financeiro

## Objetivo

Registrar a primeira auditoria da memória documental do projeto após a criação da nova estrutura de governança com:

- AGENTS.md
- .agents/skills/
- docs/INDICE_PROJETO.md
- docs/REGRAS_NEGOCIO.md

Esta auditoria não altera código e não substitui os documentos existentes.

## Diagnóstico inicial

A documentação atual preserva muita memória útil do projeto, mas ainda mistura quatro tipos de informação:

1. decisões permanentes;
2. estado atual real;
3. histórico cronológico de execução;
4. pendências e frentes futuras.

Isso torna os documentos grandes e pode aumentar consumo de tokens quando GPT ou Codex precisam consultar o projeto.

## Pontos de atenção encontrados

### 1. CEREBRO_PROJETO.md

O documento cumpre o papel de diretriz permanente, mas contém alguns itens antigos marcados como futuros que podem precisar de reclassificação após conferência com o código e com STATE.md.

Exemplos de itens a conferir:

- autenticação, perfis e permissões;
- histórico por favorecido;
- documentos por favorecido;
- recibos;
- relatório ou termo anual por favorecido.

Regra: não apagar esses itens agora. Primeiro confirmar se estão implementados, parcialmente implementados ou ainda futuros.

### 2. STATE.md

O documento contém o estado real consolidado, mas está grande e acumulando muitas etapas antigas.

Direção recomendada:

- manter STATE.md como fonte do estado atual;
- criar resumos por área antes de qualquer redução;
- não apagar histórico útil sem validação.

### 3. CODEX_RESULTADO.md

O documento cumpre o papel de histórico cronológico, mas está muito longo.

Direção recomendada:

- manter como diário de execução;
- futuramente avaliar arquivamento por período ou por bloco;
- nunca apagar sem preservar histórico.

### 4. ROADMAP_FINANCEIRO.md

O documento contém pendências reais, mas também pode conter itens já entregues ou reclassificados.

Direção recomendada:

- separar claramente:
  - futuro real;
  - parcialmente entregue;
  - entregue e mantido apenas como histórico;
  - descartado ou substituído.

### 5. REGRAS_NEGOCIO.md

O documento foi criado como camada curta de consulta, mas ainda está inicial.

Direção recomendada:

- enriquecer aos poucos;
- extrair regras permanentes dos documentos antigos;
- não transformar o arquivo em novo histórico longo.

## Frentes futuras que permanecem relevantes

Sem considerar isso como ordem de execução imediata, permanecem como frentes a revisar:

- controle de frequência/recorrência por competência;
- contratos, parcelas e recorrência;
- anexos de comprovantes;
- balancete padrão;
- importação histórica e importação de cadastros auxiliares;
- logo institucional por upload/arquivo local;
- padronização visual transversal;
- homologação ponta a ponta do sistema local.

## Regra de segurança documental

Nenhum documento antigo deve ser apagado ou reescrito amplamente nesta fase.

Toda reorganização deve seguir esta ordem:

1. identificar;
2. classificar;
3. validar com o usuário;
4. consolidar;
5. só então arquivar ou reduzir, se necessário.

## Próxima microetapa recomendada

Criar um mapa de reclassificação dos itens do ROADMAP_FINANCEIRO.md e do CEREBRO_PROJETO.md, separando:

- implementado;
- parcialmente implementado;
- futuro;
- dúvida que exige conferência no código.

Essa etapa deve continuar sendo apenas documental.

## Complemento de backlog - auditoria acionavel (pos-rateio controlado)

Foi registrada uma pendencia transversal para a frente de auditoria:

- hoje a auditoria mostra eventos, mas ainda nao oferece acao direta para abrir o objeto/documento auditado
- tambem nao existe mecanismo de desfazer/restaurar alteracoes com governanca forte

Direcao de classificacao:

- manter como FUTURO/BACKLOG com SPEC propria antes de implementacao
- incluir no escopo futuro:
  - link para objeto auditado quando existir
  - indicacao clara de objeto excluido
  - visao antes/depois mais operacional
  - estudo de reversao com permissao dedicada e trilha da propria reversao

Risco principal:

- qualquer reversao pode afetar calculo financeiro, saldos, recibos, competencias, rateios e documentos emitidos; por isso, nao deve ser implementada sem modelagem de seguranca especifica.
