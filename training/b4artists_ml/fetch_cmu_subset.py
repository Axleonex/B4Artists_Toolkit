"""Download only the pinned, bounded CMU BVH research subset; never the whole repository."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parent
COMMIT='09a07f54f3bbb58797325f009282d0b2048a2871'
BASE='https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/'+COMMIT+'/'
SPLITS={
 'train':['07_01','07_04','08_01','09_01','09_05','13_01','13_07','13_10','13_17','13_26','13_29'],
 'validation':['08_04','13_08','13_12','13_19'],
 'test':['16_01','16_17','35_01','35_17','13_20'],
}
MAX_BYTES=30*1024*1024

def main():
    cache=ROOT/'cache';cache.mkdir(exist_ok=True)
    manifest_path=ROOT/'data_manifest.json'
    previous=json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    expected={r['clip']:r for r in previous['files']} if previous else {}
    rows=[];total=0
    for split,clips in SPLITS.items():
        for clip in clips:
            path=f'data/{int(clip.split("_")[0]):03d}/{clip}.bvh'
            target=cache/(clip+'.bvh')
            if target.exists():
                data=target.read_bytes()
            else:
                with urllib.request.urlopen(BASE+path,timeout=40) as response:
                    data=response.read(min(8*1024*1024,MAX_BYTES-total)+1)
            total+=len(data)
            if total>MAX_BYTES or len(data)>8*1024*1024:
                raise RuntimeError('CMU subset exceeds announced download budget')
            if not data.lstrip().startswith(b'HIERARCHY'):
                raise ValueError('Unexpected motion file: '+clip)
            if clip in expected and hashlib.sha256(data).hexdigest()!=expected[clip]['sha256']:
                raise ValueError('Pinned manifest checksum differs: '+clip)
            if not target.exists():
                target.write_bytes(data)
            rows.append(dict(clip=clip,split=split,url=BASE+path,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
            print(split,clip,len(data),flush=True)
    manifest=dict(schema=1,commit=COMMIT,total_bytes=total,files=rows,
                  publisher='Carnegie Mellon University Graphics Lab',
                  original_terms='https://mocap.cs.cmu.edu/',
                  conversion_terms=BASE+'READMEFIRST.txt',
                  conversion='Bruce Hahne MotionBuilder BVH 2010; mirrored by una-dinosauria',
                  exclusions='No finger labels; added first T-pose frame excluded; raw motions not in addon ZIP')
    (ROOT/'data_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('Total bytes',total)

if __name__=='__main__':
    main()
