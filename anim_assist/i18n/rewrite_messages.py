"""Offline migration of display expressions to translatable templates.

Only explicitly named files and UI/message boundaries are written. Technical
metadata, logging, operator arguments, identifiers and data names are unchanged.
The runtime does not import this utility.
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MESSAGE_ARGUMENTS = {"report": 1, "poll_message_set": 0,
                     "header_text_set": 0, "status_text_set": 0}
UI_CALLS = {"label", "operator", "operator_menu_enum", "prop", "menu", "popover", "column"}
DISPLAY_FUNCTIONS = {"description", "_aa_short", "_unavailable", "_switch_unavailable", "_module_reason"}


def translated(node):
    if user_data(node):
        return True  # A data value is already safe display text, not a message key.
    if isinstance(node, ast.IfExp):
        return translated(node.body) and translated(node.orelse)
    if isinstance(node, ast.Constant) and node.value in ("", None):
        return True
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"T", "F"}


def user_data(node):
    if isinstance(node, ast.Attribute):
        return node.attr in {"name", "label", "bone_name", "object_name", "action_name", "data_path", "expression",
                             "prop_path", "constraint_name", "filepath"}
    if isinstance(node, ast.Name):
        return node.id == "name" or node.id.endswith(("_name", "_path", "_id"))
    if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
        return node.slice.value in {"name", "id", "bone", "shape_key", "data_path", "path", "expression"}
    return False


def display_expression(node, source):
    """Return source for an equivalent English display expression using T/F."""
    get = lambda item: ast.get_source_segment(source, item)
    if translated(node):
        return get(node)
    if isinstance(node, ast.Constant):
        return "T(" + repr(node.value) + ")" if isinstance(node.value, str) and node.value else get(node)
    if isinstance(node, ast.IfExp):
        return "(" + display_expression(node.body, source) + " if " + get(node.test) + " else " + display_expression(node.orelse, source) + ")"
    if isinstance(node, ast.JoinedStr):
        values = []

        def string_parts(parts):
            output = ""
            for value in parts:
                if isinstance(value, ast.Constant):
                    output += value.value.replace("{", "{{").replace("}", "}}")
                elif isinstance(value, ast.FormattedValue):
                    key = "p" + str(len(values))
                    # Format each original field before evaluating the next one,
                    # exactly as an f-string does. The translated template may
                    # reorder these finished strings without touching user data.
                    formatted = ast.unparse(ast.JoinedStr(values=[value]))
                    values.append((key, formatted))
                    output += "{" + key + "}"
            return output

        template = string_parts(node.values)
        return "F(" + repr(template) + "".join(", " + key + "=" + value for key, value in values) + ")"
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format":
        if isinstance(node.func.value, ast.Constant) and isinstance(node.func.value.value, str):
            args = [get(value) for value in node.args]
            args += [(kw.arg + "=" if kw.arg else "**") + get(kw.value) for kw in node.keywords]
            return "F(" + repr(node.func.value.value) + (", " + ", ".join(args) if args else "") + ")"
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
            return "(T(" + repr(node.left.value) + ") % " + get(node.right) + ")"
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        parts = []

        def split(part):
            if isinstance(part, ast.BinOp) and isinstance(part.op, ast.Add):
                split(part.left)
                split(part.right)
            else:
                parts.append(part)

        split(node)
        # A complete sentence template permits natural target-language order.
        template, values = "", []
        for part in parts:
            if isinstance(part, ast.Constant) and isinstance(part.value, str):
                template += part.value.replace("{", "{{").replace("}", "}}")
            else:
                key = "p" + str(len(values))
                template += "{" + key + "}"
                values.append((key, get(part)))
        if any(isinstance(part, ast.Constant) and isinstance(part.value, str) for part in parts):
            return "F(" + repr(template) + "".join(", " + key + "=" + value for key, value in values) + ")"
    # A report variable is already a complete message; never inspect/rename data.
    return "T(" + get(node) + ")"


def rewrite(source, *, relative_import="..i18n"):
    tree = ast.parse(source)
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    selected = set()
    literal_flags = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", getattr(node.func, "id", ""))
            if name in MESSAGE_ARGUMENTS and len(node.args) > MESSAGE_ARGUMENTS[name]:
                candidate = node.args[MESSAGE_ARGUMENTS[name]]
                if not translated(candidate):
                    selected.add(candidate)
            if name in UI_CALLS:
                for kw in node.keywords:
                    # Native literal text is translated by Blender's registry.
                    # Object names and other variable labels remain user data.
                    if kw.arg in {"text", "heading"}:
                        needs_template = isinstance(kw.value, (ast.JoinedStr, ast.BinOp, ast.IfExp)) and not translated(kw.value)
                        if needs_template:
                            selected.add(kw.value)
                        if kw.arg == "text" and name in {"label", "operator", "operator_menu_enum", "prop", "menu", "popover"}:
                            # T/F already localize the caption. Native gettext
                            # must not translate it or an inserted user name again.
                            already_localized = translated(kw.value) and not isinstance(kw.value, ast.Constant)
                            if needs_template or already_localized or user_data(kw.value):
                                existing = next((item for item in node.keywords if item.arg == "translate"), None)
                                if existing is None:
                                    literal_flags.append((node, None))
                                elif not (isinstance(existing.value, ast.Constant) and existing.value.value is False):
                                    literal_flags.append((node, existing.value))
            if name == "wrapped_label" and len(node.args) > 2 and not translated(node.args[2]):
                if isinstance(node.args[2], (ast.JoinedStr, ast.BinOp, ast.IfExp)):
                    selected.add(node.args[2])
        elif isinstance(node, ast.Return) and node.value is not None:
            owner = parents.get(node)
            while owner is not None and not isinstance(owner, (ast.FunctionDef, ast.AsyncFunctionDef)):
                owner = parents.get(owner)
            if owner is not None and owner.name in DISPLAY_FUNCTIONS and not translated(node.value):
                if not isinstance(node.value, ast.Constant) or isinstance(node.value.value, str):
                    selected.add(node.value)
    # If a message boundary contains another selected node, rewrite only the outer expression.
    outer = []
    for node in selected:
        parent = parents.get(node)
        while parent is not None and parent not in selected:
            parent = parents.get(parent)
        if parent is None:
            outer.append(node)
    lines = source.splitlines(keepends=True)
    offsets, total = [], 0
    for line in lines:
        offsets.append(total)
        total += len(line)

    def offset(line, column):
        # AST columns count UTF-8 bytes; Python string positions count code points.
        return offsets[line - 1] + len(lines[line - 1].encode("utf-8")[:column].decode("utf-8"))

    changes = []
    for node in outer:
        old = ast.get_source_segment(source, node)
        new = display_expression(node, source)
        if old != new:
            changes.append((offset(node.lineno, node.col_offset), offset(node.end_lineno, node.end_col_offset), new))
    for call, current in literal_flags:
        if current is not None:
            changes.append((offset(current.lineno, current.col_offset), offset(current.end_lineno, current.end_col_offset), "False"))
        else:
            end = offset(call.end_lineno, call.end_col_offset) - 1
            separator = "" if source[:end].rstrip().endswith(",") else ", "
            changes.append((end, end, separator + "translate=False"))
    for start, end, replacement in sorted(changes, reverse=True):
        source = source[:start] + replacement + source[end:]
    import_line = "from " + relative_import + " import T, F"
    requires_lookup = any("T(" in replacement or "F(" in replacement for _start, _end, replacement in changes)
    if requires_lookup and import_line not in source:
        tree = ast.parse(source)
        # Module docstring and future imports must remain first.
        index = 0
        for node in tree.body:
            if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)) or (
                    isinstance(node, ast.ImportFrom) and node.module == "__future__"):
                index = node.end_lineno
            else:
                break
        lines = source.splitlines(keepends=True)
        lines.insert(index, "\n" + import_line + "\n")
        source = "".join(lines)
    ast.parse(source)
    return source, len(changes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Exact add-on-relative source paths")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    for relative in args.paths:
        target = (ROOT / relative).resolve()
        if not target.is_relative_to(ROOT) or target.suffix != ".py" or "i18n" in target.relative_to(ROOT).parts:
            raise SystemExit("Only explicitly named add-on source files can be migrated.")
        source = target.read_text(encoding="utf-8-sig")
        depth = len(target.relative_to(ROOT).parts) - 1
        relative_import = "." * (depth + 1) + "i18n"
        replacement, count = rewrite(source, relative_import=relative_import)
        if args.write and count:
            target.write_text(replacement, encoding="utf-8", newline="\n")
        print(f"{relative}: {count} display expressions")
