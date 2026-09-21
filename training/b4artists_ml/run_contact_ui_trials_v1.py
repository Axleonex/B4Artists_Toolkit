"""Repeat the real-window contact workflow and aggregate release-gate evidence."""
from pathlib import Path
import json,subprocess,time

ROOT=Path(__file__).resolve().parents[2]
RESULT=ROOT/'training/b4artists_ml/results/contact-suggestions-ui-v1.json'
OUTPUT=ROOT/'training/b4artists_ml/results/contact-ui-trials-v1.json'
HOST=Path('X:/5.1.0/bforartists.exe')
TEST=ROOT/'tests/test_b4artists_ml_contact_suggestions.py'


def percentile(values,p):
    ordered=sorted(values)
    return ordered[min(len(ordered)-1,int(p*len(ordered)))]


def main(trials=3):
    rows=[];started=time.perf_counter()
    for index in range(trials):
        if RESULT.exists():RESULT.unlink()
        process=subprocess.run(
            [str(HOST),'--factory-startup','--disable-autoexec','--enable-event-simulate','--python',str(TEST),'--','--ui-smoke'],
            cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT,timeout=180)
        if not RESULT.exists():raise RuntimeError(f'Actual-window trial {index+1} produced no result (host exit {process.returncode})')
        report=json.loads(RESULT.read_text(encoding='utf-8'))
        if not report.get('passed'):raise RuntimeError(f'Actual-window trial {index+1} failed: {report}')
        correction=report['correction']
        slowest_suggestion=max(report['suggestion_step_details'],key=lambda row:row['elapsed_ms'])
        slowest=max(report['correction_step_details'],key=lambda row:row['elapsed_ms'])
        rows.append(dict(
            trial=index+1,host_exit=process.returncode,functional_pass=True,
            suggestion_elapsed_ms=report['suggestion']['elapsed_ms'],
            suggestion_step_p95_ms=report['suggestion_step_p95_ms'],
            suggestion_step_max_ms=report['suggestion_step_max_ms'],
            suggestion_slowest_phase=slowest_suggestion['progress'],
            correction_elapsed_ms=correction['elapsed_ms'],
            correction_step_p95_ms=report['correction_step_p95_ms'],
            correction_step_max_ms=report['correction_step_max_ms'],
            correction_slowest_phase=slowest['progress'],
            correction_error=correction['max_after'],fit_frames=correction['frames'],
            validation_frames=correction['validation_frames'],backend=correction['backend']))
    suggestion_max=[r['suggestion_step_max_ms'] for r in rows]
    correction_max=[r['correction_step_max_ms'] for r in rows]
    elapsed=[r['correction_elapsed_ms'] for r in rows]
    gates=dict(
        all_functional=all(r['functional_pass'] for r in rows),
        every_suggestion_callback_below_50ms=max(suggestion_max)<50.,
        every_correction_callback_below_50ms=max(correction_max)<50.,
        every_correction_below_8s=max(elapsed)<8000.,
        correction_error_below_2e_4=max(r['correction_error'] for r in rows)<2e-4)
    result=dict(schema=1,passed=all(gates.values()),trials=rows,summary=dict(
        correction_elapsed_median_ms=percentile(elapsed,.5),correction_elapsed_max_ms=max(elapsed),
        suggestion_callback_max_ms=max(suggestion_max),correction_callback_max_ms=max(correction_max)),
        gates=gates,host_shutdown_qualified=all(r['host_exit']==0 for r in rows),
        note='Bforartists 5.1.0 has a known post-result access violation on this host; functional evidence is written before shutdown.',
        elapsed_seconds=time.perf_counter()-started)
    OUTPUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2),flush=True)
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
