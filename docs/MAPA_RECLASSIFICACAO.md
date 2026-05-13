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

### 19. Construtor de tabelas personalizadas configuraveis

Status inicial: FUTURO REAL / FRENTE FUTURA GRANDE

Status apos auditoria documental desta microetapa: SPEC FUNCIONAL CONSOLIDADA / BACKLOG

Status apos complemento documental desta microetapa: SPEC FUNCIONAL + OPERACIONAL CONSOLIDADA / BACKLOG

Status apos fechamento documental desta microetapa: SPEC FUNCIONAL + OPERACIONAL + UX CONSOLIDADA / BACKLOG

Status apos fechamento documental desta microetapa: SPEC FUNCIONAL + OPERACIONAL + UX + NAVEGACAO CONSOLIDADA / BACKLOG
Status apos fechamento documental desta microetapa: PRIMEIRO RECORTE OPERACIONAL DOCUMENTAL FECHADO / BACKLOG
Status apos planejamento documental desta microetapa: BACKLOG TECNICO INCREMENTAL DO MVP PLANEJADO / BACKLOG
Status apos auditoria tecnica preparatoria desta microetapa: AUDITORIA TECNICA PREPARATORIA CONCLUIDA / BACKLOG
Status apos SPEC tecnica desta microetapa: SPEC TECNICA DE MODELAGEM CONSOLIDADA / BACKLOG
Status apos implementacao desta microetapa: ESTRUTURA MINIMA DE DADOS IMPLEMENTADA / BACKLOG
Status apos implementacao desta microetapa: PERMISSOES EXECUTAVEIS DA FRENTE IMPLEMENTADAS / BACKLOG
Status apos implementacao desta microetapa: MENU REAL + LISTAGEM MINIMA SOMENTE LEITURA IMPLEMENTADOS / BACKLOG
Status apos implementacao desta microetapa: REFINAMENTO DE UX E PRECISAO DECIMAL DAS LINHAS IMPLEMENTADO / BACKLOG
Status apos correcao desta microetapa: NORMALIZACAO DE EXIBICAO NUMERICA NA EDICAO DE LINHAS IMPLEMENTADA / BACKLOG

Motivo:
Foi levantada frente futura para controles configuraveis genericos, com colunas definidas pelo usuario, tipos de dado, formulas controladas por coluna e totalizadores. Deve ser tratada separadamente das correcoes imediatas do financeiro.

Consolidacao desta baixa documental:
- manter classificada como `FUTURO/BACKLOG` (sem implementacao nesta etapa)
- manter separada da frente de frequencia mensal por competencia
- exigir auditoria e SPEC propria antes de qualquer modelagem/migration
- a frente passa a ser tratada como `Construtor de tabelas personalizadas configuraveis`
- nao partir de caso de uso piloto fixo como eixo principal
- SPEC consolidada agora com:
  - navegacao/localizacao documentada para o MVP
  - contrato de UX operacional documentado
  - precisao real de `valor_numero` elevada para 8 casas no recorte de linhas
  - entrada decimal brasileira aceita com virgula ou ponto no formulario dinamico
  - edicao de linhas agora normaliza monetario, percentual, decimal e inteiro conforme o tipo antes de preencher o formulario
  - fluxo operacional documentado de uso futuro
  - objetivo funcional proprio e generico
  - recorte conceitual de MVP com construtor controlado
  - fora do MVP
  - limites de seguranca
  - limites iniciais sugeridos
  - premissas de permissao
  - diretriz de formulas permitidas/proibidas
  - diretriz de auditoria/trilha
  - diretriz de exportacao XLSX/backup
  - regra de separacao em relacao ao financeiro oficial
- classificacao das pendencias desta frente:
  - implementar agora: nenhuma
  - pendencia proxima: abrir microetapa tecnica propria para quebrar a SPEC fechada em backlog de implementacao incremental
  - backlog/futuro: exemplos/templates, referencias opcionais e importacao assistida
  - fora de escopo: engine livre estilo Excel e integracao escrevente com financeiro
  - risco a monitorar: virar "Excel dentro do sistema", perder governanca de permissoes/auditoria e confundir controle interno com dado financeiro oficial
- decisoes finais do primeiro recorte operacional agora consolidadas:
  - `data` aceita totalizadores `minimo` e `maximo` apenas quando configurados explicitamente na coluna
  - `sim/nao` e `lista de opcoes` aceitam apenas `contagem simples total` no MVP, sem agrupamento por opcao
  - busca textual simples na tela de linhas entra no MVP; filtros avancados ficam para backlog/futuro
  - reordenacao no MVP usa campo numerico `ordem`; `arrastar-e-soltar` fica para futuro
  - totalizadores aparecem somente quando configurados por coluna e, quando visiveis na tela, devem sair no rodape do XLSX
- riscos registrados para etapa futura: alta complexidade, risco de virar "Excel dentro do sistema", limites de formula por seguranca, permissoes, trilha de auditoria, backup/exportacao e separacao entre dado operacional e financeiro oficial
- backlog tecnico incremental agora organizado em ordem segura:
  - primeira microetapa futura = auditoria tecnica preparatoria da base atual
  - SPEC tecnica de modelagem antes de qualquer `model` ou `migration`
  - implementacao estrutural minima apenas depois da SPEC tecnica aprovada
  - permissoes/menu, listagem, cadastro, colunas, linhas, totalizadores, busca, exportacao, formulas, auditoria, UX e homologacao quebrados em microetapas futuras proprias
