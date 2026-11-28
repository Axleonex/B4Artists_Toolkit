"""Source-backed checks for catalog coverage and real Timeline message wiring."""

import ast
import importlib.util
import json
from pathlib import Path
import types
import unittest
import tempfile
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


extractor = load("aa_source_catalog_checks", ROOT / "i18n" / "extract.py")
i18n = load("aa_source_message_checks", ROOT / "i18n" / "__init__.py")


class SourceContractTests(unittest.TestCase):
    def test_actual_native_default_captions(self):
        fixture = json.loads((ROOT / "tests/fixtures/native_default_captions.json").read_text(encoding="utf-8"))
        entries = {entry["msgid"]: entry for entry in extractor.extract()["entries"]}
        self.assertEqual(len(fixture["rows"]), 20)
        self.assertEqual(len({row["effective_name"] for row in fixture["rows"]}), 14)
        source_trees = {}
        for row in fixture["rows"]:
            with self.subTest(owner=row["class"], property=row["target"]):
                self.assertEqual(row["effective_name"], row["target"])
                self.assertFalse(row["is_hidden"])
                if row["path"] not in source_trees:
                    source_trees[row["path"]] = ast.parse((ROOT / row["path"]).read_text(encoding="utf-8-sig"))
                owner = next(node for node in ast.walk(source_trees[row["path"]])
                             if isinstance(node, ast.ClassDef) and node.name == row["class"])
                declaration = next(node for node in owner.body if isinstance(node, ast.AnnAssign)
                                   and isinstance(node.target, ast.Name) and node.target.id == row["target"])
                names = [keyword.value for keyword in declaration.annotation.keywords if keyword.arg == "name"]
                self.assertEqual(len(names), 1)
                self.assertEqual(ast.literal_eval(names[0]), row["effective_name"])
                self.assertTrue(row["effective_name"] in entries, "Missing measured native caption: " + row["effective_name"])
                entry = entries[row["effective_name"]]
                self.assertIn(row["translation_context"], entry["contexts"])
                self.assertIn({"path": row["path"], "line": row["line"], "kind": "rna.name"}, entry["sources"])

    def test_explicit_native_names_cover_captions_without_extracting_stored_values(self):
        catalog = self.fixture('''
from bpy.props import FloatProperty, IntProperty, StringProperty, EnumProperty
import bpy as host
class Example(Operator):
    count: IntProperty(name="count", default=0, translation_context="AnimAssist")
    raw_label: host.props.StringProperty(name="raw_label", default="A user-authored stored value", translation_context="AnimAssist")
    unnamed_id: FloatProperty(default=0.0, translation_context="AnimAssist")
    hidden_id: StringProperty(options={"HIDDEN"}, translation_context="AnimAssist")
    unknown_id: StringProperty(options=runtime_options, translation_context="AnimAssist")
    explicit_id: StringProperty(name="Explicit caption", translation_context="AnimAssist")
    blank_id: StringProperty(name="", translation_context="AnimAssist")
    saved_id: EnumProperty(items=saved_names, translation_context="AnimAssist.UserLayoutName")
    foreign_id: OtherProperty(translation_context="AnimAssist")
outside_id: StringProperty(translation_context="AnimAssist")
class Shadowed(Operator):
    StringProperty = user_factory
    shadow_id: StringProperty(translation_context="AnimAssist")
''')
        for caption in ("count", "raw_label"):
            self.assertIn(caption, catalog)
            self.assertEqual(catalog[caption]["contexts"], ["AnimAssist"])
            self.assertEqual(catalog[caption]["sources"][0]["kind"], "rna.name")
        self.assertIn("Explicit caption", catalog)
        for technical_value in ("unnamed_id", "hidden_id", "unknown_id", "explicit_id", "blank_id", "saved_id",
                                "foreign_id", "outside_id", "shadow_id", "A user-authored stored value"):
            self.assertNotIn(technical_value, catalog)

    def fixture(self, source, other_files=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "fixture.py").write_text(source, encoding="utf-8")
            for relative, content in (other_files or {}).items():
                (root / relative).write_text(content, encoding="utf-8")
            with patch.object(extractor, "help_records", return_value=[]):
                return {entry["msgid"]: entry for entry in extractor.extract(root)["entries"]}

    def test_callable_enums_and_exact_native_description_context(self):
        catalog = self.fixture('''
def choices(self, context):
    return [("ID", "Visible choice", "Choice guidance")]
class Demo(Operator):
    """Owned callback guidance."""
    bl_idname = "animassist.fixture"
    bl_label = "Fixture operator"
    choice: EnumProperty(name="Choice", description="Property guidance", items=choices)
class Submenu(Menu):
    """Native menu guidance."""
    bl_label = "Fixture menu"
class Layout(Operator):
    bl_idname = "animassist.fixture_layout"
    layout: EnumProperty(name="Saved Layout", description="Layout guidance", translation_context="AnimAssist.UserLayoutName", items=choices)
''')
        self.assertEqual(catalog["Visible choice"]["contexts"], ["*"])
        self.assertEqual(catalog["Choice guidance"]["contexts"], ["*"])
        self.assertEqual(catalog["Fixture operator"]["contexts"], ["AnimAssist"])
        self.assertEqual(catalog["Owned callback guidance."]["contexts"], [])
        self.assertEqual(catalog["Native menu guidance."]["contexts"], ["*"])
        self.assertEqual(catalog["Saved Layout"]["contexts"], [])
        self.assertEqual(catalog["Layout guidance"]["contexts"], ["*"])
        self.assertFalse(any("AnimAssist.UserLayoutName" in item["contexts"] for item in catalog.values()))

    def test_category_provider_and_loop_captions_use_actual_contexts(self):
        catalog = self.fixture('''
class Example(Panel):
    bl_label = "Owned panel"
    bl_category = "Keys"
for key, label in (("RAW", "Native caption"),):
    layout.operator("animassist.example", text=label, text_ctxt="AnimAssist")
for key, label in (("CUSTOM", "Custom caption"),):
    layout.label(text=T(label), translate=False)
''')
        self.assertEqual(catalog["Owned panel"]["contexts"], ["AnimAssist"])
        self.assertEqual(catalog["Keys"]["contexts"], ["*"])
        self.assertEqual(catalog["Native caption"]["contexts"], ["AnimAssist"])
        self.assertEqual(catalog["Custom caption"]["contexts"], [])

    def test_actual_help_caption_does_not_translate_a_completed_entry_twice(self):
        source = ast.parse((ROOT / "core/help_draw.py").read_text(encoding="utf-8"))
        function = next(node for node in source.body if isinstance(node, ast.FunctionDef)
                        and node.name == "draw_explainer_label")
        function.returns = None
        for argument in function.args.args:
            argument.annotation = None
        shown = []
        layout = types.SimpleNamespace(label=lambda **kwargs: shown.append(kwargs))
        layout.row = lambda **_kwargs: layout
        namespace = {"_is_enabled": lambda _context: True, "_is_compact": lambda _context: False,
                     "help_registry": types.SimpleNamespace(get_help=lambda _ident: types.SimpleNamespace(label="PRETRANSLATED")),
                     "T": lambda text: "JA:" + text, "draw_explainer_icon": lambda *_args: None}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "actual_help_caption", "exec"), namespace)
        namespace["draw_explainer_label"](layout, None, "owned")
        self.assertEqual(shown[-1], {"text": "PRETRANSLATED", "translate": False})
        namespace["draw_explainer_label"](layout, None, "owned", "Owned caption")
        self.assertEqual(shown[-1], {"text": "JA:Owned caption", "translate": False})

    def test_format_kind_comes_from_executed_boundary(self):
        catalog = self.fixture('''
T("100% of selected keys")
F("Count: {count}", count=3)
format_text("Timing Score: {score:.0f}/100", score=90)
T("Result: %s") % value
T("Value: {}" ).format(value)
''')
        self.assertNotIn("format", catalog["100% of selected keys"])
        self.assertEqual(catalog["Count: {count}"]["format"], "brace")
        self.assertEqual(catalog["Timing Score: {score:.0f}/100"]["format"], "brace")
        self.assertEqual(catalog["Result: %s"]["format"], "percent")
        self.assertEqual(catalog["Value: {}"]["format"], "brace")
        with self.assertRaisesRegex(ValueError, "Conflicting executable formats"):
            self.fixture('F("same")\nT("same") % value\n')

    def test_named_maps_and_fallbacks_retain_executable_format(self):
        catalog = self.fixture('''
CAPTIONS = {"ID": "Visible caption"}
T(CAPTIONS.get(key))
F({}.get(key, "Count: {count}"), count=3)
''')
        self.assertIn("Visible caption", catalog)
        self.assertEqual(catalog["Count: {count}"]["format"], "brace")

    def test_imported_enum_context_comes_only_from_its_consumer(self):
        catalog = self.fixture('''
from .choices import choices
class Owner(Panel):
    option: EnumProperty(items=choices, translation_context="ActualChoiceContext")
''', {"choices.py": '''
CHOICE_ITEMS = [("ID", "Unique choice caption", "Unique choice guidance")]
def choices(self, context):
    return CHOICE_ITEMS
'''})
        self.assertEqual(catalog["Unique choice caption"]["contexts"], ["ActualChoiceContext"])
        self.assertEqual(catalog["Unique choice guidance"]["contexts"], ["*"])
        self.assertEqual(catalog["Unique choice caption"]["sources"][0]["path"], "choices.py")
        excluded = self.fixture('''
CHOICE_ITEMS = [("ID", "Literal user choice", "Literal user guidance")]
class Owner(Panel):
    option: EnumProperty(items=CHOICE_ITEMS, translation_context="AnimAssist.UserLayoutName")
''')
        self.assertNotIn("Literal user choice", excluded)

    def test_class_local_enum_tables_keep_their_own_context(self):
        catalog = self.fixture('''
BASE = [("ID", "Unrelated module caption", "Unrelated module guidance")]
class First(Panel):
    BASE = [("ID", "First caption", "First guidance")]
    ALIAS = BASE
    CHOICES = ALIAS
    option: EnumProperty(items=CHOICES, translation_context="FirstContext")
class Second(Panel):
    CHOICES = [("ID", "Second caption", "Second guidance")]
    option: EnumProperty(items=CHOICES, translation_context="SecondContext")
''')
        self.assertEqual(catalog["First caption"]["contexts"], ["FirstContext"])
        self.assertEqual(catalog["Second caption"]["contexts"], ["SecondContext"])
        self.assertEqual(catalog["First guidance"]["contexts"], ["*"])
        self.assertEqual(catalog["Second guidance"]["contexts"], ["*"])
        self.assertNotIn("Unrelated module caption", catalog)

    def test_generated_panels_and_callback_choices_exist_with_real_refs(self):
        catalog = {entry["msgid"]: entry for entry in extractor.extract()["entries"]}
        for caption in ("Driver & Target", "Variables & Expression", "Response Curve", "Pose & Match",
                        "Pose & Bake", "Clean Up", "Shape Curves", "Whole Animation", "This Pose",
                        "Motion Options", "Keys Options", "Timing Options", "Curves Options", "Tween Options",
                        "Show compact shelf view", "Choose the Timeline row to configure",
                        "Tool families the Timeline band shows in this workspace"):
            self.assertIn(caption, catalog)
            # Native descriptions retain their TIP default context.
            default_context = caption in {"Show compact shelf view",
                                          "Choose the Timeline row to configure",
                                          "Tool families the Timeline band shows in this workspace"}
            self.assertIn("*" if default_context else "AnimAssist", catalog[caption]["contexts"])
            self.assertTrue(all((ROOT / source["path"]).exists() and source["line"] > 0
                                for source in catalog[caption]["sources"]))

    def test_failure_confirm_and_caption_helpers_cover_actual_sources(self):
        fixture = self.fixture('''
report_failure(op, "Fixture failed", "Try the fixture again")
confirm_dialog(op, context, event, "Confirm this fixture?")
draw_context_warning(layout, "Choose a fixture")
analysis_box(layout, context, title="Analysis fixture")
danger_box(layout, context, label="Danger fixture")
section_header(layout, label="Section fixture")
''')
        for caption in ("Fixture failed", "Try the fixture again", "Confirm this fixture?", "Choose a fixture",
                        "Analysis fixture", "Danger fixture", "Section fixture"):
            self.assertIn(caption, fixture)
            self.assertEqual(fixture[caption]["contexts"], [])
        messages = {entry["msgid"] for entry in extractor.extract()["entries"]}
        count = 0
        for path in ROOT.rglob("*.py"):
            if path.relative_to(ROOT).parts[0] in {"i18n", "tests"}:
                continue
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8-sig"))):
                if not isinstance(node, ast.Call):
                    continue
                name = getattr(node.func, "id", getattr(node.func, "attr", ""))
                for index in extractor.HELPER_TEXT_ARGUMENTS.get(name, ()):
                    if len(node.args) > index and isinstance(node.args[index], ast.Constant) and isinstance(node.args[index].value, str):
                        self.assertIn(node.args[index].value, messages, (path, node.lineno))
                        count += 1
        self.assertGreaterEqual(count, 108)

    def test_catalog_matches_current_source(self):
        actual = json.loads((ROOT / "i18n" / "source_catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(actual, extractor.extract())

    def test_every_assembled_help_display_field_has_a_catalog_key(self):
        catalog = {entry["msgid"] for entry in extractor.extract()["entries"]}
        records = extractor.help_records()
        self.assertEqual(len(records), 475)
        for record, path, line in records:
            for field in ("label", "tooltip", "description", "category"):
                self.assertIn(record[field], catalog, (path, line, record["id"], field))

    def test_custom_templates_do_not_register_unrelated_native_contexts(self):
        catalog = {entry["msgid"]: entry for entry in extractor.extract()["entries"]}
        self.assertEqual(catalog["Shortcut: {keys}."]["contexts"], [])
        self.assertEqual(catalog["Stage: {stage}. Click to choose a stage; Ctrl+Wheel cycles. Each stage has its own toolset, edited in Settings"]["contexts"], [])
        self.assertIn("AnimAssist", catalog["Search Animation Tools"]["contexts"])
        self.assertIn("AnimAssist", catalog["Language"]["contexts"])

    def test_actual_offset_status_translates_templates_and_retains_data_names(self):
        tree = ast.parse((ROOT / "operators" / "anim_offset_ops.py").read_text(encoding="utf-8"))
        function = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == "offset_session_status")
        scene = types.SimpleNamespace(as_pointer=lambda: 1, anim_assist=types.SimpleNamespace(
            anim_offset_active=True, mask=types.SimpleNamespace(enabled=True, start_frame=1, end_frame=9,
                                                               blend_left=2, blend_right=3)))
        target = (types.SimpleNamespace(name="Settings"), types.SimpleNamespace(name="Frame"))
        old_language = i18n.active_language
        i18n.active_language = lambda context=None: "ja"
        i18n._catalogs["ja"] = {"Settings": "設定", "Frame": "フレーム",
                               "mask {start}–{end} (blend {left}/{right})": "範囲 {start}–{end}（境界 {left}/{right}）"}
        namespace = {"F": i18n.F, "T": i18n.T, "_sessions": {1: target}}
        try:
            exec(compile(ast.Module(body=[function], type_ignores=[]), "actual_offset_status", "exec"), namespace)
            self.assertEqual(namespace["offset_session_status"](scene), "Settings / Frame | 範囲 1–9（境界 2/3）")
            self.assertEqual((target[0].name, target[1].name), ("Settings", "Frame"))
        finally:
            i18n.active_language = old_language
            i18n._catalogs.clear()


if __name__ == "__main__":
    unittest.main()
