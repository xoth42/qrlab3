
import time

if 1:
    import os
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

from mclient import instruments


#WF_ro = instruments.create('WF_ro', 'WFT1153', serial = '1153')
#WF_ref = instruments.create('WF_ref', 'WFT1153_ch2')
#WF_ref.do_set_rfsource('WF_ro')
#bla


dig = instruments.create('dig', 'Keysight_DIG', chassis = 0, slot = 3, trigger_period = 200, trigger_only = False,
                         naverages = 200, nsamples = 2500, awg_list = [7, 8, 9])

AWG1 = instruments.create('AWG1', 'Keysight_AWG', chassis = 0, slot = 7,  AWG_PRODUCT = "M3202A", 
                          amps = [1.5,1.5,1.5,1.5], ofs = [0, 0, -0.0064, -0.0027])
 
AWG2 = instruments.create('AWG2', 'Keysight_AWG', chassis = 0, slot = 8,  AWG_PRODUCT = "M3202A",
                          amps = [1.5, 1.5, 1.5, 1.5], ofs = [0.016, 0.0118, 0.032, -0.098]) #[.020, 0.026, 0.022, .01]) 

AWG3 = instruments.create('AWG3', 'Keysight_AWG', chassis = 0, slot = 9,  AWG_PRODUCT = "M3202A",
                          amps = [1, 1, 1.5, 1.5], ofs = [-0.0065, -0.0206, 0.036, 0.023]) 

#AWG4 = instruments.create('AWG4', 'Keysight_AWG', chassis = 0, slot = 10,  AWG_PRODUCT = "M3202A",
#                          amps = [1.5, 1.5, 1.5, 1.5], ofs = [0, 0, 0.0389, -.1145]) 

SCalice = instruments.create('SCalice', 'SC5511A', devid='100016B5')    # 3

SCdrive = instruments.create('SCdrive', 'SC5511A', devid='10001D30')    # 6

SCqubit = instruments.create('SCqubit', 'SC5511A', devid='100016B6')  #4

#SCbob = instruments.create('SCbob', 'SC5511A', devid='10001D31')    # 5



#BrickRO = instruments.create('BrickRO', 'LabBrick_RFSource', serial=18239,
#                              use_extref=True) 
BrickRef = instruments.create('BrickRef', 'LabBrick_RFSource', serial=14510,
                              use_extref=True) 

MXG = instruments.create('MXGbob', 'Agilent_Generator', address = 'USB0::0x0957::0x1F01::MY53270811::0::INSTR')

#readout = instruments.create('readout', 'Readout_Info', IQe=(1.0), IQg=(0.1),
#                           IQe_radius= 1 , rfsource1='BrickRO', rfsource2='BrickRef',
#                           pulse_len=7000, readout_chan='2m1', acq_chan='1m1')


readout_IQ = instruments.create('readout_IQ', 'Readout_IQ_Info', IQe=(1.0), IQg=(0.1),
                                IQe_radius= 1 , rfsource='BrickRef',
                                acq_chan='1m1',
                                deltaf=-50e6,#16.9e3,
                                pi_amp=0.598,
                                pi_amp_selective=0.0115,
                                rotation='SQUARE',                             
                                rotation_selective = 'SQUARE',
                                channels='11,12',
                                sideband_channels='I10,Q10',
                                sideband_phase=0,
                                w=5,
                                w_selective=400,
                                marker_bufwidth=250,
                                marker_ofs=0,
                                pulse_width=4000)



qubit1ge = instruments.create('qubit1ge', 'Qubit_Info',
                              deltaf=-100e6,
                              pi_amp=.769,
                              pi2_amp=.384,
                              drag=-0.292,
                              pi_amp_quasilective=0.058,
                              pi_amp_selective=0.0024  ,
                              rotation='Gaussian',
                              w=4,
                              w_quasilective=40,
                              w_selective=1000,
                              channels='5,6',
                              sideband_channels='I1,Q1',
                              sideband_phase=0)