- achados da auditoria tecnica preparatoria:
  - navegacao atual do financeiro centralizada em `financeiro/templates/financeiro/base.html`, com exibicao de grupos e itens condicionada por permissao
  - camada de permissao pronta em `configuracoes` e `financeiro`, com mixins, template tags, matriz documental e seeds em migrations
  - trilha de auditoria atual pronta em `AuditoriaFinanceiro`, com `usuario`, `data_hora`, `acao` e `campos_alterados` de before/after
  - exportacao XLSX atual pronta por views dedicadas e helpers proprios no `financeiro`
  - padrao de listagem/formulario mais proximo do futuro uso esta nos cadastros auxiliares, nao em `LancamentoFinanceiro`
  - recomendacao documental de organizacao: manter a frente dentro do app `financeiro`, mas em arquivos/rotas proprios e em grupo de menu `Controles internos`
- reclassificacao da pendencia proxima apos a auditoria:
  - deixa de ser `auditoria tecnica preparatoria`
  - passa a ser `SPEC tecnica de modelagem de dados`, ainda sem `model` e sem `migration`
- consolidacao da SPEC tecnica de modelagem:
  - entidades candidatas documentadas: tabela, coluna, linha, valor, formula, totalizador, auditoria e permissoes
  - alternativas comparadas: EAV, JSON por linha, colunas tipadas separadas e modelo hibrido
  - estrategia recomendada: modelo hibrido controlado, com valor por celula e slots tipados
  - alternativa descartada como base inicial: `JSON por linha`
  - formula guiada completa permanece fora da primeira implementacao estrutural
- reclassificacao da pendencia proxima apos a SPEC tecnica:
  - deixa de ser `SPEC tecnica de modelagem de dados`
  - passa a ser `validar/aprovar a modelagem e, se aprovada, abrir a implementacao minima da estrutura de dados`
- consolidacao da implementacao estrutural minima:
  - models implementados: `TabelaPersonalizada`, `ColunaPersonalizada`, `LinhaTabelaPersonalizada` e `ValorTabelaPersonalizada`
  - migration criada no `financeiro`
  - testes minimos adicionados e suite do app validada
  - regras de formula, totalizador, menu, views, permissao executavel, exportacao e auditoria propria permanecem fora desta etapa
- reclassificacao da pendencia proxima apos a implementacao estrutural:
  - deixa de ser `implementacao minima da estrutura de dados`
  - passa a ser `permissoes e menu da frente`
- consolidacao da camada de permissao executavel:
  - catalogo canonico de permissoes criado no backend do `financeiro`
  - seed por migration criado em `configuracoes` para registrar a frente no catalogo oficial de `PermissaoSistema`
  - atribuicao inicial e conservadora por perfil-base:
    - `administrador-geral` e `gestao-administrativa` com todas as permissoes
    - `operador-financeiro` com leitura e operacao comum, sem `configurar_formula`, `arquivar_restaurar` ou `administrar_configuracoes`
    - `consulta-visualizacao` com `visualizar` e `exportar`
  - matriz documental atualizada sem abrir menu real nesta mesma etapa
- reclassificacao da pendencia proxima apos a camada de permissao:
  - deixa de ser `permissoes e menu da frente`
  - passa a ser `menu real + listagem minima da frente`, ja apoiados pelas permissoes executaveis e sem link quebrado
- consolidacao do menu real e da listagem minima:
  - rota criada dentro do app `financeiro`
  - `ListView` protegida por `financeiro.tabelas_personalizadas.visualizar`
  - template minimo de leitura criado sem links quebrados
  - item de menu criado em `Controles internos`, isolado do financeiro oficial
  - sem criacao/edicao, sem colunas, sem linhas, sem formulas, sem totalizadores e sem exportacao nesta etapa
- consolidacao do cadastro inicial de metadados:
  - formulario de `TabelaPersonalizada` criado apenas com `nome`, `descricao`, `status` e `ordem`
  - criacao e edicao protegidas por permissoes separadas da frente
  - listagem atualizada com `Nova tabela` e `Editar`, sem abrir colunas, linhas ou exportacao
- consolidacao da configuracao inicial de colunas:
  - listagem estrutural de colunas criada por tabela
  - criacao e edicao de coluna protegidas por `editar_estrutura`
  - `formula_controlada` mantida bloqueada no formulario desta etapa
  - `lista_opcoes` permitida de forma controlada em `configuracao_json.opcoes`
  - listagem de tabelas atualizada com acao `Colunas`, sem abrir linhas ou exportacao
- consolidacao da tela de linhas e do preenchimento inicial de valores:
  - listagem de linhas criada por tabela com leitura apenas de colunas ativas, visiveis e nao calculadas
  - criacao e edicao de linha protegidas por permissoes separadas de preencher/editar linhas
  - `TabelaPersonalizadaLinhaForm` dinamico criado sem abrir `formula_controlada`, totalizadores ou exportacao
  - listagem de tabelas atualizada com acao `Linhas`, respeitando o recorte de permissao da frente
- consolidacao dos totalizadores controlados por coluna:
  - model `TotalizadorColunaPersonalizada` implementado com migration dedicada no `financeiro`
  - configuracao de totalizador incorporada ao formulario de coluna, com exibicao apenas de opcoes compativeis com o tipo
  - rodape da listagem de linhas passa a exibir apenas totalizadores configurados em colunas visiveis, ativas e nao calculadas
  - linhas arquivadas ficam fora do calculo
  - contagem simples total mantida para texto, booleano, lista de opcoes e `mes_competencia`, sem agrupamentos
- consolidacao da busca textual simples nas linhas:
  - campo de busca adicionado na tela de linhas com escopo restrito a valores visiveis/editaveis da tabela atual
  - busca simples cobre texto, lista de opcoes, mes/competencia, numero, data e booleano sem abrir filtros avancados
  - colunas invisiveis, arquivadas, calculadas e `formula_controlada` ficam fora da busca
  - totalizadores passam a refletir o resultado filtrado mostrado na tela
