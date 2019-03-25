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




qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
Yoko = mclient.instruments['Yoko']
qbrick = mclient.instruments['QK']
qubit_info = mclient.get_qubit_info('qubit1ge')
#ef_info = mclient.get_qubit_info('qubit1ef')
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')
os.chdir(r'C:/qrlab/scripts')

start_freq = 948.6e6
#start_freq = 1245.31e6 #This should not be a guess but some frequency previously confirmed to be the correct qubit freq at the given flux point.
stop_freq = 5000e6
#
start_current = 1.85e-3
#start_current = 1.99e-3  #This is the flux point in question for the frequency above
stop_current = 2.02e-3
current_step= 0.01e-3
Yoko.do_set_current(start_current)
qbrick.set_frequency(start_freq)
fxn_freq1D=[]
fxn_current=[]
fxn_ROpowers =[]

from single_qubit import ssbspec_lorentzianfit
from single_qubit import contrast_check

#def run_measurement():
##    if freqrange = None:
##        freqrange= 50e6
#    seq = sequencer.Trigger(600)
#    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-50e6, 50e6, 201), seq=seq, plot_seqs=False, proj_func='phase')
#    spec.measure_keysight()
#    
#    XS = spec.xs
#    YS = spec.get_ys()
#    width = spec.width()
#    height = spec.height
#    center = spec.center


QK_freq = start_freq
current = start_current
ROpower_initial = RObrick.do_get_power() 
sweep_pow = [-2, 2, -4, 4, -6, 6] #bunu linspace tarzi bir seye donusturmek gerekebilir

seq = sequencer.Trigger(600)
spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-30e6, 30e6, 141), seq=seq, plot_seqs=False, proj_func='phase')
spec.measure_keysight()
plt.close()
    
XS = spec.xs
YS = spec.get_ys()
width = spec.width()
height = spec.height
center = spec.center

#This code strictly assumes that the first run is an accurate guess.

#phase=np.asarray(YS[:])
#phase=phase[:,None].T
fxn_freq1D.append(QK_freq + spec.center * 1e6)
#fxn_freq = np.asarray(XS + QK_freq)
#fxn_freq=fxn_freq[:,None].T
fxn_current.append(current)
fxn_ROpowers.append(ROpower_initial)

QK_freq = QK_freq + spec.center * 1e6
qbrick.set_frequency(QK_freq)
#time.sleep(.01)   

while QK_freq < stop_freq and current < stop_current:
#    if current == 2e-3:
#        dig.do_set_naverages = 2000
    current = current + current_step
    Yoko.do_set_current(current)
#    time.sleep(.01)

    seq = sequencer.Trigger(600)
    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-30e6, 30e6, 141), seq=seq, plot_seqs=False, proj_func='phase')
    spec.measure_keysight()
    plt.close()
    
    XS = spec.xs
    YS = spec.get_ys()
    width = spec.width()
    height = spec.height
    center = spec.center
   
    i=0
    
    while contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == False and i<(len(sweep_pow)): 
    #Here it should be trying to optimize the RO power and frequency to get the optimal contrast
    #Normally this will be done with histogramming, I will modify this once it is implemented to Keysight Dig
    
    #setting RO power to some other
        RObrick.do_set_power(ROpower_initial + sweep_pow[i])
        print(ROpower_initial + sweep_pow[i])
        seq = sequencer.Trigger(600)
        spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-30e6, 30e6, 141), seq=seq, plot_seqs=False, proj_func='phase')
        spec.measure_keysight()
        plt.close()
    
        XS = spec.xs
        YS = spec.get_ys()
        width = spec.width()
        height = spec.height
        center = spec.center
        
        contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None)
        i = i+1

    if contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == False:
        raise Exception('Could not get good contrast')  #BUNUN SONUNDA ILK RO POWERA DONMESINI ISTEMEM MANTIKLI OLABILIR

    if  contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == True:
        ROpower_initial = RObrick.do_get_power()  
        
#        phasenew=np.asarray(YS[:])
#        phasenew=phasenew[:,None].T
#        phase= np.concatenate([phase,phasenew])
#        fxn_freqnew = np.asarray(XS + QK_freq)
#        fxn_freqnew=fxn_freqnew[:,None].T
#        fxn_freq= np.concatenate([fxn_freq,fxn_freqnew])

        fxn_freq1D.append(QK_freq + spec.center * 1e6) #yoksa eksi mi?
        fxn_current.append(current)
        fxn_ROpowers.append(ROpower_initial)
        QK_freq = QK_freq + fxn_freq1D[len(fxn_freq1D)-1] - fxn_freq1D[len(fxn_freq1D) - 2] + spec.center * 1e6
        qbrick.set_frequency(QK_freq)
#        time.sleep(.01)
    
    


