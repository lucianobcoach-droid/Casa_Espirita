from __future__ import annotations

from django.db import migrations


PERFIS_BASE = {
    'administrador-geral': {
        'nome': 'Administrador geral',
        'descricao': 'Acesso funcional completo e administracao tecnica global.',
    },
    'gestao-administrativa': {
        'nome': 'Gestao administrativa',
        'descricao': 'Gestao funcional ampla dos modulos, sem administracao tecnica em /admin/.',
    },
    'operador-financeiro': {
        'nome': 'Operador financeiro',
        'descricao': 'Operacao diaria do financeiro, sem exclusoes sensiveis, auditoria ou configuracoes institucionais.',
    },
    'operador-biblioteca': {
        'nome': 'Operador biblioteca',
        'descricao': 'Operacao do modulo biblioteca e leitura institucional basica.',
    },
    'consulta-visualizacao': {
        'nome': 'Consulta/visualizacao',
        'descricao': 'Leitura, impressao e exportacao sem alteracao de dados.',
    },
}


PERMISSOES_BASE = [
    ('financeiro', 'lancamentos', 'listar', 'Listar lancamentos'),
    ('financeiro', 'lancamentos', 'visualizar', 'Visualizar lancamentos'),
    ('financeiro', 'lancamentos', 'criar', 'Criar lancamentos'),
    ('financeiro', 'lancamentos', 'editar', 'Editar lancamentos'),
    ('financeiro', 'lancamentos', 'excluir', 'Excluir lancamentos'),
    ('financeiro', 'lancamentos', 'clonar', 'Clonar lancamentos'),
    ('financeiro', 'lancamentos', 'editar_rateio', 'Editar rateio de lancamentos'),
    ('financeiro', 'lancamentos', 'emitir_recibo', 'Emitir recibo de lancamentos'),
    ('financeiro', 'lancamentos', 'importar', 'Importar lancamentos'),
    ('financeiro', 'lancamentos', 'exportar', 'Exportar lancamentos'),
    ('financeiro', 'lancamentos', 'baixar_modelo', 'Baixar planilha modelo de importacao'),
    ('financeiro', 'lancamentos', 'baixar_inconsistencias', 'Baixar relatorio de inconsistencias da importacao'),
    ('financeiro', 'lancamentos', 'acoes_em_lote_status', 'Alterar status de lancamentos em lote'),
    ('financeiro', 'lancamentos', 'acoes_em_lote_excluir', 'Excluir lancamentos em lote'),
    ('financeiro', 'lancamentos', 'acessar_endpoints_auxiliares', 'Acessar autocompletes, historico e sugestoes de lancamentos'),
    ('financeiro', 'extratos', 'visualizar', 'Visualizar extratos'),
    ('financeiro', 'extratos', 'imprimir', 'Imprimir extratos'),
    ('financeiro', 'resumo_financeiro', 'visualizar', 'Visualizar resumo financeiro'),
    ('financeiro', 'resumo_financeiro', 'imprimir', 'Imprimir resumo financeiro'),
    ('financeiro', 'prestacao_contas', 'visualizar', 'Visualizar prestacao de contas'),
    ('financeiro', 'prestacao_contas', 'imprimir', 'Imprimir prestacao de contas'),
    ('financeiro', 'auditoria', 'listar', 'Listar auditoria do financeiro'),
    ('financeiro', 'auditoria', 'visualizar', 'Visualizar auditoria do financeiro'),
    ('financeiro', 'contas', 'listar', 'Listar contas'),
    ('financeiro', 'contas', 'visualizar', 'Visualizar contas e extrato individual'),
    ('financeiro', 'contas', 'criar', 'Criar contas'),
    ('financeiro', 'contas', 'editar', 'Editar contas'),
    ('financeiro', 'contas', 'excluir', 'Excluir contas'),
    ('financeiro', 'contas', 'acessar_endpoints_auxiliares', 'Acessar autocomplete de contas'),
    ('financeiro', 'pessoas', 'listar', 'Listar pessoas'),
    ('financeiro', 'pessoas', 'visualizar', 'Visualizar pessoas'),
    ('financeiro', 'pessoas', 'criar', 'Criar pessoas'),
    ('financeiro', 'pessoas', 'editar', 'Editar pessoas'),
    ('financeiro', 'pessoas', 'excluir', 'Excluir pessoas'),
    ('financeiro', 'pessoas', 'acessar_endpoints_auxiliares', 'Acessar autocomplete de pessoas'),
    ('financeiro', 'categorias', 'listar', 'Listar categorias'),
    ('financeiro', 'categorias', 'visualizar', 'Visualizar categorias'),
    ('financeiro', 'categorias', 'criar', 'Criar categorias'),
    ('financeiro', 'categorias', 'editar', 'Editar categorias'),
    ('financeiro', 'categorias', 'excluir', 'Excluir categorias'),
    ('financeiro', 'categorias', 'acessar_endpoints_auxiliares', 'Acessar autocomplete de categorias'),
    ('financeiro', 'subcategorias', 'listar', 'Listar subcategorias'),
    ('financeiro', 'subcategorias', 'visualizar', 'Visualizar subcategorias'),
    ('financeiro', 'subcategorias', 'criar', 'Criar subcategorias'),
    ('financeiro', 'subcategorias', 'editar', 'Editar subcategorias'),
    ('financeiro', 'subcategorias', 'excluir', 'Excluir subcategorias'),
    ('financeiro', 'subcategorias', 'acessar_endpoints_auxiliares', 'Acessar autocomplete de subcategorias'),
    ('financeiro', 'centros_custo', 'listar', 'Listar centros de custo'),
    ('financeiro', 'centros_custo', 'visualizar', 'Visualizar centros de custo'),
    ('financeiro', 'centros_custo', 'criar', 'Criar centros de custo'),
    ('financeiro', 'centros_custo', 'editar', 'Editar centros de custo'),
    ('financeiro', 'centros_custo', 'excluir', 'Excluir centros de custo'),
    ('financeiro', 'centros_custo', 'acessar_endpoints_auxiliares', 'Acessar autocomplete de centros de custo'),
    ('financeiro', 'assinaturas', 'listar', 'Listar assinaturas institucionais'),
    ('financeiro', 'assinaturas', 'criar', 'Criar assinaturas institucionais'),
    ('financeiro', 'assinaturas', 'editar', 'Editar assinaturas institucionais'),
    ('financeiro', 'assinaturas', 'excluir', 'Excluir assinaturas institucionais'),
    ('financeiro', 'configuracoes_institucionais', 'visualizar', 'Visualizar configuracoes institucionais'),
    ('financeiro', 'configuracoes_institucionais', 'editar', 'Editar configuracoes institucionais'),
    ('biblioteca', 'autores', 'listar', 'Listar autores'),
    ('biblioteca', 'autores', 'criar', 'Criar autores'),
    ('biblioteca', 'livros', 'listar', 'Listar livros'),
    ('biblioteca', 'livros', 'criar', 'Criar livros'),
    ('biblioteca', 'vendas', 'listar', 'Listar vendas'),
    ('biblioteca', 'vendas', 'criar', 'Criar vendas'),
    ('biblioteca', 'emprestimos', 'listar', 'Listar emprestimos'),
    ('biblioteca', 'emprestimos', 'criar', 'Criar emprestimos'),
    ('configuracoes', 'siteconfig', 'visualizar', 'Visualizar configuracoes do site'),
    ('configuracoes', 'admin_global', 'acessar', 'Acessar administracao tecnica global /admin/'),
]


