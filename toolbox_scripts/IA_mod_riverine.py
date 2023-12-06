# ---------------------------------------------------------------------------
# IA_mod_riverine.py
# Created on: 2011 October
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (Community methodology by Tim Howard, NYNHP)
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
#arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"
arcpy.env.snapRaster ="F:\\_Schmid\\_GIS_Data\\SnapRasters\\snapras30met" 
# Workspace
#arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

def RiverineModuleNOTRIBS(in_put_buff, StudyArea, out_buff):

    ##############################################################################
    ##############################################################################
    ##############################################################################
    ##         NEED 2 TEST - redid some things for DOT fish, and didn't end up needing this script
    ##############################################################################
    ##############################################################################
    ##############################################################################

    NHDplus = "H:\\Please_Do_Not_Delete_me\\_Schmid\\_GIS_Data\\nhdplus\\NHDPlus02"
    NHDplusHydro = "H:\\Please_Do_Not_Delete_me\\_Schmid\\_GIS_Data\\nhdplus\\NHDPlus02\\Hydrography\\nhdflowline.shp"
    NHDplusCatch = "H:\\Please_Do_Not_Delete_me\\_Schmid\\_GIS_Data\\nhdplus\\NHDPlus02\\drainage\\catchment.shp"
    NHDplusTable="H:\\Please_Do_Not_Delete_me\\_Schmid\\_GIS_Data\\nhdplus\\NHDPlus02\\NHDFlowlineVAA.dbf"
    
    riparian_buffers="D:\\GIS Projects\\TreesforTribs\\Baselayers_2017.gdb\\Riparian_intersect_c"
    ###############HREbounds = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/HRE_Boundary"
    in_buff_ring = "in_buff_ring"

    # Select the stream segments associated with the buffered EO.
    arcpy.MakeFeatureLayer_management(NHDplusHydro, "LAYER_NHDplusHydro")
    arcpy.SelectLayerByLocation_management("LAYER_NHDplusHydro", "INTERSECT", "in_put_buff", "", "NEW_SELECTION")
    
    ####Copy out test
    test_layer="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_riv1"
    arcpy.CopyFeatures_management("LAYER_NHDplusHydro",test_layer)
    ##
    
    
    test_layer="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_riv0"
    arcpy.Intersect_analysis(["LAYER_NHDplusHydro","in_put_buff"],"pour_point","ONLY_FID","","POINT")
    
     # Create a feature layer from the vegtype featureclass
    arcpy.MakeFeatureLayer_management (NHDplusHydro,  "NHD_HYDRO_full")
    
    # Join the feature layer to a table
    arcpy.AddJoin_management("NHD_HYDRO_full", "COMID", NHDplusTable, "COMID")
    arcpy.SelectLayerByLocation_management("NHD_HYDRO_full", "INTERSECT", "in_put_buff", "", "NEW_SELECTION")
    for field in arcpy.ListFields("NHD_HYDRO_full"): print field.name
    fields=["nhdflowline.COMID","NHDFlowlineVAA.PATHLENGTH","NHDFlowlineVAA.TERMINALPA","NHDFlowlineVAA.LEVELPATHI"]
    root_ids=[]
    terminal_paths=[]
    level_paths=[]
    
    with arcpy.da.SearchCursor("NHD_HYDRO_full",fields) as cursor:
        for row in cursor:
            root_ids.append(row[0])
            terminal_paths.append(row[2])
            level_paths.append(row[3])
            
    #Get unique values of terminal paths
    terminal_list=list(set(terminal_paths))
    terminal_list=[x for x in terminal_list if x!=0]
    
    levels_list=list(set(level_paths))
    levels_list=[x for x in levels_list if x!=0]
    #Areas with the same terminal path drain to the same place, to find the lowest point in the drainage, finth the smallest path length for each termimnal path ID
    root_terminal_ids=[]
    root_level_ids=[]
    terminal_dict={}
    levels_dict={}
    for level in levels_list:
        where_clause=""" "NHDFlowlineVAA.LEVELPATHI"= """+str(level)
        with arcpy.da.SearchCursor("NHD_HYDRO_full",fields,where_clause) as cursor:
            distances=[]
            for row in cursor:
                distances.append(row[1])
            min_path=min(distances)
            max_path=max(distances)
            print str(level)+" has a minimum path of "+str(min_path)+" and a max length of "+str(max_path)
            levels_dict[level]=[min_path,max_path]
    
    for level in levels_list:
        path_length=levels_dict[level]
        print level
        print path_length
        where_clause=""" "NHDFlowlineVAA.LEVELPATHI"= """+str(level)+""" AND "NHDFlowlineVAA.PATHLENGTH"="""+str(path_length)
        with arcpy.da.SearchCursor("NHD_HYDRO_full",fields,where_clause) as cursor:
            for row in cursor:
                root_level_ids.append(row[0])
                print str(level)+" has a minimum path of "+str(row[1])+" at the ID of "+str(row[0])
        # Create a feature layer from the vegtype featureclass
    arcpy.MakeFeatureLayer_management (NHDplusHydro,  "NHD_HYDRO_select")
    
    # Join the feature layer to a table
    arcpy.AddJoin_management("NHD_HYDRO_select", "COMID", NHDplusTable, "COMID")
    
    # Select desired features from veg_layer
