# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 14:37:03 2020

@author: wanglab
"""

import mclient
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib.pyplot as plt
import os
os.chdir(r'c:\qrlab')

alz = mclient.instruments['alazar']
gaius01 = mclient.instruments['gaius01']
coolgen= mclient.instruments['cool']
ZZ = mclient.instruments['ZZ']

#qubits = mclient.get_qubits()
#qubit_info = mclient.get_qubit_info('qubit1ge')
#qubit_info2 = mclient.get_qubit_info('qubit1ge_2')
#qubit2_info = mclient.get_qubit_info('qubit2ge')
#qubit2_info2 = mclient.get_qubit_info('qubit2ge_2')
gate_info1 = mclient.get_gate_info('sq_gate1')
gate_info2 = mclient.get_gate_info('sq_gate2')
#zx90_info = mclient.get_gate_info('zx90_gate')

from scripts.single_qubit import ssbspec
from scripts.single_qubit import ssbspec_gaussianfit

from scripts.single_qubit import rabi
from scripts.single_qubit import drag_test
from scripts.fluxonium  import timerabi_interleaved
from scripts.fluxonium import CRtuning_time_phase
from scripts.fluxonium import CRtuning_time_amp
from scripts.single_qubit import timerabi
from scripts.fluxonium import CRtuning_timevsdet
from scripts.single_qubit import geophasecal_zx90
from scripts.single_qubit import Pi_train
from scripts.single_qubit import Pi2_train
cancel_info = mclient.get_gate_info('cancel_gate')



cool = sequencer.Constant(int(4e3),1,chan='3m1')
seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])



#This code assumes that we are done with qubit_info's, things have been tuned up
#in detail in prior and we are particularly focused on tuning things up 
#for the ZX90 echo scheme

#We currently use:
#gate1 = 4*3 + 12
#gate2 = 6*3 + 6


def Drag_test(qubit_info):   
    dtest = drag_test.drag_test(qubit_info, np.linspace(-0.5, 0.5, 51), plot_seqs=False, generate=True, proj_func='phase', seq=seq_cool)
    data=dtest.measure()

def qubit1_gate_check(amp, rel_amp, rel_phase):

    tr = timerabi_interleaved.TimeRabi_interleaved(gate_info1, gate_info2, np.linspace(0, 250,151), #Does not include Gaussian ramp time, sigma=4
            amp=amp, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, sigma=4,
            update=False, seq=seq_cool, postseq=None, proj_func='phase')
    data = tr.measure()
    return



def qubit2_gate_check(amp, range):
    alz.set_naverages(5000)
    rel_amp=0
    rel_phase = 0
    tr = timerabi_interleaved.TimeRabi_interleaved(
            gate_info2, gate_info1, range, #Does not include Gaussian ramp time, sigma=4
            amp, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, sigma=6,
            update=False, read_on_e=True, seq=seq_cool, postseq=None, proj_func='phase')
    data = tr.measure()
    return


def CX_timerabis(rotation_range, gate_info1, gate_info2, time_range, amp, rel_amp,rel_phase, all_axis=False, swap_chs=False, repeat_pulse=1):
    alz.set_naverages(1000)
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])     
    for R in rotation_range:
        X_proj = gate_info1.rotate(np.pi/2, np.pi/2+R)
        Y_proj = gate_info1.rotate(np.pi/2, R)
        if all_axis== False:
            for postseq in [None]:
                tr = timerabi_interleaved.TimeRabi_interleaved(
                    gate_info1, gate_info2, time_range, #Does not include Gaussian ramp time, sigma=4
                    amp=amp, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, sigma=6, read_on_e=True, cancel_info=cancel_info,
                    update=False, seq=seq_cool,repeat_pulse=repeat_pulse, postseq=postseq, proj_func='phase', swap_chs = swap_chs)#,extra_info=gate_info1)
                data = tr.measure()
        if all_axis == True:
            for postseq in [None, X_proj, Y_proj]:
                tr = timerabi_interleaved.TimeRabi_interleaved(
                    gate_info1, gate_info2, time_range, #Does not include Gaussian ramp time, sigma=4
                    amp=amp, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, sigma=6, read_on_e=True, cancel_info=cancel_info,
                    update=False, seq=seq_cool, repeat_pulse=repeat_pulse, postseq=postseq, proj_func='phase', swap_chs= swap_chs)#,extra_info=gate_info1)
                data = tr.measure()
    return         



def relative_phase_qubit1(amp, rel_amp, timerange, phase_range, control_pi=False):
    cr_tune = CRtuning_time_phase.CRtuning_time_phase(gate_info1, gate_info2, 
                                                    timerange, phase_range, 
                amp=amp, phase=0, rel_amp=rel_amp, sigma=4, seq=seq_cool, postseq=None, 
                control_pi=False, proj_func='phase' ,extra_info=gate_info2)    
    data = cr_tune.measure()
    return


def relative_amp_qubit1(amp, rel_phase, timerange, amp_range, control_pi=False):
    cr_tune = CRtuning_time_amp.CRtuning_time_amp(gate_info1, gate_info2, 
                                                    timerange, amp_range, 
                amp=amp, phase=0, rel_phase=1, sigma=4, seq=seq_cool, postseq=None, 
                control_pi=False, proj_func='phase', extra_info=gate_info2)    
    data = cr_tune.measure()
    return

def detuning_qubit1(amp,rel_amp,  rel_phase, time_range, det_range, control_pi=True):
    cr_tune = CRtuning_timevsdet.CRtuning_timevsdet(qubit_info, qubit_info2, qubit2_info2, 
                                                    time_range, det_range, 
                amp, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, sigma=4, update=False, 
                seq=seq_cool, fix_phase=True, fix_period=None, control_pi=True, proj_func='phase')    
    
    data = cr_tune.measure()
    return

def zx_amplitude(range, repeat_pulse):
    alz.set_naverages(5000)
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info2.rotate(np.pi,0)])
    tr1 = rabi.Rabi(zx90_info,range, selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=repeat_pulse,
                                   update=False, seq=seq_cool, postseq=None, proj_func='phase',
                                   extra_info=gate_info2
                                   )
    data=tr1.measure()    
    return

def pi_amp_tune(gate_info, range, repeat_pulse):

    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)]) #gate_info1.rotate(np.pi,0)])
    p = Pi_train.Pi_train(gate_info, range, seq=seq_cool, postseq=None, repeat_pulse=repeat_pulse, proj_func='phase',
                          extra_info=gate_info1
                          )
    p.measure()
    return

def pi2_amp_tune(gate_info, range, repeat_pulse): 
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)]) #gate_info1.rotate(np.pi,0)])
    p = Pi2_train.Pi2_train(gate_info, range, seq=seq_cool, postseq=None, repeat_pulse=repeat_pulse, proj_func='phase')
#                            extra_info=gate_info1
    p.measure()
    return


#------------------------------------------------------------------------------------------------------------


#Checking how well the single qubit gates are doing    

if 0:
    
    qubit1_gate_check(0.08, 1.06, 1.06)  #correct this
    qubit2_gate_check(0.3, np.linspace(0, 150, 151))
    bla
#ramsey?

#CX tune up check
if 0:
    CX_timerabis(np.linspace(0,0,1), gate_info1, gate_info2 ,np.linspace(0,300,151), 0.08, 4.452, 1.05, all_axis=False)

#CX tune up
if 0:  #change range +- the current value
    relative_phase_qubit1(0.08, 4.45, np.linspace(1,300,31), np.linspace(0.95,1.1,11), control_pi=False)
#    relative_amp_qubit1(0.079, 1.0,  np.linspace(1,300,31), np.linspace(4.35,4.55,11), control_pi=False)

    
#Single qubit tune up for qubit1:
if 0: #this one is still using the qubit_info objects since it runs a detuned sum - gaussian 
#    detuning_qubit1(0.079,4.452, 1.004, np.linspace(0,300,31),np.linspace(-5e6, 5e6, 11) , control_pi=True)
    #driving from 5/6 with control in g and e:
    CX_timerabis(np.linspace(0,-0.8,1), gate_info1, gate_info2 ,np.linspace(0,200,151), 0.077613, 0.000, 0, all_axis=False, swap_chs = False)
#    #driving from 9/10 with control in g and e:
    CX_timerabis(np.linspace(0,-0.8,1), gate_info1, gate_info2,np.linspace(0,200,151), 0.354502, 0.000, 0, all_axis=False, swap_chs = True)


#    #calculation will go in here  + I CAN'T SEE WHERE IT GETS THE PI TIME FROM, IT IS NOT EXACTLY PERIOD/2??
# ([1/pitime_56(g) - 1/pitime_56(e)] / [1/pitime_910(g) - 1/pitime_910(e)]) * rel_amp_910 / rel_amp_56 = effective amp for the single qubit gate 

#    qubit1_gate_check(0.79, 1.015, 1.004)
#Single qubit gate pi amp, pi/2 amp and drag tune up

if 0:  #center around the current value
    pi_amp_tune(gate_info1, np.linspace(0.073, 0.078, 61), repeat_pulse=5)
    pi2_amp_tune(gate_info1, np.linspace(0.037, 0.038, 61), repeat_pulse=12)
#    pi_amp_tune(gate_info2, np.linspace(0.3, 0.31, 61), repeat_pulse=5)
#    pi2_amp_tune(gate_info2, np.linspace(0.154, 0.162, 61), repeat_pulse=12)
    Drag_test(gate_info1)
    Drag_test(gate_info2)  


if 0: #ZX90_Echo tune up
    CX_timerabis(np.linspace(0.0, 0.0, 1), gate_info1, gate_info2, np.linspace(0,100,101), 0.079, 4.457, 1.01, repeat_pulse=8, all_axis=True)
#    zx_amplitude(np.linspace(0.065,0.075,61), repeat_pulse=12)
#add crossing  - check contrast after better tuning 


if 0:#Check if zx90 parameters match with gate1
    print(zx90_info.deltaf == gate_info1.deltaf)
#    print(zx90_info.relative_phase == gate_info1.relative_phase)
#    print(zx90_info.sideband_phase == gate_info1.sideband_phase)
#    print(zx90_info.sideband_phase2 == gate_info1.sideband_phase2)
#       
    
