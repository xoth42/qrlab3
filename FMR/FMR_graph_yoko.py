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
<<<<<<< HEAD
from mclient import instruments
=======
import mclient
#from mclient import instruments
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
    
    #Yoko = instruments.create('Yoko','Yokogawa_7651',address='GPIB1::3::INSTR')
    
    
    #AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='AWG1', clock=1e9, refsrc='EXT', reffreq=10e6)
    
    
<<<<<<< HEAD
VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')
Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB1::11::INSTR')
=======
#VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')
#Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB1::11::INSTR')
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7



#import mclient
import numpy as np
import datetime
import time
import matplotlib.pyplot as pl





#Make sure to check that repeat is off for Yoko GS200
#To do manually, press 'Program' key and press repeat is the left most option on screen

<<<<<<< HEAD
#mag = mclient.instruments['Magnet']
#yoko = mclient.instruments['Yoko']
#VNA = mclient.instruments['VNA']

Mi = float(270)  #initial field
Mf = float(330) #final field
step =0.1
sleeptime =6
=======
magnet = mclient.instruments['Magnet']
#yoko = mclient.instruments['Yoko']
VNA = mclient.instruments['VNA']

Mi = float(0.24)  #initial field in Tesla
Mf = float(0.285) #final field
step =0.0002
sleeptime =3
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
  #magnetic field step
#range = yoko.select_voltage_range(10)
#yoko.do_set_source_range(range)

m = Mi  
#Yoko.do_set_voltage(m/float(40))
<<<<<<< HEAD
Yoko.set_voltage_ramp(m/float(40),slew=10)
time.sleep(sleeptime)
=======
magnet.do_set_field(m)
time.sleep(3*sleeptime)
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
data = VNA.do_get_data()
value = data[0]
phase = data[1]
value = value[:,None].T
phase = phase[:,None].T
Mag = []
Mag.append(m)
axis = VNA.do_get_xaxis()
m = m + step
#axis = axis[:,None].T
while m <= Mf: #current field
<<<<<<< HEAD
    level = m/40 # change Field to Voltage
    Yoko.do_set_source_range('10E+0') # fixes range problem
#    Yoko.set_voltage_ramp(level, slew = 10) # slew is rate of change of voltage
    Yoko.do_set_voltage(level)
=======
#    level = m/40 # change Field to Voltage
#    Yoko.do_set_source_range('10E+0') # fixes range problem
#    Yoko.set_voltage_ramp(level, slew = 10) # slew is rate of change of voltage
#    Yoko.do_set_voltage(level)
    print m
    magnet.do_set_field(m)
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
    time.sleep(sleeptime)
    
    
    #mag.do_set_field(N) #commmand for using arduino power supply  
    Mag.append(m)
    
    datanew = VNA.do_get_data()
    valuenew = datanew[0]
    phasenew = datanew[1]
    valuenew = valuenew[:,None].T
    phasenew = phasenew[:,None].T

    value = np.concatenate([value,valuenew])
    phase = np.concatenate([phase,phasenew])
    
    m = m+step  
    
    
#print Mag
<<<<<<< HEAD
Yoko.do_set_voltage(0)

=======
#Yoko.do_set_voltage(0)
#magnet.do_ramp_zero()
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
axis = axis / float(1000000000)
X, Y = np.meshgrid(Mag, axis)
Z = np.transpose(value)
phase = np.transpose(phase)

#save the data as a file
to_save = [X, Y, Z, phase]
<<<<<<< HEAD
with file('text_1.5mm_copper_cavity_%s_%s_%s_P2.txt'%(Mi,Mf,step),'w') as outfile:
=======
with file('text_1.5mm_fridge_%s_%s_%s.txt'%(Mi,Mf,step),'w') as outfile:
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
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
pl.pcolormesh(X, Y, Z)
pl.colorbar()
<<<<<<< HEAD
pl.xlabel('Magnetic Field')
=======
pl.xlabel('Magnetic Field(T)')
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
pl.ylabel('Frequency (GHZ)')
pl.show()   


