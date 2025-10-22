"""URL configuration for the Casa Espírita project."""
from __future__ import annotations

from django.contrib import admin
from django.urls import path
from configuracoes.views import SiteConfigDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', SiteConfigDetailView.as_view(), name='site-config'),
]
