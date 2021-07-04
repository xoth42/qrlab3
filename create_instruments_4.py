
import time
import numpy as np
import itertools


if 1:
    import os
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

from .mclient import instruments

#yoko = instruments.create('yoko', 'Yokogawa_7651_old', address = 'GPIB0::3::INSTR')
WF_ss = instruments.create('WF_ss', 'WFT1153', COM_adrs='COM3', serial = '1153')
#WF_ref = instruments.create('WF_ref', 'WFT1153_ch2')
#WF_ref.do_set_rfsource('WF_ro')
#bla


dig = instruments.create('dig', 'Keysight_DIG', chassis = 0, slot = 3, trigger_period = 100, trigger_only = False,
                         naverages = 1000, nsamples = 2000, awg_list = [7, 8, 9], channel_delay = 150)

AWG1 = instruments.create('AWG1', 'Keysight_AWG', chassis = 0, slot = 7,  AWG_PRODUCT = "M3202A", 
                          amps = [1.5,1.5,1.5,1.5], ofs = [0, 0, -0.0099, -0.007])
 
AWG2 = instruments.create('AWG2', 'Keysight_AWG', chassis = 0, slot = 8,  AWG_PRODUCT = "M3202A",
                          amps = [1, 1, 1.5, 1.5], ofs = [0.02, 0.008, -0.01, -0.067]) #[.020, 0.026, 0.022, .01]) 

AWG3 = instruments.create('AWG3', 'Keysight_AWG', chassis = 0, slot = 9,  AWG_PRODUCT = "M3202A",
                          amps = [1.5, 1.5, 1.5, 1.5], ofs = [-0.02, -0.0255, 0.046, 0.009]) 

#AWG4 = instruments.create('AWG4', 'Keysight_AWG', chassis = 0, slot = 10,  AWG_PRODUCT = "M3202A",
#                          amps = [1.5, 1.5, 1.5, 1.5], ofs = [0, 0, 0.0389, -.1145]) 

SCalice = instruments.create('SCalice', 'SC5511A', devid='100016B5')    # 3

SCref = instruments.create('SCref', 'SC5511A', devid='10001D30')    # 6

SCqubit = instruments.create('SCqubit', 'SC5511A', devid='100016B6')  #4

#SCbob = instruments.create('SCbob', 'SC5511A', devid='10001D31')    # 5



#BrickRO = instruments.create('BrickRO', 'LabBrick_RFSource', serial=18239,
#                              use_extref=True) 
#Brickbob = instruments.create('Brickbob', 'LabBrick_RFSource', serial=14510,
#                              use_extref=True) 

MXG = instruments.create('MXGbob', 'Agilent_Generator', address = 'USB0::0x0957::0x1F01::MY53270811::0::INSTR')
#
#readout = instruments.create('readout', 'Readout_Info', IQe=(1.0), IQg=(0.1),
#                           IQe_radius= 1 , rfsource1='BrickRO', rfsource2='SCref',
#                           pulse_len=2500, readout_chan='2m1', acq_chan='1m1')


''' 
1-3: qubit
7: A
8: B
9: R
10: RO
11: A rotating frame
12: B rotating frame
15-17: cav reset stuff
20: FWM
>100: All cav number dependant qubits



'''


readout_IQ = instruments.create('readout_IQ', 'Readout_IQ_Info', IQe=(1.0), IQg=(0.1),
                                IQe_radius= 1 ,
                                rfsource='SCref',
                                acq_chan='1m1',
                                deltaf=50e6,#16.9e3,
                                channels='11,12',
                                sideband_phase=0,
                                pulse_width=4500,
                                sigma=10,
                                amp=.4,
                                fixed_phase=0,
                                )



qubit1ge = instruments.create('qubit1ge', 'Qubit_Info',
                              deltaf=-100e6,
                              pi_amp=0.885,
                              pi2_amp=.411,
                              drag=0,
                              pi_amp_quasilective=.068,
                              pi_amp_selective=0.016,
                              rotation='Gaussian',
                              w=8,
                              w_quasilective=80,
                              w_selective=400,
                              channels='5,6',
                              sideband_channels='I1,Q1',
                              sideband_phase=0)

qubit1ef = instruments.create('qubit1ef', 'Qubit_Info',
                            deltaf=-304.7e6, 
                            pi_amp=0.303,
                            pi_amp_selective= 0.0421,
                            rotation='Gaussian',
                            w=15,
                            w_selective=100,
                            channels='5,6',
                            sideband_channels='I2,Q2',
                            sideband_phase=0)

#qubit1fh = instruments.create('qubit1fh', 'Qubit_Info',
#                            deltaf=-301.220e6,
#                            pi_amp=0.306,
#                            pi_amp_selective= 0.00587,
#                            rotation='Gaussian',
#                            w=10,
#                            w_selective=500,
#                            channels='5,6',
#                            sideband_channels='I3,Q3',
#                            sideband_phase=0)

cavityA = instruments.create('cavityA', 'Qubit_Info',
                            deltaf=40e6,
                            pi_amp=.848,
                            pi_amp_selective=0.02,
                            rotation='Gaussian',
                            channels='7,8',
                            sideband_channels='I7,Q7',
                            sideband_phase=0,
                            w=30, 
                            w_selective=500,
                            marker_bufwidth=250,
                            marker_ofs=0)


cavityB = instruments.create('cavityB', 'Qubit_Info',
                            deltaf=60e6,
                            pi_amp=1.3,
                            pi_amp_selective=0.08,
                            rotation='Gaussian',
                            channels='9,10',
                            sideband_channels='I8,Q8',
                            sideband_phase=0,
                            w=100,
                            w_selective=400,
                            marker_bufwidth=250,
                            marker_ofs=0)





