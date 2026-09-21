"""Build the strict, resumable v2 reviewer for the frozen weak-label queue."""
from pathlib import Path
import hashlib
import json
import math
import re
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from motion_label_review_v2 import CONTRACT_SCHEMA, INTENTS, canonical_bytes, digest_document, loads_strict


HERE = Path(__file__).resolve()
QUEUE = ROOT / "results/motion-label-proposals-v1/review-queue.json"
V1 = ROOT / "results/motion-label-reviewer-v1"
OUT = ROOT / "results/motion-label-reviewer-v2"
EXPECTED_QUEUE_SHA256 = "33624b7f30036ca2ed23f698efe67e8920b37d4dd754b33c178a63d87c337513"
EXPECTED_V1_HTML_SHA256 = "ac6e084ab70611cc4df382b2dd21dae93ab9ab4c40e343e3b628efb35f03afa0"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_embedded_v1(queue):
    manifest = loads_strict(
        (V1 / "manifest.json").read_bytes(), "v1 reviewer manifest", maximum_bytes=100_000
    )
    page = V1 / "reviewer.html"
    if not (
        sha(QUEUE) == manifest["queue_sha256"] == EXPECTED_QUEUE_SHA256
        and sha(page) == manifest["html_sha256"] == EXPECTED_V1_HTML_SHA256
    ):
        raise ValueError("Frozen v1 reviewer identity mismatch")
    match = re.search(r"const items=(.*),parents=(\[[^;]+\]),qh=([^;]+);let i=", page.read_text(encoding="utf-8"))
    if not match:
        raise ValueError("Frozen v1 embedded payload is missing")
    items = loads_strict(
        match.group(1).encode("utf-8"), "v1 embedded items", maximum_bytes=30_000_000,
        maximum_nodes=1_000_000,
    )
    parents = loads_strict(
        match.group(2).encode("utf-8"), "v1 embedded parents", maximum_bytes=10_000
    )
    if len(parents) != 23 or parents[0] != -1:
        raise ValueError("Frozen v1 hierarchy changed")
    if len(items) != 130 or len(queue.get("items", ())) != 130:
        raise ValueError("Frozen v1 reviewer must contain 130 items")
    for source, row in zip(queue["items"], items):
        if any(row.get(key) != value for key, value in source.items()):
            raise ValueError("Frozen v1 queue payload changed")
        frames = row.get("source_frames")
        positions = row.get("positions")
        if (
            not isinstance(frames, list)
            or frames != list(range(frames[0], frames[-1] + 1))
            or not isinstance(positions, list)
            or len(positions) != len(frames)
        ):
            raise ValueError("Frozen v1 preview frame layout changed")
        for frame in positions:
            if len(frame) != 23 or any(
                len(point) != 3 or any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in point)
                for point in frame
            ):
                raise ValueError("Frozen v1 preview contains invalid joint data")
    return items, parents


