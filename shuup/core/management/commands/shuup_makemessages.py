"""
Makemessages helper for Shuup projects.

Runs Django's makemessages for django and djangojs domains with sane
defaults for Shuup projects (ignores and extensions).
"""

from . import makemessages

IGNORES = ["node_modules", "bower_components", "static", "*tests", "_misc", "doc", "docs"]
EXTENSIONS = ["py", "jinja"]


class Command(makemessages.Command):
    help = __doc__

    def add_arguments(self, parser):
        class InterceptedParser:
            def add_argument(self, *args, **kwargs):
                if args[0] == "--domain":
                    return
                elif args[0] == "--ignore":
                    kwargs["default"] = IGNORES
                elif args[0] == "--no-obsolete":
                    kwargs["default"] = True
                elif args[0] == "--no-location":
                    kwargs["default"] = True
                elif args[0] == "--no-pot-date":
                    kwargs["default"] = True
                parser.add_argument(*args, **kwargs)
                if args[0].startswith("--no-") and kwargs.get("default"):
                    name = "--include-" + args[0][5:]
                    kwargs["default"] = False
                    kwargs["action"] = "store_false"
                    kwargs["help"] = "Opposite of " + args[0]
                    new_args = (name,) + args[1:]
                    parser.add_argument(*new_args, **kwargs)

        super().add_arguments(InterceptedParser())

    def handle(self, *args, **options):
        if not options.get("extensions"):
            options["extensions"] = EXTENSIONS

        self.stdout.write("Doing makemessages for django domain")
        super().handle(*args, domain="django", **options)

        options["extensions"] = ["js", "jsx"]
        self.stdout.write("Doing makemessages for djangojs domain")
        super().handle(*args, domain="djangojs", **options)
