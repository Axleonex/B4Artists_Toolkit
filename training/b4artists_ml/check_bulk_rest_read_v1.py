"""Compare bulk RNA matrix reads with the exact serialized rest signature."""
from pathlib import Path
import sys,os,json,time,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();OUT=ROOT/'training/b4artists_ml/results/bulk-rest-read-v1.json'
def host():
 import bpy,numpy as np
 sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
 from b4artists_ml import workflow as w
 from test_b4artists_ml_context_rig import ContextRigTests
 ContextRigTests.setUpClass();helper=ContextRigTests();rows=[]
 def bulk(ob,transpose):
  bones=ob.data.bones;data=np.empty((len(bones),4,4),np.float32);bones.foreach_get('matrix_local',data.ravel())
  values=(data.transpose(0,2,1) if transpose else data).reshape(len(bones),16).tolist()
  return {b.name:dict(parent=b.parent.name if b.parent else None,rest=values[i]) for i,b in enumerate(bones)}
 for label in helper.builders:
  ob,source,session,targets,mask=helper.fixture(label);reference=w._rest_signature(ob);encoded=json.dumps(reference);matching=[t for t in [False,True] if json.dumps(bulk(ob,t))==encoded];assert len(matching)==1
  transpose=matching[0];times={'reference':[],'bulk':[]}
  for _ in range(50):
   for mode in ['reference','bulk','bulk','reference']:
    start=time.perf_counter();value=w._rest_signature(ob) if mode=='reference' else bulk(ob,transpose);times[mode].append((time.perf_counter()-start)*1000);assert json.dumps(value)==encoded
  rows.append(dict(rig=label,bones=len(ob.data.bones),transpose=transpose,serialized_exact=True,reference_median_ms=float(np.median(times['reference'])),bulk_median_ms=float(np.median(times['bulk']))));session.cancel()
 assert len({r['transpose'] for r in rows})==1
 OUT.write_text(json.dumps(dict(passed=True,rows=rows,workflow_sha256=hashlib.sha256((ROOT/'b4artists_ml/workflow.py').read_bytes()).hexdigest(),scope='Exact serialized structural signatures across five real rig profiles with repeated alternating reads. Local function prototype only; no runtime mutation or cache.'),indent=2)+'\n')
if __name__=='__main__':
 if '--host' in sys.argv:host()
 else:
  if OUT.exists():raise RuntimeError('Evidence exists')
  log=ROOT/'training/b4artists_ml/cache/bulk-rest-read-v1.log';start=time.perf_counter()
  with log.open('w') as stream:
   proc=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host'],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=120)
  receipt=dict(exit_code=proc.returncode,seconds=time.perf_counter()-start,log=log.relative_to(ROOT).as_posix(),result_present=OUT.exists());(OUT.parent/'bulk-rest-read-process-v1.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
