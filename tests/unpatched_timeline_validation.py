"""Run representative access/effect checks in an actual unpatched GUI host."""
import ast
import bpy
import addon_utils
import contextlib
import datetime
import importlib
import json
import os
from pathlib import Path
import traceback

ROOT=Path(os.environ['AA_VALIDATION_ROOT'])
PACKAGE='B4_anim_assist'
addon_utils.enable(PACKAGE,default_set=True,persistent=True)
bpy.context.preferences.use_preferences_save=False
cat=importlib.import_module(PACKAGE+'.ui.timeline_catalog')
toolbar=importlib.import_module(PACKAGE+'.ui.timeline_strip')
compat=importlib.import_module(PACKAGE+'.core.fcurve_compat')
checks=[]
MODAL_ACTIONS={'DRAG','NEIGHBORS','FRAME','EASE','AMPLIFY','SMOOTH','SCALE_DRAG','OFFSET_DRAG','OFFSET'}

# Share the fixture and exact action-specific assertions; only the owning
# header context differs between native and unpatched hosts.
source=Path(__file__).with_name('native_timeline_validation.py').read_text()
selected={'write_results','check','object_snapshot','fixture','immediate_catalogue'}
tree=ast.parse(source)
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in selected:
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(__file__),'exec'))

@contextlib.contextmanager
def timeline_context(index=0,region='WINDOW'):
    owning=[(w,a) for w in bpy.context.window_manager.windows for a in w.screen.areas
            if toolbar.is_timeline(a)]
    w,a=owning[index]
    r=next(r for r in a.regions if r.type==region)
    with bpy.context.temp_override(window=w,area=a,region=r): yield a

def dispatch(action):
    with timeline_context(region='HEADER'):
        return sorted(bpy.ops.animassist.timeline_tool('INVOKE_DEFAULT',action=action))

def validate():
    check('Actual unpatched feature detection',not toolbar.native_available())
    before=sum(len(w.screen.areas) for w in bpy.context.window_manager.windows)
    results=immediate_catalogue()
    check('All 80 immediate fallback actions have effects',not results['failed'],results)
    check('Fallback creates no separate editor',sum(len(w.screen.areas) for w in bpy.context.window_manager.windows)==before)
    with timeline_context() as area:
        regions=[dict(type=r.type,width=r.width,height=r.height) for r in area.regions]
    (ROOT/'fallback-summary.json').write_text(json.dumps(dict(binary=bpy.app.binary_path,
        build_hash=bpy.app.build_hash.decode(),version=list(bpy.app.version),
        native_available=toolbar.native_available(),results=results,regions=regions),indent=2))
    return None

bpy.app.timers.register(validate,first_interval=4)
