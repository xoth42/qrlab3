# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 15:42:10 2013

@author: Brian Vlastakis
"""

import numpy as np
import matplotlib.pyplot as plt

from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement2D
from lib.math import fit


def analysis(delays, displacements, data, ax=None, bgcor=False, plotdx=None, plotdy = None):
    if bgcor:
        data = data[::2] - data[1::2]

    XS = delays
    YS = np.angle(displacements)
    ZS = data.reshape(XS.shape)

    if plotdx is not None:
        axes = plt.subplots(nrows = 1, ncols = 2)
        plt.pcolormesh(plotdx, plotdy, ZS)
    else:
        plt.pcolormesh(XS, YS, ZS)
    ax = plt.gca()
    plt.colorbar()

    ax.set_xlim(np.min(plotdx), np.max(plotdx))
    ax.set_ylim(np.min(plotdy), np.max(plotdy))
    ax.set_xlabel(r'$Delay \{ns \}$')
    ax.set_ylabel(r'$Angle \{\phi \}$')

class RotFrameTest(Measurement2D):

    def __init__(self, qubit_info, cav_info, tmax, Nt, mag, angle, bgcor=False, extra_info=None,saveas=None, **kwargs):
        self.qubit_info = qubit_info
        self.cav_info = cav_info
        self.bgcor = bgcor
        self.mag = mag
        self.extra_info = extra_info
        self.saveas = saveas

        xs = np.linspace(0, tmax, Nt)
        delta = (xs[1] - xs[0])/2
        self.plotdx = np.linspace(0-delta, tmax+delta, Nt+1)#np.linspace(0-delta, tmax+delta, Nt+1)

        angle_list = np.linspace(-angle, angle, 3)
        delta2 = (angle_list[1] - angle_list[0])/2
        self.plotdy = np.linspace(-angle-delta2, angle+delta2, 4)

        ys = mag * np.exp(1j * angle_list)

        XS, YS = np.meshgrid(xs, ys)
        self.delay_times = XS
        self.displacements = YS


        npoints = len(xs)*len(ys)
        if bgcor:
            npoints *= 2
        super(RotFrameTest, self).__init__(npoints, **kwargs)
        self.data.create_dataset('delay_times', data=self.delay_times, dtype=np.float)
        self.data.create_dataset('displacements', data = self.displacements, dtype=np.complex)

    def generate(self):
        '''
        If bg = True generate background measurement, i.e. without qubit pi pulse
        '''

        s = Sequence()

        r = self.qubit_info.rotate
        c = self.cav_info.rotate
        delay_list = self.delay_times.flatten()
        alpha_list = self.displacements.flatten()
        npoints = len(delay_list)

        for i in range(npoints):
            for i_bg in range(2):
                if i_bg == 1 and not self.bgcor:
                    continue

                s.append(Trigger(250))

                alpha = alpha_list[i]
                dispPulseIni = c(np.abs(alpha), 0)
                dispPulse = c(-np.abs(alpha), np.angle(alpha))
                #s.append(dispPulse)

                delay_time = delay_list[i]
                delayPulse = Constant(delay_time, 0.0, chan=self.cav_info.channels[0])
                #delayPulse = smartConstant(delay_time, [0], chans = self.cav_info.channels)
                combo = Join([dispPulseIni,delayPulse,dispPulse])
                if i_bg ==0:
                    combo = Join([combo, r(np.pi, X_AXIS)])
                else:
                    combo = Join([combo, Combined([
                        Constant(1, 0, chan=r.chans[0]),
                        Constant(1, 0, chan=r.chans[1])
                    ])])

                combo = Join([combo, Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ])])

                s.append(combo)

        s = Sequencer(s)
        seqs = s.render()
        #seqs = join_all_small_elements(seqs)

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

        self.seqs=seqs
        return seqs

    def analyze(self, data=None, ax=None):
        ZS, pax = self.get_ys_ax(data, ax)
        ret = analysis(self.delay_times, self.displacements, ZS, pax, bgcor=self.bgcor, plotdx=self.plotdx, plotdy=self.plotdy)
        if self.title:
            plt.title(self.title)
        if self.saveas:
            plt.savefig(self.saveas)
