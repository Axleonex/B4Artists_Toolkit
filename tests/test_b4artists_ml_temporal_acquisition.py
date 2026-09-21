"""Bounded acquisition and immutable confirmation ownership, no real network."""
import sys,unittest,tempfile,json,hashlib,io
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'training/b4artists_ml'))
import fetch_cmu_temporal_v8 as fetcher
class Reply(io.BytesIO):
 def __init__(self,payload,length=None):super().__init__(payload);self.headers={'Content-Length':str(len(payload) if length is None else length)}
class AcquisitionTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);(self.root/'cache').mkdir();self.patch=patch.object(fetcher,'ROOT',self.root);self.patch.start()
  self.plan=dict(planned_splits={'train':['90_02'],'validation':['118_01'],'confirmation':['143_02']},max_additional_bytes=1000,max_file_bytes=500,provenance='test fixture');self.write_plan()
 def tearDown(self):self.patch.stop();self.temp.cleanup()
 def write_plan(self):(self.root/'temporal_expansion_plan_v8.json').write_text(json.dumps(self.plan))
 def response(self,url,timeout):return Reply(b'HIERARCHY '+url.encode())
 def frozen(self):
  (self.root/'model.npz').write_bytes(b'model');p=self.root/'selection.json';p.write_text(json.dumps(dict(confirmation_loaded=False,plan_sha256=fetcher.sha(self.root/'temporal_expansion_plan_v8.json'),model_files={'model.npz':fetcher.sha(self.root/'model.npz')})));return p
 def test_confirmation_is_not_requested_without_frozen_model(self):
  with patch.object(fetcher.urllib.request,'urlopen',side_effect=self.response) as get:r=fetcher.fetch()
  self.assertEqual(get.call_count,2);self.assertEqual({v['split'] for v in r['files']},{'train','validation'});self.assertFalse((self.root/'cache/143_02.bvh').exists())
 def test_model_change_blocks_confirmation_before_network(self):
  p=self.frozen();(self.root/'model.npz').write_bytes(b'changed')
  with patch.object(fetcher.urllib.request,'urlopen') as get:
   with self.assertRaises(AssertionError):fetcher.fetch(p)
   get.assert_not_called()
 def test_confirmation_is_bound_to_first_selection(self):
  p=self.frozen()
  with patch.object(fetcher.urllib.request,'urlopen',side_effect=self.response):r=fetcher.fetch(p)
  self.assertEqual(r['confirmation_selection_sha256'],fetcher.sha(p));other=self.root/'other.json';d=json.loads(p.read_text());d['different_selection']=True;other.write_text(json.dumps(d))
  with patch.object(fetcher.urllib.request,'urlopen') as get:
   with self.assertRaisesRegex(ValueError,'another frozen selection'):fetcher.fetch(other)
   get.assert_not_called()
 def test_content_length_over_budget_refused_without_cache_write(self):
  with patch.object(fetcher.urllib.request,'urlopen',return_value=Reply(b'HIERARCHY',501)):
   with self.assertRaisesRegex(ValueError,'byte cap'):fetcher.fetch()
  self.assertEqual(list((self.root/'cache').iterdir()),[])
 def test_existing_unrecorded_clip_is_not_claimed_untouched(self):
  (self.root/'cache/90_02.bvh').write_bytes(b'HIERARCHY existing')
  with patch.object(fetcher.urllib.request,'urlopen') as get:
   with self.assertRaisesRegex(ValueError,'Unrecorded'):fetcher.fetch()
   get.assert_not_called()
 def test_duplicate_content_across_partitions_rejected(self):
  with patch.object(fetcher.urllib.request,'urlopen',side_effect=lambda *a,**kw:Reply(b'HIERARCHY duplicate')):
   with self.assertRaisesRegex(ValueError,'Duplicate content'):fetcher.fetch()
  self.assertFalse((self.root/'cache/118_01.bvh').exists())
 def test_total_limit_enforced_without_content_length(self):
  self.plan['max_additional_bytes']=300;self.write_plan()
  with patch.object(fetcher.urllib.request,'urlopen',side_effect=lambda url,**kw:Reply(b'HIERARCHY'+url.encode()+b'x'*40,0)):
   with self.assertRaisesRegex(ValueError,'Byte cap'):fetcher.fetch()
  rows=json.loads((self.root/'temporal_expansion_manifest_v8.json').read_text())['files'];self.assertLessEqual(sum(v['bytes'] for v in rows),300)
if __name__=='__main__':unittest.main()
