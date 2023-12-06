# IA_blandings_turtle.py
# Created on: 2013 February 6 2013
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Jesse Jaycox, former Zoologist, NYNHP, and revised by Hollie Shaw, NYNHP)
# Usage: Important Area Model for Blandings Turtle (Emydoidea blandingii)
# Shall not be distributed without permission from the New York Natural Heritage Program
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
arcpy.env.workspace = arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Reptiles_BlandingsTurtle"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)
#Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
BuffDist = "1000"
Hydro24K = "M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\ARCS.surfwatr"
Hydro24Kline = "M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\ARCS.hydro24_strmnet"
in_features = "in_EOs_buff"
DEC_wetlands = "DEC_wetlands"
NWI_select = "NWI_select"
NWI_select_lines = "NWI_select_lines"
StatewideEOs = "W:/GIS_Data/EO_Mapping/_statewide_EOs/statewide_eos.shp"
#FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01EPAL_BLT'"
    IAmodel = "01EPAL_BLT"
##ARE WE DOING HISTORICALS? ##elif EXorHIST == "Historical":
##    selectQuery = "IA_MODEL = 'XXXXX'"
##    IAmodel = "XXXXX"

#if Proj == "DOT":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
#elif Proj == "HRE Culverts":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
#elif Proj == "HREP":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"    



print("Blandings Turtle (Emydoidea blandingii) model")

##### Select out the proper EOs
arcpy.Select_analysis(in_put, in_EOs, selectQuery)
print("In EOs selected. " + EXorHIST + " " + ModelType)

##### Buffer the EOs, 1.0km
arcpy.Buffer_analysis(in_EOs, "in_EOs_buff", BuffDist, "FULL", "ROUND", "ALL")

##### Determine contiguous 1:24K surface hydrography
print("Determine contiguous 1:24K Surface Hydrography")
# Hydro24K, line features:
print("Selecting Hydro24K lines...")
arcpy.MakeFeatureLayer_management(Hydro24Kline, "LAYER_Hydro24Kline")
arcpy.SelectLayerByAttribute_management("LAYER_Hydro24Kline", "NEW_SELECTION", "\"MAJOR1\" = 50")
arcpy.SelectLayerByLocation_management("LAYER_Hydro24Kline", "INTERSECT", "in_EOs_buff", "", "SUBSET_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Hydro24Kline", "SelectedHydro")
arcpy.Clip_analysis("SelectedHydro", "in_EOs_buff", "SelectedHydro24Kline")
print("LAYER_Hydro24K lines have been selected.") 
# Buffer them the 1:24K mmu so they become polys
arcpy.Buffer_analysis("SelectedHydro24Kline", "Hydro24Kline_buff", 6.25, "FULL", "ROUND", "ALL", "")
print("Hydro 24K lines have been buffered the mmu.")

##### Determine contiguous DEC wetlands
import IA_mod_lulc_select
IA_mod_lulc_select.DEC_wetlands(in_features, DEC_wetlands, WSP)
print("LU/LC SELECT: DEC Wetlands have been selected...")

##### Determine contiguous NWI wetlands, first polys, and then lines
# Select out NWI wetland polys
import IA_mod_lulc_select
IA_mod_lulc_select.NWI_polys(in_features, NWI_select, WSP)
arcpy.MakeFeatureLayer_management(NWI_select, "LAYER_NWI_polys")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "NEW_SELECTION", "\"ATTRIBUTE\" LIKE 'R%' OR \"ATTRIBUTE\" LIKE 'P%'OR \"ATTRIBUTE\" LIKE 'L%'")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "SUBSET_SELECTION", "\"ATTRIBUTE\" NOT LIKE '%V%'")
arcpy.CopyFeatures_management ("LAYER_NWI_polys", "NWI_wet_polys")
print("NWI Wetland polys have been selected...")
# Select out NWI wetland lines
import IA_mod_lulc_select
IA_mod_lulc_select.NWI_lines(in_features, NWI_select_lines, WSP)
arcpy.MakeFeatureLayer_management(NWI_select_lines, "LAYER_NWI_lines")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_lines", "NEW_SELECTION", "\"SYSTEM\" = 'R' OR \"SYSTEM\" = 'P'OR \"SYSTEM\" = 'L'")
arcpy.CopyFeatures_management ("LAYER_NWI_lines", "NWI_wet_l")
arcpy.Clip_analysis("NWI_wet_l", "in_EOs_buff", "NWI_wet_lines")
print("NWI Wetland polys have been selected...")
# Buffer them the 1:24K mmu so they become polys
print "NWI Wetland lines have been selected."
arcpy.Buffer_analysis("NWI_wet_lines", "NWI_wetland_lines_buff", 6.25, "FULL", "ROUND", "ALL", "")
print("NWI Wetland lines have been selected...")

