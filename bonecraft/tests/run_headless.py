"""Run BoneForge BFA behavioural tests inside Bforartists (background).

Usage:
    bforartists --background --python tests/run_headless.py
Exits non-zero on failure so it can gate CI / a build loop.
"""
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))   # tests/
ROOT = os.path.dirname(HERE)                         # repo root
for p in (ROOT, HERE):                               # boneforge + test modules
    if p not in sys.path:
        sys.path.insert(0, p)


def main():
    import test_rig_build
    test_rig_build.run()
    print("\nALL IN-HOST RIG TESTS PASS")

    import test_control_layer
    test_control_layer.run()

    import test_face
    test_face.run()

    import test_retarget
    test_retarget.run()

    import test_picker
    test_picker.run()

    import test_detection
    test_detection.run()

    import test_export
    test_export.run()

    import test_rig_integrate_host
    test_rig_integrate_host.run()

    import test_skin_host
    test_skin_host.run()

    import test_twist_host
    test_twist_host.run()

    import test_retarget_ui_host
    test_retarget_ui_host.run()

    import test_stretch_host
    test_stretch_host.run()

    import test_face_markers_host
    test_face_markers_host.run()

    import test_volume_host
    test_volume_host.run()

    import test_correctives_host
    test_correctives_host.run()

    import test_face_controls_host
    test_face_controls_host.run()

    import test_garment_host
    test_garment_host.run()

    import test_dense_skin_host
    test_dense_skin_host.run()

    import test_skirt_host
    test_skirt_host.run()

    import test_sidebar_layout_host
    test_sidebar_layout_host.run()

    import test_rig_builder_placement_host
    test_rig_builder_placement_host.run()

    import test_rb_compact_draw_host
    test_rb_compact_draw_host.run()

    import test_dropped_rig_host
    test_dropped_rig_host.run()

    import test_quick_rigs_asset_host
    test_quick_rigs_asset_host.run()

    import test_rig_assets_host
    test_rig_assets_host.run()

    import test_scene_tab_host
    test_scene_tab_host.run()

    import test_tab_switches_host
    test_tab_switches_host.run()

    import test_mech_host_api
    test_mech_host_api.run()

    import test_mech_rig_ops_host
    test_mech_rig_ops_host.run()

    import test_mech_records_host
    test_mech_records_host.run()

    import test_mech_build_host
    test_mech_build_host.run()

    import test_mech_parts_host
    test_mech_parts_host.run()

    import test_mech_ops_host
    test_mech_ops_host.run()

    import test_mech_test_host
    test_mech_test_host.run()

    import test_mech_guide_host
    test_mech_guide_host.run()

    import test_mech_ui_host
    test_mech_ui_host.run()

    import test_mech_validate_host
    test_mech_validate_host.run()

    import test_mech_keep_objects_host
    test_mech_keep_objects_host.run()

    import test_show_helpers_host
    test_show_helpers_host.run()

    import test_tab_sides_host
    test_tab_sides_host.run()

    import test_wizard_done_host
    test_wizard_done_host.run()

    import test_ui_fixes_host
    test_ui_fixes_host.run()

    import test_needs_host
    test_needs_host.run()

    import test_wrap_button_host
    test_wrap_button_host.run()

    import test_wrap_layout_host
    test_wrap_layout_host.run()

    import test_ui_access_host
    test_ui_access_host.run()

    import test_operate_adjust_host
    test_operate_adjust_host.run()

    import test_action_first_host
    test_action_first_host.run()

    import test_gesture_tools_host
    test_gesture_tools_host.run()

    import test_tooltips_host
    test_tooltips_host.run()

    import test_ui_icons_host
    test_ui_icons_host.run()

    import test_icon_meaning_host
    test_icon_meaning_host.run()

    import test_scene_switch_host
    test_scene_switch_host.run()

    import test_taskboard_health_host
    test_taskboard_health_host.run()

    import test_crescent_rose_host       # last: it opens another .blend
    test_crescent_rose_host.run()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
