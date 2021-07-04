


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
import mclient

ZZ_gate = mclient.instruments['ZZ_gate']


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
    result = lmfit.minimize(exp_decay, params, args=(xs, ys))
    lmfit.report_fit(result.params)
    
    fig.axes[0].plot(xs, -exp_decay(result.params, xs, 0), label='Fit, alpha = %.03f us +/- %.03f us '%(result.params['alpha'].value, result.params['alpha'].stderr))
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


#the original part    
#    Pg1 = ((-rd-gr+bl+yw)/(Veg-Vgg+Vee-Vge)+1)/2
#    Pg2 = ((-rd-bl+gr+yw)/(Vge-Vgg+Vee-Veg)+1)/2
#
#    Pegge = ((rd+yw-bl-gr)/(Vge+Veg-Vee-Vgg)+1)/2
#    Pgg = (Pg1+Pg2-Pegge)/2
#    Pg_cplx = (Pg1+Pg2-Pegge)/2
#
#    
#    fig2, axes2 = plt.subplots(2)
#    axes2[0].plot(xs[12:], np.real(Pgg))
#    axes2[0].plot(xs[12:], np.real(Pg1*Pg2), color='r')
#    axes2[1].plot(xs[12:], np.imag(Pgg))
#    
#    return [Pgg, Pg1, Pg2, Pg_cplx]
# end of the original part




    
    Pg1 = ((-rd-gr+bl+yw)/(Veg-Vgg+Vee-Vge)+1)/2
    Pg2 = ((-rd-bl+gr+yw)/(Vge-Vgg+Vee-Veg)+1)/2

    V_matrix = np.matrix([[Vgg, Vge, Veg, Vee], [Vge, Vgg, Veg, Vee], 
                          [Veg, Vee, Vgg, Vge], [Vee, Veg, Vge, Vgg]])
    y_vector = [rd, gr, bl, yw]
    P = np.dot(np.linalg.inv(V_matrix), y_vector)
    Pgg = np.transpose(P[0])

#    Igg = 1
#    Ige = 0.0
#    Ieg = 0.0
#    Iee = 0.0

#    Igg = 0.8
#    Ige = 0.05
#    Ieg = 0.15
#    Iee = 0.00
#    
#    I_matrix = np.matrix([[Igg, Ige, Ieg, Iee], [Ige, Igg, Iee, Ieg], 
#                          [Ieg, Iee, Igg, Ige], [Iee, Ieg, Ige, Igg]])
#    
#    P_correct = np.dot(I_matrix, P)
#
#    Pgg = np.transpose(P_correct[0])
#    Pgg= Pgg.A1
#    Pgg1 = Pgg.reshape(len(param_range),N_sequences)
#    Pgg1 = np.mean(Pgg1, axis=1)
#    print(Pgg1)
#
#    
#    fig2, axes2 = plt.subplots(2)
#    axes2[0].plot(param_range, np.real(Pgg1))
#    axes2[0].plot(xs[12:], np.real(Pg1*Pg2), color='r')
#    axes2[1].plot(xs[12:], np.imag(Pgg))
#    plt.close('all')    
    return [Pgg, Pg1, Pg2]


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

        
    

class TwoQubit_RB(Measurement1D):
    """Two qubit randomized benchmarking."""

    filepath_lookup_table = ""

    def __init__(self,  qubit_info, qubit2_info, twoQ_info, cancel_info, sweep_param, param_range, num_cal_points,   N_sequences, generator='CZ', seq=None, postseq=None, num_gates=0, category='all', cnum=None,
                 find_cheapest_recovery=False, interleave=None, use_virtual_Z=False, virtual_recovery=False, use_lookup_table=False,
                 singleQ_phases=[0,0], **kwargs):
        self.sweep_param = sweep_param
        self.param_range = param_range
        self.qubit_info = qubit_info
        self.qubit2_info = qubit2_info
        self.twoQ_info = twoQ_info
        self.cancel_info = cancel_info
        self.N_sequences = N_sequences  #number of random sequences 
        self.num_cal_points = num_cal_points
        XS = np.asarray(list(range(len(self.param_range)*N_sequences+4*self.num_cal_points))) - (4*self.num_cal_points-1)
        self.xs = np.array([XS,XS,XS,XS]).transpose().flatten() # for plotting purposes
        self.filepath_lookup_table = ""
        self.cnum=cnum
        self.interleave = interleave
        self.use_virtual_Z = use_virtual_Z
        self.virtual_recovery = virtual_recovery
        self.singleQ_phases = singleQ_phases
        self.use_lookup_table = use_lookup_table
        
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.generator = generator
        self.category = category
        self.find_cheapest_recovery = find_cheapest_recovery
        self.num_gates = num_gates
        
            
        super(TwoQubit_RB, self).__init__(4*(1*N_sequences+4*num_cal_points), infos=(qubit_info,qubit2_info,twoQ_info,cancel_info), **kwargs)
        self.data.create_dataset('Cliffords', data=list(range(4*(1*N_sequences+4*num_cal_points))))
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



        rndnum=np.zeros(self.N_sequences)
        recov_index=np.zeros(self.N_sequences)
#       
#        #N=1 Clifford    #the numbers below are for 10 random sequences only for the moment
#        rndnum = [6971,6036,2004,2164,1938,5441,10509,1979,1048,1442,271,11233]
#        recov_index = [9279,9316,4776,4414,4130,5448,10945,4799,5965,7732,2859,7017]
#
        rndnum=[6562]
        recov_index=[7063]
#
        #N=3 
#        rndnum = [10584.0,4715.0, 11442.0, 4502.0, 1638.0, 6365.0, 5815.0, 8332.0, 811.0,7524.0, 7012.0, 6642.0]
#        recov_index = [11311.0,6069.0,7414.0,7542.0,6418.0,7532.0, 1967.0, 4728.0, 47.0, 3388.0, 7446.0, 4213.0]    
#        


#        
        
#        #N=5
#        rndnum = [1562.0, 2189.0, 9314.0, 3237.0, 8847.0, 10425.0, 3711.0, 4412.0, 5001.0, 2947.0, 7727.0, 559.0]
#        recov_index = [3197.0, 4236.0, 4761.0, 7994.0, 7051.0, 4223.0, 2890.0, 216.0, 4226.0, 9046.0, 4334.0, 3027.0]        
#        
        
