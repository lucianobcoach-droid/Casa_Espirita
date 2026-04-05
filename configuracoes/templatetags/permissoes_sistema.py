from __future__ import annotations

from django import template

from configuracoes.permissoes import usuario_possui_permissao

register = template.Library()


@register.simple_tag
def tem_permissao(usuario, codigo_permissao: str) -> bool:
    return usuario_possui_permissao(usuario, codigo_permissao)


@register.simple_tag
def tem_alguma_permissao(usuario, *codigos_permissao: str) -> bool:
    return any(usuario_possui_permissao(usuario, codigo) for codigo in codigos_permissao if codigo)
