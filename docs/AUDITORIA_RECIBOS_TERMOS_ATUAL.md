# Auditoria do comportamento atual de recibos e termos no financeiro

Data: 2026-06-10  
Branch: `feat/reinicio-financeiro`

## 1. Objetivo

Registrar, com base no codigo atual, templates atuais, rotas, parametros e testes existentes, como os fluxos de `recibos` e `termos` funcionam hoje no modulo `financeiro`.

## 2. Escopo da auditoria

- rotas, views e helpers documentais de `recibos` e `termos`
- integracao dessas acoes com a `lancamento_list`
- parametros recebidos por cada fluxo
- relacao entre filtros da listagem, checkboxes e documentos gerados
- agrupamento por favorecido, descricao, categoria e subcategoria
- uso atual de `mensagem_recibo`
- diferencas entre recibo individual, recibo em lote, recibos por favorecido, recibo especial e termo anual

Fora do escopo:

- alterar regra funcional
- alterar templates ou layout
- criar nova acao documental
- redefinir a regra futura por categoria pai/subcategoria

## 3. Mapa das rotas e views de recibos/termos

| Opcao | Rota | View | Template | Status atual |
| --- | --- | --- | --- | --- |
| Recibo individual | `financeiro:lancamento-recibo` | `LancamentoFinanceiroReciboView` | `financeiro/lancamento_recibo.html` | ativo |
| Recibo especial - escolher favorecido destinatario | `financeiro:lancamento-recibo-especial-selecionar-favorecido` | `LancamentoFinanceiroReciboEspecialSelecionarFavorecidoView` | `financeiro/lancamento_recibo_especial_form.html` | ativo |
| Recibo especial - documento final | `financeiro:lancamento-recibo-especial` | `LancamentoFinanceiroReciboEspecialView` | `financeiro/lancamento_recibo_especial.html` | ativo |
| Recibo em lote tecnico de mesmo favorecido | `financeiro:lancamento-recibo-lote` | `LancamentoFinanceiroReciboLoteView` | `financeiro/lancamento_recibo.html` | ativo, mas nao e a acao principal da listagem |
| Recibos em lote por favorecido | `financeiro:lancamento-recibos-por-favorecido` | `LancamentoFinanceiroRecibosPorFavorecidoView` | `financeiro/lancamento_recibo.html` | ativo e e o fluxo real da listagem |
| Termo anual de quitacao | `financeiro:lancamento-termo-anual-quitacao` | `LancamentoFinanceiroTermoAnualQuitacaoView` | `financeiro/lancamento_documentos_por_favorecido.html` | ativo |
| Termos anuais por favorecido | `financeiro:lancamento-termos-anuais-quitacao-por-favorecido` | `LancamentoFinanceiroTermosAnuaisQuitacaoPorFavorecidoView` | redireciona para a rota singular | compatibilidade tecnica |
| Acoes em lote da listagem | `financeiro:lancamento-acoes-lote` | `LancamentoFinanceiroAcoesLoteView` | acionada por `POST` da listagem | ativo |
| Listagem de lancamentos | `financeiro:lancamento-list` | `LancamentoFinanceiroListView` | `financeiro/lancamento_list.html` | origem principal das acoes em lote |

## 4. Mapa dos templates envolvidos

| Template | Papel atual |
| --- | --- |
| `financeiro/lancamento_list.html` | filtros, checkboxes, acao em lote, botao de termo anual e links documentais por linha |
| `financeiro/lancamento_recibo.html` | pagina de recibo individual ou multigrupo de recibos |
| `financeiro/_lancamento_recibo_documento.html` | documento base do recibo comum |
| `financeiro/lancamento_recibo_especial_form.html` | escolha do favorecido destinatario do recibo especial |
| `financeiro/lancamento_recibo_especial.html` | pagina final do recibo especial |
| `financeiro/_lancamento_recibo_especial_documento.html` | documento base do recibo especial |
| `financeiro/lancamento_documentos_por_favorecido.html` | documento de termo anual por favorecido |

