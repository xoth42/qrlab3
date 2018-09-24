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


qubit_info = mclient.get_qubit_info('qubit1ge')
#RO_info = mclient.get_qubit_info('RO')
os.chdir(r'C:/qrlab/scripts')

if 0:
    from single_cavity import rocavspectroscopy_keysight
#    rofreq = 8553.1e6
    rofreq = 7719e6
    freq_range = 50e6
    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(-30, -40, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 201),
                                             qubit_pulse=False)
    ro.measure()
    
if 0:
    from single_cavity import rocavspectroscopy_keysight_IQmod
#    rofreq = 8553.1e6
    rofreq = 8306.00e6
    freq_range = 15e6
    ro = rocavspectroscopy_keysight_IQmod.ROCavSpectroscopy(qubit_info, RO_info, np.linspace(-10, -20, 3),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 55),
                                             plen=20000, amp=0.0001, qubit_pulse=False)
    ro.measure()
    

if 1:
    from single_qubit import spectroscopy_keysight
#    from scripts.single_qubit import spectroscopy_IQ
#    for i in range(5560, 5560, 0):
    qubit_freq = 4534.13e6
    freq_range = 1.5e6
    spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['geBrick'], qubit_info,
                                     np.linspace(qubit_freq-freq_range,
                                                 qubit_freq+freq_range, 251),
                                     [-30],
                                     plen=5000, amp=0.006, plot_seqs=False) 

    spec.measure()

    
    
    
if 0:
    from scripts.single_qubit import ssbspec
    seq = sequencer.Trigger(250)

    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-5e6, 2e6, 151), seq=seq, plot_seqs=False)
    spec.measure_keysight()
    