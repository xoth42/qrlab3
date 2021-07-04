import numpy as np
import matplotlib.pyplot as pl
import mclient
import time

def take_vna():
    VNA.set_averaging_trigger(0)
    VNA.set_averaging_trigger(1)
    VNA.set_averaging_trigger(0)
    time.sleep(2) 
    data = VNA.do_get_data(fmt='PLOG')#, opc=True, trig_each_avg=True)
    axis = VNA.do_get_xaxis()
    return axis, data[0]

VNA = mclient.instruments['VNA']
#brick = mclient.instruments['brick4']
SCpump = mclient.instruments['SCpump']


VNA.set_average_factor(20)   # NEEDS TO BE SET EACH TIME, change sleep time also
VNA.do_enable_averaging()

# measure 3-10 ghz w/ no pump. find dip
if 0:
    SCpump.do_set_rf_on(False)
    VNA.set_start_freq(3e9)
    VNA.set_stop_freq(10e9)
    VNA.set_power(-50)
    x, y = take_vna()
    
    pl.plot(x, y)
    pl.show()



# set pump bellow dip. sweep power past max
if 1:
    pl.clf()
    pump_freq = 6.22e9  # NEEDS TO BE SET EACH TIME
    pump_powers = np.linspace(-5, 5, 11)  # NEEDS TO BE SET EACH TIME
    VNA.set_start_freq(3e9)
    VNA.set_stop_freq(10e9)
    VNA.set_power(-50)
    SCpump.do_set_power(-40)
    SCpump.do_set_rf_on(True)
    
    SCpump.do_set_frequency(pump_freq)
    
    x = VNA.do_get_xaxis()
    traces = np.zeros((len(pump_powers), len(x)))
    for i in range(len(pump_powers)):
        print((i+1, len(pump_powers)))
        SCpump.do_set_power(pump_powers[i])
        time.sleep(1.5)
        traces[i] = take_vna()[1]
    
        pl.plot(x, traces[i], label = str(pump_powers[i]))
    
    pl.legend()
    pl.show()


# sweep frequency to max
if 0:
    VNA.set_start_freq(3e9)
    VNA.set_stop_freq(10e9)
    VNA.set_power(-50)
    pump_power = 1
    SCpump.do_set_power(pump_power)  # NEEDS TO BE SET EACH TIME
    pump_freqs = np.linspace(6e9, 6.4e9, 41)  # NEEDS TO BE SET EACH TIME
    SCpump.do_set_rf_on(True)
    
    x = VNA.do_get_xaxis()
    traces = np.zeros((len(pump_freqs), len(x)))
    pl.clf()
    for i in range(len(pump_freqs)):
        print((i+1, len(pump_freqs)))
        SCpump.do_set_frequency(pump_freqs[i])
        time.sleep(1.5)
        traces[i] = take_vna()[1]
    
    mesh_x, mesh_y = np.meshgrid(x, pump_freqs)
    pl.pcolormesh(mesh_x, mesh_y, traces)
    pl.colorbar()
    pl.xlabel('probe frequency')
    pl.ylabel('pump frequency')
    pl.title(str(pump_power) + 'dbm')
    
# sweep power to max
if 0:
    pl.clf()
    pump_freq = 6.22e9  # NEEDS TO BE SET EACH TIME
    pump_powers = np.arange(0, 6, .2)  # NEEDS TO BE SET EACH TIME
    VNA.set_start_freq(3e9)
    VNA.set_stop_freq(10e9)
    VNA.set_power(-50)
    SCpump.do_set_power(-40)
    SCpump.do_set_rf_on(True)
    
    SCpump.do_set_frequency(pump_freq)
    
    x = VNA.do_get_xaxis()
    power_traces = np.zeros((len(pump_powers), len(x)))
    for i in range(len(pump_powers)):
        print((i+1, len(pump_powers)))
        SCpump.do_set_power(pump_powers[i])
        time.sleep(1)
        power_traces[i] = take_vna()[1]
    
    mesh_x, mesh_y = np.meshgrid(x, pump_powers)
    pl.pcolormesh(mesh_x, mesh_y, power_traces)
    pl.colorbar()
    pl.xlabel('probe frequency')
    pl.ylabel('pump power')
    pl.title(str(pump_freq) + 'dbm')
    

