# Generated by Django 3.2.6 on 2021-11-11 23:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('InvoicingWeb', '0016_remove_customerinvoicelineitem_resource'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerinvoicelineitem',
            name='Resource',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='InvoicingWeb.resource'),
        ),
    ]
