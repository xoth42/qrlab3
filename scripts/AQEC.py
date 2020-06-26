"""
BREAK EVEN OR BROKE
"""

import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib, OCTlib
import matplotlib.pyplot as plt
import os
os.chdir(r'C:/qrlab/scripts')


qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
cavity_infoA = mclient.get_qubit_info('cavityA')
#cavity_infoR = mclient.get_qubit_info('cavityR')
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
#cAs = cavity_infoAs.rotate
ge = qubit_info.rotate
geqs = qubit_info.rotate_quasilective
ges = qubit_info.rotate_selective
ges_a1 = qubit_a1.rotate_selective
ges_a2 = qubit_a2.rotate_selective
ges_a3 = qubit_a3.rotate_selective

chi2 = 2.655e6
chi2s = 2.679e6
chi2n = 2.675e6

cav_amp = 114.8
qt_amp = 43.3
time_shift = 11  
lib = OCTlib.octlib(qt_amp, cav_amp, time_shift, qubit_info, cavity_infoA)

#ss = 2.091e6   #AQEC condition #1 ~8us rates circa 9/26
#fwm_comb = OCTlib.comb(fwm_info, [0, chi2, chi2*2, chi2*3], [x*0.2 for x in [-1.08, 0.90, 0.55, 0.57]], vary = [1]*4, stark_shift = ss)
#ge_comb = OCTlib.comb(qubit_info, [0, -chi2, -chi2*2, -chi2*3], [y*1.0e-3 for y in [-.9, 1.15, 1.0, 1.33]], vary = [-1]*4, stark_shift = -ss)

#ss = 2.509e6    #AQEC condition #2 ~5us rates circa 10/4 
#fwm_comb = OCTlib.comb(fwm_info, [0, chi2, chi2*2, chi2*3], [x*0.2 for x in [-1.20, 1.00, 0.62, 0.56]], vary = [1]*4, stark_shift = ss)
#ge_comb = OCTlib.comb(qubit_info, [0, -chi2, -chi2*2, -chi2*3], [y*1.0e-3 for y in [-1.03, 1.58, 1.35, 1.75]], vary = [-1]*4, stark_shift = -ss)

#ss = 2.8045e6    #AQEC condition #M0  11/28, kappa = 0.174+/-0.002 1/us
#fwm_comb = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.2, 1.03, 0.62, 0.45]], vary = [1]*4, stark_shift = ss,
#                       phases = [np.pi, 0, 0, 0])
#ge_comb = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [0.92, 1.55, 1.25, 1.13]], 
#                      vary = [-1]*4, stark_shift = -ss, phases = [np.pi, 0, 0, 0])
        
#ss = 2.834e6     #AQEC condition #MPtemp
#fwm_comb = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.22, 1.00, 0.64, 0.49]], vary = [1]*4, stark_shift = ss,
#                       phases = [np.pi, 0, 0, 0])
#ge_comb = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [1.07, 1.49, 1.27, 1.12]], 
#                      vary = [-1]*4, stark_shift = -ss, phases = [np.pi-0.64, -0.14, 0.14, 0.00])

#ss = 2.829e6     #AQEC condition #MP-
#fwm_comb = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.22, 1.00, 0.64, 0.49]], vary = [1]*4, stark_shift = ss,
#                       phases = [np.pi, 0, 0, 0])
#ge_comb = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [1.06, 1.54, 1.26, 1.12]], 
#                      vary = [-1]*4, stark_shift = -ss, phases = [np.pi-0.54, -0.14, 0.32, 0.20])

#ss = 2.820e6    #AQEC condition #MP+  12/20
#fwm_comb = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.22, 1.01, 0.64, 0.47]], vary = [1]*4, stark_shift = ss,
#                       phases = [np.pi, 0, 0, 0])
#ge_comb = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [1.28, 1.87, 1.56, 1.36]],
#                      vary = [-1]*4, stark_shift = -ss, phases = [np.pi-0.76, -0.10, 0.13, 0.02])
#rot_speed_MPt = 18.37


#ss = 2.804e6    #AQEC condition #P135
#fwm_comb = OCTlib.comb(fwm_info, [0, chi2, chi2*2, chi2*3], [x*0.2 for x in [1.21, 1.00, 0.63, 0.50]], vary = [1]*4, stark_shift = ss,
#                               phases = [np.pi, 0, 0, 0])
#ge_comb = OCTlib.comb(qubit_info, [0, -chi2, -chi2*2, -chi2*3], [y*1.0e-3 for y in [1.03, 1.60, 1.29, 1.30]], 
#                              vary = [-1]*4, stark_shift = -ss, phases = [np.pi-0.3, 0.0, 0.1, 0.0])

#ss = 2.779e6    #non-uniform chi
#fwm_comb = OCTlib.comb(fwm_info, [0, chi2, chi2*2, chi2*3], [x*0.2 for x in [1.21, 1.00, 0.63, 0.50]], vary = [1]*4, stark_shift = ss,
#                               phases = [np.pi, 0, 0, 0])
#ge_comb = OCTlib.comb(qubit_info, [0-delta, -chi2+delta, -chi2*2+delta, -chi2*3-delta], [y*1.0e-3 for y in [1.00, 1.56, 1.25, 1.14]], 
#                              vary = [-1]*4, stark_shift = -ss, phases = [np.pi-0.42, 0.1, 0.2, 0.1])
       
