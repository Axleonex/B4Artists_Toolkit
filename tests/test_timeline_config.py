import ast
import copy
import json
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('timeline_config',ROOT/'anim_assist/ui/timeline_config.py')
config=importlib.util.module_from_spec(spec); spec.loader.exec_module(config)
tree=ast.parse((ROOT/'anim_assist/ui/timeline_catalog.py').read_text(encoding='utf-8'))
actions=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
             and any(isinstance(t,ast.Name) and t.id=='ACTIONS' for t in n.targets))
groups=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
            and any(isinstance(t,ast.Name) and t.id=='GROUPS' for t in n.targets))
config.register_families(groups)
family={a:k for k,_l,acts in groups for a in acts if a}


class ConfigTests(unittest.TestCase):
    def setUp(self): self.record=config.recommended(actions)

    def test_defaults(self):
        tools=self.record['active']['tools']
        self.assertEqual(len(tools),96)
        self.assertEqual({k for k,v in tools.items() if v['mode']=='INLINE'},{'DRAG','SMOOTH'})
        self.assertEqual(tools['SCALE_DRAG']['mode'],'POPOUT')
        self.assertEqual(len(config.SLIDERS),10)
        self.assertEqual(config.FAMILY_ORDER[:3],('tween','timing','curves'))

    def test_roundtrip(self):
        self.assertEqual(config.decode(config.encode(self.record,actions),actions),self.record)

    def test_invalid_modes(self):
        for action in ('COPY_KEYS','OFFSET','BAKE_STEP'):
            for mode in ('INLINE','POPOUT','invalid'):
                with self.assertRaises(ValueError): config.validate_tool(action,{'mode':mode})

    def test_invalid_numeric(self):
        for value in (float('nan'),float('inf'),True,'50'):
            with self.assertRaises(ValueError): config.validate_tool('DRAG',{'default':value})
        for fields in ({'range_min':100,'range_max':0},{'range_min':-101},
                       {'range_max':201},{'width':40},{'precision':2.5},{'snap_step':0}):
            with self.assertRaises(ValueError): config.validate_tool('DRAG',fields)
        with self.assertRaises(ValueError): config.validate_tool('SCALE_DRAG',{'range_min':0})

    def test_extended_ranges(self):
        self.assertEqual(config.validate_tool('SCALE_DRAG',{'range_max':500})['range_max'],500)
        self.assertEqual(config.validate_tool('SMOOTH',{'range_min':-100,'range_max':200})['range_min'],-100)

    def test_old_selection(self):
        for selected in (set(),{'B25','SMOOTH','OFFSET'}):
            old=config.from_legacy(actions,selected)
            self.assertEqual({k for k,v in old['active']['tools'].items() if v['mode']!='HIDDEN'},selected)
            self.assertEqual(config.decode(config.encode(old,actions),actions),old)

    def test_future_and_bad_records(self):
        before=copy.deepcopy(self.record)
        for raw in ('{}','not json','{"schema_version":3}','{"schema_version":true}'):
            with self.assertRaises(ValueError): config.decode(raw,actions)
        self.assertEqual(self.record,before)

    def test_unknown_records_preserved(self):
        self.record['active']['tools']['FUTURE_TOOL']={'special':42,'mode':'INLINE'}
        result=config.decode(config.encode(self.record,actions),actions)
        self.assertEqual(result['active']['tools']['FUTURE_TOOL'],{'special':42,'mode':'INLINE'})
        self.assertIn('FUTURE_TOOL',result['active']['order'])

    def test_library(self):
        config.save_as(self.record,' Blocking '); blocking=self.record['active_saved_id']
        self.record['active']['tools']['DRAG']['mode']='POPOUT'
        self.assertTrue(config.modified(self.record,actions))
        config.save_as(self.record,'Polish'); polish=self.record['active_saved_id']
        config.load(self.record,blocking,actions)
        self.assertEqual(self.record['active']['tools']['DRAG']['mode'],'INLINE')
        config.rename(self.record,blocking,'ブロック')
        self.assertEqual(self.record['active']['name'],'ブロック')
        config.delete(self.record,blocking)
        self.assertEqual(self.record['active']['name'],'Custom')
        config.load(self.record,'recommended',actions)
        self.assertEqual(len(self.record['saved']),1)
        self.assertEqual(self.record['saved'][0]['id'],polish)

    def test_name_errors_and_protected_defaults(self):
        config.save_as(self.record,'Blocking')
        for name in ('','   ','x'*65,'blocking','Recommended'):
            before=copy.deepcopy(self.record)
            with self.assertRaises(ValueError): config.save_as(self.record,name)
            self.assertEqual(before,self.record)
        for fn in (lambda:config.delete(self.record,'recommended'),
                   lambda:config.rename(self.record,'recommended','Other')):
            with self.assertRaises(ValueError): fn()

    def test_update_and_deep_copy(self):
        config.save_as(self.record,'One')
        self.record['active']['tools']['DRAG']['presets']=[25,50,75]
        self.assertEqual(self.record['saved'][0]['tools']['DRAG']['presets'],[])
        config.update_saved(self.record)
        self.assertFalse(config.modified(self.record,actions))

    def test_pointer_precision_snap(self):
        tool=config.tool_default('DRAG')
        self.assertEqual(config.value_from_pointer(tool,50,50),75)
        self.assertEqual(config.value_from_pointer(tool,50,50,precise=True),52.5)
        self.assertEqual(config.value_from_pointer(tool,50,10000),100)
        tool['snap_step']=25
        self.assertEqual(config.value_from_pointer(tool,50,60,snap=True),75)

    def test_stage_defaults_match_table(self):
        stages=self.record['active']['stages']
        self.assertEqual(stages['SPLINE']['order'],['TO_SPLINE','NEIGHBORS','EASE','SMOOTH','REFERENCE','FRAME',
                                                    'AMPLIFY','HANDLE_CLAMPED','HANDLE_VECTOR','HANDLE_FREE',
                                                    'TRAIL_TOGGLE'])
        self.assertEqual(stages['BLOCK']['order'][0],'DRAG')
        self.assertNotIn('B25',stages['BLOCK']['order']); self.assertNotIn('PUSH_PREV',stages['BLOCK']['order'])
        self.assertNotIn('T80',stages['POLISH']['order'])
        self.assertEqual(stages['BLOCK']['tools']['DRAG']['presets'],[-25.,25.,50.,75.,125.])
        self.assertEqual(stages['POLISH']['tools']['SCALE_DRAG'],{'mode':'INLINE','label_mode':'LABEL','presets':[80.,90.,110.,120.]})
        self.assertEqual(stages['SPLINE']['tools']['FRAME'],{'mode':'POPOUT','label_mode':'LABEL'})
        self.assertEqual(stages['BLOCK']['tools']['DRAG']['mode'],'INLINE')
        self.assertEqual(stages['POLISH']['tools']['OFFSET_DRAG']['mode'],'INLINE')
        self.assertEqual(stages['DELIVER']['order'],['BAKE_STEP','BAKE_PREVIEW','SMART_BAKE','REDUCE','BAKE_INTEGER',
            'PROXY_BAKE','PROXY_TRANSLATION','PROXY_ORIENTATION','PROXY_WORLD','PROXY_PARENT','BAKE_CLEANUP',
            'CLEANUP_ALL'])
        self.assertEqual(config.stage_families('SPLINE'),('curves','motion'))
        self.assertEqual(config.stage_families('DELIVER'),('bake',))
        for stage in config.STAGE_KEYS:
            allowed=set(config.stage_families(stage))
            self.assertTrue(all(family[a] in allowed for a in stages[stage]['order']),stage)
            self.assertEqual(stages[stage],config.stage_default(stage))

    def test_v1_migration_keeps_library(self):
        old=copy.deepcopy(self.record); old['schema_version']=1
        old['active'].pop('stages')
        saved=copy.deepcopy(old['active']); saved.update(id='abc',name='Blocking')
        saved['tools']['DRAG']['mode']='POPOUT'; old['saved']=[saved]; old['active_saved_id']='abc'
        result=config.decode(json.dumps(old),actions)
        self.assertEqual(result['schema_version'],2)
        self.assertEqual(result['active_saved_id'],'abc')
        self.assertEqual(result['saved'][0]['name'],'Blocking')
        self.assertEqual(result['saved'][0]['tools']['DRAG']['mode'],'POPOUT')
        self.assertEqual(result['saved'][0]['stages']['BLOCK'],config.stage_default('BLOCK'))
        self.assertEqual(result['active']['tools'],self.record['active']['tools'])

    def test_invalid_stage_rejected(self):
        bad=[('BLOCK',{'order':['B25','B25'],'tools':{'B25':{'mode':'BUTTON'}}}),
             ('BLOCK',{'order':['B25'],'tools':{'B25':{'mode':'INLINE'}}}),
             ('SPLINE',{'order':[],'tools':{'SMOOTH':{'mode':'INLINE'}}})]
        for stage,setup in bad:
            record=copy.deepcopy(self.record); record['active']['stages'][stage]=setup
            with self.assertRaises(ValueError,msg=(stage,setup)): config.validate(record,actions)

    def test_tool_from_a_moved_family_is_dropped(self):
        # A Deliver setup saved while Motion belonged to Deliver still loads; the trail tool is dropped.
        record=copy.deepcopy(self.record)
        record['active']['stages']['DELIVER']={'order':['BAKE_STEP','TRAIL_SHOW'],
            'tools':{'BAKE_STEP':{'mode':'BUTTON'},'TRAIL_SHOW':{'mode':'BUTTON'}}}
        result=config.validate(record,actions)
        self.assertEqual(result['active']['stages']['DELIVER']['order'],['BAKE_STEP'])

    def test_stage_roundtrip_and_modified(self):
        self.assertEqual(config.decode(config.encode(self.record,actions),actions),self.record)
        self.assertFalse(config.modified(self.record,actions))
        config.set_stage_tool(self.record,'SPLINE','SMOOTH',mode='HIDDEN')
        self.assertNotIn('SMOOTH',self.record['active']['stages']['SPLINE']['order'])
        self.assertTrue(config.modified(self.record,actions))
        self.assertEqual(config.decode(config.encode(self.record,actions),actions),self.record)

    def test_reset_stage_only_current(self):
        config.set_stage_tool(self.record,'BLOCK','INBETWEEN',mode='HIDDEN')
        config.set_stage_tool(self.record,'POLISH','SNAP',mode='HIDDEN')
        config.reset_stage(self.record,'BLOCK')
        stages=self.record['active']['stages']
        self.assertEqual(stages['BLOCK'],config.stage_default('BLOCK'))
        self.assertNotIn('SNAP',stages['POLISH']['order'])
        config.load(self.record,'recommended',actions)
        self.assertEqual(self.record['active']['stages']['POLISH'],config.stage_default('POLISH'))

    def test_set_stage_tool_show_hide(self):
        config.set_stage_tool(self.record,'BLOCK','INBETWEEN',mode='HIDDEN')
        config.set_stage_tool(self.record,'BLOCK','INBETWEEN',mode='BUTTON')
        order=self.record['active']['stages']['BLOCK']['order']
        self.assertEqual([a for a in order if family[a]=='tween'][-1],'INBETWEEN')
        self.assertLess(order.index('INBETWEEN'),order.index('RANGE'))
        config.set_stage_tool(self.record,'BLOCK','GROW_BOTH',mode='BUTTON')
        self.assertEqual([a for a in order if family[a]=='keys'][-1],'GROW_BOTH')
        config.set_stage_tool(self.record,'ALL','DRAG',mode='HIDDEN')
        self.assertEqual(self.record['active']['tools']['DRAG']['mode'],'HIDDEN')
        self.assertIn('DRAG',order)

    def test_pin_target(self):
        self.assertEqual(config.pin_target('BLOCK','BAKE_STEP'),'ALL')
        self.assertEqual(config.pin_target('BLOCK','INBETWEEN'),'BLOCK')
        self.assertEqual(config.pin_target('ALL','INBETWEEN'),'ALL')

    def test_entries_round_trip_per_stage(self):
        entries=config.stage_entries(self.record,'BLOCK',actions)
        self.assertEqual({family[e['action']] for e in entries},{'tween','keys'})
        self.assertEqual([e['action'] for e in entries][:3],['DRAG','INBETWEEN','INBETWEENS'])
        by={e['action']:e for e in entries}
        hold=entries.pop([e['action'] for e in entries].index('TYPE_HOLD'))
        entries.insert([e['action'] for e in entries].index('RANGE'),hold)
        by['INBETWEEN']['mode']='HIDDEN'; by['DRAG']['width']=150.
        before_all=copy.deepcopy(self.record['active']['order'])
        polish=copy.deepcopy(self.record['active']['stages']['POLISH'])
        config.apply_entries(self.record,'BLOCK',entries,actions)
        order=self.record['active']['stages']['BLOCK']['order']
        self.assertLess(order.index('TYPE_HOLD'),order.index('RANGE'))
        self.assertNotIn('INBETWEEN',order)
        self.assertEqual(self.record['active']['tools']['DRAG']['width'],150.)
        self.assertEqual(self.record['active']['order'],before_all)
        self.assertEqual(self.record['active']['stages']['POLISH'],polish)
        self.assertEqual(len(config.stage_entries(self.record,'ALL',actions)),96)
        config.validate(self.record,actions)

    def test_future_stage_tools_survive_settings(self):
        self.record['active']['tools']['FUTURE']={'mode':'BUTTON'}
        self.record['active']['stages']['BLOCK']['order'].append('FUTURE')
        self.record['active']['stages']['BLOCK']['tools']['FUTURE']={'mode':'BUTTON','extra':1}
        record=config.validate(self.record,actions)
        config.apply_entries(record,'BLOCK',config.stage_entries(record,'BLOCK',actions),actions)
        self.assertIn('FUTURE',record['active']['stages']['BLOCK']['order'])
        self.assertEqual(record['active']['stages']['BLOCK']['tools']['FUTURE'],{'mode':'BUTTON','extra':1})

    def test_malformed_unknown_stage_tool_rejected(self):
        for setup in ({'order':['FUTURE'],'tools':{'FUTURE':[1]}},{'order':[],'tools':{'FUTURE':'x'}}):
            record=copy.deepcopy(self.record); record['active']['stages']['BLOCK']=setup
            with self.assertRaises(ValueError): config.validate(record,actions)

    def test_hundred_layouts_fit(self):
        for index in range(100):
            config.save_as(self.record,f'Layout {index}')
        self.assertLessEqual(len(config.encode(self.record,actions)),config.RECORD_LIMIT)


