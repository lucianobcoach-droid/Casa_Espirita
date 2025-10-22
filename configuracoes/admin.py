"""Configuração do Django admin para o aplicativo de configurações."""
from __future__ import annotations

from django.contrib import admin

from .models import SiteConfig


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    """Administração das configurações do site."""

    list_display = ('site_name', 'slogan', 'atualizado_em')
    search_fields = ('site_name', 'slogan')
    readonly_fields = ('atualizado_em',)

    fieldsets = (
        (None, {'fields': ('site_name', 'slogan', 'descricao')}),
        ('Identidade visual', {'fields': ('logo',)}),
        ('Auditoria', {'fields': ('atualizado_em',)}),
    )
