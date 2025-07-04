# Generated by Django 2.2.14 on 2020-07-23 08:48

import django.db.models.deletion
from django.db import migrations

import parler.fields


class Migration(migrations.Migration):
    dependencies = [
        ("shuup_gdpr", "0007_help-text-improvements"),
    ]

    operations = [
        migrations.AlterField(
            model_name="gdprcookiecategorytranslation",
            name="master",
            field=parler.fields.TranslationsForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="translations",
                to="shuup_gdpr.GDPRCookieCategory",
            ),
        ),
        migrations.AlterField(
            model_name="gdprsettingstranslation",
            name="master",
            field=parler.fields.TranslationsForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="translations",
                to="shuup_gdpr.GDPRSettings",
            ),
        ),
    ]
