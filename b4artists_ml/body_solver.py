"""Contextual position proposals projected through actual rig controls.
SPDX-License-Identifier: GPL-2.0-or-later
Host-verified proxy fitting reduces rig evaluation cost without changing the pose target.
"""
import time
import weakref
from importlib.resources import files
import numpy as np
import bpy
from mathutils import Vector,Quaternion
from . import posing as p,workflow as w,rig_state as rs
from . import joint_limits as limits,joint_frames
from .body_model import encode,JOINTS,forward,decode_model,MODEL_SHA256

_SESSIONS=weakref.WeakValueDictionary()
POLE_CHAINS={6:(5,6,7),9:(8,9,10),12:(11,12,13),15:(14,15,16)}
ORIENTATION_JOINTS=(0,4,7,10,13,16)
DISTRIBUTED_ORIENTATION_JOINTS=(1,2,3)
SUPPORTED_ORIENTATION_JOINTS=tuple(sorted(set(ORIENTATION_JOINTS+DISTRIBUTED_ORIENTATION_JOINTS)))
_TORSO_ROTATION_COUNTS={
    'BoneForge Control Rig':5,
    'Rigify Generated':7,
    'BoneForge Legacy / Rigify Metarig':6,
    'Mocap Humanoid':5,
    'Unity Humanoid':5,
    'Unreal Mannequin':5,
}

MAX_COUPLED_TORSO_PARAMETER_NORM=.35
MAX_COUPLED_PELVIS_SPINE_PARAMETER_NORM=.75
MAX_COUPLED_PELVIS_SPINE_CHEST_PARAMETER_NORM=.9


class CoupledTorsoError(ValueError):
    """The requested semantic Spine motion is not supported by the controls."""


def bounded_coupled_torso_update(jacobian,displacement,*,max_norm=MAX_COUPLED_TORSO_PARAMETER_NORM,
                                 damping=1e-4,rank_tolerance=1e-5):
    """Return a bounded minimum-norm update for ``J @ update ~= displacement``.

    The Jacobian is measured on the actual mapped rig.  The pelvis is not a
    parameter in this system: callers evaluate the semantic Spine relative to
    the pinned pelvis, so no hidden translation degree of freedom is invented.
    A rank of two is sufficient for the distance-constrained Spine point.
    """
    J=np.asarray(jacobian,dtype=float);d=np.asarray(displacement,dtype=float)
    if J.ndim!=2 or J.shape[0]!=3 or J.shape[1]<1:
        raise CoupledTorsoError('Coupled torso Jacobian must have shape (3, controls)')
    if d.shape!=(3,) or not np.isfinite(J).all() or not np.isfinite(d).all():
        raise CoupledTorsoError('Coupled torso parameterization requires finite inputs')
    if not np.isfinite(max_norm) or max_norm<=0 or not np.isfinite(damping) or damping<=0:
        raise CoupledTorsoError('Coupled torso bounds are invalid')
    U,singular,Vt=np.linalg.svd(J,full_matrices=False);scale=max(float(singular[0]),1e-12)
    rank=int(np.sum(singular>scale*rank_tolerance))
    if rank<2:raise CoupledTorsoError('Coupled Spine target has insufficient torso control rank')
    coefficients=(singular/(singular*singular+damping*damping))*(U.T@d)
    update=Vt.T@coefficients;norm=float(np.linalg.norm(update));clamped=norm>max_norm
    if clamped:update*=max_norm/norm
    projected=J@update
    return update,dict(rank=rank,singular_values=singular.tolist(),requested_norm=norm,
        applied_norm=float(np.linalg.norm(update)),clamped=bool(clamped),
        projected_norm=float(np.linalg.norm(projected)),residual_norm=float(np.linalg.norm(d-projected)))


def verify_coupled_torso_request(displacement,metrics,*,max_residual=.02):
    """Reject a large unreachable component before the nonlinear solver runs."""
    d=np.asarray(displacement,dtype=float)
    if d.shape!=(3,) or not np.isfinite(d).all():raise CoupledTorsoError('Coupled Spine displacement is invalid')
    if not isinstance(metrics,dict) or not np.isfinite(metrics.get('residual_norm',float('nan'))):
        raise CoupledTorsoError('Coupled torso metrics are invalid')
    if not np.isfinite(max_residual) or max_residual<=0:raise CoupledTorsoError('Coupled torso residual bound is invalid')
    bound=max(max_residual,float(np.linalg.norm(d))*.25)
    if metrics['residual_norm']>bound:
        raise CoupledTorsoError('Coupled Spine target is outside the verified torso control space '
                                f'(residual={metrics["residual_norm"]:.6g}, bound={bound:.6g})')
    return True


def _bounded_coupled_update(jacobian,displacement,*,max_norm,rank_tolerance=1e-5,damping=1e-4):
    """Solve a bounded multi-point coupled update from an actual-rig Jacobian."""
    J=np.asarray(jacobian,dtype=float);d=np.asarray(displacement,dtype=float)
    if J.ndim!=2 or J.shape[0]<1 or J.shape[1]<1 or d.shape!=(J.shape[0],):
        raise CoupledTorsoError('Coupled pelvis/Spine Jacobian shape is invalid')
    if not np.isfinite(J).all() or not np.isfinite(d).all():
        raise CoupledTorsoError('Coupled pelvis/Spine parameterization requires finite inputs')
    if not np.isfinite(max_norm) or max_norm<=0:
        raise CoupledTorsoError('Coupled pelvis/Spine bound is invalid')
    U,singular,Vt=np.linalg.svd(J,full_matrices=False);scale=max(float(singular[0]),1e-12)
    rank=int(np.sum(singular>scale*rank_tolerance))
    if rank<3:raise CoupledTorsoError('Coupled pelvis/Spine control rank is insufficient')
    coefficients=(singular/(singular*singular+damping*damping))*(U.T@d)
    update=Vt.T@coefficients;norm=float(np.linalg.norm(update));clamped=norm>max_norm
    if clamped:update*=max_norm/norm
    projected=J@update
    return update,dict(rank=rank,singular_values=singular.tolist(),requested_norm=norm,
        applied_norm=float(np.linalg.norm(update)),clamped=bool(clamped),
        projected_norm=float(np.linalg.norm(projected)),residual_norm=float(np.linalg.norm(d-projected)))


def _verify_coupled_pelvis_spine_request(displacement,metrics,*,max_residual=.02):
    d=np.asarray(displacement,dtype=float)
    if d.ndim!=1 or d.size!=6 or not np.isfinite(d).all():
        raise CoupledTorsoError('Coupled pelvis/Spine displacement is invalid')
    if not isinstance(metrics,dict) or not np.isfinite(metrics.get('residual_norm',float('nan'))):
        raise CoupledTorsoError('Coupled pelvis/Spine metrics are invalid')
    bound=max(max_residual,float(np.linalg.norm(d))*.25)
    if metrics['residual_norm']>bound:
        raise CoupledTorsoError('Coupled pelvis/Spine target is outside the verified control space '
                                f'(residual={metrics["residual_norm"]:.6g}, bound={bound:.6g})')
    return True


def _verify_coupled_pelvis_spine_chest_request(displacement,metrics,*,max_residual=.02):
    d=np.asarray(displacement,dtype=float)
    if d.ndim!=1 or d.size!=9 or not np.isfinite(d).all():
        raise CoupledTorsoError('Coupled pelvis/Spine/Chest displacement is invalid')
    if not isinstance(metrics,dict) or not np.isfinite(metrics.get('residual_norm',float('nan'))):
        raise CoupledTorsoError('Coupled pelvis/Spine/Chest metrics are invalid')
    if not np.isfinite(max_residual) or max_residual<=0:
        raise CoupledTorsoError('Coupled pelvis/Spine/Chest residual bound is invalid')
    bound=max(max_residual,float(np.linalg.norm(d))*.25)
    if metrics['residual_norm']>bound:
        raise CoupledTorsoError('Coupled pelvis/Spine/Chest target is outside the verified control space '
                                f'(residual={metrics["residual_norm"]:.6g}, bound={bound:.6g})')
    return True


