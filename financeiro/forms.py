from __future__ import annotations

import json
from datetime import date
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max, Q, Sum
from django.forms.models import construct_instance
from django.urls import reverse_lazy
from django.utils import timezone

from .models import (
    AlocacaoCompetenciaFinanceira,
    AssinaturaInstitucional,
    CategoriaFinanceira,
    ColunaPersonalizada,
    ConfiguracaoInstitucional,
    CentroCusto,
    ContaFinanceira,
    LinhaTabelaPersonalizada,
    LancamentoFinanceiro,
    PessoaFinanceira,
    TabelaPersonalizada,
    TipoContaFinanceira,
    ValorTabelaPersonalizada,
)

MESES_PT_BR_ABREV = (
    'Jan',
    'Fev',
    'Mar',
    'Abr',
    'Mai',
    'Jun',
    'Jul',
    'Ago',
    'Set',
    'Out',
    'Nov',
    'Dez',
)


def categorias_vinculaveis_queryset(tipo: str | None = None, categoria_extra_id: int | str | None = None):
    queryset = CategoriaFinanceira.objects.filter(categoria_pai__isnull=False)
    if tipo in {
        LancamentoFinanceiro.TipoLancamento.RECEITA,
        LancamentoFinanceiro.TipoLancamento.DESPESA,
    }:
        queryset = queryset.filter(tipo=tipo)
    if categoria_extra_id:
        queryset = queryset | CategoriaFinanceira.objects.filter(pk=categoria_extra_id)
    return queryset.order_by('tipo', 'nome')


def contas_lancamento_queryset(*conta_extra_ids: int | str | None):
    extras = [conta_id for conta_id in conta_extra_ids if conta_id]
    queryset = ContaFinanceira.objects.filter(Q(ativa=True) | Q(pk__in=extras))
    return queryset.order_by('nome')


def _parse_competencias_payload(payload: str) -> list[dict[str, str]]:
    if not payload:
        return []
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []

    linhas: list[dict[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        linhas.append(
            {
                'mes': str(item.get('mes', '') or '').strip(),
                'ano': str(item.get('ano', '') or '').strip(),
                'valor': str(item.get('valor', '') or '').strip(),
            }
        )
    return linhas


def _parse_competencias_rateio_payload(payload: str) -> dict[str, list[dict[str, str]]]:
    if not payload:
        return {}
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}

    competencias_por_categoria: dict[str, list[dict[str, str]]] = {}
    for categoria_id, linhas in data.items():
        categoria_key = str(categoria_id or '').strip()
        if not categoria_key or not isinstance(linhas, list):
            continue
        competencias_por_categoria[categoria_key] = []
        for item in linhas:
            if not isinstance(item, dict):
                continue
            competencias_por_categoria[categoria_key].append(
                {
                    'mes': str(item.get('mes', '') or '').strip(),
                    'ano': str(item.get('ano', '') or '').strip(),
                    'valor': str(item.get('valor', '') or '').strip(),
                }
            )
    return competencias_por_categoria


def _linhas_rateio_controladas(
    *,
    tipo: str | None,
    pessoa: PessoaFinanceira | None,
    rateio_linhas: list[dict[str, object]] | None,
) -> list[dict[str, object]]:
    if tipo not in {
        LancamentoFinanceiro.TipoLancamento.RECEITA,
        LancamentoFinanceiro.TipoLancamento.DESPESA,
    }:
        return []
    if not pessoa or not pessoa.contribuinte_recorrente:
        return []

    linhas_controladas: list[dict[str, object]] = []
    for linha in rateio_linhas or []:
        categoria = linha.get('categoria')
        if not categoria:
            continue
        if categoria.controla_recorrencia_competencia and categoria.permite_vinculo_em_lancamento:
            linhas_controladas.append(linha)
    return linhas_controladas


def _formatar_decimal_brl(valor: Decimal | str | None) -> str:
    if valor in (None, ''):
        return ''

    if not isinstance(valor, Decimal):
        try:
            valor = Decimal(str(valor))
        except (InvalidOperation, TypeError, ValueError):
            return ''

    valor = valor.quantize(Decimal('0.01'))
    negativo = valor < Decimal('0.00')
    valor_absoluto = abs(valor)
    inteiro, centavos = f'{valor_absoluto:.2f}'.split('.')
    inteiro_formatado = f'{int(inteiro):,}'.replace(',', '.')
    prefixo = '-R$ ' if negativo else 'R$ '
    return f'{prefixo}{inteiro_formatado},{centavos}'


def _iterar_meses_assistente(referencia: date) -> list[tuple[int, int]]:
    base_indice = referencia.year * 12 + (referencia.month - 1)
    competencias: list[tuple[int, int]] = []
    for deslocamento in range(-5, 6):
        indice_atual = base_indice + deslocamento
        ano_atual = indice_atual // 12
        mes_atual = (indice_atual % 12) + 1
        competencias.append((ano_atual, mes_atual))
    return competencias


def _montar_assistente_meses(
    *,
    referencia: date,
    pessoa_id: int | None,
    categoria_id: int | None,
    linhas_atuais: list[dict[str, str]],
    registro_lookup: dict[str, dict[str, dict[str, str]]],
) -> list[dict[str, object]]:
    linhas_por_competencia: dict[str, str] = {}
    for linha in linhas_atuais:
        mes_raw = str(linha.get('mes', '') or '').strip()
        ano_raw = str(linha.get('ano', '') or '').strip()
        valor_raw = str(linha.get('valor', '') or '').strip()
        if not mes_raw or not ano_raw:
            continue
        try:
            chave = f'{int(ano_raw):04d}-{int(mes_raw):02d}'
        except (TypeError, ValueError):
            continue
        linhas_por_competencia[chave] = valor_raw

    registros_categoria = (
        registro_lookup.get(str(pessoa_id or ''), {}).get(str(categoria_id or ''), {})
        if pessoa_id and categoria_id
        else {}
    )

    meses = []
    for ano_competencia, mes_competencia in _iterar_meses_assistente(referencia):
        chave = f'{ano_competencia:04d}-{mes_competencia:02d}'
        valor_registrado = registros_categoria.get(chave, '')
        valor_lancamento = linhas_por_competencia.get(chave, '')
        possui_registro = bool(valor_registrado and Decimal(valor_registrado or '0.00') > Decimal('0.00'))
        meses.append(
            {
                'chave': chave,
                'mes': mes_competencia,
                'ano': ano_competencia,
                'label': f'{MESES_PT_BR_ABREV[mes_competencia - 1]}/{ano_competencia}',
                'ja_registrado': valor_registrado,
                'ja_registrado_texto': _formatar_decimal_brl(valor_registrado) if possui_registro else '',
                'ja_possui_contribuicao': possui_registro,
                'status_texto': 'Ja possui contribuicao' if possui_registro else 'Sem quitacao registrada',
                'valor_lancamento': valor_lancamento,
                'valor_lancamento_texto': _formatar_decimal_brl(valor_lancamento).replace('R$ ', '')
                if valor_lancamento
                else '',
            }
        )
    return meses


def _montar_lookup_competencias_registradas(
    *,
    excluir_lancamento_ids: set[int] | None = None,
) -> dict[str, dict[str, dict[str, str]]]:
    queryset = AlocacaoCompetenciaFinanceira.objects.filter(
        categoria__controla_recorrencia_competencia=True,
        lancamento__pessoa__contribuinte_recorrente=True,
    )
    if excluir_lancamento_ids:
        queryset = queryset.exclude(lancamento_id__in=excluir_lancamento_ids)

    lookup: dict[str, dict[str, dict[str, str]]] = {}
    for registro in queryset.values(
        'lancamento__pessoa_id',
        'categoria_id',
        'ano_competencia',
        'mes_competencia',
    ).annotate(total=Sum('valor_alocado')):
        pessoa_key = str(registro['lancamento__pessoa_id'])
        categoria_key = str(registro['categoria_id'])
        competencia_key = f"{registro['ano_competencia']:04d}-{registro['mes_competencia']:02d}"
        lookup.setdefault(pessoa_key, {}).setdefault(categoria_key, {})[competencia_key] = (
            f"{registro['total']:.2f}"
        )
    return lookup


class ContaFinanceiraForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_conta'].queryset = TipoContaFinanceira.objects.filter(ativo=True).order_by('ordem', 'nome')
        self.fields['tipo_conta'].required = False
        self.fields['tipo_conta'].empty_label = 'Outros'
        self.fields['disponibilidade'].required = False
        self.fields['mensagem_indisponibilidade'].required = False

    def clean_tipo_conta(self):
        tipo_conta = self.cleaned_data.get('tipo_conta')
        if tipo_conta:
            return tipo_conta
        return TipoContaFinanceira.objects.filter(codigo='outros').first()

    def clean_disponibilidade(self):
        return (
            self.cleaned_data.get('disponibilidade')
            or ContaFinanceira.DisponibilidadeConta.DISPONIVEL
        )

    class Meta:
        model = ContaFinanceira
        fields = [
            'nome',
            'descricao',
            'saldo_inicial',
            'data_saldo_inicial',
            'tipo_conta',
            'disponibilidade',
            'mensagem_indisponibilidade',
            'ativa',
        ]
        widgets = {
            'data_saldo_inicial': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'mensagem_indisponibilidade': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'tipo_conta': 'Tipo de conta',
            'disponibilidade': 'Disponibilidade',
            'mensagem_indisponibilidade': 'Mensagem de indisponibilidade',
        }
        help_texts = {
            'mensagem_indisponibilidade': 'Opcional. Use apenas quando a conta for vinculada ou indisponivel.',
        }


class CentroCustoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['codigo'].required = False
        self.fields['codigo'].help_text = 'Opcional. Se vazio, sera gerado automaticamente.'

    class Meta:
        model = CentroCusto
        fields = [
            'codigo',
            'nome',
            'ativo',
        ]


class PessoaFinanceiraForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['codigo'].required = False
        self.fields['codigo'].help_text = 'Opcional. Se vazio, sera gerado automaticamente.'

    class Meta:
        model = PessoaFinanceira
        fields = [
            'codigo',
            'nome',
            'tipo_pessoa',
            'documento',
            'telefone',
            'email',
            'observacoes',
            'contribuinte_recorrente',
            'ativo',
        ]
        labels = {
            'tipo_pessoa': 'Tipo favorecido',
            'contribuinte_recorrente': 'Contribuinte recorrente',
        }


class CategoriaFinanceiraForm(forms.ModelForm):
    class Meta:
        model = CategoriaFinanceira
        fields = [
            'nome',
            'tipo',
            'categoria_pai',
            'controla_recorrencia_competencia',
            'mensagem_recibo',
            'ativo',
        ]
        widgets = {
            'mensagem_recibo': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Mensagem opcional exibida no rodape do recibo desta categoria.',
                }
            ),
        }
        help_texts = {
            'controla_recorrencia_competencia': (
                'Marque quando esta subcategoria deve entrar no controle de recorrencia por competencia.'
            ),
            'mensagem_recibo': (
                'Opcional. Quando preenchida, substitui a mensagem padrao simples do recibo para esta categoria.'
            ),
        }