- consolidacao da exportacao XLSX das linhas:
  - rota de exportacao propria criada dentro da tabela personalizada, protegida por `financeiro.tabelas_personalizadas.exportar`
  - botao `Exportar XLSX` adicionado na tela de linhas apenas para quem possui permissao de exportar
  - o arquivo reflete exatamente o recorte visivel da tela: somente colunas ativas/visiveis/nao calculadas, somente linhas ativas e busca ativa quando houver
  - totalizadores visiveis passam a sair no bloco final da planilha com o mesmo resultado filtrado exibido na tela
  - o cabecalho do arquivo reforca o contexto de controle interno sem efeito financeiro oficial
- reclassificacao da pendencia proxima apos a exportacao:
  - deixa de ser `exportacao XLSX`
  - passa a ser `formulas guiadas por coluna`, mantendo auditoria operacional propria fora do recorte imediato
- status apos SPEC tecnica curta desta microetapa:
  - `SPEC TECNICA CURTA DE FORMULAS GUIADAS CONSOLIDADA / AGUARDANDO IMPLEMENTACAO INCREMENTAL`
- consolidacao registrada:
  - recomendacao inicial de persistencia em `configuracao_json.formula`, sem migration no primeiro recorte
  - fontes iniciais restritas a `inteiro`, `decimal`, `monetario` e `percentual`
  - resultado inicial recomendado restrito a `decimal` e `monetario`
  - operadores iniciais restritos a `soma`, `subtracao`, `multiplicacao` e `divisao`
  - formula sobre formula, totalizador em coluna calculada e filtro estruturado em calculada ficam fora do primeiro recorte
  - proxima etapa mais segura passa a ser configuracao da formula na estrutura da coluna antes do calculo e da integracao com tela/XLSX
- guardrails reforcados:
  - qualquer alteracao em banco real exige backup e autorizacao
  - arquivos SQLite nao devem ser versionados
  - a frente continua sem integracao escrevente com o financeiro oficial

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

### 34. Frequencia por competencia - base cadastral minima implementada

Status: IMPLEMENTADO (BASE CADASTRAL), COM IMPLEMENTACAO FUNCIONAL PRINCIPAL PENDENTE

Consolidacao:
- campo `contribuinte_recorrente` criado em `PessoaFinanceira` (default `False`)
- campo `controla_recorrencia_competencia` criado em `CategoriaFinanceira` (default `False`)
- interface administrativa e operacional atualizada para marcar/desmarcar os dois controles
- importacao/exportacao auxiliar de pessoas/categorias atualizada para os novos campos
- sem alteracao de lancamentos, calculos, saldos, Balancete, Extrato e Fechamento/Prestacao

Proxima etapa recomendada:
- modelagem/implementacao da alocacao de competencia (mes/ano + valor) vinculada ao lancamento/subcategoria controlada

### 35. Frequencia por competencia - alocacao mensal vinculada ao lancamento

Status: IMPLEMENTADO PARCIALMENTE (LANCAMENTO SIMPLES), COM RATEIO AINDA PREPARADO

Consolidacao:
- model `AlocacaoCompetenciaFinanceira` criado como estrutura filha de `LancamentoFinanceiro`
- lancamento simples recorrente/controlado agora aceita uma ou mais competencias com `mes/ano + valor`
- soma das alocacoes passou a fechar com o valor controlado do lancamento
- clone comum nao copia competencias automaticamente
- exclusao do lancamento remove as alocacoes vinculadas
- o fluxo de rateio nao foi quebrado, mas a captura por item controlado no create inicial do grupo permanece pendente para evitar uso indevido do valor total do documento
- validacao da usuaria registrada como aprovada para o recorte de lancamento simples
- confirmado no aceite:
  - exibicao condicional do bloco de competencias
  - salvamento com soma fechada
  - bloqueio com soma divergente
  - edicao recarregando competencias existentes
  - clone sem copiar competencias automaticamente

Proxima etapa recomendada:
- implementar captura/validacao de competencias por item controlado no fluxo de rateio e preparar a futura matriz mensal com valores

### 36. Frequencia por competencia - rateio controlado

Status: IMPLEMENTADO

Consolidacao:
- o fluxo de rateio agora captura competencias apenas para a subcategoria controlada do grupo
- a validacao compara a soma das competencias com o valor consolidado dessa subcategoria, sem usar o valor bruto total do documento
- itens nao controlados do mesmo documento continuam fora da frequencia
- favorecido nao recorrente ou grupo sem item controlado nao exigem competencias
- create com rateio e edicao coordenada do grupo persistem/removem alocacoes conforme as linhas finais do grupo
- clone de rateio permanece sem copiar competencias automaticamente

Proxima etapa recomendada:
- implementar a matriz sem valores derivada da matriz com valores e manter termo por favorecido para a etapa seguinte

### 37. Auditoria acionavel (transversal)

Status: FUTURO/BACKLOG - REQUER SPEC PROPRIA

Consolidacao:
- necessidade registrada para toda a auditoria, nao apenas lancamentos
- objetivo futuro: permitir navegar do evento auditado para o objeto/documento relacionado quando ainda existir
- quando o objeto nao existir mais, auditoria deve sinalizar exclusao de forma clara
- desfazer/restaurar so pode ser avaliado com trilha de reversao, permissao dedicada e regras fortes de seguranca

Riscos:
- reversao pode impactar calculo financeiro, saldos, recibos, competencias, rateios e documentos emitidos
- sem snapshot suficiente, exclusao pode nao ser restauravel com seguranca

### 38. Listagem de lancamentos - acoes faltantes (exclusao/recibo)

Status: AGUARDANDO AUDITORIA TECNICA/UX

Consolidacao:
- usuaria observou ausencia de acoes esperadas em alguns lancamentos da listagem
- pendencia registrada para auditoria funcional antes de correcao
- recorte tecnico ainda precisa identificar se ocorre em rateio, competencias, linhas controladas ou outro caso

### 39. Competencias duplicadas no mesmo lancamento/subcategoria

Status: IMPLEMENTADO

