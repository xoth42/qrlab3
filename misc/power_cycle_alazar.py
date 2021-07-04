# -*- coding: utf-8 -*-


import ctypes
import numpy as np
import types
import time
import logging

import win32api
import msvcrt

# Load DLL, 64-bit seems to require windll, 32-bit cdll.
_DLL_FILE = r'c:\windows\system32\ATSApi.dll'
try:
    ats = ctypes.windll.LoadLibrary(_DLL_FILE)
    ats.AlazarGetStatus(0)
except:
    ats = ctypes.cdll.LoadLibrary(_DLL_FILE)

handle = ats.AlazarGetBoardBySystemID(1, 1)

return_code = ats.AlazarSleepDevice(handle, 0x0)
print(return_code)
power_code = ats.AlazarSleepDevice(handle, 0x1)
print(power_code)

