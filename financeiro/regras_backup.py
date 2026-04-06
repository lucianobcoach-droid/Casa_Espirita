from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from django.core.management.base import CommandError
from django.db import transaction

from financeiro.models import AuditoriaFinanceiro, CategoriaFinanceira, CentroCusto, ContaFinanceira, LancamentoFinanceiro, PessoaFinanceira, RegraLancamentoFinanceiro
from financeiro.rateio_backup import _build_auditoria_payload, _serializar_referencia_categoria, _serializar_referencia_centro_custo, _serializar_referencia_conta, _serializar_referencia_pessoa


FORMATO_BACKUP_REGRAS = 'financeiro.regras.backup.v1'
CONFIRMACAO_RESTAURACAO_REGRAS = 'RESTAURAR_REGRAS_FINANCEIRO'


def _normalizar_json(valor: Any) -> Any:
    if isinstance(valor, dict):
        return {chave: _normalizar_json(item) for chave, item in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_normalizar_json(item) for item in valor]
    return valor


def _snapshot_regra(regra: RegraLancamentoFinanceiro) -> dict[str, Any]:
    snapshot: dict[str, Any] = {}
    for field in regra._meta.concrete_fields:
        if field.name in {'criado_em', 'atualizado_em'}:
            continue
        snapshot[field.name] = getattr(regra, field.attname)
    return _normalizar_json(snapshot)


def _resolver_conta(referencia: dict[str, Any], *, campo: str) -> ContaFinanceira:
    nome = (referencia.get('nome') or '').strip()
    if not nome:
        raise CommandError(f'Backup invalido: {campo} sem nome de conta.')
    queryset = ContaFinanceira.objects.filter(nome=nome)
    total = queryset.count()
    if total == 0:
        raise CommandError(f'Conta "{nome}" nao encontrada para restauracao de regra.')
    if total > 1:
        raise CommandError(f'Conta "{nome}" ambigua para restauracao de regra.')
    return queryset.get()


def _resolver_pessoa(referencia: dict[str, Any] | None, *, obrigatoria: bool) -> PessoaFinanceira | None:
    if not referencia:
        if obrigatoria:
            raise CommandError('Backup invalido: pessoa obrigatoria ausente em regra operacional.')
        return None
    codigo = (referencia.get('codigo') or '').strip()
    if not codigo:
        if obrigatoria:
            raise CommandError('Backup invalido: pessoa obrigatoria sem codigo.')
        return None
    try:
        return PessoaFinanceira.objects.get(codigo=codigo)
    except PessoaFinanceira.DoesNotExist as exc:
        raise CommandError(f'Pessoa "{codigo}" nao encontrada para restauracao de regra.') from exc


def _resolver_centro_custo(referencia: dict[str, Any] | None) -> CentroCusto | None:
    if not referencia:
        return None
    codigo = (referencia.get('codigo') or '').strip()
    if not codigo:
        return None
    try:
        return CentroCusto.objects.get(codigo=codigo)
    except CentroCusto.DoesNotExist as exc:
        raise CommandError(f'Centro de custo "{codigo}" nao encontrado para restauracao de regra.') from exc


def _resolver_categoria(referencia: dict[str, Any] | None, *, obrigatoria: bool) -> CategoriaFinanceira | None:
    if not referencia:
        if obrigatoria:
            raise CommandError('Backup invalido: categoria obrigatoria ausente em regra operacional.')
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
        raise CommandError(f'Categoria "{detalhe}" nao encontrada para restauracao de regra.')
    if total > 1:
        raise CommandError(f'Categoria "{tipo} / {nome}" ambigua para restauracao de regra.')
    return queryset.get()


def construir_payload_backup_regras() -> dict[str, Any]:
    regras = (
        RegraLancamentoFinanceiro.objects.select_related(
            'pessoa',
            'categoria__categoria_pai',
            'centro_custo',
            'conta',
            'conta_destino',
        )
        .order_by('descricao', 'pk')
    )
    itens: list[dict[str, Any]] = []
    for regra in regras:
        itens.append(
            {
                'descricao': regra.descricao,
                'tipo': regra.tipo,
                'ativa': regra.ativa,
                'observacoes': regra.observacoes,
                'conta': _serializar_referencia_conta(regra.conta),
                'conta_destino': _serializar_referencia_conta(regra.conta_destino),
                'pessoa': _serializar_referencia_pessoa(regra.pessoa),
                'categoria': _serializar_referencia_categoria(regra.categoria),
                'centro_custo': _serializar_referencia_centro_custo(regra.centro_custo),
            }
        )
    return {
        'formato': FORMATO_BACKUP_REGRAS,
        'total_regras': len(itens),
        'regras': itens,
    }


