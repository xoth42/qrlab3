# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 13:57:28 2020

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



def S31_resid(params,x,y):
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
    k_in1 = param['k_in1']
    k_in2 = param['k_in2']
    A = param['A']
    phi = param['phi']
    ioff = param['ioff']
    roff = param['roff']
    identity = np.array([[1,0],[0,1]])
    gamma = np.array([[np.sqrt(k_in1),0],[0,np.sqrt(k_in2)]])
    out_2 = []
#    Matrix_1 = np.array([[ga*(spl+1j*delta*k)*ga2 + ga*(1j*gamma4/2+)],[ga2,wn-1j*gamma4/2]])

    # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
    b_in = np.array([1,0]).T
    for i in range(len(x)):
        Matrix_1 =x[i]*identity -np.array([[wa-1j*gamma1/2, 0],[0,wb - 1j*gamma2/2]])- (1/(-spl**2-(delta*k)**2+1j*gamma4*x[i]/2+x[i]**2-x[i]*wn-1j*gamma4*wp/2-x[i]*wp+wn*wp))*np.array([[ga*((spl+1j*delta*k)*ga2 + ga*(1j*gamma4/2+x[i]-wn))+ga2*((spl-1j*delta*k)*ga+ga2*(x[i]-wp)),-2*1j*ga*ga2*delta*k-ga*(ga*(1j*gamma4/2+x[i]-wn))+ga2**2*(x[i]-wp)],
                          [2*1j*ga*ga2*delta*k-ga*(ga*(1j*gamma4/2+x[i]-wn))+ga2**2*(x[i]-wp),-ga*((spl+1j*delta*k)*ga2 - ga*(1j*gamma4/2+x[i]-wn))+ga2*(-(spl-1j*delta*k)*ga+ga2*(x[i]-wp))]])

        a = -1j*linalg.inv(Matrix_1).dot(gamma.dot(b_in))
        
        out_2.append(A*np.exp(1j*phi)*(np.sqrt(k_in2)*a[1]) + roff + 1j * ioff)
#    S31_mag = abs(np.array(out_3))
#    S31_phase = np.angle(np.array(out_3))
#    S31 = np.concatenate((S31_mag,S31_phase))
    S21 = np.asarray(out_2)
    return np.sqrt((S21.real-y.real)**2+(S21.imag-y.imag)**2)


''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#filepath = 'C:\\Users\\Wang_Lab\\Downloads\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
#hdf5_name = '0626cooldown_circualtor_VNA - Copy.hdf5'
hdf5_name = '0626cooldown_circualtor_VNA - Copy.hdf5'

#date = '20191126'
#time = '190211'
date = '20200702'
#time = '120736' #-.05T S21
time = '043455'
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

data = real-1j*imag
magnitude = abs(data)
data_mag = magnitude
phase = np.angle(data)
data_phase = phase

fix_vary = False
params = lmfit.Parameters()


#params.add('gamma4',value = .08,min = .01, max = 1,vary = fix_vary)
#params.add('wb',value = 10.8056, vary = False)
#params.add('wa',value = 10.8105, vary = False)
#params.add('wp',value = 10.55, min = 10.4, max = 11, vary = fix_vary)
#params.add('wn',value = 10.8, min = 10.5, max = 11.1, vary = False)
#params.add('ga',value = .04746, min = -.06, max = .06,vary = fix_vary)
#params.add('ga2',value = .004052, min = -.03, max = .03, vary = fix_vary)
#params.add('spl',value = -0.0017, min = -.2, max = .2, vary = fix_vary)
#params.add('k_in1', value = .0001, min = .00001, max = .001, vary = False)
#params.add('k_in2', value = .0001, min = .00001, max = .001, vary = False)
#params.add('gamma1', value = .0001, min = .0001, max = .001, vary = fix_vary)
#params.add('gamma2', value = .0016, min = .00001, max = .01, vary = fix_vary)
#params.add('A',value = .14,min = .01, max = 1,vary = fix_vary)
#params.add('delta',value = -.05, vary = False)
#params.add('k',value =8,min = 6, max = 10, vary = fix_vary)
#params.add('phi',value = 2.3,min = -5, max = 5,vary = False)
#params.add('ioff',value = 0,min = -.1*np.max(abs(imag)), max = .1*np.max(abs(imag)), vary = False)
#params.add('roff',value = 0,min = -.1*np.max(abs(real)), max = .1*np.max(abs(real)),vary = False)

