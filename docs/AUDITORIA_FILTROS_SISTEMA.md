# AUDITORIA DE FILTROS E BUSCAS DO SISTEMA

Data: 2026-06-09
Branch: feat/reinicio-financeiro

## 1. Objetivo

Registrar uma auditoria transversal de buscas, filtros, selecao multipla, preservacao de query string e padrao de UX nas telas relevantes de `financeiro`, `biblioteca` e `configuracoes`.

## 2. Regra conceitual recomendada

- busca textual deve priorizar leitura parcial (`icontains` ou equivalente seguro) nos campos operacionais mais provaveis para a usuaria
- filtros de selecao multipla devem usar `request.GET.getlist()` quando o caso de uso envolver mais de um item por consulta
- paginação, exportacao, impressao e acoes de retorno devem preservar o recorte atual por query string sempre que houver consulta filtrada
- filtros estruturais/analiticos podem continuar sem busca textual quando a tela nao trabalha com lista aberta de registros
- telas de uso diario devem ter:
  - botao `Limpar`
  - resumo discreto dos filtros ativos
  - nomenclatura consistente entre modulo, view e acao

## 3. Tabela de diagnostico por tela

Legenda curta:

- `Busca`: existe campo de busca textual
- `Parcial`: busca por qualquer parte do texto
- `Filtros rel.`: filtros por relacionamento/estrutura
- `Single`: filtros de selecao unica
- `Multi`: filtros de selecao multipla ja existentes
- `Deveria multi`: filtros que fazem sentido futuro como multipla selecao
- `GET/getlist`: como a view le os parametros
- `Pag`: preserva filtros na paginacao
- `Acoes`: preserva filtros em botoes/retornos
- `Exp`: preserva filtros na exportacao
- `Imp`: preserva filtros na impressao

