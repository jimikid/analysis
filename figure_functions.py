"""
Created on 02/24/2016, @author: sbaek
    - initial release

    V01 : 03/25/2016
     - def soft_index()

    V02 : 04/15/2016
     - values=OrderedDict().  dict() format change the orders and color codes on plots are not consistent. 

    V03 : 06/01/2016
     - plot() and plot_bar() are added

"""
from collections import OrderedDict
from os import makedirs
from os.path import dirname, exists

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm


def plot(data=[], label=None, limit=None, fig_num=1, title='', marker='o-',
         grid=True, save=True, combine=False, hold=False,
         xtick=None, xtick_label=None ,ytick=None, ytick_label=None,
         legend=None, figsize=(8, 8), scale=''):
    '''
    :param data: [ ([x1 values],[y1 values]), ([x2 values],[y2 values]) ..]
    :param label: [ (x1 label, y1 label), (x2 label, y2 label) ..] , if there is one set given, it is duplicated
    :param limit: [ (x1 label, y1 label), (x2 label, y2 label) ..]
    :param fig_num:
    :param title: ''
    :param marker:
    :param grid: Bool
    :param save: Bool
    :param combine: Bool  #plot datasets on one plot
    :param hold: Bool
    :param legend: []  # list of str names for multiple datasets on one plot
    :param figsize:
    :return:
    '''

    print '\n figure %s' % fig_num
    fig = plt.figure(fig_num, figsize=figsize)

    sp = len(data)

    cnt = 1
    for i in data:
        subplot = 100 * sp + 10 + cnt  #
        if combine: subplot = 111
        figure = fig.add_subplot(subplot)

        if grid: figure.grid(grid)

        if legend is not None:
            print ' plot %s' % legend[cnt - 1]
            figure.plot(i[0], i[1], marker, label=legend[cnt - 1])
            figure.legend(loc='upper left')  # need to set the location.  label is given in plot()

        if scale is 'log': figure.set_xscale("log")
        if scale is 'loglog':
            figure.set_xscale("log")
            figure.set_yscale("log")

        if label is not None:
            if len(label)==1:xlabel, ylabel = label[0][0], label[0][1]  #if one set is given duplicated
            else:xlabel, ylabel = label[cnt - 1][0], label[cnt - 1][1]

            plt.xlabel(xlabel)
            plt.ylabel(ylabel)

        if limit is not None:
            xlimit, ylimit = limit[cnt - 1][0], limit[cnt - 1][1]
            plt.xlim(xlimit)
            plt.ylim(ylimit)

        #plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

        if xtick is not None:plt.xticks(xtick, xtick_label)
        if ytick is not None: plt.yticks(ytick, ytick_label)

        print ' ...%s' % cnt
        if cnt == 1:
            plt.title(title)  # this has to be at the end. set title once on the top
        else: pass
        cnt = cnt + 1


    if hold: plt.show()  # show()hold plot.  cannot close.
    if save:
        if title is '': fig_name = 'fig%s.png' %('_'+scale)
        else: fig_name = title + '%s.png' %('_'+scale)
        fig.savefig(fig_name)
        print ' save %s \n' % (fig_name)
        plt.close(fig)
    else:pass

    return fig


def plot_bar(df, xticks, title='', save=True):
    '''
    - value referred to df.index.
    - file format
              flux_Sec_In_110_Bavg  flux_Sec_Out_110_Bavg
path_02_B []              0.442064               0.176952
path_04_B []              0.103560               0.256245

    :param df: list
    :param xticks: list
    :param title:
    :param save:
    :return:
    '''

    for i in df.keys():  # iteration at the number of keys
        labels=df.index.tolist()
        y_pos = np.arange(len(labels))
        plt.barh(y_pos, df[i], align='center', alpha=0.5)
        xticks = xticks
        plt.xticks(xticks)
        plt.yticks(y_pos, labels)
        plt.xlabel(title)
        # plt.title('')
    plt.show()

    if save:
        if not title:
            title = 'fig_bar'
        fig_name = title + '.png'
        plt.savefig(fig_name)
        print ' save %s' % (fig_name)
        plt.close()



def create_mapplot(data=[], fig_num=1, vlim='auto',  zlim='auto', ylim='auto', xlim='auto', label='auto', title='auto', linewidth=0.1):

    fig=plt.figure(fig_num)
    ax = fig.gca(projection='3d')    
    ax.plot_trisurf(data[0], data[1], data[2], cmap=cm.jet)

    if vlim=='auto':
        ax.plot_trisurf(data[0], data[1], data[2], cmap=cm.jet, linewidth=linewidth)
    else:
        ax.plot_trisurf(data[0], data[1], data[2], cmap=cm.jet, vmin=vlim[0], vmax=vlim[1], linewidth=linewidth)
    
    if not(label=='auto'):
        fontsize=12
        ax.set_xlabel(label[0], fontsize=fontsize)
        ax.set_ylabel(label[1], fontsize=fontsize)
        ax.set_zlabel(label[2], fontsize=fontsize)
    
    if not(zlim=='auto'): ax.set_zlim(zlim[0], zlim[1])
    if not(ylim=='auto'): ax.set_ylim(ylim[0], ylim[1])
    if not(xlim=='auto'): ax.set_xlim(xlim[0], xlim[1])
    if not(title=='auto'): ax.set_title(title)
    plt.show()

