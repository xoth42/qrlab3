# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 18:19:08 2019

@author: Wang_Lab
"""

import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import math
import random 
import time
#import lmfit

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.xs


#def seq_table(symbol):
#    if symbol == 'A1':
#        return r(np.pi/2, X_AXIS)
#    elif symbol == 'A2':
#        return r(np.pi/2, Y_AXIS)
#    elif symbol == 'A3':
#        return r(-np.pi/2, X_AXIS)
#    elif symbol == 'A4':
#        return r(-np.pi/2, Y_AXIS)
#    elif symbol == 'B1':
#        return r(np.pi, X_AXIS)
#    elif symbol == 'B2':
#        return r(np.pi, Y_AXIS)
#    elif symbol == 'B3':            #Z(PI)
#        return Delay(40)
#    elif symbol == 'B4':            #Identity
#        return Delay(40)
#    elif symbol == 'B5':
#        return r(-np.pi, X_AXIS)
#    elif symbol == 'B6':
#        return r(-np.pi, Y_AXIS)
#    elif symbol == 'B7':
#        return Delay(40)            #Z(-PI)



    

class rndm_diagnostics(Measurement1D):

    def __init__(self, qubit_info, num_cal_points, n_gates_start, n_gates_stop, n_gates_step, seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        
        self.num_cal_points = num_cal_points
        
        if seq is None:
            seq = Trigger(250)
        self.xs = np.append(np.array(range(1,2*num_cal_points+1,1)),np.array(range(n_gates_start + 2*num_cal_points, n_gates_stop+2*num_cal_points +1, n_gates_step)))                                  
        self.start = n_gates_start
        self.stop = n_gates_stop
        self.step = n_gates_step
        n_gates = (n_gates_stop-n_gates_start)/n_gates_step+1
        self.seq = seq
        self.postseq = postseq
        n_points = n_gates + 2*num_cal_points
        super(rndm_diagnostics, self).__init__(n_points, infos=(qubit_info,), **kwargs)
        self.data.create_dataset('number_of_gates', data=np.linspace(1, n_points, n_points))
#        self.data.set_attrs()


    def generate(self):
        s = Sequence()
        r = self.qubit_info.rotate
        
        rotation_list = ['A3', 'B5', 'A1', 'B5', 'A3', 'B7', 'A3', 'B3', 'A4', 'B2', 'A3', 'B4', 'A2', 'B5', 'A1', 'B1', 'A2', 'B7', 'A4', 'B5', 'A2', 'B2', 'A2', 'B2', 'A3', 'B2', 'A1', 'B1', 'A1', 'B2', 'A3', 'B5', 'A4', 'B3', 'A4', 'B1', 'A4', 'B6', 'A1', 'B4', 'A4', 'B6', 'A4', 'B1', 'A3', 'B4', 'A3', 'B3', 'A4', 'B7', 'A4', 'B3', 'A1', 'B7', 'A2', 'B6', 'A1', 'B1', 'A2', 'B5', 'A2', 'B4', 'A3', 'B6', 'A4', 'B5', 'A4', 'B4', 'A2', 'B3', 'A3', 'B5', 'A3', 'B5', 'A1', 'B1', 'A2', 'B4', 'A2', 'B4', 'A1', 'B4', 'A1', 'B3', 'A2', 'B6', 'A1', 'B2', 'A3', 'B4', 'A3', 'B4', 'A3', 'B3', 'A3', 'B2', 'A2', 'B7', 'A4', 'B2', 'A3', 'B4', 'A1', 'B2', 'A4', 'B7', 'A4', 'B6', 'A3', 'B2', 'A4', 'B3', 'A3', 'B7', 'A4', 'B6', 'A3', 'B4', 'A3', 'B1', 'A2', 'B3', 'A4', 'B2', 'A1', 'B2', 'A1', 'B2', 'A3', 'B7', 'A3', 'B1', 'A2', 'B2', 'A4', 'B7', 'A3', 'B5', 'A4', 'B4', 'A4', 'B6', 'A2', 'B5', 'A3', 'B5', 'A1', 'B1', 'A4', 'B3', 'A1', 'B2', 'A4', 'B3', 'A2', 'B2', 'A4', 'B5', 'A4', 'B4', 'A2', 'B1', 'A4', 'B3', 'A2', 'B1', 'A3', 'B4', 'A3', 'B7', 'A1', 'B5', 'A3', 'B3', 'A1', 'B1', 'A4', 'B1', 'A4', 'B1', 'A1', 'B3', 'A3', 'B3', 'A3', 'B5', 'A2', 'B1', 'A3', 'B5', 'A3', 'B7', 'A4', 'B2', 'A4', 'B3', 'A4', 'B6', 'A3', 'B6', 'A4', 'B4', 'A3', 'B5', 'A2', 'B3', 'A2', 'B6', 'A2', 'B5', 'A4', 'B7', 'A2', 'B6', 'A2', 'B7', 'A2', 'B6', 'A4', 'B1', 'A4', 'B1', 'A4', 'B2', 'A1', 'B2', 'A1', 'B6', 'A4', 'B5', 'A3', 'B6', 'A3', 'B1', 'A2', 'B3', 'A2', 'B3', 'A2', 'B4', 'A4', 'B7', 'A2', 'B5', 'A3', 'B1', 'A2', 'B7', 'A2', 'B5', 'A4', 'B3', 'A4', 'B6', 'A2', 'B1', 'A1', 'B5', 'A2', 'B3', 'A2', 'B6', 'A1', 'B4', 'A4', 'B5', 'A1', 'B5', 'A2', 'B2', 'A4', 'B7', 'A3', 'B6', 'A2', 'B2', 'A3', 'B7', 'A4', 'B7', 'A3', 'B5', 'A1', 'B6', 'A4', 'B7', 'A2', 'B7', 'A4', 'B6', 'A4', 'B5', 'A1', 'B5', 'A1', 'B6', 'A3', 'B5', 'A3', 'B5', 'A4', 'B3', 'A4', 'B6', 'A3', 'B1', 'A3', 'B1', 'A4', 'B3', 'A4', 'B2', 'A2', 'B7', 'A3', 'B3', 'A1', 'B2', 'A2', 'B2', 'A4', 'B5', 'A2', 'B1', 'A3', 'B3', 'A1', 'B7', 'A4', 'B6', 'A2', 'B1', 'A2', 'B1', 'A4', 'B3', 'A2', 'B1', 'A3', 'B6', 'A2', 'B2', 'A4', 'B3', 'A2', 'B3', 'A3', 'B1', 'A3', 'B6', 'A3', 'B2', 'A2', 'B4', 'A3', 'B4', 'A4', 'B4', 'A1', 'B2', 'A1', 'B1', 'A4', 'B4', 'A1', 'B4', 'A2', 'B5', 'A1', 'B4', 'A2', 'B3', 'A2', 'B6', 'A3', 'B2', 'A3', 'B4', 'A2', 'B5', 'A3', 'B7', 'A4', 'B1', 'A3', 'B4', 'A1', 'B6', 'A2', 'B2', 'A1', 'B4', 'A1', 'B4', 'A2', 'B5', 'A2', 'B5', 'A2', 'B4', 'A2', 'B5', 'A4', 'B3', 'A2', 'B6', 'A3', 'B5', 'A4', 'B5', 'A1', 'B5', 'A1', 'B1', 'A1', 'B5', 'A4', 'B6', 'A4', 'B4', 'A4', 'B5']
        correction_list = ['A3', 'B4', 'A3', 'B4', 'A4', 'A4', 'B4', 'A1', 'A3', 'A1', 'A1', 'A1', 'B4', 'A1', 'B2', 'A1', 'A3', 'A1', 'A1', 'B4', 'A4', 'B2', 'A3', 'B4', 'A4', 'B4', 'A1', 'A1', 'B2', 'A2', 'B4', 'A1', 'A3', 'A3', 'A1', 'B4', 'A3', 'B4', 'A4', 'B2', 'A1', 'B4', 'A2', 'A4', 'A4', 'A4', 'A2', 'A4', 'B2', 'A2', 'A2', 'A4', 'B4', 'A4', 'A2', 'B2', 'A1', 'A1', 'B2', 'A1', 'A3', 'A3', 'B4', 'A3', 'B4', 'A3', 'A3', 'A1', 'B4', 'A2', 'B4', 'A4', 'A4', 'A4', 'B4', 'A3', 'A1', 'A1', 'A3', 'A3', 'A1', 'A3', 'A1', 'B2', 'A1', 'B2', 'A1', 'B2', 'A4', 'B2', 'A3', 'B4', 'A3', 'A1', 'B4', 'A3', 'A3', 'A1', 'A1', 'B4', 'A2', 'A2', 'B4', 'A2', 'B2', 'A2', 'B2', 'A4', 'B4', 'A2', 'B4', 'A4', 'A2', 'A4', 'B2', 'A3', 'B2', 'A4', 'B2', 'A2', 'B2', 'A2', 'A2', 'B4', 'A4', 'B4', 'A4', 'B4', 'A1', 'A3', 'A3', 'B2', 'A4', 'A4', 'B4', 'A4', 'A2', 'B2', 'A1', 'A3', 'B2', 'A1', 'A3', 'A1', 'A1', 'A3', 'B4', 'A3', 'B2', 'A1', 'A3', 'A3', 'B2', 'A1', 'A3', 'A3', 'A1', 'B2', 'A1', 'A1', 'A3', 'A1', 'B2', 'A3', 'A3', 'A1', 'A3', 'A1', 'A3', 'B2', 'A4', 'B4', 'A2', 'A2', 'A4', 'A2', 'B4', 'A1', 'A1', 'B2', 'A3', 'A3', 'B2', 'A2', 'A2', 'B4', 'A2', 'A4', 'A4', 'B4', 'A3', 'A1', 'B2', 'A1', 'A1', 'B4', 'A3', 'A1', 'A3', 'A3', 'A1', 'A3', 'A3', 'B2', 'A4', 'A4', 'A4', 'A4', 'B2', 'A4', 'B2']
        print rotation_list
        print correction_list
         
#        for j in range(self.num_cal_points):
#            s.append(self.seq)
#            s.append(Delay(80))   
#            s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#                ]))
#            s.append(Delay(2000))        
                    
        for j in range(self.num_cal_points):
            s.append(self.seq)
            s.append(r(np.pi, X_AXIS))   
            s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(2000))
        print('appended calibration pi pulses')
        
#        s.append(Delay(100000))
        
        for j in range(self.num_cal_points):
            s.append(self.seq)
            s.append(Delay(80))   
            s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(2000))
        print('appended calibration ground state')

#This for loop is for Z pi gate that is composed of delay only:
            
#            
#        for n in range(self.start, self.stop+1, self.step):
#            s.append(self.seq)
#            
#            for i in range(2*n):
#                s.append(self.seq_table(rotation_list[i]))
#                s.append(Delay(5))
#                
#            s.append(self.seq_table(correction_list[n-1]))
#            s.append(Delay(5))
##            if self.postseq is not None:
##                s.append(self.postseq)
#            s.append(Combined([
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#                ]))
#            s.append(Delay(2000))
#            
#        s = self.get_sequencer(s)
#        seqs = s.render()
#
#        return seqs

#This is the for loop to be used for the compound pulse for Z pi and Z -pi:
#What it does is that it plays 'B1' (X, pi) and 'B2' (Y, pi) consecutively rather than a delay.
        
                    
        for n in range(self.start, self.stop+1, self.step):
            temp_seq = Sequence()
            temp_seq.append(self.seq)
            
            for i in range(2*n):
                if rotation_list[i] in ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B4', 'B5', 'B6']:
                    temp_seq.append(self.seq_table(rotation_list[i]))
#                    s.append(Delay(5))
                if rotation_list[i] in ['B3', 'B7']:
                    temp_seq.append(r(np.pi, X_AXIS))
                    temp_seq.append(r(np.pi, Y_AXIS))
#                    s.append(Delay(5))
     
            temp_seq.append(self.seq_table(correction_list[n-1]))
#            temp_seq.append(Delay(5))
#            if self.postseq is not None:
#                s.append(self.postseq)
            temp_seq.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            temp_seq.append(Delay(2000))
            s.append(Join(temp_seq))
            
        s = self.get_sequencer(s)
        time_before_render = time.time()
        print('before render', time_before_render)
        seqs = s.render()
        print('after render', time.time() - time_before_render)

        return seqs






    def seq_table(self, symbol):
        r = self.qubit_info.rotate
        if symbol == 'A1':
            return r(np.pi/2, X_AXIS)
        elif symbol == 'A2':
            return r(np.pi/2, Y_AXIS)
        elif symbol == 'A3':
            return r(-np.pi/2, X_AXIS)
        elif symbol == 'A4':
            return r(-np.pi/2, Y_AXIS)
        elif symbol == 'B1':
            return r(np.pi, X_AXIS)  
        elif symbol == 'B2':
            return r(np.pi, Y_AXIS)
        elif symbol == 'B3':            #Z(PI)
            return Delay(40)
#        elif symbol == 'B3':            #Z(PI)
#            return Delay(40)
        elif symbol == 'B4':            #Identity
            return Delay(20)
        elif symbol == 'B5':
            return r(-np.pi, X_AXIS)
        elif symbol == 'B6':
            return r(-np.pi, Y_AXIS)
        elif symbol == 'B7':
            return Delay(40)            #Z(-PI)

    def analyze(self, data=None, fig=None):
#        self.fit_params = analysis(self, data, fig)
        return #self.fit_params['tau'].value