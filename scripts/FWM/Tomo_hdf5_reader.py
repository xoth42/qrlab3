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
Reading data from cat pump Wigner HDF5 file. Has the ability to stitch multi runs into a square plot.

Juliang Li
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

from scripts.single_cavity import WignerbyParity



''' Path to the .hdf5 file '''
filepath = 'C:\\Users\wanglab\Desktop\hdf_tomo_copy'
hdf5_name = '\June19PumpCat.hdf5'
date = '20190623'
#time = '110154'

qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info=mclient.get_qubit_info('qubit1ef')
cavity_infoB=mclient.get_qubit_info('cavityBob')

x_range = 0.5
x_start=-2.4

x_row=25
y_col=6

data_all= np.zeros([x_row*8, y_col*8])
 

t_list=['090107', '094123', '102139', '110154', '114210', '122226', '130242', '14258']
time = t_list[4]
experiment = 'WignerFunction'

''' Primary x axis and secondary if 2d'''
x_key = 'gates'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]


Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoB, t_ge=210, t_gf=0,
                                     xs = np.linspace(x_start, x_start+x_range, 6), ys = np.linspace(-1.2, 1.2, 25),
                                     seq=None, delay=0, saveas=None, bgcor=True, zmax=29, zmin=-29, cav_switch=None,
                                     ) 


data = exp['avg_pp'].value


x_index=list(range(x_row))
y_index=list(range(y_col))

data_2D = np.zeros([x_row,y_col])

for iii in x_index:
    for jjj in y_index:
        
        data_2D[iii][jjj]=data[2*y_col*iii+2*jjj]-data[2*y_col*iii+2*jjj+1]


Wfun.analyze(data = data_2D)
fig = Wfun.fig
pl.show()


