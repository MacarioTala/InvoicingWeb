# Generated by Django 3.2.6 on 2021-11-11 21:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('InvoicingWeb', '0011_auto_20211111_1325'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectresource',
            old_name='ProjectResourceProject',
            new_name='Project',
        ),
        migrations.RenameField(
            model_name='projectresource',
            old_name='ProjectResourceRateToCustomer',
            new_name='RateToCustomer',
        ),
        migrations.RenameField(
            model_name='projectresource',
            old_name='ProjectResourceTransferRate',
            new_name='TransferRate',
        ),
    ]