#ss = 2.526e6    #AQEC condition #ML
#fwm_comb = OCTlib.comb(fwm_info, [0, chi2n, chi2n*2, chi2n*3], [x*0.2 for x in [1.17, 0.91, 0.59, 0.48]], vary = [1]*4, stark_shift = ss,
#                       phases = [-np.pi, 0, 0, 0])
#ge_comb = OCTlib.comb(qubit_info, [0, -chi2n, -chi2n*2, -chi2n*3], [y*1.0e-3 for y in [1.14, 1.62, 1.37, 1.20]],
#                      vary = [-1]*4, stark_shift = -ss, phases =[np.pi-0.75, -0.10,  0.12, -0.10])


#ss = 2.918e6   #oxy  
#fwm_comb4 = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.22, 1.00, 0.64, 0.49]], vary = [1]*4, stark_shift = ss,
#                   phases = [np.pi, 0, 0, 0])
#ge_comb4 = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [0.770, 1.314, 1.114, 0.991]], 
#                  vary = [-1]*4, stark_shift = -ss, phases = [2.46, -0.14, -0.05, -0.45])
#rot_speed4 = 18.79


ss1 = 2.900e6
fwm_comb1 = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.22, 1.00, 0.64, 0.49]], vary = [1]*4, stark_shift = ss1,
                       phases = [np.pi, 0, 0, 0])
ge_comb1 = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [1.06, 1.54, 1.29, 1.12]], 
                      vary = [-1]*4, stark_shift = -ss1, phases = [np.pi-0.66, -0.14, 0.29, 0.30])
rot_speed1 = 18.82


ss = 2.868e6     #OMP
fwm_comb5 = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.22, 1.00, 0.64, 0.49]], vary = [1]*4, stark_shift = ss,
                   phases = [np.pi, 0, 0, 0])
ge_comb5 = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [0.98, 1.52, 1.27, 1.14]], 
                  vary = [-1]*4, stark_shift = -ss, phases = [2.576, -0.14, -0.116, -0.49])


if 0: # poly ssbspec to find stark shift
    from FWM import poly_fwm_ssbspec
#    ss = 2.776e6  # AQEC condition #MP established 11/29, kappa = 0.175+/-0.003 /us, phase matched within 0.04 radian
#    fwm_comb = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.2, 1.02, 0.62, 0.47]], vary = [1]*4, stark_shift = ss,
#                           phases = [np.pi, 0, 0, 0])
#    ge_comb = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [1.00, 1.56, 1.25, 1.14]], 
#                          vary = [-1]*4, stark_shift = -ss, phases = [np.pi-0.42, -0.10, 0.12, 0.10])      
    
    freqs = np.linspace(-0.2e6, 0.2e6, 51)
    delay_times=[10e3]
    seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state_two_file('2')])
    for delay_t in delay_times:
        ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(qubit_a3, [fwm_comb, ge_comb],
                                                freqs, delay_t, post_delay = 1e3,
                                                seq = None, plot_seqs = False,
                                                bgcor = True,
                                                extra_info = [qubit_info, cavity_infoA]
                                                )
        ssb.measure_keysight()
    bla
    
    
if 0: # 2d poly ssbspec to find stark shift
    from FWM import poly_fwm_ssbspec2d
    dig.set_trigger_period(2000)
    dig.set_naverages(1200)
    fwm_freqs = np.linspace(-0.6e6, 0.6e6, 13)
    ge_freqs = np.linspace(-0.08e6, 0.08e6, 9)
    delay_times=[10e3]
    seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state_two_file('2')])
    for delay_t in delay_times:
        ssb2d = poly_fwm_ssbspec2d.poly_fwm_ssbspec2d(qubit_a3, fwm_comb, ge_comb,
                                                fwm_freqs, ge_freqs, delay_t,
                                                seq = seq, post_delay = 1e3, bgcor = True,
                                                extra_info = [qubit_info, cavity_infoA]
                                                )
        ssb2d.measure_keysight()
    bla

    
if 0: # time domain
    from FWM import poly_time_domain
    comb_list = [fwm_comb, ge_comb]
    qubit_list = [
#                  qubit_info, 
                  qubit_a1, 
#                  qubit_a2, 
                  qubit_a3, 
#                  qubit_a4, 
                  qubit_a5,
#                  qubit_a6,
                  qubit_a7
                  ]
#    delays = np.concatenate((np.linspace(0e3, 18e3, 5),
#                             np.linspace(20e3, 350e3, 21),
#                             ))
    delays = np.linspace(6e6, 7e6, 2)
    seq = sequencer.Join([sequencer.Trigger(200)])
    td = poly_time_domain.poly_time_domain(comb_list, qubit_list, delays,
                                       plot_seqs=False, bgcor=True, seq=seq, 
                                       extra_info = [qubit_info, cavity_infoA],
                                       )
    td.measure_keysight()
    bla


if 0: # Measure all four e-o rates
    from FWM import poly_fwm_ssbspec
    from FWM import poly_time_domain
    
#for f3 in np.linspace(1.28, 1.32, 1):
    for g3 in np.linspace(1.17, 1.27, 1):
    
        '''Pure test for Gamma up'''  
#        sst = 1.791e6#0.91e6*1.4**2+17e3
#        fwm_comb = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.4, 0.00, 0, 0]], vary = [1]*4, stark_shift = sst,
#                               phases = [np.pi, 0, 0, 0])
#        ge_comb = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [1.25, 0, 0, 0]],
#                              vary = [-1]*4, stark_shift = -sst, phases = [np.pi-0.54, -0.10, 0.20, 0.08])

        delays = np.concatenate((np.linspace(0e3, 7e3, 8), np.linspace(8e3, 40e3, 17)))#, np.linspace(44e3, 60e3, 5)))
