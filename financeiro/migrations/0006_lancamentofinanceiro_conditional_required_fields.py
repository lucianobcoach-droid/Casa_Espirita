from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('financeiro', '0005_lancamentofinanceiro_pessoa_required'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lancamentofinanceiro',
            name='categoria',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.PROTECT,
                related_name='lancamentos',
                to='financeiro.categoriafinanceira',
            ),
        ),
        migrations.AlterField(
            model_name='lancamentofinanceiro',
            name='pessoa',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.PROTECT,
                related_name='lancamentos',
                to='financeiro.pessoafinanceira',
            ),
        ),
    ]
