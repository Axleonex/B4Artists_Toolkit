"""Offline source catalog extraction. Run with Python, never from draw().

The catalog includes native metadata and explicit custom-text boundaries. Source
references explain why each message is present. Stable IDs are not messages.
"""

from __future__ import annotations

import argparse
import ast
import copy
from collections import namedtuple
import importlib
import json
from pathlib import Path
from string import Formatter
import sys
import types
import uuid


ROOT = Path(__file__).resolve().parents[1]
OWN_CONTEXT = "AnimAssist"  # Matches the owned class registration boundary.
UI_CALLS = {"label", "operator", "operator_menu_enum", "operator_enum", "prop", "menu",
            "popover", "panel", "box", "column", "row", "split", "template_list"}
MESSAGE_CALLS = {"report": 1, "poll_message_set": 0, "header_text_set": 0, "status_text_set": 0,
                 "T": 0, "F": 0, "translate": 0, "wrapped_label": 2,
                 "section_header": 1, "subsection": 4, "format_text": 0,
                 "ValueError": 0, "RuntimeError": 0, "ValidationError": 0}
DISPLAY_MAPS = {"TIPS", "QUICK_LABELS", "ROW_LABELS", "ALL_ROW_LABELS", "_PLACES", "_NATIVE_NAMES", "SEARCH_TERMS", "_ISSUE_LABELS"}
CUSTOM_ENUM_CONTEXTS = {"AnimAssist.UserLayoutName", "AnimAssist.ToolChoices"}
HELPER_TEXT_ARGUMENTS = {"report_failure": (1, 2), "confirm_dialog": (3,), "draw_context_warning": (1,)}
# These helpers translate their display arguments, but their names are not
# translation APIs outside the verified modules that define or import them.
SCOPED_HELPER_TEXT_ARGUMENTS = {
    "ui/nla_panels.py": {"native": (2,), "timing": (2,), "options": (2,)},
    "ui/header_menus.py": {"timing": (2,)},
    "ui/timeline_overlay.py": {"_text": (1,)},
}
HELPER_TEXT_KEYWORDS = {
    "report_failure": {"what", "fix"}, "confirm_dialog": {"message"}, "draw_context_warning": {"message"},
    "wrapped_label": {"text"}, "section_header": {"label"}, "subsection": {"label"},
    "analysis_box": {"title"}, "danger_box": {"label"}, "scope_block": {"title"},
    "explained_op": {"text"}, "explained_prop": {"text"},
}


def literal(node):
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError):
        return None


def fields(text):
    try:
        return sorted(field + ("!" + conversion if conversion else "") + (":" + spec if spec else "")
                      for _part, field, spec, conversion in Formatter().parse(text) if field is not None)
    except ValueError:
        return []  # A literal brace in UI prose is not a format call.