#        #N=7
#        rndnum = [7357.0, 321.0, 4370.0, 10632.0, 3770.0, 5260.0, 9787.0, 1250.0, 10254.0, 1180.0, 2888.0, 9484.0]
#        recov_index = [8476.0, 5041.0, 77.0, 3133.0, 6977.0, 6879.0, 6232.0, 3525.0, 9735.0, 4584.0, 3271.0, 4867.0]    
#
        
#        rndm =[]
#        recov =[]
#        for i in range(12):
#            rndm.append(rndnum[i][6])
#            recov.append(recov_index[i][6])
#
#

#    rndnum=np.zeros((30,8))
#    recov_index=np.zeros((30,8))
#    
#    rndnum[0] = [6971,1550,10584,1613,1562,6911,7357,2831]
#    recov_index[0] = [9279,268,11311,5531,3197,9409,8476,10775]    
#    rndnum[1]= [6036,8636,4715,6858,2189,8847,321,7811]
#    recov_index[1] = [9316,11127,6069,7468,4236,1244,5041,3588]    
#    rndnum[2] = [2004,1724,11442,6908,9314,1799,4370,9999]
#    recov_index[2] = [4776,1986,7414,9499,4761,4133,77,2577]    
#    rndnum[3] = [2164,10040,4502,2420,3237,1143,10632,1410]
#    recov_index[3] = [4414,7210,7542,9941,7994,10314,3133,814]        
#    rndnum[4] = [1938,2620,1638,11348,8847,3942,3770,6094]
#    recov_index[4] = [4130,9594,6418,1318,7051,7174,6977,477]    
#    rndnum[5] = [5441,3523,6365,10292,10425,6631,5260,8453]
#    recov_index[5] = [5448,5539,7532,6204,4223,10620,6879,2150]    
#    rndnum[6] = [10509,8755,5815,5653,3711,11321,9787,3124]
#    recov_index[6] = [10945,746,1967,3380,2890,9683,6232,3666]    
#    rndnum[7] = [1979,9256,8332,4828,4412,3369,1250,2614]
#    recov_index[7] = [4799,3771,4728,1286,216,7271,3525,6507]    
#    rndnum[8] = [1048,1134,811,9111,5001,9350,10254,4129]
#    recov_index[8] = [5965,8551,47,10019,4226,4909,9735,5695]      
#    rndnum[9] = [1442,1829,7524,10034,2947,647,1180,8955]
#    recov_index[9] = [7732,4845,3388,2822,9046,5189,4584,11306]    
#    rndnum[10] = [271,5838,7012,978,7727,6775,2888,1364]
#    recov_index[10] = [2859,10361,7446,723,4334,5540,3271,11151]   
#    rndnum[11] = [11233,11258,6642,6180,559,2017,9484,9667]
#    recov_index[11] = [7017,1159,4213,1503,3027,405,4867,9526]    
#    rndnum[12] = [5714,1839,11219,1633,11442,8105,3509,10395]
#    recov_index[12] = [5686,931,3946,3142,4386,9841,10184,3213]    
#    rndnum[13] = [11190,3133,10467,10303,8426,6538,6569,2225]
#    recov_index[13] = [5874,10322,3302,7032,4291,3377,3929,137]    
#    rndnum[14] = [2339,3172,943,5730,10827,10282,9430,7067]
#    recov_index[14] = [9228,8202,17,1457,8141,9794,9314,18]   
#    rndnum[15] = [10730,8625,1026,3133,1426,2548,9210,375]
#    recov_index[15] = [11364,6185,3920,6022,8762,7655,10313,4475]   
#    rndnum[16] = [5833,1646,8533,1070,6212,2909,8409,9856]
#    recov_index[16] = [6053,7261,4586,5685,4171,1782,7514,7487]    
#    rndnum[17] = [11501,7466,1374,1583,5861,7027,1626,3036]
#    recov_index[17] = [9370,8190,86,10013,312,10257,2105,1601]    
#    rndnum[18] = [9638,3400,947,3337,4350,3879,71,11250]
#    recov_index[18] = [3115,953,3673,6736,10423,10409,2789,5884]    
#    rndnum[19] = [7822,2929,7157,3166,11129,4587,10821,9220]
#    recov_index[19] = [5526,10400,4286,5327,9148,10680,3488,9777]    
#    rndnum[20] = [8915,5951,8677,4975,10347,5130,3061,9752]
#    recov_index[20] = [8319,4885,11352,6650,9837,6491,3284,7343]    
#    rndnum[21] = [5324,4065,4538,11509,3612,2185,10845,4446]
#    recov_index[21] = [4875,1260,10650,7871,7546,6992,5368,9586]    
#    rndnum[22] = [1785,4439,10587,3483,6556,563,3339,6651]
#    recov_index[22] = [742,10245,2971,3422,8684,732,5067,6216]   
#    rndnum[23] = [9240,534,9512,5246,6625,4313,4952,1838]
#    recov_index[23] = [1663,4894,7771,4653,2216,140,4098,2619]   
#    rndnum[24] = [6942,383,10940,2956,7834,2028,8105,6095]
#    recov_index[24] = [8654,9783,2664,3581,7540,8179,11501,5725]    
#    rndnum[25] = [7542,11454,7437,3968,6394,8437,5829,10684]
#    recov_index[25] = [710,10958,1102,974,3142,10669,548,11138]   
#    rndnum[26] = [6301,3919,8024,2772,11501,6915,4087,10655]
#    recov_index[26] = [5897,5772,7904,1542,7938,4175,3813,1346]   
#    rndnum[27] = [9875,9562,1726,1633,6235,9834,7796,9446]
#    recov_index[27] = [4244,9958,1831,11463,5268,133,3810,10097]    
#    rndnum[28] = [7951,3205,3189,1260,10593,8796,11344,7229]
#    recov_index[28] = [4387,7507,6763,9687,2343,9931,1784,9896]    
#    rndnum[29] = [5833,8028,5650,11467,6495,4693,970,8477]
#    recov_index[29] = [6053,10676,2383,5924,7325,2745,3549,4794]
#    
#    
#    
#    
#    
#    
#    

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
        phi1 = [0]
        phi2 = [0]

        for x in self.param_range:
            if self.sweep_param == 'Drag':
                drag = x
                amp = self.twoQ_info.pi_amp

            elif self.sweep_param == 'Pi_amp':
                amp  = x 
                drag = self.twoQ_info.drag

            for n in range(self.N_sequences):
               temp_pulseSeq1 = []
               temp_pulseSeq2 = []
               self.add_twoQ_clifford(rndnum[n], cliffordSeq1, cliffordSeq2, temp_pulseSeq1, temp_pulseSeq2, len1, len2, phi1, phi2, amp, drag, virtualZ=self.use_virtual_Z,  generator = self.generator)
               print((phi1[0], phi2[0]))
               if self.interleave == 'ZX90':
                   print ('This code does not support ZX90 yet')
                   
               elif self.interleave == 'I':
                   cliffordSeq1.append('I')
                   cliffordSeq2.append('I')
                   temp_pulseSeq1.append(Delay(32))
                   temp_pulseSeq2.append(Delay(32))
                   len1[0] = len1[0] + 32
                   len2[0] = len2[0] + 32
    
               elif self.interleave == 'CX':
                   cliffordSeq1.append('Ic')
                   cliffordSeq2.append('CX')
                   temp_pulseSeq1.append(r4(np.pi,X_AXIS))
                   temp_pulseSeq2.append(r3(0,0,amp=-amp, drag=drag))
                   len1[0] = len1[0] + twoQ_len
                   len2[0] = len2[0] + twoQ_len
                   
               elif self.interleave == 'CZ': 
                   cliffordSeq1.append('Ic')
                   cliffordSeq2.append('CZ')
                   temp_pulseSeq1.append(Delay(twoQ_len))
                   temp_pulseSeq2.append(r3(0,0,amp=amp, drag=drag))
                   len1[0] = len1[0] + twoQ_len
                   len2[0] = len2[0] + twoQ_len
                   phi1[0] = phi1[0] + self.singleQ_phases[0]
                   phi2[0] = phi2[0] + self.singleQ_phases[1]
     
