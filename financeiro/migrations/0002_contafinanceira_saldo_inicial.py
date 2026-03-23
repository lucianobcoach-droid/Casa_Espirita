# Generated manually because Django is unavailable in the local environment
from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contafinanceira',
            name='data_saldo_inicial',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contafinanceira',
            name='saldo_inicial',
            field=models.DecimalField(decimal_places=2, default='0.00', max_digits=12),
        ),
    ]
