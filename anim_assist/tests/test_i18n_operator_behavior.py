"""Exercise production message paths without starting the native application."""

from __future__ import annotations

import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]


def function(path, name, namespace, owner=None, start_at=None):
    """Compile the actual function body, retaining its calls and branch order."""
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8-sig"))
    body = next(node.body for node in tree.body
                if isinstance(node, ast.ClassDef) and node.name == owner) if owner else tree.body
    node = copy.deepcopy(next(node for node in body
                              if isinstance(node, ast.FunctionDef) and node.name == name))
    node.decorator_list = []
    if start_at:
        index = next(index for index, statement in enumerate(node.body)
                     if isinstance(statement, ast.Assign)
                     and any(isinstance(target, ast.Name) and target.id == start_at
                             for target in statement.targets))
        node.body = node.body[index:]
    future = ast.parse("from __future__ import annotations").body[0]
    exec(compile(ast.Module(body=[future, node], type_ignores=[]), str(ROOT / path), "exec"), namespace)
    return namespace[name]


def module(path):
    name = "_aa_operator_test_" + uuid.uuid4().hex
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    try:
        spec.loader.exec_module(result)
    finally:
        sys.modules.pop(name, None)
    return result


def translations(catalog):
    def text(source, **_kwargs):
        return catalog.get(source, source)

    def formatted(source, *args, **kwargs):
        return text(source).format(*args, **kwargs)

    return text, formatted


def reporter(**values):
    messages = []
    return NS(report=lambda flags, text: messages.append(text), **values), messages


