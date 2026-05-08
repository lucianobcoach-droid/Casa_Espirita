"""Testes básicos para o aplicativo de configurações."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

from configuracoes.permissoes import usuario_possui_permissao
from financeiro.permissoes import PermissoesTabelasPersonalizadas

from .models import PerfilAcesso, SiteConfig, UsuarioPerfilAcesso


class SiteConfigModelTest(TestCase):
    """Validações simples para o modelo de configuração."""

    def test_string_representation(self) -> None:
        config = SiteConfig.objects.create(site_name='Lar Espírita', slogan='Luz e Caridade')
        self.assertEqual(str(config), 'Lar Espírita')

    def test_layout_leve_desativado_por_padrao(self) -> None:
        config = SiteConfig.objects.create(site_name='Lar Espírita')
        self.assertFalse(config.usar_layout_leve)


class PermissoesTabelasPersonalizadasSeedTests(TestCase):
    def test_catalogo_de_permissoes_da_frente_foi_semeado(self):
        perfil_admin = PerfilAcesso.objects.get(codigo='administrador-geral')

        self.assertTrue(
            set(PermissoesTabelasPersonalizadas.TODAS).issubset(
                set(perfil_admin.permissoes.values_list('codigo', flat=True))
            )
        )

    def test_operador_financeiro_recebe_recorte_operacional_conservador(self):
        perfil = PerfilAcesso.objects.get(codigo='operador-financeiro')
        codigos = set(perfil.permissoes.values_list('codigo', flat=True))

        self.assertIn(PermissoesTabelasPersonalizadas.VISUALIZAR, codigos)
        self.assertIn(PermissoesTabelasPersonalizadas.CRIAR, codigos)
        self.assertIn(PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA, codigos)
        self.assertIn(PermissoesTabelasPersonalizadas.PREENCHER_LINHAS, codigos)
        self.assertIn(PermissoesTabelasPersonalizadas.EDITAR_LINHAS, codigos)
        self.assertIn(PermissoesTabelasPersonalizadas.EXPORTAR, codigos)
        self.assertNotIn(PermissoesTabelasPersonalizadas.CONFIGURAR_FORMULA, codigos)
        self.assertNotIn(PermissoesTabelasPersonalizadas.ARQUIVAR_RESTAURAR, codigos)
        self.assertNotIn(PermissoesTabelasPersonalizadas.ADMINISTRAR_CONFIGURACOES, codigos)

    def test_consulta_visualizacao_recebe_apenas_leitura_e_exportacao(self):
        perfil = PerfilAcesso.objects.get(codigo='consulta-visualizacao')
        codigos = set(perfil.permissoes.values_list('codigo', flat=True))

        self.assertIn(PermissoesTabelasPersonalizadas.VISUALIZAR, codigos)
        self.assertIn(PermissoesTabelasPersonalizadas.EXPORTAR, codigos)
        self.assertNotIn(PermissoesTabelasPersonalizadas.CRIAR, codigos)
        self.assertNotIn(PermissoesTabelasPersonalizadas.EDITAR_ESTRUTURA, codigos)
        self.assertNotIn(PermissoesTabelasPersonalizadas.CONFIGURAR_FORMULA, codigos)

    def test_helper_de_permissao_respeita_novo_catalogo(self):
        user_model = get_user_model()
        usuario = user_model.objects.create_user(
            username='consulta_tabelas',
            password='senha-segura-123',
            is_active=True,
        )
        perfil = PerfilAcesso.objects.get(codigo='consulta-visualizacao')
        UsuarioPerfilAcesso.objects.create(usuario=usuario, perfil=perfil)

        self.assertTrue(
            usuario_possui_permissao(usuario, PermissoesTabelasPersonalizadas.VISUALIZAR)
        )
        self.assertTrue(
            usuario_possui_permissao(usuario, PermissoesTabelasPersonalizadas.EXPORTAR)
        )
        self.assertFalse(
            usuario_possui_permissao(
                usuario,
                PermissoesTabelasPersonalizadas.CONFIGURAR_FORMULA,
            )
        )
