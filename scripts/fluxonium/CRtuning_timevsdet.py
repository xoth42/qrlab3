# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 11:08:29 2020

@author: WangLabPC7
"""

import numpy as np
import matplotlib.pyplot as plt
from measurement import Measurement2D
#from lib.math import fit
from pulseseq.sequencer import *
from pulseseq.pulselib import *


def analysis(meas, data=None, fig=None):
    zs, fig = meas.get_ys_fig(data, fig)
    zs = zs.reshape(len(meas.xs), len(meas.ys))
    xs, ys = meas.get_plotxsys()
    ax = fig.axes[0]
    plt.sca(ax)
    pc = ax.pcolormesh(xs, ys, zs, cmap=plt.get_cmap('RdBu'))
    fig.colorbar(pc)

    ax.set_xlim(xs.min()), xs.max()
    ax.set_ylim(ys.min(), ys.max())
    ax.set_xlabel('times')
    ax.set_ylabel('detuning')
    fig.canvas.draw()

class CRtuning_timevsdet(Measurement2D):

#The purpose here is to sweep over time and detuning for the combined pulse without the pi pulse on the control qubit

    def __init__(self, qubit_info, qubit_info2, qubit2_info, times, detunings, amp=0.35, phase=0, rel_amp=1, rel_phase=1, sigma=5, update=False, seq=None, r_axis=0, fix_phase=True,
                 fix_period=None, repeat_pulse=1, postseq=None, selective=False, control_pi=False,  **kwargs):
        self.qubit_info = qubit_info
        self.qubit_info2 = qubit_info2
        self.qubit2_info = qubit2_info
        self.times = times
#        self.xs = np.array([times,times]).transpose().flatten() / 1e3      # For plotting purposes
        self.detunings = -detunings
        self.ys = detunings / 1e6       # For plot
        self.xs=times

        self.amp = amp
        self.phase = phase
        self.rel_amp = rel_amp
        self.rel_phase = rel_phase
        self.update_ins = update
        if seq is None:
            seq = Trigger(1000)
        self.seq = seq
        self.postseq = postseq
        self.fix_phase = fix_phase
        self.fix_period = fix_period
        self.repeat_pulse = repeat_pulse
        self.r_axis = r_axis
        self.selective = selective
        self.sigma = sigma
        self.control_pi=control_pi

        
        XS, YS = np.meshgrid(self.xs, self.ys)
        self.two_axes = (-XS + 1j*YS)

        npoints = self.two_axes.size
        
        super(CRtuning_timevsdet, self).__init__(npoints, infos=(qubit_info,qubit_info2, qubit2_info), **kwargs)
        self.data.create_dataset('two_axes', data=self.two_axes, dtype=np.complex)





    def generate(self):
        s = Sequence()
        ampI = self.amp * np.cos(self.phase)
        ampQ = self.amp * np.sin(self.phase)
        ampIc = self.amp *self.rel_amp * np.cos(self.phase+self.rel_phase)
        ampQc = self.amp *self.rel_amp * np.sin(self.phase+self.rel_phase)
        chs = self.qubit_info.sideband_channels
        chs2 = self.qubit_info2.sideband_channels
        

            
        s.append(self.seq)    

        for df in self.detunings:
            for plen in self.times:
                
                g1 = DetunedGaussSquare(int(plen), self.sigma, self.chans=chs[0])
#                if df != 0:
#                    period = 1e9 / df
#                else:
#                    period = 1e50
#                    g1.add(ampI, period)
#
#                g2 = DetunedGaussSquare(int(plen), self.sigma, chan=chs[1])
#                if df != 0:
#                    period = 1e9 / df
#                else:
#                    period = 1e50
#                    g2.add(ampQ, period)
#                    
#                g1c = DetunedGaussSquare(int(plen), self.sigma, chan=chs2[0])
#                if df != 0:
#                    period = 1e9 / df
#                else:
#                    period = 1e50
#                    g1c.add(ampIc, period)
#
#                g2c = DetunedGaussSquare(int(plen), self.sigma, chan=chs2[1])
#                if df != 0:
#                    period = 1e9 / df
#                else:
#                    period = 1e50
#                    g2c.add(ampQc, period)
#


                if self.control_pi==True:
             
                    s.append(Join[(self.qubit2_info.rotate(np.pi,0), Combined([g1,g2,g1c,g2c]),s.append(self.qubit2_info.rotate(np.pi,0)))])
                else:
#                    s.append(Combined([g1,g2,g1c,g2c]))
                    s.append(g1)
                if self.postseq:
                    s.append(self.postseq)
                s.append(Delay(10))
                s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
                s.append(Delay(3000))
            
            
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs


    def get_ys(self, data=None):
        ys = super(CRtuning_timevsdet, self).get_ys(data)
        return ys

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data=data, fig=fig)


