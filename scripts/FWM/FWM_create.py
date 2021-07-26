import time

if 1:
    import os
    os.chdir(r'C:/qrlab/')
    os.system(r'C:\qrlab-3\start.bat')
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


#qubit1ef = instruments.create('qubit1ef', 'Qubit_Info',
#                            deltaf=-216.40e6,
#                            pi_amp=0.28254,
#                            pi_amp_selective=0.02103,
#                            rotation='Gaussian',
#                            w=20,
#                            w_selective=300,
#                            channels='3,4',
#                            sideband_channels='I2,Q2',
#                            sideband_phase=0)

CavityB = instruments.create('cavityBob', 'Qubit_Info',
                            deltaf=-100e6,
                            pi_amp=.879,
                            pi_amp_selective=.527,
                            rotation='Gaussian',
                            channels='5,6',
                            sideband_channels='I0,Q0',
                            sideband_phase=0,
                            w=1200,
                            w_selective=2000)

CavityA = instruments.create('cavityAlice', 'Qubit_Info',
                            deltaf=100e6,
                            pi_amp=.879,
                            pi_amp_selective=0.03,
                            rotation='Gaussian',
                            channels='7,8',
                            sideband_channels='I3,Q3',
                            sideband_phase=0,
                            w=40,
                            w_selective=3000)

#SCqubit = instruments.create('SCqubit', 'SC5511A', devid='100016B6')
#SCref = instruments.create('SCref', 'SC5511A', devid='10001C09')


#sc2 = instruments.create('sc2', 'SC5511A', devid='100016B5')
AWG1 = instruments.create('AWG1', 'Keysight_AWG', chassis = 0, slot = 7,
                              AWG_PRODUCT = "M3202A",
                              amps = [1, 1.5, 1, 1], ofs = [0, 0, 0, 0])

AWG2 = instruments.create('AWG2', 'Keysight_AWG', chassis = 0, slot = 8,  
                              AWG_PRODUCT = "M3202A", 
                              amps = [1, 1, 1, 1], ofs = [0, 0, 0, 0])

AWG3 = instruments.create('AWG3', 'Keysight_AWG', chassis = 0, slot = 10,  
                              AWG_PRODUCT = "M3202A", 
                              amps = [1, 1, 1, 1], ofs = [0, 0, 0, 0])

dig = instruments.create('dig', 'Keysight_DIG', chassis = 0, slot = 3, trigger_period = 200, trigger_only = False)
dig.set_naverages(1000)

#ROFG = instruments.create('ROFG', 'Agilent_Generator', address = 'USB0::0x0957::0x1F01::MY53270811::0::INSTR')


readout = instruments.create('readout', 'Readout_Info', IQe=(1.0), IQg=(0.1),
                           IQe_radius= 1 , rfsource1='ROFG', rfsource2='SCref',
                         pulse_len=1000, readout_chan='2m1', acq_chan='1m1')


FWM_info = instruments.create('fwm_info', 'FWM_Info',
                            deltaf=100e6,
                            pi_amp=.1,
                            pi_amp_selective=0.03,
                            rotation='Gaussian',
                            channels='9,10',
                            sideband_channels='I2,Q2',
                            sideband_phase=0,
                            w=40,
                            w_selective=3000)