## 5. Como funciona hoje

| Opcao | Como e acionada | Fonte de dados | Agrupamento principal | Categoria/subcategoria | `mensagem_recibo` | Observacoes |
| --- | --- | --- | --- | --- | --- | --- |
| Recibo individual | link por linha na listagem ou URL direta por `pk` | um unico lancamento | nao agrupa | usa a `categoria` do proprio lancamento apenas para mensagem final | sim, da categoria do lancamento, com fallback institucional | nao lista itens; `Referente a` usa `descricao` |
| Recibo em lote tecnico | URL direta com `?ids=...` | ids explicitos via GET | um unico documento, exige mesmo favorecido | nao bloqueia por categoria unica | nao | consolida itens por descricao exata |
| Recibos por favorecido | acao em lote da listagem ou link por linha de rateio | ids explicitos via GET | um documento por favorecido no mesmo HTML | categoria nao separa grupos nem aparece no topo | nao | e o fluxo real do botao `Recibos em lote` da listagem |
| Recibo especial | acao em lote da listagem + escolha manual de destinatario | ids explicitos via GET/POST + `destinatario` manual | um unico documento final | nao depende de categoria unica | nao | aceita multiplos favorecidos originais; cada linha mostra descricao + favorecido original |
| Termo anual de quitacao | botao proprio na listagem com GET atual | filtros atuais da listagem, sem ids selecionados | um termo por favorecido no mesmo HTML | nao agrupa nem separa por categoria | nao usa mensagem de categoria; usa fallback institucional | restringe internamente a receitas quitadas com favorecido e sem rateio |

## 6. Entrada de dados / parametros por opcao

| Opcao | Metodo | Parametros principais | Usa ids selecionados? | Usa filtros da listagem? |
| --- | --- | --- | --- | --- |
| Recibo individual | `GET` | `pk` na URL | nao | nao |
| Recibo em lote tecnico | `GET` | `ids` CSV | sim | nao, salvo se o chamador montar os ids a partir da tela filtrada |
| Recibos por favorecido | `POST` na listagem -> redirect `GET` | `lancamentos_selecionados[]`, `acao_lote`, `filtros_retorno`, depois `ids` CSV | sim | so de forma indireta, via escolha manual dos checkboxes no recorte filtrado |
| Recibo especial - escolha | `POST` na listagem -> redirect `GET` | `lancamentos_selecionados[]`, `acao_lote`, `filtros_retorno`, depois `ids` CSV | sim | so de forma indireta, via checkboxes |
| Recibo especial - final | `GET` | `ids`, `destinatario`, opcional `filtros` | sim | apenas para retorno |
| Termo anual | `GET` | mesmos filtros da listagem, especialmente `data_inicial` e `data_final` | nao | sim, diretamente |
| Termos anuais por favorecido | `GET` | mesma query da rota singular | nao | sim, por redirecionamento |

## 7. Usa filtros da listagem?

| Opcao | Resposta objetiva | Detalhe |
| --- | --- | --- |
| Recibo individual | nao | abre um lancamento especifico |
| Recibo em lote tecnico | nao, por contrato proprio | le apenas `ids` passados na URL |
| Recibos por favorecido | nao diretamente | o documento final le apenas `ids`; os filtros so influenciam se o usuario selecionou itens a partir da grade filtrada |
| Recibo especial | nao diretamente | o fluxo final tambem le apenas `ids`; `filtros` existe so para voltar com aviso/retorno |
| Termo anual | sim | reutiliza `_filtrar_lancamentos_por_parametros(request.GET)` antes da triagem propria do termo |
| Termos anuais por favorecido | sim | so redireciona para a rota singular |

## 8. Usa selecao manual?

| Opcao | Resposta objetiva | Detalhe |
| --- | --- | --- |
| Recibo individual | nao | um lancamento por vez |
| Recibo em lote tecnico | sim, se o chamador montar `ids` | nao ha UI principal especifica na listagem para essa rota |
| Recibos por favorecido | sim | usa checkboxes `lancamentos_selecionados[]` |
| Recibo especial | sim | usa checkboxes `lancamentos_selecionados[]` e depois destinatario manual |
| Termo anual | nao | ignora checkboxes; usa o filtro GET atual |

