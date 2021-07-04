'''
Reading data from ssb spec HDF5 file to fit lorentzian cruves to get cavity 
temperatures. Requires the path information to be filled out. Also requires
the min_x and max_x to be specified for the lorentaizn peak you want to fit.
Take amplitude values to calculate the temp.

Jeff Gertler
'''



import os
import time
if 0:
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

from pulseseq import sequencer, pulselib
#from scripts.single_qubit import rabi
from scripts.single_qubit import ssbspec
    
import mclient
from mclient import instruments

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
import lmfit


def lorentzian(params, x, data):
    est = (params['offset'].value + params['amplitude'].value / np.pi * params['sigma'].value 
                / ((x - params['center'].value)**2 + params['sigma'].value**2))
    return data - est




''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = '20190204 Cooldown_from_computer_6.hdf5'
#hdf5_name = '20190204 Cooldown.hdf5'
date = '20190320'
time = '172552'
#time = '143054'

experiment = 'SSBSpec'

''' Primary x axis and secondary if 2d'''
x_key = 'detunings'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]
y_keys = list(exp.keys())
print(y_keys)

y_keys.remove(x_key)
#y_keys.remove(x2_key)


    
qubit_info = mclient.get_qubit_info('qubit1ge')
#ef_info = mclient.get_qubit_info('qubit1ef')
#qubit2_info = mclient.get_qubit_info('qubit2tone')

#cavity_infoR = mclient.get_qubit_info('cavity1R')
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#cavity_infoB = mclient.get_qubit_info('cavityBob')

#toload = ['qubit1ge', 'readout']
#mclient.load_settings_from_file(filepath + 'settings/' + date + '/' + time + '.set', toload)    # Last time-Rabi callibration

#qubits = mclient.get_qubits()
#qubit_info = mclient.get_qubit_info('qubit1ge')
spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
                                   np.linspace(-11e6, -9.6e6, 51), 
                                   np.linspace(-2e6, -1e6, 50), 
                                   np.linspace(-1e6, 1e6, 50),
                                   )), 
                       seq=None, plot_seqs=False, keep_data=False)

    
#spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
#                                   np.linspace(-5.0e6, -3.4e6, 51), 
#                                   np.linspace(-1.8e6, -0.9e6, 50), 
#                                   np.linspace(-.5e6, .5e6, 50),
#                                   )), 
#                       seq=None, plot_seqs=False)
spec.detunings = -1* exp[x_key].value
data = exp['avg_pp'].value
spec.avg_data = exp['avg_pp']
spec.analyze(data = data)
fig = spec.fig

xs = -1*spec.detunings /1e6
ys = data

# alice peak
#min_x = -5
#max_x = -3

#qubit peak
min_x = -2
max_x = -.4

mask = [(xs>min_x) & (xs<max_x)]
xs = xs[mask]
ys = ys[mask]

params = lmfit.Parameters()
#params.add('offset', value=np.max(ys))
# if offset needs to be forced to match previous value
params.add('offset', value=14.97, vary=False) 
params.add('amplitude', value=-1)
params.add('center', value=(min_x + max_x)/2, min = min_x, max = max_x)
#params.add('center', value=0, vary=False)
params.add('sigma', value=max_x-min_x, min = 0)


result = lmfit.minimize(lorentzian, params, args=(xs, ys))
lmfit.report_fit(result.params)
    
pl.plot(xs, -lorentzian(result.params, xs, np.zeros(len(xs))))

print(('real amp', result.params['amplitude']/(result.params['sigma'] * np.pi)))

pl.show()

