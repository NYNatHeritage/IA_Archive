# ---------------------------------------------------------------------------
# IA_Birds_HenslowSparrow.py
# Created on: 2011 July
#   (script by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw and Jesse Jaycox, NYNHP)
# Usage: Important Area Model for NYNHP Hensow's Sparrow -
#           Ammodramus henslowii (Henslow’s Sparrow)
# Latest Edits: Update to arcpy module
#   
# This script shall not be distributed without permission from the New York Natural Heritage Program
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

ModelType = "Birds_HenslowSparrow"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)
Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
in_features = "in_EOs"
CCAP_select = "CCAP_select"
CCAP_Select_Query = "\"VALUE\" = 14 OR \"VALUE\" = 15"
DEC_wetlands = "DEC_wetlands"
NWI_select = "NWI_select"


AcreExpression = "float(!SHAPE.AREA@ACRES!)"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETPL_HES'"
    IAmodel = "01ETPL_HES"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"
    
if Proj == "DOT":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
    Roadblocks = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/ALIS_ACC1and2_DOT_poly"
    
elif Proj == "HRE Culverts":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"
    Roadblocks = "XXXXX"
    
elif Proj == "All":
    LULC = "C:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
    StudyArea = "M:/reg0/reg0data/base/borders/statemun/region.state"
    Roadblocks = "XXXXX"
    
elif Proj == "HREP":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HREP"
    Roadblocks = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/ALIS_ACC1and2_HREP_poly"

    
arcpy.AddMessage(ModelType + " model")


# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)
                              
################### Select Grasslands from CCAP
###################
#   Selecting CCAP Wetlands, palustrine and estuarine, but not including water
LAYER_CCAP_HSL = ExtractByAttributes(LULC, "\"VALUE\" = 7 OR \"VALUE\" = 8 OR \"VALUE\" = 20 OR \"VALUE\" = 5")
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management(LAYER_CCAP_HSL, "LAYER_CCAP_HSLpre")
arcpy.RasterToPolygon_conversion("LAYER_CCAP_HSLpre", "polys_HSL", "NO_SIMPLIFY", "VALUE")
arcpy.AddMessage("HSLands selected from CCAP")

################### Calc Acres
###################
arcpy.AddField_management(in_EOs, "Acres_", "DOUBLE", "20")
arcpy.CalculateField_management(in_EOs, "Acres_", AcreExpression, "PYTHON")
arcpy.AddMessage("Acres calculated.")

##################### Pull >= 133 acres out
#####################
arcpy.Select_analysis(in_EOs, "Append_in_HSBirds", "Acres_ >= 133")
arcpy.Select_analysis(in_EOs, "Working_in_HSBirds", "Acres_ < 133")
arcpy.AddMessage("Henslow Sparrow EOs >= 133 acres differentiated.")


################### Two loops - go through each EO, and buffer as many times as necessary to reach thresholds
###################

# BIG LOOP: Go through each EO =< hectare threshold

rows = arcpy.SearchCursor("Working_in_HSBirds")

