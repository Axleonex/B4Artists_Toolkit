"""An English template migration must preserve inserted data and evaluation order."""

import importlib.util
import ast
from pathlib import Path
import subprocess
import sys
import unittest
import uuid
import types


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tool = load("aa_message_migration", ROOT / "i18n" / "rewrite_messages.py")
i18n = load("aa_message_runtime", ROOT / "i18n" / "__init__.py")


class MessageMigrationTests(unittest.TestCase):
    def test_formatted_data_and_nested_precision_stay_equivalent(self):
        source = '''def show(layout, name, value, precision):
    layout.label(text=f"Selected {name!r}: {value:.{precision}f}")
'''
        migrated, count = tool.rewrite(source)
        self.assertEqual(count, 2)  # Template plus native-translation protection.
        results = []
        namespace = {"T": i18n.T, "F": i18n.F}
        # Remove the relative import only for this isolated expression test.
        exec(migrated.replace("from ..i18n import T, F", ""), namespace)
        layout = type("Layout", (), {"label": lambda _self, **kw: results.append(kw["text"])})()
        namespace["show"](layout, "Bone.L", 1.234, 2)
        self.assertEqual(results, ["Selected 'Bone.L': 1.23"])

    def test_technical_arguments_and_user_names_are_untouched(self):
        source = '''def show(layout, obj):
    layout.label(text=obj.name)
    op = layout.operator("animassist.match", text="Match")
    op.bone_name = f"{obj.name}.L"
'''
        migrated, count = tool.rewrite(source)
        self.assertEqual(count, 1)
        self.assertIn("text=obj.name, translate=False", migrated)
        self.assertIn('op.bone_name = f"{obj.name}.L"', migrated)
        self.assertIn('layout.operator("animassist.match", text="Match")', migrated)
        self.assertNotIn("import T, F", migrated)

    def test_repeated_migration_is_idempotent(self):
        source = 'def show(self, count):\n    self.report({"INFO"}, f"Moved {count} keys")\n'
        migrated, count = tool.rewrite(source)
        self.assertEqual(count, 1)
        repeated, count = tool.rewrite(migrated)
        self.assertEqual(count, 0)
        self.assertEqual(repeated, migrated)

    def test_condition_and_concatenation_use_complete_templates(self):
        source = 'def description(cls, context, props):\n    return "Select " + props.name if props.enabled else "Enable the tool"\n'
        migrated, count = tool.rewrite(source)
        self.assertEqual(count, 1)
        self.assertIn("F('Select {p0}', p0=props.name)", migrated)
        self.assertIn("T('Enable the tool')", migrated)

    def test_field_conversion_order_matches_original_fstring(self):
        source = '''def show(layout, value, events):
    layout.label(text=f"{value!r}: {events.append('second') or len(events)}")
'''
        migrated, count = tool.rewrite(source)
        self.assertEqual(count, 2)
        events = []

        class Value:
            def __repr__(self):
                events.append("repr")
                return "Bone.L"

        outputs = []
        namespace = {"T": i18n.T, "F": i18n.F}
        exec(migrated.replace("from ..i18n import T, F", ""), namespace)
        layout = type("Layout", (), {"label": lambda _self, **kw: outputs.append(kw["text"])})()
        namespace["show"](layout, Value(), events)
        self.assertEqual(events, ["repr", "second"])
        self.assertEqual(outputs, ["Bone.L: 2"])

    def test_import_depth_for_root_and_nested_modules(self):
        source = 'def show(self):\n    self.report({"INFO"}, "Done")\n'
        prefix = "_i18n_cli_test_" + uuid.uuid4().hex
        root_file = ROOT / (prefix + ".py")
        directory = ROOT / prefix
        nested = directory / "nested"
        deep_file = nested / "module.py"
        self.assertTrue(root_file.resolve().is_relative_to(ROOT.resolve()))
        self.assertTrue(nested.resolve().is_relative_to(ROOT.resolve()))
        try:
            nested.mkdir(parents=True)
            root_file.write_text(source, encoding="utf-8")
            deep_file.write_text(source, encoding="utf-8")
            command = [sys.executable, "-B", "-X", "utf8", str(ROOT / "i18n" / "rewrite_messages.py"),
                       "--write", root_file.relative_to(ROOT).as_posix(), deep_file.relative_to(ROOT).as_posix()]
            completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("from .i18n import T, F", root_file.read_text(encoding="utf-8"))
            self.assertIn("from ...i18n import T, F", deep_file.read_text(encoding="utf-8"))
        finally:
            root_file.unlink(missing_ok=True)
            deep_file.unlink(missing_ok=True)
            if nested.exists():
                nested.rmdir()
            if directory.exists():
                directory.rmdir()

    def test_wrapped_labels_translate_before_wrapping(self):
        source = 'def show(layout, context, name):\n    wrapped_label(layout, context, f"Owner: {name}")\n'
        migrated, count = tool.rewrite(source)
        self.assertEqual(count, 1)
        self.assertIn("F('Owner: {p0}'", migrated)

    def test_conditional_migration_is_idempotent(self):
        source = 'def show(layout, context, value):\n    wrapped_label(layout, context, f"Value: {value:.2f}" if value else "No value")\n'
        migrated, count = tool.rewrite(source)
        self.assertEqual(count, 1)
        repeated, count = tool.rewrite(migrated)
        self.assertEqual(count, 0)
        self.assertEqual(repeated, migrated)

    def test_native_labels_do_not_retranslate_inserted_data(self):
        source = 'def show(layout, obj):\n    layout.label(text=obj.name)\n    layout.label(text=f"Owner: {obj.name}")\n'
        migrated, _count = tool.rewrite(source)
        outputs = []
        old_language = i18n.active_language
        i18n.active_language = lambda context=None: "ja"
        i18n._catalogs["ja"] = {"Owner: {p0}": "所有者: {p0}", "Settings": "設定"}

        class Layout:
            def label(self, *, text, translate=True):
                outputs.append(i18n.T(text) if translate else text)

        namespace = {"T": i18n.T, "F": i18n.F}
        try:
            exec(migrated.replace("from ..i18n import T, F", ""), namespace)
            namespace["show"](Layout(), types.SimpleNamespace(name="Settings"))
            self.assertEqual(outputs, ["Settings", "所有者: Settings"])
        finally:
            i18n.active_language = old_language
            i18n._catalogs.clear()

    def test_conditional_user_data_names_stay_literal(self):
        source = 'def show(layout, obj, other, enabled):\n    layout.label(text=obj.name if enabled else other.name)\n    layout.label(text=obj.name if enabled else "")\n    layout.label(text=obj.name if enabled else "No owner")\n'
        migrated, _count = tool.rewrite(source)
        repeated, count = tool.rewrite(migrated)
        self.assertEqual(count, 0)
        self.assertEqual(repeated, migrated)
        self.assertNotIn("T(obj.name)", migrated)
        outputs = []
        old_language = i18n.active_language
        i18n.active_language = lambda context=None: "ja"
        i18n._catalogs["ja"] = {"Settings": "設定", "Frame": "フレーム", "No owner": "所有者なし"}

        class Layout:
            def label(self, *, text, translate=True):
                outputs.append(i18n.T(text) if translate else text)

        namespace = {"T": i18n.T, "F": i18n.F}
        try:
            exec(migrated.replace("from ..i18n import T, F", ""), namespace)
            namespace["show"](Layout(), types.SimpleNamespace(name="Settings"), types.SimpleNamespace(name="Frame"), True)
            self.assertEqual(outputs, ["Settings", "Settings", "Settings"])
            outputs.clear()
            namespace["show"](Layout(), types.SimpleNamespace(name="Settings"), types.SimpleNamespace(name="Frame"), False)
            self.assertEqual(outputs, ["Frame", "", "所有者なし"])
        finally:
            i18n.active_language = old_language
            i18n._catalogs.clear()

    def test_actual_section_header_translates_before_native_drawing(self):
        source = ast.parse((ROOT / "ui" / "ui_helpers.py").read_text(encoding="utf-8"))
        function = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == "section_header")
        future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
        module = ast.fix_missing_locations(ast.Module(body=[future, function], type_ignores=[]))
        outputs = []

        class Layout:
            def row(self, **kwargs):
                return self

            def label(self, **kwargs):
                outputs.append(kwargs)

        namespace = {"T": lambda text: {"Primary Actions": "基本操作"}.get(text, text)}
        exec(compile(module, "actual_section_header", "exec"), namespace)
        namespace["section_header"](Layout(), "Primary Actions")
        self.assertEqual(outputs, [{"text": "基本操作", "translate": False}])


if __name__ == "__main__":
    unittest.main()
