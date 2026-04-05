"""Mixins reutilizaveis de enforcement backend para configuracoes."""
from __future__ import annotations

from .permissoes import PermissaoSistemaMixin


class ConfiguracoesPermissaoMixin(PermissaoSistemaMixin):
    """Exige usuario autenticado e permissao funcional explicita."""

    permission_denied_message = 'Voce nao tem permissao para acessar esta area de configuracoes.'
