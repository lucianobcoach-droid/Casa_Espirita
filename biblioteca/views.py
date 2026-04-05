from __future__ import annotations

from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView

from .forms import AutorForm, EmprestimoForm, LivroForm, VendaForm
from .models import Autor, Emprestimo, Livro, Venda
from .permissoes import BibliotecaPermissaoMixin
from configuracoes.permissoes import usuario_possui_permissao


class BibliotecaHomeRedirectView(BibliotecaPermissaoMixin, View):
    """Resolve a entrada canonica do modulo para a primeira tela liberada."""

    permissao_requerida = 'biblioteca.autores.listar'
    entradas_canonicas = (
        ('biblioteca.autores.listar', 'biblioteca:autor-list'),
        ('biblioteca.livros.listar', 'biblioteca:livro-list'),
        ('biblioteca.vendas.listar', 'biblioteca:venda-list'),
        ('biblioteca.emprestimos.listar', 'biblioteca:emprestimo-list'),
    )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        for codigo_permissao, url_name in self.entradas_canonicas:
            if usuario_possui_permissao(request.user, codigo_permissao):
                return HttpResponseRedirect(reverse_lazy(url_name))

        return HttpResponseForbidden(self.get_permission_denied_message())


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
