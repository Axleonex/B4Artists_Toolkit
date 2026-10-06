"""Ghost Tool 3.6 Round C: folders, checked rows, Apply to Checked, batch actions. Run with:
    bforartists --background --factory-startup --python tests/test_ghost_paths_folders.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ghost_paths import GhostPaths, _cube, _rig, bpy, gd, ghost_tool, mp  # noqa: E402


class _Layout:
    """Records what a draw function asks for; operator() returns a settable stand-in."""

    def __init__(self, calls=None):
        self.calls = [] if calls is None else calls
        self.enabled, self.scale_y, self.operator_context = True, 1.0, 'INVOKE_DEFAULT'

    def row(self, **_kw):
        return _Layout(self.calls)

    column = row

    def operator(self, idname, **kw):
        op = SimpleNamespace()
        self.calls.append(("op", idname, kw.get("text"), kw.get("icon"), op))
        return op

    def prop(self, _data, name, **kw):
        self.calls.append(("prop", name, kw.get("text"), kw.get("icon"), None))

    def menu(self, idname, **kw):
        self.calls.append(("menu", idname, kw.get("text"), kw.get("icon"), None))

    def label(self, **kw):
        self.calls.append(("label", kw.get("text"), None, kw.get("icon"), None))

    def template_list(self, *args, **_kw):
        self.calls.append(("list", args[0], None, None, None))

    def separator(self, **_kw):
        pass


def _valid_icons():
    return set(bpy.types.UILayout.bl_rna.functions["operator"].parameters["icon"].enum_items.keys())


class GhostPathFolders(unittest.TestCase):
    """Uses GhostPaths' scene setup without re-running its tests."""

    setUp = GhostPaths.setUp
    select_bones = GhostPaths.select_bones
    _drop_deferred_timer = GhostPaths._drop_deferred_timer

    @classmethod
    def setUpClass(cls):
        with patch.object(ghost_tool, "_clear_pycache"):
            ghost_tool.register()

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def _path(self, object_name, bone_name="", folder=""):
        e = self.settings.motion_paths.add()
        e.object_name, e.bone_name, e.folder = object_name, bone_name, folder
        return e

    def _folder(self, name, key, collapsed=False):
        f = self.settings.motion_paths.add()
        f.is_folder, f.object_name, f.folder_key, f.collapsed = True, name, key, collapsed
        return f

    def test_folder_rows_group_and_hide_children(self):
        rig = _rig()
        self._path(rig.name, "upper")                    # 0 top level
        self._folder("Arms", "k1")                       # 1
        self._path(rig.name, "lower", folder="k1")       # 2 in Arms
        self._path("Cube")                               # 3 top level
        self._folder("Legs", "k2", collapsed=True)       # 4
        self._path("Other", folder="k2")                 # 5 in Legs, hidden
        self._path("Lost", folder="gone")                # 6 its folder is gone: top level
        self.assertEqual(mp.list_rows(self.settings),
                         [(0, True), (3, True), (6, True), (1, True), (2, True), (4, True), (5, False)])
        self.settings.motion_paths[1].object_name = "Arms renamed"   # a rename keeps the folder's paths
        self.assertIn((2, True), mp.list_rows(self.settings))

    def test_list_filter_items_orders_and_hides(self):
        from ghost_tool.ui_panel import GHOST_UL_paths
        self._path("A")                          # 0
        self._folder("Arms", "k1")               # 1
        self._path("B", folder="k1")             # 2
        self._path("C")                          # 3
        self._folder("Legs", "k2", collapsed=True)   # 4
        self._path("D", folder="k2")             # 5
        shown = 1 << 30
        flags, order = GHOST_UL_paths.filter_items(SimpleNamespace(bitflag_filter_item=shown),
                                                   bpy.context, self.settings, "motion_paths")
        self.assertEqual(order, [0, 2, 3, 1, 4, 5])   # item i is drawn at position order[i]
        self.assertEqual(flags, [shown] * 5 + [0])

    def test_list_rows_draw_folder_and_indented_path(self):
        from ghost_tool.ui_panel import GHOST_UL_paths
        folder = self._folder("Arms", "k1")
        child = self._path("Cube", folder="k1")
        top = self._path("Cube")
        draw = GHOST_UL_paths.draw_item

        def drawn(item, index):
            layout = _Layout()
            draw(None, bpy.context, layout, self.settings, item, 0, None, "", index)
            return layout.calls

        calls = drawn(folder, 0)
        self.assertEqual([(c[0], c[1]) for c in calls],
                         [("prop", "checked"), ("op", "ghost_tool.paths_toggle_folder"),
                          ("op", "ghost_tool.paths_toggle_visible"), ("prop", "object_name"),
                          ("op", "ghost_tool.paths_remove")])
        self.assertEqual(calls[1][4].index, 0)
        folder.collapsed = True
        self.assertEqual(drawn(folder, 0)[1][3], 'RIGHTARROW')
        child_calls, top_calls = drawn(child, 1), drawn(top, 2)
        self.assertEqual(child_calls[1][:4], ("label", "", None, 'BLANK1'))   # indented under its folder
        self.assertNotIn('BLANK1', [c[3] for c in top_calls])
        icons = _valid_icons()
        for call in calls + child_calls + top_calls:
            if call[3]:
                self.assertIn(call[3], icons)

    def test_popover_and_checked_menus_draw(self):
        from ghost_tool import ui_panel
        self._path("A")
        self._folder("Arms", "k1")
        layout = _Layout()
        ui_panel._draw_motion_paths(layout, bpy.context)
        names = [c[1] for c in layout.calls]
        for name in ("ghost_tool.paths_add_folder", "ghost_tool.paths_apply_to_checked", "GHOST_MT_paths_checked"):
            self.assertIn(name, names)
        self.assertIn(("label", "Motion paths · 1"), [(c[0], c[1]) for c in layout.calls])   # folders not counted
        menu = _Layout()
        ui_panel.GHOST_MT_paths_checked.draw(SimpleNamespace(layout=menu), bpy.context)
        ops = [c for c in menu.calls if c[0] == "op"]
        self.assertEqual([c[4].action for c in ops if c[1] == "ghost_tool.paths_checked_action"],
                         ['SHOW', 'HIDE', 'RESET_RANGE', 'REMOVE'])
        self.assertTrue(ops[-1][4].include_range)
        self.assertIn(("menu", "GHOST_MT_paths_move_to"), [(c[0], c[1]) for c in menu.calls])
        move = _Layout()
        ui_panel.GHOST_MT_paths_move_to.draw(SimpleNamespace(layout=move), bpy.context)
        self.assertEqual([(c[2], c[4].action, c[4].folder) for c in move.calls],
                         [("Top Level", 'MOVE', ""), ("Arms", 'MOVE', "k1")])
        icons = _valid_icons()
        for call in layout.calls + menu.calls + move.calls:
            if call[3]:
                self.assertIn(call[3], icons)
        for name in ("GHOST_MT_paths_checked", "GHOST_MT_paths_move_to"):
            self.assertTrue(hasattr(bpy.types, name))

    def test_folder_visibility_gates_children(self):
        rig = _rig()
        self._folder("Arms", "k1").visible = False
        self._path(rig.name, "lower", folder="k1")
        self._path(rig.name, "upper")
        self.assertEqual([t.key for t in mp.pinned_targets(self.scene)], [(rig.name, "upper")])
        self.settings.motion_paths[0].visible = True
        self.assertEqual(len(mp.pinned_targets(self.scene)), 2)

    def test_hidden_pinned_path_does_not_return_as_follow_path(self):
        # Review C1 F1: Follow is for unpinned selections (design §2 tests: "unpinned selected bone draws grey").
        rig = _rig()
        self._folder("Arms", "k1").visible = False
        self._path(rig.name, "lower", folder="k1")
        self._path(rig.name, "upper").visible = False
        self.settings.paths_follow_selection = True
        self.select_bones(rig, "upper", "lower")
        self.assertEqual(mp.all_targets(bpy.context), [])
        self.select_bones(rig, "lower")
        self.settings.motion_paths.clear()   # unpinned now: Follow draws it grey
        self.assertEqual([(t.key, t.pinned) for t in mp.all_targets(bpy.context)], [((rig.name, "lower"), False)])
        bpy.ops.object.mode_set(mode='OBJECT')
        self.settings.paths_follow_selection = False
        self._drop_deferred_timer()

    def test_folder_is_never_a_path(self):
        cube = _cube()
        folder = self._folder(cube.name, "k1")   # a folder may share an object's name
        bpy.context.view_layer.objects.active = cube
        self.assertFalse(mp.entry_is_missing(folder))
        self.assertEqual(mp.pinned_targets(self.scene), [])
        self.assertEqual(mp.active_entry_index(bpy.context), -1)
        self.settings.motion_paths_index = 0
        self.assertIsNone(mp.list_active_key(self.settings))
        self.assertEqual(folder.label, cube.name)

    def test_removing_folder_keeps_paths(self):
        rig = _rig()
        self._folder("Arms", "k1")
        self._path(rig.name, "lower", folder="k1")
        mp.refresh_paths(bpy.context)
        bpy.ops.ghost_tool.paths_remove(index=0)
        self.assertEqual([(e.bone_name, e.folder, e.is_folder) for e in self.settings.motion_paths],
                         [("lower", "", False)])
        self.assertIn((rig.name, "lower", 10.0), mp._cache)   # the path kept its samples
        self._drop_deferred_timer()

    def test_add_folder_takes_checked_paths(self):
        rig = _rig()
        self._path(rig.name, "upper").checked = True
        self._path(rig.name, "lower")
        bpy.ops.ghost_tool.paths_add_folder()
        bpy.ops.ghost_tool.paths_add_folder()
        paths = self.settings.motion_paths
        first, second = paths[2], paths[3]
        self.assertEqual((first.object_name, second.object_name), ("Folder", "Folder 2"))
        self.assertTrue(first.folder_key and first.folder_key != second.folder_key)
        self.assertEqual((paths[0].folder, paths[0].checked), (first.folder_key, False))
        self.assertEqual(paths[1].folder, "")
        self.assertEqual(self.settings.motion_paths_index, 3)

    def test_apply_to_checked(self):
        rig = _rig()
        source = self._path(rig.name, "upper")
        source.color, source.thickness, source.dot_size, source.in_front = (1.0, 0.0, 0.0), 5, 9, False
        source.anchor = 'TAIL'
        source.use_own_range, source.own_before = True, 1
        target = self._path(rig.name, "lower")
        target.checked = True
        target.color_before = (0.0, 0.0, 1.0)   # a stored choice; the source follows its colour
        untouched = self._path("Cube")
        folder = self._folder("Arms", "k1")
        folder.checked = True
        self.settings.motion_paths_index = 0
        self.assertTrue(bpy.ops.ghost_tool.paths_apply_to_checked.poll())
        bpy.ops.ghost_tool.paths_apply_to_checked()
        self.assertEqual(tuple(target.color), (1.0, 0.0, 0.0))
        self.assertEqual((target.thickness, target.dot_size, target.in_front, target.anchor), (5, 9, False, 'TAIL'))
        for before, colour in zip(target.color_before, target.color):
            self.assertAlmostEqual(before, colour * 0.55, places=5)   # follows like the source
        self.assertFalse(target.use_own_range)                       # range only when asked
        self.assertEqual((untouched.thickness, untouched.dot_size), (2, 6))
        self.assertEqual([round(c, 3) for c in folder.color], [0.96, 0.71, 0.0])   # folders are never written to
        bpy.ops.ghost_tool.paths_apply_to_checked(include_range=True)
        self.assertEqual((target.use_own_range, target.own_before), (True, 1))
        self.settings.motion_paths_index = 3
        self.assertFalse(bpy.ops.ghost_tool.paths_apply_to_checked.poll())   # a folder is no source
        self._drop_deferred_timer()

    def test_apply_to_checked_keeps_object_paths_on_head(self):
        rig = _rig(); cube = _cube()
        source = self._path(rig.name, "upper")
        source.anchor = 'TAIL'
        target = self._path(cube.name)
        target.checked = True
        self.settings.motion_paths_index = 0
        self.assertEqual(mp.apply_to_checked(self.settings, False), 1)
        self.assertEqual(target.anchor, 'HEAD')   # an object origin has no tail
        self._drop_deferred_timer()

    def test_checked_actions(self):
        rig = _rig()
        a = self._path(rig.name, "upper")
        b = self._path(rig.name, "lower")
        folder = self._folder("Arms", "k1")
        a.checked = b.checked = True
        bpy.ops.ghost_tool.paths_checked_action(action='HIDE')
        self.assertEqual((a.visible, b.visible, folder.visible), (False, False, True))
        bpy.ops.ghost_tool.paths_checked_action(action='SHOW')
        self.assertTrue(a.visible and b.visible)
        a.use_own_range = b.use_own_range = True
        bpy.ops.ghost_tool.paths_checked_action(action='RESET_RANGE')
        self.assertFalse(a.use_own_range or b.use_own_range)
        bpy.ops.ghost_tool.paths_checked_action(action='MOVE', folder="k1")
        self.assertEqual((a.folder, b.folder), ("k1", "k1"))
        self.assertEqual(bpy.ops.ghost_tool.paths_checked_action(action='MOVE', folder="nope"), {'CANCELLED'})
        self.assertEqual(a.folder, "k1")
        bpy.ops.ghost_tool.paths_checked_action(action='MOVE', folder="")
        self.assertEqual((a.folder, b.folder), ("", ""))
        self._drop_deferred_timer()

    def test_checked_folder_stands_for_its_paths(self):
        # Review C2 F1: a folder's checkbox did nothing for path actions.
        rig = _rig()
        source = self._path(rig.name, "upper")
        source.thickness = 5
        folder = self._folder("Arms", "k1")
        child = self._path(rig.name, "lower", folder="k1")
        other = self._folder("Legs", "k2")
        folder.checked = True
        self.settings.motion_paths_index = 0
        self.assertEqual(mp.checked_paths(self.settings), [2])
        self.assertTrue(bpy.ops.ghost_tool.paths_apply_to_checked.poll())
        bpy.ops.ghost_tool.paths_apply_to_checked()
        self.assertEqual(child.thickness, 5)
        child.use_own_range = True
        bpy.ops.ghost_tool.paths_checked_action(action='RESET_RANGE')
        self.assertFalse(child.use_own_range)
        bpy.ops.ghost_tool.paths_checked_action(action='HIDE')   # rows: the folder hides, its path keeps its eye
        self.assertEqual((folder.visible, child.visible), (False, True))
        bpy.ops.ghost_tool.paths_checked_action(action='MOVE', folder=other.folder_key)
        self.assertEqual(child.folder, "k2")
        self.assertEqual(mp.checked_paths(self.settings), [])   # it left the checked folder
        self._drop_deferred_timer()

    def test_checked_remove_drops_cache_and_markers(self):
        rig = _rig()
        self._path(rig.name, "upper").checked = True
        self._path(rig.name, "lower")
        mp.refresh_paths(bpy.context)
        self.settings.paths_show_markers = True
        mp.sync_markers(bpy.context)
        self.assertEqual({g.bone_name for g in mp.owned_markers(self.scene)}, {"upper", "lower"})
        bpy.ops.ghost_tool.paths_checked_action(action='REMOVE')
        # Review C1 F2: the removed path's markers are gone from the store itself, not only from
        # the owned set (owned_markers filters the store by ownership, so it cannot see a leak).
        self.assertEqual({g.bone_name for g in gd.GhostStore.get(self.scene)}, {"lower"})
        self.assertEqual([e.bone_name for e in self.settings.motion_paths], ["lower"])
        self.assertFalse(any(k[:2] == (rig.name, "upper") for k in mp._cache))
        self.assertTrue(any(k[:2] == (rig.name, "lower") for k in mp._cache))
        self.assertEqual(bpy.ops.ghost_tool.paths_checked_action(action='REMOVE'), {'CANCELLED'})   # none checked
        self.settings.paths_show_markers = False
        self._drop_deferred_timer()


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(GhostPathFolders))
    print("GHOST_PATH_FOLDERS_RESULT: " + ("PASS" if result.wasSuccessful() else "FAIL"), flush=True)
    if not result.wasSuccessful():
        sys.exit(1)
