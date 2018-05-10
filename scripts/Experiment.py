import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer

alz = mclient.instruments['alazar']
fg = mclient.instruments['funcgen']
brick2 = mclient.instruments['brick2']
readout = mclient.instruments['readout']
alz = mclient.instruments['alazar']

qubits = mclient.get_qubits()
readout_info = mclient.get_readout_info('readout')

qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
#qubitph_info = mclient.get_qubit_info('qubit2ge_ph')
#efph_info = mclient.get_qubit_info('qubit2ef_ph')

#gf_info1 = mclient.get_qubit_info('Qubit1gf')
#cavity_info1R = mclient.get_qubit_info('cavity1R')
cavity_info1A = mclient.get_qubit_info('cavity1A')
cavity_info1B = mclient.get_qubit_info('cavity1B')
#Qswitch_info1A = mclient.get_qubit_info('Qswitch1A')
#Qswitch_info1B = mclient.get_qubit_info('Qswitch1B')

cA = cavity_info1A.rotate
cB = cavity_info1B.rotate
ge = qubit_info.rotate
#geph = qubitph_info.rotate
geqs= qubit_info.rotate_quasilective
ges= qubit_info.rotate_selective
ef = ef_info.rotate
#geph = qubitph_info.rotate
#efph = efph_info.rotate
#efqs= ef_info.rotate_quasilective

gepi = qubit_info.rotate(np.pi,0)
gepi2 = qubit_info.rotate(np.pi/2,0)
efpi = ef_info.rotate(np.pi,0)
#gfpi = gf_info.rotate(np.pi,0)

pi=np.pi


prepareA = sequencer.Join([sequencer.Trigger(250), cA(1.5,0)])
prepareB = sequencer.Join([sequencer.Trigger(250), cB(1.5,0)])
prepareAF = sequencer.Join([sequencer.Trigger(250), gepi, efpi, cA(1.5,0)])
prepareBF = sequencer.Join([sequencer.Trigger(250), cB(2.0,0), gepi, efpi])

if 0: # Kerr revival
    from scripts.single_cavity import Qfunction
    for delay in [150, 200, 250, 300, 350, 400]:
        seq = sequencer.Join([sequencer.Trigger(250), cA(2.0, 0), sequencer.Repeat(sequencer.Delay(10000), delay/10)])
        Qfun = Qfunction.QFunction(qubit_info, cavity_info1A, amax=2.5, N=15, amaxx=None, Nx=None, amaxy=None, Ny=None,
                     seq=seq, delay=0, saveas=None, bgcor=False)
        Qfun.measure()
    bla

if 0: # Chi evolution for Cavity A
    from scripts.single_cavity import Qfunction
    for delay in [690]:
        seq = sequencer.Join([prepareA, gepi, sequencer.Delay(delay), cA(2.0, pi*0.0),
                              gepi])
        Qfun = Qfunction.QFunction(qubit_info, cavity_info1A, amax=1.5, N=9, amaxx=None, Nx=None, amaxy=None, Ny=None,
                     seq=seq, delay=5, bgcor=False, Qswitch_infoA=Qswitch_info1A, Qswitch_infoB=Qswitch_info1B, extra_info=[Qswitch_info1A, Qswitch_info1B,])
        Qfun.measure()

if 0: # Chi evolution for Cavity B
    from scripts.single_cavity import Qfunction
    for delay in [350]:
        seq = sequencer.Join([prepareB, gepi, sequencer.Delay(delay), #cB(1.65, -pi*0.175),
                              gepi])
        Qfun = Qfunction.QFunction(qubit_info, cavity_info1B, amax=2.0, N=9, amaxx=None, Nx=None, amaxy=None, Ny=None,
                     seq=seq, delay=5, bgcor=False, Qswitch_infoA=Qswitch_info1A, Qswitch_infoB=Qswitch_info1B, extra_info=[Qswitch_info1A, Qswitch_info1B,])
        Qfun.measure()
        bla