Consolidacao:
- matriz futura deve continuar somando multiplos lancamentos da mesma pessoa/subcategoria/competencia
- dentro do mesmo lancamento e mesma subcategoria controlada, repetir o mesmo mes/ano deve ser bloqueado
- mensagem sugerida:
  - `Ja existe uma competencia informada para este mes/ano. Agrupe o valor em uma unica linha.`

### 40. Frequencia por competencia - primeira matriz mensal com valores

Status: IMPLEMENTADO

Consolidacao:
- nova tela `Frequencia por competencia` criada em `/financeiro/frequencia-competencias/`
- fonte unica da matriz: `AlocacaoCompetenciaFinanceira`
- favorecidos recorrentes aparecem como linhas mesmo sem valor no periodo
- colunas cobrem todas as competencias mensais do intervalo selecionado
- celulas somam `valor_alocado` por pessoa/competencia
- totais entregues:
  - por favorecido
  - por mes
  - total geral
- filtros entregues:
  - competencia inicial/final
  - subcategoria controlada
  - status (`Todos`, `Quitados`, `Em aberto`)
- recortes mantidos:
  - item nao controlado do rateio segue fora
  - favorecido nao recorrente fica fora por padrao
  - matriz sem valores/check-X ainda pendente
  - termo por favorecido ainda pendente

Proxima etapa recomendada:
- implementar a matriz sem valores derivada da base ja entregue e manter termo por favorecido para a onda seguinte

### 41. Frequencia por competencia - matriz sem valores derivada

Status: IMPLEMENTADO

Consolidacao:
- a tela `/financeiro/frequencia-competencias/` passou a alternar entre matriz com valores e matriz sem valores/frequencia visual
- a nova leitura continua derivada de `AlocacaoCompetenciaFinanceira`, sem controle paralelo
- regra visual consolidada:
  - `✓` quando ha contribuicao no mes filtrado
  - `×` quando nao ha contribuicao
- totais entregues no modo sem valores:
  - por favorecido = quantidade de competencias positivas
  - por mes = quantidade de favorecidos com contribuicao
  - total geral = total de ocorrencias positivas
- filtros preservados:
  - competencia inicial/final
  - subcategoria controlada
  - status (`Todos`, `Quitados`, `Em aberto`)
- impressao ainda nao implementada
- termo por favorecido ainda nao implementado

Proxima etapa recomendada:
- preparar a impressao da matriz com tentativa de acomodar todas as colunas na mesma pagina, reaproveitando margens e padrao de impressao do modulo

### 42. Frequencia por competencia - impressao da matriz

Status: IMPLEMENTADO

Consolidacao:
- a tela `/financeiro/frequencia-competencias/` passou a ter acao `Imprimir`
- o impresso cobre os formatos:
  - `Com valores`
  - `Sem valores (frequencia)`
- o template reaproveita o padrao documental do modulo com cabecalho de impressao e metadados essenciais
- foi adotado contrato local de print com `A4 landscape`, margem reduzida e tabela compactada para tentar acomodar todas as competencias na mesma pagina
- a fonte de dados continua sendo `AlocacaoCompetenciaFinanceira`
- a compactacao nao promete pagina unica perfeita em qualquer combinacao; periodos mais longos ainda podem ficar apertados conforme navegador/impressora
- termo por favorecido segue pendente

Proxima etapa recomendada:
- implementar o termo por favorecido usando a mesma base de competencias ja consolidada

### 43. Frequencia por competencia - refinamento da impressao

Status: IMPLEMENTADO

Consolidacao:
- corrigida a compressao excessiva da coluna `Favorecido` no PDF da matriz de frequencia
- o impresso passou a usar cabecalho compacto de competencias no formato `MM/AAAA`
- a tela normal preserva o rotulo visual ja validado
- a coluna `Favorecido` recebeu largura dedicada e protecao contra quebra letra por letra
- as colunas mensais foram compactadas no print para economizar largura sem mudar a fonte de dados
- a limitacao pratica de periodos longos continua registrada

Proxima etapa recomendada:
- implementar o termo por favorecido usando a mesma base de competencias ja consolidada

### 44. Frequencia por competencia - ajuste de cores no print e assistente futuro

Status: PARCIAL (ajuste de impressao concluido + frente futura registrada)

Consolidacao:
- ajuste concluido: impressao dos indicadores `✓` e `×` no modo sem valores com tentativa de preservar verde/vermelho no PDF/print e fallback legivel sem cor
- frente futura registrada (sem implementacao): `Assistente inteligente de competencias`
- direcao futura registrada:
  - sugerir meses proximos (ultimos 5, atual, proximos 5)
  - ausencia de valor nao vira status `em aberto`; fica como `sem quitacao registrada`
  - mes com valor alocado aparece como quitado/ja contribuido
  - valor preenchido no mes e o gatilho principal da competencia atendida
  - modo manual continua obrigatoriamente disponivel
  - complemento/observacao por competencia depende de SPEC propria

Proxima etapa recomendada:
- abrir SPEC dedicada do assistente antes de mexer em forms/models/templates de lancamento e rateio

### 45. Frequencia por competencia - cabecalho impresso limpo e subcategoria legivel

Status: IMPLEMENTADO (AJUSTE DE IMPRESSAO) + FRENTE FUTURA MANTIDA

Consolidacao:
- cabecalho/metadados do impresso da matriz foi simplificado:
  - removido `Formato`
  - removido `Status`
  - mantidos `Periodo`, `Subcategoria` e `Emitido em`
- regra da subcategoria no cabecalho impresso:
  - quando houver filtro especifico, exibir nome legivel da subcategoria
  - quando nao houver filtro especifico, exibir `Todas controladas`
- ajuste de impressao dos indicadores no modo sem valores mantido:
  - `✓` e `×` com tentativa de preservar verde/vermelho no print/PDF
  - fallback legivel sem cor preservado
- sem alteracao de calculo financeiro, saldos, fonte da matriz ou banco real

