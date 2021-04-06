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
    
    
    
    from scripts.fluxonium import TwoQ_RB
    
    
    ''' Path to the .hdf5 file '''
    filepath = 'C:\Users\wanglab\Desktop\hdf5_copies'
    hdf5_name = '\Fluxonium31october_copy.hdf5'
    date = '20201105'
    
    #non interleaved
    timetable1 = ['025859', '030447', '031027', '031602', '032139', '032712', '033248', '033824', '034400', 
                  '034938', '035515', '040053', '040630', '041208', '041748', '042327', '042902',
                  '043447', '044022', '044555', '045130', '045703', '050238', '050814', '051349', 
                  '051923', '052458', '053033', '053608', '054145']
    
    
    #interleaved with CZ
    
    timetable2 = ['030149', '030738', '031314', '031850', '032423', '033000', '033535', '034110', '034647',
                  '035225', '035804', '040339', '040918', '041455', '042036', '042613', '043158',
                  '043734', '044307', '044842', '045415', '045950', '050525', '051100', '051635', 
                  '052209', '052744', '053320', '053856', '054432']
    
    
    experiment = 'TwoQubit_RB'
    
    ''' Primary x axis and secondary if 2d'''
    x_key = 'Cliffords'
    #x2_key = 'powers'
    
    
    time = timetable1[29]
    f = h5.File(filepath + hdf5_name, 'r')
    exp = f['/' + date + '/' + time + '_' + experiment]    
    rndmben0 = TwoQ_RB.TwoQubit_RB(gate_info2, gate_info1, ZZ_info, cancel_info, num_cal_points=3, N_cliffords=35, 
                                  plot_seqs=False, category='all', generator='CZ',
                                  find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True, use_lookup_table=True,
                                  singleQ_phases=[-2.685,-1.366], seq=None, proj_func='phase')
    
    data = exp['avg'].value
    
    ys=data
    
    
    y2d = ys.reshape(len(ys)/4,4)
    xs=np.array([-11., -10.,  -9.,  -8.,  -7.,  -6.,  -5.,  -4.,  -3.,  -2.,  -1.,
             0.,   1.,   2.,   3.,   4.,   5.,   6.,   7.,   8.,   9.,  10.,
            11.,  12., 13, 14, 15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35])
    y1s = y2d[:,0]
    y2s = y2d[:,1]
    y3s = y2d[:,2]
    y4s = y2d[:,3]    
    
    #3 is the number of calibration point here
    calibration_qubit1_excited = (y1s[:3] + y2s[:3] + y3s[:3] + y4s[:3])/4
    calibration_qubit2_excited = (y1s[3:6] + y2s[3:6] + y3s[3:6] + y4s[3:6])/4
    calibration_bothqubits_excited = (y1s[6:9] + y2s[6:9] + y3s[6:9] + y4s[6:9])/4
    calibration_ground = (y1s[9:12] + y2s[9:12] + y3s[9:12] + y4s[9:12])/4
    

