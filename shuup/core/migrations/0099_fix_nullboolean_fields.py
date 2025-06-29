# Generated migration for fixing NullBooleanField warnings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shuup', '0098_change_productmedia_verbose_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactgrouppricedisplay',
            name='hide_prices',
            field=models.BooleanField(blank=True, default=None, null=True, verbose_name='hide prices'),
        ),
        migrations.AlterField(
            model_name='contactgrouppricedisplay',
            name='show_prices_including_taxes',
            field=models.BooleanField(blank=True, default=None, null=True, verbose_name='show prices including taxes'),
        ),
    ]
