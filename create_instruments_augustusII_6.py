# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 10:12:30 2019

@author: wanglab
"""

import time

if 1:
    import os
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

from mclient import instruments

#SCtest = instruments.create('SCtest', 'SC5506A', devid='10001FA3')

instruments.remove('dig')
dig = instruments.create('dig', 'Keysight_DIG', chassis = 1, slot = 3, trigger_period =50, 
                         trigger_only = True, awg_list = [7,8,9])


#yoko = instruments.create('yoko', 'Yokogawa_GS200', address = 'GPIB0::9::INSTR')

#
qubit1ge = instruments.create('qubit1ge', 'Qubit_Info',
                              deltaf=216.31e6,
                              pi_amp=0.0685, 
                              pi2_amp=0.0347,
                              drag=-0.18,
                              pi_amp_quasilective=.0253, #.0356,
                              pi_amp_selective=.001025,
                              rotation='Gaussian',
                              w=6,
                              w_quasilective=160, #120,
                              w_selective=400,
                              channels='5,6',
                              sideband_channels='I1,Q1',
                              sideband_phase=0.8)



qubit1ge_2 = instruments.create('qubit1ge_2', 'Qubit_Info',
                              deltaf=216.31e6,
                              pi_amp=0.34622, 
                              pi2_amp=0,
                              drag=0,
                              pi_amp_quasilective=.0253, #.0356,
                              pi_amp_selective=.0024,
                              rotation='Gaussian',
                              w=6,
                              w_quasilective=160, #120,
                              w_selective=400,
                              channels='9,10',
                              sideband_channels='I2,Q2',
                              sideband_phase=-0.2)


#qubit1ge = instruments.create('qubit1ge', 'Qubit_Info',
#                              deltaf=-173.05e6,
#                              pi_amp=0.75310, 
#                              pi2_amp=0.34379,
#                              drag=0,
#                              pi_amp_quasilective=.0253, #.0356,
#                              pi_amp_selective=.1473,
#                              rotation='Gaussian',
#                              w=1000,
#                              w_quasilective=160, #120,
#                              w_selective=500,
#                              channels='4,4',
#                              sideband_channels='I1,Q1',
#                              sideband_phase=0.17)
#
#qubit1ef = instruments.create('qubit1ef', 'Qubit_Info',
#                            deltaf=-100e6,
#                            pi_amp=0.051,
#                            pi_amp_selective=0.01,
#                            rotation='Gaussian',
#                            w=50,
#                            w_selective=300,
#                            channels='7,8',
#                            sideband_channels='I3,Q3',
#                            sideband_phase=0)



qubit2ge = instruments.create('qubit2ge', 'Qubit_Info',
                              deltaf=-378.65e6,
                              pi_amp=0.113,
                              pi2_amp=0.0553,
                              drag=0.3,
                              pi_amp_quasilective=.0253, #.0356,
                              pi_amp_selective=0.001624,
                              rotation='Gaussian',
                              w=6,
                              w_quasilective=160, #120,
                              w_selective=400,
                              channels='5,6',
                              sideband_channels='I3,Q3',
                              sideband_phase=-1)


qubit2ge_2 = instruments.create('qubit2ge_2', 'Qubit_Info',
                              deltaf=-378.65e6,
                              pi_amp=0.3476,
                              pi2_amp=0.0,
                              drag=0,
                              pi_amp_quasilective=.0253, #.0356,
                              pi_amp_selective=.01374,
                              rotation='Gaussian',
                              w=6,
                              w_quasilective=160, #120,
                              w_selective=400,
                              channels='9,10',
                              sideband_channels='I4,Q4',
                              sideband_phase=0.0)

AWG1 = instruments.create('AWG1', 'Keysight_AWG', chassis = 0, slot = 8,
                              AWG_PRODUCT = "M3202A",
                              amps = [1.5, 1.5, 1.5, 1], ofs = [0, 0, 0, 0])

AWG2 = instruments.create('AWG2', 'Keysight_AWG', chassis = 0, slot = 7,
                              AWG_PRODUCT = "M3202A",
                              amps = [1.45,1.45,1,1], ofs = [0.016, 0.013, 0.087, -0.048])

AWG3 = instruments.create('AWG3', 'Keysight_AWG', chassis = 0, slot = 9,
                              AWG_PRODUCT = "M3202A",
                              amps = [1.34,1.5,1.5,1.5], ofs = [0.004, -0.026, 0, 0])


cool = instruments.create('cool', 'Agilent_Generator', address = 'USB0::0x0957::0x1F01::MY53270760::INSTR')
#
##refbrick = instruments.create('refbrick', 'LabBrick_RFSource', serial=14511, use_extref=True) 
refbrick = instruments.create('refbrick', 'LabBrick_RFSource', serial=14511, use_extref=True) 
#
RObrick = instruments.create('RObrick', 'LabBrick_RFSource', serial=17912, use_extref=True)
##control_drive = instruments.create('control_drive', 'LabBrick_RFSource', serial=21513,  use_extref=True)
gaius01 = instruments.create('gaius01', 'LabBrick_RFSource', serial=21513,  use_extref=True)
##instruments.remove('SCref')
#SCref = instruments.create('SCref', 'SC5511A', devid='10001D31')
#cool = instruments.create('cool', 'Agilent_Generator', address = 'USB0::0x0957::0x1F01::MY53270760::INSTR')
# 
ZZ= instruments.create('ZZ', 'LabBrick_RFSource', serial = 21515, use_extref=True)

readout = instruments.create('readout', 'Readout_Info', IQe=(1.0), IQg=(0.1),
                              IQe_radius= 1 , rfsource1='RObrick',
                              rfsource2='refbrick',
                              pulse_len=1400, readout_chan='1m1', acq_chan='2m1')
#
#WF_xxx = instruments.create('WF_xxx', 'WFT1153', serial = '1153')

instruments.remove('alz')
alz = instruments.create('alazar', 'Alazar_Daemon')
alz.set_ch1_range('200mV')
alz.set_ch2_range('100mV')
alz.set_nsamples(1600)
alz.set_naverages(5000)
alz.set_ch1_coupling('AC')
alz.set_ch2_coupling('AC')
#alz.set_clock_source('EXT10M')
alz.set_clock_source('EXT')
alz.set_sample_rate('1GEXT10')
alz.set_engJ_trig_src('EXT')
alz.set_engJ_trig_lvl(128+5)
alz.set_real_signals(False)
alz.set_timeout(10000)
alz.setup_clock()
alz.setup_channels()
alz.setup_trigger()
