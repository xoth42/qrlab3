"""
Created on Sat Nov 30 14:19:44 2019
@author: Wang_Lab

BREAK EVEN OR BROKE
"""

import mclient
import importlib
importlib.reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib, OCTlib
import matplotlib.pyplot as plt
import os
os.chdir(r'C:/qrlab/scripts')

from .FWM import poly_fwm_ssbspec, poly_time_domain
from .AQEC import husimiq_angle_test, CavT2_AQEC

qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
cavity_infoA = mclient.get_qubit_info('cavityA')
#cavity_infoAs = mclient.get_qubit_info('cavityAs')
dig = mclient.instruments['dig']

fwm_info = mclient.get_qubit_info('FWM_info')
qubit_a1 = mclient.get_qubit_info('qubit_a1')
qubit_a2 = mclient.get_qubit_info('qubit_a2')
qubit_a3 = mclient.get_qubit_info('qubit_a3')
qubit_a4 = mclient.get_qubit_info('qubit_a4')
qubit_a5 = mclient.get_qubit_info('qubit_a5')
qubit_a6 = mclient.get_qubit_info('qubit_a6')
qubit_a7 = mclient.get_qubit_info('qubit_a7')

cA = cavity_infoA.rotate
ge = qubit_info.rotate

chi2 = 2.655e6
chi2s = 2.679e6
chi2n = 2.675e6

cav_amp = 114.8
qt_amp = 43.3
time_shift = 11    
lib = OCTlib.octlib(qt_amp, cav_amp, time_shift, qubit_info, cavity_infoA)

bloch = ['-y', '+y', '-x',  '+x', '-z', '+z']
bloch_targets = [[-1, 0, 0], [1, 0, 0], [0, -1, 0],  [0, 1, 0], [0, 0, -1], [0, 0, 1]]

'''AQEC condition #M0  11/28, kappa = 0.174+/-0.002 1/us'''
ss0 = 2.8045e6
fwm_comb0 = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.2, 1.03, 0.62, 0.45]], vary = [1]*4, stark_shift = ss0,
                       phases = [np.pi, 0, 0, 0])
ge_comb0 = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [0.92, 1.55, 1.25, 1.13]], 
                      vary = [-1]*4, stark_shift = -ss0, phases = [np.pi, 0, 0, 0])
infos0 = [fwm_comb0.info, ge_comb0.info]
rot_speed_M0 = 18.20    

'''AQEC condition #MP-  12/22.  Conversion rate/phase matching based, closest to earlier #MP'''        
ss1 = 2.904e6
fwm_comb1 = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.22, 1.00, 0.64, 0.49]], vary = [1]*4, stark_shift = ss1,
                       phases = [np.pi, 0, 0, 0])
ge_comb1 = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [1.06, 1.54, 1.29, 1.12]], 
                      vary = [-1]*4, stark_shift = -ss1, phases = [np.pi-0.66, -0.14, 0.29, 0.30])
rot_speed1 = 18.86

#'''AQEC condition #ML  12/18, lower Stark shift, kappa = 0.170-0.175 /us, full optimized with pre-Kerr'''
#ss2 = 2.502e6    
#fwm_comb2 = OCTlib.comb(fwm_info, [0, chi2n, chi2n*2, chi2n*3], [x*0.2 for x in [1.17, 0.91, 0.59, 0.48]], vary = [1]*4, stark_shift = ss2,
#                       phases = [-np.pi, 0, 0, 0])
#ge_comb2 = OCTlib.comb(qubit_info, [0, -chi2n, -chi2n*2, -chi2n*3], [y*1.0e-3 for y in [1.14, 1.62, 1.37, 1.20]],
#                      vary = [-1]*4, stark_shift = -ss2, phases =[np.pi-0.75, -0.10,  0.12, -0.10])
#rot_speed_ML = 16.75

#'''AQEC condition #OL  12/26, lower Stark shift'''
#ss2 = 2.537e6    
#fwm_comb2 = OCTlib.comb(fwm_info, [0, chi2n, chi2n*2, chi2n*3], [x*0.2 for x in [1.16, 0.91, 0.59, 0.47]], vary = [1]*4, stark_shift = ss2,
#                       phases = [-np.pi, 0, 0, 0])
#ge_comb2 = OCTlib.comb(qubit_info, [0, -chi2n, -chi2n*2, -chi2n*3], [y*1.0e-3 for y in [0.854, 1.409, 1.194, 1.075]], 
#                      vary = [-1]*4, stark_shift = -ss2, phases = [2.44, -0.14, 0.01, -0.36])
#rot_speed2 = 16.95

'''AQEC condition #OL  last optimized 1/26, lower Stark shift'''
ss2 = 2.500e6    
fwm_comb2 = OCTlib.comb(fwm_info, [0, chi2n, chi2n*2, chi2n*3], [x*0.2 for x in [1.15, 0.90, 0.59, 0.47]], vary = [1]*4, stark_shift = ss2,
                       phases = [-np.pi, 0, 0, 0])
ge_comb2 = OCTlib.comb(qubit_info, [0, -chi2n, -chi2n*2, -chi2n*3], [y*1.0e-3 for y in [0.714, 1.194, 1.101, .964]], 
                      vary = [-1]*4, stark_shift = -ss2, phases = [2.51, -0.14, -0.024, -0.40])
rot_speed2 = 16.87

#'''AQEC condition #MP+  12/19, larger ge amps, guided by pre-Kerr optimizer'''        
#ss3 = 2.831e6
#fwm_comb3 = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.22, 1.01, 0.64, 0.47]], vary = [1]*4, stark_shift = ss3,
#                       phases = [np.pi, 0, 0, 0])
#ge_comb3 = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [1.27, 1.86, 1.56, 1.355]],
#                      vary = [-1]*4, stark_shift = -ss3, phases = [np.pi-0.76, -0.10, 0.13, 0.02])
#rot_speed_MPp = 18.39

'''AQEC condition #OXY   last optimized 12/25'''
#ss = 2.898e6     
#fwm_comb4 = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.22, 1.00, 0.64, 0.49]], vary = [1]*4, stark_shift = ss,
#                   phases = [np.pi, 0, 0, 0])
#ge_comb4 = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [0.849, 1.421, 1.201, 1.048]], 
#                  vary = [-1]*4, stark_shift = -ss, phases = [2.48, -0.14, -0.02, -0.38])
#rot_speed4 = 18.68
'''last optimzed 1/31'''
ss = 2.870e6     
fwm_comb4 = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.22, 1.00, 0.64, 0.49]], vary = [1]*4, stark_shift = ss,
                   phases = [np.pi, 0, 0, 0])
