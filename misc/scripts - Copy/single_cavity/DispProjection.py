# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 10:58:00 2013

@author: Brian Vlastakis
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
        ret =  p[0] * np.exp(-np.square(p[1] * x)) * np.power(np.abs(p[1]*x), (2*self.proj_num)) / factorial(self.proj_num)
        return ret

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.displacements
    fig.axes[0].plot(xs, ys, 'ks', ms=3)
    amp0 = np.max(ys) - np.min(ys)
    scaling0 = 1
    print 'Amplitude estimate: %.03f ' % (amp0)

    fPoiss = PoissonFit(meas.proj_num, xs, ys)
    p0 = [amp0, scaling0]
#    plt.plot(xs/1e3, ft2.func(p0, xs), label='Guess')
    p = fPoiss.fit(p0)
    fig.axes[0].plot(xs, fPoiss.func(p, xs), label='Fit, Amp=%.03f , Scaling=%.03f '%(p[0], p[1]))
    fig.axes[0].legend()
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Displacement [alpha]')

    fig.axes[1].plot(xs, ys - fPoiss.func(p, xs))
    fig.canvas.draw()
    return p[1]


class DispProjection(Measurement1D):

    def __init__(self, qubit_info, cav_info, dmax, N, proj_num, sigma=None, seq=None, delay=0, saveas=None, bgcor=False, update = False, extra_info=None, **kwargs):
        self.qubit_info = qubit_info
        self.cav_info = cav_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.proj_num = proj_num
        self.delay = delay
        self.saveas = saveas
        self.bgcor = bgcor
        self.update_ins = update
        self.extra_info = extra_info
        self.displacements = np.linspace(0, dmax, N)
        self.xs = self.displacements

        npoints = len(self.displacements)
        if self.bgcor:
            npoints *= 2
        super(DispProjection, self).__init__(npoints, **kwargs)
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

        r = self.qubit_info.rotate
        c = self.cav_info.rotate
        for i, alpha in enumerate(self.displacements):
            for i_bg in range(2):
                if i_bg == 1 and not self.bgcor:
                    continue

                s.append(self.seq)

                add = c(np.abs(alpha), np.angle(alpha))
                if i_bg == 0:
                    add = Join([add, r(np.pi, X_AXIS)])
                else:
                    add = Join([add, Combined([
                        Constant(1, 0, chan=r.chans[0]),
                        Constant(1, 0, chan=r.chans[1]
                    )])])

                if self.delay:
                    add = Join([Delay(self.delay), add])

                add = Join([add, Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ])])

                s.append(add)

        s = Sequencer(s)
        seqs = s.render()
        if self.qubit_info.ssb:
            self.qubit_info.ssb.modulate(seqs)
        if self.cav_info.ssb:
            self.cav_info.ssb.modulate(seqs)
        if type(self.extra_info) in (types.TupleType, types.ListType):
            for info in self.extra_info:
                if info.ssb:
                    info.ssb.modulate(seqs)
        elif self.extra_info and self.extra_info.ssb:
            self.extra_info.ssb.modulate(seqs)
#        s.plot_seqs(seqs)

        self.seqs = seqs
        return seqs

    def get_ys(self, data=None):
        ys = super(DispProjection, self).get_ys(data)
        if self.bgcor:
            return ys[::2] - ys[1::2]
        return ys

    def analyze(self, data=None, fig=None):
        scaling = analysis(self, data, fig)
        cav = mclient.instruments.get(self.cav_info.insname)
        area_new = cav.get_pi_area() / scaling
        if self.update_ins:
            print 'Setting cavity area scaling by %.03f' % scaling
            cav.set_pi_area(area_new)
        else:
            print 'Estimated new area: %.03f (not setting)' % area_new
        return area_new