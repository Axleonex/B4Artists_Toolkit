"""Project-only implementation-progress extension; final quality scoring is canonical."""
import copy, time

def evaluate(state, observations, root, *, now=None):
    from prime_bridge import goalposts as canonical
    now=time.time() if now is None else now
    trial=copy.deepcopy(state)
    declared={v['id'] for v in trial['contract']['progress_milestones']}
    milestones=observations.get('milestones',{})
    if set(milestones)-declared:raise ValueError('Undeclared progress milestone')
    current=canonical.fingerprint(root,trial['contract']['inputs'])
    passing={k for k,v in milestones.items() if canonical._proof(root,v,current,judgment=False,builder=trial['contract']['builder_id'])=='pass'}
    report=canonical.evaluate(trial,observations.get('quality',{}),root,now=now,milestone=True)
    regression=any(c['regression'] for c in report['categories'].values()) or bool(set(state['passed_endpoint'])-{k for k,v in report['endpoint'].items() if v=='pass'})
    old=set(state.get('passed_progress_milestones',[]))
    lost=old-passing
    gained=passing-old
    progress=bool(gained) and not regression and not lost
    report['canonical_decision']=report['decision'];report['canonical_reason']=report['reason']
    report['implementation_progress']=dict(passing=sorted(passing),new=sorted(gained),lost=sorted(lost),accepted=progress)
    if progress:
        trial['passed_progress_milestones']=sorted(old|passing)
        trial['stagnant_rounds']=report['stagnant_rounds']=0
        if report['decision']=='checkpoint' and report['reason']=='no measurable progress; endpoint may be infeasible':
            report['decision']='iterate';report['reason']='Verified implementation milestone advanced; final endpoint and quality gates remain unmet';trial['status']='active'
    if lost and report['decision']=='complete':
        report['decision']='checkpoint';report['reason']='Previously verified implementation milestone regressed';trial['status']='checkpoint'
    # Canonical max-wall/max-goalposts stops and completion requirements stay authoritative.
    trial['history'][-1]=report
    state.clear();state.update(trial)
    return report

if __name__=='__main__':
    import argparse,json,sys
    from pathlib import Path
    parser=argparse.ArgumentParser();parser.add_argument('--workspace',type=Path,required=True);parser.add_argument('--state',required=True);parser.add_argument('--observations',required=True);parser.add_argument('--canonical-root',required=True);args=parser.parse_args()
    sys.path.insert(0,args.canonical_root)
    from prime_bridge.goalposts import local_file,markdown
    path=local_file(args.workspace,args.state);state=json.loads(path.read_text());observations=json.loads(local_file(args.workspace,args.observations).read_text())
    report=evaluate(state,observations,args.workspace);path.write_text(json.dumps(state,indent=2)+'\n');path.with_suffix('.md').write_text(markdown(report));print(json.dumps(report,indent=2))
