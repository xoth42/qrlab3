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
qubit2_info = mclient.get_qubit_info('qubit2ge')
ef_info = mclient.get_qubit_info('qubit1ef')
alz = mclient.instruments['alazar']


ge = mclient.instruments['qubit1ge']
ef = mclient.instruments['qubit1ef']
ge2 = mclient.instruments['qubit2ge']

yoko = mclient.instruments['yoko']
Qbrick = mclient.instruments['Qbrick']
RObrick = mclient.instruments['RObrick']
refbrick = mclient.instruments['refbrick']

readout_info = mclient.get_readout_info('readout')
ro = mclient.instruments['readout']

AWG1 = mclient.instruments['AWG1']


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


if 0: # T1_FT1 static flux
    from scripts.single_qubit import T1measurement, FT1measurement, rabi
    for j in range(100):
        N = 60 # number of full curves you want to take for each T1 and FT1
        alz.set_naverages(1500)
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
                                 np.logspace(4, 5.1, num=21)))
        f_delays = np.concatenate((np.logspace(1, 3, num=3, endpoint=False), 
                                 np.logspace(3, 4, num=3, endpoint=False), 
                                 np.logspace(4, 5, num=21)))
        '''Just helps with bookkeeping later on during data analysis'''
        start_time = list(str(datetime.datetime.now())[:19])
        start_time[13] = '-'
        start_time[16] = '-'
        for i in range(N):
            print '###############'
            print i
            print '##############'
            '''Do the T1 measurement and save the fit parameters'''
            t1 = T1measurement.T1Measurement(qubit_info, delays, double_exp=False, generate=True, plot_seqs=False, proj_func='projection')
            t1.measure()
            t1_result[i] = t1.fit_params['tau'].value/1000
            t1_err[i] = t1.fit_params['tau'].stderr/1000
            t1_ofs[i] = t1.fit_params['ofs'].value
            t1_ofs_err[i] = t1.fit_params['ofs'].stderr
            t1_amp[i] = t1.fit_params['amplitude'].value
            t1_amp_err[i] = t1.fit_params['amplitude'].stderr
            plt.close()
            
            '''Do the FT1 measurement and save the fit parameters'''
            ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, f_delays, generate=True, proj_func='projection')
            ft1.measure()
            ft1_result[i] = ft1.fit_params['tau'].value/1000
            ft1_err[i] = ft1.fit_params['tau'].stderr/1000
            ft1_ofs[i] = ft1.fit_params['ofs'].value
            ft1_ofs_err[i] = ft1.fit_params['ofs'].stderr
            ft1_amp[i] = ft1.fit_params['amplitude'].value
            ft1_amp_err[i] = ft1.fit_params['amplitude'].stderr
            plt.close()
    
        '''More bookkeeping'''
        end_time = list(str(datetime.datetime.now())[:19])
        end_time[13] = '-'
        end_time[16] = '-'
        
        '''These are just showing you how good your fits were for this run'''
        print('Average percent error on %.0f T1 measurements was %.03f:' %(int(N), np.average(t1_err/t1_result)))
        print('Average percent error on %.0f FT1 measurements was %.03f:' %(int(N), np.average(ft1_err/ft1_result)))
        
        '''Save the data for later analysis'''
        main_filepath = 'C:/Users/wanglab/Documents/DRosenstock/t1ft1/full curve results/static_flux/'
        time_stamp = start_time + list(str(' to ')) + end_time
        save_filepath = main_filepath + ''.join(time_stamp) + '/'
        
        if not os.path.exists(save_filepath):
            os.makedirs(save_filepath)
            
        np.savetxt(save_filepath + 'results.txt',
                   np.column_stack((t1_result, t1_err, t1_ofs, t1_ofs_err, t1_amp, t1_amp_err, ft1_result, ft1_err, ft1_ofs, ft1_ofs_err, ft1_amp, ft1_amp_err)),
                   header = 
                   
                   'T1 result, T1 error, T1 offset, T1 offset error, T1 amplitude, T1 amplitude error, FT1 result, FT1 error, FT1 offset, FT1 offset error, FT1 amplitude, FT1 amplitude error')
        
        np.savetxt(save_filepath + 'notes.txt', [0],
                   header = 
                   'N = ' + str(N) +
                   ', num_averages = ' + str(alz.get_naverages()) +
                   ', rep_rate = ' + str(dig.do_get_trigger_period()) + str(' us') + 
                   ', n_points = ' + str(len(delays)) +
                   ', RO power = ' + str(RObrick.do_get_power()) + str(' dBm') + 
                   ', RO frequency = ' + str(RObrick.do_get_frequency()/1e6) + str(' MHz') + 
                   ', w_ge = ' + str((qbrick.do_get_frequency() + ge.get('deltaf'))/1e6) + str(' MHz') +
                   ', w_ef = ' + str((qbrick.do_get_frequency() + ef.get('deltaf'))/1e6) + str(' MHz') +
                   ', pulse_len = ' + str(4.0*ge.get('w')) + str(' ns'))
        
        '''Plot the data'''
        plt.figure()
        plt.errorbar(range(len(t1_result)), t1_result, yerr = t1_err, label='|e> decay')
        plt.errorbar(range(len(ft1_result)), ft1_result, yerr = ft1_err, label='|f> decay')
        plt.xlabel('Measurement iterations')
        plt.ylabel('lifetime (us)')
        plt.legend(loc='upper right')
        plt.savefig(save_filepath + 'decays.png')
    
