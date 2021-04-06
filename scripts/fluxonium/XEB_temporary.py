#!/usr/bin/env python3

import random as rnd

#import cliffords

#log = logging.getLogger('LabberDriver')
import os
path_currentdir  = os.path.dirname(os.path.realpath(__file__)) # curret directory

import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import math
import random 
import time
import lmfit
import pickle


def exp_decay(params, x, data):
    est = params['A'] * params['alpha']**x + params['B']
    return data - est

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
    
    params = lmfit.Parameters()
    params.add('B', value=np.min(ys))
    params.add('A', value = np.max(ys))
    params.add('alpha', value=xs[-1]/2.0)
#    result = lmfit.minimize(exp_decay, params, args=(xs, ys))
#    lmfit.report_fit(result.params)
    
#    fig.axes[0].plot(xs, -exp_decay(result.params, xs, 0), label='Fit, alpha = %.03f us +/- %.03f us '%(result.params['alpha'].value, result.params['alpha'].stderr))
    fig.axes[0].clear()
    fig.axes[0].plot(xs, y1s, 'bs', ms=3, color='r', linestyle = '-', label='none')
    fig.axes[0].plot(xs, y2s, 'rs', ms=3, color = 'b', linestyle = '-', label= 'pi pulse on 1')    
    fig.axes[0].plot(xs, y3s, 'bs', ms=3, color= 'g', linestyle = '-', label = 'pi pulse on 2')
    fig.axes[0].plot(xs, y4s, 'rs', ms=3, color='y', linestyle = '-', label = 'pi pulse on both')  
    fig.axes[0].legend(loc=0)
    fig.axes[0].set_ylabel('Phase [AU]')
    fig.axes[0].set_xlabel('# of Cliffords')
    fig.canvas.draw()
    
    ys = meas.avg_data
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
    Y3 = np.mean(calibration_qubit1_excited)
    Y2 = np.mean(calibration_qubit2_excited)
    Y4 = np.mean(calibration_bothqubits_excited)
    Y1 = np.mean(calibration_ground)
    print Y1, Y2, Y3, Y4


    Igg = 0.8867067517164442
    Ieg = 0.07810721368681817
    Ige = 0.03233752366966949
    Iee = 0.0028485109270681716


    I_matrix = np.matrix([[Igg, Ige, Ieg, Iee], [Ige, Igg, Iee, Ieg], 
                          [Ieg, Iee, Igg, Ige], [Iee, Ieg, Ige, Igg]])
#    
    Y_vector = [Y1, Y2, Y3, Y4] #made of calibration points
    V_vector = np.zeros(4)
    
    V_vector =  np.dot(np.linalg.inv(I_matrix), Y_vector)
    Vgg = V_vector[0] 
    Vge= V_vector[1]
    Veg = V_vector[2]
    Vee= V_vector[3] 


    rd = y1s[12:]
    bl = y2s[12:]
    gr = y3s[12:]
    yw = y4s[12:]




    
    y_vector = [rd, gr, bl, yw]


    V_matrix = np.matrix([[Vgg, Vge, Veg, Vee], [Vge, Vgg, Vee, Veg], 
                          [Veg, Vee, Vgg, Vge], [Vee, Veg, Vge, Vgg]])

    P = np.dot(np.linalg.inv(V_matrix), y_vector)  #those are already our real populations 
#    print('P:', np.abs(P))
#    print(np.real(P))

###    
    Pgg = np.transpose(P[0])
    Pgg= Pgg.A1
    
#    fig2, axes2 = plt.subplots(2)
#    axes2[0].plot(xs[12:], np.real(Pgg))
#    axes2[0].plot(xs[12:], np.real(Pg1*Pg2), color='r')
#    axes2[1].plot(xs[12:], np.imag(Pgg))
    
    final_states = meas.exp_dists
    ideal_pops = np.square((np.absolute(final_states)))


    for i in range(meas.N_cycles): 
        ideal_pops[i] = np.dot(I_matrix, ideal_pops[i])
#
#
#    print('ideal_pops:', ideal_pops)
#    
#
    
    inc_pops = [0.25, 0.25, 0.25, 0.25]
#    
    H_inc_exp = -(np.dot(inc_pops, np.log(ideal_pops)))
    H_inc_exp = np.asarray(H_inc_exp).reshape(-1)

