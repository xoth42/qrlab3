import time


#import visa
if 1:
    import os
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

from mclient import instruments


#SC_Test = instruments.create('SC_Test', 'SC5506A', devid= '10001FA3')


#yoko = instruments.create('yoko', 'Yokogawa_7651_new', address = 'GPIB0::6::INSTR')
#yoko.do_set_voltage_range(1)


#
instruments.remove('dig')

dig = instruments.create('dig', 'Keysight_DIG', chassis = 0, slot = 3, trigger_period=100,nsamples=1500, naverages=6000, awg_list = [7, 8])



#dig = instruments.create('dig', 'Keysight_DIG', chassis = 0, slot = 3, trigger_period = 100, trigger_only = False,
#                         naverages = 1000, nsamples = 2500)

AWG1 = instruments.create('AWG1', 'Keysight_AWG', chassis = 0, slot = 7,  AWG_PRODUCT = "M3202A", 
                          amps = [1.5,1.5,1.5,1.5], ofs = [0.5, 0, 0.001,-0.01])

#AWG1 = instruments.create('AWG1', 'Keysight_AWG', chassis = 0, slot = 7,  AWG_PRODUCT = "M3202A", 
#                          amps = [1.5,1.5,1.5,1.5], ofs = [0.5, 0, 0.021, 0.015])


AWG2 = instruments.create('AWG2', 'Keysight_AWG', chassis = 0, slot = 8,  AWG_PRODUCT = "M3202A", 
                          amps = [1.5,1.5,1.5,1.5], ofs = [0.0693, 0.0125, -0.0059, 0.0048])

#AWG3 = instruments.create('AWG3', 'Keysight_AWG', chassis = 0, slot = 10,  AWG_PRODUCT = "M3202A", 
#                          amps = [1,1,1,1], ofs = [0.0045, -0.002, 0, 0])

#
#dig = instruments.create('dig', 'Keysight_DIG', chassis = 0, slot = 3, trigger_period=500)
#
#
#AWG1 = instruments.create('AWG1', 'Keysight_AWG', chassis = 0, slot = 7,  AWG_PRODUCT = "M3202A", 
#                          amps = [1,1.5,1.5,1.5], ofs = [0.5, 0, -0.0012, 0.0466])
#
#
#AWG2 = instruments.create('AWG2', 'Keysight_AWG', chassis = 0, slot = 8,  AWG_PRODUCT = "M3202A", 
#                          amps = [1.5,1.5,1,1], ofs = [0.02, -0.098, 0, 0])
##
#AWG3 = instruments.create('AWG3', 'Keysight_AWG', chassis = 1, slot = 10,  AWG_PRODUCT = "M3202A", 
#                          amps = [1,1,1,1], ofs = [0, 0, 0, 0])
'''
RObrick = instruments.create('RObrick', 'LabBrick_RFSource', serial=19151, use_extref=True)
refbrick = instruments.create('refbrick', 'LabBrick_RFSource', serial=14511, use_extref=True) 
SC_qubit = instruments.create('SC_qubit', 'SC5511A', devid= '10001D2F')

readout = instruments.create('readout', 'Readout_Info', IQe=(30.69-48.9j), IQg=(31.27-48.64j),
                             IQe_radius=1 , rfsource1='RObrick', rfsource2='refbrick',
                             pulse_len=1000, readout_chan='1m1', acq_chan='2m1')

qubit1ge = instruments.create('qubit1ge', 'Qubit_Info',
                             deltaf=-100e6,
                              pi_amp=0.142,
                              pi2_amp=0,
                              drag=0,
                              pi_amp_quasilective=0.9,
                              pi_amp_selective=0.0038,
                              rotation='Gaussian',
                              w=50,
                              w_quasilective=100,
                              w_selective=500,
                              channels='3,4',
                              sideband_channels='I1,Q1',
                              sideband_phase=0)
#
qubit1ef = instruments.create('qubit1ef', 'Qubit_Info',
                            deltaf=-380e6,
                            pi_amp=0.4654,
                            pi_amp_quasilective=0.02,
                            pi_amp_selective=0.004,
                            rotation='Gaussian',
                            w=5,
                            w_quasilective=100,
                            w_selective=600,
                            channels='3,4',
                            sideband_channels='I2,Q2',
                            sideband_phase=0)

'''

