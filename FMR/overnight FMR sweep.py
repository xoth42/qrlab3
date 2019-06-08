# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 19:11:58 2019

@author: Wang_Lab
"""
VNA.set_power(0)
VNA =  mclient.instruments['VNA']
from scripts.single_cavity import Magnet_sweep_VNA
VNA.set_timeout(40000)
VNA.do_enable_averaging(True)
VNA.set_averaging_trigger(1)
VNA.set_trigger_source('internal')

a = [0]
a[0] = np.linspace(0.23,0.3,351)
#    a[1] = np.linspace(0.1,0,101)
#    a[2] = np.linspace(0,-0.1,101)
#    a[3] = np.linspace(-0.1,0,101)
for i in range(len(a)):
    
#    a= np.log10(a)*10
#    a[0] = -11
    ro = Magnet_sweep_VNA.Magnet_Sweep_VNA(fields = a[i], freqs = np.linspace(7e9, 9e9, 1601),
                                                   average_factor =1, avelimit =1,if_bandwidth = 1000, Sij =['S21'],fig_name ='field sweep',comment = 'Yig cavity')
    #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
    ro.measure()
    pl.show()



VNA.set_power(-25)
from scripts.single_cavity import Magnet_sweep_VNA
VNA.set_timeout(40000)
VNA.do_enable_averaging(True)
VNA.set_averaging_trigger(1)
VNA.set_trigger_source('internal')

a = [0]
a[0] = np.linspace(0.23,0.3,101)
#    a[1] = np.linspace(0.1,0,101)
#    a[2] = np.linspace(0,-0.1,101)
#    a[3] = np.linspace(-0.1,0,101)
for i in range(len(a)):
    
#    a= np.log10(a)*10
#    a[0] = -11
    ro = Magnet_sweep_VNA.Magnet_Sweep_VNA(fields = a[i], freqs = np.linspace(7e9, 9e9, 1601),
                                                   average_factor =100, avelimit =10,if_bandwidth = 1000, Sij =['S21'],fig_name ='field sweep',comment = 'Yig cavity')
    #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
    ro.measure()
    pl.show()
    
    
    
from scripts.single_cavity import Magnet_sweep_VNA
VNA.set_timeout(40000)
VNA.do_enable_averaging(True)
VNA.set_averaging_trigger(1)
VNA.set_trigger_source('internal')

a = [0]
a[0] = np.linspace(0.23,0.3,101)
#    a[1] = np.linspace(0.1,0,101)
#    a[2] = np.linspace(0,-0.1,101)
#    a[3] = np.linspace(-0.1,0,101)
for i in range(len(a)):
    
#    a= np.log10(a)*10
#    a[0] = -11
    ro = Magnet_sweep_VNA.Magnet_Sweep_VNA(fields = a[i], freqs = np.linspace(8e9, 8.5e9, 1601),
                                                   average_factor =100, avelimit =10,if_bandwidth = 1000, Sij =['S21'],fig_name ='field sweep',comment = 'Yig cavity')
    #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
    ro.measure()
    pl.show()