for row in rows: 

    EO_ID = row.EO_ID
    rEO_ID = repr(EO_ID)
    # Take out one of the <61ha EOs at a time, to get buffered
    arcpy.Select_analysis("Working_in_HSBirds", "GetBuffed", "EO_ID = " + rEO_ID)

    Dist = 20
    TotalDist = 520 # This includes "Dist" value for killing the loop
    TotalDistm = 538234
    checkOne = 1
    countDist = 0

    # Create a 'roadblock' to clip the features with (we do not want buffer rings to go past ACC = 1 or 2 roads
    arcpy.MakeFeatureLayer_management(Roadblocks, "LAYER_Roadblocks")
    arcpy.SelectLayerByLocation_management("LAYER_Roadblocks", "INTERSECT", "GetBuffed", "", "NEW_SELECTION")

    # Smaller loop, buffer concentric rings
    while checkOne > 0:
        arcpy.Buffer_analysis("GetBuffed", "HSBirdsBuff", Dist, "FULL", "ROUND", "ALL", "")
        countDist = countDist + Dist
        arcpy.AddMessage(repr(countDist) + " meters, buffering EO.")
        #Clip HSLands with bird EO buffer
        arcpy.Clip_analysis("polys_HSL", "HSBirdsBuff", "HSBirdsbuff_clip")
        #Clip previous clip with roadless block
        arcpy.Clip_analysis("HSBirdsbuff_clip", "LAYER_Roadblocks", "HSBirds_clip")
        #Union them and prepare to test size
        arcpy.Union_analysis("GetBuffed #; HSBirds_clip #", "HSUnion", "ONLY_FID", "", "NO_GAPS")
        arcpy.Dissolve_management("HSUnion", "HSDissolve", "", "", "MULTI_PART")
        arcpy.MakeFeatureLayer_management("HSDissolve", "LAYER_HSDissolve", "", "", "")
        # Select multipart EO/buffer >=61ha
        arcpy.SelectLayerByAttribute_management("LAYER_HSDissolve", "NEW_SELECTION", "\"Shape_Area\" >= " + repr(TotalDistm))

        # Check for empty selection and, if so, buffer EO again, or hits the hectare or distance thresholds
        # and moves on to the next EO.
        results = arcpy.GetCount_management("LAYER_HSDissolve")
        SelectCount = int(results.getOutput(0))
        arcpy.AddMessage(repr(SelectCount) + " selected features.")
        if SelectCount == 0:
            checkOne = checkOne + 1
            arcpy.AddMessage(repr(checkOne) + " buffer attempts.")
            arcpy.Copy_management("HSDissolve", "GetBuffed")
            arcpy.AddMessage("Feature " + repr(row.EO_ID) + " still not big enough.")
        else:
            checkOne = 0
            arcpy.Append_management("HSDissolve", "Append_in_HSBirds", "NO_TEST")
            arcpy.AddMessage("Feature " + repr(row.EO_ID) + " is big enough now, and appended.")
            arcpy.AddMessage("checkOne = " + repr(checkOne) + " buffer attempts.")
            arcpy.SelectLayerByAttribute_management("LAYER_HSDissolve", "CLEAR_SELECTION")
        if countDist >= TotalDist:
            checkOne = 0
            arcpy.Append_management("HSDissolve", "Append_in_HSBirds", "NO_TEST")
            arcpy.AddMessage("Feature " + repr(row.EO_ID) + " has reached 0.5km so now it is appended.")
            arcpy.AddMessage("checkOne = " + repr(checkOne) + " buffer attempts.")

# Select CCAP wetlands
import IA_mod_lulc_select
IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
arcpy.AddMessage("LU/LC SELECT: CCAP Wetlands have been selected.")

arcpy.AddMessage("Going into DEC Wetlands...")
# Select DEC wetlands
import IA_mod_lulc_select
IA_mod_lulc_select.DEC_wetlands(in_features, DEC_wetlands, WSP)
arcpy.AddMessage("LU/LC SELECT: DEC Wetlands have been selected.")

# Select out NWI wetlands
import IA_mod_lulc_select
IA_mod_lulc_select.NWI_polys(in_features, NWI_select, WSP)
# Selecting out the lacustrine and palustrine NWI wetlands
arcpy.MakeFeatureLayer_management(NWI_select, "LAYER_NWI_polys")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "NEW_SELECTION", "\"SYSTEM\" = 'E' OR \"SYSTEM\" = 'P'")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "REMOVE_FROM_SELECTION", "\"NWI_CODE\" = 'E1UBL'")
arcpy.CopyFeatures_management ("LAYER_NWI_polys", "NWI_wet_polys")

# Union and Dissolve EOs back in
arcpy.Union_analysis([in_EOs, "NWI_wet_polys", CCAP_select, DEC_wetlands, "Append_in_HSBirds"], "EOUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("EOUnion", "Dissolve", "", "", "SINGLE_PART")

# This buffer is insignificant in dimension, but allows for kitty-corner cells to be counted
# as adjacent. The only way I can find to capture kitty-corner cells.
arcpy.Buffer_analysis("Dissolve", "polys_Elim", "1 Meters", "FULL", "ROUND", "ALL", "")
arcpy.MultipartToSinglepart_management("polys_Elim", "polys_ElimSP")
arcpy.MakeFeatureLayer_management("polys_ElimSP", "LAYER_polys_ElimSP", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_polys_ElimSP", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_polys_ElimSP", "Contiguous")

################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("Contiguous", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Contiguous", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("Contiguous", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 1000000)



################### WRAP UP
################### 
arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Henslow Sparrow.")


