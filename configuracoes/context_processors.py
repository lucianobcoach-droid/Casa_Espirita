"""Contexto global para shell autenticado e navegacao principal do sistema."""
from __future__ import annotations

from django.urls import reverse

from .models import SiteConfig
from .permissoes import obter_modulos_disponiveis, obter_perfil_base_usuario


def _nome_usuario(request) -> str:
    usuario = getattr(request, 'user', None)
    if not usuario or not usuario.is_authenticated:
        return ''
    nome_completo = ' '.join(
        parte for parte in [usuario.first_name.strip(), usuario.last_name.strip()] if parte
    ).strip()
    return nome_completo or usuario.username


def navegacao_global(request):
    """Disponibiliza identidade institucional e modulos liberados ao shell autenticado."""

    site_config = SiteConfig.objects.first()
    usuario = getattr(request, 'user', None)
    perfil = obter_perfil_base_usuario(usuario)
    modulos = []
    if usuario and usuario.is_authenticated:
        modulos = [
            {
                **modulo,
                'url': reverse(modulo['url_name']),
            }
            for modulo in obter_modulos_disponiveis(usuario)
        ]

    return {
        'sistema_site_name': (
            site_config.site_name if site_config and site_config.site_name else 'Casa Espirita'
        ),
        'sistema_site_slogan': site_config.slogan if site_config and site_config.slogan else '',
        'sistema_usuario_nome': _nome_usuario(request),
        'sistema_perfil_base_nome': perfil.nome if perfil else '',
        'sistema_modulos_disponiveis': modulos,
        'sistema_admin_tecnico_url': reverse('admin:index'),
        'sistema_inicio_url': reverse('configuracoes:inicio'),
        'sistema_logout_url': reverse('configuracoes:logout'),
        'sistema_login_url': reverse('configuracoes:login'),
    }