#        delays = np.linspace(0e3, 80e3, 21)
#        delays = np.linspace(1.86e6, 1.90e6, 3)

        dig.set_trigger_period(2000)
        freqs = np.linspace(-0.2e6, 0.2e6, 41)
        dig.set_naverages(600)
        
        ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(qubit_a1, [fwm_comb, ge_comb], freqs, 20e3, post_delay = 1e3, seq = None,
                                                bgcor = False, extra_info = [qubit_info, cavity_infoA])
        dss0 = ssb.measure_keysight()

#        seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state_two_file('2')])
#        ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(qubit_a3, [fwm_comb, ge_comb], freqs, 10e3, post_delay = 1e3, seq = seq,
#                                                bgcor = False, extra_info = [qubit_info, cavity_infoA])
#        dss2 = ssb.measure_keysight()
#        
#        seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state_two_file('4')])
#        ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(qubit_a5, [fwm_comb, ge_comb], freqs, 10e3, post_delay = 1e3, seq = seq,
#                                                bgcor = False, extra_info = [qubit_info, cavity_infoA])
#        dss4 = ssb.measure_keysight()
#    
#        seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state('6')])
#        ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(qubit_a7, [fwm_comb, ge_comb], freqs, 10e3, post_delay = 1e3, seq = seq,
#                                                bgcor = False, extra_info = [qubit_info, cavity_infoA])
#        dss6 = ssb.measure_keysight()
#
#        ss -= (dss0+dss2+dss4+dss6)/4
#        print 'dss=', dss0/1000, dss2/1000, dss4/1000, dss6/1000
#        print 'ss=', ss/1000
        ss -= (dss0+10e3)
        fwm_comb.stark_shift = ss
        ge_comb.stark_shift= -ss

#        sst -= dss0
#        fwm_comb.stark_shift = sst
#        ge_comb.stark_shift= -sst      
        
#        dig.set_trigger_period(2000)
#        dig.set_naverages(1500)
#        td0 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a1], delays, bgcor=True, seq=None, 
#                                           extra_info = [qubit_info, cavity_infoA])
#        hl0 = td0.measure_keysight()
#        
#        seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state_two_file('2')])
#        td2 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a3], delays, bgcor=True, seq=seq, 
#                                           extra_info = [qubit_info, cavity_infoA])
#        hl2 = td2.measure_keysight()
#        
#        dig.set_trigger_period(2500)
#        dig.set_naverages(2000)
#        seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state_two_file('4')])
#        td4 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a5], delays, bgcor=True, seq=seq, 
#                                           extra_info = [qubit_info, cavity_infoA])
#        hl4 = td4.measure_keysight()
#        
#        seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state('6')])
#        td6 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a7,], delays, bgcor=True, seq=seq,
#                                           extra_info = [qubit_info, cavity_infoA])
#        hl6 = td6.measure_keysight()
#        
#        print(hl0, hl2, hl4, hl6)
            
#    bla
    

if 1: # SSB after e-o dissipation
    from single_qubit import ssbspec
    dig.set_trigger_period(2000)
    dig.set_naverages(6000)
    times = [1.7e6]#np.arange(20e3, 40e3, 1e3)
    infos = [fwm_comb5.info, ge_comb5.info]
#    seq = [sequencer.Join([sequencer.Trigger(200), lib.prekerr()])]
#    seq = [sequencer.Join([sequencer.Trigger(200), lib.mod4_prep('+x')])]    
#    seq = [sequencer.Join([sequencer.Trigger(200), ge(np.pi/2, 0), lib.fock01_encode()])]
#    seq = [sequencer.Trigger(200), lib.fock_state('02')]
    for dt in times:
        seq = [sequencer.Trigger(200)]
        if dt>0:
#            poly_seq = sequencer.Combined(fwm_comb5.get_poly_seq(dt - fwm_comb5.sigma*4, 0) + ge_comb5.get_poly_seq(dt - ge_comb5.sigma*4, 0))
            poly_seq = sequencer.Sequence(fwm_comb5.get_poly_seq(dt - fwm_comb5.sigma*4, 0))
            seq += [poly_seq]
            
        spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
                                            np.linspace(-4.5e6, 0.5e6, 101),
                                            )), 
                                seq=sequencer.Join(seq), 
                                extra_info = infos + [cavity_infoA]
                                )
        spec.measure_keysight()
    bla    

if 0: # Q function w/ e-o dissipation on coherence state
    from scripts.single_cavity import Qfunction
    
    infos = [fwm_comb.info, ge_comb.info]
    for dt in [130e3]:
        seq = sequencer.Join([sequencer.Trigger(200), None])
        if dt>0:
            seq.append(sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0)))
            
        Qfun = Qfunction.QFunction(qubit_info, cavity_infoA, amax=2.1, N=15, amaxx=None, Nx=None, amaxy=None, Ny=None,
             seq=seq, postseq=None, delay=5, bgcor=False, 
             extra_info = infos+ [qubit_info, cavity_infoA]
             )
        Qfun.measure_keysight()
    bla


if 0: # W function after e-o dissipation on prepared state
    from scripts.single_cavity import WignerbyParity
    dig.set_naverages(200)
    dig.set_trigger_period(2500)
