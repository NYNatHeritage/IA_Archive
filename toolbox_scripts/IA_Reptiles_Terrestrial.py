# ---------------------------------------------------------------------------
# IA_Terrestrial_Reptiles.py
# Created on: 2010 December 1
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw, Zoologist, NYNHP)
# Usage: Important Area Model for Fence Lizard (Sceloporus undulatus hyacinthinus) and Eastern Wormsnake (Carphophis amoenus)
#   Dependency: none
# Shall not be distributed without permission from the New York Natural Heritage Program
#   Edited: 2012 February 28
#   Edit Reason: Updated script to arcpy module and created tool for toolbox.
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
#arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Reptile_Terrestrial"
#in_put = arcpy.GetParameterAsText(0)
in_put= "D:\\Git_Repos\\IA_geoprocessing_scripts\\EOs_test_for_scripts.gdb\\EOs_test_for_scripts_sample"
#EXorHIST = arcpy.GetParameterAsText(1)
EXorHIST = "Extant"
#tyme = arcpy.GetParameterAsText(2)
tyme="12_01_2011"
#Proj = arcpy.GetParameterAsText(3)
Proj = "HREP"

in_EOs = "in_EOs"
CCAP_Select_Query = "VALUE = 1 OR VALUE = 2 OR VALUE = 3 OR VALUE = 4 OR VALUE = 5 OR VALUE = 6 OR VALUE = 7 OR VALUE = 8 OR VALUE = 9 OR VALUE = 10, OR VALUE = 11 OR VALUE = 12"
FinalFC = "D:\\Git_Repos\\IA_geoprocessing_scripts\\output.GDB\\" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETER_TR1'"
    IAmodel = "01ETER_TR1"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"
    
if Proj == "DOT":
    LULC = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
    StudyArea = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
    
elif Proj == "HRE Culverts":
    LULC = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
    StudyArea = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"

elif Proj == "All":
    LULC = "F:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
    StudyArea = "M:/reg0/reg0data/base/borders/statemun/region.state"
    
elif Proj == "HREP":
    LULC = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"
    StudyArea = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HREP"


arcpy.AddMessage(ModelType + " model")


# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

################### Buffer selected EOs 200 meters
###################
arcpy.Buffer_analysis(in_EOs, "in_EOs_buff", 200, "FULL", "ROUND", "NONE", "")

################### Extracting the CCAP uplands
###################
arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAP_upland", CCAP_Select_Query)
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management("LAYER_CCAP_upland", "CCAP_upland")
arcpy.RasterToPolygon_conversion("CCAP_upland", "polys_CCAPU", "NO_SIMPLIFY", "VALUE")

################### Clip the upland LU/LC with the 200m buffer
###################
arcpy.Clip_analysis("polys_CCAPU", "in_EOs_buff", "CCAP_uplands")

################### Union and Dissolve all
###################
arcpy.Union_analysis(in_EOs + " #; CCAP_uplands #", "UpUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("UpUnion", "UpDissolve", "", "", "SINGLE_PART")

################### Alis Roads (Class 1 only)
################### I had to place the select by attribute before the select by location, because there is a software
################### bug when you try to select by location on a very large SDE dataset. Sheesh.

arcpy.AddMessage("Selecting Roads....")
arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\AIMS.alisroads", "LAYER_alisroads")

arcpy.SelectLayerByAttribute_management("LAYER_alisroads", "NEW_SELECTION", "\"ACC\" = 1 OR \"ACC\" = 2")
arcpy.SelectLayerByLocation_management("LAYER_alisroads", "INTERSECT", "UpDissolve", "", "SUBSET_SELECTION")

arcpy.MakeFeatureLayer_management("LAYER_alisroads", "LAYER_selected_alisroads")

arcpy.AddMessage("Buffering Selected Roads...")
arcpy.Buffer_analysis("LAYER_selected_alisroads", "Buff_alisroads", 6.25, "FULL", "ROUND", "ALL", "")

arcpy.AddMessage("Cut Buffers with Roads...")
arcpy.Erase_analysis("UpDissolve", "Buff_alisroads", "Erase_Up")

################### Developed Land Use
###################

# Extracting the CCAP Developed, and Erasing the buffered uplands with it.
arcpy.AddMessage("Select out high and medium intensity develed lands from CCAP....")
arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAP_developed", "\"VALUE\" = 2")
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management("LAYER_CCAP_developed", "CCAP_developed")
arcpy.RasterToPolygon_conversion("CCAP_developed", "polys_CCAP", "NO_SIMPLIFY", "VALUE")
arcpy.Dissolve_management("polys_CCAP", "polys_CCAPDissolve", "", "", "SINGLE_PART")
arcpy.AddMessage("Erase Developed Lands from Wetland Buffers...")
arcpy.Erase_analysis("Erase_Up", "polys_CCAPDissolve", "Erase_CCAP")
arcpy.MultipartToSinglepart_management("Erase_CCAP","Erase_fl")

################### Union and Dissolve EOs back in
###################
arcpy.Union_analysis(in_EOs + " #; Erase_fl #", "EOUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("EOUnion", "Dissolve", "", "", "SINGLE_PART")
# Next two steps are necessary because arc doesn't consider a donut hole vector square (remnant of cells) with a corner touching the 'outside' of the
# non-hole part of the donut as a hole to eliminate - so I buffer it one meter to become a true donut hole (don't get me going, ugh).
arcpy.Buffer_analysis("Dissolve", "dissbuff", 1, "FULL", "ROUND", "ALL")
arcpy.MultipartToSinglepart_management("dissbuff","dissbuff_sp")

################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("dissbuff_sp", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("dissbuff_sp", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("dissbuff_sp", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 1000000)

arcpy.MakeFeatureLayer_management("Elim", "LAYER_Elim")
arcpy.SelectLayerByLocation_management("LAYER_Elim", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Elim", "Contiguous")

################### WRAP UP
################### 
arcpy.CopyFeatures_management ("Contiguous", FinalFC)
#arcpy.CopyFeatures_management ("Contiguous", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Terretrial Reptiles.")

