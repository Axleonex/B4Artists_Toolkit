"""Current canonical goal-proof boundary: unsigned evidence never earns credit."""
import sys,json,tempfile,unittest,hashlib,copy
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'training/b4artists_ml'),r"\\100.114.2.71\Gdrive\LapArt\hermes-agent-self-evolution"]
from prime_bridge import goalposts as g
from evaluate_milestone_goal_v2 import evaluate

class ReceiptBoundaryTests(unittest.TestCase):
    def setup_case(self):
        td=tempfile.TemporaryDirectory(dir=ROOT/'training/b4artists_ml/cache',prefix='goal-proof-test-');self.addCleanup(td.cleanup);root=Path(td.name)
        (root/'input.txt').write_text('input');(root/'proof.json').write_text('{"passed":true}')
        state=g.create(dict(goal_id='test',objective='Full quality endpoint',builder_id='builder',inputs=['input.txt'],endpoint=[dict(id='complete',description='Full requirement')],categories=[dict(id='correctness',label='Correctness',checks=[dict(id='ready',label='Working input',kind='deterministic')]),dict(id='usability',label='Usability',checks=[dict(id='human',label='Independent usability',kind='judgment')])],progress_milestones=[dict(id='integration',description='Tested integration')]),now=1000)
        state['passed_checks']=['ready'];state['floors']={'correctness':100};state['history']=[{'evidence_id':'old'}];state['stagnant_rounds']=1;state['passed_progress_milestones']=['integration']
        proof=dict(artifact='proof.json',sha256=hashlib.sha256((root/'proof.json').read_bytes()).hexdigest(),input_fingerprint=g.fingerprint(root,['input.txt']),method='deterministic',passed=True)
        return root,state,dict(quality={'ready':proof},milestones={'integration':dict(proof)})
    def test_unsigned_evidence_unknown_preserves_history_and_floors(self):
        root,state,obs=self.setup_case();old=copy.deepcopy(state);r=evaluate(state,obs,root,now=1010,evidence_owner=False)
        self.assertEqual(r['categories']['correctness']['checks']['ready'],'unknown');self.assertEqual(r['endpoint']['complete'],'unknown');self.assertEqual(r['implementation_progress']['lost'],['integration']);self.assertFalse(r['implementation_progress']['accepted']);self.assertNotEqual(r['decision'],'complete')
        self.assertEqual(state['floors'],old['floors']);self.assertEqual(state['passed_checks'],old['passed_checks']);self.assertEqual(state['passed_progress_milestones'],old['passed_progress_milestones']);self.assertEqual(state['history'][:-1],old['history']);self.assertEqual(state['contract'],old['contract'])
    def test_proof_arguments_and_owner_forwarded_to_canonical(self):
        root,state,obs=self.setup_case()
        with patch.object(g,'_proof',wraps=g._proof) as spy:evaluate(state,obs,root,now=1010,evidence_owner=False)
        calls=[x for x in spy.call_args_list if x.kwargs['check_id']=='integration'];self.assertEqual(len(calls),1)
        self.assertEqual(calls[0].kwargs['contract_hash'],state['contract_hash']);self.assertIs(calls[0].kwargs['owner'],False)
    def test_no_new_milestone_credit_from_unsigned_claim(self):
        root,state,obs=self.setup_case();state['passed_progress_milestones']=[];r=evaluate(state,obs,root,now=1010,evidence_owner=False)
        self.assertEqual(r['implementation_progress']['new'],[]);self.assertEqual(state['passed_progress_milestones'],[])
    def test_goalpost_ceiling_still_stops(self):
        root,state,obs=self.setup_case();state['contract']['max_goalposts']=2;state['contract_hash']=g.digest(state['contract']);r=evaluate(state,obs,root,now=1010,evidence_owner=False)
        self.assertEqual(r['decision'],'checkpoint');self.assertEqual(r['reason'],'goalpost limit reached')
    def test_wall_ceiling_still_stops(self):
        root,state,obs=self.setup_case();state['contract']['max_wall_seconds']=5;state['contract_hash']=g.digest(state['contract']);r=evaluate(state,obs,root,now=1010,evidence_owner=False)
        self.assertEqual(r['decision'],'checkpoint');self.assertEqual(r['reason'],'wall-clock ceiling reached')
    def test_undeclared_milestone_preserves_state(self):
        root,state,obs=self.setup_case();old=copy.deepcopy(state);obs['milestones']['surprise']=dict(obs['milestones']['integration'])
        with self.assertRaises(ValueError):evaluate(state,obs,root,now=1010,evidence_owner=False)
        self.assertEqual(state,old)
    def test_missing_owner_resolution_does_not_create_identity(self):
        root,state,obs=self.setup_case()
        with patch.object(g,'_evidence_owner',return_value=None) as resolver:r=evaluate(state,obs,root,now=1010)
        self.assertEqual(resolver.call_count,1);self.assertEqual(r['categories']['correctness']['checks']['ready'],'unknown')
if __name__=='__main__':unittest.main(verbosity=2)
