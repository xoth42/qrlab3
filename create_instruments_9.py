#Written By Tal Summer 2021.

import time


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

if 1:  ### AWG
    AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='GPIB0::1::INSTR', clock=1e9, refsrc='EXT', reffreq=10e6)

if 1:  ### Lab Brick
    LabBrick = instruments.create('LabBrick', 'LabBrick_RFSource', serial=18239, use_extref=False) 

if 1:  ### Wind Freak
    WindFreak = instruments.create('WindFreak', 'WFT1153', channel_index = 0, serial='1266', COM_adrs='COM3')

if 0:  ### Alazar
    alz = instruments.create('alazar', 'Alazar_Daemon')
    alz.set_ch1_range('200mV')
    alz.set_ch2_range('200mV')
    alz.set_nsamples(1600)
    alz.set_naverages(2000)
    alz.set_ch1_coupling('AC')
    alz.set_ch2_coupling('AC')
    alz.set_clock_source('EXT10M')
    alz.set_sample_rate('1GEXT10')
    alz.set_engJ_trig_src('EXT')
    alz.set_engJ_trig_lvl(128+5)
    alz.set_real_signals(False)
    alz.set_timeout(10e3)
    alz.setup_clock()
    alz.setup_channels()
    alz.setup_trigger()

if 0:  ### Yoko
    Yoko = instruments.create('Yoko','Yokogawa_7651_new',address='GPIB0::2::INSTR')

if 1:  ### Readout
    readout = instruments.create('readout', 'Readout_Info', IQe=(1.0), IQg=(0.1),
                                IQe_radius= 1 , rfsource1='LabBrick', rfsource2='WindFreak',
                                pulse_len=1000, readout_chan='2m1', acq_chan='1m1')

if 1:  ### Qubit1ge
    qubit1ge = instruments.create('qubit1ge', 'Qubit_Info',
                              deltaf=-100e6,
                              pi_amp=0.137,
                              pi2_amp=0,
                              drag=0,
                              pi_amp_quasilective=.01,
                              pi_amp_selective=.8,
                              rotation='Gaussian',
                              w=20,
                              w_quasilective=160, #120,
                              w_selective=100,
                              channels='1,2',
                              sideband_channels='I1,Q1',
                              sideband_phase=-0.15)

os.system(r'C:\qrlab-3\start_QRLab.bat') 