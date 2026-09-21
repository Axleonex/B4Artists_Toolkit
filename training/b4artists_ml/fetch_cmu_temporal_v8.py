"""Pinned, byte-bounded motion acquisition with confirmation kept behind selection."""
from pathlib import Path
import argparse,json,hashlib,urllib.request
ROOT=Path(__file__).resolve().parent
BASE='https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/09a07f54f3bbb58797325f009282d0b2048a2871/'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fetch(selection=None):
 plan_path=ROOT/'temporal_expansion_plan_v8.json';plan=json.loads(plan_path.read_text());dest=ROOT/'temporal_expansion_manifest_v8.json';old=json.loads(dest.read_text()) if dest.exists() else {};rows=old.get('files',[]);by_clip={r['clip']:r for r in rows}
 prior=[]
 for p in ROOT.glob('*manifest*.json'):
  if p!=dest:prior.extend(json.loads(p.read_text()).get('files',[]))
 planned=[c for clips in plan['planned_splits'].values() for c in clips];assert len(planned)==len(set(planned));assert not set(planned)&{r['clip'] for r in prior}
 selection_hash=None
 if selection:
  selection=selection.resolve();assert selection.is_relative_to(ROOT.resolve());frozen=json.loads(selection.read_text());assert frozen['confirmation_loaded'] is False
  assert frozen['plan_sha256']==sha(plan_path)
  for rel,expected in frozen['model_files'].items():
   p=(ROOT/rel).resolve();assert p.is_relative_to(ROOT.resolve()) and sha(p)==expected
  selection_hash=sha(selection)
  if old.get("confirmation_selection_sha256") not in (None,selection_hash):raise ValueError("Confirmation already belongs to another frozen selection; do not relabel it as untouched")
 def persist():
  result=dict(schema=8,plan_sha256=sha(plan_path),files=rows,additional_raw_bytes=sum(r['bytes'] for r in rows),max_additional_bytes=plan['max_additional_bytes'],confirmation_selection_sha256=selection_hash or old.get('confirmation_selection_sha256'),provenance=plan['provenance']);dest.write_text(json.dumps(result,indent=2)+'\n');return result
 for split,clips in plan['planned_splits'].items():
  if split=='confirmation' and selection is None:continue
  for clip in clips:
   p=ROOT/'cache'/(clip+'.bvh');url=BASE+f'data/{int(clip.split("_")[0]):03d}/{clip}.bvh'
   if clip in by_clip:
    assert p.exists() and sha(p)==by_clip[clip]['sha256'];continue
   if p.exists():raise ValueError('Unrecorded existing clip cannot be claimed as untouched: '+clip)
   remaining=plan['max_additional_bytes']-sum(r['bytes'] for r in rows);cap=min(plan['max_file_bytes'],remaining)
   with urllib.request.urlopen(url,timeout=30) as response:
    if int(response.headers.get('Content-Length',0))>cap:raise ValueError('Clip exceeds remaining declared byte cap: '+clip)
    data=response.read(cap+1)
   if len(data)>cap or not data.lstrip().startswith(b'HIERARCHY'):raise ValueError('Byte cap or BVH format refused: '+clip)
   digest=hashlib.sha256(data).hexdigest()
   if digest in {r['sha256'] for r in prior+rows}:raise ValueError('Duplicate content across motion splits: '+clip)
   p.write_bytes(data);row=dict(clip=clip,split=split,url=url,bytes=len(data),sha256=digest);rows.append(row);by_clip[clip]=row;persist();print(json.dumps(row),flush=True)
 return persist()
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--selection',type=Path);args=parser.parse_args();print(json.dumps(fetch(args.selection)),flush=True)