class TooltipWrapTests(unittest.TestCase):
    measure = staticmethod(lambda text: 6 * len(text))

    def test_wrap_keeps_every_word_within_width(self):
        text = 'Bake the active object world motion to keys through a temporary translation proxy ' * 4
        lines = config.wrap_to_width(text, 120, self.measure)
        self.assertEqual(' '.join(lines).split(), text.split())
        self.assertTrue(all(self.measure(line) <= 120 for line in lines))

    def test_wrap_splits_a_word_wider_than_the_line(self):
        lines = config.wrap_to_width('x' * 50, 60, self.measure)
        self.assertEqual(''.join(lines), 'x' * 50)
        self.assertTrue(all(len(line) <= 10 for line in lines))

    def test_fit_keeps_all_lines_when_they_fit(self):
        paragraphs = [('Title', 'TITLE'), ('word ' * 60, 'BODY'), ('Works on: things.', 'DETAIL'),
                      ('Unavailable: select an object.', 'WARNING')]
        lines, width, height = config.fit_tooltip(paragraphs, 1600, 220, self.measure, 1, 15, 7, 420)
        self.assertEqual(' '.join(l for l, _ in lines).split(), ' '.join(t for t, _ in paragraphs).split())
        self.assertLessEqual(height, 220)
        self.assertLessEqual(width, 420)
        self.assertIn('WARNING', [r for _, r in lines])

    def test_fit_widens_before_dropping_details(self):
        paragraphs = [('Title', 'TITLE'), ('word ' * 120, 'BODY'), ('Also in Bake > Tool.', 'DETAIL')]
        lines, width, height = config.fit_tooltip(paragraphs, 1600, 120, self.measure, 1, 15, 7, 420)
        self.assertGreater(width, 420)
        self.assertLessEqual(height, 120)
        self.assertIn('DETAIL', [r for _, r in lines])

    def test_fit_drops_only_details_in_a_tiny_region(self):
        paragraphs = [('Title', 'TITLE'), ('Body text here.', 'BODY'), ('Unavailable: why.', 'WARNING'),
                      ('Detail one.', 'DETAIL'), ('Detail two.', 'DETAIL')]
        lines, _w, _h = config.fit_tooltip(paragraphs, 400, 60, self.measure, 1, 15, 7, 420)
        roles = [r for _, r in lines]
        self.assertEqual(roles[:3], ['TITLE', 'BODY', 'WARNING'])


