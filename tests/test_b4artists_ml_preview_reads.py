"""Actual-host scoped preview reads: invalidation, isolation and existing guards."""
from pathlib import Path
import os,sys,json,copy,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import bpy
from b4artists_ml import body_preview as body,body_live as live,workflow as w
from test_b4artists_ml_body_live import LivePoseTests

class PreviewReadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):LivePoseTests.setUpClass();cls.helper=LivePoseTests()
    def tearDown(self):self.helper.tearDown()
    def fixture(self):return self.helper.fixture()
    def test_scope_lifetime_foreign_rig_and_independent_mutation(self):
        ob,*_=self.fixture();scope=body._ReadScope(ob)
        with scope:
            first=body._read(ob,_scope=scope);original=copy.deepcopy(first)
            session=body._get(ob,_scope=scope);body._request(ob,session,_scope=scope)
            self.assertIs(body._read(ob,_scope=scope),first);self.assertEqual(first,original)
            other=body._read(ob);self.assertIsNot(other,first);other['signature']={'changed':True}
            self.assertEqual(body._read(ob,_scope=scope),original)
            with self.assertRaises(ValueError):body._read(ob.b4ml.body_targets['Head'].target,_scope=scope)
        self.assertIsNone(scope.record);self.assertIsNone(scope.payload)
        with self.assertRaises(ValueError):body._read(ob,_scope=scope)
        with self.assertRaises(ValueError):scope.__enter__()
    def test_each_idle_tick_decodes_once_and_never_reuses_across_ticks(self):
        ob,*_=self.fixture();body.solve(ob);live.start(ob,now=0.)
        decoded=[];original=body._decode
        def spy(payload):
            record=original(payload);decoded.append(record);return record
        with patch.object(body,'_decode',spy):
            for i in range(5):self.assertEqual(live.tick(ob,now=(i+1)*.02),'idle')
        self.assertEqual(len(decoded),5);self.assertEqual(len({id(r) for r in decoded}),5)
        self.assertFalse(body._JOBS)
    def test_changed_invalid_and_reverted_payload_reparsed(self):
        ob,*_=self.fixture();original=ob.b4ml.body_payload
        try:
            with body._ReadScope(ob) as scope:
                first=body._read(ob,_scope=scope);changed=copy.deepcopy(first);changed['note']='new serialized state'
                ob.b4ml.body_payload=json.dumps(changed);second=body._read(ob,_scope=scope)
                self.assertIsNot(first,second);self.assertEqual(second['note'],'new serialized state');self.assertNotIn('note',first)
                ob.b4ml.body_payload='{'
                for _ in range(2):
                    with self.assertRaises(json.JSONDecodeError):body._read(ob,_scope=scope)
                ob.b4ml.body_payload=original
                self.assertEqual(body._read(ob,_scope=scope),first);self.assertNotIn('note',body._read(ob,_scope=scope))
        finally:ob.b4ml.body_payload=original
    def test_cached_payload_does_not_skip_live_session_validation(self):
        ob,*_=self.fixture();original=ob.matrix_world.copy()
        try:
            with body._ReadScope(ob) as scope:
                body._get(ob,_scope=scope)
                ob.location.x+=.01;bpy.context.view_layer.update()
                with self.assertRaisesRegex(ValueError,'transform changed'):body._get(ob,_scope=scope)
        finally:ob.matrix_world=original;bpy.context.view_layer.update()
    def test_unchanged_payload_still_reads_new_helper_intent(self):
        ob,*_=self.fixture();payload=ob.b4ml.body_payload
        with body._ReadScope(ob) as scope:
            session=body._get(ob,_scope=scope);first=body._request(ob,session,_scope=scope)[2]
            ob.b4ml.body_targets['Head'].target.location.y+=.002
            second=body._request(ob,session,_scope=scope)[2]
            self.assertNotEqual(first,second);self.assertEqual(ob.b4ml.body_payload,payload)
    def test_dependency_update_payload_mutation_stops_fit_and_restores_preview(self):
        ob,*_=self.fixture();body.solve(ob);before=w.raw_pose(ob);live.start(ob,now=0.)
        target=ob.b4ml.body_targets['Head'].target;target.location.y+=.002;bpy.context.view_layer.update()
        live.tick(ob,now=.02);self.assertEqual(live.tick(ob,now=.2),'solving')
        original=ob.b4ml.body_payload;fired=[]
        def mutate(*args):
            if not fired:
                fired.append(True);record=json.loads(original);record['schema']=2;ob.b4ml.body_payload=json.dumps(record)
        bpy.app.handlers.depsgraph_update_post.append(mutate)
        try:
            target.location.y+=.002
            with self.assertRaisesRegex(ValueError,'Unsupported whole-body preview record'):live.tick(ob,now=.22)
            self.assertTrue(fired);self.assertFalse(ob.b4ml.body_live);self.assertFalse(body._JOBS)
            self.assertEqual(w.raw_pose(ob),before)
        finally:
            bpy.app.handlers.depsgraph_update_post.remove(mutate);ob.b4ml.body_payload=original
    def test_completed_solve_never_mutates_borrowed_record(self):
        ob,*_=self.fixture();body.solve(ob)
        with body._ReadScope(ob) as scope:
            first=body._read(ob,_scope=scope);saved=copy.deepcopy(first)
            ob.b4ml.body_targets['Head'].target.location.y+=.002;body.solve(ob)
            self.assertEqual(first,saved)
            second=body._read(ob,_scope=scope);self.assertIsNot(first,second)
            self.assertNotEqual(second['signature'],first['signature']);self.assertNotEqual(second['preview'],first['preview'])
if __name__=='__main__':unittest.main()
