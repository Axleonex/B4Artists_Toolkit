"""Native stress helper; loaded by the isolated request bridge only."""
from math import isclose


def stress_resize(height):
    a=timeline()
    assert bpy.ops.screen.area_move.poll()
    bpy.ops.screen.area_move(x=a.x+100,y=a.y+a.height,delta=height-a.height)


def stress_small():
    assert abs(timeline().height-85)<=2, timeline().height
    stress_geometry('narrow-height')


def stress_geometry(name):
    with timeline_context():
        items,band=overlay._items(bpy.context);r=bpy.context.region
        assert items and {i[0] for i in items}>={'MORE','SETTINGS','SEARCH'},items
        for item in items:
            x,y,w,h=item[3]
            assert 0<=x<x+w<=r.width+1 and 0<=y<y+h<=r.height+1,item
        for first,second in zip(items,items[1:]):
            assert first[3][0]+first[3][2]<=second[3][0],(first,second)
    ui_screenshot(name)


def stress_header():
    with timeline_context(region='HEADER'):
        bpy.ops.screen.region_flip()


def stress_header_check():
    stress_geometry('flipped-header')


def stress_maximize():
    with timeline_context():bpy.ops.screen.screen_full_area(use_hide_panels=False)


def stress_scale(value):
    # Native preference determines the read-only effective system scale.
    bpy.context.preferences.view.ui_scale=value


