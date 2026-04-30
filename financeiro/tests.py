import json
from datetime import date
from decimal import Decimal

from django.template.loader import get_template, render_to_string
from django.http import QueryDict
from django.test import RequestFactory, TestCase
from django.urls import resolve, reverse

from .forms import ContaFinanceiraForm, LancamentoFinanceiroForm, PessoaFinanceiraForm
from .models import (
    AssinaturaInstitucional,
    CategoriaFinanceira,
    ContaFinanceira,
    LancamentoFinanceiro,
    PessoaFinanceira,
)
from .views import (
    BalanceteInstitucionalFinanceiroView,
    ContaFinanceiraAutocompleteView,
    ExtratoFinanceiroView,
    LancamentoFinanceiroCloneView,
    PrestacaoContasFinanceiroView,
    _filtrar_lancamentos_por_parametros,
    montar_contexto_fechamento_periodo,
)


class ContaFinanceiraEdicaoFormTests(TestCase):
    def test_form_edicao_carrega_saldo_inicial_e_data_html(self):
        conta = ContaFinanceira.objects.create(
            nome='Conta teste',
            saldo_inicial=Decimal('1234.56'),
            data_saldo_inicial=date(2026, 3, 15),
        )

        form = ContaFinanceiraForm(instance=conta)

        self.assertEqual(str(form['saldo_inicial'].value()), '1234.56')
        self.assertIn('value="2026-03-15"', form['data_saldo_inicial'].as_widget())

    def test_form_edicao_permite_atualizar_saldo_inicial_e_data(self):
        conta = ContaFinanceira.objects.create(
            nome='Conta teste',
            saldo_inicial=Decimal('1234.56'),
            data_saldo_inicial=date(2026, 3, 15),
        )

        form = ContaFinanceiraForm(
            data={
                'nome': 'Conta teste atualizada',
                'descricao': '',
                'saldo_inicial': '987.65',
                'data_saldo_inicial': '2026-04-20',
                'ativa': 'on',
            },
            instance=conta,
        )

        self.assertTrue(form.is_valid(), form.errors)
        conta_atualizada = form.save()
        self.assertEqual(conta_atualizada.saldo_inicial, Decimal('987.65'))
        self.assertEqual(conta_atualizada.data_saldo_inicial, date(2026, 4, 20))


class LancamentoContaInativaTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.conta_ativa = ContaFinanceira.objects.create(
            nome='Conta ativa',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
            ativa=True,
        )
        self.conta_destino_ativa = ContaFinanceira.objects.create(
            nome='Conta destino ativa',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
            ativa=True,
        )
        self.conta_inativa = ContaFinanceira.objects.create(
            nome='Conta inativa',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
            ativa=False,
        )
        self.pessoa = PessoaFinanceira.objects.create(codigo='P001', nome='Favorecido teste')
        self.categoria_pai = CategoriaFinanceira.objects.create(
            nome='Receitas',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
        )
        self.categoria = CategoriaFinanceira.objects.create(
            nome='Doacoes',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
            categoria_pai=self.categoria_pai,
        )

    def _dados_receita(self, conta):
        return {
            'descricao': 'Receita teste',
            'tipo': LancamentoFinanceiro.TipoLancamento.RECEITA,
            'status': LancamentoFinanceiro.StatusLancamento.QUITADO,
            'valor': '50.00',
            'data_competencia': '2026-03-01',
            'data_pagamento': '2026-03-01',
            'numero_documento': '',
            'pessoa': str(self.pessoa.pk),
            'categoria': str(self.categoria.pk),
            'centro_custo': '',
            'conta': str(conta.pk),
            'conta_destino': '',
            'observacoes': '',
            'lancamento_com_rateio': '',
            'salvar_como_regra_automatica': '',
            'valor_total_documento': '',
            'rateio_payload': '',
        }

    def test_novo_lancamento_nao_permite_conta_inativa(self):
        form = LancamentoFinanceiroForm(data=self._dados_receita(self.conta_inativa))

        self.assertFalse(form.is_valid())
        self.assertIn('conta', form.errors)

    def test_novo_lancamento_com_rateio_nao_permite_conta_inativa(self):
        dados = self._dados_receita(self.conta_inativa)
        dados.update(
            {
                'lancamento_com_rateio': 'on',
                'valor': '',
                'valor_total_documento': '50.00',
                'rateio_payload': json.dumps([
                    {'categoria': str(self.categoria.pk), 'valor': '30.00'},
                    {'categoria': str(self.categoria.pk), 'valor': '20.00'},
                ]),
            }
        )

        form = LancamentoFinanceiroForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn('conta', form.errors)

    def test_transferencia_nova_nao_permite_conta_destino_inativa(self):
        dados = self._dados_receita(self.conta_ativa)
        dados.update(
            {
                'tipo': LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA,
                'pessoa': '',
                'categoria': '',
                'conta_destino': str(self.conta_inativa.pk),
            }
        )

        form = LancamentoFinanceiroForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn('conta_destino', form.errors)

    def test_edicao_preserva_conta_inativa_ja_vinculada(self):
        lancamento = LancamentoFinanceiro.objects.create(
            descricao='Receita antiga',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('50.00'),
            data_competencia=date(2026, 3, 1),
            data_pagamento=date(2026, 3, 1),
            pessoa=self.pessoa,
            categoria=self.categoria,
            conta=self.conta_inativa,
        )
        dados = self._dados_receita(self.conta_inativa)
        dados['descricao'] = 'Receita antiga ajustada'
        dados['numero_documento'] = lancamento.numero_documento

        form = LancamentoFinanceiroForm(data=dados, instance=lancamento)

        self.assertTrue(form.is_valid(), form.errors)

    def test_clone_nao_reaproveita_conta_inativa_automaticamente(self):
        lancamento = LancamentoFinanceiro.objects.create(
            descricao='Receita antiga',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('50.00'),
            data_competencia=date(2026, 3, 1),
            data_pagamento=date(2026, 3, 1),
            pessoa=self.pessoa,
            categoria=self.categoria,
            conta=self.conta_inativa,
        )
        view = LancamentoFinanceiroCloneView()
        view.lancamento_origem = lancamento

        initial = view.get_initial()

        self.assertNotIn('conta', initial)

    def test_autocomplete_contas_nao_retorna_inativas(self):
        request = self.factory.get('/financeiro/autocomplete/contas/', {'q': 'Conta'})
        view = ContaFinanceiraAutocompleteView()
        view.request = request

        response = view.get(request)
        payload = json.loads(response.content)
        labels = [item['label'] for item in payload['results']]

        self.assertIn('Conta ativa', labels)
        self.assertIn('Conta destino ativa', labels)
        self.assertNotIn('Conta inativa', labels)

    def test_filtros_historicos_mostram_inativa_apenas_com_movimento_no_periodo(self):
        conta_inativa_sem_movimento = ContaFinanceira.objects.create(
            nome='Conta inativa sem movimento',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
            ativa=False,
        )
        conta_inativa_fora_periodo = ContaFinanceira.objects.create(
            nome='Conta inativa fora do periodo',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
            ativa=False,
        )
        LancamentoFinanceiro.objects.create(
            descricao='Movimento inativo no periodo',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('80.00'),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            pessoa=self.pessoa,
            categoria=self.categoria,
            conta=self.conta_inativa,
        )
        LancamentoFinanceiro.objects.create(
            descricao='Movimento inativo fora do periodo',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('90.00'),
            data_competencia=date(2026, 2, 10),
            data_pagamento=date(2026, 2, 10),
            pessoa=self.pessoa,
            categoria=self.categoria,
            conta=conta_inativa_fora_periodo,
        )

        request = self.factory.get(
            '/financeiro/prestacao-contas/',
            data=[
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.conta_inativa.pk)),
            ],
        )
        view = PrestacaoContasFinanceiroView()
        view.request = request

        contexto = view._build_periodo_context()
        nomes = [conta.nome for conta in contexto['contas_disponiveis']]

        self.assertIn('Conta ativa', nomes)
        self.assertIn('Conta inativa', nomes)
        self.assertNotIn(conta_inativa_sem_movimento.nome, nomes)
        self.assertNotIn(conta_inativa_fora_periodo.nome, nomes)
        self.assertIn(str(self.conta_inativa.pk), contexto['contas_selecionadas_ids'])


class PrestacaoContasTransferenciasEscopoTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.dinheiro = ContaFinanceira.objects.create(
            nome='Dinheiro',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
        )
        self.banco = ContaFinanceira.objects.create(
            nome='Banco',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
        )
        self.caixa_externo = ContaFinanceira.objects.create(
            nome='Caixa externo',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
        )

        self._criar_transferencia('Dinheiro para banco', self.dinheiro, self.banco, '100.00')
        self._criar_transferencia('Dinheiro para caixa externo', self.dinheiro, self.caixa_externo, '30.00')
        self._criar_transferencia('Caixa externo para dinheiro', self.caixa_externo, self.dinheiro, '70.00')

    def _criar_transferencia(self, descricao, conta_origem, conta_destino, valor):
        return LancamentoFinanceiro.objects.create(
            descricao=descricao,
            tipo=LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal(valor),
            data_competencia=date(2026, 2, 28),
            data_pagamento=date(2026, 3, 5),
            conta=conta_origem,
            conta_destino=conta_destino,
        )

    def _contexto(self, contas, exibir_transferencias=False):
        params = [
            ('data_inicial', '2026-03-01'),
            ('data_final', '2026-03-31'),
        ]
        params.extend(('contas', str(conta.id)) for conta in contas)
        if exibir_transferencias:
            params.append(('exibir_transferencias', '1'))
        request = self.factory.get('/financeiro/prestacao-contas/', data=params)
        view = PrestacaoContasFinanceiroView()
        view.request = request
        return view._build_periodo_context()

    def _render_balancete(self, request, contexto):
        request.resolver_match = resolve('/financeiro/balancete-institucional/')
        return render_to_string('financeiro/balancete_institucional.html', contexto, request=request)

    def _documento_balancete_html(self, html):
        return html.split('<article class="balancete-document balancete-documento">', 1)[1]

    def test_transferencias_compõem_saldo_por_escopo_sem_inflar_resultado(self):
        contexto_dinheiro_fechado = self._contexto([self.dinheiro])
        contexto_dinheiro_aberto = self._contexto([self.dinheiro], exibir_transferencias=True)
        contexto_dinheiro_banco = self._contexto([self.dinheiro, self.banco], exibir_transferencias=True)
        contexto_todas = self._contexto([self.dinheiro, self.banco, self.caixa_externo], exibir_transferencias=True)

        self.assertEqual(contexto_dinheiro_fechado['total_receitas_periodo'], Decimal('0.00'))
        self.assertEqual(contexto_dinheiro_fechado['total_despesas_periodo'], Decimal('0.00'))
        self.assertEqual(contexto_dinheiro_fechado['total_entradas_outras_contas'], Decimal('70.00'))
        self.assertEqual(contexto_dinheiro_fechado['total_saidas_outras_contas'], Decimal('130.00'))
        self.assertEqual(contexto_dinheiro_fechado['saldo_inicial_consolidado'], Decimal('0.00'))
        self.assertEqual(contexto_dinheiro_fechado['saldo_final_consolidado'], Decimal('-60.00'))
        self.assertEqual(contexto_dinheiro_fechado['saldo_final_reconciliado'], Decimal('-60.00'))
        self.assertTrue(contexto_dinheiro_fechado['reconciliacao_saldo_consistente'])
        self.assertEqual(contexto_dinheiro_fechado['transferencias_periodo'], [])

        self.assertEqual(contexto_dinheiro_aberto['saldo_final_consolidado'], contexto_dinheiro_fechado['saldo_final_consolidado'])
        self.assertEqual(contexto_dinheiro_aberto['saldo_final_reconciliado'], contexto_dinheiro_fechado['saldo_final_reconciliado'])
        self.assertEqual(len(contexto_dinheiro_aberto['transferencias_periodo']), 3)
        self.assertEqual(contexto_dinheiro_aberto['total_transferencias_entrada'], Decimal('70.00'))
        self.assertEqual(contexto_dinheiro_aberto['total_transferencias_saida'], Decimal('130.00'))

        self.assertEqual(contexto_dinheiro_banco['total_entradas_outras_contas'], Decimal('70.00'))
        self.assertEqual(contexto_dinheiro_banco['total_saidas_outras_contas'], Decimal('30.00'))
        self.assertEqual(contexto_dinheiro_banco['saldo_final_consolidado'], Decimal('40.00'))
        self.assertEqual(contexto_dinheiro_banco['saldo_final_reconciliado'], Decimal('40.00'))
        self.assertEqual(len(contexto_dinheiro_banco['transferencias_periodo']), 2)

        self.assertEqual(contexto_todas['total_entradas_outras_contas'], Decimal('0.00'))
        self.assertEqual(contexto_todas['total_saidas_outras_contas'], Decimal('0.00'))
        self.assertEqual(contexto_todas['saldo_final_consolidado'], Decimal('0.00'))
        self.assertEqual(contexto_todas['saldo_final_reconciliado'], Decimal('0.00'))
        self.assertEqual(contexto_todas['transferencias_periodo'], [])

    def test_base_comum_de_calculo_fechamento_reconcilia_saldo(self):
        request = self.factory.get(
            '/financeiro/prestacao-contas/',
            data=[
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
            ],
        )
        view = PrestacaoContasFinanceiroView()
        view.request = request

        contexto = montar_contexto_fechamento_periodo(view)

        self.assertEqual(contexto['saldo_final_consolidado'], Decimal('-60.00'))
        self.assertEqual(contexto['saldo_final_reconciliado'], Decimal('-60.00'))
        self.assertTrue(contexto['reconciliacao_saldo_consistente'])

    def test_url_balancete_institucional_resolve_para_view_propria(self):
        url = reverse('financeiro:balancete-institucional')

        resolved = resolve(url)

        self.assertEqual(url, '/financeiro/balancete-institucional/')
        self.assertIs(resolved.func.view_class, BalanceteInstitucionalFinanceiroView)
        self.assertIsNotNone(get_template('financeiro/balancete_institucional.html'))

    def test_balancete_institucional_reaproveita_contexto_do_fechamento(self):
        assinatura_1 = AssinaturaInstitucional.objects.create(
            nome='Assinatura A',
            assinatura_texto='Pessoa A',
            cargo='Tesouraria',
            ativo=True,
            padrao=True,
        )
        assinatura_2 = AssinaturaInstitucional.objects.create(
            nome='Assinatura B',
            assinatura_texto='Pessoa B',
            cargo='Diretoria',
            ativo=True,
        )
        request = self.factory.get(
            '/financeiro/balancete-institucional/',
            data=[
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('assinatura_1', str(assinatura_1.pk)),
                ('assinatura_2', str(assinatura_2.pk)),
            ],
        )
        view = BalanceteInstitucionalFinanceiroView()
        view.request = request

        contexto = view.get_context_data()

        self.assertEqual(contexto['page_title'], 'Balancete Institucional')
        self.assertEqual(contexto['saldo_final_consolidado'], Decimal('-60.00'))
        self.assertEqual(contexto['saldo_final_reconciliado'], Decimal('-60.00'))
        self.assertTrue(contexto['reconciliacao_saldo_consistente'])
        self.assertEqual(contexto['assinatura_1'], assinatura_1)
        self.assertEqual(contexto['assinatura_2'], assinatura_2)

    def test_balancete_institucional_nao_usa_assinaturas_reais_sem_selecao(self):
        assinatura_padrao = AssinaturaInstitucional.objects.create(
            nome='Assinatura Padrao',
            assinatura_texto='Pessoa Padrao',
            cargo='Tesouraria',
            ativo=True,
            padrao=True,
        )
        assinatura_secundaria = AssinaturaInstitucional.objects.create(
            nome='Assinatura Secundaria',
            assinatura_texto='Pessoa Secundaria',
            cargo='Presidencia',
            ativo=True,
        )
        request = self.factory.get(
            '/financeiro/balancete-institucional/',
            data=[
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
            ],
        )
        view = BalanceteInstitucionalFinanceiroView()
        view.request = request

        contexto = view.get_context_data()

        self.assertIsNone(contexto['assinatura_1'])
        self.assertIsNone(contexto['assinatura_2'])
        self.assertEqual(contexto['assinatura_1_id'], '')
        self.assertEqual(contexto['assinatura_2_id'], '')
        html = self._render_balancete(request, contexto)
        documento_html = self._documento_balancete_html(html)
        self.assertNotIn('6. ASSINATURAS', documento_html)
        self.assertNotIn('Assinatura Padrao', documento_html)
        self.assertNotIn('Assinatura Secundaria', documento_html)
        self.assertNotIn('Responsavel financeiro', documento_html)
        self.assertNotIn('Responsavel institucional', documento_html)

    def test_balancete_institucional_exibe_apenas_assinatura_selecionada(self):
        assinatura_unica = AssinaturaInstitucional.objects.create(
            nome='Assinatura Unica',
            assinatura_texto='Pessoa Unica',
            cargo='Tesouraria',
            ativo=True,
        )
        request = self.factory.get(
            '/financeiro/balancete-institucional/',
            data=[
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('assinatura_1', str(assinatura_unica.pk)),
            ],
        )
        view = BalanceteInstitucionalFinanceiroView()
        view.request = request

        contexto = view.get_context_data()

        self.assertEqual(contexto['assinatura_1'], assinatura_unica)
        self.assertIsNone(contexto['assinatura_2'])
        html = self._render_balancete(request, contexto)
        self.assertIn('6. ASSINATURAS', html)
        self.assertIn('Pessoa Unica', html)
        self.assertNotIn('Responsavel institucional', html)

    def test_balancete_institucional_exibe_apenas_assinatura_2_selecionada(self):
        assinatura_1 = AssinaturaInstitucional.objects.create(
            nome='Assinatura Um',
            assinatura_texto='Pessoa Um',
            cargo='Tesouraria',
            ativo=True,
        )
        assinatura_2 = AssinaturaInstitucional.objects.create(
            nome='Assinatura Dois',
            assinatura_texto='Pessoa Dois',
            cargo='Presidencia',
            ativo=True,
        )
        request = self.factory.get(
            '/financeiro/balancete-institucional/',
            data=[
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('assinatura_2', str(assinatura_2.pk)),
            ],
        )
        view = BalanceteInstitucionalFinanceiroView()
        view.request = request

        contexto = view.get_context_data()

        self.assertIsNone(contexto['assinatura_1'])
        self.assertEqual(contexto['assinatura_2'], assinatura_2)
        html = self._render_balancete(request, contexto)
        self.assertIn('Pessoa Dois', html)
        self.assertNotIn('Pessoa Um', html)

    def test_balancete_institucional_exibe_duas_assinaturas_selecionadas(self):
        assinatura_1 = AssinaturaInstitucional.objects.create(
            nome='Assinatura Um',
            assinatura_texto='Pessoa Um',
            cargo='Tesouraria',
            ativo=True,
        )
        assinatura_2 = AssinaturaInstitucional.objects.create(
            nome='Assinatura Dois',
            assinatura_texto='Pessoa Dois',
            cargo='Presidencia',
            ativo=True,
        )
        request = self.factory.get(
            '/financeiro/balancete-institucional/',
            data=[
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('assinatura_1', str(assinatura_1.pk)),
                ('assinatura_2', str(assinatura_2.pk)),
            ],
        )
        view = BalanceteInstitucionalFinanceiroView()
        view.request = request

        contexto = view.get_context_data()

        html = self._render_balancete(request, contexto)
        self.assertIn('Pessoa Um', html)
        self.assertIn('Pessoa Dois', html)

    def test_balancete_institucional_oculta_contas_zeradas_por_padrao(self):
        request = self.factory.get(
            '/financeiro/balancete-institucional/',
            data=[
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
            ],
        )
        view = BalanceteInstitucionalFinanceiroView()
        view.request = request

        contexto = view.get_context_data()

        self.assertEqual(contexto['saldo_inicial_consolidado'], Decimal('0.00'))
        self.assertEqual(contexto['balancete_composicao_inicial'], [])
        self.assertEqual(
            [item['conta'] for item in contexto['balancete_composicao_final']],
            [self.dinheiro],
        )
        self.assertEqual(contexto['balancete_abrangencia_label'], 'Dinheiro')

    def test_balancete_institucional_exibe_contas_zeradas_quando_opcao_ativa(self):
        request = self.factory.get(
            '/financeiro/balancete-institucional/',
            data=[
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('mostrar_contas_zeradas', '1'),
            ],
        )
        view = BalanceteInstitucionalFinanceiroView()
        view.request = request

        contexto = view.get_context_data()

        self.assertEqual(
            [item['conta'] for item in contexto['balancete_composicao_inicial']],
            [self.dinheiro],
        )

    def test_balancete_institucional_resume_abrangencia_de_multiplas_contas(self):
        request = self.factory.get(
            '/financeiro/balancete-institucional/',
            data=[
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('contas', str(self.banco.id)),
            ],
        )
        view = BalanceteInstitucionalFinanceiroView()
        view.request = request

        contexto = view.get_context_data()

        self.assertEqual(contexto['balancete_abrangencia_label'], 'Contas selecionadas')
        self.assertIn('Dinheiro', contexto['balancete_contas_label_completo'])
        self.assertIn('Banco', contexto['balancete_contas_label_completo'])


class ExtratoFinanceiroMultiplasContasTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.dinheiro = ContaFinanceira.objects.create(
            nome='Dinheiro',
            saldo_inicial=Decimal('100.00'),
            data_saldo_inicial=date(2026, 1, 1),
        )
        self.banco = ContaFinanceira.objects.create(
            nome='Banco',
            saldo_inicial=Decimal('50.00'),
            data_saldo_inicial=date(2026, 1, 1),
        )
        self.caixa_externo = ContaFinanceira.objects.create(
            nome='Caixa externo',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
        )

        self._criar_transferencia(
            'Banco para dinheiro antes do periodo',
            self.banco,
            self.dinheiro,
            '40.00',
            date(2026, 2, 20),
        )
        self._criar_transferencia('Dinheiro para banco', self.dinheiro, self.banco, '30.00', date(2026, 3, 5))
        self._criar_transferencia(
            'Dinheiro para caixa externo',
            self.dinheiro,
            self.caixa_externo,
            '20.00',
            date(2026, 3, 6),
        )
        self._criar_transferencia(
            'Caixa externo para dinheiro',
            self.caixa_externo,
            self.dinheiro,
            '70.00',
            date(2026, 3, 7),
        )

    def _criar_transferencia(self, descricao, conta_origem, conta_destino, valor, data_pagamento):
        return LancamentoFinanceiro.objects.create(
            descricao=descricao,
            tipo=LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal(valor),
            data_competencia=data_pagamento,
            data_pagamento=data_pagamento,
            conta=conta_origem,
            conta_destino=conta_destino,
        )

    def _contexto(self, params):
        request = self.factory.get('/financeiro/extratos/', data=params)
        view = ExtratoFinanceiroView()
        view.request = request
        return view.get_context_data()

    def test_extrato_respeita_escopo_de_contas(self):
        periodo = {
            'data_inicial': '2026-03-01',
            'data_final': '2026-03-31',
        }
        contexto_uma_conta = self._contexto(
            {
                **periodo,
                'conta': str(self.dinheiro.id),
            }
        )
        contexto_duas_contas = self._contexto(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('contas', str(self.banco.id)),
            ]
        )
        contexto_todas = self._contexto(
            {
                **periodo,
                'todas_contas': '1',
            }
        )
        contexto_todas_com_parcial = self._contexto(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('todas_contas', '1'),
                ('contas', str(self.dinheiro.id)),
            ]
        )
        contexto_sem_contas = self._contexto(
            {
                **periodo,
                'contas_form': '1',
            }
        )

        self.assertEqual(contexto_uma_conta['saldo_anterior'], Decimal('140.00'))
        self.assertEqual(contexto_uma_conta['total_entradas_periodo'], Decimal('70.00'))
        self.assertEqual(contexto_uma_conta['total_saidas_periodo'], Decimal('50.00'))
        self.assertEqual(contexto_uma_conta['saldo_final'], Decimal('160.00'))
        self.assertFalse(contexto_uma_conta['extrato_multiplas_contas'])

        self.assertEqual(contexto_duas_contas['saldo_anterior'], Decimal('150.00'))
        self.assertEqual(contexto_duas_contas['total_entradas_periodo'], Decimal('70.00'))
        self.assertEqual(contexto_duas_contas['total_saidas_periodo'], Decimal('20.00'))
        self.assertEqual(contexto_duas_contas['saldo_final'], Decimal('200.00'))
        self.assertTrue(contexto_duas_contas['extrato_multiplas_contas'])
        self.assertEqual(len(contexto_duas_contas['itens_extrato']), 2)
        self.assertEqual(
            [item['lancamento'].descricao for item in contexto_duas_contas['itens_extrato']],
            ['Dinheiro para caixa externo', 'Caixa externo para dinheiro'],
        )
        self.assertTrue(all(item['conta_exibicao'] for item in contexto_duas_contas['itens_extrato']))
        self.assertEqual(
            [item['favorecido_exibicao'] for item in contexto_duas_contas['itens_extrato']],
            ['TRANSFERÊNCIA ENTRE CONTAS', 'TRANSFERÊNCIA ENTRE CONTAS'],
        )

        self.assertEqual(contexto_todas['saldo_anterior'], Decimal('150.00'))
        self.assertEqual(contexto_todas['total_entradas_periodo'], Decimal('0.00'))
        self.assertEqual(contexto_todas['total_saidas_periodo'], Decimal('0.00'))
        self.assertEqual(contexto_todas['saldo_final'], Decimal('150.00'))
        self.assertTrue(contexto_todas['extrato_todas_contas'])
        self.assertEqual(contexto_todas['itens_extrato'], [])

        self.assertFalse(contexto_todas_com_parcial['todas_contas_selecionadas'])
        self.assertEqual(contexto_todas_com_parcial['contas_selecionadas_ids'], [str(self.dinheiro.id)])
        self.assertEqual(contexto_todas_com_parcial['saldo_final'], Decimal('160.00'))

        self.assertEqual(
            contexto_sem_contas['extrato_error'],
            'Selecione pelo menos uma conta para carregar o extrato.',
        )
        self.assertFalse(contexto_sem_contas['tem_extrato'])


