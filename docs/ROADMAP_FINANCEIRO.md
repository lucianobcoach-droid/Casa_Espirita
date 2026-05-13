# ROADMAP FINANCEIRO

Data: 2026-05-13

## 0.21. SPEC funcional inicial: construtor de tabelas personalizadas configuraveis

Status consolidado: SPEC FUNCIONAL DOCUMENTAL CONSOLIDADA / BACKLOG TECNICO INCREMENTAL PLANEJADO

### Classificacao da frente

- Frente propria e separada da frequencia por competencia.
- Deve ser tratada como `Construtor de tabelas personalizadas configuraveis`.
- A liberdade de uso deve ser estrutural, mas controlada pelas regras do sistema.
- Nao deve partir de um caso de uso piloto fixo como eixo principal.
- Pode futuramente ter exemplos de uso, mas o MVP conceitual deve ser generico e controlado.
- Nao deve ser tratada como extensao da matriz de frequencia nem como ajuste pequeno do financeiro atual.
- Deve permanecer em trilha propria de especificacao, homologacao e futura implementacao incremental.

### Objetivo funcional

- Permitir que a usuaria crie qualquer controle interno por meio de tabelas configuraveis, reduzindo dependencia de planilhas externas sem transformar o sistema em planilha livre.
- Atender controles operacionais e gerenciais que hoje nao cabem bem em lancamentos, cadastros ou relatorios oficiais do financeiro.

### Escopo possivel do MVP

- cadastro de tabela personalizada com:
  - nome;
  - descricao;
  - status ativo/inativo ou arquivado;
  - ordem de exibicao, se fizer sentido no recorte.
- cadastro de colunas personalizadas com:
  - nome da coluna;
  - tipo de dado;
  - obrigatoria sim/nao;
  - ordem da coluna;
  - visivel sim/nao, se fizer sentido;
  - classificacao entre coluna comum e coluna calculada.
- tipos de dados iniciais:
  - texto curto;
  - texto longo;
  - numero inteiro;
  - numero decimal;
  - valor monetario;
  - percentual;
  - data;
  - mes/competencia;
  - sim/nao;
  - lista de opcoes;
  - formula controlada.
- linhas personalizadas com:
  - criacao manual;
  - edicao manual;
  - arquivamento ou exclusao logica;
  - validacao conforme o tipo de dado da coluna.
- formulas controladas por coluna:
  - aplicadas a coluna inteira, nao celula por celula no MVP;
  - restritas a colunas da mesma linha;
  - permitidas apenas por whitelist simples e segura.
- totalizadores definidos pelo sistema:
  - soma;
  - media;
  - minimo;
  - maximo;
  - contagem.
- exportacao XLSX como recorte preferencial do MVP.
- trilha de auditoria de estrutura, formulas e dados.
- separacao explicita entre dado de controle interno e financeiro oficial.

### Fora do MVP

- planilha livre estilo Excel;
- formula livre por texto arbitrario;
- formula celula por celula;
- automacoes, macros, scripts ou qualquer execucao dinamica;
- referencia circular;
- referencia livre entre tabelas;
- escrita automatica em lancamentos, saldos, relatorios ou cadastros oficiais do financeiro;
- importacao em massa;
- dashboards avancados;
- definicao definitiva de modelagem de banco antes do fechamento funcional desta SPEC.

### Tipos de coluna e diretriz de formula

- Tipos de coluna aceitaveis para o recorte inicial:
  - texto curto;
  - texto longo;
  - numero inteiro;
  - numero decimal;
  - valor monetario;
  - percentual;
  - data;
  - mes/competencia;
  - sim/nao;
  - lista de opcoes;
  - formula controlada.
- No MVP, formula deve ser atributo de coluna calculada e nao configuracao livre celula por celula.
- Formula deve ser estritamente controlada por whitelist e limitada a operacoes no contexto da propria linha.
- Formulas permitidas no desenho inicial:
  - operacoes aritmeticas simples (`+`, `-`, `*`, `/`);
  - parenteses;
  - funcoes seguras e fechadas, se realmente necessarias, como `ABS`, `ROUND`, `MIN` e `MAX`;
  - uso apenas de colunas da mesma linha;
  - totalizadores calculados pelo proprio sistema, sem expressao livre complexa do usuario final.
- Formulas proibidas:
  - qualquer avaliacao de Python, JavaScript, SQL ou codigo executavel;
  - referencias livres entre tabelas;
  - referencias circulares;
  - referencias que alterem outras linhas, outras colunas ou outros registros;
  - formulas com efeito colateral, chamada externa, importacao de arquivo, acesso a rede ou leitura/escrita no sistema;
  - referencia direta a saldos, calculos, balancetes, extratos, prestacao, fechamento ou lancamentos reais como dado editavel.

### Limites de seguranca

- Nao permitir que a frente vire um "Excel dentro do sistema".
- A liberdade deve existir na estrutura da tabela, nao na execucao irrestrita de formulas ou automacoes.
- Impor limites de quantidade de colunas, linhas por consulta, tipos suportados e complexidade de formula.
- Separar claramente configuracao da tabela, lancamento de linhas e administracao de permissoes.
- Qualquer vinculo futuro com entidades oficiais deve nascer como referencia controlada e nao como escrita automatica.
- A frente nao pode criar novo caminho para alterar calculos financeiros, saldos, relatorios oficiais ou lancamentos reais.

### Limites iniciais sugeridos

- ate 30 colunas por tabela;
- ate 5.000 linhas por tabela no MVP;
- ate 10 colunas calculadas por tabela;
- ate 20 opcoes em colunas do tipo lista;
- formulas apenas entre colunas da mesma linha;
- totalizadores apenas em rodape/listagem;
- sem importacao no primeiro recorte;
- sem integracao escrevente com o financeiro oficial.

### Premissas de permissoes

- Permissoes devem ser separadas por acao, no minimo:
  - visualizar tabelas;
  - criar/editar estrutura;
  - preencher/editar linhas;
  - alterar formulas;
  - exportar;
  - arquivar/restaurar;
  - administrar permissoes/configuracoes da tabela.
- Estrutura da tabela e formulas devem exigir permissao mais forte do que o simples preenchimento de linhas.
- Se existir vinculo futuro com entidades oficiais, ele deve exigir permissao dedicada e auditoria reforcada.

### Diretriz de auditoria e trilha de alteracoes

- Registrar criacao, edicao e arquivamento da tabela.
- Registrar criacao, edicao e remocao de colunas.
- Registrar alteracao de formulas.
- Registrar inclusao, edicao e exclusao logica de linhas com antes/depois quando aplicavel.
- Registrar usuario, data/hora, tabela afetada e acao de exportacao/backup/restauracao.
- Excluir fisicamente dados de controle deve ser excecao; preferir arquivamento ou exclusao logica quando o uso real justificar.

### Diretriz de exportacao e backup

- Cada tabela deve poder ser exportada ao menos em XLSX no recorte inicial preferencial.
- Deve existir estrategia futura de backup que preserve estrutura + dados + metadados essenciais da tabela.
- Restauracao, quando existir, deve ser tratada como operacao administrativa auditada.
- Exportacao nao pode ser tratada como integracao oficial com o financeiro; e apenas saida documental/operacional.

### Relacao com o financeiro oficial

- Quando deve ficar separado:
  - controles internos, provisoes, acompanhamentos operacionais, metas, medidores e listas auxiliares que nao representam por si so lancamento financeiro oficial;
  - qualquer dado ainda em preparo, conferencia ou organizacao interna.
- Quando pode futuramente vincular entidades:
  - pessoa, conta, categoria ou lancamento podem entrar apenas como referencia opcional e controlada;
  - primeiro recorte seguro e leitura/relacionamento, nao escrita;
  - eventual integracao futura deve nascer por microetapa propria e com regra explicita de permissao/auditoria.
- O que nao pode alterar:
  - calculo financeiro;
  - saldos;
  - extrato;
  - resumo;
  - prestacao/fechamento;
  - balancete;
  - lancamentos reais;
  - regras de transferencia, rateio ou competencias ja consolidadas.

### Regra de separacao com o financeiro oficial

- As tabelas personalizadas sao controles internos.
- Nao geram lancamento financeiro.
- Nao alteram saldo.
- Nao alteram extrato.
- Nao alteram resumo.
- Nao alteram prestacao/fechamento.
- Nao alteram balancete.
- Nao alteram regras de transferencia, rateio ou competencia.
- Eventual vinculo futuro com pessoa, conta, categoria ou lancamento deve ser somente leitura no primeiro recorte e exigir microetapa propria.

### Riscos principais

- risco de escopo crescer ate virar "Excel dentro do sistema";
- risco de a flexibilidade estrutural ser confundida com liberdade irrestrita de planilha;
- risco de proliferacao de tabelas sem governanca;
- risco de formulas ambiguas ou dificeis de auditar;
- risco de confusao entre controle interno e dado financeiro oficial;
- risco de permissao excessiva para quem so deveria preencher linhas;
- risco de exportacao/backup insuficiente para uma frente que tende a concentrar dado operacional importante;
- risco de futura integracao com financeiro criar expectativa de escrita automatica indevida.

### Classificacao de pendencias desta frente

- Implementar agora:
  - nenhuma; esta microetapa e apenas de auditoria documental e SPEC funcional inicial.
- Pendencia proxima:
  - fechar os detalhes do construtor generico controlado sem rebaixar a governanca da frente;
  - validar se os limites iniciais sugeridos permanecem adequados para o primeiro recorte funcional;
  - definir o contrato inicial de exportacao XLSX e a forma de exibicao/edicao das colunas calculadas.
- Backlog/futuro:
  - referencias opcionais a entidades oficiais;
  - exemplos/templates de tabela;
  - importacao assistida;
  - filtros/visoes salvas;
  - formulas controladas mais ricas, se o uso real justificar.
- Fora de escopo:
  - modelagem definitiva de banco nesta etapa;
  - implementacao funcional agora;
  - qualquer impacto em Python, templates, JS/CSS, migrations, banco ou financeiro oficial;
  - transformacao da frente em engine generica de planilha.
- Risco a monitorar:
  - escopo expandir por conveniencia e perder governanca;
  - mistura entre controle interno e fonte oficial financeira;
  - permissao, auditoria e backup ficarem atras da flexibilidade entregue.

### SPEC operacional documental do uso futuro

#### Fluxo operacional de criacao de tabela

- A usuaria inicia por `Criar nova tabela`.
- O sistema solicita:
  - nome da tabela;
  - descricao;
  - status inicial (`ativa`, `inativa` ou `arquivada`, conforme o recorte aprovado);
  - ordem de exibicao, se esse campo entrar no primeiro recorte.
- Ao salvar a estrutura inicial:
  - a tabela pode nascer sem linhas;
  - a tabela deve nascer com estrutura editavel;
  - a tela seguinte deve conduzir naturalmente para o cadastro das colunas.

#### Fluxo operacional de criacao de colunas

- A partir da tabela criada, a usuaria usa `Adicionar coluna`.
- Para cada coluna, o sistema deve pedir:
  - nome da coluna;
  - tipo de dado;
  - obrigatoria sim/nao;
  - ordem de exibicao;
  - visivel sim/nao;
  - coluna comum ou coluna calculada.
- Ao salvar uma coluna:
  - o sistema valida o contrato minimo do tipo;
  - colunas comuns ficam prontas para preenchimento manual nas linhas;
  - colunas calculadas exigem definicao da formula guiada antes de entrarem em uso real.

#### Tipos de dados e comportamento esperado

- `texto curto`:
  - campo de texto simples;
  - pensado para identificadores, rotulos e descricoes curtas.
- `texto longo`:
  - campo de texto expandido;
  - pensado para observacoes e conteudo descritivo.
- `numero inteiro`:
  - aceita apenas numeros sem casas decimais.
- `numero decimal`:
  - aceita casas decimais conforme padrao do sistema ou configuracao futura controlada.
- `valor monetario`:
  - usa formato monetario;
  - deve preservar leitura numerica consistente para totalizadores e formulas permitidas.
- `percentual`:
  - usa formato percentual;
  - continua sendo dado numerico validado pelo sistema.
- `data`:
  - aceita apenas datas validas.
- `mes/competencia`:
  - representa competencia mensal em formato controlado de mes/ano.
- `sim/nao`:
  - comportamento booleano.
- `lista de opcoes`:
  - valor obrigatoriamente escolhido dentro das opcoes cadastradas para a coluna.
- `formula controlada`:
  - valor nao digitado manualmente;
  - resultado calculado pelo sistema a partir de colunas da mesma linha.

#### Regras de validacao por tipo

- `texto curto`:
  - deve ter limite de caracteres menor e objetivo;
  - no recorte inicial, a SPEC pode considerar um teto curto e padronizado.
- `texto longo`:
  - deve ter limite superior maior do que o texto curto, ainda com teto controlado.
- `numero inteiro`:
  - nao aceita casas decimais;
  - nao aceita texto mascarado fora do formato numerico esperado.
- `numero decimal`:
  - aceita casas decimais;
  - deve obedecer quantidade padrao ou configuracao futura controlada, sem liberdade irrestrita.
- `valor monetario`:
  - deve validar numero monetario e exibir formatacao monetaria coerente.
- `percentual`:
  - deve validar numero percentual e exibir formatacao percentual coerente.
- `data`:
  - deve bloquear data invalida.
- `mes/competencia`:
  - deve aceitar apenas formato controlado de mes/ano.
- `sim/nao`:
  - deve persistir comportamento booleano claro, sem variantes textuais livres.
- `lista de opcoes`:
  - deve bloquear qualquer valor fora das opcoes configuradas.
- `formula controlada`:
  - deve ser sempre calculada pelo sistema;
  - nao deve permitir digitacao direta da celula.

#### Fluxo operacional de formulas por coluna

- Formula e atributo de uma coluna calculada.
- A formula vale para a coluna inteira.
- No MVP, a formula nao e editavel celula por celula.
- A formula usa apenas colunas da mesma linha.
- Operacoes permitidas:
  - soma;
  - subtracao;
  - multiplicacao;
  - divisao;
  - parenteses;
  - `ABS`;
  - `ROUND`;
  - `MIN`;
  - `MAX`.
- A formula deve ser criada por construtor guiado, e nao por codigo livre.
- Deve ficar explicitamente proibido:
  - Python;
  - JavaScript;
  - SQL;
  - macros;
  - scripts;
  - referencia circular;
  - referencia livre entre tabelas.

#### UX sugerida para formulas

- A usuaria escolhe a coluna calculada.
- Depois escolhe as colunas de origem elegiveis.
- Em seguida escolhe operadores e funcoes permitidas no construtor guiado.
- O sistema exibe uma previa textual legivel da formula antes do salvamento.
- Antes de salvar, o sistema valida:
  - sintaxe do construtor;
  - compatibilidade entre tipos;
  - ausencia de referencia circular;
  - aderencia as operacoes permitidas.
- Se uma coluna usada por formula for alterada ou removida:
  - o sistema deve bloquear a mudanca;
  - ou exigir revisao explicita da formula antes de concluir a alteracao estrutural.

#### Fluxo operacional de linhas

- A usuaria usa `Adicionar linha`.
- O sistema exibe apenas campos editaveis correspondentes as colunas comuns.
- Cada celula deve respeitar o tipo de dado da coluna.
- Ao salvar a linha:
  - o sistema valida obrigatoriedade;
  - valida formato e tipo;
  - calcula automaticamente as colunas calculadas.
- Em `Editar linha`:
  - a usuaria altera apenas colunas editaveis;
  - colunas calculadas aparecem como resultado, sem edicao direta.
- Em `Arquivar` ou `Excluir logicamente linha`:
  - a linha deixa de compor o uso operacional normal;
  - o historico deve permanecer auditavel.

#### Totalizadores

- Totalizadores aceitos no recorte inicial:
  - soma;
  - media;
  - minimo;
  - maximo;
  - contagem.
- Totalizadores devem aparecer em rodape ou listagem consolidada.
- Totalizadores devem ser definidos pelo sistema, nao por formula livre do usuario.
- Totalizadores devem respeitar o tipo de dado aplicavel de cada coluna.

#### Exportacao XLSX

- A exportacao deve permitir `Exportar tabela visivel`.
- O arquivo deve incluir:
  - cabecalhos das colunas;
  - dados das linhas visiveis conforme o recorte aprovado;
  - formatacao basica coerente com o tipo de dado.
- Decisao operacional sugerida para o MVP:
  - incluir totalizadores no XLSX quando eles estiverem presentes na listagem/rodape da tabela;
  - manter essa inclusao como comportamento padrao do documento exportado, e nao como integracao com o financeiro.
- A exportacao deve ser registrada na auditoria.
- A exportacao nao deve ser tratada como integracao oficial com o financeiro.

#### Auditoria operacional

- Auditar:
  - criacao, edicao e arquivamento de tabela;
  - criacao, edicao e remocao de coluna;
  - alteracao de tipo de dado;
  - alteracao de formula;
  - inclusao, edicao e exclusao logica de linha;
  - exportacao XLSX.
- Cada evento deve registrar, quando aplicavel:
  - usuario;
  - data/hora;
  - acao;
  - antes/depois.

#### Permissoes operacionais

- Permissoes minimas sugeridas:
  - visualizar tabela;
  - criar tabela;
  - editar estrutura;
  - preencher linhas;
  - editar linhas;
  - alterar formulas;
  - exportar;
  - arquivar/restaurar tabela;
  - administrar configuracoes/permissoes.
- Estrutura e formulas devem exigir permissao mais forte do que preenchimento simples de linhas.

#### Regras de seguranca operacionais

- Nao alterar financeiro oficial.
- Nao gerar lancamento.
- Nao alterar saldos.
- Nao alterar extrato.
- Nao alterar resumo.
- Nao alterar prestacao/fechamento.
- Nao alterar balancete.
- Nao alterar regras de transferencia, rateio ou competencia.
- Vinculos futuros com pessoa, conta, categoria ou lancamento devem nascer como leitura no primeiro recorte, nunca como escrita automatica.

#### Classificacao de pendencias desta SPEC operacional

- Implementar agora:
  - nenhuma; esta etapa continua exclusivamente documental.
- Pendencia proxima:
  - fechar a UX do construtor guiado de formulas;
  - fechar limites concretos de caracteres e precisao por tipo;
  - decidir o comportamento final de totalizadores no XLSX;
  - decidir a experiencia de bloqueio/revisao quando coluna usada em formula for alterada.
- Backlog/futuro:
  - importacao assistida;
  - exemplos/templates de tabela;
  - referencias opcionais de leitura a entidades oficiais;
  - filtros e visoes salvas;
  - formulas controladas mais ricas, se o uso real justificar.
- Fora de escopo:
  - implementacao funcional nesta microetapa;
  - modelagem definitiva de banco;
  - planilha livre estilo Excel;
  - formula celula por celula;
  - macros, scripts e execucao de codigo;
  - integracao escrevente com financeiro;
  - geracao automatica de lancamentos financeiros.
- Risco a monitorar:
  - escopo crescer para automacao excessiva;
  - perda de governanca sobre formulas e auditoria;
  - confusao entre controle interno e dado financeiro oficial.

### SPEC de UX operacional documental

#### Tela de listagem de tabelas personalizadas

- A frente deve ter uma tela propria de listagem, separada do financeiro operacional e sem mistura com lancamentos.
- A listagem deve mostrar, no minimo:
  - nome;
  - descricao curta;
  - status;
  - quantidade de colunas;
  - quantidade de linhas;
  - ultima atualizacao.
- Acoes previstas na listagem:
  - abrir;
  - editar estrutura;
  - arquivar/restaurar;
  - exportar;
  - criar nova tabela.
- A leitura visual deve reforcar que se trata de controles internos configuraveis, nao de documentos financeiros.

#### Fluxo de criacao e edicao da tabela

- O formulario de criacao/edicao deve expor:
  - nome;
  - descricao;
  - status;
  - ordem de exibicao, se esse campo for mantido no recorte.
- Depois de salvar uma tabela nova:
  - o sistema deve conduzir para a configuracao das colunas;
  - a tabela pode existir sem nenhuma linha inicialmente;
  - nao deve existir vinculo obrigatorio com financeiro.
- Em edicao:
  - a usuaria deve conseguir revisar os metadados da tabela sem ser forcada a alterar linhas.

#### Tela de configuracao de colunas

- A tela de colunas deve exibir uma lista ordenavel.
- Deve permitir:
  - adicionar coluna;
  - editar coluna;
  - ocultar/arquivar coluna;
  - reordenar colunas.
- Cada item da lista deve mostrar:
  - nome da coluna;
  - tipo de dado;
  - obrigatoriedade;
  - visibilidade;
  - se e coluna calculada.
- O sistema deve impedir remocao insegura de coluna usada em formula sem revisao previa da dependencia.

#### UX de criacao e edicao de coluna

- O formulario da coluna deve expor:
  - nome da coluna;
  - tipo de dado;
  - obrigatoria sim/nao;
  - visivel sim/nao;
  - ordem;
  - coluna comum ou calculada.
- Para `lista de opcoes`:
  - a UX deve permitir cadastrar e revisar as opcoes permitidas da coluna.
- Para `coluna calculada`:
  - o fluxo deve abrir, ou exigir antes do fechamento, o construtor guiado de formula.

#### Limites concretos por tipo de dado

- `texto curto`:
  - limite inicial sugerido: 120 caracteres.
- `texto longo`:
  - limite inicial sugerido: 2000 caracteres.
- `numero inteiro`:
  - validar inteiro, sem casas decimais.
- `numero decimal`:
  - precisao padrao sugerida: ate 4 casas decimais.
- `valor monetario`:
  - precisao padrao sugerida: 2 casas decimais.
- `percentual`:
  - formato percentual com precisao padrao sugerida de 2 casas decimais.
- `data`:
  - formato de data do sistema.
- `mes/competencia`:
  - formato `MM/AAAA`.
- `sim/nao`:
  - valor booleano.
- `lista de opcoes`:
  - ate 20 opcoes no MVP.
- `formula controlada`:
  - valor sempre calculado pelo sistema.

#### UX do construtor guiado de formulas

- Nao permitir campo livre estilo Excel.
- A experiencia deve ser guiada.
- O fluxo deve permitir:
  - escolher colunas de origem elegiveis;
  - escolher operadores permitidos;
  - escolher funcoes permitidas, quando aplicavel;
  - visualizar previa textual legivel da formula.
- Antes de salvar, o sistema deve validar:
  - consistencia da formula;
  - compatibilidade de tipos;
  - ausencia de referencia circular;
  - ausencia de referencia entre tabelas;
  - ausencia de uso de coluna incompatível com calculo.
- A formula continua aplicada a coluna inteira, nunca celula por celula no MVP.

#### Comportamento quando coluna usada em formula for alterada ou removida

- Se alterar apenas o nome da coluna:
  - a formula pode permanecer valida;
  - o rotulo exibido na previa e na leitura deve ser atualizado.
- Se alterar o tipo:
  - o sistema deve bloquear quando a mudanca quebrar a formula;
  - ou exigir revisao explicita antes de concluir.
- Se ocultar a coluna:
  - o sistema deve permitir apenas se isso nao quebrar a leitura esperada;
  - caso exista dependencia relevante, deve sinalizar essa dependencia.
- Se arquivar/remover a coluna:
  - o sistema deve bloquear quando houver formula dependente;
  - a remocao so pode seguir apos revisao ou remocao previa da formula.
- A decisao tomada deve ser auditada.

#### Tela de preenchimento de linhas

- O preenchimento deve ocorrer em formato tabular.
- A tela deve permitir:
  - adicionar linha;
  - editar linha;
  - arquivar/excluir logicamente linha.
- Cada campo deve respeitar o tipo da coluna.
- Colunas calculadas devem aparecer como somente leitura.
- Totalizadores devem aparecer em rodape ou area equivalente da listagem.
- Filtros simples podem ficar para backlog, se nao couberem no MVP.

#### Totalizadores

- Totalizadores aceitos:
  - soma;
  - media;
  - minimo;
  - maximo;
  - contagem.
- Tipos que aceitam totalizador no recorte inicial:
  - `numero inteiro`;
  - `numero decimal`;
  - `valor monetario`;
  - `percentual` com cautela de leitura;
  - `data` apenas para `minimo` e `maximo`, se isso entrar no recorte;
  - `sim/nao` e `lista de opcoes` podem usar `contagem` apenas se o uso real justificar.
- Direcao sugerida para o MVP:
  - totalizador configurado por coluna, nao automatico apenas por tipo;
  - a interface deve deixar claro se a coluna participa ou nao do rodape de totalizacao.
- Na tela:
  - totalizadores devem aparecer em rodape/listagem, alinhados com a coluna correspondente.
- No XLSX:
  - totalizadores visiveis na tela devem sair tambem no rodape exportado.

#### Exportacao XLSX na UX

- A exportacao deve exportar a tabela visivel.
- O arquivo deve incluir:
  - cabecalhos;
  - linhas visiveis;
  - formatacao basica por tipo;
  - colunas calculadas com o valor ja calculado;
  - totalizadores quando estiverem visiveis na tela.
- O evento de exportacao deve ir para a auditoria.
- A exportacao nao deve ser tratada como integracao financeira.

#### Auditoria de UX

- Registrar:
  - criacao, edicao e arquivamento de tabela;
  - criacao, edicao, remocao, ocultacao e reordenacao de coluna;
  - alteracao de formula;
  - inclusao, edicao e exclusao logica de linha;
  - exportacao.
- Registrar, quando aplicavel:
  - usuario;
  - data/hora;
  - acao;
  - antes/depois.

#### Permissoes na UX

- Permissoes operacionais da experiencia:
  - visualizar tabela;
  - criar tabela;
  - editar estrutura;
  - configurar formula;
  - preencher linha;
  - editar linha;
  - arquivar/restaurar;
  - exportar;
  - administrar tabela/configuracoes.
- A UX deve diferenciar com clareza:
  - quem pode apenas preencher linhas;
  - quem pode alterar estrutura;
  - quem pode alterar formulas.

#### Seguranca e limites na UX

- A UX deve evitar aparencia de planilha livre estilo Excel.
- A liberdade deve ser de estrutura controlada, nao de formula livre.
- Nao permitir:
  - formula livre;
  - macro;
  - script;
  - codigo executavel.
- Nao permitir escrita no financeiro.
- Nao gerar lancamento.
- Nao alterar saldo, extrato, resumo, prestacao/fechamento ou balancete.

### SPEC de navegacao e enquadramento documental

#### Enquadramento estrategico da frente

- A frente deve ficar isolada do financeiro oficial.
- No MVP, pode nascer dentro do modulo `financeiro` como area de `Controles internos`.
- Nao deve se misturar com:
  - lancamentos;
  - relatorios financeiros;
  - extrato;
  - resumo;
  - prestacao/fechamento;
  - balancete.
