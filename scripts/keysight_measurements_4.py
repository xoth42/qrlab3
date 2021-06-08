# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 14:53:09 2018

@author: wanglab111
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
import datetime

#fxb01 = mclient.get_qubit_info('fxb01')
#fxa01 = mclient.get_qubit_info('fxa01')

qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
readout = 'readout_IQ'
#fh_info = mclient.get_qubit_info('qubit1fh')
#qubit_a1 = mclient.get_qubit_info('qubit_a1')
#qubit_a1b1 = mclient.get_qubit_info('qubit_a1b1')
#qubit_a2b2 = mclient.get_qubit_info('qubit_a2b2')
#qubit_a3b3 = mclient.get_qubit_info('qubit_a3b3')

#qubit_b1 = mclient.get_qubit_info('qubit_b1')

#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')
os.chdir(r'C:/qrlab/scripts')
    
if 0: # test digitizer
    dig = mclient.instruments['dig']
    data = dig.test_dig(4000, 1, 1, 1)
    print(np.shape(data))
    plt.figure()
    plt.plot(data[0][0][:], label = 'sig')
    plt.plot(data[1][0][:], label = 'ref')
    plt.legend() 
    plt.show() 
    bla
    
if 0: # test digitizer DEMODULATED
    dig = mclient.instruments['dig']
    avgs = dig.test_dig_demod(4000, 10000)
    print(np.shape(avgs))
    plt.figure()
    plt.plot(np.real(avgs), label = 'real')
    plt.plot(np.imag(avgs), label = 'imag')
    plt.plot(np.abs(avgs), label = 'abs')
    plt.legend() 
    plt.show()
    bla

if 0: # Check histogramming
    from scripts.single_qubit import rabi
    tr = rabi.Rabi(qubit_info, [qubit_info.pi_amp,], histogram=True, title='|e>',
                   readout=readout)
    tr.measure_keysight()
    tr = rabi.Rabi(qubit_info, [0.001,], histogram=True, title='|g>',
                   readout=readout)
    tr.measure_keysight()
    tr = rabi.Rabi(qubit_info, [qubit_info.pi_amp/2,], histogram=True, title='|g>+|e>',
                   readout=readout)
    tr.measure_keysight()
    bla


if 0: # Quantum Jump
    dig = mclient.instruments['dig']
    nsamples = 100
    navg = 70
    avgs = dig.test_dig_demod(nsamples*navg*10, 1)
    print(np.shape(avgs)) 
    ave10 = np.zeros(nsamples,dtype = 'complex64')
    for i in range(nsamples):
        ave10[i]=np.average(avgs[i*navg:(i+1)*navg])
#    plt.figure()
    plt.scatter(np.real(ave10),np.imag(ave10))
#    plt.plot(np.real(avgs), label = 'real')
#    plt.plot(np.imag(avgs), label = 'imag')
#    plt.plot(np.abs(avgs), label = 'abs')
    plt.xlim([-100,100])
    plt.ylim([-100,100])
    plt.legend() 
    plt.show()
    bla

if 0: # cav transmission NEW IQ
    from single_cavity import ROCavSpec_IQ
    freq_range =1.5e6
    df = np.linspace(-freq_range, freq_range, 61)
    amps = np.linspace(.8, .8, 1)
#    readout_IQ = mclient.instruments['readout_IQ']

    for i in range(1):    
#        readout_IQ.set_pi_amp(i)

        ro = ROCavSpec_IQ.ROCavSpec_IQ(qubit_info, amps, df,
                                       qubit_pulse=False, seq=None,
                                       readout = 'readout_IQ')
        ro.measure()
        
        '''amp = ro.ampdata[:]
        f= open('ampdata_2d_HP.txt', 'w')
        f.write(str(amp))
        f.close()'''
        
    bla



if 0: # cav transmission OLD
    from single_cavity import rocavspectroscopy_keysight
    
    rofreq = 7274.8e6
#    rofreq = 7320e6
    freq_range = 5e6
    freqs = np.linspace(rofreq-freq_range, rofreq+freq_range, 101)
    powers = np.linspace(-8,-6,1) # doesn't matter for readout_iq


    readout_IQ = mclient.instruments['readout_IQ']

    for i in [.04]:
        readout_IQ.set_amp(i)
        ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, powers, freqs,
                                                 qubit_pulse=False, seq=None, readout = readout,
                                                 plot_seqs = True)
        ro.measure()

    '''amp = ro.ampdata[:]
    f= open('ampdata_2d_HP.txt', 'w')
    f.write(str(amp))
    f.close()'''
    
    bla
 #f.open(' ')   

    
