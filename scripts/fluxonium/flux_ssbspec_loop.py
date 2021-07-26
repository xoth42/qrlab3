# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 14:55:43 2018

@author: wanglab
"""

import mclient
import importlib
importlib.reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
matplotlib.rcParams['backend'] = 'Qt4Agg'
matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
#from t1t2_plotting import smart_T1_delays
import math as math
import time
from scipy.optimize import curve_fit
def quadratic(x, a, b, c):
    return (a*(x**2)) + (b*x) + c


import os
os.chdir(r'c:\qrlab-3')

#mpl.rcParams['figure.figsize']=[5,3.5]
#mpl.rcParams['axes.color_cycle'] = ['b', 'g', 'r', 'c', 'm', 'k']
alz = mclient.instruments['alazar']
alz.set_naverages(1000)

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')

ge = mclient.instruments['qubit1ge']

Yoko = mclient.instruments['Yoko']
qbrick = mclient.instruments['qbrick']
RObrick = mclient.instruments['RObrick']
refbrick = mclient.instruments['refbrick']


'''Be careful about changing the current step without widening the SSBspec
    The interpolation should help this but still be careful.'''
currents = np.arange(0.00002, 0.0013, .00004)
ssbspec_freqs = np.linspace(-15e6, 5e6, 40) #range of points to check each ssbspec
qbrick_freq = 5944e6
RObrick_freq = 8306.75e6
w = 40
w_selective = 100
pi_amp_initial = .1934
cav_update_rate = 5
default_sideband = 100e6


w_q = np.zeros_like(currents)
t1_times = np.zeros_like(currents)
t2_times = np.zeros_like(currents)
pi_amps = np.zeros_like(currents)
w_c = np.zeros(len(currents)/cav_update_rate)

qbrick.set_frequency(qbrick_freq)
RObrick.set_frequency(RObrick_freq)
refbrick.set_frequency(RObrick_freq+50e6)
time.sleep(1)

ge.set('pi_amp_selective', float(w)/w_selective * pi_amp_initial)
ge.set('w', w)
ge.set('w_selective', w_selective)
qubit_info = mclient.get_qubit_info('qubit1ge')


for i in range(len(currents)):
    
    Yoko.do_set_current(currents[i])
    time.sleep(1)
    if i % cav_update_rate==0:
        j = i/cav_update_rate
        from scripts.single_cavity import rocavspectroscopy
        
        rocav_freqs = np.linspace(w_c[j-1] - 3e6, w_c[j-1] + 2e6, 10)
        ro = rocavspectroscopy.ROCavSpectroscopy(qubit_info, [-30],
                                         rocav_freqs, qubit_pulse=False)
        ro.measure()
        w_c[j] = rocav_freqs[np.argmax(ro.ampdata[0])]
        RObrick.set_frequency(w_c[j])
        refbrick.set_frequency(w_c[j]+50e6)
        time.sleep(1)   

    ''' Interpolate to guess the new qubit frequency so the spec hits'''
    if i == 1:
        qbrick.set_frequency(w_q[i-1] + default_sideband)
    elif i==2:
        qbrick.set_frequency(w_q[i-1]*2-w_q[i-2] + default_sideband)
        print((w_q[i-1]*2-w_q[i-2] + default_sideband))
    elif i>2:
        fit_params, covariance = curve_fit(quadratic, np.arange(i), w_q[:i], p0 = [-1, 0, w_q[0]])
        function_parameters = [i] + list(fit_params)
        result = quadratic(*function_parameters)
        print(('Qubit Freq guess from fit: ', result))
        qbrick.set_frequency(result + default_sideband)
    
             
    '''Here we do an SSB spec'''
    from scripts.single_qubit import ssbspec
    seq = sequencer.Trigger(250)        
    spec = ssbspec.SSBSpec(qubit_info, ssbspec_freqs, seq=seq, plot_seqs=False)
    spec.measure()
    drive_freq = qbrick.do_get_frequency()
    w_q[i] = ssbspec_freqs[np.argmin(spec.get_ys())] + drive_freq - default_sideband

    qbrick.set_frequency(w_q[i] + default_sideband)
    
    
#    qbrick.set_frequency(w_q[i] + 100e6)
#    qbrick.set_frequency(result + 100e6)
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

Yoko.do_set_current(0)
    