#AWG1.do_set_waveform_delay(200000)
#bla
#instruments.remove('Magnet')
Magnet = instruments.create('Magnet','AMI_430')
#print 'Magnet OK'
#instruments.remove('Magnet')
#VNA = instruments.create('VNA', 'Agilent_E5071C', address='TCPIP0::172.30.56.25::4000::SOCKET')
#
#VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')

#Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB0::11::INSTR')
#AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='TCPIP0::172.30.56.25::inst0::INSTR', clock=1e9, refsrc='EXT', reffreq=10e6)
#AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='AWG1')
#AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='GPIB1::1::INSTR')


#sc1 = instruments.create('sc1', 'SC5511A', devid='100016B6')

#sc2 = instruments.create('sc2', 'SC5511A', devid='100016B5')



#efBrick = instruments.create('efBrick', 'LabBrick_RFSource', serial=18238, use_extref=True) # qubit
#brick2 = instruments.create('brick2', 'LabBrick_RFSource', serial=14511, use_extref=True) # ref
#Brick14 = instruments.create('Brick14', 'LabBrick_RFSource', serial=14511, use_extref=True) # old RO
#Brick03 = instruments.create('Brick03', 'LabBrick_RFSource', serial=17912, use_extref=True)
#efBrick = instruments.create('efBrick', 'LabBrick_RFSource', serial=17912, use_extref=True)
#brick5 = instruments.create('brick5', 'LabBrick_RFSource', serial=14525, use_extref=True) # New brick
#brick6 = instruments.create('brick6', 'LabBrick_RFSource', serial=18238, use_extref=True)#reference

#refbrick = instruments.create('refbrick', 'LabBrick_RFSource', serial=14511, 
#                             use_extref=True) #reference
RObrick = instruments.create('RObrick', 'LabBrick_RFSource', serial=14524, use_extref=True) #readout


#SC_qubit1FWM = instruments.create('SC_qubit1FWM', 'SC5506A', devid= '10001FA3')
#SSdrive = instruments.create('SSdrive', 'SC5511A', devid= '10001C09')#qubit 2
SC_ref = instruments.create('SC_ref', 'SC5511A', devid= '10001C09')#qubit 2
SS_drive = instruments.create('SS_drive', 'SC5511A', devid= '10001D2F')
readout = instruments.create('readout', 'Readout_Info', IQe=(30.69-48.9j), IQg=(31.27-48.64j),
                             IQe_radius=1 , rfsource1='RObrick', rfsource2='SC_ref',
                             pulse_len=2000, readout_chan='1m1', acq_chan='2m1')

qubit1ge = instruments.create('qubit1ge', 'Qubit_Info',

                             deltaf=99.3e6,
                              pi_amp=0.4325,#0.404,  # 0.1594,
                              pi2_amp=0,
                              drag=0,
                              pi_amp_quasilective=0.9,
                              pi_amp_selective=0.0633,
                              rotation='Gaussian',
                              rotation_selective = 'Square',
                              w=5,

                              w_quasilective=100,
                              w_selective=80,
                              channels='3,4',
                              sideband_channels='I1,Q1',
                              sideband_phase=0)
#
qubit1ef = instruments.create('qubit1ef', 'Qubit_Info',
                            deltaf=-181e6,
                            pi_amp=0.4223,
                            pi_amp_quasilective=0.02,
                            pi_amp_selective=0.02131,
                            rotation='Gaussian',
                            w=7,
                            w_quasilective=100,
                            w_selective=100,
                            channels='3,4',
                            sideband_channels='I2,Q2',
                            sideband_phase=0)

