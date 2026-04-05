"""Views do aplicativo de configuracoes."""
from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView

from .forms import ConfiguracoesPasswordResetForm, UsuarioPerfilBaseForm
from .mixins import ConfiguracoesPermissaoMixin
from .models import PerfilAcesso, SiteConfig, UsuarioPerfilAcesso

User = get_user_model()


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


class SistemaInicioView(LoginRequiredMixin, ConfiguracoesIdentidadeMixin, TemplateView):
    """Portal autenticado com os modulos liberados ao usuario."""

    template_name = 'configuracoes/inicio.html'
    login_url = reverse_lazy('configuracoes:login')


class PerfilAcessoListView(ConfiguracoesPermissaoMixin, ConfiguracoesIdentidadeMixin, ListView):
    """Lista funcional minima dos perfis-base existentes."""

    model = PerfilAcesso
    template_name = 'configuracoes/perfil_acesso_list.html'
    context_object_name = 'perfis'
    permissao_requerida = 'configuracoes.perfis_acesso.listar'

    def get_queryset(self):
        return (
            PerfilAcesso.objects.order_by('nome')
            .prefetch_related('permissoes', 'usuarios_vinculados')
        )


class PerfilAcessoDetailView(ConfiguracoesPermissaoMixin, ConfiguracoesIdentidadeMixin, DetailView):
    """Detalhe legivel de um perfil, agrupando permissoes por modulo/recurso."""

    model = PerfilAcesso
    template_name = 'configuracoes/perfil_acesso_detail.html'
    context_object_name = 'perfil'
    permissao_requerida = 'configuracoes.perfis_acesso.visualizar'

    def get_queryset(self):
        return PerfilAcesso.objects.prefetch_related('permissoes', 'usuarios_vinculados').order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grupos: dict[str, dict[str, list[dict[str, str]]]] = {}
        for permissao in self.object.permissoes.filter(ativo=True).order_by('modulo', 'recurso', 'acao'):
            grupos.setdefault(permissao.modulo, {}).setdefault(permissao.recurso, []).append(
                {
                    'codigo': permissao.codigo,
                    'nome': permissao.nome,
                    'acao': permissao.acao.replace('_', ' '),
                }
            )
        context['permissoes_agrupadas'] = [
            {
                'modulo': modulo.replace('_', ' '),
                'recursos': [
                    {
                        'recurso': recurso.replace('_', ' '),
                        'acoes': acoes,
                    }
                    for recurso, acoes in recursos.items()
                ],
            }
            for modulo, recursos in grupos.items()
        ]
        return context


class UsuarioPerfilAcessoListView(ConfiguracoesPermissaoMixin, ConfiguracoesIdentidadeMixin, ListView):
    """Lista usuarios com seu perfil-base atual para administracao funcional."""

    model = User
    template_name = 'configuracoes/usuario_perfil_list.html'
    context_object_name = 'usuarios'
    permissao_requerida = 'configuracoes.usuarios_acesso.listar'

    def get_queryset(self):
        return User.objects.order_by('username').select_related('vinculo_perfil_acesso__perfil')


class UsuarioPerfilAcessoUpdateView(ConfiguracoesPermissaoMixin, ConfiguracoesIdentidadeMixin, FormView):
    """Altera o vinculo funcional do usuario com um perfil-base."""

    template_name = 'configuracoes/usuario_perfil_form.html'
    form_class = UsuarioPerfilBaseForm
    permissao_requerida = 'configuracoes.usuarios_acesso.editar_perfil'

    def dispatch(self, request, *args, **kwargs):
        self.usuario_obj = get_object_or_404(
            User.objects.select_related('vinculo_perfil_acesso__perfil'),
            pk=kwargs['pk'],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.usuario_obj
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario_obj'] = self.usuario_obj
        return context

    def form_valid(self, form):
        perfil = form.cleaned_data.get('perfil_base')
        if perfil is None:
            UsuarioPerfilAcesso.objects.filter(usuario=self.usuario_obj).delete()
        else:
            UsuarioPerfilAcesso.objects.update_or_create(
                usuario=self.usuario_obj,
                defaults={'perfil': perfil},
            )
        messages.success(self.request, 'Perfil base atualizado com sucesso.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('configuracoes:usuario-perfil-list')
