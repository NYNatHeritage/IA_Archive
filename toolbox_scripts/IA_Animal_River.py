# ---------------------------------------------------------------------------
# IA_Animals_River.py
# Created on: 2009 April
#   Edits: 2011 September  - update to version 10 and for new ANC HREP Culvert
#       project.
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (animal methodology by Hollie Shaw, NYNHP)
# This script shall not be distributed without permission from the New York Natural Heritage Program
# 
#   Dependency: IA_common_functions.py (riverine module), NHD_Selection, and NHD_subselect
# ---------------------------------------------------------------------------

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

ModelType = "Animals_River_"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)


in_put_buff = "in_put_buff"
out_buff = "out_buff"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/_latest_results/" + ModelType + tyme + EXorHIST + ".shp"


if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ERIV_G01'"
    IAmodel = "01ERIV_G01"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HXXXXXXX'"
    IAmodel = "01HXXXXXXX"

# First buffer the EO to catch the segments.
arcpy.Buffer_analysis(in_put, in_put_buff, 100, "FULL", "ROUND", "ALL")

# Run riverine community module.
import IA_mod_riverine
IA_mod_riverine.RiverineModule(in_put_buff, out_buff)

# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management(out_buff, "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management(out_buff, "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management(out_buff, "Dissolve", "IA_MODEL_R", "", "SINGLE_PART")

################### WRAP UP
################### 

arcpy.CopyFeatures_management ("Dissolve", FinalFC)
arcpy.CopyFeatures_management ("Dissolve", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Riverine Animals.")















