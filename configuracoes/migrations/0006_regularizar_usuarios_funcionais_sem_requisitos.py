from __future__ import annotations

from django.conf import settings
from django.db import migrations
from django.db.models import Q


def regularizar_usuarios_funcionais(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    UsuarioPerfilAcesso = apps.get_model('configuracoes', 'UsuarioPerfilAcesso')

    usuarios_com_perfil = UsuarioPerfilAcesso.objects.values_list('usuario_id', flat=True)

    (
        User.objects.filter(is_active=True, is_staff=False, is_superuser=False)
        .filter(Q(email__isnull=True) | Q(email='') | ~Q(pk__in=usuarios_com_perfil))
        .update(is_active=False)
    )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('configuracoes', '0005_alinhar_siteconfig_operador_financeiro'),
    ]

    operations = [
        migrations.RunPython(
            regularizar_usuarios_funcionais,
            migrations.RunPython.noop,
        ),
    ]
