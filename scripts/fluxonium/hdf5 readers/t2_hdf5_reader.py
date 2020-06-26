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
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)


import mclient
from mclient import instruments

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json

from scripts.single_qubit import T2measurement



''' Path to the .hdf5 file '''
filepath = 'C:\Users\Wang_Lab\Desktop\hdf5_copies'
hdf5_name = '\April9Fluxonium_2julycopy.hdf5'
#hdf5_name = '20190204 Cooldown.hdf5'
date = '20190528'
time = '045702'
#time = '143054'

experiment = 'T2Measurement'

''' Primary x axis and secondary if 2d'''
x_key = 'gates'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]






qubit_info = mclient.get_qubit_info('qubit1ge')


t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 5e3, 101), detune=2e6, double_freq=False, generate=True, 
                                         seq=None, extra_info=ef_info, postseq=None, proj_func='phase', keep_data=False)



data = exp['avg_pp'].value
t2.avg_data = exp['avg_pp']
t2.analyze(data = data)
fig = t2.fig
t2_result.append(t2.fit_params['tau'].value)
t2_err.append(t2.fit_params['tau'].stderr)
t2_ofs.append(t2.fit_params['ofs'].value)


pl.show()
plt.close()



ys = data
print(ys)




pl.show()
#t2_result =[]
#t2_err=[]
#t2_amp = []
#t2_ofs=[]


