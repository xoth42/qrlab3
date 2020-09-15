# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 10:56:29 2020

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 15:21:40 2020

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 19:01:25 2020

@author: svgwi
"""


import os
import time
import lmfit 



import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
import json
from matplotlib import gridspec
from scipy import linalg


# def S31(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w):
#     A=gam1/2-1j*(w-w1)
#     B=gam2/2-1j*(w-w2)
#     C=gam3/2-1j*(w-w3)
#     D=-1j*(w-w4)
#     s31= gam3*gam1*abs((B*D*j1-B*delta*j2+2*j1*j2**2)/(B*D*j1**2+B*C*j2**2+4*j1**2*j2**2+A*(B*(C*D+delta**2)+D*j1**2+C*j2**2)))**2
#     return s31
# def S31_phase(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w):
#     A=gam1/2-1j*(w-w1)
#     B=gam2/2-1j*(w-w2)
#     C=gam3/2-1j*(w-w3)
#     D=-1j*(w-w4)
#     s31_raw = 1j*(B*D*j1-B*delta*j2+2*j1*j2**2)/(B*D*j1**2+B*C*j2**2+4*j1**2*j2**2+A*(B*(C*D+delta**2)+D*j1**2+C*j2**2))
#     s31_phase = []
#     for i in range(len(w)):
#         s31_phase.append(cmath.phase(s31_raw[i]))
#     return s31_phase

def S31_freqs(params,x,y):
    param = params.valuesdict()
    wa = param['wa']
    wb = param['wb']
    ga = param['ga']
    ga2 = param['ga2']
#    gb = ga
#    gb2 = ga2
    wp = param['wp']
    k = param['k']
    delta = param['delta']
    spl = param['spl']
    wp = param['wp']
    wn = param['wn']
    gamma1 = param['gamma1']
    gamma2 = param['gamma2']
    gamma4 = param['gamma4']
    k_in = param['k_in']
    A = param['A']
    phi = param['phi']
    ioff = param['ioff']
    roff = param['roff']
    identity = np.array([[1,0],[0,1]])
    gamma = np.array([[np.sqrt(k_in),0],[0,np.sqrt(gamma4)]])
    Matrix_1 = np.array([[wa-1j*gamma1/2,ga2],[ga2,wn-1j*gamma4]])
    Matrix_2 = np.array([[0,ga],[ga2,spl + 1j*k*delta]])
#    Matrix_3 = np.array([[-wb+1j*gamma2/2+x[i],ga],[ga,x[i]-wp]])
    Matrix_4 = np.array([[0,ga2],[ga,spl-1j*k*delta]])
    # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
    b_in = np.array([1,0]).T
    fields = np.linspace(0,.05,26)
    low_freq = []
    high_freq = []
    for j in range(len(fields)):
        out_3 = []
        for i in range(len(x)):
            Matrix_3 = np.array([[-wb+1j*gamma2/2+x[i],ga],[ga,x[i]-wp]])
            a = linalg.inv(x[i]*identity-(Matrix_1 + (Matrix_2.dot(linalg.inv(Matrix_3))).dot(Matrix_4))).dot(gamma.dot(b_in))
            
            out_3.append(A*np.exp(1j*phi)*(np.sqrt(gamma4)*a[1]) + roff + 1j * ioff)
       max_ freqs = scipy.signal.find_peaks(out_3)
#    S31_mag = abs(np.array(out_3))
#    S31_phase = np.angle(np.array(out_3))
#    S31 = np.concatenate((S31_mag,S31_phase))
    S31 = np.asarray(out_3)
    return np.sqrt((S31.real-y.real)**2+(S31.imag-y.imag)**2)


''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
hdf5_name = '0827cooldown_circualtor_VNA.hdf5'

date = '20191126'
time = '190211'
experiment = 'Power_Sweep_VNA'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]
y_keys = exp.keys()
#print(y_keys)

#y_keys.remove(x_key)
#y_keys.remove(x2_key)
freq = exp['freqs'][()]
#current = exp['currents'].value
powers = exp['powers'][()]
real = exp['realS21'][()][0]
imag = exp['imaginaryS21'][()][0]

magnitude = abs(real+1j*imag)
data_mag = magnitude
phase = np.angle(real-1j*imag)
data_phase = phase
data = real-1j*imag
fix_vary = True
params = lmfit.Parameters()
params.add('gamma1',value = .000,min = 0, vary = False)
params.add('gamma2',value = .000,min = 0, vary = False)
#params.add('gamma3',value = 0.0000001, vary = fix_vary)
params.add('gamma4',value = .455,min = 0,vary = fix_vary)
params.add('wa',value = 10.7101, vary =fix_vary)
params.add('wb',value = 10.7132, vary = fix_vary)
params.add('wp',value = 10.619, vary = False)
params.add('wn',value = 10.9762,vary = fix_vary)
params.add('ga',value = .0189,vary = fix_vary)
params.add('ga2',value = .0117,vary = fix_vary)
params.add('spl',value = .1,vary = fix_vary)
params.add('k_in',value = .00009,min = 0,vary = fix_vary)
params.add('A',value = .307,vary = fix_vary)
params.add('delta',value = 0.05, vary = False)
params.add('k',value = 8,vary = fix_vary)
params.add('phi',value = 1.31,vary = fix_vary)
params.add('ioff',value = 0,vary = fix_vary)
params.add('roff',value = 0,vary = fix_vary)
freqs = freq/1e9
result = lmfit.minimize(S31_resid, params, args=(freqs, data))
lmfit.report_fit(result.params)

gamma1 = result.params['gamma1'].value
gamma2 = result.params['gamma2'].value
#gamma3 = result.params['gamma3'].value
gamma4 = result.params['gamma4'].value
wa = result.params['wa'].value
wb = result.params['wb'].value
wp = result.params['wp'].value
wn = result.params['wn'].value
ga = result.params['ga'].value
ga2 = result.params['ga2'].value
k_in = result.params['k_in'].value
gb = ga
gb2 = ga2
spl = result.params['spl'].value
delta = result.params['delta'].value
A=result.params['A'].value
k = result.params['k'].value
phi = result.params['phi']
roff = result.params['roff']
ioff = result.params['ioff']
w = freqs
#identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
#gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
#out_3 = []
#H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*delta*k+spl],[ga2,gb2,-1j*delta*k+spl, wn]])  
## a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
#b_in = np.array([1,0,0,0]).reshape(4,1)
#for i in range(len(w)):
#    
#    big_matrix = (w[i]*identity - H + 1j*gamma/2)
#    
#    a = -1j*la.inv(big_matrix)@np.sqrt(gamma)@b_in
#    
#    out_3.append(A*np.exp(1j*phi)*(np.sqrt(gamma4)*a[3][0]))
identity = np.array([[1,0],[0,1]])
gamma = np.array([[np.sqrt(k_in),0],[0,np.sqrt(gamma4)]])
out_3 = []
Matrix_1 = np.array([[wa-1j*gamma1/2,ga2],[ga2,wn-1j*gamma4]])
Matrix_2 = np.array([[0,ga],[ga2,spl + 1j*k*delta]])
#    Matrix_3 = np.array([[-wb+1j*gamma2/2+x[i],ga],[ga,x[i]-wp]])
Matrix_4 = np.array([[0,ga2],[ga,spl-1j*k*delta]])
# a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
b_in = np.array([1,0]).T
for i in range(len(w)):
    Matrix_3 = np.array([[-wb+1j*gamma2/2+w[i],ga],[ga,w[i]-wp]])
    a = linalg.inv(w[i]*identity-(Matrix_1 + (Matrix_2.dot(linalg.inv(Matrix_3))).dot(Matrix_4))).dot(gamma.dot(b_in))
    
    out_3.append(A*np.exp(1j*phi)*(np.sqrt(gamma4)*a[1])+ roff + 1j * ioff)
S31_mag = abs(np.array(out_3))
S31_phase = np.angle(np.array(out_3))
S31 = np.concatenate((S31_mag,S31_phase))
S31_mag = abs(np.array(out_3))
S31_phase = np.angle(np.array(out_3))
plt.figure()
plt.title('Magnitude')
plt.plot(freqs,data_mag, label = 'data')
plt.plot(freqs,S31_mag,label = 'model')

plt.legend()

plt.figure()
plt.title('Phase')
plt.plot(freqs,data_phase, label = 'data')
plt.plot(freqs,S31_phase,label = 'model')

plt.legend()

plt.figure()
plt.title('IQ')
plt.plot(real,-imag,label = 'data')
plt.plot(S31_mag*np.cos(S31_phase),S31_mag*np.sin(S31_phase),label = 'model')

plt.legend()

