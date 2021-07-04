"""
Created on Fri Mar 22 16:30:25 2019

@author: WangLab
FMR Measurements at room temperature, using Yokogawa (7651) power supply and VNA
Drive Yoko in current mode – this script exists because I kept having to edit.

First, run "create_instruments.py" prior to measurement. 
"""

import matplotlib
matplotlib.interactive(True)
import objectsharer as objsh

#
from mclient import instruments
VNA = instruments['VNA']
VNA.set_timeout(40000)
Yoko = instruments['Yoko']

'''import time


    #import visa
if 1:
        import os
        os.system(r'C:\qrlab\start.bat')
        time.sleep(1)
    '''


#import mclient
import numpy as np
import datetime
import time
import matplotlib.pyplot as pl

date = datetime.datetime.now()

#Make sure to check that repeat is off for Yoko GS200
#To do manually, press 'Program' key and press repeat is the left most option on screen

I_i = 0.1 #Current - switched to controlling current on 2/1/19
I_f = 0.5

#step = 1e-3
step = 0.05
sleeptime = 1

#foldername = 'C:\Users\WangLab\Documents\\yingying\\circulator\\20190109' 
#foldername = r"C:\Users\WangLab\Documents\TConnolly\calibrated_circulator\transition1-3"

foldername = 'C:\\Users\WangLab\Documents\FMR(2019)'
filename = '%s\\YIG_3_1.5mm_DCC_ZoomForModes_S12_%s-%s-%s_Date_%s-%s_%s-%s-%s.txt'%(foldername,I_i,I_f,step,date.month,date.day,date.hour,date.minute,date.second)

VNA.set_s_param('S12')
Yoko.do_set_output_state(0)

'''Ramp up to I_i'''
I = 0
Yoko.do_set_current(I)
rstep = I_i/5
while ( I < I_i): #Rewrite ramp function to work correctly
    time.sleep(0.5)
    I = I + rstep
    Yoko.do_set_current(I)
    print(I)
    
'''Take Data!'''
time.sleep(sleeptime) 
data = VNA.do_get_data()
value = data[0]
phase = data[1]
value = value[:,None].T
phase = phase[:,None].T
Mag = []
Mag.append(I)
axis = VNA.do_get_xaxis()
I = I + step
#axis = axis[:,None].T
while np.abs(I) <= np.abs(I_f): #current field
    print(I)
    Yoko.do_set_current(I)
#    time.sleep(sleeptime)
    
    Mag.append(I) 
    
    '''OPC commands'''
    VNA.set_trigger_source('BUS')
#        VNA.write('INIT:CONT ON')

#        VNA.set_averaging_trigger(1)
    
    VNA.trigger()
    
    wait = VNA.opc(async=True) # wait for completion

#            print 'ok7'
#                a=0
    try:
        while not wait.is_valid():
#                        if a % 10 == 0:
#                            print 'async', a 
#                        a= a + 1
            
#                    time.sleep(0.1)
            objsh.helper.backend.main_loop(100) #main_loop_time = 100 ms
            VNA.set_format('MLOG')
    except:
        print('error with async')
#                VNA.set_interrupt(True)

    datanew = VNA.do_get_data()
    VNA.set_trigger_source('internal')
    valuenew = datanew[0]
    phasenew = datanew[1]
    valuenew = valuenew[:,None].T
    phasenew = phasenew[:,None].T

    value = np.concatenate([value,valuenew])
    phase = np.concatenate([phase,phasenew])
    
    I = I+step
#    s_params = ['S11','S21','S12','S22']

#    for sij in s_params:
#        VNA.set_s_param(sij)
time.sleep(sleeptime)
print('Finished Measuring!')

'''Ramp back to current = 0 mA'''
while (I > 0):
    I = I - rstep
    print(I)
    Yoko.do_set_current(I)
    time.sleep(0.1)
I = 0
Yoko.do_set_current(I)
print(I)
print('All done!')

'''Convert Yoko current to magnetic field, in mT'''
field = []
for i in Mag:
    if (i < 0.5):
        f = i*529.37 + 0.49
    else:
        f = -268.93 * (i)**2 + 839.69*i - 88.67
    field.append(f)
 
X, Y = np.meshgrid(field, axis)
Z = np.transpose(value)
phase = np.transpose(phase)

'''Save and Plot'''
to_save = [X, Y, Z, phase]
with file(filename,'w') as outfile:
    outfile.write('# new slice\n')

    # Iterating through a ndimensional array produces slices along
    # the last axis. This is equivalent to data[i,:,:] in this case
    for data_slice in to_save:

        # The formatting string indicates that I'm writing out
        # the values in left-justified columns 7 characters in width
        # with 2 decimal places.  
        np.savetxt(outfile, data_slice, fmt='%-7.7f')

        # Writing out a break to indicate different slices...
        outfile.write('# New slice\n')

pl.figure()
pl.pcolormesh(X, Y / float(10**9), Z)
pl.colorbar()
pl.title('1.5mm YIG (Sample 3) FMR Measurement of S12')
pl.xlabel('Magnetic Field (mT)')
pl.ylabel('Frequency (GHz)')
pl.show()



