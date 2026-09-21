"""Write a self-contained visual comparison; derived research poses stay in ignored cache.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import json
from train_limb_prior import ROOT
from context_data import load_examples,finish,PARENTS
from context_projection import project_pose_newton
from evaluate_context_projection import models


def main():
    manifest=json.loads((ROOT/'context_confirmation_manifest.json').read_text());predictors=models();cases=[]
    for mode in ('neutral','prior'):
        for clip,d in load_examples(ROOT,manifest,'confirmation',seed=20260908,augment=False,mode=mode):
            poses={}
            for key in ('starting_pose','mlp'):
                raw=finish(predictors[key](d['x']),d['baseline'],d['target'],d['mask'])
                result,stats=project_pose_newton(raw,d['rest'],d['target'],d['mask'])
                poses[key]=result.round(6).tolist()
            cases.append(dict(name=clip+' / '+mode,frames=d['frame'].tolist(),pins=d['mask'].tolist(),
                              reference=d['target'].round(6).tolist(),**poses))
    payload=json.dumps(dict(cases=cases,parents=PARENTS),separators=(',',':'))
    html=HTML.replace('__DATA__',payload)
    target=ROOT/'cache/context-preview.html';target.write_text(html,encoding='utf-8')
    print('VISUAL_PREVIEW',target,'CASES',len(cases),'BYTES',target.stat().st_size)

HTML=r"""<!doctype html><meta charset="utf-8"><title>B4Artists contextual pose research</title>
<style>
body{font:15px system-ui;background:#131a23;color:#e7edf5;margin:24px}h1{font-size:23px;margin-bottom:8px}p{max-width:1000px;line-height:1.5;color:#bcc9d9}
.controls{display:flex;align-items:center;gap:16px;flex-wrap:wrap;padding:14px;background:#202b39;border-radius:8px}button,select{font:inherit;background:#32445a;color:white;padding:7px;border:1px solid #617890;border-radius:4px}.views{display:flex;gap:14px;margin-top:16px}.view{flex:1;min-width:0}h2{font-size:16px;font-weight:500}canvas{width:100%;height:480px;background:#1b2532;border-radius:8px}.hint{font-size:13px}input{vertical-align:middle}@media(max-width:800px){.views{flex-direction:column}canvas{height:330px}}
</style>
<h1>B4Artists contextual pose research</h1>
<p>Reference motion, geometric adjustment, and a trained 17-joint completion model with length projection. Green points are supplied targets. These are pelvis-relative poses solved independently at each frame. Playback does not demonstrate learned motion, contacts, physics, or real-rig application.</p>
<div class="controls"><select id="case"></select><button id="play">Play</button><label>Frame <input id="frame" type="range" min="0" value="0"><span id="number"></span></label><label>View <input id="yaw" type="range" min="-180" max="180" value="-25"></label></div>
<div class="views"><div class="view"><h2>Captured reference</h2><canvas id="reference"></canvas></div><div class="view"><h2>Geometric starting-pose adjustment</h2><canvas id="starting_pose"></canvas></div><div class="view"><h2>Learned completion + length projection</h2><canvas id="mlp"></canvas></div></div>
<p class="hint">Use the same view and frame for comparison. Look for torso and elbow choices, asymmetry, and frame-to-frame jumps. The captured pose is one possible answer; numerical reconstruction error alone does not establish visual plausibility. No Cascadeur comparison or animator acceptance has been recorded.</p>
<script>
const DATA=__DATA__;const choose=document.getElementById('case'),slider=document.getElementById('frame'),yaw=document.getElementById('yaw');let running=false;
DATA.cases.forEach((c,i)=>choose.add(new Option(c.name,i)));
function draw(){const c=DATA.cases[choose.value||0],frame=+slider.value;document.getElementById('number').textContent=' '+c.frames[frame];const angle=+yaw.value*Math.PI/180;
for(const key of ['reference','starting_pose','mlp']){const canvas=document.getElementById(key),ctx=canvas.getContext('2d');canvas.width=Math.round(canvas.clientWidth*devicePixelRatio);canvas.height=Math.round(canvas.clientHeight*devicePixelRatio);ctx.scale(devicePixelRatio,devicePixelRatio);const w=canvas.clientWidth,h=canvas.clientHeight,scale=Math.min(w/4.8,h/4.8);
const points=c[key][frame].map(p=>{const x=Math.cos(angle)*p[0]-Math.sin(angle)*p[1],depth=Math.sin(angle)*p[0]+Math.cos(angle)*p[1];return[w/2+x*scale,h*.44-(p[2]*.98-depth*.15)*scale]});
ctx.strokeStyle='#526276';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(8,h*.44);ctx.lineTo(w-8,h*.44);ctx.stroke();ctx.strokeStyle=key==='reference'?'#b7cadc':key==='mlp'?'#65b6fb':'#e4ae61';ctx.lineWidth=3;
DATA.parents.forEach((parent,j)=>{if(parent<0)return;ctx.beginPath();ctx.moveTo(...points[parent]);ctx.lineTo(...points[j]);ctx.stroke()});points.forEach((p,j)=>{ctx.fillStyle=c.pins[frame][j]?'#70e0a4':'#e0e7ef';ctx.beginPath();ctx.arc(...p,c.pins[frame][j]?5:3,0,Math.PI*2);ctx.fill()})}}
function reset(){slider.max=DATA.cases[choose.value||0].frames.length-1;slider.value=0;draw()}choose.onchange=reset;slider.oninput=draw;yaw.oninput=draw;window.onresize=draw;
document.getElementById('play').onclick=()=>{running=!running;document.getElementById('play').textContent=running?'Pause':'Play'};setInterval(()=>{if(running){slider.value=(+slider.value+1)%(+slider.max+1);draw()}},1000/15);reset();
</script>"""

if __name__=='__main__':main()