class IconTests(unittest.TestCase):
    def setUp(self):
        self.record = config.recommended(actions)

    def test_block_key_types_default_to_icons(self):
        block = self.record['active']['stages']['BLOCK']['tools']
        for action in ('TYPE_KEYFRAME', 'TYPE_BREAKDOWN', 'TYPE_EXTREME', 'TYPE_HOLD'):
            self.assertEqual(block[action]['label_mode'], 'ICON')
        self.assertEqual(block['INBETWEEN']['label_mode'], 'LABEL')
        self.assertEqual(self.record['active']['tools']['TYPE_KEYFRAME']['label_mode'], 'LABEL')

    def test_icon_only_for_tools_that_have_one(self):
        self.assertTrue(config.has_icon('TYPE_BREAKDOWN'))
        self.assertTrue(config.has_icon('NUDGE_LEFT'))
        self.assertFalse(config.has_icon('SMOOTH'))
        self.assertFalse(config.has_icon('BAKE_STEP'))
        config.set_stage_tool(self.record, 'SPLINE', 'SMOOTH', label_mode='ICON')
        self.assertEqual(self.record['active']['stages']['SPLINE']['tools']['SMOOTH']['label_mode'], 'LABEL')
        config.set_stage_tool(self.record, 'ALL', 'BAKE_STEP', label_mode='ICON')
        self.assertEqual(self.record['active']['tools']['BAKE_STEP']['label_mode'], 'LABEL')

    def test_older_icon_setting_on_a_tool_without_one_loads_as_label(self):
        record = copy.deepcopy(self.record)
        record['active']['tools']['SMOOTH']['label_mode'] = 'ICON'
        record['active']['stages']['SPLINE']['tools']['EASE']['label_mode'] = 'ICON'
        result = config.validate(record, actions)
        self.assertEqual(result['active']['tools']['SMOOTH']['label_mode'], 'LABEL')
        self.assertEqual(result['active']['stages']['SPLINE']['tools']['EASE']['label_mode'], 'LABEL')

    def test_block_icons_are_narrow_unlabelled_buttons(self):
        controls = config.toolbar_layout(1920, 120, 28, False, self.record, groups, {},
                                         lambda text: len(text) * 6, 'BLOCK')
        icons = [c for c in controls if c[1] in config.KEY_TYPE_ICONS]
        self.assertEqual(len(icons), 4)
        self.assertTrue(all(c[2] == '' and c[3][2] == 24 for c in icons))


