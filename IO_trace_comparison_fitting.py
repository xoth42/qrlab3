# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 13:12:38 2020

@author: WangLab
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 22:38:49 2020

@author: WangLab
"""

import os
import time
import lmfit 


import matplotlib
matplotlib.interactive(True)
import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
import json
from matplotlib import gridspec
import scipy.linalg as la



''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
hdf5_name = '1126cooldown_circulator_VNA - Copy.hdf5'

date = '20201201'
#time = '233434'
#experiment = 'Power_Sweep_VNA'

#fields = np.linspace(-.05,-.05,1)
fields = np.linspace(-0.05,0,1)
#fields = np.linspace(0.05, 0.002,13)

''' Primary x axis and secondary if 2d'''
#x_key = 'freqs'
#x2_key = 'powers'



j = 0 #index of the power from the color plot used 0 = lowest power

data_len = 1601
itime = 0 #index of the field being analyzed so you can save your place and work on only fitting a few fields at a time

if itime == 0:
    datas = np.zeros([len(fields),data_len],dtype = complex)

f = h5.File(filepath + hdf5_name, 'r')

limit_for_off = 1
k = 0
#freq1 = np.zeros([nrows,len(fields)])
#freq2 = np.zeros([nrows,len(fields)])
#freq1_err = np.zeros([nrows,len(fields)])
#freq2_err = np.zeros([nrows,len(fields)])  
r_off = np.zeros(len(fields))
i_off = np.zeros(len(fields))
for i, title in enumerate(f[date].keys()):
#    print int(title[0:6])
#    print int(title[0:6]) <= 020617
    if int(title[0:6]) <= int('105043') and int(title[0:6]) > int('105041') and title[7:12] =='Power':
#    if int(title[0:6]) <= int('192459') and int(title[0:6]) > int('192457') and title[7:12] =='Power':
        print(title)



        x_key = 'freqs'
        #x2_key = 'powers'
        exp = f[date][title]
#    exp = f['/' + date1 + '/' + time + '_' + experiment]
        y_keys = list(exp.keys())
        #print(y_keys)
        
        #y_keys.remove(x_key)
        #y_keys.remove(x2_key)
        freq = exp['freqs'].value
        #current = exp['currents'].value
#        powers = exp['powers'].value
        real = exp['realS21'].value
        imag = exp['imaginaryS21'].value
        
        datas[itime] = real[j] + 1j * imag[j]
        if np.max(np.abs(datas)) < limit_for_off:
            r_off[k] = (datas[itime][0].real+ datas[itime][-1].real)/2
            i_off[k] = (datas[itime][0].imag+ datas[itime][-1].imag)/2#, vary = False)

        itime = itime + 1
        k += 1

        
gamma2 = .0004
gamma1 = .0012
gamma3 = 0
gamma4 = .2577
wa = 10.804
wb = 10.808
wp = 10.77
wn = 10.825
ga = .021
ga2 = -.00592
gb = ga
gb2 = ga2
spl = -.0684
A = .15
k = 8
phi = 2.15

def S31_model(gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,delta,A,k,phi):
    w = freq/1e9
    identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
    out_3 = []
    H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*delta*k+spl],[ga2,gb2,-1j*delta*k+spl, wn]])  
    # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
    b_in = np.array([0,1,0,0]).reshape(4,1)
    for i in range(len(w)):
        
        big_matrix = (w[i]*identity - H + 1j*gamma/2)
        
        a = -1j*np.matmul(np.matmul(la.inv(big_matrix),np.sqrt(gamma)),b_in)
        
        out_3.append(A*np.exp(-1j*phi)*(np.sqrt(gamma4)*a[3][0]))
    out_3_ = np.conj(out_3)
    S31_mag = abs(np.array(out_3_))
    S31_phase = np.angle(np.array(out_3_))
    print((out_3[0]))
    print((out_3_[0]))
    return [out_3_,S31_mag,S31_phase]


model_data = np.zeros([len(fields),data_len],dtype = complex)
for i in range(len(fields)):
    model_data[i] = S31_model(gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,fields[i],A,k,phi)[0] + r_off[i] + 1j*i_off[i]


#for i in range(len(fields)):
#    
#    plt.figure()
#    plt.title('Magnitude at field = %s'%(fields[i]))
#    plt.plot(freq,np.abs(model_data[i]),label = 'model')
#    plt.plot(freq,np.abs(datas[i]), label = 'data')
#    plt.legend()
#    
#    plt.figure()
#    plt.title('Phase at field = %s'%(fields[i]))
#    plt.plot(freq,np.angle(model_data[i]),label = 'model')
#    plt.plot(freq,np.angle(datas[i]), label = 'data')
#    plt.legend()
#
#    plt.figure()
#    plt.title('IQ at field = %s'%(fields[i]))
#    plt.plot(np.real(model_data[i]),np.imag(model_data[i]),label = 'model')
#    plt.plot(np.real(datas[i]),np.imag(datas[i]), label = 'data')
#    plt.legend()
#    
    
for i in range(len(fields)):
    
    plt.figure('Mag')
    plt.title('Magnitude at field = %s'%(fields[i]))
    plt.plot(freq,np.abs(model_data[i]),label = 'model')
#    plt.plot(freq,np.abs(datas[i]), label = 'data')
    plt.legend()
    
    plt.figure("phase")
    plt.title('Phase at field = %s'%(fields[i]))
    plt.plot(freq,np.angle(model_data[i]),label = 'model')
#    plt.plot(freq,np.angle(datas[i]), label = 'data')
    plt.legend()

    plt.figure("IQ")
    plt.title('IQ at field = %s'%(fields[i]))
    plt.plot(np.real(model_data[i]),np.imag(model_data[i]),label = 'model')
#    plt.plot(np.real(datas[i]),np.imag(datas[i]), label = 'data')
    plt.legend()























