import os
import time

os.system(r'C:\qrlab-3\start.bat')
time.sleep(1)

from mclient import instruments

# Real hardware connection
dig = instruments.create('dig', 'Keysight_DIG', chassis = 0, slot = 3, trigger_period = 100, trigger_only = False,
                         naverages = 1000, nsamples = 2000, awg_list = [7, 8, 9], channel_delay = 150)

AWG2 = instruments.create('AWG2', 'Keysight_AWG', chassis = 0, slot = 8,  AWG_PRODUCT = "M3202A",
                          amps = [1, 1, 1.5, 1.5], ofs = [0.02, 0.008, -0.01, -0.067])

SCtest = instruments.create('SCtest', 'SC5511A', devid='10001C09')


# Virtual instruments for control
readout_IQ = instruments.create('readout_IQ', 'Readout_IQ_Info', IQe=(1.0), IQg=(0.1),
                                IQe_radius= 1 ,
                                rfsource='SCtest',
                                acq_chan='1m1',
                                deltaf=50e6,
                                channels='7,8',
                                sideband_phase=0,
                                pulse_width=4500,
                                sigma=10,
                                amp=.4,
                                fixed_phase=0,
                                )

