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


def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.freqs
    fig.axes[0].plot(xs/1e6, ys, '.')
    fig.axes[0].set_xlabel('Detuning (MHz)')
    fig.axes[0].set_ylabel('Intensity (AU)')
    fig.canvas.draw()


class poly_fwm_ssbspec(Measurement1D):

    def __init__(self, qubit_info, fwm_infos, freqs, delay_t, ge_amp, fwm_amps,
                 seq=None, postseq=None, bgcor=False, **kwargs):
        self.qubit_info = qubit_info
        self.fwm_infos = fwm_infos
        self.freqs = freqs
        self.delay_t = delay_t
        self.ge_amp = ge_amp
        self.fwm_amps = fwm_amps
        self.bgcor = bgcor
        if seq is None:
            seq = Trigger(500)
        self.seq = seq
        self.postseq = postseq
        self.xs = freqs / 1e6       # For plot


        npoints = len(freqs)
        if bgcor:
            npoints += 1
        super(poly_fwm_ssbspec, self).__init__(npoints, residuals=False, infos=[qubit_info] + fwm_infos, **kwargs)
        self.data.create_dataset('freqs', data=freqs)

    def generate(self):
        s = Sequence()
        
        r = self.qubit_info.rotate_selective
        
        for i, df in enumerate(self.freqs):
            s.append(self.seq)
            poly_seq = []
            for i, fwm_info in enumerate(self.fwm_infos):
                g = DetunedSum(Square, self.delay_t, chans=fwm_info.sideband_channels)
                if df != 0:
                    period = 1e9 / df
                else:
                    period = 1e50
                g.add(self.fwm_amps[i], period)
                poly_seq += [g()]
            g = DetunedSum(Square, self.delay_t, chans=self.qubit_info.sideband_channels)
            if df != 0:
                period = 1e9 / df
            else:
                period = 1e50
            g.add(self.ge_amp, period)
            poly_seq += [g()]
                    
            s.append(Combined(poly_seq))
            s.append(Delay(50e3))
            s.append(r(np.pi, X_AXIS))
    
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

    def get_ys(self, data=None):
        ys = super(poly_fwm_ssbspec, self).get_ys(data)
        if self.bgcor:
            return ys[1:] - ys[0]
        return ys

    def analyze(self, data=None, fig=None):
        analysis(self, data, fig)
        self.fig = fig

