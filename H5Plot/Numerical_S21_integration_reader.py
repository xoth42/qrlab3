# -*- coding: utf-8 -*-
"""
Created on Mon Feb 01 08:50:46 2021

@author: WangLab
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 17:05:36 2021

@author: WangLab
"""

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
from scipy import integrate

''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
hdf5_name = '20210105cooldown_circulator_VNA - Copy.hdf5'

date = '20210222'
#time = '233434'
#experiment = 'Power_Sweep_VNA'

#fields = np.linspace(-.05,-.05,1)
fields = np.asarray([0,-.005,-.01,-.015,-.02,-.03,-.04,-.05,0,.005,.01,.02,.03,.04,.05])

#fields = np.linspace(0.05, 0.002,13)

''' Primary x axis and secondary if 2d'''
#x_key = 'freqs'
#x2_key = 'powers'

#freq_low = np.linspace(10.7,10.78,101)
freq_mid = np.linspace(10.78,10.83, 1601)
#freq_high = np.linspace(10.83,10.9, 101)
#freq_tot = np.concatenate((freq_low,freq_mid,freq_high))
freq_tot = freq_mid
j = 0 #index of the power from the color plot used 0 = lowest power

save_data = False
read_data = False
tf = 140
data_len_mid = 1601
#data_len_tail = 101
repeat = 20

itime = 13 #index of the field being analyzed so you can save your place and work on only fitting a few fields at a time
ct = 11

if itime == 0 and ct == 0:
#    data_lowg = np.zeros([len(fields),data_len_tail],dtype = complex)
#    data_lowe = np.zeros([len(fields),data_len_tail],dtype = complex)
    data_midg = np.zeros([len(fields),data_len_mid],dtype = complex)
    data_mide = np.zeros([len(fields),data_len_mid],dtype = complex)
    avg_lst_e = np.zeros([repeat,data_len_mid],dtype = complex)
    avg_lst_g = np.zeros([repeat,data_len_mid],dtype = complex)
#    data_highg = np.zeros([len(fields),data_len_tail],dtype = complex)
#    data_highe = np.zeros([len(fields),data_len_tail],dtype = complex)

