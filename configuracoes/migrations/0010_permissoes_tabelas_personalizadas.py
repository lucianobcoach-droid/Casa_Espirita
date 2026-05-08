from __future__ import annotations

from django.db import migrations


NOVAS_PERMISSOES = [
    ('financeiro', 'tabelas_personalizadas', 'visualizar', 'Visualizar tabelas personalizadas'),
    ('financeiro', 'tabelas_personalizadas', 'criar', 'Criar tabelas personalizadas'),
    ('financeiro', 'tabelas_personalizadas', 'editar_estrutura', 'Editar estrutura de tabelas personalizadas'),
    ('financeiro', 'tabelas_personalizadas', 'configurar_formula', 'Configurar formulas de tabelas personalizadas'),
    ('financeiro', 'tabelas_personalizadas', 'preencher_linhas', 'Preencher linhas de tabelas personalizadas'),
    ('financeiro', 'tabelas_personalizadas', 'editar_linhas', 'Editar linhas de tabelas personalizadas'),
    ('financeiro', 'tabelas_personalizadas', 'exportar', 'Exportar tabelas personalizadas'),
    ('financeiro', 'tabelas_personalizadas', 'arquivar_restaurar', 'Arquivar ou restaurar tabelas personalizadas'),
    ('financeiro', 'tabelas_personalizadas', 'administrar_configuracoes', 'Administrar configuracoes de tabelas personalizadas'),
]


def _codigo(modulo: str, recurso: str, acao: str) -> str:
    return f'{modulo}.{recurso}.{acao}'


def adicionar_permissoes_tabelas_personalizadas(apps, schema_editor):
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
        'operador-financeiro': (
            'financeiro.tabelas_personalizadas.visualizar',
            'financeiro.tabelas_personalizadas.criar',
            'financeiro.tabelas_personalizadas.editar_estrutura',
            'financeiro.tabelas_personalizadas.preencher_linhas',
            'financeiro.tabelas_personalizadas.editar_linhas',
            'financeiro.tabelas_personalizadas.exportar',
        ),
        'consulta-visualizacao': (
            'financeiro.tabelas_personalizadas.visualizar',
            'financeiro.tabelas_personalizadas.exportar',
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


def remover_permissoes_tabelas_personalizadas(apps, schema_editor):
    PermissaoSistema = apps.get_model('configuracoes', 'PermissaoSistema')
    codigos = [_codigo(modulo, recurso, acao) for modulo, recurso, acao, _nome in NOVAS_PERMISSOES]
    PermissaoSistema.objects.filter(codigo__in=codigos).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('configuracoes', '0009_permissoes_iniciais_eventos'),
    ]

    operations = [
        migrations.RunPython(
            adicionar_permissoes_tabelas_personalizadas,
            remover_permissoes_tabelas_personalizadas,
        ),
    ]
