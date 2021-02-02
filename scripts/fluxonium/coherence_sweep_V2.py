# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 11:20:37 2019

@author: Wang_Lab
"""

#This spectroscopy is intended to follow one specific transition over the full flux period and not to get the full spectrum of the device. It makes use of SSB spec rather than the regular spectroscopy
#with the hope that we can avoid the current crashing problem. -Ebru



import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
#matplotlib.rcParams['backend'] = 'Qt4Agg'
#matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
#from t1t2_plotting import smart_T1_delays
from pulseseq import sequencer, pulselib
import os
import time
import math
import datetime

fxn_freq1D=[]
fxn_current=[]
fxn_ROpowers =[]
t1_result = []
t1_result2=[]
t1_err = []
t1_err2 =[]
t1_ofs = []
t1_ofs_err = []
t1_amp = []
t1_amp_err = []
t1_amp2 = []
t1_amp2_err = []
t2_result =[]
t2_err=[]
t2_amp = []
t2_ofs=[]
t2Echo_result=[]
t2Echo_err=[]
t2Echo_amp=[]
t2Echo_ofs=[]
T1_Ypoints = []
T2_Ypoints = []
T2E_Ypoints = []

pi_amp=[]


qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
yoko = mclient.instruments['yoko']
qbrick = mclient.instruments['']
qubit_info = mclient.get_qubit_info('qubit1ge')
ge = mclient.instruments['qubit1ge']
dig = mclient.instruments['dig']
os.chdir(r'C:/qrlab/scripts')

#current_list=[-1.14,-1.119,-0.8993, -0.8, -0.5592, -0.4192, -0.320, -0.1789, -0.05849, 0.100, 0.381, 0.8606]
#freq= [3.192e+09, 3.235e+09, 3.859e+09, 4.108e+09, 4.656e+09,
#       4.883e+09, 5.024e+09, 5.197e+09, 5.29e+09,
#       5.389e+09, 5.532e+09, 5.675e+09]
#

current_list=[-1.317, -1.338, -1.398, -1.478, -1.52, -1.76, -1.819]
freq= [
       2.65e+09, 2.58e+09, 2.39e+09, 2.17e+09,
       2.04e+09, 1.31e+09, 1.16e+09]

for i in range(len(current_list)):
    yoko.do_ramp_current(current_list[i])
    qbrick.set_frequency(freq[i])
    #T1_Xpoints = np.concatenate(np.linspace(0.1e3, 1.9e3, 19), np.linspace(2e3, 20e3, 36))
    

    
    

    from single_qubit import ssbspec_lorentzianfit
    from single_qubit import contrast_check
    from scripts.single_qubit import rabi
    from scripts.single_qubit import T1measurement
    from scripts.single_qubit import T2measurement

    dig.do_set_naverages(6000)
    QK_freq = freq[i]
    current = current_list[i]
    ROpower_initial = 5 
    sweep_pow = [5, 0, -5] #bunu linspace tarzi bir seye donusturmek gerekebilir

    seq = sequencer.Trigger(600)
    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-40e6, 40e6, 181), seq=None, plot_seqs=False, proj_func='phase')
    spec.measure()
    #plt.close()
        
    XS = spec.xs
    YS = spec.get_ys()
    width = spec.width()
    height = spec.height
    center = spec.center
    
    QK_freq = QK_freq + spec.center * 1e6
    qbrick.set_frequency(QK_freq)
    
    tr = rabi.Rabi(qubit_info, np.linspace(-0.25, 0.25, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1, seq=None,
                       update=False, proj_func='phase')
    
    data=tr.measure()      
    ge.set('pi_amp', tr.pi_amp)
    pi_amp.append(tr.pi_amp)
    
    qubit_info = mclient.get_qubit_info('qubit1ge')
    
    dig.do_set_naverages(5000)
    
    t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
                                         np.concatenate((np.linspace(0.1e3, 0.9e3, 15), np.linspace(1e3, 10e3, 41), np.linspace(11e3, 30e3, 20))), 
                                         double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None)
    t1.measure()
    
    t1_result.append(t1.fit_params['tau'].value)
    t1_err.append(t1.fit_params['tau'].stderr)
    t1_ofs.append(t1.fit_params['ofs'].value)
    t1_ofs_err.append(t1.fit_params['ofs'].stderr)
    t1_amp.append(t1.fit_params['amplitude'].value)
    t1_amp_err.append(t1.fit_params['amplitude'].stderr)
    t1_amp2.append(t1.fit_params['amplitude2'].value)
    t1_amp2_err.append(t1.fit_params['amplitude2'].stderr)
    t1_result2.append(t1.fit_params['tau2'].value)
    t1_err2.append(t1.fit_params['tau2'].stderr)
    T1_Ypoints.append(t1.get_ys())
    
    
    
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 2e3, 101), detune=1e6, double_freq=False, generate=True, 
                                             seq=None,  postseq=None, proj_func='phase')
    t2.measure()
    t2_result.append(t2.fit_params['tau'].value)
    t2_err.append(t2.fit_params['tau'].stderr)
    t2_ofs.append(t2.fit_params['ofs'].value)
    T2_Ypoints.append(t2.get_ys())
    
    
    t2_amp.append(t2.fit_params['amp'].value)
    
    
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(10, 4e3, 101), detune=1e6, echotype = T2measurement.ECHO_HAHN, necho=1, seq=None, plot_seqs = False, generate=True, proj_func='phase')
    t2.measure()
    t2Echo_result.append(t2.fit_params['tau'].value)
    t2Echo_err.append(t2.fit_params['tau'].stderr)
    t2Echo_ofs.append(t2.fit_params['ofs'].value)
    t2Echo_amp.append(t2.fit_params['amp'].value)
    T2E_Ypoints.append(t2.get_ys())

##This code strictly assumes that the first run is an accurate guess.
    dig.do_set_naverages(5000)
    
    #phase=np.asarray(YS[:])
    #phase=phase[:,None].T
    fxn_freq1D.append(QK_freq)
    #fxn_freq = np.asarray(XS + QK_freq)
    #fxn_freq=fxn_freq[:,None].T
    fxn_current.append(current)
    fxn_ROpowers.append(ROpower_initial)
    

    
    
    
        
    plt.figure()

#plt.plot(ramp_currents, fxn_freq)
#    results.append(spec.ampdata[0,:])
##    results.append(spec.get_ys())
#    min_result.append(np.min(spec.ampdata[0,:]))
#    plt.close()


X, Y = np.meshgrid(fxn_current, XS)
X=fxn_current
Y = np.concatenate((np.linspace(0.1e3, 0.9e3, 15), np.linspace(1e3, 10e3, 41), np.linspace(11e3, 30e3, 20)))
X=X*1000
Y=Y/float(1E9)
Z = np.transpose(T1_Ypoints)





plt.plot(fxn_current, fxn_freq1D)           #I don't know why I insisted on having a color plot, it's not really necessary if I am just following one transition. I can add height as a 3rd parameter later. 
plt.pcolormesh(X, Y, Z)
#plt.colorbar()
#plt.xlabel('Coil Current (mA)')
#plt.ylabel('Frequency (GHZ)')
#plt.show()
#to_save = [X, Y, Z]
#
#    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
    
    
    











    
    