qubit2ge = instruments.create('qubit2ge', 'Qubit_Info',

                             deltaf=190.5e6,
                              pi_amp=0.265,
#                             pi_amp = 0.742,
                              pi2_amp=0,
                              drag=0,
                              pi_amp_quasilective=0.9,
                              pi_amp_selective=0.323,
                              rotation='Gaussian',
                              rotation_selective = 'Square',
                              w=40,
                              w_quasilective=100,
                              w_selective=80,
                              channels='5,6',
                              sideband_channels='I1,Q1',
                              sideband_phase=1.02)
#
qubit2ef = instruments.create('qubit2ef', 'Qubit_Info',
                            deltaf=-390.9e6,
                            pi_amp=0.5063,
                            pi_amp_quasilective=0.02,
                            pi_amp_selective=0.07,
                            rotation='Gaussian',
                            w=40,
                            w_quasilective=100,
                            w_selective=1000,
                            channels='5,6',
                            sideband_channels='I4,Q4',
                            sideband_phase=0.2)
#fwm_info1 = instruments.create('fwm_info1', 'Qubit_Info',
#                            deltaf=-100e6,
#                            pi_amp=0.95,
#                            pi_amp_selective=0.01,
#                            rotation='Square',
#                            channels='7,7',
#                            sideband_channels='I5,Q5',
#                            sideband_phase=0,
#                            w=500,
#                            w_selective=200)
#fwm_info2 = instruments.create('fwm_info2', 'Qubit_Info',
#                            deltaf=0e6,
#                            pi_amp=0.7,
#                            pi_amp_selective=0.01,
#                            rotation='Square',
#                            channels='8,8',
#                            sideband_channels='I6,Q6',
#                            sideband_phase=0,
#                            w=10000,
#                            w_selective=200)
mixer_info1 = instruments.create('mixer_info1', 'Qubit_Info',
                            deltaf=-100e6,
                            pi_amp=0.7,
                            pi_amp_selective=0.01,
                            rotation='Square',
                            channels='7,7',
                            sideband_channels='I5,Q5',
                            sideband_phase=0,
                            w=2000,
                            w_selective=200)

SS_mixer_info1 = instruments.create('SS_mixer_info1', 'Qubit_Info',
                            deltaf=-94.35e6,
                            pi_amp=0.7,
                            pi_amp_selective=0.01,
                            rotation='Square',
                            channels='7,7',
                            sideband_channels='I7,Q7',
                            sideband_phase=0,
                            w=300,
                            w_selective=200)

mixer_info2 = instruments.create('mixer_info2', 'Qubit_Info',
                            deltaf=-100e6,
                            pi_amp=0,
                            pi_amp_selective=0.01,
                            rotation='Square',
                            channels='8,8',
                            sideband_channels='I6,Q6',
                            sideband_phase=0,
                            w=2000,
                            w_selective=200)

SS_mixer_info2 = instruments.create('SS_mixer_info2', 'Qubit_Info',
                            deltaf=-94.35e6,
                            pi_amp=0,
                            pi_amp_selective=0.01,
                            rotation='Square',
                            channels='8,8',
                            sideband_channels='I8,Q8',
                            sideband_phase=0,
                            w=300,
                            w_selective=200)

#IQ_readout_info = instruments.create('IQ_read_out_info','IQ_readout_info',
#                            IQe=(30.69-48.9j), 
#                            IQg=(31.27-48.64j), 
#                            IQe_radius=1 ,
#                            rfsource1='RObrick',
#                            rfsource2='SC_ref',
#                            pulse_len=300,
#                            readout_chan='1m1',
#                            acq_chan='2m1',
#                            deltaf=-100e6,
#                            pi_amp=0.7,
#                            pi_amp_selective=0.01,
#                            rotation='Square',
#                            channels='7,7',
#                            sideband_channels='I5,Q5',
#                            sideband_phase=0,
#                            w=300,
#                            w_selective=200)





#readout = instruments.create('readout', 'Readout_Info', IQe=(30.69-48.9j), IQg=(31.27-48.64j),
#                             IQe_radius=1 , rfsource1='RObrick', rfsource2='SC_ref',
#                             pulse_len=300, readout_chan='1m1', acq_chan='2m1')

