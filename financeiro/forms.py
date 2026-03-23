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
            'ativo',
        ]


class LancamentoFinanceiroForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].widget.attrs.update({'data-financeiro-tipo': 'true'})
        self.fields['conta_destino'].widget.attrs.update({'data-financeiro-conta-destino': 'true'})
        self.fields['categoria'].required = True
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
        self.fields['categoria'].widget.attrs.update({'required': 'required'})

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('tipo') != LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
            cleaned_data['conta_destino'] = None
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
