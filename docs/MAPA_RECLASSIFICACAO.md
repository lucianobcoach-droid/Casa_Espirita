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

Status apos auditoria: IMPLEMENTADO COM PENDENCIAS FUTURAS

Motivo:
Há registros antigos tratando autenticação, perfis, permissões e matriz de acesso como frente estrutural. É necessário confirmar o que está implementado no código, o que está apenas documentado e o que ainda é futuro.

Achado da auditoria:
- login, logout e recuperacao/reset de senha existem em `configuracoes.urls` e `configuracoes.views`, usando as views padrao do Django com templates proprios
- existem models de permissao/perfil/vinculo em `configuracoes.models`: `PermissaoSistema`, `PerfilAcesso`, `PerfilPermissaoSistema` e `UsuarioPerfilAcesso`
- o vinculo usuario -> perfil-base existe como `OneToOneField` para o usuario Django
- ha seed/carga inicial de perfis e permissoes em migrations, incluindo matriz para `financeiro`, `biblioteca`, `configuracoes` e admin tecnico
- ha enforcement backend central em `configuracoes.permissoes.PermissaoSistemaMixin`, com mixins especificos em `financeiro`, `biblioteca` e `configuracoes`
- ha template tags de permissao e renderizacao condicional de menus/acoes nos templates principais
- o financeiro possui permissoes aplicadas nas views, relatorios, cadastros, importacao/exportacao, recibos, auditoria e acoes em lote
- a biblioteca possui permissoes aplicadas nas views e menus de autores, livros, vendas e emprestimos
- configuracoes possui permissoes aplicadas em `SiteConfig`, listagem/detalhe de perfis e listagem/edicao de vinculo usuario-perfil
- existe matriz documental em `docs/MATRIZ_PERMISSOES.md`

Classificacao documental:
- IMPLEMENTADO COM PENDENCIAS FUTURAS
- BAIXA DOCUMENTAL REALIZADA: retirado o estado generico de duvida/requer conferencia no codigo

Pendencias futuras:
- extras individuais por usuario e bloqueios individuais ainda permanecem futuros
- log de acesso ao sistema permanece futuro
- refinamento humano da matriz pode continuar como melhoria de governanca
- preferencias por perfil/usuario permanecem futuras
- administracao funcional avancada da matriz ainda pode evoluir alem da UI minima atual

Documentos relacionados:
- docs/CEREBRO_PROJETO.md
- docs/STATE.md
- docs/MATRIZ_PERMISSOES.md

---

### 2. Histórico por favorecido

Status inicial: DÚVIDA / REQUER CONFERÊNCIA NO CÓDIGO

Status apos auditoria: IMPLEMENTADO COM PENDÊNCIAS FUTURAS

Motivo:
A funcionalidade aparece como solicitação importante em chats e documentos. É necessário confirmar se já está totalmente implementada, parcialmente implementada ou ainda pendente.

Achado da auditoria:
- existe rota `financeiro:pessoa-historico` em `pessoas/<int:pk>/historico/`
- existe view `PessoaFinanceiraHistoricoView` com filtros por periodo, tipo, status, conta e busca textual
- existe template `pessoa_historico.html`
- a listagem de favorecidos (`pessoa_list.html`) expõe ação `Historico` quando o usuario tem permissao de listar lancamentos

Pendencias futuras:
- exportacao especifica do historico, caso o uso real justifique

Classificacao documental:
- IMPLEMENTADO COM PENDÊNCIAS FUTURAS

Documentos relacionados:
- docs/CEREBRO_PROJETO.md
- docs/STATE.md
- docs/ROADMAP_FINANCEIRO.md

---

### 3. Recibos por favorecido e recibos em lote

Status inicial: DÚVIDA / REQUER CONFERÊNCIA NO CÓDIGO

Status apos auditoria: IMPLEMENTADO COM PENDÊNCIAS FUTURAS

Motivo:
Há registros sobre recibo em lote, recibos por favorecido e documentos financeiros. Precisa ser conferido o estado real no código.

Achado da auditoria:
- existe recibo individual por lancamento em `financeiro:lancamento-recibo`
- existe rota tecnica `financeiro:lancamento-recibo-lote` para recibo em lote de um mesmo favorecido
- existe rota atual `financeiro:lancamento-recibos-por-favorecido`, que agrupa os lancamentos selecionados por favorecido e renderiza um ou mais recibos no mesmo documento
- a `lancamento_list.html` expoe a acao visivel `Recibos em lote`; a view de acoes em lote redireciona para o fluxo agrupado por favorecido

Pendencias futuras:
- refinamentos documentais/visuais, PDF/anexos ou regras futuras de recorrencia, se aprovados em microetapas proprias

