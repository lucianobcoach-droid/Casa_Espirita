from __future__ import annotations

from django.db import migrations, models


NOME_PLACEHOLDER = 'Lar de Teste'
NOME_INSTITUCIONAL_OFICIAL = 'Casa Espírita Caminheiros da Luz'


def regularizar_nome_siteconfig(apps, schema_editor):
    SiteConfig = apps.get_model('configuracoes', 'SiteConfig')
    SiteConfig.objects.filter(site_name=NOME_PLACEHOLDER).update(
        site_name=NOME_INSTITUCIONAL_OFICIAL
    )


class Migration(migrations.Migration):

    dependencies = [
        ('configuracoes', '0007_permissoes_ui_funcional_acesso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteconfig',
            name='site_name',
            field=models.CharField(
                default=NOME_INSTITUCIONAL_OFICIAL,
                max_length=150,
                verbose_name='Nome do site',
            ),
        ),
        migrations.RunPython(
            regularizar_nome_siteconfig,
            migrations.RunPython.noop,
        ),
    ]