class OperatorMessageBehaviorTests(unittest.TestCase):
    def test_driver_modifier_uses_provider_context_and_preserves_default(self):
        tree = ast.parse((ROOT / "operators/driver_ops.py").read_text())
        owner = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                     and node.name == "ANIMASSIST_OT_driver_modifier_add")
        prop = next(node.annotation for node in owner.body if isinstance(node, ast.AnnAssign)
                    and node.target.id == "type")
        values = {item.arg: item.value for item in prop.keywords}
        self.assertEqual(ast.literal_eval(values["translation_context"]), "Action")
        self.assertEqual(ast.literal_eval(values["default"]), "LIMITS")
        self.assertEqual(values["items"].id, "_MODIFIER_TYPES")

    def test_tool_choices_refresh_language_and_retain_native_item_lifetime(self):
        prefix = "_aa_tool_choice_" + uuid.uuid4().hex
        root, core, registry = [ModuleType(prefix + suffix)
                                for suffix in ("", ".core", ".core.p10_tool_registry")]
        root.__path__, core.__path__ = [], []
        tool = NS(op_id="animassist.smooth", label="Smooth Keys",
                  description="Smooth selected keys", icon="KEY_HLT")
        registry.all_tools = lambda: [tool]
        modules = {item.__name__: item for item in (root, core, registry)}
        language = ["fr"]
        catalogs = {"fr": {"Smooth Keys": "Lisser les cles", "Smooth selected keys": "Lisser la selection"},
                    "ja": {"Smooth Keys": "キーを滑らかに", "Smooth selected keys": "選択したキーを滑らかにする"}}
        namespace = {"__package__": prefix + ".operators", "_tool_enum_snapshot": None,
                     "_tool_enum_language_items": {},
                     "_tool_enum_items": [], "active_language": lambda context: language[0],
                     "T": lambda text, **kwargs: catalogs[language[0]].get(text, text),
                     "_log": NS(error=lambda *args: None)}
        choices = function("operators/p10_shelf_ops.py", "_get_tool_items", namespace)
        sys.modules.update(modules)
        try:
            french = choices(None, None)
            self.assertEqual(french, [("animassist.smooth", "Lisser les cles", "Lisser la selection", "KEY_HLT", 0)])
            self.assertIs(choices(None, None), french)
            french_identity = id(french)
            del french
            language[0] = "ja"
            japanese = choices(None, None)
            self.assertEqual(japanese, [("animassist.smooth", "キーを滑らかに", "選択したキーを滑らかにする", "KEY_HLT", 0)])
            self.assertIs(choices(None, None), japanese)
            self.assertIn("fr", namespace["_tool_enum_language_items"])
            self.assertEqual(id(namespace["_tool_enum_language_items"]["fr"][1]), french_identity)
            language[0] = "fr"
            self.assertEqual(id(choices(None, None)), french_identity)
            self.assertEqual((tool.op_id, tool.label, tool.description),
                             ("animassist.smooth", "Smooth Keys", "Smooth selected keys"))
        finally:
            for name in modules:
                sys.modules.pop(name, None)

    def diagnostics(self, catalog, target):
        text, formatted = translations(catalog)
        namespace = {
            "T": text, "F": formatted,
            "constants": NS(ADDON_VERSION_STRING="1.2.3"),
            "bpy": NS(app=NS(version_string="5.3")),
            "get_active_target": lambda context: target,
            "AnimContextResolver": NS(get_graph_editor=lambda context: True,
                                      get_dope_sheet=lambda context: None,
                                      get_timeline=lambda context: True),
            "cap_mod": NS(get_registry=lambda: NS(all_capabilities=lambda: {"curve.id": True})),
            "cache_mod": NS(get_cache=lambda: NS(selection_history=[1, 2], last_used_tool="tool.id")),
            "rts_mod": NS(get_state=lambda: NS(active_tool_id="active.id", is_batch_processing=False)),
        }
        return function("operators/diagnostics_ops.py", "_build_diagnostics_text", namespace)(NS())

    def test_english_diagnostic_output_keeps_original_values(self):
        result = self.diagnostics({}, None)
        self.assertEqual(result, "Anim Assist v1.2.3\nBlender 5.3\n\nActive Object: None\n\n"
                         "Graph Editor: found\nDope Sheet: not found\nTimeline: found\n\n"
                         "Capabilities (1):\n  curve.id: OK\n\nSelection history entries: 2\n"
                         "Last used tool: tool.id\nActive tool: active.id\nBatch processing: False")

    def test_translated_diagnostics_do_not_translate_user_names(self):
        target = NS(obj=NS(name="found"), bone_name="Action: None", action=NS(name="found"),
                    fcurves=[1, 2], is_linked=False)
        result = self.diagnostics({"Active Object: {p0}": "Objet : {p0}",
                                   "Active Bone: {p0}": "Os : {p0}",
                                   "Graph Editor: {p0}": "Graphe : {p0}",
                                   "found": "trouve", "Action: None": "Aucune action"}, target)
        self.assertIn("Objet : found\nOs : Action: None", result)
        self.assertIn("Action: found (2 fcurves)", result)
        self.assertIn("Graphe : trouve", result)

    def test_timing_clipboard_uses_formatter_and_keeps_owner_name(self):
        diag = module("core/p6_diagnostics.py")
        state = diag.TimingDiagnostics(score=73.6, key_count=3, frame_span=20)
        text, formatted = translations({"Timing Score: {score:.0f}/100": "Note : {score:.0f}/100",
                                         "No significant gaps.": "Aucun intervalle.",
                                         "found": "trouve"})
        namespace = {"T": text, "F": formatted, "diag": diag,
                     "get_cached_diag": lambda: state, "_cached_diag_obj": "found"}
        execute = function("operators/p6_diag_ops.py", "execute", namespace,
                           "AA_OT_p6_copy_diag_report")
        operator, messages = reporter()
        context = NS(window_manager=NS(clipboard="old"))
        self.assertEqual(execute(operator, context), {"FINISHED"})
        self.assertIn("found", context.window_manager.clipboard)
        self.assertNotIn("trouve", context.window_manager.clipboard)
        self.assertIn("Note : 74/100", context.window_manager.clipboard)
        self.assertIn("Aucun intervalle.", context.window_manager.clipboard)
        self.assertEqual(messages, ["Diagnostics report copied to clipboard"])

    def test_timing_summary_translates_items_and_keeps_counts(self):
        state = NS(gaps=[1, 2], clusters=[3], score=73.6, result_enum="WARNING")
        settings = NS(gap_threshold=10, cluster_radius=2)
        text, formatted = translations({"{p0} gap(s)": "{p0} intervalles",
                                         "{p0} cluster(s)": "{p0} groupes",
                                         "Diagnostics: {p0}  |  Score {p1}/100": "Note {p1} : {p0}"})
        namespace = {"T": text, "F": formatted, "get_p6": lambda context: settings,
                     "_get_fcurves": lambda context: ([1], "found"),
                     "diag": NS(run_diagnostics=lambda *args, **kwargs: state),
                     "_tag_redraw": lambda context: None}
        execute = function("operators/p6_diag_ops.py", "execute", namespace,
                           "AA_OT_p6_run_diagnostics")
        operator, messages = reporter()
        self.assertEqual(execute(operator, NS()), {"FINISHED"})
        self.assertEqual(messages, ["Note 74 : 2 intervalles, 1 groupes"])
        self.assertEqual((settings.last_diag_gap_count, settings.last_diag_cluster_count), (2, 1))
        self.assertEqual(namespace["_cached_diag_obj"], "found")

    def test_pose_comparison_formats_core_messages_before_reporting(self):
        text, formatted = translations({"+ {path}[{index}]  (only in {label})":
                                         "Seulement {label} : {path}[{index}]",
                                         "found": "trouve"})
        compare = function("core/pose_compare.py", "compare_snapshots", {})
        state = NS(prev_snapshot=NS(values={}, label="Previous Pose"),
                   next_snapshot=NS(values={("found", 2): 1.0}, label="Next Pose"))
        namespace = {"T": text, "F": formatted,
                     "pc": NS(get_state=lambda: state, compare_snapshots=compare)}
        execute = function("operators/p3_pose_compare_ops.py", "execute", namespace,
                           "AA_OT_pose_compare_report")
        operator, messages = reporter(tolerance=0.001)
        self.assertEqual(execute(operator, NS()), {"FINISHED"})
        self.assertEqual(messages[-1], "Seulement Next Pose : found[2]")
        self.assertEqual(state.last_report, [messages[-1]])

    def test_breakdown_runs_once_and_formats_its_core_result(self):
        text, formatted = translations({"Wrote {count} keys": "{count} cles ecrites"})
        calls = []

        def apply(*args, format_text=str.format, **kwargs):
            calls.append((args, kwargs))
            return NS(messages=[format_text("Wrote {count} keys", count=3)])

        remembered = []
        namespace = {"T": text, "F": formatted,
                     "_resolve_target": lambda context: (NS(animation_data=NS(action=object())), None),
                     "bc": NS(apply_breakdown=apply, remember_last=remembered.append)}
        run = function("operators/p3_breakdown_ops.py", "_run", namespace)
        operator, messages = reporter()
        options, context = object(), object()
        self.assertEqual(run(operator, context, options, frames=[7]), {"FINISHED"})
        self.assertEqual(messages, ["3 cles ecrites"])
        self.assertEqual(len(calls), 1)
        self.assertIs(calls[0][0][0], context)
        self.assertEqual(calls[0][1], {"frames": [7]})
        self.assertEqual(remembered, [options])

    def test_offset_early_warnings_are_localized_without_editing_keys(self):
        text, formatted = translations({
            "No frames matched the current scope.": "Aucune image.",
            "Offset delta is zero — nothing to do.": "Decalage nul.",
            "Offset properties unavailable.": "Options indisponibles.",
            "No targets selected.": "Aucune cible."})
        master = NS(is_zero=lambda: True)
        master.masked_for_axis = lambda axis: master
        calls = []
        namespace = {"T": text, "F": formatted,
                     "om": NS(build_delta=lambda **kwargs: calls.append(kwargs) or master)}
        run = function("operators/p4_offset_ops.py", "_run_offset", namespace)
        options = NS(translate=(), rotate=(), scale=(), channel_mask="TRS", fine_step=False,
                     preset_multiplier=1.0, preserve_contact_axis="NONE")
        self.assertEqual(run(None, options, [], None, []), (0, 0, ["Aucune image."]))
        self.assertEqual(calls, [])
        self.assertEqual(run(None, options, [], None, [1]), (0, 0, ["Decalage nul."]))
        self.assertEqual(len(calls), 1)
        namespace = {"T": text, "F": formatted, "_resolve_options": lambda context: None}
        replay = function("operators/p4_offset_ops.py", "_run_from_record", namespace)
        self.assertEqual(replay(None, None), (0, 0, ["Options indisponibles."]))
        namespace["_resolve_options"] = lambda context: NS()
        namespace["tg"] = NS(resolve_targets=lambda context, **kwargs: [])
        record = NS(delta=NS(translation=(), rotation_euler=(), scale=(), channel_mask="TRS"),
                    space="LOCAL", pivot_mode="INDIVIDUAL", scope="SELECTED", falloff_shape="LINEAR")
        self.assertEqual(replay(None, record), (0, 0, ["Aucune cible."]))

    def test_macro_validation_translates_errors_and_keeps_operator_id(self):
        text, formatted = translations({"Step {index}: Invalid op_id format '{operator}'":
                                         "Etape {index} : identifiant '{operator}' invalide",
                                         "found": "trouve"})
        validate = function("core/p10_macro_engine.py", "validate_macro",
                            {"_log": NS(info=lambda *args: None)})
        namespace = {"T": text, "F": formatted, "validate_macro": validate,
                     "get_p10": lambda context: NS(macros=[NS(name="found")]),
                     "build_macro_from_property": lambda macro: [NS(enabled=True, op_id="found")],
                     "log_operation": lambda *args, **kwargs: None}
        execute = function("operators/p10_macro_ops.py", "execute", namespace,
                           "AA_OT_p10_validate_macro")
        operator, messages = reporter(index=0, bl_idname="test.id")
        self.assertEqual(execute(operator, NS()), {"FINISHED"})
        self.assertEqual(messages, ["Macro validation failed: Etape 0 : identifiant 'found' invalide"])

    def test_complete_bake_summary_can_reorder_values(self):
        text, formatted = translations({
            "Bake [{p0}/{p1}]: {p2} keys, {p3} preserved manual ({p4})":
                "{p3} manuelles; {p2} cles; [{p1}/{p0}]; {p4}"})
        tree = ast.parse((ROOT / "operators/p12_bake_ops.py").read_text())
        statement = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                         and any(isinstance(target, ast.Name) and target.id == "msg" for target in node.targets))
        namespace = {"T": text, "F": formatted, "link": NS(mode="PREVIEW", target_kind="BOTH"),
                     "total_written": 3, "total_skipped": 4, "analyze_result": NS(backend="backend.id")}
        exec(compile(ast.Module(body=[statement], type_ignores=[]), "bake-summary", "exec"), namespace)
        self.assertEqual(namespace["msg"], "4 manuelles; 3 cles; [BOTH/PREVIEW]; backend.id")

    def test_lipsync_setup_optional_instructions_translate_before_inserting_data(self):
        text, formatted = translations({
            "Lipsync layer ready: {p0}": "Lien pret : {p0}",
            "{p0} — seeded {p1} rig roles": "{p0} — {p1} roles ajoutes",
            "{p0} (sequencer strip unavailable — bind manually)": "{p0} (lier la bande manuellement)",
            "found": "trouve"})
        for seeded in (0, 2):
            for strip in ("track.id", ""):
                with self.subTest(seeded=seeded, strip=strip):
                    namespace = {"T": text, "F": formatted, "layer_name": "found",
                                 "seeded": seeded, "strip_name": strip}
                    finish = function("operators/p12_setup_ops.py", "execute", namespace,
                                      "AA_OT_p12_setup_lipsync", start_at="msg")
                    operator, messages = reporter()
                    self.assertEqual(finish(operator, None), {"FINISHED"})
                    expected = "Lien pret : found"
                    if seeded:
                        expected += " — 2 roles ajoutes"
                    if not strip:
                        expected += " (lier la bande manuellement)"
                    self.assertEqual(messages, [expected])

    def test_settings_validation_keeps_preferences_and_translates_template(self):
        text, formatted = translations({"Unknown saved layout {name}": "Disposition inconnue {name}",
                                         "found": "trouve"})
        error_text = function("i18n/__init__.py", "error_text", {"T": text, "F": formatted})
        model = module("ui/timeline_config.py")
        prefix = "_aa_operator_import_" + uuid.uuid4().hex
        root, ui, catalog, prefs_module = [ModuleType(prefix + suffix)
                                         for suffix in ("", ".ui", ".ui.timeline_catalog", ".prefs")]
        root.__path__, ui.__path__ = [], []

        def decode(*args):
            raise model.ValidationError("Unknown saved layout {name}", name="found")

        ui.timeline_config = NS(decode=decode, encode=lambda *args: None)
        catalog.ACTIONS, catalog.quick_property_name = {}, lambda value: value
        prefs_module.timeline_record = lambda *args: None
        modules = {item.__name__: item for item in (root, ui, catalog, prefs_module)}
        prefs = NS(saved_value="original")
        namespace = {"__package__": prefix + ".operators", "T": text, "F": formatted,
                     "error_text": error_text, "json": json, "_get_prefs": lambda context: prefs,
                     "Path": lambda path: NS(read_text=lambda **kwargs:
                                              json.dumps({"timeline_layouts_json": "bad"}))}
        execute = function("operators/settings_ops.py", "execute", namespace, "AA_OT_import_settings")
        operator, messages = reporter(filepath="user-file.json")
        sys.modules.update(modules)
        try:
            self.assertEqual(execute(operator, NS()), {"CANCELLED"})
        finally:
            for name in modules:
                sys.modules.pop(name, None)
        self.assertEqual(messages, ["Disposition inconnue found"])
        self.assertEqual(vars(prefs), {"saved_value": "original"})


if __name__ == "__main__":
    unittest.main()
