from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('financeiro', '0006_lancamentofinanceiro_conditional_required_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoriafinanceira',
            name='mensagem_recibo',
            field=models.TextField(blank=True),
        ),
    ]
