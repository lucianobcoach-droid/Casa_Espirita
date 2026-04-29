from datetime import date
from decimal import Decimal

from django.template.loader import get_template, render_to_string
from django.test import RequestFactory, TestCase
from django.urls import resolve, reverse

from .forms import ContaFinanceiraForm, PessoaFinanceiraForm
from .models import AssinaturaInstitucional, ContaFinanceira, LancamentoFinanceiro, PessoaFinanceira
from .views import (
    BalanceteInstitucionalFinanceiroView,
    ExtratoFinanceiroView,
    PrestacaoContasFinanceiroView,
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
