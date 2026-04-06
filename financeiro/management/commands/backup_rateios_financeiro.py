from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from financeiro.rateio_backup import construir_payload_backup_rateios, salvar_payload_backup_rateios


class Command(BaseCommand):
    help = (
        'Gera um backup tecnico em JSON apenas dos lancamentos com rateio e seus grupos, '
        'para permitir restauracao fiel apos reset do modulo financeiro.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--saida',
            default='',
            help='Arquivo JSON de destino para o backup tecnico dos rateios.',
        )
        parser.add_argument(
            '--grupo',
            action='append',
            default=[],
            help='Grupo de rateio especifico a incluir. Pode ser repetido.',
        )
        parser.add_argument(
            '--sobrescrever',
            action='store_true',
            help='Permite sobrescrever um arquivo de saida ja existente.',
        )

    def handle(self, *args, **options):
        caminho_saida = (options.get('saida') or '').strip()
        grupos = [item.strip() for item in options.get('grupo') or [] if item.strip()]
        sobrescrever = bool(options.get('sobrescrever'))

        if not caminho_saida:
            raise CommandError('Informe o arquivo de saida com --saida.')

        destino = Path(caminho_saida)
        if destino.exists() and not sobrescrever:
            raise CommandError(
                f'O arquivo "{destino}" ja existe. Use --sobrescrever se quiser substitui-lo.'
            )

        payload = construir_payload_backup_rateios(grupos_rateio=grupos or None)
        salvar_payload_backup_rateios(payload, destino)

        self.stdout.write(self.style.SUCCESS('Backup tecnico de rateios gerado com sucesso.'))
        self.stdout.write(f'- arquivo: {destino}')
        self.stdout.write(f'- grupos exportados: {payload["total_grupos"]}')
        self.stdout.write(f'- linhas exportadas: {payload["total_linhas"]}')
