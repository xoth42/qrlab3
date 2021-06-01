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

#''' Path to the .hdf5 file '''
##filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
#filepath = 'C:\_Data\\'
##hdf5_name = 'VNAtestJan30.hdf5'
##hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
#hdf5_name = '1126cooldown_circulator_VNA - Copy.hdf5'
#
#date = '20201201'
##time = '233434'
##experiment = 'Power_Sweep_VNA'
#
##fields = np.linspace(-.05,-.05,1)
#fields = np.linspace(-0.05,0,1)
##fields = np.linspace(0.05, 0.002,13)
#
#''' Primary x axis and secondary if 2d'''
##x_key = 'freqs'
##x2_key = 'powers'
#
#
#
#j = 0 #index of the power from the color plot used 0 = lowest power
#
#data_len = 1601
#itime = 0 #index of the field being analyzed so you can save your place and work on only fitting a few fields at a time
#
#if itime == 0:
#    datas = np.zeros([len(fields),data_len],dtype = complex)
#
#f = h5.File(filepath + hdf5_name, 'r')
#
#limit_for_off = 1
#k = 0
##freq1 = np.zeros([nrows,len(fields)])
##freq2 = np.zeros([nrows,len(fields)])
##freq1_err = np.zeros([nrows,len(fields)])
##freq2_err = np.zeros([nrows,len(fields)])  
#r_off = np.zeros(len(fields))
#i_off = np.zeros(len(fields))
#for i, title in enumerate(f[date].keys()):
##    print int(title[0:6])
##    print int(title[0:6]) <= 020617
#    if int(title[0:6]) <= int('105043') and int(title[0:6]) > int('105041') and title[7:12] =='Power':
##    if int(title[0:6]) <= int('192459') and int(title[0:6]) > int('192457') and title[7:12] =='Power':
#        print title
#
#
#
#        x_key = 'freqs'
#        #x2_key = 'powers'
#        exp = f[date][title]
##    exp = f['/' + date1 + '/' + time + '_' + experiment]
#        y_keys = exp.keys()
#        #print(y_keys)
#        
#        #y_keys.remove(x_key)
#        #y_keys.remove(x2_key)
#        freq = exp['freqs'].value
#        #current = exp['currents'].value
##        powers = exp['powers'].value
#        real = exp['realS21'].value
#        imag = exp['imaginaryS21'].value
#        
#        datas[itime] = real[j] + 1j * imag[j]
#        if np.max(np.abs(datas)) < limit_for_off:
#            r_off[k] = (datas[itime][0].real+ datas[itime][-1].real)/2
#            i_off[k] = (datas[itime][0].imag+ datas[itime][-1].imag)/2#, vary = False)
#
#        itime = itime + 1
#        k += 1
#
#    
data_len = 1601    
gamma1 = .0004
gamma2 = .0012
gamma3 = 0
gamma4 = .2577
wa = 10.808
wb = 10.804
wp = 10.77
wn = 10.825
ga = .021
ga2 = -.00592
gb = ga
gb2 = ga2
spl = -.0684
A = .1
k = 8
phi = 2.15
freq = np.linspace(10e9,11e9,data_len)
field = 0.05
lower_bnd = -np.inf
upper_bnd = 8


def S21_model_r(w1,w2,gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,delta,A,k,phi):
#    w = freq/1e9
    identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
#    out_3 = []
    H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*delta*k+spl],[ga2,gb2,-1j*delta*k+spl, wn]])  
    # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
    b_in = np.array([1,0,0,0]).reshape(4,1)
#    for i in range(len(w)):
        
    big_matrix1 = (w1*identity - H + 1j*gamma/2)
    
    a1 = -1j*np.matmul(np.matmul(la.inv(big_matrix1),np.sqrt(gamma)),b_in)
    
    r1 = A*np.exp(-1j*phi)*(np.sqrt(gamma2)*a1[1][0])
    H2 = np.array([[wa,0,ga,ga2],[0,wb-0.7,-gb,gb2],[ga,-gb,wp,1j*delta*k+spl],[ga2,gb2,-1j*delta*k+spl, wn]])   
    big_matrix2 = (w2*identity - H2 + 1j*gamma/2)
    
    a2 = -1j*np.matmul(np.matmul(la.inv(big_matrix2),np.sqrt(gamma)),b_in)
    
    r2 = A*np.exp(-1j*phi)*(np.sqrt(gamma2)*a2[1][0])
    
    fac = 1j/(w1-w2+.0000001)*(np.exp(-1j*(w1-w2)*140)-1)
    
    final = np.real(r1*r2*fac)
        
    return final
   
    
