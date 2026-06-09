# Auditoria transversal de categorias/subcategorias nos relatorios financeiros

## Objetivo

Mapear como os relatorios financeiros atuais usam `CategoriaFinanceira` e sua hierarquia `categoria_pai -> subcategoria`, sem alterar comportamento funcional nesta etapa.

## Regra conceitual recomendada

- categoria pai deve ser o agrupador gerencial padrao dos relatorios sinteticos;
- subcategoria deve permanecer como detalhe operacional do lancamento;
- filtros por categoria pai devem expandir para as subcategorias filhas;
- filtros por subcategoria devem restringir apenas a subcategoria escolhida;
- transferencias nao devem ser forcadas em categoria/subcategoria;
- nenhum relatorio deve criar calculo paralelo diferente da base atual.

## Diagnostico objetivo

| Relatorio | Rota / view | Template | Exibe categoria | Exibe subcategoria | Agrupamento atual | Filtro categoria | Filtro subcategoria | Centro de custo | XLSX | Impressao | Classificacao | Risco ao mexer | Melhor oportunidade | Prioridade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Resumo Financeiro | `financeiro:resumo` / `ResumoFinanceiroView` | `financeiro/resumo.html` | Sim | Nao explicita | `lancamento.categoria` via `_agrupar_por_campo(..., 'categoria')` | Nao | Nao | Nao | Nao | Nao | `PRECISA FILTRAR CATEGORIA/SUBCATEGORIA` | Medio: resumo sintetico alimenta leitura gerencial do periodo | adicionar filtro por categoria pai e subcategoria, com microcopy explicando que afeta receitas/despesas e nao a composicao das contas | Alta |
| Extrato Financeiro | `financeiro:extrato-list`, `financeiro:conta-extrato`, `financeiro:extrato-exportacao-xlsx` / `ExtratoFinanceiroView`, `ContaFinanceiraExtratoView`, `ExtratoFinanceiroExportacaoXlsxView` | `financeiro/conta_extrato.html` | Sim, na exportacao XLSX e no payload | Nao | Sem agrupamento por categoria; listagem cronologica de lancamentos | Nao | Nao | Sim | Sim | Sim | `OK COMO ESTA` | Baixo: categoria nao interfere no calculo do extrato | manter sem filtro por categoria no curto prazo; se evoluir, deixar muito claro que seria apenas leitura de receitas/despesas e nao filtro de saldo bancario | Baixa |
| Prestacao / Fechamento do periodo | `financeiro:prestacao-contas` / `PrestacaoContasFinanceiroView` | `financeiro/prestacao_contas.html` | Sim | Nao explicita | `lancamento.categoria` via `_agrupar_por_campo(..., 'categoria')` | Nao | Nao | Sim, bloco complementar | Nao | Sim | `PRECISA EXIBIR SUBCATEGORIA` | Medio: documento sintetico e formal, com risco de poluir a leitura se detalhar demais | manter agrupamento gerencial, mas avaliar detalhamento opcional por subcategoria em bloco analitico secundario | Media |
| Balancete Institucional | `financeiro:balancete-institucional` / `BalanceteInstitucionalFinanceiroView` | `financeiro/balancete_institucional.html` | Sim | Nao explicita | `lancamento.categoria` via `_agrupar_por_campo(..., 'categoria')` | Nao | Nao | Nao no bloco de categoria | Nao | Sim | `PRECISA PADRONIZACAO DE NOMENCLATURA` | Medio: balancete e documento compacto; mexer no agrupamento exige cuidado com linguagem institucional | explicitar no texto do documento que entradas/saidas estao em nivel gerencial e planejar exibicao analitica fora do balancete compacto | Media |
| Evolucao por categorias | `financeiro:evolucao-categorias` / `EvolucaoCategoriasFinanceiroView` | `financeiro/evolucao_categorias.html` | Sim | Sim | Tem dois escopos reais: `categorias` expande para subcategorias filhas; `subcategorias` usa item individual | Sim | Sim | Nao | Nao | Sim | `OK COMO ESTA` | Baixo: ja e a referencia mais madura para a hierarquia | usar esta tela como padrao conceitual para futuras evolucoes de filtro em outros relatorios | Alta como referencia, nao como correção |
| Frequencia por competencias | `financeiro:frequencia-competencias` / `FrequenciaCompetenciasView` | `financeiro/frequencia_competencias.html` | Nao | Sim, apenas subcategoria controlada | Subcategoria controlada (`categoria_pai__isnull=False`, `controla_recorrencia_competencia=True`) | Nao | Sim | Nao | Nao | Sim | `OK COMO ESTA` | Baixo: dominio proprio de competencias | padronizar nomenclatura de filtro para deixar explicito que `categoria` na query significa subcategoria controlada | Media |
| Listagem de lancamentos | `financeiro:lancamento-list`, `financeiro:lancamento-exportacao` / `LancamentoFinanceiroListView`, `LancamentoFinanceiroExportacaoView` | `financeiro/lancamento_list.html` | Sim | Nao explicita | Sem agrupamento; usa `lancamento.categoria` em coluna e exportacao | Sim, por `categoria_id` direto | Nao | Sim | Sim | Nao | `PRECISA FILTRAR CATEGORIA/SUBCATEGORIA` | Medio: tela operacional muito usada | separar filtro de categoria pai e subcategoria, preservando compatibilidade da listagem e exportacao | Alta |
| Recibos e termos por lancamento / favorecido | `financeiro:lancamento-recibo`, `financeiro:lancamento-recibos-por-favorecido`, `financeiro:lancamento-recibo-especial`, `financeiro:lancamento-termo-anual-quitacao`, `financeiro:lancamento-termos-anuais-quitacao-por-favorecido` / views documentais correspondentes | `_lancamento_recibo_documento.html`, `_lancamento_recibo_especial_documento.html`, `financeiro/lancamento_documentos_por_favorecido.html` | Sim, como contexto documental e validacao de unicidade | Nao | Nao agrupa por pai/filha; exige `categoria` unica nos fluxos por favorecido | Sim, em helpers documentais | Nao | Nao | Nao | Sim | `REQUER CONFERENCIA NO CODIGO` | Medio/alto: categoria aqui afeta mensagem documental e elegibilidade de lote | antes de abrir filtro por categoria pai, decidir se a unicidade documental deve continuar em nivel de subcategoria atual ou migrar para categoria pai | Media |

