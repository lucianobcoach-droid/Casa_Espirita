"""Servicos centrais de consulta de perfil e permissao funcional."""
from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist


def obter_perfil_base_usuario(usuario):
    """Retorna o perfil-base ativo do usuario autenticado ou ``None``."""

    if not usuario or not usuario.is_authenticated or not usuario.is_active:
        return None

    try:
        vinculo = usuario.vinculo_perfil_acesso
    except ObjectDoesNotExist:
        return None

    if not vinculo.perfil.ativo:
        return None

    return vinculo.perfil


def usuario_possui_permissao(usuario, codigo_permissao: str) -> bool:
    """Valida uma permissao funcional por codigo canonico sem fallback implicito."""

    perfil = obter_perfil_base_usuario(usuario)
    if perfil is None:
        return False

    return perfil.permissoes.filter(
        codigo=codigo_permissao,
        ativo=True,
    ).exists()