cavityR = instruments.create('cavityR', 'Qubit_Info',
                            deltaf=50e6,#16.9e3,
                            pi_amp=1,
                            pi_amp_selective=0.0115,
                            rotation='SQUARE',                             
                            rotation_selective = 'SQUARE',
                            channels='11,12',
                            sideband_channels='I9,Q9',
                            sideband_phase=0,
                            w=50,
                            w_selective=400,
                            marker_bufwidth=250,
                            marker_ofs=0)





fwm_info = instruments.create('fwm_info', 'Qubit_Info',
                              deltaf=50e6,
                              pi_amp=0.642,
                              pi2_amp=0,
                              drag=0,
                              pi_amp_quasilective=0.0102,
                              pi_amp_selective=0.014,
                              rotation='SQUARE',
                              rotation_selective = 'SQUARE',
                              w=5,
                              w_quasilective=100,
                              w_selective=300,
                              channels='3,4',
                              sideband_channels='I20,Q20',
                              sideband_phase=3.14,
                              marker_bufwidth=1500,
                              marker_ofs=0)

#fwm_info_static = instruments.create('fwm_info_static', 'Qubit_Info',
#                              deltaf=-41.9e6,
#                              pi_amp=0.642,
#                              pi2_amp=0,
#                              drag=0,
#                              pi_amp_quasilective=0.0102,
#                              pi_amp_selective=0.014,
#                              rotation='SQUARE',
#                              rotation_selective = 'SQUARE',
#                              w=5,
#                              w_quasilective=100,
#                              w_selective=300,
#                              channels='3,4',
#                              sideband_channels='I21,Q21',
#                              sideband_phase=3.14,
#                              marker_bufwidth=1500,
#                              marker_ofs=0)


'''
# these infos for a rotating fram for tomography
cavityArf = instruments.create('_cavityArf', 'Qubit_Info',
                            deltaf=40e6,
                            pi_amp=0.845,
                            pi_amp_selective=0.01,
                            rotation='Gaussian',
                            channels='7,8',
                            sideband_channels='I11,Q11',
                            sideband_phase=0,
                            w=7, 
                            w_selective=400,
                            marker_bufwidth=250,
                            marker_ofs=0)

cavityBrf = instruments.create('_cavityBrf', 'Qubit_Info',
                            deltaf=60e6,
                            pi_amp=1.5,
                            pi_amp_selective=0.01,
                            rotation='Gaussian',
                            channels='9,10',
                            sideband_channels='I12,Q12',
                            sideband_phase=0,
                            w=7,
                            w_selective=400,
                            marker_bufwidth=250,
                            marker_ofs=0)

cavityAreset = instruments.create('cavAreset', 'Qubit_Info',
                            deltaf=40e6 + 20e6,
                            pi_amp=0.845,
                            pi_amp_selective=0.01,
                            rotation='Gaussian',
                            channels='7,8',
                            sideband_channels='I15,Q15',
                            sideband_phase=0,
                            w=7, 
                            w_selective=400,
                            marker_bufwidth=250,
                            marker_ofs=0)


cavityBreset = instruments.create('cavBreset', 'Qubit_Info',
                            deltaf=60e6 + 20e6,
                            pi_amp=1.5,
                            pi_amp_selective=0.01,
                            rotation='Gaussian',
                            channels='9,10',
                            sideband_channels='I16,Q16',
                            sideband_phase=0,
                            w=7,
                            w_selective=400,
                            marker_bufwidth=250,
                            marker_ofs=0)

cavityRreset = instruments.create('cavRreset', 'Qubit_Info',
                            deltaf=50e6 + 20e6,#16.9e3,
                            pi_amp=1,
                            pi_amp_selective=0.0115,
                            rotation='SQUARE',                             
                            rotation_selective = 'SQUARE',
                            channels='11,12',
                            sideband_channels='I17,Q17',
                            sideband_phase=0,
                            w=50,
                            w_selective=400,
                            marker_bufwidth=250,
                            marker_ofs=0)


'''



# Some code to generate all the cavity number dependant qubit info objects easily
# Calculate generic dfreqs
N = 3
chi_a = 1.97e6
chi_b = 5.95e6
dfreqs = np.zeros((N, N))
#for i, j in itertools.product(range(N), range(N)):
#    dfreqs[i, j] = -100e6 - chi_a * i - chi_b * j
    

# Setting specific frequencies to correct errors
dfreqs[1, 1] = -107.44e6
dfreqs[2, 2] = -114.45e6
#dfreqs[3, 3] = -120.89e6

#delta =1
dfreqs[1, 0] = -101.97e6
dfreqs[2, 1] = -108.73e6
#dfreqs[3, 2] = -115.6e6


#delta=-1
dfreqs[0, 1] = -105.95e6
dfreqs[1, 2] = -112.41e6
#dfreqs[2, 3] = -118.75e6

#dfreqs[4, 4] = -127.5e6

for i, j in itertools.product(list(range(N)), list(range(N))):
    if dfreqs[i,j] != 0:
        instruments.create('_qubit_a' + str(i) + 'b' + str(j), 'Qubit_Info',
                           deltaf = dfreqs[i, j],
                           sideband_channels='I1' + str(100+10*i+j) + ',Q1' + str(100+10*i+j),
                           pi_amp=0.885,
                           pi2_amp=.411,
                           drag=0,
                           pi_amp_quasilective=.068,
                           pi_amp_selective=0.016,
                           rotation='Gaussian',
                           w=8,
                           w_quasilective=80,
                           w_selective=400,
                           channels='5,6',
                           sideband_phase=0)
        




