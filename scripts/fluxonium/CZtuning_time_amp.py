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

#    ax.set_xlim(xs.min()), xs.max()
#    ax.set_ylim(ys.min(), ys.max())
    ax.set_xlabel('times')
    ax.set_ylabel('amp')
    fig.canvas.draw()

class CRtuning_time_amp(Measurement2D):

#The purpose here is to sweep over time and detuning for the combined pulse without the pi pulse on the control qubit

    def __init__(self, gate_info1, gate_info2, ZZ_info, times, amps, amp=0.35, phase=0,  sigma=5, 
                 update=False, seq=None, r_axis=0, fix_phase=True, cancel_info=None,
                 fix_period=None, repeat_pulse=1, postseq=None, selective=False, control_pi=False, **kwargs):
        self.gate_info1 = gate_info1
        self.gate_info2= gate_info2
        self.cancel_info = cancel_info
        self.ZZ_info = ZZ_info
        self.times = times
        self.amps = amps
#        self.xs = np.array([times,times]).transpose().flatten() / 1e3      # For plotting purposes        
        self.xs=times
        self.ys=amps
        
        self.phase = phase
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
        self.control_pi = control_pi
        
        XS, YS = np.meshgrid(self.xs, self.ys)
        self.two_axes = (-XS + 1j*YS)

        npoints = self.two_axes.size
        
        if cancel_info is not None:
            super(CRtuning_time_amp, self).__init__(npoints, infos=(gate_info1, gate_info2, cancel_info, ZZ_info), **kwargs)
        else:
            super(CRtuning_time_amp, self).__init__(npoints, infos=(gate_info1, gate_info2, ZZ_info), **kwargs)
        self.data.create_dataset('two_axes', data=self.two_axes, dtype=np.complex)

    def generate(self):

        s = Sequence()
#        chs2 = self.offset_info.sideband_channels
        chs = self.ZZ_info.sideband_channels

#        chs3 = self.cancel_info.sideband_channels

        for amp in self.amps:
            for plen in self.times:

                ampI = amp * np.cos(self.phase)
                ampQ = amp * np.sin(self.phase)
                    
                s.append(self.seq)
                if plen >= 0:
    #                s.append(Delay(int(plen)))
                    g1= Combined([GaussSquare(int(plen), ampI, self.sigma, chan=chs[0]),
                                  GaussSquare(int(plen), ampQ, self.sigma, chan=chs[1])])                   
                    s.append(self.gate_info1.rotate(np.pi/2,0))
                    for j in range(self.repeat_pulse):
                        s.append(g1)
                    s.append(Combined([self.gate_info2.rotate(np.pi,0), self.gate_info1.rotate(np.pi,0)]))
                    for j in range(self.repeat_pulse):
                        s.append(g1)
    
                    s.append(self.gate_info1.rotate(np.pi/2,0))
        
                s.append(Delay(5))
                
                
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
        ys = super(CRtuning_time_amp, self).get_ys(data)
        return ys

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data=data, fig=fig)


