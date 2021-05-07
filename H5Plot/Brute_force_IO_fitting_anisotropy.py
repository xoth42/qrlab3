# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 11:25:50 2021

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

fields = np.linspace(0,0,1)
limit_for_off = 1


def S31_resid(param,x,y,delta):

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
    gamma1 = param[8]
    gamma2 = param[9]
    gamma3 = 0
    gamma4 = param[10]
    A = param[11]
    phi = param[12]
    i_off = param[13]
    r_off = param[14]
    ani_diag = param[15]
    null_field = param[16]

    identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
    out_3 = []
    H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*delta*k+spl],[ga2,gb2,-1j*delta*k+spl, wn]])  
    # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
    b_in = np.array([1,0,0,0]).reshape(4,1)
    x = x/1e9
    for i in range(len(x)):
        wpp = wp + ani_diag*(1/np.cosh(delta/null_field))
        wnn = wn - ani_diag*(1/np.cosh(delta/null_field))
        wpn = 1j*delta*k+spl*(1/np.cosh(delta/null_field))
        wnp = -1j*delta*k+spl*(1/np.cosh(delta/null_field))
        H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wpp,wpn],[ga2,gb2,wnp, wnn]])
        
        big_matrix = (x[i]*identity - H + 1j*gamma/2)
        
        a = -1j*np.matmul(np.matmul(la.inv(big_matrix),np.sqrt(gamma)),b_in)
        
        out_3.append(A*np.exp(-1j*phi)*(np.sqrt(gamma4)*a[3][0]))
    out_3_ = np.conj(out_3)
#    if np.max(np.abs(datas)) < limit_for_off:
#        r_off = (y[0].real+ y[-1].real)/2
#        i_off = (y[0].imag+ y[-1].imag)/2#, vary = False)
    out_3_ = out_3_ + r_off + 1j*i_off

#    S31_mag = abs(np.array(out_3_))
#    S31_phase = np.angle(np.array(out_3_))
#    return np.abs(out_3_ - y)
    return np.sum(np.sqrt((np.real(out_3_)-np.real(y))**2+(np.imag(out_3_)-np.imag(y))**2))

''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
hdf5_name = '20210105cooldown_circulator_VNA - Copy.hdf5'

#date = ['20210109','20210110']
#times = ['090240','072113']
#fields = [-.048,.048]
times = ['005144']
date = ['20210109']
fields = [0]
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

for i in range(len(times)):
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
    exp = f[date[i]][title]
    #    exp = f['/' + date1 + '/' + time + '_' + experiment]
    y_keys = exp.keys()
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

wa = 10.8104
wb = 10.804
ga = .013
ga2 = .002
gb = ga
gb2 = ga2
wp = 10.72
k = 9
spl = .105
wn = 10.82
gamma1 = .0001333
gamma2 = .001153
gamma3 = 0
gamma4 = 1.254
A = .2388
phi = 1.65
i_off = .0001277
r_off = .001
ani_diag = .07
null_field = .025


param = [wa,wb,ga,ga2,wp,k,spl,wn,gamma1,gamma2,gamma4,A,phi,i_off,r_off,ani_diag,null_field]

var = 0    
val_num = 1
wa_lst = np.linspace(wa*(1-var),wa*(1+var),val_num)
wb_lst = np.linspace(wb*(1-var),wb*(1+var),val_num)
ga_lst = np.linspace(ga*(1-var),ga*(1+var),val_num)
ga2_lst = np.linspace(ga2*(1-var),ga2*(1+var),val_num)
gb = ga
gb2 = ga2
#wp_lst = np.linspace(wp*(1-var),wp*(1+var),val_num)
k_lst = np.linspace(k,k,1)
spl_lst = np.linspace(spl*(1-var),spl*(1+var),val_num)
wp_lst = np.linspace(wp*(1-var),wp*(1+var),val_num)
wn_lst = np.linspace(wn*(1-var),wn*(1+var),val_num)
gamma1_lst = np.linspace(gamma1*(1-0),gamma1*(1+0),1)
gamma2_lst = np.linspace(gamma2*(1-0),gamma2*(1+0),1)
gamma4_lst = np.linspace(gamma4*(1-var),gamma4*(1+var),val_num)
A_lst = np.linspace(A*(1-0),A*(1+0),1)
#gamma1_lst = np.linspace(gamma1*(1-.8),gamma1*(1+1),15)
#gamma2_lst = np.linspace(gamma2*(1-.9),gamma2*(1+.5),15)
#gamma4_lst = np.linspace(gamma4*(1-.5),gamma4*(1+.8),15)
#A_lst = np.linspace(A*(1-.5),A*(1+.5),15)
phi_lst = np.linspace(phi*(1-var),phi*(1+var),val_num)
i_off_lst = np.linspace(i_off*(1-var),i_off*(1+var),val_num)
r_off_lst = np.linspace(r_off*(1-var),r_off*(1+var),val_num)
ani_diag_lst = np.linspace(ani_diag*(1-var),ani_diag*(1+var),val_num)
null_field_lst = np.linspace(null_field*(1-var),null_field*(1+var),val_num)