ge_comb4 = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [0.684, 1.252, 1.102, 0.921]], 
                  vary = [-1]*4, stark_shift = -ss, phases = [2.61, -0.14, -0.09, -0.52])
rot_speed4 = 18.86

'''AQEC condition #OMP'''
ss = 2.870e6
fwm_comb5 = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.22, 1.00, 0.64, 0.49]], vary = [1]*4, stark_shift = ss,
                   phases = [np.pi, 0, 0, 0])
ge_comb5 = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [0.98, 1.52, 1.27, 1.14]], 
                  vary = [-1]*4, stark_shift = -ss, phases = [2.576, -0.14, -0.116, -0.49])
rot_speed5 = 18.68


'''Free condition to make running easier '''
fwm_free = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*1e-10 for x in [1.22, 1.00, 0.64, 0.49]], vary = [1]*4, stark_shift = ss,
                   phases = [np.pi, 0, 0, 0])
ge_free = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1e-10 for y in [0.98, 1.52, 1.27, 1.14]], 
                  vary = [-1]*4, stark_shift = -ss, phases = [2.576, -0.14, -0.116, -0.49])
rot_speed_free = 18.68

def stark_cal(fwm_comb, ge_comb, fast=False, update=True, confidence=0.7):
    ss = fwm_comb.stark_shift
    freqs = np.linspace(-0.11e6, 0.1e6, 41)

    period = dig.get_trigger_period()
    naverages = dig.get_naverages()
    dig.set_trigger_period(2000)   
    dig.set_naverages(1200)
    
    ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(qubit_a1, [fwm_comb, ge_comb], freqs, 12e3, post_delay = 1e3, seq = None,
                                            bgcor = False, extra_info = [qubit_info, cavity_infoA])
    dss0 = ssb.measure_keysight()

    if fast:
        ss -= (dss0+10e3)*confidence   #Estimate ss is 10kHz above dss0
        print('Fast check stark shift -- Only 0->1 is measured.\n', 'dss0=', dss0, '\n', 'ss=', ss/1000, '\n')
    
    else:   
        seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state_two_file('2')])
        ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(qubit_a3, [fwm_comb, ge_comb], freqs, 12e3, post_delay = 1e3, seq = seq,
                                                bgcor = False, extra_info = [qubit_info, cavity_infoA])
        dss2 = ssb.measure_keysight()
        
        seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state_two_file('4')])
        ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(qubit_a5, [fwm_comb, ge_comb], freqs, 12e3, post_delay = 1e3, seq = seq,
                                                bgcor = False, extra_info = [qubit_info, cavity_infoA])
        dss4 = ssb.measure_keysight()
    
        seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state('6')])
        ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(qubit_a7, [fwm_comb, ge_comb], freqs, 12e3, post_delay = 1e3, seq = seq,
                                                bgcor = False, extra_info = [qubit_info, cavity_infoA])
        dss6 = ssb.measure_keysight()    
        
        ss -= (dss0+dss2+dss4+dss6)/4*confidence
        print('\n', 'dss=', dss0/1000, dss2/1000, dss4/1000, dss6/1000, '\n', 'ss=', ss/1000, '\n')
    
    if update:
        fwm_comb.stark_shift = ss
        ge_comb.stark_shift= -ss
        
    dig.set_trigger_period(period)   
    dig.set_naverages(naverages)
    return ss

def T2_stark_cal(fwm_comb, ge_comb, fast=True, update=True):
    from .AQEC import T2_AQEC
    ss = fwm_comb.stark_shift
    period = dig.get_trigger_period()
    naverages = dig.get_naverages()
    dig.set_trigger_period(500)   
    dig.set_naverages(1000)
    
    comb_offset = 50e6
    fwm_comb_t2 = OCTlib.comb(fwm_info, [x+comb_offset for x in [0, chi2s, chi2s*2, chi2s*3]], [x*0.224 for x in [1.770, 0, 0, 0]],#[1.22, 1.00, 0.64, 0.49]], 
                              vary = [1]*4, stark_shift = 0, phases = [np.pi, 0, 0, 0])
    st2 = T2_AQEC.T2_AQEC(qubit_info, np.linspace(1e3, 20e3, 77), [fwm_comb_t2], detune=2.6e6, 
                                     double_freq=False, generate=True, seq=None,
                                     plot_seqs=False)
    deltaf = st2.measure_keysight()
    ss = 2.600e6 + deltaf*1e9
    if fwm_comb == fwm_comb2:
        ss = (deltaf*1e9-0.3e6)*0.86+2.491e6
    print('\n', 'ss=', ss/1000, 'kHz \n')
    
    if update:
        fwm_comb.stark_shift = ss
        ge_comb.stark_shift= -ss
    dig.set_trigger_period(period)   
    dig.set_naverages(naverages)
    return ss

def cav_qubit_T2(echo=False):
    from .single_cavity import cavT2
    from .single_qubit import T2measurement
    period = dig.get_trigger_period()
    naverages = dig.get_naverages()
    dig.set_naverages(1000)

    dig.set_trigger_period(2000)
    ct2 = cavT2.CavT2(qubit_info, cavity_infoA, .7, np.linspace(0, 500e3, 41), detune=10e3, seq=None, echo=echo, 
                       postseq=None, bgcor=False)
    ct2.measure_keysight()
    
    dig.set_trigger_period(500)
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0e3, 25e3, 76), detune=0.3e6, 
                                     double_freq=False, generate=True, seq=None)
    t2.measure_keysight()

    dig.set_trigger_period(period)   
    dig.set_naverages(naverages)
    return #[ct2, t2, st2]
    
def cav_T2(echo=False):
    from .single_cavity import cavT2
    period = dig.get_trigger_period()
    naverages = dig.get_naverages()
    dig.set_naverages(1000)
    dig.set_trigger_period(2000)
    ct2 = cavT2.CavT2(qubit_info, cavity_infoA, .7, np.linspace(0, 500e3, 41), detune=10e3, seq=None, echo=echo, 
                       postseq=None, bgcor=False)
    ct2.measure_keysight()
    dig.set_trigger_period(period)   
    dig.set_naverages(naverages)
    return ct2

