# ---------------------------------------------------------------------------
# IA_Animals_Lacustrine.py
# Created on: 2010 December 2
#   
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw, Zoologist, NYNHP)
# Usage: Important Area Model for Tiger Salamander (Ambystoma tigrinum)
#   Dependency: IA_mod_palustrine.py
# Shall not be distributed without permission from the New York Natural Heritage Program
#   Edited: February 26, 2013
#   Edit: For HREP updates
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


ModelType = "Animals_lacustrine"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)
Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
in_features = "in_put_buff"
CCAP_select = "CCAP_select"
LULC = "C:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
# LU Code 21 not included below because it includes estuarine.
CCAP_Select_Query = "\"VALUE\" = 13 OR \"VALUE\" = 14 OR \"VALUE\" = 15 OR \"VALUE\" = 22"
DEC_wetlands = "DEC_wetlands"
NWI_select = "NWI_select"
in_buff_ring = "in_buff_ring"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

arcpy.AddMessage("Basic Lacustrine Animals model")

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ELAC_G01'"
    IAmodel = "01ELAC_G01"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HLAC_G01'"
    IAmodel = "01HLAC_G01"

if Proj == "DOT":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
    
elif Proj == "HRE Culverts":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"

elif Proj == "All":
    LULC = "C:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
    StudyArea = "M:/reg0/reg0data/base/borders/statemun/region.state"
    
# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)


arcpy.AddMessage("In EOs selected. " + EXorHIST + " " + ModelType)

################### Buffer the EOs 30 meters
###################

arcpy.Buffer_analysis(in_EOs, "in_put_buff", 100, "FULL", "ROUND", "ALL", "")


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
# Selecting out the lacustrine and palustrine NWI wetlands
arcpy.MakeFeatureLayer_management(NWI_select, "LAYER_NWI_polys")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "NEW_SELECTION", "\"SYSTEM\" = 'P' OR \"SYSTEM\" = 'L'")
#arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "SUBSET_SELECTION ", "\"WETLAND_TY\" <> 'Estuarine and Marine Deepwater' ")
arcpy.CopyFeatures_management ("LAYER_NWI_polys", "NWI_wet_polys")
arcpy.AddMessage("LU/LC SELECT: NWI Wetlands have been selected.")

#Union all wetlands and EOs
arcpy.Union_analysis(["in_put_buff", CCAP_select, DEC_wetlands, "NWI_wet_polys"], "Unioned", "", "", "NO_GAPS")
# Dissolve all wetlands from previous Union
arcpy.Dissolve_management("Unioned", "Dissolve", "", "", "SINGLE_PART")

# Apply baseline buffer: 163m
arcpy.AddMessage("Apply baseline buffer: 163m")
arcpy.AddField_management("Dissolve", "ORIG_ID", "SHORT")
arcpy.CalculateField_management("Dissolve", "ORIG_ID", "int(!OBJECTID!)", "PYTHON")
arcpy.Buffer_analysis("Dissolve", in_buff_ring, 163, "FULL", "ROUND", "LIST", "ORIG_ID")

arcpy.AddMessage("Start the Assess Land Cover Type and Slope Module")
value_field = "ORIG_ID"
cell_size = 15
in_buff = "Dissolve"
out_buff = "out_buff"
import IA_mod_assessLCSLP
IA_mod_assessLCSLP.ALCSLP_PALmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size)

# Erase out NWI deepwater habitats
arcpy.MakeFeatureLayer_management("Database Connections\\bloodhound.sde\\SDEADMIN.nc_nwi_poly", "LAYER_NWI")
arcpy.SelectLayerByAttribute_management("LAYER_NWI", "NEW_SELECTION", "\"WETLAND_TY\" = 'Estuarine and Marine Deepwater'")
arcpy.Erase_analysis(out_buff, "LAYER_NWI", "NWI_wet_NoDW")
arcpy.AddMessage("LU/LC SELECT: NWI Wetlands have been selected.")

# Add the IA_MODEL_R field
arcpy.AddMessage("wrap up....")
arcpy.Union_analysis([in_EOs, "NWI_wet_NoDW"], "UnionedEOs", "", "", "NO_GAPS")
arcpy.AddField_management("UnionedEOs", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("UnionedEOs", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management("UnionedEOs", "Dissolve", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve", "Elim", "AREA", 1000000)
arcpy.MakeFeatureLayer_management("Elim", "LAYER_Elim")
arcpy.SelectLayerByLocation_management("LAYER_Elim", "INTERSECT", in_EOs, "", "NEW_SELECTION")

################### WRAP UP
################### 
arcpy.CopyFeatures_management ("LAYER_Elim", FinalFC)
arcpy.CopyFeatures_management ("LAYER_Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Animals - Lacustrine.")





