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
    est = params['ofs'].value - params['amp'].value * np.cos(2*np.pi* (x-params['phase'].value) / params['period'].value)
    return data  - est


def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    
    phases = meas.phases
    num_phases = len(phases)
    data = ys[0*num_phases : 1*num_phases]
    bg = ys[1*num_phases : 2*num_phases]

    fig.axes[0].clear()
    for ys in [bg, data]:
        params = lmfit.Parameters()
        params.add('ofs', value=np.average(ys))
        params.add('amp', value=np.max(ys) - np.average(ys), min = 0)
        params.add('phase', value=phases[np.argmin(ys)])
        params.add('period', value= np.pi, vary = False)
        
        result = lmfit.minimize(fit_amprabi, params, args=(phases, ys))
        
        txt = 'Amp = %.03f +- %.03e\nPhase = %.03f +- %.03e' % (result.params['amp'].value, 
                                                                                result.params['amp'].stderr, 
                                                                                result.params['phase'].value, 
                                                                                result.params['phase'].stderr)
        
        fig.axes[0].plot(phases, -fit_amprabi(result.params, phases, 0), label=txt)
        fig.axes[1].plot(phases, fit_amprabi(result.params, phases, ys), marker='s')
        
        lmfit.report_fit(result.params)
        fig.axes[0].legend(loc=0)
    
        fig.axes[0].plot(phases, ys, '.')
        plt.xlabel('phase')

    return result.params


class prekerr_calibrate(Measurement1D):

    def __init__(self, qubit_info, cav_info, lib, comb_list, phases = np.linspace(0, np.pi, 11), pump_time = 26e3, init_state='prekerr',
                 g_value=None, e_value=None,
                 seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.cav_info = cav_info
        self.lib = lib
        self.comb_list = comb_list
        self.phases = phases
        self.pump_time = pump_time
        self.init_state = init_state

        info = []
        for c in comb_list:
            info += [c.info]

        if seq is None:
            seq = Trigger(500)
        self.seq = seq
        self.postseq = postseq
    
#        self.xs = self.phases
        self.xs = np.tile(self.phases, 2)
        npoints = len(self.phases)*2
                
        super(prekerr_calibrate, self).__init__(npoints, infos= [qubit_info, cav_info] + info, **kwargs)
        
        self.ampdata = self.data.create_dataset('amplitudes', shape=[npoints])
        self.data.create_dataset('phases', data=self.phases)


    def generate(self):
        r = self.qubit_info.rotate
        s = Sequence()
        for phase in self.phases:
            s_temp = [self.seq]
            
            if self.init_state == 'prekerr':
                s_temp += [self.lib.prekerr()]
            else:
                s_temp += [self.lib.mod4_prep(self.init_state)]
#            s_temp += [self.lib.mod4_prep('+x')]
                     
            poly_seq = []
            for c in self.comb_list:
                poly_seq += c.get_poly_seq(self.pump_time - c.sigma*4, 0)
            s_temp += [Combined(poly_seq)]
                
            s_temp += [self.lib.mod4_decode(phase = phase)]
            
            if self.init_state == '+y':
                s_temp += [r(np.pi/2, X_AXIS)]
            else:
                s_temp += [r(np.pi/2, -Y_AXIS)]
                        
            if self.postseq:
                s_temp += [self.postseq]
            s_temp += [Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])]
#            s_temp += [Delay(1000)]
            s.append(Join(s_temp))
            
        for phase in self.phases:
            s_temp = [self.seq]
                
            s_temp += [self.lib.mod4_prep('+x')]
            s_temp += [self.lib.mod4_decode(phase = phase)]

            s_temp += [r(np.pi/2, -Y_AXIS)]
            
            if self.postseq:
                s_temp += [self.postseq]
            s_temp += [Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])]

            s.append(Join(s_temp))                

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def analyze(self, data=None, fig=None):
        return analysis(self, data, fig)

