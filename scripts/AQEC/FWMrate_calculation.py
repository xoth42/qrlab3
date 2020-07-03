# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 11:09:47 2019

@author: Wang_Lab
"""
import numpy as np

delta=2.656/0.93

#'''AQEC #MP'''
#a=-1.22
#b=1.01
#c=0.64
#d=0.47
#A=-1.06*np.exp(-0.54j)
#B=1.53*np.exp(-0.1j)
#C=1.27*np.exp(0.2j)
#D=1.14*np.exp(0.08j)
#
'''AQEC #MP-'''
a=-1.22
b=1.00
c=0.64
d=0.49
A=-1.06*np.exp(-0.66j)
B=1.54*np.exp(-0.14j)
C=1.29*np.exp(0.29j)
D=1.12*np.exp(0.30j)

'''AQEC #OMP'''
a=-1.22
b=1.00
c=0.64
d=0.49
A=0.98*np.exp(2.71j)
B=1.52*np.exp(-0.14j)
C=1.27*np.exp(-0.10j)
D=1.14*np.exp(-0.49j)
#
#
#'''AQEC #OXY'''
#a=-1.22
#b=1.00
#c=0.64
#d=0.49
#A=0.684*np.exp(2.61j)
#B=1.252*np.exp(-0.14j)
#C=1.102*np.exp(-0.09j)
#D=0.921*np.exp(-0.52j)


#'''AQEC #MP+'''
#a=-1.22
#b=1.01
#c=0.64
#d=0.47
#A=-1.28*np.exp(-0.76j)
#B=1.87*np.exp(-0.1j)
#C=1.56*np.exp(0.13j)
#D=1.36*np.exp(0.02j)

#'''AQEC OL'''
#a=-1.15
#b=0.90
#c=0.59
#d=0.47
#A=0.762*np.exp(2.44j)
#B=1.286*np.exp(-0.14j)
#C=1.113*np.exp(0.01j)
#D=0.955*np.exp(-0.36j)

'''
R1 = a*(delta+b**2+c**2/2+d**2/3) +b*c*(b+3*d/2)

R2 = b*(delta-a**2+c**2+d**2/2) +c*d*(c-a/2)

R3 = c*(delta-a**2/2-b**2+d**2) -a*b*(b-d/2)

R4 = d*(delta-a**2/3-b**2/2-c**2) -b*c*(c+3*a/2)

G1 = A*delta + B*(a*b+b*c+c*d) + C*(a*c+b*d)/2 + D*(a*d)/3
G2 = B*delta + (C-A)*(a*b+b*c+c*d) + D*(a*c+b*d)/2
G3 = C*delta + (D-B)*(a*b+b*c+c*d) - A*(a*c+b*d)/2
G4 = D*delta - C*(a*b+b*c+c*d) - B*(a*c+b*d)/2 - A*(a*d)/3

print 'fwm rates:'
print (R1)
print (R2*np.sqrt(3))
print (R3*np.sqrt(5))
print (R4*np.sqrt(7))

SS = (a**2 + b**2 + c**2 + d**2)*0.93
print 'Stark shift=', SS

print 'ge rates:'
print -np.abs(G1)
print np.abs(G2)
print np.abs(G3)
print np.abs(G4)
'''


import matplotlib.pyplot as plt
#FWMamps = np.array([0.04, 0.0625, 0.09, 0.09, 0.1225, 0.16, 0.16, 0.2025, 0.2025, 0.25, 0.25, 0.36, 0.64, 1.00, 1.44, 1.96])
FWMamps = np.array([0.2, 0.25, 0.3, 0.3, 0.35, 0.4, 0.4, 0.45, 0.45, 0.5, 0.5, 0.6, 0.8, 1.0, 1.2, 1.4])
Cav_ups_exp = np.array([0.163, 0.224, 0.294, 0.290, 0.349, 0.385, 0.379, 0.432, 0.461, 0.48, 0.4938, 0.572, 0.692, 0.778, 0.810, 0.847])/0.52

kappa = 580.0
FWMamps_kHz = FWMamps/1.45*100  # FWMamp = 1.383 converts to Omega of 100 kHz

qubit_decay = 1/0.038


plt.figure()
plt.plot(FWMamps_kHz, Cav_ups_exp, ls=None, marker='^')
plt.plot([96.7], [1.7], ls=None, marker='o')

FWMamps_kHz = np.linspace(0, 100, 101)
qubit_gamma_eff = 2*np.pi*4*FWMamps_kHz**2/kappa

qubit_gamma_up = 1.36
Cav_ups_thy = qubit_gamma_eff/(qubit_gamma_eff+qubit_decay)*qubit_gamma_up
plt.plot(FWMamps_kHz, Cav_ups_thy)

qubit_gamma_up = 1.8
Cav_ups_thy = qubit_gamma_eff/(qubit_gamma_eff+qubit_decay)*qubit_gamma_up
plt.plot(FWMamps_kHz, Cav_ups_thy)


#
#real_Gammaup = 0.92
#qubitdecay = 0.18
#Gammaups_exp -= -0.02
#Gammaups_thy = FWMamps/(FWMamps+qubitdecay)*real_Gammaup
#
#plt.figure()
#plt.plot(FWMamps, Gammaups_exp, ls=None, marker='s')
#plt.plot(FWMamps, Gammaups_thy)
