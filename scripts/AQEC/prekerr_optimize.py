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


def fit_amprabi(params, x, data):
    est = params['ofs'].value - params['amp'].value * np.cos(2*np.pi*x / params['period'].value + params['phase'].value)
    return data  - est


def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    n = len(meas.values)
    
    xs = meas.values
    ys1 = ys[:n]
    ys2 = ys[n:2*n]
    Ys = ys1-ys2

    fig.axes[0].clear()
#    fig.axes[0].plot(xs, Ys, '.')
    fig.axes[0].plot(xs, Ys)
    pf = np.polyfit(xs, Ys, 2)
    optimal = -pf[1]/pf[0]/2.0
    txt = 'optimal at = %.03f' % (optimal)
    fig.axes[0].plot(xs, pf[0]*xs*xs + pf[1]*xs + pf[2], label=txt)
    fig.axes[1].plot(xs, Ys-(pf[0]*xs*xs + pf[1]*xs + pf[2]))
    plt.xlabel(meas.parameter)
    fig.axes[0].legend()

    return optimal


class prekerr_optimize(Measurement1D):

    def __init__(self, qubit_info, cav_info, lib, comb_list, parameter, values, phase = 0, pump_time = 26e3, init_state = 'prekerr',
                 g_value=None, e_value=None, bgcor=True,
                 seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.cav_info = cav_info
        self.lib = lib
        self.comb_list = comb_list[:]
        self.parameter = parameter
        self.values = values
        self.phase = phase
        self.bgcor = bgcor
        self.init_state = init_state
        self.pump_time = pump_time

        self.famps = self.comb_list[0].amps[:]
        self.fphases = self.comb_list[0].phases[:]
        self.gamps = self.comb_list[1].amps[:]
        self.gphases = self.comb_list[1].phases[:]
        self.ss = self.comb_list[0].stark_shift
        self.ss_const = 23.04e6
        self.rot_const = 5.05e-12
        
        info = []
        for c in comb_list:
            info += [c.info]

        if seq is None:
            seq = Trigger(500)
        self.seq = seq
        self.postseq = postseq
    
        self.xs = self.values

        npoints = len(self.values)
        if self.bgcor:
            npoints = npoints*2
            self.xs = np.tile(self.xs, 2)
                
        super(prekerr_optimize, self).__init__(npoints, infos= [qubit_info, cav_info] + info, **kwargs)
        
        self.ampdata = self.data.create_dataset('amplitudes', shape=[npoints])
        self.data.create_dataset('values', data=self.values)


    def generate(self):
        r = self.qubit_info.rotate
        s = Sequence()
        
        phase = self.phase
        for i_bg in range(2):
                    
            if i_bg == 1 and not self.bgcor:
                continue
            
            for value in self.values:
                index = int(self.parameter[-1])
                if index == 9:
                    if 'fwm_amp' in self.parameter:
                        ss = self.ss
                        for i in range(4):
                            self.comb_list[0].amps[i] = self.famps[i]*value
                            ss += self.famps[i]**2 *(value**2-1) * self.ss_const
                        self.comb_list[0].stark_shift = ss
                        self.comb_list[1].stark_shift = -ss
                        phase = self.phase + self.pump_time*(ss-self.ss)*self.rot_const *2*np.pi
                    if 'ge_amp' in self.parameter:
                        for i in range(4):
                            self.comb_list[1].amps[i] = self.gamps[i]*value
                else:
                    if 'fwm_amp' in self.parameter:
                        self.comb_list[0].amps[index] = self.famps[index]*value
                        ss = self.ss + self.famps[index]**2 *(value**2-1) * self.ss_const
                        self.comb_list[0].stark_shift = ss
                        self.comb_list[1].stark_shift = -ss
                        phase = self.phase + self.pump_time*(ss-self.ss)*self.rot_const *2*np.pi
                    elif 'ge_amp' in self.parameter:
                        self.comb_list[1].amps[index] = self.gamps[index]*value
                    elif 'fwm_phase' in self.parameter:
                        self.comb_list[0].phases[index] = self.fphases[index]+value
                    elif 'ge_phase' in self.parameter:
                        self.comb_list[1].phases[index] = self.gphases[index]+value
                            
                
                s_temp = [self.seq]
                if self.init_state == 'prekerr':
                    s_temp += [self.lib.prekerr()]
                else:    
                    s_temp += [self.lib.mod4_prep(self.init_state)]
     
                poly_seq = []
                for c in self.comb_list:
                    poly_seq += c.get_poly_seq(self.pump_time - c.sigma*4, 0)
                s_temp += [Combined(poly_seq)]
                    
    #            s_temp += [self.lib.mod4_prep('+x')]
                if i_bg == 0:                
                    s_temp += [self.lib.mod4_decode(phase = phase)]
                else:
                    s_temp += [self.lib.mod4_decode(phase = phase-np.pi/2)]
                    
                if self.init_state == '+y' or self.init_state == '-y':
                    s_temp += [r(np.pi/2, X_AXIS)]                
                else:
                    s_temp += [r(np.pi/2, -Y_AXIS)]
                
                if self.postseq:
                    s_temp += [self.postseq]
                s_temp += [Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ])]
                s.append(Join(s_temp))
            
        for i in range(4):  #Reset the amps back
            self.comb_list[0].amps[i] = self.famps[i]
            self.comb_list[1].amps[i] = self.gamps[i]
            self.comb_list[0].phases[i] = self.fphases[i]
            self.comb_list[1].phases[i] = self.gphases[i]
        self.comb_list[0].stark_shift = self.ss
        self.comb_list[1].stark_shift = -self.ss
            
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def analyze(self, data=None, fig=None):
        return analysis(self, data, fig)