#               print ('computing recovery')
               print(('cliffordSeq1 is:', cliffordSeq1))
               print(('cliffordSeq2 is:', cliffordSeq2))
    #            # get recovery gate seq
               (recoverySeq1, recoverySeq2, recovery_pulseSeq1, recovery_pulseSeq2) = self.get_recovery_gate(recov_index[n], cliffordSeq1, cliffordSeq2, phi1, phi2, amp, drag, generator = self.generator)
    #           print(phi1[0], phi2[0])
               recov_cliffordSeq1.append(recoverySeq1)
               recov_cliffordSeq2.append(recoverySeq2)
               recov_pulseSeq1.append(recovery_pulseSeq1)
               recov_pulseSeq2.append(recovery_pulseSeq2)
               pulseSeq1.append(temp_pulseSeq1)
               pulseSeq2.append(temp_pulseSeq2)
    
            print(('total # gates:', len(cliffordSeq1)))
            print(('total # gates:', len(cliffordSeq2)))
    
            print(('recov_cliffordSeq1 is:', recov_cliffordSeq1))
            print(('recov_cliffordSeq2 is:', recov_cliffordSeq2))
            
            print(('pulseseq1 is:', pulseSeq1))


        
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

           
        for m in range(self.N_sequences * len(self.param_range)):
           
           

            for ROpostseq in [None, r(np.pi,0), r2(np.pi,0),
                              Combined([r(np.pi,0),r2(np.pi,0)])]:
                s.append(self.seq)
                
                s.append(Combined([Join(pulseSeq1[m]), Join(pulseSeq2[m])]))
                s.append(Combined([Join(recov_pulseSeq1[m]), Join(recov_pulseSeq2[m])]))
            
                if ROpostseq is not None:
                    s.append(ROpostseq)
                s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
    #                s.append(Delay(200))

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



    def get_recovery_gate(self, recov_index, gate_seq_1, gate_seq_2, phase1, phase2, amp, drag, generator = 'CZ'):    

#            
            
        recovery_seq_1 = []
        recovery_seq_2 = []
        temp_pulse_seq_1 = []
        temp_pulse_seq_2 = []
        temp_recov_len1 = [0]
        temp_recov_len2 = [0]
        temp_phi1 = [0] 
        temp_phi2 = [0]
        temp_phi1[0] = temp_phi1[0] + phase1[0]
        temp_phi2[0] = temp_phi2[0] + phase2[0]
        
        
        self.add_twoQ_clifford(recov_index, recovery_seq_1, recovery_seq_2, temp_pulse_seq_1, temp_pulse_seq_2, temp_recov_len1, temp_recov_len2, temp_phi1, temp_phi2, amp, drag, virtualZ=self.virtual_recovery, generator = generator)
#
        return (recovery_seq_1, recovery_seq_2, temp_pulse_seq_1, temp_pulse_seq_2)
