import numpy as np
import matplotlib.pyplot as pl


folder = r'C:\Users\WangLab\Documents\yingying\strongly_coupled_DITOM'
S11_file = np.loadtxt(folder + r'\S11.txt', delimiter = ",")
S21_file = np.loadtxt(folder + r'\S21.txt', delimiter = ",")
S12_file = np.loadtxt(folder + r'\S12.txt', delimiter = ",")
S22_file = np.loadtxt(folder + r'\S22.txt', delimiter = ",")

frequency = S11_file[:,0]
S11_dB = S11_file[:,1]
S21_dB = S21_file[:,1]
S12_dB = S12_file[:,1]
S22_dB = S22_file[:,1]

def to_linear_voltage(Sij_dB):
    Sij = np.zeros(len(Sij_dB))
    for k in range(len(Sij_dB)):
        Sij[k] = 10**(Sij_dB[k]/20)
    return(Sij)
    
S11 = to_linear_voltage(S11_dB)
S21 = to_linear_voltage(S21_dB)
S12 = to_linear_voltage(S12_dB)
S22 = to_linear_voltage(S22_dB)

pl.figure(1)
pl.plot(frequency, S11_dB)
pl.plot(frequency, S21_dB)
pl.figure(2)
pl.plot(frequency,(1 - S22**2-S12**2))
pl.ylabel('Loss')
pl.xlabel('frequency (GHz)')
pl.show()