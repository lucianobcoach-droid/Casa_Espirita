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
- paginas autenticadas nao devem adotar como padrao principal um topo minimo com apenas botao de navegacao quando o sistema ja possui shell contextual completo disponivel
- no `financeiro`, o padrao oficial passa a ser `financeiro/base.html` com barra superior contextual + contexto institucional/usuario + navegacao lateral persistente
- em modulos que usam `configuracoes/sistema_base.html`, o padrao oficial continua sendo topbar completa com acoes do usuario e navegacao local do modulo quando aplicavel
- excecoes de shell precisam ser claras e justificadas, especialmente em autenticacao, impressao e recibos
- recibos devem ser tratados como documentos finais: controles de navegacao ou impressao, quando existirem, devem ficar fora da area documental e ocultos no modo de impressao
- no contexto financeiro, `PessoaFinanceira` deve ser exibida ao usuario como `Favorecido`, preservando nomes tecnicos internos quando a mudanca for apenas de rotulo/UX
- listagens extensas podem oferecer selecao de quantidade por pagina quando isso melhorar o uso real; em tabelas largas, scroll horizontal deve permanecer confinado ao wrapper da tabela, podendo ter controle superior sincronizado quando a usabilidade exigir
- listagens operacionais com muitas colunas podem oferecer configuracao de colunas visiveis, ordem manual simples e restauracao de padrao; o conjunto inicial deve priorizar leitura diaria enxuta, mantendo campos complementares como opcionais quando couber
- na listagem principal de lancamentos do `financeiro`, o conjunto essencial deve manter `Data pagamento`, `Tipo`, `Descricao` e `Valor`, alem de selecao e acoes quando as permissoes aplicarem
- totalizadores em listagens devem deixar claro o escopo do calculo, por exemplo pagina atual exibida ou resultado filtrado; totalizadores de selecao devem reagir dinamicamente quando houver acoes em lote

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