if 0: # T1_FT1 switching flux
    from scripts.single_qubit import T1measurement, FT1measurement, rabi
    for j in range(100):
        N = 60 # number of full curves you want to take for each T1 and FT1
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
        
        t1B_result = np.zeros(N)
        t1B_err = np.zeros(N)
        t1B_ofs = np.zeros(N)
        t1B_amp = np.zeros(N)
        '''Set the delay points you would like to use. It's a good idea to tweak these manually a bit to
        minimize the errors on your fit parameters'''
        t1delays = np.concatenate((np.logspace(1, 3, num=3, endpoint=False), 
                                 np.logspace(3, 4, num=11, endpoint=False), 
                                 np.logspace(4, 4.3, num=6)))
        ft1delays = np.concatenate((np.logspace(1, 3, num=3, endpoint=False), 
                                 np.logspace(3, 4, num=15, endpoint=False), 
                                 np.logspace(4, 4.3, num=11)))
        t1Bdelays = np.concatenate((np.logspace(1, 3, num=3, endpoint=False), 
                                 np.logspace(3, 4, num=11, endpoint=False), 
                                 np.logspace(4, 4.3, num=6)))
        '''Create variables for instrument objects since we will have to change them in between measurements'''
        ge = mclient.instruments['qubit1ge']
        ef = mclient.instruments['qubit1ef']
        ge2 = mclient.instruments['qubit2ge']
    
        Yoko = mclient.instruments['yoko']
        qbrick = mclient.instruments['qbrick']
        RObrick = mclient.instruments['RObrick']
        refbrick = mclient.instruments['SCref']
        
        '''Settings for measuring |e> lifetime detuned from f_max (flux A)'''
        A_current = 3.365
        qubitge_drive_freq_A = 6734.77e6
        RO_freq_A =  8154e6
#        RO_power_A = 10
        
        '''Settings for measuring |f> lifetime at f_max (flux B)'''
        B_current = 0
        qubitge_drive_freq_B = 6734.77e6
        RO_freq_B = 8160.5e6
#        RO_power_B = 10

        
        '''These are the values you need to do the T1 measurement at the non f_max flux bias point'''
        Yoko.do_set_current(A_current)
#        qbrick.set_frequency(qubitge_drive_freq_A)
#        RObrick.set_frequency(RO_freq_A)
#        refbrick.set_frequency(RO_freq_A+50e6)
#        RObrick.set_power(RO_power_A)
#        
#        ef.set('deltaf', -357.75e6)
#        ge.set('pi_amp', 0.228)
#        ef.set('pi_amp', 0.303)
#        ge2.set('pi_amp', 0.44)
#        
#        readout.set('IQg', (-242.16+52.82j))
#        readout.set('IQe', (-30.6+97.2j))
        
