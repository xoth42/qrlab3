import matplotlib
matplotlib.interactive(True)


from mclient import instruments

#Yoko = instruments.create('Yoko','Yokogawa_7651',address='GPIB1::3::INSTR')


#AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='AWG1', clock=1e9, refsrc='EXT', reffreq=10e6)


#VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')
#Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB1::11::INSTR')

VNA = instruments['VNA']

import matplotlib.pyplot as pl

data = VNA.do_get_data()
axis = VNA.do_get_xaxis()


if axis[len(axis) - 1] > 10 **9:
    axis = axis / float(1000000000)
    pl.xlabel('frequency(GHZ)')
else:
    axis = axis / float(1000000)
    pl.xlabel('frequency(MHZ)')


pl.plot(axis, data[0])

pl.ylabel('dB')
#pl.show()


import numpy as np
axis = axis[:,None].T
trace = np.concatenate([axis,data]).T
np.savetxt(r'trace.txt' , trace , delimiter=",") # saves data