#    H_meas_exp = -(np.dot(np.transpose(P), np.log(ideal_pops)))
#    H_meas_exp = np.asarray(H_meas_exp).reshape(-1)
    P0 =  np.transpose(P_correct[0])
    P0= P0.A1

    P1 =  np.transpose(P_correct[1])
    P1= np.real(P1.A1)
    P2 =  np.transpose(P_correct[2])
    P2= np.real(P2.A1)
    P3 =  np.transpose(P_correct[3])
    P3= np.real(P3.A1)




#    H_meas_exp = np.zeros(meas.N_cycles)
#    for i in range(meas.N_cycles):
#     H_meas_exp[i] = np.asarray(-np.dot(np.transpose(P)[i], np.log(ideal_pops[i]))).reshape(-1)[0]    
#    

    H_meas_exp = np.zeros(meas.N_cycles)
    for i in range(meas.N_cycles):
        H_meas_exp[i] = np.asarray(-np.dot(np.transpose(np.abs(P))[i], np.log(ideal_pops[i]))).reshape(-1)[0]    




    H_exp = np.zeros(meas.N_cycles)
    for i in range(meas.N_cycles):
        H_exp[i] = -(np.dot(np.transpose(ideal_pops[i]), np.log(ideal_pops[i]))).reshape(-1)[0]
#    
    alpha = (H_inc_exp - H_meas_exp)/(H_inc_exp - H_exp)
#    
    plt.figure()
    plt.plot(np.linspace(1, meas.N_cycles, meas.N_cycles), alpha, linestyle='None', marker='o')
    print('alpha:', alpha)
    print('H_inc_exp was:', H_inc_exp)
    print('H_meas_exp was:', H_meas_exp)
    print('H_exp was:', H_exp)
    
    return [alpha]


def CheckIdentity(matrix):
    """
    Check whether the matrix is identity by calculating it numerically.

    Parameters
    ----------
    matrix: 4x4 np.matrix
        matrix

    Returns
    -------
    result: bool
        True, if identity.
    """

    #Check all the diagonal entries.
#    if ((np.abs(matrix[0,0]-1)< 1e-6) and
#        (np.abs(matrix[1,1]-1)< 1e-6) and
#        (np.abs(matrix[2,2]-1)< 1e-6) and
#        (np.abs(matrix[3,3]-1)< 1e-6)):
    if ((np.abs(np.abs(matrix[0,0])-1)< 1e-3) and
        (np.abs(np.abs(matrix[1,1])-1)< 1e-3) and
        (np.abs(np.abs(matrix[2,2])-1)< 1e-3) and
        (np.abs(np.abs(matrix[3,3])-1)< 1e-3) and
        (np.abs(matrix[1,1]/matrix[0,0]-1)<1e-3) and
        (np.abs(matrix[2,2]/matrix[0,0]-1)<1e-3) and
        (np.abs(matrix[3,3]/matrix[0,0]-1)<1e-3)):
        return True
    else:
        return False
    
