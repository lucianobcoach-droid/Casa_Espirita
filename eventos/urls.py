from __future__ import annotations

from django.urls import path

from .views import EventosHomeView

app_name = 'eventos'

urlpatterns = [
    path('', EventosHomeView.as_view(), name='home'),
]
