import json
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.loader import get_template, render_to_string
from django.http import QueryDict
from django.test import RequestFactory, TestCase
from django.urls import resolve, reverse

from .forms import (
    CategoriaFinanceiraForm,
    ContaFinanceiraForm,
    LancamentoFinanceiroForm,
    LancamentoFinanceiroGrupoRateioForm,
    PessoaFinanceiraForm,
)
from .models import (
    AlocacaoCompetenciaFinanceira,
    AssinaturaInstitucional,
    CategoriaFinanceira,
    ContaFinanceira,
    LancamentoFinanceiro,
    PessoaFinanceira,
    TipoContaFinanceira,
)
from .views import (
    BalanceteInstitucionalFinanceiroView,
    ContaFinanceiraAutocompleteView,
    ExtratoFinanceiroView,
    _gerar_arquivo_xlsx,
    _linha_exportacao_cadastro_auxiliar,
    LancamentoFinanceiroCloneView,
    LancamentoFinanceiroCreateView,
    LancamentoFinanceiroGrupoRateioCloneView,
    LancamentoFinanceiroGrupoRateioUpdateView,
    PrestacaoContasFinanceiroView,
    _filtrar_lancamentos_por_parametros,
    _validar_conteudo_planilha_importacao_contas_xlsx,
    montar_contexto_fechamento_periodo,
)
from configuracoes.models import PerfilAcesso, PermissaoSistema, UsuarioPerfilAcesso


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