| Tela | App | Rota | View | Template | Busca | Parcial | Campos cobertos | Campos importantes fora | Filtros rel. | Single | Multi | Deveria multi | GET/getlist | Pag | Acoes | Exp | Imp | Limpar | Classificacao | Confusao UX | Prioridade | Risco tecnico | Microetapa futura recomendada |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lancamentos financeiros | financeiro | `financeiro:lancamento-list` -> `/lancamentos/` | `LancamentoFinanceiroListView` | `financeiro/lancamento_list.html` | Sim | Sim | `descricao`, `numero_documento` | `observacoes`, `pessoa.nome`, `categoria.nome`, `centro_custo.nome` | Sim | `tipo`, `status`, `pessoa`, `categoria_pai`, `subcategoria`, `por_pagina` | `contas` | `pessoa`, `categoria_pai`, `subcategoria` | `get()` + `getlist(contas)` | Sim | Sim | Sim | N/A | Sim | OK COMO ESTA | Medio | Alta | Baixo | ampliar busca textual sem mexer no contrato hierarquico ja entregue |
| Resumo financeiro | financeiro | `financeiro:resumo` -> `/resumo/` | `ResumoFinanceiroView` | `financeiro/resumo.html` | Nao | N/A | N/A | descricao/documento nao se aplicam ao recorte sintetico | Sim | `categoria_pai`, `subcategoria`, `mostrar_subcategoria` | `contas` | `categoria_pai` e `subcategoria` podem ficar single nesta etapa | `get()` + `getlist(contas)` | N/A | N/A | N/A | Sim | Sim | OK COMO ESTA | Baixo | Alta | Medio | manter contrato atual e so revisar UX fina se uso real pedir |
| Extrato financeiro | financeiro | `financeiro:extrato-list` -> `/extratos/` | `ExtratoFinanceiroView` | `financeiro/conta_extrato.html` | Nao | N/A | N/A | descricao/documento poderiam entrar apenas em futura microetapa analitica | Sim | `data_inicial`, `data_final`, `exibir_observacao` | `contas` | busca textual por descricao/documento e futuro possivel | `get()` + `getlist(contas)` | N/A | N/A | Sim | Sim | Sim | OK COMO ESTA | Baixo | Alta | Medio | manter recorte atual; futura busca textual so se houver demanda real |
| Fechamento do periodo | financeiro | `financeiro:prestacao-contas` -> `/prestacao-contas/` | `PrestacaoContasFinanceiroView` | `financeiro/prestacao_contas.html` | Nao | N/A | N/A | nao se aplica ao recorte consolidado | Sim | periodo, opcoes booleanas | `contas` | contas ja cobrem o caso principal | `get()` + `getlist(contas)` | N/A | N/A | N/A | Sim | Sim | OK COMO ESTA | Baixo | Alta | Medio | sem mudanca funcional; apenas padrao visual se necessario |
| Balancete institucional | financeiro | `financeiro:balancete-institucional` -> `/balancete-institucional/` | `BalanceteInstitucionalFinanceiroView` | `financeiro/balancete_institucional.html` | Nao | N/A | N/A | nao se aplica ao recorte contabil/documental | Sim | formato, composicao, assinaturas, opcoes booleanas | `contas` | contas ja cobrem o caso principal | `get()` + `getlist(contas)` | N/A | N/A | N/A | Sim | Sim | OK COMO ESTA | Medio | Alta | Medio | manter padrao atual e nao abrir nova frente sem decisao da usuaria |
| Evolucao por categorias | financeiro | `financeiro:evolucao-categorias` -> `/evolucao-categorias/` | `EvolucaoCategoriasFinanceiroView` | `financeiro/evolucao_categorias.html` | Sim, mas local ao seletor | Sim | busca local no seletor de categorias/subcategorias | sem busca textual direta por descricao de lancamento, o que e aceitavel aqui | Sim | `modo`, `escopo`, `leitura`, `granularidade`, periodo | `contas`, `categorias` | sem necessidade imediata extra | `get()` + `getlist(contas,categorias)` | N/A | N/A | N/A | Sim | Sim | OK COMO ESTA | Medio | Alta | Medio | futura padronizacao visual do seletor, sem mexer na regra analitica |
| Frequencia por competencias | financeiro | `financeiro:frequencia-competencias` -> `/frequencia-competencias/` | `FrequenciaCompetenciasView` | `financeiro/frequencia_competencias.html` | Nao | N/A | N/A | nome do favorecido e subcategoria poderiam virar busca futura, mas nao sao obrigatorios agora | Sim | `categoria`, `status`, `formato_matriz`, periodo de competencia | Nenhum | `categoria` poderia virar multi no futuro | `get()` | N/A | N/A | N/A | Sim | Sim | FUTURO / BACKLOG | Medio | Alta | Medio | avaliar multi-selecao de subcategorias controladas apenas depois da validacao operacional |
| Auditoria do financeiro | financeiro | `financeiro:auditoria-lancamento-list` -> `/auditoria/lancamentos/` | `AuditoriaLancamentoFinanceiroListView` | `financeiro/auditoria_lancamento_list.html` | Nao | N/A | N/A | `modelo`, `campos_alterados`, nome do usuario, trecho before/after nao sao pesquisaveis | Sim | `acao`, `usuario`, `registro_id`, datas | Nenhum | `acao`, `usuario`, possivelmente `modelo` | `get()` | N/A | Parcial (`return_to` contextual) | N/A | N/A | Sim | PRECISA BUSCA TEXTUAL MAIS AMPLA | Alto | Alta | Baixo | adicionar busca textual e avaliar multi-selecao de acao/usuario |
| Favorecidos financeiros | financeiro | `financeiro:pessoa-list` -> `/pessoas/` | `PessoaFinanceiraListView` | `financeiro/pessoa_list.html` | Sim | Sim | `nome`, `codigo` | `documento`, `email`, `telefone`, `tipo_pessoa`, status/recorrencia | Nao | Nenhum | Nenhum | `tipo`, `ativo`, `contribuinte_recorrente` | `get()` | N/A | Sim | Sim | N/A | Sim | PRECISA BUSCA TEXTUAL MAIS AMPLA | Medio | Alta | Baixo | ampliar busca e adicionar filtros simples de status/recorrencia |
| Historico do favorecido | financeiro | `financeiro:pessoa-historico` -> `/pessoas/<pk>/historico/` | `PessoaFinanceiraHistoricoView` | `financeiro/pessoa_historico.html` | Sim | Sim | `descricao`, `numero_documento` | `categoria`, `centro_custo`, `conta.nome`, `conta_destino.nome` | Sim | `tipo`, `status`, `conta`, datas | Nenhum | `conta` | `get()` | N/A | Nao ha acoes contextuais relevantes | N/A | Nao | Sim | PRECISA BUSCA TEXTUAL MAIS AMPLA | Medio | Alta | Baixo | ampliar busca textual e avaliar filtro multiplo de conta |
| Contas financeiras | financeiro | `financeiro:conta-list` -> `/contas/` | `ContaFinanceiraListView` | `financeiro/conta_list.html` | Sim | Sim | `nome` | `descricao`, `tipo_conta.nome`, `mensagem_indisponibilidade` | Sim | `ativa` | Nenhum | `tipo_conta`, `disponibilidade` | `get()` | N/A | Sim | Sim | N/A | Sim | PRECISA BUSCA TEXTUAL MAIS AMPLA | Medio | Media | Baixo | ampliar busca e adicionar filtros estruturais leves |
| Centros de custo | financeiro | `financeiro:centro-custo-list` -> `/centros-custo/` | `CentroCustoListView` | `financeiro/centro_custo_list.html` | Sim | Sim | `codigo`, `nome` | `ativo` | Nao | Nenhum | Nenhum | `ativo` | `get()` | N/A | Sim | Sim | N/A | Sim | PRECISA PADRONIZACAO DE UX | Baixo | Media | Baixo | adicionar filtro de status para alinhar com outros cadastros |
| Categorias financeiras | financeiro | `financeiro:categoria-list` -> `/categorias/` | `CategoriaFinanceiraListView` | `financeiro/categoria_list.html` | Sim | Sim | `nome` | `categoria_pai.nome`, `ativo`, `controla_recorrencia_competencia` | Sim | `tipo` | Nenhum | `categoria_pai`, `ativo`, `controla_recorrencia_competencia` | `get()` | N/A | Sim | Sim | N/A | Sim | PRECISA BUSCA TEXTUAL MAIS AMPLA | Medio | Media | Baixo | ampliar busca por hierarquia e adicionar filtros simples de status/frequencia |
| Tabelas personalizadas | financeiro | `financeiro:tabela-personalizada-list` -> `/controles-internos/tabelas-personalizadas/` | `TabelaPersonalizadaListView` | `financeiro/tabela_personalizada_list.html` | Sim | Sim | `nome` | `descricao` | Sim | `status` | Nenhum | sem necessidade imediata | `get()` | N/A | Sim | N/A | N/A | Sim | OK COMO ESTA | Baixo | Media | Baixo | futura ampliacao de busca por descricao, se uso real justificar |
| Linhas da tabela personalizada | financeiro | `financeiro:tabela-personalizada-linha-list` -> `/controles-internos/tabelas-personalizadas/<id>/linhas/` | `TabelaPersonalizadaLinhaListView` | `financeiro/tabela_personalizada_linha_list.html` | Sim | Sim | valores textuais/normalizados das colunas visiveis, inclusive formula controlada em leitura | colunas ocultas/arquivadas fora da visualizacao atual | Sim | `status_linha`, `ordenar`, `direcao`, `visualizacao` | `colunas` (visualizacao) | filtros estruturados multi poderiam evoluir no futuro | `get()` + `getlist(colunas)` | N/A | Sim | Sim | Sim | Sim | OK COMO ESTA | Medio | Alta | Medio | manter contrato atual; apenas evoluir filtros estruturados se houver demanda |
| Autores | biblioteca | `biblioteca:autor-list` -> `/autores/` | `AutorListView` | `biblioteca/autor_list.html` | Nao | N/A | N/A | `nome`, `biografia` | Nao | Nenhum | Nenhum | N/A | Nenhum uso de GET | N/A | Nao | N/A | N/A | Nao | PRECISA BUSCA TEXTUAL | Medio | Media | Baixo | adicionar busca por nome/biografia e botao limpar |
| Livros | biblioteca | `biblioteca:livro-list` -> `/livros/` | `LivroListView` | `biblioteca/livro_list.html` | Nao | N/A | N/A | `titulo`, `autores`, faixa de estoque | Sim | Nenhum | Nenhum | `autores`, status de estoque | Nenhum uso de GET | N/A | Nao | N/A | N/A | Nao | PRECISA BUSCA TEXTUAL MAIS AMPLA | Alto | Media | Baixo | adicionar busca por titulo/autores e filtro por estoque |
| Vendas | biblioteca | `biblioteca:venda-list` -> `/vendas/` | `VendaListView` | `biblioteca/venda_list.html` | Nao | N/A | N/A | `livro`, periodo, valor | Sim | Nenhum | Nenhum | `livro`, periodo | Nenhum uso de GET | N/A | Nao | N/A | N/A | Nao | PRECISA BUSCA TEXTUAL | Medio | Media | Baixo | adicionar busca por livro e filtro de periodo |
| Emprestimos | biblioteca | `biblioteca:emprestimo-list` -> `/emprestimos/` | `EmprestimoListView` | `biblioteca/emprestimo_list.html` | Nao | N/A | N/A | `livro`, `leitor`, `status`, periodo de emprestimo/devolucao | Sim | Nenhum | Nenhum | `status`, `livro`, `leitor` | Nenhum uso de GET | N/A | Nao | N/A | N/A | Nao | PRECISA BUSCA TEXTUAL MAIS AMPLA | Alto | Media | Baixo | adicionar busca e filtros basicos de operacao diaria |
| Perfis de acesso | configuracoes | `configuracoes:perfil-list` -> `/perfis/` | `PerfilAcessoListView` | `configuracoes/perfil_acesso_list.html` | Nao | N/A | N/A | `nome`, `descricao`, status ativo | Nao | Nenhum | Nenhum | `ativo` | Nenhum uso de GET | N/A | Nao | N/A | N/A | Nao | PRECISA BUSCA TEXTUAL | Medio | Media | Baixo | adicionar busca por nome/descricao e filtro de status |
| Usuarios e perfis | configuracoes | `configuracoes:usuario-perfil-list` -> `/usuarios/` | `UsuarioPerfilAcessoListView` | `configuracoes/usuario_perfil_list.html` | Nao | N/A | N/A | `username`, nome completo, `email`, `perfil`, `is_active` | Sim | Nenhum | Nenhum | `perfil`, `status` | Nenhum uso de GET | N/A | Nao | N/A | N/A | Nao | PRECISA BUSCA TEXTUAL MAIS AMPLA | Alto | Media | Baixo | adicionar busca por usuario/email e filtros por perfil/status |

