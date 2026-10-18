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
config.register_families(values['GROUPS'])
layout=config.toolbar_layout



class TimelineLayoutTests(unittest.TestCase):
    def controls(self,width,scale=1,top=False,all_actions=False,stage='ALL'):
        record=config.recommended(values['ACTIONS'])
        if all_actions:
            for action,tool in record['active']['tools'].items():
                tool['mode']='INLINE' if action in config.SLIDERS else 'BUTTON'
        before=copy.deepcopy(record)
        result=layout(width,120*scale,28*scale,top,record,values['GROUPS'],values['QUICK_LABELS'],
                      lambda text:len(text)*6*scale,stage)
        self.assertEqual(record,before)
        return result

    def test_bounds_and_no_overlap(self):
        for scale in (1,1.5,2):
            for width in (250,480,800,1164,1920):
                for top in (True,False):
                    for all_actions in (True,False):
                        for stage in config.STAGE_IDS:
                            controls=self.controls(width,scale,top,all_actions,stage)
                            previous=0
                            for kind,key,label,(x,y,w,h) in controls:
                                self.assertGreaterEqual(x,previous)
                                self.assertLessEqual(x+w,width)
                                self.assertGreaterEqual(y,0)
                                self.assertLessEqual(y+h,120*scale)
                                previous=x+w
                            self.assertEqual([c[0] for c in controls[-3:]],['SEARCH','MORE','SETTINGS'])
                            self.assertIn(controls[0][0],{'STAGE','STAGE_CYCLE'})

    def test_stage_filters_families_only(self):
        for stage,_label,families in config.STAGES:
            controls=self.controls(1920,stage=stage)
            menus=[c[1] for c in controls if c[0]=='MENU']
            self.assertEqual(menus,list(families and [f for f in config.FAMILY_ORDER if f in families]
                                        or config.FAMILY_ORDER))
            shown={c[1].split(':')[0] for c in controls if c[0] in {'ACTION','SLIDER','POPOUT','PRESET'}}
            groups={key:{a for a in actions if a} for key,_l,actions in values['GROUPS']}
            self.assertTrue(all(any(a in groups[f] for f in menus) for a in shown))

    def test_all_stage_matches_unstaged_toolbar(self):
        strip=lambda cs:[c for c in cs if c[0] not in {'STAGE','STAGE_CYCLE'}]
        tools=lambda cs:[(c[0],c[1]) for c in strip(cs)]
        self.assertEqual(tools(self.controls(1920)),tools(self.controls(1920,stage='ALL')))
        self.assertEqual([c[1] for c in self.controls(1920) if c[0]=='STAGE'],list(config.STAGE_IDS))

    def test_lead_never_depends_on_stage(self):
        # Switching stage at a fixed width must not swap tabs for the cycle
        # button (that would move controls under the cursor).
        for scale in (1,1.5,2):
            for width in range(250,1921,10):
                leads={self.controls(width,scale,stage=s)[0][:2] for s in config.STAGE_IDS}
                kinds={kind for kind,_key in leads}
                self.assertEqual(len(kinds),1,(scale,width,leads))
                if kinds=={'STAGE_CYCLE'}:
                    self.assertEqual({key for _k,key in leads},{'CYCLE'})

    def test_tabs_only_when_every_stage_fits_in_full(self):
        # "Tabs give way first": with tabs shown, no stage loses family menus
        # or demotes an inline slider.
        for width in range(250,1921,10):
            for stage,_label,families in config.STAGES:
                controls=self.controls(width,stage=stage)
                if controls[0][0]!='STAGE': continue
                expected=[f for f in config.FAMILY_ORDER if families is None or f in families]
                self.assertEqual([c[1] for c in controls if c[0]=='MENU'],expected,(width,stage))
                order,tools=config.stage_view(config.recommended(values['ACTIONS'])['active'],stage)
                inline={a for a in order if a in tools and isinstance(tools[a],dict) and tools[a].get('mode')=='INLINE'}
                self.assertEqual({c[1] for c in controls if c[0]=='SLIDER'},inline,(width,stage))

    def test_hidden_family_note(self):
        self.assertEqual(config.hidden_family_note('ALL','pose','Pose'),'')
        self.assertEqual(config.hidden_family_note('POLISH','pose','Pose'),'')
        self.assertEqual(config.hidden_family_note('BLOCK','pose','Pose'),
                         'Pose is hidden in the Block stage; choose All or Polish to see it.')
        for family in config.FAMILY_ORDER:
            owner=config.stage_for_family(family)
            self.assertIn(family,config.stage_families(owner))
            self.assertNotEqual(owner,'ALL')

    def test_narrow_band_cycles_stage(self):
        controls=self.controls(250,stage='POLISH')
        self.assertEqual(controls[0][:3],('STAGE_CYCLE','CYCLE','Polish'))

    def test_stage_cycle_wraps_and_tolerates_unknown(self):
        self.assertEqual(config.next_stage('DELIVER',1),'ALL')
        self.assertEqual(config.next_stage('ALL',-1),'DELIVER')
        self.assertEqual(config.next_stage('BOGUS',1),'BLOCK')
        self.assertEqual(config.stage_families('BOGUS'),config.FAMILY_ORDER)
        staged=[f for _k,_l,fs in config.STAGES if fs for f in fs]
        self.assertEqual(sorted(staged),sorted(config.FAMILY_ORDER))

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

    def test_spline_shows_its_defaults(self):
        controls=self.controls(1920,stage='SPLINE')
        shown=[c[1] for c in controls if c[0] in {'ACTION','SLIDER','POPOUT'}]
        expected=['REFERENCE','FRAME','NEIGHBORS','EASE','SMOOTH','AMPLIFY','HANDLE_CLAMPED','HANDLE_VECTOR','HANDLE_FREE']
        self.assertEqual(shown,expected[:len(shown)])
        self.assertTrue(len(shown)==len(expected) or 'MORE' in [c[0] for c in controls])

    def test_stage_independent_of_all_visibility(self):
        record=config.recommended(values['ACTIONS'])
        record['active']['tools']['SMOOTH']['mode']='HIDDEN'
        measure=lambda text:len(text)*6
        spline=layout(1920,120,28,False,record,values['GROUPS'],values['QUICK_LABELS'],measure,'SPLINE')
        everything=layout(1920,120,28,False,record,values['GROUPS'],values['QUICK_LABELS'],measure,'ALL')
        self.assertIn('SMOOTH',[c[1] for c in spline])
        self.assertNotIn('SMOOTH',[c[1] for c in everything])

    def test_all_output_unchanged_by_stages(self):
        record=config.recommended(values['ACTIONS'])
        config.set_stage_tool(record,'SPLINE','SMOOTH',mode='HIDDEN')
        config.set_stage_tool(record,'BLOCK','GROW_BOTH',mode='BUTTON')
        measure=lambda text:len(text)*6
        plain=config.recommended(values['ACTIONS'])
        for width in (480,1164,1920):
            a=layout(width,120,28,False,record,values['GROUPS'],values['QUICK_LABELS'],measure,'ALL')
            b=layout(width,120,28,False,plain,values['GROUPS'],values['QUICK_LABELS'],measure,'ALL')
            strip=lambda cs:[c for c in cs if c[0] not in {'STAGE','STAGE_CYCLE'}]
            self.assertEqual([c[:2] for c in strip(a)],[c[:2] for c in strip(b)])

if __name__=='__main__': unittest.main()