- Nao deve gerar documentos financeiros oficiais.
- Nao deve gerar lancamento.
- Nao deve alterar saldo.

#### Localizacao sugerida para o MVP

- Menu do financeiro:
  - grupo: `Controles internos`
  - item: `Tabelas personalizadas`
- Nome funcional da tela:
  - `Tabelas personalizadas`
- Descricao operacional sugerida:
  - area para criar controles internos configuraveis, sem efeito sobre lancamentos financeiros oficiais.

#### Alternativas futuras de posicionamento

- Manter como area interna do `financeiro`, se o uso continuar essencialmente gerencial/financeiro.
- Evoluir futuramente para modulo proprio `Controles internos`, se a frente passar a atender controles gerais da Casa fora do escopo financeiro.

#### Regra de separacao na navegacao

- Nao entrar em `Lançamentos`.
- Nao entrar como relatorio financeiro.
- Nao aparecer como parte de `Extrato`.
- Nao aparecer como parte de `Resumo`.
- Nao aparecer como parte de `Prestacao/Fechamento`.
- Nao aparecer como parte de `Balancete`.
- Nao gerar documentos financeiros oficiais.
- Nao gerar lancamento.
- Nao alterar saldo.

#### Fluxo de navegacao do MVP

- Caminho principal:
  - `Financeiro > Controles internos > Tabelas personalizadas`
- Ao abrir:
  - o sistema mostra a listagem de tabelas personalizadas.
- Na listagem, a usuaria pode:
  - abrir tabela;
  - criar nova tabela;
  - editar estrutura;
  - exportar;
  - arquivar/restaurar, se tiver permissao.
- Ao criar nova tabela:
  - salva os metadados;
  - conduz para configuracao de colunas.
- Depois de configurar colunas:
  - conduz para o preenchimento de linhas.
- Na tela de linhas:
  - deve existir caminho claro para voltar a estrutura;
  - deve existir caminho claro para voltar a listagem;
  - deve existir caminho claro para exportar.
- Colunas calculadas devem aparecer como resultado somente leitura na tela de linhas.

#### Filtros simples sugeridos para o MVP

- Na listagem de tabelas:
  - busca por nome;
  - filtro por status;
  - ordenacao simples por nome ou ultima atualizacao.
- Na tela de linhas:
  - busca textual simples, se tecnicamente segura no MVP;
  - filtro por status da linha, se houver arquivamento/exclusao logica.
- Filtros avancados ficam fora do MVP.

#### Decisoes finais consolidadas do primeiro recorte operacional

- `data`:
  - no MVP, permitir `minimo` e `maximo`;
  - somente quando o totalizador for configurado explicitamente na coluna;
  - nao aplicar automaticamente em toda coluna de data.
- `sim/nao` e `lista de opcoes`:
  - no MVP, permitir apenas `contagem simples total`;
  - nao implementar agrupamento por opcao no primeiro recorte;
  - agrupamentos por opcao ficam para backlog/futuro.
- Busca textual simples na tela de linhas:
  - entra no MVP como busca simples sobre os valores visiveis/editaveis da tabela;
  - filtros avancados, visoes salvas, busca por tipo especifico e filtros compostos ficam para backlog/futuro.
- Reordenacao de colunas:
  - no MVP, usar campo numerico `ordem`;
  - `arrastar-e-soltar` fica para futuro;
  - a ordenacao deve afetar a exibicao na tela e no XLSX.
- Totalizadores:
  - aparecem somente quando configurados por coluna;
  - se visiveis na tela, devem ser incluidos no rodape do XLSX;
  - nao sao formulas livres e continuam controlados pelo sistema.

#### Permissoes afetadas pela navegacao

- visualizar tabelas personalizadas;
- criar tabela personalizada;
- editar estrutura;
- configurar formula;
- preencher linhas;
- editar linhas;
- exportar;
- arquivar/restaurar;
- administrar configuracoes.
- A visibilidade do item de menu deve depender da permissao de visualizar tabelas personalizadas.

#### Classificacao de pendencias desta SPEC de UX

- Implementar agora:
  - nenhuma; a etapa continua apenas documental.
- Pendencia proxima:
  - nenhuma decisao de escopo funcional pendente para fechar o primeiro recorte operacional documental;
  - proxima pendencia e abrir microetapa propria para traducao desta SPEC em backlog tecnico incremental (sem modelagem definitiva nesta fase).
- Backlog/futuro:
  - agrupamentos por opcao em colunas `sim/nao` e `lista de opcoes`;
  - filtros avancados, busca por tipo especifico e filtros compostos;
  - `arrastar-e-soltar` para reordenacao de colunas;
  - visoes salvas;
  - exemplos/templates de tabela;
  - importacao assistida;
  - refinamentos visuais adicionais da grade.
- Fora de escopo:
  - implementacao funcional nesta etapa;
  - modelagem definitiva de banco;
  - planilha livre estilo Excel;
  - formula celula por celula;
  - integracao escrevente com financeiro;
  - geracao automatica de lancamentos.
- Risco a monitorar:
  - a UX ficar complexa demais e incentivar uso como planilha livre;
  - a experiencia de formulas guiadas ficar confusa para usuaria nao tecnica;
  - a distincao entre preencher linhas e alterar estrutura/permissoes ficar fraca.
  - a frente nascer visualmente perto demais de relatorios ou lancamentos e confundir seu papel.

### Backlog tecnico incremental do MVP

#### Guardrails transversais do backlog

- A primeira microetapa tecnica futura deve ser auditoria tecnica preparatoria, e nao implementacao.
- A modelagem de dados deve vir em SPEC tecnica propria antes de qualquer `model` ou `migration`.
- Qualquer alteracao em banco real exige cuidado, backup e autorizacao explicita.
- Arquivos SQLite nao devem ser versionados.
- A frente continua sem integracao escrevente com o financeiro oficial.
- Enquanto este backlog estiver apenas documental:
  - nao criar `model`;
  - nao criar `migration`;
  - nao alterar Python;
  - nao alterar templates;
  - nao alterar JS/CSS;
  - nao alterar banco.

#### Microetapa 1 - auditoria tecnica preparatoria da base atual

- Objetivo:
  - mapear por onde a frente entraria com seguranca no codigo atual.
- Escopo:
  - auditar menu/topbar do financeiro;
  - auditar padrao atual de permissoes;
  - auditar trilha de auditoria existente;
  - auditar padroes atuais de exportacao XLSX;
  - auditar padroes de views, templates e listagens reutilizaveis;
  - registrar achados e riscos sem alterar comportamento.
- Arquivos provaveis a consultar:
  - `financeiro/base.html`;
  - `configuracoes/permissoes.py`;
  - `docs/MATRIZ_PERMISSOES.md`;
  - views/templates/listagens do `financeiro`;
  - pontos atuais de exportacao XLSX e auditoria do modulo.
- Risco:
  - mapear de forma incompleta e abrir implementacao em superficie errada.
- Envolve model/migration/banco:
  - nao.
- Validacoes esperadas:
  - confirmacao documental de pontos de entrada, permissoes e padroes reaproveitaveis;
  - ausencia total de diff funcional.
- Dependencias anteriores:
  - SPEC funcional, operacional, UX e navegacao ja fechadas.
- Fora de escopo:
  - implementacao;
  - proposta definitiva de banco;
  - criacao de permissao ou menu real.

##### Resultado da auditoria tecnica preparatoria

- Navegacao/menu/topbar do financeiro:
  - o shell atual da navegacao fica em `financeiro/templates/financeiro/base.html`
  - o menu atual e organizado em grupos `Visao geral`, `Movimentacao`, `Relatorios`, `Cadastros` e `Institucional`
  - a exibicao dos itens usa `tem_permissao` e `tem_alguma_permissao` com codigos funcionais do financeiro
  - o ponto futuro mais seguro para esta frente e nascer como novo grupo `Controles internos` dentro do menu do financeiro, com item `Tabelas personalizadas`, sem entrar em `Lancamentos` nem em relatorios oficiais
- Permissoes:
  - a base atual fica em `configuracoes.models` com `PermissaoSistema`, `PerfilAcesso`, `PerfilPermissaoSistema` e `UsuarioPerfilAcesso`
  - o enforcement backend reutilizavel ja existe em `configuracoes.permissoes.PermissaoSistemaMixin` e no adaptador do modulo `financeiro.permissoes.FinanceiroPermissaoMixin`
  - o padrao de template tag ja existe em `financeiro/templatetags/financeiro_permissoes.py`
  - seeds e evolucoes documentais/executaveis de permissao ja existem em `configuracoes/migrations`, com base inicial em `0004_seed_perfis_permissoes_v1.py`
  - padrao futuro documental recomendado para a frente:
    - `financeiro.tabelas_personalizadas.visualizar`
    - `financeiro.tabelas_personalizadas.criar`
    - `financeiro.tabelas_personalizadas.editar_estrutura`
    - `financeiro.tabelas_personalizadas.configurar_formula`
    - `financeiro.tabelas_personalizadas.preencher_linhas`
    - `financeiro.tabelas_personalizadas.editar_linhas`
    - `financeiro.tabelas_personalizadas.exportar`
    - `financeiro.tabelas_personalizadas.arquivar_restaurar`
    - `financeiro.tabelas_personalizadas.administrar_configuracoes`
- Auditoria:
  - ja existe trilha atual em `financeiro.models.AuditoriaFinanceiro`
  - o modelo atual registra `acao`, `modelo`, `registro_id`, `data_hora`, `usuario` e `campos_alterados` em `JSONField`
  - o modulo ja possui helpers de snapshot, normalizacao e diff em `financeiro/views.py`, incluindo `_build_auditoria_payload` e registradores por entidade
  - existe listagem propria de auditoria em `financeiro:auditoria-lancamento-list` com filtros e exibicao de before/after
  - a futura frente deve reaproveitar este padrao, mas exigira complemento de escopo e nomenclatura para auditar tabela, coluna, formula, linha e exportacao sem ficar limitada ao vocabulario de lancamentos
- Exportacao XLSX:
  - o financeiro ja possui fluxo de exportacao por views dedicadas com filtros `GET`, `HttpResponse` de download e `Content-Disposition` por arquivo
  - a geracao XLSX atual usa helpers proprios em `financeiro/views.py`, com montagem XML compactada, sem dependencia aparente de biblioteca externa tipo `openpyxl`
  - os cadastros auxiliares ja seguem padrao reutilizavel de exportacao com cabecalhos, ordenacao previsivel e reaproveitamento dos filtros da listagem
  - a futura frente pode reaproveitar esse contrato tecnico, desde que a exportacao continue tratada como download documental e nunca como integracao com o financeiro oficial
- Views/listagens/forms/templates:
  - o padrao dominante de listagem no financeiro usa `ListView` com filtros simples por `GET`, botao `Exportar`, acao primaria de criacao e acoes por linha condicionadas por permissao
  - o padrao de formulario reutilizavel esta em `FinanceiroFormMixin`, com mensagens de sucesso, `return_to`, opcao de salvar e permanecer e templates dedicados por recurso
  - o padrao de exclusao reutilizavel esta em `FinanceiroDeleteMixin`, com confirmacao explicita e retorno controlado
  - templates proximos do futuro uso sao `conta_list.html`, `pessoa_list.html`, `categoria_list.html` e `centro_custo_list.html`, porque ja mostram filtros simples, estado vazio, acoes por linha e leitura de cadastro sem mistura com relatorios
- Organizacao tecnica futura:
  - a frente deve permanecer dentro do app `financeiro`, porque compartilha governanca, permissoes, auditoria e localizacao de menu
  - ao mesmo tempo, nao deve entrar no miolo de `LancamentoFinanceiro`; a recomendacao documental e abrir arquivos e rotas proprios da frente dentro do app, com views/templates/forms separados dos fluxos de lancamentos e relatorios oficiais
- Riscos tecnicos mapeados:
  - misturar a frente com `Lancamentos` e contaminar a percepcao de dado oficial
  - expor menu ou tela sem separar bem permissao de estrutura, formula e preenchimento
  - reaproveitar auditoria de forma insuficiente e perder trilha de mudancas estruturais
  - fazer a exportacao parecer integracao escrevente com o financeiro
  - escolher modelagem dinamica ampla demais na proxima SPEC tecnica
  - herdar UX tabular que aproxime a frente de uma planilha livre estilo Excel
- Baixa desta microetapa:
  - auditoria tecnica preparatoria concluida sem implementacao funcional
  - proxima microetapa recomendada: SPEC tecnica de modelagem de dados, ainda sem `model` e sem `migration`

#### Microetapa 2 - SPEC tecnica de modelagem de dados

- Objetivo:
  - propor modelos candidatos e relacoes do MVP antes de qualquer `migration`.
- Escopo:
  - avaliar entidades candidatas de tabela, coluna, linha, valor, formula, totalizador, auditoria e permissoes;
  - avaliar riscos de EAV, JSON e dados tipados;
  - comparar alternativas e registrar recorte recomendado do MVP.
- Arquivos provaveis a consultar:
  - `financeiro/models.py`;
  - modelos existentes de auditoria/permissao;
  - documentos oficiais desta frente.
- Risco:
  - antecipar modelagem definitiva sem auditoria tecnica suficiente;
  - escolher estrutura flexivel demais e aproximar a frente de uma planilha livre.
- Envolve model/migration/banco:
  - nao.
- Validacoes esperadas:
  - SPEC tecnica aprovada documentalmente;
  - lista clara do que fica para depois da primeira modelagem.
- Dependencias anteriores:
  - microetapa 1 concluida.
- Fora de escopo:
  - `model`;
  - `migration`;
  - alteracao de banco real.

##### Resultado da SPEC tecnica de modelagem de dados

###### Premissa central da modelagem

- A modelagem desta frente deve continuar separada do dominio de `LancamentoFinanceiro`.
- A frente deve nascer dentro do app `financeiro`, mas com entidades proprias de controles internos configuraveis.
- Esta SPEC ainda nao autoriza `model`, `migration` nem alteracao de banco.
- A modelagem recomendada ainda precisa de aprovacao explicita antes de virar implementacao estrutural.

###### Entidades candidatas do MVP

- `TabelaPersonalizada`
  - responsabilidade:
    - representar o controle interno configuravel como unidade principal.
  - campos provaveis:
    - `nome`
    - `descricao`
    - `status`
    - `ordem`
    - `criado_por`
    - `atualizado_por`
    - `criado_em`
    - `atualizado_em`
  - relacionamentos provaveis:
    - 1 tabela possui N colunas
    - 1 tabela possui N linhas
  - regras de validacao:
    - nome obrigatorio
    - nome unico por escopo funcional do modulo, ou ao menos bloqueio de duplicidade ativa equivalente
    - status limitado a ativo/inativo/arquivado
  - riscos:
    - tabela virar container generico demais sem governanca
    - metadado misturar regra estrutural e regra operacional
  - fora do MVP:
    - versionamento completo de layout
    - ownership granular por tabela
    - vinculos obrigatorios com entidades do financeiro oficial
- `ColunaPersonalizada`
  - responsabilidade:
    - definir estrutura, tipo, visibilidade e comportamento de cada coluna da tabela.
  - campos provaveis:
    - `tabela`
    - `nome`
    - `tipo_dado`
    - `obrigatoria`
    - `visivel`
    - `ordem`
    - `calculada`
    - `configuracao_json`
    - `status`
  - relacionamentos provaveis:
    - N colunas pertencem a 1 tabela
    - 1 coluna pode ter 0 ou 1 formula ativa no recorte inicial
    - 1 coluna pode ter 0 ou 1 totalizador configurado no recorte inicial
  - regras de validacao:
    - nome obrigatorio dentro da tabela
    - `tipo_dado` por whitelist fechada
    - coluna calculada nao pode ser editavel na entrada de linhas
    - `configuracao_json` usada apenas para dados controlados como opcoes, precisao e metadados do tipo
  - riscos:
    - JSON de configuracao virar escape para regra livre
    - alteracao de tipo quebrar dados ja preenchidos
  - fora do MVP:
    - formulas por celula
    - dependencia entre tabelas
    - tipos arbitrarios criados pelo usuario
- `LinhaTabelaPersonalizada`
  - responsabilidade:
    - representar cada registro operacional preenchido pela usuaria.
  - campos provaveis:
    - `tabela`
    - `status`
    - `ordem` ou `criado_em` como referencia de ordenacao inicial
    - `criado_por`
    - `atualizado_por`
    - `criado_em`
    - `atualizado_em`
  - relacionamentos provaveis:
    - N linhas pertencem a 1 tabela
    - 1 linha possui N valores de celula
  - regras de validacao:
    - linha pertence sempre a uma unica tabela
    - arquivamento/exclusao deve ser logico no MVP
  - riscos:
    - ordenar por posicao rigida demais e gerar custo de manutencao
    - exclusao fisica perder trilha
  - fora do MVP:
    - workflow/aprovacao de linhas
    - historico de versoes por linha
- `ValorTabelaPersonalizada`
  - responsabilidade:
    - persistir o valor efetivo de cada cruzamento linha x coluna no modelo estrutural do MVP.
  - campos provaveis:
    - `linha`
    - `coluna`
    - `valor_texto`
    - `valor_numero`
    - `valor_data`
    - `valor_booleano`
    - `valor_json`
    - `valor_calculado`
    - `atualizado_em`
  - relacionamentos provaveis:
    - 1 valor pertence a 1 linha e 1 coluna
    - unicidade logica por par `linha + coluna`
  - regras de validacao:
    - somente um slot principal de valor manual deve estar preenchido conforme o tipo da coluna
    - coluna calculada grava apenas resultado calculado e permanece somente leitura na entrada
    - `valor_json` reservado para tipos controlados como lista de opcoes ou payload estruturado de baixo risco
  - riscos:
    - proliferacao de registros por celula
    - ambiguidade se mais de um campo tipado ficar preenchido
  - fora do MVP:
    - historico por celula
    - anexos/binarios
    - engine de formula por valor livre
- `FormulaColunaPersonalizada`
  - responsabilidade:
    - registrar a definicao normalizada da formula guiada aplicada a uma coluna calculada.
  - campos provaveis:
    - `coluna`
    - `expressao_normalizada` ou `estrutura_json_guiada`
    - `versao`
    - `ativa`
    - `validada_em`
  - relacionamentos provaveis:
    - 1 coluna calculada pode ter historico simples de versoes
  - regras de validacao:
    - formula apenas para coluna marcada como calculada
    - formula so referencia colunas da mesma tabela e da mesma linha
    - operadores e funcoes apenas por whitelist
    - nao aceitar texto livre estilo Excel
  - riscos:
    - definicao textual abrir brecha para parser inseguro
    - revisao de dependencias ficar complexa cedo demais
  - fora do MVP:
    - macros
    - scripts
    - referencia entre tabelas
    - formula guiada completa ja na primeira implementacao estrutural
- `TotalizadorColunaPersonalizada`
  - responsabilidade:
    - representar a configuracao de totalizacao controlada por coluna.
  - campos provaveis:
    - `coluna`
    - `tipo_totalizador`
    - `ativo`
  - relacionamentos provaveis:
    - 1 coluna pode ter 0 ou 1 totalizador no recorte inicial
  - regras de validacao:
    - apenas tipos elegiveis aceitam totalizador
    - `data` so aceita `minimo` e `maximo`
    - `sim/nao` e `lista de opcoes` so aceitam `contagem simples total`
  - riscos:
    - crescer para mini-engine analitica
    - custo de consulta em tabelas grandes sem estrategia de leitura cuidadosa
  - fora do MVP:
    - agrupamentos por opcao
    - totalizadores compostos
    - dashboards
- `Auditoria operacional`
  - responsabilidade:
    - registrar mudancas de tabela, coluna, formula, linha e exportacao.
  - campos provaveis:
    - reaproveitar conceito atual de `acao`, `modelo`, `registro_id`, `usuario`, `data_hora`, `campos_alterados`
  - relacionamentos provaveis:
    - eventos ligados ao usuario autenticado e ao registro alterado
  - regras de validacao:
    - exportacao precisa ser registravel mesmo sem before/after rico
    - alteracoes estruturais precisam capturar diff inteligivel
  - riscos:
    - vocabulário atual de auditoria ficar curto para `exportacao`
    - volume de log crescer rapido em edicao tabular
  - fora do MVP:
    - trilha imutavel completa por celula
    - versionamento full de estrutura
- `Permissoes`
  - responsabilidade:
    - separar governanca de estrutura, formulas, preenchimento, exportacao e administracao.
  - campos provaveis:
    - reaproveitar `PermissaoSistema` atual no formato `modulo.recurso.acao`
  - relacionamentos provaveis:
    - ligacao via perfil-base ja existente em `configuracoes`
  - regras de validacao:
    - menu escondido nao substitui enforcement backend
    - acoes sensiveis precisam ser mais restritas que preenchimento simples
  - riscos:
    - granularidade insuficiente entre editar estrutura e editar linhas
  - fora do MVP:
    - permissao por tabela individual
    - extras e bloqueios finos por usuario nesta frente

###### Comparacao de alternativas de persistencia para valores dinamicos

- Alternativa A: EAV com um registro por celula
  - simplicidade:
    - media; estrutura conceitual simples, mas leitura e validacao crescem rapido
  - flexibilidade:
    - alta
  - validacao por tipo:
    - media para baixa se o valor ficar generico demais
  - busca textual simples:
    - media, mas exige cuidado para nao pesquisar campos tecnicos indevidos
  - totalizadores:
    - media; agregacoes existem, mas exigem filtragem por tipo e coerencia forte
  - exportacao XLSX:
    - media; exige pivotar muitos registros por linha
  - auditoria before/after:
    - media; diffs por celula sao possiveis, mas podem gerar ruido
  - risco de performance:
    - medio, com crescimento direto de uma linha por celula
  - risco de virar planilha livre:
    - medio para alto, se o valor ficar generico e a coluna perder governanca
  - aderencia ao MVP:
    - razoavel, mas pede disciplina forte de tipagem
- Alternativa B: JSON por linha
  - simplicidade:
    - alta para gravar, baixa para governar
  - flexibilidade:
    - muito alta
  - validacao por tipo:
    - baixa no longo prazo; concentraria muita regra fora do model
  - busca textual simples:
    - baixa para media, dependendo de leitura e filtros manuais
  - totalizadores:
    - baixa
  - exportacao XLSX:
    - media; leitura e montagem seriam possiveis, mas mais manuais
  - auditoria before/after:
    - baixa; diff tende a ficar grosso demais por linha inteira
  - risco de performance:
    - medio inicialmente, mas com custo de parsing e pouca seletividade
  - risco de virar planilha livre:
    - alto
  - aderencia ao MVP:
    - baixa; simplifica demais a gravacao e enfraquece a governanca
- Alternativa C: colunas tipadas separadas por tipo
  - simplicidade:
    - baixa; multiplica entidades e fluxos cedo demais
  - flexibilidade:
    - media
  - validacao por tipo:
    - alta
  - busca textual simples:
    - media, mas com unificacao trabalhosa
  - totalizadores:
    - alta para tipos numericos, com custo de orquestracao
  - exportacao XLSX:
    - media; exige compor varias fontes
  - auditoria before/after:
    - media; diffs ficam dispersos
  - risco de performance:
    - medio, com varios joins e duplicacao de logica
  - risco de virar planilha livre:
    - medio
  - aderencia ao MVP:
    - baixa para o primeiro recorte, por excesso de estrutura
- Alternativa D: modelo hibrido
  - leitura desta SPEC:
    - entidades explicitas de tabela, coluna, linha, formula e totalizador
    - persistencia de valor por celula com slots tipados controlados e `valor_json` residual apenas para casos guiados
  - simplicidade:
    - media
  - flexibilidade:
    - alta o suficiente para o MVP, sem abrir JSON livre por linha
  - validacao por tipo:
    - alta
  - busca textual simples:
    - media para alta no recorte do MVP, porque os valores visiveis/editaveis continuam controlados
  - totalizadores:
    - alta no que o MVP precisa
  - exportacao XLSX:
    - alta para o recorte da frente
  - auditoria before/after:
    - alta; conversa melhor com o padrao atual de snapshot/diff
  - risco de performance:
    - medio, mas administravel com os limites atuais de 5.000 linhas e 30 colunas
  - risco de virar planilha livre:
    - menor do que nas demais, desde que `configuracao_json` e formulas continuem governados
  - aderencia ao MVP:
    - alta

###### Estrategia recomendada desta SPEC

- Abordagem preferencial:
  - adotar modelo hibrido controlado
  - estrutura principal separada em `TabelaPersonalizada`, `ColunaPersonalizada`, `LinhaTabelaPersonalizada`, `ValorTabelaPersonalizada`, `FormulaColunaPersonalizada` e `TotalizadorColunaPersonalizada`
  - persistencia de valor por celula com slots tipados, e nao JSON solto por linha inteira
- Justificativa:
  - conversa melhor com o estilo atual do projeto, que privilegia models explicitos, validacoes objetivas, auditoria por snapshot e permissoes claras
  - facilita manter busca textual simples, exportacao XLSX previsivel e totalizadores controlados sem abrir engine livre
  - preserva governanca sobre tipos, visibilidade e formulas, reduzindo o risco de virar "Excel dentro do sistema"
- Alternativa descartada como estrategia inicial:
  - `JSON por linha`
  - motivo:
    - enfraquece validacao por tipo
    - dificulta auditoria before/after legivel
    - aumenta o risco de formula e configuracao escaparem do controle do sistema
- Alternativa a evitar como primeira onda:
  - `colunas tipadas separadas por tipo`
  - motivo:
    - deixa a estrutura mais pesada do que o MVP exige
    - complica leitura, manutencao e exportacao cedo demais
- Pontos que precisam ser reavaliados antes da implementacao real:
  - se `valor_monetario` merece slot proprio ou se `valor_numero` com contexto do tipo atende o recorte
  - se `valor_calculado` deve ficar persistido ou apenas derivado em leitura nas primeiras iteracoes
  - se `TotalizadorColunaPersonalizada` deve aceitar uma configuracao por coluna ou historico/versionamento futuro
  - se a auditoria de exportacao entra por extensao de `AuditoriaFinanceiro` ou por regra especifica acoplada ao fluxo
  - se a ordenacao de linhas nasce por `criado_em` e `pk` ou se ja vale um campo explicito de `ordem`

###### Modelagem conceitual minima sugerida

- `TabelaPersonalizada`
  - `nome`
  - `descricao`
  - `status`
  - `ordem`
  - `criado_por`
  - `atualizado_por`
  - `criado_em`
  - `atualizado_em`
