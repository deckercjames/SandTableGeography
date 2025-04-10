
from src.spacial.geo_coord_sys import GeoBoundingBox
import math

def test_init_basic():
    
    bbox = GeoBoundingBox(4,60,5,70)
    
    assert bbox.get_min_lat() == 4
    assert bbox.get_min_lon() == 60
    assert bbox.get_max_lat() == 5
    assert bbox.get_max_lon() == 70
    
    assert math.isclose(bbox.get_lat_midpoint(), 4.5)
    assert bbox.get_lon_midpoint() == 65
    
    assert bbox.get_all_values_tuple() == (60, 4, 70, 5)
    
    assert bbox.get_lat_height() == 1
    assert bbox.get_lon_width() == 10


def test_init_basic_reversed():
    
    # Construct with max values firts
    bbox = GeoBoundingBox(5,70,4,60)
    
    assert bbox.get_min_lat() == 4
    assert bbox.get_min_lon() == 60
    assert bbox.get_max_lat() == 5
    assert bbox.get_max_lon() == 70
    
    assert math.isclose(bbox.get_lat_midpoint(), 4.5)
    assert bbox.get_lon_midpoint() == 65
    
    assert bbox.get_all_values_tuple() == (60, 4, 70, 5)
    
    assert bbox.get_lat_height() == 1
    assert bbox.get_lon_width() == 10
