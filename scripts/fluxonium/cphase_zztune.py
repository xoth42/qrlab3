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
    zs = zs.reshape(len(meas.ys), len(meas.xs))
    xs, ys = meas.get_plotxsys()
    ax = fig.axes[0]
    plt.sca(ax)
    pc = ax.pcolormesh(xs, ys, zs, cmap=plt.get_cmap('RdBu'))
    fig.colorbar(pc)

    ax.set_xlim(xs.min()), xs.max()
    ax.set_ylim(ys.min(), ys.max())
    ax.set_xlabel('times (ns)')
    ax.set_ylabel('detuning (MHz)')
    fig.canvas.draw()

class cphase_zztune(Measurement2D):

#The purpose here is to sweep over time and detuning for the combined pulse without the pi pulse on the control qubit

    def __init__(self, ZZ_info, offset_info, gate_info1, gate_info2, times, detunings, amp=0.35, phase=0,  sigma=5, update=False, seq=None, r_axis=0, fix_phase=True,
                 fix_period=None, repeat_pulse=1, postseq=None, selective=False,  **kwargs):
        self.ZZ_info = ZZ_info
        self.offset_info = offset_info
        self.gate_info1 = gate_info1
        self.gate_info2 = gate_info2
        self.times = times
#        self.xs = np.array([times,times]).transpose().flatten() / 1e3      # For plotting purposes
        self.detunings = -detunings
        self.ys = detunings / 1e6       # For plot
        self.xs=times

        self.amp = amp
        self.phase = phase
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

        
        XS, YS = np.meshgrid(self.xs, self.ys)
        self.two_axes = (-XS + 1j*YS)

        npoints = self.two_axes.size
        
        super(cphase_zztune, self).__init__(npoints, infos=(ZZ_info,offset_info, gate_info1, gate_info2), **kwargs)
        self.data.create_dataset('two_axes', data=self.two_axes, dtype=np.complex)



    def generate(self):
        s = Sequence()
#        ampI = self.amp * np.cos(self.phase)
#        ampQ = self.amp * np.sin(self.phase)
#        ampIc = 0.008
#        ampQc = -0.0713
        chs = self.ZZ_info.sideband_channels
        ampI = self.amp * np.cos(0)
        ampQ = self.amp * np.sin(0)

#        chs2 = self.offset_info.sideband_channels
            
        for df in self.detunings:
            for plen in self.times:
                
                s.append(self.seq)    
                
#                g1 = DetunedGaussSquare(int(plen), self.sigma, chs)
##                g1 = DetunedSum(self.gate_info1.rotate_selective.base, self.gate_info1.w_selective, chans=self.gate_info1.sideband_channels)
#                if df != 0:
#                    period = 1e9 / df
#                else:
#                    period = 1e50
#                g1.add(self.amp, period)

                g1= Combined([GaussSquare(int(plen), ampI, self.sigma, chan=chs[0]),
                              GaussSquare(int(plen), ampQ, self.sigma, chan=chs[1])])                   
                    
#                g2 = Combined([Constant((int(plen)+self.sigma*3), ampIc, chan=chs2[0]), 
#                               Constant((int(plen)+self.sigma*3), ampQc, chan=chs2[1])])
#                g2 = Constant((int(plen)+self.sigma*3), 0.005, chan=chs2[0])

#WHY THIS DOESN'T WORK WHEN I REPEAT s.append(Combined([g1(),g2]))

                
#                g3 = DetunedGaussSquare(int(plen), self.sigma, chs)
##                g1 = DetunedSum(self.gate_info1.rotate_selective.base, self.gate_info1.w_selective, chans=self.gate_info1.sideband_channels)
#                if df != 0:
#                    period = 1e9 / df
#                else:
#                    period = 1e50
#                g3.add(self.amp, period)
#                    
#                g4 = Combined([Constant((int(plen)+self.sigma*3), ampIc, chan=chs2[0]), 
#                               Constant((int(plen)+self.sigma*3), ampQc, chan=chs2[1])])

                s.append(self.gate_info1.rotate(np.pi/2,0))
                s.append(g1)
                s.append(Combined([self.gate_info2.rotate(np.pi,0), self.gate_info1.rotate(np.pi,0)]))
#                s.append(Combined([g3(),g4]))
                s.append(g1)
                s.append(self.gate_info1.rotate(np.pi/2,0))

#                s.append(self.gate_info1.rotate(np.pi/2,0))
#                s.append(Combined([g1(),g2]))
#                s.append(self.gate_info2.rotate(np.pi,0))
                    
                if self.postseq:
                    s.append(self.postseq)
                s.append(Delay(10))
                s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
                s.append(Delay(2000))
            
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs


    def get_ys(self, data=None):
        ys = super(cphase_zztune, self).get_ys(data)
        return ys

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data=data, fig=fig)


