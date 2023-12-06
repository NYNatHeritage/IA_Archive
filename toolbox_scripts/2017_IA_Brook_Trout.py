# Import system modules
import sys, string, os, arcgisscripting, win32com.client, arcpy

# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"

# Workspace
arcpy.env.workspace = arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Animals_Brook_Trout_"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
tyme = "8_29_"
#in_put="W:\\Projects\\HREP\\Impt_Areas_updates_2018\\GIS\EOs_IA_model_input.shp"
in_put="W:\\Projects\\HREP\\Impt_Areas_updates_2018\\GIS\\BrookTrout_Merge3.shp"
in_EOs = "in_EOs"
in_put_buff = "in_put_buff"
out_buff = "out_buff"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/_latest_results/" + ModelType + tyme + EXorHIST + ".shp"


if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ERIV_WBT'"
    IAmodel = "01ERIV_WBT"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HXXXXXXX'"
    IAmodel = "01HXXXXXXX"


# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)


arcpy.Buffer_analysis(in_EOs, in_put_buff, 100, "FULL", "ROUND", "ALL")

########Run NHD for Region 02
    NHDplus = "H:\\Please_Do_Not_Delete_me\\_Schmid\\_GIS_Data\\nhdplus\\NHDPlus02"
    NHDplusHydro = "H:\\Please_Do_Not_Delete_me\\_Schmid\\_GIS_Data\\nhdplus\\NHDPlus02\\Hydrography\\nhdflowline.shp"
    NHDplusCatch = "H:\\Please_Do_Not_Delete_me\\_Schmid\\_GIS_Data\\nhdplus\\NHDPlus02\\drainage\\catchment.shp"
    NHDplusTable="H:\\Please_Do_Not_Delete_me\\_Schmid\\_GIS_Data\\nhdplus\\NHDPlus02\\NHDFlowlineVAA.dbf"
    
 
    ###############HREbounds = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/HRE_Boundary"
    in_buff_ring = "in_buff_ring"

    # Select the stream segments associated with the buffered EO.
    arcpy.MakeFeatureLayer_management(NHDplusHydro, "LAYER_NHDplusHydro")
    arcpy.SelectLayerByLocation_management("LAYER_NHDplusHydro", "INTERSECT", "in_put_buff", "", "NEW_SELECTION")
    
   
    
    
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
        path_length=levels_dict[level][0]
        print level
        print path_length
        where_clause=""" "NHDFlowlineVAA.LEVELPATHI"= """+str(level)+""" AND "NHDFlowlineVAA.PATHLENGTH"="""+str(path_length)
        with arcpy.da.SearchCursor("NHD_HYDRO_full",fields,where_clause) as cursor:
            for row in cursor:
                root_level_ids.append(row[0])
                print str(level)+" has a minimum path of "+str(row[1])+" at the ID of "+str(row[0])
       ###Add in the COMIDS of lines in the feature class that have a level of 0 each will have to be run seperately
       arcpy.CopyFeatures_management ("NHD_HYDRO_full",  "nhd_test")
       root_ids_w_zero=[]
       where=""" "NHDFlowlineVAA.LEVELPATHI"= """+str(0.0)
       with arcpy.da.SearchCursor("NHD_HYDRO_full",fields,where)as cursor:
           for row in cursor:
               root_ids_w_zero.append(row[0])
        
        ##Save these and ensure that they are in the final Segments
        
        # Create a feature layer from the vegtype featureclass
    arcpy.MakeFeatureLayer_management (NHDplusHydro,  "NHD_HYDRO_select")
    
    # Join the feature layer to a table
    arcpy.AddJoin_management("NHD_HYDRO_select", "COMID", NHDplusTable, "COMID")
    
    # Select desired features from veg_layer

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
    arcpy.CopyFeatures_management("NHD_HYDRO_select","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_brook")
    
 # Select out the catchments, so we can use them in turn to select out the
    for field in arcpy.ListFields("NHD_HYDRO_select"):print field.name
    # higher resolution hydrography ANC wants to use.
    arcpy.MakeFeatureLayer_management(NHDplusCatch, "LAYER_NHDplusCatch")
    arcpy.SelectLayerByLocation_management("LAYER_NHDplusCatch", "INTERSECT","NHD_HYDRO_select", "", "NEW_SELECTION")
    #Make Catchments that just intersect the original EOs
    arcpy.MakeFeatureLayer_management(NHDplusCatch, "LAYER_NHDplusCatchEO")
    arcpy.SelectLayerByLocation_management("LAYER_NHDplusCatchEO", "INTERSECT",in_put_buff, "", "NEW_SELECTION")
    arcpy.CopyFeatures_management("LAYER_NHDplusCatchEO","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_brookcate")
    arcpy.Merge_management(["LAYER_NHDplusCatch","LAYER_NHDplusCatchEO"],"LAYER_NHDplusCatchM")

