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
    xs = np.zeros(len(meas.xs)/4)
    for i in range(len(meas.xs)/4):
        xs[i] = meas.xs[4*i]
    
    y2d = ys.reshape(len(ys)/4,4)
    y1s = y2d[:,0]
    y2s = y2d[:,1]
    y3s = y2d[:,2]
    y4s = y2d[:,3]

    fig.axes[0].clear()   
    fig.axes[0].plot(xs, y1s, 'bs', ms=3, color='r', linestyle = '-', label='none')
    fig.axes[0].plot(xs, y2s, 'rs', ms=3, color = 'b', linestyle = '-', label= 'pi pulse on 1')    
    fig.axes[0].plot(xs, y3s, 'bs', ms=3, color= 'g', linestyle = '-', label = 'pi pulse on 2')
    fig.axes[0].plot(xs, y4s, 'rs', ms=3, color='y', linestyle = '-', label = 'pi pulse on both')    

    fig.axes[0].legend()
    fig.canvas.draw()

    ys = meas.avg_data   # We now pull complex data to process populations at this point  
    y2d = ys.reshape(len(ys)/4,4)
    y1s = y2d[:,0]
    y2s = y2d[:,1]
    y3s = y2d[:,2]
    y4s = y2d[:,3]    

    #3 is the number of calibration point here
    calibration_qubit1_excited = (y1s[:3] + y2s[:3] + y3s[:3] + y4s[:3])/4
    calibration_qubit2_excited = (y1s[3:6] + y2s[3:6] + y3s[3:6] + y4s[3:6])/4
    calibration_bothqubits_excited = (y1s[6:9] + y2s[6:9] + y3s[6:9] + y4s[6:9])/4
    calibration_ground = (y1s[9:12] + y2s[9:12] + y3s[9:12] + y4s[9:12])/4
    Veg = np.mean(calibration_qubit1_excited)
    Vge = np.mean(calibration_qubit2_excited)
    Vee = np.mean(calibration_bothqubits_excited)
    Vgg = np.mean(calibration_ground)
    print(Veg, Vge, Vee, Vgg)
#    
#    q1_epop_cplx = ((y1s[13:] + y3s[13:]) - (Vge + Vgg))/ (Veg-Vgg+Vee-Vge)
#    
#    fig2, axes2 = plt.subplots(2)
#    axes2[0].plot(xs[13:], np.real(q1_epop_cplx))
#    axes2[1].plot(xs[13:], np.imag(q1_epop_cplx))
##
#    return q1_epop_cplx
#
#
# ge~ -10, eg~ +8, ee~ +6
#
##

    rd = y1s[12:]
    bl = y2s[12:]
    gr = y3s[12:]
    yw = y4s[12:]
    Pg1 = ((-rd-gr+bl+yw)/(Veg-Vgg+Vee-Vge)+1)/2
    Pg2 = ((-rd-bl+gr+yw)/(Vge-Vgg+Vee-Veg)+1)/2
    
#    B = ((y1s[12:] + y3s[12:]) - (Vge + Vgg))/ (Veg-Vgg+Vee-Vge)  #QUBIT 1 POPULATION (P2 +P3)
#    D = ((y1s[12:] + y2s[12:]) - (Veg + Vgg))/ (Vge-Veg-Vgg+Vee)   #QUBIT 2 POPULATION (P1 +P3)
#    C = ((y2s[12:] + y3s[12:]) - (Vge + Veg)) / (Vee-Vge-Veg + Vgg)  #(P1 + P2)
#    A = ((y1s[12:] + y4s[12:]) - (Vge + Veg)) / (Vee - Vge - Veg + Vgg)  # (P0 + P3)
#    Pg_cplx = A-((D-C+B)/2)

    Pegge = ((rd+yw-bl-gr)/(Vge+Veg-Vee-Vgg)+1)/2
    Pg_cplx = (Pg1+Pg2-Pegge)/2
    
