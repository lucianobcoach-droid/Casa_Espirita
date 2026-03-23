from __future__ import annotations

from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView

from .forms import (
    CategoriaFinanceiraForm,
    CentroCustoForm,
    ContaFinanceiraForm,
    LancamentoFinanceiroForm,
    PessoaFinanceiraForm,
)
from .models import (
    CategoriaFinanceira,
    CentroCusto,
    ContaFinanceira,
    LancamentoFinanceiro,
    PessoaFinanceira,
)


class FinanceiroHomeView(TemplateView):
    template_name = 'financeiro/home.html'


class ContaFinanceiraListView(ListView):
    model = ContaFinanceira
    template_name = 'financeiro/conta_list.html'
    context_object_name = 'contas'


class ContaFinanceiraCreateView(CreateView):
    model = ContaFinanceira
    form_class = ContaFinanceiraForm
    template_name = 'financeiro/conta_form.html'
    success_url = reverse_lazy('financeiro:conta-list')


class CentroCustoListView(ListView):
    model = CentroCusto
    template_name = 'financeiro/centro_custo_list.html'
    context_object_name = 'centros_custo'


class CentroCustoCreateView(CreateView):
    model = CentroCusto
    form_class = CentroCustoForm
    template_name = 'financeiro/centro_custo_form.html'
    success_url = reverse_lazy('financeiro:centro-custo-list')


class PessoaFinanceiraListView(ListView):
    model = PessoaFinanceira
    template_name = 'financeiro/pessoa_list.html'
    context_object_name = 'pessoas'


class PessoaFinanceiraCreateView(CreateView):
    model = PessoaFinanceira
    form_class = PessoaFinanceiraForm
    template_name = 'financeiro/pessoa_form.html'
    success_url = reverse_lazy('financeiro:pessoa-list')


class CategoriaFinanceiraListView(ListView):
    model = CategoriaFinanceira
    template_name = 'financeiro/categoria_list.html'
    context_object_name = 'categorias'


class CategoriaFinanceiraCreateView(CreateView):
    model = CategoriaFinanceira
    form_class = CategoriaFinanceiraForm
    template_name = 'financeiro/categoria_form.html'
    success_url = reverse_lazy('financeiro:categoria-list')


class LancamentoFinanceiroListView(ListView):
    model = LancamentoFinanceiro
    template_name = 'financeiro/lancamento_list.html'
    context_object_name = 'lancamentos'


class LancamentoFinanceiroCreateView(CreateView):
    model = LancamentoFinanceiro
    form_class = LancamentoFinanceiroForm
    template_name = 'financeiro/lancamento_form.html'
    success_url = reverse_lazy('financeiro:lancamento-list')
