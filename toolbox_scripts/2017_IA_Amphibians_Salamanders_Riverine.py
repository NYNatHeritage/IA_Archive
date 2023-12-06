# ---------------------------------------------------------------------------
# IA_Amphibians_Salamanders_Riverine.py
# Created on: 2011 November
#   
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw, Zoologist, NYNHP)
# Usage: Important Area Model for River/Stream Salamanders

# Shall not be distributed without permission from the New York Natural Heritage Program
#   Edited: 
#   Edit: 
# ---------------------------------------------------------------------------
#
# Import system modules
import sys, string, os, arcgisscripting, win32com.client, arcpy

# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"

# Workspace
arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True


ModelType = "Amphibians_Salamanders_Riverine"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)
#Proj = arcpy.GetParameterAsText(3)


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


in_EOs = "in_EOs"
CCAP_Select_Query = "\"VALUE\" = 2"
#FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST



if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ERIV_SAL'"
    IAmodel = "01ERIV_SAL"
#elif EXorHIST == "Historical":
#    selectQuery = "IA_MODEL = '01HXXXXXXX'"
#    IAmodel = "01HXXXXXXX"


arcpy.AddMessage(ModelType + " model")

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

# Buffer the points 10 and 30 meters, and then 340 meters
arcpy.AddMessage("Buffer the points 10 and 30 meters, and then 340 meters...")
arcpy.Buffer_analysis(in_EOs, "in_buff10", 10, "FULL", "ROUND", "ALL", "")
arcpy.Buffer_analysis(in_EOs, "in_buff30", 30, "FULL", "ROUND", "ALL", "")
arcpy.Buffer_analysis("in_buff30", "buff340", 340, "FULL", "ROUND", "ALL", "")

################### Alis Roads (Class 1 amd 2 only)
################### I had to place the select by attribute before the select by location, because there is a software
################### bug when you try to select by location on a very large SDE dataset. Sheesh.

print ("Removing selected Roads....")
arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\AIMS.alisroads", "LAYER_alisroads")
arcpy.SelectLayerByAttribute_management("LAYER_alisroads", "NEW_SELECTION", "\"ACC\" = 1 OR \"ACC\" = 2")
arcpy.SelectLayerByLocation_management("LAYER_alisroads", "INTERSECT", "buff340", "", "SUBSET_SELECTION")
arcpy.MakeFeatureLayer_management("LAYER_alisroads", "LAYER_selected_alisroads")
arcpy.Buffer_analysis("LAYER_selected_alisroads", "Buff_alisroads", 6.25, "FULL", "ROUND", "ALL", "")
arcpy.Erase_analysis("buff340", "Buff_alisroads", "Erase340")

# Select out the higher resolution waterbodies with the dissolved catchments.
arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\ARCS.surfwatr", "LAYER_24Kwaterbodies")
arcpy.SelectLayerByLocation_management("LAYER_24Kwaterbodies", "INTERSECT", "Erase340", "", "NEW_SELECTION")
arcpy.Union_analysis(["LAYER_24Kwaterbodies", "Erase340"], "HydroBuffUnion", "", "", "NO_GAPS")
arcpy.Dissolve_management("HydroBuffUnion", "Dissolve", "", "", "SINGLE_PART")

################### Extracting the CCAP hi intensity lu, and erase from buffer
###################
print ("Removing CCAP developed/barren land LU/LC....")
arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAP", CCAP_Select_Query)
arcpy.RasterToPolygon_conversion("LAYER_CCAP", "polys_CCAP", "NO_SIMPLIFY", "VALUE")
arcpy.Erase_analysis("Dissolve", "polys_CCAP", "Erase2")

# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("Erase2", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Erase2", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management("Erase2", "Dissolve", "IA_MODEL_R", "", "SINGLE_PART")
#Since the SINGLE_PART function in previous step is mysteriously not working:
arcpy.MultipartToSinglepart_management("Dissolve","Dissolvesp")


# Select out only those polys contiguous with the EO
arcpy.MakeFeatureLayer_management("Dissolvesp", "LAYER_Dissolvesp")
arcpy.SelectLayerByLocation_management("LAYER_Dissolvesp", "INTERSECT", "in_buff10", "", "NEW_SELECTION")

################### WRAP UP
################### 
print FinalFC
print ModelType
FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST

arcpy.CopyFeatures_management ("LAYER_Dissolvesp", FinalFC)
arcpy.CopyFeatures_management ("LAYER_Dissolvesp", FinalFC_gdb)

print ("IA model done: Stream/River Salamanders.")