#qubit1ge = instruments.create('qubit1ge', 'Qubit_Info',
#                             deltaf=100e6,
#                              pi_amp=0.2018,#0.404,  # 0.1594,
#                              pi2_amp=0,
#                              drag=0,
#                              pi_amp_quasilective=0.9,
#                              pi_amp_selective=0.0103,
#                              rotation='Gaussian',
#                              w=5,
#                              w_quasilective=100,
#                              w_selective=100,
#                              channels='5,6',
#                              sideband_channels='I1,Q1',
#                              sideband_phase=0)
##
#qubit1ef = instruments.create('qubit1ef', 'Qubit_Info',
#                            deltaf=-184.7e6,
#                            pi_amp=0.179,
#                            pi_amp_quasilective=0.02,
#                            pi_amp_selective=0.008,
#                            rotation='Gaussian',
#                            w=5,
#                            w_quasilective=100,
#                            w_selective=100,
#                            channels='5,6',
#                            sideband_channels='I2,Q2',
#                            sideband_phase=0)
#
#qubit2ge = instruments.create('qubit2ge', 'Qubit_Info',
#                             deltaf=198.34e6,
#                              pi_amp=0.2625,
##                             pi_amp = 0.742,
#                              pi2_amp=0,
#                              drag=0,
#                              pi_amp_quasilective=0.9,
#                              pi_amp_selective=0.026,
#                              rotation='Gaussian',
#                              w=30,
#                              w_quasilective=100,
#                              w_selective=300,
#                              channels='3,4',
#                              sideband_channels='I3,Q3',
#                              sideband_phase=0.2)
##
#qubit2ef = instruments.create('qubit2ef', 'Qubit_Info',
#                            deltaf=-263.7e6,
#                            pi_amp=0.2435,
#                            pi_amp_quasilective=0.14,
#                            pi_amp_selective=0.09626,
#                            rotation='Gaussian',
#                            w=80,
#                            w_quasilective=100,
#                            w_selective=200,
#                            channels='3,4',
#                            sideband_channels='I4,Q4',
#                            sideband_phase=0.2)

#fwm_info1 = instruments.create('fwm_info1', 'Qubit_Info',
#                            deltaf=-100e6,
#                            pi_amp=0.95,
#                            pi_amp_selective=0.01,
#                            rotation='Square',
#                            channels='7,7',
#                            sideband_channels='I5,Q5',
#                            sideband_phase=2.33,
#                            w=500,
#                            w_selective=200)
#qubit2efV2 = instruments.create('qubit2ef_V2', 'Qubit_Info',
#                            deltaf=-301.9e6,
#                            pi_amp=0.441,
#                            pi_amp_quasilective=0.02,
#                            pi_amp_selective=0.176,
#                            rotation='Gaussian',
#                            w=80,
#                            w_quasilective=100,
#                            w_selective=200,
#                            channels='5,6',
#                            sideband_channels='I3,Q3',
#                            sideband_phase=-0.2)

#efbrick = instruments.create('efBrick', 'Agilent_Generator', address= 'USB0::0x0957::0x1F01::MY53270760::INSTR')
#QK = instruments.create('QK', 'LabBrick_RFSource', serial=21513, use_extref=True)  #(0-1) transition, using the name QK for keeping consistency 
#SC_TWPApump = instruments.create('SC_TWPApump', 'SC5511A', devid='10001C09')
#SC_SShift = instruments.create('SC_SShift', 'SC5511A', devid= '100016B5')
#refbrick = instruments.create('refbrick', 'LabBrick_RFSource', serial=14511, 
#                            use_extref=True) #reference


#f0g1brick = instruments.create('f0g1brick', 'LabBrick_RFSource', serial=17912, 
#                            use_extref=True)

#fg = instruments.create('funcgen', 'Agilent_33250A', serial=2391)

#fg = instruments.create('funcgen', 'Agilent_33250A', address='GPIB1::30')

#fg = instruments.create('funcgen', 'BNC_FuncGen645', address='GPIB1::30')

