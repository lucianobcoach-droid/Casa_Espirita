from __future__ import annotations

from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView

from .forms import CategoriaFinanceiraForm, LancamentoFinanceiroForm, PessoaFinanceiraForm
from .models import CategoriaFinanceira, LancamentoFinanceiro, PessoaFinanceira


class FinanceiroHomeView(TemplateView):
    template_name = 'financeiro/home.html'


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
