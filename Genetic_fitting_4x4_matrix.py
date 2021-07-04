# -*- coding: utf-8 -*-
"""
Created on Tue Feb 02 15:48:52 2021

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

#fields = np.linspace(0,0,1)
#limit_for_off = 1


def S31_resid(param,x,y,delta):#fitness function, getting the S31 resiual from the theory

    wa = param[0]
    wb = param[1]
    ga = param[2]
    ga2 = param[3]
    gb = ga
    gb2 = ga2
    wp = param[4]
    k = param[5]
    spl = param[6]
    wn = param[7]
    gamma1 = abs(param[8])
    gamma2 = abs(param[9])
    gamma3 = 0
    gamma4 = abs(param[10])
    A = abs(param[11])
    phi = param[12]
    i_off = param[13]
    r_off = param[14]
    ani_diag = param[15]
    null_field = param[16]

    identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
    fitness_tot = 0
    for j in range(len(delta)):
        out_3 = []
        wpp = wp + ani_diag*np.exp(delta[j]/null_field)
        wnn = wn - ani_diag*np.exp(delta[j]/null_field)
        wpn = -1j*delta[j]*k+spl*np.exp(delta[j]/null_field)
        wnp = 1j*delta[j]*k+spl*np.exp(delta[j]/null_field)
        H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wpp,wpn],[ga2,gb2,wnp, wnn]])  
        # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
        b_in = np.array([1,0,0,0]).reshape(4,1)
        x = x/1e9
        for i in range(len(x)):
            
            big_matrix = (x[i]*identity - H + 1j*gamma/2)
            
            a = -1j*np.matmul(np.matmul(la.inv(big_matrix),np.sqrt(gamma)),b_in)
            
            out_3.append(A*np.exp(-1j*phi)*(np.sqrt(gamma4)*a[3][0]))
        out_3_ = np.conj(out_3)
    #    if np.max(np.abs(datas)) < limit_for_off:
    #        r_off = (y[0].real+ y[-1].real)/2
    #        i_off = (y[0].imag+ y[-1].imag)/2#, vary = False)
        out_3_ = out_3_ + r_off + 1j*i_off
        fitness_tot += np.sum(np.sqrt((np.real(out_3_)-np.real(y[j]))**2+(np.imag(out_3_)-np.imag(y[j]))**2))

    return fitness_tot

''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
hdf5_name = '20210105cooldown_circulator_VNA - Copy.hdf5'

date = '20210109'
times = ['005144','033519','055828','074046','090240']
fields = [0,-.016,-.03,-.04,-.048]
#times = ['225028']
#fields = [0]
#time_ = '192458'
#experiment = 'Power_Sweep_VNA'

#fields = np.linspace(-.05,-.05,1)

#fields = np.linspace(0.05, 0.002,13)

''' Primary x axis and secondary if 2d'''
#x_key = 'freqs'
#x2_key = 'powers'
data_len = 1601

datas = np.zeros((len(times),data_len),dtype = complex)
freqs_all = []
j = 0 #index of the power from the color plot used 0 = lowest power

for i in range(len(times)):#storing all the data from HDF5 files
    f = h5.File(filepath + hdf5_name, 'r')
    
    limit_for_off = 1
    k = 0
    #freq1 = np.zeros([nrows,len(fields)])
    #freq2 = np.zeros([nrows,len(fields)])
    #freq1_err = np.zeros([nrows,len(fields)])
    #freq2_err = np.zeros([nrows,len(fields)])  
    r_off = np.zeros(1)
    i_off = np.zeros(1)
    
    title = str(times[i]) + '_Power_Sweep_VNA'
    x_key = 'freqs'
    #x2_key = 'powers'
    exp = f[date][title]
    #    exp = f['/' + date1 + '/' + time + '_' + experiment]
    y_keys = list(exp.keys())
    #print(y_keys)
    
    #y_keys.remove(x_key)
    #y_keys.remove(x2_key)
    freq = exp['freqs'].value
    freqs_all.append(list(freq))
    #current = exp['currents'].value
    #        powers = exp['powers'].value
    real = exp['realS21'].value
    imag = exp['imaginaryS21'].value
    datas[i] = real[j] + 1j*imag[j] 


if np.max(np.abs(datas[0])) < limit_for_off:
    r_off = (datas[0].real+ datas[-1].real)/2
    i_off = (datas[0].imag+ datas[-1].imag)/2#, vary = False)

freqs_all = np.array(freqs_all, dtype = object)
# our starting values
wa = 10.8104 #fixed
wb = 10.804 #fixed
ga = .02
ga_stdv =.005
ga2 = .008
ga2_stdv = .003
gb = ga
gb2 = ga2
wp = 10.72
wp_stdv = .015
k = 8 #fixed
spl = .08
spl_stdv = .01
wn = 10.85
wn_stdv = .015
gamma1 = .00015
gamma1_stdv = .00015
gamma2 = .001
gamma2_stdv = .00015
gamma3 = 0 #fixed
gamma4 = .36
gamma4_stdv = .025
A = .1345
A_stdv = .025
phi = -1.6
phi_stdv = .25
i_off = .00061#fixed
r_off = -.00017#fixed
ani_diag = .07
ani_diag_stdv = .01
null_field = .05
null_field_stdv = .01

ind_vary_lst = [2,3,4,6,7,8,9,10,11,12,15,16]
params_lst = [ga,ga2,wp,spl,wn,gamma1,gamma2,gamma4,A,phi,ani_diag,null_field]
stdv_lst = [ga_stdv,ga2_stdv,wp_stdv,spl_stdv,wn_stdv,gamma1_stdv,gamma2_stdv,gamma4_stdv,A_stdv,phi_stdv,ani_diag_stdv,null_field_stdv]
trial_size = 100

param = np.asarray([wa,wb,ga,ga2,wp,k,spl,wn,gamma1,gamma2,gamma4,A,phi,i_off,r_off,ani_diag,null_field])

trials = np.zeros([trial_size,len(param)])
for i in range(len(trials)):
    trials[i] = param

for i in range(len(trials)):
    for j in range(len(ind_vary_lst)):
        trials[i][ind_vary_lst[j]] = np.random.normal(params_lst[j],stdv_lst[j])

        
fitness_test = np.zeros(trial_size)
for i in range(len(trials)):
    fitness_test[i] = S31_resid(trials[i],freq,datas,fields)

    
generations = 100
numbr_param_vary = 3
parent_number = 30

for i in range(generations):
    sort_lst = np.argsort(fitness_test)
    for j in range(len(sort_lst)-parent_number):
        for k in range(numbr_param_vary):
            parent_index = np.random.randint(0,parent_number)
            param_index = np.random.randint(0,len(ind_vary_lst))
            trials[sort_lst[10+j]][ind_vary_lst[param_index]] = np.random.normal(trials[sort_lst[parent_index]][ind_vary_lst[param_index]],stdv_lst[param_index])
        fitness_test[sort_lst[10+j]] = S31_resid(trials[sort_lst[10+j]],freq,datas,fields)
    print(i)

sort_lst_final = np.argsort(fitness_test)

param_final = trials[sort_lst_final[0]]
    

                                                                    
                                                                    

def S31_model(param,delta,freq_):
    wa = param[0]
    wb = param[1]
    ga = param[2]
    ga2 = param[3]
    gb = ga
    gb2 = ga2
    wp = param[4]
    k = param[5]
    spl = param[6]
    wn = param[7]
    gamma1 = abs(param[8])
    gamma2 = abs(param[9])
    gamma3 = 0
    gamma4 = abs(param[10])
    A = abs(param[11])
    phi = param[12]
    i_off = param[13]
    r_off = param[14]
    ani_diag = param[15]
    null_field = param[16]
    w = freq_/1e9
    identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
    out_3 = []
    wpp = wp + ani_diag*np.exp(delta/null_field)
    wnn = wn - ani_diag*np.exp(delta/null_field)
    wpn = -1j*delta*k+spl*np.exp(delta/null_field)
    wnp = 1j*delta*k+spl*np.exp(delta/null_field)
    H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wpp,wpn],[ga2,gb2,wnp, wnn]])    
    # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
    b_in = np.array([1,0,0,0]).reshape(4,1)
    for i in range(len(w)):
        
        big_matrix = (w[i]*identity - H + 1j*gamma/2)
        
        a = -1j*np.matmul(np.matmul(la.inv(big_matrix),np.sqrt(gamma)),b_in)
        
        out_3.append(A*np.exp(-1j*phi)*(np.sqrt(gamma4)*a[3][0]))
    out_3_ = np.conj(out_3)
    out_3_ = out_3_ + r_off + 1j*i_off
    S31_mag = abs(np.array(out_3_))
    S31_phase = np.angle(np.array(out_3_))
    print((out_3[0]))
    print((out_3_[0]))
    return [out_3_,S31_mag,S31_phase]



for i in range(len(fields)):

    model_data = S31_model(param_final,fields[i],freqs_all[i])[0]
    
    plt.figure()
    plt.title('Magnitude at field = %s'%(fields[i]))
    
    plt.plot(freqs_all[i],np.abs(datas[i]), label = 'data')
    plt.plot(freqs_all[i],np.abs(model_data),label = 'model')
    plt.legend()
    
    plt.figure()
    plt.title('Phase at field = %s'%(fields[i]))
    
    plt.plot(freqs_all[i],np.angle(datas[i]), label = 'data')
    plt.plot(freqs_all[i],np.angle(model_data),label = 'model')
    plt.legend()
    
    plt.figure()
    plt.title('IQ at field = %s'%(fields[i]))
    plt.plot(np.real(datas[i]),np.imag(datas[i]), label = 'data')
    plt.plot(np.real(model_data),np.imag(model_data),label = 'model')
    plt.legend()
        
    
str_params = 'wa,wb,ga,ga2,wp,k,spl,wn,gamma1,gamma2,gamma4,A,phi,i_off,r_off,ani_diag,null_field'
str_params = str_params.split(',')
for i in range(len(param)):
    print((str_params[i] + ' = ' + str(param_final[i])))





















