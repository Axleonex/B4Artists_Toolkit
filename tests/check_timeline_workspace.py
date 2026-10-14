"""Real-host workflow helpers; synthetic animation, native UI events."""
def workspace_visible(name):
    import importlib,json
    module=importlib.import_module('B4_anim_assist.ui.timeline_strip')
    canvas=importlib.import_module('B4_anim_assist.ui.timeline_overlay')
    rows=[]
    for a in bpy.context.window.screen.areas:
        if not module.is_timeline(a):continue
        r=next(r for r in a.regions if r.type=='WINDOW')
        with bpy.context.temp_override(area=a,region=r):
            items,band=canvas._items(bpy.context)
            rows.append(dict(height=a.height,region_height=r.height,band=band,controls=[i[:3] for i in items]))
            assert items and {i[0] for i in items}>={'SEARCH','MORE','SETTINGS'},rows
            for i in items:
                x,y,w,h=i[3]
                assert 0<=x<x+w<=r.width+1 and 0<=y<y+h<=r.height+1,i
            bpy.ops.screen.screenshot_area(filepath=str(root/(name+'.png')))
    assert rows
    (root/(name+'.json')).write_text(json.dumps(rows,indent=2))


def workspace_defaults():
    global workspace_initial_height
    workspace_initial_height=timeline().height
    assert workspace_initial_height<=130,workspace_initial_height
    with timeline_context():
        items,_=overlay._items(bpy.context)
        assert {i[1] for i in items if i[0]=='SLIDER'}=={'DRAG','SMOOTH'}
        assert any(i[:2]==('POPOUT','SCALE_DRAG') for i in items)
    workspace_visible('initial-row')


def workspace_right_settings():
    prepare_slider('SMOOTH','INLINE','cancel')
    with timeline_context():
        item=next(i for i in overlay._items(bpy.context)[0] if i[:2]==('SLIDER','SMOOTH'))
        x,y,w,h=item[3];r=bpy.context.region
        point=dict(x=round(r.x+x+w/2),y=round(r.y+y+h/2))
        event('MOUSEMOVE','NOTHING',**point);event('RIGHTMOUSE',**point)


def workspace_popout():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    current=settings._tool_editors[bpy.context.window.as_pointer()]
    assert current.action=='SMOOTH'
    current.mode='POPOUT'
    ui_screenshot('workspace-tool-settings')


def workspace_popout_check():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    assert settings.record(bpy.context)['active']['tools']['SMOOTH']['mode']=='POPOUT'
    with timeline_context():assert any(i[:2]==('POPOUT','SMOOTH') for i in overlay._items(bpy.context)[0])


def workspace_settings_change():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    current=settings.editor(bpy.context)
    assert current
    current.family='curves'
    index=next(i for i,e in enumerate(current.entries) if e.action=='NEIGHBORS')
    current.active_index=index;current.entries[index].mode='INLINE'
    with timeline_context():bpy.ops.animassist.toolbar_reorder(direction=-1)
    assert current.entries[current.active_index].action=='NEIGHBORS'
    ui_screenshot('workspace-toolbar-settings')


def workspace_settings_check():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    data=settings.record(bpy.context)
    assert data['active']['tools']['NEIGHBORS']['mode']=='INLINE'
    assert object_snapshot(bpy.context.active_object)==ui_before_animation
    ui_screenshot('workspace-custom-row')


def workspace_dirty_load():
    global workspace_ids
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    data=settings.record(bpy.context)
    workspace_ids={x['name']:x['id'] for x in data['saved']}
    data['active']['tools']['SMOOTH']['width']=190
    with timeline_context():
        settings.write(bpy.context,data)
        assert bpy.ops.animassist.layout_action('INVOKE_DEFAULT',operation='LOAD',target=workspace_ids['Blocking'])=={'RUNNING_MODAL'}


def workspace_guard_check():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    current=settings._layout_editors[bpy.context.window.as_pointer()]
    assert current.operation=='LOAD' and not current.discard_changes
    assert settings.record(bpy.context)['active']['tools']['SMOOTH']['width']==190
    assert object_snapshot(bpy.data.objects[layout_obj_name])==layout_animation
    ui_screenshot('layout-discard-guard')


def workspace_layout_switch():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    with timeline_context():
        assert settings.record(bpy.context)['active']['tools']['SMOOTH']['width']==190
        for name in ('Blocking','Polish'):
            assert bpy.ops.animassist.layout_action('EXEC_DEFAULT',operation='LOAD',target=workspace_ids[name],discard_changes=True)=={'FINISHED'}
            assert settings.record(bpy.context)['active']['name']==name
        assert object_snapshot(bpy.data.objects[layout_obj_name])==layout_animation


def workspace_save():
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    expected=settings.record(bpy.context)
    assert expected['active']['name']=='Polish' and len(expected['saved'])==2
    (ROOT/'workspace-saved-layout.json').write_text(json.dumps(expected))
    with timeline_context():
        bpy.ops.wm.save_userpref()
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'workflow-fixture.blend'))
    workspace_visible('saved-workspace')


def workspace_resize(height):
    settings=importlib.import_module(PACKAGE+'.ui.timeline_settings')
    sliders=importlib.import_module(PACKAGE+'.operators.timeline_slider_ops')
    diagnostics=dict(context_area=str(bpy.context.area),region=str(bpy.context.region),
        animation_playing=bpy.context.screen.is_animation_playing,slider_busy=sliders.busy(),
        toolbar_dialogs=len(settings._editors),tool_dialogs=len(settings._tool_editors),
        layout_dialogs=len(settings._layout_editors),native_resize_poll=bpy.ops.screen.area_move.poll())
    (ROOT/'resize-context.json').write_text(json.dumps(diagnostics,indent=2))
    with timeline_context():stress_resize(height)


def workspace_restart():
    import importlib,json
    settings=importlib.import_module('B4_anim_assist.ui.timeline_settings')
    expected=json.loads((root/'workspace-saved-layout.json').read_text())
    assert settings.record(bpy.context)==expected
    workspace_visible('restart-row')
    bpy.ops.wm.open_mainfile(filepath=str(root/'workflow-fixture.blend'))
