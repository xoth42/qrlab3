import mclient
reload(mclient)
import numpy as np
import matplotlib
matplotlib.rcParams['backend'] = 'Qt4Agg'
matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt

import math as math
import time
from matplotlib import gridspec
import lmfit


import os
os.chdir(r'c:\qrlab')


qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
qubit2_info = mclient.get_qubit_info('qubit2ge')
ef_info = mclient.get_qubit_info('qubit1ef')
dig = mclient.instruments['dig']
raspi = mclient.instruments['raspi']
Agilent1 = mclient.instruments['Agilent1']
Agilent2 = mclient.instruments['Agilent2']
Agilent3 = mclient.instruments['Agilent3']
Keithley = mclient.instruments['Keithley']
                                
# Sweep Raspberry Pi parameter(s) and record currents
def raspi_param_sweep(raspi_instr, bias_instr, analogpwr_instr, vcc1_instr, vcc23_instr, csvfile, param, start, stop):
    try:
        params, chip_data = raspi.import_data_(csvfile)
        wait_time = 0.5
        index_to_sweep = params.index(param)
        sweep_range = np.linspace(start, stop, stop-start+1)
        currents = []
        
        
        chip_data = [int(0*chip_data[x]) for x in range(len(chip_data))]
        time.sleep(wait_time)
        currents.append([float(bias_instr.do_get_current()), float(analogpwr_instr.do_get_current()), float(vcc1_instr.do_get_current()), float(vcc23_instr.do_get_current())])
        
        for i in range(len(sweep_range)):
            data[index_to_sweep] = int(sweep_range[i])
            raspi_instr.send_data_(chip_data)
            time.sleep(wait_time)
            currents.append([float(bias_instr.do_get_current()), float(analogpwr_instr.do_get_current()), float(vcc1_instr.do_get_current()), float(vcc23_instr.do_get_current())])
            print(i, currents[i])
#        tstamp = time.strftime("%D%T")
#        filename = 'C:\qrlab\scripts\ROIC\currents_sweep_' + param + str(tstamp) + '.csv'
#        np.savetxt(filename, currents)
        return 1
    except Exception as e:
        print(e)
        return -1



# 
raspi = mclient.instruments['raspi']
raspi.do_set_domain('172.30.52.81')
raspi.do_set_password('rafiki789')
raspi.connect_ssh()

Agilent1 = mclient.instruments['Agilent1']
Agilent2 = mclient.instruments['Agilent2']
Agilent3 = mclient.instruments['Agilent3']
Keithley = mclient.instruments['Keithley']
wait_time = 0.5
params, data = raspi.import_data_('C:\qrlab\scripts\ROIC\spi_iface-main\default_2.csv')
data = [int(0*data[x]) for x in range(len(data))]

current = float(Agilent1.do_get_current())
target_current = 1e-3
    
    