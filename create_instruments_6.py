import time

import matplotlib.pyplot as plt
import os
import numpy
if 1:

    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

from mclient import instruments
from scipy.signal import savgol_filter
from scipy.integrate import simps
import random

AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='TCPIP0::172.30.56.25::inst0::INSTR', clock=1e9, refsrc='EXT', reffreq=10e6)

sn = instruments.create('sn',
        "SignalHoundSM200A",
        speed='auto',
        center=1e8,
        span=1e4,
        vbw=300,
        rbw=300,
        ref=10,
        spur=False)
a, b = sn.sweep()
import matplotlib.pyplot as plt


time_choice = [i for i in range(0, 16)]
data = []
size = 20
wave = 'sine4'   
chan = '4'
points = 2
data = [[] for _ in range(0, size)]
choices = []


def dB_to_power(x):
    return 10**(x/10.0)
def moving_window(x, window_length):
    for i in range(window_length, len(x) - window_length):
        x[i] = numpy.average(x[i - window_length:i + window_length])
    return x
for k in range(0, size):
    
    print 'SIGNAL OFF'
    AWG1.all_off()
    time.sleep(2)       
    avg_power = []
    for _ in range(0, 5):
        freq, log_powers = sn.sweep()
   #     powers = [power[i] + abs(min(power)) for i in power]
        avg_power.append(log_powers)
    avg_power = numpy.asarray(avg_power)
    avg_waveform = avg_power.mean(axis = 0)
    baseline_in_W = map(dB_to_power, avg_waveform)
    integrated_averaged_baseline = simps(baseline_in_W)
    print 'ON SIGNAL ' + str(k)
    wait_time = random.choice(time_choice)
    time.sleep(wait_time)
    choices.append(wait_time)
    AWG1.all_on()
    
    print "BEGINNING"
    
    fig_prefix = "C:\\Users\\wanglab\\Desktop\\AWG_tests\\"
    new_direc = fig_prefix + 'run_' + str(k)
    os.mkdir(new_direc)
    for i in range(0, points):
        sweep_waveforms = []
        for _ in range(0, 100):
            a, b = sn.sweep()
            sweep_waveforms.append(b)
        waveform = numpy.mean(sweep_waveforms, axis = 0)
      #  raised_b = [b[i] + abs(min(b)) for i in b]
        actual_power = map(dB_to_power, waveform)      
        integrated_power = simps(actual_power)
        plt.plot(a, waveform)
        plt.grid()
        plt.title('AWG run sine plot # ' + str(i))
        corrected_power = abs(integrated_power) - abs(integrated_averaged_baseline)
        plt.legend([str(corrected_power)])
        plt.savefig(new_direc + '\\' + str(i) + '_' + str(time.time()) + '.png', format = 'png' )
        plt.close()

        data[k].append(corrected_power)
        time.sleep(0.5)
import csv
with open(fig_prefix + 'data.csv', 'wb') as myfile:
    wr = csv.writer(myfile)
    wr.writerows(data)
def nice_plot(data, wave, chan):
    for i in range(0, len(data)):
        plt.figure()
        plt.scatter(range(0, len(data[i])), data[i])
        plt.xlabel('t (~s)')
        plt.ylabel('dBm')
        plt.grid()
        plt.title('Run ' +str(wave) +   ' points: ' + str(points) + ' plot ' + str(i) + ' on channel ' + str(chan))
        analysis_direc = 'C:\\Users\\wanglab\\Desktop\\AWG_analysis\\'
        plt.savefig(analysis_direc + str(i) + '.png', format = 'png')
        plt.close()
        plt.figure()
        plt.hist(data[i], bins = 'auto')
        plt.title('Histogram of run: ' + str(i) + ' on wave ' + str(wave) + ' with chan ' + str(chan))
        plt.grid()
        plt.savefig(analysis_direc + '_hist_' + str(i))
    
       # plt.show()

nice_plot(data, wave, chan)
plt.figure()
for i in sweep_waveforms:
    plt.plot(i)
    
plt.plot(waveform, 'k*')
#plt.plot(waveform_, 'b*')
plt.grid()
plt.show()

