"""Loaded only by the isolated native verification request bridge."""
import ast
import contextlib
import datetime
import importlib
import json
import os
from pathlib import Path
import time
import traceback

ROOT = root
PACKAGE = 'B4_anim_assist'
cat = importlib.import_module(PACKAGE+'.ui.timeline_catalog')
toolbar = importlib.import_module(PACKAGE+'.ui.timeline_strip')
overlay = importlib.import_module(PACKAGE+'.ui.timeline_overlay')
compat = importlib.import_module(PACKAGE+'.core.fcurve_compat')
checks = []
modal_records = []
button_records = []
recovery_records = []
slider_records = []
MODAL_ACTIONS = {'DRAG','NEIGHBORS','FRAME','EASE','AMPLIFY','SMOOTH','SCALE_DRAG','OFFSET_DRAG','OFFSET'}
source = Path(__file__).with_name('native_timeline_validation.py').read_text()
needed = {'write_results','check','object_snapshot','fixture','immediate_catalogue',
          'modal_live','modal_finish'}
for node in ast.parse(source).body:
    if isinstance(node, ast.FunctionDef) and node.name in needed:
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(__file__), 'exec'))


def timeline():
    return max((a for a in bpy.context.window.screen.areas if toolbar.is_timeline(a)), key=lambda a:a.height)


@contextlib.contextmanager
def timeline_context(index=0, region='WINDOW'):
    area = timeline()
    native = next(r for r in area.regions if r.type == region)
    with bpy.context.temp_override(area=area, region=native):
        yield area


def dispatch(action):
    with timeline_context():
        return sorted(bpy.ops.animassist.timeline_tool('INVOKE_DEFAULT', action=action))


def event(kind, value='PRESS', **kwargs):
    bpy.context.window.event_simulate(type=kind,value=value,**kwargs)


def prepare_geometry():
    area=timeline()
    event('MOUSEMOVE','NOTHING',x=area.x+100,y=area.y+area.height)


def expand_geometry():
    area=timeline()
    if area.height < 220:
        assert bpy.ops.screen.area_move.poll(), 'Native border resize context unavailable'
        bpy.ops.screen.area_move(x=area.x+100,y=area.y+area.height,delta=220-area.height)
    with timeline_context():
        prefs=bpy.context.preferences.addons[PACKAGE].preferences
        prefs.timeline_toolbar_row=True
    (ROOT/'inventory.json').write_text(json.dumps(dict(actions=cat.ACTIONS,
        defaults=cat.DEFAULT_QUICK_ACTIONS, host=state()),indent=2))


def run_immediate_checks():
    global immediate
    immediate=immediate_catalogue()
    assert immediate['count']==len(cat.ACTIONS)-len(MODAL_ACTIONS)
    assert not immediate['failed'], immediate['failed']
    (ROOT/'effect-summary.json').write_text(json.dumps(immediate,indent=2))


def click_action(action):
    with timeline_context():
        region=bpy.context.region
        items,_=overlay._items(bpy.context)
        item=next(i for i in items if i[:2]==('ACTION',action))
        x,y,w,h=item[3]
        position=dict(x=round(region.x+x+w/2),y=round(region.y+y+h/2))
        event('MOUSEMOVE','NOTHING',**position)
        event('LEFTMOUSE',**position)
        event('LEFTMOUSE','RELEASE',**position)