Classificacao documental:
- IMPLEMENTADO COM PENDÊNCIAS FUTURAS

Documentos relacionados:
- docs/STATE.md
- docs/CODEX_RESULTADO.md
- docs/ROADMAP_FINANCEIRO.md

---

### 4. Termo anual de quitação

Status inicial: DÚVIDA / REQUER CONFERÊNCIA NO CÓDIGO

Status apos auditoria: IMPLEMENTADO COM PENDÊNCIAS FUTURAS

Motivo:
Há registros sobre termo anual de quitação baseado nos filtros atuais da listagem financeira. Precisa confirmar se está implementado, validado e se ainda há pendências.

Achado da auditoria:
- existe rota `financeiro:lancamento-termo-anual-quitacao`
- existe view `LancamentoFinanceiroTermoAnualQuitacaoView`
- existe template compartilhado `lancamento_documentos_por_favorecido.html`
- a acao `Termo anual de quitacao` parte da `lancamento_list.html` e usa o resultado filtrado atual
- a rota plural `financeiro:lancamento-termos-anuais-quitacao-por-favorecido` permanece apenas como compatibilidade tecnica e redireciona para o fluxo unificado

Classificacao documental:
- IMPLEMENTADO COM PENDÊNCIAS FUTURAS

Observacao sobre fluxo antigo:
- a antiga direcao de `relatorio anual por favorecido` como tela propria foi substituida por acoes documentais na listagem de lancamentos
- classificacao do fluxo antigo: HISTÓRICO / SUBSTITUÍDO POR FLUXO ATUAL

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

Status apos auditoria documental/tecnica: IMPLEMENTADO COM PENDENCIAS FUTURAS / AGUARDANDO HOMOLOGACAO

Motivo:
Há registros sobre importação, planilhas, categorias, favorecidos, contas e relatórios de inconsistência. É necessário separar o que já existe, o que foi testado e o que ainda precisa implementação.

Auditoria no codigo confirmou que a central de importacoes do financeiro existe e cobre importacao comum de lancamentos, exportacao/modelo de lancamentos, cadastros auxiliares de contas, favorecidos, centros de custo e categorias/subcategorias, validacao estrutural da planilha, validacao linha a linha com rotulos amigaveis, trava de dominio preenchido e gravacao transacional all-or-nothing. O fluxo comum suporta lancamentos simples, transferencias simples e rateio em ate 5 blocos na mesma linha. Backup/restauracao tecnica de rateios e regras automaticas existem por comandos proprios.

Baixa documental:
- IMPLEMENTADO: central de importacoes, planilhas-modelo, importacao/exportacao comum de lancamentos, importacoes auxiliares, trava de dominio vazio, validacoes estruturais e por linha, relatorio de inconsistencias, mensagens amigaveis e gravacao transacional sem importacao parcial.
- IMPLEMENTADO COM PENDENCIAS FUTURAS: duplicidades/conflitos possuem tratamento basico e seguro, mas podem evoluir para resolucao assistida; preflight existe como bloqueio/mensagem, mas pode ficar mais visivel.
- FUTURO REAL: preview operacional antes de gravar, importacao parcial, tratamento avancado de duplicidades, fluxo especifico para rateios acima de 5 blocos no caminho comum e importacao historica guiada alem do contrato atual.
- AGUARDANDO HOMOLOGACAO: uso real com planilhas historicas da usuaria e massa completa de cadastros auxiliares.

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

Status apos decisao da usuaria: HOMOLOGACAO PROGRESSIVA REALIZADA / USO REAL ACOMPANHADO

Motivo:
Após vários ajustes funcionais e visuais, ainda é necessária uma rodada de teste completo local para validar fluxo real, especialmente antes de novas frentes grandes.

Reclassificacao:
- os fluxos principais do financeiro foram testados localmente de forma progressiva durante o desenvolvimento das microetapas
- nao e necessario repetir agora uma homologacao ponta a ponta completa de tudo que ja foi testado e validado
- permanecem como acompanhamento de uso real: importacoes com massa definitiva/planilhas historicas completas, relatorios impressos em volume real e rotina diaria da Casa

Documentos relacionados:
- docs/STATE.md
- docs/ROADMAP_FINANCEIRO.md

---

### 13. Favorecido duplicado por nome

Status inicial: FUTURO REAL / BUG OPERACIONAL

Status apos baixa documental: IMPLEMENTADO

Motivo:
Foi levantado que o cadastro de favorecidos permite duplicidade por nome. Antes de implementar, e necessario conferir a regra atual de validacao, a existencia de duplicados ja cadastrados e a melhor normalizacao de nome.

