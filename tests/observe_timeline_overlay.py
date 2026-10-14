"""Isolated real-GUI observation harness; never imported by the add-on."""
import addon_utils
import bpy
import json
import os
from pathlib import Path
import traceback

root = Path(os.environ['AA_OVERLAY_EVIDENCE'])
root.mkdir(parents=True, exist_ok=True)
config = Path(os.environ['BLENDER_USER_CONFIG']).resolve()
assert config.is_dir() and Path(bpy.utils.user_resource('CONFIG')).resolve() == config
scripts = Path(os.environ['BLENDER_USER_SCRIPTS']).resolve()
assert scripts.is_dir()
addon_utils.enable('B4_anim_assist', default_set=True, persistent=True)
bpy.context.preferences.use_preferences_save = False


def state():
    windows = []
    for window in bpy.context.window_manager.windows:
        areas = []
        for area in window.screen.areas:
            item = dict(type=area.type, mode=getattr(area.spaces.active, 'mode', ''),
                        x=area.x, y=area.y, width=area.width, height=area.height,
                        regions=[dict(type=r.type, x=r.x, y=r.y, width=r.width, height=r.height)
                                 for r in area.regions])
            areas.append(item)
        windows.append(dict(width=window.width, height=window.height, areas=areas))
    return dict(binary=bpy.app.binary_path, build_hash=bpy.app.build_hash.decode(),
                windows=windows, frame=bpy.context.scene.frame_current)


def poll():
    request = root / 'request.json'
    if request.exists():
        data = json.loads(request.read_text())
        request.unlink()
        try:
            exec(data['code'], globals())
            result = dict(id=data['id'], ok=True, state=state())
        except Exception:
            result = dict(id=data['id'], ok=False, error=traceback.format_exc())
        (root / 'response.json').write_text(json.dumps(result, indent=2))
    (root / 'state.json').write_text(json.dumps(state(), indent=2))
    return .25


bpy.app.timers.register(poll, first_interval=2, persistent=True)
