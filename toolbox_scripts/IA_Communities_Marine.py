# ---------------------------------------------------------------------------
# IA_Communities_Marine.py
# Created on: 2012 September
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Aissa Feldmann, NYNHP)
# Usage: Important Area Model for NYNHP Marine communities
#           adapted to marine communities
# Shall not be distributed without permission from the New York Natural Heritage Program
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

ModelType = "Communities_Marine"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)

in_EOs = "in_EOs"
LIshore = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/Shoreline_LINYC"
LIshore_line = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/Shoreline_LINYC_line"
Shoreline_LINYC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/Shoreline_LINYC"
Hydro24K = "Database Connections/Bloodhound.sde/ARCS.surfwatr"
LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT_2006"
CCAP_select = "CCAP_select"
CCAP_Select_Query = "VALUE = 13 OR VALUE = 14 OR VALUE = 15 OR VALUE = 17 OR VALUE = 18 OR VALUE = 22 OR VALUE = 23"

FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST


if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '03EMAR_G01'"
    IAmodel = "03EMAR_G01"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"

arcpy.AddMessage("Marine Communities model")


# Select out the proper EOs
arcpy.Select_analysis(in_put, in_EOs, selectQuery)
arcpy.AddMessage("In EOs selected. " + EXorHIST + " " + ModelType)

# Buffer EOs 200m
arcpy.Buffer_analysis(in_EOs, "in_EOs200", 200, "FULL", "ROUND", "ALL", "")
# Clip the the shoreline
arcpy.Clip_analysis(LIshore_line, "in_EOs200", "Shoreline")

# Selecting out bays vs. lands
arcpy.MakeFeatureLayer_management(LIshore, "LAYER_LIshore")
arcpy.SelectLayerByAttribute_management("LAYER_LIshore", "NEW_SELECTION", "\"TYPE\" = 'Bay'")
arcpy.SelectLayerByLocation_management("LAYER_LIshore", "INTERSECT", "in_EOs200", "", "SUBSET_SELECTION")
arcpy.CopyFeatures_management ("LAYER_LIshore", "in_bays")

# Buffer captured shoreline 200m
arcpy.Buffer_analysis("in_bays", "in_bays200", 200, "FULL", "ROUND", "ALL", "")

# Buffer captured shoreline 200m
arcpy.Buffer_analysis("Shoreline", "Shoreline_200", 200, "FULL", "ROUND", "ALL", "")

### Clip the unioned buffer with the shoreline
##arcpy.Clip_analysis("ShoreUnion", Shoreline_LINYC, "Shoreclip")

# Hydro24K, poly features:
arcpy.AddMessage("Selecting Hydro24K...")

arcpy.MakeFeatureLayer_management(Hydro24K, "LAYER_Hydro24K")
arcpy.SelectLayerByAttribute_management("LAYER_Hydro24K", "NEW_SELECTION", "\"MAJOR1\" = 50")
arcpy.SelectLayerByLocation_management("LAYER_Hydro24K", "INTERSECT", "Shoreline_200", "", "SUBSET_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Hydro24K", "Hydro24K_polys")
arcpy.AddMessage("LAYER_Hydro24K have been selected.")

# Union bay buffs, hydro 24K polys, and shoreline buffs
arcpy.Union_analysis(["in_bays200", in_EOs, "Shoreline_200", "Hydro24K_polys"], "ShoreUnion", "ONLY_FID", "", "NO_GAPS")

################### Determine contiguous CCAP palustrine wetlands
###################
in_features = "ShoreUnion"
import IA_mod_lulc_select
IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
arcpy.AddMessage("LU/LC SELECT: CCAP Wetlands have been selected...")
 
# Union the input EOs and wetlands.
arcpy.Union_analysis(["ShoreUnion", "in_EOs200", CCAP_select], "WetShoreUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("WetShoreUnion", "WetShoreDiss", "", "", "SINGLE_PART")

################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("WetShoreDiss", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("WetShoreDiss", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("WetShoreDiss", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 1000000)

################### WRAP UP
################### 
arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Marine Communities.")