Achado da baixa:
- `PessoaFinanceira.clean()` bloqueia duplicidade por nome normalizado e ignora o proprio registro na edicao.
- A importacao auxiliar de favorecidos valida conflito por nome normalizado contra cadastro existente e contra linhas repetidas na propria planilha.
- A regra permanente esta registrada em `docs/REGRAS_NEGOCIO.md`.

Classificacao documental:
- IMPLEMENTADO
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

Status apos baixa documental: DIRETRIZ IMPLEMENTADA / APLICACAO PROGRESSIVA FUTURA

Motivo:
Foi definida regra geral de que cadastros do sistema nao devem duplicar identificadores-chave, como codigo, nome ou equivalentes, conforme a natureza de cada cadastro. A extensao para contas, categorias/subcategorias, centros de custo e cadastros futuros deve ocorrer em microetapas proprias.

Achado da baixa:
- A regra-mae esta registrada em `docs/REGRAS_NEGOCIO.md`.
- A implementacao pratica confirmada nesta baixa esta restrita a favorecidos/pessoas financeiras.
- Contas, categorias/subcategorias, centros de custo e demais cadastros permanecem em aplicacao progressiva futura.

Classificacao documental:
- DIRETRIZ IMPLEMENTADA
- FUTURO REAL / APLICACAO PROGRESSIVA

Prioridade documental: ALTA como diretriz; execucao incremental por cadastro

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/REGRAS_NEGOCIO.md

---

### 14. Edicao de conta sem saldo inicial/data ja preenchidos

Status inicial: FUTURO REAL / BUG OPERACIONAL

Status apos baixa documental: IMPLEMENTADO

Motivo:
Foi levantado que, ao atualizar dados da conta cadastrada, o formulario deve trazer saldo inicial e data do saldo ja cadastrados. Requer conferencia do formulario atual antes de qualquer correcao.

Achado da baixa:
- `ContaFinanceiraForm` inclui `saldo_inicial` e `data_saldo_inicial`.
- `data_saldo_inicial` usa widget `DateInput(format='%Y-%m-%d', attrs={'type': 'date'})`, compativel com input HTML/date.
- Ha teste cobrindo carregamento de saldo inicial/data na edicao e atualizacao desses valores.

Classificacao documental:
- IMPLEMENTADO

Prioridade documental: ALTA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/STATE.md

---

### 15. Conta inativa em novos lancamentos e relatorios historicos

Status inicial: FUTURO REAL / REQUER CONFERENCIA NO CODIGO

Status apos auditoria: AUDITADO / REQUER IMPLEMENTACAO

Status apos implementacao parcial: PARCIALMENTE IMPLEMENTADO / REQUER FILTROS HISTORICOS

Status apos refinamento de filtros historicos: IMPLEMENTADO

Motivo:
Foi definida a regra de que conta inativa nao deve aparecer para novos lancamentos, mas deve aparecer em filtros historicos quando tiver movimento no periodo/escopo selecionado.

Achado da auditoria:
- `LancamentoFinanceiroForm`, `LancamentoFinanceiroGrupoRateioForm` e `ContaFinanceiraAutocompleteView` ainda usam contas sem filtrar por `ativa`, permitindo conta inativa em novo lancamento e em conta destino de transferencia.
- A edicao de lancamento antigo ainda funciona porque as contas inativas permanecem no queryset, mas uma correcao futura precisa preservar explicitamente a conta ja vinculada.
- Relatorios e filtros historicos usam todas as contas, preservando movimentos antigos, mas ainda nao aplicam o refinamento de exibir inativas apenas quando tiverem movimento no periodo.
- A importacao de lancamentos ja monta indice de contas com `ContaFinanceira.objects.filter(ativa=True)`.

Implementacao parcial:
- Forms e autocomplete de lancamentos passaram a oferecer apenas contas ativas para novos lancamentos e transferencias.
- Edicao de lancamento antigo preserva apenas a conta inativa ja vinculada ao proprio registro.
- Clone passa a limpar conta origem/destino inativa do original para revisao do usuario.
- Filtros historicos de contas em consultas/relatorios passam a listar contas ativas sempre e contas inativas apenas quando houver movimento no periodo/escopo considerado.

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

Status apos microetapa funcional: IMPLEMENTADO

Motivo:
Foi levantado que, quando o lancamento for transferencia, o campo favorecido no Extrato deve aparecer como `TRANSFERÊNCIA ENTRE CONTAS`. Ajuste implementado apenas na apresentacao do Extrato, preservando calculo, saldo e regra de transferencia.

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

Status apos microetapa funcional: IMPLEMENTADO

