# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-06-20 17:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shuup_simple_cms", "0007_gdpr"),
    ]

    operations = [
        migrations.AddField(
            model_name="page",
            name="show_child_timestamps",
            field=models.BooleanField(
                default=True,
                help_text="Check this if you want to show timestamps on the child pages. Please note, that this requires the children to be listed on the page as well.",
                verbose_name="show child page timestamps",
            ),
        ),
    ]