best_fit = 0
for j in range(len(times)):
    fit_resid_o = S31_resid(param,freqs_all[j],datas[j],fields[j])
    best_fit += fit_resid_o

#oh boy this is about to get messy......
count = 0
for q in range(len(wa_lst)):
    for w in range(len(wb_lst)):
        for e in range(len(ga_lst)):
            for r in range(len(ga2_lst)):
                for t in range(len(wp_lst)):
                    for y in range(len(k_lst)):
                        for u in range(len(spl_lst)):
                            for o in range(len(wn_lst)):
                                for p in range(len(gamma1_lst)):
                                    for a in range(len(gamma2_lst)):
                                        for s in range(len(gamma4_lst)):
                                            for d in range(len(A_lst)):
                                                for f in range(len(phi_lst)):
                                                    for g in range(len(i_off_lst)):
                                                        for h in range(len(r_off_lst)):
                                                            for j in range(len(ani_diag_lst)):
                                                                for k in range(len(null_field_lst)):
                                                                    param_trial = [wa_lst[q],wb_lst[w],ga_lst[e],ga2_lst[r],wp_lst[t],k_lst[y],spl_lst[u],wn_lst[o],gamma1_lst[p],gamma2_lst[a],gamma4_lst[s],A_lst[d],phi_lst[f],i_off_lst[g],r_off_lst[h],ani_diag_lst[j],null_field_lst[k]]
                                                                    total_fit = 0
                                                                    count += 1
                                                                    if count % 100 == 0:
                                                                        print count
                                                                    for j in range(len(times)):
                                                                        fit_resid = S31_resid(param_trial,freqs_all[j],datas[j],fields[j])
                                                                        total_fit += fit_resid
                                                                    if total_fit < best_fit:
                                                                        best_fit = total_fit
                                                                        param = param_trial

                                                                    
                                                                    

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
    gamma1 = param[8]
    gamma2 = param[9]
    gamma3 = 0
    gamma4 = param[10]
    A = param[11]
    phi = param[12]
    i_off = param[13]
    r_off = param[14]
    ani_diag = param[15]
    null_field = param[16]
    
    w = freq_/1e9
    identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
    out_3 = []
#    H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*delta*k+spl],[ga2,gb2,-1j*delta*k+spl, wn]])  
    # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
    b_in = np.array([1,0,0,0]).reshape(4,1)
    for i in range(len(w)):
        wpp = wp + ani_diag*(1/np.cosh(delta/null_field))
        wnn = wn - ani_diag*(1/np.cosh(delta/null_field))
        wpn = 1j*delta*k+spl*(1/np.cosh(delta/null_field))
        wnp = -1j*delta*k+spl*(1/np.cosh(delta/null_field))
        H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wpp,wpn],[ga2,gb2,wnp, wnn]])
        
        big_matrix = (w[i]*identity - H + 1j*gamma/2)
        
        a = -1j*np.matmul(np.matmul(la.inv(big_matrix),np.sqrt(gamma)),b_in)
        
        out_3.append(A*np.exp(-1j*phi)*(np.sqrt(gamma4)*a[3][0]))
    out_3_ = np.conj(out_3)
    out_3_ = out_3_ + r_off + 1j*i_off
    S31_mag = abs(np.array(out_3_))
    S31_phase = np.angle(np.array(out_3_))
    print(out_3[0])
    print(out_3_[0])
    return [out_3_,S31_mag,S31_phase]



for i in range(len(fields)):

    model_data = S31_model(param,fields[i],freqs_all[i])[0]
    
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
        
    
str_params = 'wa,wb,ga,ga2,wp,k,spl,wn,gamma1,gamma2,gamma4,A,phi,i_off,r_off'
str_params = str_params.split(',')
for i in range(len(param)):
    print(str_params[i] + ' = ' + str(param[i]))





















