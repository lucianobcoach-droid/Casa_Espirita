from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class ContaFinanceira(models.Model):
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    data_saldo_inicial = models.DateField()
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Conta financeira'
        verbose_name_plural = 'Contas financeiras'

    def __str__(self) -> str:
        return self.nome


class CentroCusto(models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    nome = models.CharField(max_length=150)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['codigo', 'nome']
        verbose_name = 'Centro de custo'
        verbose_name_plural = 'Centros de custo'

    def __str__(self) -> str:
        return f'{self.codigo} - {self.nome}'


class PessoaFinanceira(models.Model):
    class TipoPessoa(models.TextChoices):
        FISICA = 'fisica', 'Fisica'
        JURIDICA = 'juridica', 'Juridica'

    codigo = models.CharField(max_length=30, unique=True)
    nome = models.CharField(max_length=150)
    tipo_pessoa = models.CharField(
        max_length=20,
        choices=TipoPessoa.choices,
        blank=True,
    )
    documento = models.CharField(max_length=30, blank=True)
    telefone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Pessoa financeira'
        verbose_name_plural = 'Pessoas financeiras'

    def __str__(self) -> str:
        return f'{self.codigo} - {self.nome}'


class CategoriaFinanceira(models.Model):
    class TipoCategoria(models.TextChoices):
        RECEITA = 'receita', 'Receita'
        DESPESA = 'despesa', 'Despesa'

    nome = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=TipoCategoria.choices)
    categoria_pai = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        related_name='subcategorias',
        blank=True,
        null=True,
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['tipo', 'nome']
        verbose_name = 'Categoria financeira'
        verbose_name_plural = 'Categorias financeiras'

    def __str__(self) -> str:
        return f'{self.get_tipo_display()} - {self.nome}'


class LancamentoFinanceiro(models.Model):
    class TipoLancamento(models.TextChoices):
        RECEITA = 'receita', 'Receita'
        DESPESA = 'despesa', 'Despesa'
        TRANSFERENCIA = 'transferencia', 'Transferencia'

    class StatusLancamento(models.TextChoices):
        ABERTO = 'aberto', 'Aberto'
        QUITADO = 'quitado', 'Quitado'
        CANCELADO = 'cancelado', 'Cancelado'

    descricao = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TipoLancamento.choices)
    status = models.CharField(
        max_length=20,
        choices=StatusLancamento.choices,
        default=StatusLancamento.ABERTO,
    )
    valor = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    data_competencia = models.DateField()
    data_pagamento = models.DateField(blank=True, null=True)
    numero_documento = models.CharField(max_length=50, blank=True)
    pessoa = models.ForeignKey(
        PessoaFinanceira,
        on_delete=models.PROTECT,
        related_name='lancamentos',
        blank=True,
        null=True,
    )
    categoria = models.ForeignKey(
        CategoriaFinanceira,
        on_delete=models.PROTECT,
        related_name='lancamentos',
    )
    centro_custo = models.ForeignKey(
        CentroCusto,
        on_delete=models.PROTECT,
        related_name='lancamentos',
        blank=True,
        null=True,
    )
    conta = models.ForeignKey(
        ContaFinanceira,
        on_delete=models.PROTECT,
        related_name='lancamentos_origem',
    )
    conta_destino = models.ForeignKey(
        ContaFinanceira,
        on_delete=models.PROTECT,
        related_name='lancamentos_destino',
        blank=True,
        null=True,
    )
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_competencia', '-criado_em']
        verbose_name = 'Lançamento financeiro'
        verbose_name_plural = 'Lançamentos financeiros'

    def __str__(self) -> str:
        return self.descricao

    def clean(self) -> None:
        errors: dict[str, list[str] | str] = {}
        transferencia = self.tipo == self.TipoLancamento.TRANSFERENCIA

        if transferencia and not self.conta_destino_id:
            errors['conta_destino'] = 'Transferência exige conta_destino.'

        if not transferencia and self.conta_destino_id:
            errors['conta_destino'] = 'conta_destino só pode ser usada em transferência.'

        if self.conta_id and self.conta_destino_id and self.conta_id == self.conta_destino_id:
            errors['conta_destino'] = 'conta e conta_destino não podem ser iguais.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