#        AWG1.do_set_offset(0.0315, 3)
#        AWG1.do_set_offset(0.0315, 4)
#        AWG1.do_set_amplitude(1.34, 3)
#        ge.set('sideband_phase', 0.05)
        
        start_time = list(str(datetime.datetime.now())[:19])
        start_time[13] = '-'
        start_time[16] = '-'
        Yoko.do_set_output_state(1)
#        alz.set_naverages(2500)
        for i in range(N):
            print '###############'
            print i
            print '##############'
            '''Do the T1 measurement and save the fit parameters'''
            t1 = T1measurement.T1Measurement(qubit2_info, t1delays, double_exp=False, generate=True, plot_seqs=False,
                                             proj_func='amplitude')
            t1.measure()
            t1_result[i] = t1.fit_params['tau'].value/1000
            t1_err[i] = t1.fit_params['tau'].stderr/1000
            t1_ofs[i] = t1.fit_params['ofs'].value
            t1_amp[i] = t1.fit_params['amplitude'].value
            plt.close()
            
            '''Switch your instruments to the values needed to do the FT1 measurement at f_max'''
            Yoko.do_set_current(B_current)
#            qbrick.set_frequency(qubitge_drive_freq_B)
#            RObrick.set_frequency(RO_freq_B)
#            refbrick.set_frequency(RO_freq_B+50e6)
#            RObrick.set_power(RO_power_B)
#            ge.set('pi_amp', 0.237)
#            alz.set_naverages(1500)
            
#            readout.set('IQg', (-177.24+174.58j))
#            readout.set('IQe', (20.15+88.66j))
            
#            AWG1.do_set_offset(0.0321, 3)
#            AWG1.do_set_offset(0.0236, 4)
#            AWG1.do_set_amplitude(1.36, 3)
            
            '''Do the FT1 measurement and save the fit parameters'''
            ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, ft1delays, generate=True,
                                                proj_func='projection')
            ft1.measure()
            ft1_result[i] = ft1.fit_params['tau'].value/1000
            ft1_err[i] = ft1.fit_params['tau'].stderr/1000
            ft1_ofs[i] = ft1.fit_params['ofs'].value
            ft1_amp[i] = ft1.fit_params['amplitude'].value
            plt.close()
            
            '''Do a T1 measurement at f_max'''
            t1 = T1measurement.T1Measurement(qubit_info, t1Bdelays, double_exp=False, generate=True, plot_seqs=False,
                                             proj_func='projection')
            t1.measure()
            t1B_result[i] = t1.fit_params['tau'].value/1000
            t1B_err[i] = t1.fit_params['tau'].stderr/1000
            t1B_ofs[i] = t1.fit_params['ofs'].value
            t1B_amp[i] = t1.fit_params['amplitude'].value
            plt.close()
            
            '''Switch instrument settings back to be able to measure T1 again'''
            Yoko.do_set_current(A_current)
#            qbrick.set_frequency(qubitge_drive_freq_A)
#            RObrick.set_frequency(RO_freq_A)
#            refbrick.set_frequency(RO_freq_A+50e6)
#            RObrick.set_power(RO_power_A)
#            ge.set('pi_amp', 0.464)
#            alz.set_naverages(2000)
            
#            readout.set('IQg', (-242.16+52.82j))
#            readout.set('IQe', (-30.6+97.2j))
            
