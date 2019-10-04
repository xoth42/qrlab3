# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 13:32:21 2019

@author: Wang_Lab
"""

import mclient
reload(mclient)

#ge_ss = -1.625e6#-1.261e6 #-1.295e6
#ge_ss = -2.745e6
#fwm_ss = 1.835e6
ge_ss = 0
fwm_ss = -ge_ss
#fwm_ss = 0

qubit_a0s = mclient.instruments['qubit_a0s']
qubit_a2s = mclient.instruments['qubit_a2s']
qubit_a4s = mclient.instruments['qubit_a4s']

FWM_info = mclient.instruments['FWM_info']
FWM_info_a2 = mclient.instruments['FWM_info_a2']
FWM_info_a4 = mclient.instruments['FWM_info_a4']

qubit_a0s.set_deltaf(-100.00e6+ge_ss)
qubit_a2s.set_deltaf(-102.64e6+ge_ss)
qubit_a4s.set_deltaf(-105.28e6+ge_ss)

FWM_info.set_deltaf(-60e6+fwm_ss)
FWM_info_a2.set_deltaf(-57.36e6+fwm_ss)#-2.64e6*2)
FWM_info_a4.set_deltaf(-54.72e6+fwm_ss)
#FWM_info_a2.set_deltaf(-54e6+fwm_ss)
#FWM_info_a4.set_deltaf(-50e6+fwm_ss)

