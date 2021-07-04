# -*- coding: utf-8 -*-
"""
Created on Tue May 14 16:24:58 2019

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 11:20:37 2019

@author: Wang_Lab
"""

#This spectroscopy is intended to follow one specific transition over the full flux period and not to get the full spectrum of the device. It makes use of SSB spec rather than the regular spectroscopy
#with the hope that we can avoid the current crashing problem. -Ebru



import mclient
import importlib
importlib.reload(mclient)
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




qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
ge = mclient.instruments['qubit1ge']
dig = mclient.instruments['dig']
SC_SShift = mclient.instruments['SC_SShift']
qbrick = mclient.instruments['QK']


#ef_info = mclient.get_qubit_info('qubit1ef')
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')
os.chdir(r'C:/qrlab/scripts')

qubit_drive_freq = 944.510e6
current = 2.0825e-3
#start_current = 1.99e-3  #This is the flux point in question for the frequency above




detunings =[] 
rabi_results = np.array([])


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
T1_Ypoints = np.array([])

#T1_Xpoints = np.concatenate(np.linspace(0.1e3, 1.9e3, 19), np.linspace(2e3, 20e3, 36))

pi_amp=[]



from single_qubit import ssbspec_lorentzianfit
from single_qubit import contrast_check
from scripts.single_qubit import rabi
from scripts.single_qubit import T1measurement
from scripts.single_qubit import T2measurement


SC_SShift.set_frequency(900e6)

#We want to sweep the pump power from -5 to 10 dB for a fixed pump frequency.



qbrick.set_frequency(944.594e6)
#PUMP OFF
dig.do_set_naverages(1000)
SC_SShift.do_set_rf_on(False)
seq = sequencer.Trigger(600)
spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-8e6, 4e6, 81), seq=seq, plot_seqs=False, proj_func='phase')
spec.measure_keysight()
#plt.close()    
XS = spec.xs
YS = spec.get_ys()
width = spec.width()
height = spec.height
center = spec.center
detunings.append(center)


qbrick.set_frequency(944.510e6 + spec.center * 1e6)
#tr = rabi.Rabi(qubit_info, np.linspace(-0.6, 0.6, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
#                   update=False, proj_func='phase')
#
#data=tr.measure_keysight()      
#ge.set('pi_amp', tr.pi_amp)
#pi_amp.append(tr.pi_amp)
#rabi_results = np.hstack((rabi_results, tr.get_ys()))


qubit_info = mclient.get_qubit_info('qubit1ge')
dig.do_set_naverages(10000)

t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
                                     np.concatenate((np.linspace(0.0e3, 1.9e3, 20), np.linspace(2e3, 20e3, 36))), 
                                     double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None)
#t1 = T1measurement.T1Measurement(qubit_info, np.concatenate(np.linspace(0.1e3, 1.9e3, 19), np.linspace(2e3, 20e3, 36)), double_exp=True, generate=True, plot_seqs=False, proj_func='phase')
t1.measure_keysight()

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

T1_Ypoints = np.hstack((T1_Ypoints, t1.get_ys()))

#
#
#t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 25e3, 61), detune=0.1e6, double_freq=False, generate=True, proj_func='phase')
#t2.measure_keysight()
#t2_result.append(t2.fit_params['tau'].value)
#t2_err.append(t2.fit_params['tau'].stderr)
#t2_ofs.append(t2.fit_params['ofs'].value)
##t2_amp.append(t2.fit_params['amplitude'].value)
#
#
#t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 50e3, 101), detune=0.1e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True, proj_func='phase')
#t2.measure_keysight()
#t2Echo_result.append(t2.fit_params['tau'].value)
#t2Echo_err.append(t2.fit_params['tau'].stderr)
#t2Echo_ofs.append(t2.fit_params['ofs'].value)
##t2Echo_amp.append(t2.fit_params['amplitude'].value)
##This code strictly assumes that the first run is an accurate guess.




SC_SShift.do_set_rf_on(True)
#time.sleep(.01)   

for pump_power in [-5,-3,-1,1,3,5,7,10]:

    qbrick.set_frequency(944.510e6)
    SC_SShift.do_set_power(pump_power)
    dig.do_set_naverages(1000)
    
    seq = sequencer.Trigger(600)
    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-8e6, 4e6,81 ), seq=seq, plot_seqs=False, proj_func='phase')
    spec.measure_keysight()
    #plt.close()    
    XS = spec.xs
    YS = spec.get_ys()
    width = spec.width()
    height = spec.height
    center = spec.center
    detunings.append(center)
    
    qbrick.set_frequency(944.510e6 + spec.center * 1e6)
#    tr = rabi.Rabi(qubit_info, np.linspace(-0.6, 0.6, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
#                   update=False, proj_func='phase')
#    
#    data=tr.measure_keysight()      
#    ge.set('pi_amp', tr.pi_amp)
#    pi_amp.append(tr.pi_amp)
#    rabi_results = np.hstack((rabi_results, tr.get_ys()))
    
    qubit_info = mclient.get_qubit_info('qubit1ge')
    dig.do_set_naverages(10000)
    
    
    t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
                                         np.concatenate((np.linspace(0.1e3, 1.9e3, 19), np.linspace(2e3, 20e3, 36))), 
                                         double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None)
    #t1 = T1measurement.T1Measurement(qubit_info, np.concatenate(np.linspace(0.1e3, 1.9e3, 19), np.linspace(2e3, 20e3, 36)), double_exp=True, generate=True, plot_seqs=False, proj_func='phase')
    t1.measure_keysight()
    
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
    
    T1_Ypoints = np.hstack((T1_Ypoints, t1.get_ys()))
#    

















    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
    
    
    











    
    