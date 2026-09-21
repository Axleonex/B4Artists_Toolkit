"""Build an offline visual reviewer for the frozen weak motion-label queue."""
from pathlib import Path
import hashlib
import json
import os
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from full_hierarchy_store_v1 import FullHierarchyStore
from temporal_data import quat_matrix


HERE = Path(__file__).resolve()
QUEUE = ROOT / "results/motion-label-proposals-v1/review-queue.json"
OUT = ROOT / "results/motion-label-reviewer-v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def positions(clip, first, last, anchor):
    q = np.asarray(clip.local_quaternions[first:last + 1], dtype=np.float64)
    local = quat_matrix(q)
    basis = local[anchor - first, 0] @ clip.rest_pelvis_rotation.T @ clip.reference
    roots = (np.asarray(clip.root_positions[first:last + 1], dtype=np.float64)
             - clip.root_positions[anchor]) @ basis / clip.scale
    local[:, 0] = np.einsum("ij,fjk->fik", basis.T, local[:, 0])
    world = np.empty_like(local)
    points = np.empty((len(local), len(clip.parents), 3), dtype=np.float64)
    world[:, 0] = local[:, 0]
    points[:, 0] = roots
    for child, parent in enumerate(clip.parents[1:], 1):
        world[:, child] = world[:, parent] @ local[:, child]
        points[:, child] = points[:, parent] + np.einsum(
            "fij,j->fi", world[:, parent], clip.offsets[child]
        )
    return np.round(points, 5).tolist()