start_freq = 948.6e6
#start_freq = 1245.31e6 #This should not be a guess but some frequency previously confirmed to be the correct qubit freq at the given flux point.
stop_freq = 5000e6
#
start_current = 1.85e-3
#start_current = 1.99e-3  #This is the flux point in question for the frequency above
stop_current = 1.67e-3
current_step= -0.01e-3
Yoko.do_set_current(start_current)
qbrick.set_frequency(start_freq)
#fxn_freq1D=[]
#fxn_current=[]
#fxn_ROpowers =[]
#
##from single_qubit import ssbspec_lorentzianfit
##from single_qubit import contrast_check

#def run_measurement():
##    if freqrange = None:
##        freqrange= 50e6
#    seq = sequencer.Trigger(600)
#    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-50e6, 50e6, 201), seq=seq, plot_seqs=False, proj_func='phase')
#    spec.measure_keysight()
#    
#    XS = spec.xs
#    YS = spec.get_ys()
#    width = spec.width()
#    height = spec.height
#    center = spec.center


QK_freq = start_freq
current = start_current
ROpower_initial = -18
sweep_pow = [-2, 2, -4, 4, -6, 6] #bunu linspace tarzi bir seye donusturmek gerekebilir

seq = sequencer.Trigger(600)
spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-30e6, 30e6, 141), seq=seq, plot_seqs=False, proj_func='phase')
spec.measure_keysight()
plt.close()
    
XS = spec.xs
YS = spec.get_ys()
width = spec.width()
height = spec.height
center = spec.center

#This code strictly assumes that the first run is an accurate guess.

#phase=np.asarray(YS[:])
#phase=phase[:,None].T
fxn_freq1D.append(QK_freq + spec.center * 1e6)
#fxn_freq = np.asarray(XS + QK_freq)
#fxn_freq=fxn_freq[:,None].T
fxn_current.append(current)
fxn_ROpowers.append(ROpower_initial)

QK_freq = QK_freq + spec.center * 1e6
qbrick.set_frequency(QK_freq)
#time.sleep(.01)   

while QK_freq < stop_freq and current > stop_current:
#    if current == 2e-3:
#        dig.do_set_naverages = 2000
    current = current + current_step
    Yoko.do_set_current(current)
#    time.sleep(.01)

    seq = sequencer.Trigger(600)
    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-30e6, 30e6, 141), seq=seq, plot_seqs=False, proj_func='phase')
    spec.measure_keysight()
    plt.close()
    
    XS = spec.xs
    YS = spec.get_ys()
    width = spec.width()
    height = spec.height
    center = spec.center
   
    i=0
    
    while contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == False and i<(len(sweep_pow)): 
    #Here it should be trying to optimize the RO power and frequency to get the optimal contrast
    #Normally this will be done with histogramming, I will modify this once it is implemented to Keysight Dig
    
    #setting RO power to some other
        RObrick.do_set_power(ROpower_initial + sweep_pow[i])
        print(ROpower_initial + sweep_pow[i])
        seq = sequencer.Trigger(600)
        spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-30e6, 30e6, 141), seq=seq, plot_seqs=False, proj_func='phase')
        spec.measure_keysight()
        plt.close()
    
        XS = spec.xs
        YS = spec.get_ys()
        width = spec.width()
        height = spec.height
        center = spec.center
        
        contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None)
        i = i+1

    if contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == False:
        raise Exception('Could not get good contrast')  #BUNUN SONUNDA ILK RO POWERA DONMESINI ISTEMEM MANTIKLI OLABILIR

    if  contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == True:
        ROpower_initial = RObrick.do_get_power()  
        
#        phasenew=np.asarray(YS[:])
#        phasenew=phasenew[:,None].T
#        phase= np.concatenate([phase,phasenew])
#        fxn_freqnew = np.asarray(XS + QK_freq)
#        fxn_freqnew=fxn_freqnew[:,None].T
#        fxn_freq= np.concatenate([fxn_freq,fxn_freqnew])

        fxn_freq1D.append(QK_freq + spec.center * 1e6) #yoksa eksi mi?
        fxn_current.append(current)
        fxn_ROpowers.append(ROpower_initial)
        QK_freq = QK_freq + fxn_freq1D[len(fxn_freq1D)-1] - fxn_freq1D[len(fxn_freq1D) - 2] + spec.center * 1e6
        qbrick.set_frequency(QK_freq)
#        time.sleep(.01)























    
plt.figure()

#plt.plot(ramp_currents, fxn_freq)
#    results.append(spec.ampdata[0,:])
##    results.append(spec.get_ys())
#    min_result.append(np.min(spec.ampdata[0,:]))
#    plt.close()


#X, Y = np.meshgrid(fxn_current, XS)
#Y =np.transpose(fxn_freq)
#X=X*1000
#Y=Y/float(1E9)
#Z = np.transpose(phase)


plt.plot(fxn_current, fxn_freq1D)           #I don't know why I insisted on having a color plot, it's not really necessary if I am just following one transition. I can add height as a 3rd parameter later. 
##plt.pcolormesh(X, Y, Z)
#plt.colorbar()
#plt.xlabel('Coil Current (mA)')
#plt.ylabel('Frequency (GHZ)')
#plt.show()
#to_save = [X, Y, Z]
#
#    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
    
    
    











    
    