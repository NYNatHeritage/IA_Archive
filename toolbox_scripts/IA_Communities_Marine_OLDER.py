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
LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT_2006"
CCAP_select = "CCAP_select"
CCAP_Select_Query = "VALUE = 13 OR VALUE = 14 OR VALUE = 15 OR VALUE = 17 OR VALUE = 18 OR VALUE = 22 OR VALUE = 23"

FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/_latest_results/" + ModelType + tyme + EXorHIST + ".shp"

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '03EMAR_G01'"
    IAmodel = "03EMAR_G01"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"

arcpy.AddMessage("Marine Communities model")


### Select out the proper EOs
##arcpy.Select_analysis(in_put, in_EOs, selectQuery)
##arcpy.AddMessage("In EOs selected. " + EXorHIST + " " + ModelType)
##
### Buffer EOs 100m
##arcpy.Buffer_analysis(in_EOs, "in_EOs100", 100, "FULL", "FLAT", "ALL", "")
### Clip the the shoreline
##arcpy.Clip_analysis(LIshore_line, "in_EOs100", "Shoreline")
##
### Selecting out bays vs. lands
##arcpy.MakeFeatureLayer_management(LIshore, "LAYER_LIshore")
##arcpy.SelectLayerByAttribute_management("LAYER_LIshore", "NEW_SELECTION", "\"TYPE\" = 'Bay'")
##arcpy.SelectLayerByLocation_management("LAYER_LIshore", "INTERSECT", "in_EOs100", "", "SUBSET_SELECTION")
##arcpy.CopyFeatures_management ("LAYER_LIshore", "in_bays")
##
### Buffer captured shoreline 200m
##arcpy.Buffer_analysis("in_bays", "in_bays200", 200, "FULL", "ROUND", "ALL", "")
##
### Buffer captured shoreline 200m
##arcpy.Buffer_analysis("Shoreline", "Shoreline_200", 200, "FULL", "ROUND", "ALL", "")
##
### Union bay buffs to shoreline buffs
##arcpy.Union_analysis(["in_bays200", in_EOs100, "Shoreline_200"], "ShoreUnion", "ONLY_FID", "", "NO_GAPS")
##
### Clip the unioned buffer with the shoreline
##arcpy.Clip_analysis("ShoreUnion", Shoreline_LINYC, "Shoreclip")
##
##################### Determine contiguous CCAP palustrine wetlands
#####################
##in_features = "Shoreclip"
##import IA_mod_lulc_select
##IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
##arcpy.AddMessage("LU/LC SELECT: CCAP Wetlands have been selected...")
 
# Union the input EOs and wetlands.
arcpy.Union_analysis(["Shoreclip", "in_EOs100", CCAP_select], "WetShoreUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("WetShoreUnion", "WetShoreDiss", "", "", "SINGLE_PART")







##arcpy.Buffer_analysis("LAYER_LIshore", "in_bays10", 10, "FULL", "FLAT", "ALL", "")
##
##
##
### Selecting out shoreline
##arcpy.MakeFeatureLayer_management(LIshore_line, "LAYER_LIshore_line")
##arcpy.SelectLayerByLocation_management("LAYER_LIshore_line", "INTERSECT", "in_EOs100", "", "NEW_SELECTION")
##arcpy.SelectLayerByLocation_management("LAYER_LIshore_line", "INTERSECT", "in_bays10", "", "ADD_TO_SELECTION")
##arcpy.CopyFeatures_management ("LAYER_LIshore_line", "Shoreline")

### Buffer EOs 200m, for now this simplifies capturing shoreline 200m from from the nearest shore, because no marine EOs are offshore
##arcpy.Buffer_analysis("Shoreline", "Shoreline_200", 200, "FULL", "ROUND", "ALL", "")

##### Clip the 200m buffer with the shoreline
####arcpy.Clip_analysis("Shoreline_200", "in_EOs_buff", "WetBuff")
####arcpy.AddMessage("Wetlands/Open Water, clipped.")

### Selecting out bays vs. lands
##arcpy.MakeFeatureLayer_management(LIshore, "LAYER_LIshore")
##arcpy.SelectLayerByAttribute_management("LAYER_LIshore", "NEW_SELECTION", "\"TYPE\" = 'Bay'")
##arcpy.SelectLayerByLocation_management("LAYER_LIshore", "INTERSECT", in_EOs, "", "SUBSET_SELECTION")
##arcpy.CopyFeatures_management ("LAYER_LIshore", "LIshore_Bay")



##arcpy.SelectLayerByAttribute_management("LAYER_LIshore", "NEW_SELECTION", "\"TYPE\" = 'Land'")
##arcpy.CopyFeatures_management ("LAYER_LIshore", "LIshore_Land")
##arcpy.AddMessage("Bays and Land, selected and separated.")
##
### Select bays
##arcpy.MakeFeatureLayer_management("LIshore_Bay", "LAYER_LIshore_Bay")
##arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "NEW_SELECTION", "\"SYSTEM\" = 'E'")
##arcpy.SelectLayerByLocation_management("LAYER_in_EOs", "INTERSECT", "LAYER_NWI_polys", "", "NEW_SELECTION")
##arcpy.CopyFeatures_management ("LAYER_in_EOs", "EstEOs")
##arcpy.SelectLayerByLocation_management("LAYER_in_EOs", "", "", "", "SWITCH_SELECTION")
##arcpy.CopyFeatures_management ("LAYER_in_EOs", "NoEstEOs")




####################### Determine contiguous CCAP palustrine wetlands
#######################
####in_features = in_EOs
####import IA_mod_lulc_select
####IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
####arcpy.AddMessage("LU/LC SELECT: CCAP Wetlands have been selected...")
#### 
##### Union the input EOs and wetlands.
####arcpy.Union_analysis([in_EOs, CCAP_select], "WetUnion", "ONLY_FID", "", "NO_GAPS")
####arcpy.Dissolve_management("WetUnion", "WetDiss", "", "", "SINGLE_PART")
##
##################### Run palustrine community module ###################
#####################
##value_field = "ORIG_ID"
##cell_size = 15
##in_buff = "in_EOsmp"
##in_buff_ring = "in_buff_ring"
##out_buff = "out_buff"
##
### Apply baseline buffer: 163m
##arcpy.MultipartToSinglepart_management(in_EOs, "in_EOsmp")
##arcpy.AddField_management("in_EOsmp", "ORIG_ID", "SHORT")
##arcpy.CalculateField_management("in_EOsmp", "ORIG_ID", "int(!OBJECTID!)", "PYTHON")
##arcpy.Buffer_analysis("in_EOsmp", in_buff_ring, 163, "FULL", "ROUND", "LIST", "ORIG_ID")
##
##import IA_mod_assessLCSLP
##IA_mod_assessLCSLP.ALCSLP_PALmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size)
##
##
##################### Aggregate and Dissolve all
#####################
### Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
### and came up with memory issues, so I just write to the final layer for now. 
###
##arcpy.AddField_management(out_buff, "IA_MODEL_R", "TEXT", "", "20")
##arcpy.CalculateField_management(out_buff, "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
##
##arcpy.Dissolve_management(out_buff, "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
##arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 3000)
##
##################### WRAP UP
##################### 
##arcpy.CopyFeatures_management ("Elim", FinalFC)
##arcpy.CopyFeatures_management ("Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Marine Communities.")






