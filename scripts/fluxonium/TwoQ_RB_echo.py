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

    rd = y1s[12:]
    bl = y2s[12:]
    gr = y3s[12:]
    yw = y4s[12:]
    Pg1 = ((-rd-gr+bl+yw)/(Veg-Vgg+Vee-Vge)+1)/2
    Pg2 = ((-rd-bl+gr+yw)/(Vge-Vgg+Vee-Veg)+1)/2

    Pegge = ((rd+yw-bl-gr)/(Vge+Veg-Vee-Vgg)+1)/2
    Pg_cplx = (Pg1+Pg2-Pegge)/2

    fig2, axes2 = plt.subplots(2)
    axes2[0].plot(xs[12:], np.real(Pg_cplx))
    axes2[0].plot(xs[12:], np.real(Pg1*Pg2), color='r')
    axes2[1].plot(xs[12:], np.imag(Pg_cplx))
    
    return Pg_cplx


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


def evaluate_sequence(gate_seq_1, gate_seq_2, generator = 'ZX90'):
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
#            maxLen = max(len(gate_seq_1), len(gate_seq_2))
#            if len(gate_seq_1) < maxLen:
#                gate_seq_1.extend('I')
#            if len(gate_seq_2) < maxLen:
#                gate_seq_2.extend('I')
            
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

        gate_12 = np.kron(gate_1, gate_2)  #Matrix follows gg, ge, eg, ee
#            if generator == 'CZ':
#                if (gate_seq_1[i] == gates.CZ or gate_seq_2[i] == gates.CZ):
#                    gate_12 = np.matmul(
#                        np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0],
#                                   [0, 0, 0, -1]]), gate_12)
#            elif generator == 'iSWAP':
#                if (gate_seq_1[i] == gates.iSWAP or gate_seq_2[i] == gates.iSWAP):
#                    gate_12 = np.matmul(
#                        np.matrix([[1, 0, 0, 0], [0, 0, 1j, 0], [0, 1j, 0, 0],
#                                   [0, 0, 0, 1]]), gate_12)
        
        if generator == 'CNOT':
            if (gate_seq_2[i] == 'CNOT'): #qubit1 is control, qubit2 is target
                gate_12 = np.matmul(
                        np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1],
                                   [0, 0, 1, 0]]), gate_12)
        elif generator == 'ZX90':
            if (gate_seq_2[i] == 'ZX90'): #qubit1 is control, qubit2 is target
                gate_12 = np.matmul(
                        np.matrix([[1, 1j, 0, 0], [1j, 1, 0, 0], [0, 0, 1, -1j],
                                   [0, 0, -1j, 1]]) / np.sqrt(2), gate_12)
        elif generator == 'CX':
            if (gate_seq_2[i] == 'CX'): #qubit1 is control, qubit2 is target
                gate_12 = np.matmul(
                        np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, -1j], [0, 0, -1j, 0]]), gate_12)
        twoQ_gate = np.matmul(gate_12, twoQ_gate)
    # log.info('two qubit gate: ' + str(twoQ_gate))
    return twoQ_gate
       

class TwoQubit_RB(Measurement1D):
    """Two qubit randomized benchmarking."""

    filepath_lookup_table = ""

    def __init__(self, qubit_info, qubit2_info, twoQ_info, num_cal_points, N_cliffords, generator='ZX90', seq=None, postseq=None, num_gates=0, category='all', cnum=None,
                 find_cheapest_recovery=False, interleave=False, **kwargs):
        self.qubit_info = qubit_info
        self.qubit2_info = qubit2_info
        self.twoQ_info = twoQ_info
        self.N_cliffords = N_cliffords
        self.num_cal_points = num_cal_points
        XS = np.asarray(list(range(N_cliffords+4*self.num_cal_points))) - (4*self.num_cal_points-1)
        self.xs = np.array([XS,XS,XS,XS]).transpose().flatten() # for plotting purposes
        self.filepath_lookup_table = ""
        self.cnum=cnum
        self.interleave = interleave
        
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.generator = generator
        self.category = category
        self.find_cheapest_recovery = find_cheapest_recovery
        self.num_gates = num_gates
        
            
        super(TwoQubit_RB, self).__init__(4*(N_cliffords+4*num_cal_points), infos=(qubit_info,qubit2_info,twoQ_info), **kwargs)
        self.data.create_dataset('Cliffords', data=list(range(4*(N_cliffords+4*num_cal_points))))
         

    def generate(self):
        s = Sequence()
        r = self.qubit_info.rotate
        r2 = self.qubit2_info.rotate
        r3 = self.twoQ_info.rotate
        q_len1 = self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len
        q_len2 = self.qubit2_info.chop*self.qubit2_info.w+self.qubit2_info.sq_len
        twoQ_len = self.twoQ_info.chop*self.twoQ_info.w+self.twoQ_info.sq_len# +  2*(self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len)


#        randomize = config['Randomize']
#        interleave = config['Interleave 2-QB Gate']
#        write_seq = config.get('Write sequence as txt file', False)
        
#        rnd.seed(randomize)

        # Generate 2QB RB sequence
        cliffordSeq1 = []
        cliffordSeq2 = []
        recov_cliffordSeq1 = []
        recov_cliffordSeq2 = []
        pulseSeq1 = []
        pulseSeq2 = []
        recov_pulseSeq1 = []
        recov_pulseSeq2 = []
        len1 = [0]
        len2 = [0]
        recov_len1 = [0]
        recov_len2 = [0]
        
        for n in range(self.N_cliffords):
           if self.category == 'single':
               rndnum = rnd.randint(0, 576-1) #Only applying single qubit gates
           elif self.category == 'CNOT':
               rndnum = rnd.randint(576, 576+5184-1) #Only applying single qubit gates
           elif self.category == 'iSWAP':
               rndnum = rnd.randint(576+5184, 576+5184+5184-1) #Only applying single qubit gates
           elif self.category == 'SWAP':
               rndnum = rnd.randint(576+5184+5184, 11520-1) #Only applying single qubit gates               
           else: 
               rndnum = rnd.randint(0, 11519)
           if self.cnum is not None:
               rndnum = self.cnum
           print((n, rndnum))
           temp_pulseSeq1 = []
           temp_pulseSeq2 = []
           self.add_twoQ_clifford(rndnum, cliffordSeq1, cliffordSeq2, temp_pulseSeq1, temp_pulseSeq2, len1, len2, generator = self.generator)
           if self.interleave == 'ZX90':
               pass
#               cliffordSeq1.append('Ic')
#               cliffordSeq2.append('ZX90')
#               temp_pulseSeq1.append(Delay(twoQ_len))
#               temp_pulseSeq2.append(r3(-np.pi,X_AXIS))
#               temp_pulseSeq2.append(r(np.pi,X_AXIS))
#               temp_pulseSeq2.append(r3(np.pi,X_AXIS))
#               temp_pulseSeq2.append(r(np.pi,X_AXIS))
#               len1[0] = len1[0] + twoQ_len
#               len2[0] = len2[0] + twoQ_len
           elif self.interleave == 'I':
               cliffordSeq1.append('I')
               cliffordSeq2.append('I')
               temp_pulseSeq1.append(Delay(70))
               temp_pulseSeq2.append(Delay(70))
               len1[0] = len1[0] + q_len1
               len2[0] = len2[0] + q_len1              
           elif self.interleave == 'Echo':
               cliffordSeq1.append('I')
               cliffordSeq2.append('I')
               temp_pulseSeq1.append(Delay(twoQ_len))
               temp_pulseSeq1.append(r(np.pi,X_AXIS))
               temp_pulseSeq1.append(Delay(twoQ_len))
               temp_pulseSeq1.append(r(np.pi,X_AXIS))
               temp_pulseSeq2.append(Delay(twoQ_len*2+q_len1*2))
               len1[0] = len1[0] + twoQ_len*2+q_len1*2
               len2[0] = len2[0] + twoQ_len*2+q_len1*2          
        
           print ('computing recovery')
           
