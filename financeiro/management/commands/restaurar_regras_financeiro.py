from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from financeiro.regras_backup import (
    CONFIRMACAO_RESTAURACAO_REGRAS,
    carregar_payload_backup_regras,
    restaurar_payload_backup_regras,
)


class Command(BaseCommand):
    help = (
        'Restaura, de forma transacional, as regras automaticas do financeiro a partir '
        'de um backup tecnico JSON separado do fluxo comum do usuario.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--arquivo',
            default='',
            help='Arquivo JSON de origem com o backup tecnico das regras.',
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
                f'Use exatamente: {CONFIRMACAO_RESTAURACAO_REGRAS}'
            ),
        )

    def handle(self, *args, **options):
        caminho_arquivo = (options.get('arquivo') or '').strip()
        executar = bool(options.get('executar'))
        confirmacao = (options.get('confirmar') or '').strip()

        if not caminho_arquivo:
            raise CommandError('Informe o arquivo de origem com --arquivo.')

        payload = carregar_payload_backup_regras(caminho_arquivo)
        resumo = restaurar_payload_backup_regras(payload, executar=False, origem_auditoria=caminho_arquivo)

        self.stdout.write(self.style.WARNING('RESTAURACAO TECNICA DE REGRAS DO FINANCEIRO'))
        self.stdout.write(f'- arquivo: {caminho_arquivo}')
        self.stdout.write(f'- regras avaliadas: {resumo.regras_avaliadas}')
        self.stdout.write('- escopo: apenas regras automaticas do financeiro')
        self.stdout.write('- pre-requisito: contas, pessoas, centros de custo e categorias ja recompostos')
        self.stdout.write('')

        if not executar:
            self.stdout.write(self.style.WARNING('Modo simulacao ativo. Nenhuma regra foi restaurada.'))
            self.stdout.write('Para executar a restauracao real, rode exatamente:')
            self.stdout.write(
                f'py manage.py restaurar_regras_financeiro --arquivo "{caminho_arquivo}" '
                f'--executar --confirmar {CONFIRMACAO_RESTAURACAO_REGRAS}'
            )
            return

        if confirmacao != CONFIRMACAO_RESTAURACAO_REGRAS:
            raise CommandError(
                'Restauracao cancelada por falta de confirmacao explicita. '
                f'Use --confirmar {CONFIRMACAO_RESTAURACAO_REGRAS} junto com --executar.'
            )

        resumo_execucao = restaurar_payload_backup_regras(
            payload,
            executar=True,
            origem_auditoria=f'arquivo {caminho_arquivo}',
        )
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Restauracao tecnica de regras concluida com sucesso.'))
        self.stdout.write(f'- regras restauradas: {resumo_execucao.regras_restauradas}')
