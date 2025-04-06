

from src.spacial.geo_coord_sys import GeoBoundingBox
from src.spacial.table_dimention import Table_Dimention

from src.geography_to_gcode import get_elevation_data, convert_elevation_data_to_path


def test_mnt_mousilauke_rotated():
    
    bbox = GeoBoundingBox(
        44.04207, -71.85704, 44.000153, -71.80914
    )
    
    table_dim = Table_Dimention(500, 880)
    
    elevation_data = get_elevation_data(bbox, table_dim, "./input_data/n44_w072_1arc_v3.tif", 90)
    
    path = convert_elevation_data_to_path(elevation_data, table_dim, num_contours=30)
    
    assert len(path) == 10809


def test_mnt_mousilauke_wide():
    
    bbox = GeoBoundingBox(
        44.04207, -71.85704, 44.000153, -71.80914
    )
    
    table_dim = Table_Dimention(880,550)
    
    elevation_data = get_elevation_data(bbox, table_dim, "./input_data/n44_w072_1arc_v3.tif", 90)
    
    path = convert_elevation_data_to_path(elevation_data, table_dim, num_contours=30)
    
    assert len(path) == 9980
    

def test_mnt_mousilauke_circular():
    
    bbox = GeoBoundingBox(
        44.04207, -71.85694, 44.000153, -71.80904
    )
    
    table_dim = Table_Dimention(500,500, circular=True)
    
    elevation_data = get_elevation_data(bbox, table_dim, "./input_data/n44_w072_1arc_v3.tif", 90)
    
    path = convert_elevation_data_to_path(elevation_data, table_dim, num_contours=30)
    
    assert len(path) == 23022
    