#
    
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
                
    def add_singleQ_clifford_virtualZ(self, index, gate_seq, pulse_seq, length, phase, qubit, pad_with_I=False, **kwargs):
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
        # Paulis
        if index == 0:
            gate_seq.append('I')
            pulse_seq.append(Delay(q_len))
            length[0] = length[0] + q_len
        elif index == 1:
            pulse_seq.append(r(np.pi, ((phase[0] % (2*np.pi)))))
            gate_seq.append('Xp')
            length[0] = length[0] + q_len
        elif index == 2:
            pulse_seq.append(r(np.pi, ((phase[0] % (2*np.pi)))+np.pi/2))
            gate_seq.append('VZ2p')
            gate_seq.append('Xp')
            gate_seq.append('VZ2m')
            length[0] = length[0] + q_len
        elif index == 3:
            gate_seq.append('VZp')
            phase[0] = phase[0] + np.pi
    
        # 2pi/3 rotations
        elif index == 4:
            pulse_seq.append(r(np.pi/2, ((phase[0] % (2*np.pi)))+np.pi/2))
            gate_seq.append('VZ2p')
            gate_seq.append('X2p')
            length[0] = length[0] + q_len
            phase[0] = phase[0] + np.pi/2
        elif index == 5:
            pulse_seq.append(r(np.pi/2, ((phase[0] % (2*np.pi)))))
            pulse_seq.append(r(-np.pi/2, ((phase[0] % (2*np.pi)))+np.pi/2))
            gate_seq.append('X2p')
            gate_seq.append('VZ2p')
            gate_seq.append('X2m')
            gate_seq.append('VZ2m')
            length[0] = length[0] + 2*q_len
        elif index == 6:
            pulse_seq.append(r(np.pi/2, ((phase[0] % (2*np.pi)))+np.pi/2))
            gate_seq.append('VZ2p')
            gate_seq.append('X2p')
            gate_seq.append('VZp')
            length[0] = length[0] + q_len
            phase[0] = phase[0] + 3*np.pi/2
        elif index == 7:
            pulse_seq.append(r(-np.pi/2, ((phase[0] % (2*np.pi)))))
            pulse_seq.append(r(-np.pi/2, ((phase[0] % (2*np.pi)))+np.pi/2))
            gate_seq.append('X2m')
            gate_seq.append('VZ2p')
            gate_seq.append('X2m')
            gate_seq.append('VZ2m')
            length[0] = length[0] + 2*q_len
        elif index == 8:
            pulse_seq.append(r(np.pi/2, ((phase[0] % (2*np.pi)))+np.pi/2))
            pulse_seq.append(r(np.pi/2, ((phase[0] % (2*np.pi)))))
            gate_seq.append('VZ2p')
            gate_seq.append('X2p')
            gate_seq.append('VZ2m')
            gate_seq.append('X2p')
            length[0] = length[0] + 2*q_len
        elif index == 9:
            pulse_seq.append(r(-np.pi/2, ((phase[0] % (2*np.pi)))))
            gate_seq.append('X2m')
            gate_seq.append('VZ2p')
            length[0] = length[0] + q_len
            phase[0] = phase[0] + np.pi/2
        elif index == 10:
            pulse_seq.append(r(-np.pi/2, ((phase[0] % (2*np.pi)))+np.pi))
            gate_seq.append('VZp')
            gate_seq.append('X2m')
            gate_seq.append('VZ2m')
            length[0] = length[0] + q_len
            phase[0] = phase[0] + np.pi/2
        elif index == 11:
            pulse_seq.append(r(-np.pi/2, ((phase[0] % (2*np.pi)))))
            gate_seq.append('X2m')
            gate_seq.append('VZ2m')
            length[0] = length[0] + q_len
            phase[0] = phase[0] - np.pi/2
    
        # pi/2 rotations
        elif index == 12:
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))))
            gate_seq.append('X2p')
            length[0] = length[0] + q_len
        elif index == 13:
            pulse_seq.append(r(-np.pi/2, (phase[0] % (2*np.pi))))
            gate_seq.append('X2m')
            length[0] = length[0] + q_len
        elif index == 14:
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))+np.pi/2))
            gate_seq.append('VZ2p')
            gate_seq.append('X2p')
            gate_seq.append('VZ2m')
            length[0] = length[0] + q_len
        elif index == 15:
            pulse_seq.append(r(-np.pi/2, (phase[0] % (2*np.pi))+np.pi/2))
            gate_seq.append('VZ2p')
            gate_seq.append('X2m')
            gate_seq.append('VZ2m')
            length[0] = length[0] + q_len
        elif index == 16:
            gate_seq.append('VZ2m')
            phase[0] = phase[0] - np.pi/2
        elif index == 17:
            gate_seq.append('VZ2p')
            phase[0] = phase[0] + np.pi/2

    
        # Hadamard-Like
        elif index == 18:
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))+np.pi/2))
            gate_seq.append('VZ2p')
            gate_seq.append('X2p')
            gate_seq.append('VZ2p')
            length[0] = length[0] + q_len
            phase[0] = phase[0] + np.pi
        elif index == 19:
            pulse_seq.append(r(np.pi, (phase[0] % (2*np.pi))))
            pulse_seq.append(r(-np.pi/2, (phase[0] % (2*np.pi))+np.pi/2))
            gate_seq.append('Xp')
            gate_seq.append('VZ2p')
            gate_seq.append('X2m')
            gate_seq.append('VZ2m')
            length[0] = length[0] + 2*q_len
        elif index == 20:
            pulse_seq.append(r(np.pi, (phase[0] % (2*np.pi))+np.pi/2))
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))))
            gate_seq.append('VZ2p')
            gate_seq.append('Xp')
            gate_seq.append('VZ2m')
            gate_seq.append('X2p')
            length[0] = length[0] + 2*q_len
        elif index == 21:
            pulse_seq.append(r(np.pi, (((phase[0] % (2*np.pi))))+np.pi/2))
            pulse_seq.append(r(-np.pi/2, ((phase[0] % (2*np.pi)))))
            gate_seq.append('VZ2p')
            gate_seq.append('Xp')
            gate_seq.append('VZ2m')
            gate_seq.append('X2m')
            length[0] = length[0] + 2*q_len
        elif index == 22:
            pulse_seq.append(r(np.pi, ((phase[0] % (2*np.pi)))+np.pi/2))
            gate_seq.append('VZ2p')
            gate_seq.append('Xp')
            length[0] = length[0] + q_len
            phase[0] = phase[0] + np.pi/2
        elif index == 23: 
            pulse_seq.append(r(np.pi/2, ((phase[0] % (2*np.pi)))+np.pi/2))
            pulse_seq.append(r(-np.pi/2, ((phase[0] % (2*np.pi)))+3*np.pi/2))
            gate_seq.append('VZ2p')
            gate_seq.append('X2p')
            gate_seq.append('VZp')
            gate_seq.append('X2m')
            length[0] = length[0] + 2*q_len
            phase[0] = phase[0] + 3*np.pi/2
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
    
    
    def add_twoQ_clifford(self, index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, phase1, phase2, amp, drag, virtualZ=True, generator = 'ZX90'):
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
            self.add_singleQ_based_twoQ_clifford(index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, phase1, phase2, virtual=virtualZ)
        elif (index < 5184 + 576):
            self.add_CNOT_like_twoQ_clifford(index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, phase1, phase2, amp, drag,generator = generator)
        elif (index < 5184 + 5184 + 576):
            self.add_iSWAP_like_twoQ_clifford(index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, phase1, phase2, amp, drag,  generator = generator)
        elif (index < 576 + 5184 + 5184 + 576):
            self.add_SWAP_like_twoQ_clifford(index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, phase1, phase2, amp, drag, generator = generator)
        else:
            raise ValueError(
                'index is out of range. it should be smaller than 11520 and '
                'greater or equal to 0: ', str(index))            
        self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
    
        pass
    
    def add_singleQ_S1(self, index, gate_seq, pulse_seq, length, phase, qubit):
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
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))+np.pi/2))
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))))
#            pulse_seq.append(Delay(q_len))
            length[0] = length[0] + 2*q_len
        elif index == 2:
            gate_seq.append('X2m')
            gate_seq.append('Y2m')