qubit1ef = instruments.create('qubit1ef', 'Qubit_Info',
                            deltaf=-304.65e6,
                            pi_amp=0.545,
                            pi_amp_selective= 0.0084,
                            rotation='Gaussian',
                            w=4,
                            w_selective=200,
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
                            deltaf=56e6,
                            pi_amp=0.258,
                            pi_amp_selective=0.001,
                            rotation='Gaussian',
                            channels='7,8',
                            sideband_channels='I7,Q7',
                            sideband_phase=0,
                            w=4, 
                            w_selective=400,
                            marker_bufwidth=250,
                            marker_ofs=0)


cavityB = instruments.create('cavityB', 'Qubit_Info',
                            deltaf=-80e6,
                            pi_amp=1.24,
                            pi_amp_selective=0.008,
                            rotation='Gaussian',
                            channels='9,10',
                            sideband_channels='I8,Q8',
                            sideband_phase=0,
                            w=8,
                            w_selective=400,
                            marker_bufwidth=250,
                            marker_ofs=0)


cavityR = instruments.create('cavityR', 'Qubit_Info',
                            deltaf=-50e6,#16.9e3,
                            pi_amp=0.598,
                            pi_amp_selective=0.0115,
                            rotation='SQUARE',                             
                            rotation_selective = 'SQUARE',
                            channels='11,12',
                            sideband_channels='I9,Q9',
                            sideband_phase=0,
                            w=80,
                            w_selective=400,
                            marker_bufwidth=250,
                            marker_ofs=0)


