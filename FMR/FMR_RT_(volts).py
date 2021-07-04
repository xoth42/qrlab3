import matplotlib
matplotlib.interactive(True)

#
from mclient import instruments
VNA = instruments['VNA']
Yoko = instruments['Yoko']

'''import time


    #import visa
if 1:
        import os
        os.system(r'C:\qrlab\start.bat')
        time.sleep(1)
    '''
#from mclient import instruments
#    
#    #Yoko = instruments.create('Yoko','Yokogawa_7651',address='GPIB1::3::INSTR')
#    
#    
#    #AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='AWG1', clock=1e9, refsrc='EXT', reffreq=10e6)
#    
#    
#VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')
##Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB1::11::INSTR')
#Yoko = instruments.create('Yoko','Yokogawa_7651',address='GPIB1::6::INSTR')  # NO. 2


#import mclient
import numpy as np
import datetime
import time
import matplotlib.pyplot as pl

date = datetime.datetime.now()



#Make sure to check that repeat is off for Yoko GS200
#To do manually, press 'Program' key and press repeat is the left most option on screen

#mag = mclient.instruments['Magnet']
#yoko = mclient.instruments['Yoko']
#VNA = mclient.instruments['VNA']

#Mi = float(0)  #initial field
#Mf = float(525) #final field

#Vi = 4.0
#Vf = 5.7
I_i = 0.0 #Current - switched to controlling current on 2/1/19
I_f = 0.2


#step = 1e-3
step = 0.002
sleeptime = 7

#foldername = 'C:\Users\WangLab\Documents\\yingying\\circulator\\20190109' 
foldername = r"C:\Users\WangLab\Documents\TConnolly\calibrated_circulator\transition1-3"
#filename = '%s\\circulator_S11_4_14_%s_%s_%s_7.5mm_pins_port3_terminated_%s-%s-%s.txt'%(foldername,Vi,Vf,step,date.hour,date.minute,date.second)
#Check and change angle before running angular experiments
filename = '%s\\s11_2_term%s-%s-%s_Date_%s-%s_%s-%s-%s.txt'%(foldername,I_i,I_f,step,date.month,date.day,date.hour,date.minute,date.second)

  #magnetic field step
#range = yoko.select_voltage_range(10)
#yoko.do_set_source_range(range)

#m = Mi  
#v = Vi
VNA.set_s_param('S11')
Yoko.do_set_output_state(1)
I = I_i
Yoko.do_set_current(I)
#Yoko.do_set_voltage(v)
#Yoko.do_set_voltage(m/float(40))

#Yoko.set_voltage_ramp(v,slew=1)
time.sleep(sleeptime) #+np.abs(v-float(Yoko.do_get_voltage())))  #yoko NO. 2 cannot do_get_voltage()
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
    
#    Yoko.do_set_source_range('10E+0') # fixes range problem
#    Yoko.set_voltage_ramp(level, slew = 10) # slew is rate of change of voltage
    Yoko.do_set_current(I)
    time.sleep(sleeptime)
    
    
    #mag.do_set_field(N) #commmand for using arduino power supply  
    Mag.append(I)
    
    datanew = VNA.do_get_data()
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
#        print('done')
    
    
#print Mag
#Yoko.do_set_voltage(0)
#Yoko.set_voltage_ramp(0,slew=1) #Only for YOKO GS200


#axis = axis / float(1000000000)
X, Y = np.meshgrid(Mag, axis)
Z = np.transpose(value)
phase = np.transpose(phase)

#save the data as a file
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
pl.pcolormesh(X, Y, Z)
pl.colorbar()
pl.xlabel('Magnetic Field Current (mA)')
pl.ylabel('Frequency')
pl.show()   

vlist = np.arange(I,I_i,-step) 
for i in vlist[1:]:
    print(i)
    Yoko.do_set_current(i)
    time.sleep(0.1)

    
#------------------------------------

date = datetime.datetime.now()



#Make sure to check that repeat is off for Yoko GS200
#To do manually, press 'Program' key and press repeat is the left most option on screen

#mag = mclient.instruments['Magnet']
#yoko = mclient.instruments['Yoko']
#VNA = mclient.instruments['VNA']

#Mi = float(0)  #initial field
#Mf = float(525) #final field

