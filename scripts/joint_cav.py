import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib, OCTlib
#import matplotlib.pyplot as plt
import os
import time
os.chdir(r'C:/qrlab/scripts')

from itertools import product,combinations
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


#qubit_a1b1 = mclient.get_qubit_info('_qubit_a1b1')
#qubit_a2b2 = mclient.get_qubit_info('_qubit_a2b2')
#qubit_a3b3 = mclient.get_qubit_info('_qubit_a3b3')
#qubit_a4b4 = mclient.get_qubit_info('_qubit_a4b4')
#qubit_a1 = mclient.get_qubit_info('_qubit_a1b0')
#qubit_a2 = mclient.get_qubit_info('_qubit_a2b0')
#qubit_b1 = mclient.get_qubit_info('_qubit_a0b1')
#qubit_b2 = mclient.get_qubit_info('_qubit_a0b2')


readout= 'readout_IQ'


cA = cavity_infoA.rotate
cB = cavity_infoB.rotate
cR = cavity_infoR.rotate
#cBqs = cavity_infoB.rotate_quasilective
ge = qubit_info.rotate
ges= qubit_info.rotate_selective
geqs= qubit_info.rotate_quasilective

#ges_a1= qubit_a1.rotate_selective
#ges_a2= qubit_a2.rotate_selective
#ges_b1= qubit_b1.rotate_selective
#ges_b2= qubit_b1.rotate_selective
#geqs_b1= qubit_b1.rotate_quasilective
#geqs_b2= qubit_b2.rotate_quasilective
#ges_a1b1 = qubit_a1b1.rotate_quasilective
#ef = ef_info.rotate
#efs= ef_info.rotate_selective
#efpi = sequencer.Sequence(ef_info.rotate(np.pi, 0))

#geqs2 = qubit2_info.rotate_quasilective

#fwm_info = mclient.get_qubit_info('FWM_info')

#fwm_comb = OCTlib.comb(fwm_info, [.034e6, .034e6], [.3, .3], vary = [0, 1], phases = [0, 0])

# big state pumping for 10us
#fwm_comb = OCTlib.comb(fwm_info, [-275e3], [.6], vary = [1], phases = [np.pi])
#res_comb = OCTlib.comb(cavity_infoR, [-45e3], [.02], vary = [1], phases = [0])

#Areset_comb = OCTlib.comb(mclient.get_qubit_info('cavAreset'), [0], [.2], vary = [1], phases = [0])
#Breset_comb = OCTlib.comb(mclient.get_qubit_info('cavBreset'), [0], [.2], vary = [1], phases = [0])
#Rreset_comb = OCTlib.comb(mclient.get_qubit_info('cavRreset'), [0], [.2], vary = [1], phases = [0])

# 00+11 pumping for 12us
fwm_comb = OCTlib.comb(fwm_info, [-38e3-59.5e3], [.4], vary = [1], phases = [0])
res_comb = OCTlib.comb(cavity_infoR, [-38e3-59.5e3], [.15], vary = [1], phases = [0])


def get_info(a, b):
    try:
        return mclient.get_qubit_info('_qubit_a'+ str(a) + 'b' + str(b))
    except:
        return None
    
def get_rot(a, b, s = False):
    if s == .5:
        return get_info(a, b).rotate_quasilective
    elif s:
        return get_info(a, b).rotate_selective
    else:
        return get_info(a, b).rotate

# tool to autoset and get the correct rotating frame cavity info objects
def get_cav_rf(fwm_comb, res_comb, shift = 0, dif = 0):
    nameA = '_cavityArf'
    nameB = '_cavityBrf'
    df = (fwm_comb.detunings[0] - res_comb.detunings[0] + shift)/2
    mclient.instruments[nameA].set_deltaf(mclient.get_qubit_info('cavityA').deltaf + df + dif/2)
    mclient.instruments[nameB].set_deltaf(mclient.get_qubit_info('cavityB').deltaf + df - dif/2)
    return mclient.get_qubit_info(nameA), mclient.get_qubit_info(nameB)
    
def get_reset(dt = 25e3):
    poly_seq = []
    for comb in [Areset_comb, Rreset_comb]:
        poly_seq += comb.get_poly_seq(dt - comb.sigma*4, 0)
    return sequencer.Combined(poly_seq)
    


if 0: # Cavity disp calibration
    from single_cavity import cavdisp

#for i in range(5):
#    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi, 0)])
#    dig.set_trigger_period(2000)
    disp = cavdisp.CavDisp(qubit_info, cavity_infoA, 3, 41, 0, seq=None,
                           delay=.1e3, bgcor=True, update=False, generate=True,
                           plot_seqs = False, readout=readout
#                           Qswitch_infoA=Qswitch_infoB, Qswitch_infoB=Qswitch_infoB,
#                           extra_info=[Qswitch_infoA, Qswitch_infoB,],
                          )
    disp.measure_keysight()
    bla


if 0: # Cavity T1
    from single_cavity import cavT1
