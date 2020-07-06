# -*- coding: utf-8 -*-
"""
Created on Mon May 20 17:16:46 2019

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 11:20:37 2019

@author: Wang_Lab
"""


import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
import matplotlib.pyplot as plt
from pulseseq import sequencer, pulselib
import os
import time
import math
import datetime




qubits = mclient.get_qubits()
Yoko = mclient.instruments['Yoko']
qbrick = mclient.instruments['QK']
qbrickef = mclient.instruments['efBrick']
qubit_info = mclient.get_qubit_info('qubit1ge')
ge = mclient.instruments['qubit1ge']
dig = mclient.instruments['dig']

ef_info = mclient.get_qubit_info('qubit1ef')
ef = mclient.instruments['qubit1ef']
os.chdir(r'C:/qrlab/scripts')



if 0: #Adding cooling sequence - seq=seq needs to be modified in the measurements below 
    cool_time=30e3
    cool = sequencer.Combined([sequencer.Constant(int(cool_time), 0.04, chan=ef_info.sideband_channels[0]),
                           sequencer.Constant(int(cool_time), 0.04, chan=ef_info.sideband_channels[1]),
                           sequencer.Constant(int(cool_time), 1, chan='3m1')])
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])



start_freq = 5.31575e08
start_freq_ef = 3.84048e09
#start_freq = 5.343206700729643106e+08

stop_freq = 7000e6     #This can usually be anything that is sufficiently large enough.


#start_current = 0.045e-3  #This is in units of A, so there should be a 1e-3 if we are working with mA's.
start_current = 0.006e-3
stop_current = -0.046e-3
current_step= -0.001e-3

dig_avg_num_rough = 6000 #Dig naverages for less fine runs, i.e. SSBspec and Rabi
dig_avg_num_fine1 = 6000 #Dig averages for finer purposes, i.e. T1, T2
dig_avg_num_fine2 = 10000
Yoko.do_set_current(start_current)
qbrick.set_frequency(start_freq)
qbrickef.set_frequency(start_freq_ef)

fxn_freq1D=[] 
fxn_freq1D_ef =[]     #list of arrays 
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
ft1_result = []
ft1_result2=[]
ft1_err = []
ft1_err2 =[]
ft1_ofs = []
ft1_ofs_err = []
ft1_amp = []
ft1_amp_err = []
ft1_amp2 = []
ft1_amp2_err = []

pi_amp=[]


t2Echo_ofs=[]

T1_Ypoints = []
FT1_Ypoints = []


from single_qubit import ssbspec_lorentzianfit
from single_qubit import contrast_check
from scripts.single_qubit import rabi
from scripts.single_qubit import T1measurement
from scripts.single_qubit import T2measurement
from single_qubit import FT1measurement
from scripts.single_qubit import efrabi




dig.do_set_naverages(dig_avg_num_rough)
QK_freq = start_freq
efbrick_freq = start_freq_ef
current = start_current
ROpower_initial = -5             #This is not automatic but for bookkeeping, it starts iterating with whatever RO power is there on the gui.  
sweep_pow = [-2, 2, -4, 4, -6, 6] 

seq = sequencer.Trigger(600)
spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-15e6, 15e6, 81), seq=None, plot_seqs=False, proj_func='phase')
spec.measure_keysight()

    
XS = spec.xs
YS = spec.get_ys()
width = spec.width()
height = spec.height
center = spec.center

QK_freq = QK_freq + spec.center * 1e6
qbrick.set_frequency(QK_freq)


if 1: #If we only want a frequency track wrt flux sweep, keep it 0.
    dig.do_set_naverages(dig_avg_num_fine1)
    tr = rabi.Rabi(qubit_info, np.linspace(-0.7, 0.7, 71), plot_seqs=False, generate=True, selective=False, repeat_pulse=1, seq=None,
                   update=False, proj_func='phase')


    data=tr.measure_keysight()    

    ge.set('pi_amp', tr.pi_amp)
    qubit_info = mclient.get_qubit_info('qubit1ge')
    pi_amp.append(tr.pi_amp)

