import time

if 1:
    import os
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

from .mclient import instruments

#SC_mod_test = instruments.create('SC_mod_test', 'SC5413A', devid='10001FA5')


#raspi = instruments.create('raspi', 'raspi_manager')

WF_qubit = instruments.create('WF_qubit', 'WFT1153', serial='1153', COM_adrs='COM4')
#
instruments.remove('dig')
dig = instruments.create('dig', 'Keysight_DIG', chassis = 1, slot = 3, trigger_period = 100, 
                         trigger_only = False, naverages = 3000, nsamples = 1000, awg_list = [7, 8])

#yoko = instruments.create('yoko', 'Yokogawa_7651_new', address = 'GPIB0::3::INSTR')
#signalhound = instruments.create('signalhound', 'SignalHoundSM200A', 'S/N 18104217')


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
                              channels='3,4',
                              sideband_channels='I1,Q1',
                              sideband_phase=-0.15)

qubit1ef = instruments.create('qubit1ef', 'Qubit_Info',
                            deltaf=-413.85e6,
                            pi_amp=0.179,
                            pi_amp_selective=0.001,
                            rotation='Gaussian',
                            w=5,
                            w_selective=500,
                            channels='3,4',
                            sideband_channels='I2,Q2',
                            sideband_phase=0)

qubit2ge = instruments.create('qubit2ge', 'Qubit_Info',
                             deltaf=-100e6,
                              pi_amp=0.104,
                              pi2_amp=0,
                              drag=0,
                              pi_amp_quasilective=.0253, #.0356,
                              pi_amp_selective=.005,
                              rotation='Gaussian',
                              w=20,
                              w_quasilective=160, #120,
                              w_selective=500,
                              channels='7,8',
                              sideband_channels='I3,Q3',
                              sideband_phase=0)

#qubit3 = instruments.create('qubit3', 'Qubit_Info',
#                             deltaf=0e6,
#                              pi_amp=-0.033,
#                              pi2_amp=0,
#                              drag=0,
#                              pi_amp_quasilective=.0253, #.0356,
#                              pi_amp_selective=.005,
#                              rotation='Gaussian',
#                              w=20,
#                              w_quasilective=160, #120,
#                              w_selective=500,
#                              channels='5,5',
#                              sideband_channels='I4,Q4',
#                              sideband_phase=0)

readout = instruments.create('readout', 'Readout_Info', IQe=(17.3018176573+31.8619779296j), IQg=(-46.0239832844+85.7199238753j),
                           IQe_radius= 1 , rfsource1='RObrick', rfsource2='refbrick',
                         pulse_len=1000, readout_chan='6m1', acq_chan='1m1')

refbrick = instruments.create('refbrick', 'LabBrick_RFSource', serial=18239,
                          use_extref=True)

RObrick = instruments.create('RObrick', 'LabBrick_RFSource', serial=19151,
                            use_extref=True) 
#SCref = instruments.create('SCref', 'SC5511A', devid='10001D2F')

TWPAbrick = instruments.create('TWPAbrick', 'LabBrick_RFSource', serial=14511)
#ebru changed to 8
AWG1 = instruments.create('AWG1', 'Keysight_AWG', chassis = 1, slot = 7,
                              AWG_PRODUCT = "M3202A",
                              amps = [1.5, 1.5, 1.5, 1.5], ofs = [0, 0, 0.0, 0.01])

AWG2 = instruments.create('AWG2', 'Keysight_AWG', chassis = 1, slot = 8,
                              AWG_PRODUCT = "M3202A",
                              amps = [1.5,1.5,1.5,1.5], ofs = [0, 0, 0, 0])

#alz = instruments.create('alazar', 'Alazar_Daemon')
#alz.set_ch1_range('40mV')
#alz.set_ch2_range('40mV')
#alz.set_nsamples(1280)
#alz.set_naverages(1000)
#alz.set_ch1_coupling('AC')
#alz.set_ch2_coupling('AC')
##alz.set_clock_source('EXT10M')
#alz.set_clock_source('EXT')
#alz.set_sample_rate('1GEXT10')
#alz.set_engJ_trig_src('EXT')
#alz.set_engJ_trig_lvl(128+5)
#alz.set_real_signals(False)
#alz.set_timeout(10000)
##TODO this should be fixed. we should be able to setup_clock
##alz.setup_clock()
#alz.setup_channels()
#alz.setup_trigger()
#