#    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi, 0)])
#    xs = np.concatenate((np.linspace(0e3, 50e3, 26), np.linspace(60e3, 1250e3, 55)))

    t1 = cavT1.CavT1(qubit_info, cavity_infoB, 2, np.linspace(0, 2500e3, 41),
                     proj_num=0, seq=None, postseq=sequencer.Delay(5e3), bgcor=False, 
                     force_a0 = True,
                     readout=readout
#                     extra_info=[ef_info,]
                     )
    t1.measure_keysight()
#    ys = t1.get_ys()
    bla

if 0: # Cavity T2
    from single_cavity import cavT2
    detune = 10e3
    ct2 = cavT2.CavT2(qubit_info, cavity_infoA, .7, np.linspace(.1e3, 1000e3, 101), detune=detune, seq=None,
                       postseq=None, bgcor=False, double_freq=False, readout=readout)
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


if 0: #SSB cavspec
    from single_cavity import ssbcavspec 
    cspec = ssbcavspec.SSBCavSpec(qubit_info, cavity_infoA, np.linspace(-2e6, 2e6, 91), 
                                  readout='readout_IQ'
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


if 0: # number splitting:
    from single_qubit import ssbspec
#    dig.set_naverages(1000)
#    dig.set_trigger_period(5000)
    
    
    delay_t = 10e3
    post_delay = 3e3
    poly_seq = []
    poly_seq += fwm_comb.get_poly_seq(delay_t - fwm_comb.sigma*4, 0)
    poly_seq += res_comb.get_poly_seq(delay_t - res_comb.sigma*4, 0)
    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Combined(poly_seq),
                          sequencer.Delay(post_delay)
                          ])
        
#    seq = sequencer.Join([sequencer.Trigger(250),cA(1.4, 0), cB(1.4, 0)
#                          ])   
##    seq = sequencer.Join([sequencer.Trigger(250),cA(1.14, 0), ges(2*np.pi, 0), cA(-.56, 0), 
#                          sequencer.Combined(poly_seq), sequencer.Delay(post_delay)
#                          ])

#    seq = sequencer.Join([sequencer.Trigger(250) , cB(np.sqrt(3), 0), cA(np.sqrt(3), 0)
#                            ]) # coherent state prep   
#    seq = sequencer.Join([sequencer.Trigger(250),cA(1.14, 0), ges(2*np.pi, 0), cA(-.56, 0),
#                            ]) # |1> state prep#    
#    seq = sequencer.Join([sequencer.Trigger(250),cB(1.14, 0), geqs(2*np.pi, 0), cB(-.56, 0),
#                          sequencer.Combined(poly_seq), sequencer.Delay(post_delay)]) # |1> state prep
    
#    seq = sequencer.Join([sequencer.Trigger(250),cB(1.14, 0), geqs(2*np.pi, 0), cB(-.56, 0),
#                          cA(1.14, 0), ges_b1(2*np.pi, 0), cA(-.56, 0)]) # |1>|1> state prep
#    seq = sequencer.Join([sequencer.Trigger(250),cA(1.55, 0), 
#                          sequencer.Combined([ges(2*np.pi, 0), ges_a1(2*np.pi, 0)]),
#                          cA(-.44, 0), 
#                          ]) # |2> state prep
#    seq = sequencer.Join([sequencer.Trigger(250),cA(2.1, 0), 
#                          sequencer.Combined([ges(2*np.pi, 0), ges_a1(2*np.pi, 0), ges_a2(2*np.pi, 0)]),
#                          cA(-.32, 0), cB(np.sqrt(3), 0)
#                          ]) # |3> state prep     
    
#    seq = sequencer.Join([sequencer.Trigger(250),cB(2.1, 0), 
#                          sequencer.Combined([geqs(2*np.pi, 0), 
#                                              geqs_b1(2*np.pi, 0), 
#                                              geqs_b2(2*np.pi, 0)]),
#                          cB(-.32, 0),
#                          ]) # |3> state prep     
#    seq = sequencer.Join([sequencer.Trigger(250),
#                          cB(1.14, 0), geqs(2*np.pi, 0), cB(-.56, 0),
#                          cA(1.14, 0), ges_b1(2*np.pi, 0), cA(-.56, 0)
#                          ]) # |11> prep
#    seq = sequencer.Join([sequencer.Trigger(250),cB(1.14, 0), geqs(2*np.pi, 0), cB(-.56, 0),
#                          cA(1.14, 0), ges_b1(2*np.pi, 0), cA(-.56, 0),
#                          cA(np.sqrt(0), 0), cB(np.sqrt(2), 0)]) # Displacment after 11 state state prep   
#        for freqs in [
##                      np.linspace(-27e6, -17e6, 200),
#                      np.linspace(-8.5e6, -6.5e6, 51),
#                      np.linspace(-1e6, 1e6, 51),
#                     ]:
    spec = ssbspec.SSBSpec(qubit_info, #np.linspace(-30e6, 10e6, 21),
#                           np.linspace(-10e6, 0.5e6, 151),
                           np.concatenate((
                                          np.linspace(-17e6, -13e6, 100),
#                                          np.linspace(-28e6, -24e6, 44),
#                                          np.linspace(-22e6, -20e6, 21),
#                                          np.linspace(-15e6, -13e6, 21),
#                                          np.linspace(-8.5e6, -6.5e6, 21),
#                                          np.linspace(-1e6, 1e6, 21),
                                           )),
#                           extra_info= [fwm_comb.info, res_comb.info],
                           extra_info= [cavity_infoA, cavity_infoB, cavity_infoR, fwm_info],
                           seq = seq,  plot_seqs=False,
                           bgcor = False, readout=readout,
                           reset_seq = None)
    spec.measure_keysight()
    bla


