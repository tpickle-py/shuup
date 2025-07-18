# Generated by Django 3.2.25 on 2025-07-04 06:14

from django.db import migrations
import shuup.core.fields
import shuup.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("shuup", "0102_populate_person_contact_names"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shopproduct",
            name="backorder_maximum",
            field=shuup.core.fields.QuantityField(
                blank=True,
                decimal_places=9,
                default=0,
                help_text="The number of units that can be purchased after the product is already sold out (out of stock). Set to blank for product to be purchasable without limits.",
                max_digits=36,
                null=True,
                validators=[
                    shuup.core.validators.validate_nonzero_quantity,
                    shuup.core.validators.validate_minimum_less_than_maximum,
                ],
                verbose_name="backorder maximum",
            ),
        ),
        migrations.AlterField(
            model_name="shopproduct",
            name="minimum_purchase_quantity",
            field=shuup.core.fields.QuantityField(
                decimal_places=9,
                default=1,
                help_text="Set a minimum number of products needed to be ordered for the purchase. This is useful for setting bulk orders and B2B purchases.",
                max_digits=36,
                validators=[
                    shuup.core.validators.validate_nonzero_quantity,
                    shuup.core.validators.validate_purchase_multiple,
                ],
                verbose_name="minimum purchase quantity",
            ),
        ),
    ]
