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
geqs= qubit_info.rotate_quasilective
ef = ef_info.rotate
efs= ef_info.rotate_selective
efpi = sequencer.Sequence(ef_info.rotate(np.pi, 0))

from single_cavity import cavT1
from single_cavity import cavT2

t1xs = np.concatenate((np.linspace(0e3, 20e3, 21), np.linspace(24e3, 220e3, 51), np.linspace(230e3, 1800e3, 41)))
t2xs = np.linspace(0e3, 300e3, 121)
detune = 50e3

t1arraya = []
t1arrayb = []
t2arraya = []
t2arrayb = []


#for j in range (3):
##for i in range(3): # Cavity T1 for Alice    
#    t1 = cavT1.CavT1(qubit_info, cavity_infoA, 0.9, t1xs,
#                     proj_num=0, seq=None, postseq=None, bgcor=False, extra_info=[ef_info,])
#    t1.measure_keysight()
#    t1ya = t1.get_ys()
#    t1arraya.append(t1ya)
#    
##for i in range(3): # Cavity T1 for Bob    
#    t1 = cavT1.CavT1(qubit_info, cavity_infoB, 0.9, t1xs,
#                     proj_num=0, seq=None, postseq=None, bgcor=False, extra_info=[ef_info,])
#    t1.measure_keysight()
#    t1yb = t1.get_ys()
#    t1arrayb.append(t1yb)
    
if 0:# Cavity T2 for Alice    
    ct2b = cavT2.CavT2(qubit_info, cavity_infoA, 0.7, t2xs, detune=detune, seq=None,
                       postseq=None, bgcor=False, extra_info=[qubit_info,])
    ct2b.measure_keysight()
    t2ya = ct2b.get_ys()
    t2arraya.append(t2ya)

if 1:# Cavity T2 for Bob
    ct2b = cavT2.CavT2(qubit_info, cavity_infoB, 0.7, t2xs, detune=detune, seq=None,
                       postseq=None, bgcor=False, extra_info=[qubit_info,])
    ct2b.measure_keysight()
    t2yb = ct2b.get_ys()
    t2arrayb.append(t2yb)

