"""
optimizes for some oct pulse parameter using an encoding and decoding process

Jeff Gertler
"""

import numpy as np
from math import factorial
import matplotlib.pyplot as plt
#from lib.math import fit
import copy
import mclient
from measurement import Measurement1D
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from pulseseq import OCTlib
import lmfit
import math
import time
import objectsharer as objsh
from scipy.linalg import fractional_matrix_power

def final_rotation(axis, r):
    if axis is 'mz':
        return [r(np.pi, X_AXIS)]
    elif axis is 'z':
        return []
    elif axis is 'x':
        return [r(np.pi/2, -Y_AXIS)]
    elif axis is 'y':
        return [r(np.pi/2, X_AXIS)]
    elif axis is 'mx':
        return [r(np.pi/2, Y_AXIS)]
    elif axis is 'my':
        return [r(-np.pi/2, X_AXIS)]                    
    else: 
        return []          


def density_matrix(x, y, z):
    I = np.array([[1,0],[0,1]])
    sigmax = np.array([[0,1],[1,0]])
    sigmay = np.array([[0,-1j],[1j,0]])
    sigmaz = np.array([[1,0],[0,-1]])
    return .5 * (I + x * sigmax + y * sigmay + z*sigmaz)

def fidelity(a, b):
    sqrta = fractional_matrix_power(a, .5)
    m = np.matmul(np.matmul(sqrta, b), sqrta)
    return np.power(np.trace(fractional_matrix_power(m, .5)), 2)

def exp_decay(params, x, data):
    est = params['ofs'] + params['amplitude'] * np.exp(-x / params['tau'].value)
    return data - est

def analysis(meas, data=None, fig=None):
    
    if meas.target_state == '+x': target_state = [1,0,0]
    elif meas.target_state == '-x': target_state = [-1,0,0]
    elif meas.target_state == '+y': target_state = [0,1,0]
    elif meas.target_state == '-y': target_state = [0,-1,0]
    elif meas.target_state == '+z': target_state = [0,0,1]
    elif meas.target_state == '-z': target_state = [0,0,-1]
    
#    ys, fig = meas.get_ys_fig(data, fig)
#    
#    equators = (ys[2*num_values : 3*num_values] + ys[3*num_values : 4*num_values])*0.5
#    print equators       
#    e_values = meas.e_value * np.ones(num_values)
#    g_values = equators*2 - e_values
#    print g_values
#    
#    XS = (g_values - ys[0*num_values : (1)*num_values]) / (g_values - e_values) * 2 - 1
#    YS = (g_values - ys[1*num_values : (2)*num_values]) / (g_values - e_values) * 2 - 1
#    ZS = (g_values - ys[2*num_values : (3)*num_values]) / (g_values - e_values) * 2 - 1
#    mZS = (g_values - ys[3*num_values : (4)*num_values]) / (g_values - e_values) * 2 - 1
#    fig.axes[0].plot(xs, XS, label = 'sigmaX')
#    fig.axes[0].plot(xs, YS, label = 'sigmaY')
#    fig.axes[0].plot(xs, ZS, label = 'sigmaZ')
#    fig.axes[0].plot(xs, mZS, label = '-sigmaZ')
#    fig.axes[0].set_ylim(-1, 1)
#    fig.axes[0].legend()
    
    ys, fig = meas.get_ys_fig(data, fig)
    
    xs = meas.values
    num_values = len(xs)
    XSv = ys[0*num_values : 1*num_values]
    YSv = ys[1*num_values : 2*num_values]
    ZSv = ys[2*num_values : 3*num_values]
    mXSv = ys[3*num_values : 4*num_values]
    mYSv = ys[4*num_values : 5*num_values]
    mZSv = ys[5*num_values : 6*num_values]    
    
    equators = (XSv+YSv+ZSv+mXSv+mYSv+mZSv) / 6.0
    print(equators)
    
    pf = np.polyfit(xs, equators, 1)
    eq_values = pf[0]*xs + pf[1]
    e_values = meas.e_value * np.ones(num_values)
    g_values = eq_values*2 - meas.e_value
    print(g_values)
    
    XS = (g_values - XSv) / (g_values - e_values) * 2 - 1
    YS = (g_values - YSv) / (g_values - e_values) * 2 - 1
    ZS = (g_values - ZSv) / (g_values - e_values) * 2 - 1
    mXS = (g_values - mXSv) / (g_values - e_values) * 2 - 1
    mYS = (g_values - mYSv) / (g_values - e_values) * 2 - 1
    mZS = (g_values - mZSv) / (g_values - e_values) * 2 - 1
    fig.axes[0].plot(xs, XS, label = 'sigmaX')
    fig.axes[0].plot(xs, YS, label = 'sigmaY')
    fig.axes[0].plot(xs, ZS, label = 'sigmaZ')
    fig.axes[0].plot(xs, mXS, label = '-sigmaX')
    fig.axes[0].plot(xs, mYS, label = '-sigmaY')
    fig.axes[0].plot(xs, mZS, label = '-sigmaZ')
    fig.axes[0].set_ylim(-1, 1)
    fig.axes[0].legend()
    
    rXS = (XS-mXS)/2.
    rYS = (YS-mYS)/2.
    rZS = (ZS-mZS)/2.    
    
    f = np.zeros_like(XS)
    for i in range(num_values):
        f[i] = fidelity(density_matrix(target_state[0], target_state[1], target_state[2]),
                        density_matrix(rXS[i], rYS[i], rZS[i]))
    fig.axes[1].plot(xs, f)
    plt.xlabel(meas.parameter)

    return None

    
    


