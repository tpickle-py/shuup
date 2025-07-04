# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-09-14 01:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shuup_gdpr", "0005_add_fields_to_skip_consent_on_auth"),
    ]

    operations = [
        migrations.AddField(
            model_name="gdprcookiecategory",
            name="default_active",
            field=models.BooleanField(
                default=False,
                help_text="whether this cookie category is active by default",
                verbose_name="active by default",
            ),
        ),
    ]
