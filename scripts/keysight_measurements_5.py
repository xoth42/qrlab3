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
import time
import datetime

qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
qubit2_info = mclient.get_qubit_info('qubit2ge')
#ef2_info = mclient.get_qubit_info('qubit2ef')
#ef2_V2_info = mclient.get_qubit_info('qubit2ef_V2')
#fwm_info = mclient.get_qubit_info('fwm_info1')
#fwm2_info = mclient.get_qubit_info('fwm_info2')
mixer_info1 = mclient.get_qubit_info('mixer_info1')
mixer_info2 = mclient.get_qubit_info('mixer_info2')
mixer_info1_set = mclient.instruments['mixer_info1']
mixer_info2_set = mclient.instruments['mixer_info2']
SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
SS_mixer_info2 = mclient.get_qubit_info('SS_mixer_info2')
SS_mixer_info1_set = mclient.instruments['SS_mixer_info1']
SS_mixer_info2_set = mclient.instruments['SS_mixer_info2']
#qubit03_info = mclient.get_qubit_info('qubit1_03')
#qubit14_info = mclient.get_qubit_info('qubit1_14')
readout_info = mclient.get_readout_info('readout')
readout = mclient.instruments['readout']
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')
os.chdir(r'C:/qrlab/scripts')


#cool_time=10e3
#cool = sequencer.Combined([sequencer.Constant(int(cool_time), 0.04, chan=ef_info.sideband_channels[0]),
#                           sequencer.Constant(int(cool_time), 0.04, chan=ef_info.sideband_channels[1]),
#                           sequencer.Constant(int(cool_time), 1, chan='3m1')])

if 0: # test digitizer
    dig = mclient.instruments['dig']
    data = dig.test_dig(5000, 1, 1, 1)
    print(np.shape(data))
    plt.figure()
    plt.plot(data[0][0][:], label = 'sig')
    plt.plot(data[1][0][:], label = 'ref')
    plt.legend()
    plt.show()
    bla
    
if 0: # test digitizer DEMODULATED
    dig = mclient.instruments['dig']
    avgs = dig.test_dig_demod(2500, 40000)
    print(np.shape(avgs))
    plt.figure()
    plt.plot(np.real(avgs), label = 'real')
    plt.plot(np.imag(avgs), label = 'imag')
    plt.plot(np.abs(avgs), label = 'abs')
    plt.legend() 
    plt.show()
    plt.figure()
    plt.plot(np.real(avgs),np.imag(avgs)) 
    plt.show()
    bla
    
if 0: #set readout and cavity displacement freq
    
    ro_freq = 10.8208e9
    cav_disp = 10.8225e9
    power = 10
    readout_info.rfsource1.set_frequency(ro_freq - mixer_info1.deltaf)
    readout_info.rfsource1.set_power(power)
    readout_info.rfsource2.set_frequency(ro_freq+50e6)
    deltaf = cav_disp - ro_freq + mixer_info1.deltaf
    SS_mixer_info1_set.set_deltaf(deltaf)
    SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
    
    from single_qubit import rabi_mixer
    
    tr = rabi_mixer.Rabi_mixer(qubit_info, mixer_info1, mixer_info2,
#                               np.linspace(-0.8, 0.8, 81), selective=False,
                               np.linspace(-0.6, 0.6, 81), selective=False,
#                               np.linspace(-0.08, 0.08, 81), selective=True,
#                               np.linspace(-0.4, 0.4, 81), selective=True,
        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                               plot_seqs=False, generate=True, repeat_pulse=1,# seq=seq,postseq = postseq, fix_period = 0.38087745,
                               update=False, #extra_info=[qubit_info],
                               proj_func='phase')
    tr.measure_keysight()
    plt.suptitle('ro_freq = %s'%(ro_freq))
    bla    

if 0: # cav transmission

    from single_cavity import rocavspectroscopy_keysight
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
#    Yoko.do_set_current(-0.00175)
    rofreq = 10.715e9
    freq_range = 10e6
    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(-3,0, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                             qubit_pulse=False, seq=None)#,extra_info=[ef2_info])
    ro.measure()
    
#    figure_name = '-0.03T '
#    
#    plt.figure('amp%s'%(figure_name))
#    plt.plot(ro.freqs,ro.ampdata[0],label = 'g, SS off')
#    plt.figure('phase%s'%(figure_name))
#    plt.plot(ro.freqs,ro.phasedata[0],label = 'g')
#    
#    
#    
#    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(5,10,1),
#                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
#                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
#    ro.measure()
#    plt.figure('amp%s'%(figure_name))
#    plt.plot(ro.freqs,ro.ampdata[0],label = 'qubit 1 in e')
#    plt.figure('phase%s'%(figure_name))
#    plt.plot(ro.freqs,ro.phasedata[0],label = 'qubit 1 in e')
#    
#    
#    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit2_info, np.linspace(5,10, 1),
#                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
#                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
#    ro.measure()
#
#    plt.figure('amp%s'%(figure_name))
#    plt.plot(ro.freqs,ro.ampdata[0],label = 'qubit 2 in e')
#    plt.legend()
#    fn = os.path.join(r'C:\_Data', 'images/%s_amp%s.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),figure_name))
#    fdir = os.path.split(fn)[0]
#    if not os.path.isdir(fdir):
#        os.makedirs(fdir)
#    kwargs = dict()
#    plt.savefig(fn, **kwargs)
#    plt.figure('phase%s'%(figure_name))
#    plt.plot(ro.freqs,ro.phasedata[0],label = 'qubit 2 in e')
#    plt.legend()
#    fn = os.path.join(r'C:\_Data', 'images/%s_phase%s.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),figure_name))
#    fdir = os.path.split(fn)[0]
#    if not os.path.isdir(fdir):
#        os.makedirs(fdir)
#    kwargs = dict()
#    plt.savefig(fn, **kwargs)
##by Yingying
##    ro_freq = ro.fit_params[2]
##    print ro_freq
    ro_freq = 10.815e9
    power = -6
    readout_info.rfsource1.set_frequency(ro_freq)
    readout_info.rfsource1.set_power(power)
    readout_info.rfsource1.set_rf_on(True)
    readout_info.rfsource2.set_power(10)
    readout_info.rfsource2.set_rf_on(True)
    readout_info.rfsource2.set_frequency(ro_freq+50e6)
    bla

if 0: # cav transmission with mixer
#    time.sleep(300)
    from single_cavity import rocavspectroscopy_keysight_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
