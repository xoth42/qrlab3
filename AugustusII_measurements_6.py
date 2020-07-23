# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 10:19:22 2019

@author: Ebru
"""
import mclient
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
import matplotlib.pyplot as plt
import math 
import time
import lmfit


import os
os.chdir(r'c:\qrlab')


alz = mclient.instruments['alazar']
yoko = mclient.instruments['yoko']
gaius01 = mclient.instruments['gaius01']
coolgen= mclient.instruments['cool']
ZZ = mclient.instruments['ZZ']

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
qubit_info2 = mclient.get_qubit_info('qubit1ge_2')
gate_info1 = mclient.get_gate_info('sq_gate1')


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
    from scripts.single_cavity import rocavspectroscopy
#    rofreq = 7515.5e6
    rofreq = 7564.6e6
    freq_range = 10e6
    ro = rocavspectroscopy.ROCavSpectroscopy(qubit_info, np.linspace(5, 7, 2),
                                         np.linspace(rofreq - freq_range, rofreq + freq_range, 51), qubit_pulse=False)
    ro.measure()
    bla
    
    
if 0:# Qubit spec
    from scripts.single_qubit import spectroscopy
#    from scripts.single_qubit import spectroscopy_IQ

    qubit_freq = 1192e6
    freq_range = 0e6
    spec = spectroscopy.Spectroscopy(mclient.instruments['gaius01'], qubit_info,
                                         np.linspace(qubit_freq-freq_range,
                                                     qubit_freq+freq_range, 11),
                                             [-15],
                                        plen=2000, amp=0.2, plot_seqs=False, seq=None) #1=1ns for plen
    spec.measure()
    bla    

    
    
    
if 0: # Qubit spec with phase correction
    from scripts.single_qubit import spectroscopy_phasecorrection
#    from scripts.single_qubit import spectroscopy_IQ
    qubit_freq = 3.4875e9
    freq_range = 10e6
    spec = spectroscopy_phasecorrection.Spectroscopy_phasecorrection(mclient.instruments['gaius01'], qubit_info,
                                     np.linspace(qubit_freq-freq_range,
                                                 qubit_freq+freq_range, 21),
                                     [-8],
                                     plen=1000, amp=0.1, plot_seqs=False) #1=1ns for plen
    spec.measure()
    bla


"""Qubit SSBspec"""
if 0: # Qubit SSBspec
    from scripts.single_qubit import ssbspec
#    for i in [-15,-10,-5,0,5,10]:
#    RObrick.do_set_power(i)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), 
#                          qubit2_info.rotate(np.pi,0)
                          ])
#
    for power in np.linspace(0, 16, 1):
#        coolgen.set_power(power)
        for freq in np.linspace(3.380e9,3.450e9,1):
            alz.set_naverages(8000)
#            coolgen.set_frequency(freq)
#            cool = sequencer.Constant(int(8e3),1,chan='3m1')
#            seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), 
##                                  qubit2_info2.rotate(np.pi, 0)
#                                  ])
            spec = ssbspec.SSBSpec(qubit_info, np.linspace(-4e6, 4e6, 81), proj_func='phase', seq=seq, extra_info=qubit2_info)
            spec.measure()
#            plt.close()
#    spec.measure_keysight()
    bla
    
    
    """Power Rabi -- Pi pulse calibration"""

if 0: # Calibrate pi pulse
    from scripts.single_qubit import rabi
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
#    cool = sequencer.Constant(int(200e3),1,chan='3m1')
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(200)])
    for i in range(1):
        cool = sequencer.Constant(int(4e3),1,chan='3m1')
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])# qubit2_info.rotate(np.pi, 0)])
#        postseq = qubit2_info.rotate(np.pi, 0)
#    for i in range(1): 
#        M =np.empty(3)
#        WF_xxx.set_rf_on(0)
#        for wf_power in np.linspace(-5.35408,-5.45,1):
#            WF_xxx.set_power(wf_power)
#            for wf_freq in np.linspace(7.904615e9,7.90461e9,1):
#                WF_xxx.set_frequency(wf_freq)
        tr = rabi.Rabi(gate_info2, np.linspace(-0.15, 0.15, 61), selective=False,
                #                   np.linspace(0.75, 0.95, 101), selective=False,
                #                           np.linspace(-0.2, 0.2, 61), selective=True,
                                   plot_seqs=False, generate=True, repeat_pulse=1,  #n=3 has a bug
                                   update=True, seq=seq,
                                   postseq=None, proj_func='phase', extra_info=qubit2_info)
        data=tr.measure()
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
    



    
    
if 0: # Qubit EFspec - ef_info is not defined
    from scripts.single_qubit import spectroscopy
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
    from scripts.single_qubit import ssbspec
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    spec = ssbspec.SSBSpec(ef_info, np.linspace(-5e6, 5e6, 81), seq=seq, postseq = None, extra_info=qubit_info, plot_seqs=False, generate=True, proj_func='phase')
    spec.measure()
    bla

if 0: # EF rabi   #manipulated this because i use it for the pre (red) pulse for the blue transition - ebru
    from scripts.single_qubit import efrabi
    for i in range(1):
        alz.set_naverages(15000)
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

    from scripts.single_qubit import Single_qubit_tomo
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
    print tomo_result
    bla

if 0: # Process_tomography
    from scripts.single_qubit import Process_tomo
    ptomo_result = []
    p_seq = sequencer.Sequence(sequencer.Delay(80))
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(-np.pi/2, 0)]) #this whole line was added
    sqtomo = Process_tomo.Process_tomo(qubit_info, process_seq=p_seq, generate=True)  #seq=seq was added
    sqtomo.measure()

    ptomo_result.append(sqtomo.get_ys())
    plt.close()

    print ptomo_result
    bla

if 0:# Drag test
    from scripts.single_qubit import drag_test
    dtest = drag_test.drag_test(qubit_info, np.linspace(-2, 2, 41), plot_seqs=False, generate=True, proj_func='phase', seq=seq_cool)
    data=dtest.measure()
    bla

if 0: # AllXY  # there is a separate allxy with a pre pulse for the blue transition, don't change this one
    from scripts.single_qubit import allxy
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
    alz.set_naverages(8000)
#    bla

if 0: # Randomized benchmarking
    from scripts.fluxonium import randbench
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
    from scripts.fluxonium import randbench_jointRO
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
    from scripts.fluxonium import randbench_jointRO_interleaved
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
    from scripts.single_qubit import rabi, efrabi
    alz.set_naverages(15000)
    tr = rabi.Rabi(qubit_info, [qubit_info.pi_amp,], histogram=True, title='|e>')
    tr.measure()
    tr = rabi.Rabi(qubit_info, [0.0000001,], histogram=True, title='|g>')
    tr.measure()
    tr = rabi.Rabi(qubit_info, [qubit_info.pi_amp/2,], histogram=True, title='|g>+|e>')
    tr.measure()
#    tr = efrabi.EFRabi(qubit_info, ef_info, [ef_info.pi_amp,], histogram=True, title='|f>')
#    tr.measure()
    bla


if 0: #Temporary: histogram - the set of 3 points looped together - super inefficient way to do it (Ebru)
    from scripts.single_qubit import rabi
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
    print('g:', y[:,0].mean())
    print('e:', y[:,1].mean())    
    print('eq:', y[:,2].mean())
    alz.set_naverages(2000)
    
    
    
if 0: # T1
    from scripts.single_qubit import T1measurement
    alz.set_naverages(5000)
#    t1times = np.zeros(len(range(1000)))
    for i in range(1):
#    for i in range(1):
#        #postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
        cool = sequencer.Constant(int(4e3),1,chan='3m1')
        seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])#
#        t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0.1,5e3,31), np.linspace(5.1e3, 40e3, 31))), double_exp=True, generate=True, plot_seqs=False,
        t1 = T1measurement.T1Measurement(qubit2_info, np.linspace(0, 40e3, 81), double_exp=False, generate=True, plot_seqs=False,
                                         proj_func='phase', seq=seq_cool)
        t1.measure()
#        t1times[i] = t1.analyze()
#        plt.close()
    bla

if 0: # T2
    from scripts.single_qubit import T2measurement
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    if 1:
#        coolgen.set_rf_on(True)
#    
    #    for i in range(1):
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 1e3, 81), detune=8e6, double_freq=False, 
                                         generate=True, postseq=None,extra_info =qubit_info,
                                             proj_func='phase', seq=seq_cool)
        t2.measure()
        bla

if 0: # T2echo
    from scripts.single_qubit import T2measurement
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
#    for i in range(1):
#    alz.set_naverages(4000)
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(10, 2e3, 81), detune=4e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                     proj_func='phase', seq=seq_cool)
    t2.measure()
    bla

if 0: # FT1
    from scripts.single_qubit import FT1measurement
    #ft1times = np.zeros(len(range(20)))
    for i in range(1):
        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, 
                                            np.concatenate((np.linspace(0, 10e3, 81), np.linspace(11e3, 15e3, 11))), 
                                                           proj_func='phase')
        ft1.measure()
        #ft1times[i] = ft1.analyze()
        #plt.close()
    bla

if 0: # EFT2
    from scripts.single_qubit import EFT2measurement # frequency stability of |f> vs |e>

    eft2 = EFT2measurement.EFT2Measurement(qubit_info, ef_info, np.linspace(0, 3e3, 51), detune=2e6, double_freq=False, plot_seqs = False, echotype = EFT2measurement.ECHO_NONE,
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
    from scripts.FWM import FWM_f0g1_alazar
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
    from scripts.fluxonium import G_e_voltage

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
    from scripts.fluxonium import single_rotation
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
    from scripts.fluxonium import single_rotation_forboth
    
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
    from scripts.fluxonium import single_rotation_forboth
    
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
    from scripts.fluxonium import rabi_singlequbit



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
    
if 0: # Interleaved combined Rabi
    from scripts.fluxonium import rabi_singlequbit_interleaved

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
    from scripts.fluxonium  import timerabi_interleaved
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
                    update=False, seq=seq_cool, postseq=postseq, proj_func='phase')
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

if 1: # Tune up for time vs detuning   
    
    from scripts.fluxonium import CRtuning_timevsdet
    
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])     
    cr_tune = CRtuning_timevsdet.CRtuning_timevsdet(qubit2_info, qubit2_info2, gate_info1, 
                                                    np.linspace(0,121,31), np.linspace(-20e6, 20e6, 11), 
                amp=0.078, phase=0, rel_amp=0.00, rel_phase=1.77, sigma=1, update=False, 
                seq=seq_cool, fix_phase=True, fix_period=None, control_pi=True, proj_func='phase')    
    
    data = cr_tune.measure()
    bla
    

if 0: # Tune up for time vs relative amp
    
    from scripts.fluxonium import CRtuning_timevsamp
    
    cr_tune = CRtuning_timevsamp.CRtuning_timevsamp(qubit_info, qubit_info2, qubit2_info, np.linspace(1,100,17), rel_amps=np.linspace(-1,1,17),
                amp=0.3, phase=0, rel_phase=0, sigma=5, update=False, seq=seq, r_axis=0, fix_phase=True, fix_period=None, repeat_pulse=1, postseq=None, selective=False, control_pi=False)    
    
    data = cr_tune.measure()
    bla
        


if 0: # Tune up for relative amp vs relative phase
    
    from scripts.fluxonium import CRtuning_ampvsphase
    
    cr_tune = CRtuning_ampvsphase.CRtuning_ampvsphase(qubit_info, qubit_info2, qubit2_info, np.linspace(0.3,0.5,17), np.linspace(-0.1,0.1,17), times=1000, 
                amp=0.35, phase=0, sigma=5, update=False, seq=None, r_axis=0, fix_phase=True, fix_period=None, repeat_pulse=1, postseq=None, selective=False, control_pi=True)    
    
    data = cr_tune.measure()
    bla
    

  
if 0: # cooling tone spec
    from scripts.fluxonium import cooling_tune_brickonoff
#    from scripts.single_qubit import spectroscopy_IQ
    cool_freq = 3.420e9
    freq_range = 10e6

    cool = cooling_tune_brickonoff.Cooling_tune_brickonoff(mclient.instruments['cool'], mclient.instruments['gaius01'], 
                                                           qubit2_info, np.linspace(cool_freq-freq_range, cool_freq+freq_range, 31),
                                     [9,11,13], '3m1', seq=None, plot_seqs=False) #1=1ns for plen
    cool.measure()
    bla

 
    
if 0: #Single qubit cancellation tune up 
    #This should be done after ZZ is tuned. While making single qubit gates, we want to make sure we apply 
    #a pair of tones that drives the first qubit and does not drive the second one.
    cool = sequencer.Constant(int(8e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])    
    
    from scripts.fluxonium import single_qubit_tune
    
    sq_tune = single_qubit_tune.Single_qubit_tune(qubit_info, qubit2_info, amps=np.linspace(-0.30,0.3,17), amps2=np.linspace(-0.3,0.3,11),qubit1_rotation_angle =np.pi,
                                                  update=False, seq=seq, r_axis=0, fix_phase=True, fix_period=None, repeat_pulse=1, postseq=None, selective=False)
 
  
    data = sq_tune.measure()
    bla
    

    