class encode_decode(Measurement1D):

    def __init__(self, qubit_info, cav_info, parameter, 
                 values, target_state,
                 q_amp=0, cav_amp=0, time_shift=0, g_value=None, e_value=None,
                 seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.cav_info = cav_info
        self.parameter = parameter
        self.values = values
        self.target_state = target_state
        self.g_value = g_value
        self.e_value = e_value
        self.q_amp = q_amp
        self.cav_amp = cav_amp
        self.time_shift = time_shift
        if seq is None:
            seq = Trigger(500)
        self.seq = seq
        self.postseq = postseq
    
        n_rep = 6

        xs_single = self.values
        self.xs = np.tile(xs_single, n_rep)
        npoints = len(self.values) * n_rep
                
        super(encode_decode, self).__init__(npoints, infos= [qubit_info, cav_info], **kwargs)
        
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(values)])
        self.data.create_dataset(self.parameter, data=self.values)


    def generate(self):
        r = self.qubit_info.rotate
        rs = self.qubit_info.rotate_selective
        s = Sequence()
        for axis in ['x', 'y', 'z', 'mx', 'my', 'mz']:
            for value in self.values:
                s_temp = [self.seq]
                
                q_amp = self.q_amp
                cav_amp = self.cav_amp
                time_shift = self.time_shift
                phase = 0.04
                if self.parameter is 'q_amp':
                    q_amp = value
                elif self.parameter is 'cav_amp':
                    cav_amp = value
                elif self.parameter is 'time_shift':
                    time_shift = value
                elif self.parameter is 'phase':
                    phase = value
                else:
                    print('no parameter changed')
                    
                lib = OCTlib.octlib(q_amp, cav_amp, time_shift, self.qubit_info, self.cav_info)
                
                s_temp += [lib.mod4_prep(self.target_state)]
                
                s_temp += [lib.mod4_decode(phase = phase, secondary=False)]
                
                s_temp += final_rotation(axis, r)
#                s_temp += [rs(np.pi, 0)]
                
                if self.postseq:
                    s_temp += [self.postseq]
                s_temp += [Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ])]
                s_temp += [Delay(2000)]
                s.append(Join(s_temp))
                
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def analyze(self, data=None, fig=None):
        return analysis(self, data, fig)