#    Yoko.do_set_current(-0.00175)
    mixer1_amp = 0.03
    mixer2_amp = .03
    mixer_info1_set.set_pi_amp(mixer1_amp)
    mixer_info2_set.set_pi_amp(mixer2_amp)
    mixer_info1 = mclient.get_qubit_info('mixer_info1')
    mixer_info2 = mclient.get_qubit_info('mixer_info2')
    rofreq = 10.820e9
    freq_range = 10e6
    ro = rocavspectroscopy_keysight_mixer.ROCavSpectroscopy_keysight_mixer(qubit_info, mixer_info1,mixer_info2, np.linspace(10,10,1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                             qubit_pulse=False, seq=None)#,extra_info=[ef2_info])
    ro.measure()
    plt.close()
    plt.close()
    
    figure_name = '0.04 T test1'
    
    plt.figure('amp%s'%(figure_name))
    plt.plot(ro.freqs,ro.ampdata[0],label = 'g')
    plt.figure('phase%s'%(figure_name))
    plt.plot(ro.freqs,ro.phasedata[0],label = 'g')
    
    
    
    ro = rocavspectroscopy_keysight_mixer.ROCavSpectroscopy_keysight_mixer(qubit_info, mixer_info1,mixer_info2, np.linspace(10,10,1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
    ro.measure()
    plt.close()
    plt.close()
    plt.figure('amp%s'%(figure_name))
    plt.plot(ro.freqs,ro.ampdata[0],label = 'qubit 1 in e')
    plt.figure('phase%s'%(figure_name))
    plt.plot(ro.freqs,ro.phasedata[0],label = 'qubit 1 in e')
    
    ro = rocavspectroscopy_keysight_mixer.ROCavSpectroscopy_keysight_mixer(qubit2_info, mixer_info1,mixer_info2, np.linspace(10,10,1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
    ro.measure()
    plt.close()
    plt.close()
    plt.figure('amp%s'%(figure_name))
    plt.plot(ro.freqs,ro.ampdata[0],label = 'qubit 2 in e')
    plt.figure('phase%s'%(figure_name))
    plt.plot(ro.freqs,ro.phasedata[0],label = 'qubit 2 in e')
    
    plt.legend()
    
    ro_freq = 10.8201e9
    power = 10
    mixer_info1 = mclient.get_qubit_info('mixer_info1')
    mixer_info2 = mclient.get_qubit_info('mixer_info2')
    readout_info.rfsource1.set_frequency(ro_freq - mixer_info1.deltaf)
    readout_info.rfsource1.set_power(power)
    readout_info.rfsource1.set_rf_on(True)
    readout_info.rfsource2.set_power(10)
    readout_info.rfsource2.set_rf_on(True)
    readout_info.rfsource2.set_frequency(ro_freq+50e6)
    bla


if 0: # cav transmission with mixer

    from single_cavity import rocavspectroscopy_keysight_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
#    Yoko.do_set_current(-0.00175)
    mixer1_amps = np.linspace(0.1,0.1,1)


    rofreq = 10.82e9
    freq_range = 4e6
    for mixer1_amp in mixer1_amps:
        mixer2_amp = mixer1_amp
        mixer_info1_set.set_pi_amp(mixer1_amp)
        mixer_info2_set.set_pi_amp(mixer2_amp)
        mixer_info1 = mclient.get_qubit_info('mixer_info1')
        mixer_info2 = mclient.get_qubit_info('mixer_info2')
        ro = rocavspectroscopy_keysight_mixer.ROCavSpectroscopy_keysight_mixer(qubit_info, mixer_info1,mixer_info2, np.linspace(10,10,1),
                                                 np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                                 qubit_pulse=False, seq=None)#,extra_info=[ef2_info])
        ro.measure()
        plt.close()
        plt.close()
        
        figure_name = '0T'
        
        plt.figure('amp%s'%(figure_name))
        plt.plot(ro.freqs,ro.ampdata[0],label = 'mixer1_amp = %s, mixer2_amp = %s'%(mixer1_amp, mixer2_amp))
        if mixer1_amp == mixer1_amps[-1]:
            fn = os.path.join(r'C:\_Data', 'images/%s_amp%s.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),figure_name))
            fdir = os.path.split(fn)[0]
            if not os.path.isdir(fdir):
                os.makedirs(fdir)
            kwargs = dict()
            plt.savefig(fn, **kwargs)
        plt.figure('phase%s'%(figure_name))
        plt.plot(ro.freqs,ro.phasedata[0],label = 'mixer1_amp = %s, mixer2_amp = %s'%(mixer1_amp, mixer2_amp))
        if mixer1_amp == mixer1_amps[-1]:
            fn = os.path.join(r'C:\_Data', 'images/%s_phase%s.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),figure_name))
            fdir = os.path.split(fn)[0]
            if not os.path.isdir(fdir):
                os.makedirs(fdir)
            kwargs = dict()
            plt.savefig(fn, **kwargs)
    
    bla
    
    
if 1: # cav transmission with mixer and CW qubit drive

    from single_cavity import rocavspectroscopy_keysight_mixer_cw
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
#    Yoko.do_set_current(-0.00175)
#    mixer1_amp = .3
#    mixer_info1_set.set_pi_amp(mixer1_amp)
    mixer1_amp = 0.04
    mixer2_amp = 0
    
    mixer_info1_set.set_pi_amp(mixer1_amp)
    mixer_info2_set.set_pi_amp(mixer2_amp)

    mixer_info1 = mclient.get_qubit_info('mixer_info1')
    mixer_info2 = mclient.get_qubit_info('mixer_info2')
    phase = 0
    rofreq = 10.825e9
    freq_range = 10e6
    ro = rocavspectroscopy_keysight_mixer_cw.ROCavSpectroscopy_keysight_mixer_cw(qubit_info, mixer_info1, mixer_info2, phase, 
                                             np.linspace(10,10,1),np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                             qubit_pulse=False, seq=None)#,extra_info=[ef2_info])
    ro.measure()
    plt.close()
    plt.close()
    
    figure_name = 'Qubit 1'
    
    plt.figure('amp%s'%(figure_name))
    plt.plot(ro.freqs,ro.ampdata[0],label = 'g')
    plt.figure('phase%s'%(figure_name))
    plt.plot(ro.freqs,ro.phasedata[0],label = 'g')
    
    
    
    ro = rocavspectroscopy_keysight_mixer_cw.ROCavSpectroscopy_keysight_mixer_cw(qubit_info, mixer_info1, mixer_info2, phase, 
                                            np.linspace(10,10,1),np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
    ro.measure()
    plt.figure('amp%s'%(figure_name))
    plt.plot(ro.freqs,ro.ampdata[0],label = 'qubit 1 in CW drive')
    plt.figure('phase%s'%(figure_name))
    plt.plot(ro.freqs,ro.phasedata[0],label = 'qubit 1 in CW drive')

    ro_freq = 10.8205e9
    power = 10
    readout_info.rfsource1.set_frequency(ro_freq - mixer_info1.deltaf)
    readout_info.rfsource1.set_power(power)
    readout_info.rfsource1.set_rf_on(True)
    readout_info.rfsource2.set_power(10)
    readout_info.rfsource2.set_rf_on(True)
    readout_info.rfsource2.set_frequency(ro_freq+50e6)
    bla

if 0: # demag cycle
    
    fields = [-0.04,0.03,-0.025,0.02,-0.015,0.01,-0.005, 0.0025, -0.001,0.0005,-0.00025, 0]
    fields = - np.asarray(fields)
    Magnet.do_set_PSwitch(1)
    time.sleep(35)
#fields = np.linspace(0,-0.05,26)
    for field in fields:
        print(field)
        Magnet.do_set_field(field)
        time.sleep(800)
    
    Magnet.do_set_field(0)
    time.sleep(600)
    print('Demag done')
    Magnet.do_set_PSwitch(0)
    print('start magnet cooling')
    time.sleep(350)
    print('Magnet in persistent mode')
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
#    Yoko.do_set_current(-0.00175)
##
    bla
if 0: # cav transmission with asymmetric drive 
    from single_cavity import asymmetric_drive_cav_spec
    rofreq = 10.825e9
    freq_range = 25e6
    amps1 = np.linspace(.35,.001,36)
    amps2 = np.linspace(.35,.699,36)
##    phase1 = np.linspace(2.09813509,3.05183286,6)
    phase1 = np.linspace(0,2*np.pi,36)
#    amps1 = [0.52]
#    amps2 = [0.18]
#    phase1 = [1.97]
    dig.do_set_naverages(2000)
    print('Starting sweep')
    for j in range(len(phase1)):
        for i in range(len(amps1)):
            mixer_info1_set.set_pi_amp(amps1[i])
            mixer_info2_set.set_pi_amp(amps2[i])
            mixer_info1 = mclient.get_qubit_info('mixer_info1')
            mixer_info2 = mclient.get_qubit_info('mixer_info2')
            ro = asymmetric_drive_cav_spec.AsymROCavSpectroscopy_keysight(qubit2_info, np.linspace(10,0,1),
                                                     mixer_info1, mixer_info2, phase1[j], np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                                     qubit_pulse=False, seq=None)#,extra_info=[ef2_info])
            ro.measure()
            
#            ro = asymmetric_drive_cav_spec.AsymROCavSpectroscopy_keysight(qubit2_info, np.linspace(10,0,1),
#                                                     mixer_info1, mixer_info2, phase1[j], np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
#                                                     qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
#            ro.measure()
#        plt.close()
#        plt.close()
#        
#        figure_name = 'S31 amp1 = %s amp2 = %s'%(amps1[i],amps2[i])
#        
#        plt.figure('amplitude%s'%(figure_name))
#        plt.plot(ro.freqs,ro.ampdata[0])
#        plt.figure('phase%s'%(figure_name))
#        plt.plot(ro.freqs,ro.phasedata[0])
    bla


if 0: # cav trans with qubit brick on and off
    from single_cavity import rocavspec_qubitge
    qubit_source = mclient.instruments['SC_qubit']
#    qubit_source = mclient.instruments['qubitbrick']
    rofreq = 10.713e9
    freq_range = 8e6
    ro = rocavspec_qubitge.ROCavSpec_Qubitge(qubit_source, qubit_info, np.linspace(0, 10, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 161),
                                             qubit_pulse=True,seq=None)#,extra_info=[ef2_info])
    ro.measure()  
#    ea_on = ro.ampedata[0]
#    ep_on = ro.phaseedata[0]
#    e_on = ea_on * np.exp(1j*(ep_on/180 * np.pi))
#    ea_off = ro.ampgdata[0]
#    ep_off = ro.phasegdata[0]
#    e_off = ea_off * np.exp(1j*(ep_off/180 * np.pi))
#
#
#    ro = rocavspec_qubitge.ROCavSpec_Qubitge(qubit_source, qubit2_info, np.linspace(6, 10, 1),
#                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
#                                             qubit_pulse=False,seq=None)#,extra_info=[ef2_info])
#    ro.measure()  
#    ga_on = ro.ampedata[0]
#    gp_on = ro.phaseedata[0]
#    g_on = ga_on * np.exp(1j*(gp_on/180 * np.pi))
#    ga_off = ro.ampgdata[0]
#    gp_off = ro.phasegdata[0]
#    g_off = ga_off * np.exp(1j*(gp_off/180 * np.pi))    
#    
#    print('\n')
#    diff_c_e = np.sum(np.abs(e_on-e_off))/np.sum(np.abs(e_off))
#    diff_a_e = np.sum(ea_on - ea_off)/np.sum(ea_off)
#    print('diff_c_e  = %s / %s = %s'%(np.sum(np.abs(e_on-e_off)),np.sum(np.abs(e_off)), diff_c_e))
#    print('diff_a_e  = %s / %s = %s'%(np.sum(ea_on - ea_off),np.sum(ea_off), diff_a_e))    
#    
#    diff_c_g = np.sum(np.abs(g_on-g_off))/np.sum(np.abs(g_off))
#    diff_a_g = np.sum(ga_on - ga_off)/np.sum(ga_off)
#    print('diff_c_g  = %s / %s = %s'%(np.sum(np.abs(g_on-g_off)),np.sum(np.abs(g_off)), diff_c_g))
#    print('diff_a_g  = %s / %s = %s'%(np.sum(ga_on - ga_off),np.sum(ga_off), diff_a_g))    
#    
#    diff_c_off = np.sum(np.abs(e_off-g_off))/np.sum(np.abs(g_off))
#    diff_a_off = np.sum(ea_off - ga_off)/np.sum(ga_off)
#    print('diff_c_off  = %s / %s = %s'%(np.sum(np.abs(e_off-g_off)),np.sum(np.abs(g_off)), diff_c_off))
#    print('diff_a_off  = %s / %s = %s'%(np.sum(ea_off - ga_off),np.sum(ga_off), diff_a_off))
#    
#    diff_c_sub = np.sum(np.abs((e_on-e_off)-(g_on-g_off)))/np.sum(np.abs(g_off))
#    diff_a_sub = np.sum((ea_on-ea_off) - (ga_on-ga_off))/np.sum(ga_off)
#    print('diff_c_sub  = %s / %s = %s'%(np.sum(np.abs((e_on-e_off)-(g_on-g_off))),np.sum(np.abs(g_off)), diff_c_sub))
#    print('diff_a_sub  = %s / %s = %s'%(np.sum((ea_on-ea_off) - (ga_on-ga_off)), np.sum(ga_off),diff_a_sub))
#    
    bla
if 0: # sweeping flux to find phase 
    from single_cavity import flux_phase_sweep
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
#    Yoko.do_set_current(-0.00175)
    Yoko = mclient.instruments['Yoko']
    rofreq = 7549.0e6
    freq_range = 20e6
    ccenter = 0e-3
    crange = 4e-3
    ro = flux_phase_sweep.flux_phase_sweep(qubit_info, np.linspace(-5, 0, 1),
                                             np.linspace(ccenter-crange, ccenter+crange, 201), current_source=Yoko,
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
                                               plen=20000, amp=0.3, qubit_pulse=False)
    ro.measure()
    bla
    

if 0: #     qubit spectroscopy
    from single_qubit import spectroscopy_keysight
#    from scripts.single_qubit import spectroscopy_IQ
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0), ef_info.rotate(np.pi, 0)])
#    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#    for i in [-20,-15,-10,-5,0,5]:
#        for a in [0.001, 0.01, 0.05, 0.1, 0.5]:
    qubit_freq =10.7e9
        
    freq_range = 10e6
#    for current in np.linspace(-8, -10, 5):
#        yoko.do_set_current(current)
    spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['SS_drive'], ef2_info,
                                         np.linspace(qubit_freq-freq_range,
                                                     qubit_freq+freq_range, 2), [10],
                                         plen=50000, amp=0.1, seq=None, postseq=None, plot_seqs=False)
    spec.measure()
    bla

if 0: #     use qubit spectroscopy to find FWM freq
    from single_qubit import spectroscopy_keysight
#    from scripts.single_qubit import spectroscopy_IQ
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
    postseq = sequencer.Sequence(qubit2_info.rotate(np.pi/2, 0))
#    for i in [-20,-15,-10,-5,0,5]:
#        for a in [0.001, 0.01, 0.05, 0.1, 0.5]:
    ROfreq = 10933e6
    ge = 8893.5e6
    ef = 8417e6 
    FWM_freq = np.abs(ROfreq - ge - ef) + 100e6
        
    freq_range = 20e6
#    for current in np.linspace(-8, -10, 5):
#        yoko.do_set_current(current)
    spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['qubit2FWMbrick'], fwm2_info,
                                         np.linspace(FWM_freq-freq_range,
                                                     FWM_freq+freq_range, 11), [6],
                                         plen=1000, amp=0.2, seq=seq, postseq=None, plot_seqs=None,extra_info=[qubit2_info, ef2_info])
    spec.measure()
    bla

if 0: # Qubit spec with phase correction
    from single_qubit import spectroscopy_keysight_phasecorrection
#    for i in [0,-3,-6,-9,-12]:
#    from scripts.single_qubit import spectroscopy_IQ
    qubit_freq = 437.6e6
    freq_range = 30e6
    for i in [1000]:
        spec = spectroscopy_keysight_phasecorrection.Spectroscopy_Keysight_phasecorrection(mclient.instruments['QK'], qubit_info,
                                     np.linspace(qubit_freq-freq_range, qubit_freq+freq_range, 71), [0],
                                     plen=i, amp=0.05, plot_seqs=False) #1=1ns

#    spec = spectroscopy_IQ.Spectroscopy_IQ(client.instruments['gen'], qubit_info,
#                                     np.linspace(702e6, 710e6, 81), [-30],
#                                    plen=250*100, amp=0.1, ssb=False, plot_seqs=False)

        spec.measure()
    
    bla    
    
    

if 0: # SSB spec
    from single_qubit import ssbspec
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    for i in range(1):        
#        RObrick.do_set_power(i)
        seq = sequencer.Trigger(600)
#        seq = Join([seq, qubit2_info.rotate(np.pi/2, X_AXIS)])
        spec = ssbspec.SSBSpec(qubit_info, np.linspace(-20e6, 20e6, 101), seq=seq, plot_seqs=False, proj_func='projection')
        spec.measure_keysight()
#        plt.close()
    bla
    
if 0: # SSB spec with mixer
    from single_qubit import ssbspec_mixer
    #    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    for i in range(1):        
    #        RObrick.do_set_power(i)
        seq = sequencer.Trigger(600)
    #        seq = Join([seq, qubit2_info.rotate(np.pi/2, X_AXIS)])
        spec = ssbspec_mixer.SSBSpec_mixer(qubit_info, mixer_info1,mixer_info2,
                                           np.linspace(-20e6, 20e6, 101), seq=seq, plot_seqs=True, proj_func='phase')
        spec.measure_keysight()
#        plt.close()
    bla

    
if 1: #ssb with stark shift with mixer with lorentzian fit
    from single_qubit import stark_shift_with_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    phase1 = 3.141
#    mixer_info1_set.set_deltaf(-100e6)
#    mixer_info1_set.set_deltaf(-100e6)
#    mixer_info1 = mclient.get_qubit_info('mixer_info1')
#    mixer_info2 = mclient.get_qubit_info('mixer_info2')
    for i in range(1):        
#        RObrick.do_set_power(i)
        seq = sequencer.Trigger(600)
#        seq = Join([seq, qubit2_info.rotate(np.pi/2, X_AXIS)])
        spec = stark_shift_with_mixer.Stark_shift_with_mixer(qubit_info, mixer_info1,mixer_info2,SS_mixer_info1,SS_mixer_info2, 
                                                             phase1, np.linspace(-40e6, 20e6, 101), seq=seq, plot_seqs=False, 
                                                             proj_func='amplitude')
        spec.measure_keysight()
#        plt.close()
    shift = spec.center
    bla

if 0: # SSB spec with lorentzian fit
    from single_qubit import ssbspec_lorentzianfit
    seq = sequencer.Trigger(600)
    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-4e6, 4e6, 81), seq=seq, plot_seqs=False, 
                                                       proj_func='projection', extra_info = [readout_iq_whatever])
    spec.measure_keysight()
    center = spec.center
    height = spec.height
    width = spec.width
    bla
    
if 0: # SSB spec with gaussian fit
    from single_qubit import ssbspec_gaussianfit
    seq = sequencer.Trigger(600)
    spec = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit_info, np.linspace(-20e6, 20e6, 81), seq=seq, plot_seqs=False, 
                                                   proj_func='projection')
    spec.measure_keysight()
    
    bla