Observacao importante:

- nao existe opcao atual de `todos filtrados` no backend para recibos
- o `Marcar todos` da listagem atua apenas sobre os checkboxes visiveis na pagina atual
- com paginacao, recibos em lote e recibo especial nao abrangem automaticamente as outras paginas filtradas

## 9. Agrupa por favorecido?

| Opcao | Agrupa por favorecido? | Como |
| --- | --- | --- |
| Recibo individual | nao | usa o favorecido do unico lancamento |
| Recibo em lote tecnico | exige um unico favorecido | falha se os ids tiverem mais de um favorecido |
| Recibos por favorecido | sim | separa os ids selecionados por `pessoa_id` e gera um documento por grupo |
| Recibo especial | nao por favorecido original | aceita multiplos favorecidos originais e usa um destinatario manual unico |
| Termo anual | sim | agrupa o resultado filtrado por `pessoa_id` |

## 10. Agrupa por categoria / subcategoria?

| Opcao | Agrupamento atual por categoria/subcategoria |
| --- | --- |
| Recibo individual | nao agrupa; usa um lancamento so |
| Recibo em lote tecnico | nao separa por categoria; consolida apenas por descricao exata |
| Recibos por favorecido | nao separa por categoria nem por subcategoria; consolida apenas por favorecido e depois por descricao exata |
| Recibo especial | nao separa por categoria nem por subcategoria; lista cada lancamento selecionado |
| Termo anual | nao separa por categoria nem por subcategoria; lista os lancamentos de cada favorecido linha a linha |

Confirmacoes objetivas do codigo atual:

- hoje nao ha suporte documental proprio a multiplas categorias ou multiplas subcategorias como eixos do recibo
- hoje categoria pai nao vira agrupador documental do recibo
- hoje subcategoria nao vira agrupador documental do recibo
- hoje o lote por favorecido mistura categorias diferentes do mesmo favorecido se os ids selecionados entrarem juntos

## 11. Usa `mensagem_recibo`?

| Opcao | Usa `mensagem_recibo`? | De onde |
| --- | --- | --- |
| Recibo individual | sim | `lancamento.categoria.mensagem_recibo`, com fallback para `ConfiguracaoInstitucional.mensagem_padrao_recibo` e depois texto fixo |
| Recibo em lote tecnico | nao | `categoria_documental` nao e passada ao helper |
| Recibos por favorecido | nao | o helper e chamado com `usar_mensagem_categoria=False` |
| Recibo especial | nao | chama `_contexto_recibo_institucional(usar_mensagem_categoria=False)` |
| Termo anual | nao | usa apenas `_contexto_institucional_documental()` com mensagem institucional padrao |

Consequencia pratica:

- se categoria pai e subcategoria tiverem mensagens diferentes, isso so importa hoje no recibo individual
- os fluxos em lote e o termo anual nao escolhem entre mensagens de categoria pai ou subcategoria, porque nao usam `mensagem_recibo`

## 12. Cenarios praticos A a F

### Cenario A

- Joao tem dois lancamentos de `Doacao`
- em `Recibos em lote`/`Recibos por favorecido`, se os dois ids forem selecionados:
  - sai um unico recibo para Joao
  - se a `descricao` for exatamente igual, vira um unico item consolidado com soma
  - se a `descricao` for diferente, sai um item por descricao
- em `Termo anual`, sai um unico termo para Joao com duas linhas e total final

### Cenario B

- Joao tem `Doacao` e `Contribuicao`
- se a listagem estiver filtrada para `Doacao` e o usuario selecionar so esse recorte, `Contribuicao` fica fora do recibo
- se o usuario emitir sem filtro e selecionar os dois lancamentos, o recibo por favorecido mistura ambos no mesmo documento
- no termo anual, sem filtro por categoria/subcategoria, ambos entram no mesmo termo se forem receitas quitadas com favorecido e sem rateio dentro do periodo

