import json
import re
from datetime import date
from decimal import Decimal
from io import BytesIO
from xml.etree import ElementTree
from zipfile import ZipFile

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
    ColunaPersonalizadaForm,
    ContaFinanceiraForm,
    LancamentoFinanceiroForm,
    LancamentoFinanceiroGrupoRateioForm,
    PessoaFinanceiraForm,
    TabelaPersonalizadaForm,
    TabelaPersonalizadaLinhaFiltroEstruturadoForm,
    TabelaPersonalizadaLinhaForm,
)
from .models import (
    AlocacaoCompetenciaFinanceira,
    AssinaturaInstitucional,
    AuditoriaFinanceiro,
    CategoriaFinanceira,
    ColunaPersonalizada,
    ContaFinanceira,
    LinhaTabelaPersonalizada,
    LancamentoFinanceiro,
    PessoaFinanceira,
    TabelaPersonalizada,
    TotalizadorColunaPersonalizada,
    TipoContaFinanceira,
    ValorTabelaPersonalizada,
)
from .permissoes import PermissoesTabelasPersonalizadas
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
    TabelaPersonalizadaColunaCreateView,
    TabelaPersonalizadaColunaListView,
    TabelaPersonalizadaColunaUpdateView,
    TabelaPersonalizadaCreateView,
    TabelaPersonalizadaLinhaCreateView,
    TabelaPersonalizadaLinhaExportXlsxView,
    TabelaPersonalizadaLinhaListView,
    TabelaPersonalizadaLinhaUpdateView,
    TabelaPersonalizadaListView,
    TabelaPersonalizadaUpdateView,
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

    def _build_get_request(self, path='/'):
        request = self.factory.get(path)
        request.user = type('UserStub', (), {'is_authenticated': False})()
        return request

    def _render_lancamento_form(self, form):
        request = self._build_get_request('/financeiro/lancamentos/novo/')
        return render_to_string(
            'financeiro/lancamento_form.html',
            {
                'form': form,
                'page_title': 'Novo Lancamento Financeiro',
                'cancel_url': '/financeiro/lancamentos/',
                'submit_label': 'Salvar',
                'allow_save_and_stay': False,
                'return_to': '',
                'save_and_stay_param': 'salvar_permanecer',
                'rateio_categoria_opcoes': [
                    {'id': self.categoria_controlada.pk, 'label': str(self.categoria_controlada), 'tipo': self.categoria_controlada.tipo},
                    {'id': self.categoria_nao_controlada.pk, 'label': str(self.categoria_nao_controlada), 'tipo': self.categoria_nao_controlada.tipo},
                ],
                'competencia_pessoas_recorrentes_ids': [self.pessoa_recorrente.pk],
                'competencia_categorias_controladas_ids': [self.categoria_controlada.pk],
                'request': request,
            },
            request=request,
        )

    def _render_rateio_form(self, form, grupo_rateio='grp-render'):
        request = self._build_get_request(f'/financeiro/lancamentos/rateio/{grupo_rateio}/editar/')
        return render_to_string(
            'financeiro/lancamento_rateio_grupo_form.html',
            {
                'form': form,
                'page_title': 'Editar Lancamento Financeiro',
                'submit_label': 'Atualizar',
                'cancel_url': '/financeiro/lancamentos/',
                'return_to': '',
                'grupo_rateio': grupo_rateio,
                'grupo_rateio_quantidade_linhas': len(form.grupo_lancamentos),
                'grupo_rateio_valor_total': '130,00',
                'grupo_rateio_linha_representativa': form.instance,
                'rateio_categoria_opcoes': [
                    {'id': self.categoria_controlada.pk, 'label': str(self.categoria_controlada), 'tipo': self.categoria_controlada.tipo},
                    {'id': self.categoria_nao_controlada.pk, 'label': str(self.categoria_nao_controlada), 'tipo': self.categoria_nao_controlada.tipo},
                ],
                'competencia_pessoas_recorrentes_ids': [self.pessoa_recorrente.pk],
                'competencia_categorias_controladas_ids': [self.categoria_controlada.pk],
                'request': request,
            },
            request=request,
        )

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

    def test_assistente_simples_exibe_11_meses_e_separa_ja_registrado_do_valor_do_lancamento(self):
        LancamentoFinanceiro.objects.create(
            descricao='Recebimento anterior',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('50.00'),
            data_competencia=date(2026, 1, 8),
            data_pagamento=date(2026, 1, 8),
            numero_documento='ANT-001',
            pessoa=self.pessoa_recorrente,
            categoria=self.categoria_controlada,
            conta=self.conta,
        )
        anterior = LancamentoFinanceiro.objects.get(numero_documento='ANT-001')
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=anterior,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=1,
            valor_alocado=Decimal('50.00'),
        )

        lancamento = self._criar_lancamento_controlado(valor='100.00')
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=lancamento,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=1,
            valor_alocado=Decimal('30.00'),
        )
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=lancamento,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=2,
            valor_alocado=Decimal('70.00'),
        )

        form = LancamentoFinanceiroForm(instance=lancamento)
        janeiro = next(
            mes for mes in form.assistente_competencia_meses_sugeridos
            if mes['ano'] == 2026 and mes['mes'] == 1
        )

        self.assertEqual(len(form.assistente_competencia_meses_sugeridos), 11)
        self.assertTrue(form.assistente_competencia_bloco_visivel)
        self.assertEqual(janeiro['ja_registrado'], '50.00')
        self.assertEqual(janeiro['valor_lancamento'], '30.00')

    def test_assistente_simples_aparece_na_edicao_sem_competencias_para_regularizacao(self):
        lancamento = self._criar_lancamento_controlado()

        form = LancamentoFinanceiroForm(instance=lancamento)

        self.assertTrue(form.assistente_competencia_bloco_visivel)
        self.assertEqual(len(form.assistente_competencia_meses_sugeridos), 11)
        self.assertTrue(all(not item['valor_lancamento'] for item in form.assistente_competencia_meses_sugeridos))

    def test_assistente_simples_nao_aparece_para_favorecido_nao_recorrente(self):
        lancamento = LancamentoFinanceiro.objects.create(
            descricao='Recebimento avulso',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('100.00'),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            numero_documento='AVULSO-001',
            pessoa=self.pessoa_avulsa,
            categoria=self.categoria_controlada,
            conta=self.conta,
        )

        form = LancamentoFinanceiroForm(instance=lancamento)

        self.assertFalse(form.assistente_competencia_bloco_visivel)

    def test_assistente_simples_nao_aparece_para_subcategoria_nao_controlada(self):
        lancamento = LancamentoFinanceiro.objects.create(
            descricao='Recebimento sem controle',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('100.00'),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            numero_documento='LIVRO-001',
            pessoa=self.pessoa_recorrente,
            categoria=self.categoria_nao_controlada,
            conta=self.conta,
        )

        form = LancamentoFinanceiroForm(instance=lancamento)

        self.assertFalse(form.assistente_competencia_bloco_visivel)

    def test_template_lancamento_form_exibe_rotulos_do_assistente(self):
        lancamento = self._criar_lancamento_controlado()
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=lancamento,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=1,
            valor_alocado=Decimal('100.00'),
        )
        form = LancamentoFinanceiroForm(instance=lancamento)

        html = self._render_lancamento_form(form)

        self.assertIn('Assistente de competencias', html)
        self.assertIn('financeiro-competencia-assistente-table', html)
        self.assertIn('Mes', html)
        self.assertIn('Situacao', html)
        self.assertIn('Ja registrado', html)
        self.assertIn('Valor deste lancamento', html)
        self.assertIn(
            'Distribua o valor total entre as competencias. A soma informada deve fechar com o valor do lancamento.',
            html,
        )
        self.assertIn('financeiro-competencia-assistente-status', html)
        self.assertIn('Ja possui contribuicao', html)
        self.assertIn('Sem quitacao registrada', html)
        self.assertIn('name="competencias_payload"', html)
        self.assertIn('data-financeiro-competencia-body="true"', html)
        self.assertIn('financeiro-competencia-assistente-grid', html)

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

    def test_assistente_rateio_exibe_ja_registrado_e_valor_do_grupo_atual_separadamente(self):
        anterior = LancamentoFinanceiro.objects.create(
            descricao='Recebimento anterior',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('50.00'),
            data_competencia=date(2026, 1, 12),
            data_pagamento=date(2026, 1, 12),
            numero_documento='RATEIO-ANT',
            pessoa=self.pessoa_recorrente,
            categoria=self.categoria_controlada,
            conta=self.conta,
        )
        AlocacaoCompetenciaFinanceira.objects.create(
            lancamento=anterior,
            categoria=self.categoria_controlada,
            ano_competencia=2026,
            mes_competencia=1,
            valor_alocado=Decimal('50.00'),
        )

        grupo_rateio = 'grp-assistente'
        lancamento_controlado = LancamentoFinanceiro.objects.create(
            descricao='Recebimento rateado',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('100.00'),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            numero_documento='100326-777',
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
            numero_documento='100326-777',
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
            valor_alocado=Decimal('30.00'),
        )

        form = LancamentoFinanceiroGrupoRateioForm(
            instance=lancamento_controlado,
            grupo_lancamentos=[lancamento_controlado, lancamento_nao_controlado],
        )
        janeiro = next(
            mes for mes in form.assistente_competencia_rateio_grupos_iniciais[0]['meses']
            if mes['ano'] == 2026 and mes['mes'] == 1
        )

        self.assertEqual(janeiro['ja_registrado'], '50.00')
        self.assertEqual(janeiro['valor_lancamento'], '30.00')

    def test_assistente_rateio_exibe_grupo_apenas_para_subcategoria_controlada(self):
        grupo_rateio = 'grp-assistente-controlada'
        lancamento_controlado = LancamentoFinanceiro.objects.create(
            descricao='Recebimento rateado',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('100.00'),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            numero_documento='100326-778',
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
            numero_documento='100326-778',
            pessoa=self.pessoa_recorrente,
            categoria=self.categoria_nao_controlada,
            conta=self.conta,
            com_rateio=True,
            grupo_rateio=grupo_rateio,
        )

        form = LancamentoFinanceiroGrupoRateioForm(
            instance=lancamento_controlado,
            grupo_lancamentos=[lancamento_controlado, lancamento_nao_controlado],
        )

        self.assertEqual(len(form.assistente_competencia_rateio_grupos_iniciais), 1)
        self.assertEqual(
            form.assistente_competencia_rateio_grupos_iniciais[0]['categoria_id'],
            str(self.categoria_controlada.pk),
        )

    def test_template_rateio_grupo_exibe_rotulos_do_assistente(self):
        grupo_rateio = 'grp-template'
        lancamento_controlado = LancamentoFinanceiro.objects.create(
            descricao='Recebimento rateado',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('100.00'),
            data_competencia=date(2026, 3, 10),
            data_pagamento=date(2026, 3, 10),
            numero_documento='100326-991',
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
            numero_documento='100326-991',
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
        form = LancamentoFinanceiroGrupoRateioForm(
            instance=lancamento_controlado,
            grupo_lancamentos=[lancamento_controlado, lancamento_nao_controlado],
        )

        html = self._render_rateio_form(form, grupo_rateio=grupo_rateio)

        self.assertIn('Assistente de competencias', html)
        self.assertIn('financeiro-competencia-assistente-table', html)
        self.assertIn('Mes', html)
        self.assertIn('Situacao', html)
        self.assertIn('Ja registrado', html)
        self.assertIn('Valor deste lancamento', html)
        self.assertIn(
            'Distribua o valor da subcategoria entre as competencias. A soma informada deve fechar com o valor da subcategoria.',
            html,
        )
        self.assertIn('financeiro-competencia-assistente-status', html)
        self.assertIn('Ja possui contribuicao', html)
        self.assertIn('Sem quitacao registrada', html)
        self.assertIn('financeiro-rateio-grupo-competencias-registradas', html)

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

    def test_matriz_exibe_acao_de_impressao_e_css_local_de_print(self):
        self._login_com_permissoes(
            'user-matriz-print',
            ['financeiro.resumo_financeiro.visualizar'],
        )

        response = self.client.get(
            reverse('financeiro:frequencia-competencias'),
            self._parametros_base(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'onclick="window.print()"')
        self.assertContains(response, '>Imprimir<', html=False)
        self.assertContains(response, 'financeiro-frequencia-hero no-print')
        self.assertContains(response, 'financeiro-frequencia-panel is-filters no-print')
        self.assertContains(response, '@media print')
        self.assertContains(response, 'size: A4 landscape;')
        self.assertContains(response, 'financeiro-document-header only-print')
        self.assertContains(response, 'financeiro-frequencia-th-print-label')
        self.assertContains(response, 'financeiro-frequencia-col-person')
        self.assertContains(response, 'text-overflow: ellipsis;')
        self.assertContains(response, 'word-break: normal !important;')
        self.assertContains(response, '-webkit-print-color-adjust: exact;')
        self.assertContains(response, 'print-color-adjust: exact;')
        self.assertContains(response, 'financeiro-frequencia-indicator-positive')
        self.assertContains(response, 'financeiro-frequencia-indicator-negative')

    def test_matriz_impressao_traz_cabecalho_e_metadados_essenciais(self):
        self._login_com_permissoes(
            'user-matriz-print-meta',
            ['financeiro.resumo_financeiro.visualizar'],
        )

        response = self.client.get(
            reverse('financeiro:frequencia-competencias'),
            self._parametros_base(formato_matriz='frequencia'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Frequencia por competencia')
        self.assertContains(response, 'financeiro-document-meta-label">Periodo')
        self.assertContains(response, 'Jan/2026 a Mar/2026')
        self.assertContains(response, 'financeiro-document-meta-label">Subcategoria')
        self.assertContains(response, 'Todas controladas')
        self.assertContains(response, 'financeiro-document-meta-label">Emitido em')
        self.assertNotContains(response, 'financeiro-document-meta-label">Formato')
        self.assertNotContains(response, 'financeiro-document-meta-label">Status')

    def test_matriz_impressao_exibe_nome_da_subcategoria_quando_filtrada(self):
        self._login_com_permissoes(
            'user-matriz-print-subcategoria',
            ['financeiro.resumo_financeiro.visualizar'],
        )

        response = self.client.get(
            reverse('financeiro:frequencia-competencias'),
            self._parametros_base(categoria=str(self.categoria_controlada_2.pk)),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Campanha recorrente matriz')
        self.assertContains(response, 'financeiro-document-meta-label">Subcategoria')
        self.assertNotContains(response, 'financeiro-document-meta-value">Todas controladas')
        self.assertNotContains(response, 'financeiro-document-meta-label">Formato')
        self.assertNotContains(response, 'financeiro-document-meta-label">Status')

    def test_matriz_impressao_usa_labels_compactos_para_competencias(self):
        self._login_com_permissoes(
            'user-matriz-print-labels',
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
            [coluna['label_print'] for coluna in response.context['competencias_colunas']],
            ['01/2026', '02/2026', '03/2026'],
        )
        self.assertContains(response, '<span class="financeiro-frequencia-th-screen-label">Jan/2026</span>')
        self.assertContains(response, '<span class="financeiro-frequencia-th-print-label">01/2026</span>')

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


class LancamentoReciboEspecialTests(TestCase):
    def setUp(self):
        self.conta = ContaFinanceira.objects.create(
            nome='Conta recibo especial',
            saldo_inicial=Decimal('10.00'),
            data_saldo_inicial=date(2026, 1, 1),
        )
        self.pessoa_maria = PessoaFinanceira.objects.create(
            codigo='P-MARIA-REC',
            nome='Maria Silva',
            contribuinte_recorrente=True,
        )
        self.pessoa_joao = PessoaFinanceira.objects.create(
            codigo='P-JOAO-REC',
            nome='Joao Souza',
            contribuinte_recorrente=True,
        )
        self.destinatario_manual = PessoaFinanceira.objects.create(
            codigo='P-DEST-REC',
            nome='Favorecido Destinatario',
            contribuinte_recorrente=False,
        )
        self.categoria_receita = CategoriaFinanceira.objects.create(
            nome='Receita recibo especial',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
        )
        self.subcategoria_receita = CategoriaFinanceira.objects.create(
            nome='Subcategoria receita recibo especial',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
            categoria_pai=self.categoria_receita,
        )
        self.categoria_despesa = CategoriaFinanceira.objects.create(
            nome='Despesa recibo especial',
            tipo=CategoriaFinanceira.TipoCategoria.DESPESA,
        )
        self.subcategoria_despesa = CategoriaFinanceira.objects.create(
            nome='Subcategoria despesa recibo especial',
            tipo=CategoriaFinanceira.TipoCategoria.DESPESA,
            categoria_pai=self.categoria_despesa,
        )
        self.receita_maria = LancamentoFinanceiro.objects.create(
            descricao='Pagamento de cesta basica',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('120.00'),
            data_competencia=date(2026, 2, 10),
            data_pagamento=date(2026, 2, 10),
            numero_documento='REC-ESP-001',
            pessoa=self.pessoa_maria,
            categoria=self.subcategoria_receita,
            conta=self.conta,
        )
        self.receita_joao = LancamentoFinanceiro.objects.create(
            descricao='Pagamento de cesta basica',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('80.00'),
            data_competencia=date(2026, 3, 11),
            data_pagamento=date(2026, 3, 11),
            numero_documento='REC-ESP-002',
            pessoa=self.pessoa_joao,
            categoria=self.subcategoria_receita,
            conta=self.conta,
        )
        self.receita_sem_favorecido = LancamentoFinanceiro.objects.create(
            descricao='Receita sem favorecido',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('30.00'),
            data_competencia=date(2026, 3, 12),
            data_pagamento=date(2026, 3, 12),
            numero_documento='REC-ESP-003',
            pessoa=self.pessoa_maria,
            categoria=self.subcategoria_receita,
            conta=self.conta,
        )
        LancamentoFinanceiro.objects.filter(pk=self.receita_sem_favorecido.pk).update(pessoa=None)
        self.receita_sem_favorecido.refresh_from_db()
        self.despesa_maria = LancamentoFinanceiro.objects.create(
            descricao='Despesa diversa',
            tipo=LancamentoFinanceiro.TipoLancamento.DESPESA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('45.00'),
            data_competencia=date(2026, 3, 13),
            data_pagamento=date(2026, 3, 13),
            numero_documento='REC-ESP-004',
            pessoa=self.pessoa_maria,
            categoria=self.subcategoria_despesa,
            conta=self.conta,
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

    def test_listagem_exibe_recibo_especial_apenas_com_permissao(self):
        self._login_com_permissoes(
            'user-recibo-especial-ok',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.emitir_recibo',
            ],
        )
        response = self.client.get(reverse('financeiro:lancamento-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Recibo especial')

    def test_listagem_sem_permissao_emitir_recibo_oculta_recibo_especial(self):
        self._login_com_permissoes(
            'user-recibo-especial-sem-permissao',
            [
                'financeiro.lancamentos.listar',
            ],
        )
        response = self.client.get(reverse('financeiro:lancamento-list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Recibo especial')

    def test_fluxo_recibo_especial_bloqueia_usuario_sem_permissao(self):
        self._login_com_permissoes(
            'user-recibo-especial-bloqueado',
            [
                'financeiro.lancamentos.listar',
            ],
        )
        ids = f'{self.receita_maria.pk},{self.receita_joao.pk}'
        response = self.client.get(
            reverse('financeiro:lancamento-recibo-especial-selecionar-favorecido'),
            {'ids': ids},
        )
        self.assertEqual(response.status_code, 403)
        response_final = self.client.get(
            reverse('financeiro:lancamento-recibo-especial'),
            {'ids': ids, 'destinatario': self.destinatario_manual.pk},
        )
        self.assertEqual(response_final.status_code, 403)

    def test_recibo_especial_bloqueia_selecao_vazia(self):
        self._login_com_permissoes(
            'user-recibo-especial-vazio',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.emitir_recibo',
            ],
        )
        response = self.client.post(
            reverse('financeiro:lancamento-acoes-lote'),
            {
                'acao_lote': 'recibo_especial',
                'filtros_retorno': '',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        mensagens = [str(message) for message in response.context['messages']]
        self.assertTrue(any('Selecione pelo menos um' in mensagem for mensagem in mensagens))

    def test_recibo_especial_bloqueia_lancamento_sem_favorecido(self):
        self._login_com_permissoes(
            'user-recibo-especial-sem-favorecido',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.emitir_recibo',
            ],
        )
        response = self.client.post(
            reverse('financeiro:lancamento-acoes-lote'),
            {
                'acao_lote': 'recibo_especial',
                'lancamentos_selecionados': [str(self.receita_sem_favorecido.pk)],
                'filtros_retorno': '',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Recibo especial exige lancamentos com favorecido.')

    def test_recibo_especial_bloqueia_lancamento_que_nao_e_receita(self):
        self._login_com_permissoes(
            'user-recibo-especial-despesa',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.emitir_recibo',
            ],
        )
        response = self.client.post(
            reverse('financeiro:lancamento-acoes-lote'),
            {
                'acao_lote': 'recibo_especial',
                'lancamentos_selecionados': [str(self.despesa_maria.pk)],
                'filtros_retorno': '',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Recibo especial so pode ser emitido para lancamentos do tipo receita.')

    def test_recibo_especial_aceita_multiplos_favorecidos(self):
        self._login_com_permissoes(
            'user-recibo-especial-multiplos',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.emitir_recibo',
            ],
        )
        response = self.client.post(
            reverse('financeiro:lancamento-acoes-lote'),
            {
                'acao_lote': 'recibo_especial',
                'lancamentos_selecionados': [str(self.receita_maria.pk), str(self.receita_joao.pk)],
                'filtros_retorno': 'status=quitado',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('financeiro:lancamento-recibo-especial-selecionar-favorecido'), response['Location'])
        self.assertIn(f'ids={self.receita_maria.pk}%2C{self.receita_joao.pk}', response['Location'])

    def test_recibo_especial_exige_favorecido_destinatario_manual(self):
        self._login_com_permissoes(
            'user-recibo-especial-form',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.emitir_recibo',
            ],
        )
        ids = f'{self.receita_maria.pk},{self.receita_joao.pk}'
        response = self.client.post(
            reverse('financeiro:lancamento-recibo-especial-selecionar-favorecido'),
            {'ids': ids, 'filtros': ''},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('favorecido_destinatario', response.context['form'].errors)

    def test_form_recibo_especial_exibe_apenas_campo_pesquisavel_visivel(self):
        self._login_com_permissoes(
            'user-recibo-especial-form-campo-pesquisa',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.emitir_recibo',
            ],
        )
        ids = f'{self.receita_maria.pk},{self.receita_joao.pk}'
        response = self.client.get(
            reverse('financeiro:lancamento-recibo-especial-selecionar-favorecido'),
            {'ids': ids, 'filtros': ''},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="recibo-especial-favorecido-search"')
        self.assertContains(response, 'recibo-especial-form-select-hidden')
        self.assertContains(response, 'id="recibo-especial-favorecido-results"')
        self.assertContains(response, 'id="recibo-especial-favorecido-search-error"')

    def test_recibo_especial_bloqueia_favorecido_destinatario_inexistente(self):
        self._login_com_permissoes(
            'user-recibo-especial-destinatario-invalido',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.emitir_recibo',
            ],
        )
        ids = f'{self.receita_maria.pk},{self.receita_joao.pk}'
        response = self.client.post(
            reverse('financeiro:lancamento-recibo-especial-selecionar-favorecido'),
            {
                'ids': ids,
                'filtros': '',
                'favorecido_destinatario': '999999',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('favorecido_destinatario', response.context['form'].errors)

    def test_recibo_especial_final_usa_destinatario_manual_e_descricao_composta(self):
        self._login_com_permissoes(
            'user-recibo-especial-final',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.emitir_recibo',
            ],
        )
        ids = f'{self.receita_maria.pk},{self.receita_joao.pk}'
        response = self.client.get(
            reverse('financeiro:lancamento-recibo-especial'),
            {
                'ids': ids,
                'destinatario': self.destinatario_manual.pk,
                'filtros': 'status=quitado',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'RECIBO')
        self.assertNotContains(response, 'RECIBO ESPECIAL')
        self.assertContains(response, self.destinatario_manual.nome)
        self.assertContains(response, 'Pagamento de cesta basica - Maria Silva')
        self.assertContains(response, 'Pagamento de cesta basica - Joao Souza')
        self.assertContains(response, 'A importância de')
        self.assertContains(response, 'lançamentos listados abaixo')
        self.assertContains(response, 'Descrição')
        self.assertNotContains(response, 'destinatario manual')
        self.assertNotContains(
            response,
            'Documento especial em lote com destinatario principal escolhido manualmente, sem alterar os lancamentos originais.',
        )
        self.assertNotContains(response, 'Favorecido original')
        self.receita_maria.refresh_from_db()
        self.receita_joao.refresh_from_db()
        self.conta.refresh_from_db()
        self.assertEqual(self.receita_maria.pessoa_id, self.pessoa_maria.pk)
        self.assertEqual(self.receita_joao.pessoa_id, self.pessoa_joao.pk)
        self.assertEqual(self.conta.saldo_inicial, Decimal('10.00'))

    def test_recibo_em_lote_atual_continua_exigindo_mesmo_favorecido(self):
        self._login_com_permissoes(
            'user-recibo-lote-atual',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.emitir_recibo',
            ],
        )
        ids = f'{self.receita_maria.pk},{self.receita_joao.pk}'
        response = self.client.get(
            reverse('financeiro:lancamento-recibo-lote'),
            {'ids': ids},
        )
        self.assertEqual(response.status_code, 302)

    def test_recibos_por_favorecido_atuais_continuam_agrupando_por_favorecido(self):
        self._login_com_permissoes(
            'user-recibos-por-favorecido-atual',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.emitir_recibo',
            ],
        )
        ids = f'{self.receita_maria.pk},{self.receita_joao.pk}'
        response = self.client.get(
            reverse('financeiro:lancamento-recibos-por-favorecido'),
            {'ids': ids},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['recibo_grupos']), 2)
        self.assertContains(response, self.pessoa_maria.nome)
        self.assertContains(response, self.pessoa_joao.nome)

    def test_termo_anual_permanece_com_mesma_rota_e_template(self):
        self._login_com_permissoes(
            'user-termo-anual-sem-regressao',
            [
                'financeiro.lancamentos.listar',
                'financeiro.lancamentos.emitir_recibo',
            ],
        )
        response = self.client.get(
            reverse('financeiro:lancamento-termo-anual-quitacao'),
            {
                'data_inicial': '2026-02-01',
                'data_final': '2026-03-31',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'financeiro/lancamento_documentos_por_favorecido.html')


class TabelasPersonalizadasEstruturaBaseTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester_tabelas',
            password='segredo123',
        )
        self.tabela = TabelaPersonalizada.objects.create(
            nome='Controle interno',
            descricao='Tabela base de teste',
            criado_por=self.user,
            atualizado_por=self.user,
        )

    def test_cria_tabela_personalizada(self):
        self.assertEqual(self.tabela.status, TabelaPersonalizada.StatusTabela.ATIVA)
        self.assertEqual(self.tabela.nome, 'Controle interno')
        self.assertEqual(self.tabela.criado_por, self.user)

    def test_status_choices_validos_da_tabela(self):
        self.assertEqual(
            {valor for valor, _rotulo in TabelaPersonalizada.StatusTabela.choices},
            {'ativa', 'inativa', 'arquivada'},
        )

    def test_bloqueia_nome_duplicado_de_tabela_nao_arquivada(self):
        duplicada = TabelaPersonalizada(
            nome=' controle   interno ',
            status=TabelaPersonalizada.StatusTabela.INATIVA,
        )

        with self.assertRaises(ValidationError):
            duplicada.full_clean()

    def test_cria_coluna_com_tipo_permitido(self):
        coluna = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Valor previsto',
            tipo_dado=ColunaPersonalizada.TipoDado.DECIMAL,
        )

        self.assertEqual(coluna.tipo_dado, ColunaPersonalizada.TipoDado.DECIMAL)
        self.assertFalse(coluna.calculada)

    def test_bloqueia_coluna_com_tipo_invalido(self):
        coluna = ColunaPersonalizada(
            tabela=self.tabela,
            nome='Campo invalido',
            tipo_dado='tipo_livre',
        )

        with self.assertRaises(ValidationError):
            coluna.full_clean()

    def test_bloqueia_coluna_duplicada_na_mesma_tabela(self):
        ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Observacao',
            tipo_dado=ColunaPersonalizada.TipoDado.TEXTO_CURTO,
        )
        duplicada = ColunaPersonalizada(
            tabela=self.tabela,
            nome=' observacao ',
            tipo_dado=ColunaPersonalizada.TipoDado.TEXTO_LONGO,
        )

        with self.assertRaises(ValidationError):
            duplicada.full_clean()

    def test_coluna_calculada_exige_tipo_formula_controlada(self):
        coluna = ColunaPersonalizada(
            tabela=self.tabela,
            nome='Total calculado',
            tipo_dado=ColunaPersonalizada.TipoDado.DECIMAL,
            calculada=True,
        )

        with self.assertRaises(ValidationError):
            coluna.full_clean()

    def test_cria_linha_tabela_personalizada(self):
        linha = LinhaTabelaPersonalizada.objects.create(
            tabela=self.tabela,
            criado_por=self.user,
            atualizado_por=self.user,
        )

        self.assertEqual(linha.status, LinhaTabelaPersonalizada.StatusLinha.ATIVA)
        self.assertEqual(linha.tabela, self.tabela)

    def test_cria_valor_tabela_personalizada(self):
        coluna = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Descricao',
            tipo_dado=ColunaPersonalizada.TipoDado.TEXTO_CURTO,
        )
        linha = LinhaTabelaPersonalizada.objects.create(tabela=self.tabela)

        valor = ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=coluna,
            valor_texto='Linha inicial',
        )

        self.assertEqual(valor.valor_texto, 'Linha inicial')
        self.assertEqual(valor.coluna, coluna)

    def test_bloqueia_valor_quando_coluna_e_de_outra_tabela(self):
        outra_tabela = TabelaPersonalizada.objects.create(nome='Outro controle')
        coluna_outra_tabela = ColunaPersonalizada.objects.create(
            tabela=outra_tabela,
            nome='Descricao',
            tipo_dado=ColunaPersonalizada.TipoDado.TEXTO_CURTO,
        )
        linha = LinhaTabelaPersonalizada.objects.create(tabela=self.tabela)

        valor = ValorTabelaPersonalizada(
            linha=linha,
            coluna=coluna_outra_tabela,
            valor_texto='Invalido',
        )

        with self.assertRaises(ValidationError):
            valor.full_clean()

    def test_bloqueia_unicidade_linha_coluna(self):
        coluna = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Descricao',
            tipo_dado=ColunaPersonalizada.TipoDado.TEXTO_CURTO,
        )
        linha = LinhaTabelaPersonalizada.objects.create(tabela=self.tabela)
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=coluna,
            valor_texto='Primeiro valor',
        )

        duplicado = ValorTabelaPersonalizada(
            linha=linha,
            coluna=coluna,
            valor_texto='Segundo valor',
        )

        with self.assertRaises(ValidationError):
            duplicado.full_clean()

    def test_valida_slot_basico_conforme_tipo(self):
        coluna = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Quantidade',
            tipo_dado=ColunaPersonalizada.TipoDado.INTEIRO,
        )
        linha = LinhaTabelaPersonalizada.objects.create(tabela=self.tabela)
        valor = ValorTabelaPersonalizada(
            linha=linha,
            coluna=coluna,
            valor_texto='10',
        )

        with self.assertRaises(ValidationError):
            valor.full_clean()

    def test_coluna_calculada_bloqueia_valor_manual(self):
        coluna_origem_a = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Origem inteira',
            tipo_dado=ColunaPersonalizada.TipoDado.INTEIRO,
            visivel=True,
        )
        coluna_origem_b = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Origem decimal',
            tipo_dado=ColunaPersonalizada.TipoDado.DECIMAL,
            visivel=True,
        )
        coluna = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Total',
            tipo_dado=ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA,
            calculada=True,
            configuracao_json={
                'formula': {
                    'habilitada': True,
                    'operacao': ColunaPersonalizada.OperacaoFormula.SOMA,
                    'operandos': [coluna_origem_a.pk, coluna_origem_b.pk],
                    'resultado_tipo': ColunaPersonalizada.TipoDado.DECIMAL,
                    'casas_decimais': 8,
                }
            },
        )
        linha = LinhaTabelaPersonalizada.objects.create(tabela=self.tabela)
        valor = ValorTabelaPersonalizada(
            linha=linha,
            coluna=coluna,
            valor_texto='123',
        )

        with self.assertRaises(ValidationError):
            valor.full_clean()

    def test_cria_totalizador_valido_para_coluna_numerica(self):
        coluna = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Valor previsto',
            tipo_dado=ColunaPersonalizada.TipoDado.DECIMAL,
        )

        totalizador = TotalizadorColunaPersonalizada.objects.create(
            coluna=coluna,
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )

        self.assertEqual(totalizador.coluna, coluna)
        self.assertTrue(totalizador.ativo)

    def test_bloqueia_totalizador_incompativel_com_tipo_da_coluna(self):
        coluna = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Descricao livre',
            tipo_dado=ColunaPersonalizada.TipoDado.TEXTO_CURTO,
        )
        totalizador = TotalizadorColunaPersonalizada(
            coluna=coluna,
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )

        with self.assertRaises(ValidationError):
            totalizador.full_clean()

    def test_compatibilidade_de_totalizadores_por_tipo(self):
        self.assertEqual(
            set(TotalizadorColunaPersonalizada.tipos_compativeis_por_tipo_dado(ColunaPersonalizada.TipoDado.TEXTO_CURTO)),
            {TotalizadorColunaPersonalizada.TipoTotalizador.CONTAGEM},
        )
        self.assertEqual(
            set(TotalizadorColunaPersonalizada.tipos_compativeis_por_tipo_dado(ColunaPersonalizada.TipoDado.BOOLEANO)),
            {TotalizadorColunaPersonalizada.TipoTotalizador.CONTAGEM},
        )
        self.assertEqual(
            set(TotalizadorColunaPersonalizada.tipos_compativeis_por_tipo_dado(ColunaPersonalizada.TipoDado.LISTA_OPCOES)),
            {TotalizadorColunaPersonalizada.TipoTotalizador.CONTAGEM},
        )
        self.assertEqual(
            set(TotalizadorColunaPersonalizada.tipos_compativeis_por_tipo_dado(ColunaPersonalizada.TipoDado.DATA)),
            {
                TotalizadorColunaPersonalizada.TipoTotalizador.MINIMO,
                TotalizadorColunaPersonalizada.TipoTotalizador.MAXIMO,
                TotalizadorColunaPersonalizada.TipoTotalizador.CONTAGEM,
            },
        )

    def test_lancamento_financeiro_existente_permanece_funcional(self):
        conta = ContaFinanceira.objects.create(
            nome='Conta operacional teste',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 1, 1),
        )
        pessoa = PessoaFinanceira.objects.create(codigo='TP001', nome='Pessoa teste tabelas')
        categoria_pai = CategoriaFinanceira.objects.create(
            nome='Receitas teste tabelas',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
        )
        categoria = CategoriaFinanceira.objects.create(
            nome='Doacao teste tabelas',
            tipo=CategoriaFinanceira.TipoCategoria.RECEITA,
            categoria_pai=categoria_pai,
        )

        lancamento = LancamentoFinanceiro.objects.create(
            descricao='Lancamento preservado',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('25.00'),
            data_competencia=date(2026, 5, 1),
            data_pagamento=date(2026, 5, 1),
            pessoa=pessoa,
            categoria=categoria,
            conta=conta,
        )

        self.assertEqual(lancamento.descricao, 'Lancamento preservado')


class TabelasPersonalizadasListViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester_tabelas_list',
            password='segredo123',
            is_active=True,
        )
        self.tabela = TabelaPersonalizada.objects.create(
            nome='Controle de almoxarifado',
            descricao='Controle interno sem impacto em lancamentos oficiais.',
            criado_por=self.user,
            atualizado_por=self.user,
        )
        ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Item',
            tipo_dado=ColunaPersonalizada.TipoDado.TEXTO_CURTO,
        )
        ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Quantidade',
            tipo_dado=ColunaPersonalizada.TipoDado.INTEIRO,
        )
        LinhaTabelaPersonalizada.objects.create(
            tabela=self.tabela,
            criado_por=self.user,
            atualizado_por=self.user,
        )
        self.outra_tabela = TabelaPersonalizada.objects.create(
            nome='Controle paralelo',
            descricao='Tabela separada para validar isolamento.',
            criado_por=self.user,
            atualizado_por=self.user,
        )
        self.coluna_existente = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Observacao interna',
            tipo_dado=ColunaPersonalizada.TipoDado.TEXTO_LONGO,
            obrigatoria=False,
            visivel=True,
            ordem=3,
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
        return usuario

    def _auditorias_modelo(self, modelo: str):
        return AuditoriaFinanceiro.objects.filter(modelo=modelo).order_by('-pk')

    def _ultimo_log_modelo(self, modelo: str, registro_id: int | None = None):
        queryset = self._auditorias_modelo(modelo)
        if registro_id is not None:
            queryset = queryset.filter(registro_id=registro_id)
        return queryset.first()

    def _campo_coluna(self, coluna: ColunaPersonalizada) -> str:
        return TabelaPersonalizadaLinhaForm.campo_coluna_nome(coluna.pk)

    def _habilitar_filtro_estruturado(self, coluna: ColunaPersonalizada):
        configuracao = dict(coluna.configuracao_json or {})
        configuracao['filtro'] = {
            'habilitado': True,
            'operadores': list(ColunaPersonalizada.operadores_filtro_por_tipo_dado(coluna.tipo_dado)),
        }
        coluna.configuracao_json = configuracao
        coluna.save()
        return coluna

    def _dados_filtro_estruturado(
        self,
        coluna: ColunaPersonalizada,
        *,
        operador: str,
        valor: str | None = None,
        inicio: str | None = None,
        fim: str | None = None,
        busca: str | None = None,
    ) -> dict[str, str]:
        dados: dict[str, str] = {}
        if busca is not None:
            dados['busca'] = busca
        dados[TabelaPersonalizadaLinhaFiltroEstruturadoForm.campo_operador_nome(coluna.pk)] = operador
        if valor is not None:
            dados[TabelaPersonalizadaLinhaFiltroEstruturadoForm.campo_valor_nome(coluna.pk)] = valor
        if inicio is not None:
            dados[TabelaPersonalizadaLinhaFiltroEstruturadoForm.campo_inicio_nome(coluna.pk)] = inicio
        if fim is not None:
            dados[TabelaPersonalizadaLinhaFiltroEstruturadoForm.campo_fim_nome(coluna.pk)] = fim
        return dados

    def _criar_colunas_fonte_formula(self):
        sequencia = ColunaPersonalizada.objects.filter(tabela=self.tabela).count() + 1
        return {
            'inteiro': ColunaPersonalizada.objects.create(
                tabela=self.tabela,
                nome=f'Quantidade base {sequencia}',
                tipo_dado=ColunaPersonalizada.TipoDado.INTEIRO,
                visivel=True,
                ordem=30 + sequencia,
            ),
            'decimal': ColunaPersonalizada.objects.create(
                tabela=self.tabela,
                nome=f'Consumo base {sequencia}',
                tipo_dado=ColunaPersonalizada.TipoDado.DECIMAL,
                visivel=True,
                ordem=31 + sequencia,
            ),
            'monetario': ColunaPersonalizada.objects.create(
                tabela=self.tabela,
                nome=f'Valor base {sequencia}',
                tipo_dado=ColunaPersonalizada.TipoDado.MONETARIO,
                visivel=True,
                ordem=32 + sequencia,
            ),
            'percentual': ColunaPersonalizada.objects.create(
                tabela=self.tabela,
                nome=f'Percentual base {sequencia}',
                tipo_dado=ColunaPersonalizada.TipoDado.PERCENTUAL,
                visivel=True,
                ordem=33 + sequencia,
            ),
        }

    def _dados_formula_coluna(
        self,
        *,
        nome='Campo calculado guiado',
        operacao=ColunaPersonalizada.OperacaoFormula.SOMA,
        operandos=None,
        resultado_tipo=ColunaPersonalizada.TipoDado.DECIMAL,
        casas_decimais=8,
        visivel='on',
    ):
        return {
            'nome': nome,
            'tipo_dado': ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA,
            'opcoes_lista': '',
            'totalizadores_configurados': [],
            'filtro_estruturado': '',
            'formula_operacao': operacao,
            'formula_operandos': [str(valor) for valor in (operandos or [])],
            'formula_resultado_tipo': resultado_tipo,
            'formula_casas_decimais': casas_decimais,
            'obrigatoria': '',
            'visivel': visivel,
            'ordem': 40,
            'status': ColunaPersonalizada.StatusColuna.ATIVA,
        }

    def _configurar_formula_coluna(
        self,
        coluna: ColunaPersonalizada,
        *,
        operacao: str,
        operandos: list[int],
        resultado_tipo: str = ColunaPersonalizada.TipoDado.DECIMAL,
        casas_decimais: int = 8,
    ) -> ColunaPersonalizada:
        coluna.configuracao_json = {
            'formula': {
                'habilitada': True,
                'operacao': operacao,
                'operandos': operandos,
                'resultado_tipo': resultado_tipo,
                'casas_decimais': casas_decimais,
            }
        }
        coluna.save()
        return coluna

    def _criar_colunas_para_linhas(self):
        texto = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Descricao do item',
            tipo_dado=ColunaPersonalizada.TipoDado.TEXTO_CURTO,
            obrigatoria=True,
            visivel=True,
            ordem=10,
        )
        inteiro = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Quantidade em estoque',
            tipo_dado=ColunaPersonalizada.TipoDado.INTEIRO,
            obrigatoria=True,
            visivel=True,
            ordem=11,
        )
        monetario = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Valor unitario',
            tipo_dado=ColunaPersonalizada.TipoDado.MONETARIO,
            obrigatoria=False,
            visivel=True,
            ordem=12,
        )
        decimal = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Consumo decimal',
            tipo_dado=ColunaPersonalizada.TipoDado.DECIMAL,
            obrigatoria=False,
            visivel=True,
            ordem=12,
        )
        percentual = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Percentual aplicado',
            tipo_dado=ColunaPersonalizada.TipoDado.PERCENTUAL,
            obrigatoria=False,
            visivel=True,
            ordem=12,
        )
        data_coluna = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Data de entrada',
            tipo_dado=ColunaPersonalizada.TipoDado.DATA,
            obrigatoria=False,
            visivel=True,
            ordem=13,
        )
        competencia = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Competencia interna',
            tipo_dado=ColunaPersonalizada.TipoDado.MES_COMPETENCIA,
            obrigatoria=False,
            visivel=True,
            ordem=14,
        )
        booleano = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Conferido',
            tipo_dado=ColunaPersonalizada.TipoDado.BOOLEANO,
            obrigatoria=False,
            visivel=True,
            ordem=15,
        )
        lista = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Categoria de uso',
            tipo_dado=ColunaPersonalizada.TipoDado.LISTA_OPCOES,
            obrigatoria=False,
            visivel=True,
            ordem=16,
            configuracao_json={'opcoes': ['Material', 'Limpeza', 'Apoio']},
        )
        invisivel = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Campo oculto',
            tipo_dado=ColunaPersonalizada.TipoDado.TEXTO_CURTO,
            obrigatoria=False,
            visivel=False,
            ordem=17,
        )
        arquivada = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Campo arquivado',
            tipo_dado=ColunaPersonalizada.TipoDado.TEXTO_CURTO,
            obrigatoria=False,
            visivel=True,
            ordem=18,
            status=ColunaPersonalizada.StatusColuna.ARQUIVADA,
        )
        formula = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Campo calculado futuro',
            tipo_dado=ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA,
            calculada=True,
            obrigatoria=False,
            visivel=True,
            ordem=19,
            configuracao_json={
                'formula': {
                    'habilitada': True,
                    'operacao': ColunaPersonalizada.OperacaoFormula.SOMA,
                    'operandos': [inteiro.pk, decimal.pk],
                    'resultado_tipo': ColunaPersonalizada.TipoDado.DECIMAL,
                    'casas_decimais': 8,
                }
            },
        )
        return {
            'texto': texto,
            'inteiro': inteiro,
            'monetario': monetario,
            'decimal': decimal,
            'percentual': percentual,
            'data': data_coluna,
            'competencia': competencia,
            'booleano': booleano,
            'lista': lista,
            'invisivel': invisivel,
            'arquivada': arquivada,
            'formula': formula,
        }

    def _criar_linha_com_valores(self, colunas: dict[str, ColunaPersonalizada]):
        linha = LinhaTabelaPersonalizada.objects.create(
            tabela=self.tabela,
            ordem=20,
            criado_por=self.user,
            atualizado_por=self.user,
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['texto'],
            valor_texto='Sabao liquido',
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['inteiro'],
            valor_numero=Decimal('4'),
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['monetario'],
            valor_numero=Decimal('50.72'),
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['booleano'],
            valor_booleano=True,
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['decimal'],
            valor_numero=Decimal('1.01499912'),
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['percentual'],
            valor_numero=Decimal('12.3456'),
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['data'],
            valor_data=date(2026, 5, 8),
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['competencia'],
            valor_texto='05/2026',
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['lista'],
            valor_texto='Limpeza',
        )
        return linha

    def _criar_segunda_linha_com_valores(self, colunas: dict[str, ColunaPersonalizada], *, status='ativa'):
        linha = LinhaTabelaPersonalizada.objects.create(
            tabela=self.tabela,
            ordem=21,
            status=status,
            criado_por=self.user,
            atualizado_por=self.user,
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['texto'],
            valor_texto='Detergente concentrado',
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['inteiro'],
            valor_numero=Decimal('2'),
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['monetario'],
            valor_numero=Decimal('19.90'),
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['decimal'],
            valor_numero=Decimal('2.00000088'),
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['percentual'],
            valor_numero=Decimal('4.5'),
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['data'],
            valor_data=date(2026, 5, 10),
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['competencia'],
            valor_texto='06/2026',
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['booleano'],
            valor_booleano=False,
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['lista'],
            valor_texto='Material',
        )
        return linha

    def _dados_minimos_linha(self, colunas: dict[str, ColunaPersonalizada]):
        return {
            self._campo_coluna(colunas['texto']): 'Linha base',
            self._campo_coluna(colunas['inteiro']): '1',
        }

    def _valor_renderizado_coluna(
        self,
        response,
        nome_coluna: str,
        *,
        linha_pk: int | None = None,
    ) -> str | None:
        for item in response.context['linhas_renderizadas']:
            if linha_pk is not None and item['linha'].pk != linha_pk:
                continue
            for celula in item['celulas']:
                if celula['coluna'].nome == nome_coluna:
                    return celula['valor']
        return None

    def _ler_linhas_xlsx(self, conteudo: bytes) -> list[list[str]]:
        with ZipFile(BytesIO(conteudo)) as arquivo_xlsx:
            workbook_tree = ElementTree.fromstring(arquivo_xlsx.read('xl/workbook.xml'))
            namespace_workbook = {
                'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                'rel': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
            }
            primeiro_sheet = workbook_tree.find('main:sheets/main:sheet', namespace_workbook)
            self.assertIsNotNone(primeiro_sheet)
            relation_id = primeiro_sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')

            relacoes_tree = ElementTree.fromstring(arquivo_xlsx.read('xl/_rels/workbook.xml.rels'))
            namespace_rels = {'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}
            destino = ''
            for relacao in relacoes_tree.findall('rel:Relationship', namespace_rels):
                if relacao.get('Id') == relation_id:
                    destino = relacao.get('Target', '')
                    break

            self.assertTrue(destino)
            caminho_planilha = f"xl/{destino.lstrip('./')}"
            planilha_tree = ElementTree.fromstring(arquivo_xlsx.read(caminho_planilha))
            namespace_planilha = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

            linhas = []
            for linha in planilha_tree.findall('main:sheetData/main:row', namespace_planilha):
                valores = []
                for celula in linha.findall('main:c', namespace_planilha):
                    referencia = celula.get('r', '')
                    correspondencia = re.match(r'([A-Z]+)\d+$', referencia)
                    if correspondencia:
                        indice_coluna = 0
                        for letra in correspondencia.group(1):
                            indice_coluna = (indice_coluna * 26) + (ord(letra) - ord('A') + 1)
                        while len(valores) < indice_coluna - 1:
                            valores.append('')
                    texto = ''.join(celula.itertext())
                    valores.append(texto)
                linhas.append(valores)
            return linhas

    def test_url_resolve_para_view_da_listagem_minima(self):
        resolved = resolve(reverse('financeiro:tabela-personalizada-list'))

        self.assertIs(resolved.func.view_class, TabelaPersonalizadaListView)

    def test_url_resolve_para_view_de_criacao(self):
        resolved = resolve(reverse('financeiro:tabela-personalizada-create'))

        self.assertIs(resolved.func.view_class, TabelaPersonalizadaCreateView)

    def test_url_resolve_para_view_de_edicao(self):
        resolved = resolve(reverse('financeiro:tabela-personalizada-update', kwargs={'pk': self.tabela.pk}))

        self.assertIs(resolved.func.view_class, TabelaPersonalizadaUpdateView)

    def test_url_resolve_para_view_de_listagem_de_colunas(self):
        resolved = resolve(
            reverse('financeiro:tabela-personalizada-coluna-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertIs(resolved.func.view_class, TabelaPersonalizadaColunaListView)

    def test_url_resolve_para_view_de_criacao_de_coluna(self):
        resolved = resolve(
            reverse('financeiro:tabela-personalizada-coluna-create', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertIs(resolved.func.view_class, TabelaPersonalizadaColunaCreateView)

    def test_url_resolve_para_view_de_edicao_de_coluna(self):
        resolved = resolve(
            reverse(
                'financeiro:tabela-personalizada-coluna-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': self.coluna_existente.pk},
            )
        )

        self.assertIs(resolved.func.view_class, TabelaPersonalizadaColunaUpdateView)

    def test_url_resolve_para_view_de_listagem_de_linhas(self):
        resolved = resolve(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertIs(resolved.func.view_class, TabelaPersonalizadaLinhaListView)

    def test_url_resolve_para_view_de_criacao_de_linha(self):
        resolved = resolve(
            reverse('financeiro:tabela-personalizada-linha-create', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertIs(resolved.func.view_class, TabelaPersonalizadaLinhaCreateView)

    def test_url_resolve_para_view_de_exportacao_xlsx_de_linhas(self):
        resolved = resolve(
            reverse('financeiro:tabela-personalizada-linha-export-xlsx', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertIs(resolved.func.view_class, TabelaPersonalizadaLinhaExportXlsxView)

    def test_url_resolve_para_view_de_edicao_de_linha(self):
        linha = LinhaTabelaPersonalizada.objects.create(
            tabela=self.tabela,
            criado_por=self.user,
            atualizado_por=self.user,
        )
        resolved = resolve(
            reverse(
                'financeiro:tabela-personalizada-linha-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': linha.pk},
            )
        )

        self.assertIs(resolved.func.view_class, TabelaPersonalizadaLinhaUpdateView)

    def test_usuario_com_permissao_visualizar_acessa_listagem(self):
        self._login_com_permissoes(
            'user-tabela-visualizar',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(reverse('financeiro:tabela-personalizada-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Controle de almoxarifado')
        self.assertContains(response, '2')
        self.assertContains(response, '1')

    def test_usuario_sem_permissao_visualizar_recebe_403(self):
        self._login_com_permissoes(
            'user-tabela-sem-visualizar',
            ['financeiro.lancamentos.listar'],
        )

        response = self.client.get(reverse('financeiro:tabela-personalizada-list'))

        self.assertEqual(response.status_code, 403)

    def test_usuario_com_permissao_criar_acessa_tela_de_criacao(self):
        self._login_com_permissoes(
            'user-tabela-criar',
            [PermissoesTabelasPersonalizadas.CRIAR],
        )

        response = self.client.get(reverse('financeiro:tabela-personalizada-create'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cadastro apenas dos dados gerais da tabela personalizada.')
        self.assertContains(response, 'a configuracao de colunas sera liberada em microetapa posterior.')

    def test_usuario_sem_permissao_criar_recebe_403_na_criacao(self):
        self._login_com_permissoes(
            'user-tabela-sem-criar',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(reverse('financeiro:tabela-personalizada-create'))

        self.assertEqual(response.status_code, 403)

    def test_criacao_valida_de_tabela_personalizada(self):
        usuario = self._login_com_permissoes(
            'user-tabela-criacao-valida',
            [
                PermissoesTabelasPersonalizadas.CRIAR,
                PermissoesTabelasPersonalizadas.VISUALIZAR,
            ],
        )

        response = self.client.post(
            reverse('financeiro:tabela-personalizada-create'),
            data={
                'nome': 'Controle de eventos',
                'descricao': 'Uso interno para agenda de manutencoes.',
                'status': TabelaPersonalizada.StatusTabela.INATIVA,
                'ordem': 7,
            },
        )

        self.assertRedirects(response, reverse('financeiro:tabela-personalizada-list'))
        tabela = TabelaPersonalizada.objects.get(nome='Controle de eventos')
        self.assertEqual(tabela.descricao, 'Uso interno para agenda de manutencoes.')
        self.assertEqual(tabela.status, TabelaPersonalizada.StatusTabela.INATIVA)
        self.assertEqual(tabela.ordem, 7)
        self.assertEqual(tabela.criado_por, usuario)
        self.assertEqual(tabela.atualizado_por, usuario)

    def test_form_da_tabela_personalizada_expoe_apenas_metadados(self):
        form = TabelaPersonalizadaForm()

        self.assertEqual(list(form.fields.keys()), ['nome', 'descricao', 'status', 'ordem'])

    def test_usuario_com_permissao_editar_estrutura_acessa_tela_de_edicao(self):
        self._login_com_permissoes(
            'user-tabela-editar',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-update', kwargs={'pk': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cadastro apenas dos dados gerais da tabela personalizada.')
        self.assertContains(response, self.tabela.nome)

    def test_usuario_sem_permissao_editar_estrutura_recebe_403_na_edicao(self):
        self._login_com_permissoes(
            'user-tabela-sem-editar',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-update', kwargs={'pk': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 403)

    def test_edicao_valida_de_metadados_da_tabela(self):
        usuario = self._login_com_permissoes(
            'user-tabela-edicao-valida',
            [
                PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA,
                PermissoesTabelasPersonalizadas.VISUALIZAR,
            ],
        )

        response = self.client.post(
            reverse('financeiro:tabela-personalizada-update', kwargs={'pk': self.tabela.pk}),
            data={
                'nome': 'Controle de almoxarifado revisado',
                'descricao': 'Controle interno ajustado nesta microetapa.',
                'status': TabelaPersonalizada.StatusTabela.INATIVA,
                'ordem': 3,
            },
        )

        self.assertRedirects(response, reverse('financeiro:tabela-personalizada-list'))
        self.tabela.refresh_from_db()
        self.assertEqual(self.tabela.nome, 'Controle de almoxarifado revisado')
        self.assertEqual(self.tabela.descricao, 'Controle interno ajustado nesta microetapa.')
        self.assertEqual(self.tabela.status, TabelaPersonalizada.StatusTabela.INATIVA)
        self.assertEqual(self.tabela.ordem, 3)
        self.assertEqual(self.tabela.atualizado_por, usuario)

    def test_criacao_de_tabela_gera_auditoria(self):
        self._login_com_permissoes(
            'user-tabela-auditoria-create',
            [PermissoesTabelasPersonalizadas.CRIAR],
        )

        response = self.client.post(
            reverse('financeiro:tabela-personalizada-create'),
            data={
                'nome': 'Controle auditavel',
                'descricao': 'Teste de auditoria de criacao.',
                'status': TabelaPersonalizada.StatusTabela.ATIVA,
                'ordem': 9,
            },
        )

        self.assertEqual(response.status_code, 302)
        tabela = TabelaPersonalizada.objects.get(nome='Controle auditavel')
        log = self._ultimo_log_modelo('TabelaPersonalizada', registro_id=tabela.pk)
        self.assertIsNotNone(log)
        self.assertEqual(log.acao, AuditoriaFinanceiro.AcaoAuditoria.CREATE)
        self.assertIn('nome', log.campos_alterados)
        self.assertEqual(log.campos_alterados['nome']['after'], 'Controle auditavel')

    def test_edicao_de_tabela_gera_auditoria_com_before_after(self):
        self._login_com_permissoes(
            'user-tabela-auditoria-update',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )

        response = self.client.post(
            reverse('financeiro:tabela-personalizada-update', kwargs={'pk': self.tabela.pk}),
            data={
                'nome': 'Controle auditado',
                'descricao': 'Descricao atualizada para auditoria.',
                'status': TabelaPersonalizada.StatusTabela.INATIVA,
                'ordem': 4,
            },
        )

        self.assertEqual(response.status_code, 302)
        log = self._ultimo_log_modelo('TabelaPersonalizada', registro_id=self.tabela.pk)
        self.assertIsNotNone(log)
        self.assertEqual(log.acao, AuditoriaFinanceiro.AcaoAuditoria.UPDATE)
        self.assertEqual(log.campos_alterados['nome']['before'], 'Controle de almoxarifado')
        self.assertEqual(log.campos_alterados['nome']['after'], 'Controle auditado')

    def test_usuario_com_permissao_editar_estrutura_acessa_listagem_de_colunas(self):
        self._login_com_permissoes(
            'user-coluna-list',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-coluna-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Estrutura da tabela')
        self.assertContains(response, 'Observacao interna')
        self.assertContains(response, 'estrutura das colunas')
        self.assertContains(response, 'totalizadores por coluna')

    def test_listagem_de_colunas_indica_filtro_estruturado_habilitado(self):
        self.coluna_existente.tipo_dado = ColunaPersonalizada.TipoDado.DECIMAL
        self.coluna_existente.configuracao_json = {
            'filtro': {
                'habilitado': True,
                'operadores': ['entre', 'igual', 'maior', 'menor'],
            }
        }
        self.coluna_existente.save()
        self._login_com_permissoes(
            'user-coluna-lista-filtro',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-coluna-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Filtro estruturado')
        self.assertContains(response, 'Habilitado')

    def test_listagem_de_colunas_indica_formula_guiada_configurada(self):
        fontes = self._criar_colunas_fonte_formula()
        ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Total configurado',
            tipo_dado=ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA,
            calculada=True,
            visivel=True,
            configuracao_json={
                'formula': {
                    'habilitada': True,
                    'operacao': ColunaPersonalizada.OperacaoFormula.SOMA,
                    'operandos': [fontes['inteiro'].pk, fontes['decimal'].pk],
                    'resultado_tipo': ColunaPersonalizada.TipoDado.DECIMAL,
                    'casas_decimais': 8,
                }
            },
        )
        self._login_com_permissoes(
            'user-coluna-lista-formula',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-coluna-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Formula guiada')
        self.assertContains(response, 'Configurada')

    def test_usuario_sem_permissao_editar_estrutura_nao_acessa_colunas(self):
        self._login_com_permissoes(
            'user-coluna-list-sem-permissao',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-coluna-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 403)

    def test_form_de_coluna_sem_permissao_nao_expoe_formula_controlada_nem_calculada(self):
        form = ColunaPersonalizadaForm()
        valores_tipo = {valor for valor, _rotulo in form.fields['tipo_dado'].choices}

        self.assertNotIn(ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA, valores_tipo)
        self.assertNotIn('calculada', form.fields)
        self.assertNotIn('formula_operacao', form.fields)

    def test_form_de_coluna_com_permissao_expoe_formula_guiada(self):
        fontes = self._criar_colunas_fonte_formula()
        form = ColunaPersonalizadaForm(
            tabela=self.tabela,
            pode_configurar_formula=True,
        )
        valores_tipo = {valor for valor, _rotulo in form.fields['tipo_dado'].choices}

        self.assertIn(ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA, valores_tipo)
        self.assertIn('formula_operacao', form.fields)
        self.assertIn('formula_operandos', form.fields)
        self.assertIn(str(fontes['inteiro'].pk), {valor for valor, _rotulo in form.fields['formula_operandos'].choices})

    def test_formulario_coluna_oculta_bloco_de_opcoes_lista_quando_tipo_nao_e_lista(self):
        self._login_com_permissoes(
            'user-coluna-form-lista-oculta',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )

        response = self.client.get(
            reverse(
                'financeiro:tabela-personalizada-coluna-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': self.coluna_existente.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'id="financeiro-opcoes-lista-box"',
        )
        self.assertContains(
            response,
            'data-lista-tipo="lista_opcoes"',
            html=False,
        )

    def test_formulario_coluna_mostra_formula_apenas_com_permissao_e_tipo_formula(self):
        fontes = self._criar_colunas_fonte_formula()
        coluna_formula = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Formula visivel',
            tipo_dado=ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA,
            calculada=True,
            visivel=True,
            configuracao_json={
                'formula': {
                    'habilitada': True,
                    'operacao': ColunaPersonalizada.OperacaoFormula.SOMA,
                    'operandos': [fontes['inteiro'].pk, fontes['decimal'].pk],
                    'resultado_tipo': ColunaPersonalizada.TipoDado.DECIMAL,
                    'casas_decimais': 8,
                }
            },
        )
        self._login_com_permissoes(
            'user-coluna-formula-template-permissao',
            [
                PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA,
                PermissoesTabelasPersonalizadas.CONFIGURAR_FORMULA,
            ],
        )

        response_com_permissao = self.client.get(
            reverse(
                'financeiro:tabela-personalizada-coluna-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': coluna_formula.pk},
            )
        )
        self.assertContains(response_com_permissao, 'id="financeiro-formula-guiada-box"')
        self.assertNotContains(
            response_com_permissao,
            'id="financeiro-formula-guiada-box" class="financeiro-coluna-form-formula-box is-hidden"',
            html=False,
        )

        self._login_com_permissoes(
            'user-coluna-formula-template-sem-permissao',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )
        response_sem_permissao = self.client.get(
            reverse(
                'financeiro:tabela-personalizada-coluna-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': coluna_formula.pk},
            )
        )
        self.assertEqual(response_sem_permissao.status_code, 403)

    def test_formulario_coluna_exibe_textos_de_microcopy_da_ux_autodidata(self):
        self._login_com_permissoes(
            'user-coluna-form-microcopy',
            [
                PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA,
                PermissoesTabelasPersonalizadas.CONFIGURAR_FORMULA,
            ],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-coluna-create', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Use este campo apenas quando o tipo da coluna for Lista de opcoes.')
        self.assertContains(
            response,
            'Este filtro aparecera na tela de linhas para facilitar a busca por periodo ou valor.',
        )
        self.assertContains(
            response,
            'A formula e aplicada por coluna e usa apenas colunas numericas da mesma linha.',
        )
        self.assertContains(
            response,
            'Neste primeiro recorte, o resultado da formula pode ser Decimal ou Monetario.',
        )
        self.assertContains(
            response,
            'Use Decimal com 0 casas quando quiser um resultado sem casas decimais.',
        )
        self.assertContains(response, 'O totalizador aparece no rodape da tabela de linhas.')

    def test_usuario_com_permissao_cria_coluna_valida(self):
        self._login_com_permissoes(
            'user-coluna-criar',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )

        response = self.client.post(
            reverse('financeiro:tabela-personalizada-coluna-create', kwargs={'tabela_id': self.tabela.pk}),
            data={
                'nome': 'Categoria interna',
                'tipo_dado': ColunaPersonalizada.TipoDado.LISTA_OPCOES,
                'opcoes_lista': 'Material\nLimpeza\nApoio',
                'obrigatoria': 'on',
                'visivel': 'on',
                'ordem': 5,
                'status': ColunaPersonalizada.StatusColuna.ATIVA,
            },
        )

        self.assertRedirects(
            response,
            reverse('financeiro:tabela-personalizada-coluna-list', kwargs={'tabela_id': self.tabela.pk}),
        )
        coluna = ColunaPersonalizada.objects.get(tabela=self.tabela, nome='Categoria interna')
        self.assertEqual(coluna.tipo_dado, ColunaPersonalizada.TipoDado.LISTA_OPCOES)
        self.assertEqual(coluna.configuracao_json, {'opcoes': ['Material', 'Limpeza', 'Apoio']})
        self.assertFalse(coluna.calculada)

    def test_usuario_com_permissao_configurar_formula_cria_formula_valida(self):
        fontes = self._criar_colunas_fonte_formula()
        self._login_com_permissoes(
            'user-coluna-formula-criar',
            [
                PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA,
                PermissoesTabelasPersonalizadas.CONFIGURAR_FORMULA,
            ],
        )

        response = self.client.post(
            reverse('financeiro:tabela-personalizada-coluna-create', kwargs={'tabela_id': self.tabela.pk}),
            data=self._dados_formula_coluna(
                nome='Total guiado',
                operacao=ColunaPersonalizada.OperacaoFormula.SOMA,
                operandos=[fontes['inteiro'].pk, fontes['decimal'].pk, fontes['percentual'].pk],
                resultado_tipo=ColunaPersonalizada.TipoDado.DECIMAL,
                casas_decimais=8,
            ),
        )

        self.assertRedirects(
            response,
            reverse('financeiro:tabela-personalizada-coluna-list', kwargs={'tabela_id': self.tabela.pk}),
        )
        coluna = ColunaPersonalizada.objects.get(tabela=self.tabela, nome='Total guiado')
        self.assertTrue(coluna.calculada)
        self.assertEqual(coluna.tipo_dado, ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA)
        self.assertEqual(
            coluna.configuracao_json['formula'],
            {
                'habilitada': True,
                'operacao': ColunaPersonalizada.OperacaoFormula.SOMA,
                'operandos': [fontes['inteiro'].pk, fontes['decimal'].pk, fontes['percentual'].pk],
                'resultado_tipo': ColunaPersonalizada.TipoDado.DECIMAL,
                'casas_decimais': 8,
            },
        )

    def test_usuario_com_permissao_edita_coluna_valida(self):
        self._login_com_permissoes(
            'user-coluna-editar',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )

        response = self.client.post(
            reverse(
                'financeiro:tabela-personalizada-coluna-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': self.coluna_existente.pk},
            ),
            data={
                'nome': 'Observacao revisada',
                'tipo_dado': ColunaPersonalizada.TipoDado.TEXTO_CURTO,
                'opcoes_lista': '',
                'obrigatoria': 'on',
                'visivel': '',
                'ordem': 9,
                'status': ColunaPersonalizada.StatusColuna.INATIVA,
            },
        )

        self.assertRedirects(
            response,
            reverse('financeiro:tabela-personalizada-coluna-list', kwargs={'tabela_id': self.tabela.pk}),
        )
        self.coluna_existente.refresh_from_db()
        self.assertEqual(self.coluna_existente.nome, 'Observacao revisada')
        self.assertEqual(self.coluna_existente.tipo_dado, ColunaPersonalizada.TipoDado.TEXTO_CURTO)
        self.assertTrue(self.coluna_existente.obrigatoria)
        self.assertFalse(self.coluna_existente.visivel)
        self.assertEqual(self.coluna_existente.ordem, 9)
        self.assertEqual(self.coluna_existente.status, ColunaPersonalizada.StatusColuna.INATIVA)

    def test_usuario_com_permissao_configurar_formula_pode_atualizar_formula_existente(self):
        fontes = self._criar_colunas_fonte_formula()
        coluna_formula = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Margem calculada',
            tipo_dado=ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA,
            calculada=True,
            visivel=True,
            configuracao_json={
                'formula': {
                    'habilitada': True,
                    'operacao': ColunaPersonalizada.OperacaoFormula.SOMA,
                    'operandos': [fontes['inteiro'].pk, fontes['decimal'].pk],
                    'resultado_tipo': ColunaPersonalizada.TipoDado.DECIMAL,
                    'casas_decimais': 8,
                }
            },
        )
        self._login_com_permissoes(
            'user-coluna-formula-editar',
            [
                PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA,
                PermissoesTabelasPersonalizadas.CONFIGURAR_FORMULA,
            ],
        )

        response = self.client.post(
            reverse(
                'financeiro:tabela-personalizada-coluna-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': coluna_formula.pk},
            ),
            data=self._dados_formula_coluna(
                nome='Margem calculada',
                operacao=ColunaPersonalizada.OperacaoFormula.MULTIPLICACAO,
                operandos=[fontes['decimal'].pk, fontes['percentual'].pk],
                resultado_tipo=ColunaPersonalizada.TipoDado.MONETARIO,
                casas_decimais=2,
            ),
        )

        self.assertRedirects(
            response,
            reverse('financeiro:tabela-personalizada-coluna-list', kwargs={'tabela_id': self.tabela.pk}),
        )
        coluna_formula.refresh_from_db()
        self.assertEqual(
            coluna_formula.configuracao_json['formula'],
            {
                'habilitada': True,
                'operacao': ColunaPersonalizada.OperacaoFormula.MULTIPLICACAO,
                'operandos': [fontes['decimal'].pk, fontes['percentual'].pk],
                'resultado_tipo': ColunaPersonalizada.TipoDado.MONETARIO,
                'casas_decimais': 2,
            },
        )

    def test_usuario_sem_permissao_configurar_formula_nao_consegue_criar_formula(self):
        fontes = self._criar_colunas_fonte_formula()
        self._login_com_permissoes(
            'user-coluna-sem-formula',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )

        response = self.client.post(
            reverse('financeiro:tabela-personalizada-coluna-create', kwargs={'tabela_id': self.tabela.pk}),
            data=self._dados_formula_coluna(
                operandos=[fontes['inteiro'].pk, fontes['decimal'].pk],
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            ColunaPersonalizada.objects.filter(tabela=self.tabela, nome='Campo calculado guiado').exists()
        )

    def test_usuario_sem_permissao_configurar_formula_recebe_403_ao_editar_formula_existente(self):
        fontes = self._criar_colunas_fonte_formula()
        coluna_formula = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Margem calculada',
            tipo_dado=ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA,
            calculada=True,
            visivel=True,
            configuracao_json={
                'formula': {
                    'habilitada': True,
                    'operacao': ColunaPersonalizada.OperacaoFormula.SOMA,
                    'operandos': [fontes['inteiro'].pk, fontes['decimal'].pk],
                    'resultado_tipo': ColunaPersonalizada.TipoDado.DECIMAL,
                    'casas_decimais': 8,
                }
            },
        )
        self._login_com_permissoes(
            'user-coluna-formula-bloqueada',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )

        response = self.client.get(
            reverse(
                'financeiro:tabela-personalizada-coluna-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': coluna_formula.pk},
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_form_bloqueia_formula_com_operacao_invalida(self):
        fontes = self._criar_colunas_fonte_formula()
        form = ColunaPersonalizadaForm(
            tabela=self.tabela,
            pode_configurar_formula=True,
            data={
                **self._dados_formula_coluna(
                    nome='Formula futura',
                    operandos=[fontes['inteiro'].pk, fontes['decimal'].pk],
                ),
                'formula_operacao': 'potencia',
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn('formula_operacao', form.errors)

    def test_form_bloqueia_formula_com_operando_textual_data_lista_booleano_ou_competencia(self):
        coluna_texto = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Texto origem',
            tipo_dado=ColunaPersonalizada.TipoDado.TEXTO_CURTO,
            visivel=True,
        )
        coluna_data = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Data origem',
            tipo_dado=ColunaPersonalizada.TipoDado.DATA,
            visivel=True,
        )
        coluna_lista = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Lista origem',
            tipo_dado=ColunaPersonalizada.TipoDado.LISTA_OPCOES,
            visivel=True,
            configuracao_json={'opcoes': ['A', 'B']},
        )
        coluna_booleano = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Booleano origem',
            tipo_dado=ColunaPersonalizada.TipoDado.BOOLEANO,
            visivel=True,
        )
        coluna_competencia = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Competencia origem',
            tipo_dado=ColunaPersonalizada.TipoDado.MES_COMPETENCIA,
            visivel=True,
        )
        base_numerica = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Numero base',
            tipo_dado=ColunaPersonalizada.TipoDado.DECIMAL,
            visivel=True,
        )

        for operando_invalido in (
            coluna_texto,
            coluna_data,
            coluna_lista,
            coluna_booleano,
            coluna_competencia,
        ):
            form = ColunaPersonalizadaForm(
                tabela=self.tabela,
                pode_configurar_formula=True,
                data=self._dados_formula_coluna(
                    nome=f'Formula {operando_invalido.pk}',
                    operandos=[base_numerica.pk, operando_invalido.pk],
                ),
            )

            self.assertFalse(form.is_valid())
            self.assertIn('formula_operandos', form.errors)

    def test_form_bloqueia_formula_com_operando_inexistente_invisivel_ou_inativo(self):
        base_a = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Base A',
            tipo_dado=ColunaPersonalizada.TipoDado.DECIMAL,
            visivel=True,
        )
        base_invisivel = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Base invisivel',
            tipo_dado=ColunaPersonalizada.TipoDado.DECIMAL,
            visivel=False,
        )
        base_inativa = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Base inativa',
            tipo_dado=ColunaPersonalizada.TipoDado.DECIMAL,
            visivel=True,
            status=ColunaPersonalizada.StatusColuna.INATIVA,
        )

        for operandos in (
            [base_a.pk, 999999],
            [base_a.pk, base_invisivel.pk],
            [base_a.pk, base_inativa.pk],
        ):
            form = ColunaPersonalizadaForm(
                tabela=self.tabela,
                pode_configurar_formula=True,
                data=self._dados_formula_coluna(
                    nome=f'Formula bloqueada {operandos[-1]}',
                    operandos=operandos,
                ),
            )

            self.assertFalse(form.is_valid())
            self.assertIn('formula_operandos', form.errors)

    def test_form_bloqueia_formula_sobre_formula_existente(self):
        fontes = self._criar_colunas_fonte_formula()
        coluna_formula = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Formula base',
            tipo_dado=ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA,
            calculada=True,
            visivel=True,
            configuracao_json={
                'formula': {
                    'habilitada': True,
                    'operacao': ColunaPersonalizada.OperacaoFormula.SOMA,
                    'operandos': [fontes['inteiro'].pk, fontes['decimal'].pk],
                    'resultado_tipo': ColunaPersonalizada.TipoDado.DECIMAL,
                    'casas_decimais': 8,
                }
            },
        )
        form = ColunaPersonalizadaForm(
            tabela=self.tabela,
            pode_configurar_formula=True,
            data=self._dados_formula_coluna(
                nome='Formula dependente',
                operandos=[fontes['monetario'].pk, coluna_formula.pk],
            ),
        )

        self.assertFalse(form.is_valid())
        self.assertIn('formula_operandos', form.errors)

    def test_form_bloqueia_formula_com_operando_na_propria_coluna(self):
        fontes = self._criar_colunas_fonte_formula()
        coluna_formula = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Formula editavel',
            tipo_dado=ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA,
            calculada=True,
            visivel=True,
            configuracao_json={
                'formula': {
                    'habilitada': True,
                    'operacao': ColunaPersonalizada.OperacaoFormula.SOMA,
                    'operandos': [fontes['inteiro'].pk, fontes['decimal'].pk],
                    'resultado_tipo': ColunaPersonalizada.TipoDado.DECIMAL,
                    'casas_decimais': 8,
                }
            },
        )
        form = ColunaPersonalizadaForm(
            tabela=self.tabela,
            pode_configurar_formula=True,
            instance=coluna_formula,
            data=self._dados_formula_coluna(
                nome='Formula editavel',
                operandos=[fontes['inteiro'].pk, coluna_formula.pk],
            ),
        )

        self.assertFalse(form.is_valid())
        self.assertIn('formula_operandos', form.errors)

    def test_form_bloqueia_formula_incompleta(self):
        fontes = self._criar_colunas_fonte_formula()
        form = ColunaPersonalizadaForm(
            tabela=self.tabela,
            pode_configurar_formula=True,
            data={
                **self._dados_formula_coluna(
                    nome='Formula incompleta',
                    operandos=[fontes['inteiro'].pk],
                ),
                'formula_resultado_tipo': '',
                'formula_casas_decimais': '',
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn('formula_operandos', form.errors)
        self.assertIn('formula_resultado_tipo', form.errors)
        self.assertIn('formula_casas_decimais', form.errors)

    def test_form_bloqueia_divisao_com_quantidade_invalida_de_operandos(self):
        fontes = self._criar_colunas_fonte_formula()
        form = ColunaPersonalizadaForm(
            tabela=self.tabela,
            pode_configurar_formula=True,
            data=self._dados_formula_coluna(
                nome='Formula divisao',
                operacao=ColunaPersonalizada.OperacaoFormula.DIVISAO,
                operandos=[fontes['inteiro'].pk, fontes['decimal'].pk, fontes['monetario'].pk],
            ),
        )

        self.assertFalse(form.is_valid())
        self.assertIn('formula_operandos', form.errors)

    def test_form_de_coluna_permite_configurar_totalizador_compativel(self):
        form = ColunaPersonalizadaForm(
            data={
                'nome': 'Consumo total',
                'tipo_dado': ColunaPersonalizada.TipoDado.DECIMAL,
                'opcoes_lista': '',
                'totalizadores_configurados': [
                    TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
                    TotalizadorColunaPersonalizada.TipoTotalizador.MEDIA,
                ],
                'obrigatoria': '',
                'visivel': 'on',
                'ordem': 1,
                'status': ColunaPersonalizada.StatusColuna.ATIVA,
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_form_de_coluna_bloqueia_totalizador_incompativel(self):
        form = ColunaPersonalizadaForm(
            data={
                'nome': 'Texto livre',
                'tipo_dado': ColunaPersonalizada.TipoDado.TEXTO_CURTO,
                'opcoes_lista': '',
                'totalizadores_configurados': [
                    TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
                ],
                'obrigatoria': '',
                'visivel': 'on',
                'ordem': 1,
                'status': ColunaPersonalizada.StatusColuna.ATIVA,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('totalizadores_configurados', form.errors)

    def test_form_de_coluna_limpa_totalizador_incompativel_ao_mudar_tipo(self):
        coluna = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Consumo ajustavel',
            tipo_dado=ColunaPersonalizada.TipoDado.DECIMAL,
            visivel=True,
        )
        totalizador = TotalizadorColunaPersonalizada.objects.create(
            coluna=coluna,
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
            ativo=True,
        )

        form = ColunaPersonalizadaForm(
            data={
                'nome': 'Consumo ajustavel',
                'tipo_dado': ColunaPersonalizada.TipoDado.TEXTO_CURTO,
                'opcoes_lista': '',
                'obrigatoria': '',
                'visivel': 'on',
                'ordem': 0,
                'status': ColunaPersonalizada.StatusColuna.ATIVA,
            },
            instance=coluna,
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        totalizador.refresh_from_db()
        self.assertFalse(totalizador.ativo)

    def test_form_de_coluna_permite_habilitar_filtro_estruturado_em_tipo_elegivel(self):
        form = ColunaPersonalizadaForm(
            data={
                'nome': 'Data filtravel',
                'tipo_dado': ColunaPersonalizada.TipoDado.DATA,
                'opcoes_lista': '',
                'totalizadores_configurados': [],
                'filtro_estruturado': 'on',
                'obrigatoria': '',
                'visivel': 'on',
                'ordem': 2,
                'status': ColunaPersonalizada.StatusColuna.ATIVA,
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        coluna = form.save(commit=False)
        coluna.tabela = self.tabela
        coluna.save()
        self.assertEqual(
            coluna.configuracao_json['filtro'],
            {
                'habilitado': True,
                'operadores': ['entre', 'igual', 'antes', 'depois'],
            },
        )
        self.assertTrue(coluna.filtro_estruturado_habilitado)

    def test_form_de_coluna_limpa_filtro_estruturado_ao_mudar_para_tipo_inelegivel(self):
        coluna = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Valor filtravel',
            tipo_dado=ColunaPersonalizada.TipoDado.DECIMAL,
            visivel=True,
            configuracao_json={
                'filtro': {
                    'habilitado': True,
                    'operadores': ['entre', 'igual', 'maior', 'menor'],
                }
            },
        )

        form = ColunaPersonalizadaForm(
            data={
                'nome': 'Valor filtravel',
                'tipo_dado': ColunaPersonalizada.TipoDado.TEXTO_CURTO,
                'opcoes_lista': '',
                'totalizadores_configurados': [],
                'filtro_estruturado': 'on',
                'obrigatoria': '',
                'visivel': 'on',
                'ordem': 0,
                'status': ColunaPersonalizada.StatusColuna.ATIVA,
            },
            instance=coluna,
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        coluna.refresh_from_db()
        self.assertNotIn('filtro', coluna.configuracao_json)
        self.assertFalse(coluna.filtro_estruturado_habilitado)

    def test_form_de_coluna_preserva_opcoes_da_lista_ao_editar_coluna_inelegivel_para_filtro(self):
        coluna = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Categoria filtrada',
            tipo_dado=ColunaPersonalizada.TipoDado.LISTA_OPCOES,
            visivel=True,
            configuracao_json={'opcoes': ['Material', 'Limpeza', 'Apoio']},
        )

        form = ColunaPersonalizadaForm(
            data={
                'nome': 'Categoria filtrada',
                'tipo_dado': ColunaPersonalizada.TipoDado.LISTA_OPCOES,
                'opcoes_lista': 'Material\nLimpeza\nApoio',
                'totalizadores_configurados': [],
                'filtro_estruturado': '',
                'obrigatoria': '',
                'visivel': 'on',
                'ordem': 0,
                'status': ColunaPersonalizada.StatusColuna.ATIVA,
            },
            instance=coluna,
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        coluna.refresh_from_db()
        self.assertEqual(coluna.configuracao_json, {'opcoes': ['Material', 'Limpeza', 'Apoio']})

    def test_coluna_criada_fica_vinculada_a_tabela_correta(self):
        self._login_com_permissoes(
            'user-coluna-vinculo',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )

        self.client.post(
            reverse('financeiro:tabela-personalizada-coluna-create', kwargs={'tabela_id': self.outra_tabela.pk}),
            data={
                'nome': 'Codigo secundario',
                'tipo_dado': ColunaPersonalizada.TipoDado.TEXTO_CURTO,
                'opcoes_lista': '',
                'obrigatoria': '',
                'visivel': 'on',
                'ordem': 2,
                'status': ColunaPersonalizada.StatusColuna.ATIVA,
            },
        )

        coluna = ColunaPersonalizada.objects.get(nome='Codigo secundario')
        self.assertEqual(coluna.tabela, self.outra_tabela)

    def test_criacao_de_coluna_gera_auditoria(self):
        self._login_com_permissoes(
            'user-coluna-auditoria-create',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )

        response = self.client.post(
            reverse('financeiro:tabela-personalizada-coluna-create', kwargs={'tabela_id': self.tabela.pk}),
            data={
                'nome': 'Campo auditado',
                'tipo_dado': ColunaPersonalizada.TipoDado.TEXTO_CURTO,
                'opcoes_lista': '',
                'totalizadores_configurados': [],
                'filtro_estruturado': '',
                'obrigatoria': '',
                'visivel': 'on',
                'ordem': 6,
                'status': ColunaPersonalizada.StatusColuna.ATIVA,
            },
        )

        self.assertEqual(response.status_code, 302)
        coluna = ColunaPersonalizada.objects.get(nome='Campo auditado')
        log = self._ultimo_log_modelo('ColunaPersonalizada', registro_id=coluna.pk)
        self.assertIsNotNone(log)
        self.assertEqual(log.acao, AuditoriaFinanceiro.AcaoAuditoria.CREATE)
        self.assertIn('nome', log.campos_alterados)

    def test_edicao_de_coluna_gera_auditoria_com_opcoes_de_lista(self):
        coluna = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Categoria interna',
            tipo_dado=ColunaPersonalizada.TipoDado.LISTA_OPCOES,
            configuracao_json={'opcoes': ['A']},
        )
        self._login_com_permissoes(
            'user-coluna-auditoria-opcoes',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )

        response = self.client.post(
            reverse(
                'financeiro:tabela-personalizada-coluna-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': coluna.pk},
            ),
            data={
                'nome': 'Categoria interna',
                'tipo_dado': ColunaPersonalizada.TipoDado.LISTA_OPCOES,
                'opcoes_lista': 'A\nB\nC',
                'totalizadores_configurados': [],
                'filtro_estruturado': '',
                'obrigatoria': '',
                'visivel': 'on',
                'ordem': 0,
                'status': ColunaPersonalizada.StatusColuna.ATIVA,
            },
        )

        self.assertEqual(response.status_code, 302)
        log = self._ultimo_log_modelo('ColunaPersonalizada', registro_id=coluna.pk)
        self.assertIsNotNone(log)
        self.assertIn('configuracao_json', log.campos_alterados)
        self.assertIn('opcoes', log.campos_alterados['configuracao_json']['after'])

    def test_edicao_de_coluna_gera_auditoria_com_filtro_estruturado(self):
        coluna = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Valor filtravel auditado',
            tipo_dado=ColunaPersonalizada.TipoDado.DECIMAL,
            configuracao_json={},
        )
        self._login_com_permissoes(
            'user-coluna-auditoria-filtro',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )

        response = self.client.post(
            reverse(
                'financeiro:tabela-personalizada-coluna-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': coluna.pk},
            ),
            data={
                'nome': coluna.nome,
                'tipo_dado': ColunaPersonalizada.TipoDado.DECIMAL,
                'opcoes_lista': '',
                'totalizadores_configurados': [],
                'filtro_estruturado': 'on',
                'obrigatoria': '',
                'visivel': 'on',
                'ordem': 0,
                'status': ColunaPersonalizada.StatusColuna.ATIVA,
            },
        )

        self.assertEqual(response.status_code, 302)
        log = self._ultimo_log_modelo('ColunaPersonalizada', registro_id=coluna.pk)
        self.assertIsNotNone(log)
        self.assertIn('configuracao_json', log.campos_alterados)
        self.assertIn('filtro', log.campos_alterados['configuracao_json']['after'])

    def test_edicao_de_coluna_gera_auditoria_com_totalizadores(self):
        coluna = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Consumo totalizavel auditado',
            tipo_dado=ColunaPersonalizada.TipoDado.DECIMAL,
        )
        self._login_com_permissoes(
            'user-coluna-auditoria-totalizador',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )

        response = self.client.post(
            reverse(
                'financeiro:tabela-personalizada-coluna-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': coluna.pk},
            ),
            data={
                'nome': coluna.nome,
                'tipo_dado': ColunaPersonalizada.TipoDado.DECIMAL,
                'opcoes_lista': '',
                'totalizadores_configurados': [TotalizadorColunaPersonalizada.TipoTotalizador.SOMA],
                'filtro_estruturado': '',
                'obrigatoria': '',
                'visivel': 'on',
                'ordem': 0,
                'status': ColunaPersonalizada.StatusColuna.ATIVA,
            },
        )

        self.assertEqual(response.status_code, 302)
        log = self._ultimo_log_modelo('ColunaPersonalizada', registro_id=coluna.pk)
        self.assertIsNotNone(log)
        self.assertIn('totalizadores', log.campos_alterados)
        self.assertTrue(log.campos_alterados['totalizadores']['after'])

    def test_edicao_de_coluna_gera_auditoria_com_formula(self):
        fontes = self._criar_colunas_fonte_formula()
        coluna_formula = ColunaPersonalizada.objects.create(
            tabela=self.tabela,
            nome='Formula auditavel',
            tipo_dado=ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA,
            calculada=True,
            visivel=True,
            configuracao_json={
                'formula': {
                    'habilitada': True,
                    'operacao': ColunaPersonalizada.OperacaoFormula.SOMA,
                    'operandos': [fontes['inteiro'].pk, fontes['decimal'].pk],
                    'resultado_tipo': ColunaPersonalizada.TipoDado.DECIMAL,
                    'casas_decimais': 8,
                }
            },
        )
        self._login_com_permissoes(
            'user-coluna-auditoria-formula',
            [
                PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA,
                PermissoesTabelasPersonalizadas.CONFIGURAR_FORMULA,
            ],
        )

        response = self.client.post(
            reverse(
                'financeiro:tabela-personalizada-coluna-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': coluna_formula.pk},
            ),
            data=self._dados_formula_coluna(
                nome='Formula auditavel',
                operacao=ColunaPersonalizada.OperacaoFormula.MULTIPLICACAO,
                operandos=[fontes['inteiro'].pk, fontes['decimal'].pk],
                resultado_tipo=ColunaPersonalizada.TipoDado.DECIMAL,
                casas_decimais=6,
            ),
        )

        self.assertEqual(response.status_code, 302)
        log = self._ultimo_log_modelo('ColunaPersonalizada', registro_id=coluna_formula.pk)
        self.assertIsNotNone(log)
        self.assertIn('configuracao_json', log.campos_alterados)
        self.assertIn('formula', log.campos_alterados['configuracao_json']['after'])

    def test_edicao_nao_permite_manipular_coluna_de_outra_tabela_pela_url(self):
        self._login_com_permissoes(
            'user-coluna-url-errada',
            [PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA],
        )
        coluna_outra_tabela = ColunaPersonalizada.objects.create(
            tabela=self.outra_tabela,
            nome='Campo isolado',
            tipo_dado=ColunaPersonalizada.TipoDado.TEXTO_CURTO,
        )

        response = self.client.get(
            reverse(
                'financeiro:tabela-personalizada-coluna-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': coluna_outra_tabela.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_usuario_com_permissao_visualizar_acessa_listagem_de_linhas(self):
        colunas = self._criar_colunas_para_linhas()
        linha = self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-list',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Preenchimento de linhas')
        self.assertContains(response, 'Sabao liquido')
        self.assertContains(response, 'Limpeza')
        self.assertContains(response, 'Sim')
        self.assertContains(response, 'R$ 50.72')
        self.assertContains(response, '1.01499912')
        self.assertContains(response, '12.3456%')
        self.assertContains(response, 'Campo calculado futuro')
        self.assertContains(response, 'Calculada')
        self.assertNotContains(response, 'Campo oculto')
        self.assertNotContains(response, 'Campo arquivado')
        self.assertEqual(
            self._valor_renderizado_coluna(response, 'Campo calculado futuro', linha_pk=linha.pk),
            '5,01499912',
        )

    def test_criacao_de_linha_gera_auditoria_sem_valor_calculado(self):
        colunas = self._criar_colunas_para_linhas()
        self._login_com_permissoes(
            'user-linha-auditoria-create',
            [PermissoesTabelasPersonalizadas.PREENCHER_LINHAS],
        )

        response = self.client.post(
            reverse('financeiro:tabela-personalizada-linha-create', kwargs={'tabela_id': self.tabela.pk}),
            data={
                self._campo_coluna(colunas['texto']): 'Linha auditada',
                self._campo_coluna(colunas['inteiro']): '5',
                self._campo_coluna(colunas['monetario']): '10,20',
            },
        )

        self.assertEqual(response.status_code, 302)
        linha = LinhaTabelaPersonalizada.objects.filter(tabela=self.tabela).latest('pk')
        log = self._ultimo_log_modelo('LinhaTabelaPersonalizada', registro_id=linha.pk)
        self.assertIsNotNone(log)
        self.assertEqual(log.acao, AuditoriaFinanceiro.AcaoAuditoria.CREATE)
        self.assertIn('valores', log.campos_alterados)
        serialized = json.dumps(log.campos_alterados, ensure_ascii=False)
        self.assertNotIn('valor_calculado', serialized)

    def test_edicao_de_linha_gera_auditoria_com_before_after(self):
        colunas = self._criar_colunas_para_linhas()
        linha = self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-auditoria-update',
            [PermissoesTabelasPersonalizadas.EDITAR_LINHAS],
        )

        response = self.client.post(
            reverse(
                'financeiro:tabela-personalizada-linha-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': linha.pk},
            ),
            data={
                self._campo_coluna(colunas['texto']): 'Sabao alterado',
                self._campo_coluna(colunas['inteiro']): '9',
                self._campo_coluna(colunas['monetario']): '22,30',
                self._campo_coluna(colunas['decimal']): '1,01499912',
                self._campo_coluna(colunas['percentual']): '12,3456',
                self._campo_coluna(colunas['data']): '2026-05-08',
                self._campo_coluna(colunas['competencia']): '05/2026',
                self._campo_coluna(colunas['booleano']): '1',
                self._campo_coluna(colunas['lista']): 'Limpeza',
            },
        )

        self.assertEqual(response.status_code, 302)
        log = self._ultimo_log_modelo('LinhaTabelaPersonalizada', registro_id=linha.pk)
        self.assertIsNotNone(log)
        self.assertEqual(log.acao, AuditoriaFinanceiro.AcaoAuditoria.UPDATE)
        self.assertIn('valores', log.campos_alterados)
        self.assertTrue(log.campos_alterados['valores']['before'])
        self.assertTrue(log.campos_alterados['valores']['after'])

    def test_exportacao_xlsx_nao_gera_auditoria(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-auditoria-sem-xlsx',
            [
                PermissoesTabelasPersonalizadas.VISUALIZAR,
                PermissoesTabelasPersonalizadas.EXPORTAR,
            ],
        )
        total_antes = AuditoriaFinanceiro.objects.count()

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-export-xlsx', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AuditoriaFinanceiro.objects.count(), total_antes)

    def test_listagem_e_busca_nao_geram_auditoria(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-auditoria-sem-leitura',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )
        total_antes = AuditoriaFinanceiro.objects.count()

        response_lista = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )
        response_busca = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': 'sabao'},
        )

        self.assertEqual(response_lista.status_code, 200)
        self.assertEqual(response_busca.status_code, 200)
        self.assertEqual(AuditoriaFinanceiro.objects.count(), total_antes)

    def test_listagem_de_linhas_calcula_subtracao_multiplicacao_e_divisao_em_tempo_de_leitura(self):
        colunas = self._criar_colunas_para_linhas()
        linha = self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-formula-operacoes',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )
        url = reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})

        self._configurar_formula_coluna(
            colunas['formula'],
            operacao=ColunaPersonalizada.OperacaoFormula.SUBTRACAO,
            operandos=[colunas['percentual'].pk, colunas['inteiro'].pk],
            resultado_tipo=ColunaPersonalizada.TipoDado.DECIMAL,
            casas_decimais=4,
        )
        response_subtracao = self.client.get(url)
        self.assertEqual(
            self._valor_renderizado_coluna(response_subtracao, 'Campo calculado futuro', linha_pk=linha.pk),
            '8,3456',
        )

        self._configurar_formula_coluna(
            colunas['formula'],
            operacao=ColunaPersonalizada.OperacaoFormula.MULTIPLICACAO,
            operandos=[colunas['percentual'].pk, colunas['inteiro'].pk],
            resultado_tipo=ColunaPersonalizada.TipoDado.DECIMAL,
            casas_decimais=4,
        )
        response_multiplicacao = self.client.get(url)
        self.assertEqual(
            self._valor_renderizado_coluna(response_multiplicacao, 'Campo calculado futuro', linha_pk=linha.pk),
            '49,3824',
        )

        self._configurar_formula_coluna(
            colunas['formula'],
            operacao=ColunaPersonalizada.OperacaoFormula.DIVISAO,
            operandos=[colunas['percentual'].pk, colunas['inteiro'].pk],
            resultado_tipo=ColunaPersonalizada.TipoDado.DECIMAL,
            casas_decimais=4,
        )
        response_divisao = self.client.get(url)
        self.assertEqual(response_divisao.status_code, 200)
        self.assertEqual(
            self._valor_renderizado_coluna(response_divisao, 'Campo calculado futuro', linha_pk=linha.pk),
            '3,0864',
        )

    def test_listagem_de_linhas_formata_resultado_monetario_com_duas_casas(self):
        colunas = self._criar_colunas_para_linhas()
        linha = self._criar_linha_com_valores(colunas)
        self._configurar_formula_coluna(
            colunas['formula'],
            operacao=ColunaPersonalizada.OperacaoFormula.SOMA,
            operandos=[colunas['monetario'].pk, colunas['inteiro'].pk],
            resultado_tipo=ColunaPersonalizada.TipoDado.MONETARIO,
            casas_decimais=2,
        )
        self._login_com_permissoes(
            'user-linha-formula-monetaria',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(
            self._valor_renderizado_coluna(response, 'Campo calculado futuro', linha_pk=linha.pk),
            'R$ 54,72',
        )

    def test_listagem_de_linhas_deixa_formula_vazia_quando_operando_esta_ausente_ou_divisao_tem_zero(self):
        colunas = self._criar_colunas_para_linhas()
        linha_sem_decimal = self._criar_linha_com_valores(colunas)
        ValorTabelaPersonalizada.objects.filter(
            linha=linha_sem_decimal,
            coluna=colunas['decimal'],
        ).delete()
        linha_divisao_zero = self._criar_segunda_linha_com_valores(colunas)
        ValorTabelaPersonalizada.objects.filter(
            linha=linha_divisao_zero,
            coluna=colunas['inteiro'],
        ).update(valor_numero=Decimal('0'))
        self._configurar_formula_coluna(
            colunas['formula'],
            operacao=ColunaPersonalizada.OperacaoFormula.DIVISAO,
            operandos=[colunas['decimal'].pk, colunas['inteiro'].pk],
            resultado_tipo=ColunaPersonalizada.TipoDado.DECIMAL,
            casas_decimais=4,
        )
        self._login_com_permissoes(
            'user-linha-formula-vazia',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self._valor_renderizado_coluna(response, 'Campo calculado futuro', linha_pk=linha_sem_decimal.pk),
            '',
        )
        self.assertEqual(
            self._valor_renderizado_coluna(response, 'Campo calculado futuro', linha_pk=linha_divisao_zero.pk),
            '',
        )

    def test_tela_de_linhas_exibe_filtros_apenas_quando_houver_coluna_habilitada(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._habilitar_filtro_estruturado(colunas['data'])
        self._login_com_permissoes(
            'user-linha-com-filtro',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Filtros estruturados')
        self.assertContains(response, 'Data de entrada')
        self.assertContains(response, 'Operadores: Entre, Igual, Antes, Depois.')

    def test_tela_de_linhas_nao_exibe_filtros_quando_nao_houver_coluna_habilitada(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-sem-filtro',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Filtros estruturados')

    def test_totalizador_nao_aparece_sem_configuracao_na_tela_de_linhas(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-sem-totalizador',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Totalizadores')

    def test_totalizador_aparece_no_rodape_com_soma_decimal_monetaria_percentual_e_datas(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['decimal'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['monetario'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['percentual'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['data'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.MINIMO,
        )
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['data'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.MAXIMO,
        )
        self._login_com_permissoes(
            'user-linha-totalizadores',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Totalizadores')
        self.assertContains(response, '<strong>Soma:</strong> 3.015', html=True)
        self.assertContains(response, '<strong>Soma:</strong> R$ 70.62', html=True)
        self.assertContains(response, '<strong>Soma:</strong> 16.8456%', html=True)
        self.assertContains(response, '<strong>Minimo:</strong> 08/05/2026', html=True)
        self.assertContains(response, '<strong>Maximo:</strong> 10/05/2026', html=True)

    def test_totalizador_de_contagem_simples_para_texto_booleano_e_lista(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['texto'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.CONTAGEM,
        )
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['booleano'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.CONTAGEM,
        )
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['lista'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.CONTAGEM,
        )
        self._login_com_permissoes(
            'user-linha-totalizadores-contagem',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<strong>Contagem:</strong> 2', html=True, count=3)

    def test_totalizador_ignora_linhas_arquivadas(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas, status=LinhaTabelaPersonalizada.StatusLinha.ARQUIVADA)
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['monetario'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['decimal'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['percentual'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )
        self._login_com_permissoes(
            'user-linha-totalizador-ignora-arquivada',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<strong>Soma:</strong> R$ 50.72', html=True)
        self.assertNotContains(response, '<strong>Soma:</strong> R$ 70.62', html=True)

    def test_busca_encontra_linha_por_texto(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-busca-texto',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': 'detergente'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Detergente concentrado')
        self.assertNotContains(response, 'Sabao liquido')

    def test_busca_encontra_linha_por_lista_de_opcoes(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-busca-lista',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': 'material'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Detergente concentrado')
        self.assertNotContains(response, 'Sabao liquido')

    def test_busca_encontra_linha_por_mes_competencia(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-busca-competencia',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': '06/2026'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Detergente concentrado')
        self.assertNotContains(response, 'Sabao liquido')

    def test_busca_por_numero_funciona_de_forma_simples(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-busca-numero',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': '50,72'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sabao liquido')
        self.assertNotContains(response, 'Detergente concentrado')

    def test_busca_nao_considera_coluna_invisivel(self):
        colunas = self._criar_colunas_para_linhas()
        linha = self._criar_linha_com_valores(colunas)
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['invisivel'],
            valor_texto='segredo-invisivel',
        )
        self._login_com_permissoes(
            'user-linha-busca-invisivel',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': 'segredo-invisivel'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhuma linha encontrada para a busca informada.')
        self.assertNotContains(response, 'Sabao liquido')

    def test_busca_nao_considera_coluna_arquivada(self):
        colunas = self._criar_colunas_para_linhas()
        linha = self._criar_linha_com_valores(colunas)
        ValorTabelaPersonalizada.objects.create(
            linha=linha,
            coluna=colunas['arquivada'],
            valor_texto='segredo-arquivado',
        )
        self._login_com_permissoes(
            'user-linha-busca-arquivada',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': 'segredo-arquivado'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhuma linha encontrada para a busca informada.')
        self.assertNotContains(response, 'Sabao liquido')

    def test_busca_encontra_linha_por_valor_calculado_decimal(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-busca-formula',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': '5,01499912'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sabao liquido')
        self.assertNotContains(response, 'Nenhuma linha encontrada para a busca informada.')

    def test_busca_encontra_linha_por_valor_calculado_monetario(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._configurar_formula_coluna(
            colunas['formula'],
            operacao=ColunaPersonalizada.OperacaoFormula.SOMA,
            operandos=[colunas['monetario'].pk, colunas['inteiro'].pk],
            resultado_tipo=ColunaPersonalizada.TipoDado.MONETARIO,
            casas_decimais=2,
        )
        self._login_com_permissoes(
            'user-linha-busca-formula-monetaria',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': '54,72'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sabao liquido')
        self.assertNotContains(response, 'Nenhuma linha encontrada para a busca informada.')

    def test_busca_nao_considera_coluna_calculada_invisivel_inativa_ou_sem_formula_valida(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-busca-formula-invalida',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        colunas['formula'].visivel = False
        colunas['formula'].save(update_fields=['visivel'])
        response_invisivel = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': '5,01499912'},
        )
        self.assertContains(response_invisivel, 'Nenhuma linha encontrada para a busca informada.')

        colunas['formula'].visivel = True
        colunas['formula'].status = ColunaPersonalizada.StatusColuna.ARQUIVADA
        colunas['formula'].save(update_fields=['visivel', 'status'])
        response_arquivada = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': '5,01499912'},
        )
        self.assertContains(response_arquivada, 'Nenhuma linha encontrada para a busca informada.')

        colunas['formula'].status = ColunaPersonalizada.StatusColuna.ATIVA
        colunas['formula'].save(update_fields=['status'])
        ColunaPersonalizada.objects.filter(pk=colunas['formula'].pk).update(configuracao_json={})
        response_sem_formula = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': '5,01499912'},
        )
        self.assertContains(response_sem_formula, 'Nenhuma linha encontrada para a busca informada.')

    def test_busca_restringe_resultado_a_tabela_correta(self):
        coluna_outra_tabela = ColunaPersonalizada.objects.create(
            tabela=self.outra_tabela,
            nome='Descricao secundaria',
            tipo_dado=ColunaPersonalizada.TipoDado.TEXTO_CURTO,
            visivel=True,
        )
        linha_outra_tabela = LinhaTabelaPersonalizada.objects.create(
            tabela=self.outra_tabela,
            criado_por=self.user,
            atualizado_por=self.user,
        )
        ValorTabelaPersonalizada.objects.create(
            linha=linha_outra_tabela,
            coluna=coluna_outra_tabela,
            valor_texto='item-outra-tabela',
        )
        self._login_com_permissoes(
            'user-linha-busca-outra-tabela',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': 'item-outra-tabela'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhuma linha encontrada para a busca informada.')
        self.assertEqual(response.context['linhas_renderizadas'], [])

    def test_busca_sem_resultado_exibe_mensagem_clara_e_botao_limpar(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-busca-sem-resultado',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': 'nao-encontrado'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhuma linha encontrada para a busca informada.')
        self.assertContains(response, 'Limpar')

    def test_filtro_de_data_funciona_com_entre_igual_antes_e_depois(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        self._habilitar_filtro_estruturado(colunas['data'])
        self._login_com_permissoes(
            'user-linha-filtro-data',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        url = reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})

        response_igual = self.client.get(
            url,
            self._dados_filtro_estruturado(
                colunas['data'],
                operador=ColunaPersonalizada.OperadorFiltro.IGUAL,
                valor='08/05/2026',
            ),
        )
        self.assertContains(response_igual, 'Sabao liquido')
        self.assertNotContains(response_igual, 'Detergente concentrado')

        response_antes = self.client.get(
            url,
            self._dados_filtro_estruturado(
                colunas['data'],
                operador=ColunaPersonalizada.OperadorFiltro.ANTES,
                valor='09/05/2026',
            ),
        )
        self.assertContains(response_antes, 'Sabao liquido')
        self.assertNotContains(response_antes, 'Detergente concentrado')

        response_depois = self.client.get(
            url,
            self._dados_filtro_estruturado(
                colunas['data'],
                operador=ColunaPersonalizada.OperadorFiltro.DEPOIS,
                valor='09/05/2026',
            ),
        )
        self.assertContains(response_depois, 'Detergente concentrado')
        self.assertNotContains(response_depois, 'Sabao liquido')

        response_entre = self.client.get(
            url,
            self._dados_filtro_estruturado(
                colunas['data'],
                operador=ColunaPersonalizada.OperadorFiltro.ENTRE,
                inicio='08/05/2026',
                fim='09/05/2026',
            ),
        )
        self.assertContains(response_entre, 'Sabao liquido')
        self.assertNotContains(response_entre, 'Detergente concentrado')

    def test_filtro_de_competencia_funciona_com_igual_e_entre(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        self._habilitar_filtro_estruturado(colunas['competencia'])
        self._login_com_permissoes(
            'user-linha-filtro-competencia',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        url = reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        response_igual = self.client.get(
            url,
            self._dados_filtro_estruturado(
                colunas['competencia'],
                operador=ColunaPersonalizada.OperadorFiltro.IGUAL,
                valor='06/2026',
            ),
        )
        self.assertContains(response_igual, 'Detergente concentrado')
        self.assertNotContains(response_igual, 'Sabao liquido')

        response_entre = self.client.get(
            url,
            self._dados_filtro_estruturado(
                colunas['competencia'],
                operador=ColunaPersonalizada.OperadorFiltro.ENTRE,
                inicio='05/2026',
                fim='06/2026',
            ),
        )
        self.assertContains(response_entre, 'Detergente concentrado')
        self.assertContains(response_entre, 'Sabao liquido')

    def test_filtro_numerico_funciona_com_entre_igual_maior_menor_e_aceita_virgula_ou_ponto(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        self._habilitar_filtro_estruturado(colunas['decimal'])
        self._login_com_permissoes(
            'user-linha-filtro-numerico',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        url = reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})

        response_igual_virgula = self.client.get(
            url,
            self._dados_filtro_estruturado(
                colunas['decimal'],
                operador=ColunaPersonalizada.OperadorFiltro.IGUAL,
                valor='1,01499912',
            ),
        )
        self.assertContains(response_igual_virgula, 'Sabao liquido')
        self.assertNotContains(response_igual_virgula, 'Detergente concentrado')

        response_igual_ponto = self.client.get(
            url,
            self._dados_filtro_estruturado(
                colunas['decimal'],
                operador=ColunaPersonalizada.OperadorFiltro.IGUAL,
                valor='2.00000088',
            ),
        )
        self.assertContains(response_igual_ponto, 'Detergente concentrado')
        self.assertNotContains(response_igual_ponto, 'Sabao liquido')

        response_maior = self.client.get(
            url,
            self._dados_filtro_estruturado(
                colunas['decimal'],
                operador=ColunaPersonalizada.OperadorFiltro.MAIOR,
                valor='2',
            ),
        )
        self.assertContains(response_maior, 'Detergente concentrado')
        self.assertNotContains(response_maior, 'Sabao liquido')

        response_menor = self.client.get(
            url,
            self._dados_filtro_estruturado(
                colunas['decimal'],
                operador=ColunaPersonalizada.OperadorFiltro.MENOR,
                valor='2',
            ),
        )
        self.assertContains(response_menor, 'Sabao liquido')
        self.assertNotContains(response_menor, 'Detergente concentrado')

        response_entre = self.client.get(
            url,
            self._dados_filtro_estruturado(
                colunas['decimal'],
                operador=ColunaPersonalizada.OperadorFiltro.ENTRE,
                inicio='1',
                fim='1,5',
            ),
        )
        self.assertContains(response_entre, 'Sabao liquido')
        self.assertNotContains(response_entre, 'Detergente concentrado')

    def test_busca_textual_combina_valor_calculado_com_filtro_estruturado_comum(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        self._habilitar_filtro_estruturado(colunas['competencia'])
        self._login_com_permissoes(
            'user-linha-busca-com-filtro',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            self._dados_filtro_estruturado(
                colunas['competencia'],
                operador=ColunaPersonalizada.OperadorFiltro.IGUAL,
                valor='05/2026',
                busca='5,01499912',
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sabao liquido')
        self.assertNotContains(response, 'Detergente concentrado')

    def test_totalizadores_refletem_apenas_linhas_filtradas(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['monetario'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['decimal'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['percentual'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )
        self._login_com_permissoes(
            'user-linha-totalizador-filtrado',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': 'detergente'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<strong>Soma:</strong> R$ 19.90', html=True)
        self.assertNotContains(response, '<strong>Soma:</strong> R$ 70.62', html=True)

    def test_totalizadores_refletem_busca_e_filtro_estruturado(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        self._habilitar_filtro_estruturado(colunas['competencia'])
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['monetario'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )
        self._login_com_permissoes(
            'user-linha-totalizador-busca-filtro',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            self._dados_filtro_estruturado(
                colunas['competencia'],
                operador=ColunaPersonalizada.OperadorFiltro.IGUAL,
                valor='05/2026',
                busca='sabao',
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<strong>Soma:</strong> R$ 50.72', html=True)
        self.assertNotContains(response, '<strong>Soma:</strong> R$ 70.62', html=True)

    def test_botao_exportar_xlsx_aparece_apenas_para_usuario_com_permissao(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-exporta-botao',
            [
                PermissoesTabelasPersonalizadas.VISUALIZAR,
                PermissoesTabelasPersonalizadas.EXPORTAR,
            ],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse('financeiro:tabela-personalizada-linha-export-xlsx', kwargs={'tabela_id': self.tabela.pk}),
        )
        self.assertContains(response, 'Exportar XLSX')

    def test_botao_exportar_xlsx_nao_aparece_sem_permissao(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-nao-exporta-botao',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Exportar XLSX')

    def test_usuario_com_permissao_exporta_xlsx_de_linhas(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['monetario'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['decimal'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['percentual'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )
        self._login_com_permissoes(
            'user-linha-exporta',
            [PermissoesTabelasPersonalizadas.EXPORTAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-export-xlsx', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        self.assertIn('.xlsx', response['Content-Disposition'])
        linhas = self._ler_linhas_xlsx(response.content)
        conteudo = '\n'.join(' | '.join(linha) for linha in linhas)
        self.assertIn('Controle de almoxarifado - controle interno sem efeito financeiro oficial', conteudo)
        self.assertIn('Descricao do item', conteudo)
        self.assertIn('Valor unitario', conteudo)
        self.assertIn('Sabao liquido', conteudo)
        self.assertIn('Detergente concentrado', conteudo)
        self.assertIn('R$ 50,72', conteudo)
        self.assertIn('1,01499912', conteudo)
        self.assertIn('12,3456%', conteudo)
        self.assertIn('Campo calculado futuro', conteudo)
        self.assertIn('5,01499912', conteudo)
        self.assertIn('Soma: R$ 70,62', conteudo)
        self.assertIn('Soma: 3,015', conteudo)
        self.assertIn('Soma: 16,8456%', conteudo)
        self.assertNotIn('Campo oculto', conteudo)
        self.assertNotIn('Campo arquivado', conteudo)
        self.assertNotIn('=SOMA(', conteudo)
        self.assertNotIn('operacao', conteudo)
        self.assertNotIn('operandos', conteudo)

    def test_exportacao_xlsx_inclui_valor_calculado_monetario_em_padrao_brasileiro(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._configurar_formula_coluna(
            colunas['formula'],
            operacao=ColunaPersonalizada.OperacaoFormula.SOMA,
            operandos=[colunas['monetario'].pk, colunas['inteiro'].pk],
            resultado_tipo=ColunaPersonalizada.TipoDado.MONETARIO,
            casas_decimais=2,
        )
        self._login_com_permissoes(
            'user-linha-exporta-formula-monetaria',
            [PermissoesTabelasPersonalizadas.EXPORTAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-export-xlsx', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        conteudo = '\n'.join(' | '.join(linha) for linha in self._ler_linhas_xlsx(response.content))
        self.assertIn('Campo calculado futuro', conteudo)
        self.assertIn('R$ 54,72', conteudo)

    def test_usuario_sem_permissao_exportar_recebe_403(self):
        self._login_com_permissoes(
            'user-linha-sem-exportar',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-export-xlsx', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 403)

    def test_exportacao_xlsx_respeita_busca_ativa(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['monetario'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )
        self._login_com_permissoes(
            'user-linha-exporta-busca',
            [PermissoesTabelasPersonalizadas.EXPORTAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-export-xlsx', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': 'detergente'},
        )

        self.assertEqual(response.status_code, 200)
        linhas = self._ler_linhas_xlsx(response.content)
        conteudo = '\n'.join(' | '.join(linha) for linha in linhas)
        self.assertIn('Detergente concentrado', conteudo)
        self.assertNotIn('Sabao liquido', conteudo)
        self.assertIn('Soma: R$ 19,90', conteudo)
        self.assertNotIn('Soma: R$ 70,62', conteudo)

    def test_exportacao_xlsx_respeita_busca_por_valor_calculado(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        self._configurar_formula_coluna(
            colunas['formula'],
            operacao=ColunaPersonalizada.OperacaoFormula.SOMA,
            operandos=[colunas['monetario'].pk, colunas['inteiro'].pk],
            resultado_tipo=ColunaPersonalizada.TipoDado.MONETARIO,
            casas_decimais=2,
        )
        self._login_com_permissoes(
            'user-linha-exporta-busca-formula',
            [PermissoesTabelasPersonalizadas.EXPORTAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-export-xlsx', kwargs={'tabela_id': self.tabela.pk}),
            {'busca': '54,72'},
        )

        self.assertEqual(response.status_code, 200)
        conteudo = '\n'.join(' | '.join(linha) for linha in self._ler_linhas_xlsx(response.content))
        self.assertIn('Sabao liquido', conteudo)
        self.assertNotIn('Detergente concentrado', conteudo)
        self.assertIn('R$ 54,72', conteudo)

    def test_exportacao_xlsx_respeita_busca_e_filtro_estruturado(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        self._habilitar_filtro_estruturado(colunas['competencia'])
        TotalizadorColunaPersonalizada.objects.create(
            coluna=colunas['monetario'],
            tipo_totalizador=TotalizadorColunaPersonalizada.TipoTotalizador.SOMA,
        )
        self._login_com_permissoes(
            'user-linha-exporta-busca-filtro',
            [PermissoesTabelasPersonalizadas.EXPORTAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-export-xlsx', kwargs={'tabela_id': self.tabela.pk}),
            self._dados_filtro_estruturado(
                colunas['competencia'],
                operador=ColunaPersonalizada.OperadorFiltro.IGUAL,
                valor='05/2026',
                busca='sabao',
            ),
        )

        self.assertEqual(response.status_code, 200)
        linhas = self._ler_linhas_xlsx(response.content)
        conteudo = '\n'.join(' | '.join(linha) for linha in linhas)
        self.assertIn('Sabao liquido', conteudo)
        self.assertNotIn('Detergente concentrado', conteudo)
        self.assertIn('Soma: R$ 50,72', conteudo)
        self.assertNotIn('Soma: R$ 70,62', conteudo)

    def test_exportacao_xlsx_deixa_celula_vazia_para_formula_com_operando_ausente_ou_divisao_por_zero(self):
        colunas = self._criar_colunas_para_linhas()
        linha_sem_decimal = self._criar_linha_com_valores(colunas)
        ValorTabelaPersonalizada.objects.filter(
            linha=linha_sem_decimal,
            coluna=colunas['decimal'],
        ).delete()
        linha_divisao_zero = self._criar_segunda_linha_com_valores(colunas)
        ValorTabelaPersonalizada.objects.filter(
            linha=linha_divisao_zero,
            coluna=colunas['inteiro'],
        ).update(valor_numero=Decimal('0'))
        self._configurar_formula_coluna(
            colunas['formula'],
            operacao=ColunaPersonalizada.OperacaoFormula.DIVISAO,
            operandos=[colunas['decimal'].pk, colunas['inteiro'].pk],
            resultado_tipo=ColunaPersonalizada.TipoDado.DECIMAL,
            casas_decimais=4,
        )
        self._login_com_permissoes(
            'user-linha-exporta-formula-vazia',
            [PermissoesTabelasPersonalizadas.EXPORTAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-export-xlsx', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        linhas = self._ler_linhas_xlsx(response.content)
        cabecalho = linhas[1]
        indice_formula = cabecalho.index('Campo calculado futuro')
        self.assertEqual(linhas[2][indice_formula], '')
        self.assertEqual(linhas[3][indice_formula], '')

    def test_filtro_estruturado_invalido_exibe_mensagem_clara_sem_quebrar_pagina(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._criar_segunda_linha_com_valores(colunas)
        self._habilitar_filtro_estruturado(colunas['data'])
        self._login_com_permissoes(
            'user-linha-filtro-invalido',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
            self._dados_filtro_estruturado(
                colunas['data'],
                operador=ColunaPersonalizada.OperadorFiltro.IGUAL,
                valor='2026-05-08',
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Informe uma data valida no formato DD/MM/AAAA.')
        self.assertContains(response, 'Sabao liquido')
        self.assertContains(response, 'Detergente concentrado')

    def test_exportacao_xlsx_nao_altera_dados(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        quantidades_antes = (
            LinhaTabelaPersonalizada.objects.count(),
            ValorTabelaPersonalizada.objects.count(),
        )
        self._login_com_permissoes(
            'user-linha-exporta-sem-escrita',
            [PermissoesTabelasPersonalizadas.EXPORTAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-export-xlsx', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            quantidades_antes,
            (
                LinhaTabelaPersonalizada.objects.count(),
                ValorTabelaPersonalizada.objects.count(),
            ),
        )

    def test_usuario_sem_permissao_visualizar_nao_acessa_listagem_de_linhas(self):
        self._login_com_permissoes(
            'user-linha-list-sem-permissao',
            [PermissoesTabelasPersonalizadas.PREENCHER_LINHAS],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 403)

    def test_usuario_com_permissao_preencher_acessa_criacao_de_linha(self):
        self._criar_colunas_para_linhas()
        self._login_com_permissoes(
            'user-linha-criar',
            [PermissoesTabelasPersonalizadas.PREENCHER_LINHAS],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-create', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'preenchimento basico de linhas')

    def test_usuario_sem_permissao_preencher_nao_acessa_criacao_de_linha(self):
        self._criar_colunas_para_linhas()
        self._login_com_permissoes(
            'user-linha-criar-sem-permissao',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-create', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 403)

    def test_usuario_com_permissao_editar_acessa_edicao_de_linha(self):
        colunas = self._criar_colunas_para_linhas()
        linha = self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-editar',
            [PermissoesTabelasPersonalizadas.EDITAR_LINHAS],
        )

        response = self.client.get(
            reverse(
                'financeiro:tabela-personalizada-linha-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': linha.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sabao liquido')
        self.assertContains(response, 'Limpeza')

    def test_usuario_sem_permissao_editar_nao_acessa_edicao_de_linha(self):
        colunas = self._criar_colunas_para_linhas()
        linha = self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-editar-sem-permissao',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse(
                'financeiro:tabela-personalizada-linha-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': linha.pk},
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_form_de_linha_nao_expoe_colunas_invisiveis_arquivadas_ou_formula(self):
        colunas = self._criar_colunas_para_linhas()

        form = TabelaPersonalizadaLinhaForm(tabela=self.tabela)

        self.assertIn(self._campo_coluna(colunas['texto']), form.fields)
        self.assertIn(self._campo_coluna(colunas['inteiro']), form.fields)
        self.assertNotIn(self._campo_coluna(colunas['invisivel']), form.fields)
        self.assertNotIn(self._campo_coluna(colunas['arquivada']), form.fields)
        self.assertNotIn(self._campo_coluna(colunas['formula']), form.fields)

    def test_form_de_linha_lista_opcoes_usa_opcoes_configuradas(self):
        colunas = self._criar_colunas_para_linhas()

        form = TabelaPersonalizadaLinhaForm(tabela=self.tabela)
        choices = list(form.fields[self._campo_coluna(colunas['lista'])].choices)

        self.assertEqual(choices[0], ('', 'Selecione'))
        self.assertIn(('Material', 'Material'), choices)
        self.assertIn(('Limpeza', 'Limpeza'), choices)
        self.assertIn(('Apoio', 'Apoio'), choices)

    def test_form_de_linha_respeita_obrigatoriedade(self):
        colunas = self._criar_colunas_para_linhas()
        form = TabelaPersonalizadaLinhaForm(
            data={
                self._campo_coluna(colunas['texto']): '',
                self._campo_coluna(colunas['inteiro']): '',
            },
            tabela=self.tabela,
        )

        self.assertFalse(form.is_valid())
        self.assertIn(self._campo_coluna(colunas['texto']), form.errors)
        self.assertIn(self._campo_coluna(colunas['inteiro']), form.errors)

    def test_model_valor_numero_suporta_oito_casas_decimais_reais(self):
        campo = ValorTabelaPersonalizada._meta.get_field('valor_numero')

        self.assertEqual(campo.max_digits, 20)
        self.assertEqual(campo.decimal_places, 8)

    def test_form_de_linha_aceita_decimal_com_virgula(self):
        colunas = self._criar_colunas_para_linhas()
        dados = self._dados_minimos_linha(colunas)
        dados[self._campo_coluna(colunas['decimal'])] = '1,01499912'

        form = TabelaPersonalizadaLinhaForm(data=dados, tabela=self.tabela)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.cleaned_data[self._campo_coluna(colunas['decimal'])],
            Decimal('1.01499912'),
        )

    def test_form_de_linha_aceita_decimal_com_ponto(self):
        colunas = self._criar_colunas_para_linhas()
        dados = self._dados_minimos_linha(colunas)
        dados[self._campo_coluna(colunas['decimal'])] = '1.01499912'

        form = TabelaPersonalizadaLinhaForm(data=dados, tabela=self.tabela)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.cleaned_data[self._campo_coluna(colunas['decimal'])],
            Decimal('1.01499912'),
        )

    def test_form_de_linha_rejeita_decimal_com_mais_de_oito_casas(self):
        colunas = self._criar_colunas_para_linhas()
        dados = self._dados_minimos_linha(colunas)
        campo = self._campo_coluna(colunas['decimal'])
        dados[campo] = '1,014999123'

        form = TabelaPersonalizadaLinhaForm(data=dados, tabela=self.tabela)

        self.assertFalse(form.is_valid())
        self.assertIn('ate 8 casas decimais', form.errors[campo][0])

    def test_form_de_linha_monetario_aceita_ate_duas_casas(self):
        colunas = self._criar_colunas_para_linhas()
        dados = self._dados_minimos_linha(colunas)
        campo = self._campo_coluna(colunas['monetario'])
        dados[campo] = '10,55'

        form = TabelaPersonalizadaLinhaForm(data=dados, tabela=self.tabela)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data[campo], Decimal('10.55'))

    def test_form_de_linha_monetario_rejeita_mais_de_duas_casas(self):
        colunas = self._criar_colunas_para_linhas()
        dados = self._dados_minimos_linha(colunas)
        campo = self._campo_coluna(colunas['monetario'])
        dados[campo] = '10,555'

        form = TabelaPersonalizadaLinhaForm(data=dados, tabela=self.tabela)

        self.assertFalse(form.is_valid())
        self.assertIn('ate 2 casas decimais', form.errors[campo][0])

    def test_form_de_linha_percentual_aceita_ate_quatro_casas(self):
        colunas = self._criar_colunas_para_linhas()
        dados = self._dados_minimos_linha(colunas)
        campo = self._campo_coluna(colunas['percentual'])
        dados[campo] = '12,3456'

        form = TabelaPersonalizadaLinhaForm(data=dados, tabela=self.tabela)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data[campo], Decimal('12.3456'))

    def test_form_de_linha_em_edicao_formata_valores_iniciais_por_tipo(self):
        colunas = self._criar_colunas_para_linhas()
        linha = self._criar_linha_com_valores(colunas)
        valor_percentual = linha.valores.get(coluna=colunas['percentual'])
        valor_percentual.valor_numero = Decimal('12.34')
        valor_percentual.save()

        form = TabelaPersonalizadaLinhaForm(tabela=self.tabela, linha=linha)

        self.assertEqual(form[self._campo_coluna(colunas['monetario'])].value(), '50,72')
        self.assertEqual(form[self._campo_coluna(colunas['percentual'])].value(), '12,34')
        self.assertEqual(form[self._campo_coluna(colunas['decimal'])].value(), '1,01499912')
        self.assertEqual(form[self._campo_coluna(colunas['inteiro'])].value(), '4')

    def test_edicao_de_linha_aceita_reenvio_sem_mudar_valor_monetario_carregado_pelo_sistema(self):
        colunas = self._criar_colunas_para_linhas()
        linha = self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-edicao-monetario-normalizado',
            [
                PermissoesTabelasPersonalizadas.EDITAR_LINHAS,
                PermissoesTabelasPersonalizadas.VISUALIZAR,
            ],
        )

        response = self.client.post(
            reverse(
                'financeiro:tabela-personalizada-linha-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': linha.pk},
            ),
            data={
                self._campo_coluna(colunas['texto']): 'Sabao liquido',
                self._campo_coluna(colunas['inteiro']): '4',
                self._campo_coluna(colunas['monetario']): '50,72',
                self._campo_coluna(colunas['decimal']): '1,01499912',
                self._campo_coluna(colunas['percentual']): '12,3456',
                self._campo_coluna(colunas['booleano']): '1',
                self._campo_coluna(colunas['lista']): 'Limpeza',
            },
        )

        self.assertRedirects(
            response,
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
        )
        linha.refresh_from_db()
        self.assertEqual(linha.valores.get(coluna=colunas['monetario']).valor_numero, Decimal('50.72'))

    def test_edicao_de_linha_percentual_com_zeros_excedentes_carrega_sem_erro(self):
        colunas = self._criar_colunas_para_linhas()
        linha = self._criar_linha_com_valores(colunas)
        valor_percentual = linha.valores.get(coluna=colunas['percentual'])
        valor_percentual.valor_numero = Decimal('12.34')
        valor_percentual.save()
        self._login_com_permissoes(
            'user-linha-edicao-percentual-normalizado',
            [
                PermissoesTabelasPersonalizadas.EDITAR_LINHAS,
                PermissoesTabelasPersonalizadas.VISUALIZAR,
            ],
        )

        response = self.client.post(
            reverse(
                'financeiro:tabela-personalizada-linha-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': linha.pk},
            ),
            data={
                self._campo_coluna(colunas['texto']): 'Sabao liquido',
                self._campo_coluna(colunas['inteiro']): '4',
                self._campo_coluna(colunas['monetario']): '50,72',
                self._campo_coluna(colunas['decimal']): '1,01499912',
                self._campo_coluna(colunas['percentual']): '12,34',
                self._campo_coluna(colunas['booleano']): '1',
                self._campo_coluna(colunas['lista']): 'Limpeza',
            },
        )

        self.assertRedirects(
            response,
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
        )
        linha.refresh_from_db()
        self.assertEqual(linha.valores.get(coluna=colunas['percentual']).valor_numero, Decimal('12.34'))

    def test_form_de_linha_inteiro_rejeita_valor_decimal(self):
        colunas = self._criar_colunas_para_linhas()
        dados = self._dados_minimos_linha(colunas)
        campo = self._campo_coluna(colunas['inteiro'])
        dados[campo] = '1,5'

        form = TabelaPersonalizadaLinhaForm(data=dados, tabela=self.tabela)

        self.assertFalse(form.is_valid())
        self.assertIn('apenas numeros inteiros', form.errors[campo][0])

    def test_usuario_com_permissao_cria_linha_valida_com_valores_tipados(self):
        colunas = self._criar_colunas_para_linhas()
        usuario = self._login_com_permissoes(
            'user-linha-criacao-valida',
            [
                PermissoesTabelasPersonalizadas.PREENCHER_LINHAS,
                PermissoesTabelasPersonalizadas.VISUALIZAR,
            ],
        )

        response = self.client.post(
            reverse('financeiro:tabela-personalizada-linha-create', kwargs={'tabela_id': self.tabela.pk}),
            data={
                self._campo_coluna(colunas['texto']): 'Vassoura',
                self._campo_coluna(colunas['inteiro']): '3',
                self._campo_coluna(colunas['monetario']): '12.50',
                self._campo_coluna(colunas['data']): '2026-05-08',
                self._campo_coluna(colunas['competencia']): '05/2026',
                self._campo_coluna(colunas['booleano']): '1',
                self._campo_coluna(colunas['lista']): 'Material',
            },
        )

        self.assertRedirects(
            response,
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
        )
        linha = LinhaTabelaPersonalizada.objects.filter(tabela=self.tabela).order_by('-pk').first()
        self.assertEqual(linha.criado_por, usuario)
        self.assertEqual(
            linha.valores.get(coluna=colunas['texto']).valor_texto,
            'Vassoura',
        )
        self.assertEqual(
            linha.valores.get(coluna=colunas['inteiro']).valor_numero,
            Decimal('3'),
        )
        self.assertEqual(
            linha.valores.get(coluna=colunas['monetario']).valor_numero,
            Decimal('12.500000'),
        )
        self.assertEqual(
            linha.valores.get(coluna=colunas['booleano']).valor_booleano,
            True,
        )
        self.assertEqual(
            linha.valores.get(coluna=colunas['lista']).valor_texto,
            'Material',
        )

    def test_usuario_com_permissao_edita_linha_valida(self):
        colunas = self._criar_colunas_para_linhas()
        linha = self._criar_linha_com_valores(colunas)
        usuario = self._login_com_permissoes(
            'user-linha-edicao-valida',
            [
                PermissoesTabelasPersonalizadas.EDITAR_LINHAS,
                PermissoesTabelasPersonalizadas.VISUALIZAR,
            ],
        )

        response = self.client.post(
            reverse(
                'financeiro:tabela-personalizada-linha-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': linha.pk},
            ),
            data={
                self._campo_coluna(colunas['texto']): 'Detergente neutro',
                self._campo_coluna(colunas['inteiro']): '8',
                self._campo_coluna(colunas['monetario']): '19.90',
                self._campo_coluna(colunas['data']): '2026-05-09',
                self._campo_coluna(colunas['competencia']): '06/2026',
                self._campo_coluna(colunas['booleano']): '0',
                self._campo_coluna(colunas['lista']): 'Apoio',
            },
        )

        self.assertRedirects(
            response,
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
        )
        linha.refresh_from_db()
        self.assertEqual(linha.atualizado_por, usuario)
        self.assertEqual(linha.valores.get(coluna=colunas['texto']).valor_texto, 'Detergente neutro')
        self.assertEqual(linha.valores.get(coluna=colunas['inteiro']).valor_numero, Decimal('8'))
        self.assertEqual(linha.valores.get(coluna=colunas['booleano']).valor_booleano, False)
        self.assertEqual(linha.valores.get(coluna=colunas['lista']).valor_texto, 'Apoio')

    def test_edicao_nao_permite_manipular_linha_de_outra_tabela_pela_url(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        linha_outra_tabela = LinhaTabelaPersonalizada.objects.create(
            tabela=self.outra_tabela,
            criado_por=self.user,
            atualizado_por=self.user,
        )
        self._login_com_permissoes(
            'user-linha-url-errada',
            [PermissoesTabelasPersonalizadas.EDITAR_LINHAS],
        )

        response = self.client.get(
            reverse(
                'financeiro:tabela-personalizada-linha-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': linha_outra_tabela.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_listagem_exibe_acao_linhas_para_usuario_com_visualizar(self):
        self._login_com_permissoes(
            'user-menu-linhas-visualizar',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(reverse('financeiro:tabela-personalizada-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
        )
        self.assertContains(response, 'Linhas')

    def test_listagem_de_linhas_com_usuario_apenas_visualizador_oculta_acoes_de_escrita(self):
        colunas = self._criar_colunas_para_linhas()
        self._criar_linha_com_valores(colunas)
        self._login_com_permissoes(
            'user-linha-apenas-visualiza',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            reverse('financeiro:tabela-personalizada-linha-create', kwargs={'tabela_id': self.tabela.pk}),
        )
        self.assertNotContains(
            response,
            reverse(
                'financeiro:tabela-personalizada-linha-update',
                kwargs={'tabela_id': self.tabela.pk, 'pk': LinhaTabelaPersonalizada.objects.filter(tabela=self.tabela).latest('pk').pk},
            ),
        )

    def test_estado_vazio_da_listagem_de_linhas_mostra_cta_para_quem_pode_preencher(self):
        self._criar_colunas_para_linhas()
        LinhaTabelaPersonalizada.objects.filter(tabela=self.tabela).delete()
        self._login_com_permissoes(
            'user-linha-cta-vazio',
            [
                PermissoesTabelasPersonalizadas.VISUALIZAR,
                PermissoesTabelasPersonalizadas.PREENCHER_LINHAS,
            ],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhuma linha cadastrada ainda para esta tabela.')
        self.assertContains(response, 'Cadastre a primeira linha para comecar a preencher este controle interno.')
        self.assertContains(response, '+ Nova linha')
        self.assertContains(
            response,
            reverse('financeiro:tabela-personalizada-linha-create', kwargs={'tabela_id': self.tabela.pk}),
            count=2,
        )

    def test_estado_vazio_da_listagem_de_linhas_nao_mostra_cta_para_usuario_so_visualizador(self):
        self._criar_colunas_para_linhas()
        LinhaTabelaPersonalizada.objects.filter(tabela=self.tabela).delete()
        self._login_com_permissoes(
            'user-linha-cta-vazio-visualizador',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhuma linha cadastrada ainda para esta tabela.')
        self.assertNotContains(response, '+ Nova linha')
        self.assertNotContains(
            response,
            reverse('financeiro:tabela-personalizada-linha-create', kwargs={'tabela_id': self.tabela.pk}),
        )

    def test_criacao_de_linha_nao_impacta_lancamento_financeiro_existente(self):
        colunas = self._criar_colunas_para_linhas()
        pessoa = PessoaFinanceira.objects.create(nome='Pessoa preservada linhas')
        categoria_pai = CategoriaFinanceira.objects.create(
            nome='Categoria pai preservada linhas',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
        )
        categoria = CategoriaFinanceira.objects.create(
            nome='Categoria preservada linhas',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            categoria_pai=categoria_pai,
        )
        conta = ContaFinanceira.objects.create(
            nome='Conta preservada linhas',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 5, 1),
        )
        lancamento = LancamentoFinanceiro.objects.create(
            descricao='Lancamento preservado pelas linhas',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('88.00'),
            data_competencia=date(2026, 5, 2),
            data_pagamento=date(2026, 5, 2),
            pessoa=pessoa,
            categoria=categoria,
            conta=conta,
        )
        self._login_com_permissoes(
            'user-linha-sem-impacto',
            [
                PermissoesTabelasPersonalizadas.PREENCHER_LINHAS,
                PermissoesTabelasPersonalizadas.VISUALIZAR,
            ],
        )

        response = self.client.post(
            reverse('financeiro:tabela-personalizada-linha-create', kwargs={'tabela_id': self.tabela.pk}),
            data={
                self._campo_coluna(colunas['texto']): 'Papel A4',
                self._campo_coluna(colunas['inteiro']): '2',
            },
        )

        self.assertRedirects(
            response,
            reverse('financeiro:tabela-personalizada-linha-list', kwargs={'tabela_id': self.tabela.pk}),
        )
        lancamento.refresh_from_db()
        self.assertEqual(lancamento.descricao, 'Lancamento preservado pelas linhas')
        self.assertEqual(lancamento.valor, Decimal('88.00'))

    def test_listagem_exibe_acao_colunas_apenas_com_permissao_editar_estrutura(self):
        self._login_com_permissoes(
            'user-menu-colunas-com-permissao',
            [
                PermissoesTabelasPersonalizadas.VISUALIZAR,
                PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA,
            ],
        )

        response = self.client.get(reverse('financeiro:tabela-personalizada-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse('financeiro:tabela-personalizada-coluna-list', kwargs={'tabela_id': self.tabela.pk}),
        )
        self.assertContains(response, 'Colunas')

    def test_listagem_oculta_acao_colunas_sem_permissao_editar_estrutura(self):
        self._login_com_permissoes(
            'user-menu-colunas-sem-permissao',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(reverse('financeiro:tabela-personalizada-list'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            reverse('financeiro:tabela-personalizada-coluna-list', kwargs={'tabela_id': self.tabela.pk}),
        )

    def test_listagem_exibe_estado_vazio_sem_erro(self):
        TabelaPersonalizada.objects.all().delete()
        self._login_com_permissoes(
            'user-tabela-vazia',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(reverse('financeiro:tabela-personalizada-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhuma tabela personalizada cadastrada ate o momento.')

    def test_listagem_exibe_botao_nova_tabela_apenas_com_permissao_criar(self):
        self._login_com_permissoes(
            'user-menu-tabela-criar',
            [
                PermissoesTabelasPersonalizadas.VISUALIZAR,
                PermissoesTabelasPersonalizadas.CRIAR,
            ],
        )

        response = self.client.get(reverse('financeiro:tabela-personalizada-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('financeiro:tabela-personalizada-create'))
        self.assertContains(response, 'Nova tabela')

    def test_listagem_oculta_botao_nova_tabela_sem_permissao_criar(self):
        self._login_com_permissoes(
            'user-menu-tabela-sem-criar',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(reverse('financeiro:tabela-personalizada-list'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse('financeiro:tabela-personalizada-create'))

    def test_listagem_exibe_acao_editar_apenas_com_permissao_editar_estrutura(self):
        self._login_com_permissoes(
            'user-menu-tabela-editar',
            [
                PermissoesTabelasPersonalizadas.VISUALIZAR,
                PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA,
            ],
        )

        response = self.client.get(reverse('financeiro:tabela-personalizada-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse('financeiro:tabela-personalizada-update', kwargs={'pk': self.tabela.pk}),
        )
        self.assertContains(response, 'Editar')

    def test_listagem_oculta_acao_editar_sem_permissao_editar_estrutura(self):
        self._login_com_permissoes(
            'user-menu-tabela-sem-editar',
            [PermissoesTabelasPersonalizadas.VISUALIZAR],
        )

        response = self.client.get(reverse('financeiro:tabela-personalizada-list'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            reverse('financeiro:tabela-personalizada-update', kwargs={'pk': self.tabela.pk}),
        )

    def test_menu_exibe_item_quando_usuario_tem_permissao(self):
        self._login_com_permissoes(
            'user-menu-tabela-com-permissao',
            [
                'financeiro.lancamentos.listar',
                PermissoesTabelasPersonalizadas.VISUALIZAR,
            ],
        )

        response = self.client.get(reverse('financeiro:home-secundaria'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('financeiro:tabela-personalizada-list'))
        self.assertContains(response, 'Tabelas personalizadas')

    def test_menu_nao_exibe_item_sem_permissao_da_frente(self):
        self._login_com_permissoes(
            'user-menu-tabela-sem-permissao',
            ['financeiro.lancamentos.listar'],
        )

        response = self.client.get(reverse('financeiro:home-secundaria'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse('financeiro:tabela-personalizada-list'))

    def test_criacao_de_tabela_nao_impacta_lancamento_financeiro_existente(self):
        pessoa = PessoaFinanceira.objects.create(nome='Pessoa preservada')
        categoria_pai = CategoriaFinanceira.objects.create(
            nome='Categoria pai preservada',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
        )
        categoria = CategoriaFinanceira.objects.create(
            nome='Categoria preservada',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            categoria_pai=categoria_pai,
        )
        conta = ContaFinanceira.objects.create(
            nome='Conta preservada',
            saldo_inicial=Decimal('0.00'),
            data_saldo_inicial=date(2026, 5, 1),
        )
        lancamento = LancamentoFinanceiro.objects.create(
            descricao='Lancamento preservado pela microetapa',
            tipo=LancamentoFinanceiro.TipoLancamento.RECEITA,
            status=LancamentoFinanceiro.StatusLancamento.QUITADO,
            valor=Decimal('42.00'),
            data_competencia=date(2026, 5, 2),
            data_pagamento=date(2026, 5, 2),
            pessoa=pessoa,
            categoria=categoria,
            conta=conta,
        )
        self._login_com_permissoes(
            'user-tabela-sem-impacto',
            [
                PermissoesTabelasPersonalizadas.CRIAR,
                PermissoesTabelasPersonalizadas.VISUALIZAR,
            ],
        )

        response = self.client.post(
            reverse('financeiro:tabela-personalizada-create'),
            data={
                'nome': 'Controle sem impacto',
                'descricao': '',
                'status': TabelaPersonalizada.StatusTabela.ATIVA,
                'ordem': 0,
            },
        )

        self.assertRedirects(response, reverse('financeiro:tabela-personalizada-list'))
        lancamento.refresh_from_db()
        self.assertEqual(lancamento.descricao, 'Lancamento preservado pela microetapa')
        self.assertEqual(lancamento.valor, Decimal('42.00'))