def salvar_payload_backup_regras(payload: dict[str, Any], caminho_saida: str | Path) -> Path:
    destino = Path(caminho_saida)
    if not destino.parent.exists():
        destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(_normalizar_json(payload), ensure_ascii=True, indent=2), encoding='utf-8')
    return destino


def carregar_payload_backup_regras(caminho_arquivo: str | Path) -> dict[str, Any]:
    origem = Path(caminho_arquivo)
    try:
        return json.loads(origem.read_text(encoding='utf-8'))
    except FileNotFoundError as exc:
        raise CommandError(f'Arquivo de backup nao encontrado: {origem}') from exc
    except json.JSONDecodeError as exc:
        raise CommandError(f'Arquivo de backup invalido: {origem}') from exc


@dataclass(frozen=True)
class RestauracaoRegrasResumo:
    regras_avaliadas: int
    regras_restauradas: int


def restaurar_payload_backup_regras(
    payload: dict[str, Any],
    *,
    executar: bool,
    origem_auditoria: str = '',
) -> RestauracaoRegrasResumo:
    if payload.get('formato') != FORMATO_BACKUP_REGRAS:
        raise CommandError('Arquivo de backup de regras com formato desconhecido.')
    regras = payload.get('regras')
    if not isinstance(regras, list):
        raise CommandError('Arquivo de backup de regras invalido.')

    regras_para_restaurar: list[dict[str, Any]] = []
    descricoes_vistas: set[tuple[str, str]] = set()
    for item in regras:
        if not isinstance(item, dict):
            raise CommandError('Arquivo de backup de regras invalido: item malformado.')
        descricao = (item.get('descricao') or '').strip()
        tipo = (item.get('tipo') or '').strip()
        if not descricao or not tipo:
            raise CommandError('Arquivo de backup de regras invalido: descricao/tipo ausentes.')

        chave = (descricao.casefold(), tipo)
        if chave in descricoes_vistas:
            raise CommandError(f'Arquivo de backup invalido: regra duplicada "{descricao}" / "{tipo}".')
        descricoes_vistas.add(chave)

        transferencia = tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA
        operacional = tipo in {'receita', 'despesa'}
        conta = _resolver_conta(item.get('conta') or {}, campo='conta')
        conta_destino = _resolver_conta(item.get('conta_destino') or {}, campo='conta_destino') if item.get('conta_destino') else None
        pessoa = _resolver_pessoa(item.get('pessoa'), obrigatoria=operacional)
        categoria = _resolver_categoria(item.get('categoria'), obrigatoria=operacional)
        centro_custo = _resolver_centro_custo(item.get('centro_custo'))

        regra = RegraLancamentoFinanceiro(
            descricao=descricao,
            tipo=tipo,
            pessoa=pessoa,
            categoria=categoria,
            centro_custo=centro_custo,
            conta=conta,
            conta_destino=conta_destino,
            observacoes=item.get('observacoes') or '',
            ativa=bool(item.get('ativa', True)),
        )
        try:
            regra.full_clean()
        except Exception as exc:
            raise CommandError(f'Regra "{descricao}" invalida para restauracao.') from exc

        if transferencia and not conta_destino:
            raise CommandError(f'Regra "{descricao}" de transferencia sem conta_destino.')

        regras_para_restaurar.append(
            {
                'descricao': descricao,
                'tipo': tipo,
                'pessoa': pessoa,
                'categoria': categoria,
                'centro_custo': centro_custo,
                'conta': conta,
                'conta_destino': conta_destino,
                'observacoes': item.get('observacoes') or '',
                'ativa': bool(item.get('ativa', True)),
            }
        )

    if not executar:
        return RestauracaoRegrasResumo(
            regras_avaliadas=len(regras_para_restaurar),
            regras_restauradas=0,
        )

    with transaction.atomic():
        RegraLancamentoFinanceiro.objects.all().delete()
        total = 0
        for dados in regras_para_restaurar:
            regra = RegraLancamentoFinanceiro.objects.create(**dados)
            AuditoriaFinanceiro.objects.create(
                acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
                modelo='RegraLancamentoFinanceiro',
                registro_id=regra.pk,
                usuario=None,
                campos_alterados={
                    **_build_auditoria_payload(None, _snapshot_regra(regra)),
                    'origem_restauracao_regras': {
                        'before': None,
                        'after': origem_auditoria or 'backup tecnico de regras',
                    },
                },
            )
            total += 1

    return RestauracaoRegrasResumo(
        regras_avaliadas=len(regras_para_restaurar),
        regras_restauradas=total,
    )
