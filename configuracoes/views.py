"""Views do aplicativo de configurações."""
from __future__ import annotations

from django.views.generic import DetailView

from .models import SiteConfig


class SiteConfigDetailView(DetailView):
    """Exibe a configuração ativa do site."""

    template_name = 'configuracoes/siteconfig_detail.html'
    model = SiteConfig

    def get_object(self, queryset=None):  # type: ignore[override]
        obj = SiteConfig.objects.first()
        if obj is None:
            obj = SiteConfig(site_name='Casa Espírita')
        return obj
