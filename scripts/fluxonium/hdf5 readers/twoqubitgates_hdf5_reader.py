# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 19:52:53 2019

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

from scripts.fluxonium import single_rotation_forboth



''' Path to the .hdf5 file '''
filepath = 'C:\Users\wanglab\Desktop\hdf5_copies'
hdf5_name = '\TunableTransmonJune19.hdf5'
#hdf5_name = '20190204 Cooldown.hdf5'
date = '20200217'
time = '162920'
#time = '143054'

experiment = 'Single_Rotation_forboth'

''' Primary x axis and secondary if 2d'''
x_key = 'gates'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]






qubit_info = mclient.get_qubit_info('qubit1ge')
qubit_info2 = mclient.get_qubit_info('qubit1ge_2')
qubit2_info = mclient.get_qubit_info('qubit2ge')
qubit2_info2 = mclient.get_qubit_info('qubit2ge_2')




sr = single_rotation_forboth.Single_Rotation_forboth(qubit_info, qubit_info2, qubit2_info, qubit2_info2, seq=None, plot_seqs=True, generate=True, proj_func='phase')  #seq=seq was added



data = exp['avg_pp'].value
sr.avg_data = exp['avg_pp']
sr.analyze(data = data)
fig = sr.fig





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
print(ys)
xs = np.linspace(0,35,35)
pl.scatter(xs, ys, marker = '.', color='r')
pl.plot(xs,ys)

#averages
y_ground = np.zeros(5)
for i in range(5): y_ground[i] = (ys[0] +ys[1] + ys[2] + ys[3] + ys[4])/5
x_ground = np.linspace(0,4,5)

y_red = np.zeros(5)
for i in range(5): y_red[i] = (ys[5] +ys[6] + ys[7] + ys[8] + ys[9])/5
x_red = np.linspace(5,9,5)

y_yellow = np.zeros(5)
for i in range(5): y_yellow[i] = (ys[10] +ys[11] + ys[12] + ys[13] + ys[14])/5
x_yellow = np.linspace(10,14,5)

y_gaius = np.zeros(5)
for i in range(5): y_gaius[i] = (ys[15] +ys[16] + ys[17] + ys[18] + ys[19])/5
x_gaius = np.linspace(15,19,5) 


y_green = np.zeros(5)
for i in range(5): y_green[i] = (ys[20] +ys[21] + ys[22] + ys[23] + ys[24])/5
x_green = np.linspace(20,25,5)

y_blue = np.zeros(5)
for i in range(5): y_blue[i] = (ys[25] +ys[26] + ys[27] + ys[28] + ys[29])/5
x_blue = np.linspace(26,30,5)

y_octavius = np.zeros(5)
for i in range(5): y_octavius[i] = (ys[30] +ys[31] + ys[32] + ys[33] + ys[34])/5
x_octavius = np.linspace(31,35,5) 


pl.plot(x_ground, y_ground, color='black', linestyle='--')
pl.plot(x_red, y_red, color='black', linestyle='--')
pl.plot(x_yellow, y_yellow, color='black', linestyle='--')
pl.plot(x_gaius, y_gaius, color='black', linestyle='--')
pl.plot(x_green, y_green, color='black', linestyle='--')
pl.plot(x_blue, y_blue, color='black', linestyle='--')
pl.plot(x_octavius, y_octavius, color='black', linestyle='--')
pl.show()

print(y_ground[0])  
print(y_red[0])
print(y_yellow[0])
print(y_gaius[0])
print(y_green[0])
print(y_blue[0])
print(y_octavius[0])






print('contrasts')
print(y_ground[0]-y_ground[0])  
print(y_red[0]-y_ground[0])
print(y_yellow[0]-y_ground[0])
print(y_gaius[0]-y_ground[0])
print(y_green[0]-y_ground[0])
print(y_blue[0]-y_ground[0])
print(y_octavius[0]-y_ground[0])
