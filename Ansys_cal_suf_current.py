# ----------------------------------------------
# Script Recorded by ANSYS Electronics Desktop Version 2016.0.0
# 10:53:28  May 19, 2016
# ----------------------------------------------
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
oProject = oDesktop.SetActiveProject("620_00504r03_sp")
oDesign = oProject.SetActiveDesign("pcb_v02_Q14")
oModule = oDesign.GetModule("FieldsReporter")

list=['LVN_84_Section1', 'LVP_83_Section1']
for i in list:
    name=i+'_amp'
    oModule.EnterQty("J")
    oModule.CalcOp("Real")
    oModule.EnterSurf(i)
    oModule.CalcOp("NormalComponent")
    oModule.CalcOp("Integrate")
    oModule.AddNamedExpression(name, "Fields")
    oModule.CopyNamedExprToStack(name)
    oModule.ClcEval("Setup1 : LastAdaptive", 
            [
                    "Freq:="		, "200kHz",
                    #"Irms:="		, "1A",
                    "Phase:="		, "90deg",
                    #"pcb_thick:="		, "1.665mm"
            ])
