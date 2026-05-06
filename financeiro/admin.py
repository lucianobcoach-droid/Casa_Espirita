from __future__ import annotations

from django.contrib import admin

from .models import (
    AlocacaoCompetenciaFinanceira,
    CategoriaFinanceira,
    CentroCusto,
    ContaFinanceira,
    LancamentoFinanceiro,
    PessoaFinanceira,
    TipoContaFinanceira,
)


@admin.register(TipoContaFinanceira)
class TipoContaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'ativo', 'ordem')
    list_filter = ('ativo',)
    search_fields = ('codigo', 'nome', 'descricao')
    ordering = ('ordem', 'nome')


@admin.register(ContaFinanceira)
class ContaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_conta', 'disponibilidade', 'ativa', 'criado_em', 'atualizado_em')
    list_filter = ('tipo_conta', 'disponibilidade', 'ativa')
    search_fields = ('nome', 'descricao')


@admin.register(CentroCusto)
class CentroCustoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'ativo', 'criado_em', 'atualizado_em')
    list_filter = ('ativo',)
    search_fields = ('codigo', 'nome')


@admin.register(PessoaFinanceira)
class PessoaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'tipo_pessoa', 'contribuinte_recorrente', 'documento', 'ativo')
    list_filter = ('tipo_pessoa', 'contribuinte_recorrente', 'ativo')
    search_fields = ('codigo', 'nome', 'documento', 'telefone', 'email')


@admin.register(CategoriaFinanceira)
class CategoriaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'categoria_pai', 'controla_recorrencia_competencia', 'ativo')
    list_filter = ('tipo', 'controla_recorrencia_competencia', 'ativo')
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


@admin.register(AlocacaoCompetenciaFinanceira)
class AlocacaoCompetenciaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('lancamento', 'categoria', 'mes_competencia', 'ano_competencia', 'valor_alocado')
    list_filter = ('categoria', 'ano_competencia', 'mes_competencia')
    search_fields = ('lancamento__descricao', 'categoria__nome', 'lancamento__numero_documento')
    autocomplete_fields = ('lancamento', 'categoria')