def prepare_button(action):
    global button_obj,button_before,button_action,bake_values,recovery_before,recovery_name
    with timeline_context():
        scene=bpy.context.scene
        if scene.anim_assist_p5.overlay_enabled: bpy.ops.animassist.p5_disable_overlay()
        button_obj,_=fixture(pose=action=='MIRROR_SELECTED')
        button_action=action
        scene.anim_assist_p6.ripple_delta=1
        scene.anim_assist_p6.range_mode='SELECTION'
        scene.anim_assist_p7.bake_range_mode='CUSTOM'
        scene.anim_assist_p7.bake_range_start=1
        scene.anim_assist_p7.bake_range_end=3
        scene.anim_assist_p7.bake_step=1
        if action=='MIRROR_SELECTED':
            # Unkeyed pose tool: animation evaluation otherwise replaces edits
            # between asynchronous input and assertions. Mirror Frame keys poses.
            button_obj.animation_data_clear()
            button_obj.pose.bones['Hand.L'].location=(1,2,0)
            button_obj.pose.bones['Hand.R'].location=(4,3,0)
        curves=(compat.get_fcurves(button_obj.animation_data.action,anim_data=button_obj.animation_data)
                if button_obj.animation_data and button_obj.animation_data.action else [])
        if action in {'RANGE','ENDS'}:
            for fc in curves:
                for k in fc.keyframe_points: k.select_control_point=False
        bake_values={fc.array_index: [fc.evaluate(f) for f in (1,2,3)]
                     for fc in curves if fc.data_path=='location'}
        button_before=object_snapshot(button_obj)
        recovery_before=button_before
        recovery_name=button_obj.name
        bpy.ops.ed.undo_push(message='Before toolbar '+action)


def assert_button():
    global recovery_after
    action=button_action
    after=object_snapshot(button_obj)
    recovery_after=after
    condition=False; details={}
    if action in {'B25','B50','B75'}:
        expected={'B25':1,'B50':2,'B75':3}[action]
        keys=[k for c in after if c['index']==0 for k in c['keys'] if k['co'][0]==10]
        condition=len(keys)==1 and abs(keys[0]['co'][1]-expected)<1e-5 and bpy.context.scene.frame_current==10
    elif action in {'NUDGE_LEFT','NUDGE_RIGHT','RIPPLE'}:
        frames={'NUDGE_LEFT':[0,19,39],'NUDGE_RIGHT':[2,21,41],'RIPPLE':[1,21,41]}[action]
        condition=all([k['co'][0] for k in c['keys']]==frames for c in after)
        for old,new in zip(button_before,after):
            for a,b in zip(old['keys'],new['keys']):
                delta=b['co'][0]-a['co'][0]
                condition=condition and abs(b['left'][0]-a['left'][0]-delta)<1e-5
    elif action=='RANGE': condition=all(k['selected'] for c in after for k in c['keys'])
    elif action=='ENDS': condition=all([k['selected'] for k in c['keys']]==[True,False,True] for c in after)
    elif action=='MIRROR_SELECTED':
        details={p.name:list(p.location) for p in button_obj.pose.bones}
        condition=details=={'Hand.L':[-4,3,0],'Hand.R':[-1,2,0]}
    elif action=='BAKE_STEP':
        curves=compat.get_fcurves(button_obj.animation_data.action,anim_data=button_obj.animation_data)
        errors=[abs(fc.evaluate(f)-bake_values[fc.array_index][i])
                for fc in curves if fc.data_path=='location' for i,f in enumerate((1,2,3))]
        condition=max(errors)<1e-4
        details={'sample_error':max(errors)}
    elif action=='TRAIL_SHOW':
        cache=importlib.import_module(PACKAGE+'.core.p5_path_cache')
        entry=cache.get_entry(cache.make_target_key(button_obj.name))
        assert entry and entry.samples
        old_frame=bpy.context.scene.frame_current
        errors=[]
        for sample in entry.samples[:8]:
            bpy.context.scene.frame_set(int(sample.frame),subframe=sample.frame-int(sample.frame))
            expected=button_obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation
            errors.append(max(abs(sample.world_pos[i]-expected[i]) for i in range(3)))
        bpy.context.scene.frame_set(old_frame)
        details={'world_sample_error':max(errors),'samples':len(entry.samples)}
        condition=max(errors)<1e-4
    record=dict(action=action,route='native-row',passed=condition,details=details)
    button_records.append(record)
    (ROOT/'bar-actions.json').write_text(json.dumps(button_records,indent=2))
    # Collect every bar result; the final coverage gate fails the whole run.


