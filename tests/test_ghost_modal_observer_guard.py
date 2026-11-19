"""Execute the production guard AST; retain unknown/native modal protection."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'ghost_tool' / 'utils.py'
node=next(n for n in ast.parse(SOURCE.read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name=='is_native_transform_active')
namespace={}
exec(compile(ast.Module(body=[node],type_ignores=[]),str(SOURCE),'exec'),namespace)
guard=namespace['is_native_transform_active']

def context(*windows):
    return NS(window_manager=NS(windows=[NS(modal_operators=[NS(bl_idname=name) for name in operators]) for operators in windows]))

class ObserverGuard(unittest.TestCase):
    def test_idle_anim_assist_pointer_is_not_an_animation_gesture(self):
        for name in ('ANIMASSIST_OT_timeline_pointer',):
            with self.subTest(operator=name):
                self.assertFalse(guard(context([name])))

    def test_active_editing_modals_remain_blocked_alongside_pointer(self):
        for name in ('animassist.timeline_pointer','TRANSFORM_OT_translate','TRANSFORM_OT_rotate','TRANSFORM_OT_resize',
                     'GIZMOGROUP_OT_gizmo_tweak','ANIM_OT_change_frame','POSE_OT_push',
                     'ANIMASSIST_OT_timeline_slider','animassist.timeline_slider',
                     'ANIMASSIST_OT_blend_frame','ANIMASSIST_OT_anim_offset',
                     'SCREEN_OT_area_move','WM_OT_unknown','ANIMASSIST_OT_timeline_pointer_extra',
                     'animassist.timeline_pointer_extra'):
            with self.subTest(operator=name):
                self.assertTrue(guard(context(['ANIMASSIST_OT_timeline_pointer',name])))
                self.assertTrue(guard(context(['ANIMASSIST_OT_timeline_pointer'],[name])))

    def test_existing_ghost_gestures_still_use_their_separate_guard(self):
        for name in ('GHOSTTOOL_OT_hover','GHOST_TOOL_OT_pick_marker','ghost_tool.pick_marker'):
            with self.subTest(operator=name):
                self.assertFalse(guard(context([name])))

    def test_no_modal_is_idle(self):
        self.assertFalse(guard(context([])))

if __name__=='__main__':unittest.main(verbosity=2)
