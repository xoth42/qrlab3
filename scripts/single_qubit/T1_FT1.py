from __future__ import division
import mclient
reload(mclient)
import numpy as np
import matplotlib.pyplot as plt
from pulseseq import sequencer, pulselib
import matplotlib as mpl
import math as math
import time
import datetime

import os
os.chdir(r'c:\qrlab')

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
#readout_info = mclient.get_readout_info()

'''This script can run the T1/FT1 correlation measurement, for either static flux or if you want to switch flux.

Each one requires a little bit of manual setup before just blindly running the scripts below.
For the static flux, you need to:
    a) tune current to find f_max for your qubit
    b) tune up all your pulses, this includes finding w_ge and w_ef accurately, and the respective pi amps.
    c) Set the qubit-related values in your create_instruments file and restart a new console. DO NOT have
        the GUI open in the background when you go to run this long measurement.
        
For the switching flux, you need to do the steps above for static flux PLUS:
    a) tune current to find the point where w_ge is equal to w_ef at the f_max point. This will be your 2nd flux bias location
    b) find your pi_amp here for w_ge, it may be slightly different than at the f_max point.
    c) do a RO spectroscopy to find if your cavity frequency has shifted slightly at this different flux bias
    d) set the appropriate generator frequencies, currents, and pi_amps for each measurement in the script below
'''


if 1: # T1_FT1 static flux
    from scripts.single_qubit import T1measurement, FT1measurement, T1_FT1measurement, rabi
    N = 3000 # number of full curves you want to take for each T1 and FT1
#    dig.set_naverages(2000)
    '''Create all your empty arrays to save fit parameters in'''
    t1_result = np.zeros(N)
    t1_err = np.zeros(N)
    t1_ofs = np.zeros(N)
    t1_ofs_err = np.zeros(N)
    t1_amp = np.zeros(N)
    t1_amp_err = np.zeros(N)
    ft1_result = np.zeros(N)
    ft1_err = np.zeros(N)
    ft1_ofs = np.zeros(N)
    ft1_ofs_err = np.zeros(N) 
    ft1_amp = np.zeros(N)
    ft1_amp_err = np.zeros(N)
    '''Set the delay points you would like to use. It's a good idea to tweak these manually a bit to
    minimize the errors on your fit parameters'''
    delays = np.concatenate((np.logspace(1, 3, num=3, endpoint=False), 
                             np.logspace(3, 4, num=3, endpoint=False), 
                             np.logspace(4, 5, num=21)))
    '''Just helps with bookkeeping later on during data analysis'''
    start_time = str(datetime.datetime.now())
    start_time = start_time[5:7] + start_time[8:10] + start_time[11:13] + start_time[14:16] + start_time[17:19]
    for i in range(N):
        print '###############'
        print i
        print '##############'
        '''Do the T1 measurement and save the fit parameters'''
        t1 = T1measurement.T1Measurement(qubit_info, delays, double_exp=False, generate=True, plot_seqs=False)
        t1.measure()
        t1_result[i] = t1.fit_params['tau'].value/1000
        t1_err[i] = t1.fit_params['tau'].stderr/1000
        t1_ofs[i] = t1.fit_params['ofs'].value
        t1_ofs_err[i] = t1.fit_params['ofs'].stderr
        t1_amp[i] = t1.fit_params['amplitude'].value
        t1_amp_err[i] = t1.fit_params['amplitude'].stderr
        plt.close()
        
        '''Do the FT1 measurement and save the fit parameters'''
        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, delays, generate=True)
        ft1.measure_keysight()
        ft1_result[i] = ft1.fit_params['tau'].value/1000
        ft1_err[i] = ft1.fit_params['tau'].stderr/1000
        ft1_ofs[i] = ft1.fit_params['ofs'].value
        ft1_ofs_err[i] = ft1.fit_params['ofs'].stderr
        ft1_amp[i] = ft1.fit_params['amplitude'].value
        ft1_amp_err[i] = ft1.fit_params['amplitude'].stderr
        plt.close()
#    for i in range(16000):
#        print '###############'
#        print i
#        print '##############'
#        t1_ft1 = T1_FT1measurement.T1_FT1measurement(qubit_info, ef_info, 16e3, 10e3, generate=True)
#        t1_ft1.measure_keysight()
#        plt.close()
        
#        now = datetime.datetime.now()
#        date = str(now)[5:7] + str(now)[8:10]
#        hour = str(now)[11:13]
#        minute = str(now)[14:16]
#        second = str(now)[17:19]
        
