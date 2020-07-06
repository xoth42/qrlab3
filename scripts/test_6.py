# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 10:19:22 2019

@author: Ebru
"""
import mclient
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
import matplotlib.pyplot as plt
import math 
import time


import os
os.chdir(r'c:\qrlab')


alz = mclient.instruments['alazar']
yoko = mclient.instruments['yoko']
gaius01 = mclient.instruments['gaius01']
coolgen= mclient.instruments['cool']
ZZ = mclient.instruments['ZZ']

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
qubit_info2 = mclient.get_qubit_info('qubit1ge_2')
qubit2_info = mclient.get_qubit_info('qubit2ge')
qubit2_info2 = mclient.get_qubit_info('qubit2ge_2')



if 0: # Cavity disp calibration
    from scripts.single_cavity import cavdisp
#    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi, 0)])
    seq = sequencer.Trigger(250)

    disp = cavdisp.CavDisp(qubit_info, qubit2_info, np.pi*2, 41, 0, seq=None,
                           delay=0, bgcor=False, update=False, generate=True,proj_func='phase'

                          )
    disp.measure()
    bla

if 0: # test Q function
    from scripts.single_cavity import Qfunction
    cool = sequencer.Constant(int(8e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), qubit2_info.rotate(np.pi, 0)])
    Qfun = Qfunction.QFunction(qubit_info, qubit2_info, amax=np.pi, N=11, amaxx=None, Nx=None, amaxy=None, Ny=None,
             seq=seq, delay=0, saveas=None, bgcor=False, proj_func='phase')
    Qfun.measure()

if 0: # test non-square data
    from scripts.single_cavity import WignerbyParity
#    cool = sequencer.Constant(int(8e3),1,chan='3m1')
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), qubit2_info.rotate(np.pi, 0)])
    Wfun = WignerbyParity.WignerFunction(qubit_info, qubit_info2, qubit2_info, np.linspace(-2, 2, 9), np.linspace(-2, 2, 9), 
                                         t_ge=200, t_gf=0, proj_func='phase')
    Wfun.measure()
    

    
if 1: # Tune up for time vs relative amp
    
    from scripts.fluxonium import CRtuning_timevsamp
    cool = sequencer.Constant(int(8e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])    
    cr_tune = CRtuning_timevsamp.CRtuning_timevsamp(qubit2_info2, qubit2_info, qubit_info, 
                                                    np.linspace(1,150,13), rel_amps=np.linspace(0.2,0.5,13), 
                amp=0.3, phase=0, rel_phase=0, sigma=5, update=False, seq=seq, r_axis=0, fix_phase=True, 
                fix_period=None, repeat_pulse=1, postseq=None, selective=False, control_pi=True, proj_func='phase')    
    
    data = cr_tune.measure()
    bla
        


if 0: # Tune up for relative amp vs relative phase
    
    from scripts.fluxonium import CRtuning_ampvsphase
    cool = sequencer.Constant(int(8e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])    
    
    cr_tune = CRtuning_ampvsphase.CRtuning_ampvsphase(qubit2_info2, qubit2_info, qubit_info, np.linspace(0.2,0.5,17), np.linspace(-0.5,-0.3,17), times=100, 
                amp=0.35, phase=0, sigma=5, update=False, seq=None, r_axis=0, fix_phase=True, fix_period=None, repeat_pulse=1, postseq=None, selective=False, control_pi=True)    
    
    data = cr_tune.measure()
    bla
    
