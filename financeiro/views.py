from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, timedelta
from decimal import Decimal
from urllib.parse import urlencode
from uuid import uuid4

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import (
    AssinaturaInstitucionalForm,
    CategoriaFinanceiraForm,
    ConfiguracaoInstitucionalForm,
    CentroCustoForm,
    ContaFinanceiraForm,
    LancamentoFinanceiroForm,
    LancamentoFinanceiroGrupoRateioForm,
    PessoaFinanceiraForm,
)
from .models import (
    AssinaturaInstitucional,
    AuditoriaFinanceiro,
    CategoriaFinanceira,
    ConfiguracaoInstitucional,
    CentroCusto,
    ContaFinanceira,
    LancamentoFinanceiro,
    PessoaFinanceira,
)


def _auditoria_usuario(request):
    usuario = getattr(request, 'user', None)
    if usuario and getattr(usuario, 'is_authenticated', False):
        return usuario
    return None


def _auditoria_normalizar_valor(valor):
    if isinstance(valor, Decimal):
        return str(valor)
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    if hasattr(valor, 'pk'):
        return valor.pk
    return valor


def _snapshot_model(instance, *, ignore_fields: set[str] | None = None) -> dict[str, object]:
    snapshot: dict[str, object] = {}
    ignore_fields = ignore_fields or set()
    for field in instance._meta.concrete_fields:
        if field.name in ignore_fields:
            continue
        snapshot[field.name] = _auditoria_normalizar_valor(getattr(instance, field.attname))
    return snapshot


def _snapshot_lancamento(lancamento: LancamentoFinanceiro) -> dict[str, object]:
    return _snapshot_model(lancamento, ignore_fields={'criado_em', 'atualizado_em'})


def _snapshot_conta(conta: ContaFinanceira) -> dict[str, object]:
    return _snapshot_model(conta, ignore_fields={'criado_em', 'atualizado_em'})


def _build_auditoria_payload(
    antes: dict[str, object] | None,
    depois: dict[str, object] | None,
) -> dict[str, dict[str, object]]:
    chaves = set((antes or {}).keys()) | set((depois or {}).keys())
    alteracoes: dict[str, dict[str, object]] = {}

    for chave in sorted(chaves):
        valor_antes = (antes or {}).get(chave)
        valor_depois = (depois or {}).get(chave)
        if valor_antes != valor_depois:
            alteracoes[chave] = {
                'before': valor_antes,
                'after': valor_depois,
            }

    return alteracoes


def _registrar_auditoria_lancamento(
    *,
    request,
    acao: str,
    lancamento: LancamentoFinanceiro,
    antes: dict[str, object] | None = None,
    depois: dict[str, object] | None = None,
) -> AuditoriaFinanceiro:
    return AuditoriaFinanceiro.objects.create(
        acao=acao,
        modelo='LancamentoFinanceiro',
        registro_id=lancamento.pk,
        usuario=_auditoria_usuario(request),
        campos_alterados=_build_auditoria_payload(antes, depois),
    )


def _registrar_auditoria_conta(
    *,
    request,
    acao: str,
    conta: ContaFinanceira,
    antes: dict[str, object] | None = None,
    depois: dict[str, object] | None = None,
) -> AuditoriaFinanceiro:
    return AuditoriaFinanceiro.objects.create(
        acao=acao,
        modelo='ContaFinanceira',
        registro_id=conta.pk,
        usuario=_auditoria_usuario(request),
        campos_alterados=_build_auditoria_payload(antes, depois),
    )