##### Capture palustrine EOs in the buffer
print("Capture palustrine EOs in the buffer")
# EO palustrine features:
print("Selecting EOs...")
arcpy.MakeFeatureLayer_management(StatewideEOs, "LAYER_StatewideEOs")
arcpy.SelectLayerByAttribute_management("LAYER_StatewideEOs", "NEW_SELECTION", "\"EOCODE\" LIKE 'CPAL%'")
arcpy.SelectLayerByLocation_management("LAYER_StatewideEOs", "INTERSECT", "in_EOs_buff", "", "SUBSET_SELECTION")
arcpy.CopyFeatures_management ("LAYER_StatewideEOs", "SelectedEOs")
print("LAYER_StatewideEOs have been selected.") 

##### Union and Dissolve all wetlands for palustrine community model
print("Unioning and dissolving EOs and Wetlands...")
####arcpy.Union_analysis([in_EOs, "SelectedEOs", "NWI_wetland_lines_buff", "Hydro24Kline_buff", DEC_wetlands, "NWI_wet_polys"], "WetUnionPAL", "ONLY_FID", "", "NO_GAPS")
arcpy.Merge_management([in_EOs, "SelectedEOs", "NWI_wetland_lines_buff", "Hydro24Kline_buff", DEC_wetlands, "NWI_wet_polys"], "WetUnionPAL")
arcpy.Dissolve_management("WetUnionPAL", "WetDissolvePAL", "", "", "SINGLE_PART")

##### Run palustrine community module
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

##### Union and Dissolve all wetlands for palustrine community model
print("Unioning and dissolving EOs and Wetlands...")
arcpy.Union_analysis(["in_EOs_buff", out_buff], "WUEObuff", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("WUEObuff", "WetUnionEObuff", "", "", "SINGLE_PART")


##### ALIS Roads 
# I had to place the select by attribute before the select by location, because there is a software
# bug when you try to select by location on a very large SDE dataset. Sheesh.
print("Selecting Roads....")
arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\AIMS.alisroads", "LAYER_alisroads")
arcpy.SelectLayerByAttribute_management("LAYER_alisroads", "NEW_SELECTION", "\"ACC\" = 1 OR \"ACC\" = 2")
arcpy.SelectLayerByLocation_management("LAYER_alisroads", "INTERSECT", "WetUnionEObuff", "", "SUBSET_SELECTION")
arcpy.MakeFeatureLayer_management("LAYER_alisroads", "LAYER_selected_alisroads")
print("Buffering Selected Roads...")
arcpy.Buffer_analysis("LAYER_selected_alisroads", "Buff_alisroads", 6.25, "FULL", "ROUND", "ALL", "")
print("Cut Wetland Buffers with Roads...")
arcpy.Erase_analysis("WetUnionEObuff", "Buff_alisroads", "Erase_Wet")

##### Aggregate polys and remove donut holes
arcpy.MultipartToSinglepart_management("Erase_Wet","Erase_Wet_sp")
arcpy.MakeFeatureLayer_management("Erase_Wet_sp", "LAYER_Erase_Wet_sp")
arcpy.SelectLayerByLocation_management("LAYER_Erase_Wet_sp", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Erase_Wet_sp", "Contiguous_Wet")

##### Union and Dissolve EOs back in
arcpy.Union_analysis(in_EOs + " #; Contiguous_Wet #", "EOUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("EOUnion", "Dissolve", "", "", "SINGLE_PART")

##### Aggregate and Dissolve all
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
arcpy.AddField_management("Dissolve", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Dissolve", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management("Dissolve", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 1000000)
arcpy.MakeFeatureLayer_management("Elim", "LAYER_Elim")
arcpy.SelectLayerByLocation_management("LAYER_Elim", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Elim", "Contiguous_bland")

##### WRAP UP
FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST

arcpy.CopyFeatures_management ("Contiguous_bland", FinalFC)
arcpy.CopyFeatures_management ("Contiguous_bland", FinalFC_gdb)

print("IA model done: Blandings Turtle.")
