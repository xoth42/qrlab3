import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib, OCTlib
#import matplotlib.pyplot as plt
import os
os.chdir(r'C:/qrlab/scripts')


import matplotlib.pyplot as plt


#alz = mclient.instruments['alazar']
#fg = mclient.instruments['funcgen']
os.chdir(r'C:/qrlab/scripts')
dig = mclient.instruments['dig']
#laserfg = mclient.instruments['laserfg']
#awg2 = mclient.instruments['AWG2']
#ag1 = mclient.instruments['ag1_RO']

#qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
#qubit2_info = mclient.get_qubit_info('qubit2tone')

#cavity_infoR = mclient.get_qubit_info('cavity1R')
cavity_infoA = mclient.get_qubit_info('cavityA')
#cavity_infoAs = mclient.get_qubit_info('cavityAs')
cavity_infoB = mclient.get_qubit_info('cavityB')
cavity_infoR = mclient.get_qubit_info('cavityR')
#Qswitch_info1A = mclient.get_qubit_info('Qswitch1A')
#Qswitch_info1B = mclient.get_qubit_info('Qswitch1B')

#qubit_info2 = mclient.get_qubit_info('qDblCoax2')
#ef_info2 = mclient.get_qubit_info('eDblCoax2')
#cavity_info2A = mclient.get_qubit_info('cavity2A')
#cavity_info2B = mclient.get_qubit_info('cavity2B')

fwm_info = mclient.get_qubit_info('fwm_info')


qubit_a1b1 = mclient.get_qubit_info('qubit_a1b1')



cA = cavity_infoA.rotate
cB = cavity_infoB.rotate
cR = cavity_infoR.rotate
#cBqs = cavity_infoB.rotate_quasilective
ge = qubit_info.rotate
ges= qubit_info.rotate_selective
geqs= qubit_info.rotate_quasilective
ges_a1b1 = qubit_a1b1.rotate_quasilective
#ef = ef_info.rotate
#efs= ef_info.rotate_selective
#efpi = sequencer.Sequence(ef_info.rotate(np.pi, 0))

#geqs2 = qubit2_info.rotate_quasilective

#fwm_info = mclient.get_qubit_info('FWM_info')

ss = 2.868e6     #OMP
fwm_comb = OCTlib.comb(fwm_info, [0], [.9], vary = [1], phases = [0])
res_comb = OCTlib.comb(cavity_infoR, [0], [.008], vary = [1], phases = [0])




if 1: # Cavity disp calibration
    from single_cavity import cavdisp

#for i in range(5):
#    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi, 0)])
#    dig.set_trigger_period(2000)
    disp = cavdisp.CavDisp(qubit_info, cavity_infoA, 2, 41, 0, seq=None,
                           delay=0, bgcor=True, update=False, generate=True,
                           plot_seqs = False
#                           Qswitch_infoA=Qswitch_infoB, Qswitch_infoB=Qswitch_infoB,
#                           extra_info=[Qswitch_infoA, Qswitch_infoB,],
                          )
    disp.measure_keysight()
    bla


if 0: # Cavity T1
    from single_cavity import cavT1
#    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi, 0)])
#    xs = np.concatenate((np.linspace(0e3, 50e3, 26), np.linspace(60e3, 1250e3, 55)))

    t1 = cavT1.CavT1(qubit_info, cavity_infoB, 2.2, np.linspace(1e3, 2000e3, 51),
                     proj_num=0, seq=None, postseq=None, bgcor=True, force_a0 = True
#                     extra_info=[ef_info,]
                     )
    t1.measure_keysight()
#    ys = t1.get_ys()
    bla

if 0: # Cavity T2
    from single_cavity import cavT2
    detune = 15e3
    ct2 = cavT2.CavT2(qubit_info, cavity_infoB, .7, np.linspace(10e3, 400e3, 91), detune=detune, seq=None,
                       postseq=None, bgcor=False, double_freq=False)
    ct2.measure_keysight()

    bla

