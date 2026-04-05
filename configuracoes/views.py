"""Views do aplicativo de configuracoes."""
from __future__ import annotations

from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpRequest, HttpResponse
from django.views.generic import DetailView

from .mixins import ConfiguracoesPermissaoMixin
from .models import SiteConfig


class SiteConfigDetailView(ConfiguracoesPermissaoMixin, DetailView):
    """Exibe a configuracao ativa do site."""

    template_name = 'configuracoes/siteconfig_detail.html'
    model = SiteConfig
    permissao_requerida = 'configuracoes.siteconfig.visualizar'

    def get_object(self, queryset=None):  # type: ignore[override]
        obj = SiteConfig.objects.first()
        if obj is None:
            obj = SiteConfig(site_name='Casa Espirita')
        return obj


class ConfiguracoesLoginView(LoginView):
    """Tela minima de login baseada na autenticacao padrao do Django."""

    template_name = 'configuracoes/login.html'
    redirect_authenticated_user = True


class ConfiguracoesLogoutView(LogoutView):
    """Logout com suporte a GET/POST para facilitar o bootstrap operacional."""

    http_method_names = ['get', 'post', 'options']

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.post(request, *args, **kwargs)