def S21_model_i(w1,w2,gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,delta,A,k,phi):
#    w = freq/1e9
    identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
#    out_3 = []
    H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*delta*k+spl],[ga2,gb2,-1j*delta*k+spl, wn]])  
    # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
    b_in = np.array([1,0,0,0]).reshape(4,1)
#    for i in range(len(w)):
        
    big_matrix1 = (w1*identity - H + 1j*gamma/2)
    
    a1 = -1j*np.matmul(np.matmul(la.inv(big_matrix1),np.sqrt(gamma)),b_in)
    
    r1 = A*np.exp(-1j*phi)*(np.sqrt(gamma2)*a1[1][0])
    
    H2 = np.array([[wa,0,ga,ga2],[0,wb-0.7,-gb,gb2],[ga,-gb,wp,1j*delta*k+spl],[ga2,gb2,-1j*delta*k+spl, wn]])   
    big_matrix2 = (w2*identity - H2 + 1j*gamma/2)
        
    
    a2 = -1j*np.matmul(np.matmul(la.inv(big_matrix2),np.sqrt(gamma)),b_in)
    
    r2 = A*np.exp(-1j*phi)*(np.sqrt(gamma2)*a2[1][0])
    
    fac = 1j/(w1-w2+.000001)*(np.exp(-1j*(w1-w2)*140)-1)
    
    final = np.imag(r1*r2*fac)
        
    return final
#    out_3_ = np.conj(out_3)
#    S21_mag = abs(np.array(out_3_))
#    S21_phase = np.angle(np.array(out_3_))
#    print(out_3[0])
#    print(out_3_[0])
#    return [out_3_,S21_mag,S21_phase]



#model_data = np.zeros(data_len,dtype = complex)
#model_data = S21_model(gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,field,A,k,phi)[0]
#freqs = np.linspace(10,11,16001)
#
#S21_r = np.zeros(16001)
#S21_i = np.zeros(16001)
#
#for i in range(len(freqs)):
#    S21_r[i] = S21_model_r(freqs[i],gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,field,A,k,phi)
#    S21_i[i] = S21_model_i(freqs[i],gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,field,A,k,phi)

def S21_model(w1,gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,delta,A,k,phi):
#    w = freq/1e9
    final = np.zeros(len(freq_tot),dtype = complex)
    for i in range(len(w1)):
        identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
        gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
    #    out_3 = []
        H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*delta*k+spl],[ga2,gb2,-1j*delta*k+spl, wn]])  
        # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
        b_in = np.array([1,0,0,0]).reshape(4,1)
    #    for i in range(len(w)):
            
        big_matrix1 = (w1[i]*identity - H + 1j*gamma/2)
        
        a1 = -1j*np.matmul(np.matmul(la.inv(big_matrix1),np.sqrt(gamma)),b_in)
        
        r1 = A*np.exp(-1j*phi)*(np.sqrt(gamma2)*a1[1][0])
        
        final[i] = r1
    
    return final
    


