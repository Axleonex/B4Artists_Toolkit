"""Additional exact-package native workspace/lifecycle checks in an owned profile."""
import argparse
import hashlib
import json
from pathlib import Path
from verify_timeline_toolbar import Host, install, owned_profile


def run(args):
    profile=owned_profile(args.profile)
    package=Path(args.package).resolve()
    files=install(package,profile)
    host=Host(args,profile)
    records=[]
    def request(name,code,delay=.2):
        result=host.request(code,delay)
        records.append(dict(check=name,passed=True,state=result['state']))
        (host.root/'stress.json').write_text(json.dumps(dict(
            sha256=hashlib.sha256(package.read_bytes()).hexdigest(),files=files,
            checks=records,passed=False),indent=2))
    try:
        source=Path(__file__).with_name('check_timeline_toolbar_tools.py').resolve()
        request('Load helpers',f"exec(compile(open({str(source)!r},encoding='utf-8').read(),{str(source)!r},'exec'),globals())")
        request('Dismiss welcome',"event('ESC')")
        request('Prepare geometry','prepare_geometry()')
        request('Expand geometry','expand_geometry()')
        stress=Path(__file__).with_name('check_timeline_stress.py').resolve()
        request('Load stress helpers',f"exec(compile(open({str(stress)!r},encoding='utf-8').read(),{str(stress)!r},'exec'),globals())")
        steps=EDGE_STEPS if args.edges else STEPS
        if args.tail:steps=steps[37:]
        for name,code,delay in steps:
            request(name,code,delay)
        (host.root/'stress.json').write_text(json.dumps(dict(
            sha256=hashlib.sha256(package.read_bytes()).hexdigest(),files=files,
            checks=records,passed=True),indent=2))
        print(json.dumps(dict(passed=True,steps=len(records))))
    finally:
        host.close()


STEPS=[
    ('Fresh defaults','ui_defaults()',.2),
    ('Shrink Timeline','stress_resize(85)',2.2),
    ('Retains manual small height','stress_small()',.2),
    ('Expand Timeline','stress_resize(220)',.3),
    ('Top/bottom header prepare','stress_header()',.3),
    ('Header geometry','stress_header_check()',.2),
    ('Restore header','stress_header()',.3),
    ('Maximize','stress_maximize()',.3),
    ('Maximized geometry','stress_geometry("maximized")',.2),
    ('Restore maximize','stress_maximize()',.3),
    ('Scale 1.5','stress_scale(1.5)',.5),
    ('Scale 1.5 geometry','stress_geometry("scale-1.5")',.2),
    ('Scale 2','stress_scale(2)',.5),
    ('Scale 2 geometry','stress_geometry("scale-2")',.2),
    ('Restore scale','stress_scale(1)',.5),
    ('Native pan prepare','stress_pan()',.3),
    ('Native pan check','stress_pan_check()',.2),
    ('Native zoom','stress_zoom()',.3),
    ('Native zoom check','stress_zoom_check()',.2),
    ('Playback start','stress_play()',.5),
    ('Playback changed frame','stress_play_check()',.2),
    ('Right-click settings','stress_right_settings()',.3),
    ('Right-click settings check','stress_right_settings_check()',.2),
    ('Cancel settings',"event('ESC')",.2),
    ('New window','stress_window()',1.2),
    ('Multiple-window rows','stress_window_check()',.3),
    ('Close extra window','stress_window_close()',.3),
    ('Precision prepare','prepare_slider("SMOOTH","POPOUT","cancel"); select_slider_mode(); begin_slider_ui()',.3),
    ('Precision gesture','stress_precision()',.3),
    ('Precision assertion','stress_precision_check()',.2),
    ('Cancel precision',"event('RIGHTMOUSE')",.2),
    ('Precision cancellation','check_slider_end()',.2),
    ('Snap prepare','prepare_slider("SMOOTH","POPOUT","cancel"); select_slider_mode(); begin_slider_ui()',.3),
    ('Snap gesture','stress_snap()',.3),
    ('Snap assertion','stress_snap_check()',.2),
    ('Cancel snap',"event('ESC')",.2),
    ('Snap cancellation','check_slider_end()',.2),
    ('Disable during preview prepare','prepare_slider("SMOOTH","INLINE","cancel"); select_slider_mode(); begin_slider_ui()',.3),
    ('Preview changes','move_slider()',.3),
    ('Disable during preview','stress_active_disable()',.5),
    ('Disabled preview restores','stress_active_disabled()',.2),
    ('Re-enable','lifecycle_enable()',.4),
    ('Area-loss preview prepare','prepare_slider("SMOOTH","INLINE","cancel"); select_slider_mode(); begin_slider_ui()',.3),
    ('Area-loss preview changes','move_slider()',.3),
    ('Workspace switch cancels preview','stress_lost_area()',.5),
    ('Lost-area preview restores','stress_lost_area_check()',.3),
    ('Scene save','stress_save()',.3),
    ('Scene load','stress_load()',1.3),
    ('Scene load preserves animation/layout','stress_load_check()',.2),
]

EDGE_STEPS=[
    ('Custom preset preparation','stress_preset_prepare()',.3),
    ('Custom preset pointer',"ui_click('PRESET','SMOOTH:100')",.3),
    ('Custom preset effect','stress_preset_check()',.2),
    ('Preset undo',"recover('undo');assert_recovery('undo')",.2),
    ('Preset redo',"recover('redo');assert_recovery('redo')",.2),
    ('Reset preparation','stress_preset_prepare()',.3),
    ('Reset pointer','stress_reset()',.3),
    ('Reset neutral effect','stress_reset_check()',.2),
    ('Neutral and locked/hidden scope','stress_neutral_scope()',.2),
    ('Fresh defaults after edges','ui_defaults()',.2),
    ('Native narrow split','stress_narrow()',1.2),
    ('Narrow split bounds and unchanged modes','stress_narrow_check()',.2),
]


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('package','host','evidence','profile'):p.add_argument('--'+n,required=True)
    p.add_argument('--timeout',type=float,default=60)
    p.add_argument('--edges',action='store_true')
    p.add_argument('--tail',action='store_true',help='Resume only remaining lifecycle steps after a preserved diagnostic')
    args=p.parse_args();args.attach=None;args.resume=False
    run(args)
