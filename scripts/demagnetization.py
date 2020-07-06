# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 13:07:24 2019

@author: Wang_Lab
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
#ef2_V2_info = mclient.get_qubit_info('qubit2ef_V2')

#fwm_info = mclient.get_qubit_info('fwm_info1')
#fwm2_info = mclient.get_qubit_info('fwm_info2')
#qubit03_info = mclient.get_qubit_info('qubit1_03')
#qubit14_info = mclient.get_qubit_info('qubit1_14')
readout_info = mclient.get_readout_info('readout')
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')
os.chdir(r'C:/qrlab/scripts')

fields = [-0.04, 0.03,-0.025, 0.02,-0.015, 0.01, -0.005, 0.0025, -0.001,0.0005,-0.00025, 0]
#field = 0
#fields = - np.asarray(fields)
Magnet.do_set_PSwitch(1)
time.sleep(35)




dig.set_naverages(6000)

for field in fields:
    if abs(field)>0.01:
        Magnet.do_set_field(0)
        time.sleep(600)

    

#            
    Magnet.do_set_field(field)
    time.sleep(600)
#fields = np.linspace(0,-0.05,51)
#for field in fields:
#    Magnet.do_set_PSwitch(1)
#    print('heating PSwitch')
#    time.sleep(40)
##        Magnet.do_set_field(0)
##        print('setting field')
##        time.sleep(1800)
#    Magnet.do_set_field(field)
#    print('setting field')
#    time.sleep(60)
#    Magnet.do_set_PSwitch(0)
#    print('cooling PSwitch')
#    time.sleep(350)
#
#
#
#    from single_cavity import rocavspectroscopy_keysight
##    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
##    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
##    Yoko.do_set_current(-0.00175)
#    rofreq = 10.82e9
#    freq_range = 20e6
#    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit2_info, np.linspace(10, 10, 1),
#                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 401),
#                                             qubit_pulse=False, seq=None)#,extra_info=[ef2_info])
#    ro.measure()
#    
##by Yingying
#    plt.close()
#    plt.close()
#    plt.figure('amp  %sT'%(field))
#    label = ' qubit2 in g state, field = %sT'%(field)
#    plt.plot(ro.freqs, ro.ampdata[0],label = label) 
#    plt.legend()
#    plt.figure('phase  %sT'%(field))
#    plt.plot(ro.freqs, ro.phasedata[0],label = label)   
#    plt.legend()
###    ga = ro.ampdata[0]
###    gp = ro.phasedata[0]
###    g = ga * np.exp(1j*(gp/180 * np.pi))
##    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(10, 10, 1),
##                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 201),
##                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
##    ro.measure()
##    plt.close()
##    plt.close()
##    plt.figure('amp  %sT'%(field))
##    label = ' qubit1 in e state'
##    plt.plot(ro.freqs, ro.ampdata[0],label = label) 
##    plt.legend()
##    plt.figure('phase  %sT'%(field))
##    plt.plot(ro.freqs, ro.phasedata[0],label = label)   
##    plt.legend()
#    
#    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit2_info, np.linspace(10, 10, 1),
#                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 401),
#                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
#    ro.measure()
#    plt.close()
#    plt.close()
#    plt.figure('amp  %sT'%(field))
#    label = ' qubit2 in e state'
#    plt.plot(ro.freqs, ro.ampdata[0],label = label) 
#    plt.legend()
##    plt.figure('phase  %sT'%(field))
##    plt.plot(ro.freqs, ro.phasedata[0],label = label)   
##    plt.legend()
##    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
##    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit2_info, np.linspace(10,10,1),
##                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
##                                             qubit_pulse=False, seq=seq ,extra_info=[ef2_info])
##    ro.measure()
##    plt.close()
##    plt.close()
##    plt.figure('amp  %sT'%(field))
##    label = ' qubit2 in f state'
##    plt.plot(ro.freqs, ro.ampdata[0],label = label) 
##    plt.legend()
#    fn = os.path.join(r'C:\_Data', 'images/%s_amp%sT.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),field))
#    fdir = os.path.split(fn)[0]
#    if not os.path.isdir(fdir):
#        os.makedirs(fdir)
#    kwargs = dict()
#    plt.savefig(fn, **kwargs)
#    
#    plt.figure('phase  %sT'%(field))
#    plt.plot(ro.freqs, ro.phasedata[0],label = label)   
#    plt.legend()
#    fn = os.path.join(r'C:\_Data', 'images/%s_phase%sT.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),field))
#    fdir = os.path.split(fn)[0]
#    if not os.path.isdir(fdir):
#        os.makedirs(fdir)
#    kwargs = dict()
#    plt.savefig(fn, **kwargs)
#    plt.close()
#    plt.close()
#    ro_freq = 10.8095e9
#    power = 10
#    readout_info.rfsource1.set_frequency(ro_freq)
#    readout_info.rfsource1.set_power(power)
#    readout_info.rfsource2.set_frequency(ro_freq+50e6)
#    
#    
#    
#    from single_qubit import rabi
#    import time
##    update_proj =False
##    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
#    tr = rabi.Rabi(qubit2_info, 
##                               np.linspace(-0.5, 0.5, 81), selective=False,
#                               np.linspace(-0.7, 0.7, 81), selective=False,
##                               np.linspace(-0.1, 0.1, 81), selective=True,
##                               np.linspace(-0.03, 0.03, 81), selective=True,
#        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
#                               plot_seqs=False, generate=True, repeat_pulse=1,# seq=seq,postseq = postseq,
#                               update=True,# extra_info=[qubit2_info],
#                               proj_func='phase')
#    tr.measure_keysight()
#
#
#
#    from single_qubit import T1measurement
#
##    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 250e3, 121), 
##    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(2000, 1, chan='3m1'), sequencer.Delay(250),
##                          ef_info.rotate(np.pi, 0), sequencer.Constant(4000, 1, chan='3m1'), sequencer.Delay(250)])
##    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
#
#    t1 = T1measurement.T1Measurement(qubit2_info, #np.linspace(0, 500e3, 101),
#                                         np.linspace(0e3, 40e3, 101),
##                                         np.concatenate((np.linspace(5e3, 5e3, 50), np.linspace(6e3, 6e3, 51))),
#                                         double_exp=False, generate=True, plot_seqs=False, proj_func='phase', seq=None)    
#    t1.measure_keysight()
#    
#    
#    
#    from single_qubit import T2measurement
##    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
#
#    t2 = T2measurement.T2Measurement(qubit2_info, np.linspace(0, 5e3, 101), detune=1e6, double_freq=False, generate=True, 
#                                     seq=None, postseq=None, proj_func='phase') #extra_info=[qubit2_info])
##        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
##                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')
#
#    
#    t2.measure_keysight()
