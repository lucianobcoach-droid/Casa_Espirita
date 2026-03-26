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


class FinanceiroPeriodoMixin:
    def _periodo_padrao(self) -> tuple[date, date]:
        hoje = date.today()
        primeiro_dia = hoje.replace(day=1)
        ultimo_dia = hoje.replace(day=monthrange(hoje.year, hoje.month)[1])
        return primeiro_dia, ultimo_dia

    def _parse_contas(self) -> tuple[list[ContaFinanceira], list[str], list[int]]:
        contas_disponiveis = list(ContaFinanceira.objects.order_by('nome'))
        contas_por_id = {conta.id: conta for conta in contas_disponiveis}
        selected_ids_raw = [valor.strip() for valor in self.request.GET.getlist('contas') if valor.strip()]

        selected_ids: list[int] = []
        for valor in selected_ids_raw:
            try:
                conta_id = int(valor)
            except ValueError:
                continue
            if conta_id in contas_por_id:
                selected_ids.append(conta_id)

        if not selected_ids:
            selected_ids = list(contas_por_id.keys())

        return contas_disponiveis, selected_ids_raw, selected_ids

    def _parse_periodo(self) -> tuple[str, str, date | None, date | None, str]:
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

        return data_inicial_raw, data_final_raw, data_inicial, data_final, periodo_error

    def _parse_checkbox(self, param_name: str) -> bool:
        valores = [valor.strip().lower() for valor in self.request.GET.getlist(param_name)]
        if not valores:
            return False

        for valor in reversed(valores):
            if valor in {'1', 'true', 'on', 'yes'}:
                return True
            if valor in {'0', 'false', 'off', 'no', ''}:
                return False
        return False

    def _calcular_saldos_por_conta(
        self,
        data_referencia: date,
        selected_ids: list[int],
    ) -> tuple[list[dict[str, object]], Decimal]:
        contas = list(
            ContaFinanceira.objects.filter(id__in=selected_ids, data_saldo_inicial__lte=data_referencia)
            .only('id', 'nome', 'saldo_inicial', 'data_saldo_inicial')
            .order_by('nome')
        )
        contas_por_id = {conta.id: conta for conta in contas}

        for conta in contas:
            conta.saldo_calculado = conta.saldo_inicial or Decimal('0.00')

        if contas_por_id:
            lancamentos = LancamentoFinanceiro.objects.filter(
                Q(conta_id__in=contas_por_id.keys()) | Q(conta_destino_id__in=contas_por_id.keys()),
                status=LancamentoFinanceiro.StatusLancamento.QUITADO,
                data_competencia__lte=data_referencia,
            ).only('tipo', 'valor', 'conta_id', 'conta_destino_id')

            for lancamento in lancamentos:
                if (
                    lancamento.tipo == LancamentoFinanceiro.TipoLancamento.RECEITA
                    and lancamento.conta_id in contas_por_id
                ):
                    contas_por_id[lancamento.conta_id].saldo_calculado += lancamento.valor
                elif (
                    lancamento.tipo == LancamentoFinanceiro.TipoLancamento.DESPESA
                    and lancamento.conta_id in contas_por_id
                ):
                    contas_por_id[lancamento.conta_id].saldo_calculado -= lancamento.valor
                elif lancamento.tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
                    if lancamento.conta_id in contas_por_id:
                        contas_por_id[lancamento.conta_id].saldo_calculado -= lancamento.valor
                    if lancamento.conta_destino_id in contas_por_id:
                        contas_por_id[lancamento.conta_destino_id].saldo_calculado += lancamento.valor

        composicao = [{'conta': conta, 'saldo': conta.saldo_calculado} for conta in contas]
        total = sum((item['saldo'] for item in composicao), Decimal('0.00'))
        return composicao, total

    def _lancamentos_receitas_despesas(
        self,
        data_inicial: date,
        data_final: date,
        selected_ids: list[int],
    ) -> tuple[list[LancamentoFinanceiro], list[LancamentoFinanceiro], Decimal, Decimal]:
        receitas = list(
            LancamentoFinanceiro.objects.filter(
                status=LancamentoFinanceiro.StatusLancamento.QUITADO,
                tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
                conta_id__in=selected_ids,
                data_competencia__gte=data_inicial,
                data_competencia__lte=data_final,
            )
            .select_related('conta', 'pessoa', 'categoria', 'centro_custo')
            .order_by('data_competencia', 'criado_em', 'pk')
        )
        despesas = list(
            LancamentoFinanceiro.objects.filter(
                status=LancamentoFinanceiro.StatusLancamento.QUITADO,
                tipo=LancamentoFinanceiro.TipoLancamento.DESPESA,
                conta_id__in=selected_ids,
                data_competencia__gte=data_inicial,
                data_competencia__lte=data_final,
            )
            .select_related('conta', 'pessoa', 'categoria', 'centro_custo')
            .order_by('data_competencia', 'criado_em', 'pk')
        )
        total_receitas = sum((lancamento.valor for lancamento in receitas), Decimal('0.00'))
        total_despesas = sum((lancamento.valor for lancamento in despesas), Decimal('0.00'))
        return receitas, despesas, total_receitas, total_despesas

    def _agrupar_por_campo(
        self,
        lancamentos: list[LancamentoFinanceiro],
        attr_name: str,
        fallback_label: str,
        label_key: str = 'label',
    ) -> tuple[list[dict[str, object]], Decimal]:
        agrupado: dict[str, Decimal] = {}
        for lancamento in lancamentos:
            related_obj = getattr(lancamento, attr_name)
            label = str(related_obj) if related_obj else fallback_label
            agrupado[label] = agrupado.get(label, Decimal('0.00')) + lancamento.valor

        itens = [
            {label_key: label, 'valor': valor}
            for label, valor in sorted(agrupado.items(), key=lambda item: item[0].lower())
        ]
        total = sum((item['valor'] for item in itens), Decimal('0.00'))
        return itens, total

    def _build_periodo_context(self) -> dict[str, object]:
        contas_disponiveis, selected_ids_raw, selected_ids = self._parse_contas()
        data_inicial_raw, data_final_raw, data_inicial, data_final, periodo_error = self._parse_periodo()
        mostrar_centro_custo = self._parse_checkbox('mostrar_centro_custo')
        contas_selecionadas = [conta for conta in contas_disponiveis if conta.id in selected_ids]
        context: dict[str, object] = {
            'data_inicial': data_inicial_raw,
            'data_final': data_final_raw,
            'periodo_error': periodo_error,
            'contas_disponiveis': contas_disponiveis,
            'contas_selecionadas_ids': [str(conta_id) for conta_id in selected_ids],
            'contas_selecionadas': contas_selecionadas,
            'contas_incluidas_label': (
                'Todas as contas'
                if len(selected_ids) == len(contas_disponiveis)
                else ', '.join(conta.nome for conta in contas_selecionadas)
            ),
            'quantidade_contas_selecionadas': len(contas_selecionadas),
            'mostrar_centro_custo': mostrar_centro_custo,
        }

        if not data_inicial or not data_final:
            return context

        dia_anterior = data_inicial - timedelta(days=1)
        composicao_inicial, saldo_inicial_consolidado = self._calcular_saldos_por_conta(dia_anterior, selected_ids)
        composicao_final, saldo_final_consolidado = self._calcular_saldos_por_conta(data_final, selected_ids)
        receitas, despesas, total_receitas, total_despesas = self._lancamentos_receitas_despesas(
            data_inicial,
            data_final,
            selected_ids,
        )
        context.update(
            {
                'periodo_label': f'{data_inicial.strftime("%d/%m/%Y")} a {data_final.strftime("%d/%m/%Y")}',
                'saldo_inicial_consolidado': saldo_inicial_consolidado,
                'total_receitas_periodo': total_receitas,
                'total_despesas_periodo': total_despesas,
                'saldo_final_consolidado': saldo_final_consolidado,
                'saldo_periodo': saldo_final_consolidado - saldo_inicial_consolidado,
                'composicao_inicial': composicao_inicial,
                'composicao_final': composicao_final,
                'receitas_periodo': receitas,
                'despesas_periodo': despesas,
            }
        )

        receitas_por_categoria, total_receitas_por_categoria = self._agrupar_por_campo(
            receitas,
            'categoria',
            'Sem categoria',
            label_key='categoria',
        )
        despesas_por_categoria, total_despesas_por_categoria = self._agrupar_por_campo(
            despesas,
            'categoria',
            'Sem categoria',
            label_key='categoria',
        )
        despesas_por_centro_custo, total_despesas_por_centro_custo = self._agrupar_por_campo(
            despesas,
            'centro_custo',
            'Sem centro de custo',
        )
        context.update(
            {
                'receitas_por_categoria': receitas_por_categoria,
                'despesas_por_categoria': despesas_por_categoria,
                'total_receitas_por_categoria': total_receitas_por_categoria,
                'total_despesas_por_categoria': total_despesas_por_categoria,
                'despesas_por_centro_custo': despesas_por_centro_custo,
                'total_despesas_por_centro_custo': total_despesas_por_centro_custo,
                'existe_lancamento_sem_categoria': any(
                    lancamento.categoria_id is None for lancamento in [*receitas, *despesas]
                ),
                'existe_lancamento_sem_centro_custo': any(
                    lancamento.centro_custo_id is None for lancamento in despesas
                ),
            }
        )
        return context


