"""URL configuration for the Casa Espirita project."""
from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

from configuracoes.views import ConfiguracoesPasswordResetView, SiteConfigDetailView

urlpatterns = [
    path('admin/password_reset/', ConfiguracoesPasswordResetView.as_view(), name='admin_password_reset'),
    path('admin/', admin.site.urls),
    path('configuracoes/', SiteConfigDetailView.as_view(), name='configuracoes-entrada'),
    path('', include('configuracoes.urls')),
    path('biblioteca/', include('biblioteca.urls')),
    path('eventos/', include('eventos.urls')),
    path('financeiro/', include('financeiro.urls')),
]