- `ColunaPersonalizada`
  - `tabela`
  - `nome`
  - `tipo_dado`
  - `obrigatoria`
  - `visivel`
  - `ordem`
  - `calculada`
  - `configuracao_json`, quando necessario para opcoes, precisao ou metadado guiado
  - `status`
- `LinhaTabelaPersonalizada`
  - `tabela`
  - `status`
  - `ordem` ou `criado_em`
  - `criado_por`
  - `atualizado_por`
  - `criado_em`
  - `atualizado_em`
- `ValorTabelaPersonalizada`
  - `linha`
  - `coluna`
  - `valor_texto`
  - `valor_numero`
  - `valor_data`
  - `valor_booleano`
  - `valor_json`, quando necessario para lista de opcoes ou payload guiado controlado
  - `valor_calculado`
  - `atualizado_em`
- `FormulaColunaPersonalizada`
  - `coluna_calculada`
  - `expressao_normalizada` ou `estrutura_json_guiada`
  - `versao`
  - `ativa`
  - `validada_em`
- `TotalizadorColunaPersonalizada`
  - `coluna`
  - `tipo_totalizador`
  - `ativo`
- `Auditoria`
  - avaliar reaproveitamento de `AuditoriaFinanceiro` com extensao futura de vocabulario/escopo, sem criar model nesta etapa

###### Regras tecnicas a preservar

- formula por coluna, nunca por celula no MVP
- formula apenas com colunas da mesma linha
- formula nao pode ser texto livre estilo Excel
- colunas calculadas sao somente leitura na entrada de linhas
- totalizadores nao sao formulas livres
- busca textual simples deve considerar apenas valores visiveis/editaveis no MVP
- exportacao XLSX deve refletir a tela visivel e incluir totalizadores visiveis
- nenhuma entidade desta frente gera lancamento financeiro
- nenhuma entidade desta frente altera saldo, extrato, resumo, prestacao/fechamento ou balancete

###### Permissoes e modelagem

- Esta etapa nao cria permissao executavel.
- A modelagem deve facilitar a separacao futura entre:
  - visualizar tabelas
  - criar tabela
  - editar estrutura
  - configurar formula
  - preencher linhas
  - editar linhas
  - exportar
  - arquivar/restaurar
  - administrar configuracoes
- Direcao documental recomendada para os codigos futuros:
  - `financeiro.tabelas_personalizadas.visualizar`
  - `financeiro.tabelas_personalizadas.criar`
  - `financeiro.tabelas_personalizadas.editar_estrutura`
  - `financeiro.tabelas_personalizadas.configurar_formula`
  - `financeiro.tabelas_personalizadas.preencher_linhas`
  - `financeiro.tabelas_personalizadas.editar_linhas`
  - `financeiro.tabelas_personalizadas.exportar`
  - `financeiro.tabelas_personalizadas.arquivar_restaurar`
  - `financeiro.tabelas_personalizadas.administrar_configuracoes`

###### Auditoria e modelagem

- `AuditoriaFinanceiro` pode ser reaproveitada como padrao base de estrategia, porque ja oferece:
  - `acao`
  - `modelo`
  - `registro_id`
  - `usuario`
  - `data_hora`
  - `campos_alterados` com `before/after`
- Ajustes futuros provaveis antes da implementacao da frente:
  - ampliar vocabulario para eventos de `exportacao`
  - garantir rotulos adequados para `tabela`, `coluna`, `linha`, `formula` e `totalizador`
  - decidir se eventos muito frequentes de edicao tabular entram em log por linha, por lote ou por celula
- A implementacao da auditoria pode entrar em microetapa propria ou ser acoplada a cada fluxo estrutural, conforme decisao futura, mas a estrategia de snapshot/diff deve ser preservada.

###### Riscos tecnicos da modelagem

- modelagem dinamica ampla demais
- valores tipados dificeis de buscar se a governanca dos slots for frouxa
- totalizadores pesados em tabelas maiores
- auditoria volumosa
- formulas dificeis de validar
- performance com ate 5.000 linhas x 30 colunas
- crescimento futuro para planilha livre
- vinculo indevido com financeiro oficial

###### Decisao desta SPEC

- A modelagem recomendada nesta microetapa e:
  - modelo hibrido controlado com entidades explicitas e valor por celula em slots tipados
- Esta recomendacao ainda precisa de aprovacao antes de virar `model` e `migration`.
- Se aprovada, a proxima microetapa tecnica pode ser a implementacao minima da estrutura de dados.
- Mesmo com aprovacao estrutural, a primeira implementacao nao deve incluir formula guiada completa; a camada de formulas continua como etapa sensivel posterior.

#### Microetapa 3 - implementacao minima da estrutura de dados do MVP

- Objetivo:
  - abrir a primeira etapa funcional apenas da base estrutural, apos SPEC tecnica aprovada.
- Escopo:
  - criar entidades minimas de tabela, coluna, linha e valor;
  - manter formulas mais sensiveis e integracoes fora desta primeira modelagem;
  - nao incluir formula guiada completa nesta primeira implementacao estrutural.
- Arquivos provaveis a consultar:
  - `financeiro/models.py`;
  - `financeiro/migrations/`;
  - testes do modulo financeiro.
- Risco:
  - criar base cedo demais ou ampla demais;
  - endurecer modelagem antes de validar recorte minimo.
- Envolve model/migration/banco:
  - sim.
- Validacoes esperadas:
  - `makemigrations --check --dry-run`;
  - testes dirigidos da nova estrutura;
  - confirmacao de que nao ha impacto em calculos, saldos e relatorios.
- Dependencias anteriores:
  - microetapa 2 aprovada.
- Fora de escopo:
  - formulas guiadas;
  - integracao com financeiro oficial;
  - exportacao XLSX completa;
  - UX refinada.

##### Resultado da implementacao minima da estrutura de dados

- Estrutura implementada nesta microetapa:
  - `TabelaPersonalizada`
  - `ColunaPersonalizada`
  - `LinhaTabelaPersonalizada`
  - `ValorTabelaPersonalizada`
- Regras tecnicas implementadas no recorte:
  - `TabelaPersonalizada` com `status` controlado, timestamps, `criado_por`/`atualizado_por`, ordenacao segura e bloqueio de duplicidade de nome nao arquivado por normalizacao simples
  - `ColunaPersonalizada` com `tipo_dado` por whitelist, `configuracao_json` controlada, `status`, ordenacao, `calculada` e bloqueio de duplicidade de nome por tabela entre colunas nao arquivadas
  - `LinhaTabelaPersonalizada` com vinculo a tabela, `status` logico e timestamps
  - `ValorTabelaPersonalizada` com unicidade `linha + coluna`, validacao de pertencimento da coluna a mesma tabela da linha e validacao basica do slot de valor conforme o tipo da coluna
- Validacoes basicas implementadas:
  - coluna calculada exige `tipo_dado=formula_controlada`
  - `formula_controlada` exige `calculada=True`
  - coluna calculada nao aceita valor manual nesta etapa
  - `inteiro` nao aceita casas decimais
  - `mes_competencia` exige `MM/AAAA`
  - `lista_opcoes` aceita validacao basica contra `configuracao_json.opcoes`, quando informado
- Itens deliberadamente fora desta implementacao:
  - `FormulaColunaPersonalizada`
  - `TotalizadorColunaPersonalizada`
  - formula guiada
  - totalizadores
  - menu, views, urls, templates e forms
  - permissoes executaveis
  - exportacao XLSX da nova frente
  - auditoria operacional propria da nova frente
  - qualquer integracao com financeiro oficial
- Validacao tecnica concluida nesta microetapa:
  - migration criada no `financeiro`
  - `py manage.py makemigrations --check --dry-run` sem pendencias
  - `py manage.py check` sem issues
  - `py -m compileall financeiro configuracoes` sem erro
  - `py manage.py test financeiro` com suite verde
- Proxima microetapa recomendada:
  - `permissoes executaveis da frente`
  - antes do menu real, para evitar link quebrado sem listagem minima

#### Microetapa 4 - permissoes e menu da frente

- Objetivo:
  - encaixar a frente na governanca de acesso e na navegacao do modulo.
- Escopo:
  - criar permissoes do recurso;
  - posicionar `Financeiro > Controles internos > Tabelas personalizadas`;
  - separar visualizar, criar, editar estrutura, configurar formula, preencher linhas, exportar e arquivar/restaurar.
- Arquivos provaveis a consultar:
  - `docs/MATRIZ_PERMISSOES.md`;
  - camada de permissoes em `configuracoes`;
  - shell/menu do `financeiro`.
- Risco:
  - expor menu sem enforcement backend;
  - misturar perfil de preenchimento com perfil de estrutura.
- Envolve model/migration/banco:
  - pode envolver permissao/migration apenas se a SPEC tecnica ja estiver aprovada para isso.
- Validacoes esperadas:
  - menu condicionado por permissao;
  - protecao backend coerente com a matriz.
- Dependencias anteriores:
  - microetapa 1;
  - preferencialmente apos microetapa 3 quando a frente ja tiver base funcional minima.
- Fora de escopo:
  - integrações com financeiro;
  - refinamentos amplos de UX.

- Resultado consolidado desta microetapa intermediaria segura:
  - permissoes executaveis/documentais implementadas antes do menu real;
  - codigos canonicos criados para:
    - `financeiro.tabelas_personalizadas.visualizar`
    - `financeiro.tabelas_personalizadas.criar`
    - `financeiro.tabelas_personalizadas.editar_estrutura`
    - `financeiro.tabelas_personalizadas.configurar_formula`
    - `financeiro.tabelas_personalizadas.preencher_linhas`
    - `financeiro.tabelas_personalizadas.editar_linhas`
    - `financeiro.tabelas_personalizadas.exportar`
    - `financeiro.tabelas_personalizadas.arquivar_restaurar`
    - `financeiro.tabelas_personalizadas.administrar_configuracoes`
  - seed por migration no app `configuracoes`, sem criar menu real nesta etapa
  - recorte inicial de perfis adotado:
    - `administrador-geral` e `gestao-administrativa`: todas as permissoes
    - `operador-financeiro`: `visualizar`, `criar`, `editar_estrutura`, `preencher_linhas`, `editar_linhas` e `exportar`
    - `consulta-visualizacao`: `visualizar` e `exportar`
  - `configurar_formula`, `arquivar_restaurar` e `administrar_configuracoes` ficaram mais restritas por risco de governanca
  - menu real adiado para a proxima microetapa, quando ja existir rota/listagem minima e nao houver risco de link quebrado

#### Microetapa 5 - listagem de tabelas personalizadas

- Objetivo:
  - entregar a tela inicial da frente.
- Escopo:
  - listagem de tabelas;
  - busca por nome;
  - filtro por status;
  - ordenacao simples.
- Arquivos provaveis a consultar:
  - views/listagens do `financeiro`;
  - templates de listagem ja consolidados no modulo.
- Risco:
  - herdar padrao visual que aproxime a frente de lancamentos financeiros.
- Envolve model/migration/banco:
  - nao, assumindo estrutura minima ja existente.
- Validacoes esperadas:
  - permissao de visualizacao;
  - navegacao correta pelo menu;
  - ausencia de mistura com lancamentos e relatorios financeiros.
- Dependencias anteriores:
  - microetapas 3 e 4.
- Fora de escopo:
  - edicao de colunas;
  - preenchimento de linhas;
  - formulas.
- Resultado consolidado desta microetapa:
  - rota criada em `controles-internos/tabelas-personalizadas/` com name `financeiro:tabela-personalizada-list`
  - listagem minima em `ListView`, protegida por `financeiro.tabelas_personalizadas.visualizar`
  - template proprio criado apenas para leitura de:
    - nome
    - descricao curta
    - status
    - quantidade de colunas
    - quantidade de linhas
    - ultima atualizacao
  - filtros simples entregues:
    - busca por nome
    - filtro por status
  - menu real entregue em `Financeiro > Controles internos > Tabelas personalizadas`, visivel apenas para quem tem a permissao de visualizar
  - sem acoes quebradas de criacao, edicao, estrutura, linhas, formulas, totalizadores ou exportacao
- Proxima microetapa recomendada:
  - abrir o cadastro inicial da tabela personalizada ou, se preferir um passo ainda mais seguro, refinar a listagem com ordenacao/contagem/paginacao antes de abrir escrita

#### Microetapa 6 - cadastro e edicao da tabela

- Objetivo:
  - permitir criar e manter metadados da tabela.
- Escopo:
  - nome;
  - descricao;
  - status;
  - ordem, se mantida no recorte final.
- Arquivos provaveis a consultar:
  - formularios e views de cadastro do `financeiro`;
  - padroes de validacao e mensagens do modulo.
- Risco:
  - confundir metadado de tabela com configuracao estrutural mais profunda.
- Envolve model/migration/banco:
  - nao, assumindo estrutura minima ja existente.
- Validacoes esperadas:
  - criacao/edicao sem impacto em outras frentes;
  - redirecionamento coerente para a listagem, sem depender ainda da configuracao de colunas.
- Dependencias anteriores:
  - microetapas 3, 4 e 5.
- Fora de escopo:
  - colunas;
  - linhas;
  - formulas.
- Resultado consolidado desta microetapa:
  - `TabelaPersonalizadaForm` criado apenas com `nome`, `descricao`, `status` e `ordem`
  - `TabelaPersonalizadaCreateView` protegida por `financeiro.tabelas_personalizadas.criar`
  - `TabelaPersonalizadaUpdateView` protegida por `financeiro.tabelas_personalizadas.editar_estrutura`
  - rotas criadas:
    - `financeiro:tabela-personalizada-create`
    - `financeiro:tabela-personalizada-update`
  - template proprio de formulario criado apenas para dados gerais da tabela
  - listagem atualizada com:
    - botao `Nova tabela` apenas para quem pode criar
    - acao `Editar` apenas para quem pode editar estrutura
  - sem redirecionar para colunas, porque essa microetapa ainda nao existe
- Proxima microetapa recomendada:
  - abrir a configuracao inicial de colunas da tabela, mantendo linhas, formulas, totalizadores e exportacao fora deste recorte

#### Microetapa 7 - configuracao de colunas

- Objetivo:
  - abrir a camada de estrutura configuravel da tabela.
- Escopo:
  - criar, editar, reordenar, ocultar e arquivar coluna;
  - nome, tipo, obrigatoria, visivel, ordem;
  - comum ou calculada.
- Arquivos provaveis a consultar:
  - formularios estruturais do `financeiro`;
  - templates de configuracao/listagem ordenavel.
- Risco:
  - abrir liberdade demais sem validacao por tipo;
  - permitir alteracao insegura de coluna depois de uso real.
- Envolve model/migration/banco:
  - nao, assumindo base estrutural aprovada.
- Validacoes esperadas:
  - persistencia da ordem;
  - respeito ao tipo de coluna;
  - bloqueio de acoes inseguras em colunas dependentes.
- Dependencias anteriores:
  - microetapa 6.
- Fora de escopo:
  - formula guiada completa;
  - totalizadores;
  - exportacao final.
- Resultado consolidado desta microetapa:
  - rota de configuracao estrutural criada por tabela:
    - `financeiro:tabela-personalizada-coluna-list`
    - `financeiro:tabela-personalizada-coluna-create`
    - `financeiro:tabela-personalizada-coluna-update`
  - listagem de colunas criada com:
    - nome
    - tipo de dado
    - obrigatoria
    - visivel
    - ordem
    - status
  - `ColunaPersonalizadaForm` criado sem expor `calculada`
  - `formula_controlada` bloqueada nesta etapa
  - `lista_opcoes` habilitada de forma controlada por campo textual auxiliar, com maximo de 20 opcoes e gravacao em `configuracao_json.opcoes`
  - listagem de tabelas atualizada com acao `Colunas` apenas para quem tem `editar_estrutura`
- Proxima microetapa recomendada:
  - abrir a tela de linhas e o preenchimento inicial de valores, ainda sem formulas guiadas, totalizadores ou exportacao

#### Microetapa 8 - linhas e valores editaveis

- Status apos implementacao:
  - concluida com listagem de linhas, criacao e edicao basica de valores por tabela
  - campos gerados dinamicamente apenas para colunas ativas, visiveis e nao calculadas
  - `formula_controlada` mantida fora do formulario e da listagem desta etapa
  - permissoes separadas entre visualizar, preencher e editar linhas
- Status apos refinamento tecnico curto:
  - `ValorTabelaPersonalizada.valor_numero` ampliado para 8 casas decimais reais por migration propria
  - entrada decimal brasileira aceita virgula ou ponto no formulario dinamico de linhas
  - `decimal` limitado a 8 casas, `monetario` a 2 e `percentual` a 4, com mensagens claras em portugues
  - estado vazio da grade ganhou CTA contextual `+ Nova linha` apenas para quem pode preencher
  - edicao de linha passou a normalizar por tipo os valores iniciais carregados do banco, evitando que `monetario` e `percentual` sejam exibidos com 8 casas e rejeitados pelo proprio formulario
- Objetivo:
  - abrir a grade operacional de dados do MVP.
- Escopo:
  - tela tabular;
  - adicionar linha;
  - editar linha;
  - arquivar ou excluir logicamente linha;
  - validar valor por tipo de dado.
- Arquivos provaveis a consultar:
  - templates tabulares do modulo;
  - views/formularios de edicao em lote ou grade.
- Risco:
  - UX pesada demais;
  - validacao fraca por tipo;
  - aproximacao visual de planilha livre.
- Envolve model/migration/banco:
  - nao, assumindo estrutura minima aprovada.
- Validacoes esperadas:
  - respeito a obrigatoriedade e tipos;
  - colunas calculadas somente leitura, quando existirem;
  - arquivamento logico funcional.
- Dependencias anteriores:
  - microetapa 7.
- Fora de escopo:
  - filtros avancados;
  - formulas livres;
  - importacao em massa.
- Proxima microetapa recomendada:
  - abrir os totalizadores controlados por coluna, ainda sem formulas guiadas, exportacao XLSX ou auditoria operacional propria

#### Microetapa 9 - totalizadores controlados por coluna

- Status apos implementacao: CONCLUIDA
- Objetivo:
  - adicionar leitura consolidada minima do MVP sem abrir formula livre.
- Escopo:
  - soma, media, minimo, maximo e contagem;
  - `data` com `minimo` e `maximo` somente se configurado;
  - `sim/nao` e `lista de opcoes` com contagem simples total;
  - sem agrupamento por opcao no MVP.
- Arquivos provaveis a consultar:
  - listagens e componentes de rodape do `financeiro`;
  - exportacoes atuais para coerencia de apresentacao.
- Risco:
  - transformar totalizador em mini-engine de formula;
  - gerar expectativa de analitico avancado cedo demais.
- Envolve model/migration/banco:
  - sim, no recorte implementado: model proprio e migration dedicada no app `financeiro`.
- Validacoes esperadas:
  - totalizadores corretos por tipo elegivel;
  - ausencia de expressao livre;
  - nenhuma interferencia em calculos financeiros oficiais.
- Dependencias anteriores:
  - microetapa 8.
- Fora de escopo:
  - agrupamentos por opcao;
  - dashboards;
  - filtros compostos.
- Consolidacao da entrega:
  - model `TotalizadorColunaPersonalizada` criado com choices controlados de `soma`, `media`, `minimo`, `maximo` e `contagem`
  - configuracao de totalizadores acoplada ao `ColunaPersonalizadaForm`, com exibicao apenas de opcoes compativeis por tipo
  - troca de tipo da coluna passa a limpar totalizadores incompativeis de forma segura
  - rodape da tela de linhas agora exibe apenas totalizadores configurados em colunas visiveis, ativas e nao calculadas
  - linhas arquivadas nao entram nos calculos
  - `decimal` preserva soma com 8 casas; `monetario` e `percentual` mantem exibicao ajustada ao tipo
- Proxima microetapa recomendada:
  - abrir a busca textual simples na tela de linhas, mantendo formulas guiadas, exportacao XLSX e auditoria operacional propria fora do recorte imediato

#### Microetapa 10 - busca textual simples na tela de linhas

- Status apos implementacao: CONCLUIDA
- Objetivo:
  - facilitar consulta operacional basica sem abrir filtros avancados.
- Escopo:
  - busca textual sobre valores visiveis/editaveis;
  - manter fora do MVP filtros compostos e visoes salvas.
- Arquivos provaveis a consultar:
  - padroes de busca textual em listagens do `financeiro`.
- Risco:
  - busca cara ou ambigua em estrutura dinamica;
  - pressao para evoluir cedo demais para filtro avancado.
- Envolve model/migration/banco:
  - nao necessariamente.
- Validacoes esperadas:
  - busca simples coerente com colunas visiveis;
  - sem regressao de performance basica do recorte.
- Dependencias anteriores:
  - microetapa 8.
- Fora de escopo:
  - filtros avancados;
  - busca por tipo especifico;
  - visoes salvas.
- Consolidacao da entrega:
  - campo `Buscar nas linhas` adicionado no topo da listagem de linhas
  - busca aplicada apenas sobre valores visiveis/editaveis das colunas ativas, visiveis e nao calculadas da tabela atual
  - cobertura simples de texto, lista de opcoes, mes/competencia, numero, data e booleano, sem virar filtro analitico avancado
  - mensagem propria para busca sem resultado e botao `Limpar` quando houver termo ativo
  - totalizadores do rodape passam a refletir o resultado filtrado da busca, sem opcao de alternar para total geral nesta etapa
- Proxima microetapa recomendada:
  - abrir a exportacao XLSX da nova frente, mantendo formulas guiadas e auditoria operacional propria fora do recorte imediato

#### Microetapa 11 - exportacao XLSX

- Objetivo:
  - disponibilizar saida documental do controle interno.
- Escopo:
  - exportar tabela visivel;
  - cabecalhos, linhas visiveis e formatacao basica;
  - incluir colunas calculadas pelo valor resultante, quando existirem;
  - incluir totalizadores visiveis no rodape;
  - registrar evento de exportacao na auditoria.
- Arquivos provaveis a consultar:
  - exportacoes XLSX existentes do `financeiro`;
  - pontos de auditoria e views de download.
- Risco:
  - exportacao ser confundida com integracao financeira;
  - perda de consistencia entre tela e arquivo.
- Envolve model/migration/banco:
  - nao necessariamente.
- Validacoes esperadas:
  - arquivo coerente com a tela;
  - formatacao basica por tipo;
  - evento auditavel registrado.
- Dependencias anteriores:
  - microetapas 8 e 9.
- Fora de escopo:
  - importacao em massa;
  - sincronizacao com financeiro oficial.
- Consolidacao da entrega:
  - rota `controles-internos/tabelas-personalizadas/<tabela_id>/linhas/exportar-xlsx/` implementada no app `financeiro`
  - permissao `financeiro.tabelas_personalizadas.exportar` aplicada no backend e no botao da tela de linhas
  - exportacao limitada a colunas ativas, visiveis, nao calculadas e nao `formula_controlada`
  - exportacao limitada a linhas ativas da tabela atual, respeitando a busca textual simples quando houver filtro ativo
  - valores exportados usando a mesma leitura formatada da tela de linhas
  - totalizadores visiveis incluidos no bloco final da planilha, refletindo o mesmo resultado filtrado da tela
  - cabecalho simples reforcando que o arquivo representa controle interno sem efeito financeiro oficial
- Proxima microetapa recomendada:
  - abrir formulas guiadas por coluna, mantendo auditoria operacional propria fora do recorte imediato

#### Microetapa 12 - formulas guiadas por coluna

- Objetivo:
  - abrir a parte mais sensivel da frente de forma isolada, controlada e sem transformar a tabela personalizada em planilha livre.
- Escopo:
  - formula aplicada a coluna inteira;
  - sem formula celula por celula;
  - sem formula livre estilo Excel;
  - apenas colunas da mesma linha;
  - operadores por whitelist curta;
  - bloqueio de dependencias inseguras;
  - coluna calculada fora do form de linhas e exibida apenas como leitura;
  - valor calculado aparecendo na listagem de linhas e, quando liberado, no XLSX.
- SPEC tecnica curta consolidada nesta microetapa documental:
  - armazenamento inicial recomendado em `ColunaPersonalizada.configuracao_json.formula`, sem migration no primeiro recorte
  - estrutura JSON sugerida:
    - `configuracao_json.formula.habilitada`
    - `configuracao_json.formula.operacao`
    - `configuracao_json.formula.operandos`
    - `configuracao_json.formula.resultado_tipo`
    - `configuracao_json.formula.casas_decimais`
  - justificativa para ficar em JSON no primeiro recorte:
    - `configuracao_json` ja e usado com governanca para `opcoes` e `filtro`
    - o model ja possui `calculada=True`, `tipo_dado=formula_controlada` e `valor_calculado`
    - a complexidade inicial cabe em configuracao curta, sem exigir model/migration proprios antes da homologacao do fluxo
  - gatilhos para abrir model/migration antes de ampliar a frente:
    - versoes multiplas de formula
    - dependencia entre formulas calculadas
    - necessidade de auditoria propria detalhada da estrutura
    - necessidade de indexacao/consulta estrutural fora do fluxo atual
- Tipos-fonte recomendados para o primeiro recorte:
  - `inteiro`
  - `decimal`
  - `monetario`
  - `percentual`
- Tipos fora do primeiro recorte como fonte:
  - `data`
  - `mes_competencia`
  - `texto_curto`
  - `texto_longo`
  - `booleano`
  - `lista_opcoes`
- Tipo de resultado recomendado no primeiro recorte:
  - `decimal`
  - `monetario`
- Tipos de resultado adiados:
  - `inteiro`
  - `percentual`
- Whitelist inicial recomendada:
  - `soma`
  - `subtracao`
  - `multiplicacao`
  - `divisao`
- Fora do primeiro recorte:
  - parenteses
  - `min`
  - `max`
  - arredondamento configuravel
  - percentual derivado
  - qualquer expressao textual livre digitada pela usuaria
- Regra de seguranca consolidada:
  - sem `eval`
  - sem `exec`
  - sem macro/script
  - sem referencia livre por nome digitado
  - sem formula por celula
  - sem referencia entre tabelas
  - sem leitura/escrita em `LancamentoFinanceiro`
  - sem alteracao de saldo, extrato, resumo, prestacao/fechamento ou balancete
- Validacoes necessarias:
  - bloquear formula em coluna nao marcada como calculada
  - bloquear uso da propria coluna como operando
  - bloquear formula sobre coluna calculada no primeiro recorte
  - bloquear coluna-fonte fora da mesma tabela/linha
  - bloquear coluna-fonte arquivada ou invisivel
  - bloquear formula incompleta
  - bloquear divisao por zero com mensagem clara
  - impedir edicao manual do valor calculado
