"""Camada reutilizavel de enforcement backend das permissoes do modulo eventos."""
from __future__ import annotations

from configuracoes.permissoes import PermissaoSistemaMixin


class EventosPermissaoMixin(PermissaoSistemaMixin):
    """Exige usuario autenticado e permissao funcional explicita."""

    permission_denied_message = 'Voce nao tem permissao para acessar esta area de eventos.'