class StagePresetTests(unittest.TestCase):
    def setUp(self):
        self.record = config.recommended(actions)

    def test_all_keeps_tool_presets_and_stage_shows_its_own(self):
        self.assertEqual(self.record['active']['tools']['DRAG']['presets'], [])
        all_tools = config.stage_view(self.record['active'], 'ALL')[1]
        block_tools = config.stage_view(self.record['active'], 'BLOCK')[1]
        self.assertEqual(all_tools['DRAG']['presets'], [])
        self.assertEqual(block_tools['DRAG']['presets'], [-25., 25., 50., 75., 125.])

    def test_block_row_shows_breakdown_presets_and_all_row_does_not(self):
        measure = lambda text: len(text) * 6
        block = config.toolbar_layout(1920, 120, 28, False, self.record, groups, {}, measure, 'BLOCK')
        all_row = config.toolbar_layout(1920, 120, 28, False, self.record, groups, {}, measure, 'ALL')
        self.assertEqual([c[2] for c in block if c[0] == 'PRESET'], ['-25', '25', '50', '75', '125'])
        self.assertFalse([c for c in all_row if c[0] == 'PRESET'])

    def test_stage_presets_go_past_the_display_range_within_tool_limits(self):
        self.assertEqual(config.stage_presets('DRAG', [-25, 125]), [-25., 125.])
        with self.assertRaises(ValueError): config.stage_presets('DRAG', [250])
        with self.assertRaises(ValueError): config.stage_presets('DRAG', list(range(13)))
        with self.assertRaises(ValueError): config.stage_presets('B25', [10])

    def test_presets_survive_mode_changes_and_round_trip(self):
        config.set_stage_tool(self.record, 'BLOCK', 'DRAG', mode='POPOUT')
        self.assertEqual(self.record['active']['stages']['BLOCK']['tools']['DRAG']['presets'], [-25., 25., 50., 75., 125.])
        config.set_stage_tool(self.record, 'BLOCK', 'DRAG', presets=[10, 90])
        decoded = config.decode(config.encode(self.record, actions), actions)
        self.assertEqual(decoded['active']['stages']['BLOCK']['tools']['DRAG']['presets'], [10., 90.])
        entries = config.stage_entries(self.record, 'BLOCK', actions)
        config.apply_entries(self.record, 'BLOCK', entries, actions)
        self.assertEqual(self.record['active']['stages']['BLOCK']['tools']['DRAG']['presets'], [10., 90.])

    def test_version_b_icons(self):
        icons = {stage: {a for a, t in self.record['active']['stages'][stage]['tools'].items() if t['label_mode'] == 'ICON'}
                 for stage in config.STAGE_KEYS}
        self.assertEqual(icons['SPLINE'], {'TO_SPLINE', 'HANDLE_CLAMPED', 'HANDLE_VECTOR', 'HANDLE_FREE', 'TRAIL_TOGGLE'})
        self.assertEqual(icons['POLISH'], {'NUDGE_LEFT', 'NUDGE_RIGHT'})
        self.assertTrue({'GROW_LEFT', 'GROW_RIGHT', 'COPY_KEYS', 'PASTE_KEYS', 'TYPE_KEYFRAME'} <= icons['BLOCK'])
        self.assertEqual(icons['DELIVER'], set())