#Vi = 4.0
#Vf = 5.7
I_i = 0.0 #Current - switched to controlling current on 2/1/19
I_f = 0.2


#step = 1e-3
step = 0.002
sleeptime = 7
#foldername = 'C:\Users\WangLab\Documents\\yingying\\circulator\\20190109'
#foldername = r"C:\Users\WangLab\Documents\TConnolly\calibrated_circulator\transition1-3"
#filename = '%s\\circulator_S11_4_14_%s_%s_%s_7.5mm_pins_port3_terminated_%s-%s-%s.txt'%(foldername,Vi,Vf,step,date.hour,date.minute,date.second)
#Check and change angle before running angular experiments
filename = '%s\\s21_2_term%s-%s-%s_Date_%s-%s_%s-%s-%s.txt'%(foldername,I_i,I_f,step,date.month,date.day,date.hour,date.minute,date.second)
  #magnetic field step
#range = yoko.select_voltage_range(10)
#yoko.do_set_source_range(range)
VNA.set_s_param('S21')
#m = Mi  
#v = Vi
#Yoko.do_set_output_state(1)
I = I_i
Yoko.do_set_current(I)
#Yoko.do_set_voltage(v)
#Yoko.do_set_voltage(m/float(40))

#Yoko.set_voltage_ramp(v,slew=1)
time.sleep(sleeptime) #+np.abs(v-float(Yoko.do_get_voltage())))  #yoko NO. 2 cannot do_get_voltage()
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
    
#    Yoko.do_set_source_range('10E+0') # fixes range problem
#    Yoko.set_voltage_ramp(level, slew = 10) # slew is rate of change of voltage
    Yoko.do_set_current(I)
    time.sleep(sleeptime)
    
    
    #mag.do_set_field(N) #commmand for using arduino power supply  
    Mag.append(I)
    
    datanew = VNA.do_get_data()
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
#        print('done')
    
    
#print Mag
#Yoko.do_set_voltage(0)
#Yoko.set_voltage_ramp(0,slew=1) #Only for YOKO GS200


#axis = axis / float(1000000000)
X, Y = np.meshgrid(Mag, axis)
Z = np.transpose(value)
phase = np.transpose(phase)

#save the data as a file
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
pl.pcolormesh(X, Y, Z)
pl.colorbar()
pl.xlabel('Magnetic Field Current (mA)')
pl.ylabel('Frequency')
pl.show()   

vlist = np.arange(I,I_i,-step) 
for i in vlist[1:]:
    print(i)
    Yoko.do_set_current(i)
    time.sleep(0.1)

#------------------------------------

date = datetime.datetime.now()



#Make sure to check that repeat is off for Yoko GS200
#To do manually, press 'Program' key and press repeat is the left most option on screen

#mag = mclient.instruments['Magnet']
#yoko = mclient.instruments['Yoko']
#VNA = mclient.instruments['VNA']

#Mi = float(0)  #initial field
#Mf = float(525) #final field

#Vi = 4.0
#Vf = 5.7
I_i = 0.0 #Current - switched to controlling current on 2/1/19
I_f = 0.2


#step = 1e-3
step = 0.002
sleeptime = 7
#foldername = 'C:\Users\WangLab\Documents\\yingying\\circulator\\20190109'
#foldername = r"C:\Users\WangLab\Documents\TConnolly\calibrated_circulator\transition1-3"
#filename = '%s\\circulator_S11_4_14_%s_%s_%s_7.5mm_pins_port3_terminated_%s-%s-%s.txt'%(foldername,Vi,Vf,step,date.hour,date.minute,date.second)
#Check and change angle before running angular experiments
filename = '%s\\s12_2_term%s-%s-%s_Date_%s-%s_%s-%s-%s.txt'%(foldername,I_i,I_f,step,date.month,date.day,date.hour,date.minute,date.second)
  #magnetic field step
#range = yoko.select_voltage_range(10)
#yoko.do_set_source_range(range)
VNA.set_s_param('S12')
#m = Mi  
#v = Vi
#Yoko.do_set_output_state(1)
I = I_i
Yoko.do_set_current(I)
#Yoko.do_set_voltage(v)
#Yoko.do_set_voltage(m/float(40))

