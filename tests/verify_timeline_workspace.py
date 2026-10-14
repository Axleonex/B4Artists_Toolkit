"""Native animator workflow without artificially expanding the initial Timeline."""
import argparse
import hashlib
import json
from pathlib import Path
from verify_timeline_toolbar import Host, install, owned_profile


def run(args):
    profile=owned_profile(args.profile); package=Path(args.package).resolve()
    files=install(package,profile);host=Host(args,profile);records=[]
    def step(name,code,delay=.2):
        result=host.request(code,delay)
        records.append(dict(check=name,passed=True,state=result['state']))
        (host.root/'workflow.json').write_text(json.dumps(dict(sha256=hashlib.sha256(package.read_bytes()).hexdigest(),files=files,checks=records,passed=False),indent=2))
    try:
        for name in ('check_timeline_toolbar_tools.py','check_timeline_stress.py','check_timeline_workspace.py'):
            source=Path(__file__).with_name(name).resolve()
            step('Load '+name,f"exec(compile(open({str(source)!r},encoding='utf-8').read(),{str(source)!r},'exec'),globals())")
        step('Visible before welcome dismissal','workspace_visible("first-start")')
        step('Dismiss welcome',"event('ESC')")
        step('Default two-slider row at initial height','workspace_defaults()')
        step('Breakdown direct drag prepare','prepare_slider("DRAG","INLINE","commit");begin_slider_ui()')
        step('Breakdown movement','move_slider()')
        step('Breakdown numerical preview','check_slider_live()')
        step('Release Breakdown','end_slider()')
        step('Breakdown committed snapshot','check_slider_end()')
        step('One native undo',"recover('undo');assert_recovery('undo')")
        step('One native redo',"recover('redo');assert_recovery('redo')")
        step('Right-click Smooth settings','workspace_right_settings()')
        step('Set Smooth Popout in actual dialog','workspace_popout()')
        step('Accept tool settings',"event('RET')")
        step('Smooth Popout persisted','workspace_popout_check()')
        step('Popout drag prepare','prepare_slider("SMOOTH","POPOUT","cancel");begin_slider_ui()')
        step('Popout movement','move_slider()')
        step('Popout numerical preview','check_slider_live()')
        step('Cancel popout',"event('ESC')")
        step('Popout exact restoration','check_slider_end()')
        step('Open Settings from row','ui_settings_open()')
        step('Reorder/select through Settings','workspace_settings_change()')
        step('Accept Settings',"event('RET')")
        step('Settings applied with no animation edit','workspace_settings_check()')
        step('Prepare layout snapshots','layouts_prepare()')
        for name in ('Blocking','Polish'):
            step('Name '+name,f'layout_save_open({name!r})')
            step('Accept '+name,"event('RET')")
            step('Saved '+name,f'layout_saved({name!r})')
        step('Open unsaved-change guard','workspace_dirty_load()')
        step('Guard preserves edits on Cancel','workspace_guard_check();event("ESC")')
        step('Explicit discard and switch layouts','workspace_layout_switch()')
        step('Timing Scale prepare','prepare_slider("SCALE_DRAG","POPOUT","cancel");begin_slider_ui()')
        step('Timing Scale movement','move_slider()')
        step('Timing Scale preview','check_slider_live()')
        step('Cancel Timing Scale with right click',"event('RIGHTMOUSE');event('RIGHTMOUSE','RELEASE')")
        step('Timing Scale exact restoration','check_slider_end()')
        step('Native scrub','scrub_prepare()')
        step('Native scrub effect','scrub_check()')
        step('Native play','stress_play()',.5)
        step('Native play effect','stress_play_check()')
        step('Point at native resize border','prepare_geometry()')
        step('Manual shrink to 85px','workspace_resize(85)',2.2)
        step('Small height retained','stress_small()')
        step('Expand and save workspace','workspace_resize(160)',.3)
        step('Save preferences and scene for normal restart','workspace_save()')
        host.close();args.resume=True;host=Host(args,profile)
        source=Path(__file__).with_name('check_timeline_workspace.py').resolve()
        step('Load restart helper',f"exec(compile(open({str(source)!r},encoding='utf-8').read(),{str(source)!r},'exec'),globals())")
        step('Restart restores active layout and library','workspace_restart()')
        step('Saved workspace row visible after load','workspace_visible("reloaded-workspace")')
        (host.root/'workflow.json').write_text(json.dumps(dict(sha256=hashlib.sha256(package.read_bytes()).hexdigest(),files=files,checks=records,passed=True),indent=2))
        print(json.dumps(dict(passed=True,workflow_steps=len(records),sha256=hashlib.sha256(package.read_bytes()).hexdigest())))
    finally:host.close()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('package','host','evidence','profile'):p.add_argument('--'+key,required=True)
    p.add_argument('--timeout',type=float,default=60)
    args=p.parse_args();args.attach=None;args.resume=False;run(args)
