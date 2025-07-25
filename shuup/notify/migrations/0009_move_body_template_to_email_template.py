# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-07-27 01:04
from __future__ import unicode_literals

from django.db import migrations


def move_body_to_template(apps, schema_editor):
    """
    Go through all SendEmail actions and convert body templates into EmailTemplates
    """
    Script = apps.get_model("shuup_notify", "Script")
    EmailTemplate = apps.get_model("shuup_notify", "EmailTemplate")

    for script in Script.objects.all():
        steps_data = list(script._step_data)
        changed = False

        for serialized_step in steps_data:
            for action_data in serialized_step.get("actions", []):
                if action_data.get("identifier") == "send_email":
                    for lang, template_data in action_data.get("template_data", {}).items():
                        if not template_data.get("body_template"):
                            continue

                        email_template = EmailTemplate.objects.create(
                            name="Unnamed Template {} ({})".format(EmailTemplate.objects.count() + 1, lang.upper()),
                            template=template_data["body_template"],
                        )

                        template_data["email_template"] = email_template.pk
                        changed = True

        if changed:
            script._step_data = steps_data
            script.save()


class Migration(migrations.Migration):
    dependencies = [
        ("shuup_notify", "0008_email_template"),
    ]

    operations = [
        migrations.RunPython(move_body_to_template, migrations.RunPython.noop),
    ]