## 4. Achados principais

- o `financeiro` ja tem um nucleo mais maduro de filtros estruturados nas telas de maior uso:
  - `Lancamentos`
  - `Resumo`
  - `Extrato`
  - `Prestacao`
  - `Balancete`
  - `Evolucao`
  - `Tabelas personalizadas`
- o padrao mais consistente de selecao multipla hoje esta em contas (`getlist(contas)`) e, na `Evolucao`, tambem em categorias (`getlist(categorias)`)
- `biblioteca` e `configuracoes` ainda estao em estado basal de listagem, sem busca textual, sem filtros, sem limpar filtros e sem preservacao de query string
- no `financeiro`, os maiores gaps atuais nao estao nos relatorios principais, mas em:
  - `Auditoria`
  - `Historico do favorecido`
  - cadastros auxiliares (`Favorecidos`, `Categorias`, `Contas`, `Centros de custo`)
- a preservacao de filtros em exportacao ja esta boa nos pontos em que ha XLSX relevante:
  - `Lancamentos`
  - `Extrato`
  - cadastros auxiliares do `financeiro`
  - `Tabelas personalizadas`

## 5. Oportunidades de melhoria

- ampliar busca textual de `financeiro` para campos operacionais que a usuaria ja enxerga na grade
- padronizar filtros simples de status/ativo/recorrencia nos cadastros auxiliares do `financeiro`
- levar o padrao minimo de `form method="get" + Filtrar + Limpar` para `biblioteca` e `configuracoes`
- revisar telas em que ainda faz sentido futuro adotar selecao multipla:
  - `Auditoria`
  - `Historico do favorecido`
  - `Frequencia por competencias`