def _codigo_permissao(modulo: str, recurso: str, acao: str) -> str:
    return f'{modulo}.{recurso}.{acao}'


def _codigos_filtrados(permissoes: set[str], *, modulo: str | None = None, acoes: set[str] | None = None) -> set[str]:
    return {
        codigo
        for codigo in permissoes
        if (modulo is None or codigo.startswith(f'{modulo}.'))
        and (acoes is None or codigo.rsplit('.', 1)[-1] in acoes)
    }


def _codigos_operador_financeiro(todos_codigos: set[str]) -> set[str]:
    permitidos = _codigos_filtrados(todos_codigos, modulo='financeiro')
    negados = {
        'financeiro.lancamentos.excluir',
        'financeiro.lancamentos.acoes_em_lote_excluir',
        'financeiro.auditoria.listar',
        'financeiro.auditoria.visualizar',
        'financeiro.contas.excluir',
        'financeiro.pessoas.excluir',
        'financeiro.categorias.excluir',
        'financeiro.subcategorias.excluir',
        'financeiro.centros_custo.excluir',
        'financeiro.assinaturas.listar',
        'financeiro.assinaturas.criar',
        'financeiro.assinaturas.editar',
        'financeiro.assinaturas.excluir',
        'financeiro.configuracoes_institucionais.visualizar',
        'financeiro.configuracoes_institucionais.editar',
    }
    return permitidos - negados


