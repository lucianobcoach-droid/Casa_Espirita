from __future__ import annotations

import re
import unicodedata
from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
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


def _normalizar_identificador_textual(valor: str) -> str:
    valor_sem_acentos = unicodedata.normalize('NFKD', valor or '')
    valor_sem_acentos = ''.join(
        caractere
        for caractere in valor_sem_acentos
        if not unicodedata.combining(caractere)
    )
    return re.sub(r'\s+', ' ', valor_sem_acentos).strip().casefold()


def _contar_casas_decimais(valor: Decimal) -> int:
    if valor is None:
        return 0
    return max(-valor.as_tuple().exponent, 0)


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
    contribuinte_recorrente = models.BooleanField(default=False)
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
    controla_recorrencia_competencia = models.BooleanField(default=False)
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

    def usa_controle_competencia(self) -> bool:
        return bool(
            self.tipo in {
                self.TipoLancamento.RECEITA,
                self.TipoLancamento.DESPESA,
            }
            and self.pessoa_id
            and self.categoria_id
            and self.pessoa.contribuinte_recorrente
            and self.categoria.controla_recorrencia_competencia
            and self.categoria.permite_vinculo_em_lancamento
        )

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


class AlocacaoCompetenciaFinanceira(models.Model):
    lancamento = models.ForeignKey(
        LancamentoFinanceiro,
        on_delete=models.CASCADE,
        related_name='alocacoes_competencia',
    )
    categoria = models.ForeignKey(
        CategoriaFinanceira,
        on_delete=models.PROTECT,
        related_name='alocacoes_competencia',
    )
    ano_competencia = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(9999)],
    )
    mes_competencia = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
    )
    valor_alocado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ano_competencia', 'mes_competencia', 'pk']
        verbose_name = 'Alocacao de competencia financeira'
        verbose_name_plural = 'Alocacoes de competencia financeira'

    def __str__(self) -> str:
        return (
            f'{self.lancamento.descricao} - '
            f'{self.mes_competencia:02d}/{self.ano_competencia} - '
            f'{self.valor_alocado}'
        )

    def clean(self) -> None:
        super().clean()
        errors: dict[str, str] = {}

        if self.valor_alocado <= Decimal('0.00'):
            errors['valor_alocado'] = 'O valor alocado precisa ser positivo.'

        if self.lancamento_id and self.categoria_id:
            if self.lancamento.tipo == LancamentoFinanceiro.TipoLancamento.TRANSFERENCIA:
                errors['lancamento'] = 'Transferencia nao usa alocacao de competencia.'

            if self.lancamento.categoria_id != self.categoria_id:
                errors['categoria'] = (
                    'A subcategoria da alocacao precisa ser igual a subcategoria do lancamento.'
                )

            if not self.categoria.controla_recorrencia_competencia:
                errors['categoria'] = 'A subcategoria informada nao controla recorrencia por competencia.'

            if not self.categoria.permite_vinculo_em_lancamento:
                errors['categoria'] = 'A alocacao de competencia exige uma subcategoria valida.'

            if not self.lancamento.pessoa_id or not self.lancamento.pessoa.contribuinte_recorrente:
                errors['lancamento'] = 'A alocacao exige favorecido recorrente vinculado ao lancamento.'

        if errors:
            raise ValidationError(errors)


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


