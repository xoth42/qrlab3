import os
import time
if 0:
    os.system(r'C:\qrlab-3\start.bat')
    time.sleep(1)

from pulseseq import sequencer, pulselib
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
hdf5_name = '190821CD-DblCavity.hdf5'
date = '20191013'
time = '094558'
experiment = 'WignerFunction'

''' Primary x axis and secondary if 2d'''
x_key = 'displacements'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]
y_keys = list(exp.keys())
print(y_keys)

y_keys.remove(x_key)
#y_keys.remove(x2_key)


qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
#qubit2_info = mclient.get_qubit_info('qubit2tone')

#cavity_infoR = mclient.get_qubit_info('cavity1R')
cavity_infoA = mclient.get_qubit_info('cavityA')
#cavity_infoB = mclient.get_qubit_info('cavityBob')

#toload = ['qubit1ge', 'readout']
#mclient.load_settings_from_file(filepath + 'settings/' + date + '/' + time + '.set', toload)    # Last time-Rabi callibration

#qubits = mclient.get_qubits()
#qubit_info = mclient.get_qubit_info('qubit1ge')

tr = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoA, 
                                   xs = np.linspace(-2.0,2.0,17), ys = np.linspace(-2.0,2.0,17),
                                   t_ge=356, t_gf=0,
                                   seq=None, delay=5, bgcor=True, zmax=100, zmin=-100, 
                                   saveas=None)
tr.displacements = exp[x_key].value
data = exp['avg_pp'].value
data = exp['avg_pp'].value[::2] - exp['avg_pp'].value[1::2]
#data /= 80
tr.avg_data = exp['avg']
tr.analyze(data = data)

pl.show()