if 0: # calibrate TWPA
    TWPApump = mclient.instruments['WF_twpa']
    from single_cavity import twpa_calibration_keysight
    twpa_powers = np.linspace(-10, 0, 5)
    freq = 7.9175e9
    freq_range = 50e6
    twpa_freqs = np.linspace(freq-freq_range, freq+freq_range, 51)
    tc = twpa_calibration_keysight.twpa_calibration_keysight(qubit_info, 5, 7337.62e6, twpa_powers, 
                                           twpa_freqs, TWPApump, qubit_pulse=False, snr=False,
                                           readout=readout)
    tc.measure()
    tc.snr = True
    tc.analyze()
    bla

    
if 0: # Calibrate TWPA SNR
    def analysis(twpa_powers, twpa_freqs, ampdata, ax=None):
        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)
        data = ampdata[:]
        x, y = np.meshgrid(np.append(twpa_powers, 2* twpa_powers[-1] - twpa_powers[-2]),
                       np.append(twpa_freqs, 2* twpa_freqs[-1] - twpa_freqs[-2]))
        img = ax.pcolormesh(x, y, data.T)
        fig.colorbar(img)
        ax.set_xlabel('twpa powers')
        ax.set_ylabel('twpa frequencies')

    from single_qubit import rabi
    twpa_powers = np.linspace(-4.2, -4.0, 5)
    freq = 7.918e9
    freq_range = 3e6
    twpa_freqs = np.linspace(freq-freq_range, freq+freq_range, 7)
    naverages = 3000

    ampdata = np.zeros([len(twpa_powers), len(twpa_freqs)])
    stddata = np.zeros([len(twpa_powers), len(twpa_freqs)])
    snrdata = np.zeros([len(twpa_powers), len(twpa_freqs)])
    dig.set_naverages(naverages)    
    SCqubit.set_rf_on(False)
    
    for i, p in enumerate(twpa_powers):
        SCTWPA.set_power(p)
        for j, f in enumerate(twpa_freqs):
            SCTWPA.set_frequency(f)
            tr = rabi.Rabi(qubit_info, 
                   np.linspace(-0.9, 0.9, 41), selective=False,
                   plot_seqs=False, generate=True, repeat_pulse=1, update=False, seq=None)    
            tr.measure_keysight()
            IQ = tr.avg_data
            ampdata[i,j] = np.abs(IQ.mean())
            stddata[i,j] = np.std(IQ)
            snrdata[i,j] = np.abs(IQ.mean())/np.std(IQ)/np.sqrt(naverages)
            plt.close()
    analysis(twpa_powers, twpa_freqs, ampdata)
    analysis(twpa_powers, twpa_freqs, snrdata)
    bla
    
if 0: # IQ modulated RO?
    from single_cavity import rocavspectroscopy_keysight_IQmod
#    rofreq = 8553.1e6
    rofreq = 6000.00e6
    freq_range = 100e6
    
    ro = rocavspectroscopy_keysight_IQmod.ROCavSpectroscopy(qubit_info, RO_info, np.linspace(-10, -20, 3),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 55),
                                               plen=20000, amp=0.0001, qubit_pulse=False)
    ro.measure()
    bla
    

if 0: #qubit spectroscopy
    from single_qubit import spectroscopy_keysight
#    from scripts.single_qubit import spectroscopy_IQ
    
    qubit_freq = 4670e6

    freq_range = 150e6
    spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['SCqubit'], qubit_info,
                                     np.linspace(qubit_freq-freq_range,
                                                 qubit_freq+freq_range, 100),
#                                     [2.5, 5, 7.5],
                                     [13],
                                     plen=80000, amp=.71, plot_seqs=False, readout='readout_IQ') 

    spec.measure()
    SCqubit.set_frequency(qubit_freq)
    bla

if 0: # Qubit spec with phase correction
    from single_qubit import spectroscopy_keysight_phasecorrection
#    from scripts.single_qubit import spectroscopy_IQ
    qubit_freq = 946.889e6
    freq_range = 0e6
    spec = spectroscopy_keysight_phasecorrection.Spectroscopy_Keysight_phasecorrection(mclient.instruments['QK'], qubit_info,
                                     np.linspace(qubit_freq-freq_range, qubit_freq+freq_range, 61), [-18],
                                     plen=10000, amp=0.1, plot_seqs=False) #1=1ns

#    spec = spectroscopy_IQ.Spectroscopy_IQ(client.instruments['gen'], qubit_info,
#                                     np.linspace(702e6, 710e6, 81), [-30],
#                                    plen=250*100, amp=0.1, ssb=False, plot_seqs=False)

    spec.measure()
    
    bla    
    

