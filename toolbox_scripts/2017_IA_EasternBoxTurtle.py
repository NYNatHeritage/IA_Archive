# ---------------------------------------------------------------------------
# IA_EasternBoxTurtle.py
# Created on: 2011 November 23
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw, Zoologist, NYNHP)
# Usage: Important Area Model for Fence Lizard (Sceloporus undulatus hyacinthinus) and Eastern Wormsnake (Carphophis amoenus)
#   Dependency: none
# Shall not be distributed without permission from the New York Natural Heritage Program
# ---------------------------------------------------------------------------
#
# Import system modules
import sys, string, os, arcgisscripting, win32com.client, arcpy

# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
#arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"
arcpy.env.snapRaster ="F:\\_Schmid\\_GIS_Data\\SnapRasters\\snapras30met"   #2017 update path

# Workspace
#arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True


ModelType = "EasternBoxTurtle_"
in_EOs = "in_EOs"
#in_put = arcpy.GetParameterAsText(0)
#in_put= "D:\\Git_Repos\\IA_geoprocessing_scripts\\EOs_test_for_scripts.gdb\\EOs_test_for_scripts_sample"
#EXorHIST = arcpy.GetParameterAsText(1)
#EXorHIST = "Extant"
#tyme = arcpy.GetParameterAsText(2)
#tyme="12_01_2011"
CCAP_select = "CCAP_select"
CCAP_Select_Query = "\"VALUE\" = 2 OR \"VALUE\" = 3 OR \"VALUE\" = 6 OR \"VALUE\" = 21 OR \"VALUE\" = 22 OR \"VALUE\" = 23"

#LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
#LULC = "F:\\_Schmid\\_project\\Important_Areas\\GIS_Data\\IA_Process.gdb\\LULC_HRE"
#LULC = "D:\\Git_Repos\\IA_geoprocessing_scripts\\EOs_test_for_scripts.gdb\\LULC_HRE_10"

DEC_wetlands = "DEC_wetlands"
NWI_select = "NWI_select"
#FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/_latest_results/" + ModelType + tyme + EXorHIST + ".shp"
FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETER_BOT'"
    IAmodel = "01ETER_BOT"
#elif EXorHIST == "Historical":
#    selectQuery = "IA_MODEL = '01XXXXXXX'"
#    IAmodel = "01XXXXXXX"


arcpy.AddMessage("Eastern Box Turtle model")
print ("Eastern Box Turtle model")

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)


# Buffer selected EOs 10 meters and 1000 meters
arcpy.AddMessage("Buffering EOs, 10 meters and 1000 meters....")
print ("Buffering EOs, 10 meters and 1000 meters....")
arcpy.Buffer_analysis(in_EOs, "in_buff10", 10, "FULL", "ROUND", "ALL", "")
arcpy.Buffer_analysis(in_EOs, "in_buff", 1000, "FULL", "ROUND", "ALL", "")

########HOLLIE WANTED THIS REMOVED, LEAVE HERE TILL FINAL APPROVAL
##################### Alis Roads (Class 1 only)
##################### I had to place the select by attribute before the select by location, because there is a software
##################### bug when you try to select by location on a very large SDE dataset. Sheesh.
##
##arcpy.AddMessage("Eliminating selected roads....")
##arcpy.MakeFeatureLayer_management("Database Connections/bloodhound.sde/AIMS.alisroads", "LAYER_alisroads")
##arcpy.SelectLayerByAttribute_management("LAYER_alisroads", "NEW_SELECTION", "\"ACC\" = 1 OR \"ACC\" = 2 OR \"ACC\" = 3")
##arcpy.SelectLayerByLocation_management("LAYER_alisroads", "INTERSECT", "in_buff", "", "SUBSET_SELECTION")
##arcpy.MakeFeatureLayer_management("LAYER_alisroads", "LAYER_selected_alisroads")
##arcpy.Buffer_analysis("LAYER_selected_alisroads", "Buff_alisroads", 6.25, "FULL", "ROUND", "ALL", "")
##arcpy.Erase_analysis("in_buff", "Buff_alisroads", "Erase")

# Extracting the CCAP uplands and erase from buffer
#arcpy.AddMessage("Eliminating selected CCAP....")
print "Eliminating selected CCAP...."
arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAP", CCAP_Select_Query)
arcpy.RasterToPolygon_conversion("LAYER_CCAP", "polys_CCAP", "NO_SIMPLIFY", "VALUE")
arcpy.Erase_analysis("in_buff", "polys_CCAP", "Erase2")

# Union all wetlands and EOs
arcpy.AddMessage("Unioning all....")
print "Unioning all...."
arcpy.Union_analysis(["in_buff10", "Erase2"], "Unioned", "", "", "NO_GAPS")
arcpy.Dissolve_management("Unioned", "Dissolve1", "", "", "SINGLE_PART")

# Add the IA_MODEL_R field
arcpy.AddWarning("wrap up....")
print "wrap up...."
arcpy.AddField_management("Dissolve1", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Dissolve1", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management("Dissolve1", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 3000)

# Select out only those polys contiguous with the EO
arcpy.MakeFeatureLayer_management("Elim", "LAYER_Elim")
arcpy.SelectLayerByLocation_management("LAYER_Elim", "INTERSECT", "in_buff10", "", "NEW_SELECTION")

################### WRAP UP
################### 
arcpy.CopyFeatures_management ("LAYER_Elim", FinalFC)
#arcpy.CopyFeatures_management ("LAYER_Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)
arcpy.CopyFeatures_management ("LAYER_Elim", "D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST)



arcpy.AddMessage("IA model done: Eastern Box Turtle.")
print "IA model done: Eastern Box Turtle."
