"""Fixed CMU acquisition: pinned bytes, resumable ledger, sealed confirmation."""
from pathlib import Path
import argparse, hashlib, json, re, urllib.request
ROOT=Path(__file__).resolve().parent
PLAN_SHA='8af5a83abffd86b50c1e1f5426f330ad524970dd30475e313b7d02d6cc1d669a'
BASE='https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def require(condition,message):
    if not condition: raise ValueError(message)
def safe(root,relative):
    p=(root/relative).resolve()
    require(p.is_relative_to(root.resolve()),'Path escapes research root')
    return p

def write(path,data):
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    temporary.replace(path)

def validate_payload(data,row,cap):
    require(len(data)<=cap and len(data)==row['bytes'],'Published size or byte cap mismatch')
    require(data.lstrip().startswith(b'HIERARCHY'),'Expected BVH motion')
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    require(blob==row['git_blob_sha1'],'Pinned Git blob checksum mismatch')
    return hashlib.sha256(data).hexdigest()

def fetch(root=ROOT,selection=None,*,expected_plan=PLAN_SHA,opener=urllib.request.urlopen):
    root=Path(root).resolve();plan_path=root/'temporal_expansion_plan_v19.json'
    require(sha(plan_path)==expected_plan,'Frozen acquisition plan changed')
    plan=read(plan_path);dest=root/'temporal_expansion_manifest_v19.json';planned=plan['files']
    require(len({x['clip'] for x in planned})==len(planned),'Repeated planned clip')
    require(set(plan['planned_splits'])=={'train','validation','confirmation'},'Unexpected splits')
    require(all([x['clip'] for x in planned if x['split']==s]==cs for s,cs in plan['planned_splits'].items()),'Plan order mismatch')
    require(all(re.fullmatch(r'\d+_\d+',x['clip']) and x['path']==f'data/{int(x["clip"].split("_")[0]):03d}/{x["clip"]}.bvh' for x in planned),'Invalid clip path')
    require(all(0<x['bytes']<=plan['max_file_bytes'] for x in planned),'Per-file cap exceeded')
    require(sum(x['bytes'] for x in planned)<=plan['max_additional_bytes'],'Total declared cap exceeded')
    prior=[]
    for rel,h in plan['prior_manifests'].items():
        p=safe(root,rel);require(sha(p)==h,'Prior split manifest changed');prior+=read(p).get('files',[])
    require(not {x['clip'] for x in planned}&{x['clip'] for x in prior},'Clip already owned by prior split')
    state=read(dest) if dest.exists() else dict(schema=19,plan_sha256=expected_plan,files=[],confirmation_selection_sha256=None)
    require(state['plan_sha256']==expected_plan,'Acquisition belongs to different plan')
    by_clip={x['clip']:x for x in state['files']};require(len(by_clip)==len(state['files']),'Repeated ledger clip')
    spec={x['clip']:x for x in planned}
    for clip,row in by_clip.items():
        require(clip in spec and all(row[k]==spec[clip][k] for k in ['split','bytes','git_blob_sha1']),'Ledger differs from fixed plan')
        require(row['status'] in ('pending','complete','excluded'),'Unknown acquisition status')
        if row['status']=='complete':
            p=root/'cache'/(clip+'.bvh');require(p.exists() and sha(p)==row['sha256'],'Previously completed clip changed')
    selection_hash=None
    if selection is not None:
        p=safe(root,selection);frozen=read(p);selection_hash=sha(p)
        require(frozen['confirmation_loaded'] is False,'Selection already observed confirmation')
        require(frozen['plan_sha256']==expected_plan,'Selected model belongs to different acquisition plan')
        require(frozen['model_files'],'No frozen learned model')
        for rel,h in frozen['model_files'].items():require(sha(safe(root,rel))==h,'Frozen model changed')
        q=safe(root,frozen['development_report']);require(sha(q)==frozen['development_report_sha256'],'Development evidence changed')
        report=read(q)
        require(report['plan_sha256']==expected_plan and report['model_files']==frozen['model_files'],'Development report/model mismatch')
        require(report['confirmation_read'] is False,'Development already used confirmation')
        require(all(report['development_gates'][s]['passed'] is True for s in ('old_validation','new_validation','combined')),'Development quality gates failed')
        require(state['confirmation_selection_sha256'] in (None,selection_hash),'Confirmation already assigned to another selection')
        state['confirmation_selection_sha256']=selection_hash
    def persist():
        state['additional_raw_bytes']=sum(x['bytes'] for x in state['files'] if x['status']=='complete')
        state['reserved_raw_bytes']=sum(x['bytes'] for x in state['files'])
        state['confirmation_accessed']=any(x['split']=='confirmation' for x in state['files'])
        write(dest,state)
    (root/'cache').mkdir(exist_ok=True)
    for item in planned:
        clip=item['clip'];split=item['split']
        if split=='confirmation' and selection is None:continue
        row=by_clip.get(clip);p=root/'cache'/(clip+'.bvh')
        if row and row['status'] in ('complete','excluded'):continue
        require(row is not None or not p.exists(),'Unrecorded motion cannot be claimed untouched: '+clip)
        cap=min(plan['max_file_bytes'],plan['max_additional_bytes']-sum(x['bytes'] for x in state['files'] if x['clip']!=clip))
        require(item['bytes']<=cap,'Remaining byte cap exceeded')
        url=BASE+plan['commit']+'/'+item['path']
        # Record access intent before opening the URL, including a durable
        # confirmation exposure marker even if the request is interrupted.
        if row is None:
            row={k:item[k] for k in ['clip','split','bytes','git_blob_sha1']};row.update(url=url,status='pending')
            state['files'].append(row);by_clip[clip]=row;persist()
        if p.exists():data=p.read_bytes()
        else:
            with opener(url,timeout=30) as response:
                length=response.headers.get('Content-Length')
                require(length is None or int(length)==item['bytes'],'Unexpected declared response size')
                data=response.read(cap+1)
        digest=validate_payload(data,item,cap)
        others=prior+[x for x in state['files'] if x['clip']!=clip and x['status']=='complete']
        duplicates=[dict(clip=x['clip'],split=x['split']) for x in others if x['sha256']==digest]
        if duplicates:
            require(not p.exists(),'Duplicate unexpectedly present in cache')
            row.update(sha256=digest,status='excluded',reason='duplicate_content',duplicate_owners=duplicates)
            persist();print(json.dumps(dict(event='excluded_duplicate',clip=clip,owners=duplicates)),flush=True);continue
        if not p.exists():
            temporary=p.with_suffix('.bvh.part');temporary.write_bytes(data);temporary.replace(p)
        row.update(sha256=digest,status='complete');persist()
        print(json.dumps(dict(event='acquired',clip=clip,split=split,bytes=len(data))),flush=True)
    persist();return state

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--selection',type=Path);args=parser.parse_args()
    result=fetch(selection=args.selection)
    print(json.dumps(dict(event='complete',clips=sum(x['status']=='complete' for x in result['files']),bytes=result['additional_raw_bytes'],confirmation_accessed=result['confirmation_accessed'])),flush=True)
