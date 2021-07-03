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
IQ_mod = instruments.create('IQ_mod', 'SC5413A', devid='10001FA5')
    
#SCsource = instruments.create('SCsource', 'SC5506A', devid='10001FA3')

instruments.remove('dig')
dig = instruments.create('dig', 'Keysight_DIG', chassis = 0, slot = 3, trigger_period =50, 
                         trigger_only = True, awg_list = [7,8,9])

#yoko = instruments.create('yoko', 'Yokogawa_gs200_downgraded', address = 'GPIB0::9::INSTR')
#yoko.do_set_source_type('current')
#yoko.do_set_current_range(10)
#yoko.do_set_voltage_limit(1)
#
#yoko = instruments.create('yoko', 'Yokogawa_7651_new', address = 'GPIB0::6::INSTR')

#
qubit1ge = instruments.create('qubit1ge', 'Qubit_Info',
                              deltaf=149.56e6,
                              pi_amp=0.127, 
                              pi2_amp=0,
                              drag=0.00,
                              pi_amp_quasilective=0, #.0356,
                              pi_amp_selective=0.00381,
                              rotation='Gaussian',
                              w=15,
                              w_quasilective=160, #120,
                              w_selective=500,
                              channels='5,6',
                              sideband_channels='I1,Q1',
                              sideband_phase=0.0)

#qubit1ge = instruments.create('qubit1ge', 'Qubit_Info',
#                              deltaf=228524449.5,
#                              pi_amp=0.078947, 
#                              pi2_amp=0,
#                              drag=0.00,
#                              pi_amp_quasilective=0, #.0356,
#                              pi_amp_selective=0,
#                              rotation='Gaussian',
#                              w=6,
#                              w_quasilective=160, #120,
#                              w_selective=400,
#                              channels='5,6',
#                              sideband_channels='I1,Q1',
#                              sideband_phase=1)

qubit1ge_2 = instruments.create('qubit1ge_2', 'Qubit_Info',
                              deltaf=149.56e6,
                              pi_amp=0.0576110068241, 
                              pi2_amp=0,
                              drag=0.00,
                              pi_amp_quasilective=.0253, #.0356,
                              pi_amp_selective=0.00171,
                              rotation='Gaussian',
                              w=15,
                              w_quasilective=160, #120,
                              w_selective=500,
                              channels='9,10',
                              sideband_channels='I2,Q2',
                              sideband_phase=0)

sq_gate1 = instruments.create('sq_gate1', 'Gate_Info',
                              deltaf=234220050.0,
                              pi_amp=0.076, 
                              pi2_amp=0.037,
                              drag=0.833,
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
                              relative_amp=1.000,
                              relative_phase=-0.4642
                              )


#sq_gate1 = instruments.create('sq_gate1', 'Gate_Info',
#                              deltaf=222.910e6,
#                              pi_amp=0.0767, 
#                              pi2_amp=0.0372,
#                              drag=0.28,
#                              sq_len=12,
#                              rotation='GaussianSquare',
#                              w=4,
#                              chop=3,
#                              channels='5,6',
#                              sideband_channels='I11,Q11',
#                              sideband_phase=1,
#                              channels2='9,10',
#                              sideband_channels2='I12,Q12',
#                              sideband_phase2=-0.22,
#                              relative_amp=1.003,
#                              relative_phase=-0.448
#                              )
#
#
#
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

#cx_gate = instruments.create('cx_gate', 'Gate_Info',
#                              deltaf=228430449.5,
#                              pi_amp=0.0782,
#                              pi2_amp=0,
#                              drag=0.08,
#                              rotation='GaussianSquare',
#                              sq_len=52,
#                              w=6,
#                              chop=3,
#                              channels='5,6',
#                              sideband_channels='I17,Q17',
#                              sideband_phase=1.0,
#                              channels2='9,10',
#                              sideband_channels2='I18,Q18',
#                              sideband_phase2=-0.22,
#                              relative_amp=4.457,
#                              relative_phase=1.01
#                              )
#
qubit2ge = instruments.create('qubit2ge', 'Qubit_Info',
                              deltaf=-288890000.0,
                              pi_amp=0.04,
                              pi2_amp=0,
                              drag=0.0,
                              pi_amp_quasilective=.0253, #.0356,
                              pi_amp_selective=0.001624,
                              rotation='Gaussian',
                              w=15,
                              w_quasilective=160, #120,
                              w_selective=400,
                              channels='5,6',
                              sideband_channels='I3,Q3',
                              sideband_phase=0)


qubit2ge_2 = instruments.create('qubit2ge_2', 'Qubit_Info',
                              deltaf=-288890000.0,
                              pi_amp=0.337918,
                              pi2_amp=0.0,
                              drag=0.0,
                              pi_amp_quasilective=.0253, #.0356,
                              pi_amp_selective=.01374,
                              rotation='Gaussian',
                              w=15,
                              w_quasilective=160, #120,
                              w_selective=400,
                              channels='9,10',
                              sideband_channels='I4,Q4',
                              sideband_phase=0.0)

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

#cancel_gate = instruments.create('cancel_gate', 'Gate_Info',
#                              deltaf=-421.75e6,
#                              pi_amp=0.07, 
#                              pi2_amp=0.00,
#                              drag=0.0,
#                              rotation='GaussianSquare',
#                              w=6,
#                               sq_len=52,
#                              chop=3,
#                              channels='7,8',
#                              sideband_channels='I19,Q19',
#                              sideband_phase=0,
#                              channels2='7,8',
#                              sideband_channels2='I20,Q20',
#                              sideband_phase2=-1.65,
#                              relative_amp=0.0,
#                              relative_phase=0
#                              )
#

