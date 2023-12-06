# ---------------------------------------------------------------------------
# IA_Spadefoot_Toad.py
# Created on: 2010 December 7
#   
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw, Zoologist, NYNHP)
# Usage: Important Area Model for Spadefoot Toad (Scaphiopus holbrookii)
# Shall not be distributed without permission from the New York Natural Heritage Program
#   Edited: 2013 March 4
#   Edit: Update to HREP updates
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

ModelType = "Amphibians_Spadefoot"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)
#Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
CCAP_Select_Query = "VALUE = 2 OR VALUE = 3"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01EALL_EST'"
    IAmodel = "01EALL_EST"
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

        
print("Spadefoot Toad (Scaphiopus holbrookii) model")

##################### Select EOs
#####################

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

################### Buffer the EOs 500 meters
###################

arcpy.Buffer_analysis(in_EOs, "in_EOs_buff", 500, "FULL", "ROUND", "NONE", "")

################### Alis Roads
################### I had to place the select by attribute before the select by location, because there is a software
################### bug when you try to select by location on a very large SDE dataset. Sheesh.
print("Selecting Roads....")
arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\AIMS.alisroads", "LAYER_alisroads")

arcpy.SelectLayerByAttribute_management("LAYER_alisroads", "NEW_SELECTION", "\"ACC\" = 1 OR \"ACC\" = 2 OR \"ACC\" = 3")
arcpy.SelectLayerByLocation_management("LAYER_alisroads", "INTERSECT", "in_EOs_buff", "", "SUBSET_SELECTION")

arcpy.MakeFeatureLayer_management("LAYER_alisroads", "LAYER_selected_alisroads")

print("Buffering Selected Roads...")
arcpy.Buffer_analysis("LAYER_selected_alisroads", "Buff_alisroads", 6.25, "FULL", "ROUND", "ALL", "")

print("Cut Wetland Buffers with Roads...")
arcpy.Erase_analysis("in_EOs_buff", "Buff_alisroads", "Erase_Wet")

################### Developed Land Use
###################

# Extracting the CCAP Developed, and Erasing the buffered wetlands with it.
print("Select out high and medium intensity develed lands from CCAP....")
attExtract = ExtractByAttributes(LULC, CCAP_Select_Query) 
attExtract.save("CCAP_Dev")
arcpy.RasterToPolygon_conversion("CCAP_Dev", "polys_CCAP", "NO_SIMPLIFY", "VALUE")
arcpy.Dissolve_management("polys_CCAP", "polys_CCAPDissolve", "", "", "SINGLE_PART")
print("Erase Developed Lands from Wetland Buffers...")
arcpy.Erase_analysis("Erase_Wet", "polys_CCAPDissolve", "Erase_CCAP")

##################### Eliminate matrine areas by clipping with county layer
#####################
##
arcpy.Clip_analysis("Erase_CCAP", "m:/reg0/reg0data/base/borders/statemun/region.county", "No_Marine")
##arcpy.RepairGeometry_management ("Erase_No_Marine")
##arcpy.MultipartToSinglepart_management("Erase_No_Marine","No_Marine")

################### Aggregate polys and remove donut holes
###################

arcpy.MakeFeatureLayer_management("No_Marine", "LAYER_No_Marine")
arcpy.SelectLayerByLocation_management("LAYER_No_Marine", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_No_Marine", "Contiguous_Wet")

################### Union and Dissolve EOs back in
###################
arcpy.Union_analysis(in_EOs + " #; Contiguous_Wet #", "EOUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("EOUnion", "Dissolve", "", "", "SINGLE_PART")

################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("Dissolve", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Dissolve", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("Dissolve", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 1000000)

arcpy.MakeFeatureLayer_management("Elim", "LAYER_Elim")
arcpy.SelectLayerByLocation_management("LAYER_Elim", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Elim", "Contiguous_Spade")

################### WRAP UP
################### 
FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST

arcpy.CopyFeatures_management ("Contiguous_Spade", FinalFC)
arcpy.CopyFeatures_management ("Contiguous_Spade", FinalFC_gdb)

print("IA model done: Spadefoot Toad.")