#int_model_r = integrate.nquad(S21_model_r, [[lower_bnd, upper_bnd],[lower_bnd,upper_bnd]], args = (gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,field,A,k,phi))
#
#int_model_i = integrate.nquad(S21_model_i, [[lower_bnd, upper_bnd],[lower_bnd,upper_bnd]], args = (gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,field,A,k,phi))
#
#
#print (int_model_r[0] + 1j*int_model_i[0])
#
#
#def twolorentzians_r(w1,w2,k,chi):
#    model = 1/(1j*w1 + k)/(-1j*(w2-chi)+k)*(np.exp(-1j*(w1-w2)*140)-1)/(w1-w2+.0000000001)
#    return np.real(model)
#       
#def twolorentzians_i(w1,w2,k,chi):
#    model = 1/(1j*w1 + k)/(-1j*(w2-chi)+k)*(np.exp(-1j*(w1-w2)*140)-1)/(w1-w2+.0000000001)
#    return np.imag(model)     
#
#low = .05
#high = np.inf
#int_lorentz_real = integrate.nquad(twolorentzians_r,[[low,high],[low,high]], args = (.001,.0007))
#int_lorentz_imag = integrate.nquad(twolorentzians_i,[[low,high],[low,high]], args = (.001,.0007))
#
#
#print(int_lorentz_real,int_lorentz_imag)
#
#
#def test(w, sigma):
#    model = np.exp(-w**2/sigma**2)
#    return model
#    
#low = -np.inf
#high = np.inf    
#int_test = integrate.quad(test,low,high, args = (0.001))
#
#print(int_test)

#fields = np.linspace(-0.05,.05,11)
fields = np.linspace(-0.05,0.05,11)

#freq_low = np.linspace(10.7,10.78,401)
#freq_mid = np.linspace(10.78,10.83, 1601)
#freq_high = np.linspace(10.83,10.9, 401)
#freq_tot = np.concatenate((freq_low,freq_mid,freq_high))

freq_low = np.linspace(10.3,10.78,15361)
freq_mid = np.linspace(10.78,10.83, 10001)
freq_high = np.linspace(10.83,11.3, 15041)
freq_tot = np.concatenate((freq_low,freq_mid,freq_high))

#freq_tot = freq_mid
freq_tot = np.linspace(10.80,10.815,121)


chi = .0015
tf = 140

S21_g = np.zeros([len(fields),len(freq_tot)],dtype = complex)
S21_e = np.zeros([len(fields),len(freq_tot)],dtype = complex)

for i in range(len(fields)):
    S21_g[i] = S21_model(freq_tot,gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,fields[i],A,k,phi)
    S21_e[i] = S21_model(freq_tot,gamma1,gamma2,gamma3,gamma4,wa,wb-chi,wp,wn,ga,ga2,gb,gb2,spl,fields[i],A,k,phi)
#    S21_g[i] = data[0]
#    S21_e[i] = data[i + 1] *2 - data[0]

def int_model(S21_g,S21_e):
#    data_g = np.concatenate((data_lowg,data_midg,data_highg))
#    data_e = np.concatenate((data_lowe,data_mide,data_highe))   
    data_g = S21_g
    data_e = S21_e
    I_r = np.zeros((len(freq_tot)))
    I_i = np.zeros((len(freq_tot)))
    for i in range(len(freq_tot)):
        c_in_wg = (1 - np.exp(1j * (freq_tot - 10.811)*12))/((freq_tot - 10.811000000000001))
        c_in_we = (1 - np.exp(-1j * (freq_tot[i] - 10.811)*12))/((freq_tot[i] - 10.811000000000001))
        integrand = c_in_wg * c_in_we*(data_e[i])*np.conjugate(data_g)*(np.exp(-1j*(freq_tot[i]-freq_tot)*tf)-1)/((freq_tot[i]-freq_tot+.000000000000001))
        I_r[i] = np.trapz(np.real(integrand),freq_tot)
        I_i[i] = np.trapz(np.imag(integrand),freq_tot)
    final_r = np.trapz(I_r,freq_tot)
    final_i = np.trapz(I_i, freq_tot)
    return [final_r,final_i]
    

deph = np.zeros(len(fields))
stark = np.zeros(len(fields))

for i in range(len(fields)):
    
    deph[i] = int_model(S21_g[i],S21_e[i])[0]
    stark[i] = int_model(S21_g[i],S21_e[i])[1]

plt.figure('dephasing')
plt.title('dephasing over field')
plt.xlabel('Field (T)')
plt.ylabel('dephasing at 140 ns')
plt.plot(fields,deph/1.1, label = 'dephasing, 10000pts/1.1')
plt.legend()


plt.figure()
plt.title('stark shift over field')
plt.xlabel('Field (T)')
plt.ylabel('stark shift at 140 ns')
plt.plot(fields,stark, label = 'stark shift')
plt.legend()

plt.figure()
plt.plot(fields, np.abs(deph +1j*stark))























