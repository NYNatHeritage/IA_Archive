# ---------------------------------------------------------------------------
# IA_Birds_Woodland-Shrubland.py
# Created on: 2012 February
#   (script by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw and Jesse Jaycox, NYNHP)
# Usage: Woodland/Shrubland Birds
#   
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
arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Birds_WoodlandShrubland"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)



in_EOs = "in_EOs"
#LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
CCAP_Select_Query = "\"VALUE\" = 8 OR \"VALUE\" = 9 OR \"VALUE\" = 10 OR \"VALUE\" = 11 OR \"VALUE\" = 12 OR \"VALUE\" = 20"
NWI_wetlands = "M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\SDEADMIN.nc_nwi_poly_2016"
HectExpression = "float(!SHAPE.AREA@HECTARES!)"
#FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/_latest_results/" + ModelType + tyme + EXorHIST + ".shp"

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETER_WS1'"
    IAmodel = "01ETER_WS1"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"

print(ModelType + " model")

# Select out the proper EOs
arcpy.Select_analysis(in_put, in_EOs, selectQuery)
print("In EOs selected. " + EXorHIST + " " + ModelType)



################### Select Grasslands and Marsh from CCAP
###################
# Selecting Grassland and Marsh LULC
arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAP_select", CCAP_Select_Query)
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management("LAYER_CCAP_select", "CCAP_selectPre")
arcpy.RasterToPolygon_conversion("CCAP_selectPre", "CCAP_select", "NO_SIMPLIFY", "VALUE")

arcpy.AddField_management(in_EOs, "Hectares", "DOUBLE", "20")
arcpy.MultipartToSinglepart_management(in_EOs,"in_EOsMP")
arcpy.CalculateField_management("in_EOsMP", "Hectares", HectExpression, "PYTHON")
print("Hectares calculated.")

# Add field to assign a static ID
arcpy.AddField_management("in_EOsMP", "WSBIRD_ID", "SHORT")
arcpy.CalculateField_management("in_EOsMP", "WSBIRD_ID", "int(!OBJECTID!)", "PYTHON")

arcpy.Select_analysis("in_EOsMP", "Append_in_wsBirds", "Hectares >= 11")
arcpy.Select_analysis("in_EOsMP", "Working_in_wsBirds", "Hectares < 11")
print("Woodland/Shrubland bird EOs >= 61ha differentiated.")


################### Two loops - go through each EO, and buffer as many times as necessary to reach thresholds
###################

# BIG LOOP: Go through each EO =< hectare threshold

rows = arcpy.SearchCursor("Working_in_wsBirds")

for row in rows: 
    WSBIRD_ID = row.WSBIRD_ID
    rws_ID = repr(WSBIRD_ID)
    # Take out one of the <61ha EOs at a time, to get buffered
    arcpy.Select_analysis("Working_in_wsBirds", "GetBuffed", "WSBIRD_ID = " + rws_ID)
    arcpy.Copy_management("GetBuffed", "SelectedEOpoly")
    print("WSBIRD_ID = " + rws_ID)

    Dist = 50
    TotalDist = 5050 # This includes "Dist" value for killing the loop
#    ElimDist = 6070
    TotalDistm = 110000
    checkOne = 1
    countDist = 0
    # Smaller loop, buffer concentric rings
    while checkOne > 0:
        arcpy.Buffer_analysis("GetBuffed", "wsBirdsBuff", Dist, "FULL", "ROUND", "ALL", "")
        countDist = countDist + Dist
        print(repr(countDist) + " meters, buffering EO.")
        #Clip grass/marsh with bird buffer
        arcpy.Clip_analysis("CCAP_select", "wsBirdsBuff", "wsBirdsBuff_clip")
        #Dissolve them and prepare to test size - first as single part to eliminate 1.5 acre (0.6070309 ha) and smaller
        arcpy.Dissolve_management("wsBirdsBuff_clip", "wsDissolve1", "", "", "SINGLE_PART")
        # Run the preliminary swipe to see if contiguous habitat is >21 ha
        # This buffer is insignificant in dimension, but allows for kitty-corner cells to be counted
        # as adjacent. The only way I can find to capture kitty-corner cells.
        arcpy.Buffer_analysis("wsDissolve1", "polys_wDiss1", "1 Meters", "FULL", "ROUND", "ALL", "")
        arcpy.MultipartToSinglepart_management("polys_wDiss1", "polys_wDiss1SP")
        arcpy.MakeFeatureLayer_management("polys_wDiss1SP", "LAYER_WoodlandShrubland", "", "", "")
        arcpy.SelectLayerByLocation_management("LAYER_WoodlandShrubland", "INTERSECT", "in_EOsMP", "", "NEW_SELECTION")
        arcpy.Union_analysis(["SelectedEOpoly", "LAYER_WoodlandShrubland"], "WS_EO_Union", "ONLY_FID", "", "NO_GAPS")
        arcpy.Dissolve_management("WS_EO_Union", "WS_EO_Diss", "", "", "SINGLE_PART")
        arcpy.MakeFeatureLayer_management("WS_EO_Diss", "LAYER_wsDissolve2", "", "", "")
        # Select multipart EO/buffer >=61ha
        arcpy.SelectLayerByAttribute_management("LAYER_wsDissolve2", "NEW_SELECTION", "\"Shape_Area\" >= " + repr(TotalDistm))


        # Check for empty selection and, if so, buffer EO again, or hits the hectare or distance thresholds
        # and moves on to the next EO.
        results = arcpy.GetCount_management("LAYER_wsDissolve2")
        SelectCount = int(results.getOutput(0))
        print(repr(SelectCount) + " selected features.")
        if SelectCount == 0:
            checkOne = checkOne + 1
            print repr(checkOne) + " buffer attempts."
            arcpy.Copy_management("wsBirdsBuff", "GetBuffed")
            print("Feature " + repr(row.WSBIRD_ID) + " still not big enough.")
        else:
            checkOne = 0
            arcpy.Append_management("WS_EO_Diss", "Append_in_wsBirds", "NO_TEST")
            print("Feature " + repr(row.WSBIRD_ID) + " is big enough now, and appended.")
            print("checkOne = " + repr(checkOne) + " buffer attempts.")
            arcpy.SelectLayerByAttribute_management("LAYER_wsDissolve2", "CLEAR_SELECTION")
        if countDist >= TotalDist:
            checkOne = 0
            arcpy.Append_management("WS_EO_Diss", "Append_in_wsBirds", "NO_TEST")
            print("Feature " + repr(row.WSBIRD_ID) + " has reached 0.5km so now it is appended.")
            print("checkOne = " + repr(checkOne) + " buffer attempts.")

# Union back in the starting units of the 'too small, need buffer' polygons
arcpy.Union_analysis("in_EOs #; Append_in_wsBirds #; Working_in_wsBirds #", "wsUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("wsUnion", "Dissolve", "", "", "SINGLE_PART")


################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("Dissolve", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Dissolve", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("Dissolve", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 3000)

################### WRAP UP

FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST
################### 

arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", FinalFC_gdb)

print("IA model done: Woodland/Shrubland Birds.")



