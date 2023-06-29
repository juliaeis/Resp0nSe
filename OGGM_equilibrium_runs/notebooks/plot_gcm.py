import os
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
from matplotlib.legend_handler import HandlerLineCollection,HandlerBase

from cycler import cycler


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
mpl.rcParams["figure.figsize"] = (15,10)



rgi_name={'01':'Alaska','02':'Western Canada & U.S.','03':'Arctic Canada (North)',
             '04':'Arctic Canada (South)','05':'Greenland','06':'Iceland', '07':'Svalbard',
              '08':'Scandinavia', '09':'Russian Arctic', '10':'North Asia', '11':'Central Europe','12':'Caucasus',
             '13':'Central Asia','14':'South Asia (West)','15':'South Asia (East)',
             '16': 'Low Latitudes', '17':'Southern Andes', '18':'New Zealand'}

def color_to_cmap(color):
    l = [(colors.to_rgba('#'+color,i)) for i in np.linspace(0.2,1,10)]
    cmap = colors.ListedColormap(l)
    return cmap

def create_gcm_cmap(n=13):
    color_list=[colors.to_rgb('#'+c) for c in ["001219","003946","005f73","0a9396","4fb3aa","94d2bd","e9d8a6","ecba53","ee9b00","dc8101","bb3e03","8d210c","5e0314"]]
    gcm_cmap=mpl.colors.ListedColormap(color_list).resampled(n)
    colors_k =np.vstack((gcm_cmap.colors, [0,0,0,1]))
    gcm_cmap=mpl.colors.ListedColormap(colors_k)
    return gcm_cmap

def create_color_cycler(lw, n=13):
    custom_cycler = (cycler(color=create_gcm_cmap(n).colors)+ cycler(ls=(n)*['-']+[':'])+cycler(lw=(n)*[lw]+[lw+1]))
    return custom_cycler


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

class HandlerColorLineCollection(HandlerLineCollection):
    def create_artists(self, legend, artist, xdescent, ydescent,
                       width, height, fontsize, trans):
        x = np.linspace(0, width, self.get_numpoints(legend) + 1)
        y = np.zeros(
            self.get_numpoints(legend) + 1) + height / 2. - ydescent
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        lc = LineCollection(segments, cmap=artist.cmap,
                            transform=trans)
        lc.set_array(x)
        lc.set_linewidth(artist.get_linewidth())
        return [lc]


def plot_donut(df, region, df2=None, ax=None, cmap=mpl.cm.viridis, p=71.3,startangle=174.75,**kwargs):
    if ax is None:
        ax = plt.gca() 
    data = df.loc[region]   
    
    # create figure border
    radius = 0.7+(0.3*len(cmap.colors))
    circle = plt.Circle(xy=(0, 0), radius=radius, lw=3,facecolor='white', edgecolor='k', zorder=0)
    ax.add_artist(circle)
    ax.pie([100-p,p], radius=radius+0.15, startangle=startangle, colors=['white',mpl.colors.to_rgba('k', alpha=0)])
    
    # create donut plots
    startingRadius = 0.7 + (0.3* (len(data)-1))
    
    for i,gcm in enumerate(data.drop('CRU').index):
        
        if isinstance(df2, pd.DataFrame):
            data2 = df2.loc[region]
            remain = 100-data.loc[gcm]-data2.loc[gcm]
            if remain<0:
                remain=int(remain)
            ax.pie([100], radius=startingRadius, startangle=90, colors=['white'],
                    wedgeprops={"edgecolor": "white", 'linewidth': 1})
            ax.pie([remain,data2.loc[gcm],data.loc[gcm]], radius=startingRadius, startangle=90, 
                   colors=['white',mpl.colors.to_rgba(cmap(i), alpha=0.3),cmap(i),], wedgeprops={"edgecolor": "white", 'linewidth': 1})
        else:
            ax.pie([100-data.loc[gcm],data.loc[gcm]], radius=startingRadius, startangle=90, 
                   colors=['white',cmap(i),], wedgeprops={"edgecolor": "white", 'linewidth': 1})
        startingRadius-=0.3

    # add CRU
    if isinstance(df2, pd.DataFrame):
        remain=100-data.loc['CRU']-data2.loc['CRU']
        if remain<0:
                remain=int(remain)
        ax.pie([remain, data2.loc['CRU'], data.loc['CRU']], radius=startingRadius, startangle=90, 
               colors=['white','grey', 'k'], wedgeprops={"edgecolor": "w", 'linewidth': 1}) 
    else:
        ax.pie([100-data.loc['CRU'],data.loc['CRU']], radius=startingRadius, startangle=90, colors=['white', 'k'],
                    wedgeprops={"edgecolor": "w", 'linewidth': 1})    
    # add white gaps in CRU donut
    for angel in range(5,365,15):
        ax.pie([97.5,1.25], radius=startingRadius, startangle=angel, colors=[mpl.colors.to_rgba('white', alpha=0), mpl.colors.to_rgba('white', alpha=1)],wedgeprops={"edgecolor": "w", 'linewidth': 0.5} )

    startingRadius-=0.3
    # equal ensures pie chart is drawn as a circle (equal aspect ratio)
    ax.axis('equal')
    ax.set_title('')

    # create circle and place onto pie chart
    circle = plt.Circle(xy=(0, 0), radius=0.45, facecolor='white')
    ax.add_artist(circle)
    return ax

