from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from django.core.management.base import CommandError
from django.db import transaction
from django.utils import timezone

from financeiro.models import AuditoriaFinanceiro, CategoriaFinanceira, CentroCusto, ContaFinanceira, LancamentoFinanceiro, PessoaFinanceira


FORMATO_BACKUP_RATEIO = 'financeiro.rateio.backup.v1'
CONFIRMACAO_RESTAURACAO_RATEIO = 'RESTAURAR_RATEIOS_FINANCEIRO'


def _normalizar_json(valor: Any) -> Any:
    if isinstance(valor, Decimal):
        return str(valor)
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    if isinstance(valor, dict):
        return {chave: _normalizar_json(item) for chave, item in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_normalizar_json(item) for item in valor]
    return valor


def _snapshot_lancamento(lancamento: LancamentoFinanceiro) -> dict[str, Any]:
    snapshot: dict[str, Any] = {}
    for field in lancamento._meta.concrete_fields:
        if field.name in {'criado_em', 'atualizado_em'}:
            continue
        snapshot[field.name] = _normalizar_json(getattr(lancamento, field.attname))
    return snapshot


def _build_auditoria_payload(
    antes: dict[str, Any] | None,
    depois: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    chaves = set((antes or {}).keys()) | set((depois or {}).keys())
    alteracoes: dict[str, dict[str, Any]] = {}
    for chave in sorted(chaves):
        valor_antes = (antes or {}).get(chave)
        valor_depois = (depois or {}).get(chave)
        if valor_antes != valor_depois:
            alteracoes[chave] = {
                'before': valor_antes,
                'after': valor_depois,
            }
    return alteracoes


def _decimal_texto(valor: Decimal | None) -> str:
    if valor is None:
        return ''
    return format(valor, 'f')


def _data_texto(valor: date | None) -> str:
    if not valor:
        return ''
    return valor.isoformat()


def _resolver_conta(referencia: dict[str, Any], *, campo: str) -> ContaFinanceira:
    nome = (referencia.get('nome') or '').strip()
    if not nome:
        raise CommandError(f'Backup invalido: {campo} sem nome de conta.')
    queryset = ContaFinanceira.objects.filter(nome=nome)
    total = queryset.count()
    if total == 0:
        raise CommandError(f'Conta "{nome}" nao encontrada para restauracao de rateio.')
    if total > 1:
        raise CommandError(f'Conta "{nome}" ambigua para restauracao de rateio.')
    return queryset.get()


def _resolver_pessoa(referencia: dict[str, Any] | None, *, obrigatoria: bool) -> PessoaFinanceira | None:
    if not referencia:
        if obrigatoria:
            raise CommandError('Backup invalido: pessoa obrigatoria ausente em lancamento operacional.')
        return None
    codigo = (referencia.get('codigo') or '').strip()
    if not codigo:
        if obrigatoria:
            raise CommandError('Backup invalido: pessoa obrigatoria sem codigo.')
        return None
    try:
        return PessoaFinanceira.objects.get(codigo=codigo)
    except PessoaFinanceira.DoesNotExist as exc:
        raise CommandError(f'Pessoa "{codigo}" nao encontrada para restauracao de rateio.') from exc


def _resolver_centro_custo(referencia: dict[str, Any] | None) -> CentroCusto | None:
    if not referencia:
        return None
    codigo = (referencia.get('codigo') or '').strip()
    if not codigo:
        return None
    try:
        return CentroCusto.objects.get(codigo=codigo)
    except CentroCusto.DoesNotExist as exc:
        raise CommandError(f'Centro de custo "{codigo}" nao encontrado para restauracao de rateio.') from exc


def _resolver_categoria(referencia: dict[str, Any] | None, *, obrigatoria: bool) -> CategoriaFinanceira | None:
    if not referencia:
        if obrigatoria:
            raise CommandError('Backup invalido: categoria obrigatoria ausente em lancamento operacional.')
        return None

    tipo = (referencia.get('tipo') or '').strip()
    nome = (referencia.get('nome') or '').strip()
    categoria_pai_nome = (referencia.get('categoria_pai_nome') or '').strip()
    if not tipo or not nome:
        if obrigatoria:
            raise CommandError('Backup invalido: categoria obrigatoria sem tipo/nome.')
        return None

    queryset = CategoriaFinanceira.objects.filter(tipo=tipo, nome=nome)
    if categoria_pai_nome:
        queryset = queryset.filter(categoria_pai__nome=categoria_pai_nome)
    else:
        queryset = queryset.filter(categoria_pai__isnull=True)

    total = queryset.count()
    if total == 0:
        detalhe = f'{tipo} / {nome}'
        if categoria_pai_nome:
            detalhe = f'{detalhe} / pai {categoria_pai_nome}'
        raise CommandError(f'Categoria "{detalhe}" nao encontrada para restauracao de rateio.')
    if total > 1:
        raise CommandError(f'Categoria "{tipo} / {nome}" ambigua para restauracao de rateio.')
    return queryset.get()


def _serializar_referencia_conta(conta: ContaFinanceira | None) -> dict[str, str] | None:
    if not conta:
        return None
    return {'nome': conta.nome}


def _serializar_referencia_pessoa(pessoa: PessoaFinanceira | None) -> dict[str, str] | None:
    if not pessoa:
        return None
    return {'codigo': pessoa.codigo, 'nome': pessoa.nome}


def _serializar_referencia_centro_custo(centro_custo: CentroCusto | None) -> dict[str, str] | None:
    if not centro_custo:
        return None
    return {'codigo': centro_custo.codigo, 'nome': centro_custo.nome}


def _serializar_referencia_categoria(categoria: CategoriaFinanceira | None) -> dict[str, str] | None:
    if not categoria:
        return None
    return {
        'tipo': categoria.tipo,
        'nome': categoria.nome,
        'categoria_pai_nome': categoria.categoria_pai.nome if categoria.categoria_pai_id else '',
    }


def _serializar_lancamento_rateado(lancamento: LancamentoFinanceiro) -> dict[str, Any]:
    return {
        'descricao': lancamento.descricao,
        'tipo': lancamento.tipo,
        'status': lancamento.status,
        'valor': _decimal_texto(lancamento.valor),
        'data_competencia': _data_texto(lancamento.data_competencia),
        'data_pagamento': _data_texto(lancamento.data_pagamento),
        'numero_documento': lancamento.numero_documento,
        'observacoes': lancamento.observacoes,
        'conta': _serializar_referencia_conta(lancamento.conta),
        'conta_destino': _serializar_referencia_conta(lancamento.conta_destino),
        'pessoa': _serializar_referencia_pessoa(lancamento.pessoa),
        'categoria': _serializar_referencia_categoria(lancamento.categoria),
        'centro_custo': _serializar_referencia_centro_custo(lancamento.centro_custo),
    }


def construir_payload_backup_rateios(*, grupos_rateio: list[str] | None = None) -> dict[str, Any]:
    queryset = (
        LancamentoFinanceiro.objects.filter(com_rateio=True)
        .exclude(grupo_rateio='')
        .select_related('conta', 'conta_destino', 'pessoa', 'categoria__categoria_pai', 'centro_custo')
        .order_by('grupo_rateio', 'data_competencia', 'pk')
    )
    if grupos_rateio:
        queryset = queryset.filter(grupo_rateio__in=grupos_rateio)

    grupos_payload: list[dict[str, Any]] = []
    grupos_encontrados: dict[str, list[LancamentoFinanceiro]] = {}
    for lancamento in queryset:
        grupos_encontrados.setdefault(lancamento.grupo_rateio, []).append(lancamento)

    for grupo_rateio, itens in grupos_encontrados.items():
        numeros_documento = {(item.numero_documento or '').strip() for item in itens}
        numeros_documento.discard('')
        if len(numeros_documento) > 1:
            raise CommandError(
                f'O grupo de rateio "{grupo_rateio}" possui numeros de documento divergentes e nao pode ser exportado.'
            )

        grupos_payload.append(
            {
                'grupo_rateio': grupo_rateio,
                'numero_documento': next(iter(numeros_documento), ''),
                'total_linhas': len(itens),
                'valor_total': _decimal_texto(sum((item.valor for item in itens), Decimal('0.00'))),
                'linhas': [_serializar_lancamento_rateado(item) for item in itens],
            }
        )

    return {
        'formato': FORMATO_BACKUP_RATEIO,
        'total_grupos': len(grupos_payload),
        'total_linhas': sum(item['total_linhas'] for item in grupos_payload),
        'grupos': grupos_payload,
    }


def salvar_payload_backup_rateios(payload: dict[str, Any], caminho_saida: str | Path) -> Path:
    destino = Path(caminho_saida)
    if not destino.parent.exists():
        destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(_normalizar_json(payload), ensure_ascii=True, indent=2), encoding='utf-8')
    return destino


