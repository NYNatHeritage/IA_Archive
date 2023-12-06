# ---------------------------------------------------------------------------
# IA_Reptiles_EasternMudTurtle.py
# Created on: 2010 November 18
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw, Zoologist, NYNHP)
# Usage: Important Area Model for Eastern Mud Turtle (Kinosternon subrubrum)
# Shall not be distributed without permission from the New York Natural Heritage Program
#   Edited: 2012 April 5
#   Edit: Update snapraster and standardize for appending 
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

ModelType = "Reptiles_EMudTurtle"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)


in_EOs = "in_EOs"
BuffDist = "250 Meters"
LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
Hydro24K = "Database Connections/Bloodhound.sde/ARCS.surfwatr"
Hydro24Kline = "Database Connections/Bloodhound.sde/ARCS.hydro24_strmnet"
in_features = "in_EOs_buff"
CCAP_select = "CCAP_select"
CCAP_Select_Query = "VALUE = 13 OR VALUE = 14 OR VALUE = 15, OR VALUE = 16, OR VALUE = 17, OR VALUE = 18, OR VALUE = 19, OR VALUE = 22, OR VALUE = 23"
DEC_wetlands = "DEC_wetlands"
NWI_select = "NWI_select"
NWI_select_lines = "NWI_select_lines"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/_latest_results/" + ModelType + tyme + EXorHIST + ".shp"

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01EPES_EMT'"
    IAmodel = "01EPES_EMT"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"

arcpy.AddMessage("Eastern Mud Turtle (Kinosternon subrubrum) model")


# Select out the proper EOs
arcpy.Select_analysis(in_put, in_EOs, selectQuery)
arcpy.AddMessage("In EOs selected. " + EXorHIST + " " + ModelType)

################### Buffer the EOs
###################
arcpy.Buffer_analysis(in_EOs, "in_EOs_buff", BuffDist, "FULL", "ROUND", "NONE", "")


################### Determine contiguous 1:24K surface hydrography
################### 
arcpy.AddMessage("Determine contiguous 1:24K Surface Hydrography")

# Hydro24K, poly features:
# Call out function:
arcpy.AddMessage("Selecting Hydro24K...")

arcpy.MakeFeatureLayer_management(Hydro24K, "LAYER_Hydro24K")
arcpy.SelectLayerByAttribute_management("LAYER_Hydro24K", "NEW_SELECTION", "\"MAJOR1\" = 50")
arcpy.SelectLayerByLocation_management("LAYER_Hydro24K", "INTERSECT", "in_EOs_buff", "", "SUBSET_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Hydro24K", "Hydro24K_polys")
arcpy.AddMessage("LAYER_Hydro24K have been selected.")

# Hydro24K, line features:
# Call out function:
print "Selecting Hydro24K lines..."

arcpy.MakeFeatureLayer_management(Hydro24Kline, "LAYER_Hydro24Kline")
arcpy.SelectLayerByAttribute_management("LAYER_Hydro24Kline", "NEW_SELECTION", "\"MAJOR1\" = 50")
arcpy.SelectLayerByLocation_management("LAYER_Hydro24Kline", "INTERSECT", "in_EOs_buff", "", "SUBSET_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Hydro24Kline", "SelectedHydro24Kline")
arcpy.AddMessage("LAYER_Hydro24K lines have been selected.") 
# Buffer them the 1:24K mmu so they become polys
arcpy.Buffer_analysis("SelectedHydro24Kline", "Hydro24Kline_buff", 6.25, "FULL", "ROUND", "ALL", "")
arcpy.AddMessage("Hydro 24K lines have been buffered the mmu.")

################### Determine contiguous CCAP palustrine wetlands
################### 
import IA_mod_lulc_select
IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
arcpy.AddMessage("LU/LC SELECT: CCAP Wetlands have been selected...")

################### Determine contiguous DEC wetlands
################### 
import IA_mod_lulc_select
IA_mod_lulc_select.DEC_wetlands(in_features, DEC_wetlands, WSP)
arcpy.AddMessage("LU/LC SELECT: DEC Wetlands have been selected...")


################### Determine contiguous NWI wetlands, first polys, and then lines
################### 
# Select out NWI wetland polys
import IA_mod_lulc_select
IA_mod_lulc_select.NWI_polys(in_features, NWI_select, WSP)

arcpy.MakeFeatureLayer_management(NWI_select, "LAYER_NWI_polys")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "NEW_SELECTION", "\"SYSTEM\" = 'L' OR \"SYSTEM\" = 'R' OR \"SYSTEM\" = 'P'")
arcpy.CopyFeatures_management ("LAYER_NWI_polys", "NWI_wet_polys")
arcpy.AddMessage("NWI Wetland polys have been selected...")

# Select out NWI wetland lines
import IA_mod_lulc_select
IA_mod_lulc_select.NWI_lines(in_features, NWI_select_lines, WSP)

arcpy.MakeFeatureLayer_management(NWI_select_lines, "LAYER_NWI_lines")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_lines", "NEW_SELECTION", "\"SYSTEM\" = 'L' OR \"SYSTEM\" = 'R' OR \"SYSTEM\" = 'P'")
arcpy.CopyFeatures_management ("LAYER_NWI_lines", "NWI_wet_lines")
arcpy.AddMessage("NWI Wetland polys have been selected...")

