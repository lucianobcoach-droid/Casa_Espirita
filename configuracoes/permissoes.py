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


def obter_codigos_permissao_usuario(usuario) -> frozenset[str]:
    """Retorna os codigos de permissao ativos do perfil-base do usuario."""

    if not usuario or not usuario.is_authenticated or not usuario.is_active:
        return frozenset()

    codigos_cache = getattr(usuario, '_codigos_permissao_sistema_cache', None)
    if codigos_cache is not None:
        return codigos_cache

    perfil = obter_perfil_base_usuario(usuario)
    if perfil is None:
        codigos = frozenset()
    else:
        codigos = frozenset(
            perfil.permissoes.filter(ativo=True).values_list('codigo', flat=True)
        )

    setattr(usuario, '_codigos_permissao_sistema_cache', codigos)
    return codigos


def usuario_possui_permissao(usuario, codigo_permissao: str) -> bool:
    """Valida uma permissao funcional por codigo canonico sem fallback implicito."""

    if not codigo_permissao:
        return False

    return codigo_permissao in obter_codigos_permissao_usuario(usuario)