big_comid_list=[]  
##Don't use terminal path=0  its not  
root_terminal_ids
for root in root_level_ids:
    fields=["nhdflowline.COMID","NHDFlowlineVAA.PATHLENGTH","NHDFlowlineVAA.LEVELPATHI"]
    whereclause=""" "nhdflowline.COMID"= """+str(root)
    with arcpy.da.SearchCursor("NHD_HYDRO_full",fields,whereclause) as cursor:
        for row in cursor:
            comID=row[0]
            PathLength=row[1]
            LevelPath=row[2]
            Path_End_Length=(3+float(levels_dict[LevelPath][1]))
            print str(comID)+" Level:"+str(LevelPath)+" starts:"+str(PathLength)+" Ends: "+str(Path_End_Length)
          
            where_clause=""" "NHDFlowlineVAA.PATHLENGTH">= """+str(PathLength)+""" AND "NHDFlowlineVAA.PATHLENGTH"<= """+str(Path_End_Length)+""" AND "NHDFlowlineVAA.LEVELPATHI"= """+str(LevelPath)
            arcpy.SelectLayerByAttribute_management("NHD_HYDRO_select","ADD_TO_SELECTION",where_clause)
                
    
    test_layer="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_riv5"
    arcpy.CopyFeatures_management("NHD_HYDRO_select","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_riv6b")
    
    arcpy.MakeFeatureLayer_management (riparian_buffers,  "riparian_buffers")
    
    arcpy.SelectLayerByLocation_management("riparian_buffers", "INTERSECT", "NHD_HYDRO_select", "100 meters", "NEW_SELECTION")
    arcpy.CopyFeatures_management("riparian_buffers","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_riv7")
    
    fields=["nhdflowline.COMID","NHDFlowlineVAA.PATHLENGTH","NHDFlowlineVAA.LEVELPATHI","NHDFlowlineVAA.UPLEVELPAT"]
    up_level_ids=[]
    with arcpy.da.SearchCursor("NHD_HYDRO_select",fields) as cursor:
        for row in cursor:
            up_level_ids.append(row[3])
    
    up_level_ids=list(set(up_level_ids))
    up_level_ids=[x for x in up_level_ids if x!=0]
    for level in up_level_ids:
        print level
        where_clause_a=""" "NHDFlowlineVAA.LEVELPATHI"= """+str(level)
        arcpy.SelectLayerByAttribute_management("NHD_HYDRO_select","ADD_TO_SELECTION",where_clause_a)
        
    arcpy.CopyFeatures_management("NHD_HYDRO_select","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_riv8")
    
   # arcpy.CreateTable_management(WSP, "COMID_table", "F:\\_Schmid\\_GIS_Data\\nhdplus\\NHDPlus02\\TNavWork.mdb\\tblNavResults")
    print("Get this far, 2") 
    # To populate new table with the selected segments
    Hrows = arcpy.InsertCursor("COMID_table") 

    #To populate the new table with upstream segments
    HydroRows = arcpy.SearchCursor("LAYER_NHDplusHydro")
    for HydroRow in HydroRows:
        # First populate COMID table with the root segment
        Hrow = Hrows.newRow()
        Hrow.Reachcode = HydroRow.REACHCODE
        Hrow.Comid = HydroRow.COMID
        Hrows.insertRow(Hrow)

        # Now find upstream segments
        # Upstream Trib variables
        NavT = "UPMAIN"
        StartC = HydroRow.COMID
        comidPrint = repr(StartC)
        print(comidPrint)
        StartM = 0
        MaxD = 0
        DataP = "F:/_Schmid/_GIS_Data/nhdplus/NHDPlus02"
        #AppP = "C:/Documents and Settings/All Users/Desktop/Install/VAACOMObjectNavigator/"
        AppP = "F:/_Schmid/_project/Important_Areas/geo_scripts/NHD_scripts/VAACOMObjectNavigator/"
        print("Get this far, 3")
        try:
        # See where the error is
        #
            import IA_mod_nhdNAV
            IA_mod_nhdNAV.NHDNav_module(WSP, NavT, StartC, StartM, MaxD, DataP, AppP)
        except:
            ErrDesc = "Error: Failed NHD script"
            raise StandardError, ErrDesc
        print("Get this far, 4") 
        arcpy.Append_management("F:\\_Schmid\\_GIS_Data\\nhdplus\\NHDPlus02\\TNavWork.mdb\\tblNavResults", "COMID_table", "TEST")

    del Hrow 
    del Hrows
    del HydroRow 
    del HydroRows

    
    # Select out the catchments, so we can use them in turn to select out the
    for field in arcpy.ListFields("NHD_HYDRO_select"):print field.name
    # higher resolution hydrography ANC wants to use.
    arcpy.MakeFeatureLayer_management(NHDplusCatch, "LAYER_NHDplusCatch")
    arcpy.SelectLayerByLocation_management("LAYER_NHDplusCatch", "HAVE_THEIR_CENTER_IN", StudyArea, "", "NEW_SELECTION")
    arcpy.AddJoin_management("LAYER_NHDplusCatch", "COMID", "NHD_HYDRO_select", "nhdflowline.COMID", "KEEP_COMMON")
    arcpy.CopyFeatures_management("LAYER_NHDplusCatch", "upstreamCatchments")
    
    arcpy.CopyFeatures_management("upstreamCatchments","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_catch1")
    
     arcpy.SelectLayerByLocation_management("LAYER_NHDplusCatch", "INTERSECT","NHD_HYDRO_select", "10 meters", "NEW_SELECTION")
    arcpy.CopyFeatures_management("LAYER_NHDplusCatch", "upstreamCatchments")
    arcpy.CopyFeatures_management("upstreamCatchments","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_catch2")
    # Dissolve catchments, and then eliminate donut holes (missing catchemnts, inside) due
    # to errors in the NHD.
    arcpy.Dissolve_management("upstreamCatchments", "DissCatch", "", "", "SINGLE_PART") 
    arcpy.EliminatePolygonPart_management("DissCatch", "ElimCatch", "AREA", 10000000)
   
    # Select out the higher resolution stream lines with the dissolved catchments from the previous step
    arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\ARCS.hydro24_strmnet", "LAYER_24KHydro")
    arcpy.SelectLayerByLocation_management("LAYER_24KHydro", "HAVE_THEIR_CENTER_IN", "ElimCatch", "", "NEW_SELECTION")
    arcpy.CopyFeatures_management("LAYER_24KHydro", "upstream24KHydro")
    
     arcpy.CopyFeatures_management("upstream24KHydro","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_riv11")
    
    # Buffer the streams to create polygons at the mmu for 24K
    arcpy.Buffer_analysis("upstream24KHydro", "hydro_buff", 6.25, "FULL", "ROUND", "ALL")
    
    ##Selet out Freshwater Ponds from NWI
    arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\SDEADMIN.nc_nwi_poly_2016", "LAYER_NWI_P")
    arcpy.SelectLayerByAttribute_management("LAYER_NWI_P","NEW_SELECTION",""" "WETLAND_TYPE"='Freshwater Pond' """)
    
    arcpy.SelectLayerByLocation_management("LAYER_NWI_P", "INTERSECT", "upstream24KHydro", "", "SUBSET_SELECTION")
    arcpy.CopyFeatures_management ("LAYER_NWI_P", "LAYER_NWI_streams")
    arcpy.SelectLayerByAttribute_management("LAYER_NWI_P","NEW_SELECTION",""" "WETLAND_TYPE"='Freshwater Pond' """)
    arcpy.SelectLayerByLocation_management("LAYER_NWI_P", "INTERSECT", in_put_buff, "", "SUBSET_SELECTION")
    arcpy.CopyFeatures_management ("LAYER_NWI_P", "LAYER_NWI_eos")
    arcpy.Union_analysis(["LAYER_NWI_eos", "LAYER_NWI_streams"], "upstream24Kwaterbodies", "", "", "NO_GAPS")
    
    
    # Select out the higher resolution waterbodies with the dissolved catchments.
