# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 14:55:43 2018

@author: wanglab
"""

import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
matplotlib.rcParams['backend'] = 'Qt4Agg'
matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
#from t1t2_plotting import smart_T1_delays
import math as math
import time


import os
os.chdir(r'c:\qrlab')

#mpl.rcParams['figure.figsize']=[5,3.5]
#mpl.rcParams['axes.color_cycle'] = ['b', 'g', 'r', 'c', 'm', 'k']
#alz = mclient.instruments['alazar']
#alz.set_naverages(2000)

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')

ge = mclient.instruments['qubit1ge']

Yoko = mclient.instruments['Yoko']
qbrick = mclient.instruments['sc2']
RObrick = mclient.instruments['RObrick']
refbrick = mclient.instruments['refbrick']


currents = np.arange(1.8e-3, 2.2e-3, 0.02e-3)
Yoko.set_output_state(True) 
ssbspec_freqs = np.linspace(-15e6, 15e6, 51) #range of points to check each ssbspec
qbrick_freq = 720e6
RObrick_freq = 7596.1e6
w = 200
w_selective = 1000
pi_amp_initial = .1934
default_sideband = 100e6


w_q = np.zeros_like(currents)

qbrick.set_frequency(qbrick_freq)
RObrick.set_frequency(RObrick_freq)
refbrick.set_frequency(RObrick_freq+50e6)
time.sleep(1)


for i in range(len(currents)):
    
    Yoko.do_set_current(currents[i])
    time.sleep(1)
    
             
#    '''Here we do an SSB spec'''
#    from scripts.single_qubit import ssbspec
#    seq = sequencer.Trigger(250)        
#    spec = ssbspec.SSBSpec(qubit_info, ssbspec_freqs, seq=seq, plot_seqs=False)
#    spec.measure()
#    drive_freq = qbrick.do_get_frequency()
#    w_q[i] = ssbspec_freqs[np.argmin(spec.get_ys())] + drive_freq - default_sideband
#    
#    time.sleep(1)
    '''Here we do an SSB spec'''
    from scripts.single_qubit import ssbspec
    seq = sequencer.Trigger(250)        
    spec = ssbspec.SSBSpec(qubit_info, ssbspec_freqs, seq=seq, plot_seqs=False)
    spec.measure_keysight()
    drive_freq = qbrick.do_get_frequency()
    w_q[i] = ssbspec_freqs[np.argmin(spec.get_ys())] + drive_freq - default_sideband
    
    time.sleep(1)

plt.figure()


plt.plot(currents*1e3, w_q/1e6)
plt.ylabel('w_q (MHz)')
plt.xlabel('current [mA]')


plt.plot()

Yoko.set_output_state(False)    

