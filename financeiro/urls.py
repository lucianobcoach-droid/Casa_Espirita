from __future__ import annotations

from django.urls import path

from .views import (
    CategoriaFinanceiraCreateView,
    CategoriaFinanceiraListView,
    FinanceiroHomeView,
    LancamentoFinanceiroCreateView,
    LancamentoFinanceiroListView,
    PessoaFinanceiraCreateView,
    PessoaFinanceiraListView,
)

app_name = 'financeiro'

urlpatterns = [
    path('', FinanceiroHomeView.as_view(), name='home'),
    path('pessoas/', PessoaFinanceiraListView.as_view(), name='pessoa-list'),
    path('pessoas/nova/', PessoaFinanceiraCreateView.as_view(), name='pessoa-create'),
    path('categorias/', CategoriaFinanceiraListView.as_view(), name='categoria-list'),
    path('categorias/nova/', CategoriaFinanceiraCreateView.as_view(), name='categoria-create'),
    path('lancamentos/', LancamentoFinanceiroListView.as_view(), name='lancamento-list'),
    path('lancamentos/novo/', LancamentoFinanceiroCreateView.as_view(), name='lancamento-create'),
]
