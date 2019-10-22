"""
time domain of the decay for all 6 qubit bloch points

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
import lmfit
import math
import time
import objectsharer as objsh


def exp_decay(params, x, data):
    est = params['ofs'] + params['amplitude'] * np.exp(-x / params['tau'].value)
    return data - est

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.delays
    num_delays = len(xs)
    
    for i, axis in enumerate(['x', 'y', 'z']):
        YS =  ys[i*num_delays : (i+1)*num_delays]

        fig.axes[0].plot(xs/1e3, YS, ms=3, label = axis)
        
        Xs = xs[:num_delays]
        YS = YS[:num_delays]
        params = lmfit.Parameters()
        params.add('ofs', value=np.min(YS))
        params.add('amplitude', value=np.max(YS))
        params.add('tau', value=Xs[-1]/2.0, min=50.0)
        result = lmfit.minimize(exp_decay, params, args=(Xs, YS))
#        lmfit.report_fit(params)
#        result2 = lmfit.minimize(exp_decay, result.params, args=(xs,ys))
        lmfit.report_fit(result.params)

        fig.axes[0].plot(Xs/1e3, -exp_decay(result.params, Xs, 0), label='Fit, tau = %.03f us +/- %.03f us '%(result.params['tau'].value/1000.0, result.params['tau'].stderr/1000.0))
        fig.axes[0].legend(loc=0)
        fig.axes[0].set_ylabel('Intensity [AU]')
        fig.axes[0].set_xlabel('Time [us]')        
                

    fig.axes[0].legend(loc=0)
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Time [us]')

    fig.canvas.draw()
    
    return result.params['tau'].value/1000.0


class time_bloch(Measurement1D):

    def __init__(self, qubit_info, delays,
                 seq=None, postseq=None, fidelity = False, **kwargs):
        self.qubit_info = qubit_info
        self.delays = delays
        self.fidelity = fidelity
        if seq is None:
            seq = Trigger(500)
        self.seq = seq
        self.postseq = postseq
    
        n_rep = 3

        xs_single = self.delays/1e3
        self.xs = np.tile(xs_single, n_rep)
        npoints = len(self.delays) * n_rep
                
        super(time_bloch, self).__init__(npoints, infos= qubit_info, **kwargs)
        
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(delays)])
        self.data.create_dataset('delays', data=self.delays)


    def generate(self):
        r = info.rotate
        s = Sequence()
        for axis in ['x', 'y', 'z']:
            for dt in self.delays:
                s.append(self.seq)
                if dt > 0:
                    s.append(Delay(dt))
                if axis is 'x':
                    s.append(r(Y_AXIS, np.pi/2))
                if axis is 'y':
                    s.append(r(X_AXIS, np.pi/2))
                
                s.append(Delay(self.post_delay))
        
                if self.postseq:
                    s.append(self.postseq)
                s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
                s.append(Delay(2000))
                
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def analyze(self, data=None, fig=None):
        return analysis(self, data, fig)