#Dario commenting out this section to fix a merge conflict, it looks like Chen was changing
#population calculation stuff last night and I believe I have kept the most updated version here 
#but just to be safe
#    B = ((y1s[12:] + y3s[12:]) - (Vge + Vgg))/ (Veg-Vgg+Vee-Vge)  #QUBIT 1 POPULATION (P2 +P3)
##
#    D = ((y1s[12:] + y2s[12:]) - (Veg + Vgg))/ (Vge-Veg-Vgg+Vee)   #QUBIT 2 POPULATION (P1 +P3)
##
#    C = ((y2s[12:] + y3s[12:]) - (Vge + Veg)) / (Vee-Vge-Veg + Vgg)  #(P1 + P2)
##
#    A = ((y1s[12:] + y4s[12:]) - (Vge + Veg)) / (Vee - Vge - Veg + Vgg)  # (P0 + P3)
#    
##
#    Pg_cplx = A-((D-C+B)/2)

    fig2, axes2 = plt.subplots(2)
    axes2[0].plot(xs[12:], np.real(Pg_cplx))
    axes2[0].plot(xs[12:], np.real(Pg1*Pg2), color='r')
    axes2[1].plot(xs[12:], np.imag(Pg_cplx))
    
    return Pg_cplx

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
#    This one is for Z gate with delay
    d=np.matrix([[1,5,2,0,4,3],[3,0,2,5,4,1],[2,1,5,3,0,4],[4,1,0,3,5,2],[5,3,2,1,4,0],[5,3,2,1,4,0],[5,1,4,3,2,0],[5,1,4,3,2,0],[0,1,2,3,4,5],[0,1,2,3,4,5],[0,1,2,3,4,5]])
#    This one is for composite pulse Z gate
#    d=np.matrix([[1,5,2,0,4,3],[3,0,2,5,4,1],[2,1,5,3,0,4],[4,1,0,3,5,2],[5,3,2,1,4,0],[5,3,2,1,4,0],[5,1,4,3,2,0],[5,1,4,3,2,0],[0,3,4,1,2,5],[0,3,4,1,2,5],[0,1,2,3,4,5]])
   
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




class Simultaneous_1QRB(Measurement1D):

    def __init__(self, qubit_info, qubit2_info, num_cal_points, n_gates_start, n_gates_stop, n_gates_step, seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.qubit2_info = qubit2_info
        self.num_cal_points = num_cal_points
        
        if seq is None:
            seq = Trigger(250)
        XS= np.append(np.array(list(range(-4*num_cal_points,0))), np.array(list(range(n_gates_start, n_gates_stop+1, n_gates_step))))                                  
        self.xs = np.array([XS,XS,XS,XS]).transpose().flatten()    # For plotting purposes

        self.start = n_gates_start
        self.stop = n_gates_stop
        self.step = n_gates_step
        n_gates = (n_gates_stop-n_gates_start)/n_gates_step+1
        self.seq = seq
        self.postseq = postseq
        n_points = n_gates + 4*num_cal_points
        super(Simultaneous_1QRB, self).__init__(4*n_points, infos=(qubit_info,qubit2_info), **kwargs)
        self.data.create_dataset('gates', data=np.linspace(1, n_points, n_points))
#        self.data.set_attrs()




    def generate(self):
        s = Sequence()
        r = self.qubit_info.rotate
        r2 = self.qubit2_info.rotate        
        rotation_list = rdm_rotations(self.stop)
        correction_list = correct_rdm_rot(rotation_list)
        print(rotation_list)
        print(correction_list)
        
        rotation2_list = rdm_rotations(self.stop)
        correction2_list = correct_rdm_rot(rotation2_list)
        
        print(rotation2_list)
        print(correction2_list)
         
       
                    
        for j in range(self.num_cal_points):
#            s.append(self.seq)      #Ebru: take this out after making sure that it causes no problem

            temp_seq = Sequence()
            temp_seq.append(self.qubit_info.rotate(np.pi,0))   
            for i in range(4):


                s.append(self.seq)
                s.append(Join(temp_seq))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration pi pulses qubit 1')


        for j in range(self.num_cal_points):
#            s.append(self.seq)

            temp_seq = Sequence()
            temp_seq.append(self.qubit2_info.rotate(np.pi,0))   
            for i in range(4):


                s.append(self.seq)
                s.append(Join(temp_seq))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration pi pulses qubit 2')


        for j in range(self.num_cal_points):
            s.append(self.seq) 

            temp_seq = Sequence()
            temp_seq.append(Combined([self.qubit_info.rotate(np.pi,0),self.qubit2_info.rotate(np.pi,0)]))   
            for i in range(4):


                s.append(self.seq)
                s.append(Join(temp_seq))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration pi pulses for both qubits')

        
        
        for j in range(self.num_cal_points):

            temp_seq = Sequence()
            s.append(Delay(24))   
            for i in range(4):
                s.append(self.seq)
                s.append(Join(temp_seq))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration ground state')



                    
        for n in range(self.start, self.stop+1, self.step):
#            s.append(self.seq)
            temp_seq = Sequence()
            combine_seq = Sequence()  
            combine2_seq = Sequence()
            
#            for i in range(2*n):
#                if rotation_list[i] in ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3' 'B4', 'B5', 'B6', 'B7']:
#                    combine_seq.append(self.seq_table(rotation_list[i]))
#                if rotation2_list[i] in ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7']:
#                    combine2_seq.append(self.seq2_table(rotation2_list[i]))
#                temp_seq.append(Combined([combine_seq, combine2_seq]))
#                combine_seq = Sequence()  
#                combine2_seq = Sequence()
            for i in range(2*n):
                if rotation_list[i] in ['A1', 'A2', 'A3', 'A4', 'B1', 'B2','B3',  'B4', 'B5', 'B6', 'B7']:
                    combine_seq.append(self.seq_table(rotation_list[i]))
                if rotation2_list[i] in ['A1', 'A2', 'A3', 'A4', 'B1', 'B2','B3',  'B4', 'B5', 'B6', 'B7']:
                    combine2_seq.append(self.seq2_table(rotation2_list[i]))


                
                temp_seq.append(Combined([combine_seq[0], combine2_seq[0]]))
#                temp_seq.append(combine_seq)
#                temp_seq.append(combine2_seq)
                combine_seq = Sequence()  
                combine2_seq = Sequence()

                    

            temp_seq.append(Combined([self.seq_table(correction_list[n-1]),self.seq2_table(correction2_list[n-1])]))
            for ROpostseq in [None, self.qubit_info.rotate(np.pi,0), self.qubit2_info.rotate(np.pi,0),
                              Combined([self.qubit_info.rotate(np.pi,0),self.qubit2_info.rotate(np.pi,0)])]:
               
                
                s.append(self.seq)            
                s.append(Join(temp_seq))
                if ROpostseq is not None:
                    s.append(ROpostseq)
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))


