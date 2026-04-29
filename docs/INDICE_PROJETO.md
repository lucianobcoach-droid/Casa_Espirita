# Índice do Projeto — Casa Espírita

Este documento é o ponto de entrada rápido para qualquer chat, GPT ou Codex compreender o projeto sem carregar toda a documentação longa.

## Fonte oficial

- Branch de trabalho: feat/reinicio-financeiro
- Documentação oficial: docs/
- Regras do executor: AGENTS.md
- Skills sob demanda: .agents/skills/

## Ordem recomendada de leitura

1. AGENTS.md
2. docs/INDICE_PROJETO.md
3. docs/STATE.md
4. docs/CEREBRO_PROJETO.md
5. Documento específico da tarefa

## Papel dos documentos

- CEREBRO_PROJETO.md: decisões permanentes e diretrizes estruturais.
- STATE.md: estado atual real do sistema.
- CODEX_RESULTADO.md: histórico cronológico das execuções.
- ROADMAP_FINANCEIRO.md: pendências e melhorias futuras.
- REGRAS_NEGOCIO.md: regras consolidadas do sistema.
- PADRAO_UX_SISTEMA.md: padrão visual aprovado.
- MATRIZ_PERMISSOES.md: regras de perfis e permissões.
- ROTINA_GIT_GITHUB.md: rotina oficial de sincronização local x GitHub.
- ROTINA_BAIXA_PENDENCIAS.md: rotina oficial para baixar e reclassificar pendências documentais.

## Fluxo oficial

1. GPT Cérebro consulta a documentação.
2. GPT Cérebro define a microetapa.
3. Usuário aprova.
4. Codex executa.
5. Usuário testa.
6. Resultado é registrado nos documentos base.
7. Commit e push consolidam a etapa no GitHub; se houver commit local sem push, a próxima etapa deve ser sincronização Git/GitHub.

## Documentos auxiliares de governança

- AUDITORIA_DOCUMENTACAO.md: registra riscos, diagnóstico e diretrizes para reorganização segura da documentação.
- MAPA_RECLASSIFICACAO.md: lista itens que precisam ser classificados como implementados, parcialmente implementados, futuros ou dúvida antes de qualquer reorganização maior.
- ROTINA_BAIXA_PENDENCIAS.md: define status padronizados e critérios para encerrar, reclassificar ou manter pendências.

## Regra para escolha de próxima microetapa

Antes de propor nova implementação, o GPT/Cérebro deve consultar:

1. AGENTS.md
2. docs/INDICE_PROJETO.md
3. docs/AUDITORIA_DOCUMENTACAO.md
4. docs/MAPA_RECLASSIFICACAO.md
5. docs/STATE.md
6. docs/CEREBRO_PROJETO.md
7. docs/ROADMAP_FINANCEIRO.md, se a tarefa envolver futuro/backlog

Se um item aparecer no MAPA_RECLASSIFICACAO.md como DÚVIDA ou REQUER CONFERÊNCIA NO CÓDIGO, a próxima microetapa deve ser auditoria/conferência, não implementação.
