# Generated by Django 3.2.25 on 2025-06-29 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shuup_simple_cms", "0018_longer_log_entry_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="page",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="page",
            name="level",
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name="page",
            name="lft",
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name="page",
            name="rght",
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name="pagelogentry",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="pageopengraph",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="pageopengraphtranslation",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="pagetranslation",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
    ]
