from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('financeiro', '0003_contafinanceira_data_saldo_inicial_required'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lancamentofinanceiro',
            name='categoria',
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name='lancamentos',
                to='financeiro.categoriafinanceira',
            ),
        ),
    ]
