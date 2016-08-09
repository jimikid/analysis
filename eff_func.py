"""
Created on 08/05/2016, @author: sbaek
    - initial release

"""
from collections import OrderedDict
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from numpy.random import uniform, seed
from matplotlib.mlab import griddata
import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class eff:
    def __init__(self, file_name, para= None, data_path = None):
        '''
        - 'file_name', 'data_path' have to exist
        - sort_index() can be used with 'file_name' and 'data_path'

        :param file_name:
        :param para:
        :param data_path:  'data_path' can be in 'para' or can be put seperately
        '''

        print '\n Start at %s ' % time.strftime("%d/%m/%Y %I:%M")
        self.par=para
        self.filename=file_name
        if data_path == None:
            self.path = para['data_path']
        else : self.path = data_path

        print ' read : %s' %self.path + file_name + '.csv'
        self.df = pd.read_csv(self.path + file_name + '.csv')
        self.sorted_data=self.sort_index()

    def plot_eff(self, marker="o", limit=None, figsize=(5, 7), xlim=(26, 46), ylim=(94.0, 97.0), markersize=6, add_labels=True, title=None):
        self.load = self.sorted_data.keys()

        self.p_rated = ''
        self.ac_mode = ''
        try:
            self.p_rated = self.par['p_rated']
            self.ac_mode = self.par['ac_mode']
        except:pass


        fig = plt.figure(1, figsize=figsize)
        ax1 = fig.add_subplot(111)
        plots, labels=[], []
        for key in self.load:
            l1,=ax1.plot(self.sorted_data[key].volt_in, self.sorted_data[key].eff, marker=marker, markersize=markersize)
            plots.append(l1)
            if add_labels:
                labels.append('Eff. load %s%%' % key)
            else:pass

        ax1.legend(plots, labels)
        ax1.set_xlim(xlim)
        ax1.set_ylim(ylim)
        if limit is not None:
            ax1.set_xlim(limit[0])
            ax1.set_ylim(limit[1])

        ax1.set_xlabel('Vdc[V]')
        ax1.set_ylabel('Eff.[%]')
        ax1.grid()
        if title is None:
            plt.title('P_rated= %sW, %s' %(self.p_rated, self.ac_mode))
        else : plt.title(title)

        name=self.path+'fig_%s.png' %(self.filename)
        print ' save : %s \n' %name
        plt.savefig(name)
        plt.close()


    def plot_map(self, figsize=(5,7), xlim=(26, 46), ylim=(140, 300)):
        df = self.df
        p_ac_out = df['p_ac_out']
        eff = df['eff']

        plt.figure(1, figsize=figsize)
        # volt_in = df['volt_in']
        # volt_in = df['Vdc'] # there are cases fail to boot up
        volt_in = df['volt_in']
        fault_ = df['fault']

        seed(0)
        x, y, z = volt_in, p_ac_out, eff

        # define grid.
        xi = np.linspace(26, 46, 100)
        yi = np.linspace(130, 300, 100)
        # grid the data.
        zi = griddata(x, y, z, xi, yi, interp='linear')
        # contour the gridded data, plotting dots at the nonuniform data points.
        CS = plt.contour(xi, yi, zi, 10, linewidths=0.1, colors='k')
        CS = plt.contourf(xi, yi, zi, 10, cmap=plt.cm.rainbow, vmax=zi.max(), vmin=zi.min(), alpha=0.3)

        plt.colorbar()
        plt.scatter(x, y, marker='o', c='b', s=30, zorder=20, alpha=0.9)

        ''' fault check - add red dots'''
        for j in range(len(fault_)):
            if fault_[j] == True:
                plt.scatter(x[j - 1], y[j - 1] + 3, marker='o', c='r', s=60, zorder=20, alpha=1)

        plt.xlim(xlim)
        plt.ylim(ylim)
        plt.title("Eff. [%]")
        plt.xlabel('Vdc [V]')
        plt.ylabel('P_ac_out [W]')
        name = self.path + '/Eff_Sat_' + self.filename + '.png'
        print ' save : %s \n' % name
        plt.savefig(name)
        plt.close()


    def plot_3d(self, fig_num=1, vlim='auto',  zlim='auto', ylim='auto', xlim='auto', label='auto', title='auto', linewidth=0.1):
        fig=plt.figure(fig_num)
        ax = fig.gca(projection='3d')
        ax.plot_trisurf(self.df['volt_in'], self.df['p_ac_out'], self.df['eff'], cmap=cm.jet)
        if vlim=='auto':
            ax.plot_trisurf(self.df['volt_in'], self.df['p_ac_out'], self.df['eff'], cmap=cm.jet, linewidth=linewidth)
        else:
            ax.plot_trisurf(self.df['volt_in'], self.df['p_ac_out'], self.df['eff'], cmap=cm.jet, vmin=vlim[0], vmax=vlim[1], linewidth=linewidth)

        if not(label=='auto'):
            fontsize=12
            ax.set_xlabel(label[0], fontsize=fontsize)
            ax.set_ylabel(label[1], fontsize=fontsize)
            ax.set_zlabel(label[2], fontsize=fontsize)

        if not(zlim=='auto'): ax.set_zlim(zlim[0], zlim[1])
        if not(ylim=='auto'): ax.set_ylim(ylim[0], ylim[1])
        if not(xlim=='auto'): ax.set_xlim(xlim[0], xlim[1])
        if not(title=='auto'): ax.set_title(title)

        name = self.path+'fig_3d_%s.png' %(self.filename)
        print ' save : %s \n' % name
        plt.savefig(name)
        plt.close()


    def sort_load(self, ref_index=0):
        df1=self.df[ref_index:ref_index+1]
        for i in range(len(self.df)):
            if not (i == ref_index):
                if (int(self.df ['load'][i]>int(self.df ['load'][ref_index])-5) and
                    int(self.df ['load'][i]<int(self.df ['load'][ref_index])+5)):
                    df1=pd.concat([df1,self.df [i:i+1]])
        label=str(int(round(sum(df1['load'])/len(df1['load']))))  #return string of load[%]
        return df1, label


    def sort(self, index):
        values=dict()
        for i in index:
            data, Load=self.sort_load(self.df , ref_index=i)
            data=data.set_index([range(len(data))])
            values[Load]=data
            print 'index : %s, Load : %s%%' %(i, Load)
        return values

    def sort_index(self):
        '''
        :param df:
        :return: values, OrdereredDict(), e.g. {'load' : [values]...}
        '''
        values=OrderedDict()
        index=[]  # find index, index is Load condition in integer in list
        for i in self.df ['load']:
            if int(i) in index: pass
            elif int(i)+1 in index: pass
            elif int(i)-1 in index: pass
            else:index.append(int(round(i)))

        for i in range(len(index)):
            data, Load=self.sort_load(ref_index=i)
            data=data.set_index([range(len(data))])
            values[Load]=data
            print 'index : %s, Load : %s%%' %(i, Load)
            #print values
        return values
