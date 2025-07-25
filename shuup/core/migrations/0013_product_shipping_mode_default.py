# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-11-04 22:05
from __future__ import unicode_literals

from django.db import migrations

import enumfields.fields

import shuup.core.models


class Migration(migrations.Migration):
    dependencies = [
        ("shuup", "0012_contact_language"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="shipping_mode",
            field=enumfields.fields.EnumIntegerField(
                default=1,
                enum=shuup.core.models.ShippingMode,
                verbose_name="shipping mode",
            ),
        ),
    ]
