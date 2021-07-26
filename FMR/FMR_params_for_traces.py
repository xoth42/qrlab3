# -*- coding: utf-8 -*-
"""
Created on Mon Jan 08 14:50:08 2018

@author: WangLab
"""

import mclient
import numpy as np
import matplotlib.pyplot as pl

# Read the array from file
new_data = np.loadtxt(r'C:\\qrlab-3\FMR\text_0.75mm_parall_280-305-0.2.txt')
print(new_data.shape)
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
 
m = 293.9  #the initial magnetic field you want
M = 294.9  #the final magnetic field you want
step = 0.2
kappa_a =[]
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
#      np.savetxt(r'C:\qrlab-3\FMR\%smT.txt' %(X[0][i]), trace , delimiter=",") 
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
    params.add('kappa_prod', value= 323300165.147, vary = False)
    params.add('omega_c', value= 8456886798.41, vary = False)
    params.add('kappa_a', value=3864338.96732, vary = False)
    params.add('g',value= 24.75e6)
    params.add('omega_FMR',value = 8.5e9)
    params.add('gamma_m', value = 3e6, min=0)
    print(X[0][i])
    result = lmfit.minimize(S21, params, args=(x, y))
    lmfit.report_fit(result.params)
    y=y-S21(result.params, x, y)
    
    pl.plot(x, y,'--')
    

    m = m + step