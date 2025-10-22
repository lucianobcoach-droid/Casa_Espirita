from __future__ import annotations

from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import AutorForm, EmprestimoForm, LivroForm, VendaForm
from .models import Autor, Emprestimo, Livro, Venda


class AutorListView(ListView):
    model = Autor
    template_name = "biblioteca/autor_list.html"
    context_object_name = "autores"


class AutorCreateView(CreateView):
    model = Autor
    form_class = AutorForm
    template_name = "biblioteca/autor_form.html"
    success_url = reverse_lazy("biblioteca:autor-list")


class LivroListView(ListView):
    model = Livro
    template_name = "biblioteca/livro_list.html"
    context_object_name = "livros"


class LivroCreateView(CreateView):
    model = Livro
    form_class = LivroForm
    template_name = "biblioteca/livro_form.html"
    success_url = reverse_lazy("biblioteca:livro-list")


class VendaListView(ListView):
    model = Venda
    template_name = "biblioteca/venda_list.html"
    context_object_name = "vendas"


class VendaCreateView(CreateView):
    model = Venda
    form_class = VendaForm
    template_name = "biblioteca/venda_form.html"
    success_url = reverse_lazy("biblioteca:venda-list")


class EmprestimoListView(ListView):
    model = Emprestimo
    template_name = "biblioteca/emprestimo_list.html"
    context_object_name = "emprestimos"


class EmprestimoCreateView(CreateView):
    model = Emprestimo
    form_class = EmprestimoForm
    template_name = "biblioteca/emprestimo_form.html"
    success_url = reverse_lazy("biblioteca:emprestimo-list")