#    times = np.linspace(55e3, 70e3, 10)
    times = np.array([142e3])
    infos = [fwm_comb1.info, ge_comb1.info]
    bloch = [
#         '-z', 
#         '+z',
#         '-x', 
         '+x', 
#         '-y',
#         '+y',
         ]

    for i, state in enumerate(bloch):
#        rotation = .0026*1.4*2*np.pi+.0075* 2*np.pi
        for dt in times:
            rotation = 18.22/1e3*(dt/1e3+1.1)*2*np.pi  #18.22 kHz rotating frame, 1us for effective time of state prep+Wigner prep
            seq = [sequencer.Join([sequencer.Trigger(200), lib.mod4_prep(state)])]
            if dt>0:
                poly_seq = sequencer.Combined(fwm_comb1.get_poly_seq(dt - fwm_comb1.sigma*4, 0) + ge_comb1.get_poly_seq(dt - ge_comb1.sigma*4, 0))
                seq += [poly_seq]
#                seq += [sequencer.Delay(dt)]
            
            Wfun = WignerbyParity.WignerFunction(qubit_a4, ef_info, cavity_infoA, 
                                     xs = np.linspace(-2,2,25), ys = np.linspace(-2,2,25),
                                     t_ge=356, t_gf=0,
                                     seq=seq, delay=5, bgcor=True, zmax=100, zmin=-100, 
                                     extra_info = infos+ [qubit_info],
                                     rotation = rotation
                                     )
            Wfun.measure_keysight()
            
#            n = 35
#            full_range = np.linspace(-2.5, 2.5, n)
#            for i in range(2,5):
#                Wfun = WignerbyParity.WignerFunction(qubit_a4, ef_info, cavity_infoAs, 
#                                         xs = full_range[i*n/5: (i+1)*n/5], ys = full_range,
#                                         t_ge=356, t_gf=0,
#                                         seq=seq, delay=5, bgcor=True, zmax=100, zmin=-100, 
#                                         extra_info = [qubit_info, cavity_infoA],
##                                         rotation = rotation
#                                         )
#                Wfun.measure_keysight()
            
    bla
    
    
if 0: # W function after e-o dissipation on fock superposition
    from scripts.single_cavity import WignerbyParity
#    times = np.array([0, 7.5e3, 15e3])
    dt = 25e3
    infos = [fwm_comb.info, ge_comb.info]

#    phases = np.linspace(0, 2*np.pi/2, 5)
    states = ['02', '24', '46']
    dig.set_naverages(1500)
    dig.set_trigger_period(4000)

    for state in states:
        seq = [sequencer.Trigger(200), lib.fock_state(state)]
        
#        Wfun = WignerbyParity.WignerFunction(qubit_a4, ef_info, cavity_infoA, 
#                                 xs = np.linspace(-1.8,1.8,17), ys = np.linspace(-1.8,1.8,17),
#                                 t_ge=356, t_gf=0,
#                                 seq=seq, delay=5, bgcor=True, zmax=100, zmin=-100, 
#                                 extra_info = infos+ [qubit_info],
##                                 rotation = .0026*1.4*2*np.pi+  .0075* 2*np.pi
#                                 )
#        Wfun.measure_keysight()  
        
        
#        Wfun = WignerbyParity.WignerFunction(qubit_a4, ef_info, cavity_infoA, 
#                                 xs = np.linspace(-1.8,1.8,17), ys = np.linspace(-1.8,1.8,17),
#                                 t_ge=356, t_gf=0,
#                                 seq=seq + [sequencer.Delay(dt)], delay=5, bgcor=True, zmax=100, zmin=-100, 
#                                 extra_info = infos+ [qubit_info],
##                                 rotation = .0026*1.4*2*np.pi+  .0075* 2*np.pi
#                                 )
#        Wfun.measure_keysight()  
#        
#        if dt>0:
#            poly_seq = sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0))
#            seq += [poly_seq]
##            seq += [sequencer.Delay(dt)]
#        
        n = 27
        full_range = np.linspace(-2.5, 2.5, n)
        for rep in range(2):
            for i in range(3):
                Wfun = WignerbyParity.WignerFunction(qubit_a4, ef_info, cavity_infoA, 
                                         xs = full_range[i*n/3: (i+1)*n/3], ys = full_range,
                                         t_ge=356, t_gf=0,
                                         seq=seq, delay=5, bgcor=True, zmax=120, zmin=-120, 
                                         extra_info = infos+ [qubit_info, cavity_infoA],
                                         rotation = 0
                                         )
                Wfun.measure_keysight()
            
    bla
    
if 0: # Calibrate selective pi pulse at different photon numbers
    from single_qubit import rabi
    tr = rabi.Rabi(qubit_a4, 
                   np.linspace(-0.8, 0.8, 51), selective=False,    
#                  np.linspace(-0.025, 0.025, 51), selective=True,
#                   np.linspace(-0.1, 0.1, 41), selective=.5,
                   plot_seqs=False, generate=True, repeat_pulse=2, update=False, 
                   seq=sequencer.Join([sequencer.Trigger(200), lib.fock_state_two_file('4')]),
                   extra_info=[cavity_infoA, qubit_info])
    tr.measure_keysight()
    bla

if 0: # Ramsey measurement with selective pulses at different photon numbers
    from single_qubit import T2measurement
    t2 = T2measurement.T2Measurement(qubit_a2, np.linspace(0e3, 20e3, 101), detune=.4e6,
                                     double_freq=False, generate=True, seq=None, selective=True, extra_info=[cavity_infoA, qubit_info])
    t2.measure_keysight()
    bla
    
    
