"""
Show known Shuup settings and their values.
"""

from django.core.management.base import BaseCommand

import shuup.utils.settings_doc


class Command(BaseCommand):
    help = __doc__.strip()

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--only-changed",
            action="store_true",
            default=False,
            help="Show only settings with non-default values",
        )

    def handle(self, *args, **options):
        docs = shuup.utils.settings_doc.get_known_settings_documentation(
            only_changed=options["only_changed"]
        )
        self.stdout.write(docs)