if 0: # qubit SSB spec
    from single_qubit import ssbspec
#for i in range(5):
    #dig.set_naverages(5000)
#    readout_driver = mclient.instruments.get(readout)
#    seq = sequencer.Sequence([sequencer.Trigger(400), s
#                              sequencer.Delay(10e3)])
    spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
                                        np.linspace(-10e6, -7.5e6, 71),
#                                        np.linspace(-100e6, -50e6, 111), 
#                                       np.linspace(-5e6,1e6, 101),
                                       np.linspace(-2.8e6, 1e6, 101),
#                                            np.linspace(-1.2e6, 1.2e6, 101),
                                       )), 
                           seq=None, plot_seqs=False, readout='readout_IQ',
#                           extra_info = [cavity_infoB, qubit_b0s, qubit_b2s, qubit_b4s, fwm_info, fwm_info_b2, fwm_info_b4]
                           )
    spec.measure_keysight()
    bla
    


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
     
    
if 0: # Calibrate pi pulse
    from single_qubit import rabi
#    dig.set_naverages(1000)
#    dig.set_trigger_period(100)
    tr = rabi.Rabi(qubit_info, 
#                   np.linspace(-.99, .99, 51), selective=False,
#                   np.linspace(-.2, .2, 51), selective=.5,
#                  np.linspace(-0.06, 0.06, 51), selective=True,
#                   np.linspace(.38, .5, 51), selective=False,
                   np.linspace(0, 0, 1), selective=False,
                   plot_seqs=True, generate=True, repeat_pulse=1, update=False, 
                   seq=None, readout='readout_IQ')
    tr.measure()
    bla
    
if 0: # Time Rabi
    from scripts.single_qubit import timerabi
    tr = timerabi.TimeRabi(qubit_info, np.linspace(1, 200, 51), amp=0.87)
    data = tr.measure_keysight()
    bla

    
if 0: # T1
#    dig.set_trigger_period(500)
    from single_qubit import T1measurement
    t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 19e3, 20), 
                                                                 np.linspace(20e3, 160e3, 31))), 
#    t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 90e3, 101),)), 
                                     double_exp=False, generate=True, plot_seqs=False, seq=None, 
                                     readout='readout_IQ')
    t1.measure()
    

if 0: # T2
    from single_qubit import T2measurement
    for i in range(1):
#        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0e3, 15e3, 91), detune=2e6, 
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 55e3, 101), detune=.1e6, 
                                         double_freq=False, generate=True, seq=None,
                                         plot_seqs=False, readout='readout_IQ')
        t2.measure_keysight()
#        plt.close(t2.get_figure())

    
    
if 0: # T2echo
    from single_qubit import T2measurement

    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0.01e3,65e3, 101),
#                                     np.concatenate((np.linspace(0, 3.9e3, 14), np.linspace(8e3, 50e3, 81))), 
                                     detune=0.1e6, double_freq=False,
                                     echotype = T2measurement.ECHO_HAHN, necho=1, 
                                     plot_seqs = False, generate=True, readout=readout)
    t2.measure_keysight()
    bla  


if 0: # EF SSBspec
    from single_qubit import ssbspec
    seq = sequencer.Sequence([sequencer.Trigger(400), qubit_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    spec = ssbspec.SSBSpec(ef_info, np.linspace(-2e6, 2e6, 71), seq=seq, postseq = postseq, 
                           extra_info=qubit_info, 
                           plot_seqs=False, generate=True, readout='readout_IQ')
    spec.measure_keysight()
    bla

if 0: # FH SSBspec
    from single_qubit import ssbspec
    seq = sequencer.Sequence([sequencer.Trigger(400), qubit_info.rotate(np.pi, 0), ef_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
    postseq = sequencer.Sequence([ef_info.rotate(np.pi, 0), qubit_info.rotate(np.pi, 0)])
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    spec = ssbspec.SSBSpec(fh_info, np.linspace(-2e6, 2e6, 101), seq=seq, postseq = postseq, extra_info=[qubit_info,ef_info], plot_seqs=False, generate=True)
    spec.measure_keysight()
    bla
    
if 0: # EF rabi for pop
    from single_qubit import efrabi
    dig = mclient.instruments['dig']
    dig.set_naverages(1000)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.9, 0.9, 51), plot_seqs=False, 
                        selective=False, generate=True, postseq = None, update=False, readout='readout_IQ')
    efr.measure_keysight()
    period = efr.fit_params['period'].value
    dig.set_naverages(5000)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.9, 0.9, 51), first_pi=False, 
                        selective=False, force_period=period, postseq= None, generate=True, readout='readout_IQ')
    efr.measure_keysight()
    dig.set_naverages(1000)

