
import math
from src.spacial.geo_coord_sys import GeoBoundingBox, crop_bounding_box_to_ratio


def test_crop_basic_1():
    
    bbox = GeoBoundingBox(44.04207, -71.85694, 43.99183, -71.80904)
    
    cropped_bbox = crop_bounding_box_to_ratio(bbox, 1)
    
    cropped_ratio = (cropped_bbox.get_max_lon() - cropped_bbox.get_min_lon()) / (cropped_bbox.get_max_lat() - cropped_bbox.get_min_lat())
    
    assert math.isclose(cropped_ratio, 1.0)


def test_crop_basic_2():
    
    bbox = GeoBoundingBox(44.04207, -71.85694, 44.000153, -71.80904)
    
    cropped_bbox = crop_bounding_box_to_ratio(bbox, 1)
    
    cropped_ratio = (cropped_bbox.get_max_lon() - cropped_bbox.get_min_lon()) / (cropped_bbox.get_max_lat() - cropped_bbox.get_min_lat())
    
    assert math.isclose(cropped_ratio, 1.0)


def test_crop_regression_1():
    
    bbox = GeoBoundingBox(44.04207, -71.85694, 43.99183, -71.80904)
    
    cropped_bbox = crop_bounding_box_to_ratio(bbox, 1)
    
    cropped_ratio = (cropped_bbox.get_max_lon() - cropped_bbox.get_min_lon()) / (cropped_bbox.get_max_lat() - cropped_bbox.get_min_lat())
    
    assert math.isclose(cropped_ratio, 1.0)


def test_crop_regression_2():
    
    bbox = GeoBoundingBox(44.04207, -71.85694, 44.000153, -71.80904)
    
    cropped_bbox = crop_bounding_box_to_ratio(bbox, 1)
    
    cropped_ratio = (cropped_bbox.get_max_lon() - cropped_bbox.get_min_lon()) / (cropped_bbox.get_max_lat() - cropped_bbox.get_min_lat())
    
    assert math.isclose(cropped_ratio, 1.0)