- Comportamento recomendado na tela de linhas:
  - coluna calculada continua fora do form de criacao/edicao
  - calculo refeito no pipeline central da tela antes de renderizar, buscar e exportar
  - se faltar valor de operando, o resultado deve ficar vazio no primeiro recorte, sem assumir zero silenciosamente
- Busca, filtros, totalizadores e XLSX:
  - busca textual pode passar a considerar o valor calculado quando a etapa de calculo entrar
  - filtro estruturado em coluna calculada fica fora do primeiro recorte
  - totalizador sobre coluna calculada fica fora do primeiro recorte por cautela contra divergencia entre tela, XLSX e calculo
  - XLSX deve exportar apenas o valor final calculado, sem formula Excel e com formato brasileiro
- Permissoes:
  - usar a permissao existente `financeiro.tabelas_personalizadas.configurar_formula`
  - manter separacao de `editar_estrutura`
  - usuarios com permissao apenas de visualizacao continuam vendo o resultado calculado na tela, sem editar a formula
- Arquivos provaveis a consultar:
  - `financeiro/models.py`
  - `financeiro/forms.py`
  - `financeiro/views.py`
  - `financeiro/templates/financeiro/tabela_personalizada_coluna_form.html`
  - `financeiro/templates/financeiro/tabela_personalizada_linha_list.html`
  - `financeiro/templates/financeiro/tabela_personalizada_linha_form.html`
  - `financeiro/tests.py`
- Risco:
  - virar vetor para comportamento de planilha livre;
  - criar expressao textual insegura;
  - criar dependencia circular ou regra dificil de auditar;
  - gerar divergencia entre tela, busca, totalizador e XLSX;
  - induzir leitura equivocada como se a frente alterasse o financeiro oficial.
- Envolve model/migration/banco:
  - nao no primeiro recorte recomendado; reavaliar somente se o JSON deixar de ser suficiente.
- Validacoes esperadas:
  - bloqueio de referencia circular;
  - bloqueio de referencia entre tabelas;
  - bloqueio de codigo executavel;
  - calculo restrito a whitelist;
  - bloqueio de divisao por zero;
  - bloqueio de formula manualmente inconsistente;
  - resultado vazio quando operando obrigatorio nao estiver preenchido.
- Dependencias anteriores:
  - microetapas 2, 7, 8, 9, 10 e 11.
- Fora de escopo:
  - macros;
  - scripts;
  - referencias livres;
  - escrita em outras tabelas ou no financeiro;
  - formula sobre formula;
  - filtro estruturado em coluna calculada;
  - totalizador em coluna calculada;
  - auditoria operacional propria desta frente.
- Proxima microetapa recomendada:
  - dividir a entrega em tres ondas seguras:
    - 1. configuracao da formula na estrutura da coluna, com validacao forte e sem calculo ainda
    - 2. calculo + exibicao somente leitura na listagem de linhas
    - 3. integracao controlada com busca/XLSX e decisao separada sobre totalizadores em colunas calculadas

Status apos Onda 1:
- configuracao visual da formula guiada implementada apenas na estrutura da coluna
- persistencia inicial entregue em `ColunaPersonalizada.configuracao_json.formula`, sem migration
- calculo, busca, filtros, totalizadores e XLSX com coluna calculada permaneciam fora do recorte imediato

Status apos Onda 2:
- calculo da formula guiada implementado apenas em tempo de leitura na listagem de linhas
- coluna calculada exibida como leitura na grade, sem entrar no formulario de linha
- operando ausente e divisao por zero produzem resultado vazio, sem erro de pagina
- `valor_calculado` continua sem uso e sem persistencia
- busca, filtros estruturados, totalizadores e XLSX continuam fora da integracao com colunas calculadas nesta etapa

Proxima microetapa recomendada:
- abrir onda propria para decidir integracao controlada com busca e XLSX antes de avaliar totalizadores sobre calculadas

#### Microetapa 12.2.1 - UX autodidata do formulario de colunas

- Objetivo:
  - reduzir ambiguidade no cadastro de colunas exibindo apenas blocos relevantes por tipo.
- Entregue:
  - `Opcoes da lista` restrito a `lista_opcoes`
  - `Formula guiada` restrita a `formula_controlada` + permissao `configurar_formula`
  - `Filtro estruturado` restrito aos tipos elegiveis
  - `Totalizadores` visivel apenas com compatibilidade de tipo e oculto em formula
  - microcopy curta contextual nos quatro blocos
- Guardrails mantidos:
  - sem mudanca de regra de negocio
  - sem mudanca do calculo de formulas da Onda 2
  - sem integrar formula com busca/filtro/totalizador/XLSX
  - sem model/migration/banco
- liberacao controlada apenas para quem possui `financeiro.tabelas_personalizadas.configurar_formula`
- validacoes estruturais entregues:
  - operacoes limitadas a `soma`, `subtracao`, `multiplicacao` e `divisao`
  - fontes limitadas a colunas numericas ativas, visiveis, da mesma tabela e nao calculadas
  - resultado limitado a `decimal` e `monetario`
  - bloqueio de formula sobre formula, uso da propria coluna, configuracao incompleta e quantidade invalida de operandos
- preservado nesta onda:
  - sem calculo funcional
  - sem preenchimento de `valor_calculado`
  - sem exibicao de resultado calculado na tela de linhas
  - sem impacto em busca, filtros, totalizadores e XLSX
- proxima onda recomendada:
  - implementar o calculo e a exibicao somente leitura das colunas calculadas na listagem de linhas

#### Microetapa 13 - auditoria operacional

- Objetivo:
  - fechar rastreabilidade minima da frente.
- Escopo:
  - auditar tabela, coluna, formula, linha e exportacao;
  - registrar usuario, data/hora, acao e antes/depois quando aplicavel.
- Arquivos provaveis a consultar:
  - implementacoes de auditoria ja existentes no `financeiro`;
  - camada de views sensiveis da nova frente.
- Risco:
  - abrir estrutura flexivel sem trilha suficiente;
  - dificultar suporte e governanca depois da homologacao.
- Envolve model/migration/banco:
  - possivelmente, conforme padrao de auditoria adotado.
- Validacoes esperadas:
  - eventos principais auditados;
  - leitura coerente do historico.
- Dependencias anteriores:
  - microetapa 1;
  - e, para cobertura completa, apos microetapas 6 a 12 conforme o recorte auditado.
- Fora de escopo:
  - desfazer/restaurar;
  - auditoria acionavel transversal completa.

#### Microetapa 14 - refinamento visual e UX do MVP

- Objetivo:
  - garantir que a frente pareca um controle interno governado, e nao um Excel livre.
- Escopo:
  - reforcar diferenca visual para financeiro oficial;
  - revisar mensagens, estados vazios e navegacao;
  - ajustar hierarquia entre estrutura, linhas, totalizadores e exportacao.
- Arquivos provaveis a consultar:
  - templates e componentes visuais da nova frente;
  - padroes de UX consolidados do `financeiro`.
- Risco:
  - a base funcional nascer correta, mas a experiencia induzir uso errado.
- Envolve model/migration/banco:
  - nao.
- Validacoes esperadas:
  - leitura clara de controle interno;
  - ausencia de aparencia de planilha livre;
  - navegacao compreensivel entre listagem, estrutura e linhas.
- Dependencias anteriores:
  - microetapas 5 a 13 conforme o recorte implementado.
- Fora de escopo:
  - reabertura da modelagem;
  - dashboards avancados.

#### Microetapa 15 - homologacao com massa de teste

- Objetivo:
  - validar o MVP com cenarios internos controlados antes de qualquer uso real sensivel.
- Escopo:
  - criar exemplos de controles internos;
  - validar criacao de tabelas, colunas, linhas, totalizadores, busca e exportacao;
  - evitar uso de banco real sem autorizacao e backup.
- Arquivos provaveis a consultar:
  - massa de teste controlada;
  - testes automatizados e documentos de uso da frente.
- Risco:
  - homologar cedo demais com massa irreal;
  - contaminar base real sem backup.
- Envolve model/migration/banco:
  - sim, no sentido de uso da estrutura implementada; qualquer uso em base real depende de autorizacao.
- Validacoes esperadas:
  - fluxo principal do MVP validado ponta a ponta;
  - confirmacao de ausencia de impacto em financeiro oficial.
- Dependencias anteriores:
  - microetapas 3 a 14, conforme recorte entregue.
- Fora de escopo:
  - integracao escrevente com financeiro;
  - importacao em massa;
  - backlog avancado da frente.

## 0.20. Especificacao funcional: tipo/disponibilidade de conta e Balancete patrimonial

Base cadastral das contas financeiras implementada em primeira microetapa funcional. A leitura patrimonial detalhada por conta tambem foi aplicada no Balancete Institucional, sem reabrir o MVP atual do Balancete nem alterar a base de calculo.

### Objetivo funcional

Evoluir o Balancete Institucional para leitura patrimonial/gerencial do saldo, preservando o MVP atual como base e reaproveitando a mesma base de calculo do Fechamento/Prestacao.

### Cadastro de contas - campos/conceitos futuros

- Implementado em contas: tipo de conta financeira como cadastro proprio simples; disponibilidade/vinculacao total por conta; mensagem explicativa opcional.
- Tipos iniciais carregados por migration idempotente: conta corrente, conta poupanca, dinheiro/caixa, conta investimento, integralizacao de capital, conta vinculada/indisponivel e outros.
- Importacao/exportacao auxiliar de contas: contrato ampliado com os campos patrimoniais, preservando planilha legada de contas com defaults `outros` e `disponivel`.

### Integralizacao de capital

- Nao e despesa operacional.
- Nao deve ser misturada ao saldo livre disponivel sem destaque.
- Deve compor patrimonio financeiro em grupo proprio, como valor patrimonial/vinculado/indisponivel.
- A conta de integralizacao pode ser cadastrada normalmente como conta financeira; sua separacao no Balancete patrimonial e definida pelo campo `disponibilidade`.
- Orientacao operacional: quando o valor nao puder ser movimentado ate encerramento/resgate, usar tipo `Integralizacao de capital`, disponibilidade `Indisponivel/vinculada` e mensagem opcional explicando a vinculacao conforme regra da instituicao.

### Modos de exibicao do saldo no Balancete

- Detalhado por conta: mostra cada conta individualmente.
- Consolidado por tipo de conta: agrupa e soma contas do mesmo tipo, independentemente de banco, nome ou cadastro individual.
- Total consolidado: mostra apenas o total geral quando o documento precisar ser sintetico.
- Disponivel x indisponivel/vinculado: separa saldo livre operacional de valores patrimoniais, vinculados ou indisponiveis.

### Impactos futuros esperados

- Cadastro de contas: base tecnica implementada; futura evolucao pode refinar administracao dos tipos se houver necessidade de tela propria.
- Balancete Institucional: leitura patrimonial detalhada por conta ja aplicada, com separacao entre disponivel e indisponivel/vinculado e mensagem opcional discreta por conta; seguem futuros os modos consolidados/agrupados.
- Relatorios: preservar calculos atuais e alterar apenas classificacao/apresentacao quando a leitura patrimonial for solicitada.
- Regras de negocio: manter separacao entre receita, despesa e transferencia; integralizacao nao vira despesa; saldo indisponivel nao vira saldo operacional livre.

### Decisoes aprovadas para o MVP patrimonial

- Tipo de conta financeira sera cadastro proprio simples, e nao lista fixa no codigo, para permitir adaptacao a outras instituicoes, empresas e projetos futuros sem nova migracao apenas para novos tipos.
- Tipos iniciais sugeridos para carga inicial futura: conta corrente, conta poupanca, dinheiro/caixa, conta investimento, integralizacao de capital, conta vinculada/indisponivel e outros.
- Disponibilidade/vinculacao sera total por conta no MVP: uma conta sera classificada como disponivel ou indisponivel/vinculada em seu saldo total.
- Disponibilidade parcial fica fora do MVP e permanece como evolucao futura, por exigir modelagem mais complexa de parcelas de saldo.
- Mensagem explicativa de indisponibilidade/vinculacao ficara no cadastro da conta; se vazia, nao aparece no Balancete; se preenchida, pode aparecer no Balancete patrimonial ou relatorio equivalente.
- Modo padrao do Balancete patrimonial sera detalhado por conta, preservando a leitura atual e adicionando separacao visual entre disponivel e indisponivel/vinculado quando aplicavel.
- Modos mais sinteticos ou agrupados permanecem como opcoes futuras: consolidado por tipo de conta, total consolidado, separado por disponivel x indisponivel/vinculado e combinacoes justificadas pelo uso real.
- Primeira implementacao funcional de cadastro/modelagem de conta foi concluida e a leitura patrimonial detalhada do Balancete Institucional tambem foi entregue, preservando a base de calculo atual do Fechamento/Prestacao.
- Fora do MVP: disponibilidade parcial, calculo patrimonial novo, alteracao de lancamentos, Extrato, Fechamento/Prestacao, importacao/exportacao, permissoes, regras de transferencia, saldos, controle por parcelas de saldo e automatizacao contabil avancada.

### Decisoes ainda pendentes antes dos modos avancados do Balancete

- Definir como filtrar/ordenar grupos no impresso sem reintroduzir poluicao visual.
- Definir se a leitura inicial do Balancete apenas separa disponivel/indisponivel no modo detalhado ou tambem expõe seletor de modo ja no primeiro recorte.
- Definir escopo dos testes especificos do Balancete patrimonial antes da proxima implementacao tecnica.

### Status apos a simplificacao dos filtros do Balancete

- A arquitetura por `Formato do Balancete` foi implementada: `Operacional`, `Operacional + patrimonio vinculado` e `Financeiro completo`.
- O filtro antigo `Exibir vinculadas/indisponiveis` saiu da interface e foi absorvido pela logica do formato escolhido.
- O formato `Operacional + patrimonio vinculado` ganhou bloco patrimonial complementar proprio, com detalhamento opcional.
- Nova diretriz funcional aprovada: o Balancete deve ser orientado por `Formato do Balancete` (Operacional, Operacional + patrimonio vinculado, Financeiro completo), com filtros complementares dependentes do formato.
- O filtro solto `Exibir vinculadas/indisponiveis` deixa de ser eixo principal da experiencia e deve ser absorvido pela selecao de formato na futura implementacao.
- Proxima etapa recomendada: apenas refinamentos adicionais de leitura, compactacao e acabamento visual, se o uso real justificar, sem alterar base de calculo.
- A separacao detalhada entre saldo disponivel operacional e saldo indisponivel/vinculado ja foi implementada no Balancete Institucional, sem alterar a base de calculo.
- Mensagem explicativa opcional ja pode aparecer de forma discreta para contas indisponiveis/vinculadas.
- O filtro `Modelo do relatorio` foi removido por redundancia.
- O filtro separado `Detalhar saldo inicial por conta` tambem foi removido por redundancia.
- A diferenca pratica do documento passou a ser controlada diretamente por `Composicao do saldo` e `Exibir vinculadas/indisponiveis`.
- Foram implementados os modos `Detalhada por conta`, `Consolidada por tipo de conta` e `Total consolidado`, com padrao atual em `Consolidada por tipo de conta`.
- O mesmo modo de composicao agora vale para saldo inicial e saldo final.
- Os filtros de composicao e vinculadas/indisponiveis deixaram de aparecer como metadados no cabecalho impresso.
- A sequencia documental do Balancete foi corrigida para abrir por saldo inicial, seguir por entradas e saidas, trazer o resumo operacional depois e fechar com a composicao do saldo final.
- Quando vinculadas/indisponiveis ficam ocultas, o Balancete nao mostra mais aviso textual sobre elas; nesse modo, o documento inteiro passa a representar apenas o saldo disponivel operacional.
- Transferencias entre saldo disponivel e saldo vinculado/indisponivel passam a aparecer no resumo operacional como movimentacao especifica de fronteira, sem virar receita ou despesa operacional.
- Permanecem como futuros apenas refinamentos adicionais de ordenacao, agrupamento, acabamento documental e eventuais modos extras justificados pelo uso real.

### Auditoria tecnica preparatoria

- Estado real da conta: `ContaFinanceira` possui base patrimonial cadastral implementada com tipo de conta, disponibilidade/vinculacao total e mensagem explicativa opcional.
- Cadastro de conta: `ContaFinanceiraForm`, `ContaFinanceiraListView`, `ContaFinanceiraCreateView`, `ContaFinanceiraUpdateView`, `ContaFinanceiraDeleteView`, `conta_form.html` e `conta_list.html` sao pontos diretos de impacto futuro.
- Base compartilhada: `montar_contexto_fechamento_periodo` encapsula a base reutilizada por Resumo, Prestacao/Fechamento e Balancete; a leitura patrimonial nao deve alterar essa base de calculo.
- Balancete: `BalanceteInstitucionalFinanceiroView` chama `montar_contexto_fechamento_periodo`, filtra composicoes documentais e envia `balancete_composicao_inicial`/`balancete_composicao_final` para `balancete_institucional.html`.
- Importacao/exportacao: a importacao auxiliar de contas e a exportacao de contas incluem `tipo_conta`, `disponibilidade` e `mensagem_indisponibilidade`; a importacao preserva planilha legada com defaults seguros.
- Testes existentes: foram acrescentados testes especificos de tipo/disponibilidade/mensagem, importacao nova/legada e exportacao auxiliar de contas.
- Recorte minimo recomendado agora: avaliar apenas modos avancados de exibicao patrimonial, se o uso real justificar, sem alterar a base de calculo.
- Nao alterar no primeiro recorte: lancamentos, Extrato, Fechamento/Prestacao, importacao/exportacao de lancamentos, permissoes, regras de transferencia, saldos e calculo financeiro.

### Regra de seguranca

- Nao criar calculo proprio para o Balancete patrimonial.
- Nao alterar comportamento atual de lancamentos, Fechamento/Prestacao, Extrato ou Balancete MVP.
- Implementar somente depois de nova microetapa funcional aprovada.

## 0.19. Checkpoint apos homologacao local do financeiro

Este bloco orienta a fila apos as auditorias, baixas documentais, correcoes funcionais e homologacoes locais recentes. Nao reabre itens ja homologados como pendencia ativa.

- Homologado localmente: listagem de lancamentos com filtro multi-contas, favorecido tecnico `TRANSFERENCIA ENTRE CONTAS` no Extrato, bloco `DIFERENCA A DETALHAR` no rateio e contas inativas em consultas historicas.
- HOMOLOGACAO PROGRESSIVA REALIZADA: os fluxos principais do financeiro foram testados durante as microetapas, com validacoes locais associadas as entregas; nao e necessario repetir agora uma homologacao ponta a ponta completa de tudo que ja foi conferido.
- Implementado com pendencias futuras ou acompanhamento de uso real: Balancete Institucional, importacoes/cadastros auxiliares, autenticacao/perfis/permissoes e refinamentos de relatorios impressos sujeitos a validacao por massa/volume real.
- Futuro real mantido: opcao visual do Extrato multi-contas para detalhar transferencias internas em duas linhas, tipo/disponibilidade de conta, frequencia/recorrencia por competencia, contratos/parcelas/recorrencias, anexos, tabelas personalizadas de controle e expansao visual/transversal progressiva.
- Proxima fase natural: uso real acompanhado do financeiro, com validacao de importacoes em planilhas historicas completas, relatorios impressos em volume real e rotina diaria da Casa; se houver urgencia operacional, escolher uma nova pendencia pequena e isolada.

## 0.18. Frente futura: tipo, disponibilidade de conta e composicao do Balancete

Este bloco registra nova frente gerencial/patrimonial levantada pela usuaria. Nao representa implementacao concluida.

1. **Tipo de conta financeira**
   - Classificacao: FRENTE FUTURA FUNCIONAL / REGRA GERENCIAL.
   - Prioridade documental: MEDIA.
   - Direcao: evoluir o cadastro de contas para classificar tipo de conta, com exemplos iniciais: conta corrente, conta poupanca, dinheiro/caixa, conta investimento, integralizacao de capital, conta vinculada/indisponivel e outros.
   - Observacao: avaliar cadastro proprio de tipos de conta para manter o sistema aberto a outras instituicoes, empresas e projetos futuros.

2. **Disponibilidade ou vinculacao da conta**
   - Classificacao: REGRA DE NEGOCIO / LEITURA GERENCIAL-PATRIMONIAL.
   - Prioridade documental: ALTA para desenho futuro.
   - Direcao: diferenciar conta ativa/inativa de conta disponivel/indisponivel. Ativa/inativa controla uso operacional em novos lancamentos; disponivel/indisponivel controla leitura gerencial do saldo.
   - Regra especifica: uma conta pode estar ativa para novos lancamentos e ainda assim ter saldo indisponivel/vinculado, conforme a natureza gerencial ou patrimonial.
   - Mensagem explicativa: prever campo opcional por conta para justificar indisponibilidade/vinculacao em relatorios. Se vazio, nada deve aparecer.

3. **Integralizacao de capital**
   - Classificacao: REGRA GERENCIAL / PATRIMONIAL.
   - Prioridade documental: ALTA para modelagem futura.
   - Direcao: integralizacao de capital nao deve ser tratada como despesa operacional nem como saldo livre para uso imediato; deve compor patrimonio financeiro de forma destacada como valor vinculado/indisponivel, fora do saldo operacional livre.

4. **Composicao do Balancete Institucional**
   - Classificacao: MELHORIA FUNCIONAL DE RELATORIO / IMPRESSAO.
   - Prioridade documental: MEDIA.
   - Direcao: evoluir o Balancete para permitir modos de composicao final: detalhado por conta, consolidado por tipo de conta, total consolidado e separado entre disponivel e indisponivel/vinculado.
   - Modo detalhado por conta: mostra cada conta individualmente.
   - Modo consolidado por tipo: soma contas do mesmo tipo independentemente do banco ou nome da conta; exemplos de grupos: conta corrente, poupanca, dinheiro/caixa, conta investimento, integralizacao de capital e conta vinculada/indisponivel.
   - Modo total consolidado: mostra apenas o total geral quando a usuaria quiser relatorio mais sintetico.
   - Modo disponivel x indisponivel/vinculado: separa saldo livre operacional de valores patrimoniais, vinculados ou indisponiveis.
   - Objetivo visual: reduzir poluicao e duplicacao entre fechamento consolidado e detalhamento, mantendo composicao por conta quando o usuario precisar conferir.
   - Regra de seguranca: o Balancete patrimonial nao deve ter calculo proprio divergente; deve reaproveitar a base do Fechamento/Prestacao e mudar apenas classificacao/apresentacao do saldo.
   - Pre-condicao: nenhuma implementacao desta frente deve iniciar antes de fechar a modelagem documental de tipo, disponibilidade, mensagem explicativa e modos de exibicao.

5. **Logo no Extrato impresso**
   - Classificacao: AJUSTE VISUAL DE RELATORIO / IMPRESSAO.
   - Prioridade documental: MEDIA.
   - Status: IMPLEMENTADO COM REFINAMENTO VISUAL / AGUARDANDO VALIDACAO VISUAL.
   - Achado: o Extrato usa o nome institucional no cabecalho impresso, mas nao renderiza `financeiro_shell_brand_logo_url` como `<img>`, diferente de Prestacao, Resumo e Balancete.
   - Correcao aplicada: o template do Extrato passou a reaproveitar a logo institucional via `<img>` quando configurada e manter o nome institucional como fallback quando nao houver logo; refinamentos complementares compactaram e reequilibraram o print, ajustando margem superior, contas selecionadas, hierarquia documental, contrato local de impressao e repeticao do cabecalho da tabela, sem alterar calculos.
   - Observacao: esta pendencia deve ser tratada separadamente da modelagem de tipo/disponibilidade de conta.

## 0.17. Balancete Institucional como relatorio proprio futuro

Este bloco registra a revisao da direcao conceitual anterior. A Prestacao/Fechamento atual permanece como relatorio analitico/gerencial ja validado; o Balancete Institucional nasceu como relatorio proprio em MVP e permanece com evolucoes futuras documentais/gerenciais. Nao representa frente totalmente concluida.

1. **Balancete Institucional**
   - Classificacao: PARCIALMENTE IMPLEMENTADO + AJUSTE VISUAL/DOCUMENTAL FUTURO.
   - Prioridade documental: MEDIA.
   - Direcao revisada: criar relatorio proprio chamado `Balancete Institucional`, sem substituir a Prestacao/Fechamento atual.
   - Base de calculo: reutilizar a mesma regra/base de calculo da Prestacao/Fechamento, evitando divergencia de resultado e evitando duplicar regra financeira em dois lugares diferentes.
   - Status tecnico: MVP funcional iniciado com rota, view, template proprio, link em Relatorios, filtros essenciais, reaproveitamento de `montar_contexto_fechamento_periodo` e duas assinaturas selecionaveis pelo cadastro existente; refinamento visual/documental inicial aplicado no cabecalho, abrangencia impressa e ocultacao padrao de contas zeradas.
   - Apresentacao: template/documento proprio, com fundo branco, linhas compactas, secoes numeradas, valores alinhados a direita, fechamento do saldo disponivel, composicao final do saldo e aparencia institucional.
   - Regras preservadas: manter receitas/despesas separadas, transferencias fora do resultado operacional e transferencias compondo saldo apenas quando necessarias conforme escopo de contas.
   - Impressao: priorizar uma pagina quando o volume permitir; quando o relatorio for grande, quebrar paginas de forma clara e organizada, sem assinatura ou blocos finais isolados de maneira ruim.
   - Assinaturas: o MVP permite selecao manual de assinaturas pelo cadastro existente; definicao de assinaturas padrao especificas para este documento permanece como ajuste futuro, se o uso real exigir.
   - Pendencias futuras vinculadas: tipo de conta, disponibilidade/vinculacao, separacao entre saldo disponivel e indisponivel e modos de composicao por conta/tipo/total consolidado.
   - Historico da decisao: a direcao anterior falava em evoluir a Prestacao/Fechamento para modelo tipo balancete; a direcao revisada mantem a Prestacao/Fechamento como relatorio analitico e separa o Balancete como documento proprio.
   - Baixa documental detalhada: o MVP do Balancete nao deve ser reaberto como pendencia de criacao do zero. Ficam baixados como entregues: relatorio proprio, mesma base de calculo da Prestacao/Fechamento, fundo branco/documental, secoes numeradas, saldo inicial, receitas, despesas, fechamento, composicao do saldo, assinaturas condicionais selecionaveis, ocultacao padrao de contas zeradas e tratamento de transferencias por escopo sem classifica-las como receita/despesa.
   - Aguardam validacao visual/uso real: margens, fonte, quebra de pagina, acabamento documental do PDF/print e capacidade de caber em uma pagina quando o volume permitir.
   - Permanecem como futuro/modelagem: tipo de conta, disponibilidade/vinculacao, mensagem explicativa de indisponibilidade, separacao entre saldo disponivel e indisponivel/vinculado, integralizacao de capital como valor patrimonial/vinculado, modos de composicao por conta/tipo/total consolidado e eventual assinatura padrao especifica do Balancete.

