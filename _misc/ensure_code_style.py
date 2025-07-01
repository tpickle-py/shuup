import argparse
import ast
import sys
from itertools import chain

from sanity_utils import IGNORED_DIRS, XNodeVisitor, dotify_ast_name, find_files, get_assign_first_target

KNOWN_ACRONYMS = ("SKU", "GTIN", "URL", "IP")


class ForeignKeyVisitor(XNodeVisitor):
    def __init__(self):
        self.errors = []

    def visit_call(self, node, parents):
        name = dotify_ast_name(node.func)
        if any(name.endswith(suffix) for suffix in ("ForeignKey", "FilerFileField", "FilerImageField")):
            kwmap = {kw.arg: kw.value for kw in node.keywords}
            if "on_delete" not in kwmap:
                self.errors.append(f"Error! {node.lineno}: {name} call missing explicit `on_delete`.")


class VerboseNameVisitor(XNodeVisitor):
    def __init__(self):
        self.errors = []

    def visit_call(self, node, parents, context=None):  # noqa (N802)
        name = dotify_ast_name(node.func)
        if name == "InternalIdentifierField":
            return
        if name == "TranslatedFields":
            for kw in node.keywords:
                if isinstance(kw.value, ast.Call):
                    self.visit_call(kw.value, parents, context=kw.arg)
            return
        if not any(name.endswith(suffix) for suffix in ("ForeignKey", "Field")):
            return

        if not context:
            if isinstance(parents[-1], ast.Assign):
                context = get_assign_first_target(parents[-1])

        if context and (context.startswith("_") or context.endswith("data")):
            return

        kwmap = {kw.arg: kw.value for kw in node.keywords}

        kw_value = None
        needle = None
        for needle in ("verbose_name", "label"):
            kw_value = kwmap.get(needle)
            if kw_value:
                break
        if not kw_value:
            if node.kwargs:  # Assume dynamic use (has **kwargs)
                return
            self.errors.append(f"Error! {node.lineno}: {name} call missing verbose_name or label (ctx: {context}).")
            return

        if isinstance(kw_value, ast.BinOp) and isinstance(kw_value.op, ast.Mod):
            # It's an interpolation operation; use the lvalue (probably the call)
            kw_value = kw_value.left

        if isinstance(kw_value, ast.Call) and dotify_ast_name(kw_value.func) == "_":
            arg = kw_value.args[0]
            if isinstance(arg, ast.Str) and needle == "verbose_name":
                if not arg.s[0].islower() and not any(arg.s.startswith(acronym) for acronym in KNOWN_ACRONYMS):
                    self.errors.append(
                        f"Error! {node.lineno}: {name} `{needle}` not lower-case (value: {arg.s!r}) (ctx: {context})."
                    )
            return

        if isinstance(kw_value, ast.Name):  # It's a variable
            return

        self.errors.append(f"Error! {node.lineno}: {name} `{needle}` present but not translatable (ctx: {context}).")


def process_file(path, checkers):
    with open(path, "rb") as fp:
        source = fp.read()
    for checker_class in checkers:
        ck = checker_class()
        ck.visit(ast.parse(source, path))
        for err in ck.errors:
            yield f"{checker_class.__name__}: {err}"


def create_parser():
    parser = argparse.ArgumentParser(description="Check code style with various validators")
    parser.add_argument(
        "--fks",
        action="store_true",
        help="check foreign keys"
    )
    parser.add_argument(
        "--vns",
        action="store_true",
        help="check verbose names"
    )
    parser.add_argument(
        "-f",
        "--file",
        dest="filenames",
        action="append",
        default=[],
        help="specific files to check"
    )
    parser.add_argument(
        "-d",
        "--dir",
        dest="dirnames",
        action="append",
        default=[],
        help="directories to check"
    )
    parser.add_argument(
        "-g",
        "--group",
        action="store_true",
        help="group errors by file"
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    
    # Build checkers list based on arguments
    checkers = []
    if args.fks:
        checkers.append(ForeignKeyVisitor)
    if args.vns:
        checkers.append(VerboseNameVisitor)
    
    # If no checkers specified, use all of them
    if not checkers:
        checkers = [ForeignKeyVisitor, VerboseNameVisitor]
    
    # If no directories specified, use current directory
    dirnames = args.dirnames if args.dirnames else ['.']
    
    error_count = 0
    all_filenames = chain(
        find_files(
            dirnames,
            allowed_extensions=(".py",),
            ignored_dirs=IGNORED_DIRS + ["migrations"],
        ),
        args.filenames,
    )
    
    for filename in all_filenames:
        file_errors = list(process_file(filename, checkers))
        if not file_errors:
            continue
        if args.group:
            print(f"{filename}:", file=sys.stderr)
            for error in file_errors:
                print(f"    {error}", file=sys.stderr)
                error_count += 1
            continue
        for error in file_errors:
            print(f"{filename}:{error}", file=sys.stderr)
            error_count += 1

    print("###########################")  # noqa
    print(f"Total errors to handle: {error_count}")
    print("###########################")  # noqa



if __name__ == "__main__":
    main()
