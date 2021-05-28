# -*- coding: utf-8 -*-
"""
Created on Mon 2/21 2021

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

fields = np.linspace(-0.05,0,26)

f1 = 12
f2 = 10
freqs_all = np.linspace(f1,f2,6000)

freqs_all = np.array(freqs_all, dtype = object)

wa = 10.8104
wb = 10.804
ga = .01
ga2 = .005
gb = ga
gb2 = ga2
wp = 10.72
k = 9
spl = .1
wn = 10.98
gamma1 = .00015
gamma2 = .001
gamma3 = .002
gamma4 = .25
A = .45
phi = -1.4
i_off = .00061
r_off = -.00017
ani_diagp = .07
ani_diagn = .17
null_field = .0185
ga_an = .0095
ga2_an = .003
ka = .0005
kb = .001



param = [wa,wb,ga,ga2,wp,k,spl,wn,gamma1,gamma2,gamma4,A,phi,i_off,r_off,ani_diagp,null_field,ga_an,ga2_an,ka,kb,ani_diagn]


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
    ani_diagp = param[15]
    null_field = param[16]
    ga_an = param[17]
    ga2_an = param[18]
    gb_an = ga_an
    gb2_an = ga2_an
    ka = param[19]
    kb = param[20]
    ani_diagn = param[21]
    
    w = freq_
    identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
    out_3 = []
#    H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*delta*k+spl],[ga2,gb2,-1j*delta*k+spl, wn]])  
    # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
    b_in = np.array([1,0,0,0]).reshape(4,1)
    for i in range(len(w)):
        wpp = wp + ani_diagp*((1/np.cosh(delta/null_field)))
        wnn = wn - ani_diagn*((1/np.cosh(delta/null_field)))
        wpn = -1j*delta*k+spl*((1/np.cosh(delta/null_field)))
        wnp = 1j*delta*k+spl*((1/np.cosh(delta/null_field)))
        ga_tot = ga + ga_an*((1/np.cosh(delta/null_field)))
        ga2_tot = ga2 + ga2_an*((1/np.cosh(delta/null_field)))
        gb_tot = gb + gb_an*((1/np.cosh(delta/null_field)))
        gb2_tot = gb2 + gb2_an*((1/np.cosh(delta/null_field)))
        H = np.array([[wa-1j*ka/2,0,ga_tot,ga2_tot],
                      [0,wb-1j*kb/2,-gb_tot,gb2_tot],
                      [ga_tot,-gb_tot,wpp,wpn],
                      [ga2_tot,gb2_tot,wnp, wnn]])
        big_matrix = (w[i]*identity - H + 1j*gamma/2)
        
        a = -1j*np.matmul(np.matmul(la.inv(big_matrix),np.sqrt(gamma)),b_in)
        
        out_3.append(A*np.exp(-1j*phi)*(np.sqrt(gamma4)*a[3][0]))
    out_3_ = np.conj(out_3)
    out_3_ = out_3_ + r_off + 1j*i_off
    S31_mag = abs(np.array(out_3_))
    S31_phase = np.angle(np.array(out_3_))
#    print(out_3[0])
#    print(out_3_[0])
    return [out_3_,S31_mag,S31_phase]

#def S21_model(param,delta,freq_):
#    wa = param[0]
#    wb = param[1]
#    ga = param[2]
#    ga2 = param[3]
#    gb = ga
#    gb2 = ga2
#    wp = param[4]
#    k = param[5]
#    spl = param[6]
#    wn = param[7]
#    gamma1 = param[8]
#    gamma2 = param[9]
#    gamma3 = 0
#    gamma4 = param[10]
#    A = param[11]
#    phi = param[12]
#    i_off = param[13]
#    r_off = param[14]
#    ani_diag = param[15]
#    null_field = param[16]
#    ga_an = param[17]
#    ga2_an = param[18]
#    gb_an = ga_an
#    gb2_an = ga2_an
#    ka = pram[19]
#    kb = param[20]
#    
#    w = freqs_all
#    identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
#    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
#    out_3 = []
##    H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*delta*k+spl],[ga2,gb2,-1j*delta*k+spl, wn]])  
#    # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
#    b_in = np.array([1,0,0,0]).reshape(4,1)
#    for i in range(len(w)):
#        wpp = wp + ani_diag*((1/np.cosh(delta/null_field)))
#        wnn = wn - ani_diag*((1/np.cosh(delta/null_field)))
#        wpn = -1j*delta*k+spl*((1/np.cosh(delta/null_field)))
#        wnp = 1j*delta*k+spl*((1/np.cosh(delta/null_field)))
#        ga_tot = ga + ga_an*((1/np.cosh(delta/null_field)))
#        ga2_tot = ga2 + ga2_an*((1/np.cosh(delta/null_field)))
#        gb_tot = gb + gb_an*((1/np.cosh(delta/null_field)))
#        gb2_tot = gb2 + gb2_an*((1/np.cosh(delta/null_field)))
#        H = np.array([[wa-1j*ka/2,0,ga_tot,ga2_tot],
#                      [0,wb-1j*kb/2,-gb_tot,gb2_tot],
#                      [ga_tot,-gb_tot,wpp,wpn],
#                      [ga2_tot,gb2_tot,wnp, wnn]])
#        
#        big_matrix = (w[i]*identity - H + 1j*gamma/2)
#        
#        a = -1j*np.matmul(np.matmul(la.inv(big_matrix),np.sqrt(gamma)),b_in)
#        
#        out_3.append(A*np.exp(-1j*phi)*(np.sqrt(gamma2)*a[1][0]))
#    out_3_ = np.conj(out_3)
#    out_3_ = out_3_ + r_off + 1j*i_off
#    S31_mag = abs(np.array(out_3_))
#    S31_phase = np.angle(np.array(out_3_))
#    print(out_3[0])
#    print(out_3_[0])
#    return [out_3_,S31_mag,S31_phase]
#

if 0:
    for i in range(len(fields)):
    
        model_data = S31_model(param,fields[i],freqs_all)[0]
        
        plt.figure()
        plt.title('Magnitude at field = %s'%(fields[i]))
        
    #    plt.plot(freqs_all[i],np.abs(datas[i]), label = 'data')
        plt.plot(freqs_all[i],np.abs(model_data),label = 'model')
        plt.legend()
        
        plt.figure()
        plt.title('Phase at field = %s'%(fields[i]))
        
    #    plt.plot(freqs_all[i],np.angle(datas[i]), label = 'data')
        plt.plot(freqs_all[i],np.angle(model_data),label = 'model')
        plt.legend()
        
        plt.figure()
        plt.title('IQ at field = %s'%(fields[i]))
    #    plt.plot(np.real(datas[i]),np.imag(datas[i]), label = 'data')
        plt.plot(np.real(model_data),np.imag(model_data),label = 'model')
        plt.legend()
        
HH = np.zeros((len(fields),len(freqs_all)))
for i in range(len(fields)):
    model_data = S31_model(param,fields[i],freqs_all)[1]
    HH[i] = np.abs(model_data)


        
    
#str_params = 'wa,wb,ga,ga2,wp,k,spl,wn,gamma1,gamma2,gamma4,A,phi,i_off,r_off'
#str_params = str_params.split(',')
#for i in range(len(param)):
#    print(str_params[i] + ' = ' + str(param[i]))

plt.figure()
plt.title('Theory S31 k = %sMHz'%(gamma4*1000))
plt.xlabel('Fields(T)')
plt.ylabel('Frequency(GHz)')

plt.pcolormesh(fields,freqs_all,np.transpose(20*np.log10(HH)), vmax = -30, vmin = -80)
plt.colorbar().set_label('(dB)')
plt.show()



