if 0: # Measure readout contrast
    from single_qubit import rabi
    tr = rabi.Rabi(cavity_infoA, 
                   np.linspace(-1.1/np.pi, 1.1/np.pi, 51), selective=False,
#                   np.linspace(-.12, .12, 51), selective=.5,
#                  np.linspace(-0.01, 0.01, 51), selective=True,
#                   np.linspace(0.8, .9, 51), selective=False,
#                   np.linspace(0.25, 0.4, 51), selective=False,
                   plot_seqs=False, generate=True, repeat_pulse=1, update=False, 
                   seq=None)
    tr.measure()
    bla


if 0: # Calibrate pi pulse
    from single_qubit import rabi
    seq = sequencer.Join([sequencer.Trigger(250),cB(1.14, 0), geqs(2*np.pi, 0), cB(-.56, 0),
                          cA(1.14, 0), ges_b1(2*np.pi, 0), cA(-.56, 0)]) # |1>|1> state prep
    tr = rabi.Rabi(qubit_a1b1, 
#                   np.linspace(-.9, .9, 51), selective=False,
                   np.linspace(-.03, .03, 51), selective=True,
                   plot_seqs=False, generate=True, repeat_pulse=1, update=False, 
                   seq=seq, readout='readout_IQ', extra_info=[cavity_infoA, cavity_infoB, 
                                                              qubit_b1, qubit_info])
    tr.measure()
    bla

if 0: # RO cavity shift 
    from single_cavity import rocavspectroscopy_keysight
    seq = sequencer.Join([sequencer.Trigger(250),cA(1, 0)])

    rofreq = 7317.63e6#+50e6
#    rofreq = 7320e6
    freq_range = 2e6
    freqs = np.linspace(rofreq-freq_range, rofreq+freq_range, 51)
    powers = np.linspace(5,10,1) 

    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(cavity_infoA, powers, freqs,
                                             qubit_pulse=False, seq=seq,
                                             plot_seqs = True)
    ro.measure()
    
    '''amp = ro.ampdata[:]
    f= open('ampdata_2d_HP.txt', 'w')
    f.write(str(amp))
    f.close()'''
    
    bla
    
if 0: #GE Sideband modulated number splitting:
    from single_qubit import ssbspec
    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate(1.5, 0)])
#    postseq = qubit_info.rotate(np.pi/2,0)
#    postseq = sequencer.Sequence(qubit_info.rotate(np.pi/2, 0))
    spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
#                                                    np.linspace(-22e6, -18e6, 71),  
#                                                    np.linspace(-12e6, -8e6, 71),
                                                    np.linspace(-10e6, 1e6, 91),
                                                    )),
                           extra_info= [cavity_infoA, cavity_infoB],
                           seq =seq,  postseq = None, plot_seqs=False, readout=readout)
    spec.measure_keysight()
    bla


if 0: #EF Sideband modulated number splitting:
    from single_qubit import ssbspec
    seq = sequencer.Join([sequencer.Trigger(250), qubit_info.rotate(np.pi,0), cavity_infoA.rotate(1, 0)])
#    postseq = qubit_info.rotate(np.pi/2,0)
    dig.set_trigger_period(3000)
    dig.set_naverages(5000)

    postseq = sequencer.Sequence(qubit_info.rotate(np.pi/2, 0))
    spec = ssbspec.SSBSpec(ef_info, np.concatenate((
#                                                    np.linspace(-22e6, -18e6, 71),  
#                                                    np.linspace(-12e6, -8e6, 71),
                                                    np.linspace(-30e6, 3e6, 201),
                                                    )),
                           extra_info= [qubit_info, cavity_infoA],
                           seq =seq,  postseq = postseq, plot_seqs=False, readout=readout)
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
    seq = sequencer.Join([sequencer.Trigger(250), cA(1.2, 0), cB(1.2, 0)])
    rr = RamseyRevival.RamseyRevival(qubit_info, ef_info, np.linspace(0, 400, 91), 
                                     seq = seq, extra_info = [cavity_infoA, cavity_infoB], 
                                     readout=readout)
    rr.measure_keysight()

if 0: # Wigner function by displaced parity for cavity B
    from scripts.single_cavity import WignerbyParity
#    seq = sequencer.Join([prepareB, geph(pi/2,0), sequencer.Delay(950), cB(1.65, -pi*0.175),
#                          geqs(pi,0), cB(-1.65, -pi*0.02)])
    seq = sequencer.Join([sequencer.Trigger(250), cB(1, 0)])
    disp = 1.5