def evaluate_sequence(gate_seq_1, gate_seq_2, generator = 'CZ'):
    """
    Evaluate the two qubit gate sequence.

    Parameters
    ----------
    gate_seq_1: list of class Gate (defined in "gates.py")
        The gate sequence applied to Qubit "1"

    gate_seq_2: list of class Gate (defined in "gates.py")
        The gate sequence applied to Qubit "2"

    Returns
    -------
    twoQ_gate: np.matrix (shape = (4,4))
        The evaulation result.
    """
    
    twoQ_gate = np.matrix(
        [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    for i in range(len(gate_seq_1)):
        
        gate_1 = np.matrix([[1, 0], [0, 1]])
        gate_2 = np.matrix([[1, 0], [0, 1]])        
        if (gate_seq_1[i] == 'I'):
            pass
        elif (gate_seq_1[i] == 'Ip'):
            pass
        elif (gate_seq_1[i] == 'Ic'):
            pass
        elif (gate_seq_1[i] == 'X2p'):
            gate_1 = np.matmul(
                np.matrix([[1, -1j], [-1j, 1]]) / np.sqrt(2), gate_1)
        elif (gate_seq_1[i] == 'X2m'):
            gate_1 = np.matmul(
                np.matrix([[1, 1j], [1j, 1]]) / np.sqrt(2), gate_1)
        elif (gate_seq_1[i] == 'Y2p'):
            gate_1 = np.matmul(
                np.matrix([[1, -1], [1, 1]]) / np.sqrt(2), gate_1)
        elif (gate_seq_1[i] == 'Y2m'):
            gate_1 = np.matmul(
                np.matrix([[1, 1], [-1, 1]]) / np.sqrt(2), gate_1)
        elif (gate_seq_1[i] == 'Xp'):
            gate_1 = np.matmul(np.matrix([[0, -1j], [-1j, 0]]), gate_1)
        elif (gate_seq_1[i] == 'Xpm'):
            gate_1 = np.matmul(np.matrix([[0, 1j], [1j, 0]]), gate_1)
        elif (gate_seq_1[i] == 'Yp'):
            gate_1 = np.matmul(np.matrix([[0, -1], [1, 0]]), gate_1)
        elif (gate_seq_1[i] == 'Ypm'):
            gate_1 = np.matmul(np.matrix([[0, 1], [-1, 0]]), gate_1)
        elif (gate_seq_1[i] == 'VZ2p'):
            gate_1 = np.matmul(np.matrix([[1+1j, 0], [0, 1-1j]]) / np.sqrt(2), gate_1)
        elif (gate_seq_1[i] == 'VZ2m'):
            gate_1 = np.matmul(np.matrix([[1-1j, 0], [0, 1+1j]]) / np.sqrt(2), gate_1)
        elif (gate_seq_1[i] == 'VZp'):
            gate_1 = np.matmul(np.matrix([[-1j, 0], [0, 1j]]), gate_1)
#        elif (gate_seq_1[i] == 'VZpm'):
#            gate_1 = np.matmul(np.matrix([[1j, 0], [0, -1j]]), gate_1)
        elif (gate_seq_1[i] == 'VZ4p'):
            gate_1 = np.matmul(np.matrix([[(np.sqrt(2+np.sqrt(2))/2)+(np.sqrt(2-np.sqrt(2))/2)*1j, 0], 
                                           [0, (np.sqrt(2+np.sqrt(2))/2)-(np.sqrt(2-np.sqrt(2))/2)*1j]]), gate_1)
        elif (gate_seq_1[i] == 'VZ4m'):
            gate_1 = np.matmul(np.matrix([[(np.sqrt(2+np.sqrt(2))/2)-(np.sqrt(2-np.sqrt(2))/2)*1j, 0],
                                           [0, (np.sqrt(2+np.sqrt(2))/2)+(np.sqrt(2-np.sqrt(2))/2)*1j]]), gate_1)

        if (gate_seq_2[i] == 'I'):
            pass
        elif (gate_seq_2[i] == 'Ip'):
            pass
        elif (gate_seq_2[i] == 'Ic'):
            pass
        elif (gate_seq_2[i] == 'X2p'):
            gate_2 = np.matmul(
                np.matrix([[1, -1j], [-1j, 1]]) / np.sqrt(2), gate_2)
        elif (gate_seq_2[i] == 'X2m'):
            gate_2 = np.matmul(
                np.matrix([[1, 1j], [1j, 1]]) / np.sqrt(2), gate_2)
        elif (gate_seq_2[i] == 'Y2p'):
            gate_2 = np.matmul(
                np.matrix([[1, -1], [1, 1]]) / np.sqrt(2), gate_2)
        elif (gate_seq_2[i] == 'Y2m'):
            gate_2 = np.matmul(
                np.matrix([[1, 1], [-1, 1]]) / np.sqrt(2), gate_2)
        elif (gate_seq_2[i] == 'Xp'):
            gate_2 = np.matmul(np.matrix([[0, -1j], [-1j, 0]]), gate_2)
        elif (gate_seq_2[i] == 'Xpm'):
            gate_2 = np.matmul(np.matrix([[0, 1j], [1j, 0]]), gate_2)
        elif (gate_seq_2[i] == 'Yp'):
            gate_2 = np.matmul(np.matrix([[0, -1], [1, 0]]), gate_2)
        elif (gate_seq_2[i] == 'Ypm'):
            gate_2 = np.matmul(np.matrix([[0, 1], [-1, 0]]), gate_2)
        elif (gate_seq_2[i] == 'VZ2p'):
            gate_2 = np.matmul(np.matrix([[1+1j, 0], [0, 1-1j]]) / np.sqrt(2), gate_2)
        elif (gate_seq_2[i] == 'VZ2m'):
            gate_2 = np.matmul(np.matrix([[1-1j, 0], [0, 1+1j]]) / np.sqrt(2), gate_2)
        elif (gate_seq_2[i] == 'VZp'):
            gate_2 = np.matmul(np.matrix([[-1j, 0], [0, 1j]]), gate_2)
#        elif (gate_seq_2[i] == 'VZpm'):
#            gate_2 = np.matmul(np.matrix([[1j, 0], [0, -1j]]), gate_2)
        elif (gate_seq_2[i] == 'VZ4p'):
            gate_2 = np.matmul(np.matrix([[(np.sqrt(2+np.sqrt(2))/2)+(np.sqrt(2-np.sqrt(2))/2)*1j, 0], 
                                           [0, (np.sqrt(2+np.sqrt(2))/2)-(np.sqrt(2-np.sqrt(2))/2)*1j]]), gate_2)
        elif (gate_seq_2[i] == 'VZ4m'):
            gate_2 = np.matmul(np.matrix([[(np.sqrt(2+np.sqrt(2))/2)-(np.sqrt(2-np.sqrt(2))/2)*1j, 0],
                                           [0, (np.sqrt(2+np.sqrt(2))/2)+(np.sqrt(2-np.sqrt(2))/2)*1j]]), gate_2)

        gate_12 = np.kron(gate_1, gate_2)  #Matrix follows gg, ge, eg, ee
        if generator == 'CZ':
#            if (gate_seq_1[i] == gates.CZ or gate_seq_2[i] == gates.CZ):
            if (gate_seq_2[i] == 'CZ'):
                gate_12 = np.matmul(
                        np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0],
                                   [0, 0, 0, -1]]), gate_12)
        elif generator == 'iSWAP':
            if (gate_seq_1[i] == gates.iSWAP or gate_seq_2[i] == gates.iSWAP):
                gate_12 = np.matmul(
                        np.matrix([[1, 0, 0, 0], [0, 0, 1j, 0], [0, 1j, 0, 0],
                                   [0, 0, 0, 1]]), gate_12)
            
        elif generator == 'CNOT':
            if (gate_seq_1[i] == 'CNOT' or gate_seq_2[i] == 'CNOT'):
                gate_12 = np.matmul(
                            np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1],
                                       [0, 0, 1, 0]]), gate_12)
        elif generator == 'ZX90':
            if (gate_seq_2[i] == 'ZX90'): #qubit1 is control, qubit2 is target
                gate_12 = np.matmul(
                        np.matrix([[1, 1j, 0, 0], [1j, 1, 0, 0], [0, 0, -1, 1j],
                                   [0, 0, 1j, -1]]) / np.sqrt(2), gate_12) #This still is the crazy matrix that worked the other day
       
        elif generator == 'CX':
            if (gate_seq_1[i] == 'CX' or gate_seq_2[i] == 'CX'):
                gate_12 = np.matmul(
                            np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, -1j],
                                       [0, 0, -1j, 0]]), gate_12)
    
        twoQ_gate = np.matmul(gate_12, twoQ_gate)
        # log.info('two qubit gate: ' + str(twoQ_gate))
    return twoQ_gate    
    

