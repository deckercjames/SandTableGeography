
from dataclasses import dataclass
from shapely.geometry import Polygon
from src.spacial.table_dimention import Table_Dimention
import numpy as np
from src.logger import get_logger
import logging

logger = get_logger("geo coord", logging.DEBUG)


@dataclass(frozen=True)
class GeoBoundingBox:
    lat_0: float
    lon_0: float
    lat_1: float
    lon_1: float
    def get_min_lat(self):
        return min(self.lat_0, self.lat_1)
    def get_min_lon(self):
        return min(self.lon_0, self.lon_1)
    def get_max_lat(self):
        return max(self.lat_0, self.lat_1)
    def get_max_lon(self):
        return max(self.lon_0, self.lon_1)
    def get_lon_width(self):
        return self.get_max_lon() - self.get_min_lon()
    def get_lat_height(self):
        return self.get_max_lat() - self.get_min_lat()
    def get_lon_midpoint(self):
        return (self.get_min_lon() + self.get_max_lon()) / 2
    def get_lat_midpoint(self):
        return (self.get_min_lat() + self.get_max_lat()) / 2
    def get_all_values_tuple(self):
        return (
            self.get_min_lon(),
            self.get_min_lat(),
            self.get_max_lon(),
            self.get_max_lat(),
        )
    def get_as_polygon(self):
        min_lon, min_lat, max_lon, max_lat = self.get_all_values_tuple()
        return Polygon([
            (min_lon, min_lat),
            (max_lon, min_lat),
            (max_lon, max_lat),
            (min_lon, max_lat),
            (min_lon, min_lat)
        ])


def crop_bounding_box_to_ratio(bbox: GeoBoundingBox, table_dim: Table_Dimention):
    """
    Crops the bounding box defined by latitude and longitude to the desired aspect ratio.
    
    Parameters:
    lat_min, lat_max: float - the minimum and maximum latitudes of the original bounding box
    lon_min, lon_max: float - the minimum and maximum longitudes of the original bounding box
    aspect_ratio: float - the desired width/height ratio of the cropped bounding box
    
    Returns:
    tuple: (new_lat_min, new_lat_max, new_lon_min, new_lon_max)
    """
    
    aspect_ratio = table_dim.get_aspect_ratio()
    
    lon_min, lat_min, lon_max, lat_max = bbox.get_all_values_tuple()
    
    # Compute the initial height (latitude difference) and width (longitude difference) in degrees
    lat_diff = lat_max - lat_min
    lon_diff = lon_max - lon_min
    
    # Calculate the center of the original bounding box
    lat_center = (lat_min + lat_max) / 2
    lon_center = (lon_min + lon_max) / 2
    
    # Compute the scale factor for longitude based on the latitude center
    # Longitude degrees shrink as you move towards the poles, so we need to adjust for this
    scale_factor = np.cos(np.radians(lat_center))
    
    if aspect_ratio > (lon_diff / lat_diff):
        # If the desired aspect ratio requires a wider box (width > height)
        new_width = lon_diff
        new_height = new_width / aspect_ratio
        # Adjust the latitude difference to match the desired height
        half_lat_diff = new_height / 2
        new_lat_min = lat_center - half_lat_diff
        new_lat_max = lat_center + half_lat_diff
        # Longitude remains the same
        new_lon_min, new_lon_max = lon_min, lon_max
    else:
        # If the desired aspect ratio requires a taller box (height > width)
        new_height = lat_diff
        new_width = aspect_ratio * new_height
        # Adjust the longitude difference by the scale factor (to account for decreasing distance between meridians)
        new_lon_diff = new_width / scale_factor
        # Ensure that the new longitude doesn't go beyond the limits
        half_lon_diff = new_lon_diff / 2
        new_lon_min = lon_center - half_lon_diff
        new_lon_max = lon_center + half_lon_diff
        # Latitude remains the same
        new_lat_min, new_lat_max = lat_min, lat_max
    
    # Ensure the bounding box stays within valid geographical limits
    new_lat_min = max(-90, new_lat_min)
    new_lat_max = min(90, new_lat_max)
    new_lon_min = max(-180, new_lon_min)
    new_lon_max = min(180, new_lon_max)
    
    new_lat_diff = new_lat_max - new_lat_min
    new_lon_diff = new_lon_max - new_lon_min
    
    # Calculate the area of the original bounding box (approximated)
    original_area = lat_diff * lon_diff
    # Calculate the area of the cropped bounding box (approximated)
    cropped_area = new_lat_diff * new_lon_diff
    # Calculate the fraction of the area that was cropped out
    cropped_area_fraction = abs((original_area - cropped_area) / original_area)
    
    logger.info("Cropped aproxomatly {:0.2f}% to match the table aspect ratio".format(cropped_area_fraction*100))
    
    return GeoBoundingBox(
        new_lat_min, new_lon_min, new_lat_max, new_lon_max
    )