def _verify_coupled_spine_orientation_request(displacement,metrics,*,max_residual=.02):
    d=np.asarray(displacement,dtype=float)
    if d.ndim!=1 or d.size not in (9,12,15) or not np.isfinite(d).all():
        raise CoupledTorsoError('Coupled torso orientation displacement is invalid')
    if not isinstance(metrics,dict) or not np.isfinite(metrics.get('residual_norm',float('nan'))):
        raise CoupledTorsoError('Coupled torso orientation metrics are invalid')
    if not np.isfinite(max_residual) or max_residual<=0:
        raise CoupledTorsoError('Coupled torso orientation residual bound is invalid')
    bound=max(max_residual,float(np.linalg.norm(d))*.25)
    if metrics['residual_norm']>bound:
        raise CoupledTorsoError('Coupled torso orientation target is outside the verified control space '
                                f'(residual={metrics["residual_norm"]:.6g}, bound={bound:.6g}, '
                                f'rank={metrics.get("rank")}, requested={metrics.get("requested_norm"):.6g}, '
                                f'projected={metrics.get("projected_norm"):.6g}, '
                                f'singular_values={metrics.get("singular_values")})')
    return True


class ProjectionError(ValueError):
    """Actual-rig accuracy rejection, with a bounded near-convergence retry hint."""
    def __init__(self,pin,length,orientation,pole,elapsed_ms,evaluations):
        super().__init__(f'Actual rig projection failed: pins={pin:.6g}, lengths={length:.6g}, orientation={orientation:.6g}, pole={pole:.6g}')
        self.retryable=2e-4<pin<=1e-3 and length<=.002 and orientation<=.001 and pole<=.01
        self.elapsed_ms=elapsed_ms
        self.evaluations=evaluations


def _angle(a,b):
    q=a.rotation_difference(b)
    return float(2*np.arctan2(np.linalg.norm((q.x,q.y,q.z)),abs(q.w)))


def _rotation_delta_vector(source,target):
    """Small-angle vector for the shortest quaternion delta source -> target."""
    q=source.rotation_difference(target)
    if q.w<0:q.negate()
    return 2*np.asarray((q.x,q.y,q.z),dtype=float)


def _pole_vectors(points,chain,pole):
    root,middle,end=(points[i] for i in chain)
    axis=end-root;axis/=max(float(np.linalg.norm(axis)),1e-12)
    bend=middle-root;bend-=axis*np.dot(bend,axis)
    wanted=pole-root;wanted-=axis*np.dot(wanted,axis)
    return bend,wanted


def _pole_error(points,poles):
    maximum=0.
    for index,pole in poles.items():
        bend,wanted=_pole_vectors(points,POLE_CHAINS[index],pole)
        a=float(np.linalg.norm(bend));b=float(np.linalg.norm(wanted))
        if min(a,b)<1e-6:return float('inf')
        maximum=max(maximum,float(np.arctan2(np.linalg.norm(np.cross(bend,wanted)),np.dot(bend,wanted))))
    return maximum



def mapping(obj, *, writable=True):
    profile,root,limbs=p.bindings(obj)
    if profile.name=='BoneForge Control Rig':
        body=[profile.roles[role] for role in ('hips','spine.01','chest','neck','head')]
        rotations=[profile.roles[role] for role in ('hips','spine.01','spine.02','chest','neck')]
    elif profile.name=='Rigify Generated':
        body=['ORG-spine','ORG-spine.001','ORG-spine.003','ORG-spine.004','ORG-spine.006']
        rotations=[profile.roles[role] for role in ('hips','chest','spine.01','spine.02')]
        rotations+=['spine_fk.002','spine_fk.003',profile.roles['neck']]
    elif profile.name=='BoneForge Legacy / Rigify Metarig' and 'spine.006' in obj.pose.bones:
        body=[profile.roles[role] for role in ('hips','spine.01','chest','neck','head')]
        rotations=[profile.roles[role] for role in ('hips','spine.01','spine.02','chest','neck')]
        rotations+=['spine.005']
    elif profile.name in {'Mocap Humanoid','Unity Humanoid','Unreal Mannequin'}:
        # Plain FK imported rigs: certify the actual parent relationships, not only names.
        spine=['hips','spine.01','spine.02','chest','neck','head']
        required=spine+[f'clavicle.fk-{side}' for side in ('L','R')]
        if any(role not in profile.roles for role in required):
            raise ValueError('Imported FK humanoid requires a complete mapped spine and shoulders')
        links=list(zip(spine[1:],spine[:-1]))
        for side in ('L','R'):
            links += [(f'clavicle.fk-{side}','chest'),(f'upperarm.fk-{side}',f'clavicle.fk-{side}'),
                      (f'thigh.fk-{side}','hips')]
        for child,parent in links:
            bone=obj.pose.bones[profile.roles[child]]
            if bone.parent is None or bone.parent.name!=profile.roles[parent]:
                raise ValueError('Imported FK hierarchy requires '+bone.name+' under '+profile.roles[parent])
        # Root ancestry is retained in anchors; only the selected translation root is fitted.
        # Reject dependency spaces that this plain FK adapter cannot certify.
        ancestors=[];ancestor=obj.pose.bones[profile.roles['hips']].parent
        while ancestor:
            ancestors.append(ancestor.name);ancestor=ancestor.parent
        for name in sorted(set(profile.roles.values())|set(ancestors)):
            if name.startswith(('ORG-','MCH-','DEF-')):
                raise ValueError('Imported FK ancestry contains a generated mechanism: '+name)
            bone=obj.pose.bones[name]
            if any(not c.mute and c.influence>0 for c in bone.constraints):
                raise ValueError('Imported FK dependency is constrained: '+name)
            paths={bone.path_from_id(k) for k in ('location','scale','rotation_euler','rotation_quaternion','rotation_axis_angle')}
            if obj.animation_data and any(c.data_path in paths for c in obj.animation_data.drivers):
                raise ValueError('Imported FK dependency is driven: '+name)
            if any(not np.isfinite(v) or v<=0 for v in bone.scale) or max(bone.scale)/min(bone.scale)>1.0001:
                raise ValueError('Imported FK dependency requires positive uniform bone scale: '+name)
        body=[profile.roles[role] for role in ('hips','spine.01','chest','neck','head')]
        rotations=[profile.roles[role] for role in spine[:-1]]
    else:raise ValueError('Contextual adapter currently requires a verified BoneForge, Rigify or imported FK humanoid')
    rows={row['id']:row for row in limbs}
    names=body+[n for key in ('arm-L','arm-R','leg-L','leg-R') for n in rows[key]['joints']]
    rotations += [profile.roles['clavicle.fk-'+side] for side in ('L','R')]
    rotations += [n for key in ('arm-L','arm-R','leg-L','leg-R') for n in rows[key]['fk'][:2]]
    effectors=[profile.roles['head']]+[rows[key]['fk'][2] for key in ('arm-L','arm-R','leg-L','leg-R')]
    if len(rotations+effectors) != len(set(rotations+effectors)):
        raise ValueError('Humanoid mapping correction conflicts with a required torso control')
    needed=set(names+rotations+effectors+[root])
    if not needed<=set(obj.pose.bones.keys()):raise ValueError('Incomplete contextual rig mapping')
    if writable:
        for name in rotations+effectors:p._check_controls(obj,[name],'rotation')
        p._check_controls(obj,[root],'location')
    # A controlled bone may be a deform bone in a plain FK skeleton, never a generated mechanism.
    if any(n.startswith(('ORG-','MCH-','DEF-')) for n in rotations+effectors+[root]):
        raise ValueError('Generated mechanism cannot be a writable control')
    return dict(profile=profile.name,names=names,root=root,rotations=rotations,effectors=effectors,
                controls=sorted(set(rotations+effectors+[root])|set(profile.controls)))


def orientation_bone(binding,index):
    """Map a semantic orientation joint to the evaluated bone that proves it."""
    if index==0:return binding['names'][0]
    if index in DISTRIBUTED_ORIENTATION_JOINTS:return binding['names'][index]
    if index in ORIENTATION_JOINTS:
        return binding['effectors'][ORIENTATION_JOINTS.index(index)-1]
    raise ValueError('Unsupported orientation joint')


def coupled_torso_controls(binding):
    """Return the verified writable torso controls in deterministic mapping order."""
    try:count=_TORSO_ROTATION_COUNTS[binding['profile']]
    except (KeyError,TypeError):raise ValueError('No coupled torso adapter for this profile') from None
    rotations=binding.get('rotations')
    if not isinstance(rotations,list) or len(rotations)<count:
        raise ValueError('Coupled torso adapter has incomplete rotation controls')
    controls=rotations[:count]
    if len(controls)!=len(set(controls)) or any(not isinstance(name,str) or not name for name in controls):
        raise ValueError('Coupled torso adapter has duplicate or invalid rotation controls')
    return list(controls)