if 0: # SSB spec with Stark Shift tone with gaussian fit
    from single_qubit import ssbspec_gaussianfit_SS
    seq = sequencer.Trigger(600)
    spec = ssbspec_gaussianfit_SS.SSBSpec_Gaussianfit_SS(qubit_info, np.linspace(-20e6, 20e6, 81), seq=seq, plot_seqs=False, 
                                                         proj_func='projection')
    spec.measure_keysight()
    
    bla
    
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
#    plt.figure()
#    plt.plot(freq_array, data_avg)
#    bla
#     
#    
if 0: # Power Rabi-Calibrate pi pulse

#    for cool_time in [1e3,5e3,10e3,30e3]:
#        for amp in [0.01, 0.01,0.02,0.04,0.08]:
#    cool = sequencer.Combined([sequencer.Constant(int(cool_time), amp, chan=ef_info.sideband_channels[0]),
#                                   sequencer.Constant(int(cool_time), amp, chan=ef_info.sideband_channels[1]),
#                                   sequencer.Constant(int(cool_time), 1, chan='3m1')])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
#    postseq = sequencer.Sequence(ef2_info.rotate(np.pi/2, 0))
    from single_qubit import rabi
    import time
    update_proj = True
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    tr = rabi.Rabi(qubit_info, 
#                               np.linspace(-0.5, 0.5, 81), selective=False,
                               np.linspace(-0.6, 0.6, 81), selective=False,
#                               np.linspace(-0.1, 0.1, 81), selective=True,
#                               np.linspace(-0.03, 0.03, 81), selective=True,
        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                               plot_seqs=False, generate=True, repeat_pulse=1,# seq=seq,postseq = postseq,
                               update=True, #extra_info=[qubit2_info, ef2_info],
                               proj_func='projection')
    tr.measure_keysight()
    
    if update_proj:
        if np.abs(tr.avg_data[np.argmax(abs(tr.avg_data))] - tr.avg_data[len(tr.amps)/2]) < np.abs(tr.avg_data[np.argmin(abs(tr.avg_data))] - tr.avg_data[len(tr.amps)/2]):
            readout.set_IQg(tr.avg_data[np.argmax(abs(tr.avg_data))])
            readout.set_IQe(tr.avg_data[np.argmin(abs(tr.avg_data))])
            
        else:
            readout.set_IQg(tr.avg_data[np.argmin(abs(tr.avg_data))])
            readout.set_IQe(tr.avg_data[np.argmax(abs(tr.avg_data))])
        print abs(tr.avg_data[np.argmax(abs(tr.avg_data))]- tr.avg_data[np.argmin(abs(tr.avg_data))])
    bla


