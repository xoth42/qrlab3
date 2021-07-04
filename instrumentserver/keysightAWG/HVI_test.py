# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 15:40:19 2017
Written by Josh Carey
joshuacarey@umass.edu
"""
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


HVI_file_location = r"C:\\Users\\Wang Lab\\Desktop\\Josh_HVI_work"
path = HVI_file_location + "\\trigger.HVIprj"
awg.compileHVI(path)
