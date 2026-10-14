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
extra_records = []
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
        if action=='PASTE_KEYS':
            bpy.ops.animassist.copy_selected_keys()
            bpy.context.preferences.addons[PACKAGE].preferences.timeline_paste_offset=100
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
    elif action=='COPY_KEYS':
        condition=importlib.import_module(PACKAGE+'.core.key_utils').clipboard_size()==9
    elif action=='PASTE_KEYS':
        condition=all([k['co'][0] for k in c['keys']]==[1,20,40,101,120,140] for c in after)
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
        operator=bpy.ops.screen.screenshot if 'settings' in name or 'layout' in name or name.startswith('menu-') else bpy.ops.screen.screenshot_area
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


def layouts_prepare():
    global layout_animation,layout_obj_name,layout_scene_values
    with timeline_context():
        obj,_=fixture(); layout_obj_name=obj.name
        layout_animation=object_snapshot(obj)
        layout_scene_values=(bpy.context.scene.frame_current,bpy.context.scene.anim_assist.reference_frame,
                             bpy.context.scene.anim_assist_p3.factor)


def layout_save_open(name):
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    if name=='Polish':
        data=settings.record(bpy.context)
        data['active']['tools']['DRAG']['mode']='POPOUT'
        data['active']['tools']['SMOOTH'].update(overshoot_enabled=True,range_min=-100,range_max=200,presets=[-100,0,100])
        settings.write(bpy.context,data)
    with timeline_context():
        assert bpy.ops.animassist.layout_action('INVOKE_DEFAULT',operation='SAVE',layout_name=name)=={'RUNNING_MODAL'}


def layout_saved(name):
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    data=settings.record(bpy.context)
    assert data['active']['name']==name
    assert any(item['name']==name for item in data['saved'])
    assert object_snapshot(bpy.data.objects[layout_obj_name])==layout_animation
    assert (bpy.context.scene.frame_current,bpy.context.scene.anim_assist.reference_frame,
            bpy.context.scene.anim_assist_p3.factor)==layout_scene_values


def layout_manage():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    data=settings.record(bpy.context)
    ids={item['name']:item['id'] for item in data['saved']}
    with timeline_context():
        assert bpy.ops.animassist.layout_action('EXEC_DEFAULT',operation='LOAD',target=ids['Blocking'])=={'FINISHED'}
        assert settings.record(bpy.context)['active']['tools']['DRAG']['mode']=='INLINE'
        assert bpy.ops.animassist.layout_action('EXEC_DEFAULT',operation='RENAME',target=ids['Blocking'],layout_name='ブロック')=={'FINISHED'}
        assert bpy.ops.animassist.layout_action('EXEC_DEFAULT',operation='LOAD',target=ids['Polish'])=={'FINISHED'}
        assert bpy.ops.animassist.layout_action('EXEC_DEFAULT',operation='DELETE',target=ids['Blocking'])=={'FINISHED'}
        assert len(settings.record(bpy.context)['saved'])==1
        assert bpy.ops.animassist.restore_toolbar()=={'FINISHED'}
        assert len(settings.record(bpy.context)['saved'])==1
        assert bpy.ops.animassist.layout_action('EXEC_DEFAULT',operation='LOAD',target=ids['Polish'])=={'FINISHED'}
    assert object_snapshot(bpy.data.objects[layout_obj_name])==layout_animation


def layout_transfer_and_save():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    prefs=bpy.context.preferences.addons[PACKAGE].preferences
    expected=prefs.timeline_layouts_json
    with timeline_context():
        assert bpy.ops.anim_assist.export_settings(filepath=str(ROOT/'settings.json'))=={'FINISHED'}
        exported=json.loads((ROOT/'settings.json').read_text())
        assert exported['timeline_layouts_json']==expected
        bad=dict(exported); bad['timeline_layouts_json']='{"schema_version":2}'
        bad['performance_mode']=not prefs.performance_mode
        (ROOT/'invalid-settings.json').write_text(json.dumps(bad))
        old_performance=prefs.performance_mode
        try: bpy.ops.anim_assist.import_settings(filepath=str(ROOT/'invalid-settings.json'))
        except RuntimeError: pass  # ERROR reports propagate through bpy.ops.
        assert prefs.timeline_layouts_json==expected and prefs.performance_mode==old_performance
        assert bpy.ops.animassist.restore_toolbar()=={'FINISHED'}
        assert bpy.ops.anim_assist.import_settings(filepath=str(ROOT/'settings.json'))=={'FINISHED'}
        assert prefs.timeline_layouts_json==expected
        bpy.ops.wm.save_userpref()
    (ROOT/'saved-layout.json').write_text(expected)
    assert object_snapshot(bpy.data.objects[layout_obj_name])==layout_animation


