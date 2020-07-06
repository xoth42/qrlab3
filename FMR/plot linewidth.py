# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 13:33:27 2019

@author: WangLab
"""
import csv
#data = np.genfromtxt(r'C:\Users\WangLab\Documents\yingying\0531 cooldown\linewidth.csv')
T = np.loadtxt(r'C:\Users\WangLab\Documents\yingying\0531 cooldown\T.txt')
m110_0dB = np.loadtxt(r'C:\Users\WangLab\Documents\yingying\0531 cooldown\\110_0dB.txt')
m220_0dB = np.loadtxt(r'C:\Users\WangLab\Documents\yingying\0531 cooldown\\220_0dB.txt')
m330_0dB = np.loadtxt(r'C:\Users\WangLab\Documents\yingying\0531 cooldown\\330_0dB.txt')
m440_0dB = np.loadtxt(r'C:\Users\WangLab\Documents\yingying\0531 cooldown\\440_0dB.txt')
m550_0dB = np.loadtxt(r'C:\Users\WangLab\Documents\yingying\0531 cooldown\\550_0dB.txt')
#m110_30dB = np.loadtxt(r'C:\Users\WangLab\Documents\yingying\0531 cooldown\\110_-30dB.txt')
pl.figure()
pl.scatter(T,m110_0dB, label ='110mode')
pl.scatter(T,m220_0dB, label ='220mode')
pl.scatter(T,m330_0dB, label ='330mode')
pl.scatter(T,m440_0dB, label ='440mode')
pl.scatter(T,m550_0dB, label ='550mode')
#pl.scatter(T,m110_30dB)
pl.xscale('log')
pl.legend()
pl.xlabel('T(mK)')
pl.ylabel('linewidth(MHz)')
pl.xlabel('T(mK)', fontsize = 15)
pl.ylabel('linewidth(MHz)', fontsize = 15)
pl.xlim(9,2000)
pl.show()