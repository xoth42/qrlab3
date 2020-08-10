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
dig = instruments.create('dig', 'Keysight_DIG', chassis = 0, slot = 3, trigger_period =50, 
                         trigger_only = True, awg_list = [7,8,9])


#yoko = instruments.create('yoko', 'Yokogawa_GS200', address = 'GPIB0::9::INSTR')

#
#qubit1ge = instruments.create('qubit1ge', 'Qubit_Info',
#                              deltaf=228524449.5,
#                              pi_amp=0.078947, 
#                              pi2_amp=0.0347,
#                              drag=0.08,
#                              pi_amp_quasilective=.0253, #.0356,
#                              pi_amp_selective=.001025,
#                              rotation='Gaussian',
#                              w=6,
#                              w_quasilective=160, #120,
#                              w_selective=400,
#                              channels='5,6',
#                              sideband_channels='I1,Q1',
#                              sideband_phase=1)
#
#qubit1ge_2 = instruments.create('qubit1ge_2', 'Qubit_Info',
#                              deltaf=228524449.5,
#                              pi_amp=0.362732, 
#                              pi2_amp=0,
#                              drag=0.08,
#                              pi_amp_quasilective=.0253, #.0356,
#                              pi_amp_selective=.0024,
#                              rotation='Gaussian',
#                              w=6,
#                              w_quasilective=160, #120,
#                              w_selective=400,
#                              channels='9,10',
#                              sideband_channels='I2,Q2',
#                              sideband_phase=-0.22)

sq_gate1 = instruments.create('sq_gate1', 'Gate_Info',
                              deltaf=228430449.5,
                              pi_amp=0.0755, 
                              pi2_amp=0.03753,
                              drag=-0.075,
                              sq_len=12,
                              rotation='GaussianSquare',
                              w=4,
                              chop=3,
                              channels='5,6',
                              sideband_channels='I11,Q11',
                              sideband_phase=1,
                              channels2='9,10',
                              sideband_channels2='I12,Q12',
                              sideband_phase2=-0.22,
                              relative_amp=1.015,
                              relative_phase=1.004
                              )
#
#zx90_gate = instruments.create('zx90_gate', 'Gate_Info',
#                              deltaf=228414449.5,
#                              pi_amp=0.0778,
#                              pi2_amp=0,
#                              drag=0.08,
#                              rotation='GaussianSquare',
#                              sq_len=24,
#                              w=6,
#                              chop=3,
#                              channels='5,6',
#                              sideband_channels='I15,Q15',
#                              sideband_phase=1.0,
#                              channels2='9,10',
#                              sideband_channels2='I16,Q16',
#                              sideband_phase2=-0.22,
#                              relative_amp=4.452,
#                              relative_phase=1.004
#                              )

cx_gate = instruments.create('cx_gate', 'Gate_Info',
                              deltaf=228430449.5,
                              pi_amp=0.0782,
                              pi2_amp=0,
                              drag=0.08,
                              rotation='GaussianSquare',
                              sq_len=52,
                              w=6,
                              chop=3,
                              channels='5,6',
                              sideband_channels='I17,Q17',
                              sideband_phase=1.0,
                              channels2='9,10',
                              sideband_channels2='I18,Q18',
                              sideband_phase2=-0.22,
                              relative_amp=4.457,
                              relative_phase=1.01
                              )
#
#qubit2ge = instruments.create('qubit2ge', 'Qubit_Info',
#                              deltaf=-373754763.7,
#                              pi_amp=0.121872,
#                              pi2_amp=0,
#                              drag=0.58,
#                              pi_amp_quasilective=.0253, #.0356,
#                              pi_amp_selective=0.001624,
#                              rotation='Gaussian',
#                              w=6,
#                              w_quasilective=160, #120,
#                              w_selective=400,
#                              channels='5,6',
#                              sideband_channels='I3,Q3',
#                              sideband_phase=-1.65)
#
#
#qubit2ge_2 = instruments.create('qubit2ge_2', 'Qubit_Info',
#                              deltaf=-373754763.7,
#                              pi_amp=0.337918,
#                              pi2_amp=0.0,
#                              drag=0.6,
#                              pi_amp_quasilective=.0253, #.0356,
#                              pi_amp_selective=.01374,
#                              rotation='Gaussian',
#                              w=6,
#                              w_quasilective=160, #120,
#                              w_selective=400,
#                              channels='9,10',
#                              sideband_channels='I4,Q4',
#                              sideband_phase=0.0)

#cancel_gate = instruments.create('qubit2_phase', 'Qubit_Info',
#                              deltaf=-373.75e6+30e6,
#                              pi_amp=0.343941007757,
#                              pi2_amp=0.0,
#                              drag=0.6,
#                              pi_amp_quasilective=.0253, #.0356,
#                              pi_amp_selective=.01374,
#                              rotation='Gaussian',
#                              w=4,
#                              w_quasilective=160, #120,
#                              w_selective=400,
#                              channels='9,10',
#                              sideband_channels='I5,Q5',
#                              sideband_phase=0.0)

cancel_gate = instruments.create('cancel_gate', 'Gate_Info',
                              deltaf=-421.75e6,
                              pi_amp=0.07, 
                              pi2_amp=0.00,
                              drag=0.0,
                              rotation='GaussianSquare',
                              w=6,
                              sq_len=52,
                              chop=3,
                              channels='9,10',
                              sideband_channels='I19,Q19',
                              sideband_phase=0,
                              channels2='5,6',
                              sideband_channels2='I20,Q20',
                              sideband_phase2=-1.65,
                              relative_amp=0.0,
                              relative_phase=0
                              )


sq_gate2 = instruments.create('sq_gate2', 'Gate_Info',
                              deltaf=-3373760763.7,
                              pi_amp=0.305,
                              pi2_amp=0.1579,
                              drag=-0.3,
                              rotation='GaussianSquare',
                              w=6,
                              sq_len=6,
                              chop=3,
                              channels='9,10',
                              sideband_channels='I13,Q13',
                              sideband_phase=0,
                              channels2='5,6',
                              sideband_channels2='I14,Q14',
                              sideband_phase2=-1.65,
                              relative_amp=0.0000001,
                              relative_phase=0
                              )

#
#ZX90_Echo = instruments.create('ZX90_Echo', 'Gate_Info',
#                              deltaf=228499584.324,
#                              pi_amp=0.0778,
#                              pi2_amp=0,
#                              drag=0.08,
#                              rotation='GaussianSquare',
#                              sq_len=50,
#                              w=6,
#                              chop=3,
#                              channels='5,6',
#                              sideband_channels='I15,Q15',
#                              sideband_phase=1.0,
#                              channels2='9,10',
#                              sideband_channels2='I16,Q16',
#                              sideband_phase2=-0.22,
#                              relative_amp=5.03,
#                              relative_phase=0.988
#                              )
#

AWG1 = instruments.create('AWG1', 'Keysight_AWG', chassis = 0, slot = 8,
                              AWG_PRODUCT = "M3202A",
                              amps = [1.5, 1.5, 1.5, 1], ofs = [0, 0, 0, 0])

AWG2 = instruments.create('AWG2', 'Keysight_AWG', chassis = 0, slot = 7,
                              AWG_PRODUCT = "M3202A",
                              amps = [1.2,1.5,1,1], ofs = [0.016, 0.013, 0.087, -0.048])

AWG3 = instruments.create('AWG3', 'Keysight_AWG', chassis = 0, slot = 9,
                              AWG_PRODUCT = "M3202A",
                              amps = [1.36,1.5,1.5,1.5], ofs = [0.004, -0.026, 0, 0])


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
