# Generated by Django 4.2.4 on 2024-09-25 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_screen', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Draft'), ('DELETED', 'Deleted'), ('REJECTED', 'Rejected'), ('COMPLETED', 'Completed'), ('FORMED', 'Fomed')], default='DRAFT', max_length=10),
        ),
        migrations.AddField(
            model_name='service',
            name='status',
            field=models.CharField(default=True, max_length=20, verbose_name='Статус услуги'),
        ),
    ]