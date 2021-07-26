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
    os.system(r'C:\qrlab-3\start.bat')
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

data_all= np.zeros([x_row, y_col*8])
 
experiment = 'WignerFunction'

''' Primary x axis and secondary if 2d'''
x_key = 'gates'

t_list=[['024834', '031248', '033702', '040118', '042532', '044946', '051400', '053814'],
         ['233432', '235848', '002303', '004718', '011133', '013548', '020003', '022418'],
         ['142314', '150330', '154346', '162402', '170418', '174433', '182449', '190505'],
         ['090107', '094123', '102139', '110154', '114210', '122226', '130242', '134258'],
         ['060228', '062649', '065109', '071529', '073948', '080408', '082828', '085248'],
         ['201941', '204403', '210824', '213245', '215707', '222128', '224549', '231011']]

'''
t_list=['090107', '094123', '102139', '110154', '114210', '122226', '130242', '134258']  # for dt=37.7
t_list=['142314', '150330', '154346', '162402', '170418', '174433', '182449', '190505']  # for dt=31.45
t_list=['201941', '204403', '210824', '213245', '215707', '222128', '224549', '231011']  # for dt= 88.1e3
t_list=['233432', '235845', '002303', '004718', '011133', '013548', '020003', '022418']  # for dt= 18.9e3
t_list=['024834', '031248', '033702', '040118', '042532', '044946', '051400', '053814']  # for dt= 6.3e3
t_list=['060228', '062649', '065109', '071529', '073948', '080408', '082828', '085248']   # for dt=62.9e3
'''

dt_list=list(range(6))
#fig, ax=pl.subplots(2,3, sharex='col',sharey='row')
for lll in dt_list:

    fig_list=list(range(8))
    
    for kkk in fig_list:
    
        time = t_list[lll][kkk]
    
        f = h5.File(filepath + hdf5_name, 'r')
        exp = f['/' + date + '/' + time + '_' + experiment]
        data = exp['avg_pp'].value
        x_index=list(range(x_row))
        y_index=list(range(y_col))
    
        data_2D = np.zeros([x_row,y_col])
    
        for iii in x_index:
            for jjj in y_index:
                
                data_2D[iii][jjj]=data[2*y_col*iii+2*jjj]-data[2*y_col*iii+2*jjj+1]
                data_all[iii][kkk*y_col+jjj]=(data[2*y_col*iii+2*jjj]-data[2*y_col*iii+2*jjj+1])/29
    
    
    Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoB, t_ge=210, t_gf=0,
                                         xs = np.linspace(-2.4, 2.4, 48), ys = np.linspace(-1.2, 1.2, 25),
                                         seq=None, delay=0, saveas=None, bgcor=True, zmax=29, zmin=-29, cav_switch=None,
                                         ) 
    
    Wfun.analyze(data = data_all)
#    ax[lll].imshow(data_all)
    fig = Wfun.fig
    fig.set_size_inches(7.76,5)

    size_label=24
    #pl.rc('font', size=10)
    pl.rc('axes', titlesize=size_label)
    pl.rc('axes', labelsize=size_label)
    pl.rc('xtick', labelsize=size_label)
    pl.rc('ytick', labelsize=size_label)
    pl.axes().set_aspect('1')

    fig.savefig('tomo_5'+str(lll), dpi=600)



dt_list=list(range(6))
#fig, ax=pl.subplots(2,3, sharex='col',sharey='row')
for lll in dt_list:

    fig_list=list(range(8))
    
    for kkk in fig_list:
    
        time = t_list[lll][kkk]
    
        f = h5.File(filepath + hdf5_name, 'r')
        exp = f['/' + date + '/' + time + '_' + experiment]
        data = exp['avg_pp'].value
        x_index=list(range(x_row))
        y_index=list(range(y_col))
    
        data_2D = np.zeros([x_row,y_col])
    
        for iii in x_index:
            for jjj in y_index:
                
                data_2D[iii][jjj]=data[2*y_col*iii+2*jjj]-data[2*y_col*iii+2*jjj+1]
                data_all[iii][kkk*y_col+jjj]=(data[2*y_col*iii+2*jjj]-data[2*y_col*iii+2*jjj+1])/29
    
    
    Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoB, t_ge=210, t_gf=0,
                                         xs = np.linspace(-2.4, 2.4, 48), ys = np.linspace(-1.2, 1.2, 25),
                                         seq=None, delay=0, saveas=None, bgcor=True, zmax=29, zmin=-29, cav_switch=None,
                                         ) 
    
    Wfun.analyze(data = data_all)
#    ax[lll].imshow(data_all)
    fig = Wfun.fig
    fig.set_size_inches(6.5184,4.2)

    size_label=24
    #pl.rc('font', size=10)
    pl.rc('axes', titlesize=size_label)
    pl.rc('axes', labelsize=size_label)
    pl.rc('xtick', labelsize=size_label)
    pl.rc('ytick', labelsize=size_label)
    pl.axes().set_aspect('1')

    fig.savefig('tomo_5'+str(lll+10), dpi=600)




'''
plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
'''


