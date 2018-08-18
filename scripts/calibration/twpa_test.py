import numpy as np
import matplotlib.pyplot as pl
import mclient
import time

def take_vna():
    VNA.set_averaging_trigger(0)
    VNA.set_averaging_trigger(1)
    time.sleep(30)
    data = VNA.do_get_data(fmt='PLOG')#, opc=True, trig_each_avg=True)
    axis = VNA.do_get_xaxis()
    return axis, data

VNA = mclient.instruments['VNA']
brick = mclient.insturments['brick4']


VNA.set_average_factor(20)
VNA.do_enable_averaging()

# measure 3-10 ghz w/ no pump. find dip
brick.do_set_rf_on(False)
VNA.do_set_start_freq(3e9)
VNA.do_set_stop_freq(10e9)
x, y = take_vna()




# set pump bellow dip




# sweep power past max



# sweep frequency to max


# sweep power to max