class CrossEB(Measurement1D):
    """Two qubit randomized benchmarking."""

    filepath_lookup_table = ""

    def __init__(self, qubit_info, qubit2_info, twoQ_info, cancel_info, num_cal_points, N_cycles, seq=None, postseq=None, cnum=None,
                 interleave=None, use_virtual_Z=False, singleQ_phases=[0,0], **kwargs):
        self.qubit_info = qubit_info
        self.qubit2_info = qubit2_info
        self.twoQ_info = twoQ_info
        self.cancel_info = cancel_info
        self.N_cycles = N_cycles
        self.num_cal_points = num_cal_points
        XS = np.asarray(range(N_cycles+4*self.num_cal_points)) - (4*self.num_cal_points-1)
        self.xs = np.array([XS,XS,XS,XS]).transpose().flatten() # for plotting purposes
        self.filepath_lookup_table = ""
        self.cnum=cnum
        self.interleave = interleave
        self.use_virtual_Z = use_virtual_Z
        self.singleQ_phases = singleQ_phases
        
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        
            
        super(CrossEB, self).__init__(4*(N_cycles+4*num_cal_points), infos=(qubit_info,qubit2_info,twoQ_info,cancel_info), **kwargs)
        self.data.create_dataset('Cycles', data=range(4*(N_cycles+4*num_cal_points)))