#    seq = sequencer.Join([sequencer.Trigger(500), 
#                      cB(disp, 0), ge(np.pi/2, 0), 
#                      sequencer.Delay(65), 
#                      cB(disp, 0),
#                      geqs(np.pi, 0),
#                      cB(-disp, 0)
#                      ])

    
    Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoB,
                                         xs = np.linspace(-1.8,1.8,17), ys = np.linspace(-1.3,1.3,13),
                                         t_ge=53, t_gf=0,
                                         seq=seq, delay=5, bgcor=True, zmax=100, zmin=-100, 
                                         extra_info = None, readout=readout)
    Wfun.measure_keysight()

if 0: # Wigner function by displaced parity for cavity A
    from scripts.single_cavity import WignerbyParity
#    seq = sequencer.Join([prepareB, geph(pi/2,0), sequencer.Delay(950), cB(1.65, -pi*0.175),
#                          geqs(pi,0), cB(-1.65, -pi*0.02)])    
#    seq = sequencer.Join([sequencer.Trigger(250), cA(1,0)])
    disp = 1.5
    seq = sequencer.Join([sequencer.Trigger(250), cA(disp, 0), 
                      ge(np.pi/2, 0), sequencer.Delay(233), cA(disp,0), 
                      geqs(np.pi, 0), 
                      cA(-disp,0)])
    Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoA,
                                         xs = np.linspace(-1.8,1.8,17), ys = np.linspace(-1.3,1.3,11),
                                         t_ge=230, t_gf=0,
                                         seq=seq, delay=5, bgcor=True, 
#                                         zmax=100, zmin=-100, 
                                         zmax=None, zmin=None, 
                                         extra_info = None,readout=readout)
    Wfun.measure_keysight()


if 0: # Joint Wigner Parity
    from scripts.single_cavity import JointWigner

#    seq = sequencer.Join([sequencer.Trigger(250),cA(1.14, 0), ges(2*np.pi, 0), cA(-.56, 0),
#                          sequencer.Combined(poly_seq), sequencer.Delay(post_delay)])
    
#    disp = 1 # cat in alice
#    seq = sequencer.Join([sequencer.Trigger(250), cB(disp, 0), 
#                      ge(np.pi/2, 0), sequencer.Delay(70), cB(disp,0), 
#                      geqs(np.pi, 0), 
#                      cB(-disp,0)])
#    seq = sequencer.Join([sequencer.Trigger(250),cB(1.14, 0), geqs(2*np.pi, 0), cB(-.56, 0),
#                          cA(1.14, 0), get_rot(0, 1, s=True)(2*np.pi, 0), cA(-.56, 0)]) # |1>|1> state prep
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Combined([cA(1,0), cB(1, 0)])])
    for delay_t in [10e3]:
        post_delay = 5e3
        poly_seq = []
        poly_seq += fwm_comb.get_poly_seq(delay_t - fwm_comb.sigma*4, 0)
        poly_seq += res_comb.get_poly_seq(delay_t - res_comb.sigma*4, 0)
#        seq = sequencer.Join([sequencer.Trigger(250), sequencer.Combined(poly_seq),
#                              sequencer.Delay(post_delay)
#                              ]) # delta = 0
    
        seq = sequencer.Join([sequencer.Trigger(250), cA(1.14, 0), ges(2*np.pi, 0), cA(-.56, 0), 
                              sequencer.Combined(poly_seq), sequencer.Delay(post_delay)
                              ]) # delta = +-1
    
    
    
    
        infoA, infoB = get_cav_rf(fwm_comb, res_comb, shift = 0)
#    infoA, infoB = cavity_infoA, cavity_infoB
    
    
        ax1 = 0 
        ax2 = 2
        Wfun = JointWigner.JointWigner(qubit_info, ef_info, infoA, infoB,  
                                         np.linspace(-1.5,1.5,15), np.linspace(-1.5,1.5, 15),
    #                                     np.linspace(-1.5,1.5,17), np.linspace(-1.5,1.5, 17),
                                         ax1, ax2,
                                         t_ge=250, t_gf=0,
    #                                     disp_array = disp_array,
                                         seq=seq, delay=5, bgcor=True, 
    #                                     zmax=1000, zmin=0, 
                                         zmax=None, zmin=None, plot_seqs=False,
                                         extra_info = [fwm_info, cavity_infoR, get_info(0, 1),
                                                       cavity_infoA, cavity_infoB],
                                         readout=readout)
        Wfun.measure_keysight()
    bla
    
  
if 0: # Joint Wigner shell
    from scripts.single_cavity import JointWigner  
    dig.set_trigger_period(7500)
    dig.set_naverages(1000)
    
    delay_t = 10e3
    post_delay = 5e3
    poly_seq = []
    poly_seq += fwm_comb.get_poly_seq(delay_t - fwm_comb.sigma*4, 0)
    poly_seq += res_comb.get_poly_seq(delay_t - res_comb.sigma*4, 0)
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Combined(poly_seq),
#                          sequencer.Delay(post_delay)
#                          ]) #delta=0

    seq = sequencer.Join([sequencer.Trigger(250), cA(1.14, 0), ges(2*np.pi, 0), cA(-.56, 0), 
                          sequencer.Combined(poly_seq), sequencer.Delay(post_delay)
                          ]) # delta = +-1