def stress_pan():
    global stress_rect,stress_xy
    with timeline_context():
        r=bpy.context.region
        stress_rect=tuple(r.view2d.region_to_view(0,0))
        stress_xy=dict(x=r.x+r.width//2,y=r.y+r.height//2)
        event('MOUSEMOVE','NOTHING',**stress_xy)
        event('MIDDLEMOUSE',**stress_xy)
        event('MOUSEMOVE','NOTHING',x=stress_xy['x']+80,y=stress_xy['y'])
        event('MIDDLEMOUSE','RELEASE',x=stress_xy['x']+80,y=stress_xy['y'])


def stress_pan_check():
    with timeline_context():
        assert tuple(bpy.context.region.view2d.region_to_view(0,0))!=stress_rect


def stress_zoom():
    global stress_span
    with timeline_context():
        r=bpy.context.region
        stress_span=r.view2d.region_to_view(r.width,0)[0]-r.view2d.region_to_view(0,0)[0]
        event('MOUSEMOVE','NOTHING',**stress_xy)
        event('WHEELUPMOUSE',**stress_xy)


def stress_zoom_check():
    with timeline_context():
        r=bpy.context.region
        span=r.view2d.region_to_view(r.width,0)[0]-r.view2d.region_to_view(0,0)[0]
        assert not isclose(span,stress_span), (span,stress_span)


def stress_play():
    global stress_frame
    stress_frame=bpy.context.scene.frame_current
    with timeline_context():bpy.ops.screen.animation_play()


def stress_play_check():
    assert bpy.context.screen.is_animation_playing
    assert bpy.context.scene.frame_current!=stress_frame
    with timeline_context():bpy.ops.screen.animation_cancel(restore_frame=True)


def stress_right_settings():
    prepare_slider('SMOOTH','INLINE','cancel');select_slider_mode()
    with timeline_context():
        item=next(i for i in overlay._items(bpy.context)[0] if i[:2]==('SLIDER','SMOOTH'))
        x,y,w,h=item[3];r=bpy.context.region
        xy=dict(x=round(r.x+x+w/2),y=round(r.y+y+h/2))
        event('MOUSEMOVE','NOTHING',**xy);event('RIGHTMOUSE',**xy)


def stress_right_settings_check():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    assert settings._tool_editors
    ui_screenshot('right-click-tool-settings')


def stress_window():
    global stress_windows
    stress_windows={w.as_pointer() for w in bpy.context.window_manager.windows}
    bpy.ops.wm.window_new()
    window=next(w for w in bpy.context.window_manager.windows if w.as_pointer() not in stress_windows)
    # Bforartists creates a single 3D editor in a new window, not a workspace copy.
    area=max(window.screen.areas,key=lambda a:a.width*a.height)
    area.type='DOPESHEET_EDITOR';area.spaces.active.mode='TIMELINE'


def stress_window_check():
    global stress_other
    windows=list(bpy.context.window_manager.windows)
    assert len(windows)==len(stress_windows)+1
    stress_other=next(w for w in windows if w.as_pointer() not in stress_windows)
    for window in windows:
        areas=[a for a in window.screen.areas if toolbar.is_timeline(a)]
        assert areas
        for a in areas:
            r=next(r for r in a.regions if r.type=='WINDOW')
            with bpy.context.temp_override(window=window,area=a,region=r):
                assert overlay._items(bpy.context)[0]
    assert len(overlay._keymaps)==13


def stress_window_close():
    with bpy.context.temp_override(window=stress_other):bpy.ops.wm.window_close()


def stress_precision():
    event('MOUSEMOVE','NOTHING',x=slider_xy['x']+60,y=slider_xy['y'],shift=True)


def stress_precision_check():
    op=importlib.import_module(PACKAGE+'.operators.timeline_slider_ops').feedback(bpy.context.window,timeline())
    assert op and isclose(op.value,3,abs_tol=.01),op.value if op else None
    actual=next(c for c in object_snapshot(slider_obj) if c['index']==0)['keys'][1]['co'][1]
    assert isclose(actual,3.895,abs_tol=1e-4),actual


def stress_snap():
    event('MOUSEMOVE','NOTHING',x=slider_xy['x']+61,y=slider_xy['y'],ctrl=True)


def stress_snap_check():
    op=importlib.import_module(PACKAGE+'.operators.timeline_slider_ops').feedback(bpy.context.window,timeline())
    assert op and isclose(op.value,30,abs_tol=.01),op.value if op else None
    actual=next(c for c in object_snapshot(slider_obj) if c['index']==0)['keys'][1]['co'][1]
    assert isclose(actual,2.95,abs_tol=1e-4),actual


def stress_active_disable():
    global stress_active_op,stress_cleanup_records,lifecycle_area_count
    lifecycle_area_count=sum(len(w.screen.areas) for w in bpy.context.window_manager.windows)
    module=importlib.import_module(PACKAGE+'.operators.timeline_slider_ops')
    stress_active_op=module.feedback(bpy.context.window,timeline())
    assert stress_active_op and object_snapshot(slider_obj)!=slider_before
    # Observe cleanup before unregister invalidates the native operator RNA.
    stress_cleanup_records=[]
    original=module.ANIMASSIST_OT_timeline_slider._cleanup
    def observe_cleanup(self):
        original(self)
        stress_cleanup_records.append(self._timer is None)
    module.ANIMASSIST_OT_timeline_slider._cleanup=observe_cleanup
    import addon_utils
    addon_utils.disable(PACKAGE,default_set=True)


def stress_active_disabled():
    assert object_snapshot(slider_obj)==slider_before
    assert stress_cleanup_records and all(stress_cleanup_records)
    assert overlay._handle is None and not overlay._keymaps
    assert not importlib.import_module(PACKAGE+'.operators.timeline_slider_ops').busy()


def stress_save():
    global stress_saved
    stress_saved=dict(name=slider_obj.name,animation=object_snapshot(slider_obj),
        layout=bpy.context.preferences.addons[PACKAGE].preferences.timeline_layouts_json,
        reference=bpy.context.scene.anim_assist.reference_frame)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene-fixture.blend'))


def stress_lost_area():
    global stress_workspace
    stress_workspace=bpy.context.window.workspace
    bpy.context.window.workspace=next(w for w in bpy.data.workspaces if w!=stress_workspace)


def stress_lost_area_check():
    assert object_snapshot(slider_obj)==slider_before
    assert not importlib.import_module(PACKAGE+'.operators.timeline_slider_ops').busy()
    bpy.context.window.workspace=stress_workspace


def stress_load():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene-fixture.blend'))


def stress_load_check():
    assert object_snapshot(bpy.data.objects[stress_saved['name']])==stress_saved['animation']
    assert bpy.context.preferences.addons[PACKAGE].preferences.timeline_layouts_json==stress_saved['layout']
    assert bpy.context.scene.anim_assist.reference_frame==stress_saved['reference']
    assert overlay._handle is not None and len(overlay._keymaps)==13
    assert not importlib.import_module(PACKAGE+'.operators.timeline_slider_ops').busy()
    stress_geometry('loaded-scene')


def stress_preset_prepare():
    prepare_slider('SMOOTH','INLINE','commit');select_slider_mode()
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    prefsmod=importlib.import_module(PACKAGE+'.prefs')
    data=prefsmod.timeline_record(prefsmod.get_prefs(bpy.context))
    data['active']['tools']['SMOOTH']['presets']=[100]
    with timeline_context():settings.write(bpy.context,data)


def stress_preset_check():
    global recovery_after
    recovery_after=object_snapshot(slider_obj)
    actual=next(c for c in recovery_after if c['index']==0)['keys'][1]['co'][1]
    assert isclose(actual,.5,abs_tol=1e-5),(actual,.5)
    assert recovery_after!=recovery_before


def stress_reset():
    with timeline_context():
        item=next(i for i in overlay._items(bpy.context)[0] if i[:2]==('SLIDER','SMOOTH'))
        _,_,rect=overlay._parts(item[3],item[2],bpy.context.preferences.system.ui_scale)
        x,y,w,h=rect;r=bpy.context.region
        xy=dict(x=round(r.x+x+w/2),y=round(r.y+y+h/2))
        event('MOUSEMOVE','NOTHING',**xy);event('LEFTMOUSE',**xy);event('LEFTMOUSE','RELEASE',**xy)


def stress_reset_check():
    assert object_snapshot(slider_obj)==slider_before
    sliders=importlib.import_module(PACKAGE+'.operators.timeline_slider_ops')
    assert sliders.last_value(bpy.context.window,timeline(),'SMOOTH',-1)==0


def stress_neutral_scope():
    session=importlib.import_module(PACKAGE+'.core.timeline_slider_session')
    rows=[]
    # Seven neutral scalar settings; Breakdown's 50% is a blend, not neutral.
    for action in ('SMOOTH','NEIGHBORS','FRAME','EASE','AMPLIFY','SCALE_DRAG','OFFSET_DRAG'):
        prepare_slider(action,'INLINE','cancel')
        with timeline_context():
            before=object_snapshot(slider_obj)
            tx=session.capture(bpy.context,action)
            tx.preview(100 if action=='SCALE_DRAG' else 0)
            assert object_snapshot(slider_obj)==before,action
            tx.cancel()
            curves=compat.get_fcurves(slider_obj.animation_data.action,anim_data=slider_obj.animation_data)
            curves[1].lock=True;curves[2].hide=True
            before=object_snapshot(slider_obj)
            tx=session.capture(bpy.context,action);tx.preview(150 if action=='SCALE_DRAG' else 30)
            after=object_snapshot(slider_obj)
            assert after[0]!=before[0] and after[1:]==before[1:],action
            tx.cancel();assert object_snapshot(slider_obj)==before
            rows.append(dict(action=action,neutral=True,locked_hidden_preserved=True))
    (ROOT/'neutral-scope.json').write_text(json.dumps(rows,indent=2))


def stress_narrow():
    global stress_narrow_config
    stress_narrow_config=bpy.context.preferences.addons[PACKAGE].preferences.timeline_layouts_json
    with timeline_context():bpy.ops.screen.area_split(direction='VERTICAL',factor=.3)


def stress_narrow_check():
    areas=[a for a in bpy.context.window.screen.areas if toolbar.is_timeline(a)]
    assert len(areas)==2 and min(a.width for a in areas)<600
    for a in areas:
        r=next(r for r in a.regions if r.type=='WINDOW')
        with bpy.context.temp_override(area=a,region=r):
            items,_=overlay._items(bpy.context)
            assert {i[0] for i in items}>={'SEARCH','MORE','SETTINGS'}
            for i in items:
                x,y,w,h=i[3]
                assert 0<=x<x+w<=r.width+1 and 0<=y<y+h<=r.height+1
            bpy.ops.screen.screenshot_area(filepath=str(ROOT/('narrow-'+str(a.width)+'.png')))
    assert bpy.context.preferences.addons[PACKAGE].preferences.timeline_layouts_json==stress_narrow_config
