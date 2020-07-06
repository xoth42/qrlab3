# -*- coding: utf-8 -*-
"""
Created on Fri Jan 03 10:57:56 2020

@author: Wang_Lab
"""

import numpy as np
from numpy import linalg as LA
import matplotlib.pyplot as pl


wa = 10.6
wb = 10.6 - 1j

g =1j

kappa_a = 0
kappa_b = 0
lamda = 0
wa_p =[]
wb_p = []
va_p =[]
vb_p = []



delta = 1
wp_p = []
wn_p = []





lamdalist = np.linspace(0,10,1)
#glist = np.linspace(0.004,0,101)

for i, lamda in enumerate(lamdalist):
    
#    lamda = 0.5
#    g = glist[i]

    H = np.array([[wa - 1j * kappa_a, g ], 
                  [np.conjugate(g), wb - 1j * kappa_b]])



    e,v =LA.eig(H)
    
    #if lamda == 100:
    wa_p.append(e[1])
    wb_p.append(e[0])
    va_p.append(v[:,1])
    vb_p.append(v[:,0])
           
    
print e
print v

pl.figure()
pl.subplot(211)   
pl.scatter(lamdalist,np.real(wa_p),label = 'real\n mode a')
pl.scatter(lamdalist,np.real(wb_p),label = ' mode b')

pl.ylim(10.7,10.72)
pl.legend()
pl.subplot(212) 
pl.scatter(lamdalist,np.imag(wa_p),label = 'imag\n mode a')
pl.scatter(lamdalist,np.imag(wb_p),label = ' mode b')
pl.ylim(-0.005,0.005)
pl.legend() 

va_p = np.asarray(va_p)
vb_p = np.asarray(vb_p)
pl.figure()
pl.title('components of mode a')
pl.plot(lamdalist,np.abs(va_p[:,0])**2, label = 'percentage of cavity 1')
pl.plot(lamdalist,np.abs(va_p[:,1])**2, label = 'percentage of cavity 2')  

pl.legend()
    
pl.figure()
pl.title('components of mode b')
pl.plot(lamdalist,np.abs(vb_p[:,0])**2, label = 'percentage of cavity 1')
pl.plot(lamdalist,np.abs(vb_p[:,1])**2, label = 'percentage of cavity 2')  

pl.legend()

x = np.linspace(10.69,10.71,1601)
wa = 10.7
wb = wa
kappa_a =0.007
kappa_b = 0.001
phi = 0
S21 = 0.1 /(1j * (x - wa) - kappa_a/2) + np.exp(phi) * 0.2/(1j *(x - wb) - kappa_b/2)
fig = pl.figure()
gs = gridspec.GridSpec(1, 2)
fig.add_subplot(gs[0])
fig.add_subplot(gs[1])
fig.axes[1].plot(S21.real,S21.imag)
fig.axes[0].plot(x,np.abs(S21))