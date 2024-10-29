# Generated by Django 4.2.4 on 2024-09-25 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_screen', '0002_order_status_service_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderservice',
            name='current_reading',
            field=models.IntegerField(blank=True, null=True, verbose_name='Текущие показания (оставить строку пустой, если это не жкх)'),
        ),
        migrations.AlterField(
            model_name='orderservice',
            name='last_reading',
            field=models.CharField(blank=True, null=True, verbose_name='Последние показания/Дата последней оплаты'),
        ),
    ]