Frente futura relacionada (sem implementacao):
- `Assistente inteligente de competencias` permanece como backlog com SPEC propria obrigatoria antes de mexer em forms/models/templates

### 46. Assistente inteligente de competencias

Status: SPEC FUNCIONAL CONSOLIDADA / AGUARDANDO MICROETAPA DE IMPLEMENTACAO

Consolidacao:
- a frente deixou de estar apenas como ideia/pendencia generica e passou a ter SPEC funcional fechada para o MVP
- premissas aprovadas e registradas:
  - assistente aparece apenas com favorecido recorrente + subcategoria controlada
  - no rateio, trabalha apenas por subcategoria controlada
  - meses sugeridos: ultimos 5, mes atual e proximos 5
  - ausencia de valor no mes = `sem quitacao registrada`
  - mes com valor alocado = `ja possui contribuicao`
  - valor preenchido no mes e o gatilho da competencia atendida
  - checkbox nao e obrigatorio quando o valor ja representa a competencia
  - modo manual atual permanece
  - em edicao, lancamento antigo sem competencia deve poder ser regularizado no proprio registro
  - redistribuicao de competencias nao altera automaticamente o valor financeiro total do lancamento/subcategoria
  - a UX deve separar `ja registrado` de `valor deste lancamento`
- desenho tecnico consolidado:
  - o assistente deve preencher os payloads ja existentes
  - nao deve criar nova fonte de dados nem novo fluxo de salvamento
  - deve respeitar soma fechando com o valor controlado e a validacao de duplicidade ja existente
- fora do MVP:
  - observacao/complemento por competencia
  - alteracao de model/migration
  - baixa separada
  - historico individual por competencia
  - termo por favorecido
  - mudancas na matriz

Riscos:
- confusao entre contribuicao previa e lancamento atual
- confusao entre referencia historica e valor do lancamento atual
- poluicao excessiva do formulario
- quebra do fechamento de soma
- quebra do rateio controlado
- reintroducao de leitura incorreta de `em aberto`
- redistribuicao em lancamento quitado ser interpretada como mudanca de valor financeiro

Proxima microetapa recomendada:
- implementar o MVP do assistente reaproveitando `competencias_payload` e `competencias_rateio_payload`, com o modo manual preservado

### 47. Assistente inteligente de competencias - MVP funcional

Status apos microetapa funcional: IMPLEMENTADO

Consolidacao:
- o assistente foi implementado como camada assistida sobre os payloads atuais, sem nova persistencia
- reaproveitos consolidados:
  - `competencias_payload`
  - `competencias_rateio_payload`
- coberturas funcionais entregues:
  - lancamento simples novo
  - edicao simples
  - regularizacao de lancamento antigo sem competencia
  - rateio controlado
  - edicao de grupo rateado
- regras preservadas:
  - meses sugeridos = ultimos 5 + atual + proximos 5
  - `Ja registrado` e apenas referencia historica
  - `Valor deste lancamento` e o unico valor que entra no payload atual
  - modo manual continua disponivel
  - soma continua fechando com valor controlado
  - item nao controlado continua fora do assistente/rateio de competencia
- sem alteracao de model, migration, calculos, saldos ou banco real

Proxima microetapa recomendada:
- validar o MVP em uso real e registrar os ajustes finos de UX antes de abrir nova frente de competencia/termo

### 48. Assistente inteligente de competencias - refinamento de UX

Status apos microetapa funcional: IMPLEMENTADO

Consolidacao:
- layout do assistente refinado de cards para lista/tabela compacta
- foco dos inputs corrigido sem alterar payloads nem regras backend
- mensagem orientativa de soma suavizada no simples e no rateio
- modo manual preservado como fallback
- sem alteracao de model, migration, calculos, saldos ou banco real

Pendencia:
- revisao visual mais ampla das secoes do formulario continua aberta para microetapa futura

### 49. Tabelas personalizadas - exportacao XLSX com formato brasileiro

Status apos microetapa funcional: IMPLEMENTADO

Consolidacao:
- a exportacao XLSX da tela de linhas agora usa formato brasileiro para valores numericos e totalizadores
- padrao visual aplicado no arquivo:
  - monetario com `R$` e virgula decimal
  - decimal com virgula (ate 8 casas)
  - percentual com virgula (ate 4 casas) e `%`
- recorte funcional mantido:
  - sem formulas guiadas
  - sem auditoria operacional propria
  - sem alteracao de financeiro oficial

### 50. Tabelas personalizadas - filtros configuraveis por coluna

Status: IMPLEMENTADO NO PRIMEIRO RECORTE / COM EVOLUCOES FUTURAS

Consolidacao:
- a usuaria aprovou como proxima melhoria da frente de tabelas personalizadas a capacidade de escolher, por coluna, quais campos poderao virar filtros estruturados na tela de linhas
- a busca textual simples continua valida e nao sera substituida
- primeiro recorte priorizado:
  - data
  - mes/competencia
  - inteiro
  - decimal
  - monetario
  - percentual
- operadores sugeridos por tipo ja registrados nos documentos oficiais
- totalizadores e exportacao XLSX futura devem respeitar os filtros ativos quando essa camada existir
- recomendacao tecnica inicial registrada:
  - tentar configuracao por `ColunaPersonalizada.configuracao_json`
  - se isso nao bastar, abrir microetapa propria com model/migration
- auditoria tecnica complementar desta pendencia:
  - `ColunaPersonalizada` ja usa `configuracao_json` com validacao controlada para `lista_opcoes`
  - `ColunaPersonalizadaForm` ja concentra configuracoes documentais/operacionais da coluna, inclusive totalizadores
  - a tela de linhas ja reutiliza um pipeline unico para `busca -> renderizacao -> totalizadores -> exportacao XLSX`
  - por isso, o primeiro recorte dos filtros por coluna foi classificado como compativel com configuracao em JSON, sem migration imediata
