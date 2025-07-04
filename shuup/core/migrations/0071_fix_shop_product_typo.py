# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-07-08 07:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shuup", "0070_dynamic_units"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shopproduct",
            name="limit_shipping_methods",
            field=models.BooleanField(
                default=False,
                help_text="Enable this if you want to limit your product to use only the select shipping methods. You can select the allowed shipping method(s) in the field below - all the rest are disallowed.",
                verbose_name="limit the shipping methods",
            ),
        ),
    ]
