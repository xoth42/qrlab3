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

alz = mclient.instruments['alazar']

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
qubit2_info = mclient.get_qubit_info('qubit2ge')
#readout_info = mclient.get_readout_info()


if 0: # T1_FT1
    from scripts.single_qubit import T1measurement, FT1measurement, T1_FT1measurement, rabi
    alz.set_naverages(100000)
#    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 160e3, 101), double_exp=False, generate=True, plot_seqs=False)
#    t1.measure()
#    ofs = t1.result_params['ofs'].value
#    amplitude = t1.result_params['amplitude'].value
#
#    ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.linspace(0, 120e3, 101), generate=True)
#    ft1.measure()
#    f_ofs = ft1.fit_params['ofs'].value
#    f_amp = ft1.fit_params['amplitude'].value

#    t1_decay = []
#    ft1_decay = []
#    times = []
#    t1_err = []
#    ft1_err = []
#    fullt1_decay = []
#    fullft1_decay = []

    for i in range(300):
        print '###############'
        print i
        print '##############'
        t1_ft1 = T1_FT1measurement.T1_FT1measurement(qubit_info, ef_info, 6.5e3, 5.5e3, histogram=True, generate=True)
        t1_ft1.measure()
        
#        now = datetime.datetime.now()
#        date = str(now)[5:7] + str(now)[8:10]
#        hour = str(now)[11:13]
#        minute = str(now)[14:16]
#        second = str(now)[17:19]
#    
#        times.append(str(datetime.datetime.now())[11:19])
#        t1_decay.append(t1_ft1.result_params[0]/1000)
#        ft1_decay.append(t1_ft1.result_params[1]/1000)
#        plt.close()
#        time.sleep(5)
        
#        alz.set_naverages(1000)
#        t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 200e3, 101), double_exp=False, generate=False, plot_seqs=False)
#        t1.measure()
#        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.linspace(0, 120e3, 101), generate=False)
#        ft1.measure()
#       
#        alz.set_naverages(50000)
#        tr = rabi.Rabi(qubit_info, [qubit_info.pi_amp,], histogram=True, title='|e>')
#        tr.measure()
#        tr = rabi.Rabi(qubit_info, [0.0001,], histogram=True, title='|g>')
#        tr.measure()
#        raw = np.loadtxt("C:\qrlab\instrumentserver\dario_test", dtype='str')
#        iq = raw.reshape([alz.get_naverages(), 4])
#        iq = iq.T
#        
#        raw_ft1 = iq[0]
#        raw_g = iq[1]
#        raw_e = iq[2]
#        raw_t1 = iq[3]
#
#
#        for i in range(len(raw_g)):
#           if '+-' in raw_g[i]:
#               raw_g[i] = raw_g[i].replace('+-', '-')
#               
#        for i in range(len(raw_e)):
#           if '+-' in raw_e[i]:
#               raw_e[i] = raw_e[i].replace('+-', '-')
#               
#        for i in range(len(raw_t1)):
#           if '+-' in raw_t1[i]:
#               raw_t1[i] = raw_t1[i].replace('+-', '-')
#               
#        for i in range(len(raw_ft1)):
#           if '+-' in raw_ft1[i]:
#               raw_ft1[i] = raw_ft1[i].replace('+-', '-')
#               
#        complex_g = map(complex, raw_g)
#        complex_e = map(complex, raw_e)
#        complex_t1 = map(complex, raw_t1)
#        complex_ft1 = map(complex, raw_ft1)
#        
#        vproj = readout_info.IQe - readout_info.IQg
#        vproj /= np.abs(vproj) 
#        
#        complex_g[:] = [x - readout_info.IQg for x in complex_g]
#        complex_e[:] = [x - readout_info.IQg for x in complex_e]
#        complex_t1[:] = [x - readout_info.IQg for x in complex_t1]
#        complex_ft1[:] = [x - readout_info.IQg for x in complex_ft1]
#        
#        proj_g = np.real(complex_g) * vproj.real  + np.imag(complex_g) * vproj.imag
#        proj_e = np.real(complex_e) * vproj.real  + np.imag(complex_e) * vproj.imag
#        proj_t1 = np.real(complex_t1) * vproj.real  + np.imag(complex_t1) * vproj.imag
#        proj_ft1 = np.real(complex_ft1) * vproj.real  + np.imag(complex_ft1) * vproj.imag
#
#        proj_eq = (proj_e + proj_g) / 2
#
#        rawt1decay = []
#        rawft1decay = []
#
#        for i in range(alz.get_naverages()):
#            rawt1decay.append(-40e3 / np.log((proj_t1[i]-proj_g[i])/(proj_e[i]-proj_g[i])))
#            rawft1decay.append(-25e3 / np.log((proj_ft1[i]-proj_eq[i])/(proj_e[i]-proj_eq[i])))
#        
##        amp = (np.real(raw)**2+np.imag(raw)**2)**0.5
#        errs = [np.std(np.abs(proj_g)), np.std(np.abs(proj_e)), np.std(np.abs(rawt1decay)), np.std(np.abs(rawft1decay))]
#        errs2 = [np.std(proj_g), np.std(proj_e), np.std(rawt1decay), np.std(rawft1decay)]
#        print errs
#        print errs2
#        t1_err.append(errs[2])
#        ft1_err.append(errs[3])
        
