# Generated by Django 2.2.15 on 2020-10-22 14:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("shuup", "0076_update_supplier_shops_field"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="supplier",
            name="is_approved",
        ),
    ]
