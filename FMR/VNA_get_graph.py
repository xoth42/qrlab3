import matplotlib
matplotlib.interactive(True)

import os
from mclient import instruments
import datetime
date = datetime.datetime.now()

#Yoko = instruments.create('Yoko','Yokogawa_7651',address='GPIB1::3::INSTR')


#AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='AWG1', clock=1e9, refsrc='EXT', reffreq=10e6)


#VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')
#Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB1::11::INSTR')

VNA = instruments['VNA']

import matplotlib.pyplot as pl 
date = datetime.datetime.now()
filename = '%sdB_%s_%s_%s'%(VNA.get_power(),date.hour,date.minute,date.second)

print filename
newpath = r'C:\Users\Wang_Lab\Documents\\yingying\\0418cooldown\\%s.txt'%(filename)

if not os.path.exists(os.path.dirname(newpath)):

    os.makedirs(os.path.dirname(newpath))

data = VNA.do_get_data()
axis = VNA.do_get_xaxis()

pl.figure()
if axis[len(axis) - 1] > 10 **9:
    xaxis = axis / float(1000000000)
    pl.xlabel('frequency(GHZ)')
elif axis[len(axis) - 1] > 10 **6:
    xaxis = axis / float(1000000)
    pl.xlabel('frequency(MHZ)')


pl.plot(xaxis, data[0], label = filename[0:7])

pl.ylabel('dB')
pl.show()
pl.legend()

import numpy as np
axis = axis[:,None].T
trace = np.concatenate([axis,data]).T

np.savetxt(newpath , trace , delimiter=",") # saves data