if 0: # Power Rabi-Calibrate pi pulse with mixer

#    for cool_time in [1e3,5e3,10e3,30e3]:
#        for amp in [0.01, 0.01,0.02,0.04,0.08]:
#    cool = sequencer.Combined([sequencer.Constant(int(cool_time), amp, chan=ef_info.sideband_channels[0]),
#                                   sequencer.Constant(int(cool_time), amp, chan=ef_info.sideband_channels[1]),
#                                   sequencer.Constant(int(cool_time), 1, chan='3m1')])

    from single_qubit import rabi_mixer
    import time
    update_proj =False
#    seq = sequencer.Sequence([sequencer.Trigger(400)])
#    seq = sequencer.Sequence([sequencer.Trigger(400), qubit_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
#    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    tr = rabi_mixer.Rabi_mixer(qubit_info, mixer_info1, mixer_info2,
#                               np.linspace(-0.8, 0.8, 81), selective=False,
#                               np.linspace(-0.6, 0.6, 81), selective=False,
                               np.linspace(-0.08, 0.08, 81), selective=True,
#                               np.linspace(-0.4, 0.4, 81), selective=True,
        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                               plot_seqs=False, generate=True, repeat_pulse=1,# seq=seq,postseq = postseq, fix_period = 0.38087745,
                               update=True, #extra_info=[qubit_info],
                               proj_func='phase')
    tr.measure_keysight()
    
    if update_proj:
        if np.abs(tr.avg_data[np.argmax(abs(tr.avg_data))] - tr.avg_data[len(tr.amps)/2]) < np.abs(tr.avg_data[np.argmin(abs(tr.avg_data))] - tr.avg_data[len(tr.amps)/2]):
            readout.set_IQg(tr.avg_data[np.argmax(abs(tr.avg_data))])
            readout.set_IQe(tr.avg_data[np.argmin(abs(tr.avg_data))])
            
        else:
            readout.set_IQg(tr.avg_data[np.argmin(abs(tr.avg_data))])
            readout.set_IQe(tr.avg_data[np.argmax(abs(tr.avg_data))])
        print abs(tr.avg_data[np.argmax(abs(tr.avg_data))]- tr.avg_data[np.argmin(abs(tr.avg_data))])
    bla