def _quat(pb):
    return Quaternion(w._rotation(pb))


def _set_quat(pb,q):
    if pb.rotation_mode=='QUATERNION':
        if q.dot(pb.rotation_quaternion)<0:q.negate()
        pb.rotation_quaternion=q
    elif pb.rotation_mode=='AXIS_ANGLE':
        axis,angle=q.to_axis_angle();pb.rotation_axis_angle=(angle,*axis)
    else:pb.rotation_euler=q.to_euler(pb.rotation_mode,pb.rotation_euler)


class Session:
    """One-frame reversible FK session; call cancel to restore source modes/pose.

    No keys/actions/helpers are created here. body_preview owns persistence and UI scheduling.
    """
    def __init__(self,obj):
        w.require_rig(obj);w._reject_nla(obj);p._check_space(obj)
        self.owner_key=obj.as_pointer()
        owner=_SESSIONS.get(self.owner_key)
        if owner is not None and not owner.closed:raise ValueError('Another contextual session owns this rig')
        if obj.b4ml.posing_payload or obj.b4ml.quadruped_payload or obj.b4ml.candidate_action:
            raise ValueError('Resolve the active posing/animation preview first')
        self.obj=obj;self.binding=mapping(obj);self.closed=False;self.running=False
        self.source=w.raw_pose(obj,self.binding['controls']);self.source_modes=rs.mode_values(obj)
        self.frame=(bpy.context.scene.frame_current,bpy.context.scene.frame_subframe)
        self.action=obj.animation_data.action if obj.animation_data else None
        self.slot=w._slot(obj.animation_data) if obj.animation_data else ''
        self.structure=w._rest_signature(obj);self.world=obj.matrix_world.copy()
        try:
            rs.normalize_fk(obj)
            self.normalized=w.raw_pose(obj,self.binding['controls'])
            self.modes=rs.mode_values(obj);self.switches=w._switches(obj)
            self.q0=[_quat(obj.pose.bones[n]) for n in self.binding['rotations']]
            self.root_location=obj.pose.bones[self.binding['root']].location.copy()
            names=self.binding['names'];rest=np.array([obj.matrix_world@obj.data.bones[n].head_local for n in names])
            left=rest[11]-rest[14];up=(rest[5]+rest[8]-rest[11]-rest[14])*.5
            self.scale=float(np.linalg.norm(up));left/=np.linalg.norm(left);up-=left*np.dot(up,left)
            if self.scale<1e-8 or np.linalg.norm(up)<1e-8:raise ValueError('Degenerate body frame')
            up/=np.linalg.norm(up);reference=np.stack((left,np.cross(up,left),up),axis=1)
            pelvis=obj.pose.bones[names[0]]
            current_r=np.array((obj.matrix_world@pelvis.matrix).to_quaternion().to_matrix())
            rest_r=np.array((obj.matrix_world@pelvis.bone.matrix_local).to_quaternion().to_matrix())
            self.basis=current_r@rest_r.T@reference
            self.origin=np.array(obj.matrix_world@pelvis.head)
            self.rest=(rest-rest[0])@reference/self.scale
            self.baseline=self.points()
            self.balance_reference=np.array([self.world@obj.pose.bones[n].matrix for n in names])
            self.pelvis_rotation=pelvis.matrix.to_quaternion()
            self.orientations={n:obj.pose.bones[n].matrix.to_quaternion() for n in self.binding['effectors']}
            # Check actual relevant evaluated bone lengths, not fictitious collapsed semantic edges.
            tracked=set(names)
            for n in names:
                pb=obj.pose.bones[n]
                while pb:
                    if pb.bone.use_deform or pb.name.startswith('ORG-spine'):tracked.add(pb.name)
                    pb=pb.parent
            self.lengths={n:(obj.pose.bones[n].tail-obj.pose.bones[n].head).length for n in tracked}
            self.params=decode_model(files(__package__).joinpath('models','context_pose_mlp_v1.npz').read_bytes())
            _SESSIONS[self.owner_key]=self
        except Exception:
            w.restore_pose(obj,self.source);rs.restore_values(obj,self.source_modes);self.closed=True;raise

    def points(self,update=True,obj=None):
        obj=self.obj if obj is None else obj
        if update:p._update(obj)
        points=(np.array([obj.matrix_world@obj.pose.bones[n].head for n in self.binding['names']])-self.origin)@self.basis/self.scale
        if not np.isfinite(points).all():raise ValueError('Rig produced nonfinite joint positions')
        return points

    def world_points(self,local):return np.asarray(local)@self.basis.T*self.scale+self.origin

    def _validate(self):
        ob=self.obj;ad=ob.animation_data
        if self.closed:raise ValueError('Session is closed')
        if _SESSIONS.get(self.owner_key) is not self:raise ValueError('Contextual session ownership changed')
        if self.frame!=(bpy.context.scene.frame_current,bpy.context.scene.frame_subframe):raise ValueError('Return to the session frame')
        if self.action!=(ad.action if ad else None) or self.slot!=(w._slot(ad) if ad else ''):raise ValueError('Source animation changed')
        if self.world!=ob.matrix_world or self.structure!=w._rest_signature(ob):raise ValueError('Rig structure or object transform changed')
        if self.switches!=w._switches(ob):raise ValueError('Rig properties changed')
        for name,row in self.normalized.items():
            pb=ob.pose.bones[name]
            if pb.rotation_mode!=row['mode'] or w._channels(pb)!=row['channels']:raise ValueError('Control mode or locks changed')
        w._reject_nla(ob)
        if self.binding['profile'] in {'Mocap Humanoid','Unity Humanoid','Unreal Mannequin'} and mapping(ob)!=self.binding:
            raise ValueError('Imported FK binding changed during the preview')
        for name in self.binding['rotations']+self.binding['effectors']:p._check_controls(ob,[name],'rotation')
        p._check_controls(ob,[self.binding['root']],'location')

    def _apply(self,x,obj=None,update=None):
        if not np.isfinite(x).all():raise ValueError('Nonfinite solver update')
        ob=self.obj if obj is None else obj
        ob.pose.bones[self.binding['root']].location=self.root_location+Vector(x[:3])*self.scale
        for i,(name,q) in enumerate(zip(self.binding['rotations'],self.q0)):
            vector=Vector(x[3+i*3:6+i*3]);angle=vector.length
            change=Quaternion(vector/angle,angle) if angle>1e-12 else Quaternion()
            _set_quat(ob.pose.bones[name],q@change)
        if update is None:p._update(ob)
        else:update()

    def _seed_coupled_torso(self, x, target, *, emit_progress=True, cancel_requested=None):
        """Build one bounded actual-rig torso update for semantic Spine index 1."""
        controls=coupled_torso_controls(self.binding)
        slots={name:i for i,name in enumerate(self.binding['rotations'])}
        epsilon=1e-4;metrics=None;iterations=0
        for iterations in range(8):
            if cancel_requested is not None and cancel_requested():raise InterruptedError('Contextual pose solve cancelled')
            if emit_progress:
                self._apply(x);yield dict(phase='torso_seed',iteration=iterations,total_iterations=8)
                self._validate()
            baseline=self.points();jacobian=np.empty((3,3*len(controls)),dtype=float)
            for column,name in enumerate(controls):
                for axis in range(3):
                    trial=x.copy();trial[3+slots[name]*3+axis]+=epsilon
                    self._apply(trial)
                    jacobian[:,column*3+axis]=(self.points(update=False)[1]-baseline[1])/epsilon
            self._apply(x)
            displacement=np.asarray(target,dtype=float)-self.points(update=False)[1]
            update,metrics=bounded_coupled_torso_update(jacobian,displacement)
            verify_coupled_torso_request(displacement,metrics)
            for column,name in enumerate(controls):
                slot=slots[name]
                x[3+slot*3:6+slot*3]+=update[column*3:column*3+3]
            self._apply(x)
            if float(np.linalg.norm(displacement))<1e-6:break
        final_displacement=np.asarray(target,dtype=float)-self.points()[1]
        metrics.update(controls=controls,epsilon=epsilon,iterations=iterations+1,
                       displacement_norm=float(np.linalg.norm(final_displacement)),
                       jacobian_norm=float(np.linalg.norm(jacobian)))
        return x,metrics

    def _seed_coupled_pelvis_spine(self,x,pelvis_target,spine_target,*,emit_progress=True,cancel_requested=None):
        """Solve Pelvis and Spine positions together in the mapped control space."""
        controls=coupled_torso_controls(self.binding)
        slots={name:i for i,name in enumerate(self.binding['rotations'])}
        pelvis_target=np.asarray(pelvis_target,dtype=float);spine_target=np.asarray(spine_target,dtype=float)
        if pelvis_target.shape!=(3,) or spine_target.shape!=(3,) or not np.isfinite(pelvis_target).all() or not np.isfinite(spine_target).all():
            raise CoupledTorsoError('Coupled pelvis/Spine targets are invalid')
        epsilon=1e-4;metrics=None;iterations=0
        # Start the joint position solve directly. A preliminary rotation-only
        # Spine fit can reject a request that becomes reachable once pelvis
        # translation is included in this chart.
        torso_seed_metrics=None

        def with_update(base,delta):
            candidate=base.copy();candidate[:3]+=delta[:3]
            for column,name in enumerate(controls):
                slot=slots[name]
                candidate[3+slot*3:6+slot*3]+=delta[3+column*3:3+column*3+3]
            return candidate

        for iterations in range(24):
            if cancel_requested is not None and cancel_requested():raise InterruptedError('Contextual pose solve cancelled')
            if emit_progress:
                self._apply(x);yield dict(phase='torso_seed',iteration=iterations,total_iterations=24)
                self._validate()
            baseline=self.points();jacobian=np.empty((6,3+3*len(controls)),dtype=float)
            for column in range(3):
                trial=x.copy();trial[column]+=epsilon;self._apply(trial)
                moved=self.points(update=False);jacobian[:,column]=np.r_[moved[0]-baseline[0],moved[1]-baseline[1]]/epsilon
            for column,name in enumerate(controls):
                slot=slots[name]
                for axis in range(3):
                    trial=x.copy();trial[3+slot*3+axis]+=epsilon;self._apply(trial)
                    moved=self.points(update=False);jacobian[:,3+column*3+axis]=np.r_[moved[0]-baseline[0],moved[1]-baseline[1]]/epsilon
            self._apply(x)
            current_points=self.points(update=False)
            displacement=np.r_[pelvis_target-current_points[0],spine_target-current_points[1]]
            current_norm=float(np.linalg.norm(displacement));best=None;best_norm=current_norm;best_fraction=0.;candidate_norms=[]
            for damping in (1e-4,1e-3,1e-2):
                update,metrics=_bounded_coupled_update(jacobian,displacement,
                    max_norm=MAX_COUPLED_PELVIS_SPINE_PARAMETER_NORM,damping=damping)
                _verify_coupled_pelvis_spine_request(displacement,metrics)
                for fraction in (1.,.5,.25,.125,.0625,.03125,.015625):
                    candidate=with_update(x,update*fraction);self._apply(candidate)
                    moved=self.points(update=False)
                    candidate_norm=float(np.linalg.norm(np.r_[pelvis_target-moved[0],spine_target-moved[1]]))
                    candidate_norms.append(candidate_norm)
                    if candidate_norm<best_norm:
                        best_norm=candidate_norm;best=candidate;best_fraction=fraction
                if best is not None:break
            if best is None:
                self._apply(x)
                if current_norm<1e-6:break
                raise CoupledTorsoError('Coupled pelvis/Spine nonlinear projection stalled '
                                        f'(current={current_norm:.6g}, pelvis={float(np.linalg.norm(displacement[:3])):.6g}, '
                                        f'spine={float(np.linalg.norm(displacement[3:])):.6g}, '
                                        f'candidates={[round(v,6) for v in candidate_norms]})')
            x=best;self._apply(x)
            metrics.update(line_search_fraction=best_fraction,nonlinear_residual_norm=best_norm)
            current=self.points(update=False)
            if max(float(np.linalg.norm(current[0]-pelvis_target)),
                   float(np.linalg.norm(current[1]-spine_target)))<1e-6:break
        current=self.points()
        metrics.update(controls=controls,epsilon=epsilon,iterations=iterations+1,
                       torso_seed=torso_seed_metrics,
                       pelvis_displacement_norm=float(np.linalg.norm(np.asarray(pelvis_target)-current[0])),
                       spine_displacement_norm=float(np.linalg.norm(np.asarray(spine_target)-current[1])),
                       jacobian_norm=float(np.linalg.norm(jacobian)))
        return x,metrics

    def _seed_coupled_pelvis_spine_chest(self,x,pelvis_target,spine_target,chest_target,*,emit_progress=True,cancel_requested=None):
        """Solve three explicit torso positions in the mapped control space.

        This is a bounded local chart, not an unconstrained anatomical model.  The
        Jacobian is measured on the actual rig so generated and plain FK adapters
        can reject requests that their writable controls cannot represent.
        """
        controls=coupled_torso_controls(self.binding)
        slots={name:i for i,name in enumerate(self.binding['rotations'])}
        targets=np.asarray((pelvis_target,spine_target,chest_target),dtype=float)
        if targets.shape!=(3,3) or not np.isfinite(targets).all():
            raise CoupledTorsoError('Coupled pelvis/Spine/Chest targets are invalid')
        epsilon=1e-4;metrics=None;iterations=0

        def torso_points(update=True):
            return self.points(update=update)[0:3].reshape(-1)

        def with_update(base,delta):
            candidate=base.copy();candidate[:3]+=delta[:3]
            for column,name in enumerate(controls):
                slot=slots[name]
                candidate[3+slot*3:6+slot*3]+=delta[3+column*3:3+column*3+3]
            return candidate

        for iterations in range(32):
            if cancel_requested is not None and cancel_requested():raise InterruptedError('Contextual pose solve cancelled')
            if emit_progress:
                self._apply(x);yield dict(phase='torso_seed',iteration=iterations,total_iterations=32)
                self._validate()
            baseline=torso_points();jacobian=np.empty((9,3+3*len(controls)),dtype=float)
            for column in range(3):
                trial=x.copy();trial[column]+=epsilon;self._apply(trial)
                jacobian[:,column]=(torso_points(False)-baseline)/epsilon
            for column,name in enumerate(controls):
                slot=slots[name]
                for axis in range(3):
                    trial=x.copy();trial[3+slot*3+axis]+=epsilon;self._apply(trial)
                    jacobian[:,3+column*3+axis]=(torso_points(False)-baseline)/epsilon
            self._apply(x)
            displacement=(targets-self.points(update=False)[0:3]).reshape(-1)
            current_norm=float(np.linalg.norm(displacement));best=None;best_norm=current_norm;best_fraction=0.;candidate_norms=[]
            for damping in (1e-4,1e-3,1e-2):
                update,metrics=_bounded_coupled_update(jacobian,displacement,
                    max_norm=MAX_COUPLED_PELVIS_SPINE_CHEST_PARAMETER_NORM,damping=damping)
                _verify_coupled_pelvis_spine_chest_request(displacement,metrics)
                for fraction in (1.,.5,.25,.125,.0625,.03125,.015625):
                    candidate=with_update(x,update*fraction);self._apply(candidate)
                    candidate_norm=float(np.linalg.norm(targets-self.points(update=False)[0:3]))
                    candidate_norms.append(candidate_norm)
                    if candidate_norm<best_norm:
                        best_norm=candidate_norm;best=candidate;best_fraction=fraction
                if best is not None:break
            if best is None:
                self._apply(x)
                if current_norm<1e-6:break
                raise CoupledTorsoError('Coupled pelvis/Spine/Chest nonlinear projection stalled '
                                        f'(current={current_norm:.6g}, candidates={[round(v,6) for v in candidate_norms]})')
            x=best;self._apply(x)
            metrics.update(line_search_fraction=best_fraction,nonlinear_residual_norm=best_norm)
            current=self.points(update=False)[0:3]
            if float(np.max(np.linalg.norm(current-targets,axis=1)))<1e-6:break
        current=self.points()[0:3]
        metrics.update(controls=controls,epsilon=epsilon,iterations=iterations+1,target_count=3,
                       pelvis_displacement_norm=float(np.linalg.norm(np.asarray(pelvis_target)-current[0])),
                       spine_displacement_norm=float(np.linalg.norm(np.asarray(spine_target)-current[1])),
                       chest_displacement_norm=float(np.linalg.norm(np.asarray(chest_target)-current[2])),
                       jacobian_norm=float(np.linalg.norm(jacobian)))
        return x,metrics

    def _seed_coupled_spine_orientation(self,x,targets,desired_orientation,
                                        desired_chest_orientation=None,*,emit_progress=True,
                                        cancel_requested=None):
        """Fit torso positions and explicit Spine/(optional Chest) orientations."""
        controls=coupled_torso_controls(self.binding)
        slots={name:i for i,name in enumerate(self.binding['rotations'])}
        targets=np.asarray(targets,dtype=float)
        if targets.shape not in ((2,3),(3,3)) or not np.isfinite(targets).all():
            raise CoupledTorsoError('Coupled Spine orientation requires finite two- or three-point torso targets')
        orientation_targets={1:Quaternion(desired_orientation)}
        if desired_chest_orientation is not None:
            if len(targets)!=3:
                raise CoupledTorsoError('Coupled Chest orientation requires a pinned Chest position')
            orientation_targets[2]=Quaternion(desired_chest_orientation)
        for index,orientation in orientation_targets.items():
            if (not np.isfinite(np.asarray(orientation,dtype=float)).all()
                    or orientation.magnitude<1e-8):
                raise CoupledTorsoError(f'Coupled {"Spine" if index==1 else "Chest"} orientation target is invalid')
            orientation.normalize()
        orientation_names={index:orientation_bone(self.binding,index) for index in orientation_targets}
        point_count=len(targets);epsilon=1e-3;metrics=None;iterations=0

        def current_orientation(index):
            return self.obj.pose.bones[orientation_names[index]].matrix.to_quaternion().copy()

        def orientation_residual():
            return np.concatenate([
                _rotation_delta_vector(current_orientation(index),orientation_targets[index])
                for index in sorted(orientation_targets)
            ])

        def with_update(base,delta):
            candidate=base.copy();candidate[:3]+=delta[:3]
            for column,name in enumerate(controls):
                slot=slots[name]
                candidate[3+slot*3:6+slot*3]+=delta[3+column*3:3+column*3+3]
            return candidate

        for iterations in range(32):
            if cancel_requested is not None and cancel_requested():raise InterruptedError('Contextual pose solve cancelled')
            if emit_progress:
                self._apply(x);yield dict(phase='torso_seed',iteration=iterations,total_iterations=32)
                self._validate()
            baseline_points=self.points()[:point_count].copy()
            baseline_orientations={index:current_orientation(index) for index in orientation_targets}
            baseline_orientation_residual=np.concatenate([
                _rotation_delta_vector(baseline_orientations[index],orientation_targets[index])
                for index in sorted(orientation_targets)
            ])
            displacement=np.r_[(targets-baseline_points).reshape(-1),baseline_orientation_residual]
            current_norm=float(np.linalg.norm(displacement))
            jacobian=np.empty((3*point_count+3*len(orientation_targets),3+3*len(controls)),dtype=float)
            for column in range(jacobian.shape[1]):
                trial=x.copy();trial[column]+=epsilon;self._apply(trial)
                moved=self.points(update=False)
                jacobian[:3*point_count,column]=(baseline_points-moved[:point_count]).reshape(-1)/epsilon
                jacobian[3*point_count:,column]=(orientation_residual()
                    -baseline_orientation_residual)/epsilon
            self._apply(x)
            best=None;best_norm=current_norm;best_fraction=0.;candidate_norms=[]
            solve_displacement=-displacement
            for damping in (1e-4,1e-3,1e-2):
                update,metrics=_bounded_coupled_update(jacobian,solve_displacement,
                    max_norm=MAX_COUPLED_PELVIS_SPINE_CHEST_PARAMETER_NORM,damping=damping)
                try:
                    _verify_coupled_spine_orientation_request(solve_displacement,metrics)
                    metrics['linearization_gate']='passed'
                except CoupledTorsoError as error:
                    # A poor local linear chart is not proof of an unreachable
                    # target. Continue only through bounded candidates that reduce
                    # the measured nonlinear position+orientation residual; final
                    # acceptance still uses the strict actual-rig gates.
                    metrics['linearization_gate']='deferred_to_nonlinear_projection'
                    metrics['linearization_rejection']=str(error)
                for fraction in (1.,.5,.25,.125,.0625,.03125,.015625):
                    candidate=with_update(x,update*fraction);self._apply(candidate)
                    candidate_displacement=np.r_[
                        (targets-self.points()[:point_count]).reshape(-1),
                        orientation_residual()]
                    candidate_norm=float(np.linalg.norm(candidate_displacement))
                    candidate_norms.append(candidate_norm)
                    if candidate_norm<best_norm:
                        best_norm=candidate_norm;best=candidate;best_fraction=fraction
                if best is not None:break
            if best is None:
                self._apply(x)
                if current_norm<1e-6:break
                raise CoupledTorsoError('Coupled pelvis/Spine orientation nonlinear projection stalled '
                                        f'(current={current_norm:.6g}, candidates={[round(v,6) for v in candidate_norms]})')
            x=best;self._apply(x)
            metrics.update(line_search_fraction=best_fraction,nonlinear_residual_norm=best_norm)
            current_points=self.points()[:point_count]
            orientation_errors={index:_angle(orientation_targets[index],current_orientation(index))
                                for index in orientation_targets}
            if (float(np.max(np.linalg.norm(current_points-targets,axis=1)))<1e-6
                    and max(orientation_errors.values())<1e-6):break
        current_points=self.points()[:point_count]
        orientation_errors={index:_angle(orientation_targets[index],current_orientation(index))
                            for index in orientation_targets}
        metrics.update(controls=controls,epsilon=epsilon,iterations=iterations+1,
                       target_count=point_count,orientation_joint=1,
                       orientation_joints=sorted(orientation_targets),
                       orientation_error_radians=orientation_errors[1],
                       chest_orientation_error_radians=orientation_errors.get(2),
                       pelvis_displacement_norm=float(np.linalg.norm(targets[0]-current_points[0])),
                       spine_displacement_norm=float(np.linalg.norm(targets[1]-current_points[1])),
                       chest_displacement_norm=(float(np.linalg.norm(targets[2]-current_points[2]))
                                                if point_count==3 else None),
                       jacobian_norm=float(np.linalg.norm(jacobian)))
        return x,metrics

    def _pin_coupled_pelvis(self,x,target):
        """Correct only the writable root translation after a torso projection."""
        epsilon=1e-4;baseline=self.points()[0];jacobian=np.empty((3,3),dtype=float)
        for axis in range(3):
            trial=x.copy();trial[axis]+=epsilon;self._apply(trial)
            jacobian[:,axis]=(self.points(update=False)[0]-baseline)/epsilon
        self._apply(x);displacement=np.asarray(target,dtype=float)-self.points(update=False)[0]
        update,metrics=bounded_coupled_torso_update(jacobian,displacement,max_norm=.5)
        verify_coupled_torso_request(displacement,metrics)
        x[:3]+=update;self._apply(x)
        metrics.update(epsilon=epsilon,displacement_norm=float(np.linalg.norm(displacement)),
                       jacobian_norm=float(np.linalg.norm(jacobian)))
        return x,metrics

    def solve(self,*args,**kwargs):
        """Synchronous compatibility wrapper; solve_steps provides cooperative progress."""
        steps=self.solve_steps(*args,**kwargs,_emit_progress=False)
        while True:
            try:next(steps)
            except StopIteration as done:return done.value

    def solve_steps(self,targets_world,mask,learned_influence=1.,iterations=50,jacobian_mode="reuse",cancel_requested=None,_emit_progress=True,evaluation_backend="auto",orientations_world=None,pole_targets=None,rotation_limits=None,balance=None,proposal_world=None,proposal_rotations_world=None):
        """Yield bounded progress checkpoints on the host main thread.

        Closing the generator restores the preceding preview. Exhaustion returns the
        verified result through StopIteration.value. Caller owns scheduling and closing.
        """
        if self.running:raise ValueError('A contextual solve is already active')
        self._validate()
        if type(iterations)!=int or not 1<=iterations<=100:raise ValueError('Invalid solve iteration budget')
        if jacobian_mode not in ('dense','reuse'):raise ValueError('Unknown derivative strategy')
        if evaluation_backend not in ('host','proxy','auto'):raise ValueError('Unknown rig evaluation backend')
        if cancel_requested is not None and not callable(cancel_requested):raise ValueError('Cancellation probe must be callable')
        if not np.isfinite(learned_influence) or not 0<=learned_influence<=1:raise ValueError('Invalid learned influence')
        mask=np.array(mask,dtype=bool,copy=True);targets=np.array(targets_world,dtype=float,copy=True)
        if targets.shape!=(JOINTS,3) or mask.shape!=(JOINTS,) or not mask[0]:raise ValueError('Expected 17 targets and pinned pelvis')
        if not np.isfinite(targets[mask]).all():raise ValueError('Nonfinite pinned target')
        orientations_world={} if orientations_world is None else dict(orientations_world)
        pole_targets={} if pole_targets is None else pole_targets
        if not isinstance(orientations_world,dict) or not isinstance(pole_targets,dict):raise ValueError('Expected orientation and pole dictionaries')
        balance_constraint=None
        if balance is not None:
            from .balance import Constraint
            balance_constraint=Constraint(self,balance,targets,mask,orientations_world)
        rotation_limits=limits.validate(rotation_limits,set(self.binding['rotations']+self.binding['effectors']))
        frame_pairs={};frame_rest={}
        if any(v.get('space')=='JOINT' for v in rotation_limits.values()):
            available=joint_frames.bind(self.obj,self.binding)
            for name,limit in rotation_limits.items():
                if limit.get('space')=='JOINT':
                    if name not in available:raise ValueError(f'No verified skeletal joint frame for control: {name}')
                    frame_pairs[name]=available[name];frame_rest[name]=joint_frames.rest_relative(self.obj,available[name])
        desired_pelvis=self.pelvis_rotation.copy();desired_orientations={n:q.copy() for n,q in self.orientations.items()}
        distributed_orientations={};desired_spine_orientation=None;desired_chest_orientation=None
        inverse_world=self.world.to_quaternion().inverted()
        for index,value in orientations_world.items():
            if index not in SUPPORTED_ORIENTATION_JOINTS:raise ValueError('Unsupported orientation joint')
            a=np.asarray(value,float)
            if a.shape!=(4,) or not np.isfinite(a).all() or abs(np.linalg.norm(a)-1)>1e-4:raise ValueError('Expected a finite unit orientation quaternion')
            q=inverse_world@Quaternion(a);q.normalize()
            if index==0:desired_pelvis=q
            elif index==1:
                desired_spine_orientation=q
                distributed_orientations[orientation_bone(self.binding,index)]=q
            elif index==2 and 1 in orientations_world:
                desired_chest_orientation=q
                distributed_orientations[orientation_bone(self.binding,index)]=q
            elif index in DISTRIBUTED_ORIENTATION_JOINTS:distributed_orientations[orientation_bone(self.binding,index)]=q
            else:desired_orientations[orientation_bone(self.binding,index)]=q
        poles={}
        for index,value in pole_targets.items():
            if index not in POLE_CHAINS:raise ValueError('Unsupported pole joint')
            a=np.asarray(value,float)
            if a.shape!=(3,) or not np.isfinite(a).all():raise ValueError('Expected a finite pole position')
            poles[index]=(a-self.origin)@self.basis/self.scale
        # Position-only torso requests use an explicit coupled local chart.  Pelvis
        # position remains a hard pin, while pelvis orientation is intentionally a
        # solved degree of freedom; requiring the old pelvis frame here would make
        # semantic Spine/Chest shaping unreachable on FK rigs.
        coupled_spine_only=bool(mask[1] and not np.any(mask[2:]) and not orientations_world and not poles and not rotation_limits and not frame_pairs and balance_constraint is None)
        coupled_spine_chest_only=bool(mask[1] and mask[2] and not np.any(mask[3:]) and not orientations_world and not poles and not rotation_limits and not frame_pairs and balance_constraint is None)
        coupled_torso_only=coupled_spine_only or coupled_spine_chest_only
        coupled_spine_orientation=1 in orientations_world
        if coupled_spine_orientation and not (
                mask[1] and not np.any(mask[3:]) and set(orientations_world) in ({1},{1,2})
                and (set(orientations_world)=={1} or mask[2])
                and not poles and not rotation_limits and not frame_pairs
                and balance_constraint is None and proposal_world is None
                and proposal_rotations_world is None):
            raise CoupledTorsoError('Coupled Spine orientation requires pinned Pelvis and Spine positions, '
                                    'an optional pinned Chest with optional Chest orientation, and no additional constraints')
        pelvis_orientation_required=not (coupled_torso_only or coupled_spine_orientation)
        if coupled_torso_only:
            # The unrequested endpoint frames are not implicit constraints in a
            # position-only torso edit; generated rigs otherwise pull the
            # coupled controls back through their old effector orientations.
            desired_orientations={}
            distributed_orientations={}
        elif coupled_spine_orientation:
            # Coupled Spine/Chest orientations are represented by the seed's
            # torso controls and must remain in both the objective and final
            # acceptance check.
            desired_orientations={}
        observations=(targets-self.origin)@self.basis/self.scale
        # Training conditions on an explicitly supplied pelvis frame: its observed
        # position must be zero even when the animator translates the body in world space.
        if not mask[0]:observations[0]=self.baseline[0]
        pelvis_offset=observations[0].copy()
        safe=np.where(mask[:,None],observations-pelvis_offset,self.baseline)
        # Use the actual control rig as the projection model. Collapsed semantic edges
        # are not physical bones on these rigs, so the generic length projector is inappropriate.
        model_mask=mask.copy();model_mask[0]=True
        safe[0]=0. # The learned model keeps a pelvis reference even when geometric balance may translate it.
        if proposal_world is None:
            features=encode(self.rest,self.baseline,safe,model_mask)[None]
            residual=forward(self.params,((features-self.params['mean'])/self.params['scale']).astype(np.float32))[0].reshape(JOINTS,3)
            proposal=self.baseline+residual*learned_influence+pelvis_offset
        else:
            # Temporal proposals are already predictions. Never silently mix the
            # separate pose model into their projection or their baseline comparison.
            if learned_influence!=0.:
                raise ValueError('External motion proposals require zero pose-model influence')
            supplied=np.array(proposal_world,dtype=float,copy=True)
            if supplied.shape!=(JOINTS,3) or not np.isfinite(supplied).all():
                raise ValueError('Expected a finite 17-joint motion proposal')
            proposal=(supplied-self.origin)@self.basis/self.scale
            residual=np.zeros((JOINTS,3))
        proposal=np.where(mask[:,None],observations,proposal)
        rotation_proposal=None
        if proposal_rotations_world is not None:
            if proposal_world is None:raise ValueError('Rotation proposals require an external position proposal')
            rotation_values=np.array(proposal_rotations_world,dtype=float,copy=True)
            if rotation_values.shape!=(JOINTS,4) or not np.isfinite(rotation_values).all() or np.max(abs(np.linalg.norm(rotation_values,axis=1)-1.))>1e-4:
                raise ValueError('Expected 17 finite unit proposal orientations')
            rotation_proposal=[inverse_world@Quaternion(row) for row in rotation_values]
        rotation_weight=1.
        before=w.raw_pose(self.obj,self.binding['controls']);started=time.perf_counter();evaluations=0
        x=np.zeros(3+3*len(self.q0));damping=.01;self.trace=[]
        jac=None;refreshes=0;last_refresh=-1;rejected=0
        directional=any('bend' in v for v in rotation_limits.values())
        epsilon=1e-3 if directional else (1e-4 if frame_pairs else 1e-3)
        priority_start=max(1,iterations-(24 if directional else 12))
        if coupled_torso_only:
            # The coupled seed is the complete fit for this explicitly pinned torso request;
            # reopening the generic objective can move generated controls away
            # from the verified local torso chart.
            iterations=0
        # An explicit coupled Spine request is a hard animator constraint.  Its
        # pin must dominate the unpinned pose prior, which is intentionally kept
        # active for every other target row.
        pin_weight=1000. if mask[1] else 100.
        # Once the coupled Spine row is active, unpinned semantic joints are
        # deliberately not an objective: the learned pose prior must not pull
        # the generated rig away from an explicit pelvis/Spine request.
        weights=np.where(mask,pin_weight,0. if mask[1] else 1.)[:,None]
        proxy=None;proxy_init_ms=0.;proxy_rejection='';evaluation_obj=self.obj
        def limit_residual(ob,prospective=False):
            result=[]
            for name,limit in rotation_limits.items():
                if name in frame_pairs:
                    q=joint_frames.rotation(ob,frame_pairs[name],frame_rest[name])
                elif prospective and name in desired_orientations:
                    # Effectors are set to these orientations after fitting. Include
                    # their future local rotation now so parent joints can respond.
                    matrix=desired_orientations[name].to_matrix().to_4x4()
                    matrix.translation=ob.pose.bones[name].head
                    q=ob.convert_space(pose_bone=ob.pose.bones[name],matrix=matrix,from_space='POSE',to_space='LOCAL').to_quaternion()
                else:q=_quat(ob.pose.bones[name])
                result.extend(limits.residual(q,limit))
            return np.asarray(result)
        def apply_fit(v,ob=None,update=None):
            ob=self.obj if ob is None else ob
            self._apply(v,obj=ob,update=update)
            if frame_pairs or balance_constraint is not None or rotation_proposal is not None or distributed_orientations:
                # A distributed skeleton can depend on the final effector too
                # (Rigify's neck is one example). Evaluate the actual dependency
                # graph, not an assumed constant child/parent orientation offset.
                for name,orientation in desired_orientations.items():
                    matrix=orientation.to_matrix().to_4x4();matrix.translation=ob.pose.bones[name].head
                    local=ob.convert_space(pose_bone=ob.pose.bones[name],matrix=matrix,from_space='POSE',to_space='LOCAL')
                    _set_quat(ob.pose.bones[name],local.to_quaternion())
                if update is None:p._update(ob)
                else:update()
        def evaluate(v):
            nonlocal evaluations
            if cancel_requested is not None and cancel_requested():raise InterruptedError('Contextual pose solve cancelled')
            apply_fit(v,ob=evaluation_obj,update=proxy.update if proxy else None);evaluations+=1
            points=self.points(update=False,obj=evaluation_obj)
            rotation=desired_pelvis.rotation_difference(evaluation_obj.pose.bones[self.binding['names'][0]].matrix.to_quaternion())
            if rotation.w<0:rotation.negate()
            # Quaternion vector is stable near identity where float32 acos loses precision.
            orientation_error=(list(2*np.array((rotation.x,rotation.y,rotation.z)))
                               if pelvis_orientation_required else [])
            for name,wanted in distributed_orientations.items():
                difference=wanted.rotation_difference(evaluation_obj.pose.bones[name].matrix.to_quaternion())
                if difference.w<0:difference.negate()
                orientation_error.extend(2*np.array((difference.x,difference.y,difference.z)))
            pole_residual=[]
            for index,pole in poles.items():
                bend,wanted=_pole_vectors(points,POLE_CHAINS[index],pole)
                wanted/=max(float(np.linalg.norm(wanted)),1e-12)
                pole_residual.extend((bend/max(float(np.linalg.norm(bend)),1e-5)-wanted)*20.)
            balance_error=balance_constraint.residual(evaluation_obj,self.world_points(points)) if balance_constraint is not None else []
            rotation_error=[]
            if rotation_proposal is not None:
                for name,wanted in zip(self.binding['names'],rotation_proposal):
                    difference=wanted.rotation_difference(evaluation_obj.pose.bones[name].matrix.to_quaternion())
                    if difference.w<0:difference.negate()
                    rotation_error.extend((difference.x,difference.y,difference.z))
            return np.r_[((points-proposal)*weights).ravel(),np.asarray(rotation_error)*2.*rotation_weight,np.asarray(orientation_error)*100.,pole_residual,limit_residual(evaluation_obj,True)*150.,np.asarray(balance_error)*100.,v*.005],points
        self.running=True
        torso_metrics=None
        try:
            w.restore_pose(self.obj,self.normalized)
            if mask[1]:
                if coupled_spine_orientation:
                    torso_targets=observations[:3 if mask[2] else 2]
                    x,torso_metrics=yield from self._seed_coupled_spine_orientation(
                        x,torso_targets,desired_spine_orientation,desired_chest_orientation,
                        emit_progress=_emit_progress,cancel_requested=cancel_requested)
                elif coupled_spine_chest_only:
                    x,torso_metrics=yield from self._seed_coupled_pelvis_spine_chest(
                        x,observations[0],observations[1],observations[2],
                        emit_progress=_emit_progress,cancel_requested=cancel_requested)
                elif coupled_spine_only:
                    x,torso_metrics=yield from self._seed_coupled_pelvis_spine(
                        x,observations[0],observations[1],emit_progress=_emit_progress,
                        cancel_requested=cancel_requested)
                # Mixed whole-body requests must reach the translation-capable
                # joint solve.  The rotation-only torso seed cannot establish
                # reachability when all requested joints share a root offset.
            if poles or 0 in orientations_world:
                # Seed explicit intent away from straight-limb singularities. This is
                # initialization only; the full requested pins still govern acceptance.
                inverse=self.world.inverted();p._update(self.obj)
                pelvis=self.binding['names'][0]
                p._translate(self.obj,self.binding['root'],inverse@Vector(targets[0])-self.obj.pose.bones[pelvis].head)
                if 0 in orientations_world and pelvis in self.binding['rotations']:
                    matrix=desired_pelvis.to_matrix().to_4x4();matrix.translation=self.obj.pose.bones[pelvis].head
                    p._write_rotation(self.obj,pelvis,matrix)
                _,_,limbs=p.bindings(self.obj)
                by_id={r['id']:r for r in limbs}
                limb_rows={6:by_id['arm-L'],9:by_id['arm-R'],12:by_id['leg-L'],15:by_id['leg-R']}
                for index in poles:
                    row=limb_rows[index];joints=[self.obj.pose.bones[n] for n in row['joints']]
                    root,middle,end=(j.head.copy() for j in joints)
                    last=POLE_CHAINS[index][2]
                    target=inverse@Vector(targets[last]) if mask[last] else end
                    pole=inverse@Vector(pole_targets[index])
                    reach=(middle-root).length+(end-middle).length
                    delta=target-root
                    if delta.length>reach*.995:target=root+delta.normalized()*reach*.995
                    joint,tip=p.two_bone_positions(tuple(root),tuple(target),tuple(pole),(middle-root).length,(end-middle).length)
                    p._aim(self.obj,row['fk'][0],middle-root,Vector(joint)-root)
                    middle=joints[1].head.copy();end=joints[2].head.copy()
                    p._aim(self.obj,row['fk'][1],end-middle,Vector(tip)-middle)
                x[:3]=(np.array(self.obj.pose.bones[self.binding['root']].location)-np.array(self.root_location))/self.scale
                for i,(name,base) in enumerate(zip(self.binding['rotations'],self.q0)):
                    q=base.rotation_difference(_quat(self.obj.pose.bones[name]))
                    if q.w<0:q.negate()
                    v=np.array((q.x,q.y,q.z));length=float(np.linalg.norm(v))
                    x[3+i*3:6+i*3]=v*(2*np.arctan2(length,q.w)/length) if length>1e-12 else 0.
            if not coupled_torso_only and (evaluation_backend=='proxy' or (evaluation_backend=='auto' and len(self.obj.pose.bones)>=128)):
                from .body_proxy import EvaluationProxy
                proxy_started=time.perf_counter();preparation_paused=0.
                try:
                    p._update(self.obj)
                    seeds=set(self.binding['names']+self.binding['rotations']+self.binding['effectors']+[self.binding['root']])|set(self.lengths)
                    seeds.update(n for pair in frame_pairs.values() for n in pair)
                    if _emit_progress:
                        paused=time.perf_counter()
                        yield dict(phase='preparing',iteration=0,total_iterations=iterations,evaluations=evaluations)
                        preparation_paused+=time.perf_counter()-paused
                        self._validate()
                    proxy=EvaluationProxy(self.obj,seeds,defer=True)
                    preparation=proxy.prepare_steps(self.obj,seeds)
                    try:
                        for stage in preparation:
                            if cancel_requested is not None and cancel_requested():raise InterruptedError('Solve cancelled')
                            if _emit_progress:
                                paused=time.perf_counter()
                                yield dict(phase='preparing',iteration=0,total_iterations=iterations,evaluations=evaluations)
                                preparation_paused+=time.perf_counter()-paused
                                self._validate()
                    finally:preparation.close()
                    discrepancy=max(float(np.max(np.abs(np.array(self.obj.pose.bones[n].matrix)-np.array(proxy.obj.pose.bones[n].matrix)))) for n in seeds)
                    if discrepancy>2e-5:raise ValueError('Evaluation copy differs from the original rig')
                    evaluation_obj=proxy.obj
                except ValueError as exc:
                    if proxy:proxy.close();proxy=None
                    # A source invalidation at a yielded boundary is not a reason
                    # to retry against the original host rig.
                    self._validate()
                    if evaluation_backend=='proxy':raise
                    proxy_rejection=str(exc)
                proxy_init_ms=(time.perf_counter()-proxy_started-preparation_paused)*1000
            error,actual=evaluate(x)
            step=0
            for step in range(iterations):
                if step==priority_start:
                    # Final priority projection minimizes only explicit pins/orientation.
                    weights=np.where(mask,pin_weight,0.)[:,None]
                    rotation_weight=0.
                    damping=.001;error,actual=evaluate(x);jac=None
                if jacobian_mode=='dense' or jac is None or step-last_refresh>=3 or rejected>=2:
                    epsilon=1e-3 if directional else (1e-4 if frame_pairs else 1e-3);jac=np.empty((len(error),len(x)))
                    for j in range(len(x)):
                        trial=x.copy();trial[j]+=epsilon
                        plus=evaluate(trial)[0]
                        if directional:
                            trial[j]-=2*epsilon
                            jac[:,j]=(plus-evaluate(trial)[0])/(2*epsilon)
                        else:jac[:,j]=(plus-error)/epsilon
                        # Keep the number of host probes per checkpoint bounded.
                        if _emit_progress and (j+1)%(4 if directional else 8)==0:
                            apply_fit(x)  # Never yield with a finite-difference probe visible.
                            yield dict(phase='derivatives',iteration=step+1,total_iterations=iterations,evaluations=evaluations)
                            self._validate()
                    refreshes+=1;last_refresh=step;rejected=0
                normal=jac.T@jac
                metric=np.maximum(np.diag(normal),1.)
                update=np.linalg.solve(normal+np.diag(metric*damping),-jac.T@error)
                largest=max(np.linalg.norm(update[:3])/.1,max(np.linalg.norm(update[3:].reshape(-1,3),axis=1))/.25,1.)
                update/=largest;accepted=False
                for fraction in (1.,.5,.25,.125):
                    trial=x+update*fraction;new_error,new_actual=evaluate(trial)
                    if np.dot(new_error,new_error)<np.dot(error,error):
                        improvement=float(np.dot(error,error)-np.dot(new_error,new_error))
                        if jacobian_mode=='reuse':
                            delta=trial-x;denominator=float(delta@delta)
                            if denominator>1e-14:
                                jac+=np.outer(new_error-error-jac@delta,delta)/denominator
                        x=trial;error=new_error;actual=new_actual;accepted=True;damping=max(1e-4,damping*.5);break
                if not accepted:damping=min(1e5,damping*10);rejected+=1
                else:rejected=0
                self.trace.append(dict(step=step,score=float(error@error),pin=float(np.max(np.linalg.norm(actual[mask]-observations[mask],axis=1))),damping=damping,accepted=accepted))
                if _emit_progress:
                    apply_fit(x)
                    yield dict(phase='fitting' if step<priority_start else 'pins',iteration=step+1,
                        total_iterations=iterations,evaluations=evaluations,pin_error=self.trace[-1]['pin'])
                    self._validate()
                if accepted and improvement<1e-7 and np.max(np.linalg.norm(actual[mask]-observations[mask],axis=1))<2e-4 and _pole_error(actual,poles)<.01 and np.max(np.abs(limit_residual(evaluation_obj,True)),initial=0.)<1e-3 and (balance_constraint is None or np.linalg.norm(balance_constraint.residual(evaluation_obj,self.world_points(actual)))<2e-4):break
            apply_fit(x)
            for index,(name,orientation) in enumerate(desired_orientations.items(),1):
                matrix=orientation.to_matrix().to_4x4();matrix.translation=self.obj.pose.bones[name].head
                p._write_rotation(self.obj,name,matrix)
                if _emit_progress and index%2==0:
                    yield dict(phase='finishing',iteration=step+1,total_iterations=iterations,evaluations=evaluations)
                    self._validate()
                    if cancel_requested is not None and cancel_requested():raise InterruptedError('Contextual pose solve cancelled')
            actual=self.points();pin_error=float(np.max(np.linalg.norm(actual[mask]-observations[mask],axis=1)))
            length_error=max(abs((self.obj.pose.bones[n].tail-self.obj.pose.bones[n].head).length/value-1) for n,value in self.lengths.items() if value>1e-8)
            angle=_angle(desired_pelvis,self.obj.pose.bones[self.binding['names'][0]].matrix.to_quaternion())
            orientation_error=max(([angle] if pelvis_orientation_required else [])
                +[_angle(q,self.obj.pose.bones[n].matrix.to_quaternion()) for n,q in desired_orientations.items()]
                +[_angle(q,self.obj.pose.bones[n].matrix.to_quaternion()) for n,q in distributed_orientations.items()],default=0.)
            pole_error=_pole_error(actual,poles)
            limit_errors=limit_residual(self.obj)
            limit_error=float(np.max(np.abs(limit_errors),initial=0.))
            if limit_error>1e-3:
                owners=[name for name,value in rotation_limits.items() for _ in range(4 if 'bend' in value else 2)]
                worst=owners[int(np.argmax(np.abs(limit_errors)))]
                raise ValueError(f'Joint limits conflict with the requested pose or fitting did not converge: {worst}, error={limit_error:.6g} radians')
            if pin_error>2e-4 or length_error>.002 or orientation_error>.001 or pole_error>.01:
                raise ProjectionError(pin_error,length_error,orientation_error,pole_error,(time.perf_counter()-started)*1000,evaluations)
            balance_metrics=balance_constraint.verify(self.obj) if balance_constraint is not None else None
            return dict(profile=self.binding['profile'],model_sha256=MODEL_SHA256 if proposal_world is None else None,
                proposal_source='context_pose_model' if proposal_world is None else 'external_motion',learned_influence=learned_influence,balance=balance_metrics,
                joint_limit_error_radians=limit_error,requested_joint_limits=len(rotation_limits),requested_skeletal_limits=len(frame_pairs),requested_bend_planes=sum('bend' in v for v in rotation_limits.values()),
                orientation_error_radians=orientation_error,pole_error_radians=pole_error,requested_orientations=len(orientations_world),requested_poles=len(poles),
                neural_residual_norm=float(np.linalg.norm(residual)),pin_error=pin_error,length_error=length_error,pelvis_angle=angle,
                elapsed_ms=(time.perf_counter()-started)*1000,evaluations=evaluations,
                evaluation_scope='generic_objective_only',
                iterations=0 if coupled_torso_only else step+1,
                jacobian_mode=jacobian_mode,jacobian_refreshes=refreshes,derivative_scheme='central' if directional else 'forward',derivative_step=epsilon,
                evaluation_backend='proxy' if proxy else 'host',proxy_init_ms=proxy_init_ms,
                proxy_bones=len(proxy.needed) if proxy else 0,proxy_rejection=proxy_rejection,
                torso_coupling=torso_metrics,
                proposal_error=float(np.mean(np.linalg.norm(actual-proposal,axis=1))),
                proposal_rotation_error_radians=float(np.mean([_angle(q,self.obj.pose.bones[n].matrix.to_quaternion()) for n,q in zip(self.binding['names'],rotation_proposal)])) if rotation_proposal is not None else None,points=actual.copy())
        except BaseException:
            # GeneratorExit, keyboard interruption and explicit cancellation also restore ownership.
            w.restore_pose(self.obj,before);p._update(self.obj);raise
        finally:
            try:
                if proxy:proxy.close()
            finally:self.running=False

    def cancel(self):
        if self.running:raise ValueError('Close the active solve iterator before cancelling the session')
        self._validate()
        w.restore_pose(self.obj,self.source);rs.restore_values(self.obj,self.source_modes);self.closed=True
        _SESSIONS.pop(self.owner_key,None)
