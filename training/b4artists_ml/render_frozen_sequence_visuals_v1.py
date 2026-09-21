"""Research visuals of frozen failures; not animator or rig qualification."""
from pathlib import Path
import sys,os,json,hashlib,time
TR=Path(__file__).resolve().parent;ROOT=TR.parents[1];sys.path.insert(0,str(TR));os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation,PillowWriter
from semantic_motion_data import load_windows
from context_data import PARENTS
OUT=TR/'results/frozen-sequence-visuals-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(exist_ok=False);start=time.perf_counter();protocol=read(TR/'expanded_trajectory_protocol_v19.json');prior=TR/'results/sequence-development-v1';identities=read(prior/'window-identities.json');evidence=read(ROOT/'docs/b4artists_ml/goalposts/sequence-context-evidence-v1.json');selected=[('138_01','Marching'),('141_03','Run'),('141_04','Jump distances')]
 plan=dict(script_sha256=sha(Path(__file__)),selection='Earliest frame window for each named clip, gap32 with context; selected by identity, never by error. Existing exposed development only.',clips=selected,methods=['target','projected_shape','direct-20260909','direct-20260910'],source='Frozen original sequence-development-v1 projected outputs. No active tangent-model weights.',display='Canonical coordinates; common limits per case, fixed camera;17semantic joints, half-speed playback15fps. Excerpts, not full performances or native rig/mesh previews.',maximum_output_bytes=20000000,max_seconds=300,confirmation_read=False,human_assessed=False);(OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 windows=load_windows(TR,read(TR/'temporal_training_manifest_v19.json'),'validation',protocol);rows=[]
 for clip,label in selected:
  assert time.perf_counter()-start<300;w=min((w for w in windows if w['clip']==clip and w['gap']==32 and w['context']),key=lambda w:int(w['frame'][0]));identity=dict(clip=clip,gap=32,context=True,frames=w['frame'].tolist());part='new_validation';i=identities[part].index(identity);arrays=[w['target'].reshape(-1,17,9)[...,:3]];sources=[]
  for name in plan['methods'][1:]:
   p=prior/name/(part+'-'+str(i//16*16)+'.npz');rel=p.relative_to(ROOT).as_posix();assert sha(p)==evidence['artifacts'][rel]
   with np.load(p,allow_pickle=False) as z:arrays.append(z[str(i%16)].reshape(-1,17,9)[...,:3])
   sources.append(dict(path=rel,sha256=sha(p),array=str(i%16)))
  allp=np.concatenate(arrays).reshape(-1,3);middle=(allp.max(0)+allp.min(0))/2;radius=max(float(np.ptp(allp,axis=0).max())*.56,.2);fig=plt.figure(figsize=(12,4.1),facecolor='#f7f7f7');axes=[];artists=[];titles=['Reference motion','Procedural shape','Previous direct / seed 1','Previous direct / seed 2'];colors=['#253b53','#168772','#be6835','#7b5e99']
  for j,title in enumerate(titles):
   ax=fig.add_subplot(1,4,j+1,projection='3d');ax.set_title(title,fontsize=10);ax.set_xlim(middle[0]-radius,middle[0]+radius);ax.set_ylim(middle[1]-radius,middle[1]+radius);ax.set_zlim(middle[2]-radius,middle[2]+radius);ax.set_box_aspect((1,1,1));ax.view_init(elev=12,azim=-60);ax.set_axis_off();lines=[ax.plot([],[],[],color=colors[j],linewidth=2)[0] for k,p in enumerate(PARENTS) if p>=0];axes.append(ax);artists.append(lines)
  fig.suptitle(label+' | fixed research excerpt | previous models failed quality gates',fontsize=12,y=.98);caption=fig.text(.5,.05,'',ha='center',fontsize=9);fig.subplots_adjust(left=.01,right=.99,bottom=.10,top=.87,wspace=.02)
  def update(frame):
   for points,lines in zip(arrays,artists):
    for (k,parent),line in zip([(k,p) for k,p in enumerate(PARENTS) if p>=0],lines):
     pair=points[frame,[parent,k]];line.set_data(pair[:,0],pair[:,1]);line.set_3d_properties(pair[:,2])
   caption.set_text('Source frame '+str(int(w['frame'][frame]))+' | half speed | shared view and scale | positional skeletons only')
   return [line for lines in artists for line in lines]+[caption]
  update(len(arrays[0])//2);png=OUT/(clip+'-middle.png');fig.savefig(png,dpi=120);gif=OUT/(clip+'.gif');animation=FuncAnimation(fig,update,frames=len(arrays[0]),interval=1000/15,blit=False);animation.save(gif,writer=PillowWriter(fps=15),dpi=90);plt.close(fig);assert sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())<20000000;rows.append(dict(clip=clip,label=label,identity=identity,sources=sources,png=png.relative_to(ROOT).as_posix(),png_sha256=sha(png),gif=gif.relative_to(ROOT).as_posix(),gif_sha256=sha(gif)));print(json.dumps(dict(clip=clip,seconds=time.perf_counter()-start)),flush=True)
 assert all(not (TR/'cache'/(n+'.bvh')).exists() for n in read(TR/'temporal_expansion_plan_v19.json')['planned_splits']['confirmation'])
 result=dict(complete=True,cases=rows,plan_sha256=sha(OUT/'plan.json'),seconds=time.perf_counter()-start,bytes=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file()),active_training_weights_read=False,confirmation_read=False,human_assessed=False,full_goal_complete=False);(OUT/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(complete=True,cases=len(rows),bytes=result['bytes'])),flush=True)
if __name__=='__main__':main()