#            # get recovery gate seq
           (recoverySeq1, recoverySeq2, recovery_pulseSeq1, recovery_pulseSeq2) = self.get_recovery_gate(cliffordSeq1, cliffordSeq2, generator = self.generator)
           
           recov_cliffordSeq1.append(recoverySeq1)
           recov_cliffordSeq2.append(recoverySeq2)
           recov_pulseSeq1.append(recovery_pulseSeq1)
           recov_pulseSeq2.append(recovery_pulseSeq2)
           pulseSeq1.append(temp_pulseSeq1)
           pulseSeq2.append(temp_pulseSeq2)
        print(('cliffordSeq1 is:', cliffordSeq1))
        print(('cliffordSeq2 is:', cliffordSeq2))
        print(('total # gates:', len(cliffordSeq1)))
        print(('total # gates:', len(cliffordSeq2)))

        print(('recov_cliffordSeq1 is:', recov_cliffordSeq1))
        print(('recov_cliffordSeq2 is:', recov_cliffordSeq2))
        
        
        self.num_gates = len(cliffordSeq1)

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


        for m in range(self.N_cliffords):

            for ROpostseq in [None, r(np.pi,0), r2(np.pi,0),
                              Combined([r(np.pi,0),r2(np.pi,0)])]:
                s.append(self.seq)
                for k in range(m+1):
                    s.append(Combined([Join(pulseSeq1[k]), Join(pulseSeq2[k])]))
                    
                s.append(Combined([Join(recov_pulseSeq1[m]), Join(recov_pulseSeq2[m])]))
            
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


    def get_recovery_gate(self, gate_seq_1, gate_seq_2, generator = 'ZX90'):
        """
        Get the recovery (the inverse) gate

        Parameters
        ----------
        gate_seq_1: list of class Gate
            The gate sequence applied to Qubit "1"

        gate_seq_2: list of class Gate
            The gate sequence applied to Qubit "2"

        generator: string
            Type of Native 2QB gate (optional)

        Returns
        -------
        (recovery_seq_1, recovery_seq_2): tuple of the lists
            The recovery gate
        """
        
        qubit_state = np.matrix(
            '1; 0; 0; 0')  # initial state: ground state |00>

        qubit_state = np.matmul(evaluate_sequence(
            gate_seq_1, gate_seq_2, generator = generator), qubit_state)

        # find recovery gate which makes qubit_state return to initial state
        if self.category == 'single':
            total_num_cliffords = 576 #Only applying single qubit gates
        else: 
            total_num_cliffords = 11520
        recovery_seq_1 = []
        recovery_seq_2 = []

        # Search the recovery gate in two Qubit clifford group

#        find_cheapest = True

        cheapest_recovery_seq_1 = []
        cheapest_recovery_seq_2 = []
#        log.info('*** get recovery gate *** ')
        if (self.find_cheapest_recovery == True):
            min_N_2QB_gate = np.inf
            min_N_1QB_gate = np.inf
            max_N_I_gate = -np.inf
            cheapest_index = None

#            use_lookup_table = config['Use a look-up table']
#            if (use_lookup_table == True):
#                filepath_lookup_table = config['File path of the look-up table']
#                if len(filepath_lookup_table) == 0:
#                    if (generator == 'CZ'):
#                        filepath_lookup_table = os.path.join(path_currentdir, 'recovery_rb_table.pickle')
#                    elif (generator == 'iSWAP'):
#                        filepath_lookup_table = os.path.join(path_currentdir, 'recovery_rb_table_iSWAP.pickle')
#                    
#                if filepath_lookup_table != self.filepath_lookup_table:
#                    log.info("Load Look-up table.")
#                    self.filepath_lookup_table = filepath_lookup_table
#                    self.dict_lookup_table = cliffords.loadData(filepath_lookup_table)
#                stabilizer = cliffords.get_stabilizer(qubit_state)
#                for index, item in enumerate(self.dict_lookup_table['psi_stabilizer']):
#                    if stabilizer == item:
#                        seq1 = self.dict_lookup_table['recovery_gates_QB1'][index]
#                        for str_Gate in seq1:
#                            cheapest_recovery_seq_1.append(cliffords.strGate_to_Gate(str_Gate))
#                        seq2 = self.dict_lookup_table['recovery_gates_QB2'][index]
#                        for str_Gate in seq2:
#                            cheapest_recovery_seq_2.append(cliffords.strGate_to_Gate(str_Gate))
#
#                        log.info("=== FOUND THE CHEAPEST RECOVERY GATE IN THE LOOK-UP TABLE. ===")
#                        log.info("QB1 recovery gate sequence: " + str(seq1))
#                        log.info("QB2 recovery gate sequence: " + str(seq2))
#                        log.info("=================================================")
#                        return(cheapest_recovery_seq_1, cheapest_recovery_seq_2)
#
#            log.info("--- COULDN'T FIND THE RECOVERY GATE IN THE LOOK-UP TABLE... ---")


        # Calculate the matrix of the clifford sequence
        matrix_cliffords = evaluate_sequence(gate_seq_1, gate_seq_2, generator = generator)
        print(('matrix_cliffords is:', matrix_cliffords))

        for i in range(total_num_cliffords):
            recovery_seq_1 = []
            recovery_seq_2 = []
            temp_pulse_seq_1 = []
            temp_pulse_seq_2 = []
            temp_recov_len1 = [0]
            temp_recov_len2 = [0]
            self.add_twoQ_clifford(i, recovery_seq_1, recovery_seq_2, temp_pulse_seq_1, temp_pulse_seq_2, temp_recov_len1, temp_recov_len2, generator = generator)
            
            # Calculate the matrix of the recovery clifford
            matrix_recovery = evaluate_sequence(recovery_seq_1, recovery_seq_2, generator = generator)

            # Calculate the matrix of the total clifford sequence
            matrix_total = np.matmul(matrix_recovery,matrix_cliffords)
            if (CheckIdentity(matrix_total)):
                if (self.find_cheapest_recovery == True):
                    # Less 2QB Gates, Less 1QB Gates, and More I Gates = the cheapest gates.
                    # The priority: less 2QB gates > less 1QB gates > more I gates
                    N_2QB_gate = 0
                    N_1QB_gate = 0
                    N_I_gate = 0

                    # count the numbers of the gates
                    for j in range(len(recovery_seq_1)):
