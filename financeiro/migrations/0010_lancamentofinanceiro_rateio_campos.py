from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0009_configuracaoinstitucional'),
    ]

    operations = [
        migrations.AddField(
            model_name='lancamentofinanceiro',
            name='com_rateio',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='lancamentofinanceiro',
            name='grupo_rateio',
            field=models.CharField(blank=True, db_index=True, max_length=36),
        ),
    ]
