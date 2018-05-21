import matplotlib
matplotlib.interactive(True)

import os
<<<<<<< HEAD
from mclient import instruments

=======
import mclient
import time
import numpy as np
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
#Yoko = instruments.create('Yoko','Yokogawa_7651',address='GPIB1::3::INSTR')


#AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='AWG1', clock=1e9, refsrc='EXT', reffreq=10e6)


#VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')
#Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB1::11::INSTR')
<<<<<<< HEAD

VNA = instruments['VNA']

import matplotlib.pyplot as pl 

filename = 'S12_-65dB'
newpath = r'C:\Users\Wang_Lab\Documents\yingying\FMR\cavity mode RT\%s.txt'%(filename)
=======
VNA = mclient.instruments['VNA']


import matplotlib.pyplot as pl 
#VNA.do_power_sweep(10, -10, -1)
#==============================================================================
# for i, power in enumerate(np.arange(-35, 15, 5)):
#     VNA.set_power(power)
# #    VNA.set_average_factor(30)
#     if power<-30:
#         time.sleep(200)
#     else:
#         time.sleep(20)
# #        yield self.do_get_data()
# #VNA.set_power(0)
#==============================================================================
power = -25
temp = 19400
filename = 'S12_fridge_%sdB_%smK'%(power,temp)
#    filename = 'S12_fridge_220mode_-35dB'
newpath = r'C:\qrlab\FMR\mode near FMR\%s.txt'%(filename)
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7

if not os.path.exists(os.path.dirname(newpath)):

    os.makedirs(os.path.dirname(newpath))

data = VNA.do_get_data()
axis = VNA.do_get_xaxis()

pl.figure()
if axis[len(axis) - 1] > 10 **9:
    axis = axis / float(1000000000)
    pl.xlabel('frequency(GHZ)')
elif axis[len(axis) - 1] > 10 **6:
    axis = axis / float(1000000)
    pl.xlabel('frequency(MHZ)')


pl.plot(axis, data[0], label = filename)

pl.ylabel('dB')
#pl.show()
pl.legend()

<<<<<<< HEAD
import numpy as np
=======
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
axis = axis[:,None].T
trace = np.concatenate([axis,data]).T

np.savetxt(newpath , trace , delimiter=",") # saves data
<<<<<<< HEAD
=======
    

>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
