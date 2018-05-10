import sys
#sys.path.append('C:\Program Files (x86)\Keysight\SD1\Libraries\Python')
#import visa

# All current Python Driver calls
import keysightSD1

# HVI Objects
# hvi = keysightSD1.SD_HVI()
# hviID = hvi.open('setPhase.HVI')

# MODULE CONSTANTS
	# change PRODUCT to module type
AWG_PRODUCT = "M3202A"
DIG_PRODUCT = "M3212A"
	# change CHASSIS to Chassis number 1, 2, 3, etc.
CHASSIS = 1
	# change slot number to target slot
AWG_SLOT = 7
DIG_SLOT = 8

# CREATE AND OPEN MODULES
aou = keysightSD1.SD_AOU()
ain = keysightSD1.SD_AIN()
aouID = aou.openWithSlot(AWG_PRODUCT, CHASSIS, AWG_SLOT)

# Gather Information about Digitizer S/N, Slot and S/N
DigPart = ain.getProductNameBySlot(CHASSIS, DIG_SLOT)
DigNumber = ain.getSerialNumberBySlot(CHASSIS, DIG_SLOT)
DIGNumModules = ain.moduleCount()
print("Part =", DigPart)
print("S/N =", DigNumber)
print("Number of Modules = ", DIGNumModules)

# Gather Information about AWG S/N, Slot and S/N
AWGPart = aou.getProductNameBySlot(CHASSIS, AWG_SLOT)
AWGNumber = aou.getSerialNumberBySlot(CHASSIS, AWG_SLOT)
AWGNumModules = aou.moduleCount()
print("Part =", AWGPart)
print("S/N =", AWGNumber)
print("Number of Modules = ", AWGNumModules)


# Initiate Module Settings
if aouID > -1:
	wave = keysightSD1.SD_Wave()
	# NOTE double "\" after "C:" is required because "\U" starts a unicode sequence
	wave.newFromFile('C:\\Users\Public\Documents\Keysight\SD1\Examples\Waveforms\Gaussian.csv')

	aou.waveformFlush()
	aou.waveformLoad(wave, 0)
	# waveformLoad(self, waveformObject, waveformNumber, paddingMode = 0)

	aou.AWGflush(1)
	aou.AWGqueueWaveform(1, 0, keysightSD1.SD_TriggerModes.SWHVITRIG, 1, 5, 0)
	aou.AWGflush(2)
	aou.AWGqueueWaveform(2, 0, keysightSD1.SD_TriggerModes.SWHVITRIG, 0, 0, 0)
	# AWGqueueWaveform(nAWG, waveformNumber, triggerMode, startDelay, cycles, prescaler)

	aou.channelWaveShape(1, keysightSD1.SD_Waveshapes.AOU_AWG)
	aou.channelAmplitude(1, 1.0)
	aou.channelFrequency(1, 0)
	# channelWaveShape(nChannel, waveShape)
	# channelAmplitude(nChannel, cdouble_Amplitude)
	# channelFrequency(nChannel, cdouble_Frequency) Zero is Baseband, Frequencies are in Hz

	aou.channelWaveShape(2, keysightSD1.SD_Waveshapes.AOU_AWG)
	aou.channelAmplitude(2, 1.0)
	aou.channelFrequency(2, 0)

	aou.AWGstartMultiple(3)
	aou.AWGtriggerMultiple(3)

	voltOffsetIncr  = 0.01
	voltOffset0 = 0.0
	voltOffset1 = 0.0
	aou.channelOffset(1,voltOffset0)
	aou.channelOffset(2,voltOffset1)

	# hvi.start() Used later for User GUI work

else:
	print("ERROR")
	print("aouID:", aouID)

	# Run I/Q Voltage Offset Loop


	# exiting...
	aou.close()
	print()
	print("AOU closed")