#            gate_seq.append('I')  # auxiliary
            pulse_seq.append(r(-np.pi/2, (phase[0] % (2*np.pi))))
            pulse_seq.append(r(-np.pi/2, (phase[0] % (2*np.pi))+np.pi/2))
#            pulse_seq.append(Delay(q_len))
            length[0] = length[0] + 2*q_len
            
    def add_singleQ_S1_virtualZ(self, index, gate_seq, pulse_seq, length, phase, qubit):
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
            pulse_seq.append(r(np.pi/2, ((phase[0] % (2*np.pi)))+np.pi/2))
            pulse_seq.append(r(np.pi/2, ((phase[0] % (2*np.pi)))))
            gate_seq.append('VZ2p')
            gate_seq.append('X2p')
            gate_seq.append('VZ2m')
            gate_seq.append('X2p')
            length[0] = length[0] + 2*q_len
        elif index == 2:
            pulse_seq.append(r(-np.pi/2, ((phase[0] % (2*np.pi)))))
            pulse_seq.append(r(-np.pi/2, ((phase[0] % (2*np.pi)))+np.pi/2))
            gate_seq.append('X2m')
            gate_seq.append('VZ2p')
            gate_seq.append('X2m')
            gate_seq.append('VZ2m')
            length[0] = length[0] + 2*q_len
    
    
    def add_singleQ_S1_X2p(self, index, gate_seq, pulse_seq, length, phase, qubit):
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
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))))
#            pulse_seq.append(Delay(q_len))  # auxiliary
#            pulse_seq.append(Delay(q_len))  # auxiliary
            length[0] = length[0] + q_len
        elif index == 1:
            gate_seq.append('X2p')
            gate_seq.append('Y2p')
            gate_seq.append('X2p')
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))))
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))+np.pi/2))
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))))
            length[0] = length[0] + 3*q_len
        elif index == 2:
            gate_seq.append('Y2m')
#            gate_seq.append('I')
#            gate_seq.append('I')
            pulse_seq.append(r(-np.pi/2, (phase[0] % (2*np.pi))+np.pi/2))
#            pulse_seq.append(Delay(q_len))  # auxiliary
#            pulse_seq.append(Delay(q_len))  # auxiliary
            length[0] = length[0] + q_len
            
    def add_singleQ_S1_X2p_virtualZ(self, index, gate_seq, pulse_seq, length, phase, qubit):
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
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))))
            length[0] = length[0] + q_len
        elif index == 1:
            pulse_seq.append(r(np.pi, ((phase[0] % (2*np.pi)))+np.pi/2))
            gate_seq.append('VZ2p')
            gate_seq.append('Xp')
            length[0] = length[0] + q_len
            phase[0] = phase[0] + np.pi/2
        elif index == 2:
            pulse_seq.append(r(-np.pi/2, (phase[0] % (2*np.pi))+np.pi/2))
            gate_seq.append('VZ2p')
            gate_seq.append('X2m')
            gate_seq.append('VZ2m')
            length[0] = length[0] + q_len
    
    
    def add_singleQ_S1_Y2p(self,index, gate_seq, pulse_seq, length, phase, qubit):
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
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))+np.pi/2))
#            pulse_seq.append(Delay(q_len))  # auxiliary
#            pulse_seq.append(Delay(q_len))  # auxiliary
            length[0] = length[0] + q_len
        elif index == 1:
            gate_seq.append('Yp')
            gate_seq.append('X2p')
