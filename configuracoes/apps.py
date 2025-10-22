"""Configuração do aplicativo de configurações."""
from __future__ import annotations

from django.apps import AppConfig


class ConfiguracoesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'configuracoes'
    verbose_name = 'Configurações do Site'

    def ready(self) -> None:  # pragma: no cover - hook para inicializações futuras
        """Ponto de extensão para inicialização do aplicativo."""
        return None
