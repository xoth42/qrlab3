"""
time domain of multiple tones read out on mulitple qubit frequencies


Jeff Gertler
"""


import numpy as np
from math import factorial
import matplotlib.pyplot as plt
#from lib.math import fit
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
    xs = meas.delays
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


class poly_time_domain(Measurement1D):

    def __init__(self, drive_infos, drive_amps, qubit_list, delays, 
                 seq=None, postseq=None, bgcor=False, **kwargs):
        self.drive_infos = drive_infos
        self.qubit_list = qubit_list
        self.delays = delays
        self.drive_amps = drive_amps
        self.bgcor = bgcor
        if seq is None:
            seq = Trigger(500)
        self.seq = seq
        self.postseq = postseq
    
        if bgcor:
            n_rep = len(qubit_list)+1
        else:
            n_rep = len(qubit_list)
        xs_single = self.delays/1e3
        self.xs = np.tile(xs_single, n_rep)
        npoints = len(self.delays) * n_rep
        
        super(poly_time_domain, self).__init__(npoints, infos=drive_infos + qubit_list, **kwargs)
        
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(delays)])
        self.data.create_dataset('delays', data=self.delays)
        self.data.set_attrs(
            drive_amps = drive_amps,
        )

    def generate(self):
        s = Sequence()
        
        for info in self.qubit_list:
            r = info.rotate_selective
            
            for dt in self.delays:
                s.append(self.seq)
                if dt > 0:
                    poly_seq = []
                    for i, drive_info in enumerate(self.drive_infos):
                        poly_seq += [Constant(int(dt), self.drive_amps[i], chan=drive_info.sideband_channels[0])]
                        
                    s.append(Combined(poly_seq))
                s.append(Delay(1e3))
                s.append(r(np.pi, X_AXIS))
        
                if self.postseq:
                    s.append(self.postseq)
                s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
                s.append(Delay(2000))
                
        if self.bgcor:
            for dt in self.delays:
                s.append(self.seq)
                if dt > 0:
                    poly_seq = []
                    for i, drive_info in enumerate(self.drive_infos):
                        poly_seq += [Constant(int(dt), self.drive_amps[i], chan=drive_info.sideband_channels[0])]
                        
                s.append(Combined(poly_seq))
                s.append(Delay(1e3))
                
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