def rot_frame_cal(fwm_comb, ge_comb):
    dig.set_trigger_period(2500)
    dig.set_naverages(1800)
    detune_mz = 10e3
    delays = np.linspace(10e3, 210e3, 41)
    seq = [sequencer.Trigger(200), lib.mod4_prep('-z')]    
    ct2 = CavT2_AQEC.CavT2_AQEC(qubit_info, cavity_infoA, 0.75, delays, comb_list=[fwm_comb, ge_comb], 
                                detune=detune_mz, seq=seq, postseq=None, bgcor=True, t_ge=356)
    mzt2 = ct2.measure_keysight()
    rot_speed = mzt2['freq']*1e6/4 + detune_mz/1e3
    return rot_speed


def prekerr_check(fwm_comb, ge_comb, fast=True):
    ''' We check conversion efficiency and check how far we've drifed from the optimal values in 4 of the most sensitive parameters'''
    from .AQEC import prekerr_optimize, prekerr_calibrate
    dig.set_naverages(1500)
    dig.set_trigger_period(3000)
    pc = prekerr_calibrate.prekerr_calibrate(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb],
                                           phases = np.linspace(0, np.pi, 25))
    params = pc.measure_keysight()
    phase = params['phase'].value        
    if fast: return
    
    dig.set_naverages(2000)
    dig.set_trigger_period(2000)
    for parameter in ['ge_phase_0', 'ge_phase_2']:
        po = prekerr_optimize.prekerr_optimize(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb], 
                                          parameter, np.linspace(-0.7, 0.7, 31), phase = phase-np.pi/2)
        po.measure_keysight()
    for parameter in ['ge_amp_1', 'ge_amp_2']:
        po = prekerr_optimize.prekerr_optimize(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb], 
                                          parameter, np.linspace(0.65, 1.35, 31), phase = phase-np.pi/2)
        po.measure_keysight()        
    return

def AQEC144_check(fwm_comb, ge_comb):
    ''' We check AQEC performance on +x state at 144 us'''
    from .AQEC import prekerr_calibrate
    dig.set_naverages(2000)
    dig.set_trigger_period(3000)
    pc = prekerr_calibrate.prekerr_calibrate(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb],
                                       phases = np.linspace(0, np.pi, 21), pump_time=144e3, init_state='+x')
    params = pc.measure_keysight()
    phase = params['phase'].value      
    return phase
    
def rate_curves(fwm_comb, ge_comb, fast=False):
    if fast:
        delays = np.concatenate((np.linspace(0e3, 9e3, 10), np.linspace(10e3, 18e3, 5), np.linspace(20e3, 40e3, 6)))
    else:
#        delays = np.concatenate((np.linspace(0e3, 15e3, 16), np.linspace(16e3, 40e3, 13)))
        delays = np.linspace(0e3, 40e3, 41)

    if fast:
        dig.set_trigger_period(2000)
        dig.set_naverages(1200)
    else:    
        dig.set_trigger_period(3000)
        dig.set_naverages(1800)
        
    T2_stark_cal(fwm_comb, ge_comb)
    td0 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a1], delays, bgcor=True, seq=None, 
                                       extra_info = [qubit_info, cavity_infoA])
    hl0 = td0.measure_keysight()

    T2_stark_cal(fwm_comb, ge_comb)
    seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state_two_file('2')])
    td2 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a3], delays, bgcor=True, seq=seq, 
                                       extra_info = [qubit_info, cavity_infoA])
    hl2 = td2.measure_keysight()

    if fast:
        dig.set_trigger_period(2500)
        dig.set_naverages(1600)          
    if not fast:
        dig.set_trigger_period(4000)
        dig.set_naverages(2400) 
  
    T2_stark_cal(fwm_comb, ge_comb) 
    seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state_two_file('4')])
    td4 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a5,], delays, bgcor=True, seq=seq, 
                                       extra_info = [qubit_info, cavity_infoA])
    hl4 = td4.measure_keysight()

    T2_stark_cal(fwm_comb, ge_comb)    
    seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state('6')])
    td6 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a7,], delays, bgcor=True, seq=seq,
                                       extra_info = [qubit_info, cavity_infoA])
    hl6 = td6.measure_keysight()

    return hl0, hl2, hl4, hl6


def xy_optimizer(parameter, fwm_comb, ge_comb, values, phase=2.55, allxy=True, threshold=60, confidence=0.5):
    '''Take 144us optimizer data for init state of +x and +y to find optimal parameter'''
    from .AQEC import loptimize
    pump_time = 144e3
    lop = loptimize.loptimize(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb], parameter, values, phase = phase-np.pi/2, pump_time=pump_time)
    result = lop.measure_keysight()
    optimum = result[0]
    ymax = result[1]

    index = int(parameter[-1])
    if 'ge_amp' in parameter:
        adj = optimum*confidence + 1-confidence
        adj = min(1.04, max(adj, 0.96))
        if ymax > threshold:
            ge_comb.amps[index] *= adj
            print('ge_comb amp%i adjusting by %.03f' %(index, adj), '\n')
    elif 'ge_phase' in parameter:
        adj = optimum*confidence
        adj = min(0.08, max(adj, -0.08))
        if ymax > threshold:
            ge_comb.phases[index] += adj
            print('ge_comb phase%i adjusting by %.03f' %(index, adj), '\n')

    return adj



'''
--------------------------------------------------------------------------------------------------------------------------
'''

    
if 1:  # Optimizer144 (~2 h per round)
    from .AQEC import prekerr_calibrate
    fwm_comb, ge_comb = fwm_comb4, ge_comb4

    for rep in range(3):
        T2_stark_cal(fwm_comb, ge_comb,fast=True)
        dig.set_naverages(2000)
        dig.set_trigger_period(3000)
        pc = prekerr_calibrate.prekerr_calibrate(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb],
                                           phases = np.linspace(0, np.pi, 21), pump_time=144e3, init_state='+x')
        params = pc.measure_keysight()
        phase = params['phase'].value
        cav_qubit_T2()
        dig.set_trigger_period(2500)        
        
