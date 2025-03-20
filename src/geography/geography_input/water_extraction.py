
import geopandas as gpd
import osmnx as ox
from osmnx._errors import InsufficientResponseError
from src.geography.geo_coord_sys import GeoBoundingBox
from src.logger import get_logger
import logging

logger = get_logger("water import", logging.DEBUG)

def get_lakes_with_area(bbox: GeoBoundingBox):
    """
    Get only lakes (not rivers or other waterways) within a bounding box,
    and calculate their areas.
    
    Parameters:
    - bbox: tuple of (min_lon, min_lat, max_lon, max_lat)
    
    Returns:
    - lakes_gdf: GeoDataFrame containing lakes with area information
    """
    
    bbox_gdf = gpd.GeoDataFrame(geometry=[bbox.get_as_polygon()], crs="EPSG:4326")
    
    # Get only lakes (not rivers or streams)
    tags = {'natural': ['water']}
    
    try:
        # Get water features from OpenStreetMap
        water_gdf = ox.features_from_bbox(bbox.get_all_values_tuple(), tags)
        
        # Filter to keep only lakes and similar water bodies (exclude rivers)
        # Common OSM tags for lakes
        lake_tags = ['lake', 'pond', 'reservoir', 'basin']
        lakes_gdf = water_gdf[
            (water_gdf['natural'] == 'water') & 
            (
                water_gdf['water'].isin(lake_tags) | 
                ~water_gdf['water'].notnull()  # Include if water tag is missing
            )
        ].copy()
        
        # Exclude features with waterway tags
        if 'waterway' in lakes_gdf.columns:
            lakes_gdf = lakes_gdf[~lakes_gdf['waterway'].notnull()]
        
        # Make sure we're only including polygons (lakes) not linestrings (rivers)
        lakes_gdf = lakes_gdf[lakes_gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])]
        
        # Clip to ensure only lakes completely within the bounding box
        lakes_gdf = gpd.clip(lakes_gdf, bbox_gdf)
        
        # Calculate area in square kilometers
        lakes_gdf = lakes_gdf.to_crs('+proj=utm +zone=11 +datum=WGS84')  # Convert to UTM for area calculation
        lakes_gdf['area_km2'] = lakes_gdf.geometry.area / 1000000  # Convert m² to km²
        lakes_gdf = lakes_gdf.to_crs("EPSG:4326")  # Convert back to WGS84
        
        # Sort by area (largest first)
        lakes_gdf = lakes_gdf.sort_values('area_km2', ascending=False)
        
    except InsufficientResponseError as err:
        lakes_gdf = gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
    
    
    # Print lake information
    if not lakes_gdf.empty:
        logger.info("Found {} lakes within the bounding box".format(len(lakes_gdf)))
        for _, row in lakes_gdf.iterrows():
            name = row.get('name', 'Unnamed lake')
            logger.debug("  - {}: {:.2f} km²".format(name, row['area_km2']))
        logger.warning("Lakes are not used yet in the gcode")
    else:
        logger.info("No lakes found within the specified bounding box.")
        
    return lakes_gdf
    