#    plt.figure()
#    plt.plot(range(len(t1_decay)), t1_decay, label='|e> decay')
#    plt.plot(range(len(ft1_decay)), ft1_decay, label='|f> decay')
#    plt.xlabel('Measurement iterations')
#    plt.ylabel('lifetime (us)')
#    plt.legend(loc='upper right')
#    
    '''These are just showing you how good your fits were for this run'''
    print('Average percent error on %.0f T1 measurements was %.03f:' %(int(N), np.average(t1_err/t1_result)))
    print('Average percent error on %.0f FT1 measurements was %.03f:' %(int(N), np.average(ft1_err/ft1_result)))
    
    '''Plot the data'''
    plt.figure()
    plt.errorbar(range(len(t1_result)), t1_result, yerr = t1_err, label='|e> decay')
    plt.errorbar(range(len(ft1_result)), ft1_result, yerr = ft1_err, label='|f> decay')
    plt.xlabel('Measurement iterations')
    plt.ylabel('lifetime (us)')
    plt.legend(loc='upper right')
    
    '''More bookkeeping'''
    end_time = str(datetime.datetime.now())
    end_time = end_time[5:7] + end_time[8:10] + end_time[11:13] + end_time[14:16] + end_time[17:19]
    
    '''Save the data for later analysis'''
    save_filepath = 'C:/Users/wanglab/Documents/DRosenstock/t1ft1/full curve results/'
    save_string = str('start') + str(start_time) + str('end') + str(end_time)
    np.savetxt(save_filepath + str(save_string) + 'results.txt',
               np.column_stack((t1_result, t1_err, t1_ofs, t1_ofs_err, t1_amp, t1_amp_err, ft1_result, ft1_err, ft1_ofs, ft1_ofs_err, ft1_amp, ft1_amp_err)),
               header = 
               
               'T1 result, T1 error, T1 offset, offset err, T1 amplitude, amp err, FT1 result, FT1 error, FT1 offset, offset err, FT1 amplitude, amp err')
    
if 1: # T1_FT1 switching flux
    from scripts.single_qubit import T1measurement, FT1measurement, T1_FT1measurement, rabi
    N = 3000 # number of full curves you want to take for each T1 and FT1
    alz.set_naverages(2000)
    '''Create all your empty arrays to save fit parameters in'''
    t1_result = np.zeros(N)
    t1_err = np.zeros(N)
    t1_ofs = np.zeros(N)
    t1_amp = np.zeros(N)
    ft1_result = np.zeros(N)
    ft1_err = np.zeros(N)
    ft1_ofs = np.zeros(N)
    ft1_amp = np.zeros(N)
    '''Set the delay points you would like to use. It's a good idea to tweak these manually a bit to
    minimize the errors on your fit parameters'''
    t1delays = np.concatenate((np.logspace(1, 3, num=3, endpoint=False), 
                             np.logspace(3, 4, num=3, endpoint=False), 
                             np.logspace(4, 5.2, num=21)))
    ft1delays = np.concatenate((np.logspace(1, 3, num=3, endpoint=False), 
                             np.logspace(3, 4, num=3, endpoint=False), 
                             np.logspace(4, 5, num=21)))
    '''Create variables for instrument objects since we will have to change them in between measurements'''
    ge = mclient.instruments['qubit1ge']
    ef = mclient.instruments['qubit1ef']

    Yoko = mclient.instruments['Yoko']
    qbrick = mclient.instruments['geFG']
    RObrick = mclient.instruments['RObrick']
    refbrick = mclient.instruments['refFG']
    
    '''These are the values you need to do the T1 measurement at the non f_max flux bias point'''
    Yoko.do_set_current(1.068)
    qbrick.set_frequency(4952.36e6)
    RObrick.set_frequency(8301.6e6)
    refbrick.set_frequency(8301.6e6+50e6)
    
    ef.set('deltaf', -378.50e6)
    ge.set('pi_amp', 0.24763)
    ef.set('pi_amp', 0.18491)
    
    start_time = str(datetime.datetime.now())
    start_time = start_time[5:7] + start_time[8:10] + start_time[11:13] + start_time[14:16] + start_time[17:19]
    for i in range(N):
        print '###############'
        print i
        print '##############'
        '''Do the T1 measurement and save the fit parameters'''
        t1 = T1measurement.T1Measurement(qubit_info, t1delays, double_exp=False, generate=True, plot_seqs=False)
        t1.measure_keysight()
        t1_result[i] = t1.fit_params['tau'].value/1000
        t1_err[i] = t1.fit_params['tau'].stderr/1000
        t1_ofs[i] = t1.fit_params['ofs'].value
        t1_amp[i] = t1.fit_params['amplitude'].value
        plt.close()
        
        '''Switch your instruments to the values needed to do the FT1 measurement at f_max'''
        Yoko.do_set_current(0.245)
        qbrick.set_frequency(5230.86e6)
        RObrick.set_frequency(8302.36e6)
        refbrick.set_frequency(8302.36e6+50e6)
        ge.set('pi_amp', 0.2325)
        
        '''Do the FT1 measurement and save the fit parameters'''
        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, ft1delays, generate=True)
        ft1.measure_keysight()
        ft1_result[i] = ft1.fit_params['tau'].value/1000
        ft1_err[i] = ft1.fit_params['tau'].stderr/1000
        ft1_ofs[i] = ft1.fit_params['ofs'].value
        ft1_amp[i] = ft1.fit_params['amplitude'].value
        plt.close()
        
        '''Switch instrument settings back to be able to measure T1 again'''
        Yoko.do_set_current(1.068)
        qbrick.set_frequency(4952.36e6)
        RObrick.set_frequency(8301.6e6)
        refbrick.set_frequency(8301.6e6+50e6)
        ge.set('pi_amp', 0.24763)
        
