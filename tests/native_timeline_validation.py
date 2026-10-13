"""Native GUI integration validation; launch only with a task-owned profile.

Not a background Blender substitute. Assertions and render captures execute
inside the compiled native app. Input gestures are performed separately.
"""
import bpy
import addon_utils
import builtins
import contextlib
import datetime
import hashlib
import importlib
import json
import os
from pathlib import Path
import struct
import time
import traceback
import zlib

ROOT = Path(os.environ['AA_VALIDATION_ROOT']).resolve()
CONFIG = Path(os.environ['BLENDER_USER_CONFIG']).resolve()
assert CONFIG.is_dir() and Path(bpy.utils.user_resource('CONFIG')).resolve() == CONFIG
ROOT.mkdir(parents=True, exist_ok=True)
PACKAGE = 'B4_anim_assist'
RESUME = os.environ.get('AA_VALIDATION_RESUME') == '1'
if RESUME:
    assert PACKAGE in bpy.context.preferences.addons, 'Enable preference was not retained'
    assert addon_utils.check(PACKAGE)[1], 'Saved addon was not automatically enabled'
else:
    addon_utils.enable(PACKAGE, default_set=True, persistent=True)
bpy.context.preferences.use_preferences_save = False
cat = importlib.import_module(PACKAGE + '.ui.timeline_catalog')
toolbar = importlib.import_module(PACKAGE + '.ui.timeline_strip')
compat = importlib.import_module(PACKAGE + '.core.fcurve_compat')
checks = json.loads((ROOT/'assertions.json').read_text()) if RESUME else []
captures = []
capture_handles = []
last_request = json.loads((ROOT/'request.json').read_text())['id'] if RESUME else None

