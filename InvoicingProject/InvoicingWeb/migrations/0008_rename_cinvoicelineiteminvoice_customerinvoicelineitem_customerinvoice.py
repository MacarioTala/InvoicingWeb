# Generated by Django 3.2.6 on 2021-09-29 23:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('InvoicingWeb', '0007_alter_partnerinvoice_coveredbyremittance'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customerinvoicelineitem',
            old_name='CInvoiceLineItemInvoice',
            new_name='CustomerInvoice',
        ),
    ]
