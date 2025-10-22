from __future__ import annotations

from datetime import date

from django.db import models
from django.utils import timezone


class Autor(models.Model):
    nome = models.CharField(max_length=255)
    biografia = models.TextField(blank=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class Livro(models.Model):
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    estoque_total = models.PositiveIntegerField()
    estoque_disponivel = models.PositiveIntegerField(blank=True, null=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    autores = models.ManyToManyField(Autor, related_name="livros")

    class Meta:
        ordering = ["titulo"]

    def __str__(self) -> str:
        return self.titulo

    def save(self, *args, **kwargs) -> None:
        if self.estoque_total is None:
            self.estoque_total = 0
        if self.estoque_disponivel is None:
            self.estoque_disponivel = self.estoque_total
        else:
            self.estoque_disponivel = min(self.estoque_disponivel, self.estoque_total)
        super().save(*args, **kwargs)

    def ajustar_estoque(self, diferenca: int) -> None:
        """Atualiza o estoque disponível garantindo limites válidos."""
        novo_valor = (self.estoque_disponivel or 0) - diferenca
        if novo_valor < 0:
            novo_valor = 0
        if novo_valor > self.estoque_total:
            novo_valor = self.estoque_total
        self.estoque_disponivel = novo_valor
        self.save(update_fields=["estoque_disponivel"])


class Venda(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.PROTECT, related_name="vendas")
    quantidade = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    comprador = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self) -> str:
        return f"Venda de {self.livro} ({self.quantidade})"

    @property
    def valor_total(self):
        return self.quantidade * self.valor_unitario


class Emprestimo(models.Model):
    STATUS_PENDENTE = "pendente"
    STATUS_DEVOLVIDO = "devolvido"
    STATUS_ATRASADO = "atrasado"
    STATUS_CHOICES = [
        (STATUS_PENDENTE, "Pendente"),
        (STATUS_ATRASADO, "Atrasado"),
        (STATUS_DEVOLVIDO, "Devolvido"),
    ]

    livro = models.ForeignKey(Livro, on_delete=models.PROTECT, related_name="emprestimos")
    leitor = models.CharField(max_length=255)
    quantidade = models.PositiveIntegerField(default=1)
    data_emprestimo = models.DateField(default=timezone.now)
    data_prevista_devolucao = models.DateField()
    data_devolucao = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDENTE)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-data_emprestimo", "leitor"]

    def __str__(self) -> str:
        return f"Empréstimo de {self.livro} para {self.leitor}"

    @property
    def esta_atrasado(self) -> bool:
        hoje = date.today()
        if self.status == self.STATUS_DEVOLVIDO:
            return False
        return self.data_prevista_devolucao < hoje

    def marcar_como_devolvido(self) -> None:
        self.status = self.STATUS_DEVOLVIDO
        self.data_devolucao = timezone.now().date()
        self.save(update_fields=["status", "data_devolucao", "atualizado_em"])
