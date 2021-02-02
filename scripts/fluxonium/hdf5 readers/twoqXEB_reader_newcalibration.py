# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 19:52:53 2019

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Sun May 19 23:34:46 2019

@author: Wang_Lab
"""

'''
Reading data from ssb spec HDF5 file to fit lorentzian cruves to get cavity
temperatures. Requires the path information to be filled out. Also requires
the min_x and max_x to be specified for the lorentaizn peak you want to fit.
Take amplitude values to calculate the temp.

Jeff Gertler
'''



import os
import time
if 0:
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)


import mclient
from mclient import instruments

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
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

if 1:
    from scripts.fluxonium import TwoQ_RB
    
    rndmben_result0 = []
    Pg_cplx = []
    #rndmben_result1 = []
    #Pg_cplx1 = []
    #
    
    gate_info1 = mclient.get_gate_info('sq_gate1')
    gate_info2 = mclient.get_gate_info('sq_gate2')
    cancel_info = mclient.get_gate_info('cancel_gate')
    #zx90_info = mclient.get_gate_info('zx90_gate')
    cx_info = mclient.get_gate_info('cx_gate')
    ZZ_info = mclient.get_gate_info('ZZ_gate')
    CZ = mclient.instruments['ZZ_gate']
    
    
    
    from scripts.fluxonium import TwoQ_RB_ebru_temp
    
    
    ''' Path to the .hdf5 file '''
    filepath = 'C:\Users\wanglab\Desktop\hdf5_copies'
    hdf5_name = '\Fluxonium31october_copy_2.hdf5'
    date = '20201112'
    
    #non interleaved
    timetable1 = ['013103', '014153', '015246', '020339', '021425', '022516', '023603', '024652', '025742',
                  '030847', '031941', '033036', '034133', '035229', '040326', '041421', '042521', '043619', 
                  '044720', '045821', '050921', '052022', '053122', '054225', '055330', 
                  '060431', '061529', '062632', '063739', '064845', '065954', '071102', '072215', 
                  '073328', '074447', '075603', '080715', '081831', '082946', '084100', '085210',
                  '090323', '091438', '092555', '093719'                
                  ]
    


    
    
    
    experiment = 'CrossEB'
    
    ''' Primary x axis and secondary if 2d'''
    x_key = 'Cycles'
    #x2_key = 'powers'
    
    
    time = timetable1[44]
    f = h5.File(filepath + hdf5_name, 'r')
    exp = f['/' + date + '/' + time + '_' + experiment]    
    rndmben0 = TwoQ_RB_ebru_temp.TwoQubit_RB(gate_info2, gate_info1, ZZ_info, cancel_info, num_cal_points=3, N_cliffords=35, 
                                  plot_seqs=False, category='all', generator='CZ',
                                  find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True, use_lookup_table=True,
                                  singleQ_phases=[-2.685,-1.366], seq=None, proj_func='phase')
    
    data = exp['avg'].value
    
    ys=data
    
    
#    xs=np.array([-2.,  -1.,  0.,   1.,   2.,   3.,   4.,   5., 6, 7,8,9,10,11,12,13,14,15,16,17,
#                 18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34])
    y2d = ys.reshape(4,len(ys)/4)
    y1s = y2d[0,:]
    y2s = y2d[1,:]
    y3s = y2d[2,:]
    y4s = y2d[3,:]
    
    
    #3 is the number of calibration point here
    calibration_qubit1_excited = y2s[:3] 
    calibration_qubit2_excited = y3s[:3]
    calibration_bothqubits_excited = y4s[:3]
    calibration_ground = y1s[:3]


    Y3 = np.mean(calibration_qubit1_excited)
    Y2 = np.mean(calibration_qubit2_excited)
    Y4 = np.mean(calibration_bothqubits_excited)
    Y1 = np.mean(calibration_ground)
    
if 0: #getting I_vectors for each of the sequences to see how much they deviate from the 
    #initial value, V_fixed is obtained by the first sequence's V_vector 
    print Y1, Y2, Y3, Y4

#    
    Y_vector = [Y1, Y2, Y3, Y4] #made of calibration points


#    
    
    I_vector =  np.dot(np.linalg.inv(V_fixed), Y_vector)
    I.append(I_vector)

if 1: #new method: getting V matrix directly with the initial populations
    Y3 = np.mean(calibration_qubit1_excited)
    Y2 = np.mean(calibration_qubit2_excited)
    Y4 = np.mean(calibration_bothqubits_excited)
    Y1 = np.mean(calibration_ground)
    print Y1, Y2, Y3, Y4


#
    Igg = 0.8691419515005903
    Ieg = 0.09027808839670717
    Ige = 0.036761527015064785
    Iee = 0.00381843308763781


    I_matrix = np.matrix([[Igg, Ige, Ieg, Iee], [Ige, Igg, Iee, Ieg], 
                          [Ieg, Iee, Igg, Ige], [Iee, Ieg, Ige, Igg]])
#    
    Y_vector = [Y1, Y2, Y3, Y4] #made of calibration points
    V_vector = np.zeros(4)
    
    V_vector =  np.dot(np.linalg.inv(I_matrix), Y_vector)
    V_vector=np.transpose(V_vector)
    Vgg = np.asarray(V_vector[0]).reshape(-1)[0] 
    Vge= np.asarray(V_vector[1]).reshape(-1)[0]
    Veg = np.asarray(V_vector[2]).reshape(-1)[0]
    Vee= np.asarray(V_vector[3]).reshape(-1)[0] 


    rd = y1s[3:]
    bl = y2s[3:]
    gr = y3s[3:]
    yw = y4s[3:]

#
#
#
#    
    y_vector = [rd, gr, bl, yw]
#
#
    V_matrix = np.matrix([[Vgg, Vge, Veg, Vee], [Vge, Vgg, Vee, Veg], 
                          [Veg, Vee, Vgg, Vge], [Vee, Veg, Vge, Vgg]])
#    V_fixed=V_matrix
    P = np.dot(np.linalg.inv(V_matrix), y_vector)  #those are already our real populations 
    P1_corrected.append(np.transpose((P)))

