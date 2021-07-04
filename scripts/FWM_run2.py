import mclient
import importlib
importlib.reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
#matplotlib.rcParams['backend'] = 'Qt4Agg'
#matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
import os
import time
import math

#os.chdir(r'C:/qrlab/scripts')
dig = mclient.instruments['dig']

qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')

#fwm_info = mclient.get_qubit_info('FWM_info') 
#fwm_e2g4_info = mclient.get_qubit_info('FWM_e2g4_info') 

#cavity_infoA = mclient.get_qubit_info('cavityA')
cavity_infoB = mclient.get_qubit_info('cavityB')
#cavity_infoR = mclient.get_qubit_info('cavityR')

#cA = cavity_infoA.rotate
cB = cavity_infoB.rotate
ge = qubit_info.rotate
ges= qubit_info.rotate_selective


if 0: #cavity ssb
    from scripts.single_cavity import ssbcavspec
    ssb = ssbcavspec.SSBCavSpec(qubit_info, cavity_infoB, np.linspace(-2e6, 2e6, 51))
#    ssb = ssbcavspec.SSBCavSpec(qubit_info, cavity_infoA, np.linspace(-2e6, 2e6, 51), plot_seqs = False)
    ssb.measure_keysight()
    bla

if 0: # Cavity disp calibration
    from scripts.single_cavity import cavdisp
    seq = sequencer.Trigger(250)
    disp = cavdisp.CavDisp(qubit_info, cavity_infoB, 2.5, 51, 0, seq=None,
                           delay=0, bgcor=True, update=False, generate=True, plot_seqs=False )
    disp.measure_keysight()
    bla

if 0: # Cavity T1
    from scripts.single_cavity import cavT1
    t1 = cavT1.CavT1(qubit_info, cavity_infoB, 1.5,
                     np.linspace(0e3, 1600e3, 51),
                     proj_num=0, seq=None, postseq=None, bgcor=False, force_a0 =True )
    t1.measure_keysight()
    bla

if 0:# Cavity T2
    from scripts.single_cavity import cavT2    
    detune = 20e3
    ct2b = cavT2.CavT2(qubit_info, cavity_infoB, .7, np.linspace(4e3, 600e3, 101), detune=detune, seq=None,
                       postseq=None, bgcor=False, extra_info=[qubit_info,])
    ct2b.measure_keysight()
    bla
    
if 0: # Number splitting
    from .single_qubit import ssbspec
    seq = sequencer.Sequence()
    seq.append(sequencer.Trigger(500))
    seq.append(cB(1.2,0))
#            seq.append(sequencer.Combined([
#                        cA(1.2,0), cB(0.7,0)]))
    spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
                                        np.linspace(-7e6, 1e6, 51),
                                       )), 
                           seq=seq, plot_seqs=False, extra_info = [cavity_infoB])#
    spec.measure_keysight()
    bla                

if 0: #g1-f0 cavity cooling
    fwm_gen = mclient.instruments['SCfwm']
#    target = 4.96386e9 * 2 - 221.2e6 - 6.92618e9   this is original set values (juliang)
#    target = 4.96356e9 * 2 - 221.2e6 + 6.92618e9    4.96356e9 is the frequency at the center
#    target = 6.926e9
    w_q=5024110000
    k_ef=214e6
#    k_ef=0
    w_b=6082200000
    target = 2*w_q-k_ef-w_b
#    target = 4.96320e9 * 2 - 221.2e6 - 6.92605e9
#    freqs = np.linspace(target-3e6, target+3e6, 50)    this is original set values (juliang)
#    freqs = np.linspace(target-5.0e6, target+5e6, 51)
    freqs = np.linspace(target-20.0e6, target+5.0e6, 51)
    powers = [-20, -15, -10]#, 12.5, 15]
#    powers = [10, 12.5, 15]
#    powers = [12.5]   
    shift_freq = np.zeros(len(powers))
    from .FWM import FWM_g1f0
    for i, power in enumerate(powers):
        g1f0 = FWM_g1f0.FWM_g1f0(qubit_info, cavity_infoB, fwm_gen, 400e3, 1.5,
                     freqs, power, '4m1', '3m1') 
        g1f0.measure()
        shift_freq[i] = g1f0.xs[np.argmax(g1f0.ampdata[:])]  

# delay time was 5e3

