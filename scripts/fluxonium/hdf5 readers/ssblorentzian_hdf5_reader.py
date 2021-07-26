# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 19:52:17 2019

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Sun May 19 23:34:46 2019

@author: Wang_Lab
"""

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
    os.system(r'C:\qrlab-3\start.bat')
    time.sleep(1)


import mclient
from mclient import instruments

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json

from scripts.single_qubit import ssbspec_lorentzianfit


''' Path to the .hdf5 file '''
filepath = 'C:\Users\Wang_Lab\Desktop\hdf5_copies'
hdf5_name = '\April9Fluxonium_2julycopy.hdf5'
#hdf5_name = '20190204 Cooldown.hdf5'
date = '20190524'
time = '014907'
#time = '143054'

experiment = 'SSBSpec_lorentzianfit'

''' Primary x axis and secondary if 2d'''
x_key = 'gates'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]






qubit_info = mclient.get_qubit_info('qubit1ge')



spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-15e6, 15e6, 141), seq=None, plot_seqs=False, proj_func='phase', keep_data = False)


data = exp['avg_pp'].value
spec.avg_data = exp['avg_pp']
spec.analyze(data = data)
fig = spec.fig


pl.show()
plt.close()



#t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
#                                     np.concatenate((np.linspace(0,0,50), np.linspace(0.1e3, 1.9e3, 31), np.linspace(2e3, 20e3, 56), np.linspace(20.1e3, 450e3, 60))), 
#                                     double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None) 
#t1.measure_keysight()
#
#t1_result.append(t1.fit_params['tau'].value)
#t1_err.append(t1.fit_params['tau'].stderr)
#t1_ofs.append(t1.fit_params['ofs'].value)
#t1_ofs_err.append(t1.fit_params['ofs'].stderr)
#t1_amp.append(t1.fit_params['amplitude'].value)
#t1_amp_err.append(t1.fit_params['amplitude'].stderr)
#t1_amp2.append(t1.fit_params['amplitude2'].value)
#t1_amp2_err.append(t1.fit_params['amplitude2'].stderr)
#t1_result2.append(t1.fit_params['tau2'].value)
#t1_err2.append(t1.fit_params['tau2'].stderr)
#T1_Ypoints.append(t1.get_ys())

ys = data
center = spec.center
frequency_corrections.append(center)

print(ys)
print(center)






pl.show()
