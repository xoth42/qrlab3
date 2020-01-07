# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 20:19:58 2019

@author: Wang_Lab
"""

#ys = qp.get_ys()


ys = [158.34418562, 158.33147771, 158.21805919, 158.3696851,  160.3682104,
 160.29702039, 158.36520624, 158.13720195, 160.71445303, 160.54310811,
 163.10932349, 162.97109126, 162.7319399,  162.72184294]
ys= np.array(ys)
amp_data =ys.reshape(7,2)
amp =amp_data.transpose().mean(axis=0)

efrabi_no1stpi = amp[5]-amp[2]
efrabi_1stpi = amp[6]-amp[1]

rabi = amp[2]-amp[0]
rabi_after_efpi = amp[5]-amp[3]

