# MATRIZ DE PERMISSOES DO SISTEMA

## Objetivo do documento

Registrar a primeira versao formal da matriz hierarquica de permissoes do sistema Casa Espirita, no formato `Modulo > Tela/Recurso > Acao`, para orientar a futura implementacao de autenticacao, perfis e governanca de acesso sem antecipar codigo nesta etapa.

Este documento e protegido e deve ser atualizado apenas em microetapas explicitamente autorizadas, sempre por acrescimo, consolidacao ou ajuste cirurgico, preservando historico e cronologia.

## Premissas de modelagem de acesso

- Perfil e um pacote de permissoes por funcao.
- Na V1, cada usuario deve ter 1 perfil base.
- A administracao funcional do sistema deve ser separada da administracao tecnica/global do Django admin (`/admin/`).
- Esconder item de menu nao basta: a permissao precisa ser respeitada tambem em tela, botao/acao e endpoint auxiliar.
- Acoes destrutivas e sensiveis devem ser mais restritas do que leitura e operacao comum.
- Leitura, operacao comum, operacao sensivel e administracao global devem permanecer conceitualmente diferenciadas.
- Endpoints auxiliares de autocomplete, historico, sugestoes e downloads devem herdar a governanca do recurso de origem.

## Estrutura hierarquica da matriz

- Modulo: area funcional principal do sistema (`financeiro`, `biblioteca`, `configuracoes`, `admin`).
- Tela/Recurso: tela, cadastro, relatorio, fluxo operacional ou endpoint auxiliar exposto ao usuario ou ao front-end.
- Acao: operacao real permitida sobre aquele recurso, por exemplo listar, visualizar, criar, editar, excluir, importar, exportar, imprimir ou executar acao em lote.

## Perfis-base inicialmente previstos

| Perfil-base | Intencao funcional | Observacao |
|---|---|---|
| Administrador geral | Administrar sistema, configuracoes e operacao completa | Deve ser o unico candidato natural a acesso tecnico/global amplo, inclusive `/admin/`, quando isso for implementado |
| Gestao administrativa | Supervisionar operacao e configuracoes funcionais sem necessariamente ter administracao tecnica global | Pode ter leitura ampla, relatorios, auditoria e parte das configuracoes funcionais |
| Operador financeiro | Executar rotinas operacionais do modulo financeiro | Deve concentrar lancamentos, cadastros operacionais e rotinas financeiras |
| Operador biblioteca | Executar rotinas operacionais do modulo biblioteca | Deve concentrar cadastros e lancamentos operacionais da biblioteca |
| Consulta/visualizacao | Acesso majoritariamente de leitura | Deve evitar escrita, exclusao, importacao e configuracoes sensiveis |

## Matriz por modulo, tela/recurso e acao

Legenda de permissao inicial:
- `S` = permitido na proposta inicial
- `-` = nao previsto na proposta inicial
- `R` = requer revisao explicita na proxima etapa antes de implementar

### Modulo financeiro