def layout_restart_check():
    from_module=importlib.import_module(PACKAGE+'.prefs')
    data=from_module.timeline_record(from_module.get_prefs(bpy.context))
    expected=json.loads((ROOT/'saved-layout.json').read_text())
    assert data==expected
    assert data['active']['name']=='Polish' and len(data['saved'])==1
    assert data['active']['tools']['DRAG']['mode']=='POPOUT'
    (ROOT/'layout-coverage.json').write_text(json.dumps(dict(named_layouts_saved=True,
        rename_delete_reset=True,export_import=True,rejected_future_schema=True,
        animation_unchanged=True,normal_restart=True,automatically_enabled=True,passed=True),indent=2))


def full_legacy_layout():
    model=importlib.import_module(PACKAGE+'.ui.timeline_config')
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    data=model.recommended(cat.ACTIONS)
    for action,tool in data['active']['tools'].items():
        tool['mode']='BUTTON' if action in cat.DEFAULT_QUICK_ACTIONS else 'HIDDEN'
    settings.write(bpy.context,data)


def select_slider_mode():
    model=importlib.import_module(PACKAGE+'.ui.timeline_config')
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    data=model.recommended(cat.ACTIONS)
    for tool in data['active']['tools'].values(): tool['mode']='HIDDEN'
    data['active']['tools'][slider_case['action']]['mode']=slider_case['mode']
    settings.write(bpy.context,data)


def settings_change():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    current=settings.editor(bpy.context)
    assert current and len(current.entries)==89
    for entry in current.entries:
        if entry.action=='SMOOTH': entry.mode='POPOUT'; entry.width=160
    ui_screenshot('toolbar-settings-final')


def settings_accepted():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    tool=settings.record(bpy.context)['active']['tools']['SMOOTH']
    assert tool['mode']=='POPOUT' and tool['width']==160
    assert object_snapshot(bpy.context.active_object)==ui_before_animation
    extra_records.append(dict(check='Toolbar settings acceptance',passed=True,actual=tool))


def tool_change():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    op=settings._tool_editors[bpy.context.window.as_pointer()]
    op.mode='INLINE'; op.overshoot_enabled=True; op.range_min=-100; op.range_max=200
    op.precision=2; op.presets_text='-100, 0, 100'


def tool_accepted():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    tool=settings.record(bpy.context)['active']['tools']['SMOOTH']
    assert tool['overshoot_enabled'] and tool['range_min']==-100 and tool['range_max']==200
    assert tool['presets']==[-100,0,100] and tool['precision']==2 and tool['mode']=='INLINE'
    assert object_snapshot(bpy.context.active_object)==ui_before_animation
    extra_records.append(dict(check='Per-tool settings acceptance',passed=True,actual=tool))


def numeric_prepare(value):
    global numeric_value,numeric_obj,recovery_before,recovery_name
    with timeline_context():
        numeric_obj,_=fixture()
        for other in list(bpy.context.selected_objects):
            if other!=numeric_obj: other.select_set(False)
        for fc in compat.get_fcurves(numeric_obj.animation_data.action,anim_data=numeric_obj.animation_data):
            for i,k in enumerate(fc.keyframe_points): k.select_control_point=i==1
        recovery_before=object_snapshot(numeric_obj); recovery_name=numeric_obj.name
        numeric_value=value
        bpy.ops.ed.undo_push(message='Before numeric adjustment')
        assert bpy.ops.animassist.slider_value('INVOKE_DEFAULT',True,action='SMOOTH',value=value)=={'RUNNING_MODAL'}


def numeric_check():
    global recovery_after
    recovery_after=object_snapshot(numeric_obj)
    curve=next(c for c in recovery_after if c['index']==0)
    actual=curve['keys'][1]['co'][1]; expected=4+(.5-4)*numeric_value/100
    assert abs(actual-expected)<1e-5,(actual,expected)
    extra_records.append(dict(check='Numeric/extended Smooth '+str(numeric_value),passed=True,actual=actual,expected=expected))


def misuse_checks():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    prefs=bpy.context.preferences.addons[PACKAGE].preferences
    with timeline_context():
        obj,_=fixture(); before=object_snapshot(obj)
        prefs.enable_retime=False
        assert toolbar._unavailable(bpy.context,timeline(),'SCALE_DRAG')
        prefs.enable_retime=True
        for fc in compat.get_fcurves(obj.animation_data.action,anim_data=obj.animation_data):
            fc.lock=True
        assert toolbar._unavailable(bpy.context,timeline(),'SCALE_DRAG')
        for fc in compat.get_fcurves(obj.animation_data.action,anim_data=obj.animation_data):
            fc.lock=False
            for k in fc.keyframe_points: k.select_control_point=False
        assert toolbar._unavailable(bpy.context,timeline(),'SMOOTH')
        for fc in compat.get_fcurves(obj.animation_data.action,anim_data=obj.animation_data):
            for k in fc.keyframe_points: k.select_control_point=True
        assert object_snapshot(obj)==before
        old=bpy.context.view_layer.objects.active; bpy.context.view_layer.objects.active=None
        assert toolbar._unavailable(bpy.context,timeline(),'DRAG')
        assert toolbar._unavailable(bpy.context,timeline(),'TRAIL_SHOW')
        bpy.context.view_layer.objects.active=old
    extra_records.append(dict(check='Disabled module/locked/no keys/no object prerequisites',passed=True))