if 0: # Test qubit pop after fwm tone
    from single_qubit import rabi
    tr = rabi.Rabi(fwm_info, 
#                   np.linspace(-0.9, 0.9, 101), selective=False,
                  np.linspace(-0.4, 0.4, 51), selective=True,
#                   np.linspace(-0.1, 0.1, 41), selective=.5,
                   plot_seqs=False, generate=True, repeat_pulse=1, update=False, seq=None,
                   postseq = sequencer.Delay(2e3))
    tr.measure_keysight()
    bla


if 0: # Q rotation test
    dig.set_trigger_period(2000)
    dig.set_naverages(2000)
    from AQEC import husimiq_angle_test
    infos = [fwm_comb.info, ge_comb.info]
        
#    times = np.linspace(0e3, 150e3, 11)
    times = np.concatenate((np.array([0]), np.linspace(25e3, 115e3, 7)))

    qphases = np.zeros_like(times)
    qamps = np.zeros_like(times)
    qsigmas = np.zeros_like(times)
    
    for i, dt in enumerate(times):
#    for i in [0]:
#        dt = times[i]
#        seq = [sequencer.Trigger(200), lib.mod4_prep('+x')]
        seq = [sequencer.Trigger(200), lib.fock_state('02')]
        
        if dt>0:
            poly_seq = sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0))
            seq += [poly_seq]
#            seq += [sequencer.Delay(dt)]       
            
        qa = husimiq_angle_test.husimiq_angle_test(qubit_info, cavity_infoAs, 31, 
                                                 1.35, bgcor = False, fit = 20, plot_seqs = False,
                                                 seq = seq, extra_info = [qubit_info, cavity_infoA] + infos)

        result = qa.measure_keysight()
        params = result.params
        qphases[i] = params['phase']
        qamps[i] = params['amp']
        qsigmas[i] = params['background']
        
    plt.figure()
    plt.subplot(3,1,2)
    plt.plot(times/1e3, qamps, '.')
    plt.ylabel('amps')
    plt.subplot(3,1,3)
    plt.plot(times/1e3, qsigmas, '.')
    plt.ylabel('background')
    plt.xlabel('times [us]')
    plt.subplot(3,1,1)
    plt.plot(times/1e3, qphases, '.')
    plt.ylabel('phases')

    plt.figure()    
    plt.plot(times/1e3, qphases, '.')
    pf = np.polyfit(times[2:]/1e3, qphases[2:], 1)
    plt.plot(times/1e3, pf[0]*times/1e3+pf[1], linestyle='-')
    print pf[0], pf[1]
        
    bla            
    
    
if 0: # wigner rotation test
    dig.set_trigger_period(2500)
    dig.set_naverages(2500)
    from AQEC import wigner_angle_test
    infos = [fwm_comb.info, ge_comb.info]
        
    times = np.linspace(0e3, 240e3, 7)
#    times = np.concatenate([np.linspace(120e3, 160e3, 5),
#                            np.linspace(260e3, 300e3, 5),
#                            np.linspace(400e3, 440e3, 5),
#                            ])
    
    wphases = np.zeros_like(times)
    wphase_errs = np.zeros_like(times)
    wamps = np.zeros_like(times)
    wsigmas = np.zeros_like(times)
    for i, dt in enumerate(times):
#    for i in range(1,13):
#        dt = times[i]
        seq = [sequencer.Trigger(200), lib.mod4_prep('-z')]
        if dt>0:
            poly_seq = sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0))
            seq += [poly_seq]
#            seq.append(sequencer.Delay(dt))
            
        wa = wigner_angle_test.wigner_angle_test(qubit_a4, cavity_infoAs, 41, 
                                                 .76, t_ge  = 356, bgcor = True, fit = 4,
                                                 seq = seq, extra_info = [qubit_info, cavity_infoA] + infos)
        result = wa.measure_keysight()
        params = result.params
        wphases[i] = params['phase']
        wphase_errs[i] = params['phase'].stderr
        wamps[i] = params['amp']
        wsigmas[i] = params['sigma']
        
    plt.figure()
    plt.subplot(3,1,1)
    plt.plot(times/1e3, wphases)
    plt.ylabel('phases')
    plt.subplot(3,1,2)
    plt.plot(times/1e3, wamps)
    plt.ylabel('amps')
    plt.subplot(3,1,3)
    plt.plot(times/1e3, wsigmas)
    plt.ylabel('sigmas')
    plt.xlabel('times [us]')

    plt.figure()    
    plt.plot(times/1e3, wphases, '.')
    pf = np.polyfit(times[1:]/1e3, wphases[1:], 1)
    plt.plot(times/1e3, pf[0]*times/1e3+pf[1], linestyle='-')
    print 'slope=', pf[0], ', interception=', pf[1]


    dig.set_naverages(3200)
    phases = np.zeros_like(times)
    phase_errs = np.zeros_like(times)
    amps = np.zeros_like(times)
    sigmas = np.zeros_like(times)
    for i, dt in enumerate(times):
#    for i in [6,9]:
#        dt = times[i]
        seq = [sequencer.Trigger(200), lib.mod4_prep('+z')]
        if dt>0:
            poly_seq = sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0))
            seq += [poly_seq]
