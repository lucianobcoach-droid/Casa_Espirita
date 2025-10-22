from __future__ import annotations

from django.urls import path

from . import views

app_name = "biblioteca"

urlpatterns = [
    path("autores/", views.AutorListView.as_view(), name="autor-list"),
    path("autores/novo/", views.AutorCreateView.as_view(), name="autor-create"),
    path("livros/", views.LivroListView.as_view(), name="livro-list"),
    path("livros/novo/", views.LivroCreateView.as_view(), name="livro-create"),
    path("vendas/", views.VendaListView.as_view(), name="venda-list"),
    path("vendas/nova/", views.VendaCreateView.as_view(), name="venda-create"),
    path("emprestimos/", views.EmprestimoListView.as_view(), name="emprestimo-list"),
    path("emprestimos/novo/", views.EmprestimoCreateView.as_view(), name="emprestimo-create"),
]