def ui_click(kind,key=''):
    with timeline_context():
        item=next(i for i in overlay._items(bpy.context)[0] if i[:2]==(kind,key))
        x,y,w,h=item[3]; r=bpy.context.region
        position=dict(x=round(r.x+x+w/2),y=round(r.y+y+h/2))
        event('MOUSEMOVE','NOTHING',**position); event('LEFTMOUSE',**position); event('LEFTMOUSE','RELEASE',**position)


def scrub_prepare():
    global scrub_before
    with timeline_context():
        bpy.context.scene.frame_set(10); scrub_before=10
        r=bpy.context.region
        point=dict(x=r.x+600,y=r.y+r.height-10)
        event('MOUSEMOVE','NOTHING',**point); event('LEFTMOUSE',**point); event('LEFTMOUSE','RELEASE',**point)


def scrub_check():
    assert bpy.context.scene.frame_current!=scrub_before
    extra_records.append(dict(check='Native scrub outside band',passed=True,actual=bpy.context.scene.frame_current))


def hide_check():
    prefs=bpy.context.preferences.addons[PACKAGE].preferences
    prefs.timeline_toolbar_row=False
    assert not toolbar._enabled()
    prefs.timeline_toolbar_row=True
    assert toolbar._enabled()
    extra_records.append(dict(check='Show/hide row',passed=True))


def lifecycle_disable():
    global lifecycle_area_count
    import addon_utils
    lifecycle_area_count=sum(len(w.screen.areas) for w in bpy.context.window_manager.windows)
    addon_utils.disable(PACKAGE,default_set=False)
    assert overlay._handle is None and not overlay._keymaps
    bindings=[i for km in bpy.context.window_manager.keyconfigs.addon.keymaps for i in km.keymap_items
              if i.idname in {'animassist.timeline_overlay_events','animassist.clear_timeline_hover'}]
    assert not bindings


def lifecycle_enable():
    import addon_utils
    addon_utils.enable(PACKAGE,default_set=True,persistent=True)
    assert overlay._handle is not None and len(overlay._keymaps)==13
    bindings=[i for km in bpy.context.window_manager.keyconfigs.addon.keymaps for i in km.keymap_items
              if i.idname in {'animassist.timeline_overlay_events','animassist.clear_timeline_hover'}]
    assert len(bindings)==13
    assert sum(len(w.screen.areas) for w in bpy.context.window_manager.windows)==lifecycle_area_count
    extra_records.append(dict(check='Disable/re-enable native bindings and no helper editor',passed=True))


def migration_checks():
    prefs=bpy.context.preferences.addons[PACKAGE].preferences
    from_module=importlib.import_module(PACKAGE+'.prefs')
    saved=prefs.timeline_layouts_json
    for a in cat.ACTIONS: setattr(prefs,cat.quick_property_name(a),a in {'B25','SMOOTH'})
    prefs.timeline_layouts_json=''
    migrated=from_module.timeline_record(prefs,initialize=True)
    assert {a for a,t in migrated['active']['tools'].items() if t['mode']!='HIDDEN'}=={'B25','SMOOTH'}
    assert migrated['active']['tools']['SMOOTH']['mode']=='POPOUT'
    prefs.timeline_layouts_json=''
    for a in cat.ACTIONS: setattr(prefs,cat.quick_property_name(a),False)
    empty=from_module.timeline_record(prefs,initialize=True)
    assert all(t['mode']=='HIDDEN' for t in empty['active']['tools'].values())
    prefs.timeline_layouts_json=saved
    extra_records.append(dict(check='Explicit legacy custom and empty migration',passed=True))


def write_full_coverage():
    assert len(slider_records)==32 and all(r['passed'] for r in slider_records)
    assert all(r['passed'] for r in button_records+recovery_records+extra_records)
    ui_screenshot('final-row')
    (ROOT/'extras.json').write_text(json.dumps(extra_records,indent=2))
    (ROOT/'full-coverage.json').write_text(json.dumps(dict(immediate=immediate['count'],
        original_interactive_cases=len(modal_records),native_bar_buttons=len(button_records),
        native_row_scalar_cases=len(slider_records),recovery_assertions=len(recovery_records),
        extras=len(extra_records),passed=True),indent=2))


def write_coverage():
    bpy.ops.screen.screenshot(filepath=str(ROOT/'baseline-window.png'))
    (ROOT/'coverage.json').write_text(json.dumps(dict(
        immediate=immediate['count'],modal_cases=len(modal_records),
        button_cases=len(button_records),
        modal_ids=sorted({m['action'] for m in modal_records}),
        passed=not immediate['failed'] and len(modal_records)==18
               and all(r['passed'] for r in button_records)),indent=2))
    assert all(r['passed'] for r in button_records), [r for r in button_records if not r['passed']]
