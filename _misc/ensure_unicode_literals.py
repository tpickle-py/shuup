# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import argparse
import re
from ast import BinOp, Mod, parse

from sanity_utils import XNodeVisitor, find_files
from six import text_type

encoding_comment_regexp = re.compile(r"^#.+coding[=:]\s*([-\w.]+).+$", re.MULTILINE | re.I)


class StringVisitor(XNodeVisitor):
    def __init__(self):
        self.texts = set()
        self.formattees = set()

    def visit_Str(self, node, parents):  # noqa (N802)
        s = text_type(node.s)
        is_being_formatted = parents and isinstance(parents[-1], BinOp) and isinstance(parents[-1].op, Mod)
        if is_being_formatted:
            self.formattees.add(s)
            return
        if not ("\n" in s or s.islower() or s.isupper()):  # Doesn't look like a constant or docstring
            if " " in s.strip():  # Has spaces, that's texty
                if "%" in s or not all(32 <= ord(c) < 127 for c in s):  # Has a formatting character or is non-ascii
                    self.texts.add(s)

    def get_stats(self):
        stat_bits = []
        if self.texts:
            stat_bits.append(f"{len(self.texts)} text-like strings")
        if self.formattees:
            stat_bits.append(f"{len(self.formattees)} formattee strings")
        return ", ".join(stat_bits)

    def needs_fix(self):
        return bool(self.texts or self.formattees)


def process_file(path):
    sv = StringVisitor()
    with open(path, "rb") as fp:
        source = fp.read()
    if b"unicode_literals" not in source:
        sv.visit(parse(source, path))
    return sv


def fix_file(path):
    with open(path, "rb") as fp:
        source = fp.read().decode("utf-8")
        source_lines = source.splitlines()

    need_encoding_comment = any(ord(c) > 127 for c in source)
    first_non_comment_line_index = 0
    for line_index, line in enumerate(source_lines):
        if not line.strip():
            continue
        if encoding_comment_regexp.match(line):
            need_encoding_comment = False
        if not line.startswith("#"):
            first_non_comment_line_index = line_index
            break

    if "" not in source:
        source_lines.insert(first_non_comment_line_index, "")

    source = "\n".join(source_lines)
    if need_encoding_comment:
        source = "# -*- coding: utf-8 -*-\n" + source

    with open(path, "wb") as fp:
        fp.write(source.encode("utf-8"))
        fp.write(b"\n")


def gather_files(dirnames, filenames):
    files_to_process = []
    files_to_process.extend(filename for filename in filenames if filename.endswith(".py"))
    files_to_process.extend(find_files(dirnames, allowed_extensions=(".py",)))
    return files_to_process


def command(filenames, dirnames, fix):
    for filename in gather_files(dirnames, filenames):
        visitor = process_file(filename)
        if visitor.needs_fix():
            print(f"{filename}: {visitor.get_stats()}")
            if fix:
                print(f"Fixing: {filename}")  # noqa
                fix_file(filename)


def main():
    parser = argparse.ArgumentParser(description="Ensure unicode literals in Python files.")
    parser.add_argument("-f", "--file", type=str, nargs="*", help="Files to process.")
    parser.add_argument("-d", "--dir", type=str, nargs="*", help="Directories to search for files.")
    parser.add_argument("--fix", action="store_true", help="Fix the files by adding unicode literals.")
    args = parser.parse_args()
    command(args.filenames, args.dirnames, args.fix)


if __name__ == "__main__":
    main()