def html(data, queue_hash):
    payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    parents = json.dumps(data[0]["parents"])
    return f'''<!doctype html><meta charset="utf-8"><title>B4Artists motion-label review</title>
<style>body{{font:15px system-ui;background:#17191d;color:#eee;margin:18px}}button,input,select,textarea{{background:#292d34;color:#eee;border:1px solid #555;padding:7px}}button.active{{outline:3px solid #69d}}canvas{{background:#0d0f12;border:1px solid #444;max-width:100%}}.row{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:9px 0}}textarea{{width:520px;height:45px}}#meta{{white-space:pre-wrap;color:#bbb}}</style>
<h1>B4Artists weak motion-label review</h1><p>Judge the visible motion, correct the interval if needed, and export. Keys: 1 accept, 2 reject, 3 uncertain, space play, arrows change item.</p>
<div class="row"><button id="prev">Previous</button><b id="counter"></b><button id="next">Next</button><button id="play">Play</button><button id="export">Export reviewed JSON</button></div>
<canvas id="view" width="1000" height="520"></canvas><div id="meta"></div>
<div class="row"><button data-v="accepted">1 Accepted</button><button data-v="rejected">2 Rejected</button><button data-v="uncertain">3 Uncertain</button>
Corrected start <input id="start" type="number"> end <input id="end" type="number"></div>
<div class="row">Intent <select id="intent"><option value="">unreviewed</option><option>walk</option><option>run</option><option>jump</option><option>land</option><option>turn</option><option>reach</option><option>crouch</option><option>interaction</option><option>combat</option><option>dance</option><option>gesture</option><option>other</option></select><textarea id="notes" placeholder="Optional evidence note"></textarea></div>
<script>const items={payload},parents={parents},qh={json.dumps(queue_hash)};let i=0,f=0,timer=null;const key='b4ml-review-'+qh;let reviews=JSON.parse(localStorage.getItem(key)||'{{}}');
const $=x=>document.getElementById(x),cv=$('view'),ctx=cv.getContext('2d');
function save(){{localStorage.setItem(key,JSON.stringify(reviews))}} function current(){{return items[i]}}
function setVerdict(v){{let x=current();reviews[x.review_id]={{...(reviews[x.review_id]||{{}}),verdict:v,corrected_start:+$('start').value,corrected_end:+$('end').value,intent:$('intent').value,notes:$('notes').value}};save();render()}}
function project(p,side){{let a=side?p[1]:p[0],b=p[2];return [250+side*500+a*115,445-b*115]}}
function draw(){{let x=current(),ps=x.positions[f];ctx.clearRect(0,0,cv.width,cv.height);ctx.fillStyle='#aaa';ctx.fillText('FRONT (X/Z)',20,22);ctx.fillText('SIDE (Y/Z)',520,22);for(let s=0;s<2;s++){{ctx.strokeStyle='#78b9ff';ctx.lineWidth=3;for(let j=1;j<parents.length;j++){{let a=project(ps[parents[j]],s),b=project(ps[j],s);ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.stroke()}}for(let j=0;j<ps.length;j++){{let p=project(ps[j],s);ctx.fillStyle=(j==4||j==8)?'#ffbd5b':'#eee';ctx.beginPath();ctx.arc(...p,4,0,7);ctx.fill()}}}}ctx.fillStyle='#fff';ctx.fillText('source frame '+x.source_frames[f],20,505)}}
function render(){{let x=current(),r=reviews[x.review_id]||{{}};f=Math.min(f,x.positions.length-1);$('counter').textContent=`${{i+1}} / ${{items.length}} — ${{x.review_id}}`;$('meta').textContent=`${{x.kind}} | ${{x.clip}} | subject ${{x.subject}} | ${{x.description}}\nproposal ${{x.start}}–${{x.end}}, confidence ${{x.confidence.toFixed(3)}} | saved: ${{r.verdict||'unreviewed'}}`;$('start').value=r.corrected_start??x.start;$('end').value=r.corrected_end??x.end;$('intent').value=r.intent||'';$('notes').value=r.notes||'';document.querySelectorAll('[data-v]').forEach(b=>b.classList.toggle('active',b.dataset.v==r.verdict));draw()}}
function move(d){{i=(i+d+items.length)%items.length;f=0;render()}} function play(){{if(timer){{clearInterval(timer);timer=null;return}}timer=setInterval(()=>{{f=(f+1)%current().positions.length;draw()}},1000/30)}}
$('prev').onclick=()=>move(-1);$('next').onclick=()=>move(1);$('play').onclick=play;document.querySelectorAll('[data-v]').forEach(b=>b.onclick=()=>setVerdict(b.dataset.v));['start','end','intent','notes'].forEach(n=>$(n).onchange=()=>{{let v=reviews[current().review_id]?.verdict||'uncertain';setVerdict(v)}});
$('export').onclick=()=>{{let out={{schema:'b4ml-reviewed-motion-labels-v1',source_queue_sha256:qh,exported_utc:new Date().toISOString(),reviewer:'human',items:Object.entries(reviews).map(([review_id,v])=>({{review_id,...v}}))}};let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(out,null,2)],{{type:'application/json'}}));a.download='b4ml-reviewed-motion-labels-v1.json';a.click()}};
onkeydown=e=>{{if(e.key=='ArrowLeft')move(-1);if(e.key=='ArrowRight')move(1);if(e.key==' '){{e.preventDefault();play()}}if('123'.includes(e.key))setVerdict(['accepted','rejected','uncertain'][+e.key-1])}};render();</script>'''


def main():
    if OUT.exists():
        raise RuntimeError("Reviewer evidence exists: " + str(OUT))
    queue = json.loads(QUEUE.read_text())
    if not queue["all_items_unreviewed"] or queue["reviewed_items"] or queue["ground_truth"]:
        raise ValueError("Expected the frozen unreviewed queue")
    store = FullHierarchyStore(ROOT)
    by_clip = {row["clip"]: index for index, row in enumerate(store.entries)}
    data = []
    for item in queue["items"]:
        clip = store.clip(by_clip[item["clip"]])
        first = max(0, int(item["start"]) - 12)
        last = min(len(clip.root_positions) - 1, int(item["end"]) + 12)
        row = dict(item)
        row["source_frames"] = list(range(first, last + 1))
        row["positions"] = positions(clip, first, last, int(item["start"]))
        row["parents"] = list(clip.parents)
        data.append(row)
    OUT.mkdir(parents=True)
    page = OUT / "reviewer.html"
    page.write_text(html(data, sha(QUEUE)), encoding="utf-8")
    manifest = {"complete": True, "schema": "motion-label-reviewer-v1", "items": len(data),
                "queue_sha256": sha(QUEUE), "builder_sha256": sha(HERE), "html_sha256": sha(page),
                "external_dependencies": False, "reviewed_items": 0, "ground_truth": False,
                "model_outcomes_read": False, "confirmation_read": False, "full_goal_complete": False}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__": main()
