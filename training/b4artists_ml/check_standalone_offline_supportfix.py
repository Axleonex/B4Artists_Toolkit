"""Exercise current release with Python outbound networking/process launches denied."""
from pathlib import Path
import os,sys,json,time,subprocess,zipfile,hashlib,ast
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve()
CACHE=ROOT/'training/b4artists_ml/cache/offline-v0.13.1';OUT=ROOT/'training/b4artists_ml/results/offline-v0.13.1.json'
GROUPS={
 'foundation':['test_b4artists_ml.KernelTests','test_b4artists_ml.RuntimeTests'],
 'learned':['test_b4artists_ml_learned.LearnedMathTests','test_b4artists_ml_learned.HostLearnedTests'],
 'whole_body':['test_b4artists_ml_context_preview.PreviewTests.test_operator_keep_and_interpolation_candidate','test_b4artists_ml_context_preview.PreviewTests.test_save_reload_keeps_solved_anchor','test_b4artists_ml_context_preview.PreviewTests.test_cancel_mid_solve_restores_previous_preview'],
 'contact':['test_b4artists_ml_contacts.ContactTests.test_crouch_contacts_on_five_real_rigs','test_b4artists_ml_contacts.ContactTests.test_save_cancels_running_job_and_reload_keeps_result'],
 'support':['test_b4artists_ml_support.SupportRigTests'],
 'balance':['test_b4artists_ml_balance.BalanceTests.test_balance_with_learned_proposal','test_b4artists_ml_balance.BalanceTests.test_transformed_reference_and_save_reload_recovery'],
 'flight':['test_b4artists_ml_flight.FlightTests.test_five_real_rigs']}
def host(group):
 import unittest,importlib
 denied=[]
 def audit(event,args):
  if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto','subprocess.Popen','os.system'):
   denied.append(event);raise RuntimeError('Offline validation blocks '+event)
 sys.addaudithook(audit)
 # Prove the audit gate operates, without contacting an endpoint.
 import socket
 try:socket.getaddrinfo('offline-self-test.invalid',443)
 except RuntimeError:pass
 else:raise AssertionError('Network guard did not intercept resolution')
 assert denied==['socket.getaddrinfo'];denied.clear()
 sys.path[:0]=[str(CACHE),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
 os.environ['B4ML_PACKAGE']=str(CACHE)
 suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in GROUPS[group])
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 import b4artists_ml
 assert Path(b4artists_ml.__file__).resolve().is_relative_to(CACHE.resolve())
 record=dict(group=group,tests=result.testsRun,passed=result.wasSuccessful() and not denied,failures=[x[0].id() for x in result.failures],errors=[x[0].id() for x in result.errors],denied_runtime_calls=denied,guard_self_test=True,package=b4artists_ml.__file__)
 (OUT.parent/('offline-v0.13.1-supportfix-'+group+'.json')).write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
def main():
 if CACHE.exists() or OUT.exists():raise RuntimeError('Evidence already exists')
 CACHE.mkdir()
 archive=ROOT/'releases/b4artists_ml_v0.13.1.zip'
 with zipfile.ZipFile(archive) as z:
  for name in z.namelist():
   assert not Path(name).is_absolute() and '..' not in Path(name).parts
  z.extractall(CACHE)
 imports=set();dynamic=[]
 for p in (CACHE/'b4artists_ml').rglob('*.py'):
  tree=ast.parse(p.read_text(encoding='utf-8-sig'))
  for n in ast.walk(tree):
   if isinstance(n,ast.Import):imports.update(x.name.split('.')[0] for x in n.names)
   elif isinstance(n,ast.ImportFrom) and not n.level and n.module:imports.add(n.module.split('.')[0])
   elif isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ('eval','exec','__import__'):dynamic.append(dict(file=str(p.relative_to(CACHE)),line=n.lineno,call=n.func.id))
 rows=[]
 for group in GROUPS:
  start=time.perf_counter();log=ROOT/('training/b4artists_ml/cache/offline-v0.13.1-'+group+'.log')
  with log.open('w') as f:
   p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--python',str(HERE),'--','--group',group],stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4',B4ML_PACKAGE=str(CACHE)),timeout=240)
  result=OUT.parent/('offline-v0.13.1-supportfix-'+group+'.json')
  row=json.loads(result.read_text()) if result.exists() else dict(group=group,passed=False,missing_result=True)
  row.update(host_exit=p.returncode,elapsed_seconds=time.perf_counter()-start,log=str(log.relative_to(ROOT)))
  rows.append(row);print(json.dumps(row),flush=True)
  OUT.write_text(json.dumps(dict(package_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),imports=sorted(imports),dynamic_calls=dynamic,groups=rows,complete=len(rows)==len(GROUPS),passed=len(rows)==len(GROUPS) and all(x['passed'] for x in rows),scope='Current packaged workflows under Python audit denial of outbound networking and process launches; source dependencies inspected separately. Fixture builders are test inputs, not product dependencies. No OS-wide firewall changes; native host shutdown is assessed separately.'),indent=2)+'\n')
if __name__=='__main__':
 if '--group' in sys.argv:host(sys.argv[sys.argv.index('--group')+1])
 else:main()