#    plt.figure()
#    plt.plot(range(len(t1_decay)), t1_decay, label='|e> decay')
#    plt.plot(range(len(ft1_decay)), ft1_decay, label='|f> decay')
#    plt.xlabel('Measurement iterations')
#    plt.ylabel('lifetime (us)')
#    plt.legend(loc='upper right')
#    

    
#    plt.figure()
#    plt.errorbar(range(len(t1_decay)), t1_decay, yerr = t1_err, label='|e> decay')
#    plt.errorbar(range(len(ft1_decay)), ft1_decay, yerr = ft1_err, label='|f> decay')
#    plt.xlabel('Measurement iterations')
#    plt.ylabel('lifetime (us)')
#    plt.legend(loc='upper right')

if 0: # Test fitting exponential decay to a measurement with only a few points but known initial and final voltages
    from scripts.single_qubit import T1measurement, FT1measurement
    alz.set_naverages(50000)
    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 200e3, 101), double_exp=False, generate=True, plot_seqs=False)
    t1.measure()
    ofs = t1.result_params['ofs'].value
    amplitude = t1.result_params['amplitude'].value

    ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.linspace(0, 120e3, 101), generate=True)
    ft1.measure()
    f_ofs = ft1.fit_params['ofs'].value
    f_amp = ft1.fit_params['amplitude'].value

    t1_result = []
#    tau_err = []

    ft1_result = []
#    ftau_err = []

    for i in range(10):
        t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 200e3, 3), double_exp=False, force_ofs=None,
                                         force_amplitude=None, generate=True, plot_seqs=False)
        t1.measure()
        t1_result.append(t1.result_params['tau'].value/1000)
#        tau_err.append(t1.result_params['tau'].stderr/1000)
        
        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.linspace(0, 120e3, 3), force_ofs=None,
                                            force_amplitude=None, generate=True)
        ft1.measure()
        ft1_result.append(ft1.fit_params['tau'].value/1000)
#        ftau_err.append(ft1.fit_params['tau'].stderr/1000)


    plt.figure()
#    plt.xticks(ticks, times)
#    plt.errorbar(range(len(t1_result)), t1_result, yerr = tau_err, label='|e> decay')
    plt.plot(range(len(t1_result)), t1_result, label='|e> decay')
    plt.xlabel('Measurement iterations')
    plt.ylabel('lifetime (us)')
#    plt.errorbar(range(len(ft1_result)), ft1_result, yerr = ftau_err, label='|f> decay')
    plt.errorbar(range(len(ft1_result)), ft1_result, label='|f> decay')
    plt.legend(loc='upper right')

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
        
if 1: #T1_FT1 toggle flux
    from scripts.single_qubit import Yoko_exttrig_testing
    for i in range(1):
        Yoko_test = Yoko_exttrig_testing.Yoko_test(qubit_info, ef_info, qubit2_info, 6.5e3, 5.5e3, histogram=False, generate=True)
        #t1_ft1_flux.play_sequence()
        Yoko_test.measure()