if 0: # Cavity T2E
    from single_cavity import cavT2
    detune = 5e3
    ct2 = cavT2.CavT2(qubit_info, cavity_infoB, .7, np.linspace(0, 500e3, 41), detune=detune, echo=True, seq=None,
                       postseq=None, bgcor=False)
    ct2.measure_keysight()
    bla



    
if 0: # Cavity speco

    from single_cavity import cavspectroscopy
    cav_freq = 6086.78e6
    freq_range = .2e6
    cspec = cavspectroscopy.CavSpectroscopy(mclient.instruments['MXG'], qubit_info, cavity_infoB, [np.pi], 
                                            np.linspace(cav_freq-freq_range, cav_freq+freq_range, 51), plot_seqs=False)

    #This amplitude is NOT capped at 1 like on the qubit spec
    cspec.measure_keysight()
    bla


if 1: #SSB cavspec
    from single_cavity import ssbcavspec 
    cspec = ssbcavspec.SSBCavSpec(qubit_info, cavity_infoR, np.linspace(-2e6, 2e6, 61),
#                                  postseq=efpi, extra_info=[ef_info,]
                                  )
    cspec.measure_keysight()
    bla
    
if 0: #cavity stark shift
    from single_cavity import ssbcavspec
    s = sequencer.Trigger(250)
    delay = 400e3
    s.append(sequencer.Combined([
        pulselib.Constant(int(delay-30e3), 1, chan='4m1'),
        pulselib.Constant(int(delay-30e3), .1, chan=self.fwm_info.sideband_channels[0]),
        pulselib.Constant(int(delay-30e3), .1, chan=self.fwm_info.sideband_channels[1]),
    ]))
    s.append(pulselib.Delay(30e3))
    cspec = ssbcavspec.SSBCavSpec(qubit_info, cavity_infoA, np.linspace(-5e6, 5e6, 71),
#                                  postseq=efpi, extra_info=[ef_info,]
                                  )
    cspec.measure_keysight()
    bla


if 1: #Sideband modulated number splitting:
    from single_qubit import ssbspec
    dig.do_set_naverages(5000)
    delay_t = 10e3
    post_delay = 5e3
    poly_seq = []
    poly_seq += fwm_comb.get_poly_seq(delay_t - fwm_comb.sigma*4, .6e6)
    poly_seq += res_comb.get_poly_seq(delay_t - res_comb.sigma*4, -0.04e6)
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Combined(poly_seq),
#                          sequencer.Delay(post_delay)])
     #                     cR(-0.24, 0)]) # t2 seq test
    seq = sequencer.Join([sequencer.Trigger(250),cA(1.5, 0), cB(1.5,0)])
#                          sequencer.Combined(fwm_comb.get_poly_seq(5e3 - fwm_comb.sigma*4, .2e6)),
#                          sequencer.Delay(2e3)])
    spec = ssbspec.SSBSpec(qubit_info, #np.linspace(-30e6, 10e6, 21),
                           np.linspace(-16.5e6, -15e6, 101),
#                           np.concatenate((
#                                           np.linspace(-22e6, -18e6, 15),
#                                           np.linspace(-9.8e6, -6.8e6, 25), 
#                                           np.linspace(-1e6, 1e6, 25)
#                                           )),
#                           extra_info= [fwm_comb.info, res_comb.info],
                           extra_info= [cavity_infoA, cavity_infoB],
                           seq = seq,  plot_seqs=False,
                           bgcor = False)
    spec.measure_keysight()
    bla

if 0: #EF Sideband modulated number splitting:
    from single_qubit import ssbspec
    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoB.rotate(1, 0), qubit_info.rotate(np.pi,0)])
#    postseq = qubit_info.rotate(np.pi/2,0)
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi/2, 0))
    spec = ssbspec.SSBSpec(ef_info, np.concatenate((
#                                                    np.linspace(-22e6, -18e6, 71),  
#                                                    np.linspace(-12e6, -8e6, 71),
                                                    np.linspace(-10e6, 1e6, 91),
                                                    )),
                           extra_info= [qubit_info, cavity_infoB],
                           seq =seq,  postseq = postseq, plot_seqs=False)
    spec.measure_keysight()
    bla