## 0.16. Pendencias documentadas apos correcao da edicao de contas

Este bloco registra pendencias levantadas pela usuaria para continuidade do financeiro. Nao representa implementacao concluida.

1. **Padronizacao do filtro de contas nas telas com selecao de contas**
   - Classificacao: MELHORIA DE UX + PADRONIZACAO TRANSVERSAL.
   - Prioridade documental: MEDIA.
   - Direcao: aplicar progressivamente o padrao visual/comportamental validado no filtro de contas do Extrato em outras telas que possuam selecao de contas, em microetapas separadas por tela ou conjunto minimo seguro.
   - Status: executado para as telas analiticas Resumo, Fechamento/Prestacao e Evolucao por categorias; listagem de lancamentos permanece em pendencia propria.

2. **Refinamento de impressao da Prestacao/Fechamento do periodo**
   - Classificacao: AJUSTE VISUAL DE RELATORIO / IMPRESSAO.
   - Prioridade documental: MEDIA.
   - Direcao: compactar margens, espacamentos e quebras de pagina do PDF/impresso da Prestacao/Fechamento, sem alterar calculos.
   - Status: executado ajuste de compactacao do modo print/PDF, sem alteracao de calculos.

## 0.15. Pendencias levantadas apos Extrato multi-contas

Este bloco registra pendencias novas levantadas pela usuaria apos a correcao do Fechamento/Prestacao e a implementacao do Extrato com multiplas contas. Nao representa implementacao concluida.

### Bugs / correcoes operacionais proximas

0. **Regra geral de identificadores-chave nos cadastros**
   - Classificacao: REGRA DE NEGOCIO + MELHORIA FUNCIONAL progressiva.
   - Prioridade documental: ALTA como diretriz; execucao incremental por cadastro.
   - Direcao: aplicar progressivamente a regra de nao duplicar identificadores-chave, como codigo, nome ou equivalentes, em contas financeiras, categorias/subcategorias, centros de custo e demais cadastros atuais ou futuros.
   - Status: diretriz implementada em `docs/REGRAS_NEGOCIO.md`; aplicacao pratica confirmada em favorecidos/pessoas financeiras. Demais cadastros permanecem em aplicacao progressiva futura.

1. **Favorecido duplicado por nome**
   - Classificacao: BUG / correcao operacional + REGRA DE NEGOCIO.
   - Prioridade documental: ALTA.
   - Direcao: impedir duplicidade por nome normalizado, preservando dados existentes e avaliando tratamento de duplicados ja cadastrados.
   - Status: implementado no cadastro/edicao e na importacao auxiliar de favorecidos por nome normalizado.

2. **Edicao de conta deve trazer saldo inicial e data do saldo ja cadastrados**
   - Classificacao: BUG / correcao operacional.
   - Prioridade documental: ALTA.
   - Direcao: ao abrir edicao de conta, os campos de saldo inicial e data do saldo devem aparecer preenchidos com os valores atuais.
   - Status: implementado no formulario de conta, com data em formato compativel com input HTML/date.

3. **Conta inativa em novos lancamentos e relatorios historicos**
   - Classificacao: REGRA DE NEGOCIO + correcao operacional.
   - Prioridade documental: ALTA.
   - Direcao: conta inativa nao deve aparecer para novos lancamentos, mas deve continuar disponivel em relatorios quando tiver movimento no periodo selecionado.
   - Status: IMPLEMENTADO; criacao/clone/autocomplete de lancamentos bloqueiam contas inativas, edicao historica preserva conta ja vinculada e filtros historicos passam a exibir contas inativas apenas quando houver movimento no periodo/escopo considerado.

4. **Favorecido em transferencia no Extrato**
   - Classificacao: MELHORIA DE UX + correcao operacional.
   - Prioridade documental: MEDIA.
   - Direcao: em lancamentos de transferencia, o Extrato deve apresentar o favorecido como `TRANSFERÊNCIA ENTRE CONTAS` quando nao houver favorecido operacional.
   - Status: IMPLEMENTADO na apresentacao do Extrato, sem alterar calculo, saldo, importacao/exportacao ou outros relatorios.

### Melhorias operacionais

5. **Diferenca restante no rateio**
   - Classificacao: MELHORIA FUNCIONAL + MELHORIA DE UX.
   - Prioridade documental: MEDIA.
   - Direcao: no fluxo de lancamento com rateio, mostrar o valor que ainda falta para fechar o valor total do documento.
   - Status: IMPLEMENTADO como apoio visual dinamico no formulario de novo lancamento com rateio e na edicao coordenada do grupo, sem alterar regra de validacao, saldos ou calculos.

6. **Filtro multi-contas na listagem de lancamentos**
   - Classificacao: MELHORIA FUNCIONAL + MELHORIA DE UX.
   - Prioridade documental: MEDIA.
   - Direcao: permitir selecionar mais de uma conta na listagem de lancamentos, reaproveitando a experiencia aprovada no Extrato multi-contas quando fizer sentido.
   - Status: IMPLEMENTADO; a listagem permite uma, varias ou todas as contas e inclui lancamentos cuja conta origem ou destino esteja no conjunto selecionado.

7. **Extrato multi-contas — opcao para detalhar transferencias internas**
   - Classificacao: FUTURO REAL / MELHORIA DE UX.
   - Prioridade documental: MEDIA.
   - Direcao: criar futuramente opcao visual no Extrato para exibir transferencias internas entre contas selecionadas em duas linhas operacionais: saida da conta origem e entrada na conta destino.
   - Uso previsto: conferencia operacional quando a usuaria quiser enxergar o transito entre contas dentro do proprio escopo selecionado.
   - Regra preservada: o comportamento padrao atual permanece correto para extrato consolidado; transferencias internas ao escopo selecionado se anulam, nao inflam saldo consolidado, nao alteram calculo financeiro e nao mudam a regra de transferencia.

### Frente futura grande

8. **Tabelas personalizadas de controle**
   - Classificacao: FRENTE FUTURA GRANDE.
   - Prioridade documental: FUTURA / BAIXA para execucao imediata.
   - Direcao: disponibilizar futuramente tabelas configuraveis para controles internos, com colunas personalizadas, tipos de coluna, formulas controladas entre colunas e linhas de controle.
   - Possivel evolucao: vinculo opcional com entidades existentes (financeiro, pessoas, categorias), apenas apos definicao de governanca dessa integracao.
   - Observacao de escopo: esta frente e separada da frente de frequencia por competencia e nao deve ser implementada agora.
   - Pre-condicao obrigatoria: abrir auditoria e SPEC propria antes de qualquer modelagem, model ou migration.
   - Riscos principais para fase futura: complexidade alta, risco de virar "Excel dentro do sistema", necessidade de limites de formula por seguranca, controle de permissoes, trilha de auditoria e estrategia de backup/exportacao.

## 0.13. Base analitica consolidada e retomada da padronizacao visual

- a tela `Evolucao por categorias` deixa de ser apenas uma entrega isolada e passa a ser a base atual do padrao analitico do sistema
- a estrutura consolidada dessa base fica registrada como:
  - titulo/contexto
  - filtro no topo da analise
  - KPIs
  - resultados
- nessa base, o filtro permanece no mesmo lugar estrutural quando resumido ou expandido
- a comparacao fica considerada consolidada para essa tela, incluindo:
  - `Periodo principal` e `Periodo comparativo`
  - reordenacao cronologica automatica
  - aviso discreto
  - barra do separado por magnitude absoluta
  - texto monetario com sinal real
  - tabela comparativa com semantica visual pela natureza do item
- a prioridade operacional volta a ser a propagacao controlada desse padrao para as demais telas analiticas do `financeiro`
- ordem recomendada de propagacao:
  1. `Resumo`
  2. `Extrato`
  3. `Prestacao de contas`
- observacao:
  - esta secao registra a ordem correta de continuidade
  - nao significa que `Resumo`, `Extrato` e `Prestacao de contas` ja estejam repadronizados neste mesmo contrato visual

## 0.14. Frente futura de controle de frequencia/recorrencia por competencia

- fica registrada como nova frente futura do `financeiro` a camada de controle de frequencia/recorrencia orientada por competencia
- diretriz estrutural da frente:
  - combinar `favorecido/pessoa recorrente` + `subcategoria` como eixo principal de controle da recorrencia
  - usar competencia explicita como base oficial da frequencia
  - nao inferir frequencia apenas pela data do lancamento
  - sugerir automaticamente meses/competencias em aberto
  - permitir competencias futuras
  - permitir correcao manual da competencia
  - manter a frequencia independente do valor exato pago
  - estruturar a base de forma generica para outros recorrentes, como contas de consumo
- entregaveis futuros previstos dessa frente:
  - relatorio gerencial em modo `matriz mensal com valores por competencia`
  - relatorio gerencial em modo `matriz mensal sem valores`, apenas com indicador visual de frequencia
  - `Termo de quitacao em lote por favorecido`, trazendo:
    - competencias feitas ou nao
    - valor medio contribuido
    - valor total no periodo
    - periodo selecionado

## 0.12. Evolucao por categorias

- a frente de `relatorio grafico de evolucao por categorias` deixou de ser apenas ideia futura e passou a ter primeira entrega funcional no `financeiro`
- foi criada uma tela propria em `Relatorios` para acompanhar a evolucao mensal de categorias/subcategorias selecionadas
- filtros entregues na versao atual:
  - `data inicial`
  - `data final`
  - `data inicial` e `data final` do `periodo comparativo`, em preenchimento opcional
  - controle de escopo entre `categorias` e `subcategorias`
  - selecao multipla contextual conforme o escopo
  - selecao opcional de `contas`
  - `modo analitico` do grafico
  - `forma de leitura` (`consolidado` / `separado`)
  - `granularidade` (`dias` / `meses` / `trimestres` / `anos`)
  - `mostrar valores no grafico`
- modos entregues:
  - `Evolucao de categorias selecionadas`
  - `Comparativo entrada x saida`
  - `Comparacao entre periodos`
- regra consolidada nesta versao:
  - consolidacao mensal por `data_pagamento`, com fallback para `data_competencia`
  - `Categorias` listam apenas categorias pai e podem agregar automaticamente as subcategorias lancaveis
  - `Subcategorias` listam apenas subcategorias, com indicacao explicita da categoria pai
  - `Consolidado` soma os itens escolhidos em uma unica serie
  - `Separado` mostra uma serie por item selecionado
  - o modo `Comparativo entrada x saida` preserva os nomes reais das categorias/subcategorias escolhidas
  - a comparacao entre periodos e ativada automaticamente quando o `Periodo comparativo` e preenchido
  - a saida da comparacao passou a incluir `Periodo principal`, `Periodo comparativo`, diferenca absoluta e variacao percentual com tratamento seguro quando a base e zero
  - com `Periodo comparativo` preenchido e `Leitura = Consolidado`, a comparacao passa a usar um unico grafico de linhas com duas series (`Periodo principal` e `Periodo comparativo`)
  - com `Periodo comparativo` preenchido e `Leitura = Separado`, a tabela comparativa passa a ser a leitura principal para evitar poluicao visual por excesso de linhas, com apoio visual discreto em barras horizontais agrupadas por item
  - no grafico de apoio do comparativo separado, a tela exibe ate 8 itens priorizados por maior diferenca absoluta entre os periodos, mantendo a lista completa na tabela comparativa
  - a troca de `Escopo` atualiza imediatamente o seletor visivel e a busca, sem exigir submit apenas para trocar a interface
  - o submit de `Atualizar grafico` recalcula efetivamente grafico, KPIs e tabela de apoio
- entrega visual atual:
  - grafico SVG server-side
  - KPIs do periodo
  - tabela mensal de apoio recolhida por padrao
  - busca no seletor multiplo
  - acao `Imprimir relatorio`
  - toggle textual explicito para mostrar/ocultar a tabela mensal
- consolidacao visual/estrutural posterior:
  - a tela ficou madura como base atual do padrao analitico do sistema
  - o filtro permanece no topo da analise no mesmo lugar estrutural, resumido ou expandido
  - a hierarquia consolidada passa a ser `titulo/contexto -> filtro -> KPIs -> resultados`
- backlog remanescente relacionado:
  - avaliar se a tela deve ganhar exportacao futura da tabela mensal ou apenas permanecer como consulta visual
  - avaliar, por uso real, se convem expandir a comparacao para mais de dois agrupamentos operacionais alem de `entrada x saida`
  - avaliar se a comparacao entre periodos deve ganhar tabela comparativa mais rica ou exportacao propria em etapa futura

## 0.11. Trava de seguranca para importacoes por dominio preenchido

- a central de importacoes do `financeiro` passou a barrar importacoes quando o dominio de destino ja possui registros
- dominios cobertos:
  - `contas`
  - `favorecidos`
  - `categorias/subcategorias`
  - `centros de custo`
  - `lancamentos`
- regra consolidada:
  - importacao so pode acontecer em base vazia daquele dominio
  - se houver registros existentes, a operacao e bloqueada antes da validacao/conteudo da planilha
  - o bloqueio e acompanhado de mensagem clara indicando exatamente qual dominio precisa ser limpo ou redefinido
- essa trava nao substitui os fluxos de reset/limpeza ja existentes; ela passa a reforcar operacionalmente que nova carga deve acontecer apenas sobre dominio vazio
- backlog remanescente relacionado:
  - evoluir futuramente a experiencia de preflight/importacao para informar de forma ainda mais visivel o estado de preenchimento de cada dominio antes do upload

## 0.5. Execucao atual da frente de planilha comum com ate 5 rateios na mesma linha

- a frente antes mantida como futura de `exportacao/importacao comum de lancamentos com suporte a rateio em planilha` deixou de ser backlog e entrou em execucao real
- a decisao mais recente do usuario substituiu o contrato intermediario por multiplas linhas pelo novo contrato principal:
  - `1 linha = 1 documento`
  - ate `5` blocos de rateio na mesma linha
  - `valor_total_documento = soma dos blocos preenchidos`
- o contrato comum atual da planilha de lancamentos passou a cobrir:
  - lancamentos simples
  - transferencias simples
  - lancamentos com rateio em ate `5` blocos por documento
- a exportacao comum da listagem continua respeitando filtros, mas agora sai no mesmo contrato de `Modelo` + `Instrucoes` usado pela importacao
- a importacao comum continua transacional e sem criacao automatica de cadastros auxiliares, mas agora reconstroi lancamentos rateados diretamente no fluxo funcional do usuario
- compatibilidade preservada:
  - o layout simples legado continua aceito na importacao para nao quebrar arquivos antigos ja preparados
- limite conhecido e deliberado do fluxo comum:
  - grupos com mais de `5` linhas rateadas passam a ser bloqueados com mensagem clara na exportacao/importacao comum
  - nesses casos, o caminho tecnico de `backup/restauracao` continua sendo a excecao operacional segura
- backlog remanescente relacionado a esta frente:
  - preview mais rico antes de gravar
  - tratamento avancado de duplicidades
  - importacao parcial continua fora de escopo
  - refinamentos futuros de UX/mensagens da central conforme uso real

## 0.6. Refinamento de usabilidade da listagem principal de lancamentos

- a `lancamento_list` ganhou configuracao inicial de colunas para melhorar o uso real com a sidebar expandida, sem depender apenas de ajustes de largura em CSS
- o padrao inicial ficou enxuto, com `Data pagamento`, `Tipo`, `Descricao` e `Valor` como colunas essenciais da grade, alem de selecao/acoes quando as permissoes aplicarem
- campos complementares como `Favorecido`, `Conta origem`, `Conta destino`, `Status`, `Categoria`, `Centro de custo`, `Data competencia`, `Documento` e `Observacoes` passaram a poder ser exibidos/ocultados e ordenados manualmente
- a preferencia atual fica preservada em sessao, por ser a menor solucao segura sem criar estrutura nova de banco nesta etapa
- backlog futuro relacionado:
  - avaliar persistencia permanente por usuario em banco caso a configuracao de colunas precise sobreviver de forma mais robusta entre sessoes/navegadores
  - avaliar UI mais rica de ordenacao, como drag-and-drop, apenas se o uso real justificar

## 0.7. Novo bloco operacional: cadastros, lancamentos e extrato (lotes)

Diretriz geral:
- registrar itens de uso real em lotes coerentes, sem misturar tudo no mesmo patch

Itens levantados:
1. remover `Importar` da tela de lancamentos (importacao fica centralizada no menu)
2. gerar codigo automatico tambem nos demais cadastros, sem repetir codigo existente
3. permitir digitacao de valores monetarios sem virgula, com mascara pt-BR
4. cadastrar novo favorecido direto na tela de lancamentos, mantendo dados ja preenchidos
5. recibo em lote por favorecido, consolidando descricoes no mesmo recibo
6. checkbox `Exibir observacao` no extrato
7. corrigir protecao indevida ao excluir favorecido/pessoa apos desvinculo

Lotes definidos:
- Lote 1 (prioritario): itens 1, 3, 6 e 7 (executado)
- Lote 2: itens 2 e 4 (executado)
- Lote 3: item 5 (executado)

Entrega no Lote 2:
- geracao automatica de codigo quando vazio para `Favorecidos` e `Centros de custo`, preservando codigo manual
- fluxo rapido de `Novo favorecido` no lancamento preservando dados e retornando com o favorecido criado selecionado

Entrega no Lote 3:
- acao de recibo em lote na listagem de lancamentos
- validacao obrigatoria de mesmo favorecido, sem rateio e apenas receitas
- recibo unico consolidando descricoes e valor total

Observacao:
- `Exportacao` segue contextual nas listagens; `Importacao` permanece centralizada na pagina de importacoes do modulo

## 0.8. Historico por favorecido

- a frente de `historico por favorecido` foi executada como pagina operacional propria dentro do modulo `financeiro`
- a tela permite consultar os lancamentos vinculados a um favorecido, usando `data_pagamento` como data operacional principal e fallback para `data_competencia`
- filtros entregues: data inicial, data final, tipo, status, conta e busca textual por descricao ou documento
- totalizadores entregues: total geral, receitas, despesas, quitado e em aberto, sempre sobre o resultado filtrado
- acesso natural: acao `Historico` na listagem de `Favorecidos financeiros`
- nao foram incluidos nesta etapa: exportacao especifica do historico

## 0.9. Refinamento operacional de transferencias em relatorios

- `Resumo` e `Prestacao de Contas` passaram a oferecer opcao `Exibir transferencias`
- comportamento padrao preservado: transferencias continuam ocultas da leitura principal quando a opcao esta desligada
- quando a opcao esta ligada, transferencias quitadas do periodo aparecem em bloco proprio para conferencia operacional
- o bloco de transferencias inclui total movimentado e totalizadores separados de entrada e saida para leitura de aplicacoes/resgates entre contas
- regra mantida: transferencias nao entram como receitas nem despesas e nao alteram os totais principais desses relatorios
- o filtro de contas considera transferencias em que a conta selecionada aparece como origem ou destino
- na `Prestacao de Contas`, a leitura do universo de contas foi explicitada: o saldo consolidado considera apenas as contas selecionadas no relatorio; transferencias entre esse universo e contas fora dele, como integralizacao ou outras contas nao operacionais, alteram o saldo das contas exibidas sem virar receita ou despesa
- reconciliacao consolidada da `Prestacao de Contas`:
  - `Saldo final consolidado = saldo inicial consolidado + receitas do periodo - despesas do periodo + entradas de outras contas da instituicao - saidas para outras contas da instituicao`
  - essa reconciliacao vale tanto para saida de conta selecionada para conta nao selecionada quanto para entrada vinda de conta nao selecionada para conta selecionada
- backlog remanescente: revisar, por uso real, se outros relatorios futuros devem adotar o mesmo padrao opcional de exibicao de transferencias

## 0.10. Documentos por favorecido a partir da listagem de lancamentos

- a direcao anterior de `relatorio anual por favorecido` como tela principal foi substituida por acoes documentais centralizadas na `lancamento_list`
- o relatorio anual deixou de ser fluxo exposto em menu/listagens/historico; rota, view e template foram removidos para evitar redundancia operacional
- acoes documentais consolidadas na listagem:
  - `Recibos em lote`: acao baseada na selecao manual atual da listagem, agrupando automaticamente por favorecido e gerando um bloco/pagina por favorecido quando necessario
  - `Termo anual de quitacao`: acao baseada no resultado filtrado atual da listagem, agrupando automaticamente por favorecido e gerando um ou varios termos no mesmo documento continuo
- regra atual dos recibos em lote: categoria deixou de ser elemento relevante de leitura do recibo, nao aparece no documento e nao bloqueia a emissao quando houver categorias diferentes
- regra atual dos recibos em lote: itens com a mesma descricao exata dentro do mesmo favorecido, inclusive oriundos de rateio, podem ser consolidados em uma unica linha documental com soma apenas dos valores dos lancamentos selecionados naquele grupo
- quando a consolidacao reunir datas ou documentos diferentes, o recibo sinaliza isso de forma compacta no proprio item (`Datas diversas`, `Doc. diversos`)
- os recibos em lote reaproveitam a mesma peca documental do recibo oficial ja existente e usam fallback institucional comum, sem depender de mensagem especifica por categoria
- regra do termo anual nesta primeira versao: exige filtro de periodo com data inicial e final dentro do mesmo ano e, internamente, considera apenas receitas quitadas com favorecido e sem rateio, ignorando automaticamente despesas, transferencias, receitas em aberto e demais itens incompativeis
- o termo anual em uso atual prioriza leitura documental para o usuario, com subtitulo mais claro, identificacao simples do favorecido, texto introdutorio institucional, tabela com `Data`, `Descricao`, `Documento` e `Valor` e fechamento com assinatura institucional
- na `Prestacao de Contas`, a leitura operacional das movimentacoes entre universos passou a usar linguagem mais humana: `Entradas de outras contas da instituicao` e `Saidas para outras contas da instituicao`
- permanecem futuros: PDF, anexos, assinatura final juridica, texto formal completo do termo anual, contratos, parcelas, recorrencia e refinamentos documentais apos validacao visual real

## 0.4. Ultimo bloqueio do reset real: assinaturas, configuracao institucional e regras automaticas

- depois de resolver `rateios` e `lancamentos simples` legados, o reset real ainda ficou bloqueado por uma ultima lacuna do pacote operacional
- o bloqueio era objetivo:
  - o comando de reset apagava `AssinaturaInstitucional`
  - o comando de reset apagava `ConfiguracaoInstitucional`
  - o comando de reset apagava `RegraLancamentoFinanceiro`
  - o pacote de reconstrucao ainda nao tinha trilha propria para esses itens
- a estrategia minima e segura adotada foi mista:
  - `AssinaturaInstitucional` passa a ser preservada fora do reset
  - `ConfiguracaoInstitucional` passa a ser preservada fora do reset
  - `RegraLancamentoFinanceiro` continua entrando no reset, mas passa a contar com backup/restauracao tecnica separados em `JSON`
- motivo da decisao:
  - `assinaturas` e `configuracao institucional` sao suporte documental e nao precisam ser zeradas para reiniciar a base transacional
  - `regras automaticas` dependem de cadastros que o reset precisa apagar; preserva-las fora do reset gera conflito estrutural e invalida a limpeza do dominio
- implicacao pratica:
  - o pacote operacional agora precisa incluir tambem o backup tecnico das `regras`
  - com isso, o reset real volta a ficar tecnicamente liberado
- a frente futura continua separada e visivel:
  - evolucao do layout comum de exportacao/importacao de lancamentos com suporte a `rateio` por grupo em planilha
  - essa evolucao futura nao substitui a trilha tecnica hoje adotada para restauracao de `rateios` e `regras`

## 0.1. Bloqueio real do reset e estrategia tecnica para rateios

- o reset destrutivo real do `financeiro` ficou bloqueado quando a auditoria pratica confirmou que a base local possui lancamentos `com_rateio=True` e grupos de rateio que nao podem ser recompostos pela importacao comum ja entregue
- isso nao invalida a importacao comum atual; apenas registra seu limite atual:
  - ela importa lancamentos simples
  - ela nao recompõe `grupo_rateio` como documento agrupado
- para nao abrir uma grande nova frente na importacao funcional, foi adotada a menor trilha segura e reversivel:
  - backup tecnico separado dos rateios em `JSON`
  - restauracao tecnica separada dos rateios, transacional e com confirmacao explicita
- essa solucao passa a ser a ponte operacional para permitir reset futuro sem perda estrutural dos grupos rateados
- importante:
  - isso nao significa que a importacao funcional comum de lancamentos tenha ganho suporte a rateio
  - esse suporte continua fora do fluxo comum do usuario e deve seguir visivel como limite conhecido do roadmap ate decisao futura
- em decisao posterior, essa limitacao passou a ficar registrada como frente futura explicita do backlog:
  - exportacao comum de lancamentos com suporte a rateio por grupo em planilha
  - importacao comum de lancamentos com suporte a reconstrucao de rateio por grupo em planilha
- essa frente continua futura mesmo com a existencia do backup/restauracao tecnica separado; o caminho tecnico resolve reconstrucao operacional da base, mas nao substitui a evolucao funcional do layout comum

## 0.2. Novo bloqueio real encontrado no preflight do reset

- ao preparar a execucao operacional real do reset, o projeto gerou o pacote definitivo de reconstrucao e rodou um preflight com rollback
- esse preflight confirmou que os cadastros auxiliares atuais recompõem normalmente, mas revelou legado invalido tambem entre `lancamentos simples`
- o bloqueio objetivo ficou:
  - `5` linhas de lancamentos simples nao passam pelo contrato atual da importacao comum
  - parte dessas linhas usa `Categoria` pai (`Cantina`, `Estrutura`) em despesa
  - ao menos uma linha usa categoria de `receita` (`Doacao`) em um lancamento do tipo `despesa`
- consequencia pratica:
  - o reset destrutivo real permanece adiado ate existir estrategia fechada para esses legados de lancamento simples
  - essa estrategia pode passar por saneamento de dados, trilha tecnica especifica ou outra decisao controlada em microetapa propria

## 0.3. Bloqueio dos lancamentos simples saneado

- em microetapa posterior, o projeto optou por saneamento dirigido da base atual, preservando o contrato da importacao comum
- resultado:
  - os `5` lancamentos simples bloqueadores foram corrigidos
  - um novo pacote de reconstrucao foi gerado
  - o novo preflight completo com rollback passou com sucesso
- implicacao pratica:
  - o reset destrutivo real deixa de ficar bloqueado por `rateios` e tambem deixa de ficar bloqueado por `lancamentos simples` legados
  - a proxima microetapa operacional volta a ser a execucao real do procedimento de backup/reset/reconstrucao