if 0: # ef Power Rabi-Calibrate pi pulse

#    for cool_time in [1e3,5e3,10e3,30e3]:
#        for amp in [0.01, 0.01,0.02,0.04,0.08]:
#    cool = sequencer.Combined([sequencer.Constant(int(cool_time), amp, chan=ef_info.sideband_channels[0]),
#                                   sequencer.Constant(int(cool_time), amp, chan=ef_info.sideband_channels[1]),
#                                   sequencer.Constant(int(cool_time), 1, chan='3m1')])
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
    from single_qubit import rabi
    import time
    update_proj =False
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    tr = rabi.Rabi(ef_info, 
                               np.linspace(-0.9, 0.9, 81), selective=False,
#                               np.linspace(-0.7, 0.7, 81), selective=False,
#                               np.linspace(-0.075, 0.075, 81), selective=True,
#                               np.linspace(-0.2, 0.2, 81), selective=True,
        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                               plot_seqs=False, generate=True, repeat_pulse=1, seq=seq,postseq = postseq,
                               update=True, extra_info=[qubit_info],
                               proj_func='phase')
    tr.measure_keysight()
    
    if update_proj:
        if np.abs(tr.avg_data[np.argmax(abs(tr.avg_data))] - tr.avg_data[len(tr.amps)/2]) < np.abs(tr.avg_data[np.argmin(abs(tr.avg_data))] - tr.avg_data[len(tr.amps)/2]):
            readout.set_IQg(tr.avg_data[np.argmax(abs(tr.avg_data))])
            readout.set_IQe(tr.avg_data[np.argmin(abs(tr.avg_data))])
            
        else:
            readout.set_IQg(tr.avg_data[np.argmin(abs(tr.avg_data))])
            readout.set_IQe(tr.avg_data[np.argmax(abs(tr.avg_data))])
        print abs(tr.avg_data[np.argmax(abs(tr.avg_data))]- tr.avg_data[np.argmin(abs(tr.avg_data))])
    bla
    
if 0: # ef Power Rabi-Calibrate pi pulse mixer

#    for cool_time in [1e3,5e3,10e3,30e3]:
#        for amp in [0.01, 0.01,0.02,0.04,0.08]:
#    cool = sequencer.Combined([sequencer.Constant(int(cool_time), amp, chan=ef_info.sideband_channels[0]),
#                                   sequencer.Constant(int(cool_time), amp, chan=ef_info.sideband_channels[1]),
#                                   sequencer.Constant(int(cool_time), 1, chan='3m1')])
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#    seq = sequencer.Sequence([sequencer.Trigger(250)])
#    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
    from single_qubit import rabi_mixer
    import time
    update_proj =False
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    tr = rabi_mixer.Rabi_mixer(ef_info, mixer_info1, mixer_info2,
#                               np.linspace(-0.3, 0.3, 81), selective=False,
#                               np.linspace(-.6, .6, 81), selective=False,
#                               np.linspace(-0.05, 0.05, 81), selective=True,
                               np.linspace(-0.1, 0.1, 81), selective=True,
        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                               plot_seqs=False, generate=True, repeat_pulse=1, seq=seq,postseq = postseq,#fix_period = 0.834,
                               update=True, extra_info = qubit_info,
                               proj_func='phase')
    tr.measure_keysight()
    
    if update_proj:
        if np.abs(tr.avg_data[np.argmax(abs(tr.avg_data))] - tr.avg_data[len(tr.amps)/2]) < np.abs(tr.avg_data[np.argmin(abs(tr.avg_data))] - tr.avg_data[len(tr.amps)/2]):
            readout.set_IQg(tr.avg_data[np.argmax(abs(tr.avg_data))])
            readout.set_IQe(tr.avg_data[np.argmin(abs(tr.avg_data))])
            
        else:
            readout.set_IQg(tr.avg_data[np.argmin(abs(tr.avg_data))])
            readout.set_IQe(tr.avg_data[np.argmax(abs(tr.avg_data))])
        print abs(tr.avg_data[np.argmax(abs(tr.avg_data))]- tr.avg_data[np.argmin(abs(tr.avg_data))])
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

    t1 = T1measurement.T1Measurement(qubit2_info, #np.linspace(0, 500e3, 101),
                                         np.linspace(0e3, 50e3, 101),
#                                         np.concatenate((np.linspace(5e3, 5e3, 50), np.linspace(6e3, 6e3, 51))),
                                         double_exp=False, generate=True, plot_seqs=False, proj_func='projection', seq=None)    
    t1.measure_keysight()
    bla

if 0: # T1 mixer

    from single_qubit import T1measurement_mixer

#    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 250e3, 121), 
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(2000, 1, chan='3m1'), sequencer.Delay(250),
#                          ef_info.rotate(np.pi, 0), sequencer.Constant(4000, 1, chan='3m1'), sequencer.Delay(250)])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])

    t1 = T1measurement_mixer.T1Measurement_mixer(qubit_info, mixer_info1, mixer_info2, #np.linspace(0, 500e3, 101),
                                         np.linspace(0e3, 4e3, 101),
#                                         np.concatenate((np.linspace(5e3, 5e3, 50), np.linspace(6e3, 6e3, 51))),
                                         double_exp=False, generate=True, plot_seqs=False, proj_func='phase', seq=None)    
    t1.measure_keysight()
    bla

