# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 17:14:38 2020

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

fields = np.linspace(0,0,1)
limit_for_off = 1
delta = fields[0]

def S31_resid(params,x,y):
    param = params.valuesdict()
    wa = param['wa']
    wb = param['wb']
    ga = param['ga']
    ga2 = param['ga2']
    gb = ga
    gb2 = ga2
    wp = param['wp']
    k = param['k']
    delta = fields[0]
    spl = param['spl']
    wp = param['wp']
    wn = param['wn']
    gamma1 = param['gamma1']
    gamma2 = param['gamma2']
    gamma3 = param['gamma3']
    gamma4 = param['gamma4']
    A = param['A']
    phi = param['phi']
    i_off = param['i_off']
    r_off = param['r_off']
    ani_diag = param['ani_diag']
    null_field = param['null_field']
    
    identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
    out_3 = []
    wpp = wp + ani_diag*(1-np.abs(delta/null_field))
    wnn = wn - ani_diag*(1-np.abs(delta/null_field))
    wpn = 1j*delta*k+spl*(1-np.abs(delta/null_field))
    wnp = -1j*delta*k+spl*(1-np.abs(delta/null_field))
    H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wpp,wpn],[ga2,gb2,wnp, wnn]])  
    # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
    b_in = np.array([1,0,0,0]).reshape(4,1)
    for i in range(len(x)):
        
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
    return np.sqrt((np.real(out_3_)-np.real(y))**2+(np.imag(out_3_)-np.imag(y))**2)

''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
hdf5_name = '20210105cooldown_circulator_VNA - Copy.hdf5'

date = '20210109'
time_ = '005144'
#time_ = '192458'
#experiment = 'Power_Sweep_VNA'

#fields = np.linspace(-.05,-.05,1)

#fields = np.linspace(0.05, 0.002,13)

''' Primary x axis and secondary if 2d'''
#x_key = 'freqs'
#x2_key = 'powers'



j = 0 #index of the power from the color plot used 0 = lowest power

data_len = 1601


f = h5.File(filepath + hdf5_name, 'r')

limit_for_off = 1
k = 0
#freq1 = np.zeros([nrows,len(fields)])
#freq2 = np.zeros([nrows,len(fields)])
#freq1_err = np.zeros([nrows,len(fields)])
#freq2_err = np.zeros([nrows,len(fields)])  
r_off = np.zeros(1)
i_off = np.zeros(1)

title = str(time_) + '_Power_Sweep_VNA'
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

datas = real[j] + 1j * imag[j]
if np.max(np.abs(datas)) < limit_for_off:
    r_off[k] = (datas[0].real+ datas[-1].real)/2
    i_off[k] = (datas[0].imag+ datas[-1].imag)/2#, vary = False)


        
fix_vary = False
params = lmfit.Parameters()
params.add('gamma1',value = .00015, min = 0, max = .001, vary = fix_vary)
params.add('gamma2',value = .0008, min = 0, max = .005, vary = fix_vary)
params.add('gamma3',value = 0, vary = False)
params.add('gamma4',value = .320, min = 0, vary = fix_vary)
params.add('wb',value = 10.804, vary = False)
params.add('wa',value = 10.8104, vary = False)
params.add('wp',value = 10.710, vary = True)
params.add('wn',value = 10.840, vary = True)
params.add('ga',value = .021, vary = fix_vary)
params.add('ga2',value = .01, vary = fix_vary)
params.add('spl',value = .075, vary = fix_vary)
params.add('A',value = .16, vary = fix_vary)
params.add('r_off', value = .00061, vary = fix_vary)
params.add('i_off', value = -.00017, vary = fix_vary)
params.add('ani_diag', value = .075, vary = fix_vary)
params.add('null_field', value = .05, vary = False)


# params.add('A',value = .01, min = .001, max = .1, vary = fix_vary )
# params.add('delta',value = 0, vary = False, vary = fix_vary)
params.add('k',value = 8, vary = False)
params.add('phi',value = 2, vary = True)
#freqs = freq/1e9
print('data seze %s'%(len(datas)))
result = lmfit.minimize(S31_resid, params, args=(freq, datas))
lmfit.report_fit(result.params)

gamma1 = result.params['gamma1'].value
gamma2 = result.params['gamma2'].value
gamma3 = result.params['gamma3'].value
gamma4 = result.params['gamma4'].value
wa = result.params['wa'].value
wb = result.params['wb'].value
wp = result.params['wp'].value
wn = result.params['wn'].value
ga = result.params['ga'].value
ga2 = result.params['ga2'].value
gb = 1*ga
gb2 = 1*ga2
spl = result.params['spl'].value
phi = result.params['phi'].value
i_off = result.params['i_off'].value
r_off = result.params['r_off'].value
ani_diag = result.params['ani_diag'].value
null_field = result.params['null_field'].value

# delta = result.params['delta'].value
A=result.params['A'].value
k = result.params['k'].value
def S31_model(gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,delta,A,k,phi):
    w = freq/1e9
    identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
    out_3 = []
    wpp = wp + ani_diag*(1-np.abs(delta/null_field))
    wnn = wn - ani_diag*(1-np.abs(delta/null_field))
    wpn = 1j*delta*k+spl*(1-np.abs(delta/null_field))
    wnp = -1j*delta*k+spl*(1-np.abs(delta/null_field))
    
    H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wpp,wpn],[ga2,gb2,wnp, wnn]])   
    # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
    b_in = np.array([1,0,0,0]).reshape(4,1)
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


model_data = S31_model(gamma1,gamma2,gamma3,gamma4,wa,wb,wp,wn,ga,ga2,gb,gb2,spl,fields[0],A,k,phi)[0] + r_off + 1j*i_off



    
plt.figure()
plt.title('Magnitude at field = %s'%(fields[0]))

plt.plot(freq,np.abs(datas), label = 'data')
plt.plot(freq,np.abs(model_data),label = 'model')
plt.legend()

plt.figure()
plt.title('Phase at field = %s'%(fields[0]))

plt.plot(freq,np.angle(datas), label = 'data')
plt.plot(freq,np.angle(model_data),label = 'model')
plt.legend()

plt.figure()
plt.title('IQ at field = %s'%(fields[0]))
plt.plot(np.real(datas),np.imag(datas), label = 'data')
plt.plot(np.real(model_data),np.imag(model_data),label = 'model')
plt.legend()
    
    
