def carregar_payload_backup_rateios(caminho_arquivo: str | Path) -> dict[str, Any]:
    origem = Path(caminho_arquivo)
    try:
        return json.loads(origem.read_text(encoding='utf-8'))
    except FileNotFoundError as exc:
        raise CommandError(f'Arquivo de backup nao encontrado: {origem}') from exc
    except json.JSONDecodeError as exc:
        raise CommandError(f'Arquivo de backup invalido: {origem}') from exc


@dataclass(frozen=True)
class RestauracaoRateioResumo:
    grupos_avaliados: int
    linhas_avaliadas: int
    grupos_restaurados: int
    linhas_restauradas: int
    linhas_legadas_restauradas: int
    grupos_legados_linha_unica: int


def _validar_regras_restauracao_rateio(
    *,
    grupo_rateio: str,
    tipo: str,
    data_competencia: date,
    data_pagamento: date,
    numero_documento: str,
    pessoa: PessoaFinanceira | None,
    categoria: CategoriaFinanceira | None,
    conta: ContaFinanceira,
    conta_destino: ContaFinanceira | None,
) -> None:
    transferencia = tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA
    lancamento_operacional = tipo in {
        LancamentoFinanceiro.TipoLancamento.RECEITA,
        LancamentoFinanceiro.TipoLancamento.DESPESA,
    }

    if not grupo_rateio:
        raise CommandError('Backup invalido: grupo_rateio obrigatorio em rateio.')
    if not data_competencia or not data_pagamento:
        raise CommandError(f'Grupo "{grupo_rateio}" com data_competencia/data_pagamento ausente.')
    if data_pagamento < data_competencia:
        raise CommandError(f'Grupo "{grupo_rateio}" com data_pagamento anterior a data_competencia.')
    if transferencia and not conta_destino:
        raise CommandError(f'Grupo "{grupo_rateio}" com transferencia sem conta_destino.')
    if not transferencia and conta_destino:
        raise CommandError(f'Grupo "{grupo_rateio}" com conta_destino fora de transferencia.')
    if conta_destino and conta.pk == conta_destino.pk:
        raise CommandError(f'Grupo "{grupo_rateio}" com conta e conta_destino iguais.')
    if lancamento_operacional and not pessoa:
        raise CommandError(f'Grupo "{grupo_rateio}" com lancamento operacional sem pessoa.')
    if lancamento_operacional and not categoria:
        raise CommandError(f'Grupo "{grupo_rateio}" com lancamento operacional sem categoria.')

    if numero_documento:
        queryset = LancamentoFinanceiro.objects.filter(numero_documento=numero_documento).exclude(
            grupo_rateio=grupo_rateio
        )
        if queryset.exists():
            raise CommandError(
                f'O numero_documento "{numero_documento}" do grupo "{grupo_rateio}" conflita com outro lancamento fora do grupo.'
            )