########Run for NHD01######
    NHDplus = "H:\\Please_Do_Not_Delete_me\\_Schmid\\_GIS_Data\\nhdplus\\NHDPlus01"
    NHDplusHydro = "H:\\Please_Do_Not_Delete_me\\_Schmid\\_GIS_Data\\nhdplus\\NHDPlus01\\Hydrography\\nhdflowline.shp"
    NHDplusCatch = "H:\\Please_Do_Not_Delete_me\\_Schmid\\_GIS_Data\\nhdplus\\NHDPlus01\\drainage\\catchment.shp"
    NHDplusTable="H:\\Please_Do_Not_Delete_me\\_Schmid\\_GIS_Data\\nhdplus\\NHDPlus01\\NHDFlowlineVAA.dbf"
    
 
    ###############HREbounds = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/HRE_Boundary"
    in_buff_ring = "in_buff_ring"

    # Select the stream segments associated with the buffered EO.
    arcpy.MakeFeatureLayer_management(NHDplusHydro, "LAYER_NHDplusHydro")
    arcpy.SelectLayerByLocation_management("LAYER_NHDplusHydro", "INTERSECT", "in_put_buff", "", "NEW_SELECTION")
    
   
    
    
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
        path_length=levels_dict[level][0]
        print level
        print path_length
        where_clause=""" "NHDFlowlineVAA.LEVELPATHI"= """+str(level)+""" AND "NHDFlowlineVAA.PATHLENGTH"="""+str(path_length)
        with arcpy.da.SearchCursor("NHD_HYDRO_full",fields,where_clause) as cursor:
            for row in cursor:
                root_level_ids.append(row[0])
                print str(level)+" has a minimum path of "+str(row[1])+" at the ID of "+str(row[0])
       ###Add in the COMIDS of lines in the feature class that have a level of 0 each will have to be run seperately
    arcpy.CopyFeatures_management ("NHD_HYDRO_full",  "nhd_test")
    root_ids_w_zero=[]
    where=""" "NHDFlowlineVAA.LEVELPATHI"= """+str(0.0)
       with arcpy.da.SearchCursor("NHD_HYDRO_full",fields,where)as cursor:
           for row in cursor:
               root_ids_w_zero.append(row[0])
        
        ##Save these and ensure that they are in the final Segments
        
        # Create a feature layer from the vegtype featureclass
    arcpy.MakeFeatureLayer_management (NHDplusHydro,  "NHD_HYDRO_select")
    
    # Join the feature layer to a table
    arcpy.AddJoin_management("NHD_HYDRO_select", "COMID", NHDplusTable, "COMID")
    
    # Select desired features from veg_layer

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
                
    
    test_layer="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_riv_nhd01"
    arcpy.CopyFeatures_management("NHD_HYDRO_select","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_riva_nhd01")
    
 # Select out the catchments, so we can use them in turn to select out the
    for field in arcpy.ListFields("NHD_HYDRO_select"):print field.name
    # higher resolution hydrography ANC wants to use.
    arcpy.MakeFeatureLayer_management(NHDplusCatch, "LAYER_NHDplusCatch")
    arcpy.SelectLayerByLocation_management("LAYER_NHDplusCatch", "INTERSECT","NHD_HYDRO_select", "", "NEW_SELECTION")
    #Make Catchments that just intersect the original EOs
    arcpy.MakeFeatureLayer_management(NHDplusCatch, "LAYER_NHDplusCatchEO")
    arcpy.SelectLayerByLocation_management("LAYER_NHDplusCatchEO", "INTERSECT",in_put_buff, "", "NEW_SELECTION")
    arcpy.CopyFeatures_management("LAYER_NHDplusCatchEO","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_brook_nhd")
    arcpy.Merge_management(["LAYER_NHDplusCatch","LAYER_NHDplusCatchEO"],"LAYER_NHDplusCatchM")