| Modulo | Tela/Recurso | Acao | Administrador geral | Gestao administrativa | Operador financeiro | Operador biblioteca | Consulta/visualizacao | Observacoes |
|---|---|---|---|---|---|---|---|---|
| financeiro | Visao geral / Home secundaria | visualizar | S | S | S | - | S | `/financeiro/inicio/` e rota secundaria; raiz `/financeiro/` redireciona para Lancamentos |
| financeiro | Lancamentos | listar/visualizar | S | S | S | - | S | Base da navegacao do modulo financeiro |
| financeiro | Lancamentos | criar | S | S | S | - | - | Inclui lancamento comum e lancamento com rateio |
| financeiro | Lancamentos | editar | S | S | S | - | - | Inclui edicao individual e edicao coordenada de grupo rateado |
| financeiro | Lancamentos | excluir | S | R | S | - | - | Acao destrutiva sensivel; confirmar se Gestao administrativa pode excluir na V1 |
| financeiro | Lancamentos | clonar | S | S | S | - | - | Inclui clone comum e clone por grupo rateado |
| financeiro | Lancamentos | emitir recibo | S | S | S | - | S | Hoje a acao aparece apenas quando faz sentido no fluxo atual |
| financeiro | Lancamentos | acoes em lote | S | R | S | - | - | Alterar status em lote e excluir selecionados |
| financeiro | Lancamentos | importar | S | R | S | - | - | Importacao XLSX all-or-nothing, sem criacao automatica de cadastros auxiliares |
| financeiro | Lancamentos | exportar | S | S | S | - | S | Exportacao da listagem filtrada |
| financeiro | Lancamentos | baixar modelo de importacao | S | S | S | - | R | Definir se perfil somente leitura pode baixar modelo sem poder importar |
| financeiro | Lancamentos | baixar relatorio de inconsistencias | S | S | S | - | - | Associado ao fluxo de importacao |
| financeiro | Lancamentos | acessar autocomplete/historico/sugestoes | S | S | S | - | R | Endpoints auxiliares do formulario de lancamento devem acompanhar permissao da tela/acao principal |
| financeiro | Extrato geral | visualizar/filtrar | S | S | S | - | S | `/financeiro/extratos/` |
| financeiro | Extrato por conta | visualizar/filtrar | S | S | S | - | S | `/financeiro/contas/<pk>/extrato/` |
| financeiro | Resumo financeiro | visualizar/filtrar | S | S | S | - | S | `/financeiro/resumo/` |
| financeiro | Resumo financeiro | imprimir | S | S | S | - | S | Impressao deve continuar respeitando permissao de leitura |
| financeiro | Prestacao de contas | visualizar/filtrar | S | S | S | - | S | `/financeiro/prestacao-contas/` |
| financeiro | Prestacao de contas | imprimir | S | S | S | - | S | Impressao deve continuar respeitando permissao de leitura |
| financeiro | Auditoria do Financeiro | ver auditoria | S | S | R | - | - | Definir se Operador financeiro pode ver auditoria ou se isso fica restrito a Gestao/Administrador |
| financeiro | Contas | listar/visualizar | S | S | S | - | S | Cadastro operacional do financeiro |
| financeiro | Contas | criar | S | S | S | - | - | Inclui dados de saldo inicial |
| financeiro | Contas | editar | S | S | S | - | - | Alteracao pode afetar extratos e relatorios |
| financeiro | Contas | excluir | S | R | R | - | - | Acao destrutiva sensivel; validar impacto operacional |
| financeiro | Contas | acessar autocomplete | S | S | S | - | R | Endpoint auxiliar do formulario de lancamento |
| financeiro | Pessoas | listar/visualizar | S | S | S | - | S | Cadastro operacional do financeiro |
| financeiro | Pessoas | criar | S | S | S | - | - |  |
| financeiro | Pessoas | editar | S | S | S | - | - |  |
| financeiro | Pessoas | excluir | S | R | R | - | - | Acao destrutiva sensivel; validar impacto operacional |
| financeiro | Pessoas | acessar autocomplete/historico | S | S | S | - | R | Endpoints auxiliares do formulario de lancamento |
| financeiro | Categorias | listar/visualizar | S | S | S | - | S | `Categoria` como agrupadora analitica |
| financeiro | Categorias | criar | S | S | S | - | - | Cadastro de categoria pai |
| financeiro | Categorias | editar | S | S | S | - | - |  |
| financeiro | Categorias | excluir | S | R | R | - | - | Acao destrutiva sensivel |
| financeiro | Subcategorias | listar/visualizar | S | S | S | - | S | `Subcategoria` como item operacional lancavel; mesma tela/modelo de categorias |
| financeiro | Subcategorias | criar | S | S | S | - | - | Cadastro de categoria filha |
| financeiro | Subcategorias | editar | S | S | S | - | - |  |
| financeiro | Subcategorias | excluir | S | R | R | - | - | Acao destrutiva sensivel |
| financeiro | Subcategorias | acessar autocomplete | S | S | S | - | R | Endpoint auxiliar do formulario de lancamento |
| financeiro | Centros de custo | listar/visualizar | S | S | S | - | S | Cadastro operacional do financeiro |
| financeiro | Centros de custo | criar | S | S | S | - | - |  |
| financeiro | Centros de custo | editar | S | S | S | - | - |  |
| financeiro | Centros de custo | excluir | S | R | R | - | - | Acao destrutiva sensivel |
| financeiro | Centros de custo | acessar autocomplete | S | S | S | - | R | Endpoint auxiliar do formulario de lancamento |
| financeiro | Assinaturas institucionais | listar/visualizar | S | S | - | - | - | Configuracao funcional sensivel |
| financeiro | Assinaturas institucionais | criar | S | S | - | - | - |  |
| financeiro | Assinaturas institucionais | editar | S | S | - | - | - |  |
| financeiro | Assinaturas institucionais | excluir | S | R | - | - | - | Acao destrutiva sensivel |
| financeiro | Configuracoes institucionais | listar/visualizar | S | S | - | - | - | Configuracao funcional sensivel |
| financeiro | Configuracoes institucionais | criar | S | S | - | - | - |  |
| financeiro | Configuracoes institucionais | editar | S | S | - | - | - |  |
| financeiro | Configuracoes institucionais | excluir | S | R | - | - | - | Acao destrutiva sensivel |

