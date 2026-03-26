from __future__ import annotations

from django import forms
from django.urls import reverse_lazy

from .models import (
    CategoriaFinanceira,
    CentroCusto,
    ContaFinanceira,
    LancamentoFinanceiro,
    PessoaFinanceira,
)


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


class LancamentoFinanceiroForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].widget.attrs.update({'data-financeiro-tipo': 'true'})
        self.fields['conta_destino'].widget.attrs.update({'data-financeiro-conta-destino': 'true'})
        self.fields['conta'].error_messages['required'] = 'Informe a conta de origem.'
        self.fields['pessoa'].required = False
        self.fields['categoria'].required = False
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

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        transferencia = tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA

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
                self.add_error('pessoa', 'Informe a pessoa para receita e despesa.')
            if not cleaned_data.get('categoria'):
                self.add_error('categoria', 'Informe a categoria para receita e despesa.')
        return cleaned_data

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
            'data_competencia': forms.DateInput(attrs={'type': 'date'}),
            'data_pagamento': forms.DateInput(attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 4}),
        }
