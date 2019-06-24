# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 10:59:06 2019

@author: Wang_Lab
"""

import numpy as np
import time
import mclient

Yoko = mclient.instruments['Yoko']

currents = np.linspace(-0.3e-3, -1.5e-3, 1201)

for current in currents:
    Yoko.do_set_current(current)
    time.sleep(2)