#

    #T1 with 50 additional calibration points at the beginning
    dig.do_set_naverages(dig_avg_num_fine2)
    t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
                                     np.concatenate((np.linspace(0,0,50), np.linspace(0.1e3, 1.9e3, 31), np.linspace(2e3, 20e3, 46), np.linspace(20.1e3, 80e3, 16))), 
                                     double_exp=False, generate=True, plot_seqs=False, proj_func='phase', seq=None) 



#   T1 with no additional calibration points
#    t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
#        #                                     np.concatenate((np.linspace(0.1e3, 1.9e3, 31), np.linspace(2e3, 20e3, 56), np.linspace(21e3, 450e3, 60))),
#                                             np.concatenate((np.linspace(0.1e3, 1e3, 41), np.linspace(1.01e3, 15e3, 76))),
#                                             double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None)  
    t1.measure_keysight()
    
    t1_result.append(t1.fit_params['tau'].value)
    t1_err.append(t1.fit_params['tau'].stderr)
    t1_ofs.append(t1.fit_params['ofs'].value)
    t1_ofs_err.append(t1.fit_params['ofs'].stderr)
    t1_amp.append(t1.fit_params['amplitude'].value)
    t1_amp_err.append(t1.fit_params['amplitude'].stderr)
#    t1_amp2.append(t1.fit_params['amplitude2'].value)
#    t1_amp2_err.append(t1.fit_params['amplitude2'].stderr)
#    t1_result2.append(t1.fit_params['tau2'].value)
#    t1_err2.append(t1.fit_params['tau2'].stderr)
    T1_Ypoints.append(t1.get_ys())

    fxn_freq1D.append(QK_freq)
    fxn_current.append(current)
    fxn_ROpowers.append(ROpower_initial)

    
    dig.do_set_naverages(dig_avg_num_rough)


    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(ef_info, np.linspace(-30e6, 30e6, 71), seq=None, postseq = None, extra_info=qubit_info, plot_seqs=False, generate=True, proj_func='phase')
    spec.measure_keysight()

    XS = spec.xs
    YS = spec.get_ys()
    width = spec.width()
    height = spec.height
    center = spec.center

    efbrick_freq = efbrick_freq  + spec.center * 1e6
    qbrickef.set_frequency(efbrick_freq )





