# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 19:06:08 2021

@author: WangLab
"""

datas = np.loadtxt(r'C:\Users\WangLab\Documents\circulator results\2021-03-11 16-09-18\\0to0.05colorplot_Z.txt')

datas_p = datas[:len(datas)/2] + 1j * datas[len(datas)/2:]
datas_p_plot = np.transpose(datas_p)  



              
plt.figure()
plt.title('Experiment S31')
plt.xlabel('Fields(T)')
plt.ylabel('Frequency(GHz)')
fields = np.linspace(0,0.05,26)
freqs = np.linspace(10.75,10.85,1601)
fieldsplot, freqsplot = np.meshgrid(fields,freqs)
plt.pcolormesh(fieldsplot,freqsplot,20*np.log10(np.abs(datas_p_plot)), vmax = -10, vmin = -50)
plt.colorbar().set_label('(dB)')
plt.show()               