UNIDADES_EXTENSO = (
    'zero',
    'um',
    'dois',
    'tres',
    'quatro',
    'cinco',
    'seis',
    'sete',
    'oito',
    'nove',
    'dez',
    'onze',
    'doze',
    'treze',
    'quatorze',
    'quinze',
    'dezesseis',
    'dezessete',
    'dezoito',
    'dezenove',
)
DEZENAS_EXTENSO = (
    '',
    '',
    'vinte',
    'trinta',
    'quarenta',
    'cinquenta',
    'sessenta',
    'setenta',
    'oitenta',
    'noventa',
)
CENTENAS_EXTENSO = (
    '',
    'cento',
    'duzentos',
    'trezentos',
    'quatrocentos',
    'quinhentos',
    'seiscentos',
    'setecentos',
    'oitocentos',
    'novecentos',
)
MESES_EXTENSO = (
    'janeiro',
    'fevereiro',
    'marco',
    'abril',
    'maio',
    'junho',
    'julho',
    'agosto',
    'setembro',
    'outubro',
    'novembro',
    'dezembro',
)


def _centena_por_extenso(numero: int) -> str:
    if numero == 0:
        return ''
    if numero < 20:
        return UNIDADES_EXTENSO[numero]
    if numero < 100:
        dezena, resto = divmod(numero, 10)
        texto = DEZENAS_EXTENSO[dezena]
        if resto:
            texto = f'{texto} e {UNIDADES_EXTENSO[resto]}'
        return texto
    if numero == 100:
        return 'cem'
    centena, resto = divmod(numero, 100)
    texto = CENTENAS_EXTENSO[centena]
    if resto:
        texto = f'{texto} e {_centena_por_extenso(resto)}'
    return texto


def _juntar_partes_extenso(partes: list[str]) -> str:
    if not partes:
        return ''
    if len(partes) == 1:
        return partes[0]
    if len(partes) == 2:
        return f'{partes[0]} e {partes[1]}'
    return ', '.join(partes[:-1]) + f' e {partes[-1]}'


def _numero_por_extenso(numero: int) -> str:
    if numero == 0:
        return UNIDADES_EXTENSO[0]

    grupos = [
        ('', ''),
        ('mil', 'mil'),
        ('milhao', 'milhoes'),
        ('bilhao', 'bilhoes'),
    ]
    partes: list[str] = []
    indice_grupo = 0

    while numero > 0:
        numero, grupo_valor = divmod(numero, 1000)
        if grupo_valor:
            grupo_singular, grupo_plural = grupos[indice_grupo]
            if indice_grupo == 1 and grupo_valor == 1:
                partes.append('mil')
            else:
                texto_grupo = _centena_por_extenso(grupo_valor)
                if indice_grupo > 0:
                    sufixo = grupo_singular if grupo_valor == 1 else grupo_plural
                    texto_grupo = f'{texto_grupo} {sufixo}'
                partes.append(texto_grupo)
        indice_grupo += 1

    partes.reverse()
    return _juntar_partes_extenso(partes)


def _valor_por_extenso(valor: Decimal) -> str:
    valor_normalizado = valor.quantize(Decimal('0.01'))
    reais = int(valor_normalizado)
    centavos = int((valor_normalizado - Decimal(reais)) * 100)

    partes: list[str] = []
    if reais or not centavos:
        unidade_real = 'real' if reais == 1 else 'reais'
        partes.append(f'{_numero_por_extenso(reais)} {unidade_real}')
    if centavos:
        unidade_centavo = 'centavo' if centavos == 1 else 'centavos'
        partes.append(f'{_numero_por_extenso(centavos)} {unidade_centavo}')

    return _juntar_partes_extenso(partes)


def _data_documental_por_extenso(data_referencia: date) -> str:
    return f'{data_referencia.day} de {MESES_EXTENSO[data_referencia.month - 1]} de {data_referencia.year}'


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

    def form_valid(self, form):
        response = super().form_valid(form)
        _registrar_auditoria_conta(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
            conta=self.object,
            depois=_snapshot_conta(self.object),
        )
        return response