#    for i in range(16000):
#        print '###############'
#        print i
#        print '##############'
#        t1_ft1 = T1_FT1measurement.T1_FT1measurement(qubit_info, ef_info, 16e3, 10e3, generate=True)
#        t1_ft1.measure_keysight()
#        plt.close()
        
#        now = datetime.datetime.now()
#        date = str(now)[5:7] + str(now)[8:10]
#        hour = str(now)[11:13]
#        minute = str(now)[14:16]
#        second = str(now)[17:19]
        
#    plt.figure()
#    plt.plot(range(len(t1_decay)), t1_decay, label='|e> decay')
#    plt.plot(range(len(ft1_decay)), ft1_decay, label='|f> decay')
#    plt.xlabel('Measurement iterations')
#    plt.ylabel('lifetime (us)')
#    plt.legend(loc='upper right')
#    
    '''These are just showing you how good your fits were for this run'''
    print('Average percent error on %.0f T1 measurements was %.03f:' %(int(N), np.average(t1_err/t1_result)))
    print('Average percent error on %.0f FT1 measurements was %.03f:' %(int(N), np.average(ft1_err/ft1_result)))
    
    '''Plot the data'''
    plt.figure()
    plt.errorbar(range(len(t1_result)), t1_result, yerr = t1_err, label='|e> decay')
    plt.errorbar(range(len(ft1_result)), ft1_result, yerr = ft1_err, label='|f> decay')
    plt.xlabel('Measurement iterations')
    plt.ylabel('lifetime (us)')
    plt.legend(loc='upper right')
    
    end_time = str(datetime.datetime.now())
    end_time = end_time[5:7] + end_time[8:10] + end_time[11:13] + end_time[14:16] + end_time[17:19]
    
    save_filepath = 'C:/Users/wanglab/Documents/DRosenstock/t1ft1/full curve results/'
    save_string = str('start') + str(start_time) + str('end') + str(end_time)
    np.savetxt(save_filepath + str(save_string) + 'results.txt',
               np.column_stack((t1_result, t1_err, t1_ofs, t1_amp, ft1_result, ft1_err, ft1_ofs, ft1_amp)),
               header = 
               'T1 result, T1 error, T1 offset, T1 amplitude, FT1 result, FT1 error, FT1 offset, FT1 amplitude')

if 0: # T1 Loop
    from scripts.single_qubit import T1measurement
    dig.set_naverages(5000)
    t1_result = []
    tau_err = []
    v_g = []
    g_err = []
    v_e = []
    e_err = []
#    times = []
    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 160e3, 151), double_exp=False, generate=True, plot_seqs=False)
    t1.measure()
    t1_result.append(t1.result_params['tau'].value/1000)
    tau_err.append(t1.result_params['tau'].stderr/1000)
    v_g.append(t1.result_params['ofs'].value)
    g_err.append(t1.result_params['ofs'].stderr)
    v_e.append(t1.result_params['ofs'].value + t1.result_params['amplitude'].value)
    e_err.append(t1.result_params['ofs'].stderr + t1.result_params['amplitude'].stderr)
#    times.append(str(datetime.datetime.now())[11:19])
    ofs = t1.result_params['ofs'].value
    amplitude = t1.result_params['amplitude'].value
    
    for i in range(99):
        t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 160e3, 151), double_exp=False, force_ofs=None,
                                         force_amplitude=None, generate=False, plot_seqs=False)
        t1.measure()
        now = datetime.datetime.now()
        hour = int(str(now)[11:13])
        minute = int(str(now)[14:16])
        second = int(str(now)[17:19])
        print 'This measurement took place at %.f:%.f:%.f' %(hour, minute, second)
        t1_result.append(t1.result_params['tau'].value)
        tau_err.append(t1.result_params['tau'].stderr)
        v_g.append(t1.result_params['ofs'].value)
        g_err.append(t1.result_params['ofs'].stderr)
        v_e.append(t1.result_params['ofs'].value + t1.result_params['amplitude'].value)
        e_err.append(t1.result_params['ofs'].stderr + t1.result_params['amplitude'].stderr)