- a frente futura continua visivel e separada:
  - evoluir exportacao comum de lancamentos para suportar `rateio` por grupo em planilha
  - evoluir importacao comum de lancamentos para reconstruir `rateio` por grupo em planilha

## 0. Reajuste recente de escopo operacional

- a decisao consolidada mais recente desta frente e:
  - importacoes auxiliares ficam centralizadas no financeiro geral
  - exportacoes permanecem nas telas/listagens especificas para respeitar filtros
  - `assinaturas` ficam fora da frente atual de importacoes auxiliares
- no estado atual do repositorio, a central de importacoes do financeiro ja cobre:
  - importacao de lancamentos
  - importacao auxiliar de contas
  - importacao auxiliar de pessoas
  - importacao auxiliar de centros de custo
  - importacao auxiliar de categorias/subcategorias
- backlog remanescente desta frente deve continuar visivel neste roadmap, sem rebaixar o que ja foi entregue no repositorio
- auditoria documental/tecnica posterior classificou a frente como IMPLEMENTADO COM PENDENCIAS FUTURAS / AGUARDANDO HOMOLOGACAO:
  - implementado no codigo: central de importacoes, modelos XLSX, importacao/exportacao comum de lancamentos, cadastros auxiliares, trava de dominio preenchido, validacao estrutural, validacao linha a linha, relatorio de inconsistencias e gravacao transacional all-or-nothing
  - implementado no contrato comum: lancamentos simples, transferencias simples e rateio em ate `5` blocos na mesma linha
  - permanecem futuras: preview antes de gravar, importacao parcial, tratamento avancado de duplicidades, preflight mais visivel e fluxo guiado para importacao historica ampla
  - permanece aguardando homologacao: carga real com planilhas historicas da usuaria e massa completa de cadastros auxiliares

## 1. Escopo inicial mapeado

### Cadastros principais
- contas financeiras
- centros de custo
- pessoas financeiras
- categorias financeiras

### Lancamentos financeiros
- receitas
- despesas
- transferencias entre contas
- filtros operacionais
- numeracao de documento
- validacoes condicionais

### Contratos, parcelas e recorrencia
- contratos a pagar
- contratos a receber
- geracao de parcelas
- recorrencia de lancamentos previstos

### Recibos
- emissao simples
- vinculo com lancamentos
- historico de recibos
- bloco historico inicial do tema; a base do recibo ja foi entregue e refinada no repositorio atual

### Relatorios e consultas
- resumo por periodo
- prestacao de contas
- consultas historicas por favorecido
- relatorios anuais
- balancete
- exportacao futura de consultas/listagens de lancamentos em CSV/Excel, respeitando filtros aplicados, e PDF apenas quando houver sentido documental

### Extrato e saldo
- saldo inicial por conta
- saldo atual calculado
- extrato por conta
- saldo anterior por periodo

### Importacao de historico
- importacao de planilha historica
- importacao futura em massa de lancamentos com modelo de arquivo, validacao previa, pre-visualizacao e tratamento de duplicidades
- na importacao futura, deve existir acao para baixar planilha modelo no layout proprio do sistema, com colunas e ordem esperadas para preenchimento e importacao
- saneamento de dados importados
- conciliacao inicial de base

### Usabilidade e interface
- autocomplete
- filtros uteis
- formularios condicionais
- impressao de relatorios
- fluxo operacional sem dependencia do admin

### Operacao e manutencao
- documentacao funcional
- etapas incrementais rastreaveis
- validacoes defensivas
- revisao de regras de negocio por tela

## 2. O que ja esta implementado

### Cadastros
- CRUD de contas financeiras
- CRUD de centros de custo
- CRUD de pessoas financeiras
- CRUD de categorias financeiras

### Lancamentos
- CRUD de lancamentos financeiros
- filtros por descricao, numero do documento, tipo e status
- filtros operacionais por data inicial, data final, conta, pessoa e categoria
- `numero_documento` manual quando informado pelo usuario
- `numero_documento` automatico quando vier vazio
- validacao para impedir repeticao de `numero_documento` em cadastro e edicao
- primeira versao de `Lancamento com rateio` sem documento pai, com `grupo_rateio` e validacao por `valor total do documento`
- segunda versao do rateio com redirecionamento estavel no create, `tipo` padrao em `receita`, sugestao automatica de `data_competencia` a partir de `data_pagamento` e consolidacao de categorias repetidas antes da gravacao
- a repeticao legitima de `numero_documento` no rateio ficou restrita a replicacao interna entre linhas do mesmo `grupo_rateio`, sem liberar coincidencia com documento independente
- a validacao do rateio agora tambem precisa preservar, na edicao individual, o mesmo `numero_documento` compartilhado pelas linhas do grupo

### Regras condicionais de transferencia
- transferencia nao exige pessoa
- transferencia nao exige categoria
- transferencia nao exige centro de custo
- transferencia exige conta de destino
- conta e conta de destino nao podem ser iguais
- conta de destino so pode ser usada em transferencia
- formulario limpa campos irrelevantes em transferencia
- listagem pode exibir `Transferencia entre Contas` quando nao houver pessoa

### Validacoes ja implantadas
- pessoa obrigatoria em receita e despesa
- categoria obrigatoria em receita e despesa
- categoria pai nao pode ser usada em lancamento; vinculacao passou a exigir subcategoria/categoria filha
- data de pagamento nao pode ser anterior a data de competencia
- erros de regra retornam ao formulario
- validacao de transferencia ocorre antes da gravacao
- duplicidade de `numero_documento` retorna erro claro no formulario

### Saldo inicial, extrato e saldo
- saldo inicial por conta
- data do saldo inicial obrigatoria
- saldo atual calculado em tempo de execucao
- extrato por conta
- extrato com filtro por periodo
- calculo de saldo anterior
- extrato e saldo real considerando apenas lancamentos efetivos
- consolidacao visual de rateios no extrato por `grupo_rateio`, com leitura do valor total do documento

### Resumo e prestacao de contas
- resumo consolidado por periodo
- prestacao de contas por periodo
- filtro por contas selecionadas
- agrupamento por categoria
- agrupamento de despesas por centro de custo
- controle de exibicao do bloco de centro de custo
- composicao inicial e final por conta
- acao de impressao em resumo e prestacao de contas
- exibicao curta das categorias quando a natureza ja estiver clara pelo contexto do relatorio

### Melhorias de UX ja feitas
- autocomplete real com busca por contem
- comportamento condicional do formulario de lancamento
- historico simples com os ultimos 5 lancamentos do favorecido no formulario de lancamento
- acao `Clonar` diretamente na secao de ultimos lancamentos da pessoa dentro do formulario de lancamento, reaproveitando o fluxo ja existente de clone comum e de clone por grupo rateado
- filtro do campo `Categoria`/`Subcategoria` pelo `tipo` selecionado no lancamento, exibindo apenas subcategorias de despesa em `despesa` e apenas subcategorias de receita em `receita`, com preservacao do comportamento de `transferencia`
- fase 1 de edicao em lote na listagem de lancamentos, com selecao multipla por checkbox, marcar todos os itens visiveis, exclusao em lote com confirmacao e alteracao transacional de status dos selecionados, ainda sem expandir para outros cadastros
- agrupamento visual de rateios na listagem de lancamentos como uma unica linha-resumo expandivel por `grupo_rateio`, com leitura das linhas internas sob demanda, valor total consolidado no resumo e selecao em lote mirando o grupo inteiro, sem alterar o modelo fisico nem outras telas nesta etapa
- padronizacao visual da coluna de acoes na listagem de lancamentos por slots fixos, com `Recibo` contextual apenas quando aplicavel, descricoes truncadas com reticencias e tooltip para leitura rapida, e ordenacao padrao por data principal mais recente primeiro
- fases 1, 2 e 3 da importacao/exportacao de lancamentos com pagina propria focada em upload e link de baixar planilha modelo XLSX com abas `Modelo` e `Instruções`, validacao estrutural do XLSX enviado por extensao/formato/abas/cabecalhos, validacao de conteudo linha a linha da aba `Modelo` contra cadastros ja existentes, importacao orientada prioritariamente a datas em `dd/mm/aaaa` com tolerancia interna tambem a `AAAA-MM-DD`, mensagens com rotulos amigaveis, resumo de linhas lidas/validas/importadas/com erro, download de relatorio XLSX de inconsistencias quando ha erros e importacao real all-or-nothing quando todas as linhas estao validas, primeira exportacao real simples em XLSX acionada pela propria listagem de lancamentos com respeito aos filtros ativos, cabecalhos amigaveis ao usuario, datas em `dd/mm/aaaa` e valores com virgula decimal, e ajuda rapida operacional, ainda sem preview avancado de linhas, criacao automatica de cadastros auxiliares, importacao parcial, tratamento avancado de duplicidades ou exportacao avancada com variacoes
- a mesma central do financeiro agora tambem cobre a importacao auxiliar real de `contas`, `pessoas`, `centros de custo` e `categorias/subcategorias`, reaproveitando planilhas-base XLSX com abas `Modelo` e `Instrucoes`, mantendo gravacao transacional por arquivo e deixando `assinaturas` fora desta frente
- MVP de regras automaticas no cadastro de lancamento comum, com sugestoes por digitacao em `descricao`, `pessoa` apenas como refinador opcional, preenchimento automatico por selecao da sugestao e check explicito para salvar o lancamento atual como nova regra futura
- recibo em HTML imprimivel a partir do lancamento, com refinamentos posteriores de conteudo, assinatura, configuracao institucional e impressao
- mensagens de erro mais claras em campos obrigatorios
- layout mais compacto nas tabelas
- impressao refinada para extrato e prestacao de contas
- validacao manual real de impressao de `Extrato`, `Resumo` e `Prestacao de Contas` concluida com sucesso, sem necessidade de ajuste adicional nesta microetapa
- menu proprio para extratos, resumo e prestacao de contas

## 3. O que ja existe, mas ainda pode ser refinado

- comportamento de transferencia em todas as telas e relatorios
- UX do formulario de lancamento em casos limite
- base inicial da edicao coordenada do rateio ja implementada com view e formulario proprios do grupo, ainda pendente de refinamentos para a experiencia final
- modelagem documental mais rica do rateio, se necessario em etapa posterior
- acabamento operacional do rateio em edicao individual e leitura do grupo nas telas ja existentes
- estrategia aprovada para futura edicao coordenada do grupo rateado com view e formulario proprios, dados comuns em bloco e salvamento transacional
- regularizacao eventual de bases antigas de rateio sem `grupo_rateio` valido, caso precisem entrar na leitura consolidada do extrato
- a obrigatoriedade de `data_pagamento` ja foi consolidada no nivel de validacao da aplicacao; eventual endurecimento futuro do campo no banco depende apenas de estrategia segura para bases legadas
- expansao futura da auditoria de alteracoes no financeiro para alem de `LancamentoFinanceiro` e `ContaFinanceira`, ampliando o que ja existe para outras entidades do modulo e mantendo model proprio sem `signals`
- refinamentos futuros de leitura para a tela de auditoria de `LancamentoFinanceiro`, alem dos filtros simples ja implementados
- consistencia visual do tratamento de transferencia
- refinamento visual transversal do modulo financeiro para melhorar largura de campos, distribuicao de colunas, densidade de filtros, quantidade de informacao visivel por tela, melhor aproveitamento horizontal em zoom 100% e consistencia visual entre telas, agora oficialmente iniciado pela base compartilhada e pelas telas de listagem/formulario de lancamentos
- refinamentos futuros do shell visual do `financeiro` e da sidebar ja implantada, guiados por uso real e sem reabrir troca estrutural ampla da navegacao
- consolidacao futura de componentes visuais compartilhados do modulo, como cabecalho de pagina, bloco de filtros, card padrao, KPI, tabela e formulario
- telas de impressao, PDF e recibo ficam fora da primeira onda dessa padronizacao estrutural
- validacoes defensivas adicionais em fluxos operacionais
- extrato com mais contexto operacional sem poluir a tela
- filtros da listagem de lancamentos com melhorias de usabilidade
- evolucao futura da listagem de lancamentos com mostrar/ocultar colunas, redimensionamento manual de colunas e preferencias persistentes de visualizacao por usuario ou navegador, tratada como refinamento de UX e nao como regra de negocio
- acabamento documental futuro complementar dos relatorios impressos, apenas apos uso real, especialmente quando entrarem logo institucional e configuracao avancada de assinaturas
- evolucao futura da identidade institucional nos relatorios do financeiro, incluindo uso controlado de logo quando fizer sentido documental sem poluir a leitura operacional
- evolucao futura da logica de assinaturas em relatorios do financeiro:
  - permitir mais de uma assinatura cadastrada por relatorio que tenha assinatura
  - permitir configurar em cada relatorio se mostra assinatura
  - permitir configurar quais assinaturas ativas devem aparecer em cada relatorio
- item informativo futuro na tela de lancamentos, com simbolo `i` e historico de cadastro/alteracoes do documento ou lancamento quando houver ganho operacional real
- mapeamento e revisao futura das mensagens visiveis ao usuario no modulo `financeiro`, em alinhamento com a futura frente transversal do projeto
- integracao futura do `financeiro` com autenticacao e controle de acesso por usuario quando a frente estrutural do projeto for iniciada
- definicao futura de permissoes por acao dentro do `financeiro`, sem isolar essa governanca do restante do sistema
- convivencia futura do `financeiro` com administracao global centralizada de usuarios, perfis e permissoes, preservando a separacao entre cadastros globais e cadastros especificos do modulo
- POC controlada de uso de template pronto no shell do `financeiro`, apenas como experimento comparativo e sem adocao abrupta no projeto

## 4. O que ainda falta implementar

### Alta prioridade
- contratos a pagar e a receber
- parcelas
- recorrencia
- anexos de comprovantes

### Media prioridade
- balancete padrao
- importacao de planilha historica
- evolucao futura da importacao para oferecer preview/validacao detalhada antes de gravar, tratar duplicidades de forma mais rica, refinar a importacao auxiliar centralizada ja entregue e avaliar eventual importacao parcial apenas em fase posterior
- evolucoes futuras especificas do bloco de recibos ja entregue

## 5. Fila restante reorganizada por prioridade pratica

Observacao:
- esta secao reorganiza a fila restante sem substituir nem apagar as secoes `3` e `4`
- os itens abaixo permanecem futuros; a reorganizacao serve apenas para orientar prioridade pratica de execucao

### Imediato
- proxima frente funcional prioritaria do sistema: `permissoes/autenticacao` com configuracao hierarquica de perfis por `Modulo` > `Tela/Recurso` > `Acao`, em camada transversal do projeto e nao como ajuste isolado do `financeiro`
- na abertura real da frente de `permissoes/autenticacao`, foi criada a primeira versao de `docs/MATRIZ_PERMISSOES.md` como documento proprio de mapeamento de permissoes; as proximas subetapas devem revisar essa matriz com auditoria humana, fechar a regra de exibicao de menus/botoes/endpoints por perfil e so depois iniciar a implementacao tecnica em codigo
- auditoria de UX entre telas existentes e consolidacao de um padrao visual/funcional transversal em `docs/PADRAO_UX_SISTEMA.md`, com padronizacao progressiva das melhorias ja aprovadas no `financeiro` para outros modulos
- refinamentos futuros do shell visual do `financeiro` e do menu superior atual, guiados por uso real e sem reabrir troca estrutural ampla da navegacao
- refinamento futuro do menu superior para ficar mais leve, mais coerente com o tema e menos pesado visualmente, evitando a sensacao de duplicacao de camadas
- consolidacao futura de componentes visuais compartilhados do modulo, como cabecalho de pagina, bloco de filtros, card padrao, KPI, tabela e formulario
- refinamento visual transversal do modulo financeiro para melhorar largura de campos, distribuicao de colunas, densidade de filtros, quantidade de informacao visivel por tela, melhor aproveitamento horizontal em zoom 100% e consistencia visual entre telas, agora oficialmente iniciado pela base compartilhada e pelas telas de listagem/formulario de lancamentos
- auditoria e aplicacao incremental do novo padrao transversal de UX/comunicacao operacional no restante das telas do `financeiro`, com foco em fluxo continuo, texto fixo minimo, padronizacao de linguagem e uso raro do `i`
- nas proximas microetapas dessa frente, a decisao sobre shell/topo deve vir antes do refinamento do corpo das telas: em listagens e formularios operacionais, o `financeiro_shell_header` herdado precisa ser avaliado logo no inicio e pode exigir override enxuto quando gerar sensacao de corpo novo sob topo antigo
- POC controlada de tema/base visual pronta e leve, iniciando somente em `financeiro/templates/financeiro/lancamento_form.html` e sem expansao para outras telas antes de auditoria visual e funcional explicita
- comportamento de transferencia em todas as telas e relatorios
- consistencia visual do tratamento de transferencia
- UX do formulario de lancamento em casos limite
- validacoes defensivas adicionais em fluxos operacionais
- extrato com mais contexto operacional sem poluir a tela
- filtros da listagem de lancamentos com melhorias de usabilidade
- expansao futura da auditoria de alteracoes no financeiro para alem de `LancamentoFinanceiro` e `ContaFinanceira`, ampliando o que ja existe para outras entidades do modulo e mantendo model proprio sem `signals`
- refinamentos futuros de leitura para a tela de auditoria de `LancamentoFinanceiro`, alem dos filtros simples ja implementados
- mapeamento e revisao futura das mensagens visiveis ao usuario no modulo `financeiro`, em alinhamento com a futura frente transversal do projeto

### Proximo
- evolucao futura do cadastro de logo institucional/configuracao visual para aceitar imagem opcional por URL ou upload local, com preview no formulario e regra clara de uso/fallback
- expansao futura da edicao em lote para outros cadastros e listagens operacionais alem de lancamentos, com selecao multipla de registros e aplicacao de acoes em massa, por exemplo excluir varias categorias ou trocar situacao/status em lote, tratada como melhoria de UX/operacao e nao como regra de negocio estrutural
- pagina futura de ajuda/manual de uso do sistema, voltada ao usuario final e focada em orientacao pratica de utilizacao das telas e fluxos, tratada como frente de UX/documentacao ao usuario e nao como regra de negocio nem como regras operacionais internas do modulo
- evolucao futura do cadastro de categorias para deixar explicito na propria UI se o usuario esta cadastrando `Categoria` ou `Subcategoria`, com possibilidade de seletor `Categoria | Subcategoria` e exibicao condicional do campo `Categoria`
- base inicial da edicao coordenada do rateio ja implementada com view e formulario proprios do grupo, ainda pendente de refinamentos para a experiencia final
- acabamento operacional do rateio em edicao individual e leitura do grupo nas telas ja existentes
- estrategia aprovada para futura edicao coordenada do grupo rateado com view e formulario proprios, dados comuns em bloco e salvamento transacional
- modelagem documental mais rica do rateio, se necessario em etapa posterior
- regularizacao eventual de bases antigas de rateio sem `grupo_rateio` valido, caso precisem entrar na leitura consolidada do extrato
- item informativo futuro na tela de lancamentos, com simbolo `i` e historico de cadastro/alteracoes do documento ou lancamento quando houver ganho operacional real
- evolucao futura da central de importacoes do financeiro, com preview mais rico, tratamento avancado de duplicidades e possivel importacao historica em etapa propria, preservando as exportacoes nas listagens filtradas
- evolucao futura da exportacao de lancamentos para oferecer variacoes controladas de saida e refinar o layout conforme uso real
- na importacao/exportacao futura, o fluxo de importacao deve oferecer download de planilha modelo no layout proprio do sistema, preservando a ordem e as colunas esperadas pelo backend de importacao
- refinamentos futuros do MVP de regras automaticas ja aberto no lancamento, preservando `descricao` como gatilho principal por digitacao, `pessoa` apenas como refinador opcional, preenchimento automatico por selecao de uma sugestao e check explicito para salvar nova regra a partir de lancamento comum; melhorias futuras podem incluir curadoria, edicao e governanca dessas regras em tela propria
- acao `Clonar lancamento`, com MVP inicial restrito a lancamento comum sem rateio: abrir `lancamento_form.html` em modo criacao como modelo editavel sem vinculo com o original, copiando campos operacionais seguros (`descricao`, `tipo`, `status`, `valor`, `data_competencia`, `data_pagamento`, `pessoa`, `categoria`, `centro_custo`, `conta`, `conta_destino` quando transferencia, `observacoes`) e sem copiar `pk`, `numero_documento`, auditoria, `grupo_rateio` nem `com_rateio`
- fase futura posterior de clonagem de lancamentos rateados por `grupo_rateio`, tambem sem vinculo com o original, abrindo novo documento rateado ja preenchido e exigindo ajuste manual das linhas/categorias se o `valor total do documento` for alterado no clone
- evolucao futura dos relatorios financeiros para leitura hierarquica por `Categoria` e `Subcategoria`, preservando a distincao entre agrupador analitico e item operacional lancavel
- estudo futuro de agrupamento por categoria com comportamento de expandir/recolher grupos nos relatorios e visoes consolidadas
- estudo futuro de checkboxes para definir exibicao de `centro de custo`, `categoria` e `subcategoria` em relatorios e visoes agrupadas

### Posterior
- contratos a pagar e a receber
- parcelas
- recorrencia
- anexos de comprovantes
- balancete padrao
- importacao de planilha historica
- evolucoes futuras especificas do bloco de recibos ja entregue
- a obrigatoriedade de `data_pagamento` ja foi consolidada no nivel de validacao da aplicacao; eventual endurecimento futuro do campo no banco depende apenas de estrategia segura para bases legadas
- acabamento documental futuro complementar dos relatorios impressos, apenas apos uso real, especialmente quando entrarem logo institucional e configuracao avancada de assinaturas
- evolucao futura da identidade institucional nos relatorios do financeiro, incluindo uso controlado de logo quando fizer sentido documental sem poluir a leitura operacional
- permitir mais de uma assinatura cadastrada por relatorio que tenha assinatura
- permitir configurar em cada relatorio se mostra assinatura
- permitir configurar quais assinaturas ativas devem aparecer em cada relatorio

## 14. Checklist permanente de amarracao para novas implementacoes

- a referencia operacional curta dessa revisao passa a ser `docs/CHECKLIST_EVOLUCAO_SISTEMA.md`
- Navegacao, menu e atalhos
- Permissoes por modulo, tela/recurso e acao
- Impacto em listagens: filtros, ordenacao, colunas, truncamento, acoes em lote e exportacao
- Impacto em formularios: rotulos, obrigatoriedade, mensagens, preview e consistencia visual
- Impacto em importacao/exportacao
- Impacto em auditoria/log
- Impacto em ajuda/manual do usuario
- Aderencia ao padrao UX/layout do sistema
- Atualizacao obrigatoria de `docs/CEREBRO_PROJETO.md`, `docs/STATE.md`, `docs/CODEX_RESULTADO.md` e `docs/ROADMAP_FINANCEIRO.md`

## 7. Consolidacao desta microetapa de acabamento documental

- `Extrato`, `Resumo` e `Prestacao de Contas` passaram a compartilhar cabecalho documental de impressao/PDF mais coerente, com identidade institucional leve, metadados visiveis e hierarquia visual menos tecnica.
- `Prestacao de Contas` recebeu bloco final de assinatura mais formal, ainda simples e sem antecipar a futura frente de multiplas assinaturas.
- a base atual de impressao/PDF dos tres relatorios deve ser tratada como padrao funcional e visual desta etapa; backlog futuro relacionado fica restrito a logo institucional, configuracao de assinaturas e eventual acabamento complementar por uso real
- nesta microetapa nao houve alteracao de regra de negocio nem ampliacao de escopo funcional dos relatorios

## 8. Refino posterior de identidade e margens dos relatorios

- o uso de sigla como pseudo-logo deixou de ser diretriz aceitavel para os relatorios impressos do `financeiro`
- a base atual passou a priorizar logo institucional quando existir e, na ausencia dela, usar apenas o nome institucional no cabecalho documental
- a etapa tambem reforcou margens e respiro do documento impresso, mantendo o shell isolado e melhorando o aproveitamento visual do `Extrato`
- backlog futuro de acabamento final continua restrito a logo institucional melhor curada por uso real, multiplas assinaturas e configuracao por relatorio, sem reabrir regra de negocio

## 9. Refino documental do recibo e da leitura do saldo acumulado

- o recibo passou a adotar topo mais limpo e institucional, com titulo principal unico, numero em linha secundaria e mensagem central com maior protagonismo
- no recibo, a logo agora deve liderar a identidade visual quando existir; o nome institucional permanece apenas como fallback discreto quando nao houver logo utilizavel
- o `saldo acumulado` do extrato passou a usar leitura visual por sinal, alinhada ao vocabulario de valores positivos e negativos ja usado no modulo
- backlog futuro do bloco de recibos continua restrito a evolucoes especificas posteriores, sem reabrir regra de negocio nem o escopo funcional entregue

## 10. Reforco documental de margens, bordas e identidade visual

- a base atual dos relatorios impressos e do recibo passou a usar margens de pagina mais abertas, quadro documental mais explicito e respiro interno mais perceptivel
- os relatorios passaram a evitar repeticao desnecessaria do nome institucional quando a logo ja esta presente de forma suficiente no cabecalho
- backlog futuro de acabamento permanece restrito a curadoria fina por uso real, multiplas assinaturas e configuracao futura da identidade visual global do sistema

## 11. Frentes futuras documentais relacionadas

- futura configuracao da paleta geral do sistema, com definicao de cor principal e derivacao coerente da paleta relacionada, sem aplicacao manual de cor solta em cada tela
- futuro log de acesso ao sistema em camada estrutural propria, separado da auditoria funcional do `financeiro`
- revisao futura da posicao do `Extrato` na navegacao do modulo, sem decisao de mudanca nesta etapa

## 12. Auditoria inicial da frente transversal de UX/comunicacao operacional

- telas hoje mais alinhadas ao padrao: `lancamento_form.html`, `lancamento_rateio_grupo_form.html`, `lancamento_list.html`, `conta_extrato.html`, `resumo.html`, `prestacao_contas.html` e `lancamento_recibo.html`
- telas com maior necessidade de padronizacao futura: `home.html`, `auditoria_lancamento_list.html`, `conta_list.html`, `pessoa_list.html`, `categoria_list.html`, `centro_custo_list.html` e respectivos formularios auxiliares ainda nao revisitados
- os desvios mais recorrentes nessa auditoria inicial foram: subtitulos e explicacoes acima do necessario, segmentacao visual mais antiga, headings e labels menos consistentes, estados vazios crus e acentuacao/linguagem ainda nao uniformizadas em todas as listas e cadastros
- ordem recomendada de aplicacao no restante do `financeiro`: 1) `home.html`; 2) `auditoria_lancamento_list.html`; 3) listas principais de cadastros auxiliares (`conta`, `pessoa`, `categoria`, `centro_custo`); 4) formularios auxiliares; 5) consolidacao final de componentes compartilhados para reaproveitamento transversal
- esse mesmo padrao deve orientar tanto futuros ajustes nas telas existentes quanto novos itens e novas telas que entrarem no sistema, evitando reintroducao de excesso de texto, `i` disperso e empilhamento desnecessario de blocos

