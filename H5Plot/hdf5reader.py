import os
import time
if 0:
    os.system(r'C:\qrlab-3\start.bat')
    time.sleep(1)

#from pulseseq import sequencer, pulselib
#from scripts.single_qubit import rabi
from scripts.single_cavity import WignerbyParity
    
import mclient
from mclient import instruments

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json


''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = '0626cooldown_circualtor - Copy.hdf5'
date = '20200818'
time = '132735'
experiment = 'Ramsey_Measurement_mixer'

''' Primary x axis and secondary if 2d'''
x_key = 'delays'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]
#y_keys = exp.keys()
print(y_keys)
x_data = exp[x_key].value

#y_keys.remove(x_key)
y_data = exp['avg_pp'].value



##y_keys.remove(x2_key)
#
#
#qubit_info = mclient.get_qubit_info('qubit1ge')
#ef_info = mclient.get_qubit_info('qubit1ef')
##qubit2_info = mclient.get_qubit_info('qubit2tone')
#
##cavity_infoR = mclient.get_qubit_info('cavity1R')
##cavity_infoA = mclient.get_qubit_info('cavityAlice')
#cavity_infoB = mclient.get_qubit_info('cavityBob')
#
##toload = ['qubit1ge', 'readout']
##mclient.load_settings_from_file(filepath + 'settings/' + date + '/' + time + '.set', toload)    # Last time-Rabi callibration
#
##qubits = mclient.get_qubits()
##qubit_info = mclient.get_qubit_info('qubit1ge')
#    
#tr = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoB, t_ge=300, t_gf=0,
#                                         amax=1.75, N=15, amaxx=None, Nx=None, amaxy=None, Ny=None,
#                                         seq=None, delay=5, saveas=None, bgcor=False)
#tr.displacements = exp[x_key].value
#data = exp['avg_pp'].value
##data = exp['avg_pp'].value[::2] - exp['avg_pp'].value[1::2]
##data /= 80
#tr.avg_data = exp['avg']
#tr.analyze(data = data)
#
#    
#pl.show()

