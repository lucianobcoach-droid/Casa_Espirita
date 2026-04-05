from __future__ import annotations

from django.db import migrations


def alinhar_siteconfig_operador_financeiro(apps, schema_editor):
    PerfilAcesso = apps.get_model('configuracoes', 'PerfilAcesso')
    PermissaoSistema = apps.get_model('configuracoes', 'PermissaoSistema')
    PerfilPermissaoSistema = apps.get_model('configuracoes', 'PerfilPermissaoSistema')

    perfil = PerfilAcesso.objects.filter(codigo='operador-financeiro').first()
    permissao = PermissaoSistema.objects.filter(codigo='configuracoes.siteconfig.visualizar').first()

    if perfil is None or permissao is None:
        return

    PerfilPermissaoSistema.objects.get_or_create(
        perfil=perfil,
        permissao=permissao,
    )


def reverter_alinhamento_siteconfig_operador_financeiro(apps, schema_editor):
    PerfilAcesso = apps.get_model('configuracoes', 'PerfilAcesso')
    PermissaoSistema = apps.get_model('configuracoes', 'PermissaoSistema')
    PerfilPermissaoSistema = apps.get_model('configuracoes', 'PerfilPermissaoSistema')

    perfil = PerfilAcesso.objects.filter(codigo='operador-financeiro').first()
    permissao = PermissaoSistema.objects.filter(codigo='configuracoes.siteconfig.visualizar').first()

    if perfil is None or permissao is None:
        return

    PerfilPermissaoSistema.objects.filter(
        perfil=perfil,
        permissao=permissao,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('configuracoes', '0004_seed_perfis_permissoes_v1'),
    ]

    operations = [
        migrations.RunPython(
            alinhar_siteconfig_operador_financeiro,
            reverter_alinhamento_siteconfig_operador_financeiro,
        ),
    ]