## 13. Reclassificacao estrutural da home do modulo financeiro

- a `home.html` do `financeiro` deixa de ser tratada como entrada principal do modulo e passa a ser considerada rota secundaria explicita, porque a sidebar ja cobre a navegacao estrutural e a tela nao justifica uma camada intermediaria propria
- a entrada correta do modulo passa a ser a listagem principal de lancamentos, o que reduz redundancia e alinha a navegacao com a diretriz transversal de fluxo operacional direto
- com essa decisao, a fila imediata da auditoria transversal deixa de comecar por `home.html` e passa a seguir por `auditoria_lancamento_list.html`, depois `conta_list.html`, `pessoa_list.html`, `categoria_list.html`, `centro_custo_list.html` e respectivos formularios auxiliares
- a antiga home so deve voltar a ganhar protagonismo estrutural se um dashboard operacional real vier a existir em etapa futura propria e justificada

### Estrutural futura
- integracao futura do `financeiro` com autenticacao e controle de acesso por usuario quando a frente estrutural do projeto for iniciada
- definicao futura de permissoes por acao dentro do `financeiro`, sem isolar essa governanca do restante do sistema
- convivencia futura do `financeiro` com administracao global centralizada de usuarios, perfis e permissoes, preservando a separacao entre cadastros globais e cadastros especificos do modulo
- frente estrutural futura de usuarios, login, perfis e permissoes, com centralizacao progressiva de autenticacao, acesso e governanca entre modulos
- possibilidade futura de unificacao de cadastros compartilhados, incluindo base comum de pessoas e outras entidades transversais quando isso fizer sentido para o sistema como um todo
- permissões, acesso, login e perfis continuam explicitamente como frente futura e nao entram por microetapas locais desta frente visual/operacional do `financeiro`

### Experimental
- POC controlada de uso de template pronto no shell do `financeiro`, apenas como experimento comparativo e sem adocao abrupta no projeto
- telas de impressao, PDF e recibo ficam fora da primeira onda dessa padronizacao estrutural

### Prioridade imediata atual
- a frente imediata prioritaria deixa de ser novos microajustes incrementais no layout atual de `lancamento_form.html`
- a proxima microetapa correta passa a ser uma POC visual controlada com base no **Tabler** apenas em `financeiro/templates/financeiro/lancamento_form.html`
- essa tela piloto deve preservar integralmente regra de negocio, validacoes, payload JS, `grupo_rateio`, `numero_documento`, calculos, comportamento atual do formulario e logica de exibicao/ocultacao do rateio
- recomposicoes manuais locais anteriores do `lancamento_form.html` nao contam como execucao valida dessa POC e devem ser tratadas apenas como montagem intermediaria a ser reaproveitada ou descartada de forma controlada antes da adocao real do tema-base
- a expansao do Tabler para outras telas do `financeiro` ou para outros modulos fica bloqueada ate auditoria visual e funcional real da primeira tela piloto
- so depois de validada essa POC na tela piloto o projeto pode decidir por continuidade, abandono da base ou customizacoes pontuais por cima dela

### Sequencia linear anteriormente sugerida
1. contratos previstos a pagar e a receber
2. parcelas e recorrencia
3. anexos de comprovantes
4. balancete padrao
5. importacao historica
6. evolucoes futuras especificas do bloco de recibos ja entregue

Observacao semantica do backlog:
- os itens da secao `3. O que ja existe, mas ainda pode ser refinado` representam base ja entregue com espaco para refinamento futuro
- os itens da secao `4. O que ainda falta implementar` representam frentes ainda nao entregues como bloco consolidado
- os itens da secao `5. Proximas etapas sugeridas` indicam apenas ordem sugerida de trabalho e nao reclassificam entregas ja concluidas

## 6. Diretriz importante

Este roadmap nao altera nenhuma regra de negocio ja aprovada nem substitui o estado real do repositorio.

Ele serve apenas para:
- consolidar o escopo financeiro ja mapeado
- registrar o que ja foi entregue
- organizar o que ainda falta
- orientar proximas etapas pequenas, seguras e incrementais

## Reestruturação documental futura sem perda de histórico

Fica registrada como frente futura controlada a reorganização gradual da documentação longa do projeto.

Diretrizes:

- não apagar histórico útil;
- não reescrever documentos inteiros sem necessidade;
- criar resumos e índices antes de reduzir arquivos grandes;
- manter STATE.md como estado real;
- manter CODEX_RESULTADO.md como histórico cronológico;
- usar INDICE_PROJETO.md e REGRAS_NEGOCIO.md como camada curta de leitura;
- só mover ou arquivar conteúdo após validação do usuário.

Essa frente deve ser tratada como melhoria de governança/documentação, sem impacto direto no funcionamento do sistema financeiro.
## 14. Balancete Institucional - aceite final do recorte atual

- status consolidado: IMPLEMENTADO E APROVADO PELA USUARIA (FUNCIONAL + UX)
- formatos aprovados:
  - `Operacional`
  - `Operacional + patrimonio vinculado`
  - `Financeiro completo`
- filtros aprovados no recorte atual:
  - filtro principal `Formato do Balancete`
  - composicao do saldo conforme formato
  - `Detalhar patrimonio vinculado` apenas no formato `operacional_patrimonio`
- regra consolidada:
  - patrimonio vinculado nao se mistura ao resumo operacional
  - transferencias entre operacional e vinculado seguem como movimentacao de fronteira (nao receita/despesa operacional)
- confirmacao de seguranca:
  - sem alteracao de calculo financeiro, saldos, lancamentos, Extrato, Fechamento/Prestacao e demais relatorios
- governanca:
  - nao reabrir a logica funcional/UX desse recorte do Balancete sem nova decisao explicita da usuaria
## 15. Fila recomendada apos aceite final do Balancete Institucional

- frente Balancete: ENCERRADA E APROVADA (funcional + UX), com logica congelada no recorte atual
- proximas pendencias recomendadas, em ordem:
  1. homologacao real de importacoes com planilhas historicas completas (lancamentos e cadastros auxiliares)
  2. validacao visual final de relatorios impressos em volume real, com foco no Extrato
  3. auditoria preparatoria da frente futura de frequencia/recorrencia por competencia
- observacao de governanca: enquanto nao houver nova decisao explicita da usuaria, nao reabrir logica funcional do Balancete
## 16. Auditoria e consolidacao do MVP - contribuicao mensal/frequencia por competencia

Status consolidado: MODELADA/DOCUMENTADA, SEM IMPLEMENTACAO FUNCIONAL

Direcao validada para futura implementacao:
- frente generica por recorrencia mensal, nao exclusiva de "contribuicao"
- eixo de controle: `pessoa/favorecido recorrente` + `subcategoria com controle de frequencia`
- competencia mensal explicita como base de leitura gerencial
- relatorios futuros em duas visoes: matriz com valores e matriz sem valores
- termo por favorecido como segunda onda, sem misturar no primeiro patch

Recorte minimo recomendado:
1. campos/flags minimos em pessoa e subcategoria
2. matriz mensal com valores por competencia
3. matriz sem valores (indicador de frequencia)
4. termo por favorecido (lote) em etapa posterior

Dependencias/decisoes pendentes da usuaria:
- competencia oficial do MVP: `data_competencia` ou `data_pagamento`
- considerar apenas `quitado` ou tambem `aberto` com marcacao visual
- regra de consolidacao quando houver multiplos lancamentos no mesmo mes
- subcategoria inicial obrigatoria para contribuicao mensal
- se termo por favorecido entra no MVP inicial ou na etapa seguinte

### SPEC funcional/técnica consolidada (pre-implementacao)

Decisoes de modelagem para implementacao futura:
- nao usar checkbox puro como fonte do controle de competencia;
- adotar alocacao de competencia com `mes/ano + valor` como unidade minima;
- manter lancamento financeiro como origem do dinheiro no MVP;
- nao abrir modulo separado de baixa na primeira onda.

Vinculo tecnico recomendado:
- usar estrutura filha/intermediaria de alocacao de competencia, ligada ao lancamento e com referencia explicita da subcategoria que controla frequencia;
- essa estrutura deve atender lancamento simples e lancamento com rateio sem depender do valor total bruto do documento.

Regra para lancamento simples:
- quando favorecido recorrente + subcategoria controlada, permitir registrar competencias atendidas com valor por competencia;
- soma das alocacoes deve fechar com o valor relevante daquele trecho controlado.

Regra para lancamento com rateio:
- so entra no controle o item/parte com subcategoria marcada como controla frequencia;
- a competencia nao deve usar automaticamente o valor total do lancamento quando houver itens nao recorrentes no mesmo documento.

Regra para recebimento misto (contribuicao + livro/camisa/doacao avulsa):
- apenas a parte de subcategoria controlada alimenta frequencia;
- partes nao controladas ficam fora da matriz, mesmo para favorecido recorrente.

Leituras gerenciais:
- matriz com valores vem primeiro;
- matriz sem valores deriva da matriz com valores;
- termo por favorecido fica para segunda onda, apos validacao da matriz.
## 17. Frequencia por competencia - base cadastral minima

- etapa funcional minima concluida apenas em cadastros
- campos criados:
  - `PessoaFinanceira.contribuinte_recorrente` (default `False`)
  - `CategoriaFinanceira.controla_recorrencia_competencia` (default `False`)
- exposicao concluida em formulario/listagem/admin e importacao/exportacao auxiliar de pessoas e categorias
- permanece para as proximas microetapas: alocacao de competencia, matriz com valores, matriz sem valores e termo por favorecido

## 18. Frequencia por competencia - alocacao vinculada ao lancamento

- etapa funcional concluida para lancamento simples
- model criado: `AlocacaoCompetenciaFinanceira`
- regra entregue:
  - cada alocacao guarda `categoria`, `mes_competencia`, `ano_competencia` e `valor_alocado`
  - um lancamento pode ter varias competencias
  - a soma das competencias deve fechar com o valor controlado do lancamento
  - a exigencia so aparece quando favorecido recorrente + subcategoria controlada estiverem presentes
- edicao recarrega competencias existentes; exclusao do lancamento remove as alocacoes; clone comum nao copia competencias
- rateio ficou apenas preparado nesta etapa: sem usar valor total do documento para recebimento misto e sem abrir ainda captura por item na criacao inicial do grupo
- permanecem para as proximas microetapas: alocacao segura por item rateado e matriz mensal com valores
- validacao da usuaria registrada:
  - recorte de lancamento simples aprovado em uso local
  - soma de competencias fechando com valor controlado aprovada
  - divergencia de soma bloqueando salvamento aprovada
  - edicao com recarga de competencias e clone sem copia de competencias aprovados
  - sem alteracao de calculo, saldos e relatorios existentes

## 19. Frequencia por competencia - rateio controlado

- etapa funcional concluida para captura e validacao por item/subcategoria controlada no rateio
- regra entregue:
  - o valor bruto total do documento nao entra como base da competencia em recebimento misto
  - cada subcategoria controlada do rateio fecha suas competencias apenas contra o proprio valor consolidado
  - itens nao controlados do mesmo rateio ficam fora da frequencia
  - favorecido nao recorrente ou rateio sem subcategoria controlada nao exigem competencias
- create com rateio e edicao coordenada do grupo passaram a persistir/remover alocacoes de forma coerente com as linhas finais do grupo
- clone de rateio continua sem copiar competencias automaticamente
- permanecem para as proximas microetapas: matriz sem valores derivada e termo por favorecido

## 20. Pendencias novas apos rateio controlado

- **Auditoria acionavel**: FUTURO/BACKLOG, com SPEC propria obrigatoria antes de implementacao
  - links da auditoria para objeto auditado quando existir
  - navegacao direta para lancamento/pessoa/categoria/documento relacionado
  - leitura de antes/depois em formato claro
  - indicacao explicita de objeto excluido
  - estudo de desfazer/restaurar apenas com seguranca forte, permissao dedicada e trilha da reversao
- **Listagem de lancamentos - acoes faltantes**: pendencia funcional/UX para auditoria tecnica
  - usuaria observou ausencia de acoes esperadas (exclusao/recibo) em alguns lancamentos
  - nao corrigir sem primeiro mapear recorte tecnico (rateio, competencia, linha controlada ou outro)
- **Competencias duplicadas no mesmo lancamento/subcategoria**: regra recomendada para proxima implementacao
  - manter soma entre multiplos lancamentos na matriz futura
  - bloquear repeticao de mes/ano dentro do mesmo lancamento e mesma subcategoria controlada
  - mensagem sugerida:
    - `Ja existe uma competencia informada para este mes/ano. Agrupe o valor em uma unica linha.`

## 21. Frequencia por competencia - primeira matriz mensal com valores

- etapa funcional concluida para a primeira leitura gerencial por competencia
- tela criada:
  - `/financeiro/frequencia-competencias/`
- fonte de dados:
  - `AlocacaoCompetenciaFinanceira`
- regra entregue:
  - linhas com favorecidos recorrentes, inclusive sem alocacao no periodo
  - colunas com todas as competencias mensais entre o inicio e o fim selecionados
  - celulas somando `valor_alocado` por pessoa/competencia
  - totais por favorecido, por mes e total geral
  - filtro por subcategoria controlada (`todas` ou uma subcategoria)
  - filtro por status (`Todos`, `Quitados`, `Em aberto`)
  - em `Todos`, a leitura soma `quitado + aberto` e nao inclui `cancelado`
- recortes preservados:
  - item nao controlado do rateio permanece fora da matriz
  - favorecido nao recorrente fica fora por padrao, mesmo se existir alocacao inconsistente
  - matriz sem valores/check-X ainda nao implementada
  - termo por favorecido ainda nao implementado

Proxima etapa recomendada:
- implementar a matriz sem valores derivada da matriz com valores e deixar o termo por favorecido para a microetapa seguinte

## 22. Frequencia por competencia - matriz sem valores derivada

- etapa funcional concluida para a segunda visualizacao da mesma tela `Frequencia por competencia`
- regra entregue:
  - filtro `Formato da matriz` com opcoes `Com valores` e `Sem valores (frequencia)`
  - modo sem valores derivado da mesma base `AlocacaoCompetenciaFinanceira`
  - `✓` verde quando ha contribuicao na competencia filtrada
  - `×` vermelho quando nao ha contribuicao
  - totais de frequencia por favorecido, por mes e geral
  - filtros de periodo, subcategoria controlada e status preservados
- recortes preservados:
  - nenhuma impressao implementada nesta etapa
  - nenhum termo por favorecido implementado nesta etapa
  - nenhuma exportacao implementada nesta etapa

Proxima etapa recomendada:
- preparar a impressao da matriz tentando acomodar todas as colunas na mesma pagina, reaproveitando margens e padrao de impressao ja usados no sistema

## 23. Frequencia por competencia - impressao da matriz

- etapa funcional concluida para impressao da tela `/financeiro/frequencia-competencias/`
- escopo entregue:
  - botao `Imprimir`
  - impressao dos dois formatos (`Com valores` e `Sem valores (frequencia)`)
  - cabecalho documental enxuto com formato, periodo, subcategoria, status e emissao
  - contrato local de print em `A4 landscape`
  - compactacao de fonte, padding e largura das colunas para tentar acomodar a matriz em uma pagina
- recortes preservados:
  - nenhuma exportacao dedicada
  - nenhum PDF dedicado
  - nenhuma mudanca na fonte de dados
  - nenhum termo por favorecido ainda nesta etapa
- limitacao conhecida:
  - periodos mais largos, mesmo dentro do limite funcional de 24 competencias, ainda podem ficar visualmente apertados conforme navegador/impressora

Proxima etapa recomendada:
- implementar o termo por favorecido reaproveitando a mesma base de competencias ja consolidada

## 24. Frequencia por competencia - refinamento da impressao

- etapa funcional concluida para corrigir a compressao da coluna `Favorecido` no PDF da matriz
- ajustes entregues:
  - cabecalho mensal compacto no impresso em `MM/AAAA`
  - rotulo de tela preservado em formato amigavel (`Jan/2026`)
  - coluna `Favorecido` protegida contra quebra letra por letra
  - colunas mensais mais compactas no print
  - valores/indicadores centralizados no impresso para reduzir largura
- limitacao mantida:
  - periodos mais largos dentro do limite de 24 competencias ainda podem ficar apertados conforme navegador/impressora

Proxima etapa recomendada:
- implementar o termo por favorecido reaproveitando a mesma base de competencias ja consolidada

## 25. Frequencia por competencia - ajuste de cores no print e UX futura

- etapa funcional concluida (ajuste pontual de impressao):
  - preservacao de cor/contraste dos indicadores `✓` e `×` no modo sem valores da matriz impressa
  - fallback visual mantido para impressao em preto e branco
- frente futura registrada sem implementacao:
  - `Assistente inteligente de competencias`
  - sugestao de meses proximos para preenchimento de competencias
  - regra de leitura: ausencia de valor nao significa `em aberto`, e sim `sem quitacao registrada`
  - valor alocado no mes marca competencia como atendida/quitada
  - modo manual permanece como base segura
  - complemento/observacao por competencia depende de SPEC propria

Proxima etapa recomendada:
- abrir SPEC dedicada do `Assistente inteligente de competencias` antes de qualquer mudanca em formulario/modelagem de lancamento/rateio

## 26. Frequencia por competencia - refinamento do cabecalho impresso

- etapa funcional concluida (ajuste de apresentacao):
  - cabecalho impresso ficou mais limpo e compacto
  - removidos `Formato` e `Status` dos metadados de impressao
  - mantidos `Periodo`, `Subcategoria` e `Emitido em`
  - `Subcategoria` exibe nome legivel quando filtrada; sem filtro especifico exibe `Todas controladas`
- etapa funcional concluida (ajuste visual de indicadores no print):
  - `✓` e `×` preservados no modo sem valores
  - tentativa de manter verde/vermelho no PDF/impressao com `print-color-adjust`/`-webkit-print-color-adjust`
  - fallback legivel em preto e branco mantido
- recortes preservados:
  - sem alteracao de regra de negocio
  - sem alteracao de fonte de dados (`AlocacaoCompetenciaFinanceira`)
  - sem alteracao de calculo financeiro, saldos ou banco real

Proxima etapa recomendada:
- abrir SPEC propria do `Assistente inteligente de competencias` antes de qualquer mudanca em forms/models/templates

## 27. Assistente inteligente de competencias - SPEC funcional consolidada

- etapa documental concluida: SPEC funcional do MVP futuro definida, sem implementacao nesta microetapa

### Objetivo do MVP futuro

- reduzir digitacao manual de competencias sem alterar a regra financeira ja validada
- manter o modo manual atual como fallback/base segura
- adicionar camada assistida sobre os payloads atuais, sem criar nova fonte de salvamento

### Regra de exibicao do assistente

- lancamento simples:
  - exibir apenas quando houver favorecido recorrente + subcategoria controlada
- rateio:
  - exibir apenas para cada subcategoria controlada do grupo
  - item nao controlado continua fora da frequencia
  - nao usar valor bruto total do documento
- se pessoa nao for recorrente ou se a subcategoria nao controlar competencia:
  - manter comportamento atual sem assistente

### Grade sugerida do MVP

- mostrar por padrao:
  - ultimos 5 meses
  - mes atual
  - proximos 5 meses
- por mes, a SPEC recomenda exibir:
  - competencia
  - estado visual
  - campo de valor
  - referencia opcional do valor ja alocado anteriormente naquela pessoa/subcategoria/competencia

### Estados conceituais aprovados

- `Sem quitacao registrada`:
  - nao ha valor alocado previo naquela competencia
- `Ja possui contribuicao`:
  - ja ha valor alocado previo naquela competencia
- `Informado neste lancamento`:
  - usuario digitou valor no mes no formulario atual

Observacao:
- a UX nao deve usar `Em aberto` como estado automatico para mes sem registro

### Regra de inclusao da competencia

- valor positivo preenchido no mes = inclui a competencia no payload do lancamento atual
- mes vazio = nao inclui
- zero/negativo = continua sujeito as validacoes existentes
- soma dos meses informados deve continuar fechando com o valor controlado do lancamento ou da subcategoria controlada do rateio

### Integracao tecnica recomendada

- nao criar novo model
- nao criar nova persistencia
- nao duplicar validacoes
- o assistente deve montar:
  - `competencias_payload` no simples
  - `competencias_rateio_payload` no rateio
- validacoes de soma, duplicidade e escopo por subcategoria controlada continuam centralizadas no backend atual

### Edicao e clone

- edicao simples:
  - carregar competencias ja salvas no mesmo bloco assistido/manual
- lancamento antigo sem competencia:
  - se o lancamento existente atender favorecido recorrente + subcategoria controlada, o assistente deve aparecer mesmo sem alocacoes ja salvas
  - a grade pode abrir vazia para permitir regularizacao no proprio registro
- edicao coordenada do grupo:
  - carregar competencias ja salvas por subcategoria controlada
- clone:
  - continua sem copiar competencias automaticamente

### Redistribuicao sem alterar valor total

- a edicao de competencias deve servir para corrigir a distribuicao por competencia sem alterar automaticamente o valor financeiro total do lancamento/subcategoria
- a soma editada continua precisando fechar com o valor controlado
- isso vale inclusive para lancamentos quitados ja existentes, como redistribuicao gerencial/historica da competencia

### Referencia historica x valor do formulario atual

- a UX futura deve separar claramente:
  - `Ja registrado`: valor historico previo naquela pessoa/subcategoria/competencia
  - `Valor deste lancamento`: campo editavel do formulario atual
- novo valor em mes ja contribuido nao deve ser bloqueado automaticamente
- a matriz consolidada continua somando lancamentos diferentes na mesma competencia

### Fora do MVP

- observacao/complemento por competencia
- qualquer alteracao de model/migration
- modulo proprio de baixa
- historico individual por competencia
- alertas automaticos
- calculo de inadimplencia
- importacao/exportacao de competencias
- termo por favorecido
- mudancas na matriz

### Riscos principais

- usuario confundir contribuicao anterior com o valor do lancamento atual
- usuario confundir `ja registrado` com `valor deste lancamento`
- usuario preencher valor em mes ja contribuido e interpretar isso como duplicidade proibida, quando na verdade a matriz soma multiplos lancamentos
- usuario interpretar redistribuicao de competencias como alteracao do valor financeiro quitado
- poluicao excessiva do formulario
- quebra da validacao de soma do valor controlado
- quebra do rateio controlado se o assistente fugir dos payloads atuais
- tentacao de transformar `sem quitacao registrada` em `em aberto`

### Arquivos provaveis para a futura implementacao

- `financeiro/forms.py`
- `financeiro/views.py`
- `financeiro/tests.py`
- `financeiro/templates/financeiro/lancamento_form.html`
- `financeiro/templates/financeiro/lancamento_rateio_grupo_form.html`

Proxima etapa recomendada:
- implementar o MVP do assistente, primeiro no lancamento simples e no fluxo de rateio/edicao, reaproveitando os payloads atuais e preservando o modo manual

## 28. Assistente inteligente de competencias - MVP funcional

Status: IMPLEMENTADO

Consolidacao:
- o assistente deixou de ser apenas SPEC e passou a existir nos formularios de lancamento e rateio sem alterar model, migration ou banco
- continua sendo camada assistida sobre os payloads ja existentes:
  - `competencias_payload`
  - `competencias_rateio_payload`
- fluxos implementados:
  - lancamento simples novo
  - edicao de lancamento simples
  - regularizacao de lancamento antigo sem competencia
  - rateio controlado novo
  - edicao coordenada de grupo rateado
- regra de exibicao consolidada em codigo:
  - simples: apenas com favorecido recorrente + subcategoria controlada
  - rateio: apenas por subcategoria controlada
  - item nao controlado continua fora
- grade assistida entregue com 11 meses sugeridos:
  - ultimos 5
  - atual
  - proximos 5
- a UX separa `Ja registrado` (referencia consolidada) de `Valor deste lancamento` (campo editavel do registro atual)
- o modo manual permanece visivel e funcional como fallback
- redistribuicao em edicao continua sem alterar automaticamente o valor financeiro total; o fechamento segue protegido pelas validacoes atuais

Limites que permanecem fora desta etapa:
- observacao/complemento por competencia
- alteracao de model/migration
- historico detalhado por competencia
- termo por favorecido
- importacao/exportacao de competencias
- baixa separada

Proxima microetapa recomendada:
- homologar UX real do assistente em tela e decidir se a proxima onda sera refinamento visual/local do formulario ou abertura da frente de termo por favorecido

## 29. Assistente inteligente de competencias - refinamento de UX

Status: IMPLEMENTADO

Consolidacao:
- o assistente foi compactado para lista/tabela, reduzindo altura visual e repeticao de texto dentro do formulario
- a leitura base passou a usar quatro colunas fixas:
  - `Mes`
  - `Situacao`
  - `Ja registrado`
  - `Valor deste lancamento`
- a formacao condicional por situacao foi mantida com classes distintas para meses com contribuicao previa e meses sem quitacao registrada
- a orientacao sobre soma deixou de soar como bronca e passou a ser instrucao de preenchimento
- o bug de foco foi tratado ao impedir re-render completo do assistente a cada tecla digitada
- o modo manual continua como fallback operacional e a fonte de verdade continua sendo os payloads atuais

Pendencia registrada:
- ainda cabe uma revisao visual mais ampla das secoes do formulario, porque outros blocos continuam visualmente misturados fora do escopo desta microetapa

Proxima microetapa recomendada:
- validar este refinamento em uso real e decidir se a proxima frente sera polimento visual geral do formulario ou abertura do termo por favorecido

## 30. Tabelas personalizadas - exportacao XLSX em formato brasileiro

Status: IMPLEMENTADO

Consolidacao:
- exportacao XLSX da tela de linhas ajustada para padrao brasileiro de exibicao numerica
- valores exportados:
  - decimal com virgula e ate 8 casas (sem zeros excedentes)
  - monetario com prefixo `R$` e 2 casas
  - percentual com virgula e ate 4 casas + `%`
  - inteiro sem casas decimais
