"""URL configuration for the Casa Espirita project."""
from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

from configuracoes.views import ConfiguracoesPasswordResetView

urlpatterns = [
    path('admin/password_reset/', ConfiguracoesPasswordResetView.as_view(), name='admin_password_reset'),
    path('admin/', admin.site.urls),
    path('', include('configuracoes.urls')),
    path('biblioteca/', include('biblioteca.urls')),
    path('financeiro/', include('financeiro.urls')),
]
