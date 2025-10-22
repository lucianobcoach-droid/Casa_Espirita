from __future__ import annotations

from datetime import date

from django.core.management.base import BaseCommand

from biblioteca.models import Emprestimo


class Command(BaseCommand):
    help = "Identifica empréstimos em atraso e registra notificações no console."

    def handle(self, *args, **options):
        hoje = date.today()
        emprestimos = Emprestimo.objects.filter(
            status__in=[Emprestimo.STATUS_PENDENTE, Emprestimo.STATUS_ATRASADO],
            data_prevista_devolucao__lt=hoje,
        )
        if not emprestimos.exists():
            self.stdout.write(self.style.SUCCESS("Nenhum empréstimo em atraso."))
            return

        self.stdout.write(self.style.WARNING("Empréstimos em atraso:"))
        for emprestimo in emprestimos.select_related("livro"):
            mensagem = (
                f"Leitor: {emprestimo.leitor} | Livro: {emprestimo.livro.titulo} | "
                f"Previsto para: {emprestimo.data_prevista_devolucao:%d/%m/%Y}"
            )
            self.stdout.write(f" - {mensagem}")
        self.stdout.write(self.style.NOTICE("Envie notificações para os leitores listados."))