class ContaFinanceiraUpdateView(FinanceiroFormMixin, UpdateView):
    model = ContaFinanceira
    form_class = ContaFinanceiraForm
    template_name = 'financeiro/conta_form.html'
    success_url = reverse_lazy('financeiro:conta-list')
    page_title = 'Editar Conta Financeira'
    submit_label = 'Atualizar'
    success_message = 'Conta financeira atualizada com sucesso.'

    def form_valid(self, form):
        antes = _snapshot_conta(
            ContaFinanceira.objects.get(pk=self.object.pk)
        )
        response = super().form_valid(form)
        depois = _snapshot_conta(self.object)
        _registrar_auditoria_conta(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.UPDATE,
            conta=self.object,
            antes=antes,
            depois=depois,
        )
        return response


class ContaFinanceiraDeleteView(FinanceiroDeleteMixin):
    model = ContaFinanceira
    success_url = reverse_lazy('financeiro:conta-list')
    page_title = 'Excluir Conta Financeira'
    cancel_url = reverse_lazy('financeiro:conta-list')
    success_message = 'Conta financeira excluida com sucesso.'

    def form_valid(self, form):
        conta = self.object
        antes = _snapshot_conta(conta)
        registro_id = conta.pk

        with transaction.atomic():
            response = super().form_valid(form)
            AuditoriaFinanceiro.objects.create(
                acao=AuditoriaFinanceiro.AcaoAuditoria.DELETE,
                modelo='ContaFinanceira',
                registro_id=registro_id,
                usuario=_auditoria_usuario(self.request),
                campos_alterados=_build_auditoria_payload(antes, None),
            )

        return response


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

    def _chave_bloco_extrato(self, lancamento: LancamentoFinanceiro) -> str:
        grupo_rateio = (lancamento.grupo_rateio or '').strip()
        if lancamento.com_rateio and grupo_rateio:
            return f'rateio:{grupo_rateio}'
        return f'lancamento:{lancamento.pk}'

    def _montar_itens_extrato(
        self,
        conta: ContaFinanceira,
        lancamentos: list[LancamentoFinanceiro],
        saldo_inicial: Decimal,
    ) -> tuple[list[dict[str, object]], Decimal]:
        blocos: list[list[LancamentoFinanceiro]] = []
        blocos_por_chave: dict[str, list[LancamentoFinanceiro]] = {}

        for lancamento in lancamentos:
            chave_bloco = self._chave_bloco_extrato(lancamento)
            bloco = blocos_por_chave.get(chave_bloco)
            if bloco is None:
                bloco = []
                blocos_por_chave[chave_bloco] = bloco
                blocos.append(bloco)
            bloco.append(lancamento)

        saldo_acumulado = saldo_inicial
        itens_extrato: list[dict[str, object]] = []

        for bloco in blocos:
            lancamento_representante = bloco[0]
            entrada_total = Decimal('0.00')
            saida_total = Decimal('0.00')

            for lancamento in bloco:
                entrada, saida = self._classificar_lancamento(conta, lancamento)
                entrada_total += entrada
                saida_total += saida

            saldo_acumulado += entrada_total - saida_total
            observacoes = next(
                ((lancamento.observacoes or '').strip() for lancamento in bloco if (lancamento.observacoes or '').strip()),
                '',
            )

            itens_extrato.append(
                {
                    'lancamento': lancamento_representante,
                    'entrada': entrada_total,
                    'saida': saida_total,
                    'saldo_acumulado': saldo_acumulado,
                    'rateio_consolidado': len(bloco) > 1 and bool((lancamento_representante.grupo_rateio or '').strip()),
                    'quantidade_linhas_rateio': len(bloco),
                    'observacoes_exibicao': observacoes or '-',
                }
            )

        return itens_extrato, saldo_acumulado

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

        saldo_base = saldo_anterior if data_inicial else (conta.saldo_inicial or Decimal('0.00'))
        itens_extrato, saldo_acumulado = self._montar_itens_extrato(conta, list(lancamentos), saldo_base)

        return {
            'conta': conta,
            'saldo_inicial': conta.saldo_inicial or Decimal('0.00'),
            'data_saldo_inicial': conta.data_saldo_inicial,
            'data_inicial': data_inicial,
            'data_final': data_final,
            'saldo_anterior': saldo_anterior if data_inicial else None,
            'exibe_linha_saldo_inicial': True,
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


class AuditoriaLancamentoFinanceiroListView(ListView):
    model = AuditoriaFinanceiro
    template_name = 'financeiro/auditoria_lancamento_list.html'
    context_object_name = 'auditorias'

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(modelo__in=['LancamentoFinanceiro', 'ContaFinanceira'])
            .select_related('usuario')
        )
        acao = self.request.GET.get('acao', '').strip()
        data_inicial = self.request.GET.get('data_inicial', '').strip()
        data_final = self.request.GET.get('data_final', '').strip()
        registro_id = self.request.GET.get('registro_id', '').strip()

        if acao:
            queryset = queryset.filter(acao=acao)

        if data_inicial:
            try:
                data_inicial_valor = date.fromisoformat(data_inicial)
            except ValueError:
                data_inicial_valor = None
            if data_inicial_valor:
                queryset = queryset.filter(data_hora__date__gte=data_inicial_valor)

        if data_final:
            try:
                data_final_valor = date.fromisoformat(data_final)
            except ValueError:
                data_final_valor = None
            if data_final_valor:
                queryset = queryset.filter(data_hora__date__lte=data_final_valor)

        if registro_id:
            try:
                registro_id_valor = int(registro_id)
            except ValueError:
                registro_id_valor = None
            if registro_id_valor is not None:
                queryset = queryset.filter(registro_id=registro_id_valor)

        return queryset.order_by('-data_hora', '-pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Auditoria do Financeiro'
        context['filtro_acao'] = self.request.GET.get('acao', '').strip()
        context['filtro_data_inicial'] = self.request.GET.get('data_inicial', '').strip()
        context['filtro_data_final'] = self.request.GET.get('data_final', '').strip()
        context['filtro_registro_id'] = self.request.GET.get('registro_id', '').strip()
        context['acoes_auditoria'] = AuditoriaFinanceiro.AcaoAuditoria.choices
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


class AssinaturaInstitucionalListView(ListView):
    model = AssinaturaInstitucional
    template_name = 'financeiro/assinatura_list.html'
    context_object_name = 'assinaturas'

    def get_queryset(self):
        queryset = super().get_queryset()
        nome = self.request.GET.get('nome', '').strip()
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        return queryset


class AssinaturaInstitucionalCreateView(FinanceiroFormMixin, CreateView):
    model = AssinaturaInstitucional
    form_class = AssinaturaInstitucionalForm
    template_name = 'financeiro/assinatura_form.html'
    success_url = reverse_lazy('financeiro:assinatura-list')
    page_title = 'Nova Assinatura Institucional'
    success_message = 'Assinatura institucional cadastrada com sucesso.'


class AssinaturaInstitucionalUpdateView(FinanceiroFormMixin, UpdateView):
    model = AssinaturaInstitucional
    form_class = AssinaturaInstitucionalForm
    template_name = 'financeiro/assinatura_form.html'
    success_url = reverse_lazy('financeiro:assinatura-list')
    page_title = 'Editar Assinatura Institucional'
    submit_label = 'Atualizar'
    success_message = 'Assinatura institucional atualizada com sucesso.'


class AssinaturaInstitucionalDeleteView(FinanceiroDeleteMixin):
    model = AssinaturaInstitucional
    success_url = reverse_lazy('financeiro:assinatura-list')
    page_title = 'Excluir Assinatura Institucional'
    cancel_url = reverse_lazy('financeiro:assinatura-list')
    success_message = 'Assinatura institucional excluida com sucesso.'


class ConfiguracaoInstitucionalListView(ListView):
    model = ConfiguracaoInstitucional
    template_name = 'financeiro/configuracao_institucional_list.html'
    context_object_name = 'configuracoes'

    def get_queryset(self):
        queryset = super().get_queryset()
        nome = self.request.GET.get('nome_instituicao', '').strip()
        if nome:
            queryset = queryset.filter(nome_instituicao__icontains=nome)
        return queryset


class ConfiguracaoInstitucionalCreateView(FinanceiroFormMixin, CreateView):
    model = ConfiguracaoInstitucional
    form_class = ConfiguracaoInstitucionalForm
    template_name = 'financeiro/configuracao_institucional_form.html'
    success_url = reverse_lazy('financeiro:configuracao-institucional-list')
    page_title = 'Nova Configuracao Institucional'
    success_message = 'Configuracao institucional cadastrada com sucesso.'


class ConfiguracaoInstitucionalUpdateView(FinanceiroFormMixin, UpdateView):
    model = ConfiguracaoInstitucional
    form_class = ConfiguracaoInstitucionalForm
    template_name = 'financeiro/configuracao_institucional_form.html'
    success_url = reverse_lazy('financeiro:configuracao-institucional-list')
    page_title = 'Editar Configuracao Institucional'
    submit_label = 'Atualizar'
    success_message = 'Configuracao institucional atualizada com sucesso.'


class ConfiguracaoInstitucionalDeleteView(FinanceiroDeleteMixin):
    model = ConfiguracaoInstitucional
    success_url = reverse_lazy('financeiro:configuracao-institucional-list')
    page_title = 'Excluir Configuracao Institucional'
    cancel_url = reverse_lazy('financeiro:configuracao-institucional-list')
    success_message = 'Configuracao institucional excluida com sucesso.'


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
        return queryset.order_by('-data_competencia', '-data_pagamento', '-criado_em', '-pk')

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rateio_categoria_opcoes'] = [
            {'id': categoria.pk, 'label': str(categoria)}
            for categoria in CategoriaFinanceira.objects.order_by('tipo', 'nome')
        ]
        return context

    def form_valid(self, form):
        if not form.cleaned_data.get('lancamento_com_rateio'):
            response = super().form_valid(form)
            _registrar_auditoria_lancamento(
                request=self.request,
                acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
                lancamento=self.object,
                depois=_snapshot_lancamento(self.object),
            )
            return response

        rateio_linhas = form.cleaned_data.get('rateio_linhas') or []
        grupo_rateio = form.cleaned_data.get('grupo_rateio') or uuid4().hex
        numero_documento = (form.cleaned_data.get('numero_documento') or '').strip()

        if not numero_documento:
            numero_documento = LancamentoFinanceiro(
                data_competencia=form.cleaned_data['data_competencia']
            )._gerar_numero_documento()

        dados_comuns = {
            'descricao': form.cleaned_data['descricao'],
            'tipo': form.cleaned_data['tipo'],
            'status': form.cleaned_data['status'],
            'data_competencia': form.cleaned_data['data_competencia'],
            'data_pagamento': form.cleaned_data.get('data_pagamento'),
            'numero_documento': numero_documento,
            'pessoa': form.cleaned_data.get('pessoa'),
            'centro_custo': form.cleaned_data.get('centro_custo'),
            'conta': form.cleaned_data['conta'],
            'conta_destino': form.cleaned_data.get('conta_destino'),
            'observacoes': form.cleaned_data.get('observacoes', ''),
            'com_rateio': True,
            'grupo_rateio': grupo_rateio,
        }

        lancamentos_criados: list[LancamentoFinanceiro] = []
        with transaction.atomic():
            for linha in rateio_linhas:
                lancamento = LancamentoFinanceiro.objects.create(
                    **dados_comuns,
                    categoria=linha['categoria'],
                    valor=linha['valor'],
                )
                lancamentos_criados.append(lancamento)
                _registrar_auditoria_lancamento(
                    request=self.request,
                    acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
                    lancamento=lancamento,
                    depois=_snapshot_lancamento(lancamento),
                )

        if lancamentos_criados:
            self.object = lancamentos_criados[0]

        messages.success(
            self.request,
            f'Lancamento com rateio cadastrado com sucesso em {len(lancamentos_criados)} linhas.',
        )
        return redirect(self.success_url)


