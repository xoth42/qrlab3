import os
import time
if 0:
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

from pulseseq import sequencer, pulselib
from scripts.single_qubit import rabi
    
import mclient
from mclient import instruments

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json


''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = 'LabTransmonOct8.hdf5'
date = '20181231'
time = '071234'
experiment = 'WignerFunction'

''' Primary x axis and secondary if 2d'''
#x_key = 'amps'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]
y_keys = exp.keys()
print(y_keys)

y_keys.remove(x_key)
#y_keys.remove(x2_key)


    
qubit1ge = instruments.create('qubit1ge', 'Qubit_Info')
readout = instruments.create('readout', 'Readout_Info')
toload = ['qubit1ge', 'readout']
mclient.load_settings_from_file(filepath + 'settings/' + date + '/' + time + '.set', toload)    # Last time-Rabi callibration

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
    
tr = rabi.Rabi(qubit_info, exp[x_key].value, plot_seqs=False, generate=False, selective=False, repeat_pulse=1, update=False)
tr.avg_data = exp['avg']
tr.analyze(data = exp['avg'])

    
pl.show()

