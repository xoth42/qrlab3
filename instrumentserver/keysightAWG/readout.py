""" Python code for readout pulse. Should be the same as example from Andy """



# All current Python Driver calls
import keysightSD1 as key
import time
import numpy as np
import csv

AWG_PRODUCT = "M3202A"
CHASSIS = 1
AWG_SLOT = 8

DIG_PRODUCT = "M3212A"


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
waveform_filepath = "C:\\Users\Public\Documents\Keysight\SD1\Examples\Waveforms\\"
print(waveform_filepath)
gaussian = key.SD_Wave()
gaussian.newFromFile(waveform_filepath + 'Gaussian.csv')

fh_gaussian = key.SD_Wave()
fh_gaussian.newFromFile(waveform_filepath + 'First Half Gaussian.csv')

sh_gaussian = key.SD_Wave()
sh_gaussian.newFromFile(waveform_filepath + 'Second Half Gaussian.csv')

readout = key.SD_Wave()
readout.newFromFile(waveform_filepath + 'Readout.csv')

pause = key.SD_Wave()
pause.newFromFile(waveform_filepath + '10nsPause.csv')

gaussian_data = np.loadtxt(waveform_filepath + 'Gaussian.csv', skiprows = 3)
arr_gaussian = key.SD_Wave()
arr_gaussian.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, gaussian_data)

awg.waveformFlush()
awg.waveformLoad(gaussian, 0)
awg.waveformLoad(fh_gaussian, 1)
awg.waveformLoad(sh_gaussian, 2)
awg.waveformLoad(readout, 3)
awg.waveformLoad(pause, 4)
awg.waveformLoad(arr_gaussian, 5)
# waveformLoad(self, waveformObject, waveformNumber, paddingMode = 0)

# Clear Channel 1
awg.AWGflush(1)
awg.AWGflush(2)

# Setup Sinusoid
awg.channelWaveShape(1, key.SD_Waveshapes.AOU_SINUSOIDAL)
awg.channelAmplitude(1, .0001)
awg.channelFrequency(1, 1e8)    

awg.channelWaveShape(2, key.SD_Waveshapes.AOU_SINUSOIDAL)
awg.channelAmplitude(2, .0001)
awg.channelFrequency(2, 1e8)    
# channelWaveShape(nChannel, waveShape)
# channelAmplitude(nChannel, cdouble_Amplitude)
# channelFrequency(nChannel, cdouble_Frequency) Zero is Baseband, Frequencies are in Hz



# Setup Envelope

awg.AWGqueueWaveform(1, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
awg.AWGqueueWaveform(2, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)

#awg.AWGqueueWaveform(1, 5, key.SD_TriggerModes.AUTOTRIG, 0, 1, 0)
#awg.AWGqueueWaveform(1, 2, key.SD_TriggerModes.SWHVITRIG, 0, 0, 0)
# AWGqueueWaveform(nAWG, waveformNumber, triggerMode, startDelay, cycles, prescaler)

# Modulate the sinusoid and the envelope
awg.modulationAmplitudeConfig(1, key.SD_ModulationTypes.AOU_MOD_AM, 1.5)
awg.AWGqueueConfig(1, 1)

awg.modulationAmplitudeConfig(2, key.SD_ModulationTypes.AOU_MOD_AM, 1.5)
awg.AWGqueueConfig(2, 1)
# Start and softare trigger channel 1
#awg.AWGstart(1)
#awg.AWGtrigger(1)

awg.AWGstartMultiple(3)
awg.AWGtriggerMultiple(3)