if read_data == False:    
    f = h5.File(filepath + hdf5_name, 'r')
    
    
    for i, title in enumerate(f[date].keys()):
    #    print int(title[0:6])
    #    print int(title[0:6]) <= 020617
        if int(title[0:6]) <= int('240000') and int(title[0:6]) > int('000000') and title[7:12] =='Singl':
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
            real = exp['real'].value
            imag = exp['imaginary'].value
        
            if ct%2 == 0:
                avg_lst_g[ct//2] = real[j] + 1j * imag[j]
                ct += 1
            elif ct%2 == 1:
                avg_lst_e[ct//2] = real[j] + 1j * imag[j]
                if ct < (2*repeat -1):
                    ct += 1
                elif ct == (2*repeat-1):
                    data_midg[itime] = np.average(avg_lst_g, axis = 0)
                    data_mide[itime] = np.average(avg_lst_e, axis = 0)
                    fig = plt.figure()
                    plt.suptitle('g %s'%(fields[itime]))
                    gs = gridspec.GridSpec(1, 2)
#                    fig.title('%s'%(fields[itime]))
                    fig.add_subplot(gs[0])
                    fig.add_subplot(gs[1]) 
                    for k in range(repeat):
                        fig.axes[0].plot(freq_mid,10*np.log10(avg_lst_g[k]))
                        fig.axes[1].plot(avg_lst_g[k].real,avg_lst_g[k].imag)
                    fig = plt.figure()
                    plt.suptitle('e %s'%(fields[itime]))
                    gs = gridspec.GridSpec(1, 2)
#                    fig.title('%s'%(fields[itime]))
                    fig.add_subplot(gs[0])
                    fig.add_subplot(gs[1]) 
                    for k in range(repeat):
                        fig.axes[0].plot(freq_mid,10*np.log10(avg_lst_e[k]))
                        fig.axes[1].plot(avg_lst_e[k].real,avg_lst_e[k].imag)
                    itime += 1
                    ct = 0
                
#            if ct == 0:
#                data_lowe[itime] = real[j] + 1j * imag[j]
#                ct += 1
#            elif ct == 1:
#                data_lowg[itime] = real[j] + 1j * imag[j]
#                ct += 1
#            elif ct == 2:
#                data_mide[itime] = real[j] + 1j * imag[j]
#                ct += 1
#            elif ct == 3:
#                data_midg[itime] = real[j] + 1j * imag[j]
#                ct += 1
#            elif ct == 4:
#                data_highe[itime] = real[j] + 1j * imag[j]
#                ct += 1
#            elif ct == 5:
#                data_highg[itime] = real[j] + 1j * imag[j]
#                ct = 0
#                itime += 1
if read_data == True:
    file_path = 'C:\\Users\WangLab\Documents\circulator results\\20210201_163118\\'
    file_name = 'S21_results-0.05.txt'
    data_txt = np.loadtxt(file_path+file_name)
    freq_mid = data_txt[0]
    data_midg_r = data_txt[len(data_txt)/5:len(data_txt)/5*2]
    data_midg_i = data_txt[len(data_txt)/5*2:len(data_txt)/5*3]
    data_mide_r = data_txt[len(data_txt)/5*3:len(data_txt)/5*4]
    data_mide_i = data_txt[len(data_txt)/5*4:]
    data_midg =  data_midg_r + 1j*data_midg_i
    data_mide =  data_mide_r + 1j*data_mide_i
                
def int_model(data_mide,data_midg):
#    data_g = np.concatenate((data_lowg,data_midg,data_highg))
#    data_e = np.concatenate((data_lowe,data_mide,data_highe))
    freq_tot = freq_mid    
    data_g = data_midg
    data_e = data_mide * 2 - data_midg
    I_r = np.zeros((len(freq_tot)))
    I_i = np.zeros((len(freq_tot)))
    for i in range(len(freq_tot)):
        c_in_wg = (1 - np.exp(1j * (freq_tot - 10.811)*12))/((freq_tot - 10.811000000000001))
        c_in_we = (1 - np.exp(-1j * (freq_tot[i] - 10.811)*12))/((freq_tot[i] - 10.811000000000001))
        #c_in_w1 * c_in_w2 *
        integrand =  c_in_wg * c_in_we * data_e[i]*np.conjugate(data_g)*(np.exp(-1j*(freq_tot[i]-freq_tot)*tf)-1)/((freq_tot[i]-freq_tot+.000000000000001))
#        if i == 0:
#            plt.figure()
#            plt.plot(freq_tot,integrand)
        I_r[i] = np.trapz(np.real(integrand),freq_tot)
        I_i[i] = np.trapz(np.imag(integrand),freq_tot)
    plt.figure()
    plt.plot(freq_tot,I_r, label = 'real')
    plt.plot(freq_tot,I_i, label = 'imag')
    plt.legend()
    plt.figure()
    plt.plot(I_r,I_i)
    final_r = np.trapz(I_r,freq_tot)
    final_i = np.trapz(I_i, freq_tot)
    return [final_r,final_i]
    

deph = np.zeros(len(fields))
stark = np.zeros(len(fields))

for i in range(len(fields)):
    
    deph[i] = int_model(data_mide[i],data_midg[i])[0]
    stark[i] = int_model(data_mide[i],data_midg[i])[1]

plt.figure()
plt.title('dephasing over field')
plt.xlabel('Field (T)')
plt.ylabel('dephasing at 140 ns')
plt.scatter(fields,deph, label = 'dephasing')
plt.legend()


plt.figure()
plt.title('stark shift over field')
plt.xlabel('Field (T)')
plt.ylabel('stark shift at 140 ns')
plt.scatter(fields,stark, label = 'stark shift')
plt.legend()

plt.figure()
plt.scatter(fields, np.abs(deph +1j*stark))

fields = np.asarray([0,-.005,-.01,-.015,-.02,-.03,-.04,-.05,0,.005,.01,.02,.03,.04,.05])

data_midg_color = np.asarray(list(data_midg)[7:0:-1]+list(data_midg)[8:])
#freq_color = np.asarray(list(freq_mid)[7:0:-1]+list(freq_mid)[8:])
field_color = np.asarray(list(fields)[7:0:-1]+list(fields)[8:])


plt.figure()
field_color, freq_color = np.meshgrid(field_color, freq_mid)
plt.pcolormesh(field_color,freq_color,np.transpose(20*np.log10(abs(data_midg_color))))
plt.colorbar()
plt.show()
data_midg_color_neg = 20*np.log10(abs(np.asarray(list(data_midg)[0:3]+list(data_midg)[4:8])))
data_midg_color_pos = 20*np.log10(abs(np.asarray(list(data_midg)[8:])))

field_sub = fields[8:]

data_sub = data_midg_color_neg - data_midg_color_pos

plt.figure()
field_sub, freq_color = np.meshgrid(field_sub, freq_mid)
plt.pcolormesh(field_sub,freq_color,np.transpose(data_sub))
plt.colorbar()
plt.show()


if save_data:
    freq_mid_sve = np.zeros([len(fields),data_len_mid])
    for i in range(len(fields)):
        freq_mid_sve[i] = freq_mid
# '''Save the data for later analysis'''
    end_time = date + '_' + title[0:6]
    main_filepath = 'C:/Users/WangLab/Documents/circulator results/'
    time_stamp = end_time
    save_filepath = main_filepath + ''.join(time_stamp) + '/'
    
    
    if not os.path.exists(save_filepath):
        os.makedirs(save_filepath)
        
    np.savetxt(save_filepath + 'S21_results%s.txt'%(fields[-1]),
               np.concatenate((freq_mid_sve,np.real(data_midg),np.imag(data_midg),np.real(data_mide),np.imag(data_mide))),
               header = 'freq ,data_g real,data_g imag, data_e+g_real,data_e+g_imag')

#
#dep_neg = [   9.40759431e-10,   4.93678191e-10,
#        -2.52562319e-13,  -5.28190934e-11,   2.81726407e-11]
#
#dep_neg = dep_neg[::-1]
#        
#dep_pos = [  3.43958023e-09,   7.10019422e-10,   5.67214012e-11,
#        -4.44426046e-11,  -1.16782829e-11,   1.99281293e-10]
#
#fields = np.linspace(-.05,.05,11)
#dep_tot = dep_neg + dep_pos
#
#dep_tot = np.asarray(dep_tot)
#
#dep_ram = np.array([ 0.00672172,  0.03705153,  0.03082244,  0.12425323,  0.31253818,
#        0.17380449,  0.12901363,  0.02548504,  0.00199375, -0.01259269,
#       -0.00344911])
#
#plt.figure()
#plt.title('dephasing over field')
#plt.xlabel('Field (T)')
#plt.ylabel('dephasing at 140 ns')
#plt.plot(fields,dep_tot*.9e8, label = 'dephasing from S21 integration')
#plt.plot(fields,dep_ram, label = 'dephasing from ramseys')
#plt.legend()
#



