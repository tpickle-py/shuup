"""
Sphinx plugins for Django documentation.
"""

import json
import os
import re

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx import __version__ as sphinx_ver, addnodes
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util.compat import Directive
from sphinx.util.console import bold
from sphinx.util.nodes import set_source_info
from sphinx.writers.html import SmartyPantsHTMLTranslator

# RE for option descriptions without a '--' prefix
simple_option_desc_re = re.compile(r"([-_a-zA-Z0-9]+)(\s*.*?)(?=,\s+(?:/|-|--)|$)")


def setup(app):
    app.add_crossref_type(
        directivename="setting",
        rolename="setting",
        indextemplate="pair: %s; setting",
    )
    app.add_crossref_type(
        directivename="templatetag",
        rolename="ttag",
        indextemplate="pair: %s; template tag",
    )
    app.add_crossref_type(
        directivename="templatefilter",
        rolename="tfilter",
        indextemplate="pair: %s; template filter",
    )
    app.add_crossref_type(
        directivename="fieldlookup",
        rolename="lookup",
        indextemplate="pair: %s; field lookup type",
    )
    app.add_description_unit(
        directivename="django-admin",
        rolename="djadmin",
        indextemplate="pair: %s; django-admin command",
        parse_node=parse_django_admin_node,
    )
    app.add_description_unit(
        directivename="django-admin-option",
        rolename="djadminopt",
        indextemplate="pair: %s; django-admin command-line option",
        parse_node=parse_django_adminopt_node,
    )
    app.add_config_value("django_next_version", "0.0", True)
    app.add_directive("versionadded", VersionDirective)
    app.add_directive("versionchanged", VersionDirective)
    app.add_builder(DjangoStandaloneHTMLBuilder)

    # register the snippet directive
    app.add_directive("snippet", SnippetWithFilename)
    # register a node for snippet directive so that the xml parser
    # knows how to handle the enter/exit parsing event
    app.add_node(
        snippet_with_filename,
        html=(visit_snippet, depart_snippet_literal),
        latex=(visit_snippet_latex, depart_snippet_latex),
        man=(visit_snippet_literal, depart_snippet_literal),
        text=(visit_snippet_literal, depart_snippet_literal),
        texinfo=(visit_snippet_literal, depart_snippet_literal),
    )


class snippet_with_filename(nodes.literal_block):
    """
    Subclass the literal_block to override the visit/depart event handlers.
    """

    pass


def visit_snippet_literal(self, node):
    """
    default literal block handler.
    """
    self.visit_literal_block(node)


def depart_snippet_literal(self, node):
    """
    default literal block handler.
    """
    self.depart_literal_block(node)


def visit_snippet(self, node):
    """
    HTML document generator visit handler.
    """
    lang = self.highlightlang
    linenos = node.rawsource.count("\n") >= self.highlightlinenothreshold - 1
    fname = node["filename"]
    highlight_args = node.get("highlight_args", {})
    if "language" in node:
        # code-block directives
        lang = node["language"]
        highlight_args["force"] = True
    if "linenos" in node:
        linenos = node["linenos"]

    def warner(msg):
        self.builder.warn(msg, (self.builder.current_docname, node.line))

    highlighted = self.highlighter.highlight_block(node.rawsource, lang, warn=warner, linenos=linenos, **highlight_args)
    starttag = self.starttag(node, "div", suffix="", CLASS="highlight-%s" % lang)
    self.body.append(starttag)
    self.body.append('<div class="snippet-filename">%s</div>\n' % (fname,))
    self.body.append(highlighted)
    self.body.append("</div>\n")
    raise nodes.SkipNode


def visit_snippet_latex(self, node):
    """
    Latex document generator visit handler.
    """
    self.verbatim = ""


def depart_snippet_latex(self, node):
    """
    Latex document generator depart handler.
    """
    code = self.verbatim.rstrip("\n")
    lang = self.hlsettingstack[-1][0]
    linenos = code.count("\n") >= self.hlsettingstack[-1][1] - 1
    fname = node["filename"]
    highlight_args = node.get("highlight_args", {})
    if "language" in node:
        # code-block directives
        lang = node["language"]
        highlight_args["force"] = True
    if "linenos" in node:
        linenos = node["linenos"]

    def warner(msg):
        self.builder.warn(msg, (self.curfilestack[-1], node.line))

    hlcode = self.highlighter.highlight_block(code, lang, warn=warner, linenos=linenos, **highlight_args)

    self.body.append(
        "\n{\\colorbox[rgb]{0.9,0.9,0.9}" "{\\makebox[\\textwidth][l]" "{\\small\\texttt{%s}}}}\n" % (fname,)
    )

    if self.table:
        hlcode = hlcode.replace("\\begin{Verbatim}", "\\begin{OriginalVerbatim}")
        self.table.has_problematic = True
        self.table.has_verbatim = True

    hlcode = hlcode.rstrip()[:-14]  # strip \end{Verbatim}
    hlcode = hlcode.rstrip() + "\n"
    self.body.append("\n" + hlcode + "\\end{%sVerbatim}\n" % (self.table and "Original" or ""))
    self.verbatim = None


class SnippetWithFilename(Directive):
    """
    The 'snippet' directive that allows to add the filename (optional)
    of a code snippet in the document. This is modeled after CodeBlock.
    """

    has_content = True
    optional_arguments = 1
    option_spec = {"filename": directives.unchanged_required}

    def run(self):
        code = "\n".join(self.content)

        literal = snippet_with_filename(code, code)
        if self.arguments:
            literal["language"] = self.arguments[0]
        literal["filename"] = self.options["filename"]
        set_source_info(self, literal)
        return [literal]