#    arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\ARCS.surfwatr", "LAYER_24Kwaterbodies")
#    arcpy.SelectLayerByLocation_management("LAYER_24Kwaterbodies", "INTERSECT", "ElimCatch", "", "NEW_SELECTION")
#    arcpy.CopyFeatures_management("LAYER_24Kwaterbodies", "upstream24Kwaterbodies")
#    
#    arcpy.CopyFeatures_management("upstream24Kwaterbodies","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_watrby")
#    # Union stream polys and water polys and then dissolve them, and select
    # "un-isolated", contiguous stream/pond/lake polys
    arcpy.Union_analysis(["hydro_buff", "upstream24Kwaterbodies","LAYER_all_EOs"], "HydroUnion", "", "", "NO_GAPS")
    arcpy.Dissolve_management("HydroUnion", "HydroDiss", "", "", "SINGLE_PART")
    arcpy.CopyFeatures_management("HydroDiss","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_watrby4")
    arcpy.MakeFeatureLayer_management("HydroDiss", "LAYER_HydroDiss")
    arcpy.CopyFeatures_management("LAYER_HydroDiss", "input_Riverine")

   
    
    #arcpy.MakeFeatureLayer_management("HydroDiss", "LAYER_HydroDiss")
    #arcpy.SelectLayerByLocation_management("LAYER_HydroDiss", "INTERSECT", "upstream24KHydro", "", "NEW_SELECTION")
    #arcpy.CopyFeatures_management("LAYER_HydroDiss", "input_Riverine")
    
    ################# Apply baseline buffer: 163m
    #################
    print("Apply baseline buffer: 163m")
    arcpy.AddField_management("input_Riverine", "ORIG_ID", "SHORT")
    arcpy.CalculateField_management("input_Riverine", "ORIG_ID", "int(!OBJECTID!)", "PYTHON")
    arcpy.Buffer_analysis("input_Riverine", in_buff_ring, 163, "FULL", "ROUND", "LIST", "ORIG_ID")
    
    ################# Assessing Cover Type and Slope
    #################
    print("Start the Assess Land Cover Type and Slope Module")
    value_field = "ORIG_ID"
    cell_size = 15
    in_buff = "input_Riverine"
    out_buff = "out_buff"

    import IA_mod_assessLCSLP
    IA_mod_assessLCSLP.ALCSLP_RIVmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size)








