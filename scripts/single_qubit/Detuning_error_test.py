# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 15:15:46 2019

@author: Wang_Lab
"""

import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
#import lmfit


class Detuning_error_test(Measurement1D):

    def __init__(self, qubit_info, seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq

        super(Detuning_error_test, self).__init__(12, infos=(qubit_info,), **kwargs)
        self.data.create_dataset('sequence', data=[list(range(0,12))])
#        self.data.set_attrs()


    def generate(self):
        s = Sequence()


        r = self.qubit_info.rotate
        wait = Delay(5)


   
        '''Equator sequences'''

        s.append(self.seq)
        s.append(r(np.pi/2, X_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi/2, Y_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(1000))    
        s.append(self.seq)
        s.append(r(np.pi/2, X_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi/2, Y_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(1000))     
        
        
        s.append(self.seq)
        s.append(r(np.pi/2, X_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi, X_AXIS))
        if wait is not None: s.append(wait)        
        s.append(r(np.pi/2, Y_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi, Y_AXIS))
        if wait is not None: s.append(wait)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))  
        s.append(self.seq)
        s.append(r(np.pi/2, X_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi, X_AXIS))
        if wait is not None: s.append(wait)        
        s.append(r(np.pi/2, Y_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi, Y_AXIS))
        if wait is not None: s.append(wait)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))


        
        s.append(self.seq)
        s.append(r(np.pi/2, Y_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi/2, X_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))   
        s.append(self.seq)
        s.append(r(np.pi/2, Y_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi/2, X_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 



        
        s.append(self.seq)
        s.append(r(np.pi/2, Y_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi, Y_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi/2, X_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi, X_AXIS))
        if wait is not None: s.append(wait)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))                
        s.append(self.seq)
        s.append(r(np.pi/2, Y_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi, Y_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi/2, X_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi, X_AXIS))
        if wait is not None: s.append(wait)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))       
        '''South pole'''
        
        s.append(Delay(2000))    
        s.append(self.seq)
        s.append(r(np.pi/2, X_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi/2, X_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))    
        s.append(self.seq)
        s.append(r(np.pi/2, X_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi/2, X_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))    



        s.append(Delay(2000)) 
        
        
        s.append(self.seq)
        s.append(r(np.pi/2, Y_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi/2, Y_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))        
        s.append(self.seq)
        s.append(r(np.pi/2, Y_AXIS))
        if wait is not None: s.append(wait)
        s.append(r(np.pi/2, Y_AXIS))
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
