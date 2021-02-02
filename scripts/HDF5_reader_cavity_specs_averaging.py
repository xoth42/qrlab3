# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 16:12:41 2021

@author: Wang_Lab
"""


import os
import time
import glob


import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
import datetime
#import json
#from lib.math import fit
import lmfit


''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = '01052021cooldown_circulator - Copy (3).hdf5'
date = '20210116'
#experiment = 'ROCavSpectroscopy_keysight'
#experiment = 'Power_Sweep_VNA'
f = h5.File(filepath + hdf5_name, 'r')
j = 0

avg_count = 0
save_data = False
final_plot = True
fields = np.linspace(0,-.05,1)
data_len = 101
repeat = 1
fix_phi0 = None
proj = 'projection'
if j == 0:
    avg_data_g = np.zeros([len(fields),data_len], dtype = 'complex128')
    avg_data_e = np.zeros([len(fields),data_len], dtype = 'complex128')
    
#
#if three_modes:
#    if j == 0:
#        freq1 = np.zeros([nrows,len(fields)])
#        freq2 = np.zeros([nrows,len(fields)])
#if CW_qubit:
#    exp_t = 'CW_Ram'
#else:
#    exp_t = 'Photon'
exp_t = 'ROCavS'
if avg_count == 0:
    avg_array_g = np.zeros([repeat,data_len],dtype = 'complex128')
    avg_array_e = np.zeros([repeat,data_len],dtype = 'complex128')



for i, title in enumerate(f[date].keys()):
#    print int(title[0:6])
#    print int(title[0:6]) <= 020617
    if int(title[0:6]) <= int('122500') and int(title[0:6]) > int('121845') and title[7:13] == exp_t:# and title[7:12] =='ROCav':
        print title



        x_key = 'freqs'
        #x2_key = 'powers'
        exp = f[date][title]
        y_keys = exp.keys()
        
            
        freqs = exp[x_key].value
        
        amp_data = exp['amplitudes']
        phase_data = exp['phases'] 
        if avg_count % 2 == 0:
            avg_array_g[avg_count//2] = amp_data.value*np.exp(1j*phase_data.value* np.pi/180)
            
            avg_count += 1
            
            
        elif avg_count % 2 == 1:
            avg_array_e[avg_count//2] = amp_data.value*np.exp(1j*phase_data.value* np.pi/180)
                
            if avg_count//2 == (repeat-1):
                
                new_data_g = np.average(avg_array_g, axis = 0)
                new_data_e = np.average(avg_array_e, axis = 0)
                avg_data_g[j] = new_data_g
                avg_data_e[j] = new_data_e
                
                j += 1
                avg_count = 0
                
            elif avg_count//2 < (repeat-1):
                avg_count += 1


if final_plot:
    plt.figure()
    plt.title('cavity specs g/e amp')
    plt.xlabel('frequency')
    plt.ylabel('amplitude')
    for i in range(len(fields)):
        plt.plot(freqs,np.abs(avg_data_g)[i], label = 'g %s T'%(fields[i]))
        plt.plot(freqs,np.abs(avg_data_e)[i], label = 'e %s T'%(fields[i]))
    plt.legend()
    
    plt.figure()
    plt.title('cavity specs g/e phase')
    plt.xlabel('frequency')
    plt.ylabel('amplitude')
    for i in range(len(fields)):
        plt.plot(freqs,np.angle(avg_data_g)[i], label = 'g %s T'%(fields[i]))
        plt.plot(freqs,np.angle(avg_data_e)[i], label = 'e %s T'%(fields[i]))
    plt.legend()
    
#    plt.figure()
#    plt.title('cavity specs e amp')
#    plt.xlabel('frequency')
#    plt.ylabel('amplitude')
#    for i in range(len(fields)):
#        plt.plot(freqs,np.abs(avg_data_e)[i], label = '%s T'%(fields[i]))
#    plt.legend()
#            
#    plt.figure()
#    plt.title('cavity specs e phase')
#    plt.xlabel('frequency')
#    plt.ylabel('amplitude')
#    for i in range(len(fields)):
#        plt.plot(freqs,np.angle(avg_data_e)[i], label = '%s T'%(fields[i]))
#    plt.legend()
    
    plt.figure()
    plt.title('cavity specs e-g amp')
    plt.xlabel('frequency')
    plt.ylabel('amplitude')
    for i in range(len(fields)):
        plt.plot(freqs,np.abs(avg_data_e-avg_data_g)[i], label = '%s T'%(fields[i]))
    plt.legend()
    
    plt.figure()
    plt.title('cavity specs e-g phase')
    plt.xlabel('frequency')
    plt.ylabel('amplitude')
    for i in range(len(fields)):
        plt.plot(freqs,np.angle(avg_data_e-avg_data_g)[i], label = '%s T'%(fields[i]))
    plt.legend()
            


if save_data:
        
        data_to_save = np.concatenate(avg_data_g,avg_data_e)
        main_filepath = 'C:\\Users\\Wang_Lab\\Documents\\circulator results\\01052021cooldown_circulator\\Cavity_specs\\'
        end_time = list(str(datetime.datetime.now())[:19])
        end_time[13] = '-'
        end_time[16] = '-'
        time_stamp =''.join(end_time)
        save_filepath = main_filepath 
        
        
        if not os.path.exists(save_filepath):
            os.makedirs(save_filepath)
            

        np.savetxt(save_filepath + ' %s_%s_%s_T_results.txt'%(time_stamp,fields[0],fields[-1]), data_to_save)



















































