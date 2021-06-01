# -*- coding: utf-8 -*-
"""
Created on Wed Jan 06 13:25:34 2021

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

freq = np.linspace(10.8,10.84, 1601)

def S31_model(gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,delta,A,k,phi):
    w = freq
    identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
    out_3 = []
    H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*delta*k+spl],[ga2,gb2,-1j*delta*k+spl, wn]])  
    # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
    b_in = np.array([1,0,0,0]).reshape(4,1)
    for i in range(len(w)):
        
        big_matrix = (w[i]*identity - H + 1j*gamma/2)
        
        a = -1j*np.matmul(np.matmul(la.inv(big_matrix),np.sqrt(gamma)),b_in)
        
        out_3.append(A*np.exp(-1j*phi)*(np.sqrt(gamma4)*a[3][0]))
    out_3_ = np.conj(out_3)
    S31_mag = abs(np.array(out_3_))
    S31_phase = np.angle(np.array(out_3_))
    print(out_3[0])
    print(out_3_[0])
    return [out_3_,S31_mag,S31_phase]

def S31_eigen(gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,delta,A,k,phi,chi):
#    w = freq
#    identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
    out_eigs = np.zeros([len(delta),6])
    for i in range(len(delta)):
    
        H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*delta[i]*k+spl],[ga2,gb2,-1j*delta[i]*k+spl, wn]]) - + 1j*gamma/2


        e,v =la.eig(H) 
        if e[2] > e[3]:
            out_eigs[i][0] = e[2]
            out_eigs[i][1] = e[3]
#            wa_p.append(e[2]) 
#            wb_p.append(e[3]) 
#            w3.append(e[0])
#            w4.append(e[1]) 
#            va_p.append(v[:,2]) 
#            vb_p.append(v[:,3])
        else:
            out_eigs[i][0] = e[3]
            out_eigs[i][1] = e[2]
#            wa_p.append(e[3]) 
#            wb_p.append(e[2]) 
#            w3.append(e[1])
#            w4.append(e[0])
#            va_p.append(v[:,3]) 
#            vb_p.append(v[:,2])
        H = np.array([[wa,0,ga,ga2],[0,wb-chi,-gb,gb2],[ga,-gb,wp,1j*delta[i]*k+spl],[ga2,gb2,-1j*delta[i]*k+spl, wn]]) - + 1j*gamma/2


        e,v =la.eig(H) 
        if e[2] > e[3]:
            out_eigs[i][2] = e[2]
            out_eigs[i][3] = e[3]
#            wa_p.append(e[2]) 
#            wb_p.append(e[3]) 
#            w3.append(e[0])
#            w4.append(e[1]) 
#            va_p.append(v[:,2]) 
#            vb_p.append(v[:,3])
        else:
            out_eigs[i][2] = e[3]
            out_eigs[i][3] = e[2]
#            wa_p.append(e[3]) 
#            wb_p.append(e[2]) 
#            w3.append(e[1])
#            w4.append(e[0])
#            va_p.append(v[:,3]) 
#            vb_p.append(v[:,2])
        out_eigs[i][4] = out_eigs[i][2] - out_eigs[i][0]
        out_eigs[i][5] = out_eigs[i][3] - out_eigs[i][1]
    return np.transpose(out_eigs)


gamma1 = .000344
gamma2 = .001613
gamma3 = 0
gamma4 = .1977
wa = 10.808
wb = 10.804
wp = 10.774
wn = 10.822
ga = .025
ga2 = -.00466
gb = ga
gb2 = ga2
spl = -.061
A = .15
k = 8
phi = 2.15
delta = -.02 #field
delta_lst = np.linspace(0,-.05,26)
chi = .001 #shift to cavity b frequency

freq_range = [10.80,10.81] #range of frequencies to search for a local maximum to get an effective chi shift in GHz
beg_index = list(freq).index(freq_range[0])
end_index = list(freq).index(freq_range[1])

spectrum = S31_model(gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,delta,A,k,phi)

nar_spec = spectrum[1][beg_index:end_index]

max_val = np.amax(nar_spec)
max_ind = np.where(nar_spec == max_val)[0][0] + beg_index

max_freq =  freq[max_ind]

spectrum_shift = S31_model(gamma1,gamma2,gamma3,gamma4,wa,wb-chi,wp,wn,ga,ga2,gb,gb2,spl,delta,A,k,phi)

nar_spec_shift = spectrum_shift[1][beg_index:end_index]

max_val_shift = np.amax(nar_spec_shift)
max_ind_shift = np.where(nar_spec_shift == max_val_shift)[0][0] + beg_index

max_freq_shift =  freq[max_ind_shift]

tot_shift = max_freq - max_freq_shift

plt.figure()
plt.plot(freq,spectrum[1], label = 'qubit in g')
plt.plot(freq,spectrum_shift[1], label = 'qubit in e')
plt.title('Spectrum shift = %s'%(tot_shift))
plt.xlabel('frequency (GHz)')
plt.ylabel('amplitude')
plt.legend()

chi_eig = S31_eigen(gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,delta_lst,A,k,phi,chi)

plt.figure()
plt.plot(delta_lst,chi_eig[0], label = 'mode 1 qubit 2 in g')
plt.plot(delta_lst,chi_eig[1], label = 'mode 2 qubit 2 in g')
plt.plot(delta_lst,chi_eig[2], label = 'mode 1 qubit 2 in e')
plt.plot(delta_lst,chi_eig[3], label = 'mode 2 qubit 2 in e')
plt.title('cavity eigenmodes')
plt.xlabel('fields')
plt.ylabel('frequency')
plt.legend()



plt.figure()
plt.plot(delta_lst,-chi_eig[4], label = 'mode 1')
plt.plot(delta_lst,-chi_eig[5], label = 'mode 2')
plt.title('cavity eigenmodes difference')
plt.xlabel('fields')
plt.ylabel('frequency')
plt.legend()


print(tot_shift)





























