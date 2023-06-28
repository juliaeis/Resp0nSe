import country_converter as coco

import numpy as np
import matplotlib as mpl
from matplotlib import colors
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.collections import LineCollection
from matplotlib.legend_handler import HandlerLineCollection,HandlerBase

mpl.rcParams['axes.linewidth'] = 3
mpl.rcParams['xtick.major.width'] = 3
mpl.rcParams['ytick.major.width'] = 3
mpl.rcParams['font.size'] =30
mpl.rcParams['font.weight'] = 'medium'
mpl.rcParams['axes.labelweight'] = 'medium'
mpl.rcParams['legend.fontsize'] = 20 #30
mpl.rcParams['lines.linewidth'] = 3
mpl.rcParams['xtick.major.pad']='8'
mpl.rcParams['ytick.major.pad']='8'

def create_color_maps(n_yr, ppm_color=None):
    # each century own color, shading for decadals
    l = []
    
    if ppm_color=='conc':
        color_list = [["546A7B",5],["62929E",10],["C6C5B9",2]]
       
    elif ppm_color=='glacier':
        color_list = [["172527",5],["618E83",10],["C9E4CA",2]]
    else:
         color_list = [["9E2A2B",5],["BF6535",10],["E09F3E",2]]
    print(color_list)    
    for c in color_list:
        l = l+ [(colors.to_rgba('#'+c[0],i)) for i in np.linspace(0.2,1,10)]*c[1]
    # keep n years
    l = l[:n_yr]

    cmap=colors.ListedColormap(l)
    return cmap


def color_to_cmap(color):
    l = [(colors.to_rgba('#'+color,i)) for i in np.linspace(0.2,1,10)]
    cmap = colors.ListedColormap(l)
    return cmap

class HandlerColormap(HandlerBase):
    def __init__(self, cmap, num_stripes=8, **kw):
        HandlerBase.__init__(self, **kw)
        self.cmap = cmap
        self.num_stripes = num_stripes
    def create_artists(self, legend, orig_handle, 
                       xdescent, ydescent, width, height, fontsize, trans):
        stripes = []
        for i in range(self.num_stripes):
            s = Rectangle([xdescent + i * width / self.num_stripes, ydescent], 
                          width / self.num_stripes, 
                          height, 
                          fc=self.cmap((2 * i + 1) / (2 * self.num_stripes)), 
                          transform=trans)
            stripes.append(s)
        return stripes