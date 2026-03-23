# Diagnóstico da Estrutura Atual

Data da análise: 2026-03-23
Workspace analisado: `C:\Users\lucia\OneDrive\Área de Trabalho\Casa_Espirita`

## 1. Branch atual

- `feat/reinicio-financeiro`

## 2. Último commit

- `9f59a75` - `merge: admin layout leve`

## 3. Status do git

Saída observada de `git status --short --branch`:

```text
## feat/reinicio-financeiro...origin/feat/reinicio-financeiro
```

Leitura do estado atual:

- branch local está alinhada à branch remota de mesmo nome
- não há arquivos modificados, staged ou untracked no momento da análise

## 4. Árvore principal do projeto

```text
Casa_Espirita/
|-- manage.py
|-- README.md
|-- ARQUITETURA.md
|-- requirements.txt
|-- biblioteca/
|   |-- admin.py
|   |-- apps.py
|   |-- forms.py
|   |-- models.py
|   |-- signals.py
|   |-- urls.py
|   |-- views.py
|   |-- management/
|   |   `-- commands/
|   |       `-- notificar_atrasos.py
|   |-- migrations/
|   |   `-- 0001_initial.py
|   `-- templates/
|       `-- biblioteca/
|           |-- base.html
|           |-- autor_form.html
|           |-- autor_list.html
|           |-- livro_form.html
|           |-- livro_list.html
|           |-- venda_form.html
|           |-- venda_list.html
|           |-- emprestimo_form.html
|           `-- emprestimo_list.html
|-- casa_espirita/
|   |-- settings.py
|   |-- urls.py
|   |-- asgi.py
|   `-- wsgi.py
|-- configuracoes/
|   |-- admin.py
|   |-- apps.py
|   |-- models.py
|   |-- tests.py
|   |-- views.py
|   |-- migrations/
|   |   |-- 0001_initial.py
|   |   `-- 0002_fix_usar_layout_leve.py
|   |-- templatetags/
|   |   `-- configuracoes_admin.py
|   `-- templates/
|       |-- admin/
|       |   `-- base_site.html
|       `-- configuracoes/
|           `-- siteconfig_detail.html
`-- static/
    `-- configuracoes/
        |-- logo.svg
        |-- site.css
        `-- admin/
            |-- light.css
            `-- light.js
