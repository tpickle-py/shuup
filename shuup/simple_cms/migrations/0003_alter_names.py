# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-12-14 10:47
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models

import mptt.fields


class Migration(migrations.Migration):
    dependencies = [
        ("shuup_simple_cms", "0002_md_to_html"),
    ]

    operations = [
        migrations.AlterField(
            model_name="page",
            name="available_from",
            field=models.DateTimeField(
                blank=True,
                help_text="Set an available from date to restrict the page to be available only after a certain date and time. This is useful for pages describing sales campaigns or other time-sensitive pages.",
                null=True,
                verbose_name="available from",
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="available_to",
            field=models.DateTimeField(
                blank=True,
                help_text="Set an available to date to restrict the page to be available only after a certain date and time. This is useful for pages describing sales campaigns or other time-sensitive pages.",
                null=True,
                verbose_name="available to",
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="list_children_on_page",
            field=models.BooleanField(
                default=False,
                help_text="Check this if this page should list its children pages.",
                verbose_name="list children on page",
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="parent",
            field=mptt.fields.TreeForeignKey(
                blank=True,
                help_text="Set this to a parent page if this page should be subcategorized under another page.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="shuup_simple_cms.Page",
                verbose_name="parent",
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="visible_in_menu",
            field=models.BooleanField(
                default=False,
                help_text="Check this if this page should have a link in the top menu of the store front.",
                verbose_name="visible in menu",
            ),
        ),
        migrations.AlterField(
            model_name="pagetranslation",
            name="content",
            field=models.TextField(
                help_text="The page content. This is the text that is displayed when customers click on your page link.",
                verbose_name="content",
            ),
        ),
        migrations.AlterField(
            model_name="pagetranslation",
            name="title",
            field=models.CharField(
                help_text="The page title. This is shown anywhere links to your page are shown.",
                max_length=256,
                verbose_name="title",
            ),
        ),
        migrations.AlterField(
            model_name="pagetranslation",
            name="url",
            field=models.CharField(
                blank=True,
                default=None,
                help_text="The page url. Choose a descriptive url so that search engines can rank your page higher. Often the best url is simply the page title with spaces replaced with dashes.",
                max_length=100,
                null=True,
                unique=True,
                verbose_name="URL",
            ),
        ),
    ]