class ReduceRippleTests(unittest.TestCase):
    def test_defaults(self):
        record = config.recommended(actions)
        stages = record['active']['stages']
        self.assertEqual(stages['POLISH']['tools']['RIPPLE'], {'mode': 'INLINE', 'label_mode': 'LABEL', 'presets': [-1., 1.]})
        self.assertEqual(stages['DELIVER']['tools']['REDUCE'], {'mode': 'INLINE', 'label_mode': 'LABEL', 'presets': [.001, .01, .05]})
        self.assertEqual(record['active']['tools']['REDUCE']['precision'], 3)
        self.assertEqual(record['active']['tools']['RIPPLE']['precision'], 1)
        self.assertEqual(record['active']['tools']['REDUCE']['mode'], 'HIDDEN')
        self.assertEqual(record['active']['tools']['RIPPLE']['mode'], 'HIDDEN')

    def test_older_button_records_still_load(self):
        record = config.recommended(actions)
        record['active']['tools']['REDUCE'] = {'action': 'REDUCE', 'mode': 'BUTTON', 'label_mode': 'LABEL', 'width': 120.}
        result = config.validate(record, actions)
        self.assertEqual(result['active']['tools']['REDUCE']['mode'], 'BUTTON')
        self.assertEqual(result['active']['tools']['REDUCE']['range_max'], .1)


if __name__=='__main__': unittest.main()
