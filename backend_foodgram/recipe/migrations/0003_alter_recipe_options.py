# Generated by Django 3.2.15 on 2024-12-22 08:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'default_related_name': 'recipes', 'ordering': ('-pub_date',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
    ]
