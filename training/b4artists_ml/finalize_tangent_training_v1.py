"""Document completed fixed fits without implying development qualification."""
from pathlib import Path
import json,hashlib
TR=Path(__file__).resolve().parent;ROOT=TR.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 base=TR/'results/sequence-tangent-training-v1';assert read(base/'active-process.json')['all_complete'];rows=[]
 for seed in (20260909,20260910):
  r=read(base/('direct-'+str(seed))/'report.json');q=read(TR/('results/sequence-tangent-provider-'+str(seed))/'report.json');assert r['complete'] and r['completed_epochs']==60 and q['passed'] and q['tests']==6;assert not r['validation_read'] and not r['confirmation_read'];rows.append(r)
 table=['| Seed | Final training loss | Fit seconds | CPU export maximum error |','|---|---:|---:|---:|']
 for r in rows:table.append(f"| {r['seed']} | {r['history'][-1]['mean_training_loss']:.6f} | {r['training_seconds']:.1f} | {r['cpu_export_max_abs_error']:.3g} |")
 text='''# Controlled tangent-conditioned sequence training

Both fixed direct-model seeds completed 60 epochs. Development quality has not yet been evaluated, and no model is bundled or promoted. Training loss and inference contracts do not establish motion quality or Cascadeur parity.

The experiment adds 272 explicit authored-tangent channels to the 394-channel condition. The backbone and its original parameters are initialized identically to the earlier model for each seed; added input columns start at zero. The resulting model has 819,737 parameters. Data, targets, masks, baseline, optimizer, batch schedule, loss and original acceptance gates remain fixed. This tests the conditioning configuration and its added input weights; it does not independently isolate feature information from added parameter capacity.

'''+ '\n'.join(table)+'''

Each fit used the same 5,778 training windows from 78 existing clips. All original cached arrays were checked unchanged before appending features in RAM. The augmented arrays total 984,750,156 bytes. No new motion files or persistent feature cache were acquired. Each fit retained the declared 1,800-second optimization limit, 600-second preparation limit and memory caps. Brief CPU rendering overlapped the first fit; these durations are not a controlled training-throughput comparison.

Nontrivial synthetic PyTorch/NumPy portability passed in actual Bforartists at 2, 33 and 120 frames, including exact known values and deterministic repeat output. The native process still returned 3221225477 after writing successful assertions; clean host exit remains unqualified. Trained weights additionally passed CPU export agreement and six synthetic inference contracts per seed: exact endpoints, query order, unused-context isolation, stationary holds, cache ownership and invalid-input rejection. The first portability attempt failed on the embedded interpreter's import path; both the attempt and corrected harness are preserved.

Run `training/b4artists_ml/evaluate_sequence_tangent_v2.py` next. It freezes both completed models before loading development windows and requires exact reproduction of the original projected controls. Both seeds must pass every existing old/new/combined gate. No favorable-seed selection, confirmation access or additional fit is authorized by a training pass. The six confirmation clips remain sealed.

The original evaluation-plan copy retained an inherited four-fit caption and timestamp. Version 2 corrects only those descriptions before evaluation; model identities, settings, reference hashes, metrics and gates remain unchanged. The fit plan's inherited created_at field identifies its source corpus plan; the actual fit-plan freeze timestamp is recorded in results/sequence-tangent-training-v1/frozen-plan.json.

[Prior frozen-model visual comparisons](FROZEN-MOTION-COMPARISONS-v1.md) provide marching, running and jumping excerpts. They do not use these newly trained models and are not independent human assessments. The full contact, intent, physics, rig, responsiveness, usability and equivalent Cascadeur requirements remain open.

The prepared `profile_private_phases_v1.py` has not been executed. It should run serially after training and development evaluation, to attribute remaining long preview ticks without changing production code. The existing 0.19.1 package remains the tested experimental release.
'''
 p=ROOT/'docs/b4artists_ml/TANGENT-SEQUENCE-TRAINING-v1.md';assert not p.exists();p.write_text(text,encoding='utf-8');print('Training documentation finalized; development pending')
if __name__=='__main__':main()
