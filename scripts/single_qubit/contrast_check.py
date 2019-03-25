# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 14:11:42 2019

@author: Wang_Lab
"""

#Ebru: This piece of code is used in automated T1 - T2 flux sweep 

import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
#matplotlib.rcParams['backend'] = 'Qt4Agg'
#matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
#from t1t2_plotting import smart_T1_delays
from pulseseq import sequencer, pulselib
import os
import time
import math
import datetime



 #This one is supposed to check whether the contrast of the SSB spec output is reasonable or not, comparing the Lorentzian fit height to the average bg
 #fluctuation of a flat portion (arbitrarily picked to be on the left of the dip). It simply returns a True or False statement. 

#If the number of averaging is too small, the criteria for comparison of noise_amp and height should be relaxed.
 
 
def Contrast_check(xs, ys, height, width, flat_portion = None):
    
    if flat_portion is None:
        flat_portion = 0.3
    
    #We arbitrarily pick the flat portion to get the fluctuation amplitude to be one third of the frequency interval, assuming that the width of the dip is smaller than one third of the frequency 
    #interval swept. If not, this choice should be updated.
      
    
    #This creates the array that will be populated by the y points within the chosen flat region range.
    flat_ys = np.array([])
    #This will be the array that contains the points above the average value of the y points in the above array. 
    above_avg = np.array([])
    #This will be the array that contains the points below the average value of the y points. 
    below_avg = np.array([])


    #Populating flat_region_ys array:    
    for i in range(int(len(xs) * flat_portion)):        
        flat_ys = np.append(flat_ys, ys[i])
    
    avg = np.mean(flat_ys)

    
    for i in range(len(flat_ys)):
        if flat_ys[i] < avg:
            above_avg = np.append(above_avg, flat_ys[i])
        if flat_ys[i] > avg:
            below_avg = np.append(below_avg, flat_ys[i])
    
#    Getting the average value for the points above and below
    
    ab_avg = np.mean(above_avg)
    bl_avg = np.mean(below_avg)
    
    noise_amp = ab_avg - bl_avg  #This gives an measure of the amplitude of the fluctuation of the points within the chose flat range.
            
    if width>0.2e6 and abs(height) > 1.4*abs(noise_amp):
        print ('true')
        return True 
    else:
        print('false')
        return False
            