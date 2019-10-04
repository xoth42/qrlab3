"""
time domain of multiple tones read out on mulitple qubit frequencies


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
    
    for i, info in enumerate(meas.qubit_list):
        if meas.bgcor:
            YS =  ys[i*num_delays : (i+1)*num_delays] - ys[-num_delays:]
        else:
            YS =  ys[i*num_delays : (i+1)*num_delays]

        fig.axes[0].plot(xs/1e3, YS, ms=3, label = info.insname)
        
        Xs = xs[4:num_delays]
        YS = YS[4:num_delays]
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


class poly_time_domain(Measurement1D):

    def __init__(self, comb_list, qubit_list, delays, post_delay = 1e3,
                 seq=None, postseq=None, bgcor=False, **kwargs):
        self.comb_list = comb_list
        self.qubit_list = qubit_list
        self.delays = delays
        self.post_delay = post_delay
        self.bgcor = bgcor
        if seq is None:
            seq = Trigger(500)
        self.seq = seq
        self.postseq = postseq
    
        if bgcor:
            n_rep = len(qubit_list)+1
        else:
            n_rep = len(qubit_list)
        xs_single = self.delays/1e3
        self.xs = np.tile(xs_single, n_rep)
        npoints = len(self.delays) * n_rep
        
        infos = [comb.info for comb in comb_list]
        
        super(poly_time_domain, self).__init__(npoints, infos=infos + qubit_list, **kwargs)
        
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(delays)])
        self.data.create_dataset('delays', data=self.delays)
        self.data.set_attrs(
                fwm_amps = comb_list[0].amps,
                ge_amps = comb_list[1].amps,
                stark_shift = comb_list[0].stark_shift
        )

    def generate(self):
        s = Sequence()
        
        for info in self.qubit_list:
            r = info.rotate_selective
            
            for dt in self.delays:
                s.append(self.seq)
                if dt > 0:
                    poly_seq = []
                    for comb in self.comb_list:
                        poly_seq += comb.get_poly_seq(dt - comb.sigma*4, 0)
                        
                    s.append(Combined(poly_seq))
                s.append(Delay(self.post_delay))
                s.append(r(np.pi, X_AXIS))
        
                if self.postseq:
                    s.append(self.postseq)
                s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
                s.append(Delay(2000))
                
        if self.bgcor:
            for dt in self.delays:
                s.append(self.seq)
                if dt > 0:
                    poly_seq = []
                    for comb in self.comb_list:
                        poly_seq += comb.get_poly_seq(dt - comb.sigma*4, 0)
                        
                    s.append(Combined(poly_seq))
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

