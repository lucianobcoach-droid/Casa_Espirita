from __future__ import annotations

import re
import unicodedata
from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TipoContaFinanceira(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveSmallIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordem', 'nome']
        verbose_name = 'Tipo de conta financeira'
        verbose_name_plural = 'Tipos de conta financeira'

    def __str__(self) -> str:
        return self.nome


class ContaFinanceira(models.Model):
    class DisponibilidadeConta(models.TextChoices):
        DISPONIVEL = 'disponivel', 'Disponivel'
        INDISPONIVEL = 'indisponivel', 'Indisponivel/vinculada'

    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    data_saldo_inicial = models.DateField()
    tipo_conta = models.ForeignKey(
        TipoContaFinanceira,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name='contas',
    )
    disponibilidade = models.CharField(
        max_length=20,
        choices=DisponibilidadeConta.choices,
        default=DisponibilidadeConta.DISPONIVEL,
    )
    mensagem_indisponibilidade = models.TextField(blank=True)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Conta financeira'
        verbose_name_plural = 'Contas financeiras'

    def __str__(self) -> str:
        return self.nome


def _proximo_codigo_sequencial(modelo, min_width: int = 4) -> str:
    max_codigo = 0
    for codigo in modelo.objects.values_list('codigo', flat=True):
        codigo_str = (codigo or '').strip()
        if codigo_str.isdigit():
            max_codigo = max(max_codigo, int(codigo_str))
    proximo = max_codigo + 1
    width = max(min_width, len(str(proximo)))
    return str(proximo).zfill(width)


def normalizar_nome_pessoa_financeira(valor: str) -> str:
    valor_sem_acentos = unicodedata.normalize('NFKD', valor or '')
    valor_sem_acentos = ''.join(
        caractere
        for caractere in valor_sem_acentos
        if not unicodedata.combining(caractere)
    )
    return re.sub(r'\s+', ' ', valor_sem_acentos).strip().casefold()


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

    def save(self, *args, **kwargs) -> None:
        if not (self.codigo or '').strip():
            if self.pk:
                codigo_atual = (
                    type(self).objects.filter(pk=self.pk).values_list('codigo', flat=True).first()
                )
                if codigo_atual:
                    self.codigo = codigo_atual
                else:
                    self.codigo = _proximo_codigo_sequencial(type(self))
            else:
                self.codigo = _proximo_codigo_sequencial(type(self))
        super().save(*args, **kwargs)


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

    def clean(self) -> None:
        super().clean()
        nome_normalizado = normalizar_nome_pessoa_financeira(self.nome)
        if not nome_normalizado:
            return

        queryset = type(self).objects.all()
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        for pessoa in queryset.only('nome'):
            if normalizar_nome_pessoa_financeira(pessoa.nome) == nome_normalizado:
                raise ValidationError({'nome': 'Já existe um favorecido cadastrado com este nome.'})

    def save(self, *args, **kwargs) -> None:
        if not (self.codigo or '').strip():
            if self.pk:
                codigo_atual = (
                    type(self).objects.filter(pk=self.pk).values_list('codigo', flat=True).first()
                )
                if codigo_atual:
                    self.codigo = codigo_atual
                else:
                    self.codigo = _proximo_codigo_sequencial(type(self))
            else:
                self.codigo = _proximo_codigo_sequencial(type(self))
        super().save(*args, **kwargs)


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
    mensagem_recibo = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['tipo', 'nome']
        verbose_name = 'Categoria financeira'
        verbose_name_plural = 'Categorias financeiras'

    def __str__(self) -> str:
        return self.nome

    @property
    def label_completo(self) -> str:
        return f'{self.get_tipo_display()} - {self.nome}'

    @property
    def permite_vinculo_em_lancamento(self) -> bool:
        return bool(self.categoria_pai_id)


class AssinaturaInstitucional(models.Model):
    nome = models.CharField(max_length=150)
    assinatura_texto = models.CharField(max_length=150)
    nome_exibicao = models.CharField(max_length=150, blank=True)
    cargo = models.CharField(max_length=150, blank=True)
    ativo = models.BooleanField(default=True)
    padrao = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-padrao', 'nome']
        verbose_name = 'Assinatura institucional'
        verbose_name_plural = 'Assinaturas institucionais'

    def __str__(self) -> str:
        return self.nome

    def clean(self) -> None:
        errors: dict[str, str] = {}

        if self.padrao and not self.ativo:
            errors['ativo'] = 'A assinatura padrao precisa estar ativa.'

        if self.padrao:
            queryset = type(self).objects.filter(padrao=True)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                errors['padrao'] = 'Ja existe outra assinatura marcada como padrao.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class ConfiguracaoInstitucional(models.Model):
    nome_instituicao = models.CharField(max_length=200, blank=True)
    cidade = models.CharField(max_length=120, blank=True)
    logo_url = models.URLField(blank=True)
    mensagem_padrao_recibo = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    padrao = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-padrao', '-ativo', 'nome_instituicao']
        verbose_name = 'Configuracao institucional'
        verbose_name_plural = 'Configuracoes institucionais'

    def __str__(self) -> str:
        return self.nome_instituicao or 'Configuracao institucional'

    def clean(self) -> None:
        errors: dict[str, str] = {}

        if self.padrao and not self.ativo:
            errors['ativo'] = 'A configuracao padrao precisa estar ativa.'

        if self.padrao:
            queryset = type(self).objects.filter(padrao=True)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                errors['padrao'] = 'Ja existe outra configuracao institucional marcada como padrao.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class AuditoriaFinanceiro(models.Model):
    class AcaoAuditoria(models.TextChoices):
        CREATE = 'create', 'Criacao'
        UPDATE = 'update', 'Atualizacao'
        DELETE = 'delete', 'Exclusao'

    acao = models.CharField(max_length=20, choices=AcaoAuditoria.choices)
    modelo = models.CharField(max_length=100)
    registro_id = models.PositiveBigIntegerField()
    data_hora = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditorias_financeiro',
    )
    campos_alterados = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-data_hora', '-pk']
        verbose_name = 'Auditoria do financeiro'
        verbose_name_plural = 'Auditorias do financeiro'

    def __str__(self) -> str:
        return f'{self.modelo} #{self.registro_id} - {self.acao}'


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
    com_rateio = models.BooleanField(default=False)
    grupo_rateio = models.CharField(max_length=36, blank=True, db_index=True)
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
        blank=True,
        null=True,
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
        verbose_name = 'Lancamento financeiro'
        verbose_name_plural = 'Lancamentos financeiros'

    def __str__(self) -> str:
        return self.descricao

    def clean(self) -> None:
        errors: dict[str, list[str] | str] = {}
        transferencia = self.tipo == self.TipoLancamento.TRANSFERENCIA
        lancamento_operacional = self.tipo in {
            self.TipoLancamento.RECEITA,
            self.TipoLancamento.DESPESA,
        }

        if self.com_rateio and not self.grupo_rateio:
            errors['grupo_rateio'] = 'Lancamentos com rateio precisam estar vinculados a um grupo de rateio.'

        if not self.data_competencia:
            errors['data_competencia'] = 'Informe a data de competencia.'

        if not self.data_pagamento:
            errors['data_pagamento'] = 'Informe a data de pagamento.'

        if self.data_competencia and self.data_pagamento and self.data_pagamento < self.data_competencia:
            errors['data_pagamento'] = 'A data de pagamento nao pode ser anterior a data de competencia.'

        if transferencia and not self.conta_destino_id:
            errors['conta_destino'] = 'Transferencia exige conta_destino.'

        if not transferencia and self.conta_destino_id:
            errors['conta_destino'] = 'conta_destino so pode ser usada em transferencia.'

        if self.conta_id and self.conta_destino_id and self.conta_id == self.conta_destino_id:
            errors['conta_destino'] = 'A conta de destino precisa ser diferente da conta de origem.'

        if lancamento_operacional and not self.pessoa_id:
            errors['pessoa'] = 'Pessoa e obrigatoria para receita e despesa.'

        if lancamento_operacional and not self.categoria_id:
            errors['categoria'] = 'Categoria e obrigatoria para receita e despesa.'
        elif lancamento_operacional and self.categoria_id and not self.categoria.permite_vinculo_em_lancamento:
            errors['categoria'] = 'Selecione uma subcategoria para receita e despesa. Categoria pai nao pode ser usada em lancamentos.'

        numero_documento = (self.numero_documento or '').strip()
        if numero_documento:
            self.numero_documento = numero_documento
            queryset = type(self).objects.filter(numero_documento=numero_documento)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                if not self.com_rateio:
                    errors['numero_documento'] = 'Ja existe outro lancamento com este numero de documento.'
                elif not self.grupo_rateio or queryset.exclude(grupo_rateio=self.grupo_rateio).exists():
                    errors['numero_documento'] = (
                        'Ja existe outro lancamento com este numero de documento fora do mesmo grupo de rateio.'
                    )

        if self.com_rateio and self.grupo_rateio:
            grupo_queryset = type(self).objects.filter(grupo_rateio=self.grupo_rateio)
            if self.pk:
                grupo_queryset = grupo_queryset.exclude(pk=self.pk)

            if grupo_queryset.exists():
                numeros_grupo = {
                    (lancamento.numero_documento or '').strip()
                    for lancamento in grupo_queryset.only('numero_documento')
                }
                numeros_grupo.discard('')
                if numeros_grupo:
                    if len(numeros_grupo) > 1:
                        errors['numero_documento'] = (
                            'O grupo de rateio possui linhas com numeros de documento divergentes e precisa ser regularizado.'
                        )
                    elif numero_documento and numero_documento not in numeros_grupo:
                        errors['numero_documento'] = (
                            'Lancamentos do mesmo grupo de rateio precisam compartilhar o mesmo numero de documento.'
                        )

        if errors:
            raise ValidationError(errors)

    def _gerar_numero_documento(self) -> str:
        referencia = self.data_competencia or timezone.localdate()
        prefixo = referencia.strftime('%d%m%y')
        queryset = type(self).objects.all()
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        for _ in range(50):
            sufixo = f'{uuid4().int % 1000:03d}'
            numero_documento = f'{prefixo}-{sufixo}'
            if not queryset.filter(numero_documento=numero_documento).exists():
                return numero_documento

        raise ValidationError(
            {'numero_documento': 'Nao foi possivel gerar um numero de documento unico automaticamente.'}
        )

    def save(self, *args, **kwargs) -> None:
        if not self.numero_documento:
            self.numero_documento = self._gerar_numero_documento()
        self.full_clean()
        super().save(*args, **kwargs)


