"""Evaluated skeletal frames for limits; never writes mechanism/deform bones.
SPDX-License-Identifier: GPL-2.0-or-later
"""
from . import posing as p


def bind(obj,binding):
    """Return verified control -> (skeletal bone, skeletal parent) associations.

    Generated Rigify body mechanisms are not treated as anatomical parents.
    Only actual deform/FK chains and explicitly mapped ORG chains are exposed.
    """
    mapped={}
    for name in binding['rotations']+binding['effectors']:
        bone=obj.data.bones[name]
        if bone.use_deform and bone.parent and bone.parent.use_deform:
            mapped[name]=name
    _,_,limbs=p.bindings(obj)
    for row in limbs:
        mapped.update(zip(row['fk'],row['joints']))
    if binding['profile']=='Rigify Generated':
        mapped[binding['effectors'][0]]=binding['names'][4]
        # A generated neck control governs a distributed neck chain. The head
        # bound uses its actual terminal neck parent; no fabricated joint here.
    result={}
    for control,joint in mapped.items():
        bone=obj.data.bones[joint];parent=bone.parent
        physical=lambda b: b.use_deform or b.name.startswith('ORG-')
        if parent and physical(bone) and physical(parent):
            result[control]=(joint,parent.name)
    return result


def rest_relative(obj,pair):
    joint,parent=pair
    return obj.data.bones[parent].matrix_local.to_quaternion().inverted()@obj.data.bones[joint].matrix_local.to_quaternion()


def rotation(obj,pair,rest):
    """Rest-corrected child/parent rotation in the child's rest-local axes."""
    joint,parent=pair
    child=obj.pose.bones[joint].matrix.to_quaternion()
    q=rest.inverted()@obj.pose.bones[parent].matrix.to_quaternion().inverted()@child
    q.normalize()
    return q
