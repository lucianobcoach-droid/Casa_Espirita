# Generated manually due to offline environment
from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Autor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('biografia', models.TextField(blank=True)),
            ],
            options={'ordering': ['nome']},
        ),
        migrations.CreateModel(
            name='Livro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255)),
                ('descricao', models.TextField(blank=True)),
                ('estoque_total', models.PositiveIntegerField()),
                ('estoque_disponivel', models.PositiveIntegerField(blank=True, null=True)),
                ('preco', models.DecimalField(decimal_places=2, max_digits=8)),
                ('autores', models.ManyToManyField(related_name='livros', to='biblioteca.autor')),
            ],
            options={'ordering': ['titulo']},
        ),
        migrations.CreateModel(
            name='Emprestimo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leitor', models.CharField(max_length=255)),
                ('quantidade', models.PositiveIntegerField(default=1)),
                ('data_emprestimo', models.DateField(default=django.utils.timezone.now)),
                ('data_prevista_devolucao', models.DateField()),
                ('data_devolucao', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('atrasado', 'Atrasado'), ('devolvido', 'Devolvido')], default='pendente', max_length=20)),
                ('observacoes', models.TextField(blank=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('livro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='emprestimos', to='biblioteca.livro')),
            ],
            options={'ordering': ['-data_emprestimo', 'leitor']},
        ),
        migrations.CreateModel(
            name='Venda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField()),
                ('valor_unitario', models.DecimalField(decimal_places=2, max_digits=8)),
                ('comprador', models.CharField(blank=True, max_length=255)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('livro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='vendas', to='biblioteca.livro')),
            ],
            options={'ordering': ['-criado_em']},
        ),
    ]
