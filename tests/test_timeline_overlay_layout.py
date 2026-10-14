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
import copy
import importlib.util
spec=importlib.util.spec_from_file_location('config',ROOT/'anim_assist/ui/timeline_config.py')
config=importlib.util.module_from_spec(spec); spec.loader.exec_module(config)
layout=config.toolbar_layout



class TimelineLayoutTests(unittest.TestCase):
    def controls(self,width,scale=1,top=False,all_actions=False):
        record=config.recommended(values['ACTIONS'])
        if all_actions:
            for action,tool in record['active']['tools'].items():
                tool['mode']='INLINE' if action in config.SLIDERS else 'BUTTON'
        before=copy.deepcopy(record)
        result=layout(width,120*scale,28*scale,top,record,values['GROUPS'],values['QUICK_LABELS'],lambda text:len(text)*6*scale)
        self.assertEqual(record,before)
        return result

    def test_bounds_and_no_overlap(self):
        for scale in (1,1.5,2):
            for width in (250,480,800,1164,1920):
                for top in (True,False):
                    for all_actions in (True,False):
                        controls=self.controls(width,scale,top,all_actions)
                        previous=0
                        for kind,key,label,(x,y,w,h) in controls:
                            self.assertGreaterEqual(x,previous)
                            self.assertLessEqual(x+w,width)
                            self.assertGreaterEqual(y,0)
                            self.assertLessEqual(y+h,120*scale)
                            previous=x+w
                        self.assertEqual([c[0] for c in controls[-3:]],['SEARCH','MORE','SETTINGS'])

    def test_wide_defaults_and_order(self):
        controls=self.controls(1920)
        self.assertEqual([c[1] for c in controls if c[0]=='MENU'],list(config.FAMILY_ORDER))
        self.assertEqual({c[1] for c in controls if c[0]=='SLIDER'},{'DRAG','SMOOTH'})
        self.assertIn('SCALE_DRAG',[c[1] for c in controls if c[0]=='POPOUT'])
        self.assertEqual([c[0] for c in controls[-3:]],['SEARCH','MORE','SETTINGS'])

    def test_narrow_quick_tools_and_more(self):
        controls=self.controls(250)
        self.assertIn('B25',[c[1] for c in controls])
        self.assertIn('MORE',[c[0] for c in controls])
        self.assertNotIn('SLIDER',[c[0] for c in controls])

    def test_all_tools_have_overflow_access(self):
        controls=self.controls(800,all_actions=True)
        self.assertIn('MORE',[c[0] for c in controls])
        self.assertLess(len([c for c in controls if c[0] in {'ACTION','SLIDER','POPOUT'}]),89)

    def test_slider_parts(self):
        controls=self.controls(1920)
        for kind,key,label,rect in controls:
            if kind=='SLIDER':
                track,value,reset=config.slider_parts(rect,label,lambda text:len(text)*6,1)
                self.assertLessEqual(track[0]+track[2],value[0])
                self.assertLessEqual(value[0]+value[2],reset[0])
                self.assertLessEqual(reset[0]+reset[2],rect[0]+rect[2])

if __name__=='__main__': unittest.main()
