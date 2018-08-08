# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 10:57:53 2016

@author: Andy Westwood
First simple routine to readout and display captured data fom the Dig
"""

# Import the driver calls and create an instance of SD_DIO
from signadyne_Fixes_PXie_TriggerReadWrite import *
DIGobj = SD_AIN()
AWGobj = SD_AOU()

# Gather Information about Digitizer S/N, Slot and S/N
DigPart = DIGobj.getProductNameBySlot(1,15)
DigNumber = DIGobj.getSerialNumberBySlot(1,15)
NumModules = DIGobj.moduleCount()
print("Part =",DigPart)
print("S/N =",DigNumber)
print("Number of Modules = ",NumModules)

# Gather Information about AWG S/N, Slot and S/N
AWGPart = AWGobj.getProductNameBySlot(1,13)
AWGNumber = AWGobj.getSerialNumberBySlot(1,13)
NumModules = AWGobj.moduleCount()
print("Part =",AWGPart)
print("S/N =",AWGNumber)
print("Number of Modules = ",NumModules)

# Open the Digitizer Module
#DigModuleIDbySN = DIGobj.openWithSlot("",1,6)
DIGModuleIDbySlot = DIGobj.openWithSlot("SD-PXE-DIG-H3314F-2G",1,15)
#DigModuleIDbySN = DIGobj.openWithSerialNumber("SD-PXE-DIG-H3314F-2G","0VKHSVU4")
#print("Digitizer ModuleID by S/N = ", DigModuleIDbySN)
print "Module ID by Slot", DIGModuleIDbySlot

# Open the AWG Module
#AWGModuleIDbySN = AWGobj.openWithSlot("",1,5)
AWGModuleIDbySlot = AWGobj.openWithSlot("SD-PXE-AWG-H3344F-2G",1,13)
AWGModuleIDbySN = AWGobj.openWithSerialNumber("SD-PXE-AWG-H3344F-2G","0VKHSVMJ")
#print("AWG ModuleID by S/N = ", AWGModuleIDbySN)
print "Module ID by Slot", AWGModuleIDbySlot
# Configure a waveform and send from the AWG using all-in-one command
#AWGFromFile(nAWG,waveformFile,triggerMode,startDelay,cycles,prescaler,paddingMode=0)
#AWGobj.AWGFromFile(0,"C:/Users/Public/Documents/Signadyne/Examples/Waveforms/Gaussian.csv",0,0,0,0)

# Configure a waveform and send from the AWG using individual commands
wave = SD_Wave()
# newFromFile(self, waveformFile)
wave.newFromFile("C:/Users/Public/Documents/Signadyne/Examples/Waveforms/Gaussian.csv")
# waveformLoad(self, waveformObject, waveformNumber, paddingMode = 0)
waveformLoaded = AWGobj.waveformLoad(wave, 0)
print "Loaded Waveform = ", waveformLoaded
# channelWaveShape(nChannel, waveShape)
AWGobj.channelWaveShape(0, SD_Waveshapes.AOU_AWG)
AWGobj.channelWaveShape(1, SD_Waveshapes.AOU_AWG)
# AWG.channelAmplitude(ch, value in Volts)
AWGobj.channelAmplitude(0, 1.0)
AWGobj.channelAmplitude(1, 1.0)
# AWGqueueWaveform(self, nAWG, waveformNumber, triggerMode, startDelay, cycles, prescaler)
AWGobj.AWGqueueWaveform(0, 0, 0, 0, 0, 0)
AWGobj.AWGqueueWaveform(1, 0, 0, 0, 0, 0)
# triggermode >>> 0=Auto, 1=Software/HVI, 5=S/HVI-perCycle, 2=External Trigger, 6=ExternalTrigger/Cycle
# AWGqueueMarkerConfig(self, nAWG, markerMode, trgPXImask, trgIOmask, value, syncMode, length, delay) 
# length must be equal or greater than 2
# AWGobj.AWGqueueMarkerConfig(0, 1, 0x01, 0, 1, 0, 2, 0)
AWGobj.AWGqueueMarkerConfig(0, SD_MarkerModes.START, 0x01, 0, SD_TriggerValue.HIGH, SD_SyncModes.SYNC_CLK10, 10, 0)

print("TriggerValue Before Module Start =", DIGobj.PXItriggerRead(SD_TriggerExternalSources.TRIGGER_PXI0))

# Configure two Digitizer channels
# Channel 0 is the Analog Triggered Channel and Channel 1 is the External/PXIe 
# Coupling: 0=DC, 1=AC
# Impedance 0=High-Z, 1=50Ohms
# channelInputConfig(self, channel, fullScale, impedance, coupling)
#ConfigResult = DIGobj.channelInputConfig(0, 3.0, 1, 1)
ConfigResult = DIGobj.channelInputConfig(1, 3.0, 1, 1)

# channelTriggerConfig(self, channel, analogTriggerMode, threshold)  This setsup the Analog channel
#DIGobj.channelTriggerConfig(0, SD_AIN_TriggerMode.RISING_EDGE, 0.001)
# DAQtriggerConfig(self, channel, digitalTriggerMode, digitalTriggerSource, analogTriggerMask)
#  This setsup the External/PXIe channel
#DIGobj.DAQtriggerConfig(1, 0, 0, 0x01)

# Configure the DAQ per instructions
# DAQconfig(nDAQ,nDAQPoints/Cycle,nCycles,preScaler,triggerMode)
ConfigDAQResult = DIGobj.DAQconfig(1,100,10,1,SD_TriggerModes.EXTTRIG)
# DAQtriggerExternalConfig(self, nDAQ, externalSource, triggerBehavior)
ConfigTrigExtResult = DIGobj.DAQtriggerExternalConfig(1, SD_TriggerExternalSources.TRIGGER_PXI0, SD_TriggerBehaviors.TRIGGER_FALL)
print("DAQconfig Result = ", ConfigDAQResult)
print("DAQTrigger Result = ", ConfigTrigExtResult)

DIGobj.DAQstart(1)
AWGobj.AWGstart(0)
AWGobj.AWGstart(1)

print("TriggerValue AFTER Module Start =", DIGobj.PXItriggerRead(SD_TriggerExternalSources.TRIGGER_PXI0))

# Force PXIe Trigger High
forceTrigger = DIGobj.PXItriggerWrite(SD_TriggerExternalSources.TRIGGER_PXI0, SD_TriggerValue.HIGH)
# Now Force it Low and the DAQ does recognize the Falling Edge
forceTrigger = DIGobj.PXItriggerWrite(SD_TriggerExternalSources.TRIGGER_PXI0, SD_TriggerValue.LOW)
# Question here = Why doesn't the command on line number 65 result in arming the trigger in a High State?
# If I just force the Trigger Low it times out

# Read the DAQ contents, currently the DigResult is simply a "0"
# I suspect it is waiting for a trigger
#DIGobj.DAQread(nDAQ,nPoints,timeOut)
DigResult = DIGobj.DAQread(1,1000,1)
print("DAQread Result = ", DigResult)

# Stop the AWG
AWGobj.AWGstop(0)
# Close the session and clear out variables
DIGobj.close()
AWGobj.close()
