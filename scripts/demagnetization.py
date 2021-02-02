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
#fwm_info = mclient.get_qubit_info('fwm_info1')
#fwm2_info = mclient.get_qubit_info('fwm_info2')
#qubit03_info = mclient.get_qubit_info('qubit1_03')
#qubit14_info = mclient.get_qubit_info('qubit1_14')
readout_info = mclient.get_readout_info('readout')
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')
os.chdir(r'C:/qrlab/scripts')

fields = [0.03,-0.025, 0.02,-0.015,0.01,-0.008,0.006,-0.004, 0.0025, -0.001,0.0005,-0.00025, 0]
#fields = - np.asarray(fields)
#Magnet.do_set_PSwitch(1)
#time.sleep(35)
#fields = np.linspace(0,-0.05,26)
for field in fields:
    print(field)
    if abs(field)>0.01:
        Magnet.do_set_field(0)
        time.sleep(400)

    
#    Magnet.do_set_PSwitch(1)
#    time.sleep(35)
#            
    Magnet.do_set_field(field)
    time.sleep(300)
#    Magnet.do_set_PSwitch(0)
#    time.sleep(350)
    '''
    from single_cavity import rocavspectroscopy_keysight
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
#    Yoko.do_set_current(-0.00175)
    rofreq = 10.715e9
    freq_range = 10e6
    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(10, 10, 1),
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
#    ga = ro.ampdata[0]
#    gp = ro.phasedata[0]
#    g = ga * np.exp(1j*(gp/180 * np.pi))
    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(10, 10, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
    ro.measure()
    plt.close()
    plt.close()
    plt.figure('amp  %sT'%(field))
    label = ' qubit1 in e state'
    plt.plot(ro.freqs, ro.ampdata[0],label = label) 
    plt.legend()
    plt.figure('phase  %sT'%(field))
    plt.plot(ro.freqs, ro.phasedata[0],label = label)   
    plt.legend()
    
    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit2_info, np.linspace(10, 10, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
    ro.measure()
    plt.close()
    plt.close()
    plt.figure('amp  %sT'%(field))
    label = ' qubit2 in e state'
    plt.plot(ro.freqs, ro.ampdata[0],label = label) 
    plt.legend()
    fn = os.path.join(r'C:\_Data', 'images/%s_amp%sT.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),field))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    plt.savefig(fn, **kwargs)
    
    plt.figure('phase  %sT'%(field))
    plt.plot(ro.freqs, ro.phasedata[0],label = label)   
    plt.legend()
    fn = os.path.join(r'C:\_Data', 'images/%s_phase%sT.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),field))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    plt.savefig(fn, **kwargs)

'''