## Achados principais

- `CategoriaFinanceira.__str__()` retorna apenas `nome`, entao varios relatorios hoje exibem a subcategoria isolada sem deixar clara a categoria pai.
- `permite_vinculo_em_lancamento` depende de `categoria_pai_id`, ou seja, o lancamento operacional foi desenhado para vincular subcategoria, nao categoria pai.
- `Resumo`, `Prestacao` e `Balancete` agrupam por `lancamento.categoria` diretamente. Isso funciona tecnicamente, mas deixa a leitura gerencial ambigua quando o usuario espera ver categoria pai consolidada.
- `Evolucao por categorias` ja resolveu a hierarquia de modo mais seguro:
  - escopo `categorias`: seleciona categoria pai e expande para subcategorias filhas;
  - escopo `subcategorias`: seleciona subcategoria explicitamente.
- `Frequencia por competencias` usa apenas subcategorias controladas e ja comunica isso na UX, entao nao pede reestruturacao ampla.
- `Listagem de lancamentos` filtra `categoria_id` diretamente; hoje esse filtro e, na pratica, filtro por subcategoria atual.
- `Extrato` e seus XLSX mostram categoria apenas como atributo descritivo do lancamento, nao como eixo de agrupamento ou filtro.
- `Recibos/termos por favorecido` exigem uma unica `categoria` para o grupo, porque a categoria tambem alimenta a mensagem documental. Esse ponto merece decisao propria antes de qualquer filtro hierarquico.

## Oportunidades de melhoria

1. Padronizar o vocabulario publico:
   - usar `Categoria` para categoria pai;
   - usar `Subcategoria` para o vinculo operacional do lancamento.
2. Levar para outros relatorios o padrao ja provado em `Evolucao por categorias`:
   - filtro por categoria pai com expansao de filhas;
   - filtro por subcategoria com restricao estrita.
3. Distinguir relatorios sinteticos de analiticos:
   - sinteticos: agrupam por categoria pai;
   - analiticos: podem exibir subcategoria por linha ou como coluna auxiliar.
4. Revisar exportacoes XLSX de listagem e extrato apenas quando a mesma hierarquia ja estiver clara na tela correspondente.
5. Decidir separadamente o contrato documental de recibos/termos antes de mexer em filtros desses fluxos.

## Priorizacao recomendada

### Alta

- Resumo Financeiro: filtro por categoria pai e subcategoria, com microcopy clara.
- Listagem de lancamentos: separar filtro de categoria pai e subcategoria.
- Reusar o contrato conceitual de `Evolucao por categorias` como referencia oficial da hierarquia.

### Media

- Prestacao / Fechamento: avaliar bloco analitico opcional de subcategoria.
- Balancete: ajustar nomenclatura e explicitar que o bloco continua gerencial.
- Frequencia por competencias: alinhar a nomenclatura do filtro para `Subcategoria controlada`.
- Recibos/termos: decidir o nivel documental correto antes de qualquer filtro hierarquico.

### Baixa

- Extrato Financeiro: manter sem filtro por categoria/subcategoria no curto prazo.

## Sequencia sugerida de microetapas futuras

1. `Resumo Financeiro: filtro por categoria pai + subcategoria`
   - sem alterar calculo;
   - com impacto apenas em receitas/despesas do resumo.
2. `Listagem de lancamentos: filtro separado de categoria e subcategoria`
   - refletindo a mesma logica na exportacao XLSX da listagem.
3. `Padronizacao de nomenclatura em Prestacao e Balancete`
   - consolidar leitura gerencial por categoria pai.
4. `SPEC documental para recibos/termos`
   - decidir se a unicidade continua na subcategoria atual ou sobe para categoria pai.

## Recomendacao objetiva sobre a proxima etapa

O prompt pontual do `Resumo Financeiro` pode ser aplicado como proxima microetapa.

Nao identifiquei bloqueio estrutural que exija outra implementacao antes dele. O unico cuidado e copiar o contrato conceitual ja existente em `Evolucao por categorias`, para evitar que o `Resumo` introduza uma segunda logica de hierarquia.
