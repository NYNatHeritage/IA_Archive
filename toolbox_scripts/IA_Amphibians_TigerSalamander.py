# ---------------------------------------------------------------------------
# IA_Tiger_Salamander.py
# Created on: 2010 December 2
#   
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw, Zoologist, NYNHP)
# Usage: Important Area Model for Tiger Salamander (Ambystoma tigrinum)
#   Dependency: IA_mod_palustrine.py
# Shall not be distributed without permission from the New York Natural Heritage Program
#   Edited: 2012 March 28
#   Edit: Update to arcpy module and incorporate into toolbox
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
arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True


ModelType = "Amphibians_TigerSalamander"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)

in_EOs = "in_EOs"
LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/_latest_results/" + ModelType + tyme + EXorHIST + ".shp"

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01EPAL_TGS'"
    IAmodel = "01EPAL_TGS"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HPAL_TGS'"
    IAmodel = "01HPAL_TGS"

arcpy.AddMessage("Tiger Salamander (Ambystoma tigrinum) model")

# Select out the proper EOs
arcpy.Select_analysis(in_put, in_EOs, selectQuery)
arcpy.AddMessage("In EOs selected. " + EXorHIST + " " + ModelType)

################### Buffer the EOs 340 meters
###################

arcpy.Buffer_analysis(in_EOs, "in_EOs_buff", 340, "FULL", "ROUND", "NONE", "")


################### Alis Roads
################### I had to place the select by attribute before the select by location, because there is a software
################### bug when you try to select by location on a very large SDE dataset. Sheesh.
arcpy.AddMessage("Selecting Roads....")
arcpy.MakeFeatureLayer_management("Database Connections/bloodhound.sde/AIMS.alisroads", "LAYER_alisroads")

arcpy.SelectLayerByAttribute_management("LAYER_alisroads", "NEW_SELECTION", "\"ACC\" = 1 OR \"ACC\" = 2 OR \"ACC\" = 3")
arcpy.SelectLayerByLocation_management("LAYER_alisroads", "INTERSECT", "in_EOs_buff", "", "SUBSET_SELECTION")

arcpy.MakeFeatureLayer_management("LAYER_alisroads", "LAYER_selected_alisroads")

arcpy.AddMessage("Buffering Selected Roads...")
arcpy.Buffer_analysis("LAYER_selected_alisroads", "Buff_alisroads", 6.25, "FULL", "ROUND", "ALL", "")

arcpy.AddMessage("Cut Wetland Buffers with Roads...")
arcpy.Erase_analysis("in_EOs_buff", "Buff_alisroads", "Erase_Wet")

################### Developed Land Use
###################

# Extracting the CCAP Developed, and Erasing the buffered wetlands with it.
arcpy.AddMessage("Select out high and medium intensity develed lands from CCAP....")
arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAP_developed", "\"VALUE\" = 2")
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management("LAYER_CCAP_developed", "LAYER_CCAP_developedpre")
arcpy.RasterToPolygon_conversion("LAYER_CCAP_developedpre", "polys_CCAP", "NO_SIMPLIFY", "VALUE")
arcpy.Dissolve_management("polys_CCAP", "polys_CCAPDissolve", "", "", "SINGLE_PART")
arcpy.AddMessage("Erase Developed Lands from Wetland Buffers...")
arcpy.Erase_analysis("Erase_Wet", "polys_CCAPDissolve", "Erase_CCAP")
arcpy.MultipartToSinglepart_management("Erase_CCAP","Erase_sp")

################### Remove areas above Peconic River barrier
###################

#arcpy.AddMessage("Select out high and medium intensity develed lands from CCAP....")
arcpy.MakeFeatureLayer_management("Erase_sp", "LAYER_Peconic")
arcpy.SelectLayerByLocation_management("LAYER_Peconic", "INTERSECT", "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/Peconic_Clip", "", "NEW_SELECTION")
arcpy.SelectLayerByAttribute_management("LAYER_Peconic", "SWITCH_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Peconic", "minusPeconic")

################### Eliminate matrine areas by clipping with county layer
###################

arcpy.Clip_analysis("minusPeconic", "m:/reg0/reg0data/base/borders/statemun/region.county", "No_Marine")

################### Aggregate polys and remove donut holes
###################

arcpy.MakeFeatureLayer_management("No_Marine", "LAYER_No_Marine")
arcpy.SelectLayerByLocation_management("LAYER_No_Marine", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_No_Marine", "Contiguous_Wet")

################### Union and Dissolve EOs back in
###################
arcpy.Union_analysis(in_EOs + " #; Contiguous_Wet #", "EOUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("EOUnion", "EODissolve", "", "", "SINGLE_PART")


################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("EODissolve", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("EODissolve", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("EODissolve", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 3000)

################### WRAP UP
################### 
arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Tiger Salamander.")

