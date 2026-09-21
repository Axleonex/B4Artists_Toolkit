"""Independent small tanh network and Adam optimizer; NumPy CPU only.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np


def initialize(inputs,hidden,outputs,seed=20260906,dtype=np.float32):
    rng=np.random.default_rng(seed)
    return dict(w0=rng.normal(0,np.sqrt(2/(inputs+hidden)),(inputs,hidden)).astype(dtype),
                b0=np.zeros(hidden,dtype=dtype),
                w1=rng.normal(0,.01,(hidden,outputs)).astype(dtype),b1=np.zeros(outputs,dtype=dtype))


def forward(params,x):
    hidden=np.tanh(x@params['w0']+params['b0'])
    return hidden@params['w1']+params['b1']


def loss_and_grad(params,x,target,weights,regularization=1e-5):
    hidden=np.tanh(x@params['w0']+params['b0'])
    output=hidden@params['w1']+params['b1']
    normalizer=float(np.sum(weights))
    if normalizer<=0:raise ValueError('Training weights must contain positive mass')
    delta=(output-target)*weights/normalizer
    loss=.5*np.sum((output-target)**2*weights)/normalizer
    loss+=.5*regularization*(np.sum(params['w0']**2)+np.sum(params['w1']**2))
    dh=(delta@params['w1'].T)*(1-hidden**2)
    grad=dict(w0=x.T@dh+regularization*params['w0'],b0=dh.sum(axis=0),
              w1=hidden.T@delta+regularization*params['w1'],b1=delta.sum(axis=0))
    return float(loss),grad


class Adam:
    def __init__(self,params,rate=.001):
        self.rate=rate;self.step_number=0
        self.m={k:np.zeros_like(v) for k,v in params.items()}
        self.v={k:np.zeros_like(v) for k,v in params.items()}

    def step(self,params,grad):
        self.step_number+=1
        for key in params:
            self.m[key]*=.9;self.m[key]+=.1*grad[key]
            self.v[key]*=.999;self.v[key]+=.001*grad[key]**2
            m=self.m[key]/(1-.9**self.step_number)
            v=self.v[key]/(1-.999**self.step_number)
            params[key]-=self.rate*m/(np.sqrt(v)+1e-8)