if 0: #Fock 0 to 1 dissipation
    from .single_qubit import ssbspec
    dt = 500e3
    drive_amp = 2e-3  #target 25kHz rabi rate  #sigma 400 has pi amp = 9.1e-3 or Rabi rate of 500 kHz
    freq = 7339.10e6 + 6081.13e6 - 4788.48e6 + 71e6
#    MXG = instruments['MXG']
    MXG.set_frequency(freq)
    seq = sequencer.Sequence()
    seq.append(sequencer.Trigger(500))
    seq.append(cB(1.8, 0))
    seq.append(sequencer.Combined([
            sequencer.Constant(int(dt), 1, chan='4m1'),
            sequencer.Constant(int(dt), drive_amp, chan=qubit_info.sideband_channels[0]),
        ]))
    seq.append(sequencer.Delay(1e3))
    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-5e6, 2.5e6, 51),
                           seq=seq, plot_seqs=False, extra_info=[cavity_infoB])
    spec.measure_keysight()
    bla   
    
    
if 1: # Fock 0 to 1 time domain
#    dig.set_naverages(8000)    
    fwm_info = mclient.get_qubit_info('FWM_info')
    qubit_b0 = mclient.get_qubit_info('qubit_b0')
    qubit_b1 = mclient.get_qubit_info('qubit_b1')
    qubit_b2 = mclient.get_qubit_info('qubit_b2')    
    
    MXG = mclient.instruments['MXG']
        
    from .FWM import ab_time_domain

    drive_amps = np.linspace(1e-3, 0.003, 1)
    delays = np.linspace(0e3, 30e3, 21)
    
    for drive_amp in drive_amps:
        ab_t = ab_time_domain.ab_time_domain(fwm_info, qubit_b0,
                                           [qubit_info, qubit_b1, qubit_b2],
                                           delays, drive_amp, '4m1', fwm_amp = 0.5,
                                           plot_seqs=False,
                                           bgcor=True, seq=None)
        ab_t.measure_keysight()
    bla
    

if 0: # q func test
    from scripts.single_cavity import Qfunction
    Qfun = Qfunction.QFunction(qubit_info, amax=1, N=10, amaxx=None, Nx=None, amaxy=None, Ny=None,
                 seq=None, delay=0, saveas=None, bgcor=False)
    Qfun.measure_keysight()

if 0: # fwm spec
    import FWM_spec
    fwm_gen = mclient.instruments['MXG']
    target = 5063.3e6 - 100e6 + 67e6 - 11.0258e6#5.219e9
#    target = 5.02602e9
    for power in [.1]:
        spec = FWM_spec.FWM_spec(qubit_info, cavity_infoA, fwm_info1, fwm_gen, 2.5, 
                                 750e3, np.linspace(target-1e6, target+1e6, 11), power, 
                                 '4m1', plot_seqs=False, bgcor=False)
        spec.measure()
#        spec = FWM_spec.FWM_spec(qubit_info, cavity_infoA, fwm_info1, fwm_gen, 2, 
#                         800e3, np.linspace(target-.2e6, target+.2e6, 101), power, 
#                         '4m1', plot_seqs=False, bgcor=False)
#        spec.measure()

if 0: #abt mixing spec
    fwm_gen = mclient.instruments['SCfwm']
    qubit1bob1_info = mclient.get_qubit_info('qubit1bob1')
    w_q=5024.11e6
    w_b=6082.2e6
    w_a=4062.75e6
    target = w_b + w_q - w_a - 1.98e6 
    freqs = np.linspace(target-0.75e6, target+0.75e6, 41)
#    powers = [-20, -10, 0]
    powers = [0]
    
    shift_freq = np.zeros(len(powers))
    from .FWM import FWM_abt_spec
    for i, power in enumerate(powers):
        abt_spec = FWM_abt_spec.FWM_abt_spec(qubit1bob1_info, cavity_infoA, fwm_gen, 200e3, .7,
                     freqs, power, '4m1', '3m1')
        abt_spec.measure()
        shift_freq[i] = g1f0.xs[np.argmax(g1f0.ampdata[:])]

if 0: # abt mixing and then qubit ssb
    from .single_qubit import ssbspec
    c = cavity_infoA.rotate
#    for delay in [1e3, 50e3, 100e3, 150e3, 200e3, 250e3]:
    for delay in [200e3]:
        seq = sequencer.Sequence()
        seq.append(sequencer.Trigger(250))
