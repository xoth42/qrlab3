# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 00:52:31 2020

@author: Wang_Lab
"""

from serial import Serial


#ser = Serial('COM3')

print((ser.name))

ch = ser.write('+')
#print(ser.read(2))
ser.read(2)