def begin_modal(action,ending):
    global modal_obj,modal_before,modal_case,xy,recovery_before,recovery_name
    with timeline_context():
        modal_obj,_target=fixture()
        for other in list(bpy.context.selected_objects):
            if other != modal_obj: other.select_set(False)
        scene=bpy.context.scene
        scene.anim_assist_p6.modal_snap=False
        scene.anim_assist_p3.factor=.5
        scene.anim_assist.reference_frame=1
        scene.anim_assist.mask.enabled=False
        if action in {'NEIGHBORS','FRAME','AMPLIFY','SMOOTH'}:
            for fc in compat.get_fcurves(modal_obj.animation_data.action,anim_data=modal_obj.animation_data):
                for i,k in enumerate(fc.keyframe_points): k.select_control_point=i==1
        if action=='OFFSET': scene.frame_set(20)
        modal_before=object_snapshot(modal_obj)
        recovery_before=modal_before
        recovery_name=modal_obj.name
        bpy.ops.ed.undo_push(message='Before modal '+action)
        area=timeline(); region=next(r for r in area.regions if r.type=='WINDOW')
        xy=dict(x=region.x+350,y=region.y+12)
        modal_case=dict(action=action,ending=ending,before=modal_before)
        if action in {'DRAG','SMOOTH'}:
            items,_=overlay._items(bpy.context)
            item=next(i for i in items if i[:2]==('ACTION',action))
            x,y,w,h=item[3]; xy=dict(x=round(region.x+x+w/2),y=round(region.y+y+h/2))
            event('MOUSEMOVE','NOTHING',**xy)
            event('LEFTMOUSE',**xy)
        else:
            event('MOUSEMOVE','NOTHING',**xy)
            dispatch(action)


def move_modal():
    if modal_case['action']=='OFFSET':
        fc=compat.get_fcurves(modal_obj.animation_data.action,anim_data=modal_obj.animation_data)[0]
        fc.keyframe_points[1].co.y+=2
        fc.update()
    else:
        event('MOUSEMOVE','NOTHING',x=xy['x']+60,y=xy['y'])


def assert_started():
    names=[op.bl_rna.identifier for op in bpy.context.window.modal_operators]
    modal_case['started']=names
    bpy.ops.screen.screenshot(filepath=str(ROOT/'modal-start.png'))
    required=toolbar._operator(modal_case['action']).get_rna_type().identifier
    assert required in names, (required,names,xy)


def assert_live():
    global modal_live_snapshot
    modal_live_snapshot=object_snapshot(modal_obj)
    modal_live()


def end_modal():
    if modal_case['ending']=='cancel': event('ESC')
    elif modal_case['action']=='DRAG': event('LEFTMOUSE','RELEASE',x=xy['x']+60,y=xy['y'])
    elif modal_case['action']=='OFFSET':
        bpy.context.scene.anim_assist.anim_offset_active=False
    else: event('RET')


def assert_ending():
    global recovery_after
    modal_finish()
    recovery_after=object_snapshot(modal_obj)


def assert_recovery(stage):
    obj=bpy.data.objects.get(recovery_name)
    actual=object_snapshot(obj) if obj else None
    expected=recovery_before if stage=='undo' else recovery_after
    passed=actual==expected
    record=dict(stage=stage,passed=passed,actual=actual,expected=expected)
    recovery_records.append(record)
    (ROOT/'recovery.json').write_text(json.dumps(recovery_records,indent=2))
    assert passed, (stage,'Animation snapshot differs')


def recover(stage):
    with timeline_context():
        operator=bpy.ops.ed.undo if stage=='undo' else bpy.ops.ed.redo
        assert operator.poll(), stage+' unavailable'
        assert operator()=={'FINISHED'}


