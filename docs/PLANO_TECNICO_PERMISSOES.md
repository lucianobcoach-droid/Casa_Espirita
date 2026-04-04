# PLANO TECNICO DE PERMISSOES E AUTENTICACAO

## 1. Objetivo tecnico da frente

Definir a arquitetura tecnica e a ordem incremental de implementacao da frente de `permissoes/autenticacao`, tomando `docs/MATRIZ_PERMISSOES.md` como base funcional e preservando o desenvolvimento em microetapas pequenas, auditaveis e sem regressao.

Este documento nao implementa codigo. Ele serve como ponte entre a matriz funcional ja fechada e as proximas entregas tecnicas da V1.

## 2. Escopo da V1

- autenticar usuarios com a base padrao do Django
- associar cada usuario a 1 perfil base do sistema
- representar permissoes no formato `Modulo > Tela/Recurso > Acao`
- aplicar as permissoes em rotas/views, menus/sidebar, botoes/acoes e endpoints auxiliares
- iniciar o enforcement real pelo modulo `financeiro`, por ser hoje o modulo operacional mais maduro e a referencia visual/UX do sistema
- manter `/admin/` como administracao tecnica/global separada da administracao funcional do sistema

## 3. Fora de escopo da V1

- permissoes extras individuais por usuario
- bloqueios individuais por usuario
- formula final composta em runtime com extras/bloqueios individuais
- workflow avancado de aprovacao de acesso
- log dedicado de acesso em camada propria
- preferencias persistentes por perfil/usuario
- migracao imediata de todos os modulos em uma unica etapa
- refatoracao ampla de telas fora da aplicacao necessaria de permissoes

## 4. Decisao tecnica de arquitetura

### Alternativas avaliadas

- usar apenas `Group/Permission` nativo do Django
- usar apenas uma estrutura propria de perfis/permissoes do sistema
- usar um modelo hibrido

### Decisao recomendada

Adotar um modelo hibrido, com separacao clara de responsabilidades:
- usar `User`, autenticacao, sessao e fluxo de login/logout da base padrao do Django
- manter uma camada propria do sistema para `Perfil`, `Permissao do sistema` e vinculos de autorizacao, usando `docs/MATRIZ_PERMISSOES.md` como referencia semantica
- nao usar `Group/Permission` nativo do Django como fonte principal da governanca funcional da V1
- reservar `/admin/` e eventuais permissoes tecnicas do Django para administracao tecnica/global, separada da matriz funcional da operacao diaria

### Justificativa

- a matriz aprovada e hierarquica por `Modulo > Tela/Recurso > Acao`, com granularidade funcional propria do sistema
- a V1 precisa refletir regras de menu, botoes, endpoints auxiliares e administracao funcional, nao apenas permissoes tecnicas de models
- o desenho futuro ja preve `perfil base + extras individuais - bloqueios individuais`, o que se encaixa melhor em uma camada propria de dominio de acesso
- a autenticacao do Django continua sendo aproveitada, reduzindo risco tecnico e evitando reinventar login/sessao
- manter a governanca funcional separada do `Group/Permission` nativo reduz acoplamento ao admin tecnico e facilita uma UI propria de perfis no futuro

## 5. Modelagem conceitual minima esperada

### Perfil base
- representa uma funcao operacional reutilizavel
- exemplos iniciais: `Administrador geral`, `Gestao administrativa`, `Operador financeiro`, `Operador biblioteca`, `Consulta/visualizacao`

### Permissao do sistema
- representa uma acao funcional em granularidade `modulo`, `recurso`, `acao`
- deve ter um codigo estavel, por exemplo `financeiro.lancamentos.criar`
- pode guardar rotulo legivel e metadados de agrupamento para a futura UI hierarquica de perfis

### Vinculo perfil-permissao
- define quais permissoes compoem cada perfil base
- deve permitir montar a tela futura de configuracao hierarquica de perfis

### Vinculo usuario-perfil
- na V1, cada usuario tem 1 perfil base
- esse vinculo deve ser simples, explicito e facil de auditar

### Compatibilidade futura para excecoes individuais
- prever no desenho, sem implementar agora, estruturas futuras para `permissoes extras por usuario` e `bloqueios por usuario`
- formula conceitual futura ja consolidada: `permissao final = perfil base + extras individuais - bloqueios individuais`
- na V1, a permissao efetiva deve ser somente o conjunto do perfil base

## 6. Estrategia de aplicacao das permissoes

