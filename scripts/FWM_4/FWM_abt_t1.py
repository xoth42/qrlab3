"""
Time domaign measurement of the ab^dagger scheme. This displaces alice
and then runs the FWM tone for a variable amount of time. Should
show the characteristic time of the process to optimize.

The qubit info should be set to w_ge - x_qb so that it reads if there is 
a photon in bob or not.

Needs the fwm drive generator set properly before this is run (power and 
frequency). Needs a gatable generator or a switch.

Currently this is setup for a switch on the cavity line too.

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


class FWM_abt_t1(Measurement1D):

    def __init__(self, qubit_info, cav_info, delays, disp, 
                 fwm_channel, switch_channel, seq=None, postseq=None, 
                 extra_info=None, bgcor=False, **kwargs):
        self.qubit_info = qubit_info
        self.cav_info = cav_info
        self.delays = delays
        self.disp = disp
        self.fwm_channel = fwm_channel
        self.switch_channel = switch_channel
        self.bgcor = bgcor
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.xs = self.delays/1e3

        npoints = len(self.delays)
        if bgcor:
            npoints *= 2
        super(FWM_abt_t1, self).__init__(npoints, infos=(qubit_info, cav_info), **kwargs)
        
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(delays)])

        self.data.create_dataset('delays', data=self.delays)
        self.data.set_attrs(
            disp=disp
        )

    def generate(self):
        s = Sequence()
        r = self.qubit_info.rotate_selective
        c = self.cav_info.rotate
             
        for dt in self.delays:
            s.append(self.seq)
            s.append(Constant(int(500), 1, chan=self.switch_channel))
            s.append(Combined([
                c(np.abs(self.disp), np.angle(self.disp)),
                Constant(int(self.cav_info.w*4.0), 1, chan=self.switch_channel)
                ]))        
            if dt != 0:
                s.append(Constant(int(dt), 1, chan=self.fwm_channel))
                   
            s.append(Delay(50e3))   # was 50e6 initially. but that is too long (Juliang)            
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

