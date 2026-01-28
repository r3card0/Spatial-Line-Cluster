import geopandas as gpd
import networkx as nx
from shapely import wkt
from shapely.geometry.base import BaseGeometry


class SpatialLineCluster:
    def __init__(self):
        pass

    
    def is_geodataframe(self,df:object):
        return isinstance(df,gpd.GeoDataFrame)
    
    def build_geodataframe(self,df:object,geometry_column_name:str, crs:str|None=None):
        """
        Function to convert a DataFrame to GeoDataFrame. Evaluates if the input object it's already a GeoDataFrame
        """
        if crs is None:
            raise ValueError("⚠️ CRS is required. e.g: 'EPSG:4326' ")
        else:
            crs
        # Evaluate geometry column is already a shapely object
        def safe_wkt_load(x):
            if isinstance(x,str):
                return wkt.loads(x)
            elif isinstance(x,BaseGeometry):
                return x
            else:
                raise TypeError(f"Data type not recognized: {type(x)}")
            
        if self.is_geodataframe(df) == False:
            # Convert to a geometry
            df_copy = df.copy()

            # Evaluate if dataset contains a column named: "geometry"
            cols_list = list(df_copy.columns)
            
            if cols_list.count("geometry"):
                # create a GeoDataFrame
                gdf = gpd.GeoDataFrame(df_copy,geometry="geometry", crs=crs)
            else:
                df_copy["geometry"] = df_copy[geometry_column_name].apply(safe_wkt_load)
                
                # Create a GeoDataFrame
                gdf = gpd.GeoDataFrame(df_copy,geometry="geometry", crs=crs)

                # Remove the geometry column name to avoid duplicated geometries
                gdf = gdf.drop(columns=[geometry_column_name])

            return gdf  
        else:
            return df
    
    def determine_utm_and_reproject(self,row,geometry_col_name:str,crs=None):
        """
        Determine the appropriate UTM zone for a geometry and calculate its length in meters.
    
        This method takes a row of data containing a geometry, determines the optimal UTM 
        (Universal Transverse Mercator) coordinate reference system for that geometry based 
        on its location, reprojects the geometry to that UTM CRS, and returns both the EPSG 
        code and the geometry's length in the projected coordinate system.
    
        Parameters
        ----------
        row : pandas.Series or dict-like 
            A row of data containing the geometry and associated attributes.
        geometry_col_name : str
            The name of the column containing the geometry object.
        crs : str or pyproj.CRS, optional
            The coordinate reference system of the input geometry. 
            Defaults to "EPSG:4326" (WGS84) if not specified.
    
        Returns
        -------
        tuple of (int, float)
            A tuple containing:
            - int: The EPSG code of the determined UTM zone
            - float: The length of the geometry in meters in the projected CRS
        """
        _crs = crs if crs is not None else "EPSG:4326"

    
        # 1. Define CRS
        temporal_gdf = gpd.GeoDataFrame([row],geometry=geometry_col_name,crs=_crs)

        # 2. Determine the CRS of the geometry
        utm_crs = temporal_gdf.estimate_utm_crs()

        # 3. Get a reprojected dataset
        data_reprojected = temporal_gdf.to_crs(utm_crs).geometry.iloc[0]

        return utm_crs.to_epsg(), data_reprojected.length

    def add_utm_projection_metrics(self, gdf:object, geometry_col_name:str):
        """
        Add UTM projection information and metric lengths to a GeoDataFrame.
    
        This method processes each row of a GeoDataFrame, determines the optimal UTM zone
        for each geometry, and calculates the geometry's length in meters. The results are
        added as two new columns: 'utm_epsg' (the EPSG code of the UTM zone) and 'len_mt'
        (the length in meters).

        Parameters
        ----------
        gdf : gpd.GeoDataFrame
            The input GeoDataFrame containing geometries to process.
        geometry_col_name : str
            The name of the column containing the geometry objects.
    
        Returns
        -------
        gpd.GeoDataFrame
            A copy of the input GeoDataFrame with two additional columns:
            - 'utm_epsg' (int): The EPSG code of the determined UTM zone for each geometry
            - 'len_mt' (float): The length of each geometry in meters
        """
        gdf_copy = gdf.copy()
        gdf_copy[["utm_epsg","len_mt"]] = gdf_copy.apply(self.determine_utm_and_reproject,axis=1,args=(geometry_col_name,),result_type="expand")
        return gdf_copy

    def group_geometries_by_proximity(self,gdf:object,geometry_col_name:str,tolerance_meter:float):
        """
        Group geometries based on spatial proximity using connected components analysis.
    
        This function identifies clusters of geometries (lines, polygons, etc.) that are
        touching or within a specified distance tolerance. It uses a graph-based approach
        where geometries within the tolerance distance are connected as edges, and connected
        components are identified as groups. Each group is assigned a unique 'parking_id'.
    
        Parameters
        ----------
        gdf : gpd.GeoDataFrame
            The input GeoDataFrame containing geometries to group. Must have a valid
            projected CRS (preferably in meters) for accurate distance calculations.
        geometry_col_name : str
            The name of the column containing the geometry objects.
        tolerance_meter : float, optional
            The distance tolerance in meters. Geometries within this distance are
            considered part of the same group. Default is 0.5 meters.
    
        Returns
        -------
        gpd.GeoDataFrame
            The input GeoDataFrame with an additional 'parking_id' column containing
            the group identifier (integer) for each geometry.
        """
        # 1. Create the Graph
        G = nx.Graph()
        G.add_nodes_from(gdf.index)

        # 2. Use Spatial Index
        sindex = gdf.sindex

        for i,row in gdf.iterrows():
            geom = row[geometry_col_name]
            bbox = geom.buffer(tolerance_meter).bounds
            get_indexes = sindex.intersection(bbox)

            for j in get_indexes:
                if i < j: # Avoid compare the same pair twice
                    geom_j = gdf.loc[gdf.index[j],geometry_col_name]
                    # Verify 
                    if geom.buffer(tolerance_meter).intersects(geom_j):
                        G.add_edge(i,j) 

        # 3. Identify connected component
        components = list(nx.connected_components(G))

        # DEBUGING 
        print(f"Analysis completed: It was detected {len(components)} unique groups.")

        # 4. Assign ID of the group
        for group_id, nodes in enumerate(components):
            gdf.loc[list(nodes),"parking_id"] = group_id

        return gdf

    def process_clustering(self,gdf:object,geometry_col_name:str,tolerance_in_meter:float):
        """
        Execute the complete spatial clustering pipeline for geometries.
    
        This method orchestrates a two-step process: first, it reprojects geometries to
        their optimal UTM zones and calculates metric lengths; second, it groups geometries
        based on spatial proximity. This is the main entry point for the spatial clustering
        workflow.
    
        Parameters
        ----------
        gdf : gpd.GeoDataFrame
            The input GeoDataFrame containing geometries to process. Should have a valid
            CRS defined (typically EPSG:4326 or another geographic coordinate system).
        geometry_col_name : str
            The name of the column containing the geometry objects.
        tolerance_in_meters : float
            The distance tolerance in meters for grouping. Geometries within this distance
            are considered part of the same cluster. Must be positive.
    
        Returns
        -------
        gpd.GeoDataFrame
            A GeoDataFrame with the following added columns:
            - 'utm_epsg' (int): The EPSG code of the UTM zone used for each geometry
            - 'len_mt' (float): The length of each geometry in meters
        """
        gdf_projected = self.add_utm_projection_metrics(gdf,geometry_col_name)

        grouped = self.group_geometries_by_proximity(gdf_projected,geometry_col_name,tolerance_meter=tolerance_in_meter)

        return grouped