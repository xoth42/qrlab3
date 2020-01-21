# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 15:07:20 2019

@author: Wang_Lab
"""

import numpy as np
from numpy import linalg as LA
import matplotlib.pyplot as pl


wa = 10.71
wb = 10.71
#wp = 10.6
#wn = 10.6
ga = 0.02
gb = 0.02
theta = np.pi * 2/3
wa_p =[]
wb_p = []
va_p =[]
vb_p = []


wp = 10.6
wn = 10.6 + 1j*1
delta = 1
wp_p = []
wn_p = []
deltalist = np.linspace(0,1,101)
for delta in deltalist:
    H = np.array([[wp, delta],
              [delta, wn]])



    e,v =LA.eig(H)
#    print e
#    print v
    wp_p.append(e[0])
    wn_p.append(e[1])
print e
print v
#wp_p = 10.8 + deltalist + 1j * 0.5
#wn_p = 10.6 - deltalist + 1j * 0.5
pl.figure()
pl.subplot(211)   
pl.plot(deltalist,np.real(wp_p),label = 'real')
pl.plot(deltalist,np.real(wn_p))
pl.legend()
pl.subplot(212) 
pl.plot(deltalist,np.imag(wp_p),label = 'imag')
pl.plot(deltalist,np.imag(wn_p))
pl.legend()




w3 = []
w4 = []

for i, delta in enumerate(deltalist):
    wp = wp_p[i]
    wn = wn_p[i]
    H = np.array([[wa, 0, ga*np.exp(1j*theta),ga*np.exp(-1j*theta)], 
              [0, wb, gb*np.exp(-1j*theta),gb*np.exp(1j*theta)],
              [ga*np.exp(-1j*theta),gb*np.exp(1j*theta),wp, 0],
              [ga*np.exp(1j*theta),gb*np.exp(-1j*theta),0, wn]])
    
    
    
    e,v =LA.eig(H)

    if delta == 100:
        wa_p.append(e[1])
        wb_p.append(e[0])
        va_p.append(v[1])
        vb_p.append(v[0])
    else:
        wa_p.append(e[2])
        wb_p.append(e[3])
        w3.append(e[0])
        w4.append(e[1])
        va_p.append(v[:,2])
        vb_p.append(v[:,3])            
    
print e
print v

pl.figure()
pl.subplot(211)   
pl.scatter(deltalist,np.real(wa_p),label = 'real\n mode a')
pl.scatter(deltalist,np.real(wb_p),label = ' mode b')
pl.scatter(deltalist,np.real(w3))
pl.scatter(deltalist,np.real(w4))
pl.ylim(10.7,10.72)
pl.legend()
pl.subplot(212) 
pl.scatter(deltalist,np.imag(wa_p),label = 'imag\n mode a')
pl.scatter(deltalist,np.imag(wb_p),label = ' mode b')
pl.scatter(deltalist,np.imag(w3))
pl.scatter(deltalist,np.imag(w4))
#pl.ylim(-0.002,0.005)
pl.legend() 

va_p = np.asarray(va_p)
vb_p = np.asarray(vb_p)
pl.figure()
pl.title('components of mode a')
pl.plot(deltalist,np.abs(va_p[:,0])**2, label = 'percentage of cavity 1')
pl.plot(deltalist,np.abs(va_p[:,1])**2, label = 'percentage of cavity 2')  
pl.plot(deltalist,np.abs(va_p[:,2])**2, label = 'percentage of circulator mode 1') 
pl.plot(deltalist,np.abs(va_p[:,3])**2, label = 'percentage of circulator mode 2') 
pl.legend()
    
pl.figure()
pl.title('components of mode b')
pl.plot(deltalist,np.abs(vb_p[:,0])**2, label = 'percentage of cavity 1')
pl.plot(deltalist,np.abs(vb_p[:,1])**2, label = 'percentage of cavity 2')  
pl.plot(deltalist,np.abs(vb_p[:,2])**2, label = 'percentage of circulator mode 1') 
pl.plot(deltalist,np.abs(vb_p[:,3])**2, label = 'percentage of circulator mode 2') 
pl.legend()

res = np.zeros(4, dtype = complex)
for i in range(len(H)):
    res[i] = 0
    for j in range(4):
        res[i] = res[i] + H[i][j] * v[j][3]
        
print res/e[3]
        