### Rotas/views
- toda rota operacional deve exigir usuario autenticado e validar permissao funcional da acao
- endpoints auxiliares de autocomplete, historico, sugestoes, importacao, exportacao, acoes em lote, download de modelo e relatorio de inconsistencias devem ser protegidos com a mesma regra do recurso principal
- a ausencia de permissao deve bloquear a execucao no backend, mesmo que o botao ou menu nao apareca

### Menu/sidebar/atalhos
- itens de menu e atalhos devem ser renderizados de acordo com as permissoes do perfil
- esconder navegacao melhora UX, mas nao substitui validacao no backend
- `Operador biblioteca` nao deve herdar navegacao do `financeiro`
- `Consulta/visualizacao` deve enxergar apenas entradas coerentes com leitura/impressao/exportacao permitidas

### Botoes/acoes em templates
- botoes de criar, editar, excluir, clonar, recibo, lote, importar, exportar, imprimir e links auxiliares devem aparecer somente quando a permissao correspondente existir
- se a ausencia de uma acao puder gerar confusao operacional, a UI deve ser revisada de forma coerente com `docs/PADRAO_UX_SISTEMA.md`

### Admin tecnico/global
- `/admin/` deve permanecer restrito ao perfil com administracao tecnica/global
- administracao funcional do sistema, como configuracoes institucionais do `financeiro`, deve continuar separada do admin tecnico

## 7. Ordem incremental de implementacao

### Microetapa 1 - Estrutura de dados de acesso
- criar a base tecnica de perfis, permissoes do sistema e vinculos perfil-permissao
- criar o vinculo usuario-perfil da V1
- preparar seeds/dados iniciais coerentes com `docs/MATRIZ_PERMISSOES.md`
- nao aplicar enforcement amplo em todas as telas ainda

### Microetapa 2 - Autenticacao e primeiro enforcement backend no financeiro
- ativar login/logout com `User` do Django
- aplicar protecao de autenticacao e permissao funcional primeiro no `financeiro`
- priorizar rotas de maior risco e maior uso: `Lancamentos`, `Auditoria`, `Configuracoes institucionais`, `Assinaturas`, `Importar`, `Exportar`, `Acoes em lote` e endpoints auxiliares

### Microetapa 3 - Menu, botoes e templates do financeiro
- condicionar sidebar, atalhos e botoes do `financeiro` as permissoes efetivas do usuario
- garantir que a UI nao ofereca acoes indisponiveis nem quebre o padrao visual ja consolidado

### Microetapa 4 - Expansao para biblioteca e configuracoes
- aplicar a mesma base de autorizacao ao `biblioteca` e ao `SiteConfig /`
- manter `/admin/` restrito a administracao tecnica/global

### Microetapa 5 - Tela de administracao funcional de perfis
- construir a UI propria de manutencao dos perfis e de seus vinculos com permissoes
- organizar essa UI na hierarquia `Modulo > Tela/Recurso > Acao`
- manter a governanca funcional separada do admin tecnico

### Microetapa 6 - Endurecimento, auditoria e compatibilidade futura
- revisar cobertura de rotas, botoes e endpoints auxiliares
- validar cenarios de perfil por perfil
- preparar a base para evolucao futura de extras/bloqueios individuais, sem ativar essa extensao na V1

## 8. Riscos, dependencias e cuidados de compatibilidade

- risco de proteger a tela principal e esquecer endpoints auxiliares usados por JavaScript
- risco de esconder menu/botao e ainda deixar a view executavel por acesso direto
- risco de quebrar fluxos ja consolidados do `financeiro`, especialmente importacao/exportacao, rateio, clone, regras automaticas, recibo e acoes em lote
- risco de acoplar a governanca funcional ao `/admin/` e dificultar uma UI propria de perfis
- risco de liberar leitura sensivel por engano em auditoria, configuracoes institucionais ou downloads auxiliares
- dependencia de uma estrategia clara para dados iniciais dos perfis e permissoes antes do primeiro rollout de enforcement
- dependencia de revisao cuidadosa da sidebar e dos templates para nao gerar UX incoerente quando uma acao estiver ausente

## 9. Primeiro ponto de aplicacao real

O primeiro modulo de aplicacao real da V1 deve ser o `financeiro`, por ser o modulo com maior maturidade funcional, maior superficie operacional, mais endpoints auxiliares ja existentes e o shell visual usado hoje como referencia do sistema.

Dentro do `financeiro`, a prioridade inicial de enforcement deve recair sobre:
- `Lancamentos`
- `Auditoria do Financeiro`
- `Configuracoes institucionais`
- `Assinaturas institucionais`
- `Importar/Exportar`
- endpoints auxiliares de formulario e historico
