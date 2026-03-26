from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('financeiro', '0008_assinaturainstitucional'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfiguracaoInstitucional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_instituicao', models.CharField(blank=True, max_length=200)),
                ('cidade', models.CharField(blank=True, max_length=120)),
                ('logo_url', models.URLField(blank=True)),
                ('mensagem_padrao_recibo', models.TextField(blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('padrao', models.BooleanField(default=False)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Configuracao institucional',
                'verbose_name_plural': 'Configuracoes institucionais',
                'ordering': ['-padrao', '-ativo', 'nome_instituicao'],
            },
        ),
    ]