#        self.data.set_attrs(
#            cnum=cnum,
#            interleave=interleave
#        )
         

    def generate(self):
        s = Sequence()
        r = self.qubit_info.rotate
        r2 = self.qubit2_info.rotate
        r3 = self.twoQ_info.rotate
        r4 = self.cancel_info.rotate
        q_len1 = self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len
        q_len2 = self.qubit2_info.chop*self.qubit2_info.w+self.qubit2_info.sq_len
        twoQ_len = self.twoQ_info.chop*self.twoQ_info.w+self.twoQ_info.sq_len# + self.cancel_info.chop*self.cancel_info.w+self.cancel_info.sq_len 

        # Generate 2QB RB sequence
        cycleSeq1 = []
        cycleSeq2 = []
        
        finalgateSeq1 = []
        finalgateSeq2 = []
        
        pulseSeq1 = []
        pulseSeq2 = []
        
        finalpulseSeq1 = []
        finalpulseSeq2 = []
        
        len1 = [0]
        len2 = [0]
        
        phi1 = [0]
        phi2 = [0]
        
        self.exp_dists = []
        
        for n in range(self.N_cycles):
            rndnum = rnd.randint(0, 63) 
            if self.cnum is not None:
                rndnum = self.cnum
            print(n, rndnum)
            temp_pulseSeq1 = []
            temp_pulseSeq2 = []
            self.add_cycle(rndnum, cycleSeq1, cycleSeq2, temp_pulseSeq1, temp_pulseSeq2, len1, len2, phi1, phi2, virtual=self.use_virtual_Z, final_gates=False)
            print(phi1[0], phi2[0])
            if self.interleave == 'ZX90':
                print ('This code does not support ZX90 yet')
               
            elif self.interleave == 'I':
                cliffordSeq1.append('I')
                cliffordSeq2.append('I')
    #               temp_pulseSeq1.append(Delay(q_len1))
    #               temp_pulseSeq2.append(Delay(q_len1))
    #               len1[0] = len1[0] + q_len1
    #               len2[0] = len2[0] + q_len1
                temp_pulseSeq1.append(Delay(32))
                temp_pulseSeq2.append(Delay(32))
                len1[0] = len1[0] + 32
                len2[0] = len2[0] + 32
               
            elif self.interleave == 'CZ': 
                cliffordSeq1.append('Ic')
                cliffordSeq2.append('CZ')
                temp_pulseSeq1.append(Delay(twoQ_len))
                temp_pulseSeq2.append(r3(np.pi,X_AXIS))
                len1[0] = len1[0] + twoQ_len
                len2[0] = len2[0] + twoQ_len
                phi1[0] = phi1[0] + self.singleQ_phases[0]
                phi2[0] = phi2[0] + self.singleQ_phases[1]
            pulseSeq1.append(temp_pulseSeq1)
            pulseSeq2.append(temp_pulseSeq2)
            rndnum = rnd.randint(0, 63)
            temp_finalgateSeq1 = []
            temp_finalgateSeq2 = []
            temp_finalpulseSeq1 = []
            temp_finalpulseSeq2 = []
            self.add_cycle(rndnum, temp_finalgateSeq1, temp_finalgateSeq2, temp_finalpulseSeq1, temp_finalpulseSeq2, len1, len2, phi1, phi2, virtual=self.use_virtual_Z, final_gates=True)
            finalpulseSeq1.append(temp_finalpulseSeq1)
            finalpulseSeq2.append(temp_finalpulseSeq2)
            finalgateSeq1.append(temp_finalgateSeq1)
            finalgateSeq2.append(temp_finalgateSeq2)
            print('cycleSeq1 is:', cycleSeq1)
            print('cycleSeq2 is:', cycleSeq2)
            print('finalgateSeq1 is:', finalgateSeq1)
            print('finalgateSeq2 is:', finalgateSeq2)
            print('temp_finalgateSeq1 is:', temp_finalgateSeq1)
            print('temp_finalgateSeq2 is:', temp_finalgateSeq2)
            
            
            self.exp_dists.append(self.calc_exp_dist(cycleSeq1, cycleSeq2, temp_finalgateSeq1, temp_finalgateSeq2))
            print('expected final state is:', self.calc_exp_dist(cycleSeq1, cycleSeq2, temp_finalgateSeq1, temp_finalgateSeq2))


        for j in range(self.num_cal_points):
            s.append(self.seq)
