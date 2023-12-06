# ---------------------------------------------------------------------------
# IA_Birds_BaldEagle.py
# Created on: 2013 March
#   
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Jesse Jaycox, Zoologist, NYNHP)
# Usage: Important Area Model for Bald Eagle
# Shall not be distributed without permission from the New York Natural Heritage Program
#   Edited:
#   Edit:
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


in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)
Proj = arcpy.GetParameterAsText(3)


if Proj == "DOT":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
    
elif Proj == "HRE Culverts":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"

elif Proj == "All":
    LULC = "C:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
    StudyArea = "M:/reg0/reg0data/base/borders/statemun/region.state"
    
elif Proj == "HREP":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HREP"


ModelType = "Birds_BaldEagleALL"
Hydro24Kline = "Database Connections/Bloodhound.sde/ARCS.hydro24_strmnet"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST


############################################################################################
# This model split into the three bald eagle models
############################################################################################


############################################################################################
############################################################################################
# NON_BREEDING (NBR)

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01EALL_NBR'"
    IAmodel = "01EALL_NBR"
##elif EXorHIST == "Historical":
##    selectQuery = "IA_MODEL = 'XXXXXX'"
##    IAmodel = "XXXXXX"
    
arcpy.AddMessage("Bald Eagle Non-Breeding model")
in_EOs = "in_EOs"

##################### Select EOs
# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)
arcpy.AddMessage("EOs Selected: " + IAmodel)

##################### Find Nearest 1:24K Hydro line feature, and the distance, then buffer EO that distance plus 10m to
# capture the river segment. Then buffer EO 300 ft.
arcpy.Near_analysis(in_EOs, Hydro24Kline)
arcpy.AddField_management(in_EOs, "NEARDISTplus10", "FLOAT", "", "20")
arcpy.MakeFeatureLayer_management(in_EOs, "LAYER_in_EOs")
arcpy.SelectLayerByAttribute_management("LAYER_in_EOs", "NEW_SELECTION", "\"NEAR_DIST\" > 91.44")
arcpy.CalculateField_management("LAYER_in_EOs", "NEARDISTplus10", '!NEAR_DIST! + 10', "PYTHON")
arcpy.Buffer_analysis("LAYER_in_EOs", "in_EOsbuff", "NEARDISTplus10", "FULL", "ROUND", "ALL")

##################### Capture the hydro segments that contact this new buffer (may be more than the original), and
# buffer those back 300m.
arcpy.MakeFeatureLayer_management(Hydro24Kline, "LAYER_Hydro24Kline")
arcpy.SelectLayerByLocation_management("LAYER_Hydro24Kline", "INTERSECT", "in_EOsbuff", "", "NEW_SELECTION")
arcpy.Buffer_analysis("LAYER_Hydro24Kline", "Hydro24Kline300", 91.44, "FULL", "ROUND", "ALL")

##################### Buffer EOs 300 feet
# Select out the proper EOs
arcpy.Buffer_analysis(in_EOs, "in_EOsbuff300ft", 91.44, "FULL", "ROUND", "ALL")

##################### Union and Dissolve
arcpy.Union_analysis([in_EOs, "Hydro24Kline300", "in_EOsbuff300ft", "in_EOsbuff"], "NBRUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("NBRUnion", "DISS_NBR", "", "", "SINGLE_PART")

#################### Aggregate and Dissolve all
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
arcpy.AddField_management("DISS_NBR", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("DISS_NBR", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("DISS_NBR", "DISS_NBR2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("DISS_NBR2", "FinalNBR", "AREA", 1000000)

############################################################################################
############################################################################################
# ROOSTING (BER)

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01EALL_BER'"
    IAmodel = "01EALL_BER"
##elif EXorHIST == "Historical":
##    selectQuery = "IA_MODEL = 'XXXXXX'"
##    IAmodel = "XXXXXX"

arcpy.AddMessage("Bald Eagle Roosting model")
in_EOs = "in_EOs"

##################### Select EOs
# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)
arcpy.AddMessage("EOs Selected: " + IAmodel)

# Buffer EOs 1500ft
arcpy.Buffer_analysis(in_EOs, "in_EOs1500", 457.24, "FULL", "ROUND", "ALL")
arcpy.MultipartToSinglepart_management("in_EOs1500","DISS_BER")

#################### Aggregate and Dissolve all
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
arcpy.AddField_management("DISS_BER", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("DISS_BER", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("DISS_BER", "DISS_BER2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("DISS_BER2", "FinalBER", "AREA", 1000000)

############################################################################################
############################################################################################
# NESTING (BEN)

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01EALL_BEN'"
    IAmodel = "01EALL_BEN"
##elif EXorHIST == "Historical":
##    selectQuery = "IA_MODEL = 'XXXXXX'"
##    IAmodel = "XXXXXX"

arcpy.AddMessage("Bald Eagle Roosting model")
in_EOs = "in_EOs"

##################### Select EOs
# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)
arcpy.AddMessage("EOs Selected: " + IAmodel)

##################### Buffer EOs 1500ft
arcpy.Buffer_analysis(in_EOs, "in_EOs1500", 457.24, "FULL", "ROUND", "ALL")
arcpy.MultipartToSinglepart_management("in_EOs1500","Final_Buff1500sp")

##################### Buffer EOs 5km, then clip the special eagle hydro f.c., then buffer these waterbodies 300 feet
arcpy.Buffer_analysis(in_EOs, "in_EOs5000", 5000, "FULL", "ROUND", "ALL")
arcpy.MultipartToSinglepart_management("in_EOs5000","Final_Buff5000sp")
# Clip the special Eagle waterbody layer and then buffer that 300 ft in turn
arcpy.Clip_analysis("C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/HREP_EAHYDRO_SAV", "Final_Buff5000sp", "Clipped_Buff5000sp")
arcpy.Buffer_analysis("Clipped_Buff5000sp", "BuffHydro", 91.44, "FULL", "ROUND", "ALL")

##################### Union and Dissolve
arcpy.Union_analysis(["Final_Buff1500sp", "BuffHydro"], "BENUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("BENUnion", "DISS_BEN", "", "", "SINGLE_PART")

#################### Aggregate and Dissolve all
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
arcpy.AddField_management("DISS_BEN", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("DISS_BEN", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("DISS_BEN", "DISS_BEN2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("DISS_BEN2", "FinalBEN", "AREA", 1000000)


############################################################################################
############################################################################################
# WRAP UP

####################### Union and Dissolve
arcpy.Merge_management(["FinalNBR", "FinalBER", "FinalBEN"], "FinalUnion")

arcpy.CopyFeatures_management ("FinalUnion", FinalFC)
arcpy.CopyFeatures_management ("FinalUnion", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Bald Eagle.")

