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
alz = mclient.instruments['alazar']
alz.set_naverages(2000)

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')

ge = mclient.instruments['qubit1ge']

Yoko = mclient.instruments['Yoko']
qbrick = mclient.instruments['qbrick']
RObrick = mclient.instruments['RObrick']
refbrick = mclient.instruments['refbrick']

#DON'T CHANGE THE DAMN CURRENT STEP!!!!!!!!!
currents = np.arange(0.0000, 0.0005, .00001)
w_q = np.zeros_like(currents)
t1_times = np.zeros_like(currents)
t2_times = np.zeros_like(currents)
pi_amps = np.zeros_like(currents)
w_c = np.zeros(len(currents)/10)

ssbspec_freqs = np.linspace(-20e6, 5e6, 40)
qbrick_freq = 5944e6
RObrick_freq = 8306.75e6
rocav_freqs = np.linspace(RObrick_freq - 10e6, RObrick_freq + 5e6, 40)
qbrick.set_frequency(qbrick_freq)
RObrick.set_frequency(RObrick_freq)
refbrick.set_frequency(RObrick_freq+50e6)
time.sleep(1)

w = 40
w_selective = 100

ge.set('w', w)
ge.set('w_selective', w_selective)



for i in range(len(currents)):
    
    Yoko.do_set_current(currents[i])
    time.sleep(1)
    if i %10==0:
        from scripts.single_cavity import rocavspectroscopy

        ro = rocavspectroscopy.ROCavSpectroscopy(qubit_info, [-30],
                                         rocav_freqs, qubit_pulse=False)
        ro.measure()
        newRO = rocav_freqs[np.argmax(ro.ampdata[0])]
        RObrick.set_frequency(newRO)
        refbrick.set_frequency(newRO+50e6)
        time.sleep(1)
        w_c[i/10] = newRO
        
    '''Here we do an SSB spec'''
    from scripts.single_qubit import ssbspec
    seq = sequencer.Trigger(250)        
    spec = ssbspec.SSBSpec(qubit_info, ssbspec_freqs, seq=seq, plot_seqs=False)
    spec.measure()
    drive_freq = qbrick.do_get_frequency()
    w_q[i] = ssbspec_freqs[np.argmin(spec.get_ys())] + drive_freq - 100e6
    
    qbrick.set_frequency(w_q[i] + 100e6)
    time.sleep(1)
    
    '''Here we do a Rabi'''
    from scripts.single_qubit import rabi
    tr = rabi.Rabi(qubit_info, np.linspace(-0.4, 0.4, 100), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
                   update=False)

    data=tr.measure()
    pi_amps[i] = tr.pi_amp         
    ge.set('pi_amp', tr.pi_amp)
    ge.set('pi2_amp', 0)
    ge.set('pi_amp_selective', float(w)/w_selective * tr.pi_amp)
    qubit_info = mclient.get_qubit_info('qubit1ge')
    
    '''Here we do a T1 measurement'''
    from scripts.single_qubit import T1measurement

    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 40e3, 100), double_exp=False, generate=True, plot_seqs=False)

    t1.measure()
    t1_times[i] = t1.analyze()
    
    '''Here we do a T2 measurement'''
    from scripts.single_qubit import T2measurement

    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 2e3, 150), detune=4e6, double_freq=False, generate=True)
    t2.measure()
    t2_times[i] = t2.analyze()
    time.sleep(1)
    plt.close('all')
    

f = plt.figure()
ax1 = f.add_subplot(4,1,1)
ax2 = f.add_subplot(4,1,2)
ax3 = f.add_subplot(4,1,3)
ax4 = f.add_subplot(4,1,4)

ax1.plot(currents, w_q)
ax2.plot(currents, t1_times)
ax3.plot(currents, t2_times)
ax4.plot(currents, pi_amps)
ax1.set_ylabel('w_q')
ax2.set_ylabel('t1')
ax3.set_ylabel('t2')
ax4.set_ylabel('pi_amp')
ax4.set_xlabel('current [A]')


plt.plot()
    

