# Generated by Django 3.2.6 on 2021-12-10 19:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('InvoicingWeb', '0024_alter_resourcerate_project'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerinvoicelineitem',
            name='Rate',
        ),
        migrations.RemoveField(
            model_name='customerinvoicelineitem',
            name='Rate_currency',
        ),
        migrations.RemoveField(
            model_name='customerinvoicelineitem',
            name='TotalAmount',
        ),
        migrations.RemoveField(
            model_name='customerinvoicelineitem',
            name='TotalAmount_currency',
        ),
    ]
