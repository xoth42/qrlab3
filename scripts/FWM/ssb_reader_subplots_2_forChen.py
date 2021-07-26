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
#hdf5_name='\April9Fluxonium.hdf5'

if 0:
    date = '20190711'
experiment = 'SSBSpec'

''' Primary x axis and secondary if 2d'''
x_key = 'gates'
#x2_key = 'powers'
t_list=['165236']
#t_list=['210134']
f = h5.File(filepath + hdf5_name, 'r')
qubit_info = mclient.get_qubit_info('qubit1ge')




fig, ax=pl.subplots(1,1, sharex='col',sharey='row', figsize=(16.18,10))
#pl.figure(figsize=(3,4))
#ratio_as = 0.1

# below is just for 0625 single plot

# for June 06th   X=2.15 fre_offset=-0.18e6
#time='171908'
#time='172240'
#time='172616'

# for June 12th   X=2.02 fre_offset=-0.18e6
date='20190612'
time='134700'
#time='140412'
#time='142128'

date='20190618'   #X=2.1 fre_offset=-0.0e6
#time='130103'   # 10e3 sec
#time='110744'   # 20e3 sec 
#time='114131'   # 40e3 sec

date='20190620'   #X=2.055 fre_offset=-0.0e6
#time='215845'   # 150e3 sec

date='20190622'   #X=2.08 fre_offset=-0.0e6 points 101
time='195059'   # 20e3 sec
time='194218'   # 30e3 sec
time='194546'   # 40e3 sec

date='20190625'   #X=2.08 fre_offset=0.28e6 points 121
time='213335'   # amp 0.6 
#time='213712'   # .7 
#time='214049'   # 0.8

date='20190703'   #X=6 fre_offset=-0.02e6 points 106
time='120013'   # 6 usec 
time='121054'   # 9 usec 
time='122135'   # 12 usec


fre_offset=-0.02e6

#exp = f['/' + '20190711' + '/' + '165236' + '_' + experiment]  this is for chen
exp = f['/' + date + '/' + time + '_' + experiment]
aaa=date +'_'+ time + '_' + experiment
#    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-15e6-fre_offset, 1e6-fre_offset, 101), seq=None, plot_seqs=False, proj_func='phase', keep_data = False)
#spec = ssbspec.SSBSpec(qubit_info, np.linspace(-19e6-fre_offset, 1e6-fre_offset, 121), seq=None, plot_seqs=False, proj_func='phase', keep_data = False)
spec = ssbspec.SSBSpec(qubit_info, np.linspace(-20e6-fre_offset, 1e6-fre_offset, 106), seq=None, plot_seqs=False, proj_func='phase', keep_data = False)
data = exp['avg_pp'].value
spec.avg_data = exp['avg_pp']
spec.analyze(data = data)
#fig = spec.fig
size_label=30
ax.plot(spec.xs, -spec.get_ys(), color='blue', linewidth=2.0)
ax.grid(which='major', axis='x', linestyle='--', linewidth=2,)
X_qa=4
X_qb=2
X_qc=X_qa+X_qb

#pl.setp(ax, xticks=[-18, -12, -6, 0], xticklabels=['-18', '-12', '-6', '0'], )
#pl.setp(ax, xticks=[-4*X_qc, -2*X_qc, 0], xticklabels=['4', '2', '0'], )
#pl.setp(ax, xticks=[-8*X_qc, -6*X_qc, -4*X_qc, -2*X_qc, 0], xticklabels=['8', '6', '4', '2', '0'], )
pl.setp(ax, xticks=[-2*X_qc, -1*X_qc, 0], xticklabels=['4', '2', '0'], )
pl.setp(ax, yticks=[])
ax2=ax.twiny()
ax2.set_xlim(ax.get_xlim())
#ax2.set_xticks([-4, -2])
#ax2.set_xticks([-7*X_qc, -5*X_qc, -3*X_qc, -1*X_qc])
ax2.set_xticks([-1*X_qa, -1*X_qb])
ax2.set_xticklabels(['', ''])
ax2.grid(which='major', axis='x', linestyle='--', linewidth=3,)
ax.set_ylabel('P(n)', fontsize=size_label)
#ax.set_xlabel('Detuning (MHz)', fontsize=size_label)
ax.set_xlabel('photon number', fontsize=size_label)

ax.tick_params(axis='both', which='major', labelsize=size_label)
ax.tick_params(axis='both', which='minor', labelsize=size_label)

#################



fig.savefig(str(aaa), dpi=600)

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