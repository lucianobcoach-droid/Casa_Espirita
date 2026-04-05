"""Camada reutilizavel de enforcement backend das permissoes da biblioteca."""
from __future__ import annotations

from configuracoes.permissoes import PermissaoSistemaMixin


class BibliotecaPermissaoMixin(PermissaoSistemaMixin):
    """Exige usuario autenticado e permissao funcional explicita."""

    permission_denied_message = 'Voce nao tem permissao para acessar esta area da biblioteca.'