sq_gate2 = instruments.create('sq_gate2', 'Gate_Info',
                              deltaf=-372910761.0,
                              pi_amp=0.33,
                              pi2_amp=0,
                              drag=-1.033,
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

sq_gate2 = instruments.create('sq_gate2', 'Gate_Info',
                              deltaf=-373520761.0,
                              pi_amp=0.324576,
                              pi2_amp=0,
                              drag=-1.05,
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



ZZ_gate = instruments.create('ZZ_gate', 'Gate_Info',
                              deltaf=1,
                              pi_amp=-0.1175, 
                              pi2_amp=0.0,
                              drag=3.1,
                              sq_len=4,
                              rotation='GaussianSquare',
                              w=12,
                              chop=3,
                              channels='11,12',
                              sideband_channels='I21,Q21',
                              sideband_phase=1,
                              channels2='7,8',
                              sideband_channels2='I22,Q22',
                              sideband_phase2=-0.22,
                              relative_amp=0.000001,
                              relative_phase=0
                              )
efinfo = instruments.create('efinfo', 'Qubit_Info',
                              deltaf=-85e6,
                              pi_amp=0.08, 
                              pi2_amp=0.0,
                              drag=0.00,
                              pi_amp_quasilective=0, #.0356,
                              pi_amp_selective=0.012,
                              rotation='Gaussian',
                              w=25,
                              w_quasilective=160, #120,
                              w_selective=150,
                              channels='11,12',
                              sideband_channels='I23,Q23',
                              sideband_phase=1)
#
#offset_info = instruments.create('offset_info', 'Qubit_Info',
#                              deltaf=0,
#                              pi_amp=0.337918,
#                              pi2_amp=0.0,
#                              drag=0.0,
#                              pi_amp_quasilective=.0253, #.0356,
#                              pi_amp_selective=.01374,
#                              rotation='Gaussian',
#                              w=6,
#                              w_quasilective=160, #120,
#                              w_selective=400,
#                              channels='11,12',
#                              sideband_channels='I23,Q24',
#                              sideband_phase=0.0)

#ZZ_info = instruments.create('ZZ_info', 'Qubit_Info',
#                              deltaf=-100000000,
#                              pi_amp=0.337918,
#                              pi2_amp=0.0,
#                              drag=0,
#                              pi_amp_quasilective=.0253, #.0356,
#                              pi_amp_selective=.01374,
#                              rotation='Gaussian',
#                              w=6,
#                              w_quasilective=160, #120,
#                              w_selective=400,
#                              channels='11,12',
#                              sideband_channels='I22,Q22',
#                              sideband_phase=0.0)
#
#

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
                              amps = [1.5, 1.5, 1.5, 1.5], ofs = [0, 0, 0, 0])

AWG2 = instruments.create('AWG2', 'Keysight_AWG', chassis = 0, slot = 7,
                              AWG_PRODUCT = "M3202A",
                              amps = [1.5,1.5,1.5,1.5], ofs = [-0.0184, 0.0355, 0, 0])

AWG3 = instruments.create('AWG3', 'Keysight_AWG', chassis = 0, slot = 9,
                              AWG_PRODUCT = "M3202A",
                              amps = [1.5,1.5,1.5,1.5], ofs = [0.00,0, 0, 0])


cool = instruments.create('cool', 'Agilent_Generator', address = 'USB0::0x0957::0x1F01::MY53270760::INSTR')
#gaius01_3 = instruments.create('gaius01_3', 'LabBrick_RFSource', serial=21514, use_extref=True)
#gaius01 = instruments.create('gaius01', 'LabBrick_RFSource', serial=21513, use_extref=True)

#
##refbrick = instruments.create('refbrick', 'LabBrick_RFSource', serial=14511, use_extref=True) 
refbrick = instruments.create('refbrick', 'LabBrick_RFSource', serial=14510, use_extref=True) 
#
RObrick = instruments.create('RObrick', 'LabBrick_RFSource', serial=17912, use_extref=True)
##control_drive = instruments.create('control_drive', 'LabBrick_RFSource', serial=21513,  use_extref=True)
#gaius01_2= instruments.create('gaius01_2', 'LabBrick_RFSource', serial=21515,  use_extref=True)
##instruments.remove('SCref')
gaius01 = instruments.create('gaius01', 'SC5511A', devid='10001D2F')
#cool = instruments.create('cool', 'Agilent_Generator', address = 'USB0::0x0957::0x1F01::MY53270760::INSTR')
# 
ZZ= instruments.create('ZZ', 'LabBrick_RFSource', serial = 21515, use_extref=True)

readout = instruments.create('readout', 'Readout_Info', IQe=(1.0), IQg=(0.1),
                              IQe_radius= 1 , rfsource1='RObrick',
                              rfsource2='refbrick',
                              pulse_len=2000, readout_chan='1m1', acq_chan='2m1')


#spike = instruments.create('spike', 'SignalHound_Spike', address = 'TCPIP::localhost::5025::SOCKET')


#1400
#WF_xxx = instruments.create('WF_xxx', 'WFT1153', serial = '1153')

instruments.remove('alz')
alz = instruments.create('alazar', 'Alazar_Daemon')
alz.set_ch1_range('200mV')
alz.set_ch2_range('100mV')
alz.set_nsamples(1600)
alz.set_naverages(1000)
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
