from __future__ import annotations

import json
from calendar import monthrange
from datetime import date, datetime, timedelta
from decimal import Decimal
from io import BytesIO
from urllib.parse import urlencode
from uuid import uuid4
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
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
    'marco',
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

LANCAMENTO_IMPORTACAO_MODELO_COLUNAS = [
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

LANCAMENTO_IMPORTACAO_MODELO_ROTULOS = {
    'tipo': 'Tipo',
    'status': 'Status',
    'descricao': 'Descrição',
    'valor': 'Valor',
    'data_competencia': 'Data de competência',
    'data_pagamento': 'Data de pagamento',
    'pessoa_nome': 'Pessoa',
    'categoria_nome': 'Categoria',
    'centro_custo_nome': 'Centro de custo',
    'conta_nome': 'Conta',
    'conta_destino_nome': 'Conta de destino',
    'numero_documento': 'Documento',
    'observacoes': 'Observações',
}

LANCAMENTO_IMPORTACAO_ORIENTACOES = {
    'tipo': 'Use receita, despesa ou transferencia.',
    'status': 'Use aberto, quitado ou cancelado.',
    'descricao': 'Preencha uma descrição para identificar o lançamento.',
    'valor': 'Informe um número maior que zero, com vírgula ou ponto decimal.',
    'data_competencia': 'Use o formato dd/mm/aaaa.',
    'data_pagamento': 'Use o formato dd/mm/aaaa.',
    'pessoa_nome': 'Revise o nome exatamente como está cadastrado.',
    'categoria_nome': 'Revise Tipo e Categoria e use uma subcategoria já cadastrada.',
    'centro_custo_nome': 'Revise o nome exatamente como está cadastrado.',
    'conta_nome': 'Revise o nome da conta ou preencha uma conta já cadastrada.',
    'conta_destino_nome': 'Preencha uma conta de destino já cadastrada quando o tipo for transferência.',
    'numero_documento': 'Revise duplicidade ou deixe em branco para geração automática.',
}

LANCAMENTO_IMPORTACAO_CAMPOS_MODELO = {
    'pessoa': 'pessoa_nome',
    'categoria': 'categoria_nome',
    'centro_custo': 'centro_custo_nome',
    'conta': 'conta_nome',
    'conta_destino': 'conta_destino_nome',
}

LANCAMENTO_IMPORTACAO_ABAS_OBRIGATORIAS = ['Modelo', 'Instruções']

LANCAMENTO_EXPORTACAO_COLUNAS = [
    'Tipo',
    'Status',
    'Descrição',
    'Valor',
    'Data de competência',
    'Data de pagamento',
    'Pessoa',
    'Categoria',
    'Centro de custo',
    'Conta',
    'Conta de destino',
    'Documento',
    'Observações',
]

LANCAMENTO_IMPORTACAO_MODELO_INSTRUCOES = [
    [
        'Finalidade',
        'Use esta planilha como base para preparar lançamentos que serão importados em uma próxima etapa do sistema.',
    ],
    [
        'Cabeçalhos',
        'Mantenha os nomes das colunas da aba Modelo exatamente como estão e preencha uma linha por lançamento.',
    ],
    [
        'Datas e valores',
        'Use datas no formato dd/mm/aaaa. Se necessário, o sistema também aceita AAAA-MM-DD. Para valores, use número com vírgula ou ponto decimal.',
    ],
    [
        'Campos opcionais',
        'Deixe em branco os campos que não se aplicarem ao lançamento, como centro_custo_nome, numero_documento e observacoes.',
    ],
    [
        'Transferências',
        'Preencha conta_destino_nome apenas quando o lançamento for uma transferência entre contas.',
    ],
    [
        'Layout do sistema',
        'Preencha os dados seguindo a ordem e a estrutura da aba Modelo para facilitar a futura importação.',
    ],
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
            ('Instruções', [['Item', 'Orientação'], *LANCAMENTO_IMPORTACAO_MODELO_INSTRUCOES]),
        ]
    )