#bobFG = instruments.create('bobFG', 'Agilent_Generator', address = 'USB0::0x0957::0x1F01::MY53270811::0::INSTR')
#mixFG = instruments.create('mixFG', 'Agilent_Generator', address = 'USB0::0x0957::0x1F01::MY53270760::0::INSTR')

# Setup Alazar

#alz = instruments.create('alazar', 'Alazar_Daemon')
#alz.set_ch1_range('200mV')
#alz.set_ch2_range('200mV')
#alz.set_nsamples(1600)
#alz.set_naverages(2000)
#alz.set_ch1_coupling('AC')
#alz.set_ch2_coupling('AC')
#alz.set_clock_source('EXT10M')
##alz.set_clock_source('INT')
#alz.set_sample_rate('1GEXT10')
#alz.set_engJ_trig_src('EXT')
#alz.set_engJ_trig_lvl(128+5)
#alz.set_real_signals(False)
#alz.set_timeout(10e3)
#alz.setup_clock()
#alz.setup_channels()
#alz.setup_trigger()






#alz = instruments.create('alazar', 'Alazar_Daemon')
#alz.set_ch1_range('40mV')
#alz.set_ch2_range('40mV')
#alz.set_nsamples(1600)
#alz.set_naverages(2000)
#alz.set_ch1_coupling('AC')
#alz.set_ch2_coupling('AC')
#alz.set_clock_source('EXT10M')
##alz.set_clock_source('INT')
#alz.set_sample_rate('1GEXT10')
#alz.set_engJ_trig_src('EXT')
#alz.set_engJ_trig_lvl(128+5)
#alz.set_real_signals(False)
#alz.set_timeout(10e3)
#alz.setup_clock()
#alz.setup_channels()
#alz.setup_trigger()
#
#
#readout = instruments.create('readout', 'Readout_Info', IQe=(30.69-48.9j), IQg=(31.27-48.64j),
#                             IQe_radius= 1 , rfsource1='RObrick', rfsource2='refbrick',
#                             pulse_len=1000, readout_chan='1m1', acq_chan='2m1')


'''
#AWG2 = instruments.create('AWG2', 'Tektronix_AWG5014C', address='AWG2',
#                          clock=1e9, refsrc='EXT', reffreq=10e6)


ag1 = instruments.create('ag1', 'Agilent_N5183A', address='GPIB1::19')
#ag2_JPC = instruments.create('ag2_JPC', 'Agilent_N5183A', address='GPIB1::20')
ag2 = instruments.create('ag2', 'Agilent_N5183A', address='GPIB1::22')

#instruments.remove('brick4')
#instruments.remove('brick3')
#instruments.remove('brick2')
#instruments.remove('brick1_LO')
#
#brick4 = instruments.create('brick4', 'LabBrick_RFSource', serial=10387)  # or devid
#brick1_LO = instruments.create('brick1_LO', 'LabBrick_RFSource', serial=5937)  # or devid
##brick4 = instruments.create('brick4', 'LabBrick_RFSource', serial=1352)
#brick3 = instruments.create('brick3', 'LabBrick_RFSource', serial=2495)  # or devid
#brick2 = instruments.create('brick2', 'LabBrick_RFSource', serial=2486)  # or devid
#
#VA = instruments.create('VA', 'Vlastakis_Spec', address = 'COM3', rfsource = 'brick4', if_freq = 10.596e6, delay =  0.04 )
#
##yoko = instruments.create('yoko', 'Yokogawa_)
##laserfg = instruments.create('laserfg', 'Agilent_FuncGen33250A', address='GPIB1::9')
#
'''




#fwm_info1 = instruments.create('fwm_info1', 'Qubit_Info',
#                            deltaf=-100e6,
#                            pi_amp=.785,
#                            pi_amp_selective=0.01,
#                            rotation='Square',
#                            channels='7,8',
#                            sideband_channels='I5,Q5',
#                            sideband_phase=2.33,
#                            w=10,
#                            w_selective=200)

