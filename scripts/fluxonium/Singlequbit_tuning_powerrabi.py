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
    zs_new = np.zeros(zs.size/2)
    for i in range(zs.size/2):
#        zs_new[i] = zs[2*i+1]
        
        zs_new[i] = zs[2*i+1]-zs[2*i]
    print(zs_new)
    xs_new = np.zeros(len(meas.xs)/2)
    for i in range(len(meas.xs)/2):
        xs_new[i] = meas.xs[2*i]
    
    zs_new = zs_new.reshape(len(meas.ys), len(xs_new))
    ys=meas.ys
    ax = fig.axes[0]
    plt.sca(ax)
    pc = ax.pcolormesh(xs_new, meas.ys, zs_new, cmap=plt.get_cmap('RdBu'))
    fig.colorbar(pc)
#    ax = fig.axes[0]
#    plt.sca(ax)
#    pc = ax.pcolormesh(xs_new, meas.ys, zs_new, cmap=plt.get_cmap('RdBu'))
#    fig.colorbar(pc)

    ax.set_xlim(xs_new.min()), xs_new.max()
    ax.set_ylim(ys.min(), ys.max())
    ax.set_xlabel('amp')
    ax.set_ylabel('phase')
    fig.canvas.draw()

class Singlequbit_tuning_powerrabi(Measurement2D):

#The purpose here is to sweep over time and detuning for the combined pulse without the pi pulse on the control qubit

    def __init__(self, qubit_info, qubit_info2, qubit2_info, rel_amps, rel_phases,
                 update=False, seq=None, r_axis=0, fix_phase=True,
                 fix_period=None, repeat_pulse=1, postseq=None, selective=False, **kwargs):
        self.qubit_info = qubit_info
        self.qubit_info2 = qubit_info2
        self.qubit2_info = qubit2_info
        self.rel_amps = rel_amps

        self.xs = np.array([rel_amps,rel_amps]).transpose().flatten()      # For plotting purposes 
        
        self.rel_phases = rel_phases
        self.ys=rel_phases / np.pi
        
        
        if seq is None:
            seq = Trigger(1000)
        self.seq = seq
        self.postseq = postseq
        self.fix_phase = fix_phase
        self.fix_period = fix_period
        self.repeat_pulse = repeat_pulse
        self.r_axis = r_axis
        self.selective = selective
        
        XS, YS = np.meshgrid(self.xs, self.ys)
        self.two_axes = (-XS + 1j*YS)
        npoints = self.two_axes.size

#        XS2, YS = np.meshgrid(self.xs2, self.ys)
#
#        self.two_axes_double = (-XS2 + 1j*YS)
#
#        npoints_double = self.two_axes_double.size       



        super(Singlequbit_tuning_powerrabi, self).__init__(npoints, infos=(qubit_info,qubit_info2, qubit2_info), **kwargs)
        self.data.create_dataset('two_axes', data=self.two_axes, dtype=np.complex)

    def generate(self):
        s = Sequence()
#        ampI = self.amp * np.cos(self.phase)
#        ampQ = self.amp * np.sin(self.phase)
#        ampIc = self.amp *self.rel_amps * np.cos(self.phase+self.rel_phase)
#        ampQc = self.amp *self.rel_amps * np.sin(self.phase+self.rel_phase)
        chs = self.qubit_info.sideband_channels
        chs2 = self.qubit_info2.sideband_channels


        for rel_amps in self.rel_amps:
            for rel_phases in self.rel_phases:

                
                '''Without pi pulse'''
                s.append(self.seq)    
    
                g=(Combined([self.qubit_info.rotate(np.pi,0), self.qubit_info2.rotate(0,rel_phases, rel_amps)]))

                s.append(g)
#                s.append(g)
                if self.postseq:
                    s.append(self.postseq)
                s.append(Delay(10))
                s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
                s.append(Delay(2000))

                '''With pi pulse'''
                s.append(self.seq)    
                s.append(self.qubit2_info.rotate(np.pi,0))    
                g=(Combined([self.qubit_info.rotate(np.pi,0), self.qubit_info2.rotate(0,rel_phases, rel_amps)]))
                s.append(g)
                s.append(self.qubit2_info.rotate(np.pi,0))    
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
        ys = super(Singlequbit_tuning_powerrabi, self).get_ys(data)
        return ys

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data=data, fig=fig)


