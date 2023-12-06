# ---------------------------------------------------------------------------
# IA_SouthernLeopardFrog.py
# Created on: 2010 July 15
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw, Zoologist, NYNHP)
# Usage: Important Area Model for Southern Leopard Frog
#   Dependency: IA_mod_palustrine.py
# Shall not be distributed without permission from the New York Natural Heritage Program
#   Edited: 2012 April 2
#   Edit: Update to arcpy module and incorporate into toolbox
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


ModelType = "Amphibians_SouthernLeopardFrog"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)
#Proj = arcpy.GetParameterAsText(3)


Hydro24K = "M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\ARCS.surfwatr"
in_EOs = "in_EOs"
EOs_buff = "in_EOs_buff"
BuffDist = "200 Meters"
CCAP_select = "CCAP_select"
CCAP_Select_Query = "VALUE = 13 OR VALUE = 14 OR VALUE = 15, OR VALUE = 16, OR VALUE = 17, OR VALUE = 18, OR VALUE = 19, OR VALUE = 22, OR VALUE = 23"
DEC_wetlands = "DEC_wetlands"
NWI_select = "NWI_select"
NWI_select_lines = "NWI_select_lines"
FinalFC = "D:\\Git_Repos\\IA_geoprocessing_scripts\\"  + ModelType + tyme + EXorHIST

#if Proj == "DOT":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
#    
#elif Proj == "HRE Culverts":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"
#
#elif Proj == "All":
#    LULC = "C:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
#    StudyArea = "M:/reg0/reg0data/base/borders/statemun/region.state"
#    
#elif Proj == "HREP":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HREP"


if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01EPAL_SLF'"
    IAmodel = "01EPAL_SLF"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HPAL_SLF'"
    IAmodel = "01HPAL_SLF"

print ("Southern Leopard Frog (Rana sphenocephala) model")


# Define the SLF processing procedure, which must be run twice.
def SLFwet(in_SLF, SLF_out, WSP):  

    Hydro24K = "M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\ARCS.surfwatr"
    CCAP_select = "CCAP_select"
    CCAP_Select_Query = "\"VALUE\" in ( 13, 14, 15, 16, 17, 18, 19, 22, 23)"
    DEC_wetlands = "DEC_wetlands"
    NWI_select = "NWI_select"
    NWI_select_lines = "NWI_select_lines"
    in_features = in_SLF

    
    ################### Determine contiguous 1:24K surface hydrography
    ################### 
    print("Determine contiguous 1:24K Surface Hydrography")
    
    # Hydro24K, poly features:
    # Call out function:
    print("Selecting Hydro24K...")
    # Select out all but the lacustrine NWI wetlands
    arcpy.MakeFeatureLayer_management(Hydro24K, "LAYER_Hydro24K")
    arcpy.SelectLayerByAttribute_management("LAYER_Hydro24K", "NEW_SELECTION", "\"MAJOR1\" = 50")
    arcpy.SelectLayerByLocation_management("LAYER_Hydro24K", "INTERSECT", in_SLF, "", "SUBSET_SELECTION")
    arcpy.CopyFeatures_management ("LAYER_Hydro24K", "Hydro24K_polys")
    arcpy.AddMessage("LAYER_Hydro24K have been selected.")

    ################### Determine contiguous CCAP wetlands
    ################### 
    arcpy.AddMessage("Determine contiguous CCAP wetlands")
      
    # Select contiguous CCAP Wetlands
    import IA_mod_lulc_select
    IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
    print("LU/LC SELECT: CCAP Wetlands have been selected...")
  
    ################### Determine contiguous DEC wetlands
    ################### 
    print("Determine contiguous DEC wetlands")
    
    # Select contiguous DEC Wetlands
    import IA_mod_lulc_select
    IA_mod_lulc_select.DEC_wetlands(in_features, DEC_wetlands, WSP)
    print("LU/LC SELECT: DEC Wetlands have been selected...")

    arcpy.MakeFeatureLayer_management(DEC_wetlands, "LAYER_DEC_wetlands")
    arcpy.SelectLayerByLocation_management("LAYER_DEC_wetlands", "INTERSECT", in_features, "", "NEW_SELECTION")
    arcpy.CopyFeatures_management ("LAYER_DEC_wetlands", "DEC_select")


    ################### Determine contiguous NWI wetlands
    ################### 
    arcpy.AddMessage("Determine contiguous NWI wetlands")
    
    # NWI Wetlands, poly features:
    # Call out function:
    import IA_mod_lulc_select
    IA_mod_lulc_select.NWI_polys(in_features, NWI_select, WSP)

    arcpy.MakeFeatureLayer_management(NWI_select, "LAYER_NWI_polys")
    arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "NEW_SELECTION", "\"ATTRIBUTE\" LIKE 'L%' OR \"ATTRIBUTE\" LIKE 'R%' OR \"ATTRIBUTE\" LIKE 'P%'")
    arcpy.CopyFeatures_management ("LAYER_NWI_polys", "NWI_wet_polys")
    print("NWI Wetland polys have been selected...")

    # NWI Wetlands, poly features:
    # Call out function:
    import IA_mod_lulc_select
    IA_mod_lulc_select.NWI_lines(in_features, NWI_select_lines, WSP)
    print("NWI Wetland lines have been selected.")
    arcpy.MakeFeatureLayer_management(NWI_select_lines, "LAYER_NWI_select_lines")
    arcpy.SelectLayerByAttribute_management("LAYER_NWI_select_lines", "NEW_SELECTION","\"SYSTEM\" = 'L' OR \"SYSTEM\" = 'R' OR \"SYSTEM\" = 'P'")
    arcpy.CopyFeatures_management ("LAYER_NWI_select_lines", "NWI_wet_lines")
    print("NWI Wetland polys have been selected...")
    # Create polys from wetland lines (mmu)
    arcpy.Buffer_analysis("NWI_wet_lines", "NWI_wetland_lines_buff", 6.25, "FULL", "ROUND", "ALL", "")
    print("NWI Wetland lines have been selected.")
    
    ################### Union and Dissolve all
    ###################
    # Union the three parts: the input EOs, the 163 buffer, and the final extra buffer.
    print("Unioning and dissolving EOs and Wetlands...")
    arcpy.Union_analysis([in_EOs, CCAP_select, "DEC_select", "NWI_wet_polys", "NWI_wetland_lines_buff", "Hydro24K_polys"], "WetUnion", "ONLY_FID", "", "NO_GAPS")
    arcpy.Dissolve_management("WetUnion", SLF_out, "", "", "SINGLE_PART")