def prepare_slider(action,mode,ending):
    global slider_obj,slider_before,slider_case,slider_xy,recovery_before,recovery_name
    with timeline_context():
        slider_obj,_=fixture()
        for other in list(bpy.context.selected_objects):
            if other!=slider_obj: other.select_set(False)
        bpy.context.scene.anim_assist.reference_frame=1
        bpy.context.scene.anim_assist_p3.factor=.5
        bpy.context.scene.anim_assist_p6.anchor_mode='FIRST'
        bpy.context.scene.anim_assist_p6.modal_snap=False
        if action in {'SMOOTH','NEIGHBORS','FRAME','AMPLIFY'}:
            for fc in compat.get_fcurves(slider_obj.animation_data.action,anim_data=slider_obj.animation_data):
                for i,k in enumerate(fc.keyframe_points): k.select_control_point=i==1
        slider_before=object_snapshot(slider_obj)
        recovery_before=slider_before; recovery_name=slider_obj.name
        slider_case=dict(action=action,mode=mode,ending=ending,before=slider_before)
        module=importlib.import_module(PACKAGE+'.operators.timeline_slider_ops')
        module._last_values.clear()
        region=bpy.context.region
        slider_xy=dict(x=region.x+210,y=region.y+12)
        bpy.ops.ed.undo_push(message='Before slider '+action)
        event('MOUSEMOVE','NOTHING',**slider_xy)


def begin_slider():
    with timeline_context():
        assert bpy.ops.animassist.timeline_slider('INVOKE_DEFAULT',True,
            action=slider_case['action'],mode=slider_case['mode'],track_x=150,track_y=2,track_width=120)=={'RUNNING_MODAL'}
    event('LEFTMOUSE',**slider_xy)


def move_slider():
    dx=24 if slider_case['mode']=='INLINE' else 60
    event('MOUSEMOVE','NOTHING',x=slider_xy['x']+dx,y=slider_xy['y'])


def check_slider_live():
    global slider_live
    module=importlib.import_module(PACKAGE+'.operators.timeline_slider_ops')
    op=module.feedback(bpy.context.window,timeline())
    assert op, 'Slider did not start'
    value=op.value; action=slider_case['action']; factor=value/100
    slider_live=object_snapshot(slider_obj)
    x=next(c for c in slider_live if c['index']==0)
    if action=='DRAG':
        keys=[k for k in x['keys'] if k['co'][0]==10]
        expected=4*factor; actual=keys[0]['co'][1]
    elif action in {'SCALE_DRAG','OFFSET_DRAG'}:
        expected=[1+(f-1)*factor for f in (1,20,40)] if action=='SCALE_DRAG' else [f+value for f in (1,20,40)]
        actual=[k['co'][0] for k in x['keys']]
    else:
        target={'SMOOTH':.5,'NEIGHBORS':19/39,'FRAME':0}.get(action)
        if action=='EASE':
            t=19/39; target=t*t*(3-2*t)
        expected=4*(1+factor) if action=='AMPLIFY' else 4+(target-4)*factor
        actual=x['keys'][1]['co'][1]
    error=max(abs(a-e) for a,e in zip(actual,expected)) if isinstance(actual,list) else abs(actual-expected)
    slider_case.update(value=value,actual=actual,expected=expected,error=error)
    assert error<1e-4 and slider_live!=slider_before, slider_case


def end_slider():
    if slider_case['ending']=='cancel': event('ESC')
    else: event('LEFTMOUSE','RELEASE',x=slider_xy['x']+60,y=slider_xy['y'])


def check_slider_end():
    global recovery_after
    module=importlib.import_module(PACKAGE+'.operators.timeline_slider_ops')
    after=object_snapshot(slider_obj)
    expected=slider_before if slider_case['ending']=='cancel' else slider_live
    passed=after==expected and not module.busy()
    slider_case.update(after=after,passed=passed)
    slider_records.append(slider_case.copy())
    (ROOT/'slider-actions.json').write_text(json.dumps(slider_records,indent=2))
    assert passed, slider_case
    recovery_after=after


def write_slider_coverage():
    assert len(slider_records)==32 and all(r['passed'] for r in slider_records)
    (ROOT/'slider-coverage.json').write_text(json.dumps(dict(cases=len(slider_records),
        recovery_assertions=len(recovery_records),passed=all(r['passed'] for r in recovery_records)),indent=2))


def ui_screenshot(name):
    with timeline_context():
        operator=bpy.ops.screen.screenshot if 'settings' in name or 'layout' in name else bpy.ops.screen.screenshot_area
        operator(filepath=str(ROOT/(name+'.png')))