#                        print(i, len(recovery_seq_1))
#                        if (recovery_seq_1[j] == gates.CZ or recovery_seq_2[j] == gates.CZ):
#                            N_2QB_gate += 1
#                        elif (recovery_seq_1[j] == gates.iSWAP or recovery_seq_2[j] == gates.iSWAP):
#                            N_2QB_gate += 1
                        if (recovery_seq_1[j] == 'CNOT' or recovery_seq_2[j] == 'CNOT'):
                            N_2QB_gate += 1
                        elif (recovery_seq_1[j] == 'ZX90' or recovery_seq_2[j] == 'ZX90'):
                            N_2QB_gate += 1
                        else:
                            N_1QB_gate += 2
                        if (recovery_seq_1[j] == 'I'):
                            N_I_gate += 1
                        if (recovery_seq_2[j] == 'I'):
                            N_I_gate += 1

                    if (N_2QB_gate <= min_N_2QB_gate): # if it has less 2QB gates, always update it
                        min_N_2QB_gate, min_N_1QB_gate, max_N_I_gate, cheapest_index = (N_2QB_gate, N_1QB_gate, N_I_gate, i)

                        if (N_1QB_gate <= min_N_1QB_gate): # *only if it has less 2QB gates*, check whether it has less 1QB gates
                            min_N_2QB_gate, min_N_1QB_gate, max_N_I_gate, cheapest_index = (N_2QB_gate, N_1QB_gate, N_I_gate, i)

                            if (N_I_gate >= max_N_I_gate): # *only if it has less 2QB gates & only if it has less 1QB gates*, check whether it has more I gates
                                min_N_2QB_gate, min_N_1QB_gate, max_N_I_gate, cheapest_index = (N_2QB_gate, N_1QB_gate, N_I_gate, i)

                    # check whether it is the cheapest
                    # if it has less 2QB gates, always update it.
                    if (N_2QB_gate < min_N_2QB_gate):
                        min_N_2QB_gate, min_N_1QB_gate, max_N_I_gate, cheapest_index = (N_2QB_gate, N_1QB_gate, N_I_gate, i)
#                        log.info('the cheapest sequence update! [N_2QB_gate, N_1QB_gate, N_I_gate, seq. index] ' + str([min_N_2QB_gate, min_N_1QB_gate, max_N_I_gate, cheapest_index]))
                    else:
                        # if it has equal # of 2QB gates and less 1QB gates, update it.
                        if (N_2QB_gate == min_N_2QB_gate and
                            N_1QB_gate < min_N_1QB_gate):
                            min_N_2QB_gate, min_N_1QB_gate, max_N_I_gate, cheapest_index = (N_2QB_gate, N_1QB_gate, N_I_gate, i)
#                            log.info('the cheapest sequence update! [N_2QB_gate, N_1QB_gate, N_I_gate, seq. index] ' + str([min_N_2QB_gate, min_N_1QB_gate, max_N_I_gate, cheapest_index]))
                        else:
                            # if it has equal # of 2QB & 1QB gates, and more 1QB gates, update it.
                            if (N_2QB_gate == min_N_2QB_gate and
                                N_1QB_gate == min_N_1QB_gate and
                                N_I_gate >= max_N_I_gate):
                                min_N_2QB_gate, min_N_1QB_gate, max_N_I_gate, cheapest_index = (N_2QB_gate, N_1QB_gate, N_I_gate, i)
#                                log.info('the cheapest sequence update! [N_2QB_gate, N_1QB_gate, N_I_gate, seq. index] ' + str([min_N_2QB_gate, min_N_1QB_gate, max_N_I_gate, cheapest_index]))

                else:
                    print(('recovery_index is:', i))
                    print(('matrix_recovery is:', matrix_recovery))
                    print(('matrix_total is:', matrix_total))
                    print((CheckIdentity(matrix_total)))
                    return(recovery_seq_1, recovery_seq_2, temp_pulse_seq_1, temp_pulse_seq_2)

        if (self.find_cheapest_recovery == True):
            recovery_seq_1 = []
            recovery_seq_2 = []
            temp_pulse_seq_1 = []
            temp_pulse_seq_2 = []
            temp_recov_len1 = [0]
            temp_recov_len2 = [0]
#            log.info('The index of the cheapest recovery clifford: %d'%(cheapest_index))
            self.add_twoQ_clifford(cheapest_index, recovery_seq_1, recovery_seq_2, temp_pulse_seq_1, temp_pulse_seq_2, temp_recov_len1, temp_recov_len2, generator = generator)


        if (recovery_seq_1 == [] and recovery_seq_2 == []):
            recovery_seq_1 = [None]
            recovery_seq_2 = [None]
            raise Exception ("failed to find recovery gate")
        
        print(('cheapest_index is:', cheapest_index))
        print(('cheapest matrix_recovery is:', matrix_recovery))
        print(('matrix_total is:', matrix_total))
        return (recovery_seq_1, recovery_seq_2, temp_pulse_seq_1, temp_pulse_seq_2)
    
    
    def add_singleQ_clifford(self, index, gate_seq, pulse_seq, length, qubit, pad_with_I=False, **kwargs):
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
        # Paulis
        if index == 0:
            gate_seq.append('I')
            pulse_seq.append(Delay(q_len))
            length[0] = length[0] + q_len
        elif index == 1:
            pulse_seq.append(r(np.pi, X_AXIS))
            gate_seq.append('Xp')
            length[0] = length[0] + q_len
        elif index == 2:
            pulse_seq.append(r(np.pi, Y_AXIS))
            gate_seq.append('Yp')
            length[0] = length[0] + q_len
        elif index == 3:
            pulse_seq.append(r(np.pi, Y_AXIS))
            pulse_seq.append(r(np.pi, X_AXIS))
            gate_seq.append('Yp')
            gate_seq.append('Xp')
            length[0] = length[0] + 2*q_len
    
        # 2pi/3 rotations
        elif index == 4:
            pulse_seq.append(r(np.pi/2, X_AXIS))
            pulse_seq.append(r(np.pi/2, Y_AXIS))
            gate_seq.append('X2p')
            gate_seq.append('Y2p')
            length[0] = length[0] + 2*q_len
        elif index == 5:
            pulse_seq.append(r(np.pi/2, X_AXIS))
            pulse_seq.append(r(-np.pi/2, Y_AXIS))
            gate_seq.append('X2p')
            gate_seq.append('Y2m')
            length[0] = length[0] + 2*q_len
        elif index == 6:
            pulse_seq.append(r(-np.pi/2, X_AXIS))
            pulse_seq.append(r(np.pi/2, Y_AXIS))
            gate_seq.append('X2m')
            gate_seq.append('Y2p')
            length[0] = length[0] + 2*q_len
        elif index == 7:
            pulse_seq.append(r(-np.pi/2, X_AXIS))
            pulse_seq.append(r(-np.pi/2, Y_AXIS))
            gate_seq.append('X2m')
            gate_seq.append('Y2m')
            length[0] = length[0] + 2*q_len
        elif index == 8:
            pulse_seq.append(r(np.pi/2, Y_AXIS))
            pulse_seq.append(r(np.pi/2, X_AXIS))
            gate_seq.append('Y2p')
            gate_seq.append('X2p')
            length[0] = length[0] + 2*q_len
        elif index == 9:
            pulse_seq.append(r(np.pi/2, Y_AXIS))
            pulse_seq.append(r(-np.pi/2, X_AXIS))
            gate_seq.append('Y2p')
            gate_seq.append('X2m')
            length[0] = length[0] + 2*q_len
        elif index == 10:
            pulse_seq.append(r(-np.pi/2, Y_AXIS))
            pulse_seq.append(r(np.pi/2, X_AXIS))
            gate_seq.append('Y2m')
            gate_seq.append('X2p')
            length[0] = length[0] + 2*q_len
        elif index == 11:
            pulse_seq.append(r(-np.pi/2, Y_AXIS))
            pulse_seq.append(r(-np.pi/2, X_AXIS))
            gate_seq.append('Y2m')
            gate_seq.append('X2m')
            length[0] = length[0] + 2*q_len
    
        # pi/2 rotations
        elif index == 12:
            pulse_seq.append(r(np.pi/2, X_AXIS))
            gate_seq.append('X2p')
            length[0] = length[0] + q_len
        elif index == 13:
            pulse_seq.append(r(-np.pi/2, X_AXIS))
            gate_seq.append('X2m')
            length[0] = length[0] + q_len
        elif index == 14:
            pulse_seq.append(r(np.pi/2, Y_AXIS))
            gate_seq.append('Y2p')
            length[0] = length[0] + q_len
        elif index == 15:
            pulse_seq.append(r(-np.pi/2, Y_AXIS))
            gate_seq.append('Y2m')
            length[0] = length[0] + q_len
        elif index == 16:
            pulse_seq.append(r(-np.pi/2, X_AXIS))
            pulse_seq.append(r(np.pi/2, Y_AXIS))
            pulse_seq.append(r(np.pi/2, X_AXIS))
            gate_seq.append('X2m')
            gate_seq.append('Y2p')
            gate_seq.append('X2p')
            length[0] = length[0] + 3*q_len
        elif index == 17:
            pulse_seq.append(r(-np.pi/2, X_AXIS))
            pulse_seq.append(r(-np.pi/2, Y_AXIS))
            pulse_seq.append(r(np.pi/2, X_AXIS))
            gate_seq.append('X2m')
            gate_seq.append('Y2m')
            gate_seq.append('X2p')
            length[0] = length[0] + 3*q_len
    
        # Hadamard-Like
        elif index == 18:
            pulse_seq.append(r(np.pi, X_AXIS))
            pulse_seq.append(r(np.pi/2, Y_AXIS))
            gate_seq.append('Xp')
            gate_seq.append('Y2p')
            length[0] = length[0] + 2*q_len
        elif index == 19:
            pulse_seq.append(r(np.pi, X_AXIS))
            pulse_seq.append(r(-np.pi/2, Y_AXIS))
            gate_seq.append('Xp')
            gate_seq.append('Y2m')
            length[0] = length[0] + 2*q_len
        elif index == 20:
            pulse_seq.append(r(np.pi, Y_AXIS))
            pulse_seq.append(r(np.pi/2, X_AXIS))
            gate_seq.append('Yp')
            gate_seq.append('X2p')
            length[0] = length[0] + 2*q_len
        elif index == 21:
            pulse_seq.append(r(np.pi, Y_AXIS))
            pulse_seq.append(r(-np.pi/2, X_AXIS))
            gate_seq.append('Yp')
            gate_seq.append('X2m')
            length[0] = length[0] + 2*q_len
        elif index == 22:
            pulse_seq.append(r(np.pi/2, X_AXIS))
            pulse_seq.append(r(np.pi/2, Y_AXIS))
            pulse_seq.append(r(np.pi/2, X_AXIS))
            gate_seq.append('X2p')
            gate_seq.append('Y2p')
            gate_seq.append('X2p')
            length[0] = length[0] + 3*q_len
        elif index == 23:
            pulse_seq.append(r(-np.pi/2, X_AXIS))
            pulse_seq.append(r(np.pi/2, Y_AXIS))
            pulse_seq.append(r(-np.pi/2, X_AXIS))
            gate_seq.append('X2m')
            gate_seq.append('Y2p')
            gate_seq.append('X2m')
            length[0] = length[0] + 3*q_len
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
    
    
    def add_twoQ_clifford(self, index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, generator = 'ZX90'):
        """Add single qubit clifford (11520 = 576 + 5184 + 5184 + 576)."""
        r = self.qubit_info.rotate
        r2 = self.qubit2_info.rotate
        