#    if 0:   #old method: multiplying fake populations with the initial populations matrix
#        Veg = np.mean(calibration_qubit1_excited)
#        Vge = np.mean(calibration_qubit2_excited)
#        Vee = np.mean(calibration_bothqubits_excited)
#        Vgg = np.mean(calibration_ground)
#        print Veg, Vge, Vee, Vgg
#        
#        rd = y1s[12:]
#        bl = y2s[12:]
#        gr = y3s[12:]
#        yw = y4s[12:]
#        
#        
#        
#        
#        
#        Pg1 = ((-rd-gr+bl+yw)/(Veg-Vgg+Vee-Vge)+1)/2
#        Pg2 = ((-rd-bl+gr+yw)/(Vge-Vgg+Vee-Veg)+1)/2
#        
#        
#        
#        
#        V_matrix = np.matrix([[Vgg, Vge, Veg, Vee], [Vge, Vgg, Vee, Veg], 
#                              [Veg, Vee, Vgg, Vge], [Vee, Veg, Vge, Vgg]])
#        y_vector = [rd, gr, bl, yw]
#        P = np.dot(np.linalg.inv(V_matrix), y_vector)
#        
#        
#        
#        
#        Igg = 0.8762473293856167
#        Ieg = 0.08728002509852012
#        Ige = 0.033168812572024906
#        Iee = 0.0033038329438382008
#        
#        I_matrix = np.matrix([[Igg, Ige, Ieg, Iee], [Ige, Igg, Iee, Ieg], 
#                              [Ieg, Iee, Igg, Ige], [Iee, Ieg, Ige, Igg]])
#        #    
#        P_correct = np.dot(I_matrix, P)
#        #
#        Pgg = np.transpose(P_correct[0])
#        #
#        Pge = np.transpose(P_correct[1])
#        #
#        Peg = np.transpose(P_correct[2])
#        #
#        Pee = np.transpose(P_correct[3])
#        
#        
#        
#        Pgg= Pgg.A1
    
    
if 1: #getting I_vectors for each of the sequences to see how much they deviate from the 
    #initial value, V_fixed is obtained by the first sequence's V_vector 
    
    Y3 = np.mean(calibration_qubit1_excited)
    Y2 = np.mean(calibration_qubit2_excited)
    Y4 = np.mean(calibration_bothqubits_excited)
    Y1 = np.mean(calibration_ground)
    print Y1, Y2, Y3, Y4


#    
    Y_vector = [Y1, Y2, Y3, Y4] #made of calibration points
    
    I_vector =  np.dot(np.linalg.inv(V_fixed), Y_vector)
    I.append(I_vector)

if 0: #new method: getting V matrix directly with the initial populations
    Y3 = np.mean(calibration_qubit1_excited)
    Y2 = np.mean(calibration_qubit2_excited)
    Y4 = np.mean(calibration_bothqubits_excited)
    Y1 = np.mean(calibration_ground)
    print Y1, Y2, Y3, Y4


    Igg = 0.8970689
    Ieg = 0.0641417
    Ige = 0.0362008
    Iee = 0.0025884


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


    rd = y1s[12:]
    bl = y2s[12:]
    gr = y3s[12:]
    yw = y4s[12:]

#
#
#
#    
#    y_vector = [rd, gr, bl, yw]
#
#
    V_matrix = np.matrix([[Vgg, Vge, Veg, Vee], [Vge, Vgg, Vee, Veg], 
                          [Veg, Vee, Vgg, Vge], [Vee, Veg, Vge, Vgg]])
    V_fixed=V_matrix
#    P = np.dot(np.linalg.inv(V_matrix), y_vector)  #those are already our real populations 
##    print('P:', np.abs(P))
##    print(np.real(P))
#
####    
#    Pgg = np.transpose(P[0])
#    Pgg= Pgg.A1    
#
#
#
#fig2, axes2 = plt.subplots(2)
#axes2[0].plot(xs[12:], np.real(Pgg))
#axes2[0].plot(xs[12:], np.real(Pg1*Pg2), color='r')
#axes2[1].plot(xs[12:], np.imag(Pgg))
#
#plt.close()#
##rndmben0.analyze(data = data)
##
##rndmben_result0.append(rndmben0.get_ys())
#Pg_cplx1.append(np.real(Pgg))
##
##fig = rndmben0.fig
##
##
#pl.show()
#
#
#
#
#
#
#ys = data
#print(ys)
#
#
#
#
#
#pl.show()
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


















