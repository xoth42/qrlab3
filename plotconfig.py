# Some plotting defaults

import matplotlib as mpl

mpl.rcParams['legend.fontsize'] = 9

Nmax = 10

cmap = mpl.cm.get_cmap(name='Spectral')
#mpl.rcParams['axes.color_cycle'] = [cmap(i) for i in np.linspace(0, 1.0, Nmax)]

bwr = [(0.0, 0.0, 0.7), (0.1, 0.1, 1.0), (1.0, 1.0, 1.0), (1.0, 0.1, 0.1), (0.7, 0.0, 0.0)]
pcolor_cmap = mpl.colors.LinearSegmentedColormap.from_list('mymap', bwr, gamma=1)


def general_figure():
    mpl.rcParams['figure.figsize'] = [10,8]
    mpl.rcParams['axes.linewidth'] = 4
    mpl.rcParams['xtick.major.size'] = 5
    mpl.rcParams['ytick.major.size'] = 5
    mpl.rcParams['xtick.minor.size'] = 3
    mpl.rcParams['ytick.minor.size'] = 3
    mpl.rcParams['legend.frameon'] = True
    mpl.rcParams['legend.loc'] = 'best'
    mpl.rcParams['xtick.major.width'] = 3
    mpl.rcParams['ytick.major.width'] = 3
    mpl.rcParams['xtick.minor.width'] = 2
    mpl.rcParams['ytick.minor.width'] = 2
    mpl.rcParams['font.sans-serif'] ='Arial'
    mpl.rcParams['font.size'] = 28
    mpl.rcParams['axes.labelsize']= 28
    mpl.rcParams['legend.fontsize'] = 25
#    mpl.rcParams['axes.labelpad'] = 2