- decisao documental desta microetapa:
  - usar bloco aninhado `configuracao_json.filtro` no primeiro recorte
  - manter operadores derivados do `tipo_dado`, sem configuracao livre por usuaria
  - exibir filtros estruturados apenas quando existir pelo menos uma coluna habilitada
  - combinar `busca textual simples + filtros estruturados` no mesmo resultado final da tela
  - fazer totalizadores e exportacao XLSX refletirem esse mesmo resultado filtrado
- gatilhos para reclassificar como `REQUER MODEL/MIGRATION` antes de implementar:
  - crescimento do JSON para multiplos modos ou metadados independentes do tipo
  - necessidade de indexacao/consulta mais forte no banco
  - surgimento de visoes salvas, auditoria propria de filtros ou composicoes mais avancadas

Status apos implementacao:
- `configuracao_json.filtro` passou a ser o ponto real de persistencia no primeiro recorte
- a configuracao ficou restrita a colunas elegiveis e habilitadas explicitamente
- a tela de linhas passou a combinar `busca textual + filtros estruturados`
- totalizadores e exportacao XLSX passaram a respeitar o mesmo resultado filtrado
- permanecem fora desta entrega:
  - texto avancado
  - multiplas opcoes de lista
  - booleano
  - visoes salvas
  - agrupamentos
  - dashboard
  - logica composta avancada

Fora do primeiro recorte:
- texto avancado
- multiplas opcoes de lista
- booleano
- visoes salvas
- agrupamentos
- dashboard
- logica composta avancada

Proxima microetapa recomendada:
- apos os filtros por coluna, executar auditoria tecnica dedicada dos recibos/documentos atuais para abrir a SPEC segura do `Recibo especial`

### 51. Documentos financeiros - recibo especial em lote com favorecido manual

Status: AUDITADO TECNICAMENTE / PRONTO PARA SPEC FUNCIONAL SEGURA

Consolidacao:
- a usuaria aprovou uma nova acao documental futura, separada dos recibos atuais
- a ideia e permitir selecionar lancamentos de varios favorecidos e escolher manualmente um favorecido cadastrado para aparecer como destinatario principal do recibo
- os favorecidos originais dos lancamentos devem continuar aparecendo no corpo/descricao dos itens apenas como nome compondo a descricao atual, sem rotulo adicional
- regra textual aprovada:
  - usar composicao do tipo `Descricao atual - Nome do favorecido`
  - nao usar `Favorecido original`
  - nao usar `Favorecido original: Nome`
- a frente deve ser isolada e nao pode alterar:
  - recibo em lote atual
  - recibos por favorecido atuais
  - termo anual de quitacao
  - lancamentos
  - favorecido real dos lancamentos
  - financeiro oficial

Dependencia obrigatoria:
- antes de implementar, precisa haver auditoria tecnica do fluxo atual de recibos, incluindo views, templates, helpers, recebimento dos ids selecionados e validacao do favorecido

Achados da auditoria:
- a listagem de lancamentos oferece hoje a acao em lote `Recibos em lote` e envia os selecionados para `LancamentoFinanceiroAcoesLoteView`
- essa acao resolve ids simples e grupos de rateio no backend e redireciona para `lancamento-recibos-por-favorecido`
- o recibo em lote tecnico atual (`lancamento-recibo-lote`) existe, mas so aceita lancamentos do mesmo favorecido
- nesse fluxo tecnico, o destinatario atual do documento continua vindo do primeiro favorecido do lote e os itens continuam consolidados apenas por descricao exatamente igual
- os recibos por favorecido atuais aceitam multiplos favorecidos e geram um recibo por grupo, usando o mesmo template base do recibo atual
- o termo anual usa fluxo, view e template separados, baseados nos filtros da listagem, e deve permanecer intocado
- todos esses fluxos usam a permissao `financeiro.lancamentos.emitir_recibo`
- a mesma listagem separa acao documental por linha, acao em lote e botao proprio do termo anual
- os testes encontrados hoje cobrem melhor a exibicao das acoes documentais na listagem do que o contrato interno do fluxo futuro especial

SPEC segura consolidada:
- o `Recibo especial` deve nascer como acao nova e isolada
- nao deve alterar:
  - recibo em lote atual
  - recibos por favorecido atuais
  - termo anual de quitacao
  - lancamentos
  - favorecido real dos lancamentos
- deve aceitar lancamentos selecionados de varios favorecidos
- deve exigir escolha manual de um favorecido cadastrado como destinatario principal
- deve compor cada item como `descricao atual - nome do favorecido original`
- nao deve usar `Favorecido original`
- nao deve usar `Favorecido original: Nome`

Arquitetura recomendada:
- criar nova view intermediaria para validar selecao e escolher o favorecido
- criar nova view/template de emissao documental final ou parcial nova derivada do recibo atual
- preservar helpers e templates atuais dos recibos homologados, evitando condicoes excepcionais dentro deles

Proxima microetapa recomendada:
- apos esta auditoria, abrir implementacao funcional minima do `Recibo especial` com testes de nao regressao dos documentos atuais

Status apos implementacao:
- o `Recibo especial` foi implementado como acao nova e isolada da `lancamento_list`
- o fluxo agora possui:
  - selecao em lote reaproveitando os ids resolvidos pelo backend atual
  - etapa intermediaria de escolha manual do favorecido destinatario
  - emissao final em template proprio, sem alterar o template homologado dos recibos atuais
- guardrails preservados:
  - o recibo em lote tecnico continua exigindo mesmo favorecido
  - os recibos por favorecido continuam agrupando por pessoa
  - o termo anual continua com rota e template proprios
  - o favorecido real e a descricao persistida dos lancamentos nao sao alterados

Pendencia futura remanescente:
- homologacao visual/documental do `Recibo especial` e decisao sobre permissao dedicada e auditoria propria da nova acao

