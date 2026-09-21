"""Verify the standalone port and old package boundaries before promotion."""
from pathlib import Path
import ast,copy,json,hashlib,zipfile
from build_finalization_package_v1 import definitions
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def defs(path):return {n.name:n for n in ast.parse(path.read_bytes()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def same(a,b):return ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
def main():
    tr=ROOT/'training/b4artists_ml';pkg=ROOT/'b4artists_ml';out=tr/'results/authored-runtime-source-audit-v1.json';assert not out.exists();matches=[]
    for source,dest,names in [
        ('temporal_data.py','temporal_math.py',['rotation6','quaternion','quat_matrix','slerp']),
        ('shape_reference.py','temporal_math.py',['harmonic_tangent']),
        ('rig_observations.py','temporal_observations.py',['_array','_rotations','Observations','encode','_orientation','_frame_set']),
        ('temporal_observer_steps_v1.py','temporal_observations.py',['sample_steps']),
        ('temporal_projection.py','temporal_generation.py',['_frame','_apply_known_blend'])]:
        a=defs(tr/source);b=defs(pkg/dest)
        for name in names:assert same(a[name],b[name]),name;matches.append(source+':'+name)
    a=defs(tr/'temporal_authored_cooperative_v1.py');b=defs(pkg/'temporal_generation.py')
    for name in a:
        x=copy.deepcopy(a[name])
        if name=='_generate_steps':
            i=next(i for i,v in enumerate(x.args.kwonlyargs) if v.arg=='context');assert x.args.kw_defaults[i].value is True;x.args.kw_defaults[i].value=False
        assert same(x,b[name]),name
        matches.append('temporal_authored_cooperative_v1.py:'+name)
    ui_before=definitions((tr/'results/authored-integration-baseline-v1/ui.py').read_bytes());ui_after=definitions((pkg/'ui.py').read_bytes());changed={n for n in ui_before if ui_before[n]!=ui_after[n]};assert changed=={'B4ML_PT_main.draw','register','unregister'},changed
    paths={p.relative_to(ROOT).as_posix():p for p in pkg.rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')}
    archive=ROOT/'releases/b4artists_ml_v0.17.5.zip';assert sha(archive)=='ae2b5a1aa4bbb0f6cd5f58a8095c4c29cf079d62792a0bb539181b7ace936ff2'
    with zipfile.ZipFile(archive) as z:
        added=set(paths)-set(z.namelist());assert added=={'b4artists_ml/temporal_'+n+'.py' for n in ('math','observations','generation','preview')};assert not set(z.namelist())-set(paths)
        changed_files={n for n in z.namelist() if z.read(n)!=paths[n].read_bytes()};assert changed_files=={'b4artists_ml/__init__.py','b4artists_ml/ui.py','b4artists_ml/contacts.py'},changed_files
        a=definitions(z.read('b4artists_ml/contacts.py'));b=definitions((pkg/'contacts.py').read_bytes());assert set(a)==set(b) and {n for n in a if a[n]!=b[n]}=={'correction_steps'}
        def numeric(data):return [n.value for n in ast.walk(ast.parse(data)) if isinstance(n,ast.Constant) and type(n.value) in (int,float)]
        assert numeric(z.read('b4artists_ml/contacts.py'))==numeric((pkg/'contacts.py').read_bytes())
    imports=[]
    for p in pkg.glob('temporal_*.py'):
        for n in ast.walk(ast.parse(p.read_bytes())):
            if isinstance(n,ast.Import):imports.extend(x.name for x in n.names)
            elif isinstance(n,ast.ImportFrom) and n.level==0:imports.append(n.module)
    assert set(imports)<={'sys','copy','math','numpy','bpy','mathutils','dataclasses'},imports
    report=dict(passed=True,identical_definitions=matches,default_context_change='authored endpoints only',existing_changed_ui_methods=sorted(changed),new_package_files=sorted(added),changed_package_files=sorted(changed_files),all_other_packaged_bytes_unchanged=True,contact_numeric_constants_unchanged=True,runtime_absolute_imports=sorted(set(imports)),runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in pkg.glob('*.py')},limitations=['Trajectory positions and SLERP equations unchanged; no new learned-motion or continuity claim.','Additional regression and exact-package offline checks required.'])
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(dict(passed=True,identical_definitions=len(matches),new_modules=len(added),changed_existing_files=sorted(changed_files)))
if __name__=='__main__':main()
