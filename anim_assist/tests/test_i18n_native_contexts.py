"""Owned captions must not inherit a host word with an unrelated meaning."""

import ast
import importlib.util
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("aa_native_context_extract", ROOT / "i18n/extract.py")
extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor)


NATIVE_METHODS = {'popover', 'operator_menu_enum', 'operator', 'prop_menu_enum', 'row', 'column', 'prop_search', 'prop_enum', 'label', 'prop', 'menu'}

def context_violations(root, paths):
    """Audit exact native metadata offline. Actual host drawing is checked separately."""
    issues = []
    counts = {'properties': 0, 'captions': 0, 'prelocalized_or_data': 0}
    for path in paths:
        rel = path.relative_to(root).as_posix()
        tree = ast.parse(path.read_text(encoding='utf-8-sig'))
        parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, 'id', '')
            kw = {k.arg: k.value for k in node.keywords}

            def literal(value):
                try:
                    return ast.literal_eval(value)
                except (TypeError, ValueError):
                    return None
            if name.endswith('Property'):
                counts['properties'] += 1
                expected = 'AnimAssist'
                owner = parents.get(node)
                target = getattr(getattr(owner, 'target', None), 'id', '')
                if rel == 'ui/timeline_settings.py' and target == 'layout_choice':
                    expected = 'AnimAssist.UserLayoutName'
                if rel == 'operators/p10_shelf_ops.py' and target == 'tool_enum':
                    expected = 'AnimAssist.ToolChoices'
                if rel == 'operators/driver_ops.py' and 'items' in kw:
                    items = ast.unparse(kw['items'])
                    if items == '_MODIFIER_TYPES':
                        expected = 'Action'
                    elif 'graph.handle_type' in items:
                        expected = '*'
                if literal(kw.get('translation_context')) != expected:
                    issues.append([rel, node.lineno, 'property', name, expected, literal(kw.get('translation_context'))])
            if isinstance(node.func, ast.Attribute) and name in NATIVE_METHODS:
                for caption in ('text', 'heading'):
                    if caption not in kw or (isinstance(kw[caption], ast.Constant) and (not kw[caption].value)):
                        continue
                    if literal(kw.get('translate')) is False:
                        counts['prelocalized_or_data'] += 1
                        continue
                    counts['captions'] += 1
                    context = 'heading_ctxt' if caption == 'heading' else 'text_ctxt'
                    if literal(kw.get(context)) != 'AnimAssist':
                        issues.append([rel, node.lineno, 'caption', name, 'AnimAssist', literal(kw.get(context))])
    return {'violations': issues, 'counts': counts}

