# PADRAO UX DO SISTEMA

## Objetivo
Documento enxuto e evolutivo para consolidar o padrao visual e funcional do sistema Casa Espirita.

Este arquivo nao substitui `docs/CEREBRO_PROJETO.md`, `docs/STATE.md`, `docs/CODEX_RESULTADO.md` nem `docs/ROADMAP_FINANCEIRO.md`.

## Diretrizes iniciais
- manter navegacao, rotulos, acoes e mensagens consistentes entre telas equivalentes
- reduzir texto fixo explicativo quando a estrutura da tela e a validacao ja orientam o uso
- preservar acessibilidade em iconografia e acoes compactas com `title`, `aria-label` ou texto equivalente
- priorizar listagens com leitura rapida, ordenacao clara, truncamento controlado, filtros operacionais visiveis e acoes alinhadas
- priorizar formularios com rotulos claros, obrigatoriedade bem sinalizada, mensagens compreensiveis, preview quando fizer sentido e bloco final de acoes previsivel
- revisar impacto em importacao/exportacao, auditoria/log e ajuda/manual sempre que uma nova funcionalidade entrar
- consolidar primeiro o padrao no `financeiro` e so depois expandir para outros modulos

## Checklist permanente
- Navegacao/menu/atalhos foram revisados?
- Permissoes por modulo/tela/acao foram consideradas?
- A listagem relacionada foi revisada em filtros, ordenacao, colunas, truncamento, acoes em lote e exportacao?
- O formulario relacionado foi revisado em rotulos, obrigatoriedade, mensagens, preview e consistencia visual?
- Existe impacto em importacao/exportacao?
- Existe impacto em auditoria/log?
- Existe impacto em ajuda/manual do usuario?
- A tela segue o padrao UX/layout ja consolidado?
- Os docs-base oficiais foram atualizados sem perder historico?
