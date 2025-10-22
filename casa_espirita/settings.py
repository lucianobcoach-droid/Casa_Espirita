"""Configurações Django para o projeto Casa Espírita."""
from __future__ import annotations

import os
from pathlib import Path

# ----------------------------------------------------------------------
# Caminhos / Variáveis básicas
# ----------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-troque-esta-chave")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS: list[str] = os.getenv(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost"
).split(",")

# ----------------------------------------------------------------------
# Apps
# ----------------------------------------------------------------------
INSTALLED_APPS = [
    # Jazzmin deve vir ANTES do admin
    "jazzmin",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "configuracoes",
    "biblioteca",
]

# ----------------------------------------------------------------------
# 🎨 Jazzmin – layout e UI
# ----------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    # Títulos e nomes visíveis
    "site_title": "Casa Espírita — Admin",
    "site_header": "Casa Espírita",
    "site_brand": "Painel Administrativo",
    "welcome_sign": "Bem-vindo(a) ao painel",

    # Logos/ícones (coloque os arquivos em static/configuracoes/)
    # Você pode usar .svg, .png, .jpg
    "site_logo": "configuracoes/logo_admin.svg",
    "login_logo": "configuracoes/logo_admin.svg",
    "site_icon": "configuracoes/favicon.png",  # favicon (16x16 / 32x32)

    # Navegação e UI
    "show_sidebar": True,
    "navigation_expanded": True,
    "show_ui_builder": True,   # botão do Jazzmin UI Builder (customização visual no topo)

    # Link de atalho no topo (opcional)
    "custom_links": {
        "admin.Customize": [
            {
                "name": "Personalizar tema",
                "url": "#",
                "icon": "fas fa-paint-brush",
                "permissions": ["auth.view_user"],
            }
        ]
    },

    # Ícones de modelos (Font Awesome)
    "icons": {
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users",

        "biblioteca.Autor": "fas fa-feather-alt",
        "biblioteca.Livro": "fas fa-book",
        "biblioteca.Venda": "fas fa-cash-register",
        "biblioteca.Emprestimo": "fas fa-handshake",

        "configuracoes.SiteConfig": "fas fa-cog",
    },

    # Textos de menu traduzidos (opcional, o Jazzmin já mostra em pt, mas reforçamos)
    "changeform_format": "horizontal_tabs",  # deixa formulários mais organizados
}

# Ajustes visuais (tema claro/escuro)
JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",            # tema claro
    "dark_mode_theme": "darkly",  # tema escuro
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-primary",
}

# ----------------------------------------------------------------------
# Middleware / URLConf / Templates
# ----------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "casa_espirita.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "configuracoes" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "casa_espirita.wsgi.application"
ASGI_APPLICATION = "casa_espirita.asgi.application"

# ----------------------------------------------------------------------
# Banco de dados
# ----------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ----------------------------------------------------------------------
# Autenticação / Internacionalização
# ----------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# ----------------------------------------------------------------------
# Arquivos estáticos e mídia
# ----------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