#qubit2ge = instruments.create('qubit2ge', 'Qubit_Info',
#                             deltaf=200e6,
#                              pi_amp=0.494,
#                              pi2_amp=0,
#                              drag=0,
#                              pi_amp_quasilective=0.9,
#                              pi_amp_selective=0.0123,
#                              rotation='Gaussian',
#                              w=25,
#                              w_quasilective=100,
#                              w_selective=1000,
#                              channels='5,6',
#                              sideband_channels='I3,Q3',
#                              sideband_phase=1.73)
#
#qubit2ef = instruments.create('qubit2ef', 'Qubit_Info',
#                            deltaf=-276.5e6,
#                            pi_amp=0.1356,
#                            pi_amp_quasilective=0.02,
#                            pi_amp_selective=0.4,
#                            rotation='Gaussian',
#                            w=4,
#                            w_quasilective=100,
#                            w_selective=80,
#                            channels='5,6',
#                            sideband_channels='I4,Q4',
#                            sideband_phase=-1.73)
#
#fwm_info2 = instruments.create('fwm_info2', 'Qubit_Info',
#                            deltaf=-140e6,
#                            pi_amp=.5,
#                            pi_amp_selective=0.01,
#                            rotation='Square',
#                            channels='9,10',
#                            sideband_channels='I6,Q6',
#                            sideband_phase=0,
#                            w=10,
#                            w_selective=600)
#qubit1_03 = instruments.create('qubit1_03', 'Qubit_Info',
#                            deltaf=-100e6,
#                            pi_amp=0.465,
#                            pi_amp_quasilective=0.02,
#                            pi_amp_selective=0.1,
#                            rotation='Gaussian',
#                            w=20,
#                            w_quasilective=100,
#                            w_selective=100,
#                            channels='5,6',
#                            sideband_channels='I2,Q2',
#                            sideband_phase=0)
#
#qubit1_14 = instruments.create('qubit1_14', 'Qubit_Info',
#                            deltaf=-100e6,
#                            pi_amp=0.465,
#                            pi_amp_quasilective=0.02,
#                            pi_amp_selective=0.1,
#                            rotation='Gaussian',
#                            w=10,
#                            w_quasilective=100,
#                            w_selective=100,
#                            channels='3,4',
#                            sideband_channels='I2,Q2',
#                            sideband_phase=0)



#Cavity = instruments.create('cavity0', 'Qubit_Info',
#        deltaf=-100e6,
#        pi_amp=0.10,
#        rotation='Gaussian',
#        w=200,
#        channels='1,2',
#        sideband_channels='I0,Q0',
#        sideband_phase=0.0,
#        )


#qubit1gf = instruments.create('qubit1gf', 'Qubit_Info',
#                            deltaf=-186.93e6,
#                            marker_channel='5m2',
#                            pi_amp=0.565,
#                            pi_amp_selective=4.100e-3,
#                            rotation='Gaussian',
#                            w=6,
#                            w_selective=500,
#                            channels='5,6',
#                            sideband_channels='I26,Q26',
#                            sideband_phase=0.137894)
#if 1:
#    AWG2.do_set_offset(-0.115, 1)
#    AWG2.do_set_offset(-0.127, 2)
#    AWG2.do_set_amplitude(4.078, 2)

