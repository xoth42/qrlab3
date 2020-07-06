"""
Time domaign measurement of the b^dagger^2 scheme. This displaces alice
and then runs the FWM tone for a variable amount of time. Should
show the characteristic time of the process to optimize.

Uses qubit1bob2 info which should be set to w_q - 2X_qb

NOTE: the fwm_info base must be SQUARE.

Jeff Gertler
"""


import numpy as np
from math import factorial
import matplotlib.pyplot as plt
from lib.math import fit
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

    fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3)

    params = lmfit.Parameters()
    params.add('ofs', value=np.min(ys))
    params.add('amplitude', value=np.max(ys))
    params.add('tau', value=xs[-1]/2.0, min=50.0)
    result = lmfit.minimize(exp_decay, params, args=(xs, ys))
#   lmfit.report_fit(params)
#   result2 = lmfit.minimize(exp_decay, result.params, args=(xs,ys))
    lmfit.report_fit(result.params)

    fig.axes[0].plot(xs/1e3, -exp_decay(result.params, xs, 0), label='Fit, tau = %.03f us +/- %.03f us '%(result.params['tau'].value/1000.0, result.params['tau'].stderr/1000.0))
    fig.axes[0].legend(loc=0)
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Time [us]')
    fig.axes[1].plot(xs, exp_decay(result.params, xs, ys), marker='s')

    fig.canvas.draw()
    meas.fit_params = result.params
    return result.params


class cat_pump_t1(Measurement1D):

    def __init__(self, qubit_info, qubit1bob2_info, fwm_info, delays, ge_amp, fwm_amp, 
                 fwm_switch, seq=None, postseq=None, 
                 extra_info=None, bgcor=False, **kwargs):
        self.qubit_info = qubit_info
        self.qubit1bob2_info = qubit1bob2_info
        self.fwm_info = fwm_info
        self.delays = delays
        self.fwm_switch = fwm_switch
        self.ge_amp = ge_amp
        self.fwm_amp = fwm_amp
        self.bgcor = bgcor
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.xs = self.delays/1e3

        npoints = len(self.delays)
        if bgcor:
            npoints *= 2
        super(cat_pump_t1, self).__init__(npoints, infos=(qubit_info, qubit1bob2_info, fwm_info), **kwargs)
        
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(delays)])

        self.data.create_dataset('delays', data=self.delays)
        self.data.set_attrs(
            ge_amp = ge_amp,
            fwm_amp = fwm_amp
        )

    def generate(self):
        s = Sequence()
        r = self.qubit1bob2_info.rotate_selective
             
        for dt in self.delays:
            s.append(Join([self.seq,
                          Constant(500, 1, chan=self.fwm_switch),
                          ]))
            if dt > 0:
                s.append(Join([Combined([Constant(int(dt), self.fwm_amp, chan=self.fwm_info.sideband_channels[0]),
                                         Constant(int(dt), self.fwm_amp, chan=self.fwm_info.sideband_channels[1]),           
                                         Constant(int(dt), self.ge_amp, chan=self.qubit_info.sideband_channels[0]),
                                         Constant(int(dt), self.ge_amp, chan=self.qubit_info.sideband_channels[1]),
                                         Constant(int(dt), 1, chan=self.fwm_switch),
                                         ])
                            ]))
            s.append(Delay(50e3))
            s.append(r(np.pi, X_AXIS))
    
            if self.postseq:
                s.append(self.postseq)
            s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
            s.append(Delay(1000))

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)
        return self.fit_params['tau'].value

