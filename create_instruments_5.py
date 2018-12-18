import time

if 1:
    import os
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

from mclient import instruments



qubit1ge = instruments.create('qubit1ge', 'Qubit_Info',
                             deltaf=-100e6,
                              pi_amp=.163475,
                              pi2_amp=0,
                              drag=-0.9,
                              pi_amp_quasilective=0.027025,
                              pi_amp_selective=0.03256,
                              rotation='Gaussian',
                              w=40,
                              w_quasilective=100,
                              w_selective=200,
                              channels='3,4',
                              sideband_channels='I1,Q1',
                              sideband_phase=0)


qubit1ef = instruments.create('qubit1ef', 'Qubit_Info',
                            deltaf=-216.40e6,
                            pi_amp=0.28254,
                            pi_amp_selective=0.02103,
                            rotation='Gaussian',
                            w=20,
                            w_selective=300,
                            channels='3,4',
                            sideband_channels='I2,Q2',
                            sideband_phase=0)

#CavityB = instruments.create('cavityBob', 'Qubit_Info',
#                            deltaf=-100e6,
#                            pi_amp=.879,
#                            pi_amp_selective=.527,
#                            rotation='Gaussian',
#                            channels='5,6',
#                            sideband_channels='I0,Q0',
#                            sideband_phase=0,
#                            w=1200,
#                            w_selective=2000)

CavityA = instruments.create('cavityAlice', 'Qubit_Info',
                            deltaf=100e6,
                            pi_amp=.879,
                            pi_amp_selective=0.03,
                            rotation='Gaussian',
                            channels='5,6',
                            sideband_channels='I3,Q3',
                            sideband_phase=0,
                            w=40,
                            w_selective=3000)


#qubit1ge = instruments.create('qubit1ge', 'Qubit_Info',
#                             deltaf=-100e6,
#                              pi_amp=.193178,
#                              pi2_amp=0,
#                              drag=-0.9,
#                              pi_amp_quasilective=0.027025,
#                              pi_amp_selective=0.34 / 25,
#                              rotation='Gaussian',
#                              w=40,
#                              w_quasilective=100,
#                              w_selective=500,
#                              channels='2,3',
#                              sideband_channels='I1,Q1',
#                              sideband_phase=0)
#
#
#qubit1ef = instruments.create('qubit1ef', 'Qubit_Info',
#                            deltaf=-370.50e6,
#                            pi_amp=0.153675,
#                            pi_amp_selective=0.06147,
#                            rotation='Gaussian',
#                            w=40,
#                            w_selective=100,
#                            channels='2,3',
#                            sideband_channels='I17,Q17',
#                            sideband_phase=0.138623)


#ROcav_IQ = instruments.create('RO', 'Qubit_Info',
#                             deltaf=-100e6,
#                              pi_amp=0.342948,
#                              pi2_amp=0.171474,
#                              drag=-0.9,
#                              pi_amp_quasilective=0.027025,
#                              pi_amp_selective=0.34 / 25,
#                              rotation='Gaussian',
#                              w=40,
#                              w_quasilective=100,
#                              w_selective=500,
#                              channels='1,2',
#                              sideband_channels='I3,Q3',
#                              sideband_phase=0)

# refbrick = instruments.create('refbrick', 'LabBrick_RFSource', serial=14511,
#                             use_extref=True) #reference
# RObrick = instruments.create('RObrick', 'LabBrick_RFSource', serial=19151,
#                              use_extref=True) #readout

