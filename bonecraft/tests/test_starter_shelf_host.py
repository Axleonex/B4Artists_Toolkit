"""Starter selection, dependency failure/cancel, fitting, dragging and shelf RNA."""
from types import SimpleNamespace
from unittest.mock import patch

import bpy


def run():
    from boneforge.autorig import quick_human as qh, rig_assets as ra, rig_asset_ops as ops
    native = getattr(bpy.types, 'VIEW3D_AST_object', None)
    native_poll = native.__dict__['poll'] if native else None
    native_asset_poll = native.__dict__['asset_poll'] if native else None
    qh.register()
    ra.register()
    try:
        shelf = getattr(bpy.types, ra.SHELF_IDNAME)
        assert shelf.bl_activate_operator == 'BONEFORGE_OT_add_starter_asset'
        assert shelf.bl_drag_operator == 'BONEFORGE_OT_drag_starter_asset'
        assert 'DEFAULT_VISIBLE' in shelf.bl_options
        native_enum = bpy.types.AssetWeakReference.bl_rna.properties['asset_library_type'].enum_items
        for operator in (bpy.ops.boneforge.add_starter_asset, bpy.ops.boneforge.drag_starter_asset):
            own_enum = operator.get_rna_type().properties['asset_library_type'].enum_items
            assert {(e.identifier, e.value) for e in own_enum} == {(e.identifier, e.value) for e in native_enum}
        assert ops.draw_starter_header in bpy.types.VIEW3D_HT_header.draw._draw_funcs
        if native:
            assert not native.poll(bpy.context) and shelf.poll(bpy.context)
            asset = SimpleNamespace(metadata=SimpleNamespace(tags=[SimpleNamespace(name=ra.ASSET_TAG)]))
            assert not native.asset_poll(asset)
            assert bpy.ops.boneforge.toggle_starter_shelf() == {'FINISHED'}
            assert native.poll(bpy.context) and not shelf.poll(bpy.context)
            assert bpy.ops.boneforge.toggle_starter_shelf() == {'FINISHED'}
        starter = next(r for r in ra.starter_manifest() if r['requires_rigify'])
        identifier = 'quick_rigs.blend/Object/' + starter['asset_name']
        assert ra.starter_from_reference(identifier) == starter
        assert ra.starter_from_reference('quick_rigs.blend/Object/Not A Rig') is None
        assert ra.starter_from_reference(identifier.replace('/', '\\')) == starter

        # The dependency prompt retains the choice and target; rejecting it has no scene mutation.
        prompts = []
        fake = SimpleNamespace(relative_asset_identifier=identifier, target_captured=False)
        ctx = SimpleNamespace(active_object=None, window_manager=SimpleNamespace(
            invoke_props_dialog=lambda op, **kw: prompts.append((op, kw)) or {'RUNNING_MODAL'}))
        before = set(bpy.data.objects.keys())
        with patch.object(ops, 'available', return_value=False):
            assert ops.BONEFORGE_OT_add_starter_asset.invoke(fake, ctx, None) == {'RUNNING_MODAL'}
        assert prompts[0][1]['confirm_text'] == 'Enable Rigify & Add Rig'
        assert fake.relative_asset_identifier == identifier
        assert set(bpy.data.objects.keys()) == before

        def refused(**kwargs):
            try:
                return bpy.ops.boneforge.add_starter_asset('EXEC_DEFAULT', **kwargs) == {'CANCELLED'}
            except RuntimeError:
                return True

        # Enabling failure and an installed version without the selected preset add nothing.
        with patch.object(ops, 'available', return_value=False), patch.object(qh, 'enable_rigify_if_available', return_value=False):
            assert refused(relative_asset_identifier=identifier)
        assert set(bpy.data.objects.keys()) == before
        with patch.object(ops, 'available', return_value=False), patch.object(qh, 'enable_rigify_if_available', return_value=True):
            assert refused(relative_asset_identifier=identifier)
        assert set(bpy.data.objects.keys()) == before

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = None
        # Basic works while the dependency is unavailable; run twice.
        for _ in range(2):
            with patch.object(qh, 'enable_rigify_if_available', side_effect=AssertionError('Basic must not enable Rigify')):
                assert bpy.ops.boneforge.add_starter_asset('EXEC_DEFAULT',
                    relative_asset_identifier='quick_rigs.blend/Object/' + ra.ASSET_NAME) == {'FINISHED'}
            arm = bpy.context.active_object
            assert len(arm.data.bones) == 19 and arm.get(qh.DROPPED_RIG_PROP) == 'fallback'

        # Accept the enable-and-add choice. Every shipped metarig must be usable.
        for r in ra.starter_manifest():
            if not r['requires_rigify']:
                continue
            assert bpy.ops.boneforge.add_starter_asset('EXEC_DEFAULT',
                relative_asset_identifier='quick_rigs.blend/Object/' + r['asset_name']) == {'FINISHED'}
            assert bpy.context.active_object.type == 'ARMATURE'
            assert qh._is_rigify_metarig(bpy.context.active_object)

        # Fit to the exact mesh chosen before the popup; don't auto-weight by default.
        bpy.ops.mesh.primitive_cube_add(size=2, location=(3, 0, 1))
        mesh = bpy.context.active_object
        assert bpy.ops.boneforge.add_starter_asset('EXEC_DEFAULT', relative_asset_identifier=identifier,
                                                 target_mesh_name=mesh.name, target_mesh_uid=str(mesh.session_uid),
                                                 target_captured=True) == {'FINISHED'}
        assert abs(bpy.context.active_object.location.x - 3) < .001
        assert mesh.parent is None and not mesh.vertex_groups
        before = set(bpy.data.objects.keys())
        assert refused(relative_asset_identifier=identifier, target_captured=True,
                       target_mesh_name=mesh.name, target_mesh_uid='deleted-or-replaced')
        assert set(bpy.data.objects.keys()) == before

        # Redo shows tuning controls, not the already-resolved dependency question.
        drawn = []
        redo = SimpleNamespace(relative_asset_identifier=identifier, _dependency_prompt=False,
                               layout=SimpleNamespace(prop=lambda op, name: drawn.append(name)))
        ops.BONEFORGE_OT_add_starter_asset.draw(redo, bpy.context)
        assert drawn == ['fit_to_active_mesh', 'parent_with_auto_weights', 'generate_control_rig']

        # Dragging is inert until a release in the viewport, and Esc cancels cleanly.
        events = []
        area = SimpleNamespace(type='VIEW_3D', header_text_set=lambda text: events.append(text))
        drag = SimpleNamespace(relative_asset_identifier=identifier, target_mesh=None)
        dragctx = SimpleNamespace(active_object=None, area=area,
                                  window_manager=SimpleNamespace(modal_handler_add=lambda op: None))
        before = set(bpy.data.objects.keys())
        assert ops.BONEFORGE_OT_drag_starter_asset.invoke(drag, dragctx, None) == {'RUNNING_MODAL'}
        drag._clear = lambda: ops.BONEFORGE_OT_drag_starter_asset._clear(drag)
        assert ops.BONEFORGE_OT_drag_starter_asset.modal(drag, dragctx, SimpleNamespace(type='ESC')) == {'CANCELLED'}
        assert events[-1] is None and set(bpy.data.objects.keys()) == before
        print('PASS starter shelf: complete generators; Basic independence; dependency prompt/failure; repeat, fit, drag cancel')
    finally:
        ra.unregister()
        qh.unregister()
    assert not hasattr(bpy.types, 'BONEFORGE_OT_add_starter_asset')
    assert ops.draw_starter_header not in bpy.types.VIEW3D_HT_header.draw._draw_funcs
    if native:
        assert native.__dict__['poll'] is native_poll
        assert native.__dict__['asset_poll'] is native_asset_poll