def RiverineModule(in_put_buff, StudyArea, out_buff):

    ##############################################################################
    ##############################################################################
    ##############################################################################
    ##         NEED 2 TEST - redid some things for DOT fish, and didn't end up needing this script
    ##############################################################################
    ##############################################################################
    ##############################################################################

    NHDplus = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/"
    NHDplusHydro = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/Hydrography/nhdflowline.shp"
    NHDplusCatch = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/drainage/catchment.shp"
    ###############HREbounds = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/HRE_Boundary"
    in_buff_ring = "in_buff_ring"

    # Select the stream segments associated with the buffered EO.
    arcpy.MakeFeatureLayer_management(NHDplusHydro, "LAYER_NHDplusHydro")
    arcpy.SelectLayerByLocation_management("LAYER_NHDplusHydro", "INTERSECT", "in_put_buff", "", "NEW_SELECTION")
    arcpy.CreateTable_management(WSP, "COMID_table", "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/TNavWork.mdb/tblNavResults")
    print("Get this far, 2") 
    # To populate new table with the selected segments
    Hrows = arcpy.InsertCursor("COMID_table") 

    #To populate the new table with upstream segments
    HydroRows = arcpy.SearchCursor("LAYER_NHDplusHydro")
    for HydroRow in HydroRows:
        # First populate COMID table with the root segment
        Hrow = Hrows.newRow()
        Hrow.Reachcode = HydroRow.REACHCODE
        Hrow.Comid = HydroRow.COMID
        Hrows.insertRow(Hrow)

        # Now find upstream segments
        # Upstream Trib variables
        NavT = "UPTRIB"
        StartC = HydroRow.COMID
        comidPrint = repr(StartC)
        print(comidPrint)
        StartM = 0
        MaxD = 0
        DataP = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02"
        #AppP = "C:/Documents and Settings/All Users/Desktop/Install/VAACOMObjectNavigator/"
        AppP = "C:/_Schmid/_project/Important_Areas/geo_scripts/NHD_scripts/VAACOMObjectNavigator/"
        print("Get this far, 3")
        try:
        # See where the error is
        #
            import IA_mod_nhdNAV
            IA_mod_nhdNAV.NHDNav_module(WSP, NavT, StartC, StartM, MaxD, DataP, AppP)
        except:
            ErrDesc = "Error: Failed NHD script"
            raise StandardError, ErrDesc
        print("Get this far, 4") 
        arcpy.Append_management("C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/TNavWork.mdb/tblNavResults", "COMID_table", "TEST")

    del Hrow 
    del Hrows
    del HydroRow 
    del HydroRows

    
    # Select out the catchments, so we can use them in turn to select out the
    # higher resolution hydrography ANC wants to use.
    arcpy.MakeFeatureLayer_management(NHDplusCatch, "LAYER_NHDplusCatch")
    arcpy.SelectLayerByLocation_management("LAYER_NHDplusCatch", "HAVE_THEIR_CENTER_IN", StudyArea, "", "NEW_SELECTION")
    arcpy.AddJoin_management("LAYER_NHDplusCatch", "COMID", "COMID_table", "Comid", "KEEP_COMMON")
    arcpy.CopyFeatures_management("LAYER_NHDplusCatch", "upstreamCatchments")
    
    # Dissolve catchments, and then eliminate donut holes (missing catchemnts, inside) due
    # to errors in the NHD.
    arcpy.Dissolve_management("upstreamCatchments", "DissCatch", "", "", "SINGLE_PART") 
    arcpy.EliminatePolygonPart_management("DissCatch", "ElimCatch", "AREA", 10000000)
   
    # Select out the higher resolution stream lines with the dissolved catchments from the previous step
    arcpy.MakeFeatureLayer_management("Database Connections/Bloodhound.sde/ARCS.hydro24_strmnet", "LAYER_24KHydro")
    arcpy.SelectLayerByLocation_management("LAYER_24KHydro", "HAVE_THEIR_CENTER_IN", "ElimCatch", "", "NEW_SELECTION")
    arcpy.CopyFeatures_management("LAYER_24KHydro", "upstream24KHydro")
    
    # Buffer the streams to create polygons at the mmu for 24K
    arcpy.Buffer_analysis("upstream24KHydro", "hydro_buff", 6.25, "FULL", "ROUND", "ALL")
    
    # Select out the higher resolution waterbodies with the dissolved catchments.
    arcpy.MakeFeatureLayer_management("Database Connections/Bloodhound.sde/ARCS.surfwatr", "LAYER_24Kwaterbodies")
    arcpy.SelectLayerByLocation_management("LAYER_24Kwaterbodies", "INTERSECT", "ElimCatch", "", "NEW_SELECTION")
    arcpy.CopyFeatures_management("LAYER_24Kwaterbodies", "upstream24Kwaterbodies")
    
    # Union stream polys and water polys and then dissolve them, and select
    # "un-isolated", contiguous stream/pond/lake polys
    arcpy.Union_analysis(["hydro_buff", "upstream24Kwaterbodies"], "HydroUnion", "", "", "NO_GAPS")
    arcpy.Dissolve_management("HydroUnion", "HydroDiss", "", "", "SINGLE_PART")
    
    arcpy.MakeFeatureLayer_management("HydroDiss", "LAYER_HydroDiss")
    arcpy.SelectLayerByLocation_management("LAYER_HydroDiss", "INTERSECT", "upstream24KHydro", "", "NEW_SELECTION")
    arcpy.CopyFeatures_management("LAYER_HydroDiss", "input_Riverine")
    
    ################# Apply baseline buffer: 163m
    #################
    print("Apply baseline buffer: 163m")
    arcpy.AddField_management("input_Riverine", "ORIG_ID", "SHORT")
    arcpy.CalculateField_management("input_Riverine", "ORIG_ID", "int(!OBJECTID!)", "PYTHON")
    arcpy.Buffer_analysis("input_Riverine", in_buff_ring, 163, "FULL", "ROUND", "LIST", "ORIG_ID")
    
    ################# Assessing Cover Type and Slope
    #################
    print("Start the Assess Land Cover Type and Slope Module")
    value_field = "ORIG_ID"
    cell_size = 15
    in_buff = "input_Riverine"
    out_buff = "out_buff"

    import IA_mod_assessLCSLP
    IA_mod_assessLCSLP.ALCSLP_RIVmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size)



