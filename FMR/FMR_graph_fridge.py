'''
this file is for measuring with VNA and saving data to a file, 
determine the magnetic field region and stepsize, sleeptime for magnetic field ramping, VNA average factor, filename @ line 44
and ramp the magnetic field to your Mi before start running it, or set a longer sleeptime @ line 62 for the ramping

!!remember to change the filename every time, otherwise the older data would be overwritten
'''

import matplotlib
matplotlib.interactive(True)

#
#from mclient import instruments
#VNA = instruments['VNA']
#Yoko = instruments['Yoko']

'''import time


    #import visa
if 1:
        import os
        os.system(r'C:\qrlab\start.bat')
        time.sleep(1)
    '''

import mclient


#VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')
#Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB1::11::INSTR')

import numpy as np
import datetime
import time
import matplotlib.pyplot as pl



magnet = mclient.instruments['Magnet']
#yoko = mclient.instruments['Yoko']
VNA = mclient.instruments['VNA']

Mi = float(0.0) #initial field in Tesla
Mf = float(0.8) #final field
step = 0.005
sleeptime = 9
avefac = 45
filename = 'circulator_fridge_S31_field_%s_%s_%s_ave_factor_%s-0806.txt'%(Mi,Mf,step,avefac)

VNA.set_average_factor(avefac)
VNA.do_enable_averaging()
#magnetic field step
#range = yoko.select_voltage_range(10)
#yoko.do_set_source_range(range)

if Mi<Mf:
    step = abs(step)
else:
    step = -abs(step)
m = Mi
print m  
#Yoko.do_set_voltage(m/float(40))
magnet.do_set_field(m)
time.sleep(sleeptime)
#
VNA.set_averaging_trigger(0)
VNA.set_averaging_trigger(1)
time.sleep(60)
data = VNA.do_get_data(fmt='PLOG')#, opc=True, trig_each_avg=True)

value = data[0]
phase = data[1]
value = value[:,None].T
phase = phase[:,None].T
Mag = []
Mag.append(m)
axis = VNA.do_get_xaxis()
m = m + step
axis = axis[:,None].T
while np.abs(m) <= np.abs(Mf): #current field

    print m
    magnet.do_set_field(m)
    time.sleep(sleeptime)
    
    Mag.append(m)
    VNA.set_averaging_trigger(0)
    VNA.set_averaging_trigger(1)
    time.sleep(60)
    datanew = VNA.do_get_data(fmt='PLOG')#, opc=True, trig_each_avg=True)
    valuenew = datanew[0]
    phasenew = datanew[1]
    valuenew = valuenew[:,None].T
    phasenew = phasenew[:,None].T

    value = np.concatenate([value,valuenew])
    phase = np.concatenate([phase,phasenew])
    
    m = m+step  
    


#print Mag
#magnet.do_ramp_zero()

axis = axis / float(1000000000)
X, Y = np.meshgrid(Mag, axis)
Z = np.transpose(value)
phase = np.transpose(phase)

#save the data as a file
to_save = [X, Y, Z, phase]

with file(filename,'w') as outfile:

    outfile.write('# Array\n')

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
pl.suptitle(filename[0:21])
pl.pcolormesh(X, Y, Z)
pl.colorbar()

pl.xlabel('Magnetic Field(T)')
pl.ylabel('Frequency (GHZ)')
pl.show()   



mlist = np.linspace(m,0,301) 
for i in mlist[2:]:
    print i
    magnet.do_set_field(i)
    time.sleep(sleeptime)