#    seq = sequencer.Join([sequencer.Trigger(250),cB(1.14, 0), geqs(2*np.pi, 0), cB(-.56, 0),
#                          cA(1.14, 0), ges_b1(2*np.pi, 0), cA(-.56, 0)]) # |1>|1> state prep
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Combined([cA(-1,0), cB(1, 0)])])
    
    r = .35
    angles = np.linspace(0, 2*np.pi, 17)
    angles_a, angles_b = np.meshgrid(angles, angles)
    disp_array = np.zeros((len(angles) * len(angles), 4))
    angles_a = angles_a.flatten()
    angles_b = angles_b.flatten()

    disp_array = np.transpose(np.array([r*np.cos(angles_a), r*np.sin(angles_a), 
                           r*np.cos(angles_b), r*np.sin(angles_b)]))

    Wfun = JointWigner.JointWigner(qubit_info, ef_info, cavity_infoA, cavity_infoB, 
                                   angles, angles, None, None,
                                   t_ge=250, t_gf=0,
                                   disp_array = disp_array,
                                   seq=seq, delay=5, bgcor=True, 
                                   zmax=None, zmin=None, 
                                   plot_type = 'shell',
                                   extra_info = [qubit_b1, fwm_info, cavity_infoR],readout=readout)
    Wfun.measure_keysight()
    
if 0: # Joint Wigner all slices
    from scripts.single_cavity import JointWigner  
    
    delay_t = 10e3
    post_delay = 10e3

    poly_seq = []
    poly_seq += fwm_comb.get_poly_seq(delay_t - fwm_comb.sigma*4, 0)
    poly_seq += res_comb.get_poly_seq(delay_t - res_comb.sigma*4, 0)
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Combined(poly_seq),
#                          sequencer.Delay(post_delay)
#                          ])
    seq = sequencer.Join([sequencer.Trigger(250),cB(1.14, 0), geqs(2*np.pi, 0), cB(-.56, 0), 
                          sequencer.Combined(poly_seq), sequencer.Delay(post_delay)
                          ])
                               
#    seq = sequencer.Join([sequencer.Trigger(250),cB(1.14, 0), geqs(2*np.pi, 0), cB(-.56, 0),
#                          cA(1.14, 0), ges_b1(2*np.pi, 0), cA(-.56, 0)]) # |1>|1> state prep
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Combined([cA(-1,0), cB(1, 0)])])
    


    for ax1 in range(4):
        for ax2 in range(ax1+1,4):
            Wfun = JointWigner.JointWigner(qubit_info, ef_info, cavity_infoA, cavity_infoB, 
                                     np.linspace(-1.5,1.5,17), np.linspace(-1.5,1.5, 17),
#                                     np.linspace(-1.5,1.5,17), np.linspace(-1.5,1.5, 17),
                                     ax1, ax2,
                                     t_ge=250, t_gf=0,
#                                     disp_array = disp_array,
                                     seq=seq, delay=5, bgcor=True, 
#                                     zmax=1000, zmin=0, 
                                     zmax=None, zmin=None, plot_seqs=False,
                                     extra_info = [qubit_b1, fwm_info, cavity_infoR],readout=readout)
            Wfun.measure_keysight()

        
if 0: # Joint Parity Test
    from scripts.single_cavity import JointTest
    
    delay_t = 15e3
    post_delay = 10e3
    poly_seq = []
    poly_seq += fwm_comb.get_poly_seq(delay_t - fwm_comb.sigma*4, 0)
    poly_seq += res_comb.get_poly_seq(delay_t - res_comb.sigma*4, 0)
    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Combined(poly_seq),
                          sequencer.Delay(post_delay)
                          ])
#    seq = sequencer.Join([sequencer.Trigger(250),cB(1.14, 0), geqs(2*np.pi, 0), cB(-.56, 0),
#                          cA(1.14, 0), ges_b1(2*np.pi, 0), cA(-.56, 0)]) # |1>|1> state prep
    
    Wtest = JointTest.JointTest(qubit_info, ef_info, np.arange(220, 275, 2),
                                 seq=seq, delay=10, bgcor=True, 
                                 zmax=None, zmin=None, readout=readout,
                                 extra_info = [qubit_b1, cavity_infoA, cavity_infoB,
                                               fwm_info, cavity_infoR],)
    Wtest.measure_keysight()



if 0: # Cavity cooling test
    from scripts.FWM import FWM_cavity_cooling
    freqs = np.linspace(-200.5e6, -199.5e6, 41)
#    freqs = np.array([200e6]*10)
    
    cc = FWM_cavity_cooling.FWM_cavity_cooling(qubit_info, cavity_infoA, cavity_infoR, freqs, .9, 
                 .9,1000e3)
    cc.measure_keysight()
    
    
    
    
if 0: # 2d poly ssbspec
    from FWM import poly_fwm_ssbspec2d
    dig.set_trigger_period(2500)
    dig.set_naverages(1000)
    fwm_freqs =  np.linspace(-100e3, 100e3, 19)
    res_freqs =  np.linspace(-100e3, 100e3, 19)
