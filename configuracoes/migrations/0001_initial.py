from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SiteConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(default='Casa Espírita', max_length=150, verbose_name='Nome do site')),
                ('slogan', models.CharField(blank=True, max_length=255, verbose_name='Slogan')),
                ('descricao', models.TextField(blank=True, verbose_name='Descrição')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='configuracoes/logo/', verbose_name='Logo')),
                (
                    'usar_layout_leve',
                    models.BooleanField(
                        default=False,
                        help_text='Ativa o novo layout leve do Django admin.',
                        verbose_name='Usar layout leve',
                    ),
                ),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': 'Configuração do site',
                'verbose_name_plural': 'Configurações do site',
            },
        ),
    ]
