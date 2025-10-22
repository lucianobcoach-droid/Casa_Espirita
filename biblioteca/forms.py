from __future__ import annotations

from django import forms

from .models import Autor, Emprestimo, Livro, Venda


class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ["nome", "biografia"]


class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ["titulo", "descricao", "estoque_total", "estoque_disponivel", "preco", "autores"]


class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ["livro", "quantidade", "valor_unitario", "comprador"]


class EmprestimoForm(forms.ModelForm):
    class Meta:
        model = Emprestimo
        fields = [
            "livro",
            "leitor",
            "quantidade",
            "data_emprestimo",
            "data_prevista_devolucao",
            "data_devolucao",
            "status",
            "observacoes",
        ]
        widgets = {
            "data_emprestimo": forms.DateInput(attrs={"type": "date"}),
            "data_prevista_devolucao": forms.DateInput(attrs={"type": "date"}),
            "data_devolucao": forms.DateInput(attrs={"type": "date"}),
        }
