"""Camada reutilizavel de enforcement backend das permissoes do financeiro."""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden

from configuracoes.permissoes import usuario_possui_permissao


class FinanceiroPermissaoMixin(LoginRequiredMixin):
    """Exige usuario autenticado e permissao funcional explicita."""

    permissao_requerida = ''
    permission_denied_message = 'Voce nao tem permissao para acessar esta area do financeiro.'

    def get_permissao_requerida(self) -> str:
        return self.permissao_requerida

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        permissao_requerida = self.get_permissao_requerida()
        if not permissao_requerida or not usuario_possui_permissao(
            request.user,
            permissao_requerida,
        ):
            return HttpResponseForbidden(self.get_permission_denied_message())

        return super().dispatch(request, *args, **kwargs)