#            seq.append(sequencer.Delay(dt))
            
        wa = wigner_angle_test.wigner_angle_test(qubit_a4, cavity_infoAs, 41, 
                                                 .53, t_ge  = 356, bgcor = True, fit = 4,
                                                 seq = seq, extra_info = [qubit_info, cavity_infoA] + infos)
        result = wa.measure_keysight()
        params = result.params
        phases[i] = params['phase']
        phase_errs[i] = params['phase'].stderr
        amps[i] = params['amp']
        sigmas[i] = params['sigma']
        
    plt.figure()
    plt.subplot(3,1,1)
    plt.plot(times/1e3, phases)
    plt.ylabel('phases')
    plt.subplot(3,1,2)
    plt.plot(times/1e3, amps)
    plt.ylabel('amps')
    plt.subplot(3,1,3)
    plt.plot(times/1e3, sigmas)
    plt.ylabel('sigmas')
    plt.xlabel('times [us]')

    plt.figure()    
    plt.plot(times/1e3, phases, '.')
    pf = np.polyfit(times[:]/1e3, phases[:], 1)
    plt.plot(times/1e3, pf[0]*times/1e3+pf[1], linestyle='-')
    print 'slope=', pf[0], ', interception=', pf[1]
        
    bla

    
        
if 0: # bloch characterization
    dig.set_trigger_period(2500)
    from AQEC import time_bloch
    from single_cavity import cavT2
    
#    times = np.arange(0, 400e3, 72.6e3/2)
#    times = np.linspace(0, 300e3, 13)
    
    bloch = [
#             '-z', 
#             '+z',
#             '-x', 
#             '+x', 
#             '-y',
             '+y',
             ]
    bloch_targets = [
#                     [0, 0, -1],
#                     [0, 0, 1],
#                     [-1, 0, 0],
#                     [1, 0, 0],
#                     [0, -1, 0], 
                     [0, 1, 0]
                     ]
#    kerr_corrections = [
#                        [0, 0, 0, 0] * (len(times)/4) + [0, 0, 0, 0][:len(times)%4],
#                        [0, 0, 0, 0] * (len(times)/4) + [0, 0, 0, 0][:len(times)%4],
#                        [0, 1, 2, 3] * (lsen(times)/4) + [0, 1, 2, 3][:len(times)%4],
#                        [0, 1, 2, 3] * (len(times)/4) + [0, 1, 2, 3][:len(times)%4],
#                        [0, 1, 2, 3] * (len(times)/4) + [0, 1, 2, 3][:len(times)%4],
#                        [0, 1, 2, 3] * (len(times)/4) + [0, 1, 2, 3][:len(times)%4],
#                        ]

#    times = np.concatenate((np.linspace(0, 72e3, 2), np.linspace(130e3, 160e3, 5), np.linspace(195e3, 245e3, 9), np.linspace(260e3, 320e3, 5)))
    
    for i, state in enumerate(bloch):

        dig.set_naverages(3000)

#            ss = 2.770e6  # AQEC condition #MP established 11/29, kappa = 0.175+/-0.003 /us, phase matched within 0.04 radian
#            fwm_comb = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.2, 1.02, 0.62, 0.47]], vary = [1]*4, sigma=100, stark_shift = ss,
#                                   phases = [np.pi, 0, 0, 0])
#            ge_comb = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [1.00, 1.56, 1.25, 1.14]], sigma=100,
#                                  vary = [-1]*4, stark_shift = -ss, phases = [np.pi-0.42, -0.10, 0.12, 0.10])

#            target = bloch_targets[i]
        ss = 2.842e6     #AQEC condition #MP-  12/22
        fwm_comb = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.22, 1.00, 0.64, 0.49]], vary = [1]*4, stark_shift = ss,
                               phases = [np.pi, 0, 0, 0])
        ge_comb = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [1.06, 1.54, 1.26, 1.12]], 
                              vary = [-1]*4, stark_shift = -ss, phases = [np.pi-0.54, -0.14, 0.32, 0.20])

        times = np.arange(0, 340e3, 71.5e3)
        seq = [sequencer.Join([sequencer.Trigger(200), lib.mod4_prep(state)])]            
        tb = time_bloch.time_bloch(qubit_info, times, seq = seq,
                                   target_state = 'purity',
                                   postseq = lib.mod4_decode,
                                   background_fidelity = 0.001,
#                                       kerr_correction = [0, 0, 0, 0, 0, 0],
                                   comb_list = [fwm_comb, ge_comb],
#                                       measure_ge = True,
                                   g_value = 145, e_value = 21.5,
                                   rotations = rotations,
                                   extra_info = [cavity_infoA],
                                   secondary_decode = False
                                   )
        tb.measure_keysight()
#
#            ss = 2.842e6     #AQEC condition #MPtemp
#            fwm_comb = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.22, 1.00, 0.64, 0.49]], vary = [1]*4, stark_shift = ss,
#                               phases = [np.pi, 0, 0, 0])
#            ge_comb = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [1.07, 1.49, 1.27, 1.12]], 
#                              vary = [-1]*4, stark_shift = -ss, phases = [np.pi-0.64, -0.14, 0.14, 0.00])        
#  
##            target = bloch_targets[i]
#            times = np.arange(0, 340e3, 71.5e3)
#            rotations = times/1.0e6 * 2*np.pi*rot_speed
#            seq = [sequencer.Join([sequencer.Trigger(200), lib.mod4_prep(state)])]
#            tb = time_bloch.time_bloch(qubit_info, times, seq = seq,
#                                       target_state = 'purity',
#                                       postseq = lib.mod4_decode,
#                                       background_fidelity = 0.001,
##                                       kerr_correction = kerr_corrections[i],
#                                       comb_list = [fwm_comb, ge_comb],
##                                       measure_ge = True,
#                                       g_value = 145, e_value = 21.5,
#                                       rotations = rotations,
#                                       extra_info = [cavity_infoA],
#                                       )
#            tb.measure_keysight()
#            
#            dig.set_naverages(1000)
#            ct2 = cavT2.CavT2(qubit_info, cavity_infoA, .7, np.linspace(0, 500e3, 41), detune=10e3, seq=None,
#                               postseq=None, bgcor=False)
#            ct2.measure_keysight()