### Cenario C

- Maria tem duas subcategorias da mesma categoria pai
- hoje o sistema nao agrupa pela categoria pai nem separa por subcategoria
- recibo por favorecido mistura os itens no mesmo documento, respeitando apenas favorecido e descricao
- termo anual tambem mistura as duas subcategorias no mesmo termo da Maria

### Cenario D

- lista filtrada por `categoria_pai`
- a listagem expande a categoria pai para as subcategorias filhas
- o termo anual respeita esse filtro diretamente, porque usa o mesmo helper de filtragem da listagem
- os recibos em lote respeitam isso apenas indiretamente: se o usuario selecionar os itens visiveis desse recorte, os ids escolhidos refletirao as subcategorias filhas

### Cenario E

- lista filtrada por `subcategoria`
- o termo anual sai apenas daquela subcategoria, desde que o restante da regra do termo tambem seja satisfeito
- os recibos em lote/recibo especial saem apenas daquela subcategoria se o usuario selecionar somente os ids exibidos no recorte

### Cenario F

- ha lancamentos de favorecidos diferentes
- `Recibos por favorecido` gera documento separado por favorecido
- `Recibo em lote tecnico` bloqueia e nao aceita ids de favorecidos diferentes
- `Recibo especial` aceita favorecidos diferentes e gera um unico documento com destinatario manual
- `Termo anual` gera um termo por favorecido no mesmo HTML

## 13. Riscos de mexer

1. `LancamentoFinanceiroAcoesLoteView` hoje trata `emitir_recibos`, `recibo_lote` e `recibos_lote_por_favorecido` como aliases funcionais; mudar isso sem cuidado pode quebrar a listagem e testes existentes.
2. `_montar_contexto_recibo_documento()` concentra o contrato do recibo comum; alterar esse helper impacta recibo individual, recibo em lote tecnico e recibos por favorecido ao mesmo tempo.
3. O termo anual usa o mesmo helper geral de filtros da listagem e depois aplica uma triagem propria; mudar a ordem desses filtros pode mudar silenciosamente o universo documental.
4. Hoje a selecao em lote e por checkbox visivel/pagina atual. Implementar `todos filtrados` sem SPEC propria mudaria o contrato operacional da listagem.
5. O uso de `mensagem_recibo` e desigual entre fluxos; tentar unificar sem decisao explicita pode mudar documentos ja homologados.
6. O fluxo do recibo especial e propositalmente isolado; misturar sua regra com o recibo comum pode reabrir contratos ja estabilizados.

## 14. Oportunidades reais de melhoria

1. Documentar na UI da listagem que `Recibos em lote` usa apenas os itens marcados na pagina atual.
2. Se houver necessidade real, abrir SPEC propria para `todos filtrados` em recibos.
3. Decidir em SPEC separada se o eixo documental futuro sera:
   - por favorecido apenas
   - por favorecido + categoria pai
   - por favorecido + subcategoria
4. Explicitar na UX que o `Termo anual` nasce do filtro atual e nao dos checkboxes.
5. Se a regra futura exigir categoria/subcategoria documental, isolar essa mudanca em helper novo em vez de reescrever o contrato atual do recibo comum.

## 15. Recomendacao objetiva de proximos passos

1. Considerar o estado atual como:
   - recibos em lote baseados em `ids` selecionados manualmente
   - termo anual baseado no filtro GET atual da listagem
   - agrupamento documental principal por favorecido, nao por categoria/subcategoria
2. Antes de qualquer implementacao nova, abrir uma SPEC curta decidindo:
   - se recibos futuros continuam por favorecido puro
   - se categoria pai pode virar agrupador documental
   - se subcategoria deve continuar apenas como detalhe operacional
3. Se a prioridade for operacao/UX, a melhoria mais segura e:
   - deixar a listagem mais explicita sobre `selecionados` versus `resultado filtrado`
   - sem mexer ainda no contrato do documento gerado