#            gate_seq.append('I')
            pulse_seq.append(r(np.pi, (phase[0] % (2*np.pi))+np.pi/2))
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))))
#            pulse_seq.append(Delay(q_len))  # auxiliary
            length[0] = length[0] + 2*q_len
        elif index == 2:
            gate_seq.append('X2m')
            gate_seq.append('Y2m')
            gate_seq.append('X2p')
            pulse_seq.append(r(-np.pi/2, (phase[0] % (2*np.pi))))
            pulse_seq.append(r(-np.pi/2, (phase[0] % (2*np.pi))+np.pi/2))
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))))
            length[0] = length[0] + 3*q_len
            
    def add_singleQ_S1_Y2p_virtualZ(self,index, gate_seq, pulse_seq, length, phase, qubit):
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
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))+np.pi/2))
            gate_seq.append('VZ2p')
            gate_seq.append('X2p')
            gate_seq.append('VZ2m')
            length[0] = length[0] + q_len
        elif index == 1:
            pulse_seq.append(r(np.pi, (phase[0] % (2*np.pi))+np.pi/2))
            pulse_seq.append(r(np.pi/2, (phase[0] % (2*np.pi))))
            gate_seq.append('VZ2p')
            gate_seq.append('Xp')
            gate_seq.append('VZ2m')
            gate_seq.append('X2p')
            length[0] = length[0] + 2*q_len
        elif index == 2:
            gate_seq.append('VZ2p')
            phase[0] = phase[0] + np.pi/2
    
    def add_singleQ_S1_Z2p(self, index, gate_seq, pulse_seq, length, phase, qubit):
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
            
    def add_singleQ_S1_X2p_Y2m(self, index, gate_seq, pulse_seq, length, phase, qubit):
        """Add single qubit clifford from S1_X2p_Y2m.
    
        (X2p-plus-Y2m-like-subset of single qubit clifford group) (3)
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
            gate_seq.append('Y2m')
#            gate_seq.append('I')
            pulse_seq.append(r(np.pi/2, X_AXIS))
            pulse_seq.append(r(-np.pi/2, Y_AXIS))  
#            pulse_seq.append(Delay(q_len))  # auxiliary
            length[0] = length[0] + 2*q_len
        elif index == 1:
            gate_seq.append('Xp')
#            gate_seq.append('Y2p')
#            gate_seq.append('X2p')
            pulse_seq.append(r(np.pi, X_AXIS))
#            pulse_seq.append(r(np.pi/2, Y_AXIS))
#            pulse_seq.append(r(np.pi/2, X_AXIS))
            length[0] = length[0] + q_len
        elif index == 2:
            gate_seq.append('Y2m')
            gate_seq.append('X2m')
#            gate_seq.append('I')
            pulse_seq.append(r(-np.pi/2, Y_AXIS))
            pulse_seq.append(r(-np.pi/2, X_AXIS))  
#            pulse_seq.append(Delay(q_len))  # auxiliary
            length[0] = length[0] + 2*q_len
    
    def add_singleQ_based_twoQ_clifford(self,index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, phase1, phase2, virtual, **kwargs):
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
        if virtual == True:
            self.add_singleQ_clifford_virtualZ(index_1, gate_seq_1, pulse_seq_1, length1, phase1, 1)
            self.add_singleQ_clifford_virtualZ(index_2, gate_seq_2, pulse_seq_2, length2, phase2, 2)
        else:
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
    
    
    def add_CNOT_like_twoQ_clifford(self, index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, phase1, phase2, amp, drag, generator='ZX90', **kwargs):
        """Add CNOT like two Qubit Clifford.
    
        (24*24*3*3 = 5184)
        (gate_seq_1: gate seq. of qubit #1, gate_seq_t: gate seq. of qubit #2)
        """
        r = self.qubit_info.rotate
        r2 = self.qubit2_info.rotate
        r3 = self.twoQ_info.rotate
        r4 = self.cancel_info.rotate
        q_len1 = self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len
        q_len2 = self.qubit2_info.chop*self.qubit2_info.w+self.qubit2_info.sq_len
        twoQ_len = self.twoQ_info.chop*self.twoQ_info.w+self.twoQ_info.sq_len# + self.cancel_info.chop*self.cancel_info.w+self.cancel_info.sq_len 
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
    
        if generator == 'CZ':
            if self.use_virtual_Z == True:
                self.add_singleQ_clifford_virtualZ(index_1, gate_seq_1, pulse_seq_1, length1, phase1, 1)
                self.add_singleQ_clifford_virtualZ(index_2, gate_seq_2, pulse_seq_2, length2, phase2, 2)
            else:
                self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
                self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('CZ')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            phase1[0] = phase1[0] + self.singleQ_phases[0]
            phase2[0] = phase2[0] + self.singleQ_phases[1]
            if self.use_virtual_Z == True:
                self.add_singleQ_S1_virtualZ(index_3, gate_seq_1, pulse_seq_1, length1, phase1, qubit=1)
                self.add_singleQ_S1_Y2p_virtualZ(index_4, gate_seq_2, pulse_seq_2, length2, phase2, qubit=2)
            else:
                self.add_singleQ_S1(index_3, gate_seq_1, pulse_seq_1, length1, phase1, qubit=1)
                self.add_singleQ_S1_Y2p(index_4, gate_seq_2, pulse_seq_2, length2, phase2, qubit=2)
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
            
        elif generator == 'CNOT':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('CNOT')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
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
#            pulse_seq_2.append(r3(0,0,amp=-amp, drag=drag))
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
            pulse_seq_2.append(r3(0,0,amp=-amp, drag=drag))
            pulse_seq_2.append(r(np.pi,X_AXIS))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            pulse_seq_2.append(r(np.pi,X_AXIS))


            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            
            self.add_singleQ_S1(index_3, gate_seq_1, pulse_seq_1, length1, qubit=1)
            self.add_singleQ_S1(index_4, gate_seq_2, pulse_seq_2, length2, qubit=2)

        elif generator == 'CX':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('CX')
#            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=-amp, drag=drag))
            pulse_seq_1.append(r4(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            
            self.add_singleQ_S1(index_3, gate_seq_1, pulse_seq_1, length1, qubit=1)
            self.add_singleQ_S1(index_4, gate_seq_2, pulse_seq_2, length2, qubit=2)
            
        elif generator == 'ZX90':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, qubit=1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, qubit=2)
                    
            gate_seq_1.append('I')
            gate_seq_2.append('ZX90')
            
            self.add_singleQ_S1(index_3, gate_seq_1, pulse_seq_1, length1, qubit=1)
            self.add_singleQ_S1(index_4, gate_seq_2, pulse_seq_2, length2, qubit=2)
    
        elif generator == 'CX':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, qubit=1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, qubit=2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)

                    
            gate_seq_1.append('I')
            gate_seq_2.append('CX')
            
            self.add_singleQ_S1(index_3, gate_seq_1, pulse_seq_1, length1, qubit=1)
            self.add_singleQ_S1(index_4, gate_seq_2, pulse_seq_2, length2, qubit=2)
    
    
    def add_iSWAP_like_twoQ_clifford(self, index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, phase1, phase2, amp, drag, generator='ZX90', **kwargs):
        """Add iSWAP like two Qubit Clifford.
    
        (24*24*3*3 = 5184)
        (gate_seq_1: gate seq. of qubit #1, gate_seq_t: gate seq. of qubit #2)
        """
        r = self.qubit_info.rotate
        r2 = self.qubit2_info.rotate
        r3 = self.twoQ_info.rotate
        r4 = self.cancel_info.rotate
        q_len1 = self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len
        q_len2 = self.qubit2_info.chop*self.qubit2_info.w+self.qubit2_info.sq_len
        twoQ_len = self.twoQ_info.chop*self.twoQ_info.w+self.twoQ_info.sq_len# + self.cancel_info.chop*self.cancel_info.w+self.cancel_info.sq_len 
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
    
    
    
        if generator == 'CZ':
            if self.use_virtual_Z == True:
                self.add_singleQ_clifford_virtualZ(index_1, gate_seq_1, pulse_seq_1, length1, phase1, 1)
                self.add_singleQ_clifford_virtualZ(index_2, gate_seq_2, pulse_seq_2, length2, phase2, 2)
            else:
                self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
                self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
                
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('CZ')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            phase1[0] = phase1[0] + self.singleQ_phases[0]
            phase2[0] = phase2[0] + self.singleQ_phases[1]
            
            if self.use_virtual_Z == True:
                gate_seq_1.append('VZ2p')
                gate_seq_1.append('X2p')
                gate_seq_1.append('VZ2m')
                gate_seq_2.append('X2m')
                gate_seq_2.append('Ip')
                gate_seq_2.append('Ip')
                pulse_seq_1.append(r(np.pi/2, (phase1[0] % (2*np.pi))+np.pi/2))
                pulse_seq_2.append(r2(-np.pi/2, (phase2[0] % (2*np.pi))))
                length1[0] = length1[0] + q_len1
                length2[0] = length2[0] + q_len2
            else:
                gate_seq_1.append('Y2p')
                gate_seq_2.append('X2m')
                pulse_seq_1.append(r(np.pi/2, Y_AXIS))
                pulse_seq_2.append(r2(-np.pi/2, X_AXIS))
                length1[0] = length1[0] + q_len1
                length2[0] = length2[0] + q_len2
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('CZ')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            phase1[0] = phase1[0] + self.singleQ_phases[0]
            phase2[0] = phase2[0] + self.singleQ_phases[1]
            
            if self.use_virtual_Z == True:
                self.add_singleQ_S1_Y2p_virtualZ(index_3, gate_seq_1, pulse_seq_1, length1, phase1, qubit=1)
                self.add_singleQ_S1_X2p_virtualZ(index_4, gate_seq_2, pulse_seq_2, length2, phase2, qubit=2)
            else:
                self.add_singleQ_S1_Y2p(index_3, gate_seq_1, pulse_seq_1, length1, phase1, qubit=1)
                self.add_singleQ_S1_X2p(index_4, gate_seq_2, pulse_seq_2, length2, phase2, qubit=2)



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
            
        elif generator == 'CNOT':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                        
            gate_seq_1.append('Ic')
            gate_seq_2.append('CNOT')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
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
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            pulse_seq_2.append(r4(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            
            self.add_singleQ_S1_X2p(index_3, gate_seq_1, pulse_seq_1, length1, qubit=1)
            self.add_singleQ_S1(index_4, gate_seq_2, pulse_seq_2, length2, qubit=2)
        
#ebru adding echo
        elif generator == 'ZX90':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                        
            gate_seq_1.append('Ic')
            gate_seq_2.append('ZX90')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=-amp, drag=drag))
            pulse_seq_2.append(r(np.pi,X_AXIS))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            pulse_seq_2.append(r(np.pi,X_AXIS))

            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            
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
            pulse_seq_2.append(r3(0,0,amp=-amp, drag=drag))
            pulse_seq_2.append(r(np.pi,X_AXIS))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            pulse_seq_2.append(r(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            
            self.add_singleQ_S1(index_3, gate_seq_1, pulse_seq_1, length1, qubit=1)
            self.add_singleQ_S1(index_4, gate_seq_2, pulse_seq_2, length2, qubit=2)



            
        elif generator == 'CX':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                        
            gate_seq_1.append('Ic')
            gate_seq_2.append('CX')
#            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=-amp, drag=drag))
            pulse_seq_1.append(r4(np.pi,X_AXIS))
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
            gate_seq_2.append('CX')
#            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=-amp, drag=drag))
            pulse_seq_1.append(r4(np.pi,X_AXIS))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            
            self.add_singleQ_S1_X2p_Y2m(index_3, gate_seq_1, pulse_seq_1, length1, qubit=1)
            self.add_singleQ_S1(index_4, gate_seq_2, pulse_seq_2, length2, qubit=2)
    
    
    def add_SWAP_like_twoQ_clifford(self, index, gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2, phase1, phase2, amp, drag, generator='ZX90', **kwargs):
        """Add SWAP like two Qubit Clifford.
    
        (24*24*= 576)
        (gate_seq_1: gate seq. of qubit #1, gate_seq_t: gate seq. of qubit #2)
        """
        r = self.qubit_info.rotate
        r2 = self.qubit2_info.rotate
        r3 = self.twoQ_info.rotate
        r4 = self.cancel_info.rotate
        q_len1 = self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len
        q_len2 = self.qubit2_info.chop*self.qubit2_info.w+self.qubit2_info.sq_len
        twoQ_len = self.twoQ_info.chop*self.twoQ_info.w+self.twoQ_info.sq_len #+ self.cancel_info.chop*self.cancel_info.w+self.cancel_info.sq_len 

#        print(index)
#        print(type(index))
        
        # randomly sample from single qubit cliffords (24)
        index_1 = index % 24
#        print(index_1)
#        print(type(index_1))
    
        # randomly sample from single qubit cliffords (24)
        index_2 = (index // 24) % 24
    
        if generator == 'CZ':
            if self.use_virtual_Z == True:
                self.add_singleQ_clifford_virtualZ(index_1, gate_seq_1, pulse_seq_1, length1, phase1, 1)
                self.add_singleQ_clifford_virtualZ(index_2, gate_seq_2, pulse_seq_2, length2, phase2, 2)
            else:
                self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
                self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('CZ')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            phase1[0] = phase1[0] + self.singleQ_phases[0]
            phase2[0] = phase2[0] + self.singleQ_phases[1]
            
            if self.use_virtual_Z == True:
                gate_seq_1.append('VZ2p')
                gate_seq_1.append('X2m')
                gate_seq_1.append('VZ2m')
                gate_seq_2.append('VZ2p')
                gate_seq_2.append('X2p')
                gate_seq_2.append('VZ2m')
                pulse_seq_1.append(r(-np.pi/2, ((phase1[0] % (2*np.pi)))+np.pi/2))
                pulse_seq_2.append(r2(np.pi/2, ((phase2[0] % (2*np.pi)))+np.pi/2))
                length1[0] = length1[0] + q_len1
                length2[0] = length2[0] + q_len2
            else:
                gate_seq_1.append('Y2m')
                gate_seq_2.append('Y2p')
                pulse_seq_1.append(r(-np.pi/2, Y_AXIS))
                pulse_seq_2.append(r2(np.pi/2, Y_AXIS))
                length1[0] = length1[0] + q_len1
                length2[0] = length2[0] + q_len2
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('CZ')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            phase1[0] = phase1[0] + self.singleQ_phases[0]
            phase2[0] = phase2[0] + self.singleQ_phases[1]
            
            if self.use_virtual_Z == True:
                gate_seq_1.append('VZ2p')
                gate_seq_1.append('X2p')
                gate_seq_1.append('VZ2m')
                gate_seq_2.append('VZ2p')
                gate_seq_2.append('X2m')
                gate_seq_2.append('VZ2m')
                pulse_seq_1.append(r(np.pi/2, ((phase1[0] % (2*np.pi)))+np.pi/2))
                pulse_seq_2.append(r2(-np.pi/2, ((phase2[0] % (2*np.pi)))+np.pi/2))
                length1[0] = length1[0] + q_len1
                length2[0] = length2[0] + q_len2
            else:
                gate_seq_1.append('Y2p')
                gate_seq_2.append('Y2m')
                pulse_seq_1.append(r(np.pi/2, Y_AXIS))
                pulse_seq_2.append(r2(-np.pi/2, Y_AXIS))
                length1[0] = length1[0] + q_len1
                length2[0] = length2[0] + q_len2
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('CZ')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            phase1[0] = phase1[0] + self.singleQ_phases[0]
            phase2[0] = phase2[0] + self.singleQ_phases[1]
            
            if self.use_virtual_Z == True:
                gate_seq_1.append('Ip')
                gate_seq_1.append('Ip')
                gate_seq_1.append('Ip')
                gate_seq_2.append('VZ2p')
                gate_seq_2.append('X2p')
                gate_seq_2.append('VZ2m')
                pulse_seq_2.append(r2(np.pi/2, ((phase2[0] % (2*np.pi)))+np.pi/2))
                length2[0] = length2[0] + q_len2
            else:
                gate_seq_1.append('Ip')
                gate_seq_2.append('Y2p')
                pulse_seq_2.append(r2(np.pi/2, Y_AXIS))
                length2[0] = length2[0] + q_len2
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
            
        elif generator == 'CNOT':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
            
            gate_seq_1.append('Ic')
            gate_seq_2.append('CNOT')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
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
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
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
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
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
#            pulse_seq_2.append(r3(0,0,amp=-amp, drag=drag))
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
#            pulse_seq_2.append(r3(0,0,amp=-amp, drag=drag))
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
#            pulse_seq_2.append(r3(0,0,amp=-amp, drag=drag))
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
            pulse_seq_2.append(r3(0,0,amp=-amp, drag=drag))
            pulse_seq_2.append(r(np.pi,X_AXIS))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            pulse_seq_2.append(r(np.pi,X_AXIS))



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
            gate_seq_2.append('ZX90')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=-amp, drag=drag))
            pulse_seq_2.append(r(np.pi,X_AXIS))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            pulse_seq_2.append(r(np.pi,X_AXIS))

            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            
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
            pulse_seq_2.append(r3(0,0,amp=-amp, drag=drag))
            pulse_seq_2.append(r(np.pi,X_AXIS))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            pulse_seq_2.append(r(np.pi,X_AXIS))

            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len




            
        elif generator == 'CX':
            self.add_singleQ_clifford(index_1, gate_seq_1, pulse_seq_1, length1, 1)
            self.add_singleQ_clifford(index_2, gate_seq_2, pulse_seq_2, length2, 2)
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
            
            gate_seq_1.append('I')
            gate_seq_2.append('CX')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            
            gate_seq_1.append('X2m')
            gate_seq_2.append('Y2p')
            pulse_seq_1.append(r(-np.pi/2, X_AXIS))
            pulse_seq_2.append(r2(np.pi/2, Y_AXIS))
            length1[0] = length1[0] + q_len1
            length2[0] = length2[0] + q_len2
            
            gate_seq_1.append('Y2m')
            gate_seq_2.append('Xp')
            pulse_seq_1.append(r(-np.pi/2, Y_AXIS))
            pulse_seq_2.append(r2(np.pi, X_AXIS))
            length1[0] = length1[0] + q_len1
            length2[0] = length2[0] + q_len2
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
            
            gate_seq_1.append('I')
            gate_seq_2.append('CX')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            
            gate_seq_1.append('X2m')
            gate_seq_2.append('Y2p')
            pulse_seq_1.append(r(-np.pi/2, X_AXIS))
            pulse_seq_2.append(r2(np.pi/2, Y_AXIS))
            length1[0] = length1[0] + q_len1
            length2[0] = length2[0] + q_len2
            
            gate_seq_1.append('Y2m')
            gate_seq_2.append('Xp')
            pulse_seq_1.append(r(-np.pi/2, Y_AXIS))
            pulse_seq_2.append(r2(np.pi, X_AXIS))
            length1[0] = length1[0] + q_len1
            length2[0] = length2[0] + q_len2
            
            self.pad_sequences(gate_seq_1, gate_seq_2, pulse_seq_1, pulse_seq_2, length1, length2)
            
            gate_seq_1.append('I')
            gate_seq_2.append('CX')
            pulse_seq_1.append(Delay(twoQ_len))
            pulse_seq_2.append(r3(0,0,amp=amp, drag=drag))
            length1[0] = length1[0] + twoQ_len
            length2[0] = length2[0] + twoQ_len
            

    def analyze(self, data=None, fig=None):
        results = analysis(self, data, fig)
        self.Pgg = results[0]
        self.Pg1 = results[1]
        self.Pg2 = results[2]
        return self.Pgg