if 0: # T1 - alternating pi-pulse and saturation T1
    from single_qubit import T1_alternate_pi_saturation

    t1 = T1_alternate_pi_saturation.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
                                     np.concatenate((np.linspace(0.1e3, 10e3, 21), np.linspace(11e3, 150e3, 26), np.linspace(155e3, 650e3, 30))),
                                     double_exp=True, generate=True, plot_seqs=False, proj_func='projection', seq=None)    
    t1.measure_keysight()
    bla

if 0:
    from scripts.single_qubit import ssbspec
    from scripts.single_qubit import rabi
    from scripts.single_qubit import T1measurement
    powers = np.linspace(-20, 10, 2)
    frequencies = np.linspace(120, 180, 3)

if 0: #T2
    from single_qubit import T2measurement
#    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
    for i in range(1):
        t2 = T2measurement.T2Measurement(qubit2_info, np.linspace(0, 3e3, 101), detune=4e6, double_freq=False, generate=True, 
                                         seq=None, postseq=None, proj_func='projection') #extra_info=[qubit2_info])
#        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')

        
        t2.measure_keysight()
    bla

if 1: #T2 mixer
    from single_qubit import T2measurement_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
    for i in range(1):
        t2 = T2measurement_mixer.T2Measurement_mixer(qubit_info, mixer_info1, mixer_info2, np.linspace(0, 1e3, 101), detune=8e6, 
                                                     double_freq=False, generate=True, #echotype = 'HANN',
                                                     seq=None, postseq=None, proj_func='phase') #extra_info=[qubit2_info])
#        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')

        
        t2.measure_keysight()
    bla
    
if 0: #ramsey mixer
    from single_qubit import ramsey_measurement
#    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
    for i in range(1):
        t2 = ramsey_measurement.Ramsey_Measurement_mixer(qubit_info, SS_mixer_info1, mixer_info1,mixer_info2, np.linspace(0, 3e3, 101), detune=2e6, double_freq=False, generate=True, 
                                         seq=None, postseq=None, proj_func='phase',plot_seqs = True) #extra_info=[qubit2_info])
#        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')

        
        t2.measure_keysight()
    bla

if 0: # Ramsey qubit 2 rabi sweep
    from single_qubit import T2measurementforramsey
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    amplitudes = np.linspace(-0.2, 0.2, 11)
    detunes = []
    for amplitude in amplitudes:
        t2 = T2measurementforramsey.T2MeasurementforRamsey(qubit_info, qubit2_info, amplitude, 
                                                           np.linspace(0, 5e3, 101), detune=2e6, double_freq=False, generate=True, 
                                                           seq=None, postseq=None, proj_func='phase')
#        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')

        
        t2.measure_keysight()
        detunes.append(t2.fit_params['freq'].value*1e3)
    plt.figure()
    plt.plot(amplitudes, detunes)
    bla

    
if 0: # Ramsey flux sweep
    from single_qubit import T2measurement
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    currents = np.linspace(-0.1, -0.3, 11)
    detunes = []
    for current in currents:
        yoko.do_set_current(current)
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 5e3, 101), detune=1e6, double_freq=False, generate=True, 
                                         seq=None, postseq=None, proj_func='amplitude')
#        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')

        
        t2.measure_keysight()
        detunes.append(t2.fit_params['freq'].value*1e3)
    plt.figure()
    plt.plot(currents, detunes)
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
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 5e3, 101), detune=1e6, echotype = T2measurement.ECHO_HAHN, necho=1, 
                                     plot_seqs = False, generate=True, proj_func='amplitude', seq=None)
    t2.measure_keysight()
    bla
    
if 0: # EF Qubit spec 
    from scripts.single_qubit import spectroscopy_keysight
    ef_freq = 3.679e9
    freq_range = 10e6
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
#    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
    spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['efBrick'], ef_info, np.linspace(ef_freq-freq_range, ef_freq+freq_range,21), [0],
                                     plen=1000, amp=0.12,
                                     seq=None, postseq=None,
                                     extra_info=qubit_info, plot_seqs=False)
    spec.measure()
    bla
    
