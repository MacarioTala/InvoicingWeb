# Generated by Django 3.2.6 on 2021-11-11 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InvoicingWeb', '0010_alter_partnerinvoice_customerinvoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectresource',
            name='FromDate',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='projectresource',
            name='ToDate',
            field=models.DateField(null=True),
        ),
    ]