class AssinaturaInstitucionalForm(forms.ModelForm):
    class Meta:
        model = AssinaturaInstitucional
        fields = [
            'nome',
            'assinatura_texto',
            'nome_exibicao',
            'cargo',
            'ativo',
            'padrao',
        ]
        help_texts = {
            'assinatura_texto': 'Texto manuscrito que sera exibido no recibo.',
            'nome_exibicao': 'Opcional. Nome abaixo da assinatura no recibo.',
            'cargo': 'Opcional. Cargo exibido abaixo do nome, quando informado.',
            'padrao': 'Quando marcada, esta assinatura passa a ser a usada por padrao nos recibos.',
        }


class ConfiguracaoInstitucionalForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoInstitucional
        fields = [
            'nome_instituicao',
            'cidade',
            'logo_url',
            'mensagem_padrao_recibo',
            'ativo',
            'padrao',
        ]
        widgets = {
            'mensagem_padrao_recibo': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Mensagem padrao usada no recibo quando a categoria nao tiver mensagem propria.',
                }
            ),
        }
        help_texts = {
            'logo_url': 'Opcional. Informe uma URL de logo para o cabecalho do recibo.',
            'mensagem_padrao_recibo': 'Opcional. Se vazia, o recibo continua usando o fallback simples ja existente.',
            'padrao': 'Quando marcada, esta configuracao passa a ser a usada por padrao no recibo.',
        }


class TabelaPersonalizadaForm(forms.ModelForm):
    class Meta:
        model = TabelaPersonalizada
        fields = [
            'nome',
            'descricao',
            'status',
            'ordem',
        ]
        widgets = {
            'descricao': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Descreva brevemente o objetivo deste controle interno.',
                }
            ),
            'ordem': forms.NumberInput(attrs={'min': 0}),
        }
        help_texts = {
            'descricao': 'Opcional. Use para explicar o uso interno da tabela.',
            'status': 'Controla apenas a disponibilidade documental desta tabela no MVP.',
            'ordem': 'Opcional. Valores menores aparecem primeiro na listagem.',
        }


