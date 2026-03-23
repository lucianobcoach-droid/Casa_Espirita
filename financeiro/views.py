from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta
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


class ResumoFinanceiroView(TemplateView):
    template_name = 'financeiro/resumo.html'

    def _periodo_padrao(self) -> tuple[date, date]:
        hoje = date.today()
        primeiro_dia = hoje.replace(day=1)
        ultimo_dia = hoje.replace(day=monthrange(hoje.year, hoje.month)[1])
        return primeiro_dia, ultimo_dia

    def _saldo_consolidado_ate(self, data_referencia: date) -> Decimal:
        saldo = Decimal('0.00')
        contas = ContaFinanceira.objects.filter(data_saldo_inicial__lte=data_referencia).only(
            'saldo_inicial',
            'data_saldo_inicial',
        )
        for conta in contas:
            saldo += conta.saldo_inicial or Decimal('0.00')

        lancamentos = LancamentoFinanceiro.objects.filter(
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            data_competencia__lte=data_referencia,
            tipo__in=(
                LancamentoFinanceiro.TipoLancamento.RECEITA,
                LancamentoFinanceiro.TipoLancamento.DESPESA,
            ),
        ).only('tipo', 'valor')

        for lancamento in lancamentos:
            if lancamento.tipo == LancamentoFinanceiro.TipoLancamento.RECEITA:
                saldo += lancamento.valor
            elif lancamento.tipo == LancamentoFinanceiro.TipoLancamento.DESPESA:
                saldo -= lancamento.valor

        return saldo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data_inicial_raw = self.request.GET.get('data_inicial', '').strip()
        data_final_raw = self.request.GET.get('data_final', '').strip()
        periodo_error = ''

        if not data_inicial_raw and not data_final_raw:
            data_inicial, data_final = self._periodo_padrao()
            data_inicial_raw = data_inicial.isoformat()
            data_final_raw = data_final.isoformat()
        elif not data_inicial_raw or not data_final_raw:
            data_inicial = None
            data_final = None
            periodo_error = 'Informe data inicial e data final para gerar o resumo.'
        else:
            try:
                data_inicial = date.fromisoformat(data_inicial_raw)
                data_final = date.fromisoformat(data_final_raw)
            except ValueError:
                data_inicial = None
                data_final = None
                periodo_error = 'Periodo invalido. Revise as datas informadas.'

        if data_inicial and data_final and data_inicial > data_final:
            periodo_error = 'A data inicial nao pode ser maior que a data final.'
            data_inicial = None
            data_final = None

        context['page_title'] = 'Resumo do Periodo'
        context['data_inicial'] = data_inicial_raw
        context['data_final'] = data_final_raw
        context['periodo_error'] = periodo_error

        if not data_inicial or not data_final:
            return context

        dia_anterior = data_inicial - timedelta(days=1)
        saldo_inicial_consolidado = self._saldo_consolidado_ate(dia_anterior)
        saldo_final_consolidado = self._saldo_consolidado_ate(data_final)

        lancamentos_periodo = LancamentoFinanceiro.objects.filter(
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            data_competencia__gte=data_inicial,
            data_competencia__lte=data_final,
            tipo__in=(
                LancamentoFinanceiro.TipoLancamento.RECEITA,
                LancamentoFinanceiro.TipoLancamento.DESPESA,
            ),
        ).only('tipo', 'valor')

        total_receitas = Decimal('0.00')
        total_despesas = Decimal('0.00')
        for lancamento in lancamentos_periodo:
            if lancamento.tipo == LancamentoFinanceiro.TipoLancamento.RECEITA:
                total_receitas += lancamento.valor
            elif lancamento.tipo == LancamentoFinanceiro.TipoLancamento.DESPESA:
                total_despesas += lancamento.valor

        context['periodo_label'] = f'{data_inicial.strftime("%d/%m/%Y")} a {data_final.strftime("%d/%m/%Y")}'
        context['saldo_inicial_consolidado'] = saldo_inicial_consolidado
        context['total_receitas_periodo'] = total_receitas
        context['total_despesas_periodo'] = total_despesas
        context['saldo_final_consolidado'] = saldo_final_consolidado
        context['saldo_periodo'] = saldo_final_consolidado - saldo_inicial_consolidado
        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contas = list(context['contas'])
        contas_por_id = {conta.id: conta for conta in contas}

        for conta in contas:
            conta.saldo_atual = conta.saldo_inicial or Decimal('0.00')

        if contas_por_id:
            lancamentos = LancamentoFinanceiro.objects.filter(
                Q(conta_id__in=contas_por_id.keys()) | Q(conta_destino_id__in=contas_por_id.keys()),
                status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            ).only('tipo', 'valor', 'conta_id', 'conta_destino_id')

            for lancamento in lancamentos:
                if (
                    lancamento.tipo == LancamentoFinanceiro.TipoLancamento.RECEITA
                    and lancamento.conta_id in contas_por_id
                ):
                    contas_por_id[lancamento.conta_id].saldo_atual += lancamento.valor
                elif (
                    lancamento.tipo == LancamentoFinanceiro.TipoLancamento.DESPESA
                    and lancamento.conta_id in contas_por_id
                ):
                    contas_por_id[lancamento.conta_id].saldo_atual -= lancamento.valor
                elif lancamento.tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
                    if lancamento.conta_id in contas_por_id:
                        contas_por_id[lancamento.conta_id].saldo_atual -= lancamento.valor
                    if lancamento.conta_destino_id in contas_por_id:
                        contas_por_id[lancamento.conta_destino_id].saldo_atual += lancamento.valor

        context['contas'] = contas
        return context


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