params.add('gamma4',value = .068,vary = fix_vary)
params.add('wb',value = 10.8056, vary = False)
params.add('wa',value = 10.8105, vary = False)
params.add('wp',value = 10.55, vary = False)
params.add('wn',value = 10.8, vary = False)
params.add('ga',value = .05111,vary = fix_vary)
params.add('ga2',value = .002819, vary = fix_vary)
params.add('spl',value = .08, vary = fix_vary)
params.add('k_in1', value = .0001, min = 0, vary = False)
params.add('k_in2', value = .0001, min = 0, vary = False)
params.add('gamma1', value = .0001, vary = False)
params.add('gamma2', value = .0016, vary = False)
params.add('A',value = .28,vary = fix_vary)
params.add('delta',value = 0, vary = False)
params.add('k',value =8, vary = False)
params.add('phi',value = 1.9,vary = False)
params.add('ioff',value = 0, vary = True)
params.add('roff',value = 0,vary = True)

freqs = freq/1e9
result = lmfit.minimize(S31_resid, params, args=(freqs, data))
lmfit.report_fit(result.params)

gamma1 = result.params['gamma1'].value
gamma2 = result.params['gamma2'].value
#gamma3 = result.params['gamma3'].value
gamma4 = result.params['gamma4'].value
wa = result.params['wa'].value
wb = result.params['wb'].value
k_in1 = result.params['k_in1'].value
k_in2 = result.params['k_in2'].value
wp = result.params['wp'].value
wn = result.params['wn'].value
ga = result.params['ga'].value
ga2 = result.params['ga2'].value
#k_in = result.params['k_in'].value
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
gamma = np.array([[np.sqrt(k_in1),0],[0,np.sqrt(k_in2)]])
out_2 = []
#    Matrix_1 = np.array([[ga*(spl+1j*delta*k)*ga2 + ga*(1j*gamma4/2+)],[ga2,wn-1j*gamma4/2]])
x = w
# a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
b_in = np.array([1,0]).T
for i in range(len(x)):
    Matrix_1 =x[i]*identity -np.array([[wa-1j*gamma1/2, 0],[0,wb - 1j*gamma2/2]])- (1/(-spl**2-(delta*k)**2+1j*gamma4*x[i]/2+x[i]**2-x[i]*wn-1j*gamma4*wp/2-x[i]*wp+wn*wp))*np.array([[ga*((spl+1j*delta*k)*ga2 + ga*(1j*gamma4/2+x[i]-wn))+ga2*((spl-1j*delta*k)*ga+ga2*(x[i]-wp)),-2*1j*ga*ga2*delta*k-ga*(ga*(1j*gamma4/2+x[i]-wn))+ga2**2*(x[i]-wp)],
                          [2*1j*ga*ga2*delta*k-ga*(ga*(1j*gamma4/2+x[i]-wn))+ga2**2*(x[i]-wp),-ga*((spl+1j*delta*k)*ga2 - ga*(1j*gamma4/2+x[i]-wn))+ga2*(-(spl-1j*delta*k)*ga+ga2*(x[i]-wp))]])

    a = -1j*linalg.inv(Matrix_1).dot(gamma.dot(b_in))
    
    out_2.append(A*np.exp(1j*phi)*(np.sqrt(k_in2)*a[1]) + roff + 1j * ioff)
#    S31_mag = abs(np.array(out_3))
#    S31_phase = np.angle(np.array(out_3))
#    S31 = np.concatenate((S31_mag,S31_phase))

S21_mag = abs(np.array(out_2))
S21_phase = np.angle(np.array(out_2))
S21 = np.concatenate((S21_mag,S21_phase))
S21_mag = abs(np.array(out_2))
S21_phase = np.angle(np.array(out_2))

#S31_eq_model = S31_eq(k_in,gamma2,gamma4,wa,wb,wn,wp,ga,ga2,spl+k*delta,w)
#S31_eq_model = (A*np.exp(1j*phi)*S31_eq_model +roff +1j*ioff)/50
#S31_eq_model_mag = abs(S31_eq_model)
#S31_eq_model_phase = np.angle(S31_eq_model)

plt.figure()
plt.title('Magnitude')
plt.plot(freqs,data_mag, label = 'data')
plt.plot(freqs,S21_mag,label = 'model mat')
#plt.plot(freqs,S31_eq_model_mag, label = 'model eq')

plt.legend()

plt.figure()
plt.title('Phase')
plt.plot(freqs,data_phase, label = 'data')
plt.plot(freqs,S21_phase,label = 'model mat')
#plt.plot(freqs,S31_eq_model_phase, label = 'model eq')

plt.legend()

plt.figure()
plt.title('IQ')
plt.plot(data.real,data.imag,label = 'data')
plt.plot(S21_mag*np.cos(S21_phase),S21_mag*np.sin(S21_phase),label = 'model')

plt.legend()