#Ebru: I switched back to the Z = identity for the moment, to make sure combining different pulse lengths don't cause any trouble.
# In the other case, since virtual Z is longer than the rest of the pulses, I will need to add delay to the pulse on the other qubit. 
#I am not sure which case is more realistic in terms of its effect to the fidelity


        s = self.get_sequencer(s)
        time_before_render = time.time()
        print(('before render', time_before_render))
        seqs = s.render()
        print(('after render', time.time() - time_before_render))

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
            return Delay(24)
        elif symbol == 'B4':            #Identity
            return Delay(24)
        elif symbol == 'B5':
            return r(-np.pi, X_AXIS)
        elif symbol == 'B6':
            return r(-np.pi, Y_AXIS)
        elif symbol == 'B7':
            return Delay(24)            #Z(-PI)


    def seq2_table(self, symbol):
        r2 = self.qubit2_info.rotate
        if symbol == 'A1':
            return r2(np.pi/2, X_AXIS)
        elif symbol == 'A2':
            return r2(np.pi/2, Y_AXIS)
        elif symbol == 'A3':
            return r2(-np.pi/2, X_AXIS)
        elif symbol == 'A4':
            return r2(-np.pi/2, Y_AXIS)
        elif symbol == 'B1':
            return r2(np.pi, X_AXIS)  
        elif symbol == 'B2':
            return r2(np.pi, Y_AXIS)
        elif symbol == 'B3':            #Z(PI)
            return Delay(24)
        elif symbol == 'B4':            #Identity
            return Delay(24)
        elif symbol == 'B5':
            return r2(-np.pi, X_AXIS)
        elif symbol == 'B6':
            return r2(-np.pi, Y_AXIS)
        elif symbol == 'B7':
            return Delay(24)            #Z(-PI)
#















    def analyze(self, data, fig):
        self.Pg_cplx = analysis(self, data, fig)
        return self.Pg_cplx
