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

        super(Pi_Amp_Cal, self).__init__(64, infos=(qubit_info,), **kwargs)
        self.data.create_dataset('sequence', data=[range(0,64)])
#        self.data.set_attrs()


    def generate(self):
        s = Sequence()


        r = self.qubit_info.rotate
        wait = Delay(5)



        for m in [31,29,27,25,23,21,19,17,15,13,11,9,7,5,3,1]:
            s.append(self.seq)
            s.append(r(-np.pi/2, X_AXIS))
            for i in range(m):
                s.append(r(-np.pi, X_AXIS))
                if wait is not None: s.append(wait)
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(2000)) 
            s.append(self.seq)
            s.append(r(-np.pi/2, X_AXIS))
            for i in range(m):
#                s.append(r(-np.pi/2, X_AXIS))
                s.append(r(-np.pi, X_AXIS))
                if wait is not None: s.append(wait)
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(2000)) 










#
#
#
#
#
#
#
#
#
#        s.append(self.seq)
#        for i in range(11):
#            s.append(r(-np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000)) 
#        s.append(self.seq)
#        for i in range(11):
#            s.append(r(-np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000)) 
#
#
#
#
#        s.append(self.seq)
#        for i in range(9):
#            s.append(r(-np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000)) 
#        s.append(self.seq)
#        for i in range(9):
#            s.append(r(-np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000)) 
#
#
#
#
#
#
#
#
#
#
#
#
#
#        s.append(self.seq)
#        for i in range(7):
#            s.append(r(-np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000)) 
#        s.append(self.seq)
#        for i in range(7):
#            s.append(r(-np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000)) 
#
#
#
#
#
#        ''' 201 x X(pi) rotations'''
#        
#        
#        s.append(self.seq)
#        for i in range(5):
#            s.append(r(-np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000)) 
#        s.append(self.seq)
#        for i in range(5):
#            s.append(r(-np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000))
#
#
#
#
#
#
#
#        s.append(self.seq)
#        for i in range(3):
#            s.append(r(-np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000))        
#        s.append(self.seq)
#        for i in range(3):
#            s.append(r(-np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000))  
#
#
#        '''One X(pi) rotation'''
#        
#        
#        s.append(self.seq)
#        s.append(r(-np.pi, X_AXIS))
#        if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000)) 
#        s.append(self.seq)
#        s.append(r(-np.pi, X_AXIS))
#        if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000)) 
#                
 



        for m in [1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31]:
            s.append(self.seq)
            s.append(r(np.pi/2, X_AXIS))
            for i in range(m):
                s.append(r(np.pi, X_AXIS))
                if wait is not None: s.append(wait)
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(2000)) 
            s.append(self.seq)
            s.append(r(np.pi/2, X_AXIS))
            for i in range(m):
#                s.append(r(np.pi/2, X_AXIS))
                s.append(r(np.pi, X_AXIS))
                if wait is not None: s.append(wait)
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(2000))



#       '''One X(pi) rotation'''
#        
#        
#        s.append(self.seq)
#        s.append(r(np.pi, X_AXIS))
#        if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000)) 
#        s.append(self.seq)
#        s.append(r(np.pi, X_AXIS))
#        if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000))         
#        ''' 101 x X(pi) rotations'''
#        
#        
#        s.append(self.seq)
#        for i in range(3):
#            s.append(r(np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000))        
#        
#        s.append(self.seq)
#        for i in range(3):
#            s.append(r(np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000))          
#
#        ''' 201 x X(pi) rotations'''
#        
#        
#        s.append(self.seq)
#        for i in range(5):
#            s.append(r(np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000)) 
#        s.append(self.seq)
#        for i in range(5):
#            s.append(r(np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000))         
#        
#        ''' 401 x X(pi) rotations'''
#        
#        
#        s.append(self.seq)
#        for i in range(7):
#            s.append(r(np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000)) 
#        s.append(self.seq)
#        for i in range(7):
#            s.append(r(np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000))         
#        s = self.get_sequencer(s)
#        seqs = s.render()
#
#        return seqs
#
#        ''' 401 x X(pi) rotations'''
#        
#        
#        s.append(self.seq)
#        for i in range(9):
#            s.append(r(np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000)) 
#        s.append(self.seq)
#        for i in range(9):
#            s.append(r(np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000))         
#
#
#        ''' 401 x X(pi) rotations'''
#        
#        
#        s.append(self.seq)
#        for i in range(11):
#            s.append(r(np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000)) 
#        s.append(self.seq)
#        for i in range(11):
#            s.append(r(np.pi, X_AXIS))
#            if wait is not None: s.append(wait)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000))   
        
        
        
        s = self.get_sequencer(s)
        seqs = s.render()

        return seqs

    def analyze(self, data=None, fig=None):
#        self.fit_params = analysis(self, data, fig)
        return #self.fit_params['tau'].value
