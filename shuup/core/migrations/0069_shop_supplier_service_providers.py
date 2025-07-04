# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-05-29 02:42
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models

import shuup.core.fields


class Migration(migrations.Migration):
    dependencies = [
        ("shuup", "0068_help_text_improvements"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentmethod",
            name="supplier",
            field=models.ForeignKey(
                blank=True,
                help_text="The supplier for this service. This service will be available only for order sources that contain all items from this supplier.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="shuup.Supplier",
                verbose_name="supplier",
            ),
        ),
        migrations.AddField(
            model_name="servicebehaviorcomponent",
            name="identifier",
            field=shuup.core.fields.InternalIdentifierField(
                blank=True, editable=False, max_length=64, null=True, unique=True
            ),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="shops",
            field=models.ManyToManyField(
                blank=True,
                help_text="This service provider will be available only for order sources of the given shop. If blank, this service provider is available for any order source.",
                related_name="service_providers",
                to="shuup.Shop",
                verbose_name="shops",
            ),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="supplier",
            field=models.ForeignKey(
                blank=True,
                help_text="This service provider will be available only for order sources that contain all items from the configured supplier. If blank, this service provider is available for any order source.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="service_providers",
                to="shuup.Supplier",
                verbose_name="supplier",
            ),
        ),
        migrations.AddField(
            model_name="shippingmethod",
            name="supplier",
            field=models.ForeignKey(
                blank=True,
                help_text="The supplier for this service. This service will be available only for order sources that contain all items from this supplier.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="shuup.Supplier",
                verbose_name="supplier",
            ),
        ),
        migrations.AlterField(
            model_name="supplier",
            name="name",
            field=models.CharField(
                db_index=True,
                help_text="The product supplier's name. You can enable suppliers to manage the inventory of stocked products.",
                max_length=128,
                verbose_name="name",
            ),
        ),
    ]
