#Written By Tal Summer 2021.

import time
#import visa
if 1:
    import os
    try:
        from IPython import get_ipython
        get_ipython().magic('clear')
    except:
        pass

    os.system(r'C:\qrlab-3\clear.bat')
    os.system(r'C:\qrlab-3\start.bat')
    
  
    time.sleep(3)
    

from mclient import instruments

# AWG = instruments.create('AWG', 'Tektronix_AWG5014C', address='GPIB0::1::INSTR', clock=1e9, refsrc='EXT', reffreq=10e6)

#Yoko = instruments.create('Yoko','Yokogawa_7651_new',address='GPIB0::2::INSTR')

#LabBrick = instruments.create('LabBrick', 'LabBrick_RFSource', serial=18239, use_extref=False) # qubit

# readout = instruments.create('readout', 'Readout_Info', IQe=(1.0), IQg=(0.1),
#                                 IQe_radius= 1 , rfsource1='brick3', rfsource2='brick2',
#                                 pulse_len=1000, readout_chan='3m1', acq_chan='4m2')

# WF_qubit = instruments.create('WF_qubit', 'WFT1153', serial='1266', COM_adrs='COM3')

alz = instruments.create('alazar', 'Alazar_Daemon')
alz.set_ch1_range('200mV')
alz.set_ch2_range('200mV')
alz.set_nsamples(1600)
alz.set_naverages(2000)
alz.set_ch1_coupling('AC')
alz.set_ch2_coupling('AC')
alz.set_clock_source('EXT10M')
#alz.set_clock_source('INT')
alz.set_sample_rate('1GEXT10')
alz.set_engJ_trig_src('EXT')
alz.set_engJ_trig_lvl(128+5)
alz.set_real_signals(False)
alz.set_timeout(10e3)
alz.setup_clock()
alz.setup_channels()
alz.setup_trigger()


os.system(r'C:\qrlab-3\start_QRLab.bat') 