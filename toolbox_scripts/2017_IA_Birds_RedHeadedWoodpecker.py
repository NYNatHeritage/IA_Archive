# ---------------------------------------------------------------------------
# IA_Birds_RedHeadedWoodpecker.py
# Created on: 2013 March
#   (script by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Erin White, Hollie Shaw, and Jesse Jaycox, NYNHP)
# Usage: Important Area Model for NYNHP Red-headed Woodpecker -
# Latest Edits:
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
arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Birds_RedHeadedWoodpecker"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)
#Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
HectExpression = "float(!SHAPE.AREA@HECTARES!)"

Roadblocks = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/ALIS_ACC1and2_HREP_poly"
if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETPL_RHW'"
    IAmodel = "01ETPL_RHW"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"
    
#if Proj == "DOT":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
#    Roadblocks = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/ALIS_ACC1and2_DOT_poly"
#    
#elif Proj == "HRE Culverts":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"
#    Roadblocks = "XXXXX"
#    
#elif Proj == "All":
#    LULC = "C:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
#    StudyArea = "M:/reg0/reg0data/base/borders/statemun/region.state"
#    Roadblocks = "XXXXX"
#    
#elif Proj == "HREP":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HREP"
#    Roadblocks = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/ALIS_ACC1and2_HREP_poly"

    
print(ModelType + " model")


# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)
                              
################### Select codes from CCAP
###################
#   Selecting CCAP Wetlands, palustrine and estuarine, but not including water
LAYER_CCAP_GrassL = ExtractByAttributes(LULC, "\"VALUE\" = 7 OR \"VALUE\" = 8 OR \"VALUE\" = 9 OR \"VALUE\" = 11 OR \"VALUE\" = 13 OR \"VALUE\" = 14")
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management(LAYER_CCAP_GrassL, "LAYER_CCAP_GrassLpre")
arcpy.RasterToPolygon_conversion("LAYER_CCAP_GrassLpre", "polys_GrassL", "NO_SIMPLIFY", "VALUE")
print("Grasslands selected from CCAP")

################### Calc Hectares
###################
arcpy.AddField_management(in_EOs, "Hectares", "DOUBLE", "20")
arcpy.CalculateField_management(in_EOs, "Hectares", HectExpression, "PYTHON")
print("Hectares calculated.")

##################### Pull >= 8.5Ha out
#####################
arcpy.Select_analysis(in_EOs, "Append_in_GBirds", "Hectares >= 8.5")
arcpy.Select_analysis(in_EOs, "Working_in_GBirds", "Hectares < 8.5")
print("Grassland bird EOs >= 8.5ha differentiated.")


################### Two loops - go through each EO, and buffer as many times as necessary to reach thresholds
###################

# BIG LOOP: Go through each EO =< hectare threshold

rows = arcpy.SearchCursor("Working_in_GBirds")

for row in rows: 

    EO_ID = row.EO_ID
    rEO_ID = repr(EO_ID)
    # Take out one of the <61ha EOs at a time, to get buffered
    arcpy.Select_analysis("Working_in_GBirds", "GetBuffed", "EO_ID = " + rEO_ID)

    Dist = 20
    TotalDist = 520 # This includes "Dist" value for killing the loop
    TotalDistm = 85000
    checkOne = 1
    countDist = 0

    # Create a 'roadblock' to clip the features with (we do not want buffer rings to go past ACC = 1 or 2 roads
    # Originally written for grassland birds, but no roadblock called for w/rh woodpecker so substitute the study area
    # for roadblocks
    # arcpy.MakeFeatureLayer_management(Roadblocks, "LAYER_Roadblocks")
    arcpy.MakeFeatureLayer_management(StudyArea, "LAYER_Roadblocks")
    arcpy.SelectLayerByLocation_management("LAYER_Roadblocks", "INTERSECT", "GetBuffed", "", "NEW_SELECTION")

    # Smaller loop, buffer concentric rings
    while checkOne > 0:
        arcpy.Buffer_analysis("GetBuffed", "GBirdsBuff", Dist, "FULL", "ROUND", "ALL", "")
        countDist = countDist + Dist
        print(repr(countDist) + " meters, buffering EO.")
        #Clip grasslands with bird EO buffer
        arcpy.Clip_analysis("polys_GrassL", "GBirdsBuff", "GBirdsbuff_clip")
        #Clip previous clip with roadless block
        arcpy.Clip_analysis("GBirdsbuff_clip", "LAYER_Roadblocks", "GBirds_clip")
        #Union them and prepare to test size
        arcpy.Union_analysis("GetBuffed #; GBirds_clip #", "GrassUnion", "ONLY_FID", "", "NO_GAPS")
        arcpy.Dissolve_management("GrassUnion", "GrassDissolve", "", "", "MULTI_PART")
        arcpy.MakeFeatureLayer_management("GrassDissolve", "LAYER_GrassDissolve", "", "", "")
        # Select multipart EO/buffer >=8.5ha
        arcpy.SelectLayerByAttribute_management("LAYER_GrassDissolve", "NEW_SELECTION", "\"Shape_Area\" >= " + repr(TotalDistm))

        # Check for empty selection and, if so, buffer EO again, or hits the hectare or distance thresholds
        # and moves on to the next EO.
        results = arcpy.GetCount_management("LAYER_GrassDissolve")
        SelectCount = int(results.getOutput(0))
        print(repr(SelectCount) + " selected features.")
        if SelectCount == 0:
            checkOne = checkOne + 1
            print(repr(checkOne) + " buffer attempts.")
            arcpy.Copy_management("GrassDissolve", "GetBuffed")
            print("Feature " + repr(row.EO_ID) + " still not big enough.")
        else:
            checkOne = 0
            arcpy.Append_management("GrassDissolve", "Append_in_GBirds", "NO_TEST")
            print("Feature " + repr(row.EO_ID) + " is big enough now, and appended.")
            print("checkOne = " + repr(checkOne) + " buffer attempts.")
            arcpy.SelectLayerByAttribute_management("LAYER_GrassDissolve", "CLEAR_SELECTION")
        if countDist >= TotalDist:
            checkOne = 0
            arcpy.Append_management("GrassDissolve", "Append_in_GBirds", "NO_TEST")
            print("Feature " + repr(row.EO_ID) + " has reached 0.5km so now it is appended.")
            print("checkOne = " + repr(checkOne) + " buffer attempts.")


# This buffer is insignificant in dimension, but allows for kitty-corner cells to be counted
# as adjacent. The only way I can find to capture kitty-corner cells.
arcpy.Buffer_analysis("Append_in_GBirds", "polys_Elim", "1 Meters", "FULL", "ROUND", "ALL", "")
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

FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST


arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", FinalFC_gdb)

print("IA model done: RedHeaded Woodpecker.")