#            AWG1.do_set_offset(0.0315, 3)
#            AWG1.do_set_offset(0.0315, 4)
            
    
        end_time = list(str(datetime.datetime.now())[:19])
        end_time[13] = '-'
        end_time[16] = '-'
        
        yoko.do_set_output_state(0)
        
        '''These are just showing you how good your fits were for this run'''
        print('Average percent error on %.0f T1 measurements was %.03f:' %(int(N), np.average(t1_err/t1_result)))
        print('Average percent error on %.0f FT1 measurements was %.03f:' %(int(N), np.average(ft1_err/ft1_result)))
        print('Average percent error on %.0f T1(B) measurements was %.03f:' %(int(N), np.average(t1B_err/t1B_result)))
        
        main_filepath = 'C:/Users/wanglab/Documents/DRosenstock/t1ft1/full curve results/switching_flux/'
        time_stamp = start_time + list(str(' to ')) + end_time
        save_filepath = main_filepath + ''.join(time_stamp) + '/'
            
        if not os.path.exists(save_filepath):
            os.makedirs(save_filepath)
        
        np.savetxt(save_filepath + 'results.txt',
                   np.column_stack((t1_result, t1_err, t1_ofs, t1_amp, ft1_result, ft1_err, ft1_ofs, ft1_amp, t1B_result, t1B_err, t1B_ofs, t1B_amp)),
                   header = 
                   'T1 result, T1 error, T1 offset, T1 amplitude, FT1 result, FT1 error, FT1 offset, FT1 amplitude')
        
        np.savetxt(save_filepath + 'notes.txt', [0],
                       header = 
                       'N = ' + str(N) +
                       ', num_averages = ' + str(alz.get_naverages()) +
                       ', rep_rate = ' + str(dig.do_get_trigger_period()) + str(' us') + 
                       ', n_points for T1 = ' + str(len(t1delays)) +
                       ', n_points for FT1 = ' + str(len(ft1delays)) +
                       ', n_points for T1(B) = ' + str(len(t1Bdelays)) +
                       ', RO power (A) = ' + str(RO_power_A) + str(' dBm') +
                       ', RO power (B) = ' + str(RO_power_B) + str(' dBm') +
                       ', RO frequency (A) = ' + str(RO_freq_A/1e6) + str(' MHz') + 
                       ', RO frequency (B) = ' + str(RO_freq_B/1e6) + str(' MHz') + 
                       ', w_ge (A) = ' + str((qubitge_drive_freq_A + ge.get('deltaf'))/1e6) + str(' MHz') +
                       ', w_ge (B) = ' + str((qubitge_drive_freq_B + ge.get('deltaf'))/1e6) + str(' MHz') +
                       ', w_ef (B) = ' + str((qubitge_drive_freq_B + ef.get('deltaf'))/1e6) + str(' MHz') +
                       ', applied current (A) = ' + str(A_current) + str(' mA') + 
                       ', applied current (B) = ' + str(B_current) + str(' mA') + 
                       ', pulse_len = ' + str(4.0*ge.get('w')) + str(' ns'))
        
        '''Plot the data'''
        plt.figure()
        plt.errorbar(range(len(t1_result)), t1_result, yerr = t1_err, label='|e> decay')
        plt.errorbar(range(len(ft1_result)), ft1_result, yerr = ft1_err, label='|f> decay')
        plt.errorbar(range(len(t1B_result)), t1B_result, yerr = t1B_err, label='|e>(B) decay')
        plt.xlabel('Measurement iterations')
        plt.ylabel('lifetime (us)')
        plt.legend(loc='upper right')
        plt.savefig(save_filepath + 'decays.png')
    
if 0: # T1 Loop
    from scripts.single_qubit import T1measurement
    alz.set_naverages(5000)
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

if 1: # T1_FT1 (new)
    from scripts.single_qubit import T1measurement, FT1measurement, rabi
    for i in range(500):
        N = 10 # number of full curves you want to take for each T1 and FT1
        '''Create all your empty arrays to save fit parameters in'''
        t1_results = np.zeros((N, 5))
        t1_errs = np.zeros((N,5))
        
        ft1_result = np.zeros(N)
        ft1_err = np.zeros(N)
        
        t1B_result = np.zeros(N)
        t1B_err = np.zeros(N)
        '''Set the delay points you would like to use. It's a good idea to tweak these manually a bit to
        minimize the errors on your fit parameters'''
        t1delays = np.concatenate((np.logspace(1, 3, num=3, endpoint=False), 
                                 np.logspace(3, 4, num=11, endpoint=False), 
                                 np.logspace(4, 4.8, num=21)))
        ft1delays = np.concatenate((np.logspace(1, 3, num=3, endpoint=False), 
                                 np.logspace(3, 4, num=11, endpoint=False), 
                                 np.logspace(4, 4.6, num=31)))
        t1Bdelays = np.concatenate((np.logspace(1, 3, num=3, endpoint=False), 
                                 np.logspace(3, 4, num=11, endpoint=False), 
                                 np.logspace(4, 4.8, num=31)))
        
        '''Settings for measuring |e> lifetimes detuned from f_max '''
        detuned_currents = np.linspace(1.517, 1.567, 5)
