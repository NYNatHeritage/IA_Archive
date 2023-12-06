# ---------------------------------------------------------------------------
# IA_Birds_Beaches.py
# Created on: 2011 August
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw and Tim Howard, NYNHP)
# Usage: Important Area Model for NYNHP beach birds
# Latest Edits: Update for arcpy module
#   
# Shall not be distributed without written permission from the New York Natural Heritage Program
# ---------------------------------------------------------------------------
#
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

ModelType = "Birds_Beaches"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)

in_EOs = "in_EOs"
LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/_latest_results/" + ModelType + tyme + EXorHIST + ".shp"

if EXorHIST == "Extant":
    selectQuery = "\"IA_MODEL\" = '01ESHR_PIP' OR \"IA_MODEL\" = '01ESHR_TER'"
    IAmodel = "BirdsBeachesE"
elif EXorHIST == "Historical":
    selectQuery = "\"IA_MODEL\" = '01HSHR_PIP' OR \"IA_MODEL\" = '01HSHR_TER'"
    IAmodel = "BirdsBeachesH"


# Select out the proper EOs
arcpy.Select_analysis(in_put, in_EOs, selectQuery)
arcpy.AddMessage("In EOs selected. " + EXorHIST + " Beach birds.")


################### Buffer EOs
###################
arcpy.Buffer_analysis(in_EOs, "in_EOs_buff", 200, "FULL", "ROUND", "ALL")
arcpy.AddMessage("EOs buffered 200m.")

################### Select Beaches from CCAP
###################
#   Selecting CCAP Wetlands, palustrine and estuarine, but not including water
LAYER_CCAP_Beaches = ExtractByAttributes(LULC, "VALUE = 19 OR VALUE = 20")
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management(LAYER_CCAP_Beaches, "LAYER_CCAP_selectpre")
arcpy.RasterToPolygon_conversion("LAYER_CCAP_selectpre", "polys_Beaches", "NO_SIMPLIFY", "VALUE")
arcpy.AddMessage("CCAP Beaches selected.")

################### Clip Beaches
###################
arcpy.Clip_analysis("polys_Beaches", "in_EOs_buff", "CCAPbeaches")
arcpy.AddMessage("Beaches clipped.")

################### Select only contiguous beach LC
###################
arcpy.MakeFeatureLayer_management("CCAPbeaches", "LAYER_CCAPbeaches")
arcpy.SelectLayerByLocation_management("LAYER_CCAPbeaches", "INTERSECT", in_EOs, "", "NEW_SELECTION")

################### Union all
###################
arcpy.Union_analysis(in_EOs + " #; LAYER_CCAPbeaches #", "BeachUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("BeachUnion", "Dissolve", "", "", "SINGLE_PART")

################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("Dissolve", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Dissolve", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("Dissolve", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 3000)
arcpy.AddMessage("IA's aggregated.")

################### WRAP UP
################### 
arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Beach Birds.")