#            seq = [sequencer.Join([sequencer.Trigger(200), ge(np.pi/2, -np.pi/2), lib.fock01_encode()])]
#            tbf = time_bloch.time_bloch(qubit_info, times, seq = seq,
#                                       target_state = [1, 0, 0],
##                                       postseq = lib.fock01_encode(),
#                                       background_fidelity = 0.5,
#                                       g_value = 175, e_value = 23,
#                                       extra_info = [cavity_infoA])
#            tbf.measure_keysight()

        
#            seq = [sequencer.Join([sequencer.Trigger(200), ge(np.pi/2, -np.pi/2), lib.fock01_encode()])]
#            tbf = time_bloch.time_bloch(qubit_info, times, seq = seq,
#                                       target_state = [1, 0, 0],
#                                       postseq = lib.fock01_encode(),
#                                       background_fidelity = 0.5,
#                                       g_value = 175, e_value = 23,
#                                       extra_info = [cavity_infoA])
#            tbf.measure_keysight()
#    ct2 = cavT2.CavT2(qubit_info, cavity_infoA, .7, np.linspace(0, 500e3, 41), detune=10e3, echo=True, seq=None,
#                      postseq=None, bgcor=False)
#    ct2.measure_keysight()
    bla            


if 0: # Preekerr Optimization
    from FWM import poly_fwm_ssbspec
    from AQEC import prekerr_optimize, prekerr_calibrate

    dig.set_naverages(1500)
    dig.set_trigger_period(2500)    
    
#    pc = prekerr_calibrate.prekerr_calibrate(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb], #pump_time=72e3,
#                                           phases = np.linspace(0, np.pi, 25))
#    params = pc.measure_keysight()
#    phase = params['phase'].value

#    ss = 2.842e6     #AQEC condition #MP-
#    fwm_comb = OCTlib.comb(fwm_info, [0, chi2s, chi2s*2, chi2s*3], [x*0.2 for x in [1.22, 1.00, 0.64, 0.49]], vary = [1]*4, stark_shift = ss,
#                           phases = [np.pi, 0, 0, 0])
#    ge_comb = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1.0e-3 for y in [1.06, 1.54, 1.26, 1.12]], 
#                          vary = [-1]*4, stark_shift = -ss, phases = [np.pi-0.54, -0.14, 0.32, 0.20])

    pc = prekerr_calibrate.prekerr_calibrate(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb], #pump_time=72e3,
                                           phases = np.linspace(0, np.pi, 25))
    params = pc.measure_keysight()
    phase = params['phase'].value
        
    dig.set_naverages(4000)
    dig.set_trigger_period(2000)
    
    for parameter in ['ge_phase_2', 'ge_phase_0', 'ge_phase_3']:
        po = prekerr_optimize.prekerr_optimize(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb], 
                                          parameter, np.linspace(-0.7, 0.7, 26), phase = phase-np.pi/2)
        po.measure_keysight()
    
    for parameter in ['ge_amp_1', 'ge_amp_2']:
        po = prekerr_optimize.prekerr_optimize(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb], 
                                          parameter, np.linspace(0.65, 1.35, 26), phase = phase-np.pi/2)
        po.measure_keysight()

#    for parameter in ['fwm_amp_0', 'fwm_amp_1', 'fwm_amp_2', 'fwm_amp_3']:
#        po = prekerr_optimize.prekerr_optimize(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb], 
#                                          parameter, np.linspace(0.97, 1.03, 31),
#                                          phase = 0.66)
#        po.measure_keysight()
#    
#    po = prekerr_optimize.prekerr_optimize(qubit_info, cavity_infoA, lib, [fwm_comb, ge_comb], 
#                                      'ge_amp_9', np.linspace(0.6, 1.5, 26),
#                                      phase = phase-np.pi/2)
#    po.measure_keysight()
#        
    bla
    
    
        
if 0: #T2 with AQEC on any pre-seq
    from AQEC import CavT2_AQEC
    dig.set_trigger_period(2500)
    dig.set_naverages(2500)
    detune = 15e3
#    disps = [1.3, 1.65, 1.65]
    delays = np.linspace(10e3, 210e3, 41)
#    for i, state in enumerate(['02']):
    for i in range(2):
        seq = [sequencer.Trigger(200), lib.mod4_prep('+z')]
#        seq = [sequencer.Trigger(200), lib.fock_state(state)]
        ct2 = CavT2_AQEC.CavT2_AQEC(qubit_info, cavity_infoA, 0.5, delays, comb_list=[fwm_comb, ge_comb], 
                                    detune=detune, seq=seq,
                                    postseq=None, bgcor=True, t_ge=356)
        ct2.measure_keysight()
        