#        RO_freq_detuned = 6543.53e6
        
        
        '''Settings for measuring |f> lifetime at sweet_spot (ss)'''
        ss_current = -1.26
#        RO_freq_ss = 6543.53e6
        
        
        '''Constant settings'''
        Qbrick.set_frequency(5421e6)
#        RObrick.set_power(-5)
        
#        RObrick.set_frequency(RO_freq_detuned)
#        refbrick.set_frequency(RO_freq_detuned + 50e6)
    
        
        start_time = list(str(datetime.datetime.now())[:19])
        start_time[13] = '-'
        start_time[16] = '-'
        yoko.do_set_output_state(1)
        alz.set_naverages(500)
        for j in range(N):
            print '###############'
            print j
            print '##############'
            
            
            if j == 0:
                '''Find range of detuned frequencies to drive'''
                ssbspec_freqs = np.linspace(-10e6, 10e6, 151)
                w_q = np.zeros_like(detuned_currents)
                alz.set_naverages(500)
                for k in range(len(detuned_currents)):
            
                    yoko.do_set_current(detuned_currents[k])
                    time.sleep(.5)
                    
                             
                    '''Here we do an SSB spec'''
                    from scripts.single_qubit import ssbspec
                    seq = sequencer.Trigger(250)        
                    spec = ssbspec.SSBSpec(qubit2_info, ssbspec_freqs, seq=seq, plot_seqs=False)
                    spec.measure()
                    drive_freq = Qbrick.get_frequency()
                    w_q[k] = ssbspec_freqs[np.argmin(spec.get_ys())]
                    plt.close()
                    time.sleep(1)
                alz.set_naverages(500)
            for k in range(len(detuned_currents)):
                yoko.do_set_current(detuned_currents[k])
                time.sleep(.5)
                ge2.set('deltaf', -375.52e6 + w_q[k])
                
            
                ro.set_IQg((84.205946826+119.160092229j))
                ro.set_IQe((83.3646291389+117.588541459j))
                '''Do the T1 measurement and save the fit parameters'''
                t1 = T1measurement.T1Measurement(qubit2_info, t1delays, double_exp=False, generate=True, plot_seqs=False,
                                                 proj_func='projection')
                t1.measure()
                t1_results[j][k] = t1.fit_params['tau'].value/1000
                t1_errs[j][k] = t1.fit_params['tau'].stderr/1000
                plt.close()
            
            '''Switch your instruments to the values needed to do the FT1 measurement at f_max'''
            yoko.do_set_current(ss_current)
            
#            RObrick.set_frequency(RO_freq_ss)
#            refbrick.set_frequency(RO_freq_ss+50e6)
#            alz.set_naverages(1500)
            
            ro.set_IQg((-42.6642809017+198.754568834j))
            ro.set_IQe((55.88779936+54.5801623745j))
            '''Do the FT1 measurement and save the fit parameters'''
            ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, ft1delays, generate=True,
                                                proj_func='projection')
            ft1.measure()
            ft1_result[j] = ft1.fit_params['tau'].value/1000
            ft1_err[j] = ft1.fit_params['tau'].stderr/1000
            plt.close()
            
            '''Do a T1 measurement at f_max'''
            t1 = T1measurement.T1Measurement(qubit_info, t1Bdelays, double_exp=False, generate=True, plot_seqs=False,
                                             proj_func='projection')
            t1.measure()
            t1B_result[j] = t1.fit_params['tau'].value/1000
            t1B_err[j] = t1.fit_params['tau'].stderr/1000
            plt.close()
            
            '''Switch instrument settings back to be able to measure detuned T1s again'''
        