# Buffer them the 1:24K mmu so they become polys
print "NWI Wetland lines have been selected."
arcpy.Buffer_analysis("NWI_wet_lines", "NWI_wetland_lines_buff", 6.25, "FULL", "ROUND", "ALL", "")
arcpy.AddMessage("NWI Wetland lines have been selected...")


################### Union and Dissolve all PALUSTRINE ###################
###################
# Union the three parts: the input EOs, the 163 buffer, and the final extra buffer.
print "Unioning and dissolving EOs and Wetlands..."
arcpy.Union_analysis(["in_EOs_buff", CCAP_select, "NWI_wetland_lines_buff", "Hydro24K_polys", "Hydro24Kline_buff", DEC_wetlands, "NWI_wet_polys"], "WetUnionPAL", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("WetUnionPAL", "WetDissolvePAL", "", "", "SINGLE_PART")


################### Run palustrine community module ###################
###################
value_field = "ORIG_ID"
cell_size = 15
in_buff = "WetDissolvePAL"
in_buff_ring = "in_buff_ring"
out_buff = "out_buff"

# Apply baseline buffer: 163m
arcpy.AddField_management("WetDissolvePAL", "ORIG_ID", "SHORT")
arcpy.CalculateField_management("WetDissolvePAL", "ORIG_ID", "int(!OBJECTID!)", "PYTHON")
arcpy.Buffer_analysis("WetDissolvePAL", in_buff_ring, 163, "FULL", "ROUND", "LIST", "ORIG_ID")

import IA_mod_assessLCSLP
IA_mod_assessLCSLP.ALCSLP_PALmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size)


################### Alis Roads ###################
################### I had to place the select by attribute before the select by location, because there is a software
################### bug when you try to select by location on a very large SDE dataset. Sheesh.
arcpy.AddMessage("Selecting Roads....")
arcpy.MakeFeatureLayer_management("Database Connections/bloodhound.sde/AIMS.alisroads", "LAYER_alisroads")

arcpy.SelectLayerByAttribute_management("LAYER_alisroads", "NEW_SELECTION", "\"ACC\" = 1 OR \"ACC\" = 2 OR \"ACC\" = 3")
arcpy.SelectLayerByLocation_management("LAYER_alisroads", "INTERSECT", out_buff, "", "SUBSET_SELECTION")

arcpy.MakeFeatureLayer_management("LAYER_alisroads", "LAYER_selected_alisroads")

arcpy.AddMessage("Buffering Selected Roads...")
arcpy.Buffer_analysis("LAYER_selected_alisroads", "Buff_alisroads", 6.25, "FULL", "ROUND", "ALL", "")

arcpy.AddMessage("Cut Wetland Buffers with Roads...")
arcpy.Erase_analysis(out_buff, "Buff_alisroads", "Erase_Wet")

####################### Eliminate marine areas by clipping with county layer
#####################
arcpy.Clip_analysis("Erase_Wet", "m:/reg0/reg0data/base/borders/statemun/region.county", "No_Marine")

################### Aggregate polys and remove donut holes
###################
arcpy.MultipartToSinglepart_management("No_Marine","No_Marine_sp")
arcpy.MakeFeatureLayer_management("No_Marine_sp", "LAYER_No_Marine_sp")
arcpy.SelectLayerByLocation_management("LAYER_No_Marine_sp", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_No_Marine_sp", "Contiguous_Wet")

################### Developed Land Use
###################

#   Extracting the CCAP Developed, and Erasing the buffered wetlands with it.
arcpy.AddMessage("Select out high and medium intensity develed lands from CCAP....")
arcpy.MakeRasterLayer_management("W:/GIS_Data/LU_LC/ccap/2005/ccap2005ny", "LAYER_CCAP_developed", "\"VALUE\" = 2 OR \"VALUE\" = 3")
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management("LAYER_CCAP_developed", "LAYER_CCAP_developedpre")
arcpy.RasterToPolygon_conversion("LAYER_CCAP_developedpre", "polys_CCAP", "NO_SIMPLIFY", "VALUE")
arcpy.Dissolve_management("polys_CCAP", "polys_CCAPDissolve", "", "", "SINGLE_PART")
arcpy.AddMessage("Erase Developed Lands from Wetland Buffers...")
arcpy.Erase_analysis("Contiguous_Wet", "polys_CCAPDissolve", "Erase_CCAP")
arcpy.MultipartToSinglepart_management("Erase_CCAP","Erase_CCAP_sp")
arcpy.MakeFeatureLayer_management("Erase_CCAP_sp", "LAYER_Erase_CCAP")
arcpy.SelectLayerByLocation_management("LAYER_Erase_CCAP", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Erase_CCAP", "ContiguousIA")

################### Union and Dissolve EOs back in
###################
arcpy.Union_analysis(in_EOs + " #; ContiguousIA #", "EOUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("EOUnion", "Dissolve", "", "", "SINGLE_PART")

################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("Dissolve", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Dissolve", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("Dissolve", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 3000)

arcpy.MakeFeatureLayer_management("Elim", "LAYER_Elim")
arcpy.SelectLayerByLocation_management("LAYER_Elim", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Elim", "Contiguous_Mud")

################### WRAP UP
################### 
arcpy.CopyFeatures_management ("Contiguous_Mud", FinalFC)
arcpy.CopyFeatures_management ("Contiguous_Mud", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Eastern Mud Turtle.")