class ExtratoContaMixin:
    def _classificar_lancamento(self, conta: ContaFinanceira, lancamento: LancamentoFinanceiro) -> tuple[Decimal, Decimal]:
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

        return entrada, saida

    def _get_extrato_context(
        self,
        conta: ContaFinanceira,
        data_inicial: str = '',
        data_final: str = '',
    ) -> dict[str, object]:
        queryset_base = (
            LancamentoFinanceiro.objects.filter(
                Q(conta=conta) | Q(conta_destino=conta),
                status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            )
            .select_related('conta', 'conta_destino', 'pessoa', 'categoria')
            .order_by('data_competencia', 'criado_em', 'pk')
        )

        saldo_anterior = conta.saldo_inicial or Decimal('0.00')
        if data_inicial:
            lancamentos_anteriores = queryset_base.filter(data_competencia__lt=data_inicial)
            for lancamento in lancamentos_anteriores:
                entrada, saida = self._classificar_lancamento(conta, lancamento)
                saldo_anterior += entrada - saida

        lancamentos = queryset_base
        if data_inicial:
            lancamentos = lancamentos.filter(data_competencia__gte=data_inicial)
        if data_final:
            lancamentos = lancamentos.filter(data_competencia__lte=data_final)

        saldo_acumulado = saldo_anterior if data_inicial else (conta.saldo_inicial or Decimal('0.00'))
        itens_extrato: list[dict[str, object]] = []
        for lancamento in lancamentos:
            entrada, saida = self._classificar_lancamento(conta, lancamento)
            saldo_acumulado += entrada - saida
            itens_extrato.append(
                {
                    'lancamento': lancamento,
                    'entrada': entrada,
                    'saida': saida,
                    'saldo_acumulado': saldo_acumulado,
                }
            )

        return {
            'conta': conta,
            'saldo_inicial': conta.saldo_inicial or Decimal('0.00'),
            'data_saldo_inicial': conta.data_saldo_inicial,
            'data_inicial': data_inicial,
            'data_final': data_final,
            'saldo_anterior': saldo_anterior if data_inicial else None,
            'exibe_linha_saldo_inicial': not (data_inicial or data_final),
            'itens_extrato': itens_extrato,
            'saldo_final': saldo_acumulado,
            'saldo_atual': saldo_acumulado,
        }


class ContaFinanceiraExtratoView(ExtratoContaMixin, DetailView):
    model = ContaFinanceira
    template_name = 'financeiro/conta_extrato.html'
    context_object_name = 'conta'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conta = self.object
        data_inicial = self.request.GET.get('data_inicial', '').strip()
        data_final = self.request.GET.get('data_final', '').strip()

        context.update(self._get_extrato_context(conta, data_inicial, data_final))
        context['page_title'] = f'Extrato da Conta: {conta.nome}'
        context['show_conta_filter'] = False
        context['clear_extrato_url'] = reverse_lazy('financeiro:conta-extrato', kwargs={'pk': conta.pk})
        return context


class ExtratoFinanceiroView(ExtratoContaMixin, TemplateView):
    template_name = 'financeiro/conta_extrato.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conta_id = self.request.GET.get('conta', '').strip()
        data_inicial = self.request.GET.get('data_inicial', '').strip()
        data_final = self.request.GET.get('data_final', '').strip()
        contas = ContaFinanceira.objects.order_by('nome')

        context['page_title'] = 'Extratos'
        context['contas'] = contas
        context['conta_selecionada_id'] = conta_id
        context['show_conta_filter'] = True
        context['clear_extrato_url'] = reverse_lazy('financeiro:extrato-list')

        if conta_id:
            try:
                conta = contas.get(pk=conta_id)
            except ContaFinanceira.DoesNotExist:
                context['extrato_error'] = 'Conta financeira nao encontrada.'
            else:
                context.update(self._get_extrato_context(conta, data_inicial, data_final))
                context['page_title'] = f'Extratos - {conta.nome}'

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