- totalizadores exportados passaram a seguir o mesmo padrao visual brasileiro
- recorte funcional preservado:
  - colunas ativas/visiveis/nao calculadas
  - linhas ativas
  - busca ativa aplicada na exportacao
  - totalizadores visiveis baseados nas linhas filtradas

Proxima microetapa recomendada:
- implementar formulas guiadas por coluna com whitelist e validacao segura

## 31. Tabelas personalizadas - filtros configuraveis por coluna

Status: IMPLEMENTADO NO PRIMEIRO RECORTE CONTROLADO

Consolidacao:
- a busca textual simples continua como recurso existente e deve permanecer
- a proxima evolucao desejada e adicionar filtros estruturados configuraveis por coluna, sem abrir filtro automatico para toda coluna da tabela
- a decisao funcional aprovada e que a permissao/configuracao do filtro fique vinculada a cada `ColunaPersonalizada`
- tipos priorizados para o primeiro recorte:
  - `data`
  - `mes/competencia`
  - `inteiro`
  - `decimal`
  - `monetario`
  - `percentual`
- operadores sugeridos:
  - `data`: `entre`, `igual a`, `antes de`, `depois de`
  - `mes/competencia`: `entre`, `igual a`
  - numericos (`inteiro`, `decimal`, `monetario`, `percentual`): `entre`, `igual a`, `maior que`, `menor que`
- regras de convivencia com a tela atual:
  - filtros estruturados complementam a busca textual simples; nao a substituem
  - totalizadores devem refletir o resultado filtrado, como ja ocorre com a busca
  - exportacao XLSX futura deve respeitar filtros ativos quando essa camada existir
- recomendacao tecnica inicial:
  - avaliar se a configuracao pode nascer em `ColunaPersonalizada.configuracao_json` no primeiro recorte
  - se a governanca exigir campos explicitos, abrir microetapa propria com model/migration

SPEC tecnica curta da implementacao incremental:
- resultado da auditoria:
  - `ColunaPersonalizada` ja usa `configuracao_json` para `lista_opcoes`
  - `ColunaPersonalizadaForm` ja centraliza configuracoes controladas por coluna sem abrir model auxiliar
  - a tela de linhas ja possui pipeline unico para busca textual, totalizadores e exportacao XLSX
  - por isso, o primeiro recorte de filtros estruturados pode nascer sem migration, desde que a configuracao fique aninhada e governada no JSON da coluna
- decisao recomendada para o primeiro recorte:
  - usar `ColunaPersonalizada.configuracao_json` com bloco dedicado de filtro, sem misturar com `opcoes`
  - formato conceitual sugerido:
    - `configuracao_json.opcoes` continua reservado para `lista_opcoes`
    - `configuracao_json.filtro` passa a concentrar a configuracao do filtro estruturado
    - exemplo conceitual:
      - `{"filtro": {"habilitado": true, "operadores": ["entre", "igual"]}}`
- criterio para permanecer sem migration:
  - a configuracao continua restrita ao formulario de coluna
  - os operadores continuam derivados do `tipo_dado`, e nao livres
  - a aplicacao do filtro continua acoplada a uma unica tela de linhas por tabela
  - nao ha necessidade de indexacao propria, visoes salvas ou compartilhamento transversal da configuracao
- quando abrir model/migration propria:
  - se a configuracao crescer para multiplos modos por coluna, defaults complexos ou metadados independentes do `tipo_dado`
  - se o filtro precisar de consulta/indexacao mais forte no banco em vez de montagem controlada na camada atual da tela
  - se a frente passar a exigir visoes salvas, auditoria propria de configuracao de filtros ou relacionamentos extras entre filtros
- orientacao de UX/estrutura:
  - a configuracao deve aparecer no cadastro da coluna como opcao explicita, e nao como comportamento automatico
  - a tela de linhas deve exibir area de filtros estruturados apenas quando houver pelo menos uma coluna com filtro habilitado
  - busca textual simples permanece separada e complementar
  - resultado final da tela deve aplicar `busca textual + filtros estruturados`
- validacoes tecnicas esperadas:
  - `data`: aceitar formato brasileiro e operadores `entre`, `igual`, `antes`, `depois`
  - `mes/competencia`: aceitar `MM/AAAA` e operadores `entre` e `igual`
  - `inteiro`, `decimal`, `monetario`, `percentual`: aceitar virgula ou ponto e operadores `entre`, `igual`, `maior`, `menor`
  - filtros invalidos devem renderizar mensagem clara e manter a pagina funcional
- impacto controlado na frente atual:
  - totalizadores devem refletir o resultado filtrado por busca + filtros, sem alternancia entre total geral e total filtrado
  - exportacao XLSX deve reaproveitar o mesmo estado filtrado da tela, sem exportacao paralela
- risco tecnico principal a monitorar:
  - deixar `configuracao_json` crescer de forma desorganizada; por isso, o bloco de filtro deve nascer aninhado, curto e derivado do `tipo_dado`

Implementacao realizada:
- o primeiro recorte foi implementado em `ColunaPersonalizada.configuracao_json.filtro`, sem migration
- a configuracao passou a ser feita no proprio formulario da coluna, apenas para tipos elegiveis
- a listagem de colunas passou a indicar visualmente quando o filtro estruturado esta habilitado
- a tela de linhas passou a exibir filtros estruturados apenas quando houver coluna ativa/visivel/habilitada
- busca textual simples permanece separada e complementar
- totalizadores e exportacao XLSX passaram a respeitar busca + filtros estruturados ativos no mesmo fluxo de tela
- filtros invalidos passaram a exibir mensagem clara sem quebrar a pagina

Pendencias futuras desta frente:
- filtro avancado por texto
- filtro por multiplas opcoes de lista
- filtro booleano
- visoes salvas
- agrupamentos
- dashboard
- logica composta avancada

Fora do primeiro recorte:
- filtro avancado por texto
- filtro por multiplas opcoes de lista
- filtro por booleano
- visoes salvas
- agrupamentos
- dashboard
- combinacao logica avancada
- filtros automaticos em todas as colunas

Riscos principais:
- pressao para transformar a tela em analise livre/planilha livre
- complexidade de UX na combinacao entre busca simples e filtros estruturados
- risco de abrir configuracao frouxa demais sem governanca por coluna

Proxima microetapa recomendada:
- apos este recorte, abrir a auditoria tecnica dedicada dos recibos/documentos atuais para preparar a SPEC segura do `Recibo especial`

## 32. Documentos financeiros - recibo especial em lote

Status: AUDITADO TECNICAMENTE / PRONTO PARA SPEC FUNCIONAL SEGURA

Consolidacao:
- foi registrada nova demanda de emissao documental separada dos recibos atuais
- nome sugerido para a futura acao:
  - `Recibo especial`
  - `Recibo especial em lote`
- fluxo futuro sugerido:
  - usuaria seleciona lancamentos na listagem
  - aciona nova opcao documental
  - escolhe manualmente um favorecido cadastrado
  - sistema gera documento em lote no nome desse favorecido selecionado
  - cada item do recibo preserva a descricao atual e acrescenta somente o nome do favorecido original do lancamento como complemento textual da propria descricao
- regra de composicao da descricao no recibo especial:
  - nao usar o rotulo `Favorecido original`
  - nao usar a frase `Favorecido original: Nome`
  - compor apenas a descricao atual com o nome do favorecido original
  - exemplo correto: `Pagamento de cesta basica - Maria Silva`
  - exemplo incorreto: `Pagamento de cesta basica - Favorecido original: Maria Silva`
- regra documental central:
  - o documento e apenas emissao; nao altera favorecido real, lancamentos, saldos ou relatorios financeiros

Guardrails obrigatorios:
- nao alterar o recibo em lote atual
- nao alterar o recibo por favorecido atual
- nao alterar o termo anual de quitacao
- nao alterar regras atuais dos documentos existentes
- nao alterar lancamentos nem favorecido real dos lancamentos

Auditoria tecnica obrigatoria antes da implementacao:
- auditar a acao atual de recibo em lote
- auditar templates, views e helpers dos recibos atuais
- identificar como os lancamentos selecionados sao recebidos
- identificar como o favorecido e validado hoje
- decidir se a nova frente usara view/template novos ou helper reaproveitado com parametro, sem quebrar o comportamento atual

Resultado da auditoria tecnica:
- listagem de lancamentos:
  - a acao documental em lote atual aparece em `financeiro/templates/financeiro/lancamento_list.html` como `Recibos em lote`
  - a selecao em lote envia `lancamentos_selecionados` e `filtros_retorno` para `financeiro:LancamentoFinanceiroAcoesLoteView`
  - o backend resolve selecoes simples e grupos de rateio via `_resolver_lancamentos_para_acoes_em_lote`
  - hoje, para recibos em lote, a listagem sempre redireciona para `financeiro:lancamento-recibos-por-favorecido`, nunca para a rota tecnica de mesmo favorecido
- recibo em lote tecnico atual:
  - view: `LancamentoFinanceiroReciboLoteView`
  - url: `financeiro:lancamento-recibo-lote`
  - template: `financeiro/lancamento_recibo.html` + parcial `financeiro/_lancamento_recibo_documento.html`
  - recebe ids por `GET`
  - valida obrigatoriamente:
    - ids validos
    - lancamentos existentes
    - todos com favorecido
    - todos do tipo `receita`
    - todos do mesmo favorecido
  - o destinatario principal do documento nasce do `pessoa_nome` do primeiro lancamento
  - os itens do lote sao montados por `_agrupar_itens_recibo_por_descricao`, com consolidacao por descricao exatamente igual
- recibos por favorecido atuais:
  - view: `LancamentoFinanceiroRecibosPorFavorecidoView`
  - url: `financeiro:lancamento-recibos-por-favorecido`
  - template: `financeiro/lancamento_recibo.html` + parcial `financeiro/_lancamento_recibo_documento.html`
  - aceita ids de multiplos favorecidos
  - valida apenas:
    - existencia de ids
    - lancamentos com favorecido
    - lancamentos do tipo `receita`
  - depois agrupa os lancamentos por favorecido e gera um recibo por grupo, com `recibo_grupos`
  - nao exige favorecido unico; essa view e a que hoje suporta o fluxo real acionado pela listagem
- termo anual:
  - view: `LancamentoFinanceiroTermoAnualQuitacaoView`
  - url: `financeiro:lancamento-termo-anual-quitacao`
  - template: `financeiro/lancamento_documentos_por_favorecido.html`
  - nao usa ids selecionados; usa os filtros ativos da listagem
  - exige periodo com `data_inicial` e `data_final` dentro do mesmo ano
  - restringe internamente para `receita`, `quitado`, com favorecido e sem rateio
- helper/documento a preservar:
  - o recibo atual centraliza o contexto em `_montar_contexto_recibo_documento`
  - o layout reutilizado fica em `lancamento_recibo.html` + `_lancamento_recibo_documento.html`
  - o termo anual usa template proprio e deve permanecer isolado
- acoes documentais na listagem:
  - a `lancamento_list` mantem acao documental por linha via `recibo_url`
  - a acao em lote `Recibos em lote` continua separada e nao deve ser reaproveitada como alias do futuro fluxo especial
  - o `Termo anual de quitacao` continua como botao proprio baseado nos filtros da listagem, nao nos ids selecionados
- permissao atual:
  - todos os fluxos documentais auditados usam `financeiro.lancamentos.emitir_recibo`
- testes atuais encontrados:
  - ha cobertura da presenca/ausencia das acoes documentais na listagem de lancamentos
  - nao apareceu suite dedicada forte para o contrato interno do recibo em lote tecnico, dos recibos por favorecido e do futuro `Recibo especial`; isso precisa entrar junto da implementacao funcional

Riscos principais:
- contaminar o fluxo atual dos recibos com regra excepcional
- quebrar validacoes/documentos ja homologados
- misturar emissao documental com alteracao indevida de dados operacionais

Arquitetura recomendada:
- criar acao nova e isolada na listagem, sem reaproveitar o label `Recibos em lote`
- criar view nova para o fluxo especial, em duas etapas:
  - etapa 1: receber ids selecionados e validar selecao documental minima
  - etapa 2: exigir escolha manual de um favorecido cadastrado antes de renderizar o documento
- criar template proprio do `Recibo especial` ou parcial nova derivada do recibo atual, evitando condicoes excessivas dentro do template atual
- preservar `_montar_contexto_recibo_documento` para os fluxos homologados e, se houver reaproveitamento, faze-lo por helper novo ou adaptador explicito, sem alterar o contrato atual de `recibo em lote` e `recibos por favorecido`
- manter a descricao especial como composicao nova por item:
  - `descricao atual - nome do favorecido original`
  - sem `Favorecido original`
  - sem `Favorecido original: Nome`
- a acao nova so deve aparecer na listagem quando a rota/view minima ja existir, evitando link quebrado

SPEC segura consolidada:
- o `Recibo especial` deve nascer como nova acao documental, separada de:
  - `lancamento-recibo-lote`
  - `lancamento-recibos-por-favorecido`
  - `lancamento-termo-anual-quitacao`
- deve aceitar ids selecionados da listagem, inclusive quando vierem de grupos de rateio ja resolvidos pelo backend atual
- deve validar:
  - ids selecionados existentes
  - ao menos um lancamento selecionado
  - todos os lancamentos com favorecido
  - todos os lancamentos do tipo `receita`
  - favorecido destinatario escolhido manualmente e existente no cadastro
- nao deve:
  - alterar favorecido real do lancamento
  - alterar descricao original persistida
  - alterar saldos, relatorios ou qualquer dado operacional
- o documento final deve usar o favorecido escolhido como destinatario principal e compor cada item com o nome do favorecido original somente como complemento textual da descricao

Proxima microetapa recomendada:
- implementar o fluxo funcional minimo do `Recibo especial` apenas como acao nova e isolada, com escolha manual de favorecido e testes de nao regressao dos recibos existentes

Status apos implementacao funcional minima:
- a acao `Recibo especial` passou a existir na listagem de lancamentos como fluxo separado de `Recibos em lote`
- o fluxo ja cobre:
  - selecao em lote
  - escolha manual de favorecido destinatario
  - documento unico para lancamentos de varios favorecidos
  - composicao do item como `descricao atual - nome do favorecido original`
- o fluxo permanece sem:
  - PDF proprio
  - auditoria operacional dedicada do recibo especial
  - permissao exclusiva separada de `financeiro.lancamentos.emitir_recibo`
  - refinamentos visuais/documentais apos homologacao real

Proximo passo recomendado:
- homologar visualmente o `Recibo especial` com casos reais de uso e decidir se a frente exigira permissao dedicada e auditoria documental propria

Status do refinamento curto:
- documento impresso do `Recibo especial` agora usa titulo `RECIBO`
- textos fixos foram revisados com acentuacao e pontuacao
- formulario de escolha do favorecido ganhou busca local por trecho do nome (sem rota adicional)
- recorte funcional segue isolado, sem alterar recibos homologados ou regras de lancamento

Status do refinamento de UX:
- a escolha de favorecido do `Recibo especial` passou a usar um unico campo pesquisavel visivel
- o select real por ID foi mantido oculto para preservar validacao backend e contrato de envio
- busca local por nome passou a operar por trecho, ignorando caixa e acentos
- envio sem selecao valida foi reforcado com mensagem clara no formulario
- fallback sem JavaScript mantido por `<noscript>`
- cabecalho da tela de selecao ajustado para evitar sobreposicao entre titulo e subtitulo

Status de homologacao da usuaria:
- primeiro recorte funcional/visual do `Recibo especial em lote` homologado localmente com retorno `Esta OK`
- validado:
  - fluxo funcional do recibo especial
  - titulo impresso `RECIBO`
  - busca por trecho do nome do favorecido
  - campo pesquisavel unico (sem duplicidade visual)
  - sobreposicao de titulo/subtitulo corrigida
  - descricao composta `descricao atual - nome do favorecido original`
- preservado:
  - recibo em lote atual
  - recibos por favorecido atuais
  - termo anual
  - lancamentos e favorecido real
  - sem impacto no financeiro oficial

Pendencias futuras opcionais:
- permissao dedicada para o `Recibo especial`
- auditoria operacional propria
- ajustes finos de impressao, caso o uso real indique necessidade

## Microetapa: formulas guiadas por coluna - Onda 3

Status:
- implementado o recorte de integracao controlada com busca textual simples e exportacao XLSX

Consolidacao:
- a busca textual simples agora considera colunas calculadas visiveis, ativas e com formula habilitada pelo valor final formatado
- a exportacao XLSX agora inclui colunas calculadas visiveis com o valor final calculado em padrao brasileiro
- operando ausente e divisao por zero continuam gerando celula vazia

Guardrails mantidos:
- sem persistencia em `valor_calculado`
- sem formula Excel no XLSX
- sem filtro estruturado para calculadas
- sem totalizador para calculadas
- sem impacto no financeiro oficial

Proxima decisao recomendada:
- definir em microetapa propria se colunas calculadas permanecerao fora de totalizadores no MVP ou se abrirao uma regra segura e explicita para o rodape

## Microetapa: UX de "Tipo do resultado" nas formulas guiadas

Status:
- implementado refinamento de clareza textual no campo `Tipo do resultado`

Consolidacao:
- `Decimal` e `Monetario` permanecem como unicos tipos de resultado do primeiro recorte
- microcopy do formulario passou a explicar o motivo e orientar o uso de `Decimal` com `0` casas quando necessario

Guardrails preservados:
- sem liberar `Inteiro` e `Percentual` nesta etapa
- sem alteracao de calculo da formula
- sem alteracao de busca, XLSX, filtros ou totalizadores

## Microetapa documental: SPEC de totalizadores em colunas calculadas

Status:
- auditoria tecnica concluida e decisao funcional documentada, sem implementacao

Decisao do recorte:
- no MVP atual, colunas calculadas permanecem fora dos totalizadores do rodape

Base tecnica da decisao:
- o rodape atual da tela e o rodape do XLSX compartilham o mesmo pipeline de totalizacao
- colunas calculadas hoje ja entram:
  - na grade como leitura
  - na busca textual
  - no XLSX como valor final
- colunas calculadas ainda nao entram:
  - nos filtros estruturados
  - nos totalizadores
- o valor calculado continua nao persistido e segue resolvido apenas em tempo de leitura

Motivos para manter fora:
- evitar dupla interpretacao quando a formula deriva de colunas que ja aparecem totalizadas
- evitar somar/agregar resultados vazios gerados por operando ausente ou divisao por zero
- evitar abrir rodape derivado antes de existir necessidade operacional homologada

Condicoes para eventual reabertura futura:
- microetapa propria
- apenas `resultado_tipo` `decimal` ou `monetario`
- totalizador operando sobre o valor final calculado
- linhas com resultado vazio ignoradas
- mesma exibicao no rodape da tela e no rodape do XLSX
- recorte inicial futuro, se aprovado:
  - `soma`
  - `contagem`

Proxima microetapa recomendada:
- manter o tema fechado no MVP e priorizar homologacao/auditoria operacional da frente antes de reabrir totalizadores em calculadas

## Microetapa documental: homologacao do MVP de tabelas personalizadas

Status:
- consolidado funcionalmente no primeiro recorte, com auditoria operacional propria ainda pendente

Consolidacao do MVP:
- frente de tabelas personalizadas entregue com:
  - estrutura, permissoes e menu/listagem
  - cadastro de tabelas e colunas
  - listas de opcoes
  - linhas e valores editaveis por tipo
  - busca textual simples
  - filtros estruturados por coluna comum
  - totalizadores em colunas comuns
  - exportacao XLSX
  - formulas guiadas por coluna
  - calculo de formula em leitura
  - busca e XLSX refletindo valor calculado
  - UX autodidata no formulario de colunas

Limites mantidos no MVP:
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

Guardrails de continuidade:
- resultado calculado permanece sem persistencia em `valor_calculado`
- sem alteracao em financeiro oficial, lancamentos, saldos, extrato, resumo, prestacao/fechamento ou balancete

Proxima frente recomendada:
- abrir SPEC/auditoria tecnica da auditoria operacional propria da frente de tabelas personalizadas para decidir trilha de eventos de:
  - criacao/edicao de tabela
  - criacao/edicao de coluna
  - alteracao de opcoes de lista
  - alteracao de filtros
  - alteracao de totalizadores
  - configuracao/alteracao de formula
  - criacao/edicao de linhas
  - exportacao XLSX, apenas se houver reabertura futura como evento auditavel

## Microetapa documental: SPEC da auditoria operacional de tabelas personalizadas

Status:
- auditoria tecnica concluida e recorte futuro especificado, sem implementacao

Auditoria atual do financeiro:
- base existente em `AuditoriaFinanceiro`
- diff atual em `campos_alterados` com pares `before`/`after`
- registro de `usuario`, `data_hora`, `acao`, `modelo` e `registro_id`
- helpers existentes em `views.py` suficientes para inspirar o padrao da nova frente

Eventos obrigatorios do primeiro recorte futuro:
- criacao de tabela
- edicao de tabela
- criacao de coluna
- edicao de coluna
- alteracao de opcoes de lista
- alteracao de filtro estruturado
- alteracao de totalizadores
- configuracao/alteracao de formula
- criacao de linha
- edicao de linha

Decisao fechada para o primeiro recorte:
- exportacao XLSX fica fora da auditoria operacional inicial
- justificativa:
  - e acao de leitura/extracao, nao de alteracao de dado
  - auditar agora pode elevar volume de logs e poluir a leitura operacional da trilha
- reabertura futura:
  - permitida se surgir necessidade de seguranca, controle de acesso ou rastreabilidade de extracoes

Fora do primeiro recorte:
- visualizacao de tela
- busca simples
- filtros usados apenas para leitura
- calculo de formula em tempo de leitura
- navegacao comum

Arquitetura recomendada:
- reaproveitar `AuditoriaFinanceiro` no primeiro recorte, com helpers e snapshots especificos de `Tabelas personalizadas`
- manter model proprio como avaliacao futura apenas se a frente exigir semantica, permissao ou volume incompatibilizados com a auditoria atual

Conteudo minimo por evento:
- usuario
- data/hora
- tipo de evento
- tabela afetada
- coluna afetada, quando houver
- linha afetada, quando houver
- resumo da acao
- estado anterior
- estado posterior
- campos alterados
- origem da acao

Snapshots futuros recomendados:
- tabela
- coluna
- `configuracao_json`
- totalizadores ativos
- linha
- valores persistidos da linha
- sem incluir `valor_calculado` nem calculo em leitura

Permissao recomendada:
- recorte inicial usando a governanca ja existente de `financeiro.auditoria.listar`
- permissao propria futura fica condicionada a revisao de volume/sensibilidade da frente

## Microetapa: auditoria operacional minima de tabelas personalizadas

Status:
- implementado no primeiro recorte operacional, sem model novo e sem migration

Consolidacao:
- auditoria implementada reaproveitando `AuditoriaFinanceiro`
- eventos cobertos:
  - criacao/edicao de tabela
  - criacao/edicao de coluna
  - criacao/edicao de linha
- alteracoes estruturais da coluna agora ficam rastreaveis no diff por snapshot:
  - `configuracao_json` (opcoes, filtro, formula)
  - `totalizadores`
- snapshots de linha incluem valores persistidos por coluna, sem `valor_calculado`

Limites mantidos:
- exportacao XLSX continua fora da auditoria no primeiro recorte
- leitura, busca, filtros de consulta e calculo em leitura continuam fora

Status de validacao:
- validado pela usuaria no primeiro recorte

Consolidacao da validacao:
- auditoria minima considerada aprovada para:
  - criacao/edicao de tabela
  - criacao/edicao de coluna
  - alteracoes de opcoes/filtro/formula/totalizadores na coluna
  - criacao/edicao de linha
  - valores persistidos da linha no snapshot
- limites preservados:
  - sem auditoria de exportacao XLSX
  - sem auditoria de visualizacao/busca/filtros de leitura
  - sem auditoria de calculo em leitura
  - sem `valor_calculado` no log
  - sem model novo e sem migration

Proxima frente recomendada:
- abrir microetapa de refinamento de UX/fluxo das tabelas personalizadas, reduzindo fragmentacao entre cadastro de tabela, configuracao de colunas e preenchimento de linhas

## Microetapa documental: SPEC de UX unificada das tabelas personalizadas

Status:
- documentado, sem implementacao

Problema registrado:
- o uso atual das tabelas personalizadas ficou fragmentado entre:
  - cadastro/edicao da tabela
  - configuracao de colunas
  - preenchimento de linhas
- a usuaria precisa alternar entre paginas separadas para trabalhar no mesmo controle interno

Fluxo atual auditado:
- listagem de tabelas com acesso separado para `Linhas`, `Colunas` e `Editar`
- tela propria de dados gerais da tabela
- tela propria de colunas
- tela propria de linhas com busca, filtros estruturados, exportacao XLSX, grade e totalizadores
- formularios proprios de coluna e linha
- permissao e auditoria ja acopladas aos pontos de escrita existentes

Direcao recomendada:
- a tabela aberta deve virar a tela central de trabalho da frente
- fluxo desejado:
  - `Tabelas personalizadas`
  - abrir uma tabela
  - dentro dela gerenciar linhas, busca, filtros, exportacao, colunas e dados gerais

Primeiro recorte seguro:
- manter a listagem de linhas como tela principal da tabela
- centralizar no topo desta tela as acoes:
  - `Nova linha`
  - `Configurar colunas`
  - `Editar tabela`
  - `Exportar XLSX`
- manter na mesma tela:
  - busca
  - filtros estruturados
  - grade
  - totalizadores
- reaproveitar rotas atuais
- nao criar modal complexo
- nao remover telas antigas agora

Ondas futuras:
- Onda 1:
  - melhorar a tela principal da tabela, centralizando linhas e acoes principais
- Onda 2:
  - melhorar a configuracao de colunas dentro do contexto da tabela
- Onda 3:
  - avaliar cadastro de linha em painel, modal ou inline apenas se o uso real justificar

Fora do primeiro recorte:
- edicao inline de celula
- modal complexo
- arrastar e soltar colunas
- importacao
- edicao em massa
- dashboard
- visoes salvas
- reescrever rotas
- remover telas antigas
- alterar models, banco ou auditoria
- alterar calculos, formulas, filtros, totalizadores ou XLSX

Preservacoes obrigatorias:
- permissoes:
  - `visualizar`
  - `preencher_linhas`
  - `editar_linhas`
  - `editar_estrutura`
  - `configurar_formula`
  - `exportar`
- auditoria operacional minima ja validada:
  - criacao/edicao de tabela
  - criacao/edicao de coluna
  - criacao/edicao de linha
- a evolucao futura de UX nao pode duplicar logs nem remover auditoria

Proxima microetapa recomendada:
- implementar a Onda 1 da UX unificada, promovendo a tela de linhas a tela principal da tabela e adicionando acoes de contexto no topo
