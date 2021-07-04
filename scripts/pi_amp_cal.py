# -*- coding: utf-8 -*-
"""
Created on Thu May  2 21:54:30 2019

@author: Wang_Lab
"""

#Pi and pi/2 amp calibration 

import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
#import lmfit


class Pi_Amp_Cal(Measurement1D):

    def __init__(self, qubit_info, seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq

        super(Pi_Amp_Cal, self).__init__(4, infos=(qubit_info,), **kwargs)
        self.data.create_dataset('sequence', data=[list(range(0,4))])
#        self.data.set_attrs()


    def generate(self):
        s = Sequence()


        r = self.qubit_info.rotate
        wait = Delay(5)

        '''One X(pi) rotation'''
        
        
        s.append(self.seq)
        s.append(r(np.pi, X_AXIS))
        if wait is not None: s.append(wait)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        ''' 11 x X(pi) rotations'''
        
        
        s.append(self.seq)
        for i in range(101):
            s.append(r(np.pi, X_AXIS))
            if wait is not None: s.append(wait)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))        
        

        ''' 51 x X(pi) rotations'''
        
        
        s.append(self.seq)
        for i in range(201):
            s.append(r(np.pi, X_AXIS))
            if wait is not None: s.append(wait)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        ''' 101 x X(pi) rotations'''
        
        
        s.append(self.seq)
        for i in range(101):
            s.append(r(np.pi, X_AXIS))
            if wait is not None: s.append(wait)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        s = self.get_sequencer(s)
        seqs = s.render()

        return seqs


    def analyze(self, data=None, fig=None):
#        self.fit_params = analysis(self, data, fig)
        return #self.fit_params['tau'].value