#            temp_seq = Sequence()
#            temp_seq.append(r(np.pi,0))   
            for i in range(4):
                s.append(self.seq)
                s.append(r(np.pi,0))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration pi pulses qubit 1')


        for j in range(self.num_cal_points):

            temp_seq = Sequence()
            temp_seq.append(r2(np.pi,0))   
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

            temp_seq = Sequence()
            temp_seq.append(Combined([r(np.pi,0),r2(np.pi,0)]))   
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
            temp_seq.append(Delay(24))   
            for i in range(4):
                s.append(self.seq)
                s.append(Join(temp_seq))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration ground state')





        for m in range(self.N_cycles):

            for ROpostseq in [None, r(np.pi,0), r2(np.pi,0),
                              Combined([r(np.pi,0),r2(np.pi,0)])]:
                s.append(self.seq)
                for k in range(m+1):
                    s.append(Combined([Join(pulseSeq1[k]), Join(pulseSeq2[k])]))
#                    print(k, pulseSeq1[k], pulseSeq2[k])
                s.append(Combined([Join(finalpulseSeq1[m]), Join(finalpulseSeq2[m])]))

#                
                if ROpostseq is not None:
                    s.append(ROpostseq)
                s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
#                s.append(Delay(200))

#          
#            # Avoid Error: zero-size array to reduction operation maximum which has no identity (05/05/2019)
#            if (gateSeq1 == [] and gateSeq2 == []):
#                gateSeq1.append(Delay(4*w+sq_len))
#                gateSeq2.append(Delay(4*w+sq_len))
#
#            # test the recovery gate
#            psi_gnd = np.matrix('1; 0; 0; 0') # ground state |00>
#            if write_seq == True:
#                import os
#                from datetime import datetime
#                directory = os.path.join(path_currentdir,'2QB_RBseq')
#                if not os.path.exists(directory):
#                    os.makedirs(directory)
#                filename = datetime.now().strftime('%Y-%m-%d %H-%M-%S-f')[:-3] + '_N_cliffords=%d_seed=%d.txt'%(N_cliffords,randomize)
#                # filename = datetime.now().strftime('%Y-%m-%d %H-%M-%S-%f')[:-3] + '_N_cliffords=%d_seed=%d.txt'%(N_cliffords,randomize)
#                filepath = os.path.join(directory,filename)
#                log.info('make file: ' + filepath)
#                with open(filepath, "w") as text_file:
#                    print('New Sequence', file=text_file)
#                    for i in range(len(gateSeq1)):
#                        print("Index: %d, Gate: ["%(i) + cliffords.Gate_to_strGate(gateSeq1[i]) + ", " + cliffords.Gate_to_strGate(gateSeq2[i]) +']', file=text_file)
#                    for i in range(len(cliffordSeq1)):
#                         print("CliffordIndex: %d, Gate: ["%(i) + cliffords.Gate_to_strGate(cliffordSeq1[i]) + ", " + cliffords.Gate_to_strGate(cliffordSeq2[i]) +']', file=text_file)
#                    for i in range(len(recoverySeq1)):
#                         print("RecoveryIndex: %d, Gate: ["%(i) + cliffords.Gate_to_strGate(recoverySeq1[i]) + ", " + cliffords.Gate_to_strGate(recoverySeq2[i]) +']', file=text_file)
#            psi = np.matmul(evaluate_sequence(gateSeq1, gateSeq2), psi_gnd)
#
#            np.set_printoptions(precision=2)
#            log.info('The matrix of the overall gate sequence:')
#            log.info(evaluate_sequence(gateSeq1, gateSeq2))
#
#            log.info('--- TESTING THE RECOVERY GATE ---')
#            log.info('The probability amplitude of the final state vector: ' + str(np.matrix(psi).flatten()))
#            log.info('The population of the ground state after the gate sequence: %.4f'%(np.abs(psi[0,0])**2))
#            log.info('-------------------------------------------')
#
#
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs
    
    def pad_sequences(self, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2):
        delta = np.abs(length1[0] - length2[0])
