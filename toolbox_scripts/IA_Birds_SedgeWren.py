# ---------------------------------------------------------------------------
# IA_Birds_SedgeWren.py
# Created on: 2013 March 5
#   
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Erin White, Zoologist, NYNHP)
# Usage: Important Area Model for Sedge Wren
#   
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


ModelType = "Birds_SedgeWren_"
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


in_EOs = "in_EOs"
in_features = "in_EOs"
CCAP_select = "CCAP_select"
CCAP_Select_Query = "\"VALUE\" = 5 OR \"VALUE\" = 7 OR \"VALUE\" = 8 OR \"VALUE\" = 14 OR \"VALUE\" = 15 OR \"VALUE\" = 17 OR \"VALUE\" = 18 OR \"VALUE\" = 20"
DEC_wetlands = "DEC_wetlands"
NWI_select = "NWI_select"
in_buff_ring = "in_buff_ring"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST


if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETPE_SEW'"
    IAmodel = "01ETPE_SEW"
#elif EXorHIST == "Historical":
#    selectQuery = "IA_MODEL = 'XXXXXXX'"
#    IAmodel = "XXXXXXX"

arcpy.AddMessage(ModelType + " model")

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)


#######
####### Select open areas/grasslands/wetlands
#######
# Select CCAP LU
import IA_mod_lulc_select
IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
arcpy.AddMessage("LU/LC SELECT: CCAP LU classes have been selected.")

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
arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "NEW_SELECTION", "\"SYSTEM\" = 'E' OR \"SYSTEM\" = 'P'OR \"SYSTEM\" = 'L'")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "REMOVE_FROM_SELECTION", "\"NWI_CODE\" = 'E1UBL'")
arcpy.CopyFeatures_management ("LAYER_NWI_polys", "NWI_wet_polys")

#Union all open areas/grasslands/wetlands
arcpy.Union_analysis([in_features, CCAP_select, DEC_wetlands, "NWI_wet_polys"], "Unioned", "", "", "NO_GAPS")
# Dissolve all wetlands from previous Union
arcpy.Dissolve_management("Unioned", "Dissolved", "", "", "SINGLE_PART")

#######
####### Run palustrine on EO, and then merge with the open areas/grasslands/wetlands
#######
arcpy.AddMessage("Apply baseline buffer: 163m")
arcpy.AddField_management(in_EOs, "ORIG_ID", "SHORT")
arcpy.CalculateField_management(in_EOs, "ORIG_ID", "int(!OBJECTID!)", "PYTHON")
arcpy.Buffer_analysis(in_EOs, in_buff_ring, 163, "FULL", "ROUND", "LIST", "ORIG_ID")

# Run the Land Cover Type and Slope Module
arcpy.AddMessage("Start the Assess Land Cover Type and Slope Module")
value_field = "ORIG_ID"
cell_size = 15
in_buff = in_EOs
out_buff = "out_buff"
import IA_mod_assessLCSLP
IA_mod_assessLCSLP.ALCSLP_PALmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size)

#Union all estuarine wetlands and EOs
arcpy.Union_analysis([out_buff, "Dissolved"], "UnionedSW", "", "", "NO_GAPS")
# Dissolve all wetlands from previous Union
arcpy.Dissolve_management("UnionedSW", "DissolvedSW", "", "", "SINGLE_PART")

# Add the IA_MODEL_R field
arcpy.AddMessage("wrap up....")
arcpy.AddField_management("DissolvedSW", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("DissolvedSW", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management("DissolvedSW", "DissolveLast", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("DissolveLast", "Elim", "AREA", 1000000)

################### WRAP UP
################### 
arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Sedge Wren.")





