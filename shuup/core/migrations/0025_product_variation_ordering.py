# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-05 00:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shuup", "0024_product_shop_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="productvariationvariable",
            name="ordering",
            field=models.SmallIntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name="productvariationvariablevalue",
            name="ordering",
            field=models.SmallIntegerField(db_index=True, default=0),
        ),
    ]