#        times.append(str(datetime.datetime.now())[11:19])
        plt.close()
        
#    ticks = range(len(times))
    plt.figure()
#    plt.xticks(ticks, times)
#    plt.errorbar(range(len(t1_result)), t1_result, yerr = tau_err)
    plt.plot(range(len(t1_result)), t1_result)
    plt.xlabel('Measurement iterations')
    plt.ylabel('T1 lifetime')
    
    plt.figure()
#    plt.xticks(ticks, times)
    plt.errorbar(range(len(v_g)), v_g, yerr = g_err, label='|g>')
    plt.errorbar(range(len(v_e)), v_e, yerr = e_err, label='|e>')
    plt.legend(loc='upper right')
    plt.xlabel('Measurement iterations')
    plt.ylabel('Amplitude (AU)')
    
if 0: # FT1 Loop
    from scripts.single_qubit import FT1measurement
    alz.set_naverages(50000)
    ft1_result = []
    tau_err = []
    v_g = []
    g_err = []
    v_eq = []
    eq_err = []
#    times = []
    ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.linspace(0, 120e3, 151), generate=True)
    ft1.measure()
    ft1_result.append(ft1.fit_params['tau'].value/1000)
    tau_err.append(ft1.fit_params['tau'].stderr/1000)
    v_g.append(ft1.fit_params['ofs'].value)
    g_err.append(ft1.fit_params['ofs'].stderr)
    v_eq.append(ft1.fit_params['ofs'].value + ft1.fit_params['amplitude'].value)
    eq_err.append(ft1.fit_params['ofs'].stderr + ft1.fit_params['amplitude'].stderr)
#    times.append(str(datetime.datetime.now())[11:19])
    ofs = ft1.fit_params['ofs'].value
    amplitude = ft1.fit_params['amplitude'].value
    
    for i in range(99):
        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.linspace(0, 120e3, 151), generate=True)
        ft1.measure()
        now = datetime.datetime.now()
        hour = int(str(now)[11:13])
        minute = int(str(now)[14:16])
        second = int(str(now)[17:19])
        print 'This measurement took place at %.f:%.f:%.f' %(hour, minute, second)
        ft1_result.append(ft1.fit_params['tau'].value)
        tau_err.append(ft1.fit_params['tau'].stderr)
        v_g.append(ft1.fit_params['ofs'].value)
        g_err.append(ft1.fit_params['ofs'].stderr)
        v_eq.append(ft1.fit_params['ofs'].value + ft1.fit_params['amplitude'].value)
        eq_err.append(ft1.fit_params['ofs'].stderr + ft1.fit_params['amplitude'].stderr)
#        times.append(str(datetime.datetime.now())[11:19])
        plt.close()
        
#    ticks = range(len(times))
    plt.figure()
#    plt.xticks(ticks, times)
#    plt.errorbar(range(len(ft1_result)), ft1_result, yerr = tau_err)
    plt.plot(range(len(ft1_result)), ft1_result)
    plt.xlabel('Measurement iterations')
    plt.ylabel('FT1 lifetime')
    
    plt.figure()
#    plt.xticks(ticks, times)
    plt.errorbar(range(len(v_g)), v_g, yerr = g_err, label='|g>')
    plt.errorbar(range(len(v_eq)), v_eq, yerr = eq_err, label='|g>+|e>/2')
    plt.legend(loc='upper right')
    plt.xlabel('Measurement iterations')
    plt.ylabel('Amplitude (AU)')
    
    
if 0: #T1_FT1 toggle flux
    from scripts.single_qubit import T1_FT1fluxmeasurement
    for i in range(1):
        t1_ft1_flux = T1_FT1fluxmeasurement.T1_FT1fluxmeasurement(qubit_info, ef_info, qubit2_info, 6.5e3, 5.5e3, histogram=False, generate=True)
        #t1_ft1_flux.play_sequence()
        t1_ft1_flux.measure()
        
if 0: #T1_FT1 toggle flux
    from scripts.single_qubit import Yoko_exttrig_testing
    for i in range(1):
        Yoko_test = Yoko_exttrig_testing.Yoko_test(qubit_info, ef_info, qubit2_info, 6.5e3, 5.5e3, histogram=False, generate=True)
        #t1_ft1_flux.play_sequence()
        Yoko_test.measure()