#plt.close('all')
import csv
#import numpy as np
#f_4 = open('C:\\Users\\wanglab\\Desktop\\results\\chan_3_\\AWG_tests\\data.csv', 'rb')
#reader_4 = csv.reader(f_4)
#data_4_large = list(reader_4)
#data_4 = np.asarray(data_4_large, dtype = np.float)
#
#
#f_3 = open('C:\\Users\\wanglab\\Desktop\\results\\channel_3_A\\AWG_tests\\data.csv', 'rb')
#reader_3 = csv.reader(f_3)
#data_3_large = list(reader_3)
#data_3 = np.asarray(data_3_large, dtype= np.float)
#def linear(x, a, b):
#    return a*x + b
#from scipy.optimize import curve_fit
#params, cov = curve_fit(linear, range(0, len(data_4[4])), list(data_4[4]))
#def linear(x, a, b):
#    return a*x + b
#from scipy.optimize import curve_fit
#def find_start_position(data):
#    params, cov = curve_fit(linear, range(0, len(data)), data)
#    return params[1]
#intercepts = map(find_start_position, data)

size = 20
wave = 'sine4'
chan = '4'
points = 2
import numpy as np
import csv
f = open(r'C:\Users\wanglab\Desktop\AWG_tests\data.csv', 'rb')
r = csv.reader(f)
g = list(r)
data = np.asarray(g, dtype=np.float)



import matplotlib.pyplot as plt
intercepts = [i[0] for i in data]
plt.close('all')
plt.figure()
plt.plot(intercepts, 'bo')
plt.title('Randomized off times amplitude starting points for ' + wave + ' on channel ' + chan)
plt.grid()
plt.plot(choices, 'r*')
plt.show()
plt.close('all')


figure, axis1 = plt.subplots()
axis1.plot(intercepts, 'bo')
axis1.set_ylabel('amplitudes', color='b')
axis1.tick_params('y', colors = 'b')
ax2 = axis1.twinx()
ax2.plot(choices, 'r*')
ax2.set_ylabel('off times', color = 'r')
ax2.tick_params('y', colors = 'r')
figure.tight_layout()
plt.grid()
plt.show()
              
              

#
#






#
#qubit1ge = instruments.create('qubit1ge', 'Qubit_Info',
#                              deltaf=-100e6,
#                              pi_amp=0.342948,
#                              pi2_amp=0.171474,
#                              drag=-0.9,
#                              pi_amp_quasilective=0.027025,
#                              pi_amp_selective=0.34 / 25,
#                              rotation='Gaussian',
#                              w=40,
#                              w_quasilective=100,
#                              w_selective=500,
#                              channels='5,6',
#                              sideband_channels='I1,Q1',
#                              sideband_phase=1.315)
#
#
#refbrick = instruments.create('refbrick', 'LabBrick_RFSource', serial=14511, 
#                            use_extref=True) #reference
#RObrick = instruments.create('RObrick', 'LabBrick_RFSource', serial=18239,
#                             use_extref=True) #readout
##brick1 = instruments.create('brick1', 'LabBrick_RFSource', serial=14510,
##                           use_extref=False) #qubit
##
###sc1 = instruments.create('sc1', 'SC5511A', devid='100016B6')
###sc2 = instruments.create('sc2', 'SC5511A', devid='100016B6')
##
#AWG1 = instruments.create('AWG1', 'Keysight_AWG', chassis = 0, slot = 7,
#                             AWG_PRODUCT = "M3202A",
#                             amps = [1, 1, 1, 1], ofs = [0, 0, 0, 0])
##
#AWG2 = instruments.create('AWG2', 'Keysight_AWG', chassis=0, slot=10,
#                         AWG_PRODUCT="M3202A",
#                         amps = [1, 1, 1, 1], ofs = [0, 0, 0, 0])
#
## Magnet = instruments.create('Magnet','AMI_430')
#
##
#readout = instruments.create('readout', 'Readout_Info', IQe=(1.0), IQg=(0.1),
#                             IQe_radius= 1 , rfsource1='RObrick', 
#                             rfsource2='refbrick',
#                             pulse_len=1000, readout_chan='5', acq_chan='6')
#
#
#''' Readout_IQ_Info is for iq modulation on the readout brick instead of pulse triggering '''
##readout = instruments.create('readout', 'Readout_IQ_Info', IQe=(1.0), IQg=(0.1),
##                             IQe_radius= 1 , rfsource1='RObrick', rfsource2='refbrick',
##                             pulse_len=2000, readout_chan_I=3, readout_chan_Q=4,
##                             acq_chan=1)
#
## VNA = instruments.create('VNA', 'Agilent_E5071C',
## address='TCPIP0::K-E5071C-26868.local::inst0::INSTR')
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