#        xy_optimizer('fwm_amp_9', fwm_comb, ge_comb, np.linspace(0.8, 1.2, 17), phase=phase, confidence=0.6)                
#        xy_optimizer('fwm_amp_1', fwm_comb, ge_comb, np.linspace(0.95, 1.05, 17), phase=phase, confidence=0.6)                
#        xy_optimizer('fwm_amp_2', fwm_comb, ge_comb, np.linspace(0.90, 1.10, 17), phase=phase, confidence=0.6)                
#        xy_optimizer('fwm_amp_3', fwm_comb, ge_comb, np.linspace(0.88, 1.12, 17), phase=phase, confidence=0.5)                        
#        xy_optimizer('ge_amp_9', fwm_comb, ge_comb, np.linspace(0.6, 1.45, 17), phase=phase, confidence=0.4)

        dig.set_naverages(3000)
        xy_optimizer('ge_amp_1', fwm_comb, ge_comb, np.linspace(0.7, 1.3, 15), phase=phase, confidence=0.6)
        T2_stark_cal(fwm_comb, ge_comb,fast=True)
        xy_optimizer('ge_phase_2', fwm_comb, ge_comb, np.linspace(-0.7, 0.7, 15), phase=phase, confidence=0.6)
        xy_optimizer('ge_amp_2', fwm_comb, ge_comb, np.linspace(0.7, 1.3, 15), phase=phase, confidence=0.6)
        T2_stark_cal(fwm_comb, ge_comb,fast=True)
        cav_qubit_T2()
        xy_optimizer('ge_phase_3', fwm_comb, ge_comb, np.linspace(-1.2, 1.2, 15), phase=phase, confidence=0.5)
        xy_optimizer('ge_amp_3', fwm_comb, ge_comb, np.linspace(0.5, 1.5, 15), phase=phase, confidence=0.5)
        T2_stark_cal(fwm_comb, ge_comb,fast=True)
        xy_optimizer('ge_phase_0', fwm_comb, ge_comb, np.linspace(-1.2, 1.2, 15), phase=phase, confidence=0.4)
        dig.set_naverages(4000)
        xy_optimizer('ge_amp_0', fwm_comb, ge_comb, np.linspace(0.4, 1.6, 15), phase=phase, confidence=0.4)

        
if 1: # Regular function calls
    fwm_comb, ge_comb = fwm_comb4, ge_comb4
    if 1: # Stark Cal (~6 minutes, fast 1.5 minutes)
        stark_cal(fwm_comb, ge_comb, fast=False)            
    if 1: # Stark Cal with qubit Ramsey
        ss = T2_stark_cal(fwm_comb, ge_comb)
    if 1: # Conversion rate check (~35 minutes, fast 20 minutes)
        rate_curves(fwm_comb, ge_comb, fast=False)    
    if 0: # prekerr Optimizer Check (1 hour?)
        prekerr_check(fwm_comb, ge_comb, fast=True)        
    if 0: # AQEC144_check
        AQEC144_check(fwm_comb, ge_comb)
    if 1: # 1-5 rotating frame calibration
        rot_speed4 = rot_frame_cal(fwm_comb, ge_comb)    
    if 0: 
        for i in range(20):
            cav_qubit_T2()
    



if 0: # Wigner tomography with AQEC    
    from scripts.single_cavity import WignerbyParity
    from .AQEC import time_bloch
    
#    times = np.arange(72e3, 250e3, 72e3)  #Typically we measure at 72us, 144us and 216us
    wignertimes = np.arange(0, 250e3, 35.2e3)
    times = np.arange(0, 300e3, 72e3)
    fwm_comb, ge_comb = fwm_comb5, ge_comb5
    infos = [fwm_comb.info, ge_comb.info]
    stark_cal(fwm_comb, ge_comb, fast=True)

#    for k, state in enumerate(bloch):
    for state in ['+x', '-z', '+z']:
#        state = bloch[k]
        for dt in wignertimes:
#            rot_speed4 = rot_frame_cal(fwm_comb, ge_comb) 
#            rot_speedf = 4.44
#            rotation = rot_speed5/1e3*(dt/1e3+1.1)*2*np.pi  #18.22 kHz rotating frame, 1us for effective time of state prep+Wigner prep
            seq = [sequencer.Join([sequencer.Trigger(200), lib.mod4_prep(state)])]
            if dt>0:
#                poly_seq = sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0))
#                seq += [poly_seq]
                seq += [sequencer.Delay(dt)]
                
                dig.set_trigger_period(4000)
                dig.set_naverages(1000)               
                Wfun = WignerbyParity.WignerFunction(qubit_a4, ef_info, cavity_infoA, xs = np.linspace(-2.4, 2.4, 21), ys = np.linspace(-2.4, 2.4, 21),
                             t_ge=356, t_gf=0, seq=seq, delay=5, bgcor=True, zmax=100, zmin=-100, 
                             extra_info = infos+ [qubit_info, cavity_infoA], 
#                                             rotation = rotation
                             )
                Wfun.measure_keysight()
                cav_qubit_T2()                  
#            n = 27
#            full_range = np.linspace(-2.4, 2.4, n)
#            for rep in range(3):
#                dig.set_trigger_period(4000)
#                dig.set_naverages(1000)
#                for i in range(3):
#                    Wfun = WignerbyParity.WignerFunction(qubit_a4, ef_info, cavity_infoA, xs = full_range[i*n/5: (i+1)*n/5], ys = full_range,
#                                             t_ge=356, t_gf=0, seq=seq, delay=5, bgcor=True, zmax=100, zmin=-100, 
#                                             extra_info = infos+ [qubit_info, cavity_infoA], 
##                                             rotation = rotation
#                                             )
#                    Wfun.measure_keysight()
#                    cav_qubit_T2()            

#                '''logical equator lifetime'''
#                dig.set_naverages(5000)
#                rotations = times/1.0e6 * 2*np.pi*rot_speed2
#                wseq = [sequencer.Join([sequencer.Trigger(200), lib.mod4_prep('+x')])]
#                tb = time_bloch.time_bloch(qubit_info, times, seq = wseq, target_state = 'purity',
#                                           postseq = lib.mod4_decode, background_fidelity = 0.001,
#                                           comb_list = [fwm_comb, ge_comb], g_value = 150, e_value = 21.5,
#                                           rotations = rotations, extra_info = [cavity_infoA])
#                tb.measure_keysight()
#                
#                stark_cal(fwm_comb, ge_comb, fast=True)
#                cav_qubit_T2()            
                
if 0: # Conversion Wigner for process matrix reconstruction
    from scripts.single_cavity import WignerbyParity
    from .AQEC import time_bloch
    from .single_qubit import ssbspec

    fwm_comb, ge_comb = fwm_comb5, ge_comb5
    T2_stark_cal(fwm_comb, ge_comb)
    infos = [fwm_comb.info, ge_comb.info]