def write_results():
    (ROOT / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')

def check(name, condition, actual=None, expected=None):
    record = dict(name=name, passed=bool(condition), actual=actual, expected=expected,
                  utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    checks.append(record)
    write_results()
    if not condition:
        raise AssertionError(name + ': ' + repr(actual) + ' expected ' + repr(expected))
    return record

def timelines():
    return [(w, a) for w in bpy.context.window_manager.windows for a in w.screen.areas
            if a.type == 'DOPESHEET_EDITOR' and a.spaces.active.mode == 'TIMELINE']

@contextlib.contextmanager
def timeline_context(index=0, region='WINDOW'):
    w, a = timelines()[index]
    r = next(r for r in a.regions if r.type == region)
    with bpy.context.temp_override(window=w, area=a, region=r):
        yield a

def geometry():
    return [dict(window=w.as_pointer(), screen=w.screen.name, area=a.as_pointer(),
                 x=a.x, y=a.y, width=a.width, height=a.height,
                 visible=a.spaces.active.show_region_tool_header,
                 hidden_by_user=a.spaces.active.timeline_toolbar_hidden_by_user,
                 regions=[dict(type=r.type, x=r.x, y=r.y, width=r.width, height=r.height)
                          for r in a.regions]) for w, a in timelines()]

def row_check(name='visible native rows'):
    g = geometry()
    valid = bool(g) and all(entry['visible'] and
        all(any(r['type'] == kind and r['width'] > 1 and r['height'] > 1
                for r in entry['regions']) for kind in ('TOOL_HEADER','HEADER','WINDOW'))
        for entry in g)
    return check(name, valid, g, 'All Timelines have two native headers and a visible WINDOW')

def object_snapshot(obj):
    ad = obj.animation_data
    return [dict(path=f.data_path, index=f.array_index,
                 keys=[dict(co=list(k.co), left=list(k.handle_left), right=list(k.handle_right),
                            selected=k.select_control_point, interpolation=k.interpolation,
                            left_type=k.handle_left_type, right_type=k.handle_right_type, type=k.type,
                            easing=k.easing, amplitude=k.amplitude, back=k.back, period=k.period,
                            selected_left=k.select_left_handle, selected_right=k.select_right_handle)
                       for k in f.keyframe_points])
            for f in compat.get_fcurves(ad.action, anim_data=ad)] if ad and ad.action else []

def fixture(pose=False):
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for obj in list(bpy.context.scene.objects):
        if obj.name.startswith('VAL_'):
            bpy.data.objects.remove(obj, do_unlink=True)
        else:
            obj.select_set(False)
    scene=bpy.context.scene
    scene.frame_start=1; scene.frame_end=40; scene.use_preview_range=False
    if pose:
        arm=bpy.data.armatures.new('VAL_Armature')
        obj=bpy.data.objects.new('VAL_Rig', arm); scene.collection.objects.link(obj)
        obj.select_set(True); bpy.context.view_layer.objects.active=obj
        bpy.ops.object.mode_set(mode='EDIT')
        for name,x in [('Hand.L',1),('Hand.R',-1)]:
            b=arm.edit_bones.new(name); b.head=(x,0,0); b.tail=(x,0,1)
        bpy.ops.object.mode_set(mode='POSE')
        arm.bones.active=arm.bones['Hand.L']
        select_bone=importlib.import_module(PACKAGE+'.core.bone_utils').set_pose_bone_selected
        for bone in obj.pose.bones: select_bone(bone,True)
        for pb in obj.pose.bones:
            for frame,v in [(1,0.0),(20,4.0),(40,1.0)]:
                pb.location=(v,0,0); pb.keyframe_insert('location', frame=frame)
    else:
        obj=bpy.data.objects.new('VAL_Animated',None); scene.collection.objects.link(obj)
        obj.select_set(True); bpy.context.view_layer.objects.active=obj
        for frame,v in [(1,0.0),(20,4.0),(40,1.0)]:
            obj.location=(v,0,0); obj.keyframe_insert('location',frame=frame)
    for fc in compat.get_fcurves(obj.animation_data.action,anim_data=obj.animation_data):
        fc.select=True
        for k in fc.keyframe_points:
            k.select_control_point=True
            k.handle_left_type='FREE'; k.handle_right_type='FREE'
            k.handle_left=(k.co.x-2,k.co.y-0.25)
            k.handle_right=(k.co.x+2,k.co.y+0.25)
    target=bpy.data.objects.new('VAL_Target',None); scene.collection.objects.link(target)
    target.location=(6,2,1); target.rotation_euler=(0.1,0.2,0.3); target.scale=(1.5,1.2,0.8)
    target.select_set(True)
    obj['space']=0.0
    p8=scene.anim_assist_p8
    p8.switch_prop_path='["space"]'; p8.switch_new_value=1.0; p8.switch_bone_name=''
    p8.comp_range='CUSTOM'; p8.comp_range_start=1; p8.comp_range_end=3
    scene.frame_set(10)
    bpy.context.view_layer.update()
    return obj,target

def dispatch(action):
    with timeline_context(region='TOOL_HEADER'):
        return sorted(bpy.ops.animassist.timeline_tool('INVOKE_DEFAULT',action=action))

MODAL_ACTIONS={'DRAG','NEIGHBORS','FRAME','EASE','AMPLIFY','SMOOTH','SCALE_DRAG','OFFSET_DRAG','OFFSET'}

def immediate_catalogue():
    """Exercise every immediate catalogue dispatch with an independent fixture.

    This is access and representative effect coverage, not proof of every
    operator algorithm on every production rig. Modal gestures run separately.
    """
    results=[]
    p7s=importlib.import_module(PACKAGE+'.core.p7_session')
    pose_actions={'MIRROR_ACTIVE','MIRROR_SELECTED','MIRROR_FRAME','MIRROR_RANGE','OPPOSITE','SWAP'}
    matching={'MATCH_WORLD','MATCH_PARENT','MATCH_TARGET','MATCH_LOCATION','MATCH_ROTATION',
              'MATCH_SCALE','MATCH_TRS','MATCH_VISUAL','MATCH_LOCAL','ALIGN'}
    for action in cat.ACTIONS:
        if action in MODAL_ACTIONS: continue
        entry={'action':action}
        try:
            with timeline_context():
                if bpy.context.scene.anim_assist_p5.overlay_enabled:
                    bpy.ops.animassist.p5_disable_overlay()
                if bpy.ops.animassist.p7_purge_artifacts.poll():
                    bpy.ops.animassist.p7_purge_artifacts()
                obj,target=fixture(pose=action in pose_actions)
                scene=bpy.context.scene
                prefs=bpy.context.preferences.addons[PACKAGE].preferences
                p6=scene.anim_assist_p6; p6.anchor_mode='FIRST'; p6.range_mode='SELECTION'
                p6.offset_frames=1; p6.ripple_delta=1; p6.insert_frames=1; p6.modal_snap=False
                p7=scene.anim_assist_p7; p7.bake_range_mode='CUSTOM'
                p7.bake_range_start=1; p7.bake_range_end=3; p7.bake_step=1
                p7.smart_bake_tolerance=0.01
                curves=compat.get_fcurves(obj.animation_data.action,anim_data=obj.animation_data)
                if action in {'ALL','RANGE','ENDS','GROW_LEFT','GROW_RIGHT','GROW_BOTH','SELECT_BREAKDOWNS'}:
                    for fc in curves:
                        for i,k in enumerate(fc.keyframe_points):
                            k.select_control_point=action.startswith('GROW_') and i==1
                            if action=='SELECT_BREAKDOWNS': k.type='BREAKDOWN' if i==1 else 'KEYFRAME'
                if action=='HANDLE_FREE':
                    for fc in curves:
                        for k in fc.keyframe_points: k.handle_left_type='AUTO'; k.handle_right_type='AUTO'
                if action=='TYPE_KEYFRAME':
                    for fc in curves:
                        for k in fc.keyframe_points: k.type='BREAKDOWN'
                if action=='SNAP':
                    for fc in curves:
                        for k,delta in zip(fc.keyframe_points,(0.25,0.6,0.4)): k.co.x+=delta
                if action=='DISTRIBUTE_TIME':
                    for fc in curves: fc.keyframe_points[1].co.x=7
                if action=='REDUCE':
                    for fc in curves:
                        for k in fc.keyframe_points:
                            k.co.y=k.co.x; k.interpolation='LINEAR'
                if action in pose_actions:
                    obj.pose.bones['Hand.L'].location=(1,2,0)
                    obj.pose.bones['Hand.R'].location=(4,3,0)
                    if action=='MIRROR_RANGE': scene.frame_end=3
                if action=='MATCH_PARENT': obj.parent=target
                if action=='SWITCH_INFLUENCE': scene.anim_assist_p8.switch_new_value=0.6
                if action=='PASTE_KEYS':
                    bpy.ops.animassist.copy_selected_keys()
                    prefs.timeline_paste_offset=100
                if action in {'BOOKMARK_RECALL','BOOKMARK_REMOVE'}:
                    settings=scene.anim_assist
                    settings.bookmarks.clear()
                    b=settings.bookmarks.add(); b.name='Fixture reference'; b.frame=13
                    settings.active_bookmark_index=0; settings.reference_frame=3
                if action=='BOOKMARK_ADD': scene.anim_assist.reference_frame=13
                if action=='BAKE_CLEANUP': bpy.ops.animassist.p7_create_proxy(proxy_type='WORLD_SPACE')
                if action in {'TRAIL_HIDE','TRAIL_REFRESH','TRAIL_DIAGNOSE'}:
                    bpy.ops.animassist.p5_enable_overlay()
                if action=='OFFSET_SCENE_RANGE':
                    scene.anim_assist.mask.start_frame=12; scene.anim_assist.mask.end_frame=18
                old_mask=scene.anim_assist.mask.enabled
                before=object_snapshot(obj)
                before_count=sum(len(c['keys']) for c in before)
                before_objects=len(scene.objects)
                before_loc=tuple(obj.location); target_matrix=[list(r) for r in target.matrix_world]
                object_matrix=[list(r) for r in obj.matrix_world]
                reason=toolbar._unavailable(bpy.context,bpy.context.area,action)
                assert not reason,reason
            status=dispatch(action)
            assert status==['FINISHED'],status
            bpy.context.view_layer.update()
            after=object_snapshot(obj)
            count=sum(len(c['keys']) for c in after)
            all_keys=[k for c in after for k in c['keys']]
            entry.update(status=status,before_key_count=before_count,after_key_count=count)
            condition=None; expected='Action-specific state assertion'
            if action.startswith('B') and action in {'B25','B50','B75'}:
                expected_value={'B25':1.0,'B50':2.0,'B75':3.0}[action]
                points=[k for c in after if c['index']==0 for k in c['keys'] if abs(k['co'][0]-10)<1e-5]
                condition=len(points)==1 and abs(points[0]['co'][1]-expected_value)<1e-5
                entry['points']=points; expected=f'New frame-10 key with value {expected_value}'
            elif action in {'PUSH_PREV','PULL_PREV','PULL_NEXT','PUSH_NEXT','INBETWEEN','INBETWEENS'}:
                condition=count>before_count; expected='Added breakdown/inbetween keys'
            elif action.startswith('HANDLE_'):
                kind={'HANDLE_AUTO':'AUTO','HANDLE_CLAMPED':'AUTO_CLAMPED','HANDLE_VECTOR':'VECTOR',
                      'HANDLE_ALIGNED':'ALIGNED','HANDLE_FREE':'FREE'}[action]
                condition=all(k['left_type']==kind and k['right_type']==kind for k in all_keys)
                expected='Both handles set to '+kind
            elif action.startswith('TYPE_'):
                kind=cat.ACTIONS[action][1]['key_type']
                condition=all(k['type']==kind for k in all_keys); expected='Key types '+kind
            elif action in {'ALL','RANGE'}:
                condition=all(k['selected'] for k in all_keys); expected='All fixture keys selected'
            elif action=='ENDS':
                condition=all([k['selected'] for k in c['keys']]==[True,False,True] for c in after)
                expected='Endpoints selected, middle not selected'
            elif action.startswith('GROW_'):
                selected={'GROW_LEFT':[True,True,False],'GROW_RIGHT':[False,True,True],
                          'GROW_BOTH':[True,True,True]}[action]
                condition=all([k['selected'] for k in c['keys']]==selected for c in after); expected=selected
            elif action=='SELECT_BREAKDOWNS':
                condition=all([k['selected'] for k in c['keys']]==[False,True,False] for c in after)
                expected='Only middle breakdown keys selected'
            elif action in {'NUDGE_LEFT','NUDGE_RIGHT','OFFSET_ACTION','RIPPLE','INSERT_TIME','REMOVE_TIME',
                            'T80','T90','T110','T120','REVERSE','SNAP','DISTRIBUTE_TIME'}:
                if action.startswith('T'):
                    factor=cat.ACTIONS[action][1]['scale_factor']; frames=[1,1+19*factor,1+39*factor]
                else:
                    frames={'NUDGE_LEFT':[0,19,39],'NUDGE_RIGHT':[2,21,41],'OFFSET_ACTION':[2,21,41],
                            'RIPPLE':[1,21,41],'INSERT_TIME':[1,21,41],'REMOVE_TIME':[1,19,39],
                            'REVERSE':[1,21,40],'SNAP':[1,21,40],'DISTRIBUTE_TIME':[1,20.5,40]}[action]
                actual=[[k['co'][0] for k in c['keys']] for c in after]
                condition=all(len(row)==len(frames) and all(abs(x-y)<1e-4 for x,y in zip(row,frames)) for row in actual)
                entry['frames']=actual; expected=frames
            elif action=='REFERENCE':
                condition=scene.anim_assist.reference_frame==10; expected='Reference frame 10'
            elif action=='COPY_KEYS':
                size=importlib.import_module(PACKAGE+'.core.key_utils').clipboard_size()
                condition=size==9; entry['clipboard_size']=size; expected=9
            elif action=='PASTE_KEYS':
                condition=all([k['co'][0] for k in c['keys']]==[1,20,40,101,120,140] for c in after)
                expected='Copied key times shifted by 100'
            elif action=='BOOKMARK_ADD': condition=scene.anim_assist.bookmarks[-1].frame==13
            elif action=='BOOKMARK_REMOVE': condition=len(scene.anim_assist.bookmarks)==0
            elif action=='BOOKMARK_RECALL': condition=scene.anim_assist.reference_frame==13 and scene.frame_current==10
            elif action in matching:
                if action=='MATCH_WORLD': condition=max(abs(obj.matrix_world[r][c]-(1 if r==c else 0)) for r in range(4) for c in range(4))<1e-4
                elif action=='ALIGN': condition=max(abs(target.matrix_world[r][c]-object_matrix[r][c]) for r in range(4) for c in range(4))<1e-4
                elif action=='MATCH_LOCATION': condition=max(abs(obj.matrix_world.translation[i]-target.location[i]) for i in range(3))<1e-4
                elif action=='MATCH_ROTATION': condition=max(abs(obj.rotation_euler[i]-target.rotation_euler[i]) for i in range(3))<1e-4
                elif action=='MATCH_SCALE': condition=max(abs(obj.scale[i]-target.scale[i]) for i in range(3))<1e-4
                else: condition=max(abs(obj.matrix_world[r][c]-target_matrix[r][c]) for r in range(4) for c in range(4))<1e-4
                entry['matrix']=[list(r) for r in obj.matrix_world]; expected='Configured matched transform'
            elif action.startswith('SWITCH_'):
                val=0.6 if action=='SWITCH_INFLUENCE' else 1.0
                condition=abs(obj['space']-val)<1e-5
                if action=='SWITCH_RANGE': condition=condition and any(c['path']=='["space"]' for c in after)
                entry['property_value']=obj['space']; expected=val
            elif action in {'BAKE_STEP','SMART_BAKE'}:
                condition=any(c['path']=='location' and any(abs(k['co'][0]-3)<1e-4 for k in c['keys']) for c in after)
                expected='Bake includes configured end frame 3'
            elif action=='REDUCE': condition=count<before_count; expected='Redundant linear middle keys removed'
            elif action.startswith('PROXY_'):
                condition=len(scene.objects)>before_objects and any(o.get(p7s.TAG_TEMP) for o in scene.objects)
                expected='Tagged proxy created'
            elif action=='BAKE_CLEANUP': condition=not any(o.get(p7s.TAG_TEMP) for o in scene.objects)
            elif action.startswith('TRAIL_'):
                condition=scene.anim_assist_p5.overlay_enabled==(action!='TRAIL_HIDE')
                if action!='TRAIL_HIDE':
                    overlay=importlib.import_module(PACKAGE+'.operators.p5_overlay_ops')
                    cache_entry=overlay.get_entry(overlay.make_target_key(obj.name,None))
                    condition=condition and cache_entry is not None and len(cache_entry.samples)>1
                expected='Overlay state and sampled trajectory cache'
            elif action=='OFFSET_MASK': condition=scene.anim_assist.mask.enabled!=old_mask
            elif action=='OFFSET_SCENE_RANGE': condition=(scene.anim_assist.mask.start_frame,scene.anim_assist.mask.end_frame)==(1,40)
            elif action=='OPPOSITE': condition=obj.data.bones.active.name=='Hand.R'
            elif action in {'MIRROR_ACTIVE','MIRROR_SELECTED','SWAP'}:
                entry['bone_locations']={pb.name:list(pb.location) for pb in obj.pose.bones}
                condition=entry['bone_locations']!={'Hand.L':[1,2,0],'Hand.R':[4,3,0]}
                expected='Configured mirrored or swapped pose differs'
            elif action in {'MIRROR_FRAME','MIRROR_RANGE'}:
                condition=count>before_count; expected='Mirrored pose keys created'
            assert condition is not None, 'Missing outcome assertion for '+action
            entry.update(expected=expected,passed=bool(condition))
            check('immediate action '+action,condition,entry,expected)
        except Exception:
            entry.update(passed=False,error=traceback.format_exc())
        results.append(entry)
    (ROOT/'immediate-actions.json').write_text(json.dumps(results,indent=2)+'\n')
    return dict(count=len(results),failed=[e for e in results if not e['passed']])

modal_records=[]

def modal_start(action,ending,elastic=False):
    global modal_obj,modal_before,modal_live_snapshot,modal_case
    assert action in MODAL_ACTIONS
    with timeline_context():
        modal_obj,_target=fixture()
        bpy.context.scene.anim_assist_p6.modal_snap=False
        bpy.context.scene.anim_assist_p3.factor=0.5
        bpy.context.scene.anim_assist.reference_frame=1
        bpy.context.scene.anim_assist.mask.enabled=False
        if action in {'NEIGHBORS','FRAME','AMPLIFY','SMOOTH'}:
            for fc in compat.get_fcurves(modal_obj.animation_data.action,anim_data=modal_obj.animation_data):
                for i,k in enumerate(fc.keyframe_points): k.select_control_point=i==1
        if action=='OFFSET': bpy.context.scene.frame_set(20)
        if elastic:
            for fc in compat.get_fcurves(modal_obj.animation_data.action,anim_data=modal_obj.animation_data):
                key=fc.keyframe_points[-1]
                key.interpolation='ELASTIC'; key.easing='EASE_OUT'
                key.amplitude=3.7; key.back=2.5; key.period=0.8
        modal_before=object_snapshot(modal_obj)
    modal_case={'action':action,'ending':ending,'before':modal_before,'start_epoch':time.time()}
    status=dispatch(action)
    modal_case['dispatch_status']=status
    names=[op.bl_rna.identifier for w in bpy.context.window_manager.windows for op in w.modal_operators]
    modal_case['operators_after_start']=names
    required=toolbar._operator(action).get_rna_type().identifier
    check('modal starts '+action+' '+ending,status==['FINISHED'] and required in names,names,required)
    return {'action':action,'ending':ending,'native_modal_operators':names}

def modal_live():
    global modal_live_snapshot
    modal_live_snapshot=object_snapshot(modal_obj)
    def geometry_only(snapshot):
        return [[(k['co'],k['left'],k['right']) for k in curve['keys']]
                for curve in snapshot]
    changed=geometry_only(modal_live_snapshot)!=geometry_only(modal_before)
    modal_case['live']=modal_live_snapshot
    check('modal live effect '+modal_case['action']+' '+modal_case['ending'],changed,
          modal_live_snapshot,'fixture animation visibly changes during adjustment')
    return {'changed':changed,'operators':[op.bl_rna.identifier for w in bpy.context.window_manager.windows for op in w.modal_operators]}

def modal_finish():
    bpy.context.view_layer.update()
    after=object_snapshot(modal_obj)
    modal_case['after']=after
    names=[op.bl_rna.identifier for w in bpy.context.window_manager.windows for op in w.modal_operators]
    modal_case['operators_after_finish']=names
    ending=modal_case['ending']; action=modal_case['action']
    condition=after==modal_before if ending=='cancel' else after==modal_live_snapshot
    check('modal '+ending+' preserves intended state '+action,condition,after,
          'original snapshot' if ending=='cancel' else 'committed live snapshot')
    check('modal handler cleaned up '+action+' '+ending,not names,names,[])
    if action=='OFFSET': check('offset session ends '+ending,not bpy.context.scene.anim_assist.anim_offset_active,None,False)
    modal_case['passed']=True
    modal_records.append(modal_case.copy())
    (ROOT/'modal-actions.json').write_text(json.dumps(modal_records,indent=2)+'\n')
    return {'action':action,'ending':ending,'passed':condition}

def save_png(path,w,h,pixels):
    def chunk(kind,data):
        return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    stride=w*4
    raw=b''.join(b'\0'+pixels[y*stride:(y+1)*stride] for y in range(h-1,-1,-1))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',w,h,8,6,0,0,0))+
                     chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))

