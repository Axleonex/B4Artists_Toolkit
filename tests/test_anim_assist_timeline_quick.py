"""Independent quick-toolbar fixtures; model mode needs no Blender imports.

[PowerShell] python tests/test_anim_assist_timeline_quick.py --model-only
[PowerShell] & $env:BFA_EXE --background --factory-startup --python tests/test_anim_assist_timeline_quick.py -- --case prefs
"""

from pathlib import Path
import ast
import importlib.util
import json
import sys
import types
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DEFAULTS = {
    "B25", "B50", "B75", "DRAG", "SMOOTH", "NUDGE_LEFT", "NUDGE_RIGHT",
    "RIPPLE", "RANGE", "ENDS", "MIRROR_SELECTED", "BAKE_STEP", "TRAIL_SHOW",
}
EXPECTED_FAMILIES = ("tween", "curves", "timing", "keys", "pose", "bake", "motion")


def load_catalog():
    package = "_aa_quick_fixture"
    for name, directory in ((package, ROOT / "anim_assist"),
                            (package + ".ui", ROOT / "anim_assist/ui")):
        module = types.ModuleType(name)
        module.__path__ = [str(directory)]
        sys.modules[name] = module
    for suffix, path in (("constants", ROOT / "anim_assist/constants.py"),
                         ("ui.timeline_catalog", ROOT / "anim_assist/ui/timeline_catalog.py")):
        spec = importlib.util.spec_from_file_location(package + "." + suffix, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    return module


CATALOG = load_catalog()


def literal(source, name):
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(name)


class ModelTests(unittest.TestCase):
    def test_defaults(self):
        self.assertEqual(set(CATALOG.DEFAULT_QUICK_ACTIONS), EXPECTED_DEFAULTS)
        self.assertEqual(len(CATALOG.DEFAULT_QUICK_ACTIONS), 13)
        self.assertEqual(CATALOG.selected_quick_actions(None), EXPECTED_DEFAULTS)

    def test_empty(self):
        prefs = types.SimpleNamespace(**{CATALOG.quick_property_name(a): False for a in CATALOG.ACTIONS})
        self.assertEqual(CATALOG.selected_quick_actions(prefs), set())
        clusters = CATALOG.quick_clusters([])
        self.assertEqual(tuple(c[0] for c in clusters), EXPECTED_FAMILIES)
        self.assertTrue(all(not c[2] for c in clusters))

    def test_missing_fields_and_false(self):
        prefs = types.SimpleNamespace(timeline_quick_b50=False, timeline_quick_swap=True)
        self.assertEqual(CATALOG.selected_quick_actions(prefs), EXPECTED_DEFAULTS - {"B50"} | {"SWAP"})

    def test_all_known(self):
        clusters = CATALOG.quick_clusters(CATALOG.ACTIONS)
        actions = [a for _key, _label, selected in clusters for a in selected]
        self.assertEqual(len(actions), 70)
        self.assertEqual(set(actions), set(CATALOG.ACTIONS))
        self.assertEqual(len(set(actions)), len(actions))

    def test_unknown_and_duplicates(self):
        clusters = CATALOG.quick_clusters(["B50", "B50", "not_a_tool", "PUSH_PREV"])
        self.assertEqual(clusters[0][2], ("B50", "PUSH_PREV"))
        self.assertTrue(all(not c[2] for c in clusters[1:]))

    def test_order_is_catalog_order(self):
        forward = CATALOG.quick_clusters(CATALOG.ACTIONS)
        reverse = CATALOG.quick_clusters(reversed(CATALOG.ACTIONS))
        self.assertEqual(forward, reverse)
        self.assertEqual(tuple(c[0] for c in forward), EXPECTED_FAMILIES)

    def test_stable_unique_names(self):
        names = [CATALOG.quick_property_name(a) for a in CATALOG.ACTIONS]
        self.assertEqual(len(set(names)), 70)
        self.assertEqual(CATALOG.quick_property_name("B50"), "timeline_quick_b50")
        with self.assertRaises(KeyError):
            CATALOG.quick_property_name("unknown")

    def test_dispatch_unchanged_from_zip(self):
        with zipfile.ZipFile(ROOT / "releases/b4_anim_assist_v12.4.0.zip") as archive:
            name = next(n for n in archive.namelist() if n.endswith("/ui/timeline_catalog.py"))
            before = archive.read(name).decode("utf-8-sig")
        prior = literal(before, "ACTIONS")
        self.assertEqual({a: row[:2] for a, row in CATALOG.ACTIONS.items()},
                         {a: row[:2] for a, row in prior.items()})
        self.assertEqual(CATALOG.GROUPS, literal(before, "GROUPS"))
        self.assertEqual(CATALOG.EXECUTE_ACTIONS, literal(before, "EXECUTE_ACTIONS"))


def native_setup(package_parent=None):
    import bpy
    import addon_utils
    import os
    isolated = Path(os.environ["BLENDER_USER_CONFIG"]).resolve()
    assert isolated.is_dir(), "Create the isolated CONFIG directory before host launch"
    assert Path(bpy.utils.user_resource("CONFIG")).resolve() == isolated, "Host ignored isolated CONFIG"
    if package_parent is None and "--package-parent" in sys.argv:
        package_parent = Path(sys.argv[sys.argv.index("--package-parent") + 1])
    package = "B4_anim_assist" if package_parent else "anim_assist"
    sys.path.insert(0, str(package_parent or ROOT))
    addon_utils.enable(package, default_set=True, persistent=False)
    addon = sys.modules[package]
    assert bpy.context.preferences.addons.get(package), "addon_utils did not enable preferences"
    from importlib import import_module
    prefs_module = import_module(package + ".prefs")
    prefs = prefs_module.get_prefs()
    assert prefs is not None
    return bpy, addon_utils, addon, prefs_module, prefs


def native_prefs():
    bpy, addon_utils, addon, prefs_module, prefs = native_setup()
    catalog = sys.modules[addon.__package__ + ".ui.timeline_catalog"]
    names = {catalog.quick_property_name(a) for a in catalog.ACTIONS}
    rna = prefs.bl_rna.properties
    assert len(names) == 70 and all(n in rna and rna[n].type == "BOOLEAN" for n in names)
    assert all(rna[n].description for n in names)
    assert rna["timeline_quick_family"].type == "ENUM"
    assert catalog.selected_quick_actions(prefs) == EXPECTED_DEFAULTS
    for name in names:
        setattr(prefs, name, False)
    assert not catalog.selected_quick_actions(prefs)
    prefs.timeline_quick_swap = True
    prefs_module.prepare_timeline_quick_preferences()
    assert catalog.selected_quick_actions(prefs) == {"SWAP"}
    for _ in range(2):
        addon_utils.disable(addon.__package__, default_set=False)
        addon_utils.enable(addon.__package__, default_set=False, persistent=False)
        prefs = prefs_module.get_prefs()
        assert catalog.selected_quick_actions(prefs) == {"SWAP"}
        assert all(n in prefs.bl_rna.properties for n in names)
    print("PREFS OK: 70 bools, descriptions, defaults, empty set, saved values and repeated registration")
    print("HOST", json.dumps({"version": bpy.app.version_string, "binary": bpy.app.binary_path,
                              "actual_bforartists": "show_toolshelf_tabs" in bpy.types.SpaceView3D.bl_rna.properties}))
    addon_utils.disable(addon.__package__, default_set=False)
    assert not getattr(addon.AA_AddonPreferences, "is_registered", False)
    print("UNREGISTER OK")


class RecordingLayout:
    def __init__(self, events=None):
        self.events = [] if events is None else events
        self.enabled = True

    def row(self, **kwargs):
        return RecordingLayout(self.events)

    column = row
    box = row

    def label(self, **kwargs):
        self.events.append(("label", kwargs.get("text")))

    def separator(self):
        pass

    def menu(self, name, **kwargs):
        self.events.append(("menu", name))

    def popover(self, **kwargs):
        self.events.append(("gear", kwargs["panel"]))

    def prop(self, owner, name, **kwargs):
        self.events.append(("prop", name))

    def operator(self, name, **kwargs):
        event = {"id": name, "enabled": self.enabled, **kwargs}
        self.events.append(("operator", event))

        class Properties:
            def __setattr__(self, key, value):
                event[key] = value

        return Properties()


def set_pins(prefs, catalog, actions):
    for action in catalog.ACTIONS:
        setattr(prefs, catalog.quick_property_name(action), action in actions)


def native_draw():
    bpy, addon_utils, addon, prefs_module, prefs = native_setup()
    strip = sys.modules[addon.__package__ + ".ui.timeline_strip"]
    catalog = sys.modules[addon.__package__ + ".ui.timeline_catalog"]
    legacy = [p.identifier for p in bpy.context.scene.anim_assist.bl_rna.properties
              if p.identifier.startswith("header_show_")]
    for selection in (EXPECTED_DEFAULTS, {"SWAP", "OFFSET", "PUSH_PREV"}, set(), set(catalog.ACTIONS)):
        set_pins(prefs, catalog, selection)
        expected = [("gear", "ANIMASSIST_PT_timeline_quick_settings")]
        for key, _label, actions in catalog.GROUPS:
            expected.append(("menu", strip._menu_id(key)))
            expected.extend(("action", a) for a in actions if a in selection)
        for width in (480, 800, 1280, 1920):
            for visible in (True, False):
                for name in legacy:
                    setattr(bpy.context.scene.anim_assist, name, visible)
                context = types.SimpleNamespace(area=types.SimpleNamespace(type="VIEW_3D", width=width), screen=None, scene=bpy.context.scene,
                                               preferences=bpy.context.preferences)
                layout = RecordingLayout()
                strip._draw_toolbar(types.SimpleNamespace(layout=layout), context)
                sequence = [(kind, data) if kind != "operator" else ("action", data["action"])
                            for kind, data in layout.events if kind in {"gear", "menu", "operator"}]
                assert sequence == expected, (width, visible, sequence)
                assert all(not data["enabled"] for kind, data in layout.events if kind == "operator")
    assert strip.ANIMASSIST_OT_timeline_tool.bl_options == {"INTERNAL"}
    print("CLUSTERS OK: four widths, defaults/custom/empty/all70, legacy visibility, disabled positions")


def native_config():
    bpy, addon_utils, addon, prefs_module, prefs = native_setup()
    catalog = sys.modules[addon.__package__ + ".ui.timeline_catalog"]
    scene = bpy.context.scene
    before = [(o.name, tuple(o.location), o.animation_data) for o in scene.objects]
    props = []
    for key, _label, actions in catalog.GROUPS:
        prefs.timeline_quick_family = key
        layout = RecordingLayout()
        prefs_module.draw_timeline_quick_settings(layout, bpy.context, prefs)
        drawn = [name for kind, name in layout.events if kind == "prop" and name.startswith("timeline_quick_")
                 and name != "timeline_quick_family"]
        assert drawn == [catalog.quick_property_name(a) for a in actions if a is not None]
        props.extend(drawn)
    assert len(set(props)) == 70
    set_pins(prefs, catalog, {"SWAP"})
    assert bpy.ops.animassist.reset_timeline_quick_defaults() == {"FINISHED"}
    assert catalog.selected_quick_actions(prefs) == EXPECTED_DEFAULTS
    assert before == [(o.name, tuple(o.location), o.animation_data) for o in scene.objects]
    strip = sys.modules[addon.__package__ + ".ui.timeline_strip"]
    assert "UNDO" not in strip.ANIMASSIST_OT_reset_timeline_quick_defaults.bl_options
    addon_utils.disable(addon.__package__, default_set=False)
    assert not hasattr(bpy.types, "ANIMASSIST_PT_timeline_quick_settings")
    print("CONFIG OK: all70 checkbox fields, all-family reset, no scene mutation, panel unregister")


def native_availability():
    bpy, _addon_utils, addon, _prefs_module, _prefs = native_setup()
    strip = sys.modules[addon.__package__ + ".ui.timeline_strip"]
    timeline = next(a for a in bpy.context.screen.areas if strip.is_timeline(a))
    assert strip._unavailable(bpy.context, None, "B50")
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = None
    assert strip._unavailable(bpy.context, timeline, "SMOOTH")
    assert strip._unavailable(bpy.context, timeline, "MIRROR_SELECTED")
    bpy.context.scene.anim_assist.anim_offset_active = True
    assert not strip._unavailable(bpy.context, timeline, "OFFSET")
    # AST identity protects the existing mode, explicit target Undo and paired context.
    with zipfile.ZipFile(ROOT / "releases/b4_anim_assist_v12.4.0.zip") as z:
        prior = ast.parse(z.read("B4_anim_assist/ui/timeline_strip.py").decode("utf-8-sig"))
    now = ast.parse(Path(strip.__file__).read_text(encoding="utf-8-sig"))
    for name in ("ANIMASSIST_OT_timeline_tool", "_button", "_split", "_remove_strip", "_sync", "timeline_below"):
        old = next(n for n in prior.body if getattr(n, "name", None) == name)
        new = next(n for n in now.body if getattr(n, "name", None) == name)
        assert ast.dump(old) == ast.dump(new), name
    print("AVAILABILITY OK: reasons, active Offset finish, unchanged dispatch/Undo/pairing/lifecycle")


def native_settings():
    import tempfile
    bpy, _utils, addon, prefs_module, prefs = native_setup()
    catalog = sys.modules[addon.__package__ + ".ui.timeline_catalog"]
    settings = sys.modules[addon.__package__ + ".operators.settings_ops"]
    folder = Path(tempfile.mkdtemp(prefix="aa125-settings-"))
    path = folder / "settings.json"
    for selection in (set(), set(catalog.ACTIONS), {"SWAP"}):
        set_pins(prefs, catalog, selection)
        prefs.timeline_quick_family = "pose"
        assert bpy.ops.anim_assist.export_settings(filepath=str(path)) == {"FINISHED"}
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len([k for k in data if k.startswith("timeline_quick_")]) == 71
        set_pins(prefs, catalog, EXPECTED_DEFAULTS)
        prefs.timeline_quick_family = "tween"
        assert bpy.ops.anim_assist.import_settings(filepath=str(path)) == {"FINISHED"}
        assert catalog.selected_quick_actions(prefs) == selection
        assert prefs.timeline_quick_family == "pose"
    invalid = {"timeline_quick_b50": 1, "timeline_quick_swap": "false",
               "timeline_quick_drag": None, "timeline_quick_family": "unknown",
               "timeline_quick_unrecognized": True, "_version": "old"}
    before = catalog.selected_quick_actions(prefs)
    for data in ({"performance_mode": True}, invalid):
        path.write_text(json.dumps(data), encoding="utf-8")
        assert bpy.ops.anim_assist.import_settings(filepath=str(path)) == {"FINISHED"}
        assert catalog.selected_quick_actions(prefs) == before
        assert prefs.timeline_quick_family == "pose"
    original_package = prefs_module.__package__
    for package in ("anim_assist", "B4_anim_assist", "bl_ext.fixture.anim_assist"):
        try:
            prefs_module.__package__ = package
            context = types.SimpleNamespace(preferences=types.SimpleNamespace(
                addons={package: types.SimpleNamespace(preferences=prefs)}))
            assert settings._get_prefs(context) is prefs
            assert settings._prefs_available(context)
        finally:
            prefs_module.__package__ = original_package
    print("SETTINGS OK: empty/all/custom round-trip, legacy, malformed data, three package lookups")


def native_persistence():
    bpy, _utils, addon, _prefs_module, prefs = native_setup()
    catalog = sys.modules[addon.__package__ + ".ui.timeline_catalog"]
    expected = set() if "--empty" in sys.argv else {"SWAP", "OFFSET", "TRAIL_REFRESH"}
    if "--save" in sys.argv:
        set_pins(prefs, catalog, expected)
        prefs.timeline_quick_family = "motion"
        bpy.ops.wm.save_userpref()
        print("PERSISTENCE SAVED", sorted(expected))
    else:
        assert catalog.selected_quick_actions(prefs) == expected, catalog.selected_quick_actions(prefs)
        assert prefs.timeline_quick_family == "motion"
        print("PERSISTENCE OK: restarted process retains", sorted(expected))


def native_dispatch():
    bpy, _utils, addon, _prefs_module, prefs = native_setup()
    strip = sys.modules[addon.__package__ + ".ui.timeline_strip"]
    catalog = sys.modules[addon.__package__ + ".ui.timeline_catalog"]
    context = types.SimpleNamespace(area=None, screen=None, scene=bpy.context.scene,
                                    preferences=bpy.context.preferences)
    set_pins(prefs, catalog, set(catalog.ACTIONS))
    inline = RecordingLayout()
    strip._draw_toolbar(types.SimpleNamespace(layout=inline), context)
    inline_actions = {d["action"]: d for k, d in inline.events if k == "operator"}
    menu_actions = {}
    for menu in strip._menus[:7]:
        layout = RecordingLayout()
        menu.draw(types.SimpleNamespace(layout=layout), context)
        menu_actions.update({d["action"]: d for k, d in layout.events if k == "operator" and "action" in d})
    assert set(inline_actions) == set(menu_actions) == set(catalog.ACTIONS)
    for action in catalog.ACTIONS:
        assert inline_actions[action]["id"] == menu_actions[action]["id"] == "animassist.timeline_tool"
        assert inline_actions[action]["enabled"] == menu_actions[action]["enabled"]
        assert getattr(bpy.ops.animassist, catalog.ACTIONS[action][0]).get_rna_type()
    old = {a for _k, _l, actions in catalog.QUICK_GROUPS for a in actions}
    assert len(old) == 17 and old.issubset(inline_actions)
    assert len(old | EXPECTED_DEFAULTS) == 23
    print("DISPATCH MAPPINGS OK: all70 menu/inline parity, original17 pinnable, union23 effects in GUI harness")


def native_package():
    import hashlib
    bpy, _utils, addon, _prefs_module, prefs = native_setup()
    stage = Path(addon.__file__).resolve().parent
    assert stage.parent == Path(sys.argv[sys.argv.index("--package-parent") + 1]).resolve()
    archive = ROOT / "releases/b4_anim_assist_v12.5.0.zip"
    receipt = json.loads((ROOT / "docs/anim_assist/releases/12.5.0/package-receipt.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == receipt["sha256"]
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if not name.endswith("/"):
                relative = Path(*name.split("/")[1:])
                assert (stage / relative).read_bytes() == z.read(name), name
    assert addon.bl_info["version"] == (12, 5, 0)
    catalog = sys.modules[addon.__package__ + ".ui.timeline_catalog"]
    assert catalog.selected_quick_actions(prefs) == EXPECTED_DEFAULTS
    set_pins(prefs, catalog, set())
    assert not catalog.selected_quick_actions(prefs)
    bpy.ops.animassist.reset_timeline_quick_defaults()
    assert catalog.selected_quick_actions(prefs) == EXPECTED_DEFAULTS
    print("PACKAGE OK", receipt["sha256"], "203 exact files, renamed package, defaults/empty/reset")


if __name__ == "__main__":
    if "--model-only" in sys.argv:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ModelTests))
        if not result.wasSuccessful():
            raise SystemExit(1)
        print("MODEL OK")
    else:
        case = sys.argv[sys.argv.index("--case") + 1] if "--case" in sys.argv else "prefs"
        {"prefs": native_prefs, "draw": native_draw, "config": native_config,
         "availability": native_availability, "settings": native_settings,
         "persistence": native_persistence, "dispatch": native_dispatch, "package": native_package}[case]()