#    prepare_states = ['02', '04', '06', '24', '26', '46']    
    prepare_states = ['57']    
    dt = 25e3
    times = np.arange(0, 450e3, 71.7e3)
    
    for rep in range(1):
        for state in prepare_states:
            n = 27
            full_range = np.linspace(-2.4, 2.4, n)        
            seq = [sequencer.Trigger(200), lib.fock_state(state)]
            poly_seq = sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0))
            seq += [poly_seq]
        
            dig.set_trigger_period(4000)
            dig.set_naverages(1000)
            for i in range(3):
                Wfun = WignerbyParity.WignerFunction(qubit_a4, ef_info, cavity_infoA, xs = full_range[i*n/3: (i+1)*n/3], ys = full_range,
                                         t_ge=356, t_gf=0, seq=seq, delay=5, bgcor=True, zmax=100, zmin=-100, 
                                         extra_info = infos+ [qubit_info, cavity_infoA])
                Wfun.measure_keysight()
                cav_T2()
                T2_stark_cal(fwm_comb, ge_comb, fast=True)
                
                
#            dig.set_naverages(4000)
#            spec = ssbspec.SSBSpec(qubit_info, np.linspace(-7.5, .5, 201)*chi2/2, 
#                                    seq=sequencer.Join(seq), 
#                                    extra_info = infos + [cavity_infoA]
#                                    )
#            spec.measure_keysight()
                
                
            seq2 = [sequencer.Trigger(200), lib.fock_state(state)]
        
            dig.set_trigger_period(4000)
            dig.set_naverages(1000)
            for i in range(3):
                Wfun = WignerbyParity.WignerFunction(qubit_a4, ef_info, cavity_infoA, xs = full_range[i*n/3: (i+1)*n/3], ys = full_range,
                                         t_ge=356, t_gf=0, seq=seq2, delay=5, bgcor=True, zmax=100, zmin=-100, 
                                         extra_info = infos+ [qubit_info, cavity_infoA])
                Wfun.measure_keysight()
                cav_qubit_T2()
                T2_stark_cal(fwm_comb, ge_comb, fast=True)

                
#            dig.set_naverages(4000)
#            spec = ssbspec.SSBSpec(qubit_info, np.linspace(-7.5, .5, 201)*chi2/2, 
#                                    seq=sequencer.Join(seq2), 
#                                    extra_info = infos + [cavity_infoA]
#                                    )
#            spec.measure_keysight()

#            Wfun = WignerbyParity.WignerFunction(qubit_a4, ef_info, cavity_infoA, xs = np.linspace(-1.8,1.8,17), ys = np.linspace(-1.8,1.8,17),
#                                     t_ge=356, t_gf=0, seq=seq, delay=5, bgcor=True, zmax=100, zmin=-100, extra_info = infos+ [qubit_info])
#            Wfun.measure_keysight()      

            '''logical equator lifetime'''
            dig.set_trigger_period(3000)
            dig.set_naverages(4000)    
            rotations = times/1.0e6 * 2*np.pi*rot_speed5
            wseq = [sequencer.Join([sequencer.Trigger(200), lib.mod4_prep('+x')])]
            tb = time_bloch.time_bloch(qubit_info, times, seq = wseq, target_state = 'purity', postseq = lib.mod4_decode, 
                                       background_fidelity = 0.001, comb_list = [fwm_comb, ge_comb], g_value = 170, e_value = 25,
                                       rotations = rotations, extra_info = [cavity_infoA])
            tb.measure_keysight()
#                
            stark_cal(fwm_comb, ge_comb, fast=True, update=False)



if 1: # Logical qubit lifetime
    from .AQEC import time_bloch
    rep = 6
#    times = np.arange(0, 340e3, 73e3)
    '''Kerr correction currently does not work
    kerr_corrections = [[0, 1, 2, 3] * (len(times)/4) + [0, 1, 2, 3][:len(times)%4],
                        [0, 1, 2, 3] * (len(times)/4) + [0, 1, 2, 3][:len(times)%4],
                        [0, 1, 2, 3] * (len(times)/4) + [0, 1, 2, 3][:len(times)%4],
                        [0, 1, 2, 3] * (len(times)/4) + [0, 1, 2, 3][:len(times)%4],
                        [0, 0, 0, 0] * (len(times)/4) + [0, 0, 0, 0][:len(times)%4],
                        [0, 0, 0, 0] * (len(times)/4) + [0, 0, 0, 0][:len(times)%4]]
    '''
    for j in range(rep):
        dig.set_trigger_period(3000)
        dig.set_naverages(3500)
        
        cav_qubit_T2(echo=True)
        T2_stark_cal(fwm_comb5, ge_comb5, fast=True)
        rot_speed5 = rot_frame_cal(fwm_comb5, ge_comb5)
        T2_stark_cal(fwm_comb4, ge_comb4, fast=True)
        rot_speed4 = rot_frame_cal(fwm_comb4, ge_comb4)
        AQEC144_check(fwm_comb5, ge_comb5)
        AQEC144_check(fwm_comb4, ge_comb4)
        for i, state in enumerate(bloch[:]):
            target = bloch_targets[i]
            cav_T2()
 
            ''' AQEC #OMP'''
            fwm_comb, ge_comb = fwm_comb5, ge_comb5
            stark_cal(fwm_comb, ge_comb, fast=True)
            print("current SS =", fwm_comb.stark_shift, '\n')
            times = np.arange(0, 240e3, 36e3)
            rotations = times/1.0e6 * 2*np.pi*rot_speed5
            seq = [sequencer.Join([sequencer.Trigger(200), lib.mod4_prep(state)])]
            tb = time_bloch.time_bloch(qubit_info, times, seq = seq, target_state = 'purity',
                                       postseq = lib.mod4_decode, background_fidelity = 0.001,
                                       comb_list = [fwm_comb, ge_comb], g_value = 170, e_value = 25,
                                       rotations = rotations, extra_info = [cavity_infoA],
                                       secondary_decode = True, #t2_check = lib.fock01_encode
                                       )
            tb.measure_keysight()

