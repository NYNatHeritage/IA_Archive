# ---------------------------------------------------------------------------
# IA_Invertebrates_WVWnLep.py
# Created on: 2013 March
#   (script by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw, NYNHP)
# Usage: Important Area Model for NYNHP West Virginia White Leps
#   
 # This script shall not be distributed without permission from the New York Natural Heritage Program
# ---------------------------------------------------------------------------
#
# Import system modules
import sys, string, os, arcpy

# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"

# Workspace
arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Invertebrates_WestVirginiaWhite"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)
Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

arcpy.AddMessage(ModelType + " model")

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETER_WVW'"
    IAmodel = "01ETER_WVW"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"

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

##################### Create temporary buffer
#####################
arcpy.Buffer_analysis(in_EOs, "temp_buff", "1000", "FULL", "ROUND", "ALL", "")

##################### Select codes from CCAP, clip out LULC, Union to EOs, and prep for terrestrial model
#####################
#   Selecting CCAP Wetlands, palustrine and estuarine, but not including water
LAYER_CCAP = ExtractByAttributes(LULC, "\"VALUE\" = 9 OR \"VALUE\" = 11 OR \"VALUE\" = 13")
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management(LAYER_CCAP, "LAYER_CCAP_pre")
arcpy.RasterToPolygon_conversion("LAYER_CCAP_pre", "polys_codes", "NO_SIMPLIFY", "VALUE")
arcpy.AddMessage("Codes selected from CCAP")

arcpy.Clip_analysis("polys_codes", "temp_buff", "polys_clip")
arcpy.Union_analysis(["polys_clip", in_EOs], "preUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("preUnion", "preDissolve", "", "", "SINGLE_PART")

####################### Run terrestrial module
#######################
arcpy.Erase_analysis("preDissolve", "Database Connections/Bloodhound.sde/ARCS.surfwatr", "EraseSurfW")
arcpy.Erase_analysis("EraseSurfW", "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/NEAHC2to5_unshadedstreams", "EraseUnshadeStreams")
arcpy.Erase_analysis("EraseUnshadeStreams", "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/ALIS_clipped_unshaded_buff25", "EraseUnshadeRoads")

################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("EraseUnshadeRoads", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("EraseUnshadeRoads", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("EraseUnshadeRoads", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 1000000)


################### WRAP UP
################### 
arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Invertebrates West Virginia White")



