# Arquitetura do Projeto Casa Espírita

Este documento descreve a organização inicial do projeto e serve como guia para evolução futura.

## Visão Geral

O projeto é construído sobre o framework Django 4.x e segue uma arquitetura modular, separando responsabilidades em aplicativos independentes.

```
Casa_Espirita/
├── ARQUITETURA.md
├── README.md
├── manage.py
├── requirements.txt
├── casa_espirita/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── configuracoes/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── migrations/
    │   └── __init__.py
    ├── models.py
    ├── tests.py
    └── views.py
```

## Aplicativo `configuracoes`

Responsável pela gestão das configurações do site, incluindo a entidade `SiteConfig`, que permite configurar nome, slogan e logo da instituição.

## Configurações Globais

O módulo `casa_espirita.settings` está preparado para uso em ambiente de desenvolvimento, com SQLite como banco de dados padrão. Variáveis sensíveis devem ser externalizadas por meio de variáveis de ambiente em futuras iterações.