if 0: # make a cat a la Brian for cavity A
    from scripts.single_cavity import Qfunction
    for delay in [629]:
        seq = sequencer.Join([prepareA, ge(pi/2, 0), sequencer.Delay(629),
                              cA(1.5, 0), geqs(pi, 0), cA(-1.5, 0)])
        Qfun = Qfunction.QFunction(qubit_info, cavity_info1A, amax=None, N=None, amaxx=2.0, Nx=11, amaxy=2.0, Ny=11,
                     seq=seq, postseq=efpi, delay=5, bgcor=False, extra_info=[ef_info])
        Qfun.measure()
        bla

if 0: # make a cat a la Brian for Cavity B
    from scripts.single_cavity import Qfunction
    seq = sequencer.Join([prepareB, ge(pi/2, 0), sequencer.Delay(307), cB(1.5, 0),
                          geqs(pi,0), cB(-1.5, 0)])
    Qfun = Qfunction.QFunction(qubit_info, cavity_info1B, amax=2.5, N=15, amaxx=None, Nx=None, amaxy=None, Ny=None,
                 seq=seq, postseq=efpi, delay=5, bgcor=False, extra_info=[ef_info,])
    Qfun.measure()
    bla

if 0: # ge entangled cat
    from scripts.single_cavity import Qfunction
    from scripts.single_cavity import WignerbyParity
    prepareAB = sequencer.Join([sequencer.Trigger(250), gepi2, sequencer.Combined([cA(2.0,0),cB(1.65,0)]), ])
    disentangle = sequencer.Join([sequencer.Combined([cA(2.00, pi*0.33), cB(1.65, -pi*0.175)]),
                                  geqs(np.pi,0),
                                  sequencer.Combined([cA(-1.73, pi*0.17), cB(-1.65, -pi*0.02)]), ])
#    seq = sequencer.Join([prepareAB, sequencer.Delay(950), disentangle, cB(1.65, -pi*0.02)])
#    Qfun = Qfunction.QFunction(qubit_info, cavity_info1A, amax=2.5, N=15, amaxx=None, Nx=None, amaxy=None, Ny=None,
#                 seq=seq, delay=5, saveas=None, bgcor=True, singleshotbin=True, extra_info=[cavity_info1B])
#    Qfun.measure()
#
#    seq = sequencer.Join([prepareAB, sequencer.Delay(950), disentangle, cB(-1.65, -pi*0.02)])
#    Qfun = Qfunction.QFunction(qubit_info, cavity_info1A, amax=2.5, N=15, amaxx=None, Nx=None, amaxy=None, Ny=None,
#                 seq=seq, delay=5, saveas=None, bgcor=True, singleshotbin=True, extra_info=[cavity_info1B])
#    Qfun.measure()

    seq = sequencer.Join([prepareAB, sequencer.Delay(950), disentangle])
#    Wfun = WignerbyParity.WignerFunction(qubitph_info, efph_info, cavity_info1B, t_ge=0, t_gf=205,
#                                         amax=None, N=None, amaxx=1.0, Nx=15, amaxy=1.0, Ny=15,
#                                         seq=seq, delay=5, saveas=None, bgcor=False, extra_info=[cavity_info1A, efph_info, qubit_info,])
    Wfun = WignerbyParity.WignerFunction(qubitph_info, efph_info, cavity_info1A, t_ge=0, t_gf=205,
                                         amax=None, N=None, amaxx=0.8, Nx=15, amaxy=0.8, Ny=15,
                                         seq=seq, delay=5, saveas=None, bgcor=T, extra_info=[cavity_info1B, efph_info, qubit_info,])
    Wfun.measure()

