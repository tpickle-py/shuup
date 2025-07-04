# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-05 12:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shuup", "0055_order_line_labels"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productattribute",
            name="datetime_value",
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="datetime value"),
        ),
        migrations.AlterField(
            model_name="productattribute",
            name="numeric_value",
            field=models.DecimalField(
                blank=True,
                db_index=True,
                decimal_places=9,
                max_digits=36,
                null=True,
                verbose_name="numeric value",
            ),
        ),
    ]