class LancamentoListMultiContasTests(TestCase):
    def setUp(self):
        self.conta_a = ContaFinanceira.objects.create(
            nome='Conta A',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
        )
        self.conta_b = ContaFinanceira.objects.create(
            nome='Conta B',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
        )
        self.conta_c = ContaFinanceira.objects.create(
            nome='Conta C',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
        )
        self.pessoa = PessoaFinanceira.objects.create(codigo='P100', nome='Favorecido multi-conta')
        categoria_pai = CategoriaFinanceira.objects.create(
            nome='Receitas multi',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
        )
        self.categoria = CategoriaFinanceira.objects.create(
            nome='Doacoes multi',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
            categoria_pai=categoria_pai,
        )
        self.receita_a = self._criar_receita('Receita conta A', self.conta_a, '10.00')
        self.receita_b = self._criar_receita('Receita conta B', self.conta_b, '20.00')
        self.receita_c = self._criar_receita('Receita conta C', self.conta_c, '30.00')
        self.transferencia_a_c = self._criar_transferencia('Transferencia A para C', self.conta_a, self.conta_c)
        self.transferencia_c_b = self._criar_transferencia('Transferencia C para B', self.conta_c, self.conta_b)
        self.transferencia_a_b = self._criar_transferencia('Transferencia A para B', self.conta_a, self.conta_b)

    def _criar_receita(self, descricao, conta, valor, status=LancamentoFinanceiro.StatusLancamento.QUITADO):
        return LancamentoFinanceiro.objects.create(
            descricao=descricao,
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=status,
            valor=Decimal(valor),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            pessoa=self.pessoa,
            categoria=self.categoria,
            conta=conta,
        )

    def _criar_transferencia(self, descricao, origem, destino, status=LancamentoFinanceiro.StatusLancamento.QUITADO):
        return LancamentoFinanceiro.objects.create(
            descricao=descricao,
            tipo=LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA,
            status=status,
            valor=Decimal('5.00'),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            conta=origem,
            conta_destino=destino,
        )

    def _filtrar(self, params):
        query = QueryDict('', mutable=True)
        for chave, valor in params:
            query.appendlist(chave, valor)
        queryset = _filtrar_lancamentos_por_parametros(LancamentoFinanceiro.objects.all(), query)
        return set(queryset.values_list('descricao', flat=True))

    def test_filtro_por_uma_conta_considera_origem_e_destino(self):
        descricoes = self._filtrar([('contas', str(self.conta_a.pk))])

        self.assertIn('Receita conta A', descricoes)
        self.assertIn('Transferencia A para C', descricoes)
        self.assertIn('Transferencia A para B', descricoes)
        self.assertNotIn('Receita conta B', descricoes)
        self.assertIn('Transferencia C para B', self._filtrar([('contas', str(self.conta_b.pk))]))

    def test_filtro_por_duas_contas_inclui_transferencia_interna(self):
        descricoes = self._filtrar([
            ('contas', str(self.conta_a.pk)),
            ('contas', str(self.conta_b.pk)),
        ])

        self.assertIn('Receita conta A', descricoes)
        self.assertIn('Receita conta B', descricoes)
        self.assertNotIn('Receita conta C', descricoes)
        self.assertIn('Transferencia A para C', descricoes)
        self.assertIn('Transferencia C para B', descricoes)
        self.assertIn('Transferencia A para B', descricoes)

    def test_filtro_todas_contas_preserva_comportamento_sem_recorte(self):
        descricoes = self._filtrar([('todas_contas', '1')])

        self.assertIn('Receita conta A', descricoes)
        self.assertIn('Receita conta B', descricoes)
        self.assertIn('Receita conta C', descricoes)
        self.assertIn('Transferencia A para B', descricoes)

    def test_filtro_multi_contas_combina_com_demais_filtros(self):
        self._criar_receita('Receita aberta conta A', self.conta_a, '40.00', status=LancamentoFinanceiro.StatusLancamento.ABERTO)

        descricoes = self._filtrar([
            ('contas', str(self.conta_a.pk)),
            ('contas', str(self.conta_b.pk)),
            ('status', LancamentoFinanceiro.StatusLancamento.ABERTO),
        ])

        self.assertEqual(descricoes, {'Receita aberta conta A'})

    def test_parametro_antigo_conta_unica_permanece_compativel(self):
        descricoes = self._filtrar([('conta', str(self.conta_a.pk))])

        self.assertIn('Receita conta A', descricoes)
        self.assertNotIn('Receita conta B', descricoes)


