"""
Created on 02/24/2016, @author: sbaek
  V00
    - initial release
"""

import os
from os.path import abspath, dirname, exists
import csv 
import pandas as pd
from scipy import integrate
import figure_functions as ff
import matplotlib.pyplot as plt

class waveforms:
    """
           __INIT__     
           __STR__      
           
    inputs
            dataset_path=''             - type:str with '\' at the end
            file_name=''                - type:str
  
            
    """    
    
    def __init__(self, para, file_name=''):
        self.par=para
        #self.dataset_path =dataset_path
        self.dataset_path = para['data_path']  # this is required, because we want to use this outside class
        self.file_name=file_name
        self.new_file= ''
        self.return_str=str()
        
        self.data=pd.DataFrame(dict())        
        self.VIrms=dict()
        self.VIavg=dict()
        self.freq=0
        self.mode=int()

    def __str__(self):
        self.return_str= '\n\n Waveforms \n' 
        self.return_str += '\n file_name : %s  ' %self.file_name
        #return_str += '\n save : %s  ' %self.new_file
        return self.return_str  
       
            
    def zero_crossing(self, list1, timestep):  
        skip=round(1e-6/timestep)    
        zero, k = [], 1
        while k < len(list1)-1:        
            for i in range (int(k), len(list1)-1):
                if cmp(list1[i],0)+cmp(list1[i-1], 0)==0 or list1[i]==0:
                    zero.append(i)
                    k=i+skip
                    break
                else: k=i+skip
        return zero
          
    def rms(self, x, y):
        temp1 = [float(y[i])**2 for i in range(len(y))]
        temp2=(integrate.cumtrapz(temp1, x, initial=0))
        a, b = x[len(x)-1], x[0]
        c, d=temp2[len(temp2)-1], temp2[0]
        rms= ((c-d)/(a-b))**0.5
        return rms
    
    def slope(self, x, y):    
        a, b, c, d=y[len(y)-1], y[0], x[len(x)-1], x[0]    
        slope= (a-b)/(c-d)
        return slope  
     
    def conversion(self, mode, data_file, cycle=1):         
        self.mode=mode
        print '\n conversion...  mode %s' %mode
           
        try:
            wave1, wave2=[], []                         
            
            #df=self.read_csv_4digits(mode=mode,file_index=file_index)    
            print '\n read file : %s' %data_file
            df=pd.read_csv(data_file)             
            
            wave1, wave2=[], []            
            for i in range(8):
                wave2.append([])
                wave1.append([])
               
            wave1[0]=df['Time']    
            wave1[1], wave1[2], wave1[3], wave1[4]=df[self.par['ch_names'][0]], df[self.par['ch_names'][1]],df[self.par['ch_names'][2]],df[self.par['ch_names'][3]]
            
            timestep=wave1[0][100]-wave1[0][99]
        
            print '\n find zero-crossing with ch %s ' %(self.par['zero_cross'])
            #zero = self.zero_crossing(wave1[4], timestep) 
            zero = self.zero_crossing(wave1[self.par['zero_cross']], timestep) 
            period = (zero[len(zero)-1]-zero[len(zero)-3])*timestep
            self.freq=1.0/float(period)
            print '\n Freq : %.1f [kHz]' %(self.freq/1000)
            
            cycle=int(cycle)       
            for i in range (zero[len(zero)-cycle*2-1],zero[len(zero)-1]):
                for j in range (1, 5):
                    wave2[j].append(wave1[j][i])
            for i in range (zero[len(zero)-1]-zero[len(zero)-cycle*2-1]):
                wave2[0].append(i*timestep)        
           
            VIrms, VIavg=[], []
            for i in range(1,5):
                result1=self.rms(wave2[0], wave2[i])
                result2=sum(wave2[i])/len(wave2[i])  
                VIrms.append(result1)
                VIavg.append(result2)
            
            self.VIrms={self.par['ch_names'][0]+'_rms':VIrms[0], self.par['ch_names'][1]+'_rms':VIrms[1],
                        self.par['ch_names'][2]+'_rms':VIrms[2], self.par['ch_names'][3]+'_rms':VIrms[3]}
            self.VIavg={self.par['ch_names'][0]+'_avg':VIavg[0] , self.par['ch_names'][1]+'_avg':VIavg[1],
                        self.par['ch_names'][2]+'_avg':VIavg[2] , self.par['ch_names'][3]+'_avg':VIavg[3] }    
               
            t_start, t_end, freq = wave2[0][0], wave2[0][len(wave2[0])-1], self.freq   
             
            self.data=pd.DataFrame({'Time':wave2[0], self.par['ch_names'][0]:wave2[1], self.par['ch_names'][1]:wave2[2],
                                    self.par['ch_names'][2]:wave2[3], self.par['ch_names'][3]:wave2[4]})    
            return self.VIrms, self.VIavg, self.freq               
        except:
            print '\n conversion error..'
            

    def write_file(self, file_name):  
        self.new_file=file_name+str(self.mode)+'.csv'        
        #name=self.dataset_path+self.new_file
        name=self.par['data_path']+self.new_file
        print '\n generate file : %s' %name
        self.data.to_csv(name)   
       
        
    def print_rms(self):  
        print '\n %s = %.2f,  %s = %.2f ' % (self.par['ch_names'][0]+'_rms', self.VIrms[self.par['ch_names'][0]+'_rms'], self.par['ch_names'][1]+'_rms', self.VIrms[self.par['ch_names'][1]+'_rms'])
        print ' %s = %.2f, %s = %.2f ' % (self.par['ch_names'][2]+'_rms', self.VIrms[self.par['ch_names'][2]+'_rms'], self.par['ch_names'][3]+'_rms', self.VIrms[self.par['ch_names'][3]+'_rms'])
     
    def print_avg(self):  
        print '\n %s = %.2f,  %s = %.2f ' % (self.par['ch_names'][0]+'_avg', self.VIavg[self.par['ch_names'][0]+'_avg'], self.par['ch_names'][1]+'_avg', self.VIavg[self.par['ch_names'][1]+'_avg'])
        print ' %s = %.2f, %s = %.2f ' % (self.par['ch_names'][2]+'_avg', self.VIavg[self.par['ch_names'][2]+'_avg'], self.par['ch_names'][3]+'_avg', self.VIavg[self.par['ch_names'][3]+'_avg'])
  
    def print_all(self): 
        self.print_rms()
        self.print_avg()
 
    def plot_ch(self, ch, fig_num=1, ylim=(-10,10), label=['Time[s]',''], marker='-', scale=1):
        legend=[self.par['ch_names'][ch-1]]
        #print ' plot ch %s' %ch
        #xlim=(self.data['Time'][0], self.data['Time'][len(self.data['Time'])-1]) 
        xlim=(self.data['Time'][0], self.data['Time'][0]+6e-06) 
        x1, y1=self.data['Time'], self.data[self.par['ch_names'][ch-1]]
        ff.create_figures(fig_num=fig_num, data=[(x1,y1*scale)], legend=legend, label=label, marker=marker, ylim=ylim, xlim=xlim)

    def plot_save(self, file_name='name'): 
        name=self.par['data_path']+'/'+file_name
        print ' save plot : %s \n' %(file_name+'.png')
        plt.savefig(name)
        plt.close() 