def arm_capture(label,seconds=20):
    import gpu
    stop_capture()
    captures.clear()
    deadline=time.monotonic()+seconds
    latest={}
    def capture(kind):
        if time.monotonic()>deadline or len(captures)>=180: return
        area=bpy.context.area; region=bpy.context.region
        if not toolbar.is_timeline(area): return
        now=time.monotonic()
        key=(area.as_pointer(),kind)
        if now-latest.get(key,0)<0.025: return
        latest[key]=now
        entry=dict(monotonic=now, epoch=time.time(), label=label, kind=kind, geometry=geometry(),
                   region=dict(x=region.x,y=region.y,width=region.width,height=region.height))
        try:
            # Native UI regions render into a local offscreen framebuffer.
            buff=gpu.state.active_framebuffer_get().read_color(0,0,
                     region.width,region.height,4,0,'UBYTE')
            buff.dimensions=region.width*region.height*4
            pixels=bytes(buff)
            entry['pixel_sha256']=hashlib.sha256(pixels).hexdigest()
            entry['distinct_byte_values']=len(set(pixels))
            entry['_pixels']=pixels
        except Exception as exc:
            entry['capture_error']=str(exc)
        captures.append(entry)
    for region in ('TOOL_HEADER','HEADER','WINDOW'):
        h=bpy.types.SpaceDopeSheetEditor.draw_handler_add(capture,(region,),region,'POST_PIXEL')
        capture_handles.append((h,region))
    for w,a in timelines(): a.tag_redraw()
    return dict(label=label,armed_monotonic=time.monotonic(),deadline=deadline)

