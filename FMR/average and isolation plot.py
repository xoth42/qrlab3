# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 17:45:02 2020

@author: WangLab
"""


def Average(a, n):
    b = np.zeros(len(a) - n + 1,dtype = complex)
    for i in range(len(b)):
        b[i] = np.average(a[i:i+n])
#        print np.average(a[i:i+n])
        
    return b
naverages  = 10
#datas_p = datas
datas_p1 = np.zeros([len(fields),1601 - naverages + 1],dtype = complex)
for i in range(len(datas_p)):
    datas_p1[i] = Average(datas_p[i], naverages)

#datas_n = datas
datas_n1 = np.zeros([len(fields),1601 - naverages + 1],dtype = complex)
for i in range(len(datas_n)):
    datas_n1[i] = Average(datas_n[i], naverages)

freq1 =  Average(freq, naverages)
pl.figure()
figname = ''
fieldplot = np.concatenate((fields, np.zeros(1) + fields[1]-fields[0] + fields[-1]))
mag_p = 20*np.log10(np.abs(datas_p1))
mag_n = 20*np.log10(np.abs(datas_n1))
Z = np.transpose(mag_p - mag_n)
#X,Y = np.meshgrid(field, freq)
X,Y = np.meshgrid(fieldplot, freq1)
pl.xlim(X.min(), X.max())
pl.pcolormesh(X,Y,Z,vmax = 40, vmin = 0, cmap = 'RdBu')
pl.colorbar()
#pl.title('YIG FMR Spectrum, S11 Measurement')
#pl.xlabel('Magnetic Field(mT)')
pl.ylabel('Frequency(GHz)')

itime = 15
pl.figure()
#pl.plot(freq1, mag_p[itime], label = '-%sT'%(fields[itime]))
#pl.plot(freq1 ,mag_n[itime], label = '%sT'%(fields[itime]))
pl.plot(freq1 ,mag_n[itime] - mag_p[itime], label = '%sT, isolation, average = %s'%(fields[itime],naverages))
pl.legend()