# ---------------------------------------------------------------------------
# IA_CTern_foraging.py
# Created on: 2011 August
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw, NYNHP)
# Usage: Important Area Model for NYNHP foraging common tern
# Latest Edits:
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
arcpy.env.workspace = arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace

# Load required toolboxes...
arcpy.env.overwriteOutput = True

ModelType = "Birds_CTern_foraging"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)

in_EOs = "in_EOs"
StateBounds = "m:/reg0/reg0data/base/borders/statemun/region.state"
#LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
#FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/_latest_results/" + ModelType + tyme + EXorHIST + ".shp"

if EXorHIST == "Extant":
    selectQuery = "\"IA_MODEL\" = '01ETES_COT'"
    IAmodel = "01ETES_COT"
elif EXorHIST == "Historical":
    selectQuery = "\"IA_MODEL\" = '01HTES_COT'"
    IAmodel = "01HTES_COT"


# Select out the proper EOs
arcpy.Select_analysis(in_put, in_EOs, selectQuery)
print("In EOs selected. " + EXorHIST + " " + ModelType)


################### Buffer EOs
###################
arcpy.Buffer_analysis(in_EOs, "in_EOs_buff", 5000, "FULL", "ROUND", "ALL")
print("EOs buffered 5 km.")

################### Erase terrestrial from foraging area
###################
arcpy.Erase_analysis("in_EOs_buff", StateBounds, "eraseEObuff")
print("Erased terrestrial.")

################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("eraseEObuff", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("eraseEObuff", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("eraseEObuff", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 3000)
print("IA's aggregated.")

################### WRAP UP
################### 
FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST

arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", FinalFC_gdb)

print("IA model done: Common Tern Foraging Area.")



