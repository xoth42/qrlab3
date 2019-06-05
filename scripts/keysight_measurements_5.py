# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 14:53:09 2018

@author: wanglab
"""

import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
#matplotlib.rcParams['backend'] = 'Qt4Agg'
#matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
#from t1t2_plotting import smart_T1_delays
import os
import time
import math
import lmfit


qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
#qubit03_info = mclient.get_qubit_info('qubit1_03')
#qubit14_info = mclient.get_qubit_info('qubit1_14')
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')
os.chdir(r'C:/qrlab/scripts')

#cool_time=30e3
#cool = sequencer.Combined([sequencer.Constant(int(cool_time), 0.04, chan=ef_info.sideband_channels[0]),
#                           sequencer.Constant(int(cool_time), 0.04, chan=ef_info.sideband_channels[1]),
#                           sequencer.Constant(int(cool_time), 1, chan='3m1')])

if 0: # test digitizer
    dig = mclient.instruments['dig']
    data = dig.test_dig(1000000, 1, 1, 1)
    print(np.shape(data))
    plt.figure()
    plt.plot(data[0][0][:], label = 'sig')
    plt.plot(data[1][0][:], label = 'ref')
    plt.legend()
    plt.show()
    bla

if 0: # cav transmission
    from single_cavity import rocavspectroscopy_keysight
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
#    Yoko.do_set_current(-0.00175)
    rofreq = 7608.5e6
    freq_range = 20e6
    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(10, 10, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 51),
                                             qubit_pulse=False, seq=None)
    ro.measure()
    bla
    
    
if 0: # calibrate TWPA
    SC_TWPApump = mclient.instruments['SC_TWPApump']
    from single_cavity import twpa_calibration_keysight
    target_freq = 7.915e9
    freq_range = .03e9
    twpa_powers = np.linspace(10, 12.25, 10)
    twpa_freqs = np.linspace(target_freq-freq_range, target_freq+freq_range, 100)
    for power in [5]:
        tc = twpa_calibration_keysight.twpa_calibration_keysight(qubit_info, power, 7611.55e6, twpa_powers, 
                                                   twpa_freqs, SC_TWPApump, qubit_pulse=False)
        tc.measure()
        
if 0:
    from single_cavity import rocavspectroscopy_keysight_IQmod
#    rofreq = 8553.1e6
    rofreq = 8306.00e6
    freq_range = 15e6
    ro = rocavspectroscopy_keysight_IQmod.ROCavSpectroscopy(qubit_info, RO_info, np.linspace(-10, -20, 3),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 55),
                                               plen=20000, amp=0.0001, qubit_pulse=False)
    ro.measure()
    bla
    

if 0: #     qubit spectroscopy
    from single_qubit import spectroscopy_keysight
#    from scripts.single_qubit import spectroscopy_IQ
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
    qubit_freq = 7.707e9

    freq_range = 1000e6
    spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['Brick14'], qubit14_info, 
                                     np.linspace(qubit_freq-freq_range,
                                                 qubit_freq+freq_range, 2501),
                                     [10],
                                     plen=30000, amp=0.08, extra_info=qubit_info, seq=seq, postseq=postseq, plot_seqs=False) 

    spec.measure()
    bla

if 0: # Qubit spec with phase correction
    from single_qubit import spectroscopy_keysight_phasecorrection
#    from scripts.single_qubit import spectroscopy_IQ
    qubit_freq = 946.889e6
    freq_range = 100e6
    spec = spectroscopy_keysight_phasecorrection.Spectroscopy_Keysight_phasecorrection(mclient.instruments['QK'], qubit_info,
                                     np.linspace(qubit_freq-freq_range, qubit_freq+freq_range*10, 1101), [10],
                                     plen=50000, amp=0.001, plot_seqs=False) #1=1ns

#    spec = spectroscopy_IQ.Spectroscopy_IQ(client.instruments['gen'], qubit_info,
#                                     np.linspace(702e6, 710e6, 81), [-30],
#                                    plen=250*100, amp=0.1, ssb=False, plot_seqs=False)

    spec.measure()
    
    bla    
    
    

if 0: # SSB spec
    from single_qubit import ssbspec
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    for i in range(1):
        seq = sequencer.Trigger(600)
        spec = ssbspec.SSBSpec(qubit_info, np.linspace(-5e6, 5e6, 101), seq=None, plot_seqs=False, proj_func='phase')
        spec.measure_keysight()
#        plt.close()
    bla

if 0: # SSB spec with lorentzian fit
    from single_qubit import ssbspec_lorentzianfit
    seq = sequencer.Trigger(600)
    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-30e6, 30e6, 201), seq=seq, plot_seqs=False, proj_func='phase')
    spec.measure_keysight()
    center = spec.center
    height = spec.height
    width = spec.width

if 0: # Check histogramming  #THIS DOES NOT WORK, IT NEEDS TO BE IMPLEMENTED TO KEYSIGHT
    from single_qubit import rabi
#    dig.set_naverages(50000)
    tr = rabi.Rabi(qubit_info, [qubit_info.pi_amp,], histogram=True, title='|e>')
    tr.measure_keysight()
    tr = rabi.Rabi(qubit_info, [0.001,], histogram=True, title='|g>')
    tr.measure_keysight()
    tr = rabi.Rabi(qubit_info, [qubit_info.pi_amp/2,], histogram=True, title='|g>+|e>')
    tr.measure_keysight()


    

if 0: #Multiple times SSB spec
    from single_qubit import ssbspec
    seq = sequencer.Trigger(250)
    freq_array = np.linspace(-1.5e6, 0.3e6, 60)
    spec = ssbspec.SSBSpec(qubit_info, freq_array, seq=seq, plot_seqs=False)
    spec.measure_keysight()
    data_sum = spec.get_ys()
    for i in range (10):
        seq = sequencer.Trigger(250)
        spec = ssbspec.SSBSpec(qubit_info, freq_array, seq=seq, plot_seqs=False)
        spec.measure_keysight()
        data_sum = data_sum + spec.get_ys()
        data_avg = data_sum / (i+2)
    plt.figure()
    plt.plot(freq_array, data_avg)
    bla
     
    
if 0: # Power Rabi-Calibrate pi pulse

    from single_qubit import rabi
    import time
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    for i in range(1):
        tr = rabi.Rabi(qubit_info, 
#                       np.linspace(-0.24, -0.20, 81), selective=False,
                       np.linspace(-0.6, 0.6, 81), selective=False,
#                       np.linspace(-0.26, -0.18, 101), selective=False,
#                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                       plot_seqs=False, generate=True, repeat_pulse=5, seq=None,
                       update=False, #extra_info=ef_info,
                       proj_func='phase'
                       )
        tr.measure_keysight()

    bla

if 0: # Pi/2 pulse train
    from single_qubit import Pi2_train
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    pi2tr = Pi2_train.Pi2_train(qubit_info, np.linspace(0.215, 0.221, 61), seq=seq, generate=True, 
                              repeat_pulse=16, proj_func='phase', extra_info=ef_info)
    pi2tr.measure_keysight()
    bla
#    pi2_result.append(pi2.get_ys())

if 0: # Pi pulse train
    from single_qubit import Pi_train
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    pitr = Pi_train.Pi_train(qubit_info, np.linspace(0.435, 0.441, 61), seq=seq, generate=True, 
                              repeat_pulse=15, proj_func='phase', extra_info=ef_info)
    pitr.measure_keysight()
#    pi2_result.append(pi2.get_ys())
    bla


if 0: # Pi Amp Tuning
#   for i in range (1):
#        from scripts.single_qubit import rabi
#        tr = rabi.Rabi(qubit_info, np.linspace(0, 0.2, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
#                       update=True)
#        data=tr.measure()

    dig.do_set_naverages(10000)
    from single_qubit import pi_amp_cal
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    pi_result = []
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(-np.pi/2, 0)]) #this whole line was added
    pi = pi_amp_cal.Pi_Amp_Cal(qubit_info, seq=seq, generate=True, proj_func='phase', extra_info=ef_info)  #seq=seq was added
    pi.measure_keysight()
    pi_result.append(pi.get_ys())
    plt.figure()
    plt.plot(pi.get_ys(), "o", linestyle = '-' )

    
if 0: # T1
    from single_qubit import T1measurement

#    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 250e3, 121), 
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(2000, 1, chan='3m1'), sequencer.Delay(250),
#                          ef_info.rotate(np.pi, 0), sequencer.Constant(4000, 1, chan='3m1'), sequencer.Delay(250)])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])

    t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
#                                     np.concatenate((np.linspace(0.1e3, 1.9e3, 31), np.linspace(2e3, 20e3, 56), np.linspace(21e3, 450e3, 60))),
                                     np.concatenate((np.linspace(0.1e3, 10e3, 31), np.linspace(11e3, 100e3, 56), np.linspace(105e3, 450e3, 60))),
                                     double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None)    
    t1.measure_keysight()
    bla

if 1: # T1 - alternating pi-pulse and saturation T1
    from single_qubit import T1_alternate_pi_saturation

    t1 = T1_alternate_pi_saturation.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
                                     np.concatenate((np.linspace(0.1e3, 10e3, 21), np.linspace(11e3, 150e3, 26), np.linspace(155e3, 650e3, 30))),
                                     double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None)    
    t1.measure_keysight()
    bla

if 0:
    from scripts.single_qubit import ssbspec
    from scripts.single_qubit import rabi
    from scripts.single_qubit import T1measurement
    powers = np.linspace(-20, 10, 2)
    frequencies = np.linspace(120, 180, 3)

if 1: #T2
    from single_qubit import T2measurement
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    for i in range(1):
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 12e3, 101), detune=0.8e6, double_freq=False, generate=True, 
                                         seq=None, postseq=None, proj_func='phase')
#        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')

        
        t2.measure_keysight()
    bla
    
if 0: 
    from single_qubit import rabi
    from single_qubit import T1measurement
    from single_qubit import T2measurement
    SCpump = mclient.instruments['SCpump']
    postseq = sequencer.Delay(500)
    pi_amp = []
    Tone = []
    Ttwo = []
    num = 5
    prange = np.linspace(-10, -5.3, num)
    SCpump.do_set_rf_on(True)
    for TWPA_power in prange:
        SCpump.do_set_power(TWPA_power)
#        SCpump.do_set_rf_on(False)
#        tr = rabi.Rabi(qubit_info, 
##                       np.linspace(-.08, .08, 100), selective=True,
#                        np.linspace(-.4, .4, 61), selective=False,
#                        plot_seqs=False, generate=True, repeat_pulse=1, update=True)
#        
#        tr.measure_keysight()
#        pi_amp.append(tr.fit_params['period'].value / 2)
#        t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 100e3, 61), 
#                                     double_exp=False, generate=True, plot_seqs=False)
#        t1.measure_keysight()
#        Tone.append(t1.fit_params['tau'].value)
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 8e3, 51), detune=0.8e6, double_freq=False, generate=True, postseq=postseq)
        t2.measure_keysight()
        Ttwo.append(t2.fit_params['tau'].value)
#    fig = plt.figure(figsize=(9, 3))
#    plt.subplot(1, 3, 1)
#    plt.plot(prange, pi_amp)
#    plt.subplot(1, 3, 2)
#    plt.plot(prange, Tone)
#    plt.subplot(1, 3, 3)
    plt.plot(prange, Ttwo)
    plt.savefig('C:\\Users\\Wang_Lab\\Desktop\\1.png')
    plt.clf()
    
    
    
if 0: # T2echo
    from single_qubit import T2measurement
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
#    postseq = sequencer.Delay(500)
#    for i in range (5):
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 30e3, 101), detune=0.3e6, echotype = T2measurement.ECHO_HAHN, necho=1, 
                                     plot_seqs = False, generate=True, proj_func='phase', seq=None)
    t2.measure_keysight()
    bla
    
if 0: # EF Qubit spec 
    from scripts.single_qubit import spectroscopy_keysight
    ef_freq = 2645e6
    freq_range = 10e6
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
    spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['efBrick'], ef_info, np.linspace(ef_freq-freq_range, ef_freq+freq_range,101), [10],
                                     plen=50000, amp=0.01,
                                     seq=seq, postseq=postseq,
                                     extra_info=qubit_info, plot_seqs=False)
    spec.measure()
    bla
    
if 0: # EF SSBspec
    from single_qubit import ssbspec
    seq = sequencer.Sequence([sequencer.Trigger(400), qubit_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    spec = ssbspec.SSBSpec(ef_info, np.linspace(-5e6, 5e6, 121), seq=seq, postseq = postseq, extra_info=qubit_info, plot_seqs=False, generate=True, proj_func='phase')
    spec.measure_keysight()
    bla
    
if 0: # EF rabi 
    from single_qubit import efrabi
#    dig = mclient.instruments['dig']
#    cool_time = 25e3
#    cool_time_range = [0.5e3, 1e3, 5e3, 10e3, 100e3]
#    amps = [0, 0.02, 0.05, 0.075, 0.1]
#    for cool_time in cool_time_range:
#    cool = sequencer.Combined([sequencer.Constant(int(cool_time), 0.1, chan=ef_info.sideband_channels[0]),
#                                   sequencer.Constant(int(cool_time), 0.1, chan=ef_info.sideband_channels[1]),
#                                   sequencer.Constant(int(cool_time), 1, chan='3m1')])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    dig.set_naverages(4000)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.7, 0.7, 101), first_pi=True, second_pi=True, seq=None, generate=True, update=True,
                            proj_func='phase')
    efr.measure_keysight()
    period = efr.fit_params['period'].value
    dig.set_naverages(20000)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.7, 0.7, 101), first_pi=False, second_pi=True, selective=False, seq=None, generate=True,
                            force_period = period, proj_func='phase')
    efr.measure_keysight()
    dig.set_naverages(4000)
    bla
    
if 0: # FT1
    from single_qubit import FT1measurement
    #ft1times = np.zeros(len(range(20)))
    for i in range(1):
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.linspace(0, 10e3, 101), seq=None, proj_func='phase')
        ft1.measure_keysight()
        #ft1times[i] = ft1.analyze()
        #plt.close()
        
    bla

if 0: # EFT2
    from scripts.single_qubit import EFT2measurement # frequency stability of |f> vs |e>
    for i in range(1):
#        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
        seq = sequencer.Sequence(sequencer.Trigger(250))
        eft2 = EFT2measurement.EFT2Measurement(qubit_info, ef_info, np.linspace(0, 1.5e3, 101), detune=3e6, double_freq=False, plot_seqs = False, echotype = EFT2measurement.ECHO_NONE,
                                               proj_func='phase')
        eft2.measure_keysight()

def dynamic_ssb(qubit_info, step = .1e6, plotting = True):
    from scripts.single_qubit import ssbspec
    seq = sequencer.Trigger(250)

    not_found = True
    high_pass = False
    high_mark = 0
    low_mark = 0
    while not_found:
        if high_pass and high_mark <= 60e6:
            freqs = np.arange(high_mark-1e6, high_mark + 20e6, step)
            high_mark += 20e6
            high_pass = False
        else:
            freqs = np.arange(low_mark - 20e6, low_mark+1e6, step)
            low_mark -= 20e6
            high_pass = True
        spec = ssbspec.SSBSpec(qubit_info, freqs, seq=seq, plot_seqs=False)
        spec.measure_keysight()
        ys = spec.get_ys()
        plt.axhline(np.mean(ys) + np.std(ys)*3)
        plt.axhline(np.mean(ys) - np.std(ys)*3)
        if not plotting:
            plt.close()
        if (np.abs(np.min(ys) - np.mean(ys)) > np.std(ys)*3):
            not_found = False
            guess = freqs[np.argmin(ys)]
        elif(low_mark <= -150e6):
            return None
        
    
    final_freqs = np.linspace(guess-step*10, guess+step*10, 100)
    final_spec = ssbspec.SSBSpec(qubit_info, final_freqs, seq=seq, plot_seqs=False)
    final_spec.measure_keysight()
    if not plotting:
        plt.close()
    return final_freqs[np.argmin(final_spec.get_ys())]


if 0: # Process_tomography
    from scripts.single_qubit import Process_tomo
    ptomo_result = []
    p_seq = sequencer.Sequence(sequencer.Delay(2000))
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(-np.pi/2, 0)]) #this whole line was added
    sqtomo = Process_tomo.Process_tomo(qubit_info, process_seq=p_seq, generate=True, proj_func='phase')  #seq=seq was added
    sqtomo.measure_keysight()

    ptomo_result.append(sqtomo.get_ys())
#    plt.close()

    print ptomo_result
    bla
    
    
if 0: # 
    
    from scripts.single_qubit import contrast_normalization
    
    cn_result = [] #First five points should be ground state, following five points should be excited state
    
    p_seq = sequencer.Sequence(sequencer.Delay(80))
    
    cn = contrast_normalization.Contrast_Normalization(qubit_info, process_seq=p_seq, generate=True, proj_func='phase')  #seq=seq was added
    
    cn.measure_keysight()

    cn_result.append(cn.get_ys())

    print cn_result
    bla    

if 0: # Drag test
    from scripts.single_qubit import drag_test
#    dig.do_set_naverages(3000)
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    dtest = drag_test.drag_test(qubit_info, np.linspace(-0.8, 0.5, 81), seq=seq, plot_seqs=False, generate=True, proj_func='phase', extra_info=ef_info)
    data=dtest.measure_keysight()
    bla

if 0: # Detuning test
    from scripts.single_qubit import Detuning_error
    dig.do_set_naverages(100000)
    freq_sweep = np.linspace(944e6,945e6,11)
    
    det1=[]
    det2=[]
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    for i in range(len(freq_sweep)):
        QK.set_frequency(freq_sweep[i])
#        qubit1ge.set_pi_amp(0.435 + (13e-6)*i) 
#        qubit1ge.set_pi2_amp(0.2171 + (5e-6)*i)
        det = Detuning_error.Detuning_error(qubit_info, seq= seq, plot_seqs=False, generate=True, proj_func='phase', extra_info=ef_info)
        det.measure_keysight()
        data_y = det.get_ys()
        det1.append(data_y[0])
        det2.append(data_y[1])
        plt.close()
    plt.figure()
    plt.plot(freq_sweep,det1)
    plt.plot(freq_sweep,det2)
    
    def linear_fit(params, x, data):
        est = params['m']*x + params['n']
        return (data-est)

    def linear_fit2(params, x):
        est = params['m']*x + params['n']
        return est

    params = lmfit.Parameters()
    params.add('m', value=0)
    params.add('n', value=0)
    result1 = lmfit.minimize(linear_fit, params, args=(freq_sweep,det1))
    result2 = lmfit.minimize(linear_fit, params, args=(freq_sweep,det2))
    
    lmfit.report_fit(result1.params)
    lmfit.report_fit(result2.params)
    plt.figure()
    plt.plot(freq_sweep, linear_fit2(result1.params, freq_sweep), color='r')
    plt.plot(freq_sweep, linear_fit2(result2.params, freq_sweep), color='b')
    plt.plot(freq_sweep, det1, color='r')
    plt.plot(freq_sweep, det2, color='b')
    bla

    plt.figure()
    det1 = np.array(det1)
    det2 = np.array(det2)
    plt.plot(freq_sweep, det1-det2)
    result3 = lmfit.minimize(linear_fit, params, args=(freq_sweep,det1-det2))
    plt.plot(freq_sweep, linear_fit2(result3.params, freq_sweep), color='r')
    plt.plot(freq_sweep, np.zeros(shape=len(freq_sweep)))
    
if 0: # AllXY
#   for i in range (1):
#        from scripts.single_qubit import rabi
#        tr = rabi.Rabi(qubit_info, np.linspace(0, 0.2, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
#                       update=True)
#        data=tr.measure()

#    dig.do_set_naverages(10000)
    from single_qubit import allxy
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    allxy_result = []
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(-np.pi/2, 0)]) #this whole line was added
    axy = allxy.All_XY(qubit_info, seq=seq, generate=True, proj_func='phase', extra_info=ef_info)  #seq=seq was added
    axy.measure_keysight()
    allxy_result.append(axy.get_ys())

#    for i in range(4):
#        axy = allxy.All_XY(qubit_info, seq=None, generate=True,proj_func='phase') #seq=seq added
#        axy.measure_keysight()
#        allxy_result.append(axy.get_ys())
#
#
#    plt.figure()
#    for i in range(5): plt.plot(allxy_result[i])
    bla



if 0: # Detuning Error Test


    dig.do_set_naverages(10000)
    from single_qubit import Detuning_error_test
    det_result = []
    initialfreq = 946891000.0
    freq_step=1e6
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(-np.pi/2, 0)]) #this whole line was added
    for i in np.linspace(-2,2,5):
        
        QK.set_frequency(initialfreq + i*freq_step)
        det = Detuning_error_test.Detuning_error_test(qubit_info, seq=None, generate=True, proj_func='phase')  #seq=seq was added
        det.measure_keysight()
        det_result.append(det.get_ys())
        
#    det_result.append(QK.get_frequency())

#    for i in range(4):
#        axy = allxy.All_XY(qubit_info, seq=None, generate=True,proj_func='phase') #seq=seq added
#        axy.measure_keysight()
#        allxy_result.append(axy.get_ys())
#
#
    plt.figure()
    for i in range(5): plt.plot(det_result[i], label='%s' % i)
    bla



    
if 1: # Randomized benchmarking

    from scripts.single_qubit import randbench
    from scripts.single_qubit import contrast_normalization
    run_number = 6 #How many RB runs to be completed
    rndmben_result = []

    dig.do_set_naverages(6000)
        
#    dig.do_set_naverages(30000)
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])

#
#    for i in range(run_number):
#        rndmben = randbench.rndm(qubit_info, num_cal_points=20, n_gates_start=1, n_gates_stop= 311, n_gates_step=3, seq=seq, generate=True, proj_func='phase', extra_info=ef_info) #seq=seq added
#        rndmben.measure_keysight()
#        rndmben_result.append(rndmben.get_ys())
    freq_sweep = np.linspace(944.3e6,944.7e6,9)   
    for freq in freq_sweep:
        QK.set_frequency(freq)
    
        for i in range(run_number):
            rndmben = randbench.rndm(qubit_info, num_cal_points=20, n_gates_start=1, n_gates_stop= 151, n_gates_step=3, seq=seq, generate=True, proj_func='phase', extra_info=ef_info) #seq=seq added
            rndmben.measure_keysight()
        #        normalized_result = (rndmben.get_ys() - rndmben.) / (rndmben.excited_voltage - rndmben.ground_voltage)
            rndmben_result.append(rndmben.get_ys())
                
    bla


if 0: # Randomized benchmarking - DIAGNOSTICS 

    from scripts.single_qubit import randbench_diagnostics
    qubit_info = mclient.get_qubit_info('qubit1ge')
    qbrick = mclient.instruments['QK']
    rndmben_diagnostics_result = []


    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])

#qubitfreq = 946142000.0
    for i in range(1):
#        qubitfreq= qbrick.get_frequency()
#        qbrick.set_frequency(qubitfreq)        
        #set pi_amp to something slightly deviating 
        #detune the frequency a little bit 
        rndmben_diagnostics = randbench_diagnostics.rndm_diagnostics(qubit_info, num_cal_points=20, n_gates_start=1, n_gates_stop= 211, n_gates_step=3, seq=None, generate=True, proj_func='phase', extra_info=ef_info) #seq=seq added
        rndmben_diagnostics.measure_keysight()        
#    qubitfreq = 946142000.0
#    for i in range(4):
#        qubitfreq= qbrick.get_frequency()
#        qbrick.set_frequency(qubitfreq - 50e3)        
#        #set pi_amp to something slightly deviating 
#        #detune the frequency a little bit 
#        rndmben_diagnostics = randbench_diagnostics.rndm_diagnostics(qubit_info, num_cal_points=20, n_gates_start=1, n_gates_stop= 211, n_gates_step=3, seq=seq, generate=True, proj_func='phase', extra_info=ef_info) #seq=seq added
#        rndmben_diagnostics.measure_keysight()  
        
#    plt.figure()
#    plt.plot(rndmben.xs, rndmben.get_ys())#, linestyle=None)

#        plt.close('all')
#    print rndmben_result
    bla

























    
if 0: # stark shift measurments
    try:
        from scripts.single_qubit import ssbspec
        from scripts.single_qubit import rabi
        from scripts.single_qubit import T1measurement
        import traceback
    
        
        pumpFG = mclient.instruments['pump1Brick']
        dig = mclient.instruments['dig']
        geFG = mclient.instruments['geFG']
        RObrick = mclient.instruments['RObrick']
        refFG = mclient.instruments['refFG']
        ge_instrument = mclient.instruments['qubit1ge']
        bare_ge = 5107.5e6
        pi_amp_guess = .3
        pi_amp_selective_guess = .025
        anhamonicity = 276e6
        
        num_powers = 5
        num_frequencies = 1
        powers = np.linspace(-5, 10, num_powers)
        frequencies = np.linspace(bare_ge + anhamonicity*1.5, bare_ge + anhamonicity*1, num_frequencies)
    #    dig.set_naverages(2000)
        
        T1_averages = 5
        freq_arr = np.zeros((num_powers, num_frequencies))
        T1_arr = np.zeros((num_powers, num_frequencies, T1_averages))
        T1_std_arr = np.zeros_like(T1_arr)
        amp_arr = np.zeros_like(freq_arr)
        
        pumpFG.set_rf_on(True)
        dig.set_naverages(2000)
        for j in range(num_frequencies):
            print('#################################')
            print('frequency set to ' + str(frequencies[j]))
            print('#################################')
            geFG.set_frequency(bare_ge + 100e6 - 20e6)
            ge_instrument.set_pi_amp_selective(pi_amp_selective_guess)
            for i in range(num_powers):
                # set the pump            
                pumpFG.set_power(powers[i])
                pumpFG.set_frequency(frequencies[j])
    
                # ssb spec to find the qubit
                '''
                seq = sequencer.Trigger(250)
                spec = ssbspec.SSBSpec(qubit_info, np.linspace(-30e6, 5e6, 100), seq=seq, plot_seqs=False)
                spec.measure_keysight()
                plt.close()
                freqs = spec.xs
                ys = spec.get_ys()
                '''
                
                new_ge = dynamic_ssb(qubit_info, plotting = True)
                while new_ge is None:
                    geFG.set_frequency(geFG.get_frequency()-100e6)
                    new_ge = dynamic_ssb(qubit_info, plotting = False)
                    if (bare_ge + 100e6) - geFG.get_freqiency() > 1e9:
                        break
                    
                geFG.set_frequency(geFG.get_frequency() + new_ge)
                freq_arr[i][j] = geFG.get_frequency()
                time.sleep(.1)
                
                # rabi to calibrate pi amp
                tr = rabi.Rabi(qubit_info, 
                           np.linspace(-pi_amp_guess, pi_amp_guess, 75), selective=False,
                           plot_seqs=False, generate=True, repeat_pulse=1, update=False)
                amp_arr[i][j] = tr.measure_keysight()
                ge_instrument.set_pi_amp(amp_arr[i][j])
                plt.close()
             
                # perform the actual T1
                for k in range(T1_averages):
                    t1_freqs = np.concatenate((np.linspace(0, 1e3, 3), 
                                               np.linspace(1e3, 10e3, 5), 
                                               np.linspace(10e3, 50e3, 15), 
                                               np.linspace(50e3, 180e3, 10)))
                    t1 = T1measurement.T1Measurement(qubit_info, t1_freqs, 
                                                 double_exp=False, generate=True, plot_seqs=False)
                    T1_arr[i][j][k] = t1.measure_keysight()
                    T1_std_arr[i][j][k] = t1.fit_params['tau'].stderr
                    plt.close()
                    if T1_arr[i][j][k] < 1e3 or T1_arr[i][j][k] > 100e3:
                        print('fitting has probably failed')
                        T1_arr[i][j][:] = 0
                        T1_std_arr[i][j][:] = 0
                        freq_arr[i][j] = 0
                        amp_arr[i][j] = 0
                        break
                    else:
                        ratio = ge_instrument.get_w()/ge_instrument.get_w_selective()*.8
                        ge_instrument.set_pi_amp_selective(ratio*amp_arr[i][j])
        
        pumpFG.set_rf_on(False)
    #    mean_T1 = np.average(T1_arr, axis=2, weights = T1_std_arr)
        mean_T1 = np.average(T1_arr, axis=2)
        # TODO make this a weighted std
        std_T1 = np.std(T1_arr, axis=2)
        
        
        
        if 0: # plot by frequency
            plt.figure()
            plt.subplot(3,1,1)
            for i in range(num_powers):
                plt.plot(frequencies, freq_arr[i], label = str(powers[i]) + 'dbm')
            plt.legend()
            plt.subplot(3,1,2)
            for i in range(num_powers):
                plt.errorbar(frequencies, mean_T1[i], yerr = std_T1[i], label = str(powers[i]) + 'dbm')
            plt.legend()
            plt.subplot(3,1,3)
            for i in range(num_powers):
                plt.plot(frequencies, amp_arr[i], label = str(powers[i]) + 'dbm')
            plt.legend()
            plt.show()
        if 1: # plot by power
            plt.figure()
            plt.subplot(3,1,1)
            for i in range(num_frequencies):
                plt.plot(powers[freq_arr[:,i]!=0], freq_arr[:,i][freq_arr[:,i]!=0], 
                         label = str((frequencies[i]-bare_ge)/anhamonicity) + 'w/alpha')
            plt.legend()
            plt.subplot(3,1,2)
            for i in range(num_frequencies):
                plt.errorbar(powers[mean_T1[:,i]!=0], mean_T1[:,i][mean_T1[:,i]!=0], 
                             yerr = std_T1[:,i][mean_T1[:,i]!=0], 
                             label = str((frequencies[i]-bare_ge)/anhamonicity) + 'w/alpha')
            plt.legend()
            plt.subplot(3,1,3)
            for i in range(num_frequencies):
                plt.plot(powers[amp_arr[:,i]!=0], amp_arr[:,i][amp_arr[:,i]!=0], 
                             label = str((frequencies[i]-bare_ge)/anhamonicity) + 'w/alpha')
            plt.legend()
            plt.show()
    except Exception as err:
        print(err)
        traceback.print_exc()
        pumpFG.set_rf_on(False)       
    
if 0: # f0 - g1 fwm test
    fwm_gen = mclient.instruments['f0g1brick']
    ROfreq = 7608.5e6
    ge = 944.546e6 - 100e6
    ef = 2648.8e6 - 100e6
    target_freq = ROfreq - ge - ef
    freq_range1 = 30e6
    freq_range2 = 30e6
    freqs = np.linspace(target_freq - freq_range1, target_freq + freq_range2, 101)
    amps = [.1] 
    powers = [5]
    shift_freq = np.zeros((len(amps), len(powers)))
    from FWM import FWM_f0g1
    for i, amp in enumerate(amps):
        for j, power in enumerate(powers):
            f0g1 = FWM_f0g1.FWM_f0g1(qubit_info, ef_info, fwm_gen, 1e3, 
                         freqs, power, amp, '3m1')
            f0g1.measure()
            shift_freq[i, j] = f0g1.xs[np.argmax(f0g1.ampdata[:])]
            
if 0: # Qubit population
    from single_qubit import qubit_pop
    dig.set_naverages(10000)
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    qp = qubit_pop.Qubit_Pop(qubit_info, ef_info, generate=True, seq=seq, proj_func='phase')
    qp.measure_keysight()
    print(qp.get_ys())
    
    
if 0: #f0 - g1 time domain
    fwm_gen = mclient.instruments['f0g1brick']
    from FWM import FWM_f0g1_t1
    f0g1 = FWM_f0g1_t1.FWM_f0g1_t1(qubit_info, ef_info, fwm_gen, np.linspace(0, 10e3, 101), 0.000001, '3m1', proj_func='phase')
    f0g1.measure_keysight()


    