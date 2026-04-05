from __future__ import annotations

from django.db import migrations


NOVAS_PERMISSOES = [
    ('configuracoes', 'perfis_acesso', 'listar', 'Listar perfis de acesso'),
    ('configuracoes', 'perfis_acesso', 'visualizar', 'Visualizar detalhe de perfil de acesso'),
    ('configuracoes', 'usuarios_acesso', 'listar', 'Listar usuarios e perfis funcionais'),
    ('configuracoes', 'usuarios_acesso', 'editar_perfil', 'Editar vinculo usuario -> perfil base'),
]


def _codigo(modulo: str, recurso: str, acao: str) -> str:
    return f'{modulo}.{recurso}.{acao}'


def adicionar_permissoes_ui_acesso(apps, schema_editor):
    PerfilAcesso = apps.get_model('configuracoes', 'PerfilAcesso')
    PermissaoSistema = apps.get_model('configuracoes', 'PermissaoSistema')
    PerfilPermissaoSistema = apps.get_model('configuracoes', 'PerfilPermissaoSistema')

    permissoes = {}
    for modulo, recurso, acao, nome in NOVAS_PERMISSOES:
        codigo = _codigo(modulo, recurso, acao)
        permissao, _ = PermissaoSistema.objects.update_or_create(
            codigo=codigo,
            defaults={
                'nome': nome,
                'modulo': modulo,
                'recurso': recurso,
                'acao': acao,
                'descricao': nome,
                'ativo': True,
            },
        )
        permissoes[codigo] = permissao

    for codigo_perfil in ('administrador-geral', 'gestao-administrativa'):
        perfil = PerfilAcesso.objects.filter(codigo=codigo_perfil).first()
        if perfil is None:
            continue
        for permissao in permissoes.values():
            PerfilPermissaoSistema.objects.get_or_create(
                perfil=perfil,
                permissao=permissao,
            )


def remover_permissoes_ui_acesso(apps, schema_editor):
    PermissaoSistema = apps.get_model('configuracoes', 'PermissaoSistema')
    codigos = [_codigo(modulo, recurso, acao) for modulo, recurso, acao, _nome in NOVAS_PERMISSOES]
    PermissaoSistema.objects.filter(codigo__in=codigos).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('configuracoes', '0006_regularizar_usuarios_funcionais_sem_requisitos'),
    ]

    operations = [
        migrations.RunPython(adicionar_permissoes_ui_acesso, remover_permissoes_ui_acesso),
    ]