#Yoko.set_voltage_ramp(v,slew=1)
time.sleep(sleeptime) #+np.abs(v-float(Yoko.do_get_voltage())))  #yoko NO. 2 cannot do_get_voltage()
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
    
#    Yoko.do_set_source_range('10E+0') # fixes range problem
#    Yoko.set_voltage_ramp(level, slew = 10) # slew is rate of change of voltage
    Yoko.do_set_current(I)
    time.sleep(sleeptime)
    
    
    #mag.do_set_field(N) #commmand for using arduino power supply  
    Mag.append(I)
    
    datanew = VNA.do_get_data()
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
#        print('done')
    
    
#print Mag
#Yoko.do_set_voltage(0)
#Yoko.set_voltage_ramp(0,slew=1) #Only for YOKO GS200


#axis = axis / float(1000000000)
X, Y = np.meshgrid(Mag, axis)
Z = np.transpose(value)
phase = np.transpose(phase)

#save the data as a file
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
pl.pcolormesh(X, Y, Z)
pl.colorbar()
pl.xlabel('Magnetic Field Current (mA)')
pl.ylabel('Frequency')
pl.show()   

vlist = np.arange(I,I_i,-step) 
for i in vlist[1:]:
    print(i)
    Yoko.do_set_current(i)
    time.sleep(0.1)

#------------------------------------

date = datetime.datetime.now()



#Make sure to check that repeat is off for Yoko GS200
#To do manually, press 'Program' key and press repeat is the left most option on screen

#mag = mclient.instruments['Magnet']
#yoko = mclient.instruments['Yoko']
#VNA = mclient.instruments['VNA']

#Mi = float(0)  #initial field
#Mf = float(525) #final field

#Vi = 4.0
#Vf = 5.7
I_i = 0.0 #Current - switched to controlling current on 2/1/19
I_f = 0.2


#step = 1e-3
step = 0.002
sleeptime = 7
#foldername = 'C:\Users\WangLab\Documents\\yingying\\circulator\\20190109'
#foldername = r"C:\Users\WangLab\Documents\TConnolly\calibrated_circulator\transition1-3"
#filename = '%s\\circulator_S11_4_14_%s_%s_%s_7.5mm_pins_port3_terminated_%s-%s-%s.txt'%(foldername,Vi,Vf,step,date.hour,date.minute,date.second)
#Check and change angle before running angular experiments
filename = '%s\\s22_2_term%s-%s-%s_Date_%s-%s_%s-%s-%s.txt'%(foldername,I_i,I_f,step,date.month,date.day,date.hour,date.minute,date.second)
  #magnetic field step
#range = yoko.select_voltage_range(10)
#yoko.do_set_source_range(range)
VNA.set_s_param('S22')
#m = Mi  
#v = Vi
#Yoko.do_set_output_state(1)
I = I_i
Yoko.do_set_current(I)
#Yoko.do_set_voltage(v)
#Yoko.do_set_voltage(m/float(40))

#Yoko.set_voltage_ramp(v,slew=1)
time.sleep(sleeptime) #+np.abs(v-float(Yoko.do_get_voltage())))  #yoko NO. 2 cannot do_get_voltage()
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
    
#    Yoko.do_set_source_range('10E+0') # fixes range problem
#    Yoko.set_voltage_ramp(level, slew = 10) # slew is rate of change of voltage
    Yoko.do_set_current(I)
    time.sleep(sleeptime)
    
    
    #mag.do_set_field(N) #commmand for using arduino power supply  
    Mag.append(I)
    
    datanew = VNA.do_get_data()
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
#        print('done')
    
    
#print Mag
#Yoko.do_set_voltage(0)
#Yoko.set_voltage_ramp(0,slew=1) #Only for YOKO GS200


#axis = axis / float(1000000000)
X, Y = np.meshgrid(Mag, axis)
Z = np.transpose(value)
phase = np.transpose(phase)

#save the data as a file
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
pl.pcolormesh(X, Y, Z)
pl.colorbar()
pl.xlabel('Magnetic Field Current (mA)')
pl.ylabel('Frequency')
pl.show()   

vlist = np.arange(I,I_i,-step) 
for i in vlist[1:]:
    print(i)
    Yoko.do_set_current(i)
    time.sleep(0.1)
