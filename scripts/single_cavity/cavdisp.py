# -*- coding: utf-8 -*-
"""
Cavity displacement and projection measurement, useful to calibrate
displacements.

by Brian Vlastakis, Reinier Heeres
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

class PoissonFit(fit.Function):
    '''
    Poissonian distribution given photon projection: a * exp(- (b * x)**2 /2) * (b *x)**n / sqrt(factorial(m))

     parameters:
        a = amplitude
        b = alpha scaling
        n = photon projection (fixed)
    '''

    def __init__(self, proj_num, *args, **kwargs):
        self.proj_num = proj_num
        super(PoissonFit, self).__init__(*args, **kwargs)

    def func(self, p, x=None):
        p, x = self.get_px(p, x)
        ret =  p[2] + p[0] * np.exp(-np.square(p[1] * x)) * np.power(np.abs(p[1]*x), (2*self.proj_num)) / factorial(self.proj_num)
        return ret

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.displacements
    fig.axes[0].plot(xs, ys, 'ks', ms=3)
    ofs0 = np.min(ys)
    amp0 = np.max(ys) - np.min(ys)
    scaling0 = 1
    print 'Amplitude estimate: %.03f ' % (amp0)

    fPoiss = PoissonFit(meas.proj_num, xs, ys)
#    p0 = [ofs0, amp0, scaling0] # JEFF this order seems totally wrong. I might be an idiot though...
    p0 = [amp0, scaling0, ofs0]
    print('p0', p0)
    fig.axes[0].plot(xs, p0[2] + p0[0] * np.exp(-np.square(p0[1] * xs)) * np.power(np.abs(p0[1]*xs), (2*meas.proj_num)) 
                / factorial(meas.proj_num), label='Guess')
    p = fPoiss.fit(p0)
    print('p', p)
    fig.axes[0].plot(xs, fPoiss.func(p, xs), label='Fit, Ofs=%.03f, Amp=%.03f , Scaling=%.03f '%(p[2], p[0], p[1]))
    fig.axes[0].legend()
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Displacement [alpha]')

    fig.axes[1].plot(xs, ys - fPoiss.func(p, xs))
    fig.canvas.draw()
    return p[1]

class CavDisp(Measurement1D):

    def __init__(self, qubit_info, cav_info, dmax, N, proj_num, seq=None, postseq=None,
                 delay=0, bgcor=True, update=False, Qswitch_infoA=None, Qswitch_infoB=None, **kwargs):
        self.qubit_info = qubit_info
        self.cav_info = cav_info
        self.QswA = Qswitch_infoA
        self.QswB = Qswitch_infoB
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.proj_num = proj_num
        self.delay = delay
        self.bgcor = bgcor
        self.update_ins = update
        self.displacements = np.linspace(0, dmax, N)
        self.xs = self.displacements

        npoints = len(self.displacements)
        if self.bgcor:
            npoints *= 2
        super(CavDisp, self).__init__(npoints, infos=(qubit_info, cav_info), **kwargs)
        self.data.create_dataset('displacements', data=self.displacements)
        self.data.set_attrs(
            delay=delay,
            bgcor=bgcor
        )

    def generate(self):
        '''
        If bg = True generate background measurement, i.e. no qubit pi pulse
        '''

        s = Sequence()

        r = self.qubit_info.rotate_selective
        c = self.cav_info.rotate
        for i, alpha in enumerate(self.displacements):
            for i_bg in range(2):
                if i_bg == 1 and not self.bgcor:
                    continue

                s.append(self.seq)
                s.append(c(np.abs(alpha), np.angle(alpha)))
                if i_bg == 0:
                    s.append(r(np.pi, X_AXIS))
                else:
                    s.append(Delay(self.qubit_info.w_selective*4))

                if self.delay:
                    s.append(Delay(self.delay))

                if self.postseq:
                    s.append(self.postseq)

                s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))

            if self.QswA is not None or self.QswB is not None:
                s.append(Repeat(Delay(1000), 30))   # wait for alazar acquisition to finish
                s.append(Combined([
                    Repeat(Constant(7000, 0.35, chan=self.QswA.sideband_channels[0]), 100),
                    Repeat(Constant(7000, 0.35, chan=self.QswA.sideband_channels[1]), 100),
                    Repeat(Constant(7000, 0.20, chan=self.QswB.sideband_channels[0]), 100),
                    Repeat(Constant(7000, 0.20, chan=self.QswB.sideband_channels[1]), 100),
                    Repeat(Constant(7000, 1, chan='1m1'), 100),     # Readout pump tone switch
#                    Repeat(Constant(7000, 0.0001, chan=5), 100),         # Qubit/Readout master switch
                    ]))

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def get_ys(self, data=None):
        ys = super(CavDisp, self).get_ys(data)
        if self.bgcor:
            return ys[::2] - ys[1::2]
        return ys

    def analyze(self, data=None, fig=None):
        self.scaling = analysis(self, data, fig)
        cav = mclient.instruments.get(self.cav_info.insname)
        amp_new = cav.get_pi_amp() / self.scaling
        if self.update_ins:
            print 'Setting cavity amp scaling by %.03f' % self.scaling
            cav.set_pi_amp(amp_new)
        else:
            print 'Estimated new amp: %.03f (not setting)' % amp_new
        return amp_new