"""URL configuration for the Casa Espírita project."""
from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('configuracoes.urls')),
    path('biblioteca/', include('biblioteca.urls')),
    path('financeiro/', include('financeiro.urls')),
]