def enum_records(value, path, root, cache, seen=frozenset(), local_bindings=None):
    """Follow actual enum consumers through source bindings, without imports."""
    if not isinstance(value, ast.AST):
        return
    path = path.resolve()
    identity = (path, getattr(value, "lineno", 0), ast.dump(value))
    if identity in seen or not path.is_relative_to(root.resolve()):
        return
    seen = seen | {identity}
    if path not in cache:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        bindings, imports = {}, {}
        for statement in tree.body:
            if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
                for target in targets:
                    if isinstance(target, ast.Name):
                        bindings[target.id] = statement.value
            elif isinstance(statement, ast.FunctionDef):
                bindings[statement.name] = statement
            elif isinstance(statement, ast.ImportFrom) and statement.level:
                base = path.parent
                for _ in range(statement.level - 1):
                    base = base.parent
                for alias in statement.names:
                    module = base.joinpath(*(statement.module or "").split(".")) if statement.module else base / alias.name
                    package_member = bool(statement.module and module.is_dir())
                    target = (module / alias.name).with_suffix(".py") if package_member else module.with_suffix(".py")
                    if target.is_file():
                        imports[alias.asname or alias.name] = (target, alias.name if statement.module and not package_member else None)
        cache[path] = bindings, imports
    bindings, imports = cache[path]
    if isinstance(value, ast.Name):
        if getattr(value, "_enum_module_scope", False):
            local_bindings = None
        if value.id in (local_bindings or {}):
            yield from enum_records(local_bindings[value.id], path, root, cache, seen, local_bindings)
        elif value.id in bindings:
            yield from enum_records(bindings[value.id], path, root, cache, seen)
        elif value.id in imports:
            imported, symbol = imports[value.id]
            if symbol:
                yield from enum_records(ast.Name(id=symbol), imported, root, cache, seen)
    elif isinstance(value, ast.Attribute) and isinstance(value.value, ast.Name) and value.value.id in imports:
        imported, symbol = imports[value.value.id]
        if symbol is None:
            yield from enum_records(ast.Name(id=value.attr), imported, root, cache, seen)
    elif isinstance(value, ast.FunctionDef):
        for statement in ast.walk(value):
            if isinstance(statement, ast.Return) and statement.value is not None:
                yield from enum_records(statement.value, path, root, cache, seen)
    elif isinstance(value, ast.Call):
        if isinstance(value.func, ast.Name) and value.func.id in {"tuple", "list"} and value.args:
            yield from enum_records(value.args[0], path, root, cache, seen, local_bindings)
        else:
            yield from enum_records(value.func, path, root, cache, seen, local_bindings)
    elif isinstance(value, ast.IfExp):
        yield from enum_records(value.body, path, root, cache, seen, local_bindings)
        yield from enum_records(value.orelse, path, root, cache, seen, local_bindings)
    elif isinstance(value, ast.Subscript):
        yield from enum_records(value.value, path, root, cache, seen, local_bindings)
    elif isinstance(value, (ast.List, ast.Tuple)):
        for row in value.elts:
            if isinstance(row, (ast.List, ast.Tuple)) and len(row.elts) >= 3:
                yield row.elts[1], row.elts[2], path.relative_to(root).as_posix()
    elif isinstance(value, (ast.ListComp, ast.GeneratorExp)):
        if isinstance(value.elt, (ast.List, ast.Tuple)) and len(value.elt.elts) >= 3:
            yield value.elt.elts[1], value.elt.elts[2], path.relative_to(root).as_posix()
        for generator in value.generators:
            yield from enum_records(generator.iter, path, root, cache, seen, local_bindings)


