"""Measure callable contextual completion, excluding rig/viewport and data preparation.
SPDX-License-Identifier: GPL-2.0-or-later
Run with Python, or Bforartists --background --factory-startup --python this_file.
"""
import time
IMPORT_STARTED=time.perf_counter()
import sys,json,platform,os,hashlib,ctypes
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import numpy as np
from context_data import load_examples
from context_pipeline import decode_model,complete_pose
IMPORT_MS=(time.perf_counter()-IMPORT_STARTED)*1000


def memory():
    """Windows OS counters; unavailable elsewhere, never silently substitute zero."""
    if os.name!='nt':return None
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(k,ctypes.c_size_t) for k in
            ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage',
             'QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]
    process=ctypes.WinDLL('kernel32',use_last_error=True).GetCurrentProcess
    process.restype=wintypes.HANDLE
    get=ctypes.WinDLL('psapi',use_last_error=True).GetProcessMemoryInfo
    get.argtypes=(wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD)
    get.restype=wintypes.BOOL
    counters=Counters();counters.cb=ctypes.sizeof(counters)
    if not get(process(),ctypes.byref(counters),counters.cb):raise ctypes.WinError(ctypes.get_last_error())
    return dict(working_set_bytes=counters.WorkingSetSize,process_peak_working_set_bytes=counters.PeakWorkingSetSize,
                private_commit_bytes=counters.PrivateUsage)


def main():
    manifest=json.loads((ROOT/'context_confirmation_manifest.json').read_text())
    cases=[]
    for mode in ('neutral','prior'):
        rows=load_examples(ROOT,manifest,'confirmation',seed=20260908,augment=True,mode=mode)
        for clip,data in rows:
            # All confirmation samples, including both synthetic proportion variants.
            for i in range(len(data['x'])):
                cases.append((mode,clip,int(data['frame'][i]),*[data[k][i] for k in ('rest','baseline','target','mask')]))
    before=memory();start=time.perf_counter()
    weights=decode_model((ROOT/'results/context_pose_mlp_v1.npz').read_bytes())
    load_ms=(time.perf_counter()-start)*1000;after_load=memory()
    def solve(case):
        start=time.perf_counter()
        result,stats=complete_pose(weights,*case[3:])
        elapsed=(time.perf_counter()-start)*1000
        return elapsed,stats
    first_ms,first_stats=solve(cases[0]);records=[];failures=[]
    sampled_memory=[after_load,memory()]
    for index,case in enumerate(cases):
        try:
            elapsed,stats=solve(case)
            records.append(dict(mode=case[0],clip=case[1],frame=case[2],elapsed_ms=elapsed,
                length_error=stats['max_length_error'],pin_error=stats['max_pin_error']))
        except Exception as exc:
            failures.append(dict(index=index,mode=case[0],clip=case[1],frame=case[2],error=str(exc)))
        if index%10==0:sampled_memory.append(memory())
    after=memory();sampled_memory.append(after)
    def distribution(items):
        values=np.array([r['elapsed_ms'] for r in items])
        return dict(samples=len(values),median_ms=float(np.median(values)),p95_ms=float(np.percentile(values,95)),
                    max_ms=float(np.max(values))) if len(values) else None
    try:
        import bpy
        host=dict(version=bpy.app.version_string,build_hash=bpy.app.build_hash.decode())
    except ImportError:host=None
    report=dict(schema=1,host=host,python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),
        processor=platform.processor(),logical_cpus=os.cpu_count(),model_sha256=hashlib.sha256((ROOT/'results/context_pose_mlp_v1.npz').read_bytes()).hexdigest(),
        import_ms=IMPORT_MS,model_read_validate_ms=load_ms,first_solve_ms=first_ms,first_solve_stats=first_stats,
        model_array_bytes=sum(a.nbytes for a in weights.values()),warm=distribution(records),
        per_mode={mode:distribution([r for r in records if r['mode']==mode]) for mode in ('neutral','prior')},
        before_model_memory=before,after_model_memory=after_load,after_benchmark_memory=after,
        sampled_working_set_increase_bytes=max(m['working_set_bytes'] for m in sampled_memory if m)-before['working_set_bytes'] if before else None,
        max_length_error=max(r['length_error'] for r in records),max_pin_error=max(r['pin_error'] for r in records),
        attempted=len(cases),failures=failures,records=records,
        scope='Backend only. Data preparation, rig extraction/application, dependency graph and viewport excluded. '
        'First solve follows imports and data preparation; not application cold startup. Import may reuse host modules. '
        'OS process peak includes host and data preparation; sampled RSS delta is not an allocation peak. Single machine/run.')
    name='context_backend_benchmark_host_v1.json' if host else 'context_backend_benchmark_python_v1.json'
    (ROOT/'results'/name).write_text(json.dumps(report,indent=2)+'\n')
    print('CONTEXT_BENCHMARK: '+json.dumps({k:v for k,v in report.items() if k!='records'}),flush=True)
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
