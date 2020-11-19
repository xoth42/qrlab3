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
ef2_info = mclient.get_qubit_info('qubit2ef')
ef2_info_set = mclient.instruments['qubit2ef']
#ef2_V2_info = mclient.get_qubit_info('qubit2ef_V2')
#fwm_info = mclient.get_qubit_info('fwm_info1')
#fwm_info2 = mclient.get_qubit_info('fwm_info2')
mixer_info1 = mclient.get_qubit_info('mixer_info1')
SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
SS_mixer_info2 = mclient.get_qubit_info('SS_mixer_info2')
mixer_info2 = mclient.get_qubit_info('mixer_info2')
mixer_info1_set = mclient.instruments['mixer_info1']
mixer_info2_set = mclient.instruments['mixer_info2']
SS_mixer_info1_set = mclient.instruments['SS_mixer_info1']
SS_mixer_info2_set = mclient.instruments['SS_mixer_info2']
#fwm2_info = mclient.get_qubit_info('fwm_info2')
#qubit03_info = mclient.get_qubit_info('qubit1_03')
#qubit14_info = mclient.get_qubit_info('qubit1_14')
readout_info = mclient.get_readout_info('readout')
readout = mclient.instruments['readout']
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')

#fwm_gen = mclient.instruments['SS_drive']
#fwm_gen2 = mclient.instruments['SC_qubit2FWM']
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
    avgs = dig.test_dig_demod(6500, 1000)
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
    print np.angle(np.average(avgs[0:50]))*180/np.pi
    bla

if 0: # test digitizer
    dig = mclient.instruments['dig']
    data_ave = np.zeros(1500)
    for i in range(100):
        
       data = dig.test_dig(1500, 1, 1, 1)
       data_ave = data_ave + data[0][0]
       
#    print(np.shape(data))
    plt.figure()
    plt.plot(data_ave, label = 'sig')
    plt.plot(data[1][0][:], label = 'ref')
    plt.legend()
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
    bla
    
if 0: # cav transmission

    from single_cavity import rocavspectroscopy_keysight
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
#    Yoko.do_set_current(-0.00175)
    rofreq = 10.81434e9
    freq_range = 10e6
    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit2_info, np.linspace(-6,-6,1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                             qubit_pulse=False, seq=None)#,extra_info=[ef2_info])
    ro.measure()

    plt.close()
    plt.close()

    figure_name = 'Cavity Transmission S31 .028T'
    
    plt.figure('amp%s'%(figure_name))
    plt.plot(ro.freqs,ro.ampdata[0],label = 'g')
    plt.figure('phase%s'%(figure_name))
    plt.plot(ro.freqs,ro.phasedata[0],label = 'g')
    
    
    
#    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit2_info, np.linspace(-6,10,1),
#                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
#                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
#    ro.measure()
#    plt.figure('amp%s'%(figure_name))
#    plt.plot(ro.freqs,ro.ampdata[0],label = 'qubit 2 in e')
#    plt.figure('phase%s'%(figure_name))
#    plt.plot(ro.freqs,ro.phasedata[0],label = 'qubit 2 in e')
#    
##    
#    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit2_info, np.linspace(10,10, 1),
#                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
#                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
#    ro.measure()
#    plt.close()
#    plt.close()
##    plt.figure('amp%s'%(figure_name))
##    plt.plot(ro.freqs,ro.ampdata[0],label = 'e')
##    plt.legend()
##
##    plt.figure('phase%s'%(figure_name))
##    plt.plot(ro.freqs,ro.phasedata[0],label = 'e')
##    plt.legend()
##    
##    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
##    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit2_info, np.linspace(10,10,1),
##                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
##                                             qubit_pulse=False, seq=seq ,extra_info=[ef2_info])
##    ro.measure()
###    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0),ef2_V2_info.rotate(np.pi, 0)])
###    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit2_info, np.linspace(10,10,1),
###                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
###                                             qubit_pulse=False, seq=seq ,extra_info=[ef2_info,ef2_V2_info])
###    ro.measure()
##    
##    plt.close()
##    plt.close()
##    
#    plt.figure('amp%s'%(figure_name))
#    plt.plot(ro.freqs,ro.ampdata[0],label = 'e')
#    plt.legend()
#    fn = os.path.join(r'C:\_Data', 'images/%s_amp%s.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),figure_name))
#    fdir = os.path.split(fn)[0]
#    if not os.path.isdir(fdir):
#        os.makedirs(fdir)
#    kwargs = dict()
#    plt.savefig(fn, **kwargs)
#    
#    plt.figure('phase%s'%(figure_name))
#    plt.plot(ro.freqs,ro.phasedata[0],label = 'e')
#    plt.legend()
#    fn = os.path.join(r'C:\_Data', 'images/%s_phase%s.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),figure_name))
#    fdir = os.path.split(fn)[0]
#    if not os.path.isdir(fdir):
#        os.makedirs(fdir)
#    kwargs = dict()
#    plt.savefig(fn, **kwargs)

#by Yingying
#    ro_freq = ro.fit_params[2]
#    print ro_freq
    ro_freq = 10.81434e9
    power = 10
    readout_info.rfsource1.set_frequency(ro_freq)
    readout_info.rfsource1.set_power(power)
    readout_info.rfsource2.set_frequency(ro_freq+50e6)
    bla

if 0: # cav transmission with mixer

    from single_cavity import rocavspectroscopy_keysight_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
#    Yoko.do_set_current(-0.00175)
    amps = np.linspace(.2,.4,6)
    for i in range(len(amps)):
        mixer1_amp = 0
        mixer2_amp = amps[i]
        
        mixer_info1_set.set_pi_amp(mixer1_amp)
        mixer_info2_set.set_pi_amp(mixer2_amp)
        
        mixer_info1 = mclient.get_qubit_info('mixer_info1')
        mixer_info2 = mclient.get_qubit_info('mixer_info2')
        
        rofreq = 10.825e9
        freq_range = 15e6
        ro = rocavspectroscopy_keysight_mixer.ROCavSpectroscopy_keysight_mixer(qubit2_info, mixer_info1, mixer_info2, np.linspace(10,10,1),
                                                 np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                                 qubit_pulse=False, seq=None)#,extra_info=[ef2_info])
        ro.measure()
        plt.close()
        plt.close()
        
        figure_name = 'cav2 spec'
        
        plt.figure('amp%s'%(figure_name))
        plt.plot(ro.freqs,ro.ampdata[0],label = 'g, amp = %s'%(amps[i]))
        plt.legend()
        plt.figure('phase%s'%(figure_name))
        plt.plot(ro.freqs,ro.phasedata[0],label = 'g')
        plt.legend()
        
        
#        ro = rocavspectroscopy_keysight_mixer.ROCavSpectroscopy_keysight_mixer(qubit_info, mixer_info1, mixer_info2, np.linspace(10,10,1),
#                                                 np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
#                                                 qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
#        ro.measure()
#        plt.figure('amp%s'%(figure_name))
#        plt.plot(ro.freqs,ro.ampdata[0],label = 'qubit 1 in e')
#        plt.figure('phase%s'%(figure_name))
#        plt.plot(ro.freqs,ro.phasedata[0],label = 'qubit 1 in e')
#        
#        ro = rocavspectroscopy_keysight_mixer.ROCavSpectroscopy_keysight_mixer(qubit2_info, mixer_info1, mixer_info2, np.linspace(10,10,1),
#                                                 np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
#                                                 qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
#        ro.measure()
#        plt.figure('amp%s'%(figure_name))
#        plt.plot(ro.freqs,ro.ampdata[0],label = 'qubit 2 in e')
#        plt.legend()
#        plt.figure('phase%s'%(figure_name))
#        plt.plot(ro.freqs,ro.phasedata[0],label = 'qubit 2 in e')
#        plt.legend()

    ro_freq = 10.8247e9
    power = 10
    readout_info.rfsource1.set_frequency(ro_freq - mixer_info1.deltaf)
    readout_info.rfsource1.set_power(power)
    readout_info.rfsource1.set_rf_on(True)
    readout_info.rfsource2.set_power(10)
    readout_info.rfsource2.set_rf_on(True)
    readout_info.rfsource2.set_frequency(ro_freq+50e6)
    bla