if 0: # EF rabi for calibration
    from single_qubit import efrabi
#    dig = mclient.instruments['dig']
#    dig.set_naverages(200)
    dig.set_trigger_period(100)
    efr = efrabi.EFRabi(qubit_info, ef_info, 
#                   np.linspace(-0.9, 0.9, 51), selective=False,
                   np.linspace(-0.06, 0.06, 51), selective=True,
#                   np.linspace(0.4, .6, 51), selective=False,
#                   np.linspace(0.45, 0.52, 51), selective=False,
                        repeat_pulse=1, generate=True, postseq = None, update=False, readout='readout_IQ')
    efr.measure_keysight()
    bla

if 0: # drag_test 
    from single_qubit import drag_test
    coeffs = np.linspace(-1,1,51)
    drg = drag_test.drag_test(qubit_info, coeffs, readout='readout_IQ')
    drg.measure_keysight()

if 0: # FH rabi 
    from single_qubit import efrabi
    dig = mclient.instruments['dig']
    seq = sequencer.Sequence([sequencer.Trigger(400), qubit_info.rotate(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))                      
    dig.set_naverages(1000)
    fhr = efrabi.EFRabi(ef_info, fh_info, np.linspace(-0.7, 0.7, 51), plot_seqs=False, selective=False, seq=seq, postseq = postseq, 
                        update=True, extra_info = qubit_info)
    fhr.measure_keysight()
    period = fhr.fit_params['period'].value
    dig.set_naverages(20000)
    fhr = efrabi.EFRabi(ef_info, fh_info, np.linspace(-0.7, 0.7, 51), first_pi=False, selective=False, force_period=period, seq=seq, postseq= postseq, 
                        generate=True, extra_info = qubit_info)
    fhr.measure_keysight()
    dig.set_naverages(1000)

    
if 0: # FT1
    from single_qubit import FT1measurement
    #ft1times = np.zeros(len(range(20)))
    for i in range(1):
        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.linspace(0, 40e3, 101), 
                                            readout=readout)
        ft1.measure_keysight()
        #ft1times[i] = ft1.analyze()
        #plt.close()
    bla

if 0: # EFT2
    from single_qubit import EFT2measurement

    eft2 = EFT2measurement.EFT2Measurement(qubit_info, ef_info, np.linspace(.1e3, 5e3, 121),
                                           detune=2e6, 
                                           double_freq=True, generate=True, seq=None, readout=readout)
    eft2.measure_keysight()
    bla


#def dynamic_ssb(qubit_info, step = .1e6, plotting = True):
#    from scripts.single_qubit import ssbspec
#    seq = sequencer.Trigger(250)
#
#    not_found = True
#    high_pass = False
#    high_mark = 0
#    low_mark = 0
#    while not_found:
#        if high_pass and high_mark <= 60e6:
#            freqs = np.arange(high_mark-1e6, high_mark + 20e6, step)
#            high_mark += 20e6
#            high_pass = False
#        else:
#            freqs = np.arange(low_mark - 20e6, low_mark+1e6, step)
#            low_mark -= 20e6
#            high_pass = True
#        spec = ssbspec.SSBSpec(qubit_info, freqs, seq=seq, plot_seqs=False)
#        spec.measure_keysight()
#        ys = spec.get_ys()
#        plt.axhline(np.mean(ys) + np.std(ys)*3)
#        plt.axhline(np.mean(ys) - np.std(ys)*3)
#        if not plotting:
#            plt.close()
#        if (np.abs(np.min(ys) - np.mean(ys)) > np.std(ys)*3):
#            not_found = False
#            guess = freqs[np.argmin(ys)]
#        elif(low_mark <= -150e6):
#            return None
#        
#    
#    final_freqs = np.linspace(guess-step*10, guess+step*10, 100)
#    final_spec = ssbspec.SSBSpec(qubit_info, final_freqs, seq=seq, plot_seqs=False)
#    final_spec.measure_keysight()
#    if not plotting:
#        plt.close()
#    return final_freqs[np.argmin(final_spec.get_ys())]


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
    
    
if 0: #Contrast normalization. This simply gives an array of 5 ground and 5 excited state points measurement. 
    
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
    dig.do_set_naverages(2000)
    dtest = drag_test.drag_test(qubit_info, np.linspace(-1.5, 1.5, 81), plot_seqs=False, generate=True)
    data=dtest.measure_keysight()
    bla


    
