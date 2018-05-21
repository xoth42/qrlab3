# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 16:55:53 2017

@author: WangLab
"""
from mclient import instruments
# initialize VNA, pull whatever data is on the screen, plot and save it
VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')
data = VNA.do_get_data()
import numpy as np
np.savetxt("0815_hanger_magshield_cold", data[0])
import matplotlib.pyplot as pl
# pl.plot(range(len(data[0])), data[0])
# pl.show()



# rescale x-axis
y = np.loadtxt('0815_hanger_magshield_cold', unpack=True)
cf = 8.5901166e9
span = 50000
x = np.linspace(cf-span, cf+span, 1601)
pl.plot(x, y)
pl.title('0815_hanger_magshield_cold, -40dBm')
pl.xlabel('GHz')
pl.ylabel('dB')
print 'before'
pl.show()
print 'after'
bla