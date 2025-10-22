"""Testes básicos para o aplicativo de configurações."""
from __future__ import annotations

from django.test import TestCase

from .models import SiteConfig


class SiteConfigModelTest(TestCase):
    """Validações simples para o modelo de configuração."""

    def test_string_representation(self) -> None:
        config = SiteConfig.objects.create(site_name='Lar Espírita', slogan='Luz e Caridade')
        self.assertEqual(str(config), 'Lar Espírita')