class ContaFinanceiraPatrimonialTests(TestCase):
    def _upload_xlsx(self, linhas):
        arquivo = _gerar_arquivo_xlsx([
            ('Modelo', linhas),
            ('Instrucoes', [['Item', 'Orientacao']]),
        ])
        return SimpleUploadedFile(
            'contas.xlsx',
            arquivo,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    def test_tipos_padrao_estao_disponiveis(self):
        codigos = set(TipoContaFinanceira.objects.values_list('codigo', flat=True))
        nomes_por_codigo = dict(TipoContaFinanceira.objects.values_list('codigo', 'nome'))

        self.assertIn('conta_corrente', codigos)
        self.assertIn('conta_poupanca', codigos)
        self.assertIn('dinheiro_caixa', codigos)
        self.assertIn('aplicacao_financeira', codigos)
        self.assertIn('integralizacao_capital', codigos)
        self.assertIn('conta_vinculada_indisponivel', codigos)
        self.assertIn('outros', codigos)
        self.assertEqual(nomes_por_codigo['aplicacao_financeira'], 'Conta investimento')
        self.assertEqual(nomes_por_codigo['integralizacao_capital'], 'Integralizacao de capital')

    def test_form_permite_conta_indisponivel_com_mensagem(self):
        tipo = TipoContaFinanceira.objects.get(codigo='aplicacao_financeira')
        form = ContaFinanceiraForm(
            data={
                'nome': 'Aplicacao reserva',
                'descricao': '',
                'saldo_inicial': '1000.00',
                'data_saldo_inicial': '2026-01-01',
                'tipo_conta': str(tipo.pk),
                'disponibilidade': ContaFinanceira.DisponibilidadeConta.INDISPONIVEL,
                'mensagem_indisponibilidade': 'Reserva vinculada.',
                'ativa': 'on',
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        conta = form.save()
        self.assertEqual(conta.tipo_conta, tipo)
        self.assertEqual(conta.disponibilidade, ContaFinanceira.DisponibilidadeConta.INDISPONIVEL)
        self.assertEqual(conta.mensagem_indisponibilidade, 'Reserva vinculada.')

    def test_form_usa_outros_e_disponivel_com_mensagem_opcional(self):
        form = ContaFinanceiraForm(
            data={
                'nome': 'Conta operacional',
                'descricao': '',
                'saldo_inicial': '0.00',
                'data_saldo_inicial': '2026-01-01',
                'tipo_conta': '',
                'disponibilidade': ContaFinanceira.DisponibilidadeConta.DISPONIVEL,
                'mensagem_indisponibilidade': '',
                'ativa': 'on',
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        conta = form.save()
        self.assertEqual(conta.tipo_conta.codigo, 'outros')
        self.assertEqual(conta.disponibilidade, ContaFinanceira.DisponibilidadeConta.DISPONIVEL)
        self.assertEqual(conta.mensagem_indisponibilidade, '')

    def test_importacao_contas_ler_campos_patrimoniais(self):
        upload = self._upload_xlsx([
            [
                'nome',
                'descricao',
                'saldo_inicial',
                'data_saldo_inicial',
                'tipo_conta',
                'disponibilidade',
                'mensagem_indisponibilidade',
                'ativa',
            ],
            [
                'Reserva patrimonial',
                '',
                '100,00',
                '01/01/2026',
                'aplicacao_financeira',
                'indisponivel',
                'Valor vinculado.',
                'true',
            ],
        ])

        resultado = _validar_conteudo_planilha_importacao_contas_xlsx(upload)

        self.assertEqual(resultado['linhas_validas'], 1)
        registro = resultado['registros_validos'][0]
        self.assertEqual(registro['tipo_conta'].codigo, 'aplicacao_financeira')
        self.assertEqual(registro['disponibilidade'], ContaFinanceira.DisponibilidadeConta.INDISPONIVEL)
        self.assertEqual(registro['mensagem_indisponibilidade'], 'Valor vinculado.')

    def test_importacao_contas_legada_usa_defaults_patrimoniais(self):
        upload = self._upload_xlsx([
            ['nome', 'descricao', 'saldo_inicial', 'data_saldo_inicial', 'ativa'],
            ['Conta legado', '', '50,00', '01/01/2026', 'true'],
        ])

        resultado = _validar_conteudo_planilha_importacao_contas_xlsx(upload)

        self.assertEqual(resultado['linhas_validas'], 1)
        registro = resultado['registros_validos'][0]
        self.assertEqual(registro['tipo_conta'].codigo, 'outros')
        self.assertEqual(registro['disponibilidade'], ContaFinanceira.DisponibilidadeConta.DISPONIVEL)
        self.assertEqual(registro['mensagem_indisponibilidade'], '')

    def test_exportacao_contas_inclui_campos_patrimoniais(self):
        tipo = TipoContaFinanceira.objects.get(codigo='conta_corrente')
        conta = ContaFinanceira.objects.create(
            nome='Conta exportada',
            saldo_inicial=Decimal('10.00'),
            data_saldo_inicial=date(2026, 1, 1),
            tipo_conta=tipo,
            disponibilidade=ContaFinanceira.DisponibilidadeConta.INDISPONIVEL,
            mensagem_indisponibilidade='Uso vinculado.',
        )
        linha = _linha_exportacao_cadastro_auxiliar('contas', conta)

        self.assertEqual(linha[4], 'conta_corrente')
        self.assertEqual(linha[5], ContaFinanceira.DisponibilidadeConta.INDISPONIVEL)
        self.assertEqual(linha[6], 'Uso vinculado.')


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

    def _contexto_balancete(self, params):
        request = self.factory.get('/financeiro/balancete-institucional/', data=params)
        view = BalanceteInstitucionalFinanceiroView()
        view.request = request
        return request, view.get_context_data()

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
        self.assertNotIn('5. ASSINATURAS', documento_html)
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
                ('composicao_saldo', 'detalhada'),
            ],
        )
        view = BalanceteInstitucionalFinanceiroView()
        view.request = request

        contexto = view.get_context_data()

        self.assertEqual(contexto['balancete_abrangencia_label'], 'Contas selecionadas')
        self.assertIn('Dinheiro', contexto['balancete_contas_label_completo'])
        self.assertIn('Banco', contexto['balancete_contas_label_completo'])

    def test_balancete_institucional_classifica_saldo_final_por_disponibilidade(self):
        self.dinheiro.disponibilidade = ContaFinanceira.DisponibilidadeConta.DISPONIVEL
        self.dinheiro.save(update_fields=['disponibilidade'])
        self.banco.disponibilidade = ContaFinanceira.DisponibilidadeConta.INDISPONIVEL
        self.banco.mensagem_indisponibilidade = 'Saldo vinculado para reserva institucional.'
        self.banco.save(update_fields=['disponibilidade', 'mensagem_indisponibilidade'])
        request = self.factory.get(
            '/financeiro/balancete-institucional/',
            data=[
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('contas', str(self.banco.id)),
                ('formato_balancete', 'financeiro_completo'),
                ('composicao_saldo', 'detalhada'),
            ],
        )
        view = BalanceteInstitucionalFinanceiroView()
        view.request = request

        contexto = view.get_context_data()
        html = self._render_balancete(request, contexto)

        self.assertEqual(
            [item['conta'] for item in contexto['balancete_composicao_disponivel']],
            [self.dinheiro],
        )
        self.assertEqual(
            [item['conta'] for item in contexto['balancete_composicao_indisponivel']],
            [self.banco],
        )
        self.assertEqual(contexto['balancete_subtotal_disponivel'], Decimal('-60.00'))
        self.assertEqual(contexto['balancete_subtotal_indisponivel'], Decimal('100.00'))
        self.assertEqual(contexto['balancete_total_financeiro'], Decimal('40.00'))
        self.assertEqual(contexto['balancete_total_financeiro'], contexto['saldo_final_consolidado'])
        self.assertIn('Saldo disponivel operacional', html)
        self.assertIn('Saldo indisponivel/vinculado', html)
        self.assertIn('Saldo vinculado para reserva institucional.', html)

    def test_balancete_institucional_padrao_usa_composicao_por_tipo(self):
        tipo_caixa = TipoContaFinanceira.objects.get(codigo='dinheiro_caixa')
        tipo_corrente = TipoContaFinanceira.objects.get(codigo='conta_corrente')
        self.dinheiro.tipo_conta = tipo_caixa
        self.dinheiro.saldo_inicial = Decimal('10.00')
        self.dinheiro.save(update_fields=['tipo_conta', 'saldo_inicial'])
        self.banco.tipo_conta = tipo_corrente
        self.banco.disponibilidade = ContaFinanceira.DisponibilidadeConta.INDISPONIVEL
        self.banco.saldo_inicial = Decimal('20.00')
        self.banco.save(update_fields=['tipo_conta', 'disponibilidade', 'saldo_inicial'])

        _, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('contas', str(self.banco.id)),
            ]
        )

        self.assertEqual(contexto['balancete_composicao_saldo'], 'tipo')
        self.assertEqual(contexto['balancete_formato'], 'operacional')
        self.assertFalse(contexto['balancete_exibir_indisponiveis'])
        self.assertEqual(
            [item['rotulo'] for item in contexto['balancete_grupos_apresentacao'][0]['itens']],
            ['Dinheiro/caixa'],
        )
        self.assertEqual(
            [item['rotulo'] for item in contexto['balancete_inicial_grupos_apresentacao'][0]['itens']],
            ['Dinheiro/caixa'],
        )

    def test_balancete_institucional_oculta_indisponiveis_quando_filtro_desligado(self):
        self.banco.disponibilidade = ContaFinanceira.DisponibilidadeConta.INDISPONIVEL
        self.banco.saldo_inicial = Decimal('20.00')
        self.banco.mensagem_indisponibilidade = 'Saldo vinculado para reserva institucional.'
        self.banco.save(update_fields=['disponibilidade', 'saldo_inicial', 'mensagem_indisponibilidade'])
        self.dinheiro.saldo_inicial = Decimal('10.00')
        self.dinheiro.save(update_fields=['saldo_inicial'])

        request, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('contas', str(self.banco.id)),
                ('formato_balancete', 'operacional'),
                ('composicao_saldo', 'total'),
            ]
        )
        html = self._render_balancete(request, contexto)
        documento_html = self._documento_balancete_html(html)

        self.assertEqual(contexto['balancete_composicao_saldo'], 'total')
        self.assertEqual(contexto['balancete_formato'], 'operacional')
        self.assertFalse(contexto['balancete_exibir_indisponiveis'])
        self.assertTrue(contexto['balancete_ocultou_indisponiveis'])
        self.assertFalse(contexto['balancete_exibe_total_financeiro'])
        self.assertEqual(contexto['balancete_total_apresentado_rotulo'], 'Saldo disponivel operacional')
        self.assertTrue(contexto['balancete_inicial_ocultou_indisponiveis'])
        self.assertFalse(contexto['balancete_inicial_exibe_total_financeiro'])
        self.assertEqual(
            contexto['balancete_inicial_total_apresentado_rotulo'],
            'Saldo operacional anterior',
        )
        self.assertTrue(contexto['balancete_modo_saldo_disponivel'])
        self.assertEqual(
            contexto['balancete_transferencias_disponiveis_resumo']['saida_para_indisponivel'],
            Decimal('100.00'),
        )
        self.assertNotIn('Contas vinculadas/indisponiveis nao exibidas nesta composicao.', html)
        self.assertNotIn('Saldo vinculado para reserva institucional.', html)
        self.assertNotIn('Saldo indisponivel/vinculado', documento_html)
        self.assertNotIn('Saldo total financeiro', documento_html)
        self.assertIn('(-) Transferencias para saldo vinculado/indisponivel', documento_html)
        self.assertIn('(=) Saldo disponivel final', documento_html)

    def test_balancete_institucional_resume_transferencia_de_indisponivel_para_disponivel(self):
        self.banco.disponibilidade = ContaFinanceira.DisponibilidadeConta.INDISPONIVEL
        self.banco.saldo_inicial = Decimal('90.00')
        self.banco.save(update_fields=['disponibilidade', 'saldo_inicial'])
        self._criar_transferencia(
            'Banco para dinheiro',
            self.banco,
            self.dinheiro,
            '40.00',
        )

        request, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('contas', str(self.banco.id)),
                ('formato_balancete', 'operacional'),
                ('composicao_saldo', 'detalhada'),
            ]
        )
        html = self._render_balancete(request, contexto)
        documento_html = self._documento_balancete_html(html)

        self.assertEqual(
            contexto['balancete_transferencias_disponiveis_resumo']['entrada_de_indisponivel'],
            Decimal('40.00'),
        )
        self.assertIn(
            '(+) Transferencias de saldo vinculado/indisponivel para disponivel',
            documento_html,
        )
        self.assertNotIn('Saldo total financeiro', documento_html)
        self.assertNotIn('Saldo indisponivel/vinculado', documento_html)

    def test_balancete_institucional_permite_modo_detalhado_por_conta(self):
        self.banco.disponibilidade = ContaFinanceira.DisponibilidadeConta.INDISPONIVEL
        self.banco.saldo_inicial = Decimal('20.00')
        self.banco.save(update_fields=['disponibilidade', 'saldo_inicial'])
        self.dinheiro.saldo_inicial = Decimal('10.00')
        self.dinheiro.save(update_fields=['saldo_inicial'])

        _, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('contas', str(self.banco.id)),
                ('formato_balancete', 'financeiro_completo'),
                ('composicao_saldo', 'detalhada'),
            ]
        )

        self.assertEqual(contexto['balancete_composicao_saldo'], 'detalhada')
        self.assertEqual(
            [item['rotulo'] for item in contexto['balancete_grupos_apresentacao'][0]['itens']],
            ['Dinheiro'],
        )
        self.assertEqual(
            [item['rotulo'] for item in contexto['balancete_grupos_apresentacao'][1]['itens']],
            ['Banco'],
        )
        self.assertEqual(
            [item['rotulo'] for item in contexto['balancete_inicial_grupos_apresentacao'][0]['itens']],
            ['Dinheiro'],
        )
        self.assertEqual(
            [item['rotulo'] for item in contexto['balancete_inicial_grupos_apresentacao'][1]['itens']],
            ['Banco'],
        )

    def test_balancete_institucional_agrupa_conta_investimento_e_integralizacao_por_tipo(self):
        tipo_investimento = TipoContaFinanceira.objects.get(codigo='aplicacao_financeira')
        tipo_integralizacao = TipoContaFinanceira.objects.get(codigo='integralizacao_capital')
        conta_investimento = ContaFinanceira.objects.create(
            nome='Investimento A',
            saldo_inicial=Decimal('30.00'),
            data_saldo_inicial=date(2026, 1, 1),
            tipo_conta=tipo_investimento,
        )
        conta_integralizacao = ContaFinanceira.objects.create(
            nome='Integralizacao B',
            saldo_inicial=Decimal('70.00'),
            data_saldo_inicial=date(2026, 1, 1),
            tipo_conta=tipo_integralizacao,
            disponibilidade=ContaFinanceira.DisponibilidadeConta.INDISPONIVEL,
        )

        _, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(conta_investimento.id)),
                ('contas', str(conta_integralizacao.id)),
                ('formato_balancete', 'financeiro_completo'),
                ('composicao_saldo', 'tipo'),
            ]
        )

        self.assertEqual(
            [item['rotulo'] for item in contexto['balancete_grupos_apresentacao'][0]['itens']],
            ['Conta investimento'],
        )
        self.assertEqual(
            [item['rotulo'] for item in contexto['balancete_grupos_apresentacao'][1]['itens']],
            ['Integralizacao de capital'],
        )
        self.assertEqual(
            [item['rotulo'] for item in contexto['balancete_inicial_grupos_apresentacao'][0]['itens']],
            ['Conta investimento'],
        )
        self.assertEqual(
            [item['rotulo'] for item in contexto['balancete_inicial_grupos_apresentacao'][1]['itens']],
            ['Integralizacao de capital'],
        )

    def test_balancete_institucional_permite_modo_total_consolidado(self):
        self.banco.disponibilidade = ContaFinanceira.DisponibilidadeConta.INDISPONIVEL
        self.banco.saldo_inicial = Decimal('20.00')
        self.banco.save(update_fields=['disponibilidade', 'saldo_inicial'])
        self.dinheiro.saldo_inicial = Decimal('10.00')
        self.dinheiro.save(update_fields=['saldo_inicial'])

        _, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('contas', str(self.banco.id)),
                ('formato_balancete', 'financeiro_completo'),
                ('composicao_saldo', 'total'),
            ]
        )

        self.assertEqual(contexto['balancete_composicao_saldo'], 'total')
        self.assertTrue(all(not grupo['itens'] for grupo in contexto['balancete_grupos_apresentacao']))
        self.assertTrue(contexto['balancete_exibe_total_financeiro'])
        self.assertEqual(contexto['balancete_total_apresentado'], Decimal('70.00'))
        self.assertTrue(all(not grupo['itens'] for grupo in contexto['balancete_inicial_grupos_apresentacao']))
        self.assertTrue(contexto['balancete_inicial_exibe_total_financeiro'])
        self.assertEqual(contexto['balancete_inicial_total_apresentado'], Decimal('30.00'))

    def test_balancete_institucional_ignora_parametro_legado_de_modelo(self):
        _, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('modelo_relatorio', 'contribuinte'),
            ]
        )

        self.assertEqual(contexto['balancete_formato'], 'operacional')
        self.assertEqual(contexto['balancete_composicao_saldo'], 'tipo')
        self.assertFalse(contexto['balancete_exibir_indisponiveis'])

    def test_balancete_institucional_mapeia_parametro_legado_de_vinculadas_para_formato(self):
        _, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('exibir_vinculadas', '1'),
            ]
        )

        self.assertEqual(contexto['balancete_formato'], 'financeiro_completo')
        self.assertTrue(contexto['balancete_exibir_indisponiveis'])

    def test_balancete_institucional_prioriza_formato_sobre_parametro_legado(self):
        _, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('formato_balancete', 'operacional'),
                ('exibir_vinculadas', '1'),
            ]
        )

        self.assertEqual(contexto['balancete_formato'], 'operacional')
        self.assertFalse(contexto['balancete_exibir_indisponiveis'])

    def test_balancete_institucional_ignora_parametro_legado_de_saldo_inicial_detalhado(self):
        tipo_caixa = TipoContaFinanceira.objects.get(codigo='dinheiro_caixa')
        self.dinheiro.tipo_conta = tipo_caixa
        self.dinheiro.save(update_fields=['tipo_conta'])
        _, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('mostrar_contas_zeradas', '1'),
                ('exibir_saldo_inicial_detalhado', '1'),
            ]
        )

        self.assertEqual(contexto['balancete_composicao_saldo'], 'tipo')
        self.assertEqual(
            [item['rotulo'] for item in contexto['balancete_inicial_grupos_apresentacao'][0]['itens']],
            ['Dinheiro/caixa'],
        )

    def test_balancete_institucional_nao_imprime_metadados_dos_filtros_novos(self):
        request, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
            ]
        )
        html = self._render_balancete(request, contexto)
        documento_html = self._documento_balancete_html(html)

        self.assertNotIn('Modelo do relatorio', html)
        self.assertNotIn('Modelo:', documento_html)
        self.assertNotIn('Formato do Balancete:', documento_html)
        self.assertNotIn('Composicao:', documento_html)
        self.assertNotIn('Exibir vinculadas/indisponiveis', html)
        self.assertNotIn('Detalhar saldo inicial por conta', documento_html)

    def test_balancete_institucional_organiza_blocos_na_ordem_documental(self):
        request, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
            ]
        )
        html = self._render_balancete(request, contexto)

        ordem = [
            '1. SALDO OPERACIONAL ANTERIOR',
            '2. ENTRADAS OPERACIONAIS',
            '3. SAIDAS OPERACIONAIS',
            '4. RESUMO OPERACIONAL DO PERIODO',
            '5. COMPOSICAO DO SALDO OPERACIONAL ATUAL',
        ]
        posicoes = [html.index(texto) for texto in ordem]

        self.assertNotIn('1. RESUMO FINANCEIRO DO PERIODO', html)
        self.assertEqual(posicoes, sorted(posicoes))

    def test_balancete_institucional_classifica_integralizacao_indisponivel(self):
        tipo_integralizacao = TipoContaFinanceira.objects.get(codigo='integralizacao_capital')
        conta_integralizacao = ContaFinanceira.objects.create(
            nome='Integralizacao cooperativa',
            saldo_inicial=Decimal('120.00'),
            data_saldo_inicial=date(2026, 1, 1),
            tipo_conta=tipo_integralizacao,
            disponibilidade=ContaFinanceira.DisponibilidadeConta.INDISPONIVEL,
        )
        request = self.factory.get(
            '/financeiro/balancete-institucional/',
            data=[
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(conta_integralizacao.id)),
                ('formato_balancete', 'financeiro_completo'),
            ],
        )
        view = BalanceteInstitucionalFinanceiroView()
        view.request = request

        contexto = view.get_context_data()

        self.assertEqual(contexto['balancete_composicao_disponivel'], [])
        self.assertEqual(
            [item['conta'] for item in contexto['balancete_composicao_indisponivel']],
            [conta_integralizacao],
        )
        self.assertEqual(contexto['balancete_subtotal_indisponivel'], Decimal('120.00'))
        self.assertEqual(contexto['balancete_total_financeiro'], Decimal('120.00'))

    def test_balancete_institucional_nao_exibe_mensagem_vazia(self):
        self.banco.disponibilidade = ContaFinanceira.DisponibilidadeConta.INDISPONIVEL
        self.banco.mensagem_indisponibilidade = '   '
        self.banco.save(update_fields=['disponibilidade', 'mensagem_indisponibilidade'])
        request = self.factory.get(
            '/financeiro/balancete-institucional/',
            data=[
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.banco.id)),
            ],
        )
        view = BalanceteInstitucionalFinanceiroView()
        view.request = request

        contexto = view.get_context_data()
        html = self._render_balancete(request, contexto)
        documento_html = self._documento_balancete_html(html)

        self.assertEqual(
            contexto['balancete_composicao_indisponivel'][0]['mensagem_indisponibilidade'],
            '',
        )
        self.assertNotIn('<tr class="balancete-message-row">', documento_html)

    def test_balancete_institucional_mantem_transferencias_entre_disponiveis_fora_do_resumo_vinculado(self):
        request, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('contas', str(self.banco.id)),
                ('formato_balancete', 'operacional'),
                ('composicao_saldo', 'tipo'),
            ]
        )
        html = self._render_balancete(request, contexto)
        documento_html = self._documento_balancete_html(html)

        self.assertFalse(contexto['balancete_transferencias_disponiveis_resumo']['saida_para_indisponivel'])
        self.assertFalse(contexto['balancete_transferencias_disponiveis_resumo']['entrada_de_indisponivel'])
        self.assertNotIn('Transferencias para saldo vinculado/indisponivel', documento_html)
        self.assertNotIn(
            'Transferencias de saldo vinculado/indisponivel para disponivel',
            documento_html,
        )

    def test_balancete_institucional_exibe_filtro_principal_de_formato(self):
        request, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
            ]
        )
        html = self._render_balancete(request, contexto)

        self.assertIn('Formato do Balancete', html)
        self.assertNotIn('Exibir vinculadas/indisponiveis', html)
        self.assertIn('id="balancete-formato"', html)
        self.assertIn('data-balancete-formato', html)
        self.assertIn('id="balancete-filtro-detalhar-patrimonio"', html)
        self.assertIn('data-balancete-filtro-patrimonio', html)
        self.assertIn('function atualizarVisibilidadeFiltroPatrimonio()', html)

    def test_balancete_institucional_oculta_filtro_patrimonio_fora_do_formato_dependente(self):
        request, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('formato_balancete', 'operacional'),
            ]
        )
        html = self._render_balancete(request, contexto)

        self.assertIn('id="balancete-filtro-detalhar-patrimonio"', html)
        bloco = html.split('id="balancete-filtro-detalhar-patrimonio"', 1)[1].split('>', 1)[0]
        self.assertIn('hidden', bloco)
        self.assertIn('display: none;', bloco)

    def test_balancete_institucional_oculta_filtro_patrimonio_no_financeiro_completo(self):
        request, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('formato_balancete', 'financeiro_completo'),
            ]
        )
        html = self._render_balancete(request, contexto)
        bloco = html.split('id="balancete-filtro-detalhar-patrimonio"', 1)[1].split('>', 1)[0]

        self.assertIn('hidden', bloco)
        self.assertIn('display: none;', bloco)

    def test_balancete_institucional_operacional_patrimonio_mostra_bloco_separado(self):
        self.banco.disponibilidade = ContaFinanceira.DisponibilidadeConta.INDISPONIVEL
        self.banco.saldo_inicial = Decimal('20.00')
        self.banco.mensagem_indisponibilidade = 'Reserva patrimonial.'
        self.banco.save(update_fields=['disponibilidade', 'saldo_inicial', 'mensagem_indisponibilidade'])

        request, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('contas', str(self.banco.id)),
                ('formato_balancete', 'operacional_patrimonio'),
            ]
        )
        html = self._render_balancete(request, contexto)
        documento_html = self._documento_balancete_html(html)

        self.assertEqual(contexto['balancete_formato'], 'operacional_patrimonio')
        self.assertTrue(contexto['balancete_mostrar_bloco_patrimonial'])
        self.assertFalse(contexto['balancete_detalhar_patrimonio_vinculado'])
        self.assertIn('Detalhar patrimonio vinculado', html)
        bloco = html.split('id="balancete-filtro-detalhar-patrimonio"', 1)[1].split('>', 1)[0]
        self.assertNotIn('hidden', bloco)
        self.assertNotIn('is-hidden', bloco)
        self.assertNotIn('display: none;', bloco)
        self.assertIn('6. INFORMACAO PATRIMONIAL COMPLEMENTAR', documento_html)
        self.assertIn('Saldo atual vinculado/indisponivel', documento_html)
        self.assertNotIn('Saldo inicial vinculado/indisponivel', documento_html)
        self.assertNotIn('Reserva patrimonial.', documento_html)

    def test_balancete_institucional_operacional_patrimonio_detalhado_mostra_movimento_e_mensagens(self):
        self.banco.disponibilidade = ContaFinanceira.DisponibilidadeConta.INDISPONIVEL
        self.banco.saldo_inicial = Decimal('20.00')
        self.banco.mensagem_indisponibilidade = 'Reserva patrimonial.'
        self.banco.save(update_fields=['disponibilidade', 'saldo_inicial', 'mensagem_indisponibilidade'])
        self._criar_transferencia(
            'Banco para dinheiro',
            self.banco,
            self.dinheiro,
            '40.00',
        )

        request, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('contas', str(self.banco.id)),
                ('formato_balancete', 'operacional_patrimonio'),
                ('detalhar_patrimonio_vinculado', '1'),
                ('composicao_saldo', 'detalhada'),
            ]
        )
        html = self._render_balancete(request, contexto)
        documento_html = self._documento_balancete_html(html)

        self.assertTrue(contexto['balancete_detalhar_patrimonio_vinculado'])
        self.assertIn('Saldo inicial vinculado/indisponivel', documento_html)
        self.assertIn('Entradas para saldo vinculado/indisponivel', documento_html)
        self.assertIn('Saidas do saldo vinculado/indisponivel', documento_html)
        self.assertIn('Reserva patrimonial.', documento_html)

    def test_balancete_institucional_financeiro_completo_mostra_leitura_total(self):
        self.banco.disponibilidade = ContaFinanceira.DisponibilidadeConta.INDISPONIVEL
        self.banco.saldo_inicial = Decimal('20.00')
        self.banco.save(update_fields=['disponibilidade', 'saldo_inicial'])

        request, contexto = self._contexto_balancete(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('contas', str(self.banco.id)),
                ('formato_balancete', 'financeiro_completo'),
                ('composicao_saldo', 'total'),
            ]
        )
        html = self._render_balancete(request, contexto)
        documento_html = self._documento_balancete_html(html)

        self.assertEqual(contexto['balancete_formato'], 'financeiro_completo')
        self.assertTrue(contexto['balancete_exibir_indisponiveis'])
        self.assertFalse(contexto['balancete_mostrar_bloco_patrimonial'])
        self.assertIn('1. SALDO FINANCEIRO INICIAL', documento_html)
        self.assertIn('4. RESUMO FINANCEIRO DO PERIODO', documento_html)
        self.assertIn('5. COMPOSICAO DO SALDO FINANCEIRO FINAL', documento_html)
        self.assertIn('Saldo total financeiro', documento_html)

    def test_prestacao_contas_nao_ganha_chaves_de_leitura_patrimonial(self):
        contexto = self._contexto([self.dinheiro, self.banco], exibir_transferencias=True)

        self.assertEqual(contexto['saldo_final_consolidado'], Decimal('40.00'))
        self.assertNotIn('balancete_composicao_disponivel', contexto)
        self.assertNotIn('balancete_composicao_indisponivel', contexto)


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

    def _render_extrato(self, params):
        request = self.factory.get('/financeiro/extratos/', data=params)
        request.resolver_match = resolve('/financeiro/extratos/')
        view = ExtratoFinanceiroView()
        view.request = request
        context = view.get_context_data()
        return render_to_string('financeiro/conta_extrato.html', context, request=request), context

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

    def test_extrato_cabecalho_mostra_nome_quando_ha_uma_conta(self):
        html, contexto = self._render_extrato(
            {
                'data_inicial': '2026-03-01',
                'data_final': '2026-03-31',
                'contas': str(self.dinheiro.id),
            }
        )

        self.assertEqual(contexto['extrato_contas_selecionadas_label'], 'Dinheiro')
        self.assertIn('Contas selecionadas:</strong>', html)
        self.assertIn('Dinheiro', html)
        self.assertNotIn('1 conta selecionada', html)
        self.assertEqual(contexto['saldo_final'], Decimal('160.00'))

    def test_extrato_cabecalho_mostra_nomes_ate_tres_contas(self):
        html, contexto = self._render_extrato(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('contas', str(self.banco.id)),
                ('contas', str(self.caixa_externo.id)),
            ]
        )

        self.assertEqual(
            contexto['extrato_contas_selecionadas_label'],
            'Dinheiro, Banco, Caixa externo',
        )
        self.assertIn('Dinheiro, Banco, Caixa externo', html)
        self.assertNotIn('3 contas selecionadas', html)
        self.assertEqual(contexto['saldo_final'], Decimal('150.00'))

    def test_extrato_cabecalho_resume_quando_ha_muitas_contas(self):
        conta_extra = ContaFinanceira.objects.create(
            nome='Carteira',
            saldo_inicial=Decimal('25.00'),
            data_saldo_inicial=date(2026, 1, 1),
        )
        html, contexto = self._render_extrato(
            [
                ('data_inicial', '2026-03-01'),
                ('data_final', '2026-03-31'),
                ('contas', str(self.dinheiro.id)),
                ('contas', str(self.banco.id)),
                ('contas', str(self.caixa_externo.id)),
                ('contas', str(conta_extra.id)),
            ]
        )

        self.assertEqual(contexto['extrato_contas_selecionadas_label'], '4 contas selecionadas')
        self.assertIn('4 contas selecionadas', html)
        self.assertEqual(contexto['saldo_final'], Decimal('175.00'))


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
class FrequenciaMensalBaseCadastralTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_pessoa_financeira_default_contribuinte_recorrente_false(self):
        pessoa = PessoaFinanceira.objects.create(codigo='P900', nome='Pessoa teste')

        self.assertFalse(pessoa.contribuinte_recorrente)

    def test_categoria_financeira_default_controla_recorrencia_false(self):
        categoria = CategoriaFinanceira.objects.create(
            nome='Contribuicao mensal',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
        )

        self.assertFalse(categoria.controla_recorrencia_competencia)

    def test_form_pessoa_permite_marcar_contribuinte_recorrente(self):
        form = PessoaFinanceiraForm(
            data={
                'codigo': 'P901',
                'nome': 'Pessoa recorrente',
                'tipo_pessoa': '',
                'documento': '',
                'telefone': '',
                'email': '',
                'observacoes': '',
                'contribuinte_recorrente': 'on',
                'ativo': 'on',
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        pessoa = form.save()
        self.assertTrue(pessoa.contribuinte_recorrente)

    def test_form_categoria_permite_marcar_controle_recorrencia(self):
        form = CategoriaFinanceiraForm(
            data={
                'nome': 'Contribuicao mensal',
                'tipo': CategoriaFinanceira.TipoCategoria.RECEITA,
                'categoria_pai': '',
                'controla_recorrencia_competencia': 'on',
                'mensagem_recibo': '',
                'ativo': 'on',
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        categoria = form.save()
        self.assertTrue(categoria.controla_recorrencia_competencia)

    def test_template_pessoa_list_mostra_indicador_recorrente(self):
        pessoa = PessoaFinanceira.objects.create(
            codigo='P902',
            nome='Pessoa recorrente listagem',
            contribuinte_recorrente=True,
        )
        request = self.factory.get('/financeiro/pessoas/')
        request.user = type('UserStub', (), {'is_authenticated': False})()
        html = render_to_string(
            'financeiro/pessoa_list.html',
            {
                'pessoas': [pessoa],
                'exportacao_pessoas_url': '/financeiro/pessoas/exportar/',
                'request': request,
            },
            request=request,
        )

        self.assertIn('Recorrente', html)
        self.assertIn('Sim', html)

    def test_template_categoria_list_mostra_indicador_controle_frequencia(self):
        categoria = CategoriaFinanceira.objects.create(
            nome='Contribuicao mensal',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
            controla_recorrencia_competencia=True,
        )
        request = self.factory.get('/financeiro/categorias/')
        request.user = type('UserStub', (), {'is_authenticated': False})()
        html = render_to_string(
            'financeiro/categoria_list.html',
            {
                'categorias': [categoria],
                'exportacao_categorias_url': '/financeiro/categorias/exportar/',
                'request': request,
            },
            request=request,
        )

        self.assertIn('Controla frequ', html)
        self.assertIn('Sim', html)


class AlocacaoCompetenciaFinanceiraTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.conta = ContaFinanceira.objects.create(
            nome='Conta recorrencia',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
        )
        self.pessoa_recorrente = PessoaFinanceira.objects.create(
            codigo='P950',
            nome='Contribuinte recorrente',
            contribuinte_recorrente=True,
        )
        self.pessoa_avulsa = PessoaFinanceira.objects.create(
            codigo='P951',
            nome='Pessoa avulsa',
            contribuinte_recorrente=False,
        )
        self.categoria_receita_pai = CategoriaFinanceira.objects.create(
            nome='Receitas recorrentes',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
        )
        self.categoria_controlada = CategoriaFinanceira.objects.create(
            nome='Contribuicao mensal',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
            categoria_pai=self.categoria_receita_pai,
            controla_recorrencia_competencia=True,
        )
        self.categoria_nao_controlada = CategoriaFinanceira.objects.create(
            nome='Venda de livros',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
            categoria_pai=self.categoria_receita_pai,
            controla_recorrencia_competencia=False,
        )

    def _dados_lancamento(self, **overrides):
        dados = {
            'descricao': 'Recebimento recorrente',
            'tipo': LancamentoFinanceiro.TipoLancamento.RECEITA,
            'status': LancamentoFinanceiro.StatusLancamento.QUITADO,
            'valor': '100.00',
            'data_competencia': '2026-03-10',
            'data_pagamento': '2026-03-10',
            'numero_documento': '',
            'pessoa': str(self.pessoa_recorrente.pk),
            'categoria': str(self.categoria_controlada.pk),
            'centro_custo': '',
            'conta': str(self.conta.pk),
            'conta_destino': '',
            'observacoes': '',
            'lancamento_com_rateio': '',
            'salvar_como_regra_automatica': '',
            'valor_total_documento': '',
            'rateio_payload': '',
            'competencias_payload': json.dumps([
                {'mes': '1', 'ano': '2026', 'valor': '50.00'},
                {'mes': '2', 'ano': '2026', 'valor': '50.00'},
            ]),
        }
        dados.update(overrides)
        return dados

    def _criar_lancamento_controlado(self, valor='100.00'):
        return LancamentoFinanceiro.objects.create(
            descricao='Recebimento recorrente salvo',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal(valor),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            pessoa=self.pessoa_recorrente,
            categoria=self.categoria_controlada,
            conta=self.conta,
        )

    def _dados_rateio(self, **overrides):
        dados = self._dados_lancamento(
            valor='',
            categoria='',
            lancamento_com_rateio='on',
            valor_total_documento='130.00',
            rateio_payload=json.dumps([
                {'categoria': str(self.categoria_controlada.pk), 'valor': '100.00'},
                {'categoria': str(self.categoria_nao_controlada.pk), 'valor': '30.00'},
            ]),
            competencias_payload='',
            competencias_rateio_payload=json.dumps({
                str(self.categoria_controlada.pk): [
                    {'mes': '1', 'ano': '2026', 'valor': '50.00'},
                    {'mes': '2', 'ano': '2026', 'valor': '50.00'},
                ]
            }),
        )
        dados.update(overrides)
        return dados

    def _build_request(self, path='/', data=None):
        request = self.factory.post(path, data=data or {})
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        setattr(request, '_messages', FallbackStorage(request))
        request.user = type('UserStub', (), {'is_authenticated': False})()
        return request

    def test_model_permite_criar_alocacao_valida(self):
        lancamento = self._criar_lancamento_controlado()
        alocacao = AlocacaoCompetenciaFinanceira(
            lancamento=lancamento,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=3,
            valor_alocado=Decimal('100.00'),
        )

        alocacao.full_clean()

    def test_model_nao_aceita_mes_invalido(self):
        lancamento = self._criar_lancamento_controlado()
        alocacao = AlocacaoCompetenciaFinanceira(
            lancamento=lancamento,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=13,
            valor_alocado=Decimal('100.00'),
        )

        with self.assertRaises(ValidationError):
            alocacao.full_clean()

    def test_model_nao_aceita_valor_zerado_ou_negativo(self):
        lancamento = self._criar_lancamento_controlado()
        alocacao = AlocacaoCompetenciaFinanceira(
            lancamento=lancamento,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=3,
            valor_alocado=Decimal('0.00'),
        )

        with self.assertRaises(ValidationError):
            alocacao.full_clean()

    def test_exclusao_do_lancamento_remove_alocacoes(self):
        lancamento = self._criar_lancamento_controlado()
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=lancamento,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=3,
            valor_alocado=Decimal('100.00'),
        )

        lancamento.delete()

        self.assertFalse(AlocacaoCompetenciaFinanceira.objects.exists())

    def test_lancamento_simples_salva_competencias_quando_regras_batem(self):
        form = LancamentoFinanceiroForm(data=self._dados_lancamento())

        self.assertTrue(form.is_valid(), form.errors)
        lancamento = form.save()

        self.assertEqual(lancamento.alocacoes_competencia.count(), 2)
        self.assertEqual(
            list(
                lancamento.alocacoes_competencia.values_list(
                    'mes_competencia',
                    'ano_competencia',
                    'valor_alocado',
                )
            ),
            [
                (1, 2026, Decimal('50.00')),
                (2, 2026, Decimal('50.00')),
            ],
        )

    def test_lancamento_simples_bloqueia_soma_divergente(self):
        form = LancamentoFinanceiroForm(
            data=self._dados_lancamento(
                competencias_payload=json.dumps([
                    {'mes': '1', 'ano': '2026', 'valor': '30.00'},
                    {'mes': '2', 'ano': '2026', 'valor': '50.00'},
                ])
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            'A soma das competencias deve ser igual ao valor controlado do lancamento.',
            form.errors['competencias_payload'],
        )

    def test_lancamento_sem_pessoa_recorrente_nao_exige_competencias(self):
        dados = self._dados_lancamento(
            pessoa=str(self.pessoa_avulsa.pk),
            competencias_payload='',
        )
        form = LancamentoFinanceiroForm(data=dados)

        self.assertTrue(form.is_valid(), form.errors)
        lancamento = form.save()
        self.assertEqual(lancamento.alocacoes_competencia.count(), 0)

    def test_lancamento_sem_subcategoria_controlada_nao_exige_competencias(self):
        dados = self._dados_lancamento(
            categoria=str(self.categoria_nao_controlada.pk),
            competencias_payload='',
        )
        form = LancamentoFinanceiroForm(data=dados)

        self.assertTrue(form.is_valid(), form.errors)
        lancamento = form.save()
        self.assertEqual(lancamento.alocacoes_competencia.count(), 0)

    def test_lancamento_simples_bloqueia_competencia_duplicada_no_mesmo_mes_ano(self):
        form = LancamentoFinanceiroForm(
            data=self._dados_lancamento(
                valor='110.00',
                competencias_payload=json.dumps([
                    {'mes': '1', 'ano': '2026', 'valor': '50.00'},
                    {'mes': '1', 'ano': '2026', 'valor': '60.00'},
                ]),
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            'Ja existe uma competencia informada para este mes/ano. Agrupe o valor em uma unica linha.',
            form.errors['competencias_payload'],
        )
        self.assertNotIn(
            'A soma das competencias deve ser igual ao valor controlado do lancamento.',
            form.errors['competencias_payload'],
        )

    def test_lancamento_simples_permite_competencias_iguais_em_lancamentos_diferentes(self):
        form_primeiro = LancamentoFinanceiroForm(data=self._dados_lancamento())
        self.assertTrue(form_primeiro.is_valid(), form_primeiro.errors)
        primeiro = form_primeiro.save()

        form_segundo = LancamentoFinanceiroForm(data=self._dados_lancamento(numero_documento='DOC-002'))
        self.assertTrue(form_segundo.is_valid(), form_segundo.errors)
        segundo = form_segundo.save()

        self.assertEqual(primeiro.alocacoes_competencia.count(), 2)
        self.assertEqual(segundo.alocacoes_competencia.count(), 2)

    def test_clone_nao_precarrega_competencias(self):
        lancamento = self._criar_lancamento_controlado()
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=lancamento,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=1,
            valor_alocado=Decimal('100.00'),
        )
        view = LancamentoFinanceiroCloneView()
        view.lancamento_origem = lancamento

        initial = view.get_initial()
        form = LancamentoFinanceiroForm(initial=initial)

        self.assertEqual(form.competencias_linhas_iniciais, [])
        self.assertFalse(form.competencias_bloco_visivel)

    def test_edicao_carrega_competencias_existentes(self):
        lancamento = self._criar_lancamento_controlado()
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=lancamento,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=1,
            valor_alocado=Decimal('40.00'),
        )
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=lancamento,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=2,
            valor_alocado=Decimal('60.00'),
        )

        form = LancamentoFinanceiroForm(instance=lancamento)

        self.assertEqual(
            form.competencias_linhas_iniciais,
            [
                {'mes': '1', 'ano': '2026', 'valor': '40.00'},
                {'mes': '2', 'ano': '2026', 'valor': '60.00'},
            ],
        )
        self.assertTrue(form.competencias_bloco_visivel)

    def test_rateio_com_item_controlado_exige_competencias_pela_parte_controlada(self):
        dados = self._dados_rateio()
        form = LancamentoFinanceiroForm(data=dados)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.cleaned_data['competencias_rateio_por_categoria'][self.categoria_controlada.pk],
            [
                {'mes_competencia': 1, 'ano_competencia': 2026, 'valor_alocado': Decimal('50.00')},
                {'mes_competencia': 2, 'ano_competencia': 2026, 'valor_alocado': Decimal('50.00')},
            ],
        )

    def test_rateio_misto_nao_compara_competencias_com_valor_total_do_documento(self):
        dados = self._dados_rateio(
            valor_total_documento='150.00',
            rateio_payload=json.dumps([
                {'categoria': str(self.categoria_controlada.pk), 'valor': '100.00'},
                {'categoria': str(self.categoria_nao_controlada.pk), 'valor': '50.00'},
            ]),
        )
        form = LancamentoFinanceiroForm(data=dados)

        self.assertTrue(form.is_valid(), form.errors)

    def test_rateio_bloqueia_quando_soma_competencias_da_parte_controlada_diverge(self):
        dados = self._dados_rateio(
            competencias_rateio_payload=json.dumps({
                str(self.categoria_controlada.pk): [
                    {'mes': '1', 'ano': '2026', 'valor': '40.00'},
                    {'mes': '2', 'ano': '2026', 'valor': '50.00'},
                ]
            }),
        )
        form = LancamentoFinanceiroForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn(
            f'A soma das competencias deve ser igual ao valor controlado da subcategoria no rateio: {self.categoria_controlada}.',
            form.errors['competencias_rateio_payload'],
        )

    def test_rateio_bloqueia_competencia_duplicada_na_mesma_subcategoria_controlada(self):
        dados = self._dados_rateio(
            rateio_payload=json.dumps([
                {'categoria': str(self.categoria_controlada.pk), 'valor': '110.00'},
                {'categoria': str(self.categoria_nao_controlada.pk), 'valor': '30.00'},
            ]),
            valor_total_documento='140.00',
            competencias_rateio_payload=json.dumps({
                str(self.categoria_controlada.pk): [
                    {'mes': '1', 'ano': '2026', 'valor': '50.00'},
                    {'mes': '1', 'ano': '2026', 'valor': '60.00'},
                ]
            }),
        )
        form = LancamentoFinanceiroForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn(
            f'{self.categoria_controlada}: Ja existe uma competencia informada para este mes/ano. Agrupe o valor em uma unica linha.',
            form.errors['competencias_rateio_payload'],
        )
        self.assertNotIn(
            f'A soma das competencias deve ser igual ao valor controlado da subcategoria no rateio: {self.categoria_controlada}.',
            form.errors['competencias_rateio_payload'],
        )

    def test_rateio_permite_mes_ano_igual_em_subcategorias_controladas_diferentes(self):
        outra_categoria_controlada = CategoriaFinanceira.objects.create(
            nome='Contribuicao assistencial',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
            categoria_pai=self.categoria_receita_pai,
            controla_recorrencia_competencia=True,
        )
        dados = self._dados_rateio(
            valor_total_documento='100.00',
            rateio_payload=json.dumps([
                {'categoria': str(self.categoria_controlada.pk), 'valor': '60.00'},
                {'categoria': str(outra_categoria_controlada.pk), 'valor': '40.00'},
            ]),
            competencias_rateio_payload=json.dumps({
                str(self.categoria_controlada.pk): [
                    {'mes': '1', 'ano': '2026', 'valor': '60.00'},
                ],
                str(outra_categoria_controlada.pk): [
                    {'mes': '1', 'ano': '2026', 'valor': '40.00'},
                ],
            }),
        )
        form = LancamentoFinanceiroForm(data=dados)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.cleaned_data['competencias_rateio_por_categoria'][self.categoria_controlada.pk],
            [{'mes_competencia': 1, 'ano_competencia': 2026, 'valor_alocado': Decimal('60.00')}],
        )
        self.assertEqual(
            form.cleaned_data['competencias_rateio_por_categoria'][outra_categoria_controlada.pk],
            [{'mes_competencia': 1, 'ano_competencia': 2026, 'valor_alocado': Decimal('40.00')}],
        )

    def test_rateio_sem_pessoa_recorrente_nao_exige_competencias(self):
        dados = self._dados_rateio(
            pessoa=str(self.pessoa_avulsa.pk),
            competencias_rateio_payload='',
        )
        form = LancamentoFinanceiroForm(data=dados)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['competencias_rateio_por_categoria'], {})

    def test_rateio_sem_subcategoria_controlada_nao_exige_competencias(self):
        dados = self._dados_rateio(
            rateio_payload=json.dumps([
                {'categoria': str(self.categoria_nao_controlada.pk), 'valor': '70.00'},
                {'categoria': str(self.categoria_nao_controlada.pk), 'valor': '60.00'},
            ]),
            competencias_rateio_payload='',
        )
        form = LancamentoFinanceiroForm(data=dados)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['competencias_rateio_por_categoria'], {})

    def test_rateio_cria_alocacoes_apenas_para_item_controlado(self):
        dados = self._dados_rateio()
        form = LancamentoFinanceiroForm(data=dados)

        self.assertTrue(form.is_valid(), form.errors)

        request = self._build_request('/financeiro/lancamentos/novo/', data=dados)
        view = LancamentoFinanceiroCreateView()
        view.request = request
        view.object = None

        response = view.form_valid(form)

        self.assertEqual(response.status_code, 302)
        lancamentos = list(LancamentoFinanceiro.objects.filter(grupo_rateio=form.cleaned_data['grupo_rateio']).order_by('categoria_id'))
        self.assertEqual(len(lancamentos), 2)
        lancamento_controlado = next(l for l in lancamentos if l.categoria_id == self.categoria_controlada.pk)
        lancamento_nao_controlado = next(l for l in lancamentos if l.categoria_id == self.categoria_nao_controlada.pk)
        self.assertEqual(lancamento_controlado.alocacoes_competencia.count(), 2)
        self.assertEqual(lancamento_nao_controlado.alocacoes_competencia.count(), 0)

    def test_rateio_edicao_carrega_competencias_existentes_por_subcategoria(self):
        grupo_rateio = 'grp-comp'
        lancamento_controlado = LancamentoFinanceiro.objects.create(
            descricao='Recebimento rateado',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('100.00'),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            numero_documento='100326-001',
            pessoa=self.pessoa_recorrente,
            categoria=self.categoria_controlada,
            conta=self.conta,
            com_rateio=True,
            grupo_rateio=grupo_rateio,
        )
        LancamentoFinanceiro.objects.create(
            descricao='Recebimento rateado',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('30.00'),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            numero_documento='100326-001',
            pessoa=self.pessoa_recorrente,
            categoria=self.categoria_nao_controlada,
            conta=self.conta,
            com_rateio=True,
            grupo_rateio=grupo_rateio,
        )
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=lancamento_controlado,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=1,
            valor_alocado=Decimal('40.00'),
        )
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=lancamento_controlado,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=2,
            valor_alocado=Decimal('60.00'),
        )

        form = LancamentoFinanceiroGrupoRateioForm(
            instance=lancamento_controlado,
            grupo_lancamentos=list(
                LancamentoFinanceiro.objects.filter(grupo_rateio=grupo_rateio).order_by('pk')
            ),
        )

        self.assertEqual(
            form.competencias_rateio_iniciais,
            {
                str(self.categoria_controlada.pk): [
                    {'mes': '1', 'ano': '2026', 'valor': '40.00'},
                    {'mes': '2', 'ano': '2026', 'valor': '60.00'},
                ]
            },
        )

    def test_clone_rateado_nao_precarrega_competencias(self):
        grupo_rateio = 'grp-clone'
        lancamento_controlado = LancamentoFinanceiro.objects.create(
            descricao='Recebimento rateado',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('100.00'),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            numero_documento='100326-002',
            pessoa=self.pessoa_recorrente,
            categoria=self.categoria_controlada,
            conta=self.conta,
            com_rateio=True,
            grupo_rateio=grupo_rateio,
        )
        LancamentoFinanceiro.objects.create(
            descricao='Recebimento rateado',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('30.00'),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            numero_documento='100326-002',
            pessoa=self.pessoa_recorrente,
            categoria=self.categoria_nao_controlada,
            conta=self.conta,
            com_rateio=True,
            grupo_rateio=grupo_rateio,
        )
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=lancamento_controlado,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=1,
            valor_alocado=Decimal('100.00'),
        )

        view = LancamentoFinanceiroGrupoRateioCloneView()
        view.request = self._build_request('/financeiro/lancamentos/rateio/grp-clone/clonar/')
        view.object = None
        view.kwargs = {'grupo_rateio': grupo_rateio}
        view._grupo_origem_info_cache = {
            'grupo_rateio': grupo_rateio,
            'lancamentos': list(LancamentoFinanceiro.objects.filter(grupo_rateio=grupo_rateio).order_by('pk')),
            'erro': '',
            'representante': lancamento_controlado,
        }
        form = view.get_form()

        self.assertEqual(form.competencias_rateio_iniciais, {})

    def test_rateio_edicao_remove_alocacoes_quando_item_deixa_de_ser_controlado(self):
        grupo_rateio = 'grp-update'
        lancamento_controlado = LancamentoFinanceiro.objects.create(
            descricao='Recebimento rateado',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('100.00'),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            numero_documento='100326-003',
            pessoa=self.pessoa_recorrente,
            categoria=self.categoria_controlada,
            conta=self.conta,
            com_rateio=True,
            grupo_rateio=grupo_rateio,
        )
        lancamento_nao_controlado = LancamentoFinanceiro.objects.create(
            descricao='Recebimento rateado',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('30.00'),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            numero_documento='100326-003',
            pessoa=self.pessoa_recorrente,
            categoria=self.categoria_nao_controlada,
            conta=self.conta,
            com_rateio=True,
            grupo_rateio=grupo_rateio,
        )
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=lancamento_controlado,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=1,
            valor_alocado=Decimal('100.00'),
        )

        dados = {
            'descricao': 'Recebimento rateado',
            'tipo': LancamentoFinanceiro.TipoLancamento.RECEITA,
            'status': LancamentoFinanceiro.StatusLancamento.QUITADO,
            'data_competencia': '2026-03-10',
            'data_pagamento': '2026-03-10',
            'numero_documento': '100326-003',
            'pessoa': str(self.pessoa_recorrente.pk),
            'centro_custo': '',
            'conta': str(self.conta.pk),
            'conta_destino': '',
            'observacoes': '',
            'valor_total_documento': '130.00',
            'rateio_payload': json.dumps([
                {'id': str(lancamento_controlado.pk), 'categoria': str(self.categoria_nao_controlada.pk), 'valor': '100.00'},
                {'id': str(lancamento_nao_controlado.pk), 'categoria': str(self.categoria_nao_controlada.pk), 'valor': '30.00'},
            ]),
            'competencias_rateio_payload': '',
        }
        form = LancamentoFinanceiroGrupoRateioForm(
            data=dados,
            instance=lancamento_controlado,
            grupo_lancamentos=[lancamento_controlado, lancamento_nao_controlado],
        )

        self.assertTrue(form.is_valid(), form.errors)

        request = self._build_request('/financeiro/lancamentos/rateio/grp-update/editar/', data=dados)
        view = LancamentoFinanceiroGrupoRateioUpdateView()
        view.request = request
        view.kwargs = {'grupo_rateio': grupo_rateio}
        view._grupo_info_cache = {
            'grupo_rateio': grupo_rateio,
            'lancamentos': [lancamento_controlado, lancamento_nao_controlado],
            'erro': '',
            'erro_codigo': '',
            'representante': lancamento_controlado,
        }

        response = view.form_valid(form)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(AlocacaoCompetenciaFinanceira.objects.exists())

    def test_rateio_edicao_bloqueia_competencia_duplicada_na_mesma_subcategoria(self):
        grupo_rateio = 'grp-dup'
        lancamento_controlado = LancamentoFinanceiro.objects.create(
            descricao='Recebimento rateado',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('100.00'),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            numero_documento='100326-004',
            pessoa=self.pessoa_recorrente,
            categoria=self.categoria_controlada,
            conta=self.conta,
            com_rateio=True,
            grupo_rateio=grupo_rateio,
        )
        lancamento_nao_controlado = LancamentoFinanceiro.objects.create(
            descricao='Recebimento rateado',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('30.00'),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            numero_documento='100326-004',
            pessoa=self.pessoa_recorrente,
            categoria=self.categoria_nao_controlada,
            conta=self.conta,
            com_rateio=True,
            grupo_rateio=grupo_rateio,
        )

        dados = {
            'descricao': 'Recebimento rateado',
            'tipo': LancamentoFinanceiro.TipoLancamento.RECEITA,
            'status': LancamentoFinanceiro.StatusLancamento.QUITADO,
            'data_competencia': '2026-03-10',
            'data_pagamento': '2026-03-10',
            'numero_documento': '100326-004',
            'pessoa': str(self.pessoa_recorrente.pk),
            'centro_custo': '',
            'conta': str(self.conta.pk),
            'conta_destino': '',
            'observacoes': '',
            'valor_total_documento': '130.00',
            'rateio_payload': json.dumps([
                {'id': str(lancamento_controlado.pk), 'categoria': str(self.categoria_controlada.pk), 'valor': '100.00'},
                {'id': str(lancamento_nao_controlado.pk), 'categoria': str(self.categoria_nao_controlada.pk), 'valor': '30.00'},
            ]),
            'competencias_rateio_payload': json.dumps({
                str(self.categoria_controlada.pk): [
                    {'mes': '1', 'ano': '2026', 'valor': '50.00'},
                    {'mes': '1', 'ano': '2026', 'valor': '50.00'},
                ],
            }),
        }
        form = LancamentoFinanceiroGrupoRateioForm(
            data=dados,
            instance=lancamento_controlado,
            grupo_lancamentos=[lancamento_controlado, lancamento_nao_controlado],
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            f'{self.categoria_controlada}: Ja existe uma competencia informada para este mes/ano. Agrupe o valor em uma unica linha.',
            form.errors['competencias_rateio_payload'],
        )
        self.assertNotIn(
            f'A soma das competencias deve ser igual ao valor controlado da subcategoria no rateio: {self.categoria_controlada}.',
            form.errors['competencias_rateio_payload'],
        )


