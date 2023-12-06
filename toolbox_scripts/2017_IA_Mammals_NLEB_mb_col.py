# ---------------------------------------------------------------------------
# IA_NLEB_MatBach.py
# Created on: 2018 April 30
#   
#   (created by Amy Conley, Spatial Ecologist, NYNHP)
#   (methodology by Hollie Shaw, Zoologist, NYNHP)
# Usage: Important Area Model for Northern Long Eared Bat maternal and bachelor colonies
#   Dependency: 
# Shall not be distributed without permission from the New York Natural Heritage Program
#   Edited: 
#   Edit: 
# ---------------------------------------------------------------------------
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

ModelType = "Mammals_NLEB_mbcol"


in_EOs = "in_EOs"
#FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETER_NLS'"
    IAmodel = "01ETER_NLS"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"
    


print(ModelType + " model")


# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

################### Buffer selected EOs 1.5 miles
###################
arcpy.Buffer_analysis(in_EOs, "in_EOs_buff", 2414.02, "FULL", "ROUND", "ALL", "")
arcpy.MultipartToSinglepart_management("in_EOs_buff","in_EOs_buffsp")

##################### Select codes from CCAP, clip out LULC, Union to EOs, and prep for terrestrial model
#####################
#   Selecting CCAP mixed forest, deciduous forest, evergreen forest, palustrine forested wetlands, but not including water
arcpy.gp.Con_sa(LULC, "1", "LAYER_CCAP", "0", "\"VALUE\" in ( 9,10,11,13)")
arcpy.gp.SetNull_sa("LAYER_CCAP", "1", "LAYER_CCAPnull", "\"Value\" = 0")
arcpy.gp.ExtractByMask_sa("LAYER_CCAPnull", "in_EOs_buffsp", "extractedLU")
arcpy.RasterToPolygon_conversion("extractedLU", "polys_clip", "NO_SIMPLIFY", "VALUE")


################### Buffer selected EOs 30 meters  Dissolve
###################
arcpy.Buffer_analysis("polys_clip", "polys_clip_buff", 30, "FULL", "ROUND", "ALL", "")
arcpy.MultipartToSinglepart_management("polys_clip_buff","BatDissolve")


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

print("IA model done: Mammals Norther Long Eared Bat Maternal and Bachelor colonies.")