def restaurar_payload_backup_rateios(
    payload: dict[str, Any],
    *,
    executar: bool,
    origem_auditoria: str = '',
    permitir_grupos_existentes: bool = False,
) -> RestauracaoRateioResumo:
    if payload.get('formato') != FORMATO_BACKUP_RATEIO:
        raise CommandError('Arquivo de backup de rateio com formato desconhecido.')

    grupos = payload.get('grupos')
    if not isinstance(grupos, list) or not grupos:
        raise CommandError('Arquivo de backup de rateio sem grupos validos para restauracao.')

    total_linhas = 0
    linhas_para_restaurar: list[dict[str, Any]] = []
    grupos_rateio_vistos: set[str] = set()
    grupos_legados_linha_unica = 0

    for grupo in grupos:
        if not isinstance(grupo, dict):
            raise CommandError('Arquivo de backup de rateio invalido: grupo malformado.')
        grupo_rateio = (grupo.get('grupo_rateio') or '').strip()
        if not grupo_rateio:
            raise CommandError('Arquivo de backup de rateio invalido: grupo_rateio ausente.')
        if grupo_rateio in grupos_rateio_vistos:
            raise CommandError(f'Arquivo de backup invalido: grupo_rateio duplicado "{grupo_rateio}".')
        grupos_rateio_vistos.add(grupo_rateio)

        if (
            not permitir_grupos_existentes
            and LancamentoFinanceiro.objects.filter(grupo_rateio=grupo_rateio).exists()
        ):
            raise CommandError(
                f'Ja existem lancamentos com o grupo de rateio "{grupo_rateio}" na base atual.'
            )

        linhas = grupo.get('linhas')
        if not isinstance(linhas, list) or len(linhas) < 1:
            raise CommandError(
                f'Arquivo de backup invalido: o grupo "{grupo_rateio}" precisa ter ao menos 1 linha.'
            )
        if len(linhas) == 1:
            grupos_legados_linha_unica += 1

        numero_documento_grupo = (grupo.get('numero_documento') or '').strip()

        for linha in linhas:
            if not isinstance(linha, dict):
                raise CommandError(f'Arquivo de backup invalido: linha malformada no grupo "{grupo_rateio}".')

            tipo = (linha.get('tipo') or '').strip()
            status = (linha.get('status') or '').strip()
            obrigatoria_operacional = tipo in {
                LancamentoFinanceiro.TipoLancamento.RECEITA,
                LancamentoFinanceiro.TipoLancamento.DESPESA,
            }

            conta = _resolver_conta(linha.get('conta') or {}, campo='conta')
            conta_destino = _resolver_conta(linha.get('conta_destino') or {}, campo='conta_destino') if linha.get('conta_destino') else None
            pessoa = _resolver_pessoa(linha.get('pessoa'), obrigatoria=obrigatoria_operacional)
            categoria = _resolver_categoria(linha.get('categoria'), obrigatoria=obrigatoria_operacional)
            centro_custo = _resolver_centro_custo(linha.get('centro_custo'))

            try:
                valor = Decimal(str(linha.get('valor') or '0'))
            except Exception as exc:
                raise CommandError(f'Valor invalido no grupo "{grupo_rateio}".') from exc

            try:
                data_competencia = date.fromisoformat((linha.get('data_competencia') or '').strip())
                data_pagamento = date.fromisoformat((linha.get('data_pagamento') or '').strip())
            except ValueError as exc:
                raise CommandError(
                    f'Data invalida no grupo "{grupo_rateio}". O backup precisa usar datas ISO (AAAA-MM-DD).'
                ) from exc

            numero_documento = (linha.get('numero_documento') or '').strip() or numero_documento_grupo
            if numero_documento_grupo and numero_documento and numero_documento != numero_documento_grupo:
                raise CommandError(
                    f'Linha do grupo "{grupo_rateio}" com numero_documento divergente do grupo.'
                )

            _validar_regras_restauracao_rateio(
                grupo_rateio=grupo_rateio,
                tipo=tipo,
                data_competencia=data_competencia,
                data_pagamento=data_pagamento,
                numero_documento=numero_documento,
                pessoa=pessoa,
                categoria=categoria,
                conta=conta,
                conta_destino=conta_destino,
            )

            linhas_para_restaurar.append(
                {
                    'grupo_rateio': grupo_rateio,
                    'descricao': (linha.get('descricao') or '').strip(),
                    'tipo': tipo,
                    'status': status,
                    'valor': valor,
                    'data_competencia': data_competencia,
                    'data_pagamento': data_pagamento,
                    'numero_documento': numero_documento,
                    'observacoes': linha.get('observacoes') or '',
                    'conta': conta,
                    'conta_destino': conta_destino,
                    'pessoa': pessoa,
                    'categoria': categoria,
                    'centro_custo': centro_custo,
                }
            )
            total_linhas += 1

    if not executar:
        return RestauracaoRateioResumo(
            grupos_avaliados=len(grupos),
            linhas_avaliadas=total_linhas,
            grupos_restaurados=0,
            linhas_restauradas=0,
            linhas_legadas_restauradas=0,
            grupos_legados_linha_unica=grupos_legados_linha_unica,
        )

    with transaction.atomic():
        grupos_restaurados = 0
        linhas_restauradas = 0
        linhas_legadas_restauradas = 0
        grupos_processados: set[str] = set()

        for dados in linhas_para_restaurar:
            lancamento = LancamentoFinanceiro(
                descricao=dados['descricao'],
                tipo=dados['tipo'],
                status=dados['status'],
                valor=dados['valor'],
                com_rateio=True,
                grupo_rateio=dados['grupo_rateio'],
                data_competencia=dados['data_competencia'],
                data_pagamento=dados['data_pagamento'],
                numero_documento=dados['numero_documento'],
                pessoa=dados['pessoa'],
                categoria=dados['categoria'],
                centro_custo=dados['centro_custo'],
                conta=dados['conta'],
                conta_destino=dados['conta_destino'],
                observacoes=dados['observacoes'],
            )
            categoria = dados['categoria']
            if categoria and not categoria.permite_vinculo_em_lancamento:
                agora = timezone.now()
                lancamento.criado_em = agora
                lancamento.atualizado_em = agora
                lancamento.save_base(raw=True, force_insert=True)
                linhas_legadas_restauradas += 1
            else:
                lancamento.save()
            AuditoriaFinanceiro.objects.create(
                acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
                modelo='LancamentoFinanceiro',
                registro_id=lancamento.pk,
                usuario=None,
                campos_alterados={
                    **_build_auditoria_payload(None, _snapshot_lancamento(lancamento)),
                    'origem_restauracao_rateio': {
                        'before': None,
                        'after': origem_auditoria or 'backup tecnico de rateio',
                    },
                    'restauracao_legado_categoria_pai': {
                        'before': None,
                        'after': bool(categoria and not categoria.permite_vinculo_em_lancamento),
                    },
                },
            )
            linhas_restauradas += 1
            if dados['grupo_rateio'] not in grupos_processados:
                grupos_processados.add(dados['grupo_rateio'])
                grupos_restaurados += 1

    return RestauracaoRateioResumo(
        grupos_avaliados=len(grupos),
        linhas_avaliadas=total_linhas,
        grupos_restaurados=grupos_restaurados,
        linhas_restauradas=linhas_restauradas,
        linhas_legadas_restauradas=linhas_legadas_restauradas,
        grupos_legados_linha_unica=grupos_legados_linha_unica,
    )
