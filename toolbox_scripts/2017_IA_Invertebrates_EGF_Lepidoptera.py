# ---------------------------------------------------------------------------
# IA_Invertebrates_EvergreenForestLepidoptera.py
# Created on: 2012 May
#   (script by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw and Jesse Jaycox, NYNHP)
# Usage: Important Area Model for NYNHP Evergreen Forest Leps
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
arcpy.env.workspace = arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Invertebrates_EvergreenForestLepidoptera"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)
#Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

print(ModelType + " model")

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETER_EGF'"
    IAmodel = "01ETER_EGF"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"

#if Proj == "DOT":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
#    
#elif Proj == "HRE Culverts":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"
#
#elif Proj == "All":
#    LULC = "C:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
#    StudyArea = "M:/reg0/reg0data/base/borders/statemun/region.state"
#    
#elif Proj == "HREP":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HREP"
#

##################### Select EOs
#####################

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

##################### Create temporary buffer
#####################
arcpy.Buffer_analysis(in_EOs, "temp_buff", "1500", "FULL", "ROUND", "ALL", "")

################### Select evergreen forest from CCAP, and clip it to the temp buffer
###################
#   Selecting CCAP Wetlands, palustrine and estuarine, but not including water
LAYER_CCAP_evergreen = ExtractByAttributes(LULC, "VALUE = 10 OR VALUE = 11")
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management(LAYER_CCAP_evergreen, "LAYER_CCAP_evergreenpre")
arcpy.RasterToPolygon_conversion("LAYER_CCAP_evergreenpre", "polys_evergreen", "NO_SIMPLIFY", "VALUE")
print("Evergreen Forest selected from CCAP")
arcpy.Clip_analysis("polys_evergreen", "temp_buff", "EvergreenForest_clip")
arcpy.Buffer_analysis("EvergreenForest_clip", "EvergreenForest", "1 Meters", "FULL", "ROUND", "ALL", "")
arcpy.Dissolve_management("EvergreenForest", "EvergreenForest_diss", "", "", "SINGLE_PART")
arcpy.MultipartToSinglepart_management("EvergreenForest_diss", "EvergreenForest_sp")

##################### Run terrestrial module
#####################
inputPar = "EvergreenForest_sp"
outputPar = "outputpar"
import IA_mod_terrestrial
IA_mod_terrestrial.TerrestrialModule(inputPar, outputPar)
print("Terrestrial Module complete")

#Union them and prepare to test size
arcpy.Union_analysis([outputPar, in_EOs], "EverForUnion", "ONLY_FID", "", "NO_GAPS")


################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("EverForUnion", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("EverForUnion", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("EverForUnion", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 1000000)


################### WRAP UP
################### 
FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST

arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", FinalFC_gdb)

print("IA model done: Invertebrates_EvergreenForestLepidoptera")