## 6. Priorizacao recomendada

- Alta
  - `Auditoria do financeiro`
  - `Historico do favorecido`
  - `Lancamentos financeiros` (apenas para ampliar busca textual, sem mexer no filtro hierarquico)
  - `Emprestimos`
  - `Usuarios e perfis`
- Media
  - `Favorecidos`
  - `Categorias`
  - `Contas`
  - `Livros`
  - `Vendas`
  - `Perfis de acesso`
- Baixa
  - `Resumo`
  - `Extrato`
  - `Prestacao`
  - `Balancete`
  - `Tabelas personalizadas`

## 7. Sequencia sugerida de microetapas futuras

1. `financeiro`: ampliar busca textual e padronizar filtros em `Auditoria` e `Historico do favorecido`
2. `financeiro`: ampliar busca textual dos cadastros auxiliares (`Favorecidos`, `Categorias`, `Contas`, `Centros de custo`)
3. `biblioteca`: adicionar busca textual e filtros basicos nas quatro listagens operacionais
4. `configuracoes`: adicionar busca textual e filtros por status/perfil nas listagens funcionais
5. revisar, so depois, se alguma tela pede selecao multipla extra ou exportacao/impressao nova

## 8. Recomendacao objetiva sobre a proxima etapa

A proxima etapa mais segura e de maior retorno operacional e:

- `financeiro`: ajustar `Auditoria do financeiro` e `Historico do favorecido` para ganhar busca textual mais ampla e filtros mais consistentes, sem alterar calculo financeiro nem contratos ja validados dos relatorios principais.
