# Generated manually because Django is unavailable in the local environment
from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CategoriaFinanceira',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=150)),
                ('tipo', models.CharField(choices=[('receita', 'Receita'), ('despesa', 'Despesa')], max_length=20)),
                ('ativo', models.BooleanField(default=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                (
                    'categoria_pai',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='subcategorias',
                        to='financeiro.categoriafinanceira',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Categoria financeira',
                'verbose_name_plural': 'Categorias financeiras',
                'ordering': ['tipo', 'nome'],
            },
        ),
        migrations.CreateModel(
            name='CentroCusto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=30, unique=True)),
                ('nome', models.CharField(max_length=150)),
                ('ativo', models.BooleanField(default=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Centro de custo',
                'verbose_name_plural': 'Centros de custo',
                'ordering': ['codigo', 'nome'],
            },
        ),
        migrations.CreateModel(
            name='ContaFinanceira',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=150)),
                ('descricao', models.TextField(blank=True)),
                ('ativa', models.BooleanField(default=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Conta financeira',
                'verbose_name_plural': 'Contas financeiras',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='PessoaFinanceira',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=30, unique=True)),
                ('nome', models.CharField(max_length=150)),
                ('tipo_pessoa', models.CharField(blank=True, choices=[('fisica', 'Fisica'), ('juridica', 'Juridica')], max_length=20)),
                ('documento', models.CharField(blank=True, max_length=30)),
                ('telefone', models.CharField(blank=True, max_length=30)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('observacoes', models.TextField(blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Pessoa financeira',
                'verbose_name_plural': 'Pessoas financeiras',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='LancamentoFinanceiro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(max_length=255)),
                ('tipo', models.CharField(choices=[('receita', 'Receita'), ('despesa', 'Despesa'), ('transferencia', 'Transferencia')], max_length=20)),
                ('status', models.CharField(choices=[('aberto', 'Aberto'), ('quitado', 'Quitado'), ('cancelado', 'Cancelado')], default='aberto', max_length=20)),
                ('valor', models.DecimalField(decimal_places=2, default='0.00', max_digits=12)),
                ('data_competencia', models.DateField()),
                ('data_pagamento', models.DateField(blank=True, null=True)),
                ('numero_documento', models.CharField(blank=True, max_length=50)),
                ('observacoes', models.TextField(blank=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                (
                    'categoria',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='lancamentos',
                        to='financeiro.categoriafinanceira',
                    ),
                ),
                (
                    'centro_custo',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='lancamentos',
                        to='financeiro.centrocusto',
                    ),
                ),
                (
                    'conta',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='lancamentos_origem',
                        to='financeiro.contafinanceira',
                    ),
                ),
                (
                    'conta_destino',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='lancamentos_destino',
                        to='financeiro.contafinanceira',
                    ),
                ),
                (
                    'pessoa',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='lancamentos',
                        to='financeiro.pessoafinanceira',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Lançamento financeiro',
                'verbose_name_plural': 'Lançamentos financeiros',
                'ordering': ['-data_competencia', '-criado_em'],
            },
        ),
    ]
