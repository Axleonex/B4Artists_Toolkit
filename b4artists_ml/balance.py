"""Immutable authored static-balance requests and original-rig measurements.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import math
import copy
import numpy as np
from mathutils import Matrix,Quaternion,Vector
from . import support_math as sm,balance_math as bm

INDICES={'arm-L':7,'arm-R':10,'leg-L':13,'leg-R':16}


def request(obj,scene):
    state=obj.b4ml
    if not state.body_balance or state.body_balance_strength==0:return None
    from . import motion_layer
    offset=motion_layer.offset(obj)
    dynamic=bool(getattr(state,'body_balance_dynamic',False))
    result=dict(schema=2 if dynamic else 1,strength=state.body_balance_strength,inset=state.body_balance_inset,
        free_pelvis=state.body_balance_free_pelvis,plane=list(Vector(state.support_plane_point)-offset),normal=list(state.support_plane_normal),
        gravity=list(scene.gravity) if scene.use_gravity else [0.,0.,0.],
        tolerance=state.support_tolerance,rotation_tolerance=state.support_rotation_tolerance,
        frame=scene.frame_current+scene.frame_subframe,
        masses=[dict(name=i.name,weight=i.weight,fraction=i.fraction) for i in state.mass_segments],
        contacts=[dict(limb=i.limb,start=i.start,end=i.end,strength=i.strength,point=list(Vector(i.point)-offset),rotation=list(i.rotation),
            offset=list(i.offset),width=i.support_width,length=i.support_length,heading=i.support_heading)
            for i in state.contacts if i.enabled and i.use_support])
    if dynamic:result['velocity']=list(state.body_balance_velocity)
    return result


class Constraint:
    def __init__(self,session,raw,targets,mask,orientations):
        from .support import SEGMENTS
        if not isinstance(raw,dict) or raw.get('schema') not in (1,2):raise ValueError('Unsupported balance request')
        raw=copy.deepcopy(raw)
        self.s=session;self.names=session.binding['names'];self.raw=raw
        self.dynamic=raw['schema']==2
        if raw.get('frame')!=sum(session.frame):raise ValueError('Balance contacts must use the current preview frame')
        reference=np.asarray(getattr(session,'balance_reference',None),dtype=float)
        if reference.shape!=(17,4,4) or not np.isfinite(reference).all():
            raise ValueError('Start a new whole-body preview to initialize balance reference transforms')
        if not np.allclose(reference[:,3,:],[0.,0.,0.,1.],atol=1e-7) or np.max(np.abs(reference[:,:3,3]-session.world_points(session.baseline)))>5e-6*max(session.scale,1.):
            raise ValueError('Saved balance reference does not match the preview pose')
        if type(raw.get('free_pelvis')) is not bool:raise ValueError('Choose whether the pelvis may move')
        for key in ('strength','inset','tolerance','rotation_tolerance','frame'):
            if not isinstance(raw.get(key),(int,float)) or not math.isfinite(raw[key]):raise ValueError('Balance settings must be finite')
        if not 0<raw['strength']<=1 or raw['inset']<0 or raw['tolerance']<=0 or not 0<raw['rotation_tolerance']<=math.pi:
            raise ValueError('Invalid balance strength, inset or tolerances')
        self.origin=sm.vector(raw['plane']);self.normal,self.u,self.v=sm.plane_basis(raw['normal'])
        gravity=sm.vector(raw['gravity']);g=float(np.linalg.norm(gravity))
        if g<1e-12 or np.linalg.norm(gravity/g+self.normal)>1e-6:
            raise ValueError('Static balance correction requires nonzero gravity normal into the support plane')
        masses=raw.get('masses',[])
        if [m['name'] for m in masses]!=[v[0] for v in SEGMENTS]:raise ValueError('Initialize the full humanoid mass model')
        heads=reference[:,:3,3]
        tails=np.array([m[:3,3]+m[:3,1]*session.obj.data.bones[name].length for m,name in zip(reference,self.names)])
        starts=[heads[a] for _,a,b,w in SEGMENTS];ends=[heads[b] if b is not None else tails[a] for _,a,b,w in SEGMENTS]
        self.before,_,weights=sm.center_of_mass(starts,ends,[m['weight'] for m in masses],[m['fraction'] for m in masses])
        self.head_weights=np.zeros(17);self.tail_weights=np.zeros(17)
        for (_,a,b,_),weight,mass in zip(SEGMENTS,weights,masses):
            f=mass['fraction'];self.head_weights[a]+=weight*(1-f)
            if b is None:self.tail_weights[a]+=weight*f
            else:self.head_weights[b]+=weight*f
        self.terminals=np.flatnonzero(self.tail_weights)
        self.contacts=[];vertices=[];used=set()
        if len(raw.get('contacts',[]))>32:raise ValueError('Limit balance analysis to 32 authored contacts')
        if raw['free_pelvis']:mask[0]=False
        for row in raw.get('contacts',[]):
            if not all(isinstance(row.get(k),(float,int)) and math.isfinite(row[k]) for k in ('start','end','strength')) or row['start']>row['end']:
                raise ValueError('Invalid balance contact interval')
            if not row['start']<=raw['frame']<=row['end']:continue
            if not 1.-1e-6<=row['strength']<=1:raise ValueError('Support contact strength must be one during its hold')
            index=INDICES.get(row['limb'])
            if index is None or index in used:raise ValueError('One active support interval per mapped hand or foot is required')
            used.add(index);point=sm.vector(row['point']);offset=sm.vector(row['offset']);m=reference[index]
            q=np.asarray(row['rotation'],dtype=float)
            if q.shape!=(4,) or not np.isfinite(q).all() or abs(float(np.linalg.norm(q))-1)>1e-4:
                raise ValueError('Support orientation must be a unit quaternion')
            q=q/np.linalg.norm(q);captured=Quaternion(q);original=Matrix(m.tolist()).to_quaternion()
            angle=2*math.acos(min(1.,abs(float(original.dot(captured)))))
            if np.linalg.norm(m[:3,:3]@offset+m[:3,3]-point)>raw['tolerance'] or angle>raw['rotation_tolerance']:
                raise ValueError('Support capture does not match the starting pose; recapture '+row['limb'])
            if abs(float((point-self.origin)@self.normal))>raw['tolerance']:
                raise ValueError('Support contact is off the authored plane')
            lengths=np.linalg.norm(m[:3,:3],axis=0);axes=m[:3,:3]/lengths
            if min(lengths)<1e-10 or np.linalg.det(axes)<=0 or not np.allclose(axes.T@axes,np.eye(3),atol=1e-4):
                raise ValueError('Support effector scale/shear requires another adapter')
            target=point-np.asarray(captured.to_matrix())@(lengths*offset)
            if mask[index] and np.linalg.norm(targets[index]-target)>2e-4*session.scale:
                raise ValueError('Pinned target conflicts with support contact: '+row['limb'])
            if index in orientations and 2*math.acos(min(1.,abs(float(captured.dot(Quaternion(orientations[index]))))))>.001:
                raise ValueError('Pinned orientation conflicts with support contact: '+row['limb'])
            if not mask[index]:targets[index]=target
            if index not in orientations:orientations[index]=q.tolist()
            mask[index]=True
            center=point-self.normal*((point-self.origin)@self.normal)
            vertices.extend(sm.patch_vertices(center,self.normal,row['width'],row['length'],row['heading']))
            self.contacts.append(dict(index=index,point=point,offset=offset,rotation=q))
        if not self.contacts:raise ValueError('Capture at least one active support patch before balance correction')
        self.vertices=np.asarray(vertices)
        coords=np.column_stack(((self.vertices-self.origin)@self.u,(self.vertices-self.origin)@self.v))
        self.hull=bm.inset_hull(coords,raw['inset'])
        baseline=self.project(self.before);nearest=bm.closest_in_hull(baseline,self.hull)
        if self.dynamic:
            velocity=sm.vector(raw.get('velocity'))
            self.capture_point,self.time_constant,self.capture_height,self.planar_velocity=bm.capture_point(
                self.before,velocity,gravity,self.origin,self.normal,self.u,self.v)
            self.capture_target=bm.closest_in_hull(self.capture_point,self.hull)
            self.capture_goal=self.capture_point+(self.capture_target-self.capture_point)*raw['strength']
            self.target=self.capture_goal-self.planar_velocity*self.time_constant
        else:
            self.capture_point=self.capture_target=self.capture_goal=None
            self.time_constant=self.capture_height=None
            self.planar_velocity=np.zeros(2)
            self.target=baseline+(nearest-baseline)*raw['strength']
        if (self.before-self.origin)@self.normal < -raw['tolerance']:raise ValueError('Starting COM is below the support plane')
        self.before_margin=sm.support_analysis(self.before,self.vertices,self.origin,self.normal,raw['gravity'],raw['tolerance'])['margin']

    def project(self,point):return np.array(((point-self.origin)@self.u,(point-self.origin)@self.v))

    def com(self,obj,points_world=None):
        if points_world is None:points_world=np.array([obj.matrix_world@obj.pose.bones[n].head for n in self.names])
        result=self.head_weights@points_world
        for i in self.terminals:result+=self.tail_weights[i]*np.array(obj.matrix_world@obj.pose.bones[self.names[i]].tail)
        return result

    def residual(self,obj,points_world):
        com=self.com(obj,points_world)
        if self.dynamic:
            capture,_,_,_=bm.capture_point(
                com,sm.vector(self.raw.get('velocity')),sm.vector(self.raw['gravity']),
                self.origin,self.normal,self.u,self.v)
            return (capture-self.capture_goal)/self.s.scale
        return (self.project(com)-self.target)/self.s.scale

    def verify(self,obj):
        com=self.com(obj);error=float(np.linalg.norm(self.project(com)-self.target))/self.s.scale
        drift=0.;angle=0.
        for contact in self.contacts:
            matrix=obj.matrix_world@obj.pose.bones[self.names[contact['index']]].matrix
            drift=max(drift,float(np.linalg.norm(np.array(matrix@Vector(contact['offset']))-contact['point']))/self.s.scale)
            angle=max(angle,2*math.acos(min(1.,abs(float(matrix.to_quaternion().dot(Quaternion(contact['rotation'])))))))
        report=sm.support_analysis(com,self.vertices,self.origin,self.normal,self.raw['gravity'],self.raw['tolerance'])
        capture_error=None;capture_report=report
        if self.dynamic:
            actual_capture,actual_time_constant,actual_height,_=bm.capture_point(
                com,sm.vector(self.raw.get('velocity')),sm.vector(self.raw['gravity']),
                self.origin,self.normal,self.u,self.v)
            capture_error=float(np.linalg.norm(actual_capture-self.capture_goal))/self.s.scale
            error=capture_error
            capture_world=self.origin+self.u*actual_capture[0]+self.v*actual_capture[1]
            capture_report=sm.support_analysis(capture_world,self.vertices,self.origin,self.normal,self.raw['gravity'],self.raw['tolerance'])
        if error>2e-4 or drift>2e-4 or angle>.001 or report['plane_height'] < -self.raw['tolerance']:
            label='Dynamic balance' if self.dynamic else 'Static balance'
            raise ValueError(f'{label} did not satisfy the original rig: COM={error:.6g}, contact={drift:.6g}, angle={angle:.6g}')
        if self.dynamic and (capture_error>2e-4 or capture_report['plane_height'] < -self.raw['tolerance']):
            raise ValueError(f'Dynamic balance did not satisfy the capture target: error={capture_error:.6g}')
        result=dict(com_error=error,contact_error=drift,contact_rotation_error=angle,before_com=self.before.tolist(),
            after_com=com.tolist(),target_projection=(self.origin+self.u*self.target[0]+self.v*self.target[1]).tolist(),
            before_margin=self.before_margin if not self.dynamic else sm.support_analysis(
                self.origin+self.u*self.capture_point[0]+self.v*self.capture_point[1],self.vertices,self.origin,self.normal,
                self.raw['gravity'],self.raw['tolerance'])['margin'],
            after_margin=capture_report['margin'] if self.dynamic else report['margin'],
            status=capture_report['status'] if self.dynamic else report['status'],
            strength=self.raw['strength'],inset=self.raw['inset'],free_pelvis=self.raw['free_pelvis'],contacts=len(self.contacts),
            static_only=True)
        if self.dynamic:
            result.update(schema=2,dynamic=True,static_only=False,
                capture_point=(self.origin+self.u*self.capture_point[0]+self.v*self.capture_point[1]).tolist(),
                capture_target=(self.origin+self.u*self.capture_target[0]+self.v*self.capture_target[1]).tolist(),
                capture_error=capture_error,time_constant=actual_time_constant,
                capture_height=actual_height)
        return result
