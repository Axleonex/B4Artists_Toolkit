"""Finite UI-gap candidate checks; never regenerate the installed source file."""

import ast
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


extractor = load("aa_ui_completion_extract", ROOT / "i18n/extract.py")
HELPERS = {
    "Nudge Back 1 Frame", "Nudge Forward 1 Frame",
    "Align Starts to Active Clip", "Align Ends to Active Clip", "Blend Options",
    "Push Down Active Action", "Stash Active Action", "Edit Active Source",
    "Drag to adjust \u00b7 double-click or click away to apply \u00b7 Esc cancels",
    "\u22121f", "R",
}


class UICompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = extractor.extract()
        cls.entries = {row["msgid"]: row for row in cls.candidate["entries"]}
        cls.help = {record[0]["id"]: record[0] for record in extractor.help_records()}

    def test_exact_eleven_helper_messages_and_real_references(self):
        expected_paths = {
            "Nudge Back 1 Frame": "ui/header_menus.py",
            "Nudge Forward 1 Frame": "ui/header_menus.py",
            "R": "ui/timeline_overlay.py",
            "Drag to adjust \u00b7 double-click or click away to apply \u00b7 Esc cancels":
                "ui/timeline_overlay.py",
        }
        for message in HELPERS:
            with self.subTest(message=message):
                refs = self.entries[message]["sources"]
                path = expected_paths.get(message, "ui/nla_panels.py")
                self.assertTrue(any(ref["path"] == path and
                                    ref["kind"].startswith("helper.") for ref in refs))
        self.assertNotEqual("\u22121f", "-1f")

    def test_scoped_helpers_do_not_extract_unrelated_names_or_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = {
                "ui/nla_panels.py": 'native(layout, "operator.id", "NLA caption")\n'
                    'timing(layout, "TIMING_ID", "Timing caption")\n'
                    'options(layout, "options.id", "Options caption")\n'
                    'foreign.native(layout, "ID", "Not an owned helper")\n',
                "ui/header_menus.py": 'from .nla_panels import timing\n'
                    'timing(layout, "HEADER_ID", "Header caption")\n',
                "ui/timeline_overlay.py": '_text(position, "Overlay instruction")\n',
                "unrelated.py": 'native(a, "ID", "Not a caption")\n'
                    'timing(a, "ID", "Not timing prose")\n'
                    'options(a, "ID", "Not options prose")\n'
                    '_text(a, "Not overlay prose")\n',
            }
            for relative, text in sources.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            with patch.object(extractor, "help_records", return_value=[]):
                messages = {row["msgid"] for row in extractor.extract(root)["entries"]}
            self.assertEqual(messages, {"NLA caption", "Timing caption", "Options caption",
                                        "Header caption", "Overlay instruction"})

    def test_complete_breakdown_description_preserves_runtime_value(self):
        tree = ast.parse((ROOT / "operators/p3_modal_ops.py").read_text(encoding="utf-8"))
        owner = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                     and node.name == "AA_OT_modal_drag_breakdown")
        value = next(node.value for node in owner.body if isinstance(node, ast.Assign)
                     and any(getattr(target, "id", "") == "bl_description"
                             for target in node.targets))
        constants = ast.parse((ROOT / "constants.py").read_text(encoding="utf-8"))
        hint = next(ast.literal_eval(node.value) for node in constants.body
                    if isinstance(node, ast.AnnAssign) and
                    getattr(node.target, "id", "") == "BREAKDOWN_ANCHOR_HINT")
        expected = ("Active object's Action using Breakdown targets and mask. Drag horizontally; "
                    "release left mouse to apply, Esc/right mouse restores the pre-drag keys. "
                    + hint)
        self.assertEqual(ast.literal_eval(value), expected)
        self.assertEqual(self.entries[expected]["contexts"], [])
        self.assertTrue(any(ref["kind"] == "RNA"
                            for ref in self.entries[expected]["sources"]))
        # The actual registered hover callback uses T, not a native dictionary
        # entry for bl_description. Exercise that producer without importing bpy.
        source = ast.parse((ROOT / "core/explainers.py").read_text(encoding="utf-8"))
        describe = next(node for node in source.body if isinstance(node, ast.FunctionDef)
                        and node.name == "_describe")
        cls = type("Breakdown", (), {})
        namespace = {"mode": lambda _context: "FULL", "_full": {cls: expected},
                     "T": lambda text: "TRANSLATED" if text == expected else text}
        exec(compile(ast.Module(body=[describe], type_ignores=[]), "hover-callback", "exec"), namespace)
        self.assertEqual(namespace["_describe"](cls, None, None), "TRANSLATED")

    def test_quaternion_help_distinguishes_wxyz_from_xyz(self):
        text = self.help["prop.p3_mask_axis"]["description"]
        self.assertIn("Location, Euler rotation and scale use 0=X, 1=Y and 2=Z.", text)
        self.assertIn("Quaternion rotation uses 0=W, 1=X, 2=Y and 3=Z.", text)
        self.assertNotIn("3=W", text)
        source = ast.parse((ROOT / "core/breakdown_core.py").read_text(encoding="utf-8"))
        blend = next(node for node in source.body if isinstance(node, ast.FunctionDef)
                     and node.name == "blend_quaternion")
        result = next(node.value for node in ast.walk(blend) if isinstance(node, ast.Return))
        self.assertEqual([component.attr for component in result.elts], ["w", "x", "y", "z"])

    def test_snapshot_help_matches_current_frame_and_slot_names(self):
        tree = ast.parse((ROOT / "operators/p3_pose_compare_ops.py").read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == "_active_frame")
        function.returns = None
        for argument in function.args.args:
            argument.annotation = None
        namespace = {}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "snapshot-frame", "exec"), namespace)
        context = types.SimpleNamespace(scene=types.SimpleNamespace(frame_current_final=12.25))
        self.assertEqual(namespace["_active_frame"](context), 12.25)
        for slot, suffix in (("Previous", "prev"), ("Next", "next")):
            entry = self.help["op.animassist.pose_snapshot_" + suffix]
            self.assertEqual(entry["tooltip"], "Snapshot the current-frame pose as '" + slot.lower() + "'")
            self.assertIn("at the current frame", entry["description"])
            self.assertIn(slot + " slot", entry["description"])
            owner = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                         and node.name == "AA_OT_pose_snapshot_" + suffix)
            self.assertTrue(any(isinstance(node, ast.Call) and
                                getattr(node.func, "attr", "") == "set_" + suffix and
                                ast.unparse(node.args[1]) == "_active_frame(context)"
                                for node in ast.walk(owner)))

    def test_completion_messages_and_extraction_preserve_installed_source(self):
        path = ROOT / "i18n/source_catalog.json"
        before = path.read_bytes()
        # Extraction is read-only whether the stored catalog is the held
        # predecessor or a legitimately installed matching successor.
        actual = {row["msgid"] for row in extractor.extract()["entries"]}
        new_help = {self.help["prop.p3_mask_axis"]["description"]}
        for suffix in ("prev", "next"):
            record = self.help["op.animassist.pose_snapshot_" + suffix]
            new_help.update((record["tooltip"], record["description"]))
        composite = {message for message in self.entries
                     if message.startswith("Active object's Action using Breakdown targets and mask. Drag horizontally;")}
        self.assertEqual(len(composite), 1)
        required = HELPERS | new_help | composite
        self.assertEqual(len(required), 17)
        self.assertTrue(required <= actual)
        obsolete = {
            "Per-axis checkboxes let you restrict a breakdown to, for example, only the "
            "Y component of location channels. Axis indices map to 0=X, 1=Y, 2=Z, and "
            "3=W for quaternion channels.",
            "Snapshot the pose at the previous key as 'previous'",
            "Snapshot the pose at the next key as 'next'",
            "Walks every fcurve on the active object, evaluates its value at the "
            "previous key frame, and stores the result in the Previous slot of the "
            "pose compare state. Used by the Pose Compare Report.",
            "Walks every fcurve on the active object, evaluates its value at the "
            "next key frame, and stores the result in the Next slot of the pose "
            "compare state.",
        }
        self.assertEqual(len(obsolete), 5)
        self.assertTrue(obsolete.isdisjoint(actual))
        self.assertEqual(path.read_bytes(), before)

    def test_native_registration_requires_complete_source_entries(self):
        adapter = load("aa_ui_completion_adapter", ROOT / "i18n/__init__.py")
        message = "New complete native description"
        registered = {}
        host = types.SimpleNamespace(app=types.SimpleNamespace(translations=types.SimpleNamespace(
            register=lambda _key, messages: registered.update(messages),
            unregister=lambda _key: registered.clear())))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "catalogs").mkdir()
            (root / "catalogs/ja.json").write_text(json.dumps({message: "TRANSLATED"}), encoding="utf-8")
            source = root / "source_catalog.json"
            source.write_text(json.dumps({"entries": []}), encoding="utf-8")
            with patch.object(adapter, "_ROOT", root), patch.dict(sys.modules, {"bpy": host}):
                try:
                    adapter.register()
                    self.assertEqual(adapter.T(message, language="ja"), "TRANSLATED")
                    self.assertNotIn(("*", message), registered["ja_JP"])
                    adapter.unregister()
                    source.write_text(json.dumps({"entries": [{"msgid": message, "contexts": ["*"]}]}), encoding="utf-8")
                    adapter.register()
                    self.assertEqual(registered["ja_JP"][("*", message)], "TRANSLATED")
                finally:
                    adapter.unregister()


if __name__ == "__main__":
    unittest.main()
