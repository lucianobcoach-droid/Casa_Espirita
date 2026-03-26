from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('financeiro', '0004_lancamentofinanceiro_categoria_required'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lancamentofinanceiro',
            name='pessoa',
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name='lancamentos',
                to='financeiro.pessoafinanceira',
            ),
        ),
    ]
