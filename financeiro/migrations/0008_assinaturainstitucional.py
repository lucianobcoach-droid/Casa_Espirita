from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('financeiro', '0007_categoriafinanceira_mensagem_recibo'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssinaturaInstitucional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=150)),
                ('assinatura_texto', models.CharField(max_length=150)),
                ('nome_exibicao', models.CharField(blank=True, max_length=150)),
                ('cargo', models.CharField(blank=True, max_length=150)),
                ('ativo', models.BooleanField(default=True)),
                ('padrao', models.BooleanField(default=False)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Assinatura institucional',
                'verbose_name_plural': 'Assinaturas institucionais',
                'ordering': ['-padrao', 'nome'],
            },
        ),
    ]
