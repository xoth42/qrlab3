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
print(("Part =", AWGPart))
print(("S/N =", AWGNumber))
print(("Number of Modules = ", AWGNumModules))


# Check AWG Connection
if aouID < 0:
    print("ERROR")
    print(("aouID:", aouID))
    awg.close()
    print()
    print("AOU closed")




# Load waveforms to AWG
waveform_filepath = "C:\\Users\Public\Documents\Keysight\SD1\Examples\Waveforms\\"
print(waveform_filepath)


gaussian = np.loadtxt(waveform_filepath + 'Gaussian.csv', skiprows = 3)

num_points = 2
num_averages = 1
power = np.linspace(.1, 1, num_points)

awg.waveformFlush()
for n in range(num_averages):
    for i in range(num_points):
        wave = key.SD_Wave()
        wave.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, gaussian*power[i])
        awg.waveformLoad(wave, n*num_points + i)

# Clear Channel 1
awg.AWGflush(1)

# Setup Sinusoid
awg.channelWaveShape(1, key.SD_Waveshapes.AOU_SINUSOIDAL)
awg.channelAmplitude(1, .0001)
awg.channelFrequency(1, 1e8)

# Setup Envelopes
for n in range(num_averages):
    for i in range(num_points):
        awg.AWGqueueWaveform(1, n*num_points + i, key.SD_TriggerModes.AUTOTRIG, 0, 1, 0)

# Modulate the sinusoid and the envelope
awg.modulationAmplitudeConfig(1, key.SD_ModulationTypes.AOU_MOD_AM, 1.5)
# Setup the queue in cyclic mode
awg.AWGqueueConfig(1, 1)

# Start and softare trigger channel 1
awg.AWGstart(1)

awg.AWGtrigger(1)


#awg.AWGpause(1)
#time.sleep(.01)
#awg.AWGresume(1)
#awg.AWGtrigger(1)


