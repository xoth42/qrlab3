# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 17:35:59 2020

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 11:49:29 2020

@author: Wang_Lab
"""

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
mixer_info1 = mclient.get_qubit_info('mixer_info1')
mixer_info2 = mclient.get_qubit_info('mixer_info2')
mixer_info1_set = mclient.instruments['mixer_info1']
mixer_info2_set = mclient.instruments['mixer_info2']
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

#fields = [-0.05,0.04,-0.035,0.03,-0.025,0.02,-0.015,0.01,-0.005, 0.0025, -0.001,0.0005,-0.00025, 0]
#fields = - np.asarray(fields)
#Magnet.do_set_PSwitch(1)
#time.sleep(1000)

dig.set_naverages(40000)
dig.do_set_trigger_period(100)
fields = np.linspace(0,-0.05,26)
for field in fields:
#    if abs(field)>0.01:
#        Magnet.do_set_field(0)
#        time.sleep(600)

    
    Magnet.do_set_PSwitch(1)
    print('heating PSwitch')
    time.sleep(35)
#            
    Magnet.do_set_field(field)
    print('setting field')
    time.sleep(30)
    Magnet.do_set_PSwitch(0)
    print('cooling PSwitch')
    time.sleep(350)
#    ro_freq = 10.8117e9zA
#    power = 10
#    readout_info.rfsource1.set_frequency(ro_freq)
#    readout_info.rfsource1.set_power(power)
#    readout_info.rfsource2.set_frequency(ro_freq+50e6)

    
    
#    from single_qubit import ssbspec
#    seq = sequencer.Sequence([sequencer.Trigger(400), qubit2_info.rotate(np.pi, 0)])
##    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
#    postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
##    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
#    spec = ssbspec.SSBSpec(ef2_info, np.linspace(-40e6, 10e6, 101), seq=seq, postseq = postseq, extra_info=qubit2_info, plot_seqs=False, generate=True, proj_func='phase')
#    spec.measure_keysight()
    
#    from single_qubit import efrabi
#
#    efr = efrabi.EFRabi(qubit2_info, ef2_info, np.linspace(-0.7, 0.7, 101), first_pi=True,second_pi=True, seq=None, generate=True, update=True,
#                            proj_func='phase')
#    efr.measure_keysight()
#
#
#    
#    from single_qubit import T1measurement
#    t1 = T1measurement.T1Measurement(qubit2_info, #np.linspace(0, 500e3, 101),
#                                         np.linspace(0e3, 50e3, 101),
##                                         np.concatenate((np.linspace(5e3, 5e3, 50), np.linspace(6e3, 6e3, 51))),
#                                         double_exp=False, generate=True, plot_seqs=False, proj_func='phase', seq=None)    
#    t1.measure_keysight()
#    
#    from single_qubit import FT1measurement
#    ft1 = FT1measurement.FT1Measurement(qubit2_info, ef2_info, np.linspace(0, 20e3, 101), seq=None, proj_func='phase')
##        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.concatenate((np.linspace(0, 1e3, 31), np.linspace(1.01e3, 5e3, 31))), seq=None, proj_func='phase')
#
#    ft1.measure_keysight()    
    
    from single_cavity import rocavspectroscopy_keysight_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
#    Yoko.do_set_current(-0.00175)
    mixer1_amp = .7
    mixer_info1_set.set_pi_amp(mixer1_amp)
    mixer_info1 = mclient.get_qubit_info('mixer_info1')
    rofreq = 10.8175e9
    freq_range = 17.5e6
    ro = rocavspectroscopy_keysight_mixer.ROCavSpectroscopy_keysight_mixer(qubit2_info, mixer_info1, np.linspace(10, 10, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                             qubit_pulse=False, seq=None)#,extra_info=[ef2_info])
    ro.measure()
    
#by Yingying
    plt.close()
    plt.close()
    plt.figure('amp  %sT'%(field))
    label = ' qubit in g state, field = %sT'%(field)
    plt.plot(ro.freqs, ro.ampdata[0],label = label) 
    plt.legend()
    plt.figure('phase  %sT'%(field))
    plt.plot(ro.freqs, ro.phasedata[0],label = label)   
    plt.legend()
##    ga = ro.ampdata[0]
##    gp = ro.phasedata[0]
##    g = ga * np.exp(1j*(gp/180 * np.pi))
    ro = rocavspectroscopy_keysight_mixer.ROCavSpectroscopy_keysight_mixer(qubit2_info, mixer_info1, np.linspace(10, 10, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
    ro.measure()
    plt.close()
    plt.close()
    plt.figure('amp  %sT'%(field))
    label = ' qubit1 in e state'
    plt.plot(ro.freqs, ro.ampdata[0],label = label) 
    plt.legend()
#    plt.figure('phase  %sT'%(field))
#    plt.plot(ro.freqs, ro.phasedata[0],label = label)   
#    plt.legend()
#    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit2_info, np.linspace(-6, 10, 1),
#                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 401),
#                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
#    ro.measure()
#    plt.close()
#    plt.close()
#    plt.figure('amp  %sT'%(field))
#    label = ' qubit2 in e state'
#    plt.plot(ro.freqs, ro.ampdata[0],label = label) 
#    plt.legend()
    fn = os.path.join(r'C:\_Data', 'images/%s_amp%sT.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),field))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    plt.savefig(fn, **kwargs)
    plt.figure('phase  %sT'%(field))
    plt.plot(ro.freqs, ro.phasedata[0],label = label)   
    plt.legend()
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
#    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit2_info, np.linspace(10,10,1),
#                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
#                                             qubit_pulse=False, seq=seq ,extra_info=[ef2_info])
#    ro.measure()
#    plt.close()
#    plt.close()
#    plt.figure('amp  %sT'%(field))
#    label = ' qubit2 in f state'
#    plt.plot(ro.freqs, ro.ampdata[0],label = label) 
#    plt.legend()
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
    fn = os.path.join(r'C:\_Data', 'images/%s_phase%sT.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),field))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    plt.savefig(fn, **kwargs)
    
    
#while(True):
#    from single_qubit import ssbspec
#    seq = sequencer.Sequence([sequencer.Trigger(400), qubit2_info.rotate(np.pi, 0)])
##    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
#    postseq = sequencer.Sequence(qubit2_info.rotate(np.pi, 0))
##    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
#    spec = ssbspec.SSBSpec(ef2_info, np.linspace(-40e6, 10e6, 101), seq=seq, postseq = postseq, extra_info=qubit2_info, plot_seqs=False, generate=True, proj_func='phase')
#    spec.measure_keysight()
#    
#    from single_qubit import efrabi
#
#    efr = efrabi.EFRabi(qubit2_info, ef2_info, np.linspace(-0.7, 0.7, 101), first_pi=True,second_pi=True, seq=None, generate=True, update=True,
#                            proj_func='phase')
#    efr.measure_keysight()
#
#
#    
#    from single_qubit import T1measurement
#    t1 = T1measurement.T1Measurement(qubit2_info, #np.linspace(0, 500e3, 101),
#                                         np.linspace(0e3, 50e3, 101),
##                                         np.concatenate((np.linspace(5e3, 5e3, 50), np.linspace(6e3, 6e3, 51))),
#                                         double_exp=False, generate=True, plot_seqs=False, proj_func='phase', seq=None)    
#    t1.measure_keysight()
#    
#    from single_qubit import FT1measurement
#    ft1 = FT1measurement.FT1Measurement(qubit2_info, ef2_info, np.linspace(0, 20e3, 101), seq=None, proj_func='phase')
##        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.concatenate((np.linspace(0, 1e3, 31), np.linspace(1.01e3, 5e3, 31))), seq=None, proj_func='phase')
#
#    ft1.measure_keysight() 