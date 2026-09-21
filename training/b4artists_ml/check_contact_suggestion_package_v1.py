"""Run established offline workflows plus contact suggestions on exact 0.20.0."""
from pathlib import Path
import json,os,subprocess,sys

ROOT=Path(__file__).resolve().parents[2];SOURCE=Path(__file__).with_name('check_visible_state_package_v1.py')
text=SOURCE.read_text(encoding='utf-8-sig')
for old,new in {
    "visible-state-package-v1":"contact-suggestion-package-v1",
    "(0,19,2)":"(0,20,0)",
    "b4artists_ml_v0.19.2.zip":"b4artists_ml_v0.20.0.zip",
    "package-test-v0.19.2.json":"package-test-v0.20.0.json",
}.items():
    assert old in text;text=text.replace(old,new)
exec(compile(text,str(Path(__file__)), 'exec'))

if __name__=='__main__' and '--host' not in sys.argv:
    base=ROOT/'training/b4artists_ml/cache/contact-suggestion-package-v1';result=ROOT/'training/b4artists_ml/results/contact-suggestions-package-v1.json';log=ROOT/'training/b4artists_ml/cache/contact-suggestions-package-v1.log'
    assert base.is_dir() and not result.exists()
    env=dict(os.environ,B4ML_PACKAGE=str(base),B4ML_CONTACT_SUGGEST_RESULT=result.name,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4')
    with log.open('w') as stream:proc=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(ROOT/'tests/test_b4artists_ml_contact_suggestions.py')],stdout=stream,stderr=subprocess.STDOUT,env=env,timeout=300)
    report=json.loads(result.read_text());assert report['passed'] and report['tests']==4;report['host_exit']=proc.returncode;report['exact_package']=True;report['host_shutdown_qualified']=False;result.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