class ResumoFinanceiroView(FinanceiroPeriodoMixin, TemplateView):
    template_name = 'financeiro/resumo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Resumo do Periodo'
        context.update(self._build_periodo_context())
        return context


class PrestacaoContasFinanceiroView(FinanceiroPeriodoMixin, TemplateView):
    template_name = 'financeiro/prestacao_contas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Prestacao de Contas'
        context.update(self._build_periodo_context())
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


class PessoaFinanceiraUltimosLancamentosView(View):
    limit = 5

    def get(self, request, pessoa_id: int, *args, **kwargs):
        lancamentos = list(
            LancamentoFinanceiro.objects.filter(pessoa_id=pessoa_id)
            .select_related('categoria')
            .order_by('-data_competencia', '-criado_em', '-pk')[: self.limit]
        )
        results = [
            {
                'data': lancamento.data_competencia.strftime('%d/%m/%Y'),
                'tipo': lancamento.get_tipo_display(),
                'descricao': lancamento.descricao,
                'valor': f'R$ {lancamento.valor:.2f}',
                'categoria': str(lancamento.categoria) if lancamento.categoria else 'Sem categoria',
                'numero_documento': lancamento.numero_documento or '',
            }
            for lancamento in lancamentos
        ]
        return JsonResponse({'results': results})


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
        queryset = super().get_queryset().select_related(
            'conta',
            'conta_destino',
            'pessoa',
            'categoria',
        )
        descricao = self.request.GET.get('descricao', '').strip()
        numero_documento = self.request.GET.get('numero_documento', '').strip()
        tipo = self.request.GET.get('tipo', '').strip()
        status = self.request.GET.get('status', '').strip()
        data_inicial = self.request.GET.get('data_inicial', '').strip()
        data_final = self.request.GET.get('data_final', '').strip()
        conta = self.request.GET.get('conta', '').strip()
        pessoa = self.request.GET.get('pessoa', '').strip()
        categoria = self.request.GET.get('categoria', '').strip()
        if descricao:
            queryset = queryset.filter(descricao__icontains=descricao)
        if numero_documento:
            queryset = queryset.filter(numero_documento__icontains=numero_documento)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if status:
            queryset = queryset.filter(status=status)
        if data_inicial:
            queryset = queryset.filter(data_competencia__gte=data_inicial)
        if data_final:
            queryset = queryset.filter(data_competencia__lte=data_final)
        if conta:
            queryset = queryset.filter(Q(conta_id=conta) | Q(conta_destino_id=conta))
        if pessoa:
            queryset = queryset.filter(pessoa_id=pessoa)
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contas_disponiveis'] = ContaFinanceira.objects.order_by('nome')
        context['pessoas_disponiveis'] = PessoaFinanceira.objects.order_by('nome')
        context['categorias_disponiveis'] = CategoriaFinanceira.objects.order_by('tipo', 'nome')
        return context


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


class LancamentoFinanceiroReciboView(DetailView):
    model = LancamentoFinanceiro
    template_name = 'financeiro/lancamento_recibo.html'
    context_object_name = 'lancamento'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'conta',
            'conta_destino',
            'pessoa',
            'categoria',
            'centro_custo',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data_recibo = self.object.data_pagamento or self.object.data_competencia
        context['page_title'] = f'Recibo do Lancamento {self.object.pk}'
        context['recibo_referente'] = self.object.descricao
        context['recibo_data_principal'] = data_recibo
        context['recibo_data_label'] = (
            'Data do recebimento'
            if self.object.data_pagamento
            else 'Data do recibo (fallback da data de competencia)'
        )
        context['recibo_data_fallback'] = self.object.data_pagamento is None
        context['recibo_mensagem_final'] = 'Recibo emitido com base no lancamento registrado no sistema.'
        return context


class LancamentoFinanceiroDeleteView(FinanceiroDeleteMixin):
    model = LancamentoFinanceiro
    success_url = reverse_lazy('financeiro:lancamento-list')
    page_title = 'Excluir Lancamento Financeiro'
    cancel_url = reverse_lazy('financeiro:lancamento-list')
    success_message = 'Lancamento financeiro excluido com sucesso.'