class NativeContextTests(unittest.TestCase):
    def test_all_nonoperator_native_metadata_has_owned_or_protected_contexts(self):
        # The isolated operators writer has separate ownership. Integration can
        # call context_violations(ROOT, all_runtime_paths) with the same guard.
        paths = [path for path in ROOT.rglob("*.py")
                 if not {"i18n", "tests", "operators"} & set(path.relative_to(ROOT).parts)]
        result = context_violations(ROOT, paths)
        self.assertEqual(result["violations"], [])
        self.assertGreater(result["counts"]["properties"], 400)
        self.assertGreater(result["counts"]["captions"], 400)

    def test_guard_rejects_shared_captions_but_preserves_literal_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "fixture.py"
            path.write_text('''
value: FloatProperty(name="Bias", default=0.5)
layout.label(text="Key Color")
layout.label(text=object.name, translate=False)
layout.label(text=F("Count: {count}", count=3), translate=False)
''', encoding="utf-8")
            result = context_violations(root, [path])
            self.assertEqual(len(result["violations"]), 2)
            self.assertEqual(result["counts"]["prelocalized_or_data"], 2)

    def test_guard_retains_actual_provider_and_empty_data_contexts(self):
        fixtures = {
            "operators/driver_ops.py": '''
modifier: EnumProperty(items=_MODIFIER_TYPES, translation_context="Action")
handle: EnumProperty(items=tuple((i.identifier, i.name, i.description)
                    for i in bpy.ops.graph.handle_type.get_rna_type().properties["type"].enum_items),
                    translation_context="*")
''',
            "operators/p10_shelf_ops.py": '''
tool_enum: EnumProperty(items=_get_tool_items, translation_context="AnimAssist.ToolChoices")
''',
            "ui/timeline_settings.py": '''
layout_choice: EnumProperty(items=_choices, translation_context="AnimAssist.UserLayoutName")
''',
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for rel, source in fixtures.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source, encoding="utf-8")
                paths.append(path)
            result = context_violations(root, paths)
            self.assertEqual(result["violations"], [])
            self.assertEqual(result["counts"]["properties"], 4)

    def extract(self, source):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "fixture.py").write_text(source, encoding="utf-8")
            with patch.object(extractor, "help_records", return_value=[]):
                return {entry["msgid"]: entry for entry in extractor.extract(root)["entries"]}

    def test_owned_caption_contexts_do_not_replace_native_tip_context(self):
        entries = self.extract('''
class Example(Panel):
    """Native explanation."""
    bl_label = "Key Color"
    value: EnumProperty(name="Output", description="Property explanation.",
                        translation_context="AnimAssist",
                        items=[("KEEP", "Keep", "Enum explanation.")])
layout.label(text="Key Color", text_ctxt="AnimAssist")
layout.column(heading="Response", heading_ctxt="AnimAssist")
layout.operator("animassist.keep", text="Keep", text_ctxt="AnimAssist")
''')
        for caption in ("Key Color", "Output", "Keep", "Response"):
            self.assertEqual(entries[caption]["contexts"], ["AnimAssist"])
        for description in ("Native explanation.", "Property explanation.", "Enum explanation."):
            self.assertEqual(entries[description]["contexts"], ["*"])

    def test_provider_contexts_and_empty_user_namespace_remain_exact(self):
        entries = self.extract('''
modifier: EnumProperty(name="Modifier", translation_context="Action",
                       items=[("CYCLES", "Cycles", "Repeat the response.")])
handle: EnumProperty(name="Handles", translation_context="*",
                     items=[("AUTO", "Automatic", "Automatic handles.")])
saved: EnumProperty(name="Saved Layout", translation_context="AnimAssist.UserLayoutName",
                    description="Choose a saved layout.",
                    items=[("RAW", "Key Color", "User supplied data")])
layout.label(text="Key Color", translate=False)
''')
        self.assertEqual(entries["Cycles"]["contexts"], ["Action"])
        self.assertEqual(entries["Automatic"]["contexts"], ["*"])
        self.assertEqual(entries["Repeat the response."]["contexts"], ["*"])
        self.assertEqual(entries["Saved Layout"]["contexts"], [])
        self.assertEqual(entries["Key Color"]["contexts"], [])
        self.assertNotIn("User supplied data", entries)

    def test_actual_registration_sets_owned_context_without_changing_operator_help(self):
        source = ast.parse((ROOT / "core/explainers.py").read_text(encoding="utf-8"))
        function = next(node for node in source.body if isinstance(node, ast.FunctionDef)
                        and node.name == "register_class")
        calls = []
        operator_type = type("Operator", (), {})
        bpy = types.SimpleNamespace(types=types.SimpleNamespace(Operator=operator_type),
                                    utils=types.SimpleNamespace(register_class=lambda cls: calls.append(
                                        (cls, cls.bl_translation_context, getattr(cls, "bl_description", None)))))
        namespace = {"bpy": bpy, "OWN_CONTEXT": "AnimAssist", "_full": {}, "_by_idname": {},
                     "_original": lambda cls: cls.bl_description, "_describe": lambda *_args: "Help"}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "actual_registration", "exec"), namespace)
        example = type("Example", (operator_type,), {"bl_idname": "animassist.example",
                       "bl_label": "Key Color", "bl_description": "Canonical explanation"})
        namespace["register_class"](example)
        self.assertEqual(calls, [(example, "AnimAssist", "")])
        self.assertEqual(example.bl_label, "Key Color")
        self.assertEqual(example.bl_description, "Canonical explanation")
        self.assertIs(namespace["_by_idname"]["animassist.example"], example)
        panel = type("Panel", (), {"bl_label": "Driver & Target", "bl_description": "Panel explanation"})
        namespace["register_class"](panel)
        self.assertEqual(calls[-1], (panel, "AnimAssist", "Panel explanation"))


if __name__ == "__main__":
    unittest.main()