if 0: # vacuum displacement finder for Cavity A after gf Chi evolution
    from scripts.single_cavity import vacuumfinder
    for phase in [-0.04, -0.06, -0.08]:
        seq = sequencer.Join([prepareAF, sequencer.Delay(170)])
        vacf = vacuumfinder.vacuumfinder(qubit_info, ef_info, cavity_info1A, xs=np.linspace(-1.6, -1.1, 11), ys=np.linspace(0.0, 0.5, 11),
                     seq=seq, delay=5, bgcor=False, Qswitch_infoA=Qswitch_info1A, Qswitch_infoB=Qswitch_info1B, extra_info=[ef_info, Qswitch_info1A, Qswitch_info1B,])
        vacf.measure()

if 0: # gf Chi evolution for Cavity A
    from scripts.single_cavity import Qfunction
    for phase in [-0.10]:
        seq = sequencer.Join([sequencer.Trigger(250), gepi, efpi, sequencer.Delay(170), #cA(1.29, pi*phase),
                              efpi, gepi])
        Qfun = Qfunction.QFunction(qubit_info, cavity_info1A, amax=2.5, N=11, amaxx=None, Nx=None, amaxy=None, Ny=None,
                     seq=seq, delay=5, bgcor=False, Qswitch_infoA=Qswitch_info1A, Qswitch_infoB=Qswitch_info1B, extra_info=[ef_info, Qswitch_info1A, Qswitch_info1B,])
        Qfun.measure()

if 1: # gf Chi evolution for Cavity B
    from scripts.single_cavity import Qfunction
    for delay in [325]:
        seq = sequencer.Join([prepareBF, sequencer.Delay(delay), #cB(1.5, pi*0.0),#0.05
                              ef(np.pi, np.pi), gepi])
        Qfun = Qfunction.QFunction(qubit_info, cavity_info1B, amax=2.0, N=11, amaxx=None, Nx=None, amaxy=None, Ny=None,
                     seq=seq, postseq=efpi, delay=5, bgcor=False, extra_info=[ef_info,])
        Qfun.measure()

if 0: # test GF cat cavity A
    from scripts.single_cavity import Qfunction
    seq = sequencer.Join([sequencer.Trigger(250), gepi2, efpi, cA(1.5, 0), sequencer.Delay(170),
                          cA(1.29, -0.1*pi), efpi, geqs(pi, 0), cA(-1.40, -pi*0.025)])
    Qfun = Qfunction.QFunction(qubit_info, cavity_info1A, amax=2.5, N=11, amaxx=None, Nx=None, amaxy=None, Ny=None,
                 seq=seq, delay=5, bgcor=False, Qswitch_infoA=Qswitch_info1A, Qswitch_infoB=Qswitch_info1B, extra_info=[ef_info, Qswitch_info1A, Qswitch_info1B,])
    Qfun.measure()

if 0: # test GF cat cavity B
    from scripts.single_cavity import Qfunction
    seq = sequencer.Join([sequencer.Trigger(250), gepi2, efpi, cB(1.5, 0), sequencer.Delay(170),
                          cB(1.5, pi*0.03), efpi, geqs(pi, 0), cB(-1.5, pi*0.05)])
    Qfun = Qfunction.QFunction(qubit_info, cavity_info1B, amax=2.2, N=9, amaxx=None, Nx=None, amaxy=None, Ny=None,
                 seq=seq, delay=5, bgcor=False,  Qswitch_infoA=Qswitch_info1A, Qswitch_infoB=Qswitch_info1B, extra_info=[ef_info, Qswitch_info1A, Qswitch_info1B,])
    Qfun.measure()
    bla

if 0: # Wigner function by displaced parity for cavity A
    from scripts.single_cavity import WignerbyParity
    seq = sequencer.Join([prepareA, geph(pi/2, 0), sequencer.Delay(700),
                          cA(2.0, 0), geqs(pi, 0), cA(-2.0, 0)])
    Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_info1A, t_ge=0, t_gf=210,
                                         amax=1.2, N=16, amaxx=None, Nx=None, amaxy=None, Ny=None,
                                         seq=seq, delay=5, saveas=None, bgcor=True, extra_info=[ef_info, qubitph_info,])
    Wfun.measure()