Motivo:
Foi levantada melhoria para mostrar o valor que falta para fechar o valor total do documento em lancamentos com rateio. Implementado como apoio visual/operacional no formulario de novo lancamento com rateio e na edicao coordenada do grupo, exibindo valor total do documento, total rateado e diferenca restante, sem alterar validacao, persistencia, saldos ou calculos financeiros consolidados.

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

Status apos microetapa funcional: IMPLEMENTADO

Motivo:
Foi levantada melhoria para permitir selecionar mais de uma conta na listagem de lancamentos, reaproveitando a experiencia validada no Extrato multi-contas. Implementado com selecao de uma, varias ou todas as contas, mantendo compatibilidade com o parametro antigo de conta unica e exibindo transferencias quando origem ou destino pertencem ao conjunto selecionado.

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

Status apos baixa documental: IMPLEMENTADO NAS TELAS ANALITICAS / PENDENCIA FUTURA SEPARADA NA LISTAGEM DE LANCAMENTOS

Motivo:
Foi levantada melhoria para aplicar o padrao visual/comportamental do filtro de contas validado no Extrato em outras telas que possuam selecao de contas. Deve ser implementado futuramente em microetapas por tela ou conjunto minimo seguro.

Achado da baixa:
- `resumo.html`, `prestacao_contas.html` e `evolucao_categorias.html` usam o dropdown de contas com opcao "Todas as contas", busca local, selecao parcial e lista empilhada.
- O comportamento comum do dropdown esta centralizado no shell do financeiro em `financeiro/base.html`.
- A listagem de lancamentos permanece como pendencia propria de filtro multi-contas e nao deve ser misturada a esta baixa.

Classificacao documental:
- IMPLEMENTADO NAS TELAS ANALITICAS
- FUTURO REAL para listagem de lancamentos

Prioridade documental: MEDIA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/PADRAO_UX_SISTEMA.md
- docs/STATE.md

---

### 21. Refinamento de impressao da Prestacao/Fechamento do periodo

Status inicial: FUTURO REAL / AJUSTE VISUAL DE RELATORIO

Status apos baixa documental: IMPLEMENTADO / AGUARDANDO VALIDACAO VISUAL POR USO REAL

Motivo:
Foi levantado que o PDF/impresso atual da Prestacao/Fechamento do periodo esta pouco compacto, com margens/espacamentos grandes e quebra de pagina ruim. O ajuste futuro deve tratar apenas layout de impressao, sem alterar calculos.

Achado da baixa:
- `prestacao_contas.html` possui bloco `@media print` com compactacao de margens, padding, tabelas, cabecalho documental, repeticao de `thead`/`tfoot` e regras de `break-inside`.
- A implementacao esta registrada no roadmap como ajuste de compactacao do modo print/PDF sem alteracao de calculos.

Classificacao documental:
- IMPLEMENTADO
- AGUARDANDO VALIDACAO VISUAL

Prioridade documental: MEDIA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/STATE.md
- docs/REGRAS_NEGOCIO.md

---

### 22. Balancete Institucional como relatorio proprio

Status inicial: FUTURO REAL / FRENTE DE RELATORIO

Status apos auditoria: PARCIALMENTE IMPLEMENTADO / AJUSTES FUTUROS

Motivo:
Foi revisada a direcao anterior: a Prestacao/Fechamento deve permanecer como relatorio analitico/gerencial, e o Balancete Institucional deve ser criado futuramente como relatorio proprio, formal/documental, reutilizando a mesma base de calculo da Prestacao/Fechamento.

Achado da auditoria documental:
- o Balancete ja existe como relatorio proprio, sem substituir a Prestacao/Fechamento
- o MVP reutiliza a base comum de calculo preparada a partir da Prestacao/Fechamento
- o documento ja nasceu com aparencia documental, fundo branco, composicao final do saldo e ajustes visuais de impressao registrados
- permanecem futuras as evolucoes de modelo gerencial/patrimonial, especialmente tipo de conta, separacao entre disponivel/indisponivel e modos de composicao

Classificacao documental:
- PARCIALMENTE IMPLEMENTADO
- AJUSTE VISUAL/DOCUMENTAL FUTURO
- REQUER MODELAGEM para disponibilidade/tipo de conta
- AGUARDANDO VALIDACAO VISUAL para acabamento documental do PDF/print

Prioridade documental: MEDIA

Direcao revisada:
- relatorio proprio chamado `Balancete Institucional`
- nao substituir a Prestacao/Fechamento atual
- reaproveitar regra/base de calculo da Prestacao/Fechamento
- evitar divergencia de calculo e duplicacao de regra financeira
- preservar transparencia da composicao do saldo e regra de transferencias por escopo

