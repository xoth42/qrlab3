# -*- coding: utf-8 -*-
"""
Created on Wed May 27 13:38:07 2020

@author: Jack
"""

import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import leastsq
from scipy.optimize import curve_fit
#Original data
# amps = np.array([.05,.06,.08,.1,.125,.15,.2,.25,.3,.35,.4,.45,.5])
# ss_fe = np.array([.109,.168,.386,.521,.780,1.049,1.451,1.829,2.310,2.528,2.751,2.956,3.118])

# ss_ge = np.array([.079,.122,.231,.370,.563,.694,1.015,1.484,1.903,2.130,2.201,2.187,2.120])

# ss_ge_116 = np.array([.081,.113,.226,.342,.533,.672,1.006,1.449,1.88,2.151,2.243,2.232,2.192])

# amps_FT1 = np.array([.1,.15,.2,.25,.3,.35,.4,.45,.5])

# FT1 = np.array([2.098,2.132,1.850,1.146,.765,.686,.538,.658,.488,.445,.439,.476])

# powers = np.array([-11.4,-9.85,-7.55,-6,-4.05,-3.1,-1.211,-.28,.15,.4,.8,.98,1.1])

# powers_lin = 10**(powers/10)

# powers_FT1 = np.array([-100,-25.8,-11.4,-6,-3.1,-1.211,-.28,.15,.4,.8,.98,1.1])

# powers_lin_FT1 = 10**(powers_FT1/10)

# plt.figure()
# plt.title('change in starkshift')
# plt.ylabel('stark shift')
# plt.xlabel('power')
# plt.plot(powers_lin,ss_fe,label = 'fe')
# plt.plot(powers_lin,ss_ge,label = 'ge')
# plt.legend()

# plt.figure()
# plt.title('change in FT1')
# plt.ylabel('1/FT1 microseconds')
# plt.xlabel('power^2')
# plt.plot(powers_lin_FT1,1/FT1)

#Data with outliers omitted:
    
# ss_fe = np.array([.109,.168,.386,.521,.780,1.049,1.451,1.829])

# ss_ge = np.array([-521785.96688388224,
#  -703261.7982840007,
#  -1129374.6950299076,
#  -1537955.405950409,
#  -1855476.740050007,
#  -1991223.9754789786,
#  -2123614.753362612,
#  -2403187.9612212894,
#  -2930678.1950624487,
#  -3634610.7430675025,
#  -3819387.9092207206,
#  -3939241.0668800026,
#  -3975362.3645221363,
#  -4014885.020774686,
#  -4004018.14282606,
#  -3975239.846438008])
# ss_ge = np.array([-510095.2350578911, #all at 5.49 GHz
#   -692529.354099978,
#   -1118376.4206360157,
#   -1561182.2347758287,
#   -1857753.2963644885,
#   -1981599.1450706143,
#   -2126939.5026417505,
#   -2408171.0758959274,
#   -2929414.1820523785,
#   -3500735.742550359,
#   -3817771.5451570465,])
ss_ge = np.array([.513,.711,1.160,1.712,2.079,2.152,2.238,2.55,3.228,4.223,4.662,5.26])
FT1 = np.array([1.039,.942,.700,.551,.430,.345,.286,.224,.266,.245,.234,.244])

# powers = np.array([-12.8,-11.55,-9.5,-7.88,-6.37,-5.42,-4])
powers = np.array([-12.8,-11.55,-9.5,-7.88,-6.37,-5.42,-4,-3.32,-3,-2.87,-2.72,1])
# powers = np.array([-10.7,-9.71,-8.05,-6.71,-5.46,-4.6,-3.52,-3,-2.64,-2.48,-2.36,-2.29,-2.23])

powers_lin = 10**(powers/10)

plt.figure()
plt.title('change in starkshift')
plt.ylabel('stark shift')
plt.xlabel('power')

plt.plot(powers_lin,ss_ge)


# plt.figure()
# plt.title('change in FT1')
# plt.ylabel('1/FT1 microseconds')
# plt.xlabel('power^2')
# plt.plot(powers_lin,1/FT1)
# powers_FT1 = np.array([-100,-25.8,-11.4,-6,-3.1,-1.211,-.28,.4,.8,.98])

# powers_lin_FT1 = 10**(powers_FT1/10)

def Stark_model(powers, coeffs):
    return coeffs[0]*powers

def residuals(coeffs, y, powers):
    return y-Stark_model(powers, coeffs)

# fe_fit = np.polyfit(powers_lin, ss_fe, 1)
# fe_fit_data = fe_fit[0]*powers_lin + fe_fit[1]

# ge_fit = np.polyfit(powers_lin, ss_ge, 1)
# ge_fit_data = ge_fit[0]*powers_lin + ge_fit[1]

FT1_fit = np.polyfit(powers_lin, 1/FT1, 1)
FT1_fit_data = FT1_fit[0]*powers_lin + FT1_fit[1]

init_guess = [3]

# fe, flag_fe = leastsq(residuals, init_guess, args = (ss_fe,powers_lin))
# fe_fit_data = fe[0]*powers_lin

ge, flag_ge = leastsq(residuals, init_guess, args = (ss_ge[0:4],powers_lin[0:4]))
ge_fit_data = ge[0]*powers_lin



plt.figure()
plt.title('change in starkshift')
plt.ylabel('stark shift')
plt.xlabel('power')
# plt.plot(powers_lin,ss_fe,label = 'fe')
# plt.plot(powers_lin,fe_fit_data ,'--',label = 'fe fit')
plt.plot(powers_lin,ge_fit_data ,'--',label = 'ge fit')
plt.plot(powers_lin,ss_ge,label = 'ge')
plt.legend()

plt.figure()
plt.title('change in FT1')
plt.ylabel('1/FT1 microseconds')
plt.xlabel('power')
plt.plot(powers_lin,1/FT1, label = 'data')
plt.plot(powers_lin,FT1_fit_data,'--', label = 'fit')
plt.legend()

def FWM_stark_chi(powers):
    return .5*(.8*ge[0])**.5*powers**.5

def FWM_raman(powers):
    return .315*(FT1_fit[0]*powers)**.5

plt.figure()
plt.title('fwm drive strength')
plt.ylabel('fwm drive strength')
plt.xlabel('amplitude')
plt.plot(powers_lin**.5, FWM_stark_chi(powers_lin),label = 'Stark Chi')
plt.plot(powers_lin[0:len(FT1)]**.5, FWM_raman(powers_lin[0:len(FT1)]),label = 'raman')
plt.legend()



plt.figure()
x = 0.5*(0.8 * ss_ge)**0.5
y = 0.325*(1/FT1-0.5)**0.5
plt.scatter( x,y)
#def linear_fit(x, k):
#    return k*x
#sigma = np.ones(len(x))
#popt, pcov = curve_fit(linear_fit, x, y, p0=500, sigma=sigma)
#plt.plot(x, linear_fit(x, popt[0]), label ="$f(x)=k*x | k=%.3f" % (popt[0]) )
#plt.plot(np.linspace(0,1,11),np.linspace(0,1,11),'--',label='y = x')
plt.plot(np.linspace(0,1,11),0.66*np.linspace(0,1,11),'--',label='y = 0.66x')
plt.xlabel('Model 1 fwm strength prediction(MHz)')
plt.ylabel('Model 2 fwm strength measurement(MHz)')
plt.legend()