#        seq.append(pulselib.Constant(int(500), 1, chan='3m1'))
#        seq.append(sequencer.Combined([
#                c(.7, 0),
#                pulselib.Constant(int(cavity_infoA.w*4.0), 1, chan='3m1')
#                ]))        
    
        seq.append(pulselib.Constant(int(delay), 1, chan='4m1'))
        seq.append(pulselib.Delay(50e3))
        
        spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
    #                                       np.linspace(-11.0e6, -8.6e6, 51), 
                                           np.linspace(-5e6, -3.5e6, 51), 
                                           np.linspace(-2.7e6, -1.7e6, 31), 
                                           np.linspace(-.5e6, .5e6, 31),
                                           )), 
                               seq=seq, plot_seqs=False, extra_info=cavity_infoA)
        spec.measure_keysight()
    bla


if 0: # abt mixing
    os.chdir(r'C:/qrlab/scripts/FWM/')
    from .FWM import FWM_abt
    xvec = np.linspace(-1, 1, 3)
#    abt = FWM_abt.FWM_abt(qubit_info, cavity_infoA, cavity_infoB, fwm_info, 100, 
#                          np.linspace(-1, 1, 10), np.linspace(-1, 1, 10), seq=None,
#                          generate=True, plot_seqs = True)
    abt = FWM_abt.FWM_abt(qubit_info, cavity_infoA, cavity_infoB, fwm_info, 
                          xvec, xvec, 0, which_cavity = 'b', seq=None, saveas=None, 
                          plot_seqs=True, generate = True)
    abt.measure_keysight()

if 0: #abt time domain 
    
    fwm_gen = mclient.instruments['SCfwm']
    qubit1bob1_info = mclient.get_qubit_info('qubit1bob1')
    delays = np.linspace(0, 150e3, 31)
    from .FWM import FWM_abt_t1
    

    abt_t1 = FWM_abt_t1.FWM_abt_t1(qubit1bob1_info, cavity_infoA, 
                                    delays, .7, '4m1', '3m1')
    abt_t1.measure_keysight()


if 0: # f0 - g1 fwm test
    fwm_gen = mclient.instruments['SCpump']
#    target = 4.96386e9 * 2 - 221.2e6 - 6.92618e9   this is original set values (juliang)
#    target = 4.96356e9 * 2 - 221.2e6 + 6.92618e9    4.96356e9 is the frequency at the center
#    target = 6.926e9
    target = 4.96320e9 * 2 - 221.2e6 - 6.92605e9
#    freqs = np.linspace(target-3e6, target+3e6, 50)    this is original set values (juliang)
    freqs = np.linspace(target-5.0e6, target+1e6, 51)
    amps = [.002, .003, .004, .005, .006, .007]    # Jeff's 
    powers = [10, 12.5, 15]     #Jeff's
    shift_freq = np.zeros((len(amps), len(powers)))
    from .FWM import FWM_f0g1
    for i, amp in enumerate(amps):
        for j, power in enumerate(powers):
            f0g1 = FWM_f0g1.FWM_f0g1(qubit_info, ef_info, fwm_gen, 5e3, 
                         freqs, power, amp, '2m1')
            f0g1.measure()
            shift_freq[i, j] = f0g1.xs[np.argmax(f0g1.ampdata[:])]
        
        
if 0: # f0 - g1 time domain test
    fwm_gen = mclient.instruments['SCpump']
    delays = np.linspace(0, 20e3, 151)
    from .FWM import FWM_f0g1_t1
    amps = [.002, .003, .004, .005, .006, .007]
    powers = [10, 12.5, 15]
    t1s = np.zeros_like(shift_freq)
    for i, amp in enumerate(amps):
        for j, power in enumerate(powers):
            fwm_gen.set_power(power)
            fwm_gen.set_frequency(shift_freq[i, j])
            f0g1_t1 = FWM_f0g1_t1.FWM_f0g1_t1(qubit_info, ef_info, fwm_gen, delays, 
                         amp, '2m1', plot_seqs = False)
            t1s[i, j] = f0g1_t1.measure_keysight()


if 0: # Cat pumping ssbspec
    from .FWM import cat_pump_ssbspec
    qubit1bob2_info = mclient.get_qubit_info('qubit1bob2')
    qubit1bob4_info = mclient.get_qubit_info('qubit1bob4')
    pump_info = mclient.get_qubit_info('pump_info')
    fwm_info = mclient.get_qubit_info('FWM_info')
#    freqs = np.linspace(.2e6, -.2e6, 61)
    freqs = np.linspace(-0.1e6, 0.1e6, 61)
