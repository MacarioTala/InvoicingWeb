# Generated by Django 3.2.6 on 2021-12-09 20:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('InvoicingWeb', '0023_auto_20211209_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcerate',
            name='Project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='InvoicingWeb.project'),
        ),
    ]