Baixa documental detalhada:
- Implementado: relatorio proprio, sem substituir a Prestacao/Fechamento; uso da mesma base de calculo; fundo branco/documental; secoes numeradas; saldo inicial disponivel; receitas do periodo; despesas do periodo; fechamento do saldo disponivel; composicao do saldo disponivel; assinaturas condicionais; ate duas assinaturas selecionaveis; assinatura real somente quando selecionada; contas zeradas ocultas por padrao; transferencias tratadas por escopo sem virar receita/despesa operacional.
- Implementado com validacao visual/uso real pendente: margens, fonte, quebra de pagina, acabamento documental do PDF/print e preferencia por caber em uma pagina quando o volume permitir.
- Futuro / requer modelagem: tipo de conta, disponibilidade/vinculacao, mensagem explicativa de indisponibilidade por conta, separacao entre saldo disponivel e indisponivel/vinculado, integralizacao de capital como valor patrimonial/vinculado, modos de composicao detalhado por conta, consolidado por tipo, total consolidado e separacao disponivel/indisponivel.
- Conclusao de baixa: o MVP do Balancete nao permanece pendente como bloco de criacao; o que segue aberto e evolucao futura de modelagem, composicao e acabamento documental.

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/CEREBRO_PROJETO.md
- docs/REGRAS_NEGOCIO.md

---

### 23. Duas assinaturas no Balancete Institucional

Status inicial: FUTURO REAL

Status apos auditoria: PARCIALMENTE IMPLEMENTADO / AJUSTE FUTURO

Motivo:
Foi levantada necessidade futura de permitir duas assinaturas no Balancete Institucional, aproveitando a base de cadastro manual de assinaturas ja existente e evoluindo para selecao ou definicao de duas assinaturas padrao para esse documento.

Achado da auditoria documental:
- o MVP do Balancete ja permite selecionar assinaturas a partir de `AssinaturaInstitucional`
- a regra atual evita exibir assinatura real quando nao houver selecao manual
- permanece futura a eventual definicao de assinaturas padrao especificas para o Balancete, se o uso real exigir

Classificacao documental:
- PARCIALMENTE IMPLEMENTADO
- AJUSTE DOCUMENTAL / IMPRESSAO FUTURO

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

---

### 25. Tipo de conta financeira

Status inicial: FUTURO REAL / REQUER MODELAGEM

Status apos modelagem documental: MODELADO DOCUMENTALMENTE / REQUER IMPLEMENTACAO FUTURA

Status apos decisao do MVP: DECISAO FUNCIONAL APROVADA / REQUER IMPLEMENTACAO FUTURA

Status apos auditoria tecnica: AUDITADO TECNICAMENTE / PRONTO PARA SPEC FUNCIONAL

Status apos base cadastral: IMPLEMENTADO NA BASE DE CONTAS / BALANCETE PATRIMONIAL FUTURO

Motivo:
Foi levantada necessidade de classificar contas por tipo, como conta corrente, poupanca, dinheiro/caixa, conta investimento, integralizacao de capital, conta vinculada ou outros. Deve ser avaliado se o tipo sera cadastro proprio para manter abertura a outras instituicoes.

Especificacao futura:
- exemplos iniciais: conta corrente, conta poupanca, dinheiro/caixa, conta investimento, integralizacao de capital, conta vinculada/indisponivel e outros
- decisao aprovada: usar cadastro proprio simples de tipos de conta para permitir adaptacao a outros projetos
- implementado: model proprio simples de tipo de conta com carga inicial idempotente dos tipos aprovados
- ajuste de nomenclatura: o codigo `aplicacao_financeira` permanece, mas o nome exibido passa a ser `Conta investimento`
- o tipo de conta deve permitir agrupamento gerencial no Balancete patrimonial, somando contas do mesmo tipo independentemente do banco ou nome da conta
- cadastro/listagem/importacao/exportacao auxiliar de contas ja reconhecem o tipo; Balancete deve entrar em microetapa separada ou posterior

Classificacao documental:
- MELHORIA FUNCIONAL
- REGRA GERENCIAL / PATRIMONIAL

Prioridade documental: MEDIA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/CEREBRO_PROJETO.md

---

### 26. Disponibilidade ou vinculacao da conta

Status inicial: FUTURO REAL / REQUER MODELAGEM

Status apos modelagem documental: MODELADO DOCUMENTALMENTE / REQUER IMPLEMENTACAO FUTURA

Status apos decisao do MVP: DECISAO FUNCIONAL APROVADA / REQUER IMPLEMENTACAO FUTURA

Status apos auditoria tecnica: AUDITADO TECNICAMENTE / PRONTO PARA SPEC FUNCIONAL

