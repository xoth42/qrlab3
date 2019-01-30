# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 20:04:15 2018

@author: WangLab
"""
  
import numpy as np
import matplotlib.pyplot as pl
import matplotlib


folder = r'C:\Users\WangLab\Documents\yingying\RT_circulator_414mV_082918'
S11_file = np.loadtxt(folder + r'\S11.txt', delimiter = ",")
S21_file = np.loadtxt(folder + r'\S21.txt', delimiter = ",")
S12_file = np.loadtxt(folder + r'\S12.txt', delimiter = ",")
S22_file = np.loadtxt(folder + r'\S22.txt', delimiter = ",")

frequency = S11_file[:,0]
S11_dB = S11_file[:,1]
S21_dB = S21_file[:,1]
S12_dB = S12_file[:,1]
S22_dB = S22_file[:,1]

def to_linear_voltage(Sij_dB):
    Sij = np.zeros(len(Sij_dB))
    for k in range(len(Sij_dB)):
        Sij[k] = 10**(Sij_dB[k]/20)
    return(Sij)
    
S11 = to_linear_voltage(S11_dB)
S21 = to_linear_voltage(S21_dB)
S12 = to_linear_voltage(S12_dB)
S22 = to_linear_voltage(S22_dB)

loss = np.zeros(len(frequency))
for k in range(len(frequency)):
    loss[k] = (1 - S21[k]**2 - S11[k]**2)*100


f, ax = pl.subplots(2,sharex = True)

w = 2.0
font = 12
pl.rcParams.update({'font.size': font})
f.subplots_adjust(hspace=0)


ax[0].set(title = 'Circulator Performance',xlim = [10,11],ylim = [-50,0])
ax[1].set(xlabel = 'frequency (GHz)',ylabel = 'Loss (%)',xlim = [10,11])
ax[0].set_ylabel('dB', color='red')
ax[0].tick_params(axis='y', labelcolor='red')
ax[0].plot(frequency,S11_dB, label= r'$\mathrm{S_{11}}$',color = 'red', linewidth = w)

ax[0].plot(frequency,S12_dB, label= r'$\mathrm{S_{12}}$',color = 'crimson', linewidth = w)
ax[0].plot(frequency,S22_dB, label= r'$\mathrm{S_{22}}$',color = 'pink', linewidth = w)

ax2 = ax[0].twinx()
ax2.plot(frequency,S21_dB, label= r'$\mathrm{S_{21}}$',color = 'navy', linewidth = w)
ax2.legend(loc = 4, fontsize = font)
ax2.set(ylim = [-1.5,0])
ax2.set_ylabel('dB', color = 'navy')
ax2.tick_params(axis='y', labelcolor='navy')

ax[0].legend(fontsize = font)
ax[1].plot(frequency,loss,linewidth = w)
f.tight_layout()
pl.subplots_adjust(hspace = .075)
pl.show()
pl.savefig(r'C:\Users\WangLab\Documents\yingying\RT_circulator_414mV_082918\CirculatorV3.svg')

