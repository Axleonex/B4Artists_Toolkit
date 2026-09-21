"""Compose refreshed affected suites with explicitly unchanged baseline coverage."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'training/b4artists_ml/results/read-scope-regression-composed-v1.json'
 if out.exists():raise RuntimeError('Evidence already exists')
 base_path=ROOT/'training/b4artists_ml/results/live-pose-final-v1-regression.json'
 base=json.loads(base_path.read_text());by={r['suite']:r for r in base};expected_changed={'b4artists_ml/body_live.py','b4artists_ml/body_preview.py','b4artists_ml/__init__.py'}
 # The baseline was run before the separately verified version-only 0.15.0 bump.
 current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
 sources=[ROOT/'training/b4artists_ml/results/preview-reads-v1-regression.json',ROOT/'training/b4artists_ml/results/preview-reads-integration-v1-regression.json']
 fresh=[r for p in sources for r in json.loads(p.read_text())]
 required={'test_b4artists_ml_preview_reads','test_b4artists_ml_body_live','test_b4artists_ml_context_preview','test_b4artists_ml_body_controls','test_b4artists_ml_joint_limits','test_b4artists_ml_joint_frames','test_b4artists_ml_bend_limits','test_b4artists_ml_balance','test_b4artists_ml_proxy','test_b4artists_ml_native_flight','test_b4artists_ml'}
 assert {r['suite'] for r in fresh}==required and len(fresh)==len(required)
 assert all(r['assertions_passed'] and not r['skipped'] and r['runtime_sha256']==current for r in fresh)
 for r in base:
  assert r['assertions_passed'] and not r['skipped']
  changed={k for k,v in r['runtime_sha256'].items() if current.get(k)!=v}
  assert changed<=expected_changed
 structural_path=ROOT/'training/b4artists_ml/results/read-scope-structure-v1.json';structural=json.loads(structural_path.read_text());assert structural['passed'] and structural['runtime_sha256']==current
 for r in fresh:by[r['suite']]=r
 rows=[dict(r,coverage_origin='fresh_current_source' if name in required else 'retained_baseline_with_unchanged_independent_modules') for name,r in sorted(by.items())]
 assert sum(r['tests'] for r in rows)==245
 report=dict(passed=True,unique_cases=245,suites=len(rows),fresh_cases=sum(r['tests'] for r in fresh),retained_cases=sum(r['tests'] for r in rows if r['coverage_origin'].startswith('retained')),runtime_sha256=current,rows=rows,evidence={str(p.relative_to(ROOT)):sha(p) for p in [base_path,*sources,structural_path]},scope='Affected manual/live preview, controls, limits, balance, proxy, native integration and foundation cases were rerun. Retained suites cover unchanged independent modules; changed preview decoder paths have fresh integration tests and structural equivalence of every pre-existing branch outside explicit scoped reads. This is composed coverage, not a claim that all 245 cases were freshly rerun on this source.')
 out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('passed','unique_cases','suites','fresh_cases','retained_cases')}),flush=True)
if __name__=='__main__':main()