#    ge_amps = np.linspace(.0005, .01, 5)
#    fwm_amps = np.linspace(.1, .8, 5)
    delay_times=[100e3]#37.74e3]     # 500e3 for cw mode and 50 for pulse mode
    pump_amps = [.0028]   # 0.01 for pulse mode
    fwm_amps = [0.75]   # 0.8 for pulse mode
    for delay_t in delay_times:
        for pump_amp in pump_amps:
            for fwm_amp in fwm_amps:
                cat_p_ssb = cat_pump_ssbspec.cat_pump_ssbspec(pump_info, fwm_info, qubit_info, 
                                                              freqs, delay_t, pump_amp, fwm_amp, '4m1', 
                                                              pulsed=False, plot_seqs=False)
                cat_p_ssb.measure_keysight()
    bla

if 0: # Cat pumping ssbspec polytone
    from .FWM import cat_pump_ssbspec_polytone
    qubit1bob2_info = mclient.get_qubit_info('qubit1bob2')
    fwm_info_list = [mclient.get_qubit_info('FWMinfo')]
    fwm_ssb_info = mclient.get_qubit_info('FWMe2g4_info')
    
    freqs = np.linspace(-10e6, 1e6, 51)
#    ge_amps = np.linspace(.0005, .01, 5)
#    fwm_amps = np.linspace(.1, .8, 5)
    delay=500e3     # 500e3 for cw mode and 50 for pulse mode
    ge_amp = .01   # 0.01 for pulse mode
    fwm_amp = .8   # 0.8 for pulse mode
    
    fwm_amps= [0.8]

    cat_p_ssb = cat_pump_ssbspec_polytone.cat_pump_ssbspec_polytone(qubit_info, qubit1bob2_info, 
                                  fwm_ssb_info, fwm_info_list, freqs, delay,
                                  ge_amp, fwm_amp, fwm_amps, '4m1', 
                                  pulsed=False, plot_seqs=False)
    cat_p_ssb.measure_keysight()


            
if 0: #cat pumping time domain 
    
    fwm_gen = mclient.instruments['SCfwm']
    qubit1bob2_info = mclient.get_qubit_info('qubit1bob2')
    delays = np.linspace(0, 100e3, 31)
    from .FWM import cat_pump_t1
    ge_amps = [.003]
    fwm_amps = [.5]
    
#    shift_freq = np.zeros(len(powers))
    for ge_amp in ge_amps:
        for fwm_amp in fwm_amps:
            cat_p_t1 = cat_pump_t1.cat_pump_t1(qubit_info, qubit1bob2_info, fwm_info,
                                               delays, ge_amp, fwm_amp, '4m1', plot_seqs=False)
            cat_p_t1.measure_keysight()
            
if 0: # Cat pumping two-tone ssbspec
    from .FWM import cat_pump_simul_ssbspec
#    qubit1bob2_info = mclient.get_qubit_info('qubit1bob2')
#    qubit1bob4_info = mclient.get_qubit_info('qubit1bob4')
    pump_info = mclient.get_qubit_info('pump_info')
    fwm_info = mclient.get_qubit_info('FWM_info')
#    freqs = np.linspace(.2e6, -.2e6, 61)
    freqs = np.linspace(-0.2e6, 0.2e6, 61)
#    ge_amps = np.linspace(.0005, .01, 5)
#    fwm_amps = np.linspace(.1, .8, 5)
    delay_times=[30e3]     # 500e3 for cw mode and 50 for pulse mode
    pump_amps = [.005]   # 0.01 for pulse mode
    fwm_amps = [0.6]   # 0.8 for pulse mode
    for delay_t in delay_times:
        for pump_amp in pump_amps:
            for fwm_amp in fwm_amps:
                cat_p_ssb = cat_pump_simul_ssbspec.cat_pump_ssbspec(pump_info, fwm_info, qubit_info, 
                                                              freqs, delay_t, pump_amp, fwm_amp, '4m1', 
                                                              pulsed=False, plot_seqs=False)
                cat_p_ssb.measure_keysight()
    bla
            

if 0: # Cat pumping then qubit ssb
    from .single_qubit import ssbspec
    pump_info = mclient.get_qubit_info('pump_info')
    fwm_info = mclient.get_qubit_info('FWM_info')