#        print('delta:', delta)
        if delta > 0:
                if length1[0] < length2[0]:
#                    gate_seq_1.extend('I')
                    pulse_seq_1.append(Delay(delta))
                    length1[0] = length1[0] + delta
                elif length1[0] >  length2[0]:
                    pulse_seq_2.append(Delay(delta))
                    length2[0] = length2[0] + delta
#        print('length1 after:', length1[0])
#        print('length2 after:', length2[0])

        while len(gate_seq_1) < len(gate_seq_2):
            gate_seq_1.append('Ip')
        while len(gate_seq_1) > len(gate_seq_2):
            gate_seq_2.append('Ip')
    
    
    def add_singleQ_gates(self, index, gate_seq, pulse_seq, length, qubit, pad_with_I=False, **kwargs):
        """Add single qubit clifford (24)."""
#        print(index)
#        print(type(index))
        if qubit == 1:
            r = self.qubit_info.rotate
            q_len = self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len
        elif qubit == 2:
            r = self.qubit2_info.rotate
            q_len = self.qubit2_info.chop*self.qubit2_info.w+self.qubit2_info.sq_len
        w = self.qubit_info.w
        sq_len = self.qubit_info.sq_len
        
        length_before = len(gate_seq)
    
        # pi/2 rotations
        if index == 0:
            pulse_seq.append(r(np.pi/2, 0))
            gate_seq.append('X2p')
            length[0] = length[0] + q_len
        elif index == 1:
            pulse_seq.append(r(-np.pi/2, 0))
            gate_seq.append('X2m')
            length[0] = length[0] + q_len
        elif index == 2:
            pulse_seq.append(r(np.pi/2, np.pi/2))
            gate_seq.append('Y2p')
            length[0] = length[0] + q_len
        elif index == 3:
            pulse_seq.append(r(-np.pi/2, np.pi/2))
            gate_seq.append('Y2m')
            length[0] = length[0] + q_len
        elif index == 4:
            pulse_seq.append(r(np.pi/2, np.pi/4))
            gate_seq.append('XpY2p')
            length[0] = length[0] + q_len
        elif index == 5:
            pulse_seq.append(r(-np.pi/2, np.pi/4))
            gate_seq.append('XpY2m')
            length[0] = length[0] + q_len
        elif index == 6:
            pulse_seq.append(r(np.pi/2, -np.pi/4))
            gate_seq.append('XmY2p')
            length[0] = length[0] + q_len
        elif index == 7:
            pulse_seq.append(r(-np.pi/2, -np.pi/4))
            gate_seq.append('XmY2m')
            length[0] = length[0] + q_len
        else:
            raise ValueError(
                'index is out of range. it should be smaller than 24 and greater'
                ' or equal to 0: ', str(index))
    
        length_after = len(gate_seq)
        if pad_with_I:
            # Force the clifford to have a length of 3 gates
            for i in range(3-(length_after-length_before)):
                gate_seq.append('Ip')
                pulse_seq.append(Delay(q_len))
                length[0] = length[0] + q_len
                
    def add_singleQ_gates_virtualZ(self, index, gate_seq, pulse_seq, length, phase, qubit, pad_with_I=False, **kwargs):
        """Add single qubit clifford using virtual Z gates (24)."""