def RiverineModuleHRE(in_features, ClipBuff, in_flowline, out_buff):
    # This module differs from the one above because it clips the upstream at 3km. And this module uses an input flowline, not
    # a buffer with which to select the flowline. Then the COMID is used to further select the catchments instead of 

    NHDplusHydro = "F:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/Hydrography/nhdflowline.shp"
    NHDWaterbody = "F:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/Hydrography/NHDWaterbody.shp"
    NHDplusCatch = "F:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/drainage/catchment.shp"
    in_buff_ring = "in_buff_ring"
    print("Get this far, 2") 
    # Select the stream segments associated with the buffered EO.
    #arcpy.CreateTable_management(WSP, "COMID_table", "F:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/TNavWork.mdb/tblNavResults")
    arcpy.CreateTable_management(WSP, "COMID_table", "D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\tblNavResults")
    #"D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\tblNavResults"
    HydroRows = arcpy.SearchCursor(in_flowline)
    for HydroRow in HydroRows:
        # Upstream Trib variables
        NavT = "UPTRIB"
        StartC = HydroRow.COMID
        comidPrint = repr(StartC)
        print(comidPrint)
        StartM = 0
        MaxD = 0
        DataP = "F:/_Schmid/_GIS_Data/nhdplus/NHDPlus02"
        #AppP = "C:/Documents and Settings/All Users/Desktop/Install/VAACOMObjectNavigator/"
        #AppP = "F:/_Schmid/_GIS_Data/nhdplus/VAACOMObjectNavigator/"
        AppP="C://NHDPlusTools//VAACOMObjectNavigator//"
        print("Get this far, 3")
        import IA_mod_nhdNAV
        IA_mod_nhdNAV.NHDNav_module(WSP, NavT, StartC, StartM, MaxD, DataP, AppP)
        print("Get this far, 4")
