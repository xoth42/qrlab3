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
Reading data from ssb spec HDF5 file

Juliang Li
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

from scripts.single_qubit import ssbspec


''' Path to the .hdf5 file '''
filepath = 'C:\\Users\wanglab\Desktop\hdf_tomo_copy'
hdf5_name = '\June19PumpCat.hdf5'

if 1:        #07/11
    date = '20190711'

#    time = '165236'     # 121 points

experiment = 'SSBSpec'

''' Primary x axis and secondary if 2d'''
x_key = 'gates'
#x2_key = 'powers'
t_list=['165236']
xxx=list(range(1))
y_array=np.zeros([1, 121])
for jjj in xxx:

    f = h5.File(filepath + hdf5_name, 'r')
    exp = f['/' + date + '/' + t_list[jjj] + '_' + experiment]
    
    qubit_info = mclient.get_qubit_info('qubit1ge')
    
    fre_offset=0.0e6
    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-19e6-fre_offset, 1e6-fre_offset, 121), seq=None, plot_seqs=False, proj_func='phase', keep_data = False)
    
    data = exp['avg_pp'].value
    spec.avg_data = exp['avg_pp']
#    spec.analyze(data = -data)
    mmm=list(range(121))
#    for nnn in mmm:
#        y_array[jjj][mmm]=data[mmm]
   
#pl.show()

#pl.close()




ax=pl.plot(spec.xs, -spec.get_ys(), linewidth=2.0, color='blue')
#pl.xlabel()
pl.ylabel('P(n)')


size_label=20
#pl.rc('font', size=10)
pl.rc('axes', titlesize=size_label)
pl.rc('axes', labelsize=size_label)
pl.rc('xtick', labelsize=size_label)
pl.rc('ytick', labelsize=size_label)
pl.grid(which='major', axis='x', linestyle='--', linewidth=2,)
pl.yticks([])
pl.xticks([-18, -12, -6, 0], ['18', '12', '6', '0'])

    
ax2=ax.twiny()
ax2.set_xlim(ax.get_xlim())
ax2.set_xticks([-10.75, -6.45, -2.15])
ax2.set_xticklabels(['5', '3', '1'])
ax2.grid(which='major', axis='x', linestyle='--', linewidth=1,)