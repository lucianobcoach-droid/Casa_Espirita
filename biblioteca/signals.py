from __future__ import annotations

from datetime import date

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Emprestimo, Livro, Venda


def _clamp_estoque(livro: Livro) -> None:
    if livro.estoque_disponivel is None:
        livro.estoque_disponivel = livro.estoque_total
    if livro.estoque_disponivel < 0:
        livro.estoque_disponivel = 0
    if livro.estoque_disponivel > livro.estoque_total:
        livro.estoque_disponivel = livro.estoque_total
    livro.save(update_fields=["estoque_disponivel"])


@receiver(pre_save, sender=Venda)
def registrar_delta_venda(sender, instance: Venda, **kwargs) -> None:
    if instance.pk:
        anterior = Venda.objects.get(pk=instance.pk)
        instance._estoque_delta = instance.quantidade - anterior.quantidade
    else:
        instance._estoque_delta = instance.quantidade
    if not instance.valor_unitario:
        instance.valor_unitario = instance.livro.preco


@receiver(post_save, sender=Venda)
def ajustar_estoque_venda(sender, instance: Venda, created: bool, **kwargs) -> None:
    delta = getattr(instance, "_estoque_delta", instance.quantidade if created else 0)
    if delta:
        livro = instance.livro
        livro.estoque_disponivel = max(livro.estoque_disponivel - delta, 0)
        _clamp_estoque(livro)
    if hasattr(instance, "_estoque_delta"):
        delattr(instance, "_estoque_delta")


@receiver(post_delete, sender=Venda)
def restaurar_estoque_venda(sender, instance: Venda, **kwargs) -> None:
    livro = instance.livro
    livro.estoque_disponivel = min(livro.estoque_disponivel + instance.quantidade, livro.estoque_total)
    _clamp_estoque(livro)


def _status_ativo(status: str) -> bool:
    return status in {Emprestimo.STATUS_PENDENTE, Emprestimo.STATUS_ATRASADO}


@receiver(pre_save, sender=Emprestimo)
def registrar_delta_emprestimo(sender, instance: Emprestimo, **kwargs) -> None:
    hoje = date.today()
    if instance.status != Emprestimo.STATUS_DEVOLVIDO and instance.data_prevista_devolucao < hoje:
        instance.status = Emprestimo.STATUS_ATRASADO
    if instance.status == Emprestimo.STATUS_DEVOLVIDO and instance.data_devolucao is None:
        instance.data_devolucao = timezone.now().date()
    if instance.pk:
        anterior = Emprestimo.objects.get(pk=instance.pk)
        ativo_anterior = _status_ativo(anterior.status)
        ativo_atual = _status_ativo(instance.status)
        delta_anterior = anterior.quantidade if ativo_anterior else 0
        delta_atual = instance.quantidade if ativo_atual else 0
        instance._estoque_delta = delta_atual - delta_anterior
    else:
        instance._estoque_delta = instance.quantidade if _status_ativo(instance.status) else 0


@receiver(post_save, sender=Emprestimo)
def ajustar_estoque_emprestimo(sender, instance: Emprestimo, **kwargs) -> None:
    delta = getattr(instance, "_estoque_delta", 0)
    if delta:
        livro = instance.livro
        livro.estoque_disponivel = max(livro.estoque_disponivel - delta, 0)
        _clamp_estoque(livro)
    if hasattr(instance, "_estoque_delta"):
        delattr(instance, "_estoque_delta")


@receiver(post_delete, sender=Emprestimo)
def restaurar_estoque_emprestimo(sender, instance: Emprestimo, **kwargs) -> None:
    if _status_ativo(instance.status):
        livro = instance.livro
        livro.estoque_disponivel = min(livro.estoque_disponivel + instance.quantidade, livro.estoque_total)
        _clamp_estoque(livro)
