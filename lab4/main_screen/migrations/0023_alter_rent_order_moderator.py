# Generated by Django 4.2.4 on 2024-10-29 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_screen', '0022_alter_rent_order_moderator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rent_order',
            name='moderator',
            field=models.IntegerField(verbose_name='Модератор'),
        ),
    ]
