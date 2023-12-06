# ---------------------------------------------------------------------------
# IA_Hairy-neckedTigerBeetle.py
# Created on: 2012 May
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw and Tim Howard, NYNHP)
# Usage: Important Area Model for NYNHP Hairy-necked Tiger Beetle (Cicindela hirticollis)
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

ModelType = "Invertebrates_hnTigerBeetle"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)
Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/_latest_results/" + ModelType + tyme + EXorHIST + ".shp"

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ESHR_HTB'"
    IAmodel = "01ESHR_HTB"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"

if Proj == "DOT":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
    
elif Proj == "HRE Culverts":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)


arcpy.AddMessage("In EOs selected. " + EXorHIST + " " + ModelType)


################### Select Bare Land from CCAP
###################
#   Selecting CCAP Wetlands, palustrine and estuarine, but not including water
LAYER_CCAP_BL = ExtractByAttributes(LULC, "VALUE = 19 OR VALUE = 20")
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management(LAYER_CCAP_BL, "LAYER_CCAP_selectpre")
arcpy.RasterToPolygon_conversion("LAYER_CCAP_selectpre", "polys_BL", "NO_SIMPLIFY", "VALUE")
arcpy.Dissolve_management("polys_BL", "DissolveBL", "", "", "SINGLE_PART")
arcpy.AddMessage("CCAP Bare Land selected.")

################### Select only contiguous beach LC
###################
arcpy.MakeFeatureLayer_management("DissolveBL", "LAYER_polys_BL")
arcpy.SelectLayerByLocation_management("LAYER_polys_BL", "INTERSECT", in_EOs, "", "NEW_SELECTION")

################### Union all
###################
arcpy.Union_analysis(["LAYER_polys_BL", in_EOs], "BLUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("BLUnion", "Dissolve", "", "", "SINGLE_PART")

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

arcpy.AddMessage("IA model done: Hairy-necked Tiger Beetle.")