def plot_volume_km3(ds, region, itmix_df=None, itmix_df2=None, n=None, ax=None, add_legend=True,lw=2):
    
    if ax==None:
        ax = plt.gca()
    ax.set_prop_cycle(create_color_cycler(lw, n=len(ds.gcm.values)-1))

    # plot gcms covering the whole time period
    ds.sel(region=region).plot(hue='gcm',ax=ax, add_legend=False)
    
    # plot mean
    ds.sel(region=region).drop_sel(gcm='CRU').mean(dim='gcm').plot(c='k',lw=lw+1,ax=ax)
    
    if region=='global':
        title='Global, n='+str(n)
        fontsize=30
        titleloc='center'
        ax.ticklabel_format(axis='y',style='sci',scilimits=(3,3))
    else:
        title=region+': '+rgi_name[region]
        fontsize=15
        titleloc='left'
        
    if isinstance(itmix_df, pd.DataFrame):
        #adds the donut pie charts
        if len(itmix_df.columns)>10:
            ax_i = ax.inset_axes((0.7,0.7,.55,.55))
            p=71.3
            startangle=174.75
        else:
            ax_i = ax.inset_axes((0.75,0.75,.45,.45))
            startangle=173.5
            p=70.4
        plot_donut(itmix_df, region, itmix_df2, ax=ax_i, cmap=create_gcm_cmap(n=len(ds.gcm.values)-1),startangle=startangle, p=p)
        
        ax.set_title('')
        ax.set_title(title, y=1.0, loc=titleloc,pad=10)
        bbox_to_anchor=(1,0.75)
    else:
        bbox_to_anchor=(1,1.01)
        ax.set_title(title, fontsize=fontsize-1);
    
    ax.set_ylabel(r'Glacier equilibrium volume (km$^3$)')
    ax.set_xlim(1865,2020)
    ax.set_xlabel('Time (years)');
    
    
    if add_legend:
      
        show_legend(np.insert(ds.gcm.values.astype('U16'), -1,'multimodel mean'),cmap=create_gcm_cmap(len(ds.gcm.values)-1), ax=ax, bbox_to_anchor=bbox_to_anchor)
    return ax

def plot_mass_loss_sle(ds, region, itmix_df=None, itmix_df2=None, n=None, ax=None, add_legend=True,lw=2): 
    
    if ax==None:
        ax = plt.gca()
    ax.set_prop_cycle(create_color_cycler(lw, n=len(ds.gcm.values)-1))
    
    ds.drop_sel(gcm='CRU').sel(region=region).plot(hue='gcm',add_legend=False, zorder=8)
    ds.sel(gcm='CRU', region=region).plot(add_legend=False, zorder=9)
    ds.drop_sel(gcm='CRU').sel(region=region).mean(dim='gcm').plot(color='k',lw=3,add_legend=False, zorder=10)
    '''
    if isinstance(itmix_df, pd.DataFrame):
      
        if region=='global':
            ax_i = ax.inset_axes((0.83,0.7,.5,.5))
            plot_donut(itmix_df, region, itmix_df2, ax=ax_i,cmap=create_gcm_cmap(), p=81.3, startangle=168)
        else:
            ax_i = ax.inset_axes((0.875,0.8,.45,.45))
            plot_donut(itmix_df, region, itmix_df2, ax=ax_i,cmap=create_gcm_cmap(), p=88, startangle=188)
        '''
    
    if region=='global':
        title='Global, n='+str(n)
        fontsize=30
        titleloc='center'
        #ax.ticklabel_format(axis='y',style='sci',scilimits=(3,3))
    else:
        title=region+': '+rgi_name[region]
        fontsize=15
        titleloc='left'
        
    if isinstance(itmix_df, pd.DataFrame):
        #adds the donut pie charts
        if len(itmix_df.columns)>10:
            ax_i = ax.inset_axes((0.7,0.7,.55,.55))
            p=71.3
            startangle=174.75
        else:
            ax_i = ax.inset_axes((0.83,0.75,.45,.45))
            startangle=173.5
            if region=='global':
                p=80
            else:
                p=79
        plot_donut(itmix_df, region, itmix_df2, ax=ax_i, cmap=create_gcm_cmap(n=len(ds.gcm.values)-1),startangle=startangle, p=p)
        
        ax.set_title('')
        ax.set_title(title, y=1.0, loc=titleloc,pad=10)
        bbox_to_anchor=(1,0.75)
        
    xlim=ax.get_xlim()
    ax.hlines(y=0,xmin=1850,xmax=2030, zorder=0, color='lightgrey',lw=2)
    ax.set_xlim(xlim)
    ax.set_xlabel('Time (years)')
    ax.set_ylabel('Cummulative ice mass loss (mm SLE)')
    
    if region=='global':
        title='Global, n='+str(n)
        fontsize=30
        titleloc='center'
    else:
        title=region+': '+rgi_name[region]
        fontsize=15
        titleloc='left'
    ax.set_title('')
    ax.set_title(title, y=1.0, loc=titleloc,pad=10)
    
    if add_legend:
        show_legend(np.insert(ds.gcm.values.astype('U16'), -1,r'multimodel mean'),cmap=create_gcm_cmap(len(ds.gcm.values)-1), ax=ax, bbox_to_anchor=(1,0.73));
    return ax