#    dig.do_set_naverages(dig_avg_num_fine)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-1, 1, 81), first_pi=False,second_pi=False, seq=None, generate=True, update=True,
                            proj_func='phase')
    efr.measure_keysight()

    ef_info = mclient.get_qubit_info('qubit1ef')
    ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.concatenate((np.linspace(0,0,50), np.linspace(0, 1e3, 31), np.linspace(1.01e3, 5e3, 31))), seq=None, proj_func='phase')
    ft1.measure_keysight()
    
    ft1_result.append(ft1.fit_params['tau'].value)
    ft1_err.append(ft1.fit_params['tau'].stderr)
    ft1_ofs.append(ft1.fit_params['ofs'].value)
    ft1_ofs_err.append(ft1.fit_params['ofs'].stderr)
    ft1_amp.append(ft1.fit_params['amplitude'].value)
    ft1_amp_err.append(ft1.fit_params['amplitude'].stderr)
    FT1_Ypoints.append(ft1.get_ys())

    fxn_freq1D_ef.append(efbrick_freq)





    while QK_freq < stop_freq and current > stop_current:

        current = current + current_step
        Yoko.do_set_current(current)
    
        seq = sequencer.Trigger(600)
        spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-15e6, 15e6, 81), seq=None, plot_seqs=False, proj_func='phase')
        spec.measure_keysight()
    
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
            spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-15e6, 15e6, 81), seq=None, plot_seqs=False, proj_func='phase')
            spec.measure_keysight()
    #        plt.close()
        
            XS = spec.xs
            YS = spec.get_ys()
            width = spec.width()
            height = spec.height
            center = spec.center
            
            contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None)
            i = i+1
    
        if contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == False:
            raise Exception('Could not get good contrast') 
    
        if  contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == True:
            ROpower_initial = RObrick.do_get_power()
            
            QK_freq = QK_freq + spec.center * 1e6
            qbrick.set_frequency(QK_freq)
        

        if 1: #If we only want a frequency track wrt flux sweep, keep it 0.
            dig.do_set_naverages(dig_avg_num_fine1)
            tr = rabi.Rabi(qubit_info, np.linspace(-0.7, 0.7, 71), plot_seqs=False, generate=True, selective=False, repeat_pulse=1, seq=None,
                       update=False, proj_func='phase')
        
            data=tr.measure_keysight()      
            if tr.pi_amp < (ge.get_pi_amp()/2):
                pi_amp.append(ge.get_pi_amp())
            else: 
                ge.set('pi_amp', tr.pi_amp)
                qubit_info = mclient.get_qubit_info('qubit1ge')
                pi_amp.append(tr.pi_amp)
    
    
    
    
            #T1 with 50 additional calibration points at the beginning
            dig.do_set_naverages(dig_avg_num_fine2)
            t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
                                     np.concatenate((np.linspace(0,0,50), np.linspace(0.1e3, 1.9e3, 31), np.linspace(2e3, 20e3, 46), np.linspace(20.1e3, 80e3, 16))), 
                                     double_exp=False, generate=True, plot_seqs=False, proj_func='phase', seq=None) 
        
        
        
        #   T1 with no additional calibration points
        #    t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
        #        #                                     np.concatenate((np.linspace(0.1e3, 1.9e3, 31), np.linspace(2e3, 20e3, 56), np.linspace(21e3, 450e3, 60))),
        #                                             np.concatenate((np.linspace(0.1e3, 1e3, 41), np.linspace(1.01e3, 15e3, 76))),
        #                                             double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None)  
            t1.measure_keysight()
            
            t1_result.append(t1.fit_params['tau'].value)
            t1_err.append(t1.fit_params['tau'].stderr)
            t1_ofs.append(t1.fit_params['ofs'].value)
            t1_ofs_err.append(t1.fit_params['ofs'].stderr)
            t1_amp.append(t1.fit_params['amplitude'].value)
            t1_amp_err.append(t1.fit_params['amplitude'].stderr)
            T1_Ypoints.append(t1.get_ys())
            
            dig.do_set_naverages(dig_avg_num_rough)
            
            fxn_freq1D.append(QK_freq)
            fxn_current.append(current)
            fxn_ROpowers.append(ROpower_initial)
            
            spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(ef_info, np.linspace(-30e6, 30e6, 71), seq=None, postseq = None, extra_info=qubit_info, plot_seqs=False, generate=True, proj_func='phase')
            spec.measure_keysight()

            XS = spec.xs
            YS = spec.get_ys()
            width = spec.width()
            height = spec.height
            center = spec.center
    
            efbrick_freq = efbrick_freq  + spec.center * 1e6
            qbrickef.set_frequency(efbrick_freq )
    
    
    
    
    
#            dig.do_set_naverages(dig_avg_num_rough)
            efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-1, 1, 81), first_pi=False,second_pi=False, seq=None, generate=True, update=True,
                                proj_func='phase')
            efr.measure_keysight()
    
            ef_info = mclient.get_qubit_info('qubit1ef')
            ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.concatenate((np.linspace(0,0,50), np.linspace(0, 1e3, 31), np.linspace(1.01e3, 5e3, 31))), seq=None, proj_func='phase')
            ft1.measure_keysight()
        
            ft1_result.append(ft1.fit_params['tau'].value)
            ft1_err.append(ft1.fit_params['tau'].stderr)
            ft1_ofs.append(ft1.fit_params['ofs'].value)
            ft1_ofs_err.append(ft1.fit_params['ofs'].stderr)
            ft1_amp.append(ft1.fit_params['amplitude'].value)
            ft1_amp_err.append(ft1.fit_params['amplitude'].stderr)
            FT1_Ypoints.append(ft1.get_ys())
    
            fxn_freq1D_ef.append(efbrick_freq)


            plt.close('all')
    



plt.plot(fxn_current, fxn_freq1D)
plt.plot(fxn_current, fxn_freq1D_ef)
 

















