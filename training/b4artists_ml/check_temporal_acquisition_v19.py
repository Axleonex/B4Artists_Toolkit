"""Offline acquisition invariants; network is replaced by bounded fake responses."""
from pathlib import Path
import contextlib,hashlib,io,json,tempfile,unittest
import fetch_cmu_temporal_v19 as f

class Response(io.BytesIO):
    def __init__(self,data,length=None):
        super().__init__(data);self.headers={'Content-Length':str(len(data) if length is None else length)}

class AcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        (self.root/'cache').mkdir();self.payloads={'001_01':b'HIERARCHY\ntrain','002_01':b'HIERARCHY\nvalidation','003_01':b'HIERARCHY\nconfirmation'}
        f.write(self.root/'prior.json',{'files':[]});rows=[]
        for (clip,data),split in zip(self.payloads.items(),['train','validation','confirmation']):
            rows.append(dict(clip=clip,split=split,path=f'data/{int(clip.split("_")[0]):03d}/{clip}.bvh',bytes=len(data),git_blob_sha1=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()))
        self.plan=dict(files=rows,planned_splits={x['split']:[x['clip']] for x in rows},max_file_bytes=100,max_additional_bytes=300,prior_manifests={'prior.json':f.sha(self.root/'prior.json')},commit='fixed')
        self.calls=[];self.freeze()
    def freeze(self):
        f.write(self.root/'temporal_expansion_plan_v19.json',self.plan);self.h=f.sha(self.root/'temporal_expansion_plan_v19.json')
    def open(self,url,timeout):
        self.calls.append(url);return Response(self.payloads[Path(url).stem])
    def fetch(self,**kwargs):
        with contextlib.redirect_stdout(io.StringIO()):return f.fetch(self.root,expected_plan=self.h,opener=self.open,**kwargs)
    def selection(self,passed=True):
        (self.root/'model.npz').write_bytes(b'frozen model');models={'model.npz':f.sha(self.root/'model.npz')}
        report=dict(plan_sha256=self.h,model_files=models,confirmation_read=False,development_gates={s:dict(passed=passed) for s in ['old_validation','new_validation','combined']})
        f.write(self.root/'report.json',report)
        f.write(self.root/'selection.json',dict(confirmation_loaded=False,plan_sha256=self.h,model_files=models,development_report='report.json',development_report_sha256=f.sha(self.root/'report.json')))
        return Path('selection.json')
    def test_default_seals_confirmation_and_resume_avoids_network(self):
        a=self.fetch();self.assertEqual(len(a['files']),2);self.assertFalse(a['confirmation_accessed']);self.assertFalse((self.root/'cache/003_01.bvh').exists())
        self.fetch();self.assertEqual(len(self.calls),2)
    def test_failed_development_does_not_open_confirmation(self):
        with self.assertRaisesRegex(ValueError,'quality gates'):self.fetch(selection=self.selection(False))
        self.assertEqual(self.calls,[])
    def test_confirmation_requires_matching_frozen_model(self):
        s=self.selection();(self.root/'model.npz').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'model changed'):self.fetch(selection=s)
        self.assertEqual(self.calls,[])
    def test_confirmation_opens_only_with_complete_pass_and_is_marked(self):
        a=self.fetch(selection=self.selection());self.assertEqual(len(a['files']),3);self.assertTrue(a['confirmation_accessed']);self.assertTrue(a['confirmation_selection_sha256'])
    def test_plan_tamper_is_refused(self):
        self.plan['files'][0]['split']='confirmation';f.write(self.root/'temporal_expansion_plan_v19.json',self.plan)
        with self.assertRaisesRegex(ValueError,'plan changed'):self.fetch()
        self.assertEqual(self.calls,[])
    def test_prior_ownership_mutation_refused(self):
        f.write(self.root/'prior.json',{'files':[{'clip':'001_01','split':'test','sha256':'x'}]})
        with self.assertRaisesRegex(ValueError,'manifest changed'):self.fetch()
    def test_per_file_and_total_caps_before_network(self):
        self.plan['max_file_bytes']=1;self.freeze()
        with self.assertRaisesRegex(ValueError,'Per-file cap'):self.fetch()
        self.plan['max_file_bytes']=100;self.plan['max_additional_bytes']=1;self.freeze()
        with self.assertRaisesRegex(ValueError,'Total declared cap'):self.fetch()
        self.assertEqual(self.calls,[])
    def test_same_size_wrong_blob_refused(self):
        self.payloads['001_01']=b'HIERARCHY\nwrong'
        with self.assertRaisesRegex(ValueError,'checksum mismatch'):self.fetch()
        self.assertFalse((self.root/'cache/001_01.bvh').exists())
    def test_read_caps_even_without_honest_header(self):
        data=b'HIERARCHY'+b'x'*500
        with self.assertRaisesRegex(ValueError,'size or byte cap'):f.validate_payload(data,self.plan['files'][0],100)
        self.open=lambda url,timeout:Response(data,self.plan['files'][0]['bytes'])
        with self.assertRaisesRegex(ValueError,'size or byte cap'):self.fetch()
    def test_duplicate_content_in_prior_split_refused(self):
        f.write(self.root/'prior.json',{'files':[{'clip':'009_01','split':'test','sha256':hashlib.sha256(self.payloads['001_01']).hexdigest()}]})
        self.plan['prior_manifests']['prior.json']=f.sha(self.root/'prior.json');self.freeze()
        result=self.fetch();row=result['files'][0];self.assertEqual(row['status'],'excluded');self.assertEqual(row['duplicate_owners'],[{'clip':'009_01','split':'test'}]);self.assertFalse(result['confirmation_accessed'])
        self.assertFalse((self.root/'cache/001_01.bvh').exists())
    def test_pending_resume_after_transport_failure(self):
        normal=self.open
        def failed(url,timeout):raise OSError('network unavailable')
        self.open=failed
        with self.assertRaisesRegex(OSError,'unavailable'):self.fetch()
        self.assertEqual(f.read(self.root/'temporal_expansion_manifest_v19.json')['files'][0]['status'],'pending')
        self.open=normal;self.assertEqual(len(self.fetch()['files']),2)
    def test_completed_content_mutation_refused(self):
        self.fetch();(self.root/'cache/001_01.bvh').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'completed clip changed'):self.fetch()
    def test_unrecorded_preexisting_motion_refused(self):
        (self.root/'cache/001_01.bvh').write_bytes(self.payloads['001_01'])
        with self.assertRaisesRegex(ValueError,'Unrecorded motion'):self.fetch()
    def test_selection_path_escape_refused(self):
        with self.assertRaisesRegex(ValueError,'escapes'):self.fetch(selection='../selection.json')

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(AcquisitionTests);result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(passed=result.wasSuccessful(),cases=result.testsRun,network_used=False,source_sha256={p.name:f.sha(p) for p in [Path(__file__),Path(f.__file__)]},errors=[str(x) for x in result.errors+result.failures])
    f.write(Path(__file__).parent/'results/temporal-acquisition-checks-v19.json',report)
    raise SystemExit(0 if result.wasSuccessful() else 1)
