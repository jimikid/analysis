"""
Created on 03/18/2016, @author: sbaek
  V00
    - initial release
"""

import win32com.client 
oAnsoftApp = win32com.client.Dispatch("AnsoftMaxwell.MaxwellScriptInterface")
oDesktop = oAnsoftApp.GetAppDesktop()
    
import sys
from os.path import abspath, dirname, exists
from collections import OrderedDict 
import time
date=time.strftime("%m%d") 

def initiation(init, open='Off'):
    print 'ProjectName : %s, DesignName : %s' %(init['ProjectName'], init['DesignName'])
    if open =='On':
        oDesktop.RestoreWindow()
        print init['save_name']+'.mxwl'
        oDesktop.OpenProject(init['save_name']+'.mxwl')
        oProject = oDesktop.SetActiveProject(init['ProjectName'])
        oDesign = oProject.SetActiveDesign(init['DesignName'])
    else:
        oDesktop.RestoreWindow()
        oProject = oDesktop.SetActiveProject(init['ProjectName'])
        oDesign = oProject.SetActiveDesign(init['DesignName'])
    return oProject, oDesign


def loss(oDesign, Object):
    oModule = oDesign.GetModule("FieldsReporter")
    name=Object+'_loss' 
    oModule.EnterQty("OhmicLoss")
    oModule.EnterVol(Object)
    oModule.CalcOp("Integrate")
    oModule.AddNamedExpression(name, "Fields")
    return name


def volume(oDesign, Object):
    '''
    object : list of the names in Maxwell in string format
    name_list : list of the names in calculator in Maxwell
    '''
    oModule = oDesign.GetModule("FieldsReporter")
    name=Object+'_vol'
    oModule.EnterScalar(1)
    oModule.EnterVol(Object)
    oModule.CalcOp("Integrate")    
    oModule.AddNamedExpression(name, "Fields")    
    return name
          
def unit_loss(oDesign, Object):
    oModule = oDesign.GetModule("FieldsReporter")
    name=Object+'_unit_loss'
    oModule.CopyNamedExprToStack(Object+"_loss")
    oModule.CopyNamedExprToStack(Object+"_vol")
    oModule.CalcOp("/")
    oModule.AddNamedExpression(name, "Fields")  
    return name    

def Rac(oDesign):
    oModule = oDesign.GetModule("FieldsReporter")
    oModule.CopyNamedExprToStack("AllObjects_Loss")
    oModule.CopyNamedExprToStack("winding_s_loss")
    oModule.CalcOp("-")
    oModule.AddNamedExpression("Rac", "Fields")

    
def report(oDesign, item, name="XY Plot 1"):
    oModule = oDesign.GetModule("ReportSetup")
    oModule.CreateReport(name, "Fields", "Rectangular Plot", "Setup1 : LastAdaptive", 
    	[
    		"Domain:="		, "Sweep"
    	], 
    	[
    		"Freq:="		, ["All"],
    		"Phase:="		, ["0deg"],
    	], 
    	[
    		"X Component:="		, "Freq",	#"Y Component:="		, ["Rac"]
            "Y Component:="		, item
    	], [])
     
    #log-log scale
    oModule.ChangeProperty(
    	[
    		"NAME:AllTabs",
    		[
    			"NAME:Scaling",
    			[
    				"NAME:PropServers", 
    				name+":AxisY1"
    			],
    			[
    				"NAME:ChangedProps",
    				[
    					"NAME:Axis Scaling",
    					"Value:="		, "Log"
    				]
    			]
    		],
    		[
    			"NAME:Scaling",
    			[
    				"NAME:PropServers", 
    				name+":AxisX"
    			],
    			[
    				"NAME:ChangedProps",
    				[
    					"NAME:Axis Scaling",
    					"Value:="		, "Log"
    				]
    			]
    		]
    	])


    
def main(ProjectName, DesignName):
    init['ProjectName'], init['DesignName']=ProjectName, DesignName
    init['Object']=["AllObjects",
                    'winding_s'
                    ]
    init['save_path']=''
    init['save_path']='C:/Users/sbaek/WorkSpace/2016_Hornet/FEM_Results'
    init['save_name']=init['save_path']+'/'+init['ProjectName']

    ''' Initiation, solution type'''
    oProject, oDesign=initiation(init,open='On')

#    ''' Run simulation '''
#    oDesign.AnalyzeAll()

    ''' filed reporter'''
    oModule = oDesign.GetModule("FieldsReporter")
    try:
        oModule.CalcStack("clear")
        oModule.ClearAllNamedExpr()
        print 'clear expressions in a field calculator'
    except:pass

    loss_list, unit_loss_list=[], []
    for i in init['Object']:       
        name=loss(oDesign, i)
        loss_list.append(name)
        print '\n Set ohmic loss of %s'%(name)
        
        #name=volume(oDesign, i)
        #print '\n Set volume of %s'%(name)
        
        #name=unit_loss(oDesign, i)
        #unit_loss_list.append(name)
        #print '\n Set unit_loss of %s'%(name)
    Rac(oDesign)

    ''' plot'''
    oModule = oDesign.GetModule("ReportSetup")
    try:
        oModule.DeleteAllReports()
        print 'delete plots'
    except:pass

    report(oDesign, ['Rac'], name='Rac')    #put a list of feild parameters in string format
    #report(oDesign, loss_list, name='Loss')
    #report(oDesign, unit_loss_list, name='Unit_Loss')


    #''' save'''
    #oDesign.ExportProfile("Setup1", " ", init['ProjectName']+"_profile.prof")
    #oProject.Save()
    #date=time.strftime("%d/%m/%Y %I:%M")
    #print '\n Close at %s ' %date
    #oProject.close()


if __name__ == '__main__':
    global para, init
    date= time.strftime("%m%d")
    para, init = OrderedDict(), OrderedDict()
    ProjectName, DesignName = "test1", "Xfmr"
    main(ProjectName, DesignName)



