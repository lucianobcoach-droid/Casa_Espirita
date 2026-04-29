# Rotina de Baixa Documental de Pendencias - Casa Espirita

## 1. Objetivo

Garantir que cada tarefa concluida, substituida, parcialmente concluida, descartada ou dependente de validacao seja registrada corretamente nos documentos oficiais do projeto.

## 2. Regra principal

Nenhuma tarefa deve permanecer como `DUVIDA`, `FUTURO REAL` ou `REQUER CONFERENCIA NO CODIGO` quando ja tiver sido auditada, implementada, substituida, descartada ou reclassificada por decisao da usuaria.

Quando houver implementacao tecnica mas faltar validacao visual ou teste de uso real, o item deve ser classificado como `AGUARDANDO VALIDACAO VISUAL` ou `AGUARDANDO TESTE DO USUARIO`, nao como duvida generica.

## 3. Status padronizados

- IMPLEMENTADO
- IMPLEMENTADO COM PENDENCIAS FUTURAS
- PARCIALMENTE IMPLEMENTADO
- FUTURO REAL
- REQUER MODELAGEM
- REQUER CONFERENCIA NO CODIGO
- AGUARDANDO VALIDACAO VISUAL
- AGUARDANDO TESTE DO USUARIO
- HISTORICO / SUBSTITUIDO POR FLUXO ATUAL
- DESCARTADO / NAO PRIORIZADO

## 4. Quando fazer baixa

- ao final de cada microetapa implementada;
- ao final de cada auditoria documental ou tecnica;
- quando uma pendencia for substituida por outro fluxo;
- quando uma frente futura for parcialmente implementada;
- quando algo depender apenas de validacao visual ou teste do usuario;
- quando uma decisao da usuaria mudar a direcao de uma frente ja documentada.

## 5. Documentos a atualizar conforme o caso

- `docs/STATE.md`: estado atual consolidado.
- `docs/CODEX_RESULTADO.md`: registro da execucao da etapa.
- `docs/MAPA_RECLASSIFICACAO.md`: itens em duvida, reclassificacao, substituicao ou acompanhamento.
- `docs/ROADMAP_FINANCEIRO.md`: pendencias futuras, status de roadmap e proximos recortes.
- `docs/CEREBRO_PROJETO.md`: diretriz permanente.
- `docs/REGRAS_NEGOCIO.md`: regra permanente de negocio.
- `docs/INDICE_PROJETO.md`: referencia rapida, quando houver novo documento ou rotina.

## 6. Regra de seguranca

- nao apagar historico util;
- nao reescrever documentos inteiros sem autorizacao;
- fazer baixa por acrescimo, consolidacao ou ajuste cirurgico;
- se houver divergencia entre codigo, documentacao e chat, considerar o codigo como estado real e registrar a divergencia;
- se houver duvida tecnica que exija leitura de codigo, classificar como `REQUER CONFERENCIA NO CODIGO` ate a auditoria;
- se a implementacao existir mas o PDF/tela ainda depender de aprovacao visual, classificar como `AGUARDANDO VALIDACAO VISUAL`.

## 7. Relacao com Git/GitHub

A baixa documental so fica oficialmente consolidada depois de commit e push para o GitHub, conforme `docs/ROTINA_GIT_GITHUB.md`.

Commit local sem push deve ser tratado como pendencia de sincronizacao antes de nova microetapa funcional.
