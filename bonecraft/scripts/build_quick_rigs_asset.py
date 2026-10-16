"""Rebuild boneforge/assets/quick_rigs.blend from Quick Rig's own humanoid.

Usage (from bonecraft/):
    bforartists --background --factory-startup --python scripts/build_quick_rigs_asset.py
"""
import os
import sys
import json

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from boneforge.autorig import quick_human as qh   # noqa: E402
from boneforge.autorig import rig_assets as ra    # noqa: E402

def skeleton_preview(arm, group, needs_rigify):
    """Draw the actual rest skeleton; no stock icons or guessed silhouettes.

    Software rasterization keeps asset rebuilding deterministic and headless.
    Humans face forward; animals are shown from the side. A dependency label
    is baked into each thumbnail, while its name is drawn by the native shelf.
    """
    size = 256
    axes = (0, 2) if group == 'humans' else (1, 2)
    segments = [(tuple(b.head_local[a] for a in axes), tuple(b.tail_local[a] for a in axes))
                for b in arm.data.bones]
    points = [p for line in segments for p in line]
    lo = [min(p[a] for p in points) for a in range(2)]
    hi = [max(p[a] for p in points) for a in range(2)]
    scale = min(216 / max(hi[0] - lo[0], .01), 185 / max(hi[1] - lo[1], .01))
    center = [(lo[a] + hi[a]) / 2 for a in range(2)]
    pixels = [.035, .045, .065, 1.] * (size * size)
    orange = (.95, .47, .08, 1.)

    def dot(x, y, radius=1):
        x, y = round(x), round(y)
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius and 0 <= x + dx < size and 0 <= y + dy < size:
                    at = ((y + dy) * size + x + dx) * 4
                    pixels[at:at + 4] = orange

    def project(p):
        return (128 + (p[0] - center[0]) * scale, 145 + (p[1] - center[1]) * scale)

    for head, tail in segments:
        p, q = project(head), project(tail)
        steps = max(1, int(max(abs(q[a] - p[a]) for a in range(2)) * 2))
        for n in range(steps + 1):
            dot(*(p[a] + (q[a] - p[a]) * n / steps for a in range(2)))

    font = {
        'R': ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
        'I': ['111', '010', '010', '010', '010', '010', '111'],
        'G': ['01110', '10001', '10000', '10111', '10001', '10001', '01110'],
        'F': ['11111', '10000', '10000', '11110', '10000', '10000', '10000'],
        'Y': ['10001', '10001', '01010', '00100', '00100', '00100', '00100'],
        'B': ['11110', '10001', '10001', '11110', '10001', '10001', '11110'],
        'A': ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
        'S': ['01111', '10000', '10000', '01110', '00001', '00001', '11110'],
        'C': ['01111', '10000', '10000', '10000', '10000', '10000', '01111'],
    }
    text = 'RIGIFY' if needs_rigify else 'BASIC'
    x = (size - sum((len(font[c][0]) + 1) * 4 for c in text)) // 2
    for c in text:
        glyph = font[c]
        for y, row in enumerate(glyph):
            for column, on in enumerate(row):
                if on == '1':
                    for dy in range(4):
                        for dx in range(4):
                            dot(x + column * 4 + dx, 12 + (6 - y) * 4 + dy, 0)
        x += (len(glyph[0]) + 1) * 4
    preview = arm.preview_ensure()
    preview.image_size = (size, size)
    preview.image_pixels_float = pixels


def main():
    # Only enable Rigify in the factory-startup asset-build process. Installation
    # does not activate the user's Rigify or save their preferences.
    if not qh.enable_rigify_if_available():
        raise RuntimeError("Rigify must be installed to rebuild the complete starter library")
    starters = [{"rig_name": "fallback", "op_id": qh.FALLBACK_OP_ID,
                 "label": "Basic Humanoid", "asset_name": ra.ASSET_NAME,
                 "group": "humans", "requires_rigify": False}]
    starters += [dict(r, asset_name=r['label'], requires_rigify=True)
                 for r in qh.discover_rigify_metarigs()]
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for starter in starters:
        if starter['requires_rigify']:
            module, name = starter['op_id'].split('.', 1)
            getattr(getattr(bpy.ops, module), name)()
            arm = bpy.context.active_object
        else:
            arm = qh._build_fallback_skeleton(bpy.context)
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        arm.name = starter['asset_name']
        arm.data.name = starter['asset_name']
        arm[qh.DROPPED_RIG_PROP] = starter['rig_name']
        arm.asset_mark()
        arm.asset_data.description = (
            ("Requires Rigify. Choose this starter to enable Rigify and add it. "
             if starter['requires_rigify'] else "No Rigify required. ")
            + "Starter skeleton: fit to your mesh before generating controls or weighting.")
        arm.asset_data.catalog_id = ra.CATALOGS[starter['group']][0]
        arm.asset_data.tags.new(ra.ASSET_TAG)
        skeleton_preview(arm, starter['group'], starter['requires_rigify'])
    with open(os.path.join(ra.assets_dir(), 'starter_rigs.json'), 'w', encoding='utf-8') as f:
        json.dump(starters, f, indent=2)
        f.write('\n')
    with open(os.path.join(ra.assets_dir(), 'blender_assets.cats.txt'), 'w', encoding='utf-8') as f:
        f.write('# BoneCraft starter rig catalogs\nVERSION 1\n\n')
        for catalog_id, label in dict.fromkeys(ra.CATALOGS.values()):
            f.write(f'{catalog_id}:{label}:{label}\n')
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=ra.asset_file(), compress=True)
    print('WROTE', ra.asset_file(), 'STARTERS', len(starters))


if __name__ == '__main__':
    main()
