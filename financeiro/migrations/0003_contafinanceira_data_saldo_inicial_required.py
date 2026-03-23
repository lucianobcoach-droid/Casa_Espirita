# Generated manually because Django is unavailable in the local environment
from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0002_contafinanceira_saldo_inicial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contafinanceira',
            name='data_saldo_inicial',
            field=models.DateField(),
        ),
    ]
