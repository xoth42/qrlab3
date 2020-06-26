# -*- coding: utf-8 -*-
"""
Created on Mon Sep 09 17:54:52 2019

@author: Wang_Lab
"""
import mclient
reload(mclient)
import numpy as np
#matplotlib.rcParams['backend'] = 'Qt4Agg'
#matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
#from t1t2_plotting import smart_T1_delays
import os
import time
import datetime
#Yingying
if 1: #sweep field to do T1, T2 measurement


    from scripts.single_qubit import T1measurement, T2measurement

#    magnet = mclient.instruments['Magnet']
#    qubits = mclient.get_qubits()
#    qubit_info = mclient.get_qubit_info('qubit1ge')    
#    qubit1ge = mclient.instruments['qubit1ge']
#    
#    dig = mclient.instruments['dig']
#
#    SCqubit = mclient.instruments['SCqubit']
#    ROFG = mclient.instruments['ROFG']
#    refbrick = mclient.instruments['SCref']
#    
#    readout_info = mclient.get_readout_info('readout')
#    
#    AWG1 = mclient.instruments['AWG1']
    
    
    
    '''Create all your empty arrays to save fit parameters in'''    
    m_list = np.linspace(0,0.05,10)
    
    time_of_m = np.zeros(len(m_list))
    t1_result = np.zeros(len(m_list))
    t1_err = np.zeros(len(m_list))
    t1_ofs = np.zeros(len(m_list))
    t1_ofs_err = np.zeros(len(m_list))
    t1_amp = np.zeros(len(m_list))
    t1_amp_err = np.zeros(len(m_list))
    t2_result = np.zeros(len(m_list))
    t2_err = np.zeros(len(m_list))
    t2_ofs = np.zeros(len(m_list))
    t2_ofs_err = np.zeros(len(m_list))
    t2_amp = np.zeros(len(m_list))
    t2_amp_err = np.zeros(len(m_list))
    '''Just helps with bookkeeping later on during data analysis'''
    start_time = list(str(datetime.datetime.now())[:19])
    start_time[13] = '-'
    start_time[16] = '-'
    for i,m in enumerate(m_list):
#        magnet.do_set_field(m)
        time.sleep(5)       
        time_of_m[i] = int(time.strftime('%H%M%S'))

        print '###############'
        print m,'T   T1'
        print '##############'
        '''Do the T1 measurement and save the fit parameters'''
        t1 = T1measurement.T1Measurement(qubit_info,  np.linspace(0, 20e3, 101), 
                                         double_exp=False, generate=True, plot_seqs=False)
        t1.measure_keysight()
        t1_result[i] = t1.fit_params['tau'].value/1000
        t1_err[i] = t1.fit_params['tau'].stderr/1000
        t1_ofs[i] = t1.fit_params['ofs'].value
        t1_ofs_err[i] = t1.fit_params['ofs'].stderr
        t1_amp[i] = t1.fit_params['amplitude'].value
        t1_amp_err[i] = t1.fit_params['amplitude'].stderr
        plt.close()
        
        '''Do the t2 measurement and save the fit parameters'''
        print '###############'
        print m,'T   T2'
        print '##############'
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 4e3, 101), detune=2e6, double_freq=False, generate=True, postseq=None)
        t2.measure_keysight()
        t2_result[i] = t2.fit_params['tau'].value/1000
        t2_err[i] = t2.fit_params['tau'].stderr/1000
        t2_ofs[i] = t2.fit_params['ofs'].value
        t2_ofs_err[i] = t2.fit_params['ofs'].stderr
        t2_amp[i] = t2.fit_params['amp'].value
        t2_amp_err[i] = t2.fit_params['amp'].stderr
        
        plt.close()

    '''More bookkeeping'''
    end_time = list(str(datetime.datetime.now())[:19])
    end_time[13] = '-'
    end_time[16] = '-'
    
#    '''These are just showing you how good your fits were for this run'''
#    print('Average percent error on %.0f T1 measurements was %.03f:' %(int(N), np.average(t1_err/t1_result)))
#    print('Average percent error on %.0f T2 measurements was %.03f:' %(int(N), np.average(t2_err/t2_result)))
    
    '''Save the data for later analysis'''
    main_filepath = 'C:/Users/Wang_Lab/Documents/yingying/08272019cooldown/field sweep//'
    time_stamp = start_time + list(str(' to ')) + end_time
    save_filepath = main_filepath + ''.join(time_stamp) + '/'
    
    if not os.path.exists(save_filepath):
        os.makedirs(save_filepath)
        
    np.savetxt(save_filepath + 'results.txt',
               np.column_stack((m_list,time_of_m, t1_result, t1_err, t1_ofs, t1_ofs_err, t1_amp, t1_amp_err, t2_result, t2_err, t2_ofs, t2_ofs_err, t2_amp, t2_amp_err)),
               header = 
               
               'field,time_of_field, T1 result, T1 error, T1 offset, T1 offset error, T1 amplitude, T1 amplitude error, T2 result, T2 error, T2 offset, T2 offset error, T2 amplitude, T2 amplitude error')
    
    np.savetxt(save_filepath + 'notes.txt', [0],
               header = 
               'm_list = np.linspace(' + str(m_list[0]) +',' + str(m_list[-1]) + ',' + str(len(m_list)) + ')'  +
               ', num_averages = ' + str(dig.get_naverages()) +
               ', rep_rate = ' + str(dig.do_get_trigger_period()) + str(' us') + 
               ', RO power = ' + str(RObrick.get_power()) + str(' dBm') + 
               ', RO frequency = ' + str(RObric.get_frequency()/1e6) + str(' MHz') + 
               ', w_ge = ' + str((qubitbrick.do_get_frequency() + qubit1ge.get('deltaf'))/1e6) + str(' MHz') +
               ', pulse_len = ' + str(4.0*qubit1ge.get('w')) + str(' ns'))
    
    '''Plot the data'''
    plt.figure()
    plt.errorbar(m_list, t1_result, yerr = t1_err,fmt ='o', label='t1')
    plt.errorbar(m_list, t2_result, yerr = t2_err,fmt ='o', label='t2')
    plt.xlabel('field(T)')
#    plt.xlabel('different measurement')
    plt.ylabel('lifetime (us)')
    plt.legend(loc='upper right')
    plt.savefig(save_filepath + 'decays.png')
    
#    magnet.do_set_field(0)