class VersionDirective(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {}

    def run(self):
        if len(self.arguments) > 1:
            msg = """Error! Only one argument accepted for directive '{directive_name}::'.
            Comments should be provided as content,
            not as an extra argument.""".format(
                directive_name=self.name
            )
            raise self.error(msg)

        env = self.state.document.settings.env
        ret = []
        node = addnodes.versionmodified()
        ret.append(node)

        if self.arguments[0] == env.config.django_next_version:
            node["version"] = "Development version"
        else:
            node["version"] = self.arguments[0]

        node["type"] = self.name
        if self.content:
            self.state.nested_parse(self.content, self.content_offset, node)
        env.note_versionchange(node["type"], node["version"], node, self.lineno)
        return ret


class DjangoHTMLTranslator(SmartyPantsHTMLTranslator):
    """
    Django-specific reST to HTML tweaks.
    """

    # Don't use border=1, which docutils does by default.
    def visit_table(self, node):
        self.context.append(self.compact_p)
        self.compact_p = True
        self._table_row_index = 0  # Needed by Sphinx
        self.body.append(self.starttag(node, "table", CLASS="docutils"))

    def depart_table(self, node):
        self.compact_p = self.context.pop()
        self.body.append("</table>\n")

    def visit_desc_parameterlist(self, node):
        self.body.append("(")  # by default sphinx puts <big> around the "("
        self.first_param = 1
        self.optional_param_level = 0
        self.param_separator = node.child_text_separator
        self.required_params_left = sum([isinstance(c, addnodes.desc_parameter) for c in node.children])

    def depart_desc_parameterlist(self, node):
        self.body.append(")")

    if sphinx_ver < "1.0.8":
        #
        # Don't apply smartypants to literal blocks
        #
        def visit_literal_block(self, node):
            self.no_smarty += 1
            SmartyPantsHTMLTranslator.visit_literal_block(self, node)

        def depart_literal_block(self, node):
            SmartyPantsHTMLTranslator.depart_literal_block(self, node)
            self.no_smarty -= 1

    #
    # Turn the "new in version" stuff (versionadded/versionchanged) into a
    # better callout -- the Sphinx default is just a little span,
    # which is a bit less obvious that I'd like.
    #
    # FIXME: these messages are all hardcoded in English. We need to change
    # that to accommodate other language docs, but I can't work out how to make
    # that work.
    #
    version_text = {
        "versionchanged": "Changed in Django %s",
        "versionadded": "New in Django %s",
    }

    def visit_versionmodified(self, node):
        self.body.append(self.starttag(node, "div", CLASS=node["type"]))
        version_text = self.version_text.get(node["type"])
        if version_text:
            title = "%s%s" % (version_text % node["version"], ":" if len(node) else ".")
            self.body.append('<span class="title">%s</span> ' % title)

    def depart_versionmodified(self, node):
        self.body.append("</div>\n")

    # Give each section a unique ID -- nice for custom CSS hooks
    def visit_section(self, node):
        old_ids = node.get("ids", [])
        node["ids"] = ["s-" + i for i in old_ids]
        node["ids"].extend(old_ids)
        SmartyPantsHTMLTranslator.visit_section(self, node)
        node["ids"] = old_ids


def parse_django_admin_node(env, sig, signode):
    command = sig.split(" ")[0]
    env._django_curr_admin_command = command
    title = "django-admin %s" % sig
    signode += addnodes.desc_name(title, title)
    return sig


def parse_django_adminopt_node(env, sig, signode):
    """A copy of sphinx.directives.CmdoptionDesc.parse_signature()"""
    from sphinx.domains.std import option_desc_re

    count = 0
    firstname = ""
    for m in option_desc_re.finditer(sig):
        optname, args = m.groups()
        if count:
            signode += addnodes.desc_addname(", ", ", ")
        signode += addnodes.desc_name(optname, optname)
        signode += addnodes.desc_addname(args, args)
        if not count:
            firstname = optname
        count += 1
    if not count:
        for m in simple_option_desc_re.finditer(sig):
            optname, args = m.groups()
            if count:
                signode += addnodes.desc_addname(", ", ", ")
            signode += addnodes.desc_name(optname, optname)
            signode += addnodes.desc_addname(args, args)
            if not count:
                firstname = optname
            count += 1
    if not firstname:
        raise ValueError
    return firstname


class DjangoStandaloneHTMLBuilder(StandaloneHTMLBuilder):
    """
    Subclass to add some extra things we need.
    """

    name = "djangohtml"

    def finish(self):
        super(DjangoStandaloneHTMLBuilder, self).finish()
        self.info(bold("writing templatebuiltins.js..."))
        xrefs = self.env.domaindata["std"]["objects"]
        templatebuiltins = {
            "ttags": [
                n for ((t, n), (loc, a)) in xrefs.items() if t == "templatetag" and loc == "ref/templates/builtins"
            ],
            "tfilters": [
                n for ((t, n), (loc, a)) in xrefs.items() if t == "templatefilter" and loc == "ref/templates/builtins"
            ],
        }
        outfilename = os.path.join(self.outdir, "templatebuiltins.js")
        with open(outfilename, "w") as fp:
            fp.write("var django_template_builtins = ")
            json.dump(templatebuiltins, fp)
            fp.write(";\n")
