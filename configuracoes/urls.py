"""Rotas de autenticacao e configuracoes institucionais."""
from __future__ import annotations

from django.urls import path

from .views import ConfiguracoesLoginView, ConfiguracoesLogoutView, SiteConfigDetailView

app_name = 'configuracoes'

urlpatterns = [
    path('', SiteConfigDetailView.as_view(), name='site-config'),
    path('login/', ConfiguracoesLoginView.as_view(), name='login'),
    path('logout/', ConfiguracoesLogoutView.as_view(), name='logout'),
]
