"""Templatetags auxiliares para o Django admin."""
from __future__ import annotations

from django import template

from configuracoes.models import SiteConfig

register = template.Library()


@register.simple_tag
def get_site_config() -> SiteConfig | None:
    """Retorna a instância única de ``SiteConfig`` ou ``None``.

    A consulta é realizada de forma segura para não quebrar o admin caso a tabela
    ainda não exista (por exemplo, antes de aplicar as migrações).
    """

    try:
        return SiteConfig.objects.first()
    except Exception:  # pragma: no cover - evita falhas durante migrações iniciais
        return None