'''
qubit2ge = instruments.create('qubit2ge', 'Qubit_Info',
                            deltaf=-130e6,
                            pi_amp=0.382409,
                            pi2_amp=0.18865,
                            pi_amp_quasilective=0.017948,
                            pi_amp_selective=3.601205e-3,
                            rotation='Gaussian',
                            w=5,
                            w_quasilective=100,
                            w_selective=500,
                            channels='5,6',
                            sideband_channels='I7,Q7',
                            sideband_phase=0.098018)
qubit2ef = instruments.create('qubit2ef', 'Qubit_Info',
                            deltaf=-244.520e6,
                            pi_amp=0.465043,
                            rotation='Gaussian',
                            w=5,
                            channels='5,6',
                            sideband_channels='I17,Q17',
                            sideband_phase=0.138623)


CavityN = []

CavityN.append(instruments.create('cavity0', 'Qubit_Info',
        deltaf=-100e6,
        pi_amp=0.13,
        rotation='Gaussian',
        w=10,
        channels='1,2',
        sideband_channels='I0,Q0',
        sideband_phase=0.052779,
        ))


CavityN.append(instruments.create('cavity1A', 'Qubit_Info',
        deltaf=-100e6,
        marker_channel='1m2',
        pi_amp=0.55895,
        rotation='Gaussian',
        w=5,
        channels='1,2',
        sideband_channels='I1,Q1',
        sideband_phase=-0.087965,
        ))
if 0:
    AWG1.do_set_offset(-0.037, 1)
    AWG1.do_set_offset(-0.104, 2)
    AWG1.do_set_amplitude(3.972, 2)

CavityN.append(instruments.create('cavity1B', 'Qubit_Info',
        deltaf=-110e6,
        marker_channel='3m2',
        pi_amp=0.52381,
        rotation='Gaussian',
        w=5,
        channels='3,4',
        sideband_channels='I2,Q2',
        sideband_phase=0.016588,
        ))
if 0:
    AWG1.do_set_offset(-0.005, 3)
    AWG1.do_set_offset(-0.046, 4)
    AWG1.do_set_amplitude(3.750, 3)
    AWG1.do_set_amplitude(4.386, 4)

CavityN.append(instruments.create('Qswitch1A', 'Qubit_Info',
        deltaf=-15e6,
        marker_channel='1m2',
        pi_amp=0.4,
        rotation='Square',
        w=250e3,
        channels='1,2',
        sideband_channels='I11,Q11',
        sideband_phase=-0.106814,
        ))
CavityN.append(instruments.create('Qswitch1B', 'Qubit_Info',
        deltaf=-25.142857e6,
        marker_channel='3m2',
        pi_amp=1.0,
        rotation='Square',
        w=250e3,
        channels='3,4',
        sideband_channels='I12,Q12',
        sideband_phase=0.018661,
        ))
CavityN.append(instruments.create('Qswitch1R', 'Qubit_Info',
        deltaf=-200e6,
        pi_amp=1.0,
        rotation='Square',
        w=250e3,
        channels='7,8',
        sideband_channels='I13,Q13',
        sideband_phase=0.018661,
        ))


qubit2ge_1ph = instruments.create('qubit2ge_ph', 'Qubit_Info',
                            deltaf=-131.8e6,
                            marker_channel='5m2',
                            pi_amp=0.2907,
                            pi_amp_quasilective=0.016352,
                            pi_amp_selective=3.299e-3,
                            rotation='Gaussian',
                            w=6,
                            w_quasilective=100,
                            w_selective=500,
                            channels='5,6',
                            sideband_channels='I6,Q6',
                            sideband_phase=0.089850)
qubit2ef_ph = instruments.create('qubit2ef_ph', 'Qubit_Info',
                            deltaf=-242.757e6,
                            pi_amp=0.55492,
                            marker_channel='5m2',
                            rotation='Gaussian',
                            w=5,
                            channels='5,6',
                            sideband_channels='I16,Q16',
                            sideband_phase=0.137894)

CavityN.append(instruments.create('cavity2A', 'Qubit_Info',
        deltaf=-100e6,
        pi_amp=0.521,
        rotation='Gaussian',
        w=400,
        channels='1,2',
        sideband_channels='I3,Q3',
        sideband_phase=0.027646,
        ))
if 0:
    AWG.do_set_offset(-0.097, 1)
    AWG.do_set_offset(0.105, 2)
    AWG.do_set_amplitude(3.912, 2)

CavityN.append(instruments.create('cavity2B', 'Qubit_Info',
        deltaf=-100e6,
        pi_amp=0.164,
        rotation='Gaussian',
        w=200,
        channels='1,2',
        sideband_channels='I4,Q4',
        sideband_phase=0.173416,
        ))
if 0:
    AWG.do_set_offset(-0.029, 1)
    AWG.do_set_offset(0.161, 2)
    AWG.do_set_amplitude(3.570, 2)
'''

# to reload:
# mclient.instruments.reload('AWG1')

