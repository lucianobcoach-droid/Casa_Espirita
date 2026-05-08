"""Camada reutilizavel de enforcement backend das permissoes do financeiro."""
from __future__ import annotations

from configuracoes.permissoes import PermissaoSistemaMixin, usuario_possui_permissao


class PermissoesTabelasPersonalizadas:
    """Catalogo canonico das permissoes da frente de tabelas configuraveis."""

    VISUALIZAR = 'financeiro.tabelas_personalizadas.visualizar'
    CRIAR = 'financeiro.tabelas_personalizadas.criar'
    EDITAR_ESTRUTURA = 'financeiro.tabelas_personalizadas.editar_estrutura'
    CONFIGURAR_FORMULA = 'financeiro.tabelas_personalizadas.configurar_formula'
    PREENCHER_LINHAS = 'financeiro.tabelas_personalizadas.preencher_linhas'
    EDITAR_LINHAS = 'financeiro.tabelas_personalizadas.editar_linhas'
    EXPORTAR = 'financeiro.tabelas_personalizadas.exportar'
    ARQUIVAR_RESTAURAR = 'financeiro.tabelas_personalizadas.arquivar_restaurar'
    ADMINISTRAR_CONFIGURACOES = 'financeiro.tabelas_personalizadas.administrar_configuracoes'

    TODAS = (
        VISUALIZAR,
        CRIAR,
        EDITAR_ESTRUTURA,
        CONFIGURAR_FORMULA,
        PREENCHER_LINHAS,
        EDITAR_LINHAS,
        EXPORTAR,
        ARQUIVAR_RESTAURAR,
        ADMINISTRAR_CONFIGURACOES,
    )


class FinanceiroPermissaoMixin(PermissaoSistemaMixin):
    """Exige usuario autenticado e permissao funcional explicita."""

    permission_denied_message = 'Voce nao tem permissao para acessar esta area do financeiro.'
