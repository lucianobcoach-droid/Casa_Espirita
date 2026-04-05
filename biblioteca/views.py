from __future__ import annotations

from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import AutorForm, EmprestimoForm, LivroForm, VendaForm
from .models import Autor, Emprestimo, Livro, Venda
from .permissoes import BibliotecaPermissaoMixin


class AutorListView(BibliotecaPermissaoMixin, ListView):
    model = Autor
    template_name = "biblioteca/autor_list.html"
    context_object_name = "autores"
    permissao_requerida = 'biblioteca.autores.listar'


class AutorCreateView(BibliotecaPermissaoMixin, CreateView):
    model = Autor
    form_class = AutorForm
    template_name = "biblioteca/autor_form.html"
    success_url = reverse_lazy("biblioteca:autor-list")
    permissao_requerida = 'biblioteca.autores.criar'


class LivroListView(BibliotecaPermissaoMixin, ListView):
    model = Livro
    template_name = "biblioteca/livro_list.html"
    context_object_name = "livros"
    permissao_requerida = 'biblioteca.livros.listar'


class LivroCreateView(BibliotecaPermissaoMixin, CreateView):
    model = Livro
    form_class = LivroForm
    template_name = "biblioteca/livro_form.html"
    success_url = reverse_lazy("biblioteca:livro-list")
    permissao_requerida = 'biblioteca.livros.criar'


class VendaListView(BibliotecaPermissaoMixin, ListView):
    model = Venda
    template_name = "biblioteca/venda_list.html"
    context_object_name = "vendas"
    permissao_requerida = 'biblioteca.vendas.listar'


class VendaCreateView(BibliotecaPermissaoMixin, CreateView):
    model = Venda
    form_class = VendaForm
    template_name = "biblioteca/venda_form.html"
    success_url = reverse_lazy("biblioteca:venda-list")
    permissao_requerida = 'biblioteca.vendas.criar'


class EmprestimoListView(BibliotecaPermissaoMixin, ListView):
    model = Emprestimo
    template_name = "biblioteca/emprestimo_list.html"
    context_object_name = "emprestimos"
    permissao_requerida = 'biblioteca.emprestimos.listar'


class EmprestimoCreateView(BibliotecaPermissaoMixin, CreateView):
    model = Emprestimo
    form_class = EmprestimoForm
    template_name = "biblioteca/emprestimo_form.html"
    success_url = reverse_lazy("biblioteca:emprestimo-list")
    permissao_requerida = 'biblioteca.emprestimos.criar'