Status apos base cadastral: IMPLEMENTADO NA BASE DE CONTAS / LEITURA NO BALANCETE FUTURA

Status apos leitura patrimonial: IMPLEMENTADO COM PENDENCIAS FUTURAS

Motivo:
Foi levantada necessidade de indicar se o saldo de uma conta e disponivel para uso ou indisponivel/vinculado. Esta regra e diferente de conta ativa/inativa: ativa/inativa controla uso operacional; disponibilidade controla leitura gerencial do saldo.

Especificacao futura:
- conta ativa/inativa controla uso operacional em novos lancamentos
- conta disponivel/indisponivel controla leitura gerencial e patrimonial do saldo
- uma conta pode estar ativa e ainda assim ter saldo indisponivel/vinculado
- decisao aprovada para o MVP: disponibilidade/vinculacao sera total por conta; disponibilidade parcial fica como evolucao futura
- implementado: campo simples em `ContaFinanceira` classifica a conta como disponivel ou indisponivel/vinculada em seu saldo total
- integralizacao de capital deve ficar separada como valor patrimonial/vinculado, nao como despesa operacional
- conta de integralizacao pode ser cadastrada normalmente; no Balancete, a separacao como saldo disponivel ou indisponivel/vinculado depende do campo `disponibilidade`
- implementado no Balancete: composicao final separada entre saldo disponivel operacional e saldo indisponivel/vinculado, preservando o detalhamento por conta
- nao houve alteracao de calculo, saldo, lancamentos ou transferencias; a separacao no Balancete e apenas classificatoria

Classificacao documental:
- REGRA DE NEGOCIO
- LEITURA GERENCIAL / PATRIMONIAL

Prioridade documental: ALTA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/REGRAS_NEGOCIO.md
- docs/CEREBRO_PROJETO.md

---

### 27. Mensagem explicativa de indisponibilidade por conta

Status inicial: FUTURO REAL / REQUER MODELAGEM

Status apos modelagem documental: MODELADO DOCUMENTALMENTE / REQUER IMPLEMENTACAO FUTURA

Status apos decisao do MVP: DECISAO FUNCIONAL APROVADA / REQUER IMPLEMENTACAO FUTURA

Status apos auditoria tecnica: AUDITADO TECNICAMENTE / PRONTO PARA SPEC FUNCIONAL

Status apos base cadastral: IMPLEMENTADO NA BASE DE CONTAS / EXIBICAO NO BALANCETE FUTURA

Status apos leitura patrimonial: IMPLEMENTADO COM PENDENCIAS FUTURAS

Motivo:
Foi levantada necessidade de campo opcional no cadastro de contas para justificar em relatorios por que determinado saldo esta indisponivel. Se o campo estiver vazio, nada deve aparecer no relatorio.

Especificacao futura:
- decisao aprovada: campo opcional no cadastro da conta
- implementado: mensagem opcional no cadastro/edicao/listagem/importacao/exportacao auxiliar de contas
- se vazio, nada aparece no Balancete ou relatorio patrimonial
- se preenchido, pode aparecer como justificativa do saldo indisponivel/vinculado
- implementado no Balancete: exibicao discreta da mensagem junto a conta indisponivel/vinculada, sem alterar calculo

Classificacao documental:
- MELHORIA FUNCIONAL
- MELHORIA DE UX EM RELATORIOS

Prioridade documental: MEDIA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/REGRAS_NEGOCIO.md

---

### 28. Modos de composicao do Balancete Institucional

Status inicial: FUTURO REAL / MELHORIA DE RELATORIO

Status apos modelagem documental: MODELADO DOCUMENTALMENTE / REQUER IMPLEMENTACAO FUTURA

Status apos decisao do MVP: DECISAO FUNCIONAL APROVADA / REQUER IMPLEMENTACAO FUTURA

Status apos auditoria tecnica: AUDITADO TECNICAMENTE / PRONTO PARA SPEC FUNCIONAL POSTERIOR

Status apos leitura patrimonial inicial: PARCIALMENTE IMPLEMENTADO

Status apos refinamento por publico e composicao: IMPLEMENTADO COM PENDENCIAS FUTURAS

Status apos simplificacao dos filtros: IMPLEMENTADO COM PENDENCIAS FUTURAS

Motivo:
Foi levantada necessidade de o Balancete permitir escolher entre composicao detalhada por conta, consolidada por tipo de conta ou apenas saldo total consolidado, possivelmente separando disponivel e indisponivel para reduzir poluicao visual.

