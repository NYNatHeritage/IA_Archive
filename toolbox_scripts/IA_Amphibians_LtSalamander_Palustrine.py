# ---------------------------------------------------------------------------
# IA_Tiger_Salamander.py
# Created on: 2010 December 2
#   
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw, Zoologist, NYNHP)
# Usage: Important Area Model for Tiger Salamander (Ambystoma tigrinum)
#   Dependency: IA_mod_palustrine.py
# Shall not be distributed without permission from the New York Natural Heritage Program
#   Edited: 
#   Edit: 
# ---------------------------------------------------------------------------
#
# Import system modules
import sys, string, os, arcgisscripting, win32com.client, arcpy

# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"

# Workspace
arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True


ModelType = "LtSalamander_palustrine_"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)

in_EOs = "in_EOs"
in_features = "in_features"
CCAP_select = "CCAP_select"
CCAP_Select_Query = "\"VALUE\" = 13 OR \"VALUE\" = 14 OR \"VALUE\" = 15"
LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"
DEC_wetlands = "DEC_wetlands"
NWI_select = "NWI_select"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST


arcpy.AddMessage("Longtail Salamander (palustrine) model")

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01EPAL_LTS'"
    IAmodel = "01EPAL_LTS"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"


# Select out the proper EOs
arcpy.Select_analysis(in_put, in_EOs, selectQuery)
arcpy.AddMessage("In EOs selected. " + EXorHIST + " " + ModelType)

# Buffer the EOs 30 meters
arcpy.Buffer_analysis(in_EOs, in_features, 30, "FULL", "ROUND", "ALL", "")

# Assign the un-buffered EOs to the in_EOs variable and run wetlands selection module: CCAP Wetlands 
arcpy.AddMessage("LU/LC SELECT: Run wetlands selection module: CCAP Wetlands...")

# Select CCAP wetlands
import IA_mod_lulc_select
IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
arcpy.AddMessage("LU/LC SELECT: CCAP Wetlands have been selected.")

# Select DEC wetlands
import IA_mod_lulc_select
IA_mod_lulc_select.DEC_wetlands(in_features, DEC_wetlands, WSP)
arcpy.AddMessage("LU/LC SELECT: DEC Wetlands have been selected.")

# Select out palustrine NWI wetlands
import IA_mod_lulc_select
IA_mod_lulc_select.NWI_polys(in_features, NWI_select, WSP)

arcpy.MakeFeatureLayer_management(NWI_select, "LAYER_NWI_polys")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "NEW_SELECTION", "\"SYSTEM\" = 'P'")
arcpy.CopyFeatures_management ("LAYER_NWI_polys", "NWI_wet_polys")
arcpy.AddMessage("LU/LC SELECT: NWI Wetlands have been selected.")

#Union all wetlands and EOs
arcpy.Union_analysis([in_features, CCAP_select, DEC_wetlands, NWI_select], "Unioned", "", "", "NO_GAPS")

# Buffer these selected wetlands and EOs 340 meters
arcpy.Buffer_analysis("Unioned", "Buff_Unioned", 340, "FULL", "ROUND", "ALL", "")

# Add the IA_MODEL_R field
arcpy.AddMessage("wrap up....")
arcpy.AddField_management("Buff_Unioned", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Buff_Unioned", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management("Buff_Unioned", "Dissolve", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve", "Elim", "AREA", 1000000)

################### WRAP UP
################### 
arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Longtail Salamander - Palustrine.")





