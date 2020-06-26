"""
Time domaign measurement of the ab scheme. This pumps readout
and runs the FWM tone for a variable amount of time. 

Can track any number of states specified by different qubit objects
with differnt detunings


Jeff Gertler
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
import lmfit
import math
import time
import objectsharer as objsh


def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.decaytimes
    num_delays = len(xs)
    
    for i, info in enumerate(meas.qubit_list):
        if meas.bgcor:
            fig.axes[0].plot(xs/1e3, ys[i*num_delays : (i+1)*num_delays] - ys[-num_delays:], ms=3, label = info.insname)
        else:
            fig.axes[0].plot(xs/1e3, ys[i*num_delays : (i+1)*num_delays], ms=3, label = info.insname)
        

    fig.axes[0].legend(loc=0)
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Time [us]')

    fig.canvas.draw()


class ab_time_domain(Measurement1D):

    def __init__(self, fwm_info, drive_info, qubit_list, decaytimes, pumptime, fwm_amp, drive_amp, 
                 fwm_switch, measdelay=5e3, seq=None, postseq=None, bgcor=False,
                 **kwargs):
        self.fwm_info = fwm_info
        self.drive_info = drive_info
        self.qubit_list = qubit_list
        self.pumptime = pumptime
        self.decaytimes = decaytimes
        self.measdelay = measdelay
        self.fwm_switch = fwm_switch
        self.drive_amp = drive_amp
        self.fwm_amp = fwm_amp
        self.bgcor = bgcor
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
    
        if bgcor:
            n_rep = len(qubit_list)+1
        else:
            n_rep = len(qubit_list)
        xs_single = self.decaytimes/1e3
        self.xs = np.tile(xs_single, n_rep)

        npoints = len(self.decaytimes) * n_rep
        
        super(ab_time_domain, self).__init__(npoints, infos=[fwm_info, drive_info] + qubit_list, **kwargs)
        
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(decaytimes)])

        self.data.create_dataset('decaytimes', data=self.decaytimes)
        self.data.set_attrs(
            drive_amp = drive_amp,
            fwm_amp = fwm_amp,
            pumptime = pumptime
        )

    def generate(self):
        s = Sequence()
        
        for info in self.qubit_list:
            r = info.rotate_selective
            for decayt in self.decaytimes:
                s.append(Join([self.seq,
                              Constant(250, 1, chan=self.fwm_switch),
                              ]))
                s.append(Join([Combined([Constant(int(self.pumptime), self.drive_amp, chan=self.drive_info.sideband_channels[0]),
                                         Constant(int(self.pumptime), 1, chan=self.fwm_switch),
                                         ])
                            ]))
                if decayt > 0:
                    s.append(Constant(int(decayt), 1, chan=self.fwm_switch))
                s.append(Delay(self.measdelay))
                s.append(r(np.pi, X_AXIS))
        
                if self.postseq:
                    s.append(self.postseq)
                s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
                s.append(Delay(2000))
                
        if self.bgcor:
            for decayt in self.decaytimes:
                s.append(Join([self.seq,
                              Constant(250, 1, chan=self.fwm_switch),
                              ]))
                s.append(Join([Combined([Constant(int(self.pumptime), self.drive_amp, chan=self.drive_info.sideband_channels[0]),
                                         Constant(int(self.pumptime), 1, chan=self.fwm_switch),
                                         ])
                            ]))
                if decayt > 0:
                    s.append(Constant(int(decayt), 1, chan=self.fwm_switch))
                s.append(Delay(self.measdelay))        
                
                if self.postseq:
                    s.append(self.postseq)
                s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
                s.append(Delay(2000))
                
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def analyze(self, data=None, fig=None):
        analysis(self, data, fig)
        return None

