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
    ax.set_xlabel('times')
    ax.set_ylabel('rel_phase')
    fig.canvas.draw()

class CRtuning_time_phase(Measurement2D):

#The purpose here is to sweep over time and detuning for the combined pulse without the pi pulse on the control qubit

    def __init__(self, gate_info1, gate_info2, times, rel_phases, amp, phase, rel_amp, sigma, 
                 update=False, seq=None, r_axis=0, fix_phase=True, cancel_info=None,
                 fix_period=None, repeat_pulse=1, postseq=None, selective=False, control_pi=False, **kwargs):
        self.gate_info1 = gate_info1
        self.gate_info2 = gate_info2
        self.cancel_info = cancel_info
        self.times = times
        self.rel_phases = rel_phases
#        self.xs = np.array([times,times]).transpose().flatten() / 1e3      # For plotting purposes        
        self.xs=times
        self.ys=rel_phases
        
        self.amp = amp
        self.phase = phase
        self.rel_amp = rel_amp
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
            super(CRtuning_time_phase, self).__init__(npoints, infos=(gate_info1, gate_info2, cancel_info), **kwargs)
        else:
            super(CRtuning_time_phase, self).__init__(npoints, infos=(gate_info1, gate_info2), **kwargs)
        self.data.create_dataset('two_axes', data=self.two_axes, dtype=np.complex)


    def generate(self):
        s = Sequence()
        ampI = self.amp * np.cos(self.phase)
        ampQ = self.amp * np.sin(self.phase)
        chs = self.gate_info1.sideband_channels
        chs2 = self.gate_info1.sideband_channels2
#        chs3 = self.cancel_info.sideband_channels   #needs to be commented out if cancel info is used

        for rel_phase in self.rel_phases:

            ampIc = self.amp *self.rel_amp * np.cos(self.phase+rel_phase)
            ampQc = self.amp *self.rel_amp * np.sin(self.phase+rel_phase)
            for plen in self.times:
                
                s.append(self.seq)    
    
                if plen >= 0:
                    if self.cancel_info is not None:
                        g=Repeat(Combined([
                        GaussSquare(int(plen), ampI, self.sigma, chan=chs[0]),
                        GaussSquare(int(plen), ampQ, self.sigma, chan=chs[1]),
                        GaussSquare(int(plen), ampIc, self.sigma, chan=chs2[0]),
                        GaussSquare(int(plen), ampQc, self.sigma, chan=chs2[1]),            
                        GaussSquare(int(plen), self.cancel_info.pi_amp, self.sigma, chan=chs3[0]),
                        ]), self.repeat_pulse)
                    else:       
                        g=Repeat(Combined([
                            GaussSquare(int(plen), ampI, self.sigma, chan=chs[0]),
                            GaussSquare(int(plen), ampQ, self.sigma, chan=chs[1]),
                            GaussSquare(int(plen), ampIc, self.sigma, chan=chs2[0]),
                            GaussSquare(int(plen), ampQc, self.sigma, chan=chs2[1]),            
                        ]), self.repeat_pulse)

    
                if self.control_pi==True:             
                    s.append(self.gate_info2.rotate(np.pi,0))
                    s.append(g)
#                    s.append(self.gate_info2.rotate(np.pi,0)) #Chen changed to always measure with control qubit in e
                else:
                    s.append(g)
                    s.append(self.gate_info2.rotate(np.pi,0)) #Chen changed to always measure with control qubit in e
                     
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
        ys = super(CRtuning_time_phase, self).get_ys(data)
        return ys

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data=data, fig=fig)


