# ---------------------------------------------------------------------------
# IA_Birds_Grassland.py
# Created on: 2011 July
#   (script by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw and Jesse Jaycox, NYNHP)
# Usage: Important Area Model for NYNHP grassland birds -
#           Ammodramus henslowii (Henslow�s Sparrow), Bartramia longicauda (Upland Sandpiper)
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

ModelType = "Birds_Grassland"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)
Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
HectExpression = "float(!SHAPE.AREA@HECTARES!)"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETER_GRB'"
    IAmodel = "01ETER_GRB"
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
LAYER_CCAP_GrassL = ExtractByAttributes(LULC, "\"VALUE\" = 7 OR \"VALUE\" = 8 OR \"VALUE\" = 20 OR \"VALUE\" = 5 OR \"VALUE\" = 4 OR \"VALUE\" = 6")
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management(LAYER_CCAP_GrassL, "LAYER_CCAP_GrassLpre")
arcpy.RasterToPolygon_conversion("LAYER_CCAP_GrassLpre", "polys_GrassL", "NO_SIMPLIFY", "VALUE")
arcpy.AddMessage("Grasslands selected from CCAP")

################### Calc Hectares
###################
arcpy.AddField_management(in_EOs, "Hectares", "DOUBLE", "20")
arcpy.CalculateField_management(in_EOs, "Hectares", HectExpression, "PYTHON")
arcpy.AddMessage("Hectares calculated.")

##################### Pull >= 61Ha out
#####################
arcpy.Select_analysis(in_EOs, "Append_in_GBirds", "Hectares >= 61")
arcpy.Select_analysis(in_EOs, "Working_in_GBirds", "Hectares < 61")
arcpy.AddMessage("Grassland bird EOs >= 61ha differentiated.")


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
    TotalDistm = 610000
    checkOne = 1
    countDist = 0

    # Create a 'roadblock' to clip the features with (we do not want buffer rings to go past ACC = 1 or 2 roads
    arcpy.MakeFeatureLayer_management(Roadblocks, "LAYER_Roadblocks")
    arcpy.SelectLayerByLocation_management("LAYER_Roadblocks", "INTERSECT", "GetBuffed", "", "NEW_SELECTION")

    # Smaller loop, buffer concentric rings
    while checkOne > 0:
        arcpy.Buffer_analysis("GetBuffed", "GBirdsBuff", Dist, "FULL", "ROUND", "ALL", "")
        countDist = countDist + Dist
        arcpy.AddMessage(repr(countDist) + " meters, buffering EO.")
        #Clip grasslands with bird EO buffer
        arcpy.Clip_analysis("polys_GrassL", "GBirdsBuff", "GBirdsbuff_clip")
        #Clip previous clip with roadless block
        arcpy.Clip_analysis("GBirdsbuff_clip", "LAYER_Roadblocks", "GBirds_clip")
        #Union them and prepare to test size
        arcpy.Union_analysis("GetBuffed #; GBirds_clip #", "GrassUnion", "ONLY_FID", "", "NO_GAPS")
        arcpy.Dissolve_management("GrassUnion", "GrassDissolve", "", "", "MULTI_PART")
        arcpy.MakeFeatureLayer_management("GrassDissolve", "LAYER_GrassDissolve", "", "", "")
        # Select multipart EO/buffer >=61ha
        arcpy.SelectLayerByAttribute_management("LAYER_GrassDissolve", "NEW_SELECTION", "\"Shape_Area\" >= " + repr(TotalDistm))

        # Check for empty selection and, if so, buffer EO again, or hits the hectare or distance thresholds
        # and moves on to the next EO.
        results = arcpy.GetCount_management("LAYER_GrassDissolve")
        SelectCount = int(results.getOutput(0))
        arcpy.AddMessage(repr(SelectCount) + " selected features.")
        if SelectCount == 0:
            checkOne = checkOne + 1
            arcpy.AddMessage(repr(checkOne) + " buffer attempts.")
            arcpy.Copy_management("GrassDissolve", "GetBuffed")
            arcpy.AddMessage("Feature " + repr(row.EO_ID) + " still not big enough.")
        else:
            checkOne = 0
            arcpy.Append_management("GrassDissolve", "Append_in_GBirds", "NO_TEST")
            arcpy.AddMessage("Feature " + repr(row.EO_ID) + " is big enough now, and appended.")
            arcpy.AddMessage("checkOne = " + repr(checkOne) + " buffer attempts.")
            arcpy.SelectLayerByAttribute_management("LAYER_GrassDissolve", "CLEAR_SELECTION")
        if countDist >= TotalDist:
            checkOne = 0
            arcpy.Append_management("GrassDissolve", "Append_in_GBirds", "NO_TEST")
            arcpy.AddMessage("Feature " + repr(row.EO_ID) + " has reached 0.5km so now it is appended.")
            arcpy.AddMessage("checkOne = " + repr(checkOne) + " buffer attempts.")


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
arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Grassland Birds.")