class ColunaPersonalizadaForm(forms.ModelForm):
    opcoes_lista = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 6,
                'placeholder': 'Uma opcao por linha.',
            }
        ),
        label='Opcoes da lista',
        help_text='Use apenas para o tipo Lista de opcoes. Informe uma opcao por linha, com maximo de 20 itens.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tipos_permitidos = [
            escolha
            for escolha in self.fields['tipo_dado'].choices
            if escolha[0] != ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA
        ]
        self.fields['tipo_dado'].choices = tipos_permitidos
        self.fields['ordem'].widget.attrs.update({'min': 0})

        configuracao = self.instance.configuracao_json if getattr(self.instance, 'pk', None) else {}
        if isinstance(configuracao, dict):
            opcoes = configuracao.get('opcoes', [])
            if isinstance(opcoes, list) and not self.is_bound:
                self.initial['opcoes_lista'] = '\n'.join(
                    opcao for opcao in opcoes if isinstance(opcao, str) and opcao.strip()
                )

    def clean_tipo_dado(self):
        tipo_dado = self.cleaned_data.get('tipo_dado')
        if tipo_dado == ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA:
            raise ValidationError('Formula controlada ainda nao pode ser configurada nesta etapa.')
        return tipo_dado

    def clean_opcoes_lista(self):
        conteudo = (self.cleaned_data.get('opcoes_lista') or '').replace('\r\n', '\n')
        linhas = [linha.strip() for linha in conteudo.split('\n')]
        opcoes = [linha for linha in linhas if linha]

        if not opcoes:
            return []

        opcoes_normalizadas: set[str] = set()
        for opcao in opcoes:
            opcao_normalizada = opcao.casefold()
            if opcao_normalizada in opcoes_normalizadas:
                raise ValidationError('Lista de opcoes nao pode repetir valores equivalentes.')
            opcoes_normalizadas.add(opcao_normalizada)

        if len(opcoes) > 20:
            raise ValidationError('Lista de opcoes aceita no maximo 20 itens no MVP.')

        return opcoes

    def clean(self):
        cleaned_data = super().clean()
        tipo_dado = cleaned_data.get('tipo_dado')
        opcoes = cleaned_data.get('opcoes_lista') or []

        if tipo_dado == ColunaPersonalizada.TipoDado.LISTA_OPCOES and not opcoes:
            self.add_error('opcoes_lista', 'Informe ao menos uma opcao para este tipo de coluna.')

        if tipo_dado != ColunaPersonalizada.TipoDado.LISTA_OPCOES and opcoes:
            self.add_error('opcoes_lista', 'As opcoes so podem ser preenchidas para o tipo Lista de opcoes.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.calculada = False

        tipo_dado = self.cleaned_data.get('tipo_dado')
        opcoes = self.cleaned_data.get('opcoes_lista') or []
        if tipo_dado == ColunaPersonalizada.TipoDado.LISTA_OPCOES:
            instance.configuracao_json = {'opcoes': opcoes}
        else:
            instance.configuracao_json = {}

        if commit:
            instance.save()
        return instance

    class Meta:
        model = ColunaPersonalizada
        fields = [
            'nome',
            'tipo_dado',
            'obrigatoria',
            'visivel',
            'ordem',
            'status',
        ]
        widgets = {
            'ordem': forms.NumberInput(attrs={'min': 0}),
        }
        help_texts = {
            'visivel': 'Controla apenas a exibicao futura da coluna nas telas da frente.',
            'ordem': 'Valores menores aparecem primeiro na estrutura da tabela.',
            'status': 'Use para manter a coluna ativa, inativa ou arquivada na estrutura.',
        }


class TabelaPersonalizadaLinhaForm(forms.Form):
    campo_prefixo = 'coluna_'

    @classmethod
    def colunas_editaveis_queryset(cls, tabela: TabelaPersonalizada):
        return (
            ColunaPersonalizada.objects.filter(
                tabela=tabela,
                status=ColunaPersonalizada.StatusColuna.ATIVA,
                visivel=True,
                calculada=False,
            )
            .exclude(tipo_dado=ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA)
            .order_by('ordem', 'nome', 'pk')
        )

    @classmethod
    def campo_coluna_nome(cls, coluna_id: int) -> str:
        return f'{cls.campo_prefixo}{coluna_id}'

    def __init__(self, *args, tabela: TabelaPersonalizada, linha: LinhaTabelaPersonalizada | None = None, **kwargs):
        self.tabela = tabela
        self.linha = linha
        self.colunas_dinamicas = list(self.colunas_editaveis_queryset(tabela))
        self.valores_existentes: dict[int, ValorTabelaPersonalizada] = {}
        if self.linha:
            self.valores_existentes = {
                valor.coluna_id: valor
                for valor in self.linha.valores.select_related('coluna')
            }

        super().__init__(*args, **kwargs)

        for coluna in self.colunas_dinamicas:
            field_name = self.campo_coluna_nome(coluna.pk)
            self.fields[field_name] = self._build_field(coluna)
            if not self.is_bound:
                self.initial[field_name] = self._valor_inicial_coluna(coluna)

    def _build_field(self, coluna: ColunaPersonalizada) -> forms.Field:
        comum = {
            'label': coluna.nome,
            'required': coluna.obrigatoria,
        }

        if coluna.tipo_dado == ColunaPersonalizada.TipoDado.TEXTO_CURTO:
            return forms.CharField(max_length=120, **comum)
        if coluna.tipo_dado == ColunaPersonalizada.TipoDado.TEXTO_LONGO:
            return forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), **comum)
        if coluna.tipo_dado == ColunaPersonalizada.TipoDado.INTEIRO:
            return forms.IntegerField(**comum)
        if coluna.tipo_dado == ColunaPersonalizada.TipoDado.DECIMAL:
            return forms.DecimalField(max_digits=18, decimal_places=6, **comum)
        if coluna.tipo_dado == ColunaPersonalizada.TipoDado.MONETARIO:
            return forms.DecimalField(max_digits=18, decimal_places=2, **comum)
        if coluna.tipo_dado == ColunaPersonalizada.TipoDado.PERCENTUAL:
            return forms.DecimalField(max_digits=18, decimal_places=2, **comum)
        if coluna.tipo_dado == ColunaPersonalizada.TipoDado.DATA:
            return forms.DateField(
                widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
                input_formats=['%Y-%m-%d'],
                **comum,
            )
        if coluna.tipo_dado == ColunaPersonalizada.TipoDado.MES_COMPETENCIA:
            return forms.RegexField(
                regex=r'^(0[1-9]|1[0-2])/\d{4}$',
                error_messages={'invalid': 'Use o formato MM/AAAA.'},
                **comum,
            )
        if coluna.tipo_dado == ColunaPersonalizada.TipoDado.BOOLEANO:
            choices = [('1', 'Sim'), ('0', 'Nao')]
            if not coluna.obrigatoria:
                choices = [('', 'Selecione')] + choices
            return forms.TypedChoiceField(
                choices=choices,
                coerce=lambda valor: {'1': True, '0': False}.get(valor, None),
                empty_value=None,
                **comum,
            )
        if coluna.tipo_dado == ColunaPersonalizada.TipoDado.LISTA_OPCOES:
            configuracao = coluna.configuracao_json if isinstance(coluna.configuracao_json, dict) else {}
            opcoes = configuracao.get('opcoes', [])
            choices = [(opcao, opcao) for opcao in opcoes if isinstance(opcao, str) and opcao.strip()]
            if not coluna.obrigatoria:
                choices = [('', 'Selecione')] + choices
            return forms.ChoiceField(choices=choices, **comum)

        return forms.CharField(disabled=True, required=False, label=coluna.nome)

    def _valor_inicial_coluna(self, coluna: ColunaPersonalizada):
        valor = self.valores_existentes.get(coluna.pk)
        if not valor:
            return None

        if coluna.tipo_dado in {
            ColunaPersonalizada.TipoDado.TEXTO_CURTO,
            ColunaPersonalizada.TipoDado.TEXTO_LONGO,
            ColunaPersonalizada.TipoDado.MES_COMPETENCIA,
            ColunaPersonalizada.TipoDado.LISTA_OPCOES,
        }:
            return valor.valor_texto
        if coluna.tipo_dado in {
            ColunaPersonalizada.TipoDado.INTEIRO,
            ColunaPersonalizada.TipoDado.DECIMAL,
            ColunaPersonalizada.TipoDado.MONETARIO,
            ColunaPersonalizada.TipoDado.PERCENTUAL,
        }:
            return valor.valor_numero
        if coluna.tipo_dado == ColunaPersonalizada.TipoDado.DATA:
            return valor.valor_data
        if coluna.tipo_dado == ColunaPersonalizada.TipoDado.BOOLEANO:
            if valor.valor_booleano is None:
                return None
            return '1' if valor.valor_booleano else '0'
        return None

    def _valor_vazio(self, coluna: ColunaPersonalizada, valor) -> bool:
        if coluna.tipo_dado == ColunaPersonalizada.TipoDado.BOOLEANO:
            return valor is None
        if valor is None:
            return True
        if isinstance(valor, str):
            return not valor.strip()
        return False

    def _montar_payload_valor(self, coluna: ColunaPersonalizada, valor) -> dict[str, object]:
        payload: dict[str, object] = {
            'valor_texto': '',
            'valor_numero': None,
            'valor_data': None,
            'valor_booleano': None,
            'valor_json': None,
            'valor_calculado': None,
        }

        if coluna.tipo_dado in {
            ColunaPersonalizada.TipoDado.TEXTO_CURTO,
            ColunaPersonalizada.TipoDado.TEXTO_LONGO,
            ColunaPersonalizada.TipoDado.MES_COMPETENCIA,
            ColunaPersonalizada.TipoDado.LISTA_OPCOES,
        }:
            payload['valor_texto'] = (valor or '').strip()
        elif coluna.tipo_dado in {
            ColunaPersonalizada.TipoDado.INTEIRO,
            ColunaPersonalizada.TipoDado.DECIMAL,
            ColunaPersonalizada.TipoDado.MONETARIO,
            ColunaPersonalizada.TipoDado.PERCENTUAL,
        }:
            payload['valor_numero'] = valor
        elif coluna.tipo_dado == ColunaPersonalizada.TipoDado.DATA:
            payload['valor_data'] = valor
        elif coluna.tipo_dado == ColunaPersonalizada.TipoDado.BOOLEANO:
            payload['valor_booleano'] = valor

        return payload

    def save(self, *, usuario=None):
        with transaction.atomic():
            if self.linha is None:
                self.linha = LinhaTabelaPersonalizada.objects.create(
                    tabela=self.tabela,
                    ordem=(self.tabela.linhas.aggregate(maior=Max('ordem')).get('maior') or 0) + 1,
                    criado_por=usuario,
                    atualizado_por=usuario,
                )
            else:
                if not self.linha.criado_por:
                    self.linha.criado_por = usuario
                self.linha.atualizado_por = usuario
                self.linha.save()

            for coluna in self.colunas_dinamicas:
                field_name = self.campo_coluna_nome(coluna.pk)
                valor_limpo = self.cleaned_data.get(field_name)
                queryset = ValorTabelaPersonalizada.objects.filter(linha=self.linha, coluna=coluna)

                if self._valor_vazio(coluna, valor_limpo):
                    queryset.delete()
                    continue

                payload = self._montar_payload_valor(coluna, valor_limpo)
                queryset.update_or_create(
                    linha=self.linha,
                    coluna=coluna,
                    defaults=payload,
                )

        return self.linha