class FrequenciaCompetenciasViewTests(TestCase):
    def setUp(self):
        self.conta = ContaFinanceira.objects.create(
            nome='Conta matriz',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
        )
        self.pessoa_joao = PessoaFinanceira.objects.create(
            codigo='P-MAT-001',
            nome='Joao Matriz',
            contribuinte_recorrente=True,
        )
        self.pessoa_maria = PessoaFinanceira.objects.create(
            codigo='P-MAT-002',
            nome='Maria Matriz',
            contribuinte_recorrente=True,
        )
        self.pessoa_sem_alocacao = PessoaFinanceira.objects.create(
            codigo='P-MAT-003',
            nome='Beatriz Sem Alocacao',
            contribuinte_recorrente=True,
        )
        self.pessoa_nao_recorrente = PessoaFinanceira.objects.create(
            codigo='P-MAT-004',
            nome='Carlos Avulso',
            contribuinte_recorrente=False,
        )
        self.categoria_receita_pai = CategoriaFinanceira.objects.create(
            nome='Receitas matriz',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
        )
        self.categoria_controlada_1 = CategoriaFinanceira.objects.create(
            nome='Contribuicao mensal matriz',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
            categoria_pai=self.categoria_receita_pai,
            controla_recorrencia_competencia=True,
        )
        self.categoria_controlada_2 = CategoriaFinanceira.objects.create(
            nome='Campanha recorrente matriz',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
            categoria_pai=self.categoria_receita_pai,
            controla_recorrencia_competencia=True,
        )
        self.categoria_nao_controlada = CategoriaFinanceira.objects.create(
            nome='Livro matriz',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
            categoria_pai=self.categoria_receita_pai,
            controla_recorrencia_competencia=False,
        )

        self._criar_lancamento_com_alocacao(
            pessoa=self.pessoa_joao,
            categoria=self.categoria_controlada_1,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            numero_documento='MAT-001',
            valor_lancamento='120.00',
            mes_competencia=1,
            ano_competencia=2026,
            valor_alocado='70.00',
            data_base=date(2026, 1, 5),
        )
        self._criar_lancamento_com_alocacao(
            pessoa=self.pessoa_joao,
            categoria=self.categoria_controlada_1,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            numero_documento='MAT-002',
            valor_lancamento='60.00',
            mes_competencia=1,
            ano_competencia=2026,
            valor_alocado='30.00',
            data_base=date(2026, 1, 15),
        )
        self._criar_lancamento_com_alocacao(
            pessoa=self.pessoa_joao,
            categoria=self.categoria_controlada_1,
            status=LancamentoFinanceiro.StatusLancamento.ABERTO,
            numero_documento='MAT-003',
            valor_lancamento='40.00',
            mes_competencia=2,
            ano_competencia=2026,
            valor_alocado='40.00',
            data_base=date(2026, 2, 10),
        )
        self._criar_lancamento_com_alocacao(
            pessoa=self.pessoa_maria,
            categoria=self.categoria_controlada_2,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            numero_documento='MAT-004',
            valor_lancamento='80.00',
            mes_competencia=2,
            ano_competencia=2026,
            valor_alocado='80.00',
            data_base=date(2026, 2, 14),
        )
        self.rateio_controlado = self._criar_lancamento_com_alocacao(
            pessoa=self.pessoa_joao,
            categoria=self.categoria_controlada_1,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            numero_documento='MAT-005',
            valor_lancamento='100.00',
            mes_competencia=3,
            ano_competencia=2026,
            valor_alocado='100.00',
            data_base=date(2026, 3, 20),
            com_rateio=True,
            grupo_rateio='grp-matriz',
        )
        LancamentoFinanceiro.objects.create(
            descricao='Receita rateada matriz',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('30.00'),
            data_competencia=date(2026, 3, 20),
            data_pagamento=date(2026, 3, 20),
            numero_documento='MAT-005',
            pessoa=self.pessoa_joao,
            categoria=self.categoria_nao_controlada,
            conta=self.conta,
            com_rateio=True,
            grupo_rateio='grp-matriz',
        )
        self._criar_lancamento_com_alocacao(
            pessoa=self.pessoa_nao_recorrente,
            categoria=self.categoria_controlada_1,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            numero_documento='MAT-006',
            valor_lancamento='90.00',
            mes_competencia=1,
            ano_competencia=2026,
            valor_alocado='90.00',
            data_base=date(2026, 1, 25),
        )

    def _criar_lancamento_com_alocacao(
        self,
        *,
        pessoa,
        categoria,
        status,
        numero_documento,
        valor_lancamento,
        mes_competencia,
        ano_competencia,
        valor_alocado,
        data_base,
        com_rateio=False,
        grupo_rateio='',
    ):
        lancamento = LancamentoFinanceiro.objects.create(
            descricao='Lancamento matriz',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=status,
            valor=Decimal(valor_lancamento),
            data_competencia=data_base,
            data_pagamento=data_base,
            numero_documento=numero_documento,
            pessoa=pessoa,
            categoria=categoria,
            conta=self.conta,
            com_rateio=com_rateio,
            grupo_rateio=grupo_rateio,
        )
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=lancamento,
            categoria=categoria,
            ano_competencia=ano_competencia,
            mes_competencia=mes_competencia,
            valor_alocado=Decimal(valor_alocado),
        )
        return lancamento

    def _garantir_permissao(self, codigo: str) -> PermissaoSistema:
        permissao = PermissaoSistema.objects.filter(codigo=codigo).first()
        if permissao:
            return permissao
        partes = codigo.split('.')
        modulo = partes[0] if len(partes) > 0 else 'financeiro'
        recurso = partes[1] if len(partes) > 1 else 'geral'
        acao = '.'.join(partes[2:]) if len(partes) > 2 else 'acessar'
        return PermissaoSistema.objects.create(
            codigo=codigo,
            nome=codigo,
            modulo=modulo,
            recurso=recurso,
            acao=acao,
            ativo=True,
        )

    def _login_com_permissoes(self, username: str, codigos_permissao: list[str]):
        user_model = get_user_model()
        usuario = user_model.objects.create_user(
            username=username,
            password='senha-forte-123',
            email=f'{username}@teste.local',
            is_active=True,
        )
        perfil = PerfilAcesso.objects.create(
            codigo=f'perfil-{username}',
            nome=f'Perfil {username}',
            ativo=True,
        )
        for codigo in codigos_permissao:
            perfil.permissoes.add(self._garantir_permissao(codigo))
        UsuarioPerfilAcesso.objects.create(usuario=usuario, perfil=perfil)
        self.client.force_login(usuario)

    def _parametros_base(self, **overrides):
        params = {
            'mes_inicial': '1',
            'ano_inicial': '2026',
            'mes_final': '3',
            'ano_final': '2026',
            'categoria': '',
            'status': 'todos',
        }
        params.update(overrides)
        return params

    def _linha_por_nome(self, response, nome: str):
        for linha in response.context['matriz_linhas']:
            if linha['pessoa'].nome == nome:
                return linha
        self.fail(f'Linha nao encontrada para {nome}.')

    def test_matriz_bloqueia_usuario_sem_permissao(self):
        self._login_com_permissoes('user-matriz-sem-permissao', ['financeiro.lancamentos.listar'])

        response = self.client.get(
            reverse('financeiro:frequencia-competencias'),
            self._parametros_base(),
        )

        self.assertEqual(response.status_code, 403)

    def test_matriz_permite_usuario_com_permissao_e_lista_recorrente_sem_alocacao(self):
        self._login_com_permissoes(
            'user-matriz-ok',
            ['financeiro.resumo_financeiro.visualizar'],
        )

        response = self.client.get(
            reverse('financeiro:frequencia-competencias'),
            self._parametros_base(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Joao Matriz')
        self.assertContains(response, 'Maria Matriz')
        self.assertContains(response, 'Beatriz Sem Alocacao')
        self.assertNotContains(response, 'Carlos Avulso')

    def test_matriz_abre_em_formato_com_valores_por_padrao(self):
        self._login_com_permissoes(
            'user-matriz-formato-padrao',
            ['financeiro.resumo_financeiro.visualizar'],
        )

        response = self.client.get(
            reverse('financeiro:frequencia-competencias'),
            self._parametros_base(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['formato_matriz'], 'valores')
        self.assertContains(response, 'Matriz mensal com valores')
        self.assertContains(response, 'R$ 100,00')

    def test_matriz_soma_alocacoes_por_competencia_e_ignora_item_nao_controlado(self):
        self._login_com_permissoes(
            'user-matriz-soma',
            ['financeiro.resumo_financeiro.visualizar'],
        )

        response = self.client.get(
            reverse('financeiro:frequencia-competencias'),
            self._parametros_base(),
        )

        self.assertEqual(response.status_code, 200)
        linha_joao = self._linha_por_nome(response, 'Joao Matriz')
        self.assertEqual(
            linha_joao['valores'],
            [Decimal('100.00'), Decimal('40.00'), Decimal('100.00')],
        )
        self.assertEqual(linha_joao['total'], Decimal('240.00'))
        self.assertNotContains(response, 'R$ 130,00')

    def test_matriz_gera_colunas_totais_e_total_geral_do_periodo(self):
        self._login_com_permissoes(
            'user-matriz-totais',
            ['financeiro.resumo_financeiro.visualizar'],
        )

        response = self.client.get(
            reverse('financeiro:frequencia-competencias'),
            self._parametros_base(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [coluna['label'] for coluna in response.context['competencias_colunas']],
            ['Jan/2026', 'Fev/2026', 'Mar/2026'],
        )
        self.assertEqual(
            response.context['totais_colunas'],
            [Decimal('100.00'), Decimal('120.00'), Decimal('100.00')],
        )
        self.assertEqual(response.context['total_geral'], Decimal('320.00'))

    def test_matriz_frequencia_exibe_indicadores_e_totais_por_ocorrencia(self):
        self._login_com_permissoes(
            'user-matriz-frequencia',
            ['financeiro.resumo_financeiro.visualizar'],
        )

        response = self.client.get(
            reverse('financeiro:frequencia-competencias'),
            self._parametros_base(formato_matriz='frequencia'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['formato_matriz'], 'frequencia')
        linha_joao = self._linha_por_nome(response, 'Joao Matriz')
        linha_maria = self._linha_por_nome(response, 'Maria Matriz')
        linha_beatriz = self._linha_por_nome(response, 'Beatriz Sem Alocacao')
        self.assertEqual(linha_joao['presencas'], [True, True, True])
        self.assertEqual(linha_joao['total_frequencia'], 3)
        self.assertEqual(linha_maria['presencas'], [False, True, False])
        self.assertEqual(linha_maria['total_frequencia'], 1)
        self.assertEqual(linha_beatriz['presencas'], [False, False, False])
        self.assertEqual(linha_beatriz['total_frequencia'], 0)
        self.assertEqual(response.context['totais_frequencia'], [1, 2, 1])
        self.assertEqual(response.context['total_geral_frequencia'], 4)
        self.assertContains(response, 'aria-label="Com contribuicao"', count=4)
        self.assertContains(response, 'aria-label="Sem contribuicao"', count=5)
        self.assertContains(response, '4 ocorrencias')

    def test_matriz_frequencia_respeita_filtros_de_status_categoria_e_periodo(self):
        self._login_com_permissoes(
            'user-matriz-frequencia-filtros',
            ['financeiro.resumo_financeiro.visualizar'],
        )

        response = self.client.get(
            reverse('financeiro:frequencia-competencias'),
            self._parametros_base(
                mes_inicial='2',
                ano_inicial='2026',
                mes_final='3',
                ano_final='2026',
                categoria=str(self.categoria_controlada_1.pk),
                status='quitado',
                formato_matriz='frequencia',
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [coluna['label'] for coluna in response.context['competencias_colunas']],
            ['Fev/2026', 'Mar/2026'],
        )
        linha_joao = self._linha_por_nome(response, 'Joao Matriz')
        linha_maria = self._linha_por_nome(response, 'Maria Matriz')
        linha_beatriz = self._linha_por_nome(response, 'Beatriz Sem Alocacao')
        self.assertEqual(linha_joao['presencas'], [False, True])
        self.assertEqual(linha_joao['total_frequencia'], 1)
        self.assertEqual(linha_maria['presencas'], [False, False])
        self.assertEqual(linha_beatriz['presencas'], [False, False])
        self.assertEqual(response.context['totais_frequencia'], [0, 1])
        self.assertEqual(response.context['total_geral_frequencia'], 1)

    def test_matriz_filtra_status_quitado_e_aberto(self):
        self._login_com_permissoes(
            'user-matriz-status',
            ['financeiro.resumo_financeiro.visualizar'],
        )

        response_quitado = self.client.get(
            reverse('financeiro:frequencia-competencias'),
            self._parametros_base(status='quitado'),
        )
        response_aberto = self.client.get(
            reverse('financeiro:frequencia-competencias'),
            self._parametros_base(status='aberto'),
        )

        self.assertEqual(response_quitado.status_code, 200)
        self.assertEqual(response_aberto.status_code, 200)
        self.assertEqual(
            self._linha_por_nome(response_quitado, 'Joao Matriz')['valores'],
            [Decimal('100.00'), Decimal('0.00'), Decimal('100.00')],
        )
        self.assertEqual(response_quitado.context['total_geral'], Decimal('280.00'))
        self.assertEqual(
            self._linha_por_nome(response_aberto, 'Joao Matriz')['valores'],
            [Decimal('0.00'), Decimal('40.00'), Decimal('0.00')],
        )
        self.assertEqual(response_aberto.context['total_geral'], Decimal('40.00'))

    def test_matriz_filtra_subcategoria_controlada_selecionada(self):
        self._login_com_permissoes(
            'user-matriz-categoria',
            ['financeiro.resumo_financeiro.visualizar'],
        )

        response = self.client.get(
            reverse('financeiro:frequencia-competencias'),
            self._parametros_base(categoria=str(self.categoria_controlada_1.pk)),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self._linha_por_nome(response, 'Maria Matriz')['valores'],
            [Decimal('0.00'), Decimal('0.00'), Decimal('0.00')],
        )
        self.assertEqual(response.context['total_geral'], Decimal('240.00'))


class LancamentoListagemAcoesTests(TestCase):
    def setUp(self):
        self.conta = ContaFinanceira.objects.create(
            nome='Conta listagem',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
        )
        self.pessoa = PessoaFinanceira.objects.create(
            codigo='P-LIST',
            nome='Favorecido listagem',
            contribuinte_recorrente=True,
        )
        self.categoria_receita_pai = CategoriaFinanceira.objects.create(
            nome='Receitas listagem',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
        )
        self.categoria_controlada = CategoriaFinanceira.objects.create(
            nome='Contribuicao listagem',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
            categoria_pai=self.categoria_receita_pai,
            controla_recorrencia_competencia=True,
        )
        self.categoria_nao_controlada = CategoriaFinanceira.objects.create(
            nome='Livro listagem',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
            categoria_pai=self.categoria_receita_pai,
            controla_recorrencia_competencia=False,
        )

        self.lancamento_simples = LancamentoFinanceiro.objects.create(
            descricao='Receita simples',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('80.00'),
            data_competencia=date(2026, 4, 1),
            data_pagamento=date(2026, 4, 1),
            numero_documento='LIST-001',
            pessoa=self.pessoa,
            categoria=self.categoria_nao_controlada,
            conta=self.conta,
        )
        self.lancamento_competencia = LancamentoFinanceiro.objects.create(
            descricao='Receita com competencia',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('100.00'),
            data_competencia=date(2026, 4, 2),
            data_pagamento=date(2026, 4, 2),
            numero_documento='LIST-002',
            pessoa=self.pessoa,
            categoria=self.categoria_controlada,
            conta=self.conta,
        )
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=self.lancamento_competencia,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=4,
            valor_alocado=Decimal('100.00'),
        )

        self.grupo_rateio = 'grp-list-acoes'
        self.rateio_controlado = LancamentoFinanceiro.objects.create(
            descricao='Receita rateada',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('100.00'),
            data_competencia=date(2026, 4, 3),
            data_pagamento=date(2026, 4, 3),
            numero_documento='LIST-003',
            pessoa=self.pessoa,
            categoria=self.categoria_controlada,
            conta=self.conta,
            com_rateio=True,
            grupo_rateio=self.grupo_rateio,
        )
        self.rateio_nao_controlado = LancamentoFinanceiro.objects.create(
            descricao='Receita rateada',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('30.00'),
            data_competencia=date(2026, 4, 3),
            data_pagamento=date(2026, 4, 3),
            numero_documento='LIST-003',
            pessoa=self.pessoa,
            categoria=self.categoria_nao_controlada,
            conta=self.conta,
            com_rateio=True,
            grupo_rateio=self.grupo_rateio,
        )
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=self.rateio_controlado,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=4,
            valor_alocado=Decimal('100.00'),
        )

    def _garantir_permissao(self, codigo: str) -> PermissaoSistema:
        permissao = PermissaoSistema.objects.filter(codigo=codigo).first()
        if permissao:
            return permissao
        partes = codigo.split('.')
        modulo = partes[0] if len(partes) > 0 else 'financeiro'
        recurso = partes[1] if len(partes) > 1 else 'geral'
        acao = '.'.join(partes[2:]) if len(partes) > 2 else 'acessar'
        return PermissaoSistema.objects.create(
            codigo=codigo,
            nome=codigo,
            modulo=modulo,
            recurso=recurso,
            acao=acao,
            ativo=True,
        )

    def _login_com_permissoes(self, username: str, codigos_permissao: list[str]):
        user_model = get_user_model()
        usuario = user_model.objects.create_user(
            username=username,
            password='senha-forte-123',
            email=f'{username}@teste.local',
            is_active=True,
        )
        perfil = PerfilAcesso.objects.create(
            codigo=f'perfil-{username}',
            nome=f'Perfil {username}',
            ativo=True,
        )
        for codigo in codigos_permissao:
            perfil.permissoes.add(self._garantir_permissao(codigo))
        UsuarioPerfilAcesso.objects.create(usuario=usuario, perfil=perfil)
        self.client.force_login(usuario)

    def test_listagem_exibe_acoes_completas_para_simples_competencia_e_rateio(self):
        self._login_com_permissoes(
            'user-acoes-completas',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.emitir_recibo',
                'financeiro.lancamentos.clonar',
                'financeiro.lancamentos.editar',
                'financeiro.lancamentos.editar_rateio',
                'financeiro.lancamentos.excluir',
            ],
        )

        response = self.client.get(reverse('financeiro:lancamento-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('financeiro:lancamento-recibo', kwargs={'pk': self.lancamento_simples.pk}))
        self.assertContains(response, reverse('financeiro:lancamento-delete', kwargs={'pk': self.lancamento_simples.pk}))
        self.assertContains(response, reverse('financeiro:lancamento-recibo', kwargs={'pk': self.lancamento_competencia.pk}))
        self.assertContains(response, reverse('financeiro:lancamento-delete', kwargs={'pk': self.lancamento_competencia.pk}))
        self.assertContains(
            response,
            reverse('financeiro:lancamento-rateio-update', kwargs={'grupo_rateio': self.grupo_rateio}),
        )
        self.assertContains(
            response,
            reverse('financeiro:lancamento-rateio-delete', kwargs={'grupo_rateio': self.grupo_rateio}),
        )
        ids_rateio_csv = ','.join(
            str(pk) for pk in sorted([self.rateio_controlado.pk, self.rateio_nao_controlado.pk])
        )
        self.assertContains(
            response,
            f'{reverse("financeiro:lancamento-recibos-por-favorecido")}?ids={ids_rateio_csv.replace(",", "%2C")}',
        )

    def test_listagem_sem_permissao_excluir_oculta_excluir_e_mantem_recibo(self):
        self._login_com_permissoes(
            'user-acoes-sem-excluir',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.emitir_recibo',
                'financeiro.lancamentos.clonar',
                'financeiro.lancamentos.editar',
                'financeiro.lancamentos.editar_rateio',
            ],
        )

        response = self.client.get(reverse('financeiro:lancamento-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('financeiro:lancamento-recibo', kwargs={'pk': self.lancamento_simples.pk}))
        self.assertContains(
            response,
            f'{reverse("financeiro:lancamento-recibos-por-favorecido")}?ids={self.rateio_controlado.pk}%2C{self.rateio_nao_controlado.pk}',
        )
        self.assertNotContains(response, reverse('financeiro:lancamento-delete', kwargs={'pk': self.lancamento_simples.pk}))
        self.assertNotContains(
            response,
            reverse('financeiro:lancamento-rateio-delete', kwargs={'grupo_rateio': self.grupo_rateio}),
        )

    def test_listagem_com_apenas_permissao_listar_abre_sem_recibo_ou_excluir(self):
        self._login_com_permissoes(
            'user-apenas-listar',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.clonar',
                'financeiro.lancamentos.editar',
                'financeiro.lancamentos.editar_rateio',
            ],
        )

        response = self.client.get(reverse('financeiro:lancamento-list'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse('financeiro:lancamento-recibo', kwargs={'pk': self.lancamento_simples.pk}))
        self.assertNotContains(response, reverse('financeiro:lancamento-delete', kwargs={'pk': self.lancamento_simples.pk}))
        self.assertNotContains(
            response,
            reverse('financeiro:lancamento-rateio-delete', kwargs={'grupo_rateio': self.grupo_rateio}),
        )

    def test_listagem_sem_permissao_listar_permanece_bloqueada(self):
        self._login_com_permissoes(
            'user-sem-listar',
            [
                'financeiro.lancamentos.emitir_recibo',
                'financeiro.lancamentos.clonar',
                'financeiro.lancamentos.editar',
                'financeiro.lancamentos.editar_rateio',
                'financeiro.lancamentos.excluir',
            ],
        )

        response = self.client.get(reverse('financeiro:lancamento-list'))

        self.assertEqual(response.status_code, 403)

    def test_exclusao_de_grupo_rateado_remove_linhas_e_competencias(self):
        self._login_com_permissoes(
            'user-rateio-delete',
            [
                'financeiro.lancamentos.excluir',
            ],
        )
        self.assertEqual(
            AlocacaoCompetenciaFinanceira.objects.filter(lancamento=self.rateio_controlado).count(),
            1,
        )

        response_get = self.client.get(
            reverse('financeiro:lancamento-rateio-delete', kwargs={'grupo_rateio': self.grupo_rateio})
        )
        self.assertEqual(response_get.status_code, 200)

        response = self.client.post(
            reverse('financeiro:lancamento-rateio-delete', kwargs={'grupo_rateio': self.grupo_rateio})
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            LancamentoFinanceiro.objects.filter(grupo_rateio=self.grupo_rateio).exists()
        )
        self.assertFalse(
            AlocacaoCompetenciaFinanceira.objects.filter(
                lancamento__grupo_rateio=self.grupo_rateio
            ).exists()
        )

    def test_exclusao_de_grupo_rateado_bloqueia_get_sem_permissao(self):
        self._login_com_permissoes(
            'user-rateio-sem-excluir',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.editar',
                'financeiro.lancamentos.editar_rateio',
            ],
        )

        response = self.client.get(
            reverse('financeiro:lancamento-rateio-delete', kwargs={'grupo_rateio': self.grupo_rateio})
        )

        self.assertEqual(response.status_code, 403)

    def test_exclusao_simples_continua_funcionando_com_mesma_permissao(self):
        self._login_com_permissoes(
            'user-delete-simples-ok',
            [
                'financeiro.lancamentos.excluir',
            ],
        )

        response_get = self.client.get(
            reverse('financeiro:lancamento-delete', kwargs={'pk': self.lancamento_simples.pk})
        )
        self.assertEqual(response_get.status_code, 200)
