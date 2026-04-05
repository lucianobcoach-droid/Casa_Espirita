"""Rotas de autenticacao e configuracoes institucionais."""
from __future__ import annotations

from django.urls import path

from .views import (
    ConfiguracoesLoginView,
    ConfiguracoesLogoutView,
    ConfiguracoesPasswordResetCompleteView,
    ConfiguracoesPasswordResetConfirmView,
    ConfiguracoesPasswordResetDoneView,
    ConfiguracoesPasswordResetView,
    SiteConfigDetailView,
    SistemaInicioView,
)

app_name = 'configuracoes'

urlpatterns = [
    path('', SiteConfigDetailView.as_view(), name='site-config'),
    path('inicio/', SistemaInicioView.as_view(), name='inicio'),
    path('login/', ConfiguracoesLoginView.as_view(), name='login'),
    path('logout/', ConfiguracoesLogoutView.as_view(), name='logout'),
    path('senha/esqueci/', ConfiguracoesPasswordResetView.as_view(), name='password-reset'),
    path('senha/esqueci/enviado/', ConfiguracoesPasswordResetDoneView.as_view(), name='password-reset-done'),
    path('senha/redefinir/<uidb64>/<token>/', ConfiguracoesPasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('senha/redefinir/concluido/', ConfiguracoesPasswordResetCompleteView.as_view(), name='password-reset-complete'),
]