##################### Select EOs
#####################

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

################### Buffer the EOs
###################
arcpy.Buffer_analysis(in_EOs, "in_EOs_buff", BuffDist, "FULL", "ROUND", "NONE", "")


################### First run of SLF module
###################
in_SLF = "in_EOs_buff"
SLF_out = "SLFround1"
SLFwet(in_SLF, SLF_out, WSP)


################### Buffer all: 340m
###################
print("Buffer all: 340m")
arcpy.Buffer_analysis(SLF_out, "WetBuff", 340, "FULL", "ROUND", "ALL", "")


################### Second run of SLF module
###################
in_SLF = "WetBuff"
SLF_out = "SLFround2"
SLFwet(in_SLF, SLF_out, WSP)

################### Union and Dissolve the 340 buffer with the wetlands
###################
# Union the three parts: the input EOs, the 163 buffer, and the final extra buffer.
print("Unioning and dissolving EOs and Wetlands...")
arcpy.Union_analysis([SLF_out, "WetBuff"], "Union2", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("Union2", "Diss2", "", "", "SINGLE_PART")

################### Alis Roads
################### I had to place the select by attribute before the select by location, because there is a software
################### bug when you try to select by location on a very large SDE dataset. Sheesh.
print("Selecting Roads....")
arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\AIMS.alisroads", "LAYER_alisroads")

arcpy.SelectLayerByAttribute_management("LAYER_alisroads", "NEW_SELECTION", "\"ACC\" = 1 OR \"ACC\" = 2")
arcpy.SelectLayerByLocation_management("LAYER_alisroads", "INTERSECT", "Diss2", "", "SUBSET_SELECTION")

arcpy.MakeFeatureLayer_management("LAYER_alisroads", "LAYER_selected_alisroads")

arcpy.AddMessage("Buffering Selected Roads...")
arcpy.Buffer_analysis("LAYER_selected_alisroads", "Buff_alisroads", 6.25, "FULL", "ROUND", "ALL", "")

arcpy.AddMessage("Cut Wetland Buffers with Roads...")
arcpy.Erase_analysis("Diss2", "Buff_alisroads", "Erase_Wet")

################# Developed Land Use
#################

#   Extracting the CCAP Developed, and Erasing the buffered wetlands with it.
print("Select out high and medium intensity develed lands from CCAP....")
arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAP_developed", "\"VALUE\" = 2 OR \"VALUE\" = 3")
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management("LAYER_CCAP_developed", "LAYER_CCAP_developedpre")
arcpy.RasterToPolygon_conversion("LAYER_CCAP_developedpre", "polysDev_CCAP", "SIMPLIFY", "VALUE")
arcpy.Dissolve_management("polysDev_CCAP", "polys_CCAPDissolve", "", "", "SINGLE_PART")
print("Erase Developed Lands from Wetland Buffers...")
arcpy.Erase_analysis("Erase_Wet", "polys_CCAPDissolve", "Erase_CCAP")
arcpy.MultipartToSinglepart_management("Erase_CCAP","Erase_sp")        

################### Eliminate matrine areas by clipping with county layer
###################

arcpy.Clip_analysis("Erase_sp", "m:/reg0/reg0data/base/borders/statemun/region.county", "No_Marine")

################### Aggregate polys and remove donut holes
###################

arcpy.MakeFeatureLayer_management("No_Marine", "LAYER_No_Marine")
arcpy.SelectLayerByLocation_management("LAYER_No_Marine", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.Union_analysis(["LAYER_No_Marine", in_EOs], "Union3", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("Union3", "Diss3", "", "", "SINGLE_PART")

################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("Diss3", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Diss3", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("Diss3", "Dissolve4", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve4", "Elim", "AREA", 1000000)

##################### WRAP UP
##################### 
FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"

FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST
print FinalFC

arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", FinalFC_gdb)

print("IA model done: Southern Leopard Frog.")


