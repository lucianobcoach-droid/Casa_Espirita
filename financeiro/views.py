from __future__ import annotations

import json
import math
import unicodedata
from calendar import monthrange
from datetime import date, datetime, timedelta
from decimal import ROUND_CEILING, Decimal
from io import BytesIO
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl
from uuid import uuid4
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import (
    AssinaturaInstitucionalForm,
    CategoriaFinanceiraForm,
    ConfiguracaoInstitucionalForm,
    CentroCustoForm,
    ContaFinanceiraForm,
    LancamentoFinanceiroForm,
    LancamentoFinanceiroGrupoRateioForm,
    PessoaFinanceiraForm,
    categorias_vinculaveis_queryset,
)
from .models import (
    AssinaturaInstitucional,
    AuditoriaFinanceiro,
    CategoriaFinanceira,
    ConfiguracaoInstitucional,
    CentroCusto,
    ContaFinanceira,
    LancamentoFinanceiro,
    PessoaFinanceira,
    RegraLancamentoFinanceiro,
)
from .permissoes import FinanceiroPermissaoMixin, usuario_possui_permissao


LANCAMENTO_ORDENACOES_LISTAGEM = {
    'descricao': ('descricao', 'asc'),
    '-descricao': ('descricao', 'desc'),
    'pessoa': ('pessoa', 'asc'),
    '-pessoa': ('pessoa', 'desc'),
    'tipo': ('tipo', 'asc'),
    '-tipo': ('tipo', 'desc'),
    'status': ('status', 'asc'),
    '-status': ('status', 'desc'),
    'data': ('data', 'asc'),
    '-data': ('data', 'desc'),
    'valor': ('valor', 'asc'),
    '-valor': ('valor', 'desc'),
}
LANCAMENTO_ORDENACAO_PADRAO = '-data'
LANCAMENTO_COLUNAS_ORDENAVEIS = ('descricao', 'tipo', 'status', 'valor', 'pessoa', 'data')
LANCAMENTO_LISTAGEM_POR_PAGINA_OPCOES = (25, 50, 100, 200)
LANCAMENTO_LISTAGEM_POR_PAGINA_PADRAO = 50
LANCAMENTO_LISTAGEM_COLUNAS_SESSAO = 'financeiro_lancamentos_colunas_configuraveis'
LANCAMENTO_LISTAGEM_COLUNAS_ESSENCIAIS = ('data_pagamento', 'tipo', 'descricao', 'valor')
LANCAMENTO_LISTAGEM_COLUNAS_CONFIGURAVEIS = (
    'favorecido',
    'conta_origem',
    'conta_destino',
    'status',
    'categoria',
    'centro_custo',
    'data_competencia',
    'numero_documento',
    'observacoes',
)
LANCAMENTO_LISTAGEM_COLUNAS_CONFIGURAVEIS_PADRAO = ()
LANCAMENTO_LISTAGEM_COLUNAS_META = {
    'data_pagamento': {'rotulo': 'Data pagamento', 'ordenacao': 'data', 'essencial': True},
    'tipo': {'rotulo': 'Tipo', 'ordenacao': 'tipo', 'essencial': True},
    'descricao': {'rotulo': 'Descricao', 'ordenacao': 'descricao', 'essencial': True},
    'valor': {'rotulo': 'Valor', 'ordenacao': 'valor', 'essencial': True},
    'favorecido': {'rotulo': 'Favorecido', 'ordenacao': 'pessoa', 'essencial': False},
    'conta_origem': {'rotulo': 'Conta origem', 'ordenacao': '', 'essencial': False},
    'conta_destino': {'rotulo': 'Conta destino', 'ordenacao': '', 'essencial': False},
    'status': {'rotulo': 'Status', 'ordenacao': 'status', 'essencial': False},
    'categoria': {'rotulo': 'Categoria', 'ordenacao': '', 'essencial': False},
    'centro_custo': {'rotulo': 'Centro de custo', 'ordenacao': '', 'essencial': False},
    'data_competencia': {'rotulo': 'Data competencia', 'ordenacao': '', 'essencial': False},
    'numero_documento': {'rotulo': 'Documento', 'ordenacao': '', 'essencial': False},
    'observacoes': {'rotulo': 'Observacoes', 'ordenacao': '', 'essencial': False},
}
MESES_PT_BR = (
    'Janeiro',
    'Fevereiro',
    'Março',
    'Abril',
    'Maio',
    'Junho',
    'Julho',
    'Agosto',
    'Setembro',
    'Outubro',
    'Novembro',
    'Dezembro',
)
EVOLUCAO_CATEGORIAS_SERIES_CORES = (
    '#1f5fbf',
    '#b73a32',
    '#2f855a',
    '#8a5a10',
    '#7c3aed',
    '#0f766e',
    '#c2410c',
    '#475569',
)


def _auditoria_usuario(request):
    usuario = getattr(request, 'user', None)
    if usuario and getattr(usuario, 'is_authenticated', False):
        return usuario
    return None


def _auditoria_normalizar_valor(valor):
    if isinstance(valor, Decimal):
        return str(valor)
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    if hasattr(valor, 'pk'):
        return valor.pk
    return valor


def _snapshot_model(instance, *, ignore_fields: set[str] | None = None) -> dict[str, object]:
    snapshot: dict[str, object] = {}
    ignore_fields = ignore_fields or set()
    for field in instance._meta.concrete_fields:
        if field.name in ignore_fields:
            continue
        snapshot[field.name] = _auditoria_normalizar_valor(getattr(instance, field.attname))
    return snapshot


def _snapshot_lancamento(lancamento: LancamentoFinanceiro) -> dict[str, object]:
    return _snapshot_model(lancamento, ignore_fields={'criado_em', 'atualizado_em'})


def _snapshot_conta(conta: ContaFinanceira) -> dict[str, object]:
    return _snapshot_model(conta, ignore_fields={'criado_em', 'atualizado_em'})


def _snapshot_pessoa(pessoa: PessoaFinanceira) -> dict[str, object]:
    return _snapshot_model(pessoa, ignore_fields={'criado_em', 'atualizado_em'})


def _snapshot_categoria(categoria: CategoriaFinanceira) -> dict[str, object]:
    return _snapshot_model(categoria, ignore_fields={'criado_em', 'atualizado_em'})


def _snapshot_centro_custo(centro_custo: CentroCusto) -> dict[str, object]:
    return _snapshot_model(centro_custo, ignore_fields={'criado_em', 'atualizado_em'})


def _snapshot_assinatura(assinatura: AssinaturaInstitucional) -> dict[str, object]:
    return _snapshot_model(assinatura, ignore_fields={'criado_em', 'atualizado_em'})


def _snapshot_configuracao(configuracao: ConfiguracaoInstitucional) -> dict[str, object]:
    return _snapshot_model(configuracao, ignore_fields={'criado_em', 'atualizado_em'})


def _build_auditoria_payload(
    antes: dict[str, object] | None,
    depois: dict[str, object] | None,
) -> dict[str, dict[str, object]]:
    chaves = set((antes or {}).keys()) | set((depois or {}).keys())
    alteracoes: dict[str, dict[str, object]] = {}

    for chave in sorted(chaves):
        valor_antes = (antes or {}).get(chave)
        valor_depois = (depois or {}).get(chave)
        if valor_antes != valor_depois:
            alteracoes[chave] = {
                'before': valor_antes,
                'after': valor_depois,
            }

    return alteracoes


def _registrar_auditoria_lancamento(
    *,
    request,
    acao: str,
    lancamento: LancamentoFinanceiro,
    antes: dict[str, object] | None = None,
    depois: dict[str, object] | None = None,
) -> AuditoriaFinanceiro:
    return AuditoriaFinanceiro.objects.create(
        acao=acao,
        modelo='LancamentoFinanceiro',
        registro_id=lancamento.pk,
        usuario=_auditoria_usuario(request),
        campos_alterados=_build_auditoria_payload(antes, depois),
    )


def _registrar_auditoria_conta(
    *,
    request,
    acao: str,
    conta: ContaFinanceira,
    antes: dict[str, object] | None = None,
    depois: dict[str, object] | None = None,
) -> AuditoriaFinanceiro:
    return AuditoriaFinanceiro.objects.create(
        acao=acao,
        modelo='ContaFinanceira',
        registro_id=conta.pk,
        usuario=_auditoria_usuario(request),
        campos_alterados=_build_auditoria_payload(antes, depois),
    )


def _registrar_auditoria_pessoa(
    *,
    request,
    acao: str,
    pessoa: PessoaFinanceira,
    antes: dict[str, object] | None = None,
    depois: dict[str, object] | None = None,
) -> AuditoriaFinanceiro:
    return AuditoriaFinanceiro.objects.create(
        acao=acao,
        modelo='PessoaFinanceira',
        registro_id=pessoa.pk,
        usuario=_auditoria_usuario(request),
        campos_alterados=_build_auditoria_payload(antes, depois),
    )


def _registrar_auditoria_categoria(
    *,
    request,
    acao: str,
    categoria: CategoriaFinanceira,
    antes: dict[str, object] | None = None,
    depois: dict[str, object] | None = None,
) -> AuditoriaFinanceiro:
    return AuditoriaFinanceiro.objects.create(
        acao=acao,
        modelo='CategoriaFinanceira',
        registro_id=categoria.pk,
        usuario=_auditoria_usuario(request),
        campos_alterados=_build_auditoria_payload(antes, depois),
    )


def _registrar_auditoria_centro_custo(
    *,
    request,
    acao: str,
    centro_custo: CentroCusto,
    antes: dict[str, object] | None = None,
    depois: dict[str, object] | None = None,
) -> AuditoriaFinanceiro:
    return AuditoriaFinanceiro.objects.create(
        acao=acao,
        modelo='CentroCusto',
        registro_id=centro_custo.pk,
        usuario=_auditoria_usuario(request),
        campos_alterados=_build_auditoria_payload(antes, depois),
    )


def _registrar_auditoria_assinatura(
    *,
    request,
    acao: str,
    assinatura: AssinaturaInstitucional,
    antes: dict[str, object] | None = None,
    depois: dict[str, object] | None = None,
) -> AuditoriaFinanceiro:
    return AuditoriaFinanceiro.objects.create(
        acao=acao,
        modelo='AssinaturaInstitucional',
        registro_id=assinatura.pk,
        usuario=_auditoria_usuario(request),
        campos_alterados=_build_auditoria_payload(antes, depois),
    )


def _registrar_auditoria_configuracao(
    *,
    request,
    acao: str,
    configuracao: ConfiguracaoInstitucional,
    antes: dict[str, object] | None = None,
    depois: dict[str, object] | None = None,
) -> AuditoriaFinanceiro:
    return AuditoriaFinanceiro.objects.create(
        acao=acao,
        modelo='ConfiguracaoInstitucional',
        registro_id=configuracao.pk,
        usuario=_auditoria_usuario(request),
        campos_alterados=_build_auditoria_payload(antes, depois),
    )


def _criar_regra_automatica_lancamento(lancamento: LancamentoFinanceiro) -> RegraLancamentoFinanceiro:
    return RegraLancamentoFinanceiro.objects.create(
        descricao=lancamento.descricao,
        tipo=lancamento.tipo,
        pessoa=lancamento.pessoa,
        categoria=lancamento.categoria,
        centro_custo=lancamento.centro_custo,
        conta=lancamento.conta,
        conta_destino=lancamento.conta_destino,
        observacoes=lancamento.observacoes,
        ativa=True,
    )


UNIDADES_EXTENSO = (
    'zero',
    'um',
    'dois',
    'tres',
    'quatro',
    'cinco',
    'seis',
    'sete',
    'oito',
    'nove',
    'dez',
    'onze',
    'doze',
    'treze',
    'quatorze',
    'quinze',
    'dezesseis',
    'dezessete',
    'dezoito',
    'dezenove',
)
DEZENAS_EXTENSO = (
    '',
    '',
    'vinte',
    'trinta',
    'quarenta',
    'cinquenta',
    'sessenta',
    'setenta',
    'oitenta',
    'noventa',
)
CENTENAS_EXTENSO = (
    '',
    'cento',
    'duzentos',
    'trezentos',
    'quatrocentos',
    'quinhentos',
    'seiscentos',
    'setecentos',
    'oitocentos',
    'novecentos',
)
MESES_EXTENSO = (
    'janeiro',
    'fevereiro',
    'março',
    'abril',
    'maio',
    'junho',
    'julho',
    'agosto',
    'setembro',
    'outubro',
    'novembro',
    'dezembro',
)

LANCAMENTO_IMPORTACAO_MODELO_MAX_RATEIOS = 5

LANCAMENTO_IMPORTACAO_MODELO_COLUNAS_LEGADO = [
    'tipo',
    'status',
    'descricao',
    'valor',
    'data_competencia',
    'data_pagamento',
    'pessoa_nome',
    'categoria_nome',
    'centro_custo_nome',
    'conta_nome',
    'conta_destino_nome',
    'numero_documento',
    'observacoes',
]

LANCAMENTO_IMPORTACAO_MODELO_COLUNAS_GERAIS = [
    'tipo',
    'status',
    'descricao',
    'valor_total_documento',
    'data_competencia',
    'data_pagamento',
    'pessoa_nome',
    'conta_nome',
    'conta_destino_nome',
    'numero_documento',
    'observacoes',
]

LANCAMENTO_IMPORTACAO_MODELO_BLOCOS_RATEIO = [
    (
        f'categoria_nome_{indice}',
        f'centro_custo_nome_{indice}',
        f'valor_{indice}',
    )
    for indice in range(1, LANCAMENTO_IMPORTACAO_MODELO_MAX_RATEIOS + 1)
]

LANCAMENTO_IMPORTACAO_MODELO_COLUNAS = [
    *LANCAMENTO_IMPORTACAO_MODELO_COLUNAS_GERAIS,
    *[
        coluna
        for bloco in LANCAMENTO_IMPORTACAO_MODELO_BLOCOS_RATEIO
        for coluna in bloco
    ],
]

LANCAMENTO_IMPORTACAO_MODELO_ROTULOS = {
    'valor_total_documento': 'Valor total do documento',
    'tipo': 'Tipo',
    'status': 'Status',
    'descricao': 'DescriÃ§Ã£o',
    'valor': 'Valor',
    'data_competencia': 'Data de competÃªncia',
    'data_pagamento': 'Data de pagamento',
    'pessoa_nome': 'Favorecido',
    'categoria_nome': 'Categoria',
    'centro_custo_nome': 'Centro de custo',
    'conta_nome': 'Conta origem',
    'conta_destino_nome': 'Conta destino',
    'numero_documento': 'Documento',
    'observacoes': 'ObservaÃ§Ãµes',
    **{
        f'categoria_nome_{indice}': f'Categoria {indice}'
        for indice in range(1, LANCAMENTO_IMPORTACAO_MODELO_MAX_RATEIOS + 1)
    },
    **{
        f'centro_custo_nome_{indice}': f'Centro de custo {indice}'
        for indice in range(1, LANCAMENTO_IMPORTACAO_MODELO_MAX_RATEIOS + 1)
    },
    **{
        f'valor_{indice}': f'Valor {indice}'
        for indice in range(1, LANCAMENTO_IMPORTACAO_MODELO_MAX_RATEIOS + 1)
    },
}

LANCAMENTO_IMPORTACAO_ORIENTACOES = {
    'valor_total_documento': 'Informe o valor total do documento. Em receita/despesa, ele precisa bater com a soma dos blocos preenchidos.',
    'tipo': 'Use receita, despesa ou transferencia.',
    'status': 'Use aberto, quitado ou cancelado.',
    'descricao': 'Preencha uma descriÃ§Ã£o para identificar o lanÃ§amento.',
    'data_competencia': 'Use o formato dd/mm/aaaa.',
    'data_pagamento': 'Use o formato dd/mm/aaaa.',
    'pessoa_nome': 'Revise o nome do favorecido exatamente como esta cadastrado.',
    'conta_nome': 'Revise a conta origem ou preencha uma conta ja cadastrada.',
    'conta_destino_nome': 'Preencha uma conta destino ja cadastrada quando o tipo for transferencia.',
    'numero_documento': 'Revise duplicidade ou deixe em branco para geraÃ§Ã£o automÃ¡tica.',
    **{
        f'categoria_nome_{indice}': 'Use uma subcategoria jÃ¡ cadastrada e compatÃ­vel com o tipo do lanÃ§amento.'
        for indice in range(1, LANCAMENTO_IMPORTACAO_MODELO_MAX_RATEIOS + 1)
    },
    **{
        f'centro_custo_nome_{indice}': 'Revise o nome exatamente como estÃ¡ cadastrado ou deixe em branco quando nÃ£o se aplicar.'
        for indice in range(1, LANCAMENTO_IMPORTACAO_MODELO_MAX_RATEIOS + 1)
    },
    **{
        f'valor_{indice}': 'Informe um nÃºmero maior que zero, com vÃ­rgula ou ponto decimal, para cada bloco usado.'
        for indice in range(1, LANCAMENTO_IMPORTACAO_MODELO_MAX_RATEIOS + 1)
    },
}

LANCAMENTO_IMPORTACAO_CAMPOS_MODELO = {
    'pessoa': 'pessoa_nome',
    'conta': 'conta_nome',
    'conta_destino': 'conta_destino_nome',
}

LANCAMENTO_IMPORTACAO_ABAS_OBRIGATORIAS = ['Modelo', 'InstruÃ§Ãµes']

LANCAMENTO_EXPORTACAO_COLUNAS = [
    *LANCAMENTO_IMPORTACAO_MODELO_COLUNAS,
]

LANCAMENTO_IMPORTACAO_MODELO_INSTRUCOES = [
    [
        'Finalidade',
        'Use esta planilha como base para preparar e reimportar lancamentos simples e lancamentos com ate 5 blocos de rateio na mesma linha.',
    ],
    [
        'CabeÃ§alhos',
        'Mantenha os nomes das colunas da aba Modelo exatamente como estao. O mesmo contrato vale para exportacao e importacao.',
    ],
    [
        'Lancamento simples',
        'Para receita ou despesa simples, preencha apenas categoria_nome_1, valor_1 e, se quiser, centro_custo_nome_1. Deixe os demais blocos em branco.',
    ],
    [
        'Lancamento com rateio',
        'Use uma unica linha por documento e distribua o rateio entre os blocos 1 a 5, sem deixar buracos entre eles.',
    ],
    [
        'Validacao central',
        'Em receita ou despesa, a soma dos valores dos blocos preenchidos precisa fechar exatamente com valor_total_documento.',
    ],
    [
        'Transferencia',
        'Transferencias continuam sem suporte a rateio. Nelas, deixe todos os blocos de rateio em branco e informe apenas valor_total_documento.',
    ],
    [
        'Limite do fluxo comum',
        'O fluxo comum aceita no maximo 5 blocos de rateio por documento. Grupos maiores continuam exigindo o caminho tecnico de backup e restauracao.',
    ],
    [
        'Datas e valores',
        'Use datas no formato dd/mm/aaaa. Se necessario, o sistema tambem aceita AAAA-MM-DD. Para valores, use numero com virgula ou ponto decimal.',
    ],
    [
        'Campos opcionais',
        'Deixe em branco os campos que nao se aplicarem ao lancamento, como centro_custo_nome, numero_documento, observacoes e conta_destino_nome fora de transferencias.',
    ],
]

CADASTRO_AUXILIAR_PLANILHAS_BASE = {
    'contas': {
        'titulo': 'Contas financeiras',
        'arquivo': 'planilha_base_contas_financeiras.xlsx',
        'permissao': 'financeiro.contas.criar',
        'colunas': ['nome', 'descricao', 'saldo_inicial', 'data_saldo_inicial', 'ativa'],
        'rotulos': {
            'nome': 'Nome',
            'descricao': 'Descricao',
            'saldo_inicial': 'Saldo inicial',
            'data_saldo_inicial': 'Data do saldo inicial',
            'ativa': 'Ativa',
        },
        'orientacoes': {
            'nome': 'Use um nome unico e facil de reconhecer no modulo financeiro.',
            'saldo_inicial': 'Informe um valor numerico com virgula ou ponto decimal.',
            'data_saldo_inicial': 'Use uma data valida no formato dd/mm/aaaa.',
            'ativa': 'Use true/false, sim/nao, 1/0 ou deixe em branco para considerar ativo.',
        },
        'instrucoes': [
            ['Finalidade', 'Use esta planilha-base para preparar as contas financeiras antes da carga de lancamentos.'],
            ['Cabecalhos', 'Mantenha os nomes das colunas da aba Modelo exatamente como estao.'],
            ['Saldo inicial', 'Informe o saldo inicial com virgula ou ponto decimal.'],
            ['Data do saldo', 'Use dd/mm/aaaa. Se necessario, o sistema tambem pode ler AAAA-MM-DD.'],
            ['Ativa', 'Use true/false, sim/nao, 1/0 ou deixe em branco para considerar ativo.'],
        ],
        'descricao': 'Base de contas para vinculos financeiros e saldo inicial do ambiente.',
        'sucesso': 'contas financeiras',
    },
    'pessoas': {
        'titulo': 'Favorecidos financeiros',
        'arquivo': 'planilha_base_pessoas_financeiras.xlsx',
        'permissao': 'financeiro.pessoas.criar',
        'colunas': ['codigo', 'nome', 'tipo_pessoa', 'documento', 'telefone', 'email', 'observacoes', 'ativo'],
        'rotulos': {
            'codigo': 'Codigo',
            'nome': 'Nome',
            'tipo_pessoa': 'Tipo de favorecido',
            'documento': 'Documento',
            'telefone': 'Telefone',
            'email': 'E-mail',
            'observacoes': 'Observacoes',
            'ativo': 'Ativo',
        },
        'orientacoes': {
            'codigo': 'Use um codigo unico e estavel para cada favorecido.',
            'nome': 'Use um nome unico para evitar ambiguidade na importacao de lancamentos.',
            'tipo_pessoa': 'Use fisica ou juridica. O campo pode ficar em branco quando nao se aplicar.',
            'email': 'Preencha um e-mail valido ou deixe em branco.',
            'ativo': 'Use true/false, sim/nao, 1/0 ou deixe em branco para considerar ativo.',
        },
        'instrucoes': [
            ['Finalidade', 'Use esta planilha-base para preparar favorecidos usados nos lancamentos.'],
            ['Codigo', 'Preencha um codigo unico e estavel para cada favorecido.'],
            ['Tipo de favorecido', 'Use fisica ou juridica. O campo pode ficar em branco quando nao se aplicar.'],
            ['Contato', 'Documento, telefone e email sao opcionais e podem ficar em branco.'],
            ['Ativo', 'Use true/false, sim/nao, 1/0 ou deixe em branco para considerar ativo.'],
        ],
        'descricao': 'Favorecidos e contrapartes usados por receitas e despesas.',
        'sucesso': 'favorecidos financeiros',
    },
    'centros-custo': {
        'titulo': 'Centros de custo',
        'arquivo': 'planilha_base_centros_custo_financeiro.xlsx',
        'permissao': 'financeiro.centros_custo.criar',
        'colunas': ['codigo', 'nome', 'ativo'],
        'rotulos': {
            'codigo': 'Codigo',
            'nome': 'Nome',
            'ativo': 'Ativo',
        },
        'orientacoes': {
            'codigo': 'Use um codigo unico para cada centro de custo.',
            'nome': 'Use um nome unico e consistente com a operacao local.',
            'ativo': 'Use true/false, sim/nao, 1/0 ou deixe em branco para considerar ativo.',
        },
        'instrucoes': [
            ['Finalidade', 'Use esta planilha-base para preparar os centros de custo antes da carga de lancamentos.'],
            ['Codigo', 'Preencha um codigo unico para cada centro de custo.'],
            ['Nome', 'Use um nome claro e consistente com a operacao local.'],
            ['Ativo', 'Use true/false, sim/nao, 1/0 ou deixe em branco para considerar ativo.'],
        ],
        'descricao': 'Centros usados nos filtros e relatorios operacionais.',
        'sucesso': 'centros de custo',
    },
    'categorias': {
        'titulo': 'Categorias e subcategorias',
        'arquivo': 'planilha_base_categorias_financeiras.xlsx',
        'permissao': 'financeiro.categorias.criar',
        'colunas': ['nome', 'tipo', 'categoria_pai_nome', 'mensagem_recibo', 'ativo'],
        'rotulos': {
            'nome': 'Nome',
            'tipo': 'Tipo',
            'categoria_pai_nome': 'Categoria pai',
            'mensagem_recibo': 'Mensagem de recibo',
            'ativo': 'Ativo',
        },
        'orientacoes': {
            'nome': 'Use nomes unicos por tipo para evitar ambiguidade nos lancamentos.',
            'tipo': 'Use receita ou despesa.',
            'categoria_pai_nome': 'Deixe em branco nas categorias pai e preencha o nome exato da categoria pai nas subcategorias.',
            'ativo': 'Use true/false, sim/nao, 1/0 ou deixe em branco para considerar ativo.',
        },
        'instrucoes': [
            ['Finalidade', 'Use esta planilha-base para preparar categorias pai e subcategorias do financeiro.'],
            ['Tipo', 'Use receita ou despesa.'],
            ['Hierarquia', 'Deixe categoria_pai_nome em branco nas categorias pai e preencha o nome exato da categoria pai nas subcategorias.'],
            ['Ordem interna', 'Liste primeiro as categorias pai e depois as subcategorias para facilitar a futura carga sequencial.'],
            ['Mensagem de recibo', 'Preencha apenas quando quiser uma mensagem final especifica para recibos dessa categoria.'],
        ],
        'descricao': 'Categorias pai primeiro e subcategorias depois, antes da carga de lancamentos.',
        'sucesso': 'categorias e subcategorias',
    },
}

CADASTRO_AUXILIAR_PLANILHAS_BASE_ORDEM = [
    {
        'slug': 'contas',
        'titulo': CADASTRO_AUXILIAR_PLANILHAS_BASE['contas']['titulo'],
        'dependencia': 'base de contas para vinculos financeiros e saldo inicial do ambiente',
    },
    {
        'slug': 'pessoas',
        'titulo': CADASTRO_AUXILIAR_PLANILHAS_BASE['pessoas']['titulo'],
        'dependencia': 'favorecidos e contrapartes usados por receitas e despesas',
    },
    {
        'slug': 'centros-custo',
        'titulo': CADASTRO_AUXILIAR_PLANILHAS_BASE['centros-custo']['titulo'],
        'dependencia': 'centros usados nos filtros e relatorios operacionais',
    },
    {
        'slug': 'categorias',
        'titulo': CADASTRO_AUXILIAR_PLANILHAS_BASE['categorias']['titulo'],
        'dependencia': 'categorias pai primeiro e subcategorias depois, antes da carga de lancamentos',
    },
]


def _xlsx_coluna_referencia(indice_coluna: int) -> str:
    referencia = ''
    while indice_coluna:
        indice_coluna, resto = divmod(indice_coluna - 1, 26)
        referencia = f'{chr(65 + resto)}{referencia}'
    return referencia


def _xlsx_planilha_xml(linhas: list[list[str]]) -> str:
    linhas_xml = []
    for indice_linha, linha in enumerate(linhas, start=1):
        celulas_xml = []
        for indice_coluna, valor in enumerate(linha, start=1):
            referencia = f'{_xlsx_coluna_referencia(indice_coluna)}{indice_linha}'
            celulas_xml.append(
                f'<c r="{referencia}" t="inlineStr"><is><t>{escape(str(valor))}</t></is></c>'
            )
        linhas_xml.append(f'<row r="{indice_linha}">{"".join(celulas_xml)}</row>')

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(linhas_xml)}</sheetData>'
        '</worksheet>'
    )


def _gerar_arquivo_xlsx(planilhas: list[tuple[str, list[list[str]]]]) -> bytes:
    arquivo = BytesIO()

    with ZipFile(arquivo, 'w', ZIP_DEFLATED) as workbook:
        planilhas_content_types = ''.join(
            f'<Override PartName="/xl/worksheets/sheet{indice}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            for indice, _ in enumerate(planilhas, start=1)
        )
        planilhas_workbook = ''.join(
            f'<sheet name="{escape(nome)}" sheetId="{indice}" r:id="rId{indice}"/>'
            for indice, (nome, _) in enumerate(planilhas, start=1)
        )
        planilhas_rels = ''.join(
            f'<Relationship Id="rId{indice}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{indice}.xml"/>'
            for indice, _ in enumerate(planilhas, start=1)
        )

        workbook.writestr(
            '[Content_Types].xml',
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            f'{planilhas_content_types}'
            '</Types>',
        )
        workbook.writestr(
            '_rels/.rels',
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>',
        )
        workbook.writestr(
            'xl/workbook.xml',
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets>'
            f'{planilhas_workbook}'
            '</sheets>'
            '</workbook>',
        )
        workbook.writestr(
            'xl/_rels/workbook.xml.rels',
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'{planilhas_rels}'
            '</Relationships>',
        )

        for indice, (_, linhas) in enumerate(planilhas, start=1):
            workbook.writestr(
                f'xl/worksheets/sheet{indice}.xml',
                _xlsx_planilha_xml(linhas),
            )

    return arquivo.getvalue()


def _gerar_planilha_modelo_lancamentos_xlsx() -> bytes:
    return _gerar_arquivo_xlsx(
        [
            ('Modelo', [LANCAMENTO_IMPORTACAO_MODELO_COLUNAS]),
            ('InstruÃ§Ãµes', [['Item', 'OrientaÃ§Ã£o'], *LANCAMENTO_IMPORTACAO_MODELO_INSTRUCOES]),
        ]
    )


def _gerar_planilha_base_cadastro_auxiliar_xlsx(slug: str) -> bytes:
    configuracao = CADASTRO_AUXILIAR_PLANILHAS_BASE[slug]
    return _gerar_arquivo_xlsx(
        [
            ('Modelo', [configuracao['colunas']]),
            ('Instrucoes', [['Item', 'Orientacao'], *configuracao['instrucoes']]),
        ]
    )


def _formatar_data_exportacao_auxiliar(valor) -> str:
    if not valor:
        return ''
    return valor.strftime('%d/%m/%Y')


def _formatar_decimal_exportacao_auxiliar(valor) -> str:
    if valor is None:
        return ''
    return f'{valor:.2f}'.replace('.', ',')


def _formatar_booleano_exportacao_auxiliar(valor) -> str:
    if valor is None:
        return ''
    return 'true' if valor else 'false'


def _linha_exportacao_cadastro_auxiliar(slug: str, registro) -> list[str]:
    if slug == 'contas':
        return [
            registro.nome,
            registro.descricao or '',
            _formatar_decimal_exportacao_auxiliar(registro.saldo_inicial),
            _formatar_data_exportacao_auxiliar(registro.data_saldo_inicial),
            _formatar_booleano_exportacao_auxiliar(registro.ativa),
        ]
    if slug == 'pessoas':
        return [
            registro.codigo or '',
            registro.nome,
            (registro.tipo_pessoa or '').lower(),
            registro.documento or '',
            registro.telefone or '',
            registro.email or '',
            registro.observacoes or '',
            _formatar_booleano_exportacao_auxiliar(registro.ativo),
        ]
    if slug == 'centros-custo':
        return [
            registro.codigo or '',
            registro.nome,
            _formatar_booleano_exportacao_auxiliar(registro.ativo),
        ]
    if slug == 'categorias':
        return [
            registro.nome,
            (registro.tipo or '').lower(),
            registro.categoria_pai.nome if registro.categoria_pai_id else '',
            registro.mensagem_recibo or '',
            _formatar_booleano_exportacao_auxiliar(registro.ativo),
        ]
    return []


def _gerar_planilha_exportacao_cadastro_auxiliar_xlsx(slug: str, registros) -> bytes:
    configuracao = CADASTRO_AUXILIAR_PLANILHAS_BASE[slug]
    colunas = configuracao['colunas']
    linhas = [colunas]
    for registro in registros:
        linhas.append(_linha_exportacao_cadastro_auxiliar(slug, registro))
    return _gerar_arquivo_xlsx([('Exportacao', linhas)])


def _linha_exportacao_lancamento(
    lancamentos_documento: list[LancamentoFinanceiro],
) -> list[str]:
    principal = lancamentos_documento[0]
    valor_total_documento = sum(
        (item.valor for item in lancamentos_documento),
        Decimal('0.00'),
    )
    linha = [
        principal.tipo,
        principal.status,
        principal.descricao,
        f'{valor_total_documento:.2f}'.replace('.', ','),
        principal.data_competencia.strftime('%d/%m/%Y'),
        principal.data_pagamento.strftime('%d/%m/%Y') if principal.data_pagamento else '',
        principal.pessoa.nome if principal.pessoa_id else '',
        principal.conta.nome if principal.conta_id else '',
        principal.conta_destino.nome if principal.conta_destino_id else '',
        principal.numero_documento,
        principal.observacoes,
    ]

    for indice_bloco in range(LANCAMENTO_IMPORTACAO_MODELO_MAX_RATEIOS):
        if indice_bloco < len(lancamentos_documento):
            lancamento = lancamentos_documento[indice_bloco]
            linha.extend([
                lancamento.categoria.nome if lancamento.categoria_id else '',
                lancamento.centro_custo.nome if lancamento.centro_custo_id else '',
                f'{lancamento.valor:.2f}'.replace('.', ','),
            ])
        else:
            linha.extend(['', '', ''])

    return linha


def _ordenar_linhas_grupo_rateio(linhas_grupo: list[LancamentoFinanceiro]) -> list[LancamentoFinanceiro]:
    return sorted(
        linhas_grupo,
        key=lambda item: (
            item.data_pagamento or item.data_competencia,
            item.data_competencia,
            item.pk,
        ),
    )


def _grupo_rateio_ultrapassa_layout_comum(linhas_grupo: list[LancamentoFinanceiro]) -> bool:
    return len(linhas_grupo) > LANCAMENTO_IMPORTACAO_MODELO_MAX_RATEIOS


def _grupos_rateio_fora_do_layout_comum(
    lancamentos: list[LancamentoFinanceiro],
) -> list[tuple[str, int]]:
    grupos: dict[str, list[LancamentoFinanceiro]] = {}
    for lancamento in lancamentos:
        grupo_rateio = (lancamento.grupo_rateio or '').strip()
        if lancamento.com_rateio and grupo_rateio:
            grupos.setdefault(grupo_rateio, []).append(lancamento)

    return [
        (grupo, len(linhas_grupo))
        for grupo, linhas_grupo in sorted(grupos.items())
        if _grupo_rateio_ultrapassa_layout_comum(linhas_grupo)
    ]


def _mensagem_grupos_rateio_fora_do_layout_comum(grupos: list[tuple[str, int]]) -> str:
    grupos_texto = ', '.join(
        f'{grupo} ({quantidade} linhas)'
        for grupo, quantidade in grupos
    )
    return (
        'A exportacao comum de lancamentos aceita no maximo '
        f'{LANCAMENTO_IMPORTACAO_MODELO_MAX_RATEIOS} rateios por documento. '
        'Os seguintes grupos ultrapassam esse limite: '
        f'{grupos_texto}. Use o caminho tecnico para esses casos.'
    )


def _gerar_planilha_exportacao_lancamentos_xlsx(lancamentos) -> bytes:
    lancamentos_lista = list(lancamentos)
    grupos_fora_layout = _grupos_rateio_fora_do_layout_comum(lancamentos_lista)
    if grupos_fora_layout:
        raise ValidationError(_mensagem_grupos_rateio_fora_do_layout_comum(grupos_fora_layout))

    linhas = [LANCAMENTO_IMPORTACAO_MODELO_COLUNAS]
    grupos_processados: set[str] = set()

    for lancamento in lancamentos_lista:
        grupo_rateio = (lancamento.grupo_rateio or '').strip()
        if lancamento.com_rateio and grupo_rateio:
            if grupo_rateio in grupos_processados:
                continue

            linhas_grupo = _ordenar_linhas_grupo_rateio(
                [item for item in lancamentos_lista if (item.grupo_rateio or '').strip() == grupo_rateio]
            )
            linhas.append(_linha_exportacao_lancamento(linhas_grupo))
            grupos_processados.add(grupo_rateio)
            continue

        linhas.append(_linha_exportacao_lancamento([lancamento]))

    return _gerar_arquivo_xlsx(
        [
            ('Modelo', linhas),
            ('Instrucoes', [['Item', 'Orientacao'], *LANCAMENTO_IMPORTACAO_MODELO_INSTRUCOES]),
        ]
    )


def _xlsx_normalizar_target_relacao(target: str) -> str:
    if target.startswith('/'):
        return target.lstrip('/')
    if target.startswith('xl/'):
        return target
    return f'xl/{target}'


def _xlsx_ler_strings_compartilhadas(arquivo_xlsx: ZipFile) -> list[str]:
    if 'xl/sharedStrings.xml' not in arquivo_xlsx.namelist():
        return []

    shared_strings_tree = ElementTree.fromstring(arquivo_xlsx.read('xl/sharedStrings.xml'))
    namespace = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    valores = []

    for item in shared_strings_tree.findall('main:si', namespace):
        partes = [
            texto.text or ''
            for texto in item.findall('.//main:t', namespace)
        ]
        valores.append(''.join(partes))

    return valores


def _xlsx_ler_valor_celula(celula, shared_strings: list[str], namespace: dict[str, str]) -> str:
    tipo_celula = celula.get('t', '')

    if tipo_celula == 'inlineStr':
        texto = celula.find('main:is/main:t', namespace)
        return (texto.text or '').strip() if texto is not None else ''

    valor = celula.find('main:v', namespace)
    if valor is None or not valor.text:
        return ''

    if tipo_celula == 's':
        try:
            return shared_strings[int(valor.text)].strip()
        except (ValueError, IndexError):
            return ''

    return valor.text.strip()


def _xlsx_indice_coluna_celula(celula_referencia: str) -> int:
    letras_coluna = ''.join(caractere for caractere in (celula_referencia or '') if caractere.isalpha())
    if not letras_coluna:
        return 0

    indice_coluna = 0
    for letra in letras_coluna.upper():
        indice_coluna = indice_coluna * 26 + (ord(letra) - 64)
    return indice_coluna


def _xlsx_ler_linhas_planilha(
    arquivo_xlsx: ZipFile,
    caminho_planilha: str,
    shared_strings: list[str],
    namespace: dict[str, str],
    quantidade_colunas: int,
) -> list[tuple[int, list[str]]]:
    planilha_tree = ElementTree.fromstring(arquivo_xlsx.read(caminho_planilha))
    linhas = []

    for indice_padrao, linha_xml in enumerate(
        planilha_tree.findall('main:sheetData/main:row', namespace),
        start=1,
    ):
        numero_linha = int(linha_xml.get('r') or indice_padrao)
        valores_linha = [''] * quantidade_colunas

        for indice_celula, celula in enumerate(linha_xml.findall('main:c', namespace), start=1):
            indice_coluna = _xlsx_indice_coluna_celula(celula.get('r', '')) or indice_celula
            if 1 <= indice_coluna <= quantidade_colunas:
                valores_linha[indice_coluna - 1] = _xlsx_ler_valor_celula(
                    celula,
                    shared_strings,
                    namespace,
                )

        linhas.append((numero_linha, valores_linha))

    return linhas


def _parse_decimal_importacao_lancamento(valor: str) -> Decimal | None:
    valor_normalizado = (valor or '').strip()
    if not valor_normalizado:
        return None

    if ',' in valor_normalizado:
        valor_normalizado = valor_normalizado.replace('.', '').replace(',', '.')
    try:
        return Decimal(valor_normalizado)
    except Exception:
        return None


def _parse_data_importacao_lancamento(valor: str) -> date | None:
    valor_normalizado = (valor or '').strip()
    if not valor_normalizado:
        return None

    for formato_data in ('%d/%m/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(valor_normalizado, formato_data).date()
        except ValueError:
            pass

    try:
        dias_excel = Decimal(valor_normalizado)
    except Exception:
        return None

    if dias_excel < 1:
        return None

    return date(1899, 12, 30) + timedelta(days=int(dias_excel))


def _normalizar_nome_importacao_lancamento(valor: str) -> str:
    return (valor or '').strip().lower()


def _normalizar_codigo_importacao(valor: str) -> str:
    return (valor or '').strip().lower()


def _normalizar_nome_aba_planilha_xlsx(valor: str) -> str:
    valor_normalizado = unicodedata.normalize('NFKD', valor or '')
    valor_sem_acento = ''.join(
        caractere
        for caractere in valor_normalizado
        if not unicodedata.combining(caractere)
    )
    return valor_sem_acento.strip().lower()


def _texto_ordenacao_insensivel(valor: object) -> str:
    valor_normalizado = unicodedata.normalize('NFKD', str(valor or ''))
    valor_sem_acento = ''.join(
        caractere
        for caractere in valor_normalizado
        if not unicodedata.combining(caractere)
    )
    return valor_sem_acento.strip().lower()


def _resolver_valor_ordenacao(item: object, caminho: str) -> object:
    valor = item
    for parte in caminho.split('__'):
        if isinstance(valor, dict):
            valor = valor.get(parte, '')
        else:
            valor = getattr(valor, parte, '')
    return valor


def _ordenar_itens_insensivel(itens, *campos: str):
    itens_lista = list(itens)
    return sorted(
        itens_lista,
        key=lambda item: (
            *(_texto_ordenacao_insensivel(_resolver_valor_ordenacao(item, campo)) for campo in campos),
            getattr(item, 'pk', None) if not isinstance(item, dict) else item.get('id', ''),
        ),
    )


def _parse_booleano_importacao(valor: str) -> bool | None:
    valor_normalizado = (valor or '').strip().lower()
    if not valor_normalizado:
        return True

    if valor_normalizado in {'true', '1', 'sim', 's', 'ativo'}:
        return True
    if valor_normalizado in {'false', '0', 'nao', 'nÃ£o', 'n', 'inativo'}:
        return False
    return None


def _validar_estrutura_planilha_modelo_xlsx(
    arquivo_importacao,
    colunas_esperadas: list[str],
) -> list[str]:
    nome_arquivo = (arquivo_importacao.name or '').lower()
    if not nome_arquivo.endswith('.xlsx'):
        return ['Envie um arquivo XLSX com extensao .xlsx.']

    try:
        with ZipFile(arquivo_importacao) as arquivo_xlsx:
            namespace = {
                'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                'rel': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
                'pkg': 'http://schemas.openxmlformats.org/package/2006/relationships',
            }

            workbook_tree = ElementTree.fromstring(arquivo_xlsx.read('xl/workbook.xml'))
            relacoes_tree = ElementTree.fromstring(arquivo_xlsx.read('xl/_rels/workbook.xml.rels'))
            shared_strings = _xlsx_ler_strings_compartilhadas(arquivo_xlsx)

            relacoes_planilhas = {
                relacao.get('Id'): _xlsx_normalizar_target_relacao(relacao.get('Target', ''))
                for relacao in relacoes_tree.findall('pkg:Relationship', namespace)
            }
            planilhas = {
                planilha.get('name', ''): relacoes_planilhas.get(
                    planilha.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'),
                    '',
                )
                for planilha in workbook_tree.findall('main:sheets/main:sheet', namespace)
            }
            if 'Instrucoes' in planilhas and 'InstruÃ§Ãµes' not in planilhas:
                planilhas['InstruÃ§Ãµes'] = planilhas['Instrucoes']

            abas_obrigatorias = ['Modelo', 'InstruÃ§Ãµes']
            abas_faltantes = [nome_aba for nome_aba in abas_obrigatorias if nome_aba not in planilhas]
            if abas_faltantes:
                return [
                    'A planilha enviada precisa conter as abas '
                    f'{", ".join(abas_obrigatorias)}. '
                    f'Abas ausentes: {", ".join(abas_faltantes)}.'
                ]

            caminho_modelo = planilhas.get('Modelo', '')
            if not caminho_modelo or caminho_modelo not in arquivo_xlsx.namelist():
                return ['Nao foi possivel localizar a aba Modelo dentro do arquivo XLSX.']

            modelo_tree = ElementTree.fromstring(arquivo_xlsx.read(caminho_modelo))
            primeira_linha = modelo_tree.find('main:sheetData/main:row', namespace)
            cabecalhos = []

            if primeira_linha is not None:
                cabecalhos = [
                    _xlsx_ler_valor_celula(celula, shared_strings, namespace)
                    for celula in primeira_linha.findall('main:c', namespace)
                ]

            if cabecalhos != colunas_esperadas:
                return [
                    'Os cabecalhos da aba Modelo estao diferentes do layout esperado. '
                    'Mantenha exatamente esta ordem e nomenclatura: '
                    f'{", ".join(colunas_esperadas)}.'
                ]
    except (BadZipFile, KeyError, ParseError, OSError):
        return ['Nao foi possivel ler o arquivo enviado como uma planilha XLSX valida.']
    finally:
        arquivo_importacao.seek(0)

    return []


def _obter_cabecalhos_planilha_modelo_xlsx(arquivo_importacao) -> tuple[list[str], list[str]]:
    nome_arquivo = (arquivo_importacao.name or '').lower()
    if not nome_arquivo.endswith('.xlsx'):
        return [], ['Envie um arquivo XLSX com extensao .xlsx.']

    try:
        with ZipFile(arquivo_importacao) as arquivo_xlsx:
            namespace = {
                'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                'rel': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
                'pkg': 'http://schemas.openxmlformats.org/package/2006/relationships',
            }

            workbook_tree = ElementTree.fromstring(arquivo_xlsx.read('xl/workbook.xml'))
            relacoes_tree = ElementTree.fromstring(arquivo_xlsx.read('xl/_rels/workbook.xml.rels'))
            shared_strings = _xlsx_ler_strings_compartilhadas(arquivo_xlsx)

            relacoes_planilhas = {
                relacao.get('Id'): _xlsx_normalizar_target_relacao(relacao.get('Target', ''))
                for relacao in relacoes_tree.findall('pkg:Relationship', namespace)
            }
            planilhas = {
                planilha.get('name', ''): relacoes_planilhas.get(
                    planilha.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'),
                    '',
                )
                for planilha in workbook_tree.findall('main:sheets/main:sheet', namespace)
            }
            if 'Instrucoes' in planilhas and 'InstruÃ§Ãµes' not in planilhas:
                planilhas['InstruÃ§Ãµes'] = planilhas['Instrucoes']

            abas_faltantes = [
                nome_aba
                for nome_aba in LANCAMENTO_IMPORTACAO_ABAS_OBRIGATORIAS
                if nome_aba not in planilhas
            ]
            if abas_faltantes:
                return [], [
                    'A planilha enviada precisa conter as abas '
                    f'{", ".join(LANCAMENTO_IMPORTACAO_ABAS_OBRIGATORIAS)}. '
                    f'Abas ausentes: {", ".join(abas_faltantes)}.'
                ]

            caminho_modelo = planilhas.get('Modelo', '')
            if not caminho_modelo or caminho_modelo not in arquivo_xlsx.namelist():
                return [], ['Nao foi possivel localizar a aba Modelo dentro do arquivo XLSX.']

            modelo_tree = ElementTree.fromstring(arquivo_xlsx.read(caminho_modelo))
            primeira_linha = modelo_tree.find('main:sheetData/main:row', namespace)
            if primeira_linha is None:
                return [], ['Nao foi possivel localizar os cabecalhos da aba Modelo.']

            cabecalhos = [
                _xlsx_ler_valor_celula(celula, shared_strings, namespace)
                for celula in primeira_linha.findall('main:c', namespace)
            ]
            return cabecalhos, []
    except (BadZipFile, KeyError, ParseError, OSError):
        return [], ['Nao foi possivel ler o arquivo enviado como uma planilha XLSX valida.']
    finally:
        arquivo_importacao.seek(0)


def _xlsx_ler_dados_modelo_importacao_xlsx(
    arquivo_importacao,
    colunas_esperadas: list[str],
) -> list[tuple[int, list[str]]]:
    try:
        with ZipFile(arquivo_importacao) as arquivo_xlsx:
            namespace = {
                'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                'rel': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
                'pkg': 'http://schemas.openxmlformats.org/package/2006/relationships',
            }
            workbook_tree = ElementTree.fromstring(arquivo_xlsx.read('xl/workbook.xml'))
            relacoes_tree = ElementTree.fromstring(arquivo_xlsx.read('xl/_rels/workbook.xml.rels'))
            shared_strings = _xlsx_ler_strings_compartilhadas(arquivo_xlsx)

            relacoes_planilhas = {
                relacao.get('Id'): _xlsx_normalizar_target_relacao(relacao.get('Target', ''))
                for relacao in relacoes_tree.findall('pkg:Relationship', namespace)
            }
            caminho_modelo = ''
            for planilha in workbook_tree.findall('main:sheets/main:sheet', namespace):
                if planilha.get('name', '') == 'Modelo':
                    caminho_modelo = relacoes_planilhas.get(
                        planilha.get(
                            '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
                        ),
                        '',
                    )
                    break

            if not caminho_modelo or caminho_modelo not in arquivo_xlsx.namelist():
                return []

            return _xlsx_ler_linhas_planilha(
                arquivo_xlsx,
                caminho_modelo,
                shared_strings,
                namespace,
                len(colunas_esperadas),
            )
    except (BadZipFile, KeyError, ParseError, OSError):
        return []
    finally:
        arquivo_importacao.seek(0)


def _validar_estrutura_planilha_importacao_lancamentos_xlsx(arquivo_importacao) -> list[str]:
    cabecalhos, erros = _obter_cabecalhos_planilha_modelo_xlsx(arquivo_importacao)
    if erros:
        return erros

    if cabecalhos == LANCAMENTO_IMPORTACAO_MODELO_COLUNAS:
        return []

    if cabecalhos == LANCAMENTO_IMPORTACAO_MODELO_COLUNAS_LEGADO:
        return []

    return [
        'Os cabecalhos da aba Modelo estao diferentes do layout esperado. '
        'Use o layout comum atual de 1 linha por documento, com ate 5 blocos de rateio, '
        'ou, para compatibilidade, o layout simples legado. '
        'Layout atual: '
        f'{", ".join(LANCAMENTO_IMPORTACAO_MODELO_COLUNAS)}.'
    ]


def _xlsx_ler_dados_modelo_importacao_lancamentos_xlsx(
    arquivo_importacao,
) -> tuple[list[str], list[tuple[int, list[str]]]]:
    cabecalhos, erros = _obter_cabecalhos_planilha_modelo_xlsx(arquivo_importacao)
    if erros or not cabecalhos:
        return [], []

    return cabecalhos, _xlsx_ler_dados_modelo_importacao_xlsx(
        arquivo_importacao,
        cabecalhos,
    )


def _montar_indice_importacao_por_nome(queryset):
    indice = {}
    for item in queryset:
        chave = _normalizar_nome_importacao_lancamento(item.nome)
        if chave and chave not in indice:
            indice[chave] = item
    return indice


def _montar_indice_categoria_importacao_por_tipo():
    indice = {}
    for categoria in CategoriaFinanceira.objects.filter(
        categoria_pai__isnull=False,
        ativo=True,
    ).order_by('pk'):
        chave = (categoria.tipo, _normalizar_nome_importacao_lancamento(categoria.nome))
        if chave[1] and chave not in indice:
            indice[chave] = categoria
    return indice


def _adicionar_erro_importacao(erros_por_campo: dict[str, list[str]], campo: str, mensagem: str) -> None:
    mensagens = erros_por_campo.setdefault(campo, [])
    if mensagem not in mensagens:
        mensagens.append(mensagem)


def _rotulo_campo_importacao_lancamento(campo: str) -> str:
    return LANCAMENTO_IMPORTACAO_MODELO_ROTULOS.get(campo, campo)


def _orientacao_campo_importacao_lancamento(campo: str, mensagem: str) -> str:
    if campo == 'conta_destino_nome' and 'iguais' in mensagem.lower():
        return 'Escolha uma conta de destino diferente da conta de origem.'

    return LANCAMENTO_IMPORTACAO_ORIENTACOES.get(campo, '')


def _validar_linha_importacao_lancamento(
    dados_linha: dict[str, str],
    pessoas_por_nome: dict[str, PessoaFinanceira],
    categorias_por_tipo_nome: dict[tuple[str, str], CategoriaFinanceira],
    centros_custo_por_nome: dict[str, CentroCusto],
    contas_por_nome: dict[str, ContaFinanceira],
) -> tuple[LancamentoFinanceiro | None, dict[str, list[str]]]:
    erros_por_campo: dict[str, list[str]] = {}

    tipo = (dados_linha.get('tipo') or '').strip()
    status = (dados_linha.get('status') or '').strip()
    descricao = (dados_linha.get('descricao') or '').strip()
    valor_texto = (dados_linha.get('valor') or '').strip()
    data_competencia_texto = (dados_linha.get('data_competencia') or '').strip()
    data_pagamento_texto = (dados_linha.get('data_pagamento') or '').strip()
    pessoa_nome = (dados_linha.get('pessoa_nome') or '').strip()
    categoria_nome = (dados_linha.get('categoria_nome') or '').strip()
    centro_custo_nome = (dados_linha.get('centro_custo_nome') or '').strip()
    conta_nome = (dados_linha.get('conta_nome') or '').strip()
    conta_destino_nome = (dados_linha.get('conta_destino_nome') or '').strip()
    numero_documento = (dados_linha.get('numero_documento') or '').strip()
    observacoes = (dados_linha.get('observacoes') or '').strip()

    tipos_validos = {escolha for escolha, _ in LancamentoFinanceiro.TipoLancamento.choices}
    status_validos = {escolha for escolha, _ in LancamentoFinanceiro.StatusLancamento.choices}

    if not tipo:
        _adicionar_erro_importacao(erros_por_campo, 'tipo', 'Informe o tipo do lanÃ§amento.')
    elif tipo not in tipos_validos:
        _adicionar_erro_importacao(
            erros_por_campo,
            'tipo',
            'Use um tipo vÃ¡lido: receita, despesa ou transferencia.',
        )

    if not status:
        _adicionar_erro_importacao(erros_por_campo, 'status', 'Informe o status do lanÃ§amento.')
    elif status not in status_validos:
        _adicionar_erro_importacao(
            erros_por_campo,
            'status',
            'Use um status vÃ¡lido: aberto, quitado ou cancelado.',
        )

    if not descricao:
        _adicionar_erro_importacao(erros_por_campo, 'descricao', 'Informe a descriÃ§Ã£o.')

    valor = _parse_decimal_importacao_lancamento(valor_texto)
    if not valor_texto:
        _adicionar_erro_importacao(erros_por_campo, 'valor', 'Informe o valor.')
    elif valor is None:
        _adicionar_erro_importacao(erros_por_campo, 'valor', 'Informe um valor numÃ©rico vÃ¡lido.')
    elif valor <= 0:
        _adicionar_erro_importacao(erros_por_campo, 'valor', 'Informe um valor maior que zero.')

    data_competencia = _parse_data_importacao_lancamento(data_competencia_texto)
    if not data_competencia_texto:
        _adicionar_erro_importacao(
            erros_por_campo,
            'data_competencia',
            'Informe a data de competÃªncia.',
        )
    elif data_competencia is None:
        _adicionar_erro_importacao(
            erros_por_campo,
            'data_competencia',
            'Use uma data de competÃªncia vÃ¡lida no formato dd/mm/aaaa.',
        )

    data_pagamento = _parse_data_importacao_lancamento(data_pagamento_texto)
    if not data_pagamento_texto:
        _adicionar_erro_importacao(
            erros_por_campo,
            'data_pagamento',
            'Informe a data de pagamento.',
        )
    elif data_pagamento is None:
        _adicionar_erro_importacao(
            erros_por_campo,
            'data_pagamento',
            'Use uma data de pagamento vÃ¡lida no formato dd/mm/aaaa.',
        )

    pessoa = None
    if pessoa_nome:
        pessoa = pessoas_por_nome.get(_normalizar_nome_importacao_lancamento(pessoa_nome))
        if pessoa is None:
            _adicionar_erro_importacao(
                erros_por_campo,
                'pessoa_nome',
                'Favorecido nao encontrado no cadastro.',
            )

    categoria = None
    if categoria_nome and tipo in tipos_validos:
        categoria = categorias_por_tipo_nome.get(
            (tipo, _normalizar_nome_importacao_lancamento(categoria_nome))
        )
        if categoria is None:
            _adicionar_erro_importacao(
                erros_por_campo,
                'categoria_nome',
                'Subcategoria nÃ£o encontrada para o tipo informado.',
            )

    centro_custo = None
    if centro_custo_nome:
        centro_custo = centros_custo_por_nome.get(
            _normalizar_nome_importacao_lancamento(centro_custo_nome)
        )
        if centro_custo is None:
            _adicionar_erro_importacao(
                erros_por_campo,
                'centro_custo_nome',
                'Centro de custo nÃ£o encontrado no cadastro.',
            )

    conta = None
    if conta_nome:
        conta = contas_por_nome.get(_normalizar_nome_importacao_lancamento(conta_nome))
        if conta is None:
            _adicionar_erro_importacao(
                erros_por_campo,
                'conta_nome',
                'Conta nÃ£o encontrada no cadastro.',
            )
    else:
        _adicionar_erro_importacao(erros_por_campo, 'conta_nome', 'Informe a conta.')

    conta_destino = None
    if conta_destino_nome:
        conta_destino = contas_por_nome.get(
            _normalizar_nome_importacao_lancamento(conta_destino_nome)
        )
        if conta_destino is None:
            _adicionar_erro_importacao(
                erros_por_campo,
                'conta_destino_nome',
                'Conta de destino nÃ£o encontrada no cadastro.',
            )

    lancamento = LancamentoFinanceiro(
        descricao=descricao,
        tipo=tipo,
        status=status,
        valor=valor or Decimal('0.00'),
        data_competencia=data_competencia,
        data_pagamento=data_pagamento,
        pessoa=pessoa,
        categoria=categoria,
        centro_custo=centro_custo,
        conta=conta,
        conta_destino=conta_destino,
        numero_documento=numero_documento,
        observacoes=observacoes,
    )

    try:
        lancamento.full_clean()
    except ValidationError as error:
        for campo, mensagens in error.message_dict.items():
            campo_planilha = LANCAMENTO_IMPORTACAO_CAMPOS_MODELO.get(campo, campo)
            if campo_planilha in erros_por_campo:
                continue
            for mensagem in mensagens:
                _adicionar_erro_importacao(erros_por_campo, campo_planilha, mensagem)

    return (None if erros_por_campo else lancamento), erros_por_campo


def _normalizar_dados_linha_importacao_lancamento(
    dados_linha: dict[str, str],
    cabecalhos_planilha: list[str],
) -> dict[str, str]:
    dados_normalizados = {coluna: '' for coluna in LANCAMENTO_IMPORTACAO_MODELO_COLUNAS}
    for coluna in cabecalhos_planilha:
        if coluna in dados_normalizados:
            dados_normalizados[coluna] = str(dados_linha.get(coluna, '') or '').strip()

    if cabecalhos_planilha == LANCAMENTO_IMPORTACAO_MODELO_COLUNAS_LEGADO:
        dados_normalizados['valor_total_documento'] = str(dados_linha.get('valor', '') or '').strip()
        tipo = str(dados_linha.get('tipo', '') or '').strip()
        if tipo != LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
            dados_normalizados['categoria_nome_1'] = str(
                dados_linha.get('categoria_nome', '') or ''
            ).strip()
            dados_normalizados['centro_custo_nome_1'] = str(
                dados_linha.get('centro_custo_nome', '') or ''
            ).strip()
            dados_normalizados['valor_1'] = str(dados_linha.get('valor', '') or '').strip()

    return dados_normalizados


def _registrar_erros_importacao_lancamento(
    resultado: dict[str, object],
    *,
    linha: int,
    erros_linha: dict[str, list[str]],
    dados_linha: dict[str, str],
) -> None:
    resultado['linhas_invalidas'] += 1
    resultado['erros'].append({
        'linha': linha,
        'campos': [
            {
                'campo': campo,
                'rotulo': _rotulo_campo_importacao_lancamento(campo),
                'mensagem': mensagem,
                'orientacao': _orientacao_campo_importacao_lancamento(campo, mensagem),
                'valor_informado': (dados_linha.get(campo) or '').strip(),
            }
            for campo, mensagens in erros_linha.items()
            for mensagem in mensagens
        ],
    })


def _campos_bloco_rateio_importacao(indice: int) -> tuple[str, str, str]:
    return (
        f'categoria_nome_{indice}',
        f'centro_custo_nome_{indice}',
        f'valor_{indice}',
    )


def _extrair_blocos_rateio_importacao(
    dados_linha: dict[str, str],
) -> tuple[list[dict[str, str]], list[tuple[int, tuple[str, str, str]]]]:
    blocos: list[dict[str, str]] = []
    buracos: list[tuple[int, tuple[str, str, str]]] = []
    encontrou_bloco_vazio = False

    for indice in range(1, LANCAMENTO_IMPORTACAO_MODELO_MAX_RATEIOS + 1):
        campo_categoria, campo_centro_custo, campo_valor = _campos_bloco_rateio_importacao(indice)
        categoria_nome = (dados_linha.get(campo_categoria) or '').strip()
        centro_custo_nome = (dados_linha.get(campo_centro_custo) or '').strip()
        valor = (dados_linha.get(campo_valor) or '').strip()

        if not categoria_nome and not centro_custo_nome and not valor:
            encontrou_bloco_vazio = True
            continue

        if encontrou_bloco_vazio:
            buracos.append((indice, (campo_categoria, campo_centro_custo, campo_valor)))

        blocos.append(
            {
                'indice': indice,
                'categoria_nome': categoria_nome,
                'centro_custo_nome': centro_custo_nome,
                'valor': valor,
            }
        )

    return blocos, buracos


def _montar_dados_bloco_importacao_lancamento(
    dados_linha: dict[str, str],
    bloco: dict[str, str],
) -> dict[str, str]:
    return {
        'tipo': (dados_linha.get('tipo') or '').strip(),
        'status': (dados_linha.get('status') or '').strip(),
        'descricao': (dados_linha.get('descricao') or '').strip(),
        'valor': (bloco.get('valor') or '').strip(),
        'data_competencia': (dados_linha.get('data_competencia') or '').strip(),
        'data_pagamento': (dados_linha.get('data_pagamento') or '').strip(),
        'pessoa_nome': (dados_linha.get('pessoa_nome') or '').strip(),
        'categoria_nome': (bloco.get('categoria_nome') or '').strip(),
        'centro_custo_nome': (bloco.get('centro_custo_nome') or '').strip(),
        'conta_nome': (dados_linha.get('conta_nome') or '').strip(),
        'conta_destino_nome': (dados_linha.get('conta_destino_nome') or '').strip(),
        'numero_documento': (dados_linha.get('numero_documento') or '').strip(),
        'observacoes': (dados_linha.get('observacoes') or '').strip(),
    }


def _construir_lancamentos_rateados_para_importacao(
    lancamentos_base: list[LancamentoFinanceiro],
    numero_documento: str,
) -> list[LancamentoFinanceiro]:
    token_grupo = uuid4().hex
    lancamentos_grupo: list[LancamentoFinanceiro] = []

    for base in lancamentos_base:
        lancamento = LancamentoFinanceiro(
            descricao=base.descricao,
            tipo=base.tipo,
            status=base.status,
            valor=base.valor,
            data_competencia=base.data_competencia,
            data_pagamento=base.data_pagamento,
            pessoa=base.pessoa,
            categoria=base.categoria,
            centro_custo=base.centro_custo,
            conta=base.conta,
            conta_destino=base.conta_destino,
            numero_documento=numero_documento,
            observacoes=base.observacoes,
            com_rateio=True,
            grupo_rateio=token_grupo,
        )
        if not lancamento.numero_documento:
            lancamento.numero_documento = lancamento._gerar_numero_documento()
            numero_documento = lancamento.numero_documento
        lancamentos_grupo.append(lancamento)

    for lancamento in lancamentos_grupo:
        lancamento.numero_documento = numero_documento

    return lancamentos_grupo


def _validar_grupo_rateio_importacao_lancamentos(
    *,
    linha: int,
    dados_linha: dict[str, str],
    blocos_rateio: list[dict[str, str]],
    valor_total_documento: Decimal,
    lancamentos_validos: list[LancamentoFinanceiro],
    resultado: dict[str, object],
    documentos_planilha: dict[str, int],
) -> list[LancamentoFinanceiro]:
    erros_linha: dict[str, list[str]] = {}

    if len(blocos_rateio) < 2:
        _adicionar_erro_importacao(
            erros_linha,
            'categoria_nome_2',
            'Lancamentos com rateio precisam usar pelo menos 2 blocos preenchidos.',
        )

    if lancamentos_validos and lancamentos_validos[0].tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
        _adicionar_erro_importacao(
            erros_linha,
            'tipo',
            'Lancamentos do tipo transferencia nao aceitam rateio no fluxo comum.',
        )

    soma_blocos = sum((lancamento.valor for lancamento in lancamentos_validos), Decimal('0.00'))
    if soma_blocos != valor_total_documento:
        _adicionar_erro_importacao(
            erros_linha,
            'valor_total_documento',
            'A soma dos blocos preenchidos precisa ser igual ao valor total do documento.',
        )

    numero_documento = (dados_linha.get('numero_documento') or '').strip()
    if numero_documento:
        dono_documento = documentos_planilha.get(numero_documento)
        if dono_documento and dono_documento != linha:
            _adicionar_erro_importacao(
                erros_linha,
                'numero_documento',
                f'Documento repetido na linha {dono_documento} desta planilha.',
            )
        else:
            documentos_planilha[numero_documento] = linha

    if erros_linha:
        _registrar_erros_importacao_lancamento(
            resultado,
            linha=linha,
            erros_linha=erros_linha,
            dados_linha=dados_linha,
        )
        return []

    return _construir_lancamentos_rateados_para_importacao(lancamentos_validos, numero_documento)


def _validar_conteudo_planilha_importacao_lancamentos_xlsx(arquivo_importacao) -> dict[str, object]:
    resultado = {
        'linhas_lidas': 0,
        'linhas_validas': 0,
        'linhas_importadas': 0,
        'linhas_invalidas': 0,
        'erros': [],
        'operacoes_validas': [],
    }

    cabecalhos_planilha, linhas_planilha = _xlsx_ler_dados_modelo_importacao_lancamentos_xlsx(
        arquivo_importacao
    )
    linhas_dados = linhas_planilha[1:] if linhas_planilha else []

    pessoas_por_nome = _montar_indice_importacao_por_nome(
        PessoaFinanceira.objects.filter(ativo=True).order_by('pk')
    )
    centros_custo_por_nome = _montar_indice_importacao_por_nome(
        CentroCusto.objects.filter(ativo=True).order_by('pk')
    )
    contas_por_nome = _montar_indice_importacao_por_nome(
        ContaFinanceira.objects.filter(ativa=True).order_by('pk')
    )
    categorias_por_tipo_nome = _montar_indice_categoria_importacao_por_tipo()
    documentos_importacao: dict[str, int] = {}

    for numero_linha, valores_linha in linhas_dados:
        dados_linha = _normalizar_dados_linha_importacao_lancamento(
            dict(zip(cabecalhos_planilha, valores_linha)),
            cabecalhos_planilha,
        )
        if not any((valor or '').strip() for valor in dados_linha.values()):
            continue

        resultado['linhas_lidas'] += 1
        erros_linha: dict[str, list[str]] = {}
        blocos_rateio, buracos_rateio = _extrair_blocos_rateio_importacao(dados_linha)
        valor_total_texto = (dados_linha.get('valor_total_documento') or '').strip()
        valor_total_documento = _parse_decimal_importacao_lancamento(valor_total_texto)
        tipo = (dados_linha.get('tipo') or '').strip()

        if not valor_total_texto:
            _adicionar_erro_importacao(
                erros_linha,
                'valor_total_documento',
                'Informe o valor total do documento.',
            )
        elif valor_total_documento is None:
            _adicionar_erro_importacao(
                erros_linha,
                'valor_total_documento',
                'Informe um valor total do documento valido.',
            )
        elif valor_total_documento <= 0:
            _adicionar_erro_importacao(
                erros_linha,
                'valor_total_documento',
                'Informe um valor total do documento maior que zero.',
            )

        for indice_bloco, campos_bloco in buracos_rateio:
            campo_categoria, campo_centro_custo, campo_valor = campos_bloco
            mensagem = (
                'Nao deixe buracos entre os blocos de rateio. '
                'Preencha os blocos em sequencia, sem pular posicoes.'
            )
            _adicionar_erro_importacao(erros_linha, campo_categoria, mensagem)
            _adicionar_erro_importacao(erros_linha, campo_centro_custo, mensagem)
            _adicionar_erro_importacao(erros_linha, campo_valor, mensagem)

        if tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA and blocos_rateio:
            _adicionar_erro_importacao(
                erros_linha,
                'tipo',
                'Lancamentos do tipo transferencia devem deixar todos os blocos de rateio em branco.',
            )

        if tipo != LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA and not blocos_rateio:
            _adicionar_erro_importacao(
                erros_linha,
                'categoria_nome_1',
                'Preencha pelo menos o bloco 1 para receita ou despesa.',
            )
            _adicionar_erro_importacao(
                erros_linha,
                'valor_1',
                'Preencha pelo menos o valor do bloco 1 para receita ou despesa.',
            )

        lancamentos_validos: list[LancamentoFinanceiro] = []
        for bloco in blocos_rateio:
            dados_bloco = _montar_dados_bloco_importacao_lancamento(dados_linha, bloco)
            lancamento_validado, erros_bloco = _validar_linha_importacao_lancamento(
                dados_bloco,
                pessoas_por_nome,
                categorias_por_tipo_nome,
                centros_custo_por_nome,
                contas_por_nome,
            )
            for campo, mensagens in erros_bloco.items():
                campo_destino = campo
                if campo == 'categoria_nome':
                    campo_destino = f'categoria_nome_{bloco["indice"]}'
                elif campo == 'centro_custo_nome':
                    campo_destino = f'centro_custo_nome_{bloco["indice"]}'
                elif campo == 'valor':
                    campo_destino = f'valor_{bloco["indice"]}'
                for mensagem in mensagens:
                    _adicionar_erro_importacao(erros_linha, campo_destino, mensagem)
            if lancamento_validado is not None:
                lancamentos_validos.append(lancamento_validado)

        if tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
            dados_transferencia = {
                'tipo': (dados_linha.get('tipo') or '').strip(),
                'status': (dados_linha.get('status') or '').strip(),
                'descricao': (dados_linha.get('descricao') or '').strip(),
                'valor': valor_total_texto,
                'data_competencia': (dados_linha.get('data_competencia') or '').strip(),
                'data_pagamento': (dados_linha.get('data_pagamento') or '').strip(),
                'pessoa_nome': (dados_linha.get('pessoa_nome') or '').strip(),
                'categoria_nome': '',
                'centro_custo_nome': '',
                'conta_nome': (dados_linha.get('conta_nome') or '').strip(),
                'conta_destino_nome': (dados_linha.get('conta_destino_nome') or '').strip(),
                'numero_documento': (dados_linha.get('numero_documento') or '').strip(),
                'observacoes': (dados_linha.get('observacoes') or '').strip(),
            }
            lancamento_transferencia, erros_transferencia = _validar_linha_importacao_lancamento(
                dados_transferencia,
                pessoas_por_nome,
                categorias_por_tipo_nome,
                centros_custo_por_nome,
                contas_por_nome,
            )
            for campo, mensagens in erros_transferencia.items():
                for mensagem in mensagens:
                    _adicionar_erro_importacao(erros_linha, campo, mensagem)
            if lancamento_transferencia is not None:
                lancamentos_validos = [lancamento_transferencia]

        if (
            tipo != LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA
            and len(lancamentos_validos) == 1
            and valor_total_documento is not None
            and lancamentos_validos[0].valor != valor_total_documento
        ):
            _adicionar_erro_importacao(
                erros_linha,
                'valor_total_documento',
                'O valor total do documento precisa ser igual ao valor do bloco 1 no lancamento simples.',
            )

        if erros_linha:
            _registrar_erros_importacao_lancamento(
                resultado,
                linha=numero_linha,
                erros_linha=erros_linha,
                dados_linha=dados_linha,
            )
            continue

        numero_documento = (dados_linha.get('numero_documento') or '').strip()
        if tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
            if numero_documento:
                dono_documento = documentos_importacao.get(numero_documento)
                if dono_documento:
                    _registrar_erros_importacao_lancamento(
                        resultado,
                        linha=numero_linha,
                        erros_linha={
                            'numero_documento': [
                                f'Documento repetido na linha {dono_documento} desta planilha.'
                            ]
                        },
                        dados_linha=dados_linha,
                    )
                    continue
                documentos_importacao[numero_documento] = numero_linha

            resultado['linhas_validas'] += 1
            resultado['operacoes_validas'].append({
                'tipo': 'transferencia',
                'linha': numero_linha,
                'lancamentos': lancamentos_validos,
            })
            continue

        if len(lancamentos_validos) == 1:
            if numero_documento:
                dono_documento = documentos_importacao.get(numero_documento)
                if dono_documento:
                    _registrar_erros_importacao_lancamento(
                        resultado,
                        linha=numero_linha,
                        erros_linha={
                            'numero_documento': [
                                f'Documento repetido na linha {dono_documento} desta planilha.'
                            ]
                        },
                        dados_linha=dados_linha,
                    )
                    continue
                documentos_importacao[numero_documento] = numero_linha

            resultado['linhas_validas'] += 1
            resultado['operacoes_validas'].append({
                'tipo': 'simples',
                'linha': numero_linha,
                'lancamentos': lancamentos_validos,
            })
            continue

        lancamentos_grupo = _validar_grupo_rateio_importacao_lancamentos(
            linha=numero_linha,
            dados_linha=dados_linha,
            blocos_rateio=blocos_rateio,
            valor_total_documento=valor_total_documento or Decimal('0.00'),
            lancamentos_validos=lancamentos_validos,
            resultado=resultado,
            documentos_planilha=documentos_importacao,
        )
        if lancamentos_grupo:
            resultado['linhas_validas'] += 1
            resultado['operacoes_validas'].append({
                'tipo': 'rateio',
                'linha': numero_linha,
                'lancamentos': lancamentos_grupo,
            })

    return resultado


def _serializar_erros_importacao_lancamentos(erros: list[dict[str, object]]) -> str:
    return json.dumps(erros, ensure_ascii=False)


def _normalizar_erros_importacao_lancamentos_relatorio(valor_serializado: str) -> list[dict[str, object]]:
    try:
        erros = json.loads(valor_serializado or '[]')
    except json.JSONDecodeError:
        return []

    if not isinstance(erros, list):
        return []

    erros_normalizados = []
    for erro_linha in erros:
        if not isinstance(erro_linha, dict):
            continue

        try:
            linha = int(erro_linha.get('linha'))
        except (TypeError, ValueError):
            continue

        campos_normalizados = []
        campos = erro_linha.get('campos')
        if not isinstance(campos, list):
            campos = []

        for erro_campo in campos:
            if not isinstance(erro_campo, dict):
                continue

            campos_normalizados.append({
                'campo': str(erro_campo.get('campo') or '').strip(),
                'rotulo': str(erro_campo.get('rotulo') or '').strip(),
                'mensagem': str(erro_campo.get('mensagem') or '').strip(),
                'orientacao': str(erro_campo.get('orientacao') or '').strip(),
                'valor_informado': str(erro_campo.get('valor_informado') or '').strip(),
            })

        if campos_normalizados:
            erros_normalizados.append({
                'linha': linha,
                'campos': campos_normalizados,
            })

    return erros_normalizados


def _gerar_relatorio_inconsistencias_importacao_lancamentos_xlsx(
    erros: list[dict[str, object]],
) -> bytes:
    linhas = [['Linha', 'Campo', 'Mensagem', 'Como corrigir', 'Valor informado']]

    for erro_linha in erros:
        for erro_campo in erro_linha.get('campos', []):
            linhas.append([
                erro_linha.get('linha', ''),
                erro_campo.get('rotulo', ''),
                erro_campo.get('mensagem', ''),
                erro_campo.get('orientacao', ''),
                erro_campo.get('valor_informado', ''),
            ])

    return _gerar_arquivo_xlsx([('InconsistÃªncias', linhas)])


def _resultado_importacao_auxiliar_vazio(slug: str) -> dict[str, object]:
    return {
        'linhas_lidas': 0,
        'linhas_validas': 0,
        'linhas_importadas': 0,
        'linhas_invalidas': 0,
        'erros': [],
        'registros_validos': [],
        'slug': slug,
        'titulo': CADASTRO_AUXILIAR_PLANILHAS_BASE[slug]['titulo'],
    }


def _rotulo_campo_importacao_auxiliar(slug: str, campo: str) -> str:
    return CADASTRO_AUXILIAR_PLANILHAS_BASE[slug]['rotulos'].get(campo, campo)


def _orientacao_campo_importacao_auxiliar(slug: str, campo: str) -> str:
    return CADASTRO_AUXILIAR_PLANILHAS_BASE[slug]['orientacoes'].get(campo, '')


def _registrar_erro_resultado_importacao_auxiliar(
    resultado: dict[str, object],
    *,
    linha: int,
    erros_linha: dict[str, list[str]],
    dados_linha: dict[str, str],
) -> None:
    resultado['linhas_invalidas'] += 1
    resultado['erros'].append({
        'linha': linha,
        'campos': [
            {
                'campo': campo,
                'rotulo': _rotulo_campo_importacao_auxiliar(resultado['slug'], campo),
                'mensagem': mensagem,
                'orientacao': _orientacao_campo_importacao_auxiliar(resultado['slug'], campo),
                'valor_informado': (dados_linha.get(campo) or '').strip(),
            }
            for campo, mensagens in erros_linha.items()
            for mensagem in mensagens
        ],
    })


def _validar_conteudo_planilha_importacao_contas_xlsx(arquivo_importacao) -> dict[str, object]:
    slug = 'contas'
    resultado = _resultado_importacao_auxiliar_vazio(slug)
    colunas = CADASTRO_AUXILIAR_PLANILHAS_BASE[slug]['colunas']
    linhas_planilha = _xlsx_ler_dados_modelo_importacao_xlsx(arquivo_importacao, colunas)
    linhas_dados = linhas_planilha[1:] if linhas_planilha else []

    nomes_existentes = {
        _normalizar_nome_importacao_lancamento(item.nome)
        for item in ContaFinanceira.objects.all().only('nome')
    }
    nomes_arquivo: set[str] = set()

    for linha, valores_linha in linhas_dados:
        dados_linha = dict(zip(colunas, valores_linha))
        if not any((valor or '').strip() for valor in valores_linha):
            continue

        resultado['linhas_lidas'] += 1
        erros_linha: dict[str, list[str]] = {}

        nome = (dados_linha.get('nome') or '').strip()
        descricao = (dados_linha.get('descricao') or '').strip()
        saldo_inicial_texto = (dados_linha.get('saldo_inicial') or '').strip()
        data_saldo_texto = (dados_linha.get('data_saldo_inicial') or '').strip()
        ativa_texto = (dados_linha.get('ativa') or '').strip()

        nome_normalizado = _normalizar_nome_importacao_lancamento(nome)
        saldo_inicial = _parse_decimal_importacao_lancamento(saldo_inicial_texto or '0')
        data_saldo_inicial = _parse_data_importacao_lancamento(data_saldo_texto)
        ativa = _parse_booleano_importacao(ativa_texto)

        if not nome:
            _adicionar_erro_importacao(erros_linha, 'nome', 'Informe o nome da conta.')
        elif nome_normalizado in nomes_existentes:
            _adicionar_erro_importacao(erros_linha, 'nome', 'Ja existe uma conta com este nome no cadastro.')
        elif nome_normalizado in nomes_arquivo:
            _adicionar_erro_importacao(erros_linha, 'nome', 'Este nome de conta esta repetido na planilha.')

        if saldo_inicial is None:
            _adicionar_erro_importacao(erros_linha, 'saldo_inicial', 'Informe um saldo inicial numerico valido.')

        if not data_saldo_texto:
            _adicionar_erro_importacao(erros_linha, 'data_saldo_inicial', 'Informe a data do saldo inicial.')
        elif data_saldo_inicial is None:
            _adicionar_erro_importacao(erros_linha, 'data_saldo_inicial', 'Use uma data valida no formato dd/mm/aaaa.')

        if ativa is None:
            _adicionar_erro_importacao(erros_linha, 'ativa', 'Use true/false, sim/nao, 1/0 ou deixe em branco.')

        if erros_linha:
            _registrar_erro_resultado_importacao_auxiliar(resultado, linha=linha, erros_linha=erros_linha, dados_linha=dados_linha)
            continue

        resultado['linhas_validas'] += 1
        nomes_arquivo.add(nome_normalizado)
        resultado['registros_validos'].append({
            'nome': nome,
            'descricao': descricao,
            'saldo_inicial': saldo_inicial or Decimal('0.00'),
            'data_saldo_inicial': data_saldo_inicial,
            'ativa': ativa,
        })

    return resultado


def _validar_conteudo_planilha_importacao_pessoas_xlsx(arquivo_importacao) -> dict[str, object]:
    slug = 'pessoas'
    resultado = _resultado_importacao_auxiliar_vazio(slug)
    colunas = CADASTRO_AUXILIAR_PLANILHAS_BASE[slug]['colunas']
    linhas_planilha = _xlsx_ler_dados_modelo_importacao_xlsx(arquivo_importacao, colunas)
    linhas_dados = linhas_planilha[1:] if linhas_planilha else []

    codigos_existentes = {
        _normalizar_codigo_importacao(item.codigo)
        for item in PessoaFinanceira.objects.all().only('codigo')
    }
    nomes_existentes = {
        _normalizar_nome_importacao_lancamento(item.nome)
        for item in PessoaFinanceira.objects.all().only('nome')
    }
    codigos_arquivo: set[str] = set()
    nomes_arquivo: set[str] = set()
    tipos_validos = {escolha for escolha, _ in PessoaFinanceira.TipoPessoa.choices}

    for linha, valores_linha in linhas_dados:
        dados_linha = dict(zip(colunas, valores_linha))
        if not any((valor or '').strip() for valor in valores_linha):
            continue

        resultado['linhas_lidas'] += 1
        erros_linha: dict[str, list[str]] = {}

        codigo = (dados_linha.get('codigo') or '').strip()
        nome = (dados_linha.get('nome') or '').strip()
        tipo_pessoa = (dados_linha.get('tipo_pessoa') or '').strip().lower()
        documento = (dados_linha.get('documento') or '').strip()
        telefone = (dados_linha.get('telefone') or '').strip()
        email = (dados_linha.get('email') or '').strip()
        observacoes = (dados_linha.get('observacoes') or '').strip()
        ativo_texto = (dados_linha.get('ativo') or '').strip()

        codigo_normalizado = _normalizar_codigo_importacao(codigo)
        nome_normalizado = _normalizar_nome_importacao_lancamento(nome)
        ativo = _parse_booleano_importacao(ativo_texto)

        if not codigo:
            _adicionar_erro_importacao(erros_linha, 'codigo', 'Informe o codigo do favorecido.')
        elif codigo_normalizado in codigos_existentes:
            _adicionar_erro_importacao(erros_linha, 'codigo', 'Ja existe um favorecido com este codigo no cadastro.')
        elif codigo_normalizado in codigos_arquivo:
            _adicionar_erro_importacao(erros_linha, 'codigo', 'Este codigo de favorecido esta repetido na planilha.')

        if not nome:
            _adicionar_erro_importacao(erros_linha, 'nome', 'Informe o nome do favorecido.')
        elif nome_normalizado in nomes_existentes:
            _adicionar_erro_importacao(erros_linha, 'nome', 'Ja existe um favorecido com este nome no cadastro.')
        elif nome_normalizado in nomes_arquivo:
            _adicionar_erro_importacao(erros_linha, 'nome', 'Este nome de favorecido esta repetido na planilha.')

        if tipo_pessoa and tipo_pessoa not in tipos_validos:
            _adicionar_erro_importacao(erros_linha, 'tipo_pessoa', 'Use fisica ou juridica.')

        if ativo is None:
            _adicionar_erro_importacao(erros_linha, 'ativo', 'Use true/false, sim/nao, 1/0 ou deixe em branco.')

        pessoa = PessoaFinanceira(
            codigo=codigo,
            nome=nome,
            tipo_pessoa=tipo_pessoa,
            documento=documento,
            telefone=telefone,
            email=email,
            observacoes=observacoes,
            ativo=True if ativo is None else ativo,
        )
        try:
            pessoa.full_clean()
        except ValidationError as error:
            for campo, mensagens in error.message_dict.items():
                for mensagem in mensagens:
                    _adicionar_erro_importacao(erros_linha, campo, mensagem)

        if erros_linha:
            _registrar_erro_resultado_importacao_auxiliar(resultado, linha=linha, erros_linha=erros_linha, dados_linha=dados_linha)
            continue

        resultado['linhas_validas'] += 1
        codigos_arquivo.add(codigo_normalizado)
        nomes_arquivo.add(nome_normalizado)
        resultado['registros_validos'].append({
            'codigo': codigo,
            'nome': nome,
            'tipo_pessoa': tipo_pessoa,
            'documento': documento,
            'telefone': telefone,
            'email': email,
            'observacoes': observacoes,
            'ativo': ativo,
        })

    return resultado


def _validar_conteudo_planilha_importacao_centros_custo_xlsx(arquivo_importacao) -> dict[str, object]:
    slug = 'centros-custo'
    resultado = _resultado_importacao_auxiliar_vazio(slug)
    colunas = CADASTRO_AUXILIAR_PLANILHAS_BASE[slug]['colunas']
    linhas_planilha = _xlsx_ler_dados_modelo_importacao_xlsx(arquivo_importacao, colunas)
    linhas_dados = linhas_planilha[1:] if linhas_planilha else []

    codigos_existentes = {
        _normalizar_codigo_importacao(item.codigo)
        for item in CentroCusto.objects.all().only('codigo')
    }
    nomes_existentes = {
        _normalizar_nome_importacao_lancamento(item.nome)
        for item in CentroCusto.objects.all().only('nome')
    }
    codigos_arquivo: set[str] = set()
    nomes_arquivo: set[str] = set()

    for linha, valores_linha in linhas_dados:
        dados_linha = dict(zip(colunas, valores_linha))
        if not any((valor or '').strip() for valor in valores_linha):
            continue

        resultado['linhas_lidas'] += 1
        erros_linha: dict[str, list[str]] = {}

        codigo = (dados_linha.get('codigo') or '').strip()
        nome = (dados_linha.get('nome') or '').strip()
        ativo_texto = (dados_linha.get('ativo') or '').strip()

        codigo_normalizado = _normalizar_codigo_importacao(codigo)
        nome_normalizado = _normalizar_nome_importacao_lancamento(nome)
        ativo = _parse_booleano_importacao(ativo_texto)

        if not codigo:
            _adicionar_erro_importacao(erros_linha, 'codigo', 'Informe o codigo do centro de custo.')
        elif codigo_normalizado in codigos_existentes:
            _adicionar_erro_importacao(erros_linha, 'codigo', 'Ja existe um centro de custo com este codigo no cadastro.')
        elif codigo_normalizado in codigos_arquivo:
            _adicionar_erro_importacao(erros_linha, 'codigo', 'Este codigo de centro de custo esta repetido na planilha.')

        if not nome:
            _adicionar_erro_importacao(erros_linha, 'nome', 'Informe o nome do centro de custo.')
        elif nome_normalizado in nomes_existentes:
            _adicionar_erro_importacao(erros_linha, 'nome', 'Ja existe um centro de custo com este nome no cadastro.')
        elif nome_normalizado in nomes_arquivo:
            _adicionar_erro_importacao(erros_linha, 'nome', 'Este nome de centro de custo esta repetido na planilha.')

        if ativo is None:
            _adicionar_erro_importacao(erros_linha, 'ativo', 'Use true/false, sim/nao, 1/0 ou deixe em branco.')

        centro_custo = CentroCusto(
            codigo=codigo,
            nome=nome,
            ativo=True if ativo is None else ativo,
        )
        try:
            centro_custo.full_clean()
        except ValidationError as error:
            for campo, mensagens in error.message_dict.items():
                for mensagem in mensagens:
                    _adicionar_erro_importacao(erros_linha, campo, mensagem)

        if erros_linha:
            _registrar_erro_resultado_importacao_auxiliar(resultado, linha=linha, erros_linha=erros_linha, dados_linha=dados_linha)
            continue

        resultado['linhas_validas'] += 1
        codigos_arquivo.add(codigo_normalizado)
        nomes_arquivo.add(nome_normalizado)
        resultado['registros_validos'].append({
            'codigo': codigo,
            'nome': nome,
            'ativo': ativo,
        })

    return resultado


def _validar_conteudo_planilha_importacao_categorias_xlsx(arquivo_importacao) -> dict[str, object]:
    slug = 'categorias'
    resultado = _resultado_importacao_auxiliar_vazio(slug)
    colunas = CADASTRO_AUXILIAR_PLANILHAS_BASE[slug]['colunas']
    linhas_planilha = _xlsx_ler_dados_modelo_importacao_xlsx(arquivo_importacao, colunas)
    linhas_dados = linhas_planilha[1:] if linhas_planilha else []

    tipos_validos = {escolha for escolha, _ in CategoriaFinanceira.TipoCategoria.choices}
    categorias_existentes_por_chave = {
        (item.tipo, _normalizar_nome_importacao_lancamento(item.nome)): item
        for item in CategoriaFinanceira.objects.all().only('tipo', 'nome')
    }
    categorias_pai_disponiveis = {
        (item.tipo, _normalizar_nome_importacao_lancamento(item.nome))
        for item in CategoriaFinanceira.objects.filter(categoria_pai__isnull=True).only('tipo', 'nome')
    }
    categorias_arquivo: set[tuple[str, str]] = set()

    for linha, valores_linha in linhas_dados:
        dados_linha = dict(zip(colunas, valores_linha))
        if not any((valor or '').strip() for valor in valores_linha):
            continue

        resultado['linhas_lidas'] += 1
        erros_linha: dict[str, list[str]] = {}

        nome = (dados_linha.get('nome') or '').strip()
        tipo = (dados_linha.get('tipo') or '').strip().lower()
        categoria_pai_nome = (dados_linha.get('categoria_pai_nome') or '').strip()
        mensagem_recibo = (dados_linha.get('mensagem_recibo') or '').strip()
        ativo_texto = (dados_linha.get('ativo') or '').strip()

        nome_normalizado = _normalizar_nome_importacao_lancamento(nome)
        categoria_pai_normalizada = _normalizar_nome_importacao_lancamento(categoria_pai_nome)
        ativo = _parse_booleano_importacao(ativo_texto)
        chave_categoria = (tipo, nome_normalizado)

        if not nome:
            _adicionar_erro_importacao(erros_linha, 'nome', 'Informe o nome da categoria ou subcategoria.')

        if not tipo:
            _adicionar_erro_importacao(erros_linha, 'tipo', 'Informe o tipo da categoria.')
        elif tipo not in tipos_validos:
            _adicionar_erro_importacao(erros_linha, 'tipo', 'Use receita ou despesa.')

        if ativo is None:
            _adicionar_erro_importacao(erros_linha, 'ativo', 'Use true/false, sim/nao, 1/0 ou deixe em branco.')

        if nome and tipo in tipos_validos:
            if chave_categoria in categorias_existentes_por_chave:
                _adicionar_erro_importacao(erros_linha, 'nome', 'Ja existe uma categoria ou subcategoria com este nome para o tipo informado.')
            elif chave_categoria in categorias_arquivo:
                _adicionar_erro_importacao(erros_linha, 'nome', 'Este nome esta repetido na planilha para o tipo informado.')

        if categoria_pai_nome and tipo in tipos_validos:
            chave_pai = (tipo, categoria_pai_normalizada)
            if chave_pai not in categorias_pai_disponiveis:
                _adicionar_erro_importacao(
                    erros_linha,
                    'categoria_pai_nome',
                    'Categoria pai nao encontrada. Liste a categoria pai antes da subcategoria ou use uma categoria pai ja existente.',
                )
            elif chave_pai == chave_categoria:
                _adicionar_erro_importacao(erros_linha, 'categoria_pai_nome', 'A categoria pai precisa ser diferente do proprio nome da linha.')

        if erros_linha:
            _registrar_erro_resultado_importacao_auxiliar(resultado, linha=linha, erros_linha=erros_linha, dados_linha=dados_linha)
            continue

        resultado['linhas_validas'] += 1
        categorias_arquivo.add(chave_categoria)
        if not categoria_pai_nome:
            categorias_pai_disponiveis.add(chave_categoria)
        resultado['registros_validos'].append({
            'nome': nome,
            'tipo': tipo,
            'categoria_pai_nome': categoria_pai_nome,
            'mensagem_recibo': mensagem_recibo,
            'ativo': ativo,
        })

    return resultado


def _importar_contas_validadas(registros: list[dict[str, object]], request) -> int:
    total = 0
    with transaction.atomic():
        for registro in registros:
            conta = ContaFinanceira(**registro)
            conta.full_clean()
            conta.save()
            _registrar_auditoria_conta(request=request, acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE, conta=conta, depois=_snapshot_conta(conta))
            total += 1
    return total


def _importar_pessoas_validadas(registros: list[dict[str, object]], request) -> int:
    total = 0
    with transaction.atomic():
        for registro in registros:
            pessoa = PessoaFinanceira(**registro)
            pessoa.full_clean()
            pessoa.save()
            _registrar_auditoria_pessoa(request=request, acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE, pessoa=pessoa, depois=_snapshot_pessoa(pessoa))
            total += 1
    return total


def _importar_centros_custo_validados(registros: list[dict[str, object]], request) -> int:
    total = 0
    with transaction.atomic():
        for registro in registros:
            centro_custo = CentroCusto(**registro)
            centro_custo.full_clean()
            centro_custo.save()
            _registrar_auditoria_centro_custo(request=request, acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE, centro_custo=centro_custo, depois=_snapshot_centro_custo(centro_custo))
            total += 1
    return total


def _importar_categorias_validadas(registros: list[dict[str, object]], request) -> int:
    total = 0
    categorias_pai_por_chave = {
        (item.tipo, _normalizar_nome_importacao_lancamento(item.nome)): item
        for item in CategoriaFinanceira.objects.filter(categoria_pai__isnull=True)
    }

    with transaction.atomic():
        for registro in registros:
            categoria_pai = None
            categoria_pai_nome = (registro.get('categoria_pai_nome') or '').strip()
            if categoria_pai_nome:
                categoria_pai = categorias_pai_por_chave.get((registro['tipo'], _normalizar_nome_importacao_lancamento(categoria_pai_nome)))

            categoria = CategoriaFinanceira(
                nome=registro['nome'],
                tipo=registro['tipo'],
                categoria_pai=categoria_pai,
                mensagem_recibo=registro['mensagem_recibo'],
                ativo=registro['ativo'],
            )
            categoria.full_clean()
            categoria.save()

            if categoria.categoria_pai_id is None:
                categorias_pai_por_chave[(categoria.tipo, _normalizar_nome_importacao_lancamento(categoria.nome))] = categoria

            _registrar_auditoria_categoria(request=request, acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE, categoria=categoria, depois=_snapshot_categoria(categoria))
            total += 1

    return total


def _usuario_pode_importar_cadastro_auxiliar(usuario, slug: str) -> bool:
    configuracao = CADASTRO_AUXILIAR_PLANILHAS_BASE.get(slug)
    if not configuracao:
        return False
    return usuario_possui_permissao(usuario, configuracao['permissao'])


IMPORTACAO_DOMINIOS_BLOQUEADOS_QUANDO_PREENCHIDOS = {
    'contas': {
        'modelo': ContaFinanceira,
        'mensagem': 'Ja existem registros em Contas. Limpe ou redefina a base antes de nova importacao.',
    },
    'pessoas': {
        'modelo': PessoaFinanceira,
        'mensagem': 'Ja existem registros em Favorecidos. Limpe ou redefina a base antes de nova importacao.',
    },
    'centros-custo': {
        'modelo': CentroCusto,
        'mensagem': 'Ja existem registros em Centros de custo. Importe apenas em base vazia desse dominio.',
    },
    'categorias': {
        'modelo': CategoriaFinanceira,
        'mensagem': 'Ja existem registros em Categorias/Subcategorias. Importe apenas em base vazia desse dominio.',
    },
    'lancamentos': {
        'modelo': LancamentoFinanceiro,
        'mensagem': 'Ja existem registros em Lancamentos. Limpe ou redefina a base antes de nova importacao.',
    },
}


def _dominio_importacao_ja_possui_registros(slug: str) -> bool:
    configuracao = IMPORTACAO_DOMINIOS_BLOQUEADOS_QUANDO_PREENCHIDOS.get(slug)
    if not configuracao:
        return False
    return configuracao['modelo'].objects.exists()


def _mensagem_bloqueio_importacao_dominio(slug: str) -> str:
    configuracao = IMPORTACAO_DOMINIOS_BLOQUEADOS_QUANDO_PREENCHIDOS.get(slug)
    if not configuracao:
        return 'Ja existem registros neste dominio. Limpe ou redefina a base antes de nova importacao.'
    return configuracao['mensagem']


AUXILIAR_IMPORTACAO_PROCESSADORES = {
    'contas': {'validar': _validar_conteudo_planilha_importacao_contas_xlsx, 'executar': _importar_contas_validadas},
    'pessoas': {'validar': _validar_conteudo_planilha_importacao_pessoas_xlsx, 'executar': _importar_pessoas_validadas},
    'centros-custo': {'validar': _validar_conteudo_planilha_importacao_centros_custo_xlsx, 'executar': _importar_centros_custo_validados},
    'categorias': {'validar': _validar_conteudo_planilha_importacao_categorias_xlsx, 'executar': _importar_categorias_validadas},
}


def _filtrar_lancamentos_por_parametros(queryset, parametros):
    descricao = parametros.get('descricao', '').strip()
    numero_documento = parametros.get('numero_documento', '').strip()
    tipo = parametros.get('tipo', '').strip()
    status = parametros.get('status', '').strip()
    data_inicial = parametros.get('data_inicial', '').strip()
    data_final = parametros.get('data_final', '').strip()
    conta = parametros.get('conta', '').strip()
    pessoa = parametros.get('pessoa', '').strip()
    categoria = parametros.get('categoria', '').strip()

    if descricao:
        queryset = queryset.filter(descricao__icontains=descricao)
    if numero_documento:
        queryset = queryset.filter(numero_documento__icontains=numero_documento)
    if tipo:
        queryset = queryset.filter(tipo=tipo)
    if status:
        queryset = queryset.filter(status=status)
    if data_inicial:
        queryset = queryset.filter(data_pagamento__gte=data_inicial)
    if data_final:
        queryset = queryset.filter(data_pagamento__lte=data_final)
    if conta:
        queryset = queryset.filter(Q(conta_id=conta) | Q(conta_destino_id=conta))
    if pessoa:
        queryset = queryset.filter(pessoa_id=pessoa)
    if categoria:
        queryset = queryset.filter(categoria_id=categoria)

    return queryset


def _montar_resumo_visual_rateio_lancamentos(linhas_rateio):
    partes = []
    for lancamento in linhas_rateio[:3]:
        categoria_nome = str(lancamento.categoria) if lancamento.categoria else 'Sem categoria'
        partes.append(f'{categoria_nome}: R$ {lancamento.valor}')

    if len(linhas_rateio) > 3:
        partes.append(f'+{len(linhas_rateio) - 3} linha(s)')

    return ' | '.join(partes)


def _montar_lancamentos_visuais_listagem(lancamentos_queryset):
    lancamentos_filtrados = list(lancamentos_queryset)
    grupos_rateio_visiveis = list(dict.fromkeys(
        (lancamento.grupo_rateio or '').strip()
        for lancamento in lancamentos_filtrados
        if lancamento.com_rateio and (lancamento.grupo_rateio or '').strip()
    ))

    linhas_por_grupo = {}
    if grupos_rateio_visiveis:
        linhas_rateio = (
            LancamentoFinanceiro.objects.filter(
                com_rateio=True,
                grupo_rateio__in=grupos_rateio_visiveis,
            )
            .select_related('conta', 'conta_destino', 'pessoa', 'categoria', 'centro_custo')
            .order_by('data_pagamento', 'data_competencia', 'pk')
        )
        for linha_rateio in linhas_rateio:
            grupo_rateio = (linha_rateio.grupo_rateio or '').strip()
            if grupo_rateio:
                linhas_por_grupo.setdefault(grupo_rateio, []).append(linha_rateio)

    grupos_renderizados = set()
    lancamentos_visuais = []

    for lancamento in lancamentos_filtrados:
        grupo_rateio = (lancamento.grupo_rateio or '').strip()
        if lancamento.com_rateio and grupo_rateio:
            if grupo_rateio in grupos_renderizados:
                continue

            linhas_rateio = linhas_por_grupo.get(grupo_rateio) or [lancamento]
            representante = lancamento
            lancamentos_visuais.append({
                'eh_rateio': True,
                'token_selecao': f'grupo:{grupo_rateio}',
                'representante': representante,
                'linhas_rateio': linhas_rateio,
                'valor_total': sum((linha.valor for linha in linhas_rateio), Decimal('0.00')),
                'resumo_rateio': _montar_resumo_visual_rateio_lancamentos(linhas_rateio),
            })
            lancamentos_visuais[-1]['valor_total_formatado'] = _formatar_moeda_brl(
                lancamentos_visuais[-1]['valor_total']
            )
            grupos_renderizados.add(grupo_rateio)
            continue

        lancamentos_visuais.append({
            'eh_rateio': False,
            'token_selecao': f'lancamento:{lancamento.pk}',
            'representante': lancamento,
            'linhas_rateio': [],
            'valor_total': lancamento.valor,
            'valor_total_formatado': _formatar_moeda_brl(lancamento.valor),
            'resumo_rateio': '',
        })

    return lancamentos_visuais


def _resolver_ordenacao_lancamentos_listagem(ordenacao):
    ordenacao = (ordenacao or '').strip()
    if ordenacao in LANCAMENTO_ORDENACOES_LISTAGEM:
        return ordenacao
    return LANCAMENTO_ORDENACAO_PADRAO


def _valor_ordenacao_lancamento_visual(lancamento_visual, campo_ordenacao):
    lancamento = lancamento_visual['representante']

    if campo_ordenacao == 'descricao':
        return (lancamento.descricao or '').strip().lower()
    if campo_ordenacao == 'pessoa':
        return str(lancamento.pessoa or '').strip().lower()
    if campo_ordenacao == 'tipo':
        return (lancamento.get_tipo_display() or '').strip().lower()
    if campo_ordenacao == 'status':
        return (lancamento.get_status_display() or '').strip().lower()
    if campo_ordenacao == 'valor':
        return lancamento_visual['valor_total'] or Decimal('0.00')

    return lancamento.data_pagamento or lancamento.data_competencia or date.min


def _ordenar_lancamentos_visuais_listagem(lancamentos_visuais, ordenacao):
    ordenacao = _resolver_ordenacao_lancamentos_listagem(ordenacao)
    campo_ordenacao, direcao = LANCAMENTO_ORDENACOES_LISTAGEM[ordenacao]

    lancamentos_visuais = list(lancamentos_visuais)
    lancamentos_visuais.sort(
        key=lambda lancamento_visual: lancamento_visual['representante'].pk or 0,
        reverse=True,
    )
    lancamentos_visuais.sort(
        key=lambda lancamento_visual: _valor_ordenacao_lancamento_visual(
            lancamento_visual,
            campo_ordenacao,
        ),
        reverse=(direcao == 'desc'),
    )
    return lancamentos_visuais


def _montar_url_ordenacao_lancamentos_listagem(request, coluna, direcao):
    query_params = request.GET.copy()
    query_params['ordenacao'] = coluna if direcao == 'asc' else f'-{coluna}'
    query_params.pop('page', None)
    return f'?{query_params.urlencode()}'


def _montar_contexto_ordenacao_lancamentos_listagem(request, ordenacao_atual):
    ordenacao_atual = _resolver_ordenacao_lancamentos_listagem(ordenacao_atual)
    coluna_atual, direcao_atual = LANCAMENTO_ORDENACOES_LISTAGEM[ordenacao_atual]
    ordenacao_colunas = {}

    for coluna in LANCAMENTO_COLUNAS_ORDENAVEIS:
        esta_ativa = coluna == coluna_atual
        proxima_direcao = 'desc' if esta_ativa and direcao_atual == 'asc' else 'asc'
        ordenacao_colunas[coluna] = {
            'ativa': esta_ativa,
            'direcao': direcao_atual if esta_ativa else '',
            'url': _montar_url_ordenacao_lancamentos_listagem(
                request,
                coluna,
                proxima_direcao,
            ),
        }

    return {
        'ordenacao_atual': ordenacao_atual,
        'ordenacao_colunas': ordenacao_colunas,
    }


def _formatar_moeda_brl(valor) -> str:
    valor = (valor or Decimal('0.00')).quantize(Decimal('0.01'))
    valor_formatado = f'{valor:,.2f}'
    return valor_formatado.replace(',', 'X').replace('.', ',').replace('X', '.')


def _formatar_moeda_brl_exibicao(valor) -> str:
    valor = (valor or Decimal('0.00')).quantize(Decimal('0.01'))
    prefixo = '-R$ ' if valor < Decimal('0.00') else 'R$ '
    return f"{prefixo}{_formatar_moeda_brl(abs(valor))}"


def _calcular_variacao_percentual(valor_base: Decimal, valor_comparado: Decimal) -> Decimal | None:
    valor_base = valor_base or Decimal('0.00')
    valor_comparado = valor_comparado or Decimal('0.00')
    if valor_base == Decimal('0.00'):
        return Decimal('0.00') if valor_comparado == Decimal('0.00') else None
    return ((valor_comparado - valor_base) / valor_base) * Decimal('100')


def _formatar_percentual_relatorio(valor: Decimal | None) -> str:
    if valor is None:
        return '—'

    valor_quantizado = valor.quantize(Decimal('0.1'))
    texto = f'{valor_quantizado:.1f}'.replace('.', ',')
    if texto.endswith(',0'):
        texto = texto[:-2]
    return f'{texto}%'


def _formatar_periodo_comparacao(data_inicial: date, data_final: date) -> str:
    inicio_mes_fechado = data_inicial.day == 1
    fim_mes_fechado = data_final.day == monthrange(data_final.year, data_final.month)[1]

    if inicio_mes_fechado and fim_mes_fechado:
        inicio_label = data_inicial.strftime('%m/%y')
        fim_label = data_final.strftime('%m/%y')
        if data_inicial.year == data_final.year and data_inicial.month == data_final.month:
            return inicio_label
        return f'{inicio_label} a {fim_label}'

    return f'{data_inicial.strftime("%d/%m/%Y")} a {data_final.strftime("%d/%m/%Y")}'


def _abreviacao_mes_pt_br(mes: int) -> str:
    return (
        '',
        'jan',
        'fev',
        'mar',
        'abr',
        'mai',
        'jun',
        'jul',
        'ago',
        'set',
        'out',
        'nov',
        'dez',
    )[mes]


def _rotulo_mes_pt_br(ano: int, mes: int) -> str:
    return f'{_abreviacao_mes_pt_br(mes)}/{str(ano)[2:]}'


def _primeiro_dia_mes(data_base: date) -> date:
    return date(data_base.year, data_base.month, 1)


def _primeiro_dia_trimestre(data_base: date) -> date:
    mes_inicial = (((data_base.month - 1) // 3) * 3) + 1
    return date(data_base.year, mes_inicial, 1)


def _iterar_meses_periodo(data_inicial: date, data_final: date) -> list[date]:
    meses: list[date] = []
    cursor = _primeiro_dia_mes(data_inicial)
    ultimo = _primeiro_dia_mes(data_final)
    while cursor <= ultimo:
        meses.append(cursor)
        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)
    return meses


def _iterar_buckets_periodo(data_inicial: date, data_final: date, granularidade: str) -> list[dict[str, object]]:
    buckets: list[dict[str, object]] = []

    if granularidade == 'dias':
        cursor = data_inicial
        while cursor <= data_final:
            buckets.append(
                {
                    'chave': cursor.isoformat(),
                    'rotulo': f'{cursor.day:02d} {_abreviacao_mes_pt_br(cursor.month)}',
                    'inicio': cursor,
                    'fim': cursor,
                }
            )
            cursor += timedelta(days=1)
        return buckets

    if granularidade == 'anos':
        cursor = date(data_inicial.year, 1, 1)
        ultimo = date(data_final.year, 1, 1)
        while cursor <= ultimo:
            buckets.append(
                {
                    'chave': f'{cursor.year}',
                    'rotulo': f'{cursor.year}',
                    'inicio': cursor,
                    'fim': date(cursor.year, 12, 31),
                }
            )
            cursor = date(cursor.year + 1, 1, 1)
        return buckets

    if granularidade == 'trimestres':
        cursor = _primeiro_dia_trimestre(data_inicial)
        ultimo = _primeiro_dia_trimestre(data_final)
        while cursor <= ultimo:
            trimestre = ((cursor.month - 1) // 3) + 1
            fim_mes = cursor.month + 2
            fim = date(cursor.year, fim_mes, monthrange(cursor.year, fim_mes)[1])
            buckets.append(
                {
                    'chave': f'{cursor.year}-T{trimestre}',
                    'rotulo': f'{trimestre}º tri/{str(cursor.year)[2:]}',
                    'inicio': cursor,
                    'fim': fim,
                }
            )
            if cursor.month >= 10:
                cursor = date(cursor.year + 1, 1, 1)
            else:
                cursor = date(cursor.year, cursor.month + 3, 1)
        return buckets

    cursor = _primeiro_dia_mes(data_inicial)
    ultimo = _primeiro_dia_mes(data_final)
    while cursor <= ultimo:
        fim = date(cursor.year, cursor.month, monthrange(cursor.year, cursor.month)[1])
        buckets.append(
            {
                'chave': f'{cursor.year}-{cursor.month:02d}',
                'rotulo': _rotulo_mes_pt_br(cursor.year, cursor.month),
                'inicio': cursor,
                'fim': fim,
            }
        )
        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)
    return buckets


def _chave_bucket_data_operacional(data_operacional: date, granularidade: str) -> str:
    if granularidade == 'dias':
        return data_operacional.isoformat()
    if granularidade == 'anos':
        return f'{data_operacional.year}'
    if granularidade == 'trimestres':
        trimestre = ((data_operacional.month - 1) // 3) + 1
        return f'{data_operacional.year}-T{trimestre}'
    return f'{data_operacional.year}-{data_operacional.month:02d}'


def _label_categoria_evolucao(categoria: CategoriaFinanceira) -> str:
    if categoria.categoria_pai_id:
        return f'{categoria.categoria_pai.nome} / {categoria.nome}'
    return categoria.nome


def _categoria_eh_agregadora(categoria: CategoriaFinanceira) -> bool:
    return not categoria.permite_vinculo_em_lancamento


def _rotulo_curto_lista_nomes(valores: list[str], *, limite: int = 2) -> str:
    nomes = [valor for valor in valores if valor]
    if not nomes:
        return ''
    if len(nomes) <= limite:
        return ', '.join(nomes)
    return f"{', '.join(nomes[:limite])} +{len(nomes) - limite}"


def _formatar_rotulo_valor_grafico(valor: Decimal) -> str:
    valor_absoluto = abs((valor or Decimal('0.00')).quantize(Decimal('0.01')))

    if valor_absoluto >= Decimal('1000000'):
        valor_milhoes = (valor_absoluto / Decimal('1000000')).quantize(Decimal('0.1'))
        texto = str(valor_milhoes).replace('.', ',').rstrip('0').rstrip(',')
        return f'{texto} mi'

    if valor_absoluto >= Decimal('1000'):
        valor_mil = (valor_absoluto / Decimal('1000')).quantize(Decimal('0.1'))
        texto = str(valor_mil).replace('.', ',').rstrip('0').rstrip(',')
        return f'{texto} mil'

    if valor_absoluto == valor_absoluto.to_integral_value():
        return f'{int(valor_absoluto)}'

    return _formatar_moeda_brl(valor_absoluto).replace('R$ ', '')


def _calcular_passo_bonito_eixo_y(valor_maximo: Decimal, *, divisores: int = 4) -> Decimal:
    valor_maximo = abs(valor_maximo or Decimal('0.00'))
    if valor_maximo <= Decimal('0.00'):
        return Decimal('1')

    passo_bruto = valor_maximo / Decimal(max(divisores, 1))
    expoente = int(math.floor(math.log10(float(passo_bruto)))) if passo_bruto > 0 else 0
    base = Decimal('10') ** expoente
    multiplicadores = (
        Decimal('1'),
        Decimal('2'),
        Decimal('2.5'),
        Decimal('5'),
        Decimal('7.5'),
        Decimal('10'),
    )

    for multiplicador in multiplicadores:
        passo = base * multiplicador
        if passo >= passo_bruto:
            return passo

    return base * Decimal('10')


def _montar_ticks_bonitos_eixo_y(valores: list[Decimal], *, divisores: int = 4) -> tuple[Decimal, list[Decimal]]:
    valores_absolutos = [abs(valor or Decimal('0.00')) for valor in valores]
    valor_maximo = max(valores_absolutos, default=Decimal('0.00'))
    passo = _calcular_passo_bonito_eixo_y(valor_maximo, divisores=divisores)

    if valor_maximo <= Decimal('0.00'):
        limite_superior = passo * Decimal(divisores)
    else:
        limite_superior = (valor_maximo / passo).to_integral_value(rounding=ROUND_CEILING) * passo

    ticks = [limite_superior - (passo * indice) for indice in range(divisores + 1)]
    return limite_superior, ticks


def _rotulos_visiveis_eixo_x(labels: list[str], posicao_x) -> list[dict[str, object]]:
    if not labels:
        return []

    total = len(labels)
    if total <= 8:
        indices = list(range(total))
    else:
        max_rotulos = 8
        passo = max(1, (total - 1) // (max_rotulos - 1))
        indices = list(range(0, total, passo))
        if indices[-1] != total - 1:
            indices.append(total - 1)

    vistos: set[int] = set()
    rotulos = []
    for indice in indices:
        if indice in vistos or indice >= total:
            continue
        vistos.add(indice)
        rotulos.append(
            {
                'x': posicao_x(indice),
                'x_svg': f'{posicao_x(indice):.2f}',
                'label': labels[indice],
            }
        )
    return rotulos


def _descricao_leitura_temporal_evolucao(granularidade: str) -> str:
    return {
        'dias': 'uma leitura diaria',
        'meses': 'uma leitura mensal',
        'trimestres': 'uma leitura trimestral',
        'anos': 'uma leitura anual',
    }.get(granularidade, 'uma leitura temporal')


def _ajustar_colisoes_rotulos_grafico(series_svg: list[dict[str, object]]) -> None:
    rotulos_visiveis: list[dict[str, object]] = []
    for serie in series_svg:
        for ponto in serie['pontos']:
            if ponto.get('mostrar_rotulo'):
                rotulos_visiveis.append(ponto)

    rotulos_visiveis.sort(key=lambda item: (item['x_float'], item['rotulo_y_float']))
    ultimo_rotulo: dict[str, object] | None = None

    for ponto in rotulos_visiveis:
        largura_estimada = max(44.0, min(98.0, float(len(ponto['label_curto'])) * 6.2))
        ponto['rotulo_largura_estimada'] = largura_estimada
        ponto['nivel_colisao'] = 0

        if ultimo_rotulo is not None:
            distancia_x = abs(ponto['x_float'] - ultimo_rotulo['x_float'])
            limite_colisao = ((largura_estimada + ultimo_rotulo['rotulo_largura_estimada']) / 2.0) - 6.0
            distancia_y = abs(ponto['rotulo_y_float'] - ultimo_rotulo['rotulo_y_float'])

            if distancia_x < limite_colisao and distancia_y < 18.0:
                ponto['nivel_colisao'] = int(ultimo_rotulo.get('nivel_colisao', 0)) + 1
                deslocamento = 22.0 * ponto['nivel_colisao']
                if ponto['rotulo_posicao'] == 'acima':
                    ponto['rotulo_y_float'] = max(18.0, ponto['rotulo_y_float'] - deslocamento)
                    ponto['linha_rotulo_y_float'] = ponto['rotulo_y_float'] + 5.0
                else:
                    ponto['rotulo_y_float'] = ponto['rotulo_y_float'] + deslocamento
                    ponto['linha_rotulo_y_float'] = ponto['rotulo_y_float'] - 12.0

        ponto['rotulo_y_svg'] = f"{ponto['rotulo_y_float']:.2f}"
        ponto['linha_rotulo_y_svg'] = f"{ponto['linha_rotulo_y_float']:.2f}"
        ultimo_rotulo = ponto


def _montar_eixo_svg_evolucao(
    labels: list[str],
    series: list[dict[str, object]],
) -> dict[str, object]:
    largura = max(920, 220 + (min(max(len(labels), 2), 12) * 72))
    altura = 384
    padding_esquerda = 88
    padding_direita = 28
    padding_topo = 22
    padding_base = 64
    margem_plot_esquerda = 28
    margem_plot_direita = 18
    x_inicial = padding_esquerda + margem_plot_esquerda
    x_final = largura - padding_direita - margem_plot_direita
    largura_grafico = max(1, x_final - x_inicial)
    altura_grafico = max(1, altura - padding_topo - padding_base)

    valores = [Decimal('0.00')]
    for serie in series:
        valores.extend(abs(valor or Decimal('0.00')) for valor in serie['valores'])

    divisores = 4
    limite_inferior = Decimal('0.00')
    limite_superior, ticks = _montar_ticks_bonitos_eixo_y(valores, divisores=divisores)
    amplitude_total = limite_superior - limite_inferior
    if amplitude_total <= Decimal('0.00'):
        amplitude_total = Decimal('1.00')

    def posicao_y(valor: Decimal) -> float:
        valor_absoluto = abs(valor or Decimal('0.00'))
        proporcao = float((valor_absoluto - limite_inferior) / amplitude_total)
        return padding_topo + (altura_grafico * (1 - proporcao))

    def posicao_x(indice: int) -> float:
        if len(labels) <= 1:
            return x_inicial + (largura_grafico / 2)
        passo = largura_grafico / (len(labels) - 1)
        return x_inicial + (passo * indice)

    grade: list[dict[str, object]] = []
    for valor in ticks:
        grade.append(
            {
                'y': posicao_y(valor),
                'label': _formatar_rotulo_valor_grafico(valor),
            }
        )

    zero_y = posicao_y(Decimal('0.00'))
    rotulos_eixo_x = _rotulos_visiveis_eixo_x(labels, posicao_x)

    return {
        'largura': largura,
        'altura': altura,
        'padding_esquerda': padding_esquerda,
        'padding_direita': padding_direita,
        'padding_topo': padding_topo,
        'padding_base': padding_base,
        'x_inicial': x_inicial,
        'x_final': x_final,
        'zero_y': zero_y,
        'grade': grade,
        'rotulos_eixo_x': rotulos_eixo_x,
        'posicao_x': posicao_x,
        'posicao_y': posicao_y,
    }


def _montar_contexto_svg_evolucao(
    labels: list[str],
    series: list[dict[str, object]],
    *,
    mostrar_valores: bool = False,
) -> dict[str, object]:
    if not labels or not series:
        return {'tem_dados': False}

    eixo = _montar_eixo_svg_evolucao(labels, series)
    series_svg: list[dict[str, object]] = []
    for serie in series:
        pontos = []
        path_data = []
        for indice, valor in enumerate(serie['valores']):
            x = eixo['posicao_x'](indice)
            y = eixo['posicao_y'](valor)
            rotulo_acima = y > 56
            rotulo_y = y - 14 if rotulo_acima else y + 22
            linha_rotulo_y = y - 6 if rotulo_acima else y + 6
            pontos.append(
                {
                    'x': x,
                    'y': y,
                    'x_svg': f'{x:.2f}',
                    'y_svg': f'{y:.2f}',
                    'x_float': x,
                    'y_float': y,
                    'label_mes': labels[indice],
                    'label_valor': f'R$ {_formatar_moeda_brl(abs(valor))}',
                    'label_curto': _formatar_rotulo_valor_grafico(valor),
                    'mostrar_rotulo': mostrar_valores and abs(valor) > Decimal('0.00'),
                    'rotulo_y_float': rotulo_y,
                    'linha_rotulo_y_float': linha_rotulo_y,
                    'rotulo_y_svg': f'{rotulo_y:.2f}',
                    'linha_rotulo_y_svg': f'{linha_rotulo_y:.2f}',
                    'rotulo_posicao': 'acima' if rotulo_acima else 'abaixo',
                }
            )
            path_data.append(f'{"M" if indice == 0 else "L"} {x:.2f} {y:.2f}')
        series_svg.append(
            {
                'label': serie['label'],
                'cor': serie['cor'],
                'path_data': ' '.join(path_data),
                'pontos': pontos,
            }
        )

    _ajustar_colisoes_rotulos_grafico(series_svg)

    return {
        'tem_dados': True,
        'largura': eixo['largura'],
        'altura': eixo['altura'],
        'render_width': eixo['largura'],
        'padding_base': eixo['padding_base'],
        'eixo_label_y': eixo['altura'] - eixo['padding_base'] + 18,
        'zero_y': eixo['zero_y'],
        'grade': eixo['grade'],
        'rotulos_eixo_x': eixo['rotulos_eixo_x'],
        'series': series_svg,
    }


def _somar_valores_series(series: list[dict[str, object]]) -> list[Decimal]:
    tamanho = max((len(serie.get('valores', [])) for serie in series), default=0)
    totais = [Decimal('0.00') for _ in range(tamanho)]
    for serie in series:
        for indice, valor in enumerate(serie.get('valores', [])):
            totais[indice] += abs(valor or Decimal('0.00'))
    return totais


def _resolver_conta_referencia_lancamentos_listagem(request) -> int | None:
    conta_raw = (request.GET.get('conta') or '').strip()
    if not conta_raw:
        return None

    try:
        return int(conta_raw)
    except (TypeError, ValueError):
        return None


def _componentes_resumo_lancamento_visual_listagem(
    lancamento_visual: dict[str, object],
    *,
    conta_referencia_id: int | None = None,
) -> dict[str, Decimal]:
    lancamento = lancamento_visual['representante']
    valor = lancamento_visual.get('valor_total') or Decimal('0.00')
    componentes = {
        'receitas': Decimal('0.00'),
        'despesas': Decimal('0.00'),
        'transferencias_entrada': Decimal('0.00'),
        'transferencias_saida': Decimal('0.00'),
    }

    if lancamento.tipo == LancamentoFinanceiro.TipoLancamento.RECEITA:
        componentes['receitas'] = valor
    elif lancamento.tipo == LancamentoFinanceiro.TipoLancamento.DESPESA:
        componentes['despesas'] = valor
    elif lancamento.tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
        if not conta_referencia_id:
            componentes['transferencias_entrada'] = valor
            componentes['transferencias_saida'] = valor
        elif lancamento.conta_destino_id == conta_referencia_id and lancamento.conta_id != conta_referencia_id:
            componentes['transferencias_entrada'] = valor
        else:
            componentes['transferencias_saida'] = valor

    componentes['saldo_liquido'] = (
        componentes['receitas']
        + componentes['transferencias_entrada']
        - componentes['despesas']
        - componentes['transferencias_saida']
    )
    return componentes


def _montar_resumo_financeiro_lancamentos_visuais(
    lancamentos_visuais: list[dict[str, object]],
    *,
    conta_referencia_id: int | None = None,
) -> dict[str, object]:
    resumo = {
        'quantidade': len(lancamentos_visuais),
        'receitas': Decimal('0.00'),
        'despesas': Decimal('0.00'),
        'transferencias_entrada': Decimal('0.00'),
        'transferencias_saida': Decimal('0.00'),
        'saldo_liquido': Decimal('0.00'),
        'valor_quitado': Decimal('0.00'),
        'valor_aberto': Decimal('0.00'),
    }

    for lancamento_visual in lancamentos_visuais:
        componentes = _componentes_resumo_lancamento_visual_listagem(
            lancamento_visual,
            conta_referencia_id=conta_referencia_id,
        )
        for chave in (
            'receitas',
            'despesas',
            'transferencias_entrada',
            'transferencias_saida',
            'saldo_liquido',
        ):
            resumo[chave] += componentes[chave]

        lancamento = lancamento_visual['representante']
        if lancamento.status == LancamentoFinanceiro.StatusLancamento.QUITADO:
            resumo['valor_quitado'] += componentes['saldo_liquido']
        elif lancamento.status == LancamentoFinanceiro.StatusLancamento.ABERTO:
            resumo['valor_aberto'] += componentes['saldo_liquido']

    for chave in (
        'receitas',
        'despesas',
        'transferencias_entrada',
        'transferencias_saida',
        'saldo_liquido',
        'valor_quitado',
        'valor_aberto',
    ):
        resumo[f'{chave}_formatado'] = _formatar_moeda_brl(resumo[chave])

    return resumo


def _normalizar_colunas_configuraveis_lancamentos(colunas):
    colunas_validas = []
    for coluna in colunas or []:
        coluna = (coluna or '').strip()
        if coluna in LANCAMENTO_LISTAGEM_COLUNAS_CONFIGURAVEIS and coluna not in colunas_validas:
            colunas_validas.append(coluna)
    return tuple(colunas_validas)


def _resolver_colunas_configuraveis_lancamentos(request):
    if request.GET.get('restaurar_colunas') == '1':
        request.session.pop(LANCAMENTO_LISTAGEM_COLUNAS_SESSAO, None)
        return LANCAMENTO_LISTAGEM_COLUNAS_CONFIGURAVEIS_PADRAO

    if request.GET.get('config_colunas') == '1':
        selecionadas = _normalizar_colunas_configuraveis_lancamentos(
            request.GET.getlist('colunas_lancamento')
        )
        ordenadas = sorted(
            selecionadas,
            key=lambda coluna: (
                _resolver_ordem_coluna_lancamento(request, coluna),
                LANCAMENTO_LISTAGEM_COLUNAS_CONFIGURAVEIS.index(coluna),
            ),
        )
        request.session[LANCAMENTO_LISTAGEM_COLUNAS_SESSAO] = list(ordenadas)
        return tuple(ordenadas)

    return _normalizar_colunas_configuraveis_lancamentos(
        request.session.get(
            LANCAMENTO_LISTAGEM_COLUNAS_SESSAO,
            LANCAMENTO_LISTAGEM_COLUNAS_CONFIGURAVEIS_PADRAO,
        )
    )


def _resolver_ordem_coluna_lancamento(request, coluna):
    try:
        return int(request.GET.get(f'ordem_coluna_{coluna}', '') or 999)
    except (TypeError, ValueError):
        return 999


def _montar_coluna_lancamento_contexto(coluna, *, selecionada=True, ordem=None):
    meta = LANCAMENTO_LISTAGEM_COLUNAS_META[coluna]
    return {
        'id': coluna,
        'rotulo': meta['rotulo'],
        'ordenacao': meta['ordenacao'],
        'essencial': meta['essencial'],
        'selecionada': selecionada,
        'ordem': ordem,
    }


def _montar_contexto_colunas_lancamentos(request):
    colunas_configuraveis = _resolver_colunas_configuraveis_lancamentos(request)
    colunas_visiveis = [
        _montar_coluna_lancamento_contexto(coluna)
        for coluna in LANCAMENTO_LISTAGEM_COLUNAS_ESSENCIAIS
    ]
    colunas_visiveis.extend(
        _montar_coluna_lancamento_contexto(coluna)
        for coluna in colunas_configuraveis
    )
    colunas_configuraveis_contexto = []
    for indice, coluna in enumerate(LANCAMENTO_LISTAGEM_COLUNAS_CONFIGURAVEIS, start=1):
        ordem = (
            colunas_configuraveis.index(coluna) + 1
            if coluna in colunas_configuraveis
            else indice
        )
        colunas_configuraveis_contexto.append(
            _montar_coluna_lancamento_contexto(
                coluna,
                selecionada=coluna in colunas_configuraveis,
                ordem=ordem,
            )
        )

    return {
        'colunas_lancamento_visiveis': colunas_visiveis,
        'colunas_lancamento_configuraveis': colunas_configuraveis_contexto,
        'colunas_lancamento_configuraveis_selecionadas': colunas_configuraveis,
        'colunas_lancamento_configuracao_ativa': (
            colunas_configuraveis != LANCAMENTO_LISTAGEM_COLUNAS_CONFIGURAVEIS_PADRAO
        ),
        'colunas_lancamento_limite_ordem': range(
            1,
            len(LANCAMENTO_LISTAGEM_COLUNAS_CONFIGURAVEIS) + 1,
        ),
    }


def _resolver_lancamentos_por_pagina(request) -> int:
    valor_raw = (request.GET.get('por_pagina') or '').strip()
    if valor_raw:
        try:
            valor = int(valor_raw)
        except (TypeError, ValueError):
            valor = LANCAMENTO_LISTAGEM_POR_PAGINA_PADRAO
        if valor in LANCAMENTO_LISTAGEM_POR_PAGINA_OPCOES:
            request.session['financeiro_lancamentos_por_pagina'] = valor
            return valor

    valor_sessao = request.session.get('financeiro_lancamentos_por_pagina')
    if valor_sessao in LANCAMENTO_LISTAGEM_POR_PAGINA_OPCOES:
        return valor_sessao
    return LANCAMENTO_LISTAGEM_POR_PAGINA_PADRAO


def _montar_url_lancamentos_com_query(request, **substituicoes):
    query_params = request.GET.copy()
    for chave, valor in substituicoes.items():
        if valor in (None, ''):
            query_params.pop(chave, None)
        else:
            query_params[chave] = valor
    return f'?{query_params.urlencode()}'


def _request_possui_parametros_get(request, parametros: tuple[str, ...]) -> bool:
    for parametro in parametros:
        if any((valor or '').strip() for valor in request.GET.getlist(parametro)):
            return True
    return False


def _resolver_lancamentos_para_acoes_em_lote(tokens_selecao):
    lancamento_ids = set()
    grupos_rateio = set()

    for token in tokens_selecao:
        token = (token or '').strip()
        if not token:
            continue
        if token.isdigit():
            lancamento_ids.add(int(token))
            continue
        if token.startswith('lancamento:'):
            lancamento_id = token.split(':', 1)[1].strip()
            if lancamento_id.isdigit():
                lancamento_ids.add(int(lancamento_id))
            continue
        if token.startswith('grupo:'):
            grupo_rateio = token.split(':', 1)[1].strip()
            if grupo_rateio:
                grupos_rateio.add(grupo_rateio)

    if not lancamento_ids and not grupos_rateio:
        return []

    filtros = Q()
    if lancamento_ids:
        filtros |= Q(pk__in=lancamento_ids)
    if grupos_rateio:
        filtros |= Q(com_rateio=True, grupo_rateio__in=grupos_rateio)

    return list(
        LancamentoFinanceiro.objects.filter(filtros)
        .select_related('conta', 'conta_destino', 'pessoa', 'categoria', 'centro_custo')
        .order_by('pk')
    )


def _centena_por_extenso(numero: int) -> str:
    if numero == 0:
        return ''
    if numero < 20:
        return UNIDADES_EXTENSO[numero]
    if numero < 100:
        dezena, resto = divmod(numero, 10)
        texto = DEZENAS_EXTENSO[dezena]
        if resto:
            texto = f'{texto} e {UNIDADES_EXTENSO[resto]}'
        return texto
    if numero == 100:
        return 'cem'
    centena, resto = divmod(numero, 100)
    texto = CENTENAS_EXTENSO[centena]
    if resto:
        texto = f'{texto} e {_centena_por_extenso(resto)}'
    return texto


def _juntar_partes_extenso(partes: list[str]) -> str:
    if not partes:
        return ''
    if len(partes) == 1:
        return partes[0]
    if len(partes) == 2:
        return f'{partes[0]} e {partes[1]}'
    return ', '.join(partes[:-1]) + f' e {partes[-1]}'


def _numero_por_extenso(numero: int) -> str:
    if numero == 0:
        return UNIDADES_EXTENSO[0]

    grupos = [
        ('', ''),
        ('mil', 'mil'),
        ('milhao', 'milhoes'),
        ('bilhao', 'bilhoes'),
    ]
    partes: list[str] = []
    indice_grupo = 0

    while numero > 0:
        numero, grupo_valor = divmod(numero, 1000)
        if grupo_valor:
            grupo_singular, grupo_plural = grupos[indice_grupo]
            if indice_grupo == 1 and grupo_valor == 1:
                partes.append('mil')
            else:
                texto_grupo = _centena_por_extenso(grupo_valor)
                if indice_grupo > 0:
                    sufixo = grupo_singular if grupo_valor == 1 else grupo_plural
                    texto_grupo = f'{texto_grupo} {sufixo}'
                partes.append(texto_grupo)
        indice_grupo += 1

    partes.reverse()
    return _juntar_partes_extenso(partes)


def _valor_por_extenso(valor: Decimal) -> str:
    valor_normalizado = valor.quantize(Decimal('0.01'))
    reais = int(valor_normalizado)
    centavos = int((valor_normalizado - Decimal(reais)) * 100)

    partes: list[str] = []
    if reais or not centavos:
        unidade_real = 'real' if reais == 1 else 'reais'
        partes.append(f'{_numero_por_extenso(reais)} {unidade_real}')
    if centavos:
        unidade_centavo = 'centavo' if centavos == 1 else 'centavos'
        partes.append(f'{_numero_por_extenso(centavos)} {unidade_centavo}')

    return _juntar_partes_extenso(partes)


def _data_documental_por_extenso(data_referencia: date) -> str:
    return f'{data_referencia.day} de {MESES_EXTENSO[data_referencia.month - 1]} de {data_referencia.year}'


def _append_query_params(url: str, params: dict[str, str]) -> str:
    if not url:
        return url
    partes = urlsplit(url)
    query = dict(parse_qsl(partes.query, keep_blank_values=True))
    query.update({k: v for k, v in params.items() if v is not None})
    return urlunsplit((partes.scheme, partes.netloc, partes.path, urlencode(query), partes.fragment))


class FinanceiroReturnToMixin:
    return_to_param = 'return_to'

    def _get_return_to_url(self) -> str:
        return_to = (
            self.request.POST.get(self.return_to_param)
            or self.request.GET.get(self.return_to_param)
            or ''
        ).strip()
        if not return_to:
            return ''
        if not url_has_allowed_host_and_scheme(
            return_to,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return ''
        return return_to

    def _get_configured_success_url(self) -> str:
        success_url = getattr(self, 'success_url', '')
        if success_url:
            return str(success_url)
        return super().get_success_url()

    def get_success_url(self):
        return self._get_return_to_url() or self._get_configured_success_url()

    def get_cancel_url(self):
        return self._get_return_to_url() or self._get_configured_success_url()


class FinanceiroFormMixin(FinanceiroReturnToMixin, FinanceiroPermissaoMixin):
    page_title = ''
    submit_label = 'Salvar'
    success_message = 'Registro salvo com sucesso.'
    allow_save_and_stay = False
    save_and_stay_param = 'salvar_permanecer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['submit_label'] = self.submit_label
        context['cancel_url'] = self.get_cancel_url()
        context['return_to'] = self._get_return_to_url()
        context['allow_save_and_stay'] = self.allow_save_and_stay
        context['save_and_stay_param'] = self.save_and_stay_param
        return context

    def _should_save_and_stay(self) -> bool:
        return self.allow_save_and_stay and self.save_and_stay_param in self.request.POST

    def get_save_and_stay_url(self) -> str:
        return_to = self._get_return_to_url()
        if not return_to:
            return self.request.path
        return f'{self.request.path}?{urlencode({self.return_to_param: return_to})}'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        if self._should_save_and_stay():
            return redirect(self.get_save_and_stay_url())
        return response


class FinanceiroDeleteMixin(FinanceiroReturnToMixin, FinanceiroPermissaoMixin, DeleteView):
    template_name = 'financeiro/confirm_delete.html'
    success_message = 'Registro excluido com sucesso.'
    page_title = 'Confirmar exclusao'
    cancel_url = reverse_lazy('financeiro:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['cancel_url'] = self.get_cancel_url()
        context['return_to'] = self._get_return_to_url()
        context['object_label'] = str(self.object)
        return context

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class FinanceiroHomeView(FinanceiroPermissaoMixin, TemplateView):
    permissao_requerida = 'financeiro.lancamentos.listar'
    template_name = 'financeiro/home.html'


class FinanceiroPeriodoMixin(FinanceiroPermissaoMixin):
    def _periodo_padrao(self) -> tuple[date, date]:
        hoje = date.today()
        primeiro_dia = hoje.replace(day=1)
        ultimo_dia = hoje.replace(day=monthrange(hoje.year, hoje.month)[1])
        return primeiro_dia, ultimo_dia

    def _parse_contas(self) -> tuple[list[ContaFinanceira], list[str], list[int]]:
        contas_disponiveis = _ordenar_itens_insensivel(
            ContaFinanceira.objects.all(),
            'nome',
        )
        contas_por_id = {conta.id: conta for conta in contas_disponiveis}
        selected_ids_raw = [valor.strip() for valor in self.request.GET.getlist('contas') if valor.strip()]

        selected_ids: list[int] = []
        for valor in selected_ids_raw:
            try:
                conta_id = int(valor)
            except ValueError:
                continue
            if conta_id in contas_por_id:
                selected_ids.append(conta_id)

        if not selected_ids:
            selected_ids = list(contas_por_id.keys())

        return contas_disponiveis, selected_ids_raw, selected_ids

    def _parse_periodo(self) -> tuple[str, str, date | None, date | None, str]:
        data_inicial_raw = self.request.GET.get('data_inicial', '').strip()
        data_final_raw = self.request.GET.get('data_final', '').strip()
        periodo_error = ''

        if not data_inicial_raw and not data_final_raw:
            data_inicial, data_final = self._periodo_padrao()
            data_inicial_raw = data_inicial.isoformat()
            data_final_raw = data_final.isoformat()
        elif not data_inicial_raw or not data_final_raw:
            data_inicial = None
            data_final = None
            periodo_error = 'Informe data inicial e data final para gerar o resumo.'
        else:
            try:
                data_inicial = date.fromisoformat(data_inicial_raw)
                data_final = date.fromisoformat(data_final_raw)
            except ValueError:
                data_inicial = None
                data_final = None
                periodo_error = 'Periodo invalido. Revise as datas informadas.'

        if data_inicial and data_final and data_inicial > data_final:
            periodo_error = 'A data inicial nao pode ser maior que a data final.'
            data_inicial = None
            data_final = None

        return data_inicial_raw, data_final_raw, data_inicial, data_final, periodo_error

    def _parse_checkbox(self, param_name: str) -> bool:
        valores = [valor.strip().lower() for valor in self.request.GET.getlist(param_name)]
        if not valores:
            return False

        for valor in reversed(valores):
            if valor in {'1', 'true', 'on', 'yes'}:
                return True
            if valor in {'0', 'false', 'off', 'no', ''}:
                return False
        return False

    def _calcular_saldos_por_conta(
        self,
        data_referencia: date,
        selected_ids: list[int],
    ) -> tuple[list[dict[str, object]], Decimal]:
        contas = list(
            ContaFinanceira.objects.filter(id__in=selected_ids, data_saldo_inicial__lte=data_referencia)
            .only('id', 'nome', 'saldo_inicial', 'data_saldo_inicial')
            .order_by('nome')
        )
        contas_por_id = {conta.id: conta for conta in contas}

        for conta in contas:
            conta.saldo_calculado = conta.saldo_inicial or Decimal('0.00')

        if contas_por_id:
            lancamentos = (
                LancamentoFinanceiro.objects.filter(
                    Q(conta_id__in=contas_por_id.keys()) | Q(conta_destino_id__in=contas_por_id.keys()),
                    status=LancamentoFinanceiro.StatusLancamento.QUITADO,
                )
                .annotate(data_operacional=Coalesce('data_pagamento', 'data_competencia'))
                .filter(data_operacional__lte=data_referencia)
                .only('tipo', 'valor', 'conta_id', 'conta_destino_id')
            )

            for lancamento in lancamentos:
                if (
                    lancamento.tipo == LancamentoFinanceiro.TipoLancamento.RECEITA
                    and lancamento.conta_id in contas_por_id
                ):
                    contas_por_id[lancamento.conta_id].saldo_calculado += lancamento.valor
                elif (
                    lancamento.tipo == LancamentoFinanceiro.TipoLancamento.DESPESA
                    and lancamento.conta_id in contas_por_id
                ):
                    contas_por_id[lancamento.conta_id].saldo_calculado -= lancamento.valor
                elif lancamento.tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
                    if lancamento.conta_id in contas_por_id:
                        contas_por_id[lancamento.conta_id].saldo_calculado -= lancamento.valor
                    if lancamento.conta_destino_id in contas_por_id:
                        contas_por_id[lancamento.conta_destino_id].saldo_calculado += lancamento.valor

        composicao = [{'conta': conta, 'saldo': conta.saldo_calculado} for conta in contas]
        total = sum((item['saldo'] for item in composicao), Decimal('0.00'))
        return composicao, total

    def _lancamentos_receitas_despesas(
        self,
        data_inicial: date,
        data_final: date,
        selected_ids: list[int],
    ) -> tuple[list[LancamentoFinanceiro], list[LancamentoFinanceiro], Decimal, Decimal]:
        receitas = list(
            LancamentoFinanceiro.objects.filter(
                status=LancamentoFinanceiro.StatusLancamento.QUITADO,
                tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
                conta_id__in=selected_ids,
            )
            .annotate(data_operacional=Coalesce('data_pagamento', 'data_competencia'))
            .filter(data_operacional__gte=data_inicial, data_operacional__lte=data_final)
            .select_related('conta', 'pessoa', 'categoria', 'centro_custo')
            .order_by('data_operacional', 'criado_em', 'pk')
        )
        despesas = list(
            LancamentoFinanceiro.objects.filter(
                status=LancamentoFinanceiro.StatusLancamento.QUITADO,
                tipo=LancamentoFinanceiro.TipoLancamento.DESPESA,
                conta_id__in=selected_ids,
            )
            .annotate(data_operacional=Coalesce('data_pagamento', 'data_competencia'))
            .filter(data_operacional__gte=data_inicial, data_operacional__lte=data_final)
            .select_related('conta', 'pessoa', 'categoria', 'centro_custo')
            .order_by('data_operacional', 'criado_em', 'pk')
        )
        total_receitas = sum((lancamento.valor for lancamento in receitas), Decimal('0.00'))
        total_despesas = sum((lancamento.valor for lancamento in despesas), Decimal('0.00'))
        return receitas, despesas, total_receitas, total_despesas

    def _lancamentos_transferencias(
        self,
        data_inicial: date,
        data_final: date,
        selected_ids: list[int],
    ) -> tuple[list[LancamentoFinanceiro], Decimal, Decimal, Decimal]:
        transferencias = list(
            LancamentoFinanceiro.objects.filter(
                Q(conta_id__in=selected_ids) | Q(conta_destino_id__in=selected_ids),
                status=LancamentoFinanceiro.StatusLancamento.QUITADO,
                tipo=LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA,
            )
            .annotate(data_operacional=Coalesce('data_pagamento', 'data_competencia'))
            .filter(data_operacional__gte=data_inicial, data_operacional__lte=data_final)
            .select_related('conta', 'conta_destino')
            .distinct()
            .order_by('data_operacional', 'criado_em', 'pk')
        )
        total_transferencias = sum((lancamento.valor for lancamento in transferencias), Decimal('0.00'))
        selected_ids_set = set(selected_ids)
        total_transferencias_saida = sum(
            (
                lancamento.valor
                for lancamento in transferencias
                if lancamento.conta_id in selected_ids_set
            ),
            Decimal('0.00'),
        )
        total_transferencias_entrada = sum(
            (
                lancamento.valor
                for lancamento in transferencias
                if lancamento.conta_destino_id in selected_ids_set
            ),
            Decimal('0.00'),
        )
        return (
            transferencias,
            total_transferencias,
            total_transferencias_entrada,
            total_transferencias_saida,
        )

    def _resumir_transferencias_fora_do_universo(
        self,
        data_inicial: date,
        data_final: date,
        selected_ids: list[int],
    ) -> dict[str, object]:
        selected_ids_set = set(selected_ids)
        transferencias = list(
            LancamentoFinanceiro.objects.filter(
                Q(conta_id__in=selected_ids) | Q(conta_destino_id__in=selected_ids),
                status=LancamentoFinanceiro.StatusLancamento.QUITADO,
                tipo=LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA,
            )
            .annotate(data_operacional=Coalesce('data_pagamento', 'data_competencia'))
            .filter(data_operacional__gte=data_inicial, data_operacional__lte=data_final)
            .select_related('conta', 'conta_destino')
            .distinct()
            .order_by('data_operacional', 'criado_em', 'pk')
        )

        saida_para_fora = Decimal('0.00')
        entrada_de_fora = Decimal('0.00')
        transferencias_externas: list[LancamentoFinanceiro] = []

        for lancamento in transferencias:
            origem_no_universo = lancamento.conta_id in selected_ids_set
            destino_no_universo = lancamento.conta_destino_id in selected_ids_set
            if origem_no_universo == destino_no_universo:
                continue

            transferencias_externas.append(lancamento)
            if origem_no_universo and not destino_no_universo:
                saida_para_fora += lancamento.valor
            elif destino_no_universo and not origem_no_universo:
                entrada_de_fora += lancamento.valor

        return {
            'quantidade': len(transferencias_externas),
            'saida_para_fora': saida_para_fora,
            'entrada_de_fora': entrada_de_fora,
            'tem_movimentacao_externa': bool(transferencias_externas),
            'mensagem': (
                'O relatorio principal consolida apenas as contas selecionadas. '
                'Transferencias entre esse universo e contas fora dele, como integralizacao ou outras contas nao operacionais, '
                'nao viram receita nem despesa, mas alteram o saldo consolidado das contas exibidas.'
            ) if transferencias_externas else '',
        }

    def _agrupar_por_campo(
        self,
        lancamentos: list[LancamentoFinanceiro],
        attr_name: str,
        fallback_label: str,
        label_key: str = 'label',
    ) -> tuple[list[dict[str, object]], Decimal]:
        agrupado: dict[str, Decimal] = {}
        for lancamento in lancamentos:
            related_obj = getattr(lancamento, attr_name)
            label = str(related_obj) if related_obj else fallback_label
            agrupado[label] = agrupado.get(label, Decimal('0.00')) + lancamento.valor

        itens = [
            {label_key: label, 'valor': valor}
            for label, valor in sorted(agrupado.items(), key=lambda item: item[0].lower())
        ]
        total = sum((item['valor'] for item in itens), Decimal('0.00'))
        return itens, total

    def _build_periodo_context(self) -> dict[str, object]:
        contas_disponiveis, selected_ids_raw, selected_ids = self._parse_contas()
        data_inicial_raw, data_final_raw, data_inicial, data_final, periodo_error = self._parse_periodo()
        mostrar_centro_custo = self._parse_checkbox('mostrar_centro_custo')
        exibir_transferencias = self._parse_checkbox('exibir_transferencias')
        mostrar_contas_zeradas = self._parse_checkbox('mostrar_contas_zeradas')
        filtros_relatorio_ativos = _request_possui_parametros_get(
            self.request,
            ('contas', 'data_inicial', 'data_final'),
        )
        opcoes_relatorio_ativas = mostrar_centro_custo or exibir_transferencias or mostrar_contas_zeradas
        contas_selecionadas = [conta for conta in contas_disponiveis if conta.id in selected_ids]
        todas_as_contas_selecionadas = len(selected_ids) == len(contas_disponiveis)
        contas_incluidas_label = (
            'Todas as contas'
            if todas_as_contas_selecionadas
            else ', '.join(conta.nome for conta in contas_selecionadas)
        )
        context: dict[str, object] = {
            'data_inicial': data_inicial_raw,
            'data_final': data_final_raw,
            'periodo_error': periodo_error,
            'contas_disponiveis': contas_disponiveis,
            'contas_selecionadas_ids': [str(conta_id) for conta_id in selected_ids],
            'contas_selecionadas': contas_selecionadas,
            'contas_incluidas_label': contas_incluidas_label,
            'quantidade_contas_selecionadas': len(contas_selecionadas),
            'mostrar_centro_custo': mostrar_centro_custo,
            'exibir_transferencias': exibir_transferencias,
            'mostrar_contas_zeradas': mostrar_contas_zeradas,
            'filtros_relatorio_ativos': filtros_relatorio_ativos,
            'opcoes_relatorio_ativas': opcoes_relatorio_ativas,
            'universo_contas_relatorio': {
                'todas_as_contas': todas_as_contas_selecionadas,
                'contas_label': contas_incluidas_label,
                'mostrar_nota': not todas_as_contas_selecionadas,
                'mensagem': (
                    'O saldo consolidado considera apenas as contas selecionadas neste relatorio. '
                    'Contas fora desse universo, como integralizacao ou outras contas nao operacionais, '
                    'nao entram como receita nem despesa; elas so afetam o saldo das contas exibidas quando houver transferencia entre os dois universos.'
                ) if not todas_as_contas_selecionadas else '',
            },
        }

        if not data_inicial or not data_final:
            return context

        dia_anterior = data_inicial - timedelta(days=1)
        composicao_inicial, saldo_inicial_consolidado = self._calcular_saldos_por_conta(dia_anterior, selected_ids)
        composicao_final, saldo_final_consolidado = self._calcular_saldos_por_conta(data_final, selected_ids)
        receitas, despesas, total_receitas, total_despesas = self._lancamentos_receitas_despesas(
            data_inicial,
            data_final,
            selected_ids,
        )
        resumo_transferencias_externas = self._resumir_transferencias_fora_do_universo(
            data_inicial,
            data_final,
            selected_ids,
        )
        saldo_final_reconciliado = (
            saldo_inicial_consolidado
            + total_receitas
            - total_despesas
            + resumo_transferencias_externas['entrada_de_fora']
            - resumo_transferencias_externas['saida_para_fora']
        )
        (
            transferencias_reais,
            total_transferencias_reais,
            total_transferencias_entrada_reais,
            total_transferencias_saida_reais,
        ) = self._lancamentos_transferencias(data_inicial, data_final, selected_ids)
        selected_ids_set = set(selected_ids)
        transferencias_visiveis = [
            lancamento
            for lancamento in transferencias_reais
            if (lancamento.conta_id in selected_ids_set) != (lancamento.conta_destino_id in selected_ids_set)
        ]
        total_transferencias_visiveis = sum(
            (lancamento.valor for lancamento in transferencias_visiveis),
            Decimal('0.00'),
        )
        total_transferencias_entrada_visiveis = sum(
            (
                lancamento.valor
                for lancamento in transferencias_visiveis
                if lancamento.conta_destino_id in selected_ids_set
            ),
            Decimal('0.00'),
        )
        total_transferencias_saida_visiveis = sum(
            (
                lancamento.valor
                for lancamento in transferencias_visiveis
                if lancamento.conta_id in selected_ids_set
            ),
            Decimal('0.00'),
        )
        (
            transferencias,
            total_transferencias,
            total_transferencias_entrada,
            total_transferencias_saida,
        ) = (
            (
                transferencias_visiveis,
                total_transferencias_visiveis,
                total_transferencias_entrada_visiveis,
                total_transferencias_saida_visiveis,
            )
            if exibir_transferencias
            else ([], Decimal('0.00'), Decimal('0.00'), Decimal('0.00'))
        )

        contas_com_movimentacao_ids = {
            lancamento.conta_id
            for lancamento in [*receitas, *despesas]
            if lancamento.conta_id
        }
        contas_com_movimentacao_ids.update(
            lancamento.conta_id
            for lancamento in transferencias_reais
            if lancamento.conta_id
        )
        contas_com_movimentacao_ids.update(
            lancamento.conta_destino_id
            for lancamento in transferencias_reais
            if lancamento.conta_destino_id
        )

        if not mostrar_contas_zeradas:
            saldos_iniciais_por_id = {
                item['conta'].id: item['saldo']
                for item in composicao_inicial
            }
            saldos_finais_por_id = {
                item['conta'].id: item['saldo']
                for item in composicao_final
            }

            def _manter_conta(item: dict[str, object]) -> bool:
                conta_id = item['conta'].id
                saldo_inicial = saldos_iniciais_por_id.get(conta_id, Decimal('0.00'))
                saldo_final = saldos_finais_por_id.get(conta_id, Decimal('0.00'))
                return (
                    saldo_inicial != Decimal('0.00')
                    or saldo_final != Decimal('0.00')
                    or conta_id in contas_com_movimentacao_ids
                )

            composicao_inicial = [item for item in composicao_inicial if _manter_conta(item)]
            composicao_final = [item for item in composicao_final if _manter_conta(item)]

        context.update(
            {
                'periodo_label': f'{data_inicial.strftime("%d/%m/%Y")} a {data_final.strftime("%d/%m/%Y")}',
                'saldo_inicial_consolidado': saldo_inicial_consolidado,
                'total_receitas_periodo': total_receitas,
                'total_despesas_periodo': total_despesas,
                'total_entradas_outras_contas': resumo_transferencias_externas['entrada_de_fora'],
                'total_saidas_outras_contas': resumo_transferencias_externas['saida_para_fora'],
                'saldo_final_reconciliado': saldo_final_reconciliado,
                'saldo_final_consolidado': saldo_final_consolidado,
                'saldo_periodo': saldo_final_consolidado - saldo_inicial_consolidado,
                'reconciliacao_saldo_consistente': saldo_final_reconciliado == saldo_final_consolidado,
                'composicao_inicial': composicao_inicial,
                'composicao_final': composicao_final,
                'receitas_periodo': receitas,
                'despesas_periodo': despesas,
                'transferencias_periodo': transferencias,
                'total_transferencias_periodo': total_transferencias,
                'total_transferencias_entrada': total_transferencias_entrada,
                'total_transferencias_saida': total_transferencias_saida,
                'resumo_transferencias_externas': resumo_transferencias_externas,
            }
        )

        receitas_por_categoria, total_receitas_por_categoria = self._agrupar_por_campo(
            receitas,
            'categoria',
            'Sem categoria',
            label_key='categoria',
        )
        despesas_por_categoria, total_despesas_por_categoria = self._agrupar_por_campo(
            despesas,
            'categoria',
            'Sem categoria',
            label_key='categoria',
        )
        despesas_por_centro_custo, total_despesas_por_centro_custo = self._agrupar_por_campo(
            despesas,
            'centro_custo',
            'Sem centro de custo',
        )
        context.update(
            {
                'receitas_por_categoria': receitas_por_categoria,
                'despesas_por_categoria': despesas_por_categoria,
                'total_receitas_por_categoria': total_receitas_por_categoria,
                'total_despesas_por_categoria': total_despesas_por_categoria,
                'despesas_por_centro_custo': despesas_por_centro_custo,
                'total_despesas_por_centro_custo': total_despesas_por_centro_custo,
                'existe_lancamento_sem_categoria': any(
                    lancamento.categoria_id is None for lancamento in [*receitas, *despesas]
                ),
                'existe_lancamento_sem_centro_custo': any(
                    lancamento.centro_custo_id is None for lancamento in despesas
                ),
            }
        )
        return context


class ResumoFinanceiroView(FinanceiroPeriodoMixin, TemplateView):
    permissao_requerida = 'financeiro.resumo_financeiro.visualizar'
    template_name = 'financeiro/resumo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Resumo do Periodo'
        context.update(self._build_periodo_context())
        return context


class PrestacaoContasFinanceiroView(FinanceiroPeriodoMixin, TemplateView):
    permissao_requerida = 'financeiro.prestacao_contas.visualizar'
    template_name = 'financeiro/prestacao_contas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Fechamento do periodo'
        context.update(self._build_periodo_context())
        return context


class EvolucaoCategoriasFinanceiroView(FinanceiroPermissaoMixin, TemplateView):
    permissao_requerida = 'financeiro.resumo_financeiro.visualizar'
    template_name = 'financeiro/evolucao_categorias.html'
    modo_padrao = 'categorias'
    escopo_padrao = 'categorias'
    leitura_padrao = 'separado'
    granularidade_padrao = 'meses'
    modos_disponiveis = (
        ('categorias', 'Evolucao de categorias selecionadas'),
        ('comparativo', 'Comparativo entrada x saida'),
    )
    escopos_disponiveis = (
        ('categorias', 'Categorias'),
        ('subcategorias', 'Subcategorias'),
    )
    leituras_disponiveis = (
        ('consolidado', 'Consolidado'),
        ('separado', 'Separado'),
    )
    granularidades_disponiveis = (
        ('dias', 'Dias'),
        ('meses', 'Meses'),
        ('trimestres', 'Trimestres'),
        ('anos', 'Anos'),
    )

    def _parse_periodo_campos(
        self,
        campo_inicial: str,
        campo_final: str,
        *,
        rotulo: str,
    ) -> tuple[str, str, date | None, date | None, str]:
        data_inicial_raw = (self.request.GET.get(campo_inicial) or '').strip()
        data_final_raw = (self.request.GET.get(campo_final) or '').strip()
        data_inicial = None
        data_final = None
        periodo_error = ''

        if data_inicial_raw:
            try:
                data_inicial = date.fromisoformat(data_inicial_raw)
            except ValueError:
                periodo_error = f'Informe uma data inicial valida para {rotulo}.'

        if data_final_raw and not periodo_error:
            try:
                data_final = date.fromisoformat(data_final_raw)
            except ValueError:
                periodo_error = f'Informe uma data final valida para {rotulo}.'

        if not periodo_error and ((data_inicial and not data_final) or (data_final and not data_inicial)):
            periodo_error = f'Informe data inicial e data final para {rotulo}.'

        if not periodo_error and data_inicial and data_final and data_final < data_inicial:
            periodo_error = f'A data final de {rotulo} precisa ser igual ou posterior a data inicial.'

        return data_inicial_raw, data_final_raw, data_inicial, data_final, periodo_error

    def _parse_periodo(self) -> tuple[str, str, date | None, date | None, str]:
        return self._parse_periodo_campos(
            'data_inicial',
            'data_final',
            rotulo='o periodo principal',
        )

    def _parse_periodos_comparacao(self) -> dict[str, object]:
        data_inicial_comparativo_raw = (self.request.GET.get('data_inicial_comparativo') or '').strip()
        data_final_comparativo_raw = (self.request.GET.get('data_final_comparativo') or '').strip()
        if not data_inicial_comparativo_raw and not data_final_comparativo_raw:
            data_inicial_comparativo_raw = (self.request.GET.get('data_inicial_b') or '').strip()
            data_final_comparativo_raw = (self.request.GET.get('data_final_b') or '').strip()

        data_inicial_comparativo = None
        data_final_comparativo = None
        periodo_comparativo_error = ''

        if data_inicial_comparativo_raw:
            try:
                data_inicial_comparativo = date.fromisoformat(data_inicial_comparativo_raw)
            except ValueError:
                periodo_comparativo_error = 'Informe uma data inicial valida para o periodo comparativo.'

        if data_final_comparativo_raw and not periodo_comparativo_error:
            try:
                data_final_comparativo = date.fromisoformat(data_final_comparativo_raw)
            except ValueError:
                periodo_comparativo_error = 'Informe uma data final valida para o periodo comparativo.'

        if (
            not periodo_comparativo_error
            and (
                (data_inicial_comparativo and not data_final_comparativo)
                or (data_final_comparativo and not data_inicial_comparativo)
            )
        ):
            periodo_comparativo_error = 'Informe data inicial e data final para o periodo comparativo.'

        if (
            not periodo_comparativo_error
            and data_inicial_comparativo
            and data_final_comparativo
            and data_final_comparativo < data_inicial_comparativo
        ):
            periodo_comparativo_error = 'A data final do periodo comparativo precisa ser igual ou posterior a data inicial.'

        comparacao_solicitada = bool(data_inicial_comparativo_raw or data_final_comparativo_raw)
        return {
            'data_inicial_comparativo': data_inicial_comparativo_raw,
            'data_final_comparativo': data_final_comparativo_raw,
            'periodo_comparativo_resolvido': (data_inicial_comparativo, data_final_comparativo),
            'periodo_comparativo_label': (
                _formatar_periodo_comparacao(data_inicial_comparativo, data_final_comparativo)
                if data_inicial_comparativo and data_final_comparativo
                else ''
            ),
            'comparacao_solicitada': comparacao_solicitada,
            'periodo_error': periodo_comparativo_error if comparacao_solicitada else '',
        }

    def _parse_contas(self) -> tuple[list[ContaFinanceira], list[str], list[int]]:
        contas_disponiveis = _ordenar_itens_insensivel(
            ContaFinanceira.objects.all(),
            'nome',
        )
        selected_ids_raw = [valor for valor in self.request.GET.getlist('contas') if valor.strip()]
        selected_ids: list[int] = []
        for valor in selected_ids_raw:
            try:
                selected_ids.append(int(valor))
            except (TypeError, ValueError):
                continue
        if not selected_ids:
            selected_ids = [conta.id for conta in contas_disponiveis]
        return contas_disponiveis, selected_ids_raw, selected_ids

    def _parse_escopo(self) -> tuple[str, str]:
        escopo = (self.request.GET.get('escopo') or self.escopo_padrao).strip()
        if escopo not in {item[0] for item in self.escopos_disponiveis}:
            escopo = self.escopo_padrao
        return escopo, dict(self.escopos_disponiveis).get(escopo, self.escopo_padrao)

    def _parse_leitura(self) -> tuple[str, str]:
        leitura = (self.request.GET.get('leitura') or self.leitura_padrao).strip()
        if leitura not in {item[0] for item in self.leituras_disponiveis}:
            leitura = self.leitura_padrao
        return leitura, dict(self.leituras_disponiveis).get(leitura, self.leitura_padrao)

    def _parse_granularidade(self) -> tuple[str, str]:
        granularidade = (self.request.GET.get('granularidade') or self.granularidade_padrao).strip()
        if granularidade not in {item[0] for item in self.granularidades_disponiveis}:
            granularidade = self.granularidade_padrao
        return granularidade, dict(self.granularidades_disponiveis).get(granularidade, self.granularidade_padrao)

    def _parse_mostrar_valores(self) -> bool:
        valor = (self.request.GET.get('mostrar_valores') or '').strip().lower()
        return valor in {'1', 'true', 'sim', 'on'}

    def _build_itens_disponiveis(self, escopo: str) -> list[dict[str, object]]:
        if escopo == 'categorias':
            categorias_pai = _ordenar_itens_insensivel(
                CategoriaFinanceira.objects.filter(categoria_pai__isnull=True),
                'nome',
                'tipo',
            )
            filhos = _ordenar_itens_insensivel(
                CategoriaFinanceira.objects.filter(categoria_pai_id__in=[categoria.id for categoria in categorias_pai])
                .select_related('categoria_pai'),
                'categoria_pai__nome',
                'nome',
                'tipo',
            )
            filhos_por_pai: dict[int, list[CategoriaFinanceira]] = {}
            for filho in filhos:
                filhos_por_pai.setdefault(filho.categoria_pai_id, []).append(filho)

            return [
                {
                    'id': categoria.id,
                    'objeto': categoria,
                    'label': categoria.nome,
                    'display_label': categoria.nome,
                    'tipo': categoria.tipo,
                    'tipo_label': categoria.get_tipo_display(),
                    'categoria_ids': [filho.id for filho in filhos_por_pai.get(categoria.id, [])],
                    'search_text': f"{categoria.nome} {categoria.get_tipo_display()}",
                    'is_parent': True,
                    'parent_name': '',
                    'hint': f"Categoria {categoria.get_tipo_display().lower()}",
                    'hierarquia_label': categoria.nome,
                }
                for categoria in categorias_pai
            ]

        subcategorias = _ordenar_itens_insensivel(
            CategoriaFinanceira.objects.filter(categoria_pai__isnull=False)
            .select_related('categoria_pai'),
            'nome',
            'categoria_pai__nome',
            'tipo',
        )
        nomes_normalizados: dict[str, int] = {}
        for categoria in subcategorias:
            chave_nome = _texto_ordenacao_insensivel(categoria.nome)
            nomes_normalizados[chave_nome] = nomes_normalizados.get(chave_nome, 0) + 1

        return [
            {
                'id': categoria.id,
                'objeto': categoria,
                'label': _label_categoria_evolucao(categoria),
                'display_label': (
                    f'{categoria.nome} ({categoria.categoria_pai.nome})'
                    if nomes_normalizados.get(_texto_ordenacao_insensivel(categoria.nome), 0) > 1
                    else categoria.nome
                ),
                'tipo': categoria.tipo,
                'tipo_label': categoria.get_tipo_display(),
                'categoria_ids': [categoria.id],
                'search_text': (
                    f"{categoria.categoria_pai.nome} {categoria.nome} "
                    f"{categoria.get_tipo_display()} {_label_categoria_evolucao(categoria)}"
                ),
                'is_parent': False,
                'parent_name': categoria.categoria_pai.nome,
                'hint': f"{categoria.categoria_pai.nome} • {categoria.get_tipo_display()}",
                'hierarquia_label': _label_categoria_evolucao(categoria),
                'sort_key': categoria.nome,
            }
            for categoria in subcategorias
        ]

    def _parse_itens_analiticos(self, escopo: str) -> tuple[list[dict[str, object]], list[str], list[dict[str, object]]]:
        itens_disponiveis = self._build_itens_disponiveis(escopo)
        itens_por_id = {item['id']: item for item in itens_disponiveis}
        selecionadas_raw = [valor for valor in self.request.GET.getlist('categorias') if valor.strip()]
        itens_selecionados: list[dict[str, object]] = []
        for valor in selecionadas_raw:
            try:
                item_id = int(valor)
            except (TypeError, ValueError):
                continue
            item = itens_por_id.get(item_id)
            if item:
                itens_selecionados.append(item)
        return itens_disponiveis, selecionadas_raw, itens_selecionados

    def _rotulo_serie_consolidada(self, itens: list[dict[str, object]], escopo: str) -> str:
        prefixo = 'Categorias' if escopo == 'categorias' else 'Subcategorias'
        nomes = [item['display_label'] for item in itens]
        sufixo = _rotulo_curto_lista_nomes(nomes)
        if sufixo:
            return f'{prefixo}: {sufixo}'
        return f'{prefixo} selecionadas'

    def _rotulo_serie_comparativa_consolidada(self, itens: list[dict[str, object]], tipo: str) -> str:
        prefixo = 'Receitas selecionadas' if tipo == LancamentoFinanceiro.TipoLancamento.RECEITA else 'Despesas selecionadas'
        nomes = [item['display_label'] for item in itens]
        sufixo = _rotulo_curto_lista_nomes(nomes)
        if sufixo:
            return f'{prefixo}: {sufixo}'
        return prefixo

    def _montar_rotulos_curtos_comparacao(self, itens: list[dict[str, object]]) -> dict[int, str]:
        contagem_nomes: dict[str, int] = {}
        for item in itens:
            objeto = item.get('objeto')
            nome_curto = getattr(objeto, 'nome', item.get('display_label') or item.get('label') or '')
            chave = _texto_ordenacao_insensivel(nome_curto)
            contagem_nomes[chave] = contagem_nomes.get(chave, 0) + 1

        rotulos: dict[int, str] = {}
        for item in itens:
            objeto = item.get('objeto')
            nome_curto = getattr(objeto, 'nome', item.get('display_label') or item.get('label') or '')
            chave = _texto_ordenacao_insensivel(nome_curto)
            nome_exibido = item.get('label') if contagem_nomes.get(chave, 0) > 1 else nome_curto
            rotulos[int(item['id'])] = str(nome_exibido)
        return rotulos

    def _descricao_grafico(
        self,
        *,
        modo: str,
        leitura: str,
        granularidade: str,
    ) -> str:
        leitura_temporal = _descricao_leitura_temporal_evolucao(granularidade)
        if modo == 'comparativo':
            return (
                f'Compara no mesmo eixo temporal as categorias selecionadas em {leitura_temporal}, preservando nomes reais e a natureza de entrada ou saida de cada serie.'
                if leitura == 'separado'
                else f'Compara no mesmo eixo temporal, em {leitura_temporal}, o consolidado das categorias de entrada selecionadas e o consolidado das categorias de saida selecionadas.'
            )
        return (
            f'Exibe uma serie por item selecionado em {leitura_temporal}, mantendo a leitura visual por valor absoluto de cada lancamento.'
            if leitura == 'separado'
            else f'Soma os itens selecionados em {leitura_temporal}, mantendo a leitura visual por valor absoluto dos lancamentos.'
        )

    def _build_contexto_base(self) -> dict[str, object]:
        contas_disponiveis, selected_ids_raw, selected_ids = self._parse_contas()
        modo = (self.request.GET.get('modo') or self.modo_padrao).strip()
        if modo not in {item[0] for item in self.modos_disponiveis}:
            modo = self.modo_padrao
        modo_label = dict(self.modos_disponiveis).get(modo, self.modo_padrao)
        escopo, escopo_label = self._parse_escopo()
        leitura, leitura_label = self._parse_leitura()
        granularidade, granularidade_label = self._parse_granularidade()
        mostrar_valores = self._parse_mostrar_valores()
        itens_disponiveis, categorias_raw, itens_selecionados = self._parse_itens_analiticos(escopo)
        itens_disponiveis_categorias = self._build_itens_disponiveis('categorias')
        itens_disponiveis_subcategorias = self._build_itens_disponiveis('subcategorias')
        data_inicial_raw, data_final_raw, data_inicial, data_final, periodo_error = self._parse_periodo()
        periodos_comparacao = self._parse_periodos_comparacao()
        comparacao_periodos_reorganizada = False
        if (
            not periodo_error
            and not periodos_comparacao['periodo_error']
            and data_inicial
            and data_final
            and periodos_comparacao['periodo_comparativo_resolvido'][0]
            and periodos_comparacao['periodo_comparativo_resolvido'][1]
        ):
            periodo_principal_resolvido = (data_inicial, data_final)
            periodo_comparativo_resolvido = periodos_comparacao['periodo_comparativo_resolvido']
            if periodo_comparativo_resolvido < periodo_principal_resolvido:
                data_inicial, data_final = periodo_comparativo_resolvido
                data_inicial_raw = data_inicial.isoformat()
                data_final_raw = data_final.isoformat()
                periodos_comparacao['data_inicial_comparativo'] = periodo_principal_resolvido[0].isoformat()
                periodos_comparacao['data_final_comparativo'] = periodo_principal_resolvido[1].isoformat()
                periodos_comparacao['periodo_comparativo_resolvido'] = periodo_principal_resolvido
                periodos_comparacao['periodo_comparativo_label'] = _formatar_periodo_comparacao(
                    periodo_principal_resolvido[0],
                    periodo_principal_resolvido[1],
                )
                comparacao_periodos_reorganizada = True
        comparacao_solicitada = bool(periodos_comparacao['comparacao_solicitada'])

        filtros_relatorio_ativos = _request_possui_parametros_get(
            self.request,
            (
                'contas',
                'categorias',
                'data_inicial',
                'data_final',
                'data_inicial_comparativo',
                'data_final_comparativo',
                'data_inicial_b',
                'data_final_b',
                'modo',
                'escopo',
                'leitura',
                'granularidade',
                'mostrar_valores',
            ),
        )
        contas_selecionadas = [conta for conta in contas_disponiveis if conta.id in selected_ids]
        todas_as_contas_selecionadas = len(selected_ids) == len(contas_disponiveis)
        itens_label = ', '.join(item['label'] for item in itens_selecionados)
        itens_resumo = _rotulo_curto_lista_nomes([item['label'] for item in itens_selecionados], limite=3)

        return {
            'page_title': 'Evolucao por categorias',
            'modo': modo,
            'modo_label': modo_label,
            'modos_disponiveis': self.modos_disponiveis,
            'escopo': escopo,
            'escopo_label': escopo_label,
            'escopos_disponiveis': self.escopos_disponiveis,
            'leitura': leitura,
            'leitura_label': leitura_label,
            'leituras_disponiveis': self.leituras_disponiveis,
            'granularidade': granularidade,
            'granularidade_label': granularidade_label,
            'granularidades_disponiveis': self.granularidades_disponiveis,
            'mostrar_valores': mostrar_valores,
            'contas_disponiveis': contas_disponiveis,
            'contas_selecionadas_ids': [str(conta_id) for conta_id in selected_ids],
            'quantidade_contas_selecionadas': len(contas_selecionadas),
            'contas_incluidas_label': (
                'Todas as contas'
                if todas_as_contas_selecionadas
                else ', '.join(conta.nome for conta in contas_selecionadas)
            ),
            'categorias_disponiveis': itens_disponiveis,
            'categorias_disponiveis_categorias': itens_disponiveis_categorias,
            'categorias_disponiveis_subcategorias': itens_disponiveis_subcategorias,
            'categorias_selecionadas_ids': categorias_raw,
            'categorias_selecionadas': itens_selecionados,
            'categorias_selecionadas_label': itens_label,
            'categorias_selecionadas_resumo': itens_resumo,
            'quantidade_itens_selecionados': len(itens_selecionados),
            'data_inicial': data_inicial_raw,
            'data_final': data_final_raw,
            'data_inicial_comparativo': periodos_comparacao['data_inicial_comparativo'],
            'data_final_comparativo': periodos_comparacao['data_final_comparativo'],
            'periodo_principal_label': (
                f'{data_inicial.strftime("%d/%m/%Y")} a {data_final.strftime("%d/%m/%Y")}'
                if data_inicial and data_final
                else ''
            ),
            'periodo_comparativo_label': periodos_comparacao['periodo_comparativo_label'],
            'periodo_error': periodos_comparacao['periodo_error'] or periodo_error,
            'filtros_relatorio_ativos': filtros_relatorio_ativos,
            'periodo_resolvido': (data_inicial, data_final),
            'periodo_comparativo_resolvido': periodos_comparacao['periodo_comparativo_resolvido'],
            'modo_comparacao_periodos': comparacao_solicitada,
            'comparacao_solicitada': comparacao_solicitada,
            'comparacao_periodos_reorganizada': comparacao_periodos_reorganizada,
            'comparacao_periodos_reorganizada_mensagem': (
                'Os periodos foram reorganizados automaticamente para manter a leitura cronologica anterior -> posterior.'
                if comparacao_periodos_reorganizada
                else ''
            ),
        }

    def _montar_series(
        self,
        itens_selecionados: list[dict[str, object]],
        *,
        escopo: str,
        leitura: str,
        modo: str,
    ) -> tuple[list[dict[str, object]], list[str]]:
        if not itens_selecionados:
            return [], []

        if any(not item['categoria_ids'] for item in itens_selecionados):
            return [], ['As categorias selecionadas nao possuem subcategorias lancaveis para compor o relatorio.']

        if modo == 'comparativo':
            if leitura == 'consolidado':
                series = []
                for tipo, cor in (
                    (LancamentoFinanceiro.TipoLancamento.RECEITA, '#1f5fbf'),
                    (LancamentoFinanceiro.TipoLancamento.DESPESA, '#b73a32'),
                ):
                    itens_tipo = [item for item in itens_selecionados if item['tipo'] == tipo]
                    if not itens_tipo:
                        continue
                    categoria_ids = sorted({categoria_id for item in itens_tipo for categoria_id in item['categoria_ids']})
                    series.append(
                        {
                            'chave': f'comparativo_{tipo}',
                            'label': self._rotulo_serie_comparativa_consolidada(itens_tipo, tipo),
                            'tipo': tipo,
                            'cor': cor,
                            'categoria_ids': categoria_ids,
                            'categoria_ids_set': set(categoria_ids),
                            'tipos_permitidos': {tipo},
                            'valores': [],
                        }
                    )
                return series, []

            series = []
            rotulos_curtos = self._montar_rotulos_curtos_comparacao(itens_selecionados)
            for indice, item in enumerate(itens_selecionados):
                prefixo = 'Entrada' if item['tipo'] == LancamentoFinanceiro.TipoLancamento.RECEITA else 'Saida'
                series.append(
                    {
                        'chave': f"comparativo_item_{item['id']}",
                        'label': f"{prefixo} - {item['label']}",
                        'label_grafico': rotulos_curtos.get(int(item['id']), item['label']),
                        'tipo': item['tipo'],
                        'cor': EVOLUCAO_CATEGORIAS_SERIES_CORES[indice % len(EVOLUCAO_CATEGORIAS_SERIES_CORES)],
                        'categoria_ids': item['categoria_ids'],
                        'categoria_ids_set': set(item['categoria_ids']),
                        'tipos_permitidos': {item['tipo']},
                        'valores': [],
                    }
                )
            return series, []

        if leitura == 'consolidado':
            categoria_ids = sorted({categoria_id for item in itens_selecionados for categoria_id in item['categoria_ids']})
            series = [
                {
                    'chave': f'consolidado_{escopo}',
                    'label': self._rotulo_serie_consolidada(itens_selecionados, escopo),
                    'tipo': 'misto',
                    'cor': '#1f5fbf',
                    'categoria_ids': categoria_ids,
                    'categoria_ids_set': set(categoria_ids),
                    'tipos_permitidos': {
                        LancamentoFinanceiro.TipoLancamento.RECEITA,
                        LancamentoFinanceiro.TipoLancamento.DESPESA,
                    },
                    'valores': [],
                }
            ]
            return series, []

        series = []
        rotulos_curtos = self._montar_rotulos_curtos_comparacao(itens_selecionados)
        for indice, item in enumerate(itens_selecionados):
            series.append(
                {
                    'chave': f"item_{item['id']}",
                    'label': item['label'],
                    'label_grafico': rotulos_curtos.get(int(item['id']), item['label']),
                    'tipo': item['tipo'],
                    'cor': EVOLUCAO_CATEGORIAS_SERIES_CORES[indice % len(EVOLUCAO_CATEGORIAS_SERIES_CORES)],
                    'categoria_ids': item['categoria_ids'],
                    'categoria_ids_set': set(item['categoria_ids']),
                    'tipos_permitidos': {
                        LancamentoFinanceiro.TipoLancamento.RECEITA,
                        LancamentoFinanceiro.TipoLancamento.DESPESA,
                    },
                    'valores': [],
                }
            )
        return series, []

    def _montar_relatorio_periodo(
        self,
        data_inicial: date,
        data_final: date,
        selected_ids: list[int],
        itens_selecionados: list[dict[str, object]],
        *,
        escopo: str,
        leitura: str,
        modo_series: str,
        granularidade: str,
        mostrar_valores: bool,
    ) -> dict[str, object]:
        series, erros = self._montar_series(
            itens_selecionados,
            escopo=escopo,
            leitura=leitura,
            modo=modo_series,
        )
        if erros:
            return {'erro': erros[0]}

        categorias_ids_consideradas = sorted(
            {
                categoria_id
                for serie in series
                for categoria_id in serie['categoria_ids']
            }
        )
        if not categorias_ids_consideradas:
            return {
                'erro': 'As categorias selecionadas nao possuem subcategorias lancaveis para compor o relatorio.',
            }

        lancamentos = list(
            LancamentoFinanceiro.objects.annotate(
                data_operacional=Coalesce('data_pagamento', 'data_competencia')
            )
            .filter(
                data_operacional__gte=data_inicial,
                data_operacional__lte=data_final,
                categoria_id__in=categorias_ids_consideradas,
                conta_id__in=selected_ids,
                tipo__in=(
                    LancamentoFinanceiro.TipoLancamento.RECEITA,
                    LancamentoFinanceiro.TipoLancamento.DESPESA,
                ),
            )
            .select_related('categoria', 'categoria__categoria_pai', 'conta')
            .order_by('data_operacional', 'pk')
        )

        buckets = _iterar_buckets_periodo(data_inicial, data_final, granularidade)
        labels = [str(item['rotulo']) for item in buckets]
        valores_por_serie = [
            [Decimal('0.00') for _ in buckets]
            for _ in series
        ]
        indice_bucket = {str(item['chave']): idx for idx, item in enumerate(buckets)}

        total_receitas = Decimal('0.00')
        total_despesas = Decimal('0.00')
        total_quitado = Decimal('0.00')
        total_aberto = Decimal('0.00')

        for lancamento in lancamentos:
            chave_bucket = _chave_bucket_data_operacional(lancamento.data_operacional, granularidade)
            indice_bucket_lancamento = indice_bucket.get(chave_bucket)
            if indice_bucket_lancamento is None:
                continue

            indice_serie = None
            for posicao, serie in enumerate(series):
                if (
                    lancamento.categoria_id in serie['categoria_ids_set']
                    and lancamento.tipo in serie['tipos_permitidos']
                ):
                    indice_serie = posicao
                    break

            if indice_serie is None:
                continue

            valor_visual = abs(lancamento.valor or Decimal('0.00'))
            valores_por_serie[indice_serie][indice_bucket_lancamento] += valor_visual

            if lancamento.tipo == LancamentoFinanceiro.TipoLancamento.RECEITA:
                total_receitas += lancamento.valor
            else:
                total_despesas += lancamento.valor

            if lancamento.status == LancamentoFinanceiro.StatusLancamento.QUITADO:
                total_quitado += lancamento.valor
            elif lancamento.status == LancamentoFinanceiro.StatusLancamento.ABERTO:
                total_aberto += lancamento.valor

        for indice, serie in enumerate(series):
            serie['valores'] = valores_por_serie[indice]
            serie['total'] = sum(valores_por_serie[indice], Decimal('0.00'))
            serie['total_formatado'] = _formatar_moeda_brl(serie['total'])
            serie['tipo_css'] = 'misto'
            if serie['tipo'] == LancamentoFinanceiro.TipoLancamento.RECEITA:
                serie['tipo_css'] = 'receita'
            elif serie['tipo'] == LancamentoFinanceiro.TipoLancamento.DESPESA:
                serie['tipo_css'] = 'despesa'

        linhas_tabela = []
        for indice, bucket in enumerate(buckets):
            valores_linha = [serie['valores'][indice] for serie in series]
            saldo_linha = Decimal('0.00')
            for posicao, valor in enumerate(valores_linha):
                tipo_serie = series[posicao]['tipo']
                if tipo_serie == LancamentoFinanceiro.TipoLancamento.DESPESA:
                    saldo_linha -= valor
                else:
                    saldo_linha += valor
            linhas_tabela.append(
                {
                    'mes_label': str(bucket['rotulo']),
                    'valores': [
                        {
                            'valor': valor,
                            'valor_formatado': _formatar_moeda_brl(valor),
                            'tipo': series[posicao]['tipo'],
                        }
                        for posicao, valor in enumerate(valores_linha)
                    ],
                    'saldo_liquido': saldo_linha,
                    'saldo_liquido_formatado': _formatar_moeda_brl(abs(saldo_linha)),
                }
            )

        grafico = _montar_contexto_svg_evolucao(labels, series, mostrar_valores=mostrar_valores)
        saldo_liquido = total_receitas - total_despesas

        return {
            'series': series,
            'grafico': grafico,
            'labels': labels,
            'linhas_tabela': linhas_tabela,
            'quantidade_lancamentos': len(lancamentos),
            'quantidade_buckets': len(buckets),
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'total_quitado': total_quitado,
            'total_aberto': total_aberto,
            'saldo_liquido': saldo_liquido,
            'total_receitas_formatado': _formatar_moeda_brl(total_receitas),
            'total_despesas_formatado': _formatar_moeda_brl(total_despesas),
            'total_quitado_formatado': _formatar_moeda_brl(total_quitado),
            'total_aberto_formatado': _formatar_moeda_brl(total_aberto),
            'saldo_liquido_formatado': _formatar_moeda_brl(saldo_liquido),
            'tem_dados': bool(lancamentos),
            'periodo_label': f'{data_inicial.strftime("%d/%m/%Y")} a {data_final.strftime("%d/%m/%Y")}',
            'granularidade_grafico_label': dict(self.granularidades_disponiveis).get(granularidade, granularidade),
        }

    def _montar_grafico_comparativo_consolidado(
        self,
        *,
        relatorio_principal: dict[str, object],
        relatorio_comparativo: dict[str, object],
        periodo_principal_label: str,
        periodo_comparativo_label: str,
        mostrar_valores: bool,
    ) -> dict[str, object]:
        labels_principal = list(relatorio_principal.get('labels') or [])
        labels_comparativo = list(relatorio_comparativo.get('labels') or [])
        quantidade_labels = max(len(labels_principal), len(labels_comparativo))

        labels = []
        usa_alinhamento_relativo = False
        for indice in range(quantidade_labels):
            label_principal = labels_principal[indice] if indice < len(labels_principal) else ''
            label_comparativo = labels_comparativo[indice] if indice < len(labels_comparativo) else ''
            if label_principal and label_comparativo and label_principal != label_comparativo:
                usa_alinhamento_relativo = True
            labels.append(label_principal or label_comparativo or str(indice + 1))

        valores_principal = _somar_valores_series(relatorio_principal.get('series') or [])
        valores_comparativo = _somar_valores_series(relatorio_comparativo.get('series') or [])
        if len(valores_principal) < quantidade_labels:
            valores_principal.extend([Decimal('0.00')] * (quantidade_labels - len(valores_principal)))
        if len(valores_comparativo) < quantidade_labels:
            valores_comparativo.extend([Decimal('0.00')] * (quantidade_labels - len(valores_comparativo)))

        mostrar_valores_grafico = bool(
            mostrar_valores
            and quantidade_labels <= 12
        )
        series = [
            {
                'label': periodo_principal_label,
                'cor': '#1f5fbf',
                'tipo': 'misto',
                'valores': valores_principal,
            },
            {
                'label': periodo_comparativo_label,
                'cor': '#c97316',
                'tipo': 'misto',
                'valores': valores_comparativo,
            },
        ]

        grafico = _montar_contexto_svg_evolucao(labels, series, mostrar_valores=mostrar_valores_grafico)
        rotulos_suprimidos_por_colisao = False
        if mostrar_valores_grafico and grafico.get('tem_dados'):
            rotulos_suprimidos_por_colisao = self._ajustar_rotulos_comparativo_consolidado(grafico)

        return {
            'grafico': grafico,
            'series': [{'label': serie['label'], 'cor': serie['cor']} for serie in series],
            'usa_alinhamento_relativo': usa_alinhamento_relativo,
            'rotulos_suprimidos': mostrar_valores and (
                not mostrar_valores_grafico or rotulos_suprimidos_por_colisao
            ),
        }

    @staticmethod
    def _reposicionar_rotulo_comparativo(ponto: dict[str, object], y_rotulo: float, posicao: str) -> None:
        ponto['rotulo_posicao'] = posicao
        ponto['rotulo_y_float'] = y_rotulo
        ponto['linha_rotulo_y_float'] = y_rotulo + 5.0 if posicao == 'acima' else y_rotulo - 12.0
        ponto['rotulo_y_svg'] = f'{y_rotulo:.2f}'
        ponto['linha_rotulo_y_svg'] = f"{ponto['linha_rotulo_y_float']:.2f}"

    def _ajustar_rotulos_comparativo_consolidado(self, grafico: dict[str, object]) -> bool:
        series = grafico.get('series') or []
        if len(series) < 2:
            return False

        pontos_principal = series[0].get('pontos') or []
        pontos_comparativo = series[1].get('pontos') or []
        quantidade_pontos = min(len(pontos_principal), len(pontos_comparativo))
        limite_superior = 16.0
        limite_inferior = float(grafico.get('eixo_label_y') or grafico.get('altura') or 384) - 20.0
        rotulo_suprimido = False

        for indice in range(quantidade_pontos):
            ponto_principal = pontos_principal[indice]
            ponto_comparativo = pontos_comparativo[indice]
            if not ponto_principal.get('mostrar_rotulo') and not ponto_comparativo.get('mostrar_rotulo'):
                continue

            y_principal = float(ponto_principal.get('y_float') or 0.0)
            y_comparativo = float(ponto_comparativo.get('y_float') or 0.0)
            valores_proximos = abs(y_principal - y_comparativo) < 26.0
            offset_principal = 30.0 if valores_proximos else 20.0
            offset_comparativo = 36.0 if valores_proximos else 26.0

            if ponto_principal.get('mostrar_rotulo'):
                rotulo_principal_y = max(limite_superior, y_principal - offset_principal)
                self._reposicionar_rotulo_comparativo(ponto_principal, rotulo_principal_y, 'acima')

            if ponto_comparativo.get('mostrar_rotulo'):
                rotulo_comparativo_y = min(limite_inferior, y_comparativo + offset_comparativo)
                if (
                    ponto_principal.get('mostrar_rotulo')
                    and abs(rotulo_comparativo_y - float(ponto_principal['rotulo_y_float'])) < 18.0
                ):
                    ponto_comparativo['mostrar_rotulo'] = False
                    rotulo_suprimido = True
                    continue
                self._reposicionar_rotulo_comparativo(ponto_comparativo, rotulo_comparativo_y, 'abaixo')

        return rotulo_suprimido

    def _montar_grafico_resumo_comparacao_detalhada(
        self,
        *,
        linhas_comparacao: list[dict[str, object]],
        periodo_principal_label: str,
        periodo_comparativo_label: str,
    ) -> dict[str, object]:
        limite_itens = 8
        linhas_ordenadas = sorted(
            linhas_comparacao,
            key=lambda linha: (
                -abs(linha.get('diferenca_absoluta') or Decimal('0.00')),
                -(
                    abs(linha.get('valor_a_absoluto') or Decimal('0.00'))
                    + abs(linha.get('valor_b_absoluto') or Decimal('0.00'))
                ),
                _texto_ordenacao_insensivel(linha.get('label_grafico') or linha.get('label') or ''),
            ),
        )
        linhas_exibidas = linhas_ordenadas[:limite_itens]
        maior_valor = max(
            [
                abs(linha.get('valor_a_absoluto') or Decimal('0.00'))
                for linha in linhas_exibidas
            ]
            + [
                abs(linha.get('valor_b_absoluto') or Decimal('0.00'))
                for linha in linhas_exibidas
            ],
            default=Decimal('0.00'),
        )

        def _largura_barra(valor: Decimal) -> str:
            valor = abs(valor or Decimal('0.00'))
            if maior_valor <= Decimal('0.00') or valor <= Decimal('0.00'):
                return '0'
            percentual = (valor / maior_valor) * Decimal('100')
            if percentual < Decimal('6.0'):
                percentual = Decimal('6.0')
            return str(percentual.quantize(Decimal('0.1'))).replace(',', '.')

        return {
            'tem_dados': bool(linhas_exibidas) and maior_valor > Decimal('0.00'),
            'periodo_principal_label': periodo_principal_label,
            'periodo_comparativo_label': periodo_comparativo_label,
            'quantidade_total': len(linhas_comparacao),
            'quantidade_exibida': len(linhas_exibidas),
            'tem_itens_ocultos': len(linhas_comparacao) > limite_itens,
            'itens': [
                {
                    'label': linha.get('label_grafico') or linha['label'],
                    'natureza_css': (
                        'is-despesa'
                        if linha.get('tipo') == LancamentoFinanceiro.TipoLancamento.DESPESA
                        else 'is-receita'
                    ),
                    'valor_principal_exibido_formatado': linha['valor_a_exibido_formatado'],
                    'valor_comparativo_exibido_formatado': linha['valor_b_exibido_formatado'],
                    'diferenca_absoluta_formatada': linha['diferenca_absoluta_formatada'],
                    'largura_principal': _largura_barra(linha.get('valor_a_absoluto') or Decimal('0.00')),
                    'largura_comparativo': _largura_barra(linha.get('valor_b_absoluto') or Decimal('0.00')),
                }
                for linha in linhas_exibidas
            ],
        }

    def _valor_exibicao_comparacao(self, valor: Decimal, tipo: str) -> Decimal:
        valor = valor or Decimal('0.00')
        if tipo == LancamentoFinanceiro.TipoLancamento.DESPESA:
            return -abs(valor)
        return valor

    def _classe_semantica_comparacao(self, tipo: str, valor_principal: Decimal, valor_comparativo: Decimal) -> str:
        valor_principal = abs(valor_principal or Decimal('0.00'))
        valor_comparativo = abs(valor_comparativo or Decimal('0.00'))
        if valor_comparativo == valor_principal:
            return ''
        if tipo == LancamentoFinanceiro.TipoLancamento.DESPESA:
            return 'is-receita' if valor_comparativo < valor_principal else 'is-despesa'
        return 'is-receita' if valor_comparativo > valor_principal else 'is-despesa'

    def _classe_semantica_total_comparacao(self, valor_principal: Decimal, valor_comparativo: Decimal) -> str:
        valor_principal = valor_principal or Decimal('0.00')
        valor_comparativo = valor_comparativo or Decimal('0.00')
        if valor_comparativo == valor_principal:
            return ''
        return 'is-receita' if valor_comparativo > valor_principal else 'is-despesa'

    def _montar_filtros_humanos(
        self,
        *,
        escopo: str,
        leitura: str,
        modo: str,
        granularidade: str,
        mostrar_valores: bool,
        itens_selecionados: list[dict[str, object]],
        selected_ids: list[int],
        periodo_label: str = '',
        periodo_principal_label: str = '',
        periodo_comparativo_label: str = '',
    ) -> list[str]:
        filtros_humanos = []
        if periodo_principal_label and periodo_comparativo_label:
            filtros_humanos.append(f'Comparacao: {periodo_principal_label} x {periodo_comparativo_label}')
        elif periodo_principal_label:
            filtros_humanos.append(f'Periodo principal: {periodo_principal_label}')
        elif periodo_label:
            filtros_humanos.append(f'Periodo principal: {periodo_label}')

        filtros_humanos.extend(
            [
                f"Escopo: {'Categorias' if escopo == 'categorias' else 'Subcategorias'}",
                f"Leitura: {'Consolidado' if leitura == 'consolidado' else 'Separado'}",
                f"Modo: {dict(self.modos_disponiveis).get(modo, modo)}",
                f"Granularidade: {dict(self.granularidades_disponiveis).get(granularidade, granularidade)}",
                f"Mostrar valores no grafico: {'Sim' if mostrar_valores else 'Nao'}",
            ]
        )

        if itens_selecionados:
            filtros_humanos.append(
                f"{'Categorias' if escopo == 'categorias' else 'Subcategorias'} selecionadas: "
                + ', '.join(item['label'] for item in itens_selecionados)
            )

        if selected_ids:
            contas_selecionadas = [
                conta.nome
                for conta in _ordenar_itens_insensivel(
                    ContaFinanceira.objects.filter(id__in=selected_ids),
                    'nome',
                )
            ]
            filtros_humanos.append(
                'Contas: ' + (', '.join(contas_selecionadas) if contas_selecionadas else 'Todas as contas')
            )
        return filtros_humanos

    def _montar_relatorio(
        self,
        data_inicial: date,
        data_final: date,
        selected_ids: list[int],
        itens_selecionados: list[dict[str, object]],
        *,
        escopo: str,
        leitura: str,
        modo: str,
        granularidade: str,
        mostrar_valores: bool,
    ) -> dict[str, object]:
        if not itens_selecionados:
            return {
                'erro': 'Selecione ao menos uma categoria ou subcategoria para gerar o grafico.',
            }

        relatorio = self._montar_relatorio_periodo(
            data_inicial,
            data_final,
            selected_ids,
            itens_selecionados,
            escopo=escopo,
            leitura=leitura,
            modo_series=modo,
            granularidade=granularidade,
            mostrar_valores=mostrar_valores,
        )
        if relatorio.get('erro'):
            return relatorio

        relatorio['descricao_grafico'] = self._descricao_grafico(
            modo=modo,
            leitura=leitura,
            granularidade=granularidade,
        )
        relatorio['filtros_humanos'] = self._montar_filtros_humanos(
            escopo=escopo,
            leitura=leitura,
            modo=modo,
            granularidade=granularidade,
            mostrar_valores=mostrar_valores,
            itens_selecionados=itens_selecionados,
            selected_ids=selected_ids,
            periodo_principal_label=relatorio['periodo_label'],
        )
        return relatorio

    def _montar_relatorio_comparacao(
        self,
        *,
        data_inicial_principal: date,
        data_final_principal: date,
        data_inicial_comparativo: date,
        data_final_comparativo: date,
        selected_ids: list[int],
        itens_selecionados: list[dict[str, object]],
        escopo: str,
        leitura: str,
        modo: str,
        granularidade: str,
        mostrar_valores: bool,
    ) -> dict[str, object]:
        if not itens_selecionados:
            return {
                'erro': 'Selecione ao menos uma categoria ou subcategoria para gerar a comparacao.',
            }

        relatorio_a = self._montar_relatorio_periodo(
            data_inicial_principal,
            data_final_principal,
            selected_ids,
            itens_selecionados,
            escopo=escopo,
            leitura=leitura,
            modo_series=modo,
            granularidade=granularidade,
            mostrar_valores=mostrar_valores,
        )
        if relatorio_a.get('erro'):
            return relatorio_a

        relatorio_b = self._montar_relatorio_periodo(
            data_inicial_comparativo,
            data_final_comparativo,
            selected_ids,
            itens_selecionados,
            escopo=escopo,
            leitura=leitura,
            modo_series=modo,
            granularidade=granularidade,
            mostrar_valores=mostrar_valores,
        )
        if relatorio_b.get('erro'):
            return relatorio_b

        series_a = {serie['chave']: serie for serie in relatorio_a['series']}
        series_b = {serie['chave']: serie for serie in relatorio_b['series']}
        ordem_series = [serie['chave'] for serie in relatorio_a['series']]
        for chave in series_b:
            if chave not in ordem_series:
                ordem_series.append(chave)

        linhas_comparacao = []
        total_periodo_a = Decimal('0.00')
        total_periodo_b = Decimal('0.00')
        for chave in ordem_series:
            serie_a = series_a.get(chave)
            serie_b = series_b.get(chave)
            serie_base = serie_a or serie_b
            valor_a = serie_a['total'] if serie_a else Decimal('0.00')
            valor_b = serie_b['total'] if serie_b else Decimal('0.00')
            valor_a_exibicao = self._valor_exibicao_comparacao(valor_a, serie_base['tipo'])
            valor_b_exibicao = self._valor_exibicao_comparacao(valor_b, serie_base['tipo'])
            diferenca_absoluta = abs(valor_b - valor_a)
            variacao_percentual = _calcular_variacao_percentual(valor_a, valor_b)
            comparacao_css = self._classe_semantica_comparacao(serie_base['tipo'], valor_a, valor_b)
            total_periodo_a += valor_a
            total_periodo_b += valor_b
            linhas_comparacao.append(
                {
                    'label': serie_base['label'],
                    'label_tabela': serie_base.get('label_grafico') or serie_base['label'],
                    'label_grafico': serie_base.get('label_grafico') or serie_base['label'],
                    'tipo': serie_base['tipo'],
                    'valor_a_absoluto': valor_a,
                    'valor_a_exibicao': valor_a_exibicao,
                    'valor_a_exibido_formatado': _formatar_moeda_brl_exibicao(valor_a_exibicao),
                    'valor_b_absoluto': valor_b,
                    'valor_b_exibicao': valor_b_exibicao,
                    'valor_b_exibido_formatado': _formatar_moeda_brl_exibicao(valor_b_exibicao),
                    'diferenca_absoluta': diferenca_absoluta,
                    'diferenca_absoluta_formatada': _formatar_moeda_brl_exibicao(diferenca_absoluta),
                    'diferenca_css': comparacao_css,
                    'variacao_percentual': variacao_percentual,
                    'variacao_percentual_formatada': _formatar_percentual_relatorio(variacao_percentual),
                    'variacao_css': comparacao_css if variacao_percentual is not None else '',
                }
            )

        diferenca_total_absoluta = abs(total_periodo_b - total_periodo_a)
        variacao_total_percentual = _calcular_variacao_percentual(total_periodo_a, total_periodo_b)
        total_periodo_a_exibicao = sum(
            (linha['valor_a_exibicao'] for linha in linhas_comparacao),
            Decimal('0.00'),
        )
        total_periodo_b_exibicao = sum(
            (linha['valor_b_exibicao'] for linha in linhas_comparacao),
            Decimal('0.00'),
        )
        diferenca_total_absoluta_exibicao = abs(total_periodo_b_exibicao - total_periodo_a_exibicao)
        total_liquido_css = self._classe_semantica_total_comparacao(
            total_periodo_a_exibicao,
            total_periodo_b_exibicao,
        )
        periodo_principal_label = _formatar_periodo_comparacao(data_inicial_principal, data_final_principal)
        periodo_comparativo_label = _formatar_periodo_comparacao(data_inicial_comparativo, data_final_comparativo)
        comparacao_visual_consolidada = leitura == 'consolidado'
        comparacao_grafico_consolidado = None
        comparacao_grafico_resumo_detalhado = None
        if comparacao_visual_consolidada:
            comparacao_grafico_consolidado = self._montar_grafico_comparativo_consolidado(
                relatorio_principal=relatorio_a,
                relatorio_comparativo=relatorio_b,
                periodo_principal_label=periodo_principal_label,
                periodo_comparativo_label=periodo_comparativo_label,
                mostrar_valores=mostrar_valores,
            )
        else:
            comparacao_grafico_resumo_detalhado = self._montar_grafico_resumo_comparacao_detalhada(
                linhas_comparacao=linhas_comparacao,
                periodo_principal_label=periodo_principal_label,
                periodo_comparativo_label=periodo_comparativo_label,
            )

        return {
            'modo_comparacao_periodos': True,
            'comparacao_periodo_principal': relatorio_a,
            'comparacao_periodo_comparativo': relatorio_b,
            'comparacao_series': relatorio_a['series'],
            'comparacao_visual_consolidada': comparacao_visual_consolidada,
            'comparacao_visual_detalhada': not comparacao_visual_consolidada,
            'comparacao_grafico_consolidado': comparacao_grafico_consolidado,
            'comparacao_grafico_resumo_detalhado': comparacao_grafico_resumo_detalhado,
            'linhas_comparacao': linhas_comparacao,
            'quantidade_itens_comparados': len(linhas_comparacao),
            'quantidade_lancamentos_principal': relatorio_a['quantidade_lancamentos'],
            'quantidade_lancamentos_comparativo': relatorio_b['quantidade_lancamentos'],
            'total_periodo_principal': total_periodo_a,
            'total_periodo_principal_exibido': total_periodo_a_exibicao,
            'total_periodo_principal_formatado': _formatar_moeda_brl_exibicao(total_periodo_a_exibicao),
            'total_periodo_comparativo': total_periodo_b,
            'total_periodo_comparativo_exibido': total_periodo_b_exibicao,
            'total_periodo_comparativo_formatado': _formatar_moeda_brl_exibicao(total_periodo_b_exibicao),
            'diferenca_total_absoluta': diferenca_total_absoluta,
            'diferenca_total_absoluta_exibicao': diferenca_total_absoluta_exibicao,
            'diferenca_total_absoluta_formatada': _formatar_moeda_brl_exibicao(diferenca_total_absoluta_exibicao),
            'diferenca_total_css': total_liquido_css,
            'variacao_total_percentual': variacao_total_percentual,
            'variacao_total_percentual_formatada': _formatar_percentual_relatorio(variacao_total_percentual),
            'variacao_total_css': total_liquido_css if variacao_total_percentual is not None else '',
            'descricao_grafico': (
                'No consolidado, a comparacao usa um unico grafico de linhas com duas series, reunindo a evolucao agregada dos intervalos selecionados na granularidade escolhida.'
                if comparacao_visual_consolidada
                else 'Na leitura detalhada, a tabela comparativa abaixo vira a referencia principal para evitar excesso de linhas e manter a comparacao mais segura.'
            ),
            'filtros_humanos': self._montar_filtros_humanos(
                escopo=escopo,
                leitura=leitura,
                modo=modo,
                granularidade=granularidade,
                mostrar_valores=mostrar_valores,
                itens_selecionados=itens_selecionados,
                selected_ids=selected_ids,
                periodo_principal_label=periodo_principal_label,
                periodo_comparativo_label=periodo_comparativo_label,
            ),
            'periodo_principal_label': periodo_principal_label,
            'periodo_comparativo_label': periodo_comparativo_label,
            'periodo_label': f'{periodo_principal_label} x {periodo_comparativo_label}',
            'granularidade_grafico_label': dict(self.granularidades_disponiveis).get(granularidade, granularidade),
            'tem_dados': relatorio_a['tem_dados'] or relatorio_b['tem_dados'],
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contexto_base = self._build_contexto_base()
        context.update(contexto_base)

        _, _, selected_ids = self._parse_contas()
        if contexto_base['modo_comparacao_periodos']:
            data_inicial, data_final = contexto_base['periodo_resolvido']
            data_inicial_comparativo, data_final_comparativo = contexto_base['periodo_comparativo_resolvido']
            if (
                contexto_base['periodo_error']
                or not data_inicial
                or not data_final
                or not data_inicial_comparativo
                or not data_final_comparativo
            ):
                return context

            relatorio = self._montar_relatorio_comparacao(
                data_inicial_principal=data_inicial,
                data_final_principal=data_final,
                data_inicial_comparativo=data_inicial_comparativo,
                data_final_comparativo=data_final_comparativo,
                selected_ids=selected_ids,
                itens_selecionados=contexto_base['categorias_selecionadas'],
                escopo=contexto_base['escopo'],
                leitura=contexto_base['leitura'],
                modo=contexto_base['modo'],
                granularidade=contexto_base['granularidade'],
                mostrar_valores=contexto_base['mostrar_valores'],
            )
        else:
            data_inicial, data_final = contexto_base['periodo_resolvido']
            if contexto_base['periodo_error'] or not data_inicial or not data_final:
                return context

            relatorio = self._montar_relatorio(
                data_inicial,
                data_final,
                selected_ids,
                contexto_base['categorias_selecionadas'],
                escopo=contexto_base['escopo'],
                leitura=contexto_base['leitura'],
                modo=contexto_base['modo'],
                granularidade=contexto_base['granularidade'],
                mostrar_valores=contexto_base['mostrar_valores'],
            )
        if relatorio.get('erro'):
            context['periodo_error'] = relatorio['erro']
            return context

        context.update(relatorio)
        return context


class FinanceiroAutocompleteView(FinanceiroPermissaoMixin, View):
    model = None
    search_fields: tuple[str, ...] = ()
    limit = 10

    def get_queryset(self):
        if self.model is None:
            raise ValueError('model precisa ser definida')
        queryset = self.model.objects.all()
        query = self.request.GET.get('q', '').strip()
        if query:
            filters = Q()
            for field in self.search_fields:
                filters |= Q(**{f'{field}__icontains': query})
            queryset = queryset.filter(filters)
        return queryset

    def get(self, request, *args, **kwargs):
        results = [{'id': obj.pk, 'label': str(obj)} for obj in self.get_queryset()[: self.limit]]
        return JsonResponse({'results': results})


class PessoaFinanceiraAutocompleteView(FinanceiroAutocompleteView):
    permissao_requerida = 'financeiro.pessoas.acessar_endpoints_auxiliares'
    model = PessoaFinanceira
    search_fields = ('codigo', 'nome', 'documento', 'email')


class PessoaFinanceiraUltimosLancamentosView(FinanceiroPermissaoMixin, View):
    permissao_requerida = 'financeiro.pessoas.acessar_endpoints_auxiliares'
    limit = 5

    def _get_clone_url(self, request, lancamento: LancamentoFinanceiro) -> str:
        if not usuario_possui_permissao(request.user, 'financeiro.lancamentos.clonar'):
            return ''
        if lancamento.com_rateio and lancamento.grupo_rateio:
            clone_url = reverse(
                'financeiro:lancamento-rateio-clone',
                kwargs={'grupo_rateio': lancamento.grupo_rateio},
            )
        elif not lancamento.com_rateio and not lancamento.grupo_rateio:
            clone_url = reverse(
                'financeiro:lancamento-clone',
                kwargs={'pk': lancamento.pk},
            )
        else:
            return ''

        return_to = (request.GET.get('return_to') or '').strip()
        if return_to and url_has_allowed_host_and_scheme(
            return_to,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return f'{clone_url}?{urlencode({"return_to": return_to})}'
        return clone_url

    def get(self, request, pessoa_id: int, *args, **kwargs):
        queryset_base = LancamentoFinanceiro.objects.filter(pessoa_id=pessoa_id)
        lancamentos = list(
            queryset_base
            .select_related('categoria')
            .order_by('-data_pagamento', '-data_competencia', '-criado_em', '-pk')[: self.limit]
        )
        total_quitado = (
            queryset_base
            .filter(status=LancamentoFinanceiro.StatusLancamento.QUITADO)
            .aggregate(total=Sum('valor', default=Decimal('0.00')))['total']
        )
        total_aberto = (
            queryset_base
            .filter(status=LancamentoFinanceiro.StatusLancamento.ABERTO)
            .aggregate(total=Sum('valor', default=Decimal('0.00')))['total']
        )
        results = [
            {
                'data': (lancamento.data_pagamento or lancamento.data_competencia).strftime('%d/%m/%Y'),
                'tipo': lancamento.get_tipo_display(),
                'status': lancamento.get_status_display(),
                'descricao': lancamento.descricao,
                'valor': f'R$ {lancamento.valor:.2f}',
                'categoria': str(lancamento.categoria) if lancamento.categoria else 'Sem categoria',
                'numero_documento': lancamento.numero_documento or '',
                'clone_url': self._get_clone_url(request, lancamento),
            }
            for lancamento in lancamentos
        ]
        return JsonResponse(
            {
                'results': results,
                'totais': {
                    'quitado': f"R$ {_formatar_moeda_brl(total_quitado or Decimal('0.00'))}",
                    'aberto': f"R$ {_formatar_moeda_brl(total_aberto or Decimal('0.00'))}",
                },
            }
        )


def _parse_data_iso(valor: str):
    valor = (valor or '').strip()
    if not valor:
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        return None


class CategoriaFinanceiraAutocompleteView(FinanceiroAutocompleteView):
    permissao_requerida = 'financeiro.subcategorias.acessar_endpoints_auxiliares'
    model = CategoriaFinanceira
    search_fields = ('nome',)
    limit = 1000

    def get_queryset(self):
        queryset = super().get_queryset().filter(categoria_pai__isnull=False)
        tipo = self.request.GET.get('tipo', '').strip()
        if tipo in {
            LancamentoFinanceiro.TipoLancamento.RECEITA,
            LancamentoFinanceiro.TipoLancamento.DESPESA,
        }:
            queryset = queryset.filter(tipo=tipo)
        return queryset


class ContaFinanceiraAutocompleteView(FinanceiroAutocompleteView):
    permissao_requerida = 'financeiro.contas.acessar_endpoints_auxiliares'
    model = ContaFinanceira
    search_fields = ('nome', 'descricao')


class CentroCustoAutocompleteView(FinanceiroAutocompleteView):
    permissao_requerida = 'financeiro.centros_custo.acessar_endpoints_auxiliares'
    model = CentroCusto
    search_fields = ('codigo', 'nome')


class RegraLancamentoFinanceiroSugestaoView(FinanceiroPermissaoMixin, View):
    permissao_requerida = 'financeiro.lancamentos.acessar_endpoints_auxiliares'
    limit = 5

    def get(self, request, *args, **kwargs):
        descricao = request.GET.get('descricao', '').strip()
        pessoa_id = request.GET.get('pessoa', '').strip()

        if not descricao:
            return JsonResponse({'results': []})

        filtros = Q(ativa=True, descricao__icontains=descricao)
        if pessoa_id:
            try:
                pessoa_id_int = int(pessoa_id)
            except ValueError:
                pessoa_id_int = None
            if pessoa_id_int:
                filtros &= Q(pessoa_id=pessoa_id_int) | Q(pessoa__isnull=True)

        regras = (
            RegraLancamentoFinanceiro.objects.filter(filtros)
            .select_related('pessoa', 'categoria', 'centro_custo', 'conta', 'conta_destino')
            .order_by('descricao', '-atualizado_em', '-pk')[: self.limit]
        )

        results = []
        for regra in regras:
            resumo_partes = [regra.get_tipo_display(), str(regra.conta)]
            if regra.categoria:
                resumo_partes.append(str(regra.categoria))
            results.append(
                {
                    'id': regra.pk,
                    'label': regra.descricao,
                    'resumo': ' | '.join(resumo_partes),
                    'payload': {
                        'descricao': regra.descricao,
                        'tipo': regra.tipo,
                        'pessoa': (
                            {'id': regra.pessoa_id, 'label': str(regra.pessoa)}
                            if regra.pessoa_id
                            else None
                        ),
                        'categoria': (
                            {'id': regra.categoria_id, 'label': str(regra.categoria)}
                            if regra.categoria_id
                            else None
                        ),
                        'centro_custo': (
                            {'id': regra.centro_custo_id, 'label': str(regra.centro_custo)}
                            if regra.centro_custo_id
                            else None
                        ),
                        'conta': {'id': regra.conta_id, 'label': str(regra.conta)},
                        'conta_destino': (
                            {'id': regra.conta_destino_id, 'label': str(regra.conta_destino)}
                            if regra.conta_destino_id
                            else None
                        ),
                        'observacoes': regra.observacoes,
                    },
                }
            )
        return JsonResponse({'results': results})


class ContaFinanceiraListView(FinanceiroPermissaoMixin, ListView):
    permissao_requerida = 'financeiro.contas.listar'
    model = ContaFinanceira
    template_name = 'financeiro/conta_list.html'
    context_object_name = 'contas'

    def get_queryset(self):
        queryset = super().get_queryset()
        nome = self.request.GET.get('nome', '').strip()
        ativa = self.request.GET.get('ativa', '').strip()
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if ativa == 'ativas':
            queryset = queryset.filter(ativa=True)
        elif ativa == 'inativas':
            queryset = queryset.filter(ativa=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contas = list(context['contas'])
        contas_por_id = {conta.id: conta for conta in contas}

        for conta in contas:
            conta.saldo_atual = conta.saldo_inicial or Decimal('0.00')

        if contas_por_id:
            lancamentos = LancamentoFinanceiro.objects.filter(
                Q(conta_id__in=contas_por_id.keys()) | Q(conta_destino_id__in=contas_por_id.keys()),
                status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            ).only('tipo', 'valor', 'conta_id', 'conta_destino_id')

            for lancamento in lancamentos:
                if (
                    lancamento.tipo == LancamentoFinanceiro.TipoLancamento.RECEITA
                    and lancamento.conta_id in contas_por_id
                ):
                    contas_por_id[lancamento.conta_id].saldo_atual += lancamento.valor
                elif (
                    lancamento.tipo == LancamentoFinanceiro.TipoLancamento.DESPESA
                    and lancamento.conta_id in contas_por_id
                ):
                    contas_por_id[lancamento.conta_id].saldo_atual -= lancamento.valor
                elif lancamento.tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
                    if lancamento.conta_id in contas_por_id:
                        contas_por_id[lancamento.conta_id].saldo_atual -= lancamento.valor
                    if lancamento.conta_destino_id in contas_por_id:
                        contas_por_id[lancamento.conta_destino_id].saldo_atual += lancamento.valor

        context['contas'] = contas
        exportacao_url = reverse('financeiro:conta-exportacao')
        filtros = self.request.GET.urlencode()
        if filtros:
            exportacao_url = f'{exportacao_url}?{filtros}'
        context['exportacao_contas_url'] = exportacao_url
        return context


class ContaFinanceiraCreateView(FinanceiroFormMixin, CreateView):
    permissao_requerida = 'financeiro.contas.criar'
    model = ContaFinanceira
    form_class = ContaFinanceiraForm
    template_name = 'financeiro/conta_form.html'
    success_url = reverse_lazy('financeiro:conta-list')
    page_title = 'Nova Conta Financeira'
    success_message = 'Conta financeira cadastrada com sucesso.'
    allow_save_and_stay = True

    def form_valid(self, form):
        response = super().form_valid(form)
        _registrar_auditoria_conta(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
            conta=self.object,
            depois=_snapshot_conta(self.object),
        )
        return response


class ContaFinanceiraUpdateView(FinanceiroFormMixin, UpdateView):
    permissao_requerida = 'financeiro.contas.editar'
    model = ContaFinanceira
    form_class = ContaFinanceiraForm
    template_name = 'financeiro/conta_form.html'
    success_url = reverse_lazy('financeiro:conta-list')
    page_title = 'Editar Conta Financeira'
    submit_label = 'Atualizar'
    success_message = 'Conta financeira atualizada com sucesso.'

    def form_valid(self, form):
        antes = _snapshot_conta(
            ContaFinanceira.objects.get(pk=self.object.pk)
        )
        response = super().form_valid(form)
        depois = _snapshot_conta(self.object)
        _registrar_auditoria_conta(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.UPDATE,
            conta=self.object,
            antes=antes,
            depois=depois,
        )
        return response


class ContaFinanceiraDeleteView(FinanceiroDeleteMixin):
    permissao_requerida = 'financeiro.contas.excluir'
    model = ContaFinanceira
    success_url = reverse_lazy('financeiro:conta-list')
    page_title = 'Excluir Conta Financeira'
    cancel_url = reverse_lazy('financeiro:conta-list')
    success_message = 'Conta financeira excluida com sucesso.'

    def form_valid(self, form):
        conta = self.object
        antes = _snapshot_conta(conta)
        registro_id = conta.pk

        with transaction.atomic():
            response = super().form_valid(form)
            AuditoriaFinanceiro.objects.create(
                acao=AuditoriaFinanceiro.AcaoAuditoria.DELETE,
                modelo='ContaFinanceira',
                registro_id=registro_id,
                usuario=_auditoria_usuario(self.request),
                campos_alterados=_build_auditoria_payload(antes, None),
            )

        return response


class ExtratoContaMixin(FinanceiroPermissaoMixin):
    def _formatar_data_rotulo(self, valor: str) -> str:
        if not valor:
            return ''
        try:
            return datetime.strptime(valor, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            return valor

    def _montar_periodo_label(self, data_inicial: str, data_final: str, escopo_padrao: str = 'conta') -> str:
        if data_inicial and data_final:
            return f'{self._formatar_data_rotulo(data_inicial)} a {self._formatar_data_rotulo(data_final)}'
        if data_inicial:
            return f'A partir de {self._formatar_data_rotulo(data_inicial)}'
        if data_final:
            return f'Ate {self._formatar_data_rotulo(data_final)}'
        return f'Periodo completo {escopo_padrao}'

    def _parse_checkbox(self, param_name: str) -> bool:
        valores = [valor.strip().lower() for valor in self.request.GET.getlist(param_name)]
        if not valores:
            return False

        for valor in reversed(valores):
            if valor in {'1', 'true', 'on', 'yes'}:
                return True
            if valor in {'0', 'false', 'off', 'no', ''}:
                return False
        return False

    def _classificar_lancamento(self, conta: ContaFinanceira, lancamento: LancamentoFinanceiro) -> tuple[Decimal, Decimal]:
        entrada = Decimal('0.00')
        saida = Decimal('0.00')

        if lancamento.tipo == LancamentoFinanceiro.TipoLancamento.RECEITA and lancamento.conta_id == conta.id:
            entrada = lancamento.valor
        elif lancamento.tipo == LancamentoFinanceiro.TipoLancamento.DESPESA and lancamento.conta_id == conta.id:
            saida = lancamento.valor
        elif lancamento.tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
            if lancamento.conta_id == conta.id:
                saida = lancamento.valor
            elif lancamento.conta_destino_id == conta.id:
                entrada = lancamento.valor

        return entrada, saida

    def _classificar_lancamento_escopo(
        self,
        selected_ids_set: set[int],
        lancamento: LancamentoFinanceiro,
    ) -> tuple[Decimal, Decimal]:
        entrada = Decimal('0.00')
        saida = Decimal('0.00')

        if (
            lancamento.tipo == LancamentoFinanceiro.TipoLancamento.RECEITA
            and lancamento.conta_id in selected_ids_set
        ):
            entrada = lancamento.valor
        elif (
            lancamento.tipo == LancamentoFinanceiro.TipoLancamento.DESPESA
            and lancamento.conta_id in selected_ids_set
        ):
            saida = lancamento.valor
        elif lancamento.tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
            origem_no_escopo = lancamento.conta_id in selected_ids_set
            destino_no_escopo = lancamento.conta_destino_id in selected_ids_set
            if origem_no_escopo and not destino_no_escopo:
                saida = lancamento.valor
            elif destino_no_escopo and not origem_no_escopo:
                entrada = lancamento.valor

        return entrada, saida

    def _resolver_conta_exibicao_escopo(
        self,
        selected_ids_set: set[int],
        lancamento: LancamentoFinanceiro,
    ) -> str:
        if lancamento.tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
            origem_no_escopo = lancamento.conta_id in selected_ids_set
            destino_no_escopo = lancamento.conta_destino_id in selected_ids_set
            if origem_no_escopo and destino_no_escopo:
                origem = lancamento.conta.nome if lancamento.conta_id else '-'
                destino = lancamento.conta_destino.nome if lancamento.conta_destino_id else '-'
                return f'{origem} -> {destino}'
            if origem_no_escopo and lancamento.conta_id:
                return lancamento.conta.nome
            if destino_no_escopo and lancamento.conta_destino_id:
                return lancamento.conta_destino.nome
            return '-'
        return lancamento.conta.nome if lancamento.conta_id else '-'

    def _chave_bloco_extrato(self, lancamento: LancamentoFinanceiro) -> str:
        grupo_rateio = (lancamento.grupo_rateio or '').strip()
        if lancamento.com_rateio and grupo_rateio:
            return f'rateio:{grupo_rateio}'
        return f'lancamento:{lancamento.pk}'

    def _montar_itens_extrato(
        self,
        conta: ContaFinanceira,
        lancamentos: list[LancamentoFinanceiro],
        saldo_inicial: Decimal,
    ) -> tuple[list[dict[str, object]], Decimal]:
        blocos: list[list[LancamentoFinanceiro]] = []
        blocos_por_chave: dict[str, list[LancamentoFinanceiro]] = {}

        for lancamento in lancamentos:
            chave_bloco = self._chave_bloco_extrato(lancamento)
            bloco = blocos_por_chave.get(chave_bloco)
            if bloco is None:
                bloco = []
                blocos_por_chave[chave_bloco] = bloco
                blocos.append(bloco)
            bloco.append(lancamento)

        saldo_acumulado = saldo_inicial
        itens_extrato: list[dict[str, object]] = []

        for bloco in blocos:
            lancamento_representante = bloco[0]
            entrada_total = Decimal('0.00')
            saida_total = Decimal('0.00')

            for lancamento in bloco:
                entrada, saida = self._classificar_lancamento(conta, lancamento)
                entrada_total += entrada
                saida_total += saida

            saldo_acumulado += entrada_total - saida_total
            observacoes = next(
                ((lancamento.observacoes or '').strip() for lancamento in bloco if (lancamento.observacoes or '').strip()),
                '',
            )
            itens_extrato.append(
                {
                    'lancamento': lancamento_representante,
                    'entrada': entrada_total,
                    'saida': saida_total,
                    'valor_exibicao': entrada_total if entrada_total else (-saida_total if saida_total else Decimal('0.00')),
                    'valor_exibicao_absoluto': entrada_total if entrada_total else saida_total,
                    'saldo_acumulado': saldo_acumulado,
                    'rateio_consolidado': len(bloco) > 1 and bool((lancamento_representante.grupo_rateio or '').strip()),
                    'quantidade_linhas_rateio': len(bloco),
                    'favorecido_exibicao': lancamento_representante.pessoa.nome if lancamento_representante.pessoa else '-',
                    'observacoes_exibicao': observacoes or '-',
                }
            )

        return itens_extrato, saldo_acumulado

    def _montar_itens_extrato_escopo(
        self,
        selected_ids: list[int],
        lancamentos: list[LancamentoFinanceiro],
        saldo_inicial: Decimal,
    ) -> tuple[list[dict[str, object]], Decimal]:
        selected_ids_set = set(selected_ids)
        blocos: list[list[LancamentoFinanceiro]] = []
        blocos_por_chave: dict[str, list[LancamentoFinanceiro]] = {}

        for lancamento in lancamentos:
            chave_bloco = self._chave_bloco_extrato(lancamento)
            bloco = blocos_por_chave.get(chave_bloco)
            if bloco is None:
                bloco = []
                blocos_por_chave[chave_bloco] = bloco
                blocos.append(bloco)
            bloco.append(lancamento)

        saldo_acumulado = saldo_inicial
        itens_extrato: list[dict[str, object]] = []

        for bloco in blocos:
            lancamento_representante = bloco[0]
            entrada_total = Decimal('0.00')
            saida_total = Decimal('0.00')

            for lancamento in bloco:
                entrada, saida = self._classificar_lancamento_escopo(selected_ids_set, lancamento)
                entrada_total += entrada
                saida_total += saida

            if entrada_total == Decimal('0.00') and saida_total == Decimal('0.00'):
                continue

            saldo_acumulado += entrada_total - saida_total
            observacoes = next(
                ((lancamento.observacoes or '').strip() for lancamento in bloco if (lancamento.observacoes or '').strip()),
                '',
            )
            itens_extrato.append(
                {
                    'lancamento': lancamento_representante,
                    'entrada': entrada_total,
                    'saida': saida_total,
                    'valor_exibicao': entrada_total if entrada_total else (-saida_total if saida_total else Decimal('0.00')),
                    'valor_exibicao_absoluto': entrada_total if entrada_total else saida_total,
                    'saldo_acumulado': saldo_acumulado,
                    'rateio_consolidado': len(bloco) > 1 and bool((lancamento_representante.grupo_rateio or '').strip()),
                    'quantidade_linhas_rateio': len(bloco),
                    'favorecido_exibicao': lancamento_representante.pessoa.nome if lancamento_representante.pessoa else '-',
                    'observacoes_exibicao': observacoes or '-',
                    'conta_exibicao': self._resolver_conta_exibicao_escopo(selected_ids_set, lancamento_representante),
                }
            )

        return itens_extrato, saldo_acumulado

    def _get_extrato_context(
        self,
        conta: ContaFinanceira,
        data_inicial: str = '',
        data_final: str = '',
        mostrar_observacao: bool = False,
    ) -> dict[str, object]:
        queryset_base = (
            LancamentoFinanceiro.objects.filter(
                Q(conta=conta) | Q(conta_destino=conta),
                status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            )
            .select_related('conta', 'conta_destino', 'pessoa', 'categoria')
            .annotate(data_extrato=Coalesce('data_pagamento', 'data_competencia'))
            .order_by('data_extrato', 'pk')
        )

        saldo_anterior = conta.saldo_inicial or Decimal('0.00')
        if data_inicial:
            lancamentos_anteriores = queryset_base.filter(data_extrato__lt=data_inicial)
            for lancamento in lancamentos_anteriores:
                entrada, saida = self._classificar_lancamento(conta, lancamento)
                saldo_anterior += entrada - saida

        lancamentos = queryset_base
        if data_inicial:
            lancamentos = lancamentos.filter(data_extrato__gte=data_inicial)
        if data_final:
            lancamentos = lancamentos.filter(data_extrato__lte=data_final)

        saldo_base = saldo_anterior if data_inicial else (conta.saldo_inicial or Decimal('0.00'))
        itens_extrato, saldo_acumulado = self._montar_itens_extrato(conta, list(lancamentos), saldo_base)
        total_entradas = sum((item['entrada'] for item in itens_extrato), Decimal('0.00'))
        total_saidas = sum((item['saida'] for item in itens_extrato), Decimal('0.00'))

        return {
            'conta': conta,
            'saldo_inicial': conta.saldo_inicial or Decimal('0.00'),
            'data_saldo_inicial': conta.data_saldo_inicial,
            'data_inicial': data_inicial,
            'data_final': data_final,
            'periodo_label': self._montar_periodo_label(data_inicial, data_final),
            'saldo_anterior': saldo_anterior if data_inicial else None,
            'exibe_linha_saldo_inicial': True,
            'itens_extrato': itens_extrato,
            'saldo_final': saldo_acumulado,
            'saldo_atual': saldo_acumulado,
            'mostrar_observacao': mostrar_observacao,
            'total_entradas_periodo': total_entradas,
            'total_saidas_periodo': total_saidas,
            'quantidade_movimentos': len(itens_extrato),
            'conta_label': conta.nome,
            'contas_label': conta.nome,
            'tem_extrato': True,
            'extrato_multiplas_contas': False,
            'extrato_todas_contas': False,
        }

    def _get_extrato_escopo_context(
        self,
        contas: list[ContaFinanceira],
        data_inicial: str = '',
        data_final: str = '',
        mostrar_observacao: bool = False,
        todas_as_contas: bool = False,
    ) -> dict[str, object]:
        selected_ids = [conta.id for conta in contas]
        selected_ids_set = set(selected_ids)
        queryset_base = (
            LancamentoFinanceiro.objects.filter(
                Q(conta_id__in=selected_ids) | Q(conta_destino_id__in=selected_ids),
                status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            )
            .select_related('conta', 'conta_destino', 'pessoa', 'categoria')
            .annotate(data_extrato=Coalesce('data_pagamento', 'data_competencia'))
            .order_by('data_extrato', 'pk')
        )

        saldo_inicial = sum((conta.saldo_inicial or Decimal('0.00') for conta in contas), Decimal('0.00'))
        saldo_anterior = saldo_inicial
        if data_inicial:
            lancamentos_anteriores = queryset_base.filter(data_extrato__lt=data_inicial)
            for lancamento in lancamentos_anteriores:
                entrada, saida = self._classificar_lancamento_escopo(selected_ids_set, lancamento)
                saldo_anterior += entrada - saida

        lancamentos = queryset_base
        if data_inicial:
            lancamentos = lancamentos.filter(data_extrato__gte=data_inicial)
        if data_final:
            lancamentos = lancamentos.filter(data_extrato__lte=data_final)

        saldo_base = saldo_anterior if data_inicial else saldo_inicial
        itens_extrato, saldo_acumulado = self._montar_itens_extrato_escopo(
            selected_ids,
            list(lancamentos),
            saldo_base,
        )
        total_entradas = sum((item['entrada'] for item in itens_extrato), Decimal('0.00'))
        total_saidas = sum((item['saida'] for item in itens_extrato), Decimal('0.00'))
        contas_label = (
            'Todas as contas'
            if todas_as_contas
            else ', '.join(conta.nome for conta in contas)
        )

        return {
            'conta': contas[0] if len(contas) == 1 else None,
            'contas_selecionadas': contas,
            'saldo_inicial': saldo_inicial,
            'data_saldo_inicial': None,
            'data_inicial': data_inicial,
            'data_final': data_final,
            'periodo_label': self._montar_periodo_label(data_inicial, data_final, 'do escopo'),
            'saldo_anterior': saldo_anterior if data_inicial else None,
            'exibe_linha_saldo_inicial': True,
            'itens_extrato': itens_extrato,
            'saldo_final': saldo_acumulado,
            'saldo_atual': saldo_acumulado,
            'mostrar_observacao': mostrar_observacao,
            'total_entradas_periodo': total_entradas,
            'total_saidas_periodo': total_saidas,
            'quantidade_movimentos': len(itens_extrato),
            'conta_label': contas_label,
            'contas_label': contas_label,
            'tem_extrato': True,
            'extrato_multiplas_contas': len(contas) > 1,
            'extrato_todas_contas': todas_as_contas,
        }

    def _parse_contas_extrato(self, contas) -> tuple[list[ContaFinanceira], list[str], bool, bool]:
        contas_lista = list(contas)
        contas_por_id = {conta.id: conta for conta in contas_lista}
        todas_as_contas = self._parse_checkbox('todas_contas')
        filtro_enviado = (self.request.GET.get('contas_form') or '').strip() == '1'
        selected_ids_raw = [valor.strip() for valor in self.request.GET.getlist('contas') if valor.strip()]
        conta_compat = (self.request.GET.get('conta') or '').strip()
        if conta_compat and not selected_ids_raw:
            selected_ids_raw = [conta_compat]

        selected_ids: list[int] = []
        for valor in selected_ids_raw:
            try:
                conta_id = int(valor)
            except (TypeError, ValueError):
                continue
            if conta_id in contas_por_id and conta_id not in selected_ids:
                selected_ids.append(conta_id)

        if todas_as_contas and selected_ids_raw and len(selected_ids) < len(contas_por_id):
            todas_as_contas = False

        if todas_as_contas:
            selected_ids = list(contas_por_id.keys())

        contas_selecionadas = [contas_por_id[conta_id] for conta_id in selected_ids]
        selecao_informada = filtro_enviado or todas_as_contas or bool(selected_ids_raw)
        return contas_selecionadas, [str(conta_id) for conta_id in selected_ids], todas_as_contas, selecao_informada


class ContaFinanceiraExtratoView(ExtratoContaMixin, DetailView):
    permissao_requerida = 'financeiro.extratos.visualizar'
    model = ContaFinanceira
    template_name = 'financeiro/conta_extrato.html'
    context_object_name = 'conta'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conta = self.object
        data_inicial = self.request.GET.get('data_inicial', '').strip()
        data_final = self.request.GET.get('data_final', '').strip()
        mostrar_observacao = self._parse_checkbox('exibir_observacao')

        context.update(self._get_extrato_context(conta, data_inicial, data_final, mostrar_observacao))
        context['page_title'] = f'Extrato da Conta: {conta.nome}'
        context['show_conta_filter'] = False
        context['clear_extrato_url'] = reverse_lazy('financeiro:conta-extrato', kwargs={'pk': conta.pk})
        context['mostrar_observacao'] = mostrar_observacao
        return context


class ExtratoFinanceiroView(ExtratoContaMixin, TemplateView):
    permissao_requerida = 'financeiro.extratos.visualizar'
    template_name = 'financeiro/conta_extrato.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data_inicial = self.request.GET.get('data_inicial', '').strip()
        data_final = self.request.GET.get('data_final', '').strip()
        mostrar_observacao = self._parse_checkbox('exibir_observacao')
        contas = ContaFinanceira.objects.order_by('nome')
        contas_selecionadas, contas_selecionadas_ids, todas_as_contas, selecao_informada = self._parse_contas_extrato(contas)

        context['page_title'] = 'Extratos'
        context['contas'] = contas
        context['conta_selecionada_id'] = contas_selecionadas_ids[0] if len(contas_selecionadas_ids) == 1 else ''
        context['contas_selecionadas_ids'] = contas_selecionadas_ids
        context['todas_contas_selecionadas'] = todas_as_contas
        context['tem_extrato'] = False
        context['show_conta_filter'] = True
        context['clear_extrato_url'] = reverse_lazy('financeiro:extrato-list')
        context['mostrar_observacao'] = mostrar_observacao
        context['data_inicial'] = data_inicial
        context['data_final'] = data_final
        context['periodo_label'] = self._montar_periodo_label(data_inicial, data_final, 'do escopo')

        if selecao_informada and not contas_selecionadas:
            context['extrato_error'] = 'Selecione pelo menos uma conta para carregar o extrato.'
        elif contas_selecionadas:
            if len(contas_selecionadas) == 1 and not todas_as_contas:
                conta = contas_selecionadas[0]
                context.update(self._get_extrato_context(conta, data_inicial, data_final, mostrar_observacao))
                context['contas_selecionadas'] = contas_selecionadas
                context['contas_selecionadas_ids'] = contas_selecionadas_ids
                context['todas_contas_selecionadas'] = False
                context['page_title'] = f'Extratos - {conta.nome}'
            else:
                context.update(
                    self._get_extrato_escopo_context(
                        contas_selecionadas,
                        data_inicial,
                        data_final,
                        mostrar_observacao,
                        todas_as_contas=todas_as_contas,
                    )
                )
                context['page_title'] = f'Extratos - {context["contas_label"]}'

        return context


class AuditoriaLancamentoFinanceiroListView(FinanceiroPermissaoMixin, ListView):
    permissao_requerida = 'financeiro.auditoria.listar'
    model = AuditoriaFinanceiro
    template_name = 'financeiro/auditoria_lancamento_list.html'
    context_object_name = 'auditorias'

    modelos_auditados = [
        'LancamentoFinanceiro',
        'ContaFinanceira',
        'PessoaFinanceira',
        'CategoriaFinanceira',
        'CentroCusto',
        'AssinaturaInstitucional',
        'ConfiguracaoInstitucional',
    ]

    def _get_base_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(modelo__in=self.modelos_auditados)
            .select_related('usuario')
        )

    def get_queryset(self):
        queryset = self._get_base_queryset()
        acao = self.request.GET.get('acao', '').strip()
        data_inicial = self.request.GET.get('data_inicial', '').strip()
        data_final = self.request.GET.get('data_final', '').strip()
        registro_id = self.request.GET.get('registro_id', '').strip()
        usuario_id = self.request.GET.get('usuario', '').strip()

        if acao:
            queryset = queryset.filter(acao=acao)

        if data_inicial:
            try:
                data_inicial_valor = date.fromisoformat(data_inicial)
            except ValueError:
                data_inicial_valor = None
            if data_inicial_valor:
                queryset = queryset.filter(data_hora__date__gte=data_inicial_valor)

        if data_final:
            try:
                data_final_valor = date.fromisoformat(data_final)
            except ValueError:
                data_final_valor = None
            if data_final_valor:
                queryset = queryset.filter(data_hora__date__lte=data_final_valor)

        if registro_id:
            try:
                registro_id_valor = int(registro_id)
            except ValueError:
                registro_id_valor = None
            if registro_id_valor is not None:
                queryset = queryset.filter(registro_id=registro_id_valor)

        if usuario_id:
            try:
                usuario_id_valor = int(usuario_id)
            except ValueError:
                usuario_id_valor = None
            if usuario_id_valor is not None:
                queryset = queryset.filter(usuario_id=usuario_id_valor)

        return queryset.order_by('-data_hora', '-pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuarios_auditoria = []
        usuarios_vistos: set[int] = set()
        for auditoria in (
            self._get_base_queryset()
            .exclude(usuario__isnull=True)
            .order_by('usuario_id', 'data_hora')
        ):
            usuario = auditoria.usuario
            if usuario and usuario.pk not in usuarios_vistos:
                usuarios_vistos.add(usuario.pk)
                usuarios_auditoria.append(usuario)

        context['page_title'] = 'Auditoria do Financeiro'
        context['filtro_acao'] = self.request.GET.get('acao', '').strip()
        context['filtro_data_inicial'] = self.request.GET.get('data_inicial', '').strip()
        context['filtro_data_final'] = self.request.GET.get('data_final', '').strip()
        context['filtro_registro_id'] = self.request.GET.get('registro_id', '').strip()
        context['filtro_usuario'] = self.request.GET.get('usuario', '').strip()
        context['acoes_auditoria'] = AuditoriaFinanceiro.AcaoAuditoria.choices
        context['usuarios_auditoria'] = usuarios_auditoria
        return context


class CentroCustoListView(FinanceiroPermissaoMixin, ListView):
    permissao_requerida = 'financeiro.centros_custo.listar'
    model = CentroCusto
    template_name = 'financeiro/centro_custo_list.html'
    context_object_name = 'centros_custo'

    def get_queryset(self):
        queryset = super().get_queryset()
        codigo = self.request.GET.get('codigo', '').strip()
        nome = self.request.GET.get('nome', '').strip()
        if codigo:
            queryset = queryset.filter(codigo__icontains=codigo)
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exportacao_url = reverse('financeiro:centro-custo-exportacao')
        filtros = self.request.GET.urlencode()
        if filtros:
            exportacao_url = f'{exportacao_url}?{filtros}'
        context['exportacao_centros_custo_url'] = exportacao_url
        return context


class CentroCustoCreateView(FinanceiroFormMixin, CreateView):
    permissao_requerida = 'financeiro.centros_custo.criar'
    model = CentroCusto
    form_class = CentroCustoForm
    template_name = 'financeiro/centro_custo_form.html'
    success_url = reverse_lazy('financeiro:centro-custo-list')
    page_title = 'Novo Centro de Custo'
    success_message = 'Centro de custo cadastrado com sucesso.'
    allow_save_and_stay = True

    def form_valid(self, form):
        response = super().form_valid(form)
        _registrar_auditoria_centro_custo(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
            centro_custo=self.object,
            depois=_snapshot_centro_custo(self.object),
        )
        return response

    def get_success_url(self):
        return_to = self._get_return_to_url()
        if return_to and getattr(self, 'object', None):
            return _append_query_params(
                return_to,
                {
                    'centro_custo_criado': str(self.object.pk),
                    'centro_custo_label': str(self.object),
                    'restaurar_lancamento': '1',
                },
            )
        return super().get_success_url()


class CentroCustoUpdateView(FinanceiroFormMixin, UpdateView):
    permissao_requerida = 'financeiro.centros_custo.editar'
    model = CentroCusto
    form_class = CentroCustoForm
    template_name = 'financeiro/centro_custo_form.html'
    success_url = reverse_lazy('financeiro:centro-custo-list')
    page_title = 'Editar Centro de Custo'
    submit_label = 'Atualizar'
    success_message = 'Centro de custo atualizado com sucesso.'

    def form_valid(self, form):
        antes = _snapshot_centro_custo(
            CentroCusto.objects.get(pk=self.object.pk)
        )
        response = super().form_valid(form)
        depois = _snapshot_centro_custo(self.object)
        _registrar_auditoria_centro_custo(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.UPDATE,
            centro_custo=self.object,
            antes=antes,
            depois=depois,
        )
        return response


class CentroCustoDeleteView(FinanceiroDeleteMixin):
    permissao_requerida = 'financeiro.centros_custo.excluir'
    model = CentroCusto
    success_url = reverse_lazy('financeiro:centro-custo-list')
    page_title = 'Excluir Centro de Custo'
    cancel_url = reverse_lazy('financeiro:centro-custo-list')
    success_message = 'Centro de custo excluido com sucesso.'

    def form_valid(self, form):
        centro_custo = self.object
        antes = _snapshot_centro_custo(centro_custo)
        registro_id = centro_custo.pk

        with transaction.atomic():
            response = super().form_valid(form)
            AuditoriaFinanceiro.objects.create(
                acao=AuditoriaFinanceiro.AcaoAuditoria.DELETE,
                modelo='CentroCusto',
                registro_id=registro_id,
                usuario=_auditoria_usuario(self.request),
                campos_alterados=_build_auditoria_payload(antes, None),
            )

        return response


class PessoaFinanceiraListView(FinanceiroPermissaoMixin, ListView):
    permissao_requerida = 'financeiro.pessoas.listar'
    model = PessoaFinanceira
    template_name = 'financeiro/pessoa_list.html'
    context_object_name = 'pessoas'

    def get_queryset(self):
        queryset = super().get_queryset()
        nome = self.request.GET.get('nome', '').strip()
        codigo = self.request.GET.get('codigo', '').strip()
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if codigo:
            queryset = queryset.filter(codigo__icontains=codigo)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exportacao_url = reverse('financeiro:pessoa-exportacao')
        filtros = self.request.GET.urlencode()
        if filtros:
            exportacao_url = f'{exportacao_url}?{filtros}'
        context['exportacao_pessoas_url'] = exportacao_url
        return context


class PessoaFinanceiraHistoricoView(FinanceiroPermissaoMixin, DetailView):
    permissao_requerida = 'financeiro.lancamentos.listar'
    model = PessoaFinanceira
    template_name = 'financeiro/pessoa_historico.html'
    context_object_name = 'pessoa'

    def _get_lancamentos_queryset(self):
        queryset = (
            LancamentoFinanceiro.objects
            .filter(pessoa=self.object)
            .select_related('conta', 'conta_destino', 'categoria', 'centro_custo')
            .annotate(data_operacional=Coalesce('data_pagamento', 'data_competencia'))
        )

        data_inicial = _parse_data_iso(self.request.GET.get('data_inicial', ''))
        data_final = _parse_data_iso(self.request.GET.get('data_final', ''))
        tipo = (self.request.GET.get('tipo') or '').strip()
        status = (self.request.GET.get('status') or '').strip()
        conta = (self.request.GET.get('conta') or '').strip()
        busca = (self.request.GET.get('q') or '').strip()

        if data_inicial:
            queryset = queryset.filter(data_operacional__gte=data_inicial)
        if data_final:
            queryset = queryset.filter(data_operacional__lte=data_final)
        if tipo in dict(LancamentoFinanceiro.TipoLancamento.choices):
            queryset = queryset.filter(tipo=tipo)
        if status in dict(LancamentoFinanceiro.StatusLancamento.choices):
            queryset = queryset.filter(status=status)
        if conta:
            queryset = queryset.filter(Q(conta_id=conta) | Q(conta_destino_id=conta))
        if busca:
            queryset = queryset.filter(
                Q(descricao__icontains=busca)
                | Q(numero_documento__icontains=busca)
            )

        return queryset.order_by('-data_operacional', '-pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lancamentos = list(self._get_lancamentos_queryset())
        total_geral = sum((lancamento.valor for lancamento in lancamentos), Decimal('0.00'))
        total_receitas = sum(
            (
                lancamento.valor
                for lancamento in lancamentos
                if lancamento.tipo == LancamentoFinanceiro.TipoLancamento.RECEITA
            ),
            Decimal('0.00'),
        )
        total_despesas = sum(
            (
                lancamento.valor
                for lancamento in lancamentos
                if lancamento.tipo == LancamentoFinanceiro.TipoLancamento.DESPESA
            ),
            Decimal('0.00'),
        )
        total_quitado = sum(
            (
                lancamento.valor
                for lancamento in lancamentos
                if lancamento.status == LancamentoFinanceiro.StatusLancamento.QUITADO
            ),
            Decimal('0.00'),
        )
        total_aberto = sum(
            (
                lancamento.valor
                for lancamento in lancamentos
                if lancamento.status == LancamentoFinanceiro.StatusLancamento.ABERTO
            ),
            Decimal('0.00'),
        )
        context.update(
            {
                'page_title': f'Historico do favorecido - {self.object.nome}',
                'lancamentos_historico': lancamentos,
                'contas_disponiveis': ContaFinanceira.objects.order_by('nome'),
                'tipo_choices': LancamentoFinanceiro.TipoLancamento.choices,
                'status_choices': LancamentoFinanceiro.StatusLancamento.choices,
                'filtros_historico_ativos': _request_possui_parametros_get(
                    self.request,
                    ('data_inicial', 'data_final', 'tipo', 'status', 'conta', 'q'),
                ),
                'totais_historico': {
                    'quantidade': len(lancamentos),
                    'total_geral': total_geral,
                    'total_receitas': total_receitas,
                    'total_despesas': total_despesas,
                    'total_quitado': total_quitado,
                    'total_aberto': total_aberto,
                    'total_geral_formatado': _formatar_moeda_brl(total_geral),
                    'total_receitas_formatado': _formatar_moeda_brl(total_receitas),
                    'total_despesas_formatado': _formatar_moeda_brl(total_despesas),
                    'total_quitado_formatado': _formatar_moeda_brl(total_quitado),
                    'total_aberto_formatado': _formatar_moeda_brl(total_aberto),
                },
            }
        )
        return context


class PessoaFinanceiraCreateView(FinanceiroFormMixin, CreateView):
    permissao_requerida = 'financeiro.pessoas.criar'
    model = PessoaFinanceira
    form_class = PessoaFinanceiraForm
    template_name = 'financeiro/pessoa_form.html'
    success_url = reverse_lazy('financeiro:pessoa-list')
    page_title = 'Novo Favorecido Financeiro'
    success_message = 'Favorecido financeiro cadastrado com sucesso.'
    allow_save_and_stay = True

    def form_valid(self, form):
        response = super().form_valid(form)
        _registrar_auditoria_pessoa(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
            pessoa=self.object,
            depois=_snapshot_pessoa(self.object),
        )
        return response

    def get_success_url(self):
        return_to = self._get_return_to_url()
        if return_to and getattr(self, 'object', None):
            return _append_query_params(
                return_to,
                {
                    'pessoa_criada': str(self.object.pk),
                    'pessoa_label': str(self.object),
                    'restaurar_lancamento': '1',
                },
            )
        return super().get_success_url()


class PessoaFinanceiraUpdateView(FinanceiroFormMixin, UpdateView):
    permissao_requerida = 'financeiro.pessoas.editar'
    model = PessoaFinanceira
    form_class = PessoaFinanceiraForm
    template_name = 'financeiro/pessoa_form.html'
    success_url = reverse_lazy('financeiro:pessoa-list')
    page_title = 'Editar Favorecido Financeiro'
    submit_label = 'Atualizar'
    success_message = 'Favorecido financeiro atualizado com sucesso.'

    def form_valid(self, form):
        antes = _snapshot_pessoa(
            PessoaFinanceira.objects.get(pk=self.object.pk)
        )
        response = super().form_valid(form)
        depois = _snapshot_pessoa(self.object)
        _registrar_auditoria_pessoa(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.UPDATE,
            pessoa=self.object,
            antes=antes,
            depois=depois,
        )
        return response


class PessoaFinanceiraDeleteView(FinanceiroDeleteMixin):
    permissao_requerida = 'financeiro.pessoas.excluir'
    model = PessoaFinanceira
    success_url = reverse_lazy('financeiro:pessoa-list')
    page_title = 'Excluir Favorecido Financeiro'
    cancel_url = reverse_lazy('financeiro:pessoa-list')
    success_message = 'Favorecido financeiro excluido com sucesso.'

    def form_valid(self, form):
        pessoa = self.object
        antes = _snapshot_pessoa(pessoa)
        registro_id = pessoa.pk
        lancamentos_vinculados = LancamentoFinanceiro.objects.filter(pessoa=pessoa).exists()
        if lancamentos_vinculados:
            messages.error(
                self.request,
                'Este favorecido ainda possui lancamentos vinculados. Remova o vinculo antes de excluir.',
            )
            return redirect(self.get_cancel_url())

        RegraLancamentoFinanceiro.objects.filter(pessoa=pessoa).update(pessoa=None)

        with transaction.atomic():
            response = super().form_valid(form)
            AuditoriaFinanceiro.objects.create(
                acao=AuditoriaFinanceiro.AcaoAuditoria.DELETE,
                modelo='PessoaFinanceira',
                registro_id=registro_id,
                usuario=_auditoria_usuario(self.request),
                campos_alterados=_build_auditoria_payload(antes, None),
            )

        return response


class CategoriaFinanceiraListView(FinanceiroPermissaoMixin, ListView):
    permissao_requerida = 'financeiro.categorias.listar'
    model = CategoriaFinanceira
    template_name = 'financeiro/categoria_list.html'
    context_object_name = 'categorias'

    def get_queryset(self):
        queryset = super().get_queryset()
        nome = self.request.GET.get('nome', '').strip()
        tipo = self.request.GET.get('tipo', '').strip()
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exportacao_url = reverse('financeiro:categoria-exportacao')
        filtros = self.request.GET.urlencode()
        if filtros:
            exportacao_url = f'{exportacao_url}?{filtros}'
        context['exportacao_categorias_url'] = exportacao_url
        return context


class CategoriaFinanceiraCreateView(FinanceiroFormMixin, CreateView):
    permissao_requerida = 'financeiro.categorias.criar'
    model = CategoriaFinanceira
    form_class = CategoriaFinanceiraForm
    template_name = 'financeiro/categoria_form.html'
    success_url = reverse_lazy('financeiro:categoria-list')
    page_title = 'Nova Categoria Financeira'
    success_message = 'Categoria financeira cadastrada com sucesso.'
    allow_save_and_stay = True

    def form_valid(self, form):
        response = super().form_valid(form)
        _registrar_auditoria_categoria(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
            categoria=self.object,
            depois=_snapshot_categoria(self.object),
        )
        return response

    def get_success_url(self):
        return_to = self._get_return_to_url()
        if return_to and getattr(self, 'object', None):
            return _append_query_params(
                return_to,
                {
                    'categoria_criada': str(self.object.pk),
                    'categoria_label': str(self.object),
                    'restaurar_lancamento': '1',
                },
            )
        return super().get_success_url()


class CategoriaFinanceiraUpdateView(FinanceiroFormMixin, UpdateView):
    permissao_requerida = 'financeiro.categorias.editar'
    model = CategoriaFinanceira
    form_class = CategoriaFinanceiraForm
    template_name = 'financeiro/categoria_form.html'
    success_url = reverse_lazy('financeiro:categoria-list')
    page_title = 'Editar Categoria Financeira'
    submit_label = 'Atualizar'
    success_message = 'Categoria financeira atualizada com sucesso.'

    def form_valid(self, form):
        antes = _snapshot_categoria(
            CategoriaFinanceira.objects.get(pk=self.object.pk)
        )
        response = super().form_valid(form)
        depois = _snapshot_categoria(self.object)
        _registrar_auditoria_categoria(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.UPDATE,
            categoria=self.object,
            antes=antes,
            depois=depois,
        )
        return response


class CategoriaFinanceiraDeleteView(FinanceiroDeleteMixin):
    permissao_requerida = 'financeiro.categorias.excluir'
    model = CategoriaFinanceira
    success_url = reverse_lazy('financeiro:categoria-list')
    page_title = 'Excluir Categoria Financeira'
    cancel_url = reverse_lazy('financeiro:categoria-list')
    success_message = 'Categoria financeira excluida com sucesso.'

    def form_valid(self, form):
        categoria = self.object
        antes = _snapshot_categoria(categoria)
        registro_id = categoria.pk

        with transaction.atomic():
            response = super().form_valid(form)
            AuditoriaFinanceiro.objects.create(
                acao=AuditoriaFinanceiro.AcaoAuditoria.DELETE,
                modelo='CategoriaFinanceira',
                registro_id=registro_id,
                usuario=_auditoria_usuario(self.request),
                campos_alterados=_build_auditoria_payload(antes, None),
            )

        return response


class AssinaturaInstitucionalListView(FinanceiroPermissaoMixin, ListView):
    permissao_requerida = 'financeiro.assinaturas.listar'
    model = AssinaturaInstitucional
    template_name = 'financeiro/assinatura_list.html'
    context_object_name = 'assinaturas'

    def get_queryset(self):
        queryset = super().get_queryset()
        nome = self.request.GET.get('nome', '').strip()
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        return queryset


class AssinaturaInstitucionalCreateView(FinanceiroFormMixin, CreateView):
    permissao_requerida = 'financeiro.assinaturas.criar'
    model = AssinaturaInstitucional
    form_class = AssinaturaInstitucionalForm
    template_name = 'financeiro/assinatura_form.html'
    success_url = reverse_lazy('financeiro:assinatura-list')
    page_title = 'Nova Assinatura Institucional'
    success_message = 'Assinatura institucional cadastrada com sucesso.'

    def form_valid(self, form):
        response = super().form_valid(form)
        _registrar_auditoria_assinatura(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
            assinatura=self.object,
            depois=_snapshot_assinatura(self.object),
        )
        return response


class AssinaturaInstitucionalUpdateView(FinanceiroFormMixin, UpdateView):
    permissao_requerida = 'financeiro.assinaturas.editar'
    model = AssinaturaInstitucional
    form_class = AssinaturaInstitucionalForm
    template_name = 'financeiro/assinatura_form.html'
    success_url = reverse_lazy('financeiro:assinatura-list')
    page_title = 'Editar Assinatura Institucional'
    submit_label = 'Atualizar'
    success_message = 'Assinatura institucional atualizada com sucesso.'

    def form_valid(self, form):
        antes = _snapshot_assinatura(
            AssinaturaInstitucional.objects.get(pk=self.object.pk)
        )
        response = super().form_valid(form)
        depois = _snapshot_assinatura(self.object)
        _registrar_auditoria_assinatura(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.UPDATE,
            assinatura=self.object,
            antes=antes,
            depois=depois,
        )
        return response


class AssinaturaInstitucionalDeleteView(FinanceiroDeleteMixin):
    permissao_requerida = 'financeiro.assinaturas.excluir'
    model = AssinaturaInstitucional
    success_url = reverse_lazy('financeiro:assinatura-list')
    page_title = 'Excluir Assinatura Institucional'
    cancel_url = reverse_lazy('financeiro:assinatura-list')
    success_message = 'Assinatura institucional excluida com sucesso.'

    def form_valid(self, form):
        assinatura = self.object
        antes = _snapshot_assinatura(assinatura)
        registro_id = assinatura.pk

        with transaction.atomic():
            response = super().form_valid(form)
            AuditoriaFinanceiro.objects.create(
                acao=AuditoriaFinanceiro.AcaoAuditoria.DELETE,
                modelo='AssinaturaInstitucional',
                registro_id=registro_id,
                usuario=_auditoria_usuario(self.request),
                campos_alterados=_build_auditoria_payload(antes, None),
            )

        return response


class ConfiguracaoInstitucionalListView(FinanceiroPermissaoMixin, ListView):
    permissao_requerida = 'financeiro.configuracoes_institucionais.visualizar'
    model = ConfiguracaoInstitucional
    template_name = 'financeiro/configuracao_institucional_list.html'
    context_object_name = 'configuracoes'

    def get_queryset(self):
        queryset = super().get_queryset()
        nome = self.request.GET.get('nome_instituicao', '').strip()
        if nome:
            queryset = queryset.filter(nome_instituicao__icontains=nome)
        return queryset


class ConfiguracaoInstitucionalCreateView(FinanceiroFormMixin, CreateView):
    permissao_requerida = 'financeiro.configuracoes_institucionais.criar'
    model = ConfiguracaoInstitucional
    form_class = ConfiguracaoInstitucionalForm
    template_name = 'financeiro/configuracao_institucional_form.html'
    success_url = reverse_lazy('financeiro:configuracao-institucional-list')
    page_title = 'Nova Configuracao Institucional'
    success_message = 'Configuracao institucional cadastrada com sucesso.'

    def form_valid(self, form):
        response = super().form_valid(form)
        _registrar_auditoria_configuracao(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
            configuracao=self.object,
            depois=_snapshot_configuracao(self.object),
        )
        return response


class ConfiguracaoInstitucionalUpdateView(FinanceiroFormMixin, UpdateView):
    permissao_requerida = 'financeiro.configuracoes_institucionais.editar'
    model = ConfiguracaoInstitucional
    form_class = ConfiguracaoInstitucionalForm
    template_name = 'financeiro/configuracao_institucional_form.html'
    success_url = reverse_lazy('financeiro:configuracao-institucional-list')
    page_title = 'Editar Configuracao Institucional'
    submit_label = 'Atualizar'
    success_message = 'Configuracao institucional atualizada com sucesso.'

    def form_valid(self, form):
        antes = _snapshot_configuracao(
            ConfiguracaoInstitucional.objects.get(pk=self.object.pk)
        )
        response = super().form_valid(form)
        depois = _snapshot_configuracao(self.object)
        _registrar_auditoria_configuracao(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.UPDATE,
            configuracao=self.object,
            antes=antes,
            depois=depois,
        )
        return response


class ConfiguracaoInstitucionalDeleteView(FinanceiroDeleteMixin):
    permissao_requerida = 'financeiro.configuracoes_institucionais.excluir'
    model = ConfiguracaoInstitucional
    success_url = reverse_lazy('financeiro:configuracao-institucional-list')
    page_title = 'Excluir Configuracao Institucional'
    cancel_url = reverse_lazy('financeiro:configuracao-institucional-list')
    success_message = 'Configuracao institucional excluida com sucesso.'

    def form_valid(self, form):
        configuracao = self.object
        antes = _snapshot_configuracao(configuracao)
        registro_id = configuracao.pk

        with transaction.atomic():
            response = super().form_valid(form)
            AuditoriaFinanceiro.objects.create(
                acao=AuditoriaFinanceiro.AcaoAuditoria.DELETE,
                modelo='ConfiguracaoInstitucional',
                registro_id=registro_id,
                usuario=_auditoria_usuario(self.request),
                campos_alterados=_build_auditoria_payload(antes, None),
            )

        return response


class LancamentoFinanceiroListView(FinanceiroPermissaoMixin, ListView):
    permissao_requerida = 'financeiro.lancamentos.listar'
    model = LancamentoFinanceiro
    template_name = 'financeiro/lancamento_list.html'
    context_object_name = 'lancamentos'

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'conta',
            'conta_destino',
            'pessoa',
            'categoria',
            'centro_custo',
        )
        queryset = _filtrar_lancamentos_por_parametros(queryset, self.request.GET)
        return queryset.annotate(
            data_principal_ordenacao=Coalesce('data_pagamento', 'data_competencia')
        ).order_by('-data_principal_ordenacao', '-pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ordenacao_atual = _resolver_ordenacao_lancamentos_listagem(
            self.request.GET.get('ordenacao')
        )
        por_pagina = _resolver_lancamentos_por_pagina(self.request)
        context['contas_disponiveis'] = ContaFinanceira.objects.order_by('nome')
        context['pessoas_disponiveis'] = PessoaFinanceira.objects.order_by('nome')
        context['categorias_disponiveis'] = CategoriaFinanceira.objects.order_by('tipo', 'nome')
        lancamentos_visuais = _ordenar_lancamentos_visuais_listagem(
            _montar_lancamentos_visuais_listagem(context['lancamentos']),
            ordenacao_atual,
        )
        conta_referencia_id = _resolver_conta_referencia_lancamentos_listagem(self.request)
        for lancamento_visual in lancamentos_visuais:
            componentes_resumo = _componentes_resumo_lancamento_visual_listagem(
                lancamento_visual,
                conta_referencia_id=conta_referencia_id,
            )
            lancamento_visual['resumo_componentes'] = componentes_resumo
            lancamento_visual['valor_liquido'] = componentes_resumo['saldo_liquido']
            lancamento_visual['valor_liquido_formatado'] = _formatar_moeda_brl(
                componentes_resumo['saldo_liquido']
            )
        paginator = Paginator(lancamentos_visuais, por_pagina)
        pagina_atual = self.request.GET.get('page') or 1
        try:
            page_obj = paginator.page(pagina_atual)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        lancamentos_visuais_pagina = list(page_obj.object_list)
        context['lancamentos_visuais'] = lancamentos_visuais_pagina
        context['totalizadores_lancamentos'] = _montar_resumo_financeiro_lancamentos_visuais(
            lancamentos_visuais,
            conta_referencia_id=conta_referencia_id,
        )
        context['quantidade_lancamentos_pagina'] = len(lancamentos_visuais_pagina)
        context['paginator'] = paginator
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context['por_pagina'] = por_pagina
        context['por_pagina_opcoes'] = LANCAMENTO_LISTAGEM_POR_PAGINA_OPCOES
        context['paginacao_lancamentos_urls'] = {
            'primeira': _montar_url_lancamentos_com_query(self.request, page=1),
            'anterior': _montar_url_lancamentos_com_query(self.request, page=page_obj.previous_page_number()) if page_obj.has_previous() else '',
            'proxima': _montar_url_lancamentos_com_query(self.request, page=page_obj.next_page_number()) if page_obj.has_next() else '',
            'ultima': _montar_url_lancamentos_com_query(self.request, page=paginator.num_pages),
        }
        context.update(_montar_contexto_ordenacao_lancamentos_listagem(
            self.request,
            ordenacao_atual,
        ))
        context.update(_montar_contexto_colunas_lancamentos(self.request))
        context['filtros_lancamento_ativos'] = _request_possui_parametros_get(
            self.request,
            (
                'descricao',
                'numero_documento',
                'tipo',
                'status',
                'data_inicial',
                'data_final',
                'conta',
                'pessoa',
                'categoria',
            ),
        )
        exportacao_url = reverse('financeiro:lancamento-exportacao')
        filtros_ativos = self.request.GET.urlencode()
        if filtros_ativos:
            exportacao_url = f'{exportacao_url}?{filtros_ativos}'
        context['exportacao_lancamentos_url'] = exportacao_url
        return context


class LancamentoFinanceiroImportacaoExportacaoView(FinanceiroPermissaoMixin, TemplateView):
    permissao_requerida = 'financeiro.lancamentos.importar'
    template_name = 'financeiro/lancamento_importacao_exportacao.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Importacoes do Financeiro'
        context['resultado_importacao_validacao'] = kwargs.get('resultado_importacao_validacao')
        context['resultado_importacao_erros_json'] = kwargs.get('resultado_importacao_erros_json', '')
        context['resultado_importacao_titulo'] = kwargs.get('resultado_importacao_titulo', '')
        context['resultado_importacao_slug'] = kwargs.get('resultado_importacao_slug', '')
        context['cadastro_auxiliar_planilhas_base'] = [
            {
                **item,
                'descricao': CADASTRO_AUXILIAR_PLANILHAS_BASE[item['slug']]['descricao'],
                'pode_importar': _usuario_pode_importar_cadastro_auxiliar(self.request.user, item['slug']),
                'download_url': reverse(
                    'financeiro:lancamento-importacao-modelo-cadastro-auxiliar',
                    kwargs={'slug': item['slug']},
                ),
            }
            for item in CADASTRO_AUXILIAR_PLANILHAS_BASE_ORDEM
        ]
        return context

    def _render_resultado_importacao(self, *, resultado_importacao_validacao, titulo, slug=''):
        return self.render_to_response(
            self.get_context_data(
                resultado_importacao_validacao=resultado_importacao_validacao,
                resultado_importacao_erros_json=(
                    _serializar_erros_importacao_lancamentos(resultado_importacao_validacao['erros'])
                    if resultado_importacao_validacao['erros']
                    else ''
                ),
                resultado_importacao_titulo=titulo,
                resultado_importacao_slug=slug,
            )
        )

    def _processar_importacao_lancamentos(self, request, arquivo_importacao):
        if _dominio_importacao_ja_possui_registros('lancamentos'):
            messages.error(request, _mensagem_bloqueio_importacao_dominio('lancamentos'))
            return self.get(request)

        erros_estrutura = _validar_estrutura_planilha_importacao_lancamentos_xlsx(arquivo_importacao)
        if erros_estrutura:
            for erro in erros_estrutura:
                messages.error(request, erro)
            return self.get(request)

        resultado_importacao_validacao = _validar_conteudo_planilha_importacao_lancamentos_xlsx(
            arquivo_importacao
        )

        if resultado_importacao_validacao['linhas_lidas'] == 0:
            messages.warning(
                request,
                'A estrutura da planilha esta correta, mas nao ha linhas preenchidas na aba Modelo.',
            )
        elif resultado_importacao_validacao['linhas_invalidas']:
            messages.error(
                request,
                'Nenhuma linha foi importada porque a planilha ainda tem erros. '
                'Ajuste os campos abaixo e envie novamente.',
            )
        else:
            try:
                with transaction.atomic():
                    total_importado = 0
                    for operacao in resultado_importacao_validacao['operacoes_validas']:
                        for lancamento in operacao['lancamentos']:
                            lancamento.save()
                            _registrar_auditoria_lancamento(
                                request=request,
                                acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
                                lancamento=lancamento,
                                antes=None,
                                depois=_snapshot_lancamento(lancamento),
                            )
                            total_importado += 1
                resultado_importacao_validacao['linhas_importadas'] = resultado_importacao_validacao['linhas_validas']
                messages.success(
                    request,
                    'Importacao concluida com sucesso. '
                    f'{resultado_importacao_validacao["linhas_importadas"]} linhas importadas, gerando {total_importado} lancamentos.',
                )
            except ValidationError:
                resultado_importacao_validacao['linhas_importadas'] = 0
                messages.error(
                    request,
                    'Nenhuma linha foi importada porque a planilha ficou inconsistente durante '
                    'a gravacao. Revise o arquivo e envie novamente.',
                )

        return self._render_resultado_importacao(
            resultado_importacao_validacao=resultado_importacao_validacao,
            titulo='Importacao de lancamentos',
            slug='lancamentos',
        )

    def _processar_importacao_cadastro_auxiliar(self, request, arquivo_importacao, slug: str):
        if slug not in AUXILIAR_IMPORTACAO_PROCESSADORES:
            messages.error(request, 'Tipo de importacao auxiliar invalido.')
            return self.get(request)

        if not _usuario_pode_importar_cadastro_auxiliar(request.user, slug):
            raise PermissionDenied

        if _dominio_importacao_ja_possui_registros(slug):
            messages.error(request, _mensagem_bloqueio_importacao_dominio(slug))
            return self.get(request)

        configuracao = CADASTRO_AUXILIAR_PLANILHAS_BASE[slug]
        erros_estrutura = _validar_estrutura_planilha_modelo_xlsx(
            arquivo_importacao,
            configuracao['colunas'],
        )
        if erros_estrutura:
            for erro in erros_estrutura:
                messages.error(request, erro)
            return self.get(request)

        resultado_importacao_validacao = AUXILIAR_IMPORTACAO_PROCESSADORES[slug]['validar'](
            arquivo_importacao
        )

        if resultado_importacao_validacao['linhas_lidas'] == 0:
            messages.warning(
                request,
                'A estrutura da planilha esta correta, mas nao ha linhas preenchidas na aba Modelo.',
            )
        elif resultado_importacao_validacao['linhas_invalidas']:
            messages.error(
                request,
                'Nenhuma linha foi importada porque a planilha ainda tem erros. '
                'Ajuste os campos abaixo e envie novamente.',
            )
        else:
            try:
                total_importado = AUXILIAR_IMPORTACAO_PROCESSADORES[slug]['executar'](
                    resultado_importacao_validacao['registros_validos'],
                    request,
                )
                resultado_importacao_validacao['linhas_importadas'] = total_importado
                messages.success(
                    request,
                    'Importacao concluida com sucesso. '
                    f'{total_importado} registros de {configuracao["titulo"].lower()} importados.',
                )
            except ValidationError:
                resultado_importacao_validacao['linhas_importadas'] = 0
                messages.error(
                    request,
                    'Nenhuma linha foi importada porque a planilha ficou inconsistente durante '
                    'a gravacao. Revise o arquivo e envie novamente.',
                )

        return self._render_resultado_importacao(
            resultado_importacao_validacao=resultado_importacao_validacao,
            titulo=f'Importacao de {configuracao["titulo"].lower()}',
            slug=slug,
        )

    def post(self, request, *args, **kwargs):
        tipo_importacao = (request.POST.get('tipo_importacao') or 'lancamentos').strip()
        arquivo_importacao = request.FILES.get('arquivo_importacao')
        if not arquivo_importacao:
            messages.error(request, 'Selecione uma planilha XLSX antes de importar.')
            return self.get(request, *args, **kwargs)

        if tipo_importacao == 'lancamentos':
            return self._processar_importacao_lancamentos(request, arquivo_importacao)

        return self._processar_importacao_cadastro_auxiliar(
            request,
            arquivo_importacao,
            tipo_importacao,
        )

        arquivo_importacao = request.FILES.get('arquivo_importacao')
        if not arquivo_importacao:
            messages.error(request, 'Selecione uma planilha XLSX antes de importar.')
            return self.get(request, *args, **kwargs)

        erros_estrutura = _validar_estrutura_planilha_importacao_lancamentos_xlsx(arquivo_importacao)
        if erros_estrutura:
            for erro in erros_estrutura:
                messages.error(request, erro)
            return self.get(request, *args, **kwargs)

        resultado_importacao_validacao = _validar_conteudo_planilha_importacao_lancamentos_xlsx(
            arquivo_importacao
        )

        if resultado_importacao_validacao['linhas_lidas'] == 0:
            messages.warning(
                request,
                'A estrutura da planilha estÃ¡ correta, mas nÃ£o hÃ¡ linhas preenchidas na aba Modelo.',
            )
        elif resultado_importacao_validacao['linhas_invalidas']:
            messages.error(
                request,
                'Nenhuma linha foi importada porque a planilha ainda tem erros. '
                'Ajuste os campos abaixo e envie novamente.',
            )
        else:
            try:
                with transaction.atomic():
                    for lancamento in resultado_importacao_validacao['lancamentos_validos']:
                        lancamento.save()
                        _registrar_auditoria_lancamento(
                            request=request,
                            acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
                            lancamento=lancamento,
                            antes=None,
                            depois=_snapshot_lancamento(lancamento),
                        )
                resultado_importacao_validacao['linhas_importadas'] = (
                    resultado_importacao_validacao['linhas_validas']
                )
                messages.success(
                    request,
                    'ImportaÃ§Ã£o concluÃ­da com sucesso. '
                    f'{resultado_importacao_validacao["linhas_importadas"]} '
                    'lanÃ§amentos importados.',
                )
            except ValidationError:
                resultado_importacao_validacao['linhas_importadas'] = 0
                messages.error(
                    request,
                    'Nenhuma linha foi importada porque a planilha ficou inconsistente durante '
                    'a gravaÃ§Ã£o. Revise o arquivo e envie novamente.',
                )

        return self.render_to_response(
            self.get_context_data(
                resultado_importacao_validacao=resultado_importacao_validacao,
                resultado_importacao_erros_json=(
                    _serializar_erros_importacao_lancamentos(
                        resultado_importacao_validacao['erros']
                    )
                    if resultado_importacao_validacao['erros']
                    else ''
                ),
            )
        )


class LancamentoFinanceiroImportacaoInconsistenciasView(FinanceiroPermissaoMixin, View):
    permissao_requerida = 'financeiro.lancamentos.baixar_inconsistencias'

    def post(self, request, *args, **kwargs):
        erros = _normalizar_erros_importacao_lancamentos_relatorio(
            request.POST.get('erros_importacao', '')
        )

        if not erros:
            messages.warning(
                request,
                'NÃ£o hÃ¡ inconsistÃªncias disponÃ­veis para baixar neste momento. '
                'Envie a planilha novamente para gerar o relatÃ³rio.',
            )
            return redirect('financeiro:lancamento-importacao-exportacao')

        response = HttpResponse(
            _gerar_relatorio_inconsistencias_importacao_lancamentos_xlsx(erros),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = (
            'attachment; filename="relatorio_inconsistencias_importacao_financeiro.xlsx"'
        )

        return response


class LancamentoFinanceiroImportacaoModeloView(FinanceiroPermissaoMixin, View):
    permissao_requerida = 'financeiro.lancamentos.baixar_modelo'

    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            _gerar_planilha_modelo_lancamentos_xlsx(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="modelo_importacao_lancamentos.xlsx"'

        return response


class CadastroAuxiliarPlanilhaBaseView(FinanceiroPermissaoMixin, View):
    permissao_requerida = 'financeiro.lancamentos.baixar_modelo'

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        if slug not in CADASTRO_AUXILIAR_PLANILHAS_BASE:
            return redirect('financeiro:lancamento-importacao-exportacao')
        if not _usuario_pode_importar_cadastro_auxiliar(request.user, slug):
            raise PermissionDenied

        configuracao = CADASTRO_AUXILIAR_PLANILHAS_BASE[slug]
        response = HttpResponse(
            _gerar_planilha_base_cadastro_auxiliar_xlsx(slug),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{configuracao["arquivo"]}"'
        return response


class ContaFinanceiraExportacaoView(FinanceiroPermissaoMixin, View):
    permissao_requerida = 'financeiro.contas.listar'

    def get(self, request, *args, **kwargs):
        queryset = ContaFinanceira.objects.all()
        nome = request.GET.get('nome', '').strip()
        ativa = request.GET.get('ativa', '').strip()
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if ativa == 'ativas':
            queryset = queryset.filter(ativa=True)
        elif ativa == 'inativas':
            queryset = queryset.filter(ativa=False)

        arquivo_exportacao = _gerar_planilha_exportacao_cadastro_auxiliar_xlsx(
            'contas',
            queryset.order_by('nome', 'pk'),
        )
        response = HttpResponse(
            arquivo_exportacao,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="exportacao_contas_financeiras.xlsx"'
        return response


class PessoaFinanceiraExportacaoView(FinanceiroPermissaoMixin, View):
    permissao_requerida = 'financeiro.pessoas.listar'

    def get(self, request, *args, **kwargs):
        queryset = PessoaFinanceira.objects.all()
        nome = request.GET.get('nome', '').strip()
        codigo = request.GET.get('codigo', '').strip()
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if codigo:
            queryset = queryset.filter(codigo__icontains=codigo)

        arquivo_exportacao = _gerar_planilha_exportacao_cadastro_auxiliar_xlsx(
            'pessoas',
            queryset.order_by('nome', 'pk'),
        )
        response = HttpResponse(
            arquivo_exportacao,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="exportacao_favorecidos_financeiros.xlsx"'
        return response


class CentroCustoExportacaoView(FinanceiroPermissaoMixin, View):
    permissao_requerida = 'financeiro.centros_custo.listar'

    def get(self, request, *args, **kwargs):
        queryset = CentroCusto.objects.all()
        codigo = request.GET.get('codigo', '').strip()
        nome = request.GET.get('nome', '').strip()
        if codigo:
            queryset = queryset.filter(codigo__icontains=codigo)
        if nome:
            queryset = queryset.filter(nome__icontains=nome)

        arquivo_exportacao = _gerar_planilha_exportacao_cadastro_auxiliar_xlsx(
            'centros-custo',
            queryset.order_by('nome', 'pk'),
        )
        response = HttpResponse(
            arquivo_exportacao,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="exportacao_centros_custo.xlsx"'
        return response


class CategoriaFinanceiraExportacaoView(FinanceiroPermissaoMixin, View):
    permissao_requerida = 'financeiro.categorias.listar'

    def get(self, request, *args, **kwargs):
        queryset = CategoriaFinanceira.objects.select_related('categoria_pai')
        nome = request.GET.get('nome', '').strip()
        tipo = request.GET.get('tipo', '').strip()
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        arquivo_exportacao = _gerar_planilha_exportacao_cadastro_auxiliar_xlsx(
            'categorias',
            queryset.order_by('tipo', 'nome', 'pk'),
        )
        response = HttpResponse(
            arquivo_exportacao,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="exportacao_categorias_financeiras.xlsx"'
        return response


class LancamentoFinanceiroExportacaoView(FinanceiroPermissaoMixin, View):
    permissao_requerida = 'financeiro.lancamentos.exportar'

    def get(self, request, *args, **kwargs):
        lancamentos_filtrados = list(
            _filtrar_lancamentos_por_parametros(
                LancamentoFinanceiro.objects.select_related(
                    'pessoa',
                    'categoria',
                    'centro_custo',
                    'conta',
                    'conta_destino',
                ),
                request.GET,
            )
            .order_by('-data_pagamento', '-data_competencia', '-criado_em', '-pk')
        )
        grupos_rateio = sorted({
            (lancamento.grupo_rateio or '').strip()
            for lancamento in lancamentos_filtrados
            if lancamento.com_rateio and (lancamento.grupo_rateio or '').strip()
        })
        if grupos_rateio:
            linhas_grupo = list(
                LancamentoFinanceiro.objects.select_related(
                    'pessoa',
                    'categoria',
                    'centro_custo',
                    'conta',
                    'conta_destino',
                )
                .filter(com_rateio=True, grupo_rateio__in=grupos_rateio)
                .order_by('-data_pagamento', '-data_competencia', '-criado_em', '-pk')
            )
            lancamentos_sem_rateio = [
                lancamento
                for lancamento in lancamentos_filtrados
                if not lancamento.com_rateio or not (lancamento.grupo_rateio or '').strip()
            ]
            lancamentos = lancamentos_sem_rateio + linhas_grupo
        else:
            lancamentos = lancamentos_filtrados

        try:
            arquivo_exportacao = _gerar_planilha_exportacao_lancamentos_xlsx(lancamentos)
        except ValidationError as error:
            for mensagem in error.messages:
                messages.error(request, mensagem)
            url_listagem = reverse('financeiro:lancamento-list')
            filtros = request.GET.urlencode()
            if filtros:
                return redirect(f'{url_listagem}?{filtros}')
            return redirect(url_listagem)

        response = HttpResponse(
            arquivo_exportacao,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="exportacao_lancamentos.xlsx"'

        return response


class LancamentoFinanceiroAcoesLoteView(FinanceiroPermissaoMixin, View):
    permissao_requerida = 'financeiro.lancamentos.acoes_em_lote_status'

    def get_permissao_requerida(self) -> str:
        if (self.request.POST.get('acao_lote') or '').strip() == 'excluir':
            return 'financeiro.lancamentos.acoes_em_lote_excluir'
        if (self.request.POST.get('acao_lote') or '').strip() in {
            'emitir_recibos',
            'recibo_lote',
            'recibos_lote_por_favorecido',
        }:
            return 'financeiro.lancamentos.emitir_recibo'
        return self.permissao_requerida

    def _redirect_listagem(self, request):
        filtros_retorno = (request.POST.get('filtros_retorno') or '').strip()
        url_listagem = reverse('financeiro:lancamento-list')
        if filtros_retorno:
            return redirect(f'{url_listagem}?{filtros_retorno}')
        return redirect(url_listagem)

    def post(self, request, *args, **kwargs):
        acao_lote = (request.POST.get('acao_lote') or '').strip()
        novo_status = (request.POST.get('novo_status_lote') or '').strip()
        tokens_selecao = [
            token
            for token in request.POST.getlist('lancamentos_selecionados')
            if (token or '').strip()
        ]

        if not tokens_selecao:
            messages.warning(request, 'Selecione pelo menos um lanÃ§amento para aplicar uma aÃ§Ã£o em lote.')
            return self._redirect_listagem(request)

        lancamentos = _resolver_lancamentos_para_acoes_em_lote(tokens_selecao)
        if not lancamentos:
            messages.warning(request, 'Nenhum lanÃ§amento selecionado foi encontrado para aÃ§Ã£o em lote.')
            return self._redirect_listagem(request)

        if acao_lote == 'excluir':
            with transaction.atomic():
                for lancamento in lancamentos:
                    antes = _snapshot_lancamento(lancamento)
                    registro_id = lancamento.pk
                    lancamento.delete()
                    AuditoriaFinanceiro.objects.create(
                        acao=AuditoriaFinanceiro.AcaoAuditoria.DELETE,
                        modelo='LancamentoFinanceiro',
                        registro_id=registro_id,
                        usuario=_auditoria_usuario(request),
                        campos_alterados=_build_auditoria_payload(antes, None),
                    )

            quantidade = len(lancamentos)
            sufixo = '' if quantidade == 1 else 's'
            messages.success(
                request,
                f'{quantidade} lanÃ§amento{sufixo} excluÃ­do{sufixo} com sucesso.',
            )
            return self._redirect_listagem(request)

        if acao_lote == 'alterar_status':
            status_validos = {
                escolha
                for escolha, _ in LancamentoFinanceiro.StatusLancamento.choices
            }
            if novo_status not in status_validos:
                messages.warning(request, 'Selecione um status vÃ¡lido para aplicar aos lanÃ§amentos marcados.')
                return self._redirect_listagem(request)

            try:
                with transaction.atomic():
                    for lancamento in lancamentos:
                        antes = _snapshot_lancamento(lancamento)
                        lancamento.status = novo_status
                        lancamento.full_clean()
                        lancamento.save()
                        _registrar_auditoria_lancamento(
                            request=request,
                            acao=AuditoriaFinanceiro.AcaoAuditoria.UPDATE,
                            lancamento=lancamento,
                            antes=antes,
                            depois=_snapshot_lancamento(lancamento),
                        )
            except ValidationError:
                messages.error(
                    request,
                    'Nenhum status foi alterado porque pelo menos um lanÃ§amento selecionado '
                    'ficou inconsistente na validaÃ§Ã£o. Revise os itens marcados e tente novamente.',
                )
                return self._redirect_listagem(request)

            quantidade = len(lancamentos)
            sufixo = '' if quantidade == 1 else 's'
            messages.success(
                request,
                f'Status atualizado para {quantidade} lanÃ§amento{sufixo}.',
            )
            return self._redirect_listagem(request)

        if acao_lote in {'emitir_recibos', 'recibo_lote', 'recibos_lote_por_favorecido'}:
            pessoas_ids = {lancamento.pessoa_id for lancamento in lancamentos}
            if None in pessoas_ids:
                messages.warning(
                    request,
                    'Selecione apenas lancamentos com favorecido para emitir recibos em lote.',
                )
                return self._redirect_listagem(request)
            if any(lancamento.tipo != LancamentoFinanceiro.TipoLancamento.RECEITA for lancamento in lancamentos):
                messages.warning(
                    request,
                    'Recibos em lote so podem ser emitidos para lancamentos do tipo receita.',
                )
                return self._redirect_listagem(request)
            ids_param = ','.join(str(lancamento.pk) for lancamento in lancamentos)
            filtros_retorno = (request.POST.get('filtros_retorno') or '').strip()
            query_params = {'ids': ids_param}
            if filtros_retorno:
                query_params['filtros'] = filtros_retorno
            url_recibos = reverse('financeiro:lancamento-recibos-por-favorecido')
            return redirect(f'{url_recibos}?{urlencode(query_params)}')

        messages.warning(request, 'Escolha uma aÃ§Ã£o em lote vÃ¡lida para os lanÃ§amentos selecionados.')
        return self._redirect_listagem(request)


class LancamentoFinanceiroCreateView(FinanceiroFormMixin, CreateView):
    permissao_requerida = 'financeiro.lancamentos.criar'
    model = LancamentoFinanceiro
    form_class = LancamentoFinanceiroForm
    template_name = 'financeiro/lancamento_form.html'
    success_url = reverse_lazy('financeiro:lancamento-list')
    page_title = 'Novo Lancamento Financeiro'
    success_message = 'Lancamento financeiro cadastrado com sucesso.'
    allow_save_and_stay = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rateio_categoria_opcoes'] = [
            {'id': categoria.pk, 'label': str(categoria), 'tipo': categoria.tipo}
            for categoria in categorias_vinculaveis_queryset()
        ]
        return context

    def form_valid(self, form):
        if not form.cleaned_data.get('lancamento_com_rateio'):
            with transaction.atomic():
                response = super().form_valid(form)
                if form.cleaned_data.get('salvar_como_regra_automatica'):
                    _criar_regra_automatica_lancamento(self.object)
                _registrar_auditoria_lancamento(
                    request=self.request,
                    acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
                    lancamento=self.object,
                    depois=_snapshot_lancamento(self.object),
                )
            return response

        rateio_linhas = form.cleaned_data.get('rateio_linhas') or []
        grupo_rateio = form.cleaned_data.get('grupo_rateio') or uuid4().hex
        numero_documento = (form.cleaned_data.get('numero_documento') or '').strip()

        if not numero_documento:
            numero_documento = LancamentoFinanceiro(
                data_competencia=form.cleaned_data['data_competencia']
            )._gerar_numero_documento()

        dados_comuns = {
            'descricao': form.cleaned_data['descricao'],
            'tipo': form.cleaned_data['tipo'],
            'status': form.cleaned_data['status'],
            'data_competencia': form.cleaned_data['data_competencia'],
            'data_pagamento': form.cleaned_data.get('data_pagamento'),
            'numero_documento': numero_documento,
            'pessoa': form.cleaned_data.get('pessoa'),
            'centro_custo': form.cleaned_data.get('centro_custo'),
            'conta': form.cleaned_data['conta'],
            'conta_destino': form.cleaned_data.get('conta_destino'),
            'observacoes': form.cleaned_data.get('observacoes', ''),
            'com_rateio': True,
            'grupo_rateio': grupo_rateio,
        }

        lancamentos_criados: list[LancamentoFinanceiro] = []
        with transaction.atomic():
            for linha in rateio_linhas:
                lancamento = LancamentoFinanceiro.objects.create(
                    **dados_comuns,
                    categoria=linha['categoria'],
                    valor=linha['valor'],
                )
                lancamentos_criados.append(lancamento)
                _registrar_auditoria_lancamento(
                    request=self.request,
                    acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
                    lancamento=lancamento,
                    depois=_snapshot_lancamento(lancamento),
                )

        if lancamentos_criados:
            self.object = lancamentos_criados[0]

        messages.success(
            self.request,
            f'Lancamento com rateio cadastrado com sucesso em {len(lancamentos_criados)} linhas.',
        )
        if self._should_save_and_stay():
            return redirect(self.get_save_and_stay_url())
        return redirect(self.get_success_url())


class LancamentoFinanceiroCloneView(LancamentoFinanceiroCreateView):
    permissao_requerida = 'financeiro.lancamentos.clonar'
    page_title = 'Clonar Lancamento Financeiro'
    submit_label = 'Salvar clone'
    success_message = 'Lancamento financeiro clonado com sucesso.'
    allow_save_and_stay = False

    def dispatch(self, request, *args, **kwargs):
        self.lancamento_origem = get_object_or_404(
            LancamentoFinanceiro.objects.select_related(
                'conta',
                'conta_destino',
                'pessoa',
                'categoria',
                'centro_custo',
            ),
            pk=kwargs['pk'],
        )
        if self.lancamento_origem.com_rateio or self.lancamento_origem.grupo_rateio:
            messages.warning(
                request,
                'Lancamentos com rateio ainda nao podem ser clonados nesta etapa. O registro original permaneceu inalterado.',
            )
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial.update(
            {
                'descricao': self.lancamento_origem.descricao,
                'tipo': self.lancamento_origem.tipo,
                'status': self.lancamento_origem.status,
                'valor': self.lancamento_origem.valor,
                'data_competencia': self.lancamento_origem.data_competencia,
                'data_pagamento': self.lancamento_origem.data_pagamento,
                'conta': self.lancamento_origem.conta,
                'observacoes': self.lancamento_origem.observacoes,
            }
        )

        if self.lancamento_origem.tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
            initial['conta_destino'] = self.lancamento_origem.conta_destino
            return initial

        initial.update(
            {
                'pessoa': self.lancamento_origem.pessoa,
                'categoria': self.lancamento_origem.categoria,
                'centro_custo': self.lancamento_origem.centro_custo,
            }
        )
        return initial


class LancamentoFinanceiroGrupoRateioCloneView(LancamentoFinanceiroCreateView):
    permissao_requerida = 'financeiro.lancamentos.clonar'
    page_title = 'Clonar Lancamento Financeiro com Rateio'
    submit_label = 'Salvar clone'
    allow_save_and_stay = False

    def _get_grupo_origem_info(self) -> dict[str, object]:
        if hasattr(self, '_grupo_origem_info_cache'):
            return self._grupo_origem_info_cache

        grupo_rateio = (self.kwargs.get('grupo_rateio') or '').strip()
        lancamentos = list(
            LancamentoFinanceiro.objects.filter(
                com_rateio=True,
                grupo_rateio=grupo_rateio,
            )
            .select_related(
                'conta',
                'conta_destino',
                'pessoa',
                'categoria',
                'centro_custo',
            )
            .order_by('pk')
        )

        erro = ''
        if not grupo_rateio:
            erro = 'Grupo de rateio invalido para clonagem.'
        elif not lancamentos:
            erro = 'Nenhum lancamento rateado foi encontrado para este grupo.'
        elif len(lancamentos) < 2:
            erro = 'Este grupo nao possui linhas suficientes para clonagem.'
        else:
            numeros_documento = {(lancamento.numero_documento or '').strip() for lancamento in lancamentos}
            numeros_documento.discard('')
            if len(numeros_documento) > 1:
                erro = 'Este grupo possui numeros de documento divergentes e precisa de regularizacao antes da clonagem.'

        self._grupo_origem_info_cache = {
            'grupo_rateio': grupo_rateio,
            'lancamentos': lancamentos,
            'erro': erro,
            'representante': lancamentos[0] if lancamentos else None,
        }
        return self._grupo_origem_info_cache

    def _get_grupo_origem_lancamentos(self) -> list[LancamentoFinanceiro]:
        return self._get_grupo_origem_info()['lancamentos']

    def dispatch(self, request, *args, **kwargs):
        grupo_info = self._get_grupo_origem_info()
        if grupo_info['erro']:
            messages.warning(
                request,
                f"{grupo_info['erro']} O clone do grupo nao foi aberto e o documento original permaneceu inalterado.",
            )
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        lancamento_origem = self._get_grupo_origem_lancamentos()[0]
        initial.update(
            {
                'descricao': lancamento_origem.descricao,
                'tipo': lancamento_origem.tipo,
                'status': lancamento_origem.status,
                'data_competencia': lancamento_origem.data_competencia,
                'data_pagamento': lancamento_origem.data_pagamento,
                'pessoa': lancamento_origem.pessoa,
                'centro_custo': lancamento_origem.centro_custo,
                'conta': lancamento_origem.conta,
                'conta_destino': (
                    lancamento_origem.conta_destino
                    if lancamento_origem.tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA
                    else None
                ),
                'observacoes': lancamento_origem.observacoes,
                'lancamento_com_rateio': True,
                'valor_total_documento': sum(
                    (lancamento.valor for lancamento in self._get_grupo_origem_lancamentos()),
                    Decimal('0.00'),
                ),
            }
        )
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if form.is_bound:
            return form

        form.fields['lancamento_com_rateio'].initial = True
        form.initial['lancamento_com_rateio'] = True

        valor_total_documento = sum(
            (lancamento.valor for lancamento in self._get_grupo_origem_lancamentos()),
            Decimal('0.00'),
        )
        form.fields['valor_total_documento'].initial = valor_total_documento
        form.initial['valor_total_documento'] = valor_total_documento
        form.rateio_linhas_iniciais = [
            {
                'categoria': str(lancamento.categoria_id or ''),
                'valor': str(lancamento.valor or ''),
            }
            for lancamento in self._get_grupo_origem_lancamentos()
        ]
        return form


class LancamentoFinanceiroUpdateView(FinanceiroFormMixin, UpdateView):
    permissao_requerida = 'financeiro.lancamentos.editar'
    model = LancamentoFinanceiro
    form_class = LancamentoFinanceiroForm
    template_name = 'financeiro/lancamento_form.html'
    success_url = reverse_lazy('financeiro:lancamento-list')
    page_title = 'Editar Lancamento Financeiro'
    submit_label = 'Atualizar'
    success_message = 'Lancamento financeiro atualizado com sucesso.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rateio_categoria_opcoes'] = [
            {'id': categoria.pk, 'label': str(categoria), 'tipo': categoria.tipo}
            for categoria in categorias_vinculaveis_queryset()
        ]
        return context

    def form_valid(self, form):
        antes = _snapshot_lancamento(
            LancamentoFinanceiro.objects.get(pk=self.object.pk)
        )
        response = super().form_valid(form)
        depois = _snapshot_lancamento(self.object)
        _registrar_auditoria_lancamento(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.UPDATE,
            lancamento=self.object,
            antes=antes,
            depois=depois,
        )
        return response


class LancamentoFinanceiroGrupoRateioUpdateView(FinanceiroFormMixin, UpdateView):
    permissao_requerida = 'financeiro.lancamentos.editar_rateio'
    model = LancamentoFinanceiro
    form_class = LancamentoFinanceiroGrupoRateioForm
    template_name = 'financeiro/lancamento_rateio_grupo_form.html'
    success_url = reverse_lazy('financeiro:lancamento-list')
    page_title = 'Editar Lancamento Financeiro'
    submit_label = 'Atualizar'

    def _get_grupo_info(self) -> dict[str, object]:
        if hasattr(self, '_grupo_info_cache'):
            return self._grupo_info_cache

        grupo_rateio = (self.kwargs.get('grupo_rateio') or '').strip()
        lancamentos = list(
            LancamentoFinanceiro.objects.filter(
                com_rateio=True,
                grupo_rateio=grupo_rateio,
            )
            .select_related(
                'conta',
                'conta_destino',
                'pessoa',
                'categoria',
                'centro_custo',
            )
            .order_by('pk')
        )

        erro = ''
        erro_codigo = ''
        if not grupo_rateio:
            erro = 'Grupo de rateio invalido para edicao coordenada.'
            erro_codigo = 'grupo_invalido'
        elif not lancamentos:
            erro = 'Nenhum lancamento rateado foi encontrado para este grupo.'
            erro_codigo = 'grupo_nao_encontrado'
        elif len(lancamentos) < 2:
            erro = 'Este grupo nao possui linhas suficientes para edicao coordenada.'
            erro_codigo = 'grupo_insuficiente'
        else:
            numeros_documento = {(lancamento.numero_documento or '').strip() for lancamento in lancamentos}
            numeros_documento.discard('')
            if len(numeros_documento) > 1:
                erro = 'Este grupo possui numeros de documento divergentes e precisa de regularizacao antes da edicao coordenada.'
                erro_codigo = 'documento_divergente'

        self._grupo_info_cache = {
            'grupo_rateio': grupo_rateio,
            'lancamentos': lancamentos,
            'erro': erro,
            'erro_codigo': erro_codigo,
            'representante': lancamentos[0] if lancamentos else None,
        }
        return self._grupo_info_cache

    def _get_grupo_lancamentos(self) -> list[LancamentoFinanceiro]:
        return self._get_grupo_info()['lancamentos']

    def dispatch(self, request, *args, **kwargs):
        grupo_info = self._get_grupo_info()
        if grupo_info['erro']:
            erro_codigo = grupo_info.get('erro_codigo') or 'grupo_invalido'
            messages.warning(
                request,
                f"{grupo_info['erro']} O fluxo coordenado nao foi aberto para evitar alteracao insegura do grupo. Revise este caso pela edicao individual da linha representativa.",
            )
            representante = grupo_info['representante']
            if representante:
                query_params = {
                    'origem_fluxo': 'rateio_coordenado',
                    'motivo_fluxo': erro_codigo,
                }
                return_to = self._get_return_to_url()
                if return_to:
                    query_params[self.return_to_param] = return_to
                query_string = urlencode(query_params)
                return redirect(f"{reverse('financeiro:lancamento-update', kwargs={'pk': representante.pk})}?{query_string}")
            messages.warning(
                request,
                'Nao foi possivel abrir uma linha representativa para este grupo. Voce foi redirecionado para a listagem principal de lancamentos.',
            )
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self._get_grupo_lancamentos()[0]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['grupo_lancamentos'] = self._get_grupo_lancamentos()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grupo_lancamentos = self._get_grupo_lancamentos()
        context['rateio_categoria_opcoes'] = [
            {'id': categoria.pk, 'label': str(categoria), 'tipo': categoria.tipo}
            for categoria in categorias_vinculaveis_queryset()
        ]
        context['grupo_rateio'] = grupo_lancamentos[0].grupo_rateio
        context['grupo_rateio_quantidade_linhas'] = len(grupo_lancamentos)
        context['grupo_rateio_valor_total'] = sum(
            (lancamento.valor for lancamento in grupo_lancamentos),
            Decimal('0.00'),
        )
        context['grupo_rateio_linha_representativa'] = grupo_lancamentos[0]
        return context

    def form_valid(self, form):
        grupo_lancamentos = self._get_grupo_lancamentos()
        rateio_linhas = form.cleaned_data.get('rateio_linhas') or []
        dados_comuns = {
            'descricao': form.cleaned_data['descricao'],
            'tipo': form.cleaned_data['tipo'],
            'status': form.cleaned_data['status'],
            'data_competencia': form.cleaned_data['data_competencia'],
            'data_pagamento': form.cleaned_data.get('data_pagamento'),
            'numero_documento': (form.cleaned_data.get('numero_documento') or '').strip(),
            'pessoa': form.cleaned_data.get('pessoa'),
            'centro_custo': form.cleaned_data.get('centro_custo'),
            'conta': form.cleaned_data['conta'],
            'conta_destino': form.cleaned_data.get('conta_destino'),
            'observacoes': form.cleaned_data.get('observacoes', ''),
            'com_rateio': True,
            'grupo_rateio': grupo_lancamentos[0].grupo_rateio,
        }

        existentes_por_id = {lancamento.pk: lancamento for lancamento in grupo_lancamentos}
        ids_utilizados: set[int] = set()
        lancamentos_finais: list[LancamentoFinanceiro] = []

        for linha in rateio_linhas:
            linha_id = linha.get('id')
            if linha_id and int(linha_id) not in existentes_por_id:
                form.add_error('rateio_payload', 'Foi informada uma linha que nao pertence a este grupo de rateio.')
                return self.form_invalid(form)

        with transaction.atomic():
            for linha in rateio_linhas:
                linha_id = linha.get('id')
                if linha_id:
                    lancamento = existentes_por_id.get(int(linha_id))
                    ids_utilizados.add(lancamento.pk)
                    antes = _snapshot_lancamento(lancamento)
                    for campo, valor in dados_comuns.items():
                        setattr(lancamento, campo, valor)
                    lancamento.categoria = linha['categoria']
                    lancamento.valor = linha['valor']
                    lancamento.save()
                    depois = _snapshot_lancamento(lancamento)
                    if antes != depois:
                        _registrar_auditoria_lancamento(
                            request=self.request,
                            acao=AuditoriaFinanceiro.AcaoAuditoria.UPDATE,
                            lancamento=lancamento,
                            antes=antes,
                            depois=depois,
                        )
                    lancamentos_finais.append(lancamento)
                    continue

                lancamento = LancamentoFinanceiro.objects.create(
                    **dados_comuns,
                    categoria=linha['categoria'],
                    valor=linha['valor'],
                )
                _registrar_auditoria_lancamento(
                    request=self.request,
                    acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
                    lancamento=lancamento,
                    depois=_snapshot_lancamento(lancamento),
                )
                lancamentos_finais.append(lancamento)

            for lancamento in grupo_lancamentos:
                if lancamento.pk in ids_utilizados:
                    continue
                antes = _snapshot_lancamento(lancamento)
                registro_id = lancamento.pk
                lancamento.delete()
                AuditoriaFinanceiro.objects.create(
                    acao=AuditoriaFinanceiro.AcaoAuditoria.DELETE,
                    modelo='LancamentoFinanceiro',
                    registro_id=registro_id,
                    usuario=_auditoria_usuario(self.request),
                    campos_alterados=_build_auditoria_payload(antes, None),
                )

        self.object = lancamentos_finais[0]
        messages.success(
            self.request,
            f'Grupo de rateio atualizado com sucesso em {len(lancamentos_finais)} linhas. Voce voltou para a listagem principal de lancamentos.',
        )
        query_string = urlencode(
            {
                'origem_fluxo': 'rateio_coordenado_salvo',
                'grupo_rateio': grupo_lancamentos[0].grupo_rateio,
            }
        )
        return redirect(self._get_return_to_url() or f"{reverse('financeiro:lancamento-list')}?{query_string}")


class LancamentoFinanceiroReciboView(FinanceiroPermissaoMixin, DetailView):
    permissao_requerida = 'financeiro.lancamentos.emitir_recibo'
    model = LancamentoFinanceiro
    template_name = 'financeiro/lancamento_recibo.html'
    context_object_name = 'lancamento'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'conta',
            'conta_destino',
            'pessoa',
            'categoria',
            'centro_custo',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Recibo do Lancamento {self.object.pk}'
        context['recibo_documento'] = _montar_contexto_recibo_documento(
            [self.object],
            lote=False,
            categoria_documental=self.object.categoria,
        )
        return context


class LancamentoFinanceiroReciboLoteView(FinanceiroPermissaoMixin, TemplateView):
    permissao_requerida = 'financeiro.lancamentos.emitir_recibo'
    template_name = 'financeiro/lancamento_recibo.html'

    def _redirect_listagem(self, mensagem: str):
        if mensagem:
            messages.warning(self.request, mensagem)
        return redirect(reverse('financeiro:lancamento-list'))

    def _build_context(self):
        ids_raw = (self.request.GET.get('ids') or '').strip()
        ids = [int(valor) for valor in ids_raw.split(',') if valor.strip().isdigit()]
        if not ids:
            return None, 'Selecione lancamentos validos para emitir recibo em lote.'

        lancamentos = list(
            LancamentoFinanceiro.objects.filter(pk__in=ids)
            .select_related('pessoa', 'categoria')
            .order_by('data_pagamento', 'data_competencia', 'pk')
        )
        if not lancamentos:
            return None, 'Nenhum lancamento encontrado para emitir recibo em lote.'

        pessoas_ids = {lancamento.pessoa_id for lancamento in lancamentos}
        if None in pessoas_ids or len(pessoas_ids) != 1:
            return None, 'Recibo em lote so pode ser emitido quando todos os lancamentos forem do mesmo favorecido.'

        if any(lancamento.tipo != LancamentoFinanceiro.TipoLancamento.RECEITA for lancamento in lancamentos):
            return None, 'Recibo em lote so pode ser emitido para lancamentos do tipo receita.'

        pessoa = lancamentos[0].pessoa
        context = {
            'page_title': f'Recibo em lote - {pessoa.nome if pessoa else ""}',
            'recibo_documento': _montar_contexto_recibo_documento(
                lancamentos,
                lote=True,
            ),
        }
        return context, ''

    def get(self, request, *args, **kwargs):
        context, erro = self._build_context()
        if erro:
            return self._redirect_listagem(erro)
        return self.render_to_response(context)


def _data_lancamento_documental(lancamento: LancamentoFinanceiro) -> date:
    return lancamento.data_pagamento or lancamento.data_competencia


def _obter_categoria_documental_unica(
    lancamentos: list[LancamentoFinanceiro],
) -> tuple[CategoriaFinanceira | None, str]:
    categorias = {lancamento.categoria_id for lancamento in lancamentos}
    if None in categorias:
        return None, 'Recibos por favorecido exigem categoria definida em todos os lancamentos do grupo.'
    if len(categorias) != 1:
        return None, 'Recibos por favorecido exigem uma unica categoria documental por favorecido.'
    return lancamentos[0].categoria, ''


def _contexto_recibo_institucional(
    categoria_documental: CategoriaFinanceira | None = None,
    *,
    usar_mensagem_categoria: bool = True,
) -> dict[str, object]:
    assinatura_padrao = AssinaturaInstitucional.objects.filter(ativo=True, padrao=True).first()
    configuracao_padrao = ConfiguracaoInstitucional.objects.filter(ativo=True, padrao=True).first()
    mensagem_categoria = ''
    if categoria_documental and usar_mensagem_categoria:
        mensagem_categoria = (categoria_documental.mensagem_recibo or '').strip()
    return {
        'mensagem_final': (
            mensagem_categoria
            or (
                (configuracao_padrao.mensagem_padrao_recibo or '').strip()
                if configuracao_padrao
                else ''
            )
            or 'Recibo emitido com base no lancamento registrado no sistema.'
        ),
        'mensagem_personalizada': bool(mensagem_categoria),
        'assinatura_padrao': assinatura_padrao,
        'configuracao_institucional': configuracao_padrao,
        'nome_instituicao': (
            (configuracao_padrao.nome_instituicao or '').strip() if configuracao_padrao else ''
        ),
        'logo_url': (configuracao_padrao.logo_url or '').strip() if configuracao_padrao else '',
        'cidade': (configuracao_padrao.cidade or '').strip() if configuracao_padrao else '',
    }


def _agrupar_itens_recibo_por_descricao(
    lancamentos: list[LancamentoFinanceiro],
) -> list[dict[str, object]]:
    grupos: dict[str, dict[str, object]] = {}
    ordem_grupos: list[str] = []

    for lancamento in lancamentos:
        descricao_original = (lancamento.descricao or '').strip() or '(Sem descricao)'
        chave = descricao_original
        if chave not in grupos:
            grupos[chave] = {
                'descricao': descricao_original,
                'valor': Decimal('0.00'),
                'datas': [],
                'documentos': [],
                'quantidade': 0,
                'ordem_data': _data_lancamento_documental(lancamento) or date.today(),
                'ordem_pk': lancamento.pk,
            }
            ordem_grupos.append(chave)

        grupo = grupos[chave]
        grupo['valor'] += lancamento.valor
        grupo['quantidade'] += 1
        grupo['datas'].append(_data_lancamento_documental(lancamento))
        grupo['documentos'].append(lancamento.numero_documento or '-')
        grupo['ordem_data'] = min(grupo['ordem_data'], _data_lancamento_documental(lancamento) or grupo['ordem_data'])
        grupo['ordem_pk'] = min(grupo['ordem_pk'], lancamento.pk)

    itens = []
    for chave in ordem_grupos:
        grupo = grupos[chave]
        datas_unicas = [valor for valor in dict.fromkeys(grupo['datas']) if valor]
        documentos_unicos = [valor for valor in dict.fromkeys(grupo['documentos']) if valor]

        data_label = datas_unicas[0].strftime('%d/%m/%Y') if len(datas_unicas) == 1 else 'Datas diversas'
        documento_label = documentos_unicos[0] if len(documentos_unicos) == 1 else 'Doc. diversos'

        itens.append(
            {
                'descricao': grupo['descricao'],
                'valor': grupo['valor'],
                'data': datas_unicas[0] if len(datas_unicas) == 1 else None,
                'data_label': data_label,
                'documento_label': documento_label,
                'quantidade': grupo['quantidade'],
                'consolidado': grupo['quantidade'] > 1,
                'ordem_data': grupo['ordem_data'],
                'ordem_pk': grupo['ordem_pk'],
            }
        )

    return sorted(itens, key=lambda item: (item['ordem_data'], item['ordem_pk']))


def _montar_contexto_recibo_documento(
    lancamentos: list[LancamentoFinanceiro],
    *,
    lote: bool,
    categoria_documental: CategoriaFinanceira | None = None,
    numero_documento: str = '',
    usar_mensagem_categoria: bool = True,
) -> dict[str, object]:
    lancamentos_ordenados = sorted(
        lancamentos,
        key=lambda lancamento: (_data_lancamento_documental(lancamento) or date.today(), lancamento.pk),
    )
    lancamento_referencia = lancamentos_ordenados[0]
    pessoa = lancamento_referencia.pessoa
    total_valor = sum((lancamento.valor for lancamento in lancamentos_ordenados), Decimal('0.00'))
    datas = [
        _data_lancamento_documental(lancamento)
        for lancamento in lancamentos_ordenados
        if _data_lancamento_documental(lancamento)
    ]
    data_recibo = max(datas) if datas else date.today()
    return {
        'lote': lote,
        'numero_documento': numero_documento if lote else (lancamento_referencia.numero_documento or '-'),
        'valor_total': total_valor if lote else lancamento_referencia.valor,
        'itens': _agrupar_itens_recibo_por_descricao(lancamentos_ordenados) if lote else [],
        'pessoa_nome': pessoa.nome if pessoa else '-',
        'referente': 'os lancamentos listados abaixo' if lote else lancamento_referencia.descricao,
        'data_principal': data_recibo,
        'data_humana': _data_documental_por_extenso(data_recibo),
        'valor_extenso': _valor_por_extenso(total_valor if lote else lancamento_referencia.valor),
        'data_fallback': any(lancamento.data_pagamento is None for lancamento in lancamentos_ordenados),
        **_contexto_recibo_institucional(
            categoria_documental if lote else lancamento_referencia.categoria,
            usar_mensagem_categoria=usar_mensagem_categoria,
        ),
    }


def _validar_lancamentos_documentais_receita(
    lancamentos: list[LancamentoFinanceiro],
    *,
    exigir_quitado: bool = False,
) -> str:
    if not lancamentos:
        return 'Nenhum lancamento foi encontrado para emissao documental.'
    if any(lancamento.pessoa_id is None for lancamento in lancamentos):
        return 'A emissao documental exige lancamentos com favorecido.'
    if any(lancamento.tipo != LancamentoFinanceiro.TipoLancamento.RECEITA for lancamento in lancamentos):
        return 'A emissao documental por favorecido aceita apenas lancamentos do tipo receita.'
    if exigir_quitado and any(lancamento.status != LancamentoFinanceiro.StatusLancamento.QUITADO for lancamento in lancamentos):
        return 'Termo anual de quitacao so pode considerar lancamentos quitados.'
    return ''


def _filtrar_lancamentos_compativeis_termo_anual(queryset):
    return queryset.filter(
        tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
        status=LancamentoFinanceiro.StatusLancamento.QUITADO,
        pessoa__isnull=False,
        com_rateio=False,
    )


def _resolver_categoria_documental(parametros) -> CategoriaFinanceira | None:
    categoria_raw = (parametros.get('categoria') or '').strip()
    if not categoria_raw.isdigit():
        return None
    return CategoriaFinanceira.objects.filter(pk=int(categoria_raw)).first()


def _montar_contexto_filtros_documentais(parametros) -> dict[str, object]:
    data_inicial = _parse_data_iso(parametros.get('data_inicial', ''))
    data_final = _parse_data_iso(parametros.get('data_final', ''))
    categoria = _resolver_categoria_documental(parametros)
    periodo_partes = []
    if data_inicial:
        periodo_partes.append(f'a partir de {data_inicial.strftime("%d/%m/%Y")}')
    if data_final:
        periodo_partes.append(f'ate {data_final.strftime("%d/%m/%Y")}')
    return {
        'data_inicial': data_inicial,
        'data_final': data_final,
        'periodo_label': ' e '.join(periodo_partes),
        'categoria': categoria,
    }


def _montar_grupos_documentais_por_favorecido(lancamentos: list[LancamentoFinanceiro]) -> list[dict[str, object]]:
    grupos_por_pessoa: dict[int, list[LancamentoFinanceiro]] = {}
    pessoas_por_id: dict[int, PessoaFinanceira] = {}
    for lancamento in lancamentos:
        if not lancamento.pessoa_id:
            continue
        grupos_por_pessoa.setdefault(lancamento.pessoa_id, []).append(lancamento)
        pessoas_por_id[lancamento.pessoa_id] = lancamento.pessoa

    grupos = []
    for pessoa_id, lancamentos_pessoa in sorted(
        grupos_por_pessoa.items(),
        key=lambda item: pessoas_por_id[item[0]].nome.lower(),
    ):
        lancamentos_ordenados = sorted(
            lancamentos_pessoa,
            key=lambda lancamento: (_data_lancamento_documental(lancamento), lancamento.pk),
        )
        total = sum((lancamento.valor for lancamento in lancamentos_ordenados), Decimal('0.00'))
        grupos.append(
            {
                'pessoa': pessoas_por_id[pessoa_id],
                'lancamentos': lancamentos_ordenados,
                'quantidade': len(lancamentos_ordenados),
                'total': total,
                'total_formatado': _formatar_moeda_brl(total),
                'valor_extenso': _valor_por_extenso(total),
            }
        )
    return grupos


def _contexto_institucional_documental() -> dict[str, object]:
    assinatura_padrao = (
        AssinaturaInstitucional.objects.filter(ativo=True, padrao=True).first()
        or AssinaturaInstitucional.objects.filter(ativo=True).first()
    )
    configuracao_padrao = ConfiguracaoInstitucional.objects.filter(ativo=True, padrao=True).first()
    assinatura_nome = ''
    assinatura_cargo = ''
    assinatura_texto = ''
    if assinatura_padrao:
        assinatura_nome = (
            (assinatura_padrao.nome_exibicao or '').strip()
            or (assinatura_padrao.assinatura_texto or '').strip()
            or (assinatura_padrao.nome or '').strip()
        )
        assinatura_cargo = (assinatura_padrao.cargo or '').strip()
        assinatura_texto = (assinatura_padrao.assinatura_texto or '').strip()

    return {
        'recibo_assinatura_padrao': assinatura_padrao,
        'recibo_assinatura_nome': assinatura_nome or 'Responsavel institucional',
        'recibo_assinatura_cargo': assinatura_cargo or 'Casa Espirita',
        'recibo_assinatura_texto': assinatura_texto,
        'recibo_configuracao_institucional': configuracao_padrao,
        'recibo_nome_instituicao': (
            (configuracao_padrao.nome_instituicao or '').strip() if configuracao_padrao else ''
        ),
        'recibo_logo_url': (configuracao_padrao.logo_url or '').strip() if configuracao_padrao else '',
        'recibo_cidade': (configuracao_padrao.cidade or '').strip() if configuracao_padrao else '',
        'recibo_mensagem_final': (
            (configuracao_padrao.mensagem_padrao_recibo or '').strip()
            if configuracao_padrao
            else ''
        ),
    }


def _resolver_contexto_base_termo_anual(request) -> tuple[dict[str, object], date | None, date | None, object]:
    contexto_filtros = _montar_contexto_filtros_documentais(request.GET)
    data_inicial = contexto_filtros['data_inicial']
    data_final = contexto_filtros['data_final']
    if not data_inicial or not data_final:
        return contexto_filtros, data_inicial, data_final, 'Informe Pagamento inicial e Pagamento final para emitir o termo anual de quitacao.'
    if data_inicial.year != data_final.year:
        return contexto_filtros, data_inicial, data_final, 'O termo anual de quitacao exige periodo dentro de um unico ano.'

    queryset = LancamentoFinanceiro.objects.select_related('pessoa', 'categoria')
    queryset = _filtrar_lancamentos_por_parametros(queryset, request.GET)
    queryset = _filtrar_lancamentos_compativeis_termo_anual(queryset)
    lancamentos = list(queryset.order_by('pessoa__nome', 'data_pagamento', 'data_competencia', 'pk'))
    if not lancamentos:
        return (
            contexto_filtros,
            data_inicial,
            data_final,
            'Nenhum lancamento compativel com termo anual de quitacao foi encontrado no filtro atual.',
        )
    return contexto_filtros, data_inicial, data_final, lancamentos


class LancamentoFinanceiroRecibosPorFavorecidoView(FinanceiroPermissaoMixin, TemplateView):
    permissao_requerida = 'financeiro.lancamentos.emitir_recibo'
    template_name = 'financeiro/lancamento_recibo.html'

    def _redirect_listagem(self, mensagem: str):
        if mensagem:
            messages.warning(self.request, mensagem)
        return redirect(reverse('financeiro:lancamento-list'))

    def get(self, request, *args, **kwargs):
        ids_raw = (request.GET.get('ids') or '').strip()
        ids = [int(valor) for valor in ids_raw.split(',') if valor.strip().isdigit()]
        if not ids:
            return self._redirect_listagem('Selecione lancamentos validos para emitir recibos por favorecido.')

        lancamentos = list(
            LancamentoFinanceiro.objects.filter(pk__in=ids)
            .select_related('pessoa', 'categoria')
            .order_by('pessoa__nome', 'data_pagamento', 'data_competencia', 'pk')
        )
        erro = _validar_lancamentos_documentais_receita(lancamentos)
        if erro:
            return self._redirect_listagem(erro)

        grupos_receibo = []
        grupos_por_pessoa: dict[int, list[LancamentoFinanceiro]] = {}
        for lancamento in lancamentos:
            grupos_por_pessoa.setdefault(lancamento.pessoa_id, []).append(lancamento)

        for pessoa_id, lancamentos_pessoa in sorted(
            grupos_por_pessoa.items(),
            key=lambda item: (item[1][0].pessoa.nome or '').lower(),
        ):
            grupos_receibo.append(
                _montar_contexto_recibo_documento(
                    sorted(
                        lancamentos_pessoa,
                        key=lambda lancamento: (_data_lancamento_documental(lancamento), lancamento.pk),
                    ),
                    lote=True,
                    numero_documento='Lote',
                    usar_mensagem_categoria=False,
                )
            )

        context = {
            'page_title': 'Recibos em lote por favorecido',
            'recibo_grupos': grupos_receibo,
            'recibo_multigrupo': True,
        }
        return self.render_to_response(context)


class LancamentoFinanceiroTermoAnualQuitacaoView(FinanceiroPermissaoMixin, TemplateView):
    permissao_requerida = 'financeiro.lancamentos.emitir_recibo'
    template_name = 'financeiro/lancamento_documentos_por_favorecido.html'

    def _redirect_listagem(self, mensagem: str):
        if mensagem:
            messages.warning(self.request, mensagem)
        url_listagem = reverse('financeiro:lancamento-list')
        filtros = self.request.GET.urlencode()
        if filtros:
            return redirect(f'{url_listagem}?{filtros}')
        return redirect(url_listagem)

    def get(self, request, *args, **kwargs):
        contexto_filtros, data_inicial, data_final, resultado = _resolver_contexto_base_termo_anual(request)
        if isinstance(resultado, str):
            return self._redirect_listagem(resultado)

        lancamentos = resultado
        context = {
            'page_title': f'Termo anual de quitacao {data_inicial.year}',
            'tipo_documento': 'termo_anual_quitacao',
            'titulo_documento': 'TERMO ANUAL DE QUITACAO',
            'subtitulo_documento': f'Referente ao ano de {data_inicial.year}',
            'grupos_documentais': _montar_grupos_documentais_por_favorecido(lancamentos),
            'contexto_filtros': contexto_filtros,
            'ano_documento': data_inicial.year,
            'data_emissao_humana': _data_documental_por_extenso(date.today()),
            **_contexto_institucional_documental(),
        }
        return self.render_to_response(context)


class LancamentoFinanceiroTermosAnuaisQuitacaoPorFavorecidoView(FinanceiroPermissaoMixin, TemplateView):
    permissao_requerida = 'financeiro.lancamentos.emitir_recibo'
    template_name = 'financeiro/lancamento_documentos_por_favorecido.html'

    def _redirect_listagem(self, mensagem: str):
        if mensagem:
            messages.warning(self.request, mensagem)
        url_listagem = reverse('financeiro:lancamento-list')
        filtros = self.request.GET.urlencode()
        if filtros:
            return redirect(f'{url_listagem}?{filtros}')
        return redirect(url_listagem)

    def get(self, request, *args, **kwargs):
        url = reverse('financeiro:lancamento-termo-anual-quitacao')
        query = request.GET.urlencode()
        if query:
            url = f'{url}?{query}'
        return redirect(url)


class LancamentoFinanceiroDeleteView(FinanceiroDeleteMixin):
    permissao_requerida = 'financeiro.lancamentos.excluir'
    model = LancamentoFinanceiro
    success_url = reverse_lazy('financeiro:lancamento-list')
    page_title = 'Excluir Lancamento Financeiro'
    cancel_url = reverse_lazy('financeiro:lancamento-list')
    success_message = 'Lancamento financeiro excluido com sucesso.'

    def form_valid(self, form):
        lancamento = self.object
        antes = _snapshot_lancamento(lancamento)
        registro_id = lancamento.pk

        with transaction.atomic():
            response = super().form_valid(form)
            AuditoriaFinanceiro.objects.create(
                acao=AuditoriaFinanceiro.AcaoAuditoria.DELETE,
                modelo='LancamentoFinanceiro',
                registro_id=registro_id,
                usuario=_auditoria_usuario(self.request),
                campos_alterados=_build_auditoria_payload(antes, None),
            )

        return response

