from datetime import date
from decimal import Decimal

from django.test import RequestFactory, TestCase

from .models import ContaFinanceira, LancamentoFinanceiro
from .views import ExtratoFinanceiroView, PrestacaoContasFinanceiroView


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
