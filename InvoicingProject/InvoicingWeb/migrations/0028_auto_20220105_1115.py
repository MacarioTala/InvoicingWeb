# Generated by Django 3.2.6 on 2022-01-05 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InvoicingWeb', '0027_auto_20211214_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='CustomerName',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='ResourceEmail',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='ResourceName',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