if 0: # EF SSBspec
    from single_qubit import ssbspec
    seq = sequencer.Sequence([sequencer.Trigger(400), qubit_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    spec = ssbspec.SSBSpec(ef_info, np.linspace(-100e6, 100e6, 101), seq=seq, postseq = postseq, extra_info=qubit_info, 
                           plot_seqs=False, generate=True, proj_func='phase')
    spec.measure_keysight()
    bla   
    
if 0: # EF SSBspec mixer not sure why this one isn't working use one below
    from single_qubit import ssbspec_lorentzianfit_mixer
    seq = sequencer.Sequence([sequencer.Trigger(400), qubit_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    spec = ssbspec_lorentzianfit_mixer.SSBSpec_lorentzianfit_mixer(ef_info, mixer_info1, np.linspace(-10e6, 10e6, 101), seq=seq, postseq = postseq, extra_info=qubit_info, plot_seqs=False, generate=True, proj_func='phase')
    spec.measure_keysight()
#    fit_freq=spec.center
#    deltaf_1 = ef2_info_set.get_deltaf()
#    ef2_info_set.set_deltaf(deltaf_1+fit_freq*1e6)
    bla   
  
if 0: # EF SSBspec mixer
    from single_qubit import ssbspec_mixer
    seq = sequencer.Sequence([sequencer.Trigger(400), qubit_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    spec = ssbspec_mixer.SSBSpec_mixer(ef_info, mixer_info1, mixer_info2, np.linspace(-10e6, 10e6, 101), seq=seq, postseq = postseq, extra_info=qubit_info, plot_seqs=False, generate=True, proj_func='phase')
    spec.measure_keysight()
#    fit_freq=spec.center
#    deltaf_1 = ef2_info_set.get_deltaf()
#    ef2_info_set.set_deltaf(deltaf_1+fit_freq*1e6)
    bla   
    
if 0: # EF SSBspec repeat
    from single_qubit import ssbspec_lorentzianfit
    freq_ge = []   
    freq_ef = []
    for i in range(100):
        from single_qubit import ssbspec_gaussianfit
    
        seq = sequencer.Trigger(600)
        
        spec = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit_info, np.linspace(-5e6, 5e6, 101), seq=seq, plot_seqs=False, proj_func='phase')
        spec.measure_keysight()          
        
        freq_ge.append(spec.fit_params['freq'].value/1e6)
        plt.close()

        
        seq = sequencer.Sequence([sequencer.Trigger(400), qubit_info.rotate(np.pi, 0)])
    #    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
        postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
    #    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
        spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(ef_info, np.linspace(-50e6, 50e6, 101), seq=seq, postseq = postseq, extra_info=qubit_info, plot_seqs=False, generate=True, proj_func='phase')
        spec.measure_keysight()
        freq_ef.append(spec.center)
        plt.close()
        
    plt.figure()
    plt.plot(range(len(freq_ge)),freq_ge,label = 'ge freq')
    plt.plot(range(len(freq_ef)),freq_ef,label = 'ef freq')
    plt.legend()
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
    dig.set_naverages(3000)
    efr = efrabi.EFRabi(qubit2_info, ef2_info, np.linspace(-0.7, 0.7, 101), first_pi=True,second_pi=True, seq=None, generate=True, update=True,
                            proj_func='projection')
    efr.measure_keysight()
    period = efr.fit_params['period'].value
    dig.set_naverages(10000)
    efr = efrabi.EFRabi(qubit2_info, ef2_info, np.linspace(-0.7, 0.7, 101), first_pi=False, second_pi=True, selective=False, seq=None, generate=True,
                            force_period = period, proj_func='projection')
    efr.measure_keysight()
    dig.set_naverages(3000)
    bla

if 0: # EF rabi mixer
    from single_qubit import efrabi_mixer
#    dig = mclient.instruments['dig']
#    cool_time = 25e3
#    cool_time_range = [0.5e3, 1e3, 5e3, 10e3, 100e3]
#    amps = [0, 0.02, 0.05, 0.075, 0.1]
#    for cool_time in cool_time_range:
#    cool = sequencer.Combined([sequencer.Constant(int(cool_time), 0.1, chan=ef_info.sideband_channels[0]),
#                                   sequencer.Constant(int(cool_time), 0.1, chan=ef_info.sideband_channels[1]),
#                                   sequencer.Constant(int(cool_time), 1, chan='3m1')])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
#    dig.set_naverages(4000)
    efr = efrabi_mixer.EFRabi_mixer(qubit_info, ef_info, mixer_info1, mixer_info2, np.linspace(-0.4, 0.4, 101), first_pi=True,
                                    second_pi=True, seq=None, generate=True, update=True,
                                    proj_func='phase')
    efr.measure_keysight()
    period = efr.fit_params['period'].value
    dig.set_naverages(30000)
    efr = efrabi_mixer.EFRabi_mixer(qubit_info, ef_info, mixer_info1, mixer_info2, np.linspace(-0.4, 0.4, 101), first_pi=False, 
                                    second_pi=True, selective=False, seq=None, generate=True,
                                    force_period = period, proj_func='phase')
    efr.measure_keysight()
    dig.set_naverages(6000)
    bla

if 0: # FT1 
    from single_qubit import FT1measurement
#    fwm = mclient.instruments['qubit2FWMbrick']

    for i in range(1):
#        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.linspace(0, 2e3, 101), seq=None, proj_func='phase')
#        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.concatenate((np.linspace(0, 1e3, 31), np.linspace(1.01e3, 5e3, 31))), seq=None, proj_func='phase')

        ft1.measure_keysight()


    bla
    
if 0: # FT1 mixer This one isn't working, use one below
    from single_qubit import FT1measurement_mixer
#    fwm = mclient.instruments['qubit2FWMbrick']

    for i in range(1):
#        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])

        ft1 = FT1measurement_mixer.FT1Measurement_mixer(ef_info, ef_info, mixer_info1, np.linspace(0, 2e3, 101), seq=None, proj_func='phase')
#        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.concatenate((np.linspace(0, 1e3, 31), np.linspace(1.01e3, 5e3, 31))), seq=None, proj_func='phase')

        ft1.measure_keysight()


    bla
 
if 0: # FT1 mixer

    from single_qubit import T1measurement_mixer

#    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 250e3, 121), 
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(2000, 1, chan='3m1'), sequencer.Delay(250),
#                          ef_info.rotate(np.pi, 0), sequencer.Constant(4000, 1, chan='3m1'), sequencer.Delay(250)])
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
    postseq = sequencer.Sequence([qubit_info.rotate(np.pi/2, 0)])
    t1 = T1measurement_mixer.T1Measurement_mixer(ef_info, mixer_info1, mixer_info2, #np.linspace(0, 500e3, 101),
                                         np.linspace(0e3, 3e3, 101),
#                                         np.concatenate((np.linspace(5e3, 5e3, 50), np.linspace(6e3, 6e3, 51))),
                                         double_exp=False, generate=True, plot_seqs=False, proj_func='phase', seq=seq , postseq = postseq, extra_info=qubit_info)    
    t1.measure_keysight()
    bla
    
if 0: # FT1 with 2 ef freq
    from single_qubit import FT1measurementtwomode
#    fwm = mclient.instruments['qubit2FWMbrick']


    for i in range(1):
#        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
        ft1 = FT1measurement.FT1Measurement(qubit2_info, ef2_info, np.linspace(0, 30e3, 101), seq=None, proj_func='projection')
#        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.concatenate((np.linspace(0, 1e3, 31), np.linspace(1.01e3, 5e3, 31))), seq=None, proj_func='phase')

        ft1.measure_keysight()


    bla
    
if 0: # FT1 sweep
    from single_qubit import FT1measurement
    fwm = mclient.instruments['qubit2FWMbrick']
    freq = np.linspace(6.37e9,6.385e9,31)
    powers = np.linspace(-5,10,4)
    for power in powers:
        fwm.set_power(power)
        ft1times = np.zeros(len(freq))
        for i in range(len(freq)):
            fwm.set_frequency(freq[i])
    #        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
            ft1 = FT1measurement.FT1Measurement(qubit2_info, ef2_info, np.linspace(0, 30e3, 101), seq=None, proj_func='phase')
    #        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.concatenate((np.linspace(0, 1e3, 31), np.linspace(1.01e3, 5e3, 31))), seq=None, proj_func='phase')
    
    
    
            ft1.measure_keysight()
            ft1times[i] = ft1.analyze()
            plt.close()
        plt.figure()
        plt.plot(freq, ft1times/1000,label = 'power: %sdB'%(power))    
        plt.ylabel('FT1')
        plt.legend()
    bla
    
if 0: # FT1 with fwm
    from single_qubit import FT1withFwm
    fwm_gen = mclient.instruments['qubit2FWMbrick']
#    postseq = sequencer.Sequence(sequencer.Delay(5))
    postseq = sequencer.Sequence(ef2_info.rotate(np.pi/2, 0))
    amps = np.linspace(0.6,1,9)
    freqs = np.linspace(6.505e9, 6.515e9, 11)
    plt.figure()
    for freq in freqs:
        fwm_gen.set_frequency(freq)
        ft1times = np.zeros(len(amps))
        ft1err = np.zeros(len(amps))
        for i in range(len(amps)):
    #        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
            ft1 = FT1withFwm.FT1withFWM(qubit2_info, ef2_info, fwm2_info, fwm_pulse=True, delays = np.linspace(0, 2e3, 101), 
                                        amp = amps[i], seq=None, postseq = postseq, 
                                        proj_func='phase')
    #        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.concatenate((np.linspace(0, 1e3, 31), np.linspace(1.01e3, 5e3, 31))), seq=None, proj_func='phase')
    
            ft1.measure_keysight()
            ft1times[i] = ft1.fit_params['tau'].value
            ft1err[i] = ft1.fit_params['tau'].stderr
            plt.close()
#        plt.figure()
        plt.errorbar(amps, ft1times/1000,yerr = ft1err/1000,marker = 'o',label = 'g vs (e or f) freq = %s GHz'%(freq/1e9 - 0.14)) 
    plt.xlabel('amps')
    plt.ylabel('FT1(us)')
    plt.legend()


    bla
if 0: # EFT2
    from scripts.single_qubit import EFT2measurement # frequency stability of |f> vs |e>
    for i in range(1):
#        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
        seq = sequencer.Sequence(sequencer.Trigger(250))
        eft2 = EFT2measurement.EFT2Measurement(qubit_info, ef_info, np.linspace(0, 6e3, 101), detune=1e6, double_freq=False, plot_seqs = False, echotype = EFT2measurement.ECHO_NONE,
                                               proj_func='amplitude')
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
    
    cn = contrast_normalization.Contrast_Normalization(qubit_info, ef_info, seq=None, process_seq=None, generate=True, proj_func='phase')  #seq=seq was added
    
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



    
if 0: # Randomized benchmarking

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
    fwm_gen = mclient.instruments['qubit2FWMbrick']
#    ROfreq = 10936.2e6
#    ge = 6877.3e6
#    ef = 6783.1e6 
#    target_freq = np.abs(ROfreq - ge - ef)
    target_freq = 6.4785e9
    freq_range1 = 10e6
    freq_range2 = 10e6
    freqs = np.linspace(target_freq - freq_range1, target_freq + freq_range2, 101)
    amps = [.5] 
    powers = [10]
    shift_freq = np.zeros((len(amps), len(powers)))
    from FWM import FWM_f0g1
    for i, amp in enumerate(amps):
        for j, power in enumerate(powers):
            f0g1 = FWM_f0g1.FWM_f0g1(qubit_info, ef_info, fwm_gen, 1e3, 
                         freqs, power, amp, fwm2_info.sideband_channels[0])
            f0g1.measure()
            shift_freq[i, j] = f0g1.xs[np.argmax(f0g1.ampdata[:])]
            
if 0: # Qubit population
    from single_qubit import qubit_pop
    dig.set_naverages(300000)
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    qp = qubit_pop.Qubit_Pop(qubit_info, ef_info, generate=True, seq=None, proj_func='phase')
    qp.measure_keysight()
    print(qp.get_ys())
    
    
if 0: #f0 - g1 time domain
    fwm_gen = mclient.instruments['f0g1brick']
    from FWM import FWM_f0g1_t1
    f0g1 = FWM_f0g1_t1.FWM_f0g1_t1(qubit_info, ef_info, fwm_gen, np.linspace(0, 10e3, 101), 0.000001, '3m1', proj_func='phase')
    f0g1.measure_keysight()


if 0: # RO photon number measurement
    from single_qubit import T2measurement

#    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
#    noise_powers = -2
    t2_results = np.zeros(10)
    t2_errs = np.zeros(10)
#    for j in range(len(noise_powers)):
#        SC_noise.do_set_power(noise_powers[j])
    for i in range(5):
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 0.35e3, 101), detune=15e6, double_freq=False, generate=True, 
                                         seq=None, postseq=None, proj_func='amplitude') #extra_info=[qubit2_info])
#        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')
        t2.measure_keysight()
        t2_results[i] = t2.fit_params['tau'].value
        t2_errs[i] = t2.fit_params['tau'].stderr
        plt.close()
    bla    
    
if 0: ##Stark Shift
    freqs = np.linspace(10.711e9,10.711e9,5)
    freq_range = np.linspace(-7e6, 2e6, 81)
    powers= [9]
    phase = np.zeros((len(freqs),len(freq_range)))
    phase0 = np.zeros((len(freqs),len(freq_range)))
    fit_freq = np.zeros(len(freqs))
    fit_freq0 = np.zeros(len(freqs))
    fit_freq_err = np.zeros(len(freqs))
    fit_freq0_err = np.zeros(len(freqs))
    SSdrive = mclient.instruments['SS_drive']
    for ifreq, freq in enumerate(freqs):
        SSdrive.set_power(powers[0])
        SSdrive.set_frequency(freq)
        time.sleep(0.1)
        SSdrive.set_rf_on(True)
        time.sleep(0.1)
    
        from single_qubit import ssbspec_gaussianfit_SS
    
        seq = sequencer.Trigger(600)
        spec = ssbspec_gaussianfit_SS.SSBSpec_Gaussianfit_SS(qubit2_info, freq_range, seq=seq, plot_seqs=False, proj_func='projection')
        spec.measure_keysight()
        for j in range(len(freq_range)):
             phase[ifreq][j] = spec.pp_data[j] 
             
        
        if np.max(phase[ifreq]) - np.min(phase[ifreq])>300:
            for iphase in range(len(phase[ifreq])):
                if phase[ifreq][iphase] > 0:
                    phase[ifreq][iphase] = phase[ifreq][iphase] -360
                    
        
        phase[ifreq] = phase[ifreq] - np.average(phase[ifreq])            
            
             
        fit_freq[ifreq] = spec.fit_params['freq'].value
        fit_freq_err[ifreq] = spec.fit_params['freq'].stderr
        plt.close()
        
        
        
        
        SSdrive.set_rf_on(False)
        time.sleep(0.1)
        from single_qubit import ssbspec_gaussianfit
    
        seq = sequencer.Trigger(600)
        
        spec = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit2_info, freq_range, seq=seq, plot_seqs=False, proj_func='projection')
        spec.measure_keysight()
        for j in range(len(freq_range)):
             phase0[ifreq][j] = spec.pp_data[j] 
    
        
        if np.max(phase0[ifreq]) - np.min(phase0[ifreq])>300:
            for iphase in range(len(phase0[ifreq])):
                if phase0[ifreq][iphase] > 0:
                    phase0[ifreq][iphase] = phase0[ifreq][iphase] -360
                    
        
        phase0[ifreq] = phase0[ifreq] - np.average(phase0[ifreq])            
            
             
        fit_freq0[ifreq] = spec.fit_params['freq'].value
        fit_freq0_err[ifreq] = spec.fit_params['freq'].stderr
        plt.close()
    freqsplot = np.concatenate([freqs, np.asarray([freqs[1] - freqs[0] + freqs[-1]])])  
    freq_rangeplot = np.concatenate([freq_range, np.asarray([freq_range[1] - freq_range[0] + freq_range[-1]])])      
    X, Y = np.meshgrid(freqsplot, freq_rangeplot)
    Zp = np.transpose(phase)
    plt.figure()
    plt.pcolormesh(X,Y,Zp)
    plt.title('phase, power = %s dB'%(powers[0]))
    plt.colorbar()
    fn = os.path.join(r'C:\_Data', 'images/%s_phase.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    plt.savefig(fn, **kwargs) 
    Zp0 = np.transpose(phase0)
    plt.figure()
    plt.pcolormesh(X,Y,Zp0)
    plt.title('phase SSdrive off, power = %s dB'%(powers[0]))
    plt.colorbar()
    fn = os.path.join(r'C:\_Data', 'images/%s_phase0.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    plt.savefig(fn, **kwargs)
    
    plt.figure()
    plt.errorbar(freqs/1e6, fit_freq/1e6, yerr = fit_freq_err/1e6,label = 'SS on, %.03f +/- %.03f MHz'%(np.average(fit_freq/1e6),np.average(fit_freq_err/1e6)))
    plt.errorbar(freqs/1e6, fit_freq0/1e6, yerr = fit_freq0_err/1e6,label = 'SS off, %.03f +/- %.03f MHz'%(np.average(fit_freq0/1e6),np.average(fit_freq0_err/1e6)))
    plt.ylabel('MHz')
    plt.legend()
    fn = os.path.join(r'C:\_Data', 'images/%s_fit_freqs.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    plt.savefig(fn, **kwargs)
        
        
        
        