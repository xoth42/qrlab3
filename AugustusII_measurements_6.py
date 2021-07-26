# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 10:19:22 2019

@author: Ebru
"""
from . import mclient
import numpy as np
from .pulseseq import sequencer, pulselib
import matplotlib
import matplotlib.pyplot as plt
import math 
import time
import lmfit


import os
os.chdir(r'c:\qrlab-3')


alz = mclient.instruments['alazar']
yoko = mclient.instruments['yoko']
gaius01 = mclient.instruments['gaius01']
coolgen= mclient.instruments['cool']
ZZ = mclient.instruments['ZZ']

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
qubit_info2 = mclient.get_qubit_info('qubit1ge_2')
efinfo = mclient.get_qubit_info('efinfo')
gate_info1 = mclient.get_gate_info('sq_gate1')
gate_info2 = mclient.get_gate_info('sq_gate2')
ZZ_info = mclient.get_gate_info('ZZ_gate')
gate_info1 = mclient.get_gate_info('sq_gate1')
gate_info2 = mclient.get_gate_info('sq_gate2')

K= []


#ef_info = mclient.get_qubit_info('qubit1ef')
qubit2_info = mclient.get_qubit_info('qubit2ge')
qubit2_info2 = mclient.get_qubit_info('qubit2ge_2')
#f0g1 cooling parameters
#cool_time=25e3
#coolamp = 0.1
#cool = sequencer.Combined([sequencer.Constant(int(cool_time), coolamp, chan=ef_info.sideband_channels[0]),
#                           sequencer.Constant(int(cool_time), coolamp, chan=ef_info.sideband_channels[1]),
#                           sequencer.Constant(int(cool_time),1,chan='3m1')])



if 0: # RO Cavity spec
    from .scripts.single_cavity import rocavspectroscopy
#    rofreq = 7515.5e6
    alz.set_naverages(1000)
    rofreq = 7.56e9#7570.6e6
    freq_range = 15e6#20e6
    ro = rocavspectroscopy.ROCavSpectroscopy(qubit_info, [5],
                                         np.linspace(rofreq - freq_range, rofreq + freq_range,81),
                                         qubit_pulse=False)
    ro.measure()
    
    
    freq, amp, phase = ro.freqs, ro.ampdata[0], ro.phasedata[0]
    phase = np.unwrap(phase, discont=180)
    a,b = np.polyfit(freq,phase,1)
    fig, axes = plt.subplots(nrows=2, sharex=True)
    axes[0].plot(freq, amp)
    axes[1].plot(freq, phase-(a*freq+b))
    
    
    bla
    

if 0: # RO Cavity spec Signal optimization
    from .scripts.single_cavity import rocavspectroscopy
#    rofreq = 7515.5e6
    rofreq =  7560820000.0
    freq_range = 20e6#20e6
    
    alz.set_naverages(1000)

   
    ro = rocavspectroscopy.ROCavSpectroscopy(qubit_info, [5],
                                         np.linspace(rofreq - freq_range, rofreq + freq_range,151),
                                         qubit_pulse=False)
    ro.measure()
    
    freq0, amp0, phase0 = ro.freqs, ro.ampdata[0], ro.phasedata[0]
    phase0 = np.unwrap(phase0, discont=180)
    a0,b0 = np.polyfit(freq0,phase0,1)
    fig, axes = plt.subplots(nrows=2, sharex=True)
    axes[0].plot(freq0, amp0)
    axes[1].plot(freq0, phase0-(a0*freq0+b0))
    
    fig.suptitle('RO Cavity Spec w/o qubit drive')
    axes[0].set_ylabel('Amplitude')
    axes[1].set_ylabel('Phase')
    axes[0].set_xlabel('Frequency')
  #  axes[1].plot(freq0, phase0)
    

    ro = rocavspectroscopy.ROCavSpectroscopy(qubit_info, [5],
                                         np.linspace(rofreq - freq_range, rofreq + freq_range,151),
                                         qubit_pulse=True)
    ro.measure()
    
    freq1, amp1, phase1 = ro.freqs, ro.ampdata[0], ro.phasedata[0]
    phase1 = np.unwrap(phase1, discont=181)
    a1,b1 = np.polyfit(freq1,phase1,1)
    axes[0].plot(freq1, amp1)
    axes[1].plot(freq1, phase1-(a1*freq1+b1))    
    
    fig.suptitle('RO Cavity Spec w/ qubit drive')
    axes[0].set_ylabel('Amplitude')
    axes[1].set_ylabel('Phase')
    axes[0].set_xlabel('Frequency')
   # axes[1].plot(freq1, phase1)    
    
    fig, axes = plt.subplots(nrows=2, sharex=True)
    damp = amp1-amp0
    i_ampOpt = np.abs(damp).argmax()
    
    dphase = phase1-(a1*freq1+b1)-phase0+(a0*freq0+b0)
    i_phaOpt = np.abs(dphase).argmax()

    axes[0].plot(freq0, damp)
    axes[0].axvline(x=freq0[i_ampOpt],
        label='Opt: f={:.4f} GHz'.format(freq0[i_ampOpt]*1e-9),
        color='k', ls='--')
    axes[1].plot(freq0, dphase)
    axes[1].axvline(x=freq0[i_phaOpt],
        label='Opt: f={:.4f} GHz'.format(freq0[i_phaOpt]*1e-9),
        color='k', ls='--')

    

    fig.suptitle('RO Cavity Spec w/ and w/o qubit drive')
    axes[0].set_ylabel('Amplitude difference')
    axes[1].set_ylabel('Phase shift')
    axes[1].set_xlabel('Frequency')
    axes[0].legend()
    axes[1].legend()
   # axes[1].plot(freq0, phase1-phase0)

    
    
    bla
    
if 0:# Qubit spec
    alz.set_naverages(3000)

    from .scripts.single_qubit import spectroscopy
    cool = sequencer.Constant(int(6e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    postseq = gate_info2.rotate(np.pi,0)
    qubit_freq = 3.520e9#+600e6
    freq_range = 40e6#e6
    spec = spectroscopy.Spectroscopy(mclient.instruments['cool'], qubit_info,
                                         np.linspace(qubit_freq-freq_range,
                                                     qubit_freq+freq_range,81),
                                             [5],
                                        plen=20000, amp=0.00005, seq=None,  postseq=None, plot_seqs=False, extra_info=gate_info2) #1=1ns for plen
    spec.measure()
    bla    

    
    
    
if 0: # Qubit spec with phase correction
    from .scripts.single_qubit import spectroscopy_phasecorrection
#    from scripts.single_qubit im6port spectroscopy_IQ
    qubit_freq = 3.4875e9+600e6
    freq_range = 10e6
    spec = spectroscopy_phasecorrection.Spectroscopy_phasecorrection(mclient.instruments['gaius01'], qubit_info,
                                     np.linspace(qubit_freq-freq_range,
                                                 qubit_freq+freq_range, 21),
                                     [-8],
                                     plen=1000, amp=0.1, plot_seqs=False) #1=1ns for plen
    spec.measure()
    bla
        
"""Qubit SSBspec"""
if 0:# Qubit SSBspec
    from .scripts.single_qubit import ssbspec
#    for freq in np.linspace(3.508e9,3.516e+09,21): # 4e3 before
#        coolgen.set_frequency(freq)
    for len in [5e3]:
        cool = sequencer.Constant(int(len),1,chan='3m1')
        seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
        seq_coolRO = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(int(20e3),1,chan='4m1'), sequencer.Delay(150)])
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(2000), qubit2_info.rotate(np.pi,0)])
        postseq = qubit2_info2.rotate(np.pi/2,0)
#        coolgen.set_power(power)
#    for freq in np.linspace(3.380e9,3.450e9,1):
        alz.set_naverages(2000)
    #            coolgen.set_frequency(freq)
    #            cool = sequencer.Constant(int(8e3),1,chan='3m1')
    #        seq = sequencer.Join([sequencer.Trigger(250),
    #                                  qubit_info2.rotate(np.pi, 0)])
    
    
       # fig, ax = plt.subplots(1,1)
#        while True
        spec = ssbspec.SSBSpec(qubit_info, np.linspace(-1.5e6,1.5e6,81), proj_func='phase', seq=seq_cool,
                               postseq=None, extra_info=[qubit_info,qubit2_info2])
        spec.measure()
        
           # x, dx = spec.fit_params['center1'], spec.fit_params['sigma']
            
          #  ax.errorbar(time.time()-t0,x, yerr=dx, marker='o', fillstyle='none', color='k', capsize=3)
          #  fig.canvas.draw()
        
    #            plt.close()
    #    spec.measure_keysight()
    bla
    
    
    """Power Rabi -- Pi pulse calibration"""

if 0: # Calibrate pi pulse
    from .scripts.single_qubit import rabi
#    cool = sequencer.Constant(int(4e3),1,chan='3m1')
#    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    alz.set_naverages(4000)
   # for freq in np.linspace(3.35e9,3.39e+09,81): # 4e3 before
#    for len in [10e3]:
   #     coolgen.set_frequency(freq)
   #     cool = sequencer.Constant(int(10e3),1,chan='3m1')
   #     seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
#

#    for x in np.linspace(7.54741e9,7.54770e9,30):
#    for cool_time in [0.00001e3, 5e3, 10e3, 50e3, 100e3]:
#        cool = sequencer.Constant(int(cool_time),1,chan='3m1')
#    seq = sequencer.Join([sequencer.Trigger(250), qubit_info.rotate(np.pi,0)])
                #            for coolamp in [0.05, 0.1, 0.3, 0.8]:
        
        #    postseq = sequencer.Join((ef_info.rotate(np.pi, 0), sequencer.Delay(20000)))
        #        for power in [-5]:
        #            cool_gaius.set_power(po wer)
        #        for cool_time in [0,2e3,10e3,20e3]:
#        tr = rabi.Rabi(qubit2_info, np.linspace(-0.55, 0.55, 71), selective=False,
#            #                   np.linspace(0.75, 0.95, 101), selective=False,
#            #                           np.linspace(-0.2, 0.2, 61), selective=True,
#                               plot_seqs=False, generate=True, repeat_pulse=1,
#                               update=True, seq=None,
#                               postseq=None, proj_func='phase')
#        data=tr.measure()
#        RObrick.do_set_frequency(x)
#        refbrick.do_set_frequency(x+50e6)
#    cool = sequencer.Constant(int(6e3),1,chan='3m1')
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(200)])
#
    cool = sequencer.Constant(int(5e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    seq_coolRO = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(int(10e3),1,chan='4m1'), sequencer.Delay(150)])
#
#    postseq = qubit2_info.rotate(np.pi/2,0)

#    for i in range(1):
#        cool = sequencer.Constant(int(4e3),1,chan='3m1')
##        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), sequencer.Combined([gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)]), qubit_info3.rotate(np.pi,0)])# qubit2_info.rotate(np.pi, 0)])
#        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)])
##        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info1.rotate(np.pi,0)])
#        postseq = sequencer.Join([gate_info1.rotate(np.pi,0)])
#        postseq = sequencer.Combined([gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)])
#    for i in range(1): 
#        M =np.empty(3)
#        WF_xxx.set_rf_on(0)
#        for wf_power in np.linspace(-5.35408,-5.45,1):
#            WF_xxx.set_power(wf_power)
#            for wf_freq in np.linspace(7.904615e9,7.90461e9,1):
#                WF_xxx.set_frequency(wf_fre6q)
   # powers = np.sort(np.hstack((-np.logspace(-3, 0, 30), [0],  np.logspace(-3, 0, 30)))) #np.linspace(-0.1,0.1, 61)
    powers = np.linspace(-0.05,0.05,41)/1#*15/100*1.3
  #  powers = np.linspace(-10e-3,10e-3,41)
 #   powers = [0.07,-0.07]*10#*15/100*1.3
   # powers = [0.06,-0.06]*10#np.linspace(-0.06,0.06,41)/1#*15/100*1.3
#    powers = np.linspace(-0.1,0.1,11)/1
#    powers = np.array([1,0.99]*20)
   # powers = np.array([0.06]*41)
   # powers = np.ones(20)
#    while True:
    tr = rabi.Rabi(qubit_info2, powers, selective=False,
            #                   np.linspace(0.75, 0.95, 101), selective=False,
            #                           np.linspace(-0.2, 0.2, 61), selective=True,
                               plot_seqs=False, generate=True, repeat_pulse=1,  #n=3 has a bug
                               update=True, seq=seq_cool,
                               postseq=None, proj_func='phase', extra_info=[gate_info1, gate_info2, qubit2_info])
    data=tr.measure()
#    time.sleep(5)
#                amp=tr.fit_params['amp'].value
#                K=[]
#                K.append(wf_power)
#                K.append(wf_freq)
#                K.append(amp)
#                K=np.array(K)
#                M = np.vstack((M,K))
#                time.sleep(1)
#                plt.close('all')
    bla   
    
if 0: # Rabi calib vs freq
    from .scripts.single_qubit import rabi
#    cool = sequencer.Constant(int(4e3),1,chan='3m1')
#    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    alz.set_naverages(10000)
    freq_list = np.arange(973e6, 979e6, 0.25e6)
    for freq in freq_list:
        SCsource.set_frequency(freq)
        powers = np.linspace(-1,1,11)
       # powers = np.logspace(-4, 0, 21)
        tr = rabi.Rabi(qubit_info, powers, selective=False,
                #                   np.linspace(0.75, 0.95, 101), selective=False,
                #                           np.linspace(-0.2, 0.2, 61), selective=True,
                                   plot_seqs=False, generate=True, repeat_pulse=1,  #n=3 has a bug
                                   update=True, seq=None,
                                   postseq=None, proj_func='phase', extra_info=[gate_info1, gate_info2])
        data=tr.measure()
#    time.sleep(5)
    


if 0: # Time Rabi
    from .scripts.single_qubit import timerabi
    alz.set_naverages(3000)
    cool = sequencer.Constant(int(5e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), qubit2_info2.rotate(np.pi,0)])   
#    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info2.rotate(np.pi,0)])    
#    postseq =  qubit_info2.rotate(np.pi,0)
#    postseq =  sequencer.Combined([gate_info1.rotate(np.pi,0), gate_info2.rotate(np.pi,0)])
    tr = timerabi.TimeRabi(qubit_info, np.linspace(1,400, 61), amp=0.29,#0.12, 
                           seq=seq_cool, postseq=None, proj_func='phase', plot_seqs=False, extra_info=qubit2_info2) #extra_info=[gate_info1, gate_info2])
    data = tr.measure()
    bla


    
    
if 0: # Qubit EFspec - ef_info is not defined
    from .scripts.single_qubit import spectroscopy
    ef_freq = 3295e6
    freq_range = 6e6
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
    spec = spectroscopy.Spectroscopy(mclient.instruments['gaius12'], ef_info, np.linspace(ef_freq-freq_range, ef_freq+freq_range, 11), [-8],
                                     plen=5000, amp=0.01,
                                     seq=None, postseq=None,
                                     extra_info=qubit_info, plot_seqs=False)
    spec.measure()
    bla


if 0: # EF SSBspec
    from .scripts.single_qubit import ssbspec
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150),  gate_info2.rotate(np.pi,0)])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150),  gate_info1.rotate(np.pi,0)])
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150),  gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)])# qubit2_info.rotate(np.pi, 0)])
#    for postseq in [None, sequencer.Join([gate_info1.rotate(np.pi,0)]), sequencer.Join([gate_info2.rotate(np.pi,0)]), sequencer.Join([gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)])]:
    postseq = sequencer.Join([gate_info1.rotate(np.pi,0)])
#    postseq = sequencer.Combined([gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)])
    spec = ssbspec.SSBSpec(qubit_info3, np.linspace(-15e6, 15e6, 101), seq=seq, postseq = postseq, extra_info=[gate_info2, gate_info1], plot_seqs=False, generate=True, proj_func='phase')
    spec.measure()
    bla

if 0: # EF rabi   #manipulated this because i use it for the pre (red) pulse for the blue transition - ebru
    from .scripts.single_qubit import efrabi
    for i in range(1):
        alz.set_naverages(1000)
        efr = efrabi.EFRabi(qubit_info, qubit2_info2, np.linspace(-0.4, 0.4, 101),  seq = None, plot_seqs=False, second_pi=False, selective=False, generate=True, update=True,
                             proj_func='phase')
        efr.measure()
#        period = efr.fit_params['period'].value
#        alz.set_naverages(50000)
#        efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.08, 0.08, 51), first_pi=False, selective=False, force_period=period, generate=True,
#                            proj_func='phase')
#        efr.measure()
#        alz.set_naverages(5000)
    bla

if 0: # Single qubit tomography

    from .scripts.single_qubit import Single_qubit_tomo
    tomo_result = []
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(-np.pi/2, 0)]) #this whole line was added
    sqtomo = Single_qubit_tomo.Single_qubit_tomo(qubit_info, seq=None, generate=True)  #seq=seq was added
    sqtomo.measure()
    tomo_result.append(sqtomo.get_ys())
    for i in range(5):
        sqtomo = Single_qubit_tomo.Single_qubit_tomo(qubit_info, seq=None, generate=False) #seq=seq added
        sqtomo.measure()
        tomo_result.append(sqtomo.get_ys())
        plt.close()
    print(tomo_result)
    bla

if 0: # Process_tomography
    from .scripts.single_qubit import Process_tomo
    ptomo_result = []
    p_seq = sequencer.Sequence(sequencer.Delay(80))
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(-np.pi/2, 0)]) #this whole line was added
    sqtomo = Process_tomo.Process_tomo(qubit_info, process_seq=p_seq, generate=True)  #seq=seq was added
    sqtomo.measure()

    ptomo_result.append(sqtomo.get_ys())
    plt.close()

    print(ptomo_result)
    bla

if 0:# Drag test
    from .scripts.single_qubit import drag_test
    dtest = drag_test.drag_test(qubit_info, np.linspace(-2, 2, 41), plot_seqs=False, generate=True, proj_func='phase', seq=seq_cool)
    data=dtest.measure()
    bla

if 0: # AllXY  # there is a separate allxy with a pre pulse for the blue transition, don't change this one
    from .scripts.single_qubit import allxy
    cool = sequencer.Constant(int(8e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    
#    allxy_result = np.zeros((N, 42))
    alz.set_naverages(30000)
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(-np.pi/2, 0)]) #this whole line was added
    allxy_result =[]
    axy = allxy.All_XY(qubit_info, seq=seq, generate=True, proj_func='phase')  #seq=seq was added
    axy.measure()
    #        allxy_result[i,:] = axy.get_ys()
    allxy_result = axy.get_ys()
    plt.plot(allxy_result)
#    plt.figure()
##    for i in range(N):
#        plt.plot(allxy_result[i,:])
    alz.set_naverages(4000)
#    bla

if 0: # Randomized benchmarking
    from .scripts.fluxonium import randbench
    rndmben_result = []
    cool = sequencer.Constant(int(8e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), 
#                          qubit2_info.rotate(np.pi2,0)
                          ])
    postseq=qubit2_info.rotate(np.pi,0)

    alz.set_naverages(1000)
    for i in range(1):
        rndmben = randbench.rndm(qubit2_info, num_cal_points=3, n_gates_start=1, n_gates_stop=11, n_gates_step=1, seq=seq, postseq=None, generate=True, proj_func='phase', extra_info=qubit2_info) #seq=seq added
        rndmben.measure()
        rndmben_result.append(rndmben.get_ys())
        rndmben_complex_result.append(rndmben.avg_data)

#        plt.close()
#        plt.figure()
#        plt.plot(rndmben.xs, rndmben.get_ys())#, linestyle=None)
#    print rndmben_result
#    bla

if 0: # Randomized benchmarking joint
    from .scripts.fluxonium import randbench_jointRO
    rndmben_result = []
    q_epop_cplx = []
    
    n_gates_start = 1
    n_gates_stop = 81
    n_gates_step=3
    
    
    cool = sequencer.Constant(int(8e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), 
                          ])

    alz.set_naverages(5000)
    for i in range(25):
        rndmben = randbench_jointRO.rndm(qubit_info, qubit2_info, num_cal_points=3, n_gates_start=1, n_gates_stop=81, n_gates_step=3, seq=seq, postseq=None, generate=True, proj_func='phase') #seq=seq added
        rndmben.measure()
        rndmben_result.append(rndmben.get_ys())
        q_epop_cplx.append(rndmben.q1_epop_cplx)
    bla
#fitting the averaged data of this run


    average_data= np.real(np.mean(q_epop_cplx, axis=0))
    std = np.std(np.real(q_epop_cplx), axis = 0)


    xs = np.linspace(1,81,26)  #change this 
    ys  = average_data
    err = std



    def exp_decay(params, x, data):
        est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
        return (data-est)

    def exp_decay2(params, x):
        est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
        return est

    params=lmfit.Parameters()
    params.add('amplitude', value=0.5)
    params.add('ofs', value=0.5)
    params.add('tau', value=100)
    plt.figure()
    ax1 = plt.gca()
    result= lmfit.minimize(exp_decay, params, args=(xs,ys))
    lmfit.report_fit(result.params)
    plt.plot(xs, exp_decay2(result.params,xs), markersize=4)
    plt.errorbar(xs,ys,std, markersize=3, linestyle='None', capsize=2, color='red')
    plt.plot(xs,ys, 'ro', markersize=5, color='magenta', linestyle='None')
    plt.plot(xs,np.transpose(np.real(np.mean(q_epop_cplx, axis=0))), '.', markersize=3, linestyle='None')
    plt.title('trial')
    ax1.set_ylabel('Average fidelity')
    ax1.set_xlabel('Number of gates')





if 0: # Randomized benchmarking joint interleaved two qubits
    from .scripts.fluxonium import randbench_jointRO_interleaved
    rndmben_result = []

    
    
    cool = sequencer.Constant(int(8e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), 
#                          qubit2_info.rotate(np.pi2,0)
                          ])

    alz.set_naverages(10000)
    for i in range(1):
        rndmben = randbench_jointRO_interleaved.rndm(qubit2_info, qubit_info, num_cal_points=3, n_gates_start=1, n_gates_stop=81, n_gates_step=3, seq=seq, postseq=None, generate=True, proj_func='phase') #seq=seq added
        rndmben.measure()
        rndmben_result.append(rndmben.get_ys())


if 0: # Check histogramming
    from .scripts.single_qubit import rabi, efrabi
    alz.set_naverages(15000)
    cool = sequencer.Constant(int(6e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(200)])

    tr = rabi.Rabi(qubit_info, [qubit_info.pi_amp,], histogram=True, seq=seq, title='|e>')
    tr.measure()
    tr = rabi.Rabi(qubit_info, [0.0000001,], histogram=True, seq=seq, title='|g>')
    tr.measure()
#    tr = rabi.Rabi(qubit_info, [qubit_info.pi_amp/2,], histogram=True, title='|g>+|e>')
#    tr.measure()
#    tr = efrabi.EFRabi(qubit_info, ef_info, [ef_info.pi_amp,], histogram=True, title='|f>')
#    tr.measure()
    bla


if 0: #Temporary: histogram - the set of 3 points looped together - super inefficient way to do it (Ebru)
    from .scripts.single_qubit import rabi
    alz.set_naverages(1)
    M = 1
    y=np.zeros(shape=(M,3),dtype=complex)
    for i in range(M):
        tr = rabi.Rabi(qubit_info, [qubit_info.pi_amp,], histogram=True, title='|e>')
        tr.measure()
        y[:,0][i]=tr.shot_data[:][0]
        tr = rabi.Rabi(qubit_info, [0.0000001,], histogram=True, title='|g>')
        tr.measure()
        y[:,1][i]=tr.shot_data[:][0]
        tr = rabi.Rabi(qubit_info, [qubit_info.pi_amp/2,], histogram=True, title='|g>+|e>')
        tr.measure()
        y[:,2][i]=tr.shot_data[:][0]
    print(('g:', y[:,0].mean()))
    print(('e:', y[:,1].mean()))    
    print(('eq:', y[:,2].mean()))
    alz.set_naverages(2000)
    
    
    
if 1: # T1
    from .scripts.single_qubit import T1measurement
    alz.set_naverages(1500)
   # alz.set_naverages(15000)
#    t1times = np.zeros(len(range(1000)))
    
    fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True)
    t0 = time.time()
#    for i in range(100000000):
    for i in range(1):
#        #postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
        cool = sequencer.Constant(int(5e3),1,chan='3m1')
        seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])#
        postSeq = qubit2_info.rotate(np.pi/2, 0)
#        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info1.rotate(np.pi,0)])
      #  seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
      #  postseq = sequencer.Join([gate_info1.rotate(np.pi,0)])
        
      #  seq = sequencer.Join([gate_info1.rotate(np.pi,0)])
#        postseq = sequencer.Join([gate_info1.rotate(np.pi,0), gate_info2.rotate(np.pi,0)])
#        t1 = T1measurement.T1Measurement(qubit_info3, np.concatenate((np.linspace(0,5e3,51), np.linspace(5.1e3, 40e3, 51))), double_exp=True, generate=True, plot_seqs=False,
#        times = np.linspace(0,175e3,41)
     # times = np.concatenate((np.linspace(0,15e3,31), np.linspace(15.1e3, 170e3, 31)))
        times =  np.linspace(0e3,80e3,51)
#        times =  np.linspace(0e3,0.1e3,11)
        
#        times =  np.linspace(0e3,35e3,71)
#        times =  np.linspace(0e3,75e3,21)
#        times =  np.linspace(0e3,700e3,31)
#        times = np.linspace(0,1e3,11)
        seq_train = sequencer.Join([qubit_info.rotate(-np.pi, 0), sequencer.Delay(100)]*500)
        
        seq_coolRO = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(int(10e3),1,chan='4m1'), sequencer.Delay(150)])

     #   times = np.logspace(np.log10(0.1e3), np.log10(60e3), 61)
#        while True:
        t1 = T1measurement.T1Measurement(qubit2_info2,times, double_exp=False, generate=True, plot_seqs=False,
                                         proj_func='phase', seq=seq_cool, postseq=None,  extra_info=[qubit_info,qubit2_info])
        t1.measure()
#        plt.close(t1.fig)
            
        tk = time.time()
        tau = t1.fit_params['tau']
        err = tau.stderr    
        ct = tau.value
        axes[0].errorbar(tk-t0, tau, yerr=err, marker='o', fillstyle='none', color='k',\
            capsize=3)
        axes[1].plot(tk-t0, tau/err, marker='o', fillstyle='none', color='k')
        
        fig.canvas.draw()
    axes[1].set_xlabel('time (s)')
    axes[1].set_ylabel('SNR')
    axes[0].set_ylabel('T1 (s)')
#        t1.fig.savefig('C:\\tmp\\{:03d}.png'.format(i))
#        plt.close(t1.fig)
#        t1times[i] = t1.analyze()
#        plt.close()
    bla
    
    
if 0: # T1 vs RO freq
    from .scripts.single_qubit import T1measurement

    fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True)
    
    Nrepet = 1
    rofreq = 7.57e9
    freq_range = 5e6
    freq_list = np.linspace(-freq_range, freq_range, 11)+rofreq
    
    freq_list = [7.5737e9, 7.56845e9]
    freq_list = np.linspace(np.min(freq_list), np.max(freq_list), 10)
    freq_list = freq_list + freq_list[-1]-freq_list[0]+np.mean(np.diff(freq_list))
    
    freq_list = np.linspace(7.56845e9, freq_list[-2], 300)
    
    
    times = np.linspace(0, 40e3,61)
    alz.set_naverages(16000)
    
    for freq in freq_list:
        for _ in range(Nrepet):
            RObrick.do_set_frequency(freq)
            refbrick.do_set_frequency(freq+50e6)
            
            time.sleep(3)
            
            t1 = T1measurement.T1Measurement(qubit_info, times, double_exp=False, generate=True, plot_seqs=False,
                                             proj_func='phase', seq=None, postseq=None)
            t1.measure()
            
            tk = time.time()
            tau = t1.fit_params['tau']
            err = tau.stderr
            ct = tau.value
            axes[0].errorbar(freq, tau, yerr=err, marker='o', fillstyle='none', color='k',\
                capsize=3)
            axes[1].plot(freq, tau/err, marker='o', fillstyle='none', color='k')
            
            fig.canvas.draw()
    axes[1].set_xlabel('Frequency (Hz)')
    axes[1].set_ylabel('SNR')
    axes[0].set_ylabel('T1 (s)')
    axes[0].set_xlim([np.min(freq_list), np.max(freq_list)])
    axes[0].set_ylim([0, 100000])
    axes[1].set_ylim([0, 15])

if 0: # T2
    from .scripts.single_qubit import T2measurement
    cool = sequencer.Constant(int(5e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info1.rotate(np.pi,0)])
#    seq = sequencer.Join([sequencer.Trigger(250), qubit_info2.rotate(np.pi,0)])
#    postseq = gate_info1.rotate(np.pi,0)
#    postseq = sequencer.Join([gate_info1.rotate(np.pi,0), gate_info2.rotate(np.pi,0)])
   # postseq = sequencer.Join([sequencer.Delay(20000), qubit_info.rotate(np.pi/2, 0)])
    alz.set_naverages(3000)

    if 1:
#        coolgen.set_rf_on(True)
#    
        for i in range(1):
            t2 = T2measurement.T2Measurement(qubit_info2, np.linspace(0, 6e3,51), detune=0.5e6, double_freq=False,
                                             generate=True,seq=seq_cool, postseq=None, extra_info =[qubit_info2],
                                                 proj_func='phase')
            t2.measure()
            
        bla

if 0: # T2echo
    from .scripts.single_qubit import T2measurement
    cool = sequencer.Constant(int(5e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
   # postseq = sequencer.Join([Delay(10e3), qubit_info.rotate(np.pi/2, 0))
  #  postseq = gate_info1.rotate(np.pi,0)
    alz.set_naverages(5000)
    t2 = T2measurement.T2Measurement(qubit_info2, np.linspace(0,15e3,61), detune=0.33e6, 
                                     double_freq=False, echotype = T2measurement.ECHO_HAHN, 
                                     necho=3, plot_seqs = False, generate=True,
                                     seq=seq, postseq=None, extra_info =[gate_info1, gate_info2], 
                                     proj_func='phase',
                                     selective=False)
    t2.measure()
    bla

if 0: #
    fig, ax = plt.subplots(nrows=1, ncols=1)
    from .scripts.single_qubit import T2measurement
    cool = sequencer.Constant(int(10e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    postseq = gate_info1.rotate(np.pi,0)
    alz.set_naverages(12000)
    for Necho in range(41):
        
        try:
            t2 = T2measurement.T2Measurement(qubit_info, np.array([0]*10), detune=0e6, double_freq=False, echotype = T2measurement.ECHO_HAHN, necho=Necho, plot_seqs = False, generate=True,
                                         seq=None, postseq=None, extra_info =[gate_info1, gate_info2], proj_func='phase')
            t2.measure()

        except ValueError:
            print('This is ghetto')
        except ZeroDivisionError:
            print('This is ghetto')
            
        ys = t2.get_ys(None)
        ax.plot(np.ones_like(np.mean(ys))*Necho,np.mean(ys), marker='o', fillstyle='none', color='k')
        fig.canvas.draw()
    bla


if 0: # Phase vs cooling power
  #  fig, ax = plt.subplots(nrows=1, ncols=1)
    from .scripts.single_qubit import T2measurement
    cool = sequencer.Constant(int(10e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    postseq = gate_info1.rotate(np.pi,0)
    alz.set_naverages(40000)
    for coolPower in np.linspace(18, 19, 5)[:]:
        coolgen.set_power(coolPower)
        time.sleep(10)
        try:
            t2 = T2measurement.T2Measurement(qubit_info, np.array([1e3]*10), detune=0.1e6, double_freq=False, echotype = T2measurement.ECHO_HAHN, necho=Necho, plot_seqs = False, generate=True,
                                         seq=seq, postseq=None, extra_info =[gate_info1, gate_info2], proj_func='phase')
            t2.measure()

        except ValueError:
            print('failed')
            
        ys = t2.get_ys(None)
        ax.plot(np.ones_like(np.mean(ys))*coolPower,np.mean(ys), marker='+', fillstyle='none', color='k')
        fig.canvas.draw()
    bla


if 0: # Phase vs cooling length
   # fig, ax = plt.subplots(nrows=1, ncols=1)
    from .scripts.single_qubit import T2measurement
    postseq = gate_info1.rotate(np.pi,0)
    alz.set_naverages(20000)

    for length in np.linspace(1, 30e3, 10):
    
        cool = sequencer.Constant(int(length),1,chan='3m1')
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
        time.sleep(3)
        try:
            t2 = T2measurement.T2Measurement(qubit_info, np.array([1e3]*10), detune=0.1e6, double_freq=False, echotype = T2measurement.ECHO_HAHN, necho=Necho, plot_seqs = False, generate=True,
                                         seq=seq, postseq=None, extra_info =[gate_info1, gate_info2], proj_func='phase')
            t2.measure()

        except ValueError:
            print('failed')
            
        ys = t2.get_ys(None)
        ax.plot(np.ones_like(np.mean(ys))*length,np.mean(ys), marker='v', fillstyle='none', color='k')
        fig.canvas.draw()
    bla

if 0: # FT1
    from .scripts.single_qubit import FT1measurement
    #ft1times = np.zeros(len(range(20)))

    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    postseq = sequencer.Join([gate_info1.rotate(np.pi,0)])

    for i in range(1):
        ft1 = FT1measurement.FT1Measurement(gate_info1, gate_info2, qubit_info3, 
                                            np.concatenate((np.linspace(0, 30e3, 51), np.linspace(11e3, 20e3, 11))), seq=seq, postseq=postseq,
                                                           proj_func='phase')
        ft1.measure()
        #ft1times[i] = ft1.analyze()
        #plt.close()
    bla

if 0: # EFT2
    from .scripts.single_qubit import EFT2measurement # frequency stability of |f> vs |e>
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    postseq = sequencer.Join([gate_info1.rotate(np.pi,0)])
    eft2 = EFT2measurement.EFT2Measurement(gate_info1, gate_info2, qubit_info3, np.linspace(0, 20e3, 51), detune=0e6, double_freq=False, postseq=postseq, seq=seq, plot_seqs = False, echotype = EFT2measurement.ECHO_NONE,
                                               proj_func='phase')
    eft2.measure()

    bla


if 0: # f0 - g1 fwm test / e0g2 test
    fwm_gen = mclient.instruments['cool_gaius']
    ROfreq = 7548560000.0
    ge = 172.65e6
#    ef = 3297.0e6 - 100e6
    target_freq = (ROfreq - ge)/2
#    target_freq= 3.48893e9
    freq_range1 = 10e6
    freq_range2 = 10e6
    freqs = np.linspace(target_freq - freq_range1, target_freq + freq_range2, 11)
    powers = [-10]
    
    alz.set_naverages(8000)
    from .scripts.FWM import FWM_f0g1_alazar
    for power in powers:
#        for m in [15,10,0,-10,-15]:
#            cool_gaius.set_power(m)
        for cooltime in [50e3]:#5e3,30e3,25e3]:
            f0g1 = FWM_f0g1_alazar.FWM_f0g1_alazar(qubit2_info, ef_info, fwm_gen, cooltime, 
                     freqs, power, '3m1', qubit_rfsource = fwm_gen)
            f0g1.measure()
#    cool_gaius.set_rf_on(0)
    bla        



if 0: #ground and first excited state voltages #need to figure out proper tick labeling 
    from .scripts.fluxonium import G_e_voltage

    cool_on_g=[]
    cool_on_e=[]
    cool_off_g=[]
    cool_off_e=[]
    alz.set_naverages(1500)
    cool = sequencer.Constant(int(8e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])

    for power in np.linspace(10,10,1):
        coolgen.set_power(power)
        for freq in np.linspace(3.42e9,3.440e9,21):        
            coolgen.set_frequency(freq)
            coolgen.set_rf_on(False)
            time.sleep(0.5)
            gev = G_e_voltage.G_e_voltage(qubit_info, seq=seq_cool, generate=True)  #seq=seq was added
            gev.measure()
            gev_result = gev.get_ys()
            cool_off_g.append(np.mean(gev_result[:10]))
            cool_off_e.append(np.mean(gev_result[10:]))
            plt.close()
            
            coolgen.set_rf_on(True)
            time.sleep(0.5)
            gev = G_e_voltage.G_e_voltage(qubit_info, seq=seq_cool, generate=True)  #seq=seq was added
            gev.measure()
            gev_result = gev.get_ys()
            cool_on_g.append(np.mean(gev_result[:10]))
            cool_on_e.append(np.mean(gev_result[10:]))   
            plt.close()

        plt.figure()
        plt.plot(cool_on_g, label="on_g", color='b')
        plt.plot(cool_on_e, label="on_e", color='b')
        plt.plot(cool_off_g, label="off_g", color ='r')
        plt.plot(cool_off_e, label="off_e", color='r')
        plt.legend(loc="upper left")
        plt.title(power)
    
    bla
#if 0: # Randomized benchmarking for single qubit gates
#
#    from scripts.fluxonium import randbench_singlequbitgate
#    rndmbensingle_result = []
#    alz.set_naverages(150000)
#    cool = sequencer.Constant(int(20e3),1,chan='3m1')
#
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), 
#                          qubit2_info.rotate(np.pi,0)
#                          ])
#
#    for i in range(8):
#        rndmbensingle = randbench_singlequbitgate.randbench_singlequbitgate(qubit2_info, qubit2_info2, num_cal_points=6, n_gates_start=1, n_gates_stop= 11, n_gates_step=1, seq=None, plot_seqs=False, generate=True, proj_func='phase', extra_info=qubit2_info) #seq=seq added
#        rndmbensingle.measure()
#        rndmbensingle_result.append(rndmbensingle.get_ys())
#        plt.close()
#        plt.figure()
#        plt.plot(rndmben.xs, rndmben.get_ys())#, linestyle=None)
#    print rndmben_result
    bla

if 0: # single qubit rotation try
    from .scripts.fluxonium import single_rotation
    cool = sequencer.Constant(int(20e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(200)])
    
    alz.set_naverages(100000)
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(-np.pi/2, 0)]) #this whole line was added
    result =[]
    sr = single_rotation.Single_Rotation(qubit_info, qubit2_info, seq=seq_cool, plot_seqs=True, generate=True, proj_func='phase')  #seq=seq was added
    sr.measure()
    #        allxy_result[i,:] = axy.get_ys()
    result = sr.get_ys()
    plt.plot(result)
#    plt.figure()
##    for i in range(N):
#        plt.plot(allxy_result[i,:])
    bla

if 0: # single qubit rotation try for both qubits 
    from .scripts.fluxonium import single_rotation_forboth
    
#    allxy_result = np.zeros((N, 42))
    alz.set_naverages(750000)
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(-np.pi/2, 0)]) #this whole line was added
    result =[]
    sr = single_rotation_forboth.Single_Rotation_forboth(qubit_info, qubit_info2, qubit2_info, qubit2_info2, seq=None, plot_seqs=True, generate=True, proj_func='phase')  #seq=seq was added
    sr.measure()
    #        allxy_result[i,:] = axy.get_ys()
    result1 = sr.get_ys()
    plt.plot(result)
#    plt.figure()
##    for i in range(N):
#        plt.plot(allxy_result[i,:])
    bla    


if 0: # single qubit rotation try for both qubits flipping population higher contrast the blue transition
    from .scripts.fluxonium import single_rotation_forboth
    
#    allxy_result = np.zeros((N, 42))
    alz.set_naverages(1000000)
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)]) #this whole line was added
    result =[]
    sr = single_rotation_forboth.Single_Rotation_forboth(qubit_info, qubit_info2, qubit2_info, qubit2_info2, seq=seq, plot_seqs=True, generate=True, proj_func='phase')  #seq=seq was added
    sr.measure()
    #        allxy_result[i,:] = axy.get_ys()
    result2 = sr.get_ys()
    plt.plot(result)
#    plt.figure()
##    for i in range(N):
#        plt.plot(allxy_result[i,:])
    bla 



    
if 0: # Calibrate pi pulse for the single qubit operation for the two qubit device
    from .scripts.fluxonium import rabi_singlequbit



    for angle in np.linspace(0.72, 0.77, 5)*np.pi:
#    for ratio in np.linspace(0.20, 0.21, 5):
        cool = sequencer.Constant(int(20e3),1,chan='3m1')
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(200)])

        tr = rabi_singlequbit.Rabi_singlequbit(qubit_info, qubit_info2, np.linspace(-0.5, 0.5, 51), selective=False,
            #                   np.linspace(0.75, 0.95, 101), selective=False,
            #                           np.linspace(-0.2, 0.2, 61), selective=True,
                               plot_seqs=False, generate=True, repeat_pulse=1,
                               update=False, seq=None, rel_amp=0.205, rel_angle=angle,
                               postseq=None, proj_func='phase')
        data=tr.measure()    

if 0: # for modified version
    from .scripts.fluxonium  import CZ_1Dseq_modified
    alz.set_naverages(2000)
#    postseq =  sequencer.Combined([gate_info1.rotate(np.pi,0), gate_info2.rotate(np.pi,0)])
    cz = CZ_1Dseq_modified.TimeRabi_interleaved(
                                qubit_info, qubit_info2, ZZ_info,  np.linspace(0, 3000, 71), #Does not include Gaussian ramp time, sigma=4
                                amp=-0.118, phase=0, sigma=6, read_on_e=False,update=False, seq=None, 
                                postseq=None, proj_func='phase', plot_seqs=False, extra_info=None)
    data = cz.measure()
    
if 0: # Interleaved combined Rabi
    from .scripts.fluxonium import rabi_singlequbit_interleaved

#    for cool_time in [100e3]:
#        cool = sequencer.Constant(int(cool_time),1,chan='3m1')
#        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(200)])
                #            for coolamp in [0.05, 0.1, 0.3, 0.8]:
        
        #    postseq = sequencer.Join((ef_info.rotate(np.pi, 0), sequencer.Delay(20000)))
        #        for power in [-5]:
        #            cool_gaius.set_power(po wer)
        #        for cool_time in [0,2e3,10e3,20e3]:
    cool = sequencer.Constant(int(20e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(200)])
#    postseq = qubit_info2.rotate(np.pi/2, np.pi/2)
    
    for i in range(2):
        tr = rabi_singlequbit_interleaved.Rabi_singlequbit_interleaved(qubit_info, qubit_info2, qubit2_info2, np.linspace(-0.5, 0.5, 61), selective=False,
            #                   np.linspace(0.75, 0.95, 101), selective=False,
            #                           np.linspace(-0.2, 0.2, 61), selective=True,
                               plot_seqs=False, generate=True, repeat_pulse=1,
                               update=False, seq=seq_cool, rel_amp=0.300, rel_angle=-np.pi*0.189,
                               postseq=None, proj_func='phase')
        data=tr.measure()
#        tr = rabi_singlequbit.Rabi_singlequbit(qubit_info, qubit_info2, np.linspace(-0.9, 0.9, 71), selective=False,
#            #                   np.linspace(0.75, 0.95, 101), selective=False,
#            #                           np.linspace(-0.2, 0.2, 61), selective=True,
#                               plot_seqs=False, generate=True, repeat_pulse=1,
#                               update=False, seq=None, rel_amp=0.21, rel_angle=np.pi*-0.69,
#                               postseq=None, proj_func='phase')
#        data=tr.measure()  
#
    

if 0: 
    from .scripts.fluxonium  import timerabi_interleaved
    alz.set_naverages(3000)
    
    cool = sequencer.Constant(int(8e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)]) 
    X_proj = qubit_info.rotate(np.pi/2, 0)#np.pi*0.30)
    Y_proj = qubit_info.rotate(np.pi/2, np.pi/2)

    rel_amp=1
    rel_phase = 0.25
#    for rel_amp in np.linspace(0.295, 0.298, 2):
    for rel_amp in np.linspace(1.1, 0.32, 1):
        for i in range(1):
            for postseq in [None]:
                tr = timerabi_interleaved.TimeRabi_interleaved(
                    qubit_info, qubit_info2, qubit2_info, np.linspace(0, 100, 51), #Does not include Gaussian ramp time, sigma=4
                    amp=0.05, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, 
                    update=False, seq=seq_cool, postseq=None, proj_func='phase')
                data = tr.measure()
    bla


#if 0: # Compensated Time Rabi
#    from scripts.single_qubit import timerabi_singlequbit
#    cool = sequencer.Constant(int(8e3),1,chan='3m1')
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])    
#    rel_amp=0.301
#    rel_phase = 0.188*np.pi
#
#    tr = timerabi_singlequbit.TimeRabi_singlequbit(qubit_info, qubit_info2, qubit2_info2, np.linspace(0, 500, 51), amp=0.5, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, 
#                    update=False, seq=seq_cool, postseq=postseq, proj_func='phase')
#    data = tr.measure()
#    bla
#


'''2D CR Tune-ups'''

if 0: # Tune up for time vs detuning   
    
    from .scripts.fluxonium import CRtuning_timevsdet
    
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])     
    cr_tune = CRtuning_timevsdet.CRtuning_timevsdet(gate_info2, qubit2_info2, gate_info1, 
                                                    np.linspace(0,121,31), np.linspace(-20e6, 20e6, 11), 
                amp=0.12, phase=0, rel_amp=0.00, rel_phase=1.77, sigma=1, update=False, 
                seq=seq_cool, fix_phase=True, fix_period=None, control_pi=True, proj_func='phase')    
    
    data = cr_tune.measure()
    bla
    

if 0: # Tune up for time vs relative amp
    
    from .scripts.fluxonium import CRtuning_timevsamp
    
    cr_tune = CRtuning_timevsamp.CRtuning_timevsamp(qubit_info, qubit_info2, qubit2_info, np.linspace(1,100,17), rel_amps=np.linspace(-1,1,17),
                amp=0.3, phase=0, rel_phase=0, sigma=5, update=False, seq=seq, r_axis=0, fix_phase=True, fix_period=None, repeat_pulse=1, postseq=None, selective=False, control_pi=False)    
    
    data = cr_tune.measure()
    bla
        


if 0: # Tune up for relative amp vs relative phase
    
    from .scripts.fluxonium import CRtuning_ampvsphase
    
    cr_tune = CRtuning_ampvsphase.CRtuning_ampvsphase(qubit_info, qubit_info2, qubit2_info, np.linspace(0.3,0.5,17), np.linspace(-0.1,0.1,17), times=1000, 
                amp=0.35, phase=0, sigma=5, update=False, seq=None, r_axis=0, fix_phase=True, fix_period=None, repeat_pulse=1, postseq=None, selective=False, control_pi=True)    
    
    data = cr_tune.measure()
    bla
    

  
if 0: # cooling tone spec
    from .scripts.fluxonium import cooling_tune_brickonoff
#    from scripts.single_qubit import spectroscopy_IQ
    cool_freq = 3.520e9
    freq_range = 50e6

    cool = cooling_tune_brickonoff.Cooling_tune_brickonoff(mclient.instruments['cool'], mclient.instruments['gaius01'], 
                                                           qubit2_info, np.linspace(cool_freq-freq_range, cool_freq+freq_range, 31),
                                     [-1,2,5], '3m1', seq=None, plot_seqs=False) #1=1ns for plen
    cool.measure()
    bla

 
    
if 0: #Single qubit cancellation tune up 
    #This should be done after ZZ is tuned. While making single qubit gates, we want to make sure we apply 
    #a pair of tones that drives the first qubit and does not drive the second one.
    cool = sequencer.Constant(int(8e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])    
    
    from .scripts.fluxonium import single_qubit_tune
    
    sq_tune = single_qubit_tune.Single_qubit_tune(qubit_info, qubit2_info, amps=np.linspace(-0.30,0.3,17), amps2=np.linspace(-0.3,0.3,11),qubit1_rotation_angle =np.pi,
                                                  update=False, seq=seq, r_axis=0, fix_phase=True, fix_period=None, repeat_pulse=1, postseq=None, selective=False)
 
  
    data = sq_tune.measure()
    bla
    

if 0: #TWPA sweep
    from .scripts.single_cavity import rocavspectroscopy
    twpa = mclient.instruments['WF_xxx']
    twpa_powers = np.linspace(-4.2, -3.8, 5)
    twpa_freqs = np.linspace(7905.5e6, 7905.6e6, 11)
    ro_amps = []
    ro_noise = []
    for power in twpa_powers:
        twpa.set_power(power)
        for freq in twpa_freqs:
            twpa.set_frequency(freq)
            rofreq = 7587.5e6
            freq_range = 7.5e6
            ro = rocavspectroscopy.ROCavSpectroscopy(qubit_info, np.linspace(0,0, 1),
                                                 np.linspace(rofreq - freq_range, rofreq + freq_range, 11), qubit_pulse=False)
            ro.measure()
            ro_amps.append(np.mean(ro.ampdata[0,:]))
            ro_noise.append(np.mean(ro.ampdata[0,:]))
            plt.close('all')
    bla
    
    
    
    
    
if 0: # Auto LO canceling
    import scipy.optimize as sciopt
    freq = 5e9
    
    cool.set_frequency(freq)
    IQ_mod.do_set_frequency(freq)
    
    spike.do_set_mode('RTSA')
    spike.do_set_center_frequency(freq)
    
    spike.do_set_marker_X(freq)
    spike.do_set_marker_peaktracing(True)
    

    def minimizeLO(p):
        dacI, dacQ = p
        
        if dacI<0 or dacQ<0 or dacI > 16383 or dacQ>16383:
            return np.NaN
        
        dacI = int(0 if dacI<0 else 16383 if dacI > 16383 else dacI)
        dacQ = int(0 if dacQ<0 else 16383 if dacQ > 16383 else dacQ)
        
        IQ_mod.do_set_linearityDAC('I', dacI)
        IQ_mod.do_set_linearityDAC('Q', dacQ)
        
        time.sleep(2)
        freq, amp = spike.do_get_marker_XY()
        
        print((dacI, dacQ, freq, amp))
        return amp
        
        
    popt, pcov = sciopt.minimize(minimizeLO, 
                                 [3935, 3935],
                                 method='Nelder-Mead')
    spike.do_get_marker_XY()
    

    def minimizeLO_IQ(p, args):
        level = p[0]
        tune = args[0]
        
        if level<0 or level<0:
            return np.NaN
        level = int(level)
        
        if tune=='I':
            IQ_mod.do_set_linearityDAC('I', level)
        elif tune=='Q':
            IQ_mod.do_set_linearityDAC('Q', level)
        else:
            raise ValueError            
        time.sleep(2)
        freq, amp = spike.do_get_marker_XY()
        
        print((tune, level, freq, amp))
        return amp
        
    IQ_mod.do_set_linearityDAC('I', 3935)
    IQ_mod.do_set_linearityDAC('Q', 3935)

    popt, pcov = sciopt.minimize(minimizeLO_IQ, 
                                 [3935],
                                 args=['I'],
                                 method='Nelder-Mead')
        
    
    popt, pcov = sciopt.minimize(minimizeLO_IQ, 
                                 [3935],
                                 args=['Q'],
                                 method='Nelder-Mead')
        
    
    
    
if 0: # side band
    import scipy.optimize as sciopt
    from .scripts.single_qubit import rabi

    
   # spike.do_set_mode('RTSA')
   # spike.do_set_center_frequency(freq)
    
    #spike.do_set_marker_X(freq)
   # spike.do_set_marker_peaktracing(True)
    

    def minimizeLO(p):
        qubit1ge.set_sideband_phase(p[0])
        qubit_info = mclient.get_qubit_info('qubit1ge')

        AWG2.set_ch1_amplitude(p[1])
        AWG2.set_ch2_amplitude(p[2])

        alz.set_naverages(100)
        powers = np.hstack((np.ones(40), np.ones(1)*-1))*0.0139760888479
        try:
            tr = rabi.Rabi(qubit_info, powers, selective=False,
                #                   np.linspace(0.75, 0.95, 101), selective=False,
                #                           np.linspace(-0.2, 0.2, 61), selective=True,
                                   plot_seqs=False, generate=True, repeat_pulse=100,  #n=3 has a bug
                                   update=False, seq=None,
                                   postseq=None, proj_func='phase', extra_info=[gate_info1, gate_info2])
            data=tr.measure()
            pyp.close(tr.fig)
        except ValueError:
            print('meh')
        time.sleep(2)
        freq, amp = spike.do_get_marker_XY()
        print(('\n\n\n\n' + str((p[0], amp)) + '\n\n\n\n\n\n'))

        return amp
        
        
    popt, pcov = sciopt.minimize(minimizeLO, 
                                 [0,0,0],
                                # bounds=([-np.pi,0]))
                                 method='Nelder-Mead',
                                 options = dict(initial_simplex=np.array([[-0.3,1.5,1.5],[-0.35,1.48,1.48], [-0.25,1.4,1.5], [-0.3, 1.5, 1.47]])))
    
    

if 0: # side band
    import scipy.optimize as sciopt
    from .scripts.single_qubit import rabi

    
   # spike.do_set_mode('RTSA')
   # spike.do_set_center_frequency(freq)
    
    #spike.do_set_marker_X(freq)
   # spike.do_set_marker_peaktracing(True)
    

    def minimizeLO(p):
        qubit1ge.set_sideband_phase(p[0])
        qubit_info = mclient.get_qubit_info('qubit1ge')

        alz.set_naverages(100)
        powers = np.hstack((np.ones(40), np.ones(1)*-1))*0.0139760888479
        try:
            tr = rabi.Rabi(qubit_info, powers, selective=False,
                #                   np.linspace(0.75, 0.95, 101), selective=False,
                #                           np.linspace(-0.2, 0.2, 61), selective=True,
                                   plot_seqs=False, generate=True, repeat_pulse=100,  #n=3 has a bug
                                   update=False, seq=None,
                                   postseq=None, proj_func='phase', extra_info=[gate_info1, gate_info2])
            data=tr.measure()
            pyp.close(tr.fig)
        except ValueError:
            print('meh')
        time.sleep(2)
        freq, amp = spike.do_get_marker_XY()
        print(('\n\n\n\n' + str((p[0], amp)) + '\n\n\n\n\n\n'))

        return -amp
        
        
    popt, pcov = sciopt.minimize(minimizeLO, 
                                 [0],
                                # bounds=([-np.pi,0]))
                                 method='Nelder-Mead',
                                 options = dict(initial_simplex=np.array([[0],[np.pi/40]])))
    
    
    
if 0: # side band 2
    import scipy.optimize as sciopt
    from .scripts.single_qubit import rabi
    import pandas as pd

    alz.set_naverages(3000)

   # spike.do_set_mode('RTSA')
   # spike.do_set_center_frequency(freq)
    
    #spike.do_set_marker_X(freq)
   # spike.do_set_marker_peaktracing(True)
    fig, axes = plt.subplots(1,1)
    data = pd.DataFrame()
    for phase in np.linspace(-0.4,-0.3, 21):
        qubit1ge.set_sideband_phase(phase)
        qubit_info = mclient.get_qubit_info('qubit1ge')

        alz.set_naverages(100)
        powers = np.hstack((np.ones(40), np.ones(1)*-1))*0.0139760888479
        try:
            tr = rabi.Rabi(qubit_info, powers, selective=False,
                #                   np.linspace(0.75, 0.95, 101), selective=False,
                #                           np.linspace(-0.2, 0.2, 61), selective=True,
                                   plot_seqs=False, generate=True, repeat_pulse=10,  #n=3 has a bug
                                   update=False, seq=None,
                                   postseq=None, proj_func='phase', extra_info=[gate_info1, gate_info2])
            data=tr.measure()
        except ValueError:
            print('meh')
        time.sleep(2)
        plt.close(tr.fig)

        freq, amp = spike.do_get_marker_XY()
        print(('\n\n\n\n' + str((phase, amp)) + '\n\n\n\n\n\n'))
        data = data.append({'amp':amp, 'freq':freq, 'phase':phase}, ignore_index=True)
        
        axes.plot(phase, amp, marker='o', fillstyle='none', color='k')
        
        
        if 0:#data.shape[0]>2:
            def func(x, *p):
                return p[0]*np.cos(x+p[1])
            popt, pcov = sciopt.curve_fit(func, data['phase'], 10**(data['amp']/20), p0=(1,0))
            axes.plot(data['phase'], func(data['phase'], *popt),color='k', ls='--')

        
        fig.canvas.draw()
        
        
        
        
        
        
        
    
if 0:  # Remove LO AWG
   print('lqlq')
   import scipy.optimize as sciopt
   def minimizeLO(p):
       # qubit1ge.set_sideband_phase(p[0])
       # qubit_info = mclient.get_qubit_info('qubit1ge')

        AWG2.set_ch1_offset(p[0])
        AWG2.set_ch2_offset(p[1])
        
        time.sleep(2)
        freq, amp = spike.do_get_marker_XY()
        print(( str((p, amp)) ))

        return amp
        
        
   popt, pcov = sciopt.minimize(minimizeLO, 
                                 [0, 0],
                                 method='Nelder-Mead',
                                 options = dict(initial_simplex=np.array([[-0.01, 0.01],[0.01, 0.01], [0,0]])))
    
    
    
if 0:  # Remove LO SC
   print('lqlq')
   import scipy.optimize as sciopt
   def minimizeLO(p):
       # qubit1ge.set_sideband_phase(p[0])
       # qubit_info = mclient.get_qubit_info('qubit1ge')

        dacI, dacQ = p

      #  if dacI<0 or dacQ<0 or dacI > 16383 or dacQ>16383:
       #     return np.NaN
        
        dacI = int(0 if dacI<0 else 16383 if dacI > 16383 else dacI)
        dacQ = int(0 if dacQ<0 else 16383 if dacQ > 16383 else dacQ)
        
        print((dacI, dacQ))
        IQ_mod.do_set_linearityDAC('I', dacI)
        IQ_mod.do_set_linearityDAC('Q', dacQ)
        
        time.sleep(2)
        freq, amp = spike.do_get_marker_XY()
        print(( str((p, amp)) ))

        return amp
        
        
   popt, pcov = sciopt.minimize(minimizeLO, 
                                 [0, 0],
                                 method='Nelder-Mead',
                                 options = dict(initial_simplex=np.array([[5000, 11000],[5000, 8000], [10000,1000]])))
    
    
   
   
   
if 0:
    from .scripts.single_qubit import ssbspec
    
    
    
    
    freqZZ_list = np.linspace(3940e6,3970e6, 11)
    xs = np.linspace(-4e6,4e6,81)

    fig, ax = plt.subplots(1,1)
    
    data = np.zeros((freqZZ_list.shape[0], xs.shape[0]))
    X, Y = np.meshgrid(xs, freqZZ_list)
    for k, freqZZ in enumerate(freqZZ_list):
        
        ZZ.do_set_frequency(freqZZ)
        
        cool = sequencer.Constant(int(10e3),1,chan='3m1')
        seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
       
        alz.set_naverages(1000)
        
        
        spec = ssbspec.SSBSpec(qubit_info2, xs, proj_func='phase', seq=seq_cool,
                               postseq=None, extra_info=[qubit_info,qubit2_info])
        spec.measure()
        
        ys = spec.get_ys()
        data[:, 2*k] = ys
        
        ax.pcolormesh(X, Y, data)
        fig.canvas.draw()
        
        
        
        spec = ssbspec.SSBSpec(qubit_info2, xs, proj_func='phase', seq=seq_cool,
                               postseq=qubit2_info.rotate(np.pi, 0), extra_info=[qubit_info,qubit2_info])
        spec.measure()
        
        ys = spec.get_ys()
        data[:, 2*k] = ys
        
        ax.pcolormesh(X, Y, data)
        fig.canvas.draw()
        
           # x, dx = spec.fit_params['center1'], spec.fit_params['sigma']
            
          #  ax.errorbar(time.time()-t0,x, yerr=dx, marker='o', fillstyle='none', color='k', capsize=3)
          #  fig.canvas.draw()
        
    #            plt.close()
    #    spec.measure_keysight()
    bla   