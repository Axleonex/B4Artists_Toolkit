"""Bounded second CMU subset. Confirmation values remain unread until explicit freeze.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import argparse
import hashlib
import json
import urllib.request
from train_limb_prior import ROOT
from fetch_cmu_subset import BASE

SPLITS={
 'train':['15_06','15_08','17_01','17_10','18_08','18_04','26_02','26_10','36_01','38_03','49_02','49_04'],
 'validation':['28_01','28_02'],
 'confirmation':['29_01','29_03'],
}
MAX_ADDITIONAL_BYTES=30_000_000


def fetch(include_confirmation=False,frozen_sha256=None):
    if include_confirmation and (not frozen_sha256 or len(frozen_sha256)!=64):
        raise ValueError('Confirmation requires a frozen model checksum')
    mp=ROOT/'expansion_manifest.json'
    previous=json.loads(mp.read_text()) if mp.exists() else {}
    expected={r['clip']:r for r in previous.get('files',[])}
    prior=[]
    for name in ('data_manifest.json','confirmation_manifest.json','proportion_confirmation_manifest.json'):
        prior.extend(json.loads((ROOT/name).read_text())['files'])
    if {c for clips in SPLITS.values() for c in clips}&{r['clip'] for r in prior}:
        raise ValueError('Expansion overlaps previous data')
    rows=[];total=0
    for split,clips in SPLITS.items():
        if split=='confirmation' and not include_confirmation:
            continue
        for clip in clips:
            path=ROOT/'cache'/(clip+'.bvh');url=BASE+f'data/{int(clip.split("_")[0]):03d}/{clip}.bvh'
            if path.exists():data=path.read_bytes()
            else:
                with urllib.request.urlopen(url,timeout=40) as response:
                    data=response.read(min(8_000_000,MAX_ADDITIONAL_BYTES-total)+1)
            total+=len(data);sha=hashlib.sha256(data).hexdigest()
            if total>MAX_ADDITIONAL_BYTES or len(data)>8_000_000 or not data.lstrip().startswith(b'HIERARCHY'):
                raise ValueError('Expansion data exceeds budget or has invalid format')
            if clip in expected and expected[clip]['sha256']!=sha:
                raise ValueError('Pinned expansion data changed')
            if not path.exists():path.write_bytes(data)
            rows.append(dict(clip=clip,split=split,url=url,bytes=len(data),sha256=sha))
            print(split,clip,len(data),flush=True)
    # Do not erase an existing confirmation record when reproducing training fetch.
    for row in previous.get('files',[]):
        if row['split']=='confirmation' and not include_confirmation:rows.append(row)
    result=dict(schema=1,files=rows,additional_raw_bytes=sum(r['bytes'] for r in rows),
        combined_raw_bytes=sum(r['bytes'] for r in prior)+sum(r['bytes'] for r in rows),
        additional_budget_bytes=MAX_ADDITIONAL_BYTES,
        confirmation_frozen_sha256=frozen_sha256 or previous.get('confirmation_frozen_sha256'),
        planned_splits=SPLITS,publisher_terms='https://mocap.cs.cmu.edu/',conversion_terms=BASE+'READMEFIRST.txt')
    mp.write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    args=argparse.ArgumentParser();args.add_argument('--confirmation-frozen-sha256')
    parsed=args.parse_args()
    result=fetch(bool(parsed.confirmation_frozen_sha256),parsed.confirmation_frozen_sha256)
    print('EXPANSION_BYTES',result['additional_raw_bytes'],'COMBINED_BYTES',result['combined_raw_bytes'],flush=True)
