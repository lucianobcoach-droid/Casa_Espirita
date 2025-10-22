from __future__ import annotations

from django.contrib import admin

from .models import Autor, Emprestimo, Livro, Venda


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)


class EstoqueDisponivelFilter(admin.SimpleListFilter):
    title = "Disponibilidade"
    parameter_name = "estoque"

    def lookups(self, request, model_admin):
        return (
            ("com_estoque", "Com estoque"),
            ("sem_estoque", "Sem estoque"),
        )

    def queryset(self, request, queryset):
        if self.value() == "com_estoque":
            return queryset.filter(estoque_disponivel__gt=0)
        if self.value() == "sem_estoque":
            return queryset.filter(estoque_disponivel__lte=0)
        return queryset


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "estoque_total", "estoque_disponivel", "preco")
    search_fields = ("titulo", "descricao")
    list_filter = (EstoqueDisponivelFilter, "autores")
    filter_horizontal = ("autores",)


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ("livro", "quantidade", "valor_unitario", "criado_em")
    list_filter = ("livro", "criado_em")
    search_fields = ("livro__titulo", "comprador")


@admin.action(description="Marcar empréstimos selecionados como devolvidos")
def marcar_como_devolvido(modeladmin, request, queryset):
    for emprestimo in queryset:
        emprestimo.marcar_como_devolvido()


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = (
        "livro",
        "leitor",
        "quantidade",
        "data_emprestimo",
        "data_prevista_devolucao",
        "data_devolucao",
        "status",
    )
    list_filter = ("status", "data_emprestimo", "data_prevista_devolucao")
    search_fields = ("livro__titulo", "leitor")
    actions = [marcar_como_devolvido]