### Modulo biblioteca

| Modulo | Tela/Recurso | Acao | Administrador geral | Gestao administrativa | Operador financeiro | Operador biblioteca | Consulta/visualizacao | Observacoes |
|---|---|---|---|---|---|---|---|---|
| biblioteca | Autores | listar/visualizar | S | S | - | S | S | Menu proprio em `biblioteca/templates/biblioteca/base.html` |
| biblioteca | Autores | criar | S | S | - | S | - | Nao ha rotas de editar/excluir no estado atual |
| biblioteca | Livros | listar/visualizar | S | S | - | S | S |  |
| biblioteca | Livros | criar | S | S | - | S | - | Nao ha rotas de editar/excluir no estado atual |
| biblioteca | Vendas | listar/visualizar | S | S | - | S | S |  |
| biblioteca | Vendas | criar | S | S | - | S | - | Nao ha rotas de editar/excluir no estado atual |
| biblioteca | Emprestimos | listar/visualizar | S | S | - | S | S |  |
| biblioteca | Emprestimos | criar | S | S | - | S | - | Nao ha rotas de editar/excluir no estado atual |

### Modulo configuracoes

| Modulo | Tela/Recurso | Acao | Administrador geral | Gestao administrativa | Operador financeiro | Operador biblioteca | Consulta/visualizacao | Observacoes |
|---|---|---|---|---|---|---|---|---|
| configuracoes | SiteConfig `/` | visualizar | S | S | R | R | S | Tela institucional na raiz do projeto; decidir na proxima etapa se operadores podem acessar leitura dessa pagina |

### Administracao tecnica/global

| Modulo | Tela/Recurso | Acao | Administrador geral | Gestao administrativa | Operador financeiro | Operador biblioteca | Consulta/visualizacao | Observacoes |
|---|---|---|---|---|---|---|---|---|
| admin | Django admin `/admin/` | acesso tecnico/global | S | - | - | - | - | Deve permanecer separado da administracao funcional do sistema |

## Regras gerais de aplicacao

- A permissao final deve ser validada no backend, mesmo quando menu, botao ou link estiverem escondidos na interface.
- Menu lateral, topbar, atalhos, listagens, formularios, relatorios, impressao, importacao/exportacao, auditoria e endpoints auxiliares devem seguir a mesma decisao de acesso.
- Acoes destrutivas (`excluir`, exclusao em lote), operacoes de configuracao institucional e visibilidade de auditoria devem receber revisao mais restritiva na V1.
- Acoes de leitura podem ser mais amplas do que acoes de escrita, mas nao devem abrir endpoints auxiliares que permitam contornar a governanca.
- Em recursos com `Categoria` e `Subcategoria`, a matriz deve preservar a distincao conceitual mesmo quando a UI/modelo atual compartilha a mesma tela e tabela.
- Em `Lancamentos`, a governanca deve considerar tambem operacoes de rateio, clone, recibo, regras automaticas e acoes em lote, nao apenas CRUD basico.
- O desenho de UX da futura implementacao deve evitar esconder acoes sem explicar ausencia quando isso gerar confusao operacional, preservando o padrao visual consolidado no `financeiro`.

## Itens futuros previstos, sem implementacao nesta etapa

- Extras individuais por usuario alem do perfil base.
- Bloqueios individuais por usuario mesmo quando o perfil base permitir a acao.
- Formula conceitual futura: `permissao final = perfil base + extras individuais - bloqueios individuais`.
- Persistencia de preferencias de visualizacao por perfil/usuario, quando fizer sentido.
- Log de acesso ao sistema em camada propria, separado da auditoria funcional do `financeiro`.
- Refinamento da matriz apos auditoria humana, antes de qualquer implementacao de login, decorators, mixins, grupos ou telas de cadastro de perfis.