##        import IA_mod_nhdNAV
##        IA_mod_nhdNAV.NHDNav_module(WSP, NavT, StartC, StartM, MaxD, DataP, AppP)
##        arcpy.CopyRows_management("C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/TNavWork.mdb/tblNavResults", "TABLE_TEST")
        print("Get this far, 5")
#        arcpy.Append_management("TABLE_TEST", "COMID_table", "TEST")
        arcpy.Append_management("F:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/TNavWork.mdb/tblNavResults", "F:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb/COMID_table", "TEST", "", "")
    
    # Select out the catchments, so we can use them in turn to select out the
    # higher resolution hydrography ANC wants to use.
    print("Select out the catchments...")
    arcpy.MakeFeatureLayer_management(NHDplusHydro, "LAYER_NHDplusHydro")
    arcpy.AddJoin_management("LAYER_NHDplusHydro", "COMID", "COMID_table", "Comid", "KEEP_COMMON")
    arcpy.CopyFeatures_management("LAYER_NHDplusHydro", "PreupstreamHydro")

    # Clip the streams with the cutoff buffer
    print("Clip the streams with the cutoff buffer...")
    arcpy.Clip_analysis("PreupstreamHydro", ClipBuff, "UpstreamHydroLines")

    # Select waterbodies along streams
    print("Clip waterbodies along streams...")
    arcpy.Clip_analysis("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\ARCS.surfwatr", ClipBuff, "upstreamHydroWaterbodies")

    # Buffer stream lines and then union/dissolve to waterbodies
    print("Buffer stream lines and then union/dissolve to waterbodies...")
    arcpy.Buffer_analysis("UpstreamHydroLines", "HydroLinePolys", 6.25, "FULL", "ROUND", "ALL")
    #arcpy.Union_analysis(["HydroLinePolys", "upstreamHydroWaterbodies", in_features], "HydroUnion", "", "", "NO_GAPS")
    arcpy.Union_analysis(in_features + " #; HydroLinePolys #; upstreamHydroWaterbodies #", "HydroUnion", "ONLY_FID", "", "NO_GAPS")
    # Dissolve
    arcpy.Dissolve_management("HydroUnion", "HydroDiss", "", "", "SINGLE_PART")

    ################# Apply baseline buffer: 163m
    #################
    print("Apply baseline buffer: 163m")
    arcpy.AddField_management("HydroDiss", "ORIG_ID", "SHORT")
    arcpy.CalculateField_management("HydroDiss", "ORIG_ID", "int(!OBJECTID!)", "PYTHON")
    arcpy.Buffer_analysis("HydroDiss", in_buff_ring, 163, "FULL", "ROUND", "LIST", "ORIG_ID")
    
    ################# Assessing Cover Type and Slope
    #################
    print("Start the Assess Land Cover Type and Slope Module")
    value_field = "ORIG_ID"
    cell_size = 15
    in_buff = "HydroDiss"
    out_buff = "out_buff"

    import IA_mod_assessLCSLP
    IA_mod_assessLCSLP.ALCSLP_RIVmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size)













