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
    os.system(r'C:\qrlab\start.bat')
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

if 0:        #06/21
    date = '20190621'
    #time = '105122'   #  points
    #time = '105423'
    #time='105725'
    #time='110054'
    #time='152524'
    #time='172745'
    #time='135134'

if 1:        #06/22     
    date = '20190622'
    #time = '195059'   # 101 points
    #time = '194218'  # 101 points
    #time='194546'  # 101 points
    #time='195843'
    #time='193956'
if 0:       #06/23
    date = '20190623'
    time = '073033'   # 101 points

if 0:
    #06/23
    date = '20190623'
    time = '073033'   # 101 points

if 0:
    #06/25  ab
    date = '20190625'
    #time = '213335'   # 101 points
    #time = '213712'
    #time = '214049'

if 0:
    #06/26  a2b2
    date = '20190626'
    #time = '113340'   # 101 points
    #time = '113710'
    #time = '114041'
    #time = '114415'   # 201 points 
    #time = '120252'    # not agree with one note figure

    time = '133214'     # 251 points

experiment = 'SSBSpec'

''' Primary x axis and secondary if 2d'''
x_key = 'gates'
#x2_key = 'powers'
t_list=['195059','194218','194546']
f = h5.File(filepath + hdf5_name, 'r')
qubit_info = mclient.get_qubit_info('qubit1ge')

fre_offset=0e6


fig, ax=pl.subplots(1,3, sharex='col',sharey='row')

ratio_as = 5
for iii in range(1):
    exp = f['/' + date + '/' + t_list[iii] + '_' + experiment]
    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-15e6-fre_offset, 1e6-fre_offset, 101), seq=None, plot_seqs=False, proj_func='phase', keep_data = False)
    data = exp['avg_pp'].value
    spec.avg_data = exp['avg_pp']
    spec.analyze(data = data)
    #fig = spec.fig
    size_label=20
    ax[iii].plot(spec.xs, spec.get_ys(), color='blue', linewidth=2.0)
    ax[iii].grid(which='major', axis='x', linestyle='--', linewidth=2,)
    pl.setp(ax[iii], xticks=[-15, -10, -5, 0], xticklabels=['3', '2', '1', '0'], )
    pl.setp(ax[iii], yticks=[])
    if iii==0:
        ax[iii].set_ylabel('P(n)', fontsize=size_label)
    ax[iii].tick_params(axis='both', which='major', labelsize=size_label)
    ax[iii].tick_params(axis='both', which='minor', labelsize=size_label)

#    xleft, xright = ax[iii].get_xlim()
#    ybottom, ytop = ax[iii].get_ylim()
    # the abs method is used to make sure that all numbers are positive
    # because x and y axis of an axes maybe inversed.
#    ax[iii].set_aspect(ratio_as)


'''








#pl.axes().set_aspect('1')
#
#ys = data
#center = spec.center
#frequency_corrections.append(center)
#
#print(ys)
#print(center)
#pl.show()
'''