#            RObrick.set_frequency(RO_freq_detuned)
#            refbrick.set_frequency(RO_freq_detuned + 50e6)
            
    
        end_time = list(str(datetime.datetime.now())[:19])
        end_time[13] = '-'
        end_time[16] = '-'
        
        yoko.do_set_output_state(0)
        
        '''These are just showing you how good your fits were for this run'''
#        print('Average percent error on %.0f T1 measurements was %.03f:' %(int(N), np.average(t1_err/t1_result)))
        print('Average percent error on %.0f FT1 measurements was %.03f:' %(int(N), np.average(ft1_err/ft1_result)))
        print('Average percent error on %.0f T1(B) measurements was %.03f:' %(int(N), np.average(t1B_err/t1B_result)))
#        
        main_filepath = 'C:/Users/WangLabPC7/Documents/DRosenstock/t1ft1/'
        time_stamp = start_time + list(str(' to ')) + end_time
        save_filepath = main_filepath + ''.join(time_stamp) + '/'
            
        if not os.path.exists(save_filepath):
            os.makedirs(save_filepath)
        
        np.savetxt(save_filepath + 'ss_results.txt',
                   np.column_stack((ft1_result, ft1_err, t1B_result, t1B_err)),
                   header = 
                   'FT1 result, FT1 error, T1 result, T1 error')
        
        np.savetxt(save_filepath + 'detuned_results.txt',
                   t1_results,
                   header = 
                   'detuned T1 results, columns are diff freq transitions, rows are repeated iterations')
        
        np.savetxt(save_filepath + 'detuned_errs.txt',
                   t1_errs,
                   header = 
                   'errs from detuned T1 results, columns are diff freq transitions, rows are repeated iterations')
        
        np.savetxt(save_filepath + 'freqs.txt',
                   w_q,
                   header = 
                   'freqs')
        
#        np.savetxt(save_filepath + 'notes.txt', [0],
#                       header = 
#                       'N = ' + str(N) +
#                       ', num_averages = ' + str(alz.get_naverages()) +
#                       ', rep_rate = ' + str(dig.do_get_trigger_period()) + str(' us') + 
#                       ', n_points for T1 = ' + str(len(t1delays)) +
#                       ', n_points for FT1 = ' + str(len(ft1delays)) +
#                       ', n_points for T1(B) = ' + str(len(t1Bdelays)) +
#                       ', RO power (A) = ' + str(RO_power_A) + str(' dBm') +
#                       ', RO power (B) = ' + str(RO_power_B) + str(' dBm') +
#                       ', RO frequency (A) = ' + str(RO_freq_A/1e6) + str(' MHz') + 
#                       ', RO frequency (B) = ' + str(RO_freq_B/1e6) + str(' MHz') + 
#                       ', w_ge (A) = ' + str((qubitge_drive_freq_A + ge.get('deltaf'))/1e6) + str(' MHz') +
#                       ', w_ge (B) = ' + str((qubitge_drive_freq_B + ge.get('deltaf'))/1e6) + str(' MHz') +
#                       ', w_ef (B) = ' + str((qubitge_drive_freq_B + ef.get('deltaf'))/1e6) + str(' MHz') +
#                       ', applied current (A) = ' + str(A_current) + str(' mA') + 
#                       ', applied current (B) = ' + str(B_current) + str(' mA') + 
#                       ', pulse_len = ' + str(4.0*ge.get('w')) + str(' ns'))
        
        '''Plot the data'''
        plt.figure()
        for i in range(5):
            plt.errorbar(range(len(t1_results)), t1_results[:,i], yerr = t1_errs[:,i], label='|e> decay, %.0f' %(w_q[i]))
        plt.errorbar(range(len(ft1_result)), ft1_result, yerr = ft1_err, label='|f> decay')
        plt.errorbar(range(len(t1B_result)), t1B_result, yerr = t1B_err, label='|e>(B) decay')
        plt.xlabel('Measurement iterations')
        plt.ylabel('lifetime (us)')
        plt.legend(loc='upper right')
        plt.savefig(save_filepath + 'decays.png')
        
        time.sleep(60)