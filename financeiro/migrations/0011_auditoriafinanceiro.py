from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('financeiro', '0010_lancamentofinanceiro_rateio_campos'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditoriaFinanceiro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acao', models.CharField(choices=[('create', 'Criacao'), ('update', 'Atualizacao'), ('delete', 'Exclusao')], max_length=20)),
                ('modelo', models.CharField(max_length=100)),
                ('registro_id', models.PositiveBigIntegerField()),
                ('data_hora', models.DateTimeField(auto_now_add=True)),
                ('campos_alterados', models.JSONField(blank=True, default=dict)),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='auditorias_financeiro', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Auditoria do financeiro',
                'verbose_name_plural': 'Auditorias do financeiro',
                'ordering': ['-data_hora', '-pk'],
            },
        ),
    ]
