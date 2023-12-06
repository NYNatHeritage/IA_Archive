# ---------------------------------------------------------------------------
# SSURGO2script.py
# Created on: 2012 May
#   (script by John Schmid, GIS Specialist, NYNHP)
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
arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/soils/SCRATCH_SOILS.gdb"
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

in_FGDB = arcpy.GetParameterAsText(0)


arcpy.AddMessage("New Empty Feature Class created...")
arcpy.env.workspace = in_FGDB
arcpy.AddMessage(arcpy.env.workspace)

tableList = arcpy.ListTables()
for table in tableList:
    arcpy.AddMessage(table)
    arcpy.AddMessage("Table Name: " + table)
    SoilPolyName = "soilmu_" + table
    out_County = "C:/_Schmid/_project/Important_Areas/GIS_Data/soils/ssurgo2_FinalKFact.gdb/FinalIndivCounties/SEH_Level_" + table


    arcpy.CopyFeatures_management (in_FGDB + "/SoilPolys/" + SoilPolyName, "TempSoils")

    arcpy.MakeFeatureLayer_management("TempSoils", "LAYER_in_County")
    arcpy.AddField_management("LAYER_in_County", "SEH_PreLevel", "TEXT", "", "12")
    arcpy.AddField_management("LAYER_in_County", "KFact_Num", "FLOAT")
    arcpy.AddJoin_management("LAYER_in_County", "MUKEY", table, "mukey")
    arcpy.CalculateField_management("LAYER_in_County", "KFact_Num", "!FinalKfact!", "PYTHON")
    arcpy.AddMessage("Ready....GO!")

    arcpy.SelectLayerByAttribute_management("LAYER_in_County", "NEW_SELECTION", '"KFact_Num" IS NULL')
    arcpy.CalculateField_management("LAYER_in_County", "SEH_PreLevel", "'Moderate'", "PYTHON")
    arcpy.AddMessage("Nulls")

    arcpy.SelectLayerByAttribute_management("LAYER_in_County", "NEW_SELECTION", "\"MUSYM\" = 'W'")
    arcpy.CalculateField_management("LAYER_in_County", "SEH_PreLevel", "'Water'", "PYTHON")
    arcpy.AddMessage("Water")

    arcpy.SelectLayerByAttribute_management("LAYER_in_County", "NEW_SELECTION", '"KFact_Num" <= 0.22')
    arcpy.CalculateField_management("LAYER_in_County", "SEH_PreLevel", "'Low'", "PYTHON")
    arcpy.AddMessage("Low")

    arcpy.SelectLayerByAttribute_management("LAYER_in_County", "NEW_SELECTION", '"KFact_Num" > 0.22 AND "KFact_Num" <= 0.40')
    arcpy.CalculateField_management("LAYER_in_County", "SEH_PreLevel", "'Moderate'", "PYTHON")
    arcpy.AddMessage("Moderate")

    arcpy.SelectLayerByAttribute_management("LAYER_in_County", "NEW_SELECTION", '"KFact_Num" > 0.40')
    arcpy.CalculateField_management("LAYER_in_County", "SEH_PreLevel", "'High'", "PYTHON")
    arcpy.AddMessage("High")

    arcpy.SelectLayerByAttribute_management("LAYER_in_County", "CLEAR_SELECTION")

    arcpy.CopyFeatures_management ("LAYER_in_County", "outCounty")
    arcpy.AddField_management("outCounty", "SEH_Level", "TEXT", "", "12")
    arcpy.CalculateField_management("outCounty", "SEH_Level", "!TempSoils_SEH_PreLevel!", "PYTHON")
    arcpy.Dissolve_management("outCounty", out_County, "SEH_Level", "", "SINGLE_PART")

    arcpy.DeleteFeatures_management("TempSoils")

