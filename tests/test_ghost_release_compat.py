"""Create a .blend with the published 4.0.0 ZIP, then reopen it with current source."""
import importlib
import sys
import tempfile
import zipfile
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True

with tempfile.TemporaryDirectory(prefix='ghost-4-compat-') as directory:
    temp = Path(directory)
    with zipfile.ZipFile(ROOT / 'releases' / 'b4_ghost_tool_v4.0.0.zip') as archive:
        archive.extractall(temp)
    sys.path.insert(0, str(temp))
    import ghost_tool
    assert ghost_tool.bl_info['version'] == (4, 0, 0)
    ghost_tool.register()
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.object
    obj.name = 'LegacyGhostObject'
    obj.keyframe_insert('location', frame=1)
    obj.location.x = 4
    obj.keyframe_insert('location', frame=20)
    scene = bpy.context.scene
    entry = scene.ghost_tool.motion_paths.add()
    entry.object_name = obj.name
    entry.thickness = 5
    entry.use_own_range = True
    entry.own_range_mode = 'CUSTOM'
    entry.own_start, entry.own_end = 3, 17
    scene.ghost_tool.motion_paths_index = 0
    scene.ghost_tool_easing.active_preset = 'CUSTOM'
    scene.ghost_tool_easing.custom_left_y = .7
    path = str(temp / 'published-4.0.0.blend')
    bpy.ops.wm.save_as_mainfile(filepath=path)
    ghost_tool.unregister()
    for name in tuple(sys.modules):
        if name == 'ghost_tool' or name.startswith('ghost_tool.'):
            del sys.modules[name]
    sys.path.remove(str(temp))
    sys.path.insert(0, str(ROOT))
    importlib.invalidate_caches()
    ghost_tool = importlib.import_module('ghost_tool')
    ghost_tool.register()
    bpy.ops.wm.open_mainfile(filepath=path)
    scene = bpy.context.scene
    entry = scene.ghost_tool.motion_paths[0]
    assert (entry.object_name, entry.thickness, entry.own_start, entry.own_end) == ('LegacyGhostObject', 5, 3, 17)
    assert entry.use_own_range and entry.own_range_mode == 'CUSTOM'
    assert abs(scene.ghost_tool_easing.custom_left_y - .7) < 1e-5
    assert scene.ghost_tool_easing.active_preset == 'CUSTOM'
    from ghost_tool.settings_editor import capture_target, resolve_target
    target = capture_target(bpy.context)
    assert target.path_uid and resolve_target(target, scene)[1] == ''
    ghost_tool.unregister()
print('GHOST_RELEASE_COMPAT_RESULT: PASS', flush=True)