#            ''' AQEC #MP-'''
#            fwm_comb, ge_comb = fwm_comb1, ge_comb1
#            T2_stark_cal(fwm_comb, ge_comb, fast=True)
#            print "current SS =", fwm_comb.stark_shift, '\n'
##            dig.set_naverages(8000)
#            times = np.arange(0, 240e3, 36e3)
##            times = np.arange(0, 380e3, 36e3)
#            rotations = times/1.0e6 * 2*np.pi*rot_speed1
#            seq = [sequencer.Join([sequencer.Trigger(200), lib.mod4_prep(state)])]
#            tb = time_bloch.time_bloch(qubit_info, times, seq = seq, target_state = 'purity',
#                                       postseq = lib.mod4_decode, background_fidelity = 0.001,
#                                       comb_list = [fwm_comb, ge_comb], g_value = 170, e_value = 25,
#                                       rotations = rotations, extra_info = [cavity_infoA],
#                                       secondary_decode = True, #t2_check = lib.fock01_encode
#                                       )
#            tb.measure_keysight() 
##            dig.set_naverages(3000)
            
            ''' AQEC #OXY'''
            fwm_comb, ge_comb = fwm_comb4, ge_comb4
            T2_stark_cal(fwm_comb, ge_comb, fast=True)
            print("current SS =", fwm_comb.stark_shift, '\n')
            times = np.arange(0, 240e3, 36e3)
            rotations = times/1.0e6 * 2*np.pi*rot_speed4
            seq = [sequencer.Join([sequencer.Trigger(200), lib.mod4_prep(state)])]
            tb = time_bloch.time_bloch(qubit_info, times, seq = seq, target_state = 'purity',
                                       postseq = lib.mod4_decode, background_fidelity = 0.001,
                                       comb_list = [fwm_comb, ge_comb], g_value = 170, e_value = 25,
                                       rotations = rotations, extra_info = [cavity_infoA],
                                       secondary_decode = True, #t2_check = lib.fock01_encode
                                       )
            tb.measure_keysight()                     
            
#            ''' Free evolution'''
##            fwm_comb, ge_comb = fwm_comb2, ge_comb2
##            stark_cal(fwm_comb, ge_comb, fast=True)
##            print "current SS =", fwm_comb.stark_shift, '\n'
#            times = np.arange(0, 200e3, 70.4e3/2)
#            rotations = times/1.0e6 * 2*np.pi*4.44#1.85*2.5
#            seq = [sequencer.Join([sequencer.Trigger(200), lib.mod4_prep(state)])]
#            tb = time_bloch.time_bloch(qubit_info, times, seq = seq, target_state = 'purity',
#                                       postseq = lib.mod4_decode, background_fidelity = 0.001,
##                                       comb_list = [fwm_comb, ge_comb], 
#                                       g_value = 145, e_value = 23,
#                                       rotations = rotations, extra_info = [cavity_infoA],
#                                       secondary_decode = True)
#            tb.measure_keysight()
#            cav_qubit_T2()
            
#        stark_cal(fwm_comb1, ge_comb1)
##        stark_cal(fwm_comb3, ge_comb3)




if 0: # Regular transmon characterization (~6 minutes)
    dig.set_trigger_period(500)
    dig.set_naverages(1000)

    from .single_qubit import rabi
    tr = rabi.Rabi(qubit_info, np.linspace(-0.5, 0.5, 61), selective=False,
                   plot_seqs=False, generate=True, repeat_pulse=2, update=False, seq=None)
    tr.measure_keysight()
    
    from .single_qubit import T1measurement
    t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 19e3, 20), np.linspace(20e3, 160e3, 20))), 
                                     double_exp=False, generate=True, plot_seqs=False, seq=None)
    t1.measure_keysight()

    from .single_qubit import T2measurement
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0e3, 40e3, 101), detune=0.3e6, 
                                     double_freq=True, generate=True, seq=None)
    t2.measure_keysight()
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0.1e3, 39e3, 101), detune=0.2e6, 
                                     echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True)
    t2.measure_keysight()
    
    dig.set_trigger_period(1000)
    from .single_qubit import efrabi
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.7, 0.7, 51), plot_seqs=False, selective=False, generate=True, postseq = None, update=True)
    efr.measure_keysight()
    period = efr.fit_params['period'].value
    dig.set_naverages(5000)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.7, 0.7, 51), first_pi=False, selective=False, force_period=period, postseq= None, generate=True)
    efr.measure_keysight()


if 0:  #Conversion phase calibration (new)
#for i in range(6):
    fwm_comb, ge_comb = fwm_free, ge_free
    
    dig.set_trigger_period(3000)
#    detunes = [15e3, 15e3]*1
    detunes = [15e3, 15e3]*1
#    states = ['02', '24', '46', '04', '26']
    states = ['35', '13']
#    n_dif = [2, 2, 2, 4, 4]
    n_dif = [2, 2]
#    displacements = [1.35, 1.85, 2.3, 1.5, 1.9]
    displacements = [1.35, 1.35]
    delays = np.linspace(0, 250e3, 41)
    t2_params = []
    angle_params = []
    for i, state in enumerate(states):
        T2_stark_cal(fwm_comb, ge_comb)
        seq = [sequencer.Trigger(200), lib.fock_state(state)]
        dig.set_naverages(4000)
        ct2 = CavT2_AQEC.CavT2_AQEC(qubit_info, cavity_infoA, displacements[i], delays, comb_list=[fwm_comb, ge_comb], 
                                    detune=detunes[i], seq=seq,
                                    postseq=None, bgcor=False, t_ge=356, meas_type = 'qfunc')
        t2 = ct2.measure_keysight()
        t2_params += [t2]
        
        dig.set_naverages(200)
        qa = husimiq_angle_test.husimiq_angle_test(qubit_info, cavity_infoA, 31, 
                                         displacements[i], bgcor = False, fit = n_dif[i], plot_seqs = False,
                                         seq = seq, extra_info = [qubit_info, fwm_comb.info, ge_comb.info])
        result = qa.measure_keysight()
        angle_params += [result]
    

    plt.figure()
    xs = np.linspace(0, delays[-1], 100)
    f = open("phase_conversion.txt","a+")
    for i, state in enumerate(states):
        initial_phase = angle_params[i].params['phase'].value * n_dif[i] % (2*np.pi)
        fit_phase = (t2_params[i]['phi0'].value + np.pi/2) %(2*np.pi)
        phase_dif = (fit_phase-initial_phase)%(2*np.pi)
        phase_std = np.sqrt(np.power(angle_params[i].params['phase'].stderr*n_dif[i], 2)
                          + np.power(t2_params[i]['phi0'].stderr, 2))
        print(('initial ', initial_phase, ', fit ', fit_phase))
        print((state + ' phase difference: ' + str(phase_dif) + ' +/- ' + str(phase_std) + '\n'))
        f.write('initial, %.03f, fit, %.03f \n'%(initial_phase, fit_phase))
        f.write('%s phase difference: %.03f +/- %.03f \n\n'%(state, phase_dif, phase_std))
        plt.plot(xs, -CavT2_AQEC.t2_fit(t2_params[i], xs, np.zeros_like(xs)), label = state)
    f.close()


