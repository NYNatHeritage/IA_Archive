# ---------------------------------------------------------------------------
# IA_Fish_AtlanticSilverside.py
# Created on: 2012 April
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (animal methodology by Hollie Shaw, NYNHP)
# This script shall not be distributed without permission from the New York Natural Heritage Program
# 
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os, arcpy, arcgisscripting, win32com.client

# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"

# Workspace
arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Fish_AtlanticSilverside"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)
Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_estvar"
in_estvar = "in_estvar"
out_estvar = "out_estvar"
StateBounds = "m:/reg0/reg0data/base/borders/statemun/region.state"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

arcpy.AddMessage(ModelType + " model")

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ERES_FAS'"
    IAmodel = "01ERES_FAS"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HXXXXXXX'"
    IAmodel = "01HXXXXXXX"

if Proj == "DOT":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
    
elif Proj == "HRE Culverts":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"

elif Proj == "All":
    LULC = "C:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
    StudyArea = "M:/reg0/reg0data/base/borders/statemun/region.state"
    
elif Proj == "HREP":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HREP"


##################### Select EOs
#####################

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

################### Run estuarine module
###################
arcpy.AddMessage("Running estuarine module...")
import IA_mod_estuarine
IA_mod_estuarine.EST_module(in_estvar, out_estvar, WSP, LULC)
arcpy.AddMessage("Estuarine model, complete.")

################### Buffer EOs
###################
arcpy.Buffer_analysis(in_estvar, "in_EOs_buff", 5000, "FULL", "ROUND", "ALL")
arcpy.AddMessage("EOs buffered 5 km.")

################### Erase terrestrial from 5km buffer
###################
arcpy.Erase_analysis("in_EOs_buff", StateBounds, "eraseEObuff")
arcpy.AddMessage("Erased terrestrial.")

################### Union 5km buffer with the estuarine buffer
###################
arcpy.Union_analysis([out_estvar, "eraseEObuff"], "FASUnion", "ONLY_FID", "", "NO_GAPS")

# This buffer is insignificant in dimension, but allows for kitty-corner cells to be counted
# as adjacent. The only way I can find to capture kitty-corner cells.
arcpy.Buffer_analysis("FASUnion", "polys_Elim", "1 Meters", "FULL", "ROUND", "ALL", "")
arcpy.MultipartToSinglepart_management("polys_Elim", "polys_ElimSP")
arcpy.MakeFeatureLayer_management("polys_ElimSP", "LAYER_polys_ElimSP", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_polys_ElimSP", "INTERSECT", in_estvar, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_polys_ElimSP", "Contiguous")

################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AggregatePolygons_cartography ("Contiguous", "Elim", 1, 0, 100000)
arcpy.AddField_management("Elim", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Elim", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management("Elim", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim2", "AREA", 1000000)

##################### WRAP UP
##################### 

arcpy.CopyFeatures_management ("Elim2", FinalFC)
arcpy.CopyFeatures_management ("Elim2", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Atlantic Silversides.")















