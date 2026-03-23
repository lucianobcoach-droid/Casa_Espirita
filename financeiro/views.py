from __future__ import annotations

from django.views.generic import TemplateView


class FinanceiroHomeView(TemplateView):
    template_name = 'financeiro/home.html'

