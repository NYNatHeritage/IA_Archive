# ---------------------------------------------------------------------------
# IA_Animals_LacustrineNonEOs.py
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

in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)
ModelType = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
NHDplusCatch = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/drainage/catchment.shp"
in_features = "in_put100"
CCAP_select = "CCAP_select"
# LU Code 21 not included below because it includes estuarine.
CCAP_Select_Query = "\"VALUE\" = 13 OR \"VALUE\" = 14 OR \"VALUE\" = 15 OR \"VALUE\" = 22"
LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
DEC_wetlands = "DEC_wetlands"
NWI_select = "NWI_select"
in_buff_ring = "in_buff_ring"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/_latest_results/" + ModelType + tyme + EXorHIST + ".shp"



if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ELAC_G01'"
    IAmodel = "01ELAC_G01"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HLAC_G01'"
    IAmodel = "01HLAC_G01"


arcpy.AddMessage("Basic Lacustrine Animals model")

### Select out the proper EOs
##arcpy.Select_analysis(in_put, in_EOs, selectQuery)
##arcpy.AddWarning("In EOs selected. " + EXorHIST + " " + ModelType)
##
### Buffer the waterbodies 50 meters to capture relevant non-EOs
##arcpy.AddMessage("Buffer the waterbodies 50 meters to capture relevant non-EOs...")
##arcpy.MakeFeatureLayer_management(NHDplusCatch, "LAYER_NHDplusCatch")
##arcpy.SelectLayerByLocation_management("LAYER_NHDplusCatch", "INTERSECT", in_EOs, "", "NEW_SELECTION")
##arcpy.MakeFeatureLayer_management("Database Connections/Bloodhound.sde/ARCS.surfwatr", "LAYER_surfwater")
##arcpy.SelectLayerByLocation_management("LAYER_surfwater", "INTERSECT", "LAYER_NHDplusCatch", "", "NEW_SELECTION")
##arcpy.Buffer_analysis("LAYER_surfwater", "waterbody50", 50, "FULL", "ROUND", "ALL", "")
##
### CCapture non-EOs with waterbodies
##arcpy.AddMessage("Capture non-EOs with waterbodies...")
##arcpy.MakeFeatureLayer_management(in_EOs, "LAYER_in_put")
##arcpy.SelectLayerByLocation_management("LAYER_in_put", "INTERSECT", "waterbody50", "", "NEW_SELECTION")
##arcpy.CopyFeatures_management ("LAYER_in_put", "non_EOs")
##
##
### Buffer the captured non-EOs 10 meters and then 100 meters to capture wetlands
##arcpy.AddMessage("Buffer the EOs 100 meters to capture wetlands...")
##arcpy.Buffer_analysis("non_EOs", "in_put10", 10, "FULL", "ROUND", "ALL", "")
##arcpy.Buffer_analysis("non_EOs", in_features, 100, "FULL", "ROUND", "ALL", "")
##
### Assign the un-buffered EOs to the in_EOs variable and run wetlands selection module: CCAP Wetlands 
##arcpy.AddMessage("LU/LC SELECT: Run wetlands selection module: CCAP Wetlands...")
##
### Select CCAP wetlands
##import IA_mod_lulc_select
##IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
##arcpy.AddMessage("LU/LC SELECT: CCAP Wetlands have been selected.")

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
arcpy.CopyFeatures_management ("LAYER_NWI_polys", "NWI_wet_polys")
arcpy.AddMessage("LU/LC SELECT: NWI Wetlands have been selected.")

#Union all wetlands and EOs
arcpy.Union_analysis(["in_put10", CCAP_select, DEC_wetlands, "NWI_wet_polys"], "Unioned", "", "", "NO_GAPS")
#arcpy.Union_analysis(["in_put10", CCAP_select, "NWI_wet_polys"], "Unioned", "", "", "NO_GAPS")
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

# Add the IA_MODEL_R field
arcpy.AddWarning("wrap up....")
arcpy.AddField_management(out_buff, "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management(out_buff, "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management(out_buff, "Dissolve", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve", "Elim", "AREA", 3000)

################### WRAP UP
################### 
arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Animals - Lacustrine.")





