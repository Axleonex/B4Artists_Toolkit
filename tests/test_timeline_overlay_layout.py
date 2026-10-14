"""Pure layout boundaries; no bpy import or simulated operator success."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
catalogue = ast.parse((ROOT/'anim_assist/ui/timeline_catalog.py').read_text())
values = {}
for node in catalogue.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in {'ACTIONS', 'QUICK_LABELS', 'GROUPS', 'DEFAULT_QUICK_ACTIONS'}:
                values[target.id] = ast.literal_eval(node.value)
module = ast.parse((ROOT/'anim_assist/ui/timeline_overlay.py').read_text())
function = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == 'row_layout')
exec(compile(ast.Module(body=[function], type_ignores=[]), '<row_layout>', 'exec'), values)
layout = values['row_layout']


class TimelineLayoutTests(unittest.TestCase):
    def clusters(self, all_actions=False):
        chosen = set(values['ACTIONS'] if all_actions else values['DEFAULT_QUICK_ACTIONS'])
        return [(key, label, [a for a in actions if a in chosen])
                for key, label, actions in values['GROUPS']]

    def test_bounds_and_no_overlap(self):
        for scale in (1, 1.5, 2):
            for width in (250, 400, 700, 900, 1200, 1920):
                for top in (True, False):
                    for all_actions in (True, False):
                        with self.subTest(scale=scale, width=width, top=top, all=all_actions):
                            controls = layout(width, 120*scale, 26*scale, top,
                                              self.clusters(all_actions), lambda s: len(s)*6*scale)
                            previous_end = 0
                            for _kind, _key, _label, (x,y,w,h) in controls:
                                self.assertGreaterEqual(x, previous_end)
                                self.assertLessEqual(x+w, width)
                                self.assertGreaterEqual(y, 0)
                                self.assertLessEqual(y+h, 120*scale)
                                previous_end = x+w
                            self.assertIn('SEARCH', [c[0] for c in controls])
                            self.assertIn('SETTINGS', [c[0] for c in controls])

    def test_wide_keeps_default_direct_tools_and_families(self):
        controls = layout(1920, 120, 26, False, self.clusters(), lambda s: len(s)*6)
        self.assertEqual({c[1] for c in controls if c[0]=='ACTION'}, set(values['DEFAULT_QUICK_ACTIONS']))
        self.assertEqual([c[1] for c in controls if c[0]=='MENU'], [g[0] for g in values['GROUPS']])

    def test_narrow_uses_tools_menu(self):
        controls = layout(250, 120, 26, False, self.clusters(), lambda s: len(s)*6)
        self.assertEqual([c[0] for c in controls[:2]], ['SEARCH','SETTINGS'])
        self.assertEqual(controls[-1][0], 'MORE')
        self.assertIn('B25', [c[1] for c in controls if c[0]=='ACTION'])

    def test_all_pins_keep_overflow_reachable(self):
        controls = layout(1200, 120, 26, False, self.clusters(True), lambda s: len(s)*6)
        self.assertEqual(controls[-1][0], 'MORE')


if __name__ == '__main__':
    unittest.main()