#        print(index)
#        print(type(index))
#        
        if (index < 0):
            raise ValueError(
                'index is out of range. it should be smaller than 11520 and '
                'greater or equal to 0: ', str(index))
        elif (index < 576):
            self.add_singleQ_based_twoQ_clifford(index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
        elif (index < 5184 + 576):
            self.add_CNOT_like_twoQ_clifford(index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, generator = generator)
        elif (index < 5184 + 5184 + 576):
            self.add_iSWAP_like_twoQ_clifford(index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, generator = generator)
        elif (index < 576 + 5184 + 5184 + 576):
            self.add_SWAP_like_twoQ_clifford(index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, generator = generator)
        else:
            raise ValueError(
                'index is out of range. it should be smaller than 11520 and '
                'greater or equal to 0: ', str(index))
#        print ('length of gate_seq_1 is', len(gate_seq_1))
#        print ('length of gate_seq_2 is', len(gate_seq_2))
        self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
#        print ('length of gate_seq_1 is', len(gate_seq_1))
#        print ('length of gate_seq_2 is', len(gate_seq_2))
   
        pass
    
    
    def add_singleQ_S1(self, index, gate_seq, pulse_seq, length, qubit):
        """Add single qubit clifford from S1.
    
        (I-like-subset of single qubit clifford group) (3)
        """
        if qubit == 1:
            r = self.qubit_info.rotate
            q_len = self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len
        elif qubit == 2:
            r = self.qubit2_info.rotate
            q_len = self.qubit2_info.chop*self.qubit2_info.w+self.qubit2_info.sq_len
            
        w = self.qubit_info.w
        sq_len = self.qubit_info.sq_len
        
        if index == 0:
            gate_seq.append('I')
#            gate_seq.append('I')  # auxiliary
#            gate_seq.append('I')  # auxiliary
            pulse_seq.append(Delay(q_len))
#            pulse_seq.append(Delay(q_len))
#            pulse_seq.append(Delay(q_len))
            length[0] = length[0] + q_len
        elif index == 1:
            gate_seq.append('Y2p')
            gate_seq.append('X2p')
#            gate_seq.append('I')  # auxiliary
            pulse_seq.append(r(np.pi/2, Y_AXIS))
            pulse_seq.append(r(np.pi/2, X_AXIS))
#            pulse_seq.append(Delay(q_len))
            length[0] = length[0] + 2*q_len
        elif index == 2:
            gate_seq.append('X2m')
            gate_seq.append('Y2m')
#            gate_seq.append('I')  # auxiliary
            pulse_seq.append(r(-np.pi/2, X_AXIS))
            pulse_seq.append(r(-np.pi/2, Y_AXIS))
#            pulse_seq.append(Delay(q_len))
            length[0] = length[0] + 2*q_len
    
    
    def add_singleQ_S1_X2p(self, index, gate_seq, pulse_seq, length, qubit):
        """Add single qubit clifford from S1_X2p.
    
        (X2p-like-subset of single qubit clifford group) (3)
        """
        if qubit == 1:
            r = self.qubit_info.rotate
            q_len = self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len
        elif qubit == 2:
            r = self.qubit2_info.rotate
            q_len = self.qubit2_info.chop*self.qubit2_info.w+self.qubit2_info.sq_len
            
        w = self.qubit_info.w
        sq_len = self.qubit_info.sq_len
        
        if index == 0:
            gate_seq.append('X2p')
#            gate_seq.append('I')
#            gate_seq.append('I')
            pulse_seq.append(r(np.pi/2, X_AXIS))
#            pulse_seq.append(Delay(q_len))  # auxiliary
#            pulse_seq.append(Delay(q_len))  # auxiliary
            length[0] = length[0] + q_len
        elif index == 1:
            gate_seq.append('X2p')
            gate_seq.append('Y2p')
            gate_seq.append('X2p')
            pulse_seq.append(r(np.pi/2, X_AXIS))
            pulse_seq.append(r(np.pi/2, Y_AXIS))
            pulse_seq.append(r(np.pi/2, X_AXIS))
            length[0] = length[0] + 3*q_len
        elif index == 2:
            gate_seq.append('Y2m')
#            gate_seq.append('I')
#            gate_seq.append('I')
            pulse_seq.append(r(-np.pi/2, Y_AXIS))
#            pulse_seq.append(Delay(q_len))  # auxiliary
#            pulse_seq.append(Delay(q_len))  # auxiliary
            length[0] = length[0] + q_len
    
    
    def add_singleQ_S1_Y2p(self,index, gate_seq, pulse_seq, length, qubit):
        """Add single qubit clifford from S1_Y2p.
    
        (Y2p-like-subset of single qubit clifford group) (3)
        """
        if qubit == 1:
            r = self.qubit_info.rotate
            q_len = self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len
        elif qubit == 2:
            r = self.qubit2_info.rotate
            q_len = self.qubit2_info.chop*self.qubit2_info.w+self.qubit2_info.sq_len
            
        w = self.qubit_info.w
        sq_len = self.qubit_info.sq_len
        
        if index == 0:
            gate_seq.append('Y2p')
#            gate_seq.append('I')
#            gate_seq.append('I')
            pulse_seq.append(r(np.pi/2, Y_AXIS))
#            pulse_seq.append(Delay(q_len))  # auxiliary
#            pulse_seq.append(Delay(q_len))  # auxiliary
            length[0] = length[0] + q_len
        elif index == 1:
            gate_seq.append('Yp')
            gate_seq.append('X2p')
#            gate_seq.append('I')
            pulse_seq.append(r(np.pi, Y_AXIS))
            pulse_seq.append(r(np.pi/2, X_AXIS))
#            pulse_seq.append(Delay(q_len))  # auxiliary
            length[0] = length[0] + 2*q_len
        elif index == 2:
            gate_seq.append('X2m')
            gate_seq.append('Y2m')
            gate_seq.append('X2p')
            pulse_seq.append(r(-np.pi/2, X_AXIS))
            pulse_seq.append(r(-np.pi/2, Y_AXIS))
            pulse_seq.append(r(np.pi/2, X_AXIS))
            length[0] = length[0] + 3*q_len
    
    def add_singleQ_S1_Z2p(self, index, gate_seq, pulse_seq, length, qubit):
        """Add single qubit clifford from S1_Z2p.
    
        (Z2p-like-subset of single qubit clifford group) (3)
        """
        if qubit == 1:
            r = self.qubit_info.rotate
            q_len = self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len
        elif qubit == 2:
            r = self.qubit2_info.rotate
            q_len = self.qubit2_info.chop*self.qubit2_info.w+self.qubit2_info.sq_len
            
        w = self.qubit_info.w
        sq_len = self.qubit_info.sq_len
        
        if index == 0:
            gate_seq.append('X2m')
            gate_seq.append('Y2m')
            gate_seq.append('X2p')
            pulse_seq.append(r(-np.pi/2, X_AXIS))
            pulse_seq.append(r(-np.pi/2, Y_AXIS))
            pulse_seq.append(r(np.pi/2, X_AXIS))
            length[0] = length[0] + 3*q_len
        elif index == 1:
            gate_seq.append('Y2p')
#            gate_seq.append('I')
#            gate_seq.append('I')
            pulse_seq.append(r(np.pi/2, Y_AXIS))
#            pulse_seq.append(Delay(q_len))  # auxiliary
#            pulse_seq.append(Delay(q_len))  # auxiliary
            length[0] = length[0] + q_len
        elif index == 2:
            gate_seq.append('X2m')
            gate_seq.append('Ypm')
#            gate_seq.append('I')
            pulse_seq.append(r(-np.pi/2, X_AXIS))
            pulse_seq.append(r(-np.pi, Y_AXIS))
#            pulse_seq.append(Delay(q_len))  # auxiliary
            length[0] = length[0] + 2*q_len
    
    def add_singleQ_based_twoQ_clifford(self,index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, **kwargs):
        """Add single-qubit-gates-only-based two Qubit Clifford.
    
        (24*24 = 576)
        (gate_seq_1: gate seq. of qubit #1, gate_seq_t: gate seq. of qubit #2)
        """
        r = self.qubit_info.rotate
        r2 = self.qubit2_info.rotate
#        print(index)
#        print(type(index))
        
        # randomly sample from single qubit cliffords (24)
        index_1 = index % 24
#        print(index_1)
#        print(type(index_1))
    
        # randomly sample from single qubit cliffords (24)
        index_2 = (index // 24) % 24
        self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
        self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
    
    
    def add_CNOT_like_twoQ_clifford(self, index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, generator='ZX90', **kwargs):
        """Add CNOT like two Qubit Clifford.
    
        (24*24*3*3 = 5184)
        (gate_seq_1: gate seq. of qubit #1, gate_seq_t: gate seq. of qubit #2)
        """
        r = self.qubit_info.rotate
        r2 = self.qubit2_info.rotate
        r3 = self.twoQ_info.rotate
        q_len1 = self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len
        q_len2 = self.qubit2_info.chop*self.qubit2_info.w+self.qubit2_info.sq_len
        twoQ_len = self.twoQ_info.chop*self.twoQ_info.w+self.twoQ_info.sq_len  #!!!
#        print(index)
#        print(type(index))
        
        # randomly sample from single qubit cliffords (24)
        index_1 = index % 24
#        print(index_1)
#        print(type(index_1))
    
        # randomly sample from single qubit cliffords (24)
        index_2 = (index // 24) % 24
    
        # randomly sample from S1 (3)
        index_3 = (index // 24 // 24) % 3
    
        # randomly sample from S1_Y2p (3) or S1_Z2p (3)
        index_4 = (index // 24 // 24 // 3) % 3
    
#        if generator == 'CZ':
#            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, 1)
#            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, 2)
#            gate_seq_1.append(Delay(4*w+sq_len))
#            gate_seq_2.append(gates.CZ)
#            self.add_singleQ_S1(index_3, gate_seq_1, pulse_seq_1, qubit=1)
#            self.add_singleQ_S1_Y2p(index_4, gate_seq_2, pulse_seq_2, qubit=2)
#    
#        elif generator == 'iSWAP':
#            self.add_singleQ_clifford(index_1, gate_seq_1, 1)
#            self.add_singleQ_clifford(index_2, gate_seq_2, 2)
#    
#            gate_seq_1.append(Delay(4*w+sq_len))
#            gate_seq_2.append(gates.iSWAP)
#    
#            gate_seq_1.append(r(np.pi/2, X_AXIS))
#            gate_seq_2.append(Delay(4*w+sq_len))
#    
#            gate_seq_1.append(Delay(4*w+sq_len))
#            gate_seq_2.append(gates.iSWAP)
#    
#            self.add_singleQ_S1(index_3, gate_seq_1, qubit=1)
#            self.add_singleQ_S1_Z2p(index_4, gate_seq_2, qubit=2)
            
        if generator == 'CNOT':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('CNOT')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(np.pi,X_AXIS))
            pulse_seq_2.append(r4(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            
            self.add_singleQ_S1(index_3, gate_seq_1, pulse_seq_1, length1, qubit=1)
            self.add_singleQ_S1(index_4, gate_seq_2, pulse_seq_2, length2, qubit=2)
#            
#        elif generator == 'ZX90':
#            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
#            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
#            
#            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
#                    
#            gate_seq_1.append('Ic')
#            gate_seq_2.append('ZX90')
#            pulse_seq_1.append(Delay(twoQ_len))
#            pulse_seq_2.append(r3(-np.pi,X_AXIS))
#            pulse_seq_2.append(r4(np.pi,X_AXIS))
#            length1[0] = length1[0] + twoQ_len
#            length2[0] = length2[0] + twoQ_len
#            
#            self.add_singleQ_S1(index_3, gate_seq_1, pulse_seq_1, length1, qubit=1)
#            self.add_singleQ_S1(index_4, gate_seq_2, pulse_seq_2, length2, qubit=2)
#
#
#ebru adding echo
        elif generator == 'ZX90':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('ZX90')

            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
            
            pulse_seq_1.append(r(np.pi,X_AXIS))
            pulse_seq_2.append(Delay(q_len1))
            
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(np.pi,X_AXIS))
            
            pulse_seq_1.append(r(-np.pi,X_AXIS))
            pulse_seq_2.append(Delay(q_len1))

            length1[0] = length1[0] + 2*twoQ_len+2*q_len1
            length2[0] = length2[0] + 2*twoQ_len+2*q_len1
            
            self.add_singleQ_S1(index_3, gate_seq_1, pulse_seq_1, length1, qubit=1)
            self.add_singleQ_S1(index_4, gate_seq_2, pulse_seq_2, length2, qubit=2)

            
        elif generator == 'CX':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('CX')
            pulse_seq_1.append(Delay(twoQ_len*2))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
#            pulse_seq_2.append(r4(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len*2
            length2[0] = length2[0] + twoQ_len*2
            
            self.add_singleQ_S1(index_3, gate_seq_1, pulse_seq_1, length1, qubit=1)
            self.add_singleQ_S1(index_4, gate_seq_2, pulse_seq_2, length2, qubit=2)
    
    
    def add_iSWAP_like_twoQ_clifford(self, index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, generator='ZX90', **kwargs):
        """Add iSWAP like two Qubit Clifford.
    
        (24*24*3*3 = 5184)
        (gate_seq_1: gate seq. of qubit #1, gate_seq_t: gate seq. of qubit #2)
        """
        r = self.qubit_info.rotate
        r2 = self.qubit2_info.rotate
        r3 = self.twoQ_info.rotate
        q_len1 = self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len
        q_len2 = self.qubit2_info.chop*self.qubit2_info.w+self.qubit2_info.sq_len
        twoQ_len = self.twoQ_info.chop*self.twoQ_info.w+self.twoQ_info.sq_len
#        print(index)
#        print(type(index))
            
        # randomly sample from single qubit cliffords (24)
        index_1 = index % 24
#        print(index_1)
#        print(type(index_1))
    
        # randomly sample from single qubit cliffords (24)
        index_2 = (index // 24) % 24
    
        # randomly sample from S1_Y2p (3) or S1 (3)
        index_3 = (index // 24 // 24) % 3
    
        # randomly sample from S1_X2p (3) or S1 (3)
        index_4 = (index // 24 // 24 // 3) % 3
    
    
    
#        if generator == 'CZ':
#            add_singleQ_clifford(index_1, gate_seq_1, qubit=1)
#            add_singleQ_clifford(index_2, gate_seq_2, qubit=2)
#            gate_seq_1.append(Delay(4*w+sq_len))
#            gate_seq_2.append(gates.CZ)
#            gate_seq_1.append(r(np.pi/2, Y_AXIS))
#            gate_seq_2.append(r2(-np.pi/2, X_AXIS))
#            gate_seq_1.append(Delay(4*w+sq_len))
#            gate_seq_2.append(gates.CZ)
#            add_singleQ_S1_Y2p(index_3, gate_seq_1, qubit=1)
#            add_singleQ_S1_X2p(index_4, gate_seq_2, qubit=2)
#    
#        elif generator == 'iSWAP':
#            add_singleQ_clifford(index_1, gate_seq_1, qubit=1)
#            add_singleQ_clifford(index_2, gate_seq_2, qubit=2)
#    
#            gate_seq_1.append(Delay(4*w+sq_len))
#            gate_seq_2.append(gates.iSWAP)
#    
#            add_singleQ_S1(index_3, gate_seq_1, qubit=1)
#            add_singleQ_S1(index_4, gate_seq_2, qubit=2)
            
        if generator == 'CNOT':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                        
            gate_seq_1.append('Ic')
            gate_seq_2.append('CNOT')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(np.pi,X_AXIS))
            pulse_seq_2.append(r4(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            
            gate_seq_1.append('X2m')
            gate_seq_2.append('Y2p')
            pulse_seq_1.append(r(-np.pi/2, X_AXIS))
            pulse_seq_2.append(r2(np.pi/2, Y_AXIS))
            length1[0] = length1[0] + q_len1
            length2[0] = length2[0] + q_len2
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)

            gate_seq_1.append('Ic')
            gate_seq_2.append('CNOT')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(np.pi,X_AXIS))
            pulse_seq_2.append(r4(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            
            self.add_singleQ_S1_X2p(index_3, gate_seq_1, pulse_seq_1, length1, qubit=1)
            self.add_singleQ_S1(index_4, gate_seq_2, pulse_seq_2, length2, qubit=2)
            
#        elif generator == 'ZX90':
#            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
#            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
#            
#            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
#                        
#            gate_seq_1.append('Ic')
#            gate_seq_2.append('ZX90')
#            pulse_seq_1.append(Delay(twoQ_len))
#            pulse_seq_2.append(r3(-np.pi,X_AXIS))
#            pulse_seq_2.append(r4(np.pi,X_AXIS))
#            length1[0] = length1[0] + twoQ_len
#            length2[0] = length2[0] + twoQ_len
#            
#            gate_seq_1.append('Y2m')
#            gate_seq_2.append('Y2m')
#            pulse_seq_1.append(r(-np.pi/2, Y_AXIS))
#            pulse_seq_2.append(r2(-np.pi/2, Y_AXIS))
#            length1[0] = length1[0] + q_len1
#            length2[0] = length2[0] + q_len2
#            
#            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
#
#            gate_seq_1.append('Ic')
#            gate_seq_2.append('ZX90')
#            pulse_seq_1.append(Delay(twoQ_len))
#            pulse_seq_2.append(r3(-np.pi,X_AXIS))
#            pulse_seq_2.append(r4(np.pi,X_AXIS))
#            length1[0] = length1[0] + twoQ_len
#            length2[0] = length2[0] + twoQ_len
#            
#            self.add_singleQ_S1(index_3, gate_seq_1, pulse_seq_1, length1, qubit=1)
#            self.add_singleQ_S1(index_4, gate_seq_2, pulse_seq_2, length2, qubit=2)

#ebru adding echo   #CHANGEHERE
        elif generator == 'ZX90':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                        
                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('ZX90')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))         

            pulse_seq_1.append(r(np.pi,X_AXIS))
            pulse_seq_2.append(Delay(q_len1))
            
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(np.pi,X_AXIS))
            
            pulse_seq_1.append(r(-np.pi,X_AXIS))
            pulse_seq_2.append(Delay(q_len1))

            length1[0] = length1[0] + 2*twoQ_len+2*q_len1
            length2[0] = length2[0] + 2*twoQ_len+2*q_len1

            gate_seq_1.append('Y2m')
            gate_seq_2.append('Y2m')
            pulse_seq_1.append(r(-np.pi/2, Y_AXIS))
            pulse_seq_2.append(r2(-np.pi/2, Y_AXIS))
            length1[0] = length1[0] + q_len1
            length2[0] = length2[0] + q_len2
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)

                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('ZX90')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
            
#            gate_seq_1.append('Xp')
#            gate_seq_2.append('Ip')
            pulse_seq_1.append(r(np.pi,X_AXIS))
            pulse_seq_2.append(Delay(q_len1))
            
#            gate_seq_1.append('Ic')
#            gate_seq_2.append('ZX90')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(np.pi,X_AXIS))
            
#            gate_seq_1.append('Xp')
#            gate_seq_2.append('Ip')
            pulse_seq_1.append(r(-np.pi,X_AXIS))
            pulse_seq_2.append(Delay(q_len1))


            length1[0] = length1[0] + 2*twoQ_len+2*q_len1
            length2[0] = length2[0] + 2*twoQ_len+2*q_len1
            
            self.add_singleQ_S1(index_3, gate_seq_1, pulse_seq_1, length1, qubit=1)
            self.add_singleQ_S1(index_4, gate_seq_2, pulse_seq_2, length2, qubit=2)



            
        elif generator == 'CX':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                        
            gate_seq_1.append('Ic')
            gate_seq_2.append('CX')
            pulse_seq_1.append(Delay(twoQ_len*2))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
#            pulse_seq_2.append(r4(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            
            gate_seq_1.append('Y2m')
            gate_seq_2.append('Y2m')
            pulse_seq_1.append(r(-np.pi/2, Y_AXIS))
            pulse_seq_2.append(r2(-np.pi/2, Y_AXIS))
            length1[0] = length1[0] + q_len1
            length2[0] = length2[0] + q_len2
            
            gate_seq_1.append('I')
            gate_seq_2.append('X2m')
            pulse_seq_1.append(Delay(q_len2))
            pulse_seq_2.append(r2(-np.pi/2, X_AXIS))
            length1[0] = length1[0] + q_len2
            length2[0] = length2[0] + q_len2
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)

            gate_seq_1.append('Ic')
            gate_seq_2.append('CX')
            pulse_seq_1.append(Delay(twoQ_len*2))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
#            pulse_seq_2.append(r4(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len*2
            length2[0] = length2[0] + twoQ_len*2
            
            self.add_singleQ_S1(index_3, gate_seq_1, pulse_seq_1, length1, qubit=1)
            self.add_singleQ_S1(index_4, gate_seq_2, pulse_seq_2, length2, qubit=2)
    
    
    def add_SWAP_like_twoQ_clifford(self, index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, generator='ZX90', **kwargs):
        """Add SWAP like two Qubit Clifford.
    
        (24*24*= 576)
        (gate_seq_1: gate seq. of qubit #1, gate_seq_t: gate seq. of qubit #2)
        """
        r = self.qubit_info.rotate
        r2 = self.qubit2_info.rotate
        r3 = self.twoQ_info.rotate
        q_len1 = self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len
        q_len2 = self.qubit2_info.chop*self.qubit2_info.w+self.qubit2_info.sq_len
        twoQ_len =self.twoQ_info.chop*self.twoQ_info.w+self.twoQ_info.sq_len# +  self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len

#        print(index)
#        print(type(index))
        
        # randomly sample from single qubit cliffords (24)
        index_1 = index % 24
#        print(index_1)
#        print(type(index_1))
    
        # randomly sample from single qubit cliffords (24)
        index_2 = (index // 24) % 24
    
#        if generator == 'CZ':
#            add_singleQ_clifford(index_1, gate_seq_1, qubit=1)
#            add_singleQ_clifford(index_2, gate_seq_2, qubit=2)
#            gate_seq_1.append(Delay(4*w+sq_len))
#            gate_seq_2.append(gates.CZ)
#            gate_seq_1.append(r(-np.pi/2, Y_AXIS))
#            gate_seq_2.append(r2(np.pi/2, Y_AXIS))
#            gate_seq_1.append(Delay(4*w+sq_len))
#            gate_seq_2.append(gates.CZ)
#            gate_seq_1.append(r(np.pi/2, Y_AXIS))
#            gate_seq_2.append(r2(-np.pi/2, Y_AXIS))
#            gate_seq_1.append(Delay(4*w+sq_len))
#            gate_seq_2.append(gates.CZ)
#            gate_seq_1.append(Delay(4*w+sq_len))
#            gate_seq_2.append(r2(np.pi/2, Y_AXIS))
#    
#        elif generator == 'iSWAP':
#            add_singleQ_clifford(index_1, gate_seq_1, qubit=1)
#            add_singleQ_clifford(index_2, gate_seq_2, qubit=2)
#    
#            gate_seq_1.append(Delay(4*w+sq_len))
#            gate_seq_2.append(gates.iSWAP)
#    
#            gate_seq_1.append(Delay(4*w+sq_len))
#            gate_seq_2.append(r2(-np.pi/2, X_AXIS))
#    
#            gate_seq_1.append(Delay(4*w+sq_len))
#            gate_seq_2.append(gates.iSWAP)
#    
#            gate_seq_1.append(r(-np.pi/2, X_AXIS))
#            gate_seq_2.append(Delay(4*w+sq_len))
#    
#            gate_seq_1.append(Delay(4*w+sq_len))
#            gate_seq_2.append(gates.iSWAP)
#    
#            gate_seq_1.append(Delay(4*w+sq_len))
#            gate_seq_2.append(r2(-np.pi/2, X_AXIS))
            
        if generator == 'CNOT':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
            
            gate_seq_1.append('Ic')
            gate_seq_2.append('CNOT')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(np.pi,X_AXIS))
            pulse_seq_2.append(r4(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len

            gate_seq_1.append('Xp')
            gate_seq_1.append('Y2p')
            pulse_seq_1.append(r(np.pi, X_AXIS))
            pulse_seq_1.append(r(np.pi/2, Y_AXIS))
            gate_seq_2.append('Xp')
            gate_seq_2.append('Y2p')
            pulse_seq_2.append(r2(np.pi, X_AXIS))
            pulse_seq_2.append(r2(np.pi/2, Y_AXIS))
            length1[0] = length1[0] + 2*q_len1
            length2[0] = length2[0] + 2*q_len2
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)

            gate_seq_1.append('Ic')
            gate_seq_2.append('CNOT')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(np.pi,X_AXIS))
            pulse_seq_2.append(r4(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            
            gate_seq_1.append('Xp')
            gate_seq_1.append('Y2p')
            pulse_seq_1.append(r(np.pi, X_AXIS))
            pulse_seq_1.append(r(np.pi/2, Y_AXIS))
            gate_seq_2.append('Xp')
            gate_seq_2.append('Y2p')
            pulse_seq_2.append(r2(np.pi, X_AXIS))
            pulse_seq_2.append(r2(np.pi/2, Y_AXIS))
            length1[0] = length1[0] + 2*q_len1
            length2[0] = length2[0] + 2*q_len2
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)

            gate_seq_1.append('Ic')
            gate_seq_2.append('CNOT')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(np.pi,X_AXIS))
            pulse_seq_2.append(r4(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            
#        elif generator == 'ZX90':
#            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
#            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
#            
#            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
#            
#            gate_seq_1.append('Ic')
#            gate_seq_2.append('ZX90')
#            pulse_seq_1.append(Delay(twoQ_len))
#            pulse_seq_2.append(r3(-np.pi,X_AXIS))
#            pulse_seq_2.append(r4(np.pi,X_AXIS))
#            length1[0] = length1[0] + twoQ_len
#            length2[0] = length2[0] + twoQ_len
#
#            gate_seq_1.append('Y2m')
#            gate_seq_2.append('Y2m')
#            pulse_seq_1.append(r(-np.pi/2, Y_AXIS))
#            pulse_seq_2.append(r2(-np.pi/2, Y_AXIS))
#            length1[0] = length1[0] + q_len1
#            length2[0] = length2[0] + q_len2
#            
#            gate_seq_1.append('I')
#            gate_seq_2.append('X2m')
#            pulse_seq_1.append(Delay(q_len2))
#            pulse_seq_2.append(r2(-np.pi/2, X_AXIS))
#            length1[0] = length1[0] + q_len2
#            length2[0] = length2[0] + q_len2
#            
#            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
#
#            gate_seq_1.append('Ic')
#            gate_seq_2.append('ZX90')
#            pulse_seq_1.append(Delay(twoQ_len))
#            pulse_seq_2.append(r3(-np.pi,X_AXIS))
#            pulse_seq_2.append(r4(np.pi,X_AXIS))
#            length1[0] = length1[0] + twoQ_len
#            length2[0] = length2[0] + twoQ_len
#            
#            gate_seq_1.append('X2p')
#            gate_seq_2.append('X2p')
#            pulse_seq_1.append(r(np.pi/2, X_AXIS))
#            pulse_seq_2.append(r2(np.pi/2, X_AXIS))
#            length1[0] = length1[0] + q_len1
#            length2[0] = length2[0] + q_len2
#            
#            gate_seq_1.append('I')
#            gate_seq_2.append('Y2m')
#            pulse_seq_1.append(Delay(q_len2))
#            pulse_seq_2.append(r2(-np.pi/2, Y_AXIS))
#            length1[0] = length1[0] + q_len2
#            length2[0] = length2[0] + q_len2
#            
#            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
#
#            gate_seq_1.append('Ic')
#            gate_seq_2.append('ZX90')
#            pulse_seq_1.append(Delay(twoQ_len))
#            pulse_seq_2.append(r3(-np.pi,X_AXIS))
#            pulse_seq_2.append(r4(np.pi,X_AXIS))
#            length1[0] = length1[0] + twoQ_len
#            length2[0] = length2[0] + twoQ_len
 
#ebru adding echo            
        elif generator == 'ZX90':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
            
                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('ZX90')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))

            pulse_seq_1.append(r(np.pi,X_AXIS))
            pulse_seq_2.append(Delay(q_len1))
            
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(np.pi,X_AXIS))
            
            pulse_seq_1.append(r(-np.pi,X_AXIS))
            pulse_seq_2.append(Delay(q_len1))

            length1[0] = length1[0] + 2*twoQ_len+2*q_len1
            length2[0] = length2[0] + 2*twoQ_len+2*q_len1


            gate_seq_1.append('Y2m')
            gate_seq_2.append('Y2m')
            pulse_seq_1.append(r(-np.pi/2, Y_AXIS))
            pulse_seq_2.append(r2(-np.pi/2, Y_AXIS))
            length1[0] = length1[0] + q_len1
            length2[0] = length2[0] + q_len2
            
            gate_seq_1.append('I')
            gate_seq_2.append('X2m')
            pulse_seq_1.append(Delay(q_len2))
            pulse_seq_2.append(r2(-np.pi/2, X_AXIS))
            length1[0] = length1[0] + q_len2
            length2[0] = length2[0] + q_len2
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)

                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('ZX90')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
            
            pulse_seq_1.append(r(np.pi,X_AXIS))
            pulse_seq_2.append(Delay(q_len1))
            
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(np.pi,X_AXIS))
            
            pulse_seq_1.append(r(-np.pi,X_AXIS))
            pulse_seq_2.append(Delay(q_len1))

            length1[0] = length1[0] + 2*twoQ_len+2*q_len1
            length2[0] = length2[0] + 2*twoQ_len+2*q_len1


            gate_seq_1.append('X2p')
            gate_seq_2.append('X2p')
            pulse_seq_1.append(r(np.pi/2, X_AXIS))
            pulse_seq_2.append(r2(np.pi/2, X_AXIS))
            length1[0] = length1[0] + q_len1
            length2[0] = length2[0] + q_len2
            
            gate_seq_1.append('I')
            gate_seq_2.append('Y2m')
            pulse_seq_1.append(Delay(q_len2))
            pulse_seq_2.append(r2(-np.pi/2, Y_AXIS))
            length1[0] = length1[0] + q_len2
            length2[0] = length2[0] + q_len2
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)

                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('ZX90')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
            
            pulse_seq_1.append(r(np.pi,X_AXIS))
            pulse_seq_2.append(Delay(q_len1))
            
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(np.pi,X_AXIS))
            
            pulse_seq_1.append(r(-np.pi,X_AXIS))
            pulse_seq_2.append(Delay(q_len1))

            length1[0] = length1[0] + 2*twoQ_len+2*q_len1
            length2[0] = length2[0] + 2*twoQ_len+2*q_len1


           
        elif generator == 'CX':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
            
            gate_seq_1.append('Ic')
            gate_seq_2.append('CX')
            pulse_seq_1.append(Delay(twoQ_len*2))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
