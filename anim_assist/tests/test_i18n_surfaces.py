"""Localization must preserve identity and measure the text that is drawn."""

import importlib
import importlib.util
import ast
import pathlib
import sys
import types
import unittest
import time
import json
import copy
from dataclasses import asdict
from unittest.mock import patch


ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = "aa_i18n_surface_tests"
package = types.ModuleType(PACKAGE)
package.__path__ = [str(ROOT)]
sys.modules[PACKAGE] = package
for name in ("core", "ui"):
    module = types.ModuleType(PACKAGE + "." + name)
    module.__path__ = [str(ROOT / name)]
    sys.modules[module.__name__] = module
i18n = importlib.import_module(PACKAGE + ".i18n")
catalog = importlib.import_module(PACKAGE + ".ui.timeline_catalog")
model = importlib.import_module(PACKAGE + ".ui.timeline_config")
help_registry = importlib.import_module(PACKAGE + ".core.help_registry")


class SurfaceTests(unittest.TestCase):
    def setUp(self):
        self.old_language = i18n.active_language
        i18n.active_language = lambda context=None: "ja"
        i18n._catalogs["ja"] = {"Settings": "設定", "Block": "ブロック", "Tween": "中割り",
                                 "50% Breakdown": "50%の中割り", "Help": "ヘルプ", "Summary": "概要"}

    def tearDown(self):
        i18n.active_language = self.old_language
        i18n._catalogs.clear()
        help_registry.clear_all_help()

    def test_help_is_translated_on_access_without_mutating_ids_or_source(self):
        source = help_registry.HelpEntry("op.keep", "Help", "Summary", "Summary", "phase1", "General")
        help_registry.register_help(source)
        shown = help_registry.get_help("op.keep")
        self.assertEqual(shown.label, "ヘルプ")
        self.assertEqual(shown.tooltip, "概要")
        self.assertEqual(shown.id, "op.keep")
        self.assertEqual(shown.category, "General")
        self.assertIs(help_registry._REGISTRY["op.keep"], source)
        i18n.active_language = lambda context=None: "en"
        self.assertEqual(help_registry.get_help("op.keep").label, "Help")

    def test_localized_search_keeps_english_aliases(self):
        self.assertIn("B50", catalog.search_actions("50%の中割り"))
        self.assertIn("B50", catalog.search_actions("halfway"))

    def test_help_sort_uses_translated_labels(self):
        for key, label in (("a", "Settings"), ("b", "Tween")):
            help_registry.register_help(help_registry.HelpEntry(key, label, "", "", "phase1", "General"))
        labels = [entry.label for entry in help_registry.get_all_help()]
        self.assertEqual(labels, sorted(labels, key=str.lower))

    def test_toolbar_measures_translated_text_and_keeps_saved_layout(self):
        record = model.recommended(catalog.ACTIONS)
        before = model.encode(record, catalog.ACTIONS)
        measurements = []

        def measure(text):
            measurements.append(text)
            return len(text) * 10

        row = model.toolbar_layout(3000, 28, 28, False, record, catalog.GROUPS, {}, measure,
                                   "BLOCK", translate=i18n.T)
        self.assertIn("ブロック", measurements)
        self.assertIn("設定", measurements)
        self.assertIn("中割り", measurements)
        self.assertEqual(next(item[2] for item in row if item[0] == "STAGE_CYCLE"), "ブロック")
        self.assertEqual(model.encode(record, catalog.ACTIONS), before)

    def test_production_toolbar_wiring_measures_the_language_it_draws(self):
        # Execute the actual production function against recording BLF and context.
        # This fails if its toolbar_layout call drops translate=T.
        source = ast.parse((ROOT / "ui" / "timeline_overlay.py").read_text(encoding="utf-8"))
        function = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == "_toolbar_row")
        body = ast.Module(body=[function], type_ignores=[])
        record = model.recommended(catalog.ACTIONS)
        measurements = []
        blf = types.SimpleNamespace(size=lambda *args: None,
                                    dimensions=lambda _font, text: (measurements.append(text) or len(text) * 10, 11))
        prefs_name = PACKAGE + ".prefs"
        old_prefs = sys.modules.get(prefs_name)
        sys.modules[prefs_name] = types.SimpleNamespace(get_prefs=lambda context: None,
                                                       timeline_record=lambda prefs: record)
        namespace = {"__package__": PACKAGE + ".ui", "SimpleNamespace": types.SimpleNamespace,
                     "model": model, "ACTIONS": catalog.ACTIONS, "GROUPS": catalog.GROUPS,
                     "QUICK_LABELS": catalog.QUICK_LABELS, "ROW_LABELS": {}, "ALL_ROW_LABELS": {},
                     "T": i18n.T, "blf": blf, "CORNER_INSET": 16,
                     "_row_geometry": lambda area, system: (28, 36, 14, 46),
                     "current_stage": lambda context: "BLOCK"}
        context = types.SimpleNamespace(
            region=types.SimpleNamespace(height=400, width=3000, x=0),
            area=types.SimpleNamespace(x=0, width=3000),
            preferences=types.SimpleNamespace(system=types.SimpleNamespace(ui_scale=1)),
            scene=types.SimpleNamespace(timeline_markers=[]), space_data=types.SimpleNamespace())
        try:
            exec(compile(body, str(ROOT / "ui" / "timeline_overlay.py"), "exec"), namespace)
            row = namespace["_toolbar_row"](context)
            self.assertIn("ブロック", measurements)
            self.assertEqual(next(item[2] for item in row.items if item[0] == "STAGE_CYCLE"), "ブロック")
        finally:
            if old_prefs is None:
                sys.modules.pop(prefs_name, None)
            else:
                sys.modules[prefs_name] = old_prefs

    def test_chinese_short_help_stops_at_sentence_without_spaces(self):
        old = sys.modules.get("bpy")
        sys.modules["bpy"] = types.SimpleNamespace()
        try:
            explainers = importlib.import_module(PACKAGE + ".core.explainers")
            self.assertEqual(explainers.short("选择关键帧。然后选择工具。"), "选择关键帧")
        finally:
            if old is None:
                sys.modules.pop("bpy", None)
            else:
                sys.modules["bpy"] = old

    def test_saved_layout_names_stay_literal(self):
        source = ast.parse((ROOT / "ui" / "timeline_settings.py").read_text(encoding="utf-8"))
        function = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == "_choices")
        data = {"saved": [{"id": "my-layout", "name": "Settings"}]}
        i18n._catalogs["ja"].update({"Recommended": "推奨", "Built-in two-slider layout": "標準レイアウト",
                                    "Load or manage {layout}": "{layout}を管理"})
        namespace = {"getattr": getattr, "record": lambda context: data, "_layout_items": {},
                     "active_language": lambda: "ja", "T": i18n.T, "F": i18n.F}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "actual_layout_choices", "exec"), namespace)
        items = namespace["_choices"](types.SimpleNamespace(_record=data), None)
        self.assertEqual(items[0][1], "推奨")
        self.assertEqual(items[1][0], "my-layout")
        self.assertEqual(items[1][1], "Settings")
        self.assertEqual(items[1][2], "Settingsを管理")
        self.assertEqual(data["saved"][0]["name"], "Settings")
        enum = next(node.value if node.value is not None else node.annotation for node in ast.walk(source) if isinstance(node, ast.AnnAssign)
                    and getattr(node.target, "id", "") == "layout_choice")
        context = next(ast.literal_eval(kw.value) for kw in enum.keywords if kw.arg == "translation_context")
        self.assertEqual(context, "AnimAssist.UserLayoutName")

    def test_actual_session_status_keeps_ids_and_counts(self):
        source = ast.parse((ROOT / "ui" / "p7_panels.py").read_text(encoding="utf-8"))
        function = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == "_session_info_label")
        namespace = {"F": i18n.F}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "actual_session_status", "exec"), namespace)
        session = types.SimpleNamespace(short_id="Settings", created_objects=[1, 2, 3], created_constraints=[1, 2])
        key = "Session {session}  |  {objects} obj  {constraints} con"
        i18n._catalogs["ja"][key] = "セッション {session} | オブジェクト {objects} | 制約 {constraints}"
        self.assertEqual(namespace["_session_info_label"](None, session), "セッション Settings | オブジェクト 3 | 制約 2")
        self.assertEqual(session.short_id, "Settings")
        i18n.active_language = lambda context=None: "en"
        self.assertEqual(namespace["_session_info_label"](None, session), "Session Settings  |  3 obj  2 con")

    def test_actual_driver_diagnostics_keep_variable_and_path_data(self):
        drivers = importlib.import_module(PACKAGE + ".core.driver_context")
        i18n._catalogs["ja"].update({"Variable {name}: missing target.": "変数 {name}: 対象がありません。",
                                    "Channel is locked.": "チャンネルはロックされています。"})
        variable = types.SimpleNamespace(name="Settings", type="SINGLE_PROP", targets=[types.SimpleNamespace(id=None)])
        curve = types.SimpleNamespace(driver=types.SimpleNamespace(is_valid=True, variables=[variable]),
                                      id_data=types.SimpleNamespace(is_editable=True), lock=True, mute=False)
        self.assertEqual(drivers.driver_issues(curve, None), ["チャンネルはロックされています。", "変数 Settings: 対象がありません。"])
        self.assertEqual(variable.name, "Settings")

    def test_timing_report_injects_language_without_changing_pure_results(self):
        diagnostics = importlib.import_module(PACKAGE + ".core.p6_diagnostics")
        report = diagnostics.TimingDiagnostics()
        report.key_count, report.frame_span, report.avg_spacing, report.score = 3, 8, 4, 90
        english = diagnostics.format_diagnostics_report(report, "Settings")
        self.assertEqual(english, "=== Settings ===\nKeys: 3  |  Span: 8f  |  Avg spacing: 4.0f\nTiming Score: 90/100\nNo significant gaps.\nNo key clusters.")
        i18n._catalogs["ja"]["Timing Score: {score:.0f}/100"] = "タイミング得点: {score:.0f}/100"
        localized = diagnostics.format_diagnostics_report(report, "Settings", format_text=i18n.F)
        self.assertIn("タイミング得点: 90/100", localized)
        self.assertIn("=== Settings ===", localized)
        self.assertEqual((report.key_count, report.frame_span, report.avg_spacing, report.score), (3, 8, 4, 90))

    def test_tool_description_translates_before_adding_guidance(self):
        tree = ast.parse((ROOT / "ui" / "timeline_strip.py").read_text(encoding="utf-8"))
        owner = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "ANIMASSIST_OT_timeline_tool")
        method = next(node for node in owner.body if isinstance(node, ast.FunctionDef) and node.name == "description")
        method.decorator_list = []
        i18n._catalogs["ja"].update({"Base tool help": "基本の説明", " Unavailable: {reason}.": " 使用不可: {reason}。"})
        explainers = importlib.import_module(PACKAGE + ".core.explainers")
        old = explainers.operator_text
        explainers.operator_text = lambda _identifier: "Base tool help"
        namespace = {"__package__": PACKAGE + ".ui", "T": i18n.T, "F": i18n.F,
                     "_ACTIONS": {"TEST": ("test", None, "Test")}, "_operator": lambda _action: True,
                     "command_description": lambda _action, text: text,
                     "_unavailable": lambda *_args: "Settings", "_target": lambda _context: None}
        try:
            exec(compile(ast.Module(body=[method], type_ignores=[]), "actual_tool_description", "exec"), namespace)
            shown = namespace["description"](types.SimpleNamespace(), None, types.SimpleNamespace(action="TEST"))
            self.assertEqual(shown, "基本の説明 使用不可: Settings。")
        finally:
            explainers.operator_text = old

    def test_nla_locked_track_guidance_preserves_user_names(self):
        tree = ast.parse((ROOT / "core" / "nla_context.py").read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "require_editable")
        namespace = {"T": i18n.T, "F": i18n.F, "in_nla": lambda _context: True}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "actual_nla_editability", "exec"), namespace)
        i18n._catalogs["ja"]["Unlock the editable track for {owner}: {track}"] = "{owner} のトラック {track} を解除"
        context = types.SimpleNamespace(scene=types.SimpleNamespace(is_nla_tweakmode=False))
        item = types.SimpleNamespace(owner=types.SimpleNamespace(is_editable=True, name="Settings"),
                                     track=types.SimpleNamespace(lock=True, name="Frame"))
        with self.assertRaisesRegex(ValueError, "Settings のトラック Frame を解除"):
            namespace["require_editable"](context, [item])

    def test_model_error_keeps_english_exception_and_localizes_template(self):
        i18n._catalogs["ja"]["{label} must be a finite number"] = "{label} には有限の数値を指定"
        with self.assertRaises(ValueError) as caught:
            model.finite(float("inf"), "Settings")
        self.assertEqual(str(caught.exception), "Settings must be a finite number")
        self.assertEqual(i18n.error_text(caught.exception), "Settings には有限の数値を指定")
        self.assertEqual(caught.exception.ui_fields, {"label": "Settings"})
        i18n.active_language = lambda context=None: "en"
        self.assertEqual(i18n.error_text(caught.exception), str(caught.exception))

    def test_pose_comparison_formatter_keeps_paths_and_reference_names(self):
        tree = ast.parse((ROOT / "core" / "pose_compare.py").read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "compare_snapshots")
        function.returns = None
        for argument in function.args.args + function.args.kwonlyargs:
            argument.annotation = None
        namespace = {}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "actual_pose_comparison", "exec"), namespace)
        first = types.SimpleNamespace(values={}, label="Settings")
        second = types.SimpleNamespace(values={("Frame", 0): 1}, label="Settings")
        i18n._catalogs["ja"]["+ {path}[{index}]  (only in {label})"] = "+ {path}[{index}]（{label} のみ）"
        self.assertEqual(namespace["compare_snapshots"](first, second), ["+ Frame[0]  (only in Settings)"])
        self.assertEqual(namespace["compare_snapshots"](first, second, format_text=i18n.F), ["+ Frame[0]（Settings のみ）"])
        self.assertEqual(second.values, {("Frame", 0): 1})

    def test_breakdown_formatter_keeps_owner_name_and_early_return(self):
        tree = ast.parse((ROOT / "core" / "breakdown_core.py").read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "apply_breakdown")
        function.returns = None
        for argument in function.args.args + function.args.kwonlyargs:
            argument.annotation = None
        namespace = {"BreakdownResult": lambda: types.SimpleNamespace(messages=[]), "_scene_writable": lambda _scene: True}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "actual_breakdown", "exec"), namespace)
        context = types.SimpleNamespace(scene=object())
        owner = types.SimpleNamespace(name="Settings", animation_data=None)
        i18n._catalogs["ja"]["{object}: no action to write to."] = "{object}: 書き込み先のアクションなし。"
        self.assertEqual(namespace["apply_breakdown"](context, owner, None, None).messages, ["Settings: no action to write to."])
        self.assertEqual(namespace["apply_breakdown"](context, owner, None, None, format_text=i18n.F).messages,
                         ["Settings: 書き込み先のアクションなし。"])
        self.assertIsNone(owner.animation_data)

    def test_macro_formatter_preserves_dispatch_and_existing_undo_checkpoint(self):
        tree = ast.parse((ROOT / "core" / "p10_macro_engine.py").read_text(encoding="utf-8"))
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                     and node.name in {"execute_macro", "validate_macro"}]
        for function in functions:
            function.returns = None
            for argument in function.args.args + function.args.kwonlyargs:
                argument.annotation = None
        calls, checkpoints = [], []
        state = types.SimpleNamespace(is_batch_processing=False)
        logger = types.SimpleNamespace(debug=lambda *_a, **_k: None, info=lambda *_a, **_k: None,
                                       error=lambda *_a, **_k: None, exception=lambda *_a, **_k: None)
        ops = types.SimpleNamespace(ed=types.SimpleNamespace(undo_push=lambda **kw: checkpoints.append(kw["message"])),
                                    fixture=types.SimpleNamespace(run=lambda *args, **kw: calls.append((args, kw)) or {"FINISHED"}))
        namespace = {"bpy": types.SimpleNamespace(ops=ops), "runtime": types.SimpleNamespace(get_state=lambda: state),
                     "MacroResult": lambda **kw: types.SimpleNamespace(**kw), "_log": logger, "time": time}
        exec(compile(ast.Module(body=functions, type_ignores=[]), "actual_macro_engine", "exec"), namespace)
        steps = [types.SimpleNamespace(enabled=True, op_id="fixture.run", kwargs={"name": "Settings"}),
                 types.SimpleNamespace(enabled=True, op_id="Settings", kwargs={})]
        i18n._catalogs["ja"].update({"Macro ({count} steps)": "マクロ（{count} ステップ）",
                                    "Step {index}: Invalid op_id format '{operator}'": "ステップ {index}: 無効な ID '{operator}'"})
        errors = namespace["validate_macro"](steps, format_text=i18n.F)
        self.assertEqual(errors, ["ステップ 1: 無効な ID 'Settings'"])
        result = namespace["execute_macro"](steps, None, format_text=i18n.F)
        self.assertEqual(calls, [(("EXEC_DEFAULT",), {"name": "Settings"})])
        self.assertEqual(checkpoints, ["マクロ（2 ステップ）"])
        self.assertFalse(state.is_batch_processing)
        self.assertEqual((result.steps_run, result.steps_skipped, result.success), (1, 0, False))

    def test_actual_settings_dialog_reports_template_error_without_writing(self):
        tree = ast.parse((ROOT / "ui" / "timeline_settings.py").read_text(encoding="utf-8"))
        owner = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "ANIMASSIST_OT_toolbar_settings")
        method = next(node for node in owner.body if isinstance(node, ast.FunctionDef) and node.name == "execute")
        calls, reports = [], []
        namespace = {"write": lambda *args: calls.append(args), "editor": lambda _context: None,
                     "_editors": {}, "error_text": i18n.error_text}
        exec(compile(ast.Module(body=[method], type_ignores=[]), "actual_settings_execute", "exec"), namespace)
        i18n._catalogs["ja"]["{label} must be a finite number"] = "{label} には有限の数値を指定"
        dialog = types.SimpleNamespace(serialize=lambda: model.finite(float("inf"), "Settings"),
                                       report=lambda kind, text: reports.append((kind, text)))
        context = types.SimpleNamespace(window=types.SimpleNamespace(as_pointer=lambda: 17))
        self.assertEqual(namespace["execute"](dialog, context), {"CANCELLED"})
        self.assertEqual(reports, [({"WARNING"}, "Settings には有限の数値を指定")])
        self.assertEqual(calls, [])

    def test_owned_help_callback_output_is_not_translated_twice(self):
        explainers = importlib.import_module(PACKAGE + ".core.explainers")
        old_mode = explainers.mode
        class Callback:
            bl_label = "Help"
            _aa_raw = lambda cls, context, properties: "Settings"
            _aa_short = classmethod(lambda cls, context, properties: "Settings")
        explainers._full[Callback] = "Summary"
        try:
            explainers.mode = lambda context: "FULL"
            self.assertEqual(explainers._describe(Callback, None, None), "Settings")
            self.assertEqual(explainers.raw_description(Callback, None, None), "Settings")
            explainers.mode = lambda context: "SHORT"
            self.assertEqual(explainers._describe(Callback, None, None), "Settings")
            explainers.mode = lambda context: "OFF"
            self.assertEqual(explainers._describe(Callback, None, None), "ヘルプ")
            del Callback._aa_raw
            explainers.mode = lambda context: "FULL"
            self.assertEqual(explainers._describe(Callback, None, None), "概要")
        finally:
            explainers.mode = old_mode
            explainers._full.pop(Callback, None)

    def test_lifecycle_warning_translates_before_scene_and_versions(self):
        tree = ast.parse((ROOT / "core" / "lifecycle.py").read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "check_saved_versions")
        message = next(node.args[0].value for node in ast.walk(function)
                       if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "F")
        i18n._catalogs["ja"][message] = "{scene}: 保存版 {saved}、対応版 {installed}"
        scene = types.SimpleNamespace(name="Settings", anim_assist=types.SimpleNamespace(migration_version=20))
        namespace = {"__package__": PACKAGE + ".core", "bpy": types.SimpleNamespace(data=types.SimpleNamespace(scenes=[scene])),
                     "constants": types.SimpleNamespace(MIGRATION_CURRENT_VERSION=19, SCENE_PROP_ATTR="anim_assist"),
                     "_log": types.SimpleNamespace(warning=lambda *_args: None)}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "actual_lifecycle_warning", "exec"), namespace)
        self.assertEqual(namespace["check_saved_versions"](), ["Settings: 保存版 20、対応版 19"])
        self.assertEqual(scene.name, "Settings")

    def test_finite_native_dependencies_preserve_real_rna_contexts(self):
        spec = importlib.util.spec_from_file_location("aa_native_dependency_test", ROOT / "i18n" / "extract.py")
        extractor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(extractor)
        manifest = json.loads((ROOT / "i18n" / "native_dependencies.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["entries"]), 28)
        messages = {entry["msgid"]: entry for entry in extractor.extract()["entries"]}
        for dependency in manifest["entries"]:
            entry = messages[dependency["msgid"]]
            self.assertTrue(set(dependency["contexts"]) <= set(entry["contexts"]))
            for reference in dependency["native_sources"]:
                self.assertIn(reference, entry["native_sources"])
                self.assertNotIn("path", reference)
                self.assertNotIn("line", reference)
                expected = "Action" if ".fmodifier_add." in reference["rna"] and reference["kind"] == "enum.name" else "*"
                self.assertEqual(reference["context"], expected)
                self.assertEqual(reference["host"], "5.3.0 Alpha")

    def test_discovery_keeps_canonical_help_and_searches_both_languages(self):
        registry = importlib.import_module(PACKAGE + ".core.p10_tool_registry")
        saved = dict(registry._registry)
        old_bpy = sys.modules.get("bpy")
        operators_name = PACKAGE + ".operators"
        old_operators = sys.modules.get(operators_name)
        class NativeOperator:
            pass
        class Demo(NativeOperator):
            bl_idname = "animassist.demo"
            bl_label = "Settings"
            bl_description = "Summary"
            bl_options = set()
            execute = lambda *_args: {"FINISHED"}
        Demo.__module__ = PACKAGE + ".operators.p3_fixture"
        proxy = types.SimpleNamespace(get_rna_type=lambda: types.SimpleNamespace(name="Native Name", description="(undocumented operator)"))
        sys.modules["bpy"] = types.SimpleNamespace(types=types.SimpleNamespace(Operator=NativeOperator),
                                                  ops=types.SimpleNamespace(animassist=types.SimpleNamespace(demo=proxy)))
        sys.modules[operators_name] = types.SimpleNamespace(CLASSES=[Demo])
        try:
            registry.clear()
            self.assertEqual(registry.seed_registered_tools(), 1)
            entry = registry.get_tool("animassist.demo")
            self.assertEqual((entry.label, entry.description, entry.phase), ("Settings", "Summary", 3))
            self.assertEqual(registry.search_tools("設定"), [entry])
            self.assertEqual(registry.search_tools("Settings"), [entry])
            self.assertEqual(registry.search_tools("概要"), [entry])
            i18n.active_language = lambda context=None: "en"
            self.assertEqual(registry.search_tools("設定"), [])
            self.assertEqual(registry.search_tools("Settings"), [entry])
            self.assertEqual((entry.label, entry.description), ("Settings", "Summary"))
        finally:
            registry._registry.clear()
            registry._registry.update(saved)
            for key, old in (("bpy", old_bpy), (operators_name, old_operators)):
                if old is None:
                    sys.modules.pop(key, None)
                else:
                    sys.modules[key] = old

    def test_cached_audio_fallback_translates_live_without_changing_saved_reason(self):
        adapter = importlib.import_module(PACKAGE + ".core.p12_rhubarb_adapter")
        cues = [adapter.PhonemeCue(0.0, "rest")]
        with patch.object(adapter, "is_rhubarb_available", return_value=False), patch.object(adapter, "analyze_amplitude", return_value=cues) as amplitude:
            result = adapter.analyze("Settings {audio}.wav", backend="RHUBARB")
            original = "Rhubarb executable not found on PATH"
            i18n._catalogs["ja"][original] = "Rhubarb 実行ファイルが PATH にありません"
            self.assertIs(result.cues, cues)
            self.assertIsInstance(result.fallback_reason, str)
            self.assertEqual(result.fallback_reason, original)
            self.assertEqual(i18n.error_text(result.fallback_reason), "Rhubarb 実行ファイルが PATH にありません")
            i18n.active_language = lambda context=None: "en"
            self.assertEqual(i18n.error_text(result.fallback_reason), original)
            self.assertEqual(json.loads(json.dumps(asdict(copy.deepcopy(result))))["fallback_reason"], original)
            self.assertEqual(set(asdict(result)), {"backend", "cues", "fallback_used", "fallback_reason"})
            amplitude.assert_called_once_with("Settings {audio}.wav")

    def test_failed_audio_process_reports_translated_template_and_literal_stderr(self):
        adapter = importlib.import_module(PACKAGE + ".core.p12_rhubarb_adapter")
        stderr = "Settings {value} C:/Audio/file.wav"
        process = types.SimpleNamespace(returncode=2, stderr=stderr, stdout="")
        with patch.object(adapter, "is_rhubarb_available", return_value=True), patch.object(adapter.subprocess, "run", return_value=process), patch.object(adapter, "analyze_amplitude", return_value=[]):
            result = adapter.analyze("Settings.wav", backend="RHUBARB", rhubarb_path="C:/Tools/rhubarb.exe")
        self.assertEqual(result.fallback_reason, "rhubarb exited 2: " + stderr)
        i18n._catalogs["ja"].update({"rhubarb exited {code}: {stderr}": "Rhubarb 終了 {code}: {stderr}",
                                    "Backend fallback: {p0}": "代替処理: {p0}"})
        tree = ast.parse((ROOT / "operators" / "p12_bake_ops.py").read_text(encoding="utf-8"))
        branch = next(node for node in ast.walk(tree) if isinstance(node, ast.If)
                      and isinstance(node.test, ast.Attribute) and node.test.attr == "fallback_used")
        messages = []
        namespace = {"F": i18n.F, "error_text": i18n.error_text, "analyze_result": result,
                     "self": types.SimpleNamespace(report=lambda _kind, text: messages.append(text))}
        exec(compile(ast.Module(body=[branch], type_ignores=[]), "actual_backend_fallback_report", "exec"), namespace)
        self.assertEqual(messages, ["代替処理: Rhubarb 終了 2: " + stderr])
        self.assertEqual(result.fallback_reason, "rhubarb exited 2: " + stderr)

    def test_audio_invocation_and_json_failures_keep_deferred_templates(self):
        adapter = importlib.import_module(PACKAGE + ".core.p12_rhubarb_adapter")
        variants = ((OSError("Settings {file}.wav"), None, "rhubarb subprocess failed: {error}"),
                    (None, types.SimpleNamespace(returncode=0, stderr="", stdout="not JSON"),
                     "rhubarb output not valid JSON: {error}"))
        for failure, process, template in variants:
            with self.subTest(template=template), patch.object(adapter, "is_rhubarb_available", return_value=True), patch.object(adapter.subprocess, "run", side_effect=failure, return_value=process), patch.object(adapter, "analyze_amplitude", return_value=[]):
                result = adapter.analyze("Settings.wav", backend="RHUBARB", rhubarb_path="C:/Tools/rhubarb.exe")
            self.assertTrue(result.fallback_used)
            self.assertEqual(result.backend, "AMPLITUDE")
            self.assertEqual(result.fallback_reason.ui_template, template)
            diagnostic = result.fallback_reason.ui_fields["error"]
            i18n._catalogs["ja"][template] = "処理失敗: {error}"
            self.assertEqual(i18n.error_text(result.fallback_reason), "処理失敗: " + diagnostic)
            self.assertEqual(json.loads(json.dumps(result.fallback_reason)), template.format(error=diagnostic))

    def test_actual_failure_helper_keeps_completed_message_and_literal_detail(self):
        tree = ast.parse((ROOT / "core" / "helpers.py").read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "report_failure")
        function.returns = None
        for argument in function.args.args + function.args.kwonlyargs:
            argument.annotation = None
        namespace = {"T": i18n.T, "F": i18n.F}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "actual_failure_helper", "exec"), namespace)
        i18n._catalogs["ja"].update({"Problem": "問題", "Repair": "修正",
                                    "{what} ({detail}). {fix}": "{fix} — {what}（{detail}）",
                                    "修正 — 問題（Settings）": "incorrect second lookup"})
        messages = []
        operator = types.SimpleNamespace(report=lambda _kind, text: messages.append(text))
        self.assertEqual(namespace["report_failure"](operator, "Problem", "Repair", detail="Settings"), {"CANCELLED"})
        self.assertEqual(messages, ["修正 — 問題（Settings）"])

    def test_cached_last_bake_panel_translates_live_and_records_are_not_reloaded(self):
        adapter = importlib.import_module(PACKAGE + ".core.p12_rhubarb_adapter")
        session = importlib.import_module(PACKAGE + ".core.p12_session")
        caches = (session._bake_records, session._analyze_cache, session._envelope_cache)
        saved = [dict(cache) for cache in caches]
        reason = adapter.FallbackReason.from_template("rhubarb exited {code}: {stderr}", code=2, stderr="Settings {value}")
        record = session.BakeRecord(fallback_used=True, fallback_reason=reason)
        tree = ast.parse((ROOT / "ui" / "p12_panels.py").read_text(encoding="utf-8"))
        branch = next(node for node in ast.walk(tree) if isinstance(node, ast.If)
                      and isinstance(node.test, ast.Attribute) and node.test.attr == "fallback_used")
        lines = []
        namespace = {"F": i18n.F, "error_text": i18n.error_text, "record": record,
                     "sub": types.SimpleNamespace(label=lambda **kwargs: lines.append(kwargs))}
        i18n._catalogs["ja"].update({"rhubarb exited {code}: {stderr}": "Rhubarb 終了 {code}: {stderr}",
                                    "Fallback: {p0}": "代替処理: {p0}"})
        try:
            session.record_bake("Settings", record)
            self.assertIs(session.get_last_bake("Settings"), record)
            self.assertIs(record.fallback_reason, reason)
            exec(compile(ast.Module(body=[branch], type_ignores=[]), "actual_last_bake_panel", "exec"), namespace)
            self.assertEqual(lines[-1]["text"], "代替処理: Rhubarb 終了 2: Settings {value}")
            self.assertFalse(lines[-1]["translate"])
            i18n.active_language = lambda context=None: "en"
            exec(compile(ast.Module(body=[branch], type_ignores=[]), "actual_last_bake_panel", "exec"), namespace)
            self.assertEqual(lines[-1]["text"], "Fallback: rhubarb exited 2: Settings {value}")
            self.assertEqual(json.loads(json.dumps(asdict(record)))["fallback_reason"], str(reason))
            session.clear_all_sessions()
            self.assertIsNone(session.get_last_bake("Settings"))
        finally:
            for cache, original in zip(caches, saved):
                cache.clear()
                cache.update(original)


if __name__ == "__main__":
    unittest.main()
