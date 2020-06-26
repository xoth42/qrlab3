"""

Two tone cavity cooling spec. Converts storage to readout

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

#    f = fit.Lorentzian(xs, ys)
#    h0 = np.max(ys)-np.min(ys)
#    w0 = 0.05e6
#    pos = xs[np.argmax(ys)]
#    p0 = [np.min(ys), w0*h0, pos, w0]
#    p = f.fit(p0)
#    txt = 'Center = %.03f MHz, FWHM = %.03f MHz' % (p[2]/1e6, p[3]/1e6)
#    print 'Fit gave: %s' % (txt,)

    fig.axes[0].plot(xs/1e6, ys, '.')
    fig.axes[0].set_xlabel('Detuning (MHz)')
    fig.axes[0].set_ylabel('Intensity (AU)')
    fig.canvas.draw()
    return None


class FWM_cavity_cooling(Measurement1D):

    def __init__(self, qubit_info, storage_info, reservoir_info, freqs, storage_amp, 
                 reservoir_amp,delay_t, post_delay = 10e3,
                 seq=None, postseq=None, bgcor=False, **kwargs):
        self.qubit_info = qubit_info
        self.storage_info = storage_info
        self.reservoir_info = reservoir_info
        self.freqs = freqs
        self.delay_t = delay_t
        self.post_delay = post_delay
        self.storage_amp = storage_amp
        self.reservoir_amp = reservoir_amp
        
        self.bgcor = bgcor
        if seq is None:
            seq = Trigger(500)
        self.seq = seq
        self.postseq = postseq
        self.xs = freqs / 1e6       # For plot

        # Setup all the temporary infos. We need these two add the pulses on the same channels

        npoints = len(freqs)
        if bgcor:
            npoints *= 2
        super(FWM_cavity_cooling, self).__init__(npoints, residuals=False, infos=[qubit_info, storage_info, reservoir_info], **kwargs)
        self.data.create_dataset('freqs', data=freqs)

    def generate(self):
        s = Sequence()
        for i, df in enumerate(self.freqs):
            gS = DetunedGaussSquare(self.delay_t, 100, chans=self.storage_info.sideband_channels)
            if df != 0:
                period = 1e9 / df
            else:
                period = 1e50
            gS.add(self.storage_amp, period)

            gR = DetunedGaussSquare(self.delay_t, 100, chans=self.reservoir_info.sideband_channels)
            if df != 0:
                period = 1e9 / (200e6) 
            else:
                period = 1e50
            gR.add(self.reservoir_amp, period)

            s.append(Join([
                self.seq,
                self.storage_info.rotate(2, 0),
                Combined([gS(), gR()]),
                self.qubit_info.rotate_selective(np.pi, 0)
                ]))
            s.append(self.postseq)
            s.append(Combined([
                     Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                     Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                     ]))

#            s.append(Repeat(Delay(1000), 20))   # wait for alazar acquisition to finish
#            s.append(Combined([
#                Repeat(Constant(8000, 0.6, chan=self.QswB.sideband_channels[0]), 70),
#                Repeat(Constant(8000, 0.6, chan=self.QswB.sideband_channels[1]), 70),
#                Repeat(Constant(8000, 1, chan='1m1'), 70),     # Readout pump tone switch
#                Repeat(Constant(8000, 0.0001, chan=5), 70),         # Qubit/Readout master switch
#            ]))

        s = self.get_sequencer(s)
        seqs = s.render()

        return seqs

    def get_ys(self, data=None):
        ys = super(FWM_cavity_cooling, self).get_ys(data)
        if self.bgcor:
            return ys[::2] - ys[1::2]
        return ys

    def analyze(self, data=None, fig=None):
        return analysis(self, data, fig)
        

