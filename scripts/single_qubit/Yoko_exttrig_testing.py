# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 15:02:11 2018

@author: WangLab2
"""

import matplotlib.pyplot as plt
import numpy as np
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import h5py
import lmfit

def analysis(meas, data=None, fig=None, ofs=None, amplitude=None, f_ofs=None, f_amp=None):
    return T1, FT1
    
    
class Yoko_test(Measurement1D):

    def __init__(self, qubit_info, ef_info, qubit2_info, T1delay, FT1delay, seq=None, postseq=None, ofs=None, amplitude=None, f_ofs=None,
                 f_amp=None, **kwargs):
        self.qubit_info = qubit_info
        self.ef_info = ef_info
        self.qubit2_info = qubit2_info
        self.T1delay = T1delay
        self.FT1delay = FT1delay
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.ofs = ofs
        self.amplitude = amplitude
        self.f_ofs = f_ofs
        self.f_amp = f_amp


        super(Yoko_test, self).__init__(5, infos=(qubit_info, ef_info, qubit2_info), **kwargs)
        self.T1data = self.data.create_dataset('T1delay', data=T1delay)
        self.FT1data = self.data.create_dataset('FT1delay', data=FT1delay)
        
        
    def generate(self):
        '''Optional pre-sequence'''
        s = Sequence() 
        r_ge = self.qubit_info.rotate
        r_ef = self.ef_info.rotate
        r_ge2 = self.qubit2_info.rotate
        _w = self.qubit_info.w
#        

        '''This toggles Yoko output'''
        s.append(self.seq)
        s.append(Constant(int(4e7), 1, chan=5))
        

        
        '''This toggles Yoko output'''
        s.append(self.seq)
        s.append(Combined([
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
        ]))

        
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def analyze(self, data=None, fig=None):
#        self.result_params = analysis(self, data, fig, ofs=self.ofs, amplitude=self.amplitude, f_ofs=self.f_ofs, f_amp=self.f_amp)
        return #self.result_params['tau'].value