#    for dt in [1e3, 50e3, 100e3]:
#    fwm_amp = 0.7
#    fwm_amp = 0.07
#    pump_amp = .005
#    pump_amp = .005   # for testing pumping signal (juliang)
#    for dt in [20e3, 40e3, 60e3, 80e3]:
    for fwm_amp in [0.75]:
        for pump_amp in [.0028]:
            for dt in [37.74e3]: 
                seq = sequencer.Sequence()
                seq.append(sequencer.Trigger(250))
                seq.append(sequencer.Constant(500, 1, chan='4m1'))
                seq.append(sequencer.Combined([
                        sequencer.Constant(int(dt), 1, chan='4m1'),
                        sequencer.Constant(int(dt), pump_amp, chan=pump_info.sideband_channels[0]),
#                        sequencer.Constant(int(dt), pump_amp, chan=pump_info.sideband_channels[1]),
                        sequencer.Constant(int(dt), fwm_amp, chan=fwm_info.sideband_channels[0]),
#                        sequencer.Constant(int(dt), fwm_amp, chan=fwm_info.sideband_channels[1])
                    ]))
                seq.append(sequencer.Delay(4e3))
        #        seq.append(sequencer.Delay(5e3))
                    
                    
            #        seq.append(sequencer.Trigger(250))
            #        seq.append(sequencer.Constant(500, 1, chan='4m1'))
            #        seq.append(sequencer.Join([sequencer.Combined([sequencer.Constant(int(dt), fwm_amp, chan=fwm_info.sideband_channels[0]),
            #                                                     sequencer.Constant(int(dt), fwm_amp, chan=fwm_info.sideband_channels[1]),           
            #                                                     sequencer.Constant(int(dt), ge_amp, chan=qubit_info.sideband_channels[0]),
            #                                                     sequencer.Constant(int(dt), ge_amp, chan=qubit_info.sideband_channels[1]),
            #                                                     sequencer.Constant(int(dt), 1, chan='4m1'),
            #                                 ]),
            #                        sequencer.Delay(50e3),
            #                        ]))
                spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
        #                                           np.linspace(-9e6, -6e6, 51), 
        #                                           np.linspace(-7.2e6, -6e6, 51), 
        #                                           np.linspace(-5e6, -3.5e6, 31), 
        #                                           np.linspace(-2.7e6, -1.7e6, 31), 
        #                                           np.linspace(-.5e6, .5e6, 31),
                                                    np.linspace(-14e6, 1e6, 101),
        #                                            np.linspace(1e6, 2e6, 1)
                                                   )), 
                                       seq=seq, plot_seqs=False, extra_info = [pump_info, fwm_info])
                spec.measure_keysight()

if 0: # Cat pumping then q func
    from scripts.single_cavity import Qfunction
    pump_info = mclient.get_qubit_info('pump_info')
    fwm_info = mclient.get_qubit_info('FWM_info')
    fwm_amp = .5
    pump_amp = .0028
    
    for dt in [40e3]:
#    for dt in [40e3]:
        seq = sequencer.Sequence()
        seq.append(sequencer.Trigger(250))
        seq.append(sequencer.Constant(500, 1, chan='4m1'))
        seq.append(sequencer.Combined([
                sequencer.Constant(int(dt), 1, chan='4m1'),
                sequencer.Constant(int(dt), pump_amp, chan=pump_info.sideband_channels[0]),
#                sequencer.Constant(int(dt), pump_amp, chan=pump_info.sideband_channels[1]),
                sequencer.Constant(int(dt), fwm_amp, chan=fwm_info.sideband_channels[0]),
#                sequencer.Constant(int(dt), fwm_amp, chan=fwm_info.sideband_channels[1])
            ]))
        seq.append(sequencer.Delay(5e3))
        
        Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=1.5, N=11, amaxx=None, Nx=None, amaxy=None, Ny=None,
                     seq=seq, delay=0, saveas=None, bgcor=False, extra_info=[fwm_info, pump_info], cav_switch='3m1')
        Qfun.measure_keysight()


if 0: # Cat pumping and then wigner
    from scripts.single_cavity import WignerbyParity
#    seq = sequencer.Join([prepareB, geph(pi/2,0), sequencer.Delay(950), cB(1.65, -pi*0.175),
#                          geqs(pi,0), cB(-1.65, -pi*0.02)])
#    seq = sequencer.Join([sequencer.Trigger(250), cB(.5, 0)])
    pump_info = mclient.get_qubit_info('pump_info')
    fwm_info = mclient.get_qubit_info('FWM_info')
    fwm_amp = 0.75
    pump_amp = 0.0028
    
    for dt in [88.1e3, 18.9e3, 6.3e3, 62.9e3]:
#    for dt in [37.7e3, 31.45e3, 25.15e3, 18.87e3, 12.58e3, 6.28e3]:
#    for dt in [88.1e3]:   
        seq = sequencer.Sequence()
        seq.append(sequencer.Trigger(250))
        seq.append(sequencer.Constant(500, 1, chan='4m1'))
        seq.append(sequencer.Combined([
                sequencer.Constant(int(dt), 1, chan='4m1'),
                sequencer.Constant(int(dt), pump_amp, chan=pump_info.sideband_channels[0]),
                sequencer.Constant(int(dt), fwm_amp, chan=fwm_info.sideband_channels[0]),
            ]))
        seq.append(sequencer.Delay(4e3))

        x_range = 0.5
        for x_start in [-2.4, -1.8, -1.2, -0.6, 0, 0.6, 1.2, 1.8]:
            Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoB,t_ge=210, t_gf=0,
                                                 xs = np.linspace(x_start,x_start+x_range,6), ys = np.linspace(-1.2,1.2,25),
#                                                 amax=2.5, N=15,amaxx=2.4, Nx=17, amaxy=1.2, Ny=13,
                                                 seq=seq, delay=0, saveas=None, bgcor=True, zmax=29, zmin=-29, cav_switch='3m1',
                                                 extra_info=[fwm_info, pump_info])
            Wfun.measure_keysight() 

#    Nx=31, Ny=15 amaxx=3.5, amxy=1 from yesterday. 
    
    
    

if 0: # cav transmission sweeping FWM frequency
    from .FWM import ROCavSpectroscopy_keysight_catpumptest
    
    rofreq = 7.27877e9
    freq_range = .4e6
    fwm_info = mclient.get_qubit_info('FWM_info')
    fwm_gen = mclient.instruments['SCpump']
    
    ro = ROCavSpectroscopy_keysight_catpumptest.ROCavSpectroscopy_keysight_catpumptest(qubit_info, np.linspace(-2, 3, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
#                                             np.linspace(rofreq, rofreq+freq_range, 1), 
                                             qubit_pulse=False, seq=None, fwm_info=fwm_info, plot_seqs=True,
                                             fwm_gen = fwm_gen)
    ro.measure()

    bla

if 0: # cav transmission (sweeping RO freq) with FWM
    from .FWM import ROCavSpectroscopy_withpump

    rofreq = 7.33971e9
    freq_range = 0.5e6
    fwm_info = mclient.get_qubit_info('FWM_info')    
    ro = ROCavSpectroscopy_withpump.ROCavSpectroscopy(qubit_info, fwm_info, np.linspace(4, 9, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 41), fwm_amp=0.95,
                                             qubit_pulse=False, seq=None, plot_seqs=True)
    ro.measure()
    bla
    
if 0: # EF rabi after FWM pumping
    from .single_qubit import efrabi
    cavity_infoR = mclient.get_qubit_info('CavityR')
    fwm_info = mclient.get_qubit_info('FWM_info')    
    dt = 50e3
    fwm_amp = 0.1
    drive_amp = 0.008
    for delay_time in [10e3, 30e3, 40e3, 60e3, 80e3]:
        seq = sequencer.Sequence()
        seq.append(sequencer.Trigger(250))
        seq.append(sequencer.Constant(500, 1, chan='13m1'))
        seq.append(sequencer.Combined([
                sequencer.Constant(int(dt), 1, chan='13m1'),
                sequencer.Constant(int(dt), drive_amp, chan=cavity_infoR.sideband_channels[0]),
    #            sequencer.Constant(int(dt), fwm_amp, chan=fwm_info.sideband_channels[0]),
            ]))
        seq.append(sequencer.Delay(delay_time))
    
        dig = mclient.instruments['dig']
        dig.set_naverages(1000)
        efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.3, 0.3, 21), plot_seqs=True, selective=False, seq=seq, 
                            postseq = None, extra_info=cavity_infoR )
        efr.measure_keysight()
        period = efr.fit_params['period'].value
        dig.set_naverages(3000)
        efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.3, 0.3, 51), first_pi=False, selective=False, force_period=period, seq=seq,
                            postseq = None, extra_info=cavity_infoR )
        efr.measure_keysight()
        dig.set_naverages(1000)
    bla    
    
    
if 0: # a b ssbspec
    from .FWM import cat_pump_ssbspec
    bob1alice1 = mclient.get_qubit_info('bob1alice1')
    bob2alice2 = mclient.get_qubit_info('bob2alice2')
    pump_info = mclient.get_qubit_info('pump_info')
    fwm_info = mclient.get_qubit_info('FWM_info')
    freqs = np.linspace(-0.2e6, 0.2e6, 61)