def create_2plot_2yaxis(data1=[], data2=[], data3=[], data4=[], label1=['x','y1','y2'], label2=['x','y1','y2'], marker='-'):
    '''
    creat plots  with secondary y axis. Only work with 2 data   
    num : figure number,
    plot is adjusted with max and min values with scale
    '''
#    f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
    f, ax1 = plt.subplots(2)
    
    ax1[0].plot(data1[0][0], data1[0][1], 'b'+marker)
    ax1[0].plot(data1[0][0], data1[0][1], 'b'+marker)
    ax1[0].set_xlabel(label1[0])
    ax1[0].ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    # Make the y-axis label and tick labels match the line color.
    ax1[0].set_ylabel(label1[1], color='b')
    
    ymin, ymax=plot_range(data1[0][1]) 
    ax1[0].set_ylim((ymin, ymax))
    
    ax2 = ax1[0].twinx()
    ax2.plot(data2[0][0], data2[0][1], 'g'+marker)  
    ax2.set_ylabel(label1[2], color='g')    
    ax2.ticklabel_format(style='sci', axis='y', scilimits=(0,0)) 
    
    ymin, ymax=plot_range(data2[0][1]) 
    ax2.set_ylim((ymin, ymax))   
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    plt.grid()  
  
    ax1[1].plot(data3[0][0], data3[0][1], 'b'+marker)
    ax1[1].plot(data3[0][0], data3[0][1], 'b'+marker)
    ax1[1].set_xlabel(label2[0])
    ax1[1].ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    # Make the y-axis label and tick labels match the line color.
    ax1[1].set_ylabel(label2[1], color='b')
    
    ymin, ymax=plot_range(data3[0][1]) 
    ax1[1].set_ylim((ymin, ymax))
    
    ax2 = ax1[1].twinx()
    ax2.plot(data4[0][0], data4[0][1], 'g'+marker)  
    ax2.set_ylabel(label2[2], color='g')
    ax2.ticklabel_format(style='sci', axis='y', scilimits=(0,0))    

    ymin, ymax=plot_range(data4[0][1]) 
    ax2.set_ylim((ymin, ymax))
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    plt.grid()   


def create_2yaxis(data1=[], data2=[], fig_num=1, label=['x','y1','y2'], marker='-'):
    '''
    creat plots  with secondary y axis. Only work with 2 data
    num : figure number,
    plot is adjusted with max and min values with scale
    '''

    #fig, ax1 = plt.subplots(fig_num)
    fig, ax1 = plt.subplots(fig_num)

    ax1.plot(data1[0][0], data1[0][1], 'b'+marker)
    ax1.set_xlabel(label[0])
    ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    # Make the y-axis label and tick labels match the line color.
    ax1.set_ylabel(label[1], color='b')


    ax2 = ax1.twinx()
    ax2.plot(data2[0][0], data2[0][1], 'g'+marker)
    ax2.set_ylabel(label[2], color='g')
    ax2.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

    plt.grid()

   
def create_path_dir(name='data', path = dirname(__file__)):
    '''
    creat a folder to save data under the present folder if it does not exist.
    and return the path in string form
    '''
    # the variables in definition are default, example          
    if not exists(path+'/'+name):
        print 'make dir'
        makedirs(path+'/'+name)
    newpath=path+'/'+name
    return newpath  
  


def search_csv(filename, dataset_path=''):    
    file_index = []
    #find out existing files and save index ti fuke_index,  check up to 500, 
    for i in range(10):
        if exists(dataset_path+filename+'000%s.csv' %i):
            file_index.append(i)    
    for i in range(10, 100):
        if exists(dataset_path+filename+'00%s.csv' %i):
            file_index.append(i)   

    for i in range(10):
        if exists(dataset_path+filename+'00%s.csv' %i):
            file_index.append(i)    
    for i in range(10, 100):
        if exists(dataset_path+filename+'0%s.csv' %i):
            file_index.append(i)   

    for i in range(10):
        if exists(dataset_path+filename+'0%s.csv' %i):
            file_index.append(i)                
    for i in range(10, 100):
        if exists(dataset_path+filename+'%s.csv' %i):
            file_index.append(i)   

    for i in range(10):
        if exists(dataset_path+filename+'%s.csv' %i):
            file_index.append(i)    
            
    return file_index 


def sort_load(df, ref_index=0):
    df1=df[ref_index:ref_index+1]
    for i in range(len(df)):
        if not (i == ref_index):
            if (int(df['load'][i]>int(df['load'][ref_index])-5) and
                int(df['load'][i]<int(df['load'][ref_index])+5)):
                df1=pd.concat([df1,df[i:i+1]])
    label=str(int(round(sum(df1['load'])/len(df1['load']))))  #return string of load[%]
    return df1, label


def sort(df, index):
    values=dict()
    for i in index:
        data, Load=sort_load(df, ref_index=i)
        data=data.set_index([range(len(data))]) 
        values[Load]=data
        print 'index : %s, Load : %s%%' %(i, Load)
    return values


def sort_index(df):
    values=OrderedDict()

    index=[]  # find index, index is Load condition in integer in list
    for i in df['load']:
        if int(i) in index: pass
        elif int(i)+1 in index: pass
        elif int(i)-1 in index: pass
        else:index.append(int(round(i)))

    for i in range(len(index)):
        data, Load=sort_load(df, ref_index=i)
        data=data.set_index([range(len(data))])
        values[Load]=data
        print 'index : %s, Load : %s%%' %(i, Load)
    return values