#        print(index)
#        print(type(index))
        if qubit == 1:
            r = self.qubit_info.rotate
            q_len = self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len
        elif qubit == 2:
            r = self.qubit2_info.rotate
            q_len = self.qubit2_info.chop*self.qubit2_info.w+self.qubit2_info.sq_len
        w = self.qubit_info.w
        sq_len = self.qubit_info.sq_len
        
        length_before = len(gate_seq)
    
        # pi/2 rotations
        if index == 0:
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))))
            gate_seq.append('X2p')
            length[0] = length[0] + q_len
        elif index == 1:
            pulse_seq.append(r(-np.pi/2, (phase[0] % (2*np.pi))))
            gate_seq.append('X2m')
            length[0] = length[0] + q_len
        elif index == 2:
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))+np.pi/2))
            gate_seq.append('VZ2p')
            gate_seq.append('X2p')
            gate_seq.append('VZ2m')
            length[0] = length[0] + q_len
        elif index == 3:
            pulse_seq.append(r(-np.pi/2, (phase[0] % (2*np.pi))+np.pi/2))
            gate_seq.append('VZ2p')
            gate_seq.append('X2m')
            gate_seq.append('VZ2m')
            length[0] = length[0] + q_len
        elif index == 4:
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))+np.pi/4))
            gate_seq.append('VZ4p')
            gate_seq.append('X2p')
            gate_seq.append('VZ4m')
            length[0] = length[0] + q_len
        elif index == 5:
            pulse_seq.append(r(-np.pi/2, (phase[0] % (2*np.pi))+np.pi/4))
            gate_seq.append('VZ4p')
            gate_seq.append('X2m')
            gate_seq.append('VZ4m')
            length[0] = length[0] + q_len
        elif index == 6:
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))-np.pi/4))
            gate_seq.append('VZ4m')
            gate_seq.append('X2p')
            gate_seq.append('VZ4p')
            length[0] = length[0] + q_len
        elif index == 7:
            pulse_seq.append(r(-np.pi/2, (phase[0] % (2*np.pi))-np.pi/4))
            gate_seq.append('VZ4m')
            gate_seq.append('X2m')
            gate_seq.append('VZ4p')
            length[0] = length[0] + q_len
        else:
            raise ValueError(
                'index is out of range. it should be smaller than 24 and greater'
                ' or equal to 0: ', str(index))
    
        length_after = len(gate_seq)
        if pad_with_I:
            # Force the clifford to have a length of 3 gates
            for i in range(3-(length_after-length_before)):
                gate_seq.append('Ip')
                pulse_seq.append(Delay(q_len))
                length[0] = length[0] + q_len
    
    def add_cycle(self, index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, phase1, phase2, virtual, final_gates=False, **kwargs):
        """Add single-qubit-gates-only-based two Qubit Clifford.
    
        (24*24 = 576)
        (gate_seq_1: gate seq. of qubit #1, gate_seq_t: gate seq. of qubit #2)
        """
        r = self.qubit_info.rotate
        r2 = self.qubit2_info.rotate
        r3 = self.twoQ_info.rotate
        twoQ_len = self.twoQ_info.chop*self.twoQ_info.w+self.twoQ_info.sq_len
        
        index_1 = index % 8
    
        index_2 = (index // 8) % 8
##        
        if virtual == True:
            self.add_singleQ_gates_virtualZ(index_1, gate_seq_1, pulse_seq_1, length1, phase1, 1)
            self.add_singleQ_gates_virtualZ(index_2, gate_seq_2, pulse_seq_2, length2, phase2, 2)
        else:
            self.add_singleQ_gates(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_gates(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
        self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)    
        if final_gates == False:
            gate_seq_1.append('Ic')
            gate_seq_2.append('CZ')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(np.pi, X_AXIS))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            phase1[0] = phase1[0] + self.singleQ_phases[0]
            phase2[0] = phase2[0] + self.singleQ_phases[1]
        else:
            pass  
#        
    def calc_exp_dist(self, gate_seq_1, gate_seq_2, final_gate_seq_1, final_gate_seq_2):
        initial_state = np.matrix('1; 0; 0; 0')
        
        matrix_cycles = evaluate_sequence(gate_seq_1, gate_seq_2, generator='CZ')
        
        matrix_final_gates = evaluate_sequence(final_gate_seq_1, final_gate_seq_2, generator='CZ')
        
        total_matrix = np.matmul(matrix_final_gates, matrix_cycles)
    
        final_state = np.matmul(total_matrix, initial_state)
        
    #    prob_dist = final_state*np.conj(final_state)
        np.savetxt('final_state_try.txt', final_state)
        return final_state    

    def analyze(self, data=None, fig=None):
        results = analysis(self, data, fig)
        self.alpha = results[0]

        
        return self.alpha