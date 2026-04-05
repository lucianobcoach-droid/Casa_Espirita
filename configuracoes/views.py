"""Views do aplicativo de configuracoes."""
from __future__ import annotations

from django.conf import settings
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView

from .forms import ConfiguracoesPasswordResetForm
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


class ConfiguracoesIdentidadeMixin:
    """Contexto institucional minimo para as telas de autenticacao."""

    fallback_site_name = 'Casa Espirita'

    def get_site_config(self):
        return SiteConfig.objects.first()

    def get_site_name(self) -> str:
        site_config = self.get_site_config()
        if site_config and site_config.site_name:
            return site_config.site_name
        return self.fallback_site_name

    def get_site_slogan(self) -> str:
        site_config = self.get_site_config()
        if site_config and site_config.slogan:
            return site_config.slogan
        return ''

    def email_backend_local_only(self) -> bool:
        return settings.EMAIL_BACKEND in {
            'django.core.mail.backends.console.EmailBackend',
            'django.core.mail.backends.filebased.EmailBackend',
            'django.core.mail.backends.locmem.EmailBackend',
            'django.core.mail.backends.dummy.EmailBackend',
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'site_name': self.get_site_name(),
                'site_slogan': self.get_site_slogan(),
                'email_backend_local_only': self.email_backend_local_only(),
            }
        )
        return context

    def get_email_extra_context(self) -> dict[str, str]:
        return {
            'site_name': self.get_site_name(),
        }


class ConfiguracoesLoginView(ConfiguracoesIdentidadeMixin, LoginView):
    """Tela minima de login baseada na autenticacao padrao do Django."""

    template_name = 'configuracoes/login.html'
    redirect_authenticated_user = True


class ConfiguracoesLogoutView(LogoutView):
    """Logout com suporte a GET/POST para facilitar o bootstrap operacional."""

    http_method_names = ['get', 'post', 'options']

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.post(request, *args, **kwargs)


class ConfiguracoesPasswordResetView(ConfiguracoesIdentidadeMixin, PasswordResetView):
    """Solicita redefinicao de senha com o fluxo nativo do Django."""

    template_name = 'configuracoes/password_reset_form.html'
    email_template_name = 'configuracoes/password_reset_email.txt'
    subject_template_name = 'configuracoes/password_reset_subject.txt'
    success_url = reverse_lazy('configuracoes:password-reset-done')
    form_class = ConfiguracoesPasswordResetForm

    def form_valid(self, form):
        self.extra_email_context = self.get_email_extra_context()
        return super().form_valid(form)


class ConfiguracoesPasswordResetDoneView(ConfiguracoesIdentidadeMixin, PasswordResetDoneView):
    """Confirma o disparo do fluxo de redefinicao de senha."""

    template_name = 'configuracoes/password_reset_done.html'


class ConfiguracoesPasswordResetConfirmView(ConfiguracoesIdentidadeMixin, PasswordResetConfirmView):
    """Permite definir uma nova senha a partir do token recebido."""

    template_name = 'configuracoes/password_reset_confirm.html'
    success_url = reverse_lazy('configuracoes:password-reset-complete')


class ConfiguracoesPasswordResetCompleteView(ConfiguracoesIdentidadeMixin, PasswordResetCompleteView):
    """Confirma a conclusao da redefinicao de senha."""

    template_name = 'configuracoes/password_reset_complete.html'
