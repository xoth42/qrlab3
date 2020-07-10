# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 18:53:00 2020

@author: Wang_Lab
"""

import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import h5py
import lmfit

def exp_decay(params, x, data):
    est = params['ofs'] + params['amplitude'] * np.exp(-x / params['tau'].value)
    return data - est

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.delays

    fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3)

    params = lmfit.Parameters()
    params.add('ofs', value=np.min(ys))
    params.add('amplitude', value=np.max(ys)-np.min(ys))
    params.add('tau', value=len(xs)*1000/4.0, min=0)
    result = lmfit.minimize(exp_decay, params, args=(xs, ys))
    lmfit.report_fit(result.params)

    fig.axes[0].plot(xs/1e3, -exp_decay(result.params, xs, 0), label='Fit, tau = %.03f us +/- %.03f us'%(result.params['tau'].value/1000.0, result.params['tau'].stderr/1000.0))
    fig.axes[0].legend(loc=0)
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Time [us]')

    fig.axes[1].plot(xs, exp_decay(result.params, xs, ys), marker='s')
    fig.canvas.draw()
    return result.params


class FT1Measurement_mixer(Measurement1D):

    def __init__(self, ge_info, ef_info, mixer_info, delays, seq=None, **kwargs):
        self.ge_info = ge_info
        self.ef_info = ef_info
        self.mixer_info = mixer_info
        self.delays = delays
        self.xs = delays / 1e3      # For plotting purposes

        super(FT1Measurement_mixer, self).__init__(len(delays), infos=(ge_info, ef_info, mixer_info), **kwargs)
        self.data.create_dataset('delays', data=delays)
        if seq is None:             #Ebru:Added the seq part for cooling
            seq = Trigger(250)
        self.seq = seq        

    def generate(self):
        s = Sequence()
#        s.append(Constant(250, 0, chan=4))
#        s.append(Constant(250, 1, chan='4m1'))
        
        
        r = self.ge_info.rotate
        r_ef = self.ef_info.rotate
        for i, dt in enumerate(self.delays):
            s.append(Join([
                self.seq,   #Ebru: Changed Trigger(dt=250) to self.seq for cooling
                r(np.pi, 0),
                r_ef(np.pi, 0),
            ]))
#            s.append(Combined([
#                    Constant(25000, 0.1, chan=self.qubit_info.sideband_channels[0]),
#                    Constant(25000, 0.1, chan=self.qubit_info.sideband_channels[1]),
#            ]))
            s.append(Delay(dt))
            s.append(r(np.pi/2, 0))

#            if self.postseq is not None:
#                s.append(self.postseq)
#            s.append(self.get_readout_pulse())
            
#            s.append(Delay(20))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    Constant(self.readout_info.pulse_len, self.mixer_info.pi_amp, chan=self.mixer_info.channels[0])
            ]))
            s.append(Delay(2000))
            #Ebru: changed the delay from 1000 to 20000.

#            s.append(Repeat(Delay(1000), 20))   # wait for alazar acquisition to finish
#            s.append(Combined([
#                Repeat(Constant(8000, 0.4, chan=self.QswB.sideband_channels[0]), 70),
#                Repeat(Constant(8000, 0.4, chan=self.QswB.sideband_channels[1]), 70),
#                Repeat(Constant(8000, 1, chan='1m1'), 70),     # Readout pump tone switch
#                Repeat(Constant(8000, 0.0001, chan=5), 70),         # Qubit/Readout master switch
#            ]))

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)
        return self.fit_params['tau'].value