class TabelaPersonalizada(models.Model):
    class StatusTabela(models.TextChoices):
        ATIVA = 'ativa', 'Ativa'
        INATIVA = 'inativa', 'Inativa'
        ARQUIVADA = 'arquivada', 'Arquivada'

    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=StatusTabela.choices,
        default=StatusTabela.ATIVA,
    )
    ordem = models.PositiveIntegerField(default=0)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='tabelas_personalizadas_criadas',
        null=True,
        blank=True,
    )
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='tabelas_personalizadas_atualizadas',
        null=True,
        blank=True,
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordem', 'nome', 'pk']
        verbose_name = 'Tabela personalizada'
        verbose_name_plural = 'Tabelas personalizadas'

    def __str__(self) -> str:
        return self.nome

    def clean(self) -> None:
        super().clean()
        errors: dict[str, str] = {}
        nome_normalizado = _normalizar_identificador_textual(self.nome)

        if not nome_normalizado:
            errors['nome'] = 'Informe o nome da tabela.'
        elif self.status != self.StatusTabela.ARQUIVADA:
            queryset = type(self).objects.exclude(status=self.StatusTabela.ARQUIVADA)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            for tabela in queryset.only('nome'):
                if _normalizar_identificador_textual(tabela.nome) == nome_normalizado:
                    errors['nome'] = 'Ja existe outra tabela personalizada ativa/inativa com este nome.'
                    break

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class ColunaPersonalizada(models.Model):
    class StatusColuna(models.TextChoices):
        ATIVA = 'ativa', 'Ativa'
        INATIVA = 'inativa', 'Inativa'
        ARQUIVADA = 'arquivada', 'Arquivada'

    class TipoDado(models.TextChoices):
        TEXTO_CURTO = 'texto_curto', 'Texto curto'
        TEXTO_LONGO = 'texto_longo', 'Texto longo'
        INTEIRO = 'inteiro', 'Inteiro'
        DECIMAL = 'decimal', 'Decimal'
        MONETARIO = 'monetario', 'Monetario'
        PERCENTUAL = 'percentual', 'Percentual'
        DATA = 'data', 'Data'
        MES_COMPETENCIA = 'mes_competencia', 'Mes/competencia'
        BOOLEANO = 'booleano', 'Booleano'
        LISTA_OPCOES = 'lista_opcoes', 'Lista de opcoes'
        FORMULA_CONTROLADA = 'formula_controlada', 'Formula controlada'

    class OperadorFiltro(models.TextChoices):
        ENTRE = 'entre', 'Entre'
        IGUAL = 'igual', 'Igual'
        ANTES = 'antes', 'Antes'
        DEPOIS = 'depois', 'Depois'
        MAIOR = 'maior', 'Maior que'
        MENOR = 'menor', 'Menor que'

    class OperacaoFormula(models.TextChoices):
        SOMA = 'soma', 'Soma'
        SUBTRACAO = 'subtracao', 'Subtracao'
        MULTIPLICACAO = 'multiplicacao', 'Multiplicacao'
        DIVISAO = 'divisao', 'Divisao'

    tabela = models.ForeignKey(
        TabelaPersonalizada,
        on_delete=models.CASCADE,
        related_name='colunas',
    )
    nome = models.CharField(max_length=150)
    tipo_dado = models.CharField(max_length=30, choices=TipoDado.choices)
    obrigatoria = models.BooleanField(default=False)
    visivel = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0)
    calculada = models.BooleanField(default=False)
    configuracao_json = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20,
        choices=StatusColuna.choices,
        default=StatusColuna.ATIVA,
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['tabela_id', 'ordem', 'nome', 'pk']
        verbose_name = 'Coluna personalizada'
        verbose_name_plural = 'Colunas personalizadas'

    def __str__(self) -> str:
        return f'{self.tabela.nome} - {self.nome}'

    @classmethod
    def tipos_elegiveis_filtro_estruturado(cls) -> tuple[str, ...]:
        return (
            cls.TipoDado.DATA,
            cls.TipoDado.MES_COMPETENCIA,
            cls.TipoDado.INTEIRO,
            cls.TipoDado.DECIMAL,
            cls.TipoDado.MONETARIO,
            cls.TipoDado.PERCENTUAL,
        )

    @classmethod
    def filtro_estruturado_elegivel(cls, tipo_dado: str | None) -> bool:
        return tipo_dado in cls.tipos_elegiveis_filtro_estruturado()

    @classmethod
    def operadores_filtro_por_tipo_dado(cls, tipo_dado: str | None) -> tuple[str, ...]:
        if tipo_dado == cls.TipoDado.DATA:
            return (
                cls.OperadorFiltro.ENTRE,
                cls.OperadorFiltro.IGUAL,
                cls.OperadorFiltro.ANTES,
                cls.OperadorFiltro.DEPOIS,
            )
        if tipo_dado == cls.TipoDado.MES_COMPETENCIA:
            return (
                cls.OperadorFiltro.ENTRE,
                cls.OperadorFiltro.IGUAL,
            )
        if tipo_dado in {
            cls.TipoDado.INTEIRO,
            cls.TipoDado.DECIMAL,
            cls.TipoDado.MONETARIO,
            cls.TipoDado.PERCENTUAL,
        }:
            return (
                cls.OperadorFiltro.ENTRE,
                cls.OperadorFiltro.IGUAL,
                cls.OperadorFiltro.MAIOR,
                cls.OperadorFiltro.MENOR,
            )
        return ()

    @classmethod
    def rotulo_operador_filtro(cls, operador: str) -> str:
        try:
            return cls.OperadorFiltro(operador).label
        except ValueError:
            return operador

    @classmethod
    def tipos_elegiveis_formula_fonte(cls) -> tuple[str, ...]:
        return (
            cls.TipoDado.INTEIRO,
            cls.TipoDado.DECIMAL,
            cls.TipoDado.MONETARIO,
            cls.TipoDado.PERCENTUAL,
        )

    @classmethod
    def tipos_elegiveis_formula_resultado(cls) -> tuple[str, ...]:
        return (
            cls.TipoDado.DECIMAL,
            cls.TipoDado.MONETARIO,
        )

    @classmethod
    def operacoes_formula_guiada(cls) -> tuple[str, ...]:
        return tuple(valor for valor, _rotulo in cls.OperacaoFormula.choices)

    @classmethod
    def rotulo_operacao_formula(cls, operacao: str) -> str:
        try:
            return cls.OperacaoFormula(operacao).label
        except ValueError:
            return operacao

    @classmethod
    def limite_casas_decimais_formula(cls, tipo_resultado: str | None) -> tuple[int, int] | None:
        if tipo_resultado == cls.TipoDado.MONETARIO:
            return (2, 2)
        if tipo_resultado == cls.TipoDado.DECIMAL:
            return (0, 8)
        return None

    @property
    def filtro_estruturado_config(self) -> dict[str, object]:
        configuracao = self.configuracao_json if isinstance(self.configuracao_json, dict) else {}
        filtro = configuracao.get('filtro', {})
        return filtro if isinstance(filtro, dict) else {}

    @property
    def filtro_estruturado_habilitado(self) -> bool:
        if not self.filtro_estruturado_elegivel(self.tipo_dado):
            return False
        return bool(self.filtro_estruturado_config.get('habilitado'))

    @property
    def formula_config(self) -> dict[str, object]:
        configuracao = self.configuracao_json if isinstance(self.configuracao_json, dict) else {}
        formula = configuracao.get('formula', {})
        return formula if isinstance(formula, dict) else {}

    @property
    def formula_habilitada(self) -> bool:
        if self.tipo_dado != self.TipoDado.FORMULA_CONTROLADA or not self.calculada:
            return False
        return bool(self.formula_config.get('habilitada'))

    @classmethod
    def validar_configuracao_formula_guiada(
        cls,
        *,
        coluna: ColunaPersonalizada,
        configuracao_formula: object,
    ) -> dict[str, str]:
        errors: dict[str, str] = {}

        if not isinstance(configuracao_formula, dict):
            return {'formula': 'A formula guiada precisa ser salva como um objeto JSON valido.'}

        habilitada = configuracao_formula.get('habilitada')
        operacao = configuracao_formula.get('operacao')
        operandos = configuracao_formula.get('operandos')
        resultado_tipo = configuracao_formula.get('resultado_tipo')
        casas_decimais = configuracao_formula.get('casas_decimais')

        if habilitada is not True:
            errors['formula'] = 'A formula guiada desta etapa precisa ser salva como habilitada.'

        if operacao not in cls.operacoes_formula_guiada():
            errors['operacao'] = 'Selecione uma operacao guiada valida para a formula.'

        operandos_ids: list[int] = []
        if not isinstance(operandos, list):
            errors['operandos'] = 'Selecione ao menos duas colunas numericas como operandos da formula.'
        else:
            for valor in operandos:
                try:
                    operandos_ids.append(int(valor))
                except (TypeError, ValueError):
                    errors['operandos'] = 'Selecione apenas colunas validas como operandos da formula.'
                    break

        if 'operandos' not in errors:
            if len(operandos_ids) < 2:
                errors['operandos'] = 'A formula guiada exige pelo menos duas colunas de origem.'
            elif operacao in {cls.OperacaoFormula.SUBTRACAO, cls.OperacaoFormula.DIVISAO} and len(operandos_ids) != 2:
                errors['operandos'] = 'Subtracao e divisao exigem exatamente dois operandos nesta etapa.'

        if resultado_tipo not in cls.tipos_elegiveis_formula_resultado():
            errors['resultado_tipo'] = 'Selecione um tipo de resultado valido para a formula guiada.'

        if not isinstance(casas_decimais, int):
            errors['casas_decimais'] = 'Informe a quantidade de casas decimais da formula guiada.'
        else:
            limites = cls.limite_casas_decimais_formula(resultado_tipo)
            if limites is None:
                errors['casas_decimais'] = 'Nao foi possivel definir as casas decimais para o tipo de resultado informado.'
            else:
                minimo, maximo = limites
                if not minimo <= casas_decimais <= maximo:
                    if minimo == maximo:
                        errors['casas_decimais'] = f'Este tipo de resultado exige exatamente {minimo} casas decimais.'
                    else:
                        errors['casas_decimais'] = (
                            f'Este tipo de resultado aceita de {minimo} a {maximo} casas decimais.'
                        )

        tabela = coluna.tabela if getattr(coluna, 'tabela_id', None) else None
        if tabela is not None and 'operandos' not in errors:
            operandos_queryset = cls.objects.filter(
                tabela=tabela,
                pk__in=set(operandos_ids),
            )
            operandos_lookup = {
                operando.pk: operando
                for operando in operandos_queryset
            }

            for operando_id in operandos_ids:
                operando = operandos_lookup.get(operando_id)
                if operando is None:
                    errors['operandos'] = 'Selecione apenas colunas da mesma tabela como operandos da formula.'
                    break
                if coluna.pk and operando.pk == coluna.pk:
                    errors['operandos'] = 'A propria coluna calculada nao pode ser usada como operando da formula.'
                    break
                if operando.calculada or operando.tipo_dado == cls.TipoDado.FORMULA_CONTROLADA:
                    errors['operandos'] = 'Nao e permitido criar formula sobre outra coluna calculada nesta etapa.'
                    break
                if operando.status != cls.StatusColuna.ATIVA:
                    errors['operandos'] = 'Use apenas colunas ativas como origem da formula guiada.'
                    break
                if not operando.visivel:
                    errors['operandos'] = 'Use apenas colunas visiveis como origem da formula guiada.'
                    break
                if operando.tipo_dado not in cls.tipos_elegiveis_formula_fonte():
                    errors['operandos'] = (
                        'A formula guiada desta etapa aceita apenas colunas inteiras, decimais, monetarias ou percentuais.'
                    )
                    break

        return errors

    def clean(self) -> None:
        super().clean()
        errors: dict[str, str] = {}
        nome_normalizado = _normalizar_identificador_textual(self.nome)
        configuracao = self.configuracao_json or {}
        skip_formula_validation = getattr(self, '_skip_formula_json_validation', False)

        if not nome_normalizado:
            errors['nome'] = 'Informe o nome da coluna.'

        if self.calculada and self.tipo_dado != self.TipoDado.FORMULA_CONTROLADA:
            errors['tipo_dado'] = 'Coluna calculada deve usar o tipo formula_controlada.'

        if not self.calculada and self.tipo_dado == self.TipoDado.FORMULA_CONTROLADA:
            errors['calculada'] = 'Tipo formula_controlada exige coluna marcada como calculada.'

        if configuracao and not isinstance(configuracao, dict):
            errors['configuracao_json'] = 'A configuracao da coluna precisa ser um objeto JSON.'

        if isinstance(configuracao, dict) and self.tipo_dado == self.TipoDado.LISTA_OPCOES:
            opcoes = configuracao.get('opcoes', [])
            if not isinstance(opcoes, list):
                errors['configuracao_json'] = 'Lista de opcoes exige um array em configuracao_json.opcoes.'
            else:
                opcoes_normalizadas: set[str] = set()
                for opcao in opcoes:
                    if not isinstance(opcao, str) or not opcao.strip():
                        errors['configuracao_json'] = 'Lista de opcoes aceita apenas itens textuais nao vazios.'
                        break
                    opcao_normalizada = _normalizar_identificador_textual(opcao)
                    if opcao_normalizada in opcoes_normalizadas:
                        errors['configuracao_json'] = 'Lista de opcoes nao pode repetir valores equivalentes.'
                        break
                    opcoes_normalizadas.add(opcao_normalizada)
                if len(opcoes) > 20:
                    errors['configuracao_json'] = 'Lista de opcoes aceita no maximo 20 itens no MVP.'

        if isinstance(configuracao, dict) and 'filtro' in configuracao:
            filtro = configuracao.get('filtro')
            if not isinstance(filtro, dict):
                errors['configuracao_json'] = 'A configuracao de filtro da coluna precisa ser um objeto JSON.'
            else:
                habilitado = filtro.get('habilitado', False)
                operadores = filtro.get('operadores', [])
                operadores_esperados = list(self.operadores_filtro_por_tipo_dado(self.tipo_dado))

                if not isinstance(habilitado, bool):
                    errors['configuracao_json'] = 'A configuracao de filtro da coluna exige habilitado como booleano.'
                elif habilitado and not self.filtro_estruturado_elegivel(self.tipo_dado):
                    errors['configuracao_json'] = (
                        'Filtro estruturado so pode ser habilitado para data, mes/competencia e tipos numericos nesta etapa.'
                    )

                if not isinstance(operadores, list) or any(not isinstance(valor, str) for valor in operadores):
                    errors['configuracao_json'] = 'A configuracao de filtro da coluna exige operadores em uma lista textual.'
                elif habilitado and operadores != operadores_esperados:
                    errors['configuracao_json'] = 'Os operadores do filtro estruturado devem ser derivados do tipo da coluna.'

        if not skip_formula_validation:
            if isinstance(configuracao, dict) and 'formula' in configuracao:
                if self.tipo_dado != self.TipoDado.FORMULA_CONTROLADA or not self.calculada:
                    errors['configuracao_json'] = (
                        'A configuracao de formula guiada so pode existir em colunas marcadas como formula_controlada.'
                    )
                else:
                    formula_errors = self.validar_configuracao_formula_guiada(
                        coluna=self,
                        configuracao_formula=configuracao.get('formula'),
                    )
                    if formula_errors:
                        errors['configuracao_json'] = ' '.join(formula_errors.values())
            elif self.tipo_dado == self.TipoDado.FORMULA_CONTROLADA:
                errors['configuracao_json'] = 'Coluna formula_controlada exige configuracao_json.formula valida nesta etapa.'

        if self.tabela_id and nome_normalizado and self.status != self.StatusColuna.ARQUIVADA:
            queryset = type(self).objects.filter(tabela=self.tabela).exclude(status=self.StatusColuna.ARQUIVADA)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            for coluna in queryset.only('nome'):
                if _normalizar_identificador_textual(coluna.nome) == nome_normalizado:
                    errors['nome'] = 'Ja existe outra coluna ativa/inativa com este nome nesta tabela.'
                    break

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class TotalizadorColunaPersonalizada(models.Model):
    class TipoTotalizador(models.TextChoices):
        SOMA = 'soma', 'Soma'
        MEDIA = 'media', 'Media'
        MINIMO = 'minimo', 'Minimo'
        MAXIMO = 'maximo', 'Maximo'
        CONTAGEM = 'contagem', 'Contagem'

    coluna = models.ForeignKey(
        ColunaPersonalizada,
        on_delete=models.CASCADE,
        related_name='totalizadores',
    )
    tipo_totalizador = models.CharField(max_length=20, choices=TipoTotalizador.choices)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['coluna_id', 'tipo_totalizador', 'pk']
        verbose_name = 'Totalizador de coluna personalizada'
        verbose_name_plural = 'Totalizadores de colunas personalizadas'
        constraints = [
            models.UniqueConstraint(
                fields=('coluna', 'tipo_totalizador'),
                name='uniq_totalizador_coluna_personalizada_coluna_tipo',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.coluna.nome} - {self.get_tipo_totalizador_display()}'

    @classmethod
    def tipos_compativeis_por_tipo_dado(cls, tipo_dado: str | None) -> tuple[str, ...]:
        numericos = (
            cls.TipoTotalizador.SOMA,
            cls.TipoTotalizador.MEDIA,
            cls.TipoTotalizador.MINIMO,
            cls.TipoTotalizador.MAXIMO,
            cls.TipoTotalizador.CONTAGEM,
        )
        if tipo_dado in {
            ColunaPersonalizada.TipoDado.INTEIRO,
            ColunaPersonalizada.TipoDado.DECIMAL,
            ColunaPersonalizada.TipoDado.MONETARIO,
            ColunaPersonalizada.TipoDado.PERCENTUAL,
        }:
            return numericos
        if tipo_dado == ColunaPersonalizada.TipoDado.DATA:
            return (
                cls.TipoTotalizador.MINIMO,
                cls.TipoTotalizador.MAXIMO,
                cls.TipoTotalizador.CONTAGEM,
            )
        if tipo_dado in {
            ColunaPersonalizada.TipoDado.BOOLEANO,
            ColunaPersonalizada.TipoDado.LISTA_OPCOES,
            ColunaPersonalizada.TipoDado.TEXTO_CURTO,
            ColunaPersonalizada.TipoDado.TEXTO_LONGO,
            ColunaPersonalizada.TipoDado.MES_COMPETENCIA,
        }:
            return (cls.TipoTotalizador.CONTAGEM,)
        return ()

    @classmethod
    def tipos_dado_compativeis_por_totalizador(cls, tipo_totalizador: str) -> tuple[str, ...]:
        return tuple(
            tipo_dado
            for tipo_dado, _rotulo in ColunaPersonalizada.TipoDado.choices
            if tipo_totalizador in cls.tipos_compativeis_por_tipo_dado(tipo_dado)
        )

    def clean(self) -> None:
        super().clean()
        errors: dict[str, str] = {}

        if self.coluna_id:
            if self.coluna.calculada or self.coluna.tipo_dado == ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA:
                errors['coluna'] = 'Coluna calculada nao aceita totalizador nesta etapa.'
            elif self.tipo_totalizador not in self.tipos_compativeis_por_tipo_dado(self.coluna.tipo_dado):
                errors['tipo_totalizador'] = 'O totalizador informado nao e compativel com o tipo de dado da coluna.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class LinhaTabelaPersonalizada(models.Model):
    class StatusLinha(models.TextChoices):
        ATIVA = 'ativa', 'Ativa'
        ARQUIVADA = 'arquivada', 'Arquivada'

    tabela = models.ForeignKey(
        TabelaPersonalizada,
        on_delete=models.CASCADE,
        related_name='linhas',
    )
    status = models.CharField(
        max_length=20,
        choices=StatusLinha.choices,
        default=StatusLinha.ATIVA,
    )
    ordem = models.PositiveIntegerField(default=0)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='linhas_tabelas_personalizadas_criadas',
        null=True,
        blank=True,
    )
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='linhas_tabelas_personalizadas_atualizadas',
        null=True,
        blank=True,
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['tabela_id', 'ordem', 'pk']
        verbose_name = 'Linha de tabela personalizada'
        verbose_name_plural = 'Linhas de tabela personalizada'

    def __str__(self) -> str:
        referencia = self.pk if self.pk else 'nova'
        return f'{self.tabela.nome} - linha {referencia}'

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class ValorTabelaPersonalizada(models.Model):
    linha = models.ForeignKey(
        LinhaTabelaPersonalizada,
        on_delete=models.CASCADE,
        related_name='valores',
    )
    coluna = models.ForeignKey(
        ColunaPersonalizada,
        on_delete=models.CASCADE,
        related_name='valores',
    )
    valor_texto = models.TextField(blank=True)
    valor_numero = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
    )
    valor_data = models.DateField(null=True, blank=True)
    valor_booleano = models.BooleanField(null=True, blank=True)
    valor_json = models.JSONField(null=True, blank=True)
    valor_calculado = models.JSONField(null=True, blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['linha_id', 'coluna_id', 'pk']
        verbose_name = 'Valor de tabela personalizada'
        verbose_name_plural = 'Valores de tabela personalizada'
        constraints = [
            models.UniqueConstraint(
                fields=('linha', 'coluna'),
                name='uniq_valor_tabela_personalizada_linha_coluna',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.linha} - {self.coluna.nome}'

    def clean(self) -> None:
        super().clean()
        errors: dict[str, str] = {}

        if self.linha_id and self.coluna_id and self.linha.tabela_id != self.coluna.tabela_id:
            errors['coluna'] = 'A coluna precisa pertencer a mesma tabela da linha informada.'

        possui_valor_texto = bool((self.valor_texto or '').strip())
        possui_valor_numero = self.valor_numero is not None
        possui_valor_data = self.valor_data is not None
        possui_valor_booleano = self.valor_booleano is not None
        possui_valor_json = self.valor_json is not None
        possui_valor_calculado = self.valor_calculado is not None

        slots_manuais_preenchidos = sum(
            (
                possui_valor_texto,
                possui_valor_numero,
                possui_valor_data,
                possui_valor_booleano,
                possui_valor_json,
            )
        )

        if self.coluna_id:
            if self.coluna.calculada:
                if slots_manuais_preenchidos:
                    errors['coluna'] = 'Coluna calculada nao aceita valor manual nesta etapa.'
                if self.coluna.tipo_dado != ColunaPersonalizada.TipoDado.FORMULA_CONTROLADA:
                    errors['coluna'] = 'Coluna calculada precisa usar o tipo formula_controlada.'
            else:
                if possui_valor_calculado:
                    errors['valor_calculado'] = 'Valor calculado so pode ser usado em coluna calculada.'

                tipo_dado = self.coluna.tipo_dado
                if tipo_dado in {
                    ColunaPersonalizada.TipoDado.TEXTO_CURTO,
                    ColunaPersonalizada.TipoDado.TEXTO_LONGO,
                }:
                    if not possui_valor_texto:
                        errors['valor_texto'] = 'Este tipo de coluna exige valor_texto.'
                    elif slots_manuais_preenchidos > 1:
                        errors['coluna'] = 'Preencha apenas o slot de valor compativel com a coluna.'
                    elif (
                        tipo_dado == ColunaPersonalizada.TipoDado.TEXTO_CURTO
                        and len((self.valor_texto or '').strip()) > 120
                    ):
                        errors['valor_texto'] = 'Texto curto aceita no maximo 120 caracteres.'
                elif tipo_dado == ColunaPersonalizada.TipoDado.MES_COMPETENCIA:
                    if not possui_valor_texto:
                        errors['valor_texto'] = 'Mes/competencia exige valor_texto no formato MM/AAAA.'
                    elif slots_manuais_preenchidos > 1:
                        errors['coluna'] = 'Preencha apenas o slot de valor compativel com a coluna.'
                    elif not re.match(r'^(0[1-9]|1[0-2])/\d{4}$', (self.valor_texto or '').strip()):
                        errors['valor_texto'] = 'Mes/competencia deve seguir o formato MM/AAAA.'
                elif tipo_dado in {
                    ColunaPersonalizada.TipoDado.INTEIRO,
                    ColunaPersonalizada.TipoDado.DECIMAL,
                    ColunaPersonalizada.TipoDado.MONETARIO,
                    ColunaPersonalizada.TipoDado.PERCENTUAL,
                }:
                    if not possui_valor_numero:
                        errors['valor_numero'] = 'Este tipo de coluna exige valor_numero.'
                    elif slots_manuais_preenchidos > 1:
                        errors['coluna'] = 'Preencha apenas o slot de valor compativel com a coluna.'
                    elif (
                        tipo_dado == ColunaPersonalizada.TipoDado.INTEIRO
                        and self.valor_numero != self.valor_numero.to_integral_value()
                    ):
                        errors['valor_numero'] = 'Coluna do tipo inteiro nao aceita casas decimais.'
                    else:
                        casas_decimais = _contar_casas_decimais(self.valor_numero)
                        if (
                            tipo_dado == ColunaPersonalizada.TipoDado.DECIMAL
                            and casas_decimais > 8
                        ):
                            errors['valor_numero'] = 'Este campo aceita ate 8 casas decimais.'
                        elif (
                            tipo_dado == ColunaPersonalizada.TipoDado.MONETARIO
                            and casas_decimais > 2
                        ):
                            errors['valor_numero'] = 'Este campo aceita ate 2 casas decimais.'
                        elif (
                            tipo_dado == ColunaPersonalizada.TipoDado.PERCENTUAL
                            and casas_decimais > 4
                        ):
                            errors['valor_numero'] = 'Este campo aceita ate 4 casas decimais.'
                elif tipo_dado == ColunaPersonalizada.TipoDado.DATA:
                    if not possui_valor_data:
                        errors['valor_data'] = 'Coluna do tipo data exige valor_data.'
                    elif slots_manuais_preenchidos > 1:
                        errors['coluna'] = 'Preencha apenas o slot de valor compativel com a coluna.'
                elif tipo_dado == ColunaPersonalizada.TipoDado.BOOLEANO:
                    if not possui_valor_booleano:
                        errors['valor_booleano'] = 'Coluna do tipo booleano exige valor_booleano.'
                    elif slots_manuais_preenchidos > 1:
                        errors['coluna'] = 'Preencha apenas o slot de valor compativel com a coluna.'
                elif tipo_dado == ColunaPersonalizada.TipoDado.LISTA_OPCOES:
                    if not possui_valor_texto:
                        errors['valor_texto'] = 'Lista de opcoes exige valor_texto.'
                    elif slots_manuais_preenchidos > 1:
                        errors['coluna'] = 'Preencha apenas o slot de valor compativel com a coluna.'
                    else:
                        configuracao = self.coluna.configuracao_json or {}
                        opcoes = configuracao.get('opcoes', []) if isinstance(configuracao, dict) else []
                        if opcoes and self.valor_texto not in opcoes:
                            errors['valor_texto'] = 'O valor informado nao esta entre as opcoes permitidas.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