if 0: # Wigner function by displaced parity for cavity B
    from scripts.single_cavity import WignerbyParity
    seq = sequencer.Join([prepareB, geph(pi/2,0), sequencer.Delay(950), cB(1.65, -pi*0.175),
                          geqs(pi,0), cB(-1.65, -pi*0.02)])
    Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_info1B, t_ge=0, t_gf=205,
                                         amax=None, N=None, amaxx=1.0, Nx=15, amaxy=1.0, Ny=15,
                                         seq=seq, delay=5, saveas=None, bgcor=False, extra_info=[efph_info,qubitph_info,])
    Wfun.measure()

if 0: # test Joint Chi evolution
    from scripts.single_cavity import Qfunction
#    for delay in [5, 200, 400, 2000, 1000, 3000, 4000, 5000, 6000]:
    for delay in [1000, 1200]:
        seq = sequencer.Join([prepareAB, sequencer.Delay(delay), cB(-1.5, 0)])
        Qfun = Qfunction.QFunction(qubit_info, cavity_info1A, amax=2.5, N=11, amaxx=None, Nx=None, amaxy=None, Ny=None,
                     seq=seq, delay=5, bgcor=False, Qswitch_infoA=Qswitch_info1A, Qswitch_infoB=Qswitch_info1B, extra_info=[Qswitch_info1A, Qswitch_info1B,cavity_info1B,])
        Qfun.measure()
    bla

if 1: # gf entangled cat
#for t_gf in [205, 210, 220]:
    from scripts.single_cavity import WignerbyParity, Qfunction
    prepareAB = sequencer.Join([sequencer.Trigger(250), gepi2, efpi, sequencer.Combined([cA(1.5,0),cB(1.5,0)]), ])
    disentangle = sequencer.Join([sequencer.Combined([cA(1.29, -pi*0.1), cB(1.50, pi*0.03)]),
                                  efpi, geqs(np.pi,0),
                                  sequencer.Combined([cA(-1.40, -pi*0.025), cB(-1.50, pi*0.05)]), ])

#    seq = sequencer.Join([prepareAB, sequencer.Delay(190), disentangle])
#    Wfun = WignerbyParity.WignerFunction(qubitph_info, efph_info, cavity_info1B, t_ge=0, t_gf=205,
#                                         amax=None, N=None, amaxx=1.0, Nx=15, amaxy=1.0, Ny=15,
#                                         seq=seq, delay=5, saveas=None, bgcor=False,
#                                         extra_info=[cavity_info1A, efph_info, qubit_info, ef_info,])
#    Wfun = WignerbyParity.WignerFunction(qubitph_info, efph_info, cavity_info1A, t_ge=0, t_gf=205,
#                                         amax=0.8, N=15, amaxx=None, Nx=None, amaxy=None, Ny=None,
#                                         seq=seq, delay=5, saveas=None, bgcor=True,
#                                         extra_info=[cavity_info1B, efph_info, qubit_info, ef_info,])
#    Wfun.measure()
    seq = sequencer.Join([prepareAB, sequencer.Delay(170), disentangle, cB(1.50, pi*0.05)])
    Qfun = Qfunction.QFunction(qubit_info, cavity_info1A, amax=2.5, N=11, amaxx=None, Nx=None, amaxy=None, Ny=None,
                 seq=seq, delay=5, saveas=None, bgcor=False, singleshotbin=True,
                 Qswitch_infoA=Qswitch_info1A, Qswitch_infoB=Qswitch_info1B,
                 extra_info=[Qswitch_info1A, Qswitch_info1B,cavity_info1B,ef_info])
    Qfun.measure()

    seq = sequencer.Join([prepareAB, sequencer.Delay(170), disentangle, cB(-1.50, pi*0.05)])
    Qfun = Qfunction.QFunction(qubit_info, cavity_info1A, amax=2.5, N=11, amaxx=None, Nx=None, amaxy=None, Ny=None,
                 seq=seq, delay=5, saveas=None, bgcor=False, singleshotbin=True,
                 Qswitch_infoA=Qswitch_info1A, Qswitch_infoB=Qswitch_info1B,
                 extra_info=[Qswitch_info1A, Qswitch_info1B,cavity_info1B,ef_info])
    Qfun.measure()



