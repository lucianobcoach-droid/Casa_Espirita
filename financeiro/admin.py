from __future__ import annotations

from django.contrib import admin

from .models import (
    CategoriaFinanceira,
    CentroCusto,
    ContaFinanceira,
    LancamentoFinanceiro,
    PessoaFinanceira,
)


@admin.register(ContaFinanceira)
class ContaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativa', 'criado_em', 'atualizado_em')
    list_filter = ('ativa',)
    search_fields = ('nome', 'descricao')


@admin.register(CentroCusto)
class CentroCustoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'ativo', 'criado_em', 'atualizado_em')
    list_filter = ('ativo',)
    search_fields = ('codigo', 'nome')


@admin.register(PessoaFinanceira)
class PessoaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'tipo_pessoa', 'documento', 'ativo')
    list_filter = ('tipo_pessoa', 'ativo')
    search_fields = ('codigo', 'nome', 'documento', 'telefone', 'email')


@admin.register(CategoriaFinanceira)
class CategoriaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'categoria_pai', 'ativo')
    list_filter = ('tipo', 'ativo')
    search_fields = ('nome',)


@admin.register(LancamentoFinanceiro)
class LancamentoFinanceiroAdmin(admin.ModelAdmin):
    list_display = (
        'descricao',
        'tipo',
        'status',
        'valor',
        'data_competencia',
        'data_pagamento',
        'conta',
        'conta_destino',
    )
    list_filter = ('tipo', 'status', 'data_competencia', 'data_pagamento', 'conta')
    search_fields = ('descricao', 'numero_documento', 'observacoes')
    autocomplete_fields = ('pessoa', 'categoria', 'centro_custo', 'conta', 'conta_destino')