if 0:
    def RB_fit(Pg_cplx, xs,  label='', F_final=0.5, F_init=1.0, fig=None):    #fitting the averaged data of this run
        average_data= np.real(np.mean(Pg_cplx, axis=0))
        std = np.std(np.real(Pg_cplx), axis = 0)
    
        ys  = average_data
        err = std/np.sqrt(len(Pg_cplx))
    
        def exp_decay(params, x, data):
            est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
            return (data-est)
    
        def exp_decay2(params, x):
            est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
            return est
    
        params=lmfit.Parameters()
        params.add('amplitude', value=F_init-F_final, vary=True)
        params.add('ofs', value=F_final, vary=False)
        params.add('tau', value=len(xs))
        result= lmfit.minimize(exp_decay, params, args=(xs,ys))
        lmfit.report_fit(result.params)
        EPCZ = (1-F_final-(1-F_final)*np.exp(-1.0/result.params['tau']))
        print ("EPCZ: %f" %(EPCZ))
        label = label+"EPCZ: %.3f" %(EPCZ)
    
    #
    #    if fig==None:
    #        fig, ax=plt.subplots(1)
    #    else:
    #        ax = fig.axes[0]
        plt.plot(xs, exp_decay2(result.params,xs), markersize =4)
        plt.errorbar(xs,ys,err, markersize=2, linestyle='None', capsize=2, color='black')
        plt.plot(xs,ys, 'o', markersize=3, linestyle='None', label=label)#color='magenta')
#        plt.text(12, 0.80, 'EPC: 0.076')
    #    ax.plot(xs,np.transpose(np.real(np.mean(Pg_cplx, axis=0))), '.', markersize=3, linestyle='None')
    
        plt.ylabel('Average fidelity')
        plt.xlabel('Number of Cliffords')
    #    fig.axes[0].legend(loc=0)
    #    
        return fig
    
    
    
    
    xs=np.linspace(1,15,15)
    RB_fit(Pg_cplx0, xs, F_final=0.25, F_init=1-0.1)
    
    
    
    
    
    
    
    
    
    



#hdf5_name = '20190204 Cooldown.hdf5'
#date = '20201026'

#timetable = ['012646','012937','013226','013515','014052','014340','014626','014914','015201','015448','015741','020027','020317','020856', '021146','021440','021732','022025','025424','022315','022604','022854','023144','023433','023723','024013','024303','024554','024846','025714','030006','030257','013804','020606']
#timetable = ['012813','013100','013350','013639','013928','014215','014503','014750','015036','015325','015616','015904','020153','020441', '020731','021020','021310','021606','021858','022150','022439','022728','023019','023308','023723','023558','023848','024138','024428','024720','025010','025300','025548', '025840', '030132', '030423']



#    hdf5_name = '\Fluxonium31october_copy.hdf5'
#    date = '20201102'
#    
#    #non interleaved
#    timetable1 = ['181030','181344','181658','182008','182318','182626','182934','183243','183552','183901',
#                 '184210','184518','184827','185134','185443','185753','190101','190410','190719','191028',
#                 '191336','191645','191956','192307','192619','192929','193239', '193550', '193901', '194211',
#                 '194522','194833','195145','195456','195806','200116', '200427','200737','201053', '201408', '202339', '202650', 
#                 '202959', '203310', '203619','203930', '204239', '204550', '204900', '205210', '205521', 
#                 '205831', '210141', '210451', '210801', '211111', '211420', '211730', '212040', '212349', 
#                 '212658', '213011', '213325', '213639', '213953']
#    
#    
#    #interleaved with CZ
#    
#    timetable2 = ['181207', '181521', '181833', '182143', '182452', '182800', '183108', '183417', '183727',
#                  '184035', '184343', '184652', '185001',  '185308', '185617', '185927', '190235', '190544',
#                  '190853', '191202', '191510','191820', '192131' ,'192443', '192754' , '193104', '193414',
#                  '193725', '194036', '194347', '194657', '195008' , '195320', '195631', '195941',
#                  '200252', '200602', '200915', '201230','201545', '202515', '202824', '203134', '203445',
#                  '203755','204104','204414','204724','205035','205345','205656', '210006', '210316',
#                  '210625', '210935', '211245','211554','211904', '212214', '212523', '212833', '213147' ,
#                  '213502','213816', '214131']
#    
#    