def class_value(value, bindings):
    """Freeze a class assignment's prior bindings, as Python does at that line."""
    if value is None:
        return None
    class BindNames(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id in bindings:
                return copy.deepcopy(bindings[node.id])
            node._enum_module_scope = True
            return node
    return BindNames().visit(copy.deepcopy(value))


def help_records(root=ROOT):
    """Read assembled English seed records offline, without loading the add-on.

    Seed modules contain only immutable records and registration functions. The
    synthetic registry rejects registration, so this never installs native UI.
    It also resolves the canonical English anchor hint used by composite help.
    """
    package = "_aa_catalog_" + uuid.uuid4().hex
    record_type = namedtuple("HelpRecord", "id label tooltip description phase category")
    parent = types.ModuleType(package)
    parent.__path__ = [str(root)]
    core = types.ModuleType(package + ".core")
    core.__path__ = [str(root / "core")]
    registry = types.ModuleType(package + ".core.help_registry")
    registry.HelpEntry = record_type

    def no_registration(*_args, **_kwargs):
        raise RuntimeError("Offline help extraction must not register UI")

    registry.register_phase_help = no_registration
    registry.unregister_phase_help = no_registration
    constants = types.ModuleType(package + ".constants")
    constants_source = ast.parse((root / "constants.py").read_text(encoding="utf-8-sig"))
    for node in constants_source.body:
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "BREAKDOWN_ANCHOR_HINT":
            constants.BREAKDOWN_ANCHOR_HINT = literal(node.value)
    sys.modules.update({package: parent, core.__name__: core, registry.__name__: registry,
                        constants.__name__: constants})
    records = []
    try:
        for path in sorted((root / "core").glob("help_phase*_entries.py")):
            module = importlib.import_module(package + ".core." + path.stem)
            tree = ast.parse(path.read_text(encoding="utf-8-sig"))
            lines = {}
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = getattr(node.func, "id", "")
                identifier = None
                if name == "_H" and node.args:
                    identifier = literal(node.args[0])
                elif name == "HelpEntry":
                    identifier = next((literal(kw.value) for kw in node.keywords if kw.arg == "id"), None)
                if isinstance(identifier, str):
                    lines[identifier] = node.lineno
            for name, values in vars(module).items():
                if name.endswith("_ENTRIES") and isinstance(values, (tuple, list)):
                    for record in values:
                        records.append((record._asdict(), path.relative_to(root).as_posix(), lines[record.id]))
        return records
    finally:
        for name in list(sys.modules):
            if name == package or name.startswith(package + "."):
                del sys.modules[name]


def extract(root=ROOT):
    root = root.resolve()
    entries = {}
    enum_cache = {}

    def add(node, path, kind, contexts=(), format_kind=None):
        value = node if isinstance(node, str) else literal(node)
        if not isinstance(value, str) or not value.strip():
            return
        entry = entries.setdefault(value, {"msgid": value, "contexts": set(), "sources": [],
                                            "placeholders": fields(value)})
        entry["contexts"].update(contexts)
        if format_kind:
            previous = entry.get("format")
            if previous and previous != format_kind:
                raise ValueError(f"Conflicting executable formats for {value!r}: {previous}, {format_kind}")
            entry["format"] = format_kind
        ref = {"path": path, "line": getattr(node, "lineno", 1), "kind": kind}
        if ref not in entry["sources"]:
            entry["sources"].append(ref)

    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        if rel.startswith("tests/") or (rel.startswith("i18n/") and rel != "i18n/__init__.py"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=rel)
        parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
        assignments = {}
        declarations = list(tree.body)
        declarations.extend(item for owner in tree.body if isinstance(owner, ast.ClassDef) for item in owner.body)
        for assignment in declarations:
            if isinstance(assignment, (ast.Assign, ast.AnnAssign)):
                targets = assignment.targets if isinstance(assignment, ast.Assign) else [assignment.target]
                for target in targets:
                    if isinstance(target, ast.Name):
                        assignments[target.id] = assignment.value

        def enum_items(value, contexts=("*",), local_bindings=None):
            for label, description, origin in enum_records(value, path, root, enum_cache, local_bindings=local_bindings):
                add(label, origin, "enum.label", contexts)
                add(description, origin, "enum.description", ("*",))

        def operator_class(owner):
            if not isinstance(owner, ast.ClassDef):
                return False
            if any("Operator" in getattr(base, "attr", getattr(base, "id", "")) for base in owner.bases):
                return True
            return any(isinstance(item, ast.Assign) and any(getattr(target, "id", "") == "bl_idname" for target in item.targets)
                       and isinstance(literal(item.value), str) and literal(item.value).startswith(("animassist.", "anim_assist."))
                       for item in owner.body)

        def custom_values(value, kind, format_kind=None, seen=frozenset()):
            # T may surround a dictionary lookup. Its values are captions; its
            # keys remain technical dispatch IDs. A list of UI strings is similar.
            if isinstance(value, ast.Name) and value.id in assignments:
                if value.id not in seen:
                    custom_values(assignments[value.id], kind, format_kind, seen | {value.id})
            elif isinstance(value, ast.IfExp):
                custom_values(value.body, kind, format_kind, seen)
                custom_values(value.orelse, kind, format_kind, seen)
            elif isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) and value.func.attr == "get":
                custom_values(value.func.value, kind, format_kind, seen)
                for default in value.args[1:]:
                    custom_values(default, kind, format_kind, seen)
            elif isinstance(value, ast.Dict):
                for item in value.values:
                    custom_values(item, kind, format_kind, seen)
            elif isinstance(value, (ast.List, ast.Tuple)):
                for item in value.elts:
                    custom_values(item, kind, format_kind, seen)
            else:
                add(value, rel, kind, format_kind=format_kind)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
                native_context = next((literal(kw.value) for kw in node.keywords
                                       if kw.arg == "text_ctxt"),
                                      "Operator" if name in {"operator", "operator_menu_enum", "operator_enum"} else "*")
                if name in MESSAGE_CALLS and len(node.args) > MESSAGE_CALLS[name]:
                    custom_values(node.args[MESSAGE_CALLS[name]], name,
                                  "brace" if name in {"F", "format_text"} or (name == "ValidationError" and node.keywords) else None)
                scoped = (SCOPED_HELPER_TEXT_ARGUMENTS.get(rel, {}).get(name, ())
                          if isinstance(node.func, ast.Name) else ())
                for index in HELPER_TEXT_ARGUMENTS.get(name, ()) + scoped:
                    if len(node.args) > index:
                        custom_values(node.args[index], "helper." + name)
                for keyword in node.keywords:
                    if keyword.arg in HELPER_TEXT_KEYWORDS.get(name, ()):
                        custom_values(keyword.value, "helper." + keyword.arg)
                if name == "ToolEntry":
                    for keyword in node.keywords:
                        if keyword.arg in {"label", "description", "category"}:
                            custom_values(keyword.value, "discovery." + keyword.arg)
                if (name == "from_template" and isinstance(node.func, ast.Attribute)
                        and getattr(node.func.value, "id", "") == "FallbackReason" and node.args):
                    custom_values(node.args[0], "backend.template", "brace")
                if name == "format" and isinstance(node.func, ast.Attribute):
                    source = node.func.value
                    if isinstance(source, ast.Call) and getattr(source.func, "id", "") in {"T", "translate"} and source.args:
                        custom_values(source.args[0], "translated.format", "brace")
                if name in {"Group", "_curve_menu"} and len(node.args) >= 2:
                    add(node.args[1], rel, "generated.label", (OWN_CONTEXT,))
                    if name == "_curve_menu" and len(node.args) >= 3:
                        add(node.args[2], rel, "generated.description", ("*",))
                if name in {"OffsetPreset", "BreakdownPreset", "TrajectoryPalette"}:
                    for kw in node.keywords:
                        if kw.arg in {"name", "label", "description"}:
                            add(kw.value, rel, "enum." + kw.arg, ("*",) if kw.arg == "description" else (OWN_CONTEXT,))
                        if name == "TrajectoryPalette" and kw.arg == "label" and isinstance(literal(kw.value), str):
                            add(ast.Constant(value=f"Use the {literal(kw.value)} colour scheme for trajectory overlays.",
                                             lineno=kw.value.lineno), rel, "enum.description", ("*",))
                if name.endswith("Property") or name in UI_CALLS or name in {"HelpEntry", "_H"}:
                    valid = {"name", "description"} if name.endswith("Property") else {"text", "heading"}
                    if name in {"HelpEntry", "_H"}:
                        valid = {"label", "tooltip", "description", "category"}
                    elif name in {"analysis_box", "danger_box", "scope_block"}:
                        valid = {"title", "label"}
                    for kw in node.keywords:
                        if kw.arg in valid:
                            kind = ("rna." if name.endswith("Property") else "help." if name in {"HelpEntry", "_H"} else "ui.") + kw.arg
                            property_context = next((literal(kw.value) for kw in node.keywords if kw.arg == "translation_context"), "*")
                            translated = next((literal(kw.value) for kw in node.keywords if kw.arg == "translate"), True)
                            caption_context = next((literal(item.value) for item in node.keywords
                                                    if item.arg == "heading_ctxt"), "*") if kw.arg == "heading" else native_context
                            native = () if name in {"HelpEntry", "_H"} or translated is False else (caption_context,)
                            if name.endswith("Property"):
                                native = ("*",) if kw.arg == "description" else (property_context,)
                                if property_context in CUSTOM_ENUM_CONTEXTS and kw.arg == "name":
                                    native = ()  # User-authored enum names share this deliberately empty namespace.
                            value = assignments.get(kw.value.id, kw.value) if isinstance(kw.value, ast.Name) else kw.value
                            add(value, rel, kind, native)
                        elif kw.arg == "items" and name.endswith("Property"):
                            context = next((literal(kw.value) for kw in node.keywords if kw.arg == "translation_context"), "*")
                            if context not in CUSTOM_ENUM_CONTEXTS:
                                value = kw.value
                                owner = parents.get(node)
                                while owner is not None and not isinstance(owner, ast.ClassDef):
                                    owner = parents.get(owner)
                                class_bindings = {}
                                for statement in getattr(owner, "body", ()):
                                    if statement.lineno >= node.lineno:
                                        break
                                    if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                                        targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
                                        for target in targets:
                                            if isinstance(target, ast.Name):
                                                class_bindings[target.id] = class_value(statement.value, class_bindings)
                                enum_items(value, (context,), class_bindings)
                if name == "_H":
                    # Positional HelpEntry helper: id, label, tooltip, description, category.
                    for field, item in zip(("label", "tooltip", "description", "category"), node.args[1:5]):
                        add(item, rel, "help." + field)
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                names = {getattr(target, "id", "") for target in targets}
                if names & {"bl_label", "bl_description", "bl_category"}:
                    owner = parents.get(node)
                    is_operator = operator_class(owner)
                    # Sidebar tabs use IFACE_(category_id), independent of the
                    # class context (interface_panel.cc). Class captions do not.
                    context = (OWN_CONTEXT,) if "bl_label" in names else ("*",)
                    if "bl_label" in names and isinstance(owner, ast.ClassDef):
                        explicit = next((literal(item.value) for item in owner.body if isinstance(item, ast.Assign)
                                         and any(getattr(target, "id", "") == "bl_translation_context" for target in item.targets)), None)
                        if isinstance(explicit, str):
                            context = (explicit,)
                    if is_operator and "bl_description" in names:
                        context = ()  # register_class owns callback help and empties static native description.
                    add(node.value, rel, "RNA", context)
                if any(name.startswith(("LABEL_", "VERB_", "AXIS_", "SECTION_")) for name in names):
                    add(node.value, rel, "vocabulary")
                if names & DISPLAY_MAPS and isinstance(node.value, ast.Dict):
                    for value in node.value.values:
                        add(value, rel, "display-map")
                if names & {"ACTIONS", "SLIDERS"} and isinstance(node.value, ast.Dict):
                    offset = 2 if "ACTIONS" in names else 0
                    for value in node.value.values:
                        if isinstance(value, (ast.Tuple, ast.List)):
                            add(value.elts[offset], rel, "toolbar.label", (OWN_CONTEXT,))
                if names & {"GROUPS", "STAGES", "MODES", "LANGUAGE_ITEMS"} and isinstance(node.value, (ast.Tuple, ast.List)):
                    for item in node.value.elts:
                        if isinstance(item, (ast.Tuple, ast.List)) and len(item.elts) >= 2:
                            add(item.elts[1], rel, "enum.label", (OWN_CONTEXT,))
                            if "GROUPS" in names and rel == "ui/timeline_catalog.py":
                                label = literal(item.elts[1])
                                if isinstance(label, str):
                                    add(ast.Constant(value=label + " Options", lineno=item.lineno), rel, "generated.label", (OWN_CONTEXT,))
                            if names & {"MODES", "LANGUAGE_ITEMS"} and len(item.elts) >= 3:
                                add(item.elts[2], rel, "enum.description", ("*",))
                if "_SCOPES" in names and isinstance(node.value, ast.Dict):
                    for values in node.value.values:
                        if isinstance(values, (ast.Tuple, ast.List)):
                            for value in values.elts:
                                add(value, rel, "command.scope")
                if names & {"BREAKDOWN_ANCHOR_HINT", "_SELECTED_KEY_SCOPE"}:
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        for value in node.value.elts:
                            add(value, rel, "command.scope")
                    else:
                        add(node.value, rel, "help")
                if "P12_STALE_SUFFIX" in names:
                    add(node.value, rel, "display.constant")
                if names & {"DRIVER_SECTIONS", "PIE_SLOTS", "PIE_KEYMAPS"} and isinstance(node.value, (ast.Tuple, ast.List)):
                    index = 2 if "PIE_KEYMAPS" in names else 1
                    for item in node.value.elts:
                        if isinstance(item, (ast.Tuple, ast.List)) and len(item.elts) > index:
                            add(item.elts[index], rel, "generated.label", (OWN_CONTEXT,))
                if "MENUS" in names and isinstance(node.value, ast.Dict):
                    for item in ast.walk(node.value):
                        if isinstance(item, (ast.Tuple, ast.List)) and len(item.elts) == 4:
                            add(item.elts[1], rel, "generated.label", (OWN_CONTEXT,))
                if "SIDEBARS" in names and isinstance(node.value, ast.Dict):
                    for value in node.value.values:
                        if isinstance(value, (ast.Tuple, ast.List)) and value.elts:
                            add(value.elts[0], rel, "generated.subtitle")
                if names & {"PROPERTIES_SUBTITLE"}:
                    add(node.value, rel, "generated.subtitle")
            elif isinstance(node, ast.FunctionDef) and node.name == "command_metadata":
                for assignment in ast.walk(node):
                    if isinstance(assignment, ast.Assign):
                        for target in assignment.targets:
                            if getattr(target, "id", "") in {"scope", "prerequisite", "gesture"}:
                                add(assignment.value, rel, "command.metadata")
                            elif isinstance(target, ast.Tuple):
                                if isinstance(assignment.value, ast.Tuple):
                                    for value in assignment.value.elts:
                                        add(value, rel, "command.metadata")
            elif isinstance(node, ast.FunctionDef) and node.name in HELPER_TEXT_KEYWORDS:
                for argument, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
                    if argument.arg in HELPER_TEXT_KEYWORDS[node.name] and default is not None:
                        custom_values(default, "helper.default")
            elif isinstance(node, ast.ClassDef) and operator_class(node):
                if not any(isinstance(item, ast.Assign) and any(getattr(target, "id", "") == "bl_description"
                           for target in item.targets) for item in node.body):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        add(node.body[0].value, rel, "operator.help")
                        raw = literal(node.body[0].value)
                        if isinstance(raw, str) and raw.strip() != raw:
                            add(ast.Constant(value=raw.strip(), lineno=node.body[0].lineno), rel, "operator.help.stripped")
            elif isinstance(node, ast.ClassDef):
                if any(getattr(base, "id", getattr(base, "attr", "")) in {"Menu", "Panel"} for base in node.bases):
                    if node.body and isinstance(node.body[0], ast.Expr) and not any(
                            isinstance(item, ast.Assign) and any(getattr(target, "id", "") == "bl_description" for target in item.targets)
                            for item in node.body):
                        add(node.body[0].value, rel, "native.description", ("*",))
            elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod) and isinstance(node.left, ast.Call):
                if getattr(node.left.func, "id", "") in {"T", "translate"} and node.left.args:
                    custom_values(node.left.args[0], "translated.percent", "percent")
            elif isinstance(node, (ast.For, ast.comprehension)):
                # Fixed, literal caption tables are safe to inspect. Never read
                # dynamic object collections or guess labels from technical IDs.
                target = node.target
                if isinstance(target, (ast.Tuple, ast.List)):
                    indices = [(index, item.id) for index, item in enumerate(target.elts)
                               if getattr(item, "id", "") in {"label", "text", "kt_name", "caption"}]
                    values = assignments.get(node.iter.id, node.iter) if isinstance(node.iter, ast.Name) else node.iter
                    if isinstance(values, (ast.Tuple, ast.List)):
                        for row in values.elts:
                            if isinstance(row, (ast.Tuple, ast.List)):
                                for index, variable in indices:
                                    if index < len(row.elts):
                                        contexts = set()
                                        for call in ast.walk(node):
                                            if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
                                                continue
                                            if call.func.attr not in UI_CALLS:
                                                continue
                                            keywords = {item.arg: item.value for item in call.keywords}
                                            if literal(keywords.get("translate")) is False:
                                                continue
                                            for field in ("text", "heading"):
                                                caption = keywords.get(field)
                                                if isinstance(caption, ast.Name) and caption.id == variable:
                                                    default = "Operator" if call.func.attr in {"operator", "operator_menu_enum"} else "*"
                                                    context_key = "heading_ctxt" if field == "heading" else "text_ctxt"
                                                    contexts.add(literal(keywords.get(context_key)) or default)
                                        add(row.elts[index], rel, "loop.caption", tuple(contexts))
    for record, path, line in help_records(root):
        for field in ("label", "tooltip", "description", "category"):
            existing = entries.get(record[field])
            if existing and any(source["path"] == path and source["kind"] == "help." + field
                                for source in existing["sources"]):
                continue  # The literal field already has its more precise source line.
            node = ast.Constant(value=record[field], lineno=line)
            add(node, path, "help." + field)
    dependencies = root / "i18n" / "native_dependencies.json"
    if dependencies.is_file():
        manifest = json.loads(dependencies.read_text(encoding="utf-8-sig"))
        if manifest.get("schema") != "toolkit.i18n.native-dependencies.v1":
            raise ValueError("Unsupported native dependency manifest")
        for dependency in manifest["entries"]:
            message = dependency["msgid"]
            if not isinstance(message, str) or not message:
                raise ValueError("Native dependency needs a nonempty source message")
            entry = entries.setdefault(message, {"msgid": message, "contexts": set(), "sources": [],
                                                  "placeholders": fields(message)})
            entry["contexts"].update(dependency["contexts"])
            for reference in dependency["native_sources"]:
                if reference["context"] not in dependency["contexts"]:
                    raise ValueError("Native dependency context disagrees with its source")
                if reference not in entry.setdefault("native_sources", []):
                    entry["native_sources"].append(reference)
    result = []
    for msgid in sorted(entries):
        entry = entries[msgid]
        entry["contexts"] = sorted(entry["contexts"])
        entry["sources"].sort(key=lambda source: (source["path"], source["line"], source["kind"]))
        if not entry["placeholders"]:
            del entry["placeholders"]  # Schema default []; no information is discarded.
        result.append(entry)
    return {"schema": "toolkit.i18n.catalog.v1", "entries": result}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = ROOT / "i18n" / "source_catalog.json"
    # Keep complete source references without a megabyte of indentation.
    # One entry per line also keeps catalog diffs reviewable.
    catalog = extract()
    text = '{"schema":"toolkit.i18n.catalog.v1","entries":[\n' + ",\n".join(
        json.dumps(entry, ensure_ascii=False, separators=(",", ":"))
        for entry in catalog["entries"]) + "\n]}\n"
    if args.check:
        if target.read_text(encoding="utf-8") != text:
            raise SystemExit("Source catalog is stale. Run i18n/extract.py.")
    else:
        target.write_text(text, encoding="utf-8", newline="\n")
    print(f"Catalog entries: {len(json.loads(text)['entries'])}")
