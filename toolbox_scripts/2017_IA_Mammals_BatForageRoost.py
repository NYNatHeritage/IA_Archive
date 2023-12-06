# ---------------------------------------------------------------------------
# IA_Mammals_BatForageRoost.py
# Created on: 2013 March
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Erin White, Zoologist, NYNHP)
# Usage: Important Area Model for New England Bat Foraging and Roosting
#   Dependency: none
# Shall not be distributed without permission from the New York Natural Heritage Program
#   Edited: 
#   Edit Reason:
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
arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Mammals_BatForageRoost"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)
#Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
#FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETER_MYR'"
    IAmodel = "01ETER_MYR"
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

print(ModelType + " model")


# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

################### Buffer selected EOs 2.5 miles
###################
arcpy.Buffer_analysis(in_EOs, "in_EOs_buff", 4023.36, "FULL", "ROUND", "ALL", "")
arcpy.MultipartToSinglepart_management("in_EOs_buff","in_EOs_buffsp")

##################### Select codes from CCAP, clip out LULC, Union to EOs, and prep for terrestrial model
#####################
#   Selecting CCAP Wetlands, palustrine and estuarine, but not including water
arcpy.gp.Con_sa(LULC, "1", "LAYER_CCAP", "0", "\"VALUE\" in ( 21, 4, 11, 9, 8, 7, 12, 13, 15, 14)")
arcpy.gp.SetNull_sa("LAYER_CCAP", "1", "LAYER_CCAPnull", "\"Value\" = 0")
arcpy.gp.ExtractByMask_sa("LAYER_CCAPnull", "in_EOs_buffsp", "extractedLU")
arcpy.RasterToPolygon_conversion("extractedLU", "polys_clip", "NO_SIMPLIFY", "VALUE")

##################### Erase elevation > 900
#####################
arcpy.Erase_analysis("polys_clip", "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/elevGT900feet", "EraseElev900ft")

##################### Union/Dissolve
#####################
arcpy.Union_analysis(["EraseElev900ft", in_EOs], "BatUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("BatUnion", "BatDissolve", "", "", "SINGLE_PART")

################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("BatDissolve", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("BatDissolve", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("BatDissolve", "BatDissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("BatDissolve2", "BatElim", "AREA", 1000000)

arcpy.MakeFeatureLayer_management("BatElim", "LAYER_Elim")
arcpy.SelectLayerByLocation_management("LAYER_Elim", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Elim", "Contiguous")

################### WRAP UP
################### 

FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST

arcpy.CopyFeatures_management ("Contiguous", FinalFC)
arcpy.CopyFeatures_management ("Contiguous", FinalFC_gdb)

print("IA model done: Mammals Bat Foraging and Roosting.")