#    alice_comb = OCTlib.comb(cavity_infoA, [10e6], [.9], vary = [1], phases = [0])
#    bob_comb = OCTlib.comb(cavity_infoB, [-10e6], [.9], vary = [-1], phases = [0])
#    alice_freqs =  np.linspace(-1e6, 1e6, 11)
#    bob_freqs =  np.linspace(-1e6, 1e6, 11)
#    delay_times=[10e3]
#    amps = [.005, .01, .15]
#    seq = sequencer.Join([sequencer.Trigger(250),cA(1.14, 0)])
#    seq = sequencer.Join([sequencer.Trigger(250),cA(1.14, 0), ges(2*np.pi, 0), cA(-.56, 0),
#                            ]) # |1> state prep
    for info in [get_info(1,1), get_info(2,2)]:
#    for info in [qubit_info]:
#        for amp in amps:
#            res_comb.amps = [amp]
#            fwm_comb.amps = [.5]

#            ssb2d = poly_fwm_ssbspec2d.poly_fwm_ssbspec2d(qubit_info, alice_comb, bob_comb,
#                                                alice_freqs, bob_freqs, delay_t,
#                                                seq = seq, post_delay = 5e3, bgcor = False,
#                                                extra_info = [], plot_seqs=False, readout=readout
#                                                )
#            ssb2d.measure_keysight()
            
        ssb2d = poly_fwm_ssbspec2d.poly_fwm_ssbspec2d(info, fwm_comb, res_comb,
                                            fwm_freqs, res_freqs, 50e3,
                                            seq = None, post_delay = 5e3, bgcor = True,
                                            extra_info = [], readout=readout
                                            )
        ssb2d.measure_keysight()
    
    
if 1: # poly ssbspec to find transition
    from FWM import poly_fwm_ssbspec
    dig.set_trigger_period(2500)
    dig.set_naverages(600)
#    alice_comb = OCTlib.comb(cavity_infoA, [0], [.1], vary = [1], phases = [0])
#    bob_comb = OCTlib.comb(cavity_infoB, [0], [.1], vary = [0], phases = [0], detunings = [20e6])

#    freqs =  np.linspace(-5e6, 5e6, 51)
    freqs =  np.linspace(-200e3, 200e3, 101)
#    delay_times=[10e3]
        
#    seq = sequencer.Join([sequencer.Trigger(250),cA(1.14, 0), ges(2*np.pi, 0), cA(-.56, 0),
#                            ]) # |1> state prep   
#    seq = sequencer.Join([sequencer.Trigger(250),cA(1.14, 0)])
#    seq = sequencer.Join([sequencer.Trigger(250),cB(1.14, 0), geqs(2*np.pi, 0), cB(-.56, 0),
#                          cA(1.14, 0), ges_b1(2*np.pi, 0), cA(-.56, 0)]) # |1>|1> state prep    
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoR.rotate(.7, 0)])
#    for delay_t in delay_times:
#    for amp in [.02]:
#        res_comb.amps = [amp]
    ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(get_info(2,2), 
                                            [fwm_comb, res_comb],
                                            freqs, 15e3, post_delay = 3e3,
                                            seq = None, plot_seqs = False,
                                            bgcor   = True,
                                            extra_info = [cavity_infoR, cavity_infoA, cavity_infoB,
                                                          qubit_info],
                                            readout=readout
                                            )
    ssb.measure_keysight()
    
    
    
    
    
if 0: # t2 under drive for stark shift
    from AQEC import T2_AQEC
    period = dig.get_trigger_period()
    naverages = dig.get_naverages()
    dig.set_trigger_period(3000)   
    dig.set_naverages(400)
    
    for amp in [.5]:
        fwm_comb.amps = [amp]
        st2 = T2_AQEC.T2_AQEC(qubit_info, np.linspace(.5e3, 13e3, 131), [fwm_comb], detune=5e6, 
                                         double_freq=True, generate=True, seq=None,
                                         plot_seqs=False, readout=readout)
        st2.measure()
        
        
if 0: # time domain
    from FWM import poly_time_domain
    
    dig.set_trigger_period(7500)
    dig.set_naverages(3000)
    
#    comb_list = [Areset_comb, Rreset_comb]
    comb_list = [fwm_comb, res_comb]
#    comb_list = [fwm_comb]
#    comb_list = []
#    qubit_list = [qubit_info, qubit_a1b1, qubit_a2b2, qubit_a3b3]
#    qubit_list = [qubit_info, 
##                  mclient.get_qubit_info('_qubit_a1b0'),
#                  mclient.get_qubit_info('_qubit_a1b1'),
##                  mclient.get_qubit_info('_qubit_a2b1'),
#                  mclient.get_qubit_info('_qubit_a2b2'),
##                  mclient.get_qubit_info('_qubit_a3b2')
#                    ]
#    seq = sequencer.Join([sequencer.Trigger(250),cA(1.14, 0)])
#    seq = sequencer.Join([sequencer.Trigger(250), cA(1.14, 0), ges(2*np.pi, 0), cA(-.56, 0),
#                            ]) # |1> state prep
    qubit_list = [qubit_info, get_info(1,1), get_info(2,2), get_info(3, 3), get_info(4, 4),
                  get_info(1,0), 
#                    get_info(2,1), get_info(3,2),
                  get_info(0,1), 
#                    get_info(1,2), get_info(2,3)
                  ]
