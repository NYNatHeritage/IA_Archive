# ---------------------------------------------------------------------------
# IA_Birds_Woodland.py
# Created on: 2011 May
#   (script by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw and Jesse Jaycox, NYNHP)
# Usage: Important Area Model for NYNHP estuarine birds - woody tidal - communities
# Latest Edits: 
#   
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
arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Birds_Woodland"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)
#Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
CCAP_Select_Query = "VALUE = 9 OR VALUE = 11 OR VALUE = 13"
HectExpression = "float(!SHAPE.AREA@HECTARES!)"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETER_WB1'"
    IAmodel = "01ETER_WB1"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"
    
#if Proj == "DOT":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
#    
#elif Proj == "HRE Culverts":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"
#
#elif Proj == "All":
#    LULC = "C:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
#    StudyArea = "M:/reg0/reg0data/base/borders/statemun/region.state"
#    
#elif Proj == "HREP":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HREP"


print(ModelType + " model")


# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)
                              
##################### Select Woodlands from CCAP
#####################
# Selecting CCAP Wetlands, palustrine and estuarine, but not including water
attExtract = ExtractByAttributes(LULC, CCAP_Select_Query) 
attExtract.save("CCAP_WoodL")
arcpy.RasterToPolygon_conversion("CCAP_WoodL", "polys_WoodL", "NO_SIMPLIFY", "VALUE")
print("LU/LC selected...")

################### Calc Hectares and determine < or > 21 ha
###################

arcpy.AddField_management(in_EOs, "Hectares", "DOUBLE", "20")
arcpy.MultipartToSinglepart_management(in_EOs,"in_EOsMP")
arcpy.CalculateField_management("in_EOsMP", "Hectares", HectExpression, "PYTHON")
print("Hectares calculated...")

# Add field to assign a static ID
arcpy.AddField_management("in_EOsMP", "WBIRD_ID", "SHORT")
arcpy.CalculateField_management("in_EOsMP", "WBIRD_ID", "int(!OBJECTID!)", "PYTHON")

arcpy.Select_analysis("in_EOsMP", "Append_in_wBirds", "Hectares >= 21")
arcpy.Select_analysis("in_EOsMP", "Working_in_wBirds", "Hectares < 21")
print("Woodland bird EOs >= 61ha differentiated...")


################### Two loops - go through each EO, and buffer as many times as necessary to reach thresholds
###################

# BIG LOOP: Go through each EO =< hectare threshold

rows = arcpy.SearchCursor("Working_in_wBirds")

for row in rows: 
    WBIRD_ID = row.WBIRD_ID
    rw_ID = repr(WBIRD_ID)
    # Take out one of the <61ha EOs at a time, to get buffered
    arcpy.Select_analysis("Working_in_wBirds", "GetBuffed", "WBIRD_ID = " + rw_ID)
    arcpy.Copy_management("GetBuffed", "SelectedEOpoly")
    print("WBIRD_ID = " + rw_ID)

    Dist = 50
    TotalDist = 5050 # This includes "Dist" value for killing the loop
#    ElimDist = 6070
    TotalDistm = 210000
    checkOne = 1
    countDist = 0
    # Smaller loop, buffer concentric rings
    while checkOne > 0:
        arcpy.Buffer_analysis("GetBuffed", "wBirdsBuff", Dist, "FULL", "ROUND", "ALL", "")
        countDist = countDist + Dist
        print(repr(countDist) + " meters, buffering EO.")
        #Clip grass/marsh with bird buffer
        arcpy.Clip_analysis("polys_WoodL", "wBirdsBuff", "wBirdsBuff_clip")
        #Dissolve them and prepare to test size - first as single part to eliminate 1.5 acre (0.6070309 ha) and smaller
        arcpy.Dissolve_management("wBirdsBuff_clip", "wDissolve1", "", "", "SINGLE_PART")

        # Run the preliminary swipe to see if contiguous habitat is >21 ha
        # This buffer is insignificant in dimension, but allows for kitty-corner cells to be counted
        # as adjacent. The only way I can find to capture kitty-corner cells.
        arcpy.Buffer_analysis("wDissolve1", "polys_wDiss1", "1 Meters", "FULL", "ROUND", "ALL", "")
        arcpy.MultipartToSinglepart_management("polys_wDiss1", "polys_wDiss1SP")
        arcpy.MakeFeatureLayer_management("polys_wDiss1SP", "LAYER_Woodland", "", "", "")
        arcpy.SelectLayerByLocation_management("LAYER_Woodland", "INTERSECT", "in_EOsMP", "", "NEW_SELECTION")
        arcpy.Union_analysis(["SelectedEOpoly", "LAYER_Woodland"],"W_EO_Union", "ONLY_FID", "", "NO_GAPS")
        arcpy.Dissolve_management("W_EO_Union", "W_EO_Diss", "", "", "SINGLE_PART")
        arcpy.MakeFeatureLayer_management("W_EO_Diss", "LAYER_wDissolve2", "", "", "")
        # Select multipart EO/buffer >=61ha
        arcpy.SelectLayerByAttribute_management("LAYER_wDissolve2", "NEW_SELECTION", "\"Shape_Area\" >= " + repr(TotalDistm))


        # Check for empty selection and, if so, buffer EO again, or hits the hectare or distance thresholds
        # and moves on to the next EO.
        results = arcpy.GetCount_management("LAYER_wDissolve2")
        SelectCount = int(results.getOutput(0))
        print(repr(SelectCount) + " selected features.")
        if SelectCount == 0:
            checkOne = checkOne + 1
            print repr(checkOne) + " buffer attempts."
            arcpy.Copy_management("wBirdsBuff", "GetBuffed")
            print("Feature " + repr(row.WBIRD_ID) + " still not big enough.")
        else:
            checkOne = 0
            arcpy.Append_management("W_EO_Diss", "Append_in_wBirds", "NO_TEST")
            print("Feature " + repr(row.WBIRD_ID) + " is big enough now, and appended.")
            print("checkOne = " + repr(checkOne) + " buffer attempts.")
            arcpy.SelectLayerByAttribute_management("LAYER_wDissolve2", "CLEAR_SELECTION")
        if countDist >= TotalDist:
            checkOne = 0
            arcpy.Append_management("W_EO_Diss", "Append_in_wBirds", "NO_TEST")
            print("Feature " + repr(row.WBIRD_ID) + " has reached 0.5km so now it is appended.")
            print("checkOne = " + repr(checkOne) + " buffer attempts.")

# Union back in the starting units of the 'too small, need buffer' polygons
arcpy.Union_analysis("in_EOs #; Append_in_wBirds #; Working_in_wBirds #", "wUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("wUnion", "Dissolve", "", "", "SINGLE_PART")


################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("Dissolve", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Dissolve", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("Dissolve", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 1000000)

################### WRAP UP
################### 

FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST

arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", FinalFC_gdb)

print("IA model done: Woodland Birds.")




