from django.db import migrations, connection

def add_column_if_missing(apps, schema_editor):
    with connection.cursor() as c:
        c.execute("PRAGMA table_info(configuracoes_siteconfig)")
        cols = {row[1] for row in c.fetchall()}
        if "usar_layout_leve" not in cols:
            c.execute("""
                ALTER TABLE configuracoes_siteconfig
                ADD COLUMN usar_layout_leve boolean NOT NULL DEFAULT 0
            """)

class Migration(migrations.Migration):
    dependencies = [
        ("configuracoes", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_column_if_missing, migrations.RunPython.noop),
    ]
