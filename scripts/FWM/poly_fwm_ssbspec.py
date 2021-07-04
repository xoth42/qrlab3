"""


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
from lib.math import fit


def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.freqs

    try: # This is a placeholder until stes is implemented w/ Alazar.
        fig.axes[0].errorbar(xs/1e6, ys, yerr=meas.get_errorbars(), fmt='.', 
                         markersize = 0, ecolor='grey', linewidth=1)
    except:
        print('passed no errorbars')  
        
    f = fit.Lorentzian(xs, ys)
    if 0:
        h0 = np.max(ys)-np.min(ys)
        w0 = 0.05e6
        pos = xs[np.argmax(ys)]
        p0 = [np.min(ys), w0*h0, pos, w0]
    if 1:
        h0 = np.min(ys)-np.max(ys)
        w0 = 0.05e6
        pos = xs[np.argmin(ys)]
        p0 = [np.max(ys), w0*h0, pos, w0]
        p = f.fit(p0)
    txt = 'Center = %.03f MHz, FWHM = %.03f MHz' % (p[2]/1e6, p[3]/1e6)
    print('Fit gave: %s' % (txt,))

    fig.axes[0].plot(xs/1e6, ys, '.')
    fig.axes[0].set_xlabel('Detuning (MHz)')
    fig.axes[0].set_ylabel('Intensity (AU)')
    fig.axes[0].plot(xs/1e6, f.func(p, xs), label=txt)
    fig.canvas.draw()
    return p[2]


class poly_fwm_ssbspec(Measurement1D):

    def __init__(self, qubit_info, comb_list, freqs, delay_t, post_delay = 1e3,
                 seq=None, postseq=None, bgcor=False, **kwargs):
        self.qubit_info = qubit_info
        self.comb_list = comb_list
        self.freqs = freqs
        self.delay_t = delay_t
        self.post_delay = post_delay
        
        self.bgcor = bgcor
        if seq is None:
            seq = [Trigger(500)]
        self.seq = seq
        self.postseq = postseq
        self.xs = freqs / 1e6       # For plot

        # Setup all the temporary infos. We need these two add the pulses on the same channels
        infos = [comb.info for comb in comb_list]         

        npoints = len(freqs)
        if bgcor:
            npoints *= 2
        super(poly_fwm_ssbspec, self).__init__(npoints, residuals=False, infos=[qubit_info] + infos, **kwargs)
        self.data.create_dataset('freqs', data=freqs)

    def generate(self):
        s = Sequence()
        
        r = self.qubit_info.rotate_selective
        
        for df in self.freqs:
            for i_bg in range(2):
                if i_bg == 1 and not self.bgcor:
                    continue
                s_temp = self.seq[:]
                poly_seq = []
                for comb in self.comb_list:
                    poly_seq += comb.get_poly_seq(self.delay_t - comb.sigma*4, df)
                        
                s_temp += [Combined(poly_seq)]
                s_temp += [Delay(self.post_delay)]
                if i_bg == 0:
                    s_temp += [r(np.pi, X_AXIS)]
        
                if self.postseq:
                    s_temp += [self.postseq]
                    
                s_temp += [self.readout_driver.do_get_sequence()]
                s_temp += [Delay(2000)]
                s.append(Join(s_temp))
                
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def get_ys(self, data=None):
        ys = super(poly_fwm_ssbspec, self).get_ys(data)
        if self.bgcor:
            return ys[::2] - ys[1::2]
        return ys

    def analyze(self, data=None, fig=None):
        return analysis(self, data, fig)
        

