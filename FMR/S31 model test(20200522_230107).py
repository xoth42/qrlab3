# -*- coding: utf-8 -*-
"""
Created on Mon May 18 14:07:59 2020

@author: Jack
"""

import numpy as np
import matplotlib.pyplot as plt
import cmath

def S31(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w):
    A=gam1/2-1j*(w-w1)
    B=gam2/2-1j*(w-w2)
    C=gam3/2-1j*(w-w3)
    D=-1j*(w-w4)
    s31= gam3*gam1*abs((B*D*j1-B*delta*j2+2*j1*j2**2)/(B*D*j1**2+B*C*j2**2+4*j1**2*j2**2+A*(B*(C*D+delta**2)+D*j1**2+C*j2**2)))**2
    return s31
def S31_phase(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w):
    A=gam1/2-1j*(w-w1)
    B=gam2/2-1j*(w-w2)
    C=gam3/2-1j*(w-w3)
    D=-1j*(w-w4)
    s31_raw = 1j*(B*D*j1-B*delta*j2+2*j1*j2**2)/(B*D*j1**2+B*C*j2**2+4*j1**2*j2**2+A*(B*(C*D+delta**2)+D*j1**2+C*j2**2))
    s31_phase = []
    for i in range(len(w)):
        s31_phase.append(cmath.phase(s31_raw[i]))
    return s31_phase
w=np.linspace(10.7,10.725,10000)
delta = .6
j2=.019
j1=.03
gam3=.894
w1=10.7108
w2=10.7116
w3=10.619
w4=11.4642
gam1=.0016
gam2=.00076
S31_data=(S31(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w))
S31_phase_data=(S31(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w))
# S31_data = []
# S31_phase_data = []
# for i in range(len(w4)):
#     S31_data.append(S31(gam1,gam2,gam3,w1,w2,w3,w4[i],j1,j2,delta,w))
#     S31_phase_data.append(S31(gam1,gam2,gam3,w1,w2,w3,w4[i],j1,j2,delta,w))
# plt.figure()
# plt.plot(S31_data*np.cos(S31_phase_data),S31_data*np.sin(S31_phase_data))
# plt.title('complex plane')
# plt.figure()
# plt.title('S31 magnitude')
# for i in range(len(w4)):
#     plt.plot(w,S31_data[i],label = str(w4[i]))
# plt.legend()
# plt.figure()
# plt.plot(w,S31_phase_data)
# plt.title('phase')
plt.figure()
plt.plot(w,S31_data)
plt.title('magnitude')

# def S21_num(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w):
#     A=gam1/2-1j*(w-w1)
#     B=gam2/2-1j*(w-w2)
#     C=gam3/2-1j*(w-w3)
#     D=-1j*(w-w4)
#     s21= gam3*gam1*abs((B*D*j1-B*delta*j2+2*j1*j2**2))**2
#     return s21

# def S21_den(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w):
#     A=gam1/2-1j*(w-w1)
#     B=gam2/2-1j*(w-w2)
#     C=gam3/2-1j*(w-w3)
#     D=-1j*(w-w4)
#     s21= gam3*gam1*abs((B*D*j1**2+B*C*j2**2+4*j1**2*j2**2+A*(B*(C*D+delta**2)+D*j1**2+C*j2**2)))**2
#     return s21
# plt.figure()
# plt.plot(w,S21_num(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w))
# plt.title('complex plane')
# plt.figure()
# plt.plot(w,S21_den(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w))
# plt.title('complex plane')
