# GUIA DE HOSPEDAGEM E HOMOLOGACAO DO FINANCEIRO

## Objetivo
Este guia registra o pacote minimo para subir o sistema atual em hospedagem com foco na homologacao do modulo `financeiro`.

Ele nao abre novas frentes de negocio. Ele descreve o que ja existe no repositorio e o que precisa ser preenchido no host para o sistema subir com seguranca.

## Escopo desta subida
- login/logout
- recuperacao de senha V1
- portal autenticado `/inicio/`
- shell autenticado compartilhado
- `financeiro` operacional para homologacao
- permissoes V1 ja implantadas

## Variaveis de ambiente obrigatorias

### Obrigatorias para producao/homologacao
- `DJANGO_DEBUG`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`

### Obrigatorias quando houver formulario com dominio real/HTTPS
- `DJANGO_CSRF_TRUSTED_ORIGINS`

### Obrigatorias para endurecimento minimo de HTTPS
- `DJANGO_SESSION_COOKIE_SECURE`
- `DJANGO_CSRF_COOKIE_SECURE`
- `DJANGO_SECURE_SSL_REDIRECT`
- `DJANGO_SECURE_HSTS_SECONDS`
- `DJANGO_SECURE_PROXY_SSL_HEADER`

### Recomendadas quando o dominio principal ja estiver estabilizado em HTTPS
- `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS`
- `DJANGO_SECURE_HSTS_PRELOAD`

### Obrigatorias para o banco atual da homologacao
- `DJANGO_DB_PATH`

### Obrigatorias se houver upload/logo em ambiente persistente
- `DJANGO_MEDIA_ROOT`

### Obrigatorias para recuperacao de senha real por e-mail
- `DJANGO_EMAIL_BACKEND`
- `DJANGO_EMAIL_HOST`
- `DJANGO_EMAIL_PORT`
- `DJANGO_EMAIL_HOST_USER`
- `DJANGO_EMAIL_HOST_PASSWORD`
- `DJANGO_EMAIL_USE_TLS` ou `DJANGO_EMAIL_USE_SSL`
- `DJANGO_DEFAULT_FROM_EMAIL`
- `DJANGO_SERVER_EMAIL`

## O que precisa estar preenchido no host
- uma `DJANGO_SECRET_KEY` segura
- `DJANGO_DEBUG=0`
- os dominios reais em `DJANGO_ALLOWED_HOSTS`
- os dominios com protocolo em `DJANGO_CSRF_TRUSTED_ORIGINS`
- a politica de HTTPS/HSTS adequada ao host
- um caminho persistente para o banco SQLite, se a homologacao continuar com SQLite
- um caminho persistente para `media/`, se houver upload de logo
- SMTP real, se a recuperacao de senha precisar funcionar fora do console

## Dependencias do projeto
Arquivo de referencia: [requirements.txt](C:/Users/lucia/OneDrive/Área%20de%20Trabalho/Casa_Espirita/requirements.txt)

Dependencias relevantes para hospedagem:
- `Django`
- `Pillow`
- `gunicorn`
- `whitenoise`

## Configuracao de staticfiles e media
- `STATIC_ROOT` esta definido em `staticfiles/`
- `STATIC_URL` usa `/static/`
- `STATICFILES_STORAGE` usa `whitenoise.storage.CompressedManifestStaticFilesStorage`
- `MEDIA_ROOT` pode ser controlado por `DJANGO_MEDIA_ROOT`
- `MEDIA_URL` usa `/media/`

Observacao:
- WhiteNoise cobre os arquivos estaticos do projeto
- arquivos de media continuam dependendo de pasta persistente no host ou estrategia especifica do provedor

## Banco de dados atual
- o projeto segue configurado com `sqlite3`
- o caminho pode ser controlado por `DJANGO_DB_PATH`

Observacao importante:
- para homologacao simples, SQLite pode servir se o host oferecer disco persistente
- para operacao mais sensivel ou multi-instancia, a estrategia de banco deve ser revista depois da homologacao

## Sequencia recomendada de deploy

1. criar ambiente virtual no host
2. instalar dependencias com `pip install -r requirements.txt`
3. configurar variaveis de ambiente a partir de [.env.example](C:/Users/lucia/OneDrive/Área%20de%20Trabalho/Casa_Espirita/.env.example)
4. apontar `DJANGO_DB_PATH` para local persistente
5. apontar `DJANGO_MEDIA_ROOT` para local persistente, se houver upload
6. executar `py manage.py migrate`
7. executar `py manage.py collectstatic --noinput`
8. criar ou regularizar usuario administrador tecnico
9. validar `SiteConfig` e branding institucional
10. validar login, portal `/inicio/` e entrada no `financeiro`

## Comandos operacionais de subida

### Validacao local minima
```bash
py manage.py check
```

### Validacao de deploy
```bash
py manage.py check --deploy
```

Observacao:
- se `check --deploy` acusar `HSTS` ou `SECURE_SSL_REDIRECT`, isso normalmente indica variaveis de HTTPS ainda nao preenchidas no host
- se acusar `SECRET_KEY`, a chave configurada esta fraca demais para uso real

### Migracoes
```bash
py manage.py migrate
```

### Staticfiles
```bash
py manage.py collectstatic --noinput
```

### Criacao de administrador tecnico
```bash
py manage.py createsuperuser
```

### Execucao WSGI
Exemplo com Gunicorn:
```bash
gunicorn casa_espirita.wsgi:application
```

## Usuario/admin necessario
- e necessario pelo menos 1 superusuario tecnico para acesso ao `/admin/`
- o superusuario tecnico nao substitui perfil funcional automaticamente
- para operar o sistema fora do `/admin/`, o usuario deve ter e-mail valido e perfil-base coerente

## Checklist de validacao pos-subida
- `login/` abre corretamente
- `senha/esqueci/` abre corretamente
- `/inicio/` abre apos login
- `/financeiro/` entra sem erro
- listagem de lancamentos abre
- importacao/exportacao abre
- extrato, resumo e prestacao de contas abrem
- `/admin/` abre para o superusuario tecnico
- o nome institucional vem de `SiteConfig`
- `Sair` funciona
- um usuario com perfil `Operador financeiro` entra no modulo e um usuario sem perfil continua sem acesso funcional

## Pendencias que continuam dependentes do provedor
- SMTP real para e-mail de reset
- definicao final sobre banco em producao/homologacao
- persistencia de `media/`
- camada HTTP/HTTPS do host, incluindo proxy e certificados
- paginas de erro customizadas (`403/404/500`), se o ambiente exigir acabamento maior

## Observacoes finais
- o foco atual e homologar o `financeiro`; problemas encontrados em outros modulos so devem voltar a ser tratados depois que a subida estiver estavel
- `tmp/` permanece fora do fluxo de deploy e fora de commit
