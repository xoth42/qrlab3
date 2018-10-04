import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer

alz = mclient.instruments['alazar']
fg = mclient.instruments['funcgen']
#laserfg = mclient.instruments['laserfg']
#awg2 = mclient.instruments['AWG2']
#ag1 = mclient.instruments['ag1_RO']

#qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
#cavity_infoR = mclient.get_qubit_info('cavity1R')
cavity_infoA = mclient.get_qubit_info('cavityAlice')
cavity_infoB = mclient.get_qubit_info('cavityBob')
#Qswitch_info1A = mclient.get_qubit_info('Qswitch1A')
#Qswitch_info1B = mclient.get_qubit_info('Qswitch1B')

#qubit_info2 = mclient.get_qubit_info('qDblCoax2')
#ef_info2 = mclient.get_qubit_info('eDblCoax2')
#cavity_info2A = mclient.get_qubit_info('cavity2A')
#cavity_info2B = mclient.get_qubit_info('cavity2B')

cA = cavity_infoA.rotate
cB = cavity_infoB.rotate
ge = qubit_info.rotate
ges= qubit_info.rotate_selective
ef = ef_info.rotate
efs= ef_info.rotate_selective
efpi = sequencer.Sequence(ef_info.rotate(np.pi, 0))


if 1: # figure out how fast the kerr spins the cavity
    from scripts.single_cavity import Qfunction
#    seq = sequencer.Join([sequencer.Trigger(250), cB(1.0, 0)])
#    Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=2.5, N=21, amaxx=None, Nx=None, amaxy=None, Ny=None,
#             seq=seq, delay=0, saveas=None, bgcor=False, extra_info=ef_info)
#    Qfun.measure()
    for dt in [400]:
#        seq = sequencer.Join([sequencer.Trigger(250), cB(1.0, np.pi/2)])
#        seq.append(sequencer.Delay(dt))
        seq = sequencer.Join([sequencer.Trigger(250), cB(1.5, 0), ge(np.pi,0)])
        seq.append(sequencer.Delay(dt))
        seq.append(cB(1.5, 0))
        seq.append(ge(np.pi,0))
        Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=2.5, N=15, amaxx=None, Nx=None, amaxy=None, Ny=None,
                     seq=seq, postseq=None, delay=0, saveas=None, bgcor=False, extra_info=ef_info)
        Qfun.measure()
    bla


if 0: # Cavity kerr calibration?
    from scripts.single_cavity import cavdisp
    for delay in [0, 200, 400, 600, 800, 1000]:
        seq = sequencer.Join([sequencer.Trigger(250), cB(1.5, 0), ge(np.pi, 0)])
        seq.append(sequencer.Delay(delay))
        disp = cavdisp.CavDisp(qubit_info, cavity_infoB, 2.5, 150, 0, seq=seq,
                               delay=0, bgcor=False, update=False, generate=True,
    #                           Qswitch_infoA=Qswitch_infoB, Qswitch_infoB=Qswitch_infoB,
    #                           extra_info=[Qswitch_infoA, Qswitch_infoB,],
                              )
        disp.measure()
    bla
