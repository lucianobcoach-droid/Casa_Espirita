"""Configuração do Django admin para o aplicativo de configurações."""
from __future__ import annotations

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import ConfiguracoesUserChangeForm, ConfiguracoesUserCreationForm
from .models import PerfilAcesso, PerfilPermissaoSistema, PermissaoSistema, SiteConfig, UsuarioPerfilAcesso

User = get_user_model()
admin.site.unregister(User)


class PerfilPermissaoSistemaInline(admin.TabularInline):
    """Vinculos de permissoes do perfil dentro do admin tecnico."""

    model = PerfilPermissaoSistema
    extra = 0
    autocomplete_fields = ('permissao',)
    readonly_fields = ('criado_em',)


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    """Administração das configurações do site."""

    list_display = ('site_name', 'slogan', 'atualizado_em')
    search_fields = ('site_name', 'slogan')
    readonly_fields = ('atualizado_em',)

    fieldsets = (
        (None, {'fields': ('site_name', 'slogan', 'descricao')}),
        ('Identidade visual', {'fields': ('logo',)}),
        (
            'Interface do admin',
            {
                'fields': ('usar_layout_leve',),
                'description': 'Ativa o layout leve inspirado em Colorlib (sidebar recolhível, tabelas leves).',
            },
        ),
        ('Auditoria', {'fields': ('atualizado_em',)}),
    )


@admin.register(PermissaoSistema)
class PermissaoSistemaAdmin(admin.ModelAdmin):
    """Consulta tecnica das permissoes funcionais semeadas no sistema."""

    list_display = ('codigo', 'nome', 'modulo', 'recurso', 'acao', 'ativo')
    list_filter = ('modulo', 'recurso', 'acao', 'ativo')
    search_fields = ('codigo', 'nome', 'modulo', 'recurso', 'acao')
    readonly_fields = ('codigo', 'modulo', 'recurso', 'acao', 'criado_em', 'atualizado_em')
    ordering = ('modulo', 'recurso', 'acao', 'codigo')


@admin.register(PerfilAcesso)
class PerfilAcessoAdmin(admin.ModelAdmin):
    """Administracao temporaria dos perfis-base ate existir UI funcional propria."""

    list_display = ('nome', 'codigo', 'ativo', 'atualizado_em')
    list_filter = ('ativo',)
    search_fields = ('nome', 'codigo', 'descricao')
    readonly_fields = ('criado_em', 'atualizado_em')
    inlines = (PerfilPermissaoSistemaInline,)
    ordering = ('nome', 'codigo')


@admin.register(PerfilPermissaoSistema)
class PerfilPermissaoSistemaAdmin(admin.ModelAdmin):
    """Consulta direta dos vinculos perfil-permissao."""

    list_display = ('perfil', 'permissao', 'criado_em')
    list_filter = ('perfil', 'permissao__modulo', 'permissao__recurso', 'permissao__acao')
    search_fields = ('perfil__nome', 'perfil__codigo', 'permissao__nome', 'permissao__codigo')
    autocomplete_fields = ('perfil', 'permissao')
    readonly_fields = ('criado_em',)


@admin.register(UsuarioPerfilAcesso)
class UsuarioPerfilAcessoAdmin(admin.ModelAdmin):
    """Vinculo operacional temporario entre usuario Django e perfil-base da V1."""

    list_display = ('usuario', 'perfil', 'atualizado_em')
    list_filter = ('perfil',)
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'perfil__nome', 'perfil__codigo')
    autocomplete_fields = ('usuario', 'perfil')
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(User)
class ConfiguracoesUserAdmin(UserAdmin):
    """Endurece o cadastro tecnico de usuarios com e-mail e perfil-base da V1."""

    add_form = ConfiguracoesUserCreationForm
    form = ConfiguracoesUserChangeForm
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'is_superuser',
        'perfil_base_display',
    )
    list_filter = UserAdmin.list_filter + ('vinculo_perfil_acesso__perfil',)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Identificacao e acesso', {'fields': ('first_name', 'last_name', 'email', 'perfil_base')}),
        ('Permissoes tecnicas', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'first_name',
                    'last_name',
                    'email',
                    'password1',
                    'password2',
                    'perfil_base',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ),
            },
        ),
    )

    @admin.display(description='Perfil base')
    def perfil_base_display(self, obj):
        vinculo = getattr(obj, 'vinculo_perfil_acesso', None)
        if vinculo is None:
            return 'Sem perfil'
        return vinculo.perfil.nome

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        perfil = form.cleaned_data.get('perfil_base')
        usuario = form.instance

        if perfil is None:
            UsuarioPerfilAcesso.objects.filter(usuario=usuario).delete()
            return

        UsuarioPerfilAcesso.objects.update_or_create(
            usuario=usuario,
            defaults={'perfil': perfil},
        )
