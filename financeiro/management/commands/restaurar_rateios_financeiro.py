from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from financeiro.rateio_backup import (
    CONFIRMACAO_RESTAURACAO_RATEIO,
    carregar_payload_backup_rateios,
    restaurar_payload_backup_rateios,
)


class Command(BaseCommand):
    help = (
        'Restaura, de forma transacional e fiel, os lancamentos rateados a partir de um '
        'backup tecnico JSON separado da importacao comum de lancamentos.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--arquivo',
            default='',
            help='Arquivo JSON de origem com o backup tecnico dos rateios.',
        )
        parser.add_argument(
            '--executar',
            action='store_true',
            help='Executa a restauracao real. Sem esta flag o comando roda apenas em dry-run.',
        )
        parser.add_argument(
            '--confirmar',
            default='',
            help=(
                'Confirmacao textual obrigatoria para a restauracao real. '
                f'Use exatamente: {CONFIRMACAO_RESTAURACAO_RATEIO}'
            ),
        )

    def handle(self, *args, **options):
        caminho_arquivo = (options.get('arquivo') or '').strip()
        executar = bool(options.get('executar'))
        confirmacao = (options.get('confirmar') or '').strip()

        if not caminho_arquivo:
            raise CommandError('Informe o arquivo de origem com --arquivo.')

        payload = carregar_payload_backup_rateios(caminho_arquivo)
        resumo = restaurar_payload_backup_rateios(
            payload,
            executar=False,
            origem_auditoria=caminho_arquivo,
            permitir_grupos_existentes=True,
        )

        self.stdout.write(self.style.WARNING('RESTAURACAO TECNICA DE RATEIOS DO FINANCEIRO'))
        self.stdout.write(f'- arquivo: {caminho_arquivo}')
        self.stdout.write(f'- grupos avaliados: {resumo.grupos_avaliados}')
        self.stdout.write(f'- linhas avaliadas: {resumo.linhas_avaliadas}')
        self.stdout.write(f'- grupos legados com linha unica: {resumo.grupos_legados_linha_unica}')
        self.stdout.write('- escopo: apenas lancamentos com rateio e seus grupos')
        self.stdout.write('- pre-requisito: contas, pessoas, centros de custo e categorias ja recompostos')
        self.stdout.write(
            '- observacao: o restore tecnico consegue reconstituir linhas legadas com categoria-pai '
            'sem abrir essa permissao no fluxo funcional comum'
        )
        self.stdout.write('')

        if not executar:
            self.stdout.write(self.style.WARNING('Modo simulacao ativo. Nenhum rateio foi restaurado.'))
            self.stdout.write(
                'Para executar a restauracao real, rode exatamente:'
            )
            self.stdout.write(
                f'py manage.py restaurar_rateios_financeiro --arquivo "{caminho_arquivo}" '
                f'--executar --confirmar {CONFIRMACAO_RESTAURACAO_RATEIO}'
            )
            return

        if confirmacao != CONFIRMACAO_RESTAURACAO_RATEIO:
            raise CommandError(
                'Restauracao cancelada por falta de confirmacao explicita. '
                f'Use --confirmar {CONFIRMACAO_RESTAURACAO_RATEIO} junto com --executar.'
            )

        resumo_execucao = restaurar_payload_backup_rateios(
            payload,
            executar=True,
            origem_auditoria=f'arquivo {caminho_arquivo}',
        )
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Restauracao tecnica de rateios concluida com sucesso.'))
        self.stdout.write(f'- grupos restaurados: {resumo_execucao.grupos_restaurados}')
        self.stdout.write(f'- linhas restauradas: {resumo_execucao.linhas_restauradas}')
        self.stdout.write(f'- linhas legadas restauradas: {resumo_execucao.linhas_legadas_restauradas}')
        self.stdout.write(f'- grupos legados com linha unica: {resumo_execucao.grupos_legados_linha_unica}')
