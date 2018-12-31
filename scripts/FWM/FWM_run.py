import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
#matplotlib.rcParams['backend'] = 'Qt4Agg'
#matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
#from t1t2_plotting import smart_T1_delays
import os
import time
import math

#os.chdir(r'C:/qrlab/scripts')
dig = mclient.instruments['dig']

qubit_info = mclient.get_qubit_info('qubit1ge')
#ef_info = mclient.get_qubit_info('qubit1ef')
#cavity_infoR = mclient.get_qubit_info('cavity1R')
cavity_infoA = mclient.get_qubit_info('cavityAlice')
cavity_infoB = mclient.get_qubit_info('cavityBob')
fwm_info1 = mclient.get_qubit_info('fwm_info1')
#fwm_info2 = mclient.get_qubit_info('fwm_info2')
#Qswitch_info1A = mclient.get_qubit_info('Qswitch1A')
#Qswitch_info1B = mclient.get_qubit_info('Qswitch1B')

#qubit_info2 = mclient.get_qubit_info('qDblCoax2')
#ef_info2 = mclient.get_qubit_info('eDblCoax2')
#cavity_info2A = mclient.get_qubit_info('cavity2A')
#cavity_info2B = mclient.get_qubit_info('cavity2B')

cA = cavity_infoA.rotate
#cB = cavity_infoB.rotate
ge = qubit_info.rotate
ges= qubit_info.rotate_selective
#ef = ef_info.rotate
#efs= ef_info.rotate_selective
#efpi = sequencer.Sequence(ef_info.rotate(np.pi, 0))



if 0: # q func test
    from scripts.single_cavity import Qfunction
    Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=1, N=10, amaxx=None, Nx=None, amaxy=None, Ny=None,
                 seq=None, delay=0, saveas=None, bgcor=False)
    Qfun.measure_keysight()

if 1: # fwm spec
    import FWM_spec
    fwm_gen = mclient.instruments['fwmgen']
    target = 5042e6 + 240e6 - 9e6#5.219e9
    df = 3e6
    for power in [.01]:
        spec = FWM_spec.FWM_spec(qubit_info, cavity_infoA, fwm_info1, fwm_gen, 1.5, 
                                 200e3, np.linspace(target-df, target+df, 61), power, 
                                 '4m1', plot_seqs=False, bgcor=False)
        spec.measure()

if 0: # abt mixing
    os.chdir(r'C:/qrlab/scripts/FWM/')
    import FWM_abt
    xvec = np.linspace(-1, 1, 3)
#    abt = FWM_abt.FWM_abt(qubit_info, cavity_infoA, cavity_infoB, fwm_info, 100, 
#                          np.linspace(-1, 1, 10), np.linspace(-1, 1, 10), seq=None,
#                          generate=True, plot_seqs = True)
    abt = FWM_abt.FWM_abt(qubit_info, cavity_infoA, cavity_infoB, fwm_info, 
                          xvec, xvec, 0, which_cavity = 'b', seq=None, saveas=None, 
                          plot_seqs=True, generate = True)
    abt.measure_keysight()



