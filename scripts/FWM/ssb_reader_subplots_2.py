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
#hdf5_name='\April9Fluxonium.hdf5'

if 0:
    date = '20190611'
#    time = '161741'

if 0:        #06/21
    date = '20190621'
    #time = '105122'   #  points
    #time = '105423'
    #time='105725'
    #time='110054'
    #time='152524'
    #time='172745'
    #time='135134'

if 1:        #06/22       yes
    date = '20190622'
    #time = '195059'   # 101 points    -14 to 1 MHz
    #time='194546'  # 101 points

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
    #time = '133214'     # 251 points

if 0:        # yes
    date = '20190625'   # 201 points  -14 to 1 MHz
    #time = '210134'
experiment = 'SSBSpec'

''' Primary x axis and secondary if 2d'''
x_key = 'gates'
#x2_key = 'powers'
t_list=['195059', '194546']
#t_list=['210134']
f = h5.File(filepath + hdf5_name, 'r')
qubit_info = mclient.get_qubit_info('qubit1ge')




fig, ax=pl.subplots(1,3, sharex='col',sharey='row', figsize=(18.4665,4))
#pl.figure(figsize=(3,4))
ratio_as = 5

# below is just for 0625 single plot
fre_offset=0.1e6
exp = f['/' + '20190625' + '/' + '210134' + '_' + experiment]
#    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-15e6-fre_offset, 1e6-fre_offset, 101), seq=None, plot_seqs=False, proj_func='phase', keep_data = False)
spec = ssbspec.SSBSpec(qubit_info, np.linspace(-14e6-fre_offset, 1e6-fre_offset, 201), seq=None, plot_seqs=False, proj_func='phase', keep_data = False)
data = exp['avg_pp'].value
spec.avg_data = exp['avg_pp']
spec.analyze(data = data)
#fig = spec.fig
size_label=24
ax[0].plot(spec.xs, -spec.get_ys()*0.75-10, color='blue', linewidth=2.0)
ax[0].grid(which='major', axis='x', linestyle='--', linewidth=2,)
pl.setp(ax[0], xticks=[-13.2, -8.8, -4.4, 0], xticklabels=['6', '4', '2', '0'], )
pl.setp(ax[0], yticks=[])
ax2=ax[0].twiny()
ax2.set_xlim(ax[0].get_xlim())
ax2.set_xticks([-11, -6.6, -2.2])
ax2.set_xticklabels(['5', '3', '1'])
ax2.grid(which='major', axis='x', linestyle='--', linewidth=1,)
ax[0].set_ylabel('P(n)', fontsize=size_label)
ax[0].tick_params(axis='both', which='major', labelsize=size_label)
ax[0].tick_params(axis='both', which='minor', labelsize=size_label)

#################

fre_offset=0e6
for iii in range(2):
    exp = f['/' + date + '/' + t_list[iii] + '_' + experiment]
#    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-15e6-fre_offset, 1e6-fre_offset, 101), seq=None, plot_seqs=False, proj_func='phase', keep_data = False)
    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-14e6-fre_offset, 1e6-fre_offset, 101), seq=None, plot_seqs=False, proj_func='phase', keep_data = False)
    data = exp['avg_pp'].value
    spec.avg_data = exp['avg_pp']
    spec.analyze(data = data)
    #fig = spec.fig
    size_label=20
    ax[iii+1].plot(spec.xs, -spec.get_ys(), color='blue', linewidth=2.0)
    ax[iii+1].grid(which='major', axis='x', linestyle='--', linewidth=2,)
    pl.setp(ax[iii+1], xticks=[-12.8, -8.2, -4.3, 0], xticklabels=['6', '4', '2', '0'], )
    pl.setp(ax[iii+1], yticks=[])
    ax2=ax[iii+1].twiny()
    ax2.set_xlim(ax[iii+1].get_xlim())
    ax2.set_xticks([-10.75, -6.45, -2.15])
    ax2.set_xticklabels(['5', '3', '1'])
    ax2.grid(which='major', axis='x', linestyle='--', linewidth=1,)
   
    if iii==0:
#        ax[iii].set_ylabel('P(n)', fontsize=size_label)
        ax[iii+1].tick_params(axis='both', which='major', labelsize=size_label)
        ax[iii+1].tick_params(axis='both', which='minor', labelsize=size_label)

#    xleft, xright = ax[iii].get_xlim()
#    ybottom, ytop = ax[iii].get_ylim()
    # the abs method is used to make sure that all numbers are positive
    # because x and y axis of an axes maybe inversed.
#    ax[iii].set_aspect(ratio_as)
fig.savefig('ssb_3.png', dpi=600)

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