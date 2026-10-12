"""Actual window, undo and saved-state integration. Run WITHOUT --background.

Uses a factory-startup test process; never reads or modifies an artist's session.
Pointer usability still needs a human pass in the prototype.
"""
import json
import sys
import tempfile
import traceback
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
import ghost_tool
from ghost_tool import settings_editor as editor

RESULT = ROOT / 'docs' / 'ghost_tool' / 'council-workflow-result.json'


def run():
    checks = []
    def check(value, name):
        if not value:
            raise AssertionError(name)
        checks.append(name)
    try:
        ghost_tool.register()
        source = bpy.context.window_manager.windows[0]
        area = next(a for a in source.screen.areas if a.type == 'VIEW_3D')
        region = next(r for r in area.regions if r.type == 'WINDOW')
        with bpy.context.temp_override(window=source, area=area, region=region):
            bpy.ops.mesh.primitive_cube_add()
            obj = bpy.context.active_object
            for frame, x in ((1, 0), (20, 4)):
                obj.location.x = x
                obj.keyframe_insert('location', frame=frame)
            scene = source.scene
            scene.ghost_tool.is_active = False
            entry = scene.ghost_tool.motion_paths.add()
            entry.object_name = obj.name
            scene.ghost_tool.motion_paths_index = 0
            original_selection = tuple(o.name for o in bpy.context.selected_objects)
            count = len(bpy.context.window_manager.windows)
            check(bpy.ops.ghost_tool.open_settings_editor(section='paths') == {'FINISHED'}, 'open_editor')
            window = next(w for w in bpy.context.window_manager.windows if w != source)
            check(len(bpy.context.window_manager.windows) == count + 1, 'one_editor_window')
            check(bpy.ops.ghost_tool.open_settings_editor(section='edit') == {'FINISHED'}, 'reopen_editor')
            check(len(bpy.context.window_manager.windows) == count + 1, 'reuse_editor_window')
            check(tuple(o.name for o in bpy.context.selected_objects) == original_selection, 'selection_preserved_on_travel')
            captured = editor._targets[window.as_pointer()]
            check(editor.resolve_target(captured, scene)[1] == '', 'explicit_target_resolves')

        edit_area = next(a for a in window.screen.areas if a.type == 'VIEW_3D')
        edit_region = next(r for r in edit_area.regions if r.type == 'WINDOW')
        with bpy.context.temp_override(window=window, area=edit_area, region=edit_region):
            check(bpy.ops.ghost_tool.refresh_editor_target() == {'FINISHED'}, 'refresh_target_from_source')
            check(bpy.ops.ghost_tool.return_from_editor() == {'FINISHED'}, 'return_closes_owned_editor')

        with bpy.context.temp_override(window=source, area=area, region=region):
            check(len(bpy.context.window_manager.windows) == count, 'source_window_survives_return')
            check(tuple(o.name for o in bpy.context.selected_objects) == original_selection, 'selection_preserved_on_return')
            bpy.ops.ed.undo_push(message='Ghost Council before correction')
            before = source.scene.ghost_tool.motion_paths[0].thickness
            source.scene.ghost_tool.motion_paths[0].thickness = 4
            bpy.ops.ed.undo_push(message='Ghost Council correction')
            check(bpy.ops.ed.undo() == {'FINISHED'}, 'undo_executes')
            check(abs(source.scene.ghost_tool.motion_paths[0].thickness - before) < 1e-5, 'undo_restores_settings')
            check(bpy.ops.ed.redo() == {'FINISHED'}, 'redo_executes')
            check(source.scene.ghost_tool.motion_paths[0].thickness == 4, 'redo_restores_correction')
            scene = source.scene
            scene.ghost_tool_easing.active_preset = 'CUSTOM'
            scene.ghost_tool_easing.custom_left_y = .7
            uid = scene.ghost_tool.motion_paths[0].get('_ghost_editor_uid')
            with tempfile.TemporaryDirectory(prefix='ghost-council-') as directory:
                path = str(Path(directory) / 'roundtrip.blend')
                bpy.ops.wm.save_as_mainfile(filepath=path)
                bpy.ops.wm.open_mainfile(filepath=path)
                loaded = bpy.context.scene
                check(loaded.ghost_tool.motion_paths[0].thickness == 4, 'saved_path_settings')
                check(abs(loaded.ghost_tool_easing.custom_left_y - .7) < 1e-5, 'saved_custom_easing')
                check(loaded.ghost_tool.motion_paths[0].get('_ghost_editor_uid') == uid, 'saved_path_identity')
                check(not editor._targets, 'file_load_clears_editor_targets')
        ghost_tool.unregister()
        RESULT.write_text(json.dumps({'status':'PASS', 'checks':checks,
            'host':bpy.app.version_string, 'human_pointer_validation':'pending'}, indent=2), encoding='utf-8')
        print('GHOST_COUNCIL_WORKFLOW_RESULT: PASS', flush=True)
    except Exception:
        error = traceback.format_exc()
        RESULT.write_text(json.dumps({'status':'FAIL','checks':checks,'error':error}, indent=2), encoding='utf-8')
        print(error, flush=True)
    bpy.ops.wm.quit_blender()
    return None


bpy.app.timers.register(run, first_interval=1)
