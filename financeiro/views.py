from __future__ import annotations

from decimal import Decimal

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

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


class FinanceiroFormMixin:
    page_title = ''
    submit_label = 'Salvar'
    success_message = 'Registro salvo com sucesso.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['submit_label'] = self.submit_label
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class FinanceiroDeleteMixin(DeleteView):
    template_name = 'financeiro/confirm_delete.html'
    success_message = 'Registro excluido com sucesso.'
    page_title = 'Confirmar exclusao'
    cancel_url = reverse_lazy('financeiro:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['cancel_url'] = self.cancel_url
        context['object_label'] = str(self.object)
        return context

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class FinanceiroHomeView(TemplateView):
    template_name = 'financeiro/home.html'


class FinanceiroAutocompleteView(View):
    model = None
    search_fields: tuple[str, ...] = ()
    limit = 10

    def get_queryset(self):
        if self.model is None:
            raise ValueError('model precisa ser definida')
        queryset = self.model.objects.all()
        query = self.request.GET.get('q', '').strip()
        if query:
            filters = Q()
            for field in self.search_fields:
                filters |= Q(**{f'{field}__icontains': query})
            queryset = queryset.filter(filters)
        return queryset[: self.limit]

    def get(self, request, *args, **kwargs):
        results = [{'id': obj.pk, 'label': str(obj)} for obj in self.get_queryset()]
        return JsonResponse({'results': results})


class PessoaFinanceiraAutocompleteView(FinanceiroAutocompleteView):
    model = PessoaFinanceira
    search_fields = ('codigo', 'nome', 'documento', 'email')


class CategoriaFinanceiraAutocompleteView(FinanceiroAutocompleteView):
    model = CategoriaFinanceira
    search_fields = ('nome',)


class ContaFinanceiraAutocompleteView(FinanceiroAutocompleteView):
    model = ContaFinanceira
    search_fields = ('nome', 'descricao')


class CentroCustoAutocompleteView(FinanceiroAutocompleteView):
    model = CentroCusto
    search_fields = ('codigo', 'nome')


class ContaFinanceiraListView(ListView):
    model = ContaFinanceira
    template_name = 'financeiro/conta_list.html'
    context_object_name = 'contas'

    def get_queryset(self):
        queryset = super().get_queryset()
        nome = self.request.GET.get('nome', '').strip()
        ativa = self.request.GET.get('ativa', '').strip()
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if ativa == 'ativas':
            queryset = queryset.filter(ativa=True)
        elif ativa == 'inativas':
            queryset = queryset.filter(ativa=False)
        return queryset


class ContaFinanceiraCreateView(FinanceiroFormMixin, CreateView):
    model = ContaFinanceira
    form_class = ContaFinanceiraForm
    template_name = 'financeiro/conta_form.html'
    success_url = reverse_lazy('financeiro:conta-list')
    page_title = 'Nova Conta Financeira'
    success_message = 'Conta financeira cadastrada com sucesso.'


class ContaFinanceiraUpdateView(FinanceiroFormMixin, UpdateView):
    model = ContaFinanceira
    form_class = ContaFinanceiraForm
    template_name = 'financeiro/conta_form.html'
    success_url = reverse_lazy('financeiro:conta-list')
    page_title = 'Editar Conta Financeira'
    submit_label = 'Atualizar'
    success_message = 'Conta financeira atualizada com sucesso.'


class ContaFinanceiraDeleteView(FinanceiroDeleteMixin):
    model = ContaFinanceira
    success_url = reverse_lazy('financeiro:conta-list')
    page_title = 'Excluir Conta Financeira'
    cancel_url = reverse_lazy('financeiro:conta-list')
    success_message = 'Conta financeira excluida com sucesso.'


class ContaFinanceiraExtratoView(DetailView):
    model = ContaFinanceira
    template_name = 'financeiro/conta_extrato.html'
    context_object_name = 'conta'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conta = self.object
        saldo_acumulado = conta.saldo_inicial or Decimal('0.00')
        lancamentos = (
            LancamentoFinanceiro.objects.filter(Q(conta=conta) | Q(conta_destino=conta))
            .select_related('conta', 'conta_destino', 'pessoa', 'categoria')
            .order_by('data_competencia', 'criado_em', 'pk')
        )

        itens_extrato = []
        for lancamento in lancamentos:
            entrada = Decimal('0.00')
            saida = Decimal('0.00')

            if lancamento.tipo == LancamentoFinanceiro.TipoLancamento.RECEITA and lancamento.conta_id == conta.id:
                entrada = lancamento.valor
            elif lancamento.tipo == LancamentoFinanceiro.TipoLancamento.DESPESA and lancamento.conta_id == conta.id:
                saida = lancamento.valor
            elif lancamento.tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
                if lancamento.conta_id == conta.id:
                    saida = lancamento.valor
                elif lancamento.conta_destino_id == conta.id:
                    entrada = lancamento.valor

            saldo_acumulado += entrada - saida
            itens_extrato.append(
                {
                    'lancamento': lancamento,
                    'entrada': entrada,
                    'saida': saida,
                    'saldo_acumulado': saldo_acumulado,
                }
            )

        context['page_title'] = f'Extrato da Conta: {conta.nome}'
        context['saldo_inicial'] = conta.saldo_inicial or Decimal('0.00')
        context['data_saldo_inicial'] = conta.data_saldo_inicial
        context['itens_extrato'] = itens_extrato
        context['saldo_final'] = saldo_acumulado
        return context


class CentroCustoListView(ListView):
    model = CentroCusto
    template_name = 'financeiro/centro_custo_list.html'
    context_object_name = 'centros_custo'

    def get_queryset(self):
        queryset = super().get_queryset()
        codigo = self.request.GET.get('codigo', '').strip()
        nome = self.request.GET.get('nome', '').strip()
        if codigo:
            queryset = queryset.filter(codigo__icontains=codigo)
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        return queryset


class CentroCustoCreateView(FinanceiroFormMixin, CreateView):
    model = CentroCusto
    form_class = CentroCustoForm
    template_name = 'financeiro/centro_custo_form.html'
    success_url = reverse_lazy('financeiro:centro-custo-list')
    page_title = 'Novo Centro de Custo'
    success_message = 'Centro de custo cadastrado com sucesso.'


class CentroCustoUpdateView(FinanceiroFormMixin, UpdateView):
    model = CentroCusto
    form_class = CentroCustoForm
    template_name = 'financeiro/centro_custo_form.html'
    success_url = reverse_lazy('financeiro:centro-custo-list')
    page_title = 'Editar Centro de Custo'
    submit_label = 'Atualizar'
    success_message = 'Centro de custo atualizado com sucesso.'


class CentroCustoDeleteView(FinanceiroDeleteMixin):
    model = CentroCusto
    success_url = reverse_lazy('financeiro:centro-custo-list')
    page_title = 'Excluir Centro de Custo'
    cancel_url = reverse_lazy('financeiro:centro-custo-list')
    success_message = 'Centro de custo excluido com sucesso.'


class PessoaFinanceiraListView(ListView):
    model = PessoaFinanceira
    template_name = 'financeiro/pessoa_list.html'
    context_object_name = 'pessoas'

    def get_queryset(self):
        queryset = super().get_queryset()
        nome = self.request.GET.get('nome', '').strip()
        codigo = self.request.GET.get('codigo', '').strip()
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if codigo:
            queryset = queryset.filter(codigo__icontains=codigo)
        return queryset


class PessoaFinanceiraCreateView(FinanceiroFormMixin, CreateView):
    model = PessoaFinanceira
    form_class = PessoaFinanceiraForm
    template_name = 'financeiro/pessoa_form.html'
    success_url = reverse_lazy('financeiro:pessoa-list')
    page_title = 'Nova Pessoa Financeira'
    success_message = 'Pessoa financeira cadastrada com sucesso.'


class PessoaFinanceiraUpdateView(FinanceiroFormMixin, UpdateView):
    model = PessoaFinanceira
    form_class = PessoaFinanceiraForm
    template_name = 'financeiro/pessoa_form.html'
    success_url = reverse_lazy('financeiro:pessoa-list')
    page_title = 'Editar Pessoa Financeira'
    submit_label = 'Atualizar'
    success_message = 'Pessoa financeira atualizada com sucesso.'


class PessoaFinanceiraDeleteView(FinanceiroDeleteMixin):
    model = PessoaFinanceira
    success_url = reverse_lazy('financeiro:pessoa-list')
    page_title = 'Excluir Pessoa Financeira'
    cancel_url = reverse_lazy('financeiro:pessoa-list')
    success_message = 'Pessoa financeira excluida com sucesso.'


class CategoriaFinanceiraListView(ListView):
    model = CategoriaFinanceira
    template_name = 'financeiro/categoria_list.html'
    context_object_name = 'categorias'

    def get_queryset(self):
        queryset = super().get_queryset()
        nome = self.request.GET.get('nome', '').strip()
        tipo = self.request.GET.get('tipo', '').strip()
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        return queryset


class CategoriaFinanceiraCreateView(FinanceiroFormMixin, CreateView):
    model = CategoriaFinanceira
    form_class = CategoriaFinanceiraForm
    template_name = 'financeiro/categoria_form.html'
    success_url = reverse_lazy('financeiro:categoria-list')
    page_title = 'Nova Categoria Financeira'
    success_message = 'Categoria financeira cadastrada com sucesso.'


class CategoriaFinanceiraUpdateView(FinanceiroFormMixin, UpdateView):
    model = CategoriaFinanceira
    form_class = CategoriaFinanceiraForm
    template_name = 'financeiro/categoria_form.html'
    success_url = reverse_lazy('financeiro:categoria-list')
    page_title = 'Editar Categoria Financeira'
    submit_label = 'Atualizar'
    success_message = 'Categoria financeira atualizada com sucesso.'


class CategoriaFinanceiraDeleteView(FinanceiroDeleteMixin):
    model = CategoriaFinanceira
    success_url = reverse_lazy('financeiro:categoria-list')
    page_title = 'Excluir Categoria Financeira'
    cancel_url = reverse_lazy('financeiro:categoria-list')
    success_message = 'Categoria financeira excluida com sucesso.'


class LancamentoFinanceiroListView(ListView):
    model = LancamentoFinanceiro
    template_name = 'financeiro/lancamento_list.html'
    context_object_name = 'lancamentos'

    def get_queryset(self):
        queryset = super().get_queryset()
        descricao = self.request.GET.get('descricao', '').strip()
        numero_documento = self.request.GET.get('numero_documento', '').strip()
        tipo = self.request.GET.get('tipo', '').strip()
        status = self.request.GET.get('status', '').strip()
        if descricao:
            queryset = queryset.filter(descricao__icontains=descricao)
        if numero_documento:
            queryset = queryset.filter(numero_documento__icontains=numero_documento)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class LancamentoFinanceiroCreateView(FinanceiroFormMixin, CreateView):
    model = LancamentoFinanceiro
    form_class = LancamentoFinanceiroForm
    template_name = 'financeiro/lancamento_form.html'
    success_url = reverse_lazy('financeiro:lancamento-list')
    page_title = 'Novo Lancamento Financeiro'
    success_message = 'Lancamento financeiro cadastrado com sucesso.'


class LancamentoFinanceiroUpdateView(FinanceiroFormMixin, UpdateView):
    model = LancamentoFinanceiro
    form_class = LancamentoFinanceiroForm
    template_name = 'financeiro/lancamento_form.html'
    success_url = reverse_lazy('financeiro:lancamento-list')
    page_title = 'Editar Lancamento Financeiro'
    submit_label = 'Atualizar'
    success_message = 'Lancamento financeiro atualizado com sucesso.'


class LancamentoFinanceiroDeleteView(FinanceiroDeleteMixin):
    model = LancamentoFinanceiro
    success_url = reverse_lazy('financeiro:lancamento-list')
    page_title = 'Excluir Lancamento Financeiro'
    cancel_url = reverse_lazy('financeiro:lancamento-list')
    success_message = 'Lancamento financeiro excluido com sucesso.'
