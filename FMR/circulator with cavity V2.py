# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 15:07:20 2019

@author: Wang_Lab
"""

import numpy as np
from numpy import linalg as LA
import matplotlib.pyplot as pl
from matplotlib import gridspec


wa = 10.711
wb = 10.711# + 0.0001j

ga = 0.02
ga2 = ga*0.6
gb = ga
gb2 = ga2
wa_p =[]
wb_p = []
va_p =[]
vb_p = []
vc_p =[]
vd_p = []


wp =10.619 
wn = 10.8- 1j*0.3
delta = 1
wp_p = []
wn_p = []
deltalist = np.linspace(-0,1,701)



w3 = []
w4 = []



for i, delta in enumerate(deltalist):

    H = np.array([[wa, 0,   ga, ga2], 
                  [0,  wb, -gb, gb2],
                  [ga,-gb,  wp, 1j*delta],
                  [ga2,gb2, -1j*delta, wn]])
    
    
    
    e,v =LA.eig(H)



    wa_p.append(e[2])
    wb_p.append(e[3])
    w3.append(e[0])
    w4.append(e[1])
    va_p.append(v[:,2])
    vb_p.append(v[:,3])   
    vc_p.append(v[:,0])
    vd_p.append(v[:,1])           
    
print e
print v

pl.figure()
pl.subplot(211)   
pl.scatter(deltalist,np.real(wa_p),label = 'real\n mode a')
pl.scatter(deltalist,np.real(wb_p),label = ' mode b')
pl.scatter(deltalist,np.real(w3),label = ' mode c')
pl.scatter(deltalist,np.real(w4),label = ' mode d')
pl.ylim(abs(wa) - 0.01,abs(wa) + 0.01)
pl.legend()
pl.subplot(212) 
pl.scatter(deltalist,np.imag(wa_p),label = 'imag\n mode a')
pl.scatter(deltalist,np.imag(wb_p),label = ' mode b')
pl.scatter(deltalist,np.imag(w3),label = ' mode c')
pl.scatter(deltalist,np.imag(w4),label = ' mode d')
#pl.ylim(-0.008,0.008)
pl.legend() 

va_p = np.asarray(va_p)
vb_p = np.asarray(vb_p)
vc_p = np.asarray(vc_p)
vd_p = np.asarray(vd_p)
#pl.figure()
#pl.title('components of mode a')
#pl.plot(deltalist,np.abs(va_p[:,0])**2, label = 'percentage of cavity 1, max = %.03f'%(np.max(np.abs(va_p[:,0])**2)))
#pl.plot(deltalist,np.abs(va_p[:,1])**2, label = 'percentage of cavity 2, min = %.03f'%(np.min(np.abs(va_p[:,1])**2))) 
#pl.plot(deltalist,np.abs(va_p[:,2])**2, label = 'percentage of circulator mode 1') 
#pl.plot(deltalist,np.abs(va_p[:,3])**2, label = 'percentage of circulator mode 2') 
#pl.legend()
#cal = 0
#print 'mode a\nmax = %.03f @ delta = %.03f'%(np.max(np.abs(va_p[:,0][cal:])**2), deltalist[cal+np.argmax(np.abs(va_p[:,0][cal:])**2)])
#print 'min = %.03f @ delta = %.03f'%(np.min(np.abs(va_p[:,1][cal:])**2), deltalist[cal+np.argmin(np.abs(va_p[:,1][cal:])**2)])
#print 'mode b\nmax = %.03f @ delta = %.03f'%(np.max(np.abs(vb_p[:,0][cal:])**2), deltalist[cal+np.argmax(np.abs(vb_p[:,0][cal:])**2)])
#print 'min = %.03f @ delta = %.03f'%(np.min(np.abs(vb_p[:,1][cal:])**2), deltalist[cal+np.argmin(np.abs(vb_p[:,1][cal:])**2)])    
#pl.figure()
#pl.title('components of mode b')
#pl.plot(deltalist,np.abs(vb_p[:,0])**2, label = 'percentage of cavity 1')
#pl.plot(deltalist,np.abs(vb_p[:,1])**2, label = 'percentage of cavity 2')  
#pl.plot(deltalist,np.abs(vb_p[:,2])**2, label = 'percentage of circulator mode 1') 
#pl.plot(deltalist,np.abs(vb_p[:,3])**2, label = 'percentage of circulator mode 2') 
#pl.legend()
#pl.figure()
#pl.title('components of mode c')
#pl.plot(deltalist,np.abs(vc_p[:,0])**2, label = 'percentage of cavity 1')
#pl.plot(deltalist,np.abs(vc_p[:,1])**2, label = 'percentage of cavity 2')  
#pl.plot(deltalist,np.abs(vc_p[:,2])**2, label = 'percentage of circulator mode 1') 
#pl.plot(deltalist,np.abs(vc_p[:,3])**2, label = 'percentage of circulator mode 2') 
#pl.legend()
#pl.figure()
#pl.title('components of mode d')
#pl.plot(deltalist,np.abs(vd_p[:,0])**2, label = 'percentage of cavity 1')
#pl.plot(deltalist,np.abs(vd_p[:,1])**2, label = 'percentage of cavity 2')  
#pl.plot(deltalist,np.abs(vd_p[:,2])**2, label = 'percentage of circulator mode 1') 
#pl.plot(deltalist,np.abs(vd_p[:,3])**2, label = 'percentage of circulator mode 2') 
#pl.legend()
#print ' wa,   wb'
#print wa_p[-1] , wb_p[-1]
#print ' wa - wb'
#print wa_p[-1] - wb_p[-1]

#res = np.zeros(4, dtype = complex)
#for mode in [2,3]:
#    print 'eigenvector:'
#    for i in range(len(H)):
#        res[i] = 0
#        for j in range(4):
#            res[i] = res[i] + H[i][j] * v[j][mode]
#            
#    print res/e[mode]
        
fig = pl.figure()
gs = gridspec.GridSpec(2, 2)
fig.add_subplot(gs[0])
fig.add_subplot(gs[1])   
fig.add_subplot(gs[2])
fig.add_subplot(gs[3])    

fig.axes[0].set_title('components of mode a')
fig.axes[0].plot(deltalist,np.abs(va_p[:,0])**2)#, label = 'percentage of cavity 1, max = %.03f'%(np.max(np.abs(va_p[:,0])**2)))
fig.axes[0].plot(deltalist,np.abs(va_p[:,1])**2)#, label = 'percentage of cavity 2, min = %.03f'%(np.min(np.abs(va_p[:,1])**2))) 
fig.axes[0].plot(deltalist,np.abs(va_p[:,2])**2)#, label = 'percentage of circulator mode 1') 
fig.axes[0].plot(deltalist,np.abs(va_p[:,3])**2)#, label = 'percentage of circulator mode 2') 
fig.axes[0].legend()
cal = 0
print 'mode a\nmax = %.03f @ delta = %.03f'%(np.max(np.abs(va_p[:,1][cal:])**2), deltalist[cal+np.argmax(np.abs(va_p[:,1][cal:])**2)])
print 'min = %.03f @ delta = %.03f'%(np.min(np.abs(va_p[:,0][cal:])**2), deltalist[cal+np.argmin(np.abs(va_p[:,0][cal:])**2)])
print 'mode b\nmax = %.03f @ delta = %.03f'%(np.max(np.abs(vb_p[:,1][cal:])**2), deltalist[cal+np.argmax(np.abs(vb_p[:,1][cal:])**2)])
print 'min = %.03f @ delta = %.03f'%(np.min(np.abs(vb_p[:,0][cal:])**2), deltalist[cal+np.argmin(np.abs(vb_p[:,0][cal:])**2)])    

fig.axes[1].set_title('components of mode b')
fig.axes[1].plot(deltalist,np.abs(vb_p[:,0])**2, label = 'percentage of cavity 1')
fig.axes[1].plot(deltalist,np.abs(vb_p[:,1])**2, label = 'percentage of cavity 2')  
fig.axes[1].plot(deltalist,np.abs(vb_p[:,2])**2, label = 'percentage of circulator mode 1') 
fig.axes[1].plot(deltalist,np.abs(vb_p[:,3])**2, label = 'percentage of circulator mode 2') 
fig.axes[1].legend()

fig.axes[2].set_title('components of mode c')
fig.axes[2].plot(deltalist,np.abs(vc_p[:,0])**2)#, label = 'percentage of cavity 1')
fig.axes[2].plot(deltalist,np.abs(vc_p[:,1])**2)#, label = 'percentage of cavity 2')  
fig.axes[2].plot(deltalist,np.abs(vc_p[:,2])**2)#, label = 'percentage of circulator mode 1') 
fig.axes[2].plot(deltalist,np.abs(vc_p[:,3])**2)#, label = 'percentage of circulator mode 2') 
fig.axes[2].legend()

fig.axes[3].set_title('components of mode d')
fig.axes[3].plot(deltalist,np.abs(vd_p[:,0])**2)#, label = 'percentage of cavity 1')
fig.axes[3].plot(deltalist,np.abs(vd_p[:,1])**2)#, label = 'percentage of cavity 2')  
fig.axes[3].plot(deltalist,np.abs(vd_p[:,2])**2)#, label = 'percentage of circulator mode 1') 
fig.axes[3].plot(deltalist,np.abs(vd_p[:,3])**2)#, label = 'percentage of circulator mode 2') 
fig.axes[3].legend()