def stop_capture():
    for h,region in capture_handles:
        bpy.types.SpaceDopeSheetEditor.draw_handler_remove(h,region)
    capture_handles.clear()

def flush_capture(label):
    stop_capture()
    folder=ROOT/label; folder.mkdir(exist_ok=True)
    for i,entry in enumerate(captures):
        pix=entry.pop('_pixels',None)
        if pix is not None:
            r=entry['region']; filename=f'{i:03}-{entry["kind"]}.png'
            save_png(folder/filename,r['width'],r['height'],pix)
            entry['image']=filename
    (folder/'frames.json').write_text(json.dumps(captures,indent=2)+'\n')
    return dict(samples=len(captures),kind_counts={kind:sum(e['kind']==kind for e in captures)
                                                for kind in ('TOOL_HEADER','HEADER','WINDOW')},
                errors=[e.get('capture_error') for e in captures if 'capture_error' in e])

def bridge():
    global last_request
    request=ROOT/'request.json'
    if request.exists():
        try:
            data=json.loads(request.read_text())
            if data['id'] != last_request:
                last_request=data['id']; globals()['result']=None
                try:
                    exec(data['code'],globals())
                    response=dict(id=last_request,result=globals().get('result'),error=None)
                except Exception:
                    response=dict(id=last_request,error=traceback.format_exc())
                (ROOT/'response.json').write_text(json.dumps(response,indent=2,default=str)+'\n')
        except (OSError,json.JSONDecodeError): pass
    return 0.15

def startup():
    if not RESUME:
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'AA_NATIVE_VALIDATION.blend'),check_existing=False)
    (ROOT/('restart-ready.json' if RESUME else 'ready.json')).write_text(json.dumps(dict(binary=bpy.app.binary_path,
          build_hash=bpy.app.build_hash.decode(),config=str(CONFIG),geometry=geometry()),indent=2))
    return None

bpy.app.timers.register(bridge,first_interval=1.0,persistent=True)
bpy.app.timers.register(startup,first_interval=3.0)
builtins.aa_validation=globals()
