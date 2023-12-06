# ---------------------------------------------------------------------------
# IA_Animal_River_.py
# Created on: 2011 December
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (animal methodology by Hollie Shaw, NYNHP)
# This script shall not be distributed without permission from the New York Natural Heritage Program
# 
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os, arcgisscripting, arcpy


# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"

# Workspace
arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Animals_Riverine_Manual"

################# Apply baseline buffer: 163m
#################
arcpy.AddMessage("Apply baseline buffer: 163m")
arcpy.AddField_management("HydroDiss", "ORIG_ID", "SHORT")
arcpy.CalculateField_management("HydroDiss", "ORIG_ID", "int(!OBJECTID!)", "PYTHON")
in_buff_ring = "in_buff_ring"
arcpy.Buffer_analysis("HydroDiss", in_buff_ring, 163, "FULL", "ROUND", "LIST", "ORIG_ID")

################# Assessing Cover Type and Slope
#################
arcpy.AddMessage("Start the Assess Land Cover Type and Slope Module")
value_field = "ORIG_ID"
cell_size = 15
in_buff = "HydroDiss"
out_buff = "out_buff"

import IA_mod_assessLCSLP
IA_mod_assessLCSLP.ALCSLP_RIVmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size)

##in_EOs = "in_EOs"
##in_put_buff = "in_put_buff"
##NHDplusHydro = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/Hydrography/nhdflowline.shp"
##NHDplusCatch = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/drainage/catchment.shp"
###in_features = "in_features"
##ClipBuff = "ClipBuff"
##in_flowline = "FlowAppend"
##out_buff = "out_buff"
##FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST
##
##in_EOs = "in_EOs"
##NHDplusHydro = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/Hydrography/nhdflowline.shp"
##NHDplusCatch = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/drainage/catchment.shp"
##in_features = "in_features"
##ClipBuff = "ClipBuff"
##in_flowline = "FlowAppend"
##out_buff = "out_buff"
##FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST
##

### RUN MANUAL TO THIS


##arcpy.AddMessage("Get this far, 1") 
### Run riverine community module.
##import IA_mod_riverine
##IA_mod_riverine.RiverineModuleHRE(in_features, ClipBuff, in_flowline, out_buff)
##

### Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
### and came up with memory issues, so I just write to the final layer for now. 
###
##arcpy.AddField_management(out_buff, "IA_MODEL_R", "TEXT", "", "20")
##arcpy.CalculateField_management(out_buff, "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
##arcpy.Dissolve_management(out_buff, "Dissolve", "IA_MODEL_R", "", "SINGLE_PART")
##
##
### Select out only those polys contiguous with the EO
##arcpy.MakeFeatureLayer_management("Dissolve", "LAYER_Dissolve")
##arcpy.SelectLayerByLocation_management("LAYER_Dissolve", "INTERSECT", in_EOs, "", "NEW_SELECTION")
##
##
##################### WRAP UP
##################### 
##
##arcpy.CopyFeatures_management ("LAYER_Dissolve", FinalFC)
##arcpy.CopyFeatures_management ("LAYER_Dissolve", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)
##
##arcpy.AddMessage("IA model done: " + ModelType)















