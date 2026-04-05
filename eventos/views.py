from __future__ import annotations

from django.views.generic import TemplateView

from .permissoes import EventosPermissaoMixin


class EventosHomeView(EventosPermissaoMixin, TemplateView):
    """Landing inicial do modulo de eventos."""

    template_name = 'eventos/home.html'
    permissao_requerida = 'eventos.eventos.visualizar'