Especificacao futura:
- decisao aprovada para o MVP: modo padrao detalhado por conta, preservando leitura atual com separacao visual entre disponivel e indisponivel/vinculado quando aplicavel
- implementado no Balancete: modo detalhado por conta com separacao visual entre disponivel e indisponivel/vinculado e total financeiro preservado
- ajuste posterior validado: o filtro `Modelo do relatorio` foi removido por redundancia
- ajuste posterior validado: o filtro separado de detalhamento do saldo inicial foi removido por redundancia
- ajuste posterior validado: a diferenca pratica do documento passou a ser controlada diretamente pelos filtros de composicao do saldo e exibicao de vinculadas/indisponiveis
- implementado no Balancete: consolidado por tipo de conta para somar contas do mesmo tipo, independentemente do banco ou nome da conta
- implementado no Balancete: total consolidado para leitura mais sintetica
- implementado no Balancete: opcao para exibir ou ocultar contas vinculadas/indisponiveis sem alterar calculo
- implementado no Balancete: o mesmo modo de composicao passou a valer para saldo inicial e saldo final
- implementado no Balancete: ocultacao dos metadados desses filtros no cabecalho impresso, mantendo apenas informacoes institucionais e do periodo
- implementado no Balancete: sequencia documental corrigida para saldo inicial, entradas, saidas, resumo operacional, composicao do saldo final e assinaturas
- implementado no Balancete: remocao do aviso textual sobre contas vinculadas/indisponiveis ocultas
- implementado no Balancete: quando vinculadas/indisponiveis ficam ocultas, o documento passa a representar apenas o saldo disponivel operacional; transferencias entre disponivel e indisponivel aparecem no resumo como movimentacao especifica de fronteira, sem virar receita ou despesa operacional
- decisao funcional aprovada para proxima evolucao: substituir filtro solto de vinculadas por arquitetura orientada por `Formato do Balancete` com tres formatos (Operacional, Operacional + patrimonio vinculado, Financeiro completo) e filtros dependentes por formato
- implementado no Balancete: arquitetura por formato principal com filtros dependentes, retirada do filtro antigo de vinculadas da interface e bloco patrimonial complementar separado no formato gerencial
- integralizacao de capital, contas investimento e contas vinculadas/indisponiveis devem aparecer separadas quando existirem
- deve reaproveitar a base de calculo do Fechamento/Prestacao, sem calculo proprio divergente
- implementado no recorte atual: `BalanceteInstitucionalFinanceiroView` classifica a `balancete_composicao_final` por disponibilidade e modo de composicao sem mudar `montar_contexto_fechamento_periodo`; permanecem futuros apenas refinamentos avancados de ordenacao, legibilidade e expansoes adicionais se o uso real justificar

Classificacao documental:
- MELHORIA FUNCIONAL DE RELATORIO
- AJUSTE DOCUMENTAL / IMPRESSAO

Prioridade documental: MEDIA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/CEREBRO_PROJETO.md

---

### 29. Logo institucional no Extrato impresso

Status inicial: FUTURO REAL / REQUER AUDITORIA VISUAL

Status apos auditoria: AUDITADO / REQUER CORRECAO PONTUAL NO TEMPLATE

Status apos correcao: IMPLEMENTADO COM REFINAMENTO VISUAL / AGUARDANDO VALIDACAO VISUAL

Motivo:
Foi observado que o Extrato impresso parece reservar espaco para logo institucional, mas a logo nao aparece na impressao. Deve ser auditado separadamente da frente de tipo/disponibilidade de conta.

Achado da auditoria:
- `conta_extrato.html` nao renderiza `financeiro_shell_brand_logo_url` como `<img>` no cabecalho impresso.
- Prestacao, Resumo e Balancete renderizam a logo institucional com a mesma variavel de contexto.
- Causa provavel: lacuna no template do Extrato, nao CSS de print, calculo financeiro ou configuracao institucional.

Proxima microetapa recomendada:
- adicionar ao cabecalho documental do Extrato o bloco de logo institucional ja usado nos demais relatorios, preservando fallback para nome institucional quando nao houver logo.

Correcao aplicada:
- o cabecalho impresso do Extrato passou a renderizar `financeiro_shell_brand_logo_url` como `<img>` e a manter `financeiro_shell_brand_name` apenas como fallback quando nao houver logo.
- refinamento complementar compactou o cabecalho impresso e ajustou o `thead` para repetir os titulos das colunas em quebras de pagina.
- refinamento complementar posterior reequilibrou margem superior, hierarquia documental, bloco de contas selecionadas e destaque do cabecalho da tabela.
- refinamento posterior definiu contrato local de impressao para o Extrato, com margem/padding real e respiro no `thead` em paginas seguintes.
- baixa documental confirmou que `conta_extrato.html` renderiza a logo institucional via `<img>` quando existe `financeiro_shell_brand_logo_url` e mantem `financeiro_shell_brand_name` visivel no cabecalho.

