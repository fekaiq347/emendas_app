from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('emendas_app', '0011_alter_acaoorcamentaria_cod_acao'),
    ]

    operations = [
        # Repasse
        migrations.RenameField(
            model_name='repasse',
            old_name='codigo_emenda',
            new_name='cod_emenda',
        ),
        migrations.RenameField(
            model_name='repasse',
            old_name='codigo_instituicao',
            new_name='cod_instituicao',
        ),
        # Emenda
        migrations.RenameField(
            model_name='emenda',
            old_name='codigo_funcao',
            new_name='cod_funcao',
        ),
        migrations.RenameField(
            model_name='emenda',
            old_name='codigo_proponente',
            new_name='cod_proponente',
        ),
    ]