#            pulse_seq_2.append(r4(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len*2
            length2[0] = length2[0] + twoQ_len*2

            gate_seq_1.append('Y2m')
            gate_seq_2.append('Y2m')
            pulse_seq_1.append(r(-np.pi/2, Y_AXIS))
            pulse_seq_2.append(r2(-np.pi/2, Y_AXIS))
            length1[0] = length1[0] + q_len1
            length2[0] = length2[0] + q_len2
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)

            gate_seq_1.append('Ic')
            gate_seq_2.append('CX')
            pulse_seq_1.append(Delay(twoQ_len*2))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
#            pulse_seq_2.append(r4(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len*2
            length2[0] = length2[0] + twoQ_len*2
            
            gate_seq_1.append('X2p')
            gate_seq_2.append('X2p')
            pulse_seq_1.append(r(np.pi/2, X_AXIS))
            pulse_seq_2.append(r2(np.pi/2, X_AXIS))
            length1[0] = length1[0] + q_len1
            length2[0] = length2[0] + q_len2
            
            gate_seq_1.append('I')
            gate_seq_2.append('Y2m')
            pulse_seq_1.append(Delay(q_len2))
            pulse_seq_2.append(r2(-np.pi/2, Y_AXIS))
            length1[0] = length1[0] + q_len2
            length2[0] = length2[0] + q_len2
            
            gate_seq_1.append('I')
            gate_seq_2.append('X2m')
            pulse_seq_1.append(Delay(q_len2))
            pulse_seq_2.append(r2(-np.pi/2, X_AXIS))
            length1[0] = length1[0] + q_len2
            length2[0] = length2[0] + q_len2
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)

            gate_seq_1.append('Ic')
            gate_seq_2.append('CX')
            pulse_seq_1.append(Delay(twoQ_len*2))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
            pulse_seq_2.append(r3(-np.pi,X_AXIS))
#            pulse_seq_2.append(r4(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len*2
            length2[0] = length2[0] + twoQ_len*2
            

    def analyze(self, data=None, fig=None):
        self.Pg_cplx = analysis(self, data, fig)
        return self.Pg_cplx