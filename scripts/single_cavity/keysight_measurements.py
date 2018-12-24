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


qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')
os.chdir(r'C:/qrlab/scripts')

if 0: # test digitizer
    dig = mclient.instruments['dig']
    data = dig.test_dig(3000, 1, 1, 1)
    print(np.shape(data))
    plt.figure()
    plt.plot(data[0][0][:], label = 'sig')
    plt.plot(data[1][0][:], label = 'ref')
    plt.legend()
    plt.show()

if 1: # cav spec
    from single_cavity import rocavspectroscopy_keysight
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
    rofreq = 7.7194e9
    freq_range = 1.5e6
    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(3, 3, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 11),
                                             qubit_pulse=False, seq=None)
    ro.measure()
    bla
    
    
if 0: # calibrate TWPA
    SCpump = mclient.instruments['SCpump']
    from single_cavity import twpa_calibration_keysight
    twpa_powers = np.linspace(-5.4, -5.2, 7)
    twpa_freqs = np.linspace(6.19e9, 6.20e9, 7)
    tc = twpa_calibration_keysight.twpa_calibration_keysight(qubit_info, 3, 7.71953e9, twpa_powers, 
                                           twpa_freqs, SCpump, qubit_pulse=False)
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
    

if 0:
    from single_qubit import spectroscopy_keysight
#    from scripts.single_qubit import spectroscopy_IQ
#    for i in range(5560, 5560, 0)
    qubit_freq = 400.3e6
    freq_range = 100e6
    spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['QK'], qubit_info,
                                     np.linspace(qubit_freq-freq_range,
                                                 qubit_freq+freq_range, 201),
                                     [4],
                                     plen= 5000, amp=0.1, plot_seqs=False) 
    spec.measure()


    
    
    

if 0: # SSB spec
    from single_qubit import ssbspec
    seq = sequencer.Trigger(250)

    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-1e6, 1e6, 51), seq=seq, plot_seqs=False)
    spec.measure_keysight()

    
    
if 0: # Calibrate pi pulse

    from single_qubit import rabi
    tr = rabi.Rabi(qubit_info, 
#                   np.linspace(-.08, .08, 100), selective=True,
                   np.linspace(-.4, .4, 51), selective=True,
                   plot_seqs=False, generate=True, repeat_pulse=1, update=True)
    tr.measure_keysight()

    
if 0: # T1
    from single_qubit import T1measurement

    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 100e3, 61), 
                                     double_exp=False, generate=True, plot_seqs=False)
    t1.measure_keysight()

if 0:
    from scripts.single_qubit import ssbspec
    from scripts.single_qubit import rabi
    from scripts.single_qubit import T1measurement
    powers = np.linspace(-20, 10, 2)
    frequencies = np.linspace(120, 180, 3)

    
if 0: # T2
    from single_qubit import T2measurement
    postseq = sequencer.Delay(500)
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 8e3, 61), detune=0.8e6, double_freq=False, generate=True, postseq=postseq)
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
    postseq = sequencer.Delay(500)
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 28e3, 171), detune=0.2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True, postseq=postseq)
    t2.measure_keysight()
    bla  
    
if 0: # EF SSBspec
    from single_qubit import ssbspec
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    spec = ssbspec.SSBSpec(ef_info, np.linspace(-3e6, 3e6, 61), seq=seq, postseq = postseq, extra_info=qubit_info, plot_seqs=False, generate=True)
    spec.measure_keysight()
    bla
    
if 0: # EF rabi 
    from single_qubit import efrabi
    dig = mclient.instruments['dig']
#    dig.set_naverages(2000)
    postseq = sequencer.Delay(300)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.4, 0.4, 101), plot_seqs=False, selective=False, generate=True, postseq = postseq)
    efr.measure_keysight()
    period = efr.fit_params['period'].value
#    dig.set_naverages(4000)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.4, 0.4, 101), first_pi=False, selective=False, force_period=period, postseq= postseq, generate=True)
    efr.measure_keysight()
#    dig.set_naverages(1000)
    bla
    
if 0: # FT1
    from single_qubit import FT1measurement
    #ft1times = np.zeros(len(range(20)))
    for i in range(1):
        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.linspace(0, 120e3, 101))
        ft1.measure_keysight()
        #ft1times[i] = ft1.analyze()
        #plt.close()
    bla


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
    

    