if 0: # measure large cross Kerr
    from scripts.single_cavity import Qfunction
    for delay in np.linspace(2000, 20000, 10):
        seq = sequencer.Join([sequencer.Trigger(250), cB(1.143, 0), geqs(np.pi, 0), geqs(np.pi,0.30*np.pi), cB(-0.58,0), cA(1.5,0), sequencer.Delay(delay)])
        Qfun = Qfunction.QFunction(qubit1ph_info, cavity_info1A, amax=2.5, N=11, amaxx=None, Nx=None, amaxy=None, Ny=None,
                     seq=seq, delay=5, bgcor=True, Qswitch_infoA=Qswitch_info1A, Qswitch_infoB=Qswitch_info1B, extra_info=[Qswitch_info1A, Qswitch_info1B,cavity_info1B,qubit_info,])
        Qfun.measure()
    bla


if 0: # Weird Halo effect
    brick2.set_rf_on(False)
    from scripts.single_cavity import Qfunction
    for displacement in [-1.5, 1.0, -0.5, 3.0, -2.5, 2.0]:
        seq = sequencer.Join([sequencer.Trigger(250), cB(displacement, 0)])#gepi, cA(1.5, pi*0.085), cA(1.5, pi*0.085)])
        Qfun = Qfunction.QFunction(qubit_info, cavity_info1A, amax=3.0, N=13, amaxx=None, Nx=None, amaxy=None, Ny=None,
                     seq=seq, delay=5, bgcor=False, Qswitch_infoA=Qswitch_info1A, Qswitch_infoB=Qswitch_info1B, extra_info=[Qswitch_info1A, Qswitch_info1B,cavity_info1B,])
        Qfun.measure()

if 0: # load sequence to AWG2
    import awgloader
    seq = ge(np.pi, 0)
    s = sequencer.Sequence()
    s.append(sequencer.Join([sequencer.Constant(250,1,chan=3), seq]))
#    s.append(seq)
    l = awgloader.AWGLoader()
    awg = mclient.instruments['AWG1']
#    awg = mclient.instruments['AWG2']
    l.add_awg(awg, {1: 1, 2: 2, 3: 3, 4: 4})
    s = sequencer.Sequencer(s)
    s = s.render()
    l.load(s)

stopbla

if 1:
    iqg = 66.39+17.30j
    iqe = 9.35-4.39j
    iqg_actual = iqg-(iqe-iqg)/89.0*5.0
    iqe_actual = iqe+(iqe-iqg)/88.0*6.0
    readout.set_IQe(iqe_actual)
    readout.set_IQg(iqg_actual)
    readout.set_IQe_radius(np.abs(iqe_actual-iqg_actual)/2)

if 1:
    readout.set_IQe(-39.4+36.7j)
    readout.set_IQg(-0.3-0.6j)
    readout.set_IQe_radius(30)

if 1: # High power readout
    ag1_RO=mclient.instruments['ag1_RO']
    brick1_LO=mclient.instruments['brick1_LO']
    ag1_RO.set_frequency(7686.44e6)
    brick1_LO.set_frequency(7736.44e6)
    ag1_RO.set_power(6.5)
    readout.set_pulse_len(500)

if 1: # Dispersive readout
    ag1_RO=mclient.instruments['ag1_RO']
    brick1_LO=mclient.instruments['brick1_LO']
    ag1_RO.set_frequency(7697.5e6)
    brick1_LO.set_frequency(7747.5e6)
    ag1_RO.set_power(-28)
    readout.set_IQe(0.61-0.28j)
    readout.set_IQg(3.43-0.52j)
    readout.set_pulse_len(1000)