if 0: # test Q function
    from scripts.single_cavity import Qfunction
    for dt in [65]:
        
        seq = sequencer.Join([sequencer.Trigger(250), cB(.75, 0), ge(np.pi, 0), 
                              sequencer.Delay(dt), cB(.75, 0), ge(np.pi, 0)])        
#        seq = sequencer.Join([sequencer.Trigger(250), cB(.75, 0), sequencer.Delay(dt)])
        Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=1, N=7, amaxx=None, Nx=None, amaxy=None, Ny=None,
                                   seq=seq, delay=0, saveas=None, bgcor=True)
        Qfun.measure_keysight()

#        seq = sequencer.Join([sequencer.Trigger(250), cB(1.0, np.pi/2)])
#        seq.append(sequencer.Delay(dt))
#    disp = 1.5
#    for dt in np.linspace(210, 220, 1):
#        seq = sequencer.Join([sequencer.Trigger(500), 
#                          cB(disp, 0), ge(np.pi/2, 0), 
#                          sequencer.Delay(dt), 
#                          cB(disp, 0),
#                          geqs(np.pi, 0),
#                          cB(-disp, 0)
#                          ])
#        seq = sequencer.Join(seq)
#        seq = sequencer.Combined([seq, pulselib.Constant(seq.get_length(), 1, chan='3m1')])
#        Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=1.75, N=15, amaxx=None, Nx=None, amaxy=None, Ny=None,
#                     seq=seq, delay=0, saveas=None, bgcor=False, extra_info=ef_info, cav_switch='3m1')
#        Qfun.measure_keysight()
    bla

if 0: # make a cat 
    from scripts.single_cavity import Qfunction
#    seq = sequencer.Join([sequencer.Trigger(250), cB(1.0, 0)])
#    Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=2.5, N=21, amaxx=None, Nx=None, amaxy=None, Ny=None,
#             seq=seq, delay=0, saveas=None, bgcor=False, extra_info=ef_info)
#    Qfun.measure()
    
#        seq = sequencer.Join([sequencer.Trigger(250), cB(1.0, np.pi/2)])
#        seq.append(sequencer.Delay(dt))
    disp = 1
    seq = sequencer.Join([sequencer.Trigger(500), 
                      cB(disp, 0), ge(np.pi, 0), 
                      sequencer.Delay(65), 
                      cB(disp, 0),
                      geqs(np.pi, 0),
                      cB(-disp, 0)
                      ])
    Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=1.7, N=9, amaxx=None, Nx=None, amaxy=None, Ny=None,
                 seq=seq, delay=0, saveas=None, bgcor=True, extra_info=ef_info)
    Qfun.measure_keysight()

#    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi/2, 0), 
#                          cB(disp, 0), sequencer.Delay(300), cB(disp,0), 
#                          sequencer.Combined([geqs2(np.pi, 0), geqs(np.pi, 0)]), 
#                          cB(-disp-1.3,0)])
#    Qfun = Qfunction.QFunction(qubit_info, cavity_infoA, amax=1.2, N=13, amaxx=None, Nx=None, amaxy=None, Ny=None,
#                 seq=seq, delay=0, saveas=None, bgcor=True, extra_info=ef_info)
#    Qfun.measure_keysight()
    
    
    bla


if 0: # Ramsey revival to calibrate wigner tomo
    from scripts.single_qubit import RamseyRevival
    seq = sequencer.Join([sequencer.Trigger(250), cB(1.5, 0)])
    rr = RamseyRevival.RamseyRevival(qubit_info, ef_info, np.linspace(0, 400, 81), 
                                     seq = seq, extra_info = cavity_infoB)
    rr.measure_keysight()

if 0: # Wigner function by displaced parity for cavity B
    from scripts.single_cavity import WignerbyParity
