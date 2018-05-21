# -*- coding: utf-8 -*-
"""
Created on Mon Jan 08 14:50:08 2018

@author: WangLab
"""

import lmfit

import numpy as np
import matplotlib.pyplot as pl

# Read the array from file
filename = 'text_0.5mm_270.0_300.0_0.05'
new_data = np.loadtxt(r'%s.txt'%(filename))
print new_data.shape
# Note that this returned a 2D array!
# However, going back to 3D is easy if we know the 
# original shape of the array

size = new_data.shape[1]
new_data = new_data.reshape((4,1601,size))

X = new_data[0]
Y = new_data[1]
Z = new_data[2]

Z = np.transpose(Z)
Y = np.transpose(Y)


 #if specific trace is needed
 
m = 292  #the initial magnetic field you want
M = 293  #the final magnetic field you want
step = 0.05
#f = open('parameters_per_310-345-0.2_V1.txt','w')
#f.close
kappa_a =[]
pl.figure()
while m <= M:
    for i in range(size):
        if X[0][i] < m:
             i = i + 1
        else:
            break
     
     
    z = Z[i]
     
    freq = Y[0]

#==============================================================================
#      pl.plot(freq, z)
#      pl.xlabel('frequency(GHZ)')
#      pl.ylabel('dB')
#      pl.show()
#      z = z[:,None].T
#      freq = freq[:,None].T
#      trace = np.concatenate([freq, z]).T
#      np.savetxt(r'C:\qrlab\FMR\%smT.txt' %(X[0][i]), trace , delimiter=",") 
#==============================================================================

#==============================================================================
#     x = freq
#     y = z
#     x = x * 1000000000
#     
#     ##plotting s21^2 to get the linewidth of the cavity and YIG mode
#     #y = np.power(10,y/10.0)
#     #pl.plot(x, y)
#     
#     y = np.power(10,y/20.0)
#     
#     pl.figure(m)
#     pl.plot(x, y)
#     
#     def S21(params, x, y):
#         est = np.sqrt(params['kappa1']*params['kappa2'])
#         est = est/(1j*(x-params['omega_c'])-(params['kappa1']+params['kappa2']+params['kappa_int'])/2.0 + params['g'] **2 /(1j*(x-params['omega_FMR'])-params['gamma_m']/2.0))
#         return y - abs(est)
#         
#     params = lmfit.Parameters()
#     params.add('kappa1', value= 2.1305e+05, min = 0)
#     params.add('kappa2', value=1664.58721, min = 0)
#     params.add('omega_c', value= 8.5040e+09)
#     params.add('kappa_int', value=3.0022e+06, min = 0)
#     params.add('g',value= 24.75e6)
#     params.add('omega_FMR',value = 0.63e9 + m*0.027e9)
#     params.add('gamma_m', value = 3e6, min=0)
#     
#     result = lmfit.minimize(S21, params, args=(x, y))
#     lmfit.report_fit(result.params)
#     y=y-S21(result.params, x, y)
#     
#     pl.plot(x, y,'--')
#     
#     kappa_a.append( result.params['kappa_int'].value + result.params['kappa1'].value + result.params['kappa2'].value )
#     m = m + step
#==============================================================================



# use kappa_prod and kappa_a instead of kappa 1, 2, int
    x = freq
    y = z
    x = x * 1000000000
    
    ##plotting s21^2 to get the linewidth of the cavity and YIG mode
    #y = np.power(10,y/10.0)
    #pl.plot(x, y)
    
    y = np.power(10,y/20.0)
    
#    pl.figure(m)
    pl.plot(x, y)
    
    def S21(params, x, y):
        est = np.sqrt(params['kappa_prod'])
        est = est/(1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 + params['g'] **2 /(1j*(x-params['omega_FMR'])-params['gamma_m']/2.0))
        return y - abs(est)
        
    params = lmfit.Parameters()
    params.add('kappa_prod', value= 3e10, min = 0)
    params.add('omega_c', value= 8.5e9)
    params.add('kappa_a', value=3e6, min = 0)
    params.add('g',value= 24.75e6, min = 0)
    params.add('omega_FMR',value = 8.48e9)
    params.add('gamma_m', value = 3e6, min=0)
    print X[0][i]
    result = lmfit.minimize(S21, params, args=(x, y))
    lmfit.report_fit(result.params)    
    y=y-S21(result.params, x, y)
    
    pl.plot(x, y,'--')
    

    m = m + step
    f= open('parameters_%s.txt'%(filename),'a')
    f.writelines('%s\n %s\n'%(X[0][i], result.params))
    f.close()
    
pl.legend()