fwm_info = instruments.create('fwm_info', 'Qubit_Info',
                              deltaf=60e6,
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

qubit_a1b1 = instruments.create('qubit_a1b1', 'Qubit_Info',
                              deltaf=-107.2e6,
                              pi_amp=.746,
                              pi2_amp=.384,
                              drag=-0.292,
                              pi_amp_quasilective=0.058,
                              pi_amp_selective=0.011629  ,
                              rotation='Gaussian',
                              w=4,
                              w_quasilective=40,
                              w_selective=200,
                              channels='5,6',
                              sideband_channels='I30,Q30',
                              sideband_phase=0)

# stark shifted cavity to track the rotation durring AQEC
#cavityAs = instruments.create('cavityAs', 'Qubit_Info',
##                            deltaf=56e6-2.85e3,#16.9e3,
#                            deltaf=56e6-18.22e3,#16.9e3,
#                            pi_amp=.833,
#                            pi_amp_selective=0.05,
#                            rotation='Gaussian',
#                            channels='7,8',
#                            sideband_channels='I8,Q8',
#                            sideband_phase=0,
#                            w=30,
#                            w_selective=400,
#                            marker_bufwidth=250,
#                            marker_ofs=0)



#cavityB = instruments.create('cavityB', 'Qubit_Info',
#                            deltaf=-41e6,
#                            pi_amp=.8,
#                            pi_amp_selective=0.020,
#                            pi_amp_quasilective = 1.67,
#                            rotation='Gaussian',
#                            channels='11,12',
#                            sideband_channels='I8,Q8',
#                            sideband_phase=0,
#                            w=10,
#                            w_selective=500,
#                            w_quasilective=65,
#                            marker_bufwidth=250,
#                            marker_channel='3m1',
#                            marker_ofs=0)


'''
qubit_a1 = instruments.create('qubit_a1', 'Qubit_Info',
                              deltaf=-100e6-chi2*0.5,
                              pi_amp=1.000,
                              pi2_amp=0.4869,
                              drag=-0.292,
                              pi_amp_quasilective=0.0630,
                              pi_amp_selective=0.00909,
                              rotation='Gaussian',
                              w=5,
                              w_quasilective=60,
                              w_selective=500,
                              channels='5,6',
                              sideband_channels='I11,Q11',
                              sideband_phase=0)


qubit_a2 = instruments.create('qubit_a2', 'Qubit_Info',
                              deltaf=-100e6-chi2,
                              pi_amp=1.000,
                              pi2_amp=0.4869,
                              drag=-0.292,
                              pi_amp_quasilective=0.0630,
                              pi_amp_selective=0.00909,
                              rotation='Gaussian',
                              w=5,
                              w_quasilective=60,
                              w_selective=500,
                              channels='5,6',
                              sideband_channels='I12,Q12',
                              sideband_phase=0)

qubit_a3 = instruments.create('qubit_a3', 'Qubit_Info',
                              deltaf=-100e6-chi2*1.5,
                              pi_amp=1.000,
                              pi2_amp=0.4869,
                              drag=-0.292,
                              pi_amp_quasilective=0.0630,
                              pi_amp_selective=0.00909,
                              rotation='Gaussian',
                              w=5,
                              w_quasilective=60,
                              w_selective=500,
                              channels='5,6',
                              sideband_channels='I13,Q13',
                              sideband_phase=0)

qubit_a4 = instruments.create('qubit_a4', 'Qubit_Info',
                              deltaf=-100e6-chi2*2,
                              pi_amp=1.000,
                              pi2_amp=0.4869,
                              drag=-0.292,
                              pi_amp_quasilective=0.0630,
                              pi_amp_selective=0.00909,
                              rotation='Gaussian',
                              w=5,
                              w_quasilective=60,
                              w_selective=500,
                              channels='5,6',
                              sideband_channels='I14,Q14',
                              sideband_phase=0)

qubit_a5 = instruments.create('qubit_a5', 'Qubit_Info',
                              deltaf=-100e6-chi2*2.5,
                              pi_amp=1.000,
                              pi2_amp=0.4869,
                              drag=-0.292,
                              pi_amp_quasilective=0.0630,
                              pi_amp_selective=0.00909,
                              rotation='Gaussian',
                              w=5,
                              w_quasilective=60,
                              w_selective=500,
                              channels='5,6',
                              sideband_channels='I15,Q15',
                              sideband_phase=0)

qubit_a6 = instruments.create('qubit_a6', 'Qubit_Info',
                              deltaf=-100e6-chi2*3,
                              pi_amp=1.000,
                              pi2_amp=0.4869,
                              drag=-0.292,
                              pi_amp_quasilective=0.0630,
                              pi_amp_selective=0.00909,
                              rotation='Gaussian',
                              w=5,
                              w_quasilective=60,
                              w_selective=500,
                              channels='5,6',
                              sideband_channels='I16,Q16',
                              sideband_phase=0)

qubit_a7 = instruments.create('qubit_a7', 'Qubit_Info',
                              deltaf=-100e6-chi2*3.5,
                              pi_amp=1.000,
                              pi2_amp=0.4869,
                              drag=-0.292,
                              pi_amp_quasilective=0.0630,
                              pi_amp_selective=0.00909,
                              rotation='Gaussian',
                              w=5,
                              w_quasilective=60,
                              w_selective=500,
                              channels='5,6',
                              sideband_channels='I17,Q17',
                              sideband_phase=0)
'''





#qubit_a0s = instruments.create('qubit_a0s', 'Qubit_Info',
#                             deltaf=-100.00e6-FWM_info_SS,
#                              pi_amp=0.727,
#                              pi2_amp=0.358,
#                              drag=0,
#                              pi_amp_quasilective=0.0630,
#                              pi_amp_selective=0.0113,
#                              rotation='Gaussian',
#                              w=7,
#                              w_quasilective=60,
#                              w_selective=500,
#                              channels='5,6',
#                              sideband_channels='I40,Q40',
#                              sideband_phase=0)         
#
#qubit_a2s = instruments.create('qubit_a2s', 'Qubit_Info',
#                             deltaf=-102.64e6-FWM_info_SS,
#                              pi_amp=0.727,
#                              pi2_amp=0.358,
#                              drag=0,
#                              pi_amp_quasilective=0.0630,
#                              pi_amp_selective=0.0113,
#                              rotation='Gaussian',
#                              w=7,
#                              w_quasilective=60,
#                              w_selective=500,
#                              channels='5,6',
#                              sideband_channels='I41,Q41',
#                              sideband_phase=0)         
#
#qubit_a4s = instruments.create('qubit_a4s', 'Qubit_Info',
#                             deltaf=-105.28-FWM_info_SS,
#                              pi_amp=0.727,
#                              pi2_amp=0.358,
#                              drag=0,
#                              pi_amp_quasilective=0.0630,
#                              pi_amp_selective=0.0113,
#                              rotation='Gaussian',
#                              w=7,
#                              w_quasilective=60,
#                              w_selective=500,
#                              channels='5,6',
#                              sideband_channels='I42,Q42',
#                              sideband_phase=0)         

#FWM_info = instruments.create('FWM_info', 'Qubit_Info',
#                              deltaf=-60.09e6,
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
#                              channels='9,10',
#                              sideband_channels='I20,Q20',
#                              sideband_phase=.08,
#                              marker_bufwidth=1500,
#                              marker_ofs=0)

#FWM_info_a2 = instruments.create('FWM_info_a2', 'Qubit_Info',
#                              deltaf=-57.56e6+FWM_info_SS,
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
#                              channels='9,10',
#                              sideband_channels='I21,Q21',
#                              sideband_phase=.08,
#                              marker_bufwidth=1500,
#                              marker_ofs=0)
#
#FWM_info_a4 = instruments.create('FWM_info_a4', 'Qubit_Info',
#                              deltaf=-54.72e6+FWM_info_SS,
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
#                              channels='9,10',
#                              sideband_channels='I23,Q23',
#                              sideband_phase=.08,
#                              marker_bufwidth=1500,
#                              marker_ofs=0)




'''
qubit_b1 = instruments.create('qubit_b1', 'Qubit_Info',
                             deltaf=-101.45e6,
                              pi_amp=.82,
                              pi2_amp=0,
                              drag=0,
                              pi_amp_quasilective=.0214,
                              pi_amp_selective=0.00905,
                              rotation='Gaussian',
                              w=6,
                              w_quasilective=160, #120,
                              w_selective=400,
                              channels='5,6',
                              sideband_channels='I11,Q11',
                              sideband_phase=0)

qubit_b2 = instruments.create('qubit_b2', 'Qubit_Info',
                             deltaf=-102.9e6,
                              pi_amp=.82,
                              pi2_amp=0,
                              drag=0,
                              pi_amp_quasilective=.0214,
                              pi_amp_selective=0.0091,
                              rotation='Gaussian',
                              w=6,
                              w_quasilective=160, #120,
                              w_selective=400,
                              channels='5,6',
                              sideband_channels='I12,Q12',
                              sideband_phase=0)

qubit_b3 = instruments.create('qubit_b3', 'Qubit_Info',
                             deltaf=-104.35e6,
                              pi_amp=.82,
                              pi2_amp=0,
                              drag=0,
                              pi_amp_quasilective=.0214,
                              pi_amp_selective=0.0091,
                              rotation='Gaussian',
                              w=6,
                              w_quasilective=160, #120,
                              w_selective=400,
                              channels='5,6',
                              sideband_channels='I13,Q13',
                              sideband_phase=0)

qubit_b4 = instruments.create('qubit_b4', 'Qubit_Info',
                             deltaf=-105.8e6,
                              pi_amp=.82,
                              pi2_amp=0,
                              drag=0,
                              pi_amp_quasilective=.0214,
                              pi_amp_selective=0.0091,
                              rotation='Gaussian',
                              w=6,
                              w_quasilective=160, #120,
                              w_selective=400,
                              channels='5,6',
                              sideband_channels='I14,Q14',
                              sideband_phase=0)


qubit_b0s = instruments.create('qubit_b0s', 'Qubit_Info',
                             deltaf=-100.00e6-FWM_info_SS,
                              pi_amp=.82,
                              pi2_amp=0,
                              drag=0,
                              pi_amp_quasilective=.0214,
                              pi_amp_selective=0.0121,
                              rotation='Gaussian',
                              w=6,
                              w_quasilective=160, #120,
                              w_selective=300,
                              channels='5,6',
                              sideband_channels='I30,Q30',
                              sideband_phase=0)          


qubit_b2s = instruments.create('qubit_b2s', 'Qubit_Info',
                             deltaf=-102.90e6-FWM_info_SS,
                              pi_amp=.82,
                              pi2_amp=0,
                              drag=0,
                              pi_amp_quasilective=.0214,
                              pi_amp_selective=0.0121,
                              rotation='Gaussian',
                              w=6,
                              w_quasilective=160, #120,
                              w_selective=300,
                              channels='5,6',
                              sideband_channels='I32,Q32',
                              sideband_phase=0)          

qubit_b4s = instruments.create('qubit_b4s', 'Qubit_Info',
                             deltaf=-105.8e6-FWM_info_SS,
                              pi_amp=.82,
                              pi2_amp=0,
                              drag=0,
                              pi_amp_quasilective=.0214,
                              pi_amp_selective=0.0121,
                              rotation='Gaussian',
                              w=6,
                              w_quasilective=160, #120,
                              w_selective=300,
                              channels='5,6',
                              sideband_channels='I34,Q34',
                              sideband_phase=0)          
'''


'''
FWM_info_b2 = instruments.create('FWM_info_b2', 'Qubit_Info',
                              deltaf=-68.1e6+FWM_info_SS,
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
                              channels='9,10',
                              sideband_channels='I22,Q22',
                              sideband_phase=.4,
                              marker_bufwidth=250,
                              marker_channel='13m1',
                              marker_ofs=0)

FWM_info_b4 = instruments.create('FWM_info_b4', 'Qubit_Info',
                              deltaf=-65.2e6+FWM_info_SS,
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
                              channels='9,10',
                              sideband_channels='I24,Q24',
                              sideband_phase=.4,
                              marker_bufwidth=250,
                              marker_channel='13m1',
                              marker_ofs=0)
'''



#cavityR = instruments.create('cavityR', 'Qubit_Info',
#                              deltaf=36e6,
#                              pi_amp=0.642,
#                              pi2_amp=0,
#                              drag=0,
#                              pi_amp_quasilective=0.0102,
#                              pi_amp_selective=0.014,
#                              rotation='Gaussian',
#                              rotation_selective = 'Gaussian',
#                              w=5,
#                              w_quasilective=100,
#                              w_selective=300,
#                              channels='9,10',
#                              sideband_channels='I6,Q6',
#                              sideband_phase=0.22)






#qubit_a1b1 = instruments.create('qubit_a1b1', 'Qubit_Info',
#                              deltaf=-106.0e6,
#                              pi_amp=.80,
#                              pi2_amp=0,
#                              drag=0,
#                              pi_amp_quasilective=.0214, #.0356,
#                              pi_amp_selective=0.0156,
#                              rotation='Gaussian',
#                              w=6,
#                              w_quasilective=160, #120,
#                              w_selective=300,
#                              channels='5,6',
#                              sideband_channels='I11,Q11',
#                              sideband_phase=0)
#
#qubit_a2b2 = instruments.create('qubit_a2b2', 'Qubit_Info',
#                              deltaf=-112.0e6,
#                              pi_amp=.80,
#                              pi2_amp=0,
#                              drag=0,
#                              pi_amp_quasilective=.0214, #.0356,
#                              pi_amp_selective=0.0156,
#                              rotation='Gaussian',
#                              w=6,
#                              w_quasilective=160, #120,
#                              w_selective=300,
#                              channels='5,6',
#                              sideband_channels='I12,Q12',
#                              sideband_phase=0)
#
#qubit_a3b3 = instruments.create('qubit_a3b3', 'Qubit_Info',
#                              deltaf=-118.0e6,
#                              pi_amp=.80,
#                              pi2_amp=0,
#                              drag=0,
#                              pi_amp_quasilective=.0214, #.0356,
#                              pi_amp_selective=0.0156,
#                              rotation='Gaussian',
#                              w=6,
#                              w_quasilective=160, #120,
#                              w_selective=300,
#                              channels='5,6',
#                              sideband_channels='I13,Q13',
#                              sideband_phase=0)


#

#
#qubit_a2b1 = instruments.create('qubit_a2b1', 'Qubit_Info',
#                              deltaf=-110.0e6,
#                              pi_amp=.80,
#                              pi2_amp=0,
#                              drag=0,
#                              pi_amp_quasilective=.0214, #.0356,
#                              pi_amp_selective=0.0156,
#                              rotation='Gaussian',
#                              w=6,
#                              w_quasilective=160, #120,
#                              w_selective=300,
#                              channels='5,6',
#                              sideband_channels='I18,Q18',
#                              sideband_phase=0)

#qubit1bob4 = instruments.create('qubit1bob4', 'Qubit_Info',
#                             deltaf=-104.2e6,
#                              pi_amp=.82,
#                              pi2_amp=0,
#                              drag=0,
#                              pi_amp_quasilective=.0214, #.0356,
#                              pi_amp_selective=0.0152,
#                              rotation='Gaussian',
#                              w=6,
#                              w_quasilective=160, #120,
#                              w_selective=300,
#                              channels='5,6',
#                              sideband_channels='I4,Q4',
#                              sideband_phase=0)




