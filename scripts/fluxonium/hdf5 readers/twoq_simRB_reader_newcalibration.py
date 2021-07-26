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
    os.system(r'C:\qrlab-3\start.bat')
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
    date = '20201109'
    
    #non interleaved
    timetable1 = ['164639','165026','165412','165759','170147','170533','170921','171310','171659',
                  '172051']
    
    
    
    experiment = 'TwoQubit_RB'
    
    ''' Primary x axis and secondary if 2d'''
    x_key = 'Cliffords'
    #x2_key = 'powers'
    
    
    time = timetable1[9]
    f = h5.File(filepath + hdf5_name, 'r')
    exp = f['/' + date + '/' + time + '_' + experiment]    
    rndmben0 = TwoQ_RB_ebru_temp.TwoQubit_RB(gate_info2, gate_info1, ZZ_info, cancel_info, num_cal_points=3, N_cliffords=35, 
                                  plot_seqs=False, category='all', generator='CZ',
                                  find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True, use_lookup_table=True,
                                  singleQ_phases=[-2.685,-1.366], seq=None, proj_func='phase')
    
    data = exp['avg'].value
    
    ys=data
    
    
    xs = np.linspace(-2, 80, 83)
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

if 0: #new method: getting V matrix directly with the initial populations
    Y3 = np.mean(calibration_qubit1_excited)
    Y2 = np.mean(calibration_qubit2_excited)
    Y4 = np.mean(calibration_bothqubits_excited)
    Y1 = np.mean(calibration_ground)
    print Y1, Y2, Y3, Y4


    Igg = 0.8870531225897488
    Ieg = 0.08575165073103701
    Ige = 0.024797997919957005
    Iee = 0.002397228759257298


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
##    print('P:', np.abs(P))
##    print(np.real(P))
#
####    
    Pgg = np.transpose(P[0])
    Pgg= Pgg.A1    
    Pge =  np.transpose(P[1])
    Pge = Pge.A1

    Peg =  np.transpose(P[2])
    Peg = Peg.A1

    Pg1 = Pgg + Pge
    Pg2 = Pgg + Peg

    Pgg0.append(Pgg)
    Pg10.append(Pg1)
    Pg20.append(Pg2)
















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
    
    
    
    
    xs=np.linspace(1,80,80)
    RBfig = RB_fit(Pgg0, xs, F_final=0.25, F_init=1, label='Fidelity of |gg>,  total ')
    plt.title('Simultaneous 1Q randomized benchmarking',fontsize=12)
    RB_fit(Pg20, xs, F_final=0.50, F_init=1, label='Fidelity of |g> for Qubit1, ', fig=RBfig)
    RB_fit(Pg10, xs, F_final=0.50, F_init=1, label='Fidelity of |g> for Qubit2, ', fig=RBfig)
    bla
   
    
    
    
#Major RB data
#    ''' Path to the .hdf5 file '''
#    filepath = 'C:\Users\wanglab\Desktop\hdf5_copies'
#    hdf5_name = '\Fluxonium31october_copy_2.hdf5'
#    date = '20201108'
#    
#    #non interleaved
#    timetable1 = ['123458','124013','124533', '125053', '125613', '130128', '130651', 
#                  '131216', '131742','132307', '132830', '133352', '133917', '134442', '135007',
#                  '190018', '190510', '191004', '191500', '191954', '192451', '192948', '193443',
#                  '193940', '194435', '194929', '195424', '195921', '200418', '200912', '201410',
#                  '201906', '202401', '202858', '203356', '203854', '204351', '204850', '205346', 
#                  '205848', '210347', '210844', '211342', '211839', '212336', '212832', 
#                  '213330', '213831', '214330', '214830', '215327', '215826', '220323', '220819', 
#                  '221316', '221815', '222312', '222810', '223306', '223806', '224758', '230255', 
#                  '231257']
#    
#    timetable2 = ['123734', '124251', '124813', '125332', '125850', '130407', '130932',
#                  '131458', '132024', '132548', '133109', '133633', '134200', '134724', '135247',
#                  '190243', '190735', '191231', '191726', '192222', '192719', '193215', '193709',
#                  '194205', '194701', '195155', '195653', '200149', 
#                  '200644', '201139', '201636', '202133', '202630', '203127', 
#                  '203624', '204123', '204620', '205116', '205616', '210115', '210615', '211112',
#                  '211610', '212106', '212603', '213102', '213600', '214100', 
#                  '214559', '215057', '215557', '220053', '220550', '221047', '221545', '222042', 
#                  '222538', '223037', '223534', '224033', 
#                  '225025', '230524', 
#                  '231526']
#
    
    
    



























    
    
    
#    date = '20201106'
#    
#    #non interleaved
#    timetable1 = ['204951','205014','205037','205100','205122','205145','205208','205230','205253','205316']
#    



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