if 0: # Kerr measurement (~45 min for 3 rounds)
    fwm_comb, ge_comb = fwm_comb5, ge_comb5
    stark_cal(fwm_comb, ge_comb, fast=True)
    dig.set_trigger_period(2500)

    for i in range(2):
#        T2_stark_cal(fwm_comb, ge_comb, fast=True)

        dig.set_naverages(2000)
        detune_mz = 10e3
        delays = np.linspace(10e3, 210e3, 41)
        seq = [sequencer.Trigger(200), lib.mod4_prep('-z')]
        ct2 = CavT2_AQEC.CavT2_AQEC(qubit_info, cavity_infoA, 0.75, delays, comb_list=[fwm_comb, ge_comb], 
                                    detune=detune_mz, seq=seq, postseq=None, bgcor=True, t_ge=356)
        mzt2 = ct2.measure_keysight()
        
        dig.set_naverages(3000)
        detune_pz = 15e3 # normal values
        delays = np.linspace(10e3, 210e3, 41)        

        seq = [sequencer.Trigger(200), lib.mod4_prep('+z')]
        ct2 = CavT2_AQEC.CavT2_AQEC(qubit_info, cavity_infoA, .5, delays, comb_list=[fwm_comb, ge_comb], 
                                    detune=detune_pz, seq=seq, postseq=None, bgcor=True, t_ge=356)
        pzt2 = ct2.measure_keysight()    
    
        print(('Rotating frame: ' + str(mzt2['freq']*1e6/4 + detune_mz/1e3) + ' +/- ' + str(mzt2['freq'].stderr*1e6/4) + 'KHz'))
        print(('Kerr under AQEC: ' + str((pzt2['freq'] - mzt2['freq'])*1e6/8 + (detune_pz - detune_mz)/2/1e3) + ' +/- ' 
                                  + str((np.sqrt(pzt2['freq'].stderr**2 + mzt2['freq'].stderr**2))*1e6/8) + 'KHz'))


if 0: # SSB of 0-1 conversion
    from .single_qubit import ssbspec
    dig.set_trigger_period(2000)
    dig.set_naverages(2000)
    times = np.arange(20e3, 40e3, 1e3)
    fwm_comb, ge_comb = fwm_comb1, ge_comb1
    infos = [fwm_comb.info, ge_comb.info]

    for dt in times:
        ss = T2_stark_cal(fwm_comb, ge_comb)
        seq = [sequencer.Trigger(200)]
        if dt>0:
            poly_seq = sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0))
            seq += [poly_seq]
            
        spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
                                            np.linspace(-1.5*chi2/2, .5*chi2/2, 75),
                                            )), 
                                seq=sequencer.Join(seq), 
                                extra_info = infos + [cavity_infoA]
                                )
        spec.measure_keysight()
        
        
if 0: # SSB of all focks
    from .single_qubit import ssbspec
    dig.set_trigger_period(3000)
    dig.set_naverages(4000)
    fwm_comb, ge_comb = fwm_comb5, ge_comb5
    infos = [fwm_comb.info, ge_comb.info]
    states = ['1', '2', '3', '4', '5']
    
    
    for rep in range(1):
#        for dt in [0, 25e3]:
        for dt in [25e3]:
            ss = T2_stark_cal(fwm_comb, ge_comb)
            seq = [sequencer.Trigger(200)]
            if dt>0:
                poly_seq = sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0))
                seq += [poly_seq]
                
            spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
                                                np.linspace(-9.5*chi2/2, .5*chi2/2, 201),
                                                )), 
                                    seq=sequencer.Join(seq), 
                                    extra_info = infos + [cavity_infoA]
                                    )
            spec.measure_keysight()

#        for state in states:
#            for dt in [0, 25e3]:
#                ss = T2_stark_cal(fwm_comb, ge_comb)
#                seq = [sequencer.Trigger(200), lib.fock_state_two_file(state)]
#                if dt>0:
#                    poly_seq = sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0))
#                    seq += [poly_seq]
#                    
#                spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
#                                                    np.linspace(-9.5*chi2/2, .5*chi2/2, 201),
#                                                    )), 
#                                        seq=sequencer.Join(seq), 
#                                        extra_info = infos + [cavity_infoA]
#                                        )
#                spec.measure_keysight()
#    
#        for state in ['6', '7']:
#            for dt in [0, 25e3]:
#                ss = T2_stark_cal(fwm_comb, ge_comb)
#                seq = [sequencer.Trigger(200), lib.fock_state(state)]
#                if dt>0:
#                    poly_seq = sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0))
#                    seq += [poly_seq]
#                    
#                spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
#                                                    np.linspace(-9.5*chi2/2, .5*chi2/2, 201),
#                                                    )), 
#                                        seq=sequencer.Join(seq), 
#                                        extra_info = infos + [cavity_infoA]
#                                        )
#                spec.measure_keysight()

