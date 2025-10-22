"""Modelos do aplicativo de configurações."""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteConfig(models.Model):
    """Configurações principais da Casa Espírita."""

    site_name = models.CharField(_('Nome do site'), max_length=150, default='Casa Espírita')
    slogan = models.CharField(_('Slogan'), max_length=255, blank=True)
    descricao = models.TextField(_('Descrição'), blank=True)
    logo = models.ImageField(_('Logo'), upload_to='configuracoes/logo/', blank=True, null=True)
    usar_layout_leve = models.BooleanField(
        _('Usar layout leve'),
        default=False,
        help_text=_('Ativa o novo layout leve do Django admin.'),
    )
    atualizado_em = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Configuração do site')
        verbose_name_plural = _('Configurações do site')

    def __str__(self) -> str:  # pragma: no cover - representação simples
        return self.site_name