class PessoaFinanceiraDuplicidadeNomeTests(TestCase):
    def _dados_form(self, nome, codigo=''):
        return {
            'codigo': codigo,
            'nome': nome,
            'tipo_pessoa': '',
            'documento': '',
            'telefone': '',
            'email': '',
            'observacoes': '',
            'ativo': 'on',
        }

    def test_bloqueia_cadastro_com_nome_normalizado_duplicado(self):
        PessoaFinanceira.objects.create(codigo='0001', nome='Maria Silva')

        form = PessoaFinanceiraForm(data=self._dados_form(' maria   silva ', codigo='0002'))

        self.assertFalse(form.is_valid())
        self.assertIn('Já existe um favorecido cadastrado com este nome.', form.errors['nome'])

    def test_permite_editar_o_proprio_favorecido_sem_acusar_duplicidade(self):
        pessoa = PessoaFinanceira.objects.create(codigo='0001', nome='Maria Silva')

        form = PessoaFinanceiraForm(
            data=self._dados_form('MARIA   SILVA', codigo='0001'),
            instance=pessoa,
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_bloqueia_edicao_para_nome_de_outro_favorecido(self):
        PessoaFinanceira.objects.create(codigo='0001', nome='Maria Silva')
        outra_pessoa = PessoaFinanceira.objects.create(codigo='0002', nome='Joana Souza')

        form = PessoaFinanceiraForm(
            data=self._dados_form(' maria   silva ', codigo='0002'),
            instance=outra_pessoa,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('Já existe um favorecido cadastrado com este nome.', form.errors['nome'])
