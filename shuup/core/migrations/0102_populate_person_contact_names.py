# Generated migration for Django 3+ compatibility fix
from django.db import migrations


def populate_person_contact_names(apps, schema_editor):
    """
    Populate the name field for PersonContact records based on first_name and last_name.
    This fixes the Django 3+ compatibility issue where name property conflicted with name field.
    """
    PersonContact = apps.get_model("shuup", "PersonContact")

    updated_count = 0
    for contact in PersonContact.objects.all():
        if contact.first_name or contact.last_name:
            # Compute name from first_name and last_name
            names = (contact.first_name or "", contact.last_name or "")
            computed_name = " ".join(x for x in names if x)

            # Update name field if it's different from computed name
            if computed_name and computed_name != contact.name:
                contact.name = computed_name
                contact.save(update_fields=["name"])
                updated_count += 1

    print(f"Updated {updated_count} PersonContact records with computed names")


def reverse_populate_person_contact_names(apps, schema_editor):
    """
    Reverse migration - no action needed since we're just populating data.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("shuup", "0101_piecessalesunit_salesunitasdisplayunit"),
    ]

    operations = [
        migrations.RunPython(
            populate_person_contact_names,
            reverse_populate_person_contact_names,
        ),
    ]