'''
def xy_optimizer(parameter, fwm_comb, ge_comb, values, phase=2.55, allxy=True, threshold=210, confidence=0.5):
#    Take 144us optimizer data for init state of +x and +y to find optimal parameter
    from AQEC import prekerr_optimize, loptimize
    pump_time = 144e3

    adj1 = po1.measure_keysight()
    po1 = prekerr_optimize.prekerr_optimize(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb], parameter, 
                                            values, phase = phase-np.pi/2, pump_time=pump_time, init_state='+x')
    adj1 = po1.measure_keysight()
    po2 = prekerr_optimize.prekerr_optimize(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb], parameter, 
                                            values, phase = phase-np.pi/2, pump_time=pump_time, init_state='+y')
    if allxy:
        adj2 = po2.measure_keysight()
        po3 = prekerr_optimize.prekerr_optimize(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb], parameter, 
                                                values, phase = phase-np.pi/2, pump_time=pump_time, init_state='-x')
        adj3 = po3.measure_keysight()
        po4 = prekerr_optimize.prekerr_optimize(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb], parameter, 
                                                values, phase = phase-np.pi/2, pump_time=pump_time, init_state='-y')
        adj4 = po4.measure_keysight()

    ys1, fig = po1.get_ys_fig()
    ys2, fig = po2.get_ys_fig()
    n = len(po1.values)
    xs = po1.values
    ys1a = ys1[:n]
    ys1b = ys1[n:2*n]
    ys2a = ys2[:n]
    ys2b = ys2[n:2*n]    
    Ys = ys1a-ys1b+ys2a-ys2b
    
    if allxy:
        ys3, fig = po3.get_ys_fig()
        ys4, fig = po4.get_ys_fig()
        ys3a = ys3[:n]
        ys3b = ys3[n:2*n]
        ys4a = ys4[:n]
        ys4b = ys4[n:2*n]    
        Y2s = ys3a-ys3b+ys4a-ys4b
        Ys = Ys-Y2s

    pf = np.polyfit(xs, Ys, 2)
    optimum = -pf[1]/pf[0]/2.0
    txt = 'optimal at = %.03f' % (optimum)

    fig = plt.figure()
    plt.subplot(2,1,1)
    plt.plot(xs, Ys)
    plt.plot(xs, pf[0]*xs*xs + pf[1]*xs + pf[2], label=txt)
    plt.subplot(2,1,2)
    plt.plot(xs, Ys-(pf[0]*xs*xs + pf[1]*xs + pf[2]))
    plt.xlabel(po1.parameter)
    fig.axes[0].legend()    

    index = int(parameter[-1])
    if 'ge_amp' in parameter:
        adj = optimum*confidence + 1-confidence
        adj = min(1.04, max(adj, 0.96))
        if pf[0]*optimum*optimum + pf[1]*optimum + pf[2] > threshold:
            ge_comb.amps[index] *= adj
            print 'ge_comb amp%i adjusting by %.03f' %(index, adj), '\n'
        if allxy:
            print '+x optimal = %.03f, +y optimal =%.03f, -x optimal =%.03f, -y optimal =%.03f' % (adj1, adj2, adj3, adj4)
        else:
            print '+x optimal = %.03f, +y optimal =%.03f' % (adj1, adj2)
    elif 'ge_phase' in parameter:
        adj = optimum*confidence
        adj = min(0.08, max(adj, -0.08))
        if pf[0]*optimum*optimum + pf[1]*optimum + pf[2] > threshold:
            ge_comb.phases[index] += adj
            print 'ge_comb phase%i adjusting by %.03f' %(index, adj), '\n'  
        if allxy:
            print '+x optimal = %.03f, +y optimal =%.03f, -x optimal =%.03f, -y optimal =%.03f' % (adj1, adj2, adj3, adj4)
        else:
            print '+x optimal = %.03f, +y optimal =%.03f' % (adj1, adj2)

    return optimum

def phase_plot_fit(times, amps, phases, start=0):
    plt.figure()
    plt.subplot(2,1,1)
    plt.plot(times/1e3, amps, '.')
    plt.ylabel('amps')
    plt.subplot(2,1,2)
    plt.plot(times/1e3, phases, '.')
    plt.ylabel('phases')
    pf = np.polyfit(times[start:]/1e3, phases[start:], 1)
    plt.plot(times/1e3, pf[0]*times/1e3+pf[1], linestyle='-')
    print 'slope=', pf[0], 'intercept=', pf[1], '\n\n'
    

if 0: # Conversion phase calibration (~2 hours)
    fwm_comb, ge_comb = fwm_comb1, ge_comb1
#    stark_cal(fwm_comb, ge_comb, fast=True)
    infos = [fwm_comb.info, ge_comb.info]
    times = np.concatenate((np.array([0]), np.linspace(25e3, 40e3, 4), np.linspace(50e3, 95e3, 4)))  #Somehow 85us throws crap??

    qphases = np.array([np.zeros_like(times), np.zeros_like(times), np.zeros_like(times)])
    qamps = np.array([np.zeros_like(times), np.zeros_like(times), np.zeros_like(times)])
    qoffsets = np.array([np.zeros_like(times), np.zeros_like(times), np.zeros_like(times)])
    prepare_states = ['02', '24','46']
    disps = [1.35, 1.85, 2.3]

    tperiods = [2000, 2000, 2500]
    dig.set_naverages(3000)
    
    for j in range(2):
        for i, dt in enumerate(times):
            dig.set_trigger_period(tperiods[j])
            seq = [sequencer.Trigger(200), lib.fock_state(prepare_states[j])]
            if dt>0:
                poly_seq = sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0))
                seq += [poly_seq]
                
            qa = husimiq_angle_test.husimiq_angle_test(qubit_info, cavity_infoAs, 31, disps[j], bgcor = False, fit = 20, plot_seqs = False,
                                                     seq = seq, extra_info = [qubit_info, cavity_infoA] + infos)    
            result = qa.measure_keysight()
            params = result.params
            phase = params['phase']
            if i>0:
                while phase-qphases[j][i-1]>np.pi/2:
                    phase -= np.pi
                while phase-qphases[j][i-1]<-np.pi/2:
                    phase += np.pi
            qphases[j][i] = phase
            qamps[j][i] = params['amp']
            qoffsets[j][i] = params['background']
        phase_plot_fit(times, qamps[j], qphases[j], start=1)
        
        
if 0: # Rotating speed and Kerr calibration (~2.75 hours)
    from AQEC import wigner_angle_test
    fwm_comb, ge_comb = fwm_comb1, ge_comb1
    infos = [fwm_comb.info, ge_comb.info]        
#    stark_cal(fwm_comb, ge_comb)
    
    times = np.linspace(0e3, 210e3, 8)
    dig.set_trigger_period(2500)
    naverages = [2400, 3200]
    
    wphases = np.array([np.zeros_like(times), np.zeros_like(times)])
    wphase_errs = np.array([np.zeros_like(times), np.zeros_like(times)])
    wamps = np.array([np.zeros_like(times), np.zeros_like(times)])
    woffsets = np.array([np.zeros_like(times), np.zeros_like(times)])
    prepare_states = ['-z','+z']
    disps = [0.68, 0.50]
    
    for j in range(2):
        for i, dt in enumerate(times):
            dig.set_naverages(naverages[j])
            seq = [sequencer.Trigger(200), lib.mod4_prep(prepare_states[j])]
            if dt>0:
                poly_seq = sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0))
                seq += [poly_seq]
                
            wa = wigner_angle_test.wigner_angle_test(qubit_a4, cavity_infoAs, 41, 
                                                     disps[j], t_ge  = 356, bgcor = True, fit = 40, seq = seq, extra_info = [qubit_info, cavity_infoA] + infos)
            result = wa.measure_keysight()
            params = result.params
            phase = params['phase']
            if i>0:
                if phase-wphases[j][i-1]>np.pi/4:
                    phase -= np.pi/2
                elif phase-wphases[j][i-1]<-np.pi/4:
                    phase += np.pi/2
            wphases[j][i] = phase
            wphase_errs[j][i] = params['phase'].stderr
            wamps[j][i] = params['amp']
            woffsets[j][i] = params['background']
        phase_plot_fit(times, wamps[j], wphases[j])
'''