class LancamentoFinanceiroUpdateView(FinanceiroFormMixin, UpdateView):
    model = LancamentoFinanceiro
    form_class = LancamentoFinanceiroForm
    template_name = 'financeiro/lancamento_form.html'
    success_url = reverse_lazy('financeiro:lancamento-list')
    page_title = 'Editar Lancamento Financeiro'
    submit_label = 'Atualizar'
    success_message = 'Lancamento financeiro atualizado com sucesso.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rateio_categoria_opcoes'] = [
            {'id': categoria.pk, 'label': str(categoria)}
            for categoria in CategoriaFinanceira.objects.order_by('tipo', 'nome')
        ]
        return context

    def form_valid(self, form):
        antes = _snapshot_lancamento(
            LancamentoFinanceiro.objects.get(pk=self.object.pk)
        )
        response = super().form_valid(form)
        depois = _snapshot_lancamento(self.object)
        _registrar_auditoria_lancamento(
            request=self.request,
            acao=AuditoriaFinanceiro.AcaoAuditoria.UPDATE,
            lancamento=self.object,
            antes=antes,
            depois=depois,
        )
        return response


class LancamentoFinanceiroGrupoRateioUpdateView(FinanceiroFormMixin, UpdateView):
    model = LancamentoFinanceiro
    form_class = LancamentoFinanceiroGrupoRateioForm
    template_name = 'financeiro/lancamento_rateio_grupo_form.html'
    success_url = reverse_lazy('financeiro:lancamento-list')
    page_title = 'Editar Lancamento Financeiro'
    submit_label = 'Atualizar'

    def _get_grupo_info(self) -> dict[str, object]:
        if hasattr(self, '_grupo_info_cache'):
            return self._grupo_info_cache

        grupo_rateio = (self.kwargs.get('grupo_rateio') or '').strip()
        lancamentos = list(
            LancamentoFinanceiro.objects.filter(
                com_rateio=True,
                grupo_rateio=grupo_rateio,
            )
            .select_related(
                'conta',
                'conta_destino',
                'pessoa',
                'categoria',
                'centro_custo',
            )
            .order_by('pk')
        )

        erro = ''
        erro_codigo = ''
        if not grupo_rateio:
            erro = 'Grupo de rateio invalido para edicao coordenada.'
            erro_codigo = 'grupo_invalido'
        elif not lancamentos:
            erro = 'Nenhum lancamento rateado foi encontrado para este grupo.'
            erro_codigo = 'grupo_nao_encontrado'
        elif len(lancamentos) < 2:
            erro = 'Este grupo nao possui linhas suficientes para edicao coordenada.'
            erro_codigo = 'grupo_insuficiente'
        else:
            numeros_documento = {(lancamento.numero_documento or '').strip() for lancamento in lancamentos}
            numeros_documento.discard('')
            if len(numeros_documento) > 1:
                erro = 'Este grupo possui numeros de documento divergentes e precisa de regularizacao antes da edicao coordenada.'
                erro_codigo = 'documento_divergente'

        self._grupo_info_cache = {
            'grupo_rateio': grupo_rateio,
            'lancamentos': lancamentos,
            'erro': erro,
            'erro_codigo': erro_codigo,
            'representante': lancamentos[0] if lancamentos else None,
        }
        return self._grupo_info_cache

    def _get_grupo_lancamentos(self) -> list[LancamentoFinanceiro]:
        return self._get_grupo_info()['lancamentos']

    def dispatch(self, request, *args, **kwargs):
        grupo_info = self._get_grupo_info()
        if grupo_info['erro']:
            erro_codigo = grupo_info.get('erro_codigo') or 'grupo_invalido'
            messages.warning(
                request,
                f"{grupo_info['erro']} O fluxo coordenado nao foi aberto para evitar alteracao insegura do grupo. Revise este caso pela edicao individual da linha representativa.",
            )
            representante = grupo_info['representante']
            if representante:
                query_string = urlencode(
                    {
                        'origem_fluxo': 'rateio_coordenado',
                        'motivo_fluxo': erro_codigo,
                    }
                )
                return redirect(f"{reverse('financeiro:lancamento-update', kwargs={'pk': representante.pk})}?{query_string}")
            messages.warning(
                request,
                'Nao foi possivel abrir uma linha representativa para este grupo. Voce foi redirecionado para a listagem principal de lancamentos.',
            )
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self._get_grupo_lancamentos()[0]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['grupo_lancamentos'] = self._get_grupo_lancamentos()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grupo_lancamentos = self._get_grupo_lancamentos()
        context['rateio_categoria_opcoes'] = [
            {'id': categoria.pk, 'label': str(categoria)}
            for categoria in CategoriaFinanceira.objects.order_by('tipo', 'nome')
        ]
        context['grupo_rateio'] = grupo_lancamentos[0].grupo_rateio
        context['grupo_rateio_quantidade_linhas'] = len(grupo_lancamentos)
        context['grupo_rateio_valor_total'] = sum(
            (lancamento.valor for lancamento in grupo_lancamentos),
            Decimal('0.00'),
        )
        context['grupo_rateio_linha_representativa'] = grupo_lancamentos[0]
        return context

    def form_valid(self, form):
        grupo_lancamentos = self._get_grupo_lancamentos()
        rateio_linhas = form.cleaned_data.get('rateio_linhas') or []
        dados_comuns = {
            'descricao': form.cleaned_data['descricao'],
            'tipo': form.cleaned_data['tipo'],
            'status': form.cleaned_data['status'],
            'data_competencia': form.cleaned_data['data_competencia'],
            'data_pagamento': form.cleaned_data.get('data_pagamento'),
            'numero_documento': (form.cleaned_data.get('numero_documento') or '').strip(),
            'pessoa': form.cleaned_data.get('pessoa'),
            'centro_custo': form.cleaned_data.get('centro_custo'),
            'conta': form.cleaned_data['conta'],
            'conta_destino': form.cleaned_data.get('conta_destino'),
            'observacoes': form.cleaned_data.get('observacoes', ''),
            'com_rateio': True,
            'grupo_rateio': grupo_lancamentos[0].grupo_rateio,
        }

        existentes_por_id = {lancamento.pk: lancamento for lancamento in grupo_lancamentos}
        ids_utilizados: set[int] = set()
        lancamentos_finais: list[LancamentoFinanceiro] = []

        for linha in rateio_linhas:
            linha_id = linha.get('id')
            if linha_id and int(linha_id) not in existentes_por_id:
                form.add_error('rateio_payload', 'Foi informada uma linha que nao pertence a este grupo de rateio.')
                return self.form_invalid(form)

        with transaction.atomic():
            for linha in rateio_linhas:
                linha_id = linha.get('id')
                if linha_id:
                    lancamento = existentes_por_id.get(int(linha_id))
                    ids_utilizados.add(lancamento.pk)
                    antes = _snapshot_lancamento(lancamento)
                    for campo, valor in dados_comuns.items():
                        setattr(lancamento, campo, valor)
                    lancamento.categoria = linha['categoria']
                    lancamento.valor = linha['valor']
                    lancamento.save()
                    depois = _snapshot_lancamento(lancamento)
                    if antes != depois:
                        _registrar_auditoria_lancamento(
                            request=self.request,
                            acao=AuditoriaFinanceiro.AcaoAuditoria.UPDATE,
                            lancamento=lancamento,
                            antes=antes,
                            depois=depois,
                        )
                    lancamentos_finais.append(lancamento)
                    continue

                lancamento = LancamentoFinanceiro.objects.create(
                    **dados_comuns,
                    categoria=linha['categoria'],
                    valor=linha['valor'],
                )
                _registrar_auditoria_lancamento(
                    request=self.request,
                    acao=AuditoriaFinanceiro.AcaoAuditoria.CREATE,
                    lancamento=lancamento,
                    depois=_snapshot_lancamento(lancamento),
                )
                lancamentos_finais.append(lancamento)

            for lancamento in grupo_lancamentos:
                if lancamento.pk in ids_utilizados:
                    continue
                antes = _snapshot_lancamento(lancamento)
                registro_id = lancamento.pk
                lancamento.delete()
                AuditoriaFinanceiro.objects.create(
                    acao=AuditoriaFinanceiro.AcaoAuditoria.DELETE,
                    modelo='LancamentoFinanceiro',
                    registro_id=registro_id,
                    usuario=_auditoria_usuario(self.request),
                    campos_alterados=_build_auditoria_payload(antes, None),
                )

        self.object = lancamentos_finais[0]
        messages.success(
            self.request,
            f'Grupo de rateio atualizado com sucesso em {len(lancamentos_finais)} linhas. Voce voltou para a listagem principal de lancamentos.',
        )
        query_string = urlencode(
            {
                'origem_fluxo': 'rateio_coordenado_salvo',
                'grupo_rateio': grupo_lancamentos[0].grupo_rateio,
            }
        )
        return redirect(f"{reverse('financeiro:lancamento-list')}?{query_string}")


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
        mensagem_categoria = ''
        assinatura_padrao = AssinaturaInstitucional.objects.filter(ativo=True, padrao=True).first()
        configuracao_padrao = ConfiguracaoInstitucional.objects.filter(ativo=True, padrao=True).first()
        if self.object.categoria:
            mensagem_categoria = (self.object.categoria.mensagem_recibo or '').strip()
        context['page_title'] = f'Recibo do Lancamento {self.object.pk}'
        context['recibo_pessoa_nome'] = self.object.pessoa.nome if self.object.pessoa else '-'
        context['recibo_referente'] = self.object.descricao
        context['recibo_data_principal'] = data_recibo
        context['recibo_data_humana'] = _data_documental_por_extenso(data_recibo)
        context['recibo_valor_extenso'] = _valor_por_extenso(self.object.valor)
        context['recibo_data_fallback'] = self.object.data_pagamento is None
        context['recibo_mensagem_final'] = (
            mensagem_categoria
            or (
                (configuracao_padrao.mensagem_padrao_recibo or '').strip()
                if configuracao_padrao
                else ''
            )
            or 'Recibo emitido com base no lancamento registrado no sistema.'
        )
        context['recibo_mensagem_personalizada'] = bool(mensagem_categoria)
        context['recibo_assinatura_padrao'] = assinatura_padrao
        context['recibo_configuracao_institucional'] = configuracao_padrao
        context['recibo_nome_instituicao'] = (
            (configuracao_padrao.nome_instituicao or '').strip() if configuracao_padrao else ''
        )
        context['recibo_logo_url'] = (configuracao_padrao.logo_url or '').strip() if configuracao_padrao else ''
        context['recibo_cidade'] = (configuracao_padrao.cidade or '').strip() if configuracao_padrao else ''
        return context


class LancamentoFinanceiroDeleteView(FinanceiroDeleteMixin):
    model = LancamentoFinanceiro
    success_url = reverse_lazy('financeiro:lancamento-list')
    page_title = 'Excluir Lancamento Financeiro'
    cancel_url = reverse_lazy('financeiro:lancamento-list')
    success_message = 'Lancamento financeiro excluido com sucesso.'

    def form_valid(self, form):
        lancamento = self.object
        antes = _snapshot_lancamento(lancamento)
        registro_id = lancamento.pk

        with transaction.atomic():
            response = super().form_valid(form)
            AuditoriaFinanceiro.objects.create(
                acao=AuditoriaFinanceiro.AcaoAuditoria.DELETE,
                modelo='LancamentoFinanceiro',
                registro_id=registro_id,
                usuario=_auditoria_usuario(self.request),
                campos_alterados=_build_auditoria_payload(antes, None),
            )

        return response