def _linha_exportacao_lancamento(lancamento: LancamentoFinanceiro) -> list[str]:
    return [
        lancamento.tipo,
        lancamento.status,
        lancamento.descricao,
        f'{lancamento.valor:.2f}'.replace('.', ','),
        lancamento.data_competencia.strftime('%d/%m/%Y'),
        lancamento.data_pagamento.strftime('%d/%m/%Y') if lancamento.data_pagamento else '',
        lancamento.pessoa.nome if lancamento.pessoa_id else '',
        lancamento.categoria.nome if lancamento.categoria_id else '',
        lancamento.centro_custo.nome if lancamento.centro_custo_id else '',
        lancamento.conta.nome if lancamento.conta_id else '',
        lancamento.conta_destino.nome if lancamento.conta_destino_id else '',
        lancamento.numero_documento,
        lancamento.observacoes,
    ]


def _gerar_planilha_exportacao_lancamentos_xlsx(lancamentos) -> bytes:
    linhas = [LANCAMENTO_EXPORTACAO_COLUNAS]
    linhas.extend(_linha_exportacao_lancamento(lancamento) for lancamento in lancamentos)

    return _gerar_arquivo_xlsx([('Lancamentos', linhas)])


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
) -> list[tuple[int, list[str]]]:
    planilha_tree = ElementTree.fromstring(arquivo_xlsx.read(caminho_planilha))
    linhas = []

    for indice_padrao, linha_xml in enumerate(
        planilha_tree.findall('main:sheetData/main:row', namespace),
        start=1,
    ):
        numero_linha = int(linha_xml.get('r') or indice_padrao)
        valores_linha = [''] * len(LANCAMENTO_IMPORTACAO_MODELO_COLUNAS)

        for indice_celula, celula in enumerate(linha_xml.findall('main:c', namespace), start=1):
            indice_coluna = _xlsx_indice_coluna_celula(celula.get('r', '')) or indice_celula
            if 1 <= indice_coluna <= len(LANCAMENTO_IMPORTACAO_MODELO_COLUNAS):
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


