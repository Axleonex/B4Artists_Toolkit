"""Behavioral checks for authored-only position interpolation and context isolation."""
from pathlib import Path
import sys,unittest,copy
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'training/b4artists_ml'))
sys.path.insert(0,str(ROOT))
from b4artists_ml.temporal_observations import Observations
from b4artists_ml.temporal_math import prepare

class RuntimeTrajectoryTests(unittest.TestCase):
    def observations(self,values=(0.,-.15,0.),frames=(1.,11.,21.),rotation=None,translation=None,scale=1.):
        rotation=np.eye(3) if rotation is None else rotation;translation=np.zeros(3) if translation is None else translation
        anchors=np.tile(np.arange(17)[:,None]*np.array([.1,.02,.05]),(len(values),1,1));anchors[:,:,2]+=np.array(values)[:,None]
        eye=np.broadcast_to(np.eye(3),(4,17,3,3)).copy();out=[]
        for i in range(len(values)-1):
            # Calibration may change its origin per interval, as native rigs do.
            world=anchors*scale@rotation.T+translation;origin=world[i,0]
            p=(np.stack((world[i],world[i+1],world[i]+3,world[i+1]-4))-origin)@rotation/scale
            out.append(Observations(p,eye.copy(),anchors[0],origin.copy(),rotation.copy(),scale,np.broadcast_to(np.eye(3),(17,3,3)).copy(),(frames[i+1]-frames[i])/30.,1/30.,True))
        return out,frames
    def test_priority_endpoints_are_exact(self):
        obs,frames=self.observations();fn=prepare(obs,frames,rotation='slerp')
        for i,o in enumerate(obs):np.testing.assert_array_equal(fn(i,o,np.array([0.,1.]))[0],o.positions[:2])
    def test_no_crouch_overshoot_and_peak_velocity_is_zero(self):
        obs,frames=self.observations();fn=prepare(obs,frames,rotation='slerp');np.testing.assert_array_equal(fn.tangents[1],np.zeros((17,3)))
        for i,o in enumerate(obs):
            points,_=fn(i,o,np.linspace(0,1,501));world=o.world_points(points)
            self.assertGreaterEqual(world[:,0,2].min(),-.1500000001);self.assertLessEqual(world[:,0,2].max(),1e-10)
    def test_nonuniform_timing_and_repeated_priorities(self):
        obs,frames=self.observations((0.,1.,1.,2.),(1.,5.,23.,41.));fn=prepare(obs,frames,rotation='slerp')
        points,_=fn(1,obs[1],np.linspace(0,1,101));np.testing.assert_allclose(points,np.broadcast_to(obs[1].positions[0],points.shape),atol=1e-12)
        for i in (0,2):
            points,_=fn(i,obs[i],np.linspace(0,1,101));world=obs[i].world_points(points)
            self.assertGreaterEqual(world[:,0,2].min(),i/2-1e-12);self.assertLessEqual(world[:,0,2].max(),i/2+1+1e-12)
    def test_source_neighbors_cannot_change_authored_positions_or_slerp(self):
        obs,frames=self.observations();other=copy.deepcopy(obs)
        for o in other:o.positions[2:]*=1e6;o.rotations[2:]=np.diag([-1.,-1.,1.])
        a=prepare(obs,frames,rotation='slerp');b=prepare(other,frames,rotation='slerp')
        for i in range(2):
            for x,y in zip(a(i,obs[i],np.linspace(0,1,19)),b(i,other[i],np.linspace(0,1,19))):np.testing.assert_array_equal(x,y)
    def test_common_rigid_transform_and_scale_equivariance(self):
        q=np.array([[0.,0.,1.],[1.,0.,0.],[0.,1.,0.]]);v=np.array([6.,-2.,10.]);obs,f=self.observations();other,_=self.observations(rotation=q,translation=v,scale=3.)
        a=prepare(obs,f,rotation='slerp');b=prepare(other,f,rotation='slerp')
        for i in range(2):
            t=np.linspace(0,1,31);x=obs[i].world_points(a(i,obs[i],t)[0]);y=other[i].world_points(b(i,other[i],t)[0]);np.testing.assert_allclose(y,x*3@q.T+v,rtol=0,atol=1e-12)
    def test_invalid_inputs_and_query_reject(self):
        obs,frames=self.observations()
        for f in [(1,1,21),(1,11), (1,11,float('nan')),(1,11,22)]:
            with self.assertRaises(ValueError):prepare(obs,f)
        with self.assertRaises(ValueError):prepare(obs,frames,rotation='invented')
        fn=prepare(obs,frames)
        for t in [[-1],[float('nan')],[[.5]]]:
            with self.assertRaises(ValueError):fn(0,obs[0],np.array(t))
        with self.assertRaises(ValueError):fn(True,obs[0],np.array([.5]))
    def test_disagreeing_shared_anchor_rejects(self):
        obs,frames=self.observations();obs[1].positions[0,0,0]+=.1
        with self.assertRaises(ValueError):prepare(obs,frames)
    def test_runtime_does_not_silently_use_source_rotation(self):
        obs,frames=self.observations()
        with self.assertRaises(ValueError):prepare(obs,frames,rotation='source')
if __name__=='__main__':unittest.main()