#    delay_t = 10e3
#    poly_seq = []
#    poly_seq += fwm_comb.get_poly_seq(delay_t - fwm_comb.sigma*4, 0)
#    poly_seq += res_comb.get_poly_seq(delay_t - res_comb.sigma*4, 0)
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Combined(poly_seq)])
#    seq = [sequencer.Trigger(200), cavity_infoR.rotate(2, 0)]
#    seq += [sequencer.Sequence(fwm_comb_static.get_poly_seq(5e3 - fwm_comb_static.sigma*4, 0))]
#    seq = sequencer.Join([sequencer.Trigger(250),cB(1.14, 0), geqs(2*np.pi, 0), cB(-.56, 0),
#                          cA(1.14, 0), ges_b1(2*np.pi, 0), cA(-.56, 0)]) # |1>|1> state prep    
#    seq = sequencer.Join([sequencer.Trigger(250),cB(1.55, 0), 
#                          sequencer.Combined([geqs(2*np.pi, 0), geqs_b1(2*np.pi, 0)]),
#                          cB(-.44, 0), 
#                          cA(1.2, 0)
#                          ]) # |2> state preps
    delays = np.concatenate([
                             np.linspace(.1e3, 20e3, 31), 
#                             np.linspace(200e3, 500e3, 11)
                            ])
#    seq = sequencer.Join([sequencer.Trigger(200), cA(.8, 0), cB(.8, 0)])
#    seq = sequencer.Join([sequencer.Trigger(200), cR(2, 0)])
    
#    MXG = mclient.instruments['MXGdrive']
#    freq_range = .3e6
#    freqs = np.linspace(-freq_range, freq_range, 1)
#    taus = []
#    dtaus = []
#    for FWM_freq in freqs:
#        MXG.set_frequency(FWM_freq)
#        time.sleep(.1)
#        fwm_comb.detunings = [FWM_freq]
#        fwm_comb.amps = [0]
    td = poly_time_domain.poly_time_domain(comb_list, qubit_list, delays,
                                       plot_seqs=False, bgcor=True, seq=None, 
                                       extra_info = [qubit_info, cavity_infoR, 
                                                     cavity_infoA, cavity_infoB,
                                                     fwm_info],
                                       readout=readout, post_delay=5e3,
                                       reset_seq = None)
    params = td.measure()
#        taus += [params['tau'].value]
#        dtaus += [params['tau'].stderr]
#    plt.figure()
#    plt.errorbar(freqs, taus, yerr=dtaus)
    
    
if 0: # SSB after fwm
    from single_qubit import ssbspec
    dig.set_trigger_period(500)
    dig.set_naverages(500)
    times = [200e3]#np.arange(20e3, 40e3, 1e3)
    infos = [fwm_comb.info]
    for dt in times:
        seq = [sequencer.Trigger(200), cavity_infoR.rotate(2, 0)]
        if dt>0:
            poly_seq = sequencer.Sequence(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0))
            seq += [poly_seq]
        seq += [sequencer.Delay(10e3)]
            
        spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
#                                            np.linspace(-17e6, -15e6, 51),
                                              np.linspace(-8.5e6, -6.5e6, 51),
                                              np.linspace(-1e6, 1e6, 51),
                                            )), 
                                seq=sequencer.Join(seq), 
                                extra_info = infos + [cavity_infoR], readout=readout,
                                bgcor=False
                                )
        spec.measure_keysight()
    bla    
    
    
if 0: #ab time domain 
    dig.set_naverages(8000)    
    qubit_a1b1 = mclient.get_qubit_info('qubit_a1b1')
#    qubit_a2b2 = mclient.get_qubit_info('qubit_a2b2')
#    qubit_a2b1 = mclient.get_qubit_info('qubit_a2b1')
#    qubit_a3b3 = mclient.get_qubit_info('qubit_a3b3')
    fwm_info = mclient.get_qubit_info('FWM_info')
#    qubit_b1 = mclient.get_qubit_info('qubit_b1')
#    qubit_b2 = mclient.get_qubit_info('qubit_b2')    
#    qubit_a1 = mclient.get_qubit_info('qubit_a1')
#    qubit_a2 = mclient.get_qubit_info('qubit_a2')    
    
#    MXG = mclient.instruments['MXG']
        
    from FWM import ab_time_domain

#    FWM_settings = {6: 2804.98e6}#{4.5:2805.05e6, 10.7:2804.62e6, 2:2805.13e6, 9.5: 2804.69e6}
    drive_amps = np.linspace(0.008, 0.016, 5)   # 0.0001 to mimic zero for pump without drive, probably easier to just turn SCres off
    delays = np.linspace(0e3, 40e3, 21)
    
    for drive_amp in drive_amps:
#        for FWM_freq in np.linspace(2804.36e6, 2804.42e6, 7):
#        for FWM_power in FWM_settings.keys():
#            MXG.set_power(FWM_power)
#            MXG.set_frequency(FWM_settings[FWM_power])
#            MXG.set_frequency(FWM_freq)
#            time.sleep(.1)
        seq = sequencer.Sequence()
        seq.append(sequencer.Trigger(250))
        seq.append(cR(2,0))
