from __future__ import annotations

from dataclasses import dataclass

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from financeiro.models import (
    AssinaturaInstitucional,
    AuditoriaFinanceiro,
    CategoriaFinanceira,
    ConfiguracaoInstitucional,
    CentroCusto,
    ContaFinanceira,
    LancamentoFinanceiro,
    PessoaFinanceira,
    RegraLancamentoFinanceiro,
)


CONFIRMACAO_RESET_FINANCEIRO = 'RESETAR_FINANCEIRO'


@dataclass(frozen=True)
class ResetFinanceiroSnapshot:
    regras_automaticas: int
    auditorias_financeiro: int
    lancamentos_financeiros: int
    assinaturas_institucionais: int
    configuracoes_institucionais: int
    subcategorias: int
    categorias_pai: int
    pessoas_financeiras: int
    centros_custo: int
    contas_financeiras: int

    @property
    def categorias_total(self) -> int:
        return self.subcategorias + self.categorias_pai


class Command(BaseCommand):
    help = (
        'Reinicia apenas os dados do modulo financeiro de forma controlada, '
        'preservando usuarios, autenticacao, perfis/permissoes, SiteConfig, '
        'configuracoes sistemicas, configuracoes institucionais, assinaturas '
        'institucionais e modulos fora do financeiro.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--executar',
            action='store_true',
            help='Executa o reset real. Sem esta flag o comando roda apenas em dry-run.',
        )
        parser.add_argument(
            '--confirmar',
            default='',
            help=(
                'Confirmacao textual obrigatoria para o reset real. '
                f'Use exatamente: {CONFIRMACAO_RESET_FINANCEIRO}'
            ),
        )

    def handle(self, *args, **options):
        executar = bool(options['executar'])
        confirmacao = (options.get('confirmar') or '').strip()
        snapshot = self._montar_snapshot()

        self.stdout.write(self.style.WARNING('RESET CONTROLADO DO FINANCEIRO'))
        self.stdout.write('')
        self.stdout.write('Escopo de exclusao planejado:')
        self.stdout.write(f'- lancamentos financeiros: {snapshot.lancamentos_financeiros}')
        self.stdout.write(f'- regras automaticas de lancamento: {snapshot.regras_automaticas}')
        self.stdout.write(f'- auditorias do financeiro: {snapshot.auditorias_financeiro}')
        self.stdout.write(f'- contas financeiras: {snapshot.contas_financeiras}')
        self.stdout.write(f'- pessoas financeiras: {snapshot.pessoas_financeiras}')
        self.stdout.write(
            f'- categorias/subcategorias financeiras: {snapshot.categorias_total} '
            f'({snapshot.categorias_pai} categorias, {snapshot.subcategorias} subcategorias)'
        )
        self.stdout.write(f'- centros de custo: {snapshot.centros_custo}')
        self.stdout.write('')
        self.stdout.write('Escopo explicitamente preservado:')
        self.stdout.write('- usuarios')
        self.stdout.write('- autenticacao e sessoes')
        self.stdout.write('- perfis/permissoes')
        self.stdout.write('- SiteConfig')
        self.stdout.write('- configuracoes sistemicas')
        self.stdout.write(
            f'- assinaturas institucionais do financeiro: {snapshot.assinaturas_institucionais}'
        )
        self.stdout.write(
            f'- configuracoes institucionais do financeiro: {snapshot.configuracoes_institucionais}'
        )
        self.stdout.write('- modulos fora do financeiro')
        self.stdout.write('')

        if not executar:
            self.stdout.write(self.style.WARNING('Modo simulacao ativo. Nenhum dado foi apagado.'))
            self.stdout.write(
                'Para executar o reset real, rode exatamente:'
            )
            self.stdout.write(
                f'py manage.py reset_financeiro_controlado --executar --confirmar {CONFIRMACAO_RESET_FINANCEIRO}'
            )
            return

        if confirmacao != CONFIRMACAO_RESET_FINANCEIRO:
            raise CommandError(
                'Reset cancelado por falta de confirmacao explicita. '
                f'Use --confirmar {CONFIRMACAO_RESET_FINANCEIRO} junto com --executar.'
            )

        with transaction.atomic():
            self._executar_reset()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Reset controlado do financeiro concluido com sucesso.'))
        self.stdout.write('Tudo o que pertence ao modulo financeiro foi reiniciado conforme o escopo acima.')

    def _montar_snapshot(self) -> ResetFinanceiroSnapshot:
        return ResetFinanceiroSnapshot(
            regras_automaticas=RegraLancamentoFinanceiro.objects.count(),
            auditorias_financeiro=AuditoriaFinanceiro.objects.count(),
            lancamentos_financeiros=LancamentoFinanceiro.objects.count(),
            assinaturas_institucionais=AssinaturaInstitucional.objects.count(),
            configuracoes_institucionais=ConfiguracaoInstitucional.objects.count(),
            subcategorias=CategoriaFinanceira.objects.filter(categoria_pai__isnull=False).count(),
            categorias_pai=CategoriaFinanceira.objects.filter(categoria_pai__isnull=True).count(),
            pessoas_financeiras=PessoaFinanceira.objects.count(),
            centros_custo=CentroCusto.objects.count(),
            contas_financeiras=ContaFinanceira.objects.count(),
        )

    def _executar_reset(self) -> None:
        RegraLancamentoFinanceiro.objects.all().delete()
        AuditoriaFinanceiro.objects.all().delete()
        LancamentoFinanceiro.objects.all().delete()
        CategoriaFinanceira.objects.filter(categoria_pai__isnull=False).delete()
        CategoriaFinanceira.objects.filter(categoria_pai__isnull=True).delete()
        PessoaFinanceira.objects.all().delete()
        CentroCusto.objects.all().delete()
        ContaFinanceira.objects.all().delete()
