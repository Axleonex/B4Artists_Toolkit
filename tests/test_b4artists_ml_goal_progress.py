"""Goal progress extension cannot weaken final quality gates or run ceilings."""
import sys,json,tempfile,unittest,hashlib,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'training/b4artists_ml'),r'\\100.114.2.71\Gdrive\LapArt\hermes-agent-self-evolution']
from prime_bridge import goalposts as g
from evaluate_milestone_goal import evaluate

class ProgressTests(unittest.TestCase):
    def setup_case(self):
        td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup);root=Path(td.name);(root/'input.txt').write_text('input');(root/'proof.json').write_text('{"passed":true}')
        state=g.create(dict(goal_id='test',objective='Full quality endpoint',builder_id='builder',inputs=['input.txt'],endpoint=[dict(id='complete',description='Full requirement')],categories=[dict(id='correctness',label='Correctness',checks=[dict(id='ready',label='Working input',kind='deterministic')]),dict(id='usability',label='Usability',checks=[dict(id='human',label='Independent usability',kind='judgment')])],progress_milestones=[dict(id='integration',description='Tested integration')]),now=1000)
        state['passed_checks']=['ready'];state['floors']={'correctness':100};state['history']=[{'evidence_id':'old'}];state['stagnant_rounds']=1
        proof=dict(artifact='proof.json',sha256=hashlib.sha256((root/'proof.json').read_bytes()).hexdigest(),input_fingerprint=g.fingerprint(root,['input.txt']),method='deterministic',passed=True)
        return root,state,dict(quality={'ready':proof},milestones={'integration':dict(proof)})
    def test_new_current_milestone_resumes_progress_without_completion(self):
        root,state,obs=self.setup_case();report=evaluate(state,obs,root,now=1010)
        self.assertEqual(report['canonical_decision'],'checkpoint');self.assertEqual(report['decision'],'iterate');self.assertEqual(state['stagnant_rounds'],0);self.assertEqual(report['endpoint']['complete'],'unknown');self.assertEqual(report['categories']['usability']['score'],0)
    def test_no_repeat_credit(self):
        root,state,obs=self.setup_case();state['passed_progress_milestones']=['integration'];report=evaluate(state,obs,root,now=1010);self.assertEqual(report['decision'],'checkpoint')
    def test_stale_proof_no_credit(self):
        root,state,obs=self.setup_case();obs['milestones']['integration']['input_fingerprint']='stale';report=evaluate(state,obs,root,now=1010);self.assertEqual(report['decision'],'checkpoint')
    def test_regression_no_credit(self):
        root,state,obs=self.setup_case();obs['quality']['ready']=dict(obs['quality']['ready'],passed=False);report=evaluate(state,obs,root,now=1010);self.assertEqual(report['decision'],'checkpoint');self.assertTrue(report['categories']['correctness']['regression'])
    def test_goalpost_ceiling_still_stops(self):
        root,state,obs=self.setup_case();state['contract']['max_goalposts']=2;state['contract_hash']=g.digest(state['contract']);report=evaluate(state,obs,root,now=1010);self.assertEqual(report['decision'],'checkpoint');self.assertEqual(report['reason'],'goalpost limit reached')
    def test_wall_ceiling_still_stops(self):
        root,state,obs=self.setup_case();state['contract']['max_wall_seconds']=5;state['contract_hash']=g.digest(state['contract']);report=evaluate(state,obs,root,now=1010);self.assertEqual(report['decision'],'checkpoint');self.assertEqual(report['reason'],'wall-clock ceiling reached')
    def test_undeclared_milestone_changes_nothing(self):
        root,state,obs=self.setup_case();before=copy.deepcopy(state);obs['milestones']['surprise']=obs['milestones']['integration']
        with self.assertRaises(ValueError):evaluate(state,obs,root,now=1010)
        self.assertEqual(state,before)

if __name__=='__main__':unittest.main(verbosity=2)