def page_source(items, parents, queue_hash, contract_hash):
    payload = json.dumps(items, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    parent_payload = json.dumps(parents, separators=(",", ":"))
    options = "".join(f'<option value="{name}">{name.replace("_", " ").title()}</option>' for name in sorted(INTENTS))
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>B4Artists motion-label review v2</title>
<style>body{{font:15px system-ui;background:#17191d;color:#eee;margin:18px}}button,input,select,textarea{{background:#292d34;color:#eee;border:1px solid #555;padding:7px}}button.active{{outline:3px solid #69d}}button:disabled{{opacity:.4}}canvas{{background:#0d0f12;border:1px solid #444;max-width:100%}}.row{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:9px 0}}textarea{{width:520px;height:45px}}#meta{{white-space:pre-wrap;color:#bbb}}#notice{{color:#ffd47a;min-height:1.3em}}label{{display:flex;gap:5px;align-items:center}}</style></head><body>
<h1>B4Artists weak motion-label review v2</h1><p>Judge the visible motion. A completed export requires all 130 decisions, valid intervals, reviewer details, and independent-animator self-attestation.</p>
<div class="row"><label>Reviewer code <input id="reviewer" maxlength="80"></label><label>Experience <select id="experience"><option value="">Select</option><option value="under_1_year">Under 1 year</option><option value="1_3_years">1–3 years</option><option value="3_5_years">3–5 years</option><option value="5_plus_years">5+ years</option></select></label><label><input id="independent" type="checkbox"> I am an independent animator reviewer</label></div>
<div class="row"><button id="prev">Previous</button><b id="counter"></b><button id="next">Next</button><button id="unfinished">Next unfinished</button><button id="play">Play</button><button id="backup">Export backup</button><button id="export">Export completed review</button></div>
<div id="progress"></div><div id="notice"></div><canvas id="view" width="1000" height="520"></canvas><div id="meta"></div>
<div class="row"><button data-v="accepted">1 Accepted</button><button data-v="rejected">2 Rejected</button><button data-v="uncertain">3 Uncertain</button><label>Corrected start <input id="start" type="number" step="1"></label><label>end <input id="end" type="number" step="1"></label></div>
<div class="row"><label>Intent <select id="intent">{options}</select></label><textarea id="notes" maxlength="2000" placeholder="Optional evidence note"></textarea></div>
<script>const items={payload},parents={parent_payload},qh={json.dumps(queue_hash)},ch={json.dumps(contract_hash)},experienceValues=['under_1_year','1_3_years','3_5_years','5_plus_years'];let i=0,f=0,timer=null;const key='b4ml-review-v2-'+qh;let saved={{}};try{{let raw=localStorage.getItem(key);if(raw&&raw.length<=2000000){{let parsed=JSON.parse(raw);if(parsed&&typeof parsed==='object'&&!Array.isArray(parsed))saved=parsed}}}}catch(_error){{saved={{}}}}let reviews=saved.reviews&&typeof saved.reviews==='object'&&!Array.isArray(saved.reviews)&&Object.keys(saved.reviews).length<=items.length?saved.reviews:{{}},sessionStarted=validUtc(saved.session_started_utc)?saved.session_started_utc:new Date().toISOString();const $=x=>document.getElementById(x),cv=$('view'),ctx=cv.getContext('2d');
function persist(){{localStorage.setItem(key,JSON.stringify({{reviews,session_started_utc:sessionStarted,reviewer:$('reviewer').value,experience:$('experience').value,independent:$('independent').checked}}))}}function current(){{return items[i]}}function bounds(x=current()){{return [x.source_frames[0],x.source_frames[x.source_frames.length-1]]}}function cleanText(x){{return String(x||'').trim()}}
function validUtc(v){{return typeof v==='string'&&/(?:Z|[+-]\\d{{2}}:\\d{{2}})$/.test(v)&&Number.isFinite(Date.parse(v))}}function validReviewer(){{let code=cleanText($('reviewer').value);return code.length>=2&&code.length<=80&&experienceValues.includes($('experience').value)&&$('independent').checked===true}}function validReview(x,r,exportMillis=Date.now()){{let [lo,hi]=bounds(x),a=r?.corrected_start,b=r?.corrected_end,sessionMillis=Date.parse(sessionStarted),reviewMillis=Date.parse(r?.reviewed_utc);return !!r&&r.review_id===x.review_id&&['accepted','rejected','uncertain'].includes(r.verdict)&&typeof a==='number'&&typeof b==='number'&&Number.isInteger(a)&&Number.isInteger(b)&&lo<=a&&a<=b&&b<=hi&&{json.dumps(sorted(INTENTS))}.includes(r.intent)&&typeof r.notes==='string'&&r.notes.length<=2000&&validUtc(sessionStarted)&&validUtc(r.reviewed_utc)&&sessionMillis<=reviewMillis&&reviewMillis<=exportMillis}}
function readForm(verdict){{let x=current(),a=Number($('start').value),b=Number($('end').value),[lo,hi]=bounds(x);if(!Number.isInteger(a)||!Number.isInteger(b)||a<lo||a>b||b>hi)throw Error(`Interval must be whole frames inside ${{lo}}–${{hi}}.`);return {{review_id:x.review_id,verdict,corrected_start:a,corrected_end:b,intent:$('intent').value,notes:$('notes').value.trim(),reviewed_utc:new Date().toISOString()}}}}
function setVerdict(v){{try{{reviews[current().review_id]=readForm(v);persist();$('notice').textContent='';render()}}catch(e){{$('notice').textContent=e.message}}}}
function project(p,side){{let a=side?p[1]:p[0],b=p[2];return [250+side*500+a*115,445-b*115]}}function draw(){{let x=current(),ps=x.positions[f];ctx.clearRect(0,0,cv.width,cv.height);ctx.fillStyle='#aaa';ctx.fillText('FRONT (X/Z)',20,22);ctx.fillText('SIDE (Y/Z)',520,22);for(let s=0;s<2;s++){{ctx.strokeStyle='#78b9ff';ctx.lineWidth=3;for(let j=1;j<parents.length;j++){{let a=project(ps[parents[j]],s),b=project(ps[j],s);ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.stroke()}}for(let j=0;j<ps.length;j++){{let p=project(ps[j],s);ctx.fillStyle=(j==4||j==8)?'#ffbd5b':'#eee';ctx.beginPath();ctx.arc(...p,4,0,7);ctx.fill()}}}}ctx.fillStyle='#fff';ctx.fillText('source frame '+x.source_frames[f],20,505)}}
function render(){{let x=current(),r=reviews[x.review_id]||{{}},now=Date.now(),done=items.filter(y=>validReview(y,reviews[y.review_id],now)).length;f=Math.min(f,x.positions.length-1);$('counter').textContent=`${{i+1}} / ${{items.length}} — ${{x.review_id}}`;$('progress').textContent=`Completed ${{done}} / ${{items.length}}`; $('meta').textContent=`${{x.kind}} | ${{x.clip}} | subject ${{x.subject}} | ${{x.description}}\nproposal ${{x.start}}–${{x.end}}, confidence ${{x.confidence.toFixed(3)}} | saved: ${{r.verdict||'unreviewed'}}`;$('start').min=x.source_frames[0];$('start').max=x.source_frames.at(-1);$('end').min=x.source_frames[0];$('end').max=x.source_frames.at(-1);$('start').value=r.corrected_start??x.start;$('end').value=r.corrected_end??x.end;$('intent').value=r.intent||'unknown';$('notes').value=r.notes||'';document.querySelectorAll('[data-v]').forEach(b=>b.classList.toggle('active',b.dataset.v==r.verdict));$('export').disabled=done!==items.length;draw()}}
function stop(){{if(timer){{clearInterval(timer);timer=null}}}}function move(d){{stop();i=(i+d+items.length)%items.length;f=0;render()}}function nextUnfinished(){{stop();for(let n=1;n<=items.length;n++){{let j=(i+n)%items.length;if(!validReview(items[j],reviews[items[j].review_id])){{i=j;f=0;render();return}}}}$('notice').textContent='Every item is complete.'}}function play(){{if(timer){{stop();return}}timer=setInterval(()=>{{f=(f+1)%current().positions.length;draw()}},1000/30)}}
function download(name,value){{let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{{type:'application/json'}}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),0)}}function base(schema,complete,rows,exportedUtc=new Date().toISOString()){{return {{schema,complete,source_queue_sha256:qh,review_contract_sha256:ch,session_started_utc:sessionStarted,exported_utc:exportedUtc,reviewer:{{code:cleanText($('reviewer').value),experience:$('experience').value,independent_animator:$('independent').checked}},items:rows}}}}
function exportComplete(){{let rows=items.map(x=>reviews[x.review_id]),exportedUtc=new Date().toISOString(),exportMillis=Date.parse(exportedUtc);if(!validUtc(sessionStarted)||rows.some((r,n)=>!validReview(items[n],r,exportMillis))){{$('notice').textContent='Complete every review with valid session timing before exporting.';return}}if(!validReviewer()){{$('notice').textContent='Enter reviewer code, experience, and independent-animator attestation.';return}}persist();download('b4ml-reviewed-motion-labels-v2.json',base('b4ml-reviewed-motion-labels-v2',true,rows,exportedUtc))}}
$('prev').onclick=()=>move(-1);$('next').onclick=()=>move(1);$('unfinished').onclick=nextUnfinished;$('play').onclick=play;document.querySelectorAll('[data-v]').forEach(b=>b.onclick=()=>setVerdict(b.dataset.v));['reviewer','experience','independent'].forEach(n=>$(n).onchange=persist);$('backup').onclick=()=>{{persist();download('b4ml-motion-label-review-backup-v2.json',base('b4ml-motion-label-review-backup-v2',false,items.map(x=>reviews[x.review_id]).filter(Boolean)))}};$('export').onclick=exportComplete;
if(saved.reviewer)$('reviewer').value=saved.reviewer;if(saved.experience)$('experience').value=saved.experience;$('independent').checked=!!saved.independent;onkeydown=e=>{{if(['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName))return;if(e.key==='ArrowLeft')move(-1);if(e.key==='ArrowRight')move(1);if(e.key===' '){{e.preventDefault();play()}}if('123'.includes(e.key))setVerdict(['accepted','rejected','uncertain'][+e.key-1])}};render();</script></body></html>'''


def main():
    if OUT.exists():
        raise RuntimeError("Reviewer v2 evidence exists: " + str(OUT))
    queue = loads_strict(QUEUE.read_bytes(), "source queue", maximum_bytes=4_000_000)
    items, parents = load_embedded_v1(queue)
    if len(items) != 130 or [row["review_id"] for row in items] != [row["review_id"] for row in queue["items"]]:
        raise ValueError("Frozen queue and preview order differ")
    queue_hash = sha(QUEUE)
    contract = {
        "schema": CONTRACT_SCHEMA,
        "goal_id": queue.get("goal_id"),
        "source_queue_sha256": queue_hash,
        "items": [
            {"review_id": row["review_id"], "preview_first": row["source_frames"][0], "preview_last": row["source_frames"][-1]}
            for row in items
        ],
    }
    contract_hash = digest_document(contract)
    OUT.mkdir(parents=True)
    contract_path = OUT / "review-contract.json"
    contract_path.write_bytes(canonical_bytes(contract))
    page = OUT / "reviewer.html"
    page.write_text(page_source(items, parents, queue_hash, contract_hash), encoding="utf-8")
    manifest = {
        "schema": "motion-label-reviewer-v2",
        "complete": True,
        "items": len(items),
        "embedded_frames": sum(len(row["positions"]) for row in items),
        "queue_sha256": queue_hash,
        "review_contract_sha256": contract_hash,
        "review_contract_file_sha256": sha(contract_path),
        "builder_sha256": sha(HERE),
        "html_sha256": sha(page),
        "v1_html_sha256": sha(V1 / "reviewer.html"),
        "external_dependencies": False,
        "reviewed_items": 0,
        "physical_ground_truth": False,
        "model_training_authorized": False,
        "full_goal_complete": False,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
