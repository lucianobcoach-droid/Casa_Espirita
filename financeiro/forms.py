from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import construct_instance
from django.urls import reverse_lazy

from .models import (
    AssinaturaInstitucional,
    CategoriaFinanceira,
    ConfiguracaoInstitucional,
    CentroCusto,
    ContaFinanceira,
    LancamentoFinanceiro,
    PessoaFinanceira,
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


class ContaFinanceiraForm(forms.ModelForm):
    class Meta:
        model = ContaFinanceira
        fields = [
            'nome',
            'descricao',
            'saldo_inicial',
            'data_saldo_inicial',
            'ativa',
        ]
        widgets = {
            'data_saldo_inicial': forms.DateInput(attrs={'type': 'date'}),
        }


class CentroCustoForm(forms.ModelForm):
    class Meta:
        model = CentroCusto
        fields = [
            'codigo',
            'nome',
            'ativo',
        ]


class PessoaFinanceiraForm(forms.ModelForm):
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
            'ativo',
        ]
        labels = {
            'tipo_pessoa': 'Tipo favorecido',
        }


class CategoriaFinanceiraForm(forms.ModelForm):
    class Meta:
        model = CategoriaFinanceira
        fields = [
            'nome',
            'tipo',
            'categoria_pai',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rateio_group_token = self.instance.grupo_rateio or uuid4().hex
        self.rateio_linhas_iniciais = []
        tipo_atual = self._get_tipo_atual()
        categoria_inicial = self.initial.get('categoria') or self.instance.categoria
        categoria_inicial_id = getattr(categoria_inicial, 'pk', categoria_inicial)
        self.fields['categoria'].queryset = categorias_vinculaveis_queryset(
            tipo=tipo_atual,
            categoria_extra_id=categoria_inicial_id,
        )
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
        elif self.is_bound:
            self.rateio_linhas_iniciais = self._parse_rateio_payload(self.data.get('rateio_payload', ''))
        else:
            self.rateio_linhas_iniciais = [
                {'categoria': '', 'valor': ''},
                {'categoria': '', 'valor': ''},
            ]
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

    def _get_tipo_atual(self) -> str:
        if self.is_bound:
            return (self.data.get(self.add_prefix('tipo')) or '').strip()
        return (
            self.initial.get('tipo')
            or self.instance.tipo
            or LancamentoFinanceiro.TipoLancamento.RECEITA
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

    def __init__(self, *args, grupo_lancamentos=None, **kwargs):
        self.grupo_lancamentos = list(grupo_lancamentos or [])
        self.rateio_linhas_iniciais: list[dict[str, str]] = []
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
        else:
            self.rateio_linhas_iniciais = [
                {
                    'id': str(lancamento.pk),
                    'categoria': str(lancamento.categoria_id or ''),
                    'valor': str(lancamento.valor or ''),
                }
                for lancamento in self.grupo_lancamentos
            ]
            self.fields['valor_total_documento'].initial = sum(
                (lancamento.valor for lancamento in self.grupo_lancamentos),
                Decimal('0.00'),
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
