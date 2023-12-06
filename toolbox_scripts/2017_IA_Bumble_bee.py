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

ModelType = "Bumble_bee"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)
#Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
CCAP_Select_Query = "VALUE = 21" #Select out open water
#FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETER_BEE'"
    IAmodel = "01ETER_BEE"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"


        
print("Bumblee Bee (Bombus bombus) model")

##################### Select EOs
#####################

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

################### Buffer the EOs 500 meters
###################

arcpy.Buffer_analysis(in_EOs, "in_EOs_buff", 2000, "FULL", "ROUND", "NONE", "")

################### Alis Roads
################### I had to place the select by attribute before the select by location, because there is a software
################### bug when you try to select by location on a very large SDE dataset. Sheesh.
print("Selecting Roads....")
arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\AIMS.alisroads", "LAYER_alisroads")

arcpy.SelectLayerByAttribute_management("LAYER_alisroads", "NEW_SELECTION", "\"ACC\" = 1 OR \"ACC\" = 2 ")
arcpy.SelectLayerByLocation_management("LAYER_alisroads", "INTERSECT", "in_EOs_buff", "", "SUBSET_SELECTION")

arcpy.MakeFeatureLayer_management("LAYER_alisroads", "LAYER_selected_alisroads")

print("Buffering Selected Roads...")
arcpy.Buffer_analysis("LAYER_selected_alisroads", "Buff_alisroads", 6.25, "FULL", "ROUND", "ALL", "")

print("Cut Wetland Buffers with Roads...")
arcpy.Erase_analysis("in_EOs_buff", "Buff_alisroads", "Erase_Wet")




arcpy.EliminatePolygonPart_management("Erase_Wet", "Erase_Wet_test", "AREA", 10000,"#","ANY" )

################### Developed Land Use
###################

# Extracting the CCAP Developed, and Erasing the buffered wetlands with it.
print("Select out open Water CCAP....")
attExtract = ExtractByAttributes(LULC, CCAP_Select_Query) 
attExtract.save("CCAP_Dev")
arcpy.RasterToPolygon_conversion("CCAP_Dev", "polys_CCAP", "NO_SIMPLIFY", "VALUE")
arcpy.Dissolve_management("polys_CCAP", "polys_CCAPDissolve", "", "", "SINGLE_PART")
print("Erase Open Water from Wetland Buffers...")
arcpy.Erase_analysis("Erase_Wet", "polys_CCAPDissolve", "Erase_CCAP")



arcpy.EliminatePolygonPart_management("Erase_CCAP", "Erase_CCAP_test", "AREA", 1000000 )

#####Create set of polys that only represent the high intensity land use within the buffer
#arcpy.gp.Con_sa(LULC, "1", "LAYER_CCAP_dev", "0", "\"VALUE\" in (2)")
#arcpy.gp.SetNull_sa("LAYER_CCAP_dev", "1", "LAYER_CCAPnull_dev", "\"Value\" = 0")
#arcpy.gp.ExtractByMask_sa("LAYER_CCAPnull_dev", "in_EOs_buff", "extractedLU_dev")
#arcpy.RasterToPolygon_conversion("extractedLU_dev", "polys_clip_dev", "NO_SIMPLIFY", "VALUE")



##################### Eliminate matrine areas by clipping with county layer
#####################
##
#arcpy.Clip_analysis("Erase_CCAP", "m:/reg0/reg0data/base/borders/statemun/region.county", "No_Marine")
##arcpy.RepairGeometry_management ("Erase_No_Marine")
##arcpy.MultipartToSinglepart_management("Erase_No_Marine","No_Marine")

################### Aggregate polys and remove donut holes
###################

arcpy.MakeFeatureLayer_management("Erase_CCAP", "LAYER_Erase_CCAP")
arcpy.SelectLayerByLocation_management("LAYER_Erase_CCAP", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_Erase_CCAP", "Contiguous_Wet")



################### Union and Dissolve EOs back in- Problem area- gets rid of the holes
###################
arcpy.Union_analysis("Contiguous_Wet", "EOUnion", "ONLY_FID", "", "GAPS")
arcpy.Dissolve_management("EOUnion", "Dissolve", "", "", "SINGLE_PART")

arcpy.CopyFeatures_management("Dissolve", "D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\bees_test")


################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("Dissolve", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Dissolve", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("Dissolve", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 1000000 )




####Clip out the Development Polygons  **Optional**
#arcpy.Erase_analysis("Dissolve2","polys_clip_dev","Elim",'#')
#
#tyme="_6_22_no_dev_"


arcpy.MakeFeatureLayer_management("Elim", "LAYER_Elim")
arcpy.SelectLayerByLocation_management("LAYER_Elim", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Elim", "Contiguous_Spade")

############################
#tyme="_6_22_w_dev_"
#arcpy.MakeFeatureLayer_management("Dissolve2", "LAYER_Elim")
#arcpy.SelectLayerByLocation_management("LAYER_Elim", "INTERSECT", in_EOs, "", "NEW_SELECTION")
#arcpy.CopyFeatures_management ("LAYER_Elim", "Contiguous_Spade")

################### WRAP UP
################### 
FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST


arcpy.CopyFeatures_management ("Contiguous_Spade", FinalFC)
arcpy.CopyFeatures_management ("Contiguous_Spade", FinalFC_gdb)

print("IA model done: Bumble Bee.")
