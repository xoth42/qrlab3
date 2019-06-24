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


def rdm_rotations(n_gates):
    k=[]
    l=[]
    for i in range(n_gates):
        a=random.randint(1,4)
        if a==1:
            k.append('A1')
        elif a==2:
            k.append('A2')
        elif a==3:
            k.append('A3')
        elif a==4:
            k.append('A4')
        b=random.randint(1,7)
        if b==1:
            l.append('B1')
        elif b==2:
            l.append('B2')
        elif b==3:
            l.append('B3')
        elif b==4:
            l.append('B4')
        elif b==5:
            l.append('B5')
        elif b==6:
            l.append('B6')
        elif b==7:
            l.append('B7')
    
    m=[]

    for i in range(n_gates):
        if k[i]=='A1':
            m.append('A1')
        if k[i]=='A2':
            m.append('A2')
        if k[i]=='A3':
            m.append('A3')
        if k[i]=='A4':
            m.append('A4')
        if l[i]=='B1':
            m.append('B1')
        if l[i]=='B2':
            m.append('B2')
        if l[i] =='B3':
            m.append('B3')
        if l[i]=='B4':
            m.append('B4')
        if l[i]=='B5':
            m.append('B5')
        if l[i]=='B6':
            m.append('B6')
        if l[i]=='B7':
            m.append('B7')
#    print(m)   
    return m
    
    

def correct_rdm_rot(rot_list):
    #This one is for Z gate with delay
#    d=np.matrix([[1,5,2,0,4,3],[3,0,2,5,4,1],[2,1,5,3,0,4],[4,1,0,3,5,2],[5,3,2,1,4,0],[5,3,2,1,4,0],[5,1,4,3,2,0],[5,1,4,3,2,0],[0,1,2,3,4,5],[0,1,2,3,4,5],[0,1,2,3,4,5]])
    #This one is for composite pulse Z gate
    d=np.matrix([[1,5,2,0,4,3],[3,0,2,5,4,1],[2,1,5,3,0,4],[4,1,0,3,5,2],[5,3,2,1,4,0],[5,3,2,1,4,0],[5,1,4,3,2,0],[5,1,4,3,2,0],[0,3,4,1,2,5],[0,3,4,1,2,5],[0,1,2,3,4,5]])
   
    a=[0]

    def rotate(m,a):
        if m[i]=='A1':
            a.append(d[0,a[i]])
        if m[i]=='A2':
            a.append(d[2,a[i]])
        if m[i]=='A3':
            a.append(d[1,a[i]])
        if m[i]=='A4':
            a.append(d[3,a[i]])
        if m[i]=='B1':
            a.append(d[4,a[i]])
        if m[i]=='B2':
            a.append(d[6,a[i]])
        if m[i]=='B3':
            a.append(d[8,a[i]])
        if m[i]=='B4':
            a.append(d[10,a[i]])
        if m[i]=='B5':
            a.append(d[5,a[i]])
        if m[i]=='B6':
            a.append(d[7,a[i]])
        if m[i]=='B7':
            a.append(d[9,a[i]])
        return a
    
    p= len(rot_list)
    
    for i in range(p):
        rotate(rot_list,a)
        
    cor_list=[]
    
    for i in range(1,((p/2)+1)):  #It counts the number of gates, from 1 to p/2
        final=a[2*i]
        if final==0:
            cor_list.append('B4')
        if final==1:
            cor_list.append('A3')
        if final==2:
            cor_list.append('A4')
        if final==3:
            cor_list.append('A1')
        if final==4:
            cor_list.append('A2')
        if final==5:
            cor_list.append('B2')
    return cor_list



class rndm(Measurement1D):

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
        super(rndm, self).__init__(n_points, infos=(qubit_info,), **kwargs)
        self.data.create_dataset('number_of_gates', data=np.linspace(1, n_points, n_points))
#        self.data.set_attrs()


    def generate(self):
        s = Sequence()
        r = self.qubit_info.rotate
        
        rotation_list = rdm_rotations(self.stop)
        correction_list = correct_rdm_rot(rotation_list)
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
            temp_seq = Sequence()
            temp_seq.append(r(np.pi, X_AXIS))   
            temp_seq.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            temp_seq.append(Delay(1000))
            s.append(Join(temp_seq))
        print('appended calibration pi pulses')
        
#        s.append(Delay(100000))
        
        for j in range(self.num_cal_points):
            s.append(self.seq)
            temp_seq = Sequence()
            s.append(Delay(80))   
            temp_seq.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            temp_seq.append(Delay(1000))
            s.append(Join(temp_seq))
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
            s.append(self.seq)
            
            temp_seq = Sequence()            
            for i in range(2*n):
                if rotation_list[i] in ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B4', 'B5', 'B6']:
                    temp_seq.append(self.seq_table(rotation_list[i]))
#                    s.append(Delay(5))
                if rotation_list[i] in ['B3', 'B7']:
                    temp_seq.append(r(np.pi, X_AXIS))
                    temp_seq.append(r(np.pi, Y_AXIS))
#                    s.append(Delay(5))
                if i%100==99:
                    s.append(Join(temp_seq))
                    temp_seq = Sequence()
     
            temp_seq.append(self.seq_table(correction_list[n-1]))
#            temp_seq.append(Delay(5))
#            if self.postseq is not None:
#                s.append(self.postseq)
            temp_seq.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            temp_seq.append(Delay(1000))
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