# CHECKLIST DE EVOLUCAO DO SISTEMA

Objetivo: servir como checklist operacional permanente e curta para revisar toda nova funcionalidade antes de auditoria/commit, sem substituir os docs-base do projeto.

## Checklist permanente
- Navegacao, menu e atalhos foram revisados e continuam coerentes?
- A tela evita duplicar topbar, menu local, sidebar/drawer, botao de menu e atalhos de retorno como camadas concorrentes?
- Menus suspensos da navegacao abrem acima do conteudo, sem clipping por `overflow`, `z-index` ou stacking context de cards/formularios?
- O shell autenticado da tela segue o padrao oficial do modulo, sem topo minimo divergente?
- No `financeiro`, a tela preserva a topbar unica com menu suspenso agrupado e nao reintroduz sidebar/drawer persistente como navegacao principal?
- Se uma camada antiga de menu foi desativada, o legado comentado/inerte foi removido antes de encerrar a frente?
- Permissoes por modulo, tela/recurso e acao foram consideradas ou registradas como pendencia?
- Listagens impactadas foram revisadas em filtros, ordenacao, colunas, truncamento, acoes em lote e exportacao?
- Links de criar, editar, excluir, cancelar e salvar preservam filtros, pagina, ordenacao e demais parametros da listagem quando isso for parte do fluxo?
- Se a listagem tiver muitas colunas, foi avaliado se precisa de colunas configuraveis, ordem manual, totalizadores e restauracao de padrao?
- Em telas analiticas, o filtro resumido/expandido permanece no topo da analise, sem cair para baixo dos KPIs ou dos resultados?
- Em telas analiticas, o estado resumido do filtro entrega resumo util da configuracao atual sem poluir a leitura?
- Em telas analiticas, o filtro expandido reabre no mesmo ponto estrutural do estado resumido?
- Em telas analiticas, os KPIs ficam entre o filtro e a area de resultados?
- Em telas analiticas, o resultado permanece mais protagonista do que o filtro?
- Quando houver muitas selecoes, o contexto visual foi compactado sem excesso de chips ou metadados concorrentes?
- Formularios impactados foram revisados em rotulos, obrigatoriedade, mensagens, preview e consistencia visual?
- Em cadastros sequenciais, foi avaliado o padrao `Salvar` para sair/retornar e `+` para salvar e permanecer?
- Existe impacto em importacao/exportacao?
- Quando houver importacao centralizada e exportacao local por filtros, os menus e atalhos deixam essa arquitetura clara?
- Existe impacto em auditoria/log?
- Existe impacto em ajuda/manual do usuario?
- A implementacao segue a referencia de `docs/PADRAO_UX_SISTEMA.md`?
- Os docs-base `docs/CEREBRO_PROJETO.md`, `docs/STATE.md`, `docs/CODEX_RESULTADO.md` e `docs/ROADMAP_FINANCEIRO.md` foram atualizados quando necessario?

## Uso pratico
- aplicar esta checklist a cada microetapa funcional ou visual
- se algum item nao for tratado na implementacao atual, registrar explicitamente como pendencia/backlog no doc-base adequado
- nao usar este arquivo como historico de execucao; o historico continua em `docs/CODEX_RESULTADO.md`
