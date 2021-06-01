# -*- coding: utf-8 -*-
"""
Created on Sat May 22 19:43:53 2021

@author: wanglab
"""

import mclient
#reload(mclient)
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
import pandas as pd


from scripts.single_qubit import ssbspec_lorentzianfit
from scripts.single_qubit import contrast_check
from scripts.single_qubit import rabi
from scripts.single_qubit import T1measurement
from scripts.single_qubit import T2measurement
from scripts.single_qubit import ssbspec


qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
yoko = mclient.instruments['yoko']
qbrick = mclient.instruments['gaius01']
qubit_info = mclient.get_qubit_info('qubit1ge')
ge = mclient.instruments['qubit1ge']
dig = mclient.instruments['dig']
os.chdir(r'C:/qrlab/scripts')




from scripts.single_qubit import ssbspec



alz.set_naverages(20000)
#fig, axes = plt.subplots(nrows=2, ncols=1)
coolFreqs = np.linspace(3.5, 3.6, 100)*1e9
coolFreqs = np.linspace(3.52, 3.53, 100)*1e9
coolFreqs = np.linspace(3, 4, 2000)*1e9
coolFreqs = np.linspace(3.377, 3.379, 20)*1e9
coolPows = [10]
for i, coolFreq in enumerate(coolFreqs):
    for j, coolPow in enumerate(coolPows):
        for _ in range(1):
            cool.set_power(coolPow)
            cool.set_frequency(coolFreq)
            #time.sleep(5)
            
            coolcool = sequencer.Constant(int(5e3),1,chan='3m1')
            seq_cool = sequencer.Join([sequencer.Trigger(250), coolcool, sequencer.Delay(150)])
            
            
            
            
            spec = ssbspec.SSBSpec(qubit_info, np.array([-0.422, -0.029]*2), proj_func='phase', 
                                   seq=seq_cool, extra_info=qubit_info2)
            spec.measure()
            plt.close(spec.fig)
            
            leftPeak = np.mean(spec.get_ys()[::2])
            rightPeak = np.mean(spec.get_ys()[1::2])
            
            detunings = -spec.detunings[:2]
            
            axes[0].plot(coolFreq, leftPeak, marker='o', ls='', color='r', fillstyle='none')
            axes[1].plot(coolFreq, rightPeak, marker='o', ls='', color='b', fillstyle='none')
            fig.canvas.draw()
            
            
#%%
            
            

alz.set_naverages(5000)
Nx = 71
Xpts = np.linspace(-0.5e6, 1e6, Nx)+0.5e6
fig, ax = plt.subplots(nrows=1, ncols=1)
coolFreqs = np.linspace(3.5, 3.6, 100)*1e9
coolFreqs = np.linspace(3.52, 3.53, 100)*1e9
coolFreqs = np.linspace(3, 4, 2000)*1e9
coolFreqs = np.linspace(3.3778, 3.3779, 20)*1e9+3e6
coolFreqs = np.arange(3.38, 3.45, 0.001)*1e9
coolPow = 10

ssbData = np.ones((coolFreqs.shape[0], Nx))*np.NaN
xx, yy = np.meshgrid(Xpts, coolFreqs)
for i, coolFreq in enumerate(coolFreqs):
    for _ in range(1):
        cool.set_power(coolPow)
        cool.set_frequency(coolFreq)
        #time.sleep(5)
        
        coolcool = sequencer.Constant(int(10e3),1,chan='3m1')
        seq_cool = sequencer.Join([sequencer.Trigger(250), coolcool, sequencer.Delay(150)])
        
        
        
        
        spec = ssbspec.SSBSpec(qubit_info, Xpts, proj_func='phase', 
                               seq=seq_cool, extra_info=qubit_info2)
        spec.measure()
        plt.close(spec.fig)
        
        Y = spec.get_ys()
        
        ssbData[i] = Y
        
        ax.pcolormesh(xx, yy, ssbData)
        
        
        fig.canvas.draw()
        
      
#%%
            
from scripts.single_qubit import rabi
       

alz.set_naverages(10000)
Nx = 31
Xpts = np.linspace(-1, 1, Nx)
fig, ax = plt.subplots(nrows=1, ncols=1)
coolFreqs = np.linspace(3.5, 3.6, 100)*1e9
coolFreqs = np.linspace(3.52, 3.53, 100)*1e9
coolFreqs = np.linspace(3, 4, 2000)*1e9
coolFreqs = np.linspace(3.3778, 3.3779, 20)*1e9+3e6
coolFreqs = np.arange(3.2, 3.6, 0.002)*1e9
coolPow = 19

trData = np.ones((coolFreqs.shape[0], Nx))*np.NaN
xx, yy = np.meshgrid(Xpts, coolFreqs)
for i, coolFreq in enumerate(coolFreqs):
    for _ in range(1):
        cool.set_power(coolPow)
        cool.set_frequency(coolFreq)
        #time.sleep(5)
        
        coolcool = sequencer.Constant(int(10e3),1,chan='3m1')
        seq_cool = sequencer.Join([sequencer.Trigger(250), coolcool, sequencer.Delay(150)])
        
        
        tr = rabi.Rabi(qubit_info, Xpts, selective=False,
                #                   np.linspace(0.75, 0.95, 101), selective=False,
                #                           np.linspace(-0.2, 0.2, 61), selective=True,
                                   plot_seqs=False, generate=True, repeat_pulse=1,  #n=3 has a bug
                                   update=True, seq=seq_cool,
                                   postseq=None, proj_func='phase', extra_info=[gate_info1, gate_info2])
        tr.measure()
        plt.close(tr.fig)
        
        Y = tr.get_ys()
        
        trData[i] = Y
        
        ax.pcolormesh(xx, yy, trData)
        
        
        fig.canvas.draw()
        