Classificacao documental:
- IMPLEMENTADO
- AGUARDANDO VALIDACAO VISUAL

Prioridade documental: MEDIA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/STATE.md

---

### 30. Extrato multi-contas - detalhamento opcional de transferencias internas

Status inicial: FUTURO REAL / MELHORIA DE UX

Motivo:
A usuaria homologou como correto o comportamento atual do Extrato consolidado, no qual transferencias internas ao escopo selecionado se anulam para nao inflar o saldo. Durante a validacao, foi identificada uma melhoria futura de conferencia operacional: oferecer opcao visual para detalhar essas transferencias internas em duas linhas, uma de saida da conta origem e outra de entrada na conta destino.

Classificacao documental:
- FUTURO REAL
- MELHORIA DE UX
- NAO E ERRO DA IMPLEMENTACAO ATUAL

Regra preservada:
- o comportamento padrao do Extrato permanece consolidado
- transferencias internas ao escopo selecionado continuam se anulando no saldo
- a melhoria futura nao deve alterar calculo financeiro, saldo, regra de transferencia, listagem de lancamentos, importacao/exportacao ou outros relatorios

Prioridade documental: MEDIA

Documentos relacionados:
- docs/ROADMAP_FINANCEIRO.md
- docs/STATE.md

## Próxima ação recomendada

A próxima microetapa documental deve conferir os itens acima contra o código e contra os documentos atuais, um grupo por vez, sem alterar funcionalidades.

Prioridade sugerida de conferência:

1. financeiro/documentos por favorecido;
2. permissões;
3. importação;
4. padronização visual;
5. frequência/recorrência futura.

---

### 31. Balancete Institucional - aceite final funcional e UX

Status inicial: IMPLEMENTADO COM PENDENCIAS FUTURAS

Status final: IMPLEMENTADO E APROVADO PELA USUARIA

Consolidacao:
- arquitetura por `Formato do Balancete` aprovada no uso real
- formatos ativos e aprovados: `Operacional`, `Operacional + patrimonio vinculado`, `Financeiro completo`
- filtro antigo de vinculadas removido da interface e nao reintroduzido
- filtro dependente `Detalhar patrimonio vinculado` aprovado para aparecer somente em `operacional_patrimonio`, com troca imediata ao alterar formato
- patrimonio vinculado segue separado do resumo operacional
- transferencias entre operacional e vinculado seguem como movimentacao de fronteira, sem virar receita/despesa operacional
- sem alteracao de calculo financeiro, saldos ou demais relatorios

Governanca:
- nao reabrir essa logica sem nova decisao explicita da usuaria

---

### 32. Proximas pendencias do financeiro apos aceite do Balancete

Status: LEVANTADO E CLASSIFICADO DOCUMENTALMENTE

Resumo:
- o Balancete Institucional sai da fila ativa e fica congelado no recorte aprovado
- a fila imediata recomendada passa a priorizar:
  1) homologacao real de importacoes
  2) validacao visual final de relatorios impressos em volume real (Extrato)
  3) auditoria preparatoria de frequencia/recorrencia por competencia

Observacao:
- este item e de governanca/backlog; nao representa implementacao funcional

---

### 33. Controle de contribuicao mensal / frequencia por competencia

Status anterior: FUTURO REAL

Status apos auditoria desta microetapa: PRONTA PARA SPEC FUNCIONAL (COM DECISOES PENDENTES)

Status apos consolidacao de SPEC: SPEC FUNCIONAL/TÉCNICA CONSOLIDADA (AGUARDANDO MICROETAPA DE IMPLEMENTACAO)

Consolidacao:
- regra ja modelada em documentos oficiais, sem implementacao tecnica no codigo
- frente deve nascer como estrutura generica de recorrencia por competencia, sem acoplamento exclusivo a contribuicao
- primeira onda recomendada: flags minimas em favorecido e subcategoria + matriz mensal com valores
- segunda onda recomendada: matriz sem valores e termo por favorecido

Pendencias de decisao da usuaria:
- competencia-base do MVP
- escopo de status (`quitado` apenas ou `quitado + aberto` com distincao)
- consolidacao de multiplos lancamentos no mesmo mes

Consolidacao adicional da SPEC:
- unidade minima recomendada: alocacao de competencia (`mes/ano + valor`)
- regra de rateio: considerar apenas a parte/subcategoria que controla frequencia; nao usar valor total do documento em recebimentos mistos
- matriz com valores como base e matriz sem valores derivada
- termo por favorecido mantido como segunda onda
