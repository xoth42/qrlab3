import matplotlib
matplotlib.interactive(True)

import os

from mclient import instruments
import glob

import mclient
import time
import numpy as np

#Yoko = instruments.create('Yoko','Yokogawa_7651',address='GPIB1::3::INSTR')


#AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='AWG1', clock=1e9, refsrc='EXT', reffreq=10e6)


#VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')
#Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB1::11::INSTR')

VNA = mclient.instruments['VNA']

import matplotlib.pyplot as pl 

if 1:
    filepath = r'C:\qrlab-3\FMR\RT Measurements\transitions' 
    #filepath = 'C:\Users\Wang_Lab\Documents\yingying\FMR\circulator with field 140mil pin' 
    filelist = glob.glob(r'%s\*'%(filepath))
    
    filelist1 = []
    for i in range(0,3):
        filelist1.append(filelist[i])
    
    pl.figure()
    i = 0
    for filename in filelist1:
        if 1:
        #if i== 0 or i== 5:
        #if i == (0 or 1 or 2 or 3):
        #if filename == 'C:\qrlab-3\FMR\RT Measurements\calibrated_1' or filename == 'C:\qrlab-3\FMR\RT Measurements\uncalibrated_1':
            new_data = np.loadtxt(filename,delimiter=",")
            new_data = np.transpose(new_data)
            axis = new_data[0]
            data = new_data[1]
                
            #pl.figure()
#########################THIS IS BROKEN#####################################################                
            if axis[len(axis) - 1] > 10 **9:
                axis = axis / float(1000000000)
                pl.xlabel('frequency(GHZ)')
            elif axis[len(axis) - 1] > 10 **6:
                axis = axis / float(1000000)
                pl.xlabel('frequency(MHZ)')
#############################################################################################            
                
            pl.xlabel('frequency (GHz)')
            pl.ylabel('dB')
            pl.plot(axis, data, label = filename[-3:])            
            
            #pl.show()
            pl.legend()
        i = i +1
            


'''Plotting Isolation'''
if 0: # get the graph of difference between two file
    # Read the array from file
    filename1 = r'C:/qrlab/FMR/RT Measurements/8.27_Ideal_Isolation/412.3mV/S12'
    filename2 = r'C:/qrlab/FMR/RT Measurements/8.27_Ideal_Isolation/412.3mV/S21'

    new_data = np.loadtxt(filename1,delimiter=",")
    new_data2 = np.loadtxt(filename2,delimiter=",")
    new_data = np.transpose(new_data)
    new_data2 = np.transpose(new_data2)
    
    axis = new_data[0]
    data = new_data[1] - new_data2[1]
    
    #pl.plot(axis,data, label = '%s - %s' (filename1[-3:],filename2[-3:]))
    pl.figure()
    pl.ylabel('dB')
    pl.xlabel('GHz')
    pl.plot(axis,data, label = 'isolation')
    pl.legend()
    
    
'''Plotting Loss'''
if 0: # get the graph of difference between two file

    filename1 = r'C:/qrlab/FMR/RT Measurements/8.27_Ideal_Isolation/412.3mV/S11'
    filename2 = r'C:/qrlab/FMR/RT Measurements/8.27_Ideal_Isolation/412.3mV/S21'

    new_data = np.loadtxt(filename1,delimiter=",")
    new_data2 = np.loadtxt(filename2,delimiter=",")
    new_data = np.transpose(new_data)
    new_data2 = np.transpose(new_data2)
    
    ones = np.ones(len(new_data[0]))
    
    axis = new_data[0]
    data = ones - 10**(new_data[1]/(10)) - 10**(new_data2[1]/(10))
    
    #pl.plot(axis,data, label = '%s - %s' (filename1[-3:],filename2[-3:]))
    pl.figure()
    pl.ylabel('Linear Scale')
    pl.xlabel('GHz')
    pl.plot(axis,data, label = 'loss')
    pl.legend()