Atualizacao de refinamento:
- titulo impresso do documento especial reduzido para `RECIBO`
- ajuste de ortografia/pontuacao dos textos fixos do recibo especial
- busca por favorecido destinatario adicionada no formulario com filtro por trecho do nome, sem mudar regra de validacao por ID
- nenhum impacto nos fluxos atuais de recibo, termo anual ou dados operacionais

Atualizacao de refinamento de UX:
- o fluxo de selecao do favorecido no `Recibo especial` foi ajustado para nao exibir dois campos visiveis ao usuario
- permaneceu apenas um campo pesquisavel visivel, com selecao por resultados e gravacao do ID real no campo do formulario
- o comportamento de busca foi reforcado para trecho do nome, ignorando caixa e acentos
- o envio sem selecao valida passou a ter mensagem clara na tela
- o cabecalho da tela de selecao recebeu ajuste de espaco para evitar sobreposicao de titulo/subtitulo

Atualizacao de homologacao:
- a usuaria homologou localmente o primeiro recorte funcional/visual do `Recibo especial em lote` com retorno `Esta OK`
- escopo homologado:
  - fluxo funcional da nova acao documental isolada
  - titulo impresso `RECIBO`
  - busca de favorecido por trecho do nome
  - campo pesquisavel unico (sem dois campos visiveis)
  - correcao da sobreposicao de titulo/subtitulo
  - descricao composta `descricao atual - nome do favorecido original`
- preservacoes homologadas:
  - recibo em lote atual sem alteracao
  - recibos por favorecido atuais sem alteracao
  - termo anual sem alteracao
  - lancamentos e favorecido real sem alteracao
- pendencias futuras opcionais mantidas:
  - permissao dedicada para o recibo especial
  - auditoria operacional propria
  - ajustes finos de impressao se surgirem no uso real

### 52. Tabelas personalizadas - formulas guiadas por coluna / Onda 1

Status: IMPLEMENTADO PARCIALMENTE (CONFIGURACAO VISUAL + VALIDACAO ESTRUTURAL, SEM CALCULO)

Consolidacao:
- a SPEC curta de formulas guiadas foi convertida na primeira onda funcional, restrita a configuracao da formula na estrutura da coluna
- a persistencia inicial ficou em `ColunaPersonalizada.configuracao_json.formula`, sem migration
- a liberacao da formula ficou separada de `editar_estrutura`, exigindo `financeiro.tabelas_personalizadas.configurar_formula`
- a secao visual de formula guiada passou a usar campos orientados, sem expressao textual livre

Validacoes entregues:
- operacoes permitidas apenas:
  - `soma`
  - `subtracao`
  - `multiplicacao`
  - `divisao`
- colunas-fonte permitidas apenas quando forem:
  - da mesma tabela
  - numericas
  - ativas
  - visiveis
  - nao calculadas
- resultado permitido apenas para:
  - `decimal`
  - `monetario`
- bloqueios estruturais entregues:
  - formula fora de `tipo_dado=formula_controlada`
  - coluna de formula sem `calculada=True`
  - formula sobre formula
  - uso da propria coluna
  - configuracao incompleta
  - operando invalido
  - operando textual/data/competencia/lista/booleano
  - `subtracao` e `divisao` com quantidade invalida de operandos

Guardrails preservados:
- sem calculo funcional
- sem alteracao de `valor_calculado`
- sem alteracao de busca, filtros, totalizadores e XLSX
- sem impacto em `LancamentoFinanceiro` e no financeiro oficial

Proxima microetapa recomendada:
- Onda 2 de formulas guiadas: calcular e exibir o resultado somente leitura na listagem de linhas, ainda sem integrar totalizador sobre calculada

### 53. Tabelas personalizadas - formulas guiadas por coluna / Onda 2

Status: IMPLEMENTADO PARCIALMENTE (CALCULO EM LEITURA + EXIBICAO SOMENTE LEITURA)

Consolidacao:
- a formula guiada passou a ser calculada apenas em tempo de leitura na listagem de linhas
- a coluna calculada agora aparece na grade, mas continua fora do formulario de criacao/edicao de linhas
- a persistencia continua ausente:
  - sem uso de `valor_calculado`
  - sem migration
  - sem escrita em banco para o resultado

Comportamento seguro entregue:
- operando ausente gera celula vazia
- divisao por zero gera celula vazia
- `decimal` respeita `casas_decimais`
- `monetario` aparece com 2 casas e formato brasileiro na tela

Guardrails preservados:
- busca textual continua sem considerar calculadas
- filtros estruturados continuam sem considerar calculadas
- totalizadores continuam fora para calculadas
- exportacao XLSX continua sem incluir valor calculado
- sem impacto em `LancamentoFinanceiro` e no financeiro oficial

Proxima microetapa recomendada:
- decidir em microetapa propria se busca e XLSX passarao a refletir colunas calculadas antes de abrir qualquer conversa sobre totalizadores em calculadas

### 54. Tabelas personalizadas - UX autodidata no formulario de colunas

Status: IMPLEMENTADO

Consolidacao:
- formulario de colunas passou a mostrar blocos contextuais apenas quando o tipo selecionado exigir
- recorte entregue:
  - `opcoes_lista` apenas em `lista_opcoes`
  - `formula guiada` apenas com permissao e em `formula_controlada`
  - `filtro estruturado` apenas para tipos elegiveis
  - `totalizadores` apenas quando compativeis com o tipo atual
- comportamento dinamico em JavaScript local, sem rota, sem AJAX e sem dependencia externa
- calculo de formula, regras de persistencia e contratos de busca/filtro/totalizador/XLSX preservados

### 55. Tabelas personalizadas - formulas guiadas por coluna / Onda 3

Status: IMPLEMENTADO PARCIALMENTE (BUSCA + XLSX)