class LancamentoFinanceiroForm(forms.ModelForm):
    lancamento_com_rateio = forms.BooleanField(required=False, label='Lancamento com rateio')
    salvar_como_regra_automatica = forms.BooleanField(
        required=False,
        label='Salvar como regra automatica',
    )
    valor_total_documento = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        label='Valor total do documento',
        help_text='Usado apenas para validar o fechamento do rateio nesta etapa.',
    )
    rateio_payload = forms.CharField(required=False, widget=forms.HiddenInput())
    competencias_payload = forms.CharField(required=False, widget=forms.HiddenInput())
    competencias_rateio_payload = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rateio_group_token = self.instance.grupo_rateio or uuid4().hex
        self.rateio_linhas_iniciais = []
        self.competencias_linhas_iniciais = []
        self.competencias_rateio_iniciais: dict[str, list[dict[str, str]]] = {}
        self.assistente_competencia_bloco_visivel = False
        self.assistente_competencia_meses_sugeridos: list[dict[str, object]] = []
        self.assistente_competencia_registro_lookup = _montar_lookup_competencias_registradas(
            excluir_lancamento_ids={self.instance.pk} if self.instance.pk else set()
        )
        tipo_atual = self._get_tipo_atual()
        categoria_inicial = self.initial.get('categoria') or self.instance.categoria
        categoria_inicial_id = getattr(categoria_inicial, 'pk', categoria_inicial)
        self.fields['categoria'].queryset = categorias_vinculaveis_queryset(
            tipo=tipo_atual,
            categoria_extra_id=categoria_inicial_id,
        )
        self.fields['conta'].queryset = contas_lancamento_queryset(self.instance.conta_id)
        self.fields['conta_destino'].queryset = contas_lancamento_queryset(self.instance.conta_destino_id)
        for field_name in ('data_competencia', 'data_pagamento'):
            self.fields[field_name].widget.format = '%Y-%m-%d'
            if self.is_bound:
                continue
            valor_inicial = self.initial.get(field_name) or getattr(self.instance, field_name, None)
            if valor_inicial:
                self.initial[field_name] = (
                    valor_inicial.strftime('%Y-%m-%d')
                    if hasattr(valor_inicial, 'strftime')
                    else str(valor_inicial)
                )
        self.fields['tipo'].widget.attrs.update({'data-financeiro-tipo': 'true'})
        self.fields['conta_destino'].widget.attrs.update({'data-financeiro-conta-destino': 'true'})
        self.fields['conta'].error_messages['required'] = 'Informe a conta de origem.'
        self.fields['pessoa'].required = False
        self.fields['pessoa'].label = 'Favorecido'
        self.fields['categoria'].required = False
        self.fields['valor'].required = False
        self.fields['data_pagamento'].required = True
        self.fields['data_pagamento'].error_messages['required'] = 'Informe a data de pagamento.'
        self.fields['tipo'].choices = [choice for choice in self.fields['tipo'].choices if choice[0] != '']
        if not self.instance.pk and not self.is_bound and not self.initial.get('tipo'):
            self.initial['tipo'] = LancamentoFinanceiro.TipoLancamento.RECEITA
            self.fields['tipo'].initial = LancamentoFinanceiro.TipoLancamento.RECEITA
        self.fields['lancamento_com_rateio'].initial = bool(self.instance.pk and self.instance.com_rateio)
        if self.instance.pk:
            self.fields['lancamento_com_rateio'].widget = forms.HiddenInput()
            self.fields['salvar_como_regra_automatica'].widget = forms.HiddenInput()
            self.fields['valor_total_documento'].widget = forms.HiddenInput()
            self.fields['rateio_payload'].widget = forms.HiddenInput()
        if self.is_bound:
            self.rateio_linhas_iniciais = self._parse_rateio_payload(self.data.get('rateio_payload', ''))
            self.competencias_linhas_iniciais = _parse_competencias_payload(self.data.get('competencias_payload', ''))
            self.competencias_rateio_iniciais = _parse_competencias_rateio_payload(
                self.data.get('competencias_rateio_payload', '')
            )
        else:
            if self.instance.pk:
                self.competencias_linhas_iniciais = [
                    {
                        'mes': str(alocacao.mes_competencia),
                        'ano': str(alocacao.ano_competencia),
                        'valor': f'{alocacao.valor_alocado:.2f}',
                    }
                    for alocacao in self.instance.alocacoes_competencia.order_by(
                        'ano_competencia',
                        'mes_competencia',
                        'pk',
                    )
                ]
            else:
                self.rateio_linhas_iniciais = [
                    {'categoria': '', 'valor': ''},
                    {'categoria': '', 'valor': ''},
                ]
        self.competencias_bloco_visivel = bool(
            self.competencias_linhas_iniciais or (
                self.instance.pk and self.instance.usa_controle_competencia()
            )
        )
        self.competencias_rateio_bloco_visivel = bool(self.competencias_rateio_iniciais)
        autocomplete_urls = {
            'pessoa': reverse_lazy('financeiro:autocomplete-pessoa'),
            'categoria': reverse_lazy('financeiro:autocomplete-categoria'),
            'centro_custo': reverse_lazy('financeiro:autocomplete-centro-custo'),
            'conta': reverse_lazy('financeiro:autocomplete-conta'),
            'conta_destino': reverse_lazy('financeiro:autocomplete-conta'),
        }
        for field_name, url in autocomplete_urls.items():
            self.fields[field_name].widget.attrs.update(
                {
                    'data-financeiro-autocomplete': 'true',
                    'data-autocomplete-url': str(url),
                }
            )
        self.fields['categoria'].widget.attrs.pop('required', None)
        self.fields['pessoa'].widget.attrs.pop('required', None)
        self._atualizar_assistente_competencia()

    def _get_tipo_atual(self) -> str:
        if self.is_bound:
            return (self.data.get(self.add_prefix('tipo')) or '').strip()
        return (
            self.initial.get('tipo')
            or self.instance.tipo
            or LancamentoFinanceiro.TipoLancamento.RECEITA
        )

    def _resolver_data_referencia_assistente(self) -> date:
        data_referencia = None
        if self.is_bound:
            data_referencia_raw = (
                self.data.get(self.add_prefix('data_competencia'))
                or self.data.get(self.add_prefix('data_pagamento'))
                or ''
            ).strip()
            if data_referencia_raw:
                try:
                    data_referencia = date.fromisoformat(data_referencia_raw)
                except ValueError:
                    data_referencia = None

        if data_referencia is None:
            data_referencia = (
                self.initial.get('data_competencia')
                or getattr(self.instance, 'data_competencia', None)
                or self.initial.get('data_pagamento')
                or getattr(self.instance, 'data_pagamento', None)
            )

        if hasattr(data_referencia, 'date'):
            data_referencia = data_referencia.date()
        if isinstance(data_referencia, date):
            return data_referencia
        return timezone.localdate()

    def _resolver_pessoa_atual(self) -> PessoaFinanceira | None:
        if self.is_bound:
            pessoa_id = (self.data.get(self.add_prefix('pessoa')) or '').strip()
            if pessoa_id.isdigit():
                return PessoaFinanceira.objects.filter(pk=int(pessoa_id)).first()
            return None
        pessoa = self.initial.get('pessoa') or getattr(self.instance, 'pessoa', None)
        if isinstance(pessoa, PessoaFinanceira) or pessoa is None:
            return pessoa
        if str(pessoa).isdigit():
            return PessoaFinanceira.objects.filter(pk=int(pessoa)).first()
        return None

    def _resolver_categoria_atual(self) -> CategoriaFinanceira | None:
        if self.is_bound:
            categoria_id = (self.data.get(self.add_prefix('categoria')) or '').strip()
            if categoria_id.isdigit():
                return CategoriaFinanceira.objects.filter(pk=int(categoria_id)).first()
            return None
        categoria = self.initial.get('categoria') or getattr(self.instance, 'categoria', None)
        if isinstance(categoria, CategoriaFinanceira) or categoria is None:
            return categoria
        if str(categoria).isdigit():
            return CategoriaFinanceira.objects.filter(pk=int(categoria)).first()
        return None

    def _lancamento_com_rateio_raw(self) -> bool:
        if self.instance.pk:
            return False
        if self.is_bound:
            return bool(self.data.get(self.add_prefix('lancamento_com_rateio')))
        return bool(self.initial.get('lancamento_com_rateio'))

    def _atualizar_assistente_competencia(self, cleaned_data: dict | None = None) -> None:
        if cleaned_data is None:
            tipo = self._get_tipo_atual()
            pessoa = self._resolver_pessoa_atual()
            categoria = self._resolver_categoria_atual()
            lancamento_com_rateio = self._lancamento_com_rateio_raw()
        else:
            tipo = cleaned_data.get('tipo')
            pessoa = cleaned_data.get('pessoa')
            categoria = cleaned_data.get('categoria')
            lancamento_com_rateio = bool(cleaned_data.get('lancamento_com_rateio')) and not self.instance.pk

        aplicavel = bool(
            not lancamento_com_rateio
            and tipo in {
                LancamentoFinanceiro.TipoLancamento.RECEITA,
                LancamentoFinanceiro.TipoLancamento.DESPESA,
            }
            and pessoa
            and categoria
            and pessoa.contribuinte_recorrente
            and categoria.controla_recorrencia_competencia
            and categoria.permite_vinculo_em_lancamento
        )
        self.assistente_competencia_bloco_visivel = bool(
            aplicavel
            or self.competencias_linhas_iniciais
            or (self.instance.pk and self.instance.usa_controle_competencia())
        )
        self.assistente_competencia_meses_sugeridos = _montar_assistente_meses(
            referencia=self._resolver_data_referencia_assistente(),
            pessoa_id=getattr(pessoa, 'pk', None),
            categoria_id=getattr(categoria, 'pk', None),
            linhas_atuais=self.competencias_linhas_iniciais,
            registro_lookup=self.assistente_competencia_registro_lookup,
        )

    def _parse_rateio_payload(self, payload: str) -> list[dict[str, str]]:
        if not payload:
            return []
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return []
        if not isinstance(data, list):
            return []
        linhas: list[dict[str, str]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            linhas.append(
                {
                    'categoria': str(item.get('categoria', '') or '').strip(),
                    'valor': str(item.get('valor', '') or '').strip(),
                }
            )
        return linhas

    def _parse_competencias_payload(self, payload: str) -> list[dict[str, str]]:
        return _parse_competencias_payload(payload)

    def _lancamento_requer_competencias(
        self,
        cleaned_data: dict,
        *,
        lancamento_com_rateio: bool,
    ) -> bool:
        if lancamento_com_rateio:
            return False

        tipo = cleaned_data.get('tipo')
        pessoa = cleaned_data.get('pessoa')
        categoria = cleaned_data.get('categoria')
        return bool(
            tipo in {
                LancamentoFinanceiro.TipoLancamento.RECEITA,
                LancamentoFinanceiro.TipoLancamento.DESPESA,
            }
            and pessoa
            and categoria
            and pessoa.contribuinte_recorrente
            and categoria.controla_recorrencia_competencia
            and categoria.permite_vinculo_em_lancamento
        )

    def _validar_competencias_linhas(
        self,
        linhas_brutas: list[dict[str, str]],
        *,
        field_name: str,
        empty_message: str,
        line_prefix: str = '',
    ) -> tuple[list[dict[str, object]], Decimal, bool]:
        if not linhas_brutas:
            self.add_error(field_name, empty_message)
            return [], Decimal('0.00'), True

        linhas_validas: list[dict[str, object]] = []
        soma_competencias = Decimal('0.00')
        competencias_vistas: set[tuple[int, int]] = set()
        houve_erro_linha = False
        for indice, linha in enumerate(linhas_brutas, start=1):
            mes_raw = linha.get('mes', '')
            ano_raw = linha.get('ano', '')
            valor_raw = linha.get('valor', '')
            if not mes_raw and not ano_raw and not valor_raw:
                continue

            try:
                mes = int(mes_raw)
            except (TypeError, ValueError):
                self.add_error(field_name, f'{line_prefix}Linha {indice}: informe um mes valido.')
                houve_erro_linha = True
                continue

            try:
                ano = int(ano_raw)
            except (TypeError, ValueError):
                self.add_error(field_name, f'{line_prefix}Linha {indice}: informe um ano valido.')
                houve_erro_linha = True
                continue

            try:
                valor = Decimal(valor_raw)
            except (InvalidOperation, TypeError):
                self.add_error(field_name, f'{line_prefix}Linha {indice}: informe um valor valido.')
                houve_erro_linha = True
                continue

            if mes < 1 or mes > 12:
                self.add_error(field_name, f'{line_prefix}Linha {indice}: o mes precisa ficar entre 1 e 12.')
                houve_erro_linha = True
                continue

            if ano < 1900 or ano > 9999:
                self.add_error(field_name, f'{line_prefix}Linha {indice}: informe um ano valido.')
                houve_erro_linha = True
                continue

            if valor <= Decimal('0.00'):
                self.add_error(field_name, f'{line_prefix}Linha {indice}: o valor precisa ser positivo.')
                houve_erro_linha = True
                continue

            competencia_key = (ano, mes)
            if competencia_key in competencias_vistas:
                self.add_error(
                    field_name,
                    f'{line_prefix}Ja existe uma competencia informada para este mes/ano. Agrupe o valor em uma unica linha.',
                )
                houve_erro_linha = True
                continue

            competencias_vistas.add(competencia_key)
            linhas_validas.append(
                {
                    'mes_competencia': mes,
                    'ano_competencia': ano,
                    'valor_alocado': valor,
                }
            )
            soma_competencias += valor

        if not linhas_validas:
            self.add_error(field_name, empty_message)
            return [], Decimal('0.00'), True

        return linhas_validas, soma_competencias, houve_erro_linha

    def _validar_competencias(self, cleaned_data: dict) -> None:
        linhas_brutas = self._parse_competencias_payload(cleaned_data.get('competencias_payload', ''))
        self.competencias_linhas_iniciais = linhas_brutas or [{'mes': '', 'ano': '', 'valor': ''}]
        linhas_validas, soma_competencias, houve_erro_linha = self._validar_competencias_linhas(
            linhas_brutas,
            field_name='competencias_payload',
            empty_message='Informe ao menos uma competencia atendida.',
        )
        if not linhas_validas:
            cleaned_data['competencias_linhas'] = []
            return

        valor_controlado = cleaned_data.get('valor')
        if not houve_erro_linha and (valor_controlado is None or soma_competencias != valor_controlado):
            self.add_error(
                'competencias_payload',
                'A soma das competencias deve ser igual ao valor controlado do lancamento.',
            )

        cleaned_data['competencias_linhas'] = linhas_validas

    def _validar_competencias_rateio(self, cleaned_data: dict) -> None:
        competencias_por_categoria_brutas = _parse_competencias_rateio_payload(
            cleaned_data.get('competencias_rateio_payload', '')
        )
        self.competencias_rateio_iniciais = competencias_por_categoria_brutas
        linhas_controladas = _linhas_rateio_controladas(
            tipo=cleaned_data.get('tipo'),
            pessoa=cleaned_data.get('pessoa'),
            rateio_linhas=cleaned_data.get('rateio_linhas'),
        )
        self.competencias_rateio_bloco_visivel = bool(
            linhas_controladas or self.competencias_rateio_iniciais
        )
        if not linhas_controladas:
            cleaned_data['competencias_rateio_por_categoria'] = {}
            return

        competencias_rateio_por_categoria: dict[int, list[dict[str, object]]] = {}
        for linha in linhas_controladas:
            categoria = linha['categoria']
            categoria_key = str(categoria.pk)
            linhas_brutas = competencias_por_categoria_brutas.get(categoria_key, [])
            linhas_validas, soma_competencias, houve_erro_linha = self._validar_competencias_linhas(
                linhas_brutas,
                field_name='competencias_rateio_payload',
                empty_message=f'Informe ao menos uma competencia atendida para a subcategoria "{categoria}".',
                line_prefix=f'{categoria}: ',
            )
            if not linhas_validas:
                continue

            valor_controlado = linha['valor']
            if not houve_erro_linha and soma_competencias != valor_controlado:
                self.add_error(
                    'competencias_rateio_payload',
                    f'A soma das competencias deve ser igual ao valor controlado da subcategoria no rateio: {categoria}.',
                )
                continue

            competencias_rateio_por_categoria[categoria.pk] = linhas_validas

        cleaned_data['competencias_rateio_por_categoria'] = competencias_rateio_por_categoria

    def _limpar_rateio(self, cleaned_data: dict) -> None:
        cleaned_data['lancamento_com_rateio'] = False
        cleaned_data['valor_total_documento'] = None
        cleaned_data['rateio_linhas'] = []

    def _validar_rateio(self, cleaned_data: dict) -> None:
        tipo = cleaned_data.get('tipo')
        if tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
            self.add_error('lancamento_com_rateio', 'Transferencia nao pode usar rateio nesta primeira versao.')
            return

        valor_total = cleaned_data.get('valor_total_documento')
        if valor_total is None:
            self.add_error('valor_total_documento', 'Informe o valor total do documento para validar o rateio.')

        linhas_brutas = self._parse_rateio_payload(cleaned_data.get('rateio_payload', ''))
        self.rateio_linhas_iniciais = linhas_brutas or [
            {'categoria': '', 'valor': ''},
            {'categoria': '', 'valor': ''},
        ]
        if not linhas_brutas:
            self.add_error('rateio_payload', 'Informe ao menos 2 linhas de rateio validas.')
            return

        linhas_validas = 0
        soma_rateio = Decimal('0.00')
        rateio_por_categoria: dict[int, dict[str, object]] = {}
        categorias_disponiveis = {
            str(categoria.pk): categoria for categoria in categorias_vinculaveis_queryset(tipo)
        }

        for indice, linha in enumerate(linhas_brutas, start=1):
            categoria_id = linha.get('categoria', '')
            valor_raw = linha.get('valor', '')
            if not categoria_id and not valor_raw:
                continue

            linhas_validas += 1
            categoria = categorias_disponiveis.get(categoria_id)
            if categoria is None:
                self.add_error('rateio_payload', f'Linha {indice}: informe uma categoria valida.')
                continue

            if not categoria.permite_vinculo_em_lancamento:
                self.add_error(
                    'rateio_payload',
                    f'Linha {indice}: selecione uma subcategoria valida. Categoria pai nao pode ser usada no rateio.',
                )
                continue

            try:
                valor = Decimal(valor_raw)
            except (InvalidOperation, TypeError):
                self.add_error('rateio_payload', f'Linha {indice}: informe um valor valido.')
                continue

            if valor <= Decimal('0.00'):
                self.add_error('rateio_payload', f'Linha {indice}: o valor precisa ser positivo.')
                continue

            soma_rateio += valor
            if categoria.pk not in rateio_por_categoria:
                rateio_por_categoria[categoria.pk] = {'categoria': categoria, 'valor': Decimal('0.00')}
            rateio_por_categoria[categoria.pk]['valor'] += valor

        if linhas_validas < 2:
            self.add_error('rateio_payload', 'Informe no minimo 2 linhas de rateio validas.')

        rateio_linhas = list(rateio_por_categoria.values())

        if valor_total is not None and linhas_validas and soma_rateio != valor_total:
            self.add_error(
                'rateio_payload',
                'A soma das linhas de rateio precisa ser igual ao valor total do documento.',
            )

        cleaned_data['rateio_linhas'] = rateio_linhas
        cleaned_data['valor'] = valor_total or Decimal('0.00')
        cleaned_data['categoria'] = rateio_linhas[0]['categoria'] if rateio_linhas else None
        cleaned_data['grupo_rateio'] = self._rateio_group_token

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        transferencia = tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA
        lancamento_com_rateio = bool(cleaned_data.get('lancamento_com_rateio')) and not self.instance.pk

        if not cleaned_data.get('conta'):
            self.add_error('conta', 'Informe a conta de origem.')

        if transferencia:
            cleaned_data['pessoa'] = None
            cleaned_data['categoria'] = None
            cleaned_data['centro_custo'] = None
            if not cleaned_data.get('conta_destino'):
                self.add_error('conta_destino', 'Informe a conta de destino para a transferencia.')
        else:
            cleaned_data['conta_destino'] = None

        if tipo in {
            LancamentoFinanceiro.TipoLancamento.RECEITA,
            LancamentoFinanceiro.TipoLancamento.DESPESA,
        }:
            if not cleaned_data.get('pessoa'):
                self.add_error('pessoa', 'Informe o favorecido para receita e despesa.')
            if not cleaned_data.get('categoria') and not lancamento_com_rateio:
                self.add_error('categoria', 'Informe a categoria para receita e despesa.')
            elif cleaned_data.get('categoria') and not cleaned_data['categoria'].permite_vinculo_em_lancamento:
                self.add_error(
                    'categoria',
                    'Selecione uma subcategoria para receita e despesa. Categoria pai nao pode ser usada em lancamentos.',
                )
            elif cleaned_data.get('categoria') and cleaned_data['categoria'].tipo != tipo:
                self.add_error(
                    'categoria',
                    'Selecione uma subcategoria compativel com o tipo do lancamento.',
                )

        if lancamento_com_rateio:
            cleaned_data['salvar_como_regra_automatica'] = False
            self._validar_rateio(cleaned_data)
        else:
            if not cleaned_data.get('valor'):
                self.add_error('valor', 'Informe o valor do lancamento.')
            self._limpar_rateio(cleaned_data)

        cleaned_data['competencias_requeridas'] = self._lancamento_requer_competencias(
            cleaned_data,
            lancamento_com_rateio=lancamento_com_rateio,
        )
        if cleaned_data['competencias_requeridas']:
            self._validar_competencias(cleaned_data)
        else:
            cleaned_data['competencias_linhas'] = []
        if lancamento_com_rateio:
            self._validar_competencias_rateio(cleaned_data)
        else:
            cleaned_data['competencias_rateio_por_categoria'] = {}
        self.competencias_bloco_visivel = bool(
            self.competencias_linhas_iniciais or cleaned_data['competencias_requeridas']
        )
        self._atualizar_assistente_competencia(cleaned_data)
        return cleaned_data

    def _post_clean(self):
        super_form = super()
        if not bool(self.cleaned_data.get('lancamento_com_rateio')) or self.instance.pk:
            super_form._post_clean()
            return

        opts = self._meta
        self.instance = construct_instance(self, self.instance, opts.fields, opts.exclude)
        self.instance.com_rateio = True
        self.instance.grupo_rateio = self.cleaned_data.get('grupo_rateio', self._rateio_group_token)
        self.instance.categoria = self.cleaned_data.get('categoria')
        self.instance.valor = self.cleaned_data.get('valor') or Decimal('0.00')

        if self.errors:
            return

        exclude = self._get_validation_exclusions()

        try:
            self.instance.full_clean(exclude=exclude, validate_unique=False)
        except ValidationError as error:
            self._update_errors(error)

        try:
            self.validate_unique()
        except ValidationError as error:
            self._update_errors(error)

    class Meta:
        model = LancamentoFinanceiro
        fields = [
            'descricao',
            'tipo',
            'status',
            'valor',
            'data_competencia',
            'data_pagamento',
            'numero_documento',
            'pessoa',
            'categoria',
            'centro_custo',
            'conta',
            'conta_destino',
            'observacoes',
        ]
        widgets = {
            'descricao': forms.TextInput(
                attrs={
                    'autocomplete': 'off',
                    'autocorrect': 'off',
                    'autocapitalize': 'none',
                    'spellcheck': 'false',
                }
            ),
            'data_competencia': forms.DateInput(attrs={'type': 'date'}),
            'data_pagamento': forms.DateInput(attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 4}),
        }

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if not commit:
            return instance

        if self.cleaned_data.get('competencias_requeridas'):
            competencias_linhas = self.cleaned_data.get('competencias_linhas') or []
            instance.alocacoes_competencia.all().delete()
            for linha in competencias_linhas:
                AlocacaoCompetenciaFinanceira.objects.create(
                    lancamento=instance,
                    categoria=instance.categoria,
                    **linha,
                )
        else:
            instance.alocacoes_competencia.all().delete()

        return instance


