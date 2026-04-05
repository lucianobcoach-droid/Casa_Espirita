"""Modelos do aplicativo de configurações."""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

SITE_NAME_PADRAO = 'Casa Espírita Caminheiros da Luz'


class SiteConfig(models.Model):
    """Configurações principais da Casa Espírita."""

    site_name = models.CharField(_('Nome do site'), max_length=150, default=SITE_NAME_PADRAO)
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


class PermissaoSistema(models.Model):
    """Permissao funcional do sistema no formato modulo/recurso/acao."""

    codigo = models.CharField(_('Codigo'), max_length=150, unique=True)
    nome = models.CharField(_('Nome'), max_length=150)
    modulo = models.CharField(_('Modulo'), max_length=50, db_index=True)
    recurso = models.CharField(_('Tela/Recurso'), max_length=80, db_index=True)
    acao = models.CharField(_('Acao'), max_length=80, db_index=True)
    descricao = models.TextField(_('Descricao'), blank=True)
    ativo = models.BooleanField(_('Ativo'), default=True)
    criado_em = models.DateTimeField(_('Criado em'), auto_now_add=True)
    atualizado_em = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Permissao do sistema')
        verbose_name_plural = _('Permissoes do sistema')
        ordering = ('modulo', 'recurso', 'acao', 'codigo')
        constraints = [
            models.UniqueConstraint(
                fields=('modulo', 'recurso', 'acao'),
                name='uniq_permissao_sistema_modulo_recurso_acao',
            ),
        ]

    def __str__(self) -> str:  # pragma: no cover - representacao simples
        return self.nome


class PerfilAcesso(models.Model):
    """Perfil-base de acesso da V1, composto por um pacote de permissoes."""

    codigo = models.CharField(_('Codigo'), max_length=80, unique=True)
    nome = models.CharField(_('Nome'), max_length=120, unique=True)
    descricao = models.TextField(_('Descricao'), blank=True)
    permissoes = models.ManyToManyField(
        PermissaoSistema,
        through='PerfilPermissaoSistema',
        related_name='perfis',
        verbose_name=_('Permissoes'),
        blank=True,
    )
    ativo = models.BooleanField(_('Ativo'), default=True)
    criado_em = models.DateTimeField(_('Criado em'), auto_now_add=True)
    atualizado_em = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Perfil de acesso')
        verbose_name_plural = _('Perfis de acesso')
        ordering = ('nome', 'codigo')

    def __str__(self) -> str:  # pragma: no cover - representacao simples
        return self.nome


class PerfilPermissaoSistema(models.Model):
    """Vinculo entre perfil-base e permissao funcional do sistema."""

    perfil = models.ForeignKey(
        PerfilAcesso,
        on_delete=models.CASCADE,
        related_name='vinculos_permissao',
        verbose_name=_('Perfil'),
    )
    permissao = models.ForeignKey(
        PermissaoSistema,
        on_delete=models.CASCADE,
        related_name='vinculos_perfil',
        verbose_name=_('Permissao'),
    )
    criado_em = models.DateTimeField(_('Criado em'), auto_now_add=True)

    class Meta:
        verbose_name = _('Permissao do perfil')
        verbose_name_plural = _('Permissoes dos perfis')
        ordering = ('perfil__nome', 'permissao__modulo', 'permissao__recurso', 'permissao__acao')
        constraints = [
            models.UniqueConstraint(
                fields=('perfil', 'permissao'),
                name='uniq_perfil_permissao_sistema',
            ),
        ]

    def __str__(self) -> str:  # pragma: no cover - representacao simples
        return f'{self.perfil} - {self.permissao.codigo}'


class UsuarioPerfilAcesso(models.Model):
    """Vinculo V1 de um usuario Django com um unico perfil-base do sistema."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vinculo_perfil_acesso',
        verbose_name=_('Usuario'),
    )
    perfil = models.ForeignKey(
        PerfilAcesso,
        on_delete=models.PROTECT,
        related_name='usuarios_vinculados',
        verbose_name=_('Perfil base'),
    )
    criado_em = models.DateTimeField(_('Criado em'), auto_now_add=True)
    atualizado_em = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Perfil de usuario')
        verbose_name_plural = _('Perfis de usuarios')
        ordering = ('usuario__username',)

    def __str__(self) -> str:  # pragma: no cover - representacao simples
        return f'{self.usuario} -> {self.perfil}'