Consolidacao:
- busca textual simples agora considera colunas calculadas visiveis, ativas e com formula habilitada pelo valor final formatado
- exportacao XLSX agora inclui colunas calculadas visiveis com o valor final calculado, sem formula Excel e sem configuracao interna exposta
- operando ausente e divisao por zero continuam gerando celula vazia

Guardrails preservados:
- sem persistencia em `valor_calculado`
- filtros estruturados continuam fora para calculadas
- totalizadores continuam fora para calculadas
- sem impacto em `LancamentoFinanceiro` e no financeiro oficial

### 56. Tabelas personalizadas - clareza do tipo de resultado da formula

Status: IMPLEMENTADO

Consolidacao:
- formulario de coluna recebeu esclarecimento textual no campo `Tipo do resultado`
- primeiro recorte permanece restrito a:
  - `Decimal`
  - `Monetario`
- orientacao explicita adicionada: `Decimal` com `0` casas pode ser usado para resultado sem casas decimais

Fora desta etapa:
- liberar `Inteiro` e `Percentual` como resultado de formula
- qualquer alteracao em calculo, busca, XLSX, filtros estruturados ou totalizadores

### 57. Tabelas personalizadas - SPEC de totalizadores em colunas calculadas

Status: DOCUMENTADO (SEM IMPLEMENTACAO)

Consolidacao:
- foi auditado o estado atual da frente apos formulas guiadas, busca textual e XLSX em colunas calculadas
- os totalizadores atuais seguem restritos a colunas comuns configuradas explicitamente e calculados pelo mesmo pipeline da tela e do XLSX
- colunas calculadas continuam fora dos totalizadores por bloqueio coerente em model, configuracao e montagem de `colunas_totalizaveis`
- as formulas continuam:
  - calculadas apenas em tempo de leitura
  - sem persistencia em `valor_calculado`
  - exibidas na grade
  - consideradas na busca textual
  - exportadas no XLSX como valor final

Decisao recomendada:
- manter colunas calculadas fora dos totalizadores no MVP

Justificativa:
- evita leitura duplicada quando a formula deriva de colunas que ja possuem rodape
- evita agregar resultados vazios por operando ausente ou divisao por zero como se fossem numeros comuns
- preserva o recorte atual ja homologavel de grade + busca + XLSX sem abrir nova camada de ambiguidade no rodape

Reabertura futura, se necessaria:
- apenas em microetapa propria
- apenas para `resultado_tipo` `decimal` e `monetario`
- totalizando o valor final calculado, nunca os operandos
- ignorando linhas com resultado vazio
- mantendo tela e XLSX com o mesmo rodape
- comecando, se aprovado, por `soma` e `contagem`

### 58. Tabelas personalizadas - homologacao documental do MVP

Status: DOCUMENTADO (MVP FUNCIONAL CONSOLIDADO)

Consolidacao:
- o primeiro recorte funcional da frente de tabelas personalizadas foi consolidado documentalmente como entregue
- escopo consolidado no MVP atual:
  - estrutura, permissoes, menu/listagem
  - cadastro de tabelas e colunas
  - listas de opcoes
  - linhas e valores editaveis
  - busca textual simples
  - filtros estruturados por coluna comum
  - totalizadores em colunas comuns
  - exportacao XLSX
  - formulas guiadas por coluna
  - calculo em tempo de leitura
  - busca e XLSX considerando valor calculado
  - UX autodidata no formulario de colunas

Limites mantidos fora do MVP:
- totalizadores em colunas calculadas
- filtros estruturados em colunas calculadas
- formula livre estilo Excel
- formula por celula
- importacao
- edicao em massa
- agrupamentos
- visoes salvas
- dashboard
- auditoria operacional propria
- integracao escrevente com financeiro oficial

Proxima frente recomendada:
- abrir microetapa de SPEC/auditoria tecnica da auditoria operacional propria da frente para decidir trilha de eventos auditaveis de estrutura, formula e linhas; exportacao XLSX fica fora do primeiro recorte

### 59. Tabelas personalizadas - SPEC da auditoria operacional propria

Status: DOCUMENTADO (SEM IMPLEMENTACAO)

Consolidacao:
- foi auditada a base atual da auditoria do `financeiro` e os pontos de escrita da frente de `Tabelas personalizadas`
- a recomendacao mais segura do primeiro recorte e reaproveitar `AuditoriaFinanceiro`, com helpers/snapshots especificos da frente

Eventos obrigatorios do primeiro recorte futuro:
- criacao/edicao de tabela
- criacao/edicao de coluna
- alteracao de opcoes de lista
- alteracao de filtro estruturado
- alteracao de totalizadores
- configuracao/alteracao de formula
- criacao/edicao de linha

Decisao fechada para o primeiro recorte:
- exportacao XLSX nao entra como evento auditavel inicial
- justificativa:
  - e acao de leitura/extracao
  - nao altera dado nem estrutura
  - manter fora agora reduz volume de logs e melhora leitura da auditoria operacional
- reabertura futura:
  - possivel em microetapa propria, se houver necessidade de seguranca, controle de acesso ou rastreabilidade de extracoes

Fora do primeiro recorte:
- visualizacao de tela
- busca simples
- filtros usados apenas para leitura
- calculo de formula em leitura
- navegacao comum

Guardrails:
- sem persistir `valor_calculado`
- sem auditar calculo em leitura
- sem impacto no financeiro oficial
- sem model/migration nesta etapa documental

Status apos implementacao:
- IMPLEMENTADO NO PRIMEIRO RECORTE (OPERACIONAL MINIMO)

Baixa desta frente:
- auditoria minima entregue reaproveitando `AuditoriaFinanceiro`
- eventos auditados:
  - criacao/edicao de tabela
  - criacao/edicao de coluna
  - criacao/edicao de linha
- alteracoes de opcoes, filtro, totalizadores e formula auditadas no diff da coluna
- exportacao XLSX permanece fora do recorte inicial de auditoria
