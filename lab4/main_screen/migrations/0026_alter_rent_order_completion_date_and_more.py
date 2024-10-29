# Generated by Django 4.2.4 on 2024-10-29 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_screen', '0025_rent_order_client'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rent_order',
            name='completion_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения'),
        ),
        migrations.AlterField(
            model_name='rent_order',
            name='formation_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата формирования'),
        ),
        migrations.AlterField(
            model_name='rent_order',
            name='order_date',
            field=models.DateTimeField(verbose_name='Дата создания'),
        ),
    ]