#    freqs = np.linspace(-.1e6, .1e6, 51)
#    ge_amps = np.linspace(.0005, .01, 5)
#    fwm_amps = np.linspace(.1, .8, 5)
    delay_times=[30e3]#37.74e3]     # 500e3 for cw mode and 50 for pulse mode
    pump_amps = [.005]   # 0.01 for pulse mode
    fwm_amps = [0.9]   # 0.8 for pulse mod3    for delay_t in delay_times:
    for delay_t in delay_times:
        for pump_amp in pump_amps:
            for fwm_amp in fwm_amps:
                cat_p_ssb = cat_pump_ssbspec.cat_pump_ssbspec(pump_info, fwm_info, bob1alice1, 
                                                              freqs, delay_t, pump_amp, fwm_amp, '4m1', 
                                                              pulsed=False, plot_seqs=False)
                cat_p_ssb.measure_keysight()
    bla
    
if 0: # Cat pumping spec
    fwm_gen = mclient.instruments['MXG']
#    qubit1bob2_info = mclient.get_qubit_info('qubit1bob2')
    qubit_a1b1 = mclient.get_qubit_info('qubit_a1b1')
    qubit_a2b2 = mclient.get_qubit_info('qubit_a2b2')
    cavity_infoR = mclient.get_qubit_info('cavityR')
#    w_q=5024.11e6
    w_r=7339.71e6
    w_b=6082.2e6
#    target = 2 * w_b - w_r
    target = 2804.40e6 #4.8247e9
    freqs = np.linspace(target-0.15e6, target+0.15e6, 41)
#    powers = [-20, -10, 0]
#    powers = [8]
    powers = [12.5]
    amps = [.010]
    
#    shift_freq = np.zeros(len(powers))
    from .FWM import cat_pump_spec
    for i, power in enumerate(powers):
        for j, amp in enumerate(amps): 
            spec = cat_pump_spec.cat_pump_spec(qubit_info, qubit_info, fwm_gen, 10e3,
                         freqs, power, amp, '13m1', fwm_info=cavity_infoR, plot_seqs=True)
            spec.measure()
#        shift_freq[i] = g1f0.xs[np.argmax(g1f0.ampdata[:])]            
    bla
   
    
if 0: # ab pumping then qubit ssb
    dig.set_naverages(10000)
    from .single_qubit import ssbspec
    fwm_info = mclient.get_qubit_info('FWM_info')
#    delay_times=[10e3, 30e3, 50e3, 80e3]
    pump_times=np.linspace(26e3, 18e3, 1)
    drive_amps = [0.015]#, 0.005, .01, 0.015]   # 0.01 for pulse mode
    measdelay = 5e3
    for dt in pump_times:
        for drive_amp in drive_amps:
            seq = sequencer.Sequence()
            seq.append(sequencer.Trigger(250))
#            seq.append(sequencer.Combined([
#                        cA(1.2,0), cB(0.7,0)]))
            seq.append(sequencer.Constant(int(dt), 1, chan='13m1'))
            seq.append(sequencer.Combined([
                    sequencer.Constant(int(dt), 1, chan='13m1'),
                    sequencer.Constant(int(dt), drive_amp, chan=cavity_infoR.sideband_channels[0]),
                ]))
            seq.append(sequencer.Delay(measdelay))
            spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
                                                np.linspace(-19e6, 1e6, 121),
                                               )), 
                                   seq=seq, plot_seqs=False, extra_info = [cavity_infoR, fwm_info])#, cavity_infoA, cavity_infoB])
            spec.measure_keysight()
    bla                
                
if 0: # ab pumping decay and then qubit ssb
    from .single_qubit import ssbspec
    
    cavity_infoR = mclient.get_qubit_info('cavityR')
    fwm_info = mclient.get_qubit_info('FWM_info')
#    delay_times=[10e3, 30e3, 50e3, 80e3]
    delay_times=np.linspace(12e3, 30e3, 1)
    drive_amps = [0.015]#, 0.005, .01, 0.015]   # 0.01 for pulse mode
#    fwm_amps = [0.04]#, 0.02, 0.3, 0.4]   # 0.8 for pulse mode
    pumptime = 12e3
    measdelay = 5e3
    for dt in delay_times:
        for drive_amp in drive_amps:
            seq = sequencer.Sequence()
            seq.append(sequencer.Trigger(250))
            seq.append(sequencer.Constant(500, 1, chan='13m1'))
            seq.append(sequencer.Combined([
                    sequencer.Constant(int(pumptime), 1, chan='13m1'),
                    sequencer.Constant(int(pumptime), drive_amp, chan=cavity_infoR.sideband_channels[0]),
                ]))