def plot_regional_volume_km3(ds, n=None, lw=2):
    
    fig = plt.figure(figsize=(25,15))
    fig.patch.set_facecolor('white')
    grid = plt.GridSpec(5,6, hspace=0.5, wspace=0.5,left=0.05,right=0.85,top=0.95,bottom=0.05)
    grid2 = plt.GridSpec(20,24, hspace=1, wspace=0.5,left=0.05,right=0.85,top=0.95,bottom=0.05)

    ax0 = fig.add_subplot(grid2[5:15,5:20])
    plot_volume_km3(ds,'global', n=n, ax=ax0, add_legend=False, lw=lw+1)

    for i,grid_index in enumerate([0,1,2,3,4,5,11,17,23,29,28,27,26,25,24,18,12,6]):
        reg = str(i+1).zfill(2)
        ax = fig.add_subplot(grid[grid_index])
        plot_volume_km3(ds,reg, ax=ax, add_legend=False, lw=lw)

        #ax.set_title('region '+reg,size=18)
        ax.tick_params(axis='both', which='major', labelsize=15)
        ax.yaxis.set_major_locator(MaxNLocator(3))
        if 8<i<15:
            ax.set_xlabel('Time (years)',size=15)
        else:
            ax.set_xlabel('')
        if i==0 or i>13:
            pad=None

            if reg=='17' or reg=='01':
                pad=5
            if reg=='16' or reg=='15' or reg=='18':
                pad=11
            ax.set_ylabel(r'Equilibrium ($km^3$)',size=15,labelpad=pad)
        else:
            ax.set_ylabel('')

    #legend
    show_legend(np.insert(ds.gcm.values.astype('U16'), -1,r'multimodel mean'),cmap=create_gcm_cmap(len(ds.gcm.values)-1), ax=ax0, bbox_to_anchor=(1.55,1.6), lw=lw);

    plt.savefig(os.path.join('out','run_CMIP6_geod','plots','regional_simple_volume_km3.png'),dpi=300)

def plot_regional_volume_km3_donut(ds, itmix_df, itmix_df2=None):
    
    fig = plt.figure(figsize=(40,60))
    fig.patch.set_facecolor('white')
    grid = plt.GridSpec(6,3, hspace=0.4, wspace=0.35,left=0.05,right=0.82,top=0.95,bottom=0.05)
    
    for i,grid_index in enumerate(range(1,19)):
        reg = str(i+1).zfill(2)
        ax = fig.add_subplot(grid[grid_index-1])

        plot_volume_km3(ds, reg, itmix_df=itmix_df,itmix_df2=itmix_df2, ax=ax, add_legend=False, lw=3)

        if reg not in [str(i).zfill(2) for i in range(1,19,3)]:
            ax.set_ylabel('')
        ax.yaxis.set_major_locator(MaxNLocator(3))

        #legend
        ax0 = fig.add_subplot(grid[2])
        ax0, _= show_legend(np.insert(ds.gcm.values.astype('U16'), -1,r'multimodel mean'),cmap=create_gcm_cmap(len(ds.gcm.values)-1), ax=ax0, bbox_to_anchor=(1.875,1.1), fontsize=30, lw=3);
        ax0.set_axis_off()
    plt.savefig(os.path.join('out','run_CMIP6_geod','plots','regional','interpolated','itmix_volume_km3.png'),dpi=300)
    
    
def show_legend(gcm_list, cmap=None, ax=None, bbox_to_anchor=None, fontsize=15, lw=2):
    if cmap==None:
        cmap=create_gcm_cmap(len(gcm_list)-1)
    custom_lines =[Line2D([0], [0], color=cmap(i), lw=lw) for i,gcm in enumerate(gcm_list[:-2])]+[Line2D([0], [0], color='k', lw=lw+1)]+[Line2D([0], [0], color='k',linestyle=':', lw=lw+1)]
    leg = ax.legend(custom_lines, gcm_list,fontsize=fontsize,bbox_to_anchor=bbox_to_anchor)
    leg.set_title('CMIP6 GCMs',prop={'size':fontsize+2});
    return ax, leg