#    arcpy.SelectLayerByLocation_management("LAYER_NHDplusCatch", "HAVE_THEIR_CENTER_IN", StudyArea, "", "NEW_SELECTION")
#    arcpy.AddJoin_management("LAYER_NHDplusCatch", "COMID", "NHD_HYDRO_select", "nhdflowline.COMID", "KEEP_COMMON")
#    arcpy.CopyFeatures_management("LAYER_NHDplusCatch", "upstreamCatchments")
#    
#    arcpy.CopyFeatures_management("upstreamCatchments","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_catch1")
#    
    
    arcpy.CopyFeatures_management("LAYER_NHDplusCatchM", "upstreamCatchments")
    arcpy.CopyFeatures_management("upstreamCatchments","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_brookcatm_nhd")
    arcpy.CopyFeatures_management("upstreamCatchments","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_brookcatm_nhdts")
    # Dissolve catchments, and then eliminate donut holes (missing catchemnts, inside) due
    # to errors in the NHD.
    arcpy.Dissolve_management("upstreamCatchments", "DissCatch", "", "", "SINGLE_PART") 
    arcpy.EliminatePolygonPart_management("DissCatch", "ElimCatch", "AREA", 10000000)
   
    # Select out the higher resolution stream lines with the dissolved catchments from the previous step
    arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\ARCS.hydro24_strmnet", "LAYER_24KHydro")
    arcpy.SelectLayerByLocation_management("LAYER_24KHydro", "HAVE_THEIR_CENTER_IN", "ElimCatch", "", "NEW_SELECTION")
    arcpy.CopyFeatures_management("LAYER_24KHydro", "upstream24KHydro")
    
     arcpy.CopyFeatures_management("upstream24KHydro","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_brook_3_01")
    
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
    
    arcpy.CopyFeatures_management("upstream24Kwaterbodies","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_riv_wbts")  ###THis Part OK##
    # Select out the higher resolution waterbodies with the dissolved catchments.
#    arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\ARCS.surfwatr", "LAYER_24Kwaterbodies")
#    arcpy.SelectLayerByLocation_management("LAYER_24Kwaterbodies", "INTERSECT", "ElimCatch", "", "NEW_SELECTION")
#    arcpy.CopyFeatures_management("LAYER_24Kwaterbodies", "upstream24Kwaterbodies")
#    
#    arcpy.CopyFeatures_management("upstream24Kwaterbodies","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_watrby")
#    # Union stream polys and water polys and then dissolve them, and select
    # "un-isolated", contiguous stream/pond/lake polys
    #arcpy.Union_analysis(["hydro_buff", "upstream24Kwaterbodies"], "HydroUnion", "", "", "NO_GAPS")
   
    
    arcpy.CopyFeatures_management("hydro_buff","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_riv_hbts") 
    arcpy.CopyFeatures_management("HydroUnion","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_riv_huts") ######THIS IS THE SPOT!####
    
     #############test
    
    arcpy.Union_analysis(["hydro_buff", "upstream24Kwaterbodies"], "HydroUnion", "", "")
    arcpy.CopyFeatures_management("HydroUnion","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_riv_hutsgps")
    #########end test                             
                                 
                                 
                                 
    arcpy.Dissolve_management("HydroUnion", "HydroDiss", "", "", "SINGLE_PART")
    arcpy.CopyFeatures_management("HydroDiss","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_riva_401")
    arcpy.CopyFeatures_management("HydroDiss","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_riv_4ts") 
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
    #IA_mod_assessLCSLP.ALCSLP_RIVmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size)
    ALCSLP_RIVmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size)
    
arcpy.CopyFeatures_management("out_buff","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_brookout_west")
arcpy.CopyFeatures_management("out_buff","D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\test_brookout_east")

#buff_eo_only = "buff_eo_only"
#arcpy.Buffer_analysis(in_EOs, buff_eo_only, 163, "FULL", "ROUND", "ALL")


# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("out_buff", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("out_buff", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management("out_buff", "Dissolve", "IA_MODEL_R", "", "SINGLE_PART")

################### WRAP UP
################### 
FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + "_east.shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST+ "_east"


arcpy.CopyFeatures_management ("Dissolve", FinalFC)
arcpy.CopyFeatures_management ("Dissolve", FinalFC_gdb)



arcpy.AddMessage("IA model done: Brook Trout.")
