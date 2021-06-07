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
plt.ylabel('