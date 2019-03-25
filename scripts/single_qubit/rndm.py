import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import math
import random 
#import lmfit

#This is an alternative RB code using a dictionary - not well tested

''' Maps from one bloch sphere point to another through rotations A1-A4,B1-B7'''
''' A1: X(pi/2), ....''' 
R_TABLE=np.matrix([[1,5,2,0,4,3],
                   [3,0,2,5,4,1],
                   [2,1,5,3,0,4],
                   [4,1,0,3,5,2],
                   [5,3,2,1,4,0],
                   [5,3,2,1,4,0],
                   [5,1,4,3,2,0],
                   [5,1,4,3,2,0],
                   [0,3,4,1,2,5],
                   [0,3,4,1,2,5],
                   [0,1,2,3,4,5]])

''' Maps form bloch sphere point to correct return rotation '''
X_TABLE = np.array(['B7', 'A2', 'A4', 'A1', 'A3', 'B3'])

''' number of differnet A and B roations '''
A_ROT_NUM = 4
B_ROT_NUM = 7


def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.xs
    ''' TODO: copy code for RBplotcode.py or whatever and add functionality '''

''' Generate pi/2 rotations '''
def a_rotations(n_gates):
    A = []#np.array(n_gates, dtype = str)
    for i in range(n_gates):
        A.append('A' + str(random.randint(1,A_ROT_NUM)))
    return A
    
''' Generate pi and I rotations '''
def b_rotations(n_gates):
    B = []#np.array(n_gates, dtype = str)
    for i in range(n_gates):
        B.append('B' + str(random.randint(1,B_ROT_NUM)))
    return B
    
''' Calculate return rotations '''
def x_rotations(a_list, b_list):
    x_list = np.array(len(a_list), dtype = str)
    current_position = 0
    for n in range(len(a_list)):
        current_position = update_position(current_position, a_list[n], b_list[n])
        x_list[n] = X_TABLE[current_position]
    return x_list

''' Finds new postion on bloch sphere using new current postition and a gate '''
''' TODO: write this function by actually calculating qubit rotations, not shitty matricies '''
def update_position(current_position, a, b):
    current_position = R_TABLE[int(a[1])-1, current_position] # do the A rotation
    current_position = R_TABLE[int(b[1])-1, current_position] # do the B rotation
    return current_position

                               


class rndm(Measurement1D):
    
    def __init__(self, qubit_info, min_gates, max_gates, gate_step, seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.build_dict()
        if seq is None:
            seq = Trigger(250)
        self.xs = np.array(range(min_gates, max_gates+1, gate_step))
        
        self.start = min_gates
        self.stop = max_gates
        self.step = gate_step
        self.n_measurements = (max_gates-min_gates)/gate_step+1
        self.seq = seq
        self.postseq = postseq

        super(rndm, self).__init__(self.n_measurements, infos=(qubit_info,), **kwargs)
        self.data.create_dataset('number_of_gates', data=np.linspace(1, self.n_measurements, self.n_measurements))
#        self.data.set_attrs()


    def generate(self):
        s = Sequence()
        
        a_list = a_rotations(self.stop)
        b_list = b_rotations(self.stop)
        x_list = x_rotations(a_list, b_list)
        print a_list, b_list, x_list
        
        for n in range(self.start, self.stop+1, self.step):
            s.append(self.seq)
            
            for i in range(n+1):
                for gate_seq in self.SEQ_DICT[a_list[i]]:
                    s.append(gate_seq)
                    s.append(Delay(40))
                for gate_seq in self.SEQ_DICT[b_list[i]]:
                    s.append(gate_seq)
                    s.append(Delay(40))
                
            s.append(self.SEQ_DICT[x_list[n]])
            s.append(Delay(40))
#            if self.postseq is not None:
#                s.append(self.postseq)
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            
        s = self.get_sequencer(s)
        seqs = s.render()

        return seqs

    ''' Dictionary that maps rotation names onto actual qubit rotations '''
    ''' NOTE: self.qubit_info must me setup '''
    def build_dict(self): #, seq_name): deleted chen
        self.SEQ_DICT ={'A1' : [self.qubit_info.rotate(np.pi/2, X_AXIS)],    # X(pi/2)
                        'A2' : [self.qubit_info.rotate(-np.pi/2, X_AXIS)],
                        'A3' : [self.qubit_info.rotate(np.pi/2, Y_AXIS)],
                        'A4' : [self.qubit_info.rotate(-np.pi/2, Y_AXIS)],
                        'B1' : [self.qubit_info.rotate(np.pi, X_AXIS)],
                        'B2' : [self.qubit_info.rotate(-np.pi, X_AXIS)],
                        'B3' : [self.qubit_info.rotate(np.pi, Y_AXIS)],
                        'B4' : [self.qubit_info.rotate(-np.pi, Y_AXIS)],
                        'B5' : [self.qubit_info.rotate(np.pi, X_AXIS), self.qubit_info.rotate(np.pi, Y_AXIS)],
                        'B6' : [self.qubit_info.rotate(np.pi, X_AXIS), self.qubit_info.rotate(np.pi, Y_AXIS)],
                        'B7' : [Delay(40)]}
        
    def analyze(self, data=None, fig=None):
        
        ''' TODO: copy code for RBplotcode.py or whatever and add functionality '''

        return #self.fit_params['tau'].value