class LancamentoFinanceiroGrupoRateioForm(forms.ModelForm):
    valor_total_documento = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        label='Valor total do documento',
        help_text='Usado para validar o fechamento do grupo de rateio nesta etapa.',
    )
    rateio_payload = forms.CharField(required=False, widget=forms.HiddenInput())
    competencias_rateio_payload = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, grupo_lancamentos=None, **kwargs):
        self.grupo_lancamentos = list(grupo_lancamentos or [])
        self.rateio_linhas_iniciais: list[dict[str, str]] = []
        self.competencias_rateio_iniciais: dict[str, list[dict[str, str]]] = {}
        self.assistente_competencia_rateio_grupos_iniciais: list[dict[str, object]] = []
        super().__init__(*args, **kwargs)
        for field_name in ('data_competencia', 'data_pagamento'):
            self.fields[field_name].widget.format = '%Y-%m-%d'
            if not self.is_bound:
                valor_inicial = getattr(self.instance, field_name, None)
                if valor_inicial:
                    self.initial[field_name] = valor_inicial.strftime('%Y-%m-%d')
        self.fields['tipo'].widget.attrs.update({'data-financeiro-tipo': 'true'})
        self.fields['conta_destino'].widget.attrs.update({'data-financeiro-conta-destino': 'true'})
        self.fields['pessoa'].required = False
        self.fields['pessoa'].label = 'Favorecido'
        self.fields['data_pagamento'].required = True
        self.fields['data_pagamento'].error_messages['required'] = 'Informe a data de pagamento.'
        self.fields['tipo'].choices = [choice for choice in self.fields['tipo'].choices if choice[0] != '']
        conta_extra_ids = {self.instance.conta_id, self.instance.conta_destino_id}
        for lancamento in self.grupo_lancamentos:
            conta_extra_ids.add(lancamento.conta_id)
            conta_extra_ids.add(lancamento.conta_destino_id)
        self.fields['conta'].queryset = contas_lancamento_queryset(*conta_extra_ids)
        self.fields['conta_destino'].queryset = contas_lancamento_queryset(*conta_extra_ids)
        autocomplete_urls = {
            'pessoa': reverse_lazy('financeiro:autocomplete-pessoa'),
            'centro_custo': reverse_lazy('financeiro:autocomplete-centro-custo'),
            'conta': reverse_lazy('financeiro:autocomplete-conta'),
            'conta_destino': reverse_lazy('financeiro:autocomplete-conta'),
        }
        for field_name, url in autocomplete_urls.items():
            self.fields[field_name].widget.attrs.update(
                {
                    'data-financeiro-autocomplete': 'true',
                    'data-autocomplete-url': str(url),
                }
            )
        if self.is_bound:
            self.rateio_linhas_iniciais = self._parse_rateio_payload(self.data.get('rateio_payload', ''))
            self.competencias_rateio_iniciais = _parse_competencias_rateio_payload(
                self.data.get('competencias_rateio_payload', '')
            )
        else:
            self.rateio_linhas_iniciais = [
                {
                    'id': str(lancamento.pk),
                    'categoria': str(lancamento.categoria_id or ''),
                    'valor': str(lancamento.valor or ''),
                }
                for lancamento in self.grupo_lancamentos
            ]
            competencias_por_categoria: dict[str, list[dict[str, str]]] = {}
            for lancamento in self.grupo_lancamentos:
                if not lancamento.usa_controle_competencia():
                    continue
                categoria_key = str(lancamento.categoria_id)
                competencias_por_categoria.setdefault(categoria_key, [])
                for alocacao in lancamento.alocacoes_competencia.order_by(
                    'ano_competencia',
                    'mes_competencia',
                    'pk',
                ):
                    competencias_por_categoria[categoria_key].append(
                        {
                            'mes': str(alocacao.mes_competencia),
                            'ano': str(alocacao.ano_competencia),
                            'valor': f'{alocacao.valor_alocado:.2f}',
                        }
                    )
            self.competencias_rateio_iniciais = competencias_por_categoria
            self.fields['valor_total_documento'].initial = sum(
                (lancamento.valor for lancamento in self.grupo_lancamentos),
                Decimal('0.00'),
            )
        self.competencias_rateio_bloco_visivel = bool(self.competencias_rateio_iniciais)
        self.assistente_competencia_registro_lookup = _montar_lookup_competencias_registradas(
            excluir_lancamento_ids={lancamento.pk for lancamento in self.grupo_lancamentos if lancamento.pk}
        )
        self._atualizar_assistente_competencia_rateio()

    def _resolver_data_referencia_assistente(self) -> date:
        if self.is_bound:
            data_referencia_raw = (
                self.data.get(self.add_prefix('data_competencia'))
                or self.data.get(self.add_prefix('data_pagamento'))
                or ''
            ).strip()
            if data_referencia_raw:
                try:
                    return date.fromisoformat(data_referencia_raw)
                except ValueError:
                    pass

        data_referencia = (
            getattr(self.instance, 'data_competencia', None)
            or getattr(self.instance, 'data_pagamento', None)
        )
        if hasattr(data_referencia, 'date'):
            data_referencia = data_referencia.date()
        if isinstance(data_referencia, date):
            return data_referencia
        return timezone.localdate()

    def _resolver_pessoa_atual(self) -> PessoaFinanceira | None:
        if self.is_bound:
            pessoa_id = (self.data.get(self.add_prefix('pessoa')) or '').strip()
            if pessoa_id.isdigit():
                return PessoaFinanceira.objects.filter(pk=int(pessoa_id)).first()
            return None
        pessoa = getattr(self.instance, 'pessoa', None)
        if isinstance(pessoa, PessoaFinanceira) or pessoa is None:
            return pessoa
        if str(pessoa).isdigit():
            return PessoaFinanceira.objects.filter(pk=int(pessoa)).first()
        return None

    def _resolver_rateio_linhas_atuais(
        self,
        *,
        cleaned_data: dict | None = None,
    ) -> list[dict[str, object]]:
        tipo = cleaned_data.get('tipo') if cleaned_data else self._get_tipo_atual()
        pessoa = cleaned_data.get('pessoa') if cleaned_data else self._resolver_pessoa_atual()
        if cleaned_data is not None and cleaned_data.get('rateio_linhas'):
            return _linhas_rateio_controladas(
                tipo=tipo,
                pessoa=pessoa,
                rateio_linhas=cleaned_data.get('rateio_linhas'),
            )

        categorias_disponiveis = {
            str(categoria.pk): categoria for categoria in categorias_vinculaveis_queryset(tipo)
        }
        consolidadas: dict[str, dict[str, object]] = {}
        for linha in self.rateio_linhas_iniciais:
            categoria_id = str(linha.get('categoria', '') or '').strip()
            valor_raw = str(linha.get('valor', '') or '').strip()
            categoria = categorias_disponiveis.get(categoria_id)
            if categoria is None:
                continue
            try:
                valor = Decimal(valor_raw)
            except (InvalidOperation, TypeError):
                continue
            if valor <= Decimal('0.00'):
                continue
            grupo = consolidadas.setdefault(
                categoria_id,
                {'categoria': categoria, 'valor': Decimal('0.00')},
            )
            grupo['valor'] += valor
        return _linhas_rateio_controladas(
            tipo=tipo,
            pessoa=pessoa,
            rateio_linhas=list(consolidadas.values()),
        )

    def _get_tipo_atual(self) -> str:
        if self.is_bound:
            return (self.data.get(self.add_prefix('tipo')) or '').strip()
        return (
            self.initial.get('tipo')
            or self.instance.tipo
            or LancamentoFinanceiro.TipoLancamento.RECEITA
        )

    def _atualizar_assistente_competencia_rateio(self, cleaned_data: dict | None = None) -> None:
        grupos_iniciais: list[dict[str, object]] = []
        pessoa = cleaned_data.get('pessoa') if cleaned_data else self._resolver_pessoa_atual()
        for linha in self._resolver_rateio_linhas_atuais(cleaned_data=cleaned_data):
            categoria = linha['categoria']
            grupos_iniciais.append(
                {
                    'categoria_id': str(categoria.pk),
                    'categoria_label': str(categoria),
                    'valor_controlado_texto': _formatar_decimal_brl(linha['valor']),
                    'meses': _montar_assistente_meses(
                        referencia=self._resolver_data_referencia_assistente(),
                        pessoa_id=getattr(pessoa, 'pk', None),
                        categoria_id=categoria.pk,
                        linhas_atuais=self.competencias_rateio_iniciais.get(str(categoria.pk), []),
                        registro_lookup=self.assistente_competencia_registro_lookup,
                    ),
                }
            )
        self.assistente_competencia_rateio_grupos_iniciais = grupos_iniciais
        self.competencias_rateio_bloco_visivel = bool(
            self.competencias_rateio_iniciais or self.assistente_competencia_rateio_grupos_iniciais
        )

    def _parse_rateio_payload(self, payload: str) -> list[dict[str, str]]:
        if not payload:
            return []
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return []
        if not isinstance(data, list):
            return []

        linhas: list[dict[str, str]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            linhas.append(
                {
                    'id': str(item.get('id', '') or '').strip(),
                    'categoria': str(item.get('categoria', '') or '').strip(),
                    'valor': str(item.get('valor', '') or '').strip(),
                }
            )
        return linhas

    def _validar_competencias_linhas_rateio(
        self,
        linhas_brutas: list[dict[str, str]],
        *,
        categoria: CategoriaFinanceira,
    ) -> tuple[list[dict[str, object]], Decimal, bool]:
        if not linhas_brutas:
            self.add_error(
                'competencias_rateio_payload',
                f'Informe ao menos uma competencia atendida para a subcategoria "{categoria}".',
            )
            return [], Decimal('0.00'), True

        linhas_validas: list[dict[str, object]] = []
        soma_competencias = Decimal('0.00')
        competencias_vistas: set[tuple[int, int]] = set()
        houve_erro_linha = False
        for indice, linha in enumerate(linhas_brutas, start=1):
            mes_raw = linha.get('mes', '')
            ano_raw = linha.get('ano', '')
            valor_raw = linha.get('valor', '')
            if not mes_raw and not ano_raw and not valor_raw:
                continue

            try:
                mes = int(mes_raw)
            except (TypeError, ValueError):
                self.add_error('competencias_rateio_payload', f'{categoria}: Linha {indice}: informe um mes valido.')
                houve_erro_linha = True
                continue

            try:
                ano = int(ano_raw)
            except (TypeError, ValueError):
                self.add_error('competencias_rateio_payload', f'{categoria}: Linha {indice}: informe um ano valido.')
                houve_erro_linha = True
                continue

            try:
                valor = Decimal(valor_raw)
            except (InvalidOperation, TypeError):
                self.add_error('competencias_rateio_payload', f'{categoria}: Linha {indice}: informe um valor valido.')
                houve_erro_linha = True
                continue

            if mes < 1 or mes > 12:
                self.add_error(
                    'competencias_rateio_payload',
                    f'{categoria}: Linha {indice}: o mes precisa ficar entre 1 e 12.',
                )
                houve_erro_linha = True
                continue

            if ano < 1900 or ano > 9999:
                self.add_error('competencias_rateio_payload', f'{categoria}: Linha {indice}: informe um ano valido.')
                houve_erro_linha = True
                continue

            if valor <= Decimal('0.00'):
                self.add_error('competencias_rateio_payload', f'{categoria}: Linha {indice}: o valor precisa ser positivo.')
                houve_erro_linha = True
                continue

            competencia_key = (ano, mes)
            if competencia_key in competencias_vistas:
                self.add_error(
                    'competencias_rateio_payload',
                    f'{categoria}: Ja existe uma competencia informada para este mes/ano. Agrupe o valor em uma unica linha.',
                )
                houve_erro_linha = True
                continue

            competencias_vistas.add(competencia_key)
            linhas_validas.append(
                {
                    'mes_competencia': mes,
                    'ano_competencia': ano,
                    'valor_alocado': valor,
                }
            )
            soma_competencias += valor

        if not linhas_validas:
            self.add_error(
                'competencias_rateio_payload',
                f'Informe ao menos uma competencia atendida para a subcategoria "{categoria}".',
            )
            return [], Decimal('0.00'), True
        return linhas_validas, soma_competencias, houve_erro_linha

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        valor_total = cleaned_data.get('valor_total_documento')
        linhas_existentes_por_id = {
            str(lancamento.pk): lancamento for lancamento in self.grupo_lancamentos
        }

        if not cleaned_data.get('conta'):
            self.add_error('conta', 'Informe a conta de origem.')

        if tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
            self.add_error('tipo', 'Transferencia nao pode usar rateio nesta primeira versao.')

        if tipo in {
            LancamentoFinanceiro.TipoLancamento.RECEITA,
            LancamentoFinanceiro.TipoLancamento.DESPESA,
        } and not cleaned_data.get('pessoa'):
            self.add_error('pessoa', 'Informe o favorecido para receita e despesa.')

        if valor_total is None:
            self.add_error('valor_total_documento', 'Informe o valor total do documento para validar o rateio.')

        linhas_brutas = self._parse_rateio_payload(cleaned_data.get('rateio_payload', ''))
        self.rateio_linhas_iniciais = linhas_brutas or self.rateio_linhas_iniciais or [
            {'id': '', 'categoria': '', 'valor': ''},
            {'id': '', 'categoria': '', 'valor': ''},
        ]
        if not linhas_brutas:
            self.add_error('rateio_payload', 'Informe ao menos 2 linhas de rateio validas.')
            cleaned_data['rateio_linhas'] = []
            return cleaned_data

        categorias_disponiveis = {
            str(categoria.pk): categoria for categoria in categorias_vinculaveis_queryset(tipo)
        }
        linhas_validas = 0
        soma_rateio = Decimal('0.00')
        rateio_por_categoria: dict[int, dict[str, object]] = {}

        for indice, linha in enumerate(linhas_brutas, start=1):
            linha_id = linha.get('id', '')
            categoria_id = linha.get('categoria', '')
            valor_raw = linha.get('valor', '')
            if not linha_id and not categoria_id and not valor_raw:
                continue

            if linha_id:
                try:
                    linha_id = str(int(linha_id))
                except (TypeError, ValueError):
                    self.add_error('rateio_payload', f'Linha {indice}: identificador de linha invalido para este grupo de rateio.')
                    continue
                if linha_id not in linhas_existentes_por_id:
                    self.add_error('rateio_payload', f'Linha {indice}: a linha informada nao pertence a este grupo de rateio.')
                    continue

            linhas_validas += 1
            categoria = categorias_disponiveis.get(categoria_id)
            if categoria is None:
                self.add_error('rateio_payload', f'Linha {indice}: informe uma categoria valida.')
                continue

            if not categoria.permite_vinculo_em_lancamento:
                self.add_error(
                    'rateio_payload',
                    f'Linha {indice}: selecione uma subcategoria valida. Categoria pai nao pode ser usada no rateio.',
                )
                continue

            try:
                valor = Decimal(valor_raw)
            except (InvalidOperation, TypeError):
                self.add_error('rateio_payload', f'Linha {indice}: informe um valor valido.')
                continue

            if valor <= Decimal('0.00'):
                self.add_error('rateio_payload', f'Linha {indice}: o valor precisa ser positivo.')
                continue

            soma_rateio += valor
            if categoria.pk not in rateio_por_categoria:
                rateio_por_categoria[categoria.pk] = {
                    'id': linha_id,
                    'categoria': categoria,
                    'valor': Decimal('0.00'),
                }
            elif linha_id and not rateio_por_categoria[categoria.pk].get('id'):
                rateio_por_categoria[categoria.pk]['id'] = linha_id
            rateio_por_categoria[categoria.pk]['valor'] += valor

        if linhas_validas < 2:
            self.add_error('rateio_payload', 'Informe no minimo 2 linhas de rateio validas.')

        rateio_linhas = list(rateio_por_categoria.values())
        if valor_total is not None and linhas_validas and soma_rateio != valor_total:
            self.add_error(
                'rateio_payload',
                'A soma das linhas de rateio precisa ser igual ao valor total do documento.',
            )

        cleaned_data['rateio_linhas'] = rateio_linhas
        linhas_controladas = _linhas_rateio_controladas(
            tipo=cleaned_data.get('tipo'),
            pessoa=cleaned_data.get('pessoa'),
            rateio_linhas=rateio_linhas,
        )
        competencias_brutas = _parse_competencias_rateio_payload(
            cleaned_data.get('competencias_rateio_payload', '')
        )
        self.competencias_rateio_iniciais = competencias_brutas
        self.competencias_rateio_bloco_visivel = bool(
            linhas_controladas or self.competencias_rateio_iniciais
        )
        competencias_rateio_por_categoria: dict[int, list[dict[str, object]]] = {}
        for linha in linhas_controladas:
            categoria = linha['categoria']
            linhas_competencia, soma_competencias, houve_erro_linha = self._validar_competencias_linhas_rateio(
                competencias_brutas.get(str(categoria.pk), []),
                categoria=categoria,
            )
            if not linhas_competencia:
                continue
            if not houve_erro_linha and soma_competencias != linha['valor']:
                self.add_error(
                    'competencias_rateio_payload',
                    f'A soma das competencias deve ser igual ao valor controlado da subcategoria no rateio: {categoria}.',
                )
                continue
            competencias_rateio_por_categoria[categoria.pk] = linhas_competencia
        cleaned_data['competencias_rateio_por_categoria'] = competencias_rateio_por_categoria
        self._atualizar_assistente_competencia_rateio(cleaned_data)
        return cleaned_data

    def _post_clean(self):
        super()._post_clean()
        if self.errors:
            return

        rateio_linhas = self.cleaned_data.get('rateio_linhas') or []
        primeira_linha = rateio_linhas[0] if rateio_linhas else None
        if not primeira_linha:
            return

        opts = self._meta
        self.instance = construct_instance(self, self.instance, opts.fields, opts.exclude)
        self.instance.com_rateio = True
        self.instance.grupo_rateio = self.instance.grupo_rateio or (
            self.grupo_lancamentos[0].grupo_rateio if self.grupo_lancamentos else ''
        )
        self.instance.categoria = primeira_linha['categoria']
        self.instance.valor = primeira_linha['valor']

        exclude = self._get_validation_exclusions()
        try:
            self.instance.full_clean(exclude=exclude, validate_unique=False)
        except ValidationError as error:
            self._update_errors(error)

        try:
            self.validate_unique()
        except ValidationError as error:
            self._update_errors(error)

    class Meta:
        model = LancamentoFinanceiro
        fields = [
            'descricao',
            'tipo',
            'status',
            'data_competencia',
            'data_pagamento',
            'numero_documento',
            'pessoa',
            'centro_custo',
            'conta',
            'conta_destino',
            'observacoes',
        ]
        widgets = {
            'data_competencia': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'data_pagamento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 4}),
        }