if 0: # cav transmission with fwm

    from single_cavity import rocavityspectroscopyfwm_keysight

    rofreq = 10.81e9
    freq_range = 5e6
    dig.do_set_naverages(500000)

    ro = rocavityspectroscopyfwm_keysight.ROCavSpectroscopyfwm_keysight(fwm_info2, np.linspace(-30,0, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
    ro.measure()
#    
#    plt.close()
#    plt.close()
#
    figure_name = 'Cavity Transmission fwm .028T'
#    
    plt.figure('amp%s'%(figure_name))
    plt.plot(ro.freqs,ro.ampdata[0],label = 'with fwm')
    plt.figure('phase%s'%(figure_name))
    plt.plot(ro.freqs,ro.phasedata[0],label = 'with fwm')

    ro = rocavityspectroscopyfwm_keysight.ROCavSpectroscopyfwm_keysight(fwm_info2, np.linspace(-30,0, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                             qubit_pulse=False, seq=None)#,extra_info=[ef2_info])
    ro.measure()  
    
    plt.figure('amp%s'%(figure_name))
    plt.plot(ro.freqs,ro.ampdata[0],label = 'without fwm')
    plt.legend()
    fn = os.path.join(r'C:\_Data', 'images/%s_amp%s.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),figure_name))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    plt.savefig(fn, **kwargs)
    
    plt.figure('phase%s'%(figure_name))
    plt.plot(ro.freqs,ro.phasedata[0],label = 'without fwm')
    plt.legend()
    fn = os.path.join(r'C:\_Data', 'images/%s_phase%s.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),figure_name))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    plt.savefig(fn, **kwargs)   

    ro_freq = 10.81e9
    power = 10
    readout_info.rfsource1.set_frequency(ro_freq)
    readout_info.rfsource1.set_power(power)
    readout_info.rfsource2.set_frequency(ro_freq+50e6)
    bla
    
    
    
if 0:  #cavity time rabi     #not finished yet
    ro_freq = 10.808e9
    readout_info.rfsource1.set_frequency(ro_freq)
    readout_info.rfsource2.set_frequency(ro_freq+50e6)
    from single_qubit import cavtimerabi
    ctr = cavtimerabi.CavTimeRabi(fwm_channal = '8m1', fwm_amp = 0.7, times = np.linspace(1,401,101), power = -30, seq = None)
    ctr.measure_keysight()
    
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
    spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['SS_drive'], qubit_info,
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
        spec = ssbspec.SSBSpec(qubit2_info, np.linspace(-5e6, 5e6, 101), seq=seq, plot_seqs=False, proj_func='phase')
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
        spec = ssbspec_mixer.SSBSpec_mixer(qubit2_info, mixer_info1,mixer_info2, np.linspace(-10e6, 10e6, 101), seq=seq, 
                                           plot_seqs=False, proj_func='phase')
        spec.measure_keysight()
#        plt.close()
    bla
    
if 0: # ef SSB spec with mixer
    from single_qubit import ssbspec_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    for i in range(1):        
#        RObrick.do_set_power(i)
#        postseq = qubit2_info.rotate(np.pi,0)
        postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
#        seq = sequencer.Trigger(600)
        seq = sequencer.Join([sequencer.Trigger(600), qubit2_info.rotate(np.pi,0)])
        spec = ssbspec_mixer.SSBSpec_mixer(ef2_info, mixer_info1,mixer_info2, np.linspace(-10e6, 10e6, 101), seq=seq,postseq = postseq,
                                           plot_seqs=False, proj_func='phase',extra_info=qubit2_info)
        spec.measure_keysight()
#        plt.close()
    bla
    
if 0: # SSB spec with lorentzian fit
    from single_qubit import ssbspec_lorentzianfit
    seq = sequencer.Trigger(600)
    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info,np.linspace(-5e6,5e6, 3), seq=seq, plot_seqs=True, proj_func='phase')
    spec.measure_keysight()
    center = spec.center
    height = spec.height
    width = spec.width
    bla

if 0: #ssb with stark shift with mixer with gaussian fit
    from single_qubit import stark_shift_with_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    phase1 =0
#    SS_mixer_info1_set.set_deltaf(-94.28e6)
#    SS_mixer_info2_set.set_deltaf(-94.28e6)

#    SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
#    SS_mixer_info2 = mclient.get_qubit_info('SS_mixer_info2')
#    phase = np.linspace(0,2*3.141,11)
#    delays = np.linspace(1,100,5)
    phase = [0]
#    delays = [1]
    pi_amps = np.linspace(0.3,0.7,1)
    shifts = np.zeros([len(pi_amps),len(phase)])
    widths = np.zeros([len(pi_amps),len(phase)])
    for j in range(len(pi_amps)):
        SS_mixer_info1_set.set_pi_amp(pi_amps[j])

        SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
#    for j in range(len(delays)):
        for i in range(len(phase)):        
    #        RObrick.do_set_power(i)
            seq = sequencer.Trigger(600)
#            seq_in = sequencer.Trigger(600)
#            seq = sequencer.Join([seq_in, SS_mixer_info1.rotate(np.pi, phase1 + phase[i]), sequencer.Delay(delays[j])])
            post_seq = sequencer.Delay(500)
            spec = stark_shift_with_mixer.Stark_shift_with_mixer(qubit2_info, mixer_info1,mixer_info2, SS_mixer_info1, SS_mixer_info2,
                                                                 phase1, np.linspace(-20e6, 10e6,101), seq=seq, plot_seqs=False, postseq = post_seq,
                                                                 proj_func='phase')
            spec.measure_keysight()
    #        plt.close()
            shift = spec.fit_params['freq'].value
            shifts[j][i] = shift
            width = spec.fit_params['kappa'].value
            widths[j][i] = width
    if len(pi_amps) > 1:
        
        plt.figure()
        plt.plot(pi_amps, shifts.transpose()[0], label = 'freq')
        plt.plot(pi_amps, widths.transpose()[0], label = 'FWHM')
        plt.legend()
        plt.xlabel('cav disp pi amp')
        
        plt.figure()
        plt.plot(shifts.transpose()[0], widths.transpose()[0])
        plt.legend()
        plt.xlabel('freq') 
        plt.ylabel('FWHM')
    
    
    bla
    
if 0: #ssb with cw stark shift with mixer with gaussian fit
    from single_qubit import cw_stark_shift_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    phase1 =0
#    SS_mixer_info1_set.set_deltaf(-94.28e6)
#    SS_mixer_info2_set.set_deltaf(-94.28e6)

#    SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
#    SS_mixer_info2 = mclient.get_qubit_info('SS_mixer_info2')
#    phase = np.linspace(0,2*3.141,11)
#    delays = np.linspace(1,100,5)
    repeat = 1
#    delays = [1]
    pi_amps =np.linspace(0,0.05,6)
#    pi_amps = [0,0.03,0.06, 0.1,0.11,0.12,0.13]
#    pi_amps = np.asarray(pi_amps)
    shifts = np.zeros([len(pi_amps),repeat])
    widths = np.zeros([len(pi_amps),repeat])
    for j in range(len(pi_amps)):
        SS_mixer_info1_set.set_pi_amp(pi_amps[j])

        SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
#    for j in range(len(delays)):
        for i in range(repeat):        
    #        RObrick.do_set_power(i)
            seq = sequencer.Trigger(600)
#            seq_in = sequencer.Trigger(600)
#            seq = sequencer.Join([seq_in, SS_mixer_info1.rotate(np.pi, phase1 + phase[i]), sequencer.Delay(delays[j])])
            post_seq = sequencer.Delay(500)
            spec = cw_stark_shift_mixer.CW_Stark_shift_with_mixer(qubit2_info, mixer_info1,mixer_info2, SS_mixer_info1,
                                                                 phase1, np.linspace(-20e6, 10e6,101), seq=seq, plot_seqs=False, postseq = post_seq,
                                                                 proj_func='phase')
            spec.measure_keysight()
    #        plt.close()
            shift = spec.fit_params['freq'].value
            shifts[j][i] = shift
            width = spec.fit_params['kappa'].value
            widths[j][i] = width
    if len(pi_amps) > 1:
        
        plt.figure()
        plt.plot(pi_amps, shifts.transpose()[0], label = 'freq')
        plt.plot(pi_amps, widths.transpose()[0], label = 'FWHM')
        plt.legend()
        plt.xlabel('cav disp pi amp')
        
        plt.figure()
        plt.plot(shifts.transpose()[0], widths.transpose()[0])
        plt.legend()
        plt.xlabel('freq') 
        plt.ylabel('FWHM')
    if repeat > 1:
        plt.figure()
        plt.plot(shifts[0], label = 'freq')
        plt.plot(widths[0], label = 'FWHM')
        plt.legend()
        plt.xlabel('# of repetition')
    
    
    bla
    
if 0: # SSB spec with gaussian fit
    from single_qubit import ssbspec_gaussianfit
    seq = sequencer.Trigger(600)
    spec = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit2_info, np.linspace(-10e6, 10e6, 101), seq=seq, plot_seqs=True, proj_func='phase')
    spec.measure_keysight()
#    fit_freq=spec.center
#    deltaf_1 = ef2_info_set.get_deltaf()
#    ef2_info_set.set_deltaf(deltaf_1+fit_freq*1e6)
    bla
if 0: # SSB spec with Stark Shift tone with gaussian fit
    from single_qubit import ssbspec_gaussianfit_SS
#    seq = sequencer.Trigger(600)
#    from single_qubit import ssbspec_lorentzianfit
#    seq = sequencer.Sequence([sequencer.Trigger(400), qubit2_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
#    postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
    spec = ssbspec_gaussianfit_SS.SSBSpec_Gaussianfit_SS(qubit2_info, np.linspace(-20e6, 2e6, 81),amp = 1,channel = '8m1', seq=None,postseq=None, plot_seqs=False, proj_func='phase',extra_info=qubit2_info)
    spec.measure_keysight()
    
    bla

if 0: # SSB spec with Stark Shift tone with gaussian fit for multiple amps and frequencies
    frequencies = [5.602e9]
    amps = [.1]
#    frequencies = [5.487e9]
#    amps = [.15]
    stark_shifts = []

    for i in range(len(amps)):
        print(amps[i])
        fwm_gen2.do_set_frequency(frequencies[i])
        from single_qubit import ssbspec_gaussianfit_SS
    #    seq = sequencer.Trigger(600)
    #    from single_qubit import ssbspec_lorentzianfit
#        seq = sequencer.Sequence([sequencer.Trigger(400), qubit2_info.rotate(np.pi, 0)])
    #    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
#        postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
        spec = ssbspec_gaussianfit_SS.SSBSpec_Gaussianfit_SS(qubit2_info, np.linspace(-5e6, 2e6, 81),amp = amps[i],channel = '8m1', seq=None,postseq=None, plot_seqs=False, proj_func='phase')#,extra_info=qubit2_info)
        spec.measure_keysight()
        stark_shifts.append(spec.fit_params['freq'].value)
    plt.figure()
    plt.plot(amps,stark_shifts)
    bla

if 0: # ef SSB spec with Stark Shift tone with gaussian fit
    from single_qubit import ssbspec_gaussianfit_SS
#    seq = sequencer.Trigger(600)
#    from single_qubit import ssbspec_lorentzianfit
    seq = sequencer.Sequence([sequencer.Trigger(400), qubit2_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
    postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
    spec = ssbspec_gaussianfit_SS.SSBSpec_Gaussianfit_SS(ef2_info, np.linspace(-20e6, 2e6, 81), seq=seq,postseq=postseq, plot_seqs=False, proj_func='phase',extra_info=qubit2_info)
    spec.measure_keysight()
    
    bla


if 0: # SSB spec with Stark Shift tone with gaussian fit with fwm
    from single_qubit import ssbspec_gaussianfit_SS_fwm
#    seq = sequencer.Trigger(600)
#    from single_qubit import ssbspec_lorentzianfit
#    seq = sequencer.Sequence([sequencer.Trigger(400), qubit2_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
#    postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
    spec = ssbspec_gaussianfit_SS_fwm.SSBSpec_Gaussianfit_SS_fwm(qubit2_info,fwm_info2, np.linspace(-60e6, 5e6, 161), seq=None,postseq=None, plot_seqs=False, proj_func='phase')#,extra_info=qubit2_info)
    spec.measure_keysight()
    
    bla

  
if 0: # ef SSB spec with Stark Shift tone with gaussian fit with fwm
    from single_qubit import ssbspec_gaussianfit_SS_fwm
#    seq = sequencer.Trigger(600)
#    from single_qubit import ssbspec_lorentzianfit
    seq = sequencer.Sequence([sequencer.Trigger(400), qubit2_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
    postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
    spec = ssbspec_gaussianfit_SS_fwm.SSBSpec_Gaussianfit_SS_fwm(ef2_info,fwm_info2, np.linspace(-20e6, 5e6, 81), seq=seq,postseq=postseq, plot_seqs=True, proj_func='phase',extra_info=qubit2_info)
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

    from single_qubit import rabi
    import time
    update_proj =False
#    seq = sequencer.Sequence([sequencer.Trigger(400)])
#    seq = sequencer.Sequence([sequencer.Trigger(400), qubit_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
#    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    tr = rabi.Rabi(qubit2_info, 
#                               np.linspace(-0.4, 0.4, 81), selective=False,
#                               np.linspace(-0.5, 0.5, 81), selective=False,
                               np.linspace(-0.035, 0.035, 81), selective=True,
#                               np.linspace(-0.03, 0.03, 81), selective=True,
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

if 0: # Power Rabi-Calibrate pi pulse with mixer

#    for cool_time in [1e3,5e3,10e3,30e3]:
#        for amp in [0.01, 0.01,0.02,0.04,0.08]:
#    cool = sequencer.Combined([sequencer.Constant(int(cool_time), amp, chan=ef_info.sideband_channels[0]),
#                                   sequencer.Constant(int(cool_time), amp, chan=ef_info.sideband_channels[1]),
#                                   sequencer.Constant(int(cool_time), 1, chan='3m1')])

    from single_qubit import rabi_mixer
    import time
    update_proj =False
    seq = sequencer.Sequence([sequencer.Trigger(400),sequencer.Delay(10)])
#    seq = sequencer.Sequence([sequencer.Trigger(400), qubit_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
#    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    tr = rabi_mixer.Rabi_mixer(qubit2_info, mixer_info1, mixer_info2,
#                               np.linspace(-0.9, 0.9, 81), selective=False,
                               np.linspace(-0.7, 0.7, 81), selective=False,
#                               np.linspace(-0.14, 0.14, 81), selective=True,
#                               np.linspace(-0.1, 0.1, 81), selective=True,
        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                               plot_seqs=False, generate=True, repeat_pulse=1, seq=seq,#postseq = postseq, fix_period = 0.38087745,
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

if 0: # rabi chi measurement
#    center_freqs = [10821987317.5250282,10821561320.7751045, 10820506643.1310101, 10819140331.8051739, 10817684262.6574841, 10816317541.1851597, 10815768598.7954025, 10815491607.2699833, 10815290606.1706429, 10815078431.6681404, 10814980627.0180206, 10814834099.9847260, 10814672730.2043896, 10814603950.5431747, 10814701809.3316956, 10814456968.1978436, 10814435657.6104870, 10814405500.8025951, 10814286241.7800770, 10814246719.1344051, 10814264647.1138535, 10814124216.6995411, 10814188799.6116619, 10814088084.9055729, 10814035667.3182030, 10814023859.4588299]
#    fields = np.linspace(0,.05,26)
    center_freqs = [10.830e9]
    fields = [0]
    for j in range(len(fields)):
#        Magnet.do_set_PSwitch(1)
#        print('heating PSwitch')
#        time.sleep(35)
##    #            
#        Magnet.do_set_field(fields[j])
#        print('setting field')
#        time.sleep(120)
#        Magnet.do_set_PSwitch(0)
#        print('cooling PSwitch')
#        time.sleep(350)    
        freq_range = 10e6
        ro_center = center_freqs[j]
        ro_freq = np.linspace(ro_center-freq_range,ro_center+freq_range,1)
        power = 10
    
        init_point = []
        final_point = []
        init_point2 = []

        for i in range(len(ro_freq)):
            readout_info.rfsource1.set_frequency(ro_freq[i])
#            readout_info.rfsource1.set_power(power)
            readout_info.rfsource2.set_frequency(ro_freq[i]+50e6)
            time.sleep(.1)
            from single_qubit import rabi_with_mixer
#            import time
            update_proj =False
        #    seq = sequencer.Sequence([sequencer.Trigger(400)])
        #    seq = sequencer.Sequence([sequencer.Trigger(400), qubit_info.rotate(np.pi, 0)])
        #    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
        #    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
        #    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
            tr = rabi_with_mixer.Rabi_mixer(qubit2_info, 
#                                       np.linspace(-0.7, 0.7, 81), ch = '7m1', mixer_amp = .2,selective=False,
        #                               np.linspace(-0.5, 0.5, 81), selective=False,
#                                       np.linspace(0, qubit2_info.pi_amp, 2), ch = '7m1', mixer_amp = .2, selective=False,
                                        np.array([0,0.001,qubit2_info.pi_amp]), mixer_info1 , selective=False,
        #                               np.linspace(-0.03, 0.03, 81), selective=True,
                #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                                       plot_seqs=True, generate=True, repeat_pulse=1,# seq=seq,postseq = postseq, fix_period = 0.38087745,
                                       update=False, #extra_info=[qubit_info],
                                       proj_func='phase')
            tr.measure_keysight()
            init_point.append(tr.pp_data[0])
            final_point.append(tr.pp_data[-1])
            init_point2.append(tr.pp_data[1])
            plt.close()
        chi = -(np.array(final_point)-np.array(init_point))
        chi2 = -(np.array(final_point)-np.array(init_point2))
        plt.figure()
        plt.title('Chi at %s T'%fields[j])
        
        plt.plot(ro_freq,chi)
        plt.plot(ro_freq,chi2)
        fn = os.path.join(r'C:\_Data', 'images/%s_phase%sT.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),fields[j]))
        fdir = os.path.split(fn)[0]
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        kwargs = dict()
        plt.savefig(fn, **kwargs)
    bla

if 0: # ef Power Rabi-Calibrate pi pulse

#    for cool_time in [1e3,5e3,10e3,30e3]:
#        for amp in [0.01, 0.01,0.02,0.04,0.08]:
#    cool = sequencer.Combined([sequencer.Constant(int(cool_time), amp, chan=ef_info.sideband_channels[0]),
#                                   sequencer.Constant(int(cool_time), amp, chan=ef_info.sideband_channels[1]),
#                                   sequencer.Constant(int(cool_time), 1, chan='3m1')])
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
    postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
    from single_qubit import rabi
    import time
    update_proj =False
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    tr = rabi.Rabi(ef2_info, 
                               np.linspace(-0.6, 0.6, 81), selective=False,
#                               np.linspace(-0.7, 0.7, 81), selective=False,
#                               np.linspace(-0.1, 0.1, 81), selective=True,
#                               np.linspace(-0.3, 0.3, 81), selective=True,
        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                               plot_seqs=False, generate=True, repeat_pulse=1, seq=seq,postseq = postseq,
                               update=True, extra_info=qubit2_info,
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
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
    postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
    seq = sequencer.Sequence([sequencer.Trigger(250)])

    from single_qubit import rabi_mixer
    import time
    update_proj =False
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    tr = rabi_mixer.Rabi_mixer(ef2_info, mixer_info1,mixer_info2,
#                               np.linspace(-0.3, 0.3, 81), selective=False,
                               np.linspace(-0.7, 0.7, 81), selective=False,
#                               np.linspace(-0.015, 0.015, 81), selective=True,
#                               np.linspace(-0.3, 0.3, 81), selective=True,
        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                               plot_seqs=False, generate=True, repeat_pulse=1, seq=seq,postseq = postseq,fix_period = 1.0574,
                               update=False, extra_info=qubit2_info,
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
                                         np.linspace(0e3, 30e3, 11),
#                                         np.concatenate((np.linspace(5e3, 5e3, 50), np.linspace(6e3, 6e3, 51))),
                                         double_exp=False, generate=True, plot_seqs=False, proj_func='phase', seq=None)    
    t1.measure_keysight()
    bla

if 0: # T1 mixer

    from single_qubit import T1measurement_mixer

#    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 250e3, 121), 
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(2000, 1, chan='3m1'), sequencer.Delay(250),
#                          ef_info.rotate(np.pi, 0), sequencer.Constant(4000, 1, chan='3m1'), sequencer.Delay(250)])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])

    t1 = T1measurement_mixer.T1Measurement_mixer(qubit2_info, mixer_info1,mixer_info2, #np.linspace(0, 500e3, 101),
                                         np.linspace(0.1e3, 30e3, 101),
#                                         np.concatenate((np.linspace(5e3, 5e3, 50), np.linspace(6e3, 6e3, 51))),
                                         double_exp=False, generate=True, plot_seqs=False, proj_func='phase', seq=None)    
    t1.measure_keysight()
    bla
    
    
    
if 0: # cavity T1 mixer

    from single_cavity import cavT1_mixer

#    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 250e3, 121), 
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(2000, 1, chan='3m1'), sequencer.Delay(250),
#                          ef_info.rotate(np.pi, 0), sequencer.Constant(4000, 1, chan='3m1'), sequencer.Delay(250)])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])

    t1 = cavT1_mixer.CavT1_Mixer(qubit_info, SS_mixer_info1, mixer_info1, mixer_info2, np.pi, #np.linspace(0, 500e3, 101),
                                         np.linspace(0e3, .5e3, 101), 0,
#                                         np.concatenate((np.linspace(5e3, 5e3, 50), np.linspace(6e3, 6e3, 51))),
                                         plot_seqs=False, proj_func='phase', seq=None)    
    t1.measure_keysight()
    bla
    #(self, qubit_info, cav_info, mixer_info, mixer_info2, disp, delays, proj_num, seq=None, postseq=None, extra_info=None, bgcor=False,
 #                force_a0 = False, **kwargs):
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
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 2e3, 101), detune=4e6, double_freq=False, generate=True, 
                                         seq=None, postseq=None, proj_func='phase') #extra_info=[qubit2_info])
#        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')

        
        t2.measure_keysight()
    bla

if 1: #T2 mixer
    from single_qubit import T2measurement_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
    for i in range(1):
        t2 = T2measurement_mixer.T2Measurement_mixer(qubit2_info, mixer_info1, mixer_info2, np.linspace(0, 4e3, 101), 
                                                     detune=2e6, double_freq=False, generate=True, #echotype = 'HANN',
                                                     seq=None, postseq=None, proj_func='phase') #extra_info=[qubit2_info])
#        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')

        
        t2.measure_keysight()
    bla
if 0: #ramsey mixer
    from single_qubit import ramsey_measurement
#    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
    post_seq = sequencer.Delay(500)
#    A_E = []
#    A = []
    field = 0
    pi_amps = np.linspace(0.3, 0.3,1)
    repeat = 10
    df_i = np.zeros([len(pi_amps),repeat])
    df_f = np.zeros([len(pi_amps),repeat])
    df_ave = np.zeros([len(pi_amps),repeat])
    tau_i = np.zeros([len(pi_amps),repeat])
    tau_f = np.zeros([len(pi_amps),repeat])
    tau_ave = np.zeros([len(pi_amps),repeat])
    
    for i in range(len(pi_amps)):
        SS_mixer_info1_set.set_pi_amp(pi_amps[i])

        SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
        
        for j in range(repeat):
            
       
#            t2 = ramsey_measurement.Ramsey_Measurement_mixer(qubit2_info, SS_mixer_info1, mixer_info1,mixer_info2, 
#                                                         np.linspace(0, 0.12e3, 121), detune=80e6, echotype = 'HANN', 
#                                                         necho = 1, double_freq=False, generate=True, 
#                                                         seq=None, postseq=post_seq, proj_func='phase', plot_seqs = False) #extra_info=[qubit2_info])
#            t2.measure_keysight()
#            A_E.append(t2.fit_params)
            t2 = ramsey_measurement.Ramsey_Measurement_mixer(qubit2_info, SS_mixer_info1, mixer_info1,mixer_info2, 
                                                         np.linspace(0, 0.24e3, 121), detune=40e6,  
                                                         double_freq=False, generate=True, 
                                                         seq=None, postseq=post_seq, proj_func='phase', plot_seqs = False) #extra_info=[qubit2_info])

            t2.measure_keysight()
#            A.append(t2.fit_params)
            xs = t2.delays
            df_i[i][j] = t2.fit_params['freq'].value*1e6 + t2.fit_params['A']*1e6*np.exp(-xs[0]*t2.fit_params['slope'])
            df_f[i][j] = t2.fit_params['freq'].value*1e6 + t2.fit_params['A']*1e6*np.exp(-xs[-1]*t2.fit_params['slope'])
            df_ave[i][j] = np.average(t2.fit_params['freq'].value*1e6 + t2.fit_params['A']*1e6*np.exp(-xs*t2.fit_params['slope']))
            tau_i[i][j] = 0.001/((1/t2.fit_params['tau'].value) + t2.fit_params['A2'].value*np.exp(-xs[0]*t2.fit_params['slope'].value/2))
            tau_f[i][j] = 0.001/((1/t2.fit_params['tau'].value) + t2.fit_params['A2'].value*np.exp(-xs[-1]*t2.fit_params['slope'].value/2))
            tau_ave[i][j] = 0.001/np.average((1/t2.fit_params['tau'].value) + t2.fit_params['A2'].value*np.exp(-xs*t2.fit_params['slope'].value/2))
            if len(pi_amps) * repeat >5:
                plt.close()
        if repeat >1:
            plt.figure()
            plt.title('pi_amp = %s'%(pi_amps[i]))
            plt.plot(df_i[i], label = ' df_initial, ave freq = %.3f +/- %.3f kHz'%(
                    np.average(df_i[i]), np.std(df_i[i])/np.sqrt(len(df_i[i]))))
            plt.plot(df_f[i], label = ' df_final, ave freq = %.3f +/- %.3f kHz'%(
                    np.average(df_f[i]), np.std(df_f[i])/np.sqrt(len(df_f[i]))))
            plt.plot(df_ave[i], label = ' df_average, ave freq = %.3f +/- %.3f kHz'%(
                    np.average(df_ave[i]), np.std(df_ave[i])/np.sqrt(len(df_ave[i]))))
            plt.legend()

            plt.figure()
            plt.title('pi_amp = %s'%(pi_amps[i]))
            plt.plot(tau_i[i], label = ' tau_initial, ave tau = %.3f +/- %.3f us'%(
                    np.average(tau_i[i]), np.std(tau_i[i])/np.sqrt(len(tau_i[i]))))
            plt.plot(tau_f[i], label = ' tau_final, ave tau = %.3f +/- %.3f us'%(
                    np.average(tau_f[i]), np.std(tau_f[i])/np.sqrt(len(tau_f[i]))))
            plt.plot(tau_ave[i], label = ' tau_average, ave tau = %.3f +/- %.3f us'%(
                    np.average(tau_ave[i]), np.std(tau_ave[i])/np.sqrt(len(tau_ave[i]))))
            plt.legend()

    if len(pi_amps) > 1:

        plt.figure()
        plt.title('field = %s'%(field))#%(points[u]))
        plt.plot(pi_amps,np.mean(df_i, axis = 1),label = 'df_initial')
        plt.plot(pi_amps,np.mean(df_f, axis = 1),label = 'df_final')
        plt.plot(pi_amps,np.mean(df_ave, axis = 1),label = 'df_average')
        plt.legend()   
        plt.figure()
        plt.title('field = %s'%(field))#%(points[u]))
        plt.plot(pi_amps,np.mean(tau_i, axis = 1),label = 'tau_initial')
        plt.plot(pi_amps,np.mean(tau_f, axis = 1),label = 'tau_final')
        plt.plot(pi_amps,np.mean(tau_ave, axis = 1),label = 'tau_average')
        plt.legend() 
#    slope = []
##    slope_E = []
#    tau = []
##    tau_E = []
#    A2 = []    
##    A2_E = []
#    for i in range(len(A)):
#        slope.append(A[i]['slope'].value)
##        slope_E.append( A_E[i]['slope'].value)
#        tau.append(A[i]['tau'].value)
##        tau_E.append(A_E[i]['tau'].value)
#        A2.append(A[i]['A2'].value)
##        A2_E.append(A_E[i]['A2'].value)


    bla
    
if 0: # cw ramsey mixer
    from single_qubit import cw_ramsey_mixer
    field = 0.26
    pi_amps = [0.03]
    repeat = 10
    df = np.zeros([len(pi_amps),repeat])
    tau = np.zeros([len(pi_amps),repeat])
    for i in range(len(pi_amps)):
        SS_mixer_info1_set.set_pi_amp(pi_amps[i])

        SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
        
        
        for j in range(repeat):
            t2 = cw_ramsey_mixer.CW_Ramsey_Mixer(qubit2_info,  SS_mixer_info1, mixer_info1,mixer_info2, 
                                                         np.linspace(0, 0.5e3, 101), detune = 20e6, 
                                                         generate=True, fix_phi0 =None,qubit_pulse = False,double_freq = False,
                                                         seq=None, postseq=None, proj_func='amplitude', plot_seqs =False) #extra_info=[qubit2_info])
            t2.measure_keysight() 

            df[i][j] = t2.fit_params[2]['freq'].value*1e6 

            tau[i][j] =(t2.fit_params[2]['tau'].value)/1000
            if len(pi_amps) * repeat >5:
                plt.close()
        if repeat >1:
            plt.figure()
            plt.title('pi_amp = %s'%(pi_amps[i]))
            plt.plot(df[i], label = ' df, ave freq = %.3f +/- %.3f kHz'%(
                    np.average(df[i]), np.std(df[i])/np.sqrt(len(df[i]))))
            plt.legend()

            plt.figure()
            plt.title('pi_amp = %s'%(pi_amps[i]))
            plt.plot(tau[i], label = ' tau, ave tau = %.3f +/- %.3f us'%(
                    np.average(tau[i]), np.std(tau[i])/np.sqrt(len(tau[i]))))

            plt.legend()

    if len(pi_amps) > 1:

        plt.figure()
        plt.title('field = %s'%(field))#%(points[u]))
        plt.plot(pi_amps,np.mean(df, axis = 1),label = 'df')
        plt.legend()   
        plt.figure()
        plt.title('field = %s'%(field))#%(points[u]))
        plt.plot(pi_amps,np.mean(tau, axis = 1),label = 'tau')
        plt.legend() 
    bla
if 0: #ramsey mixer for photon
    from single_qubit import photon_ramsey_measurement
#    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
    Delays = [300]
    repeat = 1
    freq_q = np.zeros([len(Delays),repeat])
    freq = np.zeros([len(Delays),repeat])
    for idelay, delay in enumerate(Delays):
        for i in range(repeat):
            t2 = photon_ramsey_measurement.Photon_Ramsey_Measurement_mixer(qubit_info, qubit2_info, SS_mixer_info1, mixer_info1,mixer_info2, 
                                                             np.linspace(0,.1e3,101), detune=60e6, fix_phi0 = -1.8, delay = delay , qubit_pulse = True, double_freq=False, generate=True, 
                                                             seq=None, postseq=None, proj_func='phase', plot_seqs =False) #extra_info=[qubit2_info])
            t2.measure_keysight()
            freq_q[idelay][i] = t2.fit_params['freq'].value
            t2 = photon_ramsey_measurement.Photon_Ramsey_Measurement_mixer(qubit_info, qubit2_info, SS_mixer_info1, mixer_info1,mixer_info2, 
                                                             np.linspace(0,.1e3,101), detune=60e6, fix_phi0 = -1.8, delay = delay, qubit_pulse = False, double_freq=False, generate=True, 
                                                             seq=None, postseq=None, proj_func='phase', plot_seqs =False) #extra_info=[qubit2_info])
            
            t2.measure_keysight()
            freq[idelay][i] = t2.fit_params['freq'].value
#            plt.close()
#            plt.close()
#            
        plt.figure()
        plt.plot(np.asarray(freq_q[idelay])*1000,label = 'with qubit, delay = %s, ave_freq = %s +/- %s MHz'%(
                delay, np.average(freq_q[idelay]*1000), np.std(freq_q[idelay]*1000)/np.sqrt(repeat)))
        plt.plot(np.asarray(freq[idelay])*1000,label = 'without qubit, delay = %s, ave_freq = %s +/- %s MHz'%(
                delay, np.average(freq[idelay]*1000), np.std(freq[idelay]*1000)/np.sqrt(repeat)))
                
        plt.ylabel('MHz')
        plt.legend()
    bla
    
if 0: #photon ramsey mixer test
    from single_qubit import photon_ramsey_test
#    delay = np.linspace(130,260,6)
    
    delay = [100]
    points = [101]
    repeat = 1
    seq_num = 3
    data = np.zeros([len(points),len(delay),seq_num])
    data_q = np.zeros([len(points),len(delay),seq_num])
    labels = ['phase 0','phase pi','averages phase']
#    freq = np.zeros([4,repeat])
    for k in range(len(points)):
        for j in range(len(delay)): 
            freq = np.zeros([seq_num,repeat])
            freq_q = np.zeros([seq_num,repeat])
            for i in range(repeat):
                t2 = photon_ramsey_test.Photon_Ramsey_Test(qubit_info, qubit2_info, SS_mixer_info1, mixer_info1,mixer_info2, 
                                                                 np.linspace(0, 0.002e3*(points[k]-1),points[k]), detune=40e6, 
                                                                 delay = delay[j], generate=True, fix_phi0 = -1.7,qubit_pulse = False,
                                                                 seq=None, postseq=None, proj_func='phase', plot_seqs =False) #extra_info=[qubit2_info])
                t2.measure_keysight()
                if repeat * len(delay)* len(points) >5:
                    
                    plt.close()
                for m in range(seq_num):
                    freq[m][i] = t2.fit_params[m]['freq'].value
                t2 = photon_ramsey_test.Photon_Ramsey_Test(qubit_info, qubit2_info, SS_mixer_info1, mixer_info1,mixer_info2, 
                                                                 np.linspace(0, 0.002e3*(points[k]-1),points[k]), detune=40e6, 
                                                                 delay = delay[j], generate=True, fix_phi0 = -1.7,qubit_pulse = True,
                                                                 seq=None, postseq=None, proj_func='phase', plot_seqs =False) #extra_info=[qubit2_info])
                t2.measure_keysight()
                if repeat * len(delay)* len(points) >5:
                    
                    plt.close()
                for m in range(seq_num):
                    freq_q[m][i] = t2.fit_params[m]['freq'].value
#            labels = ['without qubit','without qubit, delay %s'%(delay[j]), 'with qubit','with qubit, delay %s'%(delay[j])]
#            labels = ['without qubit, delay %s'%(delay[j]),'with qubit, delay %s'%(delay[j])]
        #    labels = ['without qubit, delay %s'%(delay),'without qubit', 'with qubit','with qubit, delay %s'%(delay)]
        #    labels = ['without qubit', 'with qubit','without qubit, delay %s'%(delay),'with qubit, delay %s'%(delay)]
        #    labels = ['with qubit', 'without qubit','with qubit, delay %s'%(delay),'without qubit, delay %s'%(delay)]
            if repeat >1:
                plt.figure()
                plt.title('delay = %s, points = %s'%(delay[j],points[k]))
                for l in range(seq_num):
                    plt.plot(freq[l]*1000, label = labels[l] + ' w/o qubit, ave freq = %.3f +/- %.3f MHz'%(
                            np.average(freq[l]*1000), np.std(freq[l])/np.sqrt(len(freq[l]))*1000))
                    plt.plot(freq_q[l]*1000, label = labels[l] + ' w/ qubit, ave freq = %.3f +/- %.3f MHz'%(
                            np.average(freq_q[l]*1000), np.std(freq_q[l])/np.sqrt(len(freq_q[l]))*1000))
                plt.legend()
#                plt.figure()
#                plt.title('freq_shifts, delay = %s, points = %s'%(delay[j],points[k]))
#                for l in range(4):
#                    plt.plot(freq[l]*1000 - freq[0] * 1000, label = labels[l])
#                plt.legend()
            for p in range(seq_num):
                data[k][j][p]=np.average(freq[p])
                data_q[k][j][p]=np.average(freq_q[p])
    if len(points) > 1:
        
        for u in range(len(delay)):
#            labels_ = ['without qubit','without qubit, delay', 'with qubit','with qubit, delay']
#            labels_ = ['without qubit, delay','with qubit, delay']
            plt.figure()
            plt.title('delay = %s'%(delay[u]))#%(points[u]))
            for t in range(seq_num):
                plt.plot(points,data.transpose()[t][0],label = labels[t]+' w/o qubit')
                plt.plot(points,data_p.transpose()[t][0],label = labels[t]+ ' w/ qubit')
            plt.legend()
    if len(delay) > 1:
        
        for u in range(len(points)):
#            labels_ = ['without qubit','without qubit, delay', 'with qubit','with qubit, delay']
#            labels_ = ['without qubit, delay','with qubit, delay']
            plt.figure()
            plt.title('pts = %s'%(points[u]))
            for t in range(seq_num):
                plt.plot(delay,data[u].transpose()[t],label = labels[t] + ' w/o qubit')
                plt.plot(delay,data_p[u].transpose()[t],label = labels[t]+' w/ qubit')
            plt.legend() 
            
    bla
    #(self, qubit_info1,qubit_info2, SS_mixer_info1, mixer_info1,mixer_info2, delays, detune=0, qubit_pulse=False,
#                 double_freq=False, seq=None, postseq=None, selective=True, Qswitch_infoA=None, Qswitch_infoB=None, **kwargs):
    
    
if 0:
    points = [151]
    repeat = 1
    from single_qubit import photon_ramsey_test_2
    for k in range(len(points)):
        for i in range(repeat):
            t2 = photon_ramsey_test_2.Photon_Ramsey_Test_2(qubit_info, qubit2_info, SS_mixer_info1, mixer_info1,mixer_info2, 
                                                             np.linspace(0, 0.001e3*(points[k]-1),points[k]), detune=60e6, 
                                                             delay = 300, generate=True, 
                                                             seq=None, postseq=None, proj_func='phase', plot_seqs =False) #extra_info=[qubit2_info])
            t2.measure_keysight()
if 0: # Ramsey qubit 2 rabi sweep
    from single_qubit import T2measurementforramsey
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    amplitudes = np.linspace(-0.2, 0.2, 11)
    detunes = []
    for amplitude in amplitudes:
        t2 = T2measurementforramsey.T2MeasurementforRamsey(qubit_info, qubit2_info, amplitude, 
                                                           np.linspace(0, 0.5e3, 101), detune=20e6, double_freq=False, generate=True, 
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
    t2 = T2measurement.T2Measurement(qubit2_info, np.linspace(0.1, 10e3, 101), detune=1e6, echotype = T2measurement.ECHO_HAHN, necho=1, 
                                     plot_seqs = False, generate=True, proj_func='phase', seq=None)
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
    from single_qubit import ssbspec_lorentzianfit
    seq = sequencer.Sequence([sequencer.Trigger(400), qubit2_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
    postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(ef2_info, np.linspace(-40e6, 20e6, 101), seq=seq, postseq = postseq, extra_info=qubit2_info, plot_seqs=False, generate=True, proj_func='phase')
    spec.measure_keysight()
#    fit_freq=spec.center
#    deltaf_1 = ef2_info_set.get_deltaf()
#    ef2_info_set.set_deltaf(deltaf_1+fit_freq*1e6)
    bla   

if 0: # EF SSBspec mixer
    from single_qubit import ssbspec_lorentzianfit_mixer
    seq = sequencer.Sequence([sequencer.Trigger(400), qubit2_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
    postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    spec = ssbspec_lorentzianfit_mixer.SSBSpec_lorentzianfit_mixer(ef2_info,mixer_info1, mixer_info2, np.linspace(-5e6, 5e6, 101), seq=seq, postseq = postseq, extra_info=qubit2_info, plot_seqs=False, generate=True, proj_func='phase')
    spec.measure_keysight()
#    fit_freq=spec.center
#    deltaf_1 = ef2_info_set.get_deltaf()
#    ef2_info_set.set_deltaf(deltaf_1+fit_freq*1e6)
    bla   
    
    
if 0: # EF SSBspec repeat
    from single_qubit import ssbspec_lorentzianfit
    freq_ge = []   
    freq_ef = []
    for i in range(200):
        from single_qubit import ssbspec_mixer
    
#        postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
#        seq = sequencer.Trigger(600)
#        seq = sequencer.Join([sequencer.Trigger(600), qubit2_info.rotate(np.pi,0)])
        spec = ssbspec_mixer.SSBSpec_mixer(qubit2_info, mixer_info1,mixer_info2, np.linspace(-10e6, 10e6, 101), seq=None,postseq = None,
                                           plot_seqs=False, proj_func='phase')
        spec.measure_keysight()          
        
        freq_ge.append(spec.center)
        plt.close()

        
        postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
#        seq = sequencer.Trigger(600)
        seq = sequencer.Join([sequencer.Trigger(600), qubit2_info.rotate(np.pi,0)])
        spec = ssbspec_mixer.SSBSpec_mixer(ef2_info, mixer_info1,mixer_info2, np.linspace(-10e6, 10e6, 101), seq=seq,postseq = postseq,
                                           plot_seqs=False, proj_func='phase',extra_info=qubit2_info)
        spec.measure_keysight()
        freq_ef.append(spec.center)
        plt.close()
        
    plt.figure()
    plt.plot(range(len(freq_ge)),freq_ge,label = 'ge freq')
    plt.plot(range(len(freq_ef)),freq_ef,label = 'ef freq')
    plt.legend()
    bla
 
if 0: # ge SSBspec repeat with mixer
    from single_qubit import ssbspec_mixer
    freq_ge = []   
    freq_ef = []
    for i in range(1):
        from single_qubit import ssbspec_mixer
    
        seq = sequencer.Trigger(600)
        
        spec = ssbspec_mixer.SSBSpec_mixer(qubit_info,mixer_info1,mixer_info2, np.linspace(-10e6, 10e6, 101), seq=seq, plot_seqs=False, proj_func='phase')
        spec.measure_keysight()          
        
        freq_ge.append(spec.center)
        plt.close()

        
#        seq = sequencer.Sequence([sequencer.Trigger(400), qubit2_info.rotate(np.pi, 0)])
#    #    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
#        postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
#    #    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
#        spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(ef2_info, np.linspace(-50e6, 50e6, 101), seq=seq, postseq = postseq, extra_info=qubit2_info, plot_seqs=False, generate=True, proj_func='phase')
#        spec.measure_keysight()
#        freq_ef.append(spec.center)
#        plt.close()
        
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
#    dig.set_naverages(4000)
    efr = efrabi.EFRabi(qubit2_info, ef2_info, np.linspace(-0.3, 0.3, 101), first_pi=True,second_pi=True, seq=None, generate=True, update=True,
                            proj_func='phase')
    efr.measure_keysight()
    period = efr.fit_params['period'].value
    dig.set_naverages(30000)
    efr = efrabi.EFRabi(qubit2_info, ef2_info, np.linspace(-0.3, 0.3, 101), first_pi=False, second_pi=True, selective=False, seq=None, generate=True,
                            force_period = period, proj_func='phase')
    efr.measure_keysight()
    dig.set_naverages(6000)
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
    efr = efrabi_mixer.EFRabi_mixer(qubit2_info, ef2_info, mixer_info2, np.linspace(-0.3, 0.3, 101), first_pi=True,second_pi=True, seq=None, generate=True, update=True,
                            proj_func='phase')
    efr.measure_keysight()
    period = efr.fit_params['period'].value
    dig.set_naverages(30000)
    efr = efrabi_mixer.EFRabi_mixer(qubit2_info, ef2_info, mixer_info2, np.linspace(-0.3, 0.3, 101), first_pi=False, second_pi=True, selective=False, seq=None, generate=True,
                            force_period = period, proj_func='phase')
    efr.measure_keysight()
    dig.set_naverages(6000)
    bla    
if 0: #measuring qubit temperature as we ramp field
    fields = np.linspace(0.05,0,21)
    Magnet = mclient.instruments['Magnet']
    e_g_vals=[]
    withpi_amps = []
    withpi_amps_err = []
    withoutpi_amps = []
    withoutpi_amps_err = []
    dig.set_naverages(3000)
    from single_qubit import efrabi
    for i in range(len(fields)):
        Magnet.do_set_field(fields[i])
        print(fields[i])
        time.sleep(20)
        from single_qubit import ssbspec_lorentzianfit
        seq = sequencer.Sequence([sequencer.Trigger(400), qubit2_info.rotate(np.pi, 0)])
    #    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
        postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
    #    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
        spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(ef2_info, np.linspace(-30e6, 20e6, 101), seq=seq, postseq = postseq, extra_info=qubit2_info, plot_seqs=False, generate=True, proj_func='phase')
        spec.measure_keysight()
        plt.close()
        fit_freq=spec.center
        deltaf_1 = ef2_info_set.get_deltaf()
        ef2_info_set.set_deltaf(deltaf_1+fit_freq*1e6)
        ef2_info = mclient.get_qubit_info('qubit2ef')
        efr = efrabi.EFRabi(qubit2_info, ef2_info, np.linspace(-0.4, 0.4, 101), first_pi=True,second_pi=True, seq=None, generate=True, update=True,
                                proj_func='phase')
        efr.measure_keysight()
        plt.close()
        g_amp=efr.fit_params['amp'].value
        g_amp_err = efr.fit_params['amp'].stderr
        period = efr.fit_params['period'].value
        dig.set_naverages(12000)
        efr = efrabi.EFRabi(qubit2_info, ef2_info, np.linspace(-0.4, 0.4, 101), first_pi=False, second_pi=True, selective=False, seq=None, generate=True,
                                force_period = period, proj_func='phase')
        efr.measure_keysight()
        plt.close()
        e_amp=efr.fit_params['amp'].value
        e_amp_err = efr.fit_params['amp'].stderr
        dig.set_naverages(3000)
        e_g_ratio=e_amp/g_amp
        e_g_vals.append(e_g_ratio)
        withpi_amps.append(g_amp)
        withpi_amps_err.append(g_amp_err)
        withoutpi_amps.append(e_amp)
        withoutpi_amps_err.append(e_amp_err)
    plt.figure()
    plt.plot(fields,e_g_vals)
    plt.title('qubit 2 temp with ramping magnetic field 20 sec sleep')
    plt.ylabel('e-g population ratio')
    plt.xlabel('Field T')
    plt.figure()
    plt.errorbar(fields,withpi_amps, yerr =withpi_amps_err, fmt ='o')
    plt.title('amplitude with pi pulse 20 sec sleep')
    plt.ylabel('amplitude')
    plt.xlabel('Field T')
    plt.figure()
    plt.errorbar(fields,withoutpi_amps, yerr =withoutpi_amps_err, fmt ='o')
    plt.title('amplitude without pi pulse 20 sec sleep')
    plt.ylabel('amplitude')
    plt.xlabel('Field T')
    fields = np.linspace(0,0.05,21)
    Magnet = mclient.instruments['Magnet']
    e_g_vals=[]
    withpi_amps = []
    withpi_amps_err = []
    withoutpi_amps = []
    withoutpi_amps_err = []
    dig.set_naverages(3000)
    from single_qubit import efrabi
    for i in range(len(fields)):
        Magnet.do_set_field(fields[i])
        print(fields[i])
        time.sleep(600)
        from single_qubit import ssbspec_lorentzianfit
        seq = sequencer.Sequence([sequencer.Trigger(400), qubit2_info.rotate(np.pi, 0)])
    #    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
        postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
    #    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
        spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(ef2_info, np.linspace(-30e6, 20e6, 101), seq=seq, postseq = postseq, extra_info=qubit2_info, plot_seqs=False, generate=True, proj_func='phase')
        spec.measure_keysight()
        plt.close()
        fit_freq=spec.center
        deltaf_1 = ef2_info_set.get_deltaf()
        ef2_info_set.set_deltaf(deltaf_1+fit_freq*1e6)
        ef2_info = mclient.get_qubit_info('qubit2ef')
        efr = efrabi.EFRabi(qubit2_info, ef2_info, np.linspace(-0.4, 0.4, 101), first_pi=True,second_pi=True, seq=None, generate=True, update=True,
                                proj_func='phase')
        efr.measure_keysight()
        plt.close()
        g_amp=efr.fit_params['amp'].value
        g_amp_err = efr.fit_params['amp'].stderr
        period = efr.fit_params['period'].value
        dig.set_naverages(12000)
        efr = efrabi.EFRabi(qubit2_info, ef2_info, np.linspace(-0.4, 0.4, 101), first_pi=False, second_pi=True, selective=False, seq=None, generate=True,
                                force_period = period, proj_func='phase')
        efr.measure_keysight()
        plt.close()
        e_amp=efr.fit_params['amp'].value
        e_amp_err = efr.fit_params['amp'].stderr
        dig.set_naverages(3000)
        e_g_ratio=e_amp/g_amp
        e_g_vals.append(e_g_ratio)
        withpi_amps.append(g_amp)
        withpi_amps_err.append(g_amp_err)
        withoutpi_amps.append(e_amp)
        withoutpi_amps_err.append(e_amp_err)
    plt.figure()
    plt.plot(fields,e_g_vals)
    plt.title('qubit 2 temp with ramping magnetic field 600 sec sleep')
    plt.ylabel('e-g population ratio')
    plt.xlabel('Field T')
    plt.figure()
    plt.errorbar(fields,withpi_amps, yerr =withpi_amps_err, fmt ='o')
    plt.title('amplitude with pi pulse 600 sec sleep')
    plt.ylabel('amplitude')
    plt.xlabel('Field T')
    plt.figure()
    plt.errorbar(fields,withoutpi_amps, yerr =withoutpi_amps_err, fmt ='o')
    plt.title('amplitude without pi pulse 600 sec sleep')
    plt.ylabel('amplitude')
    plt.xlabel('Field T')
    
    bla

if 0: # FT1 
    from single_qubit import FT1measurement
#    fwm = mclient.instruments['qubit2FWMbrick']

    for i in range(1):
#        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])

        ft1 = FT1measurement.FT1Measurement(qubit2_info, ef2_info, np.linspace(0, 10e3, 101), seq=None, proj_func='phase')
#        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.concatenate((np.linspace(0, 1e3, 31), np.linspace(1.01e3, 5e3, 31))), seq=None, proj_func='phase')

        ft1.measure_keysight()


    bla
if 0: # FT1 mixer this one doesn't seem to be working use one below
    from single_qubit import FT1measurement_mixer
#    fwm = mclient.instruments['qubit2FWMbrick']

    for i in range(1):
#        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])

        ft1 = FT1measurement_mixer.FT1Measurement_mixer(qubit2_info, ef2_info, mixer_info2, np.linspace(0, 30e3, 101), seq=None, proj_func='phase')
#        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.concatenate((np.linspace(0, 1e3, 31), np.linspace(1.01e3, 5e3, 31))), seq=None, proj_func='phase')

        ft1.measure_keysight()


    bla
    
if 0: # FT1 mixer

    from single_qubit import T1measurement_mixer

#    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 250e3, 121), 
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(2000, 1, chan='3m1'), sequencer.Delay(250),
#                          ef_info.rotate(np.pi, 0), sequencer.Constant(4000, 1, chan='3m1'), sequencer.Delay(250)])
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
    postseq = sequencer.Sequence([qubit2_info.rotate(np.pi/2, 0)])
    t1 = T1measurement_mixer.T1Measurement_mixer(ef2_info, mixer_info1, mixer_info2, #np.linspace(0, 500e3, 101),
                                         np.linspace(0e3, 30e3, 101),
#                                         np.concatenate((np.linspace(5e3, 5e3, 50), np.linspace(6e3, 6e3, 51))),
                                         double_exp=False, generate=True, plot_seqs=False, proj_func='phase', seq=seq , postseq = postseq, 
                                         extra_info=qubit2_info)    
    t1.measure_keysight()
    bla
    
if 0: # FT1 with 2 ef freq
    from single_qubit import FT1measurementtwomode
#    fwm = mclient.instruments['qubit2FWMbrick']

    for i in range(1):
#        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
        ft1 = FT1measurementtwomode.FT1MeasurementTwoMode(qubit2_info, ef2_info, ef2_V2_info, np.linspace(0, 20e3, 101), seq=None, proj_func='phase', plot_seqs = False)
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
    
if 0: # FT1 with fwminfo
    from single_qubit import FT1withFwm
#    fwm_gen = mclient.instruments['qubit2FWMbrick']
#    postseq = sequencer.Sequence(sequencer.Delay(5))
    postseq = sequencer.Sequence(qubit2_info.rotate(np.pi/2, 0))
    amps = np.linspace(.7,.7,1)
    freqs = np.linspace(5.6019e9, 6.515e9, 1)
    plt.figure()
    for freq in freqs:
#        fwm_gen.set_frequency(freq)
        ft1times = np.zeros(len(amps))
        ft1err = np.zeros(len(amps))
        for i in range(len(amps)):
    #        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
            ft1 = FT1withFwm.FT1withFWM(qubit2_info, ef2_info, fwm_info2, fwm_pulse=True, delays = np.linspace(100, 10e3, 101), 
                                        amp = amps[i], seq=None, postseq = postseq, plot_seqs=False,
                                        proj_func='phase')
    #        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.concatenate((np.linspace(0, 1e3, 31), np.linspace(1.01e3, 5e3, 31))), seq=None, proj_func='phase')
    
            ft1.measure_keysight()
            ft1times[i] = ft1.fit_params['tau'].value
            ft1err[i] = ft1.fit_params['tau'].stderr
#            plt.close()
#        plt.figure()
        plt.errorbar(amps, ft1times/1000,yerr = ft1err/1000,marker = 'o',label = 'FT1 freq = %s GHz'%(freq/1e9)) 
    plt.xlabel('amps')
    plt.ylabel('FT1(us)')
    plt.legend()


    bla
    
if 0: # FT1 with fwm channal
    from single_qubit import FT1withFwmchan

#    fwm_gen = mclient.instruments['SS_drive']
#    fwm_gen2.set_rf_on(True)
#    time.sleep(0.1)
#    fwm_gen2.set_power(10)
#    time.sleep(0.1)

    amps = [0.7]
    freqs = np.linspace(5.475e9, 5.485e9, 11)
    plt.figure()
    dig.set_naverages(4000)
    for j in range(len(amps)):
#        from single_qubit import ssbspec_gaussianfit
#    
#        seq = sequencer.Trigger(600)
#        
#        spec = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit2_info, np.linspace(-5e6, 5e6, 101), seq=seq, plot_seqs=False, proj_func='phase')
#        spec.measure_keysight()          
#        
##        freq_ge.append(spec.fit_params['freq'].value/1e6)
#        plt.close()
#        from single_qubit import ssbspec_lorentzianfit
#        
#        seq = sequencer.Sequence([sequencer.Trigger(400), qubit2_info.rotate(np.pi, 0)])
#    #    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
#        postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
#    #    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
#        spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(ef2_info, np.linspace(-50e6, 50e6, 101), seq=seq, postseq = postseq, extra_info=qubit2_info, plot_seqs=False, generate=True, proj_func='phase')
#        spec.measure_keysight()
##        freq_ef.append(spec.center)
#        plt.close()
        

        ft1times = np.zeros(len(freqs))
        ft1err = np.zeros(len(freqs))
        for i, freq in enumerate(freqs):
            fwm_gen2.set_frequency(freq)
    #        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
#            postseq = sequencer.Sequence(qubit2_info.rotate(np.pi/2, 0))
            ft1 = FT1withFwmchan.FT1withFWMCHAN(qubit2_info, ef2_info, fwm_pulse=True, delays = np.linspace(0, 6e3, 101), 
                                        amp = amps[j], seq=None, postseq = None, 
                                        proj_func='phase')
    #        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.concatenate((np.linspace(0, 1e3, 31), np.linspace(1.01e3, 5e3, 31))), seq=None, proj_func='phase')
    
            ft1.measure_keysight()
            ft1times[i] = ft1.fit_params['tau'].value
            ft1err[i] = ft1.fit_params['tau'].stderr
            plt.close()
#        plt.figure()
#        plt.errorbar(amps, ft1times/1000,yerr = ft1err/1000,marker = 'o',label = 'FT1 freq = %s GHz'%(freq/1e9)) 
        plt.errorbar(freqs/1e9, ft1times/1000,yerr = ft1err/1000,marker = 'o',label = 'FT1 amp = %s'%(amps[j]))
    plt.xlabel('freqs(GHz)')
#    plt.xlabel('amps')
    plt.ylabel('FT1(us)')
    plt.legend()
#    fwm_gen2.set_ch1_output(False)

    bla
    
    
if 0: # FWM SSBspec
    from single_qubit import fwm_ssbspec
#    seq = sequencer.Sequence([sequencer.Trigger(400), qubit2_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
    postseq = sequencer.Sequence(ef2_info.rotate(np.pi/2, 0))
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    spec = fwm_ssbspec.FWM_SSBSpec(qubit2_info,ef2_info,fwm_info2, np.linspace(-5e6, 10e6, 101), seq=None, postseq = postseq, plot_seqs=False, generate=True, proj_func='phase')
    spec.measure_keysight()


    bla      
    

    
if 0: # EFT2
    from scripts.single_qubit import EFT2measurement # frequency stability of |f> vs |e>
    for i in range(1):
#        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
        seq = sequencer.Sequence(sequencer.Trigger(250))
        eft2 = EFT2measurement.EFT2Measurement(qubit2_info, ef2_info, np.linspace(0, 1.5e3, 101), detune=5e6, double_freq=True, plot_seqs = False, echotype = EFT2measurement.ECHO_NONE,
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
    if 0:
        Magnet.do_set_PSwitch(1)
        print('heating PSwitch')
        time.sleep(40)
#        Magnet.do_set_field(0)
#        print('setting field')
#        time.sleep(1800)
        Magnet.do_set_field(0.0)
        print('setting field')
        time.sleep(100)
        Magnet.do_set_PSwitch(0)
        print('cooling PSwitch')
        time.sleep(350)
#    freqs = np.linspace(10.80e9,10.82e9,21)
    freqs = np.linspace(10.81e9,10.81e9,5)
#    freqs = np.linspace(10.813e9,10.813e9,3)
    freq_range = np.linspace(-14e6, 2e6, 81)
    powers = np.zeros(len(freqs))
#    powers= [10,10,10,10,10,9,8,6,4,2,0,1,3,4,4,5,7,10,10,10,10]
#    powers = [4,4,4]
    phase = np.zeros((len(freqs),len(freq_range)))
    phase0 = np.zeros((len(freqs),len(freq_range)))
    fit_freq = np.zeros(len(freqs))
    fit_freq0 = np.zeros(len(freqs))
    fit_freq_err = np.zeros(len(freqs))
    fit_freq0_err = np.zeros(len(freqs))
    SSdrive = mclient.instruments['SS_drive']
    for ifreq, freq in enumerate(freqs):
        SSdrive.set_power(powers[ifreq])
        SSdrive.set_frequency(freq)
        time.sleep(0.1)
        SSdrive.set_rf_on(True)
        time.sleep(0.1)
    
        from single_qubit import ssbspec_gaussianfit_SS
    
        seq = sequencer.Trigger(600)
        spec = ssbspec_gaussianfit_SS.SSBSpec_Gaussianfit_SS(qubit2_info, freq_range, seq=seq, plot_seqs=False, proj_func='phase')
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
        
        spec = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit2_info, freq_range, seq=seq, plot_seqs=False, proj_func='phase')
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
        
    if freqs[0] == freqs[1]:
        freqs = np.asarray(range(len(freqs)))
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
        
        
        
        