#        seq = [sequencer.Trigger(200), lib.fock_state(state)]
#        ct2 = CavT2_AQEC.CavT2_AQEC(qubit_info, cavity_infoA, disps[i], delays, comb_list=[fwm_comb, ge_comb], 
#                                    detune=detune, seq=seq,
#                                    postseq=None, bgcor=True, t_ge=356)
#        ct2.measure_keysight()
  
#    bla
    
    
if 0: # test Q function
    from scripts.single_cavity import Qfunction
    states = ['04', '06', '26']
    dt = 25e3
    dig.set_trigger_period(3000)
    dig.set_naverages(1000)   
    for state in states: 
        seq = [sequencer.Trigger(200), lib.fock_state(state)]
        poly_seq = sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0))
        seq += [poly_seq]
        Qfun = Qfunction.QFunction(qubit_info, cavity_infoA, amax=2.5, N=17, amaxx=None, Nx=None, amaxy=None, Ny=None,
                                   seq=sequencer.Join(seq), delay=0, saveas=None, bgcor=False)
        Qfun.measure_keysight()



if 1: # bloch time tests for fig4
    from AQEC import time_bloch
    rep = 10
    bloch = [
            [sequencer.Trigger(200)],  
             [sequencer.Trigger(200), ge(np.pi, 0)],  
             [sequencer.Trigger(200), ge(np.pi/2, 0)], 
             [sequencer.Trigger(200), ge(np.pi/2, np.pi/2)], 
             [sequencer.Trigger(200), ge(np.pi/2, np.pi)], 
             [sequencer.Trigger(200), ge(np.pi/2, np.pi*3/2)]
             ]
#    bloch = ['-y', 
#             '+y', '-x',  '+x', '-z', '+z'
#             ]

    bloch_targets = [[-1, 0, 0],
                     [1, 0, 0], 
                     [0, 1, 0], 
                     [0, -1, 0], 
                     [0, 0, -1],  [0, 0, 1], 
                     ]
    rot_speed = 0
    for j in range(rep):
        
        for i, seq in enumerate(bloch[:]):
            dig.set_trigger_period(2000)
            dig.set_naverages(4000)   
            times = np.linspace(0, 250e3, 20)
#            times = np.arange(0, 250e3, 70.4e3)
#            times = np.linspace(40e3, 90e3, 10)
#            rotations = times/1.0e6 * 2*np.pi*rot_speed
            tb = time_bloch.time_bloch(qubit_info, times, seq = seq + [lib.fock01_encode()], target_state = 'purity',
                                       postseq = lib.fock01_encode,               
#            tb = time_bloch.time_bloch(qubit_info, times, seq = [sequencer.Trigger(200), lib.mod4_prep(seq)], target_state = 'purity',
#                                       postseq = lib.mod4_decode,
                                       g_value = 150, e_value = 22,
                                       extra_info = [cavity_infoA],
                                       secondary_decode = True,
                                       t2_check = None,
#                                       rotations = rotations
                                       )
            tb.measure_keysight()  
            
            dig.set_trigger_period(500)
            times = np.linspace(0, 150e3, 20)
            tb = time_bloch.time_bloch(qubit_info, times, seq = seq, target_state = 'purity',
                                       g_value = 150, e_value = 22,
                                       extra_info = [cavity_infoA],
                                       secondary_decode = True,
                                       t2_check = None)
            tb.measure_keysight()        
    
    
if 0: # time bloch tester
    from AQEC import time_bloch
    dig.set_trigger_period(2500)
    dig.set_naverages(2500)
    for i, state in enumerate(['-x']):
 
        fwm_comb, ge_comb = fwm_comb1, ge_comb1
        dig.set_naverages(1000)
        times = np.arange(0, 240e3, 36e3)
        rotations = times/1.0e6 * 2*np.pi*rot_speed1
        seq = [sequencer.Join([sequencer.Trigger(200), lib.mod4_prep(state)])]
        tb = time_bloch.time_bloch(qubit_info, times, seq = seq, target_state = 'purity',
                                   postseq = lib.mod4_decode, background_fidelity = 0.001,
                                   comb_list = [fwm_comb, ge_comb], g_value = 170, e_value = 3,
                                   rotations = rotations, extra_info = [cavity_infoA],
                                   secondary_decode = True, #t2_check = lib.fock01_encode
                                   )
        tb.measure_keysight() 
        
        
        
if 0: # Qubit t2 with AQEC
    from AQEC import T2_AQEC
    ss = 2.918e6
    comb_offset = 50e6
    fwm_comb_t2 = OCTlib.comb(fwm_info, [x+comb_offset for x in [0, chi2s, chi2s*2, chi2s*3]], [x*0.22 for x in [1.77, 0, 0, 0]],#[1.22, 1.00, 0.64, 0.49]], 
                              vary = [1]*4, stark_shift = ss, phases = [np.pi, 0, 0, 0])
#    ge_comb_t2 = OCTlib.comb(qubit_info, [0, -chi2s, -chi2s*2, -chi2s*3], [y*1e-3 for y in [0.770, 1.314, 1.114, 0.991]], 
#                      vary = [-1]*4, stark_shift = -ss, phases = [2.46, -0.14, -0.05, -0.45])
    rot_speed4 = 18.79
    
    dig.set_trigger_period(500)
    dig.set_naverages(2000)
    for i in range(1):
        t2 = T2_AQEC.T2_AQEC(qubit_info, np.linspace(1e3, 20e3, 101), [fwm_comb_t2], detune=2.7e6, 
                                         double_freq=False, generate=True, seq=None,
                                         plot_seqs=False)
        t2.measure_keysight()
    bla