#    seq = sequencer.Join([prepareB, geph(pi/2,0), sequencer.Delay(950), cB(1.65, -pi*0.175),
#                          geqs(pi,0), cB(-1.65, -pi*0.02)])
#    seq = sequencer.Join([sequencer.Trigger(250), cB(.5, 0)])
    disp = 1.5
    seq = sequencer.Join([sequencer.Trigger(500), 
                      cB(disp, 0), ge(np.pi/2, 0), 
                      sequencer.Delay(65), 
                      cB(disp, 0),
                      geqs(np.pi, 0),
                      cB(-disp, 0)
                      ])

    
    Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoB,
                                         xs = np.linspace(-1.8,1.8,17), ys = np.linspace(-1.3,1.3,13),
                                         t_ge=70, t_gf=0,
                                         seq=seq, delay=5, bgcor=True, zmax=100, zmin=-100, 
                                         extra_info = None)
    Wfun.measure_keysight()

if 0: # Wigner function by displaced parity for cavity A
    from scripts.single_cavity import WignerbyParity
#    seq = sequencer.Join([prepareB, geph(pi/2,0), sequencer.Delay(950), cB(1.65, -pi*0.175),
#                          geqs(pi,0), cB(-1.65, -pi*0.02)])    
#    seq = sequencer.Join([sequencer.Trigger(250)])
    disp = 1.7
    seq = sequencer.Join([sequencer.Trigger(250), cA(disp, 0), 
                      ge(np.pi/2, 0), sequencer.Delay(270), cA(disp,0), 
                      geqs(np.pi, 0), 
                      cA(-disp,0)])
    Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoA,
                                         xs = np.linspace(-1.8,1.8,19), ys = np.linspace(-1.3,1.3,13),
                                         t_ge=270, t_gf=0,
                                         seq=seq, delay=5, bgcor=True, zmax=100, zmin=-100, 
                                         extra_info = None)
    Wfun.measure_keysight()


if 0: # Cavity cooling test
    from scripts.FWM import FWM_cavity_cooling
    freqs = np.linspace(-200.5e6, -199.5e6, 41)
#    freqs = np.array([200e6]*10)
    
    cc = FWM_cavity_cooling.FWM_cavity_cooling(qubit_info, cavity_infoA, cavity_infoR, freqs, .9, 
                 .9,1000e3)
    cc.measure_keysight()
    
    
    
    
if 0: # 2d poly ssbspec to find stark shift
    from FWM import poly_fwm_ssbspec2d
    dig.set_trigger_period(2500)
    dig.set_naverages(400)
    fwm_freqs =  np.linspace(0e6, 1.5e6, 21)
    res_freqs =  np.linspace(-1e6, 1e6, 21)
    delay_times=[20e3]
    amps = np.linspace(.008, .02, 1)
    seq = sequencer.Trigger(200)
    for delay_t in delay_times:
        for amp in amps:
            res_comb.amps = [amp]

            ssb2d = poly_fwm_ssbspec2d.poly_fwm_ssbspec2d(qubit_a1b1, fwm_comb, res_comb,
                                                fwm_freqs, res_freqs, delay_t,
                                                seq = seq, post_delay = 10e3, bgcor = True,
                                                extra_info = []
                                                )
            ssb2d.measure_keysight()
            
#            ssb2d = poly_fwm_ssbspec2d.poly_fwm_ssbspec2d(qubit_info, fwm_comb, res_comb,
#                                                fwm_freqs, res_freqs, delay_t,
#                                                seq = seq, post_delay = 10e3, bgcor = True,
#                                                extra_info = []
#                                                )
#            ssb2d.measure_keysight()
    bla
    
if 0: # poly ssbspec to find stark shift
    from FWM import poly_fwm_ssbspec
    
#    alice_comb = OCTlib.comb(cavity_infoA, [0], [.1], vary = [1], phases = [0])
#    bob_comb = OCTlib.comb(cavity_infoB, [0], [.1], vary = [0], phases = [0], detunings = [20e6])

    freqs = np.linspace(-.75e6, 1e6, 91)
    delay_times=[5e3]
    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoR.rotate(2, 0)])
    for delay_t in delay_times:
        ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(qubit_a1b1, [fwm_comb],
                                                freqs, delay_t, post_delay = 2e3,
                                                seq = seq, plot_seqs = False,
                                                bgcor = True,
                                                extra_info = [qubit_info, cavity_infoR]
                                                )
        ssb.measure_keysight()
    bla