```

Observação:

- não existia pasta `docs/` antes desta análise; este arquivo foi criado para registrar o diagnóstico solicitado

## 5. Apps Django existentes

Apps próprios identificados na estrutura e em `INSTALLED_APPS`:

- `configuracoes`
- `biblioteca`

Apps nativos do Django atualmente habilitados:

- `django.contrib.admin`
- `django.contrib.auth`
- `django.contrib.contenttypes`
- `django.contrib.sessions`
- `django.contrib.messages`
- `django.contrib.staticfiles`

## 6. Conteúdo atual de `INSTALLED_APPS`

Conteúdo atual em `casa_espirita/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'configuracoes',
    'biblioteca',
]
```

## 7. Rotas principais em `casa_espirita/urls.py`

Rotas registradas hoje:

- `/admin/` -> Django Admin
- `/` -> `SiteConfigDetailView`
- `/biblioteca/` -> inclusão de `biblioteca.urls`

Detalhamento interno de `biblioteca.urls`:

- `/biblioteca/autores/`
- `/biblioteca/autores/novo/`
- `/biblioteca/livros/`
- `/biblioteca/livros/novo/`
- `/biblioteca/vendas/`
- `/biblioteca/vendas/nova/`
- `/biblioteca/emprestimos/`
- `/biblioteca/emprestimos/novo/`

## 8. Models atuais em cada app

### App `configuracoes`

Model identificado:

- `SiteConfig`

Campos atuais:

- `site_name`: `CharField(max_length=150, default='Casa Espírita')`
- `slogan`: `CharField(max_length=255, blank=True)`
- `descricao`: `TextField(blank=True)`
- `logo`: `ImageField(upload_to='configuracoes/logo/', blank=True, null=True)`
- `usar_layout_leve`: `BooleanField(default=False)`
- `atualizado_em`: `DateTimeField(auto_now=True)`

Responsabilidade atual:

- manter configurações institucionais do site
- controlar opção visual do admin via `usar_layout_leve`

### App `biblioteca`

Models identificados:

- `Autor`
- `Livro`
- `Venda`
- `Emprestimo`

#### `Autor`

Campos:

- `nome`
- `biografia`

Comportamento:

- ordenação por `nome`

#### `Livro`

Campos:

- `titulo`
- `descricao`
- `estoque_total`
- `estoque_disponivel`
- `preco`
- `autores` (`ManyToMany` com `Autor`)

Comportamento:

- ordenação por `titulo`
- `save()` ajusta `estoque_disponivel`
- `ajustar_estoque()` limita o estoque entre `0` e `estoque_total`

#### `Venda`

Campos:

- `livro` (`ForeignKey` para `Livro`)
- `quantidade`
- `valor_unitario`
- `comprador`
- `criado_em`

Comportamento:

- ordenação por `-criado_em`
- propriedade `valor_total`

#### `Emprestimo`

Campos:

- `livro` (`ForeignKey` para `Livro`)
- `leitor`
- `quantidade`
- `data_emprestimo`
- `data_prevista_devolucao`
- `data_devolucao`
- `status`
- `observacoes`
- `criado_em`
- `atualizado_em`

Comportamento:

- statuses: `pendente`, `atrasado`, `devolvido`
- ordenação por `-data_emprestimo`, `leitor`
- propriedade `esta_atrasado`
- método `marcar_como_devolvido()`

Leitura arquitetural atual:

- o app `biblioteca` já contém uma parte operacional com impacto financeiro indireto por meio de `Venda`
- ainda não existe um app financeiro separado
- ainda não há modelos explícitos de caixa, contas, receitas, despesas, centros de custo ou conciliação

## 9. Views atuais em cada app

### App `configuracoes`

View identificada:

- `SiteConfigDetailView` (`DetailView`)

Comportamento:

- renderiza `configuracoes/siteconfig_detail.html`
- usa `SiteConfig` como model
- retorna o primeiro registro de `SiteConfig`
- se não houver registro no banco, instancia um objeto em memória com `site_name='Casa Espírita'`

### App `biblioteca`

Views identificadas:

- `AutorListView`
- `AutorCreateView`
- `LivroListView`
- `LivroCreateView`
- `VendaListView`
- `VendaCreateView`
- `EmprestimoListView`
- `EmprestimoCreateView`

Padrão atual:

- somente class-based views genéricas (`ListView` e `CreateView`)
- foco em listagem e criação
- não há views de edição, exclusão, dashboard, relatórios ou APIs

## 10. Templates principais existentes

Templates HTML encontrados:

- `biblioteca/templates/biblioteca/base.html`
- `biblioteca/templates/biblioteca/autor_form.html`
- `biblioteca/templates/biblioteca/autor_list.html`
- `biblioteca/templates/biblioteca/livro_form.html`
- `biblioteca/templates/biblioteca/livro_list.html`
- `biblioteca/templates/biblioteca/venda_form.html`
- `biblioteca/templates/biblioteca/venda_list.html`
- `biblioteca/templates/biblioteca/emprestimo_form.html`
- `biblioteca/templates/biblioteca/emprestimo_list.html`
- `configuracoes/templates/configuracoes/siteconfig_detail.html`
- `configuracoes/templates/admin/base_site.html`

Leitura prática:

- `biblioteca/base.html` aparenta ser o template-base funcional do módulo já existente
- o projeto hoje já possui interface para autores, livros, vendas e empréstimos
- `configuracoes` possui uma página inicial e customização do admin
- não há templates específicos para um módulo financeiro

## 11. Próximo passo mais seguro para iniciar o módulo financeiro

O próximo passo mais seguro, considerando a estrutura real atual, é:

- criar um app novo e isolado, por exemplo `financeiro`, sem acoplar a primeira versão diretamente ao app `biblioteca`

Justificativa:

- o projeto hoje tem separação razoável entre `configuracoes` e `biblioteca`
- `biblioteca.Venda` já representa um evento comercial, mas ainda não modela caixa, lançamento contábil nem contas
- iniciar o financeiro dentro de `biblioteca` aumentaria acoplamento e dificultaria evolução posterior
- um app isolado permite introduzir modelos financeiros com migrações próprias e integração gradual com `Venda`

Sequência mais segura sugerida antes de implementar:

1. definir o escopo mínimo do módulo financeiro
2. fechar o primeiro conjunto de entidades
3. só então criar o app e suas migrações iniciais

Escopo mínimo recomendado para a primeira iteração:

- `ContaFinanceira` ou `Caixa`
- `CategoriaFinanceira`
- `LancamentoFinanceiro`
- tipos de lançamento: receita e despesa
- vínculo opcional de lançamento com `biblioteca.Venda`

Risco principal a evitar:

- começar pela interface ou por telas sem fechar primeiro o modelo de domínio e a relação com `Venda`

Conclusão objetiva:

- a base atual está limpa e enxuta
- existem apenas dois apps próprios ativos: `configuracoes` e `biblioteca`
- a forma mais segura de iniciar o financeiro é manter um app dedicado e integrar com `biblioteca` apenas por referências explícitas, não por mistura de responsabilidades
