"""
Patched version of Django's Makemessages that works with Jinja2.

Works by monkey patching django.utils.translation.trans_real.templatize
with our version.
"""

import datetime
import os
from io import BytesIO, StringIO

import babel.messages.extract
from django.core.management.commands import makemessages
from django.utils.translation import template as trans_real

KEYWORDS = dict(
    babel.messages.extract.DEFAULT_KEYWORDS,
    **{
        "_L": None,
        "gettext_lazy": None,
        "ugettext_lazy": None,
    },
)

JINJA_EXTENSIONS = [
    "jinja2.ext.do",
    "jinja2.ext.loopcontrols",
    "django_jinja.builtins.extensions.CsrfExtension",
    "django_jinja.builtins.extensions.CacheExtension",
    "shuup.xtheme.parsing.LayoutPartExtension",
    "shuup.xtheme.parsing.PlaceholderExtension",
    "shuup.xtheme.parsing.PluginExtension",
]

BABEL_OPTIONS = {
    "silent": "false",
    "newstyle_gettext": "on",
    "extensions": ",".join(JINJA_EXTENSIONS),
}

COMMENT_TAG = "Translators:"

# Store original Django templatize function
_original_templatize = trans_real.templatize


def smart_templatize(src, origin=None, **kwargs):
    """
    Smart template processor that uses Jinja2 for .jinja files and Django for .html files.
    """
    if origin and origin.endswith(".jinja"):
        return jinja_messages_to_python(src, origin, **kwargs)
    else:
        # Use Django's original templatize for .html files
        return _original_templatize(src, origin, **kwargs)


class Command(makemessages.Command):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--no-pot-date",
            action="store_true",
            dest="no_pot_date",
            default=False,
            help=("Don't update POT-Creation-Date if it would be the only change to the PO file"),
        )

    def handle(self, *args, **options):
        self.no_pot_date = options.get("no_pot_date")

        old_templatize = trans_real.templatize
        trans_real.templatize = smart_templatize
        try:
            super().handle(*args, **options)
        finally:
            trans_real.templatize = old_templatize

    def build_potfiles(self):
        """
        Build PO Template files and return paths to them.

        Extends base classes version of this method by adding the
        "Remove POT-Creation-Date" feature.
        """
        potfiles = super().build_potfiles()

        if self.no_pot_date:
            unique_potfiles = sorted(set(potfiles))  # Remove duplicates
            for potfile in unique_potfiles:
                _remove_pot_creation_date(potfile)

        return potfiles

    def write_po_file(self, potfile, locale):
        """
        Writo PO file of given locale to disk.

        Extends base classes version of this method by adding a feature
        to not change those PO files at all that have only the
        "POT-Creation-Date" header changed.
        """

        basedir = os.path.join(os.path.dirname(potfile), locale, "LC_MESSAGES")
        pofile = os.path.join(basedir, f"{str(self.domain)}.po")

        if self.no_pot_date:
            orig_contents = _read_file(pofile)

        super().write_po_file(potfile, locale)

        if self.no_pot_date:
            new_contents = _read_file(pofile)
            if orig_contents != new_contents and new_contents:
                modified_contents = _update_pot_creation_date(new_contents)
                with open(pofile, "wb") as fp:
                    fp.write(modified_contents)


def _remove_pot_creation_date(filepath):
    modified_lines = []
    with open(filepath, "rb") as fp:
        for line in fp:
            if not line.startswith(b'"POT-Creation-Date: '):
                modified_lines.append(line)
    with open(filepath, "wb") as fp:
        for line in modified_lines:
            fp.write(line)


def _read_file(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "rb") as fp:
        return fp.read()


def _update_pot_creation_date(po_contents):
    pot_line_template = '"POT-Creation-Date: {:%Y-%m-%d %H:%M}+0000\\n"'
    now = datetime.datetime.utcnow()
    pot_line = pot_line_template.format(now).encode("utf-8")
    lines = []
    for line in po_contents.splitlines():
        if line.startswith(b'"PO-Revision-Date: '):
            lines.append(pot_line + b"\n")
        if not line.startswith(b'"POT-Creation-Date: '):
            lines.append(line + b"\n")
    return b"".join(lines)


def jinja_messages_to_python(src, origin=None, **kwargs):
    """
    Convert Jinja2 file to Python preserving only messages.
    """
    output = StringIO("")
    output_lineno = 1
    for lineno, message, comments, _context in extract_jinja(src, origin):
        for comment in comments:
            output.write(f"# {COMMENT_TAG} {comment}\n")
            output_lineno += 1
        lines_to_add = lineno - output_lineno
        if lines_to_add > 0:  # Try to keep line numbers in sync
            output.write(lines_to_add * "\n")
            output_lineno += lines_to_add
        output.write(f"gettext({message!r}),")
    return output.getvalue()


def extract_jinja(contents, origin=None):
    return babel.messages.extract.extract(
        method="jinja2.ext.babel_extract",
        fileobj=BytesIO(contents.encode("utf-8")),
        options=BABEL_OPTIONS,
        keywords=KEYWORDS,
        comment_tags=(COMMENT_TAG,),
    )
