"""Package the starter catalog for review without replacing a published release."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'releases' / 'BoneCraft-BFA-9.1.2-starter-catalog-candidate.zip'
OUT.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted((ROOT / 'boneforge').rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        if path.suffix in {'.pyc', '.pyo', '.blend1', '.blend2'}:
            continue
        archive.write(path, path.relative_to(ROOT).as_posix())
    manifest = 'boneforge/assets/starter_rigs.json'
    assert manifest in archive.namelist()
    assert 'boneforge/autorig/rig_asset_ops.py' in archive.namelist()
print(OUT)