#test = instruments.create('sh_test', 'SignalHoundUSBSA124B', waittime=100000,
#                          serial_no=61660103, ref=10, center=1.2e8,
#                          span=2e7, vbw=200e3, rbw=200e3)
#peaks, array = test.perform_sweep(peak_find = True, plot = False)




    
# AWG1.do_set_waveform_delay(200000)
# bla

# VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB0::17::INSTR')


#AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='AWG1')

#sc1 = instruments.create('sc1', 'SC5511A', devid='100016B6')



#brick3 = instruments.create('brick3', 'LabBrick_RFSource', serial=18239, use_extref=True) # old RO
#brick = instruments.create('brick', 'LabBrick_RFSource', serial=18608, use_extref=True)
#brick4 = instruments.create('brick4', 'LabBrick_RFSource', serial=17912, use_extref=True) # RO


# fg = instruments.create('funcgen', 'Agilent_33250A', serial=2391)

# fg = instruments.create('funcgen', 'Agilent_33250A', address='GPIB1::30')

# fg = instruments.create('funcgen', 'BNC_FuncGen645', address='GPIB1::30')
# Setup Alazar

#alz = instruments.create('alazar', 'Alazar_Daemon')
#alz.set_ch1_range('40mV')
#alz.set_ch2_range('40mV')
#alz.set_nsamples(4800)
#alz.set_naverages(2000)
#alz.set_ch1_coupling('AC')
#alz.set_ch2_coupling('AC')
##alz.set_clock_source('EXT10M')
#alz.set_clock_source('EXT')
#alz.set_sample_rate('1GEXT10')
#alz.set_engJ_trig_src('EXT')
#alz.set_engJ_trig_lvl(128+5)
#alz.set_real_signals(False)
#alz.set_timeout(10e3)
##TODO this should be fixed. we should be able to setup_clock
##alz.setup_clock()
#alz.setup_channels()
#alz.setup_trigger()

# readout = instruments.create('readout', 'Readout_Info', IQe=(1.0), IQg=(0.1),
#                           IQe_radius= 1 , rfsource1='brick1',
# rfsource2='brick5',
#                           pulse_len=1000, readout_chan='1m2', acq_chan='2m1')



# AWG2 = instruments.create('AWG2', 'Tektronix_AWG5014C', address='AWG2',
#                          clock=1e9, refsrc='EXT', reffreq=10e6)

# ag1 = instruments.create('ag1', 'Agilent_N5183A', address='GPIB1::19')
# ag2_JPC = instruments.create('ag2_JPC', 'Agilent_N5183A', address='GPIB1::20')
# ag2 = instruments.create('ag2', 'Agilent_N5183A', address='GPIB1::22')

# instruments.remove('brick4')
# instruments.remove('brick3')
# instruments.remove('brick2')
# instruments.remove('brick1_LO')
#
# brick4 = instruments.create('brick4', 'LabBrick_RFSource', serial=10387)  #
# or devid
# brick1_LO = instruments.create('brick1_LO', 'LabBrick_RFSource',
# serial=5937)  # or devid
##brick4 = instruments.create('brick4', 'LabBrick_RFSource', serial=1352)
# brick3 = instruments.create('brick3', 'LabBrick_RFSource', serial=2495)  #
# or devid
# brick2 = instruments.create('brick2', 'LabBrick_RFSource', serial=2486)  #
# or devid
#
# VA = instruments.create('VA', 'Vlastakis_Spec', address = 'COM3', rfsource
# = 'brick4', if_freq = 10.596e6, delay =  0.04 )
#
##yoko = instruments.create('yoko', 'Yokogawa_)
##laserfg = instruments.create('laserfg', 'Agilent_FuncGen33250A',
# address='GPIB1::9')

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
