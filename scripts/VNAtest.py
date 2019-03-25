# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 19:14:47 2019

@author: Wang_Lab
"""

import visa
import sys
from decimal import Decimal
import numpy as np

# N4960A instrument setup
visaTimeout = 120000
n4960aFWRevMin = 2.02   # minimum recommended FW version number
datarate = 25.78125e9   # set datarate to 25.78Gb/s
pattern = "PRBS2^15-1"  # set pattern to PRBS15
amplitude = 0.50        # set single-ended output amplitude to 0.5Vpp
BERMeasDepthExp = 11    # BER depth measurement exponent, depth is 10^-(exp), or 1E-(exp)

# BER measurement depth and 95% confidence interval calculations determined from inputs above
# for more information, contact author
BERMeasDepthBPS = 10**BERMeasDepthExp
BERMeasDepth = 10**-BERMeasDepthExp
maxNumBitErr95PctCI = np.array([0, 0.05129 * BERMeasDepthBPS, 0.3554 * BERMeasDepthBPS, 0.8117 * BERMeasDepthBPS, 1.366 * BERMeasDepthBPS, 1.970 * BERMeasDepthBPS, 2.613 * BERMeasDepthBPS, 3.285 * BERMeasDepthBPS],Decimal)
minNumBitErr95PctCI = np.array([2.996 * BERMeasDepthBPS, 4.744 * BERMeasDepthBPS, 6.296 * BERMeasDepthBPS, 7.754 * BERMeasDepthBPS, 9.154 * BERMeasDepthBPS, 10.51 * BERMeasDepthBPS, 11.84 * BERMeasDepthBPS, 13.12 * BERMeasDepthBPS],Decimal)
BERMeasMaxTime = 5 * (10**(BERMeasDepthExp+1))/datarate + 1  # max time for measurement, most usually should be aborted before this

# N4965A instrument setup
n4965aAddr = "ASRL15"  # "GPIB::18" for local GPIB, "ASRL15" for COM15

# visa write with ESR error checking
def visaWESR(instr,cmd):
    instr.write(cmd)
    esr = int(instr.ask("*ESR?").strip("\n"))
    if (esr != 0):
        print
        print
        print "***** visa write error"
        print "instrument: %s" % instr.resource_name
        print "command: %s" % cmd
        print "*ESR? %d" % esr
        print ":SYST:ERR:ALL?"
        err = instr.ask(":SYST:ERR:ALL?").strip("\n")
        print err
        print

# visa write with error-checking
def visaQ(instr,cmd):
    retVal = instr.ask(cmd).strip("\n")
    esr = int(instr.ask("*ESR?").strip("\n"))
    if (esr != 0):
        print
        print
        print "***** visa query error"
        print "instrument: %s" % instr.resource_name
        print "command: %s" % cmd
        print "result: %s" % retVal
        print "*ESR? %d" % esr
        print ":SYST:ERR:ALL?"
        err = instr.ask(":SYST:ERR:ALL?").strip("\n")
        print err
        print
    return retVal

# find the available instruments
resource_names = []
resource_names = visa.get_instruments_list(False)
for resource in resource_names:
    instr = visa.instrument(resource)
    instr.clear()
    instr.timeout = 120000
    idnStr = instr.ask("*IDN?").strip("\n")
    
    # check localecho
    if (idnStr.find("*IDN?") != -1):
        idnStr = instr.read().strip("\n")  # first read the actual IDN string
        instr.write("!ECHO OFF")           # set echo off
        t = instr.read()                   # throw away the echo

    # check what instrument this is
    if ((idnStr.find("N4960") != -1) | (idnStr.find("SSB16000") != -1)):
        n4960a = instr;
        headStr = n4960a.ask(":SYST:HEAD?").strip("\n").strip("\r")  # query remote heads
        print "N4960A found"
        print " VISA: " + n4960a.resource_name
        print " IDN: " + idnStr
        print " Heads: " + headStr
        print " Errors: " + n4960a.ask(":syst:err:all?").strip("\n")
        print ""
    else:
        print "Unknown instrument:"
        print " VISA: " + resource
        print " IDN: " + idnStr
        print " Errors: " + n4960a.ask(":syst:err:all?").strip("\n")
        print ""
        
# check that the N4960A was found, and that it has a PG and ED head connected
try:
    if (not ((headStr.find("PG") != -1) | (headStr.find("N4951") != -1))) & (not (headStr.find("ED") != -1 | (headStr.find("N4952") != -1))):
        print "A PG and ED head need to be attached; exiting"
        sys.exit(-1)
except NameError:
    print "N4960A not found; exiting"
    sys.exit(-1)

# check that the N4960A controller version is updated
n4960aFWRev = float(idnStr.split(',')[3])
if (n4960aFWRev <  n4960aFWRevMin):
    print "N4960A controller firmware is version " + n4960aFWRev
    print "Please upgrade the firmware beyond version " + n4960aFWRevMin
    sys.exit(-1)
    
# ***************
# now we're connected to the N4960A; prepare the n4960a by asserting a number of settings
# many of these settings are the default values and are unnecessary if the instrument is reset
#
# ** Controller settings
print "Controller settings;",

# reset the instrument (this may not be necessary or desirable)
#  we must query OPC? to determine when this command is complete
n4960a.write("*RST")                 # reset
s = n4960a.ask("*OPC?").strip("\n")  # *OPC? must be sent separately for this command only

# set the controller clock speed; note that the controller architecture uses a half-rate clock
#  we must query OPC? to determine when this command is complete
s = n4960a.ask(":SOUR:FREQ %0.0fHz;*OPC?" % (datarate / 2)).strip("\n")   # 14GHz = 28Gb/s

# check and report instrument errors
print " " + n4960a.ask(":syst:err:all?").strip("\n")

# ** PG settings
print "PG settings;",

# set the pattern generator pattern
#  we must query OPC? to determine when this command is complete
s = n4960a.ask(":PG:DATA:PATT:NAME %s;*OPC?" % pattern).strip("\n")

# set the pattern generator output amplitude (value is single-ended; differential amplitude will be 2x this value)
n4960a.write(":PG:DATA:LLEV:AMPL %0.3f" % amplitude)

# turn the pattern generator ON
n4960a.write(":PG:DATA:OUTP ON")

# check and report instrument errors
print " " + n4960a.ask(":syst:err:all?").strip("\n")

# ** ED settings
print "ED settings;",

# ensure the error detector is OFF, clear any results
n4960a.write(":ED:DATA:ACC:STOP")
n4960a.write(":ED:DATA:ACC:CLR")

# set the error detector pattern
#  we must query OPC? to determine when this command is complete
s = n4960a.ask(":ED:DATA:PATT:NAME %s;*OPC?" % pattern).strip("\n")

# set the error detector measurement to be duration limited and set the max time
#  this measurement time is the maximum amount of time we should measure to make a good measurement
#  to the BER depth at 95% CI; the measurement will often be much shorter, see the measurement details below
n4960a.write(":ED:DATA:ACC:SCON DUR")
n4960a.write(":ED:DATA:ACC:SCON:DUR %0.1fs" % BERMeasMaxTime)

# set the error detector delay to zero
#  we must query OPC? to determine when this command is complete
s = n4960a.ask(":OUTD:DEL 0;*OPC?").strip("\n")

# set the synchronization mode to AUTO, which means the error detector will try to synchronize whenever the BER is high
#  this should be set to MANual for algorithms that run bathtub curve measurements or determine TJ or eye opening width
n4960a.write(":ED:DATA:SYNC:MODE AUTO")

# set the error detector auto align to include both delay and amplitude sweeps
#  limiting the AA sweeps to just delay will speed up the AA process, but eye height won't be reported
n4960a.write(":ED:DATA:AAL:CAAL:DEL ON")    # sweep sampling delay ON
n4960a.write(":ED:DATA:AAL:CAAL:SVOL ON")   # sweep sampling voltage ON

# check and report instrument errors
print " " + n4960a.ask(":syst:err:all?").strip("\n")

# ***************
# now the N4960A and heads are configured, we can run an auto align procedure and make a BER measurement
#
# start the error detector auto-align procedure
#  we must query OPC? to determine when this command is complete
print "ED auto-align;",
s = n4960a.ask(":ED:DATA:AAL:EXEC;*OPC?").strip("\n")

# check AA results: eye width
eyewidth = n4960a.ask(":ED:DATA:AAL:RES:EWID?").strip("\n").strip(" ")
print " eye width: %s" % eyewidth,

# check AA results: eye height
eyeheight = n4960a.ask(":ED:DATA:AAL:RES:EHE?").strip("\n").strip(" ")
print " eye height: %s" % eyeheight

# clear BER results and start BER measurement
print "ED BER meas;",
n4960a.write(":ED:DATA:ACC:CLR")
n4960a.write(":ED:DATA:ACC:STAR")

while True:
    # measure until 95% CI requirement is satisfied, lots of bit errors are detected, or max bits are evaluated
    result = n4960a.ask(":ED:DATA:ACC:RES:ALL?").strip("\n").strip("\r").strip(" ").split(',')
    nBit = Decimal(result[0])
    nErr = Decimal(result[1])
    elapTime = Decimal(result[3].strip("S"))
    run = (result[4].find("RUNN") != -1)

    # repeat until:
    # -we have more than six errors
    # -we measured enough bits to determine to 95% CI requirement that our BER is below our target threshold
    # -or we hit the max time for the measurement (and the measurement stopped already)
    if ((nErr > 6) | (nBit > minNumBitErr95PctCI[nErr]) | (not run)):
        break

# if the BER measurement was aborted early, stop it
if (run): n4960a.write(":ED:DATA:ACC:STOP")

# calculate BER from the number of errors and bits
BER = Decimal(0)
if (nBit != 0): BER = nErr / nBit;

# output results
print " BER: %.0e" % BER,
print " #Bit: %d #Err: %d Time: %0.3fs" % (nBit, nErr, elapTime),

# check and report instrument errors
print " " + n4960a.ask(":syst:err:all?").strip("\n")

# close the VI VISA connections
n4960a.close()