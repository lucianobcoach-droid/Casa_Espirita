# CHECKLIST DE EVOLUCAO DO SISTEMA

Objetivo: servir como checklist operacional permanente e curta para revisar toda nova funcionalidade antes de auditoria/commit, sem substituir os docs-base do projeto.

## Checklist permanente
- Navegacao, menu e atalhos foram revisados e continuam coerentes?
- O shell autenticado da tela segue o padrao oficial do modulo, sem topo minimo divergente?
- Permissoes por modulo, tela/recurso e acao foram consideradas ou registradas como pendencia?
- Listagens impactadas foram revisadas em filtros, ordenacao, colunas, truncamento, acoes em lote e exportacao?
- Se a listagem tiver muitas colunas, foi avaliado se precisa de colunas configuraveis, ordem manual, totalizadores e restauracao de padrao?
- Formularios impactados foram revisados em rotulos, obrigatoriedade, mensagens, preview e consistencia visual?
- Existe impacto em importacao/exportacao?
- Existe impacto em auditoria/log?
- Existe impacto em ajuda/manual do usuario?
- A implementacao segue a referencia de `docs/PADRAO_UX_SISTEMA.md`?
- Os docs-base `docs/CEREBRO_PROJETO.md`, `docs/STATE.md`, `docs/CODEX_RESULTADO.md` e `docs/ROADMAP_FINANCEIRO.md` foram atualizados quando necessario?

## Uso pratico
- aplicar esta checklist a cada microetapa funcional ou visual
- se algum item nao for tratado na implementacao atual, registrar explicitamente como pendencia/backlog no doc-base adequado
- nao usar este arquivo como historico de execucao; o historico continua em `docs/CODEX_RESULTADO.md`