#refbrick = instruments.create('refbrick', 'LabBrick_RFSource', serial=14511,
#                          use_extref=True)
Alicebrick = instruments.create('Alicebrick', 'LabBrick_RFSource', serial=14510,

refbrick = instruments.create('refbrick', 'LabBrick_RFSource', serial=14511,
                          use_extref=True)
RObrick = instruments.create('RObrick', 'LabBrick_RFSource', serial=17912,
                          use_extref=True)
# qbrick = instruments.create('qbrick', 'LabBrick_RFSource', serial=14524,
#                            use_extref=True) #qubits

SCqubit = instruments.create('SCqubit', 'SC5511A', devid='100016B6')
SCref = instruments.create('SCref', 'SC5511A', devid='10001C09')
#SCpump.do_set_frequency(6.194e9)
#SCpump.do_set_power(-5)
#SCpump.do_set_rf_on(True)

#VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB0::17::INSTR')

#sc2 = instruments.create('sc2', 'SC5511A', devid='100016B5')
AWG1 = instruments.create('AWG1', 'Keysight_AWG', chassis = 0, slot = 7,
                              AWG_PRODUCT = "M3202A",
                              amps = [1, 1.5, 1, 1], ofs = [0, 0, 0.008, -0.062])

AWG2 = instruments.create('AWG2', 'Keysight_AWG', chassis = 0, slot = 10,  
                              AWG_PRODUCT = "M3202A", 
                              amps = [1, 1, 1, 1], ofs = [-0.0064, -0.0646, 0, 0])

dig = instruments.create('dig', 'Keysight_DIG', chassis = 0, slot = 3, trigger_period = 2000, trigger_only = False)
dig.set_naverages(200000)

#Yoko = instruments.create('Yoko', 'Yokogawa_GS200', address = 'GPIB0::11::INSTR')
#Yoko.do_set_current(0.1)

ROFG = instruments.create('ROFG', 'Agilent_Generator', address = 'USB0::0x0957::0x1F01::MY53270811::0::INSTR')
#refFG = instruments.create('refFG', 'Agilent_Generator', address = 'USB0::0x0957::0x1F01::MY53270760::0::INSTR')
#=======
# #qbrick = instruments.create('qbrick', 'LabBrick_RFSource', serial=14510,
# #                           use_extref=True) #qubit
# qbrick = instruments.create('qbrick', 'LabBrick_RFSource', serial=14524,
#                            use_extref=True) #qubits

#sc1 = instruments.create('sc1', 'SC5511A', devid='100016B6')
SCqubit = instruments.create('SCqubit', 'SC5511A', devid='100016B6')
SCpump = instruments.create('SCpump', 'SC5511A', devid='10001C09')
#SCpump.do_set_frequency(6.194e9)
#SCpump.do_set_power(-5)
#SCpump.do_set_rf_on(True)

#VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB0::17::INSTR')

#sc2 = instruments.create('sc2', 'SC5511A', devid='100016B5')
AWG1 = instruments.create('AWG1', 'Keysight_AWG', chassis = 0, slot = 7,
                              AWG_PRODUCT = "M3202A",
                              amps = [1, 1.5, 1, 1], ofs = [0, 0, 0.0085, -0.0615])

AWG2 = instruments.create('AWG2', 'Keysight_AWG', chassis = 0, slot = 10,  
                              AWG_PRODUCT = "M3202A", 
                              amps = [1,1,1,1], ofs = [0.00078, 0.00091, 0, 0])

dig = instruments.create('dig', 'Keysight_DIG', chassis = 0, slot = 3, trigger_only = False)
dig.set_naverages(4000)

bobFG = instruments.create('bobFG', 'Agilent_Generator', address = 'USB0::0x0957::0x1F01::MY53270811::0::INSTR')
#refFG = instruments.create('refFG', 'Agilent_Generator', address = 'USB0::0x0957::0x1F01::MY53270760::0::INSTR')
# AWG1 = instruments.create('AWG1', 'Keysight_AWG', chassis = 0, slot = 7,
#                              AWG_PRODUCT = "M3202A",
#                              amps = [1.5, 1, 1, 1], ofs = [0.5, -.002, -.006, 0])
#
# dig = instruments.create('dig', 'Keysight_DIG', chassis = 0, slot = 3)


#AWG2 = instruments.create('AWG2', 'Keysight_AWG', chassis=0, slot=10,
#                         AWG_PRODUCT="M3202A",
#                         amps = [1, 1, 1, 1], ofs = [0, 0, 0, 0])

# Magnet = instruments.create('Magnet','AMI_430')

#
# readout = instruments.create('readout', 'Readout_Info', IQe=(1.0), IQg=(0.1),
#                              IQe_radius= 1 , rfsource1='RObrick',
#                              rfsource2='refbrick',
#                              pulse_len=1000, readout_chan='1m1', acq_chan='4m1')

#Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB0::11::INSTR')


#''' Readout_IQ_Info is for iq modulation on the readout brick instead of pulse triggering '''
#readout = instruments.create('readout', 'Readout_IQ_Info', IQe=(1.0), IQg=(0.1),
#                             IQe_radius= 1 , rfsource1='RObrick', rfsource2='refbrick',
#                             pulse_len=1000, readout_chan_I=1, readout_chan_Q=2,
#                             acq_chan=4)

# VNA = instruments.create('VNA', 'Agilent_E5071C', address='TCPIP0::K-E5071C-26868.local::inst0::INSTR')
 
 
#qubit1ef = instruments.create('qubit1ef', 'Qubit_Info',
#                              deltaf=-212.100e6,
#                              pi_amp=0.09,
#                              pi_amp_quasilective=0.02,
#                              pi_amp_selective=4.100e-3,
#                              rotation='Gaussian',
#                              w=40,
#                              w_quasilective=100,
#                              w_selective=500,
#                              channels='3,4',
#                              sideband_channels='I2,Q2',
#                              sideband_phase=1.315)

# test = instruments.create('sh_test', 'SignalHoundUSBSA124B', waittime=100000,
#                          serial_no=61660103, ref=-20, center=6e9,
#                          span=1e8, vbw=30e3, rbw=30e3)
# peaks, array = test.perform_sweep(peak_find = True, plot = True)





# AWG1.do_set_waveform_delay(200000)
# bla

#VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB0::17::INSTR')

#AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C',
#                          address='TCPIP0::172.30.56.25::inst0::INSTR', clock=1e9, refsrc='EXT', 
#                          reffreq=10e6)
# AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='AWG1')



# brick3 = instruments.create('brick3', 'LabBrick_RFSource', serial=18239,
# use_extref=True) # old RO
# brick4 = instruments.create('brick4', 'LabBrick_RFSource', serial=17912,
# use_extref=True) # RO



# fg = instruments.create('funcgen', 'Agilent_33250A', serial=2391)

# fg = instruments.create('funcgen', 'Agilent_33250A', address='GPIB1::30')

# fg = instruments.create('funcgen', 'BNC_FuncGen645', address='GPIB1::30')
# Setup Alazar



#alz = instruments.create('alazar', 'Alazar_Daemon')
#alz.set_ch1_range('40mV')
#alz.set_ch2_range('40mV')
#alz.set_nsamples(4800)
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
##TODO this should be fixed. we should be able to setup_clo#alz.setup_clock()
#alz.setup_channels()
#alz.setup_trigger()

#
# alz = instruments.create('alazar', 'Alazar_Daemon')
# alz.set_ch1_range('40mV')
# alz.set_ch2_range('40mV')
# alz.set_nsamples(4800)
# alz.set_naverages(2000)
# alz.set_ch1_coupling('AC')
# alz.set_ch2_coupling('AC')
# #alz.set_clock_source('EXT10M')
# alz.set_clock_source('EXT')
# alz.set_sample_rate('1GEXT10')
# alz.set_engJ_trig_src('EXT')
# alz.set_engJ_trig_lvl(128+5)
# alz.set_real_signals(False)
# alz.set_timeout(10000)
# #TODO this should be fixed. we should be able to setup_clock
# #alz.setup_clock()
# alz.setup_channels()
# alz.setup_trigger()





readout = instruments.create('readout', 'Readout_Info', IQe=(1.0), IQg=(0.1),
                           IQe_radius= 1 , rfsource1='ROFG', rfsource2='SCref',
                         pulse_len=1000, readout_chan='2m1', acq_chan='1m1')


#readout2 = instruments.create('readout2', 'Readout_Info', IQe=(1.0), IQg=(0.1),
#                             IQe_radius= 1 , rfsource1='brick4', rfsource2='brick2',
#                             pulse_len=1000, readout_chan='1m1', acq_chan='1m2')

#AWG2 = instruments.create('AWG2', 'Tektronix_AWG5014C', address='AWG2',
 #                         clock=1e9, refsrc='EXT', reffreq=10e6)

'''
#ag1 = instruments.create('ag1', 'Agilent_N5183A', address='GPIB1::19')
#ag2_JPC = instruments.create('ag2_JPC', 'Agilent_N5183A', address='GPIB1::20')
#ag2 = instruments.create('ag2', 'Agilent_N5183A', address='GPIB1::22')

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

# Cavity = instruments.create('cavity0', 'Qubit_Info',
#        deltaf=-100e6,
#        pi_amp=0.10,
#        rotation='Gaussian',
#        w=200,
#        channels='1,2',
#        sideband_channels='I0,Q0',
#        sideband_phase=0.0,
#        )


# qubit1gf = instruments.create('qubit1gf', 'Qubit_Info',
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
# if 1:
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
'''

# to reload:
# mclient.instruments.reload('AWG1')
'''