if 0: # AllXY
#    for i in range (1):
#        from scripts.single_qubit import rabi
#        tr = rabi.Rabi(qubit_info, np.linspace(0, 0.2, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
#                       update=True)
#        data=tr.measure()

    dig.do_set_naverages(5000)
    from single_qubit import allxy
    allxy_result = []
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(-np.pi/2, 0)]) #this whole line was added
    axy = allxy.All_XY(qubit_info, seq=None, generate=True)  #seq=seq was added
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
#    bla
    
if 0: # Randomized benchmarking   

    from scripts.single_qubit import randbench
    from scripts.single_qubit import contrast_normalization  #This part is is only necessary when we want a separate ground and excited state measurement before the RB.
    run_number = 15 #How many RB runs to be completed
    rndmben_result = []
    
    
#To be commented out for the above preliminary measurement.
#    cn_result=np.zeros(shape=(run_number,10))
#    cn_result = np.array(cn_result)
#
#    

#        dig.do_set_naverages(5000)
#        p_seq = sequencer.Sequence(sequencer.Delay(80))
#        cn = contrast_normalization.Contrast_Normalization(qubit_info, process_seq=p_seq, generate=True, proj_func='phase')
#        cn.measure_keysight()
#        cn_result[i,:]= cn.get_ys()
#        #These are horribly sketcky, I need to clean those later. 
#        ground_voltage = (cn_result[i][0] +  cn_result[i][1] + cn_result[i][2] + cn_result[i][3] + cn_result[i][4])/5
#        excited_voltage = (cn_result[i][5] + cn_result[i][6] + cn_result[i][7] + cn_result[i][8] + cn_result[i][9])/5
        
    dig.do_set_naverages(60000)
    for i in range(run_number):
        rndmben = randbench.rndm(qubit_info, num_cal_points=20, n_gates_start=1, n_gates_stop= 301, n_gates_step=3, seq=None, generate=True, proj_func='phase') #seq=seq added
        rndmben.measure_keysight()
        
        
#        normalized_result = (rndmben.get_ys() - rndmben.) / (rndmben.excited_voltage - rndmben.ground_voltage)
        rndmben_result.append(rndmben.get_ys())
        

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
    

if 1: # overnight coherence measurements
    from single_qubit import T1measurement
    from single_qubit import T2measurement
    from single_qubit import efrabi
    from single_qubit import FT1measurement
    from single_qubit import EFT2measurement
    dig.set_trigger_period(500)
    dig.set_naverages(1000)
    for i in range(100000):
        
        t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 19e3, 20), 
                                                                     np.linspace(20e3, 160e3, 31))), 
                                         double_exp=False, generate=True, plot_seqs=False, seq=None, 
                                         readout='readout_IQ')
        t1.measure()
        
        
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 55e3, 121), detune=.1e6, 
                                         double_freq=False, generate=True, seq=None,
                                         plot_seqs=False, readout='readout_IQ')
        t2.measure_keysight()
        
        t2e = T2measurement.T2Measurement(qubit_info, np.linspace(0.01e3, 65e3, 121),
                                         detune=0.1e6, double_freq=False,
                                         echotype = T2measurement.ECHO_HAHN, necho=1, 
                                         plot_seqs = False, generate=True, readout=readout)
        t2e.measure_keysight()
        
        
        dig.set_naverages(1000)
        efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.9, 0.9, 51), plot_seqs=False, 
                            selective=False, generate=True, postseq = None, update=False, readout='readout_IQ')
        efr.measure_keysight()
        period = efr.fit_params['period'].value
        dig.set_naverages(5000)
        efr2 = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.9, 0.9, 51), first_pi=False, 
                            selective=False, force_period=period, postseq= None, generate=True, readout='readout_IQ')
        efr2.measure_keysight()
        dig.set_naverages(1000)
        
        
        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.linspace(0, 40e3, 101), 
                                            readout=readout)
        ft1.measure_keysight()
    

        ft2 = EFT2measurement.EFT2Measurement(qubit_info, ef_info, np.linspace(.1e3, 10e3, 151),
                                               detune=2e6, 
                                               double_freq=True, generate=True, seq=None, readout=readout)
        ft2.measure_keysight()
        
        plt.close(t1.get_figure())
        plt.close(t2.get_figure())
        plt.close(t2e.get_figure())
        plt.close(efr.get_figure())
        plt.close(efr2.get_figure())
        plt.close(ft1.get_figure())
        plt.close(ft2.get_figure())

