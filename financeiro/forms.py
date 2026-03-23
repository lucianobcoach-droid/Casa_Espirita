from __future__ import annotations

from django import forms

from .models import CategoriaFinanceira, LancamentoFinanceiro, PessoaFinanceira


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