class RegraLancamentoFinanceiro(models.Model):
    descricao = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=LancamentoFinanceiro.TipoLancamento.choices)
    pessoa = models.ForeignKey(
        PessoaFinanceira,
        on_delete=models.PROTECT,
        related_name='regras_lancamento',
        blank=True,
        null=True,
    )
    categoria = models.ForeignKey(
        CategoriaFinanceira,
        on_delete=models.PROTECT,
        related_name='regras_lancamento',
        blank=True,
        null=True,
    )
    centro_custo = models.ForeignKey(
        CentroCusto,
        on_delete=models.PROTECT,
        related_name='regras_lancamento',
        blank=True,
        null=True,
    )
    conta = models.ForeignKey(
        ContaFinanceira,
        on_delete=models.PROTECT,
        related_name='regras_lancamento_origem',
    )
    conta_destino = models.ForeignKey(
        ContaFinanceira,
        on_delete=models.PROTECT,
        related_name='regras_lancamento_destino',
        blank=True,
        null=True,
    )
    observacoes = models.TextField(blank=True)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['descricao', '-atualizado_em', '-pk']
        verbose_name = 'Regra de lancamento financeiro'
        verbose_name_plural = 'Regras de lancamento financeiro'

    def __str__(self) -> str:
        return self.descricao

    def clean(self) -> None:
        errors: dict[str, str] = {}
        transferencia = self.tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA
        lancamento_operacional = self.tipo in {
            LancamentoFinanceiro.TipoLancamento.RECEITA,
            LancamentoFinanceiro.TipoLancamento.DESPESA,
        }

        if transferencia and not self.conta_destino_id:
            errors['conta_destino'] = 'Transferencia exige conta_destino.'

        if not transferencia and self.conta_destino_id:
            errors['conta_destino'] = 'conta_destino so pode ser usada em transferencia.'

        if self.conta_id and self.conta_destino_id and self.conta_id == self.conta_destino_id:
            errors['conta_destino'] = 'A conta de destino precisa ser diferente da conta de origem.'

        if lancamento_operacional and not self.pessoa_id:
            errors['pessoa'] = 'Pessoa e obrigatoria para receita e despesa.'

        if lancamento_operacional and not self.categoria_id:
            errors['categoria'] = 'Categoria e obrigatoria para receita e despesa.'
        elif lancamento_operacional and self.categoria_id and not self.categoria.permite_vinculo_em_lancamento:
            errors['categoria'] = 'Selecione uma subcategoria para receita e despesa. Categoria pai nao pode ser usada em regras.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
