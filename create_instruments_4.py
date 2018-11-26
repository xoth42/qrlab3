import time


#import visa
if 1:
    import os
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

from mclient import instruments

#Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB0::11::INSTR')



#yoko = instruments.create('yoko', 'Yokogawa_7651', address = 'GPIB1::17::INSTR')
#yoko.do_set_voltage_range(1)



<<<<<<< HEAD




#dig = instruments.create('dig', 'Keysight_DIG', chassis = 0, slot = 3, trigger_period=500)
#
#
#AWG1 = instruments.create('AWG1', 'Keysight_AWG', chassis = 0, slot = 7,  AWG_PRODUCT = "M3202A", 
#                          amps = [1,1.5,1.5,1.5], ofs = [0.5, 0, -0.0012, 0.0466])
#
#
#AWG2 = instruments.create('AWG2', 'Keysight_AWG', chassis = 0, slot = 8,  AWG_PRODUCT = "M3202A", 
#                          amps = [1.5,1.5,1,1], ofs = [0.02, -0.098, 0, 0])
=======
>>>>>>> 4c5a5d601badfc0c2317ef3dd47af3d22598bd6c
#
#
#
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




#AWG1.do_set_waveform_delay(200000)
#bla

Magnet = instruments.create('Magnet','AMI_430')
print 'Magnet OK'
#VNA = instruments.create('VNA', 'Agilent_E5071C', address='TCPIP0::172.30.56.25::4000::SOCKET')
<<<<<<< HEAD
#VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')
#print 'VNA OK'
=======
VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')
>>>>>>> 4c5a5d601badfc0c2317ef3dd47af3d22598bd6c
#Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB0::11::INSTR')
#AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='TCPIP0::172.30.56.25::inst0::INSTR', clock=1e9, refsrc='EXT', reffreq=10e6)
#AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='AWG1')
#AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='GPIB1::1::INSTR')


#sc1 = instruments.create('sc1', 'SC5511A', devid='100016B6')

#sc2 = instruments.create('sc2', 'SC5511A', devid='100016B5')
<<<<<<< HEAD
#
#efBrick = instruments.create('efBrick', 'LabBrick_RFSource', serial=17912, use_extref=True) # qubit
##brick2 = instruments.create('brick2', 'LabBrick_RFSource', serial=14511, use_extref=True) # ref
##ROBrick = instruments.create('ROBrick', 'LabBrick_RFSource', serial=14524, use_extref=True) # old RO
##aliceBrick = instruments.create('aliceBrick', 'LabBrick_RFSource', serial=17912, use_extref=False) # RO
##brick5 = instruments.create('brick5', 'LabBrick_RFSource', serial=14525, use_extref=True) # New brick
##brick6 = instruments.create('brick6', 'LabBrick_RFSource', serial=18238, use_extref=True)#reference
=======

#efBrick = instruments.create('efBrick', 'LabBrick_RFSource', serial=17912, use_extref=True) # qubit
#brick2 = instruments.create('brick2', 'LabBrick_RFSource', serial=14511, use_extref=True) # ref
#ROBrick = instruments.create('ROBrick', 'LabBrick_RFSource', serial=14524, use_extref=True) # old RO
#aliceBrick = instruments.create('aliceBrick', 'LabBrick_RFSource', serial=17912, use_extref=False) # RO
#brick5 = instruments.create('brick5', 'LabBrick_RFSource', serial=14525, use_extref=True) # New brick
#brick6 = instruments.create('brick6', 'LabBrick_RFSource', serial=18238, use_extref=True)#reference
>>>>>>> 4c5a5d601badfc0c2317ef3dd47af3d22598bd6c
#refbrick = instruments.create('refbrick', 'LabBrick_RFSource', serial=14511, 
#                            use_extref=True) #reference
#RObrick = instruments.create('RObrick', 'LabBrick_RFSource', serial=19151,
#                             use_extref=True) #readout
#refbrick = instruments.create('refbrick', 'LabBrick_RFSource', serial=19151, 
#                            use_extref=True) #reference

#fg = instruments.create('funcgen', 'Agilent_33250A', serial=2391)

#fg = instruments.create('funcgen', 'Agilent_33250A', address='GPIB1::30')

#fg = instruments.create('funcgen', 'BNC_FuncGen645', address='GPIB1::30')

#bobFG = instruments.create('bobFG', 'Agilent_Generator', address = 'USB0::0x0957::0x1F01::MY53270811::0::INSTR')
#mixFG = instruments.create('mixFG', 'Agilent_Generator', address = 'USB0::0x0957::0x1F01::MY53270760::0::INSTR')

# Setup Alazar
<<<<<<< HEAD

=======
#
>>>>>>> 4c5a5d601badfc0c2317ef3dd47af3d22598bd6c
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
<<<<<<< HEAD
#
=======

>>>>>>> 4c5a5d601badfc0c2317ef3dd47af3d22598bd6c

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
qubit1ge = instruments.create('qubit1ge', 'Qubit_Info',
                             deltaf=-100e6,
                              pi_amp=0.283499,
                              pi2_amp=0,
                              drag=0,
                              pi_amp_quasilective=0.027025,
                              pi_amp_selective=0.1,
                              rotation='Gaussian',
                              w=200,
                              w_quasilective=100,
                              w_selective=500,
                              channels='3,4',
                              sideband_channels='I1,Q1',
                              sideband_phase=0.1)



qubit1ef = instruments.create('qubit1ef', 'Qubit_Info',
                            deltaf=-100e6,
                            pi_amp=0.09,
                            pi_amp_quasilective=0.02,
                            pi_amp_selective=0.1,
                            rotation='Gaussian',
                            w=80,
                            w_quasilective=100,
                            w_selective=500,
                            channels='5,6',
                            sideband_channels='I2,Q2',
                            sideband_phase=0)

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

