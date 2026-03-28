from __future__ import annotations

from django.db.utils import OperationalError, ProgrammingError

from .models import ConfiguracaoInstitucional


_STOPWORDS_INICIAIS = {
    'a',
    'as',
    'da',
    'das',
    'de',
    'do',
    'dos',
    'e',
}


def _extrair_iniciais(nome: str) -> str:
    partes = [parte for parte in (nome or '').strip().split() if parte]
    relevantes = [parte for parte in partes if parte.lower() not in _STOPWORDS_INICIAIS]
    base = relevantes or partes
    if base:
        return ''.join(parte[0] for parte in base[:2]).upper()

    compacto = ''.join(ch for ch in nome if ch.isalnum()).upper()
    if compacto:
        return compacto[:2]

    return 'CE'


def financeiro_shell_brand(request):
    nome_instituicao = 'Casa Espirita'
    logo_url = ''

    try:
        configuracao = (
            ConfiguracaoInstitucional.objects.filter(ativo=True, padrao=True)
            .only('nome_instituicao', 'logo_url')
            .first()
        )
    except (OperationalError, ProgrammingError):
        configuracao = None

    if configuracao and configuracao.nome_instituicao and configuracao.nome_instituicao.strip():
        nome_instituicao = configuracao.nome_instituicao.strip()
    if configuracao and configuracao.logo_url and configuracao.logo_url.strip():
        logo_url = configuracao.logo_url.strip()

    return {
        'financeiro_shell_brand_name': nome_instituicao,
        'financeiro_shell_brand_initials': _extrair_iniciais(nome_instituicao),
        'financeiro_shell_brand_logo_url': logo_url,
    }
