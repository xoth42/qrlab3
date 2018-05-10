
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




# Load waveforms to AWG
waveform_filepath = "C:\\qrlab\instrumentserver\keysightAWG\waveforms\\"
print(waveform_filepath)


gaussian = np.loadtxt(waveform_filepath + 'Gaussian.csv', skiprows = 3)
pulse_length = len(gaussian)

wait_time = 100
num_points = 10
power = np.linspace(.1, 1, num_points)

full_length = pulse_length + wait_time

awg.waveformFlush()

# Load the trigger
trigger = key.SD_Wave()
trigger_data = np.concatenate((np.ones(10), np.zeros(full_length-10)))
trigger.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, trigger_data)
awg.waveformLoad(trigger, 0)

pause = key.SD_Wave()
pause.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, np.zeros(wait_time))
awg.waveformLoad(pause, 1)

gaussian = np.concatenate((gaussian, np.zeros(wait_time)))
# Load the rabi pulses
for i in range(num_points):
    wave = key.SD_Wave()
    wave.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, gaussian*power[i])
    awg.waveformLoad(wave, i + 2)
    


# Clear Channels
awg.AWGflush(2)
awg.AWGflush(3)

# Setup Sinusoid
awg.channelWaveShape(2, key.SD_Waveshapes.AOU_SINUSOIDAL)
awg.channelAmplitude(2, 0)
awg.channelFrequency(2, 1e8)

awg.channelWaveShape(3, key.SD_Waveshapes.AOU_AWG)

awg.channelAmplitude(2, 0)
awg.channelAmplitude(3, 2)

awg.modulationAmplitudeConfig(2, key.SD_ModulationTypes.AOU_MOD_AM, 1.5)

# Setup the queue in cyclic mode
awg.AWGqueueConfig(2,1)
awg.AWGqueueConfig(3,1)

print('cyclic modes', awg.AWGqueueConfigRead(1), awg.AWGqueueConfigRead(1))

#pause at start
awg.AWGqueueWaveform(2, 1, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
awg.AWGqueueWaveform(3, 1, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)


# Setup Envelopes
for i in range(num_points):
    awg.AWGqueueWaveform(2, i + 2, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
    # Setup outgoing trigger
    awg.AWGqueueWaveform(3, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)


awg.AWGstartMultiple(15)