def ui_defaults():
    global ui_original_config
    model=importlib.import_module(PACKAGE+'.ui.timeline_config')
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    with timeline_context():
        settings.write(bpy.context,model.recommended(cat.ACTIONS))
        items,band=overlay._items(bpy.context)
        assert [i[1] for i in items if i[0]=='MENU']==list(model.FAMILY_ORDER)
        assert {i[1] for i in items if i[0]=='SLIDER'}=={'DRAG','SMOOTH'}, items
        assert [i[0] for i in items[-3:]]==['SEARCH','MORE','SETTINGS']
        ui_original_config=bpy.context.preferences.addons[PACKAGE].preferences.timeline_layouts_json
    ui_screenshot('default-row')


def begin_slider_ui():
    global slider_xy
    with timeline_context():
        region=bpy.context.region
        items,_=overlay._items(bpy.context)
        kind='SLIDER' if slider_case['mode']=='INLINE' else 'POPOUT'
        item=next(i for i in items if i[:2]==(kind,slider_case['action']))
        x,y,w,h=item[3]
        if kind=='SLIDER':
            track,_,_=overlay._parts(item[3],item[2],bpy.context.preferences.system.ui_scale)
            x,y,w,h=track
        slider_xy=dict(x=round(region.x+x+w/2),y=round(region.y+y+h/2))
        event('MOUSEMOVE','NOTHING',**slider_xy)
        event('LEFTMOUSE',**slider_xy)


def ui_settings_open():
    global ui_before_config,ui_before_animation
    with timeline_context():
        ui_before_config=bpy.context.preferences.addons[PACKAGE].preferences.timeline_layouts_json
        ui_before_animation=object_snapshot(bpy.context.active_object)
        items,_=overlay._items(bpy.context)
        kind,key,label,(x,y,w,h)=next(i for i in items if i[0]=='SETTINGS')
        r=bpy.context.region; position=dict(x=round(r.x+x+w/2),y=round(r.y+y+h/2))
        event('MOUSEMOVE','NOTHING',**position); event('LEFTMOUSE',**position); event('LEFTMOUSE','RELEASE',**position)


def ui_settings_check():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    current=settings.editor(bpy.context)
    assert current and len(current.entries)==89, 'Settings dialog did not open'
    current.entries[0].mode='HIDDEN'
    ui_screenshot('toolbar-settings')


def ui_settings_cancelled():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    assert settings.editor(bpy.context) is None
    assert bpy.context.preferences.addons[PACKAGE].preferences.timeline_layouts_json==ui_before_config
    assert object_snapshot(bpy.context.active_object)==ui_before_animation


def ui_tool_open():
    with timeline_context():
        assert bpy.ops.animassist.tool_settings('INVOKE_DEFAULT',action='SMOOTH')=={'RUNNING_MODAL'}


def ui_tool_cancelled():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    assert not settings._tool_editors
    assert bpy.context.preferences.addons[PACKAGE].preferences.timeline_layouts_json==ui_before_config


def ui_finish():
    assert len(slider_records)==6 and all(r['passed'] for r in slider_records)
    (ROOT/'ui-coverage.json').write_text(json.dumps(dict(row_slider_cases=6,
        settings_cancelled_without_mutation=True,tool_settings_opened=True,
        recovery_assertions=len(recovery_records),passed=all(r['passed'] for r in recovery_records)),indent=2))


def write_coverage():
    bpy.ops.screen.screenshot(filepath=str(ROOT/'baseline-window.png'))
    (ROOT/'coverage.json').write_text(json.dumps(dict(
        immediate=immediate['count'],modal_cases=len(modal_records),
        button_cases=len(button_records),
        modal_ids=sorted({m['action'] for m in modal_records}),
        passed=not immediate['failed'] and len(modal_records)==18
               and all(r['passed'] for r in button_records)),indent=2))
    assert all(r['passed'] for r in button_records), [r for r in button_records if not r['passed']]
