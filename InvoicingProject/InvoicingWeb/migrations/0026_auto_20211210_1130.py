# Generated by Django 3.2.6 on 2021-12-10 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InvoicingWeb', '0025_auto_20211210_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcerate',
            name='RateToCustomer',
            field=models.DecimalField(decimal_places=2, max_digits=14),
        ),
        migrations.AlterField(
            model_name='resourcerate',
            name='TransferRate',
            field=models.DecimalField(decimal_places=2, max_digits=14),
        ),
    ]