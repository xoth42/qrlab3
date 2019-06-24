# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 16:02:33 2019

@author: Wang_Lab
"""

import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
#import lmfit


class Contrast_Normalization(Measurement1D):

    def __init__(self, qubit_info, seq=None, process_seq=None, **kwargs):
        self.qubit_info = qubit_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.process_seq=process_seq

        super(Contrast_Normalization, self).__init__(10, infos=(qubit_info,), **kwargs)
        self.data.create_dataset('sequence', data=[0,1,2,3,4,5,6,7,8,9])
#        self.data.set_attrs()


    def generate(self):
        s = Sequence()

        r = self.qubit_info.rotate
#Ebru: I messed wih those initial rotations
#        init_states = [Delay(80), Delay(80), Delay(80),Delay(80), Delay(80), r(np.pi, X_AXIS), r(np.pi, X_AXIS), r(np.pi, X_AXIS), r(np.pi, X_AXIS),  r(np.pi, X_AXIS) ]
        init_states = [r(np.pi, X_AXIS), r(np.pi, X_AXIS), r(np.pi, X_AXIS), r(np.pi, X_AXIS),  r(np.pi, X_AXIS),r(np.pi, X_AXIS), r(np.pi, X_AXIS), r(np.pi, X_AXIS), r(np.pi, X_AXIS),  r(np.pi, X_AXIS) ]

        for init_state in init_states:
            s.append(self.seq)
            s.append(init_state) #prepare x or y or z
            s.append(self.process_seq)
            '''measure sigma z'''

            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
            s.append(Delay(2000))
#            s.append(Delay(2000))    #Buna gerek yok sanirim cunku rep rate zaten fazlasiyla yeterli olmali tekrar ground state'e inmesi icin.
#            s.append(self.seq)
#            s.append(init_state) #prepare x or y or z
#            s.append(self.process_seq)
#            '''measure sigma y after the process to be characterized'''
#            s.append(r(np.pi/2, X_AXIS))
#            s.append(Combined([
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#                ]))
#            s.append(Delay(2000))
#            s.append(self.seq)
#            s.append(init_state) #prepare x or y or z
#            s.append(self.process_seq)
#            '''measure sigma z after the process to be characterized'''
#            s.append(Combined([
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#                ]))
#        s.append(Delay(2000))
        s = self.get_sequencer(s)
        seqs = s.render()

        return seqs

    def analyze(self, data=None, fig=None):
#        self.fit_params = analysis(self, data, fig)
        return #self.fit_params['tau'].value
