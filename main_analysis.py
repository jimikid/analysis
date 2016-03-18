"""
Created on 03/18/2016, @author: sbaek
  V00
    - initial release
"""


from __future__ import division 
from math import *
import win32com.client 
global ProjectName,  DesignName

def main(it, names):    
    ProjectName=names[0]
    DesignName=names[1]
    
    oAnsoftApp = win32com.client.Dispatch("AnsoftMaxwell.MaxwellScriptInterface")
    oDesktop = oAnsoftApp.GetAppDesktop()
    oDesktop.RestoreWindow()
    
    #oDesktop.OpenProject('C:/Users/sbaek/Documents/Ansoft/'+ProjectName+'.mxwl')
    oProject = oDesktop.SetActiveProject(ProjectName)
    oDesign = oProject.SetActiveDesign(DesignName)

    #oDesign.AnalyzeAll()

    oModule = oDesign.GetModule("Optimetrics")  #for parametric sweep
    oModule.SolveSetup("ParametricSetup1")      #for parametric sweep
    
    oProject.Save()
    oProject.close()

   
if __name__ == '__main__':
    names=[['Cu7oz_Rac_pri', 'Xfmr'], ['Cu7oz_Rac_sec', 'Xfmr']]
    for it in range(len(names)):
        main(it, names[it])

