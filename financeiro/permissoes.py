"""Camada reutilizavel de enforcement backend das permissoes do financeiro."""
from __future__ import annotations

from configuracoes.permissoes import PermissaoSistemaMixin, usuario_possui_permissao


class FinanceiroPermissaoMixin(PermissaoSistemaMixin):
    """Exige usuario autenticado e permissao funcional explicita."""

    permission_denied_message = 'Voce nao tem permissao para acessar esta area do financeiro.'
