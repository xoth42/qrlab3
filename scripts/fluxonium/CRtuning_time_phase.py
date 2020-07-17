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

    def __init__(self, qubit_info, qubit_info2, qubit2_info, times, rel_phases, amp=0.35, phase=0, rel_amp=0.2, sigma=5, 
                 update=False, seq=None, r_axis=0, fix_phase=True,
                 fix_period=None, repeat_pulse=1, postseq=None, selective=False, control_pi=False, **kwargs):
        self.qubit_info = qubit_info
        self.qubit_info2 = qubit_info2
        self.qubit2_info = qubit2_info
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
        
        super(CRtuning_time_phase, self).__init__(npoints, infos=(qubit_info,qubit_info2, qubit2_info), **kwargs)
        self.data.create_dataset('two_axes', data=self.two_axes, dtype=np.complex)


    def generate(self):
        s = Sequence()
#        ampI = self.amp * np.cos(self.phase)
#        ampQ = self.amp * np.sin(self.phase)
#        ampIc = self.amp *self.rel_amps * np.cos(self.phase+self.rel_phase)
#        ampQc = self.amp *self.rel_amps * np.sin(self.phase+self.rel_phase)
        chs = self.qubit_info.sideband_channels
        chs2 = self.qubit_info2.sideband_channels

        for rel_phase in self.rel_phases:
            for plen in self.times:
                
                s.append(self.seq)    
    
#                if plen > 0:
                g=(Combined([
        #                GaussSquare(int(plen), ampI, self.sigma, chan=chs[0]),
        #                GaussSquare(int(plen), ampQ, self.sigma, chan=chs[1]),
        #                GaussSquare(int(plen), ampIc, self.sigma, chan=chs2[0]),
        #                GaussSquare(int(plen), ampQc, self.sigma, chan=chs2[1]),            
                        Constant(int(plen), self.amp * np.cos(self.phase), chan=chs[0]),
                        Constant(int(plen), self.amp * np.sin(self.phase), chan=chs[1]),
                        Constant(int(plen), self.amp *self.rel_amp * np.cos(self.phase+rel_phase), chan=chs2[0]),
                        Constant(int(plen), self.amp *self.rel_amp * np.sin(self.phase+rel_phase), chan=chs2[1]),              
                    ]))
    
                if self.control_pi==True:             
                    s.append(self.qubit2_info.rotate(np.pi,0))
                    s.append(g)
                    s.append(self.qubit2_info.rotate(np.pi,0))
                else:
                     s.append(g)
                     
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