#            seq.append(sequencer.Constant(int(dt), 1, chan='4m1'))
            seq.append(sequencer.Delay(dt))
            seq.append(sequencer.Delay(measdelay))
            spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
                                                np.linspace(-14e6, 1e6, 76),
                                               )), 
                                   seq=seq, plot_seqs=False, extra_info = [cavity_infoR, fwm_info])
            spec.measure_keysight()
    bla

if 1: #ab time domain 
    dig.set_naverages(8000)    
    qubit_a1b1 = mclient.get_qubit_info('qubit_a1b1')
    qubit_a2b2 = mclient.get_qubit_info('qubit_a2b2')
#    qubit_a2b1 = mclient.get_qubit_info('qubit_a2b1')
    qubit_a3b3 = mclient.get_qubit_info('qubit_a3b3')
    fwm_info = mclient.get_qubit_info('FWM_info')
    qubit_b1 = mclient.get_qubit_info('qubit_b1')
    qubit_b2 = mclient.get_qubit_info('qubit_b2')    
    qubit_a1 = mclient.get_qubit_info('qubit_a1')
    qubit_a2 = mclient.get_qubit_info('qubit_a2')    
    
    MXG = mclient.instruments['MXG']
        
    from .FWM import ab_time_domain

#    FWM_settings = {6: 2804.98e6}#{4.5:2805.05e6, 10.7:2804.62e6, 2:2805.13e6, 9.5: 2804.69e6}
    drive_amps = np.linspace(0.008, 0.016, 5)   # 0.0001 to mimic zero for pump without drive, probably easier to just turn SCres off
    delays = np.linspace(0e3, 40e3, 21)
    
    for drive_amp in drive_amps:
        for FWM_freq in np.linspace(2804.36e6, 2804.42e6, 7):
#        for FWM_power in FWM_settings.keys():
#            MXG.set_power(FWM_power)
#            MXG.set_frequency(FWM_settings[FWM_power])
            MXG.set_frequency(FWM_freq)
            time.sleep(.1)
#            seq = sequencer.Sequence()
#            seq.append(sequencer.Trigger(250))
#            seq.append(sequencer.Combined([
#                        cA(1.2,0), cB(0.7,0)]))
            ab_t = ab_time_domain.ab_time_domain(fwm_info, cavity_infoR,
                                               [qubit_info, qubit_a1b1, qubit_a2b2],
#                                               [qubit_info, qubit_a1, qubit_a1b1, qubit_a2b1],
                                               delays, drive_amp, '13m1', plot_seqs=False, 
                                               bgcor=True, seq=None,)# extra_info = [cavity_infoA, cavity_infoB] )
            ab_t.measure_keysight()
    bla

    
if 1: #ab pump decay
    dig.set_naverages(8000)
    qubit_a1b1 = mclient.get_qubit_info('qubit_a1b1')
    qubit_a2b2 = mclient.get_qubit_info('qubit_a2b2')
#    qubit_a3b3 = mclient.get_qubit_info('bob3alice3')
    fwm_info = mclient.get_qubit_info('FWM_info')
    
    from .FWM import ab_pump_decay

    delays = np.concatenate((np.linspace(0e3, 28e3, 15), np.linspace(30e3, 130e3, 21)))
#    delays = np.linspace(0, 50e3, 11)
    drive_amps = [0.015]
    fwm_amp = 0.1
    pump_times = [25e3]
    FWM_settings = {4.5:2805.05e6}#{10.7:2804.62e6}#{6: 2804.98e6, 2:2805.13e6} 
    for FWM_power in list(FWM_settings.keys()):
        MXG.set_power(FWM_power)
        MXG.set_frequency(FWM_settings[FWM_power])
        time.sleep(.1)

        for drive_amp in drive_amps:
            for pump_time in pump_times:
                ab_t = ab_pump_decay.ab_time_domain(fwm_info, cavity_infoR,
                                                   [qubit_info, qubit_a1b1, qubit_a2b2],# bob3alice3],
                                                   delays, pump_time, fwm_amp, drive_amp, '13m1', measdelay=5e3, 
                                                   plot_seqs=False, 
                                                   bgcor=True)
                ab_t.measure_keysight()
    bla