def _codigos_consulta_visualizacao(todos_codigos: set[str]) -> set[str]:
    acoes_leitura = {'listar', 'visualizar', 'imprimir', 'exportar'}
    permitidos = _codigos_filtrados(todos_codigos, modulo='financeiro', acoes=acoes_leitura)
    permitidos |= _codigos_filtrados(todos_codigos, modulo='biblioteca', acoes={'listar'})
    permitidos.add('configuracoes.siteconfig.visualizar')
    return permitidos


def _sincronizar_perfis_permissoes(apps, schema_editor):
    PerfilAcesso = apps.get_model('configuracoes', 'PerfilAcesso')
    PermissaoSistema = apps.get_model('configuracoes', 'PermissaoSistema')
    PerfilPermissaoSistema = apps.get_model('configuracoes', 'PerfilPermissaoSistema')

    permissoes_por_codigo = {}
    for modulo, recurso, acao, nome in PERMISSOES_BASE:
        codigo = _codigo_permissao(modulo, recurso, acao)
        permissao, _criado = PermissaoSistema.objects.update_or_create(
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
        permissoes_por_codigo[codigo] = permissao

    perfis_por_codigo = {}
    for codigo, dados in PERFIS_BASE.items():
        perfil, _criado = PerfilAcesso.objects.update_or_create(
            codigo=codigo,
            defaults={
                'nome': dados['nome'],
                'descricao': dados['descricao'],
                'ativo': True,
            },
        )
        perfis_por_codigo[codigo] = perfil

    todos_codigos = set(permissoes_por_codigo.keys())
    codigos_por_perfil = {
        'administrador-geral': todos_codigos,
        'gestao-administrativa': todos_codigos - {'configuracoes.admin_global.acessar'},
        'operador-financeiro': _codigos_operador_financeiro(todos_codigos),
        'operador-biblioteca': _codigos_filtrados(todos_codigos, modulo='biblioteca') | {'configuracoes.siteconfig.visualizar'},
        'consulta-visualizacao': _codigos_consulta_visualizacao(todos_codigos),
    }

    for codigo_perfil, codigos_permissoes in codigos_por_perfil.items():
        perfil = perfis_por_codigo[codigo_perfil]
        PerfilPermissaoSistema.objects.filter(perfil=perfil).exclude(
            permissao__codigo__in=codigos_permissoes,
        ).delete()
        for codigo_permissao in sorted(codigos_permissoes):
            PerfilPermissaoSistema.objects.get_or_create(
                perfil=perfil,
                permissao=permissoes_por_codigo[codigo_permissao],
            )


def _reverter_seed_permissoes(apps, schema_editor):
    return None


class Migration(migrations.Migration):
    dependencies = [
        ('configuracoes', '0003_perfilacesso_perfilpermissaosistema_permissaosistema_and_more'),
    ]

    operations = [
        migrations.RunPython(_sincronizar_perfis_permissoes, _reverter_seed_permissoes),
    ]
