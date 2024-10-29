# Generated by Django 4.2.4 on 2024-10-01 06:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_screen', '0007_order_total_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bill_date', models.DateField(verbose_name='Дата создания')),
                ('address', models.CharField(max_length=255, verbose_name='Адрес')),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('DELETED', 'Deleted'), ('REJECTED', 'Rejected'), ('COMPLETED', 'Completed'), ('FORMED', 'Fomed')], default='DRAFT', max_length=10)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Итоговая стоимость')),
            ],
            options={
                'verbose_name': 'Заявка',
                'verbose_name_plural': 'Заявки',
            },
        ),
        migrations.CreateModel(
            name='BillService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_reading', models.CharField(blank=True, null=True, verbose_name='Последние показания/Дата последней оплаты')),
                ('current_reading', models.CharField(blank=True, null=True, verbose_name='Текущие показания/Дата')),
                ('amount_due', models.IntegerField(default=0, verbose_name='Сумма к оплате')),
                ('payment_icon', models.URLField(blank=True, default='http://127.0.0.1:9000/lab1/money_icon.svg', null=True, verbose_name='Иконка платежа')),
                ('bill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_screen.bill', verbose_name='Заявка')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_screen.service', verbose_name='Услуга')),
            ],
            options={
                'verbose_name': 'Услуга заявки',
                'verbose_name_plural': 'Услуги заявок',
            },
        ),
        migrations.RemoveField(
            model_name='orderservice',
            name='order',
        ),
        migrations.RemoveField(
            model_name='orderservice',
            name='service',
        ),
        migrations.DeleteModel(
            name='Order',
        ),
        migrations.DeleteModel(
            name='OrderService',
        ),
    ]
