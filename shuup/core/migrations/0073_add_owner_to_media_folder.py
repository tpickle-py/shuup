# Generated by Django 2.2 on 2020-08-13 07:29

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("shuup", "0072_django2_managers"),
    ]

    operations = [
        migrations.AddField(
            model_name="mediafolder",
            name="owners",
            field=models.ManyToManyField(
                help_text="Select which users will own this folder.",
                related_name="owning_media_folders",
                to=settings.AUTH_USER_MODEL,
                verbose_name="owners",
            ),
        ),
        migrations.AddField(
            model_name="mediafolder",
            name="visible",
            field=models.BooleanField(
                default=False,
                help_text="Should this folder be visible for everyone in the media browser",
                verbose_name="visible",
            ),
        ),
    ]