def _validar_estrutura_planilha_importacao_lancamentos_xlsx(arquivo_importacao) -> list[str]:
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

            abas_faltantes = [
                nome_aba
                for nome_aba in LANCAMENTO_IMPORTACAO_ABAS_OBRIGATORIAS
                if nome_aba not in planilhas
            ]
            if abas_faltantes:
                return [
                    'A planilha enviada precisa conter as abas '
                    f'{", ".join(LANCAMENTO_IMPORTACAO_ABAS_OBRIGATORIAS)}. '
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

            if cabecalhos != LANCAMENTO_IMPORTACAO_MODELO_COLUNAS:
                return [
                    'Os cabecalhos da aba Modelo estao diferentes do layout esperado. '
                    'Mantenha exatamente esta ordem e nomenclatura: '
                    f'{", ".join(LANCAMENTO_IMPORTACAO_MODELO_COLUNAS)}.'
                ]
    except (BadZipFile, KeyError, ParseError, OSError):
        return ['Nao foi possivel ler o arquivo enviado como uma planilha XLSX valida.']
    finally:
        arquivo_importacao.seek(0)

    return []


def _xlsx_ler_dados_modelo_importacao_lancamentos_xlsx(arquivo_importacao) -> list[tuple[int, list[str]]]:
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
            )
    except (BadZipFile, KeyError, ParseError, OSError):
        return []
    finally:
        arquivo_importacao.seek(0)


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
    erros_por_campo.setdefault(campo, []).append(mensagem)


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
        _adicionar_erro_importacao(erros_por_campo, 'tipo', 'Informe o tipo do lançamento.')
    elif tipo not in tipos_validos:
        _adicionar_erro_importacao(
            erros_por_campo,
            'tipo',
            'Use um tipo válido: receita, despesa ou transferencia.',
        )

    if not status:
        _adicionar_erro_importacao(erros_por_campo, 'status', 'Informe o status do lançamento.')
    elif status not in status_validos:
        _adicionar_erro_importacao(
            erros_por_campo,
            'status',
            'Use um status válido: aberto, quitado ou cancelado.',
        )

    if not descricao:
        _adicionar_erro_importacao(erros_por_campo, 'descricao', 'Informe a descrição.')

    valor = _parse_decimal_importacao_lancamento(valor_texto)
    if not valor_texto:
        _adicionar_erro_importacao(erros_por_campo, 'valor', 'Informe o valor.')
    elif valor is None:
        _adicionar_erro_importacao(erros_por_campo, 'valor', 'Informe um valor numérico válido.')
    elif valor <= 0:
        _adicionar_erro_importacao(erros_por_campo, 'valor', 'Informe um valor maior que zero.')

    data_competencia = _parse_data_importacao_lancamento(data_competencia_texto)
    if not data_competencia_texto:
        _adicionar_erro_importacao(
            erros_por_campo,
            'data_competencia',
            'Informe a data de competência.',
        )
    elif data_competencia is None:
        _adicionar_erro_importacao(
            erros_por_campo,
            'data_competencia',
            'Use uma data de competência válida no formato dd/mm/aaaa.',
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
            'Use uma data de pagamento válida no formato dd/mm/aaaa.',
        )

    pessoa = None
    if pessoa_nome:
        pessoa = pessoas_por_nome.get(_normalizar_nome_importacao_lancamento(pessoa_nome))
        if pessoa is None:
            _adicionar_erro_importacao(
                erros_por_campo,
                'pessoa_nome',
                'Pessoa não encontrada no cadastro.',
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
                'Subcategoria não encontrada para o tipo informado.',
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
                'Centro de custo não encontrado no cadastro.',
            )

    conta = None
    if conta_nome:
        conta = contas_por_nome.get(_normalizar_nome_importacao_lancamento(conta_nome))
        if conta is None:
            _adicionar_erro_importacao(
                erros_por_campo,
                'conta_nome',
                'Conta não encontrada no cadastro.',
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
                'Conta de destino não encontrada no cadastro.',
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


def _validar_conteudo_planilha_importacao_lancamentos_xlsx(arquivo_importacao) -> dict[str, object]:
    resultado = {
        'linhas_lidas': 0,
        'linhas_validas': 0,
        'linhas_importadas': 0,
        'linhas_invalidas': 0,
        'erros': [],
        'lancamentos_validos': [],
    }

    linhas_planilha = _xlsx_ler_dados_modelo_importacao_lancamentos_xlsx(arquivo_importacao)
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
        dados_linha = dict(zip(LANCAMENTO_IMPORTACAO_MODELO_COLUNAS, valores_linha))
        if not any((valor or '').strip() for valor in dados_linha.values()):
            continue

        resultado['linhas_lidas'] += 1
        lancamento_validado, erros_linha = _validar_linha_importacao_lancamento(
            dados_linha,
            pessoas_por_nome,
            categorias_por_tipo_nome,
            centros_custo_por_nome,
            contas_por_nome,
        )

        numero_documento = (dados_linha.get('numero_documento') or '').strip()
        if numero_documento and numero_documento in documentos_importacao:
            _adicionar_erro_importacao(
                erros_linha,
                'numero_documento',
                f'Documento repetido na linha {documentos_importacao[numero_documento]} desta planilha.',
            )
        elif numero_documento and lancamento_validado:
            documentos_importacao[numero_documento] = numero_linha

        if erros_linha:
            resultado['linhas_invalidas'] += 1
            resultado['erros'].append({
                'linha': numero_linha,
                'campos': [
                    {
                        'campo': campo,
                        'rotulo': _rotulo_campo_importacao_lancamento(campo),
                        'mensagem': mensagem,
                        'orientacao': _orientacao_campo_importacao_lancamento(
                            campo,
                            mensagem,
                        ),
                        'valor_informado': (dados_linha.get(campo) or '').strip(),
                    }
                    for campo, mensagens in erros_linha.items()
                    for mensagem in mensagens
                ],
            })
        else:
            resultado['linhas_validas'] += 1
            resultado['lancamentos_validos'].append(lancamento_validado)

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

    return _gerar_arquivo_xlsx([('Inconsistências', linhas)])


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
        queryset = queryset.filter(data_competencia__gte=data_inicial)
    if data_final:
        queryset = queryset.filter(data_competencia__lte=data_final)
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
            .order_by('pk')
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
            grupos_renderizados.add(grupo_rateio)
            continue

        lancamentos_visuais.append({
            'eh_rateio': False,
            'token_selecao': f'lancamento:{lancamento.pk}',
            'representante': lancamento,
            'linhas_rateio': [],
            'valor_total': lancamento.valor,
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


class FinanceiroFormMixin(FinanceiroPermissaoMixin):
    page_title = ''
    submit_label = 'Salvar'
    success_message = 'Registro salvo com sucesso.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['submit_label'] = self.submit_label
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class FinanceiroDeleteMixin(FinanceiroPermissaoMixin, DeleteView):
    template_name = 'financeiro/confirm_delete.html'
    success_message = 'Registro excluido com sucesso.'
    page_title = 'Confirmar exclusao'
    cancel_url = reverse_lazy('financeiro:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['cancel_url'] = self.cancel_url
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
        contas_disponiveis = list(ContaFinanceira.objects.order_by('nome'))
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
            lancamentos = LancamentoFinanceiro.objects.filter(
                Q(conta_id__in=contas_por_id.keys()) | Q(conta_destino_id__in=contas_por_id.keys()),
                status=LancamentoFinanceiro.StatusLancamento.QUITADO,
                data_competencia__lte=data_referencia,
            ).only('tipo', 'valor', 'conta_id', 'conta_destino_id')

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
                data_competencia__gte=data_inicial,
                data_competencia__lte=data_final,
            )
            .select_related('conta', 'pessoa', 'categoria', 'centro_custo')
            .order_by('data_competencia', 'criado_em', 'pk')
        )
        despesas = list(
            LancamentoFinanceiro.objects.filter(
                status=LancamentoFinanceiro.StatusLancamento.QUITADO,
                tipo=LancamentoFinanceiro.TipoLancamento.DESPESA,
                conta_id__in=selected_ids,
                data_competencia__gte=data_inicial,
                data_competencia__lte=data_final,
            )
            .select_related('conta', 'pessoa', 'categoria', 'centro_custo')
            .order_by('data_competencia', 'criado_em', 'pk')
        )
        total_receitas = sum((lancamento.valor for lancamento in receitas), Decimal('0.00'))
        total_despesas = sum((lancamento.valor for lancamento in despesas), Decimal('0.00'))
        return receitas, despesas, total_receitas, total_despesas

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
        contas_selecionadas = [conta for conta in contas_disponiveis if conta.id in selected_ids]
        context: dict[str, object] = {
            'data_inicial': data_inicial_raw,
            'data_final': data_final_raw,
            'periodo_error': periodo_error,
            'contas_disponiveis': contas_disponiveis,
            'contas_selecionadas_ids': [str(conta_id) for conta_id in selected_ids],
            'contas_selecionadas': contas_selecionadas,
            'contas_incluidas_label': (
                'Todas as contas'
                if len(selected_ids) == len(contas_disponiveis)
                else ', '.join(conta.nome for conta in contas_selecionadas)
            ),
            'quantidade_contas_selecionadas': len(contas_selecionadas),
            'mostrar_centro_custo': mostrar_centro_custo,
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
        context.update(
            {
                'periodo_label': f'{data_inicial.strftime("%d/%m/%Y")} a {data_final.strftime("%d/%m/%Y")}',
                'saldo_inicial_consolidado': saldo_inicial_consolidado,
                'total_receitas_periodo': total_receitas,
                'total_despesas_periodo': total_despesas,
                'saldo_final_consolidado': saldo_final_consolidado,
                'saldo_periodo': saldo_final_consolidado - saldo_inicial_consolidado,
                'composicao_inicial': composicao_inicial,
                'composicao_final': composicao_final,
                'receitas_periodo': receitas,
                'despesas_periodo': despesas,
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
        context['page_title'] = 'Prestacao de Contas'
        context.update(self._build_periodo_context())
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
            return reverse(
                'financeiro:lancamento-rateio-clone',
                kwargs={'grupo_rateio': lancamento.grupo_rateio},
            )
        if not lancamento.com_rateio and not lancamento.grupo_rateio:
            return reverse(
                'financeiro:lancamento-clone',
                kwargs={'pk': lancamento.pk},
            )
        return ''

    def get(self, request, pessoa_id: int, *args, **kwargs):
        lancamentos = list(
            LancamentoFinanceiro.objects.filter(pessoa_id=pessoa_id)
            .select_related('categoria')
            .order_by('-data_competencia', '-criado_em', '-pk')[: self.limit]
        )
        results = [
            {
                'data': lancamento.data_competencia.strftime('%d/%m/%Y'),
                'tipo': lancamento.get_tipo_display(),
                'descricao': lancamento.descricao,
                'valor': f'R$ {lancamento.valor:.2f}',
                'categoria': str(lancamento.categoria) if lancamento.categoria else 'Sem categoria',
                'numero_documento': lancamento.numero_documento or '',
                'clone_url': self._get_clone_url(request, lancamento),
            }
            for lancamento in lancamentos
        ]
        return JsonResponse({'results': results})


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
        return context


class ContaFinanceiraCreateView(FinanceiroFormMixin, CreateView):
    permissao_requerida = 'financeiro.contas.criar'
    model = ContaFinanceira
    form_class = ContaFinanceiraForm
    template_name = 'financeiro/conta_form.html'
    success_url = reverse_lazy('financeiro:conta-list')
    page_title = 'Nova Conta Financeira'
    success_message = 'Conta financeira cadastrada com sucesso.'

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
                    'saldo_acumulado': saldo_acumulado,
                    'rateio_consolidado': len(bloco) > 1 and bool((lancamento_representante.grupo_rateio or '').strip()),
                    'quantidade_linhas_rateio': len(bloco),
                    'favorecido_exibicao': lancamento_representante.pessoa.nome if lancamento_representante.pessoa else '-',
                    'observacoes_exibicao': observacoes or '-',
                }
            )

        return itens_extrato, saldo_acumulado

    def _get_extrato_context(
        self,
        conta: ContaFinanceira,
        data_inicial: str = '',
        data_final: str = '',
    ) -> dict[str, object]:
        queryset_base = (
            LancamentoFinanceiro.objects.filter(
                Q(conta=conta) | Q(conta_destino=conta),
                status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            )
            .select_related('conta', 'conta_destino', 'pessoa', 'categoria')
            .order_by('data_competencia', 'criado_em', 'pk')
        )

        saldo_anterior = conta.saldo_inicial or Decimal('0.00')
        if data_inicial:
            lancamentos_anteriores = queryset_base.filter(data_competencia__lt=data_inicial)
            for lancamento in lancamentos_anteriores:
                entrada, saida = self._classificar_lancamento(conta, lancamento)
                saldo_anterior += entrada - saida

        lancamentos = queryset_base
        if data_inicial:
            lancamentos = lancamentos.filter(data_competencia__gte=data_inicial)
        if data_final:
            lancamentos = lancamentos.filter(data_competencia__lte=data_final)

        saldo_base = saldo_anterior if data_inicial else (conta.saldo_inicial or Decimal('0.00'))
        itens_extrato, saldo_acumulado = self._montar_itens_extrato(conta, list(lancamentos), saldo_base)

        return {
            'conta': conta,
            'saldo_inicial': conta.saldo_inicial or Decimal('0.00'),
            'data_saldo_inicial': conta.data_saldo_inicial,
            'data_inicial': data_inicial,
            'data_final': data_final,
            'saldo_anterior': saldo_anterior if data_inicial else None,
            'exibe_linha_saldo_inicial': True,
            'itens_extrato': itens_extrato,
            'saldo_final': saldo_acumulado,
            'saldo_atual': saldo_acumulado,
        }


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

        context.update(self._get_extrato_context(conta, data_inicial, data_final))
        context['page_title'] = f'Extrato da Conta: {conta.nome}'
        context['show_conta_filter'] = False
        context['clear_extrato_url'] = reverse_lazy('financeiro:conta-extrato', kwargs={'pk': conta.pk})
        return context


class ExtratoFinanceiroView(ExtratoContaMixin, TemplateView):
    permissao_requerida = 'financeiro.extratos.visualizar'
    template_name = 'financeiro/conta_extrato.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conta_id = self.request.GET.get('conta', '').strip()
        data_inicial = self.request.GET.get('data_inicial', '').strip()
        data_final = self.request.GET.get('data_final', '').strip()
        contas = ContaFinanceira.objects.order_by('nome')

        context['page_title'] = 'Extratos'
        context['contas'] = contas
        context['conta_selecionada_id'] = conta_id
        context['show_conta_filter'] = True
        context['clear_extrato_url'] = reverse_lazy('financeiro:extrato-list')

        if conta_id:
            try:
                conta = contas.get(pk=conta_id)
            except ContaFinanceira.DoesNotExist:
                context['extrato_error'] = 'Conta financeira nao encontrada.'
            else:
                context.update(self._get_extrato_context(conta, data_inicial, data_final))
                context['page_title'] = f'Extratos - {conta.nome}'

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


class CentroCustoCreateView(FinanceiroFormMixin, CreateView):
    permissao_requerida = 'financeiro.centros_custo.criar'
    model = CentroCusto
    form_class = CentroCustoForm
    template_name = 'financeiro/centro_custo_form.html'
    success_url = reverse_lazy('financeiro:centro-custo-list')
    page_title = 'Novo Centro de Custo'
    success_message = 'Centro de custo cadastrado com sucesso.'

    def form_valid(self, form):
        response = super().form_valid(form)
        _registrar_auditoria_centro_custo(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
            centro_custo=self.object,
            depois=_snapshot_centro_custo(self.object),
        )
        return response


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


class PessoaFinanceiraCreateView(FinanceiroFormMixin, CreateView):
    permissao_requerida = 'financeiro.pessoas.criar'
    model = PessoaFinanceira
    form_class = PessoaFinanceiraForm
    template_name = 'financeiro/pessoa_form.html'
    success_url = reverse_lazy('financeiro:pessoa-list')
    page_title = 'Nova Pessoa Financeira'
    success_message = 'Pessoa financeira cadastrada com sucesso.'

    def form_valid(self, form):
        response = super().form_valid(form)
        _registrar_auditoria_pessoa(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
            pessoa=self.object,
            depois=_snapshot_pessoa(self.object),
        )
        return response


class PessoaFinanceiraUpdateView(FinanceiroFormMixin, UpdateView):
    permissao_requerida = 'financeiro.pessoas.editar'
    model = PessoaFinanceira
    form_class = PessoaFinanceiraForm
    template_name = 'financeiro/pessoa_form.html'
    success_url = reverse_lazy('financeiro:pessoa-list')
    page_title = 'Editar Pessoa Financeira'
    submit_label = 'Atualizar'
    success_message = 'Pessoa financeira atualizada com sucesso.'

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
    page_title = 'Excluir Pessoa Financeira'
    cancel_url = reverse_lazy('financeiro:pessoa-list')
    success_message = 'Pessoa financeira excluida com sucesso.'

    def form_valid(self, form):
        pessoa = self.object
        antes = _snapshot_pessoa(pessoa)
        registro_id = pessoa.pk

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


class CategoriaFinanceiraCreateView(FinanceiroFormMixin, CreateView):
    permissao_requerida = 'financeiro.categorias.criar'
    model = CategoriaFinanceira
    form_class = CategoriaFinanceiraForm
    template_name = 'financeiro/categoria_form.html'
    success_url = reverse_lazy('financeiro:categoria-list')
    page_title = 'Nova Categoria Financeira'
    success_message = 'Categoria financeira cadastrada com sucesso.'

    def form_valid(self, form):
        response = super().form_valid(form)
        _registrar_auditoria_categoria(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
            categoria=self.object,
            depois=_snapshot_categoria(self.object),
        )
        return response


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
        context['contas_disponiveis'] = ContaFinanceira.objects.order_by('nome')
        context['pessoas_disponiveis'] = PessoaFinanceira.objects.order_by('nome')
        context['categorias_disponiveis'] = CategoriaFinanceira.objects.order_by('tipo', 'nome')
        context['lancamentos_visuais'] = _ordenar_lancamentos_visuais_listagem(
            _montar_lancamentos_visuais_listagem(context['lancamentos']),
            ordenacao_atual,
        )
        context.update(_montar_contexto_ordenacao_lancamentos_listagem(
            self.request,
            ordenacao_atual,
        ))
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
        context['page_title'] = 'Importação de Lançamentos'
        context['resultado_importacao_validacao'] = kwargs.get('resultado_importacao_validacao')
        context['resultado_importacao_erros_json'] = kwargs.get('resultado_importacao_erros_json', '')
        return context

    def post(self, request, *args, **kwargs):
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
                'A estrutura da planilha está correta, mas não há linhas preenchidas na aba Modelo.',
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
                    'Importação concluída com sucesso. '
                    f'{resultado_importacao_validacao["linhas_importadas"]} '
                    'lançamentos importados.',
                )
            except ValidationError:
                resultado_importacao_validacao['linhas_importadas'] = 0
                messages.error(
                    request,
                    'Nenhuma linha foi importada porque a planilha ficou inconsistente durante '
                    'a gravação. Revise o arquivo e envie novamente.',
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
                'Não há inconsistências disponíveis para baixar neste momento. '
                'Envie a planilha novamente para gerar o relatório.',
            )
            return redirect('financeiro:lancamento-importacao-exportacao')

        response = HttpResponse(
            _gerar_relatorio_inconsistencias_importacao_lancamentos_xlsx(erros),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = (
            'attachment; filename="relatorio_inconsistencias_importacao_lancamentos.xlsx"'
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


class LancamentoFinanceiroExportacaoView(FinanceiroPermissaoMixin, View):
    permissao_requerida = 'financeiro.lancamentos.exportar'

    def get(self, request, *args, **kwargs):
        lancamentos = (
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
            .order_by('-data_competencia', '-data_pagamento', '-criado_em', '-pk')
        )
        response = HttpResponse(
            _gerar_planilha_exportacao_lancamentos_xlsx(lancamentos),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="exportacao_lancamentos.xlsx"'

        return response


class LancamentoFinanceiroAcoesLoteView(FinanceiroPermissaoMixin, View):
    permissao_requerida = 'financeiro.lancamentos.acoes_em_lote_status'

    def get_permissao_requerida(self) -> str:
        if (self.request.POST.get('acao_lote') or '').strip() == 'excluir':
            return 'financeiro.lancamentos.acoes_em_lote_excluir'
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
            messages.warning(request, 'Selecione pelo menos um lançamento para aplicar uma ação em lote.')
            return self._redirect_listagem(request)

        lancamentos = _resolver_lancamentos_para_acoes_em_lote(tokens_selecao)
        if not lancamentos:
            messages.warning(request, 'Nenhum lançamento selecionado foi encontrado para ação em lote.')
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
                f'{quantidade} lançamento{sufixo} excluído{sufixo} com sucesso.',
            )
            return self._redirect_listagem(request)

        if acao_lote == 'alterar_status':
            status_validos = {
                escolha
                for escolha, _ in LancamentoFinanceiro.StatusLancamento.choices
            }
            if novo_status not in status_validos:
                messages.warning(request, 'Selecione um status válido para aplicar aos lançamentos marcados.')
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
                    'Nenhum status foi alterado porque pelo menos um lançamento selecionado '
                    'ficou inconsistente na validação. Revise os itens marcados e tente novamente.',
                )
                return self._redirect_listagem(request)

            quantidade = len(lancamentos)
            sufixo = '' if quantidade == 1 else 's'
            messages.success(
                request,
                f'Status atualizado para {quantidade} lançamento{sufixo}.',
            )
            return self._redirect_listagem(request)

        messages.warning(request, 'Escolha uma ação em lote válida para os lançamentos selecionados.')
        return self._redirect_listagem(request)


class LancamentoFinanceiroCreateView(FinanceiroFormMixin, CreateView):
    permissao_requerida = 'financeiro.lancamentos.criar'
    model = LancamentoFinanceiro
    form_class = LancamentoFinanceiroForm
    template_name = 'financeiro/lancamento_form.html'
    success_url = reverse_lazy('financeiro:lancamento-list')
    page_title = 'Novo Lancamento Financeiro'
    success_message = 'Lancamento financeiro cadastrado com sucesso.'

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
        return redirect(self.success_url)


class LancamentoFinanceiroCloneView(LancamentoFinanceiroCreateView):
    permissao_requerida = 'financeiro.lancamentos.clonar'
    page_title = 'Clonar Lancamento Financeiro'
    submit_label = 'Salvar clone'
    success_message = 'Lancamento financeiro clonado com sucesso.'

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
            return redirect(self.success_url)
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
            return redirect(self.success_url)
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
                query_string = urlencode(
                    {
                        'origem_fluxo': 'rateio_coordenado',
                        'motivo_fluxo': erro_codigo,
                    }
                )
                return redirect(f"{reverse('financeiro:lancamento-update', kwargs={'pk': representante.pk})}?{query_string}")
            messages.warning(
                request,
                'Nao foi possivel abrir uma linha representativa para este grupo. Voce foi redirecionado para a listagem principal de lancamentos.',
            )
            return redirect(self.success_url)
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
        return redirect(f"{reverse('financeiro:lancamento-list')}?{query_string}")


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
        data_recibo = self.object.data_pagamento or self.object.data_competencia
        mensagem_categoria = ''
        assinatura_padrao = AssinaturaInstitucional.objects.filter(ativo=True, padrao=True).first()
        configuracao_padrao = ConfiguracaoInstitucional.objects.filter(ativo=True, padrao=True).first()
        if self.object.categoria:
            mensagem_categoria = (self.object.categoria.mensagem_recibo or '').strip()
        context['page_title'] = f'Recibo do Lancamento {self.object.pk}'
        context['recibo_pessoa_nome'] = self.object.pessoa.nome if self.object.pessoa else '-'
        context['recibo_referente'] = self.object.descricao
        context['recibo_data_principal'] = data_recibo
        context['recibo_data_humana'] = _data_documental_por_extenso(data_recibo)
        context['recibo_valor_extenso'] = _valor_por_extenso(self.object.valor)
        context['recibo_data_fallback'] = self.object.data_pagamento is None
        context['recibo_mensagem_final'] = (
            mensagem_categoria
            or (
                (configuracao_padrao.mensagem_padrao_recibo or '').strip()
                if configuracao_padrao
                else ''
            )
            or 'Recibo emitido com base no lancamento registrado no sistema.'
        )
        context['recibo_mensagem_personalizada'] = bool(mensagem_categoria)
        context['recibo_assinatura_padrao'] = assinatura_padrao
        context['recibo_configuracao_institucional'] = configuracao_padrao
        context['recibo_nome_instituicao'] = (
            (configuracao_padrao.nome_instituicao or '').strip() if configuracao_padrao else ''
        )
        context['recibo_logo_url'] = (configuracao_padrao.logo_url or '').strip() if configuracao_padrao else ''
        context['recibo_cidade'] = (configuracao_padrao.cidade or '').strip() if configuracao_padrao else ''
        return context


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
