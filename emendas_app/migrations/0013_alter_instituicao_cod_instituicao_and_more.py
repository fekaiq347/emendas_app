# Generated by Django 5.2.3 on 2025-06-30 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emendas_app', '0012_rename_codigo_to_cod'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instituicao',
            name='cod_instituicao',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='proponente',
            name='cod_proponente',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
    ]