#            seq.append(sequencer.Combined([
#                        cA(1.2,0), cB(0.7,0)]))
        ab_t = ab_time_domain.ab_time_domain(fwm_info, cavity_infoR,
                                           [qubit_info, qubit_a1b1],
#                                               [qubit_info, qubit_a1, qubit_a1b1, qubit_a2b1],
                                           delays, drive_amp, '13m1', plot_seqs=False, 
                                           bgcor=True, seq=None,)# extra_info = [cavity_infoA, cavity_infoB] )
        ab_t.measure_keysight()
    bla
    
    
if 0: # check ro-storage crosstalk
    from single_cavity import rocavspectroscopy_keysight
    from single_cavity import cavdisp
    from single_qubit import rabi
    from single_qubit import T2measurement

    rofreq = 7318e6+50e6
#    rofreq = 7320e6
    freq_range = 1e6
    freqs = np.linspace(rofreq-freq_range, rofreq+freq_range, 51)

    readout_IQ = mclient.instruments['readout_IQ']
    SC = mclient.instruments['SCqubit']
    for i in [.005, .1]:    
        readout_IQ.set_pi_amp(i)                                    
#        ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, [], freqs,
#                                                 qubit_pulse=False, seq=None, readout = readout,
#                                                 plot_seqs = True)
#        ro.measure()
        dig.do_set_trigger_period(500)
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0e3, 15e3, 91), detune=1e6, 
                     double_freq=False, generate=True, seq=None,
                     plot_seqs=False, readout=readout)
        t2.measure()
        SC.do_set_frequency(SC.do_get_frequency() + t2.fit_params['freq']*1e9 - 1e6)
        
        
        tr = rabi.Rabi(qubit_info, 
                       np.linspace(-0.015, 0.015, 51), selective=True,
                       plot_seqs=False, generate=True, repeat_pulse=1, update=True, 
                       seq=None, readout=readout)
        tr.measure()
            
        dig.do_set_trigger_period(2000)
        disp = cavdisp.CavDisp(qubit_info, cavity_infoA, 2.8, 41, 0, seq=None,
                               delay=0, bgcor=False, update=False, generate=True,
                               plot_seqs = False, readout=readout
                              )
        disp.measure_keysight()    

        disp = cavdisp.CavDisp(qubit_info, cavity_infoB, 2.8, 41, 0, seq=None,
                               delay=0, bgcor=False, update=False, generate=True,
                               plot_seqs = False, readout=readout
                              )
        disp.measure_keysight()


    
    bla
    
if 0: # RO with FWM
    from single_cavity import ROCavSpec_IQ
    freq_range = .1e6
    df = np.linspace(-freq_range, freq_range, 101)
    amps = np.linspace(.005,.3, 1)
#    readout_IQ = mclient.instruments['readout_IQ']

    for i in np.linspace(1e6, 1e6, 11):    
#        readout_IQ.set_pi_amp(i)
        fwm_comb.detunings = [i]

        ro = ROCavSpec_IQ.ROCavSpec_IQ(qubit_info, amps, df,
                                       qubit_pulse=False, seq=None,
                                       readout = 'readout_IQ',
                                       comb_list = [fwm_comb], extra_info = [fwm_comb.info],
                                       plot_seqs=False)
        ro.measure()
        
        '''amp = ro.ampdata[:]
        f= open('ampdata_2d_HP.txt', 'w')
        f.write(str(amp))
        f.close()'''
        
    bla
    
    
    
if 0: # Joint wigner t2
    from FWM import CavT2_Joint
    
#    delay_t = 10e3
#    post_delay = 10e3
#    poly_seq = []
#    poly_seq += fwm_comb.get_poly_seq(delay_t - fwm_comb.sigma*4, 0)
#    poly_seq += res_comb.get_poly_seq(delay_t - res_comb.sigma*4, 0)
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Combined(poly_seq)])
    
    seq = sequencer.Join([sequencer.Trigger(250), cA(1.14, 0), ges(2*np.pi, 0), 
                          cA(-.56, 0)]) # delta = +-1
    
    
#    disp = [.7, .0, -.7, .0] # delta=0
    disp = [.75, .0, 1.125, .0] # delta=1
#    disp = [0, 0, 0, 0]                 
    ax1=0
    ax2=2
    
    delays = np.linspace(10e3, 20e3, 51)
    infoA, infoB = get_cav_rf(fwm_comb, res_comb, shift = 0)
#    infoA, infoB = cavity_infoA, cavity_infoB

    t2 = CavT2_Joint.CavT2_Joint(qubit_info, infoA, infoB, disp, delays, 
                                 ax1, ax2, comb_list = [fwm_comb, res_comb], detune = 0,
                                 t_ge=250, bgcor=True, seq = seq, post_delay = 5e3, 
                                 extra_info = [fwm_comb.info, res_comb.info],
                                 readout=readout, plot_seqs=False)
    t2.measure()
    
if 0: # delay test (needs work and thought)
    pass
    