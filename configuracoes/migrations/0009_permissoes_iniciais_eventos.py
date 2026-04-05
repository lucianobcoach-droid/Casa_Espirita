from __future__ import annotations

from django.db import migrations


NOVAS_PERMISSOES = [
    ('eventos', 'eventos', 'visualizar', 'Visualizar landing do modulo de eventos'),
    ('eventos', 'eventos', 'listar', 'Listar eventos'),
    ('eventos', 'eventos', 'criar', 'Criar eventos'),
]


def _codigo(modulo: str, recurso: str, acao: str) -> str:
    return f'{modulo}.{recurso}.{acao}'


def adicionar_permissoes_eventos(apps, schema_editor):
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

    codigos_por_perfil = {
        'administrador-geral': tuple(permissoes.keys()),
        'gestao-administrativa': tuple(permissoes.keys()),
        'consulta-visualizacao': (
            'eventos.eventos.visualizar',
            'eventos.eventos.listar',
        ),
    }

    for codigo_perfil, codigos_permissoes in codigos_por_perfil.items():
        perfil = PerfilAcesso.objects.filter(codigo=codigo_perfil).first()
        if perfil is None:
            continue
        for codigo_permissao in codigos_permissoes:
            permissao = permissoes.get(codigo_permissao)
            if permissao is None:
                continue
            PerfilPermissaoSistema.objects.get_or_create(
                perfil=perfil,
                permissao=permissao,
            )


def remover_permissoes_eventos(apps, schema_editor):
    PermissaoSistema = apps.get_model('configuracoes', 'PermissaoSistema')
    codigos = [_codigo(modulo, recurso, acao) for modulo, recurso, acao, _nome in NOVAS_PERMISSOES]
    PermissaoSistema.objects.filter(codigo__in=codigos).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('configuracoes', '0008_regularizar_nome_institucional_siteconfig'),
    ]

    operations = [
        migrations.RunPython(adicionar_permissoes_eventos, remover_permissoes_eventos),
    ]
