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
This will get separate figure for each plot. 
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
#hdf5_name = '\June19PumpCat.hdf5'
hdf5_name = '\April9Fluxonium.hdf5'
if 1:        # 06/06
    date= '20190606'
#    t_list=['171908', '172240', '172616'],   102 data points -10 to 1 MHz
if 0:        #06/21
    date = '20190621'
    #time = '105122'   #  points
    #time = '105423'
    #time='105725'
    #time='110054'
    #time='152524'
    #time='172745'
    #time='135134'

if 0:        #06/22     
    date = '20190622'
    #time = '195059'   # 101 points
    #time = '194218'  # 101 points
    #time='194546'  # 101 points
    #time='195843'

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
#t_list=['195059','194218','194546']
t_list=['171908', '172240', '172616']
xxx=list(range(3))
y_array=np.zeros([3, 101])
fig, ax=pl.subplots(1, 1)
for jjj in xxx:

    f = h5.File(filepath + hdf5_name, 'r')
    exp = f['/' + date + '/' + t_list[jjj] + '_' + experiment]
    
    qubit_info = mclient.get_qubit_info('qubit1ge')
    
    fre_offset=-0.18e6
    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-10e6-fre_offset, 1e6-fre_offset, 102), seq=None, plot_seqs=False, proj_func='phase', keep_data = False)
    
    data = exp['avg_pp'].value
    spec.avg_data = exp['avg_pp']
#    spec.analyze(data = data)
    mmm=list(range(101))
    for nnn in mmm:
        y_array[jjj][mmm]=data[mmm]
   

#    pl.close()
    
#    pl.figure(jjj)
    pl.figure()

#    ax.plot(spec.xs, -spec.get_ys(), linewidth=2.0, color='blue')
    #pl.xlabel()
#    pl.ylabel('P(n)')
    pl.show
    
    size_label=20
#    #pl.rc('font', size=10)
#    pl.rc('axes', titlesize=size_label)
#    pl.rc('axes', labelsize=size_label)
#    pl.rc('xtick', labelsize=size_label)
#    pl.rc('ytick', labelsize=size_label)
#    pl.grid(which='major', axis='x', linestyle='--', linewidth=2,)
#    pl.yticks([])
    X_qc=2.15
#    pl.xticks([-4*X_qc, -2*X_qc, 0], ['4', '2', '0'])
    size_label=24
    ax.plot(spec.xs, -spec.get_ys(), color='blue', linewidth=2.0)
    ax.grid(which='major', axis='x', linestyle='--', linewidth=2,)
    pl.setp(ax, xticks=[-4*X_qc, -2*X_qc, 0], xticklabels=['4', '2', '0'], )
    pl.setp(ax, yticks=[])
    ax2=ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks([-2])
    ax2.set_xticklabels(['1'])
    ax2.grid(which='major', axis='x', linestyle='--', linewidth=1,)
    ax.set_ylabel('P(n)', fontsize=size_label)
    ax.set_xlabel('Photon number', fontsize=size_label)
    
    ax.tick_params(axis='both', which='major', labelsize=size_label)
    ax.tick_params(axis='both', which='minor', labelsize=size_label)

 #pl.xticks([-15, -10, -5, 0], ['3', '2', '1', '0'])
#pl.axes().set_aspect('1')
#
#ys = data
#center = spec.center
#frequency_corrections.append(center)
#
#print(ys)
#print(center)
#pl.show()
