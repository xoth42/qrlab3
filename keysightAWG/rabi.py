import keysightSD1 as key
import time
import numpy as np
import csv



AWG_PRODUCT = "M3202A"
CHASSIS = 1
AWG_SLOT = 7

# CREATE AND OPEN MODULES
awg = key.SD_AOU()
aouID = awg.openWithSlot(AWG_PRODUCT, CHASSIS, AWG_SLOT)

# Gather Information about AWG S/N, Slot and S/N
AWGPart = awg.getProductNameBySlot(CHASSIS, AWG_SLOT)
AWGNumber = awg.getSerialNumberBySlot(CHASSIS, AWG_SLOT)
AWGNumModules = awg.moduleCount()
print("Part =", AWGPart)
print("S/N =", AWGNumber)
print("Number of Modules = ", AWGNumModules)


# Check AWG Connection
if aouID < 0:
    print("ERROR")
    print("aouID:", aouID)
    awg.close()
    print()
    print("AOU closed")

awg.AWGstopMultiple(15)


# Load waveforms to AWG
waveform_filepath = "C:\\qrlab\instrumentserver\keysightAWG\waveforms\\"
print(waveform_filepath)


gaussian = np.loadtxt(waveform_filepath + 'Gaussian.csv', skiprows = 3)
pulse_length = len(gaussian)

wait_time = 0
num_points = 10
num_averages = 1
power = np.linspace(.1, 1, num_points)

full_length = pulse_length + wait_time

awg.waveformFlush()

# Load the trigger
trigger = key.SD_Wave()
''' Trigger every power cycle '''
#trigger_data = np.concatenate((np.ones(10)*.5, np.zeros(full_length*num_points-10)))
''' Trigger every waveform '''
trigger_data = np.concatenate((np.ones(10), np.zeros(full_length-10)))
trigger.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, trigger_data)
awg.waveformLoad(trigger, 0)


wave_data = np.zeros((full_length) * num_points, dtype=float)
# Load the rabi pulses
for i in range(num_points):
    wave_data[i * full_length: i * full_length + pulse_length] = gaussian * power[i]
    
wave = key.SD_Wave()
wave.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, wave_data)
awg.waveformLoad(wave, 1)

# Clear Channels
awg.AWGflush(1)
awg.AWGflush(2)
awg.AWGflush(3)
awg.AWGflush(4)

# Setup Sinusoid
awg.channelWaveShape(1, key.SD_Waveshapes.AOU_SINUSOIDAL)
awg.channelAmplitude(1, 0)
awg.channelFrequency(1, 1e8)

awg.channelAmplitude(2, .7)
awg.channelAmplitude(3, .7)
awg.channelAmplitude(4, .7)

awg.channelWaveShape(2, key.SD_Waveshapes.AOU_AWG)
awg.channelWaveShape(3, key.SD_Waveshapes.AOU_AWG)
awg.channelWaveShape(4, key.SD_Waveshapes.AOU_AWG)

# Setup Envelopes
awg.AWGqueueWaveform(1, 1, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
awg.AWGqueueWaveform(2, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
awg.AWGqueueWaveform(3, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
awg.AWGqueueWaveform(4, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)

awg.AWGqueueWaveform(1, 1, key.SD_TriggerModes.AUTOTRIG, 0, num_averages-1, 0)
awg.AWGqueueWaveform(2, 0, key.SD_TriggerModes.AUTOTRIG, 0, num_averages-1, 0)
awg.AWGqueueWaveform(3, 0, key.SD_TriggerModes.AUTOTRIG, 0, num_averages-1, 0)
awg.AWGqueueWaveform(4, 0, key.SD_TriggerModes.AUTOTRIG, 0, num_averages-1, 0)


# Modulate the sinusoid and the envelope
awg.modulationAmplitudeConfig(1, key.SD_ModulationTypes.AOU_MOD_AM, 1.5)
# Setup the queue in cyclic mode
awg.AWGqueueConfig(1,0)
awg.AWGqueueConfig(2,0)
awg.AWGqueueConfig(3,0)
awg.AWGqueueConfig(4,0)






# Start and softare trigger channel 1
#awg.AWGstart(2)
awg.AWGstartMultiple(15)
awg.AWGtriggerMultiple(15)



#awg.AWGtrigger(1)
#awg.AWGtriggerMultiple(3)


#awg.AWGpause(1)
#time.sleep(.01)
#awg.AWGresume(1)
#awg.AWGtrigger(1)


