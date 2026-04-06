from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from financeiro.regras_backup import construir_payload_backup_regras, salvar_payload_backup_regras


class Command(BaseCommand):
    help = (
        'Gera um backup tecnico em JSON das regras automaticas do financeiro, '
        'para permitir restauracao fiel apos reset do modulo.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--saida',
            default='',
            help='Arquivo JSON de destino para o backup tecnico das regras.',
        )
        parser.add_argument(
            '--sobrescrever',
            action='store_true',
            help='Permite sobrescrever um arquivo de saida ja existente.',
        )

    def handle(self, *args, **options):
        caminho_saida = (options.get('saida') or '').strip()
        sobrescrever = bool(options.get('sobrescrever'))

        if not caminho_saida:
            raise CommandError('Informe o arquivo de saida com --saida.')

        destino = Path(caminho_saida)
        if destino.exists() and not sobrescrever:
            raise CommandError(
                f'O arquivo "{destino}" ja existe. Use --sobrescrever se quiser substitui-lo.'
            )

        payload = construir_payload_backup_regras()
        salvar_payload_backup_regras(payload, destino)

        self.stdout.write(self.style.SUCCESS('Backup tecnico de regras gerado com sucesso.'))
        self.stdout.write(f'- arquivo: {destino}')
        self.stdout.write